/*
*! @title      Class to handle hardware configuration
*! @file       HwCfg.h
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

#ifndef __HWCFG_H__
#define __HWCFG_H__

#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string>
#include <string.h>

#include "AxiLite.h"
#include "CustomPrint.h"
#include "hw_config_system.h"
#include "hw_config_com.h"
#include "hw_config_ionrates.h"
#include "hw_config_hhparam.h"
#include "hw_config_synapses.h"
#include "reg_control.h"

using namespace std;

// #define DBG_FIXED_SEED

#define HEADER_SIZE 2
#define KEY_SEP '='
#define COL_SEP ';'
#define VAL_SEP ','

static uint16_t twsyn[ (NB_RAM_TWSYN*RAMWIDTH_TWSYN/(8*sizeof(uint16_t))) * (RAMDEPTH_TWSYN)];

class HwCfg{
    private:
        string      _fpath;
        ifstream    _hw_cfg_file;
        uint16_t    _nb_nrn         = NB_NRN;
        uint16_t    _nb_hhparam     = NB_HHPARAM;
        uint16_t    _depth_ionrate  = IONRATE_TABLE_DEPTH;
        uint16_t    _nb_ionrate     = NB_IONRATE;
        uint16_t    _depth_synrate  = SYNRATE_TABLE_DEPTH;

        AxiLite*    _axilite;
        uint32_t    _val_regw_setup_syn;

        int applyHhparam();
        int applyIonrates();
        int applySynrates();
        int applySynParams();
        int applySynConf();

        template <typename data_t>
        int decodeLine(string key, data_t* rval);

    public:
        HwCfg(string fpath, AxiLite* axilite);
        int apply();
        int setSeed();
        uint16_t getNbNrn();
};

#endif