"""Step 6 - Fact: assemble fact_loan with foreign keys to every dimension.

We recompute the same derived keys used to build the dims, then merge (left join)
to attach each surrogate key. One row per loan.
"""
import pandas as pd

from . import dimensions as dim


def build_fact(df: pd.DataFrame, dims: dict) -> pd.DataFrame:
    f = df.copy()

    # derived join keys (must match how the dims were built)
    f["date_key"] = pd.to_datetime(f["issue_date"]).apply(lambda x: x.year * 100 + x.month)
    f["term_months"] = f["term_months"].astype("int64")
    f["emp_bucket"] = f["emp_length_years"].map(dim._emp_bucket)
    f["income_band"] = f["annual_inc"].map(dim._income_band)

    f = f.merge(dims["dim_grade"][["grade_key", "sub_grade"]], on="sub_grade", how="left")
    f = f.merge(dims["dim_purpose"][["purpose_key", "purpose"]], on="purpose", how="left")
    f = f.merge(dims["dim_loan_status"][["status_key", "loan_status"]], on="loan_status", how="left")
    f = f.merge(dims["dim_geography"][["geo_key", "addr_state"]], on="addr_state", how="left")
    f = f.merge(dims["dim_term"][["term_key", "term_months"]], on="term_months", how="left")
    f = f.merge(dims["dim_borrower"],
                on=["emp_bucket", "home_ownership", "income_band", "verification_status"],
                how="left")

    fact = pd.DataFrame({
        "loan_id": f["id"],
        # foreign keys
        "date_key": f["date_key"],
        "grade_key": f["grade_key"],
        "purpose_key": f["purpose_key"],
        "status_key": f["status_key"],
        "geo_key": f["geo_key"],
        "borrower_key": f["borrower_key"],
        "term_key": f["term_key"],
        # measures
        "loan_amnt": f["loan_amnt"],
        "funded_amnt": f["funded_amnt"],
        "int_rate": f["int_rate"],
        "installment": f["installment"],
        "annual_inc": f["annual_inc"],
        "dti": f["dti"],
        "fico_avg": f["fico_avg"],
        "total_pymnt": f["total_pymnt"],
        "total_rec_prncp": f["total_rec_prncp"],
        "recoveries": f["recoveries"],
        "is_default": f["is_default"],
        "profit": f["profit"],
    })
    return fact
