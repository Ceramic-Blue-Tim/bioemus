import numpy as np
import plotext as plt
import sys

NB_NEURONS  = 1024
TIME_ROW    = 0
SPK_ROW     = 1

data = np.genfromtxt(sys.argv[1], delimiter=';', skip_header=1)
# data = np.genfromtxt("raster.csv", delimiter=';', skip_header=1)

max_id = max(data[:,SPK_ROW])
plt.theme("clear")
plt.scatter(data[:, TIME_ROW], data[:,SPK_ROW], marker="dot")
# plt.yticks(ticks=np.linspace(0, NB_NEURONS, 16, endpoint=False))
plt.ylim(0, max_id)
plt.title("Raster")
plt.xlabel("Time (in ticks)")
plt.ylabel("Neuron index")
plt.show()