"""
02_extract_wikipedia_pageviews.py

Extracts daily Wikipedia pageviews for Google Translate and competitor
articles using the official Wikimedia REST API (free, no auth needed).

Docs: https://wikimedia.org/api/rest_v1/#/Pageviews%20data

Requires: pip install requests pandas --break-system-packages
"""

import time
import requests
import pandas as pd
import os

OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ARTICLES = [
    "Google_Translate",
    "DeepL",
    "ChatGPT",
    "Neural_machine_translation",
]

BASE_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "en.wikipedia/all-access/all-agents/{article}/monthly/{start}/{end}"
)

START = "2015070100"  # API coverage begins July 2015
END = "2026072200"     # today

HEADERS = {
    # Wikimedia asks for a descriptive User-Agent identifying the project
    "User-Agent": "MDS-UniPisa-ResearchProject/1.0 (student project; contact: none)"
}


def fetch_article_views(article):
    url = BASE_URL.format(article=article, start=START, end=END)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    df = pd.DataFrame(items)
    df["article"] = article
    return df


def main():
    all_frames = []
    for article in ARTICLES:
        print(f"Fetching pageviews for {article}...")
        try:
            df = fetch_article_views(article)
            all_frames.append(df)
            print(f"  Got {len(df)} monthly records")
        except Exception as e:
            print(f"  Failed for {article}: {e}")
        time.sleep(1)  # polite delay

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}/wikipedia_pageviews_raw.csv", index=False)
        print(f"Saved {len(combined)} rows to {OUTPUT_DIR}/wikipedia_pageviews_raw.csv")
    else:
        print("No data fetched -- check network access.")


if __name__ == "__main__":
    main()
