"""
Anomaly detection - two complementary detectors.

1. Isolation Forest (company level): looks at each day's KPIs *jointly*
   (revenue and orders vs their same-weekday baseline, basket size, discount
   rate, margin rate, refund rate) and flags days that are strange in
   combination - e.g. the pricing bug where margin collapsed.
2. Rolling z-score (store level): compares each store's daily revenue with
   its same-weekday history, its order count with a Poisson baseline, and
   its daily refunds with the trailing 4 weeks - catches local incidents
   (POS outage, flood, returns abuse) that company totals smooth away.

Detected alerts are then matched against the injected ground truth
(`anomaly_ground_truth`) to measure event-level recall.

Outputs (SQLite)
----------------
- anomalies          : anomaly_id, date_key, store_id, metric, method, value,
                       expected, score, severity, description
- anomaly_validation : label, start, end, stores, detected, n_alerts, methods

Run from the project root:
    python -m src.ml.anomaly_detection
"""
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scipy.stats import norm, poisson
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.config import DB_PATH, ANOMALY_CONTAMINATION, ZSCORE_THRESHOLD, RANDOM_SEED

WEEKDAY_WINDOW = 6            # same-weekday observations in the store baseline
ORDERS_WINDOW = 56            # trailing days for the store order-count level
RETURNS_WINDOW = 28           # trailing days for the return-count level
# Store revenue is heavy-tailed (a few big baskets dominate a store-day), so a
# plain 3-sigma rule fires on most days. A higher bar keeps alerts actionable.
STORE_REVENUE_Z = 2 * ZSCORE_THRESHOLD
RETURNS_Z = ZSCORE_THRESHOLD + 1


def z_severity(z):
    z = abs(z)
    if z >= 12:
        return "Critical"
    if z >= 9:
        return "High"
    if z >= 7.5:
        return "Medium"
    return "Low"


def ratio_severity(ratio):
    """Severity from how far a count is above its expected level (ratio >= 1)."""
    if ratio >= 10:
        return "Critical"
    if ratio >= 5:
        return "High"
    if ratio >= 3:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# 1. Isolation Forest on company-level daily KPIs
# ---------------------------------------------------------------------------

def detect_company(con):
    k = pd.read_sql("SELECT * FROM agg_daily_kpis ORDER BY date_key", con)
    k["d"] = pd.to_datetime(k["date_key"])
    k["dow"] = k["d"].dt.dayofweek

    # same-weekday baseline (previous WEEKDAY_WINDOW same weekdays, median)
    for col in ["net_revenue", "orders"]:
        k[f"{col}_base"] = k.groupby("dow")[col].transform(
            lambda s: s.shift(1).rolling(WEEKDAY_WINDOW, min_periods=3).median())

    k["rev_ratio"] = k["net_revenue"] / k["net_revenue_base"]
    k["orders_ratio"] = k["orders"] / k["orders_base"]
    k["basket"] = k["net_revenue"] / k["orders"].replace(0, np.nan)
    k["discount_rate"] = k["discounts"] / k["gross_revenue"].replace(0, np.nan)
    k["margin_rate"] = k["margin"] / k["net_revenue"].replace(0, np.nan)
    k["refund_rate"] = k["refunds"] / k["net_revenue"].replace(0, np.nan)

    feats = ["rev_ratio", "orders_ratio", "basket", "discount_rate", "margin_rate", "refund_rate"]
    df = k.dropna(subset=feats).copy()
    X = StandardScaler().fit_transform(df[feats])
    iso = IsolationForest(n_estimators=300, contamination=ANOMALY_CONTAMINATION,
                          random_state=RANDOM_SEED).fit(X)
    df["score"] = -iso.score_samples(X)
    df["flag"] = iso.predict(X) == -1

    # standardised features explain *why* a day was flagged
    zf = pd.DataFrame(X, columns=feats, index=df.index)
    out = []
    flagged = df[df["flag"]]
    s_lo, s_hi = df["score"].quantile(0.95), df["score"].max()
    for i, r in flagged.iterrows():
        z = zf.loc[i]
        if z["margin_rate"] < -2.5 and z["discount_rate"] > 2.5:
            desc = "Margin collapse with heavy discounting - possible pricing error"
        elif r["rev_ratio"] > 1.4:
            desc = "Revenue surge vs seasonal baseline - promo/event spike"
        elif r["rev_ratio"] < 0.7:
            desc = "Revenue drop vs seasonal baseline - possible outage"
        else:
            desc = "Unusual combination of daily KPIs"
        rel = (r["score"] - s_lo) / max(s_hi - s_lo, 1e-9)
        sev = "Critical" if rel >= 0.6 else "High" if rel >= 0.35 else "Medium" if rel >= 0.15 else "Low"
        out.append({
            "date_key": r["date_key"], "store_id": "ALL", "metric": "daily_kpis",
            "method": "IsolationForest", "value": round(r["net_revenue"], 2),
            "expected": round(r["net_revenue_base"], 2), "score": round(r["score"], 3),
            "severity": sev, "description": desc,
        })
    print(f"  IsolationForest  : {len(out):>5} anomalous days")
    return out


# ---------------------------------------------------------------------------
# 2. Rolling z-scores per store
# ---------------------------------------------------------------------------

def _active_grid(df, value_col, con):
    """Pivot to date x store, filling missing days with 0 after each store's first sale."""
    piv = df.pivot_table(index="date_key", columns="store_id", values=value_col, aggfunc="sum")
    piv.index = pd.to_datetime(piv.index)
    full = pd.date_range(piv.index.min(), piv.index.max(), freq="D")
    piv = piv.reindex(full)
    first = pd.read_sql("SELECT store_id, MIN(date_key) d FROM agg_daily_store GROUP BY store_id", con)
    for _, r in first.iterrows():
        if r["store_id"] in piv.columns:
            col = piv[r["store_id"]]
            piv[r["store_id"]] = col.where(col.index < pd.Timestamp(r["d"]), col.fillna(0))
    return piv


def detect_store_revenue(con):
    df = pd.read_sql("SELECT date_key, store_id, net_revenue FROM agg_daily_store", con)
    piv = _active_grid(df, "net_revenue", con)
    out = []
    dow = piv.index.dayofweek
    for store in piv.columns:
        s = piv[store]
        mean = s.groupby(dow).transform(lambda x: x.shift(1).rolling(WEEKDAY_WINDOW, min_periods=4).mean())
        std = s.groupby(dow).transform(lambda x: x.shift(1).rolling(WEEKDAY_WINDOW, min_periods=4).std())
        std = np.maximum(std, 0.08 * mean)          # floor: avoids blow-ups on very stable stores
        z = (s - mean) / std
        hits = z[(z.abs() >= STORE_REVENUE_Z) & s.notna()].dropna()
        for d, zv in hits.items():
            desc = ("Store revenue spike vs same-weekday baseline - promo/event" if zv > 0 else
                    "Store revenue collapse vs same-weekday baseline - operational incident likely")
            out.append({
                "date_key": d.strftime("%Y-%m-%d"), "store_id": store, "metric": "store_revenue",
                "method": "Rolling z-score", "value": round(float(s[d]), 2),
                "expected": round(float(mean[d]), 2), "score": round(float(zv), 2),
                "severity": z_severity(zv), "description": desc,
            })
    print(f"  Store revenue z  : {len(out):>5} alerts")
    return out


def detect_store_orders(con):
    """Order-count collapse per store (Poisson tail test).

    Store revenue is dominated by a few large baskets, so an outage can leave
    revenue looking normal while the number of orders collapses. Orders are
    counts, so the expected value is modelled as Poisson(lambda) with lambda =
    trailing ORDERS_WINDOW-day level x same-weekday factor, and the tail
    probability is converted to a z-score.
    """
    df = pd.read_sql("SELECT date_key, store_id, orders FROM agg_daily_store", con)
    piv = _active_grid(df, "orders", con)
    out = []
    for store in piv.columns:
        s = piv[store]
        level = s.shift(1).rolling(ORDERS_WINDOW, min_periods=14).mean()
        dow_factor = (s / level).groupby(s.index.dayofweek).transform(
            lambda x: x.shift(1).rolling(8, min_periods=4).median())
        lam = (level * dow_factor).clip(lower=1)
        z = pd.Series(norm.ppf(np.clip(poisson.cdf(s, lam), 1e-12, 1)), index=s.index)
        hits = z[(z <= -ZSCORE_THRESHOLD) & s.notna() & lam.notna()]
        for d, zv in hits.items():
            ratio = s[d] / lam[d]
            sev = ("Critical" if ratio <= 0.25 else "High" if ratio <= 0.4
                   else "Medium" if ratio <= 0.6 else "Low")
            out.append({
                "date_key": d.strftime("%Y-%m-%d"), "store_id": store, "metric": "store_orders",
                "method": "Rolling z-score", "value": float(s[d]),
                "expected": round(float(lam[d]), 1), "score": round(float(zv), 2),
                "severity": sev,
                "description": "Order count collapse vs expected traffic - operational incident likely",
            })
    print(f"  Store orders z   : {len(out):>5} alerts")
    return out


def detect_store_returns(con):
    """Return-count surge per store (Poisson upper tail).

    Refund *amounts* are too lumpy (one jewellery return looks like fraud),
    so the test runs on the number of items returned; the alert still reports
    the refunded amount vs its trailing average.
    """
    df = pd.read_sql("SELECT date_key, store_id, returns_qty, refunds "
                     "FROM agg_daily_store_returns", con)
    qty = _active_grid(df, "returns_qty", con)
    amt = _active_grid(df, "refunds", con)
    out = []
    for store in qty.columns:
        s = qty[store]
        lam = s.shift(1).rolling(RETURNS_WINDOW, min_periods=14).mean().clip(lower=0.5)
        z = pd.Series(norm.isf(np.clip(poisson.sf(s - 1, lam), 1e-15, 1)), index=s.index)  # P(X >= s)
        exp_amt = amt[store].shift(1).rolling(RETURNS_WINDOW, min_periods=14).mean()
        hits = z[(z >= RETURNS_Z) & lam.notna()]
        for d, zv in hits.items():
            out.append({
                "date_key": d.strftime("%Y-%m-%d"), "store_id": store, "metric": "store_returns",
                "method": "Rolling z-score", "value": round(float(amt[store][d]), 2),
                "expected": round(float(exp_amt[d]), 2), "score": round(float(zv), 2),
                "severity": ratio_severity(s[d] / lam[d]),
                "description": (f"Abnormal return volume ({int(s[d])} items vs ~{lam[d]:.1f} expected)"
                                " - possible returns abuse"),
            })
    print(f"  Store returns z  : {len(out):>5} alerts")
    return out


# ---------------------------------------------------------------------------
# Validation against injected ground truth
# ---------------------------------------------------------------------------

def validate(anoms: pd.DataFrame, con):
    gt = pd.read_sql("SELECT * FROM anomaly_ground_truth", con)
    rows = []
    for _, g in gt.iterrows():
        in_window = anoms[(anoms["date_key"] >= g["start"]) & (anoms["date_key"] <= g["end"])]
        if g["stores"] != "ALL":
            stores = g["stores"].split(",")
            in_window = in_window[in_window["store_id"].isin(stores + ["ALL"])]
        rows.append({
            "label": g["label"], "start": g["start"], "end": g["end"], "stores": g["stores"],
            "detected": int(len(in_window) > 0), "n_alerts": int(len(in_window)),
            "methods": ", ".join(sorted(in_window["method"].unique())),
        })
    val = pd.DataFrame(rows)
    for _, v in val.iterrows():
        mark = "OK  " if v["detected"] else "MISS"
        print(f"    [{mark}] {v['label']:42s} {v['n_alerts']:>3} alerts  {v['methods']}")
    print(f"  Event-level recall: {val['detected'].sum()}/{len(val)}")
    return val


def main():
    t0 = time.time()
    print("=" * 60)
    print("ML - Anomaly detection (IsolationForest + rolling z-score)")
    print("=" * 60)
    con = sqlite3.connect(DB_PATH)
    alerts = (detect_company(con) + detect_store_revenue(con) +
              detect_store_orders(con) + detect_store_returns(con))
    anoms = pd.DataFrame(alerts).sort_values(["date_key", "store_id", "metric"]).reset_index(drop=True)
    anoms.insert(0, "anomaly_id", [f"A{i + 1:05d}" for i in range(len(anoms))])
    anoms.to_sql("anomalies", con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS idx_an_date ON anomalies(date_key)")

    print("\n  Validation vs injected incidents:")
    validate(anoms, con).to_sql("anomaly_validation", con, if_exists="replace", index=False)
    con.commit()
    con.close()
    print(f"\n  anomalies {len(anoms):,} rows")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
