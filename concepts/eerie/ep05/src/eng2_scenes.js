// ---------- EP05 scenes: "If Your AI Job Interview Ever Asks Who Else Is In The Room" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const clockStr = s => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return [h, m, x].map(v => String(v).padStart(2, '0')).join(':'); };
const T300 = 3 * 3600;
// typed text: the first n characters by time
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));

// ---------- you, at the desk ----------
// o.look: eyes down (0 at the screen, 1 at your phone); o.turn: 0 facing the laptop .. 1 turned round to the room
function mePose(o = {}) {
  const tr = ease(clamp(o.turn || 0));
  return poseOf({ x: SEAT.x, z: SEAT.z, yaw: Math.PI + tr * 2.6, crouch: 1, lean: 0.08, look: o.look || 0, roll: o.roll || 0, L: [-0.17, 0.78, 0.42 - 0.2 * tr], R: [0.17, 0.78, 0.42 - 0.2 * tr], ...(o.pose || {}) });
}
const ME = { col: C.fig, top: '#d8d8dc', legs: '#6a6a70' };
const SHOULDER = () => { const j = skeleton(mePose()); return V3.add(j.sh.L, [0.01, 0.05, -0.03]); };
// where it stands behind you
const BEHIND = [0.12, 1.42];

// ---------- the room, as the laptop's camera sees it ----------
// o: room5 options + me {look, turn, hide}, thing {at, hand, sit, lean, red, alpha, step, fold}, standMe (you standing behind your chair), front()
function webScene(t, o = {}) {
  room5(t, o);
  const th = o.thing;
  if (th && !(th.front)) thing5(t, th);
  chair5();
  if (o.standMe) body3(poseOf({ x: -0.05, z: 1.45, yaw: Math.PI, look: 0.1, L: [-0.25, 0.85, 0.05], R: [0.25, 0.85, 0.05] }), ME);
  if (!(o.me && o.me.hide)) body3(mePose(o.me || {}), ME);
  if (th && th.front) thing5(t, th);
  if (th) thing5Hand(t, th);
  if (o.front) o.front();
}
// the camera's picture in a rect r {x,y,w}; o.z zoom on o.focus (a world point); o.camObj another camera
let LASTPV = null;
function preview(t, o = {}, r = PV) {
  const s = r.w / W;
  ctx.save(); ctx.translate(r.x, r.y); ctx.scale(s, s);
  ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip();
  rr(0, 0, W, H, 0, '#000');
  const cm = o.camObj || CAMS.web; setCam(cm);
  const z = o.z || 1, fp = o.focus ? (prj(o.focus) || [W / 2, H / 2]) : [W / 2, H / 2];
  LASTPV = { r, s, z, fx: fp[0], fy: fp[1], camObj: cm };
  ctx.save(); ctx.translate(fp[0], fp[1]); ctx.scale(z, z); ctx.translate(-fp[0], -fp[1]);
  if (!(o.off >= 1)) webScene(t, o);
  ctx.restore();
  // a cheap webcam at night: cold, grainy, dark at the edges; the screen's light on you
  ctx.save(); ctx.globalCompositeOperation = 'color'; ctx.globalAlpha = 0.45; ctx.fillStyle = '#76808e'; ctx.fillRect(0, 0, W, H); ctx.restore();
  if (grainC) { ctx.save(); ctx.globalAlpha = 0.12 + 0.4 * (o.noise || 0); ctx.drawImage(grainC[Math.floor(t * 24) % 4], 0, 0, W, H); ctx.restore(); }
  const vg = ctx.createRadialGradient(W / 2, H * 0.62, H * 0.25, W / 2, H / 2, H * 1.0); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.8)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  if (o.off > 0) { ctx.save(); ctx.globalAlpha = clamp(o.off); rr(0, 0, W, H, 0, '#050505'); ctx.restore(); }
  if (o.label !== false) { rr(30, H - 96, 150, 66, 12, 'rgba(0,0,0,0.6)'); text(o.label || 'You', 105, H - 50, `600 40px ${UI}`, '#f2f2f2'); }
  ctx.restore();
  rrS(r.x, r.y, r.w, r.w * H / W, 14 * Math.max(0.5, r.w / 670), '#3a3a3e', 3);
}
function pvPt(p) { const L = LASTPV; if (!L) return null; setCam(L.camObj); const q = prj(p); if (!q) return null;
  const x = L.fx + (q[0] - L.fx) * L.z, y = L.fy + (q[1] - L.fy) * L.z; return [L.r.x + x * L.s, L.r.y + y * L.s, q[3] * L.z * L.s]; }
// a label tied to something in the preview
function pvTag(t, t0, s, p, tx, ty, col = C.fig, size = 44) {
  if (t < t0) return; const q = pvPt(p); if (!q) return;
  if (tx === 'rel') { tx = q[0] + ty[0]; ty = q[1] + ty[1]; }
  const k = easeOut(prog(t, t0, 0.3)); ctx.save(); ctx.globalAlpha *= k; ctx.setLineDash([8, 8]); ln(q[0], q[1], lerp(q[0], tx, k), lerp(q[1], ty + 20, k), 3, col); ctx.setLineDash([]);
  circ(q[0], q[1], 9, col); ctx.restore(); pop(t, t0 + 0.1, tx, ty, () => tag(s, tx, ty + 10, col, size, 'center'));
}
// a face-tracking box round a head in the preview, with its label and eye-contact score
function faceBox(t, t0, p, label, col, sz = 0.2, score) {
  if (t < t0) return; const q = pvPt(p); if (!q) return; const k = easeOut(prog(t, t0, 0.25)), h = sz * q[2] * lerp(1.6, 1, k);
  ctx.save(); ctx.globalAlpha *= k; if (col === C.red) redGlow(14);
  const c = 0.28 * h; ctx.lineWidth = 4; ctx.strokeStyle = col; ctx.beginPath();
  for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const x = q[0] + sx * h / 2, y = q[1] + sy * h / 2; ctx.moveTo(x, y - sy * c); ctx.lineTo(x, y); ctx.lineTo(x - sx * c, y); }
  ctx.stroke(); noGlow();
  const lab = score != null ? `${label}  ${Math.round(score)}%` : label; ctx.font = `700 22px ${UI}`; const w = ctx.measureText(lab).width + 20;
  rr(q[0] - h / 2, q[1] - h / 2 - 36, w, 32, 6, col); text(lab, q[0] - h / 2 + 10, q[1] - h / 2 - 13, `700 22px ${UI}`, col === C.red ? '#fff' : '#000', 'left');
  ctx.restore();
}

// ---------- the interview app on the laptop ----------
const PV = { x: 1190, y: 104, w: 670 };                       // the camera preview, top right
const AV = { x: 60, y: 104, w: 1100, h: 690 };                 // the interviewer's panel
// the interviewer: a calm grey face, two eyes, no mouth, just a line that moves when it speaks. o.talk 0..1, o.red, o.look [dx,dy] its eyes
function avatar(t, cx, cy, s, o = {}) {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  const g = ctx.createRadialGradient(-40, -80, 20, 0, 0, 260); g.addColorStop(0, '#b4b4ba'); g.addColorStop(1, '#5a5a60');
  glow('rgba(255,255,255,0.15)', 30); ctx.beginPath(); ctx.ellipse(0, 0, 165, 215, 0, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill(); noGlow();
  ctx.beginPath(); ctx.moveTo(-70, 200); ctx.quadraticCurveTo(0, 240, 70, 200); ctx.lineTo(90, 330); ctx.lineTo(-90, 330); ctx.closePath(); ctx.fillStyle = '#4a4a50'; ctx.fill();   // the neck
  const [lx, ly] = o.look || [0, 0];
  for (const sg of [-1, 1]) { ctx.save(); ctx.translate(sg * 62, -30); ctx.beginPath(); ctx.ellipse(0, 0, 40, o.blink ? 3 : 24, 0, 0, Math.PI * 2); ctx.fillStyle = '#ececee'; ctx.fill();
    if (!o.blink) { ctx.save(); ctx.clip(); if (o.red) redGlow(20); circ(lx * 16, ly * 10, 16, o.red ? C.red : '#141416'); noGlow(); circ(lx * 16 - 5, ly * 10 - 5, 4, 'rgba(255,255,255,0.8)'); ctx.restore(); } ctx.restore(); }
  // the line
  const amp = o.talk || 0; ctx.beginPath(); for (let i = 0; i <= 40; i++) { const x = -80 + i * 4, u = i / 40, y = 95 + Math.sin(i * 0.9 + t * 30) * Math.sin(u * Math.PI) * 16 * amp * (0.6 + 0.4 * Math.sin(t * 11 + i)); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.lineWidth = 4; ctx.strokeStyle = o.red ? C.red : '#2a2a2e'; ctx.lineCap = 'round'; ctx.stroke();
  ctx.restore();
}
// is the interviewer speaking now: during quoted lines, or as given
const talking = (t, spans) => spans.some(([a, b]) => t >= a && t < b) ? 0.6 + 0.4 * Math.abs(Math.sin(t * 9)) : 0;
// the whole app. o: q {n, text, t0}, pv (preview options or null), talk, red, warn {text, t0}, score [{label, v, col}], answer {text, t0}, time
function app(t, o = {}) {
  rr(0, 0, W, H, 0, '#0b0b0d');
  // top bar
  rr(0, 0, W, 76, 0, '#111114'); circS(62, 38, 15, '#cfcfd4', 4); circ(62, 38, 5, '#cfcfd4');
  text('AI INTERVIEW', 92, 50, `700 30px ${UI}`, '#e8e8ec', 'left');
  if (o.q) text(`Question ${o.q.n} of 5`, 330, 50, `500 26px ${UI}`, '#8a8a90', 'left');
  if (Math.floor(t * 1.6) % 2 === 0) { ctx.save(); redGlow(10); circ(W - 330, 38, 10, C.red); ctx.restore(); }
  text('REC', W - 310, 49, `700 26px ${UI}`, '#e8e8ec', 'left'); text(clockStr(o.time ?? T300), W - 60, 49, `600 30px Plex`, '#e8e8ec', 'right');
  // the interviewer
  rr(AV.x, AV.y, AV.w, AV.h, 18, '#141417');
  ctx.save(); ctx.beginPath(); ctx.roundRect(AV.x, AV.y, AV.w, AV.h, 18); ctx.clip();
  if (o.avatarFn) o.avatarFn(); else avatar(t, AV.x + AV.w / 2, AV.y + AV.h / 2 - 20, 1, { talk: o.talk || 0, red: o.red, look: o.look, blink: o.blink });
  ctx.restore();
  rr(AV.x + 24, AV.y + AV.h - 70, 220, 48, 10, 'rgba(0,0,0,0.5)'); text('Interviewer', AV.x + 44, AV.y + AV.h - 36, `600 26px ${UI}`, '#d8d8dc', 'left');
  // the question
  rr(AV.x, 820, AV.w, 200, 18, '#141417');
  if (o.q) { text(`QUESTION ${o.q.n}`, AV.x + 36, 870, `700 22px ${UI}`, '#7a7a80', 'left');
    const qs = o.q.t0 != null ? typed(o.q.text, t, o.q.t0, 40) : o.q.text; wrapText(qs, AV.x + 36, 930, AV.w - 72, 46, `700 42px ${UI}`, o.q.col || '#f2f2f2'); }
  // the preview
  if (o.pv !== null) preview(t, o.pv || {}, PV);
  // right column: your answer, or the scores
  rr(PV.x, 510, PV.w, 510, 18, '#141417');
  if (o.score) { text('LIVE ASSESSMENT', PV.x + 30, 560, `700 22px ${UI}`, '#7a7a80', 'left');
    o.score.forEach((s, i) => { const y = 610 + i * 110; text(s.label, PV.x + 30, y, `700 28px ${UI}`, s.col || '#e8e8ec', 'left'); text(Math.round(s.v) + '%', PV.x + PV.w - 30, y, `700 28px Plex`, s.col || '#e8e8ec', 'right');
      rr(PV.x + 30, y + 22, PV.w - 60, 14, 7, '#26262a'); ctx.save(); if (s.col === C.red) redGlow(12); rr(PV.x + 30, y + 22, (PV.w - 60) * clamp(s.v / 100), 14, 7, s.col || '#cfcfd4'); ctx.restore(); }); }
  else { text('YOUR ANSWER', PV.x + 30, 560, `700 22px ${UI}`, '#7a7a80', 'left');
    if (o.answer) wrapText(o.answer.t0 != null ? typed(o.answer.text, t, o.answer.t0, o.answer.cps || 22) : o.answer.text, PV.x + 30, 620, PV.w - 60, 44, `500 34px ${UI}`, o.answer.col || '#d8d8dc');
    // your microphone level
    const lv = o.mic || 0; for (let i = 0; i < 18; i++) rr(PV.x + 30 + i * 34, 960, 22, 26, 4, i < lv * 18 ? '#cfcfd4' : '#26262a'); }
  if (o.warn && t >= o.warn.t0) { const k = easeOut(prog(t, o.warn.t0, 0.3)); ctx.save(); ctx.globalAlpha *= k; ctx.translate(0, -20 * (1 - k));
    ctx.font = `700 34px ${UI}`; const w = ctx.measureText(o.warn.text).width + 100, x = AV.x + AV.w / 2 - w / 2;
    redGlow(16); rr(x, AV.y + 30, w, 70, 14, o.warn.col || C.red); noGlow(); text('!', x + 40, AV.y + 78, `900 38px ${UI}`, '#fff'); text(o.warn.text, x + 70, AV.y + 77, `700 34px ${UI}`, '#fff', 'left'); ctx.restore(); }
}
function wrapText(s, x, y, maxW, lh, font, col) {
  ctx.font = font; const ws = s.split(' '); let line = '', yy = y;
  for (const w of ws) { const tl = line ? line + ' ' + w : w; if (ctx.measureText(tl).width > maxW && line) { text(line, x, yy, font, col, 'left'); line = w; yy += lh; } else line = tl; }
  if (line) text(line, x, yy, font, col, 'left'); return yy;
}
// the screen as a laptop on the desk, for the shots that pull back from it
function laptopFrame(t, fn, o = {}) {
  ctx.save(); rr(140, 40, 1640, 960, 30, '#1a1a1d'); rrS(140, 40, 1640, 960, 30, '#3a3a3e', 3); circ(960, 64, 6, '#050505');
  ctx.save(); ctx.beginPath(); ctx.rect(180, 90, 1560, 878); ctx.clip(); ctx.translate(180, 90); ctx.scale(1560 / W, 878 / H); fn(); ctx.restore();
  pth('M60,1000 L1860,1000 L1920,1080 L0,1080 Z', '#232326'); ln(60, 1000, 1860, 1000, 3, '#3a3a3e'); ctx.restore();
}

// ---------- email ----------
function mailApp(t, o = {}) {
  rr(0, 0, W, H, 0, '#0e0e10'); rr(0, 0, W, 76, 0, '#141417'); text('Inbox', 60, 50, `700 32px ${UI}`, '#e8e8ec', 'left');
  rr(0, 76, 560, H - 76, 0, '#111114');
  (o.list || []).forEach(([from, subj, time, hot, at], i) => { if (at != null && t < at) return; const y = 100 + i * 120, k = at != null ? easeOut(prog(t, at, 0.35)) : 1;
    ctx.save(); ctx.globalAlpha *= k; rr(16, y, 528, 104, 12, i === (o.sel ?? 0) ? '#1d1d22' : '#141417'); if (hot) { ctx.save(); redGlow(8); circ(40, y + 34, 8, C.red); ctx.restore(); }
    text(from, 60, y + 42, `700 26px ${UI}`, '#f2f2f2', 'left'); text(time, 520, y + 42, `500 22px ${UI}`, '#8a8a90', 'right'); text(subj, 60, y + 80, `500 23px ${UI}`, hot ? '#ff6a6a' : '#9a9aa0', 'left'); ctx.restore(); });
  if (o.body) { ctx.save(); ctx.translate(620, 120); o.body(); ctx.restore(); }
}
