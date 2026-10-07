"""
Revenue forecasting - champion / challenger.

Models
------
- Holt-Winters (statsmodels): additive damped trend + weekly seasonality.
- Gradient Boosting (scikit-learn): calendar + lag features. Every lag is
  >= the forecast horizon, so the whole horizon is predicted directly
  (no recursive error accumulation).

Both are backtested on the last FORECAST_BACKTEST_DAYS days (MAPE, RMSE).
The champion (lowest MAPE) is refit on the full history and produces the
official FORECAST_HORIZON_DAYS forecast with a widening 95% interval.
Category-level forecasts use Holt-Winters.

Outputs (SQLite)
----------------
- forecast_daily   : date_key, scope, actual, forecast, lo, hi, model, kind
- forecast_metrics : model, scope, mape, rmse, is_champion

Run from the project root:
    python -m src.ml.forecasting
"""
import sqlite3
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.ensemble import GradientBoostingRegressor
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.config import (DB_PATH, FORECAST_HORIZON_DAYS, FORECAST_BACKTEST_DAYS,
                        RANDOM_SEED)
from src.data_generation.generate_data import RAMADAN, EID, _in_ranges

HISTORY_SHOWN_DAYS = 180      # history rows written next to the forecast
HW_TRAIN_DAYS = 730           # Holt-Winters fits on the last 2 years
Z95 = 1.96


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_series(con):
    """Return {scope: pd.Series(daily net revenue, DatetimeIndex)}."""
    out = {}
    comp = pd.read_sql("SELECT date_key, net_revenue FROM agg_daily_kpis", con)
    out["company"] = _to_series(comp)
    cat = pd.read_sql("SELECT date_key, category, net_revenue FROM agg_daily_category", con)
    for name, grp in cat.groupby("category"):
        out[name] = _to_series(grp)
    return out


def _to_series(df):
    s = df.assign(date_key=pd.to_datetime(df["date_key"])) \
          .groupby("date_key")["net_revenue"].sum()
    full = pd.date_range(s.index.min(), s.index.max(), freq="D")
    return s.reindex(full, fill_value=0.0).astype(float)


def mape(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    m = y != 0
    return float(np.mean(np.abs((y[m] - yhat[m]) / y[m])) * 100)


def rmse(y, yhat):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(yhat)) ** 2)))


# ---------------------------------------------------------------------------
# Holt-Winters
# ---------------------------------------------------------------------------

def hw_forecast(train: pd.Series, steps: int) -> np.ndarray:
    train = train.iloc[-HW_TRAIN_DAYS:]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ExponentialSmoothing(
            train, trend="add", damped_trend=True,
            seasonal="add", seasonal_periods=7,
            initialization_method="estimated",
        ).fit(optimized=True)
        fc = np.asarray(model.forecast(steps), float)
    return np.clip(fc, 0, None)


# ---------------------------------------------------------------------------
# Gradient Boosting
# ---------------------------------------------------------------------------

LAGS = [91, 98, 364, 371]     # all >= horizon -> direct multi-step forecasting


def _calendar(idx: pd.DatetimeIndex) -> pd.DataFrame:
    md = idx.month * 100 + idx.day
    return pd.DataFrame({
        "dow": idx.dayofweek,
        "month": idx.month,
        "doy": idx.dayofyear,
        "weekend": idx.dayofweek.isin([4, 5, 6]).astype(int),
        "ramadan": _in_ranges(idx, RAMADAN).astype(int),
        "eid": _in_ranges(idx, EID).astype(int),
        # fixed-date retail events (recur every year)
        "dsf": ((md >= 1208) | (md <= 112)).astype(int),
        "back_to_school": ((md >= 820) & (md <= 905)).astype(int),
        "national_day": ((md >= 1201) & (md <= 1203)).astype(int),
        "white_friday": ((idx.month == 11) & (idx.day >= 24)).astype(int),
        "t": (idx - pd.Timestamp("2023-01-01")).days,
    }, index=idx)


def _features(full: pd.Series, idx: pd.DatetimeIndex) -> pd.DataFrame:
    X = _calendar(idx)
    for lag in LAGS:
        X[f"lag_{lag}"] = full.reindex(idx - pd.Timedelta(days=lag)).to_numpy()
    roll = full.rolling(28, min_periods=7).mean()
    X["roll28_lag91"] = roll.reindex(idx - pd.Timedelta(days=91)).to_numpy()
    return X


def gbm_forecast(train: pd.Series, steps: int) -> np.ndarray:
    X = _features(train, train.index).dropna()
    y = train.loc[X.index]
    model = GradientBoostingRegressor(
        n_estimators=400, learning_rate=0.05, max_depth=4,
        subsample=0.8, random_state=RANDOM_SEED,
    ).fit(X, y)
    fut_idx = pd.date_range(train.index[-1] + pd.Timedelta(days=1), periods=steps, freq="D")
    Xf = _features(train, fut_idx)
    Xf = Xf.fillna(X.mean())
    return np.clip(model.predict(Xf[X.columns]), 0, None)


MODELS = {"Holt-Winters": hw_forecast, "Gradient Boosting": gbm_forecast}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def backtest(series: pd.Series, fn):
    train, test = series.iloc[:-FORECAST_BACKTEST_DAYS], series.iloc[-FORECAST_BACKTEST_DAYS:]
    pred = fn(train, len(test))
    return pred, mape(test, pred), rmse(test, pred), test.to_numpy() - pred


def forecast_scope(scope, series, model_names):
    """Backtest the candidate models, refit the champion, return (rows, metrics)."""
    results = {}
    for name in model_names:
        results[name] = backtest(series, MODELS[name])
        print(f"    {scope:22s} {name:18s} MAPE {results[name][1]:6.2f}%  "
              f"RMSE {results[name][2]:>10,.0f}")
    champ = min(results, key=lambda n: results[n][1])
    bt_pred, _, _, resid = results[champ]

    fc = MODELS[champ](series, FORECAST_HORIZON_DAYS)
    sigma = float(np.std(resid))
    h = np.arange(1, FORECAST_HORIZON_DAYS + 1)
    half = Z95 * sigma * np.sqrt(1 + h / 30.0)            # widening interval
    fut_idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1),
                            periods=FORECAST_HORIZON_DAYS, freq="D")

    hist = series.iloc[-HISTORY_SHOWN_DAYS:]
    bt = pd.Series(bt_pred, index=series.index[-FORECAST_BACKTEST_DAYS:])
    rows = pd.DataFrame({
        "date_key": hist.index.strftime("%Y-%m-%d"),
        "scope": scope,
        "actual": hist.round(2).to_numpy(),
        "forecast": bt.reindex(hist.index).round(2).to_numpy() if scope == "company" else np.nan,
        "lo": np.nan, "hi": np.nan,
        "model": champ, "kind": "history",
    })
    fut = pd.DataFrame({
        "date_key": fut_idx.strftime("%Y-%m-%d"),
        "scope": scope,
        "actual": np.nan,
        "forecast": np.round(fc, 2),
        "lo": np.round(np.clip(fc - half, 0, None), 2),
        "hi": np.round(fc + half, 2),
        "model": champ, "kind": "forecast",
    })
    metrics = [{"model": n, "scope": scope, "mape": round(r[1], 2), "rmse": round(r[2], 0),
                "is_champion": int(n == champ)} for n, r in results.items()]
    return pd.concat([rows, fut], ignore_index=True), metrics


def main():
    t0 = time.time()
    print("=" * 60)
    print("ML - Revenue forecasting (Holt-Winters vs Gradient Boosting)")
    print("=" * 60)
    con = sqlite3.connect(DB_PATH)
    series = load_series(con)

    all_rows, all_metrics = [], []
    for scope, s in series.items():
        names = list(MODELS) if scope == "company" else ["Holt-Winters"]
        rows, metrics = forecast_scope(scope, s, names)
        all_rows.append(rows)
        all_metrics.extend(metrics)

    fdaily = pd.concat(all_rows, ignore_index=True)
    fmetrics = pd.DataFrame(all_metrics)
    fdaily.to_sql("forecast_daily", con, if_exists="replace", index=False)
    fmetrics.to_sql("forecast_metrics", con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS idx_fc_scope ON forecast_daily(scope, date_key)")
    con.commit()
    con.close()

    champ = fmetrics[(fmetrics.scope == "company") & (fmetrics.is_champion == 1)].iloc[0]
    print(f"\n  Champion (company): {champ.model}  MAPE {champ.mape:.2f}%")
    print(f"  forecast_daily {len(fdaily):,} rows, forecast_metrics {len(fmetrics)} rows")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
