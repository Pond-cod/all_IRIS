"""Step 5 - Dimensions: build conformed dimensions with surrogate keys.

Grain of the star = one loan. Each dimension gets an integer surrogate key
(*_key) that the fact table references.
"""
import pandas as pd

# --------------------------- lookup helpers ---------------------------
_REGION = {}
for _r, _states in {
    "Northeast": "CT ME MA NH RI VT NJ NY PA",
    "Midwest":   "IL IN MI OH WI IA KS MN MO NE ND SD",
    "South":     "DE FL GA MD NC SC VA DC WV AL KY MS TN AR LA OK TX",
    "West":      "AZ CO ID MT NV NM UT WY AK CA HI OR WA",
}.items():
    for _s in _states.split():
        _REGION[_s] = _r


def _region(state: str) -> str:
    return _REGION.get(state, "Other")


def _risk_band(grade: str) -> str:
    if grade in ("A", "B"):
        return "Low"
    if grade in ("C", "D"):
        return "Medium"
    return "High"


def _income_band(x) -> str:
    if pd.isna(x):
        return "Unknown"
    if x < 40000:
        return "<40k"
    if x < 80000:
        return "40-80k"
    if x < 120000:
        return "80-120k"
    return "120k+"


def _emp_bucket(x) -> str:
    if pd.isna(x):
        return "Unknown"
    x = int(x)
    if x <= 1:
        return "0-1y"
    if x <= 4:
        return "2-4y"
    if x <= 9:
        return "5-9y"
    return "10y+"


PURPOSE_CATEGORY = {
    "debt_consolidation": "Debt", "credit_card": "Debt",
    "home_improvement": "Home", "house": "Home", "renewable_energy": "Home",
    "car": "Auto", "major_purchase": "Purchase",
    "medical": "Life", "vacation": "Life", "moving": "Life",
    "wedding": "Life", "educational": "Life",
    "small_business": "Business", "other": "Other",
}


# --------------------------- dimension builders ---------------------------
def build_date(df: pd.DataFrame) -> pd.DataFrame:
    p = pd.to_datetime(df["issue_date"]).dropna().dt.to_period("M").drop_duplicates()
    d = pd.DataFrame({"period": sorted(p)})
    d["date_key"] = d["period"].apply(lambda x: x.year * 100 + x.month)
    d["full_date"] = d["period"].apply(lambda x: x.to_timestamp())
    d["year"] = d["period"].apply(lambda x: x.year)
    d["quarter"] = d["period"].apply(lambda x: x.quarter)
    d["month"] = d["period"].apply(lambda x: x.month)
    d["month_name"] = d["full_date"].dt.strftime("%b")
    d["year_month"] = d["full_date"].dt.strftime("%Y-%m")
    return d.drop(columns="period").reset_index(drop=True)


def build_grade(df: pd.DataFrame) -> pd.DataFrame:
    d = (df[["grade", "sub_grade"]].dropna().drop_duplicates()
         .sort_values("sub_grade").reset_index(drop=True))
    d.insert(0, "grade_key", d.index + 1)
    d["risk_band"] = d["grade"].map(_risk_band)
    return d


def build_purpose(df: pd.DataFrame) -> pd.DataFrame:
    d = (df[["purpose"]].dropna().drop_duplicates()
         .sort_values("purpose").reset_index(drop=True))
    d.insert(0, "purpose_key", d.index + 1)
    d["purpose_category"] = d["purpose"].map(PURPOSE_CATEGORY).fillna("Other")
    return d


def build_status(df: pd.DataFrame) -> pd.DataFrame:
    d = (df[["loan_status", "status_group", "is_default"]].drop_duplicates()
         .sort_values("loan_status").reset_index(drop=True))
    d.insert(0, "status_key", d.index + 1)
    return d


def build_geography(df: pd.DataFrame) -> pd.DataFrame:
    d = (df[["addr_state"]].dropna().drop_duplicates()
         .sort_values("addr_state").reset_index(drop=True))
    d.insert(0, "geo_key", d.index + 1)
    d["region"] = d["addr_state"].map(_region)
    return d


def build_borrower(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy()
    t["emp_bucket"] = t["emp_length_years"].map(_emp_bucket)
    t["income_band"] = t["annual_inc"].map(_income_band)
    cols = ["emp_bucket", "home_ownership", "income_band", "verification_status"]
    d = t[cols].drop_duplicates().sort_values(cols).reset_index(drop=True)
    d.insert(0, "borrower_key", d.index + 1)
    return d


def build_term(df: pd.DataFrame) -> pd.DataFrame:
    d = (df[["term_months"]].dropna().drop_duplicates()
         .sort_values("term_months").reset_index(drop=True))
    d["term_months"] = d["term_months"].astype("int64")
    d.insert(0, "term_key", d.index + 1)
    d["term_label"] = d["term_months"].astype(str) + " months"
    return d


def build_all(df: pd.DataFrame) -> dict:
    return {
        "dim_date": build_date(df),
        "dim_grade": build_grade(df),
        "dim_purpose": build_purpose(df),
        "dim_loan_status": build_status(df),
        "dim_geography": build_geography(df),
        "dim_borrower": build_borrower(df),
        "dim_term": build_term(df),
    }
