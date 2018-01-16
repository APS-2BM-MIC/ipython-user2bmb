print(__file__)


USER2BMB_ROOT_DIR = "/local/user2bmb"

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')

# note: see 10-devices.py for how Devices are constructed

A_shutter = AB_Shutter("2bma:A_shutter", name="A_shutter")
B_shutter = AB_Shutter("2bma:B_shutter", name="B_shutter")
A_filter = EpicsSignal("2bma:fltr1:select.VAL", name="A_filter")
A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
A_slit1_h_center = EpicsSignal("2bma:Slit1Hcenter", name="A_slit1_h_center")


pso1     = PSO_Device("2bmb:PSOFly1:", name="pso1")
pso2     = PSO_Device("2bmb:PSOFly2:", name="pso2")
tableFly2_sseq_PROC = EpicsSignal(
          "2bmb:tableFly2:sseq2.PROC", name="tableFly2_sseq_PROC")

# TODO: assign more meaningful names?
"""
=== ======================
#   name
=== ======================
1   prefix
2   prefix #
3   auto-increase #
4   sample name
5   lens mag
6   sam-det dist (mm)
7   scinThickness (um)
8   scinType
9   filter
10  proj #
=== ======================
"""
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

interlaceFlySub_2bmb = SynApps_Record_asub("2bmb:iFly:interlaceFlySub", name="interlaceFlySub_2bmb")
savedata_2bmb = SynApps_saveData_Device("2bmb:saveData", name="savedata_2bmb")

preTemp = EpicsSignal("2bmb:ET2k:1:Temperature.VAL", name="preTemp")

userCalcs_2bmb = userCalcsDevice("2bmb:", name="userCalcs_2bmb")
