print(__file__)

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')
userCalc1_2bmb = EpicsSignalRO('2bmb:userCalc1', name='userCalc1_2bmb')
scaler = EpicsScaler('2bmb:scaler1', name='scaler')
