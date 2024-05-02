/*
*! @title      Main application for bioemus
*! @file       bioemus.cpp
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

#include "bioemus.h"

#include "CustomPrint.h"
#include "AxiLite.h"
#include "HwCfg.h"
#include "HwControl.h"
#include "HwMonitoring.h"
// #include "UIO.h"
#include "hw_config_com.h"
#include "hw_config_system.h"
#include "hw_config_hhparam.h"
#include "hw_config_ionrates.h"
#include "zmq.hpp"
#include "AxiDma.h"
#include "ArgParse.h"
#include "SwConfigParser.h"

#include <getopt.h>
#include <stdint.h>
#include <string>
#include <iostream>
#include <cstdint>
#include <atomic>

using namespace std;

int main(int argc, char* argv[])
{
    // Print app information
    cout << string(50, '=') << endl;
    cout << "* " << ITLC("Application: BioemuS") << endl;
    cout << "* " << ITLC("Date: ") << ITLC(__DATE__) << " " << ITLC(__TIME__) << endl;
    cout << "* " << ITLC("SW version: ") << ITLC(SW_VERSION) << endl;
    cout << "* " << ITLC("HW version: ") << ITLC(HW_VERSION) << endl;
    cout << "* " << ITLC("HW FPGA architecture: ") << ITLC(HW_FPGA_ARCH) << endl;
    cout << string(50, '=') << endl;
    
    int r; // Status return

    // Get starting time
    uint64_t tstart_core = get_posix_clock_time_usec();

    // Parse argument
    string fpath_swconfig;
    bool print_swconfig;
    uint8_t sweep_progress;
    r = parse_args(argc, argv, &fpath_swconfig, &print_swconfig, &sweep_progress);
    statusPrint(r, "Parse arguments");
    if(r==EXIT_FAILURE)
        return EXIT_FAILURE;
    
    // Parse configuration file
    SwConfigParser swconfig_parser = SwConfigParser(fpath_swconfig);
    if(print_swconfig)
        swconfig_parser.print();
    struct sw_config swconfig = swconfig_parser.getConfig();

    // Instanciate axilite
    AxiLite axilite_hw_setup = AxiLite( BASEADDR_AXI_LITE_CORE0, RANGE_AXI_LITE_CORE0,
                                        NB_REGS_WRITE_AXILITE_CORE0,
                                        NB_REGS_READ_AXILITE_CORE0);
    axilite_hw_setup.test_RW();
    
    // Hardware instances
    HwControl hw_ctrl(&axilite_hw_setup);           // Hardware control
    HwCfg hw_cfg(swconfig.fpath_hwconfig, &axilite_hw_setup);  // Hardware configuration

    // Init DMA
    AxiDma dma = AxiDma(swconfig);
    
    // Apply seeds for noise generator
    r = hw_cfg.setSeed();

    // Reset system
    infoPrint(0, "Reset system");
    r = hw_ctrl.reset();
    statusPrint(r, "Reset system");

    // Hardware configuration
    r = hw_cfg.apply();
    statusPrint(r, "Apply hardware configuration");

    // Hardware instance monitoring
    HwMonitoring hw_mon(&axilite_hw_setup, hw_cfg.getNbNrn());  // Hardware monitoring

    // Enable waveform monitoring
    infoPrint(0, "Activate waveform monitoring");
    r = hw_mon.setWaveformMonitoring(swconfig.sel_nrn_vmem_dac);
    r = hw_mon.startWaveformMonitoring();
    statusPrint(r, "Activate waveform monitoring");

    // Enable spike monitoring
	if (swconfig.save_local_spikes || swconfig.en_zmq_spikes || swconfig.en_wifi_spikes){
        infoPrint(0, "Activate spike monitoring");
        r = hw_mon.setSpikeMonitoring(swconfig.nb_tstamp_per_spk_transfer);
        r = hw_mon.startSpikeMonitoring();
        statusPrint(r, "Activate spike monitoring");
    }

    // Enable vmem monitoring
    if (swconfig.save_local_vmem ||swconfig.en_zmq_vmem){
        infoPrint(0, "Activate vmem monitoring");
        r = hw_mon.setVmemMonitoring(swconfig.sel_nrn_vmem_dma, swconfig.nb_tstep_per_vmem_transfer);
        r = hw_mon.startVmemMonitoring();
        statusPrint(r, "Activate vmem monitoring");
    }

    // Update sweep status
    infoPrint(0, "Update led progress");
    r = hw_ctrl.setSweepProgressLed(sweep_progress);
    statusPrint(r, "Update led progress");

    // Insert stimulation
    if (swconfig.en_stim){
        infoPrint(0, "Send stimulation");
        r = hw_ctrl.setStimTriggerDelayMs(swconfig.stim_delay_ms);
        r = hw_ctrl.setStimTriggerWidthMs(swconfig.stim_duration_ms);
        r = hw_ctrl.armStimTrigger();
        r = hw_ctrl.sendStimTrigger();
        r = hw_ctrl.armStimTrigger();
        statusPrint(r, "Send stimulation");
    }

    if(swconfig.save_local_spikes || swconfig.save_local_vmem || swconfig.en_zmq_spikes || swconfig.en_zmq_vmem)
        dma.monitoring(swconfig, hw_ctrl);
    else
        sleep(swconfig.emulation_time_s);

    // Disable calculation core
    infoPrint(0, "Disable calculation core");
    r = hw_ctrl.disableCore();
    statusPrint(r, "Disable calculation core");
    uint64_t tstop_core = get_posix_clock_time_usec();

    // Disable waveform monitoring
    r = hw_mon.stopWaveformMonitoring();
    statusPrint(r, "Disable waveform monitoring");

    // Disable spike monitoring
    if (swconfig.save_local_spikes || swconfig.en_zmq_spikes || swconfig.en_wifi_spikes){
        r = hw_mon.stopSpikeMonitoring();
        statusPrint(r, "Disable spike monitoring");
    }

    // Disable vmem monitoring
    if (swconfig.save_local_vmem ||swconfig.en_zmq_vmem){
        r = hw_mon.stopVmemMonitoring();
        statusPrint(r, "Disable vmem monitoring");
    }

    cout << "Application runtime: " << (tstop_core-tstart_core)*1e-6 << " seconds" << endl;
    statusPrint(EXIT_SUCCESS, "Running application");

    hw_ctrl.hold_reset();

    return EXIT_SUCCESS;
}
