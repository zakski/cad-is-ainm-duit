"""
One-off script: frequency of words from words_british.txt in the occupation column
of ire_occupation_1901.csv. Outputs a CSV of word, frequency (weighted by row count).
"""

import re
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
WORDS_PATH = SCRIPT_DIR / "words_british.txt"
# Census occupations CSV (with occupation, count columns)
CSV_PATH = SCRIPT_DIR.parent / "census" / "ireland" / "prompts" / "ire_occupation_1901.csv"
OUTPUT_PATH = SCRIPT_DIR / "words_british_occupation_frequency.csv"


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
    print("Loading British word list ...", flush=True)
    british_words = {
        w.strip().lower()
        for w in WORDS_PATH.read_text(encoding="utf-8").splitlines()
        if w.strip()
    }
    print(f"  Loaded {len(british_words)} words.", flush=True)

    print("Loading occupations CSV ...", flush=True)
    df = pd.read_csv(CSV_PATH.resolve(), encoding="utf-8")
    if "count" not in df.columns or "occupation" not in df.columns:
        raise SystemExit("CSV must have 'occupation' and 'count' columns.")
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype("int64")
    print(f"  Loaded {len(df)} rows.", flush=True)

    print("Counting word frequencies in occupations ...", flush=True)
    freq: dict[str, int] = {w: 0 for w in british_words}
    for _, row in df.iterrows():
        occ = row["occupation"]
        cnt = int(row["count"])
        for token in tokenize_occupation(str(occ)):
            if token in british_words:
                freq[token] += cnt

    # Ensure every dictionary word has minimum frequency 1
    for w in british_words:
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
