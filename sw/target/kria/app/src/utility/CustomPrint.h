/*
*! @title      Custom functions for print
*! @file       CustomPrint.h
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

#ifndef CUSTOM_PRINT_H
#define CUSTOM_PRINT_H

    #include <stdint.h>
    #include <string>
    #include <iostream>
    using namespace std;

    // Source : https://stackoverflow.com/questions/2616906/how-do-i-output-coloured-text-to-a-linux-terminal
    /* FOREGROUND */
    #define RST     "\x1B[0m"
    #define KRED    "\x1B[31m"
    #define KGRN    "\x1B[32m"
    #define KYEL    "\x1B[33m"
    #define KBLU    "\x1B[34m"
    #define KMAG    "\x1B[35m"
    #define KCYN    "\x1B[36m"
    #define KWHT    "\x1B[37m"

    #define FRED(x) KRED x RST
    #define FGRN(x) KGRN x RST
    #define FYEL(x) KYEL x RST
    #define FBLU(x) KBLU x RST
    #define FMAG(x) KMAG x RST
    #define FCYN(x) KCYN x RST
    #define FWHT(x) KWHT x RST

    #define BOLD(x) "\x1B[1m" x RST
    #define ITLC(x) "\x1B[3m" x RST
    #define UNDL(x) "\x1B[4m" x RST

    /***************************************************************************
     * Print error and debug information
     *
     * @param status EXIT_FAILURE, EXIT_SUCCESS
     * @param msg Message to print
     * @return NULL
    ****************************************************************************/
    void statusPrint(int status, const string msg);
    void infoPrint(int type, const string msg);

#endif