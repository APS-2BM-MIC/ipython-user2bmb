print(__file__)

"""PG3 PointGrey Grasshopper3 detector"""

from ophyd import PointGreyDetectorCam

# PVA plugin not staged enabled/disabled yet, be prepared
class MyPvaPlugin(PluginBase):
    """PVA plugin (not in ophyd)"""
    _default_suffix = 'EDGEDSC:'
    _suffix_re = 'pva\d:'
    _html_docs = ['unconfigured.html']
    _plugin_type = 'NDPluginPva'
    pva_image_pv_name = ADComponent(EpicsSignalRO, "PvName_RBV")


class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Grasshopper3 detector as used by 2-BM-B tomography"""
    
    cam = ADComponent(PointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    hdf1 = ADComponent(HDF5Plugin, "HDF1:")
    pva1 = ADComponent(MyPvaPlugin, "Pva1:")


pg3_det = MyPointGreyDetector(
    EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
    name="pg3_det")
