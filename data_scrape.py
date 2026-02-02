
import pandas as pd
import requests
import time
import os
import glob
from unidecode import unidecode
import sys 
import re
from bs4 import BeautifulSoup
import random

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
SERPER_API_KEY = "be361518bfb80e064f3fe93d72a1c48a86ca359b"
DATA_FILE = "data/gebip_awardees.csv"
BATCH_DIR = "data/serper_batches"
MERGED_OUTPUT_FILE = "data/gebip_scholar_enriched.csv"
BATCH_SIZE = 20

# ==============================================================================
# SECTION 1: SERPER API & SCRAPING LOGIC
# ==============================================================================

UNIVERSITY_MAPPING = {
    "odtu": "middle east technical university",
    "metu": "middle east technical university",
    "middle east technical university": "middle east technical university",
    "itu": "istanbul technical university",
    "istanbul teknik universitesi": "istanbul technical university",
    "boun": "bogazici university",
    "bogazici": "bogazici university",
    "iyte": "izmir institute of technology",
    "izmir yuksek teknoloji enstitusu": "izmir institute of technology",
    "ku": "koc university",
    "su": "sabanci university"
}

def generate_name_variations(name_str):
    """Generates variations of a name."""
    if not isinstance(name_str, str):
        return []

    name_clean = name_str.strip()
    name_english = unidecode(name_clean)
    
    variations = set()
    variations.add(name_clean)
    variations.add(name_english)
    
    parts = name_english.split()
    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]
        middles = parts[1:-1]
        
        # Abbreviated first name
        variations.add(f"{first[0]}. {' '.join(middles)} {last}".strip().replace("  ", " "))
        
        if middles:
             # Abbreviated middle names
             middle_initials = " ".join([f"{m[0]}." for m in middles])
             variations.add(f"{first} {middle_initials} {last}")
             
             # Abbreviated first and middle
             variations.add(f"{first[0]}. {middle_initials} {last}")

    return list(variations)

def calculate_match_score(original_aff, found_aff):
    """Calculates a match integrity score (1-5)."""
    if pd.isna(found_aff) or not found_aff:
        return 3, "No affiliation in profile"
        
    if pd.isna(original_aff):
        return 3, "No original affiliation to compare"

    # Normalize
    org_norm = unidecode(str(original_aff)).lower()
    found_norm = unidecode(str(found_aff)).lower()
    
    # Expand abbreviations
    for key, value in UNIVERSITY_MAPPING.items():
        if key in org_norm:
            org_norm = org_norm.replace(key, value)
    
    # Token matching
    stop_words = {"university", "universitesi", "faculty", "fakultesi", "of", "department", "bolumu", "institute", "enstitusu", "univ", "uni", "prof", "assoc", "asst", "dr"}
    
    def get_tokens(text):
        tokens = set(text.replace(",", " ").replace("-", " ").replace("/", " ").split())
        return {t for t in tokens if len(t) > 2 and t not in stop_words}

    org_tokens = get_tokens(org_norm)
    found_tokens = get_tokens(found_norm)
    
    common = org_tokens.intersection(found_tokens)
    
    if len(common) > 0:
        return 5, f"Matched tokens: {', '.join(common)}"
    else:
        if org_norm in found_norm or found_norm in org_norm:
             return 5, "Substring match"
        return 1, f"Affiliation mismatch? '{original_aff}' vs '{found_aff}'"

def scrape_extra_metrics(scholar_id):
    """
    Scrapes the Google Scholar profile page for deep metrics.
    Returns: h_index, i10_index, citations_per_year (str), total_documents (int - approx)
    """
    url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    metrics = {
        "h_index": 0,
        "i10_index": 0,
        "citations_per_year": "",
        "total_documents": 0,
        "documents_per_year": "",
        "total_citations": 0
    }
    
    try:
        time.sleep(random.uniform(1.0, 2.0))
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f" [Scrape Failed: {response.status_code}]", end="")
            return metrics
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Parse Metrics Table (#gsc_rsb_st)
        table = soup.select_one("#gsc_rsb_st")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    label = cols[0].get_text(strip=True).lower()
                    val_all = cols[1].get_text(strip=True)
                    
                    if "citations" in label or "alıntılar" in label:
                        metrics["total_citations"] = int(val_all) if val_all.isdigit() else 0
                    elif "h-index" in label or "h-endeksi" in label:
                        metrics["h_index"] = int(val_all) if val_all.isdigit() else 0
                    elif "i10-index" in label or "i10-endeksi" in label:
                        metrics["i10_index"] = int(val_all) if val_all.isdigit() else 0
                        
        # 2. Parse Citations Graph (Yearly)
        years_els = soup.select(".gsc_g_t")
        vals_els = soup.select(".gsc_g_a")
        if not vals_els:
            vals_els = soup.select(".gsc_g_al")
            
        yearly_data = []
        if len(years_els) == len(vals_els):
            for y, v in zip(years_els, vals_els):
                yearly_data.append(f"{y.get_text(strip=True)}:{v.get_text(strip=True)}")
        
        metrics["citations_per_year"] = " | ".join(yearly_data)
        
        # 3. Total Documents (Pagination Loop)
        # Detailed logic to paginate through documents to get counts per year
        page_num = 0
        MAX_PAGES = 30 # Cap at 3000 docs
        from collections import Counter
        doc_years = Counter()
        total_docs_count = 0
        
        while page_num < MAX_PAGES:
            if page_num > 0:
                time.sleep(1.0)
                
            loop_url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&cstart={page_num*100}&pagesize=100"
            
            try:
                resp_loop = requests.get(loop_url, headers=headers, timeout=10)
                if resp_loop.status_code != 200:
                   break
                   
                soup_loop = BeautifulSoup(resp_loop.text, "html.parser")
                rows = soup_loop.select(".gsc_a_tr")
                count = len(rows)
                total_docs_count += count
                
                for row in rows:
                    year_el = row.select_one(".gsc_a_y")
                    if year_el:
                        y_text = year_el.get_text(strip=True)
                        if y_text.isdigit():
                            doc_years[int(y_text)] += 1
                
                if count < 100:
                    break
            except:
                break
                
            page_num += 1
            
        metrics["total_documents"] = total_docs_count
        sorted_years = sorted(doc_years.keys())
        docs_str_list = [f"{y}:{doc_years[y]}" for y in sorted_years]
        metrics["documents_per_year"] = " | ".join(docs_str_list)
        
        return metrics

    except Exception as e:
        print(f" [Scrape Error: {e}]", end="")
        return metrics

def search_and_enrich_serper(name):
    """
    Searches for a Google Scholar profile using Serper Dev.
    Then SCRAPES the profile page for detailed metrics.
    """
    url = "https://google.serper.dev/search"
    name_clean = name.replace("'", "").replace('"', "")
    
    payload = {
        "q": f"site:scholar.google.com {name_clean}",
        "gl": "tr",
        "hl": "en" 
    }
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        for result in data.get("organic", []):
            link = result.get("link", "")
            
            if "scholar.google" in link and "user=" in link:
                try:
                    # link format: ...?user=ID&... or .../citations?user=ID
                    author_id = link.split("user=")[1].split("&")[0]
                except:
                    continue 
                
                raw_snippet = result.get("snippet", "")
                snippet = raw_snippet.replace('\u202a', '').replace('\u202c', '').replace('\u200e', '').replace('\u200f', '')
                parts = snippet.split(" - ")
                affiliation = parts[0] if len(parts) > 0 else "Unknown"
                
                # Check for "Cited by" in snippet as backup
                total_citations = 0
                match_en = re.search(r"Cited by\s+([\d,]+)", snippet, re.IGNORECASE)
                match_tr = re.search(r"([\d\.,]+)\s+tarafından alıntılandı", snippet, re.IGNORECASE)
                
                if match_en:
                    num_str = match_en.group(1).replace(",", "")
                    if num_str.isdigit(): total_citations = int(num_str)
                elif match_tr:
                    num_str = match_tr.group(1).replace(".", "").replace(",", "") 
                    if num_str.isdigit(): total_citations = int(num_str)
                    
                interests = []
                for p in parts:
                    p_clean = p.strip()
                    if not p_clean: continue
                    if p_clean == affiliation.strip(): continue
                    if "Cited by" in p_clean or "tarafından alıntılandı" in p_clean: continue
                    if "Verified email" in p_clean or "doğrulanmış e-posta" in p_clean: continue
                    if "Google Scholar" in p_clean or "Google Akademik" in p_clean: continue
                    interests.append(p_clean)
                
                print(f" [Scraping Profile...]", end="")
                extras = scrape_extra_metrics(author_id)
                
                final_citations = extras["total_citations"] if extras["total_citations"] > 0 else total_citations
                
                return {
                    "scholar_id": author_id,
                    "scholar_name": result.get("title", "").replace(" - Google Scholar", "").replace(" - Google Akademik", ""),
                    "affiliation": affiliation.strip(),
                    "total_citations": final_citations, 
                    "h_index": extras["h_index"],
                    "i10_index": extras["i10_index"],
                    "citations_per_year": extras["citations_per_year"],
                    "total_documents": extras["total_documents"],
                    "documents_per_year": extras["documents_per_year"],
                    "interests": interests
                }
        return None
    except Exception as e:
        print(f"Error searching for {name}: {e}")
        return None

def scrape_profile_by_id(scholar_id):
    """
    Directly scrapes a Google Scholar profile by ID to get Name, Affiliation, and Metrics.
    """
    url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    info = {
        "scholar_id": scholar_id,
        "scholar_name": None,
        "scholar_affiliation": None,
        "interests": [],
        "total_citations": 0,
        "h_index": 0,
        "i10_index": 0,
        "citations_per_year": "",
        "total_documents": 0,
        "documents_per_year": ""
    }

    try:
        # 1. Fetch main page for Name, Affiliation, Interests
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Name (#gsc_prf_in)
            name_el = soup.select_one("#gsc_prf_in")
            if name_el:
                info["scholar_name"] = name_el.get_text(strip=True)
                
            # Affiliation (.gsc_prf_il)
            aff_els = soup.select(".gsc_prf_il")
            for el in aff_els:
                txt = el.get_text(strip=True)
                if "Verified email" not in txt and "Follow" not in txt:
                    info["scholar_affiliation"] = txt
                    break 
            
            # Interests
            int_els = soup.select(".gsc_prf_inta")
            interests = [i.get_text(strip=True) for i in int_els]
            info["interests"] = interests

    except Exception as e:
        print(f" [Meta Scrape Error: {e}]", end="")

    # 2. Get Metrics reuse
    metrics = scrape_extra_metrics(scholar_id)
    info.update(metrics)
    
    return info

# ==============================================================================
# SECTION 2: BATCH PROCESSING
# ==============================================================================

def process_all_authors():
    if not os.path.exists(BATCH_DIR):
        os.makedirs(BATCH_DIR)
        
    df_source = pd.read_csv(DATA_FILE)
    total_records = len(df_source)
    
    # Identify processed indices
    processed_indices = set()
    for f in glob.glob(os.path.join(BATCH_DIR, "batch_*.csv")):
        try:
            base = os.path.basename(f)
            parts = base.replace("batch_", "").replace(".csv", "").split("_")
            start = int(parts[0])
            end = int(parts[1])
            for i in range(start, end):
                processed_indices.add(i)
        except:
            pass
            
    for start_idx in range(0, total_records, BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, total_records)
        
        batch_indices = set(range(start_idx, end_idx))
        if batch_indices.issubset(processed_indices):
            print(f"Skipping batch {start_idx}-{end_idx} (Already processed)")
            continue
            
        print(f"\nProcessing batch: {start_idx} to {end_idx}")
        
        batch_df = df_source.iloc[start_idx:end_idx].copy()
        
        cols = ["scholar_id", "scholar_name", "scholar_affiliation", "total_citations", 
                "h_index", "i10_index", "citations_per_year", "total_documents", 
                "documents_per_year", "interests", "match_score", "match_notes"]
        for col in cols:
            batch_df[col] = None
            
        for index, row in batch_df.iterrows():
            name = row["adi_soyadi"]
            original_affiliation = row["calistigi_kurum"]
            
            print(f"[{index}] {name}...", end="", flush=True)
            
            result = search_and_enrich_serper(name)
            
            if not result:
                variations = generate_name_variations(name)
                for var_name in variations:
                    if var_name == name: continue
                    result = search_and_enrich_serper(var_name)
                    if result:
                        print(f" (Found via '{var_name}')", end="")
                        break
            
            if result:
                print(f" [ID: {result['scholar_id']} | Citations: {result['total_citations']}]", end="")
                batch_df.at[index, "scholar_id"] = result["scholar_id"]
                batch_df.at[index, "scholar_name"] = result["scholar_name"]
                batch_df.at[index, "scholar_affiliation"] = result["affiliation"]
                batch_df.at[index, "total_citations"] = result["total_citations"]
                batch_df.at[index, "h_index"] = result["h_index"]
                batch_df.at[index, "i10_index"] = result["i10_index"]
                batch_df.at[index, "citations_per_year"] = result["citations_per_year"]
                batch_df.at[index, "total_documents"] = result["total_documents"]
                batch_df.at[index, "documents_per_year"] = result["documents_per_year"]
                batch_df.at[index, "interests"] = ", ".join(result["interests"])
                
                score, notes = calculate_match_score(original_affiliation, result["affiliation"])
                batch_df.at[index, "match_score"] = score
                batch_df.at[index, "match_notes"] = notes
            else:
                print(" [Not Found]", end="")
                batch_df.at[index, "match_notes"] = "Search failed"
                
            print("") 
            time.sleep(0.5) 
            
        out_file = os.path.join(BATCH_DIR, f"batch_{start_idx}_{end_idx}.csv")
        batch_df.to_csv(out_file, index=False)
        print(f"Saved: {out_file}")
        time.sleep(2)

# ==============================================================================
# SECTION 3: MERGING AND VALIDATION LOGIC
# ==============================================================================

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    clean = unidecode(name).lower()
    for char in [".", "-", ",", "(", ")", "[", "]", "'", '"']:
        clean = clean.replace(char, " ")
    return " ".join(clean.split())

def is_name_match(name1, name2):
    if pd.isna(name1) or pd.isna(name2):
        return False
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2: return False
    
    if n1 in n2 or n2 in n1: return True
    
    parts1 = n1.split()
    parts2 = n2.split()
    set1 = set(parts1)
    set2 = set(parts2)
    common = set1.intersection(set2)
    
    if len(common) >= 2: return True
    if len(common) >= 1 and any(len(c) > 2 for c in common):
        rem1 = [p for p in parts1 if p not in common]
        rem2 = [p for p in parts2 if p not in common]
        if not rem1 or not rem2: return True
        if (rem1 and rem2 and rem1[0][0] == rem2[0][0]): return True
    return False

def merge_and_validate():
    print("Identifying batches to merge...")
    all_files = glob.glob(os.path.join(BATCH_DIR, "batch_*.csv"))
    valid_files = []
    
    for f in all_files:
        try:
            base = os.path.basename(f)
            parts = base.replace("batch_", "").replace(".csv", "").split("_")
            start = int(parts[0])
            valid_files.append((start, f))
        except:
            continue
            
    valid_files.sort(key=lambda x: x[0])
    files_to_read = [x[1] for x in valid_files]
    
    if not files_to_read:
        print("No matching files found.")
        return

    print(f"Merging {len(files_to_read)} files...")
    df_list = [pd.read_csv(f) for f in files_to_read]
    merged_df = pd.concat(df_list, ignore_index=True)
    
    print(f"Total rows before validation: {len(merged_df)}")
    mismatch_count = 0
    
    for index, row in merged_df.iterrows():
        original_name = row.get("adi_soyadi")
        scholar_name = row.get("scholar_name")
        scholar_id = row.get("scholar_id")
        
        if pd.isna(scholar_id) or str(scholar_id).lower() == "nan":
            continue
            
        if not is_name_match(original_name, scholar_name):
            print(f" [MISMATCH] Row {index}: '{original_name}' vs Found '{scholar_name}' -> CLEARED")
            
            cols_to_clear = [
                "scholar_name", "scholar_affiliation", "total_citations", 
                "h_index", "i10_index", "citations_per_year", 
                "total_documents", "documents_per_year", "interests",
                "match_score", "match_notes"
            ]
            merged_df.at[index, "scholar_id"] = "no id found"
            for col in cols_to_clear:
                if col in merged_df.columns:
                    merged_df.at[index, col] = None
            mismatch_count += 1
            
    print(f"\nValidation complete. Mismatches cleared: {mismatch_count}")
    merged_df.to_csv(MERGED_OUTPUT_FILE, index=False)
    print(f"Saved merged file to: {MERGED_OUTPUT_FILE}")

# ==============================================================================
# SECTION 4: SERPAPI (LEGACY CODE - COMMENTED OUT)
# ==============================================================================
"""
# This code is preserved for future use if we switch back to SerpAPI.
# Requires 'google-search-results' package (pip install google-search-results)

import requests
SERPAPI_KEY = "c9f5958126d2bc3e0e6788bb2cafff23b37487f9169f686f5f62b8839511d8cd"

def search_scholar_profile_serpapi(name):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": name,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        profiles = data.get("profiles", {}).get("authors", [])
        if not profiles:
            return None
        return profiles[0].get("author_id")
    except Exception as e:
        print(f"Error searching for {name}: {e}")
        return None

def get_author_metrics_serpapi(author_id):
    if not author_id: return None
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        author = data.get("author", {})
        cited_by = data.get("cited_by", {})
        table = cited_by.get("table", [])
        
        total_citations = table[0].get("citations", {}).get("all", 0) if len(table)>=1 else 0
        h_index = table[1].get("h_index", {}).get("all", 0) if len(table)>=2 else 0
        i10_index = table[2].get("i10_index", {}).get("all", 0) if len(table)>=3 else 0

        return {
            "scholar_id": author_id,
            "scholar_name": author.get("name"),
            "affiliation": author.get("affiliations"),
            "total_citations": total_citations,
            "h_index": h_index,
            "i10_index": i10_index,
            "interests": [i.get("title") for i in author.get("interests", [])],
        }
    except Exception as e:
        print(f"Error fetching metrics for {author_id}: {e}")
        return None
"""

if __name__ == "__main__":
    print("Starting Data Scrape Pipeline...")
    print("1. Running Batch Processing...")
    process_all_authors()
    
    print("\n2. Running Merge and Validate...")
    merge_and_validate()
