import os
import glob
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# --- Configuration ---
# For immediate testing, we use a local SQLite database.
# To switch to PostgreSQL later, change this to: 'postgresql://username:password@localhost:5432/your_database'
DB_CONNECTION_STRING = 'sqlite:///production_bi_warehouse.db'

# Directory paths from Phase 1
BASE_DIR = "production_data_sources"
JSON_DIR = os.path.join(BASE_DIR, "api_json")
CSV_DIR = os.path.join(BASE_DIR, "export_csv")

def get_db_engine():
    """Creates and returns a SQLAlchemy database engine."""
    return create_engine(DB_CONNECTION_STRING)

def load_data_to_staging(df, table_name, engine):
    """Loads a Pandas DataFrame into a SQL table."""
    if df.empty:
        print(f"  -> Skipping {table_name}: No data found.")
        return

    # Add an ingestion timestamp so we know exactly when this data arrived
    df['ingested_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Push to SQL. 'replace' drops the table and recreates it (good for full daily loads). 
    # Use 'append' if you want to keep a historical log of all runs.
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"  -> Successfully loaded {len(df)} rows into staging table: '{table_name}'")

def process_machine_telemetry(engine):
    print("Extracting Machine Telemetry (JSON APIs)...")
    json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
    
    dataframes = []
    for file in json_files:
        df = pd.read_json(file)
        dataframes.append(df)
    
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        load_data_to_staging(combined_df, 'stg_machine_telemetry', engine)

def process_employee_shifts(engine):
    print("Extracting Employee Shifts (HR CSVs)...")
    csv_files = glob.glob(os.path.join(CSV_DIR, "*_shifts.csv"))
    
    dataframes = [pd.read_csv(file) for file in csv_files]
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        load_data_to_staging(combined_df, 'stg_employee_shifts', engine)

def process_inventory_and_orders(engine):
    print("Extracting ERP Data (Inventory & Orders CSVs)...")
    
    # Process Inventory
    inventory_files = glob.glob(os.path.join(CSV_DIR, "*_inventory.csv"))
    if inventory_files:
        inv_df = pd.concat([pd.read_csv(f) for f in inventory_files], ignore_index=True)
        load_data_to_staging(inv_df, 'stg_inventory', engine)

    # Process Orders
    order_files = glob.glob(os.path.join(CSV_DIR, "*_orders.csv"))
    if order_files:
        ord_df = pd.concat([pd.read_csv(f) for f in order_files], ignore_index=True)
        load_data_to_staging(ord_df, 'stg_orders', engine)

if __name__ == "__main__":
    print(f"--- Starting Data Pipeline Engine at {datetime.now().strftime('%H:%M:%S')} ---")
    
    db_engine = get_db_engine()
    
    process_machine_telemetry(db_engine)
    process_employee_shifts(db_engine)
    process_inventory_and_orders(db_engine)
    
    print("\n--- Pipeline Run Complete! ---")
    print(f"Data is now staged in: {DB_CONNECTION_STRING}")