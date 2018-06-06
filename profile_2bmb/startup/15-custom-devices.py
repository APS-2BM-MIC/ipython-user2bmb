print(__file__)

"""ophyd support for the busy record fly scan"""


#22
# from APS_BlueSky_tools.devices import ApsPssShutter
class ApsPssShutter(Device):
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
