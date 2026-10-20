// ---------- EP02 props: the phone, the chat, the photo from the ceiling, the thing in the corner ----------
const UI = 'I';                              // Inter, the phone's interface font
const CEIL = 110, WALL = 250, BX = 330, TS = 1.35;   // BX: the bed's left foot; TS: size of the thing in the corner                  // side-view room: ceiling line and the left wall; the corner is where they meet
const CORNER = { x: WALL, y: CEIL };
const NS = { x: BX + 650, w: 130, h: 150 };       // nightstand (no clock: the phone tells the time)
const PH_NS = { x: NS.x + NS.w / 2, y: FY - NS.h };   // the phone lying on the nightstand
const HEAD_S = { x: BX + 112 * 1.05, y: FY - 238 * 1.05 };   // your head on the pillow, asleep
const HEAD_W = { x: BX + 150 * 1.05, y: FY - 298 * 1.05 };   // your head propped up, awake

// side-view bedroom: walls, window, nightstand, picture frame; o.sun for the morning
function room2(t, o = {}) {
  ln(WALL, CEIL, W + 40, CEIL, 4, C.dim); ln(WALL, CEIL, WALL, FY, 4, C.dim); ln(WALL, FY, W + 40, FY, 4, C.dim);
  // window with the moon (or the sun), right of the nightstand: the corner above the bed stays empty
  ctx.save(); ctx.translate(780, 0);
  rrS(380, 220, 220, 230, 6, C.mid, 6); ln(490, 226, 490, 444, 4, C.mid); ln(386, 335, 594, 335, 4, C.mid);
  if (o.sun) { ctx.save(); glow('rgba(255,255,255,0.6)', 30); circ(450, 280, 26, C.fig); ctx.restore();
    ctx.save(); ctx.globalAlpha *= 0.12; pth('M386,226 L594,226 L460,' + FY + ' L-90,' + FY + ' Z', '#fff'); ctx.restore(); }
  else { ctx.save(); glow('rgba(255,255,255,0.5)', 24); circ(550, 275, 22, C.fig); noGlow(); circ(560, 268, 20, '#000'); ctx.restore(); }
  pth('M366,212 C390,290 380,390 350,460 L366,460 Z', C.dim); pth('M614,212 C590,290 600,390 630,460 L614,460 Z', C.dim); rr(350, 206, 280, 10, 3, C.mid);
  ctx.restore();
  // nightstand
  rr(NS.x, FY - NS.h, NS.w, NS.h, 6, '#262626'); rrS(NS.x, FY - NS.h, NS.w, NS.h, 6, C.mid, 3); ln(NS.x + 10, FY - 95, NS.x + NS.w - 10, FY - 95, 3, C.mid); circ(NS.x + NS.w / 2, FY - 120, 5, C.mid);
  // picture frame and the door on the far right
  rrS(1010, 290, 90, 110, 4, C.dim, 5); pthS('M1022,386 L1050,340 L1070,366 L1086,346 L1092,386', C.dim, 3);
  rrS(1580, FY - 520, 230, 520, 4, C.dim, 5); circ(1610, FY - 250, 8, C.dim);
  ln(WALL, FY - 10, 1570, FY - 10, 3, C.dim);
}
// the phone lying flat on the nightstand, seen from the side; lit 0..1 throws a cone of light at the ceiling
function phoneFlat(lit = 0, buzz = 0) {
  const x = PH_NS.x + Math.sin(buzz * 90) * 3 * (buzz > 0 ? 1 : 0), y = PH_NS.y;
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit;
    const g = ctx.createRadialGradient(x, y, 4, x, y - 260, 520); g.addColorStop(0, 'rgba(225,235,255,0.42)'); g.addColorStop(1, 'rgba(225,235,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x - 50, y - 4); ctx.lineTo(x - 520, CEIL); ctx.lineTo(x + 520, CEIL); ctx.lineTo(x + 50, y - 4); ctx.closePath(); ctx.fill();
    glow('rgba(220,232,255,0.95)', 30); rr(x - 46, y - 9, 92, 4, 2, '#eaf0ff'); ctx.restore(); }
  rr(x - 50, y - 7, 100, 8, 3, '#0b0b0b'); rrS(x - 50, y - 7, 100, 8, 3, C.mid, 2);
}
// your arm holding the phone up in front of your face in bed (bed must be 'woke'); lit = screen light on your face
function phoneInHand(t, lit = 1, o = {}) {
  const hx = HEAD_W.x + 150, hy = HEAD_W.y + 30;
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; const g = ctx.createRadialGradient(hx - 20, hy, 10, hx - 60, hy, 260);
    g.addColorStop(0, 'rgba(225,235,255,0.32)'); g.addColorStop(1, 'rgba(225,235,255,0)'); ctx.fillStyle = g; ctx.fillRect(hx - 340, hy - 260, 520, 480); ctx.restore(); }
  glow('rgba(255,255,255,0.22)', 14);
  poly([[HEAD_W.x + 40, HEAD_W.y + 120], [HEAD_W.x + 110, HEAD_W.y + 96], [hx + 6, hy + 16]], 20, C.fig); circ(hx + 4, hy + 14, 12, C.fig);
  noGlow();
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(-0.25);
  rr(-8, -44, 16, 88, 4, '#0b0b0b'); rrS(-8, -44, 16, 88, 4, C.mid, 2);
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; glow('rgba(220,232,255,0.9)', 22); rr(-9, -40, 3, 80, 1, '#eaf0ff'); ctx.restore(); }
  ctx.restore();
}

// ---------- the thing in the corner ----------
// It clings in the corner where the ceiling meets the wall: arms spread along the ceiling, legs down the wall, body hanging towards the bed.
// Its face is a blank screen with one lens. o.vis 0..1, o.lit how much light reaches it, o.face 'lens'|'dots'|'off'|'blank', o.red 0..1, o.reach 0..1 (an arm drops toward the bed)
function cornerThing(t, o = {}) {
  const vis = o.vis ?? 1; if (vis <= 0) return;
  const lit = o.lit ?? 0.3, br = Math.sin(t * 2.1) * (o.breath ?? 1);
  const body = o.body || `rgb(${Math.round(lerp(26, 120, lit))},${Math.round(lerp(26, 120, lit))},${Math.round(lerp(28, 124, lit))})`;
  const edge = o.edge || `rgba(255,255,255,${0.1 + 0.32 * lit})`;
  ctx.save(); ctx.globalAlpha *= vis; ctx.translate(CORNER.x, CORNER.y);
  const s = o.s ?? TS; ctx.scale(s, s);
  // a limb: shoulder -> elbow -> hand, with long fingers splayed on the surface
  const limb = (pts, w, fingers, fdir) => {
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (const p of pts.slice(1)) ctx.lineTo(p[0], p[1]);
    ctx.strokeStyle = edge; ctx.lineWidth = w + 4; ctx.stroke(); ctx.strokeStyle = body; ctx.lineWidth = w; ctx.stroke();
    const [hx, hy] = pts[pts.length - 1];
    for (let i = 0; i < 4; i++) { const a = fdir + (i - 1.5) * 0.32, L = 46 + (i === 1 || i === 2 ? 14 : 0);
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.quadraticCurveTo(hx + Math.cos(a) * L * 0.6, hy + Math.sin(a) * L * 0.6 + 8, hx + Math.cos(a) * L, hy + Math.sin(a) * L);
      ctx.strokeStyle = edge; ctx.lineWidth = 9; ctx.stroke(); ctx.strokeStyle = body; ctx.lineWidth = 5.5; ctx.stroke(); }
  };
  const sh = { x: 120 + br * 2, y: 70 + br * 3 };      // shoulders, a little out of the corner
  const hip = { x: 54, y: 190 };
  // legs down the wall
  limb([[hip.x, hip.y], [20, 290], [8, 400]], 16, 4, Math.PI / 2 + 0.2);
  limb([[hip.x + 18, hip.y + 10], [70, 330], [10, 470]], 16, 4, Math.PI / 2 + 0.1);
  // arms along the ceiling; o.reach lets the near arm unfold down toward the bed
  limb([[sh.x, sh.y], [250, 30], [380, 8]], 15, 4, 0.1);
  const rk = ease(o.reach ?? 0);
  limb([[sh.x + 10, sh.y + 16], [lerp(300, 260, rk), lerp(60, 260, rk)], [lerp(470, 300, rk), lerp(10, 460, rk)]], 15, 4, lerp(0.05, 1.2, rk));
  // torso: a long hunched shape from the hips to the shoulders
  ctx.beginPath(); ctx.moveTo(hip.x - 22, hip.y + 10); ctx.quadraticCurveTo(10, 90, sh.x - 30, sh.y - 34); ctx.quadraticCurveTo(sh.x + 40, sh.y - 10, sh.x + 22, sh.y + 30);
  ctx.quadraticCurveTo(110, 170, hip.x + 30, hip.y + 26); ctx.closePath();
  ctx.fillStyle = body; ctx.fill(); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke();
  // ribs showing through
  ctx.save(); ctx.globalAlpha *= 0.5 * lit; for (let i = 0; i < 4; i++) pthS(`M${66 + i * 10},${150 - i * 22} q16,-6 30,4`, '#000', 3); ctx.restore();
  // neck and the screen face, tilted down at the bed
  ln(sh.x + 4, sh.y + 4, sh.x + 52, sh.y + 52, 18, body);
  ctx.save(); ctx.translate(sh.x + 74, sh.y + 78); ctx.rotate(-0.62);
  const face = o.face || 'lens', red = o.red ?? 0;
  rr(-46, -70, 92, 140, 18, '#0a0a0a'); rrS(-46, -70, 92, 140, 18, edge, 3);
  if (face !== 'off') {
    const on = face === 'blank' ? 0.55 : 0.85;
    ctx.save(); glow(red > 0.3 ? 'rgba(255,43,43,0.7)' : 'rgba(220,232,255,0.6)', 24); rr(-40, -64, 80, 128, 14, o.faceFill || `rgba(${Math.round(lerp(210, 120, red))},${Math.round(lerp(222, 30, red))},${Math.round(lerp(240, 30, red))},${on * (0.35 + 0.15 * lit)})`); ctx.restore();
    if (face === 'lens') { circ(0, -38, 11, '#050505'); ctx.save(); if (red > 0) redGlow(16 * red); circ(0, -38, 5, red > 0 ? `rgba(255,43,43,${0.4 + 0.6 * red})` : '#6a6a6a'); ctx.restore(); }
    if (face === 'dots') for (let i = 0; i < 3; i++) circ(-20 + i * 20, 4 + Math.sin(t * 9 - i * 0.9) * 5, 6.5, '#f0f0f0');
  } else if (o.offLine) {   // the last line of light as the face switches off
    ctx.save(); glow('rgba(255,255,255,0.9)', 18); rr(-40 * o.offLine, -1.5, 80 * o.offLine, 3, 1, '#fff'); ctx.restore();
  }
  ctx.restore();
  ctx.restore();
}

// ---------- the phone, face on ----------
// phone body centred at (x,y), scale s; fn draws the screen in screen space (368 x 808, origin top-left), clipped to the glass
const SW = 368, SH = 808;
function phone(x, y, s, fn, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.rot || 0);
  const bright = o.bright ?? 1;
  if (bright > 0) { ctx.save(); ctx.globalAlpha *= 0.55 * bright; glow('rgba(215,228,255,0.9)', 90); rr(-190, -414, 380, 828, 50, '#0d0d0d'); ctx.restore(); }
  rr(-200, -424, 400, 848, 58, '#111'); rrS(-200, -424, 400, 848, 58, '#5e5e5e', 5); rrS(-193, -417, 386, 834, 52, '#262626', 3);
  rr(-204, -280, 6, 70, 3, '#3a3a3a'); rr(198, -300, 6, 110, 3, '#3a3a3a');    // buttons
  ctx.save(); ctx.beginPath(); ctx.roundRect(-SW / 2, -SH / 2, SW, SH, 44); ctx.clip();
  ctx.translate(-SW / 2, -SH / 2); rr(0, 0, SW, SH, 0, '#000'); fn();
  if (bright < 1) { ctx.globalAlpha = 1 - bright; rr(0, 0, SW, SH, 0, '#000'); ctx.globalAlpha = 1; }
  ctx.restore();
  rr(-58, -SH / 2 + 14, 116, 34, 17, '#000');    // the camera pill
  circ(30, -SH / 2 + 31, 7, '#151515');
  ctx.restore();
}
// screen-space helpers (inside phone())
function statusBar(time = '3:00', dark = true) {
  const c = dark ? '#f2f2f2' : '#111';
  text(time, 46, 40, `600 19px ${UI}`, c, 'left');
  for (let i = 0; i < 4; i++) rr(276 + i * 8, 34 - i * 3, 5, 6 + i * 3, 1, c);
  rrS(312, 26, 32, 15, 4, c, 2); rr(315, 29, 22, 9, 2, c); rr(345, 30, 2, 7, 1, c);
}
// the assistant's avatar: a plain ring with a dot (no real logo)
function aiAvatar(x, y, r, red = 0) {
  ctx.save(); glow(red > 0 ? 'rgba(255,43,43,0.8)' : 'rgba(255,255,255,0.5)', 10);
  circS(x, y, r, red > 0 ? C.red : '#e8e8e8', r * 0.16); circ(x, y, r * 0.34, red > 0 ? C.red : '#e8e8e8'); ctx.restore();
}
function wrapLines(str, maxW, font) {
  ctx.font = font; const out = []; let cur = '';
  for (const w of str.split(' ')) { const tr = cur ? cur + ' ' + w : w; if (ctx.measureText(tr).width > maxW && cur) { out.push(cur); cur = w; } else cur = tr; }
  if (cur) out.push(cur); return out;
}
// one chat bubble; returns its height. m: {me, text, photo (fn w,h), red, chars (0..1 typed out)}
function bubbleH(m) {
  if (m.photo) return (m.ph || 300) + 16;
  if (m.dots) return 54;
  const ls = wrapLines(m.text, 230, `500 23px ${UI}`); return ls.length * 31 + 26;
}
function chatBubble(m, y, t) {
  const font = `500 23px ${UI}`;
  if (m.photo) { const w = m.pw || 250, h = m.ph || 300, x = m.me ? SW - 16 - w : 64;
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 20); ctx.clip(); m.photo(x, y, w, h); ctx.restore(); rrS(x, y, w, h, 20, '#333', 2); return h + 16; }
  if (m.dots) { rr(64, y, 92, 44, 22, '#262626'); for (let i = 0; i < 3; i++) circ(90 + i * 20, y + 22 + Math.sin(t * 9 - i * 0.9) * 4, 6, '#bdbdbd'); return 54; }
  let str = m.text; if (m.chars != null && m.chars < 1) str = str.slice(0, Math.floor(str.length * clamp(m.chars)));
  const lsFull = wrapLines(m.text, 230, font), ls = wrapLines(str || ' ', 230, font);
  ctx.font = font; const w = Math.max(...lsFull.map(l => ctx.measureText(l).width)) + 34, h = lsFull.length * 31 + 16;
  const x = m.me ? SW - 16 - w : 64;
  rr(x, y, w, h, 20, m.me ? '#ececec' : (m.red ? '#3a0d0d' : '#262626'));
  ls.forEach((l, i) => text(l, x + 17, y + 32 + i * 31, font, m.me ? '#111' : (m.red ? '#ff5a5a' : '#f2f2f2'), 'left'));
  return h + 10;
}
// a full chat screen. msgs: [{me, text|photo|dots, at (time it appears), status}], o.input (text being typed), o.header
function chatScreen(t, msgs, o = {}) {
  rr(0, 0, SW, SH, 0, '#0a0a0a'); statusBar(o.time || '3:00');
  // header
  ln(0, 118, SW, 118, 1.5, '#222');
  pthS('M30,72 l-12,12 l12,12', '#bdbdbd', 3.5);
  aiAvatar(78, 84, 20, o.redAvatar || 0); text('Assistant', 110, 80, `600 21px ${UI}`, '#f2f2f2', 'left');
  text(o.sub || 'online', 110, 104, `400 15px ${UI}`, o.subRed ? '#ff5a5a' : '#8a8a8a', 'left');
  // messages stack from the top; when they overflow, the list scrolls up
  const shown = msgs.filter(m => t >= (m.at ?? -1));
  let total = 0; for (const m of shown) total += bubbleH(m) + 10;
  const top = 140, bottom = SH - 110, off = Math.max(0, total - (bottom - top));
  ctx.save(); ctx.beginPath(); ctx.rect(0, 120, SW, bottom - 120 + 6); ctx.clip();
  let y = top - off;
  for (const m of shown) {
    const k = easeOut(prog(t, m.at ?? -1, 0.25));
    ctx.save(); ctx.globalAlpha *= k; ctx.translate(0, 14 * (1 - k));
    if (!m.me && !m.dots && m.avatar !== false) aiAvatar(38, y + 22, 13, m.red ? 1 : 0);
    const h = chatBubble(m, y, t);
    if (m.status) text(m.status, SW - 20, y + h + 8, `500 14px ${UI}`, m.statusRed ? '#ff5a5a' : '#8a8a8a', 'right');
    ctx.restore();
    y += h + (m.status ? 26 : 0) + 10;
  }
  ctx.restore();
  // input bar
  rr(16, SH - 92, SW - 90, 52, 26, '#1d1d1d');
  const inp = o.input || '';
  if (inp) { text(inp, 38, SH - 58, `500 21px ${UI}`, '#f2f2f2', 'left'); ctx.font = `500 21px ${UI}`;
    if ((t * 2) % 1 < 0.6) rr(40 + ctx.measureText(inp).width, SH - 78, 2.5, 26, 1, '#ececec'); }
  else text('Message', 38, SH - 58, `400 21px ${UI}`, '#666', 'left');
  circ(SW - 44, SH - 66, 25, inp ? '#ececec' : '#2a2a2a'); pthS(`M${SW - 44},${SH - 54} l0,-24 m-10,10 l10,-10 l10,10`, inp ? '#111' : '#666', 3.5);
  rr(SW / 2 - 66, SH - 14, 132, 5, 3, '#555');
}
function lockScreen(t, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, SH); g.addColorStop(0, '#15161a'); g.addColorStop(1, '#050506'); ctx.fillStyle = g; ctx.fillRect(0, 0, SW, SH);
  statusBar('', true);
  text(o.date || 'Wednesday, October 21', SW / 2, 136, `600 21px ${UI}`, '#d8d8d8');
  text(o.time || '3:00', SW / 2, 260, `600 112px ${UI}`, o.timeRed ? '#ff3b3b' : '#f2f2f2');
  for (const n of o.notes || []) {
    if (t < n.at) continue; const k = easeOut(prog(t, n.at, 0.35)), y = (n.y ?? 330) - 30 * (1 - k);
    const nh = 96 + 25 * ((Array.isArray(n.text) ? n.text.length : 1) - 1);
    ctx.save(); ctx.globalAlpha *= k; rr(14, y, SW - 28, nh, 22, 'rgba(70,70,76,0.75)');
    rr(30, y + 18, 40, 40, 10, '#0a0a0a'); aiAvatar(50, y + 38, 12, n.red ? 1 : 0);
    text('Assistant', 84, y + 34, `600 18px ${UI}`, '#f2f2f2', 'left'); text(n.when || 'now', SW - 34, y + 34, `400 15px ${UI}`, '#a8a8a8', 'right');
    (Array.isArray(n.text) ? n.text : [n.text]).forEach((l, i) => text(l, 84, y + 64 + i * 25, `400 19px ${UI}`, n.red ? '#ff6a6a' : '#e8e8e8', 'left'));
    ctx.restore();
  }
  rr(SW / 2 - 66, SH - 14, 132, 5, 3, '#888');
}
// a thumb reaching in from the bottom right of the screen; tip at (x,y) in screen space
function thumb(x, y, press = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.42); ctx.scale(1 - press * 0.05, 1 - press * 0.05);
  glow('rgba(0,0,0,0.6)', 22); rr(-38, -6, 76, 420, 38, '#d9d9d9'); noGlow();
  rr(-26, 6, 52, 64, 22, '#efefef'); rrS(-26, 6, 52, 64, 22, '#b0b0b0', 2);   // nail
  pthS('M-34,150 q34,14 68,0', '#a8a8a8', 3);
  ctx.restore();
}

// ---------- the photo it took: you asleep, from the corner of the ceiling, lit by a flash ----------
// draws into the rect (x,y,w,h). o.zoom 1..: how close it was taken; o.n seeds the small differences between nights; o.stamp: timestamp text
function ceilPhoto(x, y, w, h, o = {}) {
  const z = o.zoom ?? 1, n = o.n ?? 0;
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rr(x, y, w, h, 0, '#0c0c0c');
  // the scene is drawn in a 1000x1000 world seen from above, rotated as if from the corner
  const head = { x: 330, y: 300 };
  ctx.translate(x + w / 2, y + h / 2); const sc = Math.min(w, h) / 1000 * z; ctx.scale(sc, sc);
  ctx.rotate(-0.38 + hash(n + 1) * 0.06);
  const fz = lerp(0, 1, clamp((z - 1) / 3));
  ctx.translate(-lerp(500, head.x, fz), -lerp(520, head.y, fz));
  // floor boards
  for (let i = -8; i < 20; i++) ln(-400 + i * 90, -400, -400 + i * 90, 1500, 2, '#262626');
  // nightstand with the phone glowing on it
  rr(730, 120, 170, 170, 8, '#3a3a3a'); rrS(730, 120, 170, 170, 8, '#5a5a5a', 3);
  ctx.save(); glow('rgba(220,232,255,0.9)', 26); rr(790, 160, 52, 96, 8, '#dfe8ff'); ctx.restore();
  // bed from above: frame, mattress, pillow, you, the blanket
  rr(160, 120, 540, 880, 18, '#8c8c8c'); rr(176, 136, 508, 848, 14, '#bdbdbd');
  rr(210, 170, 250, 140, 40, '#e9e9e9');                                    // pillow
  pth('M190,360 C260,330 420,340 640,350 L670,970 L190,970 Z', '#f4f4f4');   // blanket
  ctx.save(); ctx.globalAlpha = 0.18; pthS('M240,500 q120,30 240,0 M230,680 q160,40 380,-10 M300,850 q120,20 300,-6', '#000', 6); ctx.restore();
  // you, from above: the back of your head and hair, shoulder, one arm out over the blanket
  ell(head.x, head.y, 62, 74, -0.3, '#d8d8d8');                                // face side
  pth(`M${head.x - 60},${head.y - 30} C${head.x - 40},${head.y - 96} ${head.x + 60},${head.y - 90} ${head.x + 66},${head.y - 4} C${head.x + 40},${head.y - 30} ${head.x - 20},${head.y - 34} ${head.x - 60},${head.y - 30} Z`, '#2a2a2a');   // hair
  pth('M260,370 C300,340 420,350 450,400 L450,420 L250,420 Z', '#e6e6e6');      // shoulder under the blanket edge
  if (o.awake) {
    // you, awake: both arms up, holding the phone over your chest, its light on your face
    ctx.save(); const gl = ctx.createRadialGradient(head.x + 20, head.y + 60, 10, head.x + 20, head.y + 60, 260);
    gl.addColorStop(0, 'rgba(215,228,255,0.55)'); gl.addColorStop(1, 'rgba(215,228,255,0)'); ctx.fillStyle = gl; ctx.fillRect(head.x - 260, head.y - 200, 520, 520); ctx.restore();
    ell(head.x - 14, head.y + 10, 11, 8, -0.3, '#f4f4f4'); circ(head.x - 10, head.y + 11, 5, '#111');   // open eye, looking at the screen
    ctx.lineCap = 'round';
    // sleeves out of the blanket, forearms up to the phone (outlined so they read against the sheet)
    ctx.lineJoin = 'round';
    for (const pts of [[[255, 405], [205, 560], [305, 540]], [[445, 415], [505, 575], [435, 520]]]) for (const [w, c] of [[50, '#8a8a8a'], [42, '#d6d6d6']]) {
      ctx.beginPath(); ctx.moveTo(...pts[0]); ctx.lineTo(...pts[1]); ctx.lineTo(...pts[2]); ctx.strokeStyle = c; ctx.lineWidth = w; ctx.stroke(); }
    ctx.save(); ctx.translate(370, 520); ctx.rotate(-0.25);
    glow('rgba(215,228,255,0.7)', 30); rr(-62, -95, 124, 190, 18, '#161616'); noGlow();
    rrS(-62, -95, 124, 190, 18, '#555', 4); rr(-40, -78, 34, 34, 8, '#2a2a2a'); circ(-30, -68, 7, '#0a0a0a'); circ(-16, -56, 7, '#0a0a0a');   // the phone, back to the camera, its lenses
    for (const sx of [-1, 1]) { ctx.save(); ctx.translate(sx * 62, 10); rr(-16, -34, 32, 68, 14, '#8a8a8a'); rr(-12, -30, 24, 60, 11, '#dcdcdc'); ctx.restore(); }   // fingers round its edges
    ctx.restore();
  } else {
    pthS(`M${head.x - 16},${head.y + 10} q10,7 20,0`, '#333', 4);                // closed eye
    ctx.save(); ctx.translate(470, 430); ctx.rotate(0.5 + hash(n + 3) * 0.3); rr(0, -20, 200, 40, 20, '#dcdcdc'); circ(206, 0, 26, '#e2e2e2'); ctx.restore();   // arm over the blanket
  }
  ctx.restore();
  // the flash: blown-out centre, harsh fall-off, a little noise
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const g = ctx.createRadialGradient(x + w * 0.5, y + h * 0.48, Math.min(w, h) * 0.05, x + w * 0.5, y + h * 0.5, Math.max(w, h) * 0.75);
  g.addColorStop(0, 'rgba(255,252,245,0.42)'); g.addColorStop(0.45, 'rgba(255,252,245,0.05)'); g.addColorStop(0.75, 'rgba(0,0,0,0.35)'); g.addColorStop(1, 'rgba(0,0,0,0.85)');
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  if (o.grain !== false && grainC) { ctx.globalAlpha = 0.14; ctx.drawImage(grainC[(n % 4 + 4) % 4], x, y, w, h); ctx.globalAlpha = 1; }
  if (o.stamp) { const fs = Math.max(11, Math.round(h * 0.055)); ctx.save(); redGlow(6); text(o.stamp, x + w - fs * 0.6, y + h - fs * 0.6, `600 ${fs}px Plex`, '#ff4a2a', 'right'); ctx.restore(); }
  ctx.restore();
}
// the newest photo: so close it is only your eye, shut, lashes, skin texture, the flash on it
function eyePhoto(x, y, w, h, o = {}) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rr(x, y, w, h, 0, '#cfcfcf');
  const cx = x + w / 2, cy = y + h / 2, s = Math.min(w, h) / 500;
  ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate(-0.12);
  // brow, lid crease, the closed seam and the lashes
  pth('M-260,-150 C-120,-220 120,-220 260,-140 L260,-110 C120,-180 -120,-180 -260,-120 Z', '#3a3a3a');
  pthS('M-200,-30 C-100,-90 100,-90 200,-30', '#9a9a9a', 6);
  pthS('M-210,20 C-100,70 100,70 210,20', '#2a2a2a', 9);
  for (let i = 0; i < 16; i++) { const u = -190 + i * 25, v = 20 + 50 * (1 - Math.pow(u / 210, 2)); pthS(`M${u},${v} q${u * 0.02},34 ${u * 0.08 + 6},58`, '#1e1e1e', 4.5); }
  for (let i = 0; i < 40; i++) circ((hash(i * 1.3) - 0.5) * 480, (hash(i * 2.9) - 0.5) * 420, 1.5 + hash(i) * 2, 'rgba(0,0,0,0.12)');
  ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const g = ctx.createRadialGradient(x + w * 0.45, y + h * 0.4, 5, x + w / 2, y + h / 2, Math.max(w, h) * 0.7);
  g.addColorStop(0, 'rgba(255,255,255,0.5)'); g.addColorStop(0.5, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,0.75)'); ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  if (grainC) { ctx.globalAlpha = 0.16; ctx.drawImage(grainC[1], x, y, w, h); ctx.globalAlpha = 1; }
  if (o.stamp) { const fs = Math.max(11, Math.round(h * 0.055)); ctx.save(); redGlow(6); text(o.stamp, x + w - fs * 0.6, y + h - fs * 0.6, `600 ${fs}px Plex`, '#ff4a2a', 'right'); ctx.restore(); }
  ctx.restore();
}
// where the lens on its face is, in the room
const LENS = { x: WALL + 172 * TS, y: CEIL + 117 * TS };
function lensGlint(a = 1) { ctx.save(); ctx.globalAlpha *= a; redGlow(14); circ(LENS.x, LENS.y, 4.5, C.red); ctx.restore(); }
// a dashed sight line
function sight(x1, y1, x2, y2, col, p = 1, w = 4) { ctx.save(); ctx.setLineDash([14, 11]); lnP(x1, y1, x2, y2, w, col, p); ctx.restore(); }
