"""
Bahgat Insight Platform - Flask application.

Serves the interactive BI dashboard (6 pages) on top of the SQLite
warehouse built by run_pipeline.py. All analytics endpoints return JSON
consumed by the front-end (ApexCharts + vanilla JS).

Run from the project root (after `python run_pipeline.py`):
    python app.py            ->  http://127.0.0.1:5000
"""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

from src.config import DB_PATH, LOG_DIR, COMPANY_NAME, PLATFORM_NAME, CURRENCY

app = Flask(__name__)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def q(sql, params=()):
    """Query -> list of dicts."""
    cur = get_db().execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


def q1(sql, params=()):
    rows = q(sql, params)
    return rows[0] if rows else {}


def anchor_date():
    """The 'today' of the simulation = last day with sales."""
    return q1("SELECT MAX(date_key) AS d FROM agg_daily_kpis")["d"]


def window(days):
    """Return (start_iso, end_iso) for the last N days of data."""
    end = datetime.strptime(anchor_date(), "%Y-%m-%d").date()
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def prev_window(days):
    end = datetime.strptime(anchor_date(), "%Y-%m-%d").date() - timedelta(days=days)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def days_arg(default=90):
    try:
        d = int(request.args.get("days", default))
    except (TypeError, ValueError):
        d = default
    return max(7, min(d, 1200))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

PAGES = {
    "overview": "Executive Overview",
    "sales": "Sales Analytics",
    "forecast": "Forecasting",
    "anomalies": "Anomaly Detection",
    "customers": "Customer Intelligence",
    "pipeline": "Data Pipeline",
}


def render_page(page):
    return render_template(
        f"{page}.html", page=page, page_title=PAGES[page],
        company=COMPANY_NAME, platform=PLATFORM_NAME, currency=CURRENCY,
        anchor=anchor_date(),
    )


@app.route("/")
def overview():
    return render_page("overview")


@app.route("/sales")
def sales():
    return render_page("sales")


@app.route("/forecast")
def forecast():
    return render_page("forecast")


@app.route("/anomalies")
def anomalies():
    return render_page("anomalies")


@app.route("/customers")
def customers():
    return render_page("customers")


@app.route("/pipeline")
def pipeline():
    return render_page("pipeline")


# ---------------------------------------------------------------------------
# Meta / filters
# ---------------------------------------------------------------------------

@app.route("/api/meta")
def api_meta():
    stores = q("SELECT store_id, store_name, city, country, store_type FROM dim_store ORDER BY store_name")
    cats = q("SELECT DISTINCT category FROM dim_product ORDER BY category")
    return jsonify({
        "anchor": anchor_date(), "currency": CURRENCY,
        "company": COMPANY_NAME, "platform": PLATFORM_NAME,
        "stores": stores, "categories": [c["category"] for c in cats],
    })


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

@app.route("/api/kpis")
def api_kpis():
    days = days_arg(30)
    s, e = window(days)
    ps, pe = prev_window(days)

    cur = q1("""SELECT SUM(net_revenue) rev, SUM(orders) orders, SUM(margin) margin,
                       SUM(refunds) refunds, SUM(units) units, SUM(marketing_spend) mkt
                FROM agg_daily_kpis WHERE date_key BETWEEN ? AND ?""", (s, e))
    prv = q1("""SELECT SUM(net_revenue) rev, SUM(orders) orders, SUM(margin) margin,
                       SUM(refunds) refunds FROM agg_daily_kpis
                WHERE date_key BETWEEN ? AND ?""", (ps, pe))
    cust = q1("""SELECT COUNT(DISTINCT customer_id) c FROM fact_sales
                 WHERE date_key BETWEEN ? AND ? AND customer_id IS NOT NULL""", (s, e))
    cust_prev = q1("""SELECT COUNT(DISTINCT customer_id) c FROM fact_sales
                      WHERE date_key BETWEEN ? AND ? AND customer_id IS NOT NULL""", (ps, pe))

    def pct(a, b):
        if not b:
            return None
        return round((a - b) / b * 100, 1)

    rev, orders = cur["rev"] or 0, cur["orders"] or 0
    prev_rev, prev_orders = prv["rev"] or 0, prv["orders"] or 0
    aov = rev / orders if orders else 0
    prev_aov = prev_rev / prev_orders if prev_orders else 0
    margin_rate = (cur["margin"] or 0) / rev * 100 if rev else 0
    prev_margin_rate = (prv["margin"] or 0) / prev_rev * 100 if prev_rev else 0
    return_rate = (cur["refunds"] or 0) / rev * 100 if rev else 0
    prev_return_rate = (prv["refunds"] or 0) / prev_rev * 100 if prev_rev else 0

    return jsonify({
        "days": days, "start": s, "end": e,
        "kpis": [
            {"key": "revenue", "label": "Net Revenue", "value": round(rev, 0),
             "fmt": "currency", "delta": pct(rev, prev_rev)},
            {"key": "orders", "label": "Orders", "value": int(orders),
             "fmt": "int", "delta": pct(orders, prev_orders)},
            {"key": "aov", "label": "Avg Order Value", "value": round(aov, 1),
             "fmt": "currency", "delta": pct(aov, prev_aov)},
            {"key": "margin", "label": "Gross Margin", "value": round(margin_rate, 1),
             "fmt": "pct", "delta": round(margin_rate - prev_margin_rate, 1), "delta_pts": True},
            {"key": "customers", "label": "Active Customers", "value": int(cust["c"] or 0),
             "fmt": "int", "delta": pct(cust["c"] or 0, cust_prev["c"] or 0)},
            {"key": "returns", "label": "Return Rate", "value": round(return_rate, 2),
             "fmt": "pct", "delta": round(return_rate - prev_return_rate, 2),
             "delta_pts": True, "invert": True},
        ],
    })


# ---------------------------------------------------------------------------
# Trends & breakdowns
# ---------------------------------------------------------------------------

@app.route("/api/revenue_trend")
def api_revenue_trend():
    days = days_arg(90)
    s, e = window(days)
    gran = request.args.get("granularity", "day")
    if gran == "month":
        rows = q("""SELECT substr(date_key,1,7) AS label, SUM(net_revenue) rev,
                           SUM(margin) margin, SUM(orders) orders
                    FROM agg_daily_kpis WHERE date_key BETWEEN ? AND ?
                    GROUP BY 1 ORDER BY 1""", (s, e))
    elif gran == "week":
        rows = q("""SELECT MIN(date_key) AS label, SUM(net_revenue) rev,
                           SUM(margin) margin, SUM(orders) orders
                    FROM agg_daily_kpis WHERE date_key BETWEEN ? AND ?
                    GROUP BY strftime('%Y-%W', date_key) ORDER BY 1""", (s, e))
    else:
        rows = q("""SELECT date_key AS label, net_revenue rev, margin, orders
                    FROM agg_daily_kpis WHERE date_key BETWEEN ? AND ?
                    ORDER BY date_key""", (s, e))
    revs = [r["rev"] or 0 for r in rows]
    ma7 = []
    for i in range(len(revs)):
        lo = max(0, i - 6)
        ma7.append(round(sum(revs[lo:i + 1]) / (i - lo + 1), 0))
    return jsonify({
        "labels": [r["label"] for r in rows],
        "revenue": [round(r["rev"] or 0, 0) for r in rows],
        "margin": [round(r["margin"] or 0, 0) for r in rows],
        "orders": [int(r["orders"] or 0) for r in rows],
        "ma7": ma7 if gran == "day" else None,
    })


@app.route("/api/category_breakdown")
def api_category_breakdown():
    days = days_arg(90)
    s, e = window(days)
    rows = q("""SELECT category, SUM(net_revenue) rev, SUM(margin) margin,
                       SUM(units) units, SUM(orders) orders
                FROM agg_daily_category WHERE date_key BETWEEN ? AND ?
                GROUP BY category ORDER BY rev DESC""", (s, e))
    total = sum(r["rev"] or 0 for r in rows) or 1
    for r in rows:
        r["rev"] = round(r["rev"] or 0, 0)
        r["share"] = round(r["rev"] / total * 100, 1)
        r["margin_rate"] = round((r["margin"] or 0) / r["rev"] * 100, 1) if r["rev"] else 0
        r["margin"] = round(r["margin"] or 0, 0)
    return jsonify(rows)


@app.route("/api/store_performance")
def api_store_performance():
    days = days_arg(90)
    s, e = window(days)
    rows = q("""SELECT a.store_id, d.store_name, d.city, d.country, d.store_type, d.sqm,
                       SUM(a.net_revenue) rev, SUM(a.orders) orders, SUM(a.margin) margin
                FROM agg_daily_store a JOIN dim_store d ON d.store_id = a.store_id
                WHERE a.date_key BETWEEN ? AND ?
                GROUP BY a.store_id ORDER BY rev DESC""", (s, e))
    for r in rows:
        r["rev"] = round(r["rev"] or 0, 0)
        r["margin"] = round(r["margin"] or 0, 0)
        r["rev_per_sqm"] = round(r["rev"] / r["sqm"], 0) if r["sqm"] else None
    return jsonify(rows)


@app.route("/api/channel_split")
def api_channel_split():
    days = days_arg(365)
    s, e = window(days)
    rows = q("""SELECT substr(date_key,1,7) AS month, sales_channel,
                       SUM(net_amount) rev
                FROM fact_sales WHERE date_key BETWEEN ? AND ?
                GROUP BY 1, 2 ORDER BY 1""", (s, e))
    months = sorted({r["month"] for r in rows})
    by_ch = {"In-Store": {}, "Online": {}}
    for r in rows:
        by_ch.setdefault(r["sales_channel"], {})[r["month"]] = round(r["rev"] or 0, 0)
    return jsonify({
        "months": months,
        "instore": [by_ch["In-Store"].get(m, 0) for m in months],
        "online": [by_ch["Online"].get(m, 0) for m in months],
    })


@app.route("/api/payment_methods")
def api_payment_methods():
    days = days_arg(90)
    s, e = window(days)
    rows = q("""SELECT payment_method, COUNT(DISTINCT order_id) orders,
                       SUM(net_amount) rev
                FROM fact_sales WHERE date_key BETWEEN ? AND ?
                GROUP BY payment_method ORDER BY rev DESC""", (s, e))
    for r in rows:
        r["rev"] = round(r["rev"] or 0, 0)
    return jsonify(rows)


@app.route("/api/top_products")
def api_top_products():
    days = days_arg(90)
    s, e = window(days)
    cat = request.args.get("category", "")
    store = request.args.get("store", "")
    sql = """SELECT f.product_id, p.product_name, p.category, p.brand,
                    SUM(f.quantity) units, SUM(f.net_amount) rev,
                    SUM(f.margin_amount) margin
             FROM fact_sales f JOIN dim_product p ON p.product_id = f.product_id
             WHERE f.date_key BETWEEN ? AND ?"""
    params = [s, e]
    if cat:
        sql += " AND p.category = ?"
        params.append(cat)
    if store:
        sql += " AND f.store_id = ?"
        params.append(store)
    sql += " GROUP BY f.product_id ORDER BY rev DESC LIMIT 15"
    rows = q(sql, params)
    for r in rows:
        r["rev"] = round(r["rev"] or 0, 0)
        r["margin"] = round(r["margin"] or 0, 0)
    return jsonify(rows)


@app.route("/api/monthly_perf")
def api_monthly_perf():
    rows = q("""SELECT substr(date_key,1,7) AS month, SUM(net_revenue) rev,
                       SUM(margin) margin, SUM(marketing_spend) mkt,
                       SUM(refunds) refunds, SUM(orders) orders
                FROM agg_daily_kpis GROUP BY 1 ORDER BY 1""")
    for r in rows:
        for k in ["rev", "margin", "mkt", "refunds"]:
            r[k] = round(r[k] or 0, 0)
        r["roi"] = round(r["rev"] / r["mkt"], 1) if r["mkt"] else None
    return jsonify(rows)


@app.route("/api/web_summary")
def api_web_summary():
    days = days_arg(90)
    s, e = window(days)
    cur = q1("""SELECT SUM(sessions) sessions, SUM(online_orders) orders,
                       AVG(conversion_rate)*100 cr, AVG(bounce_rate)*100 bounce
                FROM fact_web_traffic WHERE date BETWEEN ? AND ?""", (s, e))
    trend = q("""SELECT date, sessions, online_orders
                 FROM fact_web_traffic WHERE date BETWEEN ? AND ? ORDER BY date""", (s, e))
    return jsonify({
        "sessions": int(cur["sessions"] or 0),
        "orders": int(cur["orders"] or 0),
        "conversion_rate": round(cur["cr"] or 0, 2),
        "bounce_rate": round(cur["bounce"] or 0, 1),
        "trend": trend,
    })


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------

@app.route("/api/forecast")
def api_forecast():
    scope = request.args.get("scope", "company")
    rows = q("""SELECT date_key, actual, forecast, lo, hi, model, kind
                FROM forecast_daily WHERE scope = ? ORDER BY date_key""", (scope,))
    return jsonify(rows)


@app.route("/api/forecast_metrics")
def api_forecast_metrics():
    return jsonify(q("SELECT * FROM forecast_metrics ORDER BY scope='company' DESC, mape"))


# ---------------------------------------------------------------------------
# Anomalies
# ---------------------------------------------------------------------------

@app.route("/api/anomaly_series")
def api_anomaly_series():
    days = days_arg(540)
    s, e = window(days)
    series = q("""SELECT date_key, net_revenue FROM agg_daily_kpis
                  WHERE date_key BETWEEN ? AND ? ORDER BY date_key""", (s, e))
    marks = q("""SELECT a.date_key, a.store_id, a.severity, a.method, a.description,
                        k.net_revenue
                 FROM anomalies a JOIN agg_daily_kpis k ON k.date_key = a.date_key
                 WHERE a.date_key BETWEEN ? AND ?
                 ORDER BY a.date_key""", (s, e))
    return jsonify({"series": series, "anomalies": marks})


@app.route("/api/anomalies")
def api_anomalies():
    sev = request.args.get("severity", "")
    sql = """SELECT a.*, COALESCE(d.store_name, 'Company-wide') AS store_name
             FROM anomalies a LEFT JOIN dim_store d ON d.store_id = a.store_id"""
    params = []
    if sev:
        sql += " WHERE a.severity = ?"
        params.append(sev)
    sql += " ORDER BY a.date_key DESC LIMIT 300"
    return jsonify(q(sql, params))


@app.route("/api/anomaly_validation")
def api_anomaly_validation():
    return jsonify(q("SELECT * FROM anomaly_validation"))


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@app.route("/api/segments")
def api_segments():
    return jsonify(q("SELECT * FROM segment_profiles ORDER BY avg_monetary DESC"))


@app.route("/api/segment_scatter")
def api_segment_scatter():
    rows = q("""SELECT frequency, monetary, churn_risk, segment
                FROM customer_segments
                WHERE monetary > 0
                ORDER BY RANDOM() LIMIT 1200""")
    return jsonify(rows)


@app.route("/api/at_risk")
def api_at_risk():
    rows = q("""SELECT customer_id, first_name || ' ' || last_name AS name, city,
                       segment, recency, frequency, monetary, churn_risk, clv_annual
                FROM customer_segments
                WHERE churn_risk >= 0.5
                ORDER BY clv_annual DESC LIMIT 25""")
    return jsonify(rows)


@app.route("/api/demographics")
def api_demographics():
    rows = q("""SELECT age_band, gender, COUNT(*) customers, SUM(monetary) revenue
                FROM customer_segments
                WHERE age_band IS NOT NULL AND age_band != 'nan'
                GROUP BY age_band, gender ORDER BY age_band""")
    for r in rows:
        r["revenue"] = round(r["revenue"] or 0, 0)
    return jsonify(rows)


# ---------------------------------------------------------------------------
# Pipeline / data ops
# ---------------------------------------------------------------------------

@app.route("/api/pipeline_status")
def api_pipeline_status():
    dq = q("SELECT * FROM dq_log")
    runs = q("SELECT * FROM pipeline_runs")
    tables = {}
    for t in ["fact_sales", "fact_returns", "fact_marketing", "fact_web_traffic",
              "fact_inventory", "dim_customer", "dim_product", "dim_store",
              "dim_date", "anomalies", "forecast_daily", "customer_segments"]:
        try:
            tables[t] = q1(f"SELECT COUNT(*) c FROM {t}")["c"]
        except sqlite3.OperationalError:
            tables[t] = None
    manifest = {}
    mpath = Path(LOG_DIR) / "generation_manifest.json"
    if mpath.exists():
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    db_size_mb = round(Path(DB_PATH).stat().st_size / 1e6, 1) if Path(DB_PATH).exists() else 0
    return jsonify({"dq_log": dq, "runs": runs, "tables": tables,
                    "manifest": manifest, "db_size_mb": db_size_mb})


if __name__ == "__main__":
    if not Path(DB_PATH).exists():
        raise SystemExit(
            "Warehouse not found. Run the pipeline first:\n"
            "    python run_pipeline.py"
        )
    print(f"\n  {PLATFORM_NAME} - dashboard for {COMPANY_NAME}")
    print("  http://127.0.0.1:5000\n")
    app.run(debug=False, host="127.0.0.1", port=5000)
