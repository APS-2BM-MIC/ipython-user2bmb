print(__file__)

"""various signals at the beam line"""

"""short, recognizable names for controls"""
EPICS_PV_prefix = {}

# such as this area detector
EPICS_PV_prefix["PG3 PointGrey Grasshopper3"] = "2bmbPG3:"

#magic_config["PG3 PointGrey Grasshopper3"] = (PGClass,
#                                              {'name': 'pg_dt', 'prefix': '2bmbPG3:'},)

#for klass, cfg in magic_config.values():
#    ip.user_ns[cfg['name']] = klass(**cfg)


# for area detector file plugins (& other)
USER2BMB_ROOT_DIR = "/local/user2bmb"


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


class APS_Operator_Messages_Device(Device):
    operators = Component(EpicsSignalRO, "OPS:message1", string=True)
    floor_coordinator = Component(EpicsSignalRO, "OPS:message2", string=True)
    fll_pattern = Component(EpicsSignalRO, "OPS:message3", string=True)
    last_problem_message = Component(EpicsSignalRO, "OPS:message4", string=True)
    last_trip_message = Component(EpicsSignalRO, "OPS:message5", string=True)
    # messages 6-8: meaning?
    message6 = Component(EpicsSignalRO, "OPS:message6", string=True)
    message7 = Component(EpicsSignalRO, "OPS:message7", string=True)
    message8 = Component(EpicsSignalRO, "OPS:message8", string=True)


class APS_Machine_Parameters_Device(Device):
    current = Component(EpicsSignalRO, "S:SRcurrentAI")
    lifetime = Component(EpicsSignalRO, "S:SRlifeTimeHrsCC")
    machine_status = Component(EpicsSignalRO, "S:DesiredMode", string=True)
    operating_mode = Component(EpicsSignalRO, "S:ActualMode", string=True)
    shutter_permit = Component(EpicsSignalRO, "ACIS:ShutterPermit", string=True)
    fill_number = Component(EpicsSignalRO, "S:FillNumber")
    orbit_correction = Component(EpicsSignalRO, "S:OrbitCorrection:CC")
    global_feedback = Component(EpicsSignalRO, "SRFB:GBL:LoopStatusBI", string=True)
    global_feedback_h = Component(EpicsSignalRO, "SRFB:GBL:HLoopStatusBI", string=True)
    global_feedback_v = Component(EpicsSignalRO, "SRFB:GBL:VLoopStatusBI", string=True)
    operator_messages = Component(APS_Operator_Messages_Device)


APS = APS_Machine_Parameters_Device(name="APS")
aps_current = APS.current

sd.baseline.append(APS)


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
