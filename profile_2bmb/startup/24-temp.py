print(__file__)

import epics

# TODO: remove once APS_BlueSky_tools is updated


AD_FrameType_schemes = {
    "reset" : dict(             # default names from Area Detector code
        ZRST = "Normal",
        ONST = "Background",
        TWST = "FlatField",
        ),
    "NeXus" : dict(             # NeXus (typical locations)
        ZRST = "/entry/data/data",
        ONST = "/entry/data/dark",
        TWST = "/entry/data/white",
        ),
    "DataExchange" : dict(      # APS Data Exchange
        ZRST = "/exchange/data",
        ONST = "/exchange/data_dark",
        TWST = "/exchange/data_white",
        ),
}


def AD_setup_FrameType(prefix, scheme="NeXus"):
    """
    configure so frames are identified & handled by type (dark, white, or image)
    
    PARAMETERS

        prefix (str) : EPICS PV prefix of area detector, such as "13SIM1:"
        scheme (str) : any key in the `AD_FrameType_schemes` dictionary
    
    This routine prepares the EPICS Area Detector to identify frames
    by image type for handling by clients, such as the HDF5 file writing plugin.
    With the HDF5 plugin, the `FrameType` PV is added to the NDattributes
    and then used in the layout file to direct the acquired frame to
    the chosen dataset.  The `FrameType` PV value provides the HDF5 address
    to be used.
    
    To use a different scheme than the defaults, add a new key to
    the `AD_FrameType_schemes` dictionary, defining storage values for the
    fields of the EPICS `mbbo` record that you will be using.
    
    see: https://github.com/BCDA-APS/use_bluesky/blob/master/notebooks/images_darks_flats.ipynb
    
    EXAMPLE::
    
        AD_setup_FrameType("2bmbPG3:", scheme="DataExchange")
    
    * Call this function *before* creating the ophyd area detector object
    * use lower-level PyEpics interface
    """
    db = AD_FrameType_schemes.get(scheme)
    if db is None:
        msg = "unknown AD_FrameType_schemes scheme: {}".format(scheme)
        msg += "\n Should be one of: " + ", ".join(AD_FrameType_schemes.keys())
        raise ValueError(msg)

    template = "{}cam1:FrameType{}.{}"
    for field, value in db.items():
        epics.caput(template.format(prefix, "", field), value)
        epics.caput(template.format(prefix, "_RBV", field), value)
