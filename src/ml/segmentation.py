"""
Customer segmentation - RFM + KMeans, churn risk and annualised CLV.

- RFM per customer (recency in days vs the warehouse anchor date, number of
  orders, lifetime net spend). Features are log-transformed (heavy tails),
  standardised and clustered with KMeans (k = RFM_CLUSTERS).
- Clusters are auto-labelled from their centroids (Champions, Loyal
  Customers, Promising Mid-Tier, Slipping Away / At Risk (High Value),
  Hibernating).
- churn_risk: logistic function of recency centred on CHURN_INACTIVE_DAYS.
- clv_annual: lifetime spend annualised over the customer's tenure.

Outputs (SQLite)
----------------
- customer_segments : customer_id, recency, frequency, monetary, first_purchase,
                      tenure_days, segment, churn_risk, clv_annual + identity cols
- segment_profiles  : per-segment averages and revenue share

Run from the project root:
    python -m src.ml.segmentation
"""
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import DB_PATH, RFM_CLUSTERS, CHURN_INACTIVE_DAYS, RANDOM_SEED

CHURN_SCALE_DAYS = 25.0


def build_rfm(con):
    rfm = pd.read_sql("""
        SELECT customer_id,
               MAX(date_key)            AS last_purchase,
               MIN(date_key)            AS first_purchase,
               COUNT(DISTINCT order_id) AS frequency,
               SUM(net_amount)          AS monetary
        FROM fact_sales
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id""", con)
    anchor = pd.Timestamp(pd.read_sql("SELECT MAX(date_key) d FROM agg_daily_kpis", con)["d"][0])
    rfm["recency"] = (anchor - pd.to_datetime(rfm["last_purchase"])).dt.days
    rfm["tenure_days"] = (anchor - pd.to_datetime(rfm["first_purchase"])).dt.days
    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm


def label_clusters(rfm):
    """Map KMeans cluster ids to business names using centroid statistics."""
    c = rfm.groupby("cluster").agg(r=("recency", "mean"), f=("frequency", "mean"),
                                   m=("monetary", "mean"))
    # value score: high spend & frequency, low recency
    c["score"] = c["m"].rank() + c["f"].rank() - c["r"].rank()
    order = c.sort_values("score", ascending=False).index.tolist()
    names = {order[0]: "Champions", order[-1]: "Hibernating"}
    middle = c.loc[order[1:-1]]
    if len(middle):
        stalest = middle["r"].idxmax()
        names[stalest] = ("At Risk (High Value)" if middle.loc[stalest, "m"] > c["m"].median()
                          else "Slipping Away")
        rest = middle.drop(index=stalest).sort_values("m", ascending=False).index.tolist()
        for cid, name in zip(rest, ["Loyal Customers", "Promising Mid-Tier", "Needs Attention"]):
            names[cid] = name
    return rfm["cluster"].map(names).fillna("Other")


def main():
    t0 = time.time()
    print("=" * 60)
    print("ML - Customer segmentation (RFM + KMeans)")
    print("=" * 60)
    con = sqlite3.connect(DB_PATH)
    rfm = build_rfm(con)

    X = np.log1p(rfm[["recency", "frequency", "monetary"]].clip(lower=0))
    X = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=RFM_CLUSTERS, n_init=10, random_state=RANDOM_SEED).fit(X)
    rfm["cluster"] = km.labels_
    rfm["segment"] = label_clusters(rfm)

    rfm["churn_risk"] = (1 / (1 + np.exp(-(rfm["recency"] - CHURN_INACTIVE_DAYS)
                                         / CHURN_SCALE_DAYS))).round(3)
    rfm["clv_annual"] = (rfm["monetary"] / rfm["tenure_days"].clip(lower=30) * 365).round(2)

    ident = pd.read_sql("SELECT customer_id, first_name, last_name, city, gender, age_band "
                        "FROM dim_customer", con)
    seg = rfm.merge(ident, on="customer_id", how="left")[[
        "customer_id", "recency", "frequency", "monetary", "first_purchase", "tenure_days",
        "segment", "churn_risk", "clv_annual",
        "first_name", "last_name", "city", "gender", "age_band",
    ]]

    prof = seg.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_recency_days=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
        avg_churn_risk=("churn_risk", "mean"),
        avg_clv=("clv_annual", "mean"),
    ).reset_index()
    prof["revenue_share_pct"] = (prof["total_revenue"] / prof["total_revenue"].sum() * 100).round(1)
    prof = prof.round({"avg_recency_days": 2, "avg_frequency": 2, "avg_monetary": 2,
                       "total_revenue": 2, "avg_churn_risk": 2, "avg_clv": 2})
    prof = prof.sort_values("avg_monetary", ascending=False)

    seg.to_sql("customer_segments", con, if_exists="replace", index=False)
    prof.to_sql("segment_profiles", con, if_exists="replace", index=False)
    con.commit()
    con.close()

    for _, p in prof.iterrows():
        print(f"  {p['segment']:22s} {p['customers']:>7,} customers  "
              f"avg spend {p['avg_monetary']:>10,.0f}  revenue share {p['revenue_share_pct']:>5.1f}%")
    print(f"\n  customer_segments {len(seg):,} rows")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
