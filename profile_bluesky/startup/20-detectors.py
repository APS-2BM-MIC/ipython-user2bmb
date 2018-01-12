print(__file__)

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')
userCalc1_2bmb = EpicsSignalRO('2bmb:userCalc1', name='userCalc1_2bmb')
scaler = EpicsScaler('2bmb:scaler1', name='scaler')

try:
    pco_dimax = MyPcoDetector("PCOIOC2:", name="pco_dimax")  # TODO: check PV prefix
except TimeoutError:
    print("Could not connect to PCOIOC2:pco_dimax - is the IOC off?")

try:
    pco_edge = MyPcoDetector("PCOIOC3:", name="pco_edge")  # TODO: check PV prefix
except TimeoutError:
    print("Could not connect to PCOIOC3:pco_edge - is the IOC off?")
