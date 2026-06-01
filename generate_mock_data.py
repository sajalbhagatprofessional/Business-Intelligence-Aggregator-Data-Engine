import os
import csv
import json
import random
from datetime import datetime, timedelta

# --- Configuration ---
BASE_DIR = "production_data_sources"
JSON_DIR = os.path.join(BASE_DIR, "api_json")
CSV_DIR = os.path.join(BASE_DIR, "export_csv")

# Ensure directories exist
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# Shared reference data to ensure the data is relational (can be JOINed later)
MACHINE_IDS = [f"MCH-{str(i).zfill(3)}" for i in range(1, 11)]
EMPLOYEE_IDS = [f"EMP-{str(i).zfill(3)}" for i in range(100, 150)]
MATERIAL_IDS = ["MAT-A", "MAT-B", "MAT-C", "MAT-D", "MAT-E"]

def generate_timestamps(days_back=7):
    """Generates random timestamps for the past week."""
    base = datetime.now() - timedelta(days=days_back)
    return (base + timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")

# --- 1. Machine Telemetry (JSON) - 5 Sources ---
# Simulates APIs from 5 different assembly lines
def create_machine_apis():
    statuses = ["Running", "Idle", "Maintenance", "Offline"]
    for i in range(1, 6):
        data = []
        for _ in range(50): # 50 records per line
            record = {
                "assembly_line": i,
                "machine_id": random.choice(MACHINE_IDS),
                "timestamp": generate_timestamps(),
                "status": random.choices(statuses, weights=[70, 15, 10, 5])[0],
                "temperature_c": round(random.uniform(40.0, 95.0), 1),
                "parts_produced": random.randint(0, 500) if statuses != "Offline" else 0
            }
            data.append(record)
        
        filepath = os.path.join(JSON_DIR, f"line_{i}_telemetry.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Created: {filepath}")

# --- 2. Employee Shift Logs (CSV) - 5 Sources ---
# Simulates HR flat-file exports for 5 different departments
def create_employee_csvs():
    departments = ["Welding", "Assembly", "Quality_Assurance", "Packaging", "Maintenance"]
    for dept in departments:
        filepath = os.path.join(CSV_DIR, f"{dept}_shifts.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["employee_id", "department", "shift_date", "hours_worked", "overtime_hours"])
            
            for _ in range(40):
                writer.writerow([
                    random.choice(EMPLOYEE_IDS),
                    dept,
                    (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                    random.choice([8, 10, 12]),
                    random.randint(0, 4)
                ])
        print(f"Created: {filepath}")

# --- 3. Inventory & Orders (CSV) - 5 Sources ---
# Simulates ERP and Supplier data exports
def create_inventory_csvs():
    # 3 Supplier Inventory Feeds
    for i in range(1, 4):
        filepath = os.path.join(CSV_DIR, f"supplier_{i}_inventory.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["material_id", "supplier_id", "stock_level", "last_restock_date"])
            for mat in MATERIAL_IDS:
                writer.writerow([
                    mat,
                    f"SUP-{i}",
                    random.randint(100, 5000),
                    generate_timestamps()
                ])
        print(f"Created: {filepath}")

    # 2 Production Order Feeds
    for i in ["Priority", "Standard"]:
        filepath = os.path.join(CSV_DIR, f"{i}_orders.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["order_id", "material_required", "quantity", "deadline"])
            for j in range(1, 26):
                writer.writerow([
                    f"ORD-{i[:3].upper()}-{random.randint(1000, 9999)}",
                    random.choice(MATERIAL_IDS),
                    random.randint(50, 1000),
                    (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")
                ])
        print(f"Created: {filepath}")

if __name__ == "__main__":
    print("Initializing Data Engine Sources...\n")
    create_machine_apis()
    create_employee_csvs()
    create_inventory_csvs()
    print("\nSuccess! 15 mock data sources generated in the 'production_data_sources' directory.")