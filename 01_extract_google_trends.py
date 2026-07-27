import glob
import os
import matplotlib.pyplot as plt
import pandas as pd

INPUT_DIR = "."
OUTPUT_DIR = "./processed_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Standardize search term names across different languages/exports
COLUMN_MAPPING = {
    "Google Переводчик": "Google Translate",
    "Google Translate": "Google Translate",
    "ChatGPT": "ChatGPT",
    "DeepL": "DeepL",
    "Gemini": "Gemini",
    "Bing Translate": "Bing Translate",
}


def clean_google_trends_csv(file_path):
    """Parses, cleans, and standardizes Google Trends raw export CSV files."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Detect the actual tabular data start line
    skip_lines = 0
    for i, line in enumerate(lines[:5]):
        if any(
            k in line for k in ["Неделя", "Месяц", "Week", "Month", "Date", "Day"]
        ):
            skip_lines = i
            break

    df = pd.read_csv(file_path, skiprows=skip_lines)

    # Standardize date column
    date_col = df.columns[0]
    df = df.rename(columns={date_col: "Date"})
    df["Date"] = pd.to_datetime(df["Date"])

    # Clean and remap search term column names
    clean_cols = {"Date": "Date"}
    for col in df.columns[1:]:
        raw_name = col.split(":")[0].strip()
        standard_name = COLUMN_MAPPING.get(raw_name, raw_name)
        clean_cols[col] = standard_name

    df = df.rename(columns=clean_cols)

    # Convert numeric values and handle '<1' threshold representations
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace("<1", "0.5")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def main():
    csv_files = glob.glob(f"{INPUT_DIR}/*.csv")

    if not csv_files:
        print(f"No CSV files found in directory: '{INPUT_DIR}'")
        return

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}...")

        df = clean_google_trends_csv(file_path)

        # Save cleaned dataset
        save_path = os.path.join(OUTPUT_DIR, f"clean_{filename}")
        df.to_csv(save_path, index=False)
        print(f"Saved dataset: {save_path}")

        # Generate visual trend plot
        plt.figure(figsize=(12, 6))
        for col in df.columns[1:]:
            plt.plot(df["Date"], df[col], label=col)

        plt.title(f"Google Trends Interest Over Time - {filename}")
        plt.xlabel("Date")
        plt.ylabel("Search Interest (0-100)")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)

        plot_path = os.path.join(
            OUTPUT_DIR, f"plot_{filename.replace('.csv', '.png')}"
        )
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()
        print(f"Saved plot: {plot_path}")


if __name__ == "__main__":
    main()
