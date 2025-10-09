
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

# England And Wales Firstname Frequency Constants
headerEngWalesFreqPre1996 = ["RANK", "NAME"]
headerEngWalesFreqPost1996 = ["Rank", "Name", "Count"]


typesEngWalesFreqPre1996 = {
    "RANK": 'Int64',
    "NAME": 'string',
}

typesEngWalesFreqPost1996 = {
    "Rank": 'Int64',
    "Name": 'string',
    "Count": 'Int64'
}