# Day 3 — Teaching Slides

**`Day3_Workshop_Slides.pdf`** — สไลด์สอน 28 หน้า สำหรับเวิร์กช็อป 1 วัน
(ETL → MSSQL star schema → Power BI) พื้นหลังแบรนด์ **BOI STEM++ / IRIS BrighterBee**

แยก 2 โหมดชัดเจน (chip มุมขวาล่างทุกสไลด์เนื้อหา):
- **📖 CONCEPT** — สไลด์บรรยาย / อธิบายโค้ด (ฟัง·ดู — มือยังไม่แตะคีย์บอร์ด)
- **🧪 LAB** — สไลด์ checkpoint ลงมือทำ (หยุดบรรยาย → เปิด notebook/Power BI ทำตามขั้น มีเวลากำกับ + ผลลัพธ์ที่จะได้)

โครงสไลด์: Title · Agenda · โจทย์ธุรกิจ · Architecture · (เช้า) Setup / Explore →
**LAB 1** → Data Model / Star Schema / Clean / Validate / Transform → **LAB 2** →
Load MSSQL → **LAB 3** · (บ่าย) ติดตั้ง Power BI / Connect+Model+DAX → **LAB 4** →
Dashboard Layout → **LAB 5** (STEP 0 → DAX Measures → A1 Cards → A2 Combo →
A3+A4 Line/Bar → A5 Map) · สรุป + Q&A

## สร้างใหม่ / แก้ไข
```bash
pip install python-pptx
python build_slides.py      # อ่าน assets/bg_iris.jpg -> Day3_Workshop_Slides.pptx
```
- `build_slides.py` — ตัว generator (แก้ข้อความ/เลย์เอาต์ที่นี่ แล้วรันใหม่)
- `assets/bg_iris.jpg` — พื้นเนื้อหา · `assets/bg_cover_dark.jpg` — พื้นปก (สไลด์ 1)
- ⚠️ `build_slides.py` สร้างเด็คเวอร์ชันแรก (25 หน้า) — เวอร์ชันปัจจุบัน 28 หน้า
  แก้เพิ่มเติมในไฟล์ .pptx โดยตรง แล้ว export เป็น `Day3_Workshop_Slides.pdf` ที่ commit ไว้

## ฟอนต์ (macOS-like)
- **อังกฤษ:** Inter (≈ SF Pro) · **ไทย:** Kanit (≈ Sukhumvit) · **โค้ด:** Cascadia Mono
- repo เก็บเฉพาะ **`.pdf`** (ฟอนต์ฝังในตัวโดยธรรมชาติ → เปิดเครื่องไหนก็ไม่เพี้ยน)
- ถ้า regenerate `.pptx`: ต้องมี Inter + Kanit + Cascadia ในเครื่อง แล้ว embed ฟอนต์ผ่าน PowerPoint COM
  → `$pres.SaveAs(path, 24, -1)`  (24 = pptx, -1 = embed fonts) · export PDF → `$pres.SaveAs(path, 32)`

> หมายเหตุ: render QA บน Windows ใช้ PowerPoint COM (`$pres.Export(...,"PNG")`) — เครื่องนี้ไม่มี LibreOffice
