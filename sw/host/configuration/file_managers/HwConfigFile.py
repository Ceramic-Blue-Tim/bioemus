# -*- coding: utf-8 -*-
# @title      Hardware Configuration File handling class
# @file       HwConfigFile.py
# @author     Romain Beaubois
# @date       19 Oct 2022
# @copyright
# SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Handling of the hardware config file
#   * HH parameters
#   * rates tables for m and h ionic channels states
# 
# @details 
# > **29 Jul 2022** : file creation (RB)
# > **19 Oct 2022** : remove L diagonal and add node area (RB)
# > **05 Dec 2022** : adapt file from simoton to snn_hh (RB)

import os
import numpy as np
from datetime import datetime

COM_SEP     = '#'
KEY_SEP     = '='
VAL_SEP     = ',' # has to be python default list separator
COL_SEP     = ';'

class HwConfigFile :
    def __init__(self, sw_ver, NB_NEURONS):
        """Initialize configuration file variables"""
        # Config file info
        self.sw_ver     = sw_ver

        # Network parameters
        self.dt         = 0
        self.nb_nrn     = NB_NEURONS

        # HH parameters
        self.nb_hhparam = 0
        self.HH_param   = []    # Hodgkin-Huxley model parameters (hhparam; nrn)

        # Synapses parameters
        self.psyn               = []    # Synaptic parameters (psyn)

        # Rate tables of ionic channels
        self.depth_ionrate      = 0
        self.nb_ionrate         = 0
        self.m_rates1           = []    # Rates table for ionic channel state m (r; ionchan)
        self.m_rates2           = []    # Rates table for ionic channel state m (r; ionchan)
        self.h_rates1           = []    # Rates table for ionic channel state h (r; ionchan)
        self.h_rates2           = []    # Rates table for ionic channel state h (r; ionchan)

        # Synaptic rates tables
        self.depth_synrate      = 0
        self.synrates           = []    # Synaptic rates tables (r_Bv; r_Tv, r_sn_gabab)
        

        # Synaptic configuration
        self.tsyn               = []    # Synaptic type
        self.wsyn               = []    # Synaptic weight

    
    def write(self, fpath):
        """Write configuration file

                hhparam (gion, eion)
            N0  0.1,0.2,0.3,0.4
            N1  0.1,0.2,0.3,0.4
            
                    m_rates1    ; m_rates2  ; h_rates1  ; h_rates2
            I0_A0   0.1         ; 0.2       ; 0.3       ; 0.4
            I0_A1   0.1         ; 0.2       ; 0.3       ; 0.4
            ...
            I1_A0   0.1         ; 0.2
        """
        with open(fpath, "w") as f:
            # Header
            f.write(COM_SEP + "SW_VERSION" + KEY_SEP + self.sw_ver + '\n')
            f.write(COM_SEP + "DATE" + KEY_SEP + str(datetime.now()) + '\n')

            # Global parameters (fetch from config)
            # f.write("NB_NRN" + KEY_SEP + str(self.nb_nrn) + '\n')
            # f.write("NB_HHPARAM" + KEY_SEP + str(self.nb_hhparam) + '\n')
            # f.write("DEPTH_IONRATE" + KEY_SEP + str(self.depth_ionrate) + '\n')
            # f.write("NB_IONRATE" + KEY_SEP + str(self.nb_ionrate) + '\n')
            # f.write("DEPTH_SYNRATE" + KEY_SEP + str(self.depth_synrate) + '\n')

            # HH parameters
            for nrn in range(self.nb_nrn):
                f.write("HHparam_N{}".format(nrn) + KEY_SEP + VAL_SEP.join(map(self.__formatFloat, self.HH_param[nrn][:])) + '\n')

            # Synapses parameters
            f.write("psyn" + KEY_SEP + VAL_SEP.join(map(self.__formatFloat_exp, self.psyn)) + '\n')

            # m and h table rates
            for ionch in range(self.nb_ionrate):
                for addr in range(self.depth_ionrate):
                    str_ir = "ionrates_I{}A{}".format(ionch, addr) + KEY_SEP
                    str_ir += self.__formatFloat(self.m_rates1[ionch][addr]) + COL_SEP
                    str_ir += self.__formatFloat(self.m_rates2[ionch][addr]) + COL_SEP
                    str_ir += self.__formatFloat(self.h_rates1[ionch][addr]) + COL_SEP
                    str_ir += self.__formatFloat(self.h_rates2[ionch][addr]) + '\n'
                    f.write(str_ir)

            # synrates tables
            for addr in range(self.depth_synrate):
                str_ir = "synrates_A{}".format(addr) + KEY_SEP
                str_ir += self.__formatFloat(self.synrates[0][addr]) + COL_SEP # Bv
                str_ir += self.__formatFloat(self.synrates[1][addr]) + COL_SEP # Bv
                str_ir += self.__formatFloat(self.synrates[2][addr]) + '\n'    # Tv
                f.write(str_ir)
            
            # synaptic configuration
            for nrn in range(self.nb_nrn):
                f.write("N{}".format(nrn) + KEY_SEP + VAL_SEP.join(str(tsyn) + '$'+ str(wsyn) for tsyn,wsyn in zip(self.tsyn[nrn][:], self.wsyn[nrn][:])) + '\n')

            print("Hardware configuration file saved at: " + fpath)


    def __formatFloat(self, val:float):
        if val == 0.0 or val == 1.0:
            return str(round(val,1))
        else:
            return "{:e}".format(val)

    def __formatFloat_exp(self, val:float):
        vfp = np.float32(val)
        return "{:e}".format(vfp)