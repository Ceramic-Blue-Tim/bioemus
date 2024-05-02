import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as mpl

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

def mean_firing_rate(events, rec_duration_ms) : 
    mean        = []
    spikecounts = []
    time        = rec_duration_ms # in [ms]
    '''calculate the mean firing rate of neuron signals'''

    for neuron in events : 
        spikecounts.append(len(neuron))
        mean.append(len(neuron)/(time/1e3)) # in [spikes/s]

    return mean, spikecounts

def ISI_distribution(raster_list, events_list, rec_duration_ms) : 
    '''returns time interval between spikes histogram and boxplot of neuron signals'''
    
    # fig, ax     = plt.subplots(3, layout = 'tight', figsize = (15,15))
    fig, ax     = plt.subplots(3, layout = 'tight', num="ISI + MFR")
    diff_total  = []
    mean_total  = []
    label       = raster_list
    color_list = mpl.colormaps.get_cmap('tab10').resampled(len(raster_list)).colors
    for events in events_list :
        
        number_neurons = len(events)
        diff = []
        mean_total.append(mean_firing_rate(events, rec_duration_ms)[0])
        for neuron in events :        
            if len(neuron) > 1 :     
                diff.append(neuron[1:]-neuron[:-1])
        diff = np.concatenate(diff, axis=0)
        diff_total.append(diff)
        
    # tau = np.linspace(0,9000, 30)  
    tau = np.logspace(np.log10(min([min(i) for i in diff_total])),np.log10(max([max(i) for i in diff_total])), 30)
    ax[0].hist(diff_total, tau, color = color_list, edgecolor =  'k'  , stacked=False, label = label)
    
    ax[0].set_xlabel(r'$\tau$-[ms]')
    ax[0].set_ylabel('number')
    ax[0].set_xscale('log')
    ax[0].legend()
    ax[0].set_title('Histogram of ISI distribution')
    
    bp = ax[1].boxplot(diff_total,patch_artist=True, vert=True, meanline = True, showfliers= False, labels = label)
    for patch, color in zip(bp['boxes'], color_list): 
        patch.set_facecolor(color)
    
    ax[1].set_ylabel('ISI [ms]')
    ax[1].set_title('Box plot ISI')
    
    bp2 = ax[2].boxplot(mean_total,patch_artist=True, vert=True, meanline = True, showfliers= False, labels = label)
    for patch, color in zip(bp2['boxes'], color_list): 
        patch.set_facecolor(color)
    
    ax[2].set_ylabel('MFR [spikes/s]')
    ax[2].set_title('Box plot MFR')
    
    return diff

def spike_analysis(raster_list, tstamp_list, rec_duration_s):
    ISI_distribution(raster_list, tstamp_list, rec_duration_s*1e3)
