# 🌆 บ่าย — Power BI Dashboard (ต่อ MSSQL → Loan Analytics + Data Quality)

คู่มือสร้าง Dashboard จาก **star schema** ที่เราโหลดเข้า MSSQL ตอนเช้า
(ต่อยอดสไตล์จาก `amornpan/dq_power-bi`)

**สิ่งที่จะได้:** Dashboard 2 หน้า
- **หน้า 1 — Loan Analytics:** ใครเบี้ยวหนี้, กลุ่มไหนกำไร, แนวโน้มเป็นยังไง
- **หน้า 2 — Data Quality:** ข้อมูลที่ถูก quarantine ตอนเช้า (validity / completeness)

---

## ⏱️ โครงเวลา (3 ชม.)

| เวลา | หัวข้อ |
|---|---|
| 0:00–0:20 | ต่อ Power BI → MSSQL (TestDB, schema ของทีม) |
| 0:20–0:50 | Data Model — เชื่อม relationships (star) + date table |
| 0:50–1:20 | DAX Measures (analytics + DQ) |
| 1:20–1:30 | ☕ พัก |
| 1:30–2:20 | หน้า 1 — Loan Analytics (KPI + charts + map) |
| 2:20–2:45 | หน้า 2 — Data Quality + จัด layout/ธีม |
| 2:45–3:00 | Publish + เล่า insight |

---

## 1. ต่อ Power BI เข้า MSSQL

### 1.1 Get Data → SQL Server
1. เปิด **Power BI Desktop**
2. **Home → Get Data → SQL Server**
3. กรอก:
   - **Server:** `34.59.223.196`
   - **Database:** `de_loan_dw`
   - **Data Connectivity mode:** **Import** (เร็วสุดสำหรับเวิร์กช็อป)
4. **Credentials → Database** → ใส่ user กลาง: **`deadmin`** / **`de@admin2026`** (ทุกคนใช้ตัวเดียวกัน)

### 1.2 เลือกตาราง (ขึ้นต้นด้วย prefix ของคุณ)
ทุกคนเขียนลง `de_loan_dw` เหมือนกัน แต่ตารางขึ้นต้นด้วย `TEAM_ID` ของแต่ละคน
ใน **Navigator** เลือกตารางที่ขึ้นต้นด้วย prefix ของคุณ (เช่น `team01_`):

```
☑ team01_fact_loan
☑ team01_dim_date
☑ team01_dim_grade
☑ team01_dim_purpose
☑ team01_dim_loan_status
☑ team01_dim_geography
☑ team01_dim_borrower
☑ team01_dim_term
☑ team01_quarantine_loan      ← สำหรับหน้า Data Quality
```
แล้วคลิก **Load**

> 💡 **สำคัญ:** หลัง Load ให้ **rename ตารางใน Power BI** ตัด prefix ออก
> (`team01_fact_loan` → `fact_loan`, `team01_dim_date` → `dim_date` …) เพื่อให้สูตร DAX + relationship
> ในคู่มือนี้ใช้ได้เลยไม่ต้องแก้ — right-click ตาราง → **Rename**

### 1.3 ตรวจ Data Types (Model / Power Query)
| คอลัมน์ | Type ที่ถูก |
|---|---|
| `dim_date[full_date]` | **Date** |
| `int_rate`, `dti`, `profit`, `funded_amnt`, ... | **Decimal Number** |
| `*_key`, `is_default`, `term_months` | **Whole Number** |
| `grade`, `addr_state`, `loan_status`, ... | **Text** |

---

## 2. Data Model — เชื่อม Relationships (Star)

### 2.1 สร้าง relationships (fact → dim, แบบ 1-to-many)
ไปที่ **Model View** ลากคีย์เชื่อมตามนี้ (ถ้า Power BI auto-detect ให้ตรวจว่าถูก):

| จาก `fact_loan` | ไป dimension | ทิศ |
|---|---|---|
| `date_key` | `dim_date[date_key]` | Single |
| `grade_key` | `dim_grade[grade_key]` | Single |
| `purpose_key` | `dim_purpose[purpose_key]` | Single |
| `status_key` | `dim_loan_status[status_key]` | Single |
| `geo_key` | `dim_geography[geo_key]` | Single |
| `borrower_key` | `dim_borrower[borrower_key]` | Single |
| `term_key` | `dim_term[term_key]` | Single |

> ทุกเส้น: **One (dim) → Many (fact)**, Cross-filter = **Single**
> `quarantine_loan` **ไม่ต้องเชื่อม** (เป็นตารางแยกสำหรับหน้า DQ)

```
        dim_date    dim_grade   dim_loan_status
            \          |            /
 dim_purpose ── ★ fact_loan ★ ── dim_geography
            /          |            \
     dim_borrower   dim_term     (วัดผล: funded, int_rate,
                                  is_default, profit ...)
```

### 2.2 ตั้ง `dim_date` เป็น Date Table
1. คลิกตาราง `dim_date` → **Table tools → Mark as date table**
2. เลือกคอลัมน์ **`full_date`**
> ทำให้ใช้ time-intelligence + แกนเวลาเรียงถูก (grain = รายเดือน)

---

## 3. DAX Measures

สร้าง measure (คลิกขวาที่ `fact_loan` → **New measure**)

### 3.1 Analytics
```dax
Total Loans = COUNTROWS(fact_loan)
```
```dax
Total Funded = SUM(fact_loan[funded_amnt])
```
```dax
Avg Int Rate = AVERAGE(Pixie_fact_loan[int_rate])
```
```dax
Total Profit = SUM(Pixie_fact_loan[profit])
```
```dax
Default Rate % = DIVIDE(SUM(Pixie_fact_loan[is_default]), COUNTROWS(Pixie_fact_loan), 0)
```
```dax
Charge-off $ = CALCULATE(SUM(Pixie_fact_loan[funded_amnt]), Pixie_fact_loan[is_default] = 1)
```
```dax
ROI % = DIVIDE([Total Profit], [Total Funded], 0)
```
> Format: `Default Rate %` และ `ROI %` ตั้งเป็น **Percentage**; เงินตั้งเป็น **Currency / 0 decimals**

### 3.2 Data Quality (ใช้กับ `quarantine_loan` — แนวเดียวกับ repo `dq_power-bi`)
```dax
Loaded Rows = COUNTROWS(fact_loan)
```
```dax
Quarantined Rows = COUNTROWS(quarantine_loan)
```
```dax
Quarantine Rate % =
DIVIDE([Quarantined Rows], [Loaded Rows] + [Quarantined Rows], 0)
```

---

## 4. หน้า 1 — Loan Analytics Dashboard

### 4.1 Layout
```
┌────────────────────────────────────────────────────────────────────┐
│  [Total Funded] [Total Loans] [Default Rate %] [Avg Int Rate] [ROI%] │  ← KPI cards
├─────────────────────────────────────┬──────────────────────────────┤
│  Default Rate % & Avg Int Rate       │   Total Funded by Month       │
│  by Grade (combo: bar + line)        │   (line chart - trend)        │
├─────────────────────────────────────┼──────────────────────────────┤
│  Total Profit by Purpose (bar)       │   Default Rate % by State     │
│                                      │   (filled map)                │
├──────────────────────────────────────────────────────────────────── │
│  Slicers: [Year] [Grade] [Status Group]                              │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 วิธีสร้างแต่ละ visual
| Visual | Type | ตั้งค่า |
|---|---|---|
| KPI 5 ตัว | **Card** | ใส่ measure: Total Funded / Total Loans / Default Rate % / Avg Int Rate / ROI % |
| ความเสี่ยง vs ราคา | **Line and clustered column** | Axis = `dim_grade[grade]` · Column = `Default Rate %` · Line = `Avg Int Rate` |
| แนวโน้ม | **Line chart** | Axis = `dim_date[full_date]` · Value = `Total Funded` (หรือ `Default Rate %`) |
| กำไรตามวัตถุประสงค์ | **Clustered bar** | Axis = `dim_purpose[purpose_category]` · Value = `Total Profit` |
| แผนที่ความเสี่ยง | **Filled map** | Location = `dim_geography[addr_state]` (Data category = *State or Province*) · Color = `Default Rate %` |
| ตัวกรอง | **Slicer** | `dim_date[year]`, `dim_grade[grade]`, `dim_loan_status[status_group]` |

> 💡 visual "ความเสี่ยง vs ราคา" คือพระเอกของ insight: ถ้าเกรดไหน **Default Rate สูงแต่ดอกเบี้ยไม่สูงตาม** = ตั้งราคาความเสี่ยงผิด

---

## 5. หน้า 2 — Data Quality

(เพิ่ม Page ใหม่ — reuse แนว `dq_power-bi`)

### 5.1 Layout
```
┌──────────────────────────────────────────────────────────────┐
│  [Loaded Rows]   [Quarantined Rows]   [Quarantine Rate %]      │  ← cards
├───────────────────────────────┬──────────────────────────────┤
│  Quarantine by reject_reason   │   Loaded vs Quarantined        │
│  (donut)                       │   (donut / 100% stacked)       │
├───────────────────────────────┴──────────────────────────────┤
│  ตาราง: ดู bad rows + reject_reason (จากเช้า)                  │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 วิธีสร้าง
| Visual | Type | ตั้งค่า |
|---|---|---|
| สรุปจำนวน | **Card** | Loaded Rows / Quarantined Rows / Quarantine Rate % |
| สาเหตุที่ถูกคัด | **Donut** | Legend = `quarantine_loan[reject_reason]` · Values = Count |
| ตารางรายแถว | **Table** | `id`, `loan_amnt`, `loan_status`, `reject_reason`, `quarantined_at` |

> ธีมสี (แนว repo เดิม): Data Rows `#9DC3E6` · Valid `#C6E0B4` · Invalid/Quarantine `#FF6600`

---

## 6. จัด Layout, ธีม, เล่าเรื่อง
1. **Insert → Text box** ใส่ชื่อ dashboard + โลโก้
2. เลือกหลาย visual (Ctrl+click) → **Format → Align / Distribute** ให้เรียบ
3. **View → Themes** เลือก/สร้างธีมสีเดียวกันทั้งเล่ม
4. เรียงเล่าเรื่อง: **KPI (ภาพรวม) → ความเสี่ยง/ราคา → แนวโน้ม → action**

---

## 7. Publish + Share
1. **File → Save** (`teamXX_loan_dashboard.pbix`)
2. **Home → Publish** → เลือก Workspace
3. ใน Power BI Service → **Share** หรือตั้ง **Scheduled refresh** (ถ้าต้องการให้ดึง MSSQL ใหม่อัตโนมัติ — ต้องตั้ง Gateway)

---

## 8. สรุป Measures ทั้งหมด
| Measure | DAX |
|---|---|
| Total Loans | `COUNTROWS(fact_loan)` |
| Total Funded | `SUM(fact_loan[funded_amnt])` |
| Avg Int Rate | `AVERAGE(fact_loan[int_rate])` |
| Total Profit | `SUM(fact_loan[profit])` |
| Default Rate % | `DIVIDE(SUM(fact_loan[is_default]), COUNTROWS(fact_loan), 0)` |
| Charge-off $ | `CALCULATE(SUM(fact_loan[funded_amnt]), fact_loan[is_default]=1)` |
| ROI % | `DIVIDE([Total Profit], [Total Funded], 0)` |
| Quarantined Rows | `COUNTROWS(quarantine_loan)` |
| Quarantine Rate % | `DIVIDE([Quarantined Rows], [Loaded Rows]+[Quarantined Rows], 0)` |

---

## 9. Tips & Troubleshooting
| ปัญหา | แก้ |
|---|---|
| ต่อ SQL Server ไม่ได้ | เช็ค server/port (1433), credential ของทีม, firewall อนุญาต IP |
| Navigator ไม่เห็นตารางทีม | ทีมยังไม่ได้รัน notebook 03 (โหลด MSSQL) หรือ login ผิด schema |
| Relationship ไม่ขึ้นเอง | สร้างเองใน Model View (fact `*_key` → dim) |
| แกนเวลาเรียงผิด | ยังไม่ได้ **Mark as date table** ที่ `dim_date[full_date]` |
| แผนที่ไม่ขึ้น | Maps ถูกปิดในองค์กร → ใช้ bar by `addr_state` แทน |
| ตัวเลขโชว์ Blank | ใส่ `+ 0` หรือ `COALESCE(...)` ใน measure |

---

## เอกสารอ้างอิง
- ต้นแบบสไตล์: `github.com/amornpan/dq_power-bi`
- [Power BI Docs](https://learn.microsoft.com/power-bi/) · [DAX Reference](https://learn.microsoft.com/dax/)
