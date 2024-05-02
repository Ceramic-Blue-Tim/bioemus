/*
*! @title      Class to handle hardware control
*! @file       HwControl.h
*! @author     Romain Beaubois
*! @date       09 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **09 Aug 2022** : file creation (RB)
*/

#ifndef __HWCONTROL_H__
#define __HWCONTROL_H__

#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string>

#include "AxiLite.h"
#include "CustomPrint.h"
#include "hw_config_system.h"
#include "hw_config_com.h"
#include "hw_config_ionrates.h"
#include "hw_config_hhparam.h"
#include "reg_control.h"

using namespace std;

class HwControl{
    private:
        AxiLite*    _axilite;
        uint32_t    _val_regw_control;

    public:
        HwControl(AxiLite* axilite);
        int reset();
        int hold_reset();
        int enableCore();
        int disableCore();
        int setStimTriggerDelayMs(float stim_delay_ms);
        int setStimTriggerDelayUs(float stim_delay_us);
        int setStimTriggerWidthUs(float stim_width_us);
        int setStimTriggerWidthMs(float stim_width_ms);
        int sendStimTrigger();
        int armStimTrigger();
        int setSweepProgressLed(uint8_t sweep_progress);
};

#endif