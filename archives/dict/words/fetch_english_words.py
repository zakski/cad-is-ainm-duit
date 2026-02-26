#!/usr/bin/env python3
"""
Fetch the dwyl/english-words word list once and store under archives/dict.

Downloads words_alpha.txt from https://github.com/dwyl/english-words, then
converts American spellings to British via the breame package and writes
words_british.txt. Run from project root or archives/dict:

  python archives/dict/fetch_english_words.py

Requires: breame (pip install breame)
"""

import urllib.request
from pathlib import Path

WORDS_ALPHA_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
SCRIPT_DIR = Path(__file__).resolve().parent
WORDS_ALPHA_PATH = SCRIPT_DIR / "words_alpha.txt"
WORDS_BRITISH_PATH = SCRIPT_DIR / "words_british.txt"


def main() -> None:
    if not WORDS_ALPHA_PATH.exists():
        print(f"Downloading {WORDS_ALPHA_URL} ...")
        urllib.request.urlretrieve(WORDS_ALPHA_URL, WORDS_ALPHA_PATH)
        print(f"Saved to {WORDS_ALPHA_PATH}")
    else:
        print(f"Using existing {WORDS_ALPHA_PATH}")

    from breame.spelling import get_british_spelling

    words = [
        line.strip().lower()
        for line in WORDS_ALPHA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    print(f"Converting {len(words)} words to British spelling ...")
    british = set()
    for i, w in enumerate(words):
        try:
            bw = get_british_spelling(w)
            british.add(bw.lower() if bw else w)
        except Exception:
            british.add(w)
        if (i + 1) % 50000 == 0:
            print(f"  {i + 1}/{len(words)}")
    WORDS_BRITISH_PATH.write_text("\n".join(sorted(british)), encoding="utf-8")
    print(f"Wrote {len(british)} words to {WORDS_BRITISH_PATH}")


if __name__ == "__main__":
    main()
