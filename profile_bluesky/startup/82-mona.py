print(__file__)

# custom callbacks

import APS_BlueSky_tools.callbacks
import APS_BlueSky_tools.filewriters
from APS_BlueSky_tools.zmq_pair import ZMQ_Pair, mona_zmq_sender
import bluesky.plan_stubs as bps


doc_collector = APS_BlueSky_tools.callbacks.DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = APS_BlueSky_tools.filewriters.SpecWriterCallback()
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
print("SPEC data file:", specwriter.spec_filename)


class MonaCallback0MQ(object):
    """
    My BlueSky 0MQ talker to send *all* documents emitted
    """
    
    def __init__(self, 
            host=None, port=None, detector=None, signal_name=None,
            rotation_name=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
        self.signal_name = signal_name
        self.rotation_name = rotation_name
    
    def end(self):
        """ZMQ client tells the server to end the connection"""
        self.talker.end()

    def receiver(self, key, document):
        """receive from RunEngine, send from 0MQ talker"""
        mona_zmq_sender(
            self.talker, 
            key, 
            document, 
            self.detector, 
            signal_name=self.signal_name,
            rotation_name=self.rotation_name)


def demo_mona_count():
    """
    show how to use stream an image signal for MONA via 0MQ
    """
    calc2 = calcs.calc2
    swait_setup_incrementer(calc1)
    swait_setup_random_number(calc2)
    ad_continuous_setup(adsimdet, acq_time=0.1)
    scaler.preset_time.put(0.5)
    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    adsimdet.stage_sigs.update({'cam.image_mode': 'Continuous'})

    staged_device_list = [adsimdet]
    monitored_signals_list = [
        adsimdet.image.array_counter, 
        calc1.val, 
        calc2.val, 
        m1.user_readback,
        ]
    
    @bpp.stage_decorator(staged_device_list)
    @bpp.monitor_during_decorator(monitored_signals_list)
    def mona_core(detectors, acquire, num=1):
        yield from bps.trigger(adsimdet, wait=False)
        yield from bp.count(detectors, num=num)
    
    RE(mona_core([scaler], adsimdet.cam.acquire, num=3))


def demo_mona_motor_scan(detectors, area_det, motor, start, finish, num=10, md={}):
    """
    show how to use a motor and stream an image signal for MONA via 0MQ
    
    EXAMPLE:
    
        zmq_talker = demo_setup_mona_callback_as_zmq_client()
        demo_mona_motor_scan([scaler], adsimdet, m1, -1, 0, num=1)
    
    """
    ad_continuous_setup(area_det, acq_time=0.1)
    scaler.preset_time.put(0.5)
    scaler.channels.read_attrs = ['chan1', 'chan2', 'chan3', 'chan6']
    area_det.stage_sigs.update({'cam.image_mode': 'Continuous'})
    
    # this turns the motor speed way down
    # m1.stage_sigs["velocity"] = 1
    # this sets it back to normal
    # m1.velocity = 30

    monitored_signals_list = [
        area_det.image.array_counter, 
        motor.user_readback,
        ]
    staged_device_list = [area_det]
    
    metadata = dict(
        demo="MONA motor scan",
        purpose="development",
    )
    metadata.update(md)
    
    @bpp.stage_decorator(staged_device_list)
    @bpp.monitor_during_decorator(monitored_signals_list)
    def mona_core(detector_list, acquire, num=1):
        yield from bps.trigger(area_det, wait=False)
        yield from bp.scan(detector_list, motor, start, finish, num=num)
    
    RE(mona_core(detectors, adsimdet.cam.acquire, num=3), md=metadata)


def demo_setup_mona_callback_as_zmq_client(host=None):
    """
    Prepare to demo the MONA 0MQ callback chain
    First: be sure the ZMQ server code is already running (outside of BlueSky).
    Clear out any existing BlueSky setup we don't want now.
    
    EXAMPLE::
    
        zmq_talker = demo_setup_mona_callback_as_zmq_client()
        
        # ... use the queue
        
        zmq_talker.end()
        exit   # end the ipython BlueSky session
    
    """
    prune_list = "doc_collector specwriter zmq_talker BestEffortCallback".split()
    prune_list = "specwriter zmq_talker BestEffortCallback".split()
    for key in prune_list:
        if key in callback_db:
            RE.unsubscribe(callback_db[key])
            del callback_db[key]
    zmq_talker = MonaCallback0MQ(
        detector=adsimdet.image,
        signal_name=adsimdet.image.array_counter.name,
        rotation_name=m1.user_readback.name,
        host=host)
    callback_db['zmq_talker'] = RE.subscribe(zmq_talker.receiver)
    return zmq_talker
