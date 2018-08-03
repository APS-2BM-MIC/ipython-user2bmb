print(__file__)

"""
databroker configuration to read HDF5 files for data exchange
"""

from databroker.assets.handlers import HDF5DatasetSliceHandler


# https://github.com/NSLS-II/databroker/blob/master/databroker/assets/handlers.py

class DataExchangeAreaDetectorHDF5Handler(HDF5DatasetSliceHandler):
    """
    Handler for the 'AD_HDF5' spec used by Area Detectors writing 
    in the Data Exchange format.  In this spec, the key (i.e., 
    HDF5 dataset path) is always '/exchange/data'.

    Parameters
    ----------
    filename : string
        path to HDF5 file
    frame_per_point : integer, optional
        number of frames to return as one datum, default 1
    """
    specs = {'AD_HDF5_DX_V1'} | HDF5DatasetSliceHandler.specs

    def __init__(self, filename, frame_per_point=None):
        print(frame_per_point)
        hardcoded_key = '/exchange/data'
        super().__init__(
            filename=filename, key=hardcoded_key,
            frame_per_point=frame_per_point)

db.reg.register_handler("AD_HDF5_DX_V1", DataExchangeAreaDetectorHDF5Handler,  overwrite=True)
db.reg.register_handler("AD_HDF5", DataExchangeAreaDetectorHDF5Handler, overwrite=True)
