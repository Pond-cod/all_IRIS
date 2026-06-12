"""loan_etl - a modular ETL package for Lending Club loan data.

CSV -> clean -> validate -> transform -> star schema -> warehouse -> reconcile.
"""
from . import (config, extract, clean, validate, transform,
               dimensions, facts, load, reconcile, pipeline)
from .config import Settings, settings, for_team
from .pipeline import run_pipeline

__all__ = [
    "config", "extract", "clean", "validate", "transform",
    "dimensions", "facts", "load", "reconcile", "pipeline",
    "Settings", "settings", "for_team", "run_pipeline",
]
__version__ = "0.1.0"
