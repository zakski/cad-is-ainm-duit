"""
Correct and standardise Irish 1901 census occupation strings.

Reads ire_occupation_1901.csv (occupations by descending count), applies
British English spelling/grammar and period-appropriate normalisation
(apostrophes, word order, abbreviations, compound words). Outputs the full
dataset with original columns plus corrected_occupation and change_category
to ire_occupation_1901_corrected.csv. File order is preserved; the file is
not re-sorted.

Pipeline (per occupation.md): remove brackets; treat '-' as whitespace;
condense duplicate whitespace; then apply spelling/grammar/ordering and
compound-word rules from CORRECTIONS. To refine rules, process in batches,
inspect differences (occupation vs corrected_occupation), add new entries
to CORRECTIONS and re-run.

Change categories (change_category column):
    UNCHANGED
        No change was made; corrected_occupation equals the original occupation.
    NORMALIZATION
        Only normalization was applied (brackets removed, hyphens as space,
        duplicate whitespace collapsed). No dict lookup was used.
    DICT_LOOKUP
        The occupation was corrected using the CORRECTIONS mapping (exact or
        case-insensitive match).
    DICT_LOOKUP; NORMALIZATION
        Both normalization and a dict lookup were applied (e.g. "House-Keeper"
        → "House Keeper" → "Housekeeper").
    AMERICAN_SPELLING
        American "Labor"/"Laborer" was converted to British "Labour"/"Labourer"
        via a pattern rule.
    ABBREVIATION
        Abbreviation "Servt" was expanded to "Servant" via a pattern rule.
    POSSESSIVE
        Possessive apostrophe was added via a pattern rule (e.g. "Farmers Son"
        → "Farmer's Son" for known occupation stems + relation words).
    WORD_ORDER
        Word order was corrected by a pattern rule (e.g. "Servant Domestic"
        → "Domestic Servant", "Domestic Servant General" → "General Domestic Servant").
    LABOURER_ORDER
        "Labourer X" was reordered to "X Labourer" by a pattern rule.
    COMPOUND_KEEPER
        "X Keeper" was compounded to "Xkeeper" by a pattern rule (e.g. "House Keeper"
        → "Housekeeper").
    AGRICULTURAL_ABBREVIATION
        Unambiguous agricultural abbreviation (Agl, Agrl, Agr, etc.) was expanded
        to "Agricultural Labourer" by a pattern rule.
    GENERAL_ABBREVIATION
        Unambiguous general abbreviation (Genl, Gen, etc.) was expanded to
        "General Labourer" by a pattern rule.
    ABBREVIATION_AMBIGUOUS
        Ambiguous abbreviation ("A Labourer", "G Labourer") was expanded; use this
        category to review and confirm these corrections.
    Any of the above may appear combined (e.g. "DICT_LOOKUP; POSSESSIVE").

Rows whose original occupation matches a Scholar variant (e.g. Scholars, Scolar)
are written to ire_occupation_1901_scholar_review.csv for manual review; no
pattern correction is applied for Scholar.

Rows whose corrected_occupation contains words not in the British English word list
are written to ire_occupation_1901_spellcheck_review.csv with unknown_words and
suggested_occupation (pyspellchecker correction using words_british.txt). The word
list is read from archives/dict/words/words_british.txt only. Create it once with:
  python archives/dict/words/fetch_english_words.py
"""

import re
from pathlib import Path
from typing import Callable

import pandas as pd

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "ire_occupation_1901.csv"
OUTPUT_PATH = SCRIPT_DIR / "ire_occupation_1901_corrected.csv"
OUTPUT_CHANGED_PATH = SCRIPT_DIR / "ire_occupation_1901_corrected_changed.csv"
OUTPUT_UNCHANGED_PATH = SCRIPT_DIR / "ire_occupation_1901_corrected_unchanged.csv"
OUTPUT_SCHOLAR_REVIEW_PATH = SCRIPT_DIR / "ire_occupation_1901_scholar_review.csv"
OUTPUT_SPELLCHECK_REVIEW_PATH = SCRIPT_DIR / "ire_occupation_1901_spellcheck_review.csv"

from occupation_spellcheck import has_word_list, suggest_spellcorrected, unknown_words_in_text

# Complete correction mapping (all corrections from JS)
CORRECTIONS = {
    # All apostrophe corrections
    "Farmers Son": "Farmer's Son",
    "Farmers Daughter": "Farmer's Daughter",
    "Farmers Wife": "Farmer's Wife",
    "Farmer Son": "Farmer's Son",
    "Farmer Daughter": "Farmer's Daughter",
    "Farmers Sister": "Farmer's Sister",
    "Farmers Brother": "Farmer's Brother",
    "Farmers Nephew": "Farmer's Nephew",
    "Farmers Niece": "Farmer's Niece",
    "Farmers Mother": "Farmer's Mother",
    "Farmers Widow": "Farmer's Widow",
    "Farmers Servant": "Farmer's Servant",
    "Farmers Labourer": "Farmer's Labourer",
    "Farmers Assistant": "Farmer's Assistant",
    "Farmers Daughter in Law": "Farmer's Daughter in Law",
    "Farmers Son in Law": "Farmer's Son in Law",
    "Farmers Grand Son": "Farmer's Grandson",
    "Farmers Grand Daughter": "Farmer's Granddaughter",
    "Farmers Daught": "Farmer's Daughter",
    "Drapers Apprentice": "Draper's Apprentice",
    "Grocers Apprentice": "Grocer's Apprentice",
    "Grocers Porter": "Grocer's Porter",
    "Solicitors Clerk": "Solicitor's Clerk",
    "Masons Labourer": "Mason's Labourer",
    "Labourers Wife": "Labourer's Wife",
    "Labourers Daughter": "Labourer's Daughter",
    "Labourers Son": "Labourer's Son",
    "Labourers Widow": "Labourer's Widow",
    "Labourer Wife": "Labourer's Wife",
    "Labourer Son": "Labourer's Son",
    "Labourer Daughter": "Labourer's Daughter",
    "Blacksmiths Assistant": "Blacksmith's Assistant",
    "Butchers Assistant": "Butcher's Assistant",
    "Butchers Porter": "Butcher's Porter",
    "Tailors Assistant": "Tailor's Assistant",
    "Shoemakers Assistant": "Shoemaker's Assistant",
    "Carpenters Assistant": "Carpenter's Assistant",
    "Carpenters Apprentice": "Carpenter's Apprentice",
    "Drapers Assistant": "Draper's Assistant",
    "Drapers Porter": "Draper's Porter",
    "Drapers Clerk": "Draper's Clerk",
    "Grocers Assistant": "Grocer's Assistant",
    "Bakers Assistant": "Baker's Assistant",
    "Soldiers Wife": "Soldier's Wife",
    "Builders Labourer": "Builder's Labourer",
    "Builder Labourer": "Builder's Labourer",
    "Chemists Assistant": "Chemist's Assistant",
    "Policemans Son": "Policeman's Son",
    "Policemans Wife": "Policeman's Wife",
    "Teachers Daughter": "Teacher's Daughter",
    "Tailors Wife": "Tailor's Wife",
    "Carpenters Wife": "Carpenter's Wife",
    "Carpenters Son": "Carpenter's Son",
    "Carpenters Daughter": "Carpenter's Daughter",
    "Shepherds Son": "Shepherd's Son",
    "Shepherds Daughter": "Shepherd's Daughter",
    "Shepherds Wife": "Shepherd's Wife",
    "Herds Son": "Herd's Son",
    "Herds Daughter": "Herd's Daughter",
    "Herds Wife": "Herd's Wife",
    "Publicans Son": "Publican's Son",
    "Publicans Daughter": "Publican's Daughter",
    "Publicans Wife": "Publican's Wife",
    "Publicans Assistant": "Publican's Assistant",
    "Shopkeepers Son": "Shopkeeper's Son",
    "Shopkeepers Daughter": "Shopkeeper's Daughter",
    "Shop Keepers Daughter": "Shopkeeper's Daughter",
    "Shop Keepers Wife": "Shopkeeper's Wife",
    "Dairymans Son": "Dairyman's Son",
    "Dairymans Daughter": "Dairyman's Daughter",
    "Mill Owners Wife": "Mill Owner's Wife",
    "Fishermans Daughter": "Fisherman's Daughter",
    "Farmers Mother in Law": "Farmer's Mother in Law",
    "Accountants Clerk": "Accountant's Clerk",
    "Blacksmiths Apprentice": "Blacksmith's Apprentice",
    "Agricultural Labourers Daughter": "Agricultural Labourer's Daughter",
    "Fishermans Wife": "Fisherman's Wife",
    "Printers Labourer": "Printer's Labourer",
    "Chemists Apprentice": "Chemist's Apprentice",
    "Brewers Clerk": "Brewer's Clerk",
    "Shoemakers Wife": "Shoemaker's Wife",
    "Caretakers Wife": "Caretaker's Wife",
    "Blacksmiths Helper": "Blacksmith's Helper",
    "Childrens Nurse": "Children's Nurse",
    "Sailors Wife": "Sailor's Wife",
    "Shepherd Son": "Shepherd's Son",
    "Herd Daughter": "Herd's Daughter",
    "Tailors Daughter": "Tailor's Daughter",
    "Famers Daughter": "Farmer's Daughter",
    "Caretakers Daughter": "Caretaker's Daughter",
    "Farmeress Son": "Farmeress's Son",
    "Farmeress Daughter": "Farmeress's Daughter",
    "Labrs Wife": "Labourer's Wife",
    "Childrens Maid": "Children's Maid",
    # Compound words
    "House Keeper": "Housekeeper",
    "General House Keeper": "General Housekeeper",
    "Domestic House Keeper": "Domestic Housekeeper",
    "Retired House Keeper": "Retired Housekeeper",
    "House Keeper at Home": "Housekeeper at Home",
    "Box Maker": "Boxmaker",
    "Brush Maker": "Brushmaker",
    "Boot Maker": "Bootmaker",
    "Shop Keeper": "Shopkeeper",
    "Assistant Shop Keeper": "Assistant Shopkeeper",
    "Retired Shop Keeper": "Retired Shopkeeper",
    "Shop Keeper and Farmer": "Shopkeeper and Farmer",
    "Watch Maker": "Watchmaker",
    "Store Keeper": "Storekeeper",
    "Gate Keeper": "Gatekeeper",
    "School Master": "Schoolmaster",
    "School Mistress": "Schoolmistress",
    "Coach Maker": "Coachmaker",
    "Railway Station Master": "Railway Stationmaster",
    "Ship Builder": "Shipbuilder",
    "House Builder": "Housebuilder",
    "Brick Maker": "Brickmaker",
    "Time Keeper": "Timekeeper",
    "Care Taker": "Caretaker",
    "Clock Maker": "Clockmaker",
    "Cabinet Maker": "Cabinetmaker",
    "Cabnet Maker": "Cabinetmaker",
    "Shoe Maker": "Shoemaker",
    "Book Keeper": "Bookkeeper",
    "Ship Wright": "Shipwright",
    "Dress Maker": "Dressmaker",
    "Black Smith": "Blacksmith",
    "Paper Hanger": "Paperhanger",
    "Stone Mason": "Stonemason",
    "Gold Smith": "Goldsmith",
    "Tin Smith": "Tinsmith",
    "White Smith": "Whitesmith",
    "Mill Wright": "Millwright",
    "Police Man": "Policeman",
    "Milk Man": "Milkman",
    "Bar Man": "Barman",
    "Bar Maid": "Barmaid",
    "Rope Maker": "Ropemaker",
    "Lace Maker": "Lacemaker",
    "Hair Dresser": "Hairdresser",
    "News Agent": "Newsagent",
    "Station Master": "Stationmaster",
    "Post Master": "Postmaster",
    "Post Mistress": "Postmistress",
    "Brick Layer": "Bricklayer",
    "Fisher Man": "Fisherman",
    "Iron Monger": "Ironmonger",
    "Post Man": "Postman",
    "House Maid": "Housemaid",
    "Silver Smith": "Silversmith",
    "Coach Man": "Coachman",
    "Wheel Wright": "Wheelwright",
    "Watch Man": "Watchman",
    "House Work": "Housework",
    "Land Agents Assistant": "Land Agent's Assistant",
    "Hous Wife": "Housewife",
    "House Wife": "Housewife",
    "Farms Servant": "Farm Servant",
    "Paper Maker": "Papermaker",
    "Boat Builder": "Boat Builder",
    # Servant variations
    "General Servant Domestic": "General Domestic Servant",
    "Domestic General Servant": "General Domestic Servant",
    "General Servant, Domestic": "General Domestic Servant",
    "Domestic Servant, General": "General Domestic Servant",
    "Domestic Servant General": "General Domestic Servant",
    "General Servt Domestic": "General Domestic Servant",
    "Genl Servant Domestic": "General Domestic Servant",
    "Gen Servant Domestic": "General Domestic Servant",
    "G Servant Domestic": "General Domestic Servant",
    "Servant Domestic": "Domestic Servant",
    "Domestic Servant Cook": "Cook Domestic Servant",
    "Servant (Domestic)": "Domestic Servant",
    "Domestic Servt": "Domestic Servant",
    "Dom Servant": "Domestic Servant",
    "D Servant": "Domestic Servant",
    "Genl. Servant Domestic": "General Domestic Servant",
    "Domestic Servent": "Domestic Servant",
    "Domestic Serveant": "Domestic Servant",
    "Domestick Servant": "Domestic Servant",
    "Domestic servant": "Domestic Servant",
    "Domest Servant": "Domestic Servant",
    "General Servent": "General Servant",
    "Genl Servt Domestic": "General Domestic Servant",
    "General Domestic Servt": "General Domestic Servant",
    "General Servt. Domestic": "General Domestic Servant",
    "Housemaid Domestic Servt": "Housemaid Domestic Servant",
    "Coachman Domestic Servt": "Coachman Domestic Servant",
    "Gardener Domestic Servt": "Gardener Domestic Servant",
    "Farm Servt": "Farm Servant",
    "Nurse Domestic Servt": "Nurse Domestic Servant",
    "Cook Domestic Servt": "Cook Domestic Servant",
    "Domestic Servant House Maid": "Housemaid Domestic Servant",
    "Genl Servant": "General Servant",
    "General Servt": "General Servant",
    "Gen Servant": "General Servant",
    "Genl Domestic Servant": "General Domestic Servant",
    # American to British spelling
    "Agricultural Laborer": "Agricultural Labourer",
    "Farm Laborer": "Farm Labourer",
    "General Laborer": "General Labourer",
    "Laborer": "Labourer",
    # Order corrections
    "Labourer General": "General Labourer",
    "Labourer Agricultural": "Agricultural Labourer",
    "Labourer, General": "General Labourer",
    "Labourer, Agricultural": "Agricultural Labourer",
    "Agricultural Labourer General": "General Agricultural Labourer",
    "Clerk Bank": "Bank Clerk",
    "Clerk Railway": "Railway Clerk",
    "Clerk Post Office": "Post Office Clerk",
    "Porter Railway": "Railway Porter",
    "Labourer Dock": "Dock Labourer",
    "Labourer Road": "Road Labourer",
    "Labourer Railway": "Railway Labourer",
    "Labourer Farm": "Farm Labourer",
    "Laborer General": "General Labourer",
    "Labourer Quay": "Quay Labourer",
    "Labourer Agl": "Agricultural Labourer",
    "Labourer Gen": "General Labourer",
    "Weaver Linen": "Linen Weaver",
    "Dealer General": "General Dealer",
    "Tailor Master": "Master Tailor",
    # Common spelling corrections
    "Sempstress": "Seamstress",
    "Seamstres": "Seamstress",
    "Seamtress": "Seamstress",
    "Seamsteress": "Seamstress",
    "Seamestress": "Seamstress",
    "Seamsterss": "Seamstress",
    "Seamistress": "Seamstress",
    "Semstress": "Seamstress",
    "Seanstress": "Seamstress",
    "Cleark": "Clerk",
    "Clarke": "Clerk",
    "Clerke": "Clerk",
    "Clerkess": "Clerk",
    "Plumer": "Plumber",
    "Shomaker": "Shoemaker",
    "Miliner": "Milliner",
    "Millner": "Milliner",
    "Laundres": "Laundress",
    "Aprentice": "Apprentice",
    "Serveant": "Servant",
    "At Chool": "At School",
    "Farm Serveant": "Farm Servant",
    "Farme Servant": "Farm Servant",
    "Buttler": "Butler",
    "Quay Labour": "Quay Labourer",
    "Shool Boy": "School Boy",
    "Frame Maker": "Framemaker",
    "Farm Laborour": "Farm Labourer",
    "Genl Labour": "General Labourer",
    "Grocers Manager": "Grocer's Manager",
    "Railway Labour": "Railway Labourer",
    "Scool Boy": "School Boy",
    # From Batch 2
    "Gardner": "Gardener",
    "Gardner Domestic Servant": "Gardener Domestic Servant",
    "Gardiner": "Gardener",
    "Atending School": "Attending School",
    "Bookeeper": "Bookkeeper",
    "No Buisness": "No Business",
    # Scholar variants
    "Scholars": "Scholar",
    "Schollar": "Scholar",
    "Scolar": "Scholar",
    "Scholoar": "Scholar",
    "Scholors": "Scholar",
    "Schollars": "Scholar",
    "Schoolar": "Scholar",
    "Scohlar": "Scholar",
    "Scoller": "Scholar",
    "Scollor": "Scholar",
    "Scollar": "Scholar",
    "Scholor": "Scholar",
    "Scholler": "Scholar",
    "Schol": "Scholar",
    "Sholars": "Scholar",
    "Shollar": "Scholar",
    "Sholar": "Scholar",
    "Sclolar": "Scholar",
    "Scoholar": "Scholar",
    "Scholare": "Scholar",
    "Scholour": "Scholar",
    "Schlar": "Scholar",
    "Schalor": "Scholar",
    "Scholl": "Scholar",
    "Shool": "Scholar",
    "Scoolar": "Scholar",
    "Shoolar": "Scholar",
    # Labourer variants
    "Labourers": "Labourer",
    "Laborour": "Labourer",
    "Labrour": "Labourer",
    "Laboror": "Labourer",
    "Laberour": "Labourer",
    "Labouer": "Labourer",
    "Labour": "Labourer",
    "Labours": "Labourer",
    "Labiour": "Labourer",
    "Labouring": "Labourer",
    "Labrourer": "Labourer",
    "Laburer": "Labourer",
    "Genl Laborer": "General Labourer",
    # Order corrections
    "Labourer Agr": "Agricultural Labourer",
    "Labourer Brewery": "Brewery Labourer",
    "Labourer Ship Yard": "Ship Yard Labourer",
    # Abbreviations
    "Agl Labourer": "Agricultural Labourer",
    "Agrl Labourer": "Agricultural Labourer",
    "Agr Labourer": "Agricultural Labourer",
    "Agr. Labourer": "Agricultural Labourer",
    "Agrl. Labourer": "Agricultural Labourer",
    "Agl. Labourer": "Agricultural Labourer",
    "Agricl Labourer": "Agricultural Labourer",
    "Agric Labourer": "Agricultural Labourer",
    "Agri Labourer": "Agricultural Labourer",
    "Ag Labourer": "Agricultural Labourer",
    "Ag. Labourer": "Agricultural Labourer",
    "A Labourer": "Agricultural Labourer",
    "Agriculture Labourer": "Agricultural Labourer",
    "Agricultural Labour": "Agricultural Labourer",
    "Agricultural Labor": "Agricultural Labourer",
    "Agricultural Lab": "Agricultural Labourer",
    "Agricultural Labr": "Agricultural Labourer",
    "Agricultural Labrour": "Agricultural Labourer",
    "Agricultural Laberour": "Agricultural Labourer",
    "Agricultural Laboue": "Agricultural Labourer",
    "Agricultural Labouer": "Agricultural Labourer",
    "Agricultral Labourer": "Agricultural Labourer",
    "Agriculural Labourer": "Agricultural Labourer",
    "Agricutural Labourer": "Agricultural Labourer",
    "Agricult Labourer": "Agricultural Labourer",
    "Agricul Labourer": "Agricultural Labourer",
    "Agricultl Labourer": "Agricultural Labourer",
    "Agricultur Labourer": "Agricultural Labourer",
    "Genl Labourer": "General Labourer",
    "Genl. Labourer": "General Labourer",
    "Gen Labourer": "General Labourer",
    "G Labourer": "General Labourer",
    "Gl Labourer": "General Labourer",
    "General Laberour": "General Labourer",
    "General Labrour": "General Labourer",
    "General Laborour": "General Labourer",
    "Genral Labourer": "General Labourer",
    "Genrl Labourer": "General Labourer",
    "G. Labourer": "General Labourer",
    "N S Teacher": "National School Teacher",
    "N.S. Teacher": "National School Teacher",
    "N. S. Teacher": "National School Teacher",
    "NS Teacher": "National School Teacher",
    "Nat Teacher": "National Teacher",
    "Natl Teacher": "National Teacher",
    "National S Teacher": "National School Teacher",
    "Nat School Teacher": "National School Teacher",
    "Natl School Teacher": "National School Teacher",
    "N School Teacher": "National School Teacher",
    # Religious
    "R C Priest": "Roman Catholic Priest",
    "R.C. Priest": "Roman Catholic Priest",
    "RC Priest": "Roman Catholic Priest",
    "R C Clergyman": "Roman Catholic Clergyman",
    "R.C. Clergyman": "Roman Catholic Clergyman",
    "RC Clergyman": "Roman Catholic Clergyman",
    "Pensioner R.I.C.": "R.I.C. Pensioner",
    "Pensioner R.I.C": "R.I.C. Pensioner",
    # Other corrections
    "Coalminer": "Coal Miner",
    "Millworker": "Mill Worker",
    "Dressmaking": "Dressmaker",
    "House keeper": "Housekeeper",
    "Hous Keeper": "Housekeeper",
    "HouseKeeper": "Housekeeper",
    "Housekeper": "Housekeeper",
    "Huse Keeper": "Housekeeper",
    # Carpenter variants
    "Carpinter": "Carpenter",
    "Carpanter": "Carpenter",
    "Carpentar": "Carpenter",
    "Cartpenter": "Carpenter",
    "Corpenter": "Carpenter",
    "Carpender": "Carpenter",
    # All other established corrections
    "Famers Son": "Farmer's Son",
    "Farmers' Son": "Farmer's Son",
    "Market Gardner": "Market Gardener",
    "Gardner Domestic": "Gardener Domestic",
    "Plummer": "Plumber",
    "Salior": "Sailor",
    "Schloar": "Scholar",
    "At Shool": "At School",
    # Machinist
    "Machinest": "Machinist",
    "Machanist": "Machinist",
    "Machineist": "Machinist",
}

# Case-insensitive fallback: map lowercased key -> canonical key for lookup
CORRECTIONS_LOWER = {k.lower(): k for k in CORRECTIONS}

# Scholar variants: keys in CORRECTIONS that map to "Scholar" (for review output only; no pattern corrects these)
SCHOLAR_VARIANTS_LOWER = {k.lower() for k, v in CORRECTIONS.items() if v == "Scholar"}

# Pattern-based rules: (compiled_regex, replacement, change_category).
# Applied after normalization, before dict lookup. Order matters.
_POSSESSIVE_STEMS = (
    "Farmer",
    "Labourer",
    "Grocer",
    "Draper",
    "Tailor",
    "Mason",
    "Shepherd",
    "Herd",
    "Publican",
    "Dairyman",
    "Carpenter",
    "Blacksmith",
    "Baker",
    "Butcher",
    "Soldier",
    "Builder",
    "Chemist",
    "Teacher",
    "Policeman",
    "Printer",
    "Brewer",
    "Caretaker",
    "Fisherman",
    "Sailor",
    "Accountant",
    "Shoemaker",
    "Mill Owner",
)
_POSSESSIVE_RELATIONS = (
    r"Son|Daughter|Wife|Widow|Mother|Father|Brother|Sister|Nephew|Niece|"
    r"Servant|Assistant|Apprentice|Labourer|Clerk|Porter|Helper|Manager|"
    r"Daughter in Law|Son in Law|Mother in Law"
)
PATTERN_RULES: list[tuple[re.Pattern, str | Callable[..., str], str]] = [
    (
        re.compile(r"\bLabor(er)?\b", re.IGNORECASE),
        lambda m: "Labour" + (m.group(1) or ""),
        "AMERICAN_SPELLING",
    ),
    (re.compile(r"\bServt\.?\b", re.IGNORECASE), "Servant", "ABBREVIATION"),
    (
        re.compile(
            r"\b(" + "|".join(re.escape(s) for s in _POSSESSIVE_STEMS) + r")s ("
            + _POSSESSIVE_RELATIONS + r")\b",
            re.IGNORECASE,
        ),
        lambda m: m.group(1).title() + "'s " + m.group(2).title(),
        "POSSESSIVE",
    ),
    # Word-order: "Domestic Servant General" → "General Domestic Servant" (before Servant Domestic)
    (
        re.compile(r"\bDomestic\s+Servant\s+General\b", re.IGNORECASE),
        "General Domestic Servant",
        "WORD_ORDER",
    ),
    # Word-order: "Servant Domestic" → "Domestic Servant"
    (
        re.compile(r"\bServant\s+Domestic\b", re.IGNORECASE),
        "Domestic Servant",
        "WORD_ORDER",
    ),
    # Labourer X → X Labourer
    (
        re.compile(
            r"\bLabourer\s+(General|Agricultural|Farm|Dock|Road|Railway|Quay|Brewery|Ship\s+Yard)\b",
            re.IGNORECASE,
        ),
        lambda m: m.group(1).title() + " Labourer",
        "LABOURER_ORDER",
    ),
    # Compound X Keeper
    (
        re.compile(r"\b(House|Shop|Store|Gate|Time|Book)\s+Keeper\b", re.IGNORECASE),
        lambda m: m.group(1).title() + "keeper",
        "COMPOUND_KEEPER",
    ),
    # Agricultural abbreviation (unambiguous): Agl, Agrl, Agr, etc. + Labourer
    (
        re.compile(
            r"\b(Agl|Agrl|Agr|Agricl|Agric|Agri|Ag)\.?\s+Labourer\b",
            re.IGNORECASE,
        ),
        "Agricultural Labourer",
        "AGRICULTURAL_ABBREVIATION",
    ),
    # General abbreviation (unambiguous): Genl, Gen, etc. + Labourer
    (
        re.compile(
            r"\b(Genl|Gen|Genral|Genrl|Gl)\.?\s+Labourer\b",
            re.IGNORECASE,
        ),
        "General Labourer",
        "GENERAL_ABBREVIATION",
    ),
    # Ambiguous: "A Labourer" → Agricultural Labourer (for review)
    (
        re.compile(r"\bA\s+Labourer\b", re.IGNORECASE),
        "Agricultural Labourer",
        "ABBREVIATION_AMBIGUOUS",
    ),
    # Ambiguous: "G Labourer" / "G. Labourer" → General Labourer (for review)
    (
        re.compile(r"\bG\.?\s+Labourer\b", re.IGNORECASE),
        "General Labourer",
        "ABBREVIATION_AMBIGUOUS",
    ),
]


def _normalize(s: str) -> str:
    """Remove brackets, treat '-' as space, condense whitespace (per occupation.md)."""
    s = str(s).strip()
    s = re.sub(r"[\[\]()]", "", s)
    s = s.replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


def correct_occupation_final(occupation: str, max_passes: int = 3) -> tuple[str, str]:
    """Apply occupation corrections; return (corrected_occupation, change_category)."""
    if not occupation or (isinstance(occupation, float) and pd.isna(occupation)):
        return ("", "UNCHANGED")

    original = str(occupation).strip()
    categories: set[str] = set()

    corrected = _normalize(occupation)
    if corrected != original:
        categories.add("NORMALIZATION")

    for _ in range(max_passes):
        prev = corrected
        # Apply pattern-based rules (Labor→Labour, Servt→Servant, Xs Y→X's Y)
        for pattern, repl, category in PATTERN_RULES:
            new = pattern.sub(repl, corrected)
            if new != corrected:
                categories.add(category)
                corrected = new
        if corrected in CORRECTIONS:
            corrected = CORRECTIONS[corrected]
            categories.add("DICT_LOOKUP")
        elif corrected.lower() in CORRECTIONS_LOWER:
            canonical_key = CORRECTIONS_LOWER[corrected.lower()]
            corrected = CORRECTIONS[canonical_key]
            categories.add("DICT_LOOKUP")
        if corrected == prev:
            break

    if corrected == original:
        change_category = "UNCHANGED"
    elif categories:
        change_category = "; ".join(sorted(categories))
    else:
        change_category = "UNCHANGED"

    return (corrected, change_category)


def main() -> None:
    print("Loading CSV ...", flush=True)
    df = pd.read_csv(CSV_PATH, encoding="utf-8").dropna(how="all")
    print(f"  Loaded {len(df)} rows.", flush=True)

    print("Applying corrections (normalize + dict + patterns) ...", flush=True)
    df = df.copy()
    result = df["occupation"].map(correct_occupation_final)
    df["corrected_occupation"] = result.map(lambda x: x[0])
    df["change_category"] = result.map(lambda x: x[1])
    print("  Done.", flush=True)

    print("Sorting and writing main output ...", flush=True)
    df["_sort_count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype("int64")
    df["_occ_lower"] = df["occupation"].str.lower()
    df = df.sort_values(by=["_sort_count", "_occ_lower"], ascending=[False, True]).drop(
        columns=["_sort_count", "_occ_lower"]
    )
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"  Wrote {len(df)} rows to {OUTPUT_PATH}", flush=True)

    print("Writing changed/unchanged splits ...", flush=True)
    df["_sort_count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype("int64")
    df["_occ_lower"] = df["occupation"].str.lower()

    changed = df[df["occupation"] != df["corrected_occupation"]].copy()
    changed = changed.sort_values(by=["_sort_count", "_occ_lower"], ascending=[False, True]).drop(
        columns=["_sort_count", "_occ_lower"]
    )
    changed.to_csv(OUTPUT_CHANGED_PATH, index=False, encoding="utf-8")
    print(f"  Wrote {len(changed)} rows (changed) to {OUTPUT_CHANGED_PATH}", flush=True)

    unchanged = df[df["occupation"] == df["corrected_occupation"]].copy()
    unchanged = unchanged.sort_values(by=["_sort_count", "_occ_lower"], ascending=[False, True]).drop(
        columns=["_sort_count", "_occ_lower"]
    )
    unchanged.to_csv(OUTPUT_UNCHANGED_PATH, index=False, encoding="utf-8")
    print(f"  Wrote {len(unchanged)} rows (unchanged) to {OUTPUT_UNCHANGED_PATH}", flush=True)

    print("Writing Scholar review ...", flush=True)
    scholar_review = df[
        df["occupation"].str.strip().str.lower().isin(SCHOLAR_VARIANTS_LOWER)
    ].copy()
    scholar_review = scholar_review.sort_values(
        by=["_sort_count", "_occ_lower"], ascending=[False, True]
    ).drop(columns=["_sort_count", "_occ_lower"])
    scholar_review.to_csv(OUTPUT_SCHOLAR_REVIEW_PATH, index=False, encoding="utf-8")
    print(f"  Wrote {len(scholar_review)} rows (Scholar variants) to {OUTPUT_SCHOLAR_REVIEW_PATH}", flush=True)

    print("Spellcheck review ...", flush=True)
    if has_word_list():
        print("  Identifying rows with unknown words ...", flush=True)
        unknown_per_row = df["corrected_occupation"].map(unknown_words_in_text)
        has_unknown = unknown_per_row.map(len) > 0
        spellcheck_review = df[has_unknown].copy()
        spellcheck_review["unknown_words"] = unknown_per_row[has_unknown].map(lambda w: "; ".join(w))
        print(f"  Computing suggestions for {len(spellcheck_review)} rows (may take a while) ...", flush=True)
        spellcheck_review["suggested_occupation"] = spellcheck_review["corrected_occupation"].map(
            suggest_spellcorrected
        )
        print("  Sorting and writing spellcheck review ...", flush=True)
        spellcheck_review = spellcheck_review.sort_values(
            by=["_sort_count", "_occ_lower"], ascending=[False, True]
        ).drop(columns=["_sort_count", "_occ_lower"])
        spellcheck_review.to_csv(OUTPUT_SPELLCHECK_REVIEW_PATH, index=False, encoding="utf-8")
        print(f"  Wrote {len(spellcheck_review)} rows (spellcheck review) to {OUTPUT_SPELLCHECK_REVIEW_PATH}", flush=True)
    else:
        print(
            "  Skipped (no word list in archives/dict/words; run python archives/dict/words/fetch_english_words.py)",
            flush=True,
        )


if __name__ == "__main__":
    main()
