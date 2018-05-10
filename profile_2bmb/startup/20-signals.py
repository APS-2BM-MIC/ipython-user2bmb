print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}

# such as this area detector
EPICS_PV_prefix["PG3 PointGrey Grasshopper3"] = "2bmbPG3:"

# for area detector file plugins (& other)
USER2BMB_ROOT_DIR = "/local/user2bmb"


aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

try:
    A_shutter = ApsPssShutter("2bma:A_shutter", name="A_shutter")
    B_shutter = ApsPssShutter("2bma:B_shutter", name="B_shutter")
except Exception as _exc:
    print(_exc)
