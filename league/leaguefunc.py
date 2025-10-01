import pandas as pd
import numpy as np

import os

import leagueconst as const

def expandRange(data, minimumCol, maximumCol, rangeCol, col):

    # Add a len column for the size of our range. We're also adding an original_index column we'll need later.
    data = data.assign(range_col = data[maximumCol]- data[minimumCol]+1, original_index=data.index).rename({"range_col": rangeCol}, axis=1)

    # Create a new dataframe by repeating the values from the original rangeCol times. So the rows from the
    # first range will be repeated 100 times, the second range will be repeated 10 times, etc.
    new_data = pd.DataFrame(np.repeat(data.values, data[rangeCol], axis=0))
    new_data.columns = data.columns
    new_data = new_data.astype(data.dtypes)


    # At this point, we've expanded our ranges, but we don't have a
    # column that represents the number that the range has been expanded into.

    # To get that, we're going to use the SICs_min column, plus a counter that resets
    # every time we get to a new SIC range.

    # The counter can be made by grouping by the original SICs range and then doing
    # a cumulative sum of a column of just ones.
    cumsum = new_data.assign(ones=np.ones_like(new_data.index)).groupby('original_index').ones.cumsum()

    # This looks like 1-100, followed by 1-10, etc. We need it to be 0-99, 0-9 etc. so we subtract one
    # before we add it to the SICs_min to get the actual SIC number.
    finalData = new_data.assign(actual_col=new_data[minimumCol] + cumsum - 1).rename({"actual_col": col}, axis=1)
    return finalData.drop(['original_index',rangeCol],axis=1)

def countCompetitionCreations(seasonsDF, competitionsStartsDF):
    # Count creations by season
    compCreationDF = competitionsStartsDF['format_year'].value_counts().reset_index()
    cupCreationDF = competitionsStartsDF[competitionsStartsDF['competition_type'] == 'cup']['format_year'].value_counts().reset_index()
    leagueCreationDF = competitionsStartsDF[competitionsStartsDF['competition_type'] == 'league']['format_year'].value_counts().reset_index()
    compCreationDi = dict(zip(compCreationDF['format_year'], compCreationDF['count']))
    cupCreationDi = dict(zip(cupCreationDF['format_year'], cupCreationDF['count']))
    leagueCreationDi = dict(zip(leagueCreationDF['format_year'], leagueCreationDF['count']))

    # Add In Creation Events
    seasonsDF['competitionsCreated'] = seasonsDF['format_year'].map(compCreationDi)
    seasonsDF['competitionsCreated'] = seasonsDF['competitionsCreated'].fillna(0).astype(int)
    seasonsDF['cupsCreated'] = seasonsDF['format_year'].map(cupCreationDi)
    seasonsDF['cupsCreated'] = seasonsDF['cupsCreated'].fillna(0).astype(int)
    seasonsDF['leaguesCreated'] = seasonsDF['format_year'].map(leagueCreationDi)
    seasonsDF['leaguesCreated'] = seasonsDF['leaguesCreated'].fillna(0).astype(int)

    return seasonsDF

def countTeamsCreations(seasonsDF, teamsStartsDF):
    # Count creations by season
    teamsCreationDF = teamsStartsDF['season_year'].value_counts().reset_index()
    teamsCreationDi = dict(zip(teamsCreationDF['season_year'], teamsCreationDF['count']))

    # Add In Creation Events
    seasonsDF['teamsCreated'] = seasonsDF['season_year'].map(teamsCreationDi)
    seasonsDF['teamsCreated'] = seasonsDF['teamsCreated'].fillna(0).astype(int)

    return seasonsDF


def countCompetitionEnds(seasonsDF, competitionsEndsDF):
    # Count these dissolution by season
    compDissolutionDF = competitionsEndsDF['format_year'].value_counts().reset_index()
    cupDissolutionDF = competitionsEndsDF[competitionsEndsDF['competition_type'] == 'cup']['format_year'].value_counts().reset_index()
    leagueDissolutionDF = competitionsEndsDF[competitionsEndsDF['competition_type'] == 'league']['format_year'].value_counts().reset_index()
    compDissolutionDF['format_year'] = compDissolutionDF['format_year']+1
    cupDissolutionDF['format_year'] = cupDissolutionDF['format_year']+1
    leagueDissolutionDF['format_year'] = leagueDissolutionDF['format_year']+1
    compDissolutionDi = dict(zip(compDissolutionDF['format_year'], compDissolutionDF['count']))
    cupDissolutionDi = dict(zip(cupDissolutionDF['format_year'], cupDissolutionDF['count']))
    leagueDissolutionDi = dict(zip(leagueDissolutionDF['format_year'], leagueDissolutionDF['count']))

    # Add In Dissolution Events
    seasonsDF['competitionsFolded'] = seasonsDF['format_year'].map(compDissolutionDi)
    seasonsDF['competitionsFolded'] = seasonsDF['competitionsFolded'].fillna(0).astype(int)
    seasonsDF['cupsFolded'] = seasonsDF['format_year'].map(cupDissolutionDi)
    seasonsDF['cupsFolded'] = seasonsDF['cupsFolded'].fillna(0).astype(int)
    seasonsDF['leaguesFolded'] = seasonsDF['format_year'].map(leagueDissolutionDi)
    seasonsDF['leaguesFolded'] = seasonsDF['leaguesFolded'].fillna(0).astype(int)

    return seasonsDF

def countTeamsEnds(seasonsDF, competitionsEndsDF):
    # Count these dissolution by season
    teamDissolutionDF = competitionsEndsDF['season_year'].value_counts().reset_index()
    teamDissolutionDF['season_year'] = teamDissolutionDF['season_year']+1
    teamDissolutionDi = dict(zip(teamDissolutionDF['season_year'], teamDissolutionDF['count']))

    # Add In Dissolution Events
    seasonsDF['teamsFolded'] = seasonsDF['season_year'].map(teamDissolutionDi)
    seasonsDF['teamsFolded'] = seasonsDF['teamsFolded'].fillna(0).astype(int)

    return seasonsDF

def countActiveCompetitions(expandedDF):
    seasonsDF = expandedDF.drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(competitions =('competition_name','count')).reset_index()
    seasonsDF.index = seasonsDF['format_year']
    seasonsDF = seasonsDF.reindex(np.arange(seasonsDF['format_year'].min(), seasonsDF['format_year'].max() + 1)).fillna(0)
    seasonsDF['competitions'] = seasonsDF['competitions'].astype(int)
    seasonsDF = seasonsDF.drop(['format_year'],axis=1).reset_index()

    return seasonsDF

def countActiveCups(expandedDF):
    seasonsDF = expandedDF[expandedDF['competition_type'] == 'cup'].drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(cups =('competition_name','count')).reset_index()
    seasonsDF.index = seasonsDF['format_year']
    seasonsDF = seasonsDF.reindex(np.arange(seasonsDF['format_year'].min(), seasonsDF['format_year'].max() + 1)).fillna(0)
    seasonsDF['cups'] = seasonsDF['cups'].astype(int)
    seasonsDF = seasonsDF.drop(['format_year'],axis=1).reset_index()

    return seasonsDF

def countActiveLeagues(expandedDF):
    seasonsDF = expandedDF[expandedDF['competition_type'] == 'league'].drop_duplicates(subset=['format_year','competition_name']).groupby('format_year').agg(leagues=('competition_name','count')).reset_index()
    seasonsDF.index = seasonsDF['format_year']
    seasonsDF = seasonsDF.reindex(np.arange(seasonsDF['format_year'].min(), seasonsDF['format_year'].max() + 1)).fillna(0)
    seasonsDF['leagues'] = seasonsDF['leagues'].astype(int)
    seasonsDF = seasonsDF.drop(['format_year'],axis=1).reset_index()

    return seasonsDF

def countActiveDivisions(expandedDF):
    divisionsDF = expandedDF[expandedDF['competition_type'] == 'league'].groupby(['format_year','competition_name']).agg(divisions=('competition_name','count'),leagueClubs=('clubs','sum'),maxTier=('competition_tier','min'),minTier=('competition_tier','max'),minDivisionClubs=('clubs','min'),maxDivisionClubs=('clubs','max')).reset_index()
    maxDivisions = divisionsDF['divisions'].max()

    divisionsGroupedDF = divisionsDF.groupby(['competition_name'])
    divisionsDF = pd.DataFrame()

    for group_name, divisionsDF_group in divisionsGroupedDF:
        divisionsDF_group['divisionsPrv'] = divisionsDF_group['divisions'].shift(1).fillna(0).astype(int)
        divisionsDF_group['divisionsRem'] = divisionsDF_group['divisionsPrv']-1
        divisionsDF_group.loc[divisionsDF_group['divisionsRem']<0,'divisionsRem']=0
        divisionsDF_group['divisionsEmpt'] = maxDivisions - divisionsDF_group['divisions']
        divisionsDF_group['divisionsCreated'] = divisionsDF_group['divisions'] - divisionsDF_group['divisionsPrv']
        divisionsDF_group.loc[divisionsDF_group['divisionsCreated']<0,'divisionsCreated']=0
        divisionsDF_group['divisionsFolded'] = divisionsDF_group['divisionsPrv'] - divisionsDF_group['divisions']
        divisionsDF_group.loc[divisionsDF_group['divisionsFolded']<0,'divisionsFolded']=0
        divisionsDF_group.iloc[0, divisionsDF_group.columns.get_loc('divisionsCreated')] = 0
        divisionsDF = pd.concat([divisionsDF,divisionsDF_group])

    divisionsDF = divisionsDF.groupby('format_year').agg(divisions=('divisions','sum'),minDivisions=('divisions','min'),maxDivisions=('divisions','max'),minTier=('minTier','max'),maxTier=('maxTier','min'),divisionsCreated=('divisionsCreated','sum'),divisionsFolded=('divisionsFolded','sum'),divisionsRem=('divisionsRem','sum'),divisionsEmpt=('divisionsEmpt','sum'),leagueClubs=('leagueClubs','sum'),minDivisionClubs=('minDivisionClubs','min'),maxDivisionClubs=('maxDivisionClubs','max')).reset_index()
    divisionsDF.index = divisionsDF['format_year']
    divisionsDF = divisionsDF.reindex(np.arange(divisionsDF['format_year'].min(), divisionsDF['format_year'].max() + 1)).fillna(0)
    divisionsDF['divisions'] = divisionsDF['divisions'].astype(int)
    divisionsDF['minDivisions'] = divisionsDF['minDivisions'].astype(int)
    divisionsDF['maxDivisions'] = divisionsDF['maxDivisions'].astype(int)
    divisionsDF['divisionsCreated'] = divisionsDF['divisionsCreated'].astype(int)
    divisionsDF['divisionsFolded'] = divisionsDF['divisionsFolded'].astype(int)
    divisionsDF['divisionsRem'] = divisionsDF['divisionsRem'].astype(int)
    divisionsDF['divisionsEmpt'] = divisionsDF['divisionsEmpt'].astype(int)
    divisionsDF = divisionsDF.drop(['format_year'],axis=1).reset_index()

    return divisionsDF

def countActiveTeams(expandedDF):
    seasonsDF = expandedDF.drop_duplicates(subset=['season_year','team_name']).groupby('season_year').agg(teams =('team_name','count')).reset_index()
    seasonsDF.index = seasonsDF['season_year']
    seasonsDF = seasonsDF.reindex(np.arange(seasonsDF['season_year'].min(), seasonsDF['season_year'].max() + 1)).fillna(0)
    seasonsDF['teams'] = seasonsDF['teams'].astype(int)
    seasonsDF = seasonsDF.drop(['season_year'],axis=1).reset_index()

    return seasonsDF

def calcCompetitionDeltas(seasonsDF):
    seasonsDF['competitionsDelta'] = seasonsDF['competitions'].diff().fillna(0).astype(int)
    seasonsDF['cupsDelta'] = seasonsDF['cups'].diff().fillna(0).astype(int)
    seasonsDF['leaguesDelta'] = seasonsDF['leagues'].diff().fillna(0).astype(int)

    return seasonsDF

def calcTeamsDeltas(seasonsDF):
    seasonsDF['teamsDelta'] = seasonsDF['teams'].diff().fillna(0).astype(int)

    return seasonsDF

def calcCompetitionNetChanges(seasonsDF):
    seasonsDF['competitionsNetChange'] = seasonsDF['competitionsCreated']  - seasonsDF['competitionsFolded']
    seasonsDF['cupsNetChange'] = seasonsDF['cupsCreated']  - seasonsDF['cupsFolded']
    seasonsDF['leaguesNetChange'] = seasonsDF['leaguesCreated']  - seasonsDF['leaguesFolded']

    return seasonsDF

def calcTeamNetChanges(seasonsDF):
    seasonsDF['teamsNetChange'] = seasonsDF['teamsCreated']  - seasonsDF['teamsFolded']

    return seasonsDF

def calcCompetitionsNetSuspensions(seasonsDF):
    seasonsDF['competitionsNetSuspended'] = seasonsDF['competitionsNetChange']  - seasonsDF['competitionsDelta']
    seasonsDF['cupsNetSuspended'] = seasonsDF['cupsNetChange']  - seasonsDF['cupsDelta']
    seasonsDF['leaguesNetSuspended'] = seasonsDF['leaguesNetChange']  - seasonsDF['leaguesDelta']

    return seasonsDF

def calcCompetitionsSuspended(seasonsDF):
    seasonsDF['competitionsSuspendedTotal'] = seasonsDF['competitionsNetSuspended'].cumsum()
    seasonsDF['cupsSuspendedTotal'] = seasonsDF['cupsNetSuspended'].cumsum()
    seasonsDF['leaguesSuspendedTotal'] = seasonsDF['leaguesNetSuspended'].cumsum()

    return seasonsDF

def calcCompetitionsUnsuspensions(seasonsDF):
    seasonsDF['competitionsUnsuspended'] = seasonsDF['competitionsNetSuspended'].mask(seasonsDF['competitionsNetSuspended'] > 0,0).abs()
    seasonsDF['cupsUnsuspended'] = seasonsDF['cupsNetSuspended'].mask(seasonsDF['cupsNetSuspended'] > 0,0).abs()
    seasonsDF['leaguesUnsuspended'] = seasonsDF['leaguesNetSuspended'].mask(seasonsDF['leaguesNetSuspended'] > 0,0).abs()

    return seasonsDF

def calcCompetitionsSuspensions(seasonsDF):
    seasonsDF['competitionsSuspended'] = seasonsDF['competitionsNetSuspended'].mask(seasonsDF['competitionsNetSuspended'] < 0,0)
    seasonsDF['cupsSuspended'] = seasonsDF['cupsNetSuspended'].mask(seasonsDF['cupsNetSuspended'] < 0,0).abs()
    seasonsDF['leaguesSuspended'] = seasonsDF['leaguesNetSuspended'].mask(seasonsDF['leaguesNetSuspended'] < 0,0)

    return seasonsDF

def aggregateSeasonsEvents(expandedDF):
    # Get first season for each competition and add as column
    startSeasonDF = expandedDF.groupby('competition_name').agg(firstSeason =('format_year','min')).reset_index()
    startSeasonDi = dict(zip(startSeasonDF['competition_name'], startSeasonDF['firstSeason']))
    expandedDF['firstSeason'] = expandedDF['competition_name'].map(startSeasonDi)

    # Get last season for each competition and add as column
    lastSeasonDF = expandedDF.groupby('competition_name').agg(lastSeason =('format_year','max')).reset_index()
    lastSeasonDi = dict(zip(lastSeasonDF['competition_name'], lastSeasonDF['lastSeason']))
    expandedDF['lastSeason'] = expandedDF['competition_name'].map(lastSeasonDi)

    # Filter if row season date equals first season date column
    competitionStartDF = expandedDF[expandedDF['firstSeason'] == expandedDF['format_year']].drop_duplicates(subset=['format_year','competition_name'])
    # Filter if row season date equals last season date column
    competitionEndDF = expandedDF[expandedDF['lastSeason'] == expandedDF['format_year']].drop_duplicates(subset=['format_year','competition_name'])

    # Count reported competitions by season
    seasonsDF = countActiveCompetitions(expandedDF)
    # Count reported cup competitions by season
    seasonsCupDF = countActiveCups(expandedDF)
    # Count reported league competitions by season
    seasonsLeagueDF = countActiveLeagues(expandedDF)
    # Count reported divisions by season
    seasonsDivDF = countActiveDivisions(expandedDF)

    # merge Counts
    seasonsDF = (seasonsDF.merge(seasonsCupDF,how='left', left_on='format_year', right_on='format_year')
                 .merge(seasonsLeagueDF,how='left', left_on='format_year', right_on='format_year')
                 .merge(seasonsDivDF,how='left', left_on='format_year', right_on='format_year'))
    seasonsDF = seasonsDF.fillna(0).astype('int64')

    # Add Change From Previous Year
    seasonsDF['delta'] = 'delta'
    seasonsDF = calcCompetitionDeltas(seasonsDF)

    # Add In Creation Events
    seasonsDF['created'] = 'created'
    seasonsDF = countCompetitionCreations(seasonsDF,competitionStartDF)

    # Set Initial Delta to Creation Events
    seasonsDF.loc[0:0,'competitionsDelta'] = seasonsDF.at[0, 'competitionsCreated']
    seasonsDF.loc[0:0,'cupsDelta'] = seasonsDF.at[0, 'cupsCreated']
    seasonsDF.loc[0:0,'leaguesDelta'] = seasonsDF.at[0, 'leaguesCreated']

    # Add In Dissolution Events
    seasonsDF['folded'] = 'folded'
    seasonsDF = countCompetitionEnds(seasonsDF,competitionEndDF)

    # Add In Net Change Events
    seasonsDF['netChange'] = 'netChange'
    seasonsDF = calcCompetitionNetChanges(seasonsDF)

    # Add In Net Suspension Events
    seasonsDF['suspendedNet'] = 'suspensionsNet'
    seasonsDF = calcCompetitionsNetSuspensions(seasonsDF)
    # Add In Total Suspended
    seasonsDF['suspendedTotal'] = 'suspendedTotal'
    seasonsDF = calcCompetitionsSuspended(seasonsDF)
    # Separate Suspensions from Unsuspensions
    seasonsDF['unsuspensions'] = 'unsuspensions'
    seasonsDF = calcCompetitionsUnsuspensions(seasonsDF)
    # Separate Suspensions from Unsuspensions
    seasonsDF['suspensions'] = 'suspensions'
    seasonsDF = calcCompetitionsSuspensions(seasonsDF)

    # Add Total From Previous Year
    seasonsDF['previous'] = 'previous'
    seasonsDF['competitionsPrv'] = seasonsDF['competitions'].shift(1).fillna(0).astype(int)
    seasonsDF['cupsPrv'] = seasonsDF['cups'].shift(1).fillna(0).astype(int)
    seasonsDF['leaguesPrv'] = seasonsDF['leagues'].shift(1).fillna(0).astype(int)
    seasonsDF['competitionsSuspendedPrv'] = seasonsDF['competitionsSuspendedTotal'].shift(1).fillna(0).astype(int)
    seasonsDF['cupsSuspendedPrv'] = seasonsDF['cupsSuspendedTotal'].shift(1).fillna(0).astype(int)
    seasonsDF['leaguesSuspendedPrv'] = seasonsDF['leaguesSuspendedTotal'].shift(1).fillna(0).astype(int)

    # Add In Empty Competition Slots
    maxComps = (seasonsDF['competitions'] + seasonsDF['competitionsSuspendedTotal']).max()
    maxCups = (seasonsDF['cups'] +  seasonsDF['cupsSuspendedTotal']).max()
    maxLeagues = (seasonsDF['leagues'] + seasonsDF['leaguesSuspendedTotal']).max()

    seasonsDF['emptyCompSlots'] = 'emptyCompSlots'
    seasonsDF['emptyComps'] = (maxComps - (seasonsDF['competitions'] + seasonsDF['competitionsSuspendedTotal'])) + seasonsDF['competitionsCreated']
    seasonsDF['emptyCups'] = (maxCups - (seasonsDF['cups'] + seasonsDF['cupsSuspendedTotal'])) + seasonsDF['cupsCreated']
    seasonsDF['emptyLeagues'] = (maxLeagues - (seasonsDF['leagues'] + seasonsDF['cupsSuspendedTotal'])) + seasonsDF['leaguesCreated']

    return seasonsDF

def aggregateTeamEvents(expandedDF):
    # Filter if row season date equals first season date column
    teamStartDF = expandedDF[expandedDF['season_founded'] == expandedDF['season_year']].drop_duplicates(subset=['season_year','team_name'])
    # Filter if row season date equals last season date column
    teamEndDF = expandedDF[expandedDF['season_last'] == expandedDF['season_year']].drop_duplicates(subset=['season_year','team_name'])

    # Count reported teams by season
    seasonsDF = countActiveTeams(expandedDF)
    seasonsDF = seasonsDF.fillna(0).astype('int64')

    # Add Change From Previous Year
    seasonsDF['delta'] = 'delta'
    seasonsDF = calcTeamsDeltas(seasonsDF)

    # Add In Creation Events
    seasonsDF['created'] = 'created'
    seasonsDF = countTeamsCreations(seasonsDF,teamStartDF)

    # Set Initial Delta to Creation Events
    seasonsDF.loc[0:0,'teamsDelta'] = seasonsDF.at[0, 'teamsCreated']

    # Add In Dissolution Events
    seasonsDF['folded'] = 'folded'
    seasonsDF = countTeamsEnds(seasonsDF,teamEndDF)

    # Add In Net Change Events
    seasonsDF['netChange'] = 'netChange'
    seasonsDF = calcTeamNetChanges(seasonsDF)

    # Add Total From Previous Year
    seasonsDF['previous'] = 'previous'
    seasonsDF['teamsPrv'] = seasonsDF['teams'].shift(1).fillna(0).astype(int)

    # Add In Empty Slots
    maxTeams = seasonsDF['teams'].max()

    seasonsDF['emptyTeamSlots'] = 'emptyTeamSlots'
    seasonsDF['emptyTeams'] = (maxTeams - seasonsDF['teams']) + seasonsDF['teamsCreated']

    return seasonsDF

def summariseSeasonsPeriodEvents(periodName, periodDF):
    periodProbDF = periodDF.drop(const.removalForCompsProbs,axis=1).agg(['sum'])
    periodProbDF['duration'] = periodDF['format_year'].max() - periodDF['format_year'].min() + 1 - len(periodDF[periodDF['competitionsPrv'] == 0])

    periodProbDF['competitionsMin'] = periodDF['competitions'].min()
    periodProbDF['competitions25%'] = periodDF['competitions'].quantile(0.25)
    periodProbDF['competitionsMedian'] = periodDF['competitions'].median()
    periodProbDF['competitions75%'] = periodDF['competitions'].quantile(0.75)
    periodProbDF['competitionsMax'] = periodDF['competitions'].max()

    periodProbDF['cupsMin'] = periodDF['cups'].min()
    periodProbDF['cups25%'] = periodDF['cups'].quantile(0.25)
    periodProbDF['cupsMedian'] = periodDF['cups'].median()
    periodProbDF['cups75%'] = periodDF['cups'].quantile(0.75)
    periodProbDF['cupsMax'] = periodDF['cups'].max()

    periodProbDF['leagMin'] = periodDF['leagues'].min()
    periodProbDF['leag25%'] = periodDF['leagues'].quantile(0.25)
    periodProbDF['leagMedian'] = periodDF['leagues'].median()
    periodProbDF['leag75%'] = periodDF['leagues'].quantile(0.75)
    periodProbDF['leagMax'] = periodDF['leagues'].max()

    periodProbDF['divMin'] = periodDF['minDivisions'].min()
    periodProbDF['divMax'] = periodDF['maxDivisions'].max()
    periodProbDF['divTierMin'] = periodDF['minTier'].max()
    periodProbDF['divTierMax'] = periodDF['maxTier'].min()
    periodProbDF['divClubsMin'] = periodDF['minDivisionClubs'].min()
    periodProbDF['divClubsMax'] = periodDF['maxDivisionClubs'].max()

    periodProbDF['competitionsCreatedProb'] = (periodProbDF['competitionsCreated'] / periodProbDF['emptyComps']).round(2)
    periodProbDF['cupsCreatedProb'] =  (periodProbDF['cupsCreated'] / periodProbDF['emptyCups']).round(2)
    periodProbDF['leaguesCreatedProb'] = (periodProbDF['leaguesCreated'] / periodProbDF['emptyLeagues']).round(2)
    periodProbDF['divisionsCreatedProb'] = (periodProbDF['divisionsCreated'] / periodProbDF['divisionsEmpt']).round(2)

    periodProbDF['compsFoldedProb'] = (periodProbDF['competitionsFolded'] / periodProbDF['competitionsPrv']).round(2)
    periodProbDF['cupsFoldedProb'] =  (periodProbDF['cupsFolded'] / periodProbDF['cupsPrv']).round(2)
    periodProbDF['leaguesFoldedProb'] = (periodProbDF['leaguesFolded'] / periodProbDF['leaguesPrv']).round(2)
    periodProbDF['divisionsFoldedProb'] = (periodProbDF['divisionsFolded'] / periodProbDF['divisionsRem']).round(2)

    periodProbDF['competitionsSuspendedProb'] = (periodProbDF['competitionsSuspended'] / periodProbDF['competitionsPrv']).round(2)
    periodProbDF['cupsSuspendedProb'] =  (periodProbDF['cupsSuspended'] / periodProbDF['cupsPrv']).round(2)
    periodProbDF['leaguesSuspendedProb'] = (periodProbDF['leaguesSuspended'] / periodProbDF['leaguesPrv']).round(2)

    periodProbDF['competitionsUnSuspendedProb'] = (periodProbDF['competitionsUnsuspended'] / periodProbDF['competitionsSuspendedPrv']).round(2)
    periodProbDF['cupsUnSuspendedProb'] =  (periodProbDF['cupsUnsuspended'] / periodProbDF['cupsSuspendedPrv']).round(2)
    periodProbDF['leaguesUnSuspendedProb'] = (periodProbDF['leaguesUnsuspended'] / periodProbDF['leaguesSuspendedPrv']).round(2)

    periodProbDF['periodName'] = periodName

    periodProbDF = periodProbDF.fillna(0)
    periodProbDF['duration'] = periodProbDF['duration'].astype('int64')

    periodProbDF['competitionsMin'] = periodProbDF['competitionsMin'].round(0).astype('int64')
    periodProbDF['competitions25%'] = periodProbDF['competitions25%'].round(0).astype('int64')
    periodProbDF['competitionsMedian'] = periodProbDF['competitionsMedian'].round(0).astype('int64')
    periodProbDF['competitions75%'] = periodProbDF['competitions75%'].round(0).astype('int64')
    periodProbDF['competitionsMax'] = periodProbDF['competitionsMax'].round(0).astype('int64')

    periodProbDF['cupsMin'] = periodProbDF['cupsMin'].round(0).astype('int64')
    periodProbDF['cups25%'] = periodProbDF['cups25%'].round(0).astype('int64')
    periodProbDF['cupsMedian'] = periodProbDF['cupsMedian'].round(0).astype('int64')
    periodProbDF['cups75%'] = periodProbDF['cups75%'].round(0).astype('int64')
    periodProbDF['cupsMax'] = periodProbDF['cupsMax'].round(0).astype('int64')

    periodProbDF['leagMin'] = periodProbDF['leagMin'].round(0).astype('int64')
    periodProbDF['leag25%'] = periodProbDF['leag25%'].round(0).astype('int64')
    periodProbDF['leagMedian'] = periodProbDF['leagMedian'].round(0).astype('int64')
    periodProbDF['leag75%'] = periodProbDF['leag75%'].round(0).astype('int64')
    periodProbDF['leagMax'] = periodProbDF['leagMax'].round(0).astype('int64')

    periodProbDF['divMin'] = periodProbDF['divMin'].round(0).astype('int64')
    periodProbDF['divMax'] = periodProbDF['divMax'].round(0).astype('int64')
    periodProbDF['divTierMin'] = periodProbDF['divTierMin'].round(0).astype('int64')
    periodProbDF['divTierMax'] = periodProbDF['divTierMax'].round(0).astype('int64')
    periodProbDF['divClubsMin'] = periodProbDF['divClubsMin'].round(0).astype('int64')
    periodProbDF['divClubsMax'] = periodProbDF['divClubsMax'].round(0).astype('int64')

    return periodProbDF.loc[:, ['periodName', 'duration', 'competitionsMin','competitions25%','competitionsMedian','competitions75%','competitionsMax', 'cupsMin','cups25%','cupsMedian','cups75%','cupsMax', 'leagMin','leag25%','leagMedian','leag75%','leagMax','divMin','divMax','divTierMin','divTierMax','divClubsMin','divClubsMax', 'competitionsCreatedProb','cupsCreatedProb', 'leaguesCreatedProb','divisionsCreatedProb','compsFoldedProb','cupsFoldedProb','leaguesFoldedProb','divisionsFoldedProb','competitionsSuspendedProb','cupsSuspendedProb','leaguesSuspendedProb','competitionsUnSuspendedProb','cupsUnSuspendedProb','leaguesUnSuspendedProb']]

def summariseSeasonsEvents(compsDF, shouldPrint, resultsDir, belleEpYear = 1914, interwarYears = [1918,1940], postwarYears = [1945,1980], glasnostYears = [1979,1990], modernYear = 1989):
    belleEpSliceDf = compsDF[compsDF['format_year'] < belleEpYear]
    interwarSliceDf = compsDF[compsDF['format_year'] < interwarYears[1]][compsDF['format_year'] > interwarYears[0]]
    postwarSliceDf = compsDF[compsDF['format_year'] < postwarYears[1]][compsDF['format_year'] > postwarYears[0]]
    glasnostSliceDf = compsDF[compsDF['format_year'] < glasnostYears[1]][compsDF['format_year'] > glasnostYears[0]]
    modernSliceDf = compsDF[compsDF['format_year'] > modernYear]

    if shouldPrint:
        belleEpSliceDf.to_csv(os.path.join(resultsDir,'league_period_belleEp_agg.csv'),index=False)
        interwarSliceDf.to_csv(os.path.join(resultsDir,'league_period_interwar_agg.csv'),index=False)
        postwarSliceDf.to_csv(os.path.join(resultsDir,'league_period_postwar_agg.csv'),index=False)
        glasnostSliceDf.to_csv(os.path.join(resultsDir,'league_period_glasnost_agg.csv'),index=False)
        modernSliceDf.to_csv(os.path.join(resultsDir,'league_period_modern_agg.csv'),index=False)

    belleEpSumDf = summariseSeasonsPeriodEvents('La Belle Époque',belleEpSliceDf)
    interwarSumDf = summariseSeasonsPeriodEvents('Interbellum', interwarSliceDf)
    postwarSumDf = summariseSeasonsPeriodEvents('Post-War', postwarSliceDf)
    glasnostSumDf = summariseSeasonsPeriodEvents('Glasnost', glasnostSliceDf)
    modernSumDf = summariseSeasonsPeriodEvents('Modern', modernSliceDf)

    return pd.concat([belleEpSumDf,interwarSumDf,postwarSumDf,glasnostSumDf,modernSumDf])

def summariseTeamsPeriodEvents(periodName, periodDF, sport):
    periodProbDF = periodDF.drop(const.removalForTeamsProbs,axis=1).agg(['sum'])
    periodProbDF['seasons'] = periodDF['season_year'].max() - periodDF['season_year'].min() + 1 - len(periodDF[periodDF['teamsPrv'] == 0])

    periodProbDF['teamsMin'] = periodDF['teams'].min()
    periodProbDF['teams25%'] = periodDF['teams'].quantile(0.25)
    periodProbDF['teamsMedian'] = periodDF['teams'].median()
    periodProbDF['teams75%'] = periodDF['teams'].quantile(0.75)
    periodProbDF['teamsMax'] = periodDF['teams'].max()

    periodProbDF['teamsCreatedProb'] = (periodProbDF['teamsCreated'] / periodProbDF['emptyTeams']).round(2)
    periodProbDF['teamsFoldedProb'] = (periodProbDF['teamsFolded'] / periodProbDF['teamsPrv']).round(2)


    periodProbDF['sport'] = sport
    periodProbDF['periodName'] = periodName

    periodProbDF = periodProbDF.fillna(0)
    periodProbDF['seasons'] = periodProbDF['seasons'].astype('int64')

    periodProbDF['teamsMin'] = periodProbDF['teamsMin'].round(0).astype('int64')
    periodProbDF['teams25%'] = periodProbDF['teams25%'].round(0).astype('int64')
    periodProbDF['teamsMedian'] = periodProbDF['teamsMedian'].round(0).astype('int64')
    periodProbDF['teams75%'] = periodProbDF['teams75%'].round(0).astype('int64')
    periodProbDF['teamsMax'] = periodProbDF['teamsMax'].round(0).astype('int64')

    return periodProbDF.loc[:, ['periodName', 'sport','seasons', 'teamsMin','teams25%','teamsMedian','teams75%','teamsMax', 'teamsCreatedProb','teamsFoldedProb']]

def summariseTeamEvents(teamsDF, sport, shouldPrint, resultsDir):
    belleEpSliceDf = teamsDF[teamsDF['season_year'] < 1914]
    interwarSliceDf = teamsDF[teamsDF['season_year'] < 1940][teamsDF['season_year'] > 1918]
    postwarSliceDf = teamsDF[teamsDF['season_year'] < 1980][teamsDF['season_year'] > 1945]
    glasnostSliceDf = teamsDF[teamsDF['season_year'] < 1990][teamsDF['season_year'] > 1979]
    modernSliceDf = teamsDF[teamsDF['season_year'] > 1989]

    if shouldPrint:
        belleEpSliceDf.to_csv(os.path.join(resultsDir,'teams_period_belleEp_agg.csv'),index=False)
        interwarSliceDf.to_csv(os.path.join(resultsDir,'teams_period_interwar_agg.csv'),index=False)
        postwarSliceDf.to_csv(os.path.join(resultsDir,'teams_period_postwar_agg.csv'),index=False)
        glasnostSliceDf.to_csv(os.path.join(resultsDir,'teams_period_glasnost_agg.csv'),index=False)
        modernSliceDf.to_csv(os.path.join(resultsDir,'teams_period_modern_agg.csv'),index=False)

    belleEpSumDf = summariseTeamsPeriodEvents('La Belle Époque',belleEpSliceDf,sport)
    interwarSumDf = summariseTeamsPeriodEvents('Interbellum', interwarSliceDf,sport)
    postwarSumDf = summariseTeamsPeriodEvents('Post-War', postwarSliceDf,sport)
    glasnostSumDf = summariseTeamsPeriodEvents('Glasnost', glasnostSliceDf,sport)
    modernSumDf = summariseTeamsPeriodEvents('Modern', modernSliceDf,sport)

    return pd.concat([belleEpSumDf,interwarSumDf,postwarSumDf,glasnostSumDf,modernSumDf])

def processSeasonsEvents(compsDF, shouldPrint, resultsDir, belleEpYear = 1914, interwarYears = [1918,1940], postwarYears = [1945,1980], glasnostYears = [1979,1990], modernYear = 1989):
    # expand
    compsExpDF = expandRange(compsDF,'format_start','format_end','format_range','format_year')
    compsExpDF = compsExpDF.sort_values(['format_year','competition_tier'],ascending=[True,True])

    if shouldPrint:
        compsExpDF.to_csv(os.path.join(resultsDir,'league_expanded.csv'),index=False)

    seasonsDF = aggregateSeasonsEvents(compsExpDF)

    if shouldPrint:
        seasonsDF.to_csv(os.path.join(resultsDir,'league_aggregate.csv'),index=False)

    foldedProbability = summariseSeasonsEvents(seasonsDF,True,resultsDir,belleEpYear,interwarYears, postwarYears, glasnostYears, modernYear)


    if shouldPrint:
        printDf = foldedProbability.copy()
        printDf['created'] = 'created'
        printDf['folded'] = 'folded'
        printDf['suspended'] = 'suspended'
        printDf['unsuspended'] = 'unsuspended'
        printDf['created'] = 'created'
        printDf['comps'] = 'comps'
        printDf['cups'] = 'cups'
        printDf['leag'] = 'leagues'
        printDf['divs'] = 'divisions'
        printDf = printDf.loc[:, ['periodName', 'duration','comps','competitionsMin','competitions25%','competitionsMedian','competitions75%','competitionsMax', 'cups','cupsMin','cups25%','cupsMedian','cups75%','cupsMax','leag', 'leagMin','leag25%','leagMedian','leag75%','leagMax','divs','divMin','divMax','divTierMin','divTierMax','divClubsMin','divClubsMax','created','competitionsCreatedProb','cupsCreatedProb', 'leaguesCreatedProb','divisionsCreatedProb','folded','compsFoldedProb','cupsFoldedProb','leaguesFoldedProb','divisionsFoldedProb','suspended','competitionsSuspendedProb','cupsSuspendedProb','leaguesSuspendedProb','unsuspended','competitionsUnSuspendedProb','cupsUnSuspendedProb','leaguesUnSuspendedProb']]
        printDf.to_csv(os.path.join(resultsDir,'league_sum.csv'),index=False)

    return foldedProbability

def processTeamsEvents(teamsDF, sport, shouldPrint, resultsDir):
    # expand
    teamsExpDF = expandRange(teamsDF,'season_founded','season_last','season_range','season_year')
    teamsExpDF = teamsExpDF.sort_values(['season_year','team_name'],ascending=[True,True])

    if shouldPrint:
        teamsExpDF.to_csv(os.path.join(resultsDir,'teams_expanded.csv'),index=False)

    teamsAggDF = aggregateTeamEvents(teamsExpDF)

    if shouldPrint:
        teamsAggDF.to_csv(os.path.join(resultsDir,'teams_aggregate.csv'),index=False)

    teamsSumDF = summariseTeamEvents(teamsAggDF,sport,True,resultsDir)

    if shouldPrint:
        teamsSumDF.to_csv(os.path.join(resultsDir,'teams_sum.csv'),index=False)

    return teamsSumDF