print(__file__)


"""Set up default complex devices"""


import time
from ophyd import Component, Device, DeviceStatus, Signal
from ophyd import EpicsMotor, EpicsScaler
from ophyd.scaler import ScalerCH
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import PVPositioner, PVPositionerPC
from ophyd import AreaDetector, PcoDetectorCam
from ophyd import SingleTrigger, ImagePlugin, HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import PluginBase

# TODO: refactor as bps.mv, bps.mvr, ...
from bluesky.plan_stubs import mv, mvr, abs_set, wait

from APS_BlueSky_tools.devices import userCalcsDevice
from APS_BlueSky_tools.devices import ApsPssShutter
from APS_BlueSky_tools.devices import EpicsMotorShutter
from APS_BlueSky_tools.devices import EpicsMotorWithDial
from APS_BlueSky_tools.devices import EpicsMotorWithServo


class Mirror1_A(Device):
    """
    Mirror 1 in the 2BM-A station
    
    A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
    A_mirror1.angle.put(Mirr_Ang)
    A_mirror1.average.put(Mirr_YAvg)
    """
    angle = Component(EpicsSignal, "angl")
    average = Component(EpicsSignal, "avg")


class PSO_Device(Device):
    """
    Operate the motion trajectory controls of an Aerotech Ensemble controller
    
    note: PSO means Position Synchronized Output (Aerotech's term)
    
    USAGE:
    
        pso1 = PSO_Device("2bmb:PSOFly1:", name="pso1")
        #
        # ... configure the pso1 object
        #
        pso1.set("taxi")    # or pso1.taxi() interactively
        pso1.set("fly")     # or pso1.fly() interactively
        
        # in a plan, use this instead
        yield from abs_set(pso1, "taxi", wait=True)
        yield from abs_set(pso1, "fly", wait=True)

    """
    # TODO: this might fit the ophyd "Flyer" API
    slew_speed = Component(EpicsSignal, "slewSpeed.VAL")
    scan_control = Component(EpicsSignal, "scanControl.VAL", string=True)
    start_pos = Component(EpicsSignal, "startPos.VAL")
    end_pos = Component(EpicsSignal, "endPos.VAL")
    scan_delta = Component(EpicsSignal, "scanDelta.VAL")
    pso_taxi = Component(EpicsSignal, "taxi.VAL", put_complete=True)
    pso_fly = Component(EpicsSignal, "fly.VAL", put_complete=True)
    busy = Signal(value=False, name="busy")
    
#     def __init__(self, motor, detector):
#         self.motor = motor
#         self.detector = detector
# 
#         self.return_position = self.motor.position
#         self.poll_delay_s = 0.05
#         self.num_spins = 1
# 
#         self._completion_status = None
#         self._data = deque()
    
    def taxi(self):
        """
        request move to taxi position, interactive use
        
        Since ``pso_taxi`` has the ``put_complete=True`` attribute,
        this will block until the move is complete.
        
        (note: ``2bmb:PSOFly1:taxi.RTYP`` is a ``busy`` record.)
        """
        # TODO: verify that this blocks until complete
        self.pso_taxi.put("Taxi")
    
    def fly(self):
        """
        request fly scan to start, interactive use
        
        Since ``pso_fly`` has the ``put_complete=True`` attribute,
        this will block until the move is complete.
        """
        # TODO: verify that this blocks until complete
        self.pso_fly.put("Fly")

    def set(self, value):       # interface for BlueSky plans
        """value is either Taxi, Fly, or Return"""
#         allowed = "Taxi Fly Return".split()
        allowed = "Taxi Fly".split()
        if str(value).lower() not in list(map(str.lower, allowed)):
            msg = "value should be one of: " + " | ".join(allowed)
            msg + " received " + str(value)
            raise ValueError(msg)

        if self.busy.value:
            raise RuntimeError("shutter is operating")

        status = DeviceStatus(self)
        
        def action():
            """the real action of ``set()`` is here"""
            if str(value).lower() == "taxi":
                self.taxi()
            elif str(value).lower() == "fly":
                self.fly()
#             elif str(value).lower() == "return":
#                 self.motor.move(self.return_position)

        def run_and_wait():
            """handle the ``action()`` in a thread"""
            self.busy.put(True)
            action()
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_wait, daemon=True).start()
        return status

#     def kickoff(self):
#         """
#         Start a flyer
#         """
#         if self._completion_status is not None:
#             raise RuntimeError("Already kicked off.")
#         self._data = deque()
# 
#         self._future = self.loop.run_in_executor(None, self._spin_sequence)
#         self._completion_status = DeviceStatus(device=self)
#         return self._completion_status
# 
#     def complete(self):
#         """
#         Wait for flying to be complete
#         """
#         if self._completion_status is None:
#             raise RuntimeError("No collection in progress")
#         
#         while self.motor.moving:
#             time.sleep(self.poll_delay_s)
#         
#         return self._completion_status
#     
#     def collect(self):
#         """
#         Retrieve data from the flyer as *proto-events*
#         """
#         if self._completion_status is None or not self._completion_status.done:
#             raise RuntimeError("No reading until done!")
#         self._completion_status = None
# 
#         yield from self._data
# 
#     def _spin_sequence(self):        # TODO: 2018-02-15: test this!
#         """
#         spin flyer, called from kickoff() in asyncio thread
#         """
#         self.return_position = self.motor.position
#         
#         for spin_num in range(self.num_spins):
#             self.taxi()
#     
#             self.pre_fly()
#             self.fly()
#             det_post_fly(self.detector)
# 
#             while self.detector.hdf1.write_file.value:
#                 time.sleep(0.01)    # wait for file to be written
#     
#             event = OrderedDict()
#             event["time"] = time.time()
#             event["seq_num"] = spin_num + 1
#             event["data"] = {}
#             event["timestamps"] = {}
#             # TODO: generalize this list
#             for d_item in (self.detector.hdf1.full_file_name, ):
#                 d = d_item.read()
#                 for k, v in d.items():
#                     event['data'][k] = v['value']
#                     event['timestamps'][k] = v['timestamp']
#     
#             self._data.append(event)
#             # print("# data: {}".format(len(self._data)))
# 
#         self.set("Return")
#         self._completion_status._finished(success=True)
#     
#     def pre_fly(self):
#         """ """
#         pass        # TODO: implement
#     
#     def post_fly(self):
#         """ """
#         pass        # TODO: implement


class MyEdgeDescrambler(PluginBase):
    """PCO Edge detector descrambler"""
    _default_suffix = 'EDGEDSC:'
    _suffix_re = 'descrambler\d:'
    _html_docs = ['unconfigured.html']
    _plugin_type = 'NDPluginFile'


class MyPcoCam(PcoDetectorCam):
    """PCO Dimax detector"""
    pco_cancel_dump = Component(EpicsSignal, "pco_cancel_dump")
    pco_live_view = Component(EpicsSignal, "pco_live_view")
    pco_trigger_mode = Component(EpicsSignal, "pco_trigger_mode")
    pco_edge_fastscan = Component(EpicsSignal, "pco_edge_fastscan")
    pco_is_frame_rate_mode = Component(EpicsSignal, "pco_is_frame_rate_mode")
    pco_imgs2dump = Component(EpicsSignalWithRBV, "pco_imgs2dump")
    pco_dump_counter = Component(EpicsSignal, "pco_dump_counter")
    pco_dump_camera_memory = Component(EpicsSignal, "pco_dump_camera_memory")
    pco_max_imgs_seg0 = Component(EpicsSignalRO, "pco_max_imgs_seg0_RBV")
    pco_ready2acquire = Component(EpicsSignal, "pco_ready2acquire")
    pco_set_frame_rate = Component(EpicsSignal, "pco_set_frame_rate")
    

class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
#class MyHDF5Plugin(HDF5Plugin):
    """adapt HDF5 plugin for AD 2.5+"""
    
    file_number_sync = None
    # FIXME:  .put() works OK but .value returns numpy object metadata
    # In [48]: pco_edge.hdf1.xml_layout_file.get()
    # Out[48]: '<array size=21, type=time_char>'
    # FIXME: xml_layout_file = Component(EpicsSignalWithRBV, "XMLFileName", string=True)
    xml_layout_file = Component(EpicsSignal, "XMLFileName", string=True)    # use as WRITE-ONLY for now due to error above
    xml_layout_valid = Component(EpicsSignalRO, "XMLValid_RBV")
    xml_layout_error_message = Component(EpicsSignalRO, "XMLErrorMsg_RBV", string=True)
    
    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()
    

class MyPcoDetector(SingleTrigger, AreaDetector):
    """PCO detectors as used by 2-BM tomography"""
    # TODO: configure the "root" and "write_path_template" attributes
    
    cam = Component(MyPcoCam, "cam1:")
    image = Component(ImagePlugin, "image1:")
    hdf1 = Component(
        MyHDF5Plugin, 
        "HDF1:", 
        root="/",                   # root path for HDF5 files (for databroker filestore)
        write_path_template="/tmp", # path for HDF5 files (for EPICS area detector)
        )


class SynApps_saveData_Device(Device):
    """
    saveData support, just the fields used here
    
    USAGE::

        savedata = SynApps_saveData_Device("2bmb:saveData" name="savedata")
        savedata.scan_number.put(5)
        savedata.base_name.put("bane name")

    """

    scan_number = Component(EpicsSignal, "_scanNumber")
    base_name = Component(EpicsSignal, "_baseName")


class SynApps_Record_asub(Device):
    """asub record, just the fields used here"""
    # https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_Array_Subroutine
    
    proc = Component(EpicsSignal, ".PROC")
    a = Component(EpicsSignal, ".A")
    b = Component(EpicsSignal, ".B")
    vale = Component(EpicsSignal, ".VALE")
