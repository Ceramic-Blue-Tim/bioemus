/*
*! @title      Main application for bioemus
*! @file       bioemus.h
*! @author     Romain Beaubois
*! @date       10 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **10 Aug 2022** : file creation (RB)
*/

#ifndef BIOEMUS_H
#define BIOEMUS_H

    #include "hw_config_system.h"

    #define SW_VERSION "0.2.0"

    /* ############################# AXI Lite setup ############################# */
    #ifdef HW_FPGA_ARCH_ZYNQMP
        #define BASEADDR_AXI_LITE_CORE0     0xA002'0000 // physical address map
        #define RANGE_AXI_LITE_CORE0        0x0001'0000 // range address map
    #endif
    #ifdef HW_FPGA_ARCH_VERSAL
        #define BASEADDR_AXI_LITE_CORE0     0x0203'4000'0000 // physical address map
        #define RANGE_AXI_LITE_CORE0        0x0000'0001'0000 // range address map
    #endif
#endif
