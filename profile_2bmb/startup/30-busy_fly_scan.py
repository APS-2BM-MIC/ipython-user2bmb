import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky import IllegalMessageSequence

print(__file__)

"""Aerotech Ensemble PSO scan"""

NUM_FLAT_FRAMES = 10
NUM_DARK_FRAMES = 10
NUM_TEST_FRAMES = 10
ROT_STAGE_FAST_SPEED = 50


# scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep


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


def motor_set_modulo(motor, modulo):
    if not 0 <= motor.value < modulo:
        yield from bps.mv(motor.set_use_switch, 1)
        yield from bps.mv(motor.user_setpoint, motor.position % modulo)
        yield from bps.mv(motor.set_use_switch, 0)


def _init_tomo_fly_(*, samInPos=0, start=0, stop=180, numProjPerSweep=1500, slewSpeed=10, accl=1):
    pso = psofly
    #samStage = tomo_stage.x
    rotStage = tomo_stage.rotary
    det = pg3_det
    shutter = B_shutter

    yield from bps.mv(det.cam.nd_attributes_file, "monaDetectorAttributes.xml")
    yield from set_image_frame()

    yield from bps.stop(rotStage)
    yield from motor_set_modulo(rotStage, 360.0)

    yield from bps.mv(rotStage, 0)
    yield from bps.mv(samStage, samInPos)

    # TODO: anything from _plan_edgeSet() needed? (Feb 2018 setup: 50-plans.py)


def _set_pso_stage_sigs(pso, rotStage, angStart, angEnd, scanDelta,
                        slewSpeed, acclTime):

    pso.stage_sigs["start_pos"] = angStart
    pso.stage_sigs["end_pos"] = angEnd
    pso.stage_sigs["scan_delta"] = scanDelta
    pso.stage_sigs["slew_speed"] = slewSpeed
    rotStage.stage_sigs["velocity"] = ROT_STAGE_STANDARD_SPEED
    rotStage.stage_sigs["acceleration"] = 3

    # rotStage.stage_sigs["acceleration"] = acclTime



def tomo_scan(*, start=0, stop=180, numProjPerSweep=1500, slewSpeed=10, accl=1, md=None):
    """
    standard tomography fly scan with BlueSky
    """
    _md = md or OrderedDict()
    _md["project"] = "mona"
    _md["APS_storage_ring_current,mA"] = aps_current.value
    _md["datetime_plan_started"] = str(datetime.now())

    pso = psofly
    det = pg3_det
    rotStage = tomo_stage.rotary
    shutter = B_shutter

    staged_device_list = [det]
    monitored_signals_list = [
        det.image.array_counter,
        rotStage.user_readback,
        ]

    _set_pso_stage_sigs(pso, rotstage, start, stop, scanDelta, slewSpeed, None)

    def cleanup():
        for d in [det.image.array_counter, theta.user_readback]:
            try:
                yield from bps.unmonitor(d)
            except IllegalMessageSequence:
                pass
        yield from bps.abs_set(shutter, "close", group='shutter')
        yield from bps.mv(rotStage, 0.00)
        yield from bps.wait(group='shutter')

    @bpp.stage_decorator(staged_device_list)
    @bpp.run_decorator(md=_md)
    @bpp.finalize_decorator(cleanup)
    def _internal_tomo():
        yield from bps.monitor(rotStage.user_readback, name="rotation")
        yield from bps.monitor(det.image.array_counter, name="array_counter")

        yield from _init_tomo_fly_(
            start=start,
            stop=stop,
            numProjPerSweep=numProjPerSweep,
            slewSpeed=slewSpeed)

        # do not touch shutter during development
        yield from bps.abs_set(shutter, "open")

        # back off to the taxi point (back-off distance before fly start)
        yield from bps.mv(pso.taxi, "Taxi")

        rotStage.stage_sigs["velocity"] = slewSpeed

        # run the fly scan
        yield from bps.trigger(det.cam.acquire, group='fly')
        yield from bps.abs_set(pso.fly, "Fly", group='fly')
        yield from bps.wait(group='fly')

        # read the camera
        yield from bps.create(name='primary')
        yield from bps.read(det)
        yield from bps.save()
        # return rotStage to standard
        rotStage.stage_sigs["velocity"] = ROT_STAGE_RETURN_SPEED

    return (yield from _internal_tomo())
