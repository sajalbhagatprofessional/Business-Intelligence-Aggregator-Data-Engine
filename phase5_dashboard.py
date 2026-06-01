import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# --- Configuration ---
DB_FILE = 'production_bi_warehouse.db'

# Set up the web page layout
st.set_page_config(page_title="Production BI Dashboard", layout="wide")
st.title("🏭 Manufacturing Business Intelligence Aggregator")
st.markdown("Automated master report for production scheduling and labor efficiency.")

# --- Data Loading ---
# We use st.cache_data so the dashboard doesn't re-query the DB on every click
@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        df_orders = pd.read_sql_query("SELECT * FROM vw_master_production_schedule", conn)
        df_kpis = pd.read_sql_query("SELECT * FROM vw_daily_operations_kpi", conn)
        
        # Load validation logs to show pipeline health
        df_logs = pd.read_sql_query("SELECT * FROM data_integrity_logs ORDER BY check_timestamp DESC LIMIT 2", conn)
        conn.close()
        return df_orders, df_kpis, df_logs
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_orders, df_kpis, df_logs = load_data()

# --- Section 1: Data Pipeline Health ---
st.sidebar.header("🛡️ Pipeline Health Status")
if not df_logs.empty:
    for index, row in df_logs.iterrows():
        if "✅ PASS" in row['status']:
            st.sidebar.success(f"{row['validation_test_name']}: PASSED")
        else:
            st.sidebar.error(f"{row['validation_test_name']}: FAILED")
    st.sidebar.caption(f"Last validated: {df_logs.iloc[0]['check_timestamp']}")

# --- Section 2: Top-Level KPIs ---
st.header("Executive Summary")
col1, col2, col3 = st.columns(3)

# Calculate some quick metrics from the KPI view
avg_efficiency = df_kpis['parts_per_labor_hour'].mean()
total_production = df_kpis['total_parts_produced'].sum()
blocked_orders = len(df_orders[df_orders['production_status'].str.contains('Blocked')])

col1.metric("Avg Parts per Labor Hour", f"{avg_efficiency:.2f}")
col2.metric("Total Parts Produced (7 Days)", f"{total_production:,}")
col3.metric("Blocked Orders (Material Shortage)", blocked_orders, delta_color="inverse")

st.divider()

# --- Section 3: Daily Operations (Line Chart) ---
st.header("📈 Daily Labor Efficiency")
if not df_kpis.empty:
    fig_kpi = px.line(
        df_kpis, 
        x='operation_date', 
        y='parts_per_labor_hour',
        markers=True,
        title="Parts Produced Per Labor Hour Over Time",
        labels={'parts_per_labor_hour': 'Efficiency Rate', 'operation_date': 'Date'}
    )
    # Add a bar chart for total volume on the same figure
    fig_kpi.add_bar(x=df_kpis['operation_date'], y=df_kpis['total_parts_produced'], name="Total Volume")
    st.plotly_chart(fig_kpi, use_container_width=True)

st.divider()

# --- Section 4: Master Production Schedule (Table & Bar Chart) ---
st.header("📋 Master Production Schedule")

tab1, tab2 = st.tabs(["📊 Inventory Readiness", "🗄️ Raw Data Table"])

with tab1:
    # Visualize which orders are ready vs blocked
    status_counts = df_orders['production_status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Order Count']
    
    # Custom colors based on status string
    color_map = {
        '🟢 Ready for Production': '#28a745', 
        '🔴 Blocked: Material Shortage': '#dc3545'
    }
    
    fig_status = px.pie(
        status_counts, 
        values='Order Count', 
        names='Status',
        title="Production Readiness Breakdown",
        color='Status',
        color_discrete_map=color_map
    )
    st.plotly_chart(fig_status, use_container_width=True)

with tab2:
    st.dataframe(
        df_orders.style.map(
            lambda x: 'background-color: #ffcccc' if 'Blocked' in str(x) else 'background-color: #ccffcc' if 'Ready' in str(x) else '',
            subset=['production_status']
        ),
        use_container_width=True
    )