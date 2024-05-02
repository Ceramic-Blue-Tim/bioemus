# -*- coding: utf-8 -*-
# @title      Emulate configuration
# @file       SnnEmulator.py
# @author     Romain Beaubois
# @date       23 Oct 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief
# 
# @details
# > **23 Oct 2023** : file creation (RB)

from configuration.file_managers.HwConfigFile import *
from configuration.file_managers.SwConfigFile import *
from emulation.hh_snn.SnnEmulator import *

def emulate_config(hwconfig:HwConfigFile, swconfig:SwConfigFile, nlist, fpga_emu, store_context:bool, dtype):
    snn_emu = SnnEmulator(hwconfig, swconfig, store_context, dtype)
    
    if fpga_emu:
        print("Software emulation using FPGA equations")
    else:
        print("Software emulation using exact equations")

    snn_emu.run(nlist, fpga_emu)
    return snn_emu