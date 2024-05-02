# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1376, 740)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_37 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_37.setObjectName("gridLayout_37")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gbox_logs = QtWidgets.QGroupBox(self.centralwidget)
        self.gbox_logs.setObjectName("gbox_logs")
        self.gridLayout = QtWidgets.QGridLayout(self.gbox_logs)
        self.gridLayout.setObjectName("gridLayout")
        self.line_error_logs = QtWidgets.QLineEdit(self.gbox_logs)
        self.line_error_logs.setReadOnly(True)
        self.line_error_logs.setObjectName("line_error_logs")
        self.gridLayout.addWidget(self.line_error_logs, 0, 1, 1, 1)
        self.gridLayout_3.addWidget(self.gbox_logs, 0, 2, 1, 1)
        self.gbox_raster_control = QtWidgets.QGroupBox(self.centralwidget)
        self.gbox_raster_control.setObjectName("gbox_raster_control")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gbox_raster_control)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_raster_window_width = QtWidgets.QLabel(self.gbox_raster_control)
        self.label_raster_window_width.setObjectName("label_raster_window_width")
        self.gridLayout_4.addWidget(self.label_raster_window_width, 0, 0, 1, 1)
        self.btn_set_save_path = QtWidgets.QPushButton(self.gbox_raster_control)
        self.btn_set_save_path.setObjectName("btn_set_save_path")
        self.gridLayout_4.addWidget(self.btn_set_save_path, 0, 4, 1, 1)
        self.sbox_raster_window_width = QtWidgets.QSpinBox(self.gbox_raster_control)
        self.sbox_raster_window_width.setObjectName("sbox_raster_window_width")
        self.gridLayout_4.addWidget(self.sbox_raster_window_width, 0, 1, 1, 1)
        self.line_save_path = QtWidgets.QLineEdit(self.gbox_raster_control)
        self.line_save_path.setEnabled(True)
        self.line_save_path.setReadOnly(True)
        self.line_save_path.setObjectName("line_save_path")
        self.gridLayout_4.addWidget(self.line_save_path, 0, 3, 1, 1)
        self.btn_save_raster = QtWidgets.QRadioButton(self.gbox_raster_control)
        self.btn_save_raster.setObjectName("btn_save_raster")
        self.gridLayout_4.addWidget(self.btn_save_raster, 0, 2, 1, 1)
        self.btn_raster_clear = QtWidgets.QPushButton(self.gbox_raster_control)
        self.btn_raster_clear.setObjectName("btn_raster_clear")
        self.gridLayout_4.addWidget(self.btn_raster_clear, 0, 5, 1, 1)
        self.gridLayout_3.addWidget(self.gbox_raster_control, 0, 1, 1, 1)
        self.gbox_target_communication = QtWidgets.QGroupBox(self.centralwidget)
        self.gbox_target_communication.setObjectName("gbox_target_communication")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gbox_target_communication)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_connect_target_ip = QtWidgets.QLabel(self.gbox_target_communication)
        self.label_connect_target_ip.setObjectName("label_connect_target_ip")
        self.gridLayout_2.addWidget(self.label_connect_target_ip, 0, 0, 1, 1)
        self.line_connect_target_ip = QtWidgets.QLineEdit(self.gbox_target_communication)
        self.line_connect_target_ip.setObjectName("line_connect_target_ip")
        self.gridLayout_2.addWidget(self.line_connect_target_ip, 0, 1, 1, 1)
        self.btn_connect_target = QtWidgets.QPushButton(self.gbox_target_communication)
        self.btn_connect_target.setObjectName("btn_connect_target")
        self.gridLayout_2.addWidget(self.btn_connect_target, 0, 2, 1, 1)
        self.gridLayout_3.addWidget(self.gbox_target_communication, 0, 0, 1, 1)
        self.gridLayout_37.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.main_tab_widget = QtWidgets.QTabWidget(self.centralwidget)
        self.main_tab_widget.setObjectName("main_tab_widget")
        self.tab_raster_plot = QtWidgets.QWidget()
        self.tab_raster_plot.setObjectName("tab_raster_plot")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_raster_plot)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.grid_raster_plot_3 = QtWidgets.QGridLayout()
        self.grid_raster_plot_3.setObjectName("grid_raster_plot_3")
        self.plot_widget_raster = PlotWidget(self.tab_raster_plot)
        self.plot_widget_raster.setObjectName("plot_widget_raster")
        self.grid_raster_plot_3.addWidget(self.plot_widget_raster, 0, 0, 1, 2)
        self.gridLayout_5.addLayout(self.grid_raster_plot_3, 0, 0, 1, 1)
        self.main_tab_widget.addTab(self.tab_raster_plot, "")
        self.gridLayout_37.addWidget(self.main_tab_widget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1376, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.main_tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.gbox_logs.setTitle(_translate("MainWindow", "Logs"))
        self.gbox_raster_control.setTitle(_translate("MainWindow", "Raster control"))
        self.label_raster_window_width.setText(_translate("MainWindow", "Window width (s)"))
        self.btn_set_save_path.setText(_translate("MainWindow", "..."))
        self.btn_save_raster.setText(_translate("MainWindow", "Save"))
        self.btn_raster_clear.setText(_translate("MainWindow", "Clear"))
        self.gbox_target_communication.setTitle(_translate("MainWindow", "Target communication"))
        self.label_connect_target_ip.setText(_translate("MainWindow", "IP Address:Port"))
        self.btn_connect_target.setText(_translate("MainWindow", "Connect"))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.tab_raster_plot), _translate("MainWindow", "Raster plot"))
from pyqtgraph import PlotWidget
