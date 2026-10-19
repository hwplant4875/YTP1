import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross, esc, ICON } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from './tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, fly, perched, branch, flowerT, blossom, heartIcon, birdHeart, gauge, readout, card, ecg, arrow, bobB, timer } from './ha.mjs';
const N = K.navy;

// 12 fuel = flowers; then a big x-ray head shows the long tongue inside the beak
export function h12(t) {
  const tf = at('h12', 'Flowers'), tl = at('h12', "Let's look inside"), tt = at('h12', 'very long tongue');
  const A = () => { const k = eo(tf - 0.2, tf + 1.2, t), cx = lerp(560, 760, k), cy = lerp(520, 600, k), sc = 1.0;
    let s = '';
    if (t > tf - 0.8) s += `<g opacity="${f1(sm(tf - 0.8, tf - 0.3, t))}">${flowerT(1290, 560, 1.5, { rot: -62 })}</g>`;
    s += fly(cx, cy + bobB(t, 6), sc, t, { rate: 7, amp: 55, rot: 8 });
    s += big(960, 150, 'FUEL?', t, 0.3, { size: 160, fill: '#fff', stroke: N, sw: 18 });
    s += big(1500, 900, 'FLOWERS', t, tf, { size: 120, fill: K.yellow, stroke: N, sw: 16 });
    return s; };
  const B = () => { const cx = 380, cy = 560, sc = 2.6, ext = eo(tt - 0.2, tt + 0.8, t) * 1.6;
    let s = placeB(cx, cy, sc, birdInside({ tongue: ext, glow: t > tt ? 'hyoid' : null }));
    const [tx, ty] = toB(cx, cy, sc, 990 + ext * 40, 199);
    s += tag(tx - 200, ty, 1500, 820, 'TONGUE', t, tt + 0.3, { col: K.yellow });
    s += big(1300, 170, 'INSIDE THE BEAK', t, tl + 0.4, { size: 110, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tl + 0.2 ? A() : xfade(t, tl + 0.2, 0.6, A, B);
}

// one prong of the forked tongue, pointing down from (x, y0) to y1; side = -1 left, +1 right; op = flap opening 0..1; wet = nectar held 0..1
const prong = (x, y0, y1, side, op, wet) => {
  let s = `<path d="M${f1(x)} ${f1(y0)} L${f1(x)} ${f1(y1)}" stroke="${C.tongue}" stroke-width="50" stroke-linecap="round"/><path d="M${f1(x - side * 6)} ${f1(y0 + 20)} L${f1(x - side * 6)} ${f1(y1 - 10)}" stroke="#ffb3c6" stroke-width="7" stroke-linecap="round" opacity=".7"/>`;
  const n = 9;
  for (let i = 0; i < n; i++) { const yy = lerp(y0 + 60, y1 - 4, i / (n - 1)), a = lerp(12, 70, op) * Math.PI / 180, L = 84;
    const ex = x + side * (22 + Math.sin(a) * L), ey = yy - Math.cos(a) * L;
    if (wet > 0) s += `<ellipse cx="${f1(x + side * 44)}" cy="${f1(yy - 30)}" rx="${f1(22 * wet)}" ry="${f1(30 * wet)}" fill="#ffc83a" opacity=".95"/>`;
    s += `<path d="M${f1(x + side * 20)} ${f1(yy)} Q${f1(x + side * (22 + Math.sin(a) * L * 0.6))} ${f1(yy - 14)} ${f1(ex)} ${f1(ey)}" stroke="#ff8fae" stroke-width="12" fill="none" stroke-linecap="round"/>`; }
  return s; };
// 13 forked tongue dips into nectar, fringes open, snap shut and pull it back
export function h13(t) {
  const tsp = at('h13', 'split in two'), td = at('h13', 'dips into nectar'), to = at('h13', 'open up'), tsh = at('h13', 'snap shut'), tb = at('h13', 'pull it back');
  const split = eo(tsp - 0.2, tsp + 0.6, t), dip = sm(td - 0.3, td + 0.5, t) * (1 - sm(tb - 0.1, tb + 0.8, t));
  const op = sm(to - 0.1, to + 0.5, t) * (1 - sm(tsh - 0.1, tsh + 0.25, t)), wet = t > tsh - 0.1 ? sm(tsh - 0.1, tsh + 0.3, t) : 0;
  const surf = 760;
  let s = '';
  // flower tube cross-section with nectar at the bottom
  s += `<path d="M560 0 L560 1080 M1360 0 L1360 1080" stroke="${N}" stroke-width="12"/><rect x="566" y="0" width="788" height="1080" fill="#ff7f97" opacity=".35"/>`;
  let wv = `M566 ${surf}`; for (let x = 566; x <= 1354; x += 20) wv += ` L${x} ${f1(surf + 8 * Math.sin(x / 40 + t * 3))}`;
  s += `<path d="${wv} L1354 1080 L566 1080Z" fill="#ffc83a" stroke="${N}" stroke-width="6"/>`;
  // beak tip at the top
  s += `<path d="M900 -20 L1020 -20 L978 120 L942 120Z" fill="${C.beak}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  const fork = 400 + 240 * dip, tip = 660 + 260 * dip, sep = 110 * split;
  s += `<path d="M960 60 L960 ${f1(fork)}" stroke="${C.tongue}" stroke-width="60" stroke-linecap="round"/>`;
  s += prong(960 - sep, fork, tip, -1, op, wet) + prong(960 + sep, fork, tip, 1, op, wet);
  // nectar surface over the dipped part (semi-transparent so you still see the fringes)
  if (dip > 0.05) s += `<path d="${wv} L1354 1080 L566 1080Z" fill="#ffc83a" opacity=".35"/>`;
  s += big(960, 140, 'FORKED TONGUE', t, tsp, { size: 120, fill: '#fff', stroke: N, sw: 16 });
  s += tag(1340, 900, 1640, 900, 'NECTAR', t, td, { col: K.yellow, line: false });
  s += tag(960 + sep + 100, (fork + tip) / 2, 1640, 520, 'BRUSHES', t, to + 0.1, { col: '#fff' });
  if (t > tsh) s += big(330, 520, 'SNAP!', t, tsh, { size: 120, fill: K.yellow, stroke: N, sw: 14, rot: -8 });
  if (t > tb) s += arrow(330, 860, 330, 640, { w: 22, head: 60 });
  return s;
}

// 14 fifteen licks a second: x-ray head drinking from a see-through flower
export function h14(t) {
  const tn = at('h14', 'fifteen licks');
  const cx = 520, cy = 600, sc = 2.2, lick = (Math.sin(t * Math.PI * 2 * 4) + 1) / 2;
  let s = placeB(cx, cy, sc, birdInside({ tongue: 0.6 + 1.4 * lick }));
  const [bx, by] = toB(cx, cy, sc, 990, 199);
  s += `<g opacity=".75">${flowerT(bx - 20, by, 1.6, { rot: -90, stem: 0 })}</g>`;
  if (t > tn - 0.3) s += readout(1580, 840, count(15, t, tn - 0.3, 0.8), 'LICKS A SECOND', { size: 200 });
  const a = (t * 2) % 1 * Math.PI * 2;
  s += `<g transform="translate(1110 820) scale(0.85)"><circle r="120" fill="#fff" stroke="${N}" stroke-width="10"/><rect x="-24" y="-160" width="48" height="34" rx="8" fill="${N}"/><path d="M0 0 L${f1(Math.sin(a) * 90)} ${f1(-Math.cos(a) * 90)}" stroke="${K.red}" stroke-width="12" stroke-linecap="round"/><circle r="12" fill="${N}"/></g>`;
  s += big(960, 120, 'FAST!', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  return s;
}

// balance beam: left load / right load drawn by callbacks at pan centres; ang in degrees (positive = right side down)
const balance = (cx, cy, ang, L, R) => { const a = ang * Math.PI / 180, w = 520, lx = cx - Math.cos(a) * w, ly = cy - Math.sin(a) * w, rx = cx + Math.cos(a) * w, ry = cy + Math.sin(a) * w;
  const pan = (x, y, inner) => `<path d="M${f1(x)} ${f1(y)} L${f1(x - 150)} ${f1(y + 190)} M${f1(x)} ${f1(y)} L${f1(x + 150)} ${f1(y + 190)}" stroke="${N}" stroke-width="6"/>${inner(x, y + 190)}<path d="M${f1(x - 190)} ${f1(y + 190)} Q${f1(x)} ${f1(y + 260)} ${f1(x + 190)} ${f1(y + 190)}Z" fill="#fff" stroke="${N}" stroke-width="9"/>`;
  return `<path d="M${cx} ${cy} L${cx - 120} ${cy + 520} L${cx + 120} ${cy + 520}Z" fill="${N}"/><path d="M${f1(lx)} ${f1(ly)} L${f1(rx)} ${f1(ry)}" stroke="${N}" stroke-width="24" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="22" fill="${K.yellow}" stroke="${N}" stroke-width="7"/>` + pan(lx, ly, L) + pan(rx, ry, R); };
const drop = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M0 -150 C40 -90 100 -30 100 30 C100 90 55 130 0 130 C-55 130 -100 90 -100 30 C-100 -30 -40 -90 0 -150Z" fill="#ffc83a" stroke="${N}" stroke-width="9"/><path d="M-50 20 C-56 50 -40 80 -16 90" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" opacity=".6"/></g>`;
// 15 hundreds to thousands of flowers a day; then a balance: nectar outweighs the bird
export function h15(t) {
  const th = at('h15', 'thousands'), tw = at('h15', 'And in one day');
  const A = () => { let s = ''; const n = 40, prog = eo(0.2, th + 1.6, t) * n;
    seed(5); const pts = []; for (let i = 0; i < n; i++) pts.push([160 + (i % 10) * 175 + rnd() * 50, 380 + Math.floor(i / 10) * 175 + rnd() * 40, ['#ff5f87', '#ff3d5e', '#b26bff', '#ffd23a', '#ffffff'][i % 5]]);
    pts.forEach(([x, y, c], i) => { s += blossom(x, y, 56, c, pop(i * (th + 1.4) / n + 0.2, t, 0.35)); });
    const i = Math.min(n - 1, Math.floor(prog)), [x, y] = pts[i], [x2, y2] = pts[Math.min(n - 1, i + 1)], f = prog - Math.floor(prog);
    s += fly(lerp(x, x2, f) - 170, lerp(y, y2, f) - 60, 0.38, t, { rate: 7, amp: 50 });
    const v = Math.round(lerp(0, 1000, eo(0.2, th + 1.6, t)));
    s += readout(960, 200, v >= 1000 ? '1,000+' : v.toLocaleString('en-US'), '', { size: 150 });
    s += fade(960, 300, 'FLOWERS A DAY', t, 0.5, { size: 70, fill: N });
    return s; };
  const B = () => { const tb = at('h15', 'body weight'), ang = lerp(0, 12, eo(tb, tb + 1.0, t));
    let s = balance(960, 380, ang, (x, y) => perched(x, y - 100, 0.42, {}), (x, y) => drop(x, y - 120, 0.9));
    s += fade(1480, 860, 'NECTAR', t, tb + 0.4, { size: 80, fill: N });
    s += big(960, 130, 'MORE THAN ITS WEIGHT', t, tb + 0.6, { size: 110, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tw - 0.3 ? A() : xfade(t, tw - 0.3, 0.5, A, B);
}

const sugar = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M0 -110 L110 -55 L0 0 L-110 -55Z" fill="#ffffff" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><path d="M-110 -55 L0 0 L0 120 L-110 65Z" fill="#e9eef6" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><path d="M110 -55 L0 0 L0 120 L110 65Z" fill="#d3dbe8" stroke="${N}" stroke-width="8" stroke-linejoin="round"/>${[[-40, -60], [30, -50], [-60, 20], [50, 40], [-30, 60]].map(([a, b]) => `<rect x="${a}" y="${b}" width="8" height="8" fill="#b8c3d6"/>`).join('')}</g>`;
const gnat = (x, y, s, t) => { const w = 20 * Math.sin(t * 50); return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><ellipse cx="-6" cy="-24" rx="30" ry="14" transform="rotate(${f1(-20 + w)} -6 -10)" fill="#fff" opacity=".8" stroke="${N}" stroke-width="4"/><ellipse cx="0" cy="0" rx="36" ry="16" fill="#3a3a4a" stroke="${N}" stroke-width="5"/><circle cx="36" cy="-4" r="13" fill="#3a3a4a" stroke="${N}" stroke-width="5"/><circle cx="42" cy="-8" r="4" fill="#ff5a4f"/><path d="M-10 14 L-18 34 M6 14 L2 36 M20 12 L24 32" stroke="${N}" stroke-width="4"/></g>`; };
const spider = (x, y, s) => { let l = ''; for (let i = 0; i < 4; i++) { const a = (-50 + i * 34) * Math.PI / 180, c = Math.cos(a), si = Math.sin(a);
    l += `<path d="M0 0 Q${f1(c * 60)} ${f1(si * 60 - 30)} ${f1(c * 90)} ${f1(si * 90 + 10)}" stroke="${N}" stroke-width="6" fill="none"/><path d="M0 0 Q${f1(-c * 60)} ${f1(si * 60 - 30)} ${f1(-c * 90)} ${f1(si * 90 + 10)}" stroke="${N}" stroke-width="6" fill="none"/>`; }
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M0 -40 L0 -400" stroke="#fff" stroke-width="3"/>${l}<ellipse cx="0" cy="0" rx="34" ry="30" fill="#5a3a2a" stroke="${N}" stroke-width="5"/><circle cx="0" cy="-36" r="18" fill="#5a3a2a" stroke="${N}" stroke-width="5"/><circle cx="-6" cy="-40" r="4" fill="#fff"/><circle cx="6" cy="-40" r="4" fill="#fff"/></g>`; };
const bricks = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})">${[[-110, 0], [0, 0], [110, 0], [-55, -70], [55, -70], [0, -140]].map(([a, b]) => `<rect x="${a - 52}" y="${b - 32}" width="104" height="64" rx="8" fill="#e06a4a" stroke="${N}" stroke-width="7"/>`).join('')}</g>`;
// 16 sugar is not enough: bird snaps up gnats and a spider; then SUGAR = ENERGY, BUGS = BUILDING
export function h16(t) {
  const ti = at('h16', 'tiny insects'), tsp = at('h16', 'spiders'), te = at('h16', 'Sugar for energy');
  const A = () => { let s = '';
    if (t < ti - 0.4) { s += sugar(960, 560, 1.6); s += big(960, 160, 'SUGAR ONLY?', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 }); s += cross(960, 580, 260, t, at('h16', "isn't enough")); return s; }
    const k = sm(ti - 0.4, ti, t), u = clamp((t - ti + 0.4) / 2.2), bx = lerp(260, 1150, eo(0, 1, u)), by = 560 + 80 * Math.sin(u * 6);
    s += `<g opacity="${f1(k)}">`;
    seed(3); for (let i = 0; i < 6; i++) { const gx = 700 + rnd() * 900 + 30 * Math.sin(t * 3 + i), gy = 300 + rnd() * 500 + 20 * Math.cos(t * 4 + i); if (bx + 380 < gx || i > 2) s += gnat(gx, gy, 0.9, t + i); }
    if (t > tsp - 0.3) s += `<g opacity="${f1(sm(tsp - 0.3, tsp, t))}">${spider(1580, 420 + 10 * Math.sin(t * 2), 1.2)}</g>`;
    s += fly(bx, by, 0.75, t, { rate: 7, amp: 55 }) + `</g>`;
    s += big(960, 140, 'BUGS TOO!', t, ti, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    if (t > tsp) s += tag(1580, 380, 1580, 200, 'SPIDER', t, tsp, { col: '#fff', line: false, size: 60 });
    return s; };
  const B = () => { const tb = at('h16', 'bugs for building');
    let s = card(200, 200, 700, 760, '#fff', 0.92) + card(1020, 200, 700, 760, '#fff', 0.92);
    s += sugar(550, 420, 1.0) + `<g transform="translate(550 700) scale(0.9)">${ICON.bolt()}</g>` + `<text x="550" y="910" font-family="Black" font-size="84" fill="${N}" text-anchor="middle">ENERGY</text>`;
    if (t < tb) s += `<text x="1370" y="640" font-family="Black" font-size="260" fill="${N}" opacity="${f1(0.25 * (1 - sm(tb - 0.3, tb, t)))}" text-anchor="middle">?</text>`;
    if (t > tb - 0.3) { const k = sm(tb - 0.3, tb + 0.1, t); s += `<g opacity="${f1(k)}">${gnat(1370, 400, 2.0, t)}${bricks(1370, 720, 1.0)}<text x="1370" y="910" font-family="Black" font-size="84" fill="${N}" text-anchor="middle">BUILDING</text></g>`; }
    s += big(550, 130, 'SUGAR', t, te, { size: 100, fill: '#fff', stroke: N, sw: 14 }) + big(1370, 130, 'BUGS', t, tb, { size: 100, fill: '#fff', stroke: N, sw: 14 });
    return s; };
  return t < te - 0.3 ? A() : xfade(t, te - 0.3, 0.5, A, B);
}

// pollen dots on the head/beak (box coords)
const POL = [[700, 140], [726, 132], [688, 156], [744, 150], [760, 184], [800, 186], [840, 190], [712, 124], [676, 172]];
// 17 pollen taxi: drinks at flower A, gets dusted, flies to flower B, pollen rubs off, seeds
export function h17(t) {
  const tp = at('h17', 'Yellow pollen'), tn = at('h17', 'At the next flower'), tr = at('h17', 'rubs off'), ts = at('h17', 'make seeds'), tx = at('h17', 'tiny taxi');
  const fa = [700, 560], fb = [1560, 560], sc = 0.85;
  const off = (fx, fy) => [fx - (990 - 600) * sc - 10, fy - (199 - 300) * sc + 30];
  const [ax, ay] = off(...fa), [bx2, by2] = off(...fb), u = sm(tn - 0.2, tn + 1.6, t);
  const bx = lerp(ax, bx2, u), by = lerp(ay, by2, u) - 260 * Math.sin(u * Math.PI);
  let s = flowerT(fa[0], fa[1], 1.25, { rot: -62 }) + flowerT(fb[0], fb[1], 1.25, { rot: -62, col: '#ff7a3d', col2: '#c4501f' });
  const rub = sm(tr - 0.2, tr + 0.6, t);
  if (rub > 0) for (let i = 0; i < 7; i++) s += `<circle cx="${f1(fb[0] - 10 + (i % 4) * 14)}" cy="${f1(fb[1] - 70 + Math.floor(i / 4) * 14)}" r="${f1(8 * rub)}" fill="#ffe14a" stroke="${N}" stroke-width="3"/>`;
  const dust = sm(tp - 0.2, tp + 0.6, t) * (1 - 0.7 * rub);
  let pol = ''; POL.forEach(([x, y]) => { if (dust > 0) pol += `<circle cx="${x}" cy="${y}" r="${f1(9 * dust)}" fill="#ffe14a" stroke="${N}" stroke-width="2.5"/>`; });
  const taxi = pop(tx, t);
  const sign = taxi > 0 ? `<g transform="translate(696 112) scale(${f1(taxi * 100) / 100})"><rect x="-70" y="-56" width="140" height="56" rx="12" fill="${K.yellow}" stroke="${N}" stroke-width="7"/><text x="0" y="-14" font-family="Black" font-size="40" fill="${N}" text-anchor="middle">TAXI</text></g>` : '';
  s += placeB(bx, by + bobB(t, 5), sc, birdSolid() + pol + sign + wings(t, { rate: 7, amp: 55 }), { rot: 8 });
  if (t > ts) { const k = eo(ts, ts + 0.8, t); for (let i = 0; i < 5; i++) { const x = fb[0] - 220 + i * 110, y = 1010; s += `<ellipse cx="${x}" cy="${y}" rx="${f1(18 * k)}" ry="${f1(12 * k)}" fill="#8a5a2b" stroke="${N}" stroke-width="4"/><path d="M${x} ${y - 10} Q${x - 10} ${f1(y - 10 - 50 * k)} ${x + 14} ${f1(y - 20 - 70 * k)}" stroke="#2f9a4f" stroke-width="8" fill="none" stroke-linecap="round"/>`; }
    s += fade(fb[0] - 420, 990, 'SEEDS', t, ts + 0.2, { size: 70, fill: N }); }
  { const [px, py] = toB(bx, by, sc, 720, 140); if (t < tx) s += tag(px, py, px - 260, py - 170, 'POLLEN', t, tp + 0.1, { col: '#ffe14a' }); }
  if (t > tx) s += big(960, 150, 'POLLEN TAXI', t, tx, { size: 140, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 18 brain + memory: x-ray head with the memory part glowing, then a meadow of flowers with refill timers
export function h18(t) {
  const tm = at('h18', 'memory'), tr = at('h18', 'A hummingbird can remember'), tl = at('h18', 'how long');
  const A = () => { const cx = 260, cy = 700, sc = 2.6, [bx, by] = toB(cx, cy, sc, 682, 160), [hx, hy] = toB(cx, cy, sc, 668, 150);
    let s = placeB(cx, cy, sc, birdInside({ glow: 'brain' }));
    s += tag(bx + 30, by - 20, 1300, 300, 'BRAIN', t, 0.3, { col: C.brain });
    if (t > tm) { const p = 1 + 0.15 * Math.sin(t * 6); s += `<ellipse cx="${f1(hx)}" cy="${f1(hy)}" rx="${f1(22 * p)}" ry="${f1(14 * p)}" fill="${K.yellow}" stroke="${N}" stroke-width="5"/>`; }
    s += tag(hx, hy, 1300, 620, 'MEMORY', t, tm + 0.1, { col: K.yellow });
    s += big(1300, 880, 'VERY BIG!', t, at('h18', 'very big'), { size: 110, fill: '#fff', stroke: N, sw: 14 });
    return s; };
  const B = () => { let s = ''; const F = [[300, 580], [700, 820], [1000, 520], [1360, 840], [1640, 540], [560, 380]];
    F.forEach(([x, y], i) => { s += blossom(x, y + 80, 64, ['#ff5f87', '#b26bff', '#ffd23a', '#ff3d5e', '#ffffff', '#ff7a3d'][i]);
      if (t > tr + 0.4 + i * 0.35) s += `<path d="M${x - 40} ${y - 30} L${x - 10} ${y} L${x + 44} ${y - 60}" stroke="${K.green}" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
      if (t > tl) s += timer(x + 90, y - 40, 44, clamp((t - tl + i * 0.3) / (2.5 + i * 0.4))); });
    const u = clamp((t - tr) / 4.0) * (F.length - 1), i = Math.min(F.length - 2, Math.floor(u)), f = eo(0, 1, u - i);
    s += fly(lerp(F[i][0], F[i + 1][0], f) - 150, lerp(F[i][1], F[i + 1][1], f) - 40, 0.4, t, { rate: 7, amp: 50 });
    s += big(960, 130, 'SUPER MEMORY', t, tr, { size: 140, fill: '#fff', stroke: N, sw: 18 });
    return s; };
  return t < tr - 0.3 ? A() : xfade(t, tr - 0.3, 0.5, A, B);
}

// rainbow bands (centre x,y; radius r); uv = 0..1 extra violet band; k = how much of the arc is drawn
const rainbow = (x, y, r, uv, k = 1) => { const cols = ['#ff4d4d', '#ff9a3c', '#ffe14a', '#3fd27a', '#3ca8ff', '#6f5bff']; let s = '';
  cols.forEach((c, i) => { const R = r - i * 44, a = Math.PI * k; s += `<path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x - R * Math.cos(a))} ${f1(y - R * Math.sin(a))}" stroke="${c}" stroke-width="44" fill="none"/>`; });
  if (uv > 0) { const R = r - 6 * 44; s += `<path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x + R)} ${y}" stroke="#c13cff" stroke-width="${f1(44 * uv)}" fill="none"/><path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x + R)} ${y}" stroke="#fff" stroke-width="6" fill="none" stroke-dasharray="6 14" opacity="${f1(uv)}"/>`; }
  return s; };
// 19 eyes see ultraviolet: rainbow + extra band, then YOU SEE vs BIRD SEES
export function h19(t) {
  const tu = at('h19', 'ultraviolet'), tg = at('h19', 'To a hummingbird');
  const A = () => { const k = eo(0.2, 1.4, t), uv = sm(tu - 0.2, tu + 0.5, t);
    let s = rainbow(960, 900, 620, uv, k);
    s += placeB(960, 860, 0.75, birdSolid() + wings(0, { still: -35, blur: 0 }));
    s += fade(960, 230, "COLORS WE CAN'T SEE", t, at('h19', "colors we can't"), { size: 90, fill: N });
    if (uv > 0) s += tag(960 + 360, 900 - 300, 1640, 360, 'UV', t, tu, { col: '#c13cff', txt: '#fff' });
    return s; };
  const B = () => { const tp = at('h19', 'patterns'), g = sm(tp - 0.3, tp + 0.6, t) * (0.75 + 0.25 * Math.sin(t * 4));
    let s = card(160, 220, 760, 760, '#fff', 0.9) + card(1000, 220, 760, 760, '#2a1a5e', 0.95);
    s += `<defs><radialGradient id="uvh"><stop offset="0" stop-color="#d78bff" stop-opacity=".9"/><stop offset="1" stop-color="#d78bff" stop-opacity="0"/></radialGradient></defs><circle cx="1380" cy="560" r="${f1(300 * g)}" fill="url(#uvh)"/>`;
    s += flowerT(540, 560, 1.4, { rot: 0, stem: 0 }) + flowerT(1380, 560, 1.4, { rot: 0, stem: 0, glowUV: g });
    s += `<text x="540" y="920" font-family="Black" font-size="80" fill="${N}" text-anchor="middle">YOU SEE</text><text x="1380" y="920" font-family="Black" font-size="80" fill="#fff" text-anchor="middle">BIRD SEES</text>`;
    s += big(960, 120, 'SECRET PATTERNS', t, tp, { size: 110, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tg - 0.3 ? A() : xfade(t, tg - 0.3, 0.5, A, B);
}

const moon = (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#fff6c8"/><circle cx="${x + r * 0.45}" cy="${y - r * 0.2}" r="${r * 0.9}" fill="#1a2552"/>`;
const zzz = (x, y, t) => { let s = ''; for (let i = 0; i < 3; i++) { const u = (t * 0.5 + i / 3) % 1; s += `<text x="${f1(x + u * 120 + i * 10)}" y="${f1(y - u * 200)}" font-family="Black" font-size="${f1(50 + 40 * u)}" fill="#fff" opacity="${f1(1 - u)}">Z</text>`; } return s; };
// 20 night: no food, fuel runs low, torpor
export function h20(t) {
  const tc = at('h20', "can't eat"), tf = at('h20', 'run out of fuel'), tt = at('h20', 'deep sleep'), tor = at('h20', 'torpor');
  const sl = sm(tt - 0.3, tt + 1.2, t);
  let s = moon(1620, 200, 90) + branch(240, 1100, 780) + perched(700, 640, 1.0, { puff: sl, closed: sl });
  if (t > tc - 0.3 && t < tf - 0.3) { const k = sm(tc - 0.3, tc, t); s += `<g opacity="${f1(k)}">${flowerT(1420, 470, 1.0, { rot: 0, stem: 0, col: '#7a6a8a', col2: '#5a4a6a' })}</g>` + cross(1420, 470, 170, t, tc + 0.1); }
  if (t > tf - 0.3) { const k = sm(tf - 0.3, tf, t) * (1 - sm(tt - 0.4, tt, t)), v = lerp(0.6, 0.05, eo(tf, tf + 2, t));
    if (k > 0) s += `<g opacity="${f1(k)}">${gauge(1420, 500, 200, v, { lab: 'FUEL', lo: 'E', hi: 'F', red: 0.25, rev: 1 })}</g>`; }
  if (sl > 0.5) s += zzz(880, 380, t);
  if (t > tt) s += big(1480, 500, 'TORPOR', t, tor, { size: 170, fill: '#fff', stroke: N, sw: 18 }) + fade(1480, 650, 'DEEP SLEEP', t, tt, { size: 80, fill: '#9fc4ff' });
  s += big(960, 140, 'NIGHT', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  return s;
}

// thermometer, level 0..1
const thermo = (x, y, lv, col) => `<g transform="translate(${x} ${y})"><rect x="-40" y="-300" width="80" height="380" rx="40" fill="#fff" stroke="${N}" stroke-width="9"/><circle cx="0" cy="120" r="70" fill="${col}" stroke="${N}" stroke-width="9"/><rect x="-20" y="${f1(60 - 340 * lv)}" width="40" height="${f1(340 * lv + 40)}" rx="20" fill="${col}"/>${[0, 1, 2, 3, 4].map(i => `<path d="M40 ${-260 + i * 70} L66 ${-260 + i * 70}" stroke="${N}" stroke-width="7"/>`).join('')}</g>`;
// 21 body cools, heart slows 1,200 → 50, almost off; morning: warm up and fly
export function h21(t) {
  const th = at('h21', 'Its heart slows'), toff = at('h21', 'switches itself off'), tm = at('h21', 'In the morning'), tw = at('h21', 'warms back up');
  const dawn = sm(tm - 0.3, tm + 1.2, t), wake = sm(tw, tw + 0.8, t), go = sm(tw + 1.0, tw + 2.4, t);
  let s = dawn > 0 ? `<defs><linearGradient id="dw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffc46b"/><stop offset="1" stop-color="#ff8f45"/></linearGradient></defs><rect x="-100" y="-100" width="2120" height="1280" fill="url(#dw)" opacity="${f1(dawn)}"/>` : '';
  if (dawn > 0) s += `<circle cx="300" cy="${f1(lerp(1180, 240, dawn))}" r="110" fill="#ffe27a" stroke="#fff" stroke-width="10"/>`;
  s += branch(160, 980, 860);
  const puff = 1 - wake;
  s += go > 0 ? fly(lerp(560, -500, go), 720 - 420 * go, 0.85, t, { rate: 7, amp: 55, flip: true }) : perched(560, 720, 0.85, { puff, closed: puff });
  if (puff > 0.5 && dawn < 0.6) s += zzz(700, 480, t);
  const lv = lerp(0.85, 0.3, eo(0.2, 2.2, t)) + 0.55 * wake;
  s += thermo(1150, 520, Math.min(0.85, lv), lv < 0.5 ? '#3ca8ff' : K.red);
  const bpm = t < th ? 1200 : Math.round(lerp(1200, 50, eo(th + 0.3, th + 3.0, t)) + wake * 1150);
  const bps = bpm / 60 / (bpm > 300 ? 4 : 1);
  s += card(1300, 260, 520, 520, '#fff', 0.9) + ecg(1330, 1790, 600, t, Math.max(0.6, bps), { amp: 70 });
  s += readout(1560, 430, Math.min(1200, bpm).toLocaleString('en-US'), 'BEATS A MINUTE', { size: 110 });
  if (t > toff && t < tm) s += big(960, 140, 'ALMOST OFF', t, toff, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  if (t > tm) s += big(960, 140, 'GOOD MORNING!', t, tm + 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  else if (t < toff) s += big(960, 140, 'COOL DOWN', t, 0.4, { size: 130, fill: '#9fc4ff', stroke: N, sw: 16 });
  return s;
}
