#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 14:48:25 2020

@author: sangyuxu
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import locoUtilities
import datetime
import re

def readMetaAndCount(dataFolder, startMin, endMin):
    conversion = 0.215
    filelist=os.listdir(dataFolder)
    countLogList = [s for s in filelist if "CountLog" in s]
    metaDataList = [s for s in filelist if "MetaData" in s]
    if len(metaDataList)!=len(countLogList):
        print('Different numbers of metadata files and countLog files')
    countLogList=np.sort(countLogList)
    metaDataList=np.sort(metaDataList)
    print('countLog files found: \n')
    print(countLogList)
    print('\nmetadata files found: \n')
    print(metaDataList)
    bigCountLogDf = pd.DataFrame()
    bigMetaDataDf = pd.DataFrame()
    for dataSetNumber in range(0, len(countLogList)):
        print(countLogList[dataSetNumber])
        print(metaDataList[dataSetNumber])
        companionMetaData = [m for m in metaDataList if (datetime.datetime.strptime(m[9:28], '%Y-%m-%d_%H-%M-%S') - datetime.datetime.strptime(countLogList[dataSetNumber][9:28], '%Y-%m-%d_%H-%M-%S')).seconds < 5][0]
        metaDataDf=pd.read_csv( dataFolder + companionMetaData)
        metaDataDf.columns = metaDataDf.columns.str.replace(' ', '')
        metaDataDf['Date'] = countLogList[dataSetNumber][9:28]
        countLogDfUnselected=pd.read_csv( dataFolder + countLogList[dataSetNumber] )
        expectedIDs = {int(re.search(r'Ch(.*)_Obj1_X', s).group(1)) for s in countLogDfUnselected.filter(regex = '_X').columns}
        existingIDs = set(metaDataDf.ID)
        diffID = expectedIDs - existingIDs 
        print('MetaData is missing IDs ' + str(np.sort(list(diffID))))
        for id in diffID:
            todrop = countLogDfUnselected.filter(regex = 'Ch'+str(id)).columns
            countLogDfUnselected = countLogDfUnselected.drop(todrop.tolist(), axis = 1)
#        countLogColumns = countLogDfUnselected.columns.str
        countLogDfTrimmed = calculateSpeedinCountLog(countLogDfUnselected)
        countLogDfTimeBanded=countLogDfTrimmed.loc[(countLogDfTrimmed.Seconds > startMin *60) & (countLogDfTrimmed.Seconds < endMin * 60)]
        countLogDfNew, countLogDfOld = locoUtilities.resampleCountLog(countLogDfTimeBanded, countLogList[dataSetNumber], 50)
        countLogDfNew.columns = countLogList[dataSetNumber][9:28] + '_' + countLogDfNew.columns
        if dataSetNumber == 0:
            bigCountLogDf = countLogDfNew
            bigMetaDataDf = metaDataDf
        else:
            bigCountLogDf = pd.concat([bigCountLogDf, countLogDfNew], axis = 1)
            bigMetaDataDf = pd.concat([bigMetaDataDf, metaDataDf], axis = 0)
    bigMetaDataDf = bigMetaDataDf.reset_index(drop = True)
    bigMetaDataDf['Genotype'] = bigMetaDataDf['Genotype'].str.lower()
    bigMetaDataDf = assignStatus(bigMetaDataDf)
    print(bigMetaDataDf)
    return bigMetaDataDf, bigCountLogDf

def calculateSpeedinCountLog(countLogDf, speedThreshold = 20):
    conversion = 0.215
    cx = countLogDf.filter(regex = '_X')*conversion
    cy = 18 - countLogDf.filter(regex = '_Y')*conversion
    cv = countLogDf.filter(regex = '_Vpix/s')*conversion
    XX = cx.rename(columns = lambda x : str(x)[:-2])
    YY = cy.rename(columns = lambda x : str(x)[:-2])
    VV = cv.rename(columns = lambda x : str(x)[:-7])
    for column in VV.columns:
        indToDelete = VV[column]>speedThreshold
        VV.loc[indToDelete, column] = np.nan
        XX.loc[indToDelete, column] = np.nan
        YY.loc[indToDelete, column] = np.nan
    XX = XX.rename(columns = lambda x : str(x)+'_X')
    YY = YY.rename(columns = lambda x : str(x)+'_Y')
    VV = VV.rename(columns = lambda x : str(x)+'_V')
    newCountLog = pd.concat([countLogDf.iloc[:, [0, 1, 2]], XX, YY, VV], axis = 1)
    return newCountLog

def intrapolateUnderThreshold(s, th):
    sOverTh = s>th
    sOverTh = np.array([i for i, x in enumerate(sOverTh) if x])
    print('removed indices ' + str(sOverTh))
    s[sOverTh] = 'NaN'
    nans, interpInd= np.isnan(s), lambda z: z.nonzero()[0]
    s[nans]= np.interp(interpInd(nans), interpInd(~nans), s[~nans])
    return s

def assignStatus(metaDataDf):
    if 'Status' not in metaDataDf.columns:
        metaDataDf.insert(1, 'Status', metaDataDf.Genotype, True) 
        metaDataDfCopy = metaDataDf.copy()
        TestInd=[i for i, s in enumerate(metaDataDf.Genotype) if 'w1118' not in s ]
        metaDataDfCopy['Status'] = 'Sibling'
        metaDataDfCopy.loc[TestInd, 'Status'] = 'Offspring'
        metaDataDf = metaDataDfCopy
    return metaDataDf