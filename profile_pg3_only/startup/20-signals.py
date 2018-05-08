print(__file__)


USER2BMB_ROOT_DIR = "/local/user2bmb"

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

