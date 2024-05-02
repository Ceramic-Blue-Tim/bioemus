# -*- coding: utf-8 -*-
# @title      Generate configuration files for SNN HH
# @file       gen_config.py
# @author     Romain Beaubois
# @date       23 Oct 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Script to generate configuration file for SNN HH
# 
# @details 
# > **23 Oct 2023** : file creation (RB)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from configuration.file_managers.HwConfigFile     import *
from configuration.file_managers.SwConfigFile     import *
from configuration.neurons.Ionrates               import *
from configuration.neurons.Hhparam                import *
from configuration.synapses.Synapses              import *
from configuration.network_models.OrgStructures   import *
from configuration.network_models.OrgStructures   import nrncode
from configuration.utility.settings               import _SOFTWARE_VERSION, _HW_MAX_NB_NEURONS, _HW_DT

class NetwConfParams:
    model="custom"
    emulation_time_s=300
    en_step_stim=False
    step_stim_delay_ms=0
    step_stim_duration_ms=0
    local_save_path="/home/ubuntu/bioemus/data/"
    en_randomize_hh_params=False
    val_randomize_hh_params=0.10
    org_wsyninh = 1.0
    org_wsynexc = 0.22
    org_pcon_in=0.08
    org_pcon_out=0.02
    org_wsyn_in=1.0
    org_wsyn_out=1.0
    org_inh_ratio=0.2


def gen_config(config_name:str, netw_conf_params:NetwConfParams, save_path:str="./"):
    # System parameters ####################################################################
    # Hardware platform (from KR260 platform)
    sw_ver              = _SOFTWARE_VERSION
    NB_NEURONS          = _HW_MAX_NB_NEURONS
    dt                  = _HW_DT

    # Files
    config_fname        = config_name
    local_dirpath_save  = save_path

    # Model selection
    MODEL               = netw_conf_params.model   # Model to generate: "organoid" "custom"

    # FPGA dev
    GEN_SIM_DEBUG_DATA          = False

    # Application parameters ################################################################
    swconfig_builder                                           = SwConfigFile()
    swconfig_builder.parameters["fpath_hwconfig"]              = "/home/ubuntu/bioemus/config/hwconfig_" + config_fname + ".txt"
    swconfig_builder.parameters["emulation_time_s"]            = netw_conf_params.emulation_time_s
    swconfig_builder.parameters["sel_nrn_vmem_dac"]            = [n for n in range(8)]
    swconfig_builder.parameters["sel_nrn_vmem_dma"]            = [n for n in range(16)]
    swconfig_builder.parameters["save_local_spikes"]           = False
    swconfig_builder.parameters["save_local_vmem"]             = False
    swconfig_builder.parameters["save_path"]                   = netw_conf_params.local_save_path # target saving director
    swconfig_builder.parameters["en_zmq_spikes"]               = True
    swconfig_builder.parameters["en_zmq_vmem"]                 = False
    swconfig_builder.parameters["en_zmq_stim"]                 = False
    swconfig_builder.parameters["en_wifi_spikes"]              = False
    swconfig_builder.parameters["ip_zmq_spikes"]               = "tcp://*:5557"
    swconfig_builder.parameters["ip_zmq_vmem"]                 = "tcp://*:5558"
    swconfig_builder.parameters["ip_zmq_stim"]                 = "tcp://192.168.137.1:5559"
    swconfig_builder.parameters["bin_fmt_save_spikes"]         = False
    swconfig_builder.parameters["bin_fmt_save_vmem"]           = True
    swconfig_builder.parameters["bin_fmt_send_spikes"]         = True
    swconfig_builder.parameters["bin_fmt_send_vmem"]           = True
    swconfig_builder.parameters["nb_tstamp_per_spk_transfer"]  = 100
    swconfig_builder.parameters["nb_tstep_per_vmem_transfer"]  = 190
    swconfig_builder.parameters["en_stim"]                     = netw_conf_params.en_step_stim
    swconfig_builder.parameters["stim_delay_ms"]               = netw_conf_params.step_stim_delay_ms
    swconfig_builder.parameters["stim_duration_ms"]            = netw_conf_params.step_stim_duration_ms

    # Globals & Builders ####################################################################
    tsyn_row, wsyn_row    = ([] for i in range(2))
    tsyn,     wsyn        = ([] for i in range(2))
    tnrn                  = []

    #   ██████ ██    ██ ███████ ████████  ██████  ███    ███ 
    #  ██      ██    ██ ██         ██    ██    ██ ████  ████ 
    #  ██      ██    ██ ███████    ██    ██    ██ ██ ████ ██ 
    #  ██      ██    ██      ██    ██    ██    ██ ██  ██  ██ 
    #   ██████  ██████  ███████    ██     ██████  ██      ██ 
    #                                                        
    # Custom model #################################################################
    if MODEL == "custom":
        # USER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        tnrn    = ["FS_nonoise"]*NB_NEURONS

        # tnrn[0] = "FS"
        # for i in range(0,511,1):
        #     tnrn[i]  = "FSorg"
        # for i in range(512,1023,1):
        #     tnrn[i]  = "RSorg"

        tnrn[0] = "FS_nonoise"
        tnrn[1] = "RS_nonoise"
        tnrn[2] = "IB_nonoise"
        tnrn[3] = "LTS_nonoise"

        SYN_MODE = "NONE"
        # SYN_MODE = "CHASER"
        # SYN_MODE = "RANDOM"
        # SYN_MODE = "ONE_TO_ALL"
        # SYN_MODE = "ONE_TO_ONE"
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


        # USER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Create synaptic conncetions
        # Synaptic types
        #      | source |
        # -----|--------|
        # dest |        |
        tsyn_dict = Synapses().getDict()
        weight = 1.9
        for dest in range(NB_NEURONS):
            for src in range(NB_NEURONS):

                if SYN_MODE == "NONE":
                    tsyn_i = "destexhe_none"

                elif SYN_MODE == "CHASER":
                    if ((src+1) == dest):
                        tsyn_i = "destexhe_ampa"
                    else:
                        tsyn_i = "destexhe_none"

                elif SYN_MODE == "RANDOM":
                    if (dest < 100) and (src < 100):
                        if dest != src:
                            if (np.random.rand() < 0.2):
                                tsyn_i = "destexhe_ampa"
                            else:
                                tsyn_i = "destexhe_none"
                        else:
                            tsyn_i = "destexhe_none"
                    else:
                        tsyn_i = "destexhe_none"

                elif SYN_MODE == "ONE_TO_ONE":
                    if src==0 and dest==1:
                        tsyn_i = "destexhe_gabab"
                    elif src==1 and dest==2:
                        tsyn_i = "destexhe_gabab"
                    else:
                        tsyn_i = "destexhe_none"

                elif SYN_MODE == "ONE_TO_ALL":
                    if src==0 and dest != 0:
                        tsyn_i = "destexhe_gabaa"
                    else:
                        tsyn_i = "destexhe_none"
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                tsyn_row.append(tsyn_dict[tsyn_i])
                if tsyn_i == "destexhe_none":
                    wsyn_row.append(0.0)
                else:
                    wsyn_row.append(weight)

            tsyn.append(tsyn_row)
            wsyn.append(wsyn_row)
            tsyn_row = []
            wsyn_row = []

    #   ██████  ██████   ██████   █████  ███    ██  ██████  ██ ██████  
    #  ██    ██ ██   ██ ██       ██   ██ ████   ██ ██    ██ ██ ██   ██ 
    #  ██    ██ ██████  ██   ███ ███████ ██ ██  ██ ██    ██ ██ ██   ██ 
    #  ██    ██ ██   ██ ██    ██ ██   ██ ██  ██ ██ ██    ██ ██ ██   ██ 
    #   ██████  ██   ██  ██████  ██   ██ ██   ████  ██████  ██ ██████  
    #                                                                  
    # Organoid modeling #################################################################
    elif MODEL == "connectoid" or MODEL == "single":
        PCON_IN     = netw_conf_params.org_pcon_in
        PCON_OUT    = netw_conf_params.org_pcon_out
        WSYN_IN     = netw_conf_params.org_wsyn_in
        WSYN_OUT    = netw_conf_params.org_wsyn_out
        INH_RATIO   = netw_conf_params.org_inh_ratio

        # Instanciate helper for organoid modeling configuration
        org         = OrgStructures(NB_NEURONS)

        # Configure organoid model
        ## (1) - Add organoids
        if MODEL == "single":
            org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[0, 0])
            org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[300, 0])
        elif MODEL == "connectoid":
            org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[0, 0])
            org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[300, 0])

        ## (2) - Generate neurons
        org.genNeurons(inh_ratio=INH_RATIO)

        ## (3) - Generate synaptic connections
        if MODEL == "single":
            org.genSynCon(rule="single", org_src=0, org_dest=0, max_pcon=PCON_IN)
            org.genSynCon(rule="single", org_src=1, org_dest=1, max_pcon=PCON_IN)
        elif MODEL == "connectoid":
            org.genSynCon(rule="single", org_src=0, org_dest=0, max_pcon=PCON_IN)
            org.genSynCon(rule="single", org_src=1, org_dest=1, max_pcon=PCON_IN)
            org.genSynCon(rule="connectoid", org_src=1, org_dest=0, max_pcon=PCON_OUT)
            org.genSynCon(rule="connectoid", org_src=0, org_dest=1, max_pcon=PCON_OUT)

        ## (4) - Assign weights
        if MODEL == "single":
            org.genSynWeights(org_src= 0, org_dest=0, weight=WSYN_IN)
            org.genSynWeights(org_src= 1, org_dest=1, weight=WSYN_IN)
        elif MODEL == "connectoid":
            org.genSynWeights(org_src= 0, org_dest=0, weight=WSYN_IN)
            org.genSynWeights(org_src= 1, org_dest=1, weight=WSYN_IN)
            org.genSynWeights(org_src= 0, org_dest=1, weight=WSYN_OUT)
            org.genSynWeights(org_src= 1, org_dest=0, weight=WSYN_OUT)

        # Print
        # org.plot("xy_pos")
        # org.plot("syn_con", org_src=0, org_dest=0)
        # org.plot("syn_con", org_src=1, org_dest=1)
        # org.plot("syn_con", org_src=0, org_dest=1)
        # org.plot("syn_con", org_src=1, org_dest=0)
        # org.plot("syn_con", block=True)

        # --------------------------------
        # NO NEED TO EDIT UNDER
        # (format for hardware config)

        # Get model parameters
        tsyn_org    = org.getSynTypes()
        wsyn_org    = org.getSynWeights()
        tnrn_org    = org.getNeuronTypes()
        tsyn_dict   = Synapses().getDict()

        for dest in range(NB_NEURONS):
            for src in range(NB_NEURONS):
                tsyn_i = tsyn_org[dest][src]
                wsyn_i = wsyn_org[dest][src]
                tsyn_row.append(tsyn_dict[tsyn_i])
                if tsyn_i == "destexhe_none":
                    wsyn_row.append(0.0)
                elif tsyn_i == "destexhe_ampa":
                    wsyn_row.append(netw_conf_params.org_wsynexc*wsyn_i)
                elif tsyn_i == "destexhe_gabaa":
                    wsyn_row.append(netw_conf_params.org_wsyninh*wsyn_i)
                else:
                    wsyn_row.append(wsyn_i)

            tsyn.append(tsyn_row)
            wsyn.append(wsyn_row)

            tsyn_row = []
            wsyn_row = []
        
        tnrn = tnrn_org
    else:
        exit()

    #   ██████  ██████  ███    ██ ███████ ██  ██████      ███████ ██ ██      ███████ 
    #  ██      ██    ██ ████   ██ ██      ██ ██           ██      ██ ██      ██      
    #  ██      ██    ██ ██ ██  ██ █████   ██ ██   ███     █████   ██ ██      █████   
    #  ██      ██    ██ ██  ██ ██ ██      ██ ██    ██     ██      ██ ██      ██      
    #   ██████  ██████  ██   ████ ██      ██  ██████      ██      ██ ███████ ███████ 
    #                                                                                
    # Config file #################################################################
    hw_cfg_file                 = HwConfigFile(sw_ver, NB_NEURONS)

    # Parameters
    hw_cfg_file.dt              = dt
    hw_cfg_file.nb_hhparam      = Hhparam().getNb()
    hw_cfg_file.nb_ionrate      = Ionrates().getNbIonRates("pospischil")
    hw_cfg_file.depth_ionrate   = Ionrates().getDepthIonRates("pospischil")
    hw_cfg_file.depth_synrate   = Synapses().getDepthSynRates("destexhe")

    # Ionrates
    [hw_cfg_file.m_rates1, hw_cfg_file.m_rates2,
    hw_cfg_file.h_rates1, hw_cfg_file.h_rates2] = Ionrates().getIonRates("pospischil", dt, GEN_SIM_DEBUG_DATA)

    # Synapse parameters
    hw_cfg_file.psyn     = Synapses().getPsyn("destexhe", dt)

    # Synrates
    hw_cfg_file.synrates = Synapses().getSynRates("destexhe", GEN_SIM_DEBUG_DATA)

    # Neuron types
    for n in tnrn:
        hhp = Hhparam().getParameters(n, dt)

        # Randomize noise parameters
        if netw_conf_params.en_randomize_hh_params:
            dp = Hhparam().getDict()
            hhp[dp["mu"]]       = hhp[dp["mu"]]    + netw_conf_params.val_randomize_hh_params*np.random.randn()*hhp[dp["mu"]]
            hhp[dp["theta"]]    = hhp[dp["theta"]] + netw_conf_params.val_randomize_hh_params*np.random.randn()*hhp[dp["theta"]]
            hhp[dp["sigma"]]    = hhp[dp["sigma"]] + netw_conf_params.val_randomize_hh_params*np.random.randn()*hhp[dp["sigma"]]
            hhp[dp["v_init"]]   = hhp[dp["v_init"]]+ netw_conf_params.val_randomize_hh_params*np.random.randn()*hhp[dp["v_init"]]

        hw_cfg_file.HH_param.append(hhp)

    # Synapses
    hw_cfg_file.tsyn = tsyn
    hw_cfg_file.wsyn = wsyn

    # Write file
    swconfig_builder.write(os.path.join(local_dirpath_save, "swconfig_" + config_fname + ".json"))  # save path of swconfig on local
    hw_cfg_file.write(os.path.join(local_dirpath_save, "hwconfig_" + config_fname + ".txt"))        # save path of hwconfig on local

    # Export network configuration and stimulation neurons
    if MODEL == "connectoid" or MODEL == "single":
        BOUNDARY_STIM_OUTER_RING = 0.9
        stim_nrn = np.where(np.array(org.dist2c_all) > BOUNDARY_STIM_OUTER_RING, True, False)
        params = [
            f'# BOUNDARY_STIM_OUTER_RING={BOUNDARY_STIM_OUTER_RING}',
            f'PCON_IN={PCON_IN}',
            f'PCON_OUT={PCON_OUT}',
            f'WSYN_IN={WSYN_IN}',
            f'WSYN_OUT={WSYN_OUT}',
            f'INH_RATIO={INH_RATIO}'
        ]
        bioemus_org = pd.DataFrame({
            'x': org.x_all,
            'y': org.y_all,
            'ntype': [nrncode[n] for n in org.tnrn_all],
            'stim': stim_nrn
        })
        fpath_cfg_stim = os.path.join(local_dirpath_save, "bioemus_cfg_stim_" + config_fname + ".csv")
        np.savetxt(fpath_cfg_stim, np.where(stim_nrn)[0], fmt='%d')
        
        fpath_cfg_network = os.path.join(local_dirpath_save, "bioemus_cfg_network_" + config_fname + ".csv")
        with open(fpath_cfg_network, 'a') as f:
            f.write('|'.join(params))
            bioemus_org.to_csv(f, index=False, sep=';')


    return [hw_cfg_file, swconfig_builder]