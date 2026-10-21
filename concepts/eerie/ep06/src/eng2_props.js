// ---------- EP06 props: Halloween night, the man in the white mask ----------
// Flat 2D pictograms. Everything dark and white; warm amber only for lamps and pumpkin light; red only for danger.
const NIGHT = { sky0: '#06080c', sky1: '#000', house: '#111214', houseHi: '#26272b', roof: '#0b0b0d', street: '#0c0c0e', walk: '#151517', grass: '#090b09',
  amber: '#ffc36b', jump: '#2a323f', jumpHi: '#4a5568', jumpLo: '#1b212b', mask: '#eef0ed', maskSh: '#b7bbbb', hair: '#2b2119', hairHi: '#4b3b2c' };
const amberGlow = (b = 24) => glow('rgba(255,180,90,0.85)', b);

// ---------- the man ----------
// front view, feet at (x,y), 600 units tall at s=1. o.tilt (rad, head), o.knife: 0 none, 1 low at his side, 2 raised; o.wave 0..1 (left hand up);
// o.walk: step phase (rad) or null; o.back: seen from behind; o.red 0..1 (eyes); o.dark 0..1 (body sinks into the dark, only the mask stays);
// o.lower 0..1 (raised knife comes down); o.handsEmpty: show both open hands
function myers(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const dk = o.dark || 0, body = o.bodyCol || NIGHT.jump, edge = `rgba(150,158,170,${0.55 * (1 - dk)})`;
  const sw = o.walk != null ? Math.sin(o.walk) : 0;
  ctx.save(); ctx.globalAlpha *= 1 - 0.75 * dk;
  // legs
  for (const d of [-1, 1]) {
    const lift = o.walk != null ? Math.max(0, d * sw) * 18 : 0, fx = d * 34 + (o.walk != null ? d * sw * 10 : 0);
    ctx.beginPath(); ctx.moveTo(d * 8, -300); ctx.lineTo(d * 62, -300); ctx.lineTo(fx + d * 24, -22 - lift); ctx.lineTo(fx - d * 22, -22 - lift); ctx.closePath();
    ctx.fillStyle = body; ctx.fill(); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke();
    ln(d * 36 - 14, -150, d * 36 + 12, -144, 2, NIGHT.jumpLo); ln(d * 36 - 10, -136, d * 36 + 8, -132, 2, NIGHT.jumpLo);   // creases at the knee
    rr(fx - 30, -30 - lift, 60, 30, 10, '#121315');                                       // boots
  }
  // torso: work coveralls, wide shoulders
  const torso = new Path2D('M-78,-500 C-90,-470 -84,-380 -66,-290 L66,-290 C84,-380 90,-470 78,-500 C40,-512 -40,-512 -78,-500 Z');
  ctx.fillStyle = body; ctx.fill(torso); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke(torso);
  if (!o.back) {
    ln(0, -470, 0, -300, 3, '#59627a'); rr(-4, -462, 8, 16, 2, '#7a8296');                                   // zip and its pull
    for (const d of [-1, 1]) {
      pth(`M${d * 4},-506 L${d * 46},-508 L${d * 40},-476 L${d * 2},-462 Z`, NIGHT.jumpHi);              // pointed collar
      pthS(`M${d * 4},-506 L${d * 46},-508 L${d * 40},-476 L${d * 2},-462`, NIGHT.jumpLo, 2);
      rr(d > 0 ? 18 : -60, -446, 42, 44, 4, NIGHT.jumpLo); rr(d > 0 ? 16 : -62, -450, 46, 14, 3, '#151a22');   // chest pockets with flaps
      ln(d * 60, -340, d * 30, -330, 2, NIGHT.jumpLo);                                                  // a fold at the hip
    }
  }
  else ln(0, -505, 0, -300, 2, NIGHT.jumpLo);
  rr(-68, -304, 136, 10, 3, NIGHT.jumpLo); for (let i = -5; i <= 5; i++) ln(i * 12, -306, i * 12, -296, 1.5, '#151a22');   // elastic waist
  // arms: shoulder -> elbow -> hand; returns the knife hand position
  const arm = (d, hand, elbow) => { ctx.beginPath(); ctx.moveTo(d * 70, -492); ctx.lineTo(elbow[0], elbow[1]); ctx.lineTo(hand[0], hand[1]);
    ctx.lineWidth = 38; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = body; ctx.stroke();
    ctx.lineWidth = 3; ctx.strokeStyle = edge; ctx.stroke(); circ(hand[0], hand[1], 19, '#cfcdc4'); };
  // his right hand (screen left)
  let kh = null, kAng = Math.PI / 2;
  const raise = o.knife === 2 ? 1 - (o.lower || 0) : 0;
  if (o.knife) {
    const hx = lerp(-96, -60, raise), hy = lerp(-270, -640, raise), ex = lerp(-100, -132, raise), ey = lerp(-385, -520, raise);
    kh = [hx, hy]; kAng = lerp(Math.PI / 2, -Math.PI / 2 - 0.1, raise);
    arm(-1, kh, [ex, ey]);
  } else arm(-1, [-96 + (o.walk != null ? -sw * 14 : 0), -268], [-102, -385]);
  // left hand (screen right): down, or waving
  const wv = o.wave || 0;
  if (wv > 0) { const wob = Math.sin((o.waveT || 0) * 7) * 0.5 * clamp(wv * 2 - 1);
    const hx = lerp(96, 120 + wob * 40, wv), hy = lerp(-268, -600, wv); arm(1, [hx, hy], [lerp(102, 150, wv), lerp(-385, -470, wv)]);
    if (wv > 0.6) for (let i = 0; i < 4; i++) { const a = -2.2 + i * 0.32 + wob * 0.3; ln(hx + Math.cos(a) * 12, hy + Math.sin(a) * 12, hx + Math.cos(a) * 42, hy + Math.sin(a) * 42, 9, '#cfcdc4'); } }
  else arm(1, [96 + (o.walk != null ? sw * 14 : 0), -268], [102, -385]);
  ctx.restore();
  // the knife: dark handle, long pale blade with a glint
  if (kh) knife(kh[0], kh[1], kAng, 1, { red: o.knifeRed });
  // head
  ctx.save(); ctx.translate(0, -505); ctx.rotate(o.tilt || 0);
  rr(-20, -24, 40, 30, 8, body);                                                            // neck / collar
  maskHead(0, -58, 1, o);
  ctx.restore();
  ctx.restore();
}
// the mask, centred at (x,y): the pale latex face from the film (long face, high cheekbones, thin straight nose,
// hollow almond eyes under heavy lids, thin closed lips), the mask's neck tucked into the collar, messy brown hair swept back
function maskHead(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const SH = a => `rgba(55,64,74,${a})`, HAIR = NIGHT.hair, HI = NIGHT.hairHi;
  // hair behind: full, wavy
  pth('M-62,-4 C-76,-40 -70,-94 -32,-112 C-6,-124 32,-122 54,-102 C74,-82 74,-36 64,-4 C62,8 56,16 50,20 L-50,20 C-58,14 -62,6 -62,-4 Z', HAIR);
  if (o.back) { pth('M-58,-50 C-60,0 -48,40 0,60 C48,40 60,0 58,-50 C46,-96 -46,-96 -58,-50 Z', HAIR);
    ctx.save(); ctx.globalAlpha *= 0.6; for (let i = 0; i < 7; i++) { const a = -44 + i * 15; pthS(`M${a},-80 C${a + 6},-40 ${a - 4},0 ${a + 2},40`, HI, 3); } ctx.restore(); ctx.restore(); return; }
  // the mask's neck, going into the collar
  rr(-25, 46, 50, 56, 12, '#c4c8c7');
  // the face
  glow(`rgba(255,255,255,${o.glowA ?? 0.32})`, o.glowB ?? 28);
  const face = new Path2D('M0,-90 C26,-90 44,-76 45,-52 C47,-30 48,-12 46,4 C44,22 38,40 30,54 C24,66 16,78 0,82 C-16,78 -24,66 -30,54 C-38,40 -44,22 -46,4 C-48,-12 -47,-30 -45,-52 C-44,-76 -26,-90 0,-90 Z');
  const g = ctx.createLinearGradient(-48, 0, 48, 0); g.addColorStop(0, '#c3c7c6'); g.addColorStop(0.22, '#e8eae7'); g.addColorStop(0.5, NIGHT.mask); g.addColorStop(0.78, '#e8eae7'); g.addColorStop(1, '#c3c7c6');
  ctx.fillStyle = g; ctx.fill(face); noGlow();
  // sculpted shading, soft, kept inside the face
  ctx.save(); ctx.clip(face); ctx.filter = `blur(${Math.max(1, 5 * s)}px)`;
  for (const d of [-1, 1]) {
    ell(d * 32, 32, 12, 24, d * 0.35, SH(0.22));                 // cheek hollows under the cheekbones
    ell(d * 44, -40, 9, 24, 0, SH(0.2));                         // temples
    ell(d * 19, -22, 18, 12, d * 0.08, SH(0.32));                // eye sockets
    ell(d * 9, 2, 5, 18, d * 0.1, SH(0.16));                     // sides of the nose
    ell(d * 17, 40, 5, 12, d * -0.3, SH(0.14));                  // beside the mouth
    ell(d * 30, -2, 12, 7, d * -0.4, 'rgba(255,255,255,0.5)');   // cheekbones catch the light
  }
  ell(0, 86, 42, 16, 0, SH(0.26)); ell(0, 56, 9, 4, 0, SH(0.2)); ell(0, -62, 22, 10, 0, 'rgba(255,255,255,0.45)');
  ctx.filter = 'none'; ctx.restore();
  for (const d of [-1, 1]) {
    pthS(`M${d * 34},-36 C${d * 26},-41 ${d * 13},-41 ${d * 6},-35`, SH(0.3), 3);            // brow ridge
    pthS(`M${d * 7},-26 C${d * 14},-32 ${d * 26},-32 ${d * 33},-21`, SH(0.28), 2);           // heavy upper lid
    pth(`M${d * 7},-20 C${d * 12},-28 ${d * 26},-28 ${d * 32},-16 C${d * 25},-12 ${d * 12},-12 ${d * 7},-20 Z`, '#040404');   // the eye hole, drooping at the outside
    ell(d * 6, 22, 3.4, 1.8, 0, 'rgba(35,38,42,0.6)');                                      // nostrils
    const r = o.red || 0;
    if (r > 0) { ctx.save(); ctx.globalAlpha *= r; redGlow(16); circ(d * 19, -19, 3.2, C.red); noGlow(); ctx.restore(); }
  }
  ctx.save(); ctx.globalAlpha *= 0.6; ln(0, -34, 0, 12, 5, '#ffffff'); ctx.restore();         // the bridge catches the light
  pthS('M-11,19 C-6,24 6,24 11,19', SH(0.3), 2);                                               // tip of the nose
  pth('M-15,45 C-8,41 -3,42 0,43 C3,42 8,41 15,45 C8,46 -8,46 -15,45 Z', SH(0.28));            // thin upper lip
  pthS('M-15,45 C-6,47 6,47 15,45', '#4a4e53', 1.8);                                           // closed
  // hair over the top: high hairline, thick and messy, swept back, loose at the temples
  pth('M-52,-40 C-60,-84 -36,-114 2,-114 C40,-114 64,-88 53,-40 C49,-56 42,-68 32,-73 C27,-81 16,-84 6,-81 C-4,-86 -18,-84 -25,-77 C-35,-75 -46,-62 -52,-40 Z', HAIR);
  for (const d of [-1, 1]) pth(`M${d * 44},-60 C${d * 54},-46 ${d * 52},-26 ${d * 48},-14 C${d * 46},-28 ${d * 45},-42 ${d * 40},-54 Z`, HAIR);
  ctx.save(); ctx.globalAlpha *= 0.8;
  for (const [a, b] of [[-44, -92], [-30, -104], [-12, -110], [8, -110], [26, -104], [42, -92]]) pthS(`M${a},${b} C${a + 6},${b + 6} ${a + 4},${b + 14} ${a + 10},${b + 18}`, HI, 2.5);
  ctx.restore();
  ctx.restore();
  ctx.restore();
}
// a kitchen knife: handle at (x,y), blade pointing along ang
function knife(x, y, ang, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s);
  rr(-34, -9, 40, 18, 5, '#1b1b1d'); circ(-22, 0, 2.5, '#777'); circ(-8, 0, 2.5, '#777');
  glow(o.red ? 'rgba(255,43,43,0.8)' : 'rgba(255,255,255,0.35)', o.red ? 18 : 12);
  pth('M8,-11 L120,-6 C134,-4 140,2 146,8 L8,11 Z', o.red ? '#ffdede' : '#e9e9e9'); noGlow();
  ln(20, -6, 118, -3, 2, 'rgba(255,255,255,0.9)');
  ctx.restore();
}

// ---------- you, the neighbours, the kids ----------
// a flat white person; feet at (x,y), 360 tall at s=1. o.face: 'front' (two eyes, no mouth) | 'back' | 'left' | 'right'; o.arms: [l, r] raise 0..1; o.walk phase
function me(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); const col = o.col || C.fig;
  glow('rgba(255,255,255,0.25)', 14);
  const sw = o.walk != null ? Math.sin(o.walk) : 0;
  ln(-14, -170, -16 - sw * 16, -6, 26, col); ln(14, -170, 16 + sw * 16, -6, 26, col);
  rr(-34, -300, 68, 150, 24, col);
  const [al, ar] = o.arms || [0, 0];
  ln(-30, -280, lerp(-44 + sw * 14, -70, al), lerp(-170, -330, al), 20, col);
  ln(30, -280, lerp(44 - sw * 14, 70, ar), lerp(-170, -330, ar), 20, col);
  circ(0, -340, 36, col); noGlow();
  const f = o.face || 'front';
  if (f === 'front') { circ(-12, -344, 5.5, '#000'); circ(12, -344, 5.5, '#000'); }
  if (f === 'left') circ(-18, -344, 5.5, '#000');
  if (f === 'right') circ(18, -344, 5.5, '#000');
  ctx.restore();
}
// trick-or-treaters: kind 'ghost' | 'witch' | 'kid'; feet at (x,y), ~200 tall at s=1, bag swinging
function trickKid(x, y, s, kind, ph = 0) {
  ctx.save(); ctx.translate(x, y + Math.abs(Math.sin(ph)) * -6 * s); ctx.scale(s, s);
  glow('rgba(255,255,255,0.22)', 10);
  if (kind === 'ghost') {
    pth('M-44,0 C-48,-70 -46,-170 0,-176 C46,-170 48,-70 44,0 L30,-12 L15,0 L0,-12 L-15,0 L-30,-12 Z', C.fig); noGlow();
    ell(-14, -128, 7, 10, 0, '#000'); ell(14, -128, 7, 10, 0, '#000');
  } else {
    ln(-10, -70, -12 - Math.sin(ph) * 10, 0, 16, C.fig); ln(10, -70, 12 + Math.sin(ph) * 10, 0, 16, C.fig);
    rr(-24, -150, 48, 86, 16, C.fig); circ(0, -172, 26, C.fig); noGlow();
    circ(-9, -174, 4, '#000'); circ(9, -174, 4, '#000');
    if (kind === 'witch') { pth('M-40,-188 L40,-188 L6,-268 Z', '#9a9a9a'); rr(-46, -194, 92, 10, 4, '#9a9a9a'); }
  }
  // the candy pillowcase
  const bx = 34 + Math.sin(ph) * 4; ln(26, -110, bx, -70, 6, C.sec); pth(`M${bx - 20},-74 L${bx + 22},-74 L${bx + 26},-20 C${bx + 10},-6 ${bx - 10},-6 ${bx - 24},-20 Z`, C.sec);
  ctx.restore();
}

// ---------- the street ----------
function jackO(x, y, r, lit = 1, smashed = false) {
  if (smashed) { for (let i = 0; i < 6; i++) { const a = hash(x + i) * 6.28, d = r * (0.4 + hash(i + y) * 1.2); ell(x + Math.cos(a) * d, y + 6 + Math.sin(a) * d * 0.3, r * 0.34, r * 0.16, a, '#3a3a3a'); } return; }
  ell(x, y, r * 1.25, r, 0, '#2a2a2a'); ell(x, y, r * 0.6, r, 0, '#232323'); rr(x - r * 0.1, y - r * 1.25, r * 0.2, r * 0.35, 3, '#3a3a3a');
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; amberGlow(r * 0.8);
    pth(`M${x - r * 0.62},${y - r * 0.22} L${x - r * 0.3},${y - r * 0.22} L${x - r * 0.46},${y - r * 0.52} Z M${x + r * 0.62},${y - r * 0.22} L${x + r * 0.3},${y - r * 0.22} L${x + r * 0.46},${y - r * 0.52} Z M${x - r * 0.7},${y + r * 0.2} L${x + r * 0.7},${y + r * 0.2} L${x + r * 0.4},${y + r * 0.5} L${x + r * 0.15},${y + r * 0.34} L${x - r * 0.15},${y + r * 0.5} L${x - r * 0.4},${y + r * 0.34} Z`, NIGHT.amber);
    noGlow(); ctx.restore(); }
}
// a house: base centre (x, y), width w; o.win: lit amount per window [4]; o.porch: porch light; o.pumpkins; o.old (empty house: boards, no light); o.door 0..1 open
function house(x, y, w, o = {}) {
  const h = w * 0.62, l = x - w / 2;
  ctx.save();
  // roof
  ctx.beginPath(); ctx.moveTo(l - w * 0.06, y - h); ctx.lineTo(x, y - h - w * 0.38); ctx.lineTo(l + w * 1.06, y - h); ctx.closePath(); ctx.fillStyle = NIGHT.roof; ctx.fill(); ctx.strokeStyle = NIGHT.houseHi; ctx.lineWidth = 3; ctx.stroke();
  if (o.chimney !== false) rr(x + w * 0.22, y - h - w * 0.36, w * 0.08, w * 0.2, 2, NIGHT.roof);
  rr(l, y - h, w, h, 0, o.old ? '#0d0d0e' : NIGHT.house); rrS(l, y - h, w, h, 0, NIGHT.houseHi, 3);
  // windows: two up, two down beside the door
  const ws = [[l + w * 0.16, y - h * 0.86], [l + w * 0.62, y - h * 0.86], [l + w * 0.1, y - h * 0.42], [l + w * 0.68, y - h * 0.42]], ww = w * 0.22, wh = h * 0.26;
  ws.forEach(([wx, wy], i) => {
    const lit = (o.win || [])[i] || 0;
    rr(wx, wy, ww, wh, 2, '#050505');
    if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; amberGlow(30); rr(wx, wy, ww, wh, 2, '#8a6a3e'); noGlow(); ctx.restore(); }
    if (o.who && o.who.win === i) { ctx.save(); ctx.beginPath(); ctx.rect(wx, wy, ww, wh); ctx.clip(); o.who.fn(wx, wy, ww, wh); ctx.restore(); }
    rrS(wx, wy, ww, wh, 2, NIGHT.houseHi, 3); ln(wx + ww / 2, wy, wx + ww / 2, wy + wh, 3, NIGHT.houseHi); ln(wx, wy + wh / 2, wx + ww, wy + wh / 2, 3, NIGHT.houseHi);
    if (o.old && i !== (o.who ? o.who.win : -1) && i % 2 === 0) { ln(wx - 6, wy + wh * 0.3, wx + ww + 6, wy + wh * 0.5, 7, '#2b2622'); ln(wx - 6, wy + wh * 0.7, wx + ww + 6, wy + wh * 0.55, 7, '#2b2622'); }
  });
  // door + steps
  const dx = x - w * 0.09, dw = w * 0.18, dh = h * 0.5;
  rr(dx, y - dh, dw, dh, 2, '#070707');
  const op = o.door || 0;
  if (op < 1) { ctx.save(); ctx.translate(dx, 0); ctx.scale(1 - op * 0.85, 1); rr(0, y - dh, dw, dh, 2, o.old ? '#16130f' : '#1d1d20'); rrS(0, y - dh, dw, dh, 2, NIGHT.houseHi, 3); circ(dw * 0.8, y - dh * 0.45, 4, '#777'); ctx.restore(); }
  rr(dx - dw * 0.3, y - 10, dw * 1.6, 10, 2, '#1a1a1c');
  if (o.porch) { ctx.save(); amberGlow(26); circ(dx + dw + 14, y - dh * 0.8, 6, NIGHT.amber); noGlow(); const g = ctx.createRadialGradient(dx + dw + 14, y - dh * 0.8, 4, dx + dw + 14, y - dh * 0.8, w * 0.35);
    g.addColorStop(0, 'rgba(255,190,110,0.18)'); g.addColorStop(1, 'rgba(255,190,110,0)'); ctx.fillStyle = g; ctx.fillRect(l - w * 0.2, y - h, w * 1.4, h + 20); ctx.restore(); }
  if (o.pumpkins) { jackO(dx - dw * 0.5, y - 12, w * 0.04, o.pumpkins, o.smashed); jackO(dx + dw * 1.5, y - 12, w * 0.032, o.pumpkins, o.smashed); }
  if (o.old) { // dead tree beside the empty house
    pthS(`M${l - w * 0.18},${y} L${l - w * 0.17},${y - h * 1.1} M${l - w * 0.17},${y - h * 0.7} L${l - w * 0.3},${y - h * 0.95} M${l - w * 0.17},${y - h * 0.9} L${l - w * 0.05},${y - h * 1.25}`, '#232323', 8); }
  ctx.restore();
}
function streetlight(x, y, s = 1, on = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (on > 0) { const g = ctx.createRadialGradient(0, -560, 10, 0, -200, 420); g.addColorStop(0, `rgba(255,250,235,${0.2 * on})`); g.addColorStop(1, 'rgba(255,250,235,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-30, -580); ctx.lineTo(30, -580); ctx.lineTo(240, 10); ctx.lineTo(-240, 10); ctx.closePath(); ctx.fill();
    ctx.save(); ctx.globalAlpha *= 0.25 * on; ell(0, 4, 230, 30, 0, '#fff7e6'); ctx.restore(); }
  rr(-7, -600, 14, 600, 4, '#2c2c30'); pthS('M0,-596 C0,-640 30,-650 60,-640', '#2c2c30', 12);
  rr(30, -650, 70, 22, 8, '#3a3a3e'); if (on > 0) { glow('rgba(255,250,235,0.9)', 30); rr(38, -632, 54, 8, 4, '#fffaf0'); noGlow(); }
  ctx.restore();
}
function mailbox(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-6, -110, 12, 110, 3, '#2a2a2c'); rr(-40, -150, 80, 46, 18, '#3a3a3e'); rrS(-40, -150, 80, 46, 18, '#55555a', 3); rr(34, -170, 6, 34, 2, '#55555a');
  ctx.restore();
}
// the view across the street. Coordinates are screen pixels at z=1. o.him: null | {x, y, s, ...myers options}; o.kids: phase; o.cam: [z, fx, fy]
function streetScene(t, o = {}) {
  const [z, fx, fy] = o.cam || [1, 960, 540], [scx, scy] = o.scr || [960, 540];
  ctx.save(); ctx.translate(scx, scy); ctx.scale(z, z); ctx.translate(-fx, -fy);
  const g = ctx.createLinearGradient(0, -200, 0, 640); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-600, -400, 3200, 1100);
  // moon and a few stars
  if (!o.morning) { ctx.save(); glow('rgba(255,255,255,0.5)', 40); circ(1560, 150, 46, '#d9d9d4'); noGlow(); ctx.restore(); }
  if (!o.morning) for (let i = 0; i < 40; i++) { const sx = hash(i * 3.3) * 2400 - 200, sy = hash(i * 5.1) * 380; ctx.save(); ctx.globalAlpha = 0.25 + 0.3 * Math.sin(t * 1.3 + i); circ(sx, sy, 1.6, '#fff'); ctx.restore(); }
  // the houses across the street
  const row = o.houses || [[-120, 0.5, [0, 0.8, 0.6, 0]], [340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]], [1820, 0.5, [0, 0.7, 0.7, 0]], [2300, 0.48, [0.6, 0, 0, 0.8]]];
  row.forEach(([hx, k, win], i) => house(hx, 600, 380 * k * 2, { win: o.dimHouses ? win.map(v => v * 0.4) : win, porch: !o.morning && i % 2 === 0, pumpkins: o.morning ? 0 : 1, smashed: o.morning }));
  if (o.emptyHouse) o.emptyHouse();
  // sidewalk, street, near sidewalk, your lawn
  rr(-600, 600, 3200, 40, 0, NIGHT.walk); rr(-600, 640, 3200, 160, 0, NIGHT.street);
  for (let i = -6; i < 30; i++) rr(i * 140 + 20, 716, 70, 7, 2, '#2a2a2c');
  rr(-600, 800, 3200, 36, 0, NIGHT.walk); rr(-600, 836, 3200, 400, 0, NIGHT.grass);
  for (let i = 0; i < 90; i++) { const gx = hash(i * 1.9) * 2400 - 200, gy = 850 + hash(i * 2.7) * 220; ln(gx, gy, gx + 3, gy - 10, 2, '#151a15'); }
  if (o.extra) o.extra();
  streetlight(1100, 640, 0.95, o.light ?? 1);
  if (o.mailbox !== false) mailbox(820, 880, 1.2);
  if (o.kids != null) { const ph = o.kids; const ks = [['witch', 0], ['ghost', 210], ['kid', 330], ['ghost', 700], ['kid', 820]];
    ks.forEach(([k, off], i) => { const kx = ((off + ph * 60) % 2600) - 300; trickKid(kx, 632 - (i % 2) * 4, 0.55, k, ph * 5 + i); }); }
  if (o.him) myers(o.him.x, o.him.y, o.him.s, o.him);
  if (o.near) o.near();
  ctx.restore();
}
// your window, from inside: the dark wall around a window with curtains. o.close 0..1 (curtains drawn), o.fn draws the outside
function windowPOV(t, o = {}) {
  const X0 = o.x0 ?? 300, X1 = o.x1 ?? 1620, Y0 = o.y0 ?? 80, Y1 = o.y1 ?? 930;
  ctx.save(); ctx.beginPath(); ctx.rect(X0, Y0, X1 - X0, Y1 - Y0); ctx.clip(); o.fn && o.fn(); ctx.restore();
  // the room wall (even-odd hole)
  ctx.save(); ctx.beginPath(); ctx.rect(-200, -200, W + 400, H + 400); ctx.rect(X0, Y0, X1 - X0, Y1 - Y0); ctx.fillStyle = '#060606'; ctx.fill('evenodd'); ctx.restore();
  // frame and the cross
  rrS(X0, Y0, X1 - X0, Y1 - Y0, 2, '#2a2a2d', 22); if (o.cross !== false) { ln((X0 + X1) / 2, Y0, (X0 + X1) / 2, Y1, 14, '#1e1e21'); ln(X0, (Y0 + Y1) / 2 - 60, X1, (Y0 + Y1) / 2 - 60, 12, '#1e1e21'); }
  rr(X0 - 50, Y1 + 10, X1 - X0 + 100, 26, 4, '#1c1c1f');                                                 // sill
  // curtains: soft folds; they meet in the middle when closed
  const cl = clamp(o.close || 0), cw = lerp(150, (X1 - X0) / 2 + 30, cl);
  for (const side of [0, 1]) {
    ctx.save(); const cx = side ? X1 + 60 - cw : X0 - 60;
    ctx.fillStyle = '#17161a'; ctx.fillRect(cx, Y0 - 50, cw, Y1 - Y0 + 120);
    for (let i = 0; i < 6; i++) { const fx = cx + (i + 0.5) * cw / 6; ln(fx, Y0 - 40, fx + Math.sin(t + i) * 3, Y1 + 60, 5, 'rgba(255,255,255,0.05)'); }
    ctx.restore();
  }
  rr(X0 - 90, Y0 - 66, X1 - X0 + 180, 16, 6, '#2a2a2d');                                                // the rail
}

// ---------- inside the house ----------
// a knife block on the counter: origin = bottom centre. Five handles, biggest first. o.missing: slot index; o.red: the empty slot glows red
const BLK = { A: [-190, -330], B: [170, -140], f: [0.13, 0.3, 0.47, 0.64, 0.81], k: [1.18, 1.06, 0.96, 0.88, 0.8] };
const BLK_N = [0.47, -0.88], BLK_ANG = Math.atan2(-0.88, 0.47), BLK_FACE = Math.atan2(BLK.B[1] - BLK.A[1], BLK.B[0] - BLK.A[0]);
const blkP = i => [lerp(BLK.A[0], BLK.B[0], BLK.f[i]), lerp(BLK.A[1], BLK.B[1], BLK.f[i])];
const blkTip = (i, extra = 50) => { const p = blkP(i), L = 150 * BLK.k[i] + extra; return [p[0] + BLK_N[0] * L, p[1] + BLK_N[1] * L]; };
function blkHandle(i, out = 0) {   // out: how far it is pulled out (0 = seated)
  const p = blkP(i), k = BLK.k[i], L = 150 * k, w = 30 * k;
  ctx.save(); ctx.translate(p[0] + BLK_N[0] * out, p[1] + BLK_N[1] * out); ctx.rotate(BLK_ANG);
  if (out > 0) { glow('rgba(255,255,255,0.4)', 14); pth(`M0,${-w * 0.42} L${-out},${-w * 0.1} L${-out},${w * 0.3} L0,${w * 0.42} Z`, '#dcdcdc'); noGlow(); }
  rr(-4, -w * 0.55, 14, w * 1.1, 3, '#8a8a90');
  rr(10, -w / 2, L, w, w * 0.45, '#161618'); rrS(10, -w / 2, L, w, w * 0.45, '#46464d', 2.5);
  for (const f of [0.3, 0.55, 0.8]) circ(10 + L * f, 0, 3.4 * k, '#9a9aa0');
  ctx.restore();
}
function knifeBlock(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const miss = o.missing ?? -1;
  // the block: front face, top face
  pth(`M-200,0 L180,0 L180,${BLK.B[1] + 10} L${BLK.A[0] - 10},${BLK.A[1] + 6} Z`, '#3d3128');
  for (let i = 0; i < 5; i++) ln(-190 + i * 10, -40 - i * 50, 170, -30 - i * 22, 2, 'rgba(0,0,0,0.18)');
  pth(`M${BLK.A[0] - 10},${BLK.A[1] + 6} L${BLK.A[0] + 6},${BLK.A[1] - 14} L${BLK.B[0] + 12},${BLK.B[1] - 12} L${BLK.B[0] + 10},${BLK.B[1] + 10} Z`, '#2a2119');
  pthS(`M-200,0 L180,0 L180,${BLK.B[1] + 10} L${BLK.A[0] - 10},${BLK.A[1] + 6} Z`, '#5a4a3c', 3);
  for (let i = 0; i < 5; i++) {
    const p = blkP(i);
    ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(BLK_FACE);
    if (i === miss && o.red) { redGlow(18 + 8 * Math.sin((o.t || 0) * 6)); rrS(-20 * BLK.k[i], -7, 40 * BLK.k[i], 14, 4, C.red, 5); noGlow(); }
    rr(-18 * BLK.k[i], -5, 36 * BLK.k[i], 10, 3, '#0a0806');
    ctx.restore();
  }
  for (let i = 4; i >= 0; i--) if (i !== miss && !(o.out && o.out[0] === i)) blkHandle(i);
  if (o.out) blkHandle(o.out[0], o.out[1]);
  ctx.restore();
}
// the dark kitchen: counter across the bottom, cabinets, the window over the sink (black glass). o.reflect(t): draws inside the glass
function kitchen(t, o = {}) {
  ctx.fillStyle = '#060606'; ctx.fillRect(-200, -200, W + 400, H + 400);
  // moonlight from the side
  const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(140,160,200,0.07)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 5; i++) { rr(80 + i * 360, 60, 330, 250, 6, '#0e0e10'); rrS(80 + i * 360, 60, 330, 250, 6, '#1f1f22', 3); circ(80 + i * 360 + (i % 2 ? 30 : 300), 280, 6, '#333'); }
  // the window over the sink
  const wx = o.winX ?? 760, wy = 330, ww = 520, wh = 330;
  rr(wx, wy, ww, wh, 4, '#030304');
  if (o.reflect) { ctx.save(); ctx.beginPath(); ctx.rect(wx, wy, ww, wh); ctx.clip(); o.reflect(wx, wy, ww, wh); ctx.restore(); }
  ctx.save(); ctx.globalAlpha = 0.08; pth(`M${wx + 40},${wy} L${wx + 140},${wy} L${wx + 20},${wy + wh} L${wx - 80},${wy + wh} Z`, '#fff'); ctx.restore();   // glass sheen
  rrS(wx, wy, ww, wh, 4, '#2a2a2d', 14); ln(wx + ww / 2, wy, wx + ww / 2, wy + wh, 10, '#1e1e21');
  // counter
  rr(-100, 700, W + 200, 40, 0, '#232327'); rr(-100, 740, W + 200, 400, 0, '#0e0e10');
  for (let i = 0; i < 6; i++) rrS(40 + i * 320, 770, 300, 300, 6, '#1d1d20', 3);
  if (o.block !== false) knifeBlock(o.blockX ?? 380, 700, o.blockS ?? 0.9, o.blockO || {});
}
// slatted closet door seen from inside: the scene behind, then the louvres over it. k = how open the gaps are
function slats(fnBehind, o = {}) {
  ctx.save(); ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); fnBehind(); ctx.restore();
  const gap = o.gap ?? 36, pitch = 74;
  ctx.fillStyle = '#0b0a09';
  for (let y = -40; y < H + 80; y += pitch) {
    ctx.beginPath(); ctx.moveTo(-50, y); ctx.lineTo(W + 50, y); ctx.lineTo(W + 50, y + pitch - gap); ctx.lineTo(-50, y + pitch - gap); ctx.closePath(); ctx.fill();
    ln(-50, y + pitch - gap, W + 50, y + pitch - gap, 3, '#24211e');
  }
  // the door frame edges, very dark
  const v = ctx.createLinearGradient(0, 0, W, 0); v.addColorStop(0, 'rgba(0,0,0,0.95)'); v.addColorStop(0.12, 'rgba(0,0,0,0)'); v.addColorStop(0.88, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.95)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
// one-point hallway: vanishing point (960, 470). o.open[i] for the side doors (0..1), o.labels, o.fig(dep) to draw someone at a depth
const HALL = { vx: 960, vy: 470 };
function hallway(t, o = {}) {
  ctx.fillStyle = '#040404'; ctx.fillRect(-200, -200, W + 400, H + 400);
  const P = d => { const k = 1 / (1 + d); return [(x, y) => [HALL.vx + (x - HALL.vx) * k, HALL.vy + (y - HALL.vy) * k]]; };
  const at = (x, y, d) => { const k = 1 / (1 + d); return [HALL.vx + (x - HALL.vx) * k, HALL.vy + (y - HALL.vy) * k]; };
  // walls, floor, ceiling as quads from d=0 to d=6
  const q = (a, b, c, e, col) => { ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(...c); ctx.lineTo(...e); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); };
  const L = 260, R = 1660, T = -60, B = 1130, D = 7;
  q(at(L, T, 0), at(L, T, D), at(L, B, D), at(L, B, 0), '#1a1a1e');
  q(at(R, T, 0), at(R, T, D), at(R, B, D), at(R, B, 0), '#16161a');
  q(at(L, B, 0), at(L, B, D), at(R, B, D), at(R, B, 0), '#1d1c20');
  q(at(L, T, 0), at(L, T, D), at(R, T, D), at(R, T, 0), '#0e0e10');
  const end = [at(L, T, D), at(R, B, D)]; rr(end[0][0], end[0][1], end[1][0] - end[0][0], end[1][1] - end[0][1], 0, '#202128');
  { const a = at(760, 200, D), b = at(1160, 700, D); ctx.save(); glow('rgba(170,190,230,0.6)', 30); rr(a[0], a[1], b[0] - a[0], b[1] - a[1], 2, '#3a4152'); noGlow(); ln((a[0] + b[0]) / 2, a[1], (a[0] + b[0]) / 2, b[1], 3, '#202128'); ctx.restore(); }
  for (let d = 0.5; d < D; d += 0.6) { const a = at(L, B, d), b = at(R, B, d); ln(a[0], a[1], b[0], b[1], 2, '#1a191c'); }   // floorboards
  // side doors: [side, depth]
  const doors = o.doors || [[-1, 0.5], [1, 1.25], [-1, 2.1], [1, 3.1]];
  doors.forEach(([sd, d], i) => {
    const x = sd < 0 ? L : R, d1 = d + 0.55, op = (o.open || [])[i] || 0;
    const a = at(x, 260, d), b = at(x, 260, d1), c = at(x, B, d1), e = at(x, B, d);
    q(a, b, c, e, '#000');
    // the door leaf swings into the room
    const sw = lerp(d1, d1 - 0.5 * op, 1), lx = x - sd * 520 * op;
    q(at(x, 260, d), at(lx, 260, d + 0.55 * (1 - op)), at(lx, B, d + 0.55 * (1 - op)), at(x, B, d), '#2c2b31'); { const m = at(lx + sd * 60 * (1 - op), 700, d + 0.45 * (1 - op)); circ(m[0], m[1], 7 / (1 + d), '#77777e'); }
    ctx.save(); ctx.globalAlpha = 0.6; ln(...at(x, 260, d), ...at(x, B, d), 3, '#333'); ctx.restore();
    if (o.labels && o.labels[i] && o.labels[i][1] <= t) { const m = at(x, 560, d + 0.27), ly = m[1] - 200 / (1 + d) + (o.labels[i][2] || 0); pop(t, o.labels[i][1], m[0], ly, () => tag(o.labels[i][0], m[0], ly, C.fig, 34, 'center'), 0.3); }
  });
  if (o.fig) o.fig(at);
  // light from the far end
  const lg = ctx.createRadialGradient(HALL.vx, HALL.vy, 10, HALL.vx, HALL.vy, 700); lg.addColorStop(0, 'rgba(200,210,230,0.10)'); lg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H);
  return at;
}
// top-down floor plan; rooms: [name, x, y, w, h]; returns the room map
const PLAN = [['BEDROOM', 360, 180, 420, 330], ['BATHROOM', 780, 180, 260, 330], ['GUEST ROOM', 1040, 180, 420, 330], ['LAUNDRY', 360, 590, 300, 300], ['HALL', 660, 510, 800, 80], ['CLOSET', 1300, 590, 160, 300], ['KITCHEN', 660, 590, 640, 300]];
function floorPlan(t, o = {}) {
  ctx.save(); glow('rgba(255,255,255,0.2)', 20);
  rr(340, 160, 1140, 750, 6, '#0b0b0c'); noGlow();
  for (const [n, x, y, w, h] of PLAN) {
    if (n === 'HALL') { rr(x, y, w, h, 0, '#121214'); continue; }
    const hot = o.hot === n, chk = (o.checked || []).includes(n);
    rr(x + 6, y + 6, w - 12, h - 12, 4, hot ? 'rgba(255,43,43,0.12)' : '#0f0f11');
    rrS(x, y, w, h, 2, hot ? C.red : C.fig, 6);
    text(n, x + w / 2, y + h / 2 + 12, '900 30px M', hot ? C.red : (chk ? C.mid : C.sec));
    if (chk) { check(x + w / 2, y + h / 2 + 62, 22, 1, C.mid); }
  }
  // door gaps on the hall
  for (const gx of [540, 880, 1220]) rr(gx, 504, 70, 12, 0, '#0b0b0c');
  for (const gx of [480, 960, 1350]) rr(gx, 584, 70, 12, 0, '#0b0b0c');
  ctx.restore();
}
// rooms centres for paths
const roomC = n => { const r = PLAN.find(p => p[0] === n); return [r[1] + r[3] / 2, r[2] + r[4] / 2]; };

// a cutaway of the house: two floors, side view. rooms: [name, x, y, w, h]
const CUT = [['BEDROOM', 520, 250, 440, 300], ['CLOSET', 960, 250, 160, 300], ['BATHROOM', 1120, 250, 280, 300], ['KITCHEN', 520, 550, 520, 300], ['LIVING ROOM', 1040, 550, 360, 300]];
function cutaway(t, o = {}) {
  ctx.save();
  ctx.beginPath(); ctx.moveTo(480, 250); ctx.lineTo(960, 40); ctx.lineTo(1440, 250); ctx.closePath(); ctx.fillStyle = '#0d0d0f'; ctx.fill(); ctx.strokeStyle = '#3a3a3e'; ctx.lineWidth = 5; ctx.stroke();
  for (const [n, x, y, w, h] of CUT) {
    const hot = (o.hot || []).includes(n);
    rr(x, y, w, h, 0, hot ? 'rgba(255,43,43,0.08)' : '#0b0b0c'); rrS(x, y, w, h, 0, '#3a3a3e', 5);
    if (o.labels !== false) text(n, x + w / 2, y + 44, '900 24px M', hot ? C.red : C.mid);
  }
  rr(440, 850, 1040, 14, 0, '#3a3a3e');
  if (o.fn) o.fn();
  ctx.restore();
}
// car interior at night: the road through the windshield, the rear-view mirror at the top. o.face: 0..1 white face in the mirror
function carView(t, o = {}) {
  ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400);
  // the road in the headlights
  ctx.save(); const g = ctx.createRadialGradient(960, 760, 40, 960, 760, 760); g.addColorStop(0, 'rgba(255,248,230,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 300, W, 800);
  ctx.beginPath(); ctx.moveTo(900, 470); ctx.lineTo(1020, 470); ctx.lineTo(1700, 1080); ctx.lineTo(220, 1080); ctx.closePath(); ctx.fillStyle = '#0d0d0f'; ctx.fill();
  for (let i = 0; i < 8; i++) { const k = ((i / 8 + t * 0.9) % 1), y = lerp(480, 1080, k * k), w = lerp(3, 30, k * k), h = lerp(6, 90, k * k); rr(960 - w / 2, y, w, h, 2, '#3a3a3a'); }
  ctx.restore();
  // dashboard and the frame of the windshield
  pth('M-100,1080 L-100,820 C300,760 1620,760 2020,820 L2020,1080 Z', '#060607'); pthS('M-100,820 C300,760 1620,760 2020,820', '#222226', 4);
  pth('M-100,-100 L2020,-100 L2020,180 C1600,140 320,140 -100,180 Z', '#050506');
  pth('M-100,-100 L300,-100 L80,1080 L-100,1080 Z', '#050506'); pth('M2020,-100 L1620,-100 L1840,1080 L2020,1080 Z', '#050506');
  // steering wheel
  ctx.save(); ctx.lineWidth = 34; ctx.strokeStyle = '#141416'; ctx.beginPath(); ctx.arc(620, 1080, 300, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.restore();
  // the mirror
  const mx = 960, my = 180, mw = 520, mh = 150;
  ln(mx, 130, mx, my - mh / 2, 14, '#1a1a1c');
  rr(mx - mw / 2 - 12, my - mh / 2 - 12, mw + 24, mh + 24, 30, '#1a1a1c');
  ctx.save(); ctx.beginPath(); ctx.roundRect(mx - mw / 2, my - mh / 2, mw, mh, 22); ctx.clip();
  ctx.fillStyle = '#0a0b0d'; ctx.fillRect(mx - mw / 2, my - mh / 2, mw, mh);
  // the back seat and the rear window in the mirror
  rr(mx - 220, my + 10, 440, 80, 20, '#151518'); rr(mx - 180, my - 70, 360, 60, 10, '#101114');
  if ((o.face || 0) > 0) { ctx.save(); ctx.globalAlpha *= o.face; rr(mx - 70 + 20, my - 10, 120, 120, 40, NIGHT.jump); maskHead(mx + 10, my + 6, 0.62, { red: o.red || 0, glowA: 0.25, glowB: 16 }); ctx.restore(); }
  ctx.globalAlpha = 0.08; pth(`M${mx - mw / 2},${my - mh / 2} L${mx - mw / 2 + 120},${my - mh / 2} L${mx - mw / 2 + 40},${my + mh / 2} L${mx - mw / 2 - 80},${my + mh / 2} Z`, '#fff');
  ctx.restore();
  rrS(mx - mw / 2, my - mh / 2, mw, mh, 22, '#2e2e33', 4);
}
// icons for the teaser boxes and lists (white on dark)
function icon6(name, x, y, s = 1, col = C.fig) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 14);
  if (name === 'eye') { pth('M-90,0 C-50,-56 50,-56 90,0 C50,56 -50,56 -90,0 Z', col); noGlow(); circ(0, 0, 26, '#000'); }
  if (name === 'closet') { rrS(-70, -90, 140, 180, 6, col, 8); ln(0, -90, 0, 90, 6, col); for (let i = 0; i < 6; i++) { ln(-58, -68 + i * 26, -10, -60 + i * 26, 6, col); ln(10, -68 + i * 26, 58, -60 + i * 26, 6, col); } circ(-14, 10, 5, col); circ(14, 10, 5, col); }
  if (name === 'rise') { rr(-110, 70, 220, 12, 5, C.sec); circ(-80, 36, 28, col); rr(-46, 16, 150, 44, 18, col); ln(-80, -10, -80, -80, 12, col); pth('M-108,-66 L-80,-104 L-52,-66 Z', col); }
  if (name === 'knives') { ctx.rotate(-0.4); for (let i = 0; i < 4; i++) { rr(-60 + i * 36, -90, 20, 70, 6, col); } ctx.rotate(0.4); rr(-90, -10, 180, 90, 10, col); noGlow(); rrS(-60 + 3 * 36 - 12, -80, 40, 30, 5, C.red, 0); }
  if (name === 'phone') { rrS(-38, -72, 76, 144, 14, col, 8); circ(0, 52, 7, col); }
  if (name === 'curtain') { ln(-90, -84, 90, -84, 8, col); pth('M-80,-80 C-60,-20 -70,40 -40,84 L-4,84 C-24,40 -14,-20 -10,-80 Z', col); pth('M80,-80 C60,-20 70,40 40,84 L4,84 C24,40 14,-20 10,-80 Z', col); }
  if (name === 'blink') { pthS('M-90,0 C-50,40 50,40 90,0', col, 10); for (let i = -2; i <= 2; i++) ln(i * 34, 26 - Math.abs(i) * 4, i * 44, 56 - Math.abs(i) * 4, 7, col); }
  if (name === 'search') { circS(-14, -14, 52, col, 12); ln(24, 24, 74, 74, 16, col); }
  if (name === 'voice') { circ(-40, 0, 40, col); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(-10, 0, 46 + i * 24, -0.7, 0.7); ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.stroke(); } }
  if (name === 'door') { rrS(-56, -90, 112, 180, 6, col, 8); circ(32, 4, 8, col); }
  if (name === 'step') { ell(-30, 20, 22, 42, -0.2, col); ell(36, -30, 22, 42, 0.2, col); }
  if (name === 'breath') { for (let i = 0; i < 3; i++) pthS(`M-80,${-40 + i * 40} C-30,${-60 + i * 40} 10,${-20 + i * 40} 80,${-40 + i * 40}`, col, 9); }
  if (name === 'hand') { rr(-40, -10, 80, 90, 24, col); for (let i = 0; i < 4; i++) rr(-40 + i * 21, -80, 16, 80, 8, col); ctx.save(); ctx.translate(-44, 30); ctx.rotate(-0.7); rr(-8, -50, 16, 56, 8, col); ctx.restore(); }
  if (name === 'back') { circ(0, -60, 32, col); rr(-34, -22, 68, 100, 20, col); pthS('M60,-40 C110,-20 110,40 60,60', col, 8); pth('M54,46 L82,70 L50,80 Z', col); }
  if (name === 'hanger') { pthS('M0,-50 C0,-80 30,-80 30,-60 C30,-46 0,-44 0,-30 L-90,40 L90,40 L0,-30', col, 9); }
  if (name === 'needle') { ln(-90, 70, 90, -70, 9, col); ellS(-70, 54, 12, 6, -0.66, col); }
  if (name === 'knife') { knife(-70, 30, -0.45, 0.95); }
  if (name === 'gun') { rr(-90, -30, 150, 40, 8, col); ctx.save(); ctx.translate(30, 0); ctx.rotate(0.25); rr(-10, 0, 40, 80, 8, col); ctx.restore(); circS(10, 30, 16, col, 6); }
  if (name === 'lock') { ctx.beginPath(); ctx.arc(0, -20, 40, Math.PI, 0); ctx.lineWidth = 14; ctx.strokeStyle = col; ctx.stroke(); rr(-60, -20, 120, 100, 14, col); noGlow(); circ(0, 22, 12, '#000'); rr(-5, 22, 10, 30, 3, '#000'); }
  if (name === 'car') { pth('M-100,30 L-90,-10 L-56,-60 L56,-60 L90,-10 L100,30 L100,50 L-100,50 Z', col); noGlow(); circ(-56, 54, 22, '#000'); circ(56, 54, 22, '#000'); circ(-56, 54, 12, col); circ(56, 54, 12, col); rr(-46, -48, 40, 34, 4, '#000'); rr(6, -48, 40, 34, 4, '#000'); }
  if (name === 'scream') { circ(0, -10, 56, col); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(0, -10, 80 + i * 24, -0.5, 0.5); ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.stroke(); ctx.beginPath(); ctx.arc(0, -10, 80 + i * 24, Math.PI - 0.5, Math.PI + 0.5); ctx.stroke(); } }
  if (name === 'call') { pth('M-60,-70 C-80,-40 -60,20 -10,60 C30,90 70,80 80,60 L50,30 L20,44 C0,30 -30,0 -36,-24 L-20,-50 Z', col); }
  noGlow(); ctx.restore();
}
const ellS = (x, y, rx, ry, rot, s, w = 6) => { ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); ctx.strokeStyle = s; ctx.lineWidth = w; ctx.stroke(); };
// a dark card behind a list of items over a busy scene
function listCard(x, y, w, h) { ctx.save(); ctx.globalAlpha *= 0.86; rr(x, y, w, h, 18, '#050505'); ctx.restore(); rrS(x, y, w, h, 18, '#2a2a2d', 3); }
// a row with an icon box, text, and a red X that draws on at tx
function noRow(t, t0, tx, x, y, ic, label, size = 46) {
  slideIn(t, t0, 50, 0, () => {
    rr(x, y - 60, 120, 120, 16, '#121214'); rrS(x, y - 60, 120, 120, 16, '#3a3a3e', 3); icon6(ic, x + 60, y, 0.5);
    text(label, x + 160, y + size * 0.36, `900 ${size}px M`, C.fig, 'left');
    redX(x + 60, y, 50, prog(t, tx, 0.3));
  }, 0.35);
}
// the man in profile (facing o.dir = 1 right / -1 left). Feet at (x,y), 600 tall at s=1.
// o.walk phase, o.knife 0/1/2, o.lean (rad, whole body tips back around the feet: falling), o.floor 0..1: lying on his back -> o.sit 0..1 sits up from the waist
function myersSide(x, y, s = 1, o = {}) {
  const dir = o.dir || 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const body = NIGHT.jump, edge = 'rgba(150,158,170,0.5)';
  const limb = (pts, w, col = body) => { ctx.beginPath(); ctx.moveTo(...pts[0]); for (const p of pts.slice(1)) ctx.lineTo(...p); ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = col; ctx.stroke(); };
  const upper = (o2) => {   // torso, arm, head around the hip at (0,0), pointing up
    const tor = new Path2D('M-50,-210 C-58,-150 -52,-60 -44,0 L44,0 C52,-60 56,-150 46,-210 C20,-222 -26,-222 -50,-210 Z');
    ctx.fillStyle = body; ctx.fill(tor); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke(tor);
    const raise = o2.knife === 2 ? 1 : 0;
    const hand = o2.knife === 2 ? [46, -350] : o2.floorHand ? [40, -20] : [26 + (o2.walk != null ? Math.sin(o2.walk) * 18 : 0), 30];
    limb([[0, -196], [lerp(18, 30, raise), lerp(-90, -270, raise)], hand], 36);
    circ(hand[0], hand[1], 18, '#cfcdc4');
    if (o2.knife) knife(hand[0], hand[1], o2.knife === 2 ? -Math.PI / 2 + 0.25 : Math.PI / 2 - 0.1, 1);
    // head in profile
    ctx.save(); ctx.translate(6, -262);
    pth('M-52,-30 C-58,-76 -24,-104 12,-100 C34,-98 46,-78 42,-44 L-20,44 C-50,34 -58,0 -52,-30 Z', NIGHT.hair);
    glow('rgba(255,255,255,0.3)', 24);
    pth('M-8,-74 C24,-82 44,-60 44,-34 C46,-24 56,-12 52,-4 C48,2 44,4 44,10 C46,36 34,58 12,62 C-6,60 -18,40 -20,10 C-24,-30 -24,-60 -8,-74 Z', NIGHT.mask); noGlow();
    pth('M-12,-72 C14,-84 40,-70 44,-44 C30,-58 10,-62 -14,-56 Z', NIGHT.hair);
    ctx.save(); ctx.filter = 'blur(3px)'; ell(22, -26, 16, 11, 0.1, 'rgba(55,64,74,0.35)'); ell(4, 18, 16, 22, 0, 'rgba(55,64,74,0.1)'); ell(30, 50, 14, 8, 0, 'rgba(55,64,74,0.2)'); ctx.filter = 'none'; ctx.restore();
    pthS('M8,-40 C18,-46 32,-46 40,-38', 'rgba(55,64,74,0.4)', 3);                 // brow
    pth('M16,-26 C20,-32 30,-32 34,-24 C30,-20 20,-20 16,-26 Z', '#030303');           // the eye hole
    ell(46, 2, 3, 2, 0, 'rgba(35,38,42,0.6)');                                         // nostril
    pthS('M38,22 L46,22', '#4a4e53', 2);                                               // closed lips
    if (o2.red) { ctx.save(); ctx.globalAlpha *= o2.red; redGlow(16); circ(25, -26, 3, C.red); noGlow(); ctx.restore(); }
    ctx.restore();
  };
  if (o.floor) {
    // lying on his back: legs along the floor toward +x, torso tips up from -x as he sits up
    const sit = clamp(o.sit || 0);
    limb([[0, -40], [150, -36], [300, -30]], 44); limb([[0, -40], [160, -50], [300, -40]], 44, NIGHT.jumpLo); rr(286, -64, 34, 60, 10, '#121315');
    ctx.save(); ctx.translate(0, -40); ctx.rotate(lerp(-Math.PI / 2, 0, ease(sit))); upper({ ...o, knife: 0, floorHand: true }); ctx.restore();
    if (o.knife) knife(80, -14, 0.05, 1);
  } else {
    ctx.rotate(-(o.lean || 0));
    const sw = o.walk != null ? Math.sin(o.walk) : 0;
    limb([[0, -300], [sw * 40, -150], [sw * 70, -16]], 44, NIGHT.jumpLo); rr(sw * 70 - 18, -30, 64, 30, 10, '#121315');
    limb([[0, -300], [-sw * 40, -150], [-sw * 70, -16]], 44); rr(-sw * 70 - 18, -30, 64, 30, 10, '#121315');
    ctx.save(); ctx.translate(0, -300); upper(o); ctx.restore();
  }
  ctx.restore();
}
