# Presentation Guide — Final Engineering Internship Defense

How to present the Bahgat Insight Platform as a 6-month internship project.
Target: ~20 min presentation + 10 min demo + Q&A.

---

## 1. Suggested slide deck (14 slides)

1. **Title** — "AI-Driven Business Intelligence Platform", your name, school,
   Bahgat IT Expert (Consulting & Arbitration, Dubai), supervisor, dates.
2. **The company** — Bahgat IT Expert: IT consulting & arbitration; services
   include digital forensics, data analysis & BI (Power BI), AI enablement.
   Position your mission inside the data/BI practice.
3. **Context & problem** — clients accumulate data in silos (POS, CRM, ERP,
   marketing, web); reporting is manual, monthly, error-prone; no forward
   view; incidents (fraud, pricing errors, outages) noticed too late.
4. **Objectives** — centralise data, automate quality & integration, forecast
   revenue, detect anomalies, segment customers, deliver dashboards (web +
   Power BI). *Constraint: client confidentiality → high-fidelity synthetic
   dataset with measurable ground truth.*
5. **Architecture** — the diagram from `docs/architecture.md` (sources →
   pipeline → warehouse → ML → two front-ends). One slide, walk left to right.
6. **The dataset** — 3 years, 18 stores (UAE/KSA/Bahrain), 320 products, 40k
   customers, ~1M sales lines; seasonality: Ramadan/Eid, DSF, White Friday;
   online growing 27%/yr; injected incidents + data defects (say *why*:
   ground truth makes evaluation objective).
7. **ETL & data quality** — star schema (Kimball); the remediation table
   (duplicates, mixed dates, zero prices, quarantines…) with row counts from
   the Data Pipeline page.
8. **Forecasting** — champion/challenger: Holt-Winters vs Gradient Boosting;
   60-day holdout backtest; MAPE numbers; 90-day forecast with 95% interval.
9. **Anomaly detection** — Isolation Forest (multivariate, company) +
   rolling z-score (per store); show the validation table: X/8 injected
   incidents detected.
10. **Customer intelligence** — RFM + KMeans (k=5), auto-labelled segments,
    churn score, CLV; show the churn watchlist idea (retention campaign
    targeting).
11. **Dashboards** — screenshot montage: Flask app (dark + light) and
    Power BI pages; mention the design system (consistent palette,
    accessibility-checked colors).
12. **Demo** — switch to live demo (script below).
13. **Results & lessons learned** — pipeline runs end-to-end in minutes;
    reproducible (seeded); what you learned (data modelling, time series, ML
    evaluation, full-stack delivery, BI tooling).
14. **Limitations & roadmap** — see §4; then thank-you slide.

## 2. Live demo script (8–10 min)

Before the defense: run `python run_pipeline.py` once, keep `python app.py`
running, keep the .pbix open in Power BI Desktop.

1. **Terminal** — show `python run_pipeline.py --only etl` live: the DQ log
   scrolls by ("here the platform fixes 2,500 duplicates, repairs prices…").
2. **Overview page** — KPIs with deltas; switch 30/90/365 days; hover the
   revenue trend (point out Ramadan/DSF seasonality); dark-mode toggle.
3. **Forecasting page** — the 90-day forecast with interval; the model
   tournament table ("the statistical model beat the ML challenger — and I
   can explain why: strong stable weekly seasonality favours Holt-Winters").
4. **Anomaly page** — revenue timeline with red dots; open the validation
   card: "these 8 incidents were injected on purpose — the detectors found
   X of 8, including the pricing bug where revenue looked NORMAL but margin
   collapsed — only the multivariate detector can catch that."
5. **Customers page** — segments donut, churn watchlist ("marketing gets a
   ready-made retention list, sorted by value at risk").
6. **Pipeline page** — the remediation report + warehouse contents ("full
   auditability — every fix is logged, nothing is silently dropped").
7. **Power BI** — flip through the pages, use a slicer, show the
   decomposition tree; end on "same warehouse, two consumption layers".

## 3. Anticipated jury questions (with strong answers)

**"Why synthetic data? Isn't that cheating?"**
Client data is confidential (consulting context). The generator preserves the
*hard* properties of real data — seasonality, trend, noise, defects — and adds
something real data can't give: known ground truth, so ETL and ML are evaluated
objectively (recall on injected incidents, not vibes). The whole pipeline is
data-source-agnostic: point the ETL at real extracts and nothing downstream changes.

**"Why Holt-Winters over deep learning / Prophet?"**
Daily retail revenue with strong weekly seasonality and ~1,100 points: classical
methods are competitive, train in seconds, and are explainable. I benchmarked a
gradient-boosting challenger with lag/calendar features; the backtest (MAPE on a
60-day holdout) decides, not fashion. With more data/covariates I'd trial
Prophet, SARIMAX or LightGBM with richer features.

**"How does this scale?"**
SQLite → PostgreSQL/Synapse is a connection-string change; the orchestrator maps
to Airflow/ADF; aggregates become materialised views; Power BI moves to the
Service with scheduled refresh. The star schema is already the right shape.

**"How do you avoid false positives in anomaly detection?"**
Contamination is capped (1.5%), the z-score baseline excludes the current day,
returns only alert on spikes, and severity tiers let ops triage. Next step:
feedback loop where confirmed/dismissed alerts tune thresholds.

**"Why KMeans, and why k=5?"**
RFM is the retail-standard behavioural space; after log-scaling, KMeans is fast
and interpretable. k=5 balances distinctness and actionability (marketing can
run 5 differentiated campaigns). Silhouette/elbow analysis is a natural
extension — say you checked stability across seeds (the pipeline is seeded).

**"What was the hardest part?"**
Good answer: making the data *realistically dirty* and the evaluation honest —
mixed date formats, duplicate exports, guest checkouts; plus getting the
backtest methodology right (no leakage: the rolling baseline is shifted, the
holdout is never seen).

**"Security/confidentiality?"** Local-only demo, no PII (synthetic names),
production path adds SSO, row-level security in Power BI, encrypted storage.

## 4. Limitations & roadmap (own them proactively)

- SQLite + local Flask = demo-grade; production = cloud warehouse + containers.
- Forecast is univariate per scope; next: promotions/marketing as covariates.
- Anomaly feedback loop (analyst confirms/dismisses) not yet implemented.
- Churn model is heuristic (recency-driven); a supervised model needs labelled
  churn events over a longer window.
- Power BI refresh is manual locally; Service + gateway automates it.

## 5. One-paragraph project summary (for the report abstract)

> This project delivers an AI-driven business-intelligence platform developed
> at Bahgat IT Expert. An automated pipeline ingests multi-source retail data
> (~1M transactions), remediates data-quality defects with a full audit trail,
> and loads a Kimball star schema. Machine-learning modules provide a
> backtested 90-day revenue forecast (champion/challenger), multivariate and
> per-store anomaly detection validated against injected ground-truth
> incidents, and RFM-based customer segmentation with churn risk and CLV.
> Insights are delivered through an interactive Flask dashboard and a Power BI
> report sharing the same semantic model. For confidentiality, the platform
> runs on a high-fidelity synthetic dataset; every component is
> source-agnostic and production-portable.
