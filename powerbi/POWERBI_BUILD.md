# 🛠️ สร้าง Power BI Dashboard ตามสไลด์ (Loan Analytics)

ทำตามนี้ ~30 นาที จะได้ `.pbix` ตรงตามสไลด์ 19–24 · ใช้ schema จริงจาก `sql/ddl_star_schema.sql`

> ⚠️ **ก่อนเริ่ม:** ต้องโหลดข้อมูลเข้า MSSQL แล้ว (notebook 03 ตั้ง `LOAD_TO_MSSQL = True`) → มีตาราง `<TEAM_ID>_fact_loan`, `<TEAM_ID>_dim_*`, `<TEAM_ID>_quarantine_loan`

---

## 1) Connect — ต่อ MSSQL
1. **Home → Get Data → SQL Server**
2. Server: `mssql.minddatatech.com` (หรือ `34.59.223.196`) · Database: `de_loan_dw`
3. Data Connectivity mode: **Import**
4. ใส่ credentials (Database): `deadmin` / `de@admin2026`
5. เลือกตารางของทีม: `<TEAM_ID>_fact_loan`, `<TEAM_ID>_dim_date`, `_dim_grade`, `_dim_purpose`, `_dim_loan_status`, `_dim_geography`, `_dim_borrower`, `_dim_term`, `_quarantine_loan` → **Load**
6. **Rename** ทุกตารางตัด prefix ออก (เช่น `team01_fact_loan` → `fact_loan`) เพื่อให้ DAX/relationship สะอาด

## 2) Model — เชื่อม relationships (star)
ไป **Model view** ลากเชื่อม (fact → dim, ทิศ single, 1-to-many):
| จาก fact_loan | ไป dimension |
|---|---|
| `date_key` | `dim_date[date_key]` |
| `grade_key` | `dim_grade[grade_key]` |
| `purpose_key` | `dim_purpose[purpose_key]` |
| `status_key` | `dim_loan_status[status_key]` |
| `geo_key` | `dim_geography[geo_key]` |
| `borrower_key` | `dim_borrower[borrower_key]` |
| `term_key` | `dim_term[term_key]` |

> ⚠️ **Power BI auto-detect มักสร้าง relationship เกิน** (เช่นเห็น **12** เส้นใน Model → Relationships) — เพราะมีคอลัมน์ชื่อซ้ำ เช่น `is_default` อยู่ทั้งใน `fact_loan` และ `dim_loan_status` → เชื่อมมั่ว
> **ต้องเหลือแค่ 7 เส้นที่เป็น `_key` ตามตารางบน** · เส้นอื่น **คลิกขวา → Delete** (ทิศต้องเป็น fact `*` → dim `1`)

→ คลิก `dim_date` → **Table tools → Mark as date table** → เลือก `full_date`

## 3) DAX — สร้าง measures
1. ไป **Report view** หรือ **Table view** (ไอคอนซ้าย) → Data pane แท็บ **Tables**
2. **คลิกขวาที่ตาราง `fact_loan` → New measure** (สร้างจาก "ตาราง" — ไม่ใช่จากแท็บ Model)
3. เปิดไฟล์ **`measures.dax`** → วาง DAX ทีละก้อนในแถบสูตร → กด **Enter**
   (Default Rate %, ROI %, Total Funded, Total Loans, Avg Int Rate, Total Profit + กลุ่ม Data Quality)

> 💡 ถ้า **ยังไม่ rename** ตาราง (ขั้น 1 ข้อ 6) ให้แก้ชื่อใน DAX เป็น `team01_fact_loan` แทน `fact_loan`
> — แต่ rename จะง่ายกว่า (ทุกทีมใช้ measures.dax ชุดเดียวกันได้)

---

## 4) หน้า Analytics (ตามสไลด์ 21)
**แถว KPI cards** (visual = Card, อันละใบ):
`Total Funded` · `Total Loans` · `Default Rate %` · `Avg Int Rate` · `ROI %`

**4 กราฟล่าง:**
| Visual | ชนิด | Axis / Location | Values |
|---|---|---|---|
| Default Rate % vs Int Rate · by Grade | Clustered column | `dim_grade[grade]` | `Default Rate %`, `Avg Int Rate` |
| Total Funded · by Month | Line | `dim_date[year_month]` | `Total Funded` |
| Total Profit · by Purpose | Bar | `dim_purpose[purpose]` | `Total Profit` |
| Default Rate % · by State | Filled map | `dim_geography[addr_state]` | `Default Rate %` |

**Slicers (มุมบน):** `dim_grade[grade]` · `dim_date[year]` (หรือ `year_month`)

## 5) หน้า Data Quality (ตามสไลด์ 22–23)
เพิ่มหน้าใหม่ (+ ล่างซ้าย):
| Visual | ชนิด | Field |
|---|---|---|
| Data Rows | Card | `Total Rows` |
| Validity % | Card | `Validity %` |
| Completeness % | Card | `Completeness %` |
| Good / Bad split | Donut | Legend `dim_loan_status[status_group]` · Values `Total Loans` |
| Validity (good vs quarantine) | Donut | ดู note ด้านล่าง |

> 💡 Donut "good vs quarantine" แบบ dq_power-bi: ต้องรวม fact (good) กับ quarantine (bad) เป็นมิติเดียว — วิธีง่าย: ทำ **calculated table**
> ```DAX
> DQ Split = UNION (
>     ROW ( "สถานะ", "Good", "Rows", COUNTROWS ( fact_loan ) ),
>     ROW ( "สถานะ", "Quarantine", "Rows", COUNTROWS ( quarantine_loan ) ) )
> ```
> แล้ว Donut: Legend `DQ Split[สถานะ]` · Values `DQ Split[Rows]`

---

## 6) ตรวจ + บันทึก
- ตัวเลขใน card ควรตรงกับ `reconcile` (เช่น Total Loans = จำนวนแถว fact)
- **File → Save as** → `Loan_Analytics_<TEAM_ID>.pbix`
- แชร์: **File → Export → Create PDF/XPS** (อย่าใช้ "Save as Adobe PDF" — ภาษาไทยเพี้ยน) หรือ Publish ขึ้น Power BI Service

> 🎨 ต้นแบบหน้า Data Quality เต็มๆ + ไฟล์ .pbix: `github.com/amornpan/dq_power-bi`
