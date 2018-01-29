print(__file__)

"""
functions converted from macros_2bmb.py (PyEpics macros from Xianghui)
"""

# HDF5 File Writer Plugin configuration for 2-BM-B
# -5: means create maximum 5 directories as needed
MAX_DIRECTORIES_TO_CREATE = -5


def auto_increment_prefix_number():
    """increment the prefix number if permitted"""
    if cpr_auto_increase.value == 'Yes':
        cpr_prefix_num.put(str(int(cpr_prefix_num.value)+1))


def string_by_index(choices_str, index, delim=" "):
    """
    pick a substring from a delimited string using the index as reference
    
    choices_str : str
        string with possible choices, separated by delimiter
    delim : str
        string delimiter
    index : int
        number (0-based) of label to be selected
    """
    choices = choices_str.split(delim)
    if index in range(len(choices)):
        return choices[index]
    return None


def make_timestamp(the_time=None):
    """
    such as: 2018-01-12 15:40:46 is FriJan12_15_40_46_2018
    
    the_time : str
        string representation of the time
        default time.asctime()
        example: Sun Jan 4 18:59:31 1959
        result:  SunJan4_18_59_31_1959
        
    """
    the_time = the_time or time.asctime()
    timestamp = [x for x in the_time.rsplit(' ') if x!='']
    timestamp = ''.join(timestamp[0:3]) \
                + '_' + timestamp[3].replace(':','_') \
                + '_' + timestamp[4]
    return timestamp


def trunc(v, n=3):
    """truncate `v` (a float) to `n` digits precision"""
    factor = pow(10, n)
    return int(v*factor)/factor


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
    cpr_filename.put("proj")
    path = "s:/data/2017_12/Commissioning"
    cpr_filepath.put(path)


def setDefaultFolderStructure():
    def caput_desc(signal, description):
        """.DESC field is not part of EpicsSignal"""
        pvname = signal.pvname.split(".")[0] + ".DESC"
        epics.caput(pvname, description, wait=True, timeout=1000.0)

    caput_desc(cpr_prefix, 'prefix')
    caput_desc(cpr_prefix_num, 'prefix #')
    caput_desc(cpr_auto_increase, 'auto-increase #')
    caput_desc(cpr_sample_name, 'sample name')
    caput_desc(cpr_lens_mag, 'lens mag')
    caput_desc(cpr_sam_det_dist, 'sam-det dist(mm)')
    caput_desc(cpr_scin_thickness, 'scinThickness(um)')
    caput_desc(cpr_scin_type, 'scinType')
    caput_desc(cpr_filter, 'filter')
    caput_desc(cpr_proj_num, 'proj #')

    cpr_filename.put('proj')
    cpr_prefix.put('Exp')
    cpr_prefix_num.put('1')
    cpr_auto_increase.put('Yes')
    cpr_sample_name.put('S1')
    cpr_lens_mag.put('10')
    cpr_sam_det_dist.put('50')
    cpr_scin_thickness.put('10')
    cpr_scin_type.put('LuAG')
    cpr_filter.put('1mmC1mmGlass')
    cpr_proj_num.put('1')
                                

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
        # FIXME: det.hdf1.num_captured.put(0)
    rotStage.servo.put("Enable")
    process_tableFly2_sseq_record()
    rotStage.velocity.put(180)
    rotStage.acceleration.put(3)
    rotStage.move(0)
    samStage.move(samInPos)
    print("Dimax is reset!")


def initEdge(samInPos=0, samStage=None, rotStage=None):
    """
    setup the PCO Edge detector
    """
    samStage = samStage or am49
    rotStage = rotStage or bm82
    det = pco_edge

    tomo_shutter.open()
    A_shutter.open()

    det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")

    det.cam.acquire.put("Done")

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
        # FIXME: det.hdf1.num_captured.put(0)
    det.image.enable.put("Enable")
    process_tableFly2_sseq_record()
    rotStage.stop()
    rotStage.set_current_position(rotStage.position % 360.0)
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
    energy_index = energy_index.data[0]        # pull value out of numpy array

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
    am7.move(XIASlit_list[energy_index])
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
    filepath_top = cpr_filepath.value

#    filepath = os.path.join(filepath_top, cpr_prefix.value+ \
#                cpr_prefix_num.value.zfill(3)+'_'+ 'Radiography_' +\
#                cpr_sample_name.value+'_'+\
#                      'YPos'+str(am20.position)+'mm_'+\
#                cam+'_'+cpr_lens_mag.value+'x'+'_'+\
#                cpr_sam_det_dist.value+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
#                camShutterMode+'_'+cpr_scin_thickness.value+'um'+\
#                cpr_scin_type.value+'_'+\
#                cpr_filter.value+'_'+\
#                str(A_mirror1.angle.value)+'mrad_USArm'+\
#                str(am30.position)+\
#                '_monoY_'+str(am26.position)+'_'+station)

    # det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")
    # if hasattr(det, "hdf1"):
    #     det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")

    for ii in range(repeat):
        tomo_shutter.close()
        
        if True:    # the old way
            filepath = os.path.join(filepath_top, \
                       cpr_prefix.value+ \
                       cpr_prefix_num.value.zfill(3)+'_'+ 'Radiography_'+\
                       cpr_sample_name.value+'_'+\
                       'YPos'+str(trunc(posStage.position))+'mm_'+\
                       make_timestamp() + '_'+\
                       cam+'_'+cpr_lens_mag.value+'x'+'_'+\
                       cpr_sam_det_dist.value+'mm'+'_'+\
                       str(exposureTime*1000)+'msecExpTime_'+\
                       camShutterMode+'_'+cpr_scin_thickness.value+'um'+\
                       cpr_scin_type.value+'_'+\
                       cpr_filter.value+'_'+\
                       str(trunc(A_mirror1.angle.value))+'mrad_'+\
                       'USArm'+str(trunc(am30.position))+'_'+\
                       'monoY_'+str(trunc(am26.position))+'_'+\
                       station)
        else:   # the proposed way
            # TODO: Which is easier to read & edit?
            #   'YPos'+str(int(posStage.position*1000)/1000.0)+'mm_'
            #   'YPos'+str(trunc(posStage.position))+'mm_'
            #   'YPos{}mm_'.format(trunc(posStage.position))
            #   'YPos{0:.3f}mm_'.format(posStage.position)    # NOTE: rounds instead of truncates
            #   'YPos%.3fmm_' % posStage.position    # NOTE: rounds instead of truncates

            # 2018-01-26, PRJ: I propose this looks easier to understand and maintain
            fp = '{}{}_'.format(cpr_prefix.value, cpr_prefix_num.value.zfill(3))
            fp += 'Radiography_'
            fp += '{}_'.format(cpr_sample_name.value)
            fp += 'YPos{0:.3f}mm_'.format(posStage.position)
            # fp += 'Ypos%.3fmm_' % posStage.position
            fp += '{}_'.format(make_timestamp())
            fp += '{}_'.format(cam)
            fp += '{}x_'.format(cpr_lens_mag.value)
            fp += '{}mm_'.format(cpr_sam_det_dist.value)
            fp += '{}msecExpTime_'.format(exposureTime*1000)
            fp += '{}_'.format(camShutterMode)
            fp += '{}um_'.format(cpr_scin_thickness.value)
            fp += '{}_'.format(cpr_scin_type.value)
            fp += '{}_'.format(cpr_filter.value)
            fp += '{0:.3f}mrad_'.format(A_mirror1.angle.value)
            fp += 'USArm{0:.3f}_'.format(am30.position)
            fp += 'monoY{0:.3f}_'.format(am26.position)
            fp += station
            filepath = os.path.join(filepath_top, fp)
        filename = cpr_filename.value   
    
        det.cam.acquire.put("Done")

        det.cam.pco_trigger_mode.put("Auto")
        det.cam.pco_is_frame_rate_mode.put("DelayExp")
        det.cam.pco_live_view.put("No")
        det.cam.size.size_x.put(roiSizeX)
        det.cam.size.size_y.put(roiSizeY)
        det.cam.acquire_period.put(0)

        if hasattr(det, "hdf1"):
            det.hdf1.capture.put("Done")
            det.hdf1.create_directory.put(MAX_DIRECTORIES_TO_CREATE)
            det.hdf1.file_number.put(cpr_proj_num.value)
            det.hdf1.enable.put("Enable")
            det.hdf1.auto_increment.put("Yes")
            det.hdf1.num_capture.put(numImage)
            # FIXME: det.hdf1.num_captured.put(numImage)
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

        cpr_proj_num.put(det.hdf1.file_number.value)
        auto_increment_prefix_number()

        print(str(ii), 'the acquisition is done at ', time.asctime())
        if ii != repeat-1:
            time.sleep(delay)

    det.cam.pco_live_view.put("Yes")
    tomo_shutter.close()
    A_shutter.close()
    print('Radiography acquisition finished!')


def EdgeMultiPosScan(
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
        timeFile=0, clShutter=1):
    """
    Multiple position scans along vertical direction with edge camera
    
    axisShift : float
        Rotation axis shift in unit um/mm. 
        Defined as the shift distance when the vertical stage moves up.
        Assumes rotation axis is at image center (`posInit`) when this 
        function is called.
    """

    BL = "2bmb"     # TODO: is this used?
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
    #station = 'BHutch'
    stack = 'LAT'
    #stack = 'SAT'
    samStage, posStage, rotStage, pso = motor_assignments[station][stack]

    if station == 'AHutch':
        ##### AHutch tomo configurations -- start
        shutter = A_shutter
        # tomo_shutter.open()
        camShutterMode = string_by_index("Rolling Global", shutterMode)
        if camShutterMode is None:
            print("Wrong camera shutter mode! Quit ...")
            return False

        camScanSpeed = string_by_index("Normal Fast Fastest", scanMode)
        if camScanSpeed is None:
            print("Wrong camera scan mode! Quit...")
            return False

        initEdge(samInPos=samInPos, samStage=samStage, rotStage=rotStage)
        ##### AHutch tomo configurations -- end                    

    elif station == 'BHutch':
        ##### BHutch tomo configurations -- start
        shutter = B_shutter
        initEdge()
        camScanSpeed = "Fastest"
        camShutterMode = "Rolling"
        samInInitPos = samInPos  
        ####### BHutch tomo configurations -- end    
    #-------------------------------------------------------------------

    #    posCurr = posStage.position
    #    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
    #    samStage.set_current_position(posStageOffset)
    #    cpr_arg14.put(str(posCurr))
                    
    #    ''' 
    #    this is the case in which the rotation axis move toward left side 
    #    (smaller 'center' in reconstruction)
    #    when the sample stage moves up.                                                                
    #    '''
    #    if posStep > 0:
    #        axisShift = np.abs(axisShift)    
    #    elif posStep < 0:    
    #        axisShift = -np.abs(axisShift)    

    #    ''' 
    #    this is the case in which the rotation axis move toward right side 
    #    (larger 'center' in reconstruction)
    #    when the sample stage moves up.                            
    #    '''
    #
    #    if posStep > 0:
    #        axisShift = -np.abs(axisShift)    
    #    elif posStep < 0:    
    #        axisShift = np.abs(axisShift)                                

    filepath_top = cpr_filepath.value
           
    det.hdf1.create_directory(MAX_DIRECTORIES_TO_CREATE)
               
    posInit = posStage.position
    pso.scan_control.put("Standard")
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)

    det.hdf1.file_number.put(cpr_proj_num.value)
            
    #    shutter.open()
                    
    #    filepath = cpr_filepath.value
    filename = cpr_filename.value

    filepathString = cpr_filepath.value
    filenameString = cpr_filename.value
    pathSep =  filepathString.rsplit('/')
    logFilePath, logFileName = make_log_file(
            filepathString, filenameString, 
            int(det.hdf1.file_number.value))
    print("Your scan is logged in ", logFileName)
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print(roiSizeX, roiSizeY)
    _edgeTest(camScanSpeed, camShutterMode, roiSizeX=roiSizeX, roiSizeY=roiSizeY, pso=pso)

    # sample scan -- start
    #    shutter.open()
    if timeFile == 1:
        tf = open('~/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close() 
        posNum = len(timeSeq)            
    print("start sample scan ... ")
    for ii in range(posNum):
        # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 
            
        posStage.move(posInit+ii*posStep)

        ##### heating with Eurotherm2K:3                                            
        #        filepath = os.path.join(filepath_top, \
        #               cpr_prefix.value+ \
        #               cpr_prefix_num.value.zfill(3)+'_'+ \
        #               cpr_sample_name.value+'_'+\
        #               str(int(preTemp.value))+'C_'+\
        #               str(ii).zfill(1) + '_' + \
        #               'YPos'+str(trunc(posStage.position))+'mm_'+\
        #               make_timestamp() + '_'+\
        #               cam+'_'+cpr_lens_mag.value+'x'+'_'+\
        #               cpr_sam_det_dist.value+'mm'+'_'+\
        #               str(exposureTime*1000)+'msecExpTime_'+\
        #               str(slewSpeed)+'DegPerSec_'+\
        #               camShutterMode+'_'+\
        #               cpr_scin_thickness.value+'um'+\
        #               cpr_scin_type.value+'_'+\
        #               cpr_filter.value+'_'+\
        #               str(trunc(A_mirror1.angle.value))+'mrad_USArm'+\
        #               str(trunc(am30.position))+\
        #               '_monoY_'+str(trunc(am26.position))+'_'+station) 

        ##### tension with 2bma:m58
        #        s1_d1done_read.put(1)
        #        filepath = os.path.join(filepath_top, \
        #               cpr_prefix.value+ \
        #               cpr_prefix_num.value.zfill(3)+'_'+ \
        #               cpr_sample_name.value+'_'+\
        #               str('{:5.5f}'.format(s1_d1dmm_calc.value))+'N_'+\
        #               str(ii).zfill(2) + '_' + \
        #               'YPos'+str(trunc(posStage.position))+'mm_'+\
        #               make_timestamp() + '_'+\
        #               cam+'_'+cpr_lens_mag.value+'x'+'_'+\
        #               cpr_sam_det_dist.value+'mm'+'_'+\
        #               str(exposureTime*1000)+'msecExpTime_'+\
        #               str(slewSpeed)+'DegPerSec_'+\
        #               camShutterMode+'_'+\
        #               cpr_scin_thickness.value+'um'+\
        #               cpr_scin_type.value+'_'+\
        #               cpr_filter.value+'_'+\
        #               str(trunc(A_mirror1.angle.value))+'mrad_USArm'+\
        #               str(trunc(am30.position))+\
        #               '_monoY_'+str(trunc(am26.position))+'_'+station) 

        #        filepath = os.path.join(filepath_top, \
        #               cpr_prefix.value+ \
        #               cpr_prefix_num.value.zfill(3)+'_'+ \
        #               cpr_sample_name.value+'_'+\
        #               'YPos'+str(trunc(posStage.position))+'mm_'+\
        #               '0DegPos'+str(trunc(s1m2.position))+'mm_'+\
        #               '90DegPos'+str(trunc(s1m1.position))+'mm_'+\
        #               make_timestamp() + '_'+\
        #               cam+'_'+cpr_lens_mag.value+'x'+'_'+\
        #               cpr_sam_det_dist.value+'mm'+'_'+\
        #               str(exposureTime*1000)+'msecExpTime_'+\
        #               str(slewSpeed)+'DegPerSec_'+\
        #               camShutterMode+'_'+\
        #               cpr_scin_thickness.value+'um'+\
        #               cpr_scin_type.value+'_'+\
        #               cpr_filter.value+'_'+\
        #               str(trunc(A_mirror1.angle.value))+'mrad_USArm'+\
        #               str(trunc(am30.position))+\
        #               '_monoY_'+str(trunc(am26.position))+'_'+station) 

        #### normal filename
        # 2018-01-26, PRJ: I propose this looks easier to understand and maintain
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
        filepath = os.path.join(filepath_top, fp)
                   
        _edgeSet(filepath, filename, numImage, exposureTime, frate, pso=pso)
        _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, pso=pso, rotStage=rotStage)                              
        shutter.open()
        tomo_shutter.close()
        time.sleep(3)                                                            
        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter, pso=pso, rotStage=rotStage)
        det.cam.acquire.put("Done")
        print("scan at position #",ii+1," is done!")

        samOutPos = samInPos + samOutDist
        
        if flatPerScan == 1:
        # set for white field -- start                   
            print("Acquiring flat images ...")
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso)       
            det.cam.acquire.put("Done")
            print("flat for position #", ii+1, " is done!")
        # set for white field -- end                                            
                                
        if darkPerScan == 1:
            # set for dark field -- start
            print("Acquiring dark images ...")
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso) 
            det.cam.acquire.put("Done")
            print("dark is done!")
        if posNum!=1 and darkPerScan!=0 and flatPerScan!=0 and ii!=(posNum-1):       
            det.hdf1.capture.put("Done")
        cpr_proj_num.put(det.hdf1.file_number.value)
        # set for dark field -- end
                                
        auto_increment_prefix_number()
        
        if ii != (posNum-1):
            time.sleep(delay)

    shutter.close()
    tomo_shutter.close()
    print("sample scan is done!")

    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if clShutter==1:
        if flatPerScan == 0:    
            # set for white field -- start                   
            print("Acquiring flat images ...")
            shutter.open()
            time.sleep(3)                
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso) 
            det.cam.acquire.put("Done")
    #        det.hdf1.capture.put("Done")
            print("flat is done!")
            # set for white field -- end
    
        if darkPerScan == 0:    
            # set for dark field -- start
            print("Acquiring dark images ...")
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso)
            det.cam.acquire.put("Done")
    #        det.hdf1.capture.put("Done")
            print("dark is done!")

    det.hdf1.capture.put("Done")
    cpr_proj_num.put(det.hdf1.file_number.value)
    # set for dark field -- end
    
    # set for new scans -- start
    det.cam.pco_edge_fastscan.put("Normal")
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.image_mode.put("Continuous")
    det.cam.size_x.put(roiSizeX)
    det.cam.size_y.put(roiSizeY)
    # set for new scans -- end
    print("Scan finished!")
    posStage.move(posInit)


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
    """radiography using the edge detector"""

    station = 'AHutch'
    # station = 'BHutch'   
    samStage = am49
    posStage = am20
    rotStage = bm82
    pso = pso2
    cam = "edge"
    det = pco_edge
    BL = "2bmb"

    shutter = A_shutter
    shutter.open()
    tomo_shutter.close()

    numImage = frmRate * acqPeriod
                
    if scanMode in (0, 1, 2):
        camScanSpeed = "Normal Fast Fastest".split()[scanMode]
    else:
        print("Wrong camera scan mode! Quit...")
        return False

    camShutterMode = "Rolling"                

    filepath_top = cpr_filepath.value

    for ii in range(repeat):
        fp = '{}{}_'.format(cpr_prefix.value, cpr_prefix_num.value.zfill(3))
        fp += 'Radiography_'
        fp += '{}_'.format(cpr_sample_name.value)
        fp += 'YPos{0:.3f}mm_'.format(posStage.position)
        fp += '{}_'.format(make_timestamp())
        fp += '{}_'.format(cam)
        fp += '{}x_'.format(cpr_lens_mag.value)
        fp += '{}mm_'.format(cpr_sam_det_dist.value)
        fp += '{}msecExpTime_'.format(exposureTime*1000)
        fp += '{}_'.format(camShutterMode)
        fp += '{}um_'.format(cpr_scin_thickness.value)
        fp += '{}_'.format(cpr_scin_type.value)
        fp += '{}_'.format(cpr_filter.value)
        fp += '{0:.3f}mrad_'.format(A_mirror1.angle.value)
        fp += 'USArm{0:.3f}_'.format(am30.position)
        fp += 'monoY{0:.3f}_'.format(am26.position)
        fp += station
        filepath = os.path.join(filepath_top, fp)

        filename = cpr_filename.value
    
        det.cam.acquire.put("Done")

        if hasattr(det, "hdf1"):
            det.hdf1.capture.put("Done",)
            det.hdf1.create_directory.put(MAX_DIRECTORIES_TO_CREATE)
            det.hdf1.file_number.put(cpr_proj_num.value)

        det.cam.pco_trigger_mode.put("Auto")
        det.cam.image_mode.put("Multiple")
        det.cam.num_images.put(numImage)
        det.cam.pco_edge_fastscan.put(camScanSpeed)
        det.cam.pco_trigger_mode.put("Auto")
        det.cam.size.size_x.put(roiSizeX)
        det.cam.size.size_y.put(roiSizeY)
        det.cam.pco_global_shutter.put(camShutterMode)
        det.cam.pco_is_frame_rate_mode.put("DelayExp")
        det.cam.acquire_period.put(0)
        det.cam.frame_type.put("Normal")

        if hasattr(det, "hdf1"):
            det.hdf1.enable.put("Enable")
            det.hdf1.auto_increment.put("Yes")
            det.hdf1.num_capture.put(numImage+20)
            # FIXME: det.hdf1.num_captured.put(0)
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
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso)
        print('flat is done')
             
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso)
        print('dark is done')
    
        shutter.close()
        tomo_shutter.close()
        det.cam.image_mode.put("Continuous")

        if hasattr(det, "hdf1"):
            cpr_proj_num.put(det.hdf1.file_number.value)
        auto_increment_prefix_number()

        print(str(ii), 'the acquisition is done at ', time.asctime())
        if ii != repeat-1:
            time.sleep(delay)

    print('Radiography acquisition finished!')


def _setPSO(slewSpeed, scanDelta, acclTime, angStart=0, angEnd=180, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82

    pso.start_pos.put(angStart)
    pso.end_pos.put(angEnd)
    rotStage.velocity.put(slewSpeed)
    pso.slew_speed.put(slewSpeed)
    rotStage.acceleration.put(acclTime)
    pso.scan_delta.put(scanDelta)


def _edgeTest(camScanSpeed,camShutterMode,roiSizeX=2560,roiSizeY=2160,pso=None):
    pso = pso or pso1
    det = pco_edge

    # pso.scan_control.put("Standard")
    det.cam.array_callbacks.put("Enable")
    det.cam.num_images.put(10)
    det.cam.image_mode.put("Multiple")
    det.cam.pco_global_shutter.put(camShutterMode)
    det.cam.pco_edge_fastscan.put(camScanSpeed)
    det.cam.acquire_time.put(0.001000)
    det.cam.size.size_x.put(roiSizeX)
    det.cam.size.size_y.put(roiSizeY)
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")
    print("camera passes test!")


def _edgeSet(filepath, filename, numImage, exposureTime, frate, pso=None):
    pso = pso or pso1    
    det = pco_edge

    det.cam.pco_is_frame_rate_mode.put("DelayExp")
    det.cam.acquire_period.put(0)
    det.cam.pco_set_frame_rate.put(frate+1)     # TODO: why twice?
    det.cam.pco_set_frame_rate.put(frate)
    det.hdf1.auto_increment.put("Yes")
    det.hdf1.num_capture.put(numImage)
    det.hdf1.num_capture.put(numImage)
    # FIXME: det.hdf1.num_captured.put(0)
    det.hdf1.file_path.put(filepath)
    det.hdf1.file_name.put(filename)
    det.hdf1.file_template.put("%s%s_%4.4d.hdf")
    det.hdf1.auto_save.put("Yes")
    det.hdf1.file_write_mode.put("Stream")
    det.hdf1.capture.put("Capture", wait=False)
    det.cam.num_images.put(numImage)
    det.cam.image_mode.put("Multiple")
    det.cam.acquire_time.put(exposureTime)
    det.cam.pco_trigger_mode.put("Soft/Ext")
    det.cam.pco_ready2acquire.put(0)
    det.cam.acquire.put("Acquire", wait=False)


def _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    shutter.open()
    det.cam.frame_type.put("Normal")
    samStage.move(samInPos)
    rotStage.velocity.put(50.00000)
    rotStage.move(0.00000)
    pso.taxi()
    pso.fly()
    if pso.pso_fly.value == 0 & clShutter == 1:               
        shutter.close()     
    # Does this change the RVAL also?  Really need to change the RVAL at the same time.
    # If offset is FIXED, then writing to VAL also writes to DVAL.
    # TODO: verify this
    rotStage.set_current_position(1.0*rotStage.position%360.0)
    rotStage.velocity.put(50.00000)
    time.sleep(1)
    rotStage.move(0.00000)
    # shutter.close()
    while (det.hdf1.num_captured.value != numProjPerSweep):    
        time.sleep(1)                    


def _edgeInterlaceAcquisition(samInPos,samStage,numProjPerSweep,shutter, clShutter=1, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    det.cam.frame_type.put("Normal")
    samStage.move(samInPos)
    pso.put("Fly")
    # shutter.close()
    # shutter.open()
    if clShutter == 1:
        shutter.close()
    rotStage.set_current_position(1.0*rotStage.position%360.0)
    rotStage.velocity.put(50.00000)
    rotStage.move(0, wait=False)
    numProjPerSweep = det.cam.num_images_counter.value
    print("Saving sample data ...")
    while (det.hdf1.num_captured.value != numProjPerSweep):    
        time.sleep(1)
    # det.cam.acquire.put("Done")
    # det.hdf1.capture.put("Done")


def _edgeAcquireDark(samInPos,filepath,samStage,rotStage, shutter, pso=None):
    pso = pso or pso1
    det = pco_edge

    pso.scan_control.put("Standard")
    shutter.close()
    time.sleep(5)
            
    det.cam.frame_type.put("Background")
    det.hdf1.num_images.put(10)

    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")
        
    # pso.start_pos.put(0.00000)
    # pso.end_pos.put(6.0000)
    # pso.scan_delta.put(0.3)
    # pso.slew_speed.put(1)
    # rotStage.velocity.put(3)
    # rotStage.acceleration.put(1)
    # pso.taxi()
    # pso.fly()
    # rotStage.velocity.put(50)
    # rotStage.move(0)
             
    #    while det.hdf1.num_capture.value != det.hdf1.num_captured.value:
    #        time.sleep(1)                
    det.cam.acquire.put("Done")
    samStage.move(samInPos)


def _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage, shutter, pso=None):
    pso = pso or pso1
    det = pco_edge

    samStage.move(str(samOutPos), wait=False)
    pso.scan_control.put("Standard")
    shutter.open()
    time.sleep(5)
    det.cam.frame_type.put("FlatField")
    det.cam.num_images.put(10)
    
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.acquire.put("Acquire")

    # pso.start_pos.put(0.00000)
    # pso.end_pos.put(6.0000)
    # pso.scan_delta.put(0.3)
    # pso.slew_speed.put(1)
    # rotStage.velocity.put(3)
    # rotStage.acceleration.put(1)
    # pso.taxi()
    # pso.fly()
    # rotStage.velocity.put(50)
    # rotStage.move(0)
    
    shutter.close()
    time.sleep(5)            
    #    while det.hdf1.num_capture.value != det.hdf1.num_captured.value:
    #        time.sleep(1)                
    det.cam.acquire.put("Done")
    samStage.move(samInPos)
    # set for white field -- end


def wait_temperature(T_trig, epsilon=0.1):
    """
    wait for temperature to reach trigger temperature
    
    T_trig : float
        temperature set point
    epsilon : float
        how close to set point is acceptable
    """
    T_last = preTemp.value
    # This test requires an exact temperature match for two readings.
    #while ((preTemp.value-T_trig)*(T_last-T_trig)>0):
    #    T_last = preTemp.value          
    #    time.sleep(0.5)

    # Allow for inexact but close enough
    while abs(preTemp.value - T_trig) > epsilon \
          or abs(T_last - T_trig) > epsilon:
        T_last = preTemp.value          
        time.sleep(0.5)
    # reached temperature


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
    """interlace scan not used as much now"""
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
        det.hdf1.file_number.put(cpr_proj_num.value)
        savedata_2bmb.scan_number.put(cpr_proj_num.value)

        print("Scan starts ...")

        shutter.open()
                    
        filepath_top = cpr_filepath.value
        det.hdf1.create_directory.put(MAX_DIRECTORIES_TO_CREATE)
        det.hdf1.file_number.put(cpr_proj_num.value)
        filename = cpr_filename.value             # TODO: duplicate of filenameString?
        filepathString = cpr_filepath.value
        filenameString = cpr_filename.value
        
        logFilePath, logFileName = make_log_file(
            filepathString, filenameString, int(det.hdf1.file_number.value))
        print("Your scan is logged in ", logFileName)
        
        samInPos = samStage.position
        samOutPos = samInPos + samOutPos                                
                                            
        # TODO: reefactor per above (build up `fp` by parts)
        filepath = os.path.join(filepath_top, \
               cpr_prefix.value+ \
               cpr_prefix_num.value.zfill(3)+'_'+ \
               cpr_sample_name.value+'_'+\
               'YPos'+str(trunc(posStage.position))+'mm_'+\
               make_timestamp() + '_'+\
               cam+'_'+cpr_lens_mag.value+'x'+'_'+\
               cpr_sam_det_dist.value+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+\
               str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+\
               cpr_scin_thickness.value+'um'+\
               cpr_scin_type.value+'_'+\
               cpr_filter.value+'_'+\
               str(trunc(A_mirror1.angle.value))+'mrad_USArm'+\
               str(trunc(am30.position))+\
               '_monoY_'+\
               str(trunc(am26.position))+'_'+\
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
        _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,pso=pso)
        
        # set scan parameters -- start
        # _edgeSet(filepath, filename, numImage, exposureTime, frate, pso=pso)
        # _setPSO(slewSpeed, scanDelta, acclTime, pso=pso,rotStage=rotStage)
            
        # sample scan -- start  
        print("start sample scan ... ")
        
        wait_temperature(trigTemp)
        
        time.sleep(delay) 
        for ii in range(repeat):
            _edgeSet(filepath, filename, numImage, exposureTime, frate, pso=pso)
            rotStage.velocity.put(200)
            pso.taxi()
            _edgeInterlaceAcquisition(samInPos,samStage,numImage,shutter, pso=pso, rotStage=rotStage)                                       
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
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso)            
            print("flat is done!")
        # set for white field -- end
        
#        # set for dark field -- start
        if darkPerScan == 0:                                
            print("Acquiring dark images ...")
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso)            
            print("dark is done!")
    
        cpr_proj_num.put(det.hdf1.file_number.value)
        auto_increment_prefix_number()
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
#         det.hdf1.file_number.put(cpr_proj_num.value)
#         savedata_2bmb.scan_number.put(cpr_proj_num.value)
#         # det.hdf1.file_number.put(userCalcs_2bmb.calc3.val.value)
#         print("Scan starts ...")
#         shutter.open()
#                     
#         filepath = cpr_filepath   # TODO: duplicates?
#         filename = cpr_filename
#     
#         filepathString = cpr_filepath
#         filenameString = cpr_filename
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
#         _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY, pso=pso)
#         # test camera -- end
#         
#         # set scan parameters -- start
#         _dimaxSet(filepath, filename, numImage, exposureTime, frate, pso=pso)
# #        _setPSO(slewSpeed, scanDelta, acclTime, pso=pso,rotStage=rotStage)
#         # set scan parameters -- end
#                     
#         print("start sample scan ... ")
#         rotStage.velocity.put(200)
#         pso.taxi()
#         
#         wait_temperature(trigTemp)
#         
#         time.sleep(delay)                
#         _dimaxInterlaceAcquisition(samInPos,samStage,numImage,shutter, pso=pso, rotStage=rotStage)                        
#         
#         logFile = open(logFileName,'a')
#         logFile.write("Scan was done at time: " + time.asctime() + '\n')
#         logFile.close()                                                                    
#         print("sample scan is done!")
#         # scan sample -- end
#         
#         # set for white field -- start
#         print("Acquiring flat images ...")
#         _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, pso=pso)        
#         print("flat is done!")
#         # set for white field -- end
#         
#         # set for dark field -- start
#         print("Acquiring dark images ...")
#         _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, pso=pso)                
#         print("dark is done!")
#     
#         cpr_proj_num.put(det.hdf1.file_number.value)
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
