import pandas as pd
import regex as re
import glob

import peopleconst as const

from pathlib import Path

bcenterRegex = r'[\p{L}]+'

def bcenter_filter_fn(name:str) -> bool:
    if re.search(bcenterRegex,name):
        return True
    else:
        return False


def readBCenterNames():
    cols = ["name", "gender", 'origin', 'meaning']
    types = {"name": 'string', "gender": 'string', "origin": 'string', "meaning": 'string'}

    bcenter = pd.read_csv(const.bcenterFileName,names=cols,dtype=types,index_col=False)
    bcenter = bcenter[bcenter['name'].notnull()]

    bcenter['nameCap'] = bcenter.name.str.upper()
    gender = {'f' : 1, 'm' : 0}
    bcenter['gender'] = bcenter['gender'].map(gender)#.astype('int64')

    # Remove any names that are not strictly letters
    bcenter = bcenter[bcenter['nameCap'].apply(bcenter_filter_fn)]
    return bcenter

def readBWizardNames():
    cols = ["name", "gender"]
    types = {"name": 'string', "gender": 'string'}

    bwiz = pd.read_csv(const.bwizFileName,names=cols,dtype=types,index_col=False)
    bwiz = bwiz[bwiz['name'].notnull()]

    bwiz['nameCap'] = bwiz.name.str.upper()
    gender = {'female' : 1, 'male' : 0}
    bwiz['gender'] = bwiz['gender'].map(gender)#.astype('int64')

    # Remove any names that are not strictly letters
    bwiz = bwiz[bwiz['nameCap'].apply(bcenter_filter_fn)]
    return bwiz

def readBehindNames():
    cols = ["nameCap", "gender", "bn_origin", "pronounciation", "variants", "meaning"]
    types = {"nameCap": 'string', "gender": 'string', "bn_origin": 'string', "pronunciation": 'string', "variants": 'string', "meaning": 'string'}

    behind = pd.read_csv(const.behindFileName,names=cols,dtype=types,index_col=False)
    behind = behind[behind['nameCap'].notnull()]

    gender = {'female' : 1, 'male' : 0}
    behind['gender'] = behind['gender'].map(gender)#.astype('int64')

    # Remove any names that are not strictly letters
    behind = behind[behind['nameCap'].apply(bcenter_filter_fn)]
    return behind

def readScottishNamesFrequency(dirname, startYear,endYear):
    list_header = ["rank", "name", "frequency"]

    map_types = {
        "rank": 'string',
        "name": 'string',
        "frequency": 'Int64',
    }
    yearRegex = r'[0-9]{4}'

    dfList=[]

    result = pd.DataFrame(columns=list_header).astype(map_types)
    result = result.drop('rank', axis='columns')
    result.set_index(['name'], inplace=True)

    for filename in glob.iglob(dirname + '/*.csv', recursive=True):
        year = int(re.search(yearRegex,filename).group())
        if (year >= startYear and year <= endYear):
            print(filename)
            df = pd.read_csv(filename,names=list_header,header=0, dtype=map_types,index_col=False)
            df = df.drop('rank', axis='columns')
            df = df[df['name'].notnull()]
            df.set_index(['name'], inplace=True)
            dfList.append(df)

    for yearDF in dfList:
        result = result.add(yearDF, fill_value=0)

    return result.reindex(result.index).reset_index()

def readScottishFirstNamesFrequency(startYear,endYear):
    boys = readScottishNamesFrequency(const.dirDictionaryScotBoyName,startYear,endYear)
    boys.insert(1, 'gender', 0)

    girls = readScottishNamesFrequency(const.dirDictionaryScotGirlsName,startYear,endYear)
    girls.insert(1, 'gender', 1)

    return pd.concat([boys,girls], axis=0, ignore_index=True).sort_values(['name'],ascending=[True])


def readNornIreNamesFrequency(dirname, startYear,endYear):
    list_header = [ "name", "frequency", "rank"]

    map_types = {
        "name": 'string',
        "frequency": 'Int64',
        "rank": 'string',
    }
    yearRegex = r'[0-9]{4}'

    dfList=[]

    result = pd.DataFrame(columns=list_header).astype(map_types)
    result = result.drop('rank', axis='columns')
    result.set_index(['name'], inplace=True)

    for filename in glob.iglob(dirname + '/**/*.csv', recursive=True):
        year = int(re.search(yearRegex,filename).group())
        if (year >= startYear and year <= endYear):
            print(filename)
            df = pd.read_csv(filename,names=list_header,header=0, dtype=map_types,index_col=False)
            df = df.drop('rank', axis='columns')
            df = df[df['name'].notnull()]
            df.set_index(['name'], inplace=True)
            dfList.append(df)

    for yearDF in dfList:
        result = result.add(yearDF, fill_value=0)

    return result.reindex(result.index).reset_index()

def readNornIreFirstNamesFrequency(startYear,endYear):
    boys = readNornIreNamesFrequency(const.dirDictionaryNornIreBoyName,startYear,endYear)
    boys.insert(1, 'gender', 0)

    girls = readNornIreNamesFrequency(const.dirDictionarynNornIreGirlsName,startYear,endYear)
    girls.insert(1, 'gender', 1)

    return pd.concat([boys,girls], axis=0, ignore_index=True).sort_values(['name'],ascending=[True])

def readEngWalesNamesNoFrequency(dirname, startYear,endYear):
    list_header = [ "rank", "name"]

    map_types = {
        "rank": 'string',
        "name": 'string',
    }
    yearRegex = r'[0-9]{4}'

    dfList=[]

    for filename in glob.iglob(dirname + '/**/*.csv', recursive=True):
        year = int(re.search(yearRegex,filename).group())
        if (year >= startYear and year <= endYear):
            print(filename)
            df = pd.read_csv(filename,names=list_header,header=0, dtype=map_types,index_col=False)
            df = df.drop('rank', axis='columns')
            dfList.append(df)
        else:
            print("not " + filename)

    return pd.concat(dfList, axis=0, ignore_index=True)

def readEngWalesFirstNamesNoFrequency(startYear,endYear):
    boys = readEngWalesNamesNoFrequency(const.dirDictionaryEngWalesBoyName,startYear,min(endYear,1994))
    boys.insert(1, 'gender', 0)
    boys = boys.value_counts(['name', 'gender']).reset_index().rename(columns={'count': 'frequency'})

    girls = readEngWalesNamesNoFrequency(const.dirDictionarynEngWalesGirlsName,startYear,min(endYear,1994))
    girls.insert(1, 'gender', 1)
    girls = girls.value_counts(['name', 'gender']).reset_index().rename(columns={'count': 'frequency'})

    return pd.concat([boys,girls], axis=0, ignore_index=True).sort_values(['name'],ascending=[True])

def readEngWalesNamesFrequency(dirname, startYear,endYear):
    list_header = [ "rank", "name", "frequency"]

    map_types = {
        "rank": 'string',
        "name": 'string',
        "frequency": 'Int64',
    }
    yearRegex = r'[0-9]{4}'

    dfList=[]

    result = pd.DataFrame(columns=list_header).astype(map_types)
    result = result.drop('rank', axis='columns')
    result.set_index(['name'], inplace=True)

    for filename in glob.iglob(dirname + '/**/*.csv', recursive=True):
        year = int(re.search(yearRegex,filename).group())
        if (year >= startYear and year <= endYear):
            print(filename)
            df = pd.read_csv(filename,names=list_header,header=0, dtype=map_types,index_col=False)
            df = df.drop('rank', axis='columns')
            df = df[df['name'].notnull()]
            df.set_index(['name'], inplace=True)
            dfList.append(df)

    for yearDF in dfList:
        result = result.add(yearDF, fill_value=0)

    return result.reindex(result.index).reset_index()

def readEngWalesFirstNamesFrequency(startYear,endYear):
    boys = readEngWalesNamesFrequency(const.dirDictionaryEngWalesBoyName,max(startYear,1996) ,endYear)
    boys.insert(1, 'gender', 0)

    girls = readEngWalesNamesFrequency(const.dirDictionarynEngWalesGirlsName,max(startYear,1996) ,endYear)
    girls.insert(1, 'gender', 1)

    return pd.concat([boys,girls], axis=0, ignore_index=True).sort_values(['name'],ascending=[True])

def readUsaNamesFrequency(dirname, startYear,endYear):
    list_header = [ "name", "gender", "frequency"]

    map_types = {
        "name": 'string',
        "gender": 'string',
        "frequency": 'Int64',
    }
    yearRegex = r'[0-9]{4}'

    dfList=[]

    result = pd.DataFrame(columns=list_header).astype(map_types)
    result.set_index(['name'], inplace=True)

    for filename in glob.iglob(dirname + '/**/*.txt', recursive=True):
        year = int(re.search(yearRegex,filename).group())
        if (year >= startYear and year <= endYear):
            print(filename)
            df = pd.read_csv(filename,names=list_header, dtype=map_types,index_col=False)
            df = df[df['name'].notnull()]
            df.set_index(['name'], inplace=True)
            dfList.append(df)

    for yearDF in dfList:
        result = result.add(yearDF)

    gender = {'F' : 1, 'M' : 0}
    result['gender'] = result['gender'].map(gender)#.astype('int64')

    return result.reindex(result.index).reset_index()

def readUsaFirstNamesFrequency(startYear,endYear):
    usa = readUsaNamesFrequency(const.dirDictionaryUsaName,startYear ,endYear)
    usa['name'] = usa['name'].str.upper()
    return usa

def firstNamesFrequency():
    scot = readScottishFirstNamesFrequency(1974,2000)
    scot = scot[scot['frequency'] > 2]
    scot['name'] = scot['name'].str.upper()

    ni = readNornIreFirstNamesFrequency(1974,2000)
    ni['name'] = ni['name'].str.upper()

    engWalesOld = readEngWalesFirstNamesNoFrequency(1904,2000)
    engWalesNew = readEngWalesFirstNamesFrequency(1904,2000)

    usaVic = readUsaFirstNamesFrequency(1837,1900)
    usaED = readUsaFirstNamesFrequency(1901,1913)
    usaBSI = readUsaFirstNamesFrequency(1914,1916)
    usaWWI = readUsaFirstNamesFrequency(1917,1918)
    usaInter = readUsaFirstNamesFrequency(1919,1939)
    usaBSII = readUsaFirstNamesFrequency(1939,1941)
    usaWWII = readUsaFirstNamesFrequency(1942,1945)
    usaPost = readUsaFirstNamesFrequency(1946,1954)

    engWales = pd.merge(
        pd.merge(
            pd.merge(
                pd.merge(
                    pd.merge(
                        pd.merge(
                            pd.merge(
                                pd.merge(
                                    pd.merge(
                                        pd.merge(
                                            pd.merge(
                                                engWalesOld,engWalesNew,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_ew_new']
                                            ),ni,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_ni']
                                        ),scot,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_scot']
                                    ),usaVic,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_vic']
                                ),usaED,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_ed']
                            ),usaBSI,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_bs']
                        ),usaWWI,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_wwi']
                    ),usaInter,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_it']
                ),usaBSII,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_bsii']
            ),usaWWII,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_wwii']
        ),usaPost,how='outer', left_on=['name', 'gender'], right_on=['name', 'gender'], suffixes=['', '_us_post']
    )
    engWales['frequency'] = engWales['frequency'].fillna(0)
    engWales = engWales.astype({"frequency": int})
    engWales['frequency_ew_new'] = engWales['frequency_ew_new'].fillna(0)
    engWales['frequency_ni'] = engWales['frequency_ni'].fillna(0)
    engWales['frequency_scot'] = engWales['frequency_scot'].fillna(0)

    return engWales

# return engWalesOld.join(engWalesNew,how='outer',on=['name','gender'],lsuffix='_ew_old',rsuffix='_ew_new')#.join(scot,how='outer',on=['name','gender'],lsuffix='',rsuffix='_scot').join(ni,how='outer',on=['name','gender'],lsuffix='',rsuffix='_ni')