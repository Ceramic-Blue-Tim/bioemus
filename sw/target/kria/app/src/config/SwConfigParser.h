/*
*! @title      Software configuration
*! @file       SwConfig.h
*! @author     Romain Beaubois
*! @date       27 Apr 2023
*! @copyright
*! SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **27 Apr 2023** : file creation (RB)
*/

#ifndef __SWCONFIG_H__
#define __SWCONFIG_H__

#include <iostream>
#include <fstream>
#include <vector>
#include "json.hpp"

using json = nlohmann::json;

struct sw_config{
    std::string fpath_hwconfig;
    int emulation_time_s;
    std::vector<uint16_t> sel_nrn_vmem_dac;
    std::vector<uint16_t> sel_nrn_vmem_dma;
    bool save_local_spikes;
    bool save_local_vmem;
    std::string save_path;
    bool en_zmq_spikes;
    bool en_zmq_vmem;
    bool en_zmq_stim;
    bool en_wifi_spikes;
    std::string ip_zmq_spikes;
    std::string ip_zmq_vmem;
    std::string ip_zmq_stim;
    bool bin_fmt_save_spikes;
    bool bin_fmt_save_vmem;
    bool bin_fmt_send_spikes;
    bool bin_fmt_send_vmem;
    int nb_tstamp_per_spk_transfer;
    int nb_tstep_per_vmem_transfer;
    bool en_stim;
    int stim_delay_ms;
    int stim_duration_ms;
};

class SwConfigParser{
    private:
        struct sw_config _config;
    public:
        SwConfigParser(std::string fpath_cfg);
        ~SwConfigParser();
        void print();
        void print(std::string key, bool value);
        void print(std::string key, int value);
        void print(std::string key, std::string value);
        void print(std::string key, std::vector<uint16_t> value);
        struct sw_config getConfig();
};

template <typename T>
bool extract_json_variable(const json& j, const std::string& key, T& out);

#endif