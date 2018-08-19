print(__file__)

"""PG3 PointGrey Grasshopper3 detector"""

from ophyd import PointGreyDetectorCam, ProcessPlugin

# such as this area detector
EPICS_PV_prefix["PG3 PointGrey Grasshopper3"] = "2bmbPG3:"

# for area detector file plugins (& other)
USER2BMB_ROOT_DIR = "/local/user2bmb"

# HDF5_FILE_PATH = os.path.join(USER2BMB_ROOT_DIR, "mona") + "/"
# HDF5_FILE_PATH = "/home/beams/USER2BMB/mona/%Y/%m/%d/"
# HDF5_FILE_PATH = "/local/data/mona/"
HDF5_FILE_PATH = os.path.join(USER2BMB_ROOT_DIR, "mona", "%Y/%m/%d") + "/"


# PVA plugin not staged enabled/disabled yet, be prepared
class MyPvaPlugin(PluginBase):
    """PVA plugin (not in ophyd)"""
    _default_suffix = 'PVA1:'
    _suffix_re = 'pva\d:'
    _html_docs = ['unconfigured.html']
    _plugin_type = 'NDPluginPva'
    pva_image_pv_name = ADComponent(EpicsSignalRO, "PvName_RBV")


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    #file_path = ADComponent(EpicsSignalWithRBV, "FilePath")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = "AD_HDF5_DX_V1"
        # DataExchangeAreaDetectorHDF5Handler


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

from ophyd.status import Status

class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Grasshopper3 detector as used by 2-BM-B tomography"""
    
    cam = ADComponent(MyPointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    hdf1 = ADComponent(
        MyHDF5Plugin, 
        suffix="HDF1:",
        root='/',                               # for databroker
        write_path_template=HDF5_FILE_PATH,     # for EPICS AD
        )
    #process1 = ADComponent(ProcessPlugin, "Proc1:")
    pva1 = ADComponent(MyPvaPlugin, "Pva1:")
    
    def trigger(self):
        
        hdf5_st = Status()
        # callback to watch for the hdf5 plugin to finish, not needed for AD >= 3.3
        def cb(value, **kwargs):
            if value == 0:
                hdf5_st._finished()
                self.hdf1.write_file.clear_sub(cb)
        # subscribe before we start running but don't run on current value
        # should not matter, but belt and suspenders.
        self.hdf1.write_file.subscribe(cb, run=False)
        st = super().trigger()
        return st & hdf5_st
                

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


if False:   # run this code only as-needed
    APS_devices.AD_setup_FrameType(
        EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
        scheme="DataExchange"
    )


pg3_det = MyPointGreyDetector(
    EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
    name="pg3_det")
# TODO: support the process plugin for darks and flats
# TODO: configure pg3_det Image1 & PVA1 to use PROC1 output instead
#pg3_det.cam.stage_sigs["image_mode"] = "Single"
#pg3_det.cam.stage_sigs["array_counter"] = 0
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
pg3_det.pva1.stage_sigs["blocking_callbacks"] = "No"
del pg3_det.hdf1.stage_sigs["num_capture"]

pg3_det.hdf1.ensure_nonblocking() 
pg3_det.image.ensure_nonblocking() 
pg3_det.pva1.ensure_nonblocking() 
