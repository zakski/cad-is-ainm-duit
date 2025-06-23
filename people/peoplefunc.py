import pandas as pd
import regex as re

import glob



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
    #df_census = df_census.join(df_census['surname'].str.split(expand = True).add_prefix('surname_').fillna(''))
    df_census['surnameList'] = df_census['surname'].str.split(" ", expand=False)

    return df_census