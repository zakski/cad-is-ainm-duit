from tabnanny import verbose

import pandas as pd
import numpy as np
import regex as re
import glob
import os

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

# Stat out likelyhood of league creation

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

# Count these creations by season
compCreationDF = hockSSDF['format_year'].value_counts().reset_index()
cupCreationDF = hockSSDF[hockSSDF['competition_type'] == 'cup']['format_year'].value_counts().reset_index()
leagueCreationDF = hockSSDF[hockSSDF['competition_type'] == 'league']['format_year'].value_counts().reset_index()
compCreationDi = dict(zip(compCreationDF['format_year'], compCreationDF['count']))
cupCreationDi = dict(zip(cupCreationDF['format_year'], cupCreationDF['count']))
leagueCreationDi = dict(zip(leagueCreationDF['format_year'], leagueCreationDF['count']))

# Count these dissolution by season
compDissolutionDF = hockLSDF['format_year'].value_counts().reset_index()
cupDissolutionDF = hockLSDF[hockLSDF['competition_type'] == 'cup']['format_year'].value_counts().reset_index()
leagueDissolutionDF = hockLSDF[hockLSDF['competition_type'] == 'league']['format_year'].value_counts().reset_index()
compDissolutionDF['format_year'] = compDissolutionDF['format_year']+1
cupDissolutionDF['format_year'] = cupDissolutionDF['format_year']+1
leagueDissolutionDF['format_year'] = leagueDissolutionDF['format_year']+1
compDissolutionDi = dict(zip(compDissolutionDF['format_year'], compDissolutionDF['count']))
cupDissolutionDi = dict(zip(cupDissolutionDF['format_year'], cupDissolutionDF['count']))
leagueDissolutionDi = dict(zip(leagueDissolutionDF['format_year'], leagueDissolutionDF['count']))

# Count reported competitions by season
yearDF = hockExpDF.drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(competitions =('competition_name','count')).reset_index()
yearDF.index = yearDF['format_year']
yearDF = yearDF.reindex(np.arange(yearDF['format_year'].min(), yearDF['format_year'].max() + 1)).fillna(0)
yearDF['competitions'] = yearDF['competitions'].astype(int)
yearDF = yearDF.drop(['format_year'],axis=1).reset_index()

# Count reported cup competitions by season
yearCupDF = hockExpDF[hockExpDF['competition_type'] == 'cup'].drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(cups =('competition_name','count')).reset_index()
yearCupDF.index = yearCupDF['format_year']
yearCupDF = yearCupDF.reindex(np.arange(yearCupDF['format_year'].min(), yearCupDF['format_year'].max() + 1)).fillna(0)
yearCupDF['cups'] = yearCupDF['cups'].astype(int)
yearCupDF = yearCupDF.drop(['format_year'],axis=1).reset_index()

# Count reported cup competitions by season
yearLeagueDF = hockExpDF[hockExpDF['competition_type'] == 'league'].drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(leagues=('competition_name','count')).reset_index()
yearLeagueDF.index = yearLeagueDF['format_year']
yearLeagueDF = yearLeagueDF.reindex(np.arange(yearLeagueDF['format_year'].min(), yearLeagueDF['format_year'].max() + 1)).fillna(0)
yearLeagueDF['leagues'] = yearLeagueDF['leagues'].astype(int)
yearLeagueDF = yearLeagueDF.drop(['format_year'],axis=1).reset_index()

yearDF = yearDF.merge(yearCupDF, left_on='format_year', right_on='format_year').merge(yearLeagueDF, left_on='format_year', right_on='format_year')

# Add In Creation Events
yearDF['competitionsCreated'] = yearDF['format_year'].map(compCreationDi)
yearDF['competitionsCreated'] = yearDF['competitionsCreated'].fillna(0).astype(int)
yearDF['cupsCreated'] = yearDF['format_year'].map(cupCreationDi)
yearDF['cupsCreated'] = yearDF['cupsCreated'].fillna(0).astype(int)
yearDF['leaguesCreated'] = yearDF['format_year'].map(leagueCreationDi)
yearDF['leaguesCreated'] = yearDF['leaguesCreated'].fillna(0).astype(int)
# Add In Dissolution Events
yearDF['competitionsFolded'] = yearDF['format_year'].map(compDissolutionDi)
yearDF['competitionsFolded'] = yearDF['competitionsFolded'].fillna(0).astype(int)
yearDF['cupsFolded'] = yearDF['format_year'].map(cupDissolutionDi)
yearDF['cupsFolded'] = yearDF['cupsFolded'].fillna(0).astype(int)
yearDF['leaguesFolded'] = yearDF['format_year'].map(leagueDissolutionDi)
yearDF['leaguesFolded'] = yearDF['leaguesFolded'].fillna(0).astype(int)

#yearDF['competitionsDissolvable'] = yearDF['competitions'] -  yearDF['competitionsCreated']
#yearDF['cupsDissolvable'] = yearDF['cups'] -  yearDF['cupsCreated']
#yearDF['leaguesDissolvable'] = yearDF['leagues'] -  yearDF['leaguesCreated']

teamsHockSumDF = func.teamsSummary(teamsHockExpDF,'ice_hockey')
teamsHockBaseDF = teamsHockExpDF['team_base'].value_counts().reset_index()
teamsHockSuffDF = teamsHockExpDF['team_suffix'].value_counts().reset_index()

hockSSDF[["format_year", "competition_name", "competition_type"]].to_csv(os.path.join(resultsInterDirName,'hockey_comp_start.csv'),index=False)
yearDF.to_csv(os.path.join(resultsInterDirName,'hockey_expanded.csv'),index=False)

teamsHockExpDF.to_csv(os.path.join(resultsInterDirName,'teams-hockey-exp.csv'),index=False)

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