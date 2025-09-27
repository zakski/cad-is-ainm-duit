import numpy as np
import pandas as pd
import regex as re

import math
import glob
import os


import leagueconst as const
import leaguefunc as func

from pandas import Int64Dtype
from pathlib import Path
#from scipy import stats



# File Read
print('Load League Data From Path: ' + const.dirLeagueName)
#footData = pd.read_csv(dataFootballLeagueName,header=0,dtype=footieTypes,index_col=False)
leagueHockDF = pd.read_csv(const.dataHockLeagueName,header=0,dtype=const.leagueTypes,index_col=False)
leagueRugLeagueDF = pd.read_csv(const.dataRugLeagueLeagueName,header=0,dtype=const.leagueTypes,index_col=False)

teamsHockDF = pd.read_csv(const.dataTeamsHockName,header=0,dtype=const.teamTypes,index_col=False)

os.makedirs(const.resultsInterDirName, exist_ok=True)
os.makedirs(const.resultsHockDirName, exist_ok=True)
os.makedirs(const.resultsDirName, exist_ok=True)

#distribution = stats.poisson
#data = yearDF['cupsFolded'].values
#params = distribution.fit(data)
#print(params)
#ks_stat, ks_p_value = stats.kstest(data,distribution.cdf,args=params)
#print(f'KS Stat: {ks_stat}')
#print(f'P-value: {ks_p_value}')

# summarise Events
hockLeaguesDF = func.processSeasonsEvents(leagueHockDF,True,const.resultsHockDirName)
hockTeamsDF = func.processTeamsEvents(teamsHockDF, 'ice hockey',True,const.resultsHockDirName)
hockDF = hockLeaguesDF.merge(hockTeamsDF,how='inner', left_on='periodName', right_on='periodName')
hockDF.to_csv(os.path.join(const.resultsHockDirName,'all_sum.csv'),index=False)

RugLeagueLeaguesDF = func.processSeasonsEvents(leagueRugLeagueDF,True,const.resultsInterDirName)

# summarise Teams
#
#for name, group in orgFootData:
#    fileName = '{filePrefix}_{grouping}_{name}.csv'.format(filePrefix='eng',grouping='foot',name=name)
#    dirName = os.path.join(resultsInterDirName,'{grouping}_{name}'.format(grouping='foot',name=name))
#    os.makedirs(dirName, exist_ok=True)
#
#    print('Writing {name}'.format(name=fileName))
#    group.to_csv(os.path.join(dirName,fileName), index=False)