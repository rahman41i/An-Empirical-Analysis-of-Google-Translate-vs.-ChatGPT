"""
01b_parse_manual_trends_export.py

FALLBACK for when pytrends gets 429-blocked (very common on Colab / shared IPs).

Instead of hitting the Trends API programmatically, export CSVs manually from
https://trends.google.com/trends/explore in your browser (see chat instructions),
then point this script at the downloaded file(s) to convert them into the same
schema that 04_merge_and_process.py expects (matching 01_extract_google_trends.py's
output columns).

Usage:
    Put your downloaded CSV(s) in ./manual_exports/, e.g.:
        ./manual_exports/multiTimeline.csv
        ./manual_exports/multiTimeline_2.csv
    Then run:
        python 01b_parse_manual_trends_export.py

Requires: pip install pandas --break-system-packages
"""

import pandas as pd
import glob
import os

INPUT_DIR = "./manual_exports"
OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_manual_export(filepath):
    """
    Google's manual export format looks like:

        Category: All categories

        Week,Google Translate: (Worldwide),ChatGPT: (Worldwide),DeepL: (Worldwide)
        2021-07-25,63,0,5
        ...

    First 2 lines are metadata, so we skip them and read from the real header row.
    Column names have ': (Worldwide)' suffixes that need stripping.
    """
    df = pd.read_csv(filepath, skiprows=2)

    # first column is the date column, may be named "Week" or "Month" or "Day"
    date_col = df.columns[0]
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"])

    # clean term columns: "Google Translate: (Worldwide)" -> "Google Translate"
    rename_map = {}
    for col in df.columns:
        if col == "date":
            continue
        clean_name = col.split(":")[0].strip()
        rename_map[col] = clean_name
    df = df.rename(columns=rename_map)

    return df


def main():
    files = glob.glob(f"{INPUT_DIR}/*.csv")
    if not files:
        print(f"No CSV files found in {INPUT_DIR}/. "
              f"Download from trends.google.com/trends/explore and place them there.")
        return

    all_frames = []
    for f in files:
        print(f"Parsing {f}...")
        df = parse_manual_export(f)
        all_frames.append(df)
        print(f"  Found columns: {list(df.columns)}, {len(df)} rows")

    # Merge all files on date (outer join, since different files may cover
    # different term groups / date ranges)
    combined = all_frames[0]
    for df in all_frames[1:]:
        combined = combined.merge(df, on="date", how="outer")

    combined = combined.sort_values("date")
    combined.to_csv(f"{OUTPUT_DIR}/google_trends_raw.csv", index=False)
    print(f"\nSaved combined file to {OUTPUT_DIR}/google_trends_raw.csv "
          f"({len(combined)} rows, columns: {list(combined.columns)})")
    print("This file has the same schema 04_merge_and_process.py expects -- "
          "you can now run that script normally.")


if __name__ == "__main__":
    main()
