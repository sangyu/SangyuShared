#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 17:59:42 2020
@author: Sanguyu Xu
xusangyu@gmail.com
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import locoDataMunger
import locoUtilities
import locoPlotters
# import pickle
import dabest
from setFont import setFont

class EspressoLocomotion(object):
    def __init__(self, dataFolder, startMin, endMin, initialResamplePeriod = 50, longForm = False):
        self.version = '0.0.4'
        bigMetaDataDf, bigCountLogDf = locoDataMunger.readMetaAndCount(dataFolder, startMin, endMin, initialResamplePeriod, longForm)
        self.metaDataDf = bigMetaDataDf
        self.countLogDf = bigCountLogDf
        outputDir = locoUtilities.makeOutputFolders(dataFolder)
        self.dataFolder = dataFolder
        self.outputFolder = outputDir
        self.startMin = startMin
        self.endMin = endMin
        self.resultsDf = bigMetaDataDf

    def plotChamberSmallMultiples(self):
        dates = np.unique(self.metaDataDf.Date)
        for i in range (0, len(dates)):
            print(dates[i])
            submeta = self.metaDataDf.loc[self.metaDataDf.Date == dates[i]]
            subcount = self.countLogDf.filter(regex = dates[i])
            chamberSmallsTrack, axarrT  = locoPlotters.putThingsInToChamberSubplot(subcount, submeta)
            chamberSmallsHeat, axarrH  = locoPlotters.putThingsInToChamberSubplot(subcount, submeta, locoPlotters.espressoPlotHeatmap)
            OutputDir = self.outputFolder + 'chamberPlots/'
            locoUtilities.espressoSaveFig(chamberSmallsTrack, 'chamberSmallsTrack', dates[i], OutputDir, pngDPI = 200)
            locoUtilities.espressoSaveFig(chamberSmallsHeat, 'chamberSmallsHeat', dates[i], OutputDir, pngDPI = 200)

    def plotMeanHeatMaps(self, binSize = 0.8, row = None, col = None, verbose = False):
        heatMapOutputDir = self.outputFolder
        if verbose:
            meanHeatmapFig,axes,  Hall, resultsDf, smallHeatmapFigs = locoPlotters.espressoPlotMeanHeatmaps(self, binSize, verbose)
            locoUtilities.espressoSaveFig(smallHeatmapFigs, 'smallHeatmapFigs', self.metaDataDf.Date[0], heatMapOutputDir, pngDPI = 200)
        else:
            meanHeatmapFig, axes, Hall, resultsDf = locoPlotters.espressoPlotMeanHeatmaps(self, binSize, row, col, verbose)
        self.resultsDf = resultsDf
        self.heatmapMatrix = Hall
        self.heatmapAxes = axes
        self.meanHeatmapFig = meanHeatmapFig

    def plotBoundedSpeedLines(self, colorBy, row = None, col = None, rp = '200s', YLim = None):
        setFont('Source Sans Pro', 14)
        T = self.countLogDf.iloc[:, 0]/3600
        VV =self.countLogDf.filter(regex = '_V')
        self.resultsDf['averageSpeed'] = np.nanmean(VV, axis = 0)
        listOfPlots, gp, custom_palette = locoPlotters.subplotRowColColor(self.metaDataDf, colorBy, row, col)
        nr, nc = listOfPlots[-1][0][0:2]
        figure, axes = plt.subplots(nrows=nr + 1, ncols=nc + 1, squeeze = False, figsize=(5 * (nc + 1), 5 * (nr + 1)))

        maxYlim = [0]*len(listOfPlots)
        plotNames=[]
        for i in range(0, len(listOfPlots)):
            # print(listOfPlots[i])
            ro, co = listOfPlots[i][0][0:2]
            name = listOfPlots[i][1]
            ind = gp[name]
            locoPlotters.plotBoundedLine(T, VV.iloc[:, ind], ax = axes[ro, co], c = custom_palette[name[-1]], resamplePeriod = rp)
            maxYlim[i] = plt.gca().get_ylim()[1]
            axes[ro, co].set_ylabel('Average Speed (mm/s)')
            axes[ro, co].set_xlabel('Time (hour)')
            axes[ro, co].set_title(name[0]+ ' ' + name[1])
            plotNames.append([name[-1]])
        for i in range(0, len(listOfPlots)):
            ro, co = listOfPlots[i][0][0:2]
            if YLim:
                axes[ro, co].set_ylim([0, YLim])
            else:
                axes[ro, co].set_ylim([0, np.max(maxYlim)])
        axes[ro, co].legend(plotNames, loc = 'upper right')
        plt.show()
        locoUtilities.espressoSaveFig(figure, 'splitTS', self.metaDataDf.Date[0], self.outputFolder)

        return figure,  axes

    def plotContrasts(self, y, colorBy, compareBy, groupBy = 'Temperature', plot_kwargs = dict()):
        resultsDf = self.resultsDf
        resultsDf['newPlotColumn'] = resultsDf[groupBy] + '  ' + resultsDf[compareBy]
        listIdx = tuple(np.unique(resultsDf[groupBy])[0]+'  ' +np.unique(resultsDf[compareBy])[::-1])
        for i in range(1, len(np.unique(resultsDf[groupBy]))):
            listIdx = (listIdx, tuple(np.unique(resultsDf[groupBy])[i]+'  '+np.unique(resultsDf[compareBy])[::-1]))
        
        print(listIdx)
        customPalette = locoPlotters.espressoCreatePalette(resultsDf[colorBy])
        setFont('Source Sans Bold', 10)
        dabestContrastData = dabest.load(resultsDf,
                               x='newPlotColumn', # the default for this test config is to group flies by genotype
                               y=y,
                               idx=listIdx,
                               paired=False
                              )

        fig = dabestContrastData.mean_diff.plot( color_col=colorBy, custom_palette = customPalette, **plot_kwargs)
        if len(np.unique(resultsDf[groupBy]))==1:
            flatListIdxC = [item.split('  ')[1] for item in listIdx]
            flatListIdxG = [item.split('  ')[0] for item in listIdx]
        else:
            flatListIdxC = [item.split('  ')[1] for t in listIdx for item in t]
            flatListIdxG = [item.split('  ')[0] for t in listIdx for item in t]
        fig.axes[0].set_xticklabels(flatListIdxC, rotation = 45, ha="right")
        ylim = fig.axes[0].get_ylim()
        for i in range(0, len(np.unique(resultsDf[groupBy]))):
            # fig.axes[0].text(0.5, ylim[1], flatListIdxG[0],  ha="center")
            fig.axes[0].text(0.5 + 2*i, ylim[1]*1.1, flatListIdxG[2*i],  ha="center")
        locoUtilities.espressoSaveFig(fig, y +'_contrast', self.metaDataDf.Date[0], self.outputFolder)
        return fig
        # diffListIdx = flatListIdx[]
        
        # fig.axes[1].set_xticklabels('Diff', rotation = 45, ha="right")

    # def saveEspressoLocomotionObj(self):
    #     with open(self.outputFolder + 'locoObj_'+ str(self.startMin) + 'to' + str(self.endMin) + '.pickle', 'wb') as f:
    #     # Pickle the 'data' dictionary using the highest protocol available.
    #         pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    # def loadEspressoLocomotionObj(pickleFileName):
    #     with open(pickleFileName, 'rb') as f:
    #         data = pickle.load(f)
    #     return data
