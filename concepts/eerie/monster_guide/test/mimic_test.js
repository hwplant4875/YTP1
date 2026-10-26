// Monster onboarding style test: a flat cut-out "puppet" mimic in the reference channel's look (grey block city, letterbox,
// vivid accent colours, speech bubble pop, bottom subtitle band, colour-wash title card). draw(t) renders one frame at time t (s).
const cv = document.getElementById('c'), ctx = cv.getContext('2d'), W = 1920, H = 1080;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)), lerp = (a, b, k) => a + (b - a) * k;
const eo = k => 1 - (1 - clamp(k)) ** 3, eio = k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - (-2 * k + 2) ** 3 / 2; };
const back = k => { k = clamp(k); const c = 1.9; return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2; };   // overshoot pop
const prog = (t, t0, d) => clamp((t - t0) / d);
const P = (d, f, s, lw = 0) => { const p = new Path2D(d); if (f) { ctx.fillStyle = f; ctx.fill(p); } if (s) { ctx.strokeStyle = s; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke(p); } };
const R = (x, y, w, h, f, r = 0) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = f; ctx.fill(); };
const C = (x, y, r, f) => { ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = f; ctx.fill(); };
const hash = n => { const x = Math.sin(n * 127.1 + 3.7) * 43758.5; return x - Math.floor(x); };

// the grey block city behind everything, slow parallax
function city(t, cam) {
  ctx.fillStyle = '#1d1d1f'; ctx.fillRect(0, 0, W, H);
  for (const [layer, col, base, sp] of [[0, '#2a2a2d', 520, 0.3], [1, '#343438', 640, 0.6], [2, '#3e3e43', 760, 1]]) {
    for (let i = 0; i < 14; i++) { const w = 120 + hash(i + layer * 31) * 200, h = 260 + hash(i * 7 + layer) * 420, x = i * 170 - 200 - cam * sp * 40 + layer * 60;
      R(x, base - h + 300, w, h + 400, col);
      ctx.fillStyle = 'rgba(255,255,255,0.05)'; for (let r = 0; r < 6; r++) for (let c = 0; c < 3; c++) if (hash(i * 13 + r * 3 + c + layer) > 0.45) ctx.fillRect(x + 18 + c * (w - 36) / 3, base - h + 330 + r * 56, (w - 60) / 4, 26); }
  }
  ctx.fillStyle = '#151517'; ctx.fillRect(0, 880, W, 200);   // floor
  const g = ctx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1150); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.7)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

// the mimic: a treasure chest puppet. open 0..1 (lid hinge), tongue 0..1, eyes 0..1, breathe phase
function mimic(x, y, s, o) {
  const { open = 0, tongue = 0, eyes = 0, t = 0 } = o;
  const br = 1 + 0.018 * Math.sin(t * 2.4);
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s * br);
  // shadow
  ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.beginPath(); ctx.ellipse(0, 4, 330, 34, 0, 0, 7); ctx.fill();
  // the box (front face + top rim)
  const WOOD = '#8a5530', WOODD = '#5e3519', WOODL = '#a86a3c', IRON = '#6b6f78', IROND = '#454850', GOLD = '#e8b33a';
  P('M-300,0 L-300,-250 L300,-250 L300,0 Z', WOOD);
  for (let i = 0; i < 4; i++) P(`M-300,${-62 - i * 62} L300,${-62 - i * 62}`, null, WOODD, 5);   // planks
  P('M-300,0 L-300,-250 L-270,-250 L-270,0 Z', WOODD);
  for (const bx of [-210, 210]) { R(bx - 26, -250, 52, 250, IRON); R(bx - 26, -250, 10, 250, IROND); for (let k = 0; k < 4; k++) C(bx, -220 + k * 62, 7, IROND); }
  R(-300, -36, 600, 36, IRON); R(-300, -36, 600, 9, IROND);
  // the inside of the mouth (visible when the lid opens): dark red throat, lower teeth, tongue, eyes deep inside
  if (open > 0.02) {
    const mh = 230 * open;
    ctx.save(); ctx.beginPath(); ctx.rect(-290, -250 - mh, 580, mh + 6); ctx.clip();
    P(`M-290,-250 L290,-250 L290,${-250 - mh} L-290,${-250 - mh} Z`, '#2a0508');
    P(`M-250,-250 C-150,${-250 - mh * 0.7} 150,${-250 - mh * 0.7} 250,-250 Z`, '#4a0a10');
    if (eyes > 0) { ctx.save(); ctx.globalAlpha = eyes; ctx.shadowColor = '#9ff4ff'; ctx.shadowBlur = 30;
      for (const ex of [-70, 70]) { C(ex, -250 - mh * 0.62, 26, '#bff8ff'); C(ex + 6, -250 - mh * 0.62, 9, '#0c2a30'); } ctx.restore(); }
    // tongue: a long curl sliding out over the front
    ctx.restore();
  }
  // lower teeth on the rim
  if (open > 0.02) for (let i = 0; i < 13; i++) { const tx = -276 + i * 46, h = (26 + 18 * hash(i)) * clamp(open * 2);
    P(`M${tx},-250 L${tx + 22},${-250 - h} L${tx + 44},-250 Z`, '#f3ecd8', '#3a2412', 3); }
  if (tongue > 0) { const L = 380 * eo(tongue), wv = Math.sin(t * 5) * 18;
    P(`M-60,-250 C-70,${-150} ${-30 + wv},${-250 + L * 0.55} ${40 + wv},${-250 + L * 0.8} C${80 + wv},${-250 + L} ${130 + wv},${-250 + L * 0.85} ${110 + wv},${-250 + L * 0.7} C${80 + wv},${-250 + L * 0.5} 50,-150 60,-250 Z`, '#d6334a', '#5a0d16', 4);
    P(`M0,-240 C${10 + wv * 0.5},${-250 + L * 0.4} ${40 + wv},${-250 + L * 0.65} ${70 + wv},${-250 + L * 0.78}`, null, '#a01f33', 4); }
  // the lid, hinged at the back top edge: rotates up and back (drawn as a squashed front face + top)
  ctx.save(); ctx.translate(0, -250);
  const a = open * 1.15, lh = 150 * Math.cos(a), lt = 150 * Math.sin(a);   // visible lid height shrinks as it tilts back; it lifts
  ctx.translate(0, -lt * 1.55);
  P(`M-310,0 L-310,${-lh} Q0,${-lh - 70 * Math.cos(a)} 310,${-lh} L310,0 Z`, WOODL);
  P(`M-310,0 L-310,${-lh} Q0,${-lh - 70 * Math.cos(a)} 310,${-lh} L310,0 Z`, null, WOODD, 5);
  for (const bx of [-210, 210]) P(`M${bx - 26},0 L${bx - 26},${-lh - 30 * Math.cos(a)} L${bx + 26},${-lh - 30 * Math.cos(a)} L${bx + 26},0 Z`, IRON);
  // upper teeth hanging from the lid's front edge
  if (open > 0.02) for (let i = 0; i < 13; i++) { const tx = -280 + i * 46, h = (30 + 22 * hash(i + 9)) * clamp(open * 2);
    P(`M${tx},0 L${tx + 23},${h} L${tx + 46},0 Z`, '#f3ecd8', '#3a2412', 3); }
  R(-310, -18, 620, 18, IRON);
  // the lock plate stays on the lid
  R(-48, -60, 96, 84, GOLD, 10); R(-48, -60, 96, 14, '#b9861d', 6); P('M-10,-26 a10,10 0 1,1 20,0 L8,6 L-8,6 Z', '#3b2a07');
  ctx.restore();
  ctx.restore();
}

// a speech bubble that pops in with overshoot; text lines centred
function bubble(x, y, w, h, k, lines, tailX) {
  if (k <= 0) return; const s = back(k);
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha = clamp(k * 3);
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24; ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.ellipse(0, 0, w / 2, h / 2, 0, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.moveTo(tailX - 30, h / 2 - 30); ctx.lineTo(tailX + 40, h / 2 + 60); ctx.lineTo(tailX + 30, h / 2 - 20); ctx.fill(); ctx.shadowBlur = 0;
  ctx.fillStyle = '#111'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach(([txt, font], i) => { ctx.font = font; ctx.fillText(txt, 0, (i - (lines.length - 1) / 2) * 46); });
  ctx.restore();
}
function subtitle(txt, a = 1) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.font = '500 44px I'; const w = ctx.measureText(txt).width + 48;
  ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(W / 2 - w / 2, 948, w, 64); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, W / 2, 981); ctx.restore(); }
function ornament(x, y, w, a) { ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - w / 2, y); ctx.lineTo(x + w / 2, y); ctx.stroke();
  for (const d of [-1, 1]) { ctx.beginPath(); ctx.arc(x + d * w * 0.18, y - 14, 14, 0, Math.PI, d < 0); ctx.stroke(); C(x + d * w / 2, y, 6, '#fff'); } C(x, y - 6, 8, '#fff'); ctx.restore(); }

window.draw = t => {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  // camera: slow push in, then a quick punch when the lid opens
  const open = eio(prog(t, 2.0, 0.55)), punch = Math.sin(prog(t, 2.0, 0.35) * Math.PI) * 0.04;
  const z = 1 + 0.06 * eio(prog(t, 0, 6)) + punch, shake = t > 2 && t < 2.5 ? (hash(Math.floor(t * 60)) - 0.5) * 14 : 0;
  ctx.save(); ctx.translate(W / 2 + shake, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
  city(t, t);
  // the mimic slides in from the right on its feet, settles, then wakes up
  const slide = eo(prog(t, 0.1, 0.9));
  mimic(lerp(1500, 1040, slide), 880, 1.12, { open, tongue: prog(t, 2.6, 0.8), eyes: prog(t, 2.3, 0.4), t });
  ctx.restore();
  bubble(560, 330, 760, 300, prog(t, 3.3, 0.35), [['RULE 1.', '700 40px I'], ['Never be the only chest', '600 40px I'], ['in an empty room.', '600 40px I']], 200);
  subtitle(t < 3.3 ? 'Welcome to your first day as a mimic.' : 'Adventurers always count the chests.', clamp(t * 3));
  // colour-wash title card at the end
  const wash = prog(t, 5.2, 0.35);
  if (wash > 0) { ctx.fillStyle = `rgba(178,16,40,${0.82 * wash})`; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalAlpha = wash; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 20;
    ctx.font = '400 150px S'; ctx.fillText('Mimic', W / 2, 470); ctx.font = '600 46px I'; ctx.fillText('ONBOARDING  •  FILE 01', W / 2, 590); ctx.restore();
    ornament(W / 2, 360, 560 * eo(wash), wash); ornament(W / 2, 660, 560 * eo(wash), wash); }
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, 34); ctx.fillRect(0, H - 34, W, 34);   // letterbox
};
