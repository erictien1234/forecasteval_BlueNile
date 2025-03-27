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
pd.DataFrame(preccropall).to_csv('result/imerg 20012023.csv')


coarseimerg=precimerg.coarsen(Lats=10,Lons=10).mean()
anoimergwetseason=xr.DataArray()
for years in range(1,21):
    if years==1:
        anoimergwetseason=coarseimerg[years*12-7:years*12-3].sum(axis=0)
    else:
        anoimergwetseason=xr.concat([anoimergwetseason,coarseimerg[years*12-7:years*12-3].sum(axis=0)],'time')
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
    cl=(precimerg[monthmask]*24*30).mean(axis=0).plot(ax=ax[a,b],levels=np.arange(0,260,20),cmap=preccmap,add_colorbar=False)
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
plt.show()

monthmaski=np.full(249,False)
for year in range(21):
    for month in range(5,9):
        monthmaski[month+year*12]=True

preccolor=plt.colormaps.get_cmap('RdBu')(np.linspace(0,1,15))
purple=np.array([165/256, 55/256, 253/256,1])
preccolor=np.append(preccolor,[purple],axis=0)
preccmap=ListedColormap(preccolor)
fig,ax=plt.subplots(1)
cl=(precimerg[monthmaski]*24*30*4).mean(axis=0).plot(ax=ax,levels=np.arange(0,1500,100),cmap=preccmap)
world.boundary.plot(ax=ax,color='black',linewidth=0.5,alpha=0.3)
nile.boundary.plot(ax=ax,color='black')
bluenile.boundary.plot(ax=ax,color='Lime')
whitenile.boundary.plot(ax=ax,color='lime',linestyle=(0,(5,5)))
ax.set_aspect('equal')
ax.set_title('Annual',fontsize=18)
plt.show()

#%% NMME
#nmmelist=['CanCM4i']
nmmedir='E:/NMME/'
nmmelist=['CanCM4i-IC3','CCSM4','CFSv2','GEM5-NEMO','GEOS5','GFDL-SPEAR']
Junenmmeall=[]
Junenmmecorrall=[]
for nmmemodel in nmmelist:
    startyear=2001
    startmonth=1
    precall=[]
    precBN=[]
    precnmmeavgL0,precnmmeavgL1,precnmmeavgL2,precnmmeavgL3,precnmmeavgL4,precnmmeavgL5,precnmmeavgL6,precnmmeavgL7=[],[],[],[],[],[],[],[]
    precnmmelist=[precnmmeavgL0,precnmmeavgL1,precnmmeavgL2,precnmmeavgL3,precnmmeavgL4,precnmmeavgL5,precnmmeavgL6,precnmmeavgL7]
    for i in range(251):
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
        if nmmemodel=='CFSv2':
            if year >=1981 and year <1985:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 1981-1984.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 1981-1984.nc')
            elif year>=1985 and year<1988:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 1985-1988.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 1985-1988.nc')
            elif year>=1989 and year<1992:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 1989-1992.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 1989-1992.nc')
            elif year>=1993 and year<1996:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 1993-1996.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 1993-1996.nc')
            elif year>=1997 and year<2000:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 1997-2000.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 1997-2000.nc')
            elif year>=2001 and year<2004:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2001-2004.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2001-2004.nc')
            elif year>=2005 and year<2008:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2005-2008.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2005-2008.nc')
            elif year>=2009 and year<2012:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2009-2012.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2009-2012.nc')
            elif year>=2013 and year<2016:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2013-2016.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2013-2016.nc')
            elif year>=2017 and year<2020:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2017-2020.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2017-2020.nc')
            elif year>=2021:
                nmme=Dataset(nmmedir+nmmemodel+'/precip M1-14 2021-present.nc')
                nmme1=Dataset(nmmedir+nmmemodel+'/precip M15-28 2021-present.nc')
        else:
            if year >=1981 and year <1985:
                nmme=Dataset(nmmedir+nmmemodel+'/precip 1981-1984.nc')
            elif year>=1985 and year<1988:
                nmme=Dataset(nmmedir+nmmemodel+'/precip 1985-1988.nc')
            elif year>=1989 and year<1992:
                if nmmemodel=='GFDL-SPEAR':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 1991-1992.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 1989-1992.nc')
            elif year>=1993 and year<1996:
                nmme=Dataset(nmmedir+nmmemodel+'/precip 1993-1996.nc')
            elif year>=1997 and year<2000:
                nmme=Dataset(nmmedir+nmmemodel+'/precip 1997-2000.nc')
            elif year>=2001 and year<2004:
                if nmmemodel=='GEOS5':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2016.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2004.nc')
            elif year>=2005 and year<2008:
                if nmmemodel=='GEOS5':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2016.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2005-2008.nc')
            elif year>=2009 and year<2012:
                if nmmemodel=='GEOS5':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2016.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2009-2012.nc')
            elif year>=2013 and year<2016:
                if nmmemodel=='GEOS5':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2016.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2013-2016.nc')
            elif year>=2017 and year<2020:
                if nmmemodel=='GEOS5':
                    if i==192:#201701 should be in 2001-2016 for GEOS5
                        nmme=Dataset(nmmedir+nmmemodel+'/precip 2001-2016.nc')
                    else:
                        nmme=Dataset(nmmedir+nmmemodel+'/precip 2017-2020.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2017-2020.nc')
            elif year>=2021:
                if nmmemodel=='CanCM4i-IC3' or nmmemodel=='GEM5-NEMO':
                    if i < 251:
                        nmme=Dataset(nmmedir+nmmemodel+'/precip 2017-2020.nc')
                    else:
                        nmme=Dataset(nmmedir+nmmemodel+'/precip 202110-present.nc')
                elif nmmemodel=='GFDL-SPEAR':
                    nmme=Dataset(nmmedir+nmmemodel+'/precip M1-15 2021-present.nc')
                else:
                    nmme=Dataset(nmmedir+nmmemodel+'/precip 2021-present.nc')
        month=np.where(nmme['S'][:]==492+i)[0][0] # month 684=20170101,492=20010101
        Latsouth=int(np.where(nmme['Y'][:]==-5)[0])
        Latnorth=int(np.where(nmme['Y'][:]==(35+1))[0])
        Lonwest=int(np.where(nmme['X'][:]==15)[0])
        Loneast=int(np.where(nmme['X'][:]==(54+1))[0]) #extent N5.5,S--34.5;W-74.5,E-35.5
        Latsnmme = nmme['Y'][Latsouth:Latnorth]
        Lonsnmme = nmme['X'][Lonwest:Loneast]
        nmmex,nmmey=np.float32(np.meshgrid(Lonsnmme, Latsnmme))
        if nmme['prec'].dimensions==('S','L','M','Y','X'):
            if nmmemodel == 'CFSv2':
                precnmme=np.ma.concatenate([nmme['prec'][month,0:9,:,Latsouth:Latnorth,Lonwest:Loneast],nmme1['prec'][month,0:9,:,Latsouth:Latnorth,Lonwest:Loneast]],axis=1)
                precnmme=xr.DataArray(precnmme,dims=['L','M','Lats','Lons'],coords=[range(9),range(1,len(nmme['M'])+len(nmme1['M'])+1),Latsnmme,Lonsnmme])
            else:
                precnmme=nmme['prec'][month,0:9,:,Latsouth:Latnorth,Lonwest:Loneast]
                precnmme=xr.DataArray(precnmme,dims=['L','M','Lats','Lons'],coords=[range(9),range(1,len(nmme['M'])+1),Latsnmme,Lonsnmme])
            if i == 0:
                precall=xr.DataArray(precnmme.mean(axis=1))
            else:
                precall=xr.concat([precall,precnmme.mean(axis=1)],'time')
        elif nmme['prec'].dimensions==('S','M','L','Y','X'):
            precnmme=nmme['prec'][month,:,0:9,Latsouth:Latnorth,Lonwest:Loneast]
            precnmme=xr.DataArray(precnmme,dims=['M','L','Lats','Lons'],coords=[range(1,len(nmme['M'])+1),range(9),Latsnmme,Lonsnmme])
            if i == 0:
                precall=xr.DataArray(precnmme.mean(axis=0))
            else:
                precall=xr.concat([precall,precnmme.mean(axis=0)],'time')
        precnmme.rio.write_crs(4326,inplace=True)
        precnmme.rio.set_spatial_dims('Lons','Lats',inplace=True)
        cropped=precnmme.rio.clip(bluenile['geometry'],crs=4326)
        
        if nmme['prec'].dimensions==('S','L','M','Y','X'):
            if nmmemodel=='GEOS5':
                for lead in range(len(precnmmelist)):
                    precnmmelist[lead].append(cropped[lead].mean(dim=['Lons','Lats'])[0:4])
            elif nmmemodel=='GFDL-SPEAR':
                for lead in range(len(precnmmelist)):
                    precnmmelist[lead].append(cropped[lead].mean(dim=['Lons','Lats'])[0:15])
            else:
                for lead in range(len(precnmmelist)):
                    precnmmelist[lead].append(cropped[lead].mean(dim=['Lons','Lats']))
        elif nmme['prec'].dimensions==('S','M','L','Y','X'):
            for lead in range(len(precnmmelist)):
                precnmmelist[lead].append(cropped[:,lead].mean(dim=['Lons','Lats']))
        
        print(nmmemodel+' '+str(year)+' '+strmonth+' done.')
    precnmmealllead=xr.DataArray(precnmmelist,dims=['lead','time','M'])
    for lead in range(len(precnmmelist)):
        precnmmealllead[lead].to_pandas().to_csv('result/'+nmmemodel+'_lead'+str(lead)+'_20012023.csv')

    
    monthmask=np.full(251,False)
    monthmask2=np.full(249,False)
    junemask=np.full(251,False)
    for year in range(21):
        for month in range(5,9):
            monthmask[month+year*12]=True
            monthmask2[month+year*12]=True
            if month==5:
                junemask[month+year*12]=True
    Junenmmeall.append(precall[junemask,0:4].mean(axis=(0,1))*122)
    
    release=6
    #for release in range(6,3,-1):
    forecastprec=xr.DataArray()
    for years in range(20):
        if years==0:
            forecastprec=precall[release-1,6-release:10-release].sum(axis=0)
        else:
            forecastprec=xr.concat([forecastprec,precall[:][release-1+12*years,6-release:10-release].sum(axis=0)],'time')
    forecastprec=forecastprec-forecastprec.mean(axis=0)
    anoimergwetseason['Lats']=forecastprec.Lats
    anoimergwetseason['Lons']=forecastprec.Lons
    forecastcorrimerg=xr.corr(anoimergwetseason[:20],forecastprec,dim='time')
    Junenmmecorrall.append(forecastcorrimerg)

preccolor=plt.colormaps.get_cmap('RdBu')(np.linspace(0,1,11))
purple=np.array([165/256, 55/256, 253/256,1])
preccolor=np.append(preccolor,[purple],axis=0)
preccmap=ListedColormap(preccolor)

fig,ax=plt.subplots(3,3,figsize=(11,11),layout="constrained")
counter=0
cl=(coarseimerg[monthmaski]*24*30*4).mean(axis=0).plot(ax=ax[1,0],levels=np.arange(0,1650,150),cmap=preccmap,add_colorbar=False)
world.boundary.plot(ax=ax[1,0],color='black',linewidth=0.5,alpha=0.3)
nile.boundary.plot(ax=ax[1,0],color='black')
bluenile.boundary.plot(ax=ax[1,0],color='Lime')
whitenile.boundary.plot(ax=ax[1,0],color='lime',linestyle=(0,(5,5)))
ax[1,0].set_aspect('equal')
ax[1,0].set_title('IMERG',fontsize=24)
ax[1,0].set_ylabel('Latitude',fontsize=18)
ax[1,0].set_xlabel('')
ax[0,0].axis('off')
ax[2,0].axis('off')
for a in range(3):
    for b in range(2):
        cl=Junenmmeall[counter].plot(ax=ax[a,b+1],levels=np.arange(0,1650,150),cmap=preccmap,add_colorbar=False)
        world.boundary.plot(ax=ax[a,b+1],color='black',linewidth=0.5,alpha=0.3)
        nile.boundary.plot(ax=ax[a,b+1],color='black')
        bluenile.boundary.plot(ax=ax[a,b+1],color='Lime')
        whitenile.boundary.plot(ax=ax[a,b+1],color='lime',linestyle=(0,(5,5)))
        ax[a,b+1].set_title(nmmelist[counter],fontsize=24)
        ax[a,b+1].set_aspect('equal')
        ax[a,b+1].set_xlabel('')
        ax[a,b+1].set_ylabel('')
        if (a!=0 and b!=0) or (a!=2 and b!=0):
            ax[a,b+1].set_yticklabels([])
        if (a!=2 and b!=0) or (a!=2 and b!=1):
            ax[a,b+1].set_xticklabels([])
        counter+=1
ax[1,1].set_yticklabels([])
ax[2,1].set_xlabel('Longitude',fontsize=18)
fig.colorbar(cl,ax=ax[:,2],shrink=0.8,ticks=np.arange(0,1650,150),label='mm/season')
plt.show()

corrcolor=plt.colormaps.get_cmap('RdBu')(np.linspace(0,1,9))
corrcolor[3]=np.array([1,1,1,1])
corrcolor[4]=np.array([1,1,1,1])
corrcmap=ListedColormap(corrcolor)

#new correlation spatial plot, all in one
fig,ax=plt.subplots(2,3,figsize=(12,8),layout="constrained")
counter=0
for a in range(2):
    for b in range(3):
        cl=Junenmmecorrall[counter].plot(ax=ax[a,b],levels=[-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1],cmap=corrcmap,add_colorbar=False)
        world.boundary.plot(ax=ax[a,b],color='black',linewidth=0.5,alpha=0.3)
        nile.boundary.plot(ax=ax[a,b],color='black')
        bluenile.boundary.plot(ax=ax[a,b],color='Lime')
        whitenile.boundary.plot(ax=ax[a,b],color='lime',linestyle=(0,(5,5)))
        ax[a,b].set_title(nmmelist[counter],fontsize=24)
        ax[a,b].set_aspect('equal')
        ax[a,b].set_xlabel('')
        ax[a,b].set_ylabel('')
        if a==0:
            ax[a,b].set_xticklabels([])
        if b!=0:
            ax[a,b].set_yticklabels([])
        counter+=1
ax[1,1].set_xlabel('Longitude',fontsize=18)
fig.supylabel('Latitude',fontsize=18)
fig.colorbar(cl,ax=ax[:,2],shrink=0.8,ticks=[-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1],label='correlation')
plt.show()