import sys
import os
import struct
import numpy as np

NB_NEURONS_WAVE_MONITOR = 16
DT = 2**-5
# PLOT_LIB = "matplot"
PLOT_LIB = "plotext"

fpath        = sys.argv[1]
plot_time_ms = int(sys.argv[2])
sel_nrn      = list(map(int, sys.argv[3].split(',')))
dtype        = np.dtype(np.float32)
nb_samples   = int(os.path.getsize(fpath)/dtype.itemsize)
data_fpga    = np.fromfile(fpath, dtype=dtype, count=nb_samples)
nb_lines     = int(len(data_fpga)/(NB_NEURONS_WAVE_MONITOR+1))

# Reshape to tstamp, neurons
data_fpga       = data_fpga.reshape(nb_lines, (NB_NEURONS_WAVE_MONITOR+1))
# Reconstruct time stamp from float
data_fpga[:,0]  = [int.from_bytes(bytearray(struct.pack("f", data_fpga[x, 0])), "little")*2**(-5) for x in range(nb_lines)]
# Crop to range to print
data_fpga = data_fpga[0:int(plot_time_ms*(1/DT)), :]

t = data_fpga[:, 0]
if PLOT_LIB == "matplot":
    import matplotlib.pyplot as plt
    plt.figure()
    for i in range(NB_NEURONS_WAVE_MONITOR):
        plt.subplot(NB_NEURONS_WAVE_MONITOR, 1, i+1)
        plt.plot(t, data_fpga[:, i+1])
    plt.show()

elif PLOT_LIB == "plotext":
    import plotext as plt
    plt.theme('dark')
    plt.subplots(len(sel_nrn), 1)
    id = 1
    for i in sel_nrn:
        plt.subplot(id, 1)
        plt.plot(t, data_fpga[:, i+1], marker='braille')
        id += 1
    plt.show()