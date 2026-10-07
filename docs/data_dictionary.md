# Data Dictionary

All monetary values are AED. The simulation covers **2023-07-01 → 2026-06-30**.
Raw extracts live in `data/raw/`; the warehouse is `data/bi_platform.db`;
Power BI copies are in `powerbi/data/` (same schemas, PascalCase file names).

## Raw extracts (before cleaning)

| File | ~Rows | Content |
|---|---|---|
| `sales_transactions.csv` | ~1,000,000 | POS/e-com line items — **contains deliberate defects** (duplicates, mixed date formats, missing customer IDs, negative qty, zero prices, messy payment labels) |
| `returns.csv` | ~35,000 | product returns incl. a fraud burst |
| `customers.csv` | 40,000 | loyalty members (city casing issues, duplicate emails) |
| `products.csv` | 320 | product master with cost & price |
| `stores.csv` | 18 | 16 physical + 2 online stores |
| `suppliers.csv` | 40 | supplier master |
| `marketing_spend.csv` | ~5,500 | daily spend per channel & campaign |
| `web_traffic.csv` | ~1,100 | daily e-commerce sessions & conversion |
| `inventory_snapshots.csv` | ~200,000 | monthly stock per store × product |

## Warehouse — dimensions

### dim_date
| Column | Type | Notes |
|---|---|---|
| date_key | TEXT PK | `YYYY-MM-DD` |
| date, year, month, month_name, year_month, quarter | | calendar |
| day_of_week, day_name | | 1 = Monday |
| is_weekend | INT | Fri–Sun (GCC retail peak) |
| is_ramadan, is_eid | INT | approximate Hijri windows |
| retail_event | TEXT | DSF, White Friday, Back to School, National Day, Eid, Ramadan or '' |

### dim_store
`store_id` PK, store_name, city, country (UAE/KSA/Bahrain), store_type
(Flagship/Mall/Street/Online), sqm, opened_date.

### dim_product
`product_id` PK, product_name, category (8), subcategory, brand, unit_price,
unit_cost, margin_pct, launch_date, supplier_id → dim_supplier.

### dim_customer
`customer_id` PK, first/last name, gender, birth_year, age_band, city,
join_date, email, dup_email_flag.

### dim_supplier
`supplier_id` PK, supplier_name, country, lead_time_days, reliability_score.

## Warehouse — facts

### fact_sales (~1M rows, line grain)
| Column | Notes |
|---|---|
| transaction_id | PK (line) |
| order_id | groups lines into orders |
| date_key, order_time | FK dim_date + HH:MM |
| store_id, customer_id, product_id | FKs (customer NULL = guest) |
| quantity, unit_price, discount_pct | as sold |
| gross_amount | qty × price |
| discount_amount | gross × discount% |
| net_amount | gross − discount |
| cost_amount | qty × unit_cost |
| margin_amount | net − cost |
| payment_method | Card, Cash, Apple Pay, Tabby, PayPal |
| sales_channel | In-Store / Online |

### fact_returns
return_id PK, transaction_id FK, date_key, store_id, product_id, customer_id,
qty_returned, refund_amount, reason.

### fact_marketing
date, channel (5), campaign, spend_aed, impressions, clicks.

### fact_web_traffic
date, sessions, unique_visitors, new_visitor_pct, bounce_rate,
avg_session_sec, online_orders, conversion_rate.

### fact_inventory
snapshot_month, store_id, product_id, units_sold_month, units_on_hand,
stockout_days.

## Aggregates (dashboard speed)

- `agg_daily_kpis` — per day: orders, units, gross/net revenue, discounts,
  margin, customers, returns_qty, refunds, marketing_spend.
- `agg_daily_store` — per day × store: orders, units, net_revenue, margin.
- `agg_daily_category` — per day × category: orders, units, net_revenue, margin.
- `agg_daily_store_returns` — per day × store: returns_qty, refunds.

## ML outputs

- `forecast_daily` — date_key, scope (company or category), actual, forecast,
  lo, hi (95% band), model, kind (history/forecast).
- `forecast_metrics` — model, scope, mape, rmse, is_champion.
- `anomalies` — anomaly_id, date_key, store_id (or ALL), metric, method,
  value, expected, score, severity (Low→Critical), description.
- `anomaly_ground_truth` / `anomaly_validation` — injected incidents and
  whether the detectors caught them.
- `customer_segments` — customer_id, recency, frequency, monetary,
  first_purchase, tenure_days, segment, churn_risk (0–1), clv_annual + identity
  columns for display.
- `segment_profiles` — per segment: customers, averages, total_revenue,
  revenue_share_pct.

## Ops tables

- `dq_log` — issue, rows_affected, action (the ETL remediation report).
- `pipeline_runs` — stage, seconds, rows_out, run_at.

## Injected ground truth (for the defense)

| Incident | When | Where |
|---|---|---|
| POS outage (−90%) | 2024-05-14 | S03 Deira City Centre |
| Power outage (−75%) | 2024-09-17 | S12 Riyadh Park |
| Warehouse flood (−65%) | 2025-02-10 → 12 | S09, S10 (Sharjah) |
| Mega flash sale (+75%) | 2025-06-15 | all stores |
| Pricing bug: Electronics −50% | 2025-09-03 | all stores (margin collapse) |
| White Friday online surge (+110%) | 2025-11-28 → 29 | S17, S18 |
| Returns-abuse burst | 2026-01-08 → 14 | S09 |
| Electronics stockout | 2025-10 | S01 (inventory table) |
