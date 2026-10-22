// ---------- EP07 v4 scenes: "If Your Interviewer Ever Asks 'What Is Your Greatest Weakness?'" (Protocol 404) ----------
// Pure black, pure white vector figures, red only for danger. The interviewers are three near-identical bald agents in sunglasses.
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));
const segEnd = seg => seg.end + 0.7;
const seg$ = id => window.TL.segments.find(s => s.id === id);
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const flatT = fn => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); fn(); ctx.restore(); };
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
const KINDS = ['young', 'hr', 'boss'];

// ---------- the interview room ----------
const IX = [560, 960, 1360], DESK_Y = 700, CLOCK = [300, 280];
const HEADY = DESK_Y - 294;   // the agents' face centre when seated
// o.arms: one mode or three; o.eyes (middle 0..1); o.lean/o.tilt (middle); o.stand 0..1 (they rise); o.me: your back in the foreground; o.who [bools]; o.reach (left one's hand)
function room(t, o = {}) {
  meetRoom({ clock: o.clock, secRed: o.secRed, clockAt: o.clockAt ?? CLOCK });
  if (o.door) roomDoor(t, o.door);
  for (let i = 0; i < 3; i++) {
    if (o.who && !o.who[i]) continue;
    const st = ease(o.standI ? o.standI[i] : (o.stand || 0));
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'desk');
    agent(KINDS[i], IX[i], st > 0.01 ? DESK_Y + 300 - st * 120 : DESK_Y, 1, { stand: st > 0.01 ? 1 : 0, arms, eyes: i === 1 ? (o.eyes ?? 0) : 0, lean: i === 1 ? o.lean : 0, tilt: i === 1 ? o.tilt : 0,
      shake: o.shake ? o.shake[i] : 0, t, reach: o.reach, lid: o.lid, look: o.look });
  }
  meetDesk(260, 1660, DESK_Y, { n: 3 });
  if (o.me) meBack(o.meX ?? 960, 1400, 1.3);
}
// a door in the right of the room: white outline; o = { lock: 0..1 red padlock, open: 0..1 }
function roomDoor(t, d) {
  rrS(1720, 330, 170, 430, 4, C.fig, 5); circ(1742, 560, 8, C.fig);
  spaced('EXIT', 1805, 310, '900 30px M', '#8a8a8a', 8);
  if (d.lock > 0) { ctx.save(); ctx.globalAlpha *= d.lock; const red = d.open ? 1 - d.open : 1;
    ctx.translate(1805, 560); ctx.beginPath(); ctx.arc(0, -30 - 30 * (d.open || 0), 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = red > 0.5 ? C.red : C.fig; ctx.stroke();
    red > 0.5 ? redGlow(20) : glow(); rr(-40, -30, 80, 66, 10, red > 0.5 ? C.red : C.fig); noGlow(); circ(0, 0, 8, '#000'); ctx.restore(); }
}
// a "does not work" header at the top left with a red X on the icon at tx
function noHead(t, seg, ic, label, tx) {
  flatT(() => slideIn(t, seg.start, -40, 0, () => { const w = 190 + label.length * 31; ctx.save(); ctx.globalAlpha *= 0.88; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    icon7(ic, 125, 125, 0.5); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35));
}
// a small white note card (what they write down)
function noteCard(t, t0, x, y, str, rot = -0.05, col = '#111') {
  if (t < t0) return;
  pop(t, t0, x, y, () => { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.font = '900 44px M'; const w = ctx.measureText(str).width + 80;
    glow(); rr(-w / 2, -50, w, 100, 10, '#fbfbfb'); noGlow(); text(str, 0, 16, '900 44px M', col); ctx.restore(); }, 0.3);
}

// ---------- the night bedroom (rule 4) ----------
const TRIO = [1130, 1350, 1570];
// you sitting up in bed, facing right
function sitUpInBed(s = 1.3) {
  ctx.save(); ctx.translate(360, 900); ctx.scale(s, s);
  glow('rgba(255,255,255,0.25)', 16); rr(110, -360, 90, 190, 36, C.fig); circ(156, -410, 46, C.fig); noGlow(); circ(186, -416, 9, '#000');
  ctx.save(); glow('rgba(255,255,255,0.2)', 8); poly([[130, -320], [176, -250], [236, -236]], 26, C.fig); noGlow(); ctx.restore();
  ctx.restore();
}
function nightRoom(o = {}) {
  black(); ln(-200, 900, W + 200, 900, 3, '#262626');
  if (o.door !== false) { const op = o.doorOpen || 0;
    if (op > 0) { ctx.save(); ctx.globalAlpha *= 0.5 * op; rr(1700, 380, 180, 520, 2, '#1a1a1a'); ctx.restore(); }
    rrS(1700, 380, 180 * (1 - op * 0.7), 520, 4, C.fig, 5); circ(1720 + 0 * op, 650, 8, C.fig); }
  // the bedside clock: 3:00 in red
  rrS(150, 760, 160, 140, 6, '#5a5a5a', 3); rrS(166, 690, 128, 60, 8, C.fig, 4); ctx.save(); redGlow(14); text(o.time || '3:00', 230, 736, '900 40px M', C.red); ctx.restore();
}
// the three standing at the foot of the bed. o.arms (one or three), o.eyes, o.xs, o.s, o.y, o.shake [3], o.who, o.boxes 0..1, o.badges 0..1, o.drop 0..1
function trio(t, o = {}) {
  const xs = o.xs || TRIO, s = o.s || 0.78, y = o.y ?? 900;
  for (let i = 0; i < 3; i++) { if (o.who && !o.who[i]) continue;
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'board');
    const x = xs[i] + (o.walk ? o.walk[i] : 0);
    agent(KINDS[i], x, y, s, { stand: 1, arms, eyes: i === 1 ? (o.eyes ?? 1) : 0, shake: o.shake ? o.shake[i] : 0, t });
    if (o.badges) { ctx.save(); ctx.globalAlpha *= o.badges; ctx.translate(x, y - 300 * s); ctx.scale(s, s); rr(30, -150, 72, 44, 5, C.fig); rrS(30, -150, 72, 44, 5, '#000', 3); text('STAFF', 66, -121, '900 17px M', '#000'); ctx.restore(); }
    if (o.boxes) cardboardBox(x, y - 300 * s + 20 * s, s * 1.05, o.boxes);
  }
  if (o.drop) for (let i = 0; i < 3; i++) {   // their clipboards on the floor
    const k = ease(o.drop), x = xs[i] - 20, yy = lerp(y - 420 * s, y - 10, k);
    ctx.save(); ctx.translate(x, yy); ctx.rotate(lerp(-0.06, 1.45 + i * 0.1, k)); clipboard(0, 0, 0.8 * s / 0.78); ctx.restore(); }
}
// a cardboard box held at the waist: a stapler and a sad little plant inside
function cardboardBox(x, y, s, a = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha *= a;
  // plant: drooping leaves
  ln(20, -70, 20, -150, 5, '#000'); ln(20, -70, 20, -150, 3, C.fig);
  for (const [dx, dy, r] of [[-26, -128, -0.9], [60, -120, 0.9], [-14, -160, -0.4], [50, -160, 0.6]]) { ctx.save(); ctx.translate(20 + dx * 0.5, dy + 10); ctx.rotate(r); ell(dx * 0.5, 0, 26, 11, 0, C.fig); ctx.beginPath(); ctx.ellipse(dx * 0.5, 0, 26, 11, 0, 0, Math.PI * 2); ctx.strokeStyle = '#000'; ctx.lineWidth = 2.5; ctx.stroke(); ctx.restore(); }
  rr(-4, -96, 48, 34, 4, C.fig); rrS(-4, -96, 48, 34, 4, '#000', 3);   // the pot
  // stapler
  rr(-110, -92, 100, 22, 8, '#111'); rrS(-110, -92, 100, 22, 8, C.fig, 2.5); rr(-110, -72, 100, 10, 3, '#111'); rrS(-110, -72, 100, 10, 3, C.fig, 2.5);
  // the box
  glow('rgba(255,255,255,0.25)', 18); rr(-150, -70, 300, 170, 6, C.fig); noGlow(); rrS(-150, -70, 300, 170, 6, '#000', 3);
  pth('M-150,-70 L-176,-104 L-130,-104 L-110,-70 Z', C.fig); pthS('M-150,-70 L-176,-104 L-130,-104 L-110,-70', '#000', 3);
  pth('M150,-70 L176,-104 L130,-104 L110,-70 Z', C.fig); pthS('M150,-70 L176,-104 L130,-104 L110,-70', '#000', 3);
  rr(-40, -40, 80, 26, 13, '#000');   // the hand hole
  ctx.restore();
}
function night(t, o = {}) {
  nightRoom(o);
  if (o.sitUp) { bed(360, 900, 1.3, 'empty'); sitUpInBed(); } else bed(360, 900, 1.3, o.bed || 'woke', { look: 1 });
  if (o.trio !== false) trio(t, o);
}

// ---------- the handshake close-up ----------
// your arm from the left (plain white), his from the right (sleeve, cuff, outline). o.sq 0..1 his grip; o.shake px; o.crack 0..1; o.apart 0..1; o.long 0..1 (his hand stretches)
function handshake(t, o = {}) {
  const ap = ease(o.apart || 0), sh = o.shake ? Math.sin(t * 60) * o.shake : 0;
  ctx.save(); ctx.translate(-260 * ap, 0);
  glow('rgba(255,255,255,0.3)', 20); poly([[-200, 760], [700, 580]], 120, C.fig); noGlow();
  ctx.save(); ctx.translate(780, 566); ctx.rotate(-0.2); const yh = 'M-70,-52 C30,-74 120,-46 134,-4 C126,40 40,62 -70,52 Z';
  glow('rgba(255,255,255,0.25)', 14); pth(yh, C.fig); noGlow(); pthS(yh, '#000', 4); pthS('M-10,-58 C30,-40 50,-20 56,4', '#000', 4); ctx.restore();
  ctx.restore();
  ctx.save(); ctx.translate(260 * ap + sh, sh * 0.4);
  ctx.save(); ctx.lineCap = 'round'; poly([[2200, 380], [1150, 540]], 132, '#000'); poly([[2200, 380], [1150, 540]], 122, C.fig); ctx.restore();
  ctx.save(); ctx.translate(1150, 540); ctx.rotate(-0.15); ln(40, -58, 40, 58, 4, '#000'); ctx.restore();   // the shirt cuff
  const L = 1 + 0.5 * (o.long || 0), sq = o.sq || 0;
  // his hand wraps over yours: a long mitten
  ctx.save(); ctx.translate(1080, 550); ctx.scale(1 - 0.06 * sq, 1 - 0.1 * sq);
  const hp = `M60,-70 C${-120 * L},-96 ${-260 * L},-60 ${-270 * L},10 C${-268 * L},64 ${-150 * L},80 0,74 C40,72 70,40 70,0 Z`;
  glow('rgba(255,255,255,0.25)', 16); pth(hp, C.fig); noGlow(); pthS(hp, '#000', 5);
  pthS(`M${-60 * L},-62 C${-110 * L},-30 ${-150 * L},10 ${-160 * L},50`, '#000', 4);   // the thumb's edge
  ctx.restore(); ctx.restore();
  if (o.crack > 0) { ctx.save(); ctx.globalAlpha *= o.crack; redGlow(20);
    for (const [a, l] of [[-2.4, 90], [-1.2, 110], [0.4, 80], [2.2, 100], [-0.3, 130]]) { const x0 = 860 + Math.cos(a) * 110, y0 = 560 + Math.sin(a) * 80;
      poly([[x0, y0], [x0 + Math.cos(a) * l * 0.5 + 14, y0 + Math.sin(a) * l * 0.5 - 10], [x0 + Math.cos(a) * l, y0 + Math.sin(a) * l]], 6, C.red); }
    noGlow(); ctx.restore(); }
}
// the grip meter: two bars, YOU and HIM. o.you, o.him 0..1.6 (over 1 = red, past the top)
function gripMeter(t, o) {
  flatT(() => {
    const bars = [['YOU', o.you, 200], ['HIM', o.him, 380]];
    for (const [lab, v, x] of bars) {
      rrS(x - 45, 120, 90, 360, 10, '#5a5a5a', 4);
      const h = 340 * Math.min(v, 1.3), red = v > 1.0;
      ctx.save(); if (red) redGlow(24); rr(x - 35, 470 - h, 70, h, 6, red ? C.red : C.fig); noGlow(); ctx.restore();
      text(lab, x, 540, '900 44px M', red ? C.red : C.fig);
    }
    ln(140, 130, 440, 130, 3, '#8a8a8a'); text('MAX', 290, 105, '600 24px Plex', '#8a8a8a');
  });
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the three agents, the question already asked; the middle one's lenses are red
  const td = wt(seg, 'do');
  cam(t, 0, seg.end + 0.6, 1.0, 1.12, 960, 470, () => room(t, { me: true, eyes: 1 }));
  if (t < td - 0.1) say(t, -1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 250, 50);
  else pop(t, td - 0.1, 960, 140, () => tag('DO NOT TELL THE TRUTH', 960, 150, C.red, 56, 'center'), 0.3);
};
function teaserBox(t, seg, w0, draw, tx, y, x = 1600) {
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); draw(x, y); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  // three quick "do not"s: the handshake, where you live, no questions
  const ws = [[seg.start, wt(seg, 'do', 2), 'hard'], [wt(seg, 'do', 2), wt(seg, 'and'), 'live'], [wt(seg, 'and'), nextStart(seg), 'questions']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    black();
    if (i === 0) cam(t, w0, blk - w0, 1.0, 1.12, 960, 560, () => handshake(t, { sq: prog(t, w0 + 0.3, blk - w0 - 0.5), shake: 4 * prog(t, w0 + 0.6, 0.6), crack: prog(t, hit, 0.15) }));
    else if (i === 1) cam(t, w0, blk - w0, 1.0, 1.2, 800, 520, () => clipboard(800, 540, 3.6, -0.05, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 0]], under: 2, up: prog(t, w0 + 0.6, 1.0) }));
    else { const k = ease(prog(t, w0 + 0.3, hit - w0 - 0.3)); focus(t, w0, blk - w0, 2.6, 3.0, ...CLOCK, () => meetRoom({ clock: [9, lerp(47, 0, k), 30 * (1 - k)], secRed: true, floor: false })); }
    if (d > 0) flatT(() => { ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); });
  }
  blackAfter(t, blk);
  const draws = [(x, y) => pageIcon('hand', x, y, '#fff'), (x, y) => icon7('pin', x, y, 0.9), (x, y) => icon7('ask', x, y, 1.0)];
  flatT(() => teaserBox(t, seg, w0, draws[i], wt(seg, word), 250, i === 2 ? 1600 : (i === 0 ? 1600 : 1600)));
};

// ---------- rule 1: do not shake too hard ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT SHAKE TOO HARD');
S.a1 = (t, seg) => {
  // the one on the left stands and holds out his hand; his fingers are longer than they should be
  const th = wt(seg, 'hand'), tf = wt(seg, 'fingers');
  if (t < tf - 0.2) {
    cam(t, seg.start, tf - seg.start, 1.0, 1.25, 700, 470, () => room(t, { arms: [t >= th - 0.6 ? 'hand' : 'desk', 'desk', 'laptop'], standI: [prog(t, seg.start + 0.3, 0.7), 0, 0], reach: ease(prog(t, th - 0.6, 0.8)), lid: 0, me: true, meX: 760 }));
    return;
  }
  black();
  cam(t, tf - 0.2, segEnd(seg) - tf, 1.0, 1.1, 1150, 560, () => handshake(t, { apart: 1 - 0, long: ease(prog(t, tf, 1.2)) }));
  if (t >= tf + 0.5) flatT(() => { ctx.save(); ctx.setLineDash([10, 10]); ln(620, 800, 1380, 800, 3, '#8a8a8a'); ctx.restore(); text('TOO LONG', 1000, 860, '900 48px M', C.red); });
};
S.a2 = (t, seg) => {
  // everyone's advice: a firm handshake, show them you are strong
  const tf = wt(seg, 'firm'), ts = wt(seg, 'show');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('EVERYONE SAYS', 960, 260, '900 44px M', '#8a8a8a', 14), 0.4);
    okRow(t, tf - 0.3, 480, 450, 'A FIRM HANDSHAKE.', 64);
    okRow(t, ts - 0.3, 480, 650, 'SHOW THEM YOU ARE STRONG.', 56);
  });
};
S.a3 = (t, seg) => {
  // "Do not." The advice is crossed out. A firm grip is a challenge, and they always answer one.
  const tc = wt(seg, 'challenge'), ta = wt(seg, 'answer');
  if (t < tc - 0.2) {
    black();
    cam(t, seg.start, tc - seg.start, 1.0, 1.04, 960, 520, () => {
      spaced('EVERYONE SAYS', 960, 260, '900 44px M', '#5a5a5a', 14);
      okRow(t, -9, 480, 450, 'A FIRM HANDSHAKE.', 64); okRow(t, -9, 480, 650, 'SHOW THEM YOU ARE STRONG.', 56);
      ctx.save(); redGlow(12); lnP(460, 470, 1500, 430, 12, C.red, prog(t, seg.start + 0.1, 0.25)); lnP(460, 670, 1560, 630, 12, C.red, prog(t, seg.start + 0.3, 0.25)); ctx.restore();
    });
    return;
  }
  // close on the left agent: a glint in his lenses
  focus(t, tc - 0.2, segEnd(seg) - tc, 2.2, 2.5, IX[0] - 200, HEADY + 20, () => room(t, { arms: 'desk', lid: 0, look: Math.sin(t * 2) }));
  if (t >= ta) flatT(() => pop(t, ta, 520, 560, () => { tag('CHALLENGE', 520, 540, C.red, 64, 'center'); tag('ACCEPTED', 520, 650, C.red, 64, 'center'); }, 0.3));
};
S.a4 = (t, seg) => {
  // squeeze, and he squeezes back; harder; he does not stop when you stop
  const tq = wt(seg, 'squeezes'), th = wt(seg, 'harder', 1), th2 = wt(seg, 'harder', 2), ts = wt(seg, 'stop', 2);
  const you = t < ts ? lerp(0.3, 0.85, ease(prog(t, seg.start, 1.0))) : lerp(0.85, 0.15, ease(prog(t, ts - 0.4, 0.5)));
  const him = Math.max(0, lerp(0, 0.7, ease(prog(t, tq - 0.2, 0.6))) + 0.25 * ease(prog(t, th, 0.5)) + 0.35 * ease(prog(t, th2, 0.5)) + 0.4 * prog(t, ts, 1.5));
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 860, 560, () => handshake(t, { sq: clamp(him), shake: him > 1 ? 4 : him * 2 }));
  gripMeter(t, { you, him });
};
S.a5 = (t, seg) => {
  // the waiting room: a row of candidates; a crack through the door; every head turns
  const th = wt(seg, 'heard'), tw = wt(seg, 'waiting');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.2, 1.0, 1.08, 900, 560, () => {
    ln(-200, 900, W + 200, 900, 3, '#262626');
    rrS(1480, 360, 220, 540, 4, C.fig, 5); circ(1504, 640, 8, C.fig); spaced('INTERVIEW', 1590, 330, '900 30px M', '#8a8a8a', 6);
    for (let i = 0; i < 4; i++) sitSide(260 + i * 290, 900, 0.95, { dir: 1, hair: i === 1 });
    if (t >= th - 0.15) { const k = prog(t, th - 0.15, 0.2); ctx.save(); ctx.globalAlpha *= k; redGlow(24);
      for (const [a, l] of [[-2.6, 120], [-3.0, 160], [2.7, 120], [-2.2, 90]]) { const x0 = 1470, y0 = 560; poly([[x0, y0], [x0 + Math.cos(a) * l * 0.5 + 10, y0 + Math.sin(a) * l * 0.5 + 12], [x0 + Math.cos(a) * l, y0 + Math.sin(a) * l]], 7, C.red); }
      noGlow(); ctx.restore();
      for (let i = 0; i < 4; i++) pop(t, th + 0.1 + i * 0.08, 260 + i * 290, 420, () => text('!', 260 + i * 290 + 10, 470 - 0 * 0.95, '900 60px M', C.fig), 0.2); }
    if (t >= th + 0.1) pop(t, th + 0.1, 1590, 220, () => tag('CRACK.', 1590, 230, C.red, 60, 'center'), 0.25);
  });
};
S.a6 = (t, seg) => {
  // he signs everything with his left hand now: a right arm in a cast and sling, the left hand writing
  const tl = wt(seg, 'left');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => {
    // the contract
    glow(); rr(560, 380, 620, 560, 8, '#fbfbfb'); noGlow(); text('CONTRACT', 870, 460, '900 44px M', '#111');
    for (let i = 0; i < 6; i++) rr(620, 510 + i * 44, i % 3 === 2 ? 300 : 500, 12, 3, '#c4c4c8');
    ln(620, 860, 1000, 860, 3, '#111');
    const k = prog(t, seg.start + 0.4, 2.2);
    ctx.save(); ctx.beginPath(); for (let i = 0; i <= 40 * k; i++) { const x = 640 + i * 8.5, y = 836 + Math.sin(i * 0.9) * 18 * (1 - i / 50) + (i % 7 === 0 ? -14 : 0); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.stroke(); ctx.restore();
    // the left hand with the pen, shaky
    const px = 640 + 340 * k, py = 836 + Math.sin(t * 30) * 4;
    pen(px, py, 1.2, -0.5); ctx.save(); glow(); ell(px + 40, py - 60, 50, 36, -0.5, C.fig); noGlow(); ctx.beginPath(); ctx.ellipse(px + 40, py - 60, 50, 36, -0.5, 0, Math.PI * 2); ctx.strokeStyle = '#000'; ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
    // the right arm in a cast and a sling
    ctx.save(); glow(); rr(1300, 300, 130, 420, 60, C.fig); noGlow(); rrS(1300, 300, 130, 420, 60, '#000', 3); for (let i = 0; i < 5; i++) ln(1310, 380 + i * 60, 1420, 400 + i * 60, 2, '#9a9a9a');
    ln(1290, 260, 1440, 760, 10, '#5a5a5a'); ctx.restore();
  });
  if (t >= tl) flatT(() => pop(t, tl, 960, 160, () => tag('LEFT HAND ONLY', 960, 170, C.red, 56, 'center'), 0.3));
};
S.a7 = (t, seg) => {
  // keep your hand soft; let him hold it; count to three
  const tc = wt(seg, 'count'), th = wt(seg, 'three');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 860, 560, () => handshake(t, { sq: 0.15 }));
  gripMeter(t, { you: 0.12, him: 0.18 });
  if (t >= tc) flatT(() => { for (let k = 0; k < 3; k++) { const t0 = tc + 0.25 + k * ((th - tc) / 2.2); if (t >= t0) pop(t, t0, 360 + k * 220, 220, () => text(String(k + 1), 360 + k * 220, 260, '900 140px M', C.fig), 0.25); } });
};
S.a8 = (t, seg) => {
  // he loses interest and lets go; he writes "NOT A THREAT"
  const tl = wt(seg, 'lets'), tw = wt(seg, 'writes'), tg = wt(seg, 'good');
  black();
  if (t < tw - 0.2) { cam(t, seg.start, tw - seg.start, 1.0, 1.04, 960, 560, () => handshake(t, { apart: prog(t, tl - 0.2, 0.8) })); return; }
  cam(t, tw - 0.2, segEnd(seg) - tw, 1.0, 1.06, 960, 520, () => {
    clipboard(960, 540, 3.2, -0.04, { lines: [['CANDIDATE', 0], ['GRIP: SOFT', 0], ['NOT A THREAT', 0]], under: 2, up: prog(t, tw + 0.6, 0.8) });
  });
  if (t >= tg) flatT(() => { ctx.save(); ctx.translate(1480, 300); check(0, 0, 70, prog(t, tg, 0.3)); ctx.restore(); });
};

// ---------- rule 2: do not tell the truth ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT TELL THE TRUTH');
function folder(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 22);
  rr(-260, -200, 200, 50, 10, '#d8d8d8'); rr(-260, -170, 520, 360, 12, '#ececec'); noGlow(); rrS(-260, -170, 520, 360, 12, '#000', 3);
  text('CANDIDATE: YOU', -220, -100, '900 36px M', '#111', 'left'); ln(-220, -80, 220, -80, 3, '#9a9a9a');
  (o.lines || []).forEach((l, i) => text(l, -220, -30 + i * 46, '900 30px M', l.startsWith('!') ? '#d61f1f' : '#333', 'left'));
  if (!o.lines) for (let i = 0; i < 3; i++) rr(-220, -40 + i * 40, i === 2 ? 220 : 360, 14, 4, '#b9b9b9');
  ctx.restore();
}
// a small house pictogram
function house(x, y, s = 1, col = C.fig) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16); pth('M-70,0 L-70,-80 L0,-140 L70,-80 L70,0 Z', col); noGlow(); rr(-18, -60, 36, 60, 3, '#000'); ctx.restore(); }
S.b1 = (t, seg) => {
  // everything goes into a file; the file is a map to you
  const tm = wt(seg, 'map', 1), tm2 = wt(seg, 'map', 2);
  black();
  if (t < tm - 0.2) { cam(t, seg.start, tm - seg.start, 1.0, 1.1, 960, 540, () => folder(960, 560, 1.4, { lines: ['NAME', 'LAST JOB', 'ADDRESS'] })); return; }
  cam(t, tm - 0.2, segEnd(seg) - tm, 1.0, 1.08, 960, 540, () => {
    // a street map: a grid, the office on the left, your house on the right, a red route drawn between them
    for (let i = 0; i < 9; i++) { ln(160 + i * 200, 120, 160 + i * 200, 980, 3, '#262626'); ln(100, 140 + i * 110, 1820, 140 + i * 110, 3, '#262626'); }
    glow(); rr(220, 420, 160, 200, 6, C.fig); noGlow(); for (let i = 0; i < 3; i++) for (let j = 0; j < 4; j++) rr(240 + i * 46, 440 + j * 44, 30, 26, 3, '#000'); text('ROOM 4B', 300, 670, '900 30px M', '#8a8a8a');
    house(1580, 760, 1.2);
    const route = [[380, 520], [760, 520], [760, 250], [1160, 250], [1160, 690], [1500, 690]], p = prog(t, tm + 0.1, 1.6);
    ctx.save(); ctx.setLineDash([22, 16]); redGlow(14); let acc = 0; const segs = route.slice(1).map((q, i) => Math.hypot(q[0] - route[i][0], q[1] - route[i][1])), tot = segs.reduce((a, b) => a + b, 0);
    ctx.beginPath(); ctx.moveTo(...route[0]); for (let i = 0; i < segs.length; i++) { const r = clamp((p * tot - acc) / segs[i]); if (r <= 0) break; ctx.lineTo(lerp(route[i][0], route[i + 1][0], r), lerp(route[i][1], route[i + 1][1], r)); acc += segs[i]; }
    ctx.strokeStyle = C.red; ctx.lineWidth = 9; ctx.stroke(); ctx.restore();
    if (t >= tm2) pop(t, tm2, 1580, 560, () => { ctx.save(); redGlow(20); icon7('pin', 1580, 540, 0.8, C.red); ctx.restore(); text('YOU', 1580, 900, '900 50px M', C.red); }, 0.3);
  });
};
S.b2 = (t, seg) => {
  // "Tell me about yourself." Your name, one sentence, then stop.
  const ts = wt(seg, 'say', 1), to = wt(seg, 'one'), tt = wt(seg, 'stop');
  if (t < ts - 0.2) { cam(t, seg.start, ts - seg.start, 1.0, 1.08, 960, 470, () => room(t, { me: true, lid: 0 })); say(t, seg.start + 0.05, 960, 120, 'TELL ME ABOUT YOURSELF.', 960, 250, 50); return; }
  black();
  cam(t, ts - 0.2, segEnd(seg) - ts, 1.0, 1.05, 960, 520, () => {
    sitSide(480, 900, 1.35, { dir: 1 });
    [['SAY YOUR NAME.', ts], ['ONE SENTENCE.', to], ['THEN STOP.', tt]].forEach(([l, t0], i) => okRow(t, t0 - 0.15, 860, 300 + i * 190, l, 58));
  });
};
S.b3 = (t, seg) => {
  // never say you live alone: she said it; the one in the middle wrote it down and underlined it twice
  const tc = wt(seg, 'candidate'), tw = wt(seg, 'wrote'), tu = wt(seg, 'underlined'), t2 = wt(seg, 'twice');
  if (t < tw - 0.3) {
    black();
    cam(t, seg.start, tw - seg.start, 1.0, 1.06, 760, 560, () => {
      ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(560, 900, 1.3, { dir: 1, hair: true });
      if (t < tc) { listCard(240, 90, 860, 190); noRow(t, seg.start, seg.start + 0.9, 290, 185, 'pin', 'I LIVE ALONE', 60); }
      else say(t, tc, 700, 240, 'I LIVE ALONE.', 640, 360, 56);
      agent('hr', 1500, 760, 0.9, { arms: 'desk' }); meetDesk(1150, 1850, 760, { items: false });
    });
    return;
  }
  black();
  const up1 = prog(t, tu - 0.05, 0.6), up2 = prog(t, t2 - 0.05, 0.5);
  cam(t, tw - 0.3, segEnd(seg) - tw + 1.2, 1.0, 1.2, 900, 520, () => {
    clipboard(900, 560, 4.4, -0.04, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', up1 > 0.9 ? 1 : 0]], under: 2, up: up1 });
    ctx.save(); ctx.translate(900, 560); ctx.rotate(-0.04); ctx.scale(4.4, 4.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width;
    if (up2 > 0) lnP(-62, 40, -58 + w, 39, 3.5, '#d61f1f', up2);
    pen(-62 + (w + 4) * (up2 > 0 ? up2 : up1), (up2 > 0 ? 8 : 0) - 24 + 2 * 28, 0.6, 2.0); ctx.restore();
  });
};
S.b4 = (t, seg) => {
  // living alone: no one notices when you stop coming home. Your window goes dark; the mail piles up; the days count.
  const tn = wt(seg, 'notice'), ts = wt(seg, 'stop');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.2, 1.0, 1.1, 960, 560, () => {
    ln(-200, 940, W + 200, 940, 3, '#262626');
    rrS(560, 140, 800, 800, 4, C.fig, 5);
    for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) { const mine = r === 2 && c === 3, dark = mine && t >= ts - 0.2;
      if (dark) rrS(620 + c * 150, 190 + r * 140, 90, 80, 3, '#5a5a5a', 3); else { glow('rgba(255,255,255,0.4)', 14); rr(620 + c * 150, 190 + r * 140, 90, 80, 3, C.fig); noGlow(); } }
    // your door: the mail piles up
    rrS(1460, 700, 150, 240, 4, C.fig, 4);
    const n = Math.floor(lerp(0, 9, ease(prog(t, tn, 2.5))));
    for (let i = 0; i < n; i++) { ctx.save(); ctx.translate(1535 + (hash(i) - 0.5) * 80, 930 - i * 14); ctx.rotate((hash(i * 3) - 0.5) * 0.5); rr(-50, -12, 100, 28, 3, '#fbfbfb'); rrS(-50, -12, 100, 28, 3, '#000', 2); ctx.restore(); }
    if (t >= tn) { const d = Math.floor(lerp(1, 31, ease(prog(t, tn, 3.0)))); pop(t, tn, 360, 300, () => { listCard(170, 220, 380, 160); text('DAYS GONE', 360, 270, '600 26px Plex', '#8a8a8a'); text(String(d), 360, 350, '900 64px M', C.red); }, 0.3); }
  });
};
S.b5 = (t, seg) => {
  const tl = wt(seg, 'leans'), tg = wt(seg, 'leans') + 0.6, tw = wt(seg, 'what'), lean = ease(prog(t, tl, 1.2));
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.6, 960, 420, () => room(t, { lean, eyes: prog(t, tg - 0.1, 0.4), lid: 0 }));
  say(t, tw - 0.1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 230, 46);
};
S.b6 = (t, seg) => {
  // your real weakness is how they will come for you
  const tr = wt(seg, 'real'), th = wt(seg, 'how');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    pop(t, seg.start, 960, 260, () => { glow(); spaced('DO NOT TELL THE TRUTH', 960, 290, '900 70px M', C.fig, 6); noGlow(); }, 0.3);
    if (t >= tr - 0.1) slideIn(t, tr - 0.1, -40, 0, () => { glow(); rr(300, 480, 560, 150, 16, C.fig); noGlow(); text('YOUR REAL', 580, 545, '900 48px M', '#000'); text('WEAKNESS', 580, 600, '900 48px M', '#000'); }, 0.35);
    if (t >= th - 0.3) { lnP(880, 555, 1040, 555, 10, C.red, prog(t, th - 0.3, 0.3)); pth('M1040,525 L1090,555 L1040,585 Z', t >= th ? C.red : 'rgba(0,0,0,0)'); }
    if (t >= th) slideIn(t, th, 40, 0, () => { redGlow(26); rr(1100, 480, 560, 150, 16, C.red); noGlow(); text('HOW THEY', 1380, 545, '900 48px M', '#fff'); text('COME FOR YOU', 1380, 600, '900 48px M', '#fff'); }, 0.35);
  });
};
S.b7 = (t, seg) => {
  // "I'm afraid of the dark." That night, the power goes out in his building. Only his building.
  const tn = wt(seg, 'night'), tp = wt(seg, 'power'), to = wt(seg, 'only');
  black();
  if (t < tn - 0.2) {
    cam(t, seg.start, tn - seg.start, 1.0, 1.06, 760, 560, () => { ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(560, 900, 1.3, { dir: 1 }); say(t, seg.start + 0.3, 760, 240, '"I\'M AFRAID OF THE DARK."', 640, 360, 50); agent('hr', 1500, 760, 0.9, { arms: 'desk', eyes: 1 }); meetDesk(1150, 1850, 760, { items: false }); });
    return;
  }
  const off = t >= tp + 0.1;
  cam(t, tn - 0.2, segEnd(seg) - tn + 1.4, 1.0, 1.14, 960, 560, () => {
    ln(-200, 940, W + 200, 940, 3, '#262626');
    const B = [[140, 520, 260], [440, 300, 300], [790, 420, 300], [1140, 260, 280], [1460, 480, 320]];
    B.forEach(([x, top, w], bi) => { const his = bi === 2, dark = his && off;
      rrS(x, top, w, 940 - top, 3, dark ? '#3a3a3a' : '#8a8a8a', 3);
      for (let r = 0; r < Math.floor((900 - top) / 70); r++) for (let c = 0; c < Math.floor((w - 30) / 60); c++) {
        const lit = hash(bi * 97 + r * 13 + c) > 0.35; if (!lit || dark) continue; rr(x + 24 + c * 60, top + 30 + r * 70, 34, 36, 2, C.fig); } });
    // in the dark building, a window with three pairs of red lenses
    if (off && t >= to) { ctx.save(); ctx.globalAlpha *= prog(t, to + 0.3, 0.5); redGlow(18); for (let k = 0; k < 3; k++) { rr(830 + k * 70, 650, 22, 10, 3, C.red); rr(856 + k * 70, 650, 22, 10, 3, C.red); } ctx.restore(); }
  });
  if (t >= to) flatT(() => pop(t, to, 960, 150, () => tag('ONLY HIS BUILDING', 960, 160, C.red, 56, 'center'), 0.3));
};
S.b8 = (t, seg) => {
  // the answer everyone gives
  const tw = wt(seg, 'work'), tp = wt(seg, "perfectionist");
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('THE ANSWER EVERYONE GIVES', 960, 280, '900 44px M', '#8a8a8a', 12), 0.4);
    okRow(t, tw - 0.4, 480, 470, '"I WORK TOO HARD."', 64);
    okRow(t, tp - 0.5, 480, 670, '"I\'M A PERFECTIONIST."', 64);
  });
};
S.b9 = (t, seg) => {
  // already in every file: a wall of identical files; then the red fades from his glasses
  const tl = wt(seg, 'learn'), tr = wt(seg, 'new') + 0.3;
  if (t < tr - 0.4) {
    black();
    cam(t, seg.start, tr - seg.start, 1.15, 1.0, 960, 540, () => {
      for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { const x = 230 + c * 292, y = 220 + r * 210, k = prog(t, seg.start + (r * 6 + c) * 0.04, 0.25);
        ctx.save(); ctx.globalAlpha *= k; rr(x - 120, y - 80, 240, 160, 8, '#ececec'); rr(x - 120, y - 100, 90, 26, 6, '#d8d8d8'); text('"I WORK', x, y - 10, '900 26px M', '#333'); text('TOO HARD."', x, y + 26, '900 26px M', '#333'); ctx.restore(); }
      if (t >= tl) pop(t, tl, 960, 540, () => { ctx.save(); glow(); rr(560, 470, 800, 140, 16, '#000'); rrS(560, 470, 800, 140, 16, C.fig, 4); noGlow(); text('NOTHING NEW', 960, 565, '900 70px M', C.fig); ctx.restore(); }, 0.3);
    });
    return;
  }
  focus(t, tr - 0.4, segEnd(seg) - tr, 2.6, 2.8, IX[1], HEADY + 10, () => room(t, { eyes: 1 - prog(t, tr + 0.1, 1.0), lid: 0 }));
};

// ---------- rule 3: never say you have no questions ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'NEVER SAY YOU HAVE NO QUESTIONS');
S.c1 = (t, seg) => {
  const tp = wt(seg, 'pens'), td = wt(seg, 'do');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 960, 470, () => room(t, { arms: t < tp ? 'board' : 'desk', me: true, lid: 0 }));
  say(t, td - 0.1, 960, 120, 'DO YOU HAVE ANY QUESTIONS FOR US?', 960, 240, 46);
};
S.c2 = (t, seg) => {
  // the interview only ends when you ask: the exit is locked until a question unlocks it
  const te = wt(seg, 'ends'), ta = wt(seg, 'ask');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1300, 520, () => room(t, { door: { lock: prog(t, seg.start + 0.4, 0.3) }, me: true, meX: 900, lid: 0 }));
  if (t >= ta) pop(t, ta, 1805, 700, () => { glow(); circ(1805, 690, 50, C.fig); noGlow(); text('?', 1805, 718, '900 76px M', '#000'); }, 0.3);
};
S.c3 = (t, seg) => {
  // "No, I think you covered everything." The clock goes back to nine.
  const tc = wt(seg, 'clock'), tn = wt(seg, 'nine');
  if (t < tc - 0.3) {
    cam(t, seg.start, 3, 1.0, 1.05, 960, 470, () => room(t, { me: true, lid: 0 }));
    say(t, seg.start + 0.2, 1400, 830, '"NO, I THINK YOU\nCOVERED EVERYTHING."', 1040, 760, 46);
    return;
  }
  const k = ease(prog(t, tc + 0.1, tn - tc + 0.1)), m = lerp(58, 0, k);
  focus(t, tc - 0.3, 4, 3.0, 3.3, ...CLOCK, () => meetRoom({ clock: [9, m, (t * 60) % 60 * (1 - k)], secRed: true, floor: false }));
  if (k >= 1) flatT(() => pop(t, tn, 960, 900, () => tag('9:00 AM', 960, 920, C.red, 60, 'center'), 0.3));
};
S.c4 = (t, seg) => {
  // the one on the left stands and holds out his hand again: it starts over
  const tg = wt(seg, 'again'), tt = wt(seg, 'thanks'), ts = wt(seg, 'starts');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.2, 760, 470, () => room(t, { arms: ['hand', 'desk', 'laptop'], standI: [prog(t, seg.start + 0.1, 0.6), 0, 0], reach: ease(prog(t, seg.start + 0.3, 0.8)), lid: 0, clock: [9, 0, 0], me: true, meX: 760 }));
  say(t, tt - 0.1, 760, 120, 'THANKS FOR COMING IN.', 620, 250, 46);
  if (t >= ts) flatT(() => pop(t, ts, 1500, 900, () => tag('AGAIN.', 1500, 920, C.red, 60, 'center'), 0.3));
};
S.c5 = (t, seg) => {
  // the loop: handshake, question, clock, around and around until you ask
  const th = wt(seg, 'handshake'), tq = wt(seg, 'question'), tu = wt(seg, 'until');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 540, () => {
    const R = 300, cx = 960, cy = 540, rot = t * 0.9;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot);
    for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.arc(0, 0, R, k * 2.09 + 0.25, k * 2.09 + 1.85); ctx.strokeStyle = '#5a5a5a'; ctx.lineWidth = 10; ctx.stroke();
      const a = k * 2.09 + 1.85; ctx.save(); ctx.rotate(a); ctx.translate(R, 0); pth('M-22,-10 L0,30 L22,-10 Z', '#5a5a5a'); ctx.restore(); }
    ctx.restore();
    const icons = [(x, y) => pageIcon('hand', x, y, '#fff'), (x, y) => icon7('ask', x, y, 0.6), (x, y) => icon7('clock', x, y, 0.6)], times = [th, tq, seg.start];
    for (let k = 0; k < 3; k++) { const a = rot + k * 2.09 - 1.57, x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R;
      ctx.save(); glow(); circ(x, y, 74, '#000'); noGlow(); circS(x, y, 74, k === 0 && t >= th && t < tq ? C.red : C.fig, 5); icons[k](x, y); ctx.restore(); }
    const loops = 1 + Math.floor((t - seg.start) * 1.6);
    text('LOOP', cx, cy - 20, '600 30px Plex', '#8a8a8a'); text(String(loops), cx, cy + 60, '900 90px M', C.fig);
    if (t >= tu) pop(t, tu, cx, cy + 420, () => tag('UNTIL YOU ASK', cx, cy + 440, C.red, 56, 'center'), 0.3);
  });
};
S.c6 = (t, seg) => {
  // one candidate said no forty times; for him it is still Monday, nine A.M.
  const tf = wt(seg, 'forty'), tm = wt(seg, 'monday');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.0, 1.0, 1.12, 760, 560, () => {
    ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(620, 900, 1.3, { dir: 1 });
    const n = Math.floor(lerp(1, 40, ease(prog(t, seg.start + 0.3, Math.max(0.5, tf - seg.start)))));
    pop(t, seg.start + 0.3, 330, 330, () => { listCard(170, 240, 330, 170); text('"NO."', 335, 300, '900 40px M', '#8a8a8a'); text('×' + n, 335, 380, '900 70px M', t >= tf ? C.red : C.fig); }, 0.3);
    if (t >= tm) pop(t, tm, 1320, 600, () => { glow(); rr(1180, 500, 280, 220, 12, '#ececec'); noGlow(); rr(1180, 500, 280, 64, 12, '#d61f1f'); text('MONDAY', 1320, 546, '900 34px M', '#fff'); text('9:00', 1320, 676, '900 86px M', '#111'); }, 0.3);
  });
};
S.c7 = (t, seg) => {
  const ts = wt(seg, 'salary'), tl = wt(seg, 'last');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.1, 1.18, 960, 470, () => room(t, { eyes: 1, lid: 0 }));
  listCard(380, 280, 1160, 440);
  noRow(t, ts - 0.4, ts + 0.3, 440, 400, 'money', 'THE SALARY', 52);
  noRow(t, tl - 0.4, tl + 0.4, 440, 590, 'ask', 'THE LAST PERSON IN THIS JOB', 46);
};
S.c8 = (t, seg) => {
  // the one question: when will I hear back? The lock opens.
  const tw = wt(seg, 'when');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1300, 520, () => room(t, { door: { lock: 1, open: prog(t, seg.end - 0.6, 0.4) }, me: true, meX: 900, lid: 0 }));
  say(t, tw - 0.1, 1340, 860, '"WHEN WILL I\nHEAR BACK?"', 1000, 780, 50);
  if (t >= seg.end - 0.6) flatT(() => { ctx.translate(1805, 420); check(0, 0, 40, prog(t, seg.end - 0.6, 0.3)); });
};
S.c9 = (t, seg) => {
  const ts = wt(seg, 'stand'), tw = wt(seg, "we'll");
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 470, () => room(t, { stand: prog(t, ts - 0.1, 0.8), arms: 'down', lid: 0 }));
  say(t, tw - 0.1, 960, 110, "WE'LL BE IN TOUCH.", 960, 210, 54);
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  // break even one rule, and they will be in touch, exactly as promised
  const tb = wt(seg, 'broke'), tt = wt(seg, 'touch'), te = wt(seg, 'exactly');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, W / 2, 520, () => {
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9], struck: [null, tb + 0.3, null, null], dim: prog(t, tt, 0.4) });
  });
  if (t >= tt) flatT(() => pop(t, tt, 960, 900, () => { ctx.save(); redGlow(24); rr(520, 830, 880, 130, 16, C.red); noGlow(); text("THEY'LL BE IN TOUCH", 960, 915, '900 60px M', '#fff'); ctx.restore(); }, 0.3));
};
S.d2 = (t, seg) => {
  // 3 AM. You wake up. Three of them at the foot of your bed, holding your file.
  const tw = wt(seg, 'wake'), ti = wt(seg, 'interviewers'), tf = wt(seg, 'foot');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 1100, 560, () => {
    const on = t >= ti - 0.1;
    night(t, { bed: t >= tw ? 'woke' : 'sleep', trio: on, eyes: prog(t, ti + 0.3, 0.3) });
    if (on && t < ti + 0.25) { ctx.save(); ctx.globalAlpha = 0.25 * (1 - prog(t, ti - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
  });
  if (t >= tf) flatT(() => pop(t, tf, 1420, 150, () => tag('3:00 AM', 1420, 160, C.red, 52, 'center'), 0.3));
};
S.d3 = (t, seg) => {
  cam(t, seg.start, segEnd(seg) - seg.start + 0.3, 1.3, 1.4, 1440, 500, () => night(t, {}));
  say(t, seg.start + 0.1, 1100, 190, 'WE HAVE A FEW\nMORE QUESTIONS.', 1420, 330, 40);
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // pretending to sleep: LACKS ENTHUSIASM
  const tl = wt(seg, 'lacks');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1000, 560, () => night(t, { bed: 'sleep' }));
  noHead(t, seg, 'sleep', 'PRETEND TO SLEEP', seg.start + 1.5);
  noteCard(t, tl - 0.1, 1300, 280, 'LACKS ENTHUSIASM', -0.05, '#d61f1f');
};
S.d6 = (t, seg) => {
  // screaming: STRONG COMMUNICATION SKILLS
  const tsc = wt(seg, 'screaming'), ts = wt(seg, 'strong');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1000, 560, () => {
    night(t, { sitUp: true });
    // sound lines from your head (no mouth)
    if (t >= tsc) { ctx.save(); ctx.globalAlpha *= 0.9; for (let k = 0; k < 3; k++) { const r = 60 + k * 40 + ((t * 120) % 40); ctx.beginPath(); ctx.arc(360 + 156 * 1.3, 900 - 410 * 1.3, r, -0.7, 0.7); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); } ctx.restore(); }
  });
  noHead(t, seg, 'sweat', 'SCREAM', seg.start + 1.0);
  noteCard(t, ts - 0.1, 1300, 280, 'STRONG COMMUNICATION SKILLS', -0.05, '#111');
};
S.d7 = (t, seg) => {
  // another job: they ask for the company's name, and they visit that company too
  const ta = wt(seg, 'ask'), tv = wt(seg, 'visit');
  if (t < tv - 0.3) {
    cam(t, seg.start, tv - seg.start, 1.0, 1.08, 1000, 560, () => night(t, { sitUp: true }));
    noHead(t, seg, 'offer', 'ANOTHER JOB', ta + 0.3);
    say(t, ta - 0.1, 1150, 200, "WHAT'S THE\nCOMPANY'S NAME?", 1420, 330, 40);
    return;
  }
  cam(t, tv - 0.3, segEnd(seg) - tv + 0.5, 1.0, 1.1, 960, 560, () => {
    black();
    rrS(620, 80, 680, 900, 4, '#8a8a8a', 4);
    for (let r = 0; r < 12; r++) for (let c = 0; c < 6; c++) { const lit = hash(r * 7 + c) > 0.45; if (lit) rr(660 + c * 104, 120 + r * 66, 76, 40, 3, '#cfcfcf'); }
    rr(840, 860, 240, 120, 4, '#000'); rrS(840, 860, 240, 120, 4, C.fig, 3); ln(-200, 980, W + 200, 980, 3, '#262626');
    trio(t, { xs: [900, 960, 1020], s: 0.18, y: 980, arms: 'down' });
  });
  noHead(t, seg, 'offer', 'ANOTHER JOB', ta + 0.3);
};
S.d8 = (t, seg) => {
  // only one thing works: remember what they are. Not monsters. Employees.
  const tr = wt(seg, 'remember'), tm = wt(seg, 'monsters'), te = wt(seg, 'employees');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    if (t < tr - 0.1) { pop(t, seg.start, 960, 520, () => { glow(); spaced('ONLY ONE THING WORKS', 960, 540, '900 70px M', C.fig, 6); noGlow(); }, 0.35); return; }
    agent('hr', 960, 1000, 0.95, { stand: 1, arms: 'down', eyes: 0 });
    if (t >= tm - 0.1) { pop(t, tm - 0.1, 420, 420, () => { text('MONSTER', 420, 440, '900 64px M', C.fig); }, 0.3); redX(420, 420, 110, prog(t, tm + 0.3, 0.3)); }
    if (t >= te - 0.1) { pop(t, te - 0.1, 1500, 420, () => { glow(); rr(1240, 360, 520, 120, 14, C.fig); noGlow(); text('EMPLOYEE', 1500, 440, '900 64px M', '#000'); }, 0.3);
      ctx.save(); ctx.globalAlpha *= prog(t, te, 0.3); ctx.translate(960, 1000 - 300 * 0.95); ctx.scale(0.95, 0.95); rr(30, -150, 72, 44, 5, C.fig); rrS(30, -150, 72, 44, 5, '#000', 3); text('STAFF', 66, -121, '900 17px M', '#000'); ctx.restore(); }
  });
};
S.d9 = (t, seg) => {
  // every employee is afraid of the same thing: one empty cardboard box under a light
  const ts = wt(seg, 'same');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.0, 1.15, 960, 600, () => {
    const g = ctx.createRadialGradient(960, 300, 20, 960, 700, 520); g.addColorStop(0, 'rgba(255,255,255,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ln(400, 860, 1520, 860, 3, '#262626');
    fadeIn(t, seg.start + 0.3, () => cardboardBox(960, 760, 1.6), 0.6);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= prog(t, ts, 0.4); redGlow(16); spaced('THE BOX', 960, 960, '900 54px M', C.red, 10); ctx.restore(); }
  });
};
S.d10 = (t, seg) => {
  // sit up, fold your hands, look the middle one in the eye: "Congratulations. You're hired."
  const te = wt(seg, 'middle'), tc = wt(seg, 'congratulations');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, t >= te ? 1.2 : 1.06, t >= te ? 1200 : 1000, 540, () => night(t, { sitUp: true }));
  if (t >= te && t < tc) flatT(() => brackets(1420, 900 - 0.78 * 640 + 60, 160, 160, prog(t, te, 0.3)));
  say(t, tc - 0.1, 760, 200, '"CONGRATULATIONS.\nYOU\'RE HIRED."', 620, 380, 50);
};
S.d11 = (t, seg) => {
  // they freeze. Whoever makes the offer is the boss. You just made the offer.
  const tf = wt(seg, 'freeze'), tb = wt(seg, 'boss'), tm = wt(seg, 'made');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.12, 1000, 540, () => {
    night(t, { sitUp: true, eyes: 1 - prog(t, tf, 0.3) });
    if (t >= tf) { ctx.save(); ctx.globalAlpha *= prog(t, tf, 0.25); for (let i = 0; i < 3; i++) { rr(TRIO[i] - 26, 220, 18, 60, 4, C.fig); rr(TRIO[i] + 8, 220, 18, 60, 4, C.fig); } ctx.restore(); }
  });
  flatT(() => {
    if (t >= tb - 0.1) slideIn(t, tb - 0.1, -40, 0, () => { listCard(70, 70, 700, 160); text('MAKES THE OFFER', 110, 136, '600 30px Plex', '#8a8a8a', 'left'); text('= THE BOSS', 110, 200, '900 54px M', C.fig, 'left'); }, 0.35);
    if (t >= tm) pop(t, tm, 590, 330, () => { glow(); rr(470, 290, 240, 70, 12, C.fig); noGlow(); text('YOU', 590, 342, '900 48px M', '#000'); }, 0.3);
  });
};
S.d12 = (t, seg) => {
  // their clipboards drop; they stand up straight; they are your employees now
  const td = wt(seg, 'drop'), ts = wt(seg, 'straight'), te = wt(seg, 'employees');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.1, 1100, 540, () => night(t, { sitUp: true, eyes: 0, arms: t >= td - 0.1 ? 'down' : 'board', drop: t >= td - 0.1 ? prog(t, td - 0.1, 0.6) : 0, badges: prog(t, te, 0.4) }));
  if (t >= te) flatT(() => pop(t, te, 1420, 150, () => tag('YOUR EMPLOYEES', 1420, 160, C.fig, 52, 'center'), 0.3));
};
S.d13 = (t, seg) => {
  // "Unfortunately... we're letting you go. Effective immediately."
  const tu = wt(seg, 'unfortunately'), te = wt(seg, 'effective');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.12, 1000, 540, () => night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, shake: t >= te ? [4, 4, 4] : [0, 0, 0] }));
  say(t, tu - 0.1, 760, 200, t < te - 0.1 ? '"UNFORTUNATELY...\nWE\'RE LETTING YOU GO."' : '"UNFORTUNATELY...\nWE\'RE LETTING YOU GO.\nEFFECTIVE IMMEDIATELY."', 620, 380, 44, { red: t >= te });
};
S.d14 = (t, seg) => {
  // three cardboard boxes appear in their hands: a stapler and a sad little plant in each
  const ta = wt(seg, 'appear'), ts = wt(seg, 'stapler');
  if (t < ts - 0.3) { cam(t, seg.start, ts - seg.start, 1.05, 1.15, 1300, 560, () => night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, boxes: prog(t, ta - 0.1, 0.4) })); return; }
  black();
  cam(t, ts - 0.3, segEnd(seg) - ts, 1.0, 1.1, 960, 560, () => {
    cardboardBox(960, 700, 2.2);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= prog(t, ts, 0.3); text('STAPLER', 600, 380, '900 40px M', C.fig); ln(620, 400, 760, 470, 3, '#8a8a8a'); ctx.restore(); }
    if (t >= wt(seg, 'sad')) { ctx.save(); ctx.globalAlpha *= prog(t, wt(seg, 'sad'), 0.3); text('SAD LITTLE PLANT', 1360, 300, '900 40px M', C.fig); ln(1300, 320, 1080, 400, 3, '#8a8a8a'); ctx.restore(); }
  });
};
S.d15 = (t, seg) => {
  // they walk out one by one; you never give them a reference
  const tw = wt(seg, 'walk'), tr = wt(seg, 'reference');
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.05, 1.0, 1100, 560, () => {
    const walk = [0, 1, 2].map(i => 420 * ease(prog(t, tw + i * 0.5, 1.6))), who = walk.map(w => w < 400);
    night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, boxes: 1, walk, who, doorOpen: prog(t, tw - 0.3, 0.4) });
  });
  if (t >= tr) flatT(() => stampMark(t, tr, 1300, 260, [['NO REFERENCE', 70]], -0.1, '#000', 20));
};

// ---------- the next morning ----------
S.f1 = (t, seg) => {
  const te = wt(seg, 'email'), tw = wt(seg, 'we');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    if (t < tw - 0.1) {
      pop(t, seg.start, 960, 250, () => { glow(); spaced('THE NEXT MORNING', 960, 270, '900 64px M', C.fig, 10); noGlow(); }, 0.35);
      if (t >= te - 0.1) pop(t, te - 0.1, 960, 560, () => { glow(); rr(560, 470, 800, 180, 24, '#f4f4f6'); noGlow(); icon7('mail', 680, 560, 0.6, '#111'); text('1 NEW EMAIL', 780, 580, '900 54px M', '#111', 'left'); ctx.save(); redGlow(14); circ(1320, 500, 18, C.red); ctx.restore(); }, 0.35);
      return;
    }
    ctx.translate(960, 480); ctx.scale(1.3, 1.3); ctx.translate(-960, -480);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Changes in our team', body: [typed('We are sorry to hear about', t, tw, 30), typed('the recent changes in our team.', t, tw + 0.9, 30)] });
  });
};
S.f2 = (t, seg) => {
  const tw = wt(seg, 'we');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.1, 960, 520, () => {
    ctx.translate(960, 480); ctx.scale(1.3, 1.3); ctx.translate(-960, -480);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Changes in our team', body: ['We are sorry to hear about', 'the recent changes in our team.', '', typed('We have restructured our', t, tw, 30), typed('hiring process.', t, tw + 0.9, 30)] });
  });
};
// the peephole: a round fisheye view of the hallway with three new agents, one holding out his hand
function peephole(t, z, o = {}) {
  black();
  ctx.save(); ctx.beginPath(); ctx.arc(960, 520, 400, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = '#0a0a0a'; ctx.fillRect(0, 0, W, H);
  ctx.translate(960, 520); ctx.scale(z, z); ctx.translate(-960, -520);
  ln(300, 860, 1620, 860, 3, '#3a3a3a'); ln(560, 120, 560, 860, 3, '#262626'); ln(1360, 120, 1360, 860, 3, '#262626');
  for (let i = 0; i < 3; i++) agent(KINDS[i], 760 + i * 200, 880, 0.62 + (i === 1 ? 0.06 : 0), { stand: 1, arms: i === 1 ? 'hand' : 'down', reach: 0.4, eyes: o.eyes && i === 1 ? o.eyes : 0, t });
  ctx.restore();
  const g = ctx.createRadialGradient(960, 520, 250, 960, 520, 400); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.85)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(960, 520, 401, 0, Math.PI * 2); ctx.fill();
  circS(960, 520, 404, C.fig, 8);
}
S.f3 = (t, seg) => {
  // the doorbell; through the peephole, three new interviewers; one is already holding out his hand
  const tp = wt(seg, 'peephole'), tb = wt(seg, 'doorbell');
  if (t < tp - 0.2) { black(); cam(t, seg.start, tp - seg.start, 1.0, 1.06, 960, 520, () => { rrS(760, 160, 400, 760, 6, C.fig, 6); circ(1110, 560, 12, C.fig); circS(960, 360, 22, C.fig, 5);
    if (t >= tb) for (let k = 0; k < 3; k++) { ctx.save(); ctx.globalAlpha *= 1 - prog(t, tb + k * 0.15, 0.8); circS(960, 360, 40 + 60 * prog(t, tb + k * 0.15, 0.8), C.fig, 4); ctx.restore(); }
    text('DING DONG', 960, 1000, '900 40px M', '#8a8a8a'); }); return; }
  peephole(t, lerp(1.0, 1.15, ease(prog(t, tp, 3))));
};
S.f4 = (t, seg) => {
  peephole(t, lerp(1.15, 1.5, ease(prog(t, seg.start, 2.0))), { eyes: prog(t, seg.start + 0.4, 0.5) });
  say(t, seg.start + 0.1, 1560, 230, 'WELCOME TO THE\nSECOND ROUND.', 1180, 380, 46, { red: true });
};
S.f5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.f6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
