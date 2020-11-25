#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 14:01:49 2020

@author: xusy
"""

# First import all necessary libraries to run the script
import sys
sys.path.append("..") # so we can import espresso from the directory above.
import os
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib as mpl
import EspressoLocomotion
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns
import dabest 
import espresso as esp
print('Espresso Version' + esp.__version__)


# Tell it where the files are, we are expecting at least one FeedLog and one Metadata file
dataFolder = '/Users/xusy/Data/Espresso/Schlichting R58E02/MS48/'
# dataFolder = '/Users/xusy/Library/Mobile Documents/com~apple~CloudDocs/EspressoManu/Data and Python Notebooks Organized by Figure/Figure 4 Trh R50H05/validFeeds/R50CsCh/'
# dataFolder = '/Users/xusy/Library/Mobile Documents/com~apple~CloudDocs/EspressoManu/Data and Python Notebooks Organized by Figure/Figure 4 Trh R50H05/validFeeds/TrhCsCh/'
# feedDataFolder = dataFolder + 'Feeds'
feedDataFolder = dataFolder
# Make a folder for the pictures you are about to dump, if, after checking, there is no existing "images" folder
imagepath=dataFolder+'/' 'images/'
mainDataPathList=os.listdir(dataFolder)
if [s for s in mainDataPathList if 'images' in s]==[]:
    os.mkdir(imagepath)

allFeedData = esp.espresso(feedDataFolder, expt_duration_minutes=1400)
CPalette = createEspressoPalette(allFeedData)
#%%
dataFolder = '/Users/xusy/Library/Mobile Documents/com~apple~CloudDocs/EspressoManu/Data and Python Notebooks Organized by Figure/Figure 4 Trh R50H05/validFeeds/TrhCsCh/'

allSpeedData = EspressoLocomotion.EspressoLocomotion(dataFolder, 0, 120)

#%%


allSpeedData.plotBoundedSpeedLines(colorBy = 'Temperature', col = 'Status', rp = '600s')


#%%

# resultsDf = TrhCsCh.metaDataDf
allSpeedData.plotBoundedSpeedLines(colorBy = 'Sex', col = 'Status', rp = '600s')


#%%
allSpeedData.plotMeanHeatMaps(row = 'Status', col = 'Temperature')
#%%
groupBy = 'Status'
compareBy = 'Temperature'
colorBy = 'Genotype'
results = allSpeedData.resultsDf.loc[allSpeedData.resultsDf['Status'] == 'Offspring']
allSpeedData 
dabestContrastData = dabest.load(results,
                       x=compareBy, # the default for this test config is to group flies by genotype
                       y='TB Preference'
                       ,
                       idx=np.unique(allSpeedData.metaDataDf.Temperature),
                       paired=False
                      )

fig = dabestContrastData.mean_diff.plot( color_col=colorBy)

#%%

# put in the parameters you don't want to type over and over again when using the plot function
groupby='Sex'
compareby='Status'
colorby='Genotype'
startHour=0 #hours
endHour=2#hours
figAspectRatio=(8, 5)
fDPI=150


# plot volume plots with espresso contrast plot function
# load data into dabest
volume = allFeedData.plot.contrast.feed_volume_per_fly(group_by=groupby, 
                                                       compare_by=compareby,start_hour=startHour,
                                                    volume_unit="nanoliter",
                                                     end_hour=endHour)
# plot data with dabest
fvolume = volume.hedges_g.plot(color_col=colorby,swarm_label="Feed Volume (nl)",
                                custom_palette=CPalette, 
                                    fig_size=figAspectRatio)

# save both a .png for quick browsing and a .svg for manipulation
fvolume.savefig(imagepath + 'Volume' +'.png',transparent=True, bbox_inches='tight', dpi=fDPI)
fvolume.savefig(imagepath + 'Volume' +'.svg',transparent=True, bbox_inches='tight')


count = allFeedData.plot.contrast.feed_count_per_fly(group_by=groupby, 
                                                       compare_by=compareby,start_hour=startHour,
                                                     end_hour=endHour)

fcount = count.mean_diff.plot(color_col=colorby, fig_size=figAspectRatio,swarm_label="Feed count",
                                custom_palette=CPalette)
fcount.savefig(imagepath + 'Count.png',transparent=True, bbox_inches='tight', dpi=fDPI)
fcount.savefig(imagepath + 'Count.svg',transparent=True, bbox_inches='tight')



duration = allFeedData.plot.contrast.feed_duration_per_fly(group_by=groupby, 
                                                       compare_by=compareby,start_hour=startHour,
                                                     end_hour=endHour)

fduration = duration.mean_diff.plot(color_col=colorby,
                                custom_palette=CPalette, swarm_label="Feed Duration (min)", 
                                    fig_size=figAspectRatio)
fduration.savefig(imagepath + 'Duration.png',transparent=True, bbox_inches='tight', dpi=fDPI)
fduration.savefig(imagepath + 'Duration.svg',transparent=True, bbox_inches='tight')

latency = allFeedData.plot.contrast.latency_to_feed(group_by=groupby, 
                                                       compare_by=compareby,start_hour=startHour,
                                                     end_hour=endHour)

flatency = latency.mean_diff.plot(color_col=colorby,
                                custom_palette=CPalette, swarm_label="Latency to first feed (min)", 
                                    fig_size=figAspectRatio)
flatency.savefig(imagepath + 'Latency.png',transparent=True, bbox_inches='tight', dpi=fDPI)
flatency.savefig(imagepath + 'Latency.svg',transparent=True, bbox_inches='tight')

# remind yourself where the pictures are
print(imagepath)
#%%
cConsumption=allFeedData.plot.cumulative.consumption(color_by='Sex',
                                         col='Status',
                                         row=None,start_hour = 0, end_hour=2)





cConsumption.savefig(imagepath + 'CumulativeVolume' +'.png',transparent=True, bbox_inches='tight', dpi=150)
cConsumption.savefig(imagepath + 'CumulativeVolume' +'.svg',transparent=True, bbox_inches='tight')










#%%
def createEspressoPalette(allFeedData):
    # Set up a custom palette for plots
    import seaborn as sns
    CPalette = esp.create_palette(['k', 'gray', 'cyan', 'orangered'], # green for test, use this for ACR expriments
                                allFeedData.feeds.Genotype.cat.categories
                                )
    sns.palplot(CPalette.values())
    print(allFeedData.feeds.Genotype.cat.categories)
    return CPalette 
