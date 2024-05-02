/*
*! @title      Signed fixed point functions and object
*! @file       Sfixed.h
*! @author     Romain Beaubois
*! @date       09 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2021 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! Sfixed functions
*! * Convert from float to sfi 
*! * Convert from sfi to float
*! * Handle AXI output sfi (sign extension from INT+DEC to 32 bits)
*! 
*! @details
*! > **22 Sep 2021** : file creation (RB)
*! > **09 Aug 2022** : adapt types for user-space app in zynq ubuntu (RB)
*/

#ifndef SFIXED_H
#define SFIXED_H

#include <stdint.h>

float sfi2float(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec);
int32_t float2sfi(float float_v, uint8_t fp_int, uint8_t fp_dec);
int32_t float2sfi(float float_v, uint8_t fp_dec);

double sfi2double(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec);

class Sfixed{
    private:
        int32_t _v;  /// Fixed point value
        uint8_t _int; /// Fixed point integer coding
        uint8_t _dec; /// Fixed point decimal coding
    public:
        Sfixed(float float_v, uint8_t fp_int, uint8_t fp_dec);
        Sfixed(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec);
        int32_t getValue();
        uint8_t  getInt();
        uint8_t  getDec();
        void setValue(float float_v);
        void setValue(int32_t sfi_v);
        float to_float();
        double to_double();
};

#endif