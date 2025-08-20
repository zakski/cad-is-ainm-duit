import pandas as pd
import regex as re
import glob
import os

from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path

import peopleconst as const
import peoplefunc as func
import namePrep as names

# Relative to This File
rootDirName = os.path.dirname(__file__)
resultsInterDirName = os.path.join(rootDirName, Path('../results_intermediate'))
resultsDirName = os.path.join(rootDirName, Path('../results'))

# 1901 Dictionary File Read
dirDictionary1901name = os.path.join(rootDirName, Path('../data/dict/census/ireland/'))
dicLang1901name = os.path.join(dirDictionary1901name, 'ire_lang_1901.csv')
dicLang1901NoExName = os.path.join(dirDictionary1901name, 'ire_lang_1901_nonExhaust.csv')
dicLit1901name = os.path.join(dirDictionary1901name, 'ire_literacy_1901.csv')
dicLit1901NoExName = os.path.join(dirDictionary1901name, 'ire_literacy_1901_nonExhaust.csv')
dicRel1901Name = os.path.join(dirDictionary1901name, 'ire_religion_1901.csv')
dicRel1901NoExName = os.path.join(dirDictionary1901name, 'ire_religion_1901_nonExhaust.csv')
dicBirth1901Name = os.path.join(dirDictionary1901name, 'ire_birth_country_1901.csv')
dicBirth1901NoExName = os.path.join(dirDictionary1901name, 'ire_birth_country_1901_nonExhaust.csv')

# 1901 Census File Read
dir1901name = os.path.join(rootDirName, Path('../data/data/census/ireland/1901/'))
file1901InterName = os.path.join(resultsInterDirName, 'ire_census_1901.csv')
file1901Name = os.path.join(resultsDirName, 'ire_census_1901.csv')

print('Load From Base Census Path: ' + dir1901name)
df1901 = func.readCensus(dir1901name,const.header1901,const.types1901)

# 1901 Census Data Integrity Check
print("1901 Census Count = " + str(df1901.shape[0]))
assert df1901.shape[0] == 4429866
df1901.info(verbose=True)

# 1901 Census Data Sanitation

print("1901 Census Processing Surnames")
df1901 = func.processSurnames('1901',df1901)

print("1901 Census Processing First Names")
df1901 = func.processFirstNames('1901',df1901)

print("1901 Census Gender Standardisation")
gender = {'M' : 0, 'F' : 1, 'm' : 0, 'f' : 1}
df1901['gender'] = df1901['gender'].map(gender)
df1901 = df1901[df1901['gender'].notnull()]
df1901['gender'] = df1901['gender'].astype('int64')
print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census County Standardisation")
countryRename = {'Londonderry' : 'Derry',  'Queen\'s Co.': 'Laois', 'King\'s Co.' : 'Offaly'}
df1901['county'] = df1901['county'].map(countryRename).fillna(df1901['county'])
df1901 = df1901[df1901['county'].notnull()]
print("1901 Census Count = " + str(df1901.shape[0]))

print("1901 Census Processing Literacy")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicLit = (pd.read_csv(dicLit1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processLiteracy('1901',dicLit,df1901)

print("1901 Census Processing Languages")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicLang = (pd.read_csv(dicLang1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
           .to_dict())['mapped']
df1901 = func.processLanguages('1901',dicLang,df1901)

print("1901 Census Religion Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicRel = (pd.read_csv(dicRel1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processReligion('1901',dicRel,df1901)

print("1901 Census Birthplace Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicBirth = (pd.read_csv(dicBirth1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processBirthplace('1901',dicBirth,df1901)

print("1901 Census First Name Matching")
bcenter = names.readBCenterNames()
df1901['nameBCenterMatch'] =  df1901[['nameCap','gender']].apply(tuple, axis=1).isin(bcenter[['nameCap','gender']].apply(tuple, axis=1))
bwiz = names.readBWizardNames()
df1901['nameBWizMatch'] =  df1901[['nameCap','gender']].apply(tuple, axis=1).isin(bwiz[['nameCap','gender']].apply(tuple, axis=1))
behindNames = names.readBehindNames()
df1901['nameBehindMatch'] =  df1901[['nameCap','gender']].apply(tuple, axis=1).isin(behindNames[['nameCap','gender']].apply(tuple, axis=1))
df1901['nameMatch'] =  df1901[['nameBCenterMatch','nameBWizMatch','nameBehindMatch']].sum(axis=1) >= 2

df1901.info(verbose=True)

os.makedirs(resultsInterDirName, exist_ok=True)
os.makedirs(resultsDirName, exist_ok=True)

# 1901 Census Write Results
print("1901 Census Intermediate Results")
df1901.to_csv(file1901InterName, index=False)

for name, values in df1901.items():
    print('Writing ire_{name}_1901.csv'.format(name=name))
    df1901[name].value_counts().reset_index().to_csv(os.path.join(resultsInterDirName, 'ire_{name}_1901.csv'.format(name=name)), index=False)

print("1901 Census Final Results")
df1901.drop(['DED', 'firstName_1','firstName_2', 'firstName_3', 'firstName_4', 'firstName_5', 'firstName_6', 'house', 'languages', 'languagesSan', 'literacy', 'literacySan', 'religion', 'surname_1','surname_2', 'surname_3', 'surname_4', 'surname_5', 'name', 'surname', 'surnameSan', 'townlandOrStreet','birthplace'], axis=1, inplace=True)
df1901.to_csv(file1901Name, index=False)

for name, values in df1901.items():
    print('Writing ire_{name}_1901.csv'.format(name=name))
    df1901[name].value_counts().reset_index().to_csv(os.path.join(resultsDirName, 'ire_{name}_1901.csv'.format(name=name)), index=False)