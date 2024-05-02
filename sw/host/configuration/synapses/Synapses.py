# -*- coding: utf-8 -*-
# @title      Generate parameters related to synapses
# @file       Synapses.py
# @author     Romain Beaubois
# @date       05 Dec 2022
# @copyright
# SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Generate parameters related to synapses
# * for now only synapse model available is Destexhe
#
# @details
# > **05 Dec 2022** : file creation (RB)

from math import exp, ceil, pi, tanh, cosh
import numpy as np
from numpy import linspace
from configuration.utility.Utility import writeFPGASimFile

# Dictionnary of available synapses and coding
SYN_TYPE = {
    "destexhe_ampa"     : "ampa",
    "destexhe_nmda"     : "nmda",
    "destexhe_gabaa"    : "gabaa",
    "destexhe_gabab"    : "gabab",
    "destexhe_none"     : "x"
}

class Synapses:
    def __init__(self) -> None:
        """Initialize"""
        self.destexhe = Destexhe()
        pass

    def getDict(self):
        """Get dictionnary of synapses types"""
        return SYN_TYPE

    def getDepthSynRates(self, syn_model:str):
        """Get depth of synaptic rates table"""
        if syn_model == "destexhe":
            return self.destexhe.getDepthSynRates()

    def getSynRates(self, syn_model:str, gen_fpga_sim_files=False):
        """Get synaptic rates table"""
        if syn_model == "destexhe":
            return self.destexhe.getSynRates(gen_fpga_sim_files)

    def getGsyn(self, tsyn:str):
        """Get synaptic conductance depending on type and convert to surface conductivity"""
        [syn_model, syn_type] = tsyn.split('_')
        if syn_model == "destexhe":
            return self.destexhe.getGsyn(syn_type)
    
    def getPsyn(self, syn_model:str, dt):
        """Get synaptic conductance depending on type and convert to surface conductivity"""
        if syn_model == "destexhe":
            return self.destexhe.getPsyn(dt)

class Destexhe:
    PID= {
        "AMPA_K1"       :  0,
        "AMPA_K2"       :  1,
        "AMPA_Gsyn"     :  2,
        "AMPA_Esyn"     :  3,
        "NMDA_K1"       :  4,
        "NMDA_K2"       :  5,
        "NMDA_Gsyn"     :  6,
        "NMDA_Esyn"     :  7,
        "GABAa_K1"      :  8,
        "GABAa_K2"      :  9,
        "GABAa_Gsyn"    : 10,
        "GABAa_Esyn"    : 11,
        "GABAb_K1"      : 12,
        "GABAb_K2"      : 13,
        "GABAb_K3"      : 14,
        "GABAb_K4"      : 15,
        "GABAb_Gsyn"    : 16,
        "GABAb_Esyn"    : 17
    }
    NB_PSYN  = len(PID) # Kd et n excluded

    psyn = [0.0]*NB_PSYN
    # USER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    psyn[PID["AMPA_K1"]]    = 1.1e6 *1e-6   # [1/(mM.ms)]
    psyn[PID["AMPA_K2"]]    = 190   *1e-3   # [1/ms]
    psyn[PID["AMPA_Gsyn"]]  = 0.35          # 0.35 to 1.0 [nS]
    psyn[PID["AMPA_Esyn"]]  = 0.0           # [mV]
    psyn[PID["NMDA_K1"]]    = 7.2e4 *1e-6   # [1/(mM.ms)]
    psyn[PID["NMDA_K2"]]    = 6.6   *1e-3   # [1/sec]
    psyn[PID["NMDA_Gsyn"]]  = 0.30          # 0.01 to 0.6 [nS]
    psyn[PID["NMDA_Esyn"]]  = 0.0           # [mV]
    psyn[PID["GABAa_K1"]]   = 5e6 *1e-6     # [1/(mM.ms)]
    psyn[PID["GABAa_K2"]]   = 180 *1e-3     # [1/sec]
    psyn[PID["GABAa_Gsyn"]] = 0.25          # 0.25 to 1.2 [nS]
    psyn[PID["GABAa_Esyn"]] = -80.0         # [mV]
    psyn[PID["GABAb_K1"]]   = 9e4   * 1e-6  # [1/(mM.ms)]
    psyn[PID["GABAb_K2"]]   = 1.2   * 1e-3  # [1/ms]
    psyn[PID["GABAb_K3"]]   = 180   * 1e-3  # [1/ms]
    psyn[PID["GABAb_K4"]]   = 34    * 1e-3  # [1/ms]
    psyn[PID["GABAb_Gsyn"]] = 1.00          # 1.0 [nS]
    psyn[PID["GABAb_Esyn"]] = -95           # [mV]
    psyn_GABAb_Kd           = 100           #
    psyn_GABAb_n            = 4             # nb binding sites
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    def __init__(self) -> None:
        """Initialize destexhe synapses"""
        self.SYNRATE_VMIN               = -76.0
        self.SYNRATE_VMAX               = 52.0
        self.SYNRATE_DEPTH              = 2048  # 1 BRAM
        self.SYNRATE_STEP               = abs(self.SYNRATE_VMIN - self.SYNRATE_VMAX)/self.SYNRATE_DEPTH
        self.SYNRATE_FP_WIDTH_BV        = 12
        self.SYNRATE_FP_WIDTH_TV        = 18
        self.SYNRATE_FP_DEC_BV          = 10
        self.SYNRATE_FP_DEC_TV          = 16

        # s not sn
        self.TABLE_SN_GABAB_MIN         = 0.0
        self.TABLE_SN_GABAB_MAX         = 8.0 # real max (if r = 1) is ~5.3
        self.TABLE_SN_GABAB_DEPTH       = 2048
        self.TABLE_SN_GABAB_STEP        = abs(self.TABLE_SN_GABAB_MIN - self.TABLE_SN_GABAB_MAX)/self.TABLE_SN_GABAB_DEPTH
        self.TABLE_SN_GABAB_FP_WIDTH    = 18
        self.TABLE_SN_GABAB_FP_DEC      = 14

        self.g_nS_AMPA   = self.psyn[self.PID["AMPA_Gsyn"]]
        self.g_nS_NMDA   = self.psyn[self.PID["NMDA_Gsyn"]]
        self.g_nS_GABAa  = self.psyn[self.PID["GABAa_Gsyn"]]
        self.g_nS_GABAb  = self.psyn[self.PID["GABAb_Gsyn"]]

    # Synaptic rates #########################################
    def T_v(self, v):
        """Calculate T for destexhe synapses"""
        T_max = 1.0
        K_p = 5
        V_p = 2
        return T_max/(1+exp(-(v-V_p)/K_p))

    def B_v(self, v):
        """Calculate B for destexhe synapses"""
        mg2 = 1 # mM
        return 1/(1+exp(-0.062*v)*(mg2/3.57))

    def Sn_GABAb(self, s):
        n   = self.psyn_GABAb_n
        Kd  = self.psyn_GABAb_Kd
        return s**n/(s**n + Kd)

    def getDepthSynRates(self):
        """Get depth of synaptic rate tables"""
        return self.SYNRATE_DEPTH

    def getSynRates(self, gen_fpga_sim_files:bool):
        """Get synaptic rate tables"""
        l_Bv, l_Tv, synrates = ([] for i in range(3))
        l_gabab_sn = []
        v_ramp = linspace(      self.SYNRATE_VMIN,       self.SYNRATE_VMAX,        self.SYNRATE_DEPTH)
        s_ramp = linspace(self.TABLE_SN_GABAB_MIN, self.TABLE_SN_GABAB_MAX, self.TABLE_SN_GABAB_DEPTH)

        for v in v_ramp:
            l_Bv.append(self.B_v(v))
            l_Tv.append(self.T_v(v))

        for s in s_ramp:
            l_gabab_sn.append(self.Sn_GABAb(s))

        writeFPGASimFile(gen_fpga_sim_files, "rate_Bv.txt",             l_Bv, len(v_ramp),        self.SYNRATE_FP_WIDTH_BV, self.SYNRATE_FP_DEC_BV)
        writeFPGASimFile(gen_fpga_sim_files, "rate_Tv.txt",             l_Tv, len(v_ramp),        self.SYNRATE_FP_WIDTH_TV, self.SYNRATE_FP_DEC_TV)
        writeFPGASimFile(gen_fpga_sim_files, "rate_sn_gabab.txt", l_gabab_sn, len(s_ramp), self.TABLE_SN_GABAB_FP_WIDTH, self.TABLE_SN_GABAB_FP_DEC)

        synrates.append(l_Bv)
        synrates.append(l_Tv)
        synrates.append(l_gabab_sn)

        return synrates

    # Synaptic currents #########################################
    def getPsyn(self, dt):
        ret_psyn = self.psyn
        ret_psyn[self.PID["GABAb_K3"]] *= dt
        ret_psyn[self.PID["GABAb_K4"]] *= dt
        return ret_psyn

    def getGsyn(self, tsyn:str):
        """Get synaptic conductance depending on type"""
        if   tsyn == "ampa":
            gsyn = (self.g_nS_AMPA)
        elif tsyn == "nmda":
            gsyn = (self.g_nS_NMDA)
        elif tsyn == "gabaa":
            gsyn = (self.g_nS_GABAa)
        elif tsyn == "gabab":
            gsyn = (self.g_nS_GABAb)
        elif tsyn == "none":
            gsyn = 0.0
        else:
            Warning("Unkown synapse type")
            return 0.0

        return gsyn

    def rcalc(self, rprev, A, B, T, dt):
        """Calculate intermediate r for synapses"""
        dr = A * T * (1-rprev) - B*rprev
        return rprev + dr * dt

    def scalc(self, sprev, rprev, K3, K4, dt):
        """Calculate intermediate s for synapses"""
        ds = K3 * rprev - K4*sprev
        return sprev + ds * dt

    def calcISynAmpa(self, vpre, vpost, rprev, wsyn, dt):
        """Calculate synaptic current for AMPA receptor"""
        A       = self.psyn[self.PID["AMPA_K1"]]
        B       = self.psyn[self.PID["AMPA_K2"]]
        Esyn    = self.psyn[self.PID["AMPA_Esyn"]]
        gsyn    = self.psyn[self.PID["AMPA_Gsyn"]]

        rnew = self.rcalc(rprev, A, B, self.T_v(vpre), dt)
        isyn = wsyn * gsyn * rnew * (vpost - Esyn)
        return [isyn, rnew]

    def calcISynNmda(self, vpre, vpost, rprev, wsyn, dt):
        """Calculate synaptic current for NDMA receptor"""
        A       = self.psyn[self.PID["NMDA_K1"]]
        B       = self.psyn[self.PID["NMDA_K2"]]
        Esyn    = self.psyn[self.PID["NMDA_Esyn"]]
        gsyn    = self.psyn[self.PID["NMDA_Gsyn"]]
        rnew = self.rcalc(rprev, A, B, self.T_v(vpre), dt)
        isyn = wsyn * gsyn * self.B_v(vpost) * rnew * (vpost - Esyn)
        return [isyn, rnew]

    def calcISynGabaa(self, vpre, vpost, rprev, wsyn, dt):
        """Calculate synaptic current for GABAa receptor"""
        A       = self.psyn[self.PID["GABAa_K1"]]
        B       = self.psyn[self.PID["GABAa_K2"]]
        Esyn    = self.psyn[self.PID["GABAa_Esyn"]]
        gsyn    = self.psyn[self.PID["GABAa_Gsyn"]]
        rnew = self.rcalc(rprev, A, B, self.T_v(vpre), dt)
        isyn = wsyn * gsyn * rnew * (vpost - Esyn)
        return [isyn, rnew]

    def calcISynGabab(self, vpre, vpost, sprev, rprev, wsyn, dt):
        """Calculate synaptic current for GABAb receptor"""
        K1      = self.psyn[self.PID["GABAb_K1"]]
        K2      = self.psyn[self.PID["GABAb_K2"]]
        K3      = self.psyn[self.PID["GABAb_K3"]]
        K4      = self.psyn[self.PID["GABAb_K4"]]
        Kd      = self.psyn_GABAb_Kd
        Esyn    = self.psyn[self.PID["GABAb_Esyn"]]
        gsyn    = self.psyn[self.PID["GABAb_Gsyn"]]
        n       = self.psyn_GABAb_n
        rnew = self.rcalc(rprev, K1, K2, self.T_v(vpre), dt)
        snew = self.scalc(sprev, rprev, K3, K4, dt)
        isyn = wsyn * gsyn * (snew**n)/(snew**n + Kd) * (vpost - Esyn)
        return [isyn, snew, rnew]

# class Hill:
#     PID= {
#         "gSynS"          :  18,
#         "ESynS"          :  19
#     }
#     NB_PSYN  = len(PID)

#     psyn = [0.0]*NB_PSYN
#     psyn[PID["gSynS"]] = 0.25          # 0.25 to 1.2 [nS]
#     psyn[PID["ESynS"]] = 0.25          # 0.25 to 1.2 [nS]

#     def __init__(self):
#         self.SYNRATE_VMIN               = -76.0
#         self.SYNRATE_VMAX               = 52.0
#         self.SYNRATE_DEPTH              = 2048  # 1 BRAM
#         self.SYNRATE_STEP               = abs(self.SYNRATE_VMIN - self.SYNRATE_VMAX)/self.SYNRATE_DEPTH
#         self.SYNRATE_FP_WIDTH_MV        = 18
#         self.SYNRATE_FP_INT_MV          = 1  # sign
#         self.SYNRATE_FP_DEC_MV          = self.SYNRATE_FP_WIDTH_MV - self.SYNRATE_FP_INT_MV

#         self.g_nS_synS = self.psyn[self.PID["GsynS"]]

#     def Minf(v):
#         return 0.1 + 0.9 / (1 + np.exp(-1000*(v+0.04)))

#     def dM(self, v, Mprev):
#         return (self.Minf(v) - Mprev) / 0.2

#     def Mcalc(self, v, Mprev, dt):
#         # Minf = 0.1 + 0.9 / (1 + np.exp(-1000*(v+0.04)))
#         # dM = (Minf - Mprev) / 0.2
#         return Mprev + dt * self.dM(v, Mprev)

#     def fsynS(t):
#         tau_1 = 0.055
#         tau_2 = 0.01
#         tpeak = tau_1*tau_2 * np.log(tau_1/tau_2) / (tau_1 - tau_2)

#         return (1/(np.exp(-tpeak/tau_1) - np.exp(-tpeak/tau_2))) * (np.exp(-t/tau_1) - np.exp(-t/tau_2))
    
#     def calcISynS(self, vpre, vpost, mprev, wsyn, dt):

#         mnew = Mcalc(v, mprev)
#         isyn = wsyn * gsyn * (vpost - Esyn)
#         return [isyn, mnew]
