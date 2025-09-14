import math
from tabnanny import verbose

import pandas as pd
import numpy as np
import regex as re
import glob
import os

from pandas import Int64Dtype

import leagueconst as const
import leaguefunc as func

from pathlib import Path


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

# Get first season for each competition and add as column
startSeasonDF = hockExpDF.groupby('competition_name').agg(firstSeason =('format_year','min')).reset_index()
startSeasonDi = dict(zip(startSeasonDF['competition_name'], startSeasonDF['firstSeason']))
hockExpDF['firstSeason'] = hockExpDF['competition_name'].map(startSeasonDi)

# Get last season for each competition and add as column
lastSeasonDF = hockExpDF.groupby('competition_name').agg(lastSeason =('format_year','max')).reset_index()
lastSeasonDi = dict(zip(lastSeasonDF['competition_name'], lastSeasonDF['lastSeason']))
hockExpDF['lastSeason'] = hockExpDF['competition_name'].map(lastSeasonDi)

# Filter if row season date equals first season date column
hockSSDF = hockExpDF[hockExpDF['firstSeason'] == hockExpDF['format_year']].drop_duplicates(subset=['format_year','competition_name'])
# Filter if row season date equals last season date column
hockLSDF = hockExpDF[hockExpDF['lastSeason'] == hockExpDF['format_year']].drop_duplicates(subset=['format_year','competition_name'])

# Count reported competitions by season
yearDF = func.countActiveCompetitions(hockExpDF)
# Count reported cup competitions by season
yearCupDF = func.countActiveCups(hockExpDF)
# Count reported cup competitions by season
yearLeagueDF = func.countActiveLeagues(hockExpDF)
# merge Counts
yearDF = yearDF.merge(yearCupDF, left_on='format_year', right_on='format_year').merge(yearLeagueDF, left_on='format_year', right_on='format_year')

# Add Change From Previous Year
yearDF['delta'] = 'delta'
yearDF = func.calcCompetitionDeltas(yearDF)

# Add In Creation Events
yearDF['created'] = 'created'
yearDF = func.countCompetitionCreations(yearDF,hockSSDF)

# Set Initial Delta to Creation Events
yearDF.loc[0:0,'competitionsDelta'] = yearDF.at[0, 'competitionsCreated']
yearDF.loc[0:0,'cupsDelta'] = yearDF.at[0, 'cupsCreated']
yearDF.loc[0:0,'leaguesDelta'] = yearDF.at[0, 'leaguesCreated']

# Add In Dissolution Events
yearDF['folded'] = 'folded'
yearDF = func.countCompetitionEnds(yearDF,hockLSDF)

# Add In Net Change Events
yearDF['netChange'] = 'netChange'
yearDF = func.calcCompetitionNetChanges(yearDF)

# Add In Net Suspension Events
yearDF['suspendedNet'] = 'suspensionsNet'
yearDF = func.calcCompetitionsNetSuspensions(yearDF)
# Add In Total Suspended
yearDF['suspendedTotal'] = 'suspendedTotal'
yearDF = func.calcCompetitionsSuspended(yearDF)
# Separate Suspensions from Unsuspensions
yearDF['unsuspensions'] = 'unsuspensions'
yearDF = func.calcCompetitionsUnsuspensions(yearDF)
# Separate Suspensions from Unsuspensions
yearDF['suspensions'] = 'suspensions'
yearDF = func.calcCompetitionsSuspensions(yearDF)

# Add Total From Previous Year
yearDF['previous'] = 'previous'
yearDF['competitionsPrv'] = yearDF['competitions'].shift(1).fillna(0).astype(int)
yearDF['cupsPrv'] = yearDF['cups'].shift(1).fillna(0).astype(int)
yearDF['leaguesPrv'] = yearDF['leagues'].shift(1).fillna(0).astype(int)

#yearDF['competitionsDissolvable'] = yearDF['competitions'] -  yearDF['competitionsCreated']
#yearDF['cupsDissolvable'] = yearDF['cups'] -  yearDF['cupsCreated']
#yearDF['leaguesDissolvable'] = yearDF['leagues'] -  yearDF['leaguesCreated']

teamsHockSumDF = func.teamsSummary(teamsHockExpDF,'ice_hockey')
teamsHockBaseDF = teamsHockExpDF['team_base'].value_counts().reset_index()
teamsHockSuffDF = teamsHockExpDF['team_suffix'].value_counts().reset_index()

hockSSDF[["format_year", "competition_name", "competition_type"]].to_csv(os.path.join(resultsInterDirName,'hockey_comp_start.csv'),index=False)

yearDF.to_csv(os.path.join(resultsInterDirName,'league_hockey.csv'),index=False)

foldedProbability = yearDF.drop(const.removalList,axis=1).agg(['sum'])
foldedProbability['duration'] = yearDF['format_year'].max() - yearDF['format_year'].min() + 1 - len(yearDF[yearDF['competitionsPrv'] == 0])

foldedProbability['compsFoldedAvg'] = foldedProbability['competitionsFolded'] / foldedProbability['duration']
foldedProbability['cupsFoldedAvg'] =  foldedProbability['cupsFolded'] / foldedProbability['duration']
foldedProbability['leaguesFoldedAvg'] = foldedProbability['leaguesFolded'] / foldedProbability['duration']

yearDF['compsFoldedDev'] = (yearDF['competitionsFolded'] - foldedProbability['compsFoldedAvg'].iloc[0]).pow(2)
yearDF['cupsFoldedDev'] = (yearDF['cupsFolded'] - foldedProbability['cupsFoldedAvg'].iloc[0]).pow(2)
yearDF['leaguesFoldedDev'] = (yearDF['leaguesFolded'] - foldedProbability['leaguesFoldedAvg'].iloc[0]).pow(2)

foldedProbability['compsFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['compsFoldedDev'].sum() / foldedProbability['duration'])
foldedProbability['cupsFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['cupsFoldedDev'].sum() / foldedProbability['duration'])
foldedProbability['leaguesFoldedSTD'] = np.sqrt(yearDF[yearDF['competitionsPrv'] > 0]['leaguesFoldedDev'].sum() / foldedProbability['duration'])

#foldedProbability['compsFoldedAvgFOT'] = (foldedProbability['compsFoldedAvgOAT'] / foldedProbability['duration'])
#foldedProbability['cupsFoldedAvgFOT'] =  (foldedProbability['cupsFoldedAvgOAT'] / foldedProbability['duration'])
#foldedProbability['leaguesFoldedAvgFOT'] = (foldedProbability['leaguesFoldedAvgOAT'] / foldedProbability['duration'])

#foldedProbability['compsFoldedProb'] = 1 - math.pow(math.e,- foldedProbability['compsFoldedAvgFOT'] * 1)
#foldedProbability['cupsFoldedProb'] =  1 - math.pow(math.e,- foldedProbability['cupsFoldedAvgFOT'] * 1)
#foldedProbability['leaguesFoldedProb'] =   1 - math.pow(math.e,- foldedProbability['leaguesFoldedAvgFOT'] * 1)

foldedProbability.to_csv(os.path.join(resultsInterDirName,'league_hockey_sum.csv'),index=False)


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