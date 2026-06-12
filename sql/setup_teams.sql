/* ============================================================================
   Workshop Data Warehouse — setup (run ONCE with an admin login, e.g. sa)

   Approach: ทุกคนใช้ login เดียวกัน (deadmin = db_owner) เขียนลง de_loan_dw
   กันชนกันด้วยการ "นำหน้าชื่อตารางด้วย TEAM_ID" (เช่น team01_fact_loan) ใน notebook 03
   => ไม่ต้องสร้าง schema/login รายทีม

   เข้า sqlcmd ก่อน (เปลี่ยนชื่อ container/รหัส sa ตามจริง — ใช้ single quote!):
     docker exec -it sql1 /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P '<SA_PASSWORD>' -No

   หมายเหตุ: GO ต้องอยู่บรรทัดเดียวโดดๆ (ห้ามมี ;) • ถ้าขึ้น "already exists" = มีแล้ว ข้ามได้
   ============================================================================ */

-- 1) Database
CREATE DATABASE de_loan_dw;
GO

-- 2) Login (ระดับ Server) — ต้องสร้างก่อน CREATE USER เสมอ
CREATE LOGIN deadmin WITH PASSWORD = 'de@admin2026';
GO

-- 3) User + สิทธิ์เต็ม (อ่าน + เขียน + สร้างตาราง)
USE de_loan_dw;
GO
CREATE USER deadmin FOR LOGIN deadmin;   -- FOR LOGIN = ชื่อ login (deadmin) ไม่ใช่ชื่อ database
GO
ALTER ROLE db_owner ADD MEMBER deadmin;
GO

-- 4) ตรวจสอบ
SELECT IS_ROLEMEMBER('db_owner', 'deadmin') AS is_db_owner;   -- ควรได้ 1
GO
