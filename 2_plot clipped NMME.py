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
#%% loading IMERG and CHIRPS
imergjjas=pd.read_csv('result/imerg_jjas.csv',index_col=0).values.flatten()
chirpsjjas=pd.read_csv('result/chirps_jjas.csv',index_col=0).values.flatten()
#%% plotting IMERG, CHIRPS and NMME time series
def Juneforecast(nmmename):
    for month in range(6,10):
        nmmedf=pd.read_csv('result/'+nmmename+'_lead'+str(month-6)+'_20012023.csv',index_col=0)
        if month==6:
            nmme=nmmedf[monthmask]*30
        else:
            nmme=nmme+nmmedf[monthmask]*30
    nmmeem=nmme.mean(axis=1)
    nmmeem.index=list(range(2001,2022))
    return nmmeem

fig,ax=plt.subplots(layout="constrained")
ax.plot(list(range(2001,2022)),imergjjas,marker='o',color='black',label='IMERG')
ax.plot(list(range(2001,2022)),chirpsjjas,marker='o',color='gray',label='CHIRPS')

nmmelist=['CanCM4i-IC3','CCSM4','CFSv2','GEM5-NEMO','GEOS5','GFDL-SPEAR']
clist=['b','g','r','c','m','y']
monthmask=np.full(251,False)
for year in range(21):
    monthmask[5+year*12]=True

for nmmeno in [0,3,1,4,2,5]:
    nmmeem=Juneforecast(nmmelist[nmmeno])
    ax.plot(nmmeem.loc[2001:2021],label=nmmelist[nmmeno],alpha=0.8,c=clist[nmmeno])
ax.set_xticks(np.arange(2001,2022,4))
ax.set_xlim([2000.5,2021.5])
ax.set_ylabel('Seasonal Rainfall (mm)')
ax.set_xlabel('Year')
leg=fig.legend(labels=['IMERG','CHIRPS','CanCM4i','GEM-NEMO','CCSM4','GEOS5','CFSv2','GFDL-SPEAR'],loc='lower center',ncols=4,bbox_to_anchor=(0.5,-0.2),markerscale=2)
for no in [0,1,2,3,4,5,6,7]:
    leg.get_lines()[no].set_linewidth(6)
plt.show()
#%% plotting IMERG, CHIRPS, NMME percentage anomalies time series
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
    nmmeem=Juneforecast(nmmelist[nmmeno])
    bars.append(ax.bar(np.arange(2001-0.2+0.1*nmmeno,2022-0.2),(nmmeem.loc[2001:2021]/nmmeem.mean()*100)-100,label=nmmelist[nmmeno],alpha=0.8,color=clist[nmmeno],width=0.1))
ax.set_xticks(np.arange(2001,2022,2))
ax.set_xlim([2000.5,2021.5])
ax.set_ylim([-40,70])
ax.set_ylabel('Seasonal Rainfall Anomaly %')
ax.set_xlabel('Year')
ax.legend(handles=bars,labels=['IMERG','CHIRPS','CanCM4i','GEM-NEMO','CCSM4','GEOS5','CFSv2','GFDL-SPEAR'],loc='lower center',ncols=4,bbox_to_anchor=(0.5,-0.44),markerscale=2)
plt.show()

#%%plot category time series of IMERG and NMME

dfcatall=pd.DataFrame()
imergrank=imergjjas.argsort().argsort()+1
imergcat=pd.Series(np.full(21,3))
imergcat[imergrank<=8]=2
imergcat[imergrank<=2]=1
imergcat[imergrank>=14]=4
imergcat[imergrank>=20]=5
dfcatall=pd.concat([dfcatall,imergcat],axis=1)
for nmmeno in range(6):
    nmmeem=Juneforecast(nmmelist[nmmeno])
    nmmeemrank=nmmeem.argsort().argsort()+1
    nmmeemrank=nmmeemrank.reset_index(drop=True)
    nmmecat=pd.Series(np.full(21,3))
    nmmecat[nmmeemrank<=8]=2
    nmmecat[nmmeemrank<=2]=1
    nmmecat[nmmeemrank>=14]=4
    nmmecat[nmmeemrank>=20]=5
    dfcatall=pd.concat([dfcatall,nmmecat],axis=1)
dfcatall.columns=['IMERG']+nmmelist
dfcatall.index=list(range(2001,2022))
plt.rcParams.update({'font.size':10})
catnall=dfcatall.iloc[:,-7:]
fig,ax=plt.subplots(7,sharex=True,figsize=(7,11))
fig.subplots_adjust(hspace=0)
clist=['b','g','r','c','m','y']
markerlist=['.','o','v','*','x','+']
catname=['Drought','Dry','Normal','Wet','Very wet']
for nmmeno in range(6):
    for year in range(2001,2022):
        if year%2==1:
            ax[nmmeno].axvspan(year-0.5,year+0.5,facecolor='white',alpha=0.5)
        else:
            ax[nmmeno].axvspan(year-0.5,year+0.5,facecolor='gray',alpha=0.5)
    for cat in range(1,6):
        catmask=(catnall.iloc[:,nmmeno+1]==cat)
        ax[nmmeno].scatter(np.arange(2001,2022,1)[catmask],catnall.iloc[catmask.values,nmmeno+1],marker=markerlist[cat],color='black')
    ax[nmmeno].set_xlim(2000.5,2021.5)
    ax[nmmeno].set_ylim(0.5,5.5)
    ax[nmmeno].set_xticks(np.arange(2001,2022,4))
    ax[nmmeno].set_yticks(np.arange(1,6,1),['Drought','Dry','Normal','Wet','Very wet'])
    ax[nmmeno].set_ylabel(nmmelist[nmmeno])
for year in range(2001,2022):
    if year%2==1:
        ax[6].axvspan(year-0.5,year+0.5,facecolor='white',alpha=0.5)
    else:
        ax[6].axvspan(year-0.5,year+0.5,facecolor='gray',alpha=0.5)
cats=[]
for cat in range(5,0,-1):
    catmask=(catnall.iloc[:,0]==cat)
    cats.append(ax[6].scatter(np.arange(2001,2022,1)[catmask],catnall.iloc[catmask.values,0],marker=markerlist[cat],label=catname[cat-1],color='black'))
ax[6].set_xlim(2000.5,2021.5)
ax[6].set_ylim(-0.5,5.5)
ax[6].set_xticks(np.arange(2001,2022,4))
ax[6].set_yticks(np.arange(1,6,1),['Drought','Dry','Normal','Wet','Very wet'])
ax[6].set_ylabel('IMERG')
fig.legend(loc='outside lower center',bbox_to_anchor=(0.5,0.06),handlelength=0.4,ncols=5,markerscale=1.7,fontsize=14)
plt.show()