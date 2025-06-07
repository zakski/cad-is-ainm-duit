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

print("1901 Census Count = " + str(df1901.shape[0]))

df1901.info(verbose=True)

os.makedirs(resultsDirName, exist_ok=True)

# 1901 Census Write Results
df1901.to_csv(file1901name, index=False)

for name, values in df1901.items():
    df1901[name].value_counts().reset_index().to_csv(os.path.join(resultsDirName, 'ire_{name}_1901.csv'.format(name=name)), index=False)