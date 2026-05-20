/* ============================================================
   app.js — IRIS Weather Dashboard Logic (Redesigned)
   ============================================================ */

'use strict';

// ── State ────────────────────────────────────────────────────
let rawData    = null;
let comboChart = null;
let tempChart  = null;
let humChart   = null;

// ── 7timer rh2m index → relative humidity % mapping ─────────
const RH_MAP = {
  1: 5, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45,
  9: 50, 10: 55, 11: 60, 12: 65, 13: 70, 14: 75, 15: 80, 16: 90
};

// Cloud cover code → Thai label + emoji
const CLOUD_MAP = {
  1:['☀️','แจ่มใส'],  2:['☀️','แจ่มใส'],
  3:['🌤','โปร่ง'],   4:['🌤','โปร่ง'],
  5:['⛅','เมฆบาง'], 6:['🌥','เมฆปานกลาง'],
  7:['☁️','เมฆมาก'], 8:['☁️','เมฆครึ้ม'],
  9:['☁️','เมฆครึ้ม']
};

// Precip type codes
const PREC_MAP = {
  snow:'🌨 หิมะ', rain:'🌧 ฝน',
  frzr:'🌨 ฝนเย็น', icep:'🌨 ลูกเห็บ', none:''
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

function getWeatherIcon(cloudCode) {
  return (CLOUD_MAP[cloudCode] || ['🌡',''])[0];
}

function getWeatherLabel(cloudCode) {
  return (CLOUD_MAP[cloudCode] || ['','ไม่ระบุ'])[1];
}

// ── Fetch ────────────────────────────────────────────────────
async function fetchWeather() {
  const lat = parseFloat(document.getElementById('lat-input').value);
  const lon = parseFloat(document.getElementById('lon-input').value);

  if (isNaN(lat) || isNaN(lon)) {
    showStatus('กรุณาระบุ Latitude / Longitude ให้ถูกต้อง', 'error');
    return;
  }

  showStatus('กำลังดึงข้อมูลจาก 7timer.info...', 'loading');
  setNavVisible(false);

  const apiUrl   = `https://www.7timer.info/bin/api.pl?lon=${lon}&lat=${lat}&product=civil&output=json`;
  const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;

  try {
    const res  = await fetch(proxyUrl, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data?.dataseries?.length) throw new Error('ข้อมูลไม่ถูกต้องหรือไม่มีข้อมูล');

    rawData = data;
    renderAll(data, lat, lon);
    showStatus(`โหลดสำเร็จ — ${data.dataseries.length} จุดเวลา`, 'success');
    setNavVisible(true);
    showTab('chart');
  } catch (err) {
    console.error(err);
    showStatus(`เกิดข้อผิดพลาด: ${err.message}`, 'error');
  }
}

// ── Render all ───────────────────────────────────────────────
function renderAll(data, lat, lon) {
  renderHero(data);
  renderForecastStrip(data);
  renderRaw(data, lat, lon);
  renderTable(data);
  renderCharts(data);
}

// ── Hero card ────────────────────────────────────────────────
function renderHero(data) {
  const first = data.dataseries[0];
  const temp  = first.temp2m;
  const rh    = decodeRH(first.rh2m);
  const cloud = first.cloudcover;
  const icon  = getWeatherIcon(cloud);
  const cond  = getWeatherLabel(cloud);

  const prec = first.prec_type && first.prec_type !== 'none'
    ? (PREC_MAP[first.prec_type] || first.prec_type) : '';

  // Temp stats
  const temps = data.dataseries.map(d => d.temp2m);
  const maxT  = Math.max(...temps);
  const minT  = Math.min(...temps);

  document.getElementById('hero-temp').textContent       = `${temp}°`;
  document.getElementById('hero-cond').textContent       = cond + (prec ? ' · ' + prec : '');
  document.getElementById('weather-icon-large').textContent = icon;
  document.getElementById('hero-location').innerHTML =
    `<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg> กรุงเทพมหานคร`;

  document.getElementById('hero-meta').innerHTML = `
    <span class="hero-pill">💧 ${rh}%</span>
    <span class="hero-pill">🌡 สูงสุด ${maxT}°</span>
    <span class="hero-pill">🌡 ต่ำสุด ${minT}°</span>
  `;

  document.getElementById('hero-stats-mini').innerHTML = `
    <div class="mini-stat">
      <div class="mini-stat-value ${tempClass(maxT)}">${maxT}°</div>
      <div class="mini-stat-label">สูงสุด</div>
    </div>
    <div class="mini-stat">
      <div class="mini-stat-value ${tempClass(minT)}">${minT}°</div>
      <div class="mini-stat-label">ต่ำสุด</div>
    </div>
  `;

  const heroSection = document.getElementById('hero-section');
  heroSection.classList.add('visible');
}

// ── Forecast Strip ───────────────────────────────────────────
function renderForecastStrip(data) {
  const init     = data.init ?? '';
  const initDate = parseInit(init);
  const strip    = document.getElementById('forecast-strip');
  strip.innerHTML = '';

  // Show first 12 timepoints
  const items = data.dataseries.slice(0, 12);
  items.forEach((d, i) => {
    const temp = d.temp2m;
    const rh   = decodeRH(d.rh2m);
    const icon = getWeatherIcon(d.cloudcover);
    const dt   = initDate ? addHours(initDate, d.timepoint) : null;
    const timeLabel = dt ? formatStrip(dt) : `+${d.timepoint}h`;

    const div = document.createElement('div');
    div.className = 'forecast-item' + (i === 0 ? ' active-item' : '');
    div.innerHTML = `
      <div class="fi-time">${timeLabel}</div>
      <div class="fi-icon">${icon}</div>
      <div class="fi-temp ${tempClass(temp)}">${temp}°</div>
      <div class="fi-hum">💧 ${rh}%</div>
    `;
    strip.appendChild(div);
  });
}

// ── Raw JSON ─────────────────────────────────────────────────
function renderRaw(data, lat, lon) {
  document.getElementById('raw-output').textContent = JSON.stringify(data, null, 2);

  const init    = data.init ?? '';
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

// ── Table ────────────────────────────────────────────────────
function renderTable(data) {
  const init     = data.init ?? '';
  const initDate = parseInit(init);
  const tbody    = document.getElementById('table-body');
  tbody.innerHTML = '';

  data.dataseries.forEach((d, i) => {
    const rh    = decodeRH(d.rh2m);
    const temp  = d.temp2m;
    const tp    = d.timepoint;
    const dt    = initDate ? addHours(initDate, tp) : null;
    const dtStr = dt ? formatDate(dt) : `+${tp}h`;
    const cloud = getWeatherLabel(d.cloudcover);
    const icon  = getWeatherIcon(d.cloudcover);

    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="td-idx">${i + 1}</td>
      <td class="td-tp">+${tp}h</td>
      <td class="td-time">${dtStr}</td>
      <td class="td-temp ${tempClass(temp)}">${temp}°C</td>
      <td><span class="badge-hum">💧 ${rh}%</span></td>
      <td><span class="badge-cond">${icon} ${cloud}</span></td>
    `;
    tbody.appendChild(row);
  });
}

// ── Charts ───────────────────────────────────────────────────
function renderCharts(data) {
  const init     = data.init ?? '';
  const initDate = parseInit(init);

  const labels = data.dataseries.map(d => {
    if (initDate) return formatShort(addHours(initDate, d.timepoint));
    return `+${d.timepoint}h`;
  });

  const temps   = data.dataseries.map(d => d.temp2m);
  const humsRaw = data.dataseries.map(d => decodeRH(d.rh2m));

  // Destroy old
  [comboChart, tempChart, humChart].forEach(c => c?.destroy());

  // Combo
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
          borderColor: '#f97316',
          backgroundColor: createAreaGradient(ctxCombo, '#f97316', 0.25, 0.02),
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 7,
          pointBackgroundColor: '#f97316',
          pointBorderColor: '#050810',
          pointBorderWidth: 2,
          fill: true,
          tension: 0.45,
          order: 1,
        },
        {
          type: 'bar',
          label: 'ความชื้น (%)',
          data: humsRaw,
          yAxisID: 'yHum',
          backgroundColor: humsRaw.map(h => `rgba(99,102,241,${h >= 70 ? 0.55 : h >= 50 ? 0.35 : 0.2})`),
          borderColor: 'rgba(99,102,241,0.65)',
          borderWidth: 1,
          borderRadius: 6,
          borderSkipped: false,
          order: 2,
        }
      ]
    },
    options: makeOptions({
      scales: {
        x: xAxis(),
        yTemp: {
          type: 'linear', position: 'left',
          title: { display: true, text: 'อุณหภูมิ (°C)', color: '#f97316', font: { size: 11, weight: '600', family: 'Space Grotesk' } },
          ticks: { color: '#64748b', font: { size: 10 } },
          grid: { color: 'rgba(255,255,255,0.04)' },
        },
        yHum: {
          type: 'linear', position: 'right',
          min: 0, max: 100,
          title: { display: true, text: 'ความชื้น (%)', color: '#6366f1', font: { size: 11, weight: '600', family: 'Space Grotesk' } },
          ticks: { color: '#64748b', font: { size: 10 } },
          grid: { drawOnChartArea: false },
        }
      }
    })
  });

  // Temp only
  const ctxTemp = document.getElementById('temp-chart').getContext('2d');
  tempChart = new Chart(ctxTemp, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'อุณหภูมิ (°C)',
        data: temps,
        borderColor: '#f97316',
        backgroundColor: createAreaGradient(ctxTemp, '#f97316', 0.3, 0.02),
        borderWidth: 2,
        pointRadius: 2.5,
        pointHoverRadius: 6,
        pointBackgroundColor: '#f97316',
        pointBorderColor: '#050810',
        pointBorderWidth: 1.5,
        fill: true,
        tension: 0.45,
      }]
    },
    options: makeOptions({ scales: { x: xAxis(true), y: yAxis('°C') } })
  });

  // Humidity
  const ctxHum = document.getElementById('humidity-chart').getContext('2d');
  humChart = new Chart(ctxHum, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'ความชื้น (%)',
        data: humsRaw,
        backgroundColor: humsRaw.map(h =>
          h >= 70 ? 'rgba(59,130,246,0.7)' :
          h >= 50 ? 'rgba(99,102,241,0.5)' :
                    'rgba(139,92,246,0.35)'
        ),
        borderColor: 'rgba(99,102,241,0.7)',
        borderWidth: 1,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: makeOptions({ scales: { x: xAxis(true), y: { ...yAxis('%'), min: 0, max: 100 } } })
  });

  renderStats(temps, humsRaw);
}

// Stat cards
function renderStats(temps, hums) {
  const maxT = Math.max(...temps), minT = Math.min(...temps);
  const avgT = (temps.reduce((a,b)=>a+b,0)/temps.length).toFixed(1);
  const maxH = Math.max(...hums),  minH = Math.min(...hums);
  const avgH = (hums.reduce((a,b)=>a+b,0)/hums.length).toFixed(0);

  const cards = [
    { label:'🌡 สูงสุด',  value: maxT, unit:'°C', cls:'hot',   color:'#f97316' },
    { label:'🌡 ต่ำสุด',  value: minT, unit:'°C', cls:'warm',  color:'#fbbf24' },
    { label:'🌡 เฉลี่ย',  value: avgT, unit:'°C', cls:'avg',   color:'#14b8a6' },
    { label:'💧 ชื้นสุด', value: maxH, unit:'%',  cls:'humid', color:'#3b82f6' },
    { label:'💧 แห้งสุด', value: minH, unit:'%',  cls:'dry',   color:'#10b981' },
    { label:'💧 เฉลี่ย',  value: avgH, unit:'%',  cls:'mid',   color:'#8b5cf6' },
  ];

  document.getElementById('stat-cards').innerHTML = cards.map(c => `
    <div class="stat-card ${c.cls}">
      <div class="s-label">${c.label}</div>
      <div class="s-value" style="color:${c.color}">${c.value}</div>
      <div class="s-unit">${c.unit}</div>
    </div>
  `).join('');
}

// ── Chart helpers ────────────────────────────────────────────
function makeOptions(extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: 'easeOutQuart' },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: {
          color: '#94a3b8',
          font: { size: 12, family: 'Space Grotesk' },
          boxWidth: 10,
          padding: 16,
          usePointStyle: true,
          pointStyle: 'circle',
        }
      },
      tooltip: {
        backgroundColor: 'rgba(5,8,16,0.95)',
        borderColor: 'rgba(99,102,241,0.3)',
        borderWidth: 1,
        titleColor: '#f8fafc',
        bodyColor: '#94a3b8',
        padding: 14,
        cornerRadius: 10,
        titleFont: { family: 'Space Grotesk', weight: '700', size: 13 },
        bodyFont:  { family: 'Space Grotesk', size: 12 },
        caretSize: 6,
      }
    },
    ...extra,
  };
}

function xAxis(compact = false) {
  return {
    ticks: {
      color: '#475569',
      font: { size: compact ? 9 : 10, family: 'Space Grotesk' },
      maxTicksLimit: compact ? 8 : 16,
      maxRotation: 45,
    },
    grid: { color: 'rgba(255,255,255,0.03)' },
    border: { color: 'rgba(255,255,255,0.05)' },
  };
}

function yAxis(unit) {
  return {
    ticks: { color: '#64748b', font: { size: 10, family: 'Space Grotesk' } },
    grid: { color: 'rgba(255,255,255,0.04)' },
    border: { color: 'rgba(255,255,255,0.05)' },
    title: { display: true, text: unit, color: '#475569', font: { size: 10, family: 'Space Grotesk' } }
  };
}

function createAreaGradient(ctx, hexColor, alphaTop, alphaBottom) {
  // Safe parse — return static fallback if canvas isn't sized yet
  try {
    const g = ctx.createLinearGradient(0, 0, 0, 350);
    // Convert hex to rgb
    const r = parseInt(hexColor.slice(1,3), 16);
    const ge = parseInt(hexColor.slice(3,5), 16);
    const b = parseInt(hexColor.slice(5,7), 16);
    g.addColorStop(0, `rgba(${r},${ge},${b},${alphaTop})`);
    g.addColorStop(1, `rgba(${r},${ge},${b},${alphaBottom})`);
    return g;
  } catch {
    return `rgba(249,115,22,0.12)`;
  }
}

// ── Date helpers ─────────────────────────────────────────────
function parseInit(init) {
  if (!init || init.length < 10) return null;
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

function formatStrip(dt) {
  return dt.toLocaleString('th-TH', {
    timeZone: 'Asia/Bangkok',
    weekday: 'short',
    hour: '2-digit', hour12: false
  });
}

// ── UI helpers ───────────────────────────────────────────────
function showStatus(msg, type = 'loading') {
  const bar  = document.getElementById('status-bar');
  const text = document.getElementById('status-text');
  text.textContent = msg;
  bar.className = 'status-sidebar' + (type !== 'loading' ? ` ${type}` : '');
  bar.classList.remove('hidden');
}

function setNavVisible(v) {
  const nav = document.getElementById('sidebar-nav');
  nav.style.display = v ? 'flex' : 'none';
  ['raw','table','chart'].forEach(id => {
    document.getElementById(`panel-${id}`).classList.add('hidden');
  });
  document.getElementById('empty-state').classList.toggle('hidden', v);
}

function showTab(name) {
  ['raw','table','chart'].forEach(id => {
    const navEl = document.getElementById(`nav-${id}`);
    const panEl = document.getElementById(`panel-${id}`);
    if (navEl) navEl.classList.toggle('active', id === name);
    panEl.classList.toggle('hidden', id !== name);
  });
}

function copyRaw() {
  if (!rawData) return;
  navigator.clipboard.writeText(JSON.stringify(rawData, null, 2))
    .then(() => {
      const btn = document.getElementById('copy-btn');
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
      btn.style.color = '#10b981';
      setTimeout(() => {
        btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy JSON`;
        btn.style.color = '';
      }, 2000);
    });
}

// ── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Show empty state initially
  document.getElementById('empty-state').classList.remove('hidden');
  // Auto-fetch
  fetchWeather();
});

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (
    e.target.id === 'lat-input' || e.target.id === 'lon-input'
  )) fetchWeather();
});
