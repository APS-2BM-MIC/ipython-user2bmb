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

APS = APS_devices.ApsMachineParametersDevice(name="APS")
aps_current = APS.current

sd.baseline.append(APS)
#sd.monitors.append(aps_current)

#pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")

computed_theta = EpicsSignal("2bmb:DX:theta", name="computed_theta")

user_info = ExperimentInfo("2bmS1:", name="user_info")
sd.baseline.append(user_info)
