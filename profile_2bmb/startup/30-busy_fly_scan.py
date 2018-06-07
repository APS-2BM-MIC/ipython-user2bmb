print(__file__)

"""Aerotech Ensemble PSO scan"""

NUM_FLAT_FRAMES = 10
NUM_DARK_FRAMES = 10
NUM_TEST_FRAMES = 10
ROT_STAGE_FAST_SPEED = 50
SHUTTER_WAIT_TIME_SECONDS = 5


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
    scan_control = Component(EpicsSignal, "scanControl")


psofly = EnsemblePSOFlyDevice("2bmb:PSOFly:", name="psofly")


def motor_set_modulo(motor, modulo):
    if not 0 <= motor.position < modulo:
        yield from bps.mv(motor.set_use_switch, 1)
        yield from bps.mv(motor.user_setpoint, motor.position % modulo)
        yield from bps.mv(motor.set_use_switch, 0)


def _acquire_n_frames(det, quantity):
    """internal: for measuring n darks or flats"""
    yield from bps.mv(det.cam.acquire, 0)
    det.cam.stage_sigs["trigger_mode"] = "Internal"
    det.cam.stage_sigs["image_mode"] = "Multiple"
    det.cam.stage_sigs["num_images"] = quantity
    #for image_number in range(quantity):
    #    yield from bps.trigger(det.cam.acquire)
    yield from bps.trigger(det.cam.acquire)


def measure_darks(det, shutter, quantity):
    """
    measure background of detector
    """
    yield from set_dark_frame()
    yield from bps.abs_set(shutter, "close")
    yield from bps.sleep(SHUTTER_WAIT_TIME_SECONDS)
    yield from _acquire_n_frames(det, quantity)


def measure_flats(det, shutter, quantity, samStage, samPos):
    """
    measure response of detector to empty beam
    """
    priorPosition = samStage.position
    yield from set_white_frame()
    yield from bps.mv(samStage, samPos)
    yield from bps.abs_set(shutter, "open")
    yield from bps.sleep(SHUTTER_WAIT_TIME_SECONDS)
    yield from _acquire_n_frames(det, quantity)
    yield from bps.mv(samStage, priorPosition)


def tomo_scan(*, start=0, stop=180, numProjPerSweep=1500, slewSpeed=5, accl=1, samInPos=0, samOutDist=-3, md=None):
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
    
    acquire_time = 0.01

    staged_device_list = []
    monitored_signals_list = [
        det.image.array_counter,
        rotStage.user_readback,
        ]

    def cleanup():
        for d in [det.image.array_counter, rotStage.user_readback]:
            try:
                yield from bps.unmonitor(d)
            except IllegalMessageSequence:
                pass
        try:
            yield from bps.abs_set(shutter, "close", group='shutter')
        except RuntimeError as exc:
            print(exc)
        yield from bps.mv(rotStage.velocity, ROT_STAGE_FAST_SPEED)
        yield from motor_set_modulo(rotStage, 360.0)
        yield from bps.mv(
            rotStage, 0.00,
            det.cam.trigger_mode, "Internal",
            det.cam.image_mode, "Continuous",
        )
        yield from bps.wait(group='shutter')

    @bpp.stage_decorator(staged_device_list)
    @bpp.run_decorator(md=_md)
    @bpp.finalize_decorator(cleanup)
    def _internal_tomo():
        yield from bps.monitor(rotStage.user_readback, name="rotation")
        yield from bps.monitor(det.image.array_counter, name="array_counter")

        # TODO: test before using!
        # yield from measure_darks(det, shutter, NUM_DARK_FRAMES)
        # yield from measure_flats(det, shutter, NUM_FLAT_FRAMES, samStage, samInPos + samOutDist)

        # do not touch shutter during development
        yield from bps.abs_set(shutter, "open", group="shutter")

        yield from bps.mv(
            det.cam.nd_attributes_file, "monaDetectorAttributes.xml",
            det.cam.acquire_time, acquire_time,
            det.hdf1.num_capture, numProjPerSweep    # + darks & flats
        )
        yield from set_image_frame()

        yield from bps.stop(rotStage)
        yield from motor_set_modulo(rotStage, 360.0)
        
        yield from bps.mv(
            rotStage.velocity, ROT_STAGE_FAST_SPEED, 
            rotStage.acceleration, 3)
        yield from bps.mv(
            rotStage, 0, 
            samStage, samInPos)

        # back off to the taxi point (back-off distance before fly start)
        logging.debug("before taxi")
        yield from bps.mv(
            pso.start, start,
            pso.end, stop,
            pso.scan_control, "Standard",
            pso.scan_delta, 1.0*(stop-start)/numProjPerSweep,
            pso.slew_speed, slewSpeed,
            rotStage.velocity, ROT_STAGE_FAST_SPEED,
            rotStage.acceleration, slewSpeed/accl,
            det.cam.num_images, numProjPerSweep,
            det.cam.trigger_mode, "Overlapped",
            det.cam.trigger_source, "GPIO_0",
            det.cam.trigger_polarity, "Low",
            det.cam.image_mode, "Multiple",
        )
        yield from bps.mv(pso.taxi, "Taxi")
        logging.debug("after taxi")

        # run the fly scan
        logging.debug("before fly")
        yield from bps.mv(rotStage.velocity, slewSpeed)
        yield from bps.wait(group='shutter')    # shutters are slooow, MUST be done now
        yield from set_image_frame()
        #yield from bps.trigger(det, group='fly')
        yield from bps.abs_set(det.cam.acquire, 1)
        yield from bps.abs_set(pso.fly, "Fly", group='fly')
        yield from bps.wait(group='fly')
        yield from bps.abs_set(det.cam.acquire, 0)
        logging.debug("after fly")
        # return rotStage to standard

        # read the camera
        #yield from bps.create(name='primary')
        #yield from bps.read(det)
        #yield from bps.save()

    return (yield from _internal_tomo())
