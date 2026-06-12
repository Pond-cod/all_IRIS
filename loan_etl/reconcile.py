"""Step 8 - Reconcile: prove nothing was silently lost or double-counted.

After every load we assert:
    good + quarantined == rows_in            (no row vanished)
    rows_in_fact       == good               (every good row made it to the fact)
    SUM(funded) in fact == SUM(funded) good  (no value drift)
"""


def check(raw_count: int, good, fact, bad, settings) -> dict:
    n_good = int(len(good))
    n_bad = int(len(bad)) if bad is not None else 0
    n_fact = int(len(fact))

    row_ok = (n_good + n_bad == raw_count) and (n_fact == n_good)
    sum_good = round(float(good["funded_amnt"].sum()), 2)
    sum_fact = round(float(fact["funded_amnt"].sum()), 2)
    sum_ok = abs(sum_good - sum_fact) < 0.01

    return {
        "rows_in": int(raw_count),
        "rows_good": n_good,
        "rows_quarantined": n_bad,
        "rows_fact": n_fact,
        "sum_funded_good": sum_good,
        "sum_funded_fact": sum_fact,
        "row_check_passed": bool(row_ok),
        "sum_check_passed": bool(sum_ok),
        "reconcile_passed": bool(row_ok and sum_ok),
    }
