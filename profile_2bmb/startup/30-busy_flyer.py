print(__file__)

"""ophyd Flyer support for the busy record fly scan"""

# TODO: good to work this up in a notebook first

from enum import Enum


class BusyStatus(str, Enum):
    busy = "Busy"
    done = "Done"


class MyCalc(Device):
    """swait record simulates a signal"""
    result = Component(EpicsSignal, "")
    calc = Component(EpicsSignal, ".CALC")
    proc = Component(EpicsSignal, ".PROC")


class MyWaveform(Device):
    """waveform records store fly scan data"""
    wave = Component(EpicsSignalRO, "")
    number_elements = Component(EpicsSignalRO, ".NELM")
    number_read = Component(EpicsSignalRO, ".NORD")


try:

    # TODO: modify for 2-bm-b
    BUSY_PV = '2bmb:PSOFly1:taxi'
    BUSY_PV = '2bmb:PSOFly1:fly'

    class BusyFlyerDevice(Device):
        """
        support a fly scan that is triggered by a busy record
        """

        busy = Component(EpicsSignal, BUSY_PV, string=True)
        
        def __init__(self, *args, **kwargs):
            super().__init__('', parent=None, **kwargs)
            self.complete_status = None

        def kickoff(self):
            """
            Start this Flyer
            """
            logger.info("kickoff()")
            self.complete_status = DeviceStatus(self.busy)
            
            def cb(*args, **kwargs):
                if self.busy.value in (BusyStatus.done):
                    self.complete_status._finished(success=True)
            
            self.t0 = time.time()
            self.busy.put(BusyStatus.busy)
            self.busy.subscribe(cb)

            kickoff_status = DeviceStatus(self)
            kickoff_status._finished(success=True)
            return kickoff_status

        def complete(self):
            """
            Wait for flying to be complete
            """
            logger.info("complete(): " + str(self.complete_status))
            return self.complete_status

        def describe_collect(self):
            """
            Describe details for ``collect()`` method
            """
            logger.info("describe_collect()")
            schema = {}
            # TODO: What will be returned?
            return {self.name: schema}

        def collect(self):
            """
            Start this Flyer
            """
            logger.info("collect(): " + str(self.complete_status))
            self.complete_status = None
            # TODO: What will be yielded?


    bfly = BusyFlyerDevice(name="bfly")
    # RE(bp.fly([bfly], md=dict(purpose="develop busy flyer model")))

except Exception as _exc:
    print(_exc)

