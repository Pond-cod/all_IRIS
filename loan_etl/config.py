"""Central configuration.

The SAME code runs in a notebook, from the CLI, or behind an API — only the
connection/target changes. Everything is read from environment variables so no
secret is ever hard-coded.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    # --- source ---
    source_csv: str = os.getenv("SOURCE_CSV", "data/loan_sample.csv")

    # --- target warehouse ---
    target: str = os.getenv("TARGET", "sqlite")            # "sqlite" | "mssql"
    schema: str = os.getenv("DW_SCHEMA", "dbo")            # per-team schema in MSSQL, e.g. "team01"
    sqlite_path: str = os.getenv("SQLITE_PATH", "loan_dw.db")
    # e.g. mssql+pyodbc://user:pwd@host:1433/loan_dw?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no
    mssql_url: str = os.getenv("MSSQL_URL", "")

    # --- load behaviour ---
    load_mode: str = os.getenv("LOAD_MODE", "replace")     # "replace" (auto-create) | "append" (use DDL)

    def engine_url(self) -> str:
        if self.target == "mssql":
            if not self.mssql_url:
                raise ValueError("TARGET=mssql but MSSQL_URL is empty")
            return self.mssql_url
        return f"sqlite:///{self.sqlite_path}"

    def use_schema(self) -> Optional[str]:
        # SQLite has no schemas; MSSQL isolates each team by schema.
        return self.schema if self.target == "mssql" else None


def for_team(team: str, source: Optional[str] = None) -> "Settings":
    """Used by the shared API: one service, isolated per team via MSSQL schema."""
    s = Settings()
    s.target = "mssql"
    s.schema = team
    if source:
        s.source_csv = source
    return s


settings = Settings()
