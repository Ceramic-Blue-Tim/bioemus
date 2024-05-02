#ifndef __HW_CONFIG_MONITORING_H__
#define __HW_CONFIG_MONITORING_H__

// Globals
// ---
#define DATAWIDTH_MON_NID 32
#define DATAWIDTH_TIME_STEP 32

// Waves DAC
// ---
#define NB_CHANNELS_DAC 8

// Spikes DMA
// ---
#define NB_REGS_SPK_MON 32
#define MAX_NB_PACKETS_MON_SPK_DMA 256
#define DATAWIDTH_MAX_NB_PACKETS_MON_SPK_DMA 8
#define DATAWIDTH_MON_SPK_DMA 32
#define SUBSAMPLING_MON_SPK 32

// Waves DMA
// ---
#define MAX_NRN_MON_VMEM_DMA 16
#define MAX_NB_PACKETS_MON_VMEM_DMA 480
#define DATAWIDTH_MAX_NB_PACKETS_MON_VMEM_DMA 9
#define DATAWIDTH_MON_VMEM_DMA 32

// External stim
// ---
#define DATAWIDTH_DMA_STIM 32

#endif
