"""
One-command orchestrator for the Bahgat Insight Platform.

Runs the full data journey end to end:

    1. Synthetic data generation   (data/raw/*.csv)
    2. ETL to the SQLite warehouse (data/bi_platform.db)
    3. ML - revenue forecasting
    4. ML - anomaly detection
    5. ML - customer segmentation
    6. Power BI CSV export         (powerbi/data/*.csv)

Usage (from the project root):
    python run_pipeline.py             # full run
    python run_pipeline.py --skip-gen  # reuse existing raw data
    python run_pipeline.py --only etl  # run a single stage
                    (stages: gen, etl, forecast, anomaly, segment, powerbi)

Then start the dashboard:
    python app.py
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

STAGES = ["gen", "etl", "forecast", "anomaly", "segment", "powerbi"]


def run_stage(stage: str):
    if stage == "gen":
        from src.data_generation import generate_data
        generate_data.main()
    elif stage == "etl":
        from src.etl import pipeline
        pipeline.main()
    elif stage == "forecast":
        from src.ml import forecasting
        forecasting.main()
    elif stage == "anomaly":
        from src.ml import anomaly_detection
        anomaly_detection.main()
    elif stage == "segment":
        from src.ml import segmentation
        segmentation.main()
    elif stage == "powerbi":
        from src import powerbi_export
        powerbi_export.main()


def main():
    ap = argparse.ArgumentParser(description="Bahgat Insight Platform pipeline")
    ap.add_argument("--skip-gen", action="store_true",
                    help="skip data generation (reuse data/raw)")
    ap.add_argument("--only", choices=STAGES, help="run a single stage")
    args = ap.parse_args()

    stages = [args.only] if args.only else STAGES
    if args.skip_gen and "gen" in stages and not args.only:
        stages = [s for s in stages if s != "gen"]

    t0 = time.time()
    print("#" * 60)
    print("#  BAHGAT INSIGHT PLATFORM - FULL PIPELINE")
    print("#  Stages: " + " -> ".join(stages))
    print("#" * 60 + "\n")

    for stage in stages:
        run_stage(stage)
        print()

    mins = (time.time() - t0) / 60
    print("#" * 60)
    print(f"#  PIPELINE COMPLETE in {mins:.1f} min")
    print("#  Next: python app.py  ->  http://127.0.0.1:5000")
    print("#" * 60)


if __name__ == "__main__":
    main()
