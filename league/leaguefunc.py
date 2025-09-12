import pandas as pd
import numpy as np



def expandRange(data, minimumCol, maximumCol, rangeCol, col):

    # Add a len column for the size of our range. We're also adding an original_index column we'll need later.
    data = data.assign(range_col = data[maximumCol]- data[minimumCol]+1, original_index=data.index).rename({"range_col": rangeCol}, axis=1)

    # Create a new dataframe by repeating the values from the original rangeCol times. So the rows from the
    # first range will be repeated 100 times, the second range will be repeated 10 times, etc.
    new_data = pd.DataFrame(np.repeat(data.values, data[rangeCol], axis=0))
    new_data.columns = data.columns
    new_data = new_data.astype(data.dtypes)


    # At this point, we've expanded our ranges, but we don't have a
    # column that represents the number that the range has been expanded into.

    # To get that, we're going to use the SICs_min column, plus a counter that resets
    # every time we get to a new SIC range.

    # The counter can be made by grouping by the original SICs range and then doing
    # a cumulative sum of a column of just ones.
    cumsum = new_data.assign(ones=np.ones_like(new_data.index)).groupby('original_index').ones.cumsum()

    # This looks like 1-100, followed by 1-10, etc. We need it to be 0-99, 0-9 etc. so we subtract one
    # before we add it to the SICs_min to get the actual SIC number.
    finalData = new_data.assign(actual_col=new_data[minimumCol] + cumsum - 1).rename({"actual_col": col}, axis=1)
    return finalData.drop(['original_index',rangeCol],axis=1)

def teamsSummary(teamsDF, sport):
    teamsSumDF = teamsDF['season_year'].value_counts().reset_index()['count'].describe().reset_index()
    teamsSumDF = teamsSumDF.T.reset_index()
    teamsSumDF.columns = teamsSumDF.iloc[0]
    teamsSumDF = teamsSumDF.drop(['index', 'std'],axis=1)
    teamsSumDF = teamsSumDF.iloc[1:]
    teamsSumDF = teamsSumDF.round().astype('int64')
    teamsSumDF = teamsSumDF.rename(columns={"count": "seasons"})
    teamsSumDF['sport'] = sport
    return teamsSumDF