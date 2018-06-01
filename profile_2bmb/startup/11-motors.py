print(__file__)

"""motors"""

from ophyd import MotorBundle


class SampleStage(MotorBundle):
    rotary = Component(EpicsMotor, "2bmb:m100", labels=("theta", "sample"))
    x = Component(EpicsMotor, "2bmb:m63", labels=("sample",))
    y = Component(EpicsMotor, "2bmb:m57", labels=("sample",))
    pitch = Component(EpicsMotor, "2bmb:m54", labels=("sample",))
    roll = Component(EpicsMotor, "2bmb:m53", labels=("sample",))
    changer_status = Component(EpicsSignalRO, "2bmb:Begin_Scan")
    position_status = Component(EpicsSignalRO, "2bmb:Sample_Stage_Position")

class TomoStage(MotorBundle):
    rotary = Component(EpicsMotor, "2bmb:m34", labels=("theta", "tomo"))
    x = Component(EpicsMotor, "2bmb:m52", labels=("tomo",))
    y = Component(EpicsMotor, "2bmb:m50", labels=("tomo",))


sample_stage = SampleStage(name="sample_stage")

camera_rail = EpicsMotor("2bmb:m31", name="camera_rail", labels=("camera",))
top_z_0 = EpicsMotor("2bmb:m76", name="top_z_0", labels=("top",))
top_x_90 = EpicsMotor("2bmb:m77", name="top_x_90", labels=("top",))
focus = EpicsMotor("2bmb:m78", name="focus", labels=("camera",))
