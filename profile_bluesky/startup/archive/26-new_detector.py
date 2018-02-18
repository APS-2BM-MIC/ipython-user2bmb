print(__file__)


class LIXPilatus(SingleTrigger, PilatusDetector):
    # this does not get root is input because it is hardcoded above
    file = Cpt(PilatusFilePlugin, suffix="cam1:",
               write_path_template="", reg=db.reg)

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    stats1 = Cpt(StatsPlugin, 'Stats1:')
    stats2 = Cpt(StatsPlugin, 'Stats2:')
    stats3 = Cpt(StatsPlugin, 'Stats3:')
    stats4 = Cpt(StatsPlugin, 'Stats4:')

    reset_file_number = Cpt(Signal, name='reset_file_number', value=1)
    HeaderString = Cpt(EpicsSignal, "cam1:HeaderString")
    ThresholdEnergy = Cpt(EpicsSignal, "cam1:ThresholdEnergy")
    
    def __init__(self, *args, detector_id, **kwargs):
        self.detector_id = detector_id
        self._num_images = 1
        super().__init__(*args, **kwargs)

    def set_thresh(self, ene):
        """ set threshold
        """
        set_and_wait(self.ThresholdEnergy, ene)
        caput(self.prefix+"cam1:ThresholdApply", 1)
        
    def set_num_images(self, num_images):
        self._num_images = num_images
        
    def stage(self):
        self.cam.num_images.put(self._num_images)
        super().stage()
    
    def unstage(self):
        self.cam.num_images.put(1, wait=True)
super().unstage()
