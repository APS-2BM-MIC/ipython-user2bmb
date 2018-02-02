print(__file__)


USER2BMB_ROOT_DIR = "/local/user2bmb"

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

# note: see 10-devices.py for how Devices are constructed

A_shutter = ApsPssShutter("2bma:A_shutter", name="A_shutter")
B_shutter = ApsPssShutter("2bma:B_shutter", name="B_shutter")

tomo_shutter = EpicsMotorShutter("2bma:m23", name="tomo_shutter")
append_wa_motor_list(tomo_shutter.motor)

A_filter = EpicsSignal("2bma:fltr1:select.VAL", name="A_filter")
A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
A_slit1_h_center = EpicsSignal("2bma:Slit1Hcenter", name="A_slit1_h_center")


pso1     = PSO_Device("2bmb:PSOFly1:", name="pso1")
pso2     = PSO_Device("2bmb:PSOFly2:", name="pso2")
tableFly2_sseq_PROC = EpicsSignal(
          "2bmb:tableFly2:sseq2.PROC", name="tableFly2_sseq_PROC")

# assign meaningful names
# "cpr" means caputRecorder
cpr_prefix          = EpicsSignal("2bmb:caputRecorderGbl_1", name="cpr_prefix", string=True)
cpr_prefix_num      = EpicsSignal("2bmb:caputRecorderGbl_2", name="cpr_prefix_num", string=True)
cpr_auto_increase   = EpicsSignal("2bmb:caputRecorderGbl_3", name="cpr_auto_increase", string=True)
cpr_sample_name     = EpicsSignal("2bmb:caputRecorderGbl_4", name="cpr_sample_name", string=True)
cpr_lens_mag        = EpicsSignal("2bmb:caputRecorderGbl_5", name="cpr_lens_mag", string=True)
cpr_sam_det_dist    = EpicsSignal("2bmb:caputRecorderGbl_6", name="cpr_sam_det_dist", string=True)
cpr_scin_thickness  = EpicsSignal("2bmb:caputRecorderGbl_7", name="cpr_scin_thickness", string=True)
cpr_scin_type       = EpicsSignal("2bmb:caputRecorderGbl_8", name="cpr_scin_type", string=True)
cpr_filter          = EpicsSignal("2bmb:caputRecorderGbl_9", name="cpr_filter", string=True)
cpr_proj_num        = EpicsSignal("2bmb:caputRecorderGbl_10", name="cpr_proj_num", string=True)
cpr_filepath        = EpicsSignal("2bmb:caputRecorderGbl_filepath", name="cpr_filepath", string=True)
cpr_filename        = EpicsSignal("2bmb:caputRecorderGbl_filename", name="cpr_filename", string=True)

cpr_arg9  = EpicsSignal("2bmb:caputRecorderArg9Value.VAL",  name="cpr_arg9")
cpr_arg13 = EpicsSignal("2bmb:caputRecorderArg13Value.VAL", name="cpr_arg13")
cpr_arg14 = EpicsSignal("2bmb:caputRecorderArg14Value.VAL", name="cpr_arg14")

interlaceFlySub_2bmb = SynApps_Record_asub("2bmb:iFly:interlaceFlySub", name="interlaceFlySub_2bmb")
savedata_2bmb = SynApps_saveData_Device("2bmb:saveData", name="savedata_2bmb")

preTemp = EpicsSignal("2bmb:ET2k:1:Temperature.VAL", name="preTemp")

userCalcs_2bmb = userCalcsDevice("2bmb:", name="userCalcs_2bmb")
s1_d1dmm_calc = EpicsSignal("2bmS1:D1Dmm_calc", name="s1_d1dmm_calc")
s1_d1done_read = EpicsSignal("2bmS1:D1done_read", name="s1_d1done_read")
