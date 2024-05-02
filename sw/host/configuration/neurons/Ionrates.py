# -*- coding: utf-8 -*-
# @title      Ionic channels states equations
# @file       Ionrates.py
# @author     Romain Beaubois
# @date       05 Dec 2022
# @copyright
# SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Provide functions for ionic channels states equations
# to create rates from pre-multiplied rate tables
# 
# @details 
# > **05 Dec 2022** : file creation (RB)

from math import exp, ceil, pi, tanh, cosh
import numpy as np
from numpy import linspace
from configuration.utility.Utility import writeFPGASimFile, writeFPGASimFileFloat, forwardEuler, SFI

NB_IONRATES         = 5
RATE_VMIN           = -76.0
RATE_VMAX           = 52.0
RATE_TABLE_SIZE     = 2048
RATE_STEP           = abs(RATE_VMIN - RATE_VMAX)/RATE_TABLE_SIZE
v_ramp              = linspace(RATE_VMIN, RATE_VMAX, RATE_TABLE_SIZE)

class Ionrates:
    def __init__(self) -> None:
        """Initialize"""
        pass

    def getRateVmin(self):
        """Get mininmum membrane voltage for rate table"""
        return RATE_VMIN

    def getRateVmax(self):
        """Get maximum membrane voltage for rate table"""
        return RATE_VMAX

    def getRateStep(self):
        """Get step for rate table"""
        return RATE_STEP

    def getDepthIonRates(self, nrn_model:str):
        """Get depth of rate table"""
        if   nrn_model == "pospischil":
            return RATE_TABLE_SIZE
        else:
            return 0

    def getNbIonRates(self, nrn_model:str):
        """Get number of ionic channels using rate tables"""
        if   nrn_model == "pospischil":
            return NB_IONRATES
        else:
            return 0

    def getIonRates(self, nrn_model:str, dt, gen_fpga_sim_files=False, fp_width=SFI.ION.WIDTH, fp_dec=SFI.ION.DEC):
        """Get rate tables for ionic channel states
        
        :param str nrn_model: Neuron model ("pospischil", ...)
        :param float dt: Time step
        :param bool gen_fpga_sim_files: Generate rates files for FPGA simulations
        :param int fp_width: Width of sfixed
        :param int fp_dec: Bit coding decimal part of sfixed
        """
        if   nrn_model == "pospischil":
            model = Pospischil()

            # From : https://link.springer.com/article/10.1007/s00422-008-0263-8
            # functions
            # taux        = lambda alpha,beta : 1/(alpha + beta)
            # xinf        = lambda alpha,beta : 1/(1+beta/alpha)
            
            if False: # Table rate second order correct for Crank-Nicholson
                r1          = lambda xinf, taux, dt: (taux - dt/2) / (taux + dt/2)
                r2          = lambda xinf, taux, dt: (xinf*dt) / (taux + dt/2)
                r1_hines    = lambda alpha, beta, dt: (1 - (dt/2)*(alpha+beta))/(1 + (dt/2)*(alpha+beta))
                r2_hines    = lambda alpha, beta, dt: (alpha*dt)/(1 + (dt/2)*(alpha+beta))
            else: # Table rate euler
                r1          = lambda xinf, taux, dt: 1-dt/taux
                r2          = lambda xinf, taux, dt: (dt*xinf)/taux
                r1_hines    = lambda alpha, beta, dt: 1-dt*(alpha+beta)
                r2_hines    = lambda alpha, beta, dt: dt*alpha

            mNa_r1, mNa_r2, hNa_r1, hNa_r2  = ([] for _ in range(4))
            mK_r1, mK_r2                    = ([] for _ in range(2))
            mM_r1, mM_r2                    = ([] for _ in range(2))
            mL_r1, mL_r2, hL_r1, hL_r2      = ([] for _ in range(4))
            mT_r1, mT_r2, hT_r1, hT_r2      = ([] for _ in range(4))
            ones                            = [1.0]*len(v_ramp)
            m_rates1, m_rates2              = ([] for _ in range(2))
            h_rates1, h_rates2              = ([] for _ in range(2))

            ###########################################################################


            # Generate rate tables
            for v in v_ramp:
                # Na
                mNa_r1.append( r1_hines(model.alpha_m_Na(v), model.beta_m_Na(v), dt))
                mNa_r2.append( r2_hines(model.alpha_m_Na(v), model.beta_m_Na(v), dt))
                hNa_r1.append( r1_hines(model.alpha_h_Na(v), model.beta_h_Na(v), dt))
                hNa_r2.append( r2_hines(model.alpha_h_Na(v), model.beta_h_Na(v), dt))
                # K
                mK_r1.append( r1_hines(model.alpha_m_K(v), model.beta_m_K(v), dt) )
                mK_r2.append( r2_hines(model.alpha_m_K(v), model.beta_m_K(v), dt) )
                # M
                mM_r1.append( r1(model.xinf_M(v), model.taux_M(v), dt) )
                mM_r2.append( r2(model.xinf_M(v), model.taux_M(v), dt) )
                # L
                mL_r1.append( r1_hines(model.alpha_m_L(v), model.beta_m_L(v), dt))
                mL_r2.append( r2_hines(model.alpha_m_L(v), model.beta_m_L(v), dt))
                hL_r1.append( r1_hines(model.alpha_h_L(v), model.beta_h_L(v), dt))
                hL_r2.append( r2_hines(model.alpha_h_L(v), model.beta_h_L(v), dt))
                # T
                mT_r1.append( 0.0 )
                mT_r2.append( model.xinf_T_m(v) )
                hT_r1.append( r1(model.xinf_T_h(v), model.taux_T_h(v), dt) )
                hT_r2.append( r2(model.xinf_T_h(v), model.taux_T_h(v), dt) )

                
            m_rates1.append(mNa_r1) ; m_rates2.append(mNa_r2)   # Na
            m_rates1.append(mK_r1)  ; m_rates2.append(mK_r2)    # K
            m_rates1.append(mM_r1)  ; m_rates2.append(mM_r2)    # M
            m_rates1.append(mL_r1)  ; m_rates2.append(mL_r2)    # L
            m_rates1.append(mT_r1)  ; m_rates2.append(mT_r2)    # T
        
            h_rates1.append(hNa_r1) ; h_rates2.append(hNa_r2)   # Na
            h_rates1.append(ones)   ; h_rates2.append(ones)     # K
            h_rates1.append(ones)   ; h_rates2.append(ones)     # M
            h_rates1.append(hL_r1)  ; h_rates2.append(hL_r2)    # L
            h_rates1.append(hT_r1)  ; h_rates2.append(hT_r2)    # T

            writeFPGASimFile(gen_fpga_sim_files, "r1m_Na.txt", mNa_r1, len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2m_Na.txt", mNa_r2, len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1h_Na.txt", hNa_r1, len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2h_Na.txt", hNa_r2, len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1m_K.txt",  mK_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2m_K.txt",  mK_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1m_M.txt",  mM_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2m_M.txt",  mM_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1m_L.txt",  mL_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2m_L.txt",  mL_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1h_L.txt",  hL_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2h_L.txt",  hL_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1m_T.txt",  mT_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2m_T.txt",  mT_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r1h_T.txt",  hT_r1,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            writeFPGASimFile(gen_fpga_sim_files, "r2h_T.txt",  hT_r2,  len(v_ramp), SFI.ION.WIDTH, SFI.ION.DEC)
            
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1m_Na.txt", mNa_r1, len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2m_Na.txt", mNa_r2, len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1h_Na.txt", hNa_r1, len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2h_Na.txt", hNa_r2, len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1m_K.txt",  mK_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2m_K.txt",  mK_r2,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1m_M.txt",  mM_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2m_M.txt",  mM_r2,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1m_L.txt",  mL_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2m_L.txt",  mL_r2,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1h_L.txt",  hL_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2h_L.txt",  hL_r2,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1m_T.txt",  mT_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2m_T.txt",  mT_r2,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r1h_T.txt",  hT_r1,  len(v_ramp))
            # writeFPGASimFileFloat(gen_fpga_sim_files, "fp_r2h_T.txt",  hT_r2,  len(v_ramp))
            

            return [m_rates1, m_rates2, h_rates1, h_rates2]


        elif nrn_model == "MN_E13":
            """TODO : add MN_E13 ionrates"""
            # r1_hines    = lambda alpha, beta, dt: (1 - (dt/2)*(alpha+beta))/(1 + (dt/2)*(alpha+beta))
            # r2_hines    = lambda alpha, beta, dt: (alpha*dt)/(1 + (dt/2)*(alpha+beta))

            # # m_Na
            # Aa_m0 = 1.0; ka_m0 = 0.1;   da_m0 = -36.0
            # Ab_m0 = 4.0; kb_m0 = -0.05; db_m0 = -43.0
            # alpha_m_Na  = lambda v : (Aa_m0*ka_m0*(v-da_m0)/(1-exp(-ka_m0*(v-da_m0))))
            # beta_m_Na   = lambda v : (Ab_m0*exp(kb_m0*(v-db_m0)))

            # # h_Na
            # Aa_h0 = 0.07;  ka_h0 = -0.05; da_h0 = -28.0
            # Ab_h0 = 1.0;   kb_h0 = -0.2;  db_h0 = -13.0
            # alpha_h_Na  = lambda v : (Aa_h0*exp(ka_h0*(v-da_h0)))
            # beta_h_Na   = lambda v : (Ab_h0/(1+exp(kb_h0*(v-db_h0))))

            # # m_K
            # alpha_m_K   = lambda v : (0.01*(v+12)/(1-exp(-0.1*(v+12))))
            # beta_m_K    = lambda v : (0.125*exp(-0.0125*(v+22)))

            # # >>> DEBUG
            # fig, axs    = plt.subplots(NB_IONRATES, 4)
            # # <<<

            # # Na ionic channel
            # for v in v_ramp:
            #     # Generate from alpha & beta directly
            #     l_m_r1.append( r1_hines(alpha_m_Na(v), beta_m_Na(v), dt))
            #     l_h_r1.append( r1_hines(alpha_h_Na(v), beta_h_Na(v), dt))
            #     l_m_r2.append( r2_hines(alpha_m_Na(v), beta_m_Na(v), dt))
            #     l_h_r2.append( r2_hines(alpha_h_Na(v), beta_h_Na(v), dt))
            # hw_cfg_file.m_rates1.append(l_m_r1)
            # hw_cfg_file.m_rates2.append(l_m_r2)
            # hw_cfg_file.h_rates1.append(l_h_r1)
            # hw_cfg_file.h_rates2.append(l_h_r2)

            # # >>> DEBUG
            # axs[0, 0].plot(v_ramp, l_m_r1); axs[0, 0].set_title("m_Na_r1")
            # axs[0, 1].plot(v_ramp, l_m_r2); axs[0, 1].set_title("m_Na_r2")
            # axs[0, 2].plot(v_ramp, l_h_r1); axs[0, 2].set_title("h_Na_r1")
            # axs[0, 3].plot(v_ramp, l_h_r2); axs[0, 3].set_title("h_Na_r2")

            # if gen_fpga_sim_files:
            #     FP_WIDTH    = 18
            #     FP_DEC_ION  = 16
            #     with open("r1m_Na.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_m_r1[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            #     with open("r2m_Na.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_m_r2[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            #     with open("r1h_Na.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_h_r1[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            #     with open("r2h_Na.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_h_r2[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            # # <<<

            # l_m_r1 = []
            # l_m_r2 = []
            # l_h_r1 = []
            # l_h_r2 = []

            # # K ionic channel
            # for v in v_ramp:
            #     # Generate from alpha & beta directly
            #     l_m_r1.append( r1_hines(alpha_m_K(v), beta_m_K(v), dt) )
            #     l_m_r2.append( r2_hines(alpha_m_K(v), beta_m_K(v), dt) )
            #     l_h_r1.append( 1.0 )
            #     l_h_r2.append( 1.0 )
            # hw_cfg_file.m_rates1.append(l_m_r1)
            # hw_cfg_file.m_rates2.append(l_m_r2)
            # hw_cfg_file.h_rates1.append(l_h_r1)
            # hw_cfg_file.h_rates2.append(l_h_r2)

            # # >>> DEBUG
            # axs[1, 0].plot(v_ramp, l_m_r1); axs[1, 0].set_title("m_K_r1")
            # axs[1, 1].plot(v_ramp, l_m_r2); axs[1, 1].set_title("m_K_r2")
            # if gen_fpga_sim_files:
            #     FP_WIDTH    = 18
            #     FP_DEC_ION  = 16
            #     with open("r1m_K.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_m_r1[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            #     with open("r2m_K.txt", "w") as f:
            #         for i in range(len(v_ramp)): f.write(str(Fxp(l_m_r2[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC_ION).val) + "\n")
            # # <<<

            # l_m_r1 = []
            # l_m_r2 = []
            # l_h_r1 = []
            # l_h_r2 = []

            # # M ionic channel
            # for v in v_ramp:
            #     # Generate from alpha & beta directly
            #     l_m_r1.append( 0.0 )
            #     l_m_r2.append( 0.0 )
            #     l_h_r1.append( 0.0 )
            #     l_h_r2.append( 0.0 )
            # hw_cfg_file.m_rates1.append(l_m_r1)
            # hw_cfg_file.m_rates2.append(l_m_r2)
            # hw_cfg_file.h_rates1.append(l_h_r1)
            # hw_cfg_file.h_rates2.append(l_h_r2)

            # l_m_r1 = []
            # l_m_r2 = []
            # l_h_r1 = []
            # l_h_r2 = []

class Pospischil:
    V_T         = -55       # (mV) adjust spike threshold
    V_X         = 2         # (mV)
    TAU_MAX     = 1e3       # (ms)
            
    # Na ---------------------------------------------------------------------
    # m
    def alpha_m_Na(self, v) -> np.longdouble: return ((-0.32*(v-self.V_T-13)) / (exp(-(v-self.V_T-13)/4)-1))
    def  beta_m_Na(self, v) -> np.longdouble: return ((+0.28*(v-self.V_T-40)) / (exp((v-self.V_T-40)/5)-1))
    def  calc_m_Na(self, v, mpre, dt) -> np.float64: 
        dx = self.alpha_m_Na(v)*(1-mpre) - self.beta_m_Na(v)*mpre
        return forwardEuler(dx, mpre, dt)
    # h
    def alpha_h_Na(self, v)-> np.longdouble: return 0.128*exp(-(v-self.V_T-17)/18)
    def  beta_h_Na(self, v)-> np.longdouble: return 4/(1+exp(-(v-self.V_T-40)/5))
    def  calc_h_Na(self, v, hpre, dt)-> np.float64: 
        dx = self.alpha_h_Na(v)*(1-hpre) - self.beta_h_Na(v)*hpre
        return forwardEuler(dx, hpre, dt)

    # K ---------------------------------------------------------------------
    # m
    def alpha_m_K(self, v)-> np.longdouble: return (-0.035*(v-self.V_T-15)) / (exp(-(v-self.V_T-15)/5)-1)
    def  beta_m_K(self, v)-> np.longdouble: return 0.5*exp(-(v-self.V_T-10)/40)
    def  calc_m_K(self, v, mpre, dt)-> np.float64:
        dx = self.alpha_m_K(v)*(1-mpre) - self.beta_m_K(v)*mpre
        return forwardEuler(dx, mpre, dt)

    # M ---------------------------------------------------------------------
    # m_M
    def   xinf_M(self, v)-> np.longdouble: return 1.0/(1.0+exp(-(v+35.0)/10.0))
    def   taux_M(self, v)-> np.longdouble: return self.TAU_MAX/(3.3*exp((v+35.0)/20.0) + exp(-(v+35.0)/20.0))
    def calc_m_M(self, v, mpre, dt)-> np.float64:
        dx = (self.xinf_M(v)-mpre)/self.taux_M(v)
        return forwardEuler(dx, mpre, dt)

    # L ---------------------------------------------------------------------
    # m (q)
    def alpha_m_L(self, v)-> np.longdouble: return 0.055*(-27-v) / (exp((-27-v)/3.8) - 1)
    def  beta_m_L(self, v)-> np.longdouble: return 0.94*exp((-75-v)/17)
    def  calc_m_L(self, v, mpre, dt)-> np.float64: 
        dx = self.alpha_m_L(v)*(1-mpre) - self.beta_m_L(v)*mpre
        return forwardEuler(dx, mpre, dt)
    # h (r)
    def alpha_h_L(self,v)-> np.longdouble: return 0.000457*exp((-13.0-v)/50.0)
    def  beta_h_L(self,v)-> np.longdouble: return 0.0065 / (exp((-15.0-v)/28.0) + 1.0)
    def  calc_h_L(self, v, hpre, dt)-> np.float64:
        dx = self.alpha_h_L(v)*(1-hpre) - self.beta_h_L(v)*hpre
        return forwardEuler(dx, hpre, dt)
    
    # T ---------------------------------------------------------------------
    # m (directly correspond to r2)
    def xinf_T_m(self, v)-> np.longdouble: return 1 / (1 + exp(-(v+self.V_X+57)/6.2))
    def calc_m_T(self, v, mpre, dt) -> np.float64:
        dx = self.xinf_T_m(v)
        return dx
    # h
    def xinf_T_h(self, v)-> np.longdouble: return 1 / (1 + exp((v + self.V_X + 81)/4))
    def taux_T_h(self, v)-> np.longdouble: return (30.8 + ((211.4 + exp((v+self.V_X+113.2)/5)) / (1 + exp((v+self.V_X+84)/3.2)))) * (1/(3**1.2))
    def calc_h_T(self, v, hpre, dt) -> np.float64: 
        dx = (self.xinf_T_h(v)-hpre)/self.taux_T_h(v)
        return forwardEuler(dx, hpre, dt)