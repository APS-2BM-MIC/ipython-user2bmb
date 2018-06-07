print(__file__)

"""ophyd support for the busy record fly scan"""


def run_in_thread(func):
    """run ``func`` in thread"""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


#22
# from APS_BlueSky_tools.devices import ApsPssShutter
class ApsPssShutter_old(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
    
    USAGE:
    
        shutter_a = ApsPssShutter("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        shutter_a.set("open")
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(shutter_a))
        
    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.
    
    Example, add "o" & "x" as aliases for "open" & "close":
    
        shutter_a.valid_open_values.append("o")
        shutter_a.valid_close_values.append("x")
        shutter_a.set("o")
        shutter_a.set("x")
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    delay_s = 1.2
    valid_open_values = ["open",]   # lower-case strings ONLY
    valid_close_values = ["close",]
    busy = Signal(value=False, name="busy")
    
    def open(self):
        """request shutter to open, interactive use"""
        self.open_bit.put(1)
    
    def close(self):
        """request shutter to close, interactive use"""
        self.close_bit.put(1)
    
    def set(self, value, **kwargs):
        """request the shutter to open or close, BlueSky plan use"""
        # ensure numerical additions to lists are now strings
        def input_filter(v):
            return str(v).lower()
        self.valid_open_values = list(map(input_filter, self.valid_open_values))
        self.valid_close_values = list(map(input_filter, self.valid_close_values))
        
        if self.busy.value:
            raise RuntimeError("shutter is operating")

        acceptables = self.valid_open_values + self.valid_close_values
        if input_filter(value) not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)
        
        status = DeviceStatus(self)
        
        def move_shutter():
            if input_filter(value) in self.valid_open_values:
                self.open()     # no need to yield inside a thread
            elif input_filter(value) in self.valid_close_values:
                self.close()
        
        def run_and_delay():
            self.busy.put(True)
            move_shutter()
            # sleep, since we don't *know* when the shutter has moved
            time.sleep(self.delay_s)
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_delay, daemon=True).start()
        return status


class ApsPssShutterWithStatus(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
    
    USAGE:
    
        shutter_a = ApsPssShutterWithStatus("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        or
        
        %mov shutter_a "open"
        %mov shutter_a "close"
        
        or
        
        shutter_a.set("open")       # MUST be "open", not "Open"
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(shutter_a))
        
    The strings accepted by `set()` are defined in attributes
    (`open_str` and `close_str`).
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    delay_s = 1.2
    pss_state = FormattedComponent(EpicsSignalRO, "{self.state_pv}")

    # strings the user will use
    open_str = 'open'
    close_str = 'close'

    # pss_state PV values from EPICS
    open_val = 1
    close_val = 0

    def __init__(self, prefix, state_pv, *args, **kwargs):
        self.state_pv = state_pv
        super().__init__(prefix, *args, **kwargs)

    def open(self, timeout=10):
        ophyd.status.wait(self.set(self.open_str), timeout=timeout)

    def close(self, timeout=10):
        ophyd.status.wait(self.set(self.close_str), timeout=timeout)

    def set(self, value, **kwargs):
        # first, validate the input value
        acceptables = (self.close_str, self.open_str)
        if value not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)

        command_signal = {
            self.open_str: self.open_bit, 
            self.close_str: self.close_bit
        }[value]
        expected_value = {
            self.open_str: self.open_val, 
            self.close_str: self.close_val
        }[value]

        working_status = DeviceStatus(self)
        
        def shutter_cb(value, timestamp, **kwargs):
            # APS shutter state PVs do not define strings, use numbers
            #value = enums[int(value)]
            value = int(value)
            if value == expected_value:
                self.pss_state.clear_sub(shutter_cb)
                working_status._finished()
        
        self.pss_state.subscribe(shutter_cb)
        command_signal.set(1)
        return working_status


class TaxiFlyScanDevice(Device):
    """
    BlueSky Device for APS taxi & fly scans
    
    Some EPICS fly scans at APS are triggered by a pair of 
    EPICS busy records. The busy record is set, which triggers 
    the external controls to do the fly scan and then reset 
    the busy record. 
    
    The first busy is called taxi and is responsible for 
    preparing the hardware to fly. 
    The second busy performs the actual fly scan. 
    In a third (optional) phase, data is collected 
    from hardware and written to a file.
    """
    taxi = Component(EpicsSignal, "taxi", put_complete=True)
    fly = Component(EpicsSignal, "fly", put_complete=True)
    
    def plan(self):
        #logger.info("before taxi")
        yield from bps.mv(self.taxi, self.taxi.enum_strs[1])
        #logger.info("after taxi")
        
        #logger.info("before fly")
        yield from bps.mv(self.fly, self.fly.enum_strs[1])
        #logger.info("after fly")
    
    # TODO: work-in-progress
