print(__file__)
from ophyd import (PVPositioner, EpicsMotor, EpicsSignal, EpicsSignalRO,
                   PVPositionerPC, Device)
from ophyd import Component as Cpt


# note: see 10-devices.py for more stages, slits, and more

# TODO: this block is an example
m1 = EpicsMotor('2bmb:m1', name='m1')
m2 = EpicsMotor('2bmb:m2', name='m2')
m3 = EpicsMotor('2bmb:m3', name='m3')
m4 = EpicsMotor('2bmb:m4', name='m4')

m5 = EpicsMotor('2bmb:m5', name='m5')
m6 = EpicsMotor('2bmb:m6', name='m6')
m7 = EpicsMotor('2bmb:m7', name='m7')
m8 = EpicsMotor('2bmb:m8', name='m8')


A_shutter = AB_Shutter("2bma:A_shutter, "A_shutter")
B_shutter = AB_Shutter("2bma:B_shutter, "B_shutter")
A_filter = EpicsSignal("2bma:fltr1:select.VAL", name="A_filter")
A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
A_slit1_h_center = EpicsSignal("2bma:Slit1Hcenter", name="A_slit1_h_center")

tomo_shutter = Motor_Shutter("2bma:m23", "tomo_shutter")

# generic motor name: {station}m{number}
am7 = EpicsMotor("2bma:m7", name="am7")    # ? XIASLIT
am25 = EpicsMotor("2bma:m25", name="am25")    # ? DMM_USX
am26 = EpicsMotor("2bma:m26", name="am26")    # ? DMM_USY_OB
am27 = EpicsMotor("2bma:m27", name="am27")    # ? DMM_USY_IB
am28 = EpicsMotor("2bma:m28", name="am28")    # ? DMM_DSX
am29 = EpicsMotor("2bma:m29", name="am29")    # ? DMM_DSY
am30 = EpicsMotor("2bma:m30", name="am30")    # ? USArm
am31 = EpicsMotor("2bma:m31", name="am31")    # ? DSArm
am32 = EpicsMotor("2bma:m32", name="am32")    # ? M2Y


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

pso1     = PSO_Device("2bmb:PSOFly1:", name="pso1")
pso2     = PSO_Device("2bmb:PSOFly2:", name="pso2")
tableFly2_sseq_PROC = EpicsSignal(
          "2bmb:tableFly2:sseq2.PROC", name="tableFly2_sseq_PROC")

pco_dimax = MyPcoDetector("PCOIOC2:", name="pco_dimax")  # TODO: check PV prefix
pco_edge = MyPcoDetector("PCOIOC3:", name="pco_edge")  # TODO: check PV prefix

caputRecorder1 = EpicsSignal("2bmb:caputRecorderGbl_1", name="caputRecorder1", string=True)
caputRecorder2 = EpicsSignal("2bmb:caputRecorderGbl_2", name="caputRecorder2", string=True)
caputRecorder3 = EpicsSignal("2bmb:caputRecorderGbl_3", name="caputRecorder3", string=True)
caputRecorder4 = EpicsSignal("2bmb:caputRecorderGbl_4", name="caputRecorder4", string=True)
caputRecorder5 = EpicsSignal("2bmb:caputRecorderGbl_5", name="caputRecorder5", string=True)
caputRecorder6 = EpicsSignal("2bmb:caputRecorderGbl_6", name="caputRecorder6", string=True)
caputRecorder7 = EpicsSignal("2bmb:caputRecorderGbl_7", name="caputRecorder7", string=True)
caputRecorder8 = EpicsSignal("2bmb:caputRecorderGbl_8", name="caputRecorder8", string=True)
caputRecorder9 = EpicsSignal("2bmb:caputRecorderGbl_9", name="caputRecorder9", string=True)
caputRecorder10 = EpicsSignal("2bmb:caputRecorderGbl_10", name="caputRecorder10", string=True)
caputRecorder_filename = EpicsSignal("2bmb:caputRecorderGbl_filename", name="caputRecorder_filename", string=True)
caputRecorder_filepath = EpicsSignal("2bmb:caputRecorderGbl_filepath", name="caputRecorder_filepath", string=True)
