# Power BI Report — Build Guide

Step-by-step instructions to build the **Bahgat Insight** Power BI report
(5 pages) on top of the CSVs exported by the pipeline. Total build time:
roughly 2–3 hours the first time.

> Prerequisite: run `python run_pipeline.py` once — it fills `powerbi/data/`
> with 18 clean CSV files (star schema + ML outputs).

---

## 1. Load the data

1. Open **Power BI Desktop** → blank report → **Get data → Text/CSV**.
2. Import every file from `powerbi/data/`:
   - Dimensions: `DimDate`, `DimStore`, `DimProduct`, `DimCustomer`, `DimSupplier`
   - Facts: `FactSales`, `FactReturns`, `FactMarketing`, `FactWebTraffic`, `FactInventory`
   - ML outputs: `MLForecast`, `MLForecastMetrics`, `MLAnomalies`,
     `MLAnomalyValidation`, `MLCustomerSegments`, `MLSegmentProfiles`
   - Ops: `PipelineDataQuality`, `PipelineRuns`
3. In Power Query, check the column types (dates as Date, amounts as Decimal),
   then **Close & Apply**.

## 2. Model (star schema)

Open the **Model** view and create these single-direction, many-to-one
relationships (fact → dimension):

| Fact table (many) | Column | Dimension (one) | Column |
|---|---|---|---|
| FactSales | date_key | DimDate | date_key |
| FactSales | store_id | DimStore | store_id |
| FactSales | product_id | DimProduct | product_id |
| FactSales | customer_id | DimCustomer | customer_id |
| FactReturns | date_key | DimDate | date_key |
| FactReturns | store_id | DimStore | store_id |
| FactReturns | product_id | DimProduct | product_id |
| FactMarketing | date | DimDate | date |
| FactWebTraffic | date | DimDate | date |
| FactInventory | store_id / product_id | DimStore / DimProduct | store_id / product_id |
| MLForecast | date_key | DimDate | date_key |
| MLAnomalies | date_key / store_id | DimDate / DimStore | date_key / store_id |
| MLCustomerSegments | customer_id | DimCustomer | customer_id |
| DimProduct | supplier_id | DimSupplier | supplier_id |

Then:
- Select **DimDate** → *Table tools → Mark as date table* → column `date`.
- Hide the key columns on the fact side (right-click → Hide) for a clean field list.

## 3. Theme & measures

1. **View → Themes → Browse for themes** → select `powerbi/BahgatTheme.json`.
2. **Home → Enter data** → create an empty table named `_Measures`.
3. Open `powerbi/DAX_measures.dax` and add each measure to `_Measures`
   (*Modeling → New measure*, paste one measure at a time).
4. Format currency measures as `AED #,0` (Measure tools → Format), the
   `%` measures as Percentage with 1 decimal.

## 4. Report pages

### Page 1 — Executive Overview
- **Slicer** (top strip): DimDate[date] as "Between" slider; DimStore[country] as buttons.
- **6 KPI cards**: `Net Revenue`, `Orders`, `Avg Order Value`, `Margin Rate %`,
  `Active Customers`, `Return Rate %`. Add trend sparkline (card visual → sparkline)
  on Net Revenue.
- **Line chart**: Net Revenue by DimDate[date]; add `Revenue 7d Avg` as second line.
- **Donut**: Net Revenue by DimProduct[category].
- **Bar chart**: Net Revenue by DimStore[store_name] (Top N = 8 filter).
- **Map** (optional): Net Revenue by DimStore[city].
- **KPI vs LY**: card with `Revenue YoY %`.

### Page 2 — Sales Deep-Dive
- **Slicers**: category, store, sales_channel, payment_method.
- **Clustered column**: Net Revenue by DimDate[year_month].
- **Line**: Margin Rate % by year_month (own visual — don't dual-axis it).
- **Stacked area**: Net Revenue by year_month, legend = FactSales[sales_channel].
- **Matrix**: rows = category → subcategory, values = Net Revenue, Units Sold,
  Margin Rate %, Return Rate % (conditional formatting: data bars on revenue,
  red font on Return Rate % > 5%).
- **Table**: Top products — DimProduct[product_name], Units, Net Revenue,
  Gross Margin, Top N filter 15 by Net Revenue.

### Page 3 — Forecast (ML)
- **Slicer**: MLForecast[scope] (default "company").
- **Line chart**: axis = DimDate[date] (or MLForecast[date_key]),
  values = `Actual (Forecast Table)`, `Forecast Revenue`, `Forecast Lower`,
  `Forecast Upper`. Style Lower/Upper in the light band colour `#86B6EF`,
  Forecast in `#1C5CAB`, Actual in `#2A78D6`.
  (Alternative: use an Area chart for the band by plotting Upper and Lower
  with the area between them shaded, or the built-in *Forecast* analytics pane
  for comparison.)
- **Cards**: `Forecast Next 30d`; MAPE — table visual of MLForecastMetrics
  (model, scope, mape, is_champion) with conditional icon on is_champion.
- **Text box**: one-paragraph method note (Holt-Winters vs Gradient Boosting,
  60-day holdout backtest).

### Page 4 — Anomalies & Risk (ML)
- **Cards**: `Anomaly Count`, `Critical Anomalies`, `Detection Recall %`.
- **Line + dots**: Net Revenue by date; overlay MLAnomalies as a scatter
  (combo visual: line = revenue, scatter = MLAnomalies[value] on same axis), or
  use conditional markers.
- **Table**: MLAnomalies — date_key, store_id, severity, method, description;
  conditional background on severity (Critical `#D03B3B`, High `#EC835A`,
  Medium `#FAB219`).
- **Table**: MLAnomalyValidation — label, start, end, detected (icon set ✓/✗).
- **Decomposition tree** (nice wow-effect): analyse Net Revenue by
  category → store → payment method.

### Page 5 — Customers (ML)
- **Donut**: customers by MLCustomerSegments[segment].
- **Bar**: `Segment Revenue` by segment.
- **Scatter**: MLCustomerSegments — x = frequency, y = monetary (log scale),
  legend = segment, size = clv_annual (set a Top N or sample filter if slow).
- **Cards**: `Avg CLV`, `High Risk Customers`, `Avg Churn Risk`.
- **Table**: churn watchlist — first_name, last_name, city, segment, monetary,
  churn_risk (data bars), clv_annual; filter churn_risk >= 0.5, sort by clv.
- **Column chart**: customers by DimCustomer[age_band], legend = gender.

### Optional Page 6 — Data Operations
- **Table**: PipelineDataQuality (issue, rows_affected, action).
- **Table**: PipelineRuns (stage, seconds, rows_out).
- **Bar**: FactInventory stockout_days by store (spot the Oct-2025 crisis at S01).

## 5. Polish checklist

- Page navigation: insert **Buttons → Navigator → Page navigator** on every page.
- Add the report title + "Bahgat IT Expert · Al Noor Retail Group (synthetic)" text box.
- Sync the date slicer across pages (View → Sync slicers).
- Set Page 1 as the default landing page; hide helper tables (`_Measures` stays visible).
- File → Options → Current file → *Data Load* → disable auto date/time (cleaner model).
- Save as `BahgatInsight.pbix` in the `powerbi/` folder.

## 6. Refresh story (for the defense)

The CSVs are regenerated by `python run_pipeline.py`; in Power BI a single
**Refresh** button re-reads them — so the "automated pipeline → BI" story is:
pipeline runs on a schedule (Task Scheduler / cron / Azure Data Factory in
production), Power BI dataset refreshes afterwards (Power BI Service scheduled
refresh with a gateway in production). Say exactly that when asked "how would
this run in production?".
