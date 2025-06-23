import pandas as pd
import regex as re
import os

from pathlib import Path

bcenterRegex = r'[\p{L}]+'

def bcenter_filter_fn(name:str) -> bool:
    if re.search(bcenterRegex,name):
        return True
    else:
        return False


def readBCenterNames():
    rootDirName = os.path.dirname(__file__)
    bcenterFileName = os.path.join(rootDirName, Path('../data/dict/firstnames/babycenter.csv'))

    cols = ["name", "gender"]
    types = {"name": 'string', "gender": 'string'}

    bcenter = pd.read_csv(bcenterFileName,names=cols,dtype=types,index_col=False)
    bcenter = bcenter[bcenter['name'].notnull()]

    bcenter['nameCap'] = bcenter.name.str.upper()
    gender = {'female' : 'F', 'male' : 'M'}
    bcenter['gender'] = bcenter['gender'].map(gender)

    # Remove any names that are not strictly letters
    bcenter = bcenter[bcenter['nameCap'].apply(bcenter_filter_fn)]
    return bcenter

def readBWizardNames():
    rootDirName = os.path.dirname(__file__)
    bwizFileName = os.path.join(rootDirName, Path('../data/dict/firstnames/babynamewizard.csv'))

    cols = ["name", "gender"]
    types = {"name": 'string', "gender": 'string'}

    bwiz = pd.read_csv(bwizFileName,names=cols,dtype=types,index_col=False)
    bwiz = bwiz[bwiz['name'].notnull()]

    bwiz['nameCap'] = bwiz.name.str.upper()
    gender = {'female' : 'F', 'male' : 'M'}
    bwiz['gender'] = bwiz['gender'].map(gender)

    # Remove any names that are not strictly letters
    bwiz = bwiz[bwiz['nameCap'].apply(bcenter_filter_fn)]
    return bwiz

def readBehindNames():
    rootDirName = os.path.dirname(__file__)
    behindFileName = os.path.join(rootDirName, Path('../data/dict/firstnames/behindthename.csv'))

    cols = ["nameCap", "gender", "bn_origin", "pronounciation", "variants", "meaning"]
    types = {"nameCap": 'string', "gender": 'string', "bn_origin": 'string', "pronunciation": 'string', "variants": 'string', "meaning": 'string'}

    behind = pd.read_csv(behindFileName,names=cols,dtype=types,index_col=False)
    behind = behind[behind['nameCap'].notnull()]

    gender = {'female' : 'F', 'male' : 'M'}
    behind['gender'] = behind['gender'].map(gender)

    # Remove any names that are not strictly letters
    behind = behind[behind['nameCap'].apply(bcenter_filter_fn)]
    return behind