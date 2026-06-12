"""Step 1 - Extract: read raw loan data into a DataFrame.

The column list below is the subset of Lending Club columns this pipeline needs.
[ADJUST HERE] If your real loanstatus.csv uses different names, map them in
RENAME_MAP and the rest of the pipeline keeps working unchanged.
"""
import pandas as pd

RAW_COLUMNS = [
    "id", "loan_amnt", "funded_amnt", "term", "int_rate", "installment",
    "grade", "sub_grade", "emp_length", "home_ownership", "annual_inc",
    "verification_status", "issue_d", "loan_status", "purpose", "addr_state",
    "dti", "fico_range_low", "fico_range_high",
    "total_pymnt", "total_rec_prncp", "recoveries",
]

# real_name -> name_this_pipeline_expects   (fill in if your CSV differs)
RENAME_MAP: dict = {}


def read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    if RENAME_MAP:
        df = df.rename(columns=RENAME_MAP)
    keep = [c for c in RAW_COLUMNS if c in df.columns]
    missing = [c for c in RAW_COLUMNS if c not in df.columns]
    if missing:
        print(f"[extract] WARNING: missing columns ignored: {missing}")
    return df[keep].copy()
