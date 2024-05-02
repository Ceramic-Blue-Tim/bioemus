/*
*! @title      Custom functions for print
*! @file       CustomPrint.cpp
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

#include "CustomPrint.h"

/***************************************************************************
 * Print error and debug information
 *
 * @param status EXIT_FAILURE, EXIT_SUCCESS
 * @param msg Message to print
 * @return NULL
****************************************************************************/
void statusPrint(int status, const string msg){
    switch (status){
        case EXIT_SUCCESS:
#ifdef DEBUG
            cout << "[" << FGRN("SUCCESS") << "] " << msg << endl;
#endif
            break;

        case EXIT_FAILURE:
            cerr << "[" << FRED("FAILURE") << "] " << msg << endl;
            break;
        
        default:
            break;
    }
}

void infoPrint(int type, const string msg){
    cout << FMAG("> ") << FMAG(""+msg+"") << endl;
    // switch (status){
    //     case 0:
            
    //     default:
    //         break;
    // }
}