#!/home/beams/USER2BMB/Apps/BlueSky/bin/python

import argparse
import sys
import time

import numpy as np
import pyqtgraph
from   pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from   pyqtgraph.widgets.RawImageWidget import RawImageWidget

import pvaccess


framesDisplayed = 0
gain = None
black = None
MAX_FRAMES = 300


def update(v):
    global framesDisplayed, gain, black, MAX_FRAMES

    i = v['value'][0]['ubyteValue']
    if not args.noAGC:
        if gain is None:
            # compute black point and gain from first frame
            black, white = np.percentile(i, [0.01, 99.99])
            gain = 255 / (white - black)
        i = (i - black) * gain
        i = np.clip(i, 0, 255).astype('uint8')

    # resize to get a 2D array from 1D data structure
    i = np.resize(i, (y, x))

    img.setImage(np.flipud(np.rot90(i)))
    app.processEvents()

    if args.benchmark:
        framesDisplayed += 1
        if MAX_FRAMES > 0:
            if framesDisplayed > MAX_FRAMES:
                app.quit()

def main():
    global app, img, x, y, MAX_FRAMES
    global args

    parser = argparse.ArgumentParser(
            description='AreaDetector video example')

    parser.add_argument("ImagePV",
                        help="EPICS PVA image PV name, such as 13PG2:Pva1:Image")
    parser.add_argument('--benchmark', action='store_true',
                        help='measure framerate')
    parser.add_argument('--noAGC', action='store_true',
                        help='disable auto gain')
    parser.add_argument('--frames', action='store_true',
                        help='maximum number of frames (-1: unlimited)')

    args = parser.parse_args()

    app = QtGui.QApplication([])
    win = QtWidgets.QWidget()
    win.setWindowTitle('daqScope')
    layout = QtGui.QGridLayout()
    layout.setMargin(0)
    win.setLayout(layout)
    img = RawImageWidget(win)
    layout.addWidget(img, 0, 0, 0, 0)
    win.show()
    chan = pvaccess.Channel(args.ImagePV)

    x,y = chan.get('field()')['dimension']
    x = x['size']
    y = y['size']
    win.resize(x, y)

    chan.subscribe('update', update)
    chan.startMonitor()

    if args.benchmark:
        start = time.time()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        chan.stopMonitor()
        chan.unsubscribe('update')

    if args.benchmark:
        stop = time.time()
        print('Frames displayed: %d' % framesDisplayed)
        print('Elapsed time:     %.3f sec' % (stop-start))
        print('Frames per second: %.3f FPS' % (framesDisplayed/(stop-start)))


if __name__ == '__main__':
    main()
