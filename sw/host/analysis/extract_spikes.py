import numpy as np

def shape_data(data):
    
    timestamps      = []
    activeneurons   = []
    neuron          = data[:,1]
    neuron_list     = np.unique(data[:,1])
    
    for k in range(len(neuron_list)):
        
        index = np.where(neuron == neuron_list [k])[0]
        
        if len(index) >= 2 : # Consider only neurons that spiked more than once
            timestamps.append(data[index,0])
            activeneurons.append(neuron_list [k])
            
    return neuron_list, timestamps, activeneurons


def extract_spikes(dirpath, raster_list, header_len=1, delimiter=';'):
    fpath_list = [dirpath + "raster_" + e + ".csv" for e in raster_list]
    
    tstamp_list   = []
    for i in range(len(fpath_list)):
        spikes = np.loadtxt(fpath_list[i], skiprows=header_len, delimiter=delimiter)
        [nlist, tstamp, nactive] = shape_data(spikes)
        tstamp_list.append(tstamp)

    return tstamp_list