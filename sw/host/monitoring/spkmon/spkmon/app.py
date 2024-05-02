import zmq
import pyqtgraph as pg

from PyQt5.QtWidgets    import QMainWindow, QFileDialog
from PyQt5.QtCore       import pyqtSignal, QThread

from monitoring.spkmon.spkmon.ui.main_window_ui import Ui_MainWindow
from monitoring.spkmon.spkmon.settings.defaults  import *
from monitoring.spkmon.spkmon.settings.config    import *

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.zmq_thread = ZmqThread()

        self.last_tstamp            = 0
        self.window_width_raster_ms = DEFAULT_WINDOW_WIDTH_MS
        self.target_connection_ip   = DEFAULT_TARGET_IP_ADDR
        self.raster_save_fpath      = DEFAULT_SAVE_PATH
        self.raster_save_file       = None
        self.raster_save            = False

        self.sbox_raster_window_width.setRange(0, 30)
        self.sbox_raster_window_width.setValue(int(1e-3*self.window_width_raster_ms))

        self.line_connect_target_ip.setText(self.target_connection_ip)
        self.line_save_path.setText(self.raster_save_fpath)
        
        self.connectSignalsSlots()
        self.initRasterPlot()
    
    def connectSignalsSlots(self):
        self.btn_connect_target.clicked.connect(self.startZmqThread)
        self.btn_raster_clear.clicked.connect(self.clearRasterPlot)
        self.btn_set_save_path.clicked.connect(self.setRasterSavePath)
        self.btn_save_raster.clicked.connect(self.handleRasterSaveFile)
        self.sbox_raster_window_width.valueChanged.connect(self.updateRasterWindowWidth)
        self.zmq_thread.rx_data_available.connect(self.update_raster)

    def startZmqThread(self):
        self.target_connection_ip = self.line_connect_target_ip.text()
        self.zmq_thread.connect(self.target_connection_ip)
        self.zmq_thread.start()

    def initRasterPlot(self):
        pg.setConfigOption('background',  (0,0,0,0))
        pg.setConfigOption('foreground', 'k')

        self.scatter = pg.ScatterPlotItem()
        self.scatter.size = 3
        self.scatter.pen = pg.mkPen(width=3, color='k')
        
        self.plot_widget_raster.addItem(self.scatter)
        self.plot_widget_raster.setBackground('w')
        self.plot_widget_raster.setYRange(-1, NB_NRN, padding=0)
        self.plot_widget_raster.setXRange(0, self.window_width_raster_ms, padding=0)
        self.plot_widget_raster.setLabel("bottom", "Time (ms)")
        self.plot_widget_raster.setLabel("left", "Neuron (id)")

    def clearRasterPlot(self):
        self.scatter.clear()
        self.last_tstamp = 0
        self.plot_widget_raster.setYRange(-1, NB_NRN, padding=0)
        self.plot_widget_raster.setXRange(0, self.window_width_raster_ms, padding=0)

    def setRasterSavePath(self):
        dialog      = QFileDialog(self)
        fsave_path  = dialog.getSaveFileName(dialog, "Set file path for raster plot saving", ".csv")
        self.raster_save_fpath  = fsave_path[0]
        self.line_save_path.setText(self.raster_save_fpath)

    def handleRasterSaveFile(self):
        if self.btn_save_raster.isChecked() == -1:
            self.raster_save = False
            self.raster_save_file.close()
        elif self.btn_save_raster.isChecked():
            self.raster_save_file   = open(self.raster_save_fpath, "w")
            self.raster_save = True
    
    def updateRasterWindowWidth(self):
        self.window_width_raster_ms = self.sbox_raster_window_width.value()*1e3
        self.plot_widget_raster.setXRange(self.last_tstamp, self.last_tstamp+self.window_width_raster_ms, padding=0)

    def update_raster(self, spk_tab):
        """"""
        x = []
        y = []

        # # <DEBUG> Burst
        # import numpy as np
        # THRESH_NB_SPK   = 15
        # THRESH_NB_NEUR  = 64
        # spk_cnt         = np.zeros(NB_NRN, dtype=np.uint32)
        # burst_cnt       = 0
        # # </DEBUG> Burst

        for z in range(NB_FRAME_PER_BUFFER):
            nid     = 0
            tstamp  = int.from_bytes(spk_tab[ (z*SIZE_BYTE_FRAME + 0)
                                            : (z*SIZE_BYTE_FRAME + DATAWIDTH_BYTE_FRAME)], 
                                            "little")

            for i in range(NB_SPK_DATA_PER_FRAME): # nb of regs
                reg = int.from_bytes(spk_tab[ z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + 0
                                            : z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + DATAWIDTH_BYTE_FRAME], 
                                            "little")
                for k in range(DATAWIDTH_BIT_FRAME): # nb of nrn per data
                    if reg & (1<<k) != 0:
                        x.append(tstamp)
                        y.append(nid)
                        # spk_cnt[nid] += 1 # # <DEBUG> Burst
                    nid += 1
        self.scatter.addPoints(x, y)

        # # # <DEBUG> Burst
        # for nid in range(NB_NRN):
        #     if spk_cnt[nid] > THRESH_NB_SPK:
        #         burst_cnt += 1

        # if burst_cnt > THRESH_NB_NEUR:
        #     print("Burst")

        # spk_cnt.fill(0)
        # burst_cnt = 0
        # # </DEBUG> Burst

        if self.raster_save:
            for i in range(len(x)):
                self.raster_save_file.write(str(x[i]) + ";" + str(y[i]) + "\n")

        if (tstamp - self.last_tstamp) > self.window_width_raster_ms:
            self.scatter.clear()
            x.clear()
            y.clear()
            self.last_tstamp = tstamp
            self.plot_widget_raster.setXRange(tstamp, tstamp+self.window_width_raster_ms, padding=0)

class ZmqThread(QThread):
    rx_data_available  = pyqtSignal(bytes)

    def __init__(self):
        """Initialize"""
        super().__init__()
        self.target_ip = ""
        self.context = zmq.Context()
    
    def connect(self, target_connection_ip):
        self.consumer_receiver = self.context.socket(zmq.PULL)
        self.consumer_receiver.connect(target_connection_ip)
        self.target_ip = target_connection_ip

    def run(self):
        """Run serial port reading in a thread"""
        print("Start ZeroMQ thread listening on {} ...".format(self.target_ip))
        while True:
            data = self.consumer_receiver.recv(SIZE_BYTE_FRAME)
            self.rx_data_available.emit(data)