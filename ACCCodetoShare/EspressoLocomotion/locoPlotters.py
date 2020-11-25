#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 14:30:12 2020

@author: Sanguyu Xu
xusangyu@gmail.com
"""

import matplotlib.pyplot as plt
import numpy as np
import locoUtilities
from matplotlib import colors
import dabest
from setFont import setFont

def espressoChamberStyling(ax, axisSwitch = 'off'):
    ax.set_aspect('equal')
    ax.spines['bottom'].set_color('gray')
    ax.spines['top'].set_color('gray')
    ax.spines['right'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.axis(axisSwitch)
    ax.set_xlim(0, 13)
    ax.set_ylim(-2, 18)


def espressoCreatePalette(items, testColor = 'crimson'):
    wes_palette, wes_colors = createWesAndersonPalette()
    colorPalette = {}
    keys = np.sort(np.unique(items))[::-1]
    colors = wes_palette
    n=0
    for i in range(len(keys)):
        if 'gal4' in keys[i]:
            if 'w1118' in keys[i]:
                colorPalette[keys[i]] = wes_colors['black']
                continue
            if 'acr' in keys[i]:
                colorPalette[keys[i]] = wes_colors['cyan']
                continue
            if 'chrimson' in keys[i]:
                colorPalette[keys[i]] = wes_colors['crimson']
                continue
            if 'tetx' in keys[i]:
                colorPalette[keys[i]] = wes_colors['eggplant']
                continue
        if 'ms' in keys[i]:
            if 'w1118' in keys[i]:
                colorPalette[keys[i]] = wes_colors['black']
                continue
            if 'cas' in keys[i]:
                colorPalette[keys[i]] = wes_colors['cyan']
                continue
        elif 'Sibling' in keys[i]:
            colorPalette[keys[i]] = wes_colors['black']
            continue
        elif 'Offspring' in keys[i]:
            colorPalette[keys[i]] = wes_colors[testColor]
            continue
        elif keys[i] == 'F':
            colorPalette[keys[i]] = wes_colors['hotpink']
            continue
        elif keys[i] == 'M':
            colorPalette[keys[i]] = wes_colors['lakeblue']
            continue
        elif keys[i] == 'VF':
            colorPalette[keys[i]] = wes_colors['eggplant']
            continue
        else:
            colorPalette[keys[i]] = colors[n]
            n += 1
    return colorPalette


def espressoPlotTracking(X, Y, flyName, colorPalette):
    plt.plot(X, Y, linewidth = 0.5, color = colorPalette[flyName])
    # plt.plot([7, 7], [0, 19], linewidth = 0.5, color = 'r')
    # plt.plot([0, 15], [12, 12], linewidth = 0.5, color = 'r')


def espressoPlotHeatmap(X, Y, flyGenotype, colorPalette):
    import matplotlib.colors as mcolors
    # plt.hist2d(X[~np.isnan(X)],Y[~np.isnan(Y)], bins=[12, 20],cmap=plt.cm.bone, range=np.array([(0, 13), (-1, 18)]), norm=mcolors.PowerNorm(0.6))
    plt.hist2d(X[~np.isnan(X)],Y[~np.isnan(Y)], bins=[12, 20],cmap=plt.cm.bone, range=np.array([(0, 13), (-1, 18)]))

def espressoPlotMeanHeatmaps(espLocoObj, binSize, row = None, col = None, verbose = False):
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    setFont('Source Sans Pro', 12)

    XX = espLocoObj.countLogDf.filter(regex = '_X')
    YY = espLocoObj.countLogDf.filter(regex = '_Y')
    H = []
    xedges = np.arange(-1, 14, binSize)
    yedges = np.arange(-3, 19, binSize)
    numlist = list(range(0, len(espLocoObj.metaDataDf)))
    smallHeatmapFigs = plt.figure (num = 1, figsize = [5, np.ceil((len(numlist)+1)/5)*0.8])
    n = 1
    for j in numlist:
    #        plotFunc(X.iloc[:, j-1], Y.iloc[:, j-1], flyGenotype, colorPalette)
        # print(str(j) + ' ' + espLocoObj.metaDataDf.Genotype[j])
        X = XX.iloc[:, j]
        Y = YY.iloc[:, j]
        h, xedges, yedges = np.histogram2d(X[~np.isnan(X)], Y[~np.isnan(Y)], bins = [xedges, yedges])
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        if verbose:
            plt.subplot(np.ceil((len(numlist)+1)/5), 5, n)
            plt.imshow(h.T, extent=extent, origin='lower', cmap = 'bone')
        n += 1
        H.append(h)
    Hall = np.dstack(H)
    Hall = Hall/50/60 #originally resampled at 50ms and to convert to minute from second/60
    listOfPlots, gp, custom_palette = subplotRowColColor(espLocoObj.metaDataDf, None, row, col)
    nr, nc = listOfPlots[-1][0][0:2]
    meanHeatmapFig, axes = plt.subplots(nrows=nr + 1, ncols=nc + 1, figsize = (3 * (nc + 1), 4 * (nr + 1)), squeeze = False)
    images = []
    for i in range(0, len(listOfPlots)):
        # print(listOfPlots[i])
        ro, co = listOfPlots[i][0][0:2]
        # print(listOfPlots[i][0][0:2])
        name = listOfPlots[i][1]
        # print(name)
        ind = gp[name]
        Hmean = np.mean(Hall[:, :, ind], axis = 2)
        setRCParamsAxesTicks(False)
        plt.plot([10, 12], [-1, -1], color = 'w', linewidth = 2)
        plt.text(11, -2, '2 mm', color = 'w', ha = 'center')
        images.append(axes[ro, co].imshow(Hmean.T, extent=extent, origin='lower', cmap = 'bone'))
        axes[ro, co].set_title(name[0]+ '\n' + name[1])
        axes[ro, co].label_outer()
    left = np.sum(np.sum(Hall[4:9, 21:25, :], axis = 0), axis = 0)
    right = np.sum(np.sum(Hall[10:15, 21:25, :], axis = 0), axis = 0)
    bottom = np.sum(np.sum(Hall[4:15, 4:7, :], axis = 0), axis = 0)
    resultsDf = espLocoObj.resultsDf

    resultsDf['left'] = left
    resultsDf['right'] = right
    resultsDf['bottom'] = bottom
    resultsDf['LR Preference'] = (resultsDf['left']- resultsDf['right'])/ (resultsDf['right']+resultsDf['left'])
    resultsDf['TB Preference'] = (resultsDf['right'] + resultsDf['left'] - resultsDf['bottom'])/ (resultsDf['bottom']+resultsDf['right']+resultsDf['left'])
    vmin = min(image.get_array().min() for image in images)
    vmax = max(image.get_array().max() for image in images)
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    for im in images:
        im.set_norm(norm)
    axins = inset_axes(axes[-1, -1],
                   width="5%",  # width = 5% of parent_bbox width
                   height="100%",  # height : 50%
                   loc='lower left',
                   bbox_to_anchor=(1.05, 0., 1, 1),
                   bbox_transform=axes[-1, -1].transAxes,
                   borderpad=0,
                   )
    meanHeatmapFig.colorbar(images[-1], cax=axins, ticks=[0, 5, 10, 15, 20])
    def update(changed_image):
        for im in images:
            if (changed_image.get_cmap() != im.get_cmap()
                    or changed_image.get_clim() != im.get_clim()):
                im.set_cmap(changed_image.get_cmap())
                im.set_clim(changed_image.get_clim())
    for im in images:
        im.callbacksSM.connect('changed', update)
    plt.show()
    meanHeatmapFileName = 'meanHeatmapFig'+ '_' + str(col) + '_' + str(row) + str(espLocoObj.startMin) + '-' + str(espLocoObj.endMin) + 'min'
    locoUtilities.espressoSaveFig(meanHeatmapFig, meanHeatmapFileName, espLocoObj.metaDataDf.Date[0], espLocoObj.outputFolder)
    # locoUtilities.espressoWriteDictToCSV(espLocoObj.outputFolder+meanHeatmapFileName+'_ConditionsTable.csv', gp)
    if verbose:
        return meanHeatmapFig, axes, Hall, resultsDf, smallHeatmapFigs
    else:
        return meanHeatmapFig, axes, Hall, resultsDf


def plotBoundedLine(x, Y, ax=None, c = 'k', resamplePeriod = '200s'):
    if ax is None:
        ax = plt.gca()
    setRCParamsAxesTicks(True)
    if resamplePeriod:
        Y = Y.resample(resamplePeriod).agg(np.mean)
        x = x.resample(resamplePeriod).agg(np.mean)
    y = np.nanmean(Y, axis = 1)
    ci = np.nanstd(Y, axis = 1)/(np.sqrt(Y.shape[1]))*1.96
    ax.plot(x, y, color = c) ## example plot here
    ax.fill_between(x, y+ci,  y-ci, color = c, alpha=0.2)
    return(ax)



def putThingsInToChamberSubplot(countLogDf, metaDataDf, plotFunc = espressoPlotTracking, showID = True):
    noOfRows=int(np.ceil(len(metaDataDf)/15))
    chamberSmalls, axarr = plt.subplots(noOfRows, 15, figsize = [20, noOfRows*2.5])
    metaDataDf = metaDataDf.reset_index()
    for j in metaDataDf.index:
        id = metaDataDf.loc[j, 'ID']
        col = np.mod(id-1, 15)
        row = int((id - col)/15)
        chamberSmalls.sca(axarr[row, col])
        colorPalette = espressoCreatePalette(metaDataDf['Genotype'])
        flyGenotype = metaDataDf['Genotype'][j]
        X = countLogDf.filter(regex = '_X')
        Y = countLogDf.filter(regex = '_Y')
#        plotFunc(X.iloc[:, j-1], Y.iloc[:, j-1], flyGenotype, colorPalette)
        plotFunc(X.iloc[:, j], Y.iloc[:, j], flyGenotype, colorPalette)
#        axarr[row, col].set_title(flyGenotype)
        if showID:
            plt.title(metaDataDf.loc[j, 'ID'])
    chamberSmalls.suptitle(metaDataDf.loc[0, 'Date'] + ' ' + str(metaDataDf.loc[0, 'Temperature']) )
    for row in range(0, axarr.shape[0]):
        for col in range(0, axarr.shape[1]):
            espressoChamberStyling(axarr[row, col])
    return chamberSmalls, axarr
#


def subplotRowColColor(metaDataDf, colorBy, row = None, col = None):
    m = metaDataDf
    m = m.applymap(str)
    if row == None:
        m['row'] = ' '
        row = 'row'
    if col == None:
        m['col'] = ' '
        col = 'col'
    if colorBy == None:
        m['colorBy'] = ' '
        colorBy = 'colorBy'
    gp = m.groupby([row, col, colorBy]).groups
    if m.Status.str.contains('Offspring').sum()>0:
        testGenotypeName = np.unique(m.loc[m['Status'] == 'Offspring', 'Genotype'])[0]
        if 'chrimson' in testGenotypeName or 'csch' in testGenotypeName:
            testGenotypeColor = 'crimson'
        elif 'acr' in testGenotypeName:
            testGenotypeColor = 'cyan'
        elif 'tetx' in testGenotypeName:
            testGenotypeColor = 'eggplant'
        elif 'cas' and 'ms' in testGenotypeName:
            testGenotypeColor = 'cyan'
    else:
        testGenotypeColor = 'lakeblue'
    custom_palette = espressoCreatePalette(m[colorBy], testColor = testGenotypeColor)
    if row == 'Temperature':
        uniqueRows = np.sort(np.unique(m[row]))
    else:
        uniqueRows = np.sort(np.unique(m[row]))[::-1]
    w1118InUniqueRows = ['w1118' not in uniqueRows[i] for i in range(len(uniqueRows))]
    newind = np.argsort(w1118InUniqueRows)
    uniqueRows = uniqueRows[newind]
    if col == 'Temperature':
        uniqueCols = np.sort(np.unique(m[col]))
    else:
        uniqueCols = np.sort(np.unique(m[col]))[::-1]

    w1118InUniqueCols = ['w1118' not in uniqueCols[i] for i in range(len(uniqueCols))]
    newind = np.argsort(w1118InUniqueCols)
    uniqueCols = uniqueCols[newind]
    if colorBy == 'Temperature':
        uniqueColors = np.sort(np.unique(m[colorBy]))
    else:
        uniqueColors = np.sort(np.unique(m[colorBy]))[::-1]
    w1118InUniqueColors = ['w1118' not in uniqueColors[i] for i in range(len(uniqueColors))]
    newind = np.argsort(w1118InUniqueColors)
    uniqueColors = uniqueColors[newind]


    listOfPlotsUnfiltered = [((i, j, k), (r, c, cl)) for i, r in enumerate(uniqueRows) for j, c in enumerate(uniqueCols) for k, cl in enumerate(uniqueColors)]
    listOfPlots = [i for i in listOfPlotsUnfiltered if i[1] in gp.keys()]
    return listOfPlots, gp, custom_palette




import seaborn as sns
import numpy as np
def createWesAndersonPalette():
    wes_colors = {}
    wes_colors['lightgray'] = np.divide([110, 100, 102], 255)
    wes_colors['orange'] = np.divide([230, 82,  15], 255)
    wes_colors['cyan'] = np.divide([73, 186,  186], 255)
    wes_colors['crimson'] = np.divide([173, 9,  16], 255)
    wes_colors['ocre'] = np.divide([249, 166,  0], 255)
    wes_colors['darkgray'] = np.divide([55, 57,  61], 255)
    wes_colors['hotpink'] = np.divide([210, 78, 130], 255)
    wes_colors['lakeblue'] = np.divide([82, 150, 228], 255)
    wes_colors['eggplant'] = np.divide([120, 43, 102], 255)
    wes_colors['verde'] = np.divide([74, 104, 41], 255)
    wes_colors['chocolate'] = np.divide([65, 20, 17], 255)
    wes_colors['midnight'] = np.divide([10, 42,  87], 255)
    wes_colors['brick'] = np.divide([235, 59, 32], 255)
    wes_colors['black'] = np.divide([12, 13, 24], 255)
    wes_palette = tuple(map(tuple, wes_colors.values()))
    # sns.palplot(wes_palette)
    return wes_palette, wes_colors

def setRCParamsAxesTicks(axesState, gridState = False):
    plt.rcParams['axes.grid'] = gridState
    plt.rcParams['ytick.left'] = axesState
    plt.rcParams['xtick.bottom'] = axesState
    plt.rcParams['ytick.labelleft'] = axesState
    plt.rcParams['xtick.labelbottom'] = axesState
