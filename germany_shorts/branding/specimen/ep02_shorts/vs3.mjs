// vertical scenes for the hummingbird shorts b07-b09 (see vs1.mjs for the conventions)
import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from '/tmp/claude-0/hb2/tl.mjs';
import { birdSolid, wings, placeB, fly, onBranch, standing, ground, branch, coin, scale, bee, arrow, bobB, photo } from '/tmp/claude-0/hb2/ha.mjs';
import { proj, landPath } from '/tmp/claude-0/hb2/maps.mjs';
import { nest, walnut, chick, bean, mapCard, label, sparkleS } from '/tmp/claude-0/hb2/s3.mjs';
import { hat, N } from './vs1.mjs';

// flat ground with soil and grass, top at y, filling down to the bottom of the 9:16 frame
const groundV = (y, t = 0) => { let s = `<path d="M-40 ${y} L1120 ${y} L1120 1960 L-40 1960Z" fill="#c99a62" stroke="${N}" stroke-width="8"/><path d="M-40 ${y + 26} L1120 ${y + 26}" stroke="#b5864f" stroke-width="10" opacity=".6"/>`;
  seed(7); for (let i = 0; i < 30; i++) { const x = rnd() * 1080, yy = y + 50 + rnd() * 600; s += `<ellipse cx="${f1(x)}" cy="${f1(yy)}" rx="${f1(10 + rnd() * 16)}" ry="${f1(6 + rnd() * 6)}" fill="#a97a45" opacity=".7"/>`; }
  for (let x = -20; x < 1120; x += 26) { const h = 22 + 14 * Math.sin(x * 0.37), sw = 4 * Math.sin(t * 2 + x * 0.05); s += `<path d="M${x} ${y + 4} Q${f1(x + 4 + sw)} ${f1(y - h * 0.5)} ${f1(x + 8 + sw)} ${f1(y - h)}" stroke="#3f9a45" stroke-width="7" fill="none" stroke-linecap="round"/>`; }
  return s; };
const bub = (bx, by, R, k, body, id) => k <= 0 ? '' : `<g transform="translate(${bx} ${by}) scale(${f1(k * 100) / 100})"><defs><clipPath id="${id}"><circle r="${R}"/></clipPath></defs><circle r="${R + 12}" fill="${N}"/><circle r="${R}" fill="#fff4dc"/><g clip-path="url(#${id})">${body}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="8"/></g>`;
const silkBody = () => { let b = `<rect x="-160" y="-160" width="320" height="320" fill="#5e6e86"/>`;
  for (let i = 0; i < 9; i++) b += `<path d="M-160 ${-120 + i * 30} C-60 ${-90 + i * 30} 40 ${-150 + i * 34} 160 ${-110 + i * 32}" stroke="#ffffff" stroke-width="5" fill="none"/><path d="M-160 ${-120 + i * 30} C-60 ${-90 + i * 30} 40 ${-150 + i * 34} 160 ${-110 + i * 32}" stroke="#9fb3c8" stroke-width="2" fill="none" stroke-dasharray="2 10"/>`;
  for (let i = 0; i < 7; i++) b += `<path d="M${-120 + i * 40} -160 L${-100 + i * 36} 160" stroke="#ffffff" stroke-width="3" opacity=".8"/>`;
  return b + sparkleS(-40, -20, 18) + sparkleS(60, 50, 14); };
const fluffBody = () => { let b = ''; seed(5); for (let i = 0; i < 9; i++) { const x = -110 + rnd() * 220, y = -90 + rnd() * 180; for (let j = 0; j < 12; j++) { const a = j / 12 * Math.PI * 2; b += `<path d="M${f1(x)} ${f1(y)} q${f1(Math.cos(a) * 20)} ${f1(Math.sin(a) * 20 - 8)} ${f1(Math.cos(a) * 40)} ${f1(Math.sin(a) * 40)}" stroke="#d8cfbc" stroke-width="3" fill="none"/>`; } b += `<circle cx="${f1(x)}" cy="${f1(y)}" r="6" fill="#a8916a"/>`; } return b; };

// ───────── b07 SILK NEST ─────────
const b07h = t => { const ts = hat('b07', 'spider silk'), sk = sm(ts - 0.1, ts + 1.0, t), fl = Math.sin(t * 5);
  let s = branch(-40, 1120, 1290, 34) + nest(560, 1170, 1.9, { fluff: 1, silk: Math.max(0.15, sk) });
  s += placeB(310 + 6 * fl, 760 + 10 * fl, 0.7, birdSolid() + wings(t, { rate: 9, amp: 50 }));
  const k = pop(ts, t);
  s += bub(810, 720, 150, k, silkBody(), 'sb7h') + fade(810, 925, 'SPIDER SILK', t, ts + 0.1, { size: 64, fill: '#fff', stroke: N, sw: 12 });
  return s; };
const b07a = t => { const tw = at('h27', 'half a walnut'), tf = at('h27', 'soft plant fluff'), tsk = at('h27', 'spider silk'), tst = at('h27', 'The silk stretches');
  const fl = sm(tf - 0.2, tf + 0.8, t), sk = sm(tsk - 0.2, tsk + 1.0, t), grow = sm(tst, tst + 2.4, t);
  let s = branch(-40, 1120, 1290, 34), inner = '';
  if (grow > 0) for (const i of [-1, 1]) inner += chick(i * (44 + 26 * grow) / (1 + 0.3 * grow), -70 - 8 * grow, 30 + 22 * grow, 0);
  s += nest(540, 1170, 1.9, { fluff: 1, silk: Math.max(0.3, sk), wide: 1 + 0.3 * grow, inner });
  if (t < tf - 0.1) { const k = sm(tw - 0.5, tw - 0.1, t) * (1 - sm(tf - 0.6, tf - 0.1, t)); s += `<g opacity="${f1(k)}">${walnut(540, 690, 1.4)}${label(540, 840, 'HALF A WALNUT', 64)}<text x="540" y="955" font-family="Black" font-size="100" fill="${N}" text-anchor="middle">=</text></g>`; }
  const fb = pop(tf + 0.1, t) * (1 - sm(tsk - 0.3, tsk, t));
  if (fb > 0) s += bub(540, 690, 160, fb, fluffBody(), 'fb7') + fade(540, 905, 'PLANT FLUFF', t, tf + 0.2, { size: 64, fill: '#fff', stroke: N, sw: 12 });
  const sb = pop(tsk + 0.1, t) * (1 - sm(tst - 0.3, tst, t));
  if (sb > 0) s += bub(540, 690, 160, sb, silkBody(), 'sb7') + fade(540, 905, 'SPIDER SILK', t, tsk + 0.2, { size: 64, fill: '#fff', stroke: N, sw: 12 });
  if (t > tst) s += arrow(220, 1490, 60, 1490, { w: 16 }) + arrow(860, 1490, 1020, 1490, { w: 16 }) + fade(540, 1500, 'STRETCHES', t, tst + 0.3, { size: 76, fill: '#fff', stroke: N, sw: 12 });
  return s; };
const b07b = t => { const tj = at('h28', 'jelly bean'), tm = at('h28', 'The mother raises');
  const A = () => { let s = branch(-40, 1120, 1320, 32, { leaves: 0 });
    let eggs = ''; for (const [x, y, r] of [[-38, -66, -10], [40, -64, 12]]) eggs += `<ellipse cx="${x}" cy="${y}" rx="28" ry="38" transform="rotate(${r} ${x} ${y})" fill="#fffdf6" stroke="${N}" stroke-width="4"/><ellipse cx="${x - 8}" cy="${y - 14}" rx="7" ry="11" fill="#fff" transform="rotate(${r} ${x} ${y})"/>`;
    s += nest(540, 1210, 1.9, { inner: eggs });
    s += big(540, 590, '2 EGGS', t, 0.2, { size: 120, fill: '#fff', stroke: N, sw: 14 });
    if (t > tj - 0.3) { const k = pop(tj - 0.3, t); s += `<g transform="translate(540 800) scale(${f1(k * 100) / 100})">${bean(-80, 0, -24, '#ff4f7b')}${bean(80, 6, 18, '#7a5bff')}</g>` + label(540, 950, 'JELLY BEANS', 64); }
    const nk = t < tj - 0.2 ? pop(0.3, t) * (1 - sm(tj - 0.6, tj - 0.2, t)) : 0;
    s += photo('nest', 540, 1020, 640, 640, nk, { rot: 2, cap: 'REAL NEST' });
    return s; };
  const B = () => { let s = branch(-40, 1120, 1350, 32);
    const feed = Math.sin(t * 5), open = 0.5 + 0.5 * Math.max(0, Math.sin(t * 5 + 1));
    s += nest(540, 1240, 1.9, { wide: 1.1, inner: chick(-46, -86, 46, open, 6) + chick(52, -80, 44, 1 - open * 0.6, 2) });
    s += placeB(730 + 6 * feed, 830 + 10 * feed, 0.68, birdSolid({ throat: 0 }) + wings(t, { rate: 9, amp: 50 }), { rot: -40, flip: true });
    s += big(540, 1540, 'SUPER MOM', t, at('h28', 'all by herself'), { size: 120, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tm - 0.3 ? A() : xfade(t, tm - 0.3, 0.5, A, B); };

// ───────── b08 TINIEST BIRD ─────────
const b08h = t => { const sc = lerp(1.3, 0.55, eo(0.15, 2.0, t)), tq = hat('b08', 'get');
  // a real hummingbird photo first (frame 0 full), shrinking, then it hands over to the drawn bird
  const ph = () => photo('ruby', 540, 900, 820, 580, lerp(1, 0.6, eo(0.1, 1.5, t)), { rot: -2, cap: 'RUBY-THROATED' });
  let s = t < 1.3 ? ph() : xfade(t, 1.3, 0.4, ph, () => fly(540, 960 + bobB(t, 8), sc, t, { rate: 7, amp: 55 }));
  s += big(540, 1430, '?', t, tq, { size: 220, fill: K.yellow, stroke: N, sw: 18 });
  return s; };
const scl = (y, txt, k = 1.6) => `<g transform="translate(540 ${y}) scale(${k}) translate(-540 ${-y})">${scale(540, y, txt)}</g>`;
const b08a = (t, lt) => { const tg = at('h02', 'three grams'), tc = at('h02', 'single coin') - 0.3, tr = at('h02', 'ruby-throated');
  const land = eo(0.05, 1.0, lt), bs = 0.42 * 1.6, mv = eo(tc, tc + 0.7, t), pan = lerp(1000, 780, mv), gy = pan - (452 - 300) * bs;
  const bx = lerp(980, 560, land), by = lerp(520, gy, land);
  const rd = t < tg - 0.6 ? '0.0 G' : `${(3 * eo(tg - 0.6, tg + 0.2, t)).toFixed(1)} G`;
  let s = scl(pan, rd);
  s += land < 1 ? fly(bx, by, bs, t, { rate: 7, amp: 50 }) : standing(bx, pan, bs, {});
  if (t < tg - 0.1) s += tag(bx, by - 100, 540, 560, 'RUBY-THROATED', t, tr, { col: '#fff', line: false, size: 64 });
  if (mv > 0) { s += `<g opacity="${f1(mv)}">${scl(1300, '3 G')}${coin(540, 1280, 120)}</g>`;
    s += big(540, 1145, '=', t, tc + 0.4, { size: 140, fill: N }) + fade(870, 1210, 'COIN', t, tc + 0.5, { size: 76, fill: '#fff', stroke: N, sw: 12 }); }
  return s; };
const b08b = t => { const tb = at('h03', "It's called"), tf = at('h03', 'five centimeters'), ts = at('h03', 'The smallest bird');
  const A = () => { const v = { lon0: -88, lon1: -69.5, lat0: 14, lat1: 30, x: 60, y: 470, w: 960, h: 900 }, P = proj(v);
    let s = mapCard(v, 'mc8', true);
    const [x, y] = P(-79.5, 21.8), k = pop(at('h03', 'lives in'), t);
    if (k > 0) s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(110 * k)}" fill="none" stroke="${K.red}" stroke-width="12"/>` + tag(x, y - 110, x, y - 240, 'CUBA', t, at('h03', 'lives in') + 0.1, { col: K.red, txt: '#fff', line: false });
    return s; };
  const B = () => { const cx = 540, cy = 800, sc = 1.05;
    let s = placeB(cx, cy + bobB(t, 6), sc, birdSolid() + wings(t, { rate: 9, amp: 50, blur: 3 }));
    const x0 = cx + (214 - 600) * sc, x1 = cx + (990 - 600) * sc, ry = 1060, rk = eo(tf - 0.2, tf + 0.6, t);
    if (rk > 0) { const xe = lerp(x0, x1, rk); s += `<path d="M${f1(x0)} ${ry} L${f1(xe)} ${ry}" stroke="#fff" stroke-width="10" stroke-linecap="round"/><path d="M${f1(x0)} ${ry - 26} L${f1(x0)} ${ry + 26} M${f1(xe)} ${ry - 26} L${f1(xe)} ${ry + 26}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`; }
    s += big(540, 1140, '5 CM', t, tf + 0.3, { size: 100, fill: N, stroke: '#fff', sw: 16 });
    s += bee(540, 1340, 0.9, t) + tag(540, 1300, 840, 1300, 'BEE', t, tf - 0.2, { col: K.yellow, line: false, size: 60 });
    return s; };
  const p0 = tb + 0.1, p1 = tf - 0.35, pk = t < p1 ? eo(p0, p0 + 0.45, t) : 1 - eo(p1, p1 + 0.35, t), zk = 1 - 0.35 * pk;
  const G = t < tb - 0.3 ? A() : xfade(t, tb - 0.3, 0.5, A, B);
  let s = pk > 0 ? `<g transform="translate(540 960) scale(${f1(zk * 1000) / 1000}) translate(-540 -960)" opacity="${f1(1 - 0.5 * pk)}">${G}</g>` : G;
  s += photo('bee', 540, 940, 900, 600, pk);
  if (pk > 0) s += `<g opacity="${f1(pk)}">${big(540, 1360, 'BEE HUMMINGBIRD', t, p0, { size: 92, fill: '#fff', stroke: N, sw: 14 })}</g>`;
  s += big(540, 1520, 'SMALLEST BIRD', t, ts, { size: 104, fill: K.yellow, stroke: N, sw: 16 });
  return s; };

// ───────── b09 CAN'T WALK ─────────
const b09h = t => { const tw = hat('b09', "can't walk"), tft = hat('b09', 'feet'), GY = 1240;
  const z = eo(tft - 0.1, tft + 0.9, t), Z = lerp(1, 1.4, z), f0 = [540 + (570 - 600) * 1.0, GY], f = [lerp(f0[0], 540, z), lerp(f0[1], 1300, z)];
  const w = 9 * Math.sin(t * 7) * (1 - z);
  let s = `<g transform="translate(${f1(f[0])} ${f1(f[1])}) scale(${f1(Z * 1000) / 1000}) translate(${-f0[0]} ${-f0[1]})">${groundV(GY, t)}${standing(540, GY, 1.0, { lean: -14 + w })}</g>`;
  s += big(540, 620, 'WALK', t, tw - 0.1, { size: 150, fill: '#fff', stroke: N, sw: 18 }) + cross(540, 615, 150, t, tw + 0.3);
  const k = pop(tft, t);
  if (k > 0) s += `<circle cx="${f1(f[0])}" cy="${f1(f[1] - 10)}" r="${f1(150 * k)}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="22 14"/>`;
  return s; };
const b09a = t => { const tt = at('h22', 'tiny'), tg = at('h22', 'holding on'), tw = at('h22', "can't really walk"), tf = at('h22', 'If it wants to move'), tfl = at('h22', 'it flies');
  const A = () => { const z = eo(tt - 0.3, tt + 0.9, t), Z = lerp(1.0, 1.3, z), f0 = [540 + (570 - 600), 1100 - 11 - 4], fx = lerp(f0[0], 520, z), fy = lerp(f0[1], 1180, z);
    let s = `<g transform="translate(${f1(fx)} ${f1(fy)}) scale(${f1(Z * 1000) / 1000}) translate(${-f0[0]} ${-f0[1]})">${branch(-400, 1500, 1100, 22)}${onBranch(540, 1100, 1.0, { th: 22 })}</g>`;
    const k = pop(tt, t); if (k > 0) s += `<circle cx="${f1(fx)}" cy="${f1(fy - 10)}" r="${f1(110 * k)}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="20 14"/>`;
    s += tag(fx + 60, fy + 30, 640, 1420, 'TINY FEET', t, tt + 0.1, { col: K.yellow });
    const g = pop(tg - 0.1, t); if (g > 0) { const bx = 250, byy = 660, R = 150;
      s += `<path d="M${f1(bx + R * 0.72)} ${f1(byy + R * 0.72)} L${f1(fx - 40)} ${f1(fy - 20)}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12" opacity="${f1(Math.min(1, g))}"/>`;
      const arcP = (a0, a1, r) => { let d = ''; for (let i = 0; i <= 16; i++) { const a = (a0 + (a1 - a0) * i / 16) * Math.PI / 180; d += (i ? 'L' : 'M') + f1(Math.cos(a) * r) + ' ' + f1(60 + Math.sin(a) * r); } return d; };
      const claw = (a, r, dir) => { const q = a * Math.PI / 180, x = Math.cos(q) * r, y = 60 + Math.sin(q) * r, tx = -Math.sin(q) * dir, ty = Math.cos(q) * dir; return `<path d="M${f1(x)} ${f1(y)} L${f1(x + tx * 22 - Math.cos(q) * 10)} ${f1(y + ty * 22 - Math.sin(q) * 10)}" stroke="#2a2030" stroke-width="10" stroke-linecap="round"/>`; };
      let b = `<circle cx="0" cy="60" r="78" fill="#8a5a2b" stroke="${N}" stroke-width="9"/><circle cx="0" cy="60" r="54" fill="none" stroke="#a87444" stroke-width="7"/><circle cx="0" cy="60" r="30" fill="none" stroke="#a87444" stroke-width="7"/><circle cx="0" cy="60" r="9" fill="#6e4520"/>`;
      b += `<path d="M-60 -200 L-8 -22" stroke="${N}" stroke-width="30" stroke-linecap="round"/><path d="M-60 -200 L-8 -22" stroke="#3a3348" stroke-width="16" stroke-linecap="round"/>`;
      const toe = (a0, a1, r, dir) => `<path d="${arcP(a0, a1, r)}" stroke="${N}" stroke-width="24" fill="none" stroke-linecap="round"/><path d="${arcP(a0, a1, r)}" stroke="#55506a" stroke-width="11" fill="none" stroke-linecap="round"/>` + claw(a1, r, dir);
      b += toe(-95, 45, 94, 1) + toe(-95, 0, 94, 1) + toe(-95, -200, 94, -1);
      s += `<g transform="translate(${bx} ${byy}) scale(${f1(g * 100) / 100})"><defs><clipPath id="toe9"><circle r="${R}"/></clipPath></defs><circle r="${R + 12}" fill="${N}"/><circle r="${R}" fill="#fff4dc"/><g clip-path="url(#toe9)">${b}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="8"/></g>`;
      s += fade(bx, byy - R - 45, 'GOOD GRIP', t, tg + 0.1, { size: 70, fill: '#fff', stroke: N, sw: 12 }); }
    return s; };
  const GY = 1250, x0 = 330, x1 = 750;
  const B = () => { let s = groundV(GY, t);
    const k = sm(tf - 0.1, tfl + 0.3, t);
    if (k <= 0) { const w = 7 * Math.sin(t * 7); s += standing(x0, GY, 0.9, { lean: -14 + w }); s += big(540, 640, 'WALK', t, tw, { size: 150, fill: '#fff', stroke: N, sw: 18 }) + cross(540, 635, 150, t, tw + 0.4); }
    else if (k >= 1) s += standing(x1, GY, 0.9, {});
    else { const x = lerp(x0, x1, k), y = GY - 152 * 0.9 - 30 - 170 * Math.sin(Math.PI * k); s += fly(x, y, 0.9, t, { rate: 9, amp: 55 });
      for (let i = 1; i <= 3; i++) { const kk = Math.max(0, k - i * 0.07), xx = lerp(x0, x1, kk), yy = GY - 152 * 0.9 - 30 - 170 * Math.sin(Math.PI * kk); s += `<circle cx="${f1(xx - 60)}" cy="${f1(yy + 40)}" r="${f1(9 - i * 2)}" fill="#fff" opacity="${f1(0.6 - i * 0.15)}"/>`; } }
    if (t > tf) { const ax = x0 - 27, bx = x1 - 27, kk = eo(tf, tf + 0.5, t);
      s += `<g opacity="${f1(kk)}"><path d="M${f1(ax)} 1350 L${f1(bx)} 1350" stroke="#fff" stroke-width="10" stroke-linecap="round"/><path d="M${f1(ax)} 1325 L${f1(ax)} 1375 M${f1(bx)} 1325 L${f1(bx)} 1375" stroke="#fff" stroke-width="10" stroke-linecap="round"/></g>`;
      s += fade(540, 1440, 'A FEW CM', t, tf + 0.2, { size: 70, fill: N });
      s += big(540, 640, 'IT FLIES!', t, tfl, { size: 140, fill: K.yellow, stroke: N, sw: 16 }); }
    return s; };
  return t < tw - 0.4 ? A() : xfade(t, tw - 0.4, 0.5, A, B); };

export const VS3 = { b07: [b07h, b07a, b07b], b08: [b08h, b08a, b08b], b09: [b09h, b09a] };
