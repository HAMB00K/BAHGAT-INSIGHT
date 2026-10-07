"""
ETL pipeline: raw CSV extracts  ->  clean star schema in SQLite.

Stages
------
1. EXTRACT   read the 9 raw CSV files produced by the source systems
             (here: the synthetic generator).
2. TRANSFORM data-quality remediation with full audit trail:
               - deduplicate POS double-exports
               - normalise mixed date formats (YYYY-MM-DD vs DD/MM/YYYY)
               - repair zero prices from the product master
               - quarantine impossible rows (negative quantities)
               - normalise categorical labels (payment methods, cities)
             then derive business measures (gross/net revenue, margin).
3. LOAD      star schema (dim_* / fact_*) + pre-computed aggregate tables
             into SQLite, with indexes for dashboard latency.

Every run is logged to the `pipeline_runs` table and every fix is counted
in the `dq_log` table - both are displayed on the "Data Pipeline" page of
the web app.

Run from the project root:
    python -m src.etl.pipeline
"""
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import RAW_DIR, DB_PATH, LOG_DIR
from src.data_generation.generate_data import (
    RAMADAN, EID, DSF, WHITE_FRIDAY, BACK_TO_SCHOOL, NATIONAL_DAY,
    ANOMALY_EVENTS, PRICING_BUG_DAY, FRAUD_RETURN_WINDOW, FRAUD_RETURN_STORE,
    _in_ranges,
)

PAYMENT_CANONICAL = {
    "card": "Card", "cash": "Cash", "apple pay": "Apple Pay",
    "tabby": "Tabby", "paypal": "PayPal",
}


def parse_mixed_dates(s: pd.Series) -> pd.Series:
    """Parse a column that mixes YYYY-MM-DD and DD/MM/YYYY strings."""
    d = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    mask = d.isna()
    if mask.any():
        d = d.copy()
        d[mask] = pd.to_datetime(s[mask], format="%d/%m/%Y", errors="coerce")
    return d


class Pipeline:
    def __init__(self):
        self.dq = []          # (issue, rows_affected, action)
        self.runs = []        # (stage, seconds, rows_out)
        self.t_start = time.time()

    def log_dq(self, issue, rows, action):
        self.dq.append({"issue": issue, "rows_affected": int(rows), "action": action})
        print(f"    DQ: {issue:38s} {rows:>8,} rows -> {action}")

    def stage(self, name, seconds, rows):
        self.runs.append({"stage": name, "seconds": round(seconds, 2), "rows_out": int(rows)})
        print(f"  [{name}] done in {seconds:.1f}s ({rows:,} rows)")

    # ------------------------------------------------------------------ EXTRACT
    def extract(self):
        t = time.time()
        self.raw = {}
        for name in ["stores", "products", "customers", "suppliers", "sales_transactions",
                     "returns", "marketing_spend", "web_traffic", "inventory_snapshots"]:
            self.raw[name] = pd.read_csv(RAW_DIR / f"{name}.csv", dtype=str, keep_default_na=False)
        rows = sum(len(v) for v in self.raw.values())
        self.stage("EXTRACT", time.time() - t, rows)

    # ---------------------------------------------------------------- TRANSFORM
    def transform(self):
        t = time.time()
        self.clean_sales()
        self.clean_customers()
        self.clean_returns()
        self.clean_secondary()
        self.stage("TRANSFORM", time.time() - t, len(self.sales))

    def clean_sales(self):
        df = self.raw["sales_transactions"].copy()
        n0 = len(df)

        # numeric types
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").fillna(0)

        # 1. duplicates (same transaction_id exported twice)
        dup_mask = df.duplicated(subset="transaction_id", keep="first")
        self.log_dq("Duplicate transaction rows", dup_mask.sum(), "dropped (kept first)")
        df = df[~dup_mask].copy()

        # 2. mixed date formats
        iso = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
        n_bad_fmt = iso.isna().sum()
        d2 = pd.to_datetime(df.loc[iso.isna(), "order_date"], format="%d/%m/%Y", errors="coerce")
        iso = iso.copy()
        iso[iso.isna()] = d2
        df["order_date"] = iso
        self.log_dq("Non-ISO date formats (DD/MM/YYYY)", n_bad_fmt, "normalised to ISO")
        unparsed = df["order_date"].isna().sum()
        if unparsed:
            self.log_dq("Unparseable dates", unparsed, "row quarantined")
            df = df[df["order_date"].notna()].copy()

        # 3. negative quantities -> quarantine (they are errors, real returns live in returns.csv)
        neg = df["quantity"] <= 0
        self.log_dq("Negative/zero quantity", neg.sum(), "row quarantined")
        self.quarantined = df[neg].copy()
        df = df[~neg].copy()

        # 4. zero / missing price -> repair from product master
        products = self.raw["products"][["product_id", "unit_price", "unit_cost", "category",
                                         "subcategory", "brand", "product_name"]].copy()
        products["unit_price"] = pd.to_numeric(products["unit_price"], errors="coerce")
        products["unit_cost"] = pd.to_numeric(products["unit_cost"], errors="coerce")
        price_map = products.set_index("product_id")["unit_price"]
        bad_price = (df["unit_price"].isna()) | (df["unit_price"] <= 0)
        df.loc[bad_price, "unit_price"] = df.loc[bad_price, "product_id"].map(price_map)
        self.log_dq("Zero/invalid unit price", bad_price.sum(), "repaired from product master")

        # 5. payment labels
        raw_pm = df["payment_method"]
        canon = raw_pm.str.strip().str.lower().map(PAYMENT_CANONICAL)
        fixed = (canon.notna()) & (canon != raw_pm)
        self.log_dq("Messy payment labels", fixed.sum(), "normalised")
        df["payment_method"] = canon.fillna("Other")

        # 6. missing customer ids -> explicit NULL (guest checkout)
        blank = df["customer_id"].str.strip() == ""
        self.log_dq("Missing customer id", blank.sum(), "set to NULL (guest)")
        df["customer_id"] = df["customer_id"].str.strip().replace("", np.nan)

        # ---- derive measures
        cost_map = products.set_index("product_id")["unit_cost"]
        df["unit_cost"] = df["product_id"].map(cost_map)
        df["gross_amount"] = df["quantity"] * df["unit_price"]
        df["discount_amount"] = df["gross_amount"] * df["discount_pct"] / 100.0
        df["net_amount"] = df["gross_amount"] - df["discount_amount"]
        df["cost_amount"] = df["quantity"] * df["unit_cost"]
        df["margin_amount"] = df["net_amount"] - df["cost_amount"]
        for c in ["gross_amount", "discount_amount", "net_amount", "cost_amount", "margin_amount"]:
            df[c] = df[c].round(2)
        df["date_key"] = df["order_date"].dt.strftime("%Y-%m-%d")

        self.sales = df
        self.log_dq("Rows in / rows out", n0 - len(df), f"net rows removed ({n0:,} -> {len(df):,})")

    def clean_customers(self):
        df = self.raw["customers"].copy()
        messy = ~df["city"].isin(["Dubai", "Abu Dhabi", "Sharjah", "Ras Al Khaimah",
                                  "Riyadh", "Jeddah", "Manama"])
        self.log_dq("Inconsistent city casing (customers)", messy.sum(), "normalised to Title Case")
        df["city"] = df["city"].str.strip().str.title()
        df["birth_year"] = pd.to_numeric(df["birth_year"], errors="coerce")
        current_year = 2026
        df["age"] = current_year - df["birth_year"]
        df["age_band"] = pd.cut(df["age"], bins=[0, 24, 34, 44, 54, 200],
                                labels=["18-24", "25-34", "35-44", "45-54", "55+"]).astype(str)
        dup_email = df.duplicated(subset="email", keep=False) & (df["email"] != "")
        self.log_dq("Duplicate customer emails", dup_email.sum(), "flagged for review")
        df["dup_email_flag"] = dup_email.astype(int)
        self.customers = df

    def clean_returns(self):
        df = self.raw["returns"].copy()
        df["qty_returned"] = pd.to_numeric(df["qty_returned"], errors="coerce").fillna(1)
        df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
        # join back to cleaned sales to price the refund
        s = self.sales[["transaction_id", "store_id", "product_id", "customer_id",
                        "unit_price", "discount_pct"]]
        df = df.merge(s, on="transaction_id", how="left")
        orphans = df["unit_price"].isna().sum()
        self.log_dq("Orphan returns (no matching sale)", orphans, "quarantined")
        df = df[df["unit_price"].notna()]
        df["refund_amount"] = (df["qty_returned"] * df["unit_price"] *
                               (1 - df["discount_pct"] / 100.0)).round(2)
        df["date_key"] = df["return_date"].dt.strftime("%Y-%m-%d")
        self.returns = df

    def clean_secondary(self):
        m = self.raw["marketing_spend"].copy()
        for c in ["spend_aed", "impressions", "clicks"]:
            m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0)
        self.marketing = m

        w = self.raw["web_traffic"].copy()
        for c in ["sessions", "unique_visitors", "online_orders", "avg_session_sec"]:
            w[c] = pd.to_numeric(w[c], errors="coerce").fillna(0).astype(int)
        for c in ["new_visitor_pct", "bounce_rate", "conversion_rate"]:
            w[c] = pd.to_numeric(w[c], errors="coerce").fillna(0)
        self.web = w

        inv = self.raw["inventory_snapshots"].copy()
        for c in ["units_sold_month", "units_on_hand", "stockout_days"]:
            inv[c] = pd.to_numeric(inv[c], errors="coerce").fillna(0).astype(int)
        self.inventory = inv

        sup = self.raw["suppliers"].copy()
        sup["lead_time_days"] = pd.to_numeric(sup["lead_time_days"], errors="coerce")
        sup["reliability_score"] = pd.to_numeric(sup["reliability_score"], errors="coerce")
        self.suppliers = sup

        st = self.raw["stores"].copy()
        st["sqm"] = pd.to_numeric(st["sqm"], errors="coerce")
        self.stores = st

        p = self.raw["products"].copy()
        p["unit_price"] = pd.to_numeric(p["unit_price"], errors="coerce")
        p["unit_cost"] = pd.to_numeric(p["unit_cost"], errors="coerce")
        p["margin_pct"] = ((p["unit_price"] - p["unit_cost"]) / p["unit_price"] * 100).round(1)
        self.products = p

    # --------------------------------------------------------------------- LOAD
    def build_dim_date(self):
        dates = pd.date_range(self.sales["order_date"].min(), self.sales["order_date"].max(), freq="D")
        df = pd.DataFrame({"date_key": dates.strftime("%Y-%m-%d")})
        df["date"] = dates
        df["year"] = dates.year
        df["month"] = dates.month
        df["month_name"] = dates.strftime("%b")
        df["year_month"] = dates.strftime("%Y-%m")
        df["quarter"] = "Q" + dates.quarter.astype(str)
        df["day_of_week"] = dates.dayofweek + 1
        df["day_name"] = dates.strftime("%a")
        df["is_weekend"] = dates.dayofweek.isin([4, 5, 6]).astype(int)  # Fri-Sun GCC retail peak
        df["is_ramadan"] = _in_ranges(dates, RAMADAN).astype(int)
        df["is_eid"] = _in_ranges(dates, EID).astype(int)
        event = np.full(len(dates), "", dtype=object)
        for label, ranges in [("Dubai Shopping Festival", DSF), ("White Friday", WHITE_FRIDAY),
                              ("Back to School", BACK_TO_SCHOOL), ("National Day", NATIONAL_DAY),
                              ("Eid", EID), ("Ramadan", RAMADAN)]:
            mask = _in_ranges(dates, ranges) & (event == "")
            event[mask] = label
        df["retail_event"] = event
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df

    def build_aggregates(self):
        s = self.sales
        # daily company-level KPIs
        daily = s.groupby("date_key").agg(
            orders=("order_id", "nunique"),
            units=("quantity", "sum"),
            gross_revenue=("gross_amount", "sum"),
            discounts=("discount_amount", "sum"),
            net_revenue=("net_amount", "sum"),
            margin=("margin_amount", "sum"),
            customers=("customer_id", "nunique"),
        ).reset_index()
        ret_daily = self.returns.groupby("date_key").agg(
            returns_qty=("qty_returned", "sum"),
            refunds=("refund_amount", "sum"),
        ).reset_index()
        mkt_daily = self.marketing.groupby("date")["spend_aed"].sum().reset_index() \
            .rename(columns={"date": "date_key", "spend_aed": "marketing_spend"})
        daily = daily.merge(ret_daily, on="date_key", how="left") \
                     .merge(mkt_daily, on="date_key", how="left")
        daily[["returns_qty", "refunds", "marketing_spend"]] = \
            daily[["returns_qty", "refunds", "marketing_spend"]].fillna(0)
        self.agg_daily = daily.round(2)

        # daily x store
        self.agg_daily_store = s.groupby(["date_key", "store_id"]).agg(
            orders=("order_id", "nunique"), units=("quantity", "sum"),
            net_revenue=("net_amount", "sum"), margin=("margin_amount", "sum"),
        ).reset_index().round(2)

        # daily x category
        cat_map = self.products.set_index("product_id")["category"]
        s2 = s[["date_key", "product_id", "quantity", "net_amount", "margin_amount", "order_id"]].copy()
        s2["category"] = s2["product_id"].map(cat_map)
        self.agg_daily_category = s2.groupby(["date_key", "category"]).agg(
            orders=("order_id", "nunique"), units=("quantity", "sum"),
            net_revenue=("net_amount", "sum"), margin=("margin_amount", "sum"),
        ).reset_index().round(2)

        # daily x store for returns (fraud detection view)
        self.agg_daily_store_returns = self.returns.groupby(["date_key", "store_id"]).agg(
            returns_qty=("qty_returned", "sum"), refunds=("refund_amount", "sum"),
        ).reset_index().round(2)

    def load(self):
        t = time.time()
        dim_date = self.build_dim_date()
        self.build_aggregates()

        if DB_PATH.exists():
            DB_PATH.unlink()
        con = sqlite3.connect(DB_PATH)

        fact_sales = self.sales[[
            "transaction_id", "order_id", "date_key", "order_time", "store_id",
            "customer_id", "product_id", "quantity", "unit_price", "discount_pct",
            "gross_amount", "discount_amount", "net_amount", "cost_amount",
            "margin_amount", "payment_method", "sales_channel",
        ]]
        fact_returns = self.returns[[
            "return_id", "transaction_id", "date_key", "store_id", "product_id",
            "customer_id", "qty_returned", "refund_amount", "reason",
        ]]

        tables = {
            "dim_date": dim_date,
            "dim_store": self.stores,
            "dim_product": self.products,
            "dim_customer": self.customers.drop(columns=["age"], errors="ignore"),
            "dim_supplier": self.suppliers,
            "fact_sales": fact_sales,
            "fact_returns": fact_returns,
            "fact_marketing": self.marketing,
            "fact_web_traffic": self.web,
            "fact_inventory": self.inventory,
            "agg_daily_kpis": self.agg_daily,
            "agg_daily_store": self.agg_daily_store,
            "agg_daily_category": self.agg_daily_category,
            "agg_daily_store_returns": self.agg_daily_store_returns,
        }
        total_rows = 0
        for name, df in tables.items():
            df.to_sql(name, con, if_exists="replace", index=False, chunksize=50_000)
            total_rows += len(df)
            print(f"    loaded {name:26s} {len(df):>10,} rows")

        # ground truth of injected anomalies (used to validate the ML detector)
        gt = pd.DataFrame(
            [{"label": e["label"], "start": e["start"], "end": e["end"],
              "stores": ",".join(e["stores"]) if isinstance(e["stores"], list) else "ALL"}
             for e in ANOMALY_EVENTS] +
            [{"label": "Pricing bug: Electronics -50%", "start": PRICING_BUG_DAY,
              "end": PRICING_BUG_DAY, "stores": "ALL"},
             {"label": "Returns-abuse burst", "start": FRAUD_RETURN_WINDOW[0],
              "end": FRAUD_RETURN_WINDOW[1], "stores": FRAUD_RETURN_STORE}]
        )
        gt.to_sql("anomaly_ground_truth", con, if_exists="replace", index=False)

        # data-quality + run logs
        pd.DataFrame(self.dq).to_sql("dq_log", con, if_exists="replace", index=False)

        cur = con.cursor()
        for idx_sql in [
            "CREATE INDEX idx_fs_date ON fact_sales(date_key)",
            "CREATE INDEX idx_fs_store ON fact_sales(store_id)",
            "CREATE INDEX idx_fs_product ON fact_sales(product_id)",
            "CREATE INDEX idx_fs_customer ON fact_sales(customer_id)",
            "CREATE INDEX idx_fr_date ON fact_returns(date_key)",
            "CREATE INDEX idx_ads_date ON agg_daily_store(date_key)",
            "CREATE INDEX idx_adc_date ON agg_daily_category(date_key)",
        ]:
            cur.execute(idx_sql)
        con.commit()

        self.stage("LOAD", time.time() - t, total_rows)

        self.runs.append({"stage": "TOTAL", "seconds": round(time.time() - self.t_start, 2),
                          "rows_out": total_rows})
        runs_df = pd.DataFrame(self.runs)
        runs_df["run_at"] = datetime.now().isoformat(timespec="seconds")
        runs_df.to_sql("pipeline_runs", con, if_exists="replace", index=False)
        con.close()

        with open(LOG_DIR / "etl_report.json", "w", encoding="utf-8") as f:
            json.dump({"dq_log": self.dq, "stages": self.runs}, f, indent=2)


def main():
    print("=" * 60)
    print("Bahgat Insight Platform - ETL Pipeline")
    print("=" * 60)
    p = Pipeline()
    p.extract()
    p.transform()
    p.load()
    print(f"\nWarehouse ready -> {DB_PATH}")
    print("Reports -> logs/etl_report.json, tables dq_log / pipeline_runs")


if __name__ == "__main__":
    main()
