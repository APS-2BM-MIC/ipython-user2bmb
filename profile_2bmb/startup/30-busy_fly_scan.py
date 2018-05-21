print(__file__)

"""soft glue scan"""

bmb100 = EpicsMotor("2bmb:m100", name="bmb100")

class EnsemblePSOFlyDevice(TaxiFlyScanDevice):
    motor_pv_name = Component(EpicsSignalRO, "motorName")
    start = Component(EpicsSignal, "startPos")
    end = Component(EpicsSignal, "endPos")
    slew_speed = Component(EpicsSignal, "slewSpeed")
    
    # scan_delta: output a trigger pulse when motor moves this increment
    scan_delta = Component(EpicsSignal, "scanDelta")

    # advanced controls
    delta_time = Component(EpicsSignalRO, "deltaTime")
    # detector_setup_time = Component(EpicsSignal, "detSetupTime")
    # pulse_type = Component(EpicsSignal, "pulseType")


psofly = EnsemblePSOFlyDevice("2bmb:PSOFly:", name="psofly")


def simple_demo():
    motor = bmb100
    print("rotary stage position: {}".format(motor.position))
    m_start = motor.position
    yield from bps.mv(motor, 0)
    print("rotary stage position: {}".format(motor.position))
    yield from psofly.plan()
    print("rotary stage position: {}".format(motor.position))
    yield from bps.mv(motor, m_start)
    print("rotary stage position: {}".format(motor.position))
