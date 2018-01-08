print(__file__)
from ophyd import (PVPositioner, EpicsMotor, EpicsSignal, EpicsSignalRO,
                   PVPositionerPC, Device)
from ophyd import Component as Cpt

class MotorDialValues(Device):
	value = Cpt(EpicsSignalRO, ".DRBV")
	setpoint = Cpt(EpicsSignal, ".DVAL")

class MyEpicsMotorWithDial(EpicsMotor):
	dial = Cpt(MotorDialValues, "")

# m1 = MyEpicsMotorWithDial('2bmb:m1', name='m1')

m1 = EpicsMotor('2bmb:m1', name='m1')
m2 = EpicsMotor('2bmb:m2', name='m2')
m3 = EpicsMotor('2bmb:m3', name='m3')
m4 = EpicsMotor('2bmb:m4', name='m4')
m5 = EpicsMotor('2bmb:m5', name='m5')
m6 = EpicsMotor('2bmb:m6', name='m6')
m7 = EpicsMotor('2bmb:m7', name='m7')
m8 = EpicsMotor('2bmb:m8', name='m8')
