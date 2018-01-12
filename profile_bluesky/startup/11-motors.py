print(__file__)


# note: see 10-devices.py for how Devices are constructed

A_shutter = AB_Shutter("2bma:A_shutter", name="A_shutter")
B_shutter = AB_Shutter("2bma:B_shutter", name="B_shutter")
A_filter = EpicsSignal("2bma:fltr1:select.VAL", name="A_filter")
A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
A_slit1_h_center = EpicsSignal("2bma:Slit1Hcenter", name="A_slit1_h_center")

tomo_shutter = Motor_Shutter("2bma:m23", name="tomo_shutter")

# generic motor name: {station}m{number}
am7  = EpicsMotor("2bma:m7",  name="am7")     # ? XIASLIT
am25 = EpicsMotor("2bma:m25", name="am25")    # ? DMM_USX
am26 = EpicsMotor("2bma:m26", name="am26")    # ? DMM_USY_OB
am27 = EpicsMotor("2bma:m27", name="am27")    # ? DMM_USY_IB
am28 = EpicsMotor("2bma:m28", name="am28")    # ? DMM_DSX
am29 = EpicsMotor("2bma:m29", name="am29")    # ? DMM_DSY
am30 = EpicsMotor("2bma:m30", name="am30")    # ? USArm
am31 = EpicsMotor("2bma:m31", name="am31")    # ? DSArm
am32 = EpicsMotor("2bma:m32", name="am32")    # ? M2Y

# report these in default `wa` command
BlueskyMagics.positioners += [am7, am25, am26, am27, am28, am29, am30, am31, am32]
BlueskyMagics.positioners += [tomo_shutter.motor]


# TODO: should some of these be part of a Device? sample&rot&pos stages are grouped, for example
am20     = EpicsMotor("2bma:m20", name="am20")              # posStage in A LAT
am46     = EpicsMotor("2bma:m46", name="am46")              # posStage in A SAT
am49     = EpicsMotor("2bma:m49", name="am49")              # sample stage in A
bm82     = ServoRotationStage("2bmb:m82", name="bm82")      # rotation stage in A
bm63     = EpicsMotor("2bmb:m63", name="bm63")              # sample stage in B
bm100    = ServoRotationStage("2bmb:m100", name="bm100")    # rotation stage in B
furnaceY = EpicsMotor("2bma:m55", name="furnaceY")
bm4      = EpicsMotor("2bmb:m4",  name="bm4")               # posStage in B LAT
bm57     = EpicsMotor("2bmb:m57", name="bm57")              # posStage in B SAT

BlueskyMagics.positioners += [am20, am46, am49, bm82, bm63, bm100]
BlueskyMagics.positioners += [furnaceY, bm4, bm57]


# TODO: these are NOT motors!

pso1     = PSO_Device("2bmb:PSOFly1:", name="pso1")
pso2     = PSO_Device("2bmb:PSOFly2:", name="pso2")
tableFly2_sseq_PROC = EpicsSignal(
          "2bmb:tableFly2:sseq2.PROC", name="tableFly2_sseq_PROC")

# TODO: assign more meaningful names?
caputRecorder1 = EpicsSignal("2bmb:caputRecorderGbl_1", name="caputRecorder1", string=True)     # prefix
caputRecorder2 = EpicsSignal("2bmb:caputRecorderGbl_2", name="caputRecorder2", string=True)     # prefix #
caputRecorder3 = EpicsSignal("2bmb:caputRecorderGbl_3", name="caputRecorder3", string=True)     # auto-increase #
caputRecorder4 = EpicsSignal("2bmb:caputRecorderGbl_4", name="caputRecorder4", string=True)     # sample name
caputRecorder5 = EpicsSignal("2bmb:caputRecorderGbl_5", name="caputRecorder5", string=True)     # lens mag
caputRecorder6 = EpicsSignal("2bmb:caputRecorderGbl_6", name="caputRecorder6", string=True)     # sam-det dist(mm)
caputRecorder7 = EpicsSignal("2bmb:caputRecorderGbl_7", name="caputRecorder7", string=True)     # scinThickness(um)
caputRecorder8 = EpicsSignal("2bmb:caputRecorderGbl_8", name="caputRecorder8", string=True)     # scinType
caputRecorder9 = EpicsSignal("2bmb:caputRecorderGbl_9", name="caputRecorder9", string=True)     # filter
caputRecorder10 = EpicsSignal("2bmb:caputRecorderGbl_10", name="caputRecorder10", string=True)  # proj #
caputRecorder_filepath = EpicsSignal("2bmb:caputRecorderGbl_filepath", name="caputRecorder_filepath", string=True)
caputRecorder_filename = EpicsSignal("2bmb:caputRecorderGbl_filename", name="caputRecorder_filename", string=True)

userCalcs_2bmb = userCalcsDevice("2bmb:", name="userCalcs_2bmb")
