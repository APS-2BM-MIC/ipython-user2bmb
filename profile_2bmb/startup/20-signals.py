print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}


class MonaModuleSignals(Device):
    # per ./mona.db
    stop_acquisition = EpicsSignal("mona:StopAcquisition")


class ExperimentInfo(Device):
    GUP_number = Component(EpicsSignalRO, "ProposalNumber", string=True)
    title = Component(EpicsSignalRO, "ProposalTitle", string=True)
    user_name = Component(EpicsSignalRO, "UserName", string=True)
    user_institution = Component(EpicsSignalRO, "UserInstitution", string=True)
    user_badge_number = Component(EpicsSignalRO, "UserBadge", string=True)
    user_email = Component(EpicsSignalRO, "UserEmail", string=True)


try:
    A_shutter = APS_devices.ApsPssShutterWithStatus(
        "2bma:A_shutter", 
        "PA:02BM:STA_A_FES_OPEN_PL", 
        name="A_shutter")
    B_shutter = APS_devices.ApsPssShutterWithStatus(
        "2bma:B_shutter", 
        "PA:02BM:STA_B_SBS_OPEN_PL", 
        name="B_shutter")
except Exception as _exc:
    print(_exc)


mona = MonaModuleSignals(name="mona")

aps = APS_devices.ApsMachineParametersDevice(name="APS")
sd.baseline.append(aps)

aps_current = aps.current
#sd.monitors.append(aps_current)

if aps.inUserOperations:
    # no scans until A_shutter is open
    suspend_A_shutter = bluesky.suspenders.SuspendFloor(A_shutter.pss_state, 1)
    #suspend_A_shutter.install(RE)
    RE.install_suspender(suspend_A_shutter)

    # no scans if aps.current is too low
    suspend_APS_current = bluesky.suspenders.SuspendFloor(aps_current, 2, resume_thresh=10)
    RE.install_suspender(suspend_APS_current)
    pass

#pf4 = APS_devices.DualPf4FilterBox("2bmb:pf4:", name="pf4")

user_info = ExperimentInfo("2bmS1:", name="user_info")
sd.baseline.append(user_info)
