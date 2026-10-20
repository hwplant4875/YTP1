import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross, esc } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from './tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, fly, perched, perchedInner, standing, standB, FOOT_Y, branch, flowerT, blossom, coin, scale, bee, heartIcon, birdHeart, kid, gauge, readout, card, ecg, arrow, bobB, uid, photo, WING, SHOULDER } from './ha.mjs';
import { landPath, proj } from './maps.mjs';
const N = K.navy;

// 01 opened hummingbird hovering, labels on from frame 0; wings start as a 50/s blur and slow down to slow motion
const r01 = (t, r0 = 50, r1 = 1.1, t0 = 0.5, tau = 0.6) => t < t0 ? r0 : r1 + (r0 - r1) * Math.exp(-(t - t0) / tau);
const ph01 = (t, r0 = 50, r1 = 1.1, t0 = 0.5, tau = 0.6) => t < t0 ? r0 * t : r0 * t0 + r1 * (t - t0) + (r0 - r1) * tau * (1 - Math.exp(-(t - t0) / tau));
export function h01(t) {
  const cx = 900, cy = 600 + bobB(t, 8, 1.6), sc = 1.5, P = n => toB(cx, cy, sc, ...PT[n]);
  const te = at('h01', 'powerful engines'), hb = t > te ? 1 + 0.18 * Math.max(0, Math.sin(t * 14)) : 1;
  const rate = r01(t), amp = lerp(26, 52, Math.min(1, (rate - 1.1) / 20));
  let s = placeB(cx, cy, sc, birdInside({ tongue: 1, heartK: hb, glow: t > te ? 'heart' : null }) + wings(t, { rate, phase: ph01(t), amp, blur: rate > 3 ? 4 : 0, bones: 1 }));
  s += tag(...P('beak'), 1500, 170, 'TONGUE', t, -1, { col: K.yellow }) + tag(...P('muscle'), 640, 990, 'MUSCLE', t, -1) + tag(...P('heart'), 1460, 930, 'HEART', t, -1, { col: K.red, txt: '#fff' });
  return s;
}

// 02 three grams: bird lands on a kitchen scale (toes on the pan), then a coin weighs the same
export function h02(t) {
  const tg = at('h02', 'three grams'), tc = at('h02', 'single coin') - 0.3, tr = at('h02', 'ruby-throated');
  const land = eo(0.2, 1.6, t), sx = 960, sy = 740, pan = sy + 9, bs = 0.42, gy = pan - (FOOT_Y - 300) * bs;
  const bx = lerp(1500, sx + 20, land), by = lerp(330, gy, land);
  const rd = t < tg - 0.6 ? '0.0 G' : `${(3 * eo(tg - 0.6, tg + 0.2, t)).toFixed(1)} G`;
  const A = (shift = 0) => { let s = scale(sx - shift, sy, rd);
    s += land < 1 ? fly(bx - shift, by, bs, t, { rate: 7, amp: 50 }) : standing(bx - shift, pan, bs, {});
    return s; };
  let s;
  if (t < tc) { s = A(); if (t < tg - 0.1) s += tag(bx + 40, by - 120, 960, 340, 'RUBY-THROATED', t, tr, { col: '#fff', line: false, size: 64 }); }
  else { const k = eo(tc, tc + 0.7, t); s = A(330 * k);
    s += `<g opacity="${f1(k)}">${scale(sx + 330, sy, '3 G')}${coin(sx + 330, sy - 12, 80)}</g>`;
    s += big(960, 640, '=', t, tc + 0.4, { size: 200, fill: N });
    s += fade(sx + 330, 520, 'COIN', t, tc + 0.5, { size: 80, fill: '#fff', stroke: N, sw: 14 }); }
  s = `<g transform="translate(960 700) scale(1.4) translate(-960 -700)">${s}</g>`;
  s += big(960, 150, '3 GRAMS', t, tg, { size: 170, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 03 bee hummingbird: Cuba on a map, then the bird next to a honey bee with a 5 cm ruler
export function h03(t) {
  const tb = at('h03', "It's called"), tf = at('h03', 'five centimeters'), ts = at('h03', 'The smallest bird');
  const A = () => { const v = { lon0: -92, lon1: -66, lat0: 14, lat1: 30, x: 160, y: 120, w: 1600, h: 880 }, P = proj(v);
    let s = `<rect x="160" y="120" width="1600" height="880" rx="40" fill="#7cc8f0" stroke="${N}" stroke-width="9"/><clipPath id="mc3"><rect x="160" y="120" width="1600" height="880" rx="40"/></clipPath>`;
    s += `<g clip-path="url(#mc3)"><path d="${landPath(v, true)}" fill="#7fd36e" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g>`;
    const [x, y] = P(-79.5, 21.8), k = pop(at('h03', 'lives in'), t);
    if (k > 0) s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(90 * k)}" fill="none" stroke="${K.red}" stroke-width="12"/>` + tag(x, y - 90, x, y - 250, 'CUBA', t, at('h03', 'lives in') + 0.1, { col: K.red, txt: '#fff', line: false });
    return s; };
  const B = () => { const cx = 780, cy = 640, sc = 1.15;
    let s = placeB(cx, cy + bobB(t, 6), sc, birdSolid() + wings(t, { rate: 9, amp: 50, blur: 3 }));
    s += bee(1560, 660, 1.0, t);
    const x0 = cx + (214 - 600) * sc, x1 = cx + (990 - 600) * sc, ry = 925, rk = eo(tf - 0.2, tf + 0.6, t);
    if (rk > 0) { const xe = lerp(x0, x1, rk); s += `<path d="M${f1(x0)} ${ry} L${f1(xe)} ${ry}" stroke="#fff" stroke-width="10" stroke-linecap="round"/><path d="M${f1(x0)} ${ry - 26} L${f1(x0)} ${ry + 26} M${f1(xe)} ${ry - 26} L${f1(xe)} ${ry + 26}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`; }
    s += big((x0 + x1) / 2, ry + 78, '5 CM', t, tf + 0.3, { size: 100, fill: N, stroke: '#fff', sw: 16 });
    s += tag(1560, 620, 1560, 470, 'BEE', t, tf - 0.2, { col: K.yellow, line: false, size: 64 });
    return s; };
  // photo popup from the name until the size: graphics shrink away behind it, words stay on top
  const p0 = tb + 0.1, p1 = tf - 0.35, pk = t < p1 ? eo(p0, p0 + 0.45, t) : 1 - eo(p1, p1 + 0.35, t), zk = 1 - 0.35 * pk;
  const G = t < tb - 0.3 ? A() : xfade(t, tb - 0.3, 0.5, A, B);
  let s = pk > 0 ? `<g transform="translate(960 560) scale(${f1(zk * 1000) / 1000}) translate(-960 -560)" opacity="${f1(1 - 0.5 * pk)}">${G}</g>` : G;
  s += photo('bee', 960, 540, 1100, 620, pk);
  if (pk > 0) s += `<g opacity="${f1(pk)}">${big(960, 990, 'BEE HUMMINGBIRD', t, p0, { size: 100, fill: '#fff', stroke: N, sw: 16 })}</g>`;
  s += big(960, 150, 'SMALLEST BIRD', t, ts, { size: 150, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 04 wingbeats: slow at first, counter to 50 and 80, then blur and a hum
export function h04(t) {
  const t50 = at('h04', 'fifty times'), t80 = at('h04', 'eighty'), tbl = at('h04', 'blur'), thm = at('h04', 'humming sound');
  const cx = 820, cy = 560 + bobB(t, 6), sc = 1.35;
  const fast = sm(tbl - 0.8, tbl + 0.2, t), rate = lerp(1.6, 22, fast), blur = Math.round(lerp(0, 7, fast));
  // phase-continuous wing angle while the rate ramps
  const ph = 1.6 * t + (t > tbl - 0.8 ? (22 - 1.6) * Math.max(0, t - (tbl - 0.8)) * Math.min(1, (t - (tbl - 0.8)) / 1.0) : 0);
  let s = placeB(cx, cy, sc, birdSolid() + wings(ph / rate, { rate, amp: 58, blur }));
  const n = t < t80 ? count(50, t, t50, 1.0) : count(80, t, t80, 0.6, v => Math.round(lerp(50, 80, v / 80)).toString());
  if (t > t50) s += readout(1560, 470, n, 'PER SECOND', { size: 230 });
  if (t > t80) s += fade(1560, 250, 'UP TO', t, t80, { size: 80, fill: N });
  if (t > thm) { for (let i = 0; i < 4; i++) { const r = ((t - thm) * 260 + i * 120) % 480; s += `<circle cx="${cx - 80}" cy="${f1(cy - 240)}" r="${f1(r)}" fill="none" stroke="#fff" stroke-width="8" opacity="${f1(0.7 * (1 - r / 480))}"/>`; }
    s += big(1300, 960, 'HMMMMM', t, thm + 0.2, { size: 150, fill: '#fff', stroke: N, sw: 18 }); }
  return s;
}

// lemniscate point, u in [0,1)
const lem = (u, cx, cy, a, b) => { const th = u * Math.PI * 2, d = 1 + Math.sin(th) ** 2; return [cx + a * Math.cos(th) / d, cy + b * Math.sin(th) * Math.cos(th) / d]; };
// box point -> screen for placeB(cx, cy, sc, .., { rot })
const bpt = (cx, cy, sc, rot, x, y) => { const r = rot * Math.PI / 180, dx = (x - 300 - 300) * sc, dy = (y - 300) * sc; return [cx + dx * Math.cos(r) - dy * Math.sin(r), cy + dx * Math.sin(r) + dy * Math.cos(r)]; };
const WTIP = [-262, -222], WLEN = Math.hypot(...WTIP), WANG = Math.atan2(WTIP[1], WTIP[0]);
// a wing drawn from shoulder S so its tip sits on P; flip in -1..1 mirrors it across its long axis (the twist)
const wingTo = (S, P, flip, { top = C.wing2, under = '#eef7f1' } = {}) => {
  const L = Math.hypot(P[0] - S[0], P[1] - S[1]), ang = Math.atan2(P[1] - S[1], P[0] - S[0]), fy = Math.sign(flip || 1) * Math.max(0.08, Math.abs(flip));
  const col = flip >= 0 ? top : under;
  return `<g transform="translate(${f1(S[0])} ${f1(S[1])}) rotate(${f1(ang * 180 / Math.PI)}) scale(${f1(L / WLEN * 1000) / 1000} ${f1(fy * 1000) / 1000}) rotate(${f1(-WANG * 180 / Math.PI)})">
    <path d="${WING}" fill="${col}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>${flip >= 0 ? `<path d="M0 0 C4 -30 -10 -60 -40 -84 C-36 -50 -26 -24 -14 6Z" fill="${C.back}"/>` : ''}
    ${[0, 1, 2, 3, 4, 5, 6].map(i => { const u = i / 6; return `<path d="M${f1(-40 - u * 150)} ${f1(-72 - u * 112)} L${f1(-96 - u * 166)} ${f1(-96 - u * 124)}" stroke="#5f678c" stroke-width="3" opacity=".5" stroke-linecap="round"/>`; }).join('')}</g>`; };
// 05 figure eight: the wing tip really travels the sideways 8, flipping over at each end
export function h05(t) {
  const tf = at('h05', 'The wings sweep'), t8 = at('h05', 'figure eight');
  const cx = 1010, cy = 650, sc = 1.1, rot = -28, S = bpt(cx, cy, sc, rot, ...SHOULDER);
  let s = '';
  if (t < tf - 0.2) { s += placeB(cx, cy, sc, birdSolid() + wings(t, { rate: 1.3, amp: 55, blur: 0 }), { rot });
    s += arrow(1500, 800, 1500, 260, { w: 30, head: 70 }) + arrow(1500, 260, 1500, 800, { w: 30, head: 70 });
    s += fade(1500, 900, 'UP + DOWN?', t, 0.2, { size: 70, fill: N }) + cross(1500, 530, 190, t, 1.0); return s; }
  const ex = S[0] - 30, ey = S[1] - 300, A = 430, B = 180, per = 1.7, u = Math.max(0, t - tf) / per;
  const prog = clamp(u); let d = '';
  for (let i = 0; i <= 160 * prog; i++) { const [x, y] = lem(i / 160 + 0.25, ex, ey, A, B); d += (i ? 'L' : 'M') + f1(x) + ' ' + f1(y); }
  s += `<path d="${d}" stroke="#fff" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>`;
  const P = lem(u + 0.25, ex, ey, A, B), Pn = lem(u + 0.25 + 0.004, ex, ey, A, B), vx = (Pn[0] - P[0]) / (A * 0.025);
  const flip = clamp(vx * 1.6, -1, 1);
  s += placeB(cx, cy, sc, birdSolid(), { rot }) + wingTo(S, P, flip);
  s += `<circle cx="${f1(P[0])}" cy="${f1(P[1])}" r="24" fill="${K.yellow}" stroke="${N}" stroke-width="8"/>`;
  s += arrow(ex + A + 60, ey + 60, ex + A + 230, ey + 60, { col: '#fff', w: 14, head: 40 }) + fade(ex + A + 60, ey - 10, 'FORWARD', t, tf + 0.2, { size: 64, fill: N, anchor: 'start' });
  s += arrow(ex - A - 60, ey + 60, ex - A - 230, ey + 60, { col: '#fff', w: 14, head: 40 }) + fade(ex - A - 60, ey - 10, 'BACK', t, tf + 0.5, { size: 64, fill: N, anchor: 'end' });
  if (Math.abs(flip) < 0.6 && t > tf + 0.3) s += `<g opacity="${f1(1 - Math.abs(flip) / 0.6)}">${big(P[0], P[1] - 75, 'FLIP!', t, -1, { size: 60, fill: K.yellow, stroke: N, sw: 10 })}</g>`;
  s += big(960, 130, 'FIGURE 8', t, t8, { size: 170, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 06 shoulder: x-ray shoulder joint, then a wing blade that twists and pushes air down both ways
export function h06(t) {
  const tt = at('h06', 'twist its wing'), tfw = at('h06', 'on the way forward'), tbk = at('h06', 'on the way back');
  const A = () => { const cx = 1060, cy = 640, sc = 1.7, [sx, sy] = toB(cx, cy, sc, 600, 226);
    let s = placeB(cx, cy, sc, birdInside({}) + wings(0, { still: -30 + 8 * Math.sin(t * 2), blur: 0, bones: 1 }));
    const k = pop(at('h06', 'shoulder'), t);
    if (k > 0) s += `<circle cx="${f1(sx)}" cy="${f1(sy)}" r="${f1(46 * k + 6 * Math.sin(t * 8))}" fill="none" stroke="${K.yellow}" stroke-width="12"/>`;
    s += tag(sx, sy, 520, 220, 'SHOULDER', t, at('h06', 'shoulder') + 0.1, { col: K.yellow });
    return s; };
  const B = () => { // wing seen end-on as a two-tone blade: top white, underside green; the twist flips it over
    const fw = sm(tfw - 0.4, tfw + 0.9, t), bk = sm(tbk - 0.4, tbk + 0.9, t);
    const x = 960 + 330 * fw - 660 * bk;
    const fl = t < tfw - 0.4 ? Math.cos((t - tt) * 2.6) : lerp(1, -1, sm(tbk - 0.7, tbk - 0.1, t));
    let s = `<path d="M240 420 L1680 420" stroke="#fff" stroke-width="6" stroke-dasharray="6 22" stroke-linecap="round" opacity=".7"/>`;
    s += fade(250, 360, 'BACK', t, tt, { size: 70, fill: N, anchor: 'start' }) + fade(1670, 360, 'FORWARD', t, tt, { size: 70, fill: N, anchor: 'end' });
    const tilt = -16 * Math.sign(fl || 1) * Math.min(1, Math.abs(fl) * 2), sy = Math.max(0.12, Math.abs(fl)) * Math.sign(fl || 1);
    const top = 'M-260 0 C-200 -70 180 -58 260 0 Z', bot = 'M-260 0 C-180 34 180 30 260 0 Z';
    s += `<g transform="translate(${f1(x)} 520) rotate(${f1(tilt)}) scale(1.3 ${f1(sy * 130) / 100})"><path d="${top}" fill="#ffffff" stroke="${N}" stroke-width="9" stroke-linejoin="round"/><path d="${bot}" fill="${C.back}" stroke="${N}" stroke-width="9" stroke-linejoin="round"/></g>`;
    // curved twist arrow while flipping
    if (t < tfw - 0.4 || (t > tbk - 0.8 && t < tbk + 0.2)) s += `<path d="M${f1(x - 120)} 400 A140 110 0 0 1 ${f1(x + 120)} 400" fill="none" stroke="${K.yellow}" stroke-width="14" stroke-linecap="round"/><path d="M${f1(x + 150)} 392 L${f1(x + 108)} 372 L${f1(x + 112)} 420Z" fill="${K.yellow}" stroke="${N}" stroke-width="4"/>`;
    // air arrives flat from the side the wing moves towards, hits the tilted blade and is thrown straight down
    if (t > tfw - 0.4) { const dir = t > tbk - 0.4 ? -1 : 1, ak = sm(tfw - 0.4, tfw + 0.2, t) * (t > tbk - 0.7 && t < tbk - 0.2 ? 1 - sm(tbk - 0.7, tbk - 0.5, t) + sm(tbk - 0.4, tbk - 0.2, t) : 1);
      for (let i = 0; i < 3; i++) { const yy = 556 + i * 46, xd = x + dir * (150 - i * 150), R = 80 + i * 36, x0 = x + dir * 980;
        const d = `M${f1(x0)} ${yy} L${f1(xd + dir * R)} ${yy} Q${f1(xd)} ${yy} ${f1(xd)} ${yy + R} L${f1(xd)} 880`;
        s += `<g opacity="${f1(ak)}"><path d="${d}" stroke="#ffffff" stroke-width="22" fill="none" opacity=".3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="${d}" stroke="#ffffff" stroke-width="22" fill="none" stroke-dasharray="50 50" stroke-dashoffset="${f1(-t * 260 - i * 30)}" stroke-linecap="round"/>
          <path d="M${f1(xd - 32)} 856 L${f1(xd + 32)} 856 L${f1(xd)} 916Z" fill="#fff" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g>`; }
    }
    s += t > tbk - 0.4 ? arrow(x + 300, 300, x + 80, 300, { w: 16, col: K.yellow }) : t > tfw - 0.4 ? arrow(x - 300, 300, x - 80, 300, { w: 16, col: K.yellow }) : '';
    s += t < tbk ? fade(960, 1000, 'AIR DOWN', t, tfw, { size: 100, fill: '#fff', stroke: N, sw: 14 }) : big(960, 1000, 'AIR DOWN AGAIN', t, tbk, { size: 100, fill: '#fff', stroke: N, sw: 14 });
    s += big(960, 150, 'TWIST!', t, tt, { size: 150, fill: K.yellow, stroke: N, sw: 18 });
    return s; };
  return t < tt - 0.5 ? A() : xfade(t, tt - 0.5, 0.6, A, B);
}

// 07 hover / backward / upside down
export function h07(t) {
  const th = at('h07', 'hover'), tb = at('h07', 'backwards'), tu = at('h07', 'upside down');
  const A = () => fly(960, 660 + bobB(t), 1.2, t, { rate: 7, amp: 55 }) + big(960, 130, 'NO OTHER BIRD', t, 0.5, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  const B = () => { let s = '';
    const cols = [[340, 'HOVER', th], [960, 'BACKWARD', tb], [1580, 'UPSIDE DOWN', tu]];
    for (const [x, w, t0] of cols) { const k = pop(t0 - 0.2, t); if (k <= 0) { s += `<rect x="${x - 290}" y="200" width="580" height="680" rx="40" fill="#fff" opacity=".25"/>`; continue; }
      s += `<g transform="translate(${x} 540) scale(${f1(k * 100) / 100}) translate(${-x} -540)">${card(x - 290, 200, 580, 680, '#fff', 0.92)}`;
      if (w === 'HOVER') { s += `<circle cx="${x}" cy="520" r="200" fill="none" stroke="${K.yellow}" stroke-width="8" stroke-dasharray="10 18"/>` + fly(x, 540 + bobB(t, 4, 3), 0.55, t, { rate: 7, amp: 50 }); }
      if (w === 'BACKWARD') { const u = ((t - tb) * 0.5) % 1, bx = x + 120 - 240 * u; s += arrow(x + 150, 330, x - 150, 330, { col: K.red, w: 16 }) + fly(bx, 580, 0.55, t, { rate: 7, amp: 50 }); }
      if (w === 'UPSIDE DOWN') { const r = 180 * sm(tu, tu + 0.8, t); s += fly(x, 560, 0.55, t, { rate: 7, amp: 50, rot: r }) + `<path d="M${x - 150} 330 A150 150 0 0 1 ${x + 150} 330" fill="none" stroke="${K.red}" stroke-width="12"/>`; }
      s += `<text x="${x}" y="830" font-family="Black" font-size="${w.length > 9 ? 64 : 76}" fill="${N}" text-anchor="middle">${w}</text></g>`; }
    return s; };
  return t < th - 0.6 ? A() : xfade(t, th - 0.6, 0.5, A, B);
}

// 08 chest opens: flight muscle glows, a pie shows one quarter
export function h08(t) {
  const to = at('h08', 'open the chest'), tm = at('h08', 'flight muscles'), tq = at('h08', 'a quarter');
  const cx = lerp(960, 760, sm(tq - 0.4, tq + 0.4, t)), cy = 560, sc = 1.45, [mx, my] = toB(cx, cy, sc, 660, 330);
  const r = 900 * eo(to, to + 1.0, t), id = 'rv8';
  let s = placeB(cx, cy, sc, birdSolid() + wings(0, { still: -35, blur: 0 }));
  if (r > 0) s += `<defs><clipPath id="${id}"><circle cx="${f1(mx)}" cy="${f1(my)}" r="${f1(r)}"/></clipPath></defs><g clip-path="url(#${id})">${placeB(cx, cy, sc, birdInside({ glow: t > tm ? 'muscle' : null }) + wings(0, { still: -35, blur: 0, bones: 1 }))}</g>`;
  s += tag(mx + 20, my + 40, cx - 200, 990, 'MUSCLE', t, tm + 0.1, { col: '#9e2a44', txt: '#fff' });
  const k = pop(tq, t);
  if (k > 0) { const px = 1520, py = 520, R = 220 * k;
    s += `<circle cx="${px}" cy="${py}" r="${f1(R)}" fill="#fff" stroke="${N}" stroke-width="10"/><path d="M${px} ${py} L${px} ${f1(py - R)} A${f1(R)} ${f1(R)} 0 0 1 ${f1(px + R)} ${py}Z" fill="#9e2a44" stroke="${N}" stroke-width="10" stroke-linejoin="round"/>`;
    s += big(px, py + 330, '1/4', t, tq + 0.2, { size: 150, fill: '#fff', stroke: N, sw: 18 }); }
  s += big(960, 150, 'POWER', t, 0.3, { size: 150, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 09 heart: x-ray heart pumping, then a giant heart at 1,200 bpm vs your 70
export function h09(t) {
  const th = at('h09', 'huge'), t12 = at('h09', 'twelve hundred'), ty = at('h09', 'Yours');
  const A = () => { const z = eo(0, 1.2, t), cx = lerp(960, 700, z), cy = lerp(560, 540, z), sc = lerp(1.4, 2.3, z);
    const hk = 1 + (t > th ? 0.5 * sm(th, th + 0.5, t) : 0) + 0.12 * Math.max(0, Math.sin(t * 12));
    const P = toB(cx, cy, sc, ...PT.heart);
    return placeB(cx, cy, sc, birdInside({ heartK: hk, glow: 'heart' })) + tag(...P, 1560, 500, 'HEART', t, at('h09', 'the heart'), { col: K.red, txt: '#fff' }) + big(1560, 720, 'HUGE!', t, th, { size: 130, fill: '#fff', stroke: N, sw: 16 }); };
  const B = () => { const beat = 1 + 0.16 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 5)), 3);
    let s = birdHeart(480, 450, 4.2, beat);
    s += ecg(120, 900, 800, t, 5, { amp: 90 });
    s += readout(480, 960, count(1200, t, t12, 1.4), 'BEATS A MINUTE', { size: 110 });
    if (t > ty - 0.3) { const k = sm(ty - 0.3, ty + 0.3, t), sb = 1 + 0.12 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.17)), 3);
      s += `<g opacity="${f1(k)}"><path d="M960 160 L960 1000" stroke="#fff" stroke-width="8" stroke-dasharray="4 22" stroke-linecap="round"/>${kid(1440, 760, 1.25)}${heartIcon(1440, 590, 0.34 * sb)}${ecg(1080, 1820, 870, t, 1.17, { amp: 70, col: '#fff', w: 8 })}${readout(1440, 1000, '70', '', { size: 110 })}
        <text x="1440" y="250" font-family="Black" font-size="90" fill="${N}" text-anchor="middle">YOU</text></g>`; }
    return s; };
  return t < t12 - 0.5 ? A() : xfade(t, t12 - 0.5, 0.5, A, B);
}

// lungs pair (front view), k = inflation 0..1
const lungs = (x, y, s, k) => { const L = (sgn) => `<g transform="scale(${sgn} 1)"><path d="M20 -120 C60 -140 120 -100 140 -20 C160 60 150 140 110 160 C80 172 40 150 26 120 C14 60 12 -40 20 -120Z" fill="${C.lung}" stroke="${N}" stroke-width="9"/>
    <path d="M24 -80 C60 -60 80 -20 96 30 M40 30 C70 60 90 90 100 130" stroke="#d9667f" stroke-width="6" fill="none" stroke-linecap="round"/>${[[70, -40], [100, 40], [60, 90], [110, 100], [80, 0]].map(([a, b]) => `<circle cx="${a}" cy="${b}" r="8" fill="#d9667f"/>`).join('')}</g>`;
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * (1 + 0.1 * k) * 1000) / 1000} ${f1(s * (1 + 0.16 * k) * 1000) / 1000})"><path d="M0 -230 L0 -120 M0 -120 C-10 -110 -20 -110 -24 -100 M0 -120 C10 -110 20 -110 24 -100" stroke="#cfe8ff" stroke-width="22" fill="none" stroke-linecap="round"/><path d="M0 -230 L0 -120" stroke="${N}" stroke-width="6" stroke-dasharray="8 10"/>${L(-1)}${L(1)}</g>`; };
// 10 fast breathing
export function h10(t) {
  const tr = at('h10', 'Even resting'), tn = at('h10', 'two hundred and fifty');
  const br = (Math.sin(t * Math.PI * 2 * 3.2) + 1) / 2;
  let s = branch(160, 900, 890) + perched(560, 760, 0.95, { puff: 0.25 * br });
  s += lungs(1400, 470, 1.3, br);
  s += fade(560, 220, 'RESTING', t, tr, { size: 90, fill: N });
  if (t > tn - 0.2) s += readout(1400, 900, count(250, t, tn - 0.2, 1.2), 'BREATHS A MINUTE', { size: 130 });
  return s;
}

// 11 engine: energy gauge pegged in the red, then the fuel gauge drops fast
export function h11(t) {
  const te = at('h11', 'tiny engine'), tf = at('h11', 'needs a lot of fuel');
  const cx = 640, cy = 660, sc = 1.15;
  let s = placeB(cx, cy + bobB(t), sc, birdInside({ heartK: 1 + 0.15 * Math.max(0, Math.sin(t * 14)), glow: 'heart' }) + wings(t, { rate: 7, amp: 50, blur: 3, bones: 1 }));
  const shake = 0.02 * Math.sin(t * 40);
  const gx = 1460, gy = 540;
  if (t < tf - 0.4) s += gauge(gx, gy, 230, lerp(0.15, 0.97, eo(0.2, 1.4, t)) + shake, { lab: 'ENERGY', lo: '', hi: '' });
  else { const k = sm(tf - 0.4, tf + 0.1, t), v = lerp(0.95, 0.06, eo(tf, tf + 2.2, t)), blink = v < 0.25 && Math.sin(t * 12) > 0;
    s += `<g opacity="${f1(k)}">${gauge(gx, gy, 230, v, { lab: 'FUEL', lo: 'E', hi: 'F', red: 0.25, rev: 1 })}</g>`;
    if (blink) s += `<circle cx="${gx}" cy="${gy}" r="290" fill="none" stroke="${K.red}" stroke-width="16"/>`; }
  s += big(1460, 950, 'FULL SPEED', t, te, { size: 110, fill: '#fff', stroke: N, sw: 16 });
  s += big(960, 120, 'FASTEST ENGINE', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 18 });
  return s;
}
