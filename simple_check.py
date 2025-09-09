import pandas as pd
from sqlalchemy import create_engine

# Simple connection test
try:
    engine = create_engine('postgresql+psycopg2://civicops:civicops_pass@localhost:5432/civicops_311')
    print("Testing database connection...")
    
    # Simple query to check if table exists
    result = pd.read_sql('SELECT COUNT(*) as count FROM fact_requests_features', engine)
    print(f"Table has {result['count'].iloc[0]} rows")
    
    # Check status values
    status_df = pd.read_sql('SELECT DISTINCT status FROM fact_requests_features LIMIT 5', engine)
    print("Status values:")
    print(status_df['status'].tolist())
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your Postgres database is running with: docker-compose up -d")
