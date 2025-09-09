import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_USER = os.getenv('PG_USER', 'civicops')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'civicops_pass')
PG_DB = os.getenv('PG_DB', 'civicops_311')

engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')

# Read data and check what we're working with
df = pd.read_sql('SELECT * FROM fact_requests', engine, parse_dates=['created', 'closed'])

print("Data shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nRequest types:", df['request_type'].unique())
print("\nDate range:", df['created'].min(), "to", df['created'].max())
print("\nFirst few rows:")
print(df[['id', 'request_type', 'created']].head(10))
