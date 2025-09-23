import os

from pathlib import Path


# Relative to This File
rootDirName = os.path.dirname(__file__)
resultsInterDirName = os.path.join(rootDirName, Path('../results_intermediate'))
resultsDirName = os.path.join(rootDirName, Path('../results_league'))

dirLeagueName = os.path.join(rootDirName, Path('../data/data/league/'))
dataFootballLeagueName = os.path.join(dirLeagueName, 'football-leagues.csv')

dataHockLeagueName = os.path.join(dirLeagueName, 'comp-hockey.csv')
dataTeamsHockName = os.path.join(dirLeagueName, 'teams-hockey.csv')


# 1901 Census Constants
leagueTypes = {
    'level': 'string',
    'organiser_name': 'string',
    'association_name': 'string',
    'home_and_away': 'bool',
    'venue_system': 'string',
    'entry': 'string',
    'quality': 'string',
    'gender': 'string',
    'draw_bonus': 'Int64',
    'points_tiebreaker': 'string',
    'format_start': 'Int64',
    'format_end': 'Int64',
    'sport': 'string',
    'competition_type': 'string',
    'competition_tier': 'Int64',
    'competition_name': 'string',
    'competition_format': 'string',
    'division_name': 'string',
    'clubs': 'Int64',
    'entry_format': 'string',
    'has_competition_playoffs': 'bool',
    'uneven_team_format': 'string',
    'draw_format': 'string',
    'add_draw_format': 'string',
    'win': 'Int64',
    'draw': 'Int64',
    'loss': 'Int64',
    'match_format': 'string',
    'finals_format': 'string',
    'finals_draw_format': 'string',
    'tiebreaker_title': 'string',
    'promotion_teams': 'Int64',
    'promotion_system': 'string',
    'relegation_teams': 'Int64',
    'relegation_system': 'string',
}

teamTypes = {
    'team_name': 'string',
    'team_base': 'string',
    'team_suffix': 'string',
    'country_name': 'string',
    'sport_name': 'string',
    'season_founded': 'Int64',
    'season_last': 'Int64',
}

removalForProbs = [
    'format_year',
    'delta',
    'created',
    'folded',
    'netChange',
    'suspendedNet',
    'suspendedTotal',
    'previous',
    'competitions',
    'cups',
    'leagues',
    'divisions',
    'leagueClubs',
    'minDivisionClubs',
    'maxDivisionClubs',
    'competitionsDelta',
    'cupsDelta',
    'leaguesDelta',
    #'competitionsCreated',
    #'cupsCreated',
    #'leaguesCreated',
    'competitionsNetChange',
    'cupsNetChange',
    'leaguesNetChange',
    'competitionsNetSuspended',
    'cupsNetSuspended',
    'leaguesNetSuspended',
    'competitionsSuspendedTotal',
    'cupsSuspendedTotal',
    'leaguesSuspendedTotal',
    'unsuspensions',
    #'competitionsUnsuspended',
    #'cupsUnsuspended',
    #'leaguesUnsuspended',
    'suspensions',
    'emptyCompSlots',
]