# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 16:28:50 2025

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

imergjjas=pd.read_csv('result/imerg_jjas.csv',index_col=0).values.flatten()
chirpsjjas=pd.read_csv('result/chirps_jjas.csv',index_col=0).values.flatten()


fig,ax=plt.subplots(layout="constrained")
ax.plot(list(range(2001,2022)),imergjjas,marker='o',color='black',label='IMERG')
ax.plot(list(range(2001,2022)),chirpsjjas,marker='o',color='gray',label='CHIRPS')

nmmelist=['CanCM4i-IC3','CCSM4','CFSv2','GEM5-NEMO','GEOS5','GFDL-SPEAR']
clist=['b','g','r','c','m','y']
monthmask=np.full(251,False)
for year in range(21):
    monthmask[5+year*12]=True

for nmmeno in [0,3,1,4,2,5]:
    for month in range(6,10):
        nmmedf=pd.read_csv('result/'+nmmelist[nmmeno]+'_lead'+str(month-6)+'_20012023.csv',index_col=0)
        if month==6:
            nmme=nmmedf[monthmask]*30
        else:
            nmme=nmme+nmmedf[monthmask]*30
    nmmeem=nmme.mean(axis=1)
    nmmeem.index=list(range(2001,2022))
    ax.plot(nmmeem.loc[2001:2021],label=nmmelist[nmmeno],alpha=0.8,c=clist[nmmeno])
ax.set_xticks(np.arange(2001,2022,4))
ax.set_xlim([2000.5,2021.5])
ax.set_ylabel('Seasonal Rainfall (mm)')
ax.set_xlabel('Year')
leg=fig.legend(labels=['IMERG','CHIRPS','CanCM4i','GEM-NEMO','CCSM4','GEOS5','CFSv2','GFDL-SPEAR'],loc='lower center',ncols=4,bbox_to_anchor=(0.5,-0.2),markerscale=2)
for no in [0,1,2,3,4,5,6,7]:
    leg.get_lines()[no].set_linewidth(6)
plt.show()

fig,ax=plt.subplots(figsize=(10,4),layout="constrained")
bars=[]
for year in range(2001,2022):
    if year%2==1:
        ax.axvspan(year-0.5,year+0.5,facecolor='white',alpha=0.5)
    else:
        ax.axvspan(year-0.5,year+0.5,facecolor='gray',alpha=0.5)
bars.append(ax.bar(np.arange(2001-0.4,2022-0.4),(imergjjas/imergjjas.mean()*100)-100,color='black',label='IMERG',width=0.1))
bars.append(ax.bar(np.arange(2001-0.3,2022-0.3),(chirpsjjas/chirpsjjas.mean()*100)-100,color='gray',label='CHIRPS',width=0.1))
clist=['b','g','r','c','m','y']
for nmmeno in [0,3,1,4,2,5]:
    for month in range(6,10):
        nmmedf=pd.read_csv('result/'+nmmelist[nmmeno]+'_lead'+str(month-6)+'_20012023.csv',index_col=0)
        if month==6:
            nmme=nmmedf[monthmask]*30
        else:
            nmme=nmme+nmmedf[monthmask]*30
    nmmeem=nmme.mean(axis=1)
    nmmeem.index=list(range(2001,2022))
    bars.append(ax.bar(np.arange(2001-0.2+0.1*nmmeno,2022-0.2),(nmmeem.loc[2001:2021]/nmmeem.mean()*100)-100,label=nmmelist[nmmeno],alpha=0.8,color=clist[nmmeno],width=0.1))
ax.set_xticks(np.arange(2001,2022,2))
ax.set_xlim([2000.5,2021.5])
ax.set_ylim([-40,70])
ax.set_ylabel('Seasonal Rainfall Anomaly %')
ax.set_xlabel('Year')
ax.legend(handles=bars,labels=['IMERG','CHIRPS','CanCM4i','GEM-NEMO','CCSM4','GEOS5','CFSv2','GFDL-SPEAR'],loc='lower center',ncols=4,bbox_to_anchor=(0.5,-0.44),markerscale=2)
plt.show()
