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

NB_NRN              = 1024
NB_REGS_SPK         = int(NB_NRN/32)
NB_TAB_PER_FRAME    = 100
# NB_TAB_PER_FRAME    = 256
NB_BYTES_PER_REGS   = 4
BYTE_SIZE_FRAME     = (NB_REGS_SPK+1)*NB_BYTES_PER_REGS
WINDOW_WIDTH_MS     = 10e3

# IP_ADDR             = "tcp://127.0.0.1:5557"
IP_ADDR             = "tcp://192.168.137.124:5557"    #kria home
# IP_ADDR             = "tcp://192.168.137.13:5557"    #kria
# IP_ADDR             = "tcp://192.168.137.104:5557"        #zcu102

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
        
        self.last_tstamp = 0
        self.graphWidget.setYRange(-1, NB_NRN, padding=0)
        self.graphWidget.setXRange(0, WINDOW_WIDTH_MS, padding=0)

        self.zmq_thread = ZmqThread()
        self.zmq_thread.rx_data_available.connect(self.update_raster)
        self.zmq_thread.start()
    
    def update_raster(self, spk_tab):
        """"""
        x = []
        y = []

        for z in range(NB_TAB_PER_FRAME):
            nid     = 0
            tstamp  = int.from_bytes(spk_tab[ (z*BYTE_SIZE_FRAME + 0)
                                            : (z*BYTE_SIZE_FRAME + NB_BYTES_PER_REGS)], 
                                            "little")
            for i in range(NB_REGS_SPK): # nb of regs
                reg = int.from_bytes(spk_tab[ z*(BYTE_SIZE_FRAME) + (i+1)*NB_BYTES_PER_REGS + 0
                                            : z*(BYTE_SIZE_FRAME) + (i+1)*NB_BYTES_PER_REGS + NB_BYTES_PER_REGS], 
                                            "little")
                for k in range(32): # nb of nrn per reg
                    if reg & (1<<k) != 0:
                        x.append(tstamp)
                        y.append(nid)
                    nid += 1
        scatter.addPoints(x, y)

        if (tstamp - self.last_tstamp) > WINDOW_WIDTH_MS:
            scatter.clear()
            x.clear()
            y.clear()
            self.last_tstamp = tstamp
            self.graphWidget.setXRange(tstamp, tstamp+WINDOW_WIDTH_MS, padding=0)

class ZmqThread(QThread):
    rx_data_available  = pyqtSignal(bytes)

    def __init__(self):
        """Initialize"""
        super().__init__()
        print("Start consumer ...")
        self.context = zmq.Context()
        self.consumer_receiver = self.context.socket(zmq.PULL)
        self.consumer_receiver.connect(IP_ADDR)

    def run(self):
        """Run serial port reading in a thread"""
        while True:
            data = self.consumer_receiver.recv()
            self.rx_data_available.emit(data)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())