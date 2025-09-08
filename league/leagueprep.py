import pandas as pd
import regex as re
import glob
import os

import leaguefunc as func

from pathlib import Path


# Relative to This File
rootDirName = os.path.dirname(__file__)
resultsInterDirName = os.path.join(rootDirName, Path('../results_intermediate'))
resultsDirName = os.path.join(rootDirName, Path('../results_league'))

dirLeagueName = os.path.join(rootDirName, Path('../data/data/league/'))
dataFootballLeagueName = os.path.join(dirLeagueName, 'football.csv')

footieHeader = ['level','name_base','name_prefix','name_suffix','name_full','name_short','organiser','organiser_name','clubs','entry','stages','qualification_spots','qualification_byes_format','tier_1_byes','tier_1_byes_format','tier_1_bye_entry_format','tier_1_entry_format','tier_1_intermediate','tier_1_qualifying_third','tier_1_qualifying_second','tier_1_qualifying_first','tier_1_qualifying_preliminary','tier_2_byes','tier_2_byes_format','tier_2_bye_entry_format','tier_2_entry_format','tier_2_intermediate','tier_2_qualifying_sixth','tier_2_qualifying_fifth','tier_2_qualifying_fourth','tier_2_qualifying_third','tier_2_qualifying_second','tier_2_qualifying_first','tier_2_qualifying_preliminary','amateur_cup_byes','amateur_cup_bye_entry_format','non_association_byes','non_association_bye_entry_format','non_association_other_byes','non_association_other_bye_entry_format','invite_byes','invite_bye_entry_format','format_start','format_end','type','quality','gender','victory','draw','loss','points_tiebreaker','match_system','uneven_team_system','draw_system','replay_venue','add_replay_venue','extra_time','previous_winner','home_and_away','venue_system','venue_semis','venue_finals','video_referee','promotion_teams','promotion_system','relegation_teams','relegation_system']

footieTypes = {
    'level': 'string',
    'name_base': 'string',
    'name_prefix': 'string',
    'name_suffix': 'string',
    'name_full': 'string',
    'name_short': 'string',
    'organiser': 'string',
    'organiser_name': 'string',
    'clubs': 'Int64', # entry_format
    'entry': 'string', # entry_format
    'stages': 'string',
    'qualification_spots': 'Int64',
    'qualification_byes_format': 'string',
    'tier_1_byes': 'Int64', # qual_tier_1
    'tier_1_byes_format': 'string',  # qual_tier_1
    'tier_1_bye_entry_format': 'string',  # qual_tier_1
    'tier_1_entry_format': 'string',  # qual_tier_1
    'tier_1_intermediate': 'Int64',  # qual_tier_1
    'tier_1_qualifying_third': 'Int64',  # qual_tier_1
    'tier_1_qualifying_second': 'Int64',  # qual_tier_1
    'tier_1_qualifying_first': 'Int64',  # qual_tier_1
    'tier_1_qualifying_preliminary': 'Int64',  # qual_tier_1
    'tier_2_byes': 'Int64', # qual_tier_2
    'tier_2_byes_format': 'string', # qual_tier_2
    'tier_2_bye_entry_format': 'string', # qual_tier_2
    'tier_2_entry_format': 'string', # qual_tier_2
    'tier_2_intermediate': 'Int64', # qual_tier_2
    'tier_2_qualifying_sixth': 'Int64', # qual_tier_2
    'tier_2_qualifying_fifth': 'Int64', # qual_tier_2
    'tier_2_qualifying_fourth': 'Int64', # qual_tier_2
    'tier_2_qualifying_third': 'Int64', # qual_tier_2
    'tier_2_qualifying_second': 'Int64', # qual_tier_2
    'tier_2_qualifying_first': 'Int64', # qual_tier_2
    'tier_2_qualifying_preliminary': 'Int64', # qual_tier_2
    'amateur_cup_byes': 'Int64',
    'amateur_cup_bye_entry_format': 'string',
    'non_association_byes': 'Int64',
    'non_association_bye_entry_format': 'string',
    'non_association_other_byes': 'Int64',
    'non_association_other_bye_entry_format': 'string',
    'invite_byes': 'Int64',
    'invite_bye_entry_format': 'string',
    'format_start': 'Int64', # format_weight
    'format_end': 'Int64', # format_weight
    'type': 'string', # comp_format
    'quality': 'string', # comp_format
    'gender': 'string', # comp_format
    'victory': 'Int64', # score_sys
    'draw': 'Int64', # score_sys
    'loss': 'Int64', # score_sys
    'points_tiebreaker': 'string', # score_sys
    'match_system': 'string',
    'uneven_team_system': 'string',
    'draw_system': 'string',
    'replay_venue': 'string',
    'add_replay_venue': 'string',
    'extra_time': 'string',
    'previous_winner': 'string',
    'home_and_away': 'bool',
    'venue_system': 'string',
    'venue_semis': 'string',
    'venue_finals': 'string',
    'video_referee': 'bool', # video_referee
    'promotion_teams': 'Int64', # pro_sys
    'promotion_system': 'string', # pro_sys
    'relegation_teams': 'Int64', # rel_sys
    'relegation_system': 'string' # rel_sys
}

# 1901 Dictionary File Read
print('Load League Data From Path: ' + dirLeagueName)
footData = pd.read_csv(dataFootballLeagueName,header=0,names=footieHeader,dtype=footieTypes,index_col=False)

# standardisation
footData['promotion_system'] = footData['promotion_system'].fillna('none')
footData['relegation_system'] = footData['relegation_system'].fillna('none')
footData['points_tiebreaker'] = footData['points_tiebreaker'].fillna('none')
footData['victory'] = footData['victory'].fillna(0)
footData['draw'] = footData['draw'].fillna(0)
footData['loss'] = footData['loss'].fillna(0)

# group data
#footData['pro_sys'] = footData[['promotion_system', 'promotion_teams']].apply(tuple, axis=1)
#footData['rel_sys'] = footData[['relegation_system', 'relegation_teams']].apply(tuple, axis=1)

# expand
footExpandedData = func.expandRange(footData,'format_start','format_end','format_range','format_year')
footExpandedData = footExpandedData.sort_values(['format_year','level'],ascending=[True,True])

# time format used weight
#footData['format_weight'] = footData['format_end'] - footData['format_start'] + 1

# 'level'
# 'name_base'
# 'name_prefix'
# 'name_suffix'
# 'name_full'
# 'name_short'
# 'organiser'
# 'organiser_name'
#footData['entry_format'] = footData[['entry', 'clubs']].apply(tuple, axis=1)
# 'stages'
# 'qualification_spots'
# 'qualification_byes_format'
# 'tier_1_byes'
# 'tier_1_byes_format'
# 'tier_1_bye_entry_format'
# 'tier_1_entry_format'
# 'tier_1_intermediate'
# 'tier_1_qualifying_third'
# 'tier_1_qualifying_second'
# 'tier_1_qualifying_first'
# 'tier_1_qualifying_preliminary'
# 'tier_2_byes'
# 'tier_2_byes_format'
# 'tier_2_bye_entry_format'
# 'tier_2_entry_format'
# 'tier_2_intermediate'
# 'tier_2_qualifying_sixth'
# 'tier_2_qualifying_fifth'
# 'tier_2_qualifying_fourth'
# 'tier_2_qualifying_third'
# 'tier_2_qualifying_second'
# 'tier_2_qualifying_first'
# 'tier_2_qualifying_preliminary'
# 'amateur_cup_byes'
# 'amateur_cup_bye_entry_format'
# 'non_association_byes'
# 'non_association_bye_entry_format'
# 'non_association_other_byes'
# 'non_association_other_bye_entry_format'
# 'invite_byes'
# 'invite_bye_entry_format'
# 'format_start'
# 'format_end'
# 'type'
# 'quality'
# 'gender'
#footData['score_sys'] = footData[['victory', 'draw', 'loss', 'points_tiebreaker']].apply(tuple, axis=1)
# 'match_system'
# 'uneven_team_system'
# 'draw_system'
# 'extra_time'
# 'previous_winner'
# 'home_and_away'
#footData['cup_venues'] = footData[['venue_system',  'replay_venue', 'add_replay_venue','venue_semis', 'venue_finals']].apply(tuple, axis=1)
# 'video_referee'
#footData['pro_sys'] = footData[['promotion_system', 'promotion_teams']].apply(tuple, axis=1)
#footData['rel_sys'] = footData[['relegation_system', 'relegation_teams']].apply(tuple, axis=1)


footExpandedData.to_csv(os.path.join(resultsInterDirName,'expanded.csv'),index=False)

orgFootData = footExpandedData.groupby('organiser_name')

for name, group in orgFootData:
    fileName = '{filePrefix}_{grouping}_{name}.csv'.format(filePrefix='eng',grouping='foot',name=name)
    dirName = os.path.join(resultsInterDirName,'{grouping}_{name}'.format(grouping='foot',name=name))
    os.makedirs(dirName, exist_ok=True)

    print('Writing {name}'.format(name=fileName))
    group.to_csv(os.path.join(dirName,fileName), index=False)