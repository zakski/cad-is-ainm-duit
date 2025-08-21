import pandas as pd
import regex as re

import glob

from sklearn.preprocessing import MultiLabelBinarizer


def readCensus(dirname, list_header, map_types):
    dfList=[]
    for filename in glob.iglob(dirname + '/**/*.csv', recursive=True):
        print(filename)
        dfList.append(pd.read_csv(filename,names=list_header,dtype=map_types,index_col=False))

    return pd.concat(dfList, axis=0, ignore_index=True)



def filterForWords(df_census, column):
    nameRegex = r'\p{L}[\p{L} \'-]*'

    def name_filter_fn(name:str) -> bool:
        if re.search(nameRegex,name):
            return True
        else:
         return False

    df_census = df_census[df_census[column].notnull()]
    return df_census[df_census[column].apply(name_filter_fn)]

def sanitiseSurnames(df_census):
    macRegex = r'^(Ma*c) ([A-Z].+)'
    oRegex = r'^O[ ]*([A-Z].+)'
    def name_fn(name:str) -> str:
        if re.search(macRegex,name):
            return re.sub(macRegex,r'\1\2',name)
        else:
            if re.search(oRegex,name):
                return re.sub(oRegex,r"O'\1",name)
            else:
                return name

    df_census['surnameSan'] = df_census['surname'].apply(name_fn)
    df_census = df_census.join(df_census['surnameSan'].str.split(expand = True).add_prefix('surname_').fillna(''))
    # df_census['surname'].str.split(" ", expand=False)

    return df_census

def processSurnames(censusYear,df_census):
    print(censusYear + " Census Filtering Surnames")

    df_census = filterForWords(df_census,'surname')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Standardising Surnames")
    df_census = sanitiseSurnames(df_census)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    df_census.rename(columns={"surname_0": "surnameFiltered"}, inplace=True)

    print(censusYear + " Census Filtering Out Surnames With ?")
    df_census = df_census[~df_census["surnameFiltered"].str.contains("?", regex=False)]
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Capitalising Surnames")
    df_census['surnameCap'] = df_census.surnameFiltered.str.upper()
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processFirstNames(censusYear,df_census):
    print(censusYear + " Census Filtering First Names For Words")
    df_census = filterForWords(df_census,'name')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Standardising First Names")
    df_census = df_census.join(df_census['name'].str.split(expand = True).add_prefix('firstName_').fillna(''))
    df_census['firstNamesLength']=df_census['name'].str.split(expand = False).apply(lambda row: len(row))
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    df_census.rename(columns={"firstName_0": "firstNameFiltered"}, inplace=True)

    print(censusYear + " Census Filtering Out First Names With ?")
    df_census = df_census[~df_census["firstNameFiltered"].str.contains("?", regex=False)]
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Capitalising First Names")
    df_census['nameCap'] = df_census.firstNameFiltered.str.upper()
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processLiteracy(censusYear,dicLit, df_census):
    print(censusYear + " Census Filtering Literacy")
    df_census['literacy'] = df_census['literacy'].fillna('Unknown')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Sanitising Literacy")
    df_census['literacySan'] = df_census['literacy'].map(dicLit)
    df_census = df_census[df_census['literacySan'].notnull()]
    df_census["literacySanList"] = df_census["literacySan"].str.split(" ", expand=False)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Sparse Mapping Literacy")

    mlb = MultiLabelBinarizer(sparse_output=True)

    df_census = df_census.join(
        pd.DataFrame.sparse.from_spmatrix(
            mlb.fit_transform(df_census.pop('literacySanList')),
            index=df_census.index,
            columns=mlb.classes_
        )
    )

    df_census.rename(columns = {
        'Read': 'lit_read',
        'Write' : 'lit_write',
        'Unknown' : 'lit_unknown'},
        inplace=True)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    df_census = df_census.drop(['Illiterate'], axis=1)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processLanguages(censusYear,dicLang, df_census):
    print(censusYear + " Census Filtering Languages")
    df_census['languages'] = df_census['languages'].fillna('Unknown')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))


    print(censusYear + " Census Sanitising Languages")
    df_census['languagesSan'] = df_census['languages'].map(dicLang)
    df_census = df_census[df_census['languagesSan'].notnull()]
    df_census["languagesSanList"] = df_census["languagesSan"].str.split(" ", expand=False)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    mlb = MultiLabelBinarizer(sparse_output=True)

    print(censusYear + " Census Sparse Mapping Languages")
    df_census = df_census.join(
        pd.DataFrame.sparse.from_spmatrix(
            mlb.fit_transform(df_census.pop('languagesSanList')),
            index=df_census.index,
            columns=mlb.classes_
        )
    )

    df_census.rename(columns = {
    'Arabic': 'lang_arabic',
    'Austrian' : 'lang_austrian',
    'Broken-English' : 'lang_broke-eng',
    'Broken-Irish' : 'lang_broke-ire',
    'Broken-Scotch' : 'lang_broke-sco',
    'Carney' : 'lang_carney',
    'Chinese' : 'lang_chinese',
    'Dutch' : 'lang_dutch',
    'English' : 'lang_english',
    'Flemish' : 'lang_flemish',
    'French' : 'lang_french',
    'German' : 'lang_german',
    'Greek' : 'lang_greek',
    'Gujarati' : 'lang_gujarati',
    'Hebrew' : 'lang_hebrew',
    'Hindustani' : 'lang_hindustani',
    'Irish' : 'lang_irish',
    'Italian' : 'lang_italian',
    'Latin' : 'lang_latin',
    'Manx' : 'lang_manx',
    'Norwegian' : 'lang_norwegian',
    'Russian' : 'lang_russian',
    'Scotch' : 'lang_scotch',
    'Spanish' : 'lang_spanish',
    'Swedish' : 'lang_swedish',
    'Swiss-French' : 'lang_swiss-french',
    'Telugu' : 'lang_telugu',
    'Unknown' : 'lang_unknown',
    'Welsh' : 'lang_welsh',
    'Yankey' : 'lang_yankey',
    'Yiddish' : 'lang_yiddish'},
    inplace=True)
    df_census = df_census.drop(['No-Language'], axis=1)
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processReligion(censusYear,dicRel, df_census):
    print(censusYear + " Census Filtering Religion")
    df_census['religion'] = df_census['religion'].fillna('Unknown')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Sanitising Religion")
    df_census['religionSan'] = df_census['religion'].map(dicRel).astype('string')
    df_census = df_census[df_census['religionSan'].notnull()]
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processBirthplace(censusYear,dicBir, df_census):
    print(censusYear + " Census Filtering Birthplace")
    df_census['birthplace'] = df_census['birthplace'].fillna('Unknown')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Sanitising Birthplace")
    df_census['birthCountry'] = df_census['birthplace'].map(dicBir).astype('string')
    df_census = df_census[df_census['birthCountry'].notnull()]
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census

def processOccupation(censusYear,dicOcc, df_census):
    print(censusYear + " Census Filtering Occupation")
    df_census['birthplace'] = df_census['occupation'].fillna('Unknown')
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    #print(censusYear + " Census Filtering Out Occupations With ?")
    #df_census = df_census[~df_census["occupation"].str.contains("?", regex=False)]
    #print(censusYear + " Census Count = " + str(df_census.shape[0]))

    print(censusYear + " Census Sanitising Occupation")
    df_census['occupationTmp'] = df_census['occupation'].replace(dicOcc).astype('string')
    #df_census = df_census[df_census['birthCountry'].notnull()]
    print(censusYear + " Census Count = " + str(df_census.shape[0]))

    return df_census