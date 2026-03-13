"""
One-off script: frequency of words from words_british.txt + words_manual.txt in the
occupation column of ire_occupation_1901.csv. Outputs a CSV of word, frequency
(weighted by row count).
"""

import re
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
WORDS_BRITISH_PATH = SCRIPT_DIR / "words_british.txt"
WORDS_MANUAL_PATH = SCRIPT_DIR / "words_manual.txt"
# Census occupations CSV (with occupation, count columns)
CSV_PATH = SCRIPT_DIR.parent / "census" / "ireland" / "prompts" / "ire_occupation_1901.csv"
OUTPUT_PATH = SCRIPT_DIR / "words_british_occupation_frequency.csv"


# Acronym pattern: one or more "letter." segments, optionally ending with "letter" (no trailing dot)
_ACRONYM_RE = re.compile(r"^[a-zA-Z](\.[a-zA-Z])*\.?$")


def _acronym_variants(word: str) -> set[str]:
    """Return word and variant without trailing dot so tokenized 'R.I.C.' matches 'r.i.c.' in list."""
    s = word.strip().lower()
    if not s or "." not in s:
        return {s}
    out = {s}
    if s.endswith(".") and _ACRONYM_RE.match(s):
        out.add(s[:-1])  # "r.i.c." -> also add "r.i.c"
    return out


def tokenize_occupation(text: str) -> list[str]:
    """Lowercase tokens, strip leading/trailing non-letters (keep apostrophe in token)."""
    if not isinstance(text, str) or not text.strip():
        return []
    tokens = re.findall(r"[^\s]+", text)
    return [
        re.sub(r"^[^\w']+|[^\w']+$", "", t).lower()
        for t in tokens
        if any(c.isalpha() for c in t)
    ]


def main() -> None:
    print("Loading word list (words_british + words_manual) ...", flush=True)
    british_words: set[str] = set()
    for w in WORDS_BRITISH_PATH.read_text(encoding="utf-8").splitlines():
        if w.strip():
            british_words |= _acronym_variants(w)
    manual_words: set[str] = set()
    for w in WORDS_MANUAL_PATH.read_text(encoding="utf-8").splitlines():
        if w.strip():
            manual_words |= _acronym_variants(w)
    all_words = british_words | manual_words
    print(f"  British: {len(british_words)}, manual: {len(manual_words)}, combined: {len(all_words)} words.", flush=True)

    print("Loading occupations CSV ...", flush=True)
    df = pd.read_csv(CSV_PATH.resolve(), encoding="utf-8")
    if "count" not in df.columns or "occupation" not in df.columns:
        raise SystemExit("CSV must have 'occupation' and 'count' columns.")
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype("int64")
    print(f"  Loaded {len(df)} rows.", flush=True)

    print("Counting word frequencies in occupations ...", flush=True)
    freq: dict[str, int] = {w: 0 for w in all_words}
    for _, row in df.iterrows():
        occ = row["occupation"]
        cnt = int(row["count"])
        for token in tokenize_occupation(str(occ)):
            if token in all_words:
                freq[token] += cnt

    # Ensure every dictionary word has minimum frequency 1
    for w in all_words:
        if freq[w] < 1:
            freq[w] = 1

    print("Writing frequency CSV ...", flush=True)
    out = (
        pd.DataFrame([(w, c) for w, c in freq.items()], columns=["word", "frequency"])
        .sort_values("frequency", ascending=False)
        .reset_index(drop=True)
    )
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"  Wrote {len(out)} words to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
