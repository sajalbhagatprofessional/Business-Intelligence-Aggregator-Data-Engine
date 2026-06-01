import sqlite3
import pandas as pd
from datetime import datetime

# --- Configuration ---
DB_FILE = 'production_bi_warehouse.db'

def setup_logging_table(cursor):
    """Creates a table to store the history of our automated integrity checks."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_integrity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_timestamp DATETIME,
        validation_test_name TEXT,
        status TEXT,
        details TEXT
    )
    """)

def log_result(cursor, test_name, passed, details):
    """Inserts the pass/fail result into the logging table."""
    status = "✅ PASS" if passed else "❌ FAIL"
    cursor.execute("""
    INSERT INTO data_integrity_logs (check_timestamp, validation_test_name, status, details)
    VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), test_name, status, details))
    
    print(f"{status} | {test_name} | {details}")

def test_order_completeness(cursor):
    """Test 1: Check if all orders from the raw source made it to the final view."""
    
    # Get raw order count
    cursor.execute("SELECT COUNT(*) FROM stg_orders")
    raw_count = cursor.fetchone()[0]
    
    # Get final view order count
    cursor.execute("SELECT COUNT(*) FROM vw_master_production_schedule")
    final_count = cursor.fetchone()[0]
    
    # Validation Logic
    passed = raw_count == final_count
    details = f"Raw Orders: {raw_count}, Final View Orders: {final_count}"
    
    log_result(cursor, "Order Pipeline Completeness", passed, details)
    return passed

def test_production_metric_accuracy(cursor):
    """Test 2: Ensure the total parts produced sum matches between raw IoT data and final KPIs."""
    
    # Sum parts directly from raw telemetry
    cursor.execute("SELECT SUM(parts_produced) FROM stg_machine_telemetry")
    raw_parts_sum = cursor.fetchone()[0] or 0
    
    # Sum parts from the aggregated daily operations view
    cursor.execute("SELECT SUM(total_parts_produced) FROM vw_daily_operations_kpi")
    final_parts_sum = cursor.fetchone()[0] or 0
    
    # Validation Logic
    passed = raw_parts_sum == final_parts_sum
    details = f"Raw Parts Sum: {raw_parts_sum}, KPI View Sum: {final_parts_sum}"
    
    log_result(cursor, "Production Metric Accuracy", passed, details)
    return passed

if __name__ == "__main__":
    print(f"--- 🛡️ Starting Automated Data Integrity Validation ---")
    
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Setup our logging infrastructure
    setup_logging_table(cursor)
    
    # 2. Run the tests
    print("\nExecuting Tests...")
    test1_passed = test_order_completeness(cursor)
    test2_passed = test_production_metric_accuracy(cursor)
    
    # 3. Commit the logs to the database
    conn.commit()
    
    # 4. Final System Output
    print("\n--- Validation Summary ---")
    if test1_passed and test2_passed:
        print("🟢 SYSTEM HEALTHY: All data integrity checks passed. Safe to push to BI Dashboards.")
    else:
        print("🔴 SYSTEM ERROR: Data discrepancy detected. Alerting engineering team via webhook (simulated).")
        # In a real enterprise system, you would add an API call here (e.g., requests.post) 
        # to send a message to Slack or Microsoft Teams.
        
    conn.close()