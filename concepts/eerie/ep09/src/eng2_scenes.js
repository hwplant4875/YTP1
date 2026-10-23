// ---------- EP09 scenes: "If Your Dog Ever Smiles With Human Teeth… DO NOT SMILE BACK" (Protocol 404) ----------
// Pure black, pure white vector figures, red only for danger. You are faceless; only the dog has a mouth.
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const segEnd = seg => seg.end + 0.7;
const seg$ = id => window.TL.segments.find(s => s.id === id);
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const flatT = fn => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); fn(); ctx.restore(); };
const redWash = (a) => { if (a > 0) flatT(() => { ctx.globalAlpha = a; ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); }); };
// shot switcher: [[t0, fn], ...] -> the last shot whose start has passed
function shots(t, list) { let f = list[0][1], t0 = list[0][0]; for (const [a, g] of list) if (t >= a) { f = g; t0 = a; } f(t0); }
// a "does not work" header at the top left: a small drawn icon, the label, a red X on the icon at tx
function noHead(t, seg, draw, label, tx) {
  flatT(() => slideIn(t, seg.start, -40, 0, () => { ctx.font = '900 46px M'; const w = 200 + ctx.measureText(label).width; ctx.save(); ctx.globalAlpha *= 0.9; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    draw(125, 125); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35));
}
// a big label that pops and stays
const bigTag = (t, t0, s, x, y, col = C.fig, size = 56) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y, col, size, 'center'), 0.3); };
// the dog's head of each figure for growl arcs / bubbles
const DOGX = 1260, YOUX = 620;

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the dog's face, already smiling with a full set of human teeth
  const td = wt(seg, 'do'), tt = wt(seg, 'teeth');
  black();
  cam(t, 0, seg.end + 0.6, 1.0, 1.14, 960, 560, () => dogFace(960, 560, 1.32, { smile: 1, eye: prog(t, tt, 0.4) * 0.0 }));
  if (t >= td - 0.1) flatT(() => pop(t, td - 0.1, 960, 110, () => tag('DO NOT SMILE BACK', 960, 120, C.red, 56, 'center'), 0.3));
};
function teaserBox(t, w0, draw, tx, y = 250, x = 1640) {
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 130, y - 120, 260, 240, 22, '#000'); ctx.restore(); rrS(x - 130, y - 120, 260, 240, 22, C.fig, 5); draw(x, y); }, 0.3);
  redX(x, y, 95, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  // three quick "do not"s, each done anyway: it pats your head / it sits at your table / the mirror
  const ws = [[seg.start, wt(seg, 'do', 2), 'smile'], [wt(seg, 'do', 2), wt(seg, 'and'), 'eat'], [wt(seg, 'and'), nextStart(seg), 'look']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit, L = blk - w0;
  if (t < blk) {
    black();
    if (i === 0) cam(t, w0, L, 1.0, 1.15, 900, 560, () => { floorLine();
      const up = prog(t, w0 + 0.5, 1.0), pat = prog(t, hit - 0.5, 0.3);
      you(760, FL, 1.05, { dir: 1 });
      dog(1120, FL, 1.12, { dir: -1, rear: up, eye: prog(t, hit - 0.2, 0.2), smile: 1, reach: [790, 452 + Math.abs(Math.sin((t - hit) * 18)) * 18 * (t > hit - 0.5 ? 1 : 0)], reachK: pat }); });
    else if (i === 1) cam(t, w0, L, 1.0, 1.12, 1100, 560, () => { floorLine(); chair(1380, 1, -1); dog(1384, FL - 176, 1.0, { dir: -1, rear: 1, sit: 1, eye: prog(t, hit - 0.3, 0.2), smile: prog(t, w0 + 0.4, 0.6), reach: [1270, 596], reachK: 1 });
      table(640, 1290); plate(820, 600, 1, { food: true }); plate(1150, 600, 1, { fork: false }); chair(560, 1, 1); you(560, FL - 0, 1, { pose: 'sit', hand: [700, 594] }); });
    else cam(t, w0, L, 1.0, 1.2, 960, 520, () => { floorLine();
      mirrorFrame(760, 170, 400, 690, { inner: () => { floorLine(FL, '#1a1a1a'); you(950, FL, 0.78, { pose: 'fours', dir: -1, red: prog(t, hit - 0.3, 0.2) }); } });
      dog(560, FL, 0.95, { dir: 1, sit: 1 }); });
    redWash(d > 0 ? 0.35 * clamp(d / 0.2) : 0);
  }
  blackAfter(t, blk);
  const draws = [(x, y) => pageIcon('smile', x, y, '#fff'), (x, y) => pageIcon('plate', x, y, '#fff'), (x, y) => pageIcon('mirror', x, y, '#fff')];
  flatT(() => teaserBox(t, w0, (x, y) => { ctx.save(); ctx.translate(x, y); ctx.scale(1.5, 1.5); ctx.translate(-x, -y); draws[i](x, y); ctx.restore(); }, wt(seg, word)));
};

// ---------- rule 1: do not smile back ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT SMILE BACK');
S.a1 = (t, seg) => {
  // you come home; the dog runs to the door, tail going
  const tr = wt(seg, 'runs'), ttl = wt(seg, 'tail');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1100, 560, () => {
    floorLine();
    const op = ease(prog(t, seg.start + 0.1, 0.6));
    hallDoor(1500, op);
    you(lerp(1610, 1440, ease(prog(t, seg.start + 0.4, 1.4))), FL, 1, { dir: -1, walk: t < seg.start + 1.8 ? t * 8 : null });
    const run = ease(prog(t, tr - 0.3, 1.8)), dx = lerp(-200, 1130, run);
    dog(dx, FL, 0.95, { dir: 1, walk: run < 1 ? t * 14 : null, wag: t >= ttl - 0.3 ? t * 16 : t * 4 });
  });
};
S.a2 = (t, seg) => {
  // the smile: it opens slowly; then a close-up of the teeth
  const ts = wt(seg, 'smiles'), tw = wt(seg, 'wide'), tb = wt(seg, 'behind'), th = wt(seg, 'human');
  black();
  if (t < tb - 0.05) {
    const k = lerp(0, 0.25, prog(t, ts, 0.8)) + lerp(0, 0.35, prog(t, tw, 0.6));
    cam(t, seg.start, tb - seg.start, 1.0, 1.12, 960, 560, () => dogFace(960, 560, 1.15, { smile: k }));
  } else {
    focus(t, tb - 0.05, 3.0, 1.9, 2.15, 960, 700, () => dogFace(960, 560, 1.15, { smile: lerp(0.6, 1, ease(prog(t, tb, 1.4))) }));
    if (t >= th) flatT(() => { ctx.save(); redGlow(16); lnP(1560, 470, 1240, 700, 6, C.red, prog(t, th, 0.3)); ctx.restore(); bigTag(t, th + 0.2, 'HUMAN TEETH', 1600, 430, C.red, 52); });
  }
};
S.a3 = (t, seg) => {
  // something moved in; it copies the face it sees most (yours); the smile is a question
  const tl = wt(seg, 'learns'), ty = wt(seg, 'yours'), ta = wt(seg, 'and'), tq = wt(seg, 'question');
  black();
  shots(t, [
    [seg.start, t0 => cam(t, t0, tl - t0, 1.0, 1.1, 960, 600, () => { floorLine(); dog(980, FL, 1.4, { dir: 1, sit: 1 }); insideMe(880, FL - 230, 1.05, prog(t, t0 + 0.6, 0.6)); })],
    [tl - 0.05, t0 => cam(t, t0, ta - t0, 1.0, 1.06, 960, 560, () => { floorLine();
      you(560, FL, 1.15, { dir: 1, red: t >= ty ? 0.8 : 0 }); dog(1260, FL, 1.15, { dir: -1, sit: 1 });
      ctx.save(); ctx.setLineDash([16, 14]); ctx.lineDashOffset = -t * 60; ln(1170, 520, 640, 460, 5, t >= ty ? C.red : C.fig); ctx.restore();
      bigTag(t, t0 + 0.6, 'COPYING', 900, 330, C.fig, 50); })],
    [ta - 0.05, t0 => { cam(t, t0, segEnd(seg) - t0, 1.0, 1.08, 960, 560, () => dogFace(860, 580, 1.0, { smile: 1 }));
      if (t >= tq - 0.3) say(t, tq - 0.3, 1450, 260, '?', 1140, 400, 120); }],
  ]);
};
S.a4 = (t, seg) => {
  // trade places: you and the dog, two red arrows swapping
  const tt = wt(seg, 'trade');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    floorLine(); you(620, FL, 1.1, { dir: 1 }); dog(1300, FL, 1.1, { dir: -1, sit: 1, smile: 1 });
    swapArrows(640, 1290, 360, prog(t, tt - 0.1, 0.6), C.red, 150);
  });
};
S.a5 = (t, seg) => {
  // every day of its life: a wall of smiles; a smile is a yes
  const tdo = wt(seg, 'do'), ty = wt(seg, 'yes');
  black();
  if (t < tdo - 0.05) {
    const n = Math.floor(clamp((t - seg.start - 0.3) / (tdo - seg.start - 0.8)) * 160);
    cam(t, seg.start, tdo - seg.start, 1.0, 1.06, 960, 520, () => {
      for (let i = 0; i < 160; i++) { if (i >= n) break; const cx = 300 + (i % 20) * 69, cy = 200 + Math.floor(i / 20) * 72; ctx.save(); ctx.translate(cx, cy); ctx.scale(0.62, 0.62); ctx.translate(-cx, -cy); pageIcon('smile', cx, cy, C.fig); ctx.restore(); }
      text((Math.round(n * 22.8)).toLocaleString('en-US') + ' DAYS', 960, 860, '900 64px M', C.fig);
    });
  } else {
    cam(t, tdo - 0.05, segEnd(seg) - tdo, 1.0, 1.08, 960, 520, () => {
      ctx.save(); ctx.translate(960, 480); ctx.scale(4, 4); ctx.translate(-960, -480); pageIcon('smile', 960, 480, t >= ty ? C.red : C.fig); ctx.restore();
      if (t >= ty - 0.1) stampMark(t, ty - 0.1, 1230, 660, [['YES', 120]], -0.12, '#000', 30);
    });
  }
};
S.a6 = (t, seg) => {
  // what to do instead
  const tk = seg.start + 0.05, tp = wt(seg, 'pet'), tn = wt(seg, 'say'), tw = wt(seg, 'then');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.04, 960, 520, () => {
    okRow(t, tk, 520, 300, 'KEEP YOUR FACE STILL');
    okRow(t, tp - 0.1, 520, 460, 'PET IT');
    okRow(t, tn - 0.1, 520, 620, 'SAY ITS NAME');
    okRow(t, tw - 0.1, 520, 780, 'WALK AWAY');
  });
};
S.a7 = (t, seg) => {
  // one owner smiled back: it stood up and patted his head. "Good boy." In his voice.
  const tsb = wt(seg, 'smiled'), tst = wt(seg, 'stood'), tr = wt(seg, 'reached'), tp = wt(seg, 'patted'), tg = wt(seg, 'good'), tv = wt(seg, 'voice');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.22, 960, 470, () => {
    floorLine();
    const reach = prog(t, tr - 0.2, 0.6), pt = t - tp, bob = pt > 0 && pt < 1.2 ? Math.abs(Math.sin(pt * 9)) * 22 : 0;
    you(800, FL, 1.05, { dir: 1, red: t >= tv ? 0.8 : 0 });
    dog(1180, FL, 1.18, { dir: -1, rear: prog(t, tst - 0.1, 1.1), eye: t >= tg ? 1 : 0, smile: t >= tsb ? 1 : 0.2, reach: [834, 456 - bob], reachK: reach });
    if (t >= tg) say(t, tg - 0.05, 1350, 170, 'GOOD BOY.', 1180, 300, 56, { red: true });
  });
};

// ---------- rule 2: do not let it eat from your plate ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LET IT EAT FROM YOUR PLATE');
// the dining room: you at the left end of the table; o.dogAt: 'floor' (next to your chair) | 'chair' (the chair opposite) | null; o.chairOut 0..1
function dining(t, o = {}) {
  floorLine();
  const cx = lerp(1420, 1520, ease(o.chairOut ?? 0));
  if (o.dogAt === 'chair') { chair(cx, 1, -1); dog(cx + 4, FL - 176, 1.0, { dir: -1, rear: 1, sit: 1, eye: o.eye || 0, reach: [1255, 596], reachK: 1, smile: o.smile || 0 }); }
  else chair(cx, 1, -1);
  table(620, 1300);
  plate(800, 600, 1, { food: true }); if (o.dogAt === 'chair' || o.two) plate(1140, 600, 1, { food: false, fork: o.dogAt === 'chair' });
  if (o.salt) { rr(940, 556, 30, 44, 6, C.fig); circ(955, 556, 10, C.fig); }
  chair(520, 1, 1); you(522, FL, 1, { pose: 'sit', hand: o.hand || [700, 594] });
  if (o.forkUp != null) { const k = o.forkUp; ln(700, 594 - 60 * k, 770, 560 - 60 * k, 6, C.fig); }
  if (o.dogAt === 'floor') dog(380, FL, 0.8, { dir: 1, sit: 1, head: -0.3 });
  if (o.bowl !== false) bowl(1700, 0.9, { full: o.full });
}
S.b1 = (t, seg) => {
  // dinner: it walks past its bowl and sits next to your chair, watching your fork
  const tg = wt(seg, 'go'), tsit = wt(seg, 'sits'), tw = wt(seg, 'watches');
  black();
  if (t < tw - 0.1) {
    cam(t, seg.start, tw - seg.start, 1.0, 1.05, 960, 560, () => {
      dining(t, { dogAt: null, full: true });
      const k = ease(prog(t, tg - 0.6, tsit - tg + 0.8)), dx = lerp(1780, 380, k);
      dog(dx, FL, 0.8, { dir: -1, walk: k < 1 ? t * 12 : null, sit: k >= 1 ? prog(t, tsit + 0.2, 0.3) : 0 });
      if (t >= tg) bigTag(t, tg, 'BOWL', 1700, 700, '#8a8a8a', 30);
    });
  } else {
    focus(t, tw - 0.1, segEnd(seg) - tw, 1.9, 2.1, 640, 520, () => {
      dining(t, { dogAt: 'floor', forkUp: 0.5 + 0.5 * Math.sin(t * 2.4) });
      ctx.save(); ctx.setLineDash([10, 10]); ctx.lineDashOffset = -t * 40; ln(470, 630, 720, 530 - 30 * (0.5 + 0.5 * Math.sin(t * 2.4)), 4, C.red); ctx.restore();
    });
  }
};
S.b2 = (t, seg) => {
  // a real dog begs; this one is studying: the grip, the chewing, the pauses
  const tsd = wt(seg, 'studying'), th = wt(seg, 'hold'), tc = wt(seg, 'chew'), tw = wt(seg, 'wait');
  black();
  if (t < tsd - 0.1) {
    cam(t, seg.start, tsd - seg.start, 1.0, 1.06, 960, 560, () => { floorLine(); you(760, FL, 1, { pose: 'sit', hand: [870, 594] }); table(840, 1300); dog(1180, FL, 0.95, { dir: -1, rear: 0.35, wag: t * 10, reach: [1040, 600], reachK: 0.6 });
      bigTag(t, seg.start + 0.3, 'REAL DOG: BEGS', 1100, 300, '#9a9a9a', 40); });
  } else {
    cam(t, tsd - 0.1, segEnd(seg) - tsd, 1.0, 1.08, 760, 560, () => {
      dining(t, { dogAt: 'floor', forkUp: 0.5 + 0.5 * Math.sin(t * 3), bowl: false });
      const scan = (y0, y1, t0) => { if (t < t0) return; ctx.save(); ctx.setLineDash([10, 10]); ctx.globalAlpha *= 0.9; ln(470, 620, y0, y1, 3, C.red); ctx.restore(); };
      scan(720, 590, th); scan(540, 512, tc); scan(800, 600, tw);
      if (t >= th) pop(t, th, 1100, 380, () => tag('FORK GRIP: RIGHT HAND', 980, 390, C.fig, 36, 'left'), 0.3);
      if (t >= tc) pop(t, tc, 1100, 470, () => tag('CHEWS: 14 TIMES', 980, 480, C.fig, 36, 'left'), 0.3);
      if (t >= tw) pop(t, tw, 1100, 560, () => tag('PAUSE: 6.2 S', 980, 570, C.red, 36, 'left'), 0.3);
    });
  }
};
S.b3 = (t, seg) => {
  // not even one piece: every bite teaches it what you are made of
  const te = wt(seg, 'every'), tt = wt(seg, 'teaches');
  black();
  if (t < te - 0.05) {
    cam(t, seg.start, te - seg.start, 1.0, 1.06, 960, 540, () => {
      forkHand(640, 560, 1.1, 0.05, { food: true });
      dog(1520, FL + 60, 1.25, { dir: -1, sit: 1, head: -0.15 });
      redX(870, 540, 90, prog(t, seg.start + 0.6, 0.3));
    });
  } else {
    cam(t, te - 0.05, segEnd(seg) - te, 1.0, 1.06, 960, 540, () => {
      floorLine(); dog(1000, FL, 1.35, { dir: 1, sit: 1 });
      insideMe(900, FL - 220, 1.0, 0.4 + 0.6 * prog(t, tt, 0.5));
      flatT(() => meter(560, 140, 700, 'YOU, COPIED', lerp(0.12, 0.31, ease(prog(t, tt, 1.2)))));
    });
  }
};
S.b4 = (t, seg) => {
  // the next night: the bowl still full; the chair across from you pulled out
  const tc = wt(seg, 'chair'), tp = wt(seg, 'pulled');
  black();
  if (t < tc - 0.1) {
    focus(t, seg.start, tc - seg.start, 2.2, 2.4, 1700, 790, () => { floorLine(); bowl(1700, 0.9, { full: true }); });
    flatT(() => bigTag(t, seg.start + 0.3, 'NEXT NIGHT', 960, 160, C.fig, 50));
  } else {
    cam(t, tc - 0.1, segEnd(seg) - tc + 0.4, 1.0, 1.06, 1000, 560, () => dining(t, { dogAt: null, chairOut: prog(t, tp - 0.1, 0.5), full: true, two: true }));
  }
};
S.b5 = (t, seg) => {
  // it is sitting in it: back straight, paws on the table, waiting for the salt
  const tb = wt(seg, 'back'), tpw = wt(seg, 'paws'), ts = wt(seg, 'salt');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.25, 1.5, 1200, 480, () => {
    dining(t, { dogAt: 'chair', salt: true, eye: t >= ts ? 1 : 0, smile: t >= ts ? 0.6 : 0 });
    if (t >= tb && t < tpw) { ctx.save(); ctx.setLineDash([12, 10]); ln(1450, 330, 1450, 690, 4, C.fig); ctx.restore(); }
    if (t >= tpw) { ctx.save(); redGlow(14); circS(1262, 590, 46, C.red, 5); ctx.restore(); }
  });
};
S.b6 = (t, seg) => {
  // feed it in another room, close the door, eat fast
  const tc = wt(seg, 'close'), te = wt(seg, 'eat');
  black();
  shots(t, [
    [seg.start, t0 => cam(t, t0, tc - t0, 1.0, 1.05, 960, 560, () => { floorLine(); bowl(1100, 1, { full: true }); dog(820, FL, 0.9, { dir: 1, walk: t * 10 }); })],
    [tc - 0.05, t0 => cam(t, t0, te - t0, 1.0, 1.04, 960, 560, () => { floorLine(); const k = ease(prog(t, t0 + 0.1, 0.35)); rrS(860, FL - 470, 220, 470, 4, C.fig, 5);
      ctx.save(); ctx.translate(860, 0); ctx.scale(1 - 0.85 * (1 - k), 1); rr(4, FL - 466, 212, 462, 2, '#000'); rrS(4, FL - 466, 212, 462, 2, '#9a9a9a', 3); circ(186, FL - 220, 8, C.fig); ctx.restore(); })],
    [te - 0.05, t0 => cam(t, t0, segEnd(seg) - t0, 1.0, 1.06, 700, 560, () => dining(t, { dogAt: null, forkUp: 0.5 + 0.5 * Math.sin(t * 14), bowl: false }))],
  ]);
};

// ---------- rule 3: never let it look in the mirror ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'NEVER LET IT LOOK IN THE MIRROR');
// the hallway mirror with the dog sitting in front of it. o.refl(fn) overrides what the glass shows
const MIR = [820, 160, 420, 700];
function mirrorHall(t, o = {}) {
  floorLine();
  const [mx, my, mw, mh] = MIR, dk = o.dogX ?? 640;
  mirrorFrame(mx, my, mw, mh, { inner: o.refl || (() => { floorLine(FL, '#1c1c1c'); dog(1090, FL, 0.8, { dir: -1, sit: o.sit ?? 1, smile: o.smile || 0 }); }) });
  dog(dk, FL, 0.95, { dir: 1, sit: o.sit ?? 1, walk: o.walk, smile: o.smile || 0, eye: o.eye || 0, head: o.head || 0 });
}
S.c1 = (t, seg) => {
  // dogs don't care about mirrors; yours stops in front of the hallway mirror and stays
  const tst = wt(seg, 'stops'), ts = wt(seg, 'stays');
  black();
  if (t < tst - 0.1) cam(t, seg.start, tst - seg.start, 1.0, 1.04, 960, 560, () => { floorLine(); dog(lerp(-100, 1900, prog(t, seg.start, 3.2)), FL, 0.85, { dir: 1, walk: t * 12, wag: t * 6 });
    flatT(() => bigTag(t, seg.start + 0.2, 'MIRRORS: IGNORED', 960, 150, '#9a9a9a', 40)); });
  else cam(t, tst - 0.1, segEnd(seg) - tst, 1.0, 1.1, 900, 520, () => {
    const k = ease(prog(t, tst - 0.1, 1.0));
    mirrorHall(t, { dogX: lerp(200, 640, k), sit: prog(t, tst + 0.8, 0.3), walk: k < 1 ? t * 12 : null });
    if (t >= ts) pop(t, ts, 1500, 220, () => tag('2 HOURS', 1500, 230, C.red, 46, 'center'), 0.3);
  });
};
S.c2 = (t, seg) => {
  // checking its work: its teeth against yours
  const tc = wt(seg, 'comparing');
  black();
  if (t < tc - 0.05) cam(t, seg.start, tc - seg.start, 1.0, 1.08, 1000, 480, () => mirrorHall(t, { smile: prog(t, seg.start + 0.3, 0.5) }));
  else cam(t, tc - 0.05, segEnd(seg) - tc, 1.0, 1.04, 960, 520, () => {
    teethRow(960, 330, 0.95); text('YOURS', 960, 230, '900 40px M', C.fig);
    teethRow(960, 690, 0.95); text('ITS', 960, 590, '900 40px M', C.red);
    const sy = lerp(260, 820, (t - tc) % 1.2 / 1.2); ctx.save(); redGlow(12); ln(520, sy, 1400, sy, 3, C.red); ctx.restore();
    text(Math.min(98, Math.round(prog(t, tc, 1.6) * 98)) + '% MATCH', 1560, 540, '900 52px M', C.red);
  });
};
S.c3 = (t, seg) => {
  // cover it, move it, turn it to the wall
  const tc = wt(seg, 'cover'), tm = wt(seg, 'move'), tw = wt(seg, 'turn');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    floorLine(); const [mx, my, mw, mh] = MIR;
    const mv = ease(prog(t, tm, 0.5)) * 140, tr = ease(prog(t, tw, 0.5));
    ctx.save(); ctx.translate(mx + mw / 2 + mv, 0); ctx.scale(Math.max(0.04, Math.abs(Math.cos(tr * Math.PI))), 1); ctx.translate(-(mx + mw / 2), 0);
    if (tr < 0.5) mirrorFrame(mx, my, mw, mh, { inner: () => { floorLine(FL, '#1c1c1c'); dog(1090, FL, 0.8, { dir: -1, sit: 1 }); } });
    else { rr(mx, my, mw, mh, 14, '#1a1a1a'); rrS(mx, my, mw, mh, 14, C.fig, 8); ln(mx + 40, my + 40, mx + mw - 40, my + mh - 40, 3, '#3a3a3a'); ln(mx + mw - 40, my + 40, mx + 40, my + mh - 40, 3, '#3a3a3a'); }
    const cv = ease(prog(t, tc, 0.5));   // a sheet drops over it
    if (cv > 0 && tr < 0.5) { glow('rgba(255,255,255,0.25)', 16); pth(`M${mx - 30},${my - 20} L${mx + mw + 30},${my - 20} L${mx + mw + 40},${my - 20 + (mh * 0.75) * cv} C${mx + mw * 0.7},${my + mh * 0.7 * cv} ${mx + mw * 0.3},${my + mh * 0.82 * cv} ${mx - 40},${my - 20 + mh * 0.78 * cv} Z`, '#e4e4e4'); noGlow(); }
    ctx.restore();
    dog(640, FL, 0.95, { dir: 1, sit: 1, head: -0.1 });
  });
  flatT(() => { okRow(t, tc - 0.1, 1480, 300, 'COVER', 44); okRow(t, tm - 0.1, 1480, 450, 'MOVE', 44); okRow(t, tw - 0.1, 1480, 600, 'TURN', 44); });
};
S.c4 = (t, seg) => {
  // the day it sees a face that matches yours, it stops being a dog
  const tm = wt(seg, 'matches'), ts = wt(seg, 'stops');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start, 1.5, 1.8, 1030, 420, () => mirrorHall(t, { smile: 1, refl: () => { ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, W, H); dogFace(1030, 430, 0.62, { smile: 1, eye: prog(t, ts, 0.3) }); } }));
  flatT(() => meter(560, 110, 700, 'MATCH', lerp(0.98, 1, prog(t, tm, 0.6)), t >= tm ? C.red : C.fig));
};
S.c5 = (t, seg) => {
  // in the mirror, where your dog is sitting, there is a person on all fours; the dog smiles
  const tp = wt(seg, 'person'), tf = wt(seg, 'fours'), tsm = wt(seg, 'smiling');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.2, 960, 560, () => {
    const show = t >= tp - 0.1;
    mirrorHall(t, { smile: t >= tsm - 0.1 ? 1 : 0, refl: () => { floorLine(FL, '#1c1c1c'); if (show) you(1010, FL, 0.8, { pose: 'fours', dir: -1 }); else dog(1090, FL, 0.8, { dir: -1, sit: 1 }); } });
    if (show && t < tp + 0.25) { ctx.save(); ctx.globalAlpha = 0.3 * (1 - prog(t, tp - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(MIR[0], MIR[1], MIR[2], MIR[3]); ctx.restore(); }
  });
};
S.c6 = (t, seg) => {
  // it turns around, slowly: which one of you is the copy
  const tt = wt(seg, 'turns'), tw = wt(seg, 'which');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.5, 2.0, 1060, 640, () => {
    const turn = ease(prog(t, tt, 2.2));
    mirrorHall(t, { smile: 1, refl: () => { floorLine(FL, '#1c1c1c'); you(1010, FL, 0.8, { pose: 'fours', dir: -1, head: -30 * turn, red: t >= tw ? 1 : turn * 0.5 }); } });
  });
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  // broke a rule: the trade begins; leave it alone and it finishes
  const ts = wt(seg, 'smiled'), tf = wt(seg, 'fed'), tm = wt(seg, 'mirror'), tt = wt(seg, 'trade'), tfi = wt(seg, 'finishes');
  black();
  if (t < tt - 0.1) cam(t, seg.start, tt - seg.start, 1.0, 1.06, W / 2, 520, () => rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9], struck: [ts + 0.2, tf + 0.2, tm + 0.2, null] }));
  else cam(t, tt - 0.1, segEnd(seg) - tt, 1.0, 1.06, 960, 520, () => {
    floorLine(); you(620, FL, 1.05, { dir: 1, red: t >= tfi ? 1 : 0 }); dog(1300, FL, 1.05, { dir: -1, sit: 1, smile: 1, eye: t >= tfi ? 1 : 0 });
    swapArrows(640, 1290, 380, prog(t, tt, 0.5), C.red, 150);
    flatT(() => meter(560, 130, 700, 'TRADE', lerp(0.1, 1, ease(prog(t, tt + 0.4, tfi - tt + 0.2)))));
  });
};
function bedroom9(t, o = {}) {
  bedroomNight({ door: false });
  // your bed: something dog-shaped under the blanket, its head on your pillow, a tail hanging over the side
  ctx.save(); ctx.translate(380, 900); ctx.scale(1.25, 1.25);
  glow('rgba(255,255,255,0.22)', 16);
  rr(0, -330, 30, 330, 10, C.fig); rr(560, -170, 22, 170, 8, C.fig); rr(0, -150, 582, 46, 12, C.fig); rr(26, -104, 16, 104, 4, C.sec); rr(540, -104, 16, 104, 4, C.sec); rr(30, -196, 530, 48, 18, C.sec);
  ell(98, -204, 56, 16, 0, C.fig); noGlow();
  ctx.save(); ctx.translate(96, -262); ctx.scale(-0.8, 0.8); dogHead({ close: !o.awake, eye: o.awake ? 1 : 0 }); ctx.restore();
  glow('rgba(255,255,255,0.22)', 16); pth('M140,-196 C170,-252 260,-262 340,-256 C420,-250 500,-238 568,-222 L572,-176 L140,-176 Z', C.fig); noGlow();
  ctx.save(); ctx.translate(560, -186); ctx.rotate(1.3 + Math.sin(t * 2) * 0.05); pth('M0,-12 C-40,-22 -80,-34 -112,-40 C-118,-30 -110,-20 -100,-18 C-70,-10 -36,6 0,12 Z', C.fig); ctx.restore();
  ctx.restore();
  dogBed(1440, 1.05); you(1440, FL - 14, 0.95, { pose: 'curl', dir: -1, red: o.meRed || 0 });
}
S.d2 = (t, seg) => {
  // 3 AM: you wake up on the floor in the dog bed; something is asleep on your pillow
  const tw = wt(seg, 'wake'), tu = wt(seg, 'up');
  black();
  if (t < tu - 0.1) focus(t, seg.start, tu - seg.start, 1.6, 1.8, 1430, 760, () => bedroom9(t, { meRed: t >= tw ? 0.6 : 0 }));
  else cam(t, tu - 0.1, segEnd(seg) - tu + 0.4, 1.0, 1.12, 760, 600, () => bedroom9(t, {}));
  flatT(() => bigTag(t, seg.start + 0.2, '3:00 AM', 1640, 140, C.red, 52));
};
S.d3 = (t, seg) => {
  // on the nightstand: a collar, a tag, your name
  const tc = wt(seg, 'collar'), tn = wt(seg, 'name', 2);
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.3, 1.45, 960, 470, () => { nightstand(960, 2.2); collar(960, FL - 440 - 70, 1.0, { red: prog(t, tn, 0.3) }); });
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // the vet: his teeth are perfectly healthy; healthier than yours
  const th = wt(seg, 'his'), thr = wt(seg, 'healthier');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    phoneIcon(560, 560, 2.2, t < th ? C.fig : '#9a9a9a');
    if (t >= th) say(t, th - 0.05, 1240, 430, 'PERFECTLY\nHEALTHY.', 760, 520, 64);
    if (t >= thr) say(t, thr - 0.05, 1300, 700, 'HEALTHIER\nTHAN YOURS.', 820, 640, 54, { red: true });
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); ctx.scale(0.36, 0.36); phoneIcon(0, -20, 1); ctx.restore(); }, 'CALL THE VET', seg.start + 1.0);
};
S.d6 = (t, seg) => {
  // locked outside: thirty seconds later, the doorbell rings
  const tth = wt(seg, 'thirty'), td = wt(seg, 'doorbell');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1000, 560, () => {
    floorLine(); hallDoor(860, 0);
    const lk = prog(t, seg.start + 0.6, 0.3); ctx.save(); ctx.translate(1000, 560); if (lk > 0) { ctx.globalAlpha *= lk; rr(-40, -10, 80, 66, 10, C.red); ctx.beginPath(); ctx.arc(0, -10, 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = C.red; ctx.stroke(); circ(0, 22, 8, '#000'); } ctx.restore();
    bellButton(1180, 520, 1, t >= td ? 0.5 + 0.5 * Math.sin((t - td) * 20) : 0);
    if (t >= td) ripple(1180, 520, td, t, C.red, 30, 200, 6);
    if (t >= tth) text('0:' + String(Math.min(30, Math.floor((t - tth) * 14))).padStart(2, '0'), 1500, 360, '900 90px M', C.fig);
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rrS(-24, -40, 48, 80, 4, C.fig, 5); circ(14, 4, 5, C.fig); ctx.restore(); }, 'LOCK IT OUTSIDE', seg.start + 1.2);
};
S.d7 = (t, seg) => {
  // hiding: it is still a dog; it can smell you anywhere
  const tsm = wt(seg, 'smell');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    // the house in section: three rooms, you in the closet on the right
    rrS(260, 260, 1400, 600, 6, '#5a5a5a', 4); ln(720, 260, 720, 860, 4, '#5a5a5a'); ln(1200, 260, 1200, 860, 4, '#5a5a5a'); ln(260, 560, 1660, 560, 4, '#5a5a5a');
    rrS(1460, 600, 160, 250, 4, C.fig, 4); you(1540, 846, 0.62, { dir: -1 });
    const k = prog(t, seg.start + 0.5, 3.4), dx = lerp(380, 1340, k);
    dog(dx, 860, 0.62, { dir: 1, walk: k < 1 ? t * 12 : null, head: 0.25 });
    if (t >= tsm - 0.6) { ctx.save(); redGlow(12); ctx.globalAlpha *= prog(t, tsm - 0.6, 0.4);
      for (let i = 0; i < 4; i++) { const yy = 700 + i * 30; ctx.beginPath(); for (let x = dx + 60; x < 1520; x += 10) ctx.lineTo(x, yy + Math.sin(x * 0.03 + t * 5 + i) * 10); ctx.strokeStyle = C.red; ctx.lineWidth = 4; ctx.stroke(); }
      ctx.restore(); }
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rrS(-26, -42, 52, 84, 4, C.fig, 5); you(0, 34, 0.18, {}); ctx.restore(); }, 'HIDE', seg.start + 1.0);
};
S.d8 = (t, seg) => {
  // fighting it: a forty-kilo dog with a grown man's mind; it is on your chest before your hand comes down
  const tb = wt(seg, 'body'), tbe = wt(seg, 'before'), tc = wt(seg, 'chest'), ti = wt(seg, 'its'), tsm = wt(seg, 'smiles');
  black();
  shots(t, [
    [seg.start, t0 => { cam(t, t0, tb - t0, 1.0, 1.06, 960, 560, () => { floorLine(); you(760, FL, 1.05, { dir: 1, hand: [820, 420] }); dog(1250, FL, 1.05, { dir: -1, crouch: 0.6, smile: 0.5 }); });
      noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rr(-28, -28, 56, 52, 14, C.fig); ctx.restore(); }, 'FIGHT IT', seg.start + 1.0); }],
    [tb - 0.1, t0 => cam(t, t0, tbe - t0, 1.0, 1.05, 960, 540, () => {
      floorLine(); dog(560, FL, 1.0, { dir: 1, sit: 0 }); you(1380, FL, 1.05, { dir: -1 });
      bigTag(t, t0 + 0.3, 'BODY: 40 KG DOG', 560, 300, C.fig, 46); bigTag(t, wt(seg, 'mind') - 0.1, 'MIND: GROWN MAN', 1380, 300, C.red, 46); })],
    [tbe - 0.1, t0 => { const hit = tc - 0.35, k = ease(prog(t, hit, 0.2)), sh = t > hit && t < hit + 0.4 ? 10 * (1 - (t - hit) / 0.4) : 0;
      cam(t, t0, ti - t0, 1.0, 1.1, 960, 640, () => { ctx.translate(Math.sin(t * 90) * sh, 0); floorLine();
        if (k < 0.5) { you(760, FL, 1.05, { dir: 1, hand: [800 - 40 * prog(t, t0, 0.6), 380 - 60 * prog(t, t0, 0.6)] }); dog(lerp(1250, 900, k * 2), FL, 1.05, { dir: -1, crouch: 1 - k * 2, rear: k, smile: 1 }); }
        else { you(860, FL, 1.05, { pose: 'back', dir: 1 }); dog(820, FL - 40, 1.1, { dir: 1, crouch: 0.4, smile: 1, eye: 1 }); } }); }],
    [ti - 0.1, t0 => { focus(t, t0, segEnd(seg) - t0 + 0.4, 1.0, 1.12, 960, 520, () => {
      dogFace(960, 420, 1.15, { smile: lerp(0.85, 1, prog(t, tsm, 0.5)), eye: 1 });
      glow('rgba(255,255,255,0.25)', 16); pth('M300,1100 C420,860 620,800 960,800 C1300,800 1500,860 1620,1100 Z', C.fig); noGlow(); });
      flatT(() => { ctx.save(); redGlow(12); ln(1560, 520, 1560, 740, 5, C.red); ln(1530, 520, 1590, 520, 5, C.red); ln(1530, 740, 1590, 740, 5, C.red); ctx.restore(); bigTag(t, t0 + 0.3, '1 INCH', 1560, 460, C.red, 44); }); }],
  ]);
};
S.d9 = (t, seg) => {
  // the one thing that works: it copies you
  const tr = wt(seg, 'remember'), tc = wt(seg, 'copies');
  black();
  if (t < tr - 0.1) cam(t, seg.start, tr - seg.start, 1.0, 1.04, 960, 520, () => okRow(t, seg.start + 0.1, 600, 520, 'ONE THING WORKS', 72));
  else cam(t, tr - 0.1, segEnd(seg) - tr, 1.0, 1.06, 960, 560, () => { floorLine();
    you(620, FL, 1.1, { dir: 1 }); dog(1300, FL, 1.1, { dir: -1, sit: 1 });
    ctx.save(); ctx.setLineDash([16, 14]); ctx.lineDashOffset = t * 60; ln(680, 470, 1180, 520, 5, C.fig); ctx.restore();
    bigTag(t, tc - 0.1, 'IT COPIES YOU', 960, 320, C.fig, 52); });
};
S.d10 = (t, seg) => {
  // give it something else to copy: be the dog
  const tb = wt(seg, 'be');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => { floorLine();
    const k = ease(prog(t, tb - 0.2, 0.5));
    if (k < 0.5) you(860, FL, 1.15, { dir: 1 }); else you(860, FL, 1.15, { pose: 'fours', dir: 1 });
    if (t >= tb) pop(t, tb, 960, 250, () => { ctx.save(); glow('rgba(255,255,255,0.4)', 20); text('BE THE DOG.', 960, 280, '900 120px M', C.fig); ctx.restore(); }, 0.35);
  });
};
S.d11 = (t, seg) => {
  // all fours, lips back, teeth, growl. Louder.
  const tl = wt(seg, 'pull'), tt = wt(seg, 'show'), tg = wt(seg, 'growl'), tlo = wt(seg, 'loud');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 820, 600, () => { floorLine();
    you(720, FL, 1.3, { pose: 'fours', dir: 1, lunge: t >= tg ? 0.5 + 0.5 * Math.sin(t * 9) : 0 });
    growlArcs(720 + 140 * 1.3 + 60, FL - 214 * 1.3, t, 1, t >= tlo ? C.red : C.fig, t >= tlo ? 1.5 : 1, prog(t, tg - 0.1, 0.2));
  });
  flatT(() => { const x = 1240; okRow(t, seg.start + 0.1, x, 230, 'ALL FOURS', 40); okRow(t, tl - 0.1, x, 370, 'LIPS BACK', 40); okRow(t, tt - 0.1, x, 510, 'TEETH', 40); okRow(t, tg - 0.1, x, 650, 'GROWL', 40); });
};
S.d12 = (t, seg) => {
  // it hesitates; then it copies you, down onto four legs
  const th = wt(seg, 'hesitates'), tth = wt(seg, 'then'), tc = wt(seg, 'copies');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 580, () => { floorLine();
    you(560, FL, 1.05, { pose: 'fours', dir: 1, lunge: 0.4 + 0.4 * Math.sin(t * 9) });
    const down = ease(prog(t, tc - 0.3, 0.9));
    dog(1360, FL, 1.12, { dir: -1, rear: 1 - down, crouch: down, head: t < tth ? Math.sin(t * 3) * 0.12 + 0.15 : 0, smile: 1 - down * 0.7 });
    growlArcs(560 + 147 + 60, FL - 225, t, 1, C.fig, 0.9, 1);
  });
};
S.d13 = (t, seg) => {
  // face to face, both growling; the more it copies a dog, the less room for you
  const tl = wt(seg, 'lips'), tg = wt(seg, 'growls'), tm = wt(seg, 'more'), tr = wt(seg, 'room');
  black();
  if (t < tm - 0.1) cam(t, seg.start, tm - seg.start, 1.0, 1.08, 960, 600, () => { floorLine();
    you(520, FL, 1.05, { pose: 'fours', dir: 1, lunge: 0.4 + 0.4 * Math.sin(t * 9) });
    dog(1400, FL, 1.05, { dir: -1, crouch: 1, smile: t >= tl ? 1 : 0.4 });
    growlArcs(520 + 147 + 60, FL - 225, t, 1, C.fig, 0.9, 1);
    growlArcs(1400 - 220 - 40, FL - 240, t + 0.3, -1, C.fig, 0.9, prog(t, tg, 0.2));
  });
  else cam(t, tm - 0.1, segEnd(seg) - tm, 1.0, 1.06, 960, 560, () => { floorLine();
    dog(980, FL, 1.4, { dir: 1, crouch: 1 });
    const left = lerp(1, 0.2, ease(prog(t, tr - 0.4, 1.4)));
    insideMe(880, FL - 220, 1.05 * (0.4 + 0.6 * left), left);
    flatT(() => meter(560, 140, 700, 'YOU, INSIDE IT', left));
  });
};
S.d14 = (t, seg) => {
  // one by one the human teeth fall out; click, click, click; sharp dog teeth slide back in
  const clicks = [wt(seg, 'click', 1), wt(seg, 'click', 2), wt(seg, 'click', 3)], tf = wt(seg, 'onto'), tsh = wt(seg, 'sharp');
  black();
  const lostAt = tt => { let n = 0; const st = seg.start + 0.6; if (tt > st) n = Math.min(4, (tt - st) / 0.5); for (const c of clicks) if (tt > c) n += 2; return Math.min(10, n); };
  if (t < tf - 0.1 || t >= tsh - 0.1) {
    const fang = prog(t, tsh, 0.8);
    cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => {
      dogFace(960, 460, 1.2, { smile: 1, lost: t >= tsh - 0.1 ? 10 : lostAt(t), fang, snarl: 1 });
      // falling teeth
      for (let j = 0; j < 10; j++) { const i = TOOTH_ORDER[j];
        let tj = j < 4 ? seg.start + 0.6 + j * 0.5 : clicks[Math.floor((j - 4) / 2)] + (j % 2) * 0.08;
        const dt = t - tj; if (dt < 0 || dt > 1.4) continue;
        const [lx, ly] = toothPos(i, j % 2), x = 960 + lx * 1.2 + (j - 5) * 12 * dt, y = 460 + ly * 1.2 + 900 * dt * dt;
        looseTooth(x, y, 1.1, dt * (j % 2 ? 4 : -4)); }
    });
  } else {
    focus(t, tf - 0.1, tsh - tf, 1.0, 1.08, 960, 800, () => { floorLine(900, '#3a3a3a');
      for (let j = 0; j < 10; j++) looseTooth(560 + hash(j * 3.3) * 800, 880 - hash(j * 1.7) * 30, 1.0, hash(j) * 6); });
  }
};
S.d15 = (t, seg) => {
  // bark, it barks; scratch behind your ear, it scratches; don't stop until the last tooth hits the floor
  const tb = wt(seg, 'bark'), tbs = wt(seg, 'barks'), tsc = wt(seg, 'scratch'), tss = wt(seg, 'scratches'), td = wt(seg, 'do'), tl = wt(seg, 'hits');
  black();
  if (t < td - 0.1) cam(t, seg.start, td - seg.start, 1.0, 1.06, 960, 600, () => { floorLine();
    const sc = t >= tsc && t < tss + 1.4;
    you(520, FL, 1.05, { pose: 'fours', dir: 1, hand: sc ? [520 + 120, FL - 300 + Math.sin(t * 28) * 14] : null, lunge: 0.3 });
    dog(1400, FL, 1.05, { dir: -1, crouch: 0.3, scratch: t >= tss ? 1 : 0, t });
    if (t >= tb && t < tb + 0.9) growlArcs(520 + 147 + 60, FL - 225, t, 1, C.fig, 1.1, 1 - prog(t, tb + 0.5, 0.4));
    if (t >= tbs && t < tbs + 0.9) growlArcs(1400 - 220 - 40, FL - 240, t, -1, C.fig, 1.1, 1 - prog(t, tbs + 0.5, 0.4));
  });
  else focus(t, td - 0.1, segEnd(seg) - td + 0.4, 1.0, 1.15, 960, 800, () => { floorLine(900, '#3a3a3a');
    for (let j = 0; j < 9; j++) looseTooth(560 + hash(j * 3.3) * 800, 880 - hash(j * 1.7) * 30, 1.0, hash(j) * 6);
    const k = clamp((t - (tl - 0.5)) / 0.5), y = lerp(100, 878, k * k);
    looseTooth(1020, y, 1.2, k * 3);
    if (t >= tl) ripple(1020, 890, tl, t, C.red, 20, 160, 5);
  });
};
S.d16 = (t, seg) => {
  // the question only a real dog cannot answer
  const tw = wt(seg, "who's");
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => { floorLine();
    you(640, FL, 1.05, { pose: 'kneel', dir: 1, hand: [820, 600] }); dog(1260, FL, 1.05, { dir: -1, sit: 1 });
    if (t >= tw - 0.1) say(t, tw - 0.1, 760, 230, "WHO'S A GOOD BOY?", 660, 400, 56);
  });
};
S.d17 = (t, seg) => {
  // it does not say "I am"; it just wags its tail
  const tj = wt(seg, 'just');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1100, 560, () => { floorLine();
    dog(1100, FL, 1.25, { dir: -1, sit: t >= tj ? 0 : 1, wag: t >= tj ? t * 18 : 0 });
    if (t < tj + 0.4) { say(t, seg.start + 0.2, 1500, 300, 'I AM.', 1260, 460, 60, { red: true }); redX(1500, 300, 90, prog(t, seg.start + 0.9, 0.3)); }
  });
};

// ---------- the morning ----------
S.e1 = (t, seg) => {
  // morning: asleep in its own bed, normal teeth, normal dog
  const tn = wt(seg, 'normal'), tn2 = wt(seg, 'normal', 2);
  black();
  focus(t, seg.start, segEnd(seg) - seg.start, 1.5, 1.65, 1000, 700, () => { floorLine();
    rrS(1340, 220, 300, 300, 6, '#5a5a5a', 4); icon('sun', 1490, 370, 1.1);
    dogBed(900, 1.2); ctx.save(); ctx.translate(900, FL - 30); ctx.scale(1.15, 1.15); glow('rgba(255,255,255,0.25)', 14); ell(0, -40, 150, 52, 0, C.fig); ctx.restore(); noGlow();
    ctx.save(); ctx.translate(1060, FL - 100); ctx.scale(0.85, 0.85); dogHead({ close: true }); ctx.restore();
  });
  flatT(() => { okRow(t, tn - 0.1, 160, 220, 'NORMAL TEETH', 40); okRow(t, tn2 - 0.1, 160, 370, 'NORMAL DOG', 40); });
};
S.e2 = (t, seg) => {
  // brushing your teeth; you smile at the mirror
  const ts = wt(seg, 'smile');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 960, 480, () => {
    mirrorFrame(560, 120, 800, 620, { inner: () => { glow('rgba(255,255,255,0.25)', 14); circ(960, 420, 120, C.fig); rr(820, 560, 280, 260, 60, C.fig); noGlow();
      ctx.save(); ctx.translate(1100, 470); ctx.rotate(-0.6); rr(-10, -10, 160, 20, 8, '#9a9a9a'); rr(-40, -16, 40, 32, 6, '#cfcfcf'); ctx.restore(); } });
    rr(480, 760, 960, 40, 8, C.fig); ln(960, 800, 960, 860, 30, '#8a8a8a');
  });
};
S.e3 = (t, seg) => {
  // top row, left side: one tooth is long, sharp, and not yours
  const tl = wt(seg, 'left'), to = wt(seg, 'one'), tsh = wt(seg, 'sharp');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.25, lerp(960, 760, ease(prog(t, tl, 0.6))), 460, () => {
    teethRow(960, 400, 1.15, { fangAt: 2, fang: ease(prog(t, to, 1.4)) });
    if (t >= tsh) { ctx.save(); redGlow(16); circS(960 - 5 * 76 * 1.15 + 2.5 * 76 * 1.15, 520, 120, C.red, 6); ctx.restore(); }
  });
};
S.e4 = (t, seg) => {
  // it copied you; for a few minutes last night, you copied it
  const ty = wt(seg, 'you', 2);
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.0, 1.06, 960, 560, () => { floorLine();
    you(620, FL, 1.1, { dir: 1, red: t >= ty ? 0.8 : 0 }); dog(1300, FL, 1.1, { dir: -1, sit: 1 });
    const arr = (x0, x1, y, col, p) => { if (p <= 0) return; ctx.save(); if (col === C.red) redGlow(14); lnP(x0, y, x1, y, 10, col, p); if (p >= 1) { ctx.translate(x1, y); ctx.scale(Math.sign(x1 - x0), 1); pth('M0,-24 L32,0 L0,24 Z', col); } ctx.restore(); };
    arr(1180, 760, 380, C.fig, prog(t, seg.start + 0.3, 0.5));
    arr(760, 1180, 470, C.red, prog(t, ty, 0.5));
  });
};
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.e6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
