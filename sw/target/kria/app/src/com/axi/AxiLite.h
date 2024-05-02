/*
*! @title      Axi lite object
*! @file       AxiLite.h
*! @author     Romain Beaubois
*! @date       15 Sep 2021
*! @copyright
*! SPDX-FileCopyrightText: © 2021 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! Axi lite object
*! * Store pointer to base address to handle axi as C array
*! * Store numbers of read and write registers (PS pov)
*! * Read/write functions
*! 
*! @details
*! > **15 Sep 2021** : file creation (RB)
*! > **10 Aug 2022** : adapt axilite to zubuntu (RB)
*! > **21 Dec 2022** : add constructor with range setup (RB)
*/

#ifndef AXILITE_H
#define AXILITE_H

#include <iostream>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include "Sfixed.h"
#include "CustomPrint.h"

using namespace std;

class AxiLite{
    public:
        private :
        // Members
        uint16_t _nb_regs_write;
        uint16_t _nb_regs_read;
        uint16_t _nb_regs;
        volatile uint32_t* _axi_regs_u32_vptr;
        
        public :
        // Methods
        AxiLite(uint64_t base_addr, uint64_t range, uint16_t nb_regs_write, uint16_t nb_regs_read);
        int write(uint32_t wdata, uint16_t regw);
        int write(float wdata, uint16_t regw, uint8_t fp_int, uint8_t fp_dec);
        uint32_t read(uint16_t regr);
        float read(uint16_t regr, uint8_t fp_int, uint8_t fp_dec);
        int test_RW();
};

#endif