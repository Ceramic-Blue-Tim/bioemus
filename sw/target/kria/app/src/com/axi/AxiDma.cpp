/*
*! @title      Axi DMA using proxy driver
*! @file       AxiDma.cpp
*! @author     Romain Beaubois
*! @date       08 Nov 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2022 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! 
*! @details
*! > **08 Nov 2022** : file creation (RB)
*/

#include "AxiDma.h"
#include "string.h"

#if defined(DBG_PROBE_TSTAMP_STIM) || defined(DBG_PROBE_TSTAMP_SPIKES) || defined(DBG_PROBE_TSTAMP_WAVES)
	#include <chrono>
	#include <vector>
#endif

static volatile int stop = 0;
static volatile int end_rx_spikes = 0;
static volatile int end_rx_vmem = 0;
static int fd_dma_intr_rx;

zmq::context_t ctx;
zmq::socket_t sock_spk_mon(ctx, zmq::socket_type::push);
zmq::socket_t sock_vmem_mon(ctx, zmq::socket_type::push);
zmq::socket_t sock_ext_stim(ctx, zmq::socket_type::pull);

#ifdef DBG_PROBE_TSTAMP_STIM
	vector<chrono::time_point<std::chrono::high_resolution_clock>> tstamp_stim;
#endif

//   █████  ██   ██ ██     ██████  ███    ███  █████  
//  ██   ██  ██ ██  ██     ██   ██ ████  ████ ██   ██ 
//  ███████   ███   ██     ██   ██ ██ ████ ██ ███████ 
//  ██   ██  ██ ██  ██     ██   ██ ██  ██  ██ ██   ██ 
//  ██   ██ ██   ██ ██     ██████  ██      ██ ██   ██ 
//                                                    
//                                                    
AxiDma::AxiDma(struct sw_config swconfig){
    int r;

	if(swconfig.en_zmq_stim){
		// Open the file descriptors for each tx channel and map the kernel driver memory into user space
		for (int i = 0; i < TX_CHANNEL_COUNT; i++) {
			// Generate channel file name
			string fpath_tx_channel = "/dev/" + _tx_channel_names[i];

			// Open file
			_tx_channels[i].fd = open(fpath_tx_channel.c_str(), O_RDWR);
			r = (_tx_channels[i].fd < 1) ? EXIT_FAILURE : EXIT_SUCCESS;
			statusPrint(r, "Open DMA proxy device file " + fpath_tx_channel);
			if(r==EXIT_FAILURE)
				exit(EXIT_FAILURE);
			
			// Map memory
			_tx_channels[i].buf_ptr = (struct channel_buffer *)mmap(NULL, sizeof(struct channel_buffer) * TX_BUFFER_COUNT,
											PROT_READ | PROT_WRITE, MAP_SHARED, _tx_channels[i].fd, 0);
			r = (_tx_channels[i].buf_ptr == MAP_FAILED) ? EXIT_FAILURE : EXIT_SUCCESS;
			statusPrint(r, "Map " + string(fpath_tx_channel));
			if(r==EXIT_FAILURE)
				exit(EXIT_FAILURE);
		}
	}

	// Open the file descriptors for each rx channel and map the kernel driver memory into user space
	for (int i = 0; i < RX_CHANNEL_COUNT; i++) {
		// Generate channel file name
		string fpath_rx_channel = "/dev/" + _rx_channel_names[i];

		// Open file
		_rx_channels[i].fd = open(fpath_rx_channel.c_str(), O_RDWR);
		r = (_rx_channels[i].fd < 1) ? EXIT_FAILURE : EXIT_SUCCESS;
		statusPrint(r, "Open DMA proxy device file " + string(fpath_rx_channel));
		if(r==EXIT_FAILURE)
			exit(EXIT_FAILURE);
		
		// Map memory
		_rx_channels[i].buf_ptr = (struct channel_buffer *)mmap(NULL, sizeof(struct channel_buffer) * RX_BUFFER_COUNT,
										PROT_READ | PROT_WRITE, MAP_SHARED, _rx_channels[i].fd, 0);
		r = (_rx_channels[i].buf_ptr == MAP_FAILED) ? EXIT_FAILURE : EXIT_SUCCESS;
		statusPrint(r, "Map " + string(fpath_rx_channel));
		if(r==EXIT_FAILURE)
			exit(EXIT_FAILURE);
	}
}

// void AxiDma::setupTxThread(){
// 	// int newprio = 20;
// 	// struct sched_param param;

// 	// /* The transmit thread should be lower priority than the receive
// 	//  * Get the default attributes and scheduling param
// 	//  */
// 	// pthread_attr_init (&_tx_tattr);
// 	// pthread_attr_getschedparam (&_tx_tattr, &param);

// 	// /* Set the transmit priority to the lowest
// 	//  */
// 	// param.sched_priority = newprio;
// 	// pthread_attr_setschedparam (&_tx_tattr, &param);
// }

int AxiDma::monitoring(struct sw_config swconfig, HwControl hw_ctrl){
	thread_args rx_th_args[RX_CHANNEL_COUNT];
	thread_args tx_th_args[TX_CHANNEL_COUNT];

	string fname			= swconfig.fpath_hwconfig;
	size_t pos_name			= fname.rfind("_");
	size_t pos_ext			= fname.rfind(".");
	fname					= fname.substr(pos_name + 1, pos_ext - pos_name - 1);
	string fpath_save_spk	= swconfig.save_path + string("raster_") +  fname + ((swconfig.bin_fmt_save_spikes)?".bin":".csv");
	string fpath_save_vmem	= swconfig.save_path + string("waves_")  +  fname + ((swconfig.bin_fmt_save_vmem)?".bin":".csv");
	string fpath_save_stim	= swconfig.save_path + string("stim_")   +  fname + ((true)?".bin":".csv");

	/**** Thread arguments ****/
	// Spikes
	rx_th_args[TH_ID_SPK_MON].th_name				= (char*)_rx_channel_names[TH_ID_SPK_MON].c_str();
	rx_th_args[TH_ID_SPK_MON].chan_ptr				= &_rx_channels[TH_ID_SPK_MON];
	rx_th_args[TH_ID_SPK_MON].transfer_size_bytes	= (DATAWIDTH_TIME_STEP+NB_NRN)/8*swconfig.nb_tstamp_per_spk_transfer;
	rx_th_args[TH_ID_SPK_MON].nb_transfer			= swconfig.emulation_time_s*1e3 / (TIME_STEP_MS*SUBSAMPLING_MON_SPK*swconfig.nb_tstamp_per_spk_transfer);
	rx_th_args[TH_ID_SPK_MON].en_send				= swconfig.en_zmq_spikes;
	rx_th_args[TH_ID_SPK_MON].en_save				= swconfig.save_local_spikes;
	rx_th_args[TH_ID_SPK_MON].bin_fmt_save			= swconfig.bin_fmt_save_spikes;
	rx_th_args[TH_ID_SPK_MON].bin_fmt_send			= swconfig.bin_fmt_send_spikes;
	rx_th_args[TH_ID_SPK_MON].save_path				= (char*)fpath_save_spk.c_str();

	// Waves
	rx_th_args[TH_ID_VMEM_MON].th_name				= (char*)_rx_channel_names[TH_ID_VMEM_MON].c_str();
	rx_th_args[TH_ID_VMEM_MON].chan_ptr				= &_rx_channels[TH_ID_VMEM_MON];
	rx_th_args[TH_ID_VMEM_MON].transfer_size_bytes	= (DATAWIDTH_TIME_STEP+DATAWIDTH_MON_VMEM_DMA*MAX_NRN_MON_VMEM_DMA)/8*swconfig.nb_tstep_per_vmem_transfer;
	rx_th_args[TH_ID_VMEM_MON].nb_transfer			= swconfig.emulation_time_s*1e3 / (TIME_STEP_MS*swconfig.nb_tstep_per_vmem_transfer);
	rx_th_args[TH_ID_VMEM_MON].en_send				= swconfig.en_zmq_vmem;
	rx_th_args[TH_ID_VMEM_MON].en_save				= swconfig.save_local_vmem;
	rx_th_args[TH_ID_VMEM_MON].bin_fmt_send			= swconfig.bin_fmt_send_vmem;
	rx_th_args[TH_ID_VMEM_MON].bin_fmt_save			= swconfig.bin_fmt_save_vmem;
	rx_th_args[TH_ID_VMEM_MON].save_path			= (char*)fpath_save_vmem.c_str();

	// External stimulation
	tx_th_args[TH_ID_EXT_STIM].th_name				= (char*)_tx_channel_names[TH_ID_EXT_STIM].c_str();
	tx_th_args[TH_ID_EXT_STIM].chan_ptr				= &_tx_channels[TH_ID_EXT_STIM];
	tx_th_args[TH_ID_EXT_STIM].transfer_size_bytes	= (NB_NRN*DATAWIDTH_DMA_STIM)/8;
	tx_th_args[TH_ID_EXT_STIM].nb_transfer			= -1;
	tx_th_args[TH_ID_EXT_STIM].en_send				= false;
	tx_th_args[TH_ID_EXT_STIM].en_save				= false;
	tx_th_args[TH_ID_EXT_STIM].bin_fmt_send			= false;
	tx_th_args[TH_ID_EXT_STIM].bin_fmt_save			= false;
	tx_th_args[TH_ID_EXT_STIM].save_path			= (char*)fpath_save_stim.c_str();

	/**** Bind ZeroMQ sockets ****/
	// Bind spikes stream
	if (swconfig.en_zmq_spikes)
		sock_spk_mon.bind(swconfig.ip_zmq_spikes);
	// Bind waves stream
	if (swconfig.en_zmq_vmem)
		sock_vmem_mon.bind(swconfig.ip_zmq_vmem);
	// Connect external stimulation
	if (swconfig.en_zmq_stim){
		int t_out_poll_ms = 500;
		sock_ext_stim.set(zmq::sockopt::rcvtimeo, t_out_poll_ms);
		sock_ext_stim.connect(swconfig.ip_zmq_stim);

		// Wait for first stim to start
		zmq::message_t zmq_msg;
		zmq::recv_result_t res;

		// Wait an external trigger to start
		infoPrint(0, "Waiting for stimulation trigger to start");
		do{
			res = sock_ext_stim.recv(zmq_msg, zmq::recv_flags::none);
		// }while( !res.has_value() || (res.has_value() && (res.value() != 0)) ); // supposely correct but has_value=false on time out
		}while( !res.has_value() );
	}

	#ifdef DBG_PROBE_TSTAMP_STIM
		tstamp_stim.push_back(chrono::high_resolution_clock::now());
	#endif

    infoPrint(0, "Enable calculation core");
    int r = hw_ctrl.enableCore();
    statusPrint(r, "Enable calculation core");

	// /**** Setup threads attributes ****/
	// struct sched_param sch_params;
	// sch_params.sched_priority = 20;
	// for (int i = 0; i < TX_CHANNEL_COUNT; i++){
	// 	if(pthread_setschedparam(_tx_channels[i].t.native_handle(), SCHED_RR, &sch_params)) {
	// 		cerr << "Failed to set Thread scheduling : " << std::strerror(errno) << endl;
	// 	}
	// }

	/**** Start threads ****/
	if (swconfig.save_local_spikes || swconfig.en_zmq_spikes)
		_rx_channels[TH_ID_SPK_MON].t	= thread(&AxiDma::rxThreadSpikes,	this, &rx_th_args[TH_ID_SPK_MON]);
	if (swconfig.save_local_vmem || swconfig.en_zmq_vmem)
		_rx_channels[TH_ID_VMEM_MON].t	= thread(&AxiDma::rxThreadVmem,		this, &rx_th_args[TH_ID_VMEM_MON]);
	if (swconfig.en_zmq_stim)
		_tx_channels[TH_ID_EXT_STIM].t	= thread(&AxiDma::txExtStim,		this, &tx_th_args[TH_ID_EXT_STIM]);

	/**** Join ****/
	if (swconfig.save_local_spikes ||swconfig.en_zmq_spikes)
		_rx_channels[TH_ID_SPK_MON].t.join();
	if (swconfig.save_local_vmem ||swconfig.en_zmq_vmem)
		_rx_channels[TH_ID_VMEM_MON].t.join();
	if (swconfig.en_zmq_stim)
		_tx_channels[TH_ID_EXT_STIM].t.join();

	/**** Clean ****/
	if (swconfig.save_local_spikes ||swconfig.en_zmq_spikes){
		munmap(_rx_channels[TH_ID_SPK_MON].buf_ptr, sizeof(struct channel_buffer));
		close(_rx_channels[TH_ID_SPK_MON].fd);
	}
	if (swconfig.save_local_vmem ||swconfig.en_zmq_vmem){
		munmap(_rx_channels[TH_ID_VMEM_MON].buf_ptr, sizeof(struct channel_buffer));
		close(_rx_channels[TH_ID_VMEM_MON].fd);
	}
	if (swconfig.en_zmq_stim){
		munmap(_tx_channels[TH_ID_EXT_STIM].buf_ptr, sizeof(struct channel_buffer));
		close(_tx_channels[TH_ID_EXT_STIM].fd);
	}

	#ifdef DBG_PROBE_TSTAMP_STIM
		ofstream tstamp_file (swconfig.save_path + "tstamp_stim_" +  fname + ".csv");

		if(!tstamp_file.is_open()){
			cerr << "Can't open tstamp file" << endl;
			return EXIT_FAILURE;	
		}
		
		for (size_t i = 0; i < tstamp_stim.size(); i++){
			auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(tstamp_stim[i].time_since_epoch()).count();
			tstamp_file << microseconds << endl;
		}

		tstamp_file.close();
	#endif

	return EXIT_SUCCESS;
}

//  ████████ ██   ██     ███████ ██   ██ ████████     ███████ ████████ ██ ███    ███ 
//     ██     ██ ██      ██       ██ ██     ██        ██         ██    ██ ████  ████ 
//     ██      ███       █████     ███      ██        ███████    ██    ██ ██ ████ ██ 
//     ██     ██ ██      ██       ██ ██     ██             ██    ██    ██ ██  ██  ██ 
//     ██    ██   ██     ███████ ██   ██    ██        ███████    ██    ██ ██      ██ 
//                                                                                   
//                                                                        
void AxiDma::txExtStim(void* args){
	struct thread_args* args_struct = (struct thread_args*)(args);
	struct channel* channel_ptr = args_struct->chan_ptr;
	int transfer_size_bytes	= args_struct->transfer_size_bytes;
	bool save			= args_struct->en_save;
	bool send			= args_struct->en_send;
	char* th_name		= args_struct->th_name;
	char* save_path		= args_struct->save_path;

    int r;
    int buffer_id = 0;

	// Open file to save data
	FILE* f;
	string fpath = save_path;
	if(save){
		f = fopen(fpath.c_str(), "w");
		r = (f==NULL) ? EXIT_FAILURE : EXIT_SUCCESS;
		if (r == EXIT_FAILURE){
			infoPrint(0, "OOF! Failed opening saving file for dma tx data");
			exit(EXIT_FAILURE);
		}
		infoPrint(0, "Open save file" + fpath);
	}

	if (transfer_size_bytes > BUFFER_SIZE){
		statusPrint(EXIT_FAILURE, "Transfer size of ext stim larger than DMA buffer");
	}
	
	zmq::message_t zmq_msg;
	zmq::recv_result_t res;
	
	// Start all buffers being sent
	while(!stop){
		// Get ZeroMQ frame
		do{
			res = sock_ext_stim.recv(zmq_msg, zmq::recv_flags::none);
			if ( (end_rx_spikes == 1) || (end_rx_vmem == 1) )
				break;
			
		// }while( !res.has_value() || (res.has_value() && (res.value() != 0)) ); // supposely correct but has_value=false on time out
		}while( !res.has_value() );
		
		// Get time stamp
		#ifdef DBG_PROBE_TSTAMP_STIM
			tstamp_stim.push_back(chrono::high_resolution_clock::now());
		#endif

		if ( (end_rx_spikes == 1) || (end_rx_vmem == 1) )
			break;

		unsigned int* rx_buf_stim_vptr_u32 =(unsigned int*)zmq_msg.data();

		// Save zmq data
		// if(save){
			// Timing assessment
			// uint64_t tstart = get_posix_clock_time_usec();

				// Save as binary (faster)
				// fwrite(buffer, transfer_size_bytes/sizeof(unsigned int), sizeof(unsigned int),  f);

				// Save as csv alike for debug (way slower)
				// for (int j = 0; j < transfer_size_bytes/sizeof(unsigned int); j++){
				// 	fprintf(f, "%u;", rx_buf_stim_vptr_u32[j]);
				// }
				// fprintf(f, "\n");
			
			// uint64_t tstop = get_posix_clock_time_usec();
			// printf("Elapsed time: %lu µs\n", tstop-tstart);
		// }
		
		// Pointer to current buffer
		unsigned int *buffer = (unsigned int *)&channel_ptr->buf_ptr[buffer_id].buffer;

		// Fill buffer with data received from ZeroMQ
		for (int j = 0; j < transfer_size_bytes / sizeof(unsigned int); j++)
			buffer[j] = rx_buf_stim_vptr_u32[j];

		// DMA sending
		channel_ptr->buf_ptr[buffer_id].length = transfer_size_bytes; // transfer length (in bytes)
		ioctl(channel_ptr->fd, START_XFER, &buffer_id);	// start transfer
		ioctl(channel_ptr->fd, FINISH_XFER, &buffer_id); // wait for transfer end

        r = (channel_ptr->buf_ptr[buffer_id].status != channel_buffer::proxy_status::PROXY_NO_ERROR) ? EXIT_FAILURE : EXIT_SUCCESS;
		if (r == EXIT_SUCCESS){
			statusPrint(r, "Insert external stimulation");
		}

		// Circular list of buffer
		buffer_id += BUFFER_INCREMENT;
		buffer_id %= TX_BUFFER_COUNT;
	}

	if (save)
		fclose(f);
}

//  ██████  ██   ██     ███████ ██████  ██ ██   ██ ███████ ███████ 
//  ██   ██  ██ ██      ██      ██   ██ ██ ██  ██  ██      ██      
//  ██████    ███       ███████ ██████  ██ █████   █████   ███████ 
//  ██   ██  ██ ██           ██ ██      ██ ██  ██  ██           ██ 
//  ██   ██ ██   ██     ███████ ██      ██ ██   ██ ███████ ███████ 
//                                                                 
//                                                      

void AxiDma::rxThreadSpikes(void* args){
	struct thread_args* args_struct = (struct thread_args*)(args);
	struct channel* channel_ptr = args_struct->chan_ptr;
	int transfer_size_bytes		= args_struct->transfer_size_bytes;
	int nb_transfer				= args_struct->nb_transfer;
	bool save					= args_struct->en_save;
	bool send					= args_struct->en_send;
	bool bin_fmt_save			= args_struct->bin_fmt_save;
	bool bin_fmt_send			= args_struct->bin_fmt_send;
	char* th_name				= args_struct->th_name;
	char* save_path				= args_struct->save_path;
    int r;

	//
	int in_progress_count	= 0;
    int buffer_id			= 0;
	int rx_counter			= 0;
	int nb_read_dma			= nb_transfer;

	#ifdef DBG_PROBE_TSTAMP_SPIKES
		vector<chrono::time_point<std::chrono::high_resolution_clock>> tstamp_spikes;
	#endif

	// Open file to save data
	FILE* f;
	string fpath = save_path;

	if (save){
		f = fopen(fpath.c_str(), "w");
		r = (f==NULL) ? EXIT_FAILURE : EXIT_SUCCESS;
		if (r == EXIT_FAILURE){
			infoPrint(0, "OOF! Failed opening saving file for rx channel spikes");
			exit(EXIT_FAILURE);
		}

		if (!bin_fmt_save){
			fprintf(f, "time;neuron_id\n");
		}	
	}
	

	// Calculate number of buffer required to perform the required transfer size
	int nb_buffer_for_transfer;
	if (transfer_size_bytes > BUFFER_SIZE){
		transfer_size_bytes		= BUFFER_SIZE;
		nb_buffer_for_transfer	= transfer_size_bytes/BUFFER_SIZE;
	}
	else{
		nb_buffer_for_transfer = 1;
	}

	for (int i = 0; i < nb_read_dma; i++){
		// /!\ hypothesis: for now transfers always are smaller than buffer size
		// need to add extra handling of buffer of larger size
		rx_counter			= 0;
		in_progress_count	= 0;
                                                               
		// One buffer per transfer but buffer are circular for next transfer
		channel_ptr->buf_ptr[buffer_id].length = transfer_size_bytes;
		ioctl(channel_ptr->fd, START_XFER, &buffer_id);
		ioctl(channel_ptr->fd, FINISH_XFER, &buffer_id);
		r = (channel_ptr->buf_ptr[buffer_id].status != channel_buffer::proxy_status::PROXY_NO_ERROR) ? EXIT_FAILURE : EXIT_SUCCESS;
		
		if(r==EXIT_FAILURE)
			exit(EXIT_FAILURE);

		unsigned int *buffer = (unsigned int*)(&channel_ptr->buf_ptr[buffer_id].buffer);

		if(save){
			unsigned int tstamp;
			unsigned int write_cnt = 0;

			// uint64_t tstart = get_posix_clock_time_usec();

			// Save as binary

			if(bin_fmt_save){
				fwrite(buffer, transfer_size_bytes/sizeof(unsigned int), sizeof(unsigned int),  f);
			}else{
				vector<uint32_t> x; // TODO : check dynamic allocation
				vector<uint32_t> y;
				// For each frame
				const unsigned int frame_size = (DATAWIDTH_TIME_STEP+NB_NRN)/(8*sizeof(unsigned int));
				for (int j = 0; j < ((transfer_size_bytes/sizeof(unsigned int))/frame_size); j++){ 
					tstamp = buffer[frame_size*j];
					// For all spike registers
					for (int k = 0; k < NB_NRN/32; k++){
						// Detect spike for all bits
						for (int b = 0; b < 32; b++){
							if ((buffer[frame_size*j + k + 1] & (1<<b)) != 0){
								x.push_back(tstamp);
								y.push_back(32*k + b);
							}
						}
					}
				}

				// Write in file
				for (int z = 0; z < x.size(); z++)
					fprintf(f, "%u;%u\n", x[z], y[z]);
				x.clear();
				y.clear();
			}

			// uint64_t tstop = get_posix_clock_time_usec();
			// printf("Elapsed time: %lu µs\n", tstop-tstart);
		}
		if(send){
			if(bin_fmt_send){
				sock_spk_mon.send(zmq::buffer(buffer, transfer_size_bytes)); // TODO : check timing if remove zmq::send_flags::dontwait
			}
			else{
				uint32_t spk_cnt[NB_NRN];
				memset(spk_cnt, 0, sizeof(spk_cnt));

				const unsigned int frame_size = (DATAWIDTH_TIME_STEP+NB_NRN)/(8*sizeof(unsigned int));
				unsigned int tstamp = 0;

				for (int j = 0; j < ((transfer_size_bytes/sizeof(unsigned int))/frame_size); j++){
                    tstamp = buffer[frame_size*j];

					// For all spike registers
					for (int k = 0; k < NB_NRN/32; k++){
						// Detect spike for all bits
						for (int b = 0; b < 32; b++){
							if ((buffer[frame_size*j + k + 1] & (1<<b)) != 0)
								spk_cnt[32*k+b] += 1;
						}
					}
				}

				sock_spk_mon.send(zmq::buffer(spk_cnt, NB_NRN*sizeof(unsigned int)));
			}
		}

		/* Flip to next buffer treating them as a circular list, and possibly skipping some
		* to show the results when prefetching is not happening
		*/
		buffer_id += BUFFER_INCREMENT;
		buffer_id %= RX_BUFFER_COUNT;

		// If stop required, graciously exit after all transfers done
		if (stop == 1)
			break;		
	}

	end_rx_spikes = 1;

	if (save)
		fclose(f);

	#ifdef DBG_PROBE_TSTAMP_SPIKES
		ofstream tstamp_file (swconfig.save_path + "tstamp_spikes_" +  fname + ".csv");

		if(!tstamp_file.is_open()){
			cerr << "Can't open tstamp file" << endl;
			return EXIT_FAILURE;	
		}
		
		for (size_t i = 0; i < tstamp_spikes.size(); i++){
			auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(tstamp_spikes[i].time_since_epoch()).count();
			tstamp_file << microseconds << endl;
		}

		tstamp_file.close();
	#endif
}

//  ██████  ██   ██     ██    ██ ███    ███ ███████ ███    ███ 
//  ██   ██  ██ ██      ██    ██ ████  ████ ██      ████  ████ 
//  ██████    ███       ██    ██ ██ ████ ██ █████   ██ ████ ██ 
//  ██   ██  ██ ██       ██  ██  ██  ██  ██ ██      ██  ██  ██ 
//  ██   ██ ██   ██       ████   ██      ██ ███████ ██      ██ 
//                                                             
//                                                             
void AxiDma::rxThreadVmem(void* args){
	struct thread_args* args_struct = (struct thread_args*)(args);
	struct channel* channel_ptr = args_struct->chan_ptr;
	int transfer_size_bytes		= args_struct->transfer_size_bytes;
	int nb_transfer				= args_struct->nb_transfer;
	bool save					= args_struct->en_save;
	bool send					= args_struct->en_send;
	bool bin_fmt_save			= args_struct->bin_fmt_save;
	bool bin_fmt_send			= args_struct->bin_fmt_send;
	char* th_name				= args_struct->th_name;
	char* save_path				= args_struct->save_path;
    int r;

	//
	int in_progress_count	= 0;
    int buffer_id			= 0;
	int rx_counter			= 0;
	int nb_read_dma			= nb_transfer;


	#ifdef DBG_PROBE_TSTAMP_WAVES
		vector<chrono::time_point<std::chrono::high_resolution_clock>> tstamp_waves;
	#endif

	// Open file to save data
	FILE* f;
	string fpath = save_path;

	if (save){
		f = fopen(fpath.c_str(), "w");
		r = (f==NULL) ? EXIT_FAILURE : EXIT_SUCCESS;
		if (r == EXIT_FAILURE){
			infoPrint(0, "OOF! Failed opening saving file for rx channel spikes");
			exit(EXIT_FAILURE);
		}
	}
	

	// Calculate number of buffer required to perform the required transfer size
	int nb_buffer_for_transfer;
	if (transfer_size_bytes > BUFFER_SIZE){
		transfer_size_bytes		= BUFFER_SIZE;
		nb_buffer_for_transfer	= transfer_size_bytes/BUFFER_SIZE;
	}
	else{
		nb_buffer_for_transfer = 1;
	}

	for (int i = 0; i < nb_read_dma; i++){
		// /!\ hypothesis: for now transfers always are smaller than buffer size
		// need to add extra handling of buffer of larger size
		rx_counter			= 0;
		in_progress_count	= 0;
                                                               
		// One buffer per transfer but buffer are circular for next transfer
		channel_ptr->buf_ptr[buffer_id].length = transfer_size_bytes;
		ioctl(channel_ptr->fd, START_XFER, &buffer_id);
		ioctl(channel_ptr->fd, FINISH_XFER, &buffer_id);
		r = (channel_ptr->buf_ptr[buffer_id].status != channel_buffer::proxy_status::PROXY_NO_ERROR) ? EXIT_FAILURE : EXIT_SUCCESS;
		
		// string msg = "DMA Proxy transfers ";
		// msg += "# buffers used "		+ to_string(nb_buffer_for_transfer);
		// msg += ", # completed "		+ to_string(rx_counter);
		// msg += ", # in progress "	+ to_string(in_progress_count);
		// statusPrint(r, msg);
		
		if(r==EXIT_FAILURE)
			exit(EXIT_FAILURE);

		unsigned int *buffer = (unsigned int*)(&channel_ptr->buf_ptr[buffer_id].buffer);

		// Save locally as binary
		if(save){
			// uint64_t tstart = get_posix_clock_time_usec();
			
			// Binary write
			fwrite(buffer, transfer_size_bytes/sizeof(unsigned int), sizeof(unsigned int),  f);

			// CSV write
			// TODO: implement csv write (f << %f)

			// uint64_t tstop = get_posix_clock_time_usec();
			// printf("Elapsed time: %lu µs\n", tstop-tstart);
		}
		if(send){
			sock_vmem_mon.send(zmq::buffer(buffer, transfer_size_bytes)); // TODO : check timing if remove zmq::send_flags::dontwait
		}

		/* Flip to next buffer treating them as a circular list, and possibly skipping some
		* to show the results when prefetching is not happening
		*/
		buffer_id += BUFFER_INCREMENT;
		buffer_id %= RX_BUFFER_COUNT;

		// If stop required, graciously exit after all transfers done
		if (stop == 1)
			break;		
	}

	end_rx_vmem = 1;

	if (save)
		fclose(f);

	#ifdef DBG_PROBE_TSTAMP_WAVES
		ofstream tstamp_file (swconfig.save_path + "tstamp_waves_" +  fname + ".csv");

		if(!tstamp_file.is_open()){
			cerr << "Can't open tstamp file" << endl;
			return EXIT_FAILURE;	
		}
		
		for (size_t i = 0; i < tstamp_waves.size(); i++){
			auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(tstamp_waves[i].time_since_epoch()).count();
			tstamp_file << microseconds << endl;
		}

		tstamp_file.close();
	#endif
}