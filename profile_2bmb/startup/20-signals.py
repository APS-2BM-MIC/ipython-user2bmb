print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}


class MonaModuleSignals(Device):
    # per ./mona.db
    stop_acquisition = EpicsSignal("mona:StopAcquisition")


class DualPf4FilterBox(Device):
    fPosA = Component(EpicsSignal, "fPosA")
    fPosB = Component(EpicsSignal, "fPosB")
    bankA = Component(EpicsSignalRO, "bankA")
    bankB = Component(EpicsSignalRO, "bankB")
    bitFlagA = Component(EpicsSignalRO, "bitFlagA")
    bitFlagB = Component(EpicsSignalRO, "bitFlagB")
    transmission = Component(EpicsSignalRO, "trans")
    inverse_transmission = Component(EpicsSignalRO, "invTrans")
    thickness_Al_mm = Component(EpicsSignalRO, "filterAl")
    thickness_Ti_mm = Component(EpicsSignalRO, "filterTi")
    energy_keV = Component(EpicsSignal, "E_using")
    mode = Component(EpicsSignal, "useMono", string=True)


class ExperimentInfo(Device):
    GUP_number = Component(EpicsSignalRO, "ProposalNumber", string=True)
    title = Component(EpicsSignalRO, "ProposalTitle", string=True)
    user_name = Component(EpicsSignalRO, "UserName", string=True)
    user_institution = Component(EpicsSignalRO, "UserInstitution", string=True)
    user_badge_number = Component(EpicsSignalRO, "UserBadge", string=True)
    user_email = Component(EpicsSignalRO, "UserEmail", string=True)


class ApsPssShutterWithStatus(APS_devices.ApsPssShutterWithStatus):
    
    @property
    def isOpen(self):
        return self.pss_state.value == self.open_val
    
    @property
    def isClosed(self):
        return self.pss_state.value == self.close_val


try:
    A_shutter = ApsPssShutterWithStatus(
        "2bma:A_shutter", 
        "PA:02BM:STA_A_FES_OPEN_PL", 
        name="A_shutter")
    B_shutter = ApsPssShutterWithStatus(
        "2bma:B_shutter", 
        "PA:02BM:STA_B_SBS_OPEN_PL", 
        name="B_shutter")
except Exception as _exc:
    print(_exc)

# no scans until A_shutter is open
suspend_A_shutter = bluesky.suspenders.SuspendFloor(A_shutter.pss_state, 1)
#suspend_A_shutter.install(RE)
RE.install_suspender(suspend_A_shutter)


mona = MonaModuleSignals(name="mona")

APS = APS_devices.ApsMachineParametersDevice(name="APS")
sd.baseline.append(APS)

aps_current = APS.current
# no scans if APS.current is too low
suspend_APS_current = bluesky.suspenders.SuspendFloor(aps_current, 2, resume_thresh=10)
RE.install_suspender(suspend_APS_current)

#sd.monitors.append(aps_current)

#pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")

user_info = ExperimentInfo("2bmS1:", name="user_info")
sd.baseline.append(user_info)
