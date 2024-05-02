import zmq
import pyqtgraph as pg
import struct
import numpy as np

from PyQt5.QtWidgets    import QMainWindow, QFileDialog
from PyQt5.QtCore       import pyqtSignal, QThread

from monitoring.vmon.vmon.ui.main_window_ui  import Ui_MainWindow
from monitoring.vmon.vmon.settings.defaults  import *
from monitoring.vmon.vmon.settings.config    import *

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.zmq_thread = ZmqThread()

        self.tstamp                 = 0
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

        self.plot_widget_raster.setBackground('w')
        self.plot_widget_raster.setYRange(-80, 60, padding=0)
        self.plot_widget_raster.setXRange(0, self.window_width_raster_ms, padding=0)
        self.plot_widget_raster.setLabel("bottom", "Time (ms)")
        self.plot_widget_raster.setLabel("left", "Neuron (id)")


    def clearRasterPlot(self):
        self.scatter.clear()
        self.last_tstamp = 0
        self.plot_widget_raster.setYRange(-80, 60, padding=0)
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
        v_i         = np.zeros([NB_FRAME_PER_BUFFER, NB_NRN], dtype=np.float32)
        tstamp_list = []
        v_list      = np.zeros(NB_FRAME_PER_BUFFER)

        for z in range(NB_FRAME_PER_BUFFER):
            # self.tstamp += 1
            self.tstamp += 2**-5 # dt
            # self.tstamp  = int.from_bytes(spk_tab[ (z*SIZE_BYTE_FRAME + 0)
            #                                      : (z*SIZE_BYTE_FRAME + DATAWIDTH_BYTE_FRAME)], 
            #                                      "little")
            
            # for i in range(NB_NRN): # nb of regs
            #     # v[i] = struct.unpack("f", spk_tab[z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + 0
            #     #                                 : z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + DATAWIDTH_BYTE_FRAME])
            #     v_i[i] = np.frombuffer(spk_tab[z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + 0
            #                                  : z*(SIZE_BYTE_FRAME) + (i+1)*DATAWIDTH_BYTE_FRAME + DATAWIDTH_BYTE_FRAME],
            #                                  dtype=np.float32)
            #     tstamp_list.append(self.tstamp)
            # v_list.append(v_i)

            tstamp_list.append(self.tstamp)
            v = np.frombuffer(spk_tab[z*(SIZE_BYTE_FRAME) + (3+1)*DATAWIDTH_BYTE_FRAME + 0
                                    : z*(SIZE_BYTE_FRAME) + (3+1)*DATAWIDTH_BYTE_FRAME + DATAWIDTH_BYTE_FRAME],
                                    dtype=np.float32)
            v_list[z] = v
            
        self.plot_widget_raster.plot(tstamp_list, v_list)
        v_list.clear()
        tstamp_list.clear()

        if (self.tstamp - self.last_tstamp) > (32*self.window_width_raster_ms):
            self.plot_widget_raster.clear()
            self.last_tstamp = self.tstamp
            self.plot_widget_raster.setXRange(self.tstamp, self.tstamp+self.window_width_raster_ms, padding=0)

        ### Save
        # if self.raster_save:
        #     for i in range(len(x)):
        #         self.raster_save_file.write(str(x[i]) + ";" + str(y[i]) + "\n")

        ### Clear
        # if (self.tstamp - self.last_tstamp) > self.window_width_raster_ms:
        #     self.scatter.clear()
        #     self.last_tstamp = self.tstamp
        #     self.plot_widget_raster.setXRange(self.tstamp, self.tstamp+self.window_width_raster_ms, padding=0)

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
            data = self.consumer_receiver.recv()
            self.rx_data_available.emit(data)