import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_USER = os.getenv('PG_USER', 'civicops')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'civicops_pass')
PG_DB = os.getenv('PG_DB', 'civicops_311')

try:
    engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')
    print("Connected to database successfully!")
    
    # Check what status values are in the data
    df = pd.read_sql('SELECT DISTINCT status FROM fact_requests_features', engine)
    print("Available status values:")
    print(df['status'].unique())
    
    # Check what request types are available
    df_types = pd.read_sql('SELECT DISTINCT request_type FROM fact_requests_features LIMIT 10', engine)
    print("\nSample request types:")
    print(df_types['request_type'].unique())
    
except Exception as e:
    print(f"Error: {e}")
