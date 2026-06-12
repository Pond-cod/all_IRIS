"""CLI entrypoint:  python -m loan_etl --source data/loan_sample.csv --target sqlite

Prints a JSON report to stdout and exits non-zero if reconciliation fails, so an
orchestrator (n8n / Airflow) can branch on success vs failure.
"""
import argparse
import json
import sys

from .config import Settings
from . import pipeline


def main():
    p = argparse.ArgumentParser(description="Loan ETL -> star schema -> warehouse")
    p.add_argument("--source", default=None, help="path to loan CSV")
    p.add_argument("--target", default=None, choices=["sqlite", "mssql"])
    p.add_argument("--schema", default=None, help="MSSQL schema / team id (e.g. team01)")
    p.add_argument("--load-mode", default=None, choices=["replace", "append"])
    args = p.parse_args()

    s = Settings()
    if args.source:
        s.source_csv = args.source
    if args.target:
        s.target = args.target
    if args.schema:
        s.schema = args.schema
    if args.load_mode:
        s.load_mode = args.load_mode

    report = pipeline.run_pipeline(s)
    print(json.dumps(report, indent=2, default=str))
    sys.exit(0 if report["reconcile_passed"] else 1)


if __name__ == "__main__":
    main()
