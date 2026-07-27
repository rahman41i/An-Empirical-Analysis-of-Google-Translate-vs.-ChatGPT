"""
03_extract_app_reviews.py

Extracts Google Play review data (timestamps, ratings, text) for
Google Translate, DeepL, and ChatGPT apps, as a usage-volume proxy.

Requires: pip install google-play-scraper pandas --break-system-packages

NOTE: This only pulls Google Play (Android). For iOS App Store reviews,
use the `app-store-scraper` package with a near-identical pattern
(swap `reviews()` for `AppStore(...).reviews`).
"""

import pandas as pd
import os
import time
from google_play_scraper import reviews, Sort

OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Google Play package IDs
APPS = {
    "google_translate": "com.google.android.apps.translate",
    "deepl": "com.deepl.mobiletranslator",
    "chatgpt": "com.openai.chatgpt",
}

REVIEWS_PER_APP = 2000  # increase for a richer dataset; scraper paginates automatically


def fetch_reviews(app_id, count):
    all_reviews = []
    continuation_token = None
    while len(all_reviews) < count:
        batch, continuation_token = reviews(
            app_id,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=min(200, count - len(all_reviews)),
            continuation_token=continuation_token,
        )
        if not batch:
            break
        all_reviews.extend(batch)
        if continuation_token is None:
            break
        time.sleep(1)
    return all_reviews


def main():
    all_frames = []
    for label, app_id in APPS.items():
        print(f"Fetching reviews for {label} ({app_id})...")
        try:
            data = fetch_reviews(app_id, REVIEWS_PER_APP)
            df = pd.DataFrame(data)
            df["app_label"] = label
            all_frames.append(df)
            print(f"  Got {len(df)} reviews")
        except Exception as e:
            print(f"  Failed for {label}: {e}")

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        keep_cols = ["app_label", "at", "score", "content", "thumbsUpCount"]
        combined = combined[[c for c in keep_cols if c in combined.columns]]
        combined.to_csv(f"{OUTPUT_DIR}/app_reviews_raw.csv", index=False)
        print(f"Saved {len(combined)} rows to {OUTPUT_DIR}/app_reviews_raw.csv")
    else:
        print("No data fetched -- check network access.")


if __name__ == "__main__":
    main()
