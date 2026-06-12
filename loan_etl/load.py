"""Step 7 - Load: write dims + fact + quarantine to the warehouse.

Target is chosen by Settings: "sqlite" (baseline, always works) or "mssql".
For MSSQL each team is isolated by its own schema (settings.use_schema()).
"""
import sqlalchemy as sa


def get_engine(settings):
    if settings.target == "mssql":
        # fast_executemany makes pyodbc bulk INSERT dramatically faster
        return sa.create_engine(settings.engine_url(), fast_executemany=True)
    return sa.create_engine(settings.engine_url())


def load_all(dims: dict, fact, bad, settings) -> dict:
    eng = get_engine(settings)
    schema = settings.use_schema()
    mode = settings.load_mode
    written = {}

    with eng.begin() as conn:
        for name, d in dims.items():
            d.to_sql(name, conn, schema=schema, if_exists=mode, index=False)
            written[name] = int(len(d))

        fact.to_sql("fact_loan", conn, schema=schema, if_exists=mode,
                    index=False, chunksize=5000)
        written["fact_loan"] = int(len(fact))

        if bad is not None and len(bad):
            bad.to_sql("quarantine_loan", conn, schema=schema,
                       if_exists=mode, index=False)
            written["quarantine_loan"] = int(len(bad))

    return written
