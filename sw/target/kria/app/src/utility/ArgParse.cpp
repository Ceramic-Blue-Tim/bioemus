/*
*! @title      Application argument parser
*! @file       ArgParse.cpp
*! @author     Romain Beaubois
*! @date       08 Mar 2023
*! @copyright
*! SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **08 Mar 2023** : file creation (RB)
*/

#include "ArgParse.h"
#include <unistd.h>
#include <iostream>
#include <cstdlib>
#include <getopt.h>
#include <algorithm>

int parse_args(int argc, char* const argv[], std::string* fpath_swconfig, bool* print_swconfig, uint8_t* sweep_progress){
    // Default values
    *fpath_swconfig  = "/home/ubuntu/config/bioemus_swconfig.json";
    *print_swconfig  = false;
    *sweep_progress    = 100;

    // Define long options
    struct option long_options[] = {
        {"fpath-swconfig", required_argument, 0, 'f'},
        {"print-swconfig", no_argument, 0, 'p'},
        {"sweep-progress", required_argument, 0, 's'},
        {0, 0, 0, 0} // end of options marker
    };

    // Parse command line options
    int opt;
    while ((opt = getopt_long(argc, argv, "f:p:s", long_options, NULL)) != -1) {
        switch (opt) {
            case 'f':
                *fpath_swconfig = optarg;
                break;
            case 'p':
                *print_swconfig = true;
                break;
            case 's':
                *sweep_progress = atoi(optarg);
                break;
            case '?':
                std::cerr << "Unknown option: " << optopt << std::endl;
                return EXIT_FAILURE;
            default:
                std::cerr << "Error parsing arguments" << std::endl;
                std::cerr << "Usage:" << std::endl;
                std::cerr << "\t[--fpath-swconfig <fpath> path to software config file]";
                std::cerr << "\t[--print-swconfig (optionnal) print software config loaded]";
                std::cerr << "\t[--sweep-progress sweep progress 0 to 100%]";
                return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}