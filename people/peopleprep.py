import pandas as pd
import regex as re
import glob
import os

from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path

import peopleconst as const
import peoplefunc as func
import namePrep as names

print('Load From Base Census Path: ' + const.dir1901name)
df1901 = func.readCensus(const.dir1901name,const.header1901,const.types1901)

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
dicLit = (pd.read_csv(const.dicLit1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processLiteracy('1901',dicLit,df1901)

print("1901 Census Processing Languages")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicLang = (pd.read_csv(const.dicLang1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
           .to_dict())['mapped']
df1901 = func.processLanguages('1901',dicLang,df1901)

print("1901 Census Religion Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicRel = (pd.read_csv(const.dicRel1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processReligion('1901',dicRel,df1901)

print("1901 Census Birthplace Standardisation")
# Use Non Exhaust to convert errors to NaNs
#dicLang = (pd.read_csv(dicLang1901name,names=['original','languages'],dtype={'original':'string','languages':'string'},index_col='original')
#          .to_dict())
dicBirth = (pd.read_csv(const.dicBirth1901NoExName,names=['original','mapped'],dtype={'original':'string','mapped':'string'},index_col='original')
          .to_dict())['mapped']
df1901 = func.processBirthplace('1901',dicBirth,df1901)

print("1901 Census Age Standardisation")
df1901 = func.processAge('1901',df1901)

print("1901 Census First Name Matching")
bcenter = names.readBCenterNames()
df1901['nameBCenterMatch'] =  df1901[['firstNameCap','gender']].apply(tuple, axis=1).isin(bcenter[['nameCap','gender']].apply(tuple, axis=1))
bwiz = names.readBWizardNames()
df1901['nameBWizMatch'] =  df1901[['firstNameCap','gender']].apply(tuple, axis=1).isin(bwiz[['nameCap','gender']].apply(tuple, axis=1))
behindNames = names.readBehindNames()
df1901['nameBehindMatch'] =  df1901[['firstNameCap','gender']].apply(tuple, axis=1).isin(behindNames[['nameCap','gender']].apply(tuple, axis=1))
df1901['nameMatch'] =  df1901[['nameBCenterMatch','nameBWizMatch','nameBehindMatch']].sum(axis=1) >= 2

os.makedirs(const.resultsInterDirName, exist_ok=True)
os.makedirs(const.resultsDirName, exist_ok=True)

# 1901 Census Write Results
print("1901 Census Intermediate Results")
df1901.info(verbose=True)
df1901.to_csv(const.file1901InterName, index=False)
func.writeFields(const.resultsInterDirName,'ire','1901',df1901)

print("1901 Census Final Results")

df1901 = df1901[['surnameFiltered', 'firstNameFiltered', 'gender','ageBucket','married', 'surnameCap', 'firstNameCap', 'surnameSoundex', 'firstNameSoundex','firstNamesLength', 'nameBCenterMatch','nameBWizMatch','nameBehindMatch','nameMatch', 'birthCountry','county','occupation','lit_read','lit_write', 'lit_unknown' , 'religionSan', 'lang_arabic','lang_austrian','lang_broke-eng','lang_broke-ire','lang_broke-sco','lang_carney','lang_chinese','lang_dutch','lang_english','lang_flemish','lang_french','lang_german','lang_greek','lang_gujarati','lang_hebrew','lang_hindustani','lang_irish','lang_italian','lang_latin','lang_manx','lang_norwegian','lang_russian','lang_scotch','lang_spanish','lang_swedish','lang_swiss-french','lang_telugu','lang_unknown','lang_welsh','lang_yankey','lang_yiddish']]
df1901.info(verbose=True)
df1901.to_csv(const.file1901Name, index=False)
func.writeFields(const.resultsDirName,'ire','1901',df1901)

# Write Chunks
#func.writeChunks(resultsDirName,'ire','1901',5000,'occupationClaude',df1901)

#print('Writing ire_occupationTmp_AZ_1901.csv'.format(name=name))
#df1901['occupationTmp'].value_counts().reset_index().sort_values(['occupationTmp','count'],ascending=[True,False]).to_csv(os.path.join(resultsDirName, 'ire_occupationTmp_AZ_1901.csv'.format(name=name)), index=False)