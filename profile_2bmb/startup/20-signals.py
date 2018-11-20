print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}


class MonaModuleSignals(Device):
    # per ./mona.db
    stop_acquisition = EpicsSignal("2bmbmona:StopAcquisition")


class ExperimentInfo(Device):
    GUP_number = Component(EpicsSignalRO, "ProposalNumber", string=True)
    title = Component(EpicsSignalRO, "ProposalTitle", string=True)
    user_name = Component(EpicsSignalRO, "UserName", string=True)
    user_institution = Component(EpicsSignalRO, "UserInstitution", string=True)
    user_badge_number = Component(EpicsSignalRO, "UserBadge", string=True)
    user_email = Component(EpicsSignalRO, "UserEmail", string=True)


instrument_in_use = EpicsSignalRO(
    "2bm:instrument_in_use", 
    name="instrument_in_use")

def operations_in_2bmb():
    """returns True if allowed to use X-ray beam in 2-BM-B station"""
    v = instrument_in_use.value
    enums = instrument_in_use.enum_strs
    return enums[v] == "2-BM-B"

# pause if this value changes in our session
# note: this suspender is designed to require Bluesky restart if value changes
suspend_instrument_in_use = SuspendWhenChanged(instrument_in_use)
RE.install_suspender(suspend_instrument_in_use)


mona = MonaModuleSignals(name="mona")


aps = APS_devices.ApsMachineParametersDevice(name="APS")
sd.baseline.append(aps)
aps_current = aps.current


user_info = ExperimentInfo("2bmS1:", name="user_info")
sd.baseline.append(user_info)


if operations_in_2bmb() and aps.inUserOperations:
    # setup for operations using the X-ray beam
    
    # record storage ring current as additional data stream
    sd.monitors.append(aps.current)

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

    # no scans until A_shutter is open
    suspend_A_shutter = bluesky.suspenders.SuspendFloor(A_shutter.pss_state, 1)
    #suspend_A_shutter.install(RE)
    RE.install_suspender(suspend_A_shutter)

    # no scans if aps.current is too low
    suspend_APS_current = bluesky.suspenders.SuspendFloor(aps_current, 2, resume_thresh=10)
    RE.install_suspender(suspend_APS_current)

else:
    # setup for test mode without the beam
    
    # define the simulated shutter objects here
    A_shutter = APS_devices.SimulatedApsPssShutterWithStatus(name="A_shutter")
    B_shutter = APS_devices.SimulatedApsPssShutterWithStatus(name="B_shutter")

    # pete's testing items (not EPICS, just ophyd)
    import ophyd.sim
    m1 = ophyd.sim.motor
    sig = ophyd.sim.noisy_det   # Gaussian(m1), sigma=1, x0=0, 10% noise, max=1
    #  RE(bp.scan([sig], m1, -3, 3, 12))


#pf4 = APS_devices.DualPf4FilterBox("2bmb:pf4:", name="pf4")
