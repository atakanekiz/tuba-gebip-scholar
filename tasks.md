
# Deployment Tasks & Workflow

This directory contains the cleaned and consolidated scripts for the TUBA Awardees Scholar Data project.

## 1. Environment Setup

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## 2. Workflows

### A. Fresh Scraping (If starting over)
Run the scraping pipeline to fetch data for all awardees from Google Scholar.

```bash
python data_scrape.py
```
*   **What it does**:
    *   Reads `data/gebip_awardees.csv`.
    *   Scrapes Serper.dev in batches (saved to `data/serper_batches/`).
    *   Merges batches into `data/gebip_scholar_enriched.csv`.
    *   Validates names to remove mismatches.

### B. Fixing & Polishing Data (Main Maintenance Task)
Run this script to apply manual fixes, recalibrate metrics, and standardize columns. This is the **primary script** you will use to iterate on the data.

```bash
python data_fixing.py
```
*   **What it does**:
    *   Reads `data/gebip_scholar_final.csv`.
    *   **Manual Overrides**: Fixes correct IDs for specific researchers (e.g. Zeynep Ayşecan Boduroğlu Gököz).
    *   **Exclusions**: Sets `no_scholar_id` for researchers with mixed up profiles.
    *   **Rescraping**: Automatically rescrapes updated IDs or missing metrics.
    *   **Recalculation**: Computes "Citations at Award Year" derived from yearly history.
    *   **Standardization**: Renames columns to Turkish standards (e.g. `scholar_id` -> `Scholar ID`).

### C. Verification
Run this script to verify the integrity of the final dataset.

```bash
python data_verify.py
```
*   **What it does**:
    *   Checks that manual fixes are correctly applied.
    *   Ensures excluded profiles have 0 metrics.
    *   Reports summary statistics.

## 3. Data Files Overview

*   `data/gebip_awardees.csv`: **Source Record**. The original list of awardees.
*   `data/gebip_scholar_enriched.csv`: **Raw Scrape Output**. Result of the `data_scrape.py` process.
*   `data/gebip_scholar_final.csv`: **Production Dataset**. The polished file used by the dashboard.

## 4. Running the App

### Python Dashboard (Streamlit)
```bash
streamlit run dashboard.py
```

### R Shiny App
Navigate to the `shiny_app` directory and run the app. You can use the provided batch scripts on Windows.
```bash
cd shiny_app
# Double click run_app.bat or:
Rscript -e "shiny::runApp()"
```

## 5. Deployment

To deploy the dashboard, ensure `data/gebip_scholar_final.csv` is up to date and push the repository. The dashboard (`dashboard.py`) reads from this final file.
