print(__file__)

"""PG3 PointGrey Grasshopper3 detector"""

from ophyd import PointGreyDetectorCam

class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Black Fly detector(s) as used by 9-ID-C USAXS"""
    
    cam = ADComponent(PointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")


pg3_det = MyPointGreyDetector(
    area_detector_EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
    name="pg3_det")
