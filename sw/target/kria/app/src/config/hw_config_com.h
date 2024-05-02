#ifndef __HW_CONFIG_COM_H__
#define __HW_CONFIG_COM_H__

// ### AXILITE CORE 0 ###
// #########################################################
// Number of registers for Axilite : hh core 0
#define NB_REGS_WRITE_AXILITE_CORE0 63
#define NB_REGS_READ_AXILITE_CORE0 9

// Registers ID for Axilite Core 0: hardware setup
// ---
// Write registers
#define REGW_CONTROL 0
#define REGW_CONTROL_MON 1
#define REGW_SETUP_SYN 2
#define REGW_WEN_IONRATE_M 3
#define REGW_WEN_IONRATE_H 4
#define REGW_WEN_HHPARAM 5
#define REGW_WEN_TWSYN_LSB 6
#define REGW_WEN_TWSYN_MSB 7
#define REGW_WADDR_SEL_MON 8
#define REGW_WADDR_IONRATE 9
#define REGW_WADDR_HHPARAM 10
#define REGW_WADDR_SYNRATE_BV 11
#define REGW_WADDR_SYNRATE_TV 12
#define REGW_WADDR_SN_GABAB 13
#define REGW_WADDR_TWSYN 14
#define REGW_NB_PACKETS_MON_SPK 15
#define REGW_NB_PACKETS_MON_VMEM 16
#define REGW_NOISE_SEED0 17
#define REGW_NOISE_SEED1 18
#define REGW_NOISE_SEED2 19
#define REGW_NOISE_SEED3 20
#define REGW_RATE1_M 21
#define REGW_RATE2_M 22
#define REGW_RATE1_H 23
#define REGW_RATE2_H 24
#define REGW_V_INIT_SYN_SFI 25
#define REGW_SYNRATE_BV 26
#define REGW_SYNRATE_TV 27
#define REGW_SN_GABAB 28
#define REGW_INH_TSYN 29
#define REGW_SETUP_PSYN 30
#define REGW_TWSYN_0 31
#define REGW_TWSYN_1 32
#define REGW_TWSYN_2 33
#define REGW_SEL_MON 34
#define REGW_STIM_WIDTH 35
#define REGW_STIM_DELAY 36
#define REGW_USER_LEDS 37
#define REGW_SEL_MON_DAC_BASE 38
#define REGW_HHPARAM_BASE 47

// Read registers
#define REGR_V_NEW 63
#define REGR_WADDR_SEL_MON_LP 64
#define REGR_WADDR_IONRATE_LP 65
#define REGR_WADDR_HHPARAM_LP 66
#define REGR_WADDR_SYNRATE_BV_LP 67
#define REGR_WADDR_SYNRATE_TV_LP 68
#define REGR_WADDR_SN_GABAB_LP 69
#define REGR_WADDR_SETUP_PSYN_LP 70
#define REGR_WADDR_TWSYN_LP 71

// Bit ID in registers for Axilite : mhh core 0
// ---
// REGW_CONTROL : Global control register
#define BIT_CONTROL_RESET 0
#define BIT_CONTROL_EN_CORE 1
#define BIT_CONTROL_STIM_TRIG_PS 2

// REGW_CONTROL_MON : Monitoring control register
#define BIT_CONTROL_MON_EN_VNEW 0
#define BIT_CONTROL_MON_EN_SPK 1
#define BIT_CONTROL_MON_EN_DAC 2
#define BIT_CONTROL_MON_WEN_SEL_MON_VNEW 3
#define BIT_CONTROL_MON_WEN_SEL_MON_SPK 4

// REGW_SETUP_SYN : Synapses setup
#define BIT_SETUP_SYN_WEN_BV_RATE 0
#define BIT_SETUP_SYN_WEN_TV_RATE 1
#define BIT_SETUP_SYN_WEN_SN_GABAB 2

// REGW_SEL_MON : Monitoring data id
#define BIT_DATA_SEL_MON_VNEW 0
#define BIT_DATA_SEL_MON_SPK 1

#endif
