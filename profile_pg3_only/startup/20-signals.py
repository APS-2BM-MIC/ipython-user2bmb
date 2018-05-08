print(__file__)

"""various signals at the beam line"""

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")
