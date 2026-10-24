// ---------- EP09: the dog, you, and the house ----------
// Channel identity: analog horror. PURE BLACK background, PURE WHITE flat figures with thin black detail lines. Red only for danger.
// The dog is a plain white retriever. You are faceless (a plain round head, no mouth). Only the dog has a mouth: its smile is the horror.
const DOG = { fig: '#f4f4f4', far: '#c4c4c4', ear: '#dcdcdc', line: '#000', tooth: '#fbfbf6' };
const FL = 860;   // the floor line in most rooms
const rotP = (px, py, cx, cy, a) => { const c = Math.cos(a), s = Math.sin(a); return [cx + (px - cx) * c - (py - cy) * s, cy + (px - cx) * s + (py - cy) * c]; };
const inv = (wx, wy, x, y, s, dir) => [(wx - x) / (s * dir), (wy - y) / s];
// a two-part limb (thigh/shin, upper arm/forearm) with a soft joint bent to side b
function limb2(a, c, w, col, b = 1, bend = 0.12) {
  const mx = (a[0] + c[0]) / 2, my = (a[1] + c[1]) / 2, dx = c[0] - a[0], dy = c[1] - a[1];
  poly([a, [mx - dy * bend * b, my + dx * bend * b], c], w, col);
}


// the dog in profile, facing right (o.dir -1: left). Paws on the floor at (x,y). About 400 long and 330 tall at s=1.
// o.rear 0..1: the front of the body rises around the hips (1 = up on its back legs, taller than you)
// o.sit 0..1: sitting; o.walk: gait phase; o.wag: tail phase; o.crouch 0..1: front low (growling)
// o.reach: [x,y] world point for the near front paw (o.reachK 0..1 blends it in); o.scratch 0..1: hind leg scratches behind the ear
function dog(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, F = DOG.fig, FA = DOG.far, L = DOG.line;
  const rear = ease(o.rear || 0), sit = ease(o.sit || 0), cr = o.crouch || 0;
  const sw = o.walk != null ? Math.sin(o.walk) : 0, sw2 = o.walk != null ? Math.sin(o.walk + Math.PI) : 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const hip = [-100, -178 + 70 * sit + 10 * cr];
  const a = -rear * 1.36 - sit * 0.5 * (1 - rear) + cr * 0.16;   // body angle around the hip
  const R = (p) => rotP(p[0], p[1] + (hip[1] + 178), hip[0], hip[1], a);   // a body point (drawn at stand height) into place
  const shoulder = R([92, -170]), neck = R([128, -205]);
  let headC = R([180, -262 + 30 * cr]);
  if (rear > 0) headC = [headC[0] + 30 * rear, headC[1] + 10 * rear];
  // front paws: on the floor, or hanging in front of the chest when it stands up
  const floorP = (off) => [lerp(102 + off, 120, sit), -12];
  const hang = [shoulder[0] + 60, shoulder[1] + 110];
  let pn = [lerp(floorP(sw * 28)[0], hang[0], rear), lerp(-12, hang[1], rear)];
  let pf = [lerp(floorP(-14 + sw2 * 28)[0], hang[0] - 26, rear), lerp(-12, hang[1] + 8, rear)];
  if (o.reach) { const r = inv(o.reach[0], o.reach[1], x, y, s, dir), k = o.reachK ?? 1; pn = [lerp(pn[0], r[0], k), lerp(pn[1], r[1], k)]; }
  // hind legs: standing, folded under (sitting), or straight under the hips (up)
  const hindN = sit > 0.5 ? null : [lerp(-112 + sw2 * 26, -96, rear), -12], hindF = [lerp(-86 + sw * 26, -76, rear), -12];
  glow('rgba(255,255,255,0.22)', 16);
  // far legs
  limb2(hip, hindF, 28, FA, -1, 0.18); ell(hindF[0] + 10, -10, 20, 11, 0, FA);
  limb2(R([70, -165]), pf, 26, FA, 1, 0.06 + 0.1 * rear); ell(pf[0] + 10, pf[1] + 2, 19, 11, 0, FA);
  // tail
  const wag = o.wag != null ? Math.sin(o.wag) * 0.5 : 0, tb = R([-128, -192]);
  ctx.save(); ctx.translate(tb[0], tb[1]); ctx.rotate(-0.5 + wag - rear * 0.9 * (1 - sit) + sit * 1.4);
  pth('M0,-12 C-40,-22 -80,-34 -112,-40 C-118,-30 -110,-20 -100,-18 C-70,-10 -36,6 0,12 Z', F); ctx.restore();
  // body
  ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(a); ctx.translate(-hip[0], -hip[1]);
  ell(0, hip[1] - (-178) - 180, 142, 64, 0, F);
  ctx.restore();
  // near hind leg: a haunch when sitting
  if (sit > 0.5) { ell(hip[0] + 20, -64, 74, 62, -0.2, F); ell(-10, -12, 34, 13, 0, F); pthS(`M${hip[0] - 30},-40 C${hip[0]},-10 ${hip[0] + 60},-10 ${hip[0] + 80},-50`, 'rgba(0,0,0,0.35)', 3); }
  else if (o.scratch) { const sc = Math.sin((o.t || 0) * 30) * 0.5 + 0.5, ear = [headC[0] - 30, headC[1] + 10];
    limb2(hip, [lerp(hip[0] + 60, ear[0] - 20, 0.7), lerp(-80, ear[1] + 40 + sc * 26, 0.8)], 30, F, 1, 0.3); }
  else { limb2(hip, hindN, 30, F, -1, 0.18); ell(hindN[0] + 10, -10, 22, 12, 0, F); }
  // neck and chest
  poly([shoulder, neck, [headC[0] - 30, headC[1] + 20]], 70, F);
  // near front leg
  limb2(R([96, -160]), pn, 28, F, 1, 0.06 + 0.12 * rear); ell(pn[0] + 10, pn[1] + 2, 21, 12, 0, F);
  noGlow();
  // collar
  ctx.save(); ctx.translate(...[(neck[0] + headC[0]) / 2 - 18, (neck[1] + headC[1]) / 2 + 22]); ctx.rotate(0.9 - rear * 0.4); rr(-30, -6, 60, 12, 5, '#1a1a1a'); circ(0, 12, 7, o.tagRed ? C.red : '#9a9a9a'); ctx.restore();
  // head
  ctx.save(); ctx.translate(...headC); ctx.rotate((o.head || 0) - a * 0.1 + cr * 0.15); dogHead(o); ctx.restore();
  ctx.restore();
}


// you, faceless, in profile facing right (o.dir -1: left). Feet (or knees, hands) on the floor at (x,y). 360 tall standing at s=1.
// o.pose: 'stand' | 'sit' (chair seat at y-170) | 'fours' | 'curl' (asleep on your side) | 'back' (pinned on your back) | 'kneel'
// o.hand: [x,y] world target for the near hand; o.walk: gait phase; o.red: a red halo (danger); o.head: tilt
function you(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, col = o.col || C.fig, far = '#b8b8b8', P = o.pose || 'stand';
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const H = o.hand ? inv(o.hand[0], o.hand[1], x, y, s, dir) : null;
  const arm = (sh, hd, c, w = 20) => { limb2(sh, hd, w, c, 1, 0.1); circ(hd[0], hd[1], w * 0.6, c); };
  const head = (hx, hy, r = 36) => { if (o.red) { ctx.save(); redGlow(30 * o.red); circ(hx, hy, r, col); ctx.restore(); circS(hx, hy, r + 3, C.red, 4 * o.red); } else circ(hx, hy, r, col); };
  glow('rgba(255,255,255,0.25)', 14);
  if (P === 'stand') {
    const sw = o.walk != null ? Math.sin(o.walk) : 0;
    arm([0, -282], [10 - sw * 26, -160], far); ln(-2, -172, -6 + sw * 22, -10, 26, far); rr(-8 + sw * 22 - 6, -18, 34, 16, 6, far);
    ln(2, -172, 6 - sw * 22, -10, 26, col); rr(6 - sw * 22 - 6, -18, 36, 16, 6, col);
    rr(-30, -302, 60, 150, 24, col); head(4, -344);
    arm([0, -282], H || [14 + sw * 26, -160], col);
  } else if (P === 'sit') {
    arm([4, -282], [80, -210], far); poly([[-6, -184], [92, -180], [98, -14]], 28, far);
    poly([[6, -180], [100, -176], [106, -14]], 30, col); rr(96, -20, 40, 16, 6, col);
    rr(-34, -306, 64, 136, 24, col); head(2, -348);
    arm([4, -282], H || [90, -214], col);
  } else if (P === 'fours') {
    const sh = [72, -196], hp = [-112, -184];
    arm(sh, [58, -8], far, 22); limb2(hp, [-90, -18], 30, far, -1, 0.05); ln(-90, -16, -196, -12, 24, far);
    poly([hp, sh], 66, col); limb2([hp[0] + 10, hp[1]], [-104, -18], 32, col, -1, 0.05); ln(-104, -16, -214, -12, 26, col);
    head(140 + (o.lunge || 0) * 20, -214 + (o.head || 0));
    arm([sh[0] + 6, sh[1]], H || [96, -8], col, 22);
  } else if (P === 'curl') {
    poly([[-96, -44], [20, -18], [-60, -12]], 28, far);
    ell(-6, -54, 112, 44, 0.04, col); head(126, -70, 34); poly([[-90, -48], [30, -26], [-40, -14]], 30, col);
    arm([70, -78], [140, -24], col, 20);
  } else if (P === 'back') {
    ln(40, -44, 210, -24, 28, far); ln(40, -40, 200, -14, 30, col);
    poly([[-150, -46], [40, -44]], 66, col); head(-204, -50);
    arm([-110, -60], H || [-60, -150], col, 20);
  } else if (P === 'kneel') {
    ln(-40, -14, -150, -12, 26, far); ln(-30, -14, -140, -12, 28, col);
    poly([[-36, -18], [-24, -156]], 32, col);
    rr(-48, -300, 64, 150, 24, col); head(-12, -342);
    arm([-14, -280], H || [70, -190], col);
  }
  noGlow(); ctx.restore();
}
// a red outline of a person, curled up inside the dog's body (what moved in)
function insideMe(x, y, s, a = 1, dir = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s); ctx.globalAlpha *= a; redGlow(16); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(70, -30, 26, 0, Math.PI * 2); ctx.stroke();
  ctx.stroke(new Path2D('M44,-24 C10,-40 -50,-40 -80,-10 C-96,8 -80,30 -50,26 L-10,22 C10,20 20,30 30,40 M-30,22 C-10,36 30,30 50,8'));
  noGlow(); ctx.restore();
}

// ---------- rooms and props (white outlines on black) ----------
function floorLine(y = FL, col = '#262626') { ln(-200, y, W + 200, y, 3, col); }
function hallDoor(x, open = 0, o = {}) {   // the front door: outline, opens to a light doorway
  const w = 220, h = 470, y = FL - h;
  if (open > 0) { ctx.save(); glow('rgba(255,255,255,0.6)', 30); rr(x, y, w * open, h, 2, '#e9e9e9'); ctx.restore(); }
  rrS(x, y, w, h, 4, C.fig, 5);
  ctx.save(); ctx.translate(x, 0); ctx.scale(1 - open * 0.85, 1); rr(4, y + 4, w - 8, h - 8, 2, '#000'); rrS(4, y + 4, w - 8, h - 8, 2, '#9a9a9a', 3); circ(w - 30, y + 250, 8, C.fig); ctx.restore();
}
function mirrorFrame(x, y, w, h, o = {}) {   // a tall wall mirror: white frame, black glass; o.inner(fn) draws the reflection clipped inside
  glow('rgba(255,255,255,0.3)', 20); rrS(x, y, w, h, 14, C.fig, 14); noGlow();
  rr(x + 7, y + 7, w - 14, h - 14, 8, '#050505');
  if (o.inner) { ctx.save(); ctx.beginPath(); ctx.roundRect(x + 7, y + 7, w - 14, h - 14, 8); ctx.clip(); o.inner(); ctx.restore(); }
  ctx.save(); ctx.globalAlpha *= 0.12; ln(x + 40, y + 60, x + 110, y + 10, 8, '#fff'); ln(x + 40, y + 120, x + 170, y + 10, 4, '#fff'); ctx.restore();
}
function table(x0, x1, y = 600, o = {}) {   // dining table, side view: top slab on two legs
  glow('rgba(255,255,255,0.3)', 18); rr(x0, y, x1 - x0, 20, 4, C.fig); noGlow();
  for (const lx of [x0 + 40, x1 - 54]) rr(lx, y + 20, 14, FL - y - 20, 2, '#d0d0d0');
}
function chair(x, s = 1, dir = 1, o = {}) {   // side view chair, seat at FL-170; the back on the far side from dir
  ctx.save(); ctx.translate(x, FL); ctx.scale(s * dir, s);
  const c = o.col || '#8c8c8c';
  rr(-70, -176, 140, 14, 4, c); rr(-74, -420, 14, 258, 5, c); ln(-62, -162, -66, 0, 9, c); ln(60, -162, 64, 0, 9, c);
  ctx.restore();
}
function plate(x, y, s = 1, o = {}) {   // a plate seen from the side, food optional; o.fork
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ell(0, -6, 80, 12, 0, C.fig); ell(0, -10, 56, 6, 0, '#cfcfcf');
  if (o.food) { pth('M-34,-12 C-30,-36 30,-36 34,-12 Z', '#bdbdbd'); }
  if (o.fork) { ln(100, -4, 170, -4, 6, C.fig); for (let i = 0; i < 3; i++) ln(170, -8 + i * 4, 196, -8 + i * 4, 3, C.fig); }
  ctx.restore();
}
function bowl(x, s = 1, o = {}) {   // the dog's bowl on the floor; o.full
  ctx.save(); ctx.translate(x, FL); ctx.scale(s, s);
  if (o.full) pth('M-64,-48 C-56,-82 56,-82 64,-48 Z', '#cfcfcf');
  glow('rgba(255,255,255,0.3)', 14); pth('M-84,-50 L84,-50 L66,-2 L-66,-2 Z', C.fig); noGlow(); ln(-84, -50, 84, -50, 4, '#000');
  if (o.label) text(o.label, 0, -16, '900 26px M', '#000');
  ctx.restore();
}
function dogBed(x, s = 1) { ctx.save(); ctx.translate(x, FL); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 14); ell(0, -30, 230, 40, 0, C.fig); noGlow(); ell(0, -40, 196, 24, 0, '#0c0c0c'); ctx.restore(); }
// a fork held in a hand (close-up), at (x,y) pointing right
function forkHand(x, y, s = 1, rot = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  glow('rgba(255,255,255,0.3)', 14); poly([[-420, 60], [-120, 10]], 90, C.fig); noGlow();
  rr(-130, -40, 90, 90, 36, C.fig); ln(-40, 0, 160, 0, 12, C.fig); for (let i = 0; i < 4; i++) ln(160, -21 + i * 14, 230, -21 + i * 14, 7, C.fig);
  if (o.food) ell(210, 0, 34, 24, 0, '#bdbdbd');
  ctx.restore();
}
// dental chart: a row of flat human teeth seen front on, centred at (x,y); o.fangAt: index of the one long sharp tooth; o.label
function teethRow(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const n = 10, w = 76;
  glow('rgba(255,43,43,0.4)', 14); rr(-n * w / 2 - 30, -70, n * w + 60, 54, 26, C.red); noGlow();
  for (let i = 0; i < n; i++) {
    const tx = -n * w / 2 + i * w + 4, c = 1 - Math.abs(i - 4.5) / 6, h = 70 + 50 * c;
    if (o.fangAt === i) { ctx.save(); const k = o.fang ?? 1; redGlow(24 * k); ctx.beginPath(); ctx.moveTo(tx, -30); ctx.lineTo(tx + w - 8, -30); ctx.lineTo(tx + (w - 8) / 2 + 6, -30 + lerp(h, 220, k)); ctx.closePath(); ctx.fillStyle = DOG.tooth; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#000'; ctx.stroke(); ctx.restore(); }
    else { rr(tx, -30, w - 8, h, [3, 3, 18, 18], DOG.tooth); rrS(tx, -30, w - 8, h, [3, 3, 18, 18], '#000', 3); }
  }
  ctx.restore();
}
function nightstand(x, s = 1) { ctx.save(); ctx.translate(x, FL); ctx.scale(s, s); rr(-110, -200, 220, 200, 6, '#141414'); rrS(-110, -200, 220, 200, 6, '#4a4a4a', 3); ln(-100, -110, 100, -110, 3, '#4a4a4a'); circ(0, -150, 7, '#6a6a6a'); ctx.restore(); }
// the collar lying flat with its tag; o.red 0..1 (the name on the tag)
function collar(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.ellipse(0, 0, 220, 70, 0, 0, Math.PI * 2); ctx.lineWidth = 34; ctx.strokeStyle = '#222'; ctx.stroke(); ctx.lineWidth = 3; ctx.strokeStyle = '#7a7a7a'; ctx.stroke();
  rr(-30, 52, 60, 36, 6, '#9a9a9a'); rr(-14, 60, 28, 20, 3, '#222');
  ln(0, 86, 0, 120, 6, '#9a9a9a');
  const red = o.red || 0; ctx.save(); if (red > 0) redGlow(30 * red); circ(0, 200, 88, red > 0.5 ? C.red : C.fig); ctx.restore();
  circS(0, 200, 74, red > 0.5 ? '#fff' : '#000', 3); circ(0, 126, 10, '#000');
  text(o.name || 'YOU', 0, 222, '900 64px M', red > 0.5 ? '#fff' : '#000');
  ctx.restore();
}
// swap arrows: two curved arrows trading places between a and b
function swapArrows(ax, bx, y, p = 1, col = C.red, r = 120) {
  if (p <= 0) return;
  const mx = (ax + bx) / 2, rx = Math.abs(bx - ax) / 2;
  ctx.save(); redGlow(14);
  for (const d of [-1, 1]) {
    const a0 = d < 0 ? Math.PI : 0, a1 = a0 + d * Math.PI * clamp(p);
    ctx.beginPath(); ctx.ellipse(mx, y, rx, r, 0, d < 0 ? Math.PI * 1.08 : 0.08, d < 0 ? Math.PI * 1.08 + Math.PI * 0.84 * clamp(p) : 0.08 + Math.PI * 0.84 * clamp(p));
    ctx.lineWidth = 12; ctx.strokeStyle = col; ctx.stroke();
    if (p > 0.95) { const a = d < 0 ? Math.PI * 1.92 : Math.PI * 0.92, ex = mx + Math.cos(a) * rx, ey = y + Math.sin(a) * r, ang = a + Math.PI / 2;
      ctx.save(); ctx.translate(ex, ey); ctx.rotate(ang); pth('M0,-26 L34,0 L0,26 Z', col); ctx.restore(); }
  }
  ctx.restore();
}
// sound arcs coming off a head at (x,y) toward dir; col; n rings, a breathing pulse
function growlArcs(x, y, t, dir = 1, col = C.fig, size = 1, a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; if (col === C.red) redGlow(16);
  for (let k = 0; k < 3; k++) { const r = (50 + k * 36 + ((t * 90) % 36)) * size; ctx.beginPath(); ctx.arc(x, y, r, dir > 0 ? -0.6 : Math.PI - 0.6, dir > 0 ? 0.6 : Math.PI + 0.6); ctx.strokeStyle = col; ctx.lineWidth = 7 * size; ctx.stroke(); }
  noGlow(); ctx.restore();
}
// a progress bar with a label; v 0..1
function meter(x, y, w, label, v, col = C.red) {
  text(label, x, y - 18, '900 36px M', C.fig, 'left');
  rrS(x, y, w, 44, 8, '#5a5a5a', 4); ctx.save(); if (col === C.red) redGlow(18); rr(x + 6, y + 6, (w - 12) * clamp(v), 32, 5, col); ctx.restore();
  text(Math.round(v * 100) + '%', x + w + 24, y + 36, '900 40px M', col, 'left');
}
// an old phone handset (the vet call)
function phoneIcon(x, y, s = 1, col = C.fig) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  pth('M-110,-30 C-110,-70 -60,-80 -40,-60 L-20,-30 C-14,-20 -20,-8 -34,-4 L-50,0 C-40,40 -10,70 30,84 L40,66 C46,54 60,50 70,58 L100,80 C120,96 110,140 70,140 C-20,140 -110,60 -110,-30 Z', col); noGlow(); ctx.restore(); }
function bellButton(x, y, s = 1, ring = 0) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); rr(-40, -60, 80, 120, 14, '#1a1a1a'); rrS(-40, -60, 80, 120, 14, C.fig, 4); ctx.save(); if (ring > 0) redGlow(30 * ring); circ(0, 0, 22, ring > 0 ? C.red : C.fig); ctx.restore(); ctx.restore(); }
