import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QThread
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import socket,os

NB_NRN              = 512
DATAWIDTH_BIT       = 32
DATAWIDTH_BYTE      = int(DATAWIDTH_BIT/8)
NB_REGS_SPK         = int(512/(DATAWIDTH_BIT))
NB_REGS_TSTAMP      = 1

SIZE_FRAME          = NB_REGS_SPK+NB_REGS_TSTAMP
BYTE_SIZE_FRAME     = SIZE_FRAME*DATAWIDTH_BYTE
NB_FRAME_PER_BUFFER = 100

IP_ADDR             = "192.168.4.2"    # esp32
PORT                = 4444
MAX_CLIENTS         = 1

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

        self.tcp_thread = RxThread()
        self.tcp_thread.rx_data_available.connect(self.update_raster)
        self.tcp_thread.start()
    
    def update_raster(self, spk_tab):
        """"""
        x = []
        y = []

        for z in range(NB_FRAME_PER_BUFFER):
            nid     = 0
            tstamp  = int.from_bytes(spk_tab[ (z*BYTE_SIZE_FRAME + 0)
                                            : (z*BYTE_SIZE_FRAME + DATAWIDTH_BYTE)], 
                                            "little")
            # print(tstamp)
            for i in range(NB_REGS_SPK): # nb of regs
                reg = int.from_bytes(spk_tab[ z*(BYTE_SIZE_FRAME) + (i+1)*DATAWIDTH_BYTE + 0
                                            : z*(BYTE_SIZE_FRAME) + (i+1)*DATAWIDTH_BYTE + DATAWIDTH_BYTE], 
                                            "little")
                for k in range(32): # nb of nrn per reg
                    if reg & (1<<k) != 0:
                        x.append(tstamp)
                        y.append(nid)
                    nid += 1
        scatter.addPoints(x, y)
        if(tstamp != self.last_tstamp+NB_FRAME_PER_BUFFER):
            print("pute")
        self.last_tstamp = tstamp

        # if tstamp - self.last_tstamp > 1000:
        #     scatter.clear()
        #     x.clear()
        #     y.clear()

class RxThread(QThread):
    rx_data_available  = pyqtSignal(bytes)

    def __init__(self):
        """Initialize"""
        super().__init__()
        print("Start receiver ...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP_ADDR, PORT))

    def run(self):
        """Run serial port reading in a thread"""
        while True:
            [buf, _] = self.sock.recvfrom(int(NB_FRAME_PER_BUFFER*BYTE_SIZE_FRAME))
            self.rx_data_available.emit(buf)
            # connection.close()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())