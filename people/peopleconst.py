import os

from pathlib import Path

# 1901 Census Constants
header1901 = ["surname", "name", "townlandOrStreet", "DED", "county", "age", "gender", "birthplace", "occupation", "religion", "literacy", "languages", "relationToHead", "married", "illnesses", "house"]

types1901 = {
    "surname": 'string',
    "name": 'string',
    "townlandOrStreet": 'string',
    "DED": 'string',
    "county": 'string',
    "age": 'string',
    "gender": 'string',
    "birthplace": 'string',
    "occupation": 'string',
    "religion": 'string',
    "literacy": 'string',
    "languages": 'string',
    "relationToHead": 'string',
    "married": 'string',
    "illnesses": 'string',
    "house": 'string'
}

# Parent Dir Relative to This File
rootDirName = os.path.dirname(__file__)

# 1901 Census Files Dir
dir1901name = os.path.join(rootDirName, Path('../data/data/census/ireland/1901/'))

# Intermediate Results Dir Relative to This File
resultsInterDirName = os.path.join(rootDirName, Path('../results_intermediate'))
# 1901 Census Intermediate Results File
file1901InterName = os.path.join(resultsInterDirName, 'ire_census_1901.csv')

# Final Results Dir Relative to This File
resultsDirName = os.path.join(rootDirName, Path('../results'))
# 1901 Census Final Results File
file1901Name = os.path.join(resultsDirName, 'ire_census_1901.csv')

# First Name Debugging Results Dir Relative to This File
firstNamesDirName = os.path.join(rootDirName, Path('../results_firstDebug'))
# 1901 Census First Name Results File
firstNames1901Name = os.path.join(firstNamesDirName, 'ire_firstNameDebug_1901.csv')
firstNames1901FreqName = os.path.join(firstNamesDirName, 'ire_firstNameFreqDebug_1901.csv')




# Irish Census Dictionary Dir Constants
dirDictionary1901name = os.path.join(rootDirName, Path('../data/dict/census/ireland/'))

# 1901 Dictionary File Constants
# Languages
dicLang1901name = os.path.join(dirDictionary1901name, 'ire_lang_1901.csv')
dicLang1901NoExName = os.path.join(dirDictionary1901name, 'ire_lang_1901_nonExhaust.csv')
# Literacy SKill
dicLit1901name = os.path.join(dirDictionary1901name, 'ire_literacy_1901.csv')
dicLit1901NoExName = os.path.join(dirDictionary1901name, 'ire_literacy_1901_nonExhaust.csv')
# Religion Affiliation
dicRel1901Name = os.path.join(dirDictionary1901name, 'ire_religion_1901.csv')
dicRel1901NoExName = os.path.join(dirDictionary1901name, 'ire_religion_1901_nonExhaust.csv')
# Birth Country
dicBirth1901Name = os.path.join(dirDictionary1901name, 'ire_birth_country_1901.csv')
dicBirth1901NoExName = os.path.join(dirDictionary1901name, 'ire_birth_country_1901_nonExhaust.csv')
# Occupation
dicOcc1901Name = os.path.join(dirDictionary1901name, 'ire_occupation_1901.csv')
dicOcc1901NoExName = os.path.join(dirDictionary1901name, 'ire_occupation_1901_nonExhaust.csv')
dicOcc1901ClaudeName = os.path.join(dirDictionary1901name, 'ire_occupation_Claude_1901.csv')
# Marriage
dicMarried1901Name = os.path.join(dirDictionary1901name, 'ire_married_1901.csv')