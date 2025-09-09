import os
import time
import json
from dotenv import load_dotenv
from sodapy import Socrata

# Load environment variables
load_dotenv()

APP_TOKEN = os.getenv("SOC_APP_TOKEN")
DOMAIN = "data.cityofgainesville.org"
DATASET_ID = "78uv-94ar"
LIMIT = 5000  # Increased batch size for better model performance
OFFSET = 0
RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
OUTPUT_FILE = os.path.join(RAW_DIR, "311_sample.json")

os.makedirs(RAW_DIR, exist_ok=True)

# Initialize Socrata client (App Token optional)
if APP_TOKEN:
    client = Socrata(DOMAIN, APP_TOKEN)
else:
    client = Socrata(DOMAIN, None)

all_rows = []
while True:
    try:
        rows = client.get(DATASET_ID, limit=LIMIT, offset=OFFSET)
        if not rows:
            break
        all_rows.extend(rows)
        print(f"Fetched {len(rows)} rows (offset {OFFSET})")
        OFFSET += LIMIT
        # For dev, just fetch one batch
        break
    except Exception as e:
        if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
            print("Throttled by API, sleeping 10s...")
            time.sleep(10)
            continue
        print(f"Error: {e}")
        break

# Save to file
with open(OUTPUT_FILE, "w") as f:
    json.dump(all_rows, f, indent=2)

print(f"Saved {len(all_rows)} rows to {OUTPUT_FILE}")
