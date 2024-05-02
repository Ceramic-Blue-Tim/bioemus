# Utilities
import os, sys, time, math
import pyqtgraph as pg
import numpy as np
import zmq

# Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSignal

DEFAULT_NB_CHANNELS         = 16
DEFAULT_NB_DT_PER_TRANSFER  = 190
DEFAULT_TARGET_IP           = "tcp://192.168.137.16:5558"
DEFAULT_WINDOW_SIZE_S       = 1
DEFAULT_REFRESH_TIME_S      = 0.1

_DT_MS = 2**-5

# Main window gui actions #################################################################
class ZmqThread(QThread):
    """Data receiving over ZeroMQ"""
    sig_rx_data_available  = pyqtSignal(bytes)

    def __init__(self, target_ip, nb_channels, nb_dt_per_transfer):
        """Initialize"""
        super().__init__()
        
        # Initialize parameters
        self.nb_channels = nb_channels
        self.nb_dt_per_transfer = nb_dt_per_transfer

        # Initialiaze ZeroMQ
        self.target_ip = target_ip
        self.context = zmq.Context()
        self.consumer_receiver = self.context.socket(zmq.PULL)
    
    def connect(self):
        """Connect"""
        self.consumer_receiver.connect(self.target_ip)

    def run(self):
        """Run serial port reading in a thread"""
        self.connect()
        print(f"Start ZeroMQ thread listening on {self.target_ip} ...")
        while True:
            data = self.consumer_receiver.recv((self.nb_channels+1)*self.nb_dt_per_transfer*np.dtype(np.float32).itemsize)
            self.sig_rx_data_available.emit(data)

class MonitorThread(QThread):
    """Monitoring thread"""

    def __init__(self, sig_rx_data,
                 nb_channels,
                 nb_dt_per_transfer,
                 window_size_s,
                 refresh_time_s):
        super().__init__()

        # Initialize window
        self.gwin = pg.GraphicsLayoutWidget()
        self.gwin.setWindowTitle('PyQtGraph example: Update Plot with QThread')
        self.gwin.resize(800, 600)
        self.gwin.show()

        # Set parameters
        self.nb_channels = nb_channels
        self.nb_dt_per_transfer = nb_dt_per_transfer
        self.window_size_ms = int(window_size_s*1e3/(_DT_MS))
        self.refresh_interval_ms = int(refresh_time_s*1e3)

        # Setup plots
        self.pltwdg = []
        self.plots = []
        self.nb_plots = self.nb_channels
        self.max_row = round(math.sqrt(self.nb_plots))
        self.max_col = math.ceil(math.sqrt(self.nb_plots))

        for row_id in range(self.max_row):
            for col_id in range(self.max_col):
                index = row_id*self.max_col+col_id
                self.pltwdg.append(self.gwin.addPlot(row=row_id, col=col_id, title=f"{index+1}"))
                self.plots.append(self.pltwdg[-1].plot(name=f"{index+1}"))
        
        self.stop_requested = False
        self.receiving = False

        self.x = np.arange(self.window_size_ms)
        self.y = np.zeros((self.nb_channels, self.window_size_ms))
        self.offset = 0

        self.timer_refresh = QTimer()

        sig_rx_data.connect(self.update_data)
        self.timer_refresh.timeout.connect(self.update_display)

        self.timer_refresh.start(self.refresh_interval_ms)

        self.plots[0].setData(self.x, self.y[0])

    def update_data(self, rx_data_bytes):
        """Update data"""
        self.receiving = True

        rx_data  = np.frombuffer(rx_data_bytes, dtype=np.float32)
        rx_data  = rx_data.reshape(self.nb_dt_per_transfer, self.nb_channels+1)

        for i in range(1,rx_data.shape[1]):
            for j, samples in enumerate(rx_data[:, i]):
                self.y[i-1][self.offset+j] = samples

        self.offset += self.nb_dt_per_transfer

        if self.offset > self.window_size_ms-self.nb_dt_per_transfer-1:
            self.offset = 0

    def update_display(self):
        """Update GUI"""
        if self.receiving:
            for plot, y_ch in zip(self.plots, self.y):
                plot.setData(self.x, y_ch)

    def run(self):
        """Run thread"""
        while not self.stop_requested:
            time.sleep(0.5)

    def stop(self):
        """Stop thread"""
        self.stop_requested = True

def waves_mon(target_ip=DEFAULT_TARGET_IP, 
         nb_channels=DEFAULT_NB_CHANNELS, 
         nb_dt_per_transfer=DEFAULT_NB_DT_PER_TRANSFER, 
         window_size_s=DEFAULT_WINDOW_SIZE_S,
         refresh_time_s=DEFAULT_REFRESH_TIME_S):
    """Main function"""
    app = QApplication(sys.argv)
    zmq_thread = ZmqThread(target_ip,
                           nb_channels,
                           nb_dt_per_transfer)
    mon_thread = MonitorThread(zmq_thread.sig_rx_data_available,
                               nb_channels,
                               nb_dt_per_transfer,
                               window_size_s,
                               refresh_time_s)

    zmq_thread.start()
    mon_thread.start()

    # Theme
    app.setStyle('Fusion')
    sys.exit(app.exec())

waves_mon()