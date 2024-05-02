/*
*! @title      Class to handle hardware control
*! @file       HwControl.cpp
*! @author     Romain Beaubois
*! @date       19 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **19 Aug 2022** : file creation (RB)
*/

#include "HwControl.h"
#include <iostream>
#include <fstream>

/***************************************************************************
 * Constructor
 * 
 * @param axilite Pointer to hw configuration axilite 
 * @return HwControl
****************************************************************************/
HwControl::HwControl(AxiLite *axilite){
    _axilite            = axilite;
    _val_regw_control   = 0;
}

/***************************************************************************
 * Reset hardware
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::reset(){
    int r;

    SET_BIT_REG(_val_regw_control, BIT_CONTROL_RESET);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);
    usleep(300e3);
    CLEAR_BIT_REG(_val_regw_control, BIT_CONTROL_RESET);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Hold Reset
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::hold_reset(){
    int r;

    SET_BIT_REG(_val_regw_control, BIT_CONTROL_RESET);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Enable calculation core
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::enableCore(){
    int r;

    SET_BIT_REG(_val_regw_control, BIT_CONTROL_EN_CORE);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Disable calculation core
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::disableCore(){
    int r;

    CLEAR_BIT_REG(_val_regw_control, BIT_CONTROL_EN_CORE);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Send stimulation trigger
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::sendStimTrigger(){
    int r;

    SET_BIT_REG(_val_regw_control, BIT_CONTROL_STIM_TRIG_PS);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Set stimulation trigger delay in µs
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::setStimTriggerDelayUs(float stim_delay_us){
    int r;

    // Disable stimulation trigger to avoid unexpected behavior in hardware
    armStimTrigger();

    // Set stimulation width
    r = _axilite->write(stim_delay_us/(TIME_STEP_MS*1e3), REGW_STIM_DELAY);

    return r;
}

/***************************************************************************
 * Set stimulation trigger delay in ms
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::setStimTriggerDelayMs(float stim_delay_ms){
    int r;

    r = setStimTriggerDelayUs(stim_delay_ms*1e3);

    return r;
}

/***************************************************************************
 * Set stimulation trigger width in µs
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::setStimTriggerWidthUs(float stim_width_us){
    int r;

    // Disable stimulation trigger to avoid unexpected behavior in hardware
    armStimTrigger();

    // Set stimulation width
    r = _axilite->write(stim_width_us/(TIME_STEP_MS*1e3), REGW_STIM_WIDTH);

    return r;
}

/***************************************************************************
 * Set stimulation trigger width in ms
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::setStimTriggerWidthMs(float stim_width_ms){
    int r;

    r = setStimTriggerWidthUs(stim_width_ms*1e3);

    return r;
}

/***************************************************************************
 * Re arm stimulation trigger
 * 
 * @param stim_width_us stim width in us
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::armStimTrigger(){
    int r;

    // Set stim trig ps to 0 to arm fsm
    CLEAR_BIT_REG(_val_regw_control, BIT_CONTROL_STIM_TRIG_PS);
    r = _axilite->write(_val_regw_control, REGW_CONTROL);

    return r;
}

/***************************************************************************
 * Set led progress based on sweep progress
 * 
 * @param sweep_progress sweep progress 0 to 100%
 * 
 * @return EXIT_SUCCESS if successful otherwise EXIT_FAILURE
****************************************************************************/
int HwControl::setSweepProgressLed(uint8_t sweep_progress){
    int r;

    r = _axilite->write(sweep_progress, REGW_USER_LEDS);

    return r;
}