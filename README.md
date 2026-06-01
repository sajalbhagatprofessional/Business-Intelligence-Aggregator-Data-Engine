# 🏭 Business Intelligence Aggregator & Data Engine

> **Portfolio Objective:** Architected a data engine using SQL and Python to capture data from 15+ sources and integrate it into a comprehensive master report for production scheduling. Automated the validation of data integrity between source systems and final business dashboards.

## 📖 Project Overview
This project simulates an enterprise-level ELT (Extract, Load, Transform) pipeline for a manufacturing company. It extracts siloed data from 15+ mock sources (JSON APIs and HR/ERP CSVs), stages the data in a SQL database, transforms it into actionable Master Views, and visualizes the results on an interactive web dashboard. 

Crucially, the pipeline includes an **automated data integrity auditor** to guarantee zero data loss between raw extraction and final business reporting.

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.x
* **Database:** SQLite (Easily scalable to PostgreSQL)
* **Data Processing:** `pandas`, `sqlalchemy`
* **Data Transformation:** SQL (Views, CTEs, Aggregations)
* **Visualization:** `streamlit`, `plotly`

## 📂 Repository Structure
* `generate_mock_data.py` - Generates 15+ realistic relational data sources (JSON telemetry, CSV shift logs, CSV inventory).
* `phase2_data_engine.py` - The ELT extraction engine that ingests flat files into SQL staging tables.
* `phase3_data_integration.py` - Executes SQL to clean, merge, and create the Master Production Views.
* `phase4_validation.py` - Automated auditing script that compares raw row counts/sums to final aggregated views.
* `phase5_dashboard.py` - The frontend Streamlit application.

## 🚀 How to Run Locally

1. **Clone the repository and install dependencies:**
   ```bash
   git clone https://github.com/YourUsername/BI-Aggregator-Engine.git
   cd BI-Aggregator-Engine
   pip install pandas sqlalchemy streamlit plotly
   ```

2. **Execute the Data Pipeline**
   Run the following scripts in sequence to build the database from scratch:

   ```bash
   # Phase 1: Generate 15+ mock raw data files in a new directory
   python generate_mock_data.py

   # Phase 2: Extract data and load into SQLite staging tables
   python phase2_data_engine.py

   # Phase 3: Execute SQL CTEs to create Master Views
   python phase3_data_integration.py

   # Phase 4: Run the automated data auditor
   python phase4_validation.py
   ```

3. **Launch the Business Dashboard**
   ```bash
   streamlit run phase5_dashboard.py
   ```

   The dashboard will automatically open in your default web browser at `http://localhost:8501`.

## 🛡️ Automated Data Validation & Auditing

A critical feature of this pipeline is its self-auditing capability. Before data is exposed to business users, the validation script ensures completeness and accuracy.

Sample Terminal Output from Pipeline Run:

```plaintext
--- 🛡️ Starting Automated Data Integrity Validation ---
Executing Tests...
✅ PASS | Order Pipeline Completeness | Raw Orders: 50, Final View Orders: 50
✅ PASS | Production Metric Accuracy | Raw Parts Sum: 12450, KPI View Sum: 12450

--- Validation Summary ---
🟢 SYSTEM HEALTHY: All data integrity checks passed. Safe to push to BI Dashboards.
```

