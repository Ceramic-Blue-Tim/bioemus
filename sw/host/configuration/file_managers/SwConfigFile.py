# -*- coding: utf-8 -*-
# @title      Software configuration file
# @file       SwConfigFile.py
# @author     Romain Beaubois
# @date       01 May 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Script to generate software configuration file for SNN HH
# 
# @details 
# > **01 May 2023** : file creation (RB)

import os
import json
import jsbeautifier
from math import ceil

class SwConfigFile:
    parameters = {
        "fpath_hwconfig"              : "/home/ubuntu/software/app/snn_hh/config/hwconfig.txt",
        "emulation_time_s"            : 10,
        "sel_nrn_vmem_dac"            : [0, 1, 2, 3, 4, 5, 6, 7],
        "sel_nrn_vmem_dma"            : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        "save_local_spikes"           : False,
        "save_local_vmem"             : False,
        "save_path"                   : "/home/ubuntu/data/",
        "en_zmq_spikes"               : False,
        "en_zmq_vmem"                 : False,
        "en_zmq_stim"                 : False,
        "en_wifi_spikes"              : False,
        "ip_zmq_spikes"               : "tcp://*:5557",
        "ip_zmq_vmem"                 : "tcp://*:5558",
        "ip_zmq_stim"                 : "tcp://192.168.137.1:5559",
        "bin_fmt_save_spikes"         : True,
        "bin_fmt_save_vmem"           : True,
        "bin_fmt_send_spikes"         : True,
        "bin_fmt_send_vmem"           : True,
        "nb_tstamp_per_spk_transfer"  : 100,
        "nb_tstep_per_vmem_transfer"  : 96,
        "en_stim"                     : False,
        "stim_delay_ms"               : 1,
        "stim_duration_ms"            : 1
    }

    def __init__(self) -> None:
        pass

    def write(self, fpath):
        emulation_time_s_floating = self.parameters["emulation_time_s"]
        self.parameters["emulation_time_s"] = ceil(emulation_time_s_floating)

        options             = jsbeautifier.default_options()
        options.indent_size = 4
        json_obj            = jsbeautifier.beautify(json.dumps(self.parameters), options)

        with open(fpath, "w") as fout:
            fout.write(json_obj)
        print("Software configuration file saved at: " + fpath)

        self.parameters["emulation_time_s"] = emulation_time_s_floating
