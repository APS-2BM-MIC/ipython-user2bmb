print(__file__)

"""support PCO Edge detector"""

from ophyd.utils import set_and_wait


class MyPcoEdgeCam(MyPcoCam):
    """adapt CAM plugin for PCO Edge detector"""
    
    pco_global_shutter = Component(EpicsSignal, "pco_global_shutter")
    # TODO: frame_type should allow strings
    # pco_edge.cam.frame_type.enum_strs
    # Out[15]: ('Normal', 'Background', 'FlatField', 'DblCorrelation')

    frame_type_VAL = Component(EpicsSignal, "FrameType")


class MyEdgeHDF5Plugin(MyHDF5Plugin):
    """adapt HDF5 plugin for PCO Edge detector"""
    
    # http://cars.uchicago.edu/software/epics/areaDetectorDoc.html
    # NDFileCreateDir
    create_directory = Component(EpicsSignal, "CreateDirectory")

    def make_filename(self):
        """make the file name the way we want it"""
        filename = cpr_filename.value
        # write_path = cpr_filepath.value
        write_path = self.file_path.value
        read_path = "/mnt/WinS/" + write_path.split(":")[-1].replace("\\", "/")
        return filename, read_path, write_path

class MyPcoEdgeDetector(SingleTrigger, AreaDetector):
    """PCO edge detector as used by 2-BM tomography"""
    
    cam = Component(MyPcoEdgeCam, "cam1:")
    image = Component(ImagePlugin, "image1:")
    descrambler1 = Component(MyEdgeDescrambler, "EDGEDSC:")
    hdf1 = Component(
        MyEdgeHDF5Plugin, 
        "HDF1:", 
        root="/mnt/WinS",                   # root path for HDF5 files (for databroker filestore)
        write_path_template="S:/data/2018_02/Doga/test/", # exported from //grayhound/S drive
        reg=db.reg,
        )

# caputRecorderExecute.adl P=2bmb: L=2bmb:
# caputRecorderGlobal.adl P=2bmb: L=2bmb:


try:
    pco_edge = MyPcoEdgeDetector("PCOIOC3:", name="pco_edge")
    pco_edge.hdf1.stage_sigs["file_template_VAL"] = "%s%s_%4.4d.hdf"
    pco_edge.cam.stage_sigs["num_images"] = 1
    # FIXME: work around ophyd unstage() problem inside RE()
    for key in "capture file_template file_number".split():
        if key in pco_edge.hdf1.stage_sigs:
            del pco_edge.hdf1.stage_sigs[key]
    #del pco_edge.cam.stage_sigs["num_images"]
    det = pco_edge  # developer use
except TimeoutError as exc:
    print("Problem connecting to PCOIOC3:pco_edge - is the IOC off?\n" + str(exc))
