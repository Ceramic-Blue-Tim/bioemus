/*
*! @title      Software configuration
*! @file       SwConfigParser.cpp
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

#include "SwConfigParser.h"

template <typename T>
bool extract_json_variable(const json& j, const std::string& key, T& out) {
    if (!j.contains(key)) {
        std::cerr << "JSON object does not contain key: " << key << std::endl;
        return false;
    }

    try {
        out = j[key].get<T>();
        return true;
    } catch (const json::type_error& e) {
        std::cerr << "Failed to extract variable from JSON object: " << e.what() << std::endl;
        return false;
    }
}

SwConfigParser::SwConfigParser(std::string fpath_cfg){
    int r;

    // Initialize structure for compatibility
    _config.bin_fmt_save_spikes = true;
    _config.bin_fmt_save_vmem   = true;
    _config.bin_fmt_send_spikes = true;
    _config.bin_fmt_send_vmem   = true;

    // Open the configuration file
    std::ifstream config_file(fpath_cfg);
    if (!config_file.is_open()) {
        std::cerr << "Failed to open configuration file." << std::endl;
    }

    // Parse the configuration file as JSON
    json config_json;
    try {
        config_file >> config_json;
    } catch (const json::parse_error& e) {
        std::cerr << "Failed to parse configuration file: " << e.what() << std::endl;
    }

    r = !extract_json_variable(config_json, "fpath_hwconfig",               _config.fpath_hwconfig);
    r = !extract_json_variable(config_json, "emulation_time_s",             _config.emulation_time_s);
    r = !extract_json_variable(config_json, "sel_nrn_vmem_dac",             _config.sel_nrn_vmem_dac);
    r = !extract_json_variable(config_json, "sel_nrn_vmem_dma",             _config.sel_nrn_vmem_dma);
    r = !extract_json_variable(config_json, "save_local_spikes",            _config.save_local_spikes);
    r = !extract_json_variable(config_json, "save_local_vmem",              _config.save_local_vmem);
    r = !extract_json_variable(config_json, "save_path",                    _config.save_path);
    r = !extract_json_variable(config_json, "en_zmq_spikes",                _config.en_zmq_spikes);
    r = !extract_json_variable(config_json, "en_zmq_vmem",                  _config.en_zmq_vmem);
    r = !extract_json_variable(config_json, "en_zmq_stim",                  _config.en_zmq_stim);
    r = !extract_json_variable(config_json, "en_wifi_spikes",               _config.en_wifi_spikes);
    r = !extract_json_variable(config_json, "ip_zmq_spikes",                _config.ip_zmq_spikes);
    r = !extract_json_variable(config_json, "ip_zmq_vmem",                  _config.ip_zmq_vmem);
    r = !extract_json_variable(config_json, "ip_zmq_stim",                  _config.ip_zmq_stim);
    r = !extract_json_variable(config_json, "bin_fmt_save_spikes",          _config.bin_fmt_save_spikes);
    r = !extract_json_variable(config_json, "bin_fmt_save_vmem",            _config.bin_fmt_save_vmem);
    r = !extract_json_variable(config_json, "bin_fmt_send_spikes",          _config.bin_fmt_send_spikes);
    r = !extract_json_variable(config_json, "bin_fmt_send_vmem",            _config.bin_fmt_send_vmem);
    r = !extract_json_variable(config_json, "nb_tstamp_per_spk_transfer",   _config.nb_tstamp_per_spk_transfer);
    r = !extract_json_variable(config_json, "nb_tstep_per_vmem_transfer",   _config.nb_tstep_per_vmem_transfer);
    r = !extract_json_variable(config_json, "en_stim",                      _config.en_stim);
    r = !extract_json_variable(config_json, "stim_delay_ms",                _config.stim_delay_ms);
    r = !extract_json_variable(config_json, "stim_duration_ms",             _config.stim_duration_ms);
}

SwConfigParser::~SwConfigParser(){
}

void SwConfigParser::print(){
    print("fpath_hwconfig",                 _config.fpath_hwconfig);
    print("emulation_time_s",               _config.emulation_time_s);
    print("sel_nrn_vmem_dac",               _config.sel_nrn_vmem_dac);
    print("sel_nrn_vmem_dma",               _config.sel_nrn_vmem_dma);
    print("save_local_spikes",              _config.save_local_spikes);
    print("save_local_vmem",                _config.save_local_vmem);
    print("save_path",                      _config.save_path);
    print("en_zmq_spikes",                  _config.en_zmq_spikes);
    print("en_zmq_vmem",                    _config.en_zmq_vmem);
    print("en_zmq_stim",                    _config.en_zmq_stim);
    print("en_wifi_spikes",                 _config.en_wifi_spikes);
    print("ip_zmq_spikes",                  _config.ip_zmq_spikes);
    print("ip_zmq_vmem",                    _config.ip_zmq_vmem);
    print("ip_zmq_stim",                    _config.ip_zmq_stim);
    print("bin_fmt_save_spikes",            _config.bin_fmt_save_spikes);
    print("bin_fmt_save_vmem",              _config.bin_fmt_save_vmem);
    print("bin_fmt_send_spikes",            _config.bin_fmt_send_spikes);
    print("bin_fmt_send_vmem",              _config.bin_fmt_send_vmem);
    print("nb_tstamp_per_spk_transfer",     _config.nb_tstamp_per_spk_transfer);
    print("nb_tstep_per_vmem_transfer",     _config.nb_tstep_per_vmem_transfer);
    print("en_stim",                        _config.en_stim);
    print("stim_delay_ms",                  _config.stim_delay_ms);
    print("stim_duration_ms",               _config.stim_duration_ms);
}

void SwConfigParser::print(std::string key, bool value){
    std::cout << key << ": " << std::boolalpha << value << std::endl;
}

void SwConfigParser::print(std::string key, int value){
    std::cout << key << ": " << value << std::endl;
}

void SwConfigParser::print(std::string key, std::string value){
    std::cout << key << ": " << value << std::endl;
}

void SwConfigParser::print(std::string key, std::vector<uint16_t> value){
    std::cout << key << ": [ ";
    for (int elem : value)
        std::cout << elem << " ";
    std::cout << "]" << std::endl;
}

struct sw_config SwConfigParser::getConfig(){
    return _config;
}
