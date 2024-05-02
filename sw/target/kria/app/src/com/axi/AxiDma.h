/*
*! @title      Axi DMA object
*! @file       AxiDma.h
*! @author     Romain Beaubois
*! @date       24 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **24 Aug 2022** : file creation (RB)
*/

#ifndef __AXIDMA_H__
#define __AXIDMA_H__

#include <iostream>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <string.h>
#include <algorithm>

#include <unistd.h>
#include <sys/ioctl.h>
#include <thread>
#include <time.h>
#include <sys/time.h>
#include <signal.h>
#include <sched.h>
#include <errno.h>
#include <sys/param.h>
#include <linux/input.h>
#include <zmq.hpp>

#include "CustomPrint.h"
#include "dma-proxy.h" // DMA proxy driver header
#include "SwConfigParser.h"
#include "HwControl.h"
#include "hw_config_com.h"
#include "hw_config_monitoring.h"
#include "hw_config_system.h"

// DEBUG time stamp probes
// #define DBG_PROBE_TSTAMP_STIM
// #define DBG_PROBE_TSTAMP_SPIKES
// #define DBG_PROBE_TSTAMP_WAVES

// Performance assessment
static uint64_t get_posix_clock_time_usec (){
    struct timespec ts;

    if (clock_gettime (CLOCK_MONOTONIC, &ts) == 0)
        return (uint64_t) (ts.tv_sec * 1000000 + ts.tv_nsec / 1000);
    else
        return 0;
}

// TODO : make it generic in object to instance several DMA objects
// Number of channels instanciated by the driver
#define TX_CHANNEL_COUNT    1
#define RX_CHANNEL_COUNT    2
#define TH_ID_SPK_MON       0
#define TH_ID_VMEM_MON      1
#define TH_ID_EXT_STIM      0

struct channel {
	struct channel_buffer *buf_ptr;
	int fd;
	thread t;
};

struct thread_args{
    char* th_name;
    struct channel *chan_ptr;
    int transfer_size_bytes;
    int nb_transfer;
    bool en_send;
    bool en_save;
    bool bin_fmt_save;
    bool bin_fmt_send;
    char* save_path;
};

// Functions prototypes
static void sigint(int a);

using namespace std;
class AxiDma{
    public:
        private :
            const string _tx_channel_names[TX_CHANNEL_COUNT] = { "dma_proxy_tx_ext_stim" };
            const string _rx_channel_names[RX_CHANNEL_COUNT] = { "dma_proxy_rx_spk", "dma_proxy_rx_vmem"};
            struct channel _tx_channels[TX_CHANNEL_COUNT];
            struct channel _rx_channels[RX_CHANNEL_COUNT];

            void rxThreadSpikes(void* args);
            void rxThreadVmem(void* args);
            void txExtStim(void* args);
        public :
            // Methods
            AxiDma(struct sw_config swconfig);
            int monitoring(struct sw_config swconfig, HwControl hw_ctrl);
};

#endif