# -*- coding: utf-8 -*-
# @title      Emulate SNN behavior
# @file       SnnEmulator.py
# @author     Romain Beaubois
# @date       23 Oct 2023
# @copyright
# SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief
# 
# @details
# > **23 Oct 2023** : file creation (RB)

import numpy as np
from tqdm import tqdm
from fxpmath import Fxp

from configuration.file_managers.HwConfigFile import *
from configuration.file_managers.SwConfigFile import *

from configuration.neurons.Hhparam   import *
from configuration.neurons.Ionrates  import RATE_VMIN, RATE_VMAX, RATE_STEP, RATE_TABLE_SIZE
from configuration.neurons.Ionrates  import Pospischil
from configuration.synapses.Synapses import *
from configuration.utility.Utility   import SFI

SPK_THREHSOLD = -10.0 # Spike detection threshold for spikes (mV)
FP_ID   = 0
SFI_ID  = 1
CODING  = SFI_ID

class SnnEmulator:
    def __init__(self, hwconfig:HwConfigFile, swconfig:SwConfigFile, store_context:bool, dtype=np.float64) -> None:
        """Initialize emulator from hardware config file
        :param HwConfigFile hwconfig: Hardware configuration file generated for FPGA
        :param int run_time_ms: Emulatior duration in ms
        :param int stim_delay_ms: Delay of stimulation insertion in ms
        :param int stim_dur_ms: Duration of stimulation in ms
        """
        self.hwconfig = hwconfig
        self.swconfig = swconfig

        self.dt     = hwconfig.dt
        self.nb_nrn = hwconfig.nb_nrn

        self.time_ms = swconfig.parameters['emulation_time_s']*1e3
        self.t       = np.linspace(1, self.time_ms/self.dt, int(self.time_ms/self.dt))
        
        self.en_stim     = swconfig.parameters['en_stim']
        self.stim_del_ms = [swconfig.parameters['stim_delay_ms']]    * self.nb_nrn
        self.stim_dur_ms = [swconfig.parameters['stim_duration_ms']] * self.nb_nrn

        self.STORE_CONTEXT = store_context
        self.spk_tab = []
        self.dtype = dtype

        # Declare variables
        self.v              = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
        self.detect         = np.zeros( self.nb_nrn, dtype=np.bool8)
        
        self.mprev_Na       = np.zeros( self.nb_nrn, dtype=dtype )
        self.mprev_K        = np.zeros( self.nb_nrn, dtype=dtype )
        self.mprev_M        = np.zeros( self.nb_nrn, dtype=dtype )
        self.mprev_L        = np.zeros( self.nb_nrn, dtype=dtype )
        self.mprev_T        = np.zeros( self.nb_nrn, dtype=dtype )
        self.hprev_Na       = np.zeros( self.nb_nrn, dtype=dtype )
        self.hprev_L        = np.zeros( self.nb_nrn, dtype=dtype )
        self.hprev_T        = np.zeros( self.nb_nrn, dtype=dtype )
        self.iprev_noise    = np.zeros( self.nb_nrn, dtype=dtype )

        self.g_Na        = np.zeros( self.nb_nrn, dtype=dtype )
        self.g_K         = np.zeros( self.nb_nrn, dtype=dtype )
        self.g_M         = np.zeros( self.nb_nrn, dtype=dtype )
        self.g_L         = np.zeros( self.nb_nrn, dtype=dtype )
        self.g_T         = np.zeros( self.nb_nrn, dtype=dtype )
        self.g_Leak      = np.zeros( self.nb_nrn, dtype=dtype )
        self.e_Na        = np.zeros( self.nb_nrn, dtype=dtype )
        self.e_K         = np.zeros( self.nb_nrn, dtype=dtype )
        self.e_Ca        = np.zeros( self.nb_nrn, dtype=dtype )
        self.e_Leak      = np.zeros( self.nb_nrn, dtype=dtype )
        self.i_stim      = np.zeros( self.nb_nrn, dtype=dtype )
        self.v_init      = np.zeros( self.nb_nrn, dtype=dtype )
        self.noise_offs  = np.zeros( self.nb_nrn, dtype=dtype )
        self.pmul_theta  = np.zeros( self.nb_nrn, dtype=dtype )
        self.pmul_sigma  = np.zeros( self.nb_nrn, dtype=dtype )
        self.pmul_gsyn   = np.zeros( self.nb_nrn, dtype=dtype )

        self.rprev_ampa     = np.zeros( self.nb_nrn, dtype=dtype )
        self.rprev_nmda     = np.zeros( self.nb_nrn, dtype=dtype )
        self.rprev_gabaa    = np.zeros( self.nb_nrn, dtype=dtype )
        self.rprev_gabab    = np.zeros( self.nb_nrn, dtype=dtype )
        self.sprev_gabab    = np.zeros( self.nb_nrn, dtype=dtype )
        
        self.rnew_ampa      = np.zeros( self.nb_nrn, dtype=dtype )
        self.rnew_nmda      = np.zeros( self.nb_nrn, dtype=dtype )
        self.rnew_gabaa     = np.zeros( self.nb_nrn, dtype=dtype )
        self.rnew_gabab     = np.zeros( self.nb_nrn, dtype=dtype )
        self.snew_gabab     = np.zeros( self.nb_nrn, dtype=dtype )

        if self.STORE_CONTEXT:
            self.mNa        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.hNa        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.mK         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.mM         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.mL         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.hL         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.mT         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.hT         = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)

            self.i_noise    = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_Na       = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_K        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_M        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_L        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_T        = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_Leak     = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.i_syn      = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)

            self.r_ampa     = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.r_nmda     = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.r_gabaa    = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.r_gabab    = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.s_gabab    = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)
            self.Bv_nmda    = np.zeros( [self.nb_nrn, len(self.t)], dtype=dtype)

        pid = Hhparam().getDict()
        for nid in range(self.nb_nrn):
            # Fetch hhparameters for all neurons
            self.g_Na[nid]        = hwconfig.HH_param[nid][pid["G_Na"]]
            self.g_K[nid]         = hwconfig.HH_param[nid][pid["G_Kd"]]
            self.g_M[nid]         = hwconfig.HH_param[nid][pid["G_M"]]
            self.g_L[nid]         = hwconfig.HH_param[nid][pid["G_L"]]
            self.g_T[nid]         = hwconfig.HH_param[nid][pid["G_T"]]
            self.g_Leak[nid]      = hwconfig.HH_param[nid][pid["G_Leak"]]
            self.e_Na[nid]        = hwconfig.HH_param[nid][pid["E_Na"]]
            self.e_K[nid]         = hwconfig.HH_param[nid][pid["E_K"]]
            self.e_Ca[nid]        = hwconfig.HH_param[nid][pid["E_Ca"]]
            self.e_Leak[nid]      = hwconfig.HH_param[nid][pid["E_Leak"]]
            self.i_stim[nid]      = hwconfig.HH_param[nid][pid["i_stim"]]
            self.v_init[nid]      = hwconfig.HH_param[nid][pid["v_init"]]
            self.noise_offs[nid]  = hwconfig.HH_param[nid][pid["noise_offs"]]
            self.pmul_theta[nid]  = hwconfig.HH_param[nid][pid["pmul_theta"]]
            self.pmul_sigma[nid]  = hwconfig.HH_param[nid][pid["pmul_sigma"]]
            self.pmul_gsyn[nid]   = hwconfig.HH_param[nid][pid["pmul_gsyn"]]
 
        # Initial conditions
        for nid in range(self.nb_nrn):
            self.v[nid][0]      = self.v_init[nid]

            self.mprev_Na[nid]  = 0.01
            self.mprev_K[nid]   = 0.01
            self.mprev_M[nid]   = 0.01
            self.mprev_L[nid]   = 0.01
            self.mprev_T[nid]   = 0.01

            self.hprev_Na[nid]  = 0.99
            self.hprev_L[nid]   = 0.99
            self.hprev_T[nid]   = 0.99

        if self.STORE_CONTEXT:
            self.mNa[nid][0] = self.mprev_Na[nid]
            self.mK[nid][0]  = self.mprev_K[nid]
            self.mM[nid][0]  = self.mprev_M[nid]
            self.mL[nid][0]  = self.mprev_L[nid]
            self.mT[nid][0]  = self.mprev_T[nid]

            self.hNa[nid][0] = self.hprev_Na[nid]
            self.hL[nid][0]  = self.hprev_L[nid]
            self.hT[nid][0]  = self.hprev_T[nid]

        self.wsyn = hwconfig.wsyn
        self.tsyn = hwconfig.tsyn

    def run(self, nlist, FPGA_EMU:bool=False):
        """Running simulation from hardware configuration package

        This version is saving intermediate variables for later analysis.
        
        :param list nlist: Number of neurons to compute (if synapses used, has to include all neurons included)
        """

        for i in tqdm(range(len(self.t)-1)):
            for n in nlist:
                # Coding vprev/mprev
                v           = self.v[n][i]
                
                mprev_Na    = self.mprev_Na[n]
                mprev_K     = self.mprev_K[n]
                mprev_M     = self.mprev_M[n]
                mprev_L     = self.mprev_L[n]
                mprev_T     = self.mprev_T[n]
                
                hprev_Na    = self.hprev_Na[n]
                hprev_L     = self.hprev_L[n]
                hprev_T     = self.hprev_T[n]

                # Ionic channels states
                if FPGA_EMU:
                    addr    = round(abs(v - RATE_VMIN) / RATE_STEP)

                    if addr < 0:
                        addr = 0
                    elif addr >  RATE_TABLE_SIZE-1:
                        addr =  RATE_TABLE_SIZE-1

                    # Load rate table
                    mNa_r1  = self.dtype(self.hwconfig.m_rates1[0][addr])
                    mNa_r2  = self.dtype(self.hwconfig.m_rates2[0][addr])
                    hNa_r1  = self.dtype(self.hwconfig.h_rates1[0][addr])
                    hNa_r2  = self.dtype(self.hwconfig.h_rates2[0][addr])
                    mK_r1   = self.dtype(self.hwconfig.m_rates1[1][addr])
                    mK_r2   = self.dtype(self.hwconfig.m_rates2[1][addr])
                    mM_r1   = self.dtype(self.hwconfig.m_rates1[2][addr])
                    mM_r2   = self.dtype(self.hwconfig.m_rates2[2][addr])
                    mL_r1   = self.dtype(self.hwconfig.m_rates1[3][addr])
                    mL_r2   = self.dtype(self.hwconfig.m_rates2[3][addr])
                    hL_r1   = self.dtype(self.hwconfig.h_rates1[3][addr])
                    hL_r2   = self.dtype(self.hwconfig.h_rates2[3][addr])
                    mT_r1   = self.dtype(self.hwconfig.m_rates1[4][addr])
                    mT_r2   = self.dtype(self.hwconfig.m_rates2[4][addr])
                    hT_r1   = self.dtype(self.hwconfig.h_rates1[4][addr])
                    hT_r2   = self.dtype(self.hwconfig.h_rates2[4][addr])
    
                    mnew_Na = mNa_r1 * mprev_Na  +  mNa_r2
                    hnew_Na = hNa_r1 * hprev_Na  +  hNa_r2
                    mnew_K  = mK_r1  * mprev_K   +  mK_r2
                    mnew_M  = mM_r1  * mprev_M   +  mM_r2
                    mnew_L  = mL_r1  * mprev_L   +  mL_r2
                    hnew_L  = hL_r1  * hprev_L   +  hL_r2
                    mnew_T  = mT_r1  * mprev_T   +  mT_r2
                    hnew_T  = hT_r1  * hprev_T   +  hT_r2
                else:
                    # TODO: add generic emulation for the current equations
                    mnew_Na = Pospischil().calc_m_Na(v, mprev_Na, self.dt)
                    mnew_K  = Pospischil().calc_m_K( v, mprev_K,  self.dt)
                    mnew_M  = Pospischil().calc_m_M( v, mprev_M,  self.dt)
                    mnew_L  = Pospischil().calc_m_L( v, mprev_L,  self.dt)
                    mnew_T  = Pospischil().calc_m_T( v, mprev_T,  self.dt)
                    
                    hnew_Na = Pospischil().calc_h_Na(v, hprev_Na, self.dt)
                    hnew_L  = Pospischil().calc_h_L( v, hprev_L,  self.dt)
                    hnew_T  = Pospischil().calc_h_T( v, hprev_T,  self.dt)
                
                # Coding parameters
                if FPGA_EMU:
                    g_Na        = self.g_Na[n]
                    g_K         = self.g_K[n]
                    g_M         = self.g_M[n]
                    g_L         = self.g_L[n]
                    g_T         = self.g_T[n]
                    g_Leak      = self.g_Leak[n]
                    e_Na        = self.e_Na[n]
                    e_K         = self.e_K[n]
                    e_Ca        = self.e_Ca[n]
                    e_Leak      = self.e_Leak[n]

                    i_stim      = Fxp(self.i_stim[n],       signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    noise_offs  = Fxp(self.noise_offs[n],   signed=True, n_word=SFI.MU.WIDTH,        n_frac=SFI.MU.DEC)
                    pmul_theta  = Fxp(self.pmul_theta[n],   signed=True, n_word=SFI.THETA.WIDTH,     n_frac=SFI.THETA.DEC)
                    pmul_sigma  = Fxp(self.pmul_sigma[n],   signed=True, n_word=SFI.SIGMA.WIDTH,     n_frac=SFI.SIGMA.DEC)
                    pmul_gsyn   = Fxp(self.pmul_gsyn[n],    signed=True, n_word=SFI.PMUL_GSYN.WIDTH, n_frac=SFI.PMUL_GSYN.DEC)
                    iprev_noise = Fxp(self.iprev_noise[n],  signed=True, n_word=SFI.CUR_TRUNC.WIDTH, n_frac=SFI.CUR_TRUNC.DEC)
                    rand_val    = Fxp(np.random.randn(),    signed=True, n_word=SFI.THETA.WIDTH,     n_frac=SFI.THETA.DEC)
                else:
                    g_Na        = self.g_Na[n]
                    g_K         = self.g_K[n]
                    g_M         = self.g_M[n]
                    g_L         = self.g_L[n]
                    g_T         = self.g_T[n]
                    g_Leak      = self.g_Leak[n]
                    e_Na        = self.e_Na[n]
                    e_K         = self.e_K[n]
                    e_Ca        = self.e_Ca[n]
                    e_Leak      = self.e_Leak[n]
                    i_stim      = self.i_stim[n]
                    noise_offs  = self.noise_offs[n]
                    pmul_theta  = self.pmul_theta[n]
                    pmul_sigma  = self.pmul_sigma[n]
                    pmul_gsyn   = self.pmul_gsyn[n]
                    iprev_noise = self.iprev_noise[n]
                    rand_val    = np.random.randn()

                # Calculate currents (from mnew or mprev)
                if True:
                    i_Na       = g_Na * (mnew_Na*mnew_Na*mnew_Na) * hnew_Na * (v - e_Na)
                    i_K        = g_K  * (mnew_K*mnew_K*mnew_K*mnew_K)  * (v - e_K)
                    i_M        = g_M  * mnew_M     * (v - e_K)
                    i_L        = g_L  * (mnew_L*mnew_L)  * hnew_L * (v - e_Ca)
                    i_T        = g_T  * (mnew_T*mnew_T)  * hnew_T * (v - e_Ca)
                    i_Leak     = g_Leak  * (v - e_Leak)
                    i_noise    = iprev_noise + noise_offs + pmul_theta*iprev_noise + pmul_sigma*rand_val
                else:
                    i_Na       = g_Na * (mprev_Na*mprev_Na*mprev_Na) * hnew_Na * (v - e_Na)
                    i_K        = g_K  * (mprev_K*mprev_K*mprev_K*mprev_K)  * (v - e_K)
                    i_M        = g_M  * mprev_M     * (v - e_K)
                    i_L        = g_L  * (mprev_L*mprev_L)  * hnew_L * (v - e_Ca)
                    i_T        = g_T  * (mprev_T*mprev_T)  * hnew_T * (v - e_Ca)
                    i_Leak     = g_Leak  * (v - e_Leak)
                    i_noise    = iprev_noise + noise_offs + pmul_theta*iprev_noise + pmul_sigma*rand_val

                # Calulate synaptic current
                i_syn = 0
                for npre in nlist:
                    # TODO : add syn emulation
                    # if FPGA_EMU and SFI_CODING:
                    #     v_npre  = Fxp(self.v[npre][i],    signed=True, n_word=SFI.V.WIDTH, n_frac=SFI.V.DEC)
                    #     wsyn    = Fxp(self.wsyn[n][npre], signed=True, n_word=14,          n_frac=12) # TODO: check coding
                    # else:
                    v_npre = self.v[npre][i]
                    wsyn    = self.wsyn[n][npre]
                    # pmul_gsyn = pmul_gsyn.astype(float)
                    
                    if   self.tsyn[n][npre] == "ampa":
                        [i_syn_it, self.rnew_ampa[npre]]  = Synapses().destexhe.calcISynAmpa( v_npre, v, self.rprev_ampa[npre],  wsyn*pmul_gsyn, self.dt)
                    elif self.tsyn[n][npre] == "gabaa":
                        [i_syn_it, self.rnew_gabaa[npre]] = Synapses().destexhe.calcISynGabaa(v_npre, v, self.rprev_gabaa[npre], wsyn*pmul_gsyn, self.dt)
                    elif self.tsyn[n][npre] == "nmda":
                        [i_syn_it, self.rnew_nmda[npre]]  = Synapses().destexhe.calcISynNmda( v_npre, v, self.rprev_nmda[npre],  wsyn*pmul_gsyn, self.dt)
                    elif self.tsyn[n][npre] == "gabab":
                        [i_syn_it, self.snew_gabab[npre], self.rnew_gabab[npre]] = Synapses().destexhe.calcISynGabab(v_npre, v, self.sprev_gabab[npre], self.rprev_gabab[npre], wsyn*pmul_gsyn, self.dt)
                    else:
                        i_syn_it = 0
                    
                    i_syn += i_syn_it
                
                if self.STORE_CONTEXT:
                    self.r_ampa[:,  i+1]  = self.rnew_ampa
                    self.r_nmda[:,  i+1]  = self.rnew_nmda
                    self.r_gabaa[:, i+1]  = self.rnew_gabaa
                    self.r_gabab[:, i+1]  = self.rnew_gabab
                    self.s_gabab[:, i+1]  = self.snew_gabab

                    for npre in nlist:
                        self.Bv_nmda[npre, i+1]       = Synapses().destexhe.B_v(v)

                    if FPGA_EMU:
                        self.i_syn[n][i+1] = i_syn
                        # self.i_syn[n][i+1] = i_syn.astype(float)
                    else:
                        self.i_syn[n][i+1] = i_syn

                # Insert stimulation
                if (self.t[i] > (self.stim_del_ms[n]/self.dt)) and (self.t[i] < ((self.stim_del_ms[n]+self.stim_dur_ms[n])/self.dt)) and self.en_stim:
                    i_stim = i_stim
                else:
                    if FPGA_EMU:
                        i_stim = Fxp(0, signed=True, n_word=SFI.CUR.WIDTH, n_frac=SFI.CUR.DEC)
                    else:
                        i_stim = 0

                # Calculate new membrane voltage
                if FPGA_EMU: # TODO : add fpga sfi emulation of synapses
                    sfi_i_Na        = Fxp(i_Na,    signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_K         = Fxp(i_K,     signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_M         = Fxp(i_M,     signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_L         = Fxp(i_L,     signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_T         = Fxp(i_T,     signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_Leak      = Fxp(i_Leak,  signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_v           = Fxp(v,       signed=True, n_word=SFI.V.WIDTH,         n_frac=SFI.V.DEC)
                    
                    sfi_i_noise     = Fxp(i_noise,  signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_stim      = Fxp(i_stim,   signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)
                    sfi_i_syn       = Fxp(i_syn,    signed=True, n_word=SFI.CUR.WIDTH,       n_frac=SFI.CUR.DEC)

                    dV              = sfi_i_Na + sfi_i_K + sfi_i_M + sfi_i_L + sfi_i_T + sfi_i_Leak - sfi_i_noise - sfi_i_stim + sfi_i_syn
                    vnew            = sfi_v - dV
                else:
                    dV              = i_Na + i_K + i_M + i_L + i_T + i_Leak - i_noise - i_stim + i_syn
                    vnew            = v - dV

                if FPGA_EMU:
                    self.v[n][i+1]  = vnew.astype(float)
                else:
                    self.v[n][i+1]  = vnew

                # Detection for raster plot
                if (vnew > SPK_THREHSOLD) and (self.detect[n]==False):
                    self.spk_tab.append([i+1, n])
                    self.detect[n] = True
                elif (vnew < SPK_THREHSOLD) and (self.detect[n]==True):
                    self.detect[n] = False

                # Update previous values
                self.rprev_ampa     = self.rnew_ampa
                self.rprev_nmda     = self.rnew_nmda
                self.rprev_gabaa    = self.rnew_gabaa
                self.rprev_gabab    = self.rnew_gabab
                self.sprev_gabab    = self.snew_gabab

                self.mprev_Na[n] = mnew_Na
                self.mprev_K[n]  = mnew_K
                self.mprev_M[n]  = mnew_M
                self.mprev_L[n]  = mnew_L
                self.mprev_T[n]  = mnew_T
            
                self.hprev_Na[n] = hnew_Na
                self.hprev_L[n]  = hnew_L
                self.hprev_T[n]  = hnew_T

                self.iprev_noise[n] = i_noise

                # Store context
                if self.STORE_CONTEXT:
                    self.mNa[n][i+1]        = mnew_Na
                    self.hNa[n][i+1]        = hnew_Na
                    self.mK[n][i+1]         = mnew_K
                    self.mM[n][i+1]         = mnew_M
                    self.mL[n][i+1]         = mnew_L
                    self.hL[n][i+1]         = hnew_L
                    self.mT[n][i+1]         = mnew_T
                    self.hT[n][i+1]         = hnew_T
                    
                    self.i_Na[n][i+1]       = i_Na
                    self.i_K[n][i+1]        = i_K
                    self.i_M[n][i+1]        = i_M
                    self.i_L[n][i+1]        = i_L
                    self.i_T[n][i+1]        = i_T
                    self.i_Leak[n][i+1]     = i_Leak
                    self.i_noise[n][i+1]    = i_noise

        return [self.t, self.v, self.spk_tab]