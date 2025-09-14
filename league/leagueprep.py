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


# Relative to This File
rootDirName = os.path.dirname(__file__)
resultsInterDirName = os.path.join(rootDirName, Path('../results_intermediate'))
resultsDirName = os.path.join(rootDirName, Path('../results_league'))

dirLeagueName = os.path.join(rootDirName, Path('../data/data/league/'))
dataFootballLeagueName = os.path.join(dirLeagueName, 'football-leagues.csv')

dataHockLeagueName = os.path.join(dirLeagueName, 'comp-hockey.csv')
dataTeamsHockName = os.path.join(dirLeagueName, 'teams-hockey.csv')

# File Read
print('Load League Data From Path: ' + dirLeagueName)
#footData = pd.read_csv(dataFootballLeagueName,header=0,dtype=footieTypes,index_col=False)
hockDF = pd.read_csv(dataHockLeagueName,header=0,dtype=const.leagueTypes,index_col=False)
teamsHockDF = pd.read_csv(dataTeamsHockName,header=0,dtype=const.teamTypes,index_col=False)

os.makedirs(resultsInterDirName, exist_ok=True)
os.makedirs(resultsDirName, exist_ok=True)

# standardisation
#footData['victory'] = footData['victory'].fillna(0)
#footData['draw'] = footData['draw'].fillna(0)
#footData['loss'] = footData['loss'].fillna(0)
#footData['points_tiebreaker'] = footData['points_tiebreaker'].fillna('none')
#footData['promotion_system'] = footData['promotion_system'].fillna('none')
#footData['relegation_system'] = footData['relegation_system'].fillna('none')

# group data

# expand
#footExpandedData = func.expandRange(footData,'format_start','format_end','format_range','format_year')
#footExpandedData = footExpandedData.sort_values(['format_year','level'],ascending=[True,True])
hockExpDF = func.expandRange(hockDF,'format_start','format_end','format_range','format_year')
hockExpDF = hockExpDF.sort_values(['format_year','competition_tier'],ascending=[True,True])

teamsHockExpDF = func.expandRange(teamsHockDF,'season_founded','season_last','season_range','season_year')
teamsHockExpDF = teamsHockExpDF.sort_values(['season_year','team_name'],ascending=[True,True])

# aggregate
yearDF = func.aggregateSeasonEvents(hockExpDF)
yearDF.to_csv(os.path.join(resultsInterDirName,'league_hockey.csv'),index=False)

#distribution = stats.poisson
#data = yearDF['cupsFolded'].values
#params = distribution.fit(data)
#print(params)
#ks_stat, ks_p_value = stats.kstest(data,distribution.cdf,args=params)
#print(f'KS Stat: {ks_stat}')
#print(f'P-value: {ks_p_value}')

# summarise League Events
foldedProbability = yearDF.drop(const.removalForProbs,axis=1).agg(['sum'])
foldedProbability['duration'] = yearDF['format_year'].max() - yearDF['format_year'].min() + 1 - len(yearDF[yearDF['competitionsPrv'] == 0])

foldedProbability['compsFoldedProb'] = (foldedProbability['competitionsFolded'] / foldedProbability['competitionsPrv']).round(2)
foldedProbability['cupsFoldedProb'] =  (foldedProbability['cupsFolded'] / foldedProbability['cupsPrv']).round(2)
foldedProbability['leaguesFoldedProb'] = (foldedProbability['leaguesFolded'] / foldedProbability['leaguesPrv']).round(2)

foldedProbability['competitionsSuspendedProb'] = (foldedProbability['competitionsSuspended'] / foldedProbability['competitionsPrv']).round(2)
foldedProbability['cupsSuspendedProb'] =  (foldedProbability['cupsSuspended'] / foldedProbability['cupsPrv']).round(2)
foldedProbability['leaguesSuspendedProb'] = (foldedProbability['leaguesSuspended'] / foldedProbability['leaguesPrv']).round(2)

foldedProbability['minComps'] = yearDF[yearDF['competitions'] > 0]['competitions'].min()
foldedProbability['minCups'] = yearDF[yearDF['competitions'] > 0]['cups'].min()
foldedProbability['minLeagues'] = yearDF[yearDF['competitions'] > 0]['leagues'].min()

foldedProbability['maxComps'] = yearDF['competitions'].max()
foldedProbability['maxCups'] = yearDF['cups'].max()
foldedProbability['maxLeagues'] = yearDF['leagues'].max()

 #foldedProbability['compsFoldedAvg'] = foldedProbability['competitionsFolded'] / foldedProbability['duration']
#foldedProbability['cupsFoldedAvg'] =  foldedProbability['cupsFolded'] / foldedProbability['duration']
#foldedProbability['leaguesFoldedAvg'] = foldedProbability['leaguesFolded'] / foldedProbability['duration']

#yearDF['compsFoldedDev'] = (yearDF['competitionsFolded'] - foldedProbability['compsFoldedAvg'].iloc[0]).pow(2)
#yearDF['cupsFoldedDev'] = (yearDF['cupsFolded'] - foldedProbability['cupsFoldedAvg'].iloc[0]).pow(2)
#yearDF['leaguesFoldedDev'] = (yearDF['leaguesFolded'] - foldedProbability['leaguesFoldedAvg'].iloc[0]).pow(2)

#foldedProbability['compsFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['compsFoldedDev'].sum() / foldedProbability['duration'])
#foldedProbability['cupsFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['cupsFoldedDev'].sum() / foldedProbability['duration'])
#foldedProbability['leaguesFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['leaguesFoldedDev'].sum() / foldedProbability['duration'])

#foldedProbability['compsFoldedAvgFOT'] = (foldedProbability['compsFoldedAvgOAT'] / foldedProbability['duration'])
#foldedProbability['cupsFoldedAvgFOT'] =  (foldedProbability['cupsFoldedAvgOAT'] / foldedProbability['duration'])
#foldedProbability['leaguesFoldedAvgFOT'] = (foldedProbability['leaguesFoldedAvgOAT'] / foldedProbability['duration'])

#foldedProbability['compsFoldedProb'] = 1 - math.pow(math.e,- foldedProbability['compsFoldedAvgFOT'] * 1)
#foldedProbability['cupsFoldedProb'] =  1 - math.pow(math.e,- foldedProbability['cupsFoldedAvgFOT'] * 1)
#foldedProbability['leaguesFoldedProb'] =   1 - math.pow(math.e,- foldedProbability['leaguesFoldedAvgFOT'] * 1)

foldedProbability.to_csv(os.path.join(resultsInterDirName,'league_hockey_sum.csv'),index=False)

# summarise Teams
teamsHockSumDF = func.teamsSummary(teamsHockExpDF,'ice_hockey')
teamsHockBaseDF = teamsHockExpDF['team_base'].value_counts().reset_index()
teamsHockSuffDF = teamsHockExpDF['team_suffix'].value_counts().reset_index()

teamsHockSumDF.to_csv(os.path.join(resultsInterDirName,'teams_hockey_sum.csv'),index=False)
teamsHockBaseDF.to_csv(os.path.join(resultsInterDirName,'teams_hockey_base.csv'),index=False)
teamsHockSuffDF.to_csv(os.path.join(resultsInterDirName,'teams_hockey_suffix.csv'),index=False)
#
#
#
#for name, group in orgFootData:
#    fileName = '{filePrefix}_{grouping}_{name}.csv'.format(filePrefix='eng',grouping='foot',name=name)
#    dirName = os.path.join(resultsInterDirName,'{grouping}_{name}'.format(grouping='foot',name=name))
#    os.makedirs(dirName, exist_ok=True)
#
#    print('Writing {name}'.format(name=fileName))
#    group.to_csv(os.path.join(dirName,fileName), index=False)