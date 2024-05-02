/*
*! @title      Class to handle hardware configuration
*! @file       HwCfg.cpp
*! @author     Romain Beaubois
*! @date       09 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **09 Aug 2022** : file creation (RB)
*/

#include "HwCfg.h"
#include "bioemus.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <cstdlib>
#include <ctime>

/***************************************************************************
 * Split strings
 * 
 * @param str String to split
 * @param sep String separator
 * @return None
****************************************************************************/
vector<string> splitStr(const string& str, const char sep){
    auto r  = vector<string>{};
    auto ss = stringstream{str};

    for (string line; getline(ss, line, sep);)
        r.push_back(line);

    return r;
}

/***************************************************************************
 * Constructor
 * 
 * @param fpath Path to configuration file
 * @return HwCfg
****************************************************************************/
HwCfg::HwCfg(string fpath, AxiLite *axilite){
    _fpath              = fpath;
    _axilite            = axilite;
    _val_regw_setup_syn = 0;
}

/***************************************************************************
 * Set noise seed
 * 
 * @return None
****************************************************************************/
int HwCfg::setSeed(){
    int r;
    
    const uint32_t MAX_SEED = 4096;
    srand(time(nullptr));
    #ifdef DBG_FIXED_SEED
        r = _axilite->write(MAX_SEED/2, REGW_NOISE_SEED0);
        r = _axilite->write(MAX_SEED/4, REGW_NOISE_SEED1);
        r = _axilite->write(MAX_SEED/8, REGW_NOISE_SEED2);
        r = _axilite->write(MAX_SEED/16, REGW_NOISE_SEED3);
    #else
        r = _axilite->write(rand() % (MAX_SEED + 1), REGW_NOISE_SEED0);
        r = _axilite->write(rand() % (MAX_SEED + 1), REGW_NOISE_SEED1);
        r = _axilite->write(rand() % (MAX_SEED + 1), REGW_NOISE_SEED2);
        r = _axilite->write(rand() % (MAX_SEED + 1), REGW_NOISE_SEED3);
    #endif

    statusPrint(r, "Set seed noise generator");

    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration
 * 
 * @return None
****************************************************************************/
int HwCfg::apply(){
    int r;
    
    // Open configuration file
    _hw_cfg_file.open(_fpath, ios::out);
    r = !_hw_cfg_file.good() ? EXIT_FAILURE : EXIT_SUCCESS;
    statusPrint(r, "Open hardware configuration file");
    if (r == EXIT_FAILURE)
        return r;

    // Read and print header
    string tmp;
    infoPrint(0, "Read hardware configuration file: " + _fpath);
    cout << string(50,'#') << endl;
    for (int i = 0; i < HEADER_SIZE; i++){
        getline(_hw_cfg_file, tmp);
        cout << ITLC(""+tmp+"") << endl;
    }
    cout << string(50,'#') << endl;

    // Apply HH parameters
    r = applyHhparam();
    statusPrint(r, "Apply HH parameters configuration to hardware");
    if (r == EXIT_FAILURE)
        return r;

    // Apply synaptic configuration
    r = applySynParams();
    statusPrint(r, "Apply synaptic parameters to hardware");
    if (r == EXIT_FAILURE)
        return r;

    // Apply ionrate tables
    r = applyIonrates();
    statusPrint(r, "Apply ionrates tables configuration to hardware");
    if (r == EXIT_FAILURE)
        return r;
    
    // Apply synaptic rate tables
    r = applySynrates();
    statusPrint(r, "Apply synrates tables configuration to hardware");
    if (r == EXIT_FAILURE)
        return r;

    // Apply synaptic configuration
    r = applySynConf();
    statusPrint(r, "Apply synaptic configuration to hardware");
    if (r == EXIT_FAILURE)
        return r;

    // Close configuration file
    _hw_cfg_file.close();
    r = _hw_cfg_file.is_open() ? EXIT_FAILURE : EXIT_SUCCESS;
    statusPrint(r, "Close hardware configuration file");

    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration for HH parameters
 * 
 *          hhparam (gion, eion)
 *  N0S0    0.1,0.2,0.3,0.4
 *  N0S1    0.1,0.2,0.3,0.4
 * 
 * @return EXIT_SUCCESS
****************************************************************************/
int HwCfg::applyHhparam(){
    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    vector<string> HHp_Ni;

    // Apply hhparams
    for (int waddr = 0; waddr < _nb_nrn; waddr++){
        // Read line and split key/value
        getline(_hw_cfg_file, line);
        vline   = splitStr(line, KEY_SEP);
        HHp_Ni  = splitStr(vline[1], VAL_SEP);
        
        // Fill AXI registers
        for (int p = 0; p < _nb_hhparam; p++){
            if(p == HHP_ID_NOISE_OFFS){
                _axilite->write(stof(HHp_Ni[p]), REGW_HHPARAM_BASE+p, SFI_MU_INT, SFI_MU_DEC);
            }
            else if(p == HHP_ID_PMUL_THETA){
                _axilite->write(stof(HHp_Ni[p]), REGW_HHPARAM_BASE+p, SFI_THETA_INT, SFI_THETA_DEC);
            }
            else if(p == HHP_ID_PMUL_SIGMA){
                _axilite->write(stof(HHp_Ni[p]), REGW_HHPARAM_BASE+p, SFI_SIGMA_INT, SFI_SIGMA_DEC);
            }
            else if(p == HHP_ID_PMUL_GSYN){
                _axilite->write(stof(HHp_Ni[p]), REGW_HHPARAM_BASE+p, SFI_PMUL_GSYN_INT, SFI_PMUL_GSYN_DEC);
            }
            else if(p == HHP_ID_I_STIM){
                _axilite->write(stof(HHp_Ni[p]), REGW_HHPARAM_BASE+p, SFI_CUR_INT, SFI_CUR_DEC);
            }
            else{
                float hhp_val_fp = stof(HHp_Ni[p]);
                uint32_t hhp_val_int; memcpy(&hhp_val_int, &hhp_val_fp, sizeof(hhp_val_int));
                _axilite->write(hhp_val_int, REGW_HHPARAM_BASE+p);

                if (p==HHP_ID_V_INIT){
                    _axilite->write(stof(HHp_Ni[p]), REGW_V_INIT_SYN_SFI, SFI_V_TRUNC_INT, SFI_V_TRUNC_DEC);
                }
            }
        }

        // Write address and enable writing
        _axilite->write(waddr, REGW_WADDR_HHPARAM);
        _axilite->write((1<<0), REGW_WEN_HHPARAM);

        // Wait for FPGA read and disable writing
        while(_axilite->read(REGR_WADDR_HHPARAM_LP) != waddr);
        _axilite->write((0<<0), REGW_WEN_HHPARAM);

        // Empty vectors
        vline.clear();
        HHp_Ni.clear();
    }
    
    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration ionrates tables
 * 
 *          m_rates1    ; m_rates2  ; h_rates1  ; h_rates2
 *  I0_A0   0.1         ; 0.2       ; 0.3       ; 0.4
 *  I0_A1   0.1         ; 0.2       ; 0.3       ; 0.4
 * 
 * @return EXIT_SUCCESS
****************************************************************************/
int HwCfg::applyIonrates(){
    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    vector<string> mh_rates;

    for (int i = 0; i < _nb_ionrate; i++){
        for (int waddr = 0; waddr < _depth_ionrate; waddr++){
            // Read line and split key/value
            getline(_hw_cfg_file, line);
            vline = splitStr(line, KEY_SEP);
            mh_rates = splitStr(vline[1], COL_SEP);


            float mr1_fp = stof(mh_rates[0]);
            float mr2_fp = stof(mh_rates[1]);
            float hr1_fp = stof(mh_rates[2]);
            float hr2_fp = stof(mh_rates[3]);

            uint32_t mr1_int; memcpy(&mr1_int, &mr1_fp, sizeof(mr1_int));
            uint32_t mr2_int; memcpy(&mr2_int, &mr2_fp, sizeof(mr2_int));
            uint32_t hr1_int; memcpy(&hr1_int, &hr1_fp, sizeof(hr1_int));
            uint32_t hr2_int; memcpy(&hr2_int, &hr2_fp, sizeof(hr2_int));

            _axilite->write(mr1_int, REGW_RATE1_M); // m rate 1
            _axilite->write(mr2_int, REGW_RATE2_M); // m rate 2
            _axilite->write(hr1_int, REGW_RATE1_H); // h rate 1
            _axilite->write(hr2_int, REGW_RATE2_H); // h rate 2

            // Write address and enable writing
            _axilite->write(waddr, REGW_WADDR_IONRATE);
            _axilite->write((1<<i), REGW_WEN_IONRATE_M);
            _axilite->write((1<<i), REGW_WEN_IONRATE_H);

            // Wait for FPGA read and disable writing
            while(_axilite->read(REGR_WADDR_IONRATE_LP) != waddr);
            _axilite->write((0<<i), REGW_WEN_IONRATE_M);
            _axilite->write((0<<i), REGW_WEN_IONRATE_H);

            mh_rates.clear();
        }
    }

    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration synrates tables
 * 
 *          Bv  ; Tv
 *  I0_A0   0.1 ; 0.2
 *  I0_A1   0.1 ; 0.2
 * 
 * @return EXIT_SUCCESS
****************************************************************************/
int HwCfg::applySynrates(){
    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    vector<string> rates;

    for (int waddr = 0; waddr < _depth_synrate; waddr++){
        // Read line and split key/value
        getline(_hw_cfg_file, line);
        vline = splitStr(line, KEY_SEP);
        rates = splitStr(vline[1], COL_SEP);

        // Fill AXI registers
        _axilite->write(stof(rates[0]), REGW_SYNRATE_BV, SFI_BRATE_SYN_INT,     SFI_BRATE_SYN_DEC); // Bv
        _axilite->write(stof(rates[1]), REGW_SYNRATE_TV, SFI_TRATE_SYN_INT,     SFI_TRATE_SYN_DEC); // Tv
        _axilite->write(stof(rates[2]), REGW_SN_GABAB,   SFI_SN_GABAB_OUT_INT,  SFI_SN_GABAB_OUT_DEC); // sn_gabab

        // Write address and enable writing
        _axilite->write(waddr, REGW_WADDR_SYNRATE_BV);
        _axilite->write(waddr, REGW_WADDR_SYNRATE_TV);
        _axilite->write(waddr, REGW_WADDR_SN_GABAB);
        SET_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_BV_RATE);
        SET_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_TV_RATE);
        SET_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_SN_GABAB);
        _axilite->write(_val_regw_setup_syn, REGW_SETUP_SYN);

        // Wait for FPGA read and disable writing
        while(_axilite->read(REGR_WADDR_SYNRATE_TV_LP) != waddr);
        CLEAR_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_BV_RATE);
        CLEAR_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_TV_RATE);
        CLEAR_BIT_REG(_val_regw_setup_syn, BIT_SETUP_SYN_WEN_SN_GABAB);
        _axilite->write(_val_regw_setup_syn, REGW_SETUP_SYN);

        rates.clear();
    }

    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration synapses parameters
 * 
 * synparam (ampa, ndma, gabaa, gabab) with alpha,beta,gsyn, ...
 *  0.1   ; 0.2  ;   0.3 ;   0.4
 * 
 * @return EXIT_SUCCESS
****************************************************************************/
int HwCfg::applySynParams(){
    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    vector<string> psyn;
    uint32_t reg_val = 0;
    float wdata = 0.0;
    uint8_t fp_int = 2;
    uint8_t fp_dec = 16;

    // Read line and split key/value
    getline(_hw_cfg_file, line);
    vline       = splitStr(line, KEY_SEP);
    psyn        = splitStr(vline[1], VAL_SEP);

    for (uint8_t wsel = 0; wsel < NB_PSYN; wsel++){
        wdata = stof(psyn[wsel]);

        if( wsel==PSYN_ID_AMPA_K1 || wsel==PSYN_ID_NMDA_K1 || wsel==PSYN_ID_GABAA_K1 || wsel==PSYN_ID_GABAB_K1 ){
            fp_int = SFI_K1_SYN_INT;
            fp_dec = SFI_K1_SYN_DEC;
        }
        else if( wsel==PSYN_ID_AMPA_K2  || wsel==PSYN_ID_NMDA_K2  || wsel==PSYN_ID_GABAA_K2  || wsel==PSYN_ID_GABAB_K2 ){
            fp_int = SFI_K2_SYN_INT;
            fp_dec = SFI_K2_SYN_DEC;
        }
        else if( wsel==PSYN_ID_GABAB_K3 ){
            fp_int = SFI_GABAB_K3_INT;
            fp_dec = SFI_GABAB_K3_DEC;
        }
        else if( wsel==PSYN_ID_GABAB_K4 ){
            fp_int = SFI_GABAB_K4_INT;
            fp_dec = SFI_GABAB_K4_DEC;
        }
        else if( wsel==PSYN_ID_AMPA_ESYN  || wsel==PSYN_ID_NMDA_ESYN  || wsel==PSYN_ID_GABAA_ESYN  || wsel==PSYN_ID_GABAB_ESYN ){
            fp_int = SFI_V_TRUNC_INT;
            fp_dec = SFI_V_TRUNC_DEC;
        }
        else if( wsel==PSYN_ID_AMPA_GSYN  || wsel==PSYN_ID_NMDA_GSYN  || wsel==PSYN_ID_GABAA_GSYN  || wsel==PSYN_ID_GABAB_GSYN ){
            fp_int = SFI_GSYN_INT;
            fp_dec = SFI_GSYN_DEC;
        }
        else{
            fp_int = SFI_SYN_INT;
            fp_dec = SFI_SYN_DEC;
        }

        reg_val = (((uint32_t)(wsel) & ((1<<PSYN_WIDTH_WSEL)-1)) << PSYN_WIDTH_WDATA) | (float2sfi(wdata, fp_int, fp_dec) & ((1<<PSYN_WIDTH_WDATA)-1));
        SET_BIT_REG(reg_val, PSYN_BIT_WEN);

        // Fill AXI registers
        _axilite->write(reg_val, REGW_SETUP_PSYN);

        // Wait for FPGA read and disable writing
        while( _axilite->read(REGR_WADDR_SETUP_PSYN_LP) != wsel);
        CLEAR_BIT_REG(reg_val, PSYN_BIT_WEN);
        _axilite->write(reg_val, REGW_SETUP_PSYN);

    }
    psyn.clear();

    return EXIT_SUCCESS;
}

/***************************************************************************
 * Apply hardware configuration synaptic configuration
 * 
 * * tsyn/wsyn format in config file:
 *          N0       ; N1    ; N3
 *  N0      AMPA$0.1 ; x$0.3 ; x$0.2
 *  N1      AMPA$0.1 ; x$0.3 ; x$0.2
 * 
 * @return EXIT_SUCCESS
****************************************************************************/
int HwCfg::applySynConf(){

    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    vector<string> twsyn_line;
    string str_tsyn_i;
    string str_wsyn_i;
    uint8_t tsyn_i = 0;

    uint32_t cnt_col        = 0;
    uint32_t cnt_col_offs   = 0;
    uint32_t cnt_col_prev   = 0;
    uint32_t cnt_rest       = 0;
    uint32_t offs_line      = 0;
    uint32_t offs_depth     = 0;
    uint32_t offs_rest      = 0;


    // Synaptic type
    for (int dest = 0; dest < _nb_nrn; dest++){
        // Read line and split key/value
        getline(_hw_cfg_file, line);
        vline       = splitStr(line, KEY_SEP);
        twsyn_line  = splitStr(vline[1], VAL_SEP); // All synaptic types of neuron nid

        for (int src = 0; src < _nb_nrn; src++){
            stringstream ss = stringstream(twsyn_line[src]);
            getline(ss, str_tsyn_i, '$');
            getline(ss, str_wsyn_i, '$');

            if      (str_tsyn_i=="ampa") {tsyn_i = TSYN_ID_AMPA;}
            else if (str_tsyn_i=="gabaa"){tsyn_i = TSYN_ID_GABAA;}
            else if (str_tsyn_i=="gabab"){tsyn_i = TSYN_ID_GABAB;}
            else if (str_tsyn_i=="nmda") {tsyn_i = TSYN_ID_NMDA;}
            else                         {tsyn_i = TSYN_ID_AMPA;}

            twsyn[cnt_col_offs*3 + cnt_col + (offs_line+offs_rest)*(NB_RAM_TWSYN*RAMWIDTH_TWSYN/16) + offs_depth*NB_DSP_WMB_SYNAPSES*(NB_NRN-1)] = ((uint16_t)(tsyn_i)<<WEIGHT_SIZE) | (float2sfi(stof(str_wsyn_i), SFI_WSYN_INT, SFI_WSYN_DEC)&((1<<WEIGHT_SIZE)-1));
            
            if (cnt_col<(3-1)){
                cnt_col++;
                cnt_rest = 0;
            }else{
                cnt_col   = 0;
                cnt_rest  = 1;
                offs_line++;
            }
        }

        offs_line=0;

        if (cnt_col_offs<(NB_DSP_WMB_SYNAPSES-1)){
            cnt_col_offs++;
            cnt_col = cnt_col_prev;
        }else{
            cnt_col_offs    = 0;
            cnt_col_prev    = cnt_col;
            offs_depth++;

            if(cnt_rest == 1)
                offs_rest++;
        }

        twsyn_line.clear();
    }

    const int RAMWIDTH_BYTES = RAMWIDTH_TWSYN/8;
    uint8_t* twsyn_bytes = (uint8_t*)(twsyn);
    uint32_t twsyn_vptr_u32_reg0 = 0;
    uint32_t twsyn_vptr_u32_reg1 = 0;
    uint32_t twsyn_vptr_u32_reg2 = 0;
    uint32_t cnt_bytes = 0;
    for (int waddr = 0; waddr < RAMDEPTH_TWSYN; waddr++){
        for (int ram_i = 0; ram_i < NB_RAM_TWSYN; ram_i++){
            twsyn_vptr_u32_reg2 =      (uint32_t)(twsyn_bytes[cnt_bytes+8]);
            twsyn_vptr_u32_reg1 =     ((uint32_t)(twsyn_bytes[cnt_bytes+7])<<24)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+6])<<16)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+5])<<8)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+4]));
            twsyn_vptr_u32_reg0 =     ((uint32_t)(twsyn_bytes[cnt_bytes+3])<<24)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+2])<<16)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+1])<<8)
                                    + ((uint32_t)(twsyn_bytes[cnt_bytes+0]));
            _axilite->write(twsyn_vptr_u32_reg2, REGW_TWSYN_2);
            _axilite->write(twsyn_vptr_u32_reg1, REGW_TWSYN_1);
            _axilite->write(twsyn_vptr_u32_reg0, REGW_TWSYN_0);
            cnt_bytes += RAMWIDTH_BYTES;

            _axilite->write(waddr, REGW_WADDR_TWSYN);

            if (ram_i < 32)
                _axilite->write((1<<ram_i), REGW_WEN_TWSYN_LSB);
            else
                _axilite->write((1<<(ram_i-32)), REGW_WEN_TWSYN_MSB);

            while( _axilite->read(REGR_WADDR_TWSYN_LP) != waddr);

            _axilite->write((0<<0), REGW_WEN_TWSYN_LSB);
            _axilite->write((0<<0), REGW_WEN_TWSYN_MSB);
        }
    }
    
    _axilite->write(0, REGW_INH_TSYN); // Activate synapses
    
    statusPrint(EXIT_SUCCESS, "Apply synaptic types and weights");


    return EXIT_SUCCESS;
}

/***************************************************************************
 * Decode line for key/sep/value
 * 
 * @return Value read as uint
****************************************************************************/
template <typename data_t>
int HwCfg::decodeLine(string key, data_t* rval){
    int r;
    string line;
    vector<string> vline;   // [0] (string) key [1] (string) val
    getline(_hw_cfg_file, line);
    vline = splitStr(line, KEY_SEP);

    r = (vline[0].compare(key)) ? EXIT_FAILURE : EXIT_SUCCESS;
    if(r == EXIT_SUCCESS)
        *rval = stoi(vline[1]);

    return r;
}

/***************************************************************************
 * Get number of neuron
 * 
 * @return Number of neuron
****************************************************************************/
uint16_t HwCfg::getNbNrn(){
    return _nb_nrn;
}
