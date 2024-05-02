import time
import zmq
import random
import matplotlib.pyplot as plt
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QThread
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os
from tqdm import tqdm

NB_NRN      = 512
NB_REGS_SPK = 16
FRAME_SIZE  = NB_REGS_SPK + 1 # +1 for time stamp

pg.setConfigOption('background',  (0,0,0,0))
pg.setConfigOption('foreground', 'k')
scatter = pg.ScatterPlotItem()
scatter.size = 3
scatter.pen = pg.mkPen(width=3, color='k')

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.addItem(scatter)
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.update_raster()
    
    def update_raster(self):
        """"""
        x = []
        y = []

        dtype       = np.dtype(np.uint32)
        fpath       = "C:/PhD/Projects/SNN-HH/fpga/zynqmp/software/app/spkmon/rx_chan_11.txt"
        nb_samples  = int(os.path.getsize(fpath)/dtype.itemsize)
        data        = np.fromfile(fpath, dtype=dtype, count=nb_samples)

        for i in tqdm(range(int(len(data)/FRAME_SIZE))):
            for j in range(FRAME_SIZE):
                nid     = 0
                tstamp  = data[i*FRAME_SIZE]
                
                for z in range(NB_REGS_SPK): # nb of regs
                    reg = data[i*FRAME_SIZE + 1 + z]

                    for k in range(32): # nb of nrn per reg
                        if reg & (1<<k) != 0:
                            x.append(tstamp)
                            y.append(nid)
                        nid += 1

        scatter.addPoints(x, y)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())