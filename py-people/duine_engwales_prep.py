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

# Frequency File Read
dirFreqBoysName = os.path.join(rootDirName, Path('../data/data/census/engwales/common/engwalesfirstnames-boys/'))
dirFreqGirlsName = os.path.join(rootDirName, Path('../data/data/census/engwales/common/engwalesfirstnames-girls/'))

boysDF = func.readEngWalesNameFreq(dirFreqBoysName,'M')
girlsDF = func.readEngWalesNameFreq(dirFreqGirlsName,'F')
namesDF = pd.concat([boysDF,girlsDF], axis=0, ignore_index=True)

namesDF['count'] = namesDF.sum(axis=1, numeric_only=True)

namesDF = namesDF[['NAME','gender','1996_count','1997_count','1998_count','1999_count','2000_count','count']]
namesDF['90sCount'] = namesDF[['1996_count','1997_count','1998_count','1999_count','2000_count']].sum(axis=1, numeric_only=True)


boysDF = boysDF.sort_values(['NAME'],ascending=[True])
boysDF.to_csv(os.path.join(resultsInterDirName,'boys.csv'),index=False)

girlsDF = girlsDF.sort_values(['NAME'],ascending=[True])
girlsDF.to_csv(os.path.join(resultsInterDirName,'girls.csv'),index=False)

namesDF = namesDF.sort_values(['90sCount','count','NAME'],ascending=[False,False,True])
namesDF.to_csv(os.path.join(resultsInterDirName,'names.csv'),index=False)
namesDF = namesDF.sort_values(['NAME'],ascending=[True])
namesDF.to_csv(os.path.join(resultsInterDirName,'names_az.csv'),index=False)
