import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def draw_raster(dirpath, raster_list, save=False, delimiter=';'):
    FONTSIZE   = 12

    fpath_list = [dirpath + "raster_" + e + ".csv" for e in raster_list]

    x,y = ([] for _ in range(2))
    for i in range(len(fpath_list)):
        spikes  = pd.read_csv(fpath_list[i], sep=delimiter)
        x.append(spikes['time'])
        y.append(spikes['neuron_id'])    

    fig = plt.figure("Raster plot")
    for i in range(len(raster_list)):
        plt.subplot(len(raster_list),1,i+1)
        plt.scatter(x[i]*1e-3, y[i], s=1, marker='.', color='black')
        plt.ylabel('Neuron index', fontsize=FONTSIZE)
        plt.xlabel('Time (s)', fontsize=FONTSIZE)
        plt.yticks(fontsize=FONTSIZE)
        plt.xticks(fontsize=FONTSIZE)
        plt.title(raster_list[i])
    plt.show()
    
    if save:
        fig.savefig('raster_{}.tiff'.format('_'.join(raster_list)), dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"})


            