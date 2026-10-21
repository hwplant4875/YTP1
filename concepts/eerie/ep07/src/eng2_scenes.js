// ---------- EP07 scenes: "If Your Interviewer Ever Asks 'What Is Your Greatest Weakness?'" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const CLOCK = [1640, 260], AC = [220, 285];
const segDur = seg => nextStart(seg) - seg.start;
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
// ---------- the interview room ----------
// interviewers sit at x = 560 / 960 / 1360 behind the desk; their feet at FEET (hidden), desk top at DESK_Y
const IX = [560, 960, 1360], FEET = 905, DESK_Y = 620;
const HEAD = i => [IX[i], FEET - 300 - 276];
// o.arms: one mode or an array of three; o.eyes (middle, 0..1); o.lean, o.tilt (middle); o.me: your back in the foreground; o.stand 0..1; o.who [bools]
function room(t, o = {}) {
  roomWall({ floor: 900, clock: o.clock, ac: o.ac, secRed: o.secRed, door: o.door });
  // a soft overhead light on the desk
  const g = ctx.createRadialGradient(960, 260, 40, 960, 520, 900); g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
  if (o.door) roomDoor(t, o.door);
  const st = ease(o.stand || 0);
  for (let i = 0; i < 3; i++) {
    if (o.who && !o.who[i]) { if (o.chairs) officeChair(IX[i], 905, 0.82); continue; }
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'board');
    suit(IX[i], FEET - st * 110, 1, { arms, wt: t + i * 1.7, eyes: i === 1 ? (o.eyes ?? 1) : 0, lean: i === 1 ? o.lean : 0, tilt: i === 1 ? o.tilt : 0,
      shake: o.shake ? o.shake[i] : 0, t, lines: o.lines, under: o.under, up: o.up });
  }
  desk(260, 1660, DESK_Y, { n: 3 });
  if (o.me) meBack(o.meX ?? 960, 1330, 1.3);
}
// a door in the right wall: o = { lock: 0..1 red padlock, open: 0..1 }
function roomDoor(t, d) {
  rr(1700, 360, 170, 540, 4, '#0d0d0f'); rrS(1700, 360, 170, 540, 4, '#55555c', 4); circ(1720, 640, 8, '#9a9aa0');
  spaced('EXIT', 1785, 330, '900 30px M', '#6a6a72', 8);
  if (d.lock > 0) { ctx.save(); ctx.globalAlpha *= d.lock; const red = d.open ? 1 - d.open : 1;
    ctx.translate(1785, 620); ctx.beginPath(); ctx.arc(0, -30 - 30 * (d.open || 0), 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = red > 0.5 ? C.red : C.fig; ctx.stroke();
    red > 0.5 ? redGlow(20) : glow(); rr(-40, -30, 80, 66, 10, red > 0.5 ? C.red : C.fig); noGlow(); circ(0, 0, 8, '#000'); ctx.restore(); }
}
// a "does not work" header at the top left with a red X on the icon at tx
function noHead(t, seg, ic, label, tx) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start, -40, 0, () => { const w = 190 + label.length * 31; ctx.save(); ctx.globalAlpha *= 0.88; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    icon7(ic, 125, 125, 0.5); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35);
  ctx.restore();
}
const TRIO = [1310, 1530, 1750];
function trio(t, o = {}) {   // the three standing in the dark (rule 4)
  const xs = o.xs || TRIO, ss = o.ss || [0.8, 0.8, 0.8];
  for (let i = 0; i < 3; i++) { if (o.who && !o.who[i]) continue;
    if (o.fold && o.fold[i] > 0.97) continue;
    suit(xs[i], o.y ?? 900, ss[i], { arms: o.arms || 'board', eyes: i === 1 ? (o.eyes ?? 1) : 0, wt: t + i, shake: o.shake ? o.shake[i] : 0, t, fold: o.fold ? o.fold[i] : 0, lines: o.lines, under: o.under, up: o.up }); }
}
// the night bedroom with you in bed and them at the foot of it
function night(t, o = {}) {
  bedroomNight({ gapGlow: o.gapGlow, time: o.time });
  bed(360, 900, 1.3, o.bed || 'woke', { look: 1 });
  if (o.trio !== false) trio(t, o);
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the panel, the question already asked; the middle one's eyes are red
  const td = wt(seg, 'do');
  cam(t, 0, seg.end + 0.6, 1.0, 1.1, 960, 420, () => room(t, { me: true, arms: ['board', 'desk', 'board'] }));
  if (t < td - 0.1) say(t, -1, 960, 130, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 250, 50);
  else pop(t, td - 0.1, 960, 140, () => tag('DO NOT TELL THE TRUTH', 960, 150, C.red, 56, 'center'), 0.3);
};
function teaserBox(t, seg, w0, ic, word, y, x = 1600) {
  const tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon7(ic, x, y, 1.0); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  const ws = [[seg.start, wt(seg, 'never', 1), 'self', 'tell'], [wt(seg, 'never', 1), wt(seg, 'and'), 'ask', 'questions'], [wt(seg, 'and'), nextStart(seg), 'clock', 'back']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {   // the clipboard: LIVES ALONE, underlined
      black(); cam(t, w0, blk - w0, 1.0, 1.2, 800, 520, () => clipboard(800, 540, 3.6, -0.05, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 0]], under: 2, up: prog(t, w0 + 0.6, 1.0) }));
    } else if (i === 1) {   // the clock runs back to nine
      black(); const k = ease(prog(t, w0 + 0.3, hit - w0 - 0.3)), m = lerp(47, -60 * 0, k);
      focus(t, w0, blk - w0, 2.6, 3.0, ...CLOCK, () => roomWall({ clock: [9, lerp(47, 0, k), 30 * (1 - k)], secRed: true, floor: 2000 }));
    } else {   // 3 AM: three of them at the foot of your bed
      cam(t, w0, blk - w0, 1.0, 1.15, 1100, 600, () => night(t, { eyes: prog(t, hit - 0.3, 0.3) }));
    }
    if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, 250, i === 2 ? 300 : 1600); ctx.restore();
};

// ---------- rule 1: do not tell them about yourself ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT TELL THEM ABOUT YOURSELF');
S.a1 = (t, seg) => {
  // "Tell me about yourself." They have already read your résumé. Three times. Every page.
  const ta = wt(seg, 'already'), t3 = wt(seg, 'three'), te = wt(seg, 'every');
  if (t < ta - 0.1) {
    cam(t, seg.start, ta - seg.start, 1.25, 1.35, 700, 400, () => room(t, { arms: ['board', 'desk', 'desk'], eyes: 0.6 }));
    say(t, seg.start, 1080, 250, 'TELL ME ABOUT\nYOURSELF.', 660, 330, 54);
    return;
  }
  black();
  cam(t, ta, seg.end - ta + 0.7, 1.0, 1.08, 960, 480, () => {
    const n = t >= te ? 4 : 1, fk = ease(prog(t, te, 0.5));
    for (let i = n - 1; i >= 0; i--) resume(960 + (i - 1.5) * 150 * fk + (n === 1 ? 0 : 0), 520 + i * 6 * fk, 0.95, (i - 1.5) * 0.06 * fk, { marks: prog(t, ta + 0.2 + i * 0.1, 0.9) });
    for (let k = 0; k < 3; k++) if (t >= t3 + k * 0.22) pop(t, t3 + k * 0.22, 1500 + k * 46, 180, () => { ctx.save(); redGlow(16); ln(1500 + k * 46, 130, 1500 + k * 46, 230, 12, C.red); ctx.restore(); }, 0.2);
    if (t >= t3) pop(t, t3, 1300, 180, () => tag('READ', 1300, 196, C.fig, 40, 'right'), 0.25);
  });
};
S.a2 = (t, seg) => {
  // three versions of you on the chart; only one may leave the room
  const tc = wt(seg, 'checking'), ts = wt(seg, 'safe'), tr = wt(seg, 'room');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    black();
    for (let i = 0; i <= 8; i++) { const y = 860 - i * 70; ln(260, y, 1660, y, 2, '#2a2a2e'); if (i % 2 === 0) text(`${150 + i * 10}`, 240, y + 8, '600 22px Plex', '#55555c', 'right'); }
    const V = [['A', { face: 'front', arms: [0.15, 0.15] }], ['B', { face: 'front', arms: [0, 0] }], ['C', { face: 'left', arms: [0, 0.9] }]];
    V.forEach(([lab, oo], i) => { const x = 560 + i * 400;
      slideIn(t, seg.start + 0.2 + i * 0.25, 0, 40, () => { me(x, 860, 1.45, oo); rr(x - 50, 880, 100, 56, 8, '#1a1a1d'); text(lab, x, 924, '900 40px M', C.fig); }, 0.4); });
    if (t >= tc) { const k = prog(t, tc, 0.4); brackets(960, 600, 300, 620, k); }
    if (t >= ts) { redX(560, 520, 90, prog(t, ts, 0.3)); redX(1360, 520, 90, prog(t, ts + 0.15, 0.3)); }
    if (t >= tr) pop(t, tr, 960, 150, () => { glow(); rr(810, 100, 300, 90, 14, C.fig); noGlow(); spaced('SAFE', 960, 165, '900 54px M', '#000', 10); }, 0.3);
  });
};
S.a3 = (t, seg) => {
  // the script: smile, your name, one sentence, stop
  const W4 = [wt(seg, 'smile'), wt(seg, 'name'), wt(seg, 'sentence'), wt(seg, 'stop')];
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    black(); sitSide(520, 900, 1.35, { dir: 1 });
    ['SMILE.', 'SAY YOUR NAME.', 'ONE SENTENCE.', 'THEN STOP.'].forEach((l, i) => okRow(t, W4[i] - 0.15, 900, 230 + i * 170, l, 56));
  });
};
S.a4 = (t, seg) => {
  const th = wt(seg, 'hobbies'), tf = wt(seg, 'family'), tl = wt(seg, 'live');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: 'write', eyes: 0.8 }));
  listCard(420, 210, 1080, 600);
  noRow(t, th - 0.25, th + 0.25, 480, 330, 'game', 'YOUR HOBBIES', 52);
  noRow(t, tf - 0.25, tf + 0.25, 480, 510, 'family', 'YOUR FAMILY', 52);
  noRow(t, tl - 0.25, tl + 0.25, 480, 690, 'pin', 'WHERE YOU LIVE', 52);
};
S.a5 = (t, seg) => {
  // the last candidate: "I live alone." He writes it down.
  const tw = wt(seg, 'wrote');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    roomWall({ floor: 900, clockAt: [960, 150], acAt: [-600, 0] });
    sitSide(470, 900, 1.25, { dir: 1, hair: true });
    say(t, seg.start + 0.3, 520, 210, 'I LIVE ALONE.', 500, 330, 50);
    suit(1380, 905, 1.0, { arms: t >= tw - 0.2 ? 'write' : 'board', wt: t, eyes: 0 });
    desk(1080, 1680, DESK_Y, { n: 1 });
  });
};
S.a6 = (t, seg) => {
  // then he underlined it
  const tu = wt(seg, 'underlined'), up = prog(t, tu - 0.05, 0.7);
  black();
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.0, 1.25, 900, 520, () => {
    clipboard(900, 560, 4.4, -0.04, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', up > 0.9 ? 1 : 0]], under: 2, up });
    ctx.save(); ctx.translate(900, 560); ctx.rotate(-0.04); ctx.scale(4.4, 4.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width;
    pen(-62 + (w + 4) * up, -24 + 2 * 28, 0.6, 2.0); ctx.restore();
  });
};

// ---------- rule 2: do not tell the truth ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT TELL THE TRUTH');
S.b1 = (t, seg) => {
  const tl = wt(seg, 'leans'), tw = wt(seg, 'what'), lean = ease(prog(t, tl, 1.2));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.55, 960, 380, () => room(t, { arms: ['board', 'desk', 'board'], lean, eyes: lerp(0.5, 1, lean) }));
  say(t, tw - 0.1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 230, 46);
};
S.b2 = (t, seg) => {
  // quiet: the air conditioner stops, the clock stops
  const tc = wt(seg, 'conditioner'), tk = wt(seg, 'clock');
  if (t < tc - 0.4) { cam(t, seg.start, 3, 1.0, 1.04, 960, 520, () => room(t, { arms: 'desk', me: true })); return; }
  if (t < tk - 0.2) { focus(t, tc - 0.4, 3, 2.6, 2.8, ...AC, () => roomWall({ ac: 1 - prog(t, tc + 0.2, 0.8), floor: 2000 })); return; }
  const sec = 40 + (t < tk + 0.4 ? (t - tk) * 0 : 0) + (Math.sin(t * 40) * 0.25 * (t > tk + 0.2 ? 1 : 0));
  focus(t, tk - 0.2, 3, 3.0, 3.3, ...CLOCK, () => roomWall({ clock: [9, 13, sec], secRed: t > tk + 0.2, floor: 2000 }));
};
S.b3 = (t, seg) => {
  const tw = wt(seg, 'work'), tc = wt(seg, 'care');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('ALLOWED ANSWERS', 960, 280, '900 44px M', C.mid, 14), 0.4);
    lnP(560, 320, 1360, 320, 4, C.mid, prog(t, seg.start + 0.2, 0.5));
    okRow(t, tw - 0.3, 480, 470, '"I WORK TOO HARD."', 64);
    okRow(t, tc - 0.3, 480, 670, '"I CARE TOO MUCH."', 64);
  });
};
S.b4 = (t, seg) => {
  const tp = wt(seg, 'procrastination'), ts = wt(seg, 'public'), tn = wt(seg, 'nervous');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: ['board', 'desk', 'board'], eyes: 1 }));
  listCard(420, 210, 1080, 600);
  noRow(t, tp - 0.25, tp + 0.35, 480, 330, 'clock', 'PROCRASTINATION', 52);
  noRow(t, ts - 0.25, ts + 0.35, 480, 510, 'stage', 'PUBLIC SPEAKING', 52);
  noRow(t, tn - 0.25, tn + 0.35, 480, 690, 'sweat', 'I GET NERVOUS', 52);
};
function folder(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 22);
  rr(-260, -200, 200, 50, 10, '#cfcfd4'); rr(-260, -170, 520, 360, 12, '#e4e4e8'); noGlow(); rrS(-260, -170, 520, 360, 12, '#000', 3);
  text('CANDIDATE: YOU', -220, -100, '900 36px M', '#111', 'left'); ln(-220, -80, 220, -80, 3, '#9a9aa0');
  for (let i = 0; i < 3; i++) rr(-220, -40 + i * 40, i === 2 ? 220 : 360, 14, 4, '#b9b9bf');
  ctx.restore();
}
S.b5 = (t, seg) => {
  // whatever you say becomes your weakness. Forever. It goes in your file, and the file follows you.
  const tf = wt(seg, 'forever'), tfi = wt(seg, 'file'), tfo = wt(seg, 'follows');
  black();
  if (t < tfo - 0.15) {
    cam(t, seg.start, tfo - seg.start, 1.0, 1.12, 960, 540, () => {
      folder(960, 560, 1.4);
      if (t >= tfi) stampMark(t, tfi, 1040, 680, [['WEAKNESS', 70], ['PERMANENT', 34]], -0.12, '#e4e4e8', 40);
    });
    if (t >= tf && t < tfi) pop(t, tf, 960, 150, () => tag('FOREVER', 960, 160, C.red, 60, 'center'), 0.3);
    return;
  }
  // you walk away down the street; the file floats after you
  const k = (t - tfo) / 3.2, x = lerp(700, 1300, k);
  cam(t, tfo, 3.5, 1.0, 1.05, 960, 540, () => {
    ln(-200, 860, W + 200, 860, 3, '#2a2a2e');
    for (let i = 0; i < 6; i++) { const lx = ((i * 380 - (t - tfo) * 120) % 2300 + 2300) % 2300 - 200; rr(lx, 300, 12, 560, 4, '#1c1c20'); circ(lx + 6, 300, 14, '#2a2a2e'); }
    me(x, 860, 1.25, { face: 'right', walk: t * 7 });
    folder(x - 380, 470 + Math.sin(t * 3) * 14, 0.42);
    ctx.save(); ctx.setLineDash([12, 12]); ln(x - 260, 480, x - 40, 470, 3, '#55555c'); ctx.restore();
  });
};
S.b6 = (t, seg) => {
  const ts = wt(seg, 'said');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 760, 560, () => {
    roomWall({ floor: 900, clockAt: [1500, 200], acAt: [-600, 0] });
    sitSide(620, 900, 1.3, { dir: 1 });
    say(t, ts + 0.1, 760, 240, '"I CAN\'T SAY NO."', 680, 340, 56);
    suit(1420, 905, 1.0, { arms: 'write', wt: t, eyes: 1 }); desk(1120, 1720, DESK_Y, { n: 1 });
  });
};
S.b7 = (t, seg) => {
  // the office at night through the glass: he is still there. Nine years. He never went home.
  const tn = wt(seg, 'nine'), th = wt(seg, 'home');
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.2, 1000, 520, () => {
    ctx.fillStyle = '#040406'; ctx.fillRect(-200, -200, W + 400, H + 400);
    // the glass wall: frames and reflections
    for (let i = 0; i < 4; i++) { rrS(200 + i * 400, 120, 400, 760, 0, '#2a2a30', 6); ctx.save(); ctx.globalAlpha = 0.06; pth(`M${260 + i * 400},120 L${330 + i * 400},120 L${230 + i * 400},880 L${200 + i * 400},880 Z`, '#fff'); ctx.restore(); }
    // his desk + monitor glow
    const g = ctx.createRadialGradient(1080, 520, 20, 1080, 560, 520); g.addColorStop(0, 'rgba(220,235,255,0.22)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    rr(840, 640, 520, 16, 4, '#d6d6da'); rr(860, 656, 16, 220, 3, '#55555c'); rr(1320, 656, 16, 220, 3, '#55555c');
    glow('rgba(220,235,255,0.9)', 30); rr(1150, 450, 200, 130, 8, '#e8f0ff'); noGlow(); rr(1240, 580, 20, 60, 3, '#55555c');
    for (let i = 0; i < 4; i++) rr(1170, 474 + i * 24, typed('████████████', t, seg.start + i * 0.6, 8).length * 12, 10, 2, '#7a8aa0');
    sitSide(960, 880, 1.05, { dir: 1, eye: t >= th - 0.2 ? false : true });
    if (t >= th - 0.2) { ctx.save(); const hx = 960 - 4 * 1.05, hy = 880 - 420 * 1.05; redGlow(18); circ(hx - 10, hy - 4, 6, C.red); circ(hx + 12, hy - 4, 6, C.red); ctx.restore(); }   // he turns to you
    // the wall calendar
    if (t >= tn) pop(t, tn, 560, 330, () => { rr(440, 220, 240, 250, 12, '#e6e6e6'); rr(440, 220, 240, 64, 12, '#d61f1f'); text('YEAR', 560, 266, '900 36px M', '#fff'); text('9', 560, 430, '900 140px M', '#111'); }, 0.3);
  });
};

// ---------- rule 3: do not say you have no questions ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT SAY YOU HAVE NO QUESTIONS');
S.c1 = (t, seg) => {
  const tp = wt(seg, 'pens'), td = wt(seg, 'do');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.1, 960, 420, () => room(t, { arms: t < tp ? 'write' : 'desk', me: true }));
  say(t, td - 0.1, 960, 130, 'DO YOU HAVE ANY QUESTIONS FOR US?', 960, 250, 46);
};
S.c2 = (t, seg) => {
  // never say no: the door stays locked until you ask something
  const tn = wt(seg, 'never'), ta = wt(seg, 'ask');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1300, 520, () => room(t, { arms: 'desk', door: { lock: prog(t, seg.start + 0.6, 0.3) }, me: true, meX: 900 }));
  if (t >= tn) { say(t, tn - 0.05, 1230, 800, '"NO."', 990, 730, 70); redX(1230, 800, 70, prog(t, tn + 0.3, 0.3)); }
  if (t >= ta) pop(t, ta, 1785, 720, () => { glow(); circ(1785, 760, 50, C.fig); noGlow(); text('?', 1785, 788, '900 76px M', '#000'); }, 0.3);
};
S.c3 = (t, seg) => {
  // "No, I think you covered everything." The clock on the wall goes back to nine.
  const tc = wt(seg, 'clock'), tn = wt(seg, 'nine');
  if (t < tc - 0.2) {
    cam(t, seg.start, 3, 1.0, 1.05, 960, 520, () => room(t, { arms: 'desk', me: true }));
    say(t, seg.start + 0.2, 1420, 790, '"NO, I THINK YOU\nCOVERED EVERYTHING."', 1040, 730, 46);
    return;
  }
  const k = ease(prog(t, tc + 0.1, tn - tc + 0.1)), m = lerp(58, 0, k) - (k < 1 ? 0 : 0), h = 9 + m / 60 * (k < 1 ? 1 : 0);
  focus(t, tc - 0.2, 4, 3.0, 3.3, ...CLOCK, () => roomWall({ clock: [9, m, (t * 60) % 60 * (1 - k)], secRed: true, floor: 2000 }));
  if (k >= 1) pop(t, tn, 960, 860, () => tag('9:00 AM', 960, 880, C.red, 60, 'center'), 0.3);
};
S.c4 = (t, seg) => {
  // the middle one tilts his head: then let's start again
  const tt = wt(seg, 'tilts'), tl = wt(seg, 'then'), tilt = -0.28 * ease(prog(t, tt, 1.2));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.4, 1.75, 960, 380, () => room(t, { arms: ['board', 'desk', 'board'], tilt, eyes: 1, clock: [9, 0, 0] }));
  say(t, tl - 0.1, 960, 110, "THEN LET'S START AGAIN.", 1000, 200, 44);
  if (t >= wt(seg, 'tell')) say(t, wt(seg, 'tell') - 0.1, 960, 880, 'TELL ME ABOUT YOURSELF.', 960, 760, 44, { red: true });
};
S.c5 = (t, seg) => {
  // he said no three times. He is still in there. Monday, 9:00. His beard reaches the floor.
  const ts = wt(seg, 'still'), tm = wt(seg, 'monday'), g = ease(prog(t, ts - 0.2, 3.5));
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.0, 1.18, 760, 560, () => {
    roomWall({ floor: 900, clock: [9, 0, 0], clockAt: [1500, 200], acAt: [-600, 0], secRed: true });
    sitSide(620, 900, 1.3, { dir: 1 });
    // cobwebs between him and the chair; the day counter keeps going, the clock does not
    if (g > 0) { ctx.save(); ctx.globalAlpha *= g * 0.8; const cx0 = 620 - 50 * 1.3, cy0 = 900 - 380 * 1.3;
      for (let k = 0; k < 6; k++) { const a = k / 5 * Math.PI / 2; ln(cx0, cy0, cx0 + Math.cos(a) * 150, cy0 + Math.sin(a) * 150, 2, '#d6d6da'); }
      for (let r = 1; r <= 4; r++) { ctx.beginPath(); for (let k = 0; k < 6; k++) { const a = k / 5 * Math.PI / 2, rr2 = r * 34 + (k % 2) * 4; k ? ctx.lineTo(cx0 + Math.cos(a) * rr2, cy0 + Math.sin(a) * rr2) : ctx.moveTo(cx0 + Math.cos(a) * rr2, cy0 + Math.sin(a) * rr2); } ctx.strokeStyle = '#d6d6da'; ctx.lineWidth = 2; ctx.stroke(); }
      const fx = 620 + 140 * 1.3, fy = 900; for (let k = 0; k < 5; k++) { const a = Math.PI + k / 4 * Math.PI / 2; ln(fx, fy, fx + Math.cos(a) * 90, fy + Math.sin(a) * 90, 2, '#d6d6da'); }
      ctx.restore();
      const days = Math.floor(lerp(1, 4019, ease(g))); pop(t, ts - 0.2, 1320, 330, () => { listCard(1110, 250, 420, 150); text('DAYS IN THIS ROOM', 1320, 300, '600 24px Plex', '#8a8a92'); text(days.toLocaleString('en-US'), 1320, 370, '900 60px M', C.fig); }, 0.3); }
    // three NOs
    for (let k = 0; k < 3; k++) pop(t, seg.start + 0.4 + k * 0.3, 380 + k * 0, 300 + k * 110, () => { tag('NO.', 300, 320 + k * 110, C.fig, 54, 'center'); }, 0.25);
    // the desk calendar: MONDAY
    if (t >= tm) pop(t, tm, 1320, 640, () => { rr(1180, 560, 280, 200, 12, '#e6e6e6'); rr(1180, 560, 280, 60, 12, '#d61f1f'); text('MONDAY', 1320, 604, '900 34px M', '#fff'); text('9:00', 1320, 720, '900 80px M', '#111'); }, 0.3);
    if (t >= tm) rr(1120, 760, 400, 16, 4, '#d6d6da');
  });
};
S.c6 = (t, seg) => {
  const ts = wt(seg, 'salary'), tl = wt(seg, 'last');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: 'desk', eyes: 1 }));
  listCard(380, 280, 1160, 440);
  noRow(t, ts - 0.4, ts + 0.3, 440, 400, 'money', 'THE SALARY', 52);
  noRow(t, tl - 0.4, tl + 0.4, 440, 590, 'ask', 'THE LAST PERSON IN THIS ROLE', 46);
};
S.c7 = (t, seg) => {
  // the one question: when will I hear back? The lock opens.
  const tw = wt(seg, 'when');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 1300, 520, () => room(t, { arms: 'desk', door: { lock: 1, open: prog(t, seg.end - 0.6, 0.4) }, me: true, meX: 900 }));
  say(t, tw - 0.1, 1330, 800, '"WHEN WILL I\nHEAR BACK?"', 990, 730, 50);
  if (t >= seg.end - 0.6) { ctx.save(); ctx.translate(1330, 640); check(0, 0, 40, prog(t, seg.end - 0.6, 0.3)); ctx.restore(); }
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const ts = wt(seg, 'stand'), tw = wt(seg, "we'll");
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 420, () => room(t, { arms: 'board', stand: prog(t, ts - 0.1, 0.8) }));
  say(t, tw - 0.1, 960, 110, "WE'LL GET BACK TO YOU.", 960, 200, 50);
};
S.d2 = (t, seg) => {
  // 3 AM. You wake up. Three of them at the foot of your bed.
  const tw = wt(seg, 'wake'), ti = wt(seg, 'interviewers'), tf = wt(seg, 'foot');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.1, 1100, 560, () => {
    const on = t >= ti - 0.1;
    night(t, { bed: t >= tw ? 'woke' : 'sleep', trio: on, eyes: prog(t, ti + 0.3, 0.3), arms: 'board' });
    if (on && t < ti + 0.25) { ctx.save(); ctx.globalAlpha = 0.25 * (1 - prog(t, ti - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
  });
  if (t >= tf) pop(t, tf, 1530, 160, () => tag('3:00 AM', 1530, 170, C.red, 52, 'center'), 0.3);
};
S.d3 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.3, 1.4, 1820, 470, () => night(t, { arms: ['write', 'board', 'write'] }));
  say(t, seg.start + 0.1, 1150, 170, 'WE HAVE A FEW\nMORE QUESTIONS.', 1480, 300, 34);
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // pretending to sleep: LACKS ENTHUSIASM
  const tw = wt(seg, 'write'), tl = wt(seg, 'lacks');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1000, 560, () => night(t, { bed: 'sleep', arms: t >= tw - 0.3 ? ['board', 'write', 'board'] : 'board' }));
  noHead(t, seg, 'sleep', 'PRETEND TO SLEEP', seg.start + 1.6);
  if (t >= tl - 0.1) pop(t, tl - 0.1, 1300, 300, () => { ctx.save(); ctx.translate(1300, 300); ctx.rotate(-0.05); glow(); rr(-260, -50, 520, 100, 10, '#fbfbfb'); noGlow(); text('LACKS ENTHUSIASM', 0, 16, '900 44px M', '#d61f1f'); ctx.restore(); }, 0.3);
};
S.d6 = (t, seg) => {
  // another offer: they ask for the name, and they go there too
  const ta = wt(seg, 'ask'), tv = wt(seg, 'visit');
  if (t < tv - 0.3) {
    cam(t, seg.start, tv - seg.start, 1.0, 1.08, 1000, 560, () => night(t, {}));
    noHead(t, seg, 'offer', 'ANOTHER OFFER', ta + 0.3);
    say(t, ta - 0.1, 1230, 190, "WHAT'S THE\nCOMPANY'S NAME?", 1500, 320, 40);
    return;
  }
  cam(t, tv - 0.3, 3.5, 1.0, 1.1, 960, 560, () => {
    black();
    // the other company's tower at night; one floor goes dark window by window
    rr(620, 80, 680, 900, 4, '#0d0d10'); rrS(620, 80, 680, 900, 4, '#3a3a40', 4);
    for (let r = 0; r < 12; r++) for (let c = 0; c < 6; c++) { const lit = hash(r * 7 + c) > 0.45; rr(660 + c * 104, 120 + r * 66, 76, 40, 3, lit ? '#8a8a92' : '#1a1a1e'); }
    rr(840, 860, 240, 120, 4, '#2a2a30'); ln(-200, 980, W + 200, 980, 3, '#2a2a2e');
    trio(t, { xs: [880, 960, 1040], ss: [0.3, 0.3, 0.3], y: 980, arms: 'board' });
  });
  noHead(t, seg, 'offer', 'ANOTHER OFFER', ta + 0.3);
};
S.d7 = (t, seg) => {
  // blocking their email: the next one comes from inside your house
  const tn = wt(seg, 'next'), ti = wt(seg, 'inside');
  black();
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.1, 960, 560, () => {
    if (t < tn - 0.1) {
      mailCard(560, 260, 800, 520, { from: 'INTERVIEWS', subj: 'A few more questions', body: ['We noticed you have not replied.', 'We will try again.'] });
      if (t >= seg.start + 1.0) stampMark(t, seg.start + 1.0, 1140, 640, [['BLOCKED', 64]], -0.1, '#f4f4f6', 20);
    } else {
      mailCard(560, 260, 800, 520, { dot: true, from: 'YOUR LIVING ROOM', fromRed: true, subj: 'We are in the hallway.', body: ['Please come out.', 'We have a few more questions.'] });
    }
  });
  noHead(t, seg, 'mail', 'BLOCK THEIR EMAIL', seg.start + 1.2);
};
S.d8 = (t, seg) => {
  // the only thing that works: interview them. The clipboard is yours now.
  const ti = wt(seg, 'interview');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    if (t >= ti - 0.1) {
      pop(t, ti - 0.1, 960, 270, () => { glow(); spaced('INTERVIEW THEM.', 960, 300, '900 104px M', C.fig, 4); noGlow(); }, 0.35);
      slideIn(t, ti + 0.2, 0, 60, () => { me(960, 960, 1.35, { face: 'front' }); clipboard(960, 640, 1.1, 0.05); }, 0.4);
    } else pop(t, seg.start, 960, 520, () => { ctx.save(); glow(); spaced('ONLY ONE THING WORKS', 960, 540, '900 70px M', C.fig, 6); ctx.restore(); }, 0.35);
  });
};
S.d9 = (t, seg) => {
  // sit up, fold your hands, look the middle one in the eye
  const ts = wt(seg, 'so'), te = wt(seg, 'eye');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, t >= te ? 1.3 : 1.1, t >= te ? 1450 : 1000, 520, () => night(t, { bed: 'woke', arms: 'board' }));
  if (t >= te) brackets(1530, 900 - 0.8 * 576, 150, 170, prog(t, te, 0.3), C.fig);
  say(t, ts - 0.1, 760, 200, '"SO. WHAT IS YOUR\nGREATEST WEAKNESS?"', 600, 470, 44);
};
S.d10 = (t, seg) => {
  // the rules of that room apply to them too: they cannot lie
  const tl = wt(seg, 'lie');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.25, 1530, 520, () => night(t, { arms: 'down' }));
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start + 0.2, 0, -40, () => { rr(470, 70, 600, 150, 12, '#ececec'); rr(490, 103, 84, 84, 10, '#111'); text('2', 532, 169, '900 62px M', '#fff'); pageIcon('truth', 630, 145, '#111');
    text('DO NOT TELL', 700, 136, '900 40px M', '#111', 'left'); text('THE TRUTH', 700, 178, '900 40px M', '#111', 'left'); }, 0.4);
  if (t >= tl - 0.1) pop(t, tl - 0.1, 770, 300, () => { ctx.save(); redGlow(20); text('THEY CANNOT LIE', 770, 320, '900 58px M', C.red); ctx.restore(); }, 0.3);
  ctx.restore();
};
const SHRINK = (t, t0) => lerp(0.8, 0.5, ease(prog(t, t0, 0.9)));
S.d11 = (t, seg) => {
  const tb = wt(seg, 'being'), ts = wt(seg, 'smaller');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.22, 1460, 540, () => night(t, { arms: ['down', 'board', 'board'], ss: [SHRINK(t, ts - 0.2), 0.8, 0.8], shake: [t > tb ? 3 : 0, 0, 0] }));
  say(t, tb - 0.15, 1080, 200, '"BEING ASKED\nQUESTIONS."', 1300, 330, 44);
};
S.d12 = (t, seg) => {
  const tt = wt(seg, 'tell'), tsh = wt(seg, 'shake'), ts = wt(seg, 'smaller');
  const d11 = window.TL.segments.find(s => s.id === 'd11'), s0 = SHRINK(t, wt(d11, 'smaller') - 0.2);
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.22, 1460, 540, () => night(t, { arms: ['down', 'down', 'board'], ss: [s0, SHRINK(t, ts - 0.2), 0.8], shake: [0, t > tsh ? 6 : 0, 0] }));
  say(t, tt - 0.1, 700, 200, '"TELL ME ABOUT\nYOURSELF."', 560, 450, 46);
};
S.d13 = (t, seg) => {
  const th = wt(seg, 'why');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.12, 1.22, 1700, 560, () => night(t, { arms: ['down', 'down', 'down'], ss: [0.5, 0.5, 0.8], shake: [5, 5, t > th + 0.6 ? 8 : 0], eyes: 0.6 + 0.4 * Math.abs(Math.sin(t * 9)) }));
  say(t, th - 0.1, 700, 200, '"WHY SHOULD\nI HIRE YOU?"', 560, 450, 56);
};
S.d14 = (t, seg) => {
  // they fold up like paper and slide out under your door
  const tf = wt(seg, 'fold'), tsl = wt(seg, 'slide');
  const f = prog(t, tf - 0.1, 1.1), sl = ease(prog(t, tsl - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.08, 1500, 600, () => {
    night(t, { trio: false, gapGlow: sl > 0 ? 0.6 : 0 });
    const xs = TRIO, ss = [0.5, 0.5, 0.8];
    if (f < 0.97) {
      const k = clamp((f - 0.2) / 0.6);
      ctx.save(); ctx.globalAlpha *= 1 - k; trio(t, { xs, ss, arms: 'down', fold: [f * 0.6, f * 0.6, f * 0.6], shake: [2, 2, 2] }); ctx.restore();
      // each one becomes a sheet of paper, folding in half and in half again down to the floor
      for (let i = 0; i < 3; i++) { const h = lerp(560 * ss[i], 10, ease(f)), w = lerp(200 * ss[i], 170 * ss[i], f), x = xs[i];
        ctx.save(); ctx.globalAlpha *= k; glow(); rr(x - w / 2, 900 - h, w, h, 3, '#fbfbfb'); noGlow();
        if (h > 30) { ln(x - w / 2, 900 - h / 2, x + w / 2, 900 - h / 2, 2, '#9a9aa0'); ln(x - w / 2, 900 - h * 0.75, x + w / 2, 900 - h * 0.75, 1.5, '#c4c4c8'); for (let j = 0; j < 5; j++) ln(x - w / 2 + 16, 900 - h + 20 + j * h / 7, x + w / 2 - 16 - (j % 2) * 30, 900 - h + 20 + j * h / 7, 3, '#d6d6da'); }
        ctx.restore(); }
    }
    else for (let i = 0; i < 3; i++) {   // three sheets on the floor, sliding to the gap under the door
      const x = lerp(xs[i], 1700 + i * 40, sl), w = 170 * ss[i];
      ctx.save(); ctx.globalAlpha *= 1 - clamp((sl - 0.6) / 0.4); glow(); rr(x - w / 2, 890, w, 10, 2, C.fig); noGlow(); ctx.restore();
    }
    // the door is drawn again over the sheets so they disappear under it
    if (f >= 0.97) rr(1640, 380, 200, 510, 4, '#0e0e10');
    if (f >= 0.97) rrS(1640, 380, 200, 510, 4, '#3a3a40', 4); circ(1660, 650, 8, '#55555c');
  });
};

// ---------- one week later ----------
S.f1 = (t, seg) => {
  const te = wt(seg, 'email');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    pop(t, seg.start, 960, 250, () => { ctx.save(); glow(); spaced('ONE WEEK LATER', 960, 270, '900 64px M', C.fig, 10); ctx.restore(); }, 0.35);
    if (t >= te - 0.1) pop(t, te - 0.1, 960, 560, () => { glow(); rr(560, 470, 800, 180, 24, '#f4f4f6'); noGlow(); icon7('mail', 680, 560, 0.6, '#111'); text('1 NEW EMAIL', 780, 580, '900 54px M', '#111', 'left'); ctx.save(); redGlow(14); circ(1320, 500, 18, C.red); ctx.restore(); }, 0.35);
  });
};
S.f2 = (t, seg) => {
  const tw = wt(seg, 'we'), tp = wt(seg, 'would');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    const b1 = typed('We regret to inform you that our', t, tw, 30), b2 = typed('interviewers have resigned.', t, tw + 1.1, 30), b3 = typed('Would you like the position?', t, tp - 0.1, 30);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Your application', body: [b1, b2, '', b3] });
  });
};
S.f3 = (t, seg) => {
  // job title: interviewer. Location: the chair.
  const tj = wt(seg, 'job'), tl = wt(seg, 'location'), tc = wt(seg, 'chair');
  cam(t, seg.start, seg.end - seg.start + 1.2, 1.0, 1.25, 960, 480, () => {
    room(t, { who: [false, false, false], chairs: true });
    if (t >= tc) { ctx.save(); redGlow(40); ctx.globalAlpha = prog(t, tc, 0.4); rrS(960 - 110 * 0.82, 905 - 560 * 0.82, 220 * 0.82, 280 * 0.82, 30, C.red, 6); ctx.restore(); }
  });
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (t >= tj - 0.1) slideIn(t, tj - 0.1, -50, 0, () => { listCard(70, 70, 760, 230); text('JOB TITLE', 110, 140, '600 26px Plex', '#8a8a92', 'left'); text('INTERVIEWER', 110, 210, '900 62px M', C.fig, 'left');
    if (t >= tl - 0.1) { text('LOCATION', 110, 256, '600 26px Plex', '#8a8a92', 'left'); text('THE CHAIR', 280, 262, '900 40px M', C.red, 'left'); } }, 0.35);
  ctx.restore();
};
S.f4 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.f5 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
