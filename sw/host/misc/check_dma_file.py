import numpy as np
import os
import sys

dtype       = np.dtype(np.uint32)
fpath       = "/home/ubuntu/data/rx_chan_11.txt"
nb_samples  = int(os.path.getsize(fpath)/dtype.itemsize)
data        = np.fromfile(fpath, dtype=dtype, count=nb_samples)

if len(sys.argv) > 1:
  if sys.argv[1] == "all":
    for i in range(len(data)):
        print("{}: {}".format(i, data[i]))
  elif sys.argv[1] == "check":
    r = []
    for i in range(int(len(data)/17)):
        id = i*17

        if i != 0:
            if data[id] != (data_prev+1):
                r.append(id)

        data_prev = data[id]

    if r:
        print("Error tstamp")
        print(r)
    else:
        print("No tstamp error")

else:

    r = []
    for i in range(int(len(data)/17)):
        id = i*17
        print("{}: {}".format(id, data[id]))