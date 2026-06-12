"""Generate a synthetic Lending-Club-like loan_sample.csv (no real data needed).

It deliberately mimics the messy formats of the real dataset so the ETL has
something to clean (int_rate "13.56%", term " 36 months", emp_length "10+ years",
issue_d "Dec-2018") and injects a few invalid rows to demonstrate quarantine.

    python scripts/make_sample.py --rows 5000 --out data/loan_sample.csv
"""
import argparse
import os
import random

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
random.seed(42)

GRADE_SUB = {g: [f"{g}{i}" for i in range(1, 6)] for g in "ABCDEFG"}
GRADE_RATE = {"A": 7, "B": 11, "C": 15, "D": 19, "E": 23, "F": 27, "G": 30}
PURPOSES = ["debt_consolidation", "credit_card", "home_improvement", "major_purchase",
            "medical", "car", "small_business", "vacation", "moving", "house", "other"]
STATES = ["CA", "NY", "TX", "FL", "NJ", "IL", "PA", "OH", "GA", "NC",
          "VA", "WA", "AZ", "CO", "MA", "MI"]
HOME = ["RENT", "MORTGAGE", "OWN"]
VERIF = ["Verified", "Source Verified", "Not Verified"]
EMP = ["< 1 year", "1 year", "2 years", "3 years", "5 years", "7 years", "10+ years", "n/a"]
STATUS = ["Fully Paid", "Charged Off", "Current", "Default", "Late (31-120 days)", "In Grace Period"]
STATUS_W = [0.45, 0.18, 0.25, 0.03, 0.05, 0.04]
MONTHS = pd.period_range("2016-01", "2018-12", freq="M")


def _installment(amt, rate, term):
    r = rate / 100 / 12
    return round(amt * r / (1 - (1 + r) ** (-term)), 2)


def generate(n: int) -> pd.DataFrame:
    rows = []
    for i in range(n):
        g = random.choices(list("ABCDEFG"), weights=[20, 25, 20, 15, 10, 6, 4])[0]
        sub = random.choice(GRADE_SUB[g])
        rate = round(max(5.0, GRADE_RATE[g] + rng.normal(0, 1.2)), 2)
        amt = int(rng.choice([5000, 8000, 10000, 12000, 15000, 20000, 25000, 30000, 35000]))
        term = int(random.choice([36, 60]))
        inc = int(max(15000, rng.normal(75000, 35000)))
        status = random.choices(STATUS, weights=STATUS_W)[0]
        month = random.choice(MONTHS)
        inst = _installment(amt, rate, term)

        if status == "Fully Paid":
            total_pymnt = round(inst * term * rng.uniform(0.95, 1.0), 2)
            rec, prncp = 0.0, float(amt)
        elif status in ("Charged Off", "Default"):
            frac = rng.uniform(0.1, 0.6)
            total_pymnt = round(amt * frac, 2)
            rec = round(amt * rng.uniform(0, 0.1), 2)
            prncp = round(amt * frac * 0.8, 2)
        else:
            frac = rng.uniform(0.1, 0.5)
            total_pymnt = round(inst * term * frac, 2)
            rec, prncp = 0.0, round(amt * frac, 2)

        fico_low = int(rng.choice([660, 675, 690, 705, 720, 740, 760, 780]))
        rows.append({
            "id": 1_000_000 + i,
            "loan_amnt": amt,
            "funded_amnt": amt,
            "term": f" {term} months",
            "int_rate": f"{rate}%",
            "installment": inst,
            "grade": g,
            "sub_grade": sub,
            "emp_length": random.choice(EMP),
            "home_ownership": random.choice(HOME),
            "annual_inc": inc,
            "verification_status": random.choice(VERIF),
            "issue_d": month.strftime("%b-%Y"),
            "loan_status": status,
            "purpose": random.choice(PURPOSES),
            "addr_state": random.choice(STATES),
            "dti": round(rng.uniform(2, 35), 2),
            "fico_range_low": fico_low,
            "fico_range_high": fico_low + 4,
            "total_pymnt": total_pymnt,
            "total_rec_prncp": prncp,
            "recoveries": rec,
        })
    return pd.DataFrame(rows)


def inject_bad(df: pd.DataFrame, k: int = 20) -> pd.DataFrame:
    bad = df.sample(k, random_state=1).copy().reset_index(drop=True)
    bad.loc[0:4, "loan_amnt"] = -1000             # negative amount
    bad.loc[5:9, "loan_status"] = "UNKNOWN"       # invalid status
    bad.loc[10:14, "funded_amnt"] = 0             # zero funded
    bad.loc[15:19, "annual_inc"] = np.nan         # missing income
    bad["id"] = range(9_000_000, 9_000_000 + len(bad))
    return pd.concat([df, bad], ignore_index=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=5000)
    ap.add_argument("--out", default="data/loan_sample.csv")
    a = ap.parse_args()

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    df = inject_bad(generate(a.rows), 20)
    df.to_csv(a.out, index=False, encoding="utf-8-sig")
    print(f"wrote {len(df)} rows ({a.rows} good + 20 deliberately-bad) -> {a.out}")
