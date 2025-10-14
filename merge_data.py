# src/merge_datasets.py
"""
Merge all labeled datasets into one training file:
 - scans data/*_labeled.csv (EDGAR, GDELT, etc.)
 - harmonizes columns
 - de-duplicates
 - writes data/all_sources_labeled.csv

Expected columns (if present):
  ticker, date, form, url, title, snippet, price_t0, ret_3d, label_3d, ret_5d, label_5d, source
Missing columns are filled with sensible defaults.
"""

import glob
import os
import sys
import pandas as pd

DATA_DIR = "data"
OUT_FILE = os.path.join(DATA_DIR, "all_sources_labeled.csv")

REQUIRED = [
    "ticker", "date", "form", "url", "title", "snippet",
    "price_t0", "ret_3d", "label_3d", "ret_5d", "label_5d", "source",
]

def coerce_cols(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = df.copy()

    # Normalize common column name variants
    # (Feel free to extend if your other pipelines produce different names)
    rename_map = {
        "Price_t0": "price_t0",
        "price0": "price_t0",
        "text": "snippet",
        "link": "url",
        "doc_url": "url",
        "headline": "title",
        "form_base": "form",
    }
    for k, v in rename_map.items():
        if k in df.columns and v not in df.columns:
            df.rename(columns={k: v}, inplace=True)

    # Ensure all required columns exist
    for c in REQUIRED:
        if c not in df.columns:
            df[c] = None

    # Coerce types
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["form"] = df["form"].astype(str).str.strip()
    df["url"] = df["url"].astype(str).str.strip()
    df["title"] = df["title"].astype(str)
    df["snippet"] = df["snippet"].astype(str)

    # Date parsing
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Numeric returns / price
    for num in ["price_t0", "ret_3d", "ret_5d"]:
        df[num] = pd.to_numeric(df[num], errors="coerce")

    # Labels normalized to "UP"/"DOWN" (leave None if missing)
    for lab in ["label_3d", "label_5d"]:
        df[lab] = (
            df[lab]
            .astype(str)
            .str.upper()
            .replace({"1": "UP", "UPWARD": "UP", "DOWNWARD": "DOWN", "TRUE": "UP", "FALSE": "DOWN"})
        )
        df.loc[~df[lab].isin(["UP", "DOWN"]), lab] = None

    # Source tag
    if "source" not in df.columns or df["source"].isna().all():
        df["source"] = source_name

    # Keep just the required cols in the right order
    return df[REQUIRED]


def main():
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*_labeled.csv")))
    if not paths:
        print("No *_labeled.csv files found in data/. Nothing to merge.")
        sys.exit(0)

    print("Merging the following files:")
    for p in paths:
        print("  -", os.path.basename(p))

    frames = []
    for p in paths:
        src = os.path.basename(p).replace("_labeled.csv", "")
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"  ! Skipping {p}: {e}")
            continue
        frames.append(coerce_cols(df, source_name=src))

    if not frames:
        print("No valid files to merge after parsing.")
        sys.exit(0)

    all_df = pd.concat(frames, ignore_index=True)

    # Drop rows without a date or ticker
    all_df = all_df.dropna(subset=["date", "ticker"])

    # Sort and de-duplicate
    all_df = all_df.sort_values(["ticker", "date", "form", "url"], kind="stable")
    all_df = all_df.drop_duplicates(subset=["ticker", "date", "form", "url"], keep="first")

    # Quick summary
    by_src = all_df["source"].value_counts()
    print("\nRows by source:\n", by_src.to_string())
    print("\nLabel balance (3d):\n", all_df["label_3d"].value_counts(dropna=False).to_string())
    print("\nDate range:", all_df["date"].min(), "→", all_df["date"].max())

    # Write
    os.makedirs(DATA_DIR, exist_ok=True)
    all_df.to_csv(OUT_FILE, index=False)
    print(f"\n✅ Wrote {len(all_df):,} rows to {OUT_FILE}")

if __name__ == "__main__":
    main()

