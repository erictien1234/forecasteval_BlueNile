# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 11:18:17 2025

@author: EricTien
"""

import os
path=__file__
os.chdir(os.path.dirname(path))
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
from datetime import date
import scipy

#%% load data
imergjjas=pd.read_csv('result/imerg_jjas.csv',index_col=0).values.flatten()

#%%
def monthforecast(nmmename,releasemonth):
    monthmask=np.full(251,False)
    for year in range(21):
        monthmask[releasemonth-1+year*12]=True
        
    for month in range(4):
        nmmedf=pd.read_csv('result/'+nmmename+'_lead'+str(6-releasemonth+month)+'_20012023.csv',index_col=0)
        if month==0:
            nmme=nmmedf[monthmask]*30
        else:
            nmme=nmme+nmmedf[monthmask]*30
    nmmeem=nmme.mean(axis=1)
    nmmeem.index=list(range(2001,2022))
    return nmmeem

nmmelist=['CanCM4i-IC3','CCSM4','CFSv2','GEM5-NEMO','GEOS5','GFDL-SPEAR']
forecastm=['June','May','April','March','February','January']
dist = scipy.stats.beta(21/2 - 1, 21/2 - 1, loc=-1, scale=2)
picorr=dist.ppf(0.95)
clist=['b','g','r','c','m','y']
plt.rcParams.update({'font.size':12})
fig,ax=plt.subplots(1)
for nmmeno in range(len(nmmelist)):
    corr=[]
    for releasemonth in range(6,0,-1):
        nmmeem=monthforecast(nmmelist[nmmeno],releasemonth)
        corr.append(np.corrcoef(imergjjas,nmmeem)[0,1])
    ax.plot(forecastm,corr,label=nmmelist[nmmeno],marker='o',c=clist[nmmeno])
ax.axhline(y=picorr,c='gray',linestyle='--')
ax.set_ylabel('Anomaly Correlation',fontsize=16)
ax.set_xlabel('Model Initialization Month',fontsize=16)
plt.legend(loc='lower center',ncols=3,bbox_to_anchor=(0.5,-0.4))
plt.show()

