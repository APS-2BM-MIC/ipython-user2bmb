print(__file__)

"""support PCO Edge detector"""


class MyPcoEdgeCam(MyPcoCam):
    """adapt CAM plugin for PCO Edge detector"""
    
    pco_global_shutter = Component(EpicsSignal, "pco_global_shutter")


class MyEdgeHDF5Plugin(MyHDF5Plugin):
    """adapt HDF5 plugin for PCO Edge detector"""
    
    # http://cars.uchicago.edu/software/epics/areaDetectorDoc.html
    # NDFileCreateDir
    create_directory = Component(EpicsSignal, "CreateDirectory")


class MyPcoEdgeDetector(SingleTrigger, AreaDetector):
    """PCO edge detector as used by 2-BM tomography"""
    
    cam = Component(MyPcoEdgeCam, "cam1:")
    image = Component(ImagePlugin, "image1:")
    descrambler1 = Component(MyEdgeDescrambler, "EDGEDSC:")
    hdf1 = Component(
        MyEdgeHDF5Plugin, 
        "HDF1:", 
        root="S:/",                   # root path for HDF5 files (for databroker filestore)
        write_path_template="S:/data/2018_02/Doga/", # exported from //grayhound/S drive
        reg=db.reg,
        )

# caputRecorderExecute.adl P=2bmb: L=2bmb:
# caputRecorderGlobal.adl P=2bmb: L=2bmb:

try:
    pco_edge = MyPcoEdgeDetector("PCOIOC3:", name="pco_edge")
except TimeoutError:
    print("Could not connect to PCOIOC3:pco_edge - is the IOC off?")
