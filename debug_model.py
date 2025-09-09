import joblib
import pandas as pd
from sqlalchemy import create_engine

# Check what the model was actually trained on
try:
    # Load the encoders
    le_request_type = joblib.load('modeling/le_request_type.pkl')
    le_status = joblib.load('modeling/le_status.pkl')
    
    print("=== MODEL ENCODERS ===")
    print("Request types the model knows:")
    print(le_request_type.classes_)
    print("\nStatus values the model knows:")
    print(le_status.classes_)
    
    # Check current database values
    engine = create_engine('postgresql+psycopg2://civicops:civicops_pass@localhost:5432/civicops_311')
    
    print("\n=== CURRENT DATABASE VALUES ===")
    status_df = pd.read_sql('SELECT DISTINCT status FROM fact_requests_features', engine)
    print("Status values in database:")
    print(status_df['status'].unique())
    
    types_df = pd.read_sql('SELECT DISTINCT request_type FROM fact_requests_features LIMIT 10', engine)
    print("\nRequest types in database:")
    print(types_df['request_type'].unique())
    
    # Test if "In Process" is in the model's known statuses
    print(f"\n=== TESTING ===")
    print(f"'In Process' in model statuses: {'In Process' in le_status.classes_}")
    print(f"'Road Repair' in model request types: {'Road Repair' in le_request_type.classes_}")
    
except Exception as e:
    print(f"Error: {e}")
