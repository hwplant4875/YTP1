(() => {
// "UI kinetic" motion-graphics engine (16:9, crisp vector, no hand-drawn boil).
// Reference grammar: one lyric/line per scene, words appear one by one, every scene is a
// real-world interface or diagram (terminal, departure board, chart, monitor, calendar, label).
const C = {
  ink: '#0f1016', ink2: '#171923', paper: '#ececef', cream: '#f2ede2',
  text: '#e9e9ee', dim: '#6c6f7d', line: '#3a3d4c', acc: '#ff6a2b', acc2: '#ffb38a', blue: '#7f8cff',
};
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const eo = k => 1 - Math.pow(1 - clamp(k), 3);          // ease-out cubic
const eio = k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const hash = (i, s = 0) => { const x = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); };

function font(ctx, f) { ctx.font = f; }
// Words appear one after another (fade + slight rise + un-blur). *word* = accent colour.
function words(ctx, str, x, y, t, t0, opt = {}) {
  const per = opt.per ?? 0.16, f = opt.font, col = opt.color ?? C.text, acc = opt.acc ?? C.acc;
  font(ctx, f); ctx.textBaseline = 'alphabetic';
  const toks = str.split(' ');
  let cx = x;
  if (opt.align === 'center') {
    const total = toks.reduce((s, w) => s + ctx.measureText(w.replace(/\*/g, '') + ' ').width, 0) - ctx.measureText(' ').width;
    cx = x - total / 2;
  }
  toks.forEach((w, i) => {
    const hl = w.startsWith('*'), clean = w.replace(/\*/g, '');
    const k = eo((t - t0 - i * per) / 0.28);
    const wdt = ctx.measureText(clean + ' ').width;
    if (k > 0) {
      ctx.save(); ctx.globalAlpha = k * (opt.alpha ?? 1);
      if (k < 1) ctx.filter = `blur(${(1 - k) * 6}px)`;
      ctx.fillStyle = hl ? acc : col; ctx.fillText(clean, cx, y + (1 - k) * 14); ctx.restore();
    }
    cx += wdt;
  });
}
// Typewriter with block cursor.
function typed(ctx, str, x, y, t, t0, cps, opt = {}) {
  const n = clamp(Math.floor((t - t0) * cps), 0, str.length);
  if (t < t0) return 0;
  font(ctx, opt.font); ctx.fillStyle = opt.color ?? C.text; ctx.textBaseline = 'alphabetic';
  const s = str.slice(0, n); ctx.fillText(s, x, y);
  const w = ctx.measureText(s).width, done = n >= str.length;
  if (opt.cursor !== false && (!done || (opt.keepCursor && Math.floor(t * 2.2) % 2 === 0))) {
    const m = ctx.measureText('M'); ctx.fillStyle = opt.cursorColor ?? ctx.fillStyle;
    ctx.fillRect(x + w + 3, y - m.actualBoundingBoxAscent, m.width * 0.6, m.actualBoundingBoxAscent + 4);
  }
  return n;
}
function label(ctx, s, x, y, col = C.dim, size = 15, align = 'left') {
  ctx.font = `500 ${size}px Plex`; ctx.fillStyle = col; ctx.textAlign = align; ctx.fillText(s, x, y); ctx.textAlign = 'left';
}
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// Draw a polyline progressively (0..1), returns head point.
function drawOn(ctx, pts, k, col, w) {
  const n = Math.max(2, Math.floor(pts.length * clamp(k)));
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); pts.slice(0, n).forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); ctx.restore();
  return pts[n - 1];
}
function glowDot(ctx, x, y, col, r = 7) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 5); g.addColorStop(0, col); g.addColorStop(1, 'rgba(255,106,43,0)');
  ctx.fillStyle = g; ctx.fillRect(x - r * 5, y - r * 5, r * 10, r * 10);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x, y, r * 0.55, 0, 7); ctx.fill();
}
function vignette(ctx, W, H, a = 0.5) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function grid(ctx, W, H, step, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 1;
  for (let x = 0; x <= W; x += step) { ctx.beginPath(); ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); ctx.stroke(); }
  for (let y = 0; y <= H; y += step) { ctx.beginPath(); ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); ctx.stroke(); }
  ctx.restore();
}

// ---------- S1 terminal: the alarm ----------
function s1(ctx, W, H, t) {
  ctx.fillStyle = '#0b0c10'; ctx.fillRect(0, 0, W, H);
  const f = '500 36px Plex', x = 120;
  ctx.fillStyle = C.dim; ctx.font = f; ctx.fillText('me@life:~$ alarm --at 05:00 --repeat daily', x, 160);
  ctx.fillStyle = C.text; ctx.font = f; ctx.fillText('ALARM ▸ ringing', x, 215);
  const n = typed(ctx, 'snooze? [Y/n] ', x, 270, t, 0.8, 26, { font: f, color: C.text, cursor: false });
  if (t > 0.8) {
    ctx.font = f; const w = ctx.measureText('snooze? [Y/n] ').width;
    if (t > 1.9) { ctx.fillStyle = C.acc; ctx.fillText('n', x + w, 270); }
    else if (n >= 14 && Math.floor(t * 3) % 2 === 0) { ctx.fillStyle = C.text; ctx.fillRect(x + w + 2, 243, 20, 32); }
  }
  typed(ctx, '> getting up.', x, 325, t, 2.2, 28, { font: f, color: C.text });
  typed(ctx, '> excuses.exe has stopped responding', x, 380, t, 2.9, 40, { font: f, color: C.acc, keepCursor: true });
  // big clock on the right
  const sec = t < 1.3 ? 58 + Math.floor(t / 0.65) : 0, mm = t < 1.3 ? 59 : 0, hh = t < 1.3 ? 4 : 5;
  const clk = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
  ctx.font = '600 230px Inter'; ctx.textAlign = 'right'; ctx.fillStyle = t < 1.3 ? '#8d90a0' : C.text;
  ctx.fillText(clk, W - 120, 720);
  ctx.font = '500 40px Plex'; ctx.fillStyle = t < 1.3 ? '#8d90a0' : C.acc; ctx.fillText(':' + String(sec).padStart(2, '0'), W - 120, 790);
  ctx.textAlign = 'left';
  if (t >= 1.3 && t < 1.9) { // ring pulse
    const k = (t - 1.3) / 0.6; ctx.strokeStyle = `rgba(255,106,43,${1 - k})`; ctx.lineWidth = 3;
    ctx.strokeRect(W - 820 - k * 30, 520 - k * 30, 720 + k * 60, 300 + k * 60);
  }
  label(ctx, 'TTY1   pid 0500   uptime 00:00:0' + Math.floor(t), 120, H - 90);
  vignette(ctx, W, H, 0.6);
}

// ---------- S2 split-flap departure board ----------
const FLAP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:';
function flapCell(ctx, x, y, w, h, ch, t, settle, seed) {
  ctx.fillStyle = '#1b1c22'; rr(ctx, x, y, w, h, 4); ctx.fill();
  ctx.fillStyle = '#23242c'; rr(ctx, x, y, w, h / 2, 4); ctx.fill();
  let c = ch;
  if (t < settle) c = FLAP[Math.floor(hash(Math.floor(t * 22), seed) * FLAP.length)];
  if (t < settle - 1.2) c = ' ';
  ctx.fillStyle = '#f3f3f5'; ctx.font = `600 ${Math.floor(h * 0.62)}px Oswald`; ctx.textAlign = 'center';
  ctx.fillText(c, x + w / 2, y + h * 0.74); ctx.textAlign = 'left';
  ctx.fillStyle = '#0d0e12'; ctx.fillRect(x, y + h / 2 - 1, w, 2);
}
function flapRow(ctx, str, x, y, cells, w, h, t, t0, seedBase, gap = 6) {
  for (let i = 0; i < cells; i++) flapCell(ctx, x + i * (w + gap), y, w, h, (str[i] ?? ' ').toUpperCase(), t, t0 + 0.35 + i * 0.07 + hash(i, seedBase) * 0.25, seedBase + i);
}
function s2(ctx, W, H, t) {
  ctx.fillStyle = '#0d0e13'; ctx.fillRect(0, 0, W, H);
  words(ctx, 'Every morning, you board one of two flights.', 120, 150, t, 0.0, { font: 'italic 54px Serif' });
  const bx = 120, cw = 58, ch = 84;
  label(ctx, 'TIME', bx, 268); label(ctx, 'DESTINATION', bx + 370, 268); label(ctx, 'STATUS', bx + 1160, 268);
  // row 1
  flapRow(ctx, '05:00', bx, 290, 5, cw, ch, t, 0.2, 10);
  flapRow(ctx, 'BETTER YOU', bx + 370, 290, 11, cw, ch, t, 0.35, 30);
  flapRow(ctx, 'BOARDING', bx + 1160, 290, 8, cw * 0.8, ch, t, 0.6, 60);
  // row 2
  flapRow(ctx, '07:30', bx, 410, 5, cw, ch, t, 0.9, 80);
  flapRow(ctx, 'SNOOZE', bx + 370, 410, 11, cw, ch, t, 1.0, 100);
  flapRow(ctx, 'CANCELLED', bx + 1160, 410, 9, cw * 0.8, ch, t, 1.3, 120);
  // status light
  if (t > 1.6) { const on = Math.floor(t * 2) % 2 === 0; ctx.fillStyle = on ? C.acc : '#5a2a18'; ctx.beginPath(); ctx.arc(bx + 1140, 332, 8, 0, 7); ctx.fill(); }
  if (t > 2.4) { ctx.strokeStyle = C.acc; ctx.lineWidth = 4; const k = eo((t - 2.4) / 0.4); ctx.beginPath(); ctx.moveTo(bx + 360, 452); ctx.lineTo(bx + 360 + 720 * k, 452); ctx.stroke(); }
  words(ctx, 'Only one *leaves* on time.', 120, 640, t, 2.6, { font: 'italic 54px Serif' });
  label(ctx, 'GATE 05   TERMINAL: YOUR BEDROOM   WEATHER: COLD', 120, H - 90);
}

// ---------- S3 chart: motivation vs discipline ----------
function s3(ctx, W, H, t) {
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H);
  grid(ctx, W, H, 60, 'rgba(0,0,0,0.035)');
  const ox = 220, oy = 860, aw = 1500, ah = 520;
  ctx.strokeStyle = '#9a9caa'; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(ox, oy - ah - 20); ctx.lineTo(ox, oy); ctx.lineTo(ox + aw + 20, oy); ctx.stroke();
  for (let i = 1; i <= 6; i++) { label(ctx, `wk ${i * 2}`, ox + i * aw / 6 - 18, oy + 32, '#8a8c99', 14); ctx.fillStyle = '#9a9caa'; ctx.fillRect(ox + i * aw / 6, oy, 1, 8); }
  label(ctx, 'effort', ox - 70, oy - ah, '#8a8c99', 14);
  const N = 240, mot = [], dis = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, x = ox + u * aw;
    const m = Math.exp(-Math.pow((u - 0.08) / 0.07, 2)) * 0.95 + 0.12 * Math.max(0, Math.sin(u * 40)) * Math.exp(-u * 3) + 0.05;
    mot.push([x, oy - m * ah]);
    dis.push([x, oy - (0.08 + 0.78 * Math.pow(u, 0.9) + 0.015 * Math.sin(u * 60)) * ah]);
  }
  const k = eio((t - 0.3) / 3.0);
  const hm = drawOn(ctx, mot, k, '#a2a4b2', 3);
  const hd = drawOn(ctx, dis, k, C.acc, 5);
  if (k > 0.02) { glowDot(ctx, hd[0], hd[1], 'rgba(255,106,43,0.55)'); ctx.fillStyle = '#a2a4b2'; ctx.beginPath(); ctx.arc(hm[0], hm[1], 5, 0, 7); ctx.fill(); }
  if (k > 0.25) label(ctx, 'motivation', mot[50][0] + 20, mot[20][1] - 10, '#8a8c99', 24);
  if (k > 0.98) label(ctx, 'discipline', hd[0] - 150, hd[1] - 28, C.acc, 26);
  ctx.fillStyle = '#16171d';
  words(ctx, '*Motivation* gets you started.', 120, 150, t, 0.1, { font: 'italic 60px Serif', color: '#16171d', acc: '#8a8c99' });
  words(ctx, '*Discipline* keeps you going.', 120, 230, t, 1.9, { font: 'italic 60px Serif', color: '#16171d' });
  label(ctx, 'fig. 1 — effort over time, n = you', W - 120, H - 70, '#8a8c99', 14, 'right');
}

// ---------- S4 system monitor: the 40% ----------
function s4(ctx, W, H, t) {
  ctx.fillStyle = '#12131a'; ctx.fillRect(0, 0, W, H);
  const px = 980, py = 120, pw = 820, ph = 840;
  ctx.fillStyle = '#181a23'; rr(ctx, px, py, pw, ph, 14); ctx.fill();
  ctx.strokeStyle = '#2a2d3b'; ctx.lineWidth = 1; rr(ctx, px, py, pw, ph, 14); ctx.stroke();
  label(ctx, 'monitor — brain.exe', px + 30, py + 42, '#9aa0b8', 16);
  const rows = [['body.legs', 0.62], ['body.lungs', 0.71], ['mind.willpower', 0.4], ['mind.excuses', 0.95]];
  rows.forEach(([n, v], i) => {
    const y = py + 110 + i * 70, k = eo((t - 0.3 - i * 0.15) / 0.8);
    label(ctx, n, px + 30, y + 6, '#c9cbd8', 21);
    ctx.fillStyle = '#232633'; ctx.fillRect(px + 250, y - 14, 470, 22);
    ctx.fillStyle = n === 'mind.excuses' ? C.acc : '#7f8cff'; ctx.fillRect(px + 250, y - 14, 470 * v * k, 22);
    label(ctx, `${Math.round(v * k * 100)}%`, px + 790, y + 6, '#c9cbd8', 18, 'right');
  });
  // capacity gauge
  const gx = px + 60, gy = py + 440, gw = 700, gh = 120;
  label(ctx, 'TOTAL CAPACITY', gx, gy - 24, '#9aa0b8', 16);
  ctx.strokeStyle = '#d8dae6'; ctx.lineWidth = 3; rr(ctx, gx, gy, gw, gh, 12); ctx.stroke();
  ctx.fillStyle = '#d8dae6'; ctx.fillRect(gx + gw + 6, gy + 35, 16, 50);
  const used = eio((t - 0.9) / 1.0) * 0.4;
  ctx.fillStyle = '#3b3f55'; ctx.fillRect(gx + 10, gy + 10, (gw - 20) * used, gh - 20);
  if (t > 2.0) { // reveal what's left
    const k = eo((t - 2.0) / 0.9);
    ctx.fillStyle = C.acc; ctx.fillRect(gx + 10 + (gw - 20) * 0.4, gy + 10, (gw - 20) * 0.6 * k, gh - 20);
    ctx.font = '600 56px Inter'; ctx.fillStyle = '#12131a'; ctx.textAlign = 'center';
    if (k > 0.6) ctx.fillText('60% LEFT', gx + 10 + (gw - 20) * 0.7, gy + 80); ctx.textAlign = 'left';
  }
  ctx.font = '600 30px Inter'; ctx.fillStyle = '#c9cbd8'; ctx.fillText('40%', gx + 10 + (gw - 20) * used - 66, gy + gh + 46);
  label(ctx, 'PID 40   STATE: "I\'m done."   ACTUAL STATE: warming up', px + 30, py + ph - 40, '#6c7088', 15);
  words(ctx, 'When your brain says', 120, 300, t, 0.1, { font: '500 52px Inter' });
  words(ctx, '"I\'m done."', 120, 400, t, 0.6, { font: '600 96px Inter' });
  words(ctx, "you've only used *40%.*", 120, 520, t, 2.0, { font: '500 52px Inter' });
}

// ---------- S5 consistency calendar ----------
function s5(ctx, W, H, t) {
  ctx.fillStyle = C.cream; ctx.fillRect(0, 0, W, H);
  const cols = 53, rows = 7, cs = 24, gap = 5, gx = (W - cols * (cs + gap)) / 2, gy = 420;
  const days = Math.floor(clamp((t - 0.4) / 3.2) * 365);
  for (let c = 0; c < cols; c++) for (let r = 0; r < rows; r++) {
    const d = c * 7 + r; if (d >= 365) continue;
    const x = gx + c * (cs + gap), y = gy + r * (cs + gap);
    let col = '#e3ddcf';
    if (d < days) { const lv = 0.35 + 0.65 * hash(d, 4) * Math.min(1, d / 120 + 0.3); col = `rgba(255,106,43,${lv.toFixed(2)})`; }
    if (d === days - 1) col = C.acc;
    ctx.fillStyle = col; rr(ctx, x, y, cs, cs, 5); ctx.fill();
  }
  ['Mon', 'Wed', 'Fri'].forEach((s, i) => label(ctx, s, gx - 56, gy + (1 + i * 2) * (cs + gap) + 17, '#9b9483', 14));
  ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov'].forEach((s, i) => label(ctx, s, gx + i * 9 * (cs + gap), gy - 18, '#9b9483', 14));
  ctx.font = '600 120px Inter'; ctx.fillStyle = '#1c1b18'; ctx.textAlign = 'right';
  ctx.fillText(`DAY ${String(Math.max(1, days)).padStart(3, '0')}`, W - 140, 340); ctx.textAlign = 'left';
  label(ctx, `${days} contributions in the last year   •   streak: ${days} days`, gx, gy + rows * (cs + gap) + 50, '#7b7466', 16);
  words(ctx, 'Not motivated.', 120, 210, t, 0.1, { font: 'italic 64px Serif', color: '#1c1b18' });
  words(ctx, 'Just *consistent.*', 120, 290, t, 1.4, { font: 'italic 64px Serif', color: '#1c1b18' });
}

// ---------- S6 nutrition label + end card ----------
function s6(ctx, W, H, t) {
  ctx.fillStyle = '#e7e7ea'; ctx.fillRect(0, 0, W, H);
  const lx = 1050, ly = 90, lw = 560;
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.12)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
  ctx.fillStyle = '#fff'; ctx.fillRect(lx, ly + 60, lw, 700); ctx.restore();
  ctx.strokeStyle = '#111'; ctx.lineWidth = 3; ctx.strokeRect(lx + 16, ly + 76, lw - 32, 668);
  const X = lx + 34, R = lx + lw - 34; let y = ly + 152;
  ctx.fillStyle = '#111'; ctx.font = '800 66px Inter'; ctx.fillText('Discipline Facts', X, y);
  y += 40; ctx.font = '400 24px Inter'; ctx.fillText('Servings per life: unlimited', X, y);
  y += 34; ctx.font = '600 26px Inter'; ctx.fillText('Serving size', X, y); ctx.textAlign = 'right'; ctx.fillText('1 day', R, y); ctx.textAlign = 'left';
  y += 18; ctx.fillRect(X, y, R - X, 16);
  y += 56; ctx.font = '800 44px Inter'; ctx.fillText('Excuses', X, y); ctx.textAlign = 'right'; ctx.fillText('0', R, y); ctx.textAlign = 'left';
  y += 16; ctx.fillRect(X, y, R - X, 8);
  y += 34; ctx.font = '600 20px Inter'; ctx.textAlign = 'right'; ctx.fillText('% Daily Value*', R, y); ctx.textAlign = 'left';
  const items = [['Comfort', '0g', '0%'], ['Snooze', '0g', '0%'], ['Hard choices', '12g', '100%'], ['Pain (temporary)', '30g', '100%'], ['Regret', '0g', '0%'], ['Self-respect', '∞', '∞']];
  items.forEach(([n, g, p], i) => {
    const k = eo((t - 0.4 - i * 0.22) / 0.35); if (k <= 0) return;
    y += 2; ctx.fillStyle = '#111'; ctx.fillRect(X, y, R - X, 1.5); y += 44;
    ctx.save(); ctx.globalAlpha = k;
    ctx.font = '700 28px Inter'; ctx.fillStyle = '#111'; ctx.fillText(n, X, y); ctx.font = '400 28px Inter'; ctx.fillText(' ' + g, X + ctx.measureText(n).width + 6, y);
    ctx.font = '700 28px Inter'; ctx.textAlign = 'right'; ctx.fillStyle = (p === '100%' || p === '∞') ? C.acc : '#111'; ctx.fillText(p, R, y); ctx.textAlign = 'left';
    ctx.restore();
  });
  y += 20; ctx.fillStyle = '#111'; ctx.fillRect(X, y, R - X, 12);
  ctx.font = '400 17px Inter'; ctx.fillText('*Daily value based on showing up every single day.', X, y + 42);
  words(ctx, 'Side effects may include:', 120, 360, t, 1.0, { font: 'italic 58px Serif', color: '#16171d' });
  words(ctx, 'a *better* you.', 120, 450, t, 1.8, { font: 'italic 86px Serif', color: '#16171d' });
  // end card
  if (t > 3.6) {
    const k = clamp((t - 3.6) / 0.12);
    ctx.fillStyle = `rgba(11,12,16,${k})`; ctx.fillRect(0, 0, W, H);
    if (k >= 1) { ctx.textAlign = 'left'; typed(ctx, 'start today.', W / 2 - 230, H / 2 + 20, t, 3.8, 14, { font: '500 64px Plex', color: C.text, keepCursor: true, cursorColor: C.acc }); }
  }
}

const SEQ = [[s1, 4.2], [s2, 4.4], [s3, 4.4], [s4, 4.4], [s5, 4.4], [s6, 6.0]];
function film(ctx, W, H, t) {
  let t0 = 0;
  for (const [f, d] of SEQ) { if (t < t0 + d) return f(ctx, W, H, t - t0); t0 += d; }
  return SEQ[SEQ.length - 1][0](ctx, W, H, t - t0 + SEQ[SEQ.length - 1][1]);
}
window.FILM_LEN = SEQ.reduce((s, x) => s + x[1], 0);
Object.assign(window.SCENES, { M1: s1, M2: s2, M3: s3, M4: s4, M5: s5, M6: s6, MF: film });
})();
