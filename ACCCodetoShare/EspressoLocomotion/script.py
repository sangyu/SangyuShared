#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 17:02:15 2020

@author: sangyuxu
"""
import EspressoLocomotion
import matplotlib.pyplot as plt
import matplotlib
%matplotlib inline
import numpy as np
import locoDataMunger
import locoUtilities
import pandas as pd
import locoPlotters
import espresso as esp
import dabest


dataFolderTrhCsCh = '/Users/sangyuxu/xy2/'
TrhCsCh = EspressoLocomotion.EspressoLocomotion(dataFolderTrhCsCh, 0, 120 )

#%%
# resultsDf = TrhCsCh.metaDataDf


groupBy = 'Temperature'
compareBy = 'Genotype'
colorBy = 'Genotype'
uniqueGroupBy = np.unique(resultsDf[groupBy])
uniqueCompareBy = np.unique(resultsDf[compareBy])
listIdx = [tuple(gp + '@' + uniqueCompareBy[::-1]) for gp in uniqueGroupBy]
# listIdx = (tuple(np.unique(resultsDf[groupBy])[0]+' '+np.unique(resultsDf[compareBy])[::-1]), tuple(np.unique(resultsDf[groupBy])[1]+' '+np.unique(resultsDf[compareBy])[::-1]))
resultsDf['newPlotColumn'] = resultsDf[groupBy] + '@' + resultsDf[compareBy] 
dabestContrastData = dabest.load(resultsDf,
                               x='newPlotColumn', # the default for this test config is to group flies by genotype
                               y='#Flies',
                               idx=listIdx,
                               paired=False
                              )
fig = dabestContrastData.mean_diff.plot( color_col=colorBy)
flatListIdx = [item.split('@')[1] for t in listIdx for item in t] 
fig.axes[0].set_xticklabels(flatListIdx, rotation = 45, ha="right")

diffListIdx = flatListIdx[]
fig.axes[1].set_xticklabels(flatListIdx, rotation = 45, ha="right")
