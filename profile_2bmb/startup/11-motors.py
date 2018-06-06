print(__file__)

"""motors"""

from ophyd import MotorBundle


class TomoStage(MotorBundle):
    rotary = Component(EpicsMotor, "2bmb:m100", labels=("theta", "tomo"))
    x = Component(EpicsMotor, "2bmb:m63", labels=("tomo",))
    y = Component(EpicsMotor, "2bmb:m57", labels=("tomo",))
    #pitch = Component(EpicsMotor, "2bmb:m54", labels=("tomo",))
    #roll = Component(EpicsMotor, "2bmb:m53", labels=("tomo",))
    changer_status = Component(EpicsSignalRO, "2bmb:Begin_Scan")
    position_status = Component(EpicsSignalRO, "2bmb:Sample_Stage_Position")


tomo_stage = TomoStage(name="tomo_stage")
samStage = tomo_stage.x
#samStage = tomo_stage.y

#camera_rail = EpicsMotor("2bmb:m31", name="camera_rail", labels=("camera",))
top_z_0 = EpicsMotor("2bmb:m76", name="top_z_0", labels=("top",))
top_x_90 = EpicsMotor("2bmb:m77", name="top_x_90", labels=("top",))
#focus = EpicsMotor("2bmb:m78", name="focus", labels=("camera",))
