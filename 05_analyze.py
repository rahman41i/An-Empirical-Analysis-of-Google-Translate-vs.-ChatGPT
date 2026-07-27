"""
05_analyze.py

Core analyses on the merged master_dataset.csv:
1. Pre/post ChatGPT (Nov 2022) segmented trend regression for Google Translate
2. Cross-correlation between Google Translate and ChatGPT search interest
3. Relative "share of attention" over time across entities
4. Change-point detection around known milestones

Requires:
  pip install pandas numpy statsmodels matplotlib ruptures --break-system-packages
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "./data"


def load_master():
    df = pd.read_csv(f"{DATA_DIR}/master_dataset.csv", parse_dates=["month"])
    return df


def segmented_trend(df, entity="Google Translate", metric="trends_index"):
    """Fit separate linear trends before/after Nov 2022 for one entity."""
    sub = df[df["entity"] == entity].dropna(subset=[metric]).sort_values("month")
    sub = sub.copy()
    sub["t"] = np.arange(len(sub))
    cutoff = sub["month"].searchsorted(pd.Timestamp("2022-11-01"))

    pre = sub.iloc[:cutoff]
    post = sub.iloc[cutoff:]

    results = {}
    for label, seg in [("pre_chatgpt", pre), ("post_chatgpt", post)]:
        if len(seg) < 3:
            results[label] = None
            continue
        coeffs = np.polyfit(seg["t"], seg[metric], 1)
        results[label] = {"slope": coeffs[0], "intercept": coeffs[1], "n_points": len(seg)}

    return results


def cross_correlation(df, entity_a="Google Translate", entity_b="ChatGPT",
                       metric="trends_index_z", max_lag=6):
    """Simple lagged cross-correlation between two entities' normalized series."""
    a = df[df["entity"] == entity_a].set_index("month")[metric]
    b = df[df["entity"] == entity_b].set_index("month")[metric]
    joined = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()

    lags = range(-max_lag, max_lag + 1)
    corrs = []
    for lag in lags:
        shifted = joined["b"].shift(lag)
        corr = joined["a"].corr(shifted)
        corrs.append((lag, corr))
    return pd.DataFrame(corrs, columns=["lag_months", "correlation"])


def relative_share(df, metric="trends_index"):
    """Compute each entity's share of total metric per month (market-share style)."""
    pivot = df.pivot_table(index="month", columns="entity", values=metric, aggfunc="mean")
    share = pivot.div(pivot.sum(axis=1), axis=0)
    return share


def plot_share(share_df, out_path=f"{DATA_DIR}/relative_share.png"):
    share_df.plot(figsize=(10, 6))
    plt.axvline(pd.Timestamp("2022-11-01"), color="red", linestyle="--", label="ChatGPT launch")
    plt.title("Relative share of search/attention over time")
    plt.ylabel("Share")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Saved plot to {out_path}")


def main():
    df = load_master()

    print("\n--- Segmented trend: Google Translate, pre vs post ChatGPT ---")
    seg = segmented_trend(df)
    print(seg)

    print("\n--- Cross-correlation: Google Translate vs ChatGPT (Trends index) ---")
    if "trends_index_z" in df.columns:
        xcorr = cross_correlation(df)
        print(xcorr)
    else:
        print("Skipped -- trends_index_z column not present (run 04_merge_and_process.py first)")

    print("\n--- Relative share of attention across entities ---")
    if "trends_index" in df.columns:
        share = relative_share(df)
        print(share.tail())
        plot_share(share)


if __name__ == "__main__":
    main()
