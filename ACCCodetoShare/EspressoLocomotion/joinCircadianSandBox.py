#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 11:54:28 2020

@author: sangyuxu
"""

from importlib import reload
import EspressoLocomotion
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import locoDataMunger
import locoUtilities
import pandas as pd
import locoPlotters
import espresso as esp
import dabest
import datetime
import os
wes_palette, wes_colors = locoPlotters.createWesAndersonPalette()
dataFolder = '/Users/sangyuxu/Data/Espresso/LongRun1/'

#%%
   
dataFolder = '/Users/sangyuxu/Data/Espresso/LongRun1/'
Long1 = EspressoLocomotion.EspressoLocomotion(dataFolder, 0, 2000, initialResamplePeriod = 1000, longForm = True)

    
#%%
dataFolder2 = '/Users/sangyuxu/Data/Espresso/LongRun2/'
Long2 = EspressoLocomotion.EspressoLocomotion(dataFolder2, 0, 2000, initialResamplePeriod = 1000, longForm = True)
#%%
countLogDf= Long1.countLogDf.copy()
Long1.countLogDf['Seconds'] = (countLogDf.index - countLogDf.index[0]).total_seconds()

newFood = np.where(np.diff(Long1.countLogDf.index)>numpy.timedelta64(1000,'s'))[0]+1
newFood = countLogDf.iloc[np.append(0, newFood)].Seconds/3600

timePoint=countLogDf.loc[countLogDf.index == '2020-02-26 20:00:00']['Seconds']
timePoint = timePoint.values[0]/3600
eightOClocks = [timePoint]
maxTime = countLogDf['Seconds'][-1]/3600
while timePoint < maxTime:
    timePoint = timePoint+12
    eightOClocks.append(timePoint) 


#%%

#%%
feedFolder = dataFolder + 'Feeds/'
feedFileList=os.listdir(feedFolder)


feedCount = [s for s in feedFileList if "FeedCount" in s]
feedCount.sort()
feedVolume = [s for s in feedFileList if "FeedVolume" in s]
feedVolume.sort()
feedLogs = [s for s in feedFileList if "FeedLog" in s]
feedLogs.sort()
dates = [datetime.datetime.strptime(i[10:29], '%Y-%m-%d_%H-%M-%S' ) for i in feedCount]
bigFeedCountDf = pd.DataFrame()
bigFeedVolumeDf = pd.DataFrame()
for i in range (3):
    date = feedCount[i][10:29]
    feedCountFile = feedFolder+feedCount[i]
    feedVolumeFile = feedFolder+feedVolume[i]
    feedCountDf = pd.read_csv(feedCountFile)
    feedVolumeDf = pd.read_csv(feedVolumeFile)
    if i >0:
        dateDiff = dates[i]-dates[0]
        minDiff = dateDiff.days*24*60 + dateDiff.seconds / 60
        print(minDiff)
        feedCountDf['MinsFromStart'] = feedCountDf['MinsFromStart'] + minDiff
        feedVolumeDf['MinsFromStart'] = feedVolumeDf['MinsFromStart'] + minDiff
        bigFeedCountDf = pd.concat([bigFeedCountDf, feedCountDf])
        bigFeedVolumeDf = pd.concat([bigFeedVolumeDf, feedVolumeDf])
    else:
        bigFeedCountDf = feedCountDf
        bigFeedVolumeDf = feedVolumeDf
        
bigFeedCountDf = bigFeedCountDf.reset_index(drop = True)
bigFeedVolumeDf = bigFeedVolumeDf.reset_index(drop = True)
bigFeedCountDf = bigFeedCountDf.drop(['Mean'], axis = 1)
bigFeedVolumeDf = bigFeedVolumeDf.drop(['Mean'], axis = 1)

#%%
bigFeedLogDf = pd.read_csv(feedFolder + feedLogs[0])

for i in range(1, 3):    
    feedLogDf = pd.read_csv(feedFolder + feedLogs[i])
    bigFeedLogDf = pd.concat([bigFeedLogDf, feedLogDf], axis = 0)


#%%
feedLogDfValid = bigFeedLogDf.loc[bigFeedLogDf.Valid == True]
feedLogDfValid = feedLogDfValid.set_index(pd.to_datetime(feedLogDfValid['StartTime']))
feedLogDfTrimmed = feedLogDfValid.loc[:, ['FlyID', 'ChoiceIdx', 'Volume-mm3', 'Duration-ms']]
feedLogDfTrimmed['FlyID-Choice'] = feedLogDfTrimmed['FlyID'].astype(str) + '_' + feedLogDfTrimmed['ChoiceIdx'].astype(str)
volumeDf = feedLogDfTrimmed[['FlyID-Choice', 'Volume-mm3']]
durationDf = feedLogDfTrimmed[['FlyID-Choice', 'Duration-ms']]
volumePivotted = volumeDf.pivot_table(values = 'Volume-mm3', index=pd.to_datetime(volumeDf.index), columns='FlyID-Choice', aggfunc='first')
volumePivotted = volumePivotted.fillna(0)
volumePivottedResampled = volumePivotted.resample('1200S').sum()
volumePivottedResampled['Seconds'] = (volumePivottedResampled.index - volumePivottedResampled.index[0]).total_seconds()

f = plt.figure(figsize = [20, 5])
locoPlotters.plotBoundedLine(volumePivottedResampled['Seconds']/3600, volumePivottedResampled.filter(regex = '_1'), ax = None, c = wes_colors['lakeblue'], resamplePeriod = None)
locoPlotters.plotBoundedLine(volumePivottedResampled['Seconds']/3600, volumePivottedResampled.filter(regex = '_0'), ax = None, c = wes_colors['crimson'], resamplePeriod = None)
plt.fill_between(eightOClocks[0:2], 0, [.1, .1], color = wes_colors['midnight'], alpha=0.1)

# for n in newFood:
#     plt.arrow(n, 35000, 0, -2000, width = 0.05, head_width = 0.4, head_length = 1500, color = 'r')
# # plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Feed', '95% CI', 'Dark Period'])
plt.ylabel('FeedDuration')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [.1, .1], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [.1, .1], color = wes_colors['midnight'], alpha=0.1)


# plt.plot(np.mean(volumePivottedResampled.filter(regex = '_0'), axis = 1), 'r')
# plt.plot(np.mean(volumePivottedResampled.filter(regex = '_1'), axis = 1), 'b')

locoUtilities.espressoSaveFig(f, 'FeedV', Long1.metaDataDf.Date[0], Long1.outputFolder, pngDPI = 300, tp = False)

#%%
durationPivotted = durationDf.pivot_table(values = 'Duration-ms', index=pd.to_datetime(durationDf.index), columns='FlyID-Choice', aggfunc='first')
durationPivotted = durationPivotted.fillna(0)

durationPivottedResampled = durationPivotted.resample('600S').sum()
durationPivottedResampled['Seconds'] = (durationPivottedResampled.index - durationPivottedResampled.index[0]).total_seconds()

f = plt.figure(figsize = [20, 5])
locoPlotters.plotBoundedLine(durationPivottedResampled['Seconds']/3600, durationPivottedResampled.filter(regex = '_1'), ax = None, c = wes_colors['lakeblue'], resamplePeriod = None)
locoPlotters.plotBoundedLine(durationPivottedResampled['Seconds']/3600, durationPivottedResampled.filter(regex = '_0'), ax = None, c = wes_colors['crimson'], resamplePeriod = None)
plt.fill_between(eightOClocks[0:2], 0, [40000, 40000], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, 35000, 0, -2000, width = 0.05, head_width = 0.4, head_length = 1500, color = 'r')
# plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Feed', '95% CI', 'Dark Period'])
plt.ylabel('Feed Volume')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [40000, 40000], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [40000, 40000], color = wes_colors['midnight'], alpha=0.1)


# plt.plot(np.mean(durationPivottedResampled.filter(regex = '_0'), axis = 1), 'r')
# plt.plot(np.mean(durationPivottedResampled.filter(regex = '_1'), axis = 1), 'b')

locoUtilities.espressoSaveFig(f, 'FeedD', Long1.metaDataDf.Date[0], Long1.outputFolder, pngDPI = 300, tp = False)

# %%



#%%

bigFeedCountDf.columns
newColumnNames = ['']*(len(bigFeedCountDf.columns))
for i in range(1, len(bigFeedCountDf.columns)):
    c = bigFeedCountDf.columns[i]
    ftNo = int(c[-3::])
    chNo = int(np.ceil(ftNo/2))
    if np.mod(ftNo, 2) == 1:
        newColumnNames[i] = 'Ch' + str(chNo) + '_Obj1_L'
    else:
        newColumnNames[i] = 'Ch' + str(chNo) + '_Obj1_R'
newColumnNames[0] = bigFeedCountDf.columns[0]
bigFeedCountDf.columns = newColumnNames
bigFeedVolumeDf.columns = newColumnNames
#%%
f = plt.figure(figsize = [20, 5])
ax = plt.gca()
maxY = 5
locoPlotters.plotBoundedLine(bigFeedCountDf['MinsFromStart']/60, bigFeedCountDf.filter(regex = '_L'), ax = ax, c = wes_colors['crimson'], resamplePeriod = None)
locoPlotters.plotBoundedLine(bigFeedCountDf['MinsFromStart']/60, bigFeedCountDf.filter(regex = '_R'), ax = ax, c = wes_colors['lakeblue'], resamplePeriod = None)

plt.fill_between(eightOClocks[0:2], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, maxY - 0.5, 0, -0.1, width = 0.05, head_width = 0.4, head_length = 0.2, color = 'r')
plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Average Speed', '95% CI', 'Dark Period'])
plt.ylabel('Count')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)


locoUtilities.espressoSaveFig(f, 'feedCount', Long1.metaDataDf.Date[0], Long1.outputFolder, pngDPI = 300, tp = False)


f = plt.figure(figsize = [20, 5])
ax = plt.gca()
maxY = 0.05
locoPlotters.plotBoundedLine(bigFeedVolumeDf['MinsFromStart']/60, bigFeedVolumeDf.filter(regex = '_L'), ax = ax, c = wes_colors['crimson'], resamplePeriod = None)
locoPlotters.plotBoundedLine(bigFeedVolumeDf['MinsFromStart']/60, bigFeedVolumeDf.filter(regex = '_R'), ax = ax, c = wes_colors['lakeblue'], resamplePeriod = None)
plt.fill_between(eightOClocks[0:2], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, maxY-0.1, 0, -0.01, width = 0.01, head_width = 0.04, head_length = 0.02, color = 'r')
plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Average Speed', '95% CI', 'Dark Period'])
plt.ylabel('Volume (uL/s)')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [maxY, maxY], color = wes_colors['midnight'], alpha=0.1)
plt.ylim([0, 0.05])
locoUtilities.espressoSaveFig(f, 'feedVolume', Long1.metaDataDf.Date[0], Long1.outputFolder, pngDPI = 300, tp = False)


#%%


countLogDf= Long1.countLogDf.copy()
Long1.countLogDf['Seconds'] = (countLogDf.index - countLogDf.index[0]).total_seconds()

newFood = np.where(np.diff(Long1.countLogDf.index)>numpy.timedelta64(1000,'s'))[0]+1
newFood = countLogDf.iloc[np.append(0, newFood)].Seconds/3600

timePoint=countLogDf.loc[countLogDf.index == '2020-02-26 20:00:00']['Seconds']
timePoint = timePoint.values[0]/3600
eightOClocks = [timePoint]
maxTime = countLogDf['Seconds'][-1]/3600
while timePoint < maxTime:
    timePoint = timePoint+12
    eightOClocks.append(timePoint) 




f = plt.figure(figsize = [20, 5])
ax = plt.gca()
countlogDf = Long1.countLogDf
locoPlotters.plotBoundedLine(Long1.countLogDf['Seconds']/3600, Long1.countLogDf.filter(regex = '_V'), ax = ax, c = 'k', resamplePeriod = '600s')

plt.fill_between(eightOClocks[0:2], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, 3.5, 0, -0.1, width = 0.05, head_width = 0.4, head_length = 0.2, color = 'r')
plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Average Speed', '95% CI', 'Dark Period'])
plt.ylabel('Speed (mm/s)')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
locoUtilities.espressoSaveFig(f, 'circadian', Long1.metaDataDf.Date[0], Long1.outputFolder, pngDPI = 300, tp = False)


#%%

countLogDf= Long2.countLogDf.copy()
Long2.countLogDf['Seconds'] = (countLogDf.index - countLogDf.index[0]).total_seconds()

newFood = np.where(np.diff(Long2.countLogDf.index)>numpy.timedelta64(100,'s'))[0]+1
newFood = countLogDf.iloc[np.append(0, newFood)].Seconds/3600

timePoint=countLogDf.loc[countLogDf.index == '2020-02-26 20:00:00']['Seconds']
timePoint = timePoint.values[0]/3600
eightOClocks = [timePoint]
maxTime = countLogDf['Seconds'][-1]/3600
while timePoint < maxTime:
    timePoint = timePoint+12
    eightOClocks.append(timePoint) 




f = plt.figure(figsize = [20, 5])
ax = plt.gca()
# countlogDf = Long1.countLogDf
locoPlotters.plotBoundedLine(Long2.countLogDf['Seconds']/3600, Long2.countLogDf.filter(regex = '_V'), ax = ax, c = 'k', resamplePeriod = '600s')

plt.fill_between(eightOClocks[0:2], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, 3.5, 0, -0.1, width = 0.05, head_width = 0.4, head_length = 0.2, color = 'r')
plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Average Speed', '95% CI', 'Dark Period'])
plt.ylabel('Speed (mm/s)')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
locoUtilities.espressoSaveFig(f, 'circadian', Long2.metaDataDf.Date[0], Long2.outputFolder, pngDPI = 300, tp = False)


#%%
countLogDf1 = Long1.countLogDf.copy()
countLogDf2 = Long2.countLogDf.copy()
countLogDf1 = countLogDf1.resample('60S').agg(np.mean)
countLogDf2 = countLogDf2.resample('60S').agg(np.mean)
countLogDf1.columns = 'Rig1_' + countLogDf1.columns
countLogDf2.columns = 'Rig2_' + countLogDf2.columns
countLogDfComb = pd.concat([countLogDf1, countLogDf2], axis = 1)



#%%
countLogDf= countLogDfComb.copy()
countLogDf['Seconds'] = (countLogDf.index - countLogDf.index[0]).total_seconds()

newFood = np.where(np.diff(countLogDf.index)>numpy.timedelta64(100,'s'))[0]+1
newFood = countLogDf.iloc[np.append(0, newFood)].Seconds/3600

timePoint=countLogDf.loc[countLogDf.index == '2020-02-26 20:00:00']['Seconds']
timePoint = timePoint.values[0]/3600
eightOClocks = [timePoint]
maxTime = countLogDf['Seconds'][-1]/3600
while timePoint < maxTime:
    timePoint = timePoint+12
    eightOClocks.append(timePoint) 




f = plt.figure(figsize = [20, 5])
ax = plt.gca()
# countlogDf = Long1.countLogDf
locoPlotters.plotBoundedLine(countLogDf['Seconds']/3600, countLogDf.filter(regex = '_V'), ax = ax, c = 'k', resamplePeriod = '600s')

plt.fill_between(eightOClocks[0:2], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)

for n in newFood:
    plt.arrow(n, 3.5, 0, -0.1, width = 0.05, head_width = 0.4, head_length = 0.2, color = 'r')
plt.xticks(ticks = eightOClocks, labels = [12, 0, 12, 0, 12, 0, 12])
plt.xticks(eightOClocks)
plt.legend(['Average Speed', '95% CI', 'Dark Period'])
plt.ylabel('Speed (mm/s)')
plt.xlabel('Zeitgeber Time (hr)')
plt.fill_between(eightOClocks[2:4], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
plt.fill_between(eightOClocks[4:6], 0, [4, 4], color = wes_colors['midnight'], alpha=0.1)
locoUtilities.espressoSaveFig(f, 'circadianComb', Long2.metaDataDf.Date[0], Long2.outputFolder, pngDPI = 300, tp = False)

#%%
feedFolder2 = dataFolder2 + 'Feeds/'
feedFileList=os.listdir(feedFolder2)

feedStats = [s for s in feedFileList if "FeedStats" in s]
feedStats.sort()

feedStatsFile = feedFolder2+feedStats[0]
feedStatsDf = pd.read_csv(feedStatsFile)
feedStatsDf = feedStatsDf.drop(axis = 0, index = feedStatsDf.index[-1])
locoPlotters.plotBoundedLine(feedStatsDf['Minutes']/60, feedStatsDf.filter(regex = '-L'), ax = None, c = 'k', resamplePeriod = None)
