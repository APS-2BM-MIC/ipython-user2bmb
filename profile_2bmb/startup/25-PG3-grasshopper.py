print(__file__)

"""PG3 PointGrey Grasshopper3 detector"""

from ophyd import PointGreyDetectorCam, ProcessPlugin

HDF5_FILE_PATH = os.path.join(USER2BMB_ROOT_DIR, "mona")


# PVA plugin not staged enabled/disabled yet, be prepared
class MyPvaPlugin(PluginBase):
    """PVA plugin (not in ophyd)"""
    _default_suffix = 'PVA1:'
    _suffix_re = 'pva\d:'
    _html_docs = ['unconfigured.html']
    _plugin_type = 'NDPluginPva'
    pva_image_pv_name = ADComponent(EpicsSignalRO, "PvName_RBV")


class MyHDF5Plugin(HDF5Plugin):
    file_path = ADComponent(EpicsSignalWithRBV, "FilePath")


class MyPointGreyDetectorCam(PointGreyDetectorCam):
    """PointGrey Grasshopper3 cam plugin customizations (properties)"""
    auto_exposure_on_off = ADComponent(EpicsSignalWithRBV, "AutoExposureOnOff")
    auto_exposure_auto_mode = ADComponent(EpicsSignalWithRBV, "AutoExposureAutoMode")
    sharpness_on_off = ADComponent(EpicsSignalWithRBV, "SharpnessOnOff")
    sharpness_auto_mode = ADComponent(EpicsSignalWithRBV, "SharpnessAutoMode")
    gamma_on_off = ADComponent(EpicsSignalWithRBV, "GammaOnOff")
    shutter_auto_mode = ADComponent(EpicsSignalWithRBV, "ShutterAutoMode")
    gain_auto_mode = ADComponent(EpicsSignalWithRBV, "GainAutoMode")
    trigger_mode_on_off = ADComponent(EpicsSignalWithRBV, "TriggerModeOnOff")
    trigger_mode_auto_mode = ADComponent(EpicsSignalWithRBV, "TriggerModeAutoMode")
    trigger_delay_on_off = ADComponent(EpicsSignalWithRBV, "TriggerDelayOnOff")
    frame_rate_on_off = ADComponent(EpicsSignalWithRBV, "FrameRateOnOff")
    frame_rate_auto_mode = ADComponent(EpicsSignalWithRBV, "FrameRateAutoMode")
    # there are other PG3 properties, ignore them for now


class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Grasshopper3 detector as used by 2-BM-B tomography"""
    
    cam = ADComponent(MyPointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    hdf1 = ADComponent( # FIXME:
        MyHDF5Plugin, 
        suffix="HDF1:",
        # TypeError: __init__() got an unexpected keyword argument 'root'
        #root='/',                               # for databroker
        # TypeError: __init__() got an unexpected keyword argument 'write_path_template'
        #write_path_template=HDF5_FILE_PATH,     # for EPICS AD
        )
    process1 = ADComponent(ProcessPlugin, "Proc1:")
    pva1 = ADComponent(MyPvaPlugin, "Pva1:")

"""
example setup for the PVA plugin (from FileStoreTIFFSquashing)

        self._cam_name = cam_name
        self._proc_name = proc_name
        cam = getattr(self.parent, self._cam_name)
        proc = getattr(self.parent, self._proc_name)
        self.stage_sigs.update([('file_template', '%s%s_%6.6d.tiff'),
                                ('file_write_mode', 'Single'),
                                (proc.nd_array_port, cam.port_name.get()),
                                (proc.reset_filter, 1),
                                (proc.enable_filter, 1),
                                (proc.filter_type, 'Average'),
                                (proc.auto_reset_filter, 1),
                                (proc.filter_callbacks, 1),
                                ('nd_array_port', proc.port_name.get())
                                ])

"""

pg3_det = MyPointGreyDetector(
    EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
    name="pg3_det")
# TODO: support the process plugin for darks and flats
# TODO: configure pg3_det Image1 & PVA1 to use PROC1 output instead
pg3_det.cam.stage_sigs["image_mode"] = "Continuous"
pg3_det.cam.stage_sigs["array_counter"] = 0
pg3_det.cam.stage_sigs["gain"] = 0
pg3_det.cam.stage_sigs["auto_exposure_on_off"] = "Off"
pg3_det.cam.stage_sigs["auto_exposure_auto_mode"] = "Manual"
pg3_det.cam.stage_sigs["shutter_auto_mode"] = "Manual"
pg3_det.cam.stage_sigs["gain_auto_mode"] = "Manual"
pg3_det.cam.stage_sigs["trigger_mode_on_off"] = "Off"
pg3_det.cam.stage_sigs["trigger_mode_auto_mode"] = "Manual"
pg3_det.cam.stage_sigs["trigger_delay_on_off"] = "Off"
pg3_det.cam.stage_sigs["frame_rate_on_off"] = "Off"
pg3_det.cam.stage_sigs["frame_rate_auto_mode"] = "Manual"
pg3_det.read_attrs = ['hdf1']


# note: convenience plans -- call these BEFORE taking the image
# This value will appear in the attributes of the PVaccess PV
# with name of `SaveDest`

def set_white_frame(*, det=None):
    det = det or pg3_det
    #ophyd.status.wait(det.cam.frame_type.set("FlatField"))
    yield from bps.mv(det.cam.frame_type, "FlatField")

def set_dark_frame(*, det=None):
    det = det or pg3_det
    yield from bps.mv(det.cam.frame_type, "Background")

def set_image_frame(*, det=None):
    det = det or pg3_det
    yield from bps.mv(det.cam.frame_type, "Normal")
