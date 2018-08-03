print(__file__)

"""motors"""

from ophyd import MotorBundle


class TomoStage(MotorBundle):
    rotary = Component(EpicsMotor, "2bma:m82", labels=("theta", "tomo"))
    x = Component(EpicsMotor, "2bma:m49", labels=("tomo",))
    y = Component(EpicsMotor, "2bma:m20", labels=("tomo",))


tomo_stage = TomoStage(name="tomo_stage")
samStage = tomo_stage.y
