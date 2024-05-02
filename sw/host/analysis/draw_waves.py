import os
import struct
import numpy as np
import matplotlib.pyplot as plt

def draw_waves(dirpath, wave_list, plot_time_s, sel_nrn, max_nb_neurons_wave_monitor=16, dt=2**-5):

    fpath_list   = [dirpath + "waves_" + e + ".csv" for e in wave_list]
    plot_time_ms = int(plot_time_s*1e3)
    dtype        = np.dtype(np.float32)

    for z in range(len(wave_list)):
        nb_samples   = int(os.path.getsize(fpath_list[z])/dtype.itemsize)
        data_fpga    = np.fromfile(fpath_list[z], dtype=dtype, count=nb_samples)
        nb_lines     = int(len(data_fpga)/(max_nb_neurons_wave_monitor+1))

        # Reshape to tstamp, neurons
        data_fpga       = data_fpga.reshape(nb_lines, (max_nb_neurons_wave_monitor+1))
        # Reconstruct time stamp from float
        data_fpga[:,0]  = [int.from_bytes(bytearray(struct.pack("f", data_fpga[x, 0])), "little")*dt for x in range(nb_lines)]
        # Crop to range to print
        data_fpga = data_fpga[0:int(plot_time_ms*(1/dt)), :]

        t = data_fpga[:, 0]
        plt.figure("Membrane potential: {}".format(wave_list[z]))
        for i in sel_nrn:
            plt.subplot(len(sel_nrn), 1, i+1)
            plt.plot(t, data_fpga[:, i+1])
            plt.xlabel("Time (ms)")
            plt.ylabel("Amplitude (mV)")
        plt.show()