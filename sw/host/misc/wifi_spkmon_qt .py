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

FRAME_SIZE          = int(NB_REGS_SPK+NB_REGS_TSTAMP)
FRAME_BYTE_SIZE     = int(FRAME_SIZE*DATAWIDTH_BYTE)
NB_FRAME_PER_BUFFER = 128
BUFFER_BYTE_SIZE    = int(NB_FRAME_PER_BUFFER*FRAME_BYTE_SIZE)

# IP_ADDR             = "10.42.0.205"    # esp32
# PORT                = 53

IP_ADDR             = "192.168.4.1"    # esp32
PORT                = 5032

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
            tstamp  = int.from_bytes(spk_tab[ int((z*FRAME_BYTE_SIZE + 0))
                                            : int((z*FRAME_BYTE_SIZE + DATAWIDTH_BYTE))],
                                            "little")
            print(tstamp)
            for i in range(NB_REGS_SPK): # nb of regs
                reg = int.from_bytes(spk_tab[ int(z*(FRAME_BYTE_SIZE) + (i+1)*DATAWIDTH_BYTE + 0)
                                            : int(z*(FRAME_BYTE_SIZE) + (i+1)*DATAWIDTH_BYTE + DATAWIDTH_BYTE)], 
                                            "little")
                for k in range(32): # nb of nrn per reg
                    if reg & (1<<k) != 0:
                        x.append(tstamp)
                        y.append(nid)
                    nid += 1
        scatter.addPoints(x, y)
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.bind((IP_ADDR, PORT))  
        self.sock.listen(5)

    def run(self):
        """Run serial port reading in a thread"""
        while True:
            connection, address = self.sock.accept()
            buf = connection.recv(BUFFER_BYTE_SIZE)
            print("recv buf: " + str(len(buf)) + " B")
            self.rx_data_available.emit(buf)
            connection.close()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())