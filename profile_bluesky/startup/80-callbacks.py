print(__file__)

# custom callbacks

import APS_BlueSky_tools.callbacks
import APS_BlueSky_tools.filewriters

# collect last scan's documents into doc_collector.documents
doc_collector = APS_BlueSky_tools.callbacks.DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

#specwriter = APS_BlueSky_tools.filewriters.SpecWriterCallback()
#specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
#callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
#print("SPEC data file:", specwriter.spec_filename)


from APS_BlueSky_tools.zmq_pair import ZMQ_Pair, mona_zmq_sender
from collections import deque


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


class MyCallbackReceiver(object):
    def __init__(self, talker):
        self.talker = talker
        self.thread_queue = deque()

    def receiver(self, key, document):
        """
        receives documents from a BlueSky Callback and starts ZMQ receiver in a thread
        """
        print("MyCallbackReceiver.receiver()\n", key, document)
        #thread = threading.Thread(target=self.talker, args=(key, document), daemon=True)
        #self.thread_queue.append(thread.start())
        
        # daemon=True avoids need to walk the thread queue and remove the dead ones


zmq_talker = MonaCallback0MQ(
    detector=pco_edge.image,
    signal_name=pco_edge.image.array_counter.name,
    rotation_name=bm82.user_readback.name,
    host=None)

zmq_thread_factory = MyCallbackReceiver(zmq_talker.receiver)

RE.subscribe(zmq_thread_factory.receiver)


def simple_plan():
    yield from bps.open_run()
    yield from bps.monitor(bm82)
    for pos in range(10, -1, -1):
        yield from bps.mv(bm82, float(pos))
        yield from bps.sleep(0.5)
    yield from bps.unmonitor(bm82)
    yield from bps.close_run()

def simple_planb():
    yield from bps.open_run()
    yield from bps.monitor(pco_edge.image.array_counter)
    yield from bps.sleep(20)
    yield from bps.unmonitor(pco_edge.image.array_counter)
    yield from bps.close_run()
