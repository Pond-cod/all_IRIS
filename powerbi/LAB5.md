# 🧪 LAB 5 — สร้าง Dashboard เล่าเรื่อง (จับมือทำทีละคลิก)

**Power BI Desktop · ~60 นาที** · ทำต่อจาก LAB 4 (ต่อ MSSQL + สร้าง measures แล้ว)
ผลลัพธ์: **dashboard 2 หน้า** — หน้า Analytics (สไลด์ 21) + หน้า Data Quality (สไลด์ 23)

> 🧭 **ตำแหน่งหน้าจอที่จะอ้างถึงบ่อย**
> - **Visualizations pane** (ขวา): ชุดไอคอนกราฟ + แท็บ **Build (📊)** / **Format (🖌️)**
> - **Data pane** (ขวาสุด): รายชื่อตาราง + คอลัมน์ + measures
> - **Format ribbon** (บน): โผล่ตอนเลือก visual → มี Align / Distribute
> - **View ribbon** (บน): Gridlines, Themes, Page view

---

## ✅ STEP 0 — ตรวจความพร้อม (1 นาที)
ก่อนเริ่มต้องมีครบ:
- [ ] โหลด 9 ตารางเข้า model แล้ว (LAB 4)
- [ ] **Rename ตัด `teamXX_` ออก** → `fact_loan`, `dim_grade`, ... (ดับเบิลคลิกชื่อตารางใน Data pane)
      *ถ้าไม่ rename: ทุกที่ที่เขียน `fact_loan` ให้ใช้ `team01_fact_loan` แทน*
- [ ] Relationships **7 เส้น** (fact → dim) — ไม่เกิน 7 (ลบที่ auto-detect เกิน)
- [ ] สร้าง measures จาก `measures.dax` แล้ว (Total Funded, Default Rate %, ROI %, ฯลฯ)

แล้วคลิกไอคอน **Report view** (ซ้ายบนสุด) → **เตรียม canvas:**
- **View** ribbon → เปิด ☑ **Gridlines** ☑ **Snap to grid** ☑ **Snap to objects**
- **View → Page view → Fit to page**

---

# 📊 PART A — หน้า Loan Analytics

> หน้านี้ตอบ 3 คำถามธุรกิจ: เกรดไหนเบี้ยวหนี้สูง · กลุ่มไหนกำไร/ขาดทุน · แนวโน้มเป็นไง

## A1 — KPI Cards 5 ใบ (10 นาที)
**ทำใบแรก:**
1. คลิกที่ **ว่างๆ** บน canvas
2. **Visualizations pane** → คลิกไอคอน **Card** (รูปเลข `123`)
3. **Data pane** → ลาก measure **`Total Funded`** ไปวางในช่อง **Fields**
4. **Format การ์ดให้สวย** (คลิกการ์ด → 🖌️ Format visual):
   - **Callout value** → Font 28–32, สีเข้ม, Display units = Auto
   - **Category label** → On (โชว์ชื่อ "Total Funded")
   - **Effects → Background** On · **Visual border** On (มุมโค้ง ~8px)

**ทำอีก 4 ใบเร็วๆ (copy):**
5. คลิกการ์ดแรก → **Ctrl+C → Ctrl+V** (ได้ใบใหม่ทับกัน) → ลากแยกออกมา
6. คลิกใบใหม่ → ใน **Fields** เอา Total Funded ออก → ลากใส่ measure ใหม่
7. ทำจน​ครบ 5 ใบ: **`Total Funded`** · **`Total Loans`** · **`Default Rate %`** · **`Avg Int Rate`** · **`ROI %`**

**จัดเรียง 5 ใบ:**
8. คลิกใบแรก → **Ctrl+click** อีก 4 ใบ (เลือกครบ)
9. **Format ribbon → Align → Align Top**
10. **Format ribbon → Align → Distribute Horizontally** ✨
> ตำแหน่งแนะนำ (Format → General → Properties): Y=70, H=85, W=242, X= 16 / 266 / 516 / 766 / 1016

---

## A2 — กราฟ ① Default Rate % vs Int Rate · by Grade (10 นาที)
*combo: แท่ง = อัตราเบี้ยวหนี้ · เส้น = ดอกเบี้ย → "ตั้งราคาตามความเสี่ยงไหม?"*

1. คลิกที่ว่าง → **Visualizations** → **Line and clustered column chart** (ไอคอนแท่ง+เส้น)
2. ลากใส่ field:
   - **X-axis:** `dim_grade[grade]`
   - **Column y-axis:** `Default Rate %`
   - **Line y-axis:** `Avg Int Rate`
3. **เรียงเกรด A→G:** คลิก `…` (มุมขวาบนกราฟ) → **Sort axis → grade → Sort ascending**
4. **Format (🖌️):**
   - **Title** → "Default Rate % vs Int Rate by Grade" (ฟอนต์ 12–14)
   - **Columns → Colors** = น้ำเงิน · **Lines → Colors** = ส้ม (ให้ต่างกันชัด)
   - (ถ้าอยาก) **Data labels** On
5. วาง: X=16, Y=168, W=620, H=262

---

## A3 — กราฟ ② Total Funded · by Month (8 นาที)
*เส้นแนวโน้ม → ยอดปล่อยกู้รายเดือน*

1. คลิกที่ว่าง → **Visualizations** → **Line chart**
2. field:
   - **X-axis:** `dim_date[year_month]`  *(ถ้าใช้ `full_date` Power BI จะทำ date hierarchy ให้ — กดลูกศรลง "Expand to next level" เพื่อดูรายเดือน)*
   - **Y-axis:** `Total Funded`
3. **เรียงเวลา:** `…` → Sort axis → `year_month` → Ascending
4. **Format:** Title "Total Funded by Month" · เปิด **Markers** (จุดบนเส้น) ให้อ่านง่าย
5. วาง: X=644, Y=168, W=620, H=262

---

## A4 — กราฟ ③ Total Profit · by Purpose (8 นาที)
*แท่งแนวนอน → กลุ่มวัตถุประสงค์ไหนกำไร/ขาดทุน*

1. คลิกที่ว่าง → **Visualizations** → **Clustered bar chart** (แท่งแนวนอน)
2. field:
   - **Y-axis:** `dim_purpose[purpose]`
   - **X-axis:** `Total Profit`
3. **เรียงมาก→น้อย:** `…` → Sort axis → `Total Profit` → Descending
4. **Format:** Title "Total Profit by Purpose" · **Data colors → conditional** (กำไร = เขียว / ขาดทุน = แดง ได้ ถ้าอยากเด่น)
5. วาง: X=16, Y=438, W=620, H=210

---

## A5 — กราฟ ④ Default Rate % · by State (8 นาที)
*แผนที่ → รัฐไหนเบี้ยวหนี้สูง*

1. **ตั้ง data category ก่อน (สำคัญ — ไม่งั้น map ไม่ขึ้น):**
   - Data pane → คลิกคอลัมน์ `dim_geography[addr_state]`
   - ribbon **Column tools → Data category → State or Province**
2. คลิกที่ว่าง → **Visualizations** → **Filled map** (ไอคอนแผนที่ระบาย)
3. field:
   - **Location:** `dim_geography[addr_state]`
   - **Tooltips / Color saturation:** `Default Rate %`
4. **Format:** Title "Default Rate % by State" · **Fill (Heat) colors** ไล่อ่อน→เข้มตาม Default Rate %
5. วาง: X=644, Y=438, W=620, H=210
> ⚠️ ถ้า map ว่าง: **File → Options → Security → ☑ Use Map and Filled Map visuals** แล้วเปิดใหม่

---

## A6 — Slicers 3 อัน (5 นาที)
1. คลิกที่ว่าง → **Visualizations** → **Slicer** → ลากใส่ `dim_date[year]`
2. คลิก `…` slicer → เปลี่ยนเป็น **Dropdown** (ประหยัดพื้นที่)
3. ทำซ้ำอีก 2 อัน: `dim_grade[grade]` · `dim_loan_status[status_group]`
4. วางเรียงล่าง: Y=656, H=56, X= 16 / 330 / 644 (W=290)
> ลองคลิกค่าใน slicer → กราฟทั้งหน้าจะกรองตาม = **interactive!**

## A7 — ตั้งชื่อหน้า + ขัดความสวย
- ดับเบิลคลิกแท็บหน้า (ล่าง) → เปลี่ยนชื่อเป็น **"Analytics"**
- **Insert → Text box** มุมบนซ้าย → "Loan Analytics — team01"
- **View → Themes** เลือกโทนน้ำเงิน (เข้า IRIS) · ใช้ accent สีเดียว
- เลือกทุก visual ที่เป็นคู่ → **Align + Distribute** ให้ตรง grid

---

# 🩺 PART B — หน้า Data Quality

> เพิ่มหน้าใหม่: คลิก **+** (มุมล่างซ้าย ข้างแท็บหน้า) → ตั้งชื่อ **"Data Quality"**

## B1 — Cards 3 ใบ (5 นาที)
ทำเหมือน A1 (Card) ใส่ measure:
| Card | measure | ความหมาย |
|---|---|---|
| **Data Rows** | `Total Rows` | แถวทั้งหมด (good + quarantine) |
| **Validity %** | `Validity %` | % แถวที่ผ่านกฎ |
| **Quarantine Rows** | `Quarantine Rows` | แถวที่ถูกคัด |
- จัด Align Top + Distribute เหมือนเดิม

## B2 — Donut: Good vs Quarantine (8 นาที)
ต้องรวม fact (good) กับ quarantine เป็นมิติเดียวก่อน — สร้าง **calculated table**:
1. ribbon **Modeling → New table** → วาง:
   ```DAX
   DQ Split =
   UNION (
       ROW ( "สถานะ", "ผ่าน (Good)",        "Rows", COUNTROWS ( fact_loan ) ),
       ROW ( "สถานะ", "ถูกคัด (Quarantine)", "Rows", COUNTROWS ( quarantine_loan ) )
   )
   ```
2. **Visualizations → Donut chart** →
   - **Legend:** `DQ Split[สถานะ]`
   - **Values:** `DQ Split[Rows]`
3. **Format:** Title "Validity — Good vs Quarantine" · **Detail labels** = Category, Percent

## B3 — Bar: เหตุผลที่ถูกคัด (8 นาที) — เด็ดสุดของ DQ!
*โชว์ว่า "ทำไม" แถวถึงถูก quarantine*
1. **Visualizations → Clustered bar chart**
   - **Y-axis:** `quarantine_loan[reject_reason]`
   - **X-axis:** `Quarantine Rows`  *(หรือลาก `reject_reason` ใส่ทั้ง Y และ X แล้วเปลี่ยน X เป็น Count)*
2. **Sort** มาก→น้อย
3. **Format:** Title "Quarantine by Reason"
> นี่คือหัวใจ Data Quality — เห็นเลยว่ากฎไหนคัดแถวออกมากสุด

## B4 — จัดหน้า DQ ให้สวย
- Cards บน · Donut + Bar ล่าง · Align/Distribute
- ใช้สีตามสไลด์ 23: Data Rows ฟ้า `#9DC3E6` · Validity เหลือง `#FFE699` · Completeness เขียว `#C6E0B4`

---

# ✅ STEP สุดท้าย — ตรวจ Reconcile + บันทึก

## ตรวจตัวเลขให้ตรงกับ ETL (5 นาที)
| Card | ควรได้ | เทียบกับ |
|---|---|---|
| Total Loans / Loaded Rows | **5,000** | จำนวนแถว fact_loan ใน MSSQL |
| Quarantine Rows | **20** | quarantine_loan |
| Total Rows | **5,020** | good + quarantine |
> ตรง = ข้อมูลครบถ้วน ไม่หล่นระหว่างทาง ✅

## บันทึก + แชร์
1. **File → Save as** → `Loan_Analytics_team01.pbix`
2. แชร์เป็น PDF: **File → Export → Create PDF/XPS** ⚠️ (อย่าใช้ "Save as Adobe PDF" — ภาษาไทยเพี้ยน)
3. ขึ้น cloud: **Home → Publish → My workspace** (ถ้ามี Power BI Service)

---

## 🎯 เช็กลิสต์จบ LAB 5
- [ ] หน้า Analytics: 5 cards + 4 กราฟ (combo/line/bar/map) + 3 slicers
- [ ] หน้า Data Quality: 3 cards + donut + bar เหตุผล
- [ ] slicer กดแล้วกราฟกรองตาม (interactive)
- [ ] ตัวเลขตรง reconcile (5,000 / 20 / 5,020)
- [ ] บันทึก .pbix + export PDF

🎉 **จบ! ได้ dashboard ที่เล่าเรื่องจากข้อมูลดิบจนถึงคำตอบธุรกิจ + วัดคุณภาพข้อมูลได้**

> 📐 DAX ทั้งหมด: `measures.dax` · ต้นแบบ DQ เต็ม: `github.com/amornpan/dq_power-bi`
