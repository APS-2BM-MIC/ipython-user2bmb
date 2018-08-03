print(__file__)

"""plans"""


def basic(*args, darks=1, whites=1, images=1):
    det = pg3_det
        
    yield from bps.mv(
        det.hdf1.num_capture, darks+whites+images,
        det.hdf1.compression, "zlib",
    )
    yield from bps.stage(det)

    print("%d dark frames" % darks)
    yield from bps.mv(
        det.cam.frame_type, 1,
        det.cam.num_images, darks,
    )
    yield from bps.trigger(det)
    while det.hdf1.num_captured.value < darks:
        yield from bps.sleep(0.01)

    print("%d white frames" % whites)
    yield from bps.mv(
        det.cam.frame_type, 2,
        det.cam.num_images, whites,
    )
    yield from bps.trigger(det)
    while det.hdf1.num_captured.value < darks+whites:
        yield from bps.sleep(0.01)

    print("%d image frames" % images)
    yield from bps.mv(
        det.cam.frame_type, 0,
        det.cam.num_images, images,
    )
    yield from bps.trigger(det)
    while det.hdf1.num_captured.value < darks+whites+images:
        yield from bps.sleep(0.01)

    print("waiting for HDF5 writer to finish")
    # instead of setting det.hdf1.blocking_callbacks to "Yes"
    while det.hdf1.capture.value != 0:
        yield from bps.sleep(0.01)
    yield from bps.mv(
        det.hdf1.num_capture, 1,
        det.cam.num_images, 1,
        det.hdf1.compression, "None",
    )

    yield from bps.unstage(det)
