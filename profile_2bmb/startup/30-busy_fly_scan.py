print(__file__)

"""soft glue scan"""


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
    
    # TODO: complete
    # https://github.com/prjemian/ipython_mintvm/blob/master/profile_bluesky/startup/notebooks/busy_fly_scan.ipynb


psofly = EnsemblePSOFlyDevice("2bmb:PSOFly:", name="psofly")


def simple_demo():
    motor = sample_stage.rotary
    print("rotary stage position: {}".format(motor.position))
    m_start = motor.position
    yield from bps.mv(motor, 0)
    print("rotary stage position: {}".format(motor.position))
    yield from psofly.plan()
    print("rotary stage position: {}".format(motor.position))
    yield from bps.mv(motor, m_start)
    print("rotary stage position: {}".format(motor.position))
