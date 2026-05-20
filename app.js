/* ============================================================
   app.js — 7Timer Weather Dashboard Logic
   ============================================================ */

'use strict';

// ── State ────────────────────────────────────────────────────
let rawData = null;
let comboChart = null;
let tempChart  = null;
let humChart   = null;

// ── 7timer rh2m index → relative humidity % mapping ─────────
// 7timer API codes 1-16 map to fixed RH values
const RH_MAP = {
  1: 5, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45,
  9: 50, 10: 55, 11: 60, 12: 65, 13: 70, 14: 75, 15: 80,
  16: 90
};

// Cloud cover code → description
const CLOUD_MAP = {
  1:'แจ่มใส', 2:'แจ่มใส', 3:'โปร่ง', 4:'โปร่ง',
  5:'มีเมฆบาง', 6:'มีเมฆปานกลาง', 7:'มีเมฆมาก', 8:'เมฆครึ้ม', 9:'เมฆครึ้ม'
};

function decodeRH(code) {
  return RH_MAP[code] ?? (code <= 0 ? 0 : 95);
}

function tempClass(t) {
  if (t >= 35) return 'temp-hot';
  if (t >= 28) return 'temp-warm';
  if (t >= 20) return 'temp-cool';
  return 'temp-cold';
}

// ── Fetch ────────────────────────────────────────────────────
async function fetchWeather() {
  const lat = parseFloat(document.getElementById('lat-input').value);
  const lon = parseFloat(document.getElementById('lon-input').value);

  if (isNaN(lat) || isNaN(lon)) {
    showStatus('กรุณาระบุ Latitude และ Longitude ให้ถูกต้อง', 'error');
    return;
  }

  showStatus('กำลังดึงข้อมูลจาก 7timer.info...', 'loading');
  setTabsVisible(false);

  // Use a CORS proxy since 7timer doesn't send CORS headers
  const apiUrl = `https://www.7timer.info/bin/api.pl?lon=${lon}&lat=${lat}&product=civil&output=json`;
  const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;

  try {
    const res = await fetch(proxyUrl, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data?.dataseries?.length) throw new Error('ข้อมูลไม่ถูกต้องหรือไม่มีข้อมูล');

    rawData = data;
    renderAll(data, lat, lon);
    showStatus(`โหลดข้อมูลสำเร็จ — ${data.dataseries.length} จุดเวลา`, 'success');
    setTabsVisible(true);
    showTab('chart');    // default to chart view
  } catch (err) {
    console.error(err);
    showStatus(`เกิดข้อผิดพลาด: ${err.message} — ลองใหม่หรือตรวจสอบการเชื่อมต่ออินเทอร์เน็ต`, 'error');
  }
}

// ── Render all panels ────────────────────────────────────────
function renderAll(data, lat, lon) {
  renderRaw(data, lat, lon);
  renderTable(data);
  renderCharts(data);
}

// ── Panel 1: Raw JSON ────────────────────────────────────────
function renderRaw(data, lat, lon) {
  document.getElementById('raw-output').textContent = JSON.stringify(data, null, 2);

  const init = data.init ?? '';
  const initStr = init
    ? `${init.slice(0,4)}-${init.slice(4,6)}-${init.slice(6,8)} ${init.slice(8,10)}:00 UTC`
    : '-';

  document.getElementById('raw-meta').innerHTML = `
    <div class="chip">Product: <span>${data.product ?? '-'}</span></div>
    <div class="chip">Init: <span>${initStr}</span></div>
    <div class="chip">จุดเวลา: <span>${data.dataseries.length}</span></div>
    <div class="chip">Lat/Lon: <span>${lat}, ${lon}</span></div>
  `;
}

// ── Panel 2: Table ───────────────────────────────────────────
function renderTable(data) {
  const init = data.init ?? '';
  const initDate = parseInit(init);
  const tbody = document.getElementById('table-body');
  tbody.innerHTML = '';

  data.dataseries.forEach((d, i) => {
    const rh   = decodeRH(d.rh2m);
    const temp = d.temp2m;
    const tp   = d.timepoint;
    const dt   = initDate ? addHours(initDate, tp) : null;
    const dtStr = dt ? formatDate(dt) : `+${tp}h`;
    const cloud = CLOUD_MAP[d.cloudcover] ?? '-';

    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="td-idx">${i + 1}</td>
      <td class="td-tp"><strong>+${tp}</strong> h</td>
      <td class="td-time">${dtStr}</td>
      <td class="td-temp ${tempClass(temp)}">${temp} °C</td>
      <td><span class="badge-hum">💧 ${rh}%</span></td>
      <td><span class="badge-cond">${cloud}</span></td>
    `;
    tbody.appendChild(row);
  });
}

// ── Panel 3: Charts ──────────────────────────────────────────
function renderCharts(data) {
  const init = data.init ?? '';
  const initDate = parseInit(init);

  const labels = data.dataseries.map(d => {
    if (initDate) {
      const dt = addHours(initDate, d.timepoint);
      return formatShort(dt);
    }
    return `+${d.timepoint}h`;
  });

  const temps = data.dataseries.map(d => d.temp2m);
  const humsRaw = data.dataseries.map(d => decodeRH(d.rh2m));

  // Destroy old charts
  [comboChart, tempChart, humChart].forEach(c => c?.destroy());

  // --- Combo chart ---
  const ctxCombo = document.getElementById('combo-chart').getContext('2d');
  comboChart = new Chart(ctxCombo, {
    data: {
      labels,
      datasets: [
        {
          type: 'line',
          label: 'อุณหภูมิ (°C)',
          data: temps,
          yAxisID: 'yTemp',
          borderColor: '#fb923c',
          backgroundColor: 'rgba(251,146,60,0.12)',
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#fb923c',
          fill: true,
          tension: 0.4,
          order: 1,
        },
        {
          type: 'bar',
          label: 'ความชื้น (%)',
          data: humsRaw,
          yAxisID: 'yHum',
          backgroundColor: 'rgba(79,142,255,0.22)',
          borderColor: 'rgba(79,142,255,0.7)',
          borderWidth: 1.5,
          borderRadius: 6,
          order: 2,
        }
      ]
    },
    options: chartOptions({
      scales: {
        x: xAxis(),
        yTemp: {
          type: 'linear', position: 'left',
          title: { display: true, text: 'อุณหภูมิ (°C)', color: '#fb923c', font: { size: 12, weight: 600 } },
          ticks: { color: '#94a3b8', font: { size: 11 } },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
        yHum: {
          type: 'linear', position: 'right',
          min: 0, max: 100,
          title: { display: true, text: 'ความชื้น (%)', color: '#4f8eff', font: { size: 12, weight: 600 } },
          ticks: { color: '#94a3b8', font: { size: 11 } },
          grid: { drawOnChartArea: false },
        }
      }
    })
  });

  // --- Temperature line only ---
  const ctxTemp = document.getElementById('temp-chart').getContext('2d');
  tempChart = new Chart(ctxTemp, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'อุณหภูมิ (°C)',
        data: temps,
        borderColor: '#fb923c',
        backgroundColor: createGradient(ctxTemp, '#fb923c'),
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.45,
      }]
    },
    options: chartOptions({ scales: { x: xAxis(true), y: yAxis('°C') } })
  });

  // --- Humidity bar only ---
  const ctxHum = document.getElementById('humidity-chart').getContext('2d');
  humChart = new Chart(ctxHum, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'ความชื้น (%)',
        data: humsRaw,
        backgroundColor: humsRaw.map(h =>
          h >= 70 ? 'rgba(79,142,255,0.65)' :
          h >= 50 ? 'rgba(79,142,255,0.4)' :
                    'rgba(79,142,255,0.22)'
        ),
        borderColor: 'rgba(79,142,255,0.8)',
        borderWidth: 1.5,
        borderRadius: 5,
      }]
    },
    options: chartOptions({ scales: { x: xAxis(true), y: { ...yAxis('%'), min: 0, max: 100 } } })
  });

  // Stat cards
  renderStats(temps, humsRaw);
}

function renderStats(temps, hums) {
  const maxT = Math.max(...temps), minT = Math.min(...temps);
  const avgT = (temps.reduce((a,b)=>a+b,0)/temps.length).toFixed(1);
  const maxH = Math.max(...hums), minH = Math.min(...hums);
  const avgH = (hums.reduce((a,b)=>a+b,0)/hums.length).toFixed(0);

  document.getElementById('stat-cards').innerHTML = `
    <div class="stat-card">
      <div class="s-label">🌡 สูงสุด</div>
      <div class="s-value temp-hot">${maxT}</div>
      <div class="s-unit">°C</div>
    </div>
    <div class="stat-card">
      <div class="s-label">🌡 ต่ำสุด</div>
      <div class="s-value temp-cool">${minT}</div>
      <div class="s-unit">°C</div>
    </div>
    <div class="stat-card">
      <div class="s-label">🌡 เฉลี่ย</div>
      <div class="s-value temp-warm">${avgT}</div>
      <div class="s-unit">°C</div>
    </div>
    <div class="stat-card">
      <div class="s-label">💧 ชื้นสุด</div>
      <div class="s-value" style="color:var(--accent-1)">${maxH}</div>
      <div class="s-unit">%</div>
    </div>
    <div class="stat-card">
      <div class="s-label">💧 แห้งสุด</div>
      <div class="s-value" style="color:var(--accent-3)">${minH}</div>
      <div class="s-unit">%</div>
    </div>
    <div class="stat-card">
      <div class="s-label">💧 เฉลี่ย</div>
      <div class="s-value" style="color:var(--accent-2)">${avgH}</div>
      <div class="s-unit">%</div>
    </div>
  `;
}

// ── Chart helpers ────────────────────────────────────────────
function chartOptions(extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 700, easing: 'easeOutCubic' },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: { color: '#94a3b8', font: { size: 12, family: 'Outfit' }, boxWidth: 12, padding: 16 }
      },
      tooltip: {
        backgroundColor: 'rgba(8,12,24,0.92)',
        borderColor: 'rgba(255,255,255,0.12)',
        borderWidth: 1,
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        padding: 12,
        cornerRadius: 10,
        titleFont: { family: 'Outfit', weight: '700' },
        bodyFont:  { family: 'Outfit' },
      }
    },
    ...extra,
  };
}

function xAxis(compact = false) {
  return {
    ticks: {
      color: '#64748b',
      font: { size: compact ? 9 : 10, family: 'Outfit' },
      maxTicksLimit: compact ? 8 : 16,
      maxRotation: 45,
    },
    grid: { color: 'rgba(255,255,255,0.04)' },
  };
}

function yAxis(unit) {
  return {
    ticks: { color: '#94a3b8', font: { size: 11 } },
    grid: { color: 'rgba(255,255,255,0.05)' },
    title: { display: true, text: unit, color: '#64748b', font: { size: 11 } }
  };
}

function createGradient(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, color.replace(')', ', 0.35)').replace('rgb', 'rgba'));
  g.addColorStop(1, color.replace(')', ', 0)').replace('rgb', 'rgba'));
  // fallback: just return rgba string
  return `rgba(251,146,60,0.18)`;
}

// ── Date helpers ─────────────────────────────────────────────
function parseInit(init) {
  if (!init || init.length < 10) return null;
  // Format: YYYYMMDDhh
  const y = +init.slice(0,4), mo = +init.slice(4,6)-1,
        d = +init.slice(6,8), h  = +init.slice(8,10);
  return new Date(Date.UTC(y, mo, d, h));
}

function addHours(date, h) {
  return new Date(date.getTime() + h * 3600 * 1000);
}

function formatDate(dt) {
  return dt.toLocaleString('th-TH', {
    timeZone: 'Asia/Bangkok',
    day: '2-digit', month: 'short', year: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
  });
}

function formatShort(dt) {
  return dt.toLocaleString('th-TH', {
    timeZone: 'Asia/Bangkok',
    day: '2-digit', month: 'short',
    hour: '2-digit', hour12: false
  });
}

// ── UI helpers ───────────────────────────────────────────────
function showStatus(msg, type = 'loading') {
  const bar  = document.getElementById('status-bar');
  const text = document.getElementById('status-text');
  text.textContent = msg;
  bar.className = 'status-bar' + (type !== 'loading' ? ` ${type}` : '');
}

function setTabsVisible(v) {
  document.getElementById('tab-nav').style.display = v ? 'flex' : 'none';
  ['raw','table','chart'].forEach(id => {
    document.getElementById(`panel-${id}`).classList.add('hidden');
  });
}

function showTab(name) {
  ['raw','table','chart'].forEach(id => {
    document.getElementById(`tab-${id}`).classList.toggle('active', id === name);
    document.getElementById(`panel-${id}`).classList.toggle('hidden', id !== name);
  });
}

function copyRaw() {
  if (!rawData) return;
  navigator.clipboard.writeText(JSON.stringify(rawData, null, 2))
    .then(() => {
      const btn = document.querySelector('.copy-btn');
      btn.textContent = '✅ Copied!';
      setTimeout(() => { btn.textContent = '📋 Copy'; }, 2000);
    });
}

// ── Auto-load on page ready ──────────────────────────────────
document.addEventListener('DOMContentLoaded', fetchWeather);

// Allow pressing Enter in inputs
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (
    e.target.id === 'lat-input' || e.target.id === 'lon-input'
  )) fetchWeather();
});
