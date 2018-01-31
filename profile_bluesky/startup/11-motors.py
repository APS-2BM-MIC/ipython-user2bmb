print(__file__)

"""motors, stages, positioners, ..."""

tomo_shutter = Motor_Shutter("2bma:m23", name="tomo_shutter")

# generic motor name: {station}m{number}
am6  = EpicsMotor("2bma:m6",  name="am6")     # ?
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
append_wa_motor_list(am6, am7, am25, am26, am27, am28, am29, am30, am31, am32)
append_wa_motor_list(tomo_shutter.motor)


# TODO: should some of these be part of a Device? sample&rot&pos stages are grouped, for example
am20     = EpicsMotor("2bma:m20", name="am20")              # posStage in A LAT
am46     = EpicsMotor("2bma:m46", name="am46")              # posStage in A SAT
am49     = EpicsMotor("2bma:m49", name="am49")              # sample stage in A
bm82     = EpicsMotorWithServo("2bmb:m82", name="bm82")     # rotation stage in A
bm63     = EpicsMotor("2bmb:m63", name="bm63")              # sample stage in B
bm100    = EpicsMotorWithServo("2bmb:m100", name="bm100")   # rotation stage in B
furnaceY = EpicsMotor("2bma:m55", name="furnaceY")
bm4      = EpicsMotor("2bmb:m4",  name="bm4")               # posStage in B LAT
bm57     = EpicsMotor("2bmb:m57", name="bm57")              # posStage in B SAT
bm58     = EpicsMotor("2bmb:m58", name="bm58")              # samStage in B SAT

append_wa_motor_list(am20, am46, am49, bm82, bm63, bm100)
append_wa_motor_list(furnaceY, bm4, bm57, bm58)

s1m1 = EpicsMotor("2bmS1:m1", name="s1m1")
s1m2 = EpicsMotor("2bmS1:m2", name="s1m2")

append_wa_motor_list(s1m1, s1m2)
