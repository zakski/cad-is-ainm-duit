import pandas as pd
import regex as re
import glob
import os

from sklearn.preprocessing import MultiLabelBinarizer

import peopleconst as const

# Relative to This File
rootDirName = os.path.dirname(__file__)
resultsDirName = os.path.join(rootDirName, '..\\results')

# 1901 Dictionary File Read
dirDictionary1901name = os.path.join(rootDirName, '..\\data\\dict\\census\\ireland\\')
dicLang1901name = os.path.join(dirDictionary1901name, 'ire_lang_1901.csv')
dicLang1901NoExName = os.path.join(dirDictionary1901name, 'ire_lang_1901_nonExhaust.csv')
dicLit1901name = os.path.join(dirDictionary1901name, 'ire_literacy_1901.csv')
dicLit1901NoExName = os.path.join(dirDictionary1901name, 'ire_literacy_1901_nonExhaust.csv')

# 1901 Census File Read
dir1901name = os.path.join(rootDirName, '..\\data\\data\\census\\ireland\\1901\\')
file1901name = os.path.join(resultsDirName, 'ire_census_1901.csv')

dfList=[]

for filename in glob.iglob(dir1901name + '**/*.csv', recursive=True):
    print(filename)
    dfList.append(pd.read_csv(filename,names=const.header1901,dtype=const.types1901,index_col=False))

df1901 = pd.concat(dfList, axis=0, ignore_index=True)

# 1901 Census Data Integrity Check
print("1901 Census Count = " + str(df1901.shape[0]))
assert df1901.shape[0] == 4429866
df1901.info(verbose=True)

# 1901 Census Data Sanitation
nameRegex = r'\p{L}[\p{L} \'-]*'


def name_filter_fn(name:str) -> bool:
    if re.search(nameRegex,name):
        return True
    else:
        return False

print("1901 Census Filter Surname")
df1901 = df1901[df1901['surname'].notnull()]
df1901 = df1901[df1901.surname.apply(name_filter_fn)]

print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census Filter First Name")
df1901 = df1901[df1901['name'].notnull()]
df1901 = df1901[df1901.name.apply(name_filter_fn)]

print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census Capitalise")
df1901['surnameCap'] = df1901.surname.str.upper()
df1901['nameCap'] = df1901.name.str.upper()

print("1901 Census Gender Standardisation")
gender = {'M' : 0, 'F' : 1, 'm' : 0, 'f' : 1}
df1901['gender'] = df1901['gender'].map(gender)
df1901 = df1901[df1901['gender'].notnull()]
df1901['gender'] = df1901['gender'].astype('int64')

print("1901 Census Language Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicLang = (pd.read_csv(dicLang1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901['languages'] = df1901['languages'].fillna('Unknown')
df1901['languagesSan'] = df1901['languages'].map(dicLang)
df1901 = df1901[df1901['languagesSan'].notnull()]
df1901["languagesSanList"] = df1901["languagesSan"].str.split(" ", expand=False)
mlb = MultiLabelBinarizer(sparse_output=True)
df1901 = df1901.join(
    pd.DataFrame.sparse.from_spmatrix(
        mlb.fit_transform(df1901.pop('languagesSanList')),
        index=df1901.index,
        columns=mlb.classes_))
df1901.rename(columns = {
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
df1901.drop(['No-Language'], axis=1)
print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census Literacy Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicLit = (pd.read_csv(dicLit1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
           .to_dict())['mapped']
df1901['literacy'] = df1901['literacy'].fillna('Unknown')
df1901['literacySan'] = df1901['literacy'].map(dicLit)
df1901 = df1901[df1901['literacySan'].notnull()]
df1901["literacySanList"] = df1901["literacySan"].str.split(" ", expand=False)
mlb = MultiLabelBinarizer(sparse_output=True)
df1901 = df1901.join(
    pd.DataFrame.sparse.from_spmatrix(
        mlb.fit_transform(df1901.pop('literacySanList')),
        index=df1901.index,
        columns=mlb.classes_))
df1901.rename(columns = {
    'Read': 'lit_read',
    'Write' : 'lit_write',
    'Unknown' : 'lit_unknown'},
    inplace=True)
df1901.drop(['Illiterate'], axis=1)
print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census County Standardisation")
countryRename = {'Londonderry' : 'Derry',  'Queen\'s Co.': 'Laois', 'King\'s Co.' : 'Offaly'}
df1901['county'] = df1901['county'].map(countryRename).fillna(df1901['county'])
df1901 = df1901[df1901['county'].notnull()]
print("1901 Census Count = " + str(df1901.shape[0]))

df1901.info(verbose=True)

os.makedirs(resultsDirName, exist_ok=True)

# 1901 Census Write Results
df1901.to_csv(file1901name, index=False)

for name, values in df1901.items():
    df1901[name].value_counts().reset_index().to_csv(os.path.join(resultsDirName, 'ire_{name}_1901.csv'.format(name=name)), index=False)