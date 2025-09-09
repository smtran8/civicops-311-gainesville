import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_USER = os.getenv('PG_USER', 'civicops')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'civicops_pass')
PG_DB = os.getenv('PG_DB', 'civicops_311')

engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')

def prepare_data():
    """Load data and create target variable (SLA breach = 72 hours)"""
    # Read feature-enriched data
    df = pd.read_sql('SELECT * FROM fact_requests_features', engine, parse_dates=['created', 'closed'])
    
    # Only use closed tickets for training (we need to know the outcome)
    df_closed = df[df['closed'].notna()].copy()
    
    # Calculate response time in hours
    df_closed['response_hours'] = (df_closed['closed'] - df_closed['created']).dt.total_seconds() / 3600
    
    # Create target variable: SLA breach (True if > 72 hours)
    df_closed['sla_breach'] = (df_closed['response_hours'] > 72).astype(int)
    
    print(f"Dataset shape: {df_closed.shape}")
    print(f"SLA breach rate: {df_closed['sla_breach'].mean():.2%}")
    
    return df_closed

def create_features(df):
    """Create features for modeling"""
    # Select features for modeling
    feature_cols = [
        'rolling_7d_volume',
        'backlog_at_creation',
        'request_type',
        'status'
    ]
    
    # Create feature matrix
    X = df[feature_cols].copy()
    y = df['sla_breach'].copy()
    
    # Encode categorical variables
    le_request_type = LabelEncoder()
    le_status = LabelEncoder()
    
    X['request_type_encoded'] = le_request_type.fit_transform(X['request_type'])
    X['status_encoded'] = le_status.fit_transform(X['status'])
    
    # Select final features
    X_final = X[['rolling_7d_volume', 'backlog_at_creation', 'request_type_encoded', 'status_encoded']]
    
    # Save encoders for later use
    joblib.dump(le_request_type, 'modeling/le_request_type.pkl')
    joblib.dump(le_status, 'modeling/le_status.pkl')
    
    return X_final, y

def train_model(X, y):
    """Train Random Forest model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Evaluate model
    print("\n=== Model Performance ===")
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    joblib.dump(model, 'modeling/sla_breach_model.pkl')
    print(f"\nModel saved to modeling/sla_breach_model.pkl")
    
    return model, X_test, y_test, y_pred_proba

def main():
    # Prepare data
    df = prepare_data()
    
    # Create features
    X, y = create_features(df)
    
    # Train model
    model, X_test, y_test, y_pred_proba = train_model(X, y)
    
    print(f"\nTraining completed! Model ready for predictions.")

if __name__ == '__main__':
    main()
