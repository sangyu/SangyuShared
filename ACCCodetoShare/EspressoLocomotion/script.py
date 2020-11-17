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
#%%

dataFolder = '/Users/xusy/Data/Espresso/LexAOpACR/TrhLexAR50H05Gal4TwoStarvedProcessed/'
TrhLxR50Gal = EspressoLocomotion.EspressoLocomotion(dataFolder, 0, 120)


#%%
# resultsDf = TrhCsCh.metaDataDf


groupBy = 'Temperature'
compareBy = 'Status'
colorBy = 'Genotype'
dabestContrastData = dabest.load(TrhLxR50Gal.resultsDf,
                       x=compareBy, # the default for this test config is to group flies by genotype
                       y='averageSpeed'
                       ,
                       idx=np.unique(TrhLxR50Gal.metaDataDf.Status),
                       paired=False
                      )

fig = dabestContrastData.mean_diff.plot( color_col=colorBy)