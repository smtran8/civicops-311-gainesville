import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_USER = os.getenv('PG_USER', 'civicops')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'civicops_pass')
PG_DB = os.getenv('PG_DB', 'civicops_311')

CLEAN_FILE = os.path.join(os.path.dirname(__file__), '../data/clean/311_clean.csv')

engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')

def create_table():
    with engine.connect() as conn:
        with open(os.path.join(os.path.dirname(__file__), '../db/schema.sql')) as f:
            sql = f.read()
        conn.execute(text(sql))
        print('Table fact_requests ensured.')

def load_data():
    df = pd.read_csv(CLEAN_FILE)
    df.to_sql('fact_requests', engine, if_exists='replace', index=False)
    print(f'Loaded {len(df)} rows into fact_requests.')

def main():
    create_table()
    load_data()

if __name__ == '__main__':
    main()
