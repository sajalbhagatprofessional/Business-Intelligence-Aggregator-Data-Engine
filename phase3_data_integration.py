import sqlite3
import pandas as pd

# --- Configuration ---
DB_FILE = 'production_bi_warehouse.db'

def create_master_views(cursor):
    """Executes SQL to clean, transform, and integrate the staging data."""
    
    print("Executing SQL Transformations...")

    # ---------------------------------------------------------
    # VIEW 1: Master Production Schedule (Orders + Inventory)
    # ---------------------------------------------------------
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS vw_master_production_schedule AS
    WITH InventorySnapshot AS (
        -- Aggregate total inventory from all 3 suppliers
        SELECT 
            material_id, 
            SUM(stock_level) as total_stock 
        FROM stg_inventory 
        GROUP BY material_id
    )
    SELECT 
        o.order_id,
        o.deadline,
        o.material_required,
        o.quantity as ordered_quantity,
        IFNULL(i.total_stock, 0) as current_inventory,
        -- Business Logic: Check if we have enough parts to fulfill the order
        CASE 
            WHEN IFNULL(i.total_stock, 0) >= o.quantity THEN '🟢 Ready for Production'
            ELSE '🔴 Blocked: Material Shortage'
        END as production_status
    FROM stg_orders o
    LEFT JOIN InventorySnapshot i ON o.material_required = i.material_id
    ORDER BY o.deadline ASC;
    """)
    print(" -> Created View: vw_master_production_schedule")

    # ---------------------------------------------------------
    # VIEW 2: Daily Operations & Labor Efficiency (Machines + HR)
    # ---------------------------------------------------------
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS vw_daily_operations_kpi AS
    WITH DailyProduction AS (
        -- Clean & Aggregate IoT Telemetry by Date
        SELECT 
            DATE(timestamp) as op_date,
            SUM(parts_produced) as total_parts_produced,
            COUNT(DISTINCT machine_id) as active_machines,
            ROUND(AVG(temperature_c), 1) as avg_machine_temp
        FROM stg_machine_telemetry
        WHERE status != 'Offline'
        GROUP BY DATE(timestamp)
    ),
    DailyLabor AS (
        -- Clean & Aggregate HR Shift Data by Date
        SELECT 
            shift_date as op_date,
            SUM(hours_worked) as total_labor_hours,
            SUM(overtime_hours) as total_overtime_hours
        FROM stg_employee_shifts
        GROUP BY shift_date
    )
    SELECT 
        p.op_date as operation_date,
        p.active_machines,
        p.total_parts_produced,
        IFNULL(l.total_labor_hours, 0) as total_labor_hours,
        -- KPI Generation: Cross-system metric combining machines and human labor
        ROUND(CAST(p.total_parts_produced AS FLOAT) / NULLIF(l.total_labor_hours, 0), 2) as parts_per_labor_hour,
        p.avg_machine_temp
    FROM DailyProduction p
    INNER JOIN DailyLabor l ON p.op_date = l.op_date
    ORDER BY p.op_date DESC;
    """)
    print(" -> Created View: vw_daily_operations_kpi\n")

def display_results(conn):
    """Fetches the integrated data and displays it using Pandas."""
    
    print("--- 📋 MASTER PRODUCTION SCHEDULE (Top 5 Rows) ---")
    df_orders = pd.read_sql_query("SELECT * FROM vw_master_production_schedule LIMIT 5", conn)
    print(df_orders.to_string(index=False))
    
    print("\n--- 📈 DAILY OPERATIONS KPI (Top 5 Rows) ---")
    df_kpi = pd.read_sql_query("SELECT * FROM vw_daily_operations_kpi LIMIT 5", conn)
    print(df_kpi.to_string(index=False))

if __name__ == "__main__":
    # Connect to the SQLite database generated in Phase 2
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Drop views if they exist so we can re-run this script safely
    cursor.execute("DROP VIEW IF EXISTS vw_master_production_schedule;")
    cursor.execute("DROP VIEW IF EXISTS vw_daily_operations_kpi;")
    
    create_master_views(cursor)
    display_results(conn)
    
    conn.commit()
    conn.close()
    print("\n✅ Phase 3 Complete: Data Integration Successful.")