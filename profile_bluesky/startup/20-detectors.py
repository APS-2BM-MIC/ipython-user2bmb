print(__file__)

"""various detectors and other signals"""

scaler = EpicsScaler('2bmb:scaler1', name='scaler')
#scaler = ScalerCH('2bmb:scaler1', name='scaler')
