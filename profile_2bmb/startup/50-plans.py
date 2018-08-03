print(__file__)

"""plans"""


def basic(*args, darks=1, whites=1, images=1):
    det = pg3_det
    luftpause = 1
    
    yield from bps.mv(det.hdf1.num_capture, darks+whites+images)
    yield from bps.stage(det)

    print("%d dark frames" % darks)
    yield from bps.mv(
        det.cam.frame_type, 1,
        det.cam.num_images, darks,
    )
    yield from bps.sleep(luftpause)
    yield from bps.trigger(det)

    print("%d white frames" % whites)
    yield from bps.mv(
        det.cam.frame_type, 2,
        det.cam.num_images, whites,
    )
    yield from bps.sleep(luftpause)
    yield from bps.trigger(det)

    print("%d image frames" % images)
    yield from bps.mv(
        det.cam.frame_type, 0,
        det.cam.num_images, images,
    )
    yield from bps.sleep(luftpause)
    yield from bps.trigger(det)

    print("waiting for HDF5 writer to finish")
    # instead of setting det.hdf1.blocking_callbacks to "Yes"
    while det.hdf1.capture.value != 0:
        yield from bps.sleep(0.01)

    yield from bps.unstage(det)
