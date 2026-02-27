#!/usr/bin/env python3
"""Remove from words_manual.txt any line that appears in words_british.txt."""
import sys

def main():
    british_path = "words_british.txt"
    manual_path = "words_manual.txt"
    out_path = "words_manual.tmp"

    print("Loading words_british.txt into set...", file=sys.stderr)
    with open(british_path, "r", encoding="utf-8") as f:
        british = set(line.rstrip("\n") for line in f)
    print(f"  {len(british)} lines", file=sys.stderr)

    print("Filtering words_manual.txt...", file=sys.stderr)
    kept = 0
    with open(manual_path, "r", encoding="utf-8") as fin:
        with open(out_path, "w", encoding="utf-8") as fout:
            for line in fin:
                word = line.rstrip("\n")
                if word not in british:
                    fout.write(line)
                    kept += 1
    print(f"  Kept {kept} lines", file=sys.stderr)

    import os
    os.replace(out_path, manual_path)
    print("Done. words_manual.txt updated.", file=sys.stderr)

if __name__ == "__main__":
    main()
