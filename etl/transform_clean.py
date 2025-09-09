import os
import json
import pandas as pd
from datetime import datetime

RAW_FILE = os.path.join(os.path.dirname(__file__), '../data/raw/311_sample.json')
CLEAN_FILE = os.path.join(os.path.dirname(__file__), '../data/clean/311_clean.csv')

os.makedirs(os.path.dirname(CLEAN_FILE), exist_ok=True)

def parse_datetime(dt_str):
    if not dt_str:
        return pd.NaT
    try:
        return pd.to_datetime(dt_str)
    except Exception:
        return pd.NaT

def clean_category(cat):
    if not cat:
        return 'Unknown'
    return cat.strip().title()

def main():
    # Load raw data
    with open(RAW_FILE, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Normalize date fields
    for col in ['created_date', 'closed_date', 'updated_date']:
        if col in df.columns:
            df[col] = df[col].apply(parse_datetime)

    # Clean category
    if 'category' in df.columns:
        df['category'] = df['category'].apply(clean_category)

    # Handle nulls
    df.fillna({'status': 'Unknown', 'category': 'Unknown'}, inplace=True)

    # Drop columns with all nulls
    df.dropna(axis=1, how='all', inplace=True)

    # Save cleaned data
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Saved cleaned data to {CLEAN_FILE} (rows: {len(df)})")

if __name__ == '__main__':
    main()
