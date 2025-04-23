# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 11:49:53 2025

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

#%% loading data, ONI, gph and DMI provided
imergjjas=pd.read_csv('result/imerg_jjas.csv',index_col=0).values.flatten()
ONINinodf=pd.read_csv('result/ONI Nino all lead.csv',index_col=0) # from https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php
gphalllead=pd.read_csv('result/gph 1000mb Nino all lead.csv',index_col=0) # from ERSST in Nino 3.4 region
DMIleadall=pd.read_csv('result/DMI all lead.csv',index_col=0) # from old https://psl.noaa.gov/data/timeseries/month/data/dmi.had.long.data, data has discontinued
imergjjasp=(imergjjas-imergjjas.mean())/imergjjas.mean()*100

#%% plotting 3 indices scatter plots in one
plt.rcParams.update({'font.size':16})
fig=plt.figure(figsize=(18,22),linewidth=5,edgecolor='black')
subfigs=fig.subfigures(3,1,linewidth=5,edgecolor='black')
ax1=subfigs[0].subplots(2,6)
counter=0
for a in range(2):
    for b in range(6):
        monthname=ONINinodf.columns[counter]
        ax1[a,b].scatter(ONINinodf.loc[ONINinodf[monthname]>=0.5,monthname].values,imergjjasp[ONINinodf[monthname]>=0.5],marker='o',color='red')
        ax1[a,b].scatter(ONINinodf.loc[ONINinodf[monthname]<=-0.5,monthname].values,imergjjasp[ONINinodf[monthname]<=-0.5],marker='o',color='blue')
        ax1[a,b].scatter(ONINinodf.loc[~((ONINinodf[monthname]>=0.5)+(ONINinodf[monthname]<=-0.5)),monthname].values,imergjjasp[~((ONINinodf[monthname]>=0.5)+(ONINinodf[monthname]<=-0.5))],marker='o',color='black')
        ax1[a,b].text(-2.55,18,ONINinodf.columns[counter],fontsize=20)
        corr=np.corrcoef(ONINinodf[monthname],imergjjasp)[0,1]
        ax1[a,b].annotate('r = '+str(round(corr,2)),xy=(190,190),xycoords='axes points',size=16,ha='right',va='top')
        ax1[a,b].set_xlim(-2.7,2.7)
        ax1[a,b].set_ylim(-22,22)
        ax1[a,b].axhline(y=0,color='grey',linestyle='--')
        ax1[a,b].axvline(x=0,color='grey',linestyle='--')
        ax1[a,b].set_box_aspect(1)
        #ax[a,b].grid()
        if b == 0:
            ax1[a,b].set_yticks([-20,-10,0,10,20])
        else:
            ax1[a,b].set_yticks([-20,-10,0,10,20],['','','','',''])
        if a == 0:
            ax1[a,b].set_xticks([-2,-1.5,-1,-0.5,0,0.5,1,1.5,2],['','','','','','','','',''])
        else:
            ax1[a,b].set_xticks([-2,-1.5,-1,-0.5,0,0.5,1,1.5,2],['-2','','-1','','0','','1','','2'])
        counter+=1
subfigs[0].supxlabel('ONI',fontsize=26,y=0.02)
subfigs[0].subplots_adjust(wspace=-0.1,hspace=0.2,left=0.05,right=0.975,top=0.94,bottom=0.12)
subfigs[0].text(0.01,0.95,'a)',fontsize=26)

ax2=subfigs[1].subplots(2,6)
counter=0
for a in range(2):
    for b in range(6):
        monthname=gphalllead.columns[counter]
        ax2[a,b].scatter(gphalllead.loc[gphalllead[monthname]>=2.5,monthname].values,imergjjasp[gphalllead[monthname]>=2.5],marker='o',color='red')
        ax2[a,b].scatter(gphalllead.loc[gphalllead[monthname]<=-2.5,monthname].values,imergjjasp[gphalllead[monthname]<=-2.5],marker='o',color='blue')
        ax2[a,b].scatter(gphalllead.loc[~((gphalllead[monthname]>=2.5)+(gphalllead[monthname]<=-2.5)),monthname].values,imergjjasp[~((gphalllead[monthname]>=2.5)+(gphalllead[monthname]<=-2.5))],marker='o',color='black')
        ax2[a,b].text(-21,18,gphalllead.columns[counter],fontsize=20)
        corr=np.corrcoef(gphalllead[monthname],imergjjasp)[0,1]
        ax2[a,b].annotate('r = '+str(round(corr,2)),xy=(190,190),xycoords='axes points',size=16,ha='right',va='top')
        ax2[a,b].set_xlim(-22,22)
        ax2[a,b].set_ylim(-22,22)
        ax2[a,b].axhline(y=0,color='grey',linestyle='--')
        ax2[a,b].axvline(x=0,color='grey',linestyle='--')
        ax2[a,b].set_box_aspect(1)
        #ax2[a,b].grid()
        if b == 0:
            ax2[a,b].set_yticks([-20,-10,0,10,20])
        else:
            ax2[a,b].set_yticks([-20,-10,0,10,20],['','','','',''])
        if a == 0:
            ax2[a,b].set_xticks([-15,-10,-5,0,5,10,15],['','','','','','',''])
        else:
            ax2[a,b].set_xticks([-15,-10,-5,0,5,10,15],['','-10','','0','','10',''])
        counter+=1
subfigs[1].supxlabel('GPH 1000mb anomaly (m)',fontsize=26,y=0.02)
subfigs[1].supylabel('Summer Precipitation Anomaly (%)',fontsize=24,x=0.01)
subfigs[1].subplots_adjust(wspace=-0.1,hspace=0.2,left=0.05,right=0.975,top=0.94,bottom=0.12)
subfigs[1].text(0.01,0.95,'b)',fontsize=26)

ax3=subfigs[2].subplots(2,6)
counter=0
for a in range(2):
    for b in range(6):
        monthname=DMIleadall.columns[counter]
        ax3[a,b].scatter(DMIleadall.loc[DMIleadall[monthname]>=0.5,monthname].values,imergjjasp[DMIleadall[monthname]>=0.5],marker='o',color='red')
        ax3[a,b].scatter(DMIleadall.loc[DMIleadall[monthname]<=-0.5,monthname].values,imergjjasp[DMIleadall[monthname]<=-0.5],marker='o',color='blue')
        ax3[a,b].scatter(DMIleadall.loc[~((DMIleadall[monthname]>=0.5)+(DMIleadall[monthname]<=-0.5)),monthname].values,imergjjasp[~((DMIleadall[monthname]>=0.5)+(DMIleadall[monthname]<=-0.5))],marker='o',color='black')
        ax3[a,b].text(-1.05,18,DMIleadall.columns[counter],fontsize=20)
        corr=np.corrcoef(DMIleadall[monthname],imergjjasp)[0,1]
        ax3[a,b].annotate('r = '+str(round(corr,2)),xy=(190,190),xycoords='axes points',size=16,ha='right',va='top')
        ax3[a,b].set_xlim(-1.1,1.1)
        ax3[a,b].set_xticks([-0.5,0,0.5,1])
        ax3[a,b].set_ylim(-22,22)
        ax3[a,b].axhline(y=0,color='grey',linestyle='--')
        ax3[a,b].axvline(x=0,color='grey',linestyle='--')
        ax3[a,b].set_box_aspect(1)
        #ax3[a,b].grid()
        if b == 0:
            ax3[a,b].set_yticks([-20,-10,0,10,20])
        else:
            ax3[a,b].set_yticks([-20,-10,0,10,20],['','','','',''])
        if a == 0:
            ax3[a,b].set_xticks([-0.5,0,0.5,1],['','','',''])
        else:
            ax3[a,b].set_xticks([-0.5,0,0.5,1])
        counter+=1
subfigs[2].supxlabel('DMI',fontsize=26,y=0.02)
subfigs[2].subplots_adjust(wspace=-0.1,hspace=0.2,left=0.05,right=0.975,top=0.94,bottom=0.12)
subfigs[2].text(0.01,0.95,'c)',fontsize=26)
plt.show()

#%% calculating elnino conditional POD and precision dry
nmmelist=['CanCM4i-IC3','CCSM4','CFSv2','GEM5-NEMO','GEOS5','GFDL-SPEAR']
dfcatall=pd.read_csv('result/NMME IMERG cat.csv',index_col=0)
ONIJJA=ONINinodf.loc[:,'JJA']
dryyearcatnmme=dfcatall.iloc[:,1:7].loc[(dfcatall.iloc[:,0]==1)+(dfcatall.iloc[:,0]==2)]
elninocat=dfcatall.iloc[:,0].loc[ONIJJA>=0.5]
dryyearindices=ONIJJA[dfcatall.iloc[:,0]<=2]
dryelninocat=dryyearcatnmme.join(elninocat,how='inner')
PODd=((dryyearcatnmme==1)+(dryyearcatnmme==2)).sum(axis=0)/dryyearcatnmme.shape[0]
PODdryelnino=((dryelninocat==1)+(dryelninocat==2)).sum(axis=0)/dryelninocat.shape[0]
PODdONI=(dryyearindices>=0.5).sum()/dryyearindices.shape[0]

precisiond=[]
precisiondelnino=[]
precisiondnonelnino=[]
nmmecat=dfcatall.iloc[:,1:7].copy()
nmmecat.columns=['CanCM4i','CCSM4','CFSv2','GEM-NEMO','GEOS5','GFDL-SPEAR']
IMERGcat=dfcatall.iloc[:,0].copy()
elninomask=ONIJJA>=0.5
IMERGdrymask=IMERGcat<=2
for nmmeno in range(6):
    nmmedrymask=nmmecat.iloc[:,nmmeno]<=2
    precisiond.append(IMERGcat.loc[nmmedrymask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].shape[0])
    try: precisiondelnino.append(IMERGcat.loc[nmmedrymask].loc[elninomask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].loc[elninomask].shape[0])
    except: precisiondelnino.append(0.00)
    try: precisiondnonelnino.append(IMERGcat.loc[nmmedrymask].loc[~elninomask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].loc[~elninomask].shape[0])
    except: precisiondnonelnino.append(0.00)
    
#%% PODw and precision during DMI positive
wetyearcatnmme=dfcatall.iloc[:,1:7].loc[(dfcatall.iloc[:,0]==4)+(dfcatall.iloc[:,0]==5)]
DMISON=DMIleadall.loc[:,'SON']
DMIpcat=dfcatall.iloc[:,0].loc[DMISON>=0.5]
wetyearindices=DMISON[dfcatall.iloc[:,0]>=4]
wetDMIpcat=wetyearcatnmme.join(DMIpcat,how='inner')
PODw=(wetyearcatnmme>=4).sum(axis=0)/wetyearcatnmme.shape[0]
PODwetDMIp=(wetDMIpcat>=4).sum(axis=0)/wetDMIpcat.shape[0]
PODwDMI=(wetyearindices>=0.5).sum()/wetyearindices.shape[0]

precisionw=[]
precisionwDMIp=[]
precisionwnonDMIp=[]
DMIpmask=DMISON>=0.5
IMERGwetmask=IMERGcat>=4
for nmmeno in range(6):
    nmmewetmask=nmmecat.iloc[:,nmmeno]>=4
    precisionw.append(IMERGcat.loc[nmmewetmask].loc[IMERGwetmask].shape[0]/IMERGcat.loc[nmmewetmask].shape[0])
    try: precisionwDMIp.append(IMERGcat.loc[nmmewetmask].loc[DMIpmask].loc[IMERGwetmask].shape[0]/IMERGcat.loc[nmmewetmask].loc[DMIpmask].shape[0])
    except: precisionwDMIp.append(0.00)
    try: precisionwnonDMIp.append(IMERGcat.loc[nmmewetmask].loc[~DMIpmask].loc[IMERGwetmask].shape[0]/IMERGcat.loc[nmmewetmask].loc[~DMIpmask].shape[0])
    except: precisionwnonDMIp.append(0.00)

#%% POD precision during GPH negative
GPHAMJ=gphalllead.loc[:,'AMJ']
GPHncat=dfcatall.iloc[:,0].loc[GPHAMJ<=-2.5]
dryyearindices=GPHAMJ[dfcatall.iloc[:,0]<=2]
dryGPHncat=dryyearcatnmme.join(GPHncat,how='inner')
PODdryGPHn=(dryGPHncat<=2).sum(axis=0)/dryGPHncat.shape[0]
PODdGPHn=(dryyearindices<=-2.5).sum()/dryyearindices.shape[0]

precisiondGPH=[]
precisiondGPHn=[]
precisiondnonGPHn=[]
nmmecat.columns=['CanCM4i','CCSM4','CFSv2','GEM-NEMO','GEOS5','GFDL-SPEAR']
GPHnmask=GPHAMJ<=-2.5
for nmmeno in range(6):
    nmmedrymask=nmmecat.iloc[:,nmmeno]<=2
    precisiondGPH.append(IMERGcat.loc[nmmedrymask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].shape[0])
    try: precisiondGPHn.append(IMERGcat.loc[nmmedrymask].loc[GPHnmask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].loc[GPHnmask].shape[0])
    except: precisiondGPHn.append(0.00)
    try: precisiondnonGPHn.append(IMERGcat.loc[nmmedrymask].loc[~GPHnmask].loc[IMERGdrymask].shape[0]/IMERGcat.loc[nmmedrymask].loc[~GPHnmask].shape[0])
    except: precisiondnonGPHn.append(0.00)
    
#%% new plot precision
plt.rcParams.update({'font.size':12})
fig=plt.figure(figsize=(6,6),layout="constrained")
ax1 = plt.subplot2grid(shape=(2, 1), loc=(0, 0), colspan=1)
ax2 = plt.subplot2grid(shape=(2, 1), loc=(1, 0), colspan=1)
clist=['b','g','r','c','m','y']
for nmmeno in range(6):
    ax1.bar(-0.25+nmmeno*0.1,precisiond[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
    ax1.bar(0.75+nmmeno*0.1,precisiondelnino[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
ax1.set_ylabel('Probability of dry summer',fontsize=14)
ax1.text(-0.38,0.95,'a)',fontsize=20)
ax1.set_xticks(np.arange(0,2),['Dry forecast','Dry|El Nino'])
ax1.set_yticks(np.arange(0.02,1.03,0.2),[0,0.2,0.4,0.6,0.8,1.0])
ax1.set_ylim(0,1.04)

for nmmeno in range(6):
    ax2.bar(-0.25+nmmeno*0.1,precisionw[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
    ax2.bar(0.75+nmmeno*0.1,precisionwDMIp[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
ax2.set_ylabel('Probability of wet summer',fontsize=14)
ax2.text(-0.38,0.95,'b)',fontsize=20)
ax2.set_xticks(np.arange(0,2),['Wet forecast','Wet|DMI>0.5'])
ax2.set_yticks(np.arange(0.02,1.03,0.2),[0,0.2,0.4,0.6,0.8,1.0])
ax2.set_ylim(0,1.04)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(),loc='lower center',ncols=3,bbox_to_anchor=(0.5,-0.12))
plt.show()

#%% new plot POD

plt.rcParams.update({'font.size':12})
fig=plt.figure(figsize=(6,6),layout="constrained")
ax1 = plt.subplot2grid(shape=(2, 1), loc=(0, 0), colspan=1)
ax2 = plt.subplot2grid(shape=(2, 1), loc=(1, 0), colspan=1)
clist=['b','g','r','c','m','y']
for nmmeno in range(6):
    ax1.bar(-0.25+nmmeno*0.1,PODd[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
    ax1.bar(0.75+nmmeno*0.1,PODdryelnino[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
ax1.set_ylabel('Dry POD',fontsize=16)
ax1.text(-0.38,0.95,'a)',fontsize=20)
ax1.set_xticks(np.arange(0,2),['Dry observation','Dry|El Nino'])
ax1.set_yticks(np.arange(0.02,1.03,0.2),[0,0.2,0.4,0.6,0.8,1.0])
ax1.set_ylim(0,1.04)

for nmmeno in range(6):
    ax2.bar(-0.25+nmmeno*0.1,PODw[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
    ax2.bar(0.75+nmmeno*0.1,PODwetDMIp[nmmeno]+0.02,color=clist[nmmeno],label=nmmelist[nmmeno],width=0.1)
ax2.set_ylabel('Wet POD',fontsize=16)
ax2.text(-0.38,0.95,'b)',fontsize=20)
ax2.set_xticks(np.arange(0,2),['Wet observation','Wet|DMI>0.5'])
ax2.set_yticks(np.arange(0.02,1.03,0.2),[0,0.2,0.4,0.6,0.8,1.0])
ax2.set_ylim(0,1.04)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(),loc='lower center',ncols=3,bbox_to_anchor=(0.5,-0.12))
plt.show()