"""Orchestrates the full flow: ETL -> star schema -> load -> reconcile.

The SAME run_pipeline() is called from a notebook (learn), the CLI (test),
and the API (n8n triggers it). That is the whole point of "modularize".
"""
from . import (extract, clean, validate, transform,
               dimensions, facts, load, reconcile)


def run_pipeline(settings) -> dict:
    # --- ETL ---
    raw = extract.read_csv(settings.source_csv)
    raw_count = len(raw)

    cleaned = clean.clean(raw)
    good, bad = validate.split_valid(cleaned)
    good = transform.derive(good)

    # --- dimensional modeling ---
    dims = dimensions.build_all(good)
    fact = facts.build_fact(good, dims)

    # --- load + verify ---
    written = load.load_all(dims, fact, bad, settings)
    report = reconcile.check(raw_count, good, fact, bad, settings)
    report["written"] = written
    report["target"] = settings.target
    report["schema"] = settings.use_schema()
    return report
