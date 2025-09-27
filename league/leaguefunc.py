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
    seasonsDF = expandedDF[expandedDF['competition_type'] == 'league'].groupby('format_year').agg(divisions=('competition_name','count'),leagueClubs=('clubs','sum'),minDivisionClubs=('clubs','min'),maxDivisionClubs=('clubs','max')).reset_index()
    seasonsDF.index = seasonsDF['format_year']
    seasonsDF = seasonsDF.reindex(np.arange(seasonsDF['format_year'].min(), seasonsDF['format_year'].max() + 1)).fillna(0)
    seasonsDF['divisions'] = seasonsDF['divisions'].astype(int)
    seasonsDF['leagueClubs'] = seasonsDF['leagueClubs'].astype(int)
    seasonsDF['minDivisionClubs'] = seasonsDF['minDivisionClubs'].astype(int)
    seasonsDF['maxDivisionClubs'] = seasonsDF['maxDivisionClubs'].astype(int)
    seasonsDF = seasonsDF.drop(['format_year'],axis=1).reset_index()

    return seasonsDF

def calcCompetitionDeltas(seasonsDF):
    seasonsDF['competitionsDelta'] = seasonsDF['competitions'].diff().fillna(0).astype(int)
    seasonsDF['cupsDelta'] = seasonsDF['cups'].diff().fillna(0).astype(int)
    seasonsDF['leaguesDelta'] = seasonsDF['leagues'].diff().fillna(0).astype(int)

    return seasonsDF

def calcCompetitionNetChanges(seasonsDF):
    seasonsDF['competitionsNetChange'] = seasonsDF['competitionsCreated']  - seasonsDF['competitionsFolded']
    seasonsDF['cupsNetChange'] = seasonsDF['cupsCreated']  - seasonsDF['cupsFolded']
    seasonsDF['leaguesNetChange'] = seasonsDF['leaguesCreated']  - seasonsDF['leaguesFolded']

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

def summariseSeasonsPeriodEvents(periodName, periodDF):
    periodProbDF = periodDF.drop(const.removalForProbs,axis=1).agg(['sum'])
    periodProbDF['duration'] = periodDF['format_year'].max() - periodDF['format_year'].min() + 1 - len(periodDF[periodDF['competitionsPrv'] == 0])

    periodProbDF['competitionsCreatedProb'] = (periodProbDF['competitionsCreated'] / periodProbDF['emptyComps']).round(2)
    periodProbDF['cupsCreatedProb'] =  (periodProbDF['cupsCreated'] / periodProbDF['emptyCups']).round(2)
    periodProbDF['leaguesCreatedProb'] = (periodProbDF['leaguesCreated'] / periodProbDF['emptyLeagues']).round(2)

    periodProbDF['compsFoldedProb'] = (periodProbDF['competitionsFolded'] / periodProbDF['competitionsPrv']).round(2)
    periodProbDF['cupsFoldedProb'] =  (periodProbDF['cupsFolded'] / periodProbDF['cupsPrv']).round(2)
    periodProbDF['leaguesFoldedProb'] = (periodProbDF['leaguesFolded'] / periodProbDF['leaguesPrv']).round(2)

    periodProbDF['competitionsSuspendedProb'] = (periodProbDF['competitionsSuspended'] / periodProbDF['competitionsPrv']).round(2)
    periodProbDF['cupsSuspendedProb'] =  (periodProbDF['cupsSuspended'] / periodProbDF['cupsPrv']).round(2)
    periodProbDF['leaguesSuspendedProb'] = (periodProbDF['leaguesSuspended'] / periodProbDF['leaguesPrv']).round(2)

    periodProbDF['competitionsUnSuspendedProb'] = (periodProbDF['competitionsUnsuspended'] / periodProbDF['competitionsSuspendedPrv']).round(2)
    periodProbDF['cupsUnSuspendedProb'] =  (periodProbDF['cupsUnsuspended'] / periodProbDF['cupsSuspendedPrv']).round(2)
    periodProbDF['leaguesUnSuspendedProb'] = (periodProbDF['leaguesUnsuspended'] / periodProbDF['leaguesSuspendedPrv']).round(2)

    periodProbDF['periodName'] = periodName

    periodProbDF = periodProbDF.fillna(0)
    periodProbDF['duration'] = periodProbDF['duration'].astype('int64')

    return periodProbDF.loc[:, ['periodName', 'duration', 'competitionsCreatedProb','cupsCreatedProb', 'leaguesCreatedProb','compsFoldedProb','cupsFoldedProb','leaguesFoldedProb','competitionsSuspendedProb','cupsSuspendedProb','leaguesSuspendedProb','competitionsUnSuspendedProb','cupsUnSuspendedProb','leaguesUnSuspendedProb']]

def summariseSeasonsEvents(compsDF, shouldPrint, resultsDir):
    belleEpSliceDf = compsDF[compsDF['format_year'] < 1914]
    interwarSliceDf = compsDF[compsDF['format_year'] < 1940][compsDF['format_year'] > 1918]
    postwarSliceDf = compsDF[compsDF['format_year'] < 1980][compsDF['format_year'] > 1945]
    glasnostSliceDf = compsDF[compsDF['format_year'] < 1990][compsDF['format_year'] > 1979]
    modernSliceDf = compsDF[compsDF['format_year'] > 1989]

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

def summariseTeamsPeriodEvents(periodName, teamsDF, sport):
    teamsSumDF = teamsDF['season_year'].value_counts().reset_index()['count'].describe().reset_index()
    teamsSumDF = teamsSumDF.T.reset_index()
    teamsSumDF.columns = teamsSumDF.iloc[0]
    teamsSumDF = teamsSumDF.drop(['index', 'std'],axis=1)
    teamsSumDF = teamsSumDF.iloc[1:]

    teamsSumDF['sport'] = sport
    teamsSumDF['periodName'] = periodName


    teamsSumDF = teamsSumDF.fillna(0)
    teamsSumDF = teamsSumDF.round().astype('int64',errors='ignore')
    teamsSumDF = teamsSumDF.rename(columns={"count": "seasons"})

    return teamsSumDF.loc[:, ['periodName',  "seasons", 'sport', 'mean','min', '25%','50%','75%','max']]


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

def processSeasonsEvents(compsDF, shouldPrint, resultsDir):
    # expand
    compsExpDF = expandRange(compsDF,'format_start','format_end','format_range','format_year')
    compsExpDF = compsExpDF.sort_values(['format_year','competition_tier'],ascending=[True,True])

    if shouldPrint:
        compsExpDF.to_csv(os.path.join(resultsDir,'league_expanded.csv'),index=False)

    seasonsDF = aggregateSeasonsEvents(compsExpDF)

    if shouldPrint:
        seasonsDF.to_csv(os.path.join(resultsDir,'league_aggregate.csv'),index=False)

    foldedProbability = summariseSeasonsEvents(seasonsDF,True,resultsDir)


    if shouldPrint:
        foldedProbability.to_csv(os.path.join(resultsDir,'league_sum.csv'),index=False)

    return foldedProbability

def processTeamsEvents(teamsDF, sport, shouldPrint, resultsDir):
    # expand
    teamsExpDF = expandRange(teamsDF,'season_founded','season_last','season_range','season_year')
    teamsExpDF = teamsExpDF.sort_values(['season_year','team_name'],ascending=[True,True])

    if shouldPrint:
        teamsExpDF.to_csv(os.path.join(resultsDir,'teams_expanded.csv'),index=False)
        teamsBaseDF = teamsExpDF['team_base'].value_counts().reset_index()
        teamsSuffDF = teamsExpDF['team_suffix'].value_counts().reset_index()

        teamsBaseDF.to_csv(os.path.join(resultsDir,'teams_base.csv'),index=False)
        teamsSuffDF.to_csv(os.path.join(resultsDir,'teams_suffix.csv'),index=False)

    teamsSumDF = summariseTeamEvents(teamsExpDF,sport,True,resultsDir)

    if shouldPrint:
        teamsSumDF.to_csv(os.path.join(resultsDir,'teams_sum.csv'),index=False)

    return teamsSumDF