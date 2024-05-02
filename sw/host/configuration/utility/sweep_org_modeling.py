# -*- coding: utf-8 -*-
# @title      Sweep organoid modeling
# @file       sweep_org_modeling.py
# @author     Romain Beaubois
# @date       01 May 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief
# 
# @details 
# > **01 May 2023** : file creation (RB)

import numpy as np
from tqdm import tqdm

from configuration.file_managers.HwConfigFile       import *
from configuration.file_managers.SwConfigFile       import *
from configuration.synapses.Synapses           import Synapses
from NeuronHH           import NeuronHH
from emulation.hh_snn.SnnEmulator        import SnnEmulator
from configuration.network_models.OrgStructures   import OrganoidEmulator

# System parameters ####################################################################

# Hardware platform (from KR260 platform)
sw_ver              = "0.1.0"
NB_NEURONS          = 512
dt                  = 2**-5 # [ms]

# FPGA dev
GEN_SIM_DEBUG_DATA          = False

# Globals & Builders ####################################################################
nhh     = NeuronHH()
syn     = Synapses()

tsyn_row, wsyn_row    = ([] for i in range(2))
tsyn,     wsyn        = ([] for i in range(2))
tnrn                  = []

# Software configuration ################################################################
swconfig_builder                                           = SwConfigFile()
swconfig_builder.parameters["emulation_time_s"]            = 5*60
swconfig_builder.parameters["save_local_spikes"]           = True
swconfig_builder.parameters["nb_tstamp_per_spk_transfer"]  = 100
swconfig_builder.parameters["save_path"]                   = "/mnt/org_modeling/sweeps/" # target saving directory

# Sweep parameters ######################################################################
max_pcon                = []
rules                   = []
weight                  = []
local_dirpath_save      = "../../../data/sweep_config/"
target_dirpath_config   = "/home/ubuntu/software/app/snn_hh/config/"
target_swconfig_fpath   = []

MAX_PCON_OUT_LIMITS = [0.01, 0.40]
MAX_PCON_OUT_RANGE  = 4

MAX_PCON_IN_LIMITS  = [0.01, 0.40]
MAX_PCON_IN_RANGE   = 4

WEIGHT_IN_LIMITS    = [40, 120]
WEIGHT_IN_RANGE     = 4

WEIGHT_OUT_LIMITS   = [40, 120]
WEIGHT_OUT_RANGE    = 4

# Generate parameters
NB_SWEEPS           = (WEIGHT_IN_RANGE*WEIGHT_OUT_RANGE*MAX_PCON_IN_RANGE*MAX_PCON_OUT_RANGE)*3
MAX_PCON_OUT_PARAMS = np.linspace(MAX_PCON_OUT_LIMITS[0], MAX_PCON_OUT_LIMITS[1], MAX_PCON_OUT_RANGE)
MAX_PCON_IN_PARAMS  = np.linspace(MAX_PCON_IN_LIMITS[0],  MAX_PCON_IN_LIMITS[1],  MAX_PCON_IN_RANGE)
WEIGHT_OUT_PARAMS   = np.linspace(WEIGHT_OUT_LIMITS[0],   WEIGHT_OUT_LIMITS[1],   WEIGHT_OUT_RANGE)
WEIGHT_IN_PARAMS    = np.linspace(WEIGHT_IN_LIMITS[0],    WEIGHT_IN_LIMITS[1],    WEIGHT_IN_RANGE)

# Single
for p_out in range(MAX_PCON_OUT_RANGE):
    for p_in in range(MAX_PCON_IN_RANGE):
        for w_out in range(WEIGHT_OUT_RANGE):
            for w_in in range(WEIGHT_IN_RANGE):
                rules.append(["single", "single", "none", "none"])
                max_pcon.append([MAX_PCON_IN_PARAMS[p_in], MAX_PCON_IN_PARAMS[p_in], MAX_PCON_OUT_PARAMS[p_out], MAX_PCON_OUT_PARAMS[p_out]])
                weight.append([WEIGHT_IN_PARAMS[w_in], WEIGHT_IN_PARAMS[w_in], WEIGHT_OUT_PARAMS[w_out], WEIGHT_OUT_PARAMS[w_out]])

# Assembloid
for p_out in range(MAX_PCON_OUT_RANGE):
    for p_in in range(MAX_PCON_IN_RANGE):
        for w_out in range(WEIGHT_OUT_RANGE):
            for w_in in range(WEIGHT_IN_RANGE):
                rules.append(["single", "single", "assembloid", "assembloid"])
                max_pcon.append([MAX_PCON_IN_PARAMS[p_in], MAX_PCON_IN_PARAMS[p_in], MAX_PCON_OUT_PARAMS[p_out], MAX_PCON_OUT_PARAMS[p_out]])
                weight.append([WEIGHT_IN_PARAMS[w_in], WEIGHT_IN_PARAMS[w_in], WEIGHT_OUT_PARAMS[w_out], WEIGHT_OUT_PARAMS[w_out]])

# Connectoid
for p_out in range(MAX_PCON_OUT_RANGE):
    for p_in in range(MAX_PCON_IN_RANGE):
        for w_out in range(WEIGHT_OUT_RANGE):
            for w_in in range(WEIGHT_IN_RANGE):
                rules.append(["single", "single", "connectoid", "connectoid"])
                max_pcon.append([MAX_PCON_IN_PARAMS[p_in], MAX_PCON_IN_PARAMS[p_in], MAX_PCON_OUT_PARAMS[p_out], MAX_PCON_OUT_PARAMS[p_out]])
                weight.append([WEIGHT_IN_PARAMS[w_in], WEIGHT_IN_PARAMS[w_in], WEIGHT_OUT_PARAMS[w_out], WEIGHT_OUT_PARAMS[w_out]])

for i in tqdm(range(NB_SWEEPS)):
    # Organoid modeling #################################################################

    # Instanciate helper for organoid modeling configuration
    org         = OrganoidEmulator(NB_NEURONS)

    # Configure organoid model
    ## (1) - Add organoids
    org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[0, 0])
    org.addOrganoid(org_diam=250, nrn_diam=15, org_center_xy=[500, 0])

    ## (2) - Generate neurons
    org.genNeurons(inh_ratio=0.1)

    ## (3) - Generate synaptic connections
    org.genSynCon(rule=rules[i][0], org_src=0, org_dest=0, max_pcon=max_pcon[i][0])
    org.genSynCon(rule=rules[i][1], org_src=1, org_dest=1, max_pcon=max_pcon[i][1])
    org.genSynCon(rule=rules[i][2], org_src=0, org_dest=1, max_pcon=max_pcon[i][2])
    org.genSynCon(rule=rules[i][3], org_src=1, org_dest=0, max_pcon=max_pcon[i][3])

    ## (4) - Assign weights
    org.genSynWeights(org_src= 0, org_dest=0, weight=weight[i][0])
    org.genSynWeights(org_src= 1, org_dest=1, weight=weight[i][1])
    org.genSynWeights(org_src= 0, org_dest=1, weight=weight[i][2])
    org.genSynWeights(org_src= 1, org_dest=0, weight=weight[i][3])

    # --------------------------------
    # Get model parameters
    tsyn_org    = org.getSynTypes()
    wsyn_org    = org.getSynWeights()
    tnrn_org    = org.getNeuronTypes()
    tsyn_dict   = syn.getDict()

    for dest in range(NB_NEURONS):
        for src in range(NB_NEURONS):
            tsyn_i = tsyn_org[dest][src]
            [_, cmem , area_cm2] = nhh.getHHparam(tnrn_org[dest], dt)
            tsyn_row.append(tsyn_dict[tsyn_i])
            wsyn_row.append(syn.getGsyn(tsyn_i, dt, cmem, area_cm2))

        tsyn.append(tsyn_row)
        wsyn.append(wsyn_row)

        tsyn_row = []
        wsyn_row = []

    tnrn = tnrn_org
  
    # Config file #################################################################
    hw_cfg_file                 = HwConfigFile(sw_ver, NB_NEURONS)

    # Parameters
    hw_cfg_file.dt              = dt
    hw_cfg_file.nb_hhparam      = nhh.getNbHHparam()
    hw_cfg_file.nb_ionrate      = nhh.getNbIonRates("pospischil")
    hw_cfg_file.depth_ionrate   = nhh.getDepthIonRates("pospischil")
    hw_cfg_file.depth_synrate   = syn.getDepthSynRates("destexhe")

    # Ionrates
    [hw_cfg_file.m_rates1, hw_cfg_file.m_rates2,
    hw_cfg_file.h_rates1, hw_cfg_file.h_rates2] = nhh.getIonRates("pospischil", dt, GEN_SIM_DEBUG_DATA)

    # Synrates
    hw_cfg_file.synrates = syn.getSynRates("destexhe", GEN_SIM_DEBUG_DATA)

    # Neuron types
    for n in tnrn:
        [hhp, _, _] = nhh.getHHparam(n, dt)

        # Randomize noise parameters
        # [hhp, _, _] = nhh.getHHparam(n, dt)
        # dp = nhh.getDictHHparam()
        # hhp[dp["mu"]]       = hhp[dp["mu"]]    + 0.02*(np.random.rand()*hhp[dp["mu"]]      - np.random.rand()*hhp[dp["mu"]])
        # hhp[dp["theta"]]    = hhp[dp["theta"]] + 0.02*(np.random.rand()*hhp[dp["theta"]]   - np.random.rand()*hhp[dp["theta"]])
        # hhp[dp["sigma"]]    = hhp[dp["sigma"]] + 0.02*(np.random.rand()*hhp[dp["sigma"]]   - np.random.rand()*hhp[dp["sigma"]])

        hw_cfg_file.HH_param.append(hhp)

    # Synapses
    hw_cfg_file.tsyn = tsyn
    hw_cfg_file.wsyn = wsyn

    # Write files #################################################################
    fname = str(rules[i][3]) + "-pcon=" + str(max_pcon[i][:]) + "-wsyn=" + str(weight[i][:])
    fname = fname.replace(' ', '')
    hwconfig_fname  = "hwconfig_" + fname + ".txt"
    swconfig_fname  = "swconfig_" + fname + ".json"
    
    swconfig_builder.parameters["fpath_hwconfig"] = target_dirpath_config + hwconfig_fname  # save path of hwconfig on target
    hw_cfg_file.write(os.path.join(local_dirpath_save, hwconfig_fname))                     # save path of hwconfig on local
    swconfig_builder.write(os.path.join(local_dirpath_save, swconfig_fname))                # save path of swconfig on local

    target_swconfig_fpath.append(target_dirpath_config + swconfig_fname)

# Run file
fpath   = os.path.join(local_dirpath_save, "sweep.sh")
frun    = open(fpath, "w")
for i in range(NB_SWEEPS):
    frun.write("/home/ubuntu/software/app/snn_hh/deactivate.sh" + "\n")
    frun.write("/home/ubuntu/software/app/snn_hh/activate.sh" + "\n")
    frun.write("sudo /home/ubuntu/software/app/snn_hh/build/snn_hh.out --fpath-swconfig " + target_swconfig_fpath[i] + "\n")