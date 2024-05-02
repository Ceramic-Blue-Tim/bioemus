/*
*! @title      Fixed point support macros
*! @file       fixed_point.h
*! @author     Stackoverflow #30203271
*! @date       12 Aug 2021
*!
*! @brief
*! Convert int to sfixed
*! 
*! @details
*! > **12 Aug 2021** : file creation (Stackoverflow)
*/

#ifndef FIXED_POINT_H
#define FIXED_POINT_H
    #include <stdint.h>

    // sfixed macro
    typedef uint32_t sfixed;
    #define DEC         10
    #define DEC_ION     16
    #define DEC_MUL     10

    #define FLOAT2FIXED(x, y) ((int)((x) * (1 << y)))
    #define FIXED2DOUBLE(x, y) (((double)(x)) / (1 << y))

    #define FIXED_ONE (1 << DEC)
    #define INT2FIXED(x) ((x) << DEC)
    #define FIXED2INT(x) ((x) >> DEC)
    #define MULT(x, y) ( ((x) >> DEC_MUL) * ((y)>> DEC_MUL))
#endif