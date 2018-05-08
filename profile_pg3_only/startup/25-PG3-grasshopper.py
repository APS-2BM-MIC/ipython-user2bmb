print(__file__)

"""PG3 PointGrey Grasshopper3 detector"""

from ophyd import PointGreyDetectorCam


class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Grasshopper3 detector as used by 2-BM-B tomography"""
    
    cam = ADComponent(PointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    hdf1 = ADComponent(HDF5Plugin, "HDF1:")


pg3_det = MyPointGreyDetector(
    area_detector_EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
    name="pg3_det")
