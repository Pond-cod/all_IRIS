/* ============================================================================
   Star schema DDL for MSSQL (T-SQL).
   Each team is isolated in its own schema. Replace 'team01' everywhere
   (find & replace) or run with sqlcmd:  sqlcmd -v schema="team01" -i ddl_star_schema.sql

   Two ways to use this file:
     (A) Quick start  -> skip this; loan_etl load_mode="replace" auto-creates tables.
     (B) Governed     -> run this DDL first (explicit types + keys + indexes),
                         then load with LOAD_MODE=append.
   ============================================================================ */

IF SCHEMA_ID('team01') IS NULL EXEC('CREATE SCHEMA team01');
GO

/* ---- drop in dependency order (fact first) ---- */
IF OBJECT_ID('team01.fact_loan','U')        IS NOT NULL DROP TABLE team01.fact_loan;
IF OBJECT_ID('team01.dim_date','U')         IS NOT NULL DROP TABLE team01.dim_date;
IF OBJECT_ID('team01.dim_grade','U')        IS NOT NULL DROP TABLE team01.dim_grade;
IF OBJECT_ID('team01.dim_purpose','U')      IS NOT NULL DROP TABLE team01.dim_purpose;
IF OBJECT_ID('team01.dim_loan_status','U')  IS NOT NULL DROP TABLE team01.dim_loan_status;
IF OBJECT_ID('team01.dim_geography','U')    IS NOT NULL DROP TABLE team01.dim_geography;
IF OBJECT_ID('team01.dim_borrower','U')     IS NOT NULL DROP TABLE team01.dim_borrower;
IF OBJECT_ID('team01.dim_term','U')         IS NOT NULL DROP TABLE team01.dim_term;
GO

/* --------------------------- dimensions --------------------------- */
CREATE TABLE team01.dim_date (
    date_key     INT          NOT NULL PRIMARY KEY,   -- yyyymm
    full_date    DATE         NULL,
    [year]       INT          NULL,
    [quarter]    INT          NULL,
    [month]      INT          NULL,
    month_name   VARCHAR(3)   NULL,
    year_month   VARCHAR(7)   NULL
);

CREATE TABLE team01.dim_grade (
    grade_key    INT          NOT NULL PRIMARY KEY,
    grade        VARCHAR(1)   NULL,
    sub_grade    VARCHAR(2)   NULL,
    risk_band    VARCHAR(10)  NULL
);

CREATE TABLE team01.dim_purpose (
    purpose_key      INT          NOT NULL PRIMARY KEY,
    purpose          VARCHAR(40)  NULL,
    purpose_category VARCHAR(20)  NULL
);

CREATE TABLE team01.dim_loan_status (
    status_key   INT          NOT NULL PRIMARY KEY,
    loan_status  VARCHAR(60)  NULL,
    status_group VARCHAR(15)  NULL,
    is_default   INT          NULL
);

CREATE TABLE team01.dim_geography (
    geo_key      INT          NOT NULL PRIMARY KEY,
    addr_state   VARCHAR(2)   NULL,
    region       VARCHAR(15)  NULL
);

CREATE TABLE team01.dim_borrower (
    borrower_key        INT          NOT NULL PRIMARY KEY,
    emp_bucket          VARCHAR(10)  NULL,
    home_ownership      VARCHAR(10)  NULL,
    income_band         VARCHAR(10)  NULL,
    verification_status VARCHAR(20)  NULL
);

CREATE TABLE team01.dim_term (
    term_key     INT          NOT NULL PRIMARY KEY,
    term_months  INT          NULL,
    term_label   VARCHAR(12)  NULL
);
GO

/* --------------------------- fact --------------------------- */
CREATE TABLE team01.fact_loan (
    loan_id          BIGINT        NULL,
    -- foreign keys
    date_key         INT           NULL,
    grade_key        INT           NULL,
    purpose_key      INT           NULL,
    status_key       INT           NULL,
    geo_key          INT           NULL,
    borrower_key     INT           NULL,
    term_key         INT           NULL,
    -- measures
    loan_amnt        DECIMAL(12,2) NULL,
    funded_amnt      DECIMAL(12,2) NULL,
    int_rate         DECIMAL(6,2)  NULL,
    installment      DECIMAL(12,2) NULL,
    annual_inc       DECIMAL(14,2) NULL,
    dti              DECIMAL(7,2)  NULL,
    fico_avg         DECIMAL(7,2)  NULL,
    total_pymnt      DECIMAL(14,2) NULL,
    total_rec_prncp  DECIMAL(14,2) NULL,
    recoveries       DECIMAL(14,2) NULL,
    is_default       INT           NULL,
    profit           DECIMAL(14,2) NULL,
    CONSTRAINT FK_fact_date     FOREIGN KEY (date_key)     REFERENCES team01.dim_date(date_key),
    CONSTRAINT FK_fact_grade    FOREIGN KEY (grade_key)    REFERENCES team01.dim_grade(grade_key),
    CONSTRAINT FK_fact_purpose  FOREIGN KEY (purpose_key)  REFERENCES team01.dim_purpose(purpose_key),
    CONSTRAINT FK_fact_status   FOREIGN KEY (status_key)   REFERENCES team01.dim_loan_status(status_key),
    CONSTRAINT FK_fact_geo      FOREIGN KEY (geo_key)      REFERENCES team01.dim_geography(geo_key),
    CONSTRAINT FK_fact_borrower FOREIGN KEY (borrower_key) REFERENCES team01.dim_borrower(borrower_key),
    CONSTRAINT FK_fact_term     FOREIGN KEY (term_key)     REFERENCES team01.dim_term(term_key)
);
GO

/* --------------------------- helpful indexes --------------------------- */
CREATE INDEX IX_fact_date   ON team01.fact_loan(date_key);
CREATE INDEX IX_fact_grade  ON team01.fact_loan(grade_key);
CREATE INDEX IX_fact_status ON team01.fact_loan(status_key);
GO
