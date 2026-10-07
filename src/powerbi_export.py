"""
Power BI export module.

Dumps the warehouse star schema (plus ML outputs) to clean CSV files in
powerbi/data/ so the Power BI Desktop report can be built with a simple
Folder / CSV import. Column names are kept Power-BI friendly.

Run from the project root:
    python -m src.powerbi_export
"""
import sqlite3
import sys
import time
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import DB_PATH, POWERBI_DATA_DIR

EXPORTS = [
    # table_in_sqlite, csv_name
    ("dim_date", "DimDate.csv"),
    ("dim_store", "DimStore.csv"),
    ("dim_product", "DimProduct.csv"),
    ("dim_customer", "DimCustomer.csv"),
    ("dim_supplier", "DimSupplier.csv"),
    ("fact_sales", "FactSales.csv"),
    ("fact_returns", "FactReturns.csv"),
    ("fact_marketing", "FactMarketing.csv"),
    ("fact_web_traffic", "FactWebTraffic.csv"),
    ("fact_inventory", "FactInventory.csv"),
    ("forecast_daily", "MLForecast.csv"),
    ("forecast_metrics", "MLForecastMetrics.csv"),
    ("anomalies", "MLAnomalies.csv"),
    ("anomaly_validation", "MLAnomalyValidation.csv"),
    ("customer_segments", "MLCustomerSegments.csv"),
    ("segment_profiles", "MLSegmentProfiles.csv"),
    ("dq_log", "PipelineDataQuality.csv"),
    ("pipeline_runs", "PipelineRuns.csv"),
]


def main():
    t0 = time.time()
    print("=" * 60)
    print("Power BI Export")
    print("=" * 60)
    con = sqlite3.connect(DB_PATH)
    for table, csv_name in EXPORTS:
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", con)
        except Exception as e:
            print(f"  SKIP {table}: {e}")
            continue
        path = POWERBI_DATA_DIR / csv_name
        df.to_csv(path, index=False, encoding="utf-8-sig")  # BOM helps Power BI detect UTF-8
        print(f"  {csv_name:28s} {len(df):>10,} rows")
    con.close()
    print(f"\nDone in {time.time() - t0:.1f}s -> powerbi/data/")


if __name__ == "__main__":
    main()
