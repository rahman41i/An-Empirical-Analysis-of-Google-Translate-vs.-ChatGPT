"""
04_merge_and_process.py

Merges Google Trends, Wikipedia pageviews, app review volume, and
manual milestones into a single monthly panel dataset ready for analysis.

Requires: pip install pandas numpy --break-system-packages
Run after 01, 02, 03 have produced their raw CSVs in ./data/
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = "./data"


def load_trends():
    df = pd.read_csv(f"{DATA_DIR}/google_trends_raw.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    # melt wide (one column per term) into long format
    value_cols = [c for c in df.columns if c not in ("timeframe_label",)]
    long_df = df[value_cols].reset_index().melt(
        id_vars="date", var_name="entity", value_name="trends_index"
    )
    long_df["month"] = long_df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = long_df.groupby(["month", "entity"], as_index=False)["trends_index"].mean()
    return monthly


def load_pageviews():
    df = pd.read_csv(f"{DATA_DIR}/wikipedia_pageviews_raw.csv")
    df["month"] = pd.to_datetime(df["timestamp"].astype(str).str[:6], format="%Y%m")
    df = df.rename(columns={"article": "entity", "views": "wiki_pageviews"})
    monthly = df.groupby(["month", "entity"], as_index=False)["wiki_pageviews"].sum()
    return monthly


def load_reviews():
    df = pd.read_csv(f"{DATA_DIR}/app_reviews_raw.csv")
    df["at"] = pd.to_datetime(df["at"])
    df["month"] = df["at"].dt.to_period("M").dt.to_timestamp()
    df = df.rename(columns={"app_label": "entity"})
    monthly = df.groupby(["month", "entity"], as_index=False).agg(
        review_count=("content", "count"),
        avg_rating=("score", "mean"),
    )
    return monthly


def zscore(series):
    return (series - series.mean()) / series.std(ddof=0)


def main():
    frames = {}
    if os.path.exists(f"{DATA_DIR}/google_trends_raw.csv"):
        frames["trends"] = load_trends()
    if os.path.exists(f"{DATA_DIR}/wikipedia_pageviews_raw.csv"):
        frames["pageviews"] = load_pageviews()
    if os.path.exists(f"{DATA_DIR}/app_reviews_raw.csv"):
        frames["reviews"] = load_reviews()

    if not frames:
        print("No raw data found. Run scripts 01-03 first (on a machine with internet access).")
        return

    # Start from whichever frame has the broadest month range, then join others
    base = None
    for name, df in frames.items():
        if base is None:
            base = df
        else:
            base = base.merge(df, on=["month", "entity"], how="outer")

    base = base.sort_values(["entity", "month"])

    # Normalize each numeric metric within each entity (z-score) for comparability
    for col in ["trends_index", "wiki_pageviews", "review_count"]:
        if col in base.columns:
            base[f"{col}_z"] = base.groupby("entity")[col].transform(zscore)

    # Attach milestone flags
    milestones = pd.read_csv("./data_milestones_manual.csv")
    milestones["date"] = pd.to_datetime(milestones["date"])
    milestones["month"] = milestones["date"].dt.to_period("M").dt.to_timestamp()

    base["chatgpt_era"] = base["month"] >= pd.Timestamp("2022-11-01")

    base.to_csv(f"{DATA_DIR}/master_dataset.csv", index=False)
    milestones.to_csv(f"{DATA_DIR}/milestones_processed.csv", index=False)
    print(f"Master dataset saved: {DATA_DIR}/master_dataset.csv ({len(base)} rows)")


if __name__ == "__main__":
    main()
