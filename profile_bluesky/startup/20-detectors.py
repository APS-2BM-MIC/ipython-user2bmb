print(__file__)

scaler = EpicsScaler('2bmb:scaler1', name='scaler')

try:
    pco_dimax = MyPcoDetector("PCOIOC2:", name="pco_dimax")  # TODO: check PV prefix
except TimeoutError:
    print("Could not connect to PCOIOC2:pco_dimax - is the IOC off?")

try:
    # FIXME: edge detector has some different PVs than Dimax
    pco_edge = MyPcoDetector("PCOIOC3:", name="pco_edge")
except TimeoutError:
    print("Could not connect to PCOIOC3:pco_edge - is the IOC off?")
