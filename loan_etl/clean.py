"""Step 2 - Clean: fix types and the messy Lending Club string formats.

Lending Club quirks handled here:
    int_rate    "13.56%"      -> 13.56      (float)
    term        " 36 months"  -> 36         (int  -> term_months)
    emp_length  "10+ years"   -> 10         (int  -> emp_length_years; "< 1 year" -> 0)
    issue_d     "Dec-2018"    -> Timestamp  (-> issue_date)
"""
import numpy as np
import pandas as pd


def parse_percent(s: pd.Series) -> pd.Series:
    return pd.to_numeric(
        s.astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )


def parse_term(s: pd.Series) -> pd.Series:
    digits = s.astype(str).str.extract(r"(\d+)")[0]
    return pd.to_numeric(digits, errors="coerce").astype("Int64")


def parse_emp_length(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().replace(
        {"< 1 year": "0", "10+ years": "10", "n/a": np.nan, "nan": np.nan, "": np.nan}
    )
    digits = x.str.extract(r"(\d+)")[0]
    return pd.to_numeric(digits, errors="coerce").astype("Int64")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # messy strings -> numbers
    if "int_rate" in df:
        df["int_rate"] = parse_percent(df["int_rate"])
    if "term" in df:
        df["term_months"] = parse_term(df["term"])
    if "emp_length" in df:
        df["emp_length_years"] = parse_emp_length(df["emp_length"])

    # dates  ([ADJUST HERE] real Lending Club uses "Dec-2018" = "%b-%Y")
    if "issue_d" in df:
        df["issue_date"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")

    # numeric coercion
    for c in ["loan_amnt", "funded_amnt", "installment", "annual_inc", "dti",
              "fico_range_low", "fico_range_high",
              "total_pymnt", "total_rec_prncp", "recoveries"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # tidy categorical text
    for c in ["grade", "sub_grade", "home_ownership", "verification_status",
              "purpose", "addr_state", "loan_status"]:
        if c in df:
            df[c] = df[c].astype(str).str.strip()

    return df
