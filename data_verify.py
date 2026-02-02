
import pandas as pd
import sys
import os

# Ensure UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
DATA_FILE = 'data/gebip_scholar_final.csv'

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    print(f"Loading {DATA_FILE}...\n")
    df = pd.read_csv(DATA_FILE)

    print("=== FINAL VERIFICATION REPORT ===\n")

    # 1. Check Specific Researchers (Sample Validation)
    print("1. Sample Corrections Check:")
    print("-" * 60)

    # Cory David Dunn
    cory = df[df['Adı Soyadı'].str.contains('Cory David Dunn', case=False, na=False)]
    if not cory.empty:
        print(f"\nCory David Dunn:")
        print(f"  Scholar ID: {cory.iloc[0]['Scholar ID']}")
        print(f"  Status: {'✓ Correctly set to no_scholar_id' if cory.iloc[0]['Scholar ID'] == 'no_scholar_id' else '✗ NOT set to no_scholar_id'}")
    
    # Ozan Yılmaz
    ozan = df[df['Adı Soyadı'].str.upper() == 'OZAN YILMAZ']
    if not ozan.empty:
        print(f"\nOzan Yılmaz:")
        sid = ozan.iloc[0]['Scholar ID']
        print(f"  Scholar ID: {sid}")
        print(f"  Status: {'✓ Correctly set to 2HffCiYAAAAJ' if sid == '2HffCiYAAAAJ' else '✗ NOT set to 2HffCiYAAAAJ'}")

    # Fevzi Çakmak CEBECİ
    fevzi = df[df['Adı Soyadı'].str.contains('Fevzi', case=False, na=False) & 
               df['Adı Soyadı'].str.contains('CEBECİ', case=False, na=False)]
    if not fevzi.empty:
        print(f"\nFevzi Çakmak CEBECİ:")
        sid = fevzi.iloc[0]['Scholar ID']
        print(f"  Scholar ID: {sid}")
        print(f"  Status: {'✓ Correctly set to Q4oircsAAAAJ' if sid == 'Q4oircsAAAAJ' else '✗ NOT set to Q4oircsAAAAJ'}")

    # 2. Check Standardization
    print("\n\n2. Standardization Check:")
    print("-" * 60)
    
    # Check for consistency in ID naming
    no_scholar_count = (df['Scholar ID'] == 'no_scholar_id').sum()
    no_id_found_count = (df['Scholar ID'] == 'no id found').sum() # legacy check
    
    print(f"  Entries with 'no_scholar_id': {no_scholar_count}")
    print(f"  Entries with 'no id found' (Legacy): {no_id_found_count}")
    
    if no_id_found_count > 0:
        print("  WARNING: You have inconsistent 'no ID' markers. Run data_fixing.py to fix.")
    else:
        print("  ✓ 'no id found' marker is standardized.")

    # 3. Check Metric Integrity for 'no_scholar_id'
    print("\n\n3. Metric Integrity Check (no_scholar_id):")
    print("-" * 60)
    no_scholar_mask = df['Scholar ID'] == 'no_scholar_id'
    # Check if they have 0 citations
    # Note: We expect cleared data to be 0 or NaN
    ns_df = df[no_scholar_mask]
    failed_clear = ns_df[ns_df['Toplam Atıf'] > 0]
    
    print(f"  Researchers with no_scholar_id: {len(ns_df)}")
    print(f"  Researchers with no_scholar_id BUT > 0 citations: {len(failed_clear)}")
    if len(failed_clear) == 0:
        print("  ✓ All no_scholar_id entries have 0 citations.")
    else:
        print("  ✗ Some no_scholar_id entries still have citation data!")

    # 4. Check Zero Award Year Citations
    print("\n\n4. Zero Award Year Citations Check:")
    print("-" * 60)
    # Check people who HAVE an ID but have 0 citations at award year
    zero_atif = df[(df['Scholar ID'] != 'no_scholar_id') & 
                   (df['Scholar ID'].notna()) &
                   ((df['Ödül Yılındaki Atıf'] == 0.0) | (df['Ödül Yılındaki Atıf'] == 0))]
    
    print(f"  Researchers with valid ID but 0 award-year citations: {len(zero_atif)}")
    if len(zero_atif) > 0:
        print("  (This might be correct if they had no citations by that year, but worth verifying)")

    # 5. Summary
    print("\n" + "=" * 60)
    print(f"Total Records: {len(df)}")
    print(f"Enriched Records: {len(df) - no_scholar_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
