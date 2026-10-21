// ---------- EP06 scenes: "If Michael Myers Is Standing Outside Your House" ----------
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

// ---------- shared shots ----------
const LIGHT = { x: 1080, y: 642, s: 0.42 };            // where he stands: under the streetlight across the street
const MAILBOX = { x: 900, y: 884, s: 0.74 };
const LAWN = { x: 1010, y: 1080, s: 1.32 };
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
// a white bracket frame around a point (focus marks)
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
// the street through your window. o.z, o.f: zoom + focus, o.him, o.close
function lookOut(t, o = {}) {
  const x0 = o.x0 ?? 300, x1 = o.x1 ?? 1620, y0 = o.y0 ?? 80, y1 = o.y1 ?? 930;
  windowPOV(t, { cross: o.cross ?? false, close: o.close, x0, x1, y0, y1,
    fn: () => streetScene(t, { scr: [(x0 + x1) / 2, (y0 + y1) / 2], cam: [o.z || 1.3, ...(o.f || [1060, 520])], him: o.him === undefined ? LIGHT : o.him, light: o.light, kids: o.kids, near: o.near, emptyHouse: o.emptyHouse, houses: o.houses }) });
}
// a "does not work" header row at the top left, X drawn at tx
function noHead(t, seg, ic, label, tx) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start, -40, 0, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(60, 60, 150 + label.length * 30, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, 150 + label.length * 30, 130, 18, '#2a2a2d', 3);
    icon6(ic, 125, 125, 0.48); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35);
  ctx.restore();
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: through your window, he is already there under the streetlight, looking in
  const ta = wt(seg, 'away');
  lookOut(t, { cross: false, x0: 120, x1: 1800, y0: 30, y1: 1000, z: zk(t, 0, seg.end + 0.8, 2.15, 2.6), f: [1082, 470] });
  if (t >= ta - 0.3) pop(t, ta - 0.3, 960, 150, () => tag('DO NOT LOOK AWAY', 960, 160, C.red, 52, 'center'), 0.3);
};
function h2Windows(seg) { return [[seg.start, wt(seg, 'do'), 'knives', 'knives', 250], [wt(seg, 'do'), wt(seg, 'and'), 'closet', 'closet', 250], [wt(seg, 'and'), nextStart(seg), 'rise', 'dead', 250]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 1600, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon6(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {
      // the knife block in the dark kitchen: one slot is empty, and it turns red
      black(); rr(-200, 960, W + 400, 200, 0, '#121214');
      cam(t, w0, blk - w0, 1.0, 1.25, 860, 760, () => blockClose(t, { x: 860, y: 1000, s: 1.7, missing: 0, red: t >= w0 + 0.5 }));
    } else if (i === 1) {
      // you hide in the closet: the mask comes right up to the slats
      const k = ease(prog(t, w0 + 0.2, hit - w0 - 0.2));
      slats(() => { hallway(t, {}); ctx.save(); ctx.translate(960, 560); const z = lerp(0.5, 2.6, k); ctx.scale(z, z); ctx.globalAlpha = 0.85; myers(0, 520, 1, { knife: 1, red: prog(t, hit - 0.3, 0.3) }); ctx.restore(); });
    } else {
      // you go to check: he sits up
      black(); ctx.fillStyle = '#0d0c0b'; ctx.fillRect(0, 760, W, 400); for (let j = 0; j < 9; j++) ln(0, 780 + j * 34, W, 780 + j * 34, 2, '#191715');
      cam(t, w0, blk - w0, 1.1, 1.45, 820, 640, () => myersSide(760, 830, 1.15, { floor: 1, sit: prog(t, hit - 0.75, 0.6), knife: 1, red: prog(t, hit - 0.1, 0.2) }));
    }
    if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not look away ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT LOOK AWAY');
const kidX = (off, ph) => ((off + ph * 60) % 2600) - 300;
S.a1 = (t, seg) => {
  // Halloween: the street full of masks
  const tw = wt(seg, 'witches'), tg = wt(seg, 'ghosts'), tk = wt(seg, 'kids');
  streetScene(t, { cam: [zk(t, seg.start, seg.end - seg.start + 0.7, 1.35, 1.5), lerp(560, 760, ease((t - seg.start) / (seg.end - seg.start))), 470], him: null, kids: t - seg.start + 9,
    near: () => {
      const lab = [[tw, 'WITCH', 0], [tg, 'GHOST', 210], [tk, 'CANDY', 330]];
      for (const [t0, s, off] of lab) if (t >= t0) { const x = kidX(off, t - seg.start + 9) + 30; pop(t, t0, x, 480, () => tag(s, x, 480, C.fig, 26, 'center'), 0.3); }
    } });
};
S.a2 = (t, seg) => {
  // one of them is not moving: the camera stops on him while the kids walk past
  const tm = wt(seg, 'moving');
  streetScene(t, { cam: [zk(t, seg.start, 2.4, 1.6, 2.2), 1080, 480], him: LIGHT, kids: t + 30,
    near: () => { ctx.save(); trickKid(kidX(560, t + 30) + 0, 660, 0.62, 'ghost', t * 5); ctx.restore();
      brackets(LIGHT.x, LIGHT.y - 130, 150, 310, prog(t, tm - 0.1, 0.25), C.fig); } });
};
S.a3 = (t, seg) => {
  // the man: dark coveralls, pale mask, perfectly still
  const tj = wt(seg, 'jumpsuit'), tm = wt(seg, 'mask'), ts = wt(seg, 'still');
  streetScene(t, { cam: [zk(t, seg.start, seg.end - seg.start + 0.7, 2.6, 2.9), 1082, 520], him: LIGHT, kids: null,
    near: () => {
      const s = 1 / 2.7;
      if (t >= tj) pop(t, tj, 1180, 560, () => { ln(1105, 560, 1170, 560, 3 * s * 2, C.fig); ctx.save(); ctx.translate(1180, 560); ctx.scale(s, s); tag('DARK JUMPSUIT', 0, 10, C.fig, 30, 'left'); ctx.restore(); }, 0.3);
      if (t >= tm) pop(t, tm, 980, 405, () => { ln(1068, 405, 1000, 405, 3 * s * 2, C.fig); ctx.save(); ctx.translate(990, 405); ctx.scale(s, s); tag('WHITE MASK', 0, 10, C.fig, 30, 'right'); ctx.restore(); }, 0.3);
      if (t >= ts) pop(t, ts, 1180, 640, () => { ctx.save(); ctx.translate(1180, 650); ctx.scale(s, s); tag('PERFECTLY STILL', 0, 10, C.fig, 30, 'left'); ctx.restore(); }, 0.3);
    } });
};
S.a4 = (t, seg) => {
  // over his shoulder: not the houses. Your window.
  const th = wt(seg, 'houses'), tw = wt(seg, 'window');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1100, 500, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 700); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(560, 700, 520, { win: [0.6, 0, 0, 0.5], porch: 1, pumpkins: 1 });
    house(1260, 720, 700, { win: [0, 0.95, 0.3, 0], porch: 1, pumpkins: 1, who: { win: 1, fn: (x, y, w, h) => me(x + w / 2, y + h + h * 0.55, h / 300, { face: 'front' }) } });
    house(1880, 700, 480, { win: [0.5, 0.5, 0, 0], pumpkins: 1 });
    rr(-200, 700, W + 400, 400, 0, NIGHT.grass);
    // the looks: the other houses get crossed, then the line ends on your window
    const hx = 330, hy = 380;
    if (t >= th && t < tw + 0.2) for (const [x, y] of [[505, 520], [1840, 520]]) { ctx.save(); ctx.setLineDash([14, 12]); ctx.globalAlpha = 0.6; ln(hx, hy, x, y, 4, C.fig); ctx.restore(); redX(x, y, 28, prog(t, th + 0.4, 0.25)); }
    if (t >= tw - 0.1) { const k = ease(prog(t, tw - 0.1, 0.5)), wx = 1260 + 700 * 0.62 / 2 * 0 + 112, wy = 720 - 434 * 0.86 + 56;
      ctx.save(); redGlow(14); ctx.setLineDash([16, 12]); ln(hx, hy, lerp(hx, 1287, k), lerp(hy, 403, k), 6, C.red); ctx.restore(); if (k >= 1) brackets(1287, 403, 180, 130, 1, C.red); }
    myers(330, 1260, 1.45, { back: true });
  });
};
S.a5 = (t, seg) => {
  // the head tilts, slowly
  const tt = wt(seg, 'tilts');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.12, 960, 480, () => {
    black(); const g = ctx.createRadialGradient(960, 300, 50, 960, 400, 900); g.addColorStop(0, 'rgba(255,250,235,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    myers(960, 2500, 3.6, { tilt: -0.32 * ease(prog(t, tt, 2.4)) });
  });
};
S.a6 = (t, seg) => {
  // you at the window. Not to call. Not the curtains. Not even a long blink.
  const tc = wt(seg, 'call'), tu = wt(seg, 'curtains'), tb = wt(seg, 'blink');
  lookOut(t, { x0: 860, x1: 1800, y0: 90, y1: 900, z: 1.9, f: [1000, 470] });
  me(1120, 1420, 2.3, { face: 'back' });
  listCard(80, 250, 700, 560);
  noRow(t, tc - 0.2, tc + 0.25, 130, 360, 'phone', 'CALL SOMEONE', 42);
  noRow(t, tu - 0.2, tu + 0.25, 130, 530, 'curtain', 'CLOSE CURTAINS', 42);
  noRow(t, tb - 0.2, tb + 0.25, 130, 700, 'blink', 'BLINK TOO LONG', 42);
};
S.a7 = (t, seg) => {
  // he never runs: he walks
  const tr = wt(seg, 'runs'), tn = wt(seg, 'need');
  black(); rr(-200, 900, W + 400, 300, 0, '#0c0c0e'); ln(-200, 900, W + 400, 900, 3, '#26262a');
  pop(t, seg.start, 520, 600, () => { me(520, 900, 1.3, { face: 'right', walk: t * 14, arms: [0.35 + 0.3 * Math.sin(t * 14), 0.35 - 0.3 * Math.sin(t * 14)] }); }, 0.3);
  if (t >= tr) { redX(520, 620, 170, prog(t, tr, 0.3)); }
  if (t >= tr + 0.3) slideIn(t, tr + 0.3, 80, 0, () => { myersSide(1300 + (t - tr) * 30, 910, 1.0, { walk: (t - tr) * 3.2, knife: 1 }); });
  if (t >= tn) pop(t, tn, 1340, 230, () => tag('HE WALKS', 1340, 240, C.fig, 44, 'center'), 0.3);
};
S.a8 = (t, seg) => {
  // every time you look away (black), he is closer: the streetlight, the mailbox, your lawn
  const ts = wt(seg, 'streetlight'), tm = wt(seg, 'mailbox'), tl = wt(seg, 'lawn');
  const him = t < tm - 0.05 ? LIGHT : t < tl - 0.05 ? MAILBOX : LAWN;
  const lab = t < tm - 0.05 ? (t >= ts ? ['STREETLIGHT', 1400, 200] : null) : t < tl - 0.05 ? ['MAILBOX', 560, 800] : ['YOUR LAWN', 1440, 760];
  lookOut(t, { z: 1.25, f: [1000, 560], him });
  if (lab) pop(t, him === LIGHT ? ts : him === MAILBOX ? tm : tl, lab[1], lab[2], () => tag(lab[0], lab[1], lab[2], him === LAWN ? C.red : C.fig, 40, 'center'), 0.25);
  for (const b of [wt(seg, 'away'), ts, tm, tl]) if (t > b - 0.16 && t < b - 0.02) blackAfter(t, b - 0.16);   // the blink
};
S.a9 = (t, seg) => {
  // you look back: the streetlight is empty
  const te = wt(seg, 'empty');
  lookOut(t, { z: zk(t, seg.start, seg.end - seg.start + 0.6, 1.4, 2.0), f: [1080, 520], him: null });
  if (t >= te) pop(t, te, 960, 150, () => tag('EMPTY', 960, 160, C.red, 52, 'center'), 0.3);
};
S.a10 = (t, seg) => {
  // he is already inside: the white mask in the hallway door behind you
  const ti = wt(seg, 'inside'), k = ease(prog(t, ti - 0.3, 1.0));
  black();
  cam(t, seg.start, 3.5, 1.0, 1.12, 700, 520, () => {
    rr(1100, 120, 680, 700, 4, '#05070a'); ctx.save(); ctx.beginPath(); ctx.rect(1100, 120, 680, 700); ctx.clip(); streetScene(t, { cam: [1.5, 1080, 500], him: null }); ctx.restore();
    rrS(1100, 120, 680, 700, 4, '#2a2a2d', 18); ln(1440, 120, 1440, 820, 12, '#1e1e21');
    rr(260, 230, 340, 820, 2, '#020202'); rrS(260, 230, 340, 820, 2, '#1d1d20', 10);   // the dark hall door behind you
    ctx.save(); ctx.globalAlpha *= k; myers(430, 1050, 1.28, { dark: 0.55, knife: 1, red: prog(t, seg.end + 0.6, 0.3) }); ctx.restore();
    me(1440, 1240, 2.2, { face: 'back' });
  });
};

// ---------- rule 2: count the knives ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'COUNT THE KNIVES');
// knife block in close-up: slot tips for the numbers
function blockClose(t, o = {}) {
  ctx.save(); ctx.translate(o.x ?? 960, o.y ?? 940); ctx.scale(o.s ?? 2.4, o.s ?? 2.4);
  knifeBlock(0, 0, 1, { missing: o.missing ?? -1, red: o.red, t, out: o.out });
  for (let i = 0; i < 5; i++) { const nt = (o.numT || [])[i]; if (nt != null && t >= nt) { const [x, y] = blkTip(i, 44); pop(t, nt, x, y, () => { circ(x, y, 22, C.fig); text(String(i + 1), x, y + 10, '900 28px M', '#000'); }, 0.25); } }
  ctx.restore();
}
S.b1 = (t, seg) => {
  // the dark kitchen, the light stays off, count
  const tl = wt(seg, 'light'), tc = wt(seg, 'count');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.2, 760, 560, () => {
    kitchen(t, { blockX: 400, blockS: 1.0 });
    rr(1380, 470, 70, 110, 10, '#2a2a2e'); rr(1402, 495, 26, 50, 6, '#111');
    if (t >= tl) { tag('LIGHT', 1415, 650, C.fig, 30, 'center'); redX(1415, 525, 60, prog(t, tl + 0.2, 0.3)); }
    ctx.save(); ctx.translate(400, 700); ctx.scale(1.0, 1.0); for (let i = 0; i < 5; i++) { const nt = tc + 0.3 + i * 0.28; if (t >= nt) { const [x, y] = blkTip(i, 44); pop(t, nt, x, y, () => { circ(x, y, 22, C.fig); text(String(i + 1), x, y + 10, '900 28px M', '#000'); }, 0.25); } } ctx.restore();
  });
};
S.b2 = (t, seg) => {
  // he never brings a knife. He takes yours.
  const to = wt(seg, 'own'), tu = wt(seg, 'uses'), k = ease(prog(t, tu, 0.9));
  black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
  rr(1140, 820, 760, 30, 0, '#232327'); rr(1140, 850, 760, 300, 0, '#0e0e10');
  knifeBlock(1500, 820, 1.4, { missing: k > 0 ? 0 : -1 });
  myers(560, 1010, 1.25, { knife: k >= 1 ? 1 : 0 });
  if (t >= to) { pop(t, to, 560, 200, () => tag('NO KNIFE OF HIS OWN', 560, 210, C.fig, 36, 'center'), 0.3); }
  if (k > 0 && k < 1) { const tp = blkTip(0, -40), sx = 1500 + tp[0] * 1.4, sy = 820 + tp[1] * 1.4; knife(lerp(sx, 440, k), lerp(sy, 680, k), lerp(-2.1, Math.PI / 2, k) + k * 6.28, 1.25); }
  if (t >= tu + 0.9) pop(t, tu + 0.9, 1500, 260, () => tag('YOURS', 1500, 270, C.red, 44, 'center'), 0.3);
};
S.b3 = (t, seg) => {
  // five slots, five handles: good, he is still outside
  const t1 = wt(seg, 'five', 1), t2 = wt(seg, 'five', 2), tg = wt(seg, 'good'), to = wt(seg, 'outside');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 800, 600, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#121214');
    blockClose(t, { x: 700, y: 1010, s: 1.45, numT: [0, 1, 2, 3, 4].map(i => t1 + 0.2 + i * 0.12) });
    if (t >= t2) pop(t, t2, 520, 180, () => tag('5 HANDLES', 520, 190, C.fig, 40, 'center'), 0.3);
    if (t >= tg) { pop(t, tg, 860, 180, () => { check(860, 175, 40, prog(t, tg, 0.3)); }, 0.3); }
  });
  if (t >= to - 0.3) slideIn(t, to - 0.3, 60, 0, () => {
    rr(1300, 300, 520, 420, 16, '#000'); ctx.save(); ctx.beginPath(); ctx.roundRect(1310, 310, 500, 400, 12); ctx.clip(); streetScene(t, { scr: [1560, 510], cam: [1.7, 1080, 500], him: LIGHT }); ctx.restore();
    rrS(1310, 310, 500, 400, 12, C.fig, 4); tag('STILL OUTSIDE', 1560, 790, C.fig, 34, 'center'); });
};
S.b4 = (t, seg) => {
  // one slot is empty
  const te = wt(seg, 'empty');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.3, 760, 560, () => { black(); rr(-200, 940, W + 400, 300, 0, '#121214'); blockClose(t, { x: 900, y: 1020, s: 1.55, missing: 0, red: t >= te }); });
  redFlash(t, te, 0.05);
};
S.b5 = (t, seg) => {
  // do not look for it, do not call out, do not check the other rooms
  const tl = wt(seg, 'look'), tc = wt(seg, 'call'), tr = wt(seg, 'check');
  ctx.save(); ctx.globalAlpha = 0.45; black(); rr(-200, 940, W + 400, 300, 0, '#121214'); blockClose(t, { x: 1500, y: 1000, s: 1.7, missing: 0, red: true }); ctx.restore();
  listCard(160, 230, 900, 580);
  noRow(t, tl - 0.25, tl + 0.3, 220, 350, 'search', 'LOOK FOR IT', 46);
  noRow(t, tc - 0.25, tc + 0.3, 220, 520, 'voice', 'CALL OUT', 46);
  noRow(t, tr - 0.25, tr + 0.3, 220, 690, 'door', 'CHECK THE ROOMS', 46);
};
S.b6 = (t, seg) => {
  // the cutaway: you in the kitchen, him in the living room, your biggest knife
  const ti = wt(seg, 'inside'), tb = wt(seg, 'biggest');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 960, 560, () => {
    black(); cutaway(t, { hot: t >= ti ? ['LIVING ROOM'] : [] });
    me(700, 850, 0.62, { face: 'front' });
    if (t >= ti - 0.1) fadeIn(t, ti - 0.1, () => myers(1230, 850, 0.42, { knife: 1, knifeRed: t >= tb, red: t >= tb ? 1 : 0 }), 0.4);
    if (t >= tb) pop(t, tb, 1220, 470, () => tag('YOUR BIGGEST KNIFE', 1220, 480, C.red, 30, 'center'), 0.3);
  });
};
S.b7 = (t, seg) => {
  // you go looking: a dark hallway, the torch beam sweeping
  const tf = wt(seg, 'find');
  hallway(t, { open: [0.6, 0.2, 0, 0.3] });
  ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const bx = 960 + Math.sin(t * 1.1) * 300, by = 560 + Math.cos(t * 0.8) * 50;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(bx, by, 10, bx, by, 300); g.addColorStop(0, 'rgba(255,245,220,0.22)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.beginPath(); ctx.moveTo(640, 820); ctx.lineTo(bx - 150, by - 90); ctx.lineTo(bx + 150, by + 90); ctx.closePath(); ctx.fillStyle = 'rgba(255,245,220,0.05)'; ctx.fill(); ctx.restore();
  me(560, 1420, 2.0, { face: 'back', arms: [0, 0.35] });
  if (t >= tf) pop(t, tf, 960, 160, () => tag('YOU WILL FIND IT', 960, 170, C.fig, 44, 'center'), 0.3);
};
S.b8 = (t, seg) => {
  // in the black kitchen window: you, and right behind you, the mask and the knife
  const tr = wt(seg, 'reflection'), tb = wt(seg, 'behind'), k = ease(prog(t, tb - 0.2, 0.8));
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.25, 1.75, 1020, 470, () => {
    kitchen(t, { block: false, reflect: (x, y, w, h) => {
      ctx.save(); ctx.globalAlpha = 0.42; me(x + w * 0.36, y + h + 240, 1.3, { face: 'front' }); ctx.restore();
      if (k > 0) { ctx.save(); ctx.globalAlpha = 0.65 * k; myers(x + w * 0.68, y + h + 470, 1.1, { knife: 2, red: prog(t, seg.end + 0.5, 0.3) }); ctx.restore(); }
    } });
  });
  me(700, 1560, 2.6, { face: 'back' });
};

// ---------- rule 3: do not hide in the closet ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT HIDE IN THE CLOSET');
S.c1 = (t, seg) => {
  // everyone hides in the closet. He knows that.
  const tw = wt(seg, 'want'), tk = wt(seg, 'knows'), k = ease(prog(t, tw, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 520, () => {
    black(); cutaway(t, { hot: t >= tk ? ['CLOSET'] : [] });
    me(lerp(700, 1040, k), 550, 0.62, { face: k > 0.98 ? 'front' : 'right', walk: k < 1 ? t * 12 : null });
    myers(1230, 850, 0.42, { knife: 1, tilt: t >= tk ? -0.3 * ease(prog(t, tk, 0.6)) : 0 });
    if (t >= tk) { ctx.save(); redGlow(12); ctx.setLineDash([12, 10]); const kk = ease(prog(t, tk, 0.5)); ln(1230, 630, lerp(1230, 1040, kk), lerp(630, 420, kk), 5, C.red); ctx.restore(); }
  });
};
S.c2 = (t, seg) => {
  // through the slats: a shape walks past, slowly, your knife in his hand
  const tw = wt(seg, 'walks'), k = prog(t, tw - 1.0, seg.end - tw + 1.6);
  slats(() => {
    cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 520, () => {
      ctx.fillStyle = '#2a2a31'; ctx.fillRect(-200, -200, W + 400, H + 400); rr(-200, 860, W + 400, 400, 0, '#24232a');
      for (let i = 0; i < 4; i++) { rr(150 + i * 480, 220, 230, 640, 2, '#121216'); rrS(150 + i * 480, 220, 230, 640, 2, '#3a3a42', 6); }
      const g = ctx.createRadialGradient(1500, 260, 20, 1500, 260, 900); g.addColorStop(0, 'rgba(170,190,230,0.2)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
      if (k > 0) myersSide(lerp(-250, 2150, k), 1010, 1.25, { walk: (t - tw) * 3.0, knife: 1 });
    });
  }, { gap: 30 });
};
S.c3 = (t, seg) => {
  // every door, one by one
  const tb = wt(seg, 'bathroom'), tl = wt(seg, 'laundry'), tg = wt(seg, 'guest');
  const op = [prog(t, tb - 0.2, 0.6), prog(t, tl - 0.2, 0.6), 0, prog(t, tg - 0.2, 0.6)].map(ease);
  hallway(t, { open: op, labels: [['BATHROOM', tb], ['LAUNDRY', tl], null, ['GUEST ROOM', tg, -110]],
    fig: at => { const d = lerp(0.4, 3.0, ease(prog(t, seg.start, seg.end - seg.start + 0.6))), p = at(960, 1130, d); myers(p[0], p[1], 1.55 / (1 + d), { back: true, walk: t * 3 }); } });
};
S.c4 = (t, seg) => {
  // the route through the house: the closet is always last
  const tl = wt(seg, 'last'), route = ['HALL', 'BATHROOM', 'GUEST ROOM', 'BEDROOM', 'LAUNDRY', 'KITCHEN', 'CLOSET'];
  const k = prog(t, seg.start, tl - seg.start), n = Math.floor(k * (route.length - 1)), f = k * (route.length - 1) - n;
  floorPlan(t, { checked: route.slice(1, Math.min(n + 1, route.length - 1)), hot: t >= tl ? 'CLOSET' : null });
  const a = roomC(route[Math.min(n, route.length - 1)]), b = roomC(route[Math.min(n + 1, route.length - 1)]);
  const x = lerp(a[0], b[0], ease(f)), y = lerp(a[1], b[1], ease(f));
  ctx.save(); redGlow(16); circ(x, y - 40, 16, C.red); noGlow(); ctx.restore();
  if (t >= tl) pop(t, tl, 1380, 560, () => tag('LAST', 1380, 570, C.red, 40, 'center'), 0.3);
};
S.c5 = (t, seg) => {
  // when he leaves a room, slip into it behind him
  const ts = wt(seg, 'slip'), tw = wt(seg, 'walks');
  const himK = ease(prog(t, tw - 0.2, 1.4)), meK = ease(prog(t, ts - 0.2, 1.0));
  floorPlan(t, { checked: ['BATHROOM', 'GUEST ROOM'] });
  const g = roomC('GUEST ROOM'), b = roomC('BEDROOM'), c = roomC('CLOSET');
  ctx.save(); redGlow(16); circ(lerp(g[0], b[0], himK), g[1] - 40, 16, C.red); noGlow(); ctx.restore();
  const yx = lerp(c[0], g[0] + 60, meK), yy = lerp(c[1], g[1] + 40, meK); glow(); circ(yx, yy, 16, C.fig); noGlow();
  if (t >= ts + 0.8) pop(t, ts + 0.8, g[0] + 60, g[1] + 110, () => tag('YOU', g[0] + 60, g[1] + 120, C.fig, 30, 'center'), 0.3);
};
S.c6 = (t, seg) => {
  // he never checks a room twice
  const tt = wt(seg, 'twice');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.25, 1250, 350, () => {
    floorPlan(t, { checked: ['BATHROOM', 'GUEST ROOM', 'BEDROOM'] });
    const g = roomC('GUEST ROOM'); glow(); circ(g[0] + 60, g[1] + 40, 16, C.fig); noGlow();
    stampMark(t, tt - 0.1, g[0], g[1] - 60, [['CHECKED', 44]], -0.12, '#0f0f11', 20);
  });
};
S.c7 = (t, seg) => {
  // stay in the closet: the last thing you see through the slats is white
  const tw = wt(seg, 'white'), k = ease(prog(t, tw - 1.6, 2.2));
  slats(() => {
    ctx.fillStyle = '#2a2a31'; ctx.fillRect(-200, -200, W + 400, H + 400); rr(-200, 860, W + 400, 400, 0, '#24232a');
    if (k < 0.2) { const g = ctx.createRadialGradient(1500, 260, 20, 1500, 260, 900); g.addColorStop(0, 'rgba(170,190,230,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400); }
    const s = lerp(1.2, 6.5, k * k); ctx.save(); ctx.globalAlpha = 0.9; myers(960, 1040 + 520 * s * k * 0.9, s, { knife: 1, red: prog(t, seg.end + 0.5, 0.3), glowA: 0.15 }); ctx.restore();
  }, { gap: 30 });
};

// ---------- rule 4: never check if he is dead ----------
S.d0 = (t, seg) => ruleCard(t, seg, 4, "NEVER CHECK IF HE'S DEAD");
function floorTop() { ctx.fillStyle = '#0e0c0a'; ctx.fillRect(-200, -200, W + 400, H + 400); for (let i = -2; i < 16; i++) { ln(-200, i * 90, W + 200, i * 90, 3, '#1a1714'); for (let j = 0; j < 6; j++) ln(((i * 137 + j * 410) % 2300) - 200, i * 90, ((i * 137 + j * 410) % 2300) - 200, i * 90 + 90, 2, '#171411'); } }
S.d1 = (t, seg) => {
  // a hanger, a needle, your own knife. He falls.
  const th = wt(seg, 'hanger'), tn = wt(seg, 'needle'), tk = wt(seg, 'knife'), tf = wt(seg, 'falls');
  if (t < tf - 0.15) {
    black();
    [[th, 'hanger', 'COAT HANGER', 420], [tn, 'needle', 'KNITTING NEEDLE', 960], [tk, 'knife', 'KITCHEN KNIFE', 1500]].forEach(([t0, ic, s, x]) => { if (t >= t0 - 0.1) pop(t, t0 - 0.1, x, 470, () => {
      rr(x - 200, 300, 400, 340, 22, '#0f0f11'); rrS(x - 200, 300, 400, 340, 22, '#3a3a3e', 4); icon6(ic, x, 450, 1.3); text(s, x, 610, '900 30px M', C.fig); }, 0.3); });
  } else {
    black(); rr(-200, 900, W + 400, 300, 0, '#0e0c0a'); ln(-200, 900, W + 400, 900, 3, '#262320');
    const k = ease(prog(t, tf - 0.15, 0.55));
    myersSide(1000, 900, 1.15, { lean: k * Math.PI / 2 * 0.98, knife: 1 });
  }
};
S.d2 = (t, seg) => {
  // from above: he lies there, he does not move, the mask still on
  const tm = wt(seg, 'mask');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.35, 760, 540, () => {
    floorTop();
    ctx.save(); ctx.translate(1100, 540); ctx.rotate(Math.PI / 2); myers(0, 360, 1.2, { knife: 1 }); ctx.restore();
    if (t >= tm) pop(t, tm, 560, 330, () => tag('THE MASK IS STILL ON', 560, 340, C.fig, 30, 'center'), 0.3);
  });
};
S.d3 = (t, seg) => {
  // do not go closer, do not check his breathing, do not take the knife
  const tc = wt(seg, 'closer'), tb = wt(seg, 'breathing'), tk = wt(seg, 'take');
  ctx.save(); ctx.globalAlpha = 0.5; floorTop(); ctx.translate(1350, 560); ctx.rotate(Math.PI / 2); myers(0, 360, 1.2, { knife: 1 }); ctx.restore();
  listCard(120, 230, 960, 580);
  noRow(t, tc - 0.25, tc + 0.3, 180, 350, 'step', 'GO CLOSER', 46);
  noRow(t, tb - 0.25, tb + 0.3, 180, 520, 'breath', 'CHECK HIS BREATHING', 46);
  noRow(t, tk - 0.25, tk + 0.3, 180, 690, 'hand', 'TAKE THE KNIFE', 46);
};
function roomSide(t) {
  black(); rr(-200, 900, W + 400, 300, 0, '#0e0c0a'); ln(-200, 900, W + 400, 900, 3, '#262320');
  rr(-200, 0, W + 400, 900, 0, '#0b0b0d');
  rr(1640, 300, 230, 600, 2, '#020202'); rrS(1640, 300, 230, 600, 2, '#26262a', 8);    // the door out
}
S.d4 = (t, seg) => {
  // walk out backwards, eyes on him
  const tb = wt(seg, 'backwards'), te = wt(seg, 'eyes'), k = ease(prog(t, tb - 0.3, seg.end - tb + 0.6));
  roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: 0, knife: 1 });
  const x = lerp(1180, 1560, k); me(x, 900, 1.25, { face: 'left', walk: k > 0 && k < 1 ? -t * 8 : null });
  if (t >= te) { ctx.save(); ctx.setLineDash([14, 12]); const kk = ease(prog(t, te, 0.4)); ln(x - 20, 470, lerp(x - 20, 420, kk), lerp(470, 820, kk), 5, C.fig); ctx.restore(); pop(t, te, x, 280, () => tag('EYES ON HIM', x, 290, C.fig, 36, 'center'), 0.3); }
  if (t >= tb) { for (let i = 0; i < 3; i++) { const a = prog(t, tb + i * 0.15, 0.3); ctx.save(); ctx.globalAlpha *= a * 0.7; pth(`M${x + 100 + i * 40},842 l26,18 l-26,18 z`, C.fig); ctx.restore(); } }
};
S.d5 = (t, seg) => {
  // the moment you turn around
  const ta = wt(seg, 'around');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.0, 1.08, 1100, 600, () => {
    roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: 0, knife: 1 });
    me(1560, 900, 1.25, { face: t >= ta ? 'back' : 'left' });
  });
};
S.d6 = (t, seg) => {
  // behind you, very slowly, he sits up
  const ts = wt(seg, 'sits');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.08, 1.25, 900, 640, () => {
    roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: ease(prog(t, ts - 0.6, 2.4)), knife: 1, red: prog(t, ts + 1.6, 0.4) });
    me(1560, 900, 1.25, { face: 'back' });
  });
};
S.d7 = (t, seg) => {
  // he always gets back up: the mask rises into the frame
  const k = ease(prog(t, seg.start - 0.1, 1.6));
  black(); const g = ctx.createRadialGradient(960, 400, 50, 960, 500, 800); g.addColorStop(0, 'rgba(255,250,235,0.06)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  myers(960, lerp(3400, 2560, k), 3.6, { red: prog(t, seg.end + 0.2, 0.3) });
};

// ---------- emergency protocol ----------
S.e0 = (t, seg) => emergencyCard(t, seg);
S.e1 = (t, seg) => {
  // cornered: he stands in front of you, knife up
  const tw = wt(seg, 'work');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 1100, 560, () => {
    black(); rr(-200, 920, W + 400, 300, 0, '#0e0c0a'); pth('M1300,0 L1920,0 L1920,1080 L1300,920 Z', '#0d0d10'); ln(1300, 0, 1300, 920, 4, '#26262a');
    me(1560, 960, 1.4, { face: 'left', arms: [0.4, 0.4] });
    myers(820, 1020, 1.18, { knife: 2 });
  });
  if (t >= tw) pop(t, tw, 420, 160, () => tag('DOES NOT WORK', 420, 170, C.red, 50, 'center'), 0.3);
};
S.e2 = (t, seg) => {
  // six shots, he goes over the balcony; you look down: the lawn is empty
  const ts = wt(seg, 'six'), tb = wt(seg, 'balcony'), tl = wt(seg, 'look'), te = wt(seg, 'empty');
  if (t < tl - 0.1) {
    black();
    cam(t, seg.start, tl - seg.start, 1.0, 1.08, 1060, 520, () => {
      rr(440, 20, 1180, 480, 0, '#111214'); rrS(440, 20, 1180, 480, 0, '#26272b', 4);   // the back of the house, upstairs
      rr(600, 160, 220, 320, 2, '#050505');                                               // your bedroom door, open
      rr(860, 480, 640, 24, 0, '#2a2a2e'); for (let i = 0; i < 13; i++) rr(880 + i * 48, 380, 8, 100, 2, '#2a2a2e'); rr(860, 370, 640, 14, 3, '#2a2a2e');   // balcony, open at the right end
      rr(-200, 800, W + 400, 400, 0, '#121812'); for (let i = 0; i < 40; i++) ln(-100 + i * 55, 800, -90 + i * 55, 788, 3, '#1b231b');
      let hits = 0; for (let i = 0; i < 6; i++) if (t >= ts + i * 0.32) hits = i + 1;
      const fall = ease(prog(t, tb - 0.4, 0.7)), drop = prog(t, tb + 0.2, 0.5);
      if (drop < 1) { const x = 1180 + hits * 30 + fall * 200, y = lerp(480, 880, drop * drop);
        myersSide(x, y, 0.62, { dir: -1, lean: -(hits * 0.04 + fall * 0.5 + drop * 1.0), knife: 1 }); }
      else myersSide(1540, 880, 0.62, { dir: -1, floor: 1, sit: 0, knife: 1 });
      for (let i = 0; i < 6; i++) { const ft = ts + i * 0.32; if (t >= ft && t < ft + 0.1) { ctx.save(); glow('rgba(255,240,200,0.9)', 30); for (let r = 0; r < 8; r++) { const a = r * Math.PI / 4; ln(810, 330, 810 + Math.cos(a) * 40, 330 + Math.sin(a) * 40, 6, '#fff3d6'); } noGlow(); ctx.restore(); } }
      me(700, 500, 0.95, { face: 'right', arms: [0, 0.72] });
    });
  } else {
    // from above: the grass, the shape he left, and no one
    cam(t, tl - 0.1, seg.end - tl + 1, 1.0, 1.2, 960, 540, () => {
      ctx.fillStyle = '#0a0d0a'; ctx.fillRect(-200, -200, W + 400, H + 400);
      for (let i = 0; i < 260; i++) { const gx = hash(i * 1.3) * 2100 - 90, gy = hash(i * 2.9) * 1200 - 60; ln(gx, gy, gx + 4, gy - 14, 3, '#162016'); }
      ctx.save(); ctx.translate(960, 560); ctx.rotate(Math.PI / 2 - 0.2); ctx.setLineDash([12, 12]); ctx.globalAlpha = 0.6;
      pthS('M-60,-560 C-80,-520 -70,-470 -56,-450 L-120,-440 L-150,-300 L-90,-270 L-60,-20 L60,-20 L90,-270 L150,-300 L120,-440 L56,-450 C70,-470 80,-520 60,-560 C30,-600 -30,-600 -60,-560 Z', '#8a9a8a', 5); ctx.restore();
      if (t >= te) pop(t, te, 960, 160, () => tag('EMPTY', 960, 170, C.red, 52, 'center'), 0.3);
    });
  }
  noHead(t, seg, 'gun', 'SHOOT HIM', te + 0.3);
};
S.e3 = (t, seg) => {
  // you lock the door; the camera pulls back: he was already inside
  const tl = wt(seg, 'lock'), ti = wt(seg, 'inside'), k = ease(prog(t, ti - 0.6, 1.0));
  cam(t, 0, 1, lerp(1.7, 1.0, k), lerp(1.7, 1.0, k), 1420, 560, () => {
    black(); rr(-200, 920, W + 400, 300, 0, '#0e0c0a'); rr(1220, 220, 360, 700, 2, '#1d1d20'); rrS(1220, 220, 360, 700, 2, '#2e2e33', 6);
    rr(1260, 560, 40, 60, 8, '#55555a'); ctx.save(); ctx.translate(1280, 590); ctx.rotate(t >= tl ? Math.PI / 2 : 0); rr(-5, -20, 10, 40, 3, '#222'); ctx.restore();
    me(1440, 1000, 1.5, { face: 'back', arms: [0, 0.45] });
    myers(680, 1000, 1.25, { knife: 1, dark: 0.25 });
  });
  noHead(t, seg, 'lock', 'LOCK THE DOOR', ti + 0.2);
};
S.e4 = (t, seg) => {
  // drive: there is a white face in the back seat
  const tf = wt(seg, 'face');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, lerp(1.0, 1.9, 1), 960, 200, () => {});
  ctx.save(); const z = lerp(1.0, 2.2, ease(prog(t, tf - 1.0, 1.4))); ctx.translate(960, 200); ctx.scale(z, z); ctx.translate(-960, -200);
  carView(t, { face: ease(prog(t, tf - 0.4, 0.5)), red: prog(t, tf + 0.8, 0.3) }); ctx.restore();
  noHead(t, seg, 'car', 'DRIVE AWAY', tf + 0.4);
};
S.e5 = (t, seg) => {
  // scream: the neighbours step out, think it's a prank, and clap
  const ts = wt(seg, 'scream'), tn = wt(seg, 'neighbors'), tc = wt(seg, 'clap');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.06, 960, 560, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 700); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    [[280, 0], [960, 1], [1640, 2]].forEach(([x, i]) => { house(x, 640, 520, { win: [0.6, 0.4, 0.7, 0.5], porch: 1, pumpkins: 1, door: t >= tn + i * 0.2 ? 1 : 0 });
      if (t >= tn + i * 0.2 + 0.2) { const cl = t >= tc ? Math.abs(Math.sin((t - tc) * 9)) : 0; fadeIn(t, tn + i * 0.2 + 0.2, () => me(x - 30 + (i - 1) * 60, 646, 0.42, { face: 'front', arms: [0.45 + cl * 0.15, 0.45 + cl * 0.15] }), 0.3);
        if (t >= tc) { ctx.save(); ctx.globalAlpha = 0.7 * (0.5 + 0.5 * Math.sin((t - tc) * 18)); text('CLAP', x - 30 + (i - 1) * 60, 470, '900 26px M', C.fig); ctx.restore(); } } });
    rr(-200, 640, W + 400, 500, 0, NIGHT.street); rr(-200, 900, W + 400, 300, 0, NIGHT.grass);
    me(700, 1000, 1.0, { face: 'front', arms: [0.8, 0.8] });
    if (t >= ts) for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha = 0.6 * (1 - ((t - ts) * 1.2 + i / 3) % 1); ctx.beginPath(); ctx.arc(700, 640, 80 + (((t - ts) * 1.2 + i / 3) % 1) * 200, -2.4, -0.7); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); }
    myers(1200, 1000, 0.95, { knife: 2 });
  });
  noHead(t, seg, 'scream', 'SCREAM', tc + 0.3);
};
S.e6 = (t, seg) => {
  // only one thing works
  black(); const g = ctx.createRadialGradient(960, 520, 20, 960, 520, 500); g.addColorStop(0, 'rgba(255,255,255,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  pop(t, seg.start, 960, 500, () => { rr(780, 330, 360, 360, 26, '#0f0f11'); rrS(780, 330, 360, 360, 26, C.fig, 6); check(960, 510, 90, prog(t, wt(seg, 'works'), 0.4)); }, 0.35);
  if (t >= wt(seg, 'one')) pop(t, wt(seg, 'one'), 960, 800, () => spaced('ONLY ONE THING WORKS', 960, 810, '900 50px M', C.fig, 6), 0.3);
};
S.e7 = (t, seg) => {
  // say his name
  black(); ctx.save(); ctx.globalAlpha = 0.2; maskHead(960, 520, 5.2, { glowA: 0.1 }); ctx.restore();
  pop(t, seg.start, 960, 540, () => spaced('SAY HIS NAME.', 960, 570, '900 120px M', C.fig, 10), 0.35);
};
S.e8 = (t, seg) => {
  // "Michael." The knife is up.
  cam(t, seg.start, 2.2, 1.0, 1.06, 960, 500, () => { black(); myers(1380, 1900, 2.3, { knife: 2, dark: 0.2 }); });
  ctx.save(); ctx.globalAlpha = 0.8; ctx.fillStyle = '#000'; ctx.fillRect(0, 380, 1100, 300); ctx.restore();
  fadeIn(t, wt(seg, 'michael') - 0.05, () => spaced('MICHAEL.', 560, 580, '900 150px M', C.fig, 14), 0.4);
};
S.e9 = (t, seg) => {
  // six years old; and the knife stops in the air
  const t6 = wt(seg, 'six'), tk = wt(seg, 'knife');
  if (t < tk - 0.1) {
    cam(t, seg.start, tk - seg.start, 1.0, 1.1, 960, 600, () => {
      black(); const g = ctx.createRadialGradient(960, 700, 20, 960, 700, 600); g.addColorStop(0, 'rgba(255,255,255,0.06)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      rr(-200, 900, W + 400, 300, 0, '#0c0c0e');
      me(960, 900, 0.95, { face: 'front' }); pth('M920,602 L1000,602 L960,505 Z', C.sec); circ(960, 500, 8, C.sec);   // a small boy in a costume hat
      if (t >= t6) pop(t, t6, 960, 320, () => tag('AGE 6', 960, 330, C.fig, 52, 'center'), 0.3);
    });
  } else {
    cam(t, tk - 0.1, seg.end - tk + 1, 1.3, 1.36, 760, 380, () => { black(); myers(1180, 1900, 2.3, { knife: 2 }); });
    const fx = 760, fy = 250; for (let i = 0; i < 4; i++) { const a = -0.6 + i * 0.4; ln(fx + Math.cos(a) * 170, fy + Math.sin(a) * 170, fx + Math.cos(a) * 230, fy + Math.sin(a) * 230, 6, C.fig); }
    pop(t, wt(seg, 'stops'), 420, 420, () => tag('STOPPED', 420, 430, C.fig, 50, 'center'), 0.3);
  }
};
S.e10 = (t, seg) => {
  // say it again, like his mother: calm, tired
  const tc = wt(seg, 'calm'), tt = wt(seg, 'tired');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 560, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
    myers(620, 1000, 1.35, { knife: 2 });
    me(1340, 1000, 1.45, { face: 'left' });
  });
  if (t >= tc) pop(t, tc, 1350, 200, () => tag('CALM.', 1250, 210, C.fig, 50, 'center'), 0.3);
  if (t >= tt) pop(t, tt, 1560, 200, () => tag('TIRED.', 1560, 210, C.fig, 50, 'center'), 0.3);
};
S.e11 = (t, seg) => {
  // "Michael. Go home."
  const tg = wt(seg, 'go');
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.05, 960, 540, () => { black(); ctx.save(); ctx.globalAlpha = 0.35; myers(1500, 1900, 2.3, { knife: 2, tilt: -0.2 * ease(prog(t, seg.end, 0.8)) }); ctx.restore(); });
  spaced('MICHAEL.', 760, 470, '900 110px M', C.fig, 12);
  if (t >= tg - 0.05) pop(t, tg - 0.05, 760, 640, () => spaced('GO HOME.', 760, 660, '900 130px M', C.fig, 12), 0.35);
};
S.e12 = (t, seg) => {
  // he tilts his head, and lowers the knife
  const tt = wt(seg, 'tilts'), tl = wt(seg, 'lowers');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 960, 520, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
    myers(960, 1260, 1.9, { knife: 2, tilt: -0.3 * ease(prog(t, tt, 1.0)), lower: ease(prog(t, tl, 1.0)) });
  });
};
S.e13 = (t, seg) => {
  // out of your house, across the street, into the empty house on the corner
  const tn = wt(seg, 'nobody'), te = wt(seg, 'empty'), k = prog(t, seg.start + 0.2, te - seg.start + 0.4);
  const path = [[640, 1040, 0.9], [900, 900, 0.72], [1180, 720, 0.52], [1560, 650, 0.44], [1835, 600, 0.4]];
  const n = Math.min(path.length - 2, Math.floor(k * (path.length - 1))), f = k * (path.length - 1) - n;
  const p = path[n].map((v, i) => lerp(v, path[n + 1][i], f));
  const inside = k >= 1;
  streetScene(t, { cam: [1.15, 1200, 560], him: null, mailbox: false,
    houses: [[-120, 0.5, [0, 0.8, 0.6, 0]], [340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]]],
    emptyHouse: () => house(1860, 600, 420, { old: true, chimney: false, door: k > 0.9 && t < te + 1.0 ? 1 : 0 }),
    near: () => { if (!inside) myersSide(p[0], p[1], p[2], { walk: t * 3.2, knife: 1, dir: 1 });
      if (t >= tn) pop(t, tn, 1860, 300, () => tag('EMPTY FOR YEARS', 1860, 310, C.fig, 28, 'center'), 0.3); } });
};
S.e14 = (t, seg) => {
  // do not follow, do not watch which window
  const tf = wt(seg, 'follow'), tw = wt(seg, 'watch');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.06, 960, 520, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 900); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(1180, 920, 1000, { old: true, chimney: false }); rr(-200, 920, W + 400, 300, 0, NIGHT.grass);
  });
  listCard(60, 300, 560, 400);
  noRow(t, tf - 0.25, tf + 0.3, 100, 410, 'step', 'FOLLOW HIM', 40);
  noRow(t, tw - 0.25, tw + 0.3, 100, 590, 'eye', 'WATCH WINDOWS', 40);
};

// ---------- the morning, and every Halloween after ----------
S.f1 = (t, seg) => {
  // grey morning: smashed pumpkins, wrappers, police tape
  ctx.save(); streetScene(t, { cam: [1.25, 900, 600], him: null, morning: true, light: 0, dimHouses: true, houses: [[-120, 0.5, [0, 0, 0, 0]], [340, 0.48, [0, 0, 0, 0]], [800, 0.5, [0, 0, 0, 0]], [1300, 0.52, [0, 0, 0, 0]], [1820, 0.5, [0, 0, 0, 0]]],
    near: () => { for (let i = 0; i < 22; i++) { const x = hash(i * 4.1) * 1800, y = 650 + hash(i * 6.3) * 140; ctx.save(); ctx.translate(x, y); ctx.rotate(hash(i) * 3); rr(-10, -5, 20, 10, 2, i % 3 ? '#5a5a5a' : '#8a8a8a'); ctx.restore(); }
      jackO(560, 830, 30, 0, true); jackO(1320, 836, 26, 0, true); } });
  ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(70,75,85,0.35)'; ctx.fillRect(0, 0, W, H); ctx.restore();   // grey dawn
  if (t >= wt(seg, 'police')) { const k = ease(prog(t, wt(seg, 'police') - 0.1, 0.4)); ctx.save(); ctx.translate(960, 760); ctx.rotate(-0.08); ctx.globalAlpha = k; rr(-1100, -30, 2200, 60, 0, '#d8d8d8');
    ctx.beginPath(); ctx.rect(-1100, -30, 2200, 60); ctx.clip(); for (let i = -10; i < 10; i++) text('POLICE LINE  DO NOT CROSS', i * 520 + ((t * 30) % 520), 14, '900 32px M', '#111', 'left'); ctx.restore(); }
};
S.f2 = (t, seg) => {
  // your knife is back in the block, clean
  const tb = wt(seg, 'back'), k = ease(prog(t, tb - 0.4, 0.7)), tc = wt(seg, 'clean');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 880, 640, () => {
    black(); ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(120,130,150,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
    rr(-200, 960, W + 400, 300, 0, '#1a1a1d');
    blockClose(t, { x: 900, y: 1010, s: 1.5, out: k < 1 ? [0, 260 * (1 - k)] : null, fade: k });
    // (the handle slides back in: blockClose draws it pulled out)
    if (t >= tc) { const gx = 640, gy = 330, a = 1 - prog(t, tc + 0.4, 0.6); ctx.save(); ctx.globalAlpha = a; glow('rgba(255,255,255,1)', 30); for (let i = 0; i < 4; i++) { const an = i * Math.PI / 2; ln(gx, gy, gx + Math.cos(an) * 40, gy + Math.sin(an) * 40, 5, '#fff'); } noGlow(); ctx.restore();
      pop(t, tc, 1300, 300, () => tag('CLEAN', 1300, 310, C.fig, 50, 'center'), 0.3); }
  });
};
const inWindow = (o = {}) => (x, y, w, h) => { ctx.fillStyle = '#020202'; ctx.fillRect(x, y, w, h); const s = h * 0.5 / 150; myers(x + w / 2, y + h * 0.42 + 563 * s, s, o); };
S.f3 = (t, seg) => {
  // every Halloween since: he stands in the dark window of the empty house
  const th = wt(seg, 'halloween'), tl = wt(seg, 'looks');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.12, 1100, 420, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 900); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(1100, 960, 1000, { old: true, chimney: false, who: { win: 1, fn: inWindow({}) } }); rr(-200, 960, W + 400, 300, 0, NIGHT.grass);
    if (t >= tl) { ctx.save(); ctx.setLineDash([14, 12]); const k = ease(prog(t, tl, 0.6)); ln(1355, 520, lerp(1355, 300, k), lerp(520, 980, k), 5, C.fig); ctx.restore(); }
  });
  if (t >= th) { const n = Math.min(3, 1 + Math.floor((t - th) / 0.5)); pop(t, th, 300, 260, () => { rr(180, 140, 240, 250, 16, '#e6e6e6'); rr(180, 140, 240, 70, 16, '#d61f1f'); text('OCT', 300, 196, '900 40px M', '#fff'); text('31', 300, 330, '900 110px M', '#111');
    text(n === 1 ? '1 YEAR' : n + ' YEARS', 300, 450, '900 34px M', C.fig); }, 0.3); }
};
S.f4 = (t, seg) => {
  // he never comes over; he listens to his mother
  const to = wt(seg, 'over'), tm = wt(seg, 'mother');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.05, 960, 520, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 800); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(420, 700, 620, { old: true, chimney: false, who: { win: 1, fn: inWindow({}) } });
    house(1500, 700, 620, { win: [0.9, 0.6, 0.4, 0], porch: 1, pumpkins: 1 });
    rr(-200, 700, W + 400, 140, 0, NIGHT.street); rr(-200, 840, W + 400, 300, 0, NIGHT.grass);
    if (t >= to) { ctx.save(); ctx.setLineDash([16, 12]); const k = ease(prog(t, to, 0.5)); ln(560, 760, lerp(560, 1360, k), 760, 6, C.fig); ctx.restore(); redX(960, 760, 50, prog(t, to + 0.5, 0.3)); }
  });
  if (t >= tm) pop(t, tm, 960, 160, () => tag('HE LISTENS TO HIS MOTHER', 960, 170, C.fig, 40, 'center'), 0.3);
};
S.f5 = (t, seg) => {
  // this year, for the first time, he raises his hand
  const th = wt(seg, 'raises'), k = ease(prog(t, th - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.15, 960, 500, () => {
    black(); rr(560, 140, 800, 760, 4, '#030303');
    ctx.save(); ctx.beginPath(); ctx.rect(560, 140, 800, 760); ctx.clip(); myers(960, 1640, 2.0, { wave: k * 0.75 }); ctx.restore();
    rrS(560, 140, 800, 760, 4, '#2a2a2d', 26); ln(500, 230, 860, 120, 26, '#2b2622'); ln(1080, 900, 1420, 780, 26, '#2b2622');   // a board across each corner
  });
};
S.f6 = (t, seg) => {
  // he is waving
  cam(t, seg.start - 0.1, seg.end - seg.start + 1.6, 1.15, 1.22, 960, 500, () => {
    black(); rr(560, 140, 800, 760, 4, '#030303');
    ctx.save(); ctx.beginPath(); ctx.rect(560, 140, 800, 760); ctx.clip(); myers(960, 1640, 2.0, { wave: 1, waveT: t - seg.start }); ctx.restore();
    rrS(560, 140, 800, 760, 4, '#2a2a2d', 26); ln(500, 230, 860, 120, 26, '#2b2622'); ln(1080, 900, 1420, 780, 26, '#2b2622');
  });
};
S.f7 = (t, seg) => {
  // do not wave back: your hand comes up, and stops
  const tw = wt(seg, 'wave'), k = ease(prog(t, seg.start, 1.0));
  lookOut(t, { z: 1.9, f: [1700, 470], him: null, houses: [[340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]]],
    emptyHouse: () => house(1860, 600, 420, { old: true, chimney: false, who: { win: 1, fn: inWindow({ wave: 1, waveT: t }) } }) });
  ctx.save(); ctx.translate(800, lerp(1400, 860, k)); glow('rgba(255,255,255,0.25)', 16); rr(-80, 0, 160, 220, 50, C.fig); for (let i = 0; i < 4; i++) rr(-80 + i * 42, -150 + Math.abs(i - 1.5) * 18, 34, 170, 17, C.fig); rr(-150, 20, 40, 130, 20, C.fig); ctx.restore(); noGlow();
  if (t >= tw) redX(800, 820, 190, prog(t, tw, 0.35));
};
// the file closes
S.f8 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
// sign-off: the rules once more, the stamp, and the picture sinks into the dark around it
S.f9 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9, -9], fillT: [-9, -9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.95 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
