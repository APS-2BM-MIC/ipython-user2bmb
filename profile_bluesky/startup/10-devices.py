print(__file__)


"""Set up default complex devices"""


import time
from ophyd import Component, Device, DeviceStatus
from ophyd import EpicsMotor, EpicsScaler
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import PVPositioner, PVPositionerPC
from ophyd import AreaDetector, PcoDetectorCam
from ophyd import SingleTrigger, ImagePlugin, HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from APS_BlueSky_tools.devices import userCalcsDevice


class MotorDialValuesDevice(Device):
    value = Component(EpicsSignalRO, ".DRBV")
    setpoint = Component(EpicsSignal, ".DVAL")


class MyEpicsMotorWithDial(EpicsMotor):
    dial = Component(MotorDialValuesDevice, "")


class ServoRotationStage(EpicsMotor):
    """extend basic motor support to enable/disable the servo loop controls"""
    
    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)


class Mirror1_A(Device):
    """
    Mirror 1 in the 2BM-A station
    
    A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
    A_mirror1.angle.put(Mirr_Ang)
    A_mirror1.average.put(Mirr_YAvg)
    """
    angle = Component(EpicsSignal, "angl")
    average = Component(EpicsSignal, "avg")


class AB_Shutter(Device):
    """
    A or B station shutter (PSS item)
    
    USAGE::

        A_shutter = AB_Shutter("2bma:A_shutter", name="A_shutter")
        A_shutter.open()
        A_shutter.close()

        B_shutter = AB_Shutter("2bma:B_shutter", name="B_shutter")
        B_shutter.close()

    """
    pss_open = Component(EpicsSignal, ":open")
    pss_close = Component(EpicsSignal, ":close")
    
    def open(self):
        """tells PSS to open the shutter"""
        self.pss_open.put(1)
    
    def close(self):
        """tells PSS to close the shutter"""
        self.pss_close.put(1)


class Motor_Shutter(Device):
    """
    a shutter, implemented with a motor
    
    USAGE::

        tomo_shutter = Motor_Shutter("2bma:m23", name="tomo_shutter")
        tomo_shutter.open()
        tomo_shutter.close()

    """
    motor = Component(EpicsMotor, "")
    closed_position = 1.0
    open_position = 0.0
    
    def open(self):
        """move motor to BEAM NOT BLOCKED position"""
        self.motor.move(self.open_position)
    
    def close(self):
        """move motor to BEAM BLOCKED position"""
        self.motor.move(self.closed_position)


class PSO_Device(Device):
    # TODO: this might fit the ophyd "Flyer" API
    slew_speed = Component(EpicsSignal, "slewSpeed.VAL")
    scan_control = Component(EpicsSignal, "scanControl.VAL", string=True)
    start_pos = Component(EpicsSignal, "startPos.VAL")
    end_pos = Component(EpicsSignal, "endPos.VAL")
    scan_delta = Component(EpicsSignal, "scanDelta.VAL")
    pso_taxi = Component(EpicsSignal, "taxi.VAL")
    pso_fly = Component(EpicsSignal, "fly.VAL")
    
    def taxi(self):
        self.pso_taxi.put("Taxi")
    
    def fly(self):
        self.pso_fly.put("Fly")


class MyPcoCam(PcoDetectorCam):    # TODO: check this
    """PCO Dimax detector"""
    # FIXME: make different one for Edge PVs
    array_callbacks = Component(EpicsSignal, "ArrayCallbacks")
    pco_cancel_dump = Component(EpicsSignal, "pco_cancel_dump")
    pco_live_view = Component(EpicsSignal, "pco_live_view")
    pco_trigger_mode = Component(EpicsSignal, "pco_trigger_mode")
    pco_edge_fastscan = Component(EpicsSignal, "pco_edge_fastscan")
    pco_is_frame_rate_mode = Component(EpicsSignal, "pco_is_frame_rate_mode")
    pco_imgs2dump = Component(EpicsSignalWithRBV, "pco_imgs2dump")
    pco_dump_counter = Component(EpicsSignal, "pco_dump_counter")
    pco_dump_camera_memory = Component(EpicsSignal, "pco_dump_camera_memory")


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    """adapt HDF5 plugin for AD 2.5+"""
    
    file_number_sync = None
    xml_layout_file = Component(EpicsSignalWithRBV, "XMLFileName")
    
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
