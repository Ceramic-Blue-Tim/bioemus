# -*- coding: utf-8 -*-
# @title      Plot SNN emulation
# @file       SnnPlotter.py
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
import matplotlib.pyplot as plt
from configuration.file_managers.HwConfigFile import *
from configuration.neurons.Ionrates  import RATE_VMIN, RATE_VMAX, RATE_STEP, RATE_TABLE_SIZE
from emulation.hh_snn.SnnEmulator import *

class SnnPlotter:
    def __init__(self, snn_emu:SnnEmulator):
        self.snn_emu = snn_emu

    def plotIonRates(self):
            """Plot rate tables generated from ionic channel states"""

            v_ramp = np.linspace(RATE_VMIN, RATE_VMAX, RATE_TABLE_SIZE)
            fig, axs    = plt.subplots(self.snn_emu.hwconfig.nb_ionrate, 4, num="Ion channel rates")

            axs[0, 0].plot(v_ramp, self.snn_emu.hwconfig.m_rates1[0][:]); axs[0, 0].set_title("mNa_r1")
            axs[0, 1].plot(v_ramp, self.snn_emu.hwconfig.m_rates2[0][:]); axs[0, 1].set_title("mNa_r2")
            axs[0, 2].plot(v_ramp, self.snn_emu.hwconfig.h_rates1[0][:]); axs[0, 2].set_title("hNa_r1")
            axs[0, 3].plot(v_ramp, self.snn_emu.hwconfig.h_rates2[0][:]); axs[0, 3].set_title("hNa_r2")

            axs[1, 0].plot(v_ramp, self.snn_emu.hwconfig.m_rates1[1][:]); axs[1, 0].set_title("mK_r1")
            axs[1, 1].plot(v_ramp, self.snn_emu.hwconfig.m_rates2[1][:]); axs[1, 1].set_title("mK_r2")
            # axs[1, 2].plot(v_ramp, ones); axs[1, 2].set_title(" ")
            # axs[1, 3].plot(v_ramp, ones); axs[1, 3].set_title(" ")
                            
            axs[2, 0].plot(v_ramp, self.snn_emu.hwconfig.m_rates1[2][:]); axs[2, 0].set_title("mM_r1")
            axs[2, 1].plot(v_ramp, self.snn_emu.hwconfig.m_rates2[2][:]); axs[2, 1].set_title("mM_r2")
            # axs[2, 2].plot(v_ramp, ones); axs[2, 2].set_title(" ")
            # axs[2, 3].plot(v_ramp, ones); axs[2, 3].set_title(" ")

            axs[3, 0].plot(v_ramp, self.snn_emu.hwconfig.m_rates1[3][:]); axs[3, 0].set_title("mL_r1")
            axs[3, 1].plot(v_ramp, self.snn_emu.hwconfig.m_rates2[3][:]); axs[3, 1].set_title("mL_r2")
            axs[3, 2].plot(v_ramp, self.snn_emu.hwconfig.h_rates1[3][:]); axs[3, 2].set_title("hL_r1")
            axs[3, 3].plot(v_ramp, self.snn_emu.hwconfig.h_rates2[3][:]); axs[3, 3].set_title("hL_r2")

            axs[4, 0].plot(v_ramp, self.snn_emu.hwconfig.m_rates1[4][:]); axs[4, 0].set_title("mT_r1")
            axs[4, 1].plot(v_ramp, self.snn_emu.hwconfig.m_rates2[4][:]); axs[4, 1].set_title("mT_r2")
            axs[4, 2].plot(v_ramp, self.snn_emu.hwconfig.h_rates1[4][:]); axs[4, 2].set_title("hT_r1")
            axs[4, 3].plot(v_ramp, self.snn_emu.hwconfig.h_rates2[4][:]); axs[4, 3].set_title("hT_r2")
            # <<<
            fig.suptitle("Ion rates tables", fontsize=16)
            plt.show(block=False)

    def plotSynRates(self):
        """Plot synaptic rates generated for synapses"""

        syn     = Synapses()
        v_ramp  = np.linspace(syn.destexhe.SYNRATE_VMIN, syn.destexhe.SYNRATE_VMAX, syn.destexhe.SYNRATE_DEPTH)
        fig, axs    = plt.subplots(3, 1, num="Synaptic rates")

        for ax in axs:
            ax.grid()

        axs[0].plot(v_ramp, self.snn_emu.hwconfig.synrates[0][:]); axs[0].set_title("Bv", fontsize=16)
        axs[1].plot(v_ramp, self.snn_emu.hwconfig.synrates[1][:]); axs[1].set_title("Tv", fontsize=16)
        axs[2].plot(np.linspace(syn.destexhe.TABLE_SN_GABAB_MIN, syn.destexhe.TABLE_SN_GABAB_MAX, syn.destexhe.TABLE_SN_GABAB_DEPTH), self.snn_emu.hwconfig.synrates[2][:]); axs[2].set_title("s**n / (s**n + Kd)", fontsize=16)
        fig.suptitle("Syn rates tables", fontsize=16)
        # fig.tight_layout()
        plt.show(block=False)

    def plotIonChanStates(self, nid):
        if not(self.snn_emu.STORE_CONTEXT):
            print("plotIonChanStates() skipped: no emulation context")
        else:
            plt.figure("Ion Channel states N{}".format(nid))
            plt.subplot(911)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.v[nid][:])
            plt.ylim([-100, 70])
            plt.title("V_mem")

            plt.subplot(912)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.mNa[nid][:])
            plt.title("mNa")

            plt.subplot(913)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.hNa[nid][:])
            plt.title("hNa")

            plt.subplot(914)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.mK[nid][:])
            plt.title("mK")

            plt.subplot(915)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.mM[nid][:])
            plt.title("mM")
            
            plt.subplot(916)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.mL[nid][:])
            plt.title("mL")
            
            plt.subplot(917)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.hL[nid][:])
            plt.title("hL")

            plt.subplot(918)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.mT[nid][:])
            plt.title("mT")
            
            plt.subplot(919)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.hT[nid][:])
            plt.title("hT")

            plt.suptitle("Ion channel states", fontsize=16)
            plt.show(block=False)

    def plotCurrents(self, nid):
        if not(self.snn_emu.STORE_CONTEXT):
            print("plotIonCurrents() skipped: no emulation context")
        else:
            plt.figure("Ion currents N{}".format(nid))
            plt.subplot(811)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.v[nid][:])
            plt.ylim([-100, 70])
            plt.title("V_mem")

            plt.subplot(812)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_Na[nid][:])
            plt.title("i_Na")

            plt.subplot(813)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_K[nid][:])
            plt.title("i_K")

            plt.subplot(814)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_M[nid][:])
            plt.title("i_M")

            plt.subplot(815)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_T[nid][:])
            plt.title("i_L")
            
            plt.subplot(816)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_L[nid][:])
            plt.title("i_T")

            plt.subplot(817)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_Leak[nid][:])
            plt.title("i_Leak")

            plt.subplot(818)
            plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.i_noise[nid][:])
            plt.title("i_noise")

            plt.show(block=False)

    def plotRaster(self):
        """Plot raster of the spike detected"""
        plt.figure("Raster plot")
        plt.xlabel("Time (ms)")
        plt.ylabel("Neuron index")

        for [x, y] in self.snn_emu.spk_tab:
            plt.scatter(x/self.snn_emu.dt*1e-3, y, color="black", marker= ".", s=10)
        plt.show(block=False)

    def plotVmem(self, nlist, plot_type):
        if plot_type == "all":
            for nid in nlist:
                plt.figure("Membrane voltage N{}".format(nid))
                plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.v[nid][:])
                plt.xlabel("Time (ms)")
                plt.ylabel("Amplitude (mV)")
                plt.ylim([-100, 70])
                plt.title("V_mem N{}".format(nid))
                plt.show(block=False)

        elif plot_type == "comp":
            plt.figure("Membrane voltage")
            plt.xlabel("Time (ms)")
            plt.ylabel("Amplitude (mV)")
            plt.ylim([-100, 70])

            for nid in nlist:
                plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.v[nid][:])
            plt.legend(nlist)
            plt.suptitle("Compare membrane voltage", fontsize=16)
            plt.show(block=False)
        
        elif plot_type == "subplot":
            plt.figure("Membrane voltage")
            plt.xlabel("Time (ms)")
            plt.ylabel("Amplitude (mV)")
            plt.ylim([-100, 70])

            if len(nlist) < 1:
                return
            
            for i, nid in enumerate(nlist):
                if i == 0:
                    ax0 = plt.subplot(len(nlist), 1, nid+1)
                else:
                    plt.subplot(len(nlist), 1, nid+1, sharex = ax0)
                plt.plot(self.snn_emu.t/self.snn_emu.dt*1e-3, self.snn_emu.v[nid][:])
                # plt.grid()

            plt.legend(nlist)
            plt.suptitle("Compare membrane voltage", fontsize=16)
            plt.show(block=False)


    # def plot(self, nlist, plot_type):
    #     """Plot either mebrane voltage with different options
        
    #     :param str plot_type: "all", "comp", "some"
    #     """
    #     if plot_type == "all":
    #         for nid in nlist:
    #             # ---
    #             plt.figure("Membrane voltage")
    #             plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #             plt.xlabel("Time (ms)")
    #             plt.ylabel("Amplitude (mV)")
    #             plt.ylim([-100, 70])
    #             plt.title("V_mem")

    #             # ---
    #             plt.figure("Currents")
    #             plt.subplot(811)
    #             plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #             plt.ylim([-100, 70])
    #             plt.title("V_mem")

    #             plt.subplot(812)
    #             plt.plot(self.t/self.dt*1e-3, self.i_Na[nid][:])
    #             plt.title("i_Na")

    #             plt.subplot(813)
    #             plt.plot(self.t/self.dt*1e-3, self.i_K[nid][:])
    #             plt.title("i_K")

    #             plt.subplot(814)
    #             plt.plot(self.t/self.dt*1e-3, self.i_M[nid][:])
    #             plt.title("i_M")

    #             plt.subplot(815)
    #             plt.plot(self.t/self.dt*1e-3, self.i_T[nid][:])
    #             plt.title("i_L")
                
    #             plt.subplot(816)
    #             plt.plot(self.t/self.dt*1e-3, self.i_L[nid][:])
    #             plt.title("i_T")

    #             plt.subplot(817)
    #             plt.plot(self.t/self.dt*1e-3, self.i_Leak[nid][:])
    #             plt.title("i_Leak")

    #             plt.subplot(818)
    #             plt.plot(self.t/self.dt*1e-3, self.i_noise[nid][:])
    #             plt.title("i_noise")

    #             # ---
    #             plt.figure("Channel states")
    #             plt.subplot(911)
    #             plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #             plt.ylim([-100, 70])
    #             plt.title("V_mem")

    #             plt.subplot(912)
    #             plt.plot(self.t/self.dt*1e-3, self.mNa[nid][:])
    #             plt.title("mNa")

    #             plt.subplot(913)
    #             plt.plot(self.t/self.dt*1e-3, self.hNa[nid][:])
    #             plt.title("hNa")

    #             plt.subplot(914)
    #             plt.plot(self.t/self.dt*1e-3, self.mK[nid][:])
    #             plt.title("mK")

    #             plt.subplot(915)
    #             plt.plot(self.t/self.dt*1e-3, self.mM[nid][:])
    #             plt.title("mM")
                
    #             plt.subplot(916)
    #             plt.plot(self.t/self.dt*1e-3, self.mL[nid][:])
    #             plt.title("mL")
                
    #             plt.subplot(917)
    #             plt.plot(self.t/self.dt*1e-3, self.hL[nid][:])
    #             plt.title("hL")

    #             plt.subplot(918)
    #             plt.plot(self.t/self.dt*1e-3, self.mT[nid][:])
    #             plt.title("mT")
                
    #             plt.subplot(919)
    #             plt.plot(self.t/self.dt*1e-3, self.hT[nid][:])
    #             plt.title("hT")

    #             plt.suptitle("Detailed plot", fontsize=16)
    #             plt.show()

    #     elif plot_type == "comp":
    #         plt.figure("Membrane voltage")
    #         plt.xlabel("Time (ms)")
    #         plt.ylabel("Amplitude (mV)")
    #         plt.ylim([-100, 70])

    #         for nid in nlist:
    #             plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #         plt.legend(nlist)
    #         plt.suptitle("Compare membrane voltage", fontsize=16)
    #         plt.show()
        
    #     elif plot_type == "subplot":
    #         plt.figure("Membrane voltage")
    #         plt.xlabel("Time (ms)")
    #         plt.ylabel("Amplitude (mV)")
    #         plt.ylim([-100, 70])

    #         if len(nlist) < 1:
    #             return
            
    #         for i, nid in enumerate(nlist):
    #             if i == 0:
    #                 ax0 = plt.subplot(len(nlist), 1, nid+1)
    #             else:
    #                 plt.subplot(len(nlist), 1, nid+1, sharex = ax0)
    #             plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #             # plt.grid()

    #         plt.legend(nlist)
    #         plt.suptitle("Compare membrane voltage", fontsize=16)
    #         plt.show()

    #     elif plot_type == "some":
    #         plt.figure("Membrane voltage")
    #         plt.xlabel("Time (ms)")
    #         plt.ylabel("Amplitude (mV)")
    #         plt.ylim([-100, 70])

    #         some = [1, 5, 10, 15, 100, 250, 500]
    #         for nid in nlist:
    #             if nid in some:
    #                 plt.plot(self.t/self.dt*1e-3, self.v[nid][:])
    #         plt.legend(some)
    #         plt.suptitle("Compare membrane voltage", fontsize=16)
    #         plt.show()

    #     elif plot_type == "ampa":
            
    #         syn = Synapses()

    #         for n_id in nlist:
    #             fig, ax = plt.subplots(1, 1, sharex=True, figsize=(16, 9))
    #             ax.grid()
    #             ax.tick_params(axis='both', labelsize=14)
    #             ax.set_xlabel("Time (ms)", fontsize=20)
    #             ax.set_ylabel("Amplitude", fontsize=20)
    #             ax.set_xlim(left=0, right=len(self.t)/self.dt*1e-3)
    #             ax.plot(self.t/self.dt*1e-3, self.rnew_ampa_mem[n_id])
    #             ax.set_title(f'r', fontsize=20)
    #             ax.set_ylim([0, 1.0000001])
    #             plt.suptitle(f"Neuron {n_id:3d} -- Ampa r", fontsize=20)

    #             fig.tight_layout()
                
    #             plt.show()

    #     elif plot_type == "nmda":
            
    #         syn = Synapses()

    #         for n_id in nlist:
    #             fig, axs = plt.subplots(2, 1, sharex=True, figsize=(16, 9))
    #             for ax in axs:
    #                 ax.grid()
    #                 ax.tick_params(axis='both', labelsize=14)
    #                 ax.set_xlabel("Time (ms)", fontsize=20)
    #                 ax.set_ylabel("Amplitude", fontsize=20)
    #                 ax.set_xlim(left=0, right=len(self.t)/self.dt*1e-3)
    #             axs[0].plot(self.t/self.dt*1e-3, self.r_nmda[n_id])
    #             axs[0].set_title(f'r', fontsize=20)
    #             axs[1].plot(self.t/self.dt*1e-3, self.Bv_nmda[n_id])
    #             axs[1].set_title(f'B(Vpost)', fontsize=20)
    #             plt.suptitle(f"Neuron {n_id:3d} -- NMDA r & B(Vpost)", fontsize=20)

    #             axs[0].set_ylim([0, 1.0000001])
    #             axs[1].set_ylim(bottom=0)


    #             fig.tight_layout()
                
    #             plt.show()

    #     elif plot_type == "gabaa":
            
    #         syn = Synapses()

    #         for n_id in nlist:
    #             fig, ax = plt.subplots(1, 1, sharex=True, figsize=(16, 9))
    #             ax.grid()
    #             ax.tick_params(axis='both', labelsize=14)
    #             ax.set_xlabel("Time (ms)", fontsize=20)
    #             ax.set_ylabel("Amplitude", fontsize=20)
    #             ax.set_xlim(left=0, right=len(self.t)/self.dt*1e-3)
    #             ax.plot(self.t/self.dt*1e-3, self.r_gabaa[n_id])
    #             ax.set_title(f'r', fontsize=20)
    #             ax.set_ylim([0, 1.0000001])
    #             plt.suptitle(f"Neuron {n_id:3d} -- Gabaa r", fontsize=20)


    #             fig.tight_layout()
                
    #             plt.show()

    #     elif plot_type == "gabab":
            
    #         syn = Synapses()

    #         for n_id in nlist:
    #             fig, axs = plt.subplots(3, 1, sharex=True, figsize=(16, 9))
    #             for ax in axs:
    #                 ax.grid()
    #                 ax.tick_params(axis='both', labelsize=14)
    #                 ax.set_xlabel("Time (ms)", fontsize=20)
    #                 ax.set_ylabel("Amplitude", fontsize=20)
    #                 ax.set_xlim(left=0, right=len(self.t)/self.dt*1e-3)
    #             axs[0].plot(self.t/self.dt*1e-3, self.r_gabab[n_id])
    #             axs[0].set_title(f'r', fontsize=20)
    #             axs[1].plot(self.t/self.dt*1e-3, self.s_gabab[n_id])
    #             axs[1].set_title(f's', fontsize=20)
    #             axs[2].plot(self.t/self.dt*1e-3, syn.destexhe.Sn_GABAb(self.s_gabab[n_id]))
    #             axs[2].set_title(f's^n / (s^n + Kd)', fontsize=20)
    #             plt.suptitle(f"Neuron {n_id:3d} -- Gabab r & s", fontsize=20)

    #             # axs[0].set_ylim([0, 1.0000001])
    #             # axs[0].set_ylim(bottom=0)
    #             # axs[1].set_ylim(bottom=0)
    #             # axs[2].set_ylim(bottom=0)

    #             fig.tight_layout()
                
    #             plt.show()