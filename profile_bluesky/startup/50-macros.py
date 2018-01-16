print(__file__)


def make_timestamp():
    """such as: 2018-01-12 15:40:46 is FriJan12_15_40_46_2018"""
    timestamp = [x for x in time.asctime().rsplit(' ') if x!='']
    timestamp = ''.join(timestamp[0:3]) \
                + '_' + timestamp[3].replace(':','_') \
                + '_' + timestamp[4]
    return timestamp


def make_log_file(filepathString, filenameString, file_number):
    """
    make the log file (build the path (str) to keep the log file)
    
    take last three subdirs of filepathString and append to USER2BMB_ROOT_DIR
    
    returns tuple of (logFilePath, logFileName)
    
    example:
    given filepathString = "/some/long/path/with/many/sub/dirs"
    and USER2BMB_ROOT_DIR = "/local/user2bmb"
    then path is "/local/user2bmb/many/sub/dirs"
    """
    # the original has confusing syntax
    # pathSep =  filepathString.rsplit('/')
    # logFilePath = os.path.join(USER2BMB_ROOT_DIR, pathSep[-3],pathSep[-2],pathSep[-1])
    
    pathlist = [USER2BMB_ROOT_DIR]
    pathlist +=  filepathString.rsplit('/')[-3:]    # last three subdirs
    logFilePath = os.path.join(pathlist)

    # create the directory if it does not exist
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    mapping = {
        "name": filenameString,
        "index": file_number
        }
    format = "%(name)s_%(index)03d.log"
    logFileName = os.path.join(logFilePath, format % mapping)

    # create the log file
    logFile = open(logFileName,'w')
    logFile.close()                
    
    return logFilePath, logFileName


def _initFilepath():
    caputRecorder_filepath.put("proj")
    path = "s:/data/2017_12/Commissioning"
    caputRecorder_filename.put(path)


def setDefaultFolderStructure():
    def caput_desc(signal, description):
        """.DESC field is not part of EpicsSignal"""
        epics.caput(signal.pvname+".DESC", description, wait=True, timeout=1000.0)

    caput_desc(caputRecorder1, 'prefix')
    caput_desc(caputRecorder2, 'prefix #')
    caput_desc(caputRecorder3, 'auto-increase #')
    caput_desc(caputRecorder4, 'sample name')
    caput_desc(caputRecorder5, 'lens mag')
    caput_desc(caputRecorder6, 'sam-det dist(mm)')
    caput_desc(caputRecorder7, 'scinThickness(um)')
    caput_desc(caputRecorder8, 'scinType')
    caput_desc(caputRecorder9, 'filter')
    caput_desc(caputRecorder10, 'proj #')

    caputRecorder_filename.put('proj')
    caputRecorder1.put('Exp')
    caputRecorder2.put('1')
    caputRecorder3.put('Yes')
    caputRecorder4.put('S1')
    caputRecorder5.put('10')
    caputRecorder6.put('50')
    caputRecorder7.put('10')
    caputRecorder8.put('LuAG')
    caputRecorder9.put('1mmC1mmGlass')
    caputRecorder10.put('1')
                                

def process_tableFly2_sseq_record():
    tableFly2_sseq_PROC.put(1)


def initDimax(samInPos=0, hutch='A'):
    """
    I want a comment here
    """
    if hutch.lower() == ('a'):
        shutter = A_shutter
        samStage = am49
        rotStage = bm82
    else:
        shutter = B_shutter
        samStage = bm63
        rotStage = bm100

    det = pco_dimax
    det.cam.array_callbacks.put("Enable")

    # det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")

    tomo_shutter.open()
    shutter.open()
    det.cam.pco_cancel_dump.put(1)
    det.cam.acquire.put("Done")
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.pco_live_view.put("Yes")
    if hasattr(det, "hdf1"):
        det.hdf1.enable.put("Enable")
        # det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")
        det.hdf1.capture.put("Done")
        det.hdf1.num_captured.put(0)
    rotStage.servo.put("Enable")
    process_tableFly2_sseq_record()
    rotStage.velocity.put(180)
    rotStage.acceleration.put(3)
    rotStage.move(0)
    samStage.move(samInPos)
    print("Dimax is reset!")


def initEdge(samInPos=0, samStage=None, rotStage=None):
    """
    I want a comment here
    """
    samStage = samStage or am49
    rotStage = rotStage or bm82

    tomo_shutter.open()
    A_shutter.open()

    det = pco_edge

    det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")

    det.cam.acquire.put("Done")print(__file__)

    # det.cam.acquire.put("Done")  
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.image_mode.put("Continuous")
    det.cam.pco_edge_fastscan.put("Normal")
    det.cam.pco_is_frame_rate_mode.put(0)
    det.cam.acquire_time.put(0.2)
    det.cam.size.size_x.put(2560)
    det.cam.size.size_y.put(1400)
    if hasattr(det, "hdf1"):
        det.hdf1.enable.put("Enable")
        det.hdf1.capture.put("Done")
        det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")
        det.hdf1.num_captured.put(0)
    det.image.enable.put("Enable")
    process_tableFly2_sseq_record()
    rotStage.stop()
    rotStage.set_use_switch.put("Set")
    rotStage.user_setpoint.put(rotStage.position % 360.0)
    rotStage.set_use_switch.put("Use")
    rotStage.velocity.put(30)
    rotStage.acceleration.put(3)
    rotStage.move(0)
    samStage.move(samInPos)
    tomo_shutter.close()
    print("Edge is reset!")


def change2White():
    A_shutter.close()
    # am33.move(107.8, wait=False)
    A_filter.put(0)
    A_mirror1.angle.put(0)
    time.sleep(1)                

    A_mirror1.average.put(-4)
    time.sleep(1)                

    am25.move(50, wait=False)
    am28.move(50, wait=True)
    time.sleep(3)                

    am26.move(-16, wait=False)
    am27.move(-16, wait=False)
    am29.move(-16, wait=True)
    time.sleep(3)                

    A_slit1_h_center.put(4.8)
    am7.move(11.8, wait=True)


def change2Mono():
    A_shutter.close()
    # am33.move(121)
    A_filter.put(0)
    A_mirror1.average.put(0)
    time.sleep(1) 
    
    A_mirror1.angle.put(2.657)
    time.sleep(1)

    am26.move(-0.1, wait=False)
    am27.move(-0.1, wait=False)
    am29.move(-0.1)
    time.sleep(3)

    am25.move(81.5, wait=False)
    am28.move(81.5)
    time.sleep(3)

    A_slit1_h_center.put(5)
    am7.move(46.55)


def changeDMMEng(energy=24.9):
    BL = '2bma'
    A_shutter.close()
    change2Mono()
    if energy < 20.0:
        A_filter.put(4)
    else:
        A_filter.put(0)

    #    if A_mirror1.angle.get() is not 2.657:
    #        print('mirror angle is wrong. quit!')
    #        return 0                 # TODO: could raise ValueError instead!

    caliEnergy_list = np.array([40.0,35.0,31.0,27.4,24.9,22.7,21.1,20.2,18.9,17.6,16.8,16.0,15.0,14.4])
    XIASlit_list = np.array([37.35,41.35,42.35,42.35,43.35,46.35,44.35,46.35,47.35,50.35,52.35,53.35,54.35,51.35])    
    #    XIASlit_list = np.array([38.35,43.35,42.35,44.35,46.35,46.35,47.35,48.35,50.35,50.35,52.35,53.35,54.35,55.35]) 
    #    FlagSlit_list = np.array([19.9,,19.47])    
    #    GlobalY_list = np.array([-87.9,1.15,-79.8,1.25,-84.2,1.35,1.4,1.45,1.5,-79.8,1.6,1.65])                    
    USArm_list = np.array([1.10,1.25,1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.55,1.60,1.65])    
    DSArm_list = np.array([1.123,1.2725,1.121,1.169,1.2235,1.271,1.3225,1.366,1.4165,1.4655,1.5165,1.568,1.6195,1.67])
    M2Y_list = np.array([13.82,15.87,12.07,13.11,14.37,15.07,15.67,16.87,17.67,18.47,19.47,20.57,21.27,22.27]) 

    DMM_USX_list = [27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5]
    DMM_DSX_list = [27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5]
    DMM_USY_OB_list = [-5.7,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1] 
    DMM_USY_IB_list = [-5.7,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1]   
    DMM_DSY_list = [-5.7,-3.8,-0.1,-0.1,-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1] 
    
    Mirr_Ang_list = [1.500,2.000,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657]
    Mirr_YAvg_list = [0.1,-0.2,0.0,0.0,-0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

    energy_index = np.where(caliEnergy_list==energy)[0]
    if energy_index.size == 0:
        print('there is no specified energy in the energy lookup table. please choose a calibrated energy.')
        return    0                            # TODO: could raise KeyError instead!

    A_mirror1.angle.put(Mirr_Ang_list[energy_index])
    A_mirror1.average.put(Mirr_YAvg_list[energy_index])
    
    am26.move(DMM_USY_OB_list[energy_index], wait=False)
    am27.move(DMM_USY_IB_list[energy_index], wait=False)
    am29.move(DMM_DSY_list[energy_index], wait=False)
    am30.move(USArm_list[energy_index], wait=False)
    am31.move(DSArm_list[energy_index])
    time.sleep(3)

    am32.move(M2Y_list[energy_index], wait=False)
    am25.move(DMM_USX_list[energy_index], wait=False)
    am28.move(DMM_DSX_list[energy_index])
    am7.move(XIASlit_list[energy_index] )
    print('DMM energy is set to ', energy, 'keV.')


def centerAxis(axisShift=12.5, refYofX0=14.976):
    """
    function documentation
                
    axisShift: rotation axis shift in unit um/mm. 
        It is defined as the shift distance when the vertical stage moves up.
        It assumes rotation axis is at image center at posInit.
        This is the case in which the rotation axis move toward right 
        side (larger 'center' in reconstruction)
        when the sample stage moves up.                                                        
    """
    posRefPos = refYofX0 
                                
    ##### AHutch tomo configurations -- start                           
    #### for LAT                
    samStage = am49
    posStage = am20      
                
    ### for SAT                
    #    samStage = am49
    #    posStage = am46
               
    ##### AHutch tomo configurations -- end                    

    ####### BHutch tomo configurations -- start              
    #### for SAT                
    #    samStage = bm63
    #    posStage = bm57
    #                
    #### for LAT
    ##    samStage = bm58
    ##    posStage = bm4
    ####### BHutch tomo configurations -- end                   

    samStageOffset = axisShift * (posStage.position - posRefPos)/1000.0  
    print(samStageOffset)
    samStage.move(samStageOffset)
    print('done')

 
def DimaxRadiography(
        exposureTime=0.1, 
        frmRate=9, 
        acqPeriod=30,
        samInPos=0, 
        samOutPos=7,
        roiSizeX=2016, 
        roiSizeY=2016,
        repeat=1, 
        delay=600,
        scanMode=0):

    samStage = am49; station = 'AHutch'
    #samStage = bm63; station = 'BHutch'
    cam = "dimax"; det = pco_dimax
    # cam = "edge"; det = pco_edge
    posStage = am20 
    rotStage = bm82

    A_shutter.open()
    numImage = frmRate * acqPeriod + 20
    camShutterMode = "Rolling"
    filepath_top = caputRecorder_filepath.value

#    filepath = os.path.join(filepath_top, caputRecorder1.value+ \
#                caputRecorder2.value.zfill(3)+'_'+ 'Radiography_' +\
#                caputRecorder4.value+'_'+\
#                      'YPos'+str(am20.position)+'mm_'+\
#                cam+'_'+caputRecorder5.value+'x'+'_'+\
#                caputRecorder6.value+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
#                camShutterMode+'_'+caputRecorder7.value+'um'+\
#                caputRecorder8.value+'_'+\
#                caputRecorder9.value+'_'+\
#                str(A_mirror1.angle.value)+'mrad_USArm'+str(am30.position)+\
#                '_monoY_'+str(am26.position)+'_'+station)

    # det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")
    # if hasattr(det, "hdf1"):
    #     det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")

    for ii in range(repeat):
        tomo_shutter.close()
        
        filepath = os.path.join(filepath_top, \
                   caputRecorder1.value+ \
                   caputRecorder2.value.zfill(3)+'_'+ 'Radiography_'+\
                   caputRecorder4.value+'_'+\
                   'YPos'+str(int(posStage.position*1000)/1000.0)+'mm_'+\
                   make_timestamp() + '_'+\
                   cam+'_'+caputRecorder5.value+'x'+'_'+\
                   caputRecorder6.value+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+\
                   camShutterMode+'_'+caputRecorder7.value+'um'+\
                   caputRecorder8.value+'_'+\
                   caputRecorder9.value+'_'+\
                   str(int(A_mirror1.angle.value*1000)/1000.0)+'mrad_USArm'+\
                   str(int(am30.position*1000)/1000.0)+\
                   '_monoY_'+str(int(am26.position*1000)/1000.0)+'_'+\
                   station)     
        filename = caputRecorder_filename.value   
    
        det.cam.acquire.put("Done")

        det.cam.pco_trigger_mode.put("Auto")
        det.cam.pco_is_frame_rate_mode.put("DelayExp")
        det.cam.pco_live_view.put("No")
        det.cam.size.size_x.put(roiSizeX)
        det.cam.size.size_y.put(roiSizeY)
        det.cam.acquire_period.put(0)

        if hasattr(det, "hdf1"):
            det.hdf1.capture.put("Done")
            det.hdf1.create_directory.put(-5)   # TODO: Why -5?
            det.hdf1.file_number.put(caputRecorder10.value)
            det.hdf1.enable.put(1)
            det.hdf1.auto_increment.put("Yes")
            det.hdf1.num_capture.put(numImage)
            det.hdf1.num_captured.put(numImage)
            det.hdf1.file_path.put(filepath)
            det.hdf1.file_name.put(filename)
            det.hdf1.file_template.put("%s%s_%4.4d.hdf")
            det.hdf1.auto_save.put("Yes")
            det.hdf1.file_write_mode.put("Stream")
            det.hdf1.capture.put("Capture", wait=False)
            time.sleep(2)  

        samStage.move(samInPos)
        det.cam.num_images.put(numImage-20)
        det.cam.frame_type.put("Normal")
        det.cam.acquire.put("Acquire")
        det.cam.pco_dump_counter.put('0')
        det.cam.pco_imgs2dump.put(numImage-20)
        det.cam.pco_dump_camera_memory.put(1)
        print('data is done')

        det.cam.num_images.put(10)
        samStage.move(samOutPos)
        det.cam.frame_type.put("FlatField")
        det.cam.acquire.put("Acquire")
        det.cam.pco_dump_counter.put('0')
        det.cam.pco_imgs2dump.put(10)
        tomo_shutter.open()
        det.cam.pco_dump_camera_memory.put(1)
        det.cam.acquire.put("Done")
        print('flat is done')

        # tomo_shutter.open()
        samStage.move(samInPos)
        det.cam.frame_type.put("Background")
        det.cam.acquire.put("Acquire")
        det.cam.pco_dump_counter.put('0')
        det.cam.pco_imgs2dump.put(10)
        det.cam.pco_dump_camera_memory.put(1)
        det.cam.acquire.put("Done")
        print('dark is done')

        if hasattr(det, "hdf1"):
            det.hdf1.capture.put("Done", wait=False)
        det.cam.image_mode.put("Continuous")

        caputRecorder10.put(det.hdf1.file_number.value)
        if caputRecorder3.value == 'Yes':
            caputRecorder2.put(int(caputRecorder2.value)+1)

        print(str(ii), 'the acquisition is done at ', time.asctime())
        if ii != repeat-1:
            time.sleep(delay)

    det.cam.pco_live_view.put("Yes")
    tomo_shutter.close()
    A_shutter.close()
    print('Radiography acquisition finished!')


def EdgeRadiography(
        exposureTime=0.1, 
        frmRate = 9, 
        acqPeriod = 30,
        samInPos=0, 
        samOutPos=5,
        roiSizeX = 2560, 
        roiSizeY = 1300,
        repeat=1, 
        delay=300,
        scanMode=0):

    station = 'AHutch'
    # station = 'BHutch'   
    samStage = am49
    posStage = am20
    rotStage = bm82
    pso = pso2
    BL = "2bmb"
    shutter = "2bma:A_shutter"                

    shutter = A_shutter
    shutter.open()
    tomo_shutter.close()

    numImage = frmRate * acqPeriod
                
    if scanMode in (0, 1, 2):
        camScanSpeed = "Normal Fast Fastest".split()[scanMode]
    else:
        print("Wrong camera scan mode! Quit...")
        return False

    # cam = "dimax"; det = pco_dimax
    cam = "edge"; det = pco_edge
    camShutterMode = "Rolling"                

    filepath_top = caputRecorder_filepath.value

    #    filepath = os.path.join(filepath_top, caputRecorder1.value+ \
    #                caputRecorder2.value.zfill(3)+'_'+ 'Radiography_' +\
    #                caputRecorder4.value+'_'+\
    #                      'YPos'+str(am20.position)+'mm_'+\
    #                cam+'_'+caputRecorder5.value+'x'+'_'+\
    #                caputRecorder16.value+'mm'+'_'+\
    #                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
    #                camShutterMode+'_'+caputRecorder7.value+'um'+\
    #                caputRecorder8.value+'_'+\
    #                caputRecorder9.value+'_'+\
    #                str(A_mirror1.angle.value)+'mrad_USArm'+\
    #                str(am30.position)+'_monoY_'+\
    #                str(am26.position)+'_'+station)

    for ii in range(repeat):
        filepath = os.path.join(filepath_top, \
                   caputRecorder1.value+ \
                   caputRecorder2.value.zfill(3)+'_'+ 'Radiography_'+\
                   caputRecorder4.value+'_'+\
                   'YPos'+str(int(posStage.position*1000)/1000.0)+'mm_'+\
                   make_timestamp() + '_'+\
                   cam+'_'+caputRecorder5.value+'x'+'_'+\
                   caputRecorder6.value+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+\
                   camShutterMode+'_'+caputRecorder7.value+'um'+\
                   caputRecorder8.value+'_'+\
                   caputRecorder9.value+'_'+\
                   str(int(A_mirror1.angle.value*1000)/1000.0)+'mrad_USArm'+\
                   str(int(am30.position*1000)/1000.0)+'_monoY_'+\
                   str(int(am26.position*1000)/1000.0)+'_'+station)

        filename = caputRecorder_filename.value
    
        det.cam.acquire.put("Done")

        if hasattr(det, "hdf1"):
            det.hdf1.capture.put("Done",)
            det.hdf1.CreateDirectory.put(-5)
            det.hdf1.FileNumber.put(caputRecorder10.value)

        det.cam.pco_trigger_mode.put("Auto")
        det.cam.ImageMode.put("Multiple")
        det.cam.NumImages.put(numImage)
        det.cam.pco_edge_fastscan.put(camScanSpeed)
        det.cam.pco_trigger_mode.put("Auto")
        det.cam.SizeX.put(str(roiSizeX))
        det.cam.SizeY.put(str(roiSizeY))
        det.cam.pco_global_shutter.put(camShutterMode)
        det.cam.pco_is_frame_rate_mode.put("DelayExp")
        det.cam.acquire_period.put(0)
        det.cam.frame_type.put("Normal")

        if hasattr(det, "hdf1"):
            # FIXME: check these!!!
            det.hdf1.enable_callbacks.put(1)
            det.hdf1.auto_increment.put("Yes")
            det.hdf1.num_capture.put(str(numImage+20))
            det.hdf1.num_capture.put(str(numImage+20))
            det.hdf1.num_captured.put(0)
            det.hdf1.file_path.put(filepath)
            det.hdf1.file_name.put(filename)
            det.hdf1.file_template.put("%s%s_%4.4d.hdf")
            det.hdf1.auto_save.put("Yes")
            det.hdf1.file_write_mode.put("Stream")
                      
            det.hdf1.capture.put("Capture", wait=False)
        time.sleep(2)  
                                    
        det.cam.acquire.put("Acquire")
        print('data is done')
    
        det.cam.num_images.put(10)
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO=pso)    
        print('flat is done')
             
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO=pso)    
        print('dark is done')
    
        shutter.close()
        tomo_shutter.close()
        det.cam.image_mode.put("Continuous")

        if hasattr(det, "hdf1"):
            caputRecorder10.put(det.hdf1.file_number.value)
        if caputRecorder3.value == 'Yes':
            caputRecorder2.put(str(1+int(caputRecorder2.value)))

        print(str(ii), 'the acquisition is done at ', time.asctime())
        if ii != repeat-1:
            time.sleep(delay)
                 
                
    print('Radiography acquisition finished!')


def _edgeTest(camScanSpeed,camShutterMode,roiSizeX=2560,roiSizeY=2160,PSO=None):
    PSO = PSO or pso1
    det = pco_edge

    # det.cam.scan_control.put("Standard")
    det.cam.array_callbacks.put("Enable")
    det.cam.num_images.put(10)
    det.cam.image_mode.put("Multiple")
    det.cam.pco_global_shutter.put(camShutterMode)
    det.cam.pco_edge_fastscan.put(camScanSpeed)
    det.cam.acquire_time.put(0.001000)
    det.cam.size_x.put(roiSizeX)
    det.cam.size_y.put(roiSizeY)
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")
    print("camera passes test!")


def _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO=None):
    PSO = PSO or pso1    
    det = pco_edge

    det.cam.pco_is_frame_rate_mode.put("DelayExp")
    det.cam.acquire_period.put(0)
    det.cam.pco_set_frame_rate.put(frate+1)     # TODO: why twice?
    det.cam.pco_set_frame_rate.put(frate)
    det.hdf1.auto_increment.put("Yes")
    det.hdf1.num_capture.put(numImage)
    det.hdf1.num_capture.put(numImage)
    det.hdf1.num_captured.put(0)
    det.hdf1.file_path.put(filepath)
    det.hdf1.file_name.put(filename)
    det.hdf1.file_template.put("%s%s_%4.4d.hdf")
    det.hdf1.auto_save.put("Yes")
    det.hdf1.file_write_mode.put("Stream")
    det.hdf1.capture.put("Capture", wait=False)
    det.cam.num_images.put(numImage)
    det.cam.pco_image_mode.put("Multiple")
    det.cam.acquire_time.put(exposureTime)
    det.cam.pco_trigger_mode.put("Soft/Ext")
    det.cam.pco_ready2acquire.put(0)
    det.cam.acquire.put("Acquire", wait=False)


def _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1, PSO=None,rotStage=None):
    PSO = PSO or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    shutter.open()
    det.cam.frame_type("Normal")
    samStage.move(samInPos)
    rotStage.velocity.put(50.00000)
    rotStage.move(0.00000)
    PSO.taxi()
    PSO.fly()
    if PSO.pso_fly.value == 0 & clShutter == 1:               
        shutter.close()     
    rotStage.set_current_position(1.0*rotStage.position%360.0)
    rotStage.velocity.put(50.00000)
    time.sleep(1)
    rotStage.move(0.00000)
    # shutter.close()
    while (det.hdf1.num_captured.value != numProjPerSweep):    
        time.sleep(1)                    


def _edgeInterlaceAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1,InterlacePSO=None,rotStage=None):
    InterlacePSO = InterlacePSO or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    det.cam.frame_type.put("Normal")
    samStage.move(samInPos)
    InterlacePSO.put("Fly")
    # shutter.close()
    # shutter.open()
    if clShutter == 1:
        shutter.close()
    rotStage.set_current_position(1.0*rotStage.position%360.0)
    rotStage.velocity.put(50.00000)
    rotStage.move(0, wait=False)
    numProjPerSweep = det.cam1.num_images_counter.value
    print("Saving sample data ...")
    while (det.cam1.num_captured.value != numProjPerSweep):    
        time.sleep(1)
    # det.cam1.acquire.put("Done")
    # det.hdf1.acquire.put("Done")


def _edgeAcquireDark(samInPos,filepath,samStage,rotStage, shutter, PSO=None):
    PSO = PSO or pso1
    det = pco_edge

    PSO.scan_control.put("Standard")
    shutter.close()
    time.sleep(5)
            
    det.cam.frame_type.put("Background")
    det.cam.num_images.put(10)

    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")
        
    # PSO.start_pos.put(0.00000)
    # PSO.end_pos.put(6.0000)
    # PSO.scan_delta.put(0.3)
    # PSO.slew_speed.put(1)
    # rotStage.velocity.put(3)
    # rotStage.acceleration.put(1)
    # PSO.taxi()
    # PSO.fly()
    # rotStage.velocity.put(50)
    # rotStage.move(0)
             
    #    while det.cam.num_capture.value != det.cam.num_captured.value:
    #        time.sleep(1)                
    det.cam.acquire.put("Done")
    samStage.move(samInPos)


def _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage, shutter, PSO=None):
    PSO = PSO or pso1
    det = pco_edge

    samStage.move(str(samOutPos), wait=False)
    PSO.scan_control.put("Standard")
    shutter.open()
    time.sleep(5)
    det.cam.frame_type.put("FlatField")
    det.cam.num_images.put(10)
    
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")

    # PSO.start_pos.put(0.00000)
    # PSO.end_pos.put(6.0000)
    # PSO.scan_delta.put(0.3)
    # PSO.slew_speed.put(1)
    # rotStage.velocity.put(3)
    # rotStage.acceleration.put(1)
    # PSO.taxi()
    # PSO.fly()
    # rotStage.velocity.put(50)
    # rotStage.move(0)
    
    shutter.close()
    time.sleep(5)            
    #    while det.cam.num_capture.value != det.cam.num_captured.value:
    #        time.sleep(1)                
    det.cam.acquire.put("Done")
    samStage.move(samInPos)
    # set for white field -- end


def wait_temperature(trigTemp):
    """wait for temperature to reach trigger temperature"""
    previous = preTemp
    while ((preTemp-trigTemp)*(previous-trigTemp)>0):
        preTemp_ref = preTemp          
        time.sleep(0.5)


def InterlaceScan(
        exposureTime=0.006, 
        samInPos=0, 
        samOutPos=-4,
        roiSizeX = 2560, 
        roiSizeY = 800, 
        trigTemp = 550, 
        delay = 0, 
        repeat = 1, 
        interval = 60,
        flatPerScan = 0, 
        darkPerScan = 0,                                                                    
        accl = 60.0):
    cam = "edge" 
    shutter = A_shutter
    samStage = am49
    posStage = am20               
    rotStage = bm82
    pso = pso2
    # station = 'BHutch'
    BL = "2bmb"
    pso.scan_control.put("Custom")
    interlaceFlySub_2bmb.proc.put(1)
    slewSpeed = pso.slew_speed.value
    if samStage.user_setpoint.pvname.startswith('2bma'):
        station = 'AHutch'
    elif samStage.user_setpoint.pvname.startswith('2bmb'):    
        station = 'BHutch' 

    if cam == "edge":
        initEdge()
        camScanSpeed = "Fastest"
        camShutterMode = "Rolling"                
        det = pco_edge                                    

        imgPerSubCycle = 1.0*interlaceFlySub_2bmb.a.value/interlaceFlySub_2bmb.b.value
        secPerSubCycle = 180.0/pso.slew_speed.value
        frate = int(imgPerSubCycle/secPerSubCycle + 5)
        det.hdf1.file_number.put(caputRecorder10.value)
        savedata_2bmb.scan_number.put(caputRecorder10.value)

        print("Scan starts ...")

        shutter.open()
                    
        filepath_top = caputRecorder_filepath.value
        det.hdf1.create_directory.put(-5)
        det.hdf1.file_number.put(caputRecorder10.value)
        filename = caputRecorder_filename.value             # TODO: duplicate of filenameString?
        filepathString = caputRecorder_filepath.value
        filenameString = caputRecorder_filename.value
        
        logFilePath, logFileName = make_log_file(
            filepathString, filenameString, int(det.hdf1.file_number.value))
        print("Your scan is logged in ", logFileName)
        
        samInPos = samStage.position
        samOutPos = samInPos + samOutPos                                
                                            
        filepath = os.path.join(filepath_top, \
               caputRecorder1.value+ \
               caputRecorder2.value.zfill(3)+'_'+ \
               caputRecorder4.value+'_'+\
               'YPos'+str(int(posStage.position*1000)/1000.0)+'mm_'+\
               make_timestamp() + '_'+\
               cam+'_'+caputRecorder5.value+'x'+'_'+\
               caputRecorder6.value+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+\
               str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+\
               caputRecorder7.value+'um'+\
               caputRecorder8.value+'_'+\
               caputRecorder9.value+'_'+\
               str(int(A_mirror1.angle.value*1000)/1000.0)+'mrad_USArm'+\
               str(int(am30.position*1000)/1000.0)+\
               '_monoY_'+\
               str(int(am26.position*1000)/1000.0)+'_'+\
               station)
        """
        example:
        
        's:/data/2017_12/Commissioning/Exp005_TaoS_test_YPos12.58mm
        _FriJan12_15_53_23_2018_edge_10x_200mm_1.0msecExpTime
        _1.0DegPerSec_Rolling_20umLuAG_1mmAl0.5mmCu15mmSi0.79mmSn
        _0.0mrad_USArm1.149_monoY_-16.0_AHutch'
        """

        numImage = interlaceFlySub_2bmb.vale.value
        
        # test camera -- start
        _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO=PSO)
        
        # set scan parameters -- start
        # _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
        # _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
            
        # sample scan -- start  
        print("start sample scan ... ")
        
        wait_temperature(trigTemp)
        
        time.sleep(delay) 
        for ii in range(repeat):
            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
            rotStage.velocity.put(200)
            pso.taxi()
            _edgeInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                                       
            if ii < (repeat-1):
                print("repeat #", ii, " is done! next scan will be started in ", interval, " seconds ...")
                time.sleep(interval)

        shutter.open()
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print("sample scan is done!")
        # scan sample -- end                                                      
        
        # set for white field -- start
        if flatPerScan == 0:                                 
            print("Acquiring flat images ...")
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
            print("flat is done!")
        # set for white field -- end
        
#        # set for dark field -- start
        if darkPerScan == 0:                                
            print("Acquiring dark images ...")
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
            print("dark is done!")
    
        caputRecorder10.put(det.hdf1.file_number.value)
        if caputRecorder3.value == 'Yes':
            caputRecorder2.put(str(int(caputRecorder2.value)+1))
        # set for dark field -- end
        
        # set for new scans -- start
        det.hdf1.capture.put("Done")
        det.cam.acquire.put("Done")
        det.cam.pco_edge_fastscan.put("Normal")
        det.cam.pco_trigger_mode.put("Auto")
        det.cam.image_mode.put("Continuous")
        det.cam.size_x.put(roiSizeX)
        det.cam.size_y.put(roiSizeY)
        samStage.move(samInPos)
        # set for new scans -- end
        print("Scan is done.")
    elif cam == "dimax":
        raise RuntimeError("Dimax Interlace scan not implemented yet")
#         initDimax(samInPos=samInPos)    
#         det = pco_dimax     
#         # tomo configurations -- end                    
#     
# #        scanDelta = 1.0*angEnd/numProjPerSweep
# #        acclTime = 1.0*slewSpeed/accl
#         imgPerSubCycle = 1.0*interlaceFlySub_2bmb.a.value/interlaceFlySub_2bmb.b.value
#         secPerSubCycle = 180.0/pso.slew_speed.value
#         frate = int(imgPerSubCycle/secPerSubCycle + 100)                          
#         det.hdf1.file_number.put(caputRecorder10.value)
#         savedata_2bmb.scan_number.put(caputRecorder10.value)
#         # det.hdf1.file_number.put(userCalcs_2bmb.calc3.val.value)
#         print("Scan starts ...")
#         shutter.open()
#                     
#         filepath = caputRecorder_filepath   # TODO: duplicates?
#         filename = caputRecorder_filename
#     
#         filepathString = caputRecorder_filepath
#         filenameString = caputRecorder_filename
#         pathSep =  filepathString.rsplit('/')       # TODO: confusing syntax
#     
#         logFilePath, logFileName = make_log_file_path(
#             filepathString, filenameString, int(det.hdf1.file_number.value))
#         print("Your scan is logged in ", logFileName)
#         
#         numImage = interlaceFlySub_2bmb.vale.value
# #        numImage = det.cam.pco_max_imgs_seg0.value # camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL"
#         
#         # test camera -- start
#         _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#         # test camera -- end
#         
#         # set scan parameters -- start
#         _dimaxSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
# #        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
#         # set scan parameters -- end
#                     
#         print("start sample scan ... ")
#         rotStage.velocity.put(200)
#         pso.taxi()
#         
#         wait_temperature(trigTemp)
#         
#         time.sleep(delay)                
#         _dimaxInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                        
#         
#         logFile = open(logFileName,'a')
#         logFile.write("Scan was done at time: " + time.asctime() + '\n')
#         logFile.close()                                                                    
#         print("sample scan is done!")
#         # scan sample -- end
#         
#         # set for white field -- start
#         print("Acquiring flat images ...")
#         _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
#         print("flat is done!")
#         # set for white field -- end
#         
#         # set for dark field -- start
#         print("Acquiring dark images ...")
#         _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
#         print("dark is done!")
#     
#         caputRecorder10.put(det.hdf1.file_number)
#         # set for dark field -- end
#         
#         # set for new scans -- start
#         det.hdf1.capture.put("Done")
#         det.cam.acquire.put("Done")
#         det.cam.pco_trigger_mode.put("Auto")
#         det.cam.pco_live_view.put("Yes")
#         det.cam.size_x.put(roiSizeX)
#         det.cam.size_y.put(roiSizeY)
#         samStage.move(samInPos)
#         # set for new scans -- end
#         print("Scan is done.")
    pso.slew_speed.put(slewSpeed)
