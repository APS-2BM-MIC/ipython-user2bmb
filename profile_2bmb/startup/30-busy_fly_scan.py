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

    rotStage.stage_sigs["velocity"] = ROT_STAGE_FAST_SPEED
    rotStage.stage_sigs["acceleration"] = 3
    yield from bps.mv(rotStage, 0)
    yield from bps.mv(samStage, samInPos)

    # TODO: anything from _plan_edgeSet() needed? (Feb 2018 setup: 50-plans.py)

    pso.stage_sigs["start_pos"] = start
    pso.stage_sigs["end_pos"] = stop
    pso.stage_sigs["scan_delta"] = 1.0*(stop-start)/numProjPerSweep
    pso.stage_sigs["slew_speed"] = slewSpeed
    rotStage.stage_sigs["velocity"] = slewSpeed
    rotStage.stage_sigs["acceleration"] = 1.0*slewSpeed/accl   

    yield from bps.stage(det) # TODO: why?
    yield from bps.sleep(1)
        
    yield from bps.create() # TODO: why?


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

    @bpp.run_decorator(md = _md)
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

        # run the fly scan
        rotStage.stage_sigs["velocity"] = slewSpeed
        yield from bps.mv(det.cam.acquire, 1)   # TODO: why not trigger?
        yield from bps.mv(pso.fly, "Fly")

        yield from bps.abs_set(shutter, "close")

        # return rotStage to standard
        rotStage.stage_sigs["velocity"] = ROT_STAGE_FAST_SPEED
        yield from bps.mv(rotStage, 0.00)

        yield from bps.unmonitor(det.image.array_counter)
        yield from bps.unmonitor(rotStage.user_readback)

    return (yield from _internal_tomo())
