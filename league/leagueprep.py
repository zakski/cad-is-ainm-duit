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
leagueRugLeagueDF = pd.read_csv(const.dataLeagueRugLeagueName,header=0,dtype=const.leagueTypes,index_col=False)

teamsHockDF = pd.read_csv(const.dataTeamsHockName,header=0,dtype=const.teamTypes,index_col=False)
teamsRugLeagueDF = pd.read_csv(const.dataTeamsRugLeagueName,header=0,dtype=const.leagueTypes,index_col=False)

os.makedirs(const.resultsInterDirName, exist_ok=True)
os.makedirs(const.resultsHockDirName, exist_ok=True)
os.makedirs(const.resultsLeagueDirName, exist_ok=True)

#distribution = stats.poisson
#data = yearDF['cupsFolded'].values
#params = distribution.fit(data)
#print(params)
#ks_stat, ks_p_value = stats.kstest(data,distribution.cdf,args=params)
#print(f'KS Stat: {ks_stat}')
#print(f'P-value: {ks_p_value}')

# aggregate Events
hockLeaguesDF = func.processSeasonsEvents(leagueHockDF,True,const.resultsHockDirName,postwarYears = [1946,1980])
hockTeamsDF = func.processTeamsEvents(teamsHockDF, 'ice hockey',True,const.resultsHockDirName)
hockDF = hockLeaguesDF.merge(hockTeamsDF,how='inner', left_on='periodName', right_on='periodName')

hockPrintDf = hockDF.copy()
hockPrintDf['created'] = 'created'
hockPrintDf['folded'] = 'folded'
hockPrintDf['suspended'] = 'suspended'
hockPrintDf['unsuspended'] = 'unsuspended'
hockPrintDf['comps'] = 'comps'
hockPrintDf['cups'] = 'cups'
hockPrintDf['leag'] = 'leagues'
hockPrintDf = hockPrintDf.loc[:, ['periodName', 'duration','comps','competitionsMin','competitions25%','competitionsMedian','competitions75%','competitionsMax', 'cups','cupsMin','cups25%','cupsMedian','cups75%','cupsMax','leag', 'leagMin','leag25%','leagMedian','leag75%','leagMax','created','competitionsCreatedProb','cupsCreatedProb', 'leaguesCreatedProb','folded','compsFoldedProb','cupsFoldedProb','leaguesFoldedProb','suspended','competitionsSuspendedProb','cupsSuspendedProb','leaguesSuspendedProb','unsuspended','competitionsUnSuspendedProb','cupsUnSuspendedProb','leaguesUnSuspendedProb', 'seasons','sport','teamsMin','teams25%','teamsMedian','teams75%','teamsMax','teamsCreatedProb','teamsFoldedProb']]
hockPrintDf.to_csv(os.path.join(const.resultsHockDirName,'all_sum.csv'),index=False)

rugLeagueLeaguesDF = func.processSeasonsEvents(leagueRugLeagueDF,True,const.resultsLeagueDirName)
rugLeagueTeamsDF = func.processTeamsEvents(teamsRugLeagueDF, 'rugby league',True,const.resultsLeagueDirName)
rugLeagueDF = rugLeagueLeaguesDF.merge(rugLeagueTeamsDF,how='inner', left_on='periodName', right_on='periodName')

rugLeaguePrintDf = rugLeagueDF.copy()
rugLeaguePrintDf['created'] = 'created'
rugLeaguePrintDf['folded'] = 'folded'
rugLeaguePrintDf['suspended'] = 'suspended'
rugLeaguePrintDf['unsuspended'] = 'unsuspended'
rugLeaguePrintDf['comps'] = 'comps'
rugLeaguePrintDf['cups'] = 'cups'
rugLeaguePrintDf['leag'] = 'leagues'
rugLeaguePrintDf = rugLeaguePrintDf.loc[:, ['periodName', 'duration','comps','competitionsMin','competitions25%','competitionsMedian','competitions75%','competitionsMax', 'cups','cupsMin','cups25%','cupsMedian','cups75%','cupsMax','leag', 'leagMin','leag25%','leagMedian','leag75%','leagMax','created','competitionsCreatedProb','cupsCreatedProb', 'leaguesCreatedProb','folded','compsFoldedProb','cupsFoldedProb','leaguesFoldedProb','suspended','competitionsSuspendedProb','cupsSuspendedProb','leaguesSuspendedProb','unsuspended','competitionsUnSuspendedProb','cupsUnSuspendedProb','leaguesUnSuspendedProb', 'seasons','sport','teamsMin','teams25%','teamsMedian','teams75%','teamsMax','teamsCreatedProb','teamsFoldedProb']]
rugLeaguePrintDf.to_csv(os.path.join(const.resultsLeagueDirName,'all_sum.csv'),index=False)

# summarise Teams
teamsDF = pd.concat([hockTeamsDF,rugLeagueTeamsDF])
teamsDF.to_csv(os.path.join(const.resultsInterDirName,'teams.csv'),index=False)

leaguesDF = pd.concat([hockLeaguesDF,rugLeagueLeaguesDF])
leaguesDF.to_csv(os.path.join(const.resultsInterDirName,'leagues_full.csv'),index=False)

leaguesDF = leaguesDF.drop(['competitions25%','competitionsMedian','competitions75%','cups25%','cupsMedian','cups75%','leag25%','leagMedian','leag75%'],axis=1)
leaguesDF.to_csv(os.path.join(const.resultsInterDirName,'leagues_slim.csv'),index=False)

# hockey = 0.5, ar = 0.5, gaa = 0.5, fut = 0.75, rl = 0.75, ru = 1.0
# hockey = 2/4, ar = 2/4, gaa = 2/4, fut = 3/4, rl = 3/4, ru = 4/4
teamsNamesHockDF = func.expandRange(teamsHockDF,'season_founded','season_last','season_range','season_year')
teamsNamesHockDF = teamsNamesHockDF.sort_values(['season_year','team_name'],ascending=[True,True])
teamsBaseHockDF = teamsNamesHockDF['team_base'].value_counts().reset_index()
teamsSuffHockDF = teamsNamesHockDF['team_suffix'].value_counts().reset_index()

teamsBaseHockDF['count'] = teamsBaseHockDF['count'] * 2
teamsSuffHockDF['count'] = teamsSuffHockDF['count'] * 2

teamsBaseHockDF.to_csv(os.path.join(const.resultsHockDirName,'teams_base.csv'),index=False)
teamsSuffHockDF.to_csv(os.path.join(const.resultsHockDirName,'teams_suffix.csv'),index=False)

teamsNamesRugLeagueDF = func.expandRange(teamsRugLeagueDF,'season_founded','season_last','season_range','season_year')
teamsNamesRugLeagueDF = teamsNamesRugLeagueDF.sort_values(['season_year','team_name'],ascending=[True,True])
teamsBaseRugLeagueDF = teamsNamesRugLeagueDF['team_base'].value_counts().reset_index()
teamsSuffRugLeagueDF = teamsNamesRugLeagueDF['team_suffix'].value_counts().reset_index()

teamsBaseRugLeagueDF['count'] = teamsBaseRugLeagueDF['count'] * 2
teamsSuffRugLeagueDF['count'] = teamsSuffRugLeagueDF['count'] * 2

teamsBaseRugLeagueDF.to_csv(os.path.join(const.resultsLeagueDirName,'teams_base.csv'),index=False)
teamsSuffRugLeagueDF.to_csv(os.path.join(const.resultsLeagueDirName,'teams_suffix.csv'),index=False)

teamsBaseDF = teamsBaseRugLeagueDF.merge(teamsBaseHockDF, how='outer', on='team_base',  suffixes=('_rl', '_hock')).fillna(0)
teamsBaseDF['count'] =  teamsBaseDF['count_rl'] + teamsBaseDF['count_hock']
teamsBaseDF['count'] =  (teamsBaseDF['count'] / 4).apply(np.ceil).astype(int)
teamsBaseDF = teamsBaseDF.drop(['count_rl','count_hock'],axis=1)
teamsBaseDF = teamsBaseDF.sort_values(['count','team_base'],ascending=[False,True])

teamsSuffDF = teamsSuffRugLeagueDF.merge(teamsSuffHockDF, how='outer', on='team_suffix',  suffixes=('_rl', '_hock')).fillna(0)
teamsSuffDF['count'] =  teamsSuffDF['count_rl'] + teamsSuffDF['count_hock']
teamsSuffDF['count'] =  (teamsSuffDF['count'] / 4).apply(np.ceil).astype(int)
teamsSuffDF = teamsSuffDF.drop(['count_rl','count_hock'],axis=1)
teamsSuffDF = teamsSuffDF.sort_values(['count','team_suffix'],ascending=[False,True])

teamsSuffDF.to_csv(os.path.join(const.resultsInterDirName,'teams_suffix.csv'),index=False)