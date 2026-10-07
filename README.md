# Bahgat Insight Platform

**AI-Driven Business Intelligence Platform** — 6-month engineering internship
project at **Bahgat IT Expert** (Consulting & Arbitration, Dubai).

The platform transforms raw multi-source business data into actionable insight
for decision-makers: automated data pipelines, a star-schema warehouse, machine
learning (forecasting, anomaly detection, customer segmentation) and two
dashboard front-ends — an interactive **Flask web app** and a **Power BI report**.

> Because real client data is confidential, the platform runs on a fully
> synthetic — but realistic — dataset simulating *Al Noor Retail Group*, a
> fictional omni-channel retailer with 18 stores across the UAE, KSA and
> Bahrain (~1M sales line items over 3 years, seasonality, promotions,
> injected incidents and data-quality issues).

---

## Quick start

```bash
# 1. install dependencies (Python 3.10+)
pip install -r requirements.txt

# 2. run the full pipeline (~2-5 min): generate data -> ETL -> ML -> Power BI export
python run_pipeline.py

# 3. launch the dashboard
python app.py
# -> http://127.0.0.1:5000
```

Useful pipeline options:

```bash
python run_pipeline.py --skip-gen      # reuse existing raw data
python run_pipeline.py --only etl      # single stage: gen | etl | forecast | anomaly | segment | powerbi
```

The web dashboard loads chart libraries (ApexCharts, Lucide) from a CDN — the
first launch needs an internet connection.

## What's inside

| Layer | Tech | Where |
|---|---|---|
| Synthetic data generator | NumPy / pandas, seeded | `src/data_generation/` |
| ETL + data quality | pandas → SQLite star schema | `src/etl/pipeline.py` |
| Revenue forecasting | Holt-Winters vs Gradient Boosting, backtested | `src/ml/forecasting.py` |
| Anomaly detection | Isolation Forest + rolling z-score, validated vs ground truth | `src/ml/anomaly_detection.py` |
| Customer segmentation | RFM + KMeans, churn risk, CLV | `src/ml/segmentation.py` |
| Web dashboard (6 pages) | Flask + shadcn-style UI + ApexCharts | `app.py`, `templates/`, `static/` |
| Power BI report (5+ pages) | Star-schema CSVs, theme, DAX library, build guide | `powerbi/` |
| Documentation | Architecture, data dictionary, presentation guide | `docs/` |

## Dashboard pages

1. **Executive Overview** — KPIs with period-over-period deltas, revenue trend,
   category mix, store ranking, latest ML alerts.
2. **Sales Analytics** — monthly performance, margin rate, channel mix, payment
   methods, top products (filterable), e-commerce funnel.
3. **Forecasting** — 90-day revenue forecast with 95% interval, champion vs
   challenger backtest (MAPE/RMSE), per-category accuracy.
4. **Anomaly Detection** — revenue timeline with flagged days, alert log with
   severity, and validation against the incidents injected in the data.
5. **Customer Intelligence** — RFM segments, value/engagement map, demographics,
   churn watchlist with CLV.
6. **Data Pipeline** — pipeline stages and timings, data-quality remediation
   report, warehouse contents.

## Repository layout

```
├── run_pipeline.py            # one-command orchestrator
├── app.py                     # Flask dashboard
├── requirements.txt
├── src/
│   ├── config.py              # paths + business/model constants
│   ├── data_generation/generate_data.py
│   ├── etl/pipeline.py
│   ├── ml/{forecasting,anomaly_detection,segmentation}.py
│   └── powerbi_export.py
├── templates/  static/        # web UI (shadcn-style, ApexCharts)
├── data/                      # raw CSVs + bi_platform.db (generated)
├── powerbi/                   # theme, DAX, build guide + data/ exports (generated)
├── logs/                      # generation manifest + ETL report (generated)
└── docs/                      # architecture, data dictionary, presentation guide
```

## Documentation

- [docs/architecture.md](docs/architecture.md) — system design & data flow
- [docs/data_dictionary.md](docs/data_dictionary.md) — every table & column
- [docs/presentation_guide.md](docs/presentation_guide.md) — slide plan, demo script, Q&A prep
- [powerbi/POWERBI_BUILD_GUIDE.md](powerbi/POWERBI_BUILD_GUIDE.md) — Power BI step-by-step
