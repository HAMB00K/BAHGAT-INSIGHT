"""
Central configuration for the Bahgat Insight Platform.

All paths, business constants and model parameters live here so that
every pipeline stage and the Flask app share a single source of truth.
"""
import os
from pathlib import Path

# Windows 11 removed `wmic`; joblib/loky probes it to count physical cores
# and prints a scary (harmless) warning. loky only skips the probe when this
# value is STRICTLY below the logical-core count, hence the -1.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(max(1, (os.cpu_count() or 4) - 1)))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = DATA_DIR / "bi_platform.db"

POWERBI_DIR = PROJECT_ROOT / "powerbi"
POWERBI_DATA_DIR = POWERBI_DIR / "data"

LOG_DIR = PROJECT_ROOT / "logs"

for _d in (RAW_DIR, PROCESSED_DIR, POWERBI_DATA_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Business constants (synthetic retail group operating in the GCC)
# ---------------------------------------------------------------------------
COMPANY_NAME = "Al Noor Retail Group"          # fictional client of Bahgat IT Expert
PLATFORM_NAME = "Bahgat Insight Platform"
CURRENCY = "AED"

# Simulation window: 3 full years of history
SIM_START = "2023-07-01"
SIM_END = "2026-06-30"

RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Model parameters
# ---------------------------------------------------------------------------
FORECAST_HORIZON_DAYS = 90         # days to forecast ahead
FORECAST_BACKTEST_DAYS = 60        # holdout window used to compute MAPE
ANOMALY_CONTAMINATION = 0.015      # expected share of anomalous days (IsolationForest)
ZSCORE_THRESHOLD = 3.0             # rolling z-score threshold
RFM_CLUSTERS = 5                   # customer segments (KMeans)
CHURN_INACTIVE_DAYS = 120          # days without purchase => churn risk rises
