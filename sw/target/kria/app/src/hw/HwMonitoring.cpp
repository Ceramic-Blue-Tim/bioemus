/*
*! @title      Class to handle hardware monitoring
*! @file       HwMonitoring.cpp
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

#include "HwMonitoring.h"
#include <iostream>
#include <fstream>

/***************************************************************************
 * Constructor
 * 
 * @param fpath Path to configuration file
 * @return HwMonitoring
****************************************************************************/
HwMonitoring::HwMonitoring(AxiLite *axilite, uint16_t nb_nrn){
    _axilite                = axilite;
    _nb_nrn                 = nb_nrn;
    _val_regw_sel_mon       = 0;
    _val_regw_control_mon   = 0;
}

/***************************************************************************
 * Set membrane voltage monitoring selection
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::setVmemMonitoring(vector<uint16_t> sel_mon, uint32_t nb_packets_per_frame){
    int r;

    // Setup number of packets per frame
    if (nb_packets_per_frame > MAX_NB_PACKETS_MON_VMEM_DMA)
        nb_packets_per_frame = MAX_NB_PACKETS_MON_VMEM_DMA;
    
    r = _axilite->write(nb_packets_per_frame, REGW_NB_PACKETS_MON_VMEM);

    // Select neurons to monitor
    for (auto waddr = 0 ; waddr < _nb_nrn; waddr++){
        // Write monitor selection
        if (find(sel_mon.begin(), sel_mon.end(), waddr) != sel_mon.end()){
            SET_BIT_REG(_val_regw_sel_mon, BIT_DATA_SEL_MON_VNEW);
        }
        else{
            CLEAR_BIT_REG(_val_regw_sel_mon, BIT_DATA_SEL_MON_VNEW);
        }
        _axilite->write(_val_regw_sel_mon, REGW_SEL_MON);
        
        // Write address
        _axilite->write(waddr, REGW_WADDR_SEL_MON);

        // Write ram write enable
        SET_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_WEN_SEL_MON_VNEW);
        _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);

        // Wait for FPGA read and disable writing
        while(_axilite->read(REGR_WADDR_SEL_MON_LP) != waddr);
        CLEAR_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_WEN_SEL_MON_VNEW);
        _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    }

    return r;
}

/***************************************************************************
 * Set waveform monitoring on DAC
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::setWaveformMonitoring(vector<uint16_t> sel_mon){
    int r;
    for (auto i = 0; i < NB_CHANNELS_DAC; i++){
        r = _axilite->write(sel_mon[i], REGW_SEL_MON_DAC_BASE+i);
        if (r==EXIT_FAILURE)
            return r;
    }
    return r;
}

/***************************************************************************
 * Run waveform monitoring on DAC
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::startWaveformMonitoring(){
    int r;

    SET_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_DAC);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}

/***************************************************************************
 * Stop waveform monitoring
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::stopWaveformMonitoring(){
    int r;
    CLEAR_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_DAC);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}

/***************************************************************************
 * Run vmem monitoring
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::startVmemMonitoring(){
    int r;
    SET_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_VNEW);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}

/***************************************************************************
 * Stop waveform monitoring
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::stopVmemMonitoring(){
    int r;
    CLEAR_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_VNEW);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}

/***************************************************************************
 * Monitor vmem
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwMonitoring::monitorVmem(){
    int r;
	
    // doTheMagic();

    return r;
}

int HwMonitoring::setSpikeMonitoring(uint32_t nb_packets_per_frame){
    if (nb_packets_per_frame > MAX_NB_PACKETS_MON_SPK_DMA)
        nb_packets_per_frame = MAX_NB_PACKETS_MON_SPK_DMA;
    
    int r = _axilite->write(nb_packets_per_frame, REGW_NB_PACKETS_MON_SPK);

    return r;
}
int HwMonitoring::startSpikeMonitoring(){
    int r;
    SET_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_SPK);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}
int HwMonitoring::stopSpikeMonitoring(){
    int r;
    CLEAR_BIT_REG(_val_regw_control_mon, BIT_CONTROL_MON_EN_SPK);
    r = _axilite->write(_val_regw_control_mon, REGW_CONTROL_MON);
    return r;
}
