# -*- coding: utf-8 -*-
# @title      Main
# @file       main.py
# @author     Romain Beaubois
# @date       20 Feb 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief
# 
# @details
# > **20 Feb 2023** : file creation (RB)

# Imports #################################################################
# UTILITIES
import sys

# Qt5
from PyQt5.QtWidgets import (QApplication)

# Custom Qt5 GUI
from monitoring.spkmon.spkmon.app import *

# Launch application #################################################################
def main():
    app = QApplication(sys.argv)
    win = MainWindow()

    app.setStyle('Fusion')
    win.show()
    sys.exit(app.exec())