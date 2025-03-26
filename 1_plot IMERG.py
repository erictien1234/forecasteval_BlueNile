# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 17:30:25 2025

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
#%% set IMERG dir
IMERGdir='E:/UCLA 20240920/research/IMERG V7 final'

#%% plotting IMERG
world=gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
nile=gpd.read_file('shp/Nile Basin.shp')
bluenile=gpd.read_file('shp/Blue Nile Basin.shp')
whitenile=gpd.read_file('shp/White Nile Basin All.shp')

startyear=2001
startmonth=1

precimerg,preccropall,precchirps=[],[],[]
for i in range(249):
    #Loading data
    year=startyear
    monthi = startmonth+i
    while monthi > 12:
        monthi=monthi-12
        year+=1
    strmonth=''
    if monthi < 10:
        strmonth='0'+str(monthi)
    else:
        strmonth=str(monthi)
    f=Dataset(IMERGdir+'/3B-MO.MS.MRG.3IMERG.'+str(year)+strmonth+'01-S000000-E235959.'+strmonth+'.V07B.HDF5')
    #imerg prec unit: mm/hr
    
    #Setting IMERG and forecast data extent
    #extent N5.5,S--34.5;W-74.5,E-35.5
    precip = f['Grid/precipitation'][0][1945:2345,845:1255].transpose()
    theLats = f['Grid/lat'][845:1255]
    theLons = f['Grid/lon'][1945:2345]
    
    precip = xr.DataArray(precip,dims=['Lats','Lons'],coords=[theLats,theLons])
    precip=precip.where(precip>0,0)
    x, y = np.float32(np.meshgrid(theLons, theLats))
    precip.rio.write_crs(4326,inplace=True)
    precip.rio.set_spatial_dims('Lons','Lats',inplace=True)
    preccrop=precip.rio.clip(bluenile['geometry'],crs=4326).mean()
    if i==0:
        precimerg=xr.DataArray(precip)
        preccropall=xr.DataArray(preccrop)
    else:
        precimerg=xr.concat([precimerg,precip],'time')
        preccropall=xr.concat([preccropall,preccrop],'time')
    print(str(year)+' '+strmonth+' done.')
#pd.DataFrame(preccropall).to_csv('result/imerg Itaipu 20012023.csv')


coarseimerg=precimerg.coarsen(Lats=10,Lons=10).mean()
anoimergwetseason=xr.DataArray()
for years in range(1,23):
    if years==1:
        anoimergwetseason=coarseimerg[years*12-2:years*12+3].sum(axis=0)
    else:
        anoimergwetseason=xr.concat([anoimergwetseason,coarseimerg[years*12-2:years*12+3].sum(axis=0)],'time')
anoimergwetseason=anoimergwetseason-anoimergwetseason.mean(axis=0)

plt.rcParams['font.size'] = 14

preccolor=plt.colormaps.get_cmap('RdBu')(np.linspace(0,1,12))
purple=np.array([165/256, 55/256, 253/256,1])
preccolor=np.append(preccolor,[purple],axis=0)
preccmap=ListedColormap(preccolor)
fig,ax=plt.subplots(2,6,figsize=(26,8),layout="constrained")
for month in range(12):
    monthmask=np.full(249,False)
    if month>8:
        years=20
    else:
        years=21
    for year in range(years):
        monthmask[month+year*12]=True

    a=int(month/6)
    b=month%6
    cl=(precimerg[monthmask]*24*30).mean(axis=0).plot(ax=ax[a,b],levels=np.arange(0,390,30),cmap=preccmap,add_colorbar=False)
    world.boundary.plot(ax=ax[a,b],color='black',linewidth=0.5,alpha=0.3)
    nile.boundary.plot(ax=ax[a,b],color='black')
    bluenile.boundary.plot(ax=ax[a,b],color='Lime')
    whitenile.boundary.plot(ax=ax[a,b],color='lime',linestyle=(0,(5,5)))
    ax[a,b].set_aspect('equal')
    ax[a,b].set_title('month '+str(month+1),fontsize=18)
    if a==0:
        ax[a,b].set_xlabel('')
        ax[a,b].set_xticklabels([])
    if b!=0:
        ax[a,b].set_ylabel('')
        ax[a,b].set_yticklabels([])
fig.colorbar(cl,ax=ax[:,5],shrink=0.8,ticks=np.arange(0,390,30),label='mm/month')
#plt.savefig('plots/TE precip spatial IMERG monthly.png')
plt.show()

preccolor=plt.colormaps.get_cmap('RdBu')(np.linspace(0,1,11))
purple=np.array([165/256, 55/256, 253/256,1])
preccolor=np.append(preccolor,[purple],axis=0)
preccmap=ListedColormap(preccolor)
fig,ax=plt.subplots(1)
cl=(precimerg[:240]*24*365).mean(axis=0).plot(ax=ax,levels=np.arange(0,2750,250),cmap=preccmap)
world.boundary.plot(ax=ax,color='black',linewidth=0.5,alpha=0.3)
nile.boundary.plot(ax=ax,color='black')
bluenile.boundary.plot(ax=ax,color='Lime')
whitenile.boundary.plot(ax=ax,color='lime',linestyle=(0,(5,5)))
ax.set_aspect('equal')
ax.set_title('Annual',fontsize=18)
#plt.savefig('plots/TE precip spatial IMERG Annual.png')
plt.show()