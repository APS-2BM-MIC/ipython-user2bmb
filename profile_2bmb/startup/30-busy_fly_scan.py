print(__file__)

"""Aerotech Ensemble PSO scan"""

import logging
logger = logging.getLogger(os.path.split(__file__)[-1])

NUM_FLAT_FRAMES = 10
NUM_DARK_FRAMES = 10
NUM_TEST_FRAMES = 10
ROT_STAGE_FAST_SPEED = 50

MEASURE_DARKS_AND_FLATS = True


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

    scan_control = Component(EpicsSignal, "scanControl")


psofly = EnsemblePSOFlyDevice("2bmb:PSOFly:", name="psofly")


def motor_set_modulo(motor, modulo):
    if not 0 <= motor.position < modulo:
        yield from bps.mv(motor.set_use_switch, 1)
        yield from bps.mv(motor.user_setpoint, motor.position % modulo)
        yield from bps.mv(motor.set_use_switch, 0)


@APS_plans.run_in_thread
def addThetaArray(hdf5_file_name, start, stop, step):
    if not os.path.exists(hdf5_file_name):
        print("Could not find {}".format(hdf5_file_name))
        print("Cannot add /exchange/theta")
        return
    
    print("Adding /exchange/theta to {}".format(hdf5_file_name))

    theta = np.arange(start, stop, step)
    # theta = theta % 360

    with h5py.File(hdf5_file_name, "r+") as fp:
        # R/W, file must exist or fail
        exchange = fp["/exchange"]
        ds = exchange.create_dataset("theta", data=theta)
        ds.attrs["units"] = "degrees"
        ds.attrs["description"] = "computed rotation stage angle"


def wait_for_hdf5_captured(det, expected):
    while det.hdf1.num_captured.value < expected:
        yield from bps.sleep(0.01)


def measure_darks(det, shutter, expected, quantity):
    """
    measure background of detector
    
    det : area detector object
    shutter : shutter object
    quantity : number of frames to acquire
    """
    yield from bps.mv(
        shutter, "close",
        det.cam.trigger_mode, "Internal",
        det.cam.frame_type, 1,  # dark
        det.cam.num_images, quantity,
    )
    print("{} Darks, Shutter {}".format(quantity, shutter.pss_state.get(as_string=True)))

    yield from bps.trigger(det)
    yield from wait_for_hdf5_captured(det, expected)


def measure_flats(det, shutter, quantity, expected, samStage, samPos):
    """
    measure response of detector to empty beam
    """
    priorPosition = samStage.position
    yield from bps.sleep(1)     # arbitrary, shutter won't move without it
    yield from bps.mv(
        shutter, "open",
        samStage, samPos,
        det.cam.trigger_mode, "Internal",
        det.cam.frame_type, 2,  # white
        det.cam.num_images, quantity,
    )
    print("{} Flats, Shutter {}".format(quantity, shutter.pss_state.get(as_string=True)))

    yield from bps.trigger(det)
    yield from wait_for_hdf5_captured(det, expected)

    yield from bps.mv(samStage, priorPosition)


def tomo_scan(*, start=0, stop=180, numProjPerSweep=1500, slewSpeed=5, accl=1, samInPos=0, samOutDist=-3, acquire_time=0.02, md=None):
    """
    standard tomography fly scan with BlueSky
    """
    _md = md or OrderedDict()
    _md["project"] = "mona"
    _md["APS_storage_ring_current,mA"] = aps_current.value
    _md["datetime_plan_started"] = str(datetime.now())
    _md["tomo parameters"] = dict(
        start = start,
        stop = stop,
        numProjPerSweep = numProjPerSweep,
        slewSpeed = slewSpeed,
        accl = accl,
        samInPos = samInPos,
        samOutDist = samOutDist,
        acquire_time = acquire_time,
    )

    # assigns darks, whites, images to proper datasets in HDF5 file
    det = pg3_det
    try:
        APS_devices.AD_setup_FrameType(
            EPICS_PV_prefix["PG3 PointGrey Grasshopper3"], 
            scheme="DataExchange"
        )
    except NameError as _exc:
        print("advisory: APS_devices.AD_setup_FrameType error", _exc)
    pso = psofly
    rotStage = tomo_stage.rotary
    shutter = B_shutter
    
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
        # stop any in-progress motion
        try:
            yield from bps.abs_set(rotStage.motor_stop, 1)
        except RuntimeError:
            pass
        yield from bps.wait(group='shutter')
        yield from bps.mv(
            psofly.taxi, 0,
            psofly.fly, 0,
        )

        # stop detector acquisition
        # note: set by numerical value, not enumeration text
        # since RBV returns a number, value here and RBV must match
        yield from bps.abs_set(det.cam.acquire, 0)
        yield from bps.abs_set(det.hdf1.capture, 0)
        yield from bps.abs_set(det.hdf1.enable, 0)
        
        # clear the stop flag
        yield from bps.abs_set(mona.stop_acquisition, 0)

        # send the motor to 0
        yield from bps.mv(rotStage.velocity, ROT_STAGE_FAST_SPEED)
        yield from motor_set_modulo(rotStage, 360.0)
        yield from bps.mv(rotStage, 0.00)

    det.cam.stage_sigs["num_images"] = numProjPerSweep
    det.cam.stage_sigs["trigger_mode"] = "Overlapped"
    det.cam.stage_sigs["trigger_source"] = "GPIO_0"
    det.cam.stage_sigs["trigger_polarity"] = "Low"
    det.cam.stage_sigs["image_mode"] = "Multiple"

    total_number_frames = numProjPerSweep
    if MEASURE_DARKS_AND_FLATS:
        total_number_frames += NUM_DARK_FRAMES + NUM_FLAT_FRAMES

    def _report_(t):
        msg = "{:.2f}s - flying ".format(t)
        msg += "  x = {:.4f}".format(tomo_stage.x.position)
        msg += "  y = {:.4f}".format(tomo_stage.y.position)
        msg += "  r = {:.4f}".format(tomo_stage.rotary.position)
        msg += "  theta = {:.4f}".format(tomo_stage.rotary.position % 360)
        msg += "  image # {}".format(det.cam.num_images_counter.value)
        return msg

    @APS_plans.run_in_thread
    def progress_reporting():
        logger.debug("progress_reporting is starting")
        t = time.time()
        startup = t + update_interval_s/2
        while t < startup and pso.fly.get(timeout=2) == 0:    # wait for flyscan to start
            time.sleep(update_poll_delay_s)

        logger.debug("progress_reporting: fly starts")
        update_time = t = report_t0 = time.time()
        last_image_number = det.cam.num_images_counter.value
        while pso.fly.get(timeout=2) == 1:
            image_number = det.cam.num_images_counter.value
            if t >= update_time or (image_number == 1 and last_image_number != image_number):
                update_time = t + update_interval_s
                msg = _report_(t - report_t0)
                print(msg)
                logger.debug(msg)
            time.sleep(update_poll_delay_s)
            t = time.time()
            last_image_number = image_number
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
            det.cam.array_counter, 0,
            det.hdf1.num_capture, total_number_frames,
        )

        if MEASURE_DARKS_AND_FLATS:
            yield from measure_darks(det, shutter, NUM_DARK_FRAMES, NUM_DARK_FRAMES)

            yield from measure_flats(
                det, 
                shutter, 
                NUM_FLAT_FRAMES, 
                NUM_DARK_FRAMES + NUM_FLAT_FRAMES,
                samStage, samInPos + samOutDist
            )

        # !!! moves the shutter !!!
        yield from bps.abs_set(shutter, "open", group="shutter")

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
        _delta = 1.0*(stop-start)/numProjPerSweep
        _delta = float("%.4f" % _delta) # oooo wow! this cost us some time.  Why?
        yield from bps.mv(
            pso.start, start,
            pso.end, stop,
            pso.scan_control, "Standard",
            pso.scan_delta, _delta,
            pso.slew_speed, slewSpeed,
            rotStage.velocity, ROT_STAGE_FAST_SPEED,
            rotStage.acceleration, slewSpeed/accl,
        )

        progress_reporting()
        t0 = time.time()
        yield from bps.mv(pso.taxi, "Taxi")
        print(datetime.now(), "taxi time: {} s".format(time.time()-t0))
        logging.debug("after taxi")

        # run the fly scan
        logging.debug("before fly")
        yield from bps.mv(rotStage.velocity, slewSpeed)
        yield from bps.wait(group='shutter')    # shutters are slooow, MUST be done now

        yield from bps.mv(
            det.cam.frame_type, 0,      # normal images
            det.cam.num_images, numProjPerSweep,
            det.cam.trigger_mode, "Overlapped",
        )
        yield from bps.trigger(det, group='fly')
        t0 = time.time()
        yield from bps.abs_set(pso.fly, "Fly", group='fly')
        yield from bps.wait(group='fly')
        print(datetime.now(), "fly time: {} s".format(time.time()-t0))
        #yield from bps.abs_set(det.cam.acquire, 0)
        logging.debug("after fly")

        # read the camera
        yield from bps.create(name='primary')
        yield from bps.read(det)
        yield from bps.save()
        det.cam.stage_sigs = stage_sigs["det.cam"]
        
        hdf5_file_name = det.hdf1.full_file_name.value
        addThetaArray(hdf5_file_name, start, stop, _delta)

    return (yield from _internal_tomo())

"""
This is the pseudo interlaced fly scan we ran 2018-06-06.
24 rotations with prime number of projections (1511) so that none overlap.
Rotation speed adjusted to ensure that data handling stream can keep up.

    RE(tomo_scan(slewSpeed=50, stop=24*360, numProjPerSweep=1511))

A smaller half-circle scan with 1500 projections must be slower or
the data handling drops frames:

    RE(tomo_scan(slewSpeed=.5))
    RE(tomo_scan(slewSpeed=5, numProjPerSweep=151))

In the next scan, we plan to move tomo_stage.x by a small amount 
(few microns) during the scan to challenge the reconstructionb
software to correct for a shift of the sample's center position.
Ideally, for sampling purposes, we'll make that shift manually
(outside of BlueSky) about halfway through the scan.

    RE(tomo_scan(slewSpeed=10, stop=24*360, numProjPerSweep=3011), interlace_plan="Tom & Pete", idea="Francesco's bump")        

    RE(tomo_scan(slewSpeed=10, stop=24*360, numProjPerSweep=3011), sample="wood stick")        

"""


def calc_blur_pixel(exposure_time, readout_time, camera_size_x, angular_range, number_of_proj):
    """
    Calculate the blur error (pixel units) due to a rotary stage fly scan motion durng the exposure.
    
    Parameters
    ----------
    exposure_time: float
        Detector exposure time
    readout_time : float
        Detector read out time
    camera_size_x : int
        Detector X size
    angular_range : float
        Tomographic scan angular range
    number_of_proj : int
        Numember of projections

    Returns
    -------
    float
        Blur error in pixel. For good quality reconstruction this should be < 0.2 pixel.
    """

    angular_step = angular_range/number_of_proj
    scan_time = number_of_proj * (exposure_time + readout_time)
    rot_speed = angular_range / scan_time
    frame_rate = number_of_proj / scan_time
    blur_delta = exposure_time * rot_speed
    
    mid_detector = camera_size_x / 2.0
    blur_pixel = mid_detector * (1 - np.cos(blur_delta * np.pi /180.))

    #print("*************************************")
    #print("Total # of proj: ", number_of_proj)
    #print("Exposure Time: ", exposure_time, "s")
    #print("Readout Time: ", readout_time, "s")
    #print("Angular Range: ", angular_range, "degrees")
    #print("Camera X size: ", camera_size_x)
    #print("*************************************")
    #print("Angular Step: ", angular_step, "degrees")   
    #print("Scan Time: ", scan_time ,"s") 
    #print("Rot Speed: ", rot_speed, "degrees/s")
    #print("Frame Rate: ", frame_rate, "fps")
    #print("Blur: ", blur_pixel, "pixels")
    #print("*************************************")
    
    return blur_pixel, rot_speed, scan_time


def calc_acquisition(blur_pixel, exposure_time, readout_time, camera_size_x, angular_range, number_of_proj):
    """
    Calculate frame rate and rotation speed for a desired blur error t

    Parameters
    ----------
    blur_pixel : float
        Desired blur error. For good quality reconstruction this should be < 0.2 pixel.
    exposure_time: float
        Detector exposure time
    readout_time : float
        Detector read out time
    camera_size_x : int
        Detector X size
    angular_range : float
        Tomographic scan angular range
    number_of_proj : int
        Number of projections

    Returns
    -------
    float
        frame_rate, rot_speed
    """

    mid_detector = camera_size_x / 2.0
    delta_blur  = np.arccos(1 - blur_pixel / mid_detector) * 180.0 / np.pi
    rot_speed = delta_blur  / exposure_time

    scan_time = angular_range / rot_speed
    frame_rate = number_of_proj / scan_time
    print("*************************************")
    print("Total # of proj: ", number_of_proj)
    print("Exposure Time: ", exposure_time, "s")
    print("Readout Time: ", readout_time, "s")
    print("Angular Range: ", angular_range, "degrees")
    print("Camera X size: ", camera_size_x)
    print("Blur Error: ", blur_pixel, "pixels")
    print("*************************************")
    print("Rot Speed: : ", rot_speed, "degrees/s")
    print("Scan Time:: ", scan_time, "s")
    print("Frame Rate: ", frame_rate, "fps")
    print("*************************************")
  
    return frame_rate, rot_speed


__tomo_scan_counter = 0       # used internally by user_tomo_scan

def user_tomo_scan(*, acquire_time=0.02, iterations=1, delay_time_s=1.0, samOutDist=-3, md=None):
    """
    plan: user-facing plan to run tomography instrument
    
    Makes many default choices, user only needs to specify 
    acquire_time (and possibly how many times the tomography 
    scan set, `tomo_scan()`, should be run).
    
    delay_time is the time to wait between repeated runs of the 
    tomography scan set, `tomo_scan()`.
    """
    global __tomo_scan_counter
    _md = md or OrderedDict()
    _md["tomo_plan"] = "user_tomo_scan"
    det = pg3_det   # also set in tomo_scan()
    camera_size_x = det.cam.array_size.array_size_x.value

    readout_time = 0.004        # empirical estimate so we don't drop frames; was 0.003 but miss 1 frame with 0.1 s exposure time
    min_speed = 0.5             # Pete's estimate
    max_speed = 18              # top speed from other code examples
    number_of_projections = 1500
    start = 0.0
    stop = 180.0
    # PG3 camera can do at most ~128 projections/sec at 8-bit: 6.333 ms exposure time
    
    angular_range = stop - start
    scan_time = number_of_projections * (acquire_time + readout_time)

    _results = calc_blur_pixel(acquire_time, readout_time, camera_size_x, angular_range, number_of_projections)
    params = dict(
        blur_pixel = _results[0],
        rot_speed1 = _results[1], 
        scan_time = _results[2]
    )
    _results = calc_acquisition(params["blur_pixel"], acquire_time, readout_time, camera_size_x, angular_range, number_of_projections)
    params["frame_rate"] = _results[0]
    params["rot_speed2"] = _results[1]

    rotation_speed = 1          # fixed value, change here
    rotation_speed = params["rot_speed2"]

    blur_delta = acquire_time * rotation_speed
    blur_pixel = (camera_size_x / 2.0) - ((camera_size_x / 2.0) * np.cos(blur_delta * np.pi /180.))
    params["blur_delta"] = blur_delta
    params["blur_pixel"] = blur_pixel
    
    print("computed rotation speed: {} degrees / s".format(rotation_speed))
    print("computed blur angle/image: {} degrees".format(blur_delta))
    print("computed blur pixel/image: {} pixels".format(blur_pixel))
    print("iterations:", iterations)

    _md["proposed user_tomo_scan params"] = params          # proposed

    __tomo_scan_counter = 0

    def _plan_():
        """function that yields the generator we want to repeat"""
        global __tomo_scan_counter
        t0 = time.time()
        __tomo_scan_counter += 1
        yield from bps.checkpoint()
        yield from bps.mv(
            det.cam.acquire_time, acquire_time,
            # A_shutter, "open"
        )
        yield from tomo_scan(
            slewSpeed=rotation_speed, 
            acquire_time=acquire_time, 
            numProjPerSweep=number_of_projections,
            samOutDist=samOutDist,
            md=_md
        )
        msg = "{}: iteration {} of {}: total time for iteration: {} s"
        print(msg.format(
            datetime.now(), 
            __tomo_scan_counter, iterations,
            time.time()-t0
        ))
    
    t00 = time.time()
    yield from bps.repeat(_plan_, num=iterations, delay=delay_time_s)
    print("{}: total time for {} iteration(s): {} s".format(
        datetime.now(), 
        iterations, 
        time.time() - t00
    ))
