"""Step 4 - Transform: derive the analytical columns used as measures/flags.

This is where ~70% of DE work lives: turning raw fields into business meaning.
"""
import pandas as pd

BAD_STATUS = {
    "Charged Off", "Default", "Late (31-120 days)", "Late (16-30 days)",
    "Does not meet the credit policy. Status:Charged Off",
}
GOOD_STATUS = {
    "Fully Paid", "Current", "In Grace Period",
    "Does not meet the credit policy. Status:Fully Paid",
}


def status_group(s: str) -> str:
    if s in BAD_STATUS:
        return "Bad"
    if s in GOOD_STATUS:
        return "Good"
    return "In Progress"


def derive(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["status_group"] = df["loan_status"].map(status_group)
    df["is_default"] = df["loan_status"].isin(BAD_STATUS).astype(int)
    df["fico_avg"] = df[["fico_range_low", "fico_range_high"]].mean(axis=1)
    df["profit"] = df["total_pymnt"] - df["funded_amnt"]   # simple lifetime profit proxy
    return df
