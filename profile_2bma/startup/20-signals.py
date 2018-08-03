print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}


class MonaModuleSignals(Device):
    # per ./mona.db
    stop_acquisition = EpicsSignal("mona:StopAcquisition")

mona = MonaModuleSignals(name="mona")


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


APS = ApsMachineParametersDevice(name="APS")
aps_current = APS.current

sd.baseline.append(APS)
#sd.monitors.append(aps_current)


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


#pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")
