// ---------- EP03 scenes: "If Your Reflection Ever Tells You To RUN" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
// a bathroom shot with a slow 2D push toward a point in the world (the push is a narrower lens: it changes nothing in the geometry)
function shot(t, t0, d, z0, z1, focus, o) {
  setCam(o.cam || CAMS.ots); const f = prj(focus) || [W / 2, H / 2];
  cam(t, t0, d, z0, z1, f[0], f[1], () => bathroom(t, o));
}
const GLASS_C = [0, 1.52, 0];
const sideTag = (t, t0, s, x, y, col = C.fig, size = 50) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
// poses
const wave = (t, k = 1) => ({ R: [lerp(0.24, 0.32 + 0.07 * Math.sin(t * 9), k), lerp(0.9, 1.74, k), lerp(0.04, 0.14, k)] });
const washing = (t, k = 1) => ({ ...WASH, L: [-0.07 + 0.025 * Math.sin(t * 8) * k, 0.98, 0.42], R: [0.07 - 0.025 * Math.sin(t * 8) * k, 0.98, 0.42] });
// your reflection, writing on the glass from its side: it stands closer, leans in, one finger on the glass at tip (glass coords)
function writerPose(tip, k = 1) { const x = ME.x + 0.17 * k, z = 0.55; return poseOf({ x, z, lean: 0.22 * k, R: tip ? [lerp(0.24, tip[0] - x, k), lerp(0.9, tip[1] - 0.04, k), lerp(0.04, z - 0.08, k)] : STAND.R }); }
function reflFinger(p, tip, k = 1) { if (!tip || k < 0.9) return; const h = MIRROR(skeleton(p).hand.R), a = prj(h), b = prj([tip[0], tip[1], 0]);
  if (a && b) { ctx.save(); glow('rgba(255,255,255,0.25)', 10); ln(a[0], a[1], b[0], b[1], 0.024 * a[3], '#dcdcde'); ctx.restore(); } }
// an open hand flat on the glass, at glass point g; back: seen from the back (yours) or the palm (its)
function palmOn(g, col, z = 0.01, mirror = false) {
  const c = prj([g[0], g[1], z]); if (!c) return; const s = c[3];
  ctx.save(); glow('rgba(255,255,255,0.25)', 12); ell(c[0], c[1], 0.045 * s, 0.055 * s, 0, col);
  const fs = mirror ? -1 : 1;
  for (let i = 0; i < 4; i++) { const a = -Math.PI / 2 + (i - 1.5) * 0.24 * fs; ln(c[0] + Math.cos(a) * 0.04 * s, c[1] + Math.sin(a) * 0.04 * s, c[0] + Math.cos(a) * (0.1 + (i === 1 || i === 2 ? 0.015 : 0)) * s, c[1] + Math.sin(a) * (0.1 + (i === 1 || i === 2 ? 0.015 : 0)) * s, 0.02 * s, col); }
  ln(c[0] - fs * 0.04 * s, c[1] + 0.01 * s, c[0] - fs * 0.085 * s, c[1] - 0.03 * s, 0.022 * s, col);   // thumb
  ctx.restore();
}

// ---------- white icons ----------
function icon3(name, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'wipe') { rrS(-80, -90, 160, 180, 8, C.fig, 9); ctx.globalAlpha *= 0.5; for (let i = 0; i < 3; i++) pthS(`M${-50},${-40 + i * 34} q50,-24 100,0`, C.fig, 8); ctx.globalAlpha = 1; ell(30, 40, 26, 32, -0.3, C.fig); }
  if (name === 'ask') { rrS(-96, -70, 192, 120, 26, C.fig, 10); pth('M-50,48 L-70,94 L-14,50 Z', C.fig); text('?', 0, 20, '900 100px M', C.fig); }
  if (name === 'turn') { ctx.beginPath(); ctx.arc(0, 0, 70, -Math.PI * 0.2, Math.PI * 1.25); ctx.lineWidth = 14; ctx.strokeStyle = C.fig; ctx.stroke(); pth('M44,-78 L92,-40 L34,-24 Z', C.fig); circ(0, 0, 18, C.fig); }
  noGlow(); ctx.restore();
}
// small dark pictograms on the rule page
const _pageIcon = pageIcon;
pageIcon = function (name, x, y, col = '#111') {
  if (name === 'mirror') { ctx.save(); ctx.translate(x, y); rrS(-34, -50, 68, 92, 6, col, 6); circ(0, -14, 12, col); rr(-14, 0, 28, 30, 8, col); ln(-12, 54, 12, 54, 6, col); ctx.restore(); return; }
  if (name === 'run') { ctx.save(); ctx.translate(x, y); circ(10, -40, 11, col); poly([[4, -26], [-6, 8]], 12, col); poly([[-6, 8], [14, 26], [8, 48]], 10, col); poly([[-6, 8], [-22, 28], [-40, 30]], 10, col); poly([[0, -18], [22, -6], [34, -18]], 9, col); poly([[0, -18], [-18, -6], [-30, 4]], 9, col); ctx.restore(); return; }
  return _pageIcon(name, x, y, col);
};

// ---------- hook ----------
const RUN_END = (() => { const s = runStrokes(); const l = s[s.length - 1].pts; return l[l.length - 1]; })();
S.h1 = (t, seg) => {
  const tn = wt(seg, 'not'), tr = wt(seg, 'run');
  // frame 0: the word is already there, written from the other side; your reflection's finger is still on the last stroke, and behind it the doorway is not empty
  const rp = writerPose(RUN_END);
  shot(t, 0, seg.end + 0.6, 1.0, 1.1, GLASS_C, { me: poseOf({}), refl: rp, door: 1, thing: { x: 0.3, z: -3.12, t, inDoor: true }, fog: 0.85, run: [1, 1, 1], drip: 0.4 + 0.6 * prog(t, 0, 5),
    inMirror: () => reflFinger(rp, RUN_END) });
  if (t >= tn) pop(t, tn, 1500, 250, () => tag('DO NOT LOOK BACK', 1500, 260, C.red, 54, 'center'), 0.3);
};
// the three "do not"s as a teaser: each one is done anyway, you see what happens, then black
function h2Windows(seg) { return [[seg.start, wt(seg, 'do', 2), 'wipe', 'wipe', 200], [wt(seg, 'do', 2), wt(seg, 'do', 3), 'ask', 'ask', 770], [wt(seg, 'do', 3), nextStart(seg), 'turn', 'turn', 200]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 960, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.82; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon3(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {
      // you wipe the fog away. Behind the glass, where your face should be, it is waiting; its hand hits the glass
      const k = prog(t, w0 + 0.2, hit - w0 - 0.3), wipe = [];
      for (let n = 0; n < 14; n++) { const u = n / 13; if (u > k) break; wipe.push([lerp(-0.25, 0.25, (Math.sin(u * 9) + 1) / 2) + 0.02, 1.45 + u * 0.22, 0.11]); }
      const tip = wipe.length ? wipe[wipe.length - 1] : [0, 1.45];
      const me = poseOf({ lean: 0.18, R: [tip[0] - ME.x, tip[1] - 0.02, ME.z - 0.06] });
      shot(t, w0, blk - w0, 1.15, 1.45, [0.0, 1.55, 0], { me, reflOff: true, door: 1, fog: 0.9, wipe,
        behind: () => thing3(0.0, -0.32, { t, sc: 0.84, col: '#a2a2a8' }),
        glassFx: () => { if (d > -0.05) { palmOn([0.12, 1.5], '#a2a2a8', -0.005, true); glassRipple([0.12, 1.5, 0], hit, t); } } });
      if (d > 0 && d < 0.07) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    } else if (i === 1) {
      // you ask it why. It answers by turning red
      const r = ease(prog(t, w0 + 0.9, hit - w0 - 0.9));
      shot(t, w0, blk - w0, 1.1, 1.5, [ME.x, 1.6, -ME.z], { me: poseOf({}), door: 1, reflCol: `rgb(${Math.round(lerp(220, 235, r))},${Math.round(lerp(220, 30, r))},${Math.round(lerp(222, 30, r))})`,
        glassFx: () => { if (r > 0) { ctx.save(); ctx.globalAlpha = 0.35 * r; ctx.fillStyle = '#ff1a1a'; ctx.fillRect(-W, -H, 3 * W, 3 * H); ctx.restore(); } } });
      const hp = prj(skeleton(poseOf({})).head);
      if (hp) bubbleTo(hp[0] + 150, hp[1] - 190, 150, 110, '?', t, w0 + 0.25, hp[0] + 60, hp[1] - 60);
      if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.5 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    } else {
      // you turn around. Behind you, in the glass, it steps up to your reflection and takes it
      const k = ease(prog(t, w0 + 0.2, 0.7)), c = ease(prog(t, w0 + 0.5, hit - w0 - 0.5));
      const me = poseOf({ yaw: Math.PI * k });
      shot(t, w0, blk - w0, 1.05, 1.5, [ME.x, 1.6, -ME.z], { me, refl: poseOf({}), door: 1,
        thing: { x: lerp(0.3, ME.x + 0.12, c), z: lerp(-3.12, -ME.z - 0.45, c), t, inDoor: c < 0.05 },
        inMirror: () => { if (c > 0.8) { const j = skeleton(poseOf({})); for (const s of ['L', 'R']) fingers3(MIRROR(V3.add(j.sh[s], [0, 0.03, 0])), [0, -1, 0], '#9a9a9f', 0.15); } } });
      if (d > 0 && d < 0.08) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.55; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    }
  }
  if (t >= blk) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not test your reflection ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT TEST YOUR REFLECTION');
S.a1 = (t, seg) => {
  const tw = wt(seg, 'washing');
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.1, GLASS_C, { me: poseOf(washing(t, prog(t, tw - 0.4, 0.4))), water: prog(t, tw - 0.6, 0.3), door: 0, light: 0.85 + 0.15 * (hash(Math.floor(t * 12)) > 0.08 ? 1 : 0) });
  if (t >= seg.start + 0.6) slideIn(t, seg.start + 0.6, 40, 0, () => { ctx.save(); redGlow(10); text('3:00 AM', 1560, 200, '700 54px Plex', C.red); ctx.restore(); });
};
// you look up; your reflection a moment later
const lookUp = (t, t0) => ({ ...WASH, look: 1 - ease(prog(t, t0, 0.4)), lean: 0.2 * (1 - ease(prog(t, t0, 0.4))) });
S.a2 = (t, seg) => {
  const tu = wt(seg, 'up'), tm = wt(seg, 'moment'), lag = 0.9;
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.6, [ME.x, 1.6, -ME.z], { me: poseOf(lookUp(t, tu)), refl: poseOf(lookUp(t - lag, tu)), water: 1 - prog(t, tu, 0.3) });
  if (t >= tm) pop(t, tm, 1480, 300, () => tag('A MOMENT LATER', 1480, 310, C.red, 50, 'center'));
};
S.a3 = (t, seg) => {
  // two tracks: when you move, and when it moves
  const t0 = seg.start, tt = wt(seg, 'tired');
  cam(t, t0, seg.end - t0 + 0.8, 1, 1.04, W / 2, 500, () => {
    const x0 = 420, x1 = 1500, y = [400, 600];
    [['YOU', C.fig], ['REFLECTION', C.sec]].forEach(([l, c], i) => { slideIn(t, t0 + i * 0.1, -40, 0, () => { text(l, x0 - 30, y[i] + 12, '900 40px M', c, 'right'); lnP(x0, y[i], x1, y[i], 5, C.dim, easeOut(prog(t, t0, 0.6))); }); });
    const mx = 880, lagX = 1080, k = prog(t, t0 + 0.4, 0.5), k2 = prog(t, t0 + 1.0, 0.5);
    if (k > 0) pop(t, t0 + 0.4, mx, y[0], () => { glow(); circ(mx, y[0], 26, C.fig); noGlow(); });
    if (k2 > 0) pop(t, t0 + 1.0, lagX, y[1], () => { glow(); circ(lagX, y[1], 26, C.sec); noGlow(); });
    if (t >= t0 + 1.3) { ctx.save(); ctx.setLineDash([10, 9]); ln(mx, y[0] + 30, mx, y[1] + 40, 3, C.mid); ctx.restore(); redGlow(10);
      lnP(mx, y[1] + 70, lagX, y[1] + 70, 6, C.red, easeOut(prog(t, t0 + 1.3, 0.4))); noGlow();
      fadeIn(t, t0 + 1.5, () => text('0.9 s', (mx + lagX) / 2, y[1] + 130, '900 52px M', C.red)); }
    if (t >= tt) pop(t, tt, 960, 230, () => tag('JUST TIRED?', 960, 240, C.fig, 50, 'center'));
  });
};
// a crossed-out action: the label in its box with a red X beside it (never over the words)
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
S.a4 = (t, seg) => {
  const tw = wt(seg, 'wave'), tt = wt(seg, 'tilt'), lag = 0.9;
  const pose = u => poseOf({ ...wave(u, prog(u, tw - 0.2, 0.3) * (1 - prog(u, tt - 0.5, 0.3))), roll: Math.sin(clamp((u - tt) / 1.2) * Math.PI) * 1.0 });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.3, [ME.x, 1.55, -ME.z], { me: pose(t), refl: pose(t - lag) });
  if (t >= tw + 0.2) slideIn(t, tw + 0.2, 40, 0, () => { xTag('DO NOT WAVE', 1460, 300, 48, prog(t, tw + 0.5, 0.3)); });
  if (t >= tt + 0.2) slideIn(t, tt + 0.2, 40, 0, () => { xTag('DO NOT TILT', 1460, 430, 48, prog(t, tt + 0.5, 0.3)); });
};
// every test: it falls further behind
const lagA5 = (t, seg) => { const t1 = wt(seg, 'one'), t2 = wt(seg, 'two'), t3 = wt(seg, 'three');
  if (t < t1) return lerp(0.9, 1, prog(t, seg.start, t1 - seg.start)); if (t < t2) return lerp(1, 2, (t - t1) / (t2 - t1)); if (t < t3) return lerp(2, 3, (t - t2) / (t3 - t2)); return 3; };
S.a5 = (t, seg) => {
  const t1 = wt(seg, 'one');
  const pose = u => poseOf({ ...wave(u, prog(u, seg.start + 0.1, 0.3)) });
  const lag = lagA5(t, seg);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, [ME.x, 1.55, -ME.z], { me: pose(t), refl: poseOf({ ...wave(t - lag, prog(t - lag, seg.start + 0.1, 0.3)) }) });
  if (t >= t1 - 0.1) fadeIn(t, t1 - 0.1, () => { spaced('BEHIND BY', 1500, 330, '900 34px M', C.mid, 6); ctx.save(); redGlow(14); text(lag.toFixed(1) + ' s', 1500, 450, '900 110px M', C.red); ctx.restore(); });
};
// it is not slow: long grey fingers over its shoulders, from behind
function heldBack(j, k = 1) { if (k <= 0) return; ctx.save(); ctx.globalAlpha *= k; for (const s of ['L', 'R']) { const sp = MIRROR(V3.add(j.sh[s], [0, 0.03, 0])); fingers3(sp, [0, -1, 0.3], '#9a9a9f', 0.16); } ctx.restore(); }
S.a6 = (t, seg) => {
  const ts = wt(seg, 'something'), th = wt(seg, 'holding'), rp = poseOf({ ...wave(t - 3, 1) });
  const frozen = poseOf({ ...wave(seg.start - 3, 1) });   // it has stopped
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.3, 1.9, [ME.x, 1.5, -ME.z], { me: poseOf({}), refl: frozen,
    inMirror: () => heldBack(skeleton(frozen), prog(t, ts, 0.8)) });
  if (t >= th) pop(t, th, 1500, 800, () => tag('HOLDING IT BACK', 1500, 810, C.red, 50, 'center'));   // low on the dark door, clear of the frame and the raised arm
};
// what would happen: it stops, it is covered and pulled back into the dark, and the thing takes its place at the glass
S.a7 = (t, seg) => {
  const gr = evAfter('grab', seg.end), wh = evAfter('whoosh', seg.end), sl = evAfter('slam', seg.end);
  const tg = gr ? gr.t : seg.end + 0.75, tw = wh ? wh.t : seg.end + 1.15, ts = sl ? sl.t : seg.end + 1.85;
  const stop = seg.start + 1.2, pose = u => poseOf({ ...wave(u, prog(u, seg.start, 0.3)) });
  const rp = pose(Math.min(t - 1.5, stop)), pull = ease(prog(t, tw, 0.45));
  const rz = lerp(ME.z, 3.0, pull);   // its distance behind the glass as it is dragged away
  shot(t, seg.start, ts - seg.start + 0.3, 1.1, 1.35, [ME.x, 1.55, -ME.z], { me: pose(t), door: 1,
    refl: { ...rp, z: rz, x: lerp(rp.x, 0.0, pull) }, reflOff: pull > 0.98,
    thing: t >= ts - 0.12 ? { x: ME.x + 0.05, z: lerp(-1.2, -0.25, prog(t, ts - 0.12, 0.12)), t, sc: 0.86, col: '#a8a8ae' } : null,
    inMirror: () => { if (t >= tg && pull < 0.98) { const j = skeleton({ ...rp, z: rz, x: lerp(rp.x, 0.0, pull) }); const hp = prj(MIRROR(j.head));
      if (hp) { ctx.save(); glow('rgba(255,255,255,0.2)', 12); ell(hp[0] - 0.02 * hp[3], hp[1], 0.1 * hp[3], 0.07 * hp[3], 0.2, '#9a9a9f'); fingers3(MIRROR(V3.add(j.head, [0.06, 0, -0.08])), [-1, -0.2, 0], '#9a9a9f', 0.14); ctx.restore(); } } },
    glassFx: () => { if (t >= ts) { palmOn([ME.x + 0.2, 1.42], '#a8a8ae', -0.005, true); glassRipple([ME.x + 0.2, 1.42, 0], ts, t); } } });
  if (t >= ts && t < ts + 0.07) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};

// ---------- rule 2: do not look behind your reflection ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LOOK BEHIND YOUR REFLECTION');
S.b1 = (t, seg) => {
  // turned around for a moment: the door behind you, closed
  const tc = wt(seg, 'closed');
  setCam(CAMS.rev); const f = prj([0, 1.2, ROOM.z1]);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.12, f[0], f[1], () => bathroom(t, { cam: CAMS.rev, me: poseOf({}), realDoor: 0 }));
  if (t >= tc) pop(t, tc, 1480, 280, () => tag('CLOSED', 1480, 290, C.fig, 56, 'center'));
};
const DOOR_C = [0.25, 1.15, -ROOM.z1];
S.b2 = (t, seg) => {
  const to = wt(seg, 'open'), op = ease(prog(t, seg.start + 0.3, 1.4));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.45, DOOR_C, { me: poseOf({}), door: op });
  if (t >= to) pop(t, to, 1480, 280, () => tag('OPEN', 1480, 290, C.red, 60, 'center'));
};
S.b3 = (t, seg) => {
  const tl = wt(seg, 'tall'), tn = wt(seg, 'thin'), tt = wt(seg, 'touches');
  const vis = ease(prog(t, seg.start, 1.6));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.6, 2.2, [0.25, 1.3, -ROOM.z1], { me: poseOf({}), door: 1, thing: { x: 0.3, z: -3.12, t, inDoor: true, col: `rgba(154,154,159,${vis})` } });
  if (t >= tl) pop(t, tl, 1500, 260, () => tag('TALL', 1500, 270, C.fig, 56, 'center'));
  if (t >= tn) pop(t, tn, 1500, 390, () => tag('TOO THIN', 1500, 400, C.fig, 56, 'center'));
  if (t >= tt) { setCam(CAMS.ots); const p = prj([0.25, DOOR.h, -ROOM.z1]); if (p) { ctx.save(); const z = lerp(1.6, 2.2, ease((t - seg.start) / (seg.end - seg.start + 0.8))), fc = prj([0.25, 1.3, -ROOM.z1]);
      const x = fc[0] + (p[0] - fc[0]) * z, y = fc[1] + (p[1] - fc[1]) * z; redGlow(14); ctx.setLineDash([12, 9]); ctx.beginPath(); ctx.arc(x, y, 70 * prog(t, tt, 0.3) + 1, 0, Math.PI * 2); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); } }
};
// the floor plan, from above. The glass is the vertical line in the middle: your room on the right, the room in the mirror on the left
const PL = { cx: 960, cy: 500, s: 190 };
const pl = (x, z) => [PL.cx + z * PL.s, PL.cy - x * PL.s];
function planRoom(m, o = {}) {
  const sg = m ? -1 : 1, a = pl(ROOM.x1, 0), b = pl(ROOM.x0, sg * ROOM.z1);
  ctx.save(); if (m) { ctx.setLineDash([12, 10]); ctx.globalAlpha *= 0.85; }
  const x0 = Math.min(a[0], b[0]), x1 = Math.max(a[0], b[0]), y0 = Math.min(a[1], b[1]), y1 = Math.max(a[1], b[1]);
  rr(x0, y0, x1 - x0, y1 - y0, 0, m ? '#0b0b0d' : '#121214'); rrS(x0, y0, x1 - x0, y1 - y0, 0, C.mid, 4);
  // counter and basin along the mirror wall
  const c0 = pl(CTR.x1, 0), c1 = pl(CTR.x0, sg * CTR.z); rr(Math.min(c0[0], c1[0]), c0[1], Math.abs(c1[0] - c0[0]), c1[1] - c0[1], 0, '#222');
  const sc = pl(0, sg * SINK.z); ell(sc[0], sc[1], SINK.rz * PL.s, SINK.rx * PL.s, 0, '#555');
  ctx.restore();
  // the door in the far wall: a gap, and the door leaf (open or shut)
  const dx = m ? x0 : x1, d0 = pl(DOOR.x1, sg * ROOM.z1), d1 = pl(DOOR.x0, sg * ROOM.z1);
  ln(dx, d0[1], dx, d1[1], 8, '#000', 'butt');
  const op = o.door ?? 0, hinge = d1, L = (DOOR.x1 - DOOR.x0) * PL.s, ang = -Math.PI / 2 + sg * 0;
  const a1 = op * 1.45; ln(hinge[0], hinge[1], hinge[0] - sg * Math.sin(a1) * L, hinge[1] - Math.cos(a1) * L, 6, m ? C.sec : C.fig);
  if (o.label) text(o.label, (x0 + x1) / 2, y0 - 26, '900 38px M', m ? C.mid : C.sec);
}
function planPerson(x, z, face, col, label, r = 0.2) {
  const [px, py] = pl(x, z); ctx.save(); glow('rgba(255,255,255,0.25)', 12); circ(px, py, r * PL.s, col);
  pth(`M${px + face * r * PL.s * 1.35},${py} L${px + face * r * PL.s * 0.6},${py - 14} L${px + face * r * PL.s * 0.6},${py + 14} Z`, col); ctx.restore();
  if (label) text(label, px, py + r * PL.s + 48, '900 34px M', col);
}
function planThing(x, z, col = '#9a9a9f', label = 'IT') { const [px, py] = pl(x, z); ctx.save(); glow('rgba(255,255,255,0.2)', 12); ell(px, py, 0.1 * PL.s, 0.2 * PL.s, 0, col); circ(px, py, 0.08 * PL.s, '#bdbdc2'); ctx.restore(); if (label) text(label, px, py - 0.3 * PL.s - 14, '900 36px M', C.red); }
function plan(t, o = {}) {
  planRoom(1, { door: 1, label: 'IN THE MIRROR' }); planRoom(0, { door: 0, label: 'YOUR BATHROOM' });
  // the glass
  const g0 = pl(MIR.x1, 0), g1 = pl(MIR.x0, 0); ctx.save(); glow('rgba(200,225,255,0.8)', 16); ln(g0[0], g0[1], g1[0], g1[1], 10, '#cfe0ef'); ctx.restore();
  text('MIRROR', g0[0], g0[1] - 26, '900 34px M', '#cfe0ef');
  planPerson(ME.x, ME.z, -1, C.fig, 'YOU');
  planPerson(ME.x, -ME.z, 1, '#bdbdc2', 'REFLECTION');
  if (o.thing !== false) planThing(o.thingX ?? 0.3, o.thingZ ?? -3.1);
}
S.b4 = (t, seg) => {
  const tt = wt(seg, 'turn'), tn = wt(seg, 'nothing');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.22, W / 2, H / 2, () => {
    fadeIn(t, seg.start, () => plan(t));
    if (t >= tt) { const [px, py] = pl(ME.x, ME.z), k = prog(t, tt, 0.5); ctx.save(); ctx.beginPath(); ctx.arc(px, py, 52, -Math.PI * 0.8, -Math.PI * 0.8 + Math.PI * 1.4 * k); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); }
    if (t >= tn) { const [dx, dy] = pl(0, ROOM.z1 - 0.45); pop(t, tn, dx, dy, () => tag('NOTHING', dx - 30, dy + 10, C.fig, 36, 'center')); }
  });
};
S.b5 = (t, seg) => {
  const tt = wt(seg, 'turn'), te = wt(seg, 'eyes'), tl = wt(seg, 'leave'), ta = wt(seg, 'alone');
  const go = ease(prog(t, ta - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.22, 1.3, 860, H / 2, () => {
    plan(t, { thingX: lerp(0.3, ME.x + 0.05, go), thingZ: lerp(-3.1, -ME.z - 0.5, go) });
    const [px, py] = pl(ME.x, ME.z), [gx, gy] = pl(ME.x, 0);
    if (t >= tt && t < te) { pop(t, tt, px, py - 110, () => { redX(px, py - 110, 40, prog(t, tt + 0.2, 0.3)); }); }
    if (t >= te) { const away = prog(t, tl, 0.3); ctx.save(); ctx.setLineDash([12, 10]);
      if (away < 1) lnP(px - 30, py, gx, gy, 5, C.fig, prog(t, te, 0.4) * (1 - away));
      if (away > 0) { redGlow(10); lnP(px + 30, py, px + 30 + 260 * away, py, 5, C.red, 1); } ctx.restore(); }
    if (t >= ta) { const [rx, ry] = pl(ME.x, -ME.z); pop(t, ta, rx, ry + 120, () => tag('ALONE WITH IT', rx, ry + 130, C.red, 36, 'center')); }   // under the labels, clear of the IT marker
  });
};
S.b6 = (t, seg) => {
  const tb = wt(seg, 'between'), tl = wt(seg, 'late');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.3, 1.22, 860, H / 2, () => {
    plan(t);
    if (t >= tb) { const a = pl(ME.x, ME.z), b = pl(0.3, -3.1); ctx.save(); redGlow(10); ctx.setLineDash([14, 10]); lnP(a[0], a[1], b[0], b[1], 5, C.red, prog(t, tb, 0.8)); ctx.restore();
      const [rx, ry] = pl(ME.x, -ME.z); ctx.save(); glow('rgba(255,255,255,0.8)', 30); circS(rx, ry, 0.2 * PL.s + 12, C.fig, 4); ctx.restore(); }
    if (t >= tl) { const [rx, ry] = pl(ME.x, -ME.z), k = 0.5 + 0.5 * Math.sin((t - tl) * 5); ctx.save(); ctx.translate(rx, ry); ctx.rotate(Math.PI * k); pth(`M${-0.2 * PL.s * 1.4},0 L${-0.2 * PL.s * 0.7},-14 L${-0.2 * PL.s * 0.7},14 Z`, C.red); ctx.restore();
      pop(t, tl, rx, ry + 120, () => tag('IT KEEPS LOOKING BACK', rx, ry + 130, C.red, 34, 'center')); }
  });
};

// ---------- rule 3: when it writes, run ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'WHEN IT WRITES, RUN');
const WRITE = { x: ME.x };
// the writing: the first stroke of R in c2, the rest on "R. U. N."
function runProgress(t) {
  const c2 = window.TL.segments.find(s => s.id === 'c2'), c4 = window.TL.segments.find(s => s.id === 'c4'); if (!c2 || !c4) return [1, 1, 1];
  const tl = wt(c2, 'line'), r = wt(c4, 'r'), u = wt(c4, 'u'), n = wt(c4, 'n');
  const first = runStrokes()[0].L / runStrokes().filter(s => s.ch === 0).reduce((a, s) => a + s.L, 0);
  return [t < r - 0.1 ? first * prog(t, tl, 1.1) : lerp(first, 1, prog(t, r - 0.1, 0.55)), prog(t, u - 0.05, 0.42), prog(t, n - 0.05, 0.5)];
}
// your reflection's hand: raised to the glass while it writes, down again after
function writing(t) {
  const p = runProgress(t), tip = runTip(p);
  const c2 = window.TL.segments.find(s => s.id === 'c2'), k = c2 ? ease(prog(t, wt(c2, 'line') - 0.6, 0.5)) : 1;
  const last = tip || (p[2] >= 1 ? RUN_END : (p[0] > 0 ? (runTip([Math.min(p[0], 0.999), 0, 0]) || [RUN_BOX.x, RUN_BOX.y + RUN_BOX.h]) : [RUN_BOX.x, RUN_BOX.y]));
  return { p, tip: last, pose: writerPose(last, k), k };
}
S.c1 = (t, seg) => {
  const tf = wt(seg, 'fog'), tc = wt(seg, 'cold');
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.05, 1.25, GLASS_C, { me: poseOf({ ...WASH, look: 0, lean: 0.12 }), water: 1, fog: 0.85 * ease(prog(t, tf - 0.2, 1.6)) });
  if (t >= tc) pop(t, tc, 1480, 280, () => { tag('COLD', 1480, 290, '#9fd0ff', 60, 'center'); });
};
S.c2 = (t, seg) => {
  const to = wt(seg, 'other'), w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.45, [0.0, 1.55, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, inMirror: () => reflFinger(w.pose, w.tip, w.k) });
  // side view of the glass: the finger is on the far side
  if (t >= to - 0.1) slideIn(t, to - 0.1, 40, 0, () => {
    const x = 1560, y = 330; ctx.save(); ctx.globalAlpha *= 0.92; rr(x - 190, y - 190, 380, 380, 16, '#000'); ctx.restore(); rrS(x - 190, y - 190, 380, 380, 16, C.dim, 3);
    ctx.save(); glow('rgba(200,225,255,0.8)', 12); rr(x - 8, y - 140, 16, 280, 3, '#cfe0ef'); ctx.restore();
    rr(x + 8, y - 140, 26, 280, 3, 'rgba(210,220,226,0.55)');                 // fog on your side
    text('GLASS', x, y + 175, '900 24px M', '#cfe0ef'); text('IT', x - 110, y - 150, '900 28px M', C.sec); text('YOU', x + 110, y - 150, '900 28px M', C.fig);
    poly([[x - 170, y + 40], [x - 70, y + 10], [x - 12, y - 10]], 18, '#dcdcde'); circ(x - 12, y - 10, 9, '#dcdcde');   // its finger, pressed on the glass from behind
    ctx.save(); redGlow(10); ln(x + 21, y - 70, x + 21, y + 40, 8, '#000'); ctx.restore();   // the line it draws shows on your side
  });
};
S.c3 = (t, seg) => {
  const tb = wt(seg, 'backwards'), tr = wt(seg, 'read'), w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.45, 1.55, [0.0, 1.55, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, inMirror: () => reflFinger(w.pose, w.tip, w.k) });
  // its side and your side of the same word
  const box = (x, y, lbl, flip, t0) => slideIn(t, t0, 0, 30, () => { ctx.save(); ctx.globalAlpha *= 0.92; rr(x - 170, y - 100, 340, 210, 14, '#000'); ctx.restore(); rrS(x - 170, y - 100, 340, 210, 14, C.dim, 3);
    text(lbl, x, y - 58, '900 24px M', C.mid); ctx.save(); ctx.translate(x, y + 50); if (flip) ctx.scale(-1, 1); text('RUN', 0, 0, '900 90px M', flip ? C.sec : C.fig); ctx.restore(); });
  box(330, 300, 'ITS SIDE', true, tb - 0.2); box(1590, 300, 'YOUR SIDE', false, tr - 0.3);
};
S.c4 = (t, seg) => {
  const w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 1.0, 1.55, 1.7, [0.0, 1.58, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, drip: prog(t, seg.end - 0.2, 1.5), inMirror: () => reflFinger(w.pose, w.tip, w.k) });
};
S.c5 = (t, seg) => {
  const te = wt(seg, 'empty'), w = writing(t), down = ease(prog(t, seg.start + 0.2, 0.6)), rp = writerPose(RUN_END, 1 - down);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.5, 2.0, [0.25, 1.3, -ROOM.z1], { me: poseOf({}), refl: rp, door: 1, fog: 0.4, run: [1, 1, 1], drip: 1 });
  if (t >= te) pop(t, te, 1480, 280, () => tag('EMPTY', 1480, 290, C.red, 60, 'center'));
  redFlash(t, te, 0.06);
};
S.c6 = (t, seg) => {
  // from the doorway: you turn and run. Your reflection does not follow. It watches you go
  const tl = wt(seg, 'look'), k = ease(prog(t, seg.start, 0.45)), run = prog(t, seg.start + 0.4, 1.6);
  const me = poseOf({ yaw: Math.PI * k, x: lerp(ME.x, -1.0, ease(run)), z: lerp(ME.z, 2.3, run), walk: run > 0, step: t * 13, L: [-0.24, 0.85, 0.3 * Math.sin(t * 13)], R: [0.24, 0.85, -0.3 * Math.sin(t * 13)] });   // out past the left of the doorway, arms swinging, never close enough to clip the lens
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.35, 1.5, GLASS_C, { cam: CAMS.door, me, refl: poseOf({}), door: 0, fog: 0.75, run: [1, 1, 1], drip: 1 });
  if (t >= tl) pop(t, tl, 1500, 250, () => tag('DO NOT LOOK BACK', 1500, 260, C.red, 54, 'center'));
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
// the grab: its arm comes out of the glass at G and closes around your left wrist (the one with the watch)
const G = [-0.26, 1.1, 0];
const GRAB = { ...WASH, look: 0.3, lean: 0.15, L: [-0.2, 0.98, 0.4], R: [0.1, 0.98, 0.36] };
const wristOf = ps => { const j = skeleton(ps); return V3.lerp(j.hand.L, j.elb.L, 0.15); };
function grabScene(t, me, k, o = {}) {
  // k: how far the arm is out (0..1); the thing stands right behind your reflection, its arm through the glass
  const wr = wristOf(me), th = { x: ME.x + 0.38, z: -ME.z - 0.55, t, reach: true, sc: 0.95 };
  return { cam: CAMS.otsL, me, door: 1, thing: th, ...o,
    inMirror: () => { const sh = [th.x - 0.15, 1.73 * th.sc, th.z]; greyArm(sh, G, wr, 1, true);
      // the part of the arm that is out in your room is a real thing in front of the glass, so the mirror shows it too: on your reflection's wrist
      if (k > 0) { greyArm(null, G, MIRROR(wr), k, false); if (k >= 1) gripWrist(MIRROR(wr), 1); } if (o.inMirror) o.inMirror(); },
    glassFx: () => { glassRipple(G, o.rip ?? -9, t); if (o.glassFx) o.glassFx(); },
    front: () => { if (k > 0) { greyArm(null, G, wr, k, false); if (k >= 1) gripWrist(wr, 1); } if (o.front) o.front(); } };
}
S.d1 = (t, seg) => {
  const th = wt(seg, 'hand'), tg = wt(seg, 'grey'), tw = wt(seg, 'wrist'), k = ease(prog(t, th, tw - th));
  const me = poseOf(GRAB);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.5, wristOf(me), grabScene(t, me, k, { rip: th }));
  if (t >= tg) pop(t, tg, 1480, 280, () => tag('LONG GREY FINGERS', 1480, 290, C.fig, 46, 'center'));
  redFlash(t, tw, 0.08);
};
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
S.d3 = (t, seg) => {
  const tp = wt(seg, 'pull'), ts = wt(seg, 'stronger'), pull = ease(prog(t, tp - 0.1, 0.4)), back = ease(prog(t, ts, 0.5));
  const me = poseOf({ ...GRAB, lean: lerp(0.15, -0.12, pull) + 0.2 * back, L: [-0.2, 0.98, lerp(0.4, 0.3, pull) + 0.1 * back], x: ME.x, z: ME.z + 0.04 * pull - 0.06 * back });
  ctx.save(); if (pull > 0 && pull < 1) shake(4, t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.3, wristOf(me), grabScene(t, me, 1));
  ctx.restore();
  if (t >= tp) slideIn(t, tp, 40, 0, () => { xTag('PULL', 1560, 300, 56, prog(t, tp + 0.3, 0.3)); });
  if (t >= ts) pop(t, ts, 1480, 450, () => tag('STRONGER THAN YOU', 1480, 460, C.red, 44, 'center'));
};
// the glass cracks from where your fist hits it, and every piece has something looking out of it
const CRACK = [0.12, 1.5];
function cracks(t, k, eyes) {
  if (k <= 0) return; const rays = 11;
  ctx.save(); ctx.lineJoin = 'round';
  const shards = [];
  for (let i = 0; i < rays; i++) { const a = i / rays * Math.PI * 2 + hash(i) * 0.4, L = 0.9 * k; const pts = [[CRACK[0], CRACK[1]]];
    for (let s = 1; s <= 6; s++) { const r = L * s / 6, j = (hash(i * 13 + s) - 0.5) * 0.09; pts.push([CRACK[0] + Math.cos(a + j) * r, CRACK[1] + Math.sin(a + j) * r]); }
    const sp = pts.map(p => prj([p[0], p[1], 0.001])); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]);
    ctx.strokeStyle = 'rgba(235,240,245,0.85)'; ctx.lineWidth = 2.5; ctx.stroke();
    const a2 = a + Math.PI / rays; shards.push([CRACK[0] + Math.cos(a2) * 0.28, CRACK[1] + Math.sin(a2) * 0.2]); }
  for (let r = 0.09; r < 0.5 * k; r += 0.11) { const ring = []; for (let i = 0; i <= rays; i++) { const a = i / rays * Math.PI * 2; ring.push(prj([CRACK[0] + Math.cos(a) * r * (0.8 + hash(i + r * 10) * 0.4), CRACK[1] + Math.sin(a) * r * (0.8 + hash(i * 3 + r) * 0.4), 0.001])); }
    ctx.beginPath(); ctx.moveTo(ring[0][0], ring[0][1]); for (const q of ring.slice(1)) ctx.lineTo(q[0], q[1]); ctx.strokeStyle = 'rgba(235,240,245,0.5)'; ctx.lineWidth = 1.8; ctx.stroke(); }
  // a face in every piece
  if (eyes > 0) shards.forEach((s, i) => { if (s[0] < MIR.x0 + 0.06 || s[0] > MIR.x1 - 0.06 || s[1] < MIR.y0 + 0.06 || s[1] > MIR.y1 - 0.06) return;
    const p = prj([s[0], s[1], -0.3]); if (!p) return; const e = clamp(eyes * 3 - i * 0.15); if (e <= 0) return;
    ctx.save(); ctx.globalAlpha *= e; glow('rgba(255,255,255,0.2)', 10); ell(p[0], p[1], 0.05 * p[3], 0.07 * p[3], 0.2, '#9a9a9f'); noGlow();
    for (const sg of [-1, 1]) ell(p[0] + sg * 0.018 * p[3], p[1], 0.01 * p[3], 0.016 * p[3], 0, '#050505'); ctx.restore(); });
  ctx.restore();
}
S.d4 = (t, seg) => {
  const tb = wt(seg, 'break'), tp = wt(seg, 'piece'), ck = ease(prog(t, tb + 0.05, 0.25));
  const me = poseOf({ ...GRAB, R: t < tb + 0.05 ? [lerp(0.1, CRACK[0] - ME.x, prog(t, tb - 0.4, 0.4)), lerp(0.98, CRACK[1], prog(t, tb - 0.4, 0.4)), lerp(0.36, ME.z - 0.08, prog(t, tb - 0.4, 0.4))] : [0.12, 1.2, 0.4] });
  ctx.save(); const hb = t - tb; if (hb > 0 && hb < 0.25) shake(8 * (1 - hb / 0.25), t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [0.05, 1.5, 0], grabScene(t, me, 1, { glassFx: () => cracks(t, ck, prog(t, tp, 1.2)) }));
  ctx.restore();
  if (t >= tb) slideIn(t, tb, 40, 0, () => { xTag('BREAK IT', 1560, 300, 56, prog(t, tb + 0.3, 0.3)); });
  if (t >= tp + 0.6) pop(t, tp + 0.6, 1500, 450, () => tag('A NEW WINDOW', 1500, 460, C.red, 44, 'center'));
};
S.d5 = (t, seg) => {
  // someone comes to the door behind you: in the glass, their reflection, and the fingers on its shoulder too
  const tc = wt(seg, 'call'), tw = wt(seg, 'whoever'), tm = wt(seg, 'mirror'), come = ease(prog(t, tw - 0.3, 1.0));
  const me = poseOf(GRAB), helper = poseOf({ x: -0.15, z: lerp(3.9, 3.05, come), yaw: 0 });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.4, [-0.1, 1.4, -2.0], grabScene(t, me, 1, {
    inMirror: () => { if (come > 0) { body3(helper, { mirror: true, col: '#cfcfd2' }); const j = skeleton(helper); if (t >= tm) { ctx.save(); ctx.globalAlpha *= prog(t, tm, 0.5); for (const s of ['L', 'R']) fingers3(MIRROR(V3.add(j.sh[s], [0, 0.03, 0])), [0, -1, 0.3], '#9a9a9f', 0.13); ctx.restore(); } } } }));
  if (t >= tc) slideIn(t, tc, 40, 0, () => { xTag('CALL FOR HELP', 1540, 300, 50, prog(t, tc + 0.3, 0.3)); });
};
S.d6 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
// your free hand, flat on the glass; then its hand, late, against yours
const PALM = [0.22, 1.42];
const handUp = k => ({ ...GRAB, look: 0, lean: lerp(0.15, 0.32, k), R: [lerp(0.1, PALM[0] - ME.x, k), lerp(0.98, PALM[1] - 0.02, k), lerp(0.36, ME.z - 0.06, k)] });
S.d7 = (t, seg) => {
  const tf = wt(seg, 'flat'), k = ease(prog(t, seg.start + 0.3, tf - seg.start - 0.2));
  const me = poseOf(handUp(k));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [0.08, 1.3, 0], grabScene(t, me, 1, { refl: poseOf(GRAB), front: () => { if (k > 0.97) palmOn(PALM, C.fig, 0.012); } }));
  if (t >= tf) pop(t, tf, 1500, 280, () => tag('FLAT ON THE GLASS', 1500, 290, C.fig, 46, 'center'));
};
S.d8 = (t, seg) => {
  const tp = wt(seg, 'press'), tpp = wt(seg, 'palm'), k2 = ease(prog(t, tp - 0.6, 1.1));
  const me = poseOf(handUp(1)), rp = poseOf(handUp(k2));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.9, [PALM[0], PALM[1], 0], grabScene(t, me, 1, { refl: rp,
    inMirror: () => { if (k2 > 0.97) palmOn(PALM, '#dcdcde', -0.012, true); },
    glassFx: () => { if (k2 > 0.97) { const c = prj([PALM[0], PALM[1], 0]); ctx.save(); const g = ctx.createRadialGradient(c[0], c[1], 5, c[0], c[1], 0.22 * c[3]); g.addColorStop(0, 'rgba(255,255,255,0.35)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(c[0] - 300, c[1] - 300, 600, 600); ctx.restore(); } },
    front: () => palmOn(PALM, C.fig, 0.012) }));
  if (t >= tpp) pop(t, tpp, 1500, 280, () => tag('PALM TO PALM', 1500, 290, C.fig, 50, 'center'));
};
S.d9 = (t, seg) => {
  // it turns its back to you, takes hold of the grey arm and pulls; the hand lets go of your wrist and slides back into the glass
  const tt = wt(seg, 'turn'), tp = wt(seg, 'pull'), to = wt(seg, 'off');
  const turn = ease(prog(t, tt - 0.1, 0.6)), rel = ease(prog(t, to - 0.1, 0.5));
  const me = poseOf(handUp(1 - ease(prog(t, to, 0.6)))), wr = wristOf(me);
  const th = { x: ME.x + 0.38, z: -ME.z - 0.55, t, reach: true, sc: 0.95 };
  const rp = poseOf({ yaw: Math.PI * turn, z: ME.z + 0.1 * turn, L: [-0.15, 1.15, 0.3 * turn], R: [0.15, 1.15, 0.3 * turn] });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.45, [0.0, 1.35, -0.4], { cam: CAMS.otsL, me, refl: rp, door: 1, thing: th,
    inMirror: () => { const sh = [th.x - 0.15, 1.73 * th.sc, th.z]; const g2 = V3.lerp(G, [G[0], G[1], -0.3], rel); greyArm(sh, g2, wr, 1, true);
      if (rel < 1) { greyArm(null, G, MIRROR(wr), 1 - rel, false); if (rel < 0.15) gripWrist(MIRROR(wr), 1); } },
    glassFx: () => glassRipple(G, to, t),
    front: () => { if (rel < 1) { greyArm(null, G, wr, 1 - rel, false); if (rel < 0.15) gripWrist(wr, 1); } } });
  if (t >= tp) pop(t, tp, 1500, 280, () => tag('IT PULLS IT OFF YOU', 1500, 290, C.fig, 46, 'center'));
};
S.d10 = (t, seg) => {
  // you back away. In the glass they fight; do not watch
  const tw = wt(seg, 'watch'), b = ease(prog(t, seg.start, 1.4));
  const me = poseOf({ z: lerp(ME.z, 1.35, b), lean: -0.05 });
  const shake2 = Math.sin(t * 23) * 0.04;
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, GLASS_C, { me, refl: poseOf({ yaw: Math.PI, x: ME.x + shake2, z: ME.z + 0.2, L: [-0.15, 1.2, 0.35], R: [0.15, 1.2, 0.35] }), door: 1,
    thing: { x: ME.x + 0.1 - shake2, z: -ME.z - 0.75, t: t * 4, sc: 0.95 } });
  if (t >= tw) pop(t, tw, 1500, 280, () => tag('DO NOT STAY', 1500, 290, C.red, 54, 'center'));
};
S.d11 = (t, seg) => {
  const tc = wt(seg, 'towel'), th = wt(seg, 'hear'), tl = wt(seg, 'lift');
  const tk = ease(prog(t, tc - 0.4, 0.5)), bump = t >= th ? Math.max(0, Math.sin((t - th) * 5.5)) ** 3 : 0;
  shot(t, seg.start, seg.end - seg.start + 1.2, 1.05, 1.2, GLASS_C, { me: poseOf({ z: 1.35 }), refl: poseOf({ yaw: Math.PI, z: ME.z + 0.2 }), door: 1, thing: { x: ME.x + 0.1, z: -ME.z - 0.75, t: t * 4, sc: 0.95 },
    towel: tk, bump, bx: -0.1 + 0.25 * Math.sin(Math.floor((t - th) * 5.5 / Math.PI) * 2.3), by: 1.45 + 0.15 * Math.cos(Math.floor((t - th) * 1.75) * 1.7) });
  if (t >= tl) pop(t, tl, 1500, 280, () => tag('DO NOT LIFT IT', 1500, 290, C.red, 54, 'center'));
};

// ---------- morning ----------
function morning(fn) { fn(); ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.1; ctx.fillStyle = '#ffe6c8'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
S.e1 = (t, seg) => {
  const td = wt(seg, 'down'), tx = wt(seg, 'exactly'), tk = 1 - ease(prog(t, td - 0.3, 0.5));
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15, GLASS_C, { me: poseOf({}), towel: tk, light: 1 }));
  slideIn(t, seg.start + 0.3, 40, 0, () => text('7:00 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tx) pop(t, tx, 1500, 330, () => { tag('ON TIME', 1500, 340, C.fig, 54, 'center'); });
};
S.e2 = (t, seg) => {
  const tu = wt(seg, 'up'), tw = wt(seg, 'wash'), wk = prog(t, tw - 0.3, 0.4);
  const pose = { ...poseOf(lookUp(t, tu + 0.1)), ...(wk > 0 ? washing(t, wk) : {}), look: wk > 0 ? 0.6 : poseOf(lookUp(t, tu + 0.1)).look };
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [ME.x, 1.5, -ME.z], { me: poseOf(pose), water: wk }));
  [[tu, 'LOOK UP', 300], [tw, 'WASH', 430]].forEach(([t0, l, y]) => { if (t >= t0) slideIn(t, t0, 40, 0, () => { text(l, 1420, y + 16, '900 48px M', C.fig, 'left'); check(1370, y, 26, prog(t, t0 + 0.2, 0.3)); }); });
};
// from the doorway: you turn your back on the mirror and walk out. So does it. Its back is covered in marks; yours is not
const E_CAM = { x: 0.9, y: 1.62, z: 3.05, yaw: 0.2, pitch: -0.07, f: 1000 };
function leaving(t, seg3) {
  const tt = wt(seg3, 'turn'), k = ease(prog(t, tt - 0.2, 0.9)), w = prog(t, tt + 0.6, 2.4);
  return poseOf({ yaw: Math.PI * k, x: lerp(ME.x, -0.55, ease(w)), z: lerp(ME.z, 1.45, w), walk: w > 0 && w < 1, step: t * 8, L: [-0.22, 0.8, 0.12 * Math.sin(t * 8) * (w > 0 && w < 1)], R: [0.22, 0.8, -0.12 * Math.sin(t * 8) * (w > 0 && w < 1)] });
}
S.e3 = (t, seg) => {
  const me = leaving(t, seg);
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.1, GLASS_C, { cam: E_CAM, me, scars: 1 }));
};
S.e4 = (t, seg) => {
  const s3 = window.TL.segments.find(s => s.id === 'e3'), me = leaving(t, s3);
  const rb = MIRROR(skeleton(me).chest);
  morning(() => shot(t, seg.start, seg.end - seg.start + 1.4, 1.4, 3.2, rb, { cam: E_CAM, me, scars: 1 }));
  redFlash(t, seg.start + 0.9, 0.04);
};
// the file closes
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], ['404', 150]], -0.1); ctx.restore();
  });
};
// sign-off: the rules once more, the stamp, and the picture sinks into the dark around it
S.e6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.95 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
