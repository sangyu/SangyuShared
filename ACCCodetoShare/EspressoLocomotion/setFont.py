#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 15:41:20 2020

@author: sangyuxu
"""
def setFont(fontSelection, fontSize):
    import matplotlib as mpl
    from matplotlib import rcParams
    mpl.font_manager._rebuild()
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = [fontSelection]
    rcParams['font.size'] = fontSize 

