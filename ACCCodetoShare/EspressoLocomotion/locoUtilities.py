#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:04:52 2020

@author: sangyuxu
"""
import os 
# from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime



def makeOutputFolders(dataFolder):
    filelist=os.listdir(dataFolder)
    if 'output' not in filelist:
        outputDir = dataFolder + 'output/'
        os.mkdir(outputDir)
    else:
        outputDir = dataFolder + 'output/'
    if 'chamberPlots' not in os.listdir(outputDir):
        os.mkdir(outputDir + 'chamberPlots/')
    return outputDir
            
# def pathProcessing(countLogFile, endMin, startMin = 0):
#     countLogDfUnfiltered=pd.read_csv(countLogFile)
#     countLogDf=countLogDfUnfiltered.loc[(countLogDfUnfiltered.Seconds > startMin *60) & (countLogDfUnfiltered.Seconds < endMin * 60)]

#     # to account for shift in conv
#     offset= 2 
#     # to adjust for magnitude of error signal
#     threshold = 3
#     sigma = 2
#     step = [-1, 1]
#     flyIDNo=17
#     X = countLogDf.filter(regex= '_X$')
#     Y = countLogDf.filter(regex= 'Y$')
#     # x and y traces for selected fly
#     x = X.iloc[:, flyIDNo]
#     y = Y.iloc[:, flyIDNo]
#     t = countLogDf.Seconds
#     XDisp = np.diff(x, axis = 0)
#     YDisp = np.diff(y, axis = 0)
#     XDispConv = np.convolve(XDisp, step)[1::]
#     YDispConv = np.convolve(YDisp, step)[1::]
#     detectX = XDispConv>threshold
#     detectY = YDispConv>threshold
#     detectX = np.array([i for i, x in enumerate(detectX) if x])
#     detectY = np.array([i for i, x in enumerate(detectY) if x])
    
#     allIndToRemove = np.append(detectX,detectY)+offset

#     x[allIndToRemove] = 'nan'
#     y[allIndToRemove] = 'nan'
#     nans, interpInd= np.isnan(x), lambda z: z.nonzero()[0]
#     x[nans]= np.interp(interpInd(nans), interpInd(~nans), x[~nans])
#     y[nans]= np.interp(interpInd(nans), interpInd(~nans), y[~nans])
#     xProcessed = gaussian_filter1d(x, sigma)
#     yProcessed = gaussian_filter1d(y, sigma)


#     return xProcessed, yProcessed


def resampleCountLog(countLogDf, countLogName, resampleFrequencyInMs =50):
    originalCountLogDf = countLogDf
    resampleFrequency = str(resampleFrequencyInMs) + 'L'
    startDateTimeStr = countLogName[9:28]
    startDateTime = datetime.datetime.strptime(startDateTimeStr, '%Y-%m-%d_%H-%M-%S')
    absStartTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
    countLogDf.loc[:, 'NewAbsoluteTime'] = pd.to_timedelta(countLogDf['Seconds'], unit='s')
    countLogDf.loc[:, 'NewTime'] = startDateTime + pd.to_timedelta(countLogDf['Seconds'], unit='s')
    countLogDfReIndexed=countLogDf.set_index(absStartTime + countLogDf['NewAbsoluteTime'])
    countLogDfResampled = countLogDfReIndexed.resample(resampleFrequency).agg(np.mean)
    return countLogDfResampled, originalCountLogDf


def espressoSaveFig(fig, figName, figDate, figDirectory, pngDPI = 300):
    fig.savefig(figDirectory + figName + str(figDate)+'.png', dpi = pngDPI,transparent=True, bbox_inches='tight') 
    fig.savefig(figDirectory + figName + str(figDate)+'.svg') 

def espressoWriteDictToCSV(filename, dict):
    import csv
    with open(filename, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in dict.items():
           writer.writerow([key, value])