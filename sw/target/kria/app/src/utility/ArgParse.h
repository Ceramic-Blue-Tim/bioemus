/*
*! @title      Application argument parser
*! @file       ArgParse.h
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

#ifndef __ARGPARSE_H__
#define __ARGPARSE_H__

#include <string>

int parse_args(int argc, char* const argv[], std::string* fpath_swconfig, bool* print_swconfig, uint8_t* sweep_progress);

#endif