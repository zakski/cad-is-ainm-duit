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

# File Read
print('Load League Data From Path: ' + dirLeagueName)
#footData = pd.read_csv(dataFootballLeagueName,header=0,dtype=footieTypes,index_col=False)
hockDF = pd.read_csv(dataHockLeagueName,header=0,dtype=const.leagueTypes,index_col=False)

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
compCreationDi = dict(zip(compCreationDF['format_year'], compCreationDF['count']))

# Count these dissolution by season
compDissolutionDF = hockLSDF['format_year'].value_counts().reset_index()
compDissolutionDF['format_year'] = compDissolutionDF['format_year']+1
compDissolutionDi = dict(zip(compDissolutionDF['format_year'], compDissolutionDF['count']))

# Count reported competitions by season
yearDF = hockExpDF.drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(competitions =('competition_name','count')).reset_index()
yearDF.index = yearDF['format_year']
yearDF = yearDF.reindex(np.arange(yearDF['format_year'].min(), yearDF['format_year'].max() + 1)).fillna(0)
yearDF['competitions'] = yearDF['competitions'].astype(int)
yearDF = yearDF.drop(['format_year'],axis=1).reset_index()

# Add In Creation Events
yearDF['competitionsCreated'] = yearDF['format_year'].map(compCreationDi)
yearDF['competitionsCreated'] = yearDF['competitionsCreated'].fillna(0).astype(int)
yearDF['competitionsFolded'] = yearDF['format_year'].map(compDissolutionDi)
yearDF['competitionsFolded'] = yearDF['competitionsFolded'].fillna(0).astype(int)

hockSSDF[["format_year", "competition_name", "competition_type"]].to_csv(os.path.join(resultsInterDirName,'hockey_comp_start.csv'),index=False)
yearDF.to_csv(os.path.join(resultsInterDirName,'hockey_expanded.csv'),index=False)
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