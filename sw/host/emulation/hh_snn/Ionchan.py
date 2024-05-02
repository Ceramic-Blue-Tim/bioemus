# -*- coding: utf-8 -*-
# @title      Ionic channels equations
# @file       Ionchan.py
# @author     Romain Beaubois
# @date       05 Dec 2022
# @copyright
# SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# @brief Provide functions for ionic channels equations
# 
# @details 
# > **05 Dec 2022** : file creation (RB)

import numpy as np

class Ionchan:
    """"""    
    def __init__(self) -> None:
        pass
    
    def calcINa(self, nrn_model:str, v, m, h, g, e):
        """Calculate current for Na channel"""
        if nrn_model == "pospischil":
            return g * m**3 * h * (v - e)

    def calcIK(self, nrn_model:str, v, m, h, g, e):
        """Calculate current for K channel"""
        if nrn_model == "pospischil":
            return g * m**4  * (v - e)

    def calcIM(self, nrn_model:str, v, m, h, g, e):
        """Calculate current for M channel"""
        if nrn_model == "pospischil":
            return g * m * (v - e)

    def calcIL(self, nrn_model:str, v, m, h, g, e):
        """Calculate current for Leak channel"""
        if nrn_model == "pospischil":
            return g * (v - e)
    
    def calcINoise(self, nrn_model:str, iprev, noise_offs, pmul_theta, pmul_sigma):
        """Calculate current for noise"""
        if nrn_model == "pospischil":
            return iprev + noise_offs + pmul_theta*iprev + pmul_sigma*np.random.randn()

    