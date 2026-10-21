// ---------- EP04 scenes: "If Your Security Camera Ever Records Tomorrow" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const sideTag = (t, t0, s, x, y, col = C.fig, size = 50) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const whiteFlash = (t, t0, a = 0.55, d = 0.07) => { if (t >= t0 && t < t0 + d) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const clockStr = s => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return [h, m, x].map(v => String(v).padStart(2, '0')).join(':'); };
const T302 = 3 * 3600 + 2 * 60;

// ---------- the living room, seen by some camera ----------
// o: room4 options + thing {eye, ex, head}, arm {k, to, grip}, shift (the sofa moves), people [{pose, o}], lying [{x,z,a,o}], hoodie, cctvDev {led, dir}
function living(t, o = {}) {
  room4(t, o);
  for (const L of (o.lying || [])) if (L.under) lying3(L.x, L.z, L.a, L.o || {});
  sofa4({ shift: o.shift || 0 });
  // the dark gap under the front of the sofa
  { const sh = o.shift ? Math.sin(o.shift * 40) * 3 * o.shift : 0; ctx.save(); ctx.translate(sh, 0); ctx.globalAlpha *= 0.85; polyW([[SOFA.x0 + 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 + 0.1], [SOFA.x0 + 0.04, 0.003, SOFA.z1 + 0.1]], '#050505', null); ctx.restore(); }
  if (o.ooze) ooze3(o.ooze.c, o.ooze.k);
  if (o.thing) underThing(t, { ...o.thing, head: 0 });
  if (o.piece) severed3(t, o.piece.c, o.piece.a, o.piece);
  if (o.arm && !o.arm.over) thingArm(t, o.arm);
  if (o.thing && o.thing.head > 0) thingHead(t, o.thing.ex ?? THING_X, o.thing.head, o.thing);
  chair4({ hoodie: o.hoodie });
  for (const L of (o.lying || [])) if (!L.under) lying3(L.x, L.z, L.a, L.o || {});
  if (o.bait) rugBait(o.bait);
  const ps = (o.people || []).slice().sort((a, b) => V3.len(V3.sub(camPos(), [b.pose.x, 1, b.pose.z])) - V3.len(V3.sub(camPos(), [a.pose.x, 1, a.pose.z])));
  for (const p of ps) body3(p.pose, p.o || {});
  if (o.arm && o.arm.over) thingArm(t, o.arm);   // the hand closes over the ankle, in front of the leg
  if (o.cctvDev) cctv4(o.cctvDev);
  if (o.front) o.front();
}
// a shot of the room (not through the security camera): push in toward a world point
function view(t, t0, d, z0, z1, focus, o) {
  setCam(o.camObj || o.cam || CAMS.side); const f = prj(focus) || [W / 2, H / 2];
  cam(t, t0, d, z0, z1, f[0], f[1], () => living(t, o));
}
// ---------- the security camera's picture ----------
// o.rect {x,y,w} where it sits (default: big, above the captions); o.z zoom, o.focus world point to zoom on; o.date 'TOMORROW'|'TODAY'|'LIVE'|'TONIGHT';
// o.clock seconds; o.bar 0..1 (playback position); o.label; o.noise 0..1; o.off 0..1 (no signal)
const FR = { x: 160, y: 40, w: 1600 };
let LASTFEED = null;
function feed(t, o = {}) {
  const r = o.rect || FR, s = r.w / W;
  ctx.save(); ctx.translate(r.x, r.y); ctx.scale(s, s);
  ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip();
  rr(0, 0, W, H, 0, '#000');
  setCam(o.camObj || CAMS.cctv);
  const z = o.z || 1, fp = o.focus ? (prj(o.focus) || [W / 2, H / 2]) : [W / 2, H / 2];
  LASTFEED = { r, s, z, fx: fp[0], fy: fp[1], camObj: o.camObj || CAMS.cctv };
  ctx.save(); ctx.translate(fp[0], fp[1]); ctx.scale(z, z); ctx.translate(-fp[0], -fp[1]);
  if (!(o.off >= 1)) living(t, o);
  ctx.restore();
  if (o.dark > 0) { ctx.save(); ctx.globalAlpha = clamp(o.dark); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }   // the lights are off
  // the camera's own look: cold grey, scan lines, noise, a dark rim
  ctx.save(); ctx.globalCompositeOperation = 'color'; ctx.globalAlpha = 0.5; ctx.fillStyle = '#7a8a86'; ctx.fillRect(0, 0, W, H); ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.09; for (let y = 0; y < H; y += 6) rr(0, y, W, 2, 0, '#000'); ctx.restore();
  if (grainC) { ctx.save(); ctx.globalAlpha = 0.1 + 0.4 * (o.noise || 0); ctx.drawImage(grainC[Math.floor(t * 24) % 4], 0, 0, W, H); ctx.restore(); }
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.75)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  if (o.off > 0) { ctx.save(); ctx.globalAlpha = clamp(o.off); rr(0, 0, W, H, 0, '#050505'); ctx.globalAlpha *= 0.3; ctx.drawImage(grainC[Math.floor(t * 30) % 4], 0, 0, W, H); ctx.restore();
    if (o.off >= 1) spaced('NO SIGNAL', W / 2, H / 2 + 24, '600 64px Plex', '#bdbdbd', 8); }
  // the overlay: a blinking dot, the room, the date and time
  if (Math.floor(t * 1.6) % 2 === 0) { ctx.save(); redGlow(14); circ(70, 70, 16, C.red); ctx.restore(); }
  text('CAM 1', 100, 84, '600 40px Plex', '#e8e8e8', 'left');
  text(o.label || 'LIVING ROOM', 60, H - 44, '600 44px Plex', '#e8e8e8', 'left');
  const date = o.date || 'TOMORROW', hot = date === 'TOMORROW' || date === 'TONIGHT';
  const tm = clockStr(o.clock ?? T302);
  ctx.font = '600 44px Plex'; const tw = ctx.measureText(tm).width;
  text(tm, W - 60, H - 44, '600 44px Plex', '#e8e8e8', 'right');
  ctx.save(); if (hot) redGlow(14); text(date, W - 90 - tw, H - 44, '700 44px Plex', hot ? C.red : '#e8e8e8', 'right'); ctx.restore();
  if (o.bar != null) { rr(60, H - 22, W - 120, 8, 4, 'rgba(255,255,255,0.25)'); ctx.save(); redGlow(10); rr(60, H - 22, (W - 120) * clamp(o.bar), 8, 4, C.red); ctx.restore(); circ(60 + (W - 120) * clamp(o.bar), H - 18, 13, '#f2f2f2'); }
  ctx.restore();
  rrS(r.x, r.y, r.w, r.w * H / W, 6, '#3a3a3e', 3);
}
// where a world point lands on screen in the last feed drawn this frame
function feedPt(p) { const L = LASTFEED; if (!L) return null; setCam(L.camObj); const q = prj(p); if (!q) return null;
  const x = L.fx + (q[0] - L.fx) * L.z, y = L.fy + (q[1] - L.fy) * L.z; return [L.r.x + x * L.s, L.r.y + y * L.s, q[3] * L.z * L.s]; }
// a label tied to something in the feed: a thin line from the thing to the tag
function feedTag(t, t0, s, p, tx, ty, col = C.fig, size = 44) {
  if (t < t0) return; const q = feedPt(p); if (!q) return;
  if (tx === 'rel') { tx = q[0] + ty[0]; ty = q[1] + ty[1]; }
  const k = easeOut(prog(t, t0, 0.3)); ctx.save(); ctx.globalAlpha *= k; ctx.setLineDash([8, 8]); ln(q[0], q[1], lerp(q[0], tx, k), lerp(q[1], ty + 20, k), 3, col); ctx.setLineDash([]);
  circ(q[0], q[1], 9, col); ctx.restore(); pop(t, t0 + 0.1, tx, ty, () => tag(s, tx, ty + 10, col, size, 'center'));
}
// the camera app on the phone: the clip on top, the playback bar, the list of clips
function appScreen(t, o = {}) {
  rr(0, 0, SW, SH, 0, '#0b0b0c'); statusBar(o.time || '3:02');
  pthS('M30,82 l-12,12 l12,12', '#bdbdbd', 3.5); text(o.title || 'Living room', SW / 2, 102, `700 22px ${UI}`, '#f2f2f2');
  feed(t, { ...o, rect: { x: 0, y: 136, w: SW } });
  const by = 136 + SW * H / W + 34, p = clamp(o.bar ?? 0), dur = o.dur ?? 240;
  rr(24, by, SW - 48, 6, 3, '#333'); rr(24, by, (SW - 48) * p, 6, 3, C.red); circ(24 + (SW - 48) * p, by + 3, 9, '#f2f2f2');
  if (o.limit != null) { const lx = 24 + (SW - 48) * o.limit; ln(lx, by - 12, lx, by + 18, 3, '#ffd34d'); }
  const m = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  text(m(p * dur), 24, by + 34, `500 16px ${UI}`, '#9a9a9e', 'left'); text(m(dur), SW - 24, by + 34, `500 16px ${UI}`, '#9a9a9e', 'right');
  // play / pause
  const cy = by + 82; circ(SW / 2, cy, 30, '#1e1e21'); if (o.playing) { rr(SW / 2 - 10, cy - 12, 7, 24, 2, '#f2f2f2'); rr(SW / 2 + 3, cy - 12, 7, 24, 2, '#f2f2f2'); } else pth(`M${SW / 2 - 8},${cy - 13} L${SW / 2 + 13},${cy} L${SW / 2 - 8},${cy + 13} Z`, '#f2f2f2');
  // the clip list
  const clips = o.clips || [['Living room', 'Tomorrow · 3:02 AM', true]];
  text('CLIPS', 24, cy + 74, `700 15px ${UI}`, '#7a7a7e', 'left');
  clips.forEach(([a, b, red, at], i) => { const y = cy + 92 + i * 84; if (at != null && t < at) return; const k = at != null ? easeOut(prog(t, at, 0.3)) : 1;
    ctx.save(); ctx.globalAlpha *= k; rr(18, y, SW - 36, 72, 14, '#18181b'); rr(30, y + 10, 92, 52, 6, '#26262a'); pth(`M${68},${y + 26} L${86},${y + 36} L${68},${y + 46} Z`, '#bdbdbd');
    text(a, 136, y + 32, `600 18px ${UI}`, '#f2f2f2', 'left'); text(b, 136, y + 56, `500 15px ${UI}`, red ? '#ff5a5a' : '#9a9a9e', 'left'); ctx.restore(); });
}
function lockScreen(t, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, SH); g.addColorStop(0, o.morning ? '#3a3328' : '#15161b'); g.addColorStop(1, '#050506'); ctx.fillStyle = g; ctx.fillRect(0, 0, SW, SH);
  statusBar(o.time || '3:02');
  text(o.time || '3:02', SW / 2, 230, `200 104px ${UI}`, '#f2f2f2'); text(o.day || 'Tuesday', SW / 2, 136, `500 22px ${UI}`, '#d8d8d8');
  if (o.notif != null && t >= o.notif) slideIn(t, o.notif, 0, -40, () => camNotif(14, 300, SW - 28, o.sub || 'Living room · 3:02 AM'), 0.35);
}

// ---------- flat icons (white), for the teaser boxes ----------
function icon4(name, x, y, s = 1, col = C.fig) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'play') { rrS(-96, -66, 192, 120, 14, col, 9); pth('M-22,-30 L30,-4 L-22,22 Z', col); rr(-96, 74, 192, 10, 5, '#555'); rr(-96, 74, 150, 10, 5, col); }
  if (name === 'hoodie') { pth('M-70,-40 C-60,-80 60,-80 70,-40 L100,70 L60,74 L52,-6 L52,90 L-52,90 L-52,-6 L-60,74 L-100,70 Z', col); noGlow(); ell(0, -42, 30, 24, 0, '#000'); ln(-12, -20, -16, 20, 4, '#000'); ln(12, -20, 16, 20, 4, '#000'); }
  if (name === 'home') { pth('M0,-86 L92,-10 L70,-10 L70,80 L-70,80 L-70,-10 L-92,-10 Z', col); noGlow(); rr(-22, 18, 44, 62, 4, '#000'); circ(12, 50, 4, col); }
  if (name === 'clock') { circS(0, 0, 76, col, 10); ln(0, 0, 0, -48, 9, col); ln(0, 0, 36, 18, 9, col); circ(0, 0, 9, col); }
  noGlow(); ctx.restore();
}
// rule-page pictograms (dark on the page)
const _pageIcon = pageIcon;
pageIcon = function (name, x, y, col = '#111') {
  ctx.save(); ctx.translate(x, y);
  if (name === 'play') { rrS(-46, -34, 92, 62, 8, col, 6); pth('M-10,-16 L16,-2 L-10,12 Z', col); rr(-46, 38, 92, 6, 3, '#999'); rr(-46, 38, 70, 6, 3, col); ctx.restore(); return; }
  if (name === 'hoodie') { pth('M-34,-20 C-30,-42 30,-42 34,-20 L48,34 L28,36 L24,-2 L24,44 L-24,44 L-24,-2 L-28,36 L-48,34 Z', col); ell(0, -22, 14, 11, 0, '#ececec'); ctx.restore(); return; }
  if (name === 'clock') { circS(0, 0, 40, col, 6); ln(0, 0, 0, -24, 5, col); ln(0, 0, 18, 10, 5, col); ctx.restore(); return; }
  ctx.restore(); return _pageIcon(name, x, y, col);
};

// ---------- hook ----------
const ANKLE = [SPOT.x - 0.1, SPOT.z + 0.03];
const hoodieMe = (p = {}) => ({ pose: poseOf(p), o: { top: HOOD_C, hood: true } });
S.h1 = (t, seg) => {
  // frame 0: tomorrow's clip, already playing: you on the rug, and the grey arm out from under the sofa, around your ankle
  const tn = wt(seg, 'not');
  feed(t, { z: zk(t, 0, seg.end + 0.6, 1.45, 1.6), focus: [SPOT.x - 0.2, 0.55, SPOT.z - 0.35], clock: T302 + 14 + t, people: [hoodieMe({ look: 0.6 })],
    thing: { eye: 1 }, arm: { k: 1, to: ANKLE, grip: true, over: true }, bar: 0.92 + 0.02 * t / 6 });
  if (t >= tn) pop(t, tn, 1420, 230, () => tag('DO NOT BE HOME AT 3 AM', 1420, 240, C.red, 50, 'center'), 0.3);
};
// the three "do not"s as a teaser: each one is done anyway, you see what happens, then black
function h2Windows(seg) { return [[seg.start, wt(seg, 'do', 2), 'play', 'watch', 250], [wt(seg, 'do', 2), wt(seg, 'do', 3), 'hoodie', 'wear', 250], [wt(seg, 'do', 3), nextStart(seg), 'home', 'go', 250]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 1580, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon4(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    const reach = ease(prog(t, hit - 0.35, 0.35));
    if (i === 0) {
      // you watch to the end: the bar races to the end, and the arm comes for you
      feed(t, { z: zk(t, w0, blk - w0, 1.05, 1.3), focus: [SPOT.x, 0.6, SPOT.z - 0.3], clock: T302 + 6 + (t - w0) * 20, people: [hoodieMe({})], thing: { eye: 1 }, arm: { k: reach, to: ANKLE, grip: reach > 0.95, over: true }, bar: ease(prog(t, w0, hit - w0)) });
    } else if (i === 1) {
      // you in the grey hoodie: it knows you by that
      feed(t, { z: zk(t, w0, blk - w0, 1.1, 1.45), focus: [SPOT.x, 1.0, SPOT.z], clock: T302 + 20 + (t - w0), people: [{ pose: poseOf({}), o: { top: HOOD_C, hood: true, mark: t > w0 + 0.3 } }], thing: { eye: 1 }, arm: { k: reach, to: ANKLE, grip: reach > 0.95, over: true } });
    } else {
      // you go back to check: the front door opens on the dark room, and under the sofa an eye turns to you
      const op = ease(prog(t, w0, 0.6)), hd = prog(t, w0 + 0.5, hit - w0 - 0.5);
      feed(t, { z: zk(t, w0, blk - w0, 1.1, 1.6), focus: [THING_X, 0.2, SOFA.z1], date: 'TODAY', clock: T302 + 300 + (t - w0), doorOpen: op, people: [{ pose: poseOf({ x: (FDOOR.x0 + FDOOR.x1) / 2, z: 0.35 + 0.4 * op, yaw: Math.PI, walk: true, step: t * 6 }) }], thing: { eye: 1, head: hd } });
      if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.45 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    }
    if (i < 2) redFlash(t, hit, 0.12);
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not watch it to the end ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT WATCH IT TO THE END');
S.a1 = (t, seg) => {
  // 3:02 AM: the phone on the nightstand lights up
  const tn = wt(seg, 'notification'), tm = wt(seg, 'motion');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, W / 2, 470, () => {
    phone(960, 520, 0.95, () => lockScreen(t, { notif: tm - 0.2 }), { bright: prog(t, tn - 0.5, 0.3) * 0.9 + 0.1 });
  });
  if (t >= tm) pop(t, tm, 1480, 300, () => tag('3:02 AM', 1480, 310, C.red, 54, 'center'));
};
function bed2(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.2)', 16);
  rr(-260, -40, 520, 60, 10, '#3a3a3e'); rr(-280, -150, 26, 190, 8, '#555'); rr(254, -90, 26, 130, 8, '#555');
  rr(-240, -64, 120, 34, 14, C.sec); ell(-160, -88, 44, 40, 0, C.fig); rr(-150, -76, 400, 44, 18, '#d6d6da');
  noGlow(); if (o.awake) { ell(-140, -96, 6, 8, 0, '#000'); ell(-166, -98, 6, 8, 0, '#000'); }
  ctx.restore();
}
S.a2 = (t, seg) => {
  const tb = wt(seg, 'bed'), te = wt(seg, 'empty');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 470, () => {
    slideIn(t, seg.start, -40, 0, () => { bed2(470, 560, 1.15, { awake: true }); text('YOU', 470, 720, '900 48px M', C.fig); });
    slideIn(t, te - 0.6, 40, 0, () => { feed(t, { rect: { x: 980, y: 300, w: 800 }, date: 'TODAY', clock: T302 + (t - seg.start) }); text('LIVING ROOM', 1380, 790, '900 48px M', C.fig); });
  });
  if (t >= te) pop(t, te, 1380, 250, () => tag('EMPTY', 1380, 260, C.fig, 50, 'center'));
};
S.a3 = (t, seg) => {
  const ts = wt(seg, 'sofa'), tl = wt(seg, 'lamp'), td = wt(seg, 'door');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06), clock: T302 + (t - seg.start), date: '' + 'TOMORROW' });
  feedTag(t, ts, 'SOFA', [-0.4, SOFA.back, 0.3], 'rel', [0, -170]);
  feedTag(t, tl, 'LAMP', [LAMP.x, 1.5, LAMP.z], 'rel', [-170, -40]);
  feedTag(t, td, 'FRONT DOOR', [(FDOOR.x0 + FDOOR.x1) / 2, 1.3, 0], 'rel', [-60, -230]);
};
S.a4 = (t, seg) => {
  // the date in the corner: zoom on it, and it is tomorrow
  const tc = wt(seg, 'corner'), tt = wt(seg, "tomorrow's"), z = ease(prog(t, tc - 0.3, 0.9));
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(lerp(1, 2.6, z), lerp(1, 2.6, z)); ctx.translate(-1600, -890);
    feed(t, { clock: T302 + (t - seg.start), date: 'TOMORROW' }); ctx.restore();
  });
  if (t >= tt) { pop(t, tt, 760, 300, () => tag("TOMORROW'S DATE", 760, 310, C.red, 54, 'center')); redFlash(t, tt, 0.06); }
};
// you walk into the room in the clip, from the hall at the front left, to the rug
const walkIn = (t, t0, d = 2.6) => { const k = ease(prog(t, t0, d)); return poseOf({ x: lerp(-2.0, SPOT.x, k), z: lerp(4.1, SPOT.z, k), yaw: lerp(-0.5, 0, k), walk: k > 0 && k < 1, step: t * 7, L: [-0.22, 0.8, 0.1 * Math.sin(t * 7) * (k < 1)], R: [0.22, 0.8, -0.1 * Math.sin(t * 7) * (k < 1)] }); };
S.a5 = (t, seg) => {
  const tw = wt(seg, 'walks'), ty = wt(seg, 'you');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15), focus: [SPOT.x, 1, SPOT.z], clock: T302 + 8 + (t - tw), people: t > tw - 0.4 ? [{ pose: walkIn(t, tw - 0.4), o: { top: HOOD_C, hood: true } }] : [], bar: 0.03 + 0.01 * (t - seg.start) });
  if (t >= ty) { const j = skeleton(walkIn(t, tw - 0.4)); feedTag(t, ty, 'YOU', j.head, 1300, 260, C.red, 56); }
};
S.a6 = (t, seg) => {
  const tw = wt(seg, 'why'), tk = wt(seg, 'keep');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 20 + (t - seg.start), people: [hoodieMe({})], bar: 0.08 + 0.01 * (t - seg.start), playing: true }));
    if (t >= tw) bubble(1150, 330, 170, 130, '?', t, tw);
  });
  if (t >= tk) slideIn(t, tk, 40, 0, () => xTag('KEEP WATCHING', 1420, 640, 48, prog(t, tk + 0.3, 0.3)));
};
S.a7 = (t, seg) => {
  // the bar fills; at the end the clip turns from a recording into a schedule
  const t0 = seg.start, te = wt(seg, 'end'), ts = wt(seg, 'schedule'), p = ease(prog(t, t0 + 0.2, te - t0));
  cam(t, t0, seg.end - t0 + 0.8, 1, 1.04, W / 2, 470, () => {
    const x0 = 360, x1 = 1560, y = 520;
    rr(x0, y - 9, x1 - x0, 18, 9, '#2a2a2e'); ctx.save(); redGlow(16); rr(x0, y - 9, (x1 - x0) * p, 18, 9, C.red); ctx.restore(); circ(x0 + (x1 - x0) * p, y, 26, C.fig);
    text('0:00', x0, y + 80, '600 40px Plex', C.sec, 'left'); text('4:00', x1, y + 80, '600 40px Plex', C.sec, 'right');
    const rec = 1 - prog(t, ts - 0.2, 0.3);
    if (rec > 0) { ctx.save(); ctx.globalAlpha *= rec; redGlow(10); circ(x0 + 14, 360, 16, C.red); noGlow(); text('RECORDING', x0 + 44, 375, '900 46px M', C.fig, 'left'); ctx.restore(); }
    if (t >= ts - 0.2) pop(t, ts - 0.2, 960, 340, () => { ctx.save(); redGlow(20); rrS(x0, 290, 300, 110, 12, C.red, 6); ctx.restore(); rr(x0, 290, 300, 30, 0, C.red); text('03:02', x0 + 150, 380, '900 52px M', C.red); text('SCHEDULED', x0 + 340, 375, '900 58px M', C.red, 'left'); });
  });
};
S.a8 = (t, seg) => {
  const tc = wt(seg, 'close'), td = wt(seg, 'delete'), ta = wt(seg, 'as'), close = ease(prog(t, wt(seg, 'minute') + 0.1, 0.4));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 760, 520, () => {
    ctx.save(); ctx.translate(760, 540); ctx.scale(lerp(1, 0.2, close), lerp(1, 0.2, close)); ctx.globalAlpha *= 1 - close * 0.9; ctx.translate(-760, -540);
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 60, people: [hoodieMe({})], bar: lerp(0.15, 0.25, prog(t, seg.start, tc - seg.start + 1)), limit: 0.25, playing: false }));
    ctx.restore();
    if (close > 0.5) phone(760, 540, 1.0, () => lockScreen(t, { time: '3:15' }), { bright: 0.5 });
  });
  if (t >= tc) slideIn(t, tc, 40, 0, () => { text('STOP AT', 1420, 300, '900 46px M', C.fig); text('1:00', 1420, 380, '900 80px M', '#ffd34d'); });
  if (t >= td) slideIn(t, td, 40, 0, () => xTag('DELETE', 1420, 520, 50, prog(t, td + 0.3, 0.3)));
  if (t >= ta) pop(t, ta, 1420, 700, () => tag('NO ENDING', 1420, 710, C.fig, 50, 'center'));
};
// if you watch to the end: the arm, the ankle, the fall, and you are pulled under the sofa
S.a9 = (t, seg) => {
  // the arm comes out, closes on your ankle and yanks it; you go down on your back and are pulled feet first into the dark under the sofa
  const gr = evAfter('grab', seg.end), dr = evAfter('drag', seg.end);
  const tg = gr ? gr.t : seg.end + 0.8, td = dr ? dr.t : seg.end + 1.5;
  const reach = ease(prog(t, tg - 0.45, 0.45)), yank = easeOut(prog(t, tg, td - tg)), fallen = t >= td;
  const p = prog(t, td + 0.12, 1.35), pull = p * p * (1.6 - 0.6 * p);   // slow at first, then it takes you all at once
  const fx = SPOT.x - 0.1, fz = lerp(SPOT.z + 0.15, SOFA.z1 - 1.75, pull);
  const standing = { pose: poseOf({ look: lerp(0.2, -0.6, yank), lean: -0.35 * yank, footL: [lerp(ANKLE[0], ANKLE[0] + 0.05, yank), 0.05 + 0.1 * yank, lerp(ANKLE[1], ANKLE[1] - 0.35, yank)],
    L: [-0.3 - 0.1 * yank, 0.8 + 0.7 * yank, 0.1], R: [0.3 + 0.1 * yank, 0.8 + 0.75 * yank, 0.1] }), o: { top: HOOD_C, hood: true } };
  const feetZ = fz, armOut = !fallen || feetZ > SOFA.z1 + 0.02;
  feed(t, { z: zk(t, seg.start, td - seg.start + 1.4, 1.1, 1.45), focus: [SPOT.x, 0.35, (SPOT.z + SOFA.z1) / 2 + 0.2], clock: T302 + 236 + (t - seg.start), bar: lerp(0.97, 1, prog(t, seg.start, td - seg.start)),
    shift: fallen ? 0.6 * (1 - p) : 0, people: fallen ? [] : [standing], thing: { eye: 1 },
    arm: !armOut ? null : fallen ? { k: 1, to: [fx, feetZ], grip: true, over: false } : { k: reach, to: [standing.pose.footL ? standing.pose.footL[0] : ANKLE[0], standing.pose.footL ? standing.pose.footL[2] : ANKLE[1]], grip: reach > 0.95, over: true },
    lying: fallen && pull < 1 ? [{ x: fx, z: fz, a: 0, under: false, o: { top: HOOD_C, clipZ: SOFA.z1 - 0.02, reach: 1, wig: t * 16 } }] : [],
    front: () => { if (fallen) { ctx.save(); ctx.globalAlpha = 0.6; for (let i = 0; i < 4; i++) { const x = SPOT.x - 0.32 + i * 0.07 + (i > 1 ? 0.12 : 0); lnW([x, 0.006, Math.max(SOFA.z1, fz + 1.5)], [x, 0.006, SPOT.z + 1.5], 3, '#8a8a90'); } ctx.restore(); } } });
  redFlash(t, tg, 0.1);
};

// ---------- rule 2: do not wear what you wear in it ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT WEAR WHAT YOU WEAR IN IT');
S.b1 = (t, seg) => {
  const to = wt(seg, 'only');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 9 + (t - seg.start), people: [{ pose: walkIn(t, seg.start - 1.5), o: { top: HOOD_C, hood: true } }], bar: prog(t, seg.start, 3) * 0.24, limit: 0.25, playing: true }));
  });
  if (t >= to) pop(t, to, 1420, 380, () => tag('FIRST MINUTE ONLY', 1420, 390, '#ffd34d', 46, 'center'));
};
S.b2 = (t, seg) => {
  // in the clip: the grey hoodie. Then the real room: the same hoodie on your chair
  const tg = wt(seg, 'grey'), to = wt(seg, 'one'), real = t >= to - 0.1;
  if (!real) { feed(t, { z: zk(t, seg.start, to - seg.start, 1.2, 1.6), focus: [SPOT.x, 1.2, SPOT.z], clock: T302 + 30, people: [hoodieMe({})] });
    if (t >= tg) { const j = skeleton(poseOf({})); feedTag(t, tg, 'GREY HOODIE', j.chest, 1360, 260, C.fig, 48); } }
  else { view(t, to - 0.1, seg.end - to + 0.9, 1.35, 1.6, [CHAIR.x, 0.7, CHAIR.z], { cam: CAMS.chair, hoodie: 'hang', lamp: 1, moon: 1 });
    pop(t, to + 0.2, 1420, 280, () => tag('RIGHT NOW', 1420, 290, C.red, 54, 'center')); }
};
S.b3 = (t, seg) => {
  const tf = wt(seg, 'faces'), th = wt(seg, 'hoodie');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.6, 1.9), focus: [SPOT.x, 1.25, SPOT.z], clock: T302 + 31, people: [{ pose: poseOf({}), o: { top: HOOD_C, hood: true, mark: t >= th } }] });
  const hp = feedPt(skeleton(poseOf({})).head);
  if (hp && t >= tf) pop(t, tf, hp[0], hp[1], () => { ctx.save(); ctx.globalAlpha *= 0.95; rr(hp[0] - 70, hp[1] - 70, 140, 140, 10, '#2a2a2e'); ctx.globalAlpha = 0.6; ctx.drawImage(grainC[Math.floor(t * 20) % 4], hp[0] - 70, hp[1] - 70, 140, 140); ctx.restore(); text('?', hp[0], hp[1] + 30, '900 90px M', C.fig); });
  if (t >= tf) slideIn(t, tf, 40, 0, () => xTag('FACE', 1500, 330, 50, prog(t, tf + 0.3, 0.3)));
  if (t >= th) pop(t, th, 1500, 470, () => tag('HOODIE', 1500, 480, C.red, 54, 'center'));
};
// a street at night: lamp post, the bin, you throwing the hoodie in
function street(t, o = {}) {
  rr(0, 760, W, 320, 0, '#101012'); ln(0, 760, W, 760, 4, '#2c2c30');
  for (let x = 0; x < W; x += 240) ln(x, 900, x + 120, 900, 6, '#26262a');
  ctx.save(); glow('rgba(255,226,170,0.8)', 40); ln(1460, 760, 1460, 250, 12, '#5a5a5e'); ln(1460, 250, 1380, 250, 10, '#5a5a5e'); rr(1340, 248, 80, 22, 8, '#ffe2aa'); ctx.restore();
  const g = ctx.createRadialGradient(1380, 300, 10, 1380, 600, 520); g.addColorStop(0, 'rgba(255,226,170,0.14)'); g.addColorStop(1, 'rgba(255,226,170,0)'); ctx.fillStyle = g; ctx.fillRect(900, 250, 1000, 600);
  ctx.save(); glow('rgba(255,255,255,0.2)', 14); rr(1120, 560, 190, 200, 12, '#4a4a50'); rr(1104, 540, 222, 36, 10, '#5c5c62'); ctx.restore();
}
S.b4 = (t, seg) => {
  const tt = wt(seg, 'throw'), tb = wt(seg, 'bin'), k = ease(prog(t, tb - 0.2, 0.7));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 1100, 560, () => {
    street(t);
    person(820, 760, 0.85, C.fig, prog(t, tb - 0.3, 0.3) * (1 - prog(t, tb + 0.4, 0.3)), 0, { eye: true });
    const x = lerp(860, 1215, k), y = lerp(520, 545, k) - Math.sin(k * Math.PI) * 180;
    if (k < 1) { ctx.save(); ctx.translate(x, y); ctx.rotate(k * 4); glow('rgba(255,255,255,0.2)', 10); rr(-50, -30, 100, 60, 18, HOOD_C); ctx.restore(); }
  });
  if (t >= tt) slideIn(t, tt, 40, 0, () => tag('TONIGHT', 1560, 220, C.fig, 50, 'center'));
};
S.b5 = (t, seg) => {
  const tf = wt(seg, 'folded');
  view(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.7, [CHAIR.x, 0.6, CHAIR.z], { cam: CAMS.chair, hoodie: 'folded', sun: 0.7 });
  slideIn(t, seg.start + 0.3, 40, 0, () => text('7:00 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tf) pop(t, tf, 1420, 330, () => tag('FOLDED', 1420, 340, C.red, 60, 'center'));
};
S.b6 = (t, seg) => {
  const tp = wt(seg, 'put'), tb = wt(seg, 'bright'), tn = wt(seg, 'never');
  setCam(CAMS.side);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 500, () => {
    const pl = { x: 0.2, z: 1.9, yaw: -2.27 };
    ctx.save(); ctx.translate(-380, -40); setCam({ ...CAMS.side, f: 760 }); slideIn(t, seg.start, -40, 0, () => body3(poseOf(pl), { top: HOOD_C, hood: true })); ctx.restore();
    if (t >= tb) { ctx.save(); ctx.translate(380, -40); setCam({ ...CAMS.side, f: 760 }); pop(t, tb, 960, 500, () => body3(poseOf(pl), { top: '#ffffff', glow: 'rgba(255,255,255,0.7)' })); ctx.restore(); }
  });
  if (t >= tp + 0.2) { redX(580, 260, 60, prog(t, tp + 0.2, 0.3)); }
  if (t >= tb) check(1340, 260, 60, prog(t, tb + 0.3, 0.3));
  if (t >= tn) pop(t, tn, 1340, 860, () => tag('NEVER SEEN', 1340, 870, C.fig, 46, 'center'));
};
S.b7 = (t, seg) => {
  const tn = wt(seg, 'not');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.04, W / 2, 470, () => {
    feed(t, { rect: { x: 120, y: 180, w: 1000 }, z: 1.3, focus: [SPOT.x, 1.0, SPOT.z], clock: T302 + 40, people: [hoodieMe({})] });
    text('THE CLIP', 620, 830, '900 48px M', C.fig);
    setCam({ ...CAMS.side, f: 760 }); ctx.save(); ctx.translate(560, -60); slideIn(t, seg.start + 0.4, 40, 0, () => body3(poseOf({ x: 0.2, z: 1.9, yaw: -2.27 }), { top: '#ffffff', glow: 'rgba(255,255,255,0.6)' })); ctx.restore();
    text('YOU', 1560, 830, '900 48px M', C.fig);
  });
  if (t >= tn) check(1560, 260, 60, prog(t, tn, 0.3));
};

// ---------- rule 3: do not be home at 3 AM ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT BE HOME AT 3 AM');
// the outside of your front door: you lock it, the key turns
S.c1 = (t, seg) => {
  const tl = wt(seg, 'lock'), k = ease(prog(t, tl, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 900, 520, () => {
    rr(0, 0, W, H, 0, '#0c0c0d'); rr(0, 860, W, 220, 0, '#141416');
    ctx.save(); glow('rgba(255,255,255,0.12)', 30); rr(640, 120, 520, 740, 6, '#26262a'); ctx.restore(); rrS(640, 120, 520, 740, 6, '#55555a', 4);
    rrS(680, 160, 440, 300, 4, '#3a3a3e', 3); rrS(680, 500, 440, 320, 4, '#3a3a3e', 3);
    circ(1100, 500, 20, '#77777c'); ctx.save(); ctx.translate(1100, 560); ctx.rotate(k * Math.PI / 2); rr(-4, -16, 8, 32, 3, '#111'); ctx.restore(); circS(1100, 560, 22, '#77777c', 5);
    // your hand on the key
    person(1340, 860, 0.9, C.fig, 0, 0, { eye: true, hand: { x: 1112, y: 566 } });
    text(NUM, 900, 230, '900 64px M', '#55555a');
  });
  slideIn(t, seg.start + 0.2, 40, 0, () => text('2:30 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tl + 0.4) pop(t, tl + 0.4, 1560, 340, () => tag('LOCKED', 1560, 350, C.fig, 50, 'center'));
};
// somewhere bright, with people: an all-night store window
function store(t) {
  rr(0, 0, W, H, 0, '#08080a'); rr(0, 820, W, 260, 0, '#121214');
  ctx.save(); glow('rgba(255,250,230,0.5)', 60); rr(300, 160, 1320, 560, 8, '#e9e6dc'); ctx.restore();
  for (let i = 0; i < 4; i++) rr(340 + i * 330, 200, 260, 380, 6, '#d2cfc4');
  for (let i = 0; i < 5; i++) ln(320, 260 + i * 80, 1600, 260 + i * 80, 3, '#c0bdb2');
  for (const [x, s] of [[520, 0.55], [880, 0.6], [1280, 0.52]]) person(x, 700, s, '#55555a');
  text('OPEN 24H', 960, 140, '900 54px M', '#ffd34d');
}
S.c2 = (t, seg) => {
  const to = wt(seg, 'open'), ph = ease(prog(t, to - 0.2, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, W / 2, 520, () => {
    store(t); person(960, 980, 0.95, C.fig, 0, 0, { eye: true });
    if (ph > 0) { ctx.save(); ctx.globalAlpha *= ph; ctx.translate(0, 80 * (1 - ph)); phone(1480, 560, 0.85, () => appScreen(t, { date: 'LIVE', clock: T302 - 1800 + (t - seg.start), bar: 1, title: 'Live' })); ctx.restore(); }
  });
};
S.c3 = (t, seg) => {
  const te = wt(seg, 'empty'), tx = wt(seg, 'except');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08), date: 'LIVE', clock: T302 + (t - seg.start) });
  if (t >= te) pop(t, te, 960, 240, () => tag('EMPTY', 960, 250, C.fig, 54, 'center'));
  if (t >= tx) { slideIn(t, tx, 40, 0, () => { feed(t, { rect: { x: 1240, y: 520, w: 480 }, z: 1.3, focus: [SPOT.x, 1, SPOT.z], clock: T302 + 14, people: [hoodieMe({})] }); text('THE CLIP', 1480, 830, '900 34px M', C.sec); }); }
};
S.c4 = (t, seg) => {
  const tm = wt(seg, 'moves'), sh = t >= tm ? Math.max(0, 1 - (t - tm) / 0.9) : 0;
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.4), focus: [-0.4, 0.3, SOFA.z1], date: 'LIVE', clock: T302 + 9 + (t - seg.start), shift: sh });
  if (t >= tm) pop(t, tm, 1420, 260, () => tag('IT MOVED', 1420, 270, C.red, 54, 'center'));
};
S.c5 = (t, seg) => {
  const ta = wt(seg, 'arm'), tj = wt(seg, 'joint'), tj2 = wt(seg, 'joint', 2);
  const k = t < ta ? 0.15 * prog(t, seg.start + 0.6, ta - seg.start - 0.6) : t < tj ? lerp(0.15, 0.35, ease(prog(t, ta, 0.4))) : t < tj2 ? lerp(0.35, 0.6, ease(prog(t, tj, 0.4))) : lerp(0.6, 0.8, ease(prog(t, tj2, 0.4)));
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.6), focus: [-0.3, 0.1, SOFA.z1 + 0.4], date: 'LIVE', clock: T302 + 13 + (t - seg.start), thing: { eye: 0.7 }, arm: { k, to: [SPOT.x, SPOT.z + 0.1] } });
  if (t >= tj) feedTag(t, tj, 'JOINT', armPath([THING_X, SOFA.z1 - 0.1], [SPOT.x, SPOT.z + 0.1])[3], 1420, 270, C.fig, 46);
  if (t >= tj2) feedTag(t, tj2, 'ANOTHER JOINT', armPath([THING_X, SOFA.z1 - 0.1], [SPOT.x, SPOT.z + 0.1])[5], 1420, 420, C.red, 46);
};
S.c6 = (t, seg) => {
  const ts = wt(seg, 'standing'), sweep = Math.sin((t - seg.start) * 1.6);
  const to = [SPOT.x + 0.35 * sweep, SPOT.z + 0.15 + 0.2 * Math.cos((t - seg.start) * 1.1)];
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.35, 1.5), focus: [SPOT.x, 0.3, SPOT.z - 0.3], date: 'LIVE', clock: T302 + 18 + (t - seg.start), thing: { eye: 0.7 }, arm: { k: 1, to },
    front: () => { if (t >= ts - 0.3) { ctx.save(); ctx.globalAlpha *= 0.6 * prog(t, ts - 0.3, 0.4); ctx.setLineDash([10, 10]); const j = skeleton(poseOf({}));
      const a = prj(j.head), b = prj(j.foot.L), c = prj(j.foot.R); if (a && b && c) { circS(a[0], a[1], 0.11 * a[3], C.fig, 4); ln(a[0], a[1] + 0.12 * a[3], (b[0] + c[0]) / 2, b[1], 4, C.fig); ln(b[0], b[1], c[0], c[1], 4, C.fig); } ctx.restore(); } } });
  if (t >= ts) pop(t, ts, 1420, 270, () => tag('WHERE YOU SHOULD BE', 1420, 280, C.fig, 44, 'center'));
};
S.c7 = (t, seg) => {
  const tn = wt(seg, 'nothing'), te = wt(seg, 'eye'), tc = wt(seg, 'camera'), hd = prog(t, te - 0.4, tc - te + 0.6);
  feed(t, { z: zk(t, te - 0.4, seg.end - te + 1.2, 1.4, 2.3), focus: [THING_X, 0.1, SOFA.z1 + 0.1], date: 'LIVE', clock: T302 + 26 + (t - seg.start), thing: { eye: 1, head: hd }, arm: { k: 1, to: [SPOT.x, SPOT.z + 0.15] } });
  if (t >= tn) pop(t, tn, 1420, 260, () => tag('NOTHING', 1420, 270, C.fig, 50, 'center'));
  redFlash(t, tc, 0.08);
};
S.c8 = (t, seg) => {
  const tb = wt(seg, 'black'), off = prog(t, tb - 0.15, 0.25);
  feed(t, { z: 2.3, focus: [THING_X, 0.1, SOFA.z1 + 0.1], date: 'LIVE', clock: T302 + 31 + (t - seg.start), thing: { eye: 1, head: 1 }, arm: { k: 1, to: [SPOT.x, SPOT.z + 0.15] }, noise: prog(t, seg.start, 0.6), off });
};
S.c9 = (t, seg) => {
  const tg = wt(seg, 'go'), ts = wt(seg, 'sun'), sk = ease(prog(t, ts - 0.1, 1.0));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 520, () => {
    store(t); person(960, 980, 0.95, C.fig, 0, 0, { eye: true });
    if (sk > 0) { ctx.save(); ctx.globalAlpha *= sk; icon('sun', 1640, lerp(420, 260, sk), 1.1); ctx.restore(); }
  });
  if (t >= tg) slideIn(t, tg, 40, 0, () => xTag('GO BACK', 330, 800, 52, prog(t, tg + 0.3, 0.3)));
  if (t >= ts) pop(t, ts, 1560, 790, () => tag('STAY UNTIL SUNRISE', 1560, 800, C.fig, 40, 'center'));
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const tn = wt(seg, 'tonight'), flip = t >= tn - 0.05;
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(2.2, 2.2); ctx.translate(-1600, -890);
    feed(t, { clock: T302 + 236 + (t - seg.start), date: flip ? 'TONIGHT' : 'TOMORROW', noise: flip ? 0.4 * (1 - prog(t, tn, 0.5)) : 0, people: [hoodieMe({})], bar: 1 }); ctx.restore();
  });
  if (flip) redFlash(t, tn, 0.1);
};
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
// the camera, close: the plug comes out, the light turns red, it keeps recording
S.d3 = (t, seg) => {
  const tu = wt(seg, 'unplug'), tr = wt(seg, 'red'), tk = wt(seg, 'keeps'), out = ease(prog(t, tu + 0.1, 0.4));
  const cc = { x: CCTV.x - 1.0, y: CCTV.y - 0.4, z: CCTV.z - 1.1, yaw: -2.4, pitch: 0.24, f: 1700 };
  setCam(cc); const f = prj([CCTV.x, CCTV.y - 0.1, CCTV.z]) || [W / 2, H / 2];
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15, f[0], f[1], () => {
    living(t, { cctvDev: { led: t >= tr ? 'red' : 'green' } });
    const a = prj([CCTV.x - 0.02, CCTV.y - 0.12, CCTV.z]), b = prj([CCTV.x - 0.02 - 0.3 * out, CCTV.y - 0.9 - 0.3 * out, CCTV.z - 0.1]);
    if (a && b) { ln(a[0], a[1], lerp(a[0], b[0], 0.3), b[1] - 200, 5, '#bdbdbd'); ln(lerp(a[0], b[0], 0.3), b[1] - 200, b[0], b[1], 5, '#bdbdbd'); rr(b[0] - 18, b[1] - 6, 36, 40, 6, '#e8e8e8'); }
  });
  if (t >= tu) slideIn(t, tu, 40, 0, () => xTag('UNPLUG IT', 400, 300, 50, prog(t, tu + 0.3, 0.3)));
  if (t >= tk) pop(t, tk, 400, 450, () => { ctx.save(); redGlow(12); circ(310, 452, 14, C.red); ctx.restore(); text('STILL RECORDING', 340, 466, '900 40px M', C.red, 'left'); });
};
S.d4 = (t, seg) => {
  const th = wt(seg, 'hide'), ts = wt(seg, 'second'), tb = wt(seg, 'bedroom', 2);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 60, people: [hoodieMe({})], bar: 1, clips: [['Living room', 'Tomorrow · 3:02 AM', true], ['Bedroom', 'Tomorrow · 3:04 AM', true, ts]] }));
  });
  if (t >= th) slideIn(t, th, 40, 0, () => xTag('HIDE IN THE BEDROOM', 1420, 300, 42, prog(t, th + 0.3, 0.3)));
  if (t >= tb) pop(t, tb, 1420, 470, () => tag('BEDROOM 03:04', 1420, 480, C.red, 50, 'center'));
};
S.d5 = (t, seg) => {
  const tc = wt(seg, 'call'), tf = wt(seg, 'clip'), clip = t >= tf - 0.1;
  if (!clip) cam(t, seg.start, tf - seg.start, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => { rr(0, 0, SW, SH, 0, '#0b0b0c'); statusBar('2:51'); circ(SW / 2, 240, 70, '#2a2a2e'); circ(SW / 2, 222, 26, '#8a8a90'); rr(SW / 2 - 40, 254, 80, 40, 20, '#8a8a90');
      text('Calling…', SW / 2, 380, `600 30px ${UI}`, '#f2f2f2'); circ(SW / 2, 680, 40, C.red); }); });
  else feed(t, { z: zk(t, tf, seg.end - tf + 0.8, 1.2, 1.4), focus: [SPOT.x, 0.2, SPOT.z - 0.3], clock: T302 + 200, thing: { eye: 1 },
    lying: [{ x: SPOT.x - 0.1, z: SPOT.z - 0.4, a: 0.3, o: { col: '#d8d8dc' } }], arm: { k: 1, to: [SPOT.x - 0.1, SPOT.z - 0.4], grip: true, over: true } });
  if (t >= tc && !clip) slideIn(t, tc, 40, 0, () => xTag('CALL SOMEONE', 1420, 300, 46, prog(t, tc + 0.3, 0.3)));
  if (clip) pop(t, tf + 0.3, 1420, 260, () => tag('THEM, NOT YOU', 1420, 270, C.red, 50, 'center'));
};
S.d6 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
// ---------- the bait and the knife (the camera never moves: it sees the whole room, always) ----------
const BAIT_AT = [SPOT.x, SPOT.z];
const HIDE = { x: 1.08, z: 0.62, yaw: 1.75 };                                  // crouched past the end of the sofa, out of its reach, facing the rug
const PIECE = { c: [0.12, 0, 1.36], a: 0.35 };                                     // where the cut-off joint ends up
const bright = { top: '#f4f4f6', legs: '#d4d4d8', col: C.fig };
const hider = (o = {}) => ({ pose: poseOf({ x: HIDE.x, z: HIDE.z, yaw: HIDE.yaw, crouch: 1, lean: 0.25, look: 0.2, L: [-0.2, 0.55, 0.25], R: [0.18, 0.62, 0.3], ...o.pose }), o: { ...bright, knife: o.knife ?? 1, knifeDir: o.knifeDir || [-0.3, 0.85, -0.2] } });
const armFrom = to => [THING_X + 0.24 * (to[0] < THING_X ? -1 : 1), SOFA.z1 - 0.1];
// it doesn't know your face, only the hoodie
S.d7 = (t, seg) => {
  const tf = wt(seg, 'face'), th = wt(seg, 'hoodie');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.3, 1.6), focus: [SPOT.x + 0.2, 1.0, SPOT.z - 0.2], clock: T302 + 31 + (t - seg.start), thing: { eye: 0.8 },
    people: [{ pose: poseOf({}), o: { top: HOOD_C, hood: true, mark: t >= th } }] });
  const hp = feedPt(skeleton(poseOf({})).head);
  if (hp && t >= tf) pop(t, tf, hp[0], hp[1], () => { ctx.save(); ctx.globalAlpha *= 0.95; rr(hp[0] - 56, hp[1] - 56, 112, 112, 10, '#2a2a2e'); ctx.globalAlpha = 0.6; ctx.drawImage(grainC[Math.floor(t * 20) % 4], hp[0] - 56, hp[1] - 56, 112, 112); ctx.restore(); text('?', hp[0], hp[1] + 26, '900 76px M', C.fig); });
  if (t >= tf) slideIn(t, tf, 40, 0, () => xTag('FACE', 1500, 330, 50, prog(t, tf + 0.3, 0.3)));
  if (t >= th) pop(t, th, 1500, 470, () => tag('ONLY THE HOODIE', 1500, 480, C.red, 50, 'center'));
};
// roll the rug up, stand it where you stood, put the hoodie on it
S.d8 = (t, seg) => {
  const tr = wt(seg, 'roll'), ts = wt(seg, 'stand'), tw = wt(seg, 'where'), th = wt(seg, 'hoodie');
  const roll = ease(prog(t, tr + 0.1, 1.1)), stand = prog(t, ts, 0.8), hood = prog(t, th - 0.15, 0.5), ghost = prog(t, tw, 0.4) * (1 - prog(t, th, 0.4));
  const bait = { roll, stand, hood, pos: BAIT_AT };
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.4), focus: [SPOT.x, 0.5, SPOT.z - 0.1], date: 'TONIGHT', clock: T302 - 1800 + (t - seg.start), lamp: 1, rug: 1 - roll, bait,
    front: () => { if (ghost > 0) { ctx.save(); ctx.globalAlpha *= 0.7 * ghost; ctx.setLineDash([10, 10]); const j = skeleton(poseOf({}));
      const a = prj(j.head), b = prj(j.foot.L), c = prj(j.foot.R); if (a && b && c) { circS(a[0], a[1], 0.11 * a[3], C.fig, 4); ln(a[0], a[1] + 0.12 * a[3], (b[0] + c[0]) / 2, b[1], 4, C.fig); ln(b[0], b[1], c[0], c[1], 4, C.fig); } ctx.restore(); } } });
  if (t < th) feedTag(t, wt(seg, 'rug'), 'RUG', stand > 0 ? V3.add(baitBase(bait), V3.mul(baitDir(bait), 0.7)) : baitBase(bait), 'rel', [-330, -260], C.fig, 46);
  else feedTag(t, th + 0.3, 'HOODIE', baitTop(bait), 'rel', [-340, -150], C.fig, 46);
  if (t >= tw && t < th) pop(t, tw, 1450, 270, () => tag('WHERE YOU STOOD', 1450, 280, C.fig, 44, 'center'));
};
// lights off, something bright on, crouched at the end of the sofa with a kitchen knife
S.d9 = (t, seg) => {
  const to = wt(seg, 'off'), tb = wt(seg, 'bright'), tw = wt(seg, 'wait'), tk = wt(seg, 'kitchen');
  const lamp = 1 - prog(t, to, 0.12), dark = t < to ? 0 : 0.75 - 0.45 * ease(prog(t, to + 0.2, 0.7));   // black, then the camera's night mode finds the room
  const appear = prog(t, tb - 0.4, 0.4), go = ease(prog(t, tw, 1.0));
  const ps = { x: lerp(1.15, HIDE.x, go), z: lerp(1.55, HIDE.z, go), yaw: lerp(2.5, HIDE.yaw, go), crouch: go, lean: 0.25 * go, look: 0.2, L: [-0.25, lerp(0.8, 0.55, go), 0.1 + 0.15 * go], R: [lerp(0.25, 0.18, go), lerp(0.8, 0.62, go), 0.1 + 0.2 * go], walk: go > 0 && go < 1, step: (t - tw) * 9 };
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35), focus: [0.0, 0.6, 1.35], date: 'TONIGHT', clock: T302 - 600 + (t - seg.start), lamp, rug: 0, dark, noise: t >= to ? 0.5 * (1 - prog(t, to, 0.8)) : 0,
    bait: { roll: 1, stand: 1, hood: 1, pos: BAIT_AT },
    people: appear > 0 ? [{ pose: poseOf(ps), o: { ...bright, knife: t >= tk ? prog(t, tk, 1.4) : 0, knifeDir: [-0.3, 0.85, -0.2] } }] : [] });
  if (appear > 0) { const j = skeleton(poseOf(ps)); feedTag(t, tb, 'BRIGHT', j.chest, 'rel', [300, -230], C.fig, 46);
    if (t >= tk) feedTag(t, tk + 0.1, 'KNIFE', j.hand.R, 'rel', [320, 60], C.fig, 46); }
  if (t >= to) slideIn(t, to, 40, 0, () => tag('LIGHTS OFF', 330, 270, C.fig, 44, 'center'));
};
// 3:02: the arm slides out and its fingers close around the rug
const GRIP = [BAIT_AT[0] + 0.1, BAIT_AT[1] - 0.12];
S.d10 = (t, seg) => {
  const tt = wt(seg, 'two'), ts = wt(seg, 'slides'), tc = wt(seg, 'close');
  const k = easeOut(prog(t, ts - 0.1, tc - ts + 0.1));
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 1.0, 1.3, 1.75), focus: [-0.05, 0.4, 1.4], date: 'TONIGHT', clock: T302 + (t - seg.start), rug: 0, dark: 0.3,
    thing: { eye: 0.4 + 0.6 * prog(t, seg.start + 0.4, 1.0) }, bait: { roll: 1, stand: 1, hood: 1, pos: BAIT_AT },
    arm: k > 0 ? { k, to: GRIP, grip: t >= tc, over: true } : null, people: [hider({ pose: { look: 0.2 + 0.05 * Math.sin(t * 2) } })] });
  if (t >= tt) pop(t, tt, 1450, 260, () => tag('03:02', 1450, 270, C.red, 64, 'center'));
};
// it pulls; you come up out of the corner and bring the knife down on the joint closest to the sofa
const PULL = (t, t0) => ease(prog(t, t0, 2.4));
S.d11 = (t, seg) => {
  const tp = wt(seg, 'pulls'), ts = wt(seg, 'strike'), td = wt(seg, 'down'), tj = wt(seg, 'joint');
  const pl = PULL(t, tp), pos = [BAIT_AT[0] + 0.05 * pl, BAIT_AT[1] - 0.42 * pl], bait = { roll: 1, stand: 1, hood: 1, pos, tilt: 0.38 * pl + 0.04 * Math.sin(t * 13) * pl * (t < td ? 1 : 0) };
  const cut = t - td, jit = cut > 0 ? Math.sin(t * 47) * 0.05 * Math.exp(-cut * 1.6) : 0;
  const to = [GRIP[0] + pos[0] - BAIT_AT[0] + jit, GRIP[1] + pos[1] - BAIT_AT[1]], J = armPath(armFrom(to), to)[1];
  // you: up from the corner (strike), the knife high, then down onto that joint
  const lunge = ease(prog(t, ts, 0.6)), down = easeOut(prog(t, td - 0.12, 0.12)), back = ease(prog(t, td + 0.5, 0.8));
  const stand = [J[0] + 0.5, J[2] + 0.02], x = lerp(lerp(HIDE.x, stand[0], lunge), stand[0] + 0.3, back), z = lerp(lerp(HIDE.z, stand[1], lunge), stand[1] + 0.05, back);
  const yaw = lerp(HIDE.yaw, Math.atan2(-(J[0] - x), -(J[2] - z)), lunge);
  const ps0 = { x, z, yaw, crouch: lerp(1, 0.15, lunge) + 0.45 * down * (1 - back), lean: lerp(0.25, -0.1, lunge) + 0.45 * down * (1 - back), look: 0.3 + 0.5 * down };
  const hi = [x + (J[0] - x) * 0.35, 1.85, z + (J[2] - z) * 0.35], lo = [J[0] + 0.05, J[1] + 0.12, J[2] + 0.03], rest = [x - 0.1, 0.7, z - 0.05];
  const hw = t < ts ? null : t < td - 0.12 ? hi : back > 0 ? V3.lerp(lo, rest, back) : V3.lerp(hi, lo, down);
  const ps = { ...ps0, L: [-0.25, lerp(0.55, 1.1, lunge) - 0.4 * down, 0.2], R: hw ? handAt(ps0, hw) : [0.18, 0.62, 0.3] };
  const kd = t < ts ? [-0.3, 0.85, -0.2] : t < td - 0.12 ? [0, 1, 0] : back > 0 ? [-0.2, 0.6, -0.3] : V3.norm(V3.lerp([0, 1, 0], [0, -1, 0.1], down));
  const shake = cut > 0 && cut < 0.35 ? (1 - cut / 0.35) * 14 : 0;
  feed(t, { rect: { x: FR.x + Math.sin(t * 90) * shake, y: FR.y + Math.cos(t * 77) * shake * 0.6, w: FR.w }, z: zk(t, seg.start, td - seg.start + 0.3, 1.35, 2.1), focus: [lerp(-0.2, J[0] + 0.2, 0.8), 0.4, lerp(1.45, J[2], 0.8)],
    date: 'TONIGHT', clock: T302 + 5 + (t - seg.start), rug: 0, dark: 0.3, thing: { eye: 1 }, bait, ooze: cut > 0 ? { c: [J[0], 0, J[2] + 0.04], k: cut } : null,
    piece: cut > 0 ? { c: V3.lerp([J[0], 0, J[2]], PIECE.c, easeOut(clamp(cut / 0.35))), a: PIECE.a, tw: Math.exp(-cut * 1.2) } : null,
    arm: { k: 1, to, grip: true, over: true }, people: [{ pose: poseOf(ps), o: { ...bright, knife: 1, knifeDir: kd } }],
    front: () => { if (cut > 0) { const q = prj(J); if (q) { ctx.save(); ell(q[0], q[1], 0.04 * q[3], 0.03 * q[3], 0, '#050505'); for (let i = 0; i < 3; i++) { const dy = ((cut * 0.6 + i * 0.33) % 1) * 0.15 * q[3]; circ(q[0] + (i - 1) * 0.015 * q[3], q[1] + dy, 0.009 * q[3], '#050505'); } ctx.restore(); } } } });
  if (t >= ts && t < td + 0.1) feedTag(t, ts + 0.15, 'THIS JOINT', J, 'rel', [-380, -200], C.red, 44);
  if (t >= tj) pop(t, tj, 1450, 260, () => tag('CLOSEST TO THE SOFA', 1450, 270, C.fig, 42, 'center'));
};
// it lets go; the arm goes back into the dark, one joint shorter
S.d12 = (t, seg) => {
  const tl = wt(seg, 'lets'), tsl = wt(seg, 'slips'), td = wt(seg, 'dark'), tsh = wt(seg, 'shorter');
  const pos = [BAIT_AT[0] + 0.05, BAIT_AT[1] - 0.42], fall = easeOut(prog(t, tl, 0.55));
  const to = [GRIP[0] + 0.05, GRIP[1] - 0.42], k = 1 - ease(prog(t, tsl, 0.9)), opn = t >= tl;
  const J = armPath(armFrom(to), to)[1], sh = t >= td - 0.2 ? Math.max(0, 1 - (t - td + 0.2) / 0.8) : 0;
  const me = poseOf({ x: J[0] + 0.8, z: J[2] + 0.07, yaw: Math.atan2(0.8, 0.07), crouch: 0.15, lean: -0.1, look: 0.3, L: [-0.25, 0.75, 0.15], R: [0.2, 0.7, 0.2] });
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.6, 1.9), focus: [lerp(J[0], PIECE.c[0], 0.5), 0.3, lerp(J[2], PIECE.c[2], 0.5) + 0.1], date: 'TONIGHT', clock: T302 + 12 + (t - seg.start), rug: 0, dark: 0.3,
    thing: { eye: 1 - prog(t, td, 0.6) }, shift: sh, bait: { roll: 1, stand: 1, hood: 1, pos, tilt: lerp(0.38, -1.48, fall) },
    ooze: { c: [J[0], 0, J[2] + 0.04], k: 3 + (t - seg.start) }, piece: { ...PIECE, tw: 0.15 },
    arm: k > 0.01 ? { k, to, grip: !opn, over: true } : null, people: [{ pose: me, o: { ...bright, knife: 1, knifeDir: [-0.2, 0.6, -0.3] } }] });
  if (t >= tsh) pop(t, tsh, 1450, 260, () => tag('ONE JOINT SHORTER', 1450, 270, C.fig, 46, 'center'));
};

// ---------- morning ----------
S.e1 = (t, seg) => {
  const tn = wt(seg, 'notification');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, W / 2, 470, () => phone(960, 520, 0.95, () => lockScreen(t, { time: '7:00', morning: true, notif: tn - 0.2, sub: 'Living room · now' })));
};
const AFTER = { rug: 0, bait: { roll: 1, stand: 1, hood: 1, pos: [BAIT_AT[0] + 0.05, BAIT_AT[1] - 0.42], tilt: -1.48 }, piece: PIECE, ooze: { c: [0.06, 0, 1.06], k: 9 } };
S.e2 = (t, seg) => {
  const tt = wt(seg, 'tomorrow'), z = ease(prog(t, seg.start + 0.3, 0.9));
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(lerp(1, 2.4, z), lerp(1, 2.4, z)); ctx.translate(-1600, -890);
    feed(t, { ...AFTER, clock: T302 + (t - seg.start), date: 'TOMORROW' }); ctx.restore();
  });
  if (t >= tt) { pop(t, tt, 760, 300, () => tag('AGAIN', 760, 310, C.red, 60, 'center')); redFlash(t, tt, 0.06); }
};
S.e3 = (t, seg) => {
  const te = wt(seg, 'empty'), tf = wt(seg, 'finger');
  feed(t, { ...AFTER, z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.2, 2.4), focus: [PIECE.c[0] + 0.15, 0.1, PIECE.c[2] + 0.1], clock: T302 + 4 + (t - seg.start), date: 'TOMORROW' });
  if (t >= te) pop(t, te, 1450, 260, () => tag('EMPTY', 1450, 270, C.fig, 54, 'center'));
  feedTag(t, tf, 'A FINGER', [PIECE.c[0] + 0.2, 0.06, PIECE.c[2] + 0.08], 'rel', [-380, -260], C.fig, 46);
};
S.e4 = (t, seg) => {
  // very slowly its head comes out from under the sofa and turns up to the lens: to you, watching
  const tt = wt(seg, 'turns'), tl = wt(seg, 'lens'), hd = prog(t, tt - 0.3, tl - tt + 0.6);
  feed(t, { ...AFTER, z: zk(t, seg.start, seg.end - seg.start + 1.6, 1.3, 2.6), focus: [THING_X, 0.12, SOFA.z1 + 0.2], clock: T302 + 9 + (t - seg.start), date: 'TOMORROW', thing: { eye: 1, head: hd } });
  redFlash(t, tl, 0.06);
};
// the file closes
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
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
