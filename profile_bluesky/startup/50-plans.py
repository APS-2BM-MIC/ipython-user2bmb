print(__file__)

# Bluesky plans (scans)
from collections import OrderedDict
import bluesky.preprocessors as bpp

NUM_FLAT_FRAMES = 10
NUM_DARK_FRAMES = 10
NUM_TEST_FRAMES = 10


def _mona_tomo(
        exposureTime=0.2, 
        slewSpeed=0.5, 
        angStart=0, angEnd = 180,
        numProjPerSweep=1500,
        samInPos=0, samOutDist=7,
        roiSizeX = 2560, roiSizeY = 2160,
        posStep = 0, 
        posNum = 1, 
        delay = 0, 
        flatPerScan = 1, darkPerScan = 1,
        accl = 1, 
        shutterMode=0, scanMode=0, 
        timeFile=0, clShutter=1,    
        ):
    """
    
    to scan this plan, use the wrapper plan below::
    
        RE(mona_tomo(...))
    """

    cam = 'edge'
    det = pco_edge
    # motor assignments depend on station and LAT/SAT
    motor_assignments = {
        # [samStage, posStage, rotStage, pso]
        'AHutch': {
            'LAT': [am49, am20, bm82, pso2],
            'SAT': [am49, am46, bm100, pso2]
        },
        'BHutch': {
            'LAT': [bm58, bm4, bm82, pso1],
            'SAT': [bm63, bm57, bm100, pso2]
        },
    }
    station = 'AHutch'
    stack = 'LAT'
    samStage, posStage, rotStage, pso = motor_assignments[station][stack]

    if station == 'AHutch':    ##### AHutch tomo configurations
        shutter = A_shutter
        # yield from mv(tomo_shutter, "open")
        camShutterMode = string_by_index("Rolling Global", shutterMode)
        if camShutterMode is None:
            msg = "Wrong camera shutter mode!"
            raise ValueError(msg)

        camScanSpeed = string_by_index("Normal Fast Fastest", scanMode)
        if camScanSpeed is None:
            msg = "Wrong camera scan mode!"
            raise ValueError(msg)

        yield from _plan_initEdge(samInPos=samInPos, samStage=samStage, rotStage=rotStage)

    elif station == 'BHutch':    ##### BHutch tomo configurations
        shutter = B_shutter
        yield from _plan_initEdge()
        camScanSpeed = "Fastest"
        camShutterMode = "Rolling"
        samInInitPos = samInPos  
    #-------------------------------------------------------------------

    filepath_top = cpr_filepath.value
           
    yield from mv(det.hdf1.create_directory, MAX_DIRECTORIES_TO_CREATE)
               
    posInit = posStage.position
    yield from mv(pso.scan_control, "Standard")
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)

    yield from bps.mv(det.hdf1.file_number, int(cpr_proj_num.value))
            
    #    yield from mv(shutter, "open")
                    
    #    filepath = cpr_filepath.value
    filename = cpr_filename.value

    filepathString = cpr_filepath.value
    filenameString = cpr_filename.value
    pathSep =  filepathString.rsplit('/')
    # TODO: logFilePath, logFileName = make_log_file( ...
    
    numImage = numProjPerSweep + NUM_FLAT_FRAMES + NUM_DARK_FRAMES
    
    # test camera -- start
    print(roiSizeX, roiSizeY)
    # TODO: restore this test?
    #yield from _plan_edgeTest(camScanSpeed, camShutterMode, roiSizeX=roiSizeX, roiSizeY=roiSizeY, pso=pso)

    # TODO: implement time file stuff

    print("start sample scan ... ")
    for ii in range(posNum):
        posStage.move(posInit+ii*posStep)

        fp = '{}{}_'.format(cpr_prefix.value, cpr_prefix_num.value.zfill(3))
        fp += '{}_'.format(cpr_sample_name.value)
        fp += '{}C_'.format(preTemp.value)
        fp += '{}_'.format(str(ii).zfill(1+1))
        fp += 'YPos{0:.3f}mm_'.format(posStage.position)
        ##### tension with 2bma:m6                   
        # fp += 'TensionDist{0:.3f}mm_'.format(am6.position)
        fp += '{}_'.format(make_timestamp())
        fp += '{}_'.format(cam)
        fp += '{}x_'.format(cpr_lens_mag.value)
        fp += '{}mm_'.format(cpr_sam_det_dist.value)
        fp += '{}msecExpTime_'.format(exposureTime*1000)
        fp += '{}DegPerSec_'.format(slewSpeed)
        fp += '{}_'.format(camShutterMode)
        fp += '{}um_'.format(cpr_scin_thickness.value)
        fp += '{}_'.format(cpr_scin_type.value)
        fp += '{}_'.format(cpr_filter.value)
        fp += '{0:.3f}mrad_'.format(A_mirror1.angle.value)
        fp += 'USArm{0:.3f}_'.format(am30.position)
        fp += 'monoY{0:.3f}_'.format(am26.position)
        fp += station
        fp += "/"
        filepath = os.path.join(filepath_top, fp)

        # remember the original stage_sigs
        stage_sigs = OrderedDict()
        stage_sigs["hdf1"] = det.hdf1.stage_sigs
        stage_sigs["cam"] = det.cam.stage_sigs
        det.image.stage_sigs["array_counter"] = 0

        yield from _plan_edgeSet(filepath, filename, numImage, exposureTime, frate, pso=pso)
        yield from _plan_setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, pso=pso, rotStage=rotStage)                              

        yield from mv(shutter, "open")
        # yield from mv(tomo_shutter, "close")
        yield from bps.sleep(3)      

        yield from bps.stage(det)
        yield from bps.sleep(1)

        yield from _plan_edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter, pso=pso, rotStage=rotStage)
        print("scan at position #",ii+1," is done!")

        samOutPos = samInPos + samOutDist
        
        if flatPerScan == 1:    # set for white field
            print("Acquiring flat images ...")
            yield from _plan_edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso)       
            print("flat for position #", ii+1, " is done!")

        # print("# "*30)
        yield from bps.sleep(1)
        if darkPerScan == 1:    # set for dark field
            print("Acquiring dark images ...")
            yield from _plan_edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso) 
            print("dark for position #", ii+1, " is done!")

        yield from bps.unstage(det)     # AFTER images, flats, and darks are collected
        # reset the original stage_sigs
        det.hdf1.stage_sigs = stage_sigs["hdf1"]
        det.cam.stage_sigs = stage_sigs["cam"]

        yield from bps.mv(cpr_proj_num, str(det.hdf1.file_number.value))

        yield from _plan_auto_increment_prefix_number()
        
        # TODO: implement time file stuff

        if ii != (posNum-1):
            yield from bps.sleep(delay)

    yield from mv(shutter, "close")
    # yield from mv(tomo_shutter, "close")
    print("sample scan is done!")


def mona_tomo(md={}, **kwargs):
    """use this plan to run a mona_tomo scan"""

    params = dict(
        exposureTime=0.2, 
        slewSpeed=0.5, 
        angStart=0, angEnd = 180,
        numProjPerSweep=1500,
        samInPos=0, samOutDist=7,
        roiSizeX = 2560, roiSizeY = 2160,
        posStep = 0, 
        posNum = 1, 
        delay = 0, 
        flatPerScan = 1, darkPerScan = 1,
        accl = 1, 
        shutterMode=0, scanMode=0, 
        timeFile=0, clShutter=1,    
    )
    # cautious update of params dictionary
    for k, v in kwargs.items():
        if k in params:
            params[k] = v

    # metadata includes all params and other metadata
    _md = dict(**params)
    _md.update(**md)
    _md["project"] = "mona"
    _md["APS_storage_ring_current,mA"] = aps_current.value
    _md["datetime_plan_started"] = str(datetime.now())

    staged_device_list = [pco_edge]
    monitored_signals_list = [
        pco_edge.image.array_counter, 
        bm82.user_readback,
        ]
    
    def _internal_tomo():
        print("_internal_tomo()", params)
        yield from bps.monitor(bm82.user_readback, name="rotation")
        yield from bps.monitor(pco_edge.image.array_counter, name="primary")
        yield from _mona_tomo(**params)
        yield from bps.unmonitor(pco_edge.image.array_counter)
        yield from bps.unmonitor(bm82.user_readback)

    return bpp.run_decorator(md = _md)(_internal_tomo)()


def _plan_edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    yield from abs_set(shutter, "open", wait=True)
    yield from bps.abs_set(det.cam.frame_type_VAL, 0, wait=True) # 0: Normal
    yield from mv(samStage, samInPos, rotStage.velocity, 50.0)
    # or  rotStage.stage_sigs["velocity"] = 50.0
    yield from bps.sleep(1)     # wait for velocity command to reach controller
    yield from mv(rotStage, 0.00)
    
    # back off to the ramp-up point
    # print("before taxi")
    yield from abs_set(pso, "taxi", wait=True)
    # print("after taxi")
    
    slewSpeed = float(cpr_slew_speed.value)
    yield from mv(rotStage.velocity, slewSpeed)
    # or  rotStage.stage_sigs["velocity"] = slewSpeed
    yield from bps.sleep(1)     # wait for velocity command to reach controller
    # print("rotStage velocity = {}".format(rotStage.velocity.value))

    yield from mv(det.cam.acquire, 1)

    # run the fly scan
    # print("before fly")
    yield from abs_set(pso, "fly", wait=True)
    # print("after fly")

    if pso.pso_fly.value == 0 & clShutter == 1:               
        yield from abs_set(shutter, "close", wait=True)

    if not (0 < rotStage.position < 360.0):
        yield from abs_set(rotStage.set_use_switch, "Set", wait=True)
        # ensure `.RVAL` changes (not `.OFF`)
        foff_previous = rotStage.offset_freeze_switch.value
        yield from abs_set(rotStage.offset_freeze_switch, "Frozen", wait=True)
        yield from abs_set(rotStage.user_setpoint, 1.0*(rotStage.position%360.0), wait=True)
        yield from abs_set(rotStage.offset_freeze_switch, foff_previous, wait=True)
        yield from abs_set(rotStage.set_use_switch, "Use", wait=True)

    # print("after fly, returning rotStage to standard")
    yield from mv(rotStage.velocity, 50.0)
    # rotStage.stage_sigs["velocity"] = 50.0
    yield from bps.sleep(1)     # wait for velocity command to reach controller
    yield from mv(rotStage, 0.00)
    # shutter.close()
    # print("Waiting for HDF5 file to finish writing")
    # TODO: Is this necessary?  It does not ever come out of the while()
    # while (det.hdf1.num_captured.value != numProjPerSweep):    
    #     yield from bps.sleep(1)
    # print("HDF5 file write is complete")


def _plan_setPSO(slewSpeed, scanDelta, acclTime, angStart=0, angEnd=180, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82

    # TODO: stage these?
    yield from mv(pso.start_pos, angStart)
    yield from mv(pso.end_pos, angEnd)
    yield from mv(rotStage.velocity, slewSpeed)
    #  rotStage.stage_sigs["velocity"] = slewSpeed
    #  rotStage.stage_sigs["acceleration"] = acclTime
    yield from mv(pso.slew_speed, slewSpeed)
    yield from mv(rotStage.acceleration, acclTime)
    yield from mv(pso.scan_delta, scanDelta)


def _plan_edgeTest(camScanSpeed,camShutterMode,roiSizeX=2560,roiSizeY=2160,pso=None):
    pso = pso or pso1
    det = pco_edge

    # yield from mv(pso.scan_control, "Standard")
    yield from mv(det.cam.array_callbacks, "Enable")
    yield from mv(det.cam.num_images, NUM_TEST_FRAMES)
    yield from mv(det.cam.image_mode, "Multiple")
    yield from mv(det.cam.pco_global_shutter, camShutterMode)
    yield from mv(det.cam.pco_edge_fastscan, camScanSpeed)
    yield from mv(det.cam.acquire_time, 0.001000)
    yield from mv(det.cam.size.size_x, roiSizeX)
    yield from mv(det.cam.size.size_y, roiSizeY)
    yield from mv(det.cam.pco_trigger_mode, "Auto")
    # print("_plan_edgeTest('Acquire')")
    yield from bps.mv(det.cam.acquire, "Acquire")
    print("camera passes test!")


def _plan_edgeSet(filepath, filename, numImage, exposureTime, frate, pso=None):
    """
    prepare detector for tomo acquisition
    """
    pso = pso or pso1    
    det = pco_edge

    # do this early, BEFORE stage() - make_filename() needs this
    yield from bps.mv(det.hdf1.file_path, filepath)
    
    det.hdf1.stage_sigs["num_capture"] = numImage
    #det.hdf1.stage_sigs["file_path"] = filepath
    det.hdf1.stage_sigs["file_name"] = filename
    det.hdf1.stage_sigs["capture_VAL"] = "Capture"
    # FIXME: xml_layout_file is a troublemaker  (low-level ophyd fix needed)
    #det.hdf1.stage_sigs["xml_layout_file"] = "DynaMCTHDFLayout.xml"
    det.cam.stage_sigs["pco_is_frame_rate_mode"] = "DelayExp"
    det.cam.stage_sigs["acquire_period"] = frate+1
    det.cam.stage_sigs["pco_set_frame_rate"] = frate
    det.cam.stage_sigs["num_images"] = numImage-NUM_FLAT_FRAMES-NUM_DARK_FRAMES
    det.cam.stage_sigs["image_mode"] = "Multiple"
    det.cam.stage_sigs["acquire_time"] = exposureTime
    det.cam.stage_sigs["pco_trigger_mode"] = "Soft/Ext"
    det.cam.stage_sigs["pco_ready2acquire"] = 0
    
    # Why?  FIXME: This is RO!  yield from mv(det.hdf1.num_captured, 0)


def _plan_initEdge(samInPos=0, samStage=None, rotStage=None):
    """
    setup the PCO Edge detector
    """
    samStage = samStage or am49
    rotStage = rotStage or bm82
    det = pco_edge

    # yield from mv(tomo_shutter, "open")
    yield from mv(A_shutter, "open")

    yield from mv(det.cam.nd_attributes_file, "DynaMCTDetectorAttributes.xml")

    yield from mv(det.cam.acquire, "Done")

    # yield from mv(det.cam.acquire, "Done")  
    yield from mv(det.cam.pco_trigger_mode, "Auto")
    yield from mv(det.cam.image_mode, "Continuous")
    yield from mv(det.cam.pco_edge_fastscan, "Normal")
    yield from mv(det.cam.pco_is_frame_rate_mode, 0)
    yield from mv(det.cam.acquire_time, 0.2)
    yield from mv(det.cam.size.size_x, 2560)
    yield from mv(det.cam.size.size_y, 2160)    # or 1400
    if hasattr(det, "hdf1"):
        yield from mv(det.hdf1.enable, "Enable")
        yield from mv(det.hdf1.capture_VAL, "Done")
        #yield from mv(det.hdf1.xml_layout_file, "DynaMCTHDFLayout.xml")
        #yield from epics.caput(pco_edge.hdf1.xml_layout_file.pvname, "DynaMCTHDFLayout.xml"))
        # Why? FIXME:  This is RO!  yield from mv(det.hdf1.num_captured, 0)
    yield from mv(det.image.enable, "Enable")
    yield from _plan_process_tableFly2_sseq_record()
    yield from bps.stop(rotStage)

    yield from mv(rotStage.set_use_switch, 1)
    yield from mv(rotStage.user_setpoint, rotStage.position % 360.0)
    yield from mv(rotStage.set_use_switch, 0)

    yield from mv(rotStage.velocity, 30)
    yield from mv(rotStage.acceleration, 3)
    # or  rotStage.stage_sigs["velocity"] = 30
    # or  rotStage.stage_sigs["acceleration"] = 3
    yield from mv(rotStage, 0)
    yield from mv(samStage, samInPos)
    # yield from mv(tomo_shutter, "close")
    print("Edge is reset!")


def _plan_process_tableFly2_sseq_record():
    yield from mv(tableFly2_sseq_PROC, 1)


def _plan_auto_increment_prefix_number():
    """increment the prefix number if permitted"""
    if cpr_auto_increase.value == 'Yes':
        num = int(cpr_prefix_num.value)
        num += 1
        yield from bps.mv(cpr_prefix_num, str(num))


def _plan_edgeAcquireDark(samInPos,filepath,samStage,rotStage, shutter, pso=None):
    pso = pso or pso1
    det = pco_edge

    yield from bps.mv(pso.scan_control, "Standard")
    yield from bps.mv(shutter, "close")
    yield from bps.sleep(5)
    
    yield from bps.abs_set(det.cam.pco_trigger_mode, "Auto", group="dark")
    yield from bps.abs_set(det.cam.frame_type, 1, group="dark")     # 1 = Background
    yield from bps.abs_set(det.cam.num_images, NUM_DARK_FRAMES, group="dark")
    yield from bps.wait(group="dark")
    yield from bps.sleep(5)

    yield from bps.trigger(det)
    yield from bps.sleep(5)

    yield from bps.mv(samStage, samInPos)


def _plan_edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage, shutter, pso=None):
    pso = pso or pso1
    det = pco_edge

    yield from bps.abs_set(samStage, samOutPos)
    yield from bps.mv(pso.scan_control, "Standard")
    yield from bps.mv(shutter, "open")
    yield from bps.sleep(5)
    
    yield from bps.abs_set(det.cam.pco_trigger_mode, "Auto", group="flat")
    yield from bps.abs_set(det.cam.frame_type, 2, group="flat")     # 2 = FlatField
    yield from bps.abs_set(det.cam.num_images, NUM_FLAT_FRAMES, group="flat")
    yield from bps.wait(group="flat")
    yield from bps.sleep(5)

    yield from bps.trigger(det)

    yield from bps.mv(shutter, "close")
    yield from bps.sleep(5)

    yield from bps.mv(samStage, samInPos)
