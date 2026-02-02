
# Implementation Details

## architecture Overview

The project consists of three main stages: **Scraping**, **Refinement**, and **Presentation**.

### 1. Data Collection (Scraping)
*   **Script**: `data_scrape.py`
*   **Source**: Google Scholar via **Serper.dev API** (Primary).
    *   *Note*: Code for **SerpAPI** is included (commented out) as a backup strategy.
*   **Batching**: Data is processed in batches of 20 to handle rate limits and potential failures.
    *   Intermediate files: `data/serper_batches/batch_X_Y.csv`
*   **Matching Logic**:
    *   Fuzzy string matching is used to verify that the found Scholar profile matches the requested researcher.
    *   University affiliation matching scores (1-5) help flag potential mismatches.

### 2. Data Refinement (Fixing)
*   **Script**: `data_fixing.py`
*   **Purpose**: To turn raw scrape data into accurate, production-ready data.
*   **Key Features**:
    *   **Manual Overrides**: Hardcoded dictionary to map specific researchers to their correct Scholar IDs (bypassing search).
    *   **Metric Parsing**: Custom logic parses the `citations_per_year` string (format `YYYY:Count | ...`) to calculate point-in-time metrics.
        *   `Ödül Yılındaki Atıf` (Citations at Award Year) = Sum of yearly citations where Year <= Award Year.
    *   **Interactive Rescraping**: The script identifies if a manual override introduced a new ID that lacks metrics, and automatically scrapes just that profile.

### 3. Dashboard (Presentation)
*   **App**: `dashboard.py` (Streamlit) or `app.R` (Shiny)
*   **Data Source**: `data/gebip_scholar_final.csv`
*   **Visualization**:
    *   Scatter plots compares "Citations at Award Year" vs "Total Citations".
    *   Interactive tables allow filtering by Year and Field.

## Key Decisions for Reproducibility

1.  **Metric Persistence**: We rely on the `citations_per_year` string as the source of truth for historical calculations. This allows us to re-calculate "Award Year" metrics without re-scraping if the award year data changes.
2.  **Explicit Exclusion**: Researchers who definitely do not have a profile are explicitly marked as `no_scholar_id` rather than leaving them as null, preventing repeated futile search attempts.
3.  **UTF-8 Encoding**: All scripts explicitly enforce UTF-8 encoding for standard output (`sys.stdout.reconfigure`) to handle Turkish characters correctly on Windows environments.

## Future Scaling
To scale this to other contexts (e.g. other award lists):
1.  Replace `data/gebip_awardees.csv` with a new source file.
2.  Ensure columns `adi_soyadi` and `calistigi_kurum` exist.
3.  Run `data_scrape.py`.
4.  Review `data_verify.py` output and add misidentified entries to the `overrides` or `remove_ids` lists in `data_fixing.py`.
