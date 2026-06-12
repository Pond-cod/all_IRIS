"""Step 3 - Validate: enforce business rules, split good rows vs quarantine.

Nothing is deleted. Rows that fail a rule go to a quarantine table with the
reason + timestamp, so the team can review and re-process later (audit trail).
"""
import pandas as pd

VALID_STATUS = {
    "Fully Paid", "Charged Off", "Current", "Default",
    "Late (31-120 days)", "Late (16-30 days)", "In Grace Period",
    "Does not meet the credit policy. Status:Fully Paid",
    "Does not meet the credit policy. Status:Charged Off",
}


def _reason(row) -> str:
    r = []
    if not (row.get("loan_amnt", 0) > 0):
        r.append("loan_amnt<=0")
    if not (row.get("funded_amnt", 0) > 0):
        r.append("funded_amnt<=0")
    if pd.isna(row.get("annual_inc")) or row.get("annual_inc", -1) < 0:
        r.append("annual_inc_invalid")
    if pd.isna(row.get("int_rate")):
        r.append("int_rate_missing")
    tm = row.get("term_months")
    if pd.isna(tm) or int(tm) not in (36, 60):
        r.append("term_not_36_60")
    if pd.isna(row.get("issue_date")):
        r.append("issue_date_unparseable")
    if str(row.get("loan_status")) not in VALID_STATUS:
        r.append("status_invalid")
    return ";".join(r)


def split_valid(df: pd.DataFrame):
    """Return (good_df, bad_df). bad_df carries reject_reason + quarantined_at."""
    df = df.copy()
    mask = (
        (df["loan_amnt"] > 0)
        & (df["funded_amnt"] > 0)
        & (df["annual_inc"].fillna(-1) >= 0)
        & (df["int_rate"].notna())
        & (df["term_months"].isin([36, 60]))
        & (df["issue_date"].notna())
        & (df["loan_status"].isin(VALID_STATUS))
    )
    good = df[mask].copy()
    bad = df[~mask].copy()
    if len(bad):
        bad["reject_reason"] = bad.apply(_reason, axis=1)
        bad["quarantined_at"] = pd.Timestamp.now().isoformat()
    return good, bad
