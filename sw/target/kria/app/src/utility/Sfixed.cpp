/*
*! @title      Signed fixed point functions and object
*! @file       Sfixed.cpp
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

#include "Sfixed.h"

/***************************************************************************
 * Convert signed fixed data to float
 * 
 * Sign extension of AXI output sfixed from INT+DEC to int32_t to allow conversion
 * (by default AXI wrapper module sets the extra bits to 0 so as sign extension
 * is required for sfixed from PL)
 * 
 * @param sfi_v : Integer value of sfi (int32_t)
 * @param fp_int : Fixed point number of integer part encoding bits
 * @param fp_dec : Fixed point number of decimal part encoding bits
 * @return Input sfi data as float
****************************************************************************/
float sfi2float(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec){
    uint32_t mask_sign_bit = 1<<(fp_int+fp_dec-1);
    int32_t v;
    if ((sfi_v & mask_sign_bit) != 0){
        v = sfi_v | ~(mask_sign_bit - 1);
    }
    else
        v = sfi_v;
    return ((float)(v)) / (1 << fp_dec);
}

/***************************************************************************
 * Convert signed fixed data to double 
 * 
 * @param sfi_v : Integer value of sfi (int32_t)
 * @param fp_int : Fixed point number of integer part encoding bits
 * @param fp_dec : Fixed point number of decimal part encoding bits
 * @return Input sfi data as double
****************************************************************************/
double sfi2double(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec){
    uint32_t mask_sign_bit = 1<<(fp_int+fp_dec-1);
    int32_t v;
    if ((sfi_v & mask_sign_bit) != 0){
        v = sfi_v | ~(mask_sign_bit - 1);
    }
    else
        v = sfi_v;
    return ((double)(v)) / (1 << fp_dec);
}

/***************************************************************************
 * Convert float to signed fixed
 * 
 * @param float_v : Float value to convert
 * @param fp_int : Fixed point number of integer part encoding bits
 * @param fp_dec : Fixed point number of decimal part encoding bits
 * @return Signed fixed as signed integer 32 bits
****************************************************************************/
int32_t float2sfi(float float_v, uint8_t fp_int, uint8_t fp_dec){
    return (int32_t)((float_v) * (1 << fp_dec));
}
int32_t float2sfi(float float_v, uint8_t fp_dec){
    return (int32_t)((float_v) * (1 << fp_dec));
}

Sfixed::Sfixed(float float_v, uint8_t fp_int, uint8_t fp_dec){
    _int    = fp_int;
    _dec    = fp_dec;
    _v      = (int32_t)((float_v) * (1 << fp_dec));
}

Sfixed::Sfixed(int32_t sfi_v, uint8_t fp_int, uint8_t fp_dec){
    _int    = fp_int;
    _dec    = fp_dec;
    _v      = sfi_v;
}

int32_t Sfixed::getValue(){
    return _v;
};

uint8_t Sfixed::getInt(){
    return _int;
};

uint8_t Sfixed::getDec(){
    return _dec;
};

void Sfixed::setValue(float float_v){
    _v = float2sfi(float_v, _int, _dec);
}

void Sfixed::setValue(int32_t sfi_v){
    _v = sfi_v;
}

float Sfixed::to_float(){
    return sfi2float(_v, _int, _dec);
}
double Sfixed::to_double(){
    return sfi2double(_v, _int, _dec);
}
