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

def compute_features():
    # Read data from fact_requests
    df = pd.read_sql('SELECT * FROM fact_requests', engine, parse_dates=['created', 'closed'])
    df = df.sort_values(['request_type', 'created'])

    # === TIME-BASED FEATURES ===
    df['hour_of_day'] = df['created'].dt.hour
    df['day_of_week'] = df['created'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['month'] = df['created'].dt.month
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_business_hours'] = ((df['hour_of_day'] >= 9) & (df['hour_of_day'] <= 17)).astype(int)

    # === ROLLING VOLUME FEATURES (Multiple Windows) ===
    def compute_rolling_volume(group, days):
        group = group.sort_values('created')
        rolling_counts = []
        for idx, row in group.iterrows():
            window_start = row['created'] - pd.Timedelta(days=days)
            count = len(group[(group['created'] >= window_start) & (group['created'] <= row['created'])])
            rolling_counts.append(count)
        return pd.Series(rolling_counts, index=group.index)
    
    # Multiple rolling windows
    df['rolling_3d_volume'] = df.groupby('request_type').apply(lambda x: compute_rolling_volume(x, 3), include_groups=False).reset_index(level=0, drop=True)
    df['rolling_7d_volume'] = df.groupby('request_type').apply(lambda x: compute_rolling_volume(x, 7), include_groups=False).reset_index(level=0, drop=True)
    df['rolling_14d_volume'] = df.groupby('request_type').apply(lambda x: compute_rolling_volume(x, 14), include_groups=False).reset_index(level=0, drop=True)

    # === BACKLOG FEATURES ===
    # Overall backlog
    backlog = []
    for idx, row in df.iterrows():
        open_tickets = df[(df['created'] < row['created']) & ((df['closed'].isna()) | (df['closed'] > row['created']))]
        backlog.append(len(open_tickets))
    df['backlog_at_creation'] = backlog

    # Backlog by request type
    backlog_by_type = []
    for idx, row in df.iterrows():
        same_type_open = df[(df['created'] < row['created']) & 
                           ((df['closed'].isna()) | (df['closed'] > row['created'])) & 
                           (df['request_type'] == row['request_type'])]
        backlog_by_type.append(len(same_type_open))
    df['backlog_by_type'] = backlog_by_type

    # === REQUEST TYPE COMPLEXITY ===
    # Calculate average response time by request type (for closed tickets only)
    closed_tickets = df[df['closed'].notna()].copy()
    if len(closed_tickets) > 0:
        closed_tickets['response_hours'] = (closed_tickets['closed'] - closed_tickets['created']).dt.total_seconds() / 3600
        avg_response_by_type = closed_tickets.groupby('request_type')['response_hours'].mean()
        
        # Map average response time to each ticket
        df['avg_response_time_by_type'] = df['request_type'].map(avg_response_by_type)
        df['avg_response_time_by_type'] = df['avg_response_time_by_type'].fillna(df['avg_response_time_by_type'].mean())
    else:
        df['avg_response_time_by_type'] = 72  # Default to SLA time if no closed tickets

    # === FEATURE RATIOS ===
    df['backlog_ratio'] = df['backlog_by_type'] / (df['backlog_at_creation'] + 1)  # +1 to avoid division by zero
    df['volume_ratio_3d_7d'] = df['rolling_3d_volume'] / (df['rolling_7d_volume'] + 1)

    # Save to new table in Postgres
    df.to_sql('fact_requests_features', engine, if_exists='replace', index=False)
    print(f"Saved enhanced features to fact_requests_features (rows: {len(df)})")
    print(f"New features added: time-based, multiple rolling windows, backlog by type, request complexity")

if __name__ == '__main__':
    compute_features()
