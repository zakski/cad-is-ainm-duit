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
hockDF = pd.read_csv(const.dataHockLeagueName,header=0,dtype=const.leagueTypes,index_col=False)
teamsHockDF = pd.read_csv(const.dataTeamsHockName,header=0,dtype=const.teamTypes,index_col=False)

os.makedirs(const.resultsInterDirName, exist_ok=True)
os.makedirs(const.resultsDirName, exist_ok=True)

# standardisation
#footData['victory'] = footData['victory'].fillna(0)
#footData['draw'] = footData['draw'].fillna(0)
#footData['loss'] = footData['loss'].fillna(0)
#footData['points_tiebreaker'] = footData['points_tiebreaker'].fillna('none')
#footData['promotion_system'] = footData['promotion_system'].fillna('none')
#footData['relegation_system'] = footData['relegation_system'].fillna('none')

# group data

# expand
hockExpDF = func.expandRange(hockDF,'format_start','format_end','format_range','format_year')
hockExpDF = hockExpDF.sort_values(['format_year','competition_tier'],ascending=[True,True])
hockExpDF.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_expanded.csv'),index=False)

teamsHockExpDF = func.expandRange(teamsHockDF,'season_founded','season_last','season_range','season_year')
teamsHockExpDF = teamsHockExpDF.sort_values(['season_year','team_name'],ascending=[True,True])

# aggregate
seasonsHockDF = func.aggregateSeasonsEvents(hockExpDF)
seasonsHockDF.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_aggregate.csv'),index=False)

belleEpHockDf = seasonsHockDF[seasonsHockDF['format_year'] < 1914]
interwarHockDf = seasonsHockDF[seasonsHockDF['format_year'] < 1940][seasonsHockDF['format_year'] > 1918]
postwarHockDf = seasonsHockDF[seasonsHockDF['format_year'] < 1980][seasonsHockDF['format_year'] > 1945]
glasnostHockDf = seasonsHockDF[seasonsHockDF['format_year'] < 1990][seasonsHockDF['format_year'] > 1979]
modernHockDf = seasonsHockDF[seasonsHockDF['format_year'] > 1989]
belleEpHockDf.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_agg_belleEp.csv'),index=False)
interwarHockDf.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_agg_interwar.csv'),index=False)
postwarHockDf.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_agg_postwar.csv'),index=False)
glasnostHockDf.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_agg_glasnost.csv'),index=False)
modernHockDf.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_agg_modern.csv'),index=False)

#distribution = stats.poisson
#data = yearDF['cupsFolded'].values
#params = distribution.fit(data)
#print(params)
#ks_stat, ks_p_value = stats.kstest(data,distribution.cdf,args=params)
#print(f'KS Stat: {ks_stat}')
#print(f'P-value: {ks_p_value}')

# summarise League Events
foldedProbability = func.summariseSeasonsEvents(seasonsHockDF)
foldedProbability.to_csv(os.path.join(const.resultsInterDirName,'league_hockey_sum.csv'),index=False)

# summarise Teams
teamsHockSumDF = func.teamsSummary(teamsHockExpDF,'ice_hockey')
teamsHockBaseDF = teamsHockExpDF['team_base'].value_counts().reset_index()
teamsHockSuffDF = teamsHockExpDF['team_suffix'].value_counts().reset_index()

teamsHockSumDF.to_csv(os.path.join(const.resultsInterDirName,'teams_hockey_sum.csv'),index=False)
teamsHockBaseDF.to_csv(os.path.join(const.resultsInterDirName,'teams_hockey_base.csv'),index=False)
teamsHockSuffDF.to_csv(os.path.join(const.resultsInterDirName,'teams_hockey_suffix.csv'),index=False)
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