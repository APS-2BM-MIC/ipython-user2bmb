print(__file__)

"""motors"""

from ophyd import MotorBundle


class TomoStage(MotorBundle):
    rotary = Component(EpicsMotor, "2bmb:m100", labels=("theta", "tomo"))
    x = Component(EpicsMotor, "2bmb:m63", labels=("tomo",))
    y = Component(EpicsMotor, "2bmb:m57", labels=("tomo",))


tomo_stage = TomoStage(name="tomo_stage")
samStage = tomo_stage.x
#samStage = tomo_stage.y
