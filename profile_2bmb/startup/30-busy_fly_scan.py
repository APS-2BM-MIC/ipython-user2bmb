print(__file__)

"""Aerotech Ensemble PSO scan"""

import logging
logger = logging.getLogger(os.path.split(__file__)[-1])

NUM_FLAT_FRAMES = 10
NUM_DARK_FRAMES = 10
NUM_TEST_FRAMES = 10
ROT_STAGE_FAST_SPEED = 50


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
    yield from bps.mv(shutter, "close")
    yield from _acquire_n_frames(det, quantity)


def measure_flats(det, shutter, quantity, samStage, samPos):
    """
    measure response of detector to empty beam
    """
    priorPosition = samStage.position
    yield from set_white_frame()
    yield from bps.mv(
        samStage, samPos,
        shutter, "open")
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
    report_t0 = None
    update_interval_s = 5.0     # during scans, print interim progress
    update_poll_delay_s = 0.01

    stage_sigs = {}
    stage_sigs["det.cam"] = det.cam.stage_sigs

    staged_device_list = [det]
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
            #det.cam.trigger_mode, "Internal",
            #det.cam.image_mode, "Continuous",
            #det.hdf1.enable, "Disable",
            #det.hdf1.capture, "Done",
        )
        yield from bps.wait(group='shutter')

    det.cam.stage_sigs["num_images"] = numProjPerSweep
    det.cam.stage_sigs["trigger_mode"] = "Overlapped"
    det.cam.stage_sigs["trigger_source"] = "GPIO_0"
    det.cam.stage_sigs["trigger_polarity"] = "Low"
    det.cam.stage_sigs["image_mode"] = "Multiple"
    det.hdf1.stage_sigs["num_capture"] = numProjPerSweep  # TODO: + NUM_DARK_FRAMES + NUM_FLAT_FRAMES,

    def _report_(t):
        msg = "{:.2f}s - flying ".format(t)
        msg += "  x = {:.4f}".format(tomo_stage.x.position)
        msg += "  y = {:.4f}".format(tomo_stage.y.position)
        msg += "  r = {:.4f}".format(tomo_stage.rotary.position)
        msg += "  theta = {:.4f}".format(tomo_stage.rotary.position % 360)
        msg += "  image # {}".format(det.cam.num_images_counter.value)
        return msg

    @run_in_thread
    def progress_reporting():
        logger.debug("progress_reporting is starting")
        t = time.time()
        startup = t + update_interval_s/2
        while t < startup and pso.fly.value == 0:    # wait for flyscan to start
            time.sleep(update_poll_delay_s)

        logger.debug("progress_reporting: fly starts")
        update_time = t = report_t0 = time.time()
        while pso.fly.value == 1:
            if t >= update_time:
                update_time = t + update_interval_s
                msg = _report_(t - report_t0)
                print(msg)
                logger.debug(msg)
            time.sleep(update_poll_delay_s)
            t = time.time()
        msg = _report_(time.time() - report_t0)
        print(msg)
        logger.debug(msg)
        logger.debug("{}s - progress_reporting is done".format(time.time()-report_t0))

    @bpp.stage_decorator(staged_device_list)
    @bpp.run_decorator(md=_md)
    @bpp.finalize_decorator(cleanup)
    def _internal_tomo():
        yield from bps.monitor(rotStage.user_readback, name="rotation_monitor")
        yield from bps.monitor(det.image.array_counter, name="array_counter_monitor")
        yield from bps.monitor(tomo_stage.x, name="tomo_stage_x_monitor")

        # prepare the camera and the HDF5 plugin to write data
        yield from bps.mv(
            det.cam.nd_attributes_file, "monaDetectorAttributes.xml",
            det.cam.acquire_time, acquire_time,
            det.hdf1.enable, "Enable",
            det.hdf1.auto_save, "Yes",
        )
        #yield from bps.abs_set(det.hdf1.capture, "Capture")

        # TODO: test before using!
        # yield from measure_darks(det, shutter, NUM_DARK_FRAMES)
        # yield from measure_flats(det, shutter, NUM_FLAT_FRAMES, samStage, samInPos + samOutDist)

        # do not touch shutter during development
        yield from bps.abs_set(shutter, "open", group="shutter")
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
            det.cam.array_counter, 0,
        )

        progress_reporting()
        yield from bps.mv(pso.taxi, "Taxi")
        logging.debug("after taxi")

        # run the fly scan
        logging.debug("before fly")
        yield from bps.mv(rotStage.velocity, slewSpeed)
        yield from bps.wait(group='shutter')    # shutters are slooow, MUST be done now
        yield from set_image_frame()
        yield from bps.trigger(det, group='fly')
        yield from bps.abs_set(pso.fly, "Fly", group='fly')
        yield from bps.wait(group='fly')
        #yield from bps.abs_set(det.cam.acquire, 0)
        logging.debug("after fly")

        # read the camera
        yield from bps.create(name='primary')
        yield from bps.read(det)
        yield from bps.save()
        det.cam.stage_sigs = stage_sigs["det.cam"]

    return (yield from _internal_tomo())

"""
This is the pseudo interlaced fly scan we ran 2018-06-06.
24 rotations with prime number of projections (1511) so that none overlap.
Rotation speed adjusted to ensure that data handling stream can keep up.

    RE(tomo_scan(slewSpeed=50, stop=24*360, numProjPerSweep=1511))

A smaller half-circle scan with 1500 projections must be slower or
the data handling drops frames:

    RE(tomo_scan(slewSpeed=.5))

In the next scan, we plan to move tomo_stage.x by a small amount 
(few microns) during the scan to challenge the reconstructionb
software to correct for a shift of the sample's center position.
Ideally, for sampling purposes, we'll make that shift manually
(outside of BlueSky) about halfway through the scan.

    RE(tomo_scan(slewSpeed=10, stop=24*360, numProjPerSweep=3011), interlace_plan="Tom & Pete", idea="Francesco's bump")        

"""
