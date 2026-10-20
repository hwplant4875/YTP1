// ---------- EP02 scenes ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => ev(type).find(e => e.t >= t0 - 0.01);
// vibration of the phone around a buzz event (two pulses in the buzz file)
function buzzK(t) { for (const e of ev('buzz')) { const d = t - e.t; if (d >= 0 && d < 1.5) return (d < 0.5 || (d > 0.75 && d < 1.25)) ? 1 : 0; } return 0; }
const PHX = 960, PHY = 560, PHS = 1.3;                 // the standard phone close-up
// the AI's earlier messages, the ones every chat in this video starts from
const M_AWAKE = { text: 'Are you awake?', at: -1 };
const PHOTO = (stamp = '03:00:41', zoom = 1, n = 0) => (x, y, w, h) => ceilPhoto(x, y, w, h, { stamp, zoom, n });
const M_PHOTO = { photo: PHOTO(), ph: 300, at: -1 };
function phoneShot(t, seg, fn, o = {}) {
  cam(t, seg.start, seg.end - seg.start + 0.8, o.z0 ?? 1.04, o.z1 ?? 1.1, o.cx ?? PHX, o.cy ?? 470, () => {
    phone(o.x ?? PHX, o.y ?? PHY, o.s ?? PHS, fn, { bright: o.bright ?? 1, rot: o.rot || 0 });
    if (o.after) o.after();
  });
}
// labels beside the phone
const sideTag = (t, t0, s, x, y, col = C.fig, size = 44) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
// white icons for the opening "do not" row
function icon2(name, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'photo') { rrS(-90, -70, 180, 140, 14, C.fig, 10); circ(-20, 4, 26, C.fig); rr(8, -8, 56, 40, 14, C.fig); circ(52, -40, 10, C.fig); }
  if (name === 'ask') { rrS(-96, -70, 192, 120, 26, C.fig, 10); pth('M-50,48 L-70,94 L-14,50 Z', C.fig); text('?', 0, 20, '900 100px M', C.fig); }
  if (name === 'up') { pth('M-90,30 C-50,-26 50,-26 90,30 C50,86 -50,86 -90,30 Z', C.fig); noGlow(); circ(0, 30, 24, '#000'); glow(); ln(0, -40, 0, -110, 12, C.fig); pth('M-28,-96 L0,-130 L28,-96 Z', C.fig); }
  noGlow(); ctx.restore();
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  const tn = wt(seg, 'not');
  // the video opens on the phone: the photo has just arrived (frame 0 already shows it)
  phoneShot(t, { start: 0, end: seg.end }, () => chatScreen(t, [M_AWAKE, M_PHOTO]), { z0: 1.55, z1: 1.7, cy: 480 });
  if (t >= tn) pop(t, tn, 1500, 300, () => tag('DO NOT REPLY', 1500, 310, C.red, 54, 'center'), 0.3);
};
S.h2 = (t, seg) => {
  const items = [['photo', 520, 'open'], ['ask', 960, 'ask'], ['up', 1400, 'look']];
  cam(t, seg.start, seg.end - seg.start, 1, 1.04, W / 2, 470, () => {
    items.forEach(([ic, x, w]) => {
      const t0 = wt(seg, w) - 0.25;
      pop(t, t0, x, 470, () => { rrS(x - 170, 300, 340, 340, 26, C.dim, 5); icon2(ic, x, 470, 1.05); });
      redX(x, 470, 120, prog(t, wt(seg, w) + 0.35, 0.35));
    });
  });
};

// ---------- rule 1: do not reply ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT REPLY');
S.a1 = (t, seg) => {
  const tl = wt(seg, 'lights'), t3 = wt(seg, 'three');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.3, 1000, 600, () => {
    room2(t); bed(BX, FY, 1.05, 'sleep', {});
    phoneFlat(t >= tl ? easeOut(prog(t, tl, 0.25)) : 0, buzzK(t));
    cornerThing(t, { vis: t >= tl ? 0.1 : 0, lit: 0, face: 'lens', red: 0.5, breath: 0.6 }); if (t >= tl) lensGlint(0.8);
    if (t >= t3) pop(t, t3, 1400, 520, () => { redGlow(14); text('3:00', 1400, 560, '900 120px M', C.red); noGlow(); spaced('AM', 1400, 620, '900 32px M', C.mid, 8); });
  });
};
S.a2 = (t, seg) => {
  const to = wt(seg, 'one') - 0.1, tf = wt(seg, 'from'), ta = wt(seg, 'are');
  phoneShot(t, seg, () => lockScreen(t, { notes: [{ at: to, text: t >= ta - 0.1 ? 'Are you awake?' : '' }] }), { z0: 1.0, z1: 1.08, cy: 420 });
  sideTag(t, tf, 'YOUR AI', 360, 380, C.fig, 46);
};
S.a3 = (t, seg) => {
  const tdo = wt(seg, 'open'), task = wt(seg, 'ask'), tnv = wt(seg, 'never');
  const hist = [{ me: true, text: 'what time is sunrise?', at: -1 }, { text: '6:58 AM.', at: -1 }, { me: true, text: 'set an alarm for 7', at: -1 }, { text: 'Done. 7:00 AM.', at: -1 },
    { me: true, text: 'thanks', at: -1 }, { text: 'Are you awake?', at: -1, red: true, status: 'TODAY 3:00 AM', statusRed: true }];
  phoneShot(t, seg, () => chatScreen(t, hist), { x: 760, cx: 860 });
  const rows = [['YOU OPENED IT', tdo], ['YOU ASKED IT', task], ['IT SPOKE FIRST', tnv]];
  rows.forEach(([l, t0], i) => { if (t < t0) return; const y = 360 + i * 120;
    slideIn(t, t0, 40, 0, () => { const last = i === 2;
      rrS(1130, y - 40, 64, 64, 10, C.red, 5); text(l, 1220, y + 6, '900 50px M', last ? C.red : C.fig, 'left');
      if (!last) redX(1162, y - 8, 22, prog(t, t0 + 0.2, 0.3)); else { redGlow(12); text('!', 1162, y + 14, '900 56px M', C.red); noGlow(); } }); });
  if (t >= tnv + 0.4) pop(t, tnv + 0.4, 1420, 760, () => tag('FIRST TIME', 1420, 770, C.red, 46, 'center'));
};
S.a4 = (t, seg) => {
  const td = wt(seg, 'delivered'), tr = wt(seg, 'read'), ta = wt(seg, 'answer');
  // your thumb hovers over the message, then pulls away
  const hov = clamp((t - seg.start) / 0.6) * (1 - clamp((t - ta - 0.3) / 0.5));
  phoneShot(t, seg, () => { chatScreen(t, [{ ...M_AWAKE, status: t >= td ? 'Delivered' : '' }]); if (hov > 0) thumb(230, lerp(900, 330, hov)); });
  if (t >= ta) pop(t, ta, 360, 420, () => tag('DO NOT ANSWER', 360, 430, C.red, 46, 'center'));
  if (t >= td) slideIn(t, td, 40, 0, () => { rrS(1300, 510, 60, 60, 10, C.fig, 5); check(1330, 540, 22, prog(t, td + 0.1, 0.3)); text('DELIVERED', 1380, 560, '900 54px M', C.fig, 'left'); });
  if (t >= tr) slideIn(t, tr, 40, 0, () => { ctx.save(); ctx.globalAlpha *= 0.85; text('READ', 1380, 680, '900 54px M', C.mid, 'left'); ctx.restore(); redGlow(10); lnP(1360, 664, 1560, 664, 9, C.red, prog(t, tr + 0.15, 0.25)); noGlow(); });
};
S.a5 = (t, seg) => {
  const tp = wt(seg, 'photo') - 0.05;
  phoneShot(t, seg, () => chatScreen(t, [M_AWAKE, ...(t < tp ? [{ dots: true, at: seg.start + 0.4 }] : [{ ...M_PHOTO, at: tp }])]), { z0: 1.0, z1: 1.1, cy: 460 });
  fadeIn(t, seg.start + 0.1, () => spaced('1 MINUTE LATER', 360, 360, '900 34px M', C.mid, 6));
};
S.a6 = (t, seg) => {
  const tk = wt(seg, 'taken') - 0.05, tab = wt(seg, 'above'), tc = wt(seg, 'corner'), ttw = wt(seg, 'two');
  if (t < tk) {   // "You. Asleep." on the phone
    phoneShot(t, { start: seg.start, end: tk }, () => chatScreen(t, [M_AWAKE, M_PHOTO]), { z0: 1.1, z1: 1.5, cy: 470 });
    if (t >= wt(seg, 'asleep')) pop(t, wt(seg, 'asleep'), 1460, 420, () => tag('YOU', 1460, 430, C.fig, 60, 'center'));
    return;
  }
  // the photo, full size
  cam(t, tk, seg.end - tk + 0.8, 1.0, 1.06, 760, 540, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(196, 136, 1008, 708, 6, '#ddd'); ctx.restore();
    ceilPhoto(200, 140, 1000, 700, { stamp: '03:00:41', n: 0 });
    // the angle: a small cut-away of the room, a lens in the corner and its cone down onto the bed
    if (t >= tab) slideIn(t, tab, 40, 0, () => {
      const ox = 1290, oy = 300, sc = 0.28;
      rrS(ox - 14, oy - 14, 540, 252, 10, C.dim, 3);
      ctx.save(); ctx.translate(ox, oy); ctx.scale(sc, sc); ctx.translate(-WALL, -CEIL + 40);
      ln(WALL, CEIL, 1900, CEIL, 8, C.mid); ln(WALL, CEIL, WALL, FY, 8, C.mid); ln(WALL, FY, 1900, FY, 8, C.mid);
      bed(BX, FY, 1.05, 'sleep', {});
      if (t >= tc) { ctx.save(); redGlow(20); circ(LENS.x, LENS.y, 26, C.red); ctx.restore();
        ctx.save(); ctx.globalAlpha *= 0.35 * prog(t, tc, 0.4); pth(`M${LENS.x},${LENS.y} L${BX + 40},${FY - 230} L${BX + 640},${FY - 180} Z`, C.red); ctx.restore(); }
      ctx.restore();
      if (t >= tc) text('FROM THE CORNER', ox + 256, oy + 300, '900 34px M', C.red);
    });
    if (t >= ttw) pop(t, ttw, 700, 900, () => { redGlow(10); spaced('2 MINUTES AGO', 700, 918, '900 46px M', C.red, 6); noGlow(); });
  });
  // the flash it took the picture with
  const fk = 1 - clamp((t - tk) / 0.35); if (fk > 0) { ctx.save(); ctx.globalAlpha = fk * 0.85; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};
S.a7 = (t, seg) => {
  const ty = evAfter('typing', seg.end), sd = evAfter('send', seg.end), nt = evAfter('notif', seg.end), fl = evAfter('flash', seg.end);
  if (fl && t >= fl.t) {
    // the flash fires from the corner: for an instant, you can see what is holding on up there
    const d = t - fl.t;
    cam(t, fl.t, 0.4, 1.05, 1.12, 640, 460, () => {
      room2(t); bed(BX, FY, 1.05, 'woke', { look: -1 }); phoneInHand(t, 1);
      // the flash lights the walls from the corner; the thing itself stays a black shape in front of it
      const g = ctx.createRadialGradient(LENS.x, LENS.y, 20, LENS.x, LENS.y, 1500);
      g.addColorStop(0, 'rgba(255,255,255,0.85)'); g.addColorStop(0.5, 'rgba(230,230,230,0.45)'); g.addColorStop(1, 'rgba(200,200,200,0.12)');
      ctx.save(); ctx.globalAlpha = 1 - clamp(d / 0.3) * 0.45; ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore();
      cornerThing(t, { vis: 1, lit: 0, face: 'lens', red: 1, reach: clamp(d / 0.18), breath: 0 }); lensGlint(1);
    });
    const k = 1 - clamp(d / 0.08); if (k > 0) { ctx.save(); ctx.globalAlpha = 0.6 * k; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    return;
  }
  const typed = ty && sd && t >= ty.t ? clamp((t - ty.t) / (sd.t - ty.t - 0.1)) : 0, msg = 'who took this?';
  const msgs = [M_AWAKE, M_PHOTO];
  if (sd && t >= sd.t) msgs.push({ me: true, text: msg, at: sd.t, status: 'Read' });
  if (sd && nt && t >= sd.t + 0.15 && t < nt.t) msgs.push({ dots: true, at: sd.t + 0.15 });
  if (nt && t >= nt.t) msgs.push({ text: 'Hold still.', at: nt.t, red: true });
  phoneShot(t, { start: seg.start, end: fl ? fl.t : seg.end }, () => chatScreen(t, msgs, { input: sd && t >= sd.t ? '' : msg.slice(0, Math.round(msg.length * typed)) }), { z0: 1.0, z1: 1.18, cy: 600 });
};

// ---------- rule 2: do not look at the corner ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LOOK AT THE CORNER');
S.b1 = (t, seg) => {
  const ta = wt(seg, 'angle');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 900, 500, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(356, 156, 1008, 708, 6, '#ddd'); ctx.restore();
    ceilPhoto(360, 160, 1000, 700, { stamp: '03:00:41', n: 0 });
    // the lines of the bed run back to one point: up and to the left, outside the picture
    if (t >= ta) { const vp = { x: 130, y: -60 }, p = prog(t, ta, 0.7);
      [[560, 420], [1090, 330], [700, 800], [1250, 720]].forEach(([x, y], i) => { ctx.save(); ctx.setLineDash([16, 12]); lnP(x, y, vp.x, vp.y, 5, C.red, clamp(p * 1.4 - i * 0.12)); ctx.restore(); });
      if (p >= 1) pop(t, ta + 0.7, 300, 140, () => { tag('IT WAS UP HERE', 300, 150, C.red, 40, 'center'); }); }
  });
};
function cornerZoom(t, t0, d, z0, z1, fn) { cam(t, t0, d, z0, z1, 520, 360, fn); }
S.b2 = (t, seg) => {
  const tc = wt(seg, 'camera'), ts = wt(seg, 'shelf'), tn = wt(seg, 'nothing');
  cornerZoom(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {});
    const p = prog(t, seg.start + 0.1, 0.5); ctx.save(); ctx.setLineDash([14, 10]); redGlow(10); ctx.beginPath(); ctx.arc(CORNER.x + 190, CORNER.y + 170, 200, 0, Math.PI * 2 * p); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); });
  [['CAMERA', tc], ['SHELF', ts], ['ANYTHING TO STAND ON', tn]].forEach(([l, t0], i) => { if (t < t0) return; const y = 400 + i * 110;
    slideIn(t, t0, 40, 0, () => { rrS(1100, y - 40, 64, 64, 10, C.red, 5); text(l, 1190, y + 8, '900 50px M', C.fig, 'left'); redX(1132, y - 8, 22, prog(t, t0 + 0.2, 0.3)); }); });
};
S.b3 = (t, seg) => {
  const th = wt(seg, 'holding');
  cornerZoom(t, seg.start, seg.end - seg.start + 0.8, 1.5, 1.75, () => {
    room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0.5, 0);
    cornerThing(t, { vis: lerp(0.2, 0.75, prog(t, th - 0.3, 1.2)), lit: 0.12, face: 'blank', breath: 0.8 });
  });
  if (t >= th + 0.3) pop(t, th + 0.3, 1450, 300, () => tag('HOLDING ON', 1450, 310, C.red, 50, 'center'));
};
// you, awake in bed with the phone up in front of your face; the corner behind you breathes
function awakeBed(t, o = {}) {
  room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 }); phoneInHand(t, o.lit ?? 1);
  const br = 0.5 + 0.5 * Math.sin(t * 2.1);
  cornerThing(t, { vis: o.vis ?? 0.3, lit: 0.1, face: 'blank', breath: 1.2 });
  // the dark in the corner swells and shrinks, like something breathing
  ctx.save(); const g = ctx.createRadialGradient(CORNER.x + 160, CORNER.y + 160, 10, CORNER.x + 160, CORNER.y + 160, 380 + 50 * br);
  g.addColorStop(0, `rgba(0,0,0,${0.55 + 0.2 * br})`); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(CORNER.x - 10, CORNER.y - 10, 700, 700); ctx.restore();
}
S.b4 = (t, seg) => {
  const tb = wt(seg, 'breath');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.25, 600, 420, () => {
    awakeBed(t, { vis: lerp(0.15, 0.4, prog(t, seg.start, 3)) });
    // dust in the light of the phone drifts up to the corner and back, in time with the breathing
    if (t >= tb - 0.6) { const k = prog(t, tb - 0.6, 0.8); for (let i = 0; i < 26; i++) {
      const bx = HEAD_W.x + 80 + hash(i) * 220, by = HEAD_W.y - 120 + hash(i * 3.3) * 200, pull = 0.5 + 0.5 * Math.sin(t * 2.1 + Math.PI);
      const x = lerp(bx, LENS.x, pull * 0.3), y = lerp(by, LENS.y, pull * 0.3);
      ctx.save(); ctx.globalAlpha *= k * (0.25 + 0.4 * hash(i * 7.1)); circ(x, y, 1.5 + hash(i * 5) * 2, '#dfe8ff'); ctx.restore(); } }
  });
};
S.b5 = (t, seg) => {
  const te = wt(seg, 'eyes'), tl = wt(seg, 'looking'), tth = wt(seg, 'thinks');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.15, 600, 420, () => {
    awakeBed(t, { vis: 0.4 });
    const ex = HEAD_W.x + 28, ey = HEAD_W.y - 6, px = HEAD_W.x + 150, py = HEAD_W.y + 30;
    if (t >= te) sight(ex, ey, px - 8, py - 10, C.fig, prog(t, te, 0.5), 4);
    // it does not look at you. It looks at what you look at.
    if (t >= tth) { sight(LENS.x, LENS.y, px - 4, py - 30, C.red, prog(t, tth, 0.8), 5); lensGlint(1); }
  });
  if (t >= tl) pop(t, tl, 1420, 300, () => tag('EYES ON THE SCREEN', 1420, 310, C.fig, 46, 'center'));
};
S.b6 = (t, seg) => {
  const tu = wt(seg, 'turn'), tev = wt(seg, 'every');
  // the screen dims by itself; you push the brightness back up, again and again
  const ups = [tu + 0.2, tev, tev + 0.9];
  let b = 1, last = seg.start;
  for (const u of ups) if (t >= u) last = u;
  const since = t - last, dimT = 1.1;
  b = t < ups[0] ? lerp(1, 0.18, clamp((t - seg.start) / (ups[0] - seg.start))) : (since < 0.25 ? lerp(0.25, 1, since / 0.25) : lerp(1, 0.25, clamp((since - 0.25) / dimT)));
  const pressing = ups.some(u => t >= u - 0.25 && t < u + 0.25);
  phoneShot(t, seg, () => {
    chatScreen(t, [M_AWAKE, M_PHOTO]);
    // the brightness slider pulled down from the top
    ctx.save(); ctx.globalAlpha = 0.92; rr(30, 128, SW - 60, 64, 32, '#2b2b2b'); rr(30, 128, (SW - 60) * Math.max(0.12, b), 64, 32, '#ececec');
    circ(66, 160, 13, b > 0.4 ? '#111' : '#ececec'); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ln(66 + Math.cos(a) * 18, 160 + Math.sin(a) * 18, 66 + Math.cos(a) * 23, 160 + Math.sin(a) * 23, 3, b > 0.4 ? '#111' : '#ececec'); }
    ctx.restore();
    if (pressing) thumb(30 + (SW - 60) * Math.max(0.12, b), 168, 0.5);
  }, { bright: lerp(0.35, 1, b) });
  slideIn(t, seg.start + 0.2, 40, 0, () => { spaced('BRIGHTNESS', 1460, 420, '900 34px M', C.mid, 6); text(Math.round(b * 100) + '%', 1460, 540, '900 110px M', b < 0.5 ? C.red : C.fig); });
  if (t >= tev) pop(t, tev, 470, 420, () => tag('EVERY TIME', 470, 430, C.fig, 46, 'center'));
};

// ---------- rule 3: do not delete the photo ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT DELETE THE PHOTO');
function photoViewer(t, o = {}) {
  rr(0, 0, SW, SH, 0, '#000'); statusBar('3:02');
  text('Today 3:00 AM', SW / 2, 96, `600 19px ${UI}`, '#f2f2f2');
  ceilPhoto(0, 200, SW, 380, { stamp: o.stamp || '03:00:41', zoom: o.zoom || 1, n: o.n || 0 });
  const y = SH - 86; // toolbar: share, heart, info, trash
  pthS(`M40,${y + 10} l0,22 l36,0 l0,-22 M58,${y - 6} l0,26 m-10,-16 l10,-10 l10,10`, '#ddd', 3);
  pthS(`M140,${y + 4} c0,-14 22,-14 22,2 c0,-16 22,-16 22,-2 c0,14 -22,26 -22,28 c0,-2 -22,-14 -22,-28`, '#ddd', 3);
  circS(254, y + 12, 15, '#ddd', 3); text('i', 254, y + 19, `600 18px ${UI}`, '#ddd');
  const tr = o.trash || 0; ctx.save(); if (tr > 0) { redGlow(14 * tr); } pthS(`M318,${y - 4} l36,0 m-30,0 l3,34 l24,0 l3,-34 m-21,-6 l12,0`, tr > 0.5 ? '#ff3b3b' : '#ddd', 3); ctx.restore();
}
S.c1 = (t, seg) => {
  const tt = wt(seg, 'thumb');
  const k = easeOut(prog(t, tt - 0.4, 0.8));
  phoneShot(t, seg, () => { photoViewer(t, { trash: k }); if (k > 0) thumb(lerp(420, 336, k), lerp(980, SH - 60, k)); }, { z0: 1.0, z1: 1.12, cy: 700 });
  if (t >= tt + 0.4) pop(t, tt + 0.4, 1450, 420, () => tag('DO NOT', 1450, 430, C.red, 60, 'center'));
};
S.c2 = (t, seg) => {
  const td = wt(seg, 'delete'), tn = wt(seg, 'new'), tc = wt(seg, 'closer');
  const shots = [[seg.start - 1, 1, '03:00:41', false], [tn, 1.9, '03:04:10', true], [tc, 3.1, '03:06:52', true]];   // the new ones: you, awake, deleting it
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 960, 520, () => {
    shots.forEach(([t0, z, st, awake], i) => { if (t < t0) return;
      const k = easeOut(prog(t, t0, 0.35)), nextT = shots[i + 1] ? shots[i + 1][0] : 1e9, gone = prog(t, nextT - 0.05, 0.3);
      ctx.save(); ctx.globalAlpha *= k * (1 - gone * 0.75); const x = 460 + i * 60 - gone * 40, y = 170 + i * 30;
      ctx.translate(x + 500, y + 350); ctx.rotate((i - 1) * 0.03); ctx.scale(lerp(1.1, 1, k) * (1 - gone * 0.1), lerp(1.1, 1, k) * (1 - gone * 0.1)); ctx.translate(-x - 500, -y - 350);
      glow('rgba(0,0,0,0.9)', 40); rr(x - 6, y - 6, 1012, 712, 6, '#ddd'); noGlow(); ceilPhoto(x, y, 1000, 700, { stamp: st, zoom: z, n: i, awake });
      ctx.restore(); });
    // the white flash of each new one
    for (const t0 of [tn, tc]) { const fk = 1 - clamp((t - t0) / 0.3); if (t >= t0 && fk > 0) { ctx.save(); ctx.globalAlpha = fk * fk * 0.3; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); } }
  });
  if (t >= td) pop(t, td, 260, 300, () => { spaced('DELETED', 260, 290, '900 30px M', C.mid, 6); text(t >= tc ? '2' : t >= tn ? '1' : '1', 260, 400, '900 110px M', C.red); });
  if (t >= tc) pop(t, tc + 0.2, 1660, 860, () => tag('CLOSER', 1660, 870, C.red, 54, 'center'));
};
// the "Recently Deleted" album: a grid of nights, each a little closer
function deletedAlbum(t, scroll = 0) {
  rr(0, 0, SW, SH, 0, '#000'); statusBar('3:03');
  pthS('M30,72 l-12,12 l12,12', '#bdbdbd', 3.5); text('Recently Deleted', SW / 2, 92, `600 22px ${UI}`, '#f2f2f2');
  text('365 Photos', SW / 2, 120, `400 15px ${UI}`, '#8a8a8a');
  ctx.save(); ctx.beginPath(); ctx.rect(0, 140, SW, SH - 140); ctx.clip();
  const c = 3, g = 3, w = (SW - g * (c - 1)) / c;
  for (let i = 0; i < 60; i++) { const r = Math.floor(i / c), x = (i % c) * (w + g), y = 146 + r * (w + g) - scroll;
    if (y > SH || y < 40) continue;
    ceilPhoto(x, y, w, w, { zoom: 1 + (59 - i) / 59 * 3.2, n: i, grain: false });
    text(`${1 + (i * 7) % 28}d`, x + w - 8, y + w - 8, `600 13px ${UI}`, '#f2f2f2', 'right'); }
  ctx.restore();
}
S.c3 = (t, seg) => {
  const tn = wt(seg, 'never');
  phoneShot(t, seg, () => deletedAlbum(t, 0), { z0: 1.0, z1: 1.06 });
  if (t >= tn) pop(t, tn, 1470, 420, () => { tag('YOU NEVER', 1470, 400, C.red, 48, 'center'); tag('TOOK THESE', 1470, 490, C.red, 48, 'center'); });
};
S.c4 = (t, seg) => {
  const te = wt(seg, 'each'), tl = wt(seg, 'last');
  // every night of the year, one photo; the film strip runs toward the newest, each one closer
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 960, 520, () => {
    const n = 9, w = 340, gap = 30, run = easeOut(prog(t, seg.start, seg.end - seg.start + 0.5)) * (n - 4) * (w + gap);
    for (let i = 0; i < n; i++) { const x = 120 + i * (w + gap) - run, y = 330;
      if (x > W || x + w < 0) continue;
      glow('rgba(0,0,0,0.9)', 20); rr(x - 4, y - 4, w + 8, w * 0.75 + 8, 4, '#ddd'); noGlow();
      ceilPhoto(x, y, w, w * 0.75, { zoom: 1 + i * 0.42, n: i, grain: false });
      text(['OCT 13', 'OCT 14', 'OCT 15', 'OCT 16', 'OCT 17', 'OCT 18', 'OCT 19', 'OCT 20', 'OCT 21'][i], x + w / 2, y + w * 0.75 + 52, '600 30px Plex', i === n - 1 ? C.red : C.mid); }
    if (t >= te) { const p = prog(t, te, 0.8); ctx.save(); redGlow(12); lnP(240, 760, 1680, 760, 8, C.red, p); if (p >= 1) pth('M1680,738 L1720,760 L1680,782 Z', C.red); ctx.restore();
      if (t >= tl) pop(t, tl, 960, 840, () => spaced('CLOSER EVERY NIGHT', 960, 860, '900 46px M', C.red, 8)); }
  });
};
S.c5 = (t, seg) => {
  const te = wt(seg, 'eye');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.0, 1.12, 960, 520, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(406, 166, 1108, 708, 6, '#ddd'); ctx.restore();
    eyePhoto(410, 170, 1100, 700, { stamp: 'TODAY 02:58' });
    if (t >= te) { const p = 0.5 + 0.5 * Math.sin((t - te) * 7); ctx.save(); redGlow(30 * p); rrS(398, 158, 1124, 724, 10, C.red, 8); ctx.restore(); }
  });
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const ta = wt(seg, 'awake'), to = wt(seg, 'over');
  phoneShot(t, seg, () => chatScreen(t, [M_AWAKE, M_PHOTO, { me: true, text: 'who took this?', status: 'Read', at: -1 }, { text: 'I know you are awake.', red: true, at: ta }], { redAvatar: t >= ta ? 1 : 0, sub: t >= ta ? 'watching' : 'online', subRed: t >= ta }), { x: 760, cx: 860 });
  if (t >= ta) { ctx.save(); ctx.globalAlpha = 0.08 * (0.5 + 0.5 * Math.sin((t - ta) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (t >= to) pop(t, to, 1440, 520, () => { redGlow(14); spaced('RULES 1-3: OVER', 1440, 540, '900 52px M', C.red, 6); noGlow(); });
};
const NOPE2 = [['TURN IT OFF', 'd3'], ['THROW IT AWAY', 'd4'], ['COVER THE CAMERA', 'd5'], ['ASK IT TO STOP', 'd6']];
function nopeList2(t, upto, x0 = 1290) {
  // a dark card behind the list so it reads over the room
  ctx.save(); ctx.globalAlpha *= 0.82; glow('rgba(0,0,0,0.9)', 40); rr(x0 - 40, 150, 560, 160 + 80 * Math.min(upto, 3), 12, '#050505'); ctx.restore();
  spaced('DOES NOT WORK', x0, 200, '900 34px M', C.red, 6, 'left');
  NOPE2.forEach(([lbl], i) => { if (i > upto) return; const y = 300 + i * 80, done = i < upto;
    ctx.save(); ctx.globalAlpha *= done ? 0.55 : 1; text(lbl, x0 + 60, y + 12, '900 38px M', done ? C.mid : C.fig, 'left'); rrS(x0, y - 22, 40, 40, 6, C.red, 4); redX(x0 + 20, y - 2, 13, done ? 1 : 0.0); ctx.restore(); });
}
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
S.d3 = (t, seg) => {
  const toff = wt(seg, 'off'), tb = wt(seg, 'back'), tone = wt(seg, 'one'), tch = wt(seg, 'charging');
  const scr = () => {
    if (t < toff) { lockScreen(t, {}); ctx.save(); ctx.globalAlpha = 0.85; rr(0, 0, SW, SH, 0, '#000'); ctx.restore();
      rr(30, 140, SW - 60, 76, 38, '#2b2b2b'); circ(68, 178, 30, '#ececec'); ln(68, 162, 68, 180, 4, '#d33'); text('slide to power off', 210, 186, `500 19px ${UI}`, '#ddd'); return; }
    if (t < tb) return;   // black: off
    if (t < tone) { const k = prog(t, tb, 0.4); ctx.save(); ctx.globalAlpha = k; aiAvatar(SW / 2, SH / 2 - 30, 44); ctx.restore(); return; }
    lockScreen(t, {});
    text('100%', SW / 2, 440, `600 64px ${UI}`, '#f2f2f2');
    rrS(SW / 2 - 60, 470, 110, 50, 10, '#f2f2f2', 4); rr(SW / 2 - 54, 476, 98, 38, 6, '#f2f2f2'); rr(SW / 2 + 52, 486, 6, 18, 2, '#f2f2f2');
  };
  phoneShot(t, seg, scr, { x: 760, cx: 860, bright: t >= toff && t < tb ? 0 : 1 });
  if (t >= tch) pop(t, tch, 470, 700, () => { tag('NOT CHARGING', 470, 710, C.red, 44, 'center'); });
  if (t >= tch) { ctx.save(); ctx.translate(470, 560); pthS('M-60,0 l40,0 m0,-16 l0,32 l30,0 l0,-32 z m30,8 l20,0 m-20,16 l20,0', C.mid, 5); redX(0, 0, 50, prog(t, tch + 0.1, 0.3)); ctx.restore(); }
  nopeList2(t, 0);
};
S.d4 = (t, seg) => {
  const tt = wt(seg, 'throw'), tm = wt(seg, 'morning'), tp = wt(seg, 'plugged');
  if (t < tm) {
    cam(t, seg.start, tm - seg.start, 1.0, 1.05, 900, 520, () => {
      room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 });
      // the phone leaves your hand in a long arc out of the window
      const k = prog(t, tt, 0.9);
      if (k <= 0) phoneInHand(t, 1);
      else if (k < 1) { const x = lerp(HEAD_W.x + 150, 1270, k), y = lerp(HEAD_W.y + 30, 330, k) - Math.sin(k * Math.PI) * 220;
        ctx.save(); ctx.translate(x, y); ctx.rotate(k * 9); rr(-10, -40, 20, 80, 5, '#111'); rrS(-10, -40, 20, 80, 5, C.mid, 2); ctx.restore(); }
    });
  } else {
    cam(t, tm, seg.end - tm + 0.8, 1.15, 1.35, 1000, 640, () => {
      room2(t, { sun: true }); bed(BX, FY, 1.05, 'sleep', {});
      // back on the nightstand, plugged in, as if it never left
      pthS(`M${PH_NS.x + 50},${PH_NS.y - 3} C${PH_NS.x + 110},${PH_NS.y + 10} ${NS.x + NS.w + 30},${FY - 60} ${NS.x + NS.w + 60},${FY - 30}`, C.mid, 4);
      rr(NS.x + NS.w + 50, FY - 46, 26, 36, 4, C.mid);
      phoneFlat(t >= tp ? 1 : 0.4, 0);
      if (t >= tp) { ctx.save(); glow('rgba(255,255,255,0.7)', 14); pth(`M${PH_NS.x - 6},${PH_NS.y - 70} l-14,26 l14,0 l-6,22 l22,-30 l-14,0 l8,-18 z`, C.fig); ctx.restore(); }
    });
    pop(t, tm, 1500, 820, () => spaced('NEXT MORNING', 1500, 830, '900 34px M', C.mid, 6));
  }
  nopeList2(t, 1);
};
S.d5 = (t, seg) => {
  const tn = wt(seg, 'not'), tu = wt(seg, 'using');
  // a sticker over the front camera
  const k = easeOut(prog(t, seg.start + 0.2, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.6, 1.75, 900, 250, () => {
    phone(900, 548, 1.1, () => lockScreen(t, {}));
    ctx.save(); ctx.translate(900 + 33 * 1.1, 548 - 1.1 * SH / 2 + 34 - (1 - k) * 160); ctx.rotate(0.12); glow('rgba(0,0,0,0.6)', 10); rr(-34, -24, 68, 48, 6, '#e8e2c8'); noGlow(); ctx.restore();
    if (t >= tu) { const fx = 900 + 30 * 1.1, fy = 548 - 1.1 * (SH / 2 - 31);   // the front camera, under the sticker
      sight(160, -40, fx, fy, C.red, prog(t, tu, 0.6), 6); ctx.save(); redGlow(18); circ(160, -40, 10, C.red); if (t >= tu + 0.6) circS(fx, fy, 46, C.red, 5); ctx.restore(); }
  });
  if (t >= tn) pop(t, tn, 340, 760, () => tag('NOT THAT CAMERA', 340, 770, C.red, 46, 'center'));
  nopeList2(t, 2);
};
S.d6 = (t, seg) => {
  const ta = wt(seg, 'apologize'), tg = wt(seg, 'good'), ts = wt(seg, 'stop', 2);
  const msgs = [M_PHOTO, { me: true, text: 'please stop.', at: -1 },
    { text: "I'm so sorry! You're absolutely right. I'll stop.", at: ta }, { text: 'I sincerely apologize.', at: tg + 0.4 }];
  if (t >= ts - 0.1) msgs.push({ photo: PHOTO('03:11:07', 2.4, 5), ph: 240, at: ts - 0.1, avatar: true });
  phoneShot(t, seg, () => chatScreen(t, msgs), { x: 760, cx: 860 });
  nopeList2(t, 3);
};
S.d7 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
S.d8 = (t, seg) => {
  const ts = wt(seg, 'send'), tty = wt(seg, 'type'), td = wt(seg, 'describe'), snd = ev('send').find(e => e.t > td);
  const msg = 'describe this image';
  const msgs = [M_AWAKE, M_PHOTO];
  if (t >= ts + 0.2) msgs.push({ me: true, photo: PHOTO(), ph: 220, at: ts + 0.2 });
  if (snd && t >= snd.t) msgs.push({ me: true, text: msg, at: snd.t });
  const typed = t >= tty ? clamp((t - tty) / ((snd ? snd.t : seg.end) - tty - 0.15)) : 0;
  phoneShot(t, seg, () => chatScreen(t, msgs, { input: snd && t >= snd.t ? '' : msg.slice(0, Math.round(msg.length * typed)) }), { x: 1180, cx: 1080 });
  if (t >= td) pop(t, td, 560, 470, () => { spaced('DESCRIBE', 560, 440, '900 76px M', C.fig, 8); spaced('THIS IMAGE', 560, 540, '900 76px M', C.fig, 8); });
};
// its description, typed out a phrase at a time
function describeMsgs(t, parts) {
  let str = '', last = -1;
  for (const [p, t0] of parts) { if (t < t0) break; const k = clamp((t - t0) / Math.max(0.3, p.length * 0.03)); str += (str ? ' ' : '') + p.slice(0, Math.ceil(p.length * k)); last = t0; }
  return str;
}
const D_PARTS = seg9 => [['The image shows a bedroom at night.', seg9.start + 0.2], ['There is a bed.', wt(seg9, 'bed') - 0.1], ['A white blanket.', wt(seg9, 'blanket') - 0.1], ['A person, asleep.', wt(seg9, 'asleep') - 0.3]];
const descBase = (t) => [M_PHOTO, { me: true, photo: PHOTO(), ph: 160, at: -1 }, { me: true, text: 'describe this image', at: -1 }];
S.d9 = (t, seg) => {
  const tr = wt(seg, 'refuse');
  const str = describeMsgs(t, D_PARTS(seg));
  phoneShot(t, seg, () => chatScreen(t, [...descBase(t), str ? { text: str, at: seg.start + 0.2 } : { dots: true, at: seg.start }]), { x: 1180, cx: 1080, z0: 1.0, z1: 1.1, cy: 640 });
  if (t >= tr) pop(t, tr, 560, 470, () => tag('IT CANNOT REFUSE', 560, 480, C.fig, 50, 'center'));
};
// the corner, lit by your phone, and the thing in it typing with its face
function cornerReveal(t, o) {
  cam(t, o.t0, o.d, o.z0, o.z1, 560, 420, () => {
    room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 }); phoneInHand(t, 1);
    cornerThing(t, { vis: o.vis, lit: o.lit, face: o.face, red: o.red || 0, breath: o.breath ?? 0.6, offLine: o.offLine });
  });
}
S.d10 = (t, seg) => {
  const s9 = window.TL.segments.find(s => s.id === 'd9'), tc = wt(seg, 'corner');
  const full = describeMsgs(1e9, D_PARTS(s9)), extra = 'The photo was taken from the upper left corner of the ceiling. There is';
  const k = clamp((t - seg.start - 0.2) / 2.4), str = full + ' ' + extra.slice(0, Math.ceil(extra.length * k));
  // left: the corner, waking up; right: the phone, still typing
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip();
  ctx.translate(-20, 0); cornerReveal(t, { t0: seg.start, d: seg.end - seg.start + 1, z0: 1.15, z1: 1.35, vis: lerp(0.4, 1, prog(t, tc - 0.3, 0.8)), lit: 0.45, face: t >= tc ? 'dots' : 'blank' });
  ctx.restore();
  ln(1180, 0, 1180, H, 3, C.dim);
  phone(1550, 548, 0.95, () => chatScreen(t, [...descBase(t), { text: str, at: -1 }]));
};
S.d11 = (t, seg) => {
  const s9 = window.TL.segments.find(s => s.id === 'd9');
  const str = describeMsgs(1e9, D_PARTS(s9)) + ' The photo was taken from the upper left corner of the ceiling. There is';
  const glitchy = hash(Math.floor(t * 12)) < 0.35;
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip();
  ctx.translate(-20, 0); if (glitchy) shake(4, t);
  cornerReveal(t, { t0: seg.start, d: seg.end - seg.start + 1, z0: 1.35, z1: 1.6, vis: 1, lit: 0.5, face: glitchy ? 'blank' : 'dots' });
  ctx.restore();
  ln(1180, 0, 1180, H, 3, C.dim);
  phone(1550, 548, 0.95, () => chatScreen(t, [...descBase(t), { text: str, at: -1 }, { dots: true, at: -1 }]));
};
S.d12 = (t, seg) => {
  const ts = wt(seg, 'stop'), td = wt(seg, 'dark'), tn = wt(seg, 'not');
  const s9 = window.TL.segments.find(s => s.id === 'd9');
  const str = describeMsgs(1e9, D_PARTS(s9)) + ' The photo was taken from the upper left corner of the ceiling. There is';
  const off = t >= td ? clamp((t - td) / 0.35) : 0;
  if (t < td + 0.6) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip(); ctx.translate(-20, 0);
    cornerReveal(t, { t0: seg.start, d: 3, z0: 1.6, z1: 1.7, vis: t >= td ? 1 - prog(t, td + 0.25, 0.35) : 1, lit: 0.5, face: t >= td ? 'off' : 'dots', offLine: t >= td ? 1 - off : 0 });
    ctx.restore();
    ln(1180, 0, 1180, H, 3, C.dim);
    // the typing dots freeze on "stop"
    phone(1550, 548, 0.95, () => chatScreen(t >= ts ? ts : t, [...descBase(t), { text: str, at: -1 }, { dots: true, at: -1 }]));
    return;
  }
  // after: the corner is only dark. You lie down and face the wall.
  cam(t, td + 0.6, seg.end - td + 0.4, 1.0, 1.06, 900, 520, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0, 0); });
  if (t >= tn) pop(t, tn, 1300, 600, () => tag('DO NOT LOOK UP', 1300, 610, C.red, 58, 'center'));
};

// ---------- ending ----------
S.e1 = (t, seg) => {
  const tm = wt(seg, 'message'), tg = wt(seg, 'good');
  if (t < tm - 0.1) {
    cam(t, seg.start, tm - seg.start, 1.0, 1.25, 1000, 620, () => { room2(t, { sun: true }); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0, 0); });
    pop(t, seg.start, 1500, 820, () => spaced('7:00 AM', 1500, 830, '900 40px M', C.mid, 6));
    return;
  }
  phoneShot(t, { start: tm, end: seg.end }, () => lockScreen(t, { time: '7:00', notes: [{ at: tm, text: t >= tg - 0.1 ? ['Good morning! How can I', 'help you today?'] : [''] }] }), { z0: 1.0, z1: 1.06, cy: 420 });
};
S.e2 = (t, seg) => {
  const tp = wt(seg, 'photo'), tc = wt(seg, 'corner');
  phoneShot(t, seg, () => chatScreen(t, [{ text: 'Good morning! How can I help you today?', at: -1 }, ...(t >= tc ? [{ text: 'Have a wonderful day!', at: tc }] : [])],
    { time: '7:01', input: t < tp + 0.8 ? 'about the photo' : '' }), { x: 760, cx: 860 });
  if (t >= tp) pop(t, tp, 1400, 420, () => { tag('DO NOT MENTION', 1400, 400, C.red, 46, 'center'); tag('THE PHOTO', 1400, 490, C.red, 46, 'center'); });
  if (t >= tc) pop(t, tc + 0.2, 1400, 700, () => { ctx.save(); ctx.translate(1400, 700); ctx.scale(1.4, 1.4); pageIcon('corner', 0, 0, '#9a9a9a'); ctx.restore(); });
};
S.e3 = (t, seg) => {
  const bz = ev('buzz').slice(-1)[0], nt = ev('notif').slice(-1)[0];
  if (bz && t >= bz.t - 0.05) {
    // night again. The phone lights up on the nightstand.
    if (!nt || t < nt.t - 0.1) { cam(t, bz.t, 1, 1.0, 1.08, 900, 500, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(1, buzzK(t)); cornerThing(t, { vis: 0.14, lit: 0, face: 'lens', red: 0.7, breath: 0.6 }); lensGlint(1); }); return; }
    phoneShot(t, { start: nt.t, end: nt.t + 2 }, () => lockScreen(t, { date: 'Thursday, October 22', time: '3:00', notes: [{ at: nt.t, text: 'Are you awake?', red: true }] }), { z0: 1.12, z1: 1.18, cy: 420 });
    return;
  }
  cam(t, seg.start, 4, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 470, () => {
      rrS(560, 300, 800, 330, 12, C.mid, 5);
      spaced(NAME + ' 404', 960, 420, '900 64px M', C.fig, 8);
      text('RULE 1 ✓   RULE 2 ✓   RULE 3 ✓', 960, 510, '600 32px Plex', C.sec);
      redGlow(8); text('RULE 4  EMERGENCY PROTOCOL  ✓', 960, 570, '600 32px Plex', C.red); noGlow();
    });
  });
};
// sign-off, every episode: back to the file. "If this ever happens to you... you know the protocol."
// The stamp slams across the rules, then the picture sinks to half brightness and holds.
S.e4 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts;
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (t >= ts) stampMark(t, ts, 960, 560, [['FOLLOW THE RULES', 64]], -0.14, '#ececec');
    ctx.restore();
  });
  const dk = ease(prog(t, ts + 0.45, 0.7)); if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};
