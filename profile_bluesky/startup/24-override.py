print(__file__)


"""
We want control of the file path, name, and number.
We think we need to override the standard practices from ophyd.
"""

import logging
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from pathlib import PurePath


logger = logging.getLogger(__name__)


class FileStorePluginBase(FileStoreBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update([('auto_increment', 'Yes'),
                                ('array_counter', 0),
                                ('auto_save', 'Yes'),
                                ('num_capture', 0),
                                ])
        self._fn = None

    def make_filename(self):
        '''Make a filename.

        This is a hook so that the read and write paths can either be modified
        or created on disk prior to configuring the areaDetector plugin.

        Returns
        -------
        filename : str
            The start of the filename
        read_path : str
            Path that ophyd can read from
        write_path : str
            Path that the IOC can write to
        '''
        filename = new_short_uid()
        formatter = datetime.now().strftime
        write_path = formatter(self.write_path_template)
        read_path = formatter(self.read_path_template)
        return filename, read_path, write_path

    def stage(self):
        # Make a filename.
        filename, read_path, write_path = self.make_filename()

        # Ensure we do not have an old file open.
        set_and_wait(self.capture, 0)
        # These must be set before parent is staged (specifically
        # before capture mode is turned on. They will not be reset
        # on 'unstage' anyway.
        set_and_wait(self.file_path, write_path)
        set_and_wait(self.file_name, filename)
        #set_and_wait(self.file_number, 0)
        super().stage()

        # AD does this same templating in C, but we can't access it
        # so we do it redundantly here in Python.
        self._fn = self.file_template.get() % (read_path,
                                               filename,
                                               self.file_number.get() - 1)
                                               # file_number is *next* iteration
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError("Path %s does not exist on IOC."
                          "" % self.file_path.get())


class FileStoreHDF5(FileStorePluginBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5'  # spec name stored in resource doc
        self.stage_sigs.update([('file_template', '%s%s_%6.6d.h5'),
                                ('file_write_mode', 'Stream'),
                                ('capture', 1)
                                ])

    def get_frames_per_point(self):
        return self.num_capture.get()

    def stage(self):
        super().stage()
        res_kwargs = {'frame_per_point': self.get_frames_per_point()}
        logger.debug("Inserting resource with filename %s", self._fn)
        fn = PurePath(self._fn).relative_to(self.reg_root)
        self._resource = self._reg.register_resource(
            self.filestore_spec,
            str(self.reg_root), str(fn),
            res_kwargs)


class FileStoreHDF5IterativeWrite(FileStoreHDF5, FileStoreIterativeWrite):
    pass


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
#class MyHDF5Plugin(HDF5Plugin):
    """adapt HDF5 plugin for AD 2.5+"""
    
    file_number_sync = None
    capture_VAL = Component(EpicsSignal, "Capture")

    # FIXME:  .put() works OK but .value returns numpy object metadata
    # In [48]: pco_edge.hdf1.xml_layout_file.get()
    # Out[48]: '<array size=21, type=time_char>'
    # FIXME: xml_layout_file = Component(EpicsSignalWithRBV, "XMLFileName", string=True)
    xml_layout_file = Component(EpicsSignal, "XMLFileName", string=True)    # use as WRITE-ONLY for now due to error above
    xml_layout_valid = Component(EpicsSignalRO, "XMLValid_RBV")
    xml_layout_error_message = Component(EpicsSignalRO, "XMLErrorMsg_RBV", string=True)
    
    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()
