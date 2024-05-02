/*
*! @title      Class to handle hardware monitoring
*! @file       HwMonitoring.h
*! @author     Romain Beaubois
*! @date       02 Nov 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **02 Nov 2022** : file creation (RB)
*/

#ifndef __HWMONITORING_H__
#define __HWMONITORING_H__

#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string>
#include <vector>
#include <algorithm>

#include "AxiLite.h"
#include "CustomPrint.h"
#include "hw_config_system.h"
#include "hw_config_com.h"
#include "hw_config_monitoring.h"
#include "hw_config_ionrates.h"
#include "hw_config_hhparam.h"
#include "reg_control.h"

using namespace std;

class HwMonitoring{
    private:
        AxiLite*    _axilite;
        uint32_t    _val_regw_sel_mon;
        uint32_t    _val_regw_control_mon;
        vector<uint16_t> _sel_mon_vmem;
        vector<uint16_t> _sel_mon_spike;
        vector<uint16_t> _sel_mon_dac;
        uint16_t    _nb_nrn;

    public:
        HwMonitoring(AxiLite* axilite, uint16_t nb_nrn);
        /* Functions to be replaced by monitor class in next version */
        int setVmemMonitoring(vector<uint16_t> sel_mon, uint32_t nb_packets_per_frame);
        int startVmemMonitoring();
        int stopVmemMonitoring();
        int monitorVmem();
        
        int setSpikeMonitoring(uint32_t nb_packets_per_frame);
        int startSpikeMonitoring();
        int stopSpikeMonitoring();
        
        int setWaveformMonitoring(vector<uint16_t> sel_mon);
        int startWaveformMonitoring();
        int stopWaveformMonitoring();
};

#endif