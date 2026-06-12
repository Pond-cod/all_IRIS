"""Generate the workshop teaching notebooks (.ipynb) from clean Python source.

Keeping the notebook content here (instead of hand-editing .ipynb JSON) makes the
material easy to review, diff, and regenerate.

    python scripts/build_notebooks.py
"""
import os

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

NB_DIR = os.path.join(os.path.dirname(__file__), "..", "notebooks")
os.makedirs(NB_DIR, exist_ok=True)


def md(text):
    return new_markdown_cell(text.strip("\n"))


def code(text):
    return new_code_cell(text.strip("\n"))


def save(name, cells):
    nb = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
    )
    path = os.path.join(NB_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("wrote", os.path.relpath(path).replace("\\", "/"))


# =====================================================================
# 00 — Setup
# =====================================================================
save("00_setup.ipynb", [
    md("""
# 🚀 เริ่มต้น — ตรวจเครื่องมือ + รู้จักโจทย์

ยินดีต้อนรับสู่เวิร์กช็อป **Advanced Data Engineering & Applied Analytics**

**แผนวันนี้**
- 🌅 **เช้า** — ใช้ Python ทำ ETL → โหลดเข้า **MSSQL เป็น Star Schema** (จบกระบวนการ ETL)
- 🌆 **บ่าย** — ต่อ **Power BI** เข้า MSSQL → สร้าง **Dashboard**

> โน้ตบุ๊กนี้แค่เช็คว่าเครื่องมือพร้อม + รู้จักข้อมูล แล้วไปต่อ `01_explore`
"""),
    md("""
## 1) ตั้ง prefix ของคุณ
ทุกคนใช้ login เดียวกัน (`deadmin`) เขียนลง `de_loan_dw` แต่ใช้ **`TEAM_ID` นำหน้าชื่อตาราง** กันชนกัน
(เช่น `team01_fact_loan`, `team02_fact_loan`)
👉 แก้ `TEAM_ID` เป็นชื่อ/ทีมของคุณ
"""),
    code("""
TEAM_ID = "team01"   # 👈 เปลี่ยนเป็นชื่อ/ทีมของคุณ (ใช้นำหน้าชื่อตาราง)
print("prefix ของคุณ:", TEAM_ID)
"""),
    md("## 2) ตรวจว่ามี library ครบ"),
    code("""
import sys
import pandas as pd
import sqlalchemy

print("Python     :", sys.version.split()[0])
print("pandas     :", pd.__version__)
print("sqlalchemy :", sqlalchemy.__version__)

try:
    import pymssql
    print("pymssql    :", pymssql.__version__, "→ ต่อ MSSQL ได้ ✅")
except Exception as e:
    print("pymssql    : ยังไม่มี (จะใช้ตอนบ่าย/โหลด MSSQL) —", e)
"""),
    md("""
## 3) รู้จักข้อมูล — Lending Club Loans

ข้อมูลคือ **สินเชื่อ (loan)** ของ Lending Club แต่ละแถว = 1 สินเชื่อ มีข้อมูลเช่น
วงเงิน, ดอกเบี้ย, เกรดความเสี่ยง (A–G), วัตถุประสงค์, รัฐ, และ **สถานะ** (จ่ายครบ / เบี้ยวหนี้)

**คำถามธุรกิจที่เราจะตอบด้วย dashboard:**
- เกรดไหน **เบี้ยวหนี้ (default) สูง** เมื่อเทียบกับดอกเบี้ยที่คิด? → ตั้งราคาถูกไหม
- สินเชื่อกลุ่มไหน **กำไร/ขาดทุน**?
- แนวโน้มยอดปล่อยกู้ + อัตราเบี้ยวหนี้เป็นยังไง?
"""),
    md("""
## 4) เป้าหมายของวันนี้ (ภาพรวม)

```
loan_sample.csv ──► Python ETL ──► Star Schema ──► MSSQL (schema ของทีม) ──► Power BI
 (ข้อมูลดิบ)        clean+transform   dims + fact                              dashboard
```
"""),
    md("## 5) แอบดูข้อมูลสัก 5 แถว"),
    code("""
import pandas as pd
df = pd.read_csv("../data/loan_sample.csv")
print("ขนาดข้อมูล (แถว, คอลัมน์):", df.shape)
df.head()
"""),
    md("""
---
✅ ถ้ารันด้านบนได้หมด = พร้อมแล้ว! ไปต่อที่ **`01_explore.ipynb`** เพื่อสำรวจข้อมูลและออกแบบ Star Schema
"""),
])


# =====================================================================
# 01 — Explore + design the star schema
# =====================================================================
save("01_explore.ipynb", [
    md("""
# 🔍 สำรวจข้อมูล + ออกแบบ Star Schema

เป้าหมาย: **เข้าใจข้อมูล + เห็นปัญหาที่ต้อง clean + รู้ว่าจะปั้นเป็น star schema หน้าตาไหน**
"""),
    md("## 1) โหลดข้อมูล"),
    code("""
import pandas as pd
df = pd.read_csv("../data/loan_sample.csv")
print("ขนาด:", df.shape)
df.head()
"""),
    md("## 2) มีคอลัมน์อะไรบ้าง"),
    code("df.columns.tolist()"),
    md("""
## 3) 🚩 หา "ปัญหาข้อมูล" — ของจริงไม่เคยสะอาด

ลองดูคอลัมน์พวกนี้ — สังเกตว่าเก็บมาเป็น **ข้อความปนสัญลักษณ์** ใช้คำนวณไม่ได้ทันที
"""),
    code("""
df[["int_rate", "term", "emp_length", "issue_d", "loan_status"]].head(8)
"""),
    md("""
เห็นปัญหาไหม?
- `int_rate` = `"13.56%"` → มี `%` (เป็นข้อความ ไม่ใช่ตัวเลข)
- `term` = `" 36 months"` → มีคำว่า months + เว้นวรรคหน้า
- `emp_length` = `"10+ years"` / `"< 1 year"` → ข้อความ
- `issue_d` = `"Dec-2018"` → ต้องแปลงเป็นวันที่
"""),
    md("## 4) ดู type จริง + ค่าว่าง (null)"),
    code("""
print("=== dtypes ===")
print(df.dtypes)
print("\\n=== จำนวน null ต่อคอลัมน์ ===")
print(df.isnull().sum())
"""),
    md("""
สังเกต: คอลัมน์ที่ควรเป็นตัวเลข/วันที่ กลับเป็น `object` (ข้อความ) → **นี่คืองานของ ETL ตอนต่อไป**
"""),
    md("## 5) สถานะสินเชื่อมีอะไรบ้าง (สำคัญกับ default rate)"),
    code("""
df["loan_status"].value_counts()
"""),
    md("""
เราจะจัดกลุ่มสถานะเป็น **Good / Bad / In Progress** และทำ flag `is_default`
(เช่น Charged Off, Default = เบี้ยวหนี้) ในขั้น transform
"""),
    md("""
## 6) 🎯 เป้าหมาย: Star Schema

**Grain = 1 แถวต่อ 1 สินเชื่อ** ตรงกลางคือ **fact** (ตัวเลขวัดผล) ล้อมด้วย **dimension** (มุมมอง)

```
        dim_date     dim_grade     dim_loan_status
            \\          |             /
 dim_purpose ── ★ fact_loan ★ ── dim_borrower
            /          |             \\
      dim_geography  dim_term     (loan_amnt, int_rate,
                                   is_default, profit ...)
```

| ตาราง | เก็บอะไร |
|---|---|
| `fact_loan` | 1 แถว/สินเชื่อ + ตัวเลข (วงเงิน, ดอกเบี้ย, is_default, profit) + คีย์ไปหา dim |
| `dim_date` | เดือนที่ปล่อยกู้ (issue_d) |
| `dim_grade` | เกรด A–G + sub-grade + ระดับความเสี่ยง |
| `dim_purpose` | วัตถุประสงค์ + หมวด |
| `dim_loan_status` | สถานะ + กลุ่ม (Good/Bad) + is_default |
| `dim_geography` | รัฐ + ภูมิภาค |
| `dim_borrower` | โปรไฟล์ผู้กู้ (อายุงาน, บ้าน, ช่วงรายได้) |
| `dim_term` | งวด 36 / 60 เดือน |
"""),
    md("""
---
✅ เข้าใจข้อมูล + เห็นปัญหา + รู้เป้าหมาย Star Schema แล้ว
ไปต่อ **`02_etl.ipynb`** — ลงมือ **clean → validate → transform** ของจริง
"""),
])

# =====================================================================
# 02 — ETL: clean -> validate/quarantine -> transform
# =====================================================================
save("02_etl.ipynb", [
    md("""
# 🧹 ETL — Clean → Validate → Transform

เป้าหมาย: เปลี่ยน **ข้อมูลดิบเลอะ ๆ** ให้เป็น **ข้อมูลสะอาด + ตรวจแล้ว + เสริมความหมายธุรกิจ** พร้อมเข้า star schema

> นี่คือหัวใจของงาน DE — เวลาส่วนใหญ่อยู่ตรงนี้
"""),
    md("## โหลดข้อมูลดิบ"),
    code("""
import pandas as pd
df = pd.read_csv("../data/loan_sample.csv")
print("ดิบ:", df.shape)
"""),
    md("""
## 1️⃣ Clean — แก้ format ที่คำนวณไม่ได้

| ดิบ | หลังแก้ |
|---|---|
| `int_rate` = "13.56%" | `13.56` |
| `term` = " 36 months" | `36` |
| `emp_length` = "10+ years" | `10` |
| `issue_d` = "Dec-2018" | วันที่จริง |
"""),
    code("""
# int_rate "13.56%" -> 13.56
df["int_rate"] = pd.to_numeric(
    df["int_rate"].astype(str).str.replace("%", "", regex=False).str.strip(),
    errors="coerce")

# term " 36 months" -> 36
df["term_months"] = pd.to_numeric(
    df["term"].astype(str).str.extract(r"(\\d+)")[0], errors="coerce").astype("Int64")

# emp_length "10+ years" -> 10 , "< 1 year" -> 0
emp = df["emp_length"].astype(str).str.strip().replace(
    {"< 1 year": "0", "10+ years": "10", "n/a": None})
df["emp_length_years"] = pd.to_numeric(
    emp.str.extract(r"(\\d+)")[0], errors="coerce").astype("Int64")

# issue_d "Dec-2018" -> datetime
df["issue_date"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")

df[["int_rate", "term_months", "emp_length_years", "issue_date"]].head()
"""),
    code("""
# คอลัมน์ตัวเลขอื่น ๆ -> numeric ; คอลัมน์ข้อความ -> ตัดช่องว่าง
for c in ["loan_amnt", "funded_amnt", "installment", "annual_inc", "dti",
          "fico_range_low", "fico_range_high", "total_pymnt", "total_rec_prncp", "recoveries"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

for c in ["grade", "sub_grade", "home_ownership", "verification_status",
          "purpose", "addr_state", "loan_status"]:
    df[c] = df[c].astype(str).str.strip()

df[["int_rate", "term_months", "annual_inc", "issue_date"]].dtypes
"""),
    md("""
## 2️⃣ Validate + Quarantine — คัดแถวเสีย (ไม่ลบ! เก็บไว้ดูได้)

กฎ: วงเงิน > 0, รายได้ ≥ 0, มีดอกเบี้ย, งวด = 36/60, วันที่ถูก, สถานะอยู่ในลิสต์
แถวที่ไม่ผ่าน → แยกไป **quarantine** พร้อมเหตุผล
"""),
    code("""
VALID_STATUS = {"Fully Paid", "Charged Off", "Current", "Default",
                "Late (31-120 days)", "Late (16-30 days)", "In Grace Period"}

mask = (
    (df["loan_amnt"] > 0)
    & (df["funded_amnt"] > 0)
    & (df["annual_inc"].fillna(-1) >= 0)
    & df["int_rate"].notna()
    & df["term_months"].isin([36, 60])
    & df["issue_date"].notna()
    & df["loan_status"].isin(VALID_STATUS)
)

good = df[mask].copy()
bad = df[~mask].copy()
print(f"✅ good = {len(good)}   |   ⚠️ quarantine = {len(bad)}")
"""),
    code("""
# ใส่ "เหตุผล" ให้แถวที่ถูกคัดออก -> audit ได้
def reason(r):
    rs = []
    if not (r["loan_amnt"] > 0): rs.append("loan_amnt<=0")
    if not (r["funded_amnt"] > 0): rs.append("funded_amnt<=0")
    if pd.isna(r["annual_inc"]) or r["annual_inc"] < 0: rs.append("annual_inc_invalid")
    if str(r["loan_status"]) not in VALID_STATUS: rs.append("status_invalid")
    return ";".join(rs)

bad["reject_reason"] = bad.apply(reason, axis=1)
bad[["id", "loan_amnt", "funded_amnt", "annual_inc", "loan_status", "reject_reason"]].head(10)
"""),
    md("""
💡 **Quarantine แทนการลบ**: ข้อมูลไม่หาย ทีมเอาไปแก้แล้ว re-run ได้ — มี audit trail ครบทุกแถว
"""),
    md("""
## 3️⃣ Transform — สร้างคอลัมน์ที่มีความหมายธุรกิจ
- `status_group` : Good / Bad / In Progress
- `is_default`   : 1 ถ้าเบี้ยวหนี้ (ใช้คำนวณ default rate)
- `fico_avg`     : คะแนนเครดิตเฉลี่ย
- `profit`       : กำไรคร่าว ๆ = ยอดที่ได้คืน − ยอดที่ปล่อยกู้
"""),
    code("""
BAD_STATUS = {"Charged Off", "Default", "Late (31-120 days)", "Late (16-30 days)"}
GOOD_STATUS = {"Fully Paid", "Current", "In Grace Period"}

def status_group(s):
    if s in BAD_STATUS: return "Bad"
    if s in GOOD_STATUS: return "Good"
    return "In Progress"

good["status_group"] = good["loan_status"].map(status_group)
good["is_default"] = good["loan_status"].isin(BAD_STATUS).astype(int)
good["fico_avg"] = good[["fico_range_low", "fico_range_high"]].mean(axis=1)
good["profit"] = good["total_pymnt"] - good["funded_amnt"]

good[["loan_status", "status_group", "is_default", "fico_avg", "profit"]].head()
"""),
    code("""
print("default rate รวม: {:.1%}".format(good["is_default"].mean()))
good["status_group"].value_counts()
"""),
    md("""
---
✅ ได้ **`good`** (สะอาด+เสริมคอลัมน์) และ **`bad`** (quarantine)

> ทั้งหมดนี้ = โมดูล `loan_etl.clean / validate / transform` (เวอร์ชัน package ที่เก็บไว้ใช้ซ้ำ)

ไปต่อ **`03_star_schema_load.ipynb`** — ปั้นเป็น star schema แล้วโหลดเข้า MSSQL
"""),
])


# =====================================================================
# 03 — Build star schema + load to the warehouse
# =====================================================================
save("03_star_schema_load.ipynb", [
    md("""
# ⭐ Star Schema + โหลดเข้า MSSQL

เป้าหมาย: เปลี่ยน `good` เป็น **7 dimensions + 1 fact** แล้ว **โหลดเข้า MSSQL** (schema ของทีม) → จบ ETL!
"""),
    md("""
## เตรียมข้อมูล — ใช้ `loan_etl` ทำ clean/validate/transform ที่เรียนใน 02 ให้เร็ว
(โค้ดชุดเดียวกับที่เขียนเอง แต่ห่อเป็น package ใช้ซ้ำได้)
"""),
    code("""
import sys
sys.path.append("..")   # ให้ import loan_etl จาก repo root ได้

from loan_etl import extract, clean, validate, transform
df = extract.read_csv("../data/loan_sample.csv")
df = clean.clean(df)
good, bad = validate.split_valid(df)
good = transform.derive(good)
print(f"good = {len(good)} | quarantine = {len(bad)}")
"""),
    md("""
## 1️⃣ Dimensions — แต่ละ dim มี **surrogate key** (เลขประจำตัว)

ลองสร้าง `dim_grade` ด้วยมือก่อน เพื่อเข้าใจหลักการ
"""),
    code("""
dim_grade = (good[["grade", "sub_grade"]]
             .drop_duplicates().sort_values("sub_grade").reset_index(drop=True))
dim_grade.insert(0, "grade_key", dim_grade.index + 1)   # 1,2,3,... = surrogate key
dim_grade.head()
"""),
    code("""
# สร้าง dim ทั้ง 7 ตัวด้วย loan_etl (เวอร์ชัน package)
from loan_etl import dimensions, facts
dims = dimensions.build_all(good)
for name, d in dims.items():
    print(f"{name:18s} {len(d):4d} rows")
"""),
    md("## 2️⃣ Fact — `fact_loan` 1 แถว/สินเชื่อ + คีย์ไปหาทุก dim + ตัวเลขวัดผล"),
    code("""
fact = facts.build_fact(good, dims)
print("fact_loan:", fact.shape)
fact.head()
"""),
    md("## 3️⃣ ทดสอบโหลดลง SQLite ก่อน (รันได้เลย ไม่ต้องต่อ MSSQL)"),
    code("""
import sqlalchemy as sa
eng = sa.create_engine("sqlite:///loan_dw_demo.db")
with eng.begin() as conn:
    for name, d in dims.items():
        d.to_sql(name, conn, if_exists="replace", index=False)
    fact.to_sql("fact_loan", conn, if_exists="replace", index=False)
    bad.to_sql("quarantine_loan", conn, if_exists="replace", index=False)
print("โหลดเข้า SQLite สำเร็จ ✅")
"""),
    md("## 4️⃣ Reconcile — ตรวจว่าข้อมูลไม่หาย/ไม่เพี้ยน"),
    code("""
rows_in = len(good) + len(bad)
sum_match = round(good["funded_amnt"].sum(), 2) == round(fact["funded_amnt"].sum(), 2)
print("good + quarantine =", rows_in)
print("fact rows         =", len(fact), "(ควรเท่ากับ good)")
print("ยอด funded ตรงกัน :", sum_match)
print("RECONCILE PASSED  :", (len(fact) == len(good)) and sum_match)
"""),
    md("""
## 5️⃣ โหลดเข้า MSSQL จริง — จบ ETL 🎉

> ทุกคนใช้ login เดียวกัน (`deadmin`) ต่อ `de_loan_dw` แต่ตั้ง **`TEAM_ID`** ให้ต่างกัน
> ตารางจะชื่อ `<TEAM_ID>_fact_loan`, `<TEAM_ID>_dim_*` (กันชนกับเพื่อน)
> แค่ตั้ง `LOAD_TO_MSSQL = True` + แก้ `TEAM_ID` → รันได้เลย
"""),
    code("""
LOAD_TO_MSSQL = False     # 👈 เปลี่ยนเป็น True เมื่อพร้อมโหลดเข้า MSSQL
TEAM_ID = "team01"        # 👈 ชื่อ/ทีมของคุณ (นำหน้าชื่อตาราง กันชนกัน)

# --- connection กลาง: ทุกคนใช้ตัวเดียวกัน ---
HOST     = "34.59.223.196"
DATABASE = "de_loan_dw"
USER     = "deadmin"
PASSWORD = "de@admin2026"

if LOAD_TO_MSSQL:
    # URL.create encodes special chars in the password (@ # etc.) automatically
    url = sa.URL.create("mssql+pymssql", username=USER, password=PASSWORD,
                        host=HOST, port=1433, database=DATABASE)
    eng = sa.create_engine(url)
    with eng.begin() as conn:
        for name, d in dims.items():
            d.to_sql(f"{TEAM_ID}_{name}", conn, if_exists="replace", index=False)
        fact.to_sql(f"{TEAM_ID}_fact_loan", conn, if_exists="replace", index=False, chunksize=5000)
        bad.to_sql(f"{TEAM_ID}_quarantine_loan", conn, if_exists="replace", index=False)
    print(f"โหลดเข้า {DATABASE} (ตาราง {TEAM_ID}_*) สำเร็จ ✅ — พร้อมต่อ Power BI")
else:
    print("LOAD_TO_MSSQL = False -> ข้ามขั้น MSSQL (ตอนสอนจริงตั้งเป็น True)")
"""),
    md("""
---
## ✅ จบกระบวนการ ETL!
ข้อมูลอยู่ใน **star schema** บน MSSQL (`teamXX.fact_loan`, `teamXX.dim_*`) พร้อมให้ **Power BI** ดึงไปทำ dashboard ตอนบ่าย

> 💡 ทั้ง pipeline (clean→validate→transform→dims→fact→load→reconcile) ทำได้ในบรรทัดเดียวด้วย package:
"""),
    code("""
from loan_etl import Settings, run_pipeline
s = Settings()
s.source_csv = "../data/loan_sample.csv"
s.sqlite_path = "loan_dw_demo.db"
report = run_pipeline(s)     # default target = sqlite
print("reconcile_passed:", report["reconcile_passed"], "| fact rows:", report["rows_fact"])
"""),
])


print("done.")
