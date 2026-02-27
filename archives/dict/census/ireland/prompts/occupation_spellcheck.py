"""
Spellcheck utilities for occupation strings.

Loads the British English word list from archives/dict/words/words_british.txt,
strips possessives before checking/suggesting, and uses pyspellchecker for
correction suggestions. Create the word list once with:
  python archives/dict/words/fetch_english_words.py
"""

import re
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_ARCHIVES_DICT = _SCRIPT_DIR.parent.parent.parent
WORDS_BRITISH_PATH = _ARCHIVES_DICT / "words" / "words_british.txt"
# Occupation-weighted frequency (word -> count); used by SpellChecker via load_json for better suggestions
WORDS_FREQUENCY_CSV_PATH = _ARCHIVES_DICT / "words" / "words_british_occupation_frequency.csv"

_SPELL_CHECKER = None
_SUGGEST_CACHE: dict[str, str] = {}


def _load_british_word_set() -> set[str]:
    """Load British word set from frequency CSV if present, else words_british.txt."""
    if WORDS_FREQUENCY_CSV_PATH.exists():
        print("  [spellcheck] Loading word list from words_british_occupation_frequency.csv ...", flush=True)
        import pandas as pd
        freq_df = pd.read_csv(WORDS_FREQUENCY_CSV_PATH, encoding="utf-8")
        words = set(freq_df["word"].astype(str).str.strip().str.lower())
        words.discard("")
        print(f"  [spellcheck] Loaded {len(words)} words.", flush=True)
        return words
    if not WORDS_BRITISH_PATH.exists():
        print("  [spellcheck] No words_british.txt or frequency CSV found; spellcheck disabled.", flush=True)
        return set()
    print("  [spellcheck] Loading British word list from words_british.txt ...", flush=True)
    words = {
        w.strip().lower()
        for w in WORDS_BRITISH_PATH.read_text(encoding="utf-8").splitlines()
        if w.strip()
    }
    print(f"  [spellcheck] Loaded {len(words)} words.", flush=True)
    return words


BRITISH_WORDS: set[str] = _load_british_word_set()


def has_word_list() -> bool:
    """Return True if the British word list is available for spellcheck."""
    return bool(BRITISH_WORDS)


def _strip_possessive(word: str) -> tuple[str, str]:
    """If word ends with a possessive suffix ('s, s', or '), return (stem, suffix); else (word, '')."""
    if len(word) >= 2 and word.endswith("'s"):
        return word[:-2], "'s"
    if len(word) >= 2 and word.endswith("s'"):
        return word[:-2], "s'"
    if len(word) >= 1 and word.endswith("'"):
        return word[:-1], "'"
    return word, ""


def _get_spell_checker():
    """Return a SpellChecker loaded with frequency CSV (load_json) or words_british.txt (load_words), or None if unavailable."""
    global _SPELL_CHECKER
    if _SPELL_CHECKER is not None:
        return _SPELL_CHECKER
    if not BRITISH_WORDS:
        return None
    try:
        from spellchecker import SpellChecker
        import pandas as pd
        print("  [spellcheck] Initialising SpellChecker and loading dictionary ...", flush=True)
        _SPELL_CHECKER = SpellChecker(language=None)
        if WORDS_FREQUENCY_CSV_PATH.exists():
            freq_df = pd.read_csv(WORDS_FREQUENCY_CSV_PATH, encoding="utf-8")
            freq_dict = dict(zip(freq_df["word"].astype(str).str.strip().str.lower(), freq_df["frequency"].astype(int)))
            freq_dict = {k: v for k, v in freq_dict.items() if k}
            _SPELL_CHECKER.word_frequency.load_json(freq_dict)
            print(f"  [spellcheck] Dictionary loaded from frequency CSV ({len(freq_dict)} words).", flush=True)
        else:
            _SPELL_CHECKER.word_frequency.load_words(BRITISH_WORDS)
            print(f"  [spellcheck] Dictionary loaded ({len(BRITISH_WORDS)} words).", flush=True)
        return _SPELL_CHECKER
    except ImportError:
        print("  [spellcheck] pyspellchecker not installed; suggestions disabled.", flush=True)
        return None


def _spell_correct_word(spell, word: str) -> str | None:
    """Get spellchecker correction for word; try correction() then candidates() when correction returns same word (tie-breaking). Return None if no change."""
    for form in (word, word.lower()):
        corrected = spell.correction(form)
        if corrected and corrected.lower() != form.lower():
            return corrected.title() if form.islower() or form.istitle() else corrected
    # correction() can return the same word when candidates tie (e.g. no frequency in dict); use candidates()
    cands = spell.candidates(word) or spell.candidates(word.lower())
    if not cands:
        return None
    other = [c for c in cands if c.lower() != word.lower()]
    if not other:
        return None
    # Pick candidate with highest usage frequency, then alphabetically
    best = max(other, key=lambda c: (spell.word_usage_frequency(c) or 0, c))
    return best.title()


def unknown_words_in_text(text: str) -> list[str]:
    """Return list of words in text that are not in the British word set (stem checked after stripping possessive)."""
    if not text:
        return []
    tokens = re.findall(r"[^\s]+", str(text))
    unknown = []
    for t in tokens:
        word = re.sub(r"^[^\w']+|[^\w']+$", "", t)  # keep apostrophe for possessive stripping
        if not word or not any(c.isalpha() for c in word):
            continue
        stem, _ = _strip_possessive(word)
        if stem.lower() not in BRITISH_WORDS:
            unknown.append(word)
    return unknown


def suggest_spellcorrected(text: str) -> str:
    """Replace unknown words in text with pyspellchecker's best correction; strip possessive before check, add back after. Results are cached by input text."""
    if not text:
        return text
    cache = _SUGGEST_CACHE
    if text in cache:
        return cache[text]
    spell = _get_spell_checker()
    if spell is None:
        cache[text] = text
        return text
    tokens = re.findall(r"[^\s]+", str(text))
    result = []
    for t in tokens:
        word = re.sub(r"^[^\w']+|[^\w']+$", "", t)  # keep apostrophe in word for possessive
        if not word or not any(c.isalpha() for c in word):
            result.append(t)
            continue
        stem, poss_suffix = _strip_possessive(word)
        if stem.lower() in BRITISH_WORDS:
            result.append(t)
            continue
        corrected = _spell_correct_word(spell, stem)
        if corrected is not None:
            corrected = corrected + poss_suffix
            prefix = t[: t.index(word)] if word in t else ""
            suffix = t[t.index(word) + len(word) :] if word in t else ""
            result.append(prefix + corrected + suffix)
        else:
            result.append(t)
    out = " ".join(result)
    cache[text] = out
    return out
