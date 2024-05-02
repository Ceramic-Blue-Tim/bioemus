#ifndef __HW_CONFIG_SYNAPSES_H__
#define __HW_CONFIG_SYNAPSES_H__
#define TYPE_WEIGHT_SIZE 16
#define DSP_LATENCY 4
#define WEIGHT_SIZE 14

#define INT_W 2
#define DEC_W 12
#define SHIFT_DIV_FP_ISYN 4

// Synapse parameters
#define NB_PSYN 18
#define PSYN_WIDTH 32
#define PSYN_BIT_WEN 31
#define PSYN_WIDTH_WDATA 26
#define PSYN_WIDTH_WSEL 5
#define PSYN_ID_AMPA_K1 0
#define PSYN_ID_AMPA_K2 1
#define PSYN_ID_AMPA_GSYN 2
#define PSYN_ID_AMPA_ESYN 3
#define PSYN_ID_NMDA_K1 4
#define PSYN_ID_NMDA_K2 5
#define PSYN_ID_NMDA_GSYN 6
#define PSYN_ID_NMDA_ESYN 7
#define PSYN_ID_GABAA_K1 8
#define PSYN_ID_GABAA_K2 9
#define PSYN_ID_GABAA_GSYN 10
#define PSYN_ID_GABAA_ESYN 11
#define PSYN_ID_GABAB_K1 12
#define PSYN_ID_GABAB_K2 13
#define PSYN_ID_GABAB_K3 14
#define PSYN_ID_GABAB_K4 15
#define PSYN_ID_GABAB_GSYN 16
#define PSYN_ID_GABAB_ESYN 17

// Synrates tables
#define SYNRATE_TABLE_VMIN -76.0
#define SYNRATE_TABLE_VMAX 52.0
#define SYNRATE_TABLE_DEPTH 2048

// Table SN GABAb
#define SN_GABAB_TABLE_MIN 0.0
#define SN_GABAB_TABLE_MAX 8.0
#define SN_GABAB_TABLE_DEPTH 2048

#define NB_RAM_TWSYN 64
#define RAMDEPTH_TWSYN 4096
#define RAMWIDTH_TWSYN 72
#define NB_DSP_WMB_SYNAPSES 96
#define NB_TYPES_OF_SYNAPSES 4
#define TSYN_ID_AMPA 0
#define TSYN_ID_GABAA 2
#define TSYN_ID_GABAB 3
#define TSYN_ID_NMDA 1

#define SFI_GABAB_K3_INT -6
#define SFI_GABAB_K3_DEC 24
#define SFI_GABAB_K4_INT -8
#define SFI_GABAB_K4_DEC 26
#endif
