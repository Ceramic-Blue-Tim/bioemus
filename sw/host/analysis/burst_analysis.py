import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as mpl

def get_burst(events) : 
    
    '''returns timestamps list of the first and last spike for all bursts'''
    # String algorithm for the Burst Detection
    
    maxISI = 100
    minintraburstspikes = 5

    burst_event_total  = []
    end_burst_total    = []
    intraburstspikes   = []
    burstcounts        = []
    for neuron in events :     
        
        neuron = np.array(neuron)
        fake_spike=neuron[-1]+maxISI+1
        neuron = np.append(neuron, fake_spike)
        
        delta_time_spike = neuron[1:] - neuron[:-1]
        temp_mask_detection = delta_time_spike > maxISI # Change burst focusing when time delta >= 100 ms
        temp_mask_detection = np.append(True, temp_mask_detection)
        temp_time_burst_events = neuron[temp_mask_detection]
        
        burst_event_pos = np.where(np.in1d(neuron,temp_time_burst_events))[0]
        number_inburst_spike = burst_event_pos[1:] - burst_event_pos[:-1]
        mask_detection = number_inburst_spike >= minintraburstspikes # Change the number of spikes in the burst >= 5
        mask_detection = np.append(mask_detection, False)
        time_burst_events = neuron[temp_mask_detection][mask_detection]
        
        idx_end_burst = np.where(np.in1d(neuron,time_burst_events))[0] + number_inburst_spike[mask_detection[:-1]] - 1
        time_end_burst = neuron[idx_end_burst]

        burst_event_total.append(time_burst_events)
        end_burst_total.append(time_end_burst)
        intraburstspikes.append(number_inburst_spike[mask_detection[:-1]])
        burstcounts.append(len(time_burst_events))
    
    return burst_event_total, end_burst_total, intraburstspikes, burstcounts

def get_IBI(raster_list, events_list) : 
    
    '''returns time interval between burst histogram and boxplot of neuron signals'''

    IBI_file = []
    label = raster_list
    color_list = mpl.colormaps.get_cmap('tab10').resampled(len(raster_list)).colors
    
    # fig, ax = plt.subplots(2, layout  = 'tight', figsize = (15,15))
    fig, ax = plt.subplots(2, layout  = 'tight', num="IBI")
    
    for events in events_list : 
        
        burst_total, _, _, _ = get_burst(events)
        IBI_total = []
        for k in range(len(burst_total)) :
            
            if len(burst_total[k]) > 1 :
                IBI = burst_total[k][1:] - burst_total[k][:-1]
                IBI_total.append(IBI) 
            
        IBI_total = np.concatenate(IBI_total, axis=0)
        IBI_file.append(IBI_total)
        
    # time_burst = np.linspace(0,max([max(i) for i in IBI_file]), 50)
    time_burst = np.logspace(np.log10(min([min(i) for i in IBI_file])),np.log10(max([max(i) for i in IBI_file])), 30)

    ax[0].hist(IBI_file, time_burst, color = color_list, edgecolor = 'k' , stacked=False, label = label)
    ax[0].set_xlabel(r'$IBI$ [ms]')
    ax[0].set_xscale('log')
    ax[0].set_ylabel('number')
    ax[0].legend()
    ax[0].set_title('Histogram of IBI distribution')
    
    bp = ax[1].boxplot(IBI_file,patch_artist=True, vert=True, meanline = True, showfliers= False, labels = label)
    ax[1].set_ylabel('IBI [ms]')

    for patch, color in zip(bp['boxes'], color_list): 
        patch.set_facecolor(color)
    # ax.set_yscale('log')
           
    return IBI_total

def get_burst_length(raster_list, events_list) : 
    
    '''returns burst length histogram and boxplot of neuron signals'''
    
    color_list = mpl.colormaps.get_cmap('tab10').resampled(len(raster_list)).colors
    label = raster_list
    
    length_burst_file = []
    # fig, ax = plt.subplots(2, layout  = 'tight',figsize = (15,15))
    fig, ax = plt.subplots(2, layout  = 'tight', num = "Burst length")
    
    for events in events_list : 
        
        start, end, _, _ = get_burst(events)
        length_burst_total = []
        
        for k in range(len(start)) :
                                            
            if len(start[k]) > 0 : # Takes only the neurons with at least one burst
                
                length_burst_neuron = end[k]-start[k]
                length_burst_total.append(length_burst_neuron)
        
        length_burst_total = np.concatenate(length_burst_total, axis=0)
        length_burst_file.append(length_burst_total)                      
    
    time_burst = np.linspace(0,max([max(i) for i in length_burst_file]), 30)
        
    ax[0].hist(length_burst_file, time_burst, color = color_list, edgecolor = 'k'  , stacked=False, label = label)
    ax[0].set_xlabel(r'$Burst length$ [ms]')
    ax[0].set_ylabel('number')
    ax[0].legend()
    ax[0].set_title('Histogram of Burst length distribution')
    
    bp = ax[1].boxplot(length_burst_file,patch_artist=True, vert=True, meanline = True, showfliers= False, labels = label)
    ax[1].set_ylabel('Burst length [ms]')
    for patch, color in zip(bp['boxes'], color_list): 
        patch.set_facecolor(color)
    
            
    return length_burst_total

def burst_analysis(raster_list, tstamp_list):
    get_IBI(raster_list, tstamp_list)
    get_burst_length(raster_list, tstamp_list)
    pass
