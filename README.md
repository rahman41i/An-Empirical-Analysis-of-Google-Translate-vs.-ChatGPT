# An Empirical Analysis of Google Translate vs. ChatGPT

A multi-source econometric and time-series analysis examining whether the emergence of conversational generative AI models (ChatGPT) substitutes for or complements dedicated Machine Translation (MT) services (Google Translate, DeepL).

By constructing a unified monthly panel dataset from three distinct public proxies—Google Trends search indices, Wikipedia Pageviews API, and Google Play Store review volumes—this project quantifies search attention shifts following ChatGPT's November 2022 release.

---

## Project structure

```
01_extract_google_trends.py          automated Google Trends data fetcher (reference only — often rate-limited; not used downstream)
01b_parse_manual_trends_export.py    parser for manual Google Trends CSV exports (the source 04 actually reads)
02_extract_wikipedia_pageviews.py    Wikipedia Pageviews API fetcher
03_extract_app_reviews.py            Play Store review extraction via google-play-scraper
04_merge_and_process.py              data cleaning, standardization, & monthly resampling
05_analyze.py                        econometric modeling, regression, & cross-correlation
new_project.ipynb                    exploratory analysis notebook
data_milestones_manual.csv           annotated event and milestone dataset
multiTimeline_2016.csv               Google Trends monthly index, cleaned (2016–2026)
multiTimeline_5_years.csv            Google Trends weekly index, cleaned (last 5 years)
plot_data_milestones_manual.png      output chart: annotated time-series
relative_share.png                   output chart: relative attention share
report/main.tex                      the project report (LaTeX)
report/main.pdf                      compiled PDF report
report/relative_share.png            embedded report figure
```

## Running the pipeline

### 1. Installation

Ensure Python 3.9+ is installed, then install the required dependencies:

```
pip install pandas numpy matplotlib seaborn scipy statsmodels google-play-scraper
```

### 2. Pipeline execution

To execute the data processing and econometric analysis pipeline from scratch, run the scripts in order from the project root:

```
python 01b_parse_manual_trends_export.py
python 02_extract_wikipedia_pageviews.py
python 03_extract_app_reviews.py
python 04_merge_and_process.py
python 05_analyze.py
```

- `01b_parse_manual_trends_export.py` cleans the manually-exported Google Trends CSVs (`multiTimeline_2016.csv`, `multiTimeline_5_years.csv`) into a standardized format. Google's Trends API frequently rate-limits automated requests, so this manual-export path is the reliable one — `01_extract_google_trends.py` is kept in the repo for reference but its output isn't consumed by later steps.
- `02_extract_wikipedia_pageviews.py` pulls monthly Wikipedia pageview counts for each entity's article.
- `03_extract_app_reviews.py` pulls Play Store review counts and ratings for each entity.
- `04_merge_and_process.py` merges all three sources, normalizes column labels, handles missing or small values (`<1`), and outputs a unified monthly master panel dataset.
- `05_analyze.py` executes the segmented linear regressions, computes time-lagged cross-correlations, calculates relative attention shares, and generates visual plots.

Alternatively, run `new_project.ipynb` end-to-end for the same pipeline in notebook form.

## Data dictionary

### `multiTimeline_2016.csv`
Monthly Google Trends search-interest data for "Google Translate," "ChatGPT," and "DeepL" worldwide, January 2016–present.

| Column | Description |
|---|---|
| `Month` | Calendar month for the observation (YYYY-MM-DD, first of month) |
| `Google Translate` | Relative search interest, Google Trends index 0–100 (100 = peak within this file's time range) |
| `ChatGPT` | Relative search interest, same 0–100 scale |
| `DeepL` | Relative search interest, same 0–100 scale |

### `multiTimeline_5_years.csv`
Weekly Google Trends search-interest data for the same three terms, most recent 5-year window.

| Column | Description |
|---|---|
| `Week` | Start date of the weekly observation window (YYYY-MM-DD) |
| `Google Translate` | Relative search interest, 0–100 scale within this file's time range |
| `ChatGPT` | Relative search interest, 0–100 scale |
| `DeepL` | Relative search interest, 0–100 scale |

> **Note:** Google Trends values are relative, not absolute search volume — 100 marks the peak within each file's own time range. The monthly and weekly files were pulled as separate queries and are not directly comparable in scale to one another.

### `data_milestones_manual.csv`
Hand-compiled timeline of key product milestones used to annotate the trend data.

| Column | Description |
|---|---|
| `date` | Date the milestone occurred (YYYY-MM-DD) |
| `event` | Short description of the milestone (e.g. product launch, feature release) |
| `entity` | Which product/service the milestone relates to (Google Translate, ChatGPT, Gemini/Bard) |
| `source` | Where the milestone date/fact was sourced from (e.g. Wikipedia, company blog) |

## Key analytical methods

1. **Segmented Linear Regression:** Evaluates structural trend breaks in Google Translate search intent pre- vs. post-ChatGPT release date (Nov 2022).
2. **Time-Lagged Cross-Correlation:** Quantifies inverse synchronization (r ≈ -0.61 to -0.65) across a ±6-month window between LLM growth and traditional MT search volume.
3. **Relative Search Attention Share:** Decomposes aggregate web search query volume across ChatGPT, Google Translate, and DeepL by mid-2026.

## Report

`report/main.tex` is the project report written in LaTeX. Compiled output: [`report/main.pdf`](report/main.pdf).

### Compile

- **Overleaf:** Upload the `report/` folder, set `main.tex` as the main document, and click Recompile.
- **Local:** Navigate to the report folder and compile using your terminal:

```
cd report
pdflatex main.tex
pdflatex main.tex
```

Running it twice ensures all internal references, tables, and figure labels are resolved correctly. Alternatively, run `latexmk -pdf main.tex`.

## Notes on methodology

- **Search Attention vs. Market Share:** Google Trends indices measure relative web search interest and brand discovery queries, not total direct product utilization or API calls. Google Translate retains a massive baseline footprint (>1 billion active users) via browser integrations and direct access, which are not captured by search queries.
- **Data Resampling:** All multi-source time series (weekly trends, daily pageviews, app reviews) are resampled and aligned to a uniform monthly frequency for econometric panel modeling.

## Dataset

The cleaned dataset is also published on Kaggle: [Analyzing Google Translate vs. ChatGPT](https://www.kaggle.com/datasets/rahman4li/analyzing-google-translate-vs-chatgpt).

## License

## License

- **Code** (Python scripts, notebook): [MIT License](LICENSE)
- **Data** (`multiTimeline_2016.csv`, `multiTimeline_5_years.csv`, `data_milestones_manual.csv`, and derived datasets): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, share, and adapt with attribution.
- **Report** (`report/main.pdf`, `report/main.tex`): ©Rahman Aliyev, shared for reference; contact before reuse in other publications.
