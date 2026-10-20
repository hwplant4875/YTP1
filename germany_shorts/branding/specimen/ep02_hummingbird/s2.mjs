import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross, esc, ICON } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from './tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, prettyBrain, birdDefs, fly, perched, standing, bptB, fpt, meadowBack, meadowFront, stemTo, branch, flowerT, blossom, heartIcon, birdHeart, gauge, readout, card, ecg, arrow, bobB, timer } from './ha.mjs';
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
    let s = placeB(cx, cy, sc, birdInside({ tongue: ext, hyoid: sm(tt, tt + 0.6, t) }));
    const [tx, ty] = toB(cx, cy, sc, 990 + ext * 40, 199);
    s += tag(tx - 200, ty, 1500, 820, 'TONGUE', t, tt + 0.3, { col: K.yellow });
    s += big(1300, 170, 'INSIDE THE BEAK', t, tl + 0.4, { size: 110, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tl + 0.2 ? A() : xfade(t, tl + 0.2, 0.6, A, B);
}

// one prong of the forked tongue from (x0,y0) to (x1,y1); side = -1 left, +1 right; op = fringe opening 0..1; wet = nectar held 0..1
const prong = (x0, y0, x1, y1, side, op, wet) => {
  const L = Math.hypot(x1 - x0, y1 - y0), ux = (x1 - x0) / L, uy = (y1 - y0) / L, nx = -uy * -side, ny = ux * -side; // n points outward
  let s = `<path d="M${f1(x0)} ${f1(y0)} L${f1(x1)} ${f1(y1)}" stroke="${C.tongue}" stroke-width="46" stroke-linecap="round"/>`;
  const n = 8;
  for (let i = 0; i < n; i++) { const k = 0.22 + 0.76 * i / (n - 1), px = x0 + ux * L * k, py = y0 + uy * L * k, a = lerp(10, 72, op) * Math.PI / 180, FL = 80;
    // fringe leans back up along the prong when closed, swings outward when open
    const dx = -ux * Math.cos(a) + nx * Math.sin(a), dy = -uy * Math.cos(a) + ny * Math.sin(a);
    const bx = px + nx * 20, by = py + ny * 20, ex = bx + dx * FL, ey = by + dy * FL;
    if (wet > 0) s += `<ellipse cx="${f1(bx + nx * 22 - ux * 26)}" cy="${f1(by + ny * 22 - uy * 26)}" rx="${f1(20 * wet)}" ry="${f1(26 * wet)}" fill="#ffc83a" opacity=".95"/>`;
    s += `<path d="M${f1(bx)} ${f1(by)} Q${f1(bx + dx * FL * 0.5 + nx * 6)} ${f1(by + dy * FL * 0.5 + ny * 6)} ${f1(ex)} ${f1(ey)}" stroke="#ff8fae" stroke-width="12" fill="none" stroke-linecap="round"/>`; }
  s += `<path d="M${f1(x0 + ux * 30 - nx * 8)} ${f1(y0 + uy * 30 - ny * 8)} L${f1(x1 - ux * 14 - nx * 8)} ${f1(y1 - uy * 14 - ny * 8)}" stroke="#ffb3c6" stroke-width="6" stroke-linecap="round" opacity=".7"/>`;
  return s; };
// 13 forked tongue dips into nectar: the tip opens into a Y, fringes open, snap shut and pull it back
export function h13(t) {
  const tsp = at('h13', 'split in two'), td = at('h13', 'dips into nectar'), to = at('h13', 'open up'), tsh = at('h13', 'snap shut'), tb = at('h13', 'pull it back');
  const split = eo(tsp - 0.2, tsp + 0.6, t), dip = sm(td - 0.3, td + 0.5, t) * (1 - sm(tb - 0.1, tb + 0.8, t));
  const op = sm(to - 0.1, to + 0.5, t) * (1 - sm(tsh - 0.1, tsh + 0.25, t)), wet = t > tsh - 0.1 ? sm(tsh - 0.1, tsh + 0.3, t) : 0;
  const surf = 760;
  let s = '';
  s += `<path d="M560 0 L560 1080 M1360 0 L1360 1080" stroke="${N}" stroke-width="12"/><rect x="566" y="0" width="788" height="1080" fill="#ff7f97" opacity=".35"/>`;
  let wv = `M566 ${surf}`; for (let x = 566; x <= 1354; x += 20) wv += ` L${x} ${f1(surf + 8 * Math.sin(x / 40 + t * 3))}`;
  s += `<path d="${wv} L1354 1080 L566 1080Z" fill="#ffc83a" stroke="${N}" stroke-width="6"/>`;
  s += `<path d="M900 -20 L1020 -20 L978 120 L942 120Z" fill="${C.beak}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  // one tongue whose tip opens like a Y: the prongs stay joined at the fork and swing apart
  const fork = 430 + 240 * dip, len = 270, spread = 26 * split * Math.PI / 180;
  const tl = [960 - Math.sin(spread) * len, fork + Math.cos(spread) * len], tr = [960 + Math.sin(spread) * len, fork + Math.cos(spread) * len];
  s += `<path d="M960 60 L960 ${f1(fork + 10)}" stroke="${C.tongue}" stroke-width="60" stroke-linecap="round"/>`;
  s += prong(960 - 8 * split, fork, tl[0], tl[1], -1, op, wet) + prong(960 + 8 * split, fork, tr[0], tr[1], 1, op, wet);
  s += `<circle cx="960" cy="${f1(fork)}" r="30" fill="${C.tongue}"/>`;
  if (dip > 0.05) s += `<path d="${wv} L1354 1080 L566 1080Z" fill="#ffc83a" opacity=".35"/>`;
  s += big(960, 140, 'FORKED TONGUE', t, tsp, { size: 120, fill: '#fff', stroke: N, sw: 16 });
  s += tag(1340, 900, 1640, 900, 'NECTAR', t, td, { col: K.yellow, line: false });
  s += tag(tr[0] + 60, (fork + tr[1]) / 2, 1640, 520, 'BRUSHES', t, to + 0.1, { col: '#fff' });
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
    let s = balance(960, 380, ang, (x, y) => standing(x, y, 0.42, {}), (x, y) => drop(x, y - 120, 0.9));
    s += fade(1480, 860, 'NECTAR', t, tb + 0.4, { size: 80, fill: N });
    s += big(960, 130, 'MORE THAN ITS WEIGHT', t, tb + 0.6, { size: 110, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tw - 0.3 ? A() : xfade(t, tw - 0.3, 0.5, A, B);
}

const sugar = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M0 -110 L110 -55 L0 0 L-110 -55Z" fill="#ffffff" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><path d="M-110 -55 L0 0 L0 120 L-110 65Z" fill="#e9eef6" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><path d="M110 -55 L0 0 L0 120 L110 65Z" fill="#d3dbe8" stroke="${N}" stroke-width="8" stroke-linejoin="round"/>${[[-40, -60], [30, -50], [-60, 20], [50, 40], [-30, 60]].map(([a, b]) => `<rect x="${a}" y="${b}" width="8" height="8" fill="#b8c3d6"/>`).join('')}</g>`;
// small fly: segmented body, red eyes, glassy wings shown as a fast blur (three ghost positions)
const gnat = (x, y, s, t, face = 1) => { const ph = t * 31, wa = [-28, 2, 30].map((a, i) => a + 6 * Math.sin(ph + i * 2.1));
  const wing = a => `<g transform="rotate(${f1(a)} -2 -12)"><path d="M-2 -12 C-20 -44 -60 -54 -70 -36 C-74 -24 -40 -14 -2 -12Z" fill="#eaf6ff" opacity=".42" stroke="${N}" stroke-width="2.5" stroke-opacity=".5"/><path d="M-6 -16 C-24 -32 -44 -40 -60 -38" stroke="${N}" stroke-width="1.5" opacity=".35" fill="none"/></g>`;
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(face * s * 100) / 100} ${f1(s * 100) / 100})">
    <path d="M-8 12 L-16 34 M6 12 L4 36 M18 10 L26 32" stroke="${N}" stroke-width="3.5" stroke-linecap="round" fill="none"/>
    ${wing(wa[0])}${wing(wa[2])}
    <ellipse cx="-22" cy="2" rx="26" ry="13" fill="#4a4a5e" stroke="${N}" stroke-width="4"/><path d="M-34 -8 L-34 12 M-24 -10 L-24 14 M-14 -10 L-14 13" stroke="#6c6c86" stroke-width="3"/>
    <ellipse cx="8" cy="0" rx="16" ry="14" fill="#3a3a4a" stroke="${N}" stroke-width="4"/><circle cx="28" cy="-2" r="11" fill="#3a3a4a" stroke="${N}" stroke-width="4"/><circle cx="32" cy="-5" r="6" fill="#ff5a4f"/>
    ${wing(wa[1])}</g>`; };
const spider = (x, y, s) => { let l = ''; for (let i = 0; i < 4; i++) { const a = (-50 + i * 34) * Math.PI / 180, c = Math.cos(a), si = Math.sin(a);
    l += `<path d="M0 0 Q${f1(c * 60)} ${f1(si * 60 - 30)} ${f1(c * 90)} ${f1(si * 90 + 10)}" stroke="${N}" stroke-width="6" fill="none"/><path d="M0 0 Q${f1(-c * 60)} ${f1(si * 60 - 30)} ${f1(-c * 90)} ${f1(si * 90 + 10)}" stroke="${N}" stroke-width="6" fill="none"/>`; }
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M0 -40 L0 -400" stroke="#fff" stroke-width="3"/>${l}<ellipse cx="0" cy="0" rx="34" ry="30" fill="#5a3a2a" stroke="${N}" stroke-width="5"/><circle cx="0" cy="-36" r="18" fill="#5a3a2a" stroke="${N}" stroke-width="5"/><circle cx="-6" cy="-40" r="4" fill="#fff"/><circle cx="6" cy="-40" r="4" fill="#fff"/></g>`; };
const bricks = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})">${[[-110, 0], [0, 0], [110, 0], [-55, -70], [55, -70], [0, -140]].map(([a, b]) => `<rect x="${a - 52}" y="${b - 32}" width="104" height="64" rx="8" fill="#e06a4a" stroke="${N}" stroke-width="7"/>`).join('')}</g>`;
// 16 sugar is not enough: bird snaps up gnats and a spider; then SUGAR = ENERGY, BUGS = BUILDING
export function h16(t) {
  const ti = at('h16', 'tiny insects'), tsp = at('h16', 'spiders'), te = at('h16', 'Sugar for energy');
  const A = () => { let s = '';
    if (t < ti - 0.4) { s += sugar(960, 560, 1.6); s += big(960, 160, 'SUGAR ONLY?', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 }); s += cross(960, 580, 260, t, at('h16', "isn't enough")); return s; }
    const k = sm(ti - 0.4, ti, t), T0 = ti - 0.4, D = 2.4, path = v => { const uu = clamp(v); return [lerp(200, 1060, eo(0, 1, uu)), 620 + 80 * Math.sin(uu * 6)]; };
    const u = clamp((t - T0) / D), [bx, by] = path(u), tip = v => { const [x, y] = path(v); return toB(x, y, 0.75, 992, 199); };
    s += `<g opacity="${f1(k)}">`;
    // three flies right on the flight path get snapped up: each slides into the beak tip and vanishes
    [0.36, 0.62, 0.88].forEach((ui, i) => { const tc = T0 + ui * D, [gx0, gy0] = tip(ui), hx = gx0 + 40 + 14 * Math.sin(t * 3 + i), hy = gy0 - 6 + 12 * Math.cos(t * 4 + i);
      if (t < tc - 0.12) s += gnat(hx, hy, 1.4, t + i * 0.37, -1);
      else if (t < tc + 0.1) { const q = sm(tc - 0.12, tc + 0.1, t), [px, py] = tip(u); s += gnat(lerp(hx, px, q), lerp(hy, py, q), 1.4 * (1 - q), t, -1); }
      else if (t < tc + 0.45) { const q = (t - tc - 0.1) / 0.35, [px, py] = tip(u); s += `<circle cx="${f1(px)}" cy="${f1(py)}" r="${f1(14 + 40 * q)}" fill="none" stroke="#fff" stroke-width="6" opacity="${f1(1 - q)}"/>`; } });
    seed(3); for (let i = 0; i < 2; i++) { const gx = 1240 + rnd() * 240 + 30 * Math.sin(t * 3 + i), gy = 250 + rnd() * 80 + 20 * Math.cos(t * 4 + i); s += gnat(gx, gy, 1.1, t + i, i % 2 ? 1 : -1); }
    if (t > tsp - 0.3) s += `<g opacity="${f1(sm(tsp - 0.3, tsp, t))}">${spider(1580, 420 + 10 * Math.sin(t * 2), 1.2)}</g>`;
    s += fly(bx, by, 0.75, t, { rate: 7, amp: 55 }) + `</g>`;
    s += big(960, 140, 'BUGS TOO!', t, ti, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    if (t > tsp) s += tag(1580, 380, 1580, 250, 'SPIDER', t, tsp, { col: '#fff', line: false, size: 60 });
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

// pollen dust stuck on the crown, forehead and beak base (box coords), seeded once
const POL = (() => { seed(12); const p = []; for (let i = 0; i < 70; i++) { const a = rnd(), zone = i % 3;
  const [x, y] = zone === 0 ? [660 + rnd() * 80, 132 + rnd() * 30] : zone === 1 ? [720 + rnd() * 40, 150 + rnd() * 40] : [748 + rnd() * 90, 182 + rnd() * 16];
  p.push([x, y, 3 + rnd() * 5, rnd()]); } return p; })();
const dust = (x, y, r, o) => `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="#ffe14a" stroke="#d99a00" stroke-width="${f1(Math.min(1.6, r * 0.3))}" opacity="${f1(o)}"/>`;
// 17 pollen taxi: a meadow; drinks at flower A and gets dusted, flies to flower B, dust rubs off, seeds sprout
export function h17(t) {
  const tp = at('h17', 'Yellow pollen'), tn = at('h17', 'At the next flower'), tr = at('h17', 'rubs off'), ts = at('h17', 'make seeds'), tx = at('h17', 'tiny taxi');
  const FR = -60, FS = 1.5, A = [740, 520], B = [1450, 510], sc = 0.92, phi = 30, depth = 30;
  const ax = [-Math.sin(FR * Math.PI / 180), Math.cos(FR * Math.PI / 180)];
  const at0 = m => { const tip = [m[0] + ax[0] * depth, m[1] + ax[1] * depth], o = bptB(0, 0, sc, phi, 992, 199); return [tip[0] - o[0], tip[1] - o[1]]; };
  const cA = at0(A), cB = at0(B), u = t2 => sm(tn - 0.2, tn + 1.6, t2);
  const ctr = t2 => { const k = u(t2); return [lerp(cA[0], cB[0], k), lerp(cA[1], cB[1], k) - 110 * Math.sin(k * Math.PI)]; };
  const head = t2 => { const [x, y] = ctr(t2); return bptB(x, y, sc, phi, 724, 150); };
  let s = meadowBack(t);
  // background flowers growing out of the bushes, so no stem ever ends in mid air
  const BGF = [[220, 640, -20, '#b26bff', '#7a3fd0'], [1020, 700, -30, '#ffd23a', '#d9a400'], [1760, 640, -10, '#ff5f87', '#c4305a']];
  BGF.forEach(([x, y, r, c1, c2]) => { const [ex, ey] = fpt(x, y, 0.75, r, 0, 200); s += stemTo(ex, ey, ex + 10, 930, 11) + flowerT(x, y, 0.75, { rot: r, col: c1, col2: c2, stem: 0 }); });
  [[420, 800, '#ff5f87'], [880, 820, '#ffffff'], [1180, 790, '#b26bff'], [1640, 800, '#ffd23a'], [120, 820, '#ffffff'], [1880, 810, '#ff7a3d']].forEach(([x, y, c]) => { s += `<path d="M${x} ${y} L${x + 6} 920" stroke="#2f9a4f" stroke-width="8"/>` + blossom(x, y, 34, c); });
  for (const [m, c1, c2] of [[A, '#ff3d5e', '#c41f45'], [B, '#ff7a3d', '#c4501f']]) { const [ex, ey] = fpt(m[0], m[1], FS, FR, 0, 200); s += stemTo(ex, ey, ex - 20, 960, 15) + flowerT(m[0], m[1], FS, { rot: FR, col: c1, col2: c2, stem: 0 }); }
  // flower B gets dusty where the pollen lands
  const rub = sm(tr - 0.2, tr + 1.0, t);
  if (rub > 0) { seed(19); for (let i = 0; i < 26; i++) { const [px, py] = fpt(B[0], B[1], FS, FR, -30 + rnd() * 70, -90 + rnd() * 40); s += dust(px, py, 3 + rnd() * 4, rub * (0.6 + 0.4 * rnd())); } }
  // dust puff off flower A's anthers when the head brushes them
  if (t > tp - 0.2 && t < tp + 1.4) { seed(23); const q = (t - tp + 0.2) / 1.6; for (let i = 0; i < 40; i++) { const [ox, oy] = fpt(A[0], A[1], FS, FR, 5, -70), a = rnd() * Math.PI * 2, v = 60 + rnd() * 160;
    s += dust(ox + Math.cos(a) * v * q, oy + Math.sin(a) * v * q + 40 * q * q, 2 + rnd() * 4, (1 - q) * 0.9); } }
  // dust falling off behind the bird while it flies
  if (t > tn - 0.2) for (let j = 0; j < 36; j++) { const e = tn - 0.2 + j * 0.05, age = t - e; if (age < 0 || age > 1.3) continue; const [hx, hy] = head(e);
    s += dust(hx - 30 * age + 10 * Math.sin(j), hy + 70 * Math.pow(age, 1.3), 2 + (j % 4), 0.9 * (1 - age / 1.3)); }
  // dust streaming from the head onto flower B
  if (t > tr - 0.2 && t < tr + 1.2) { const [hx, hy] = head(t); for (let i = 0; i < 16; i++) { const q = clamp((t - tr + 0.2 - i * 0.04) / 0.6); if (q <= 0 || q >= 1) continue; const [px, py] = fpt(B[0], B[1], FS, FR, -20 + (i % 5) * 12, -84 + (i % 3) * 10);
    s += dust(lerp(hx, px, q), lerp(hy, py, q) - 20 * Math.sin(q * Math.PI), 3 + (i % 3), 1); } }
  // the bird with its dusty head
  const stick = sm(tp - 0.1, tp + 0.9, t) * (1 - 0.7 * rub);
  let pol = ''; POL.forEach(([x, y, r, d]) => { const k = clamp(stick * 1.6 - d * 0.6); if (k > 0) pol += dust(x, y, r * k, 0.95); });
  const taxi = pop(tx, t);
  const sign = taxi > 0 ? `<g transform="translate(690 112) rotate(-6) scale(${f1(taxi * 140) / 100})"><rect x="-74" y="-58" width="148" height="58" rx="12" fill="${K.yellow}" stroke="${N}" stroke-width="7"/><text x="0" y="-14" font-family="Black" font-size="40" fill="${N}" text-anchor="middle">TAXI</text></g>` : '';
  const [bx, by] = ctr(t);
  s += placeB(bx, by + bobB(t, 4), sc, birdSolid() + pol + sign + wings(t, { rate: 7, amp: 50 }), { rot: phi });
  s += meadowFront(t);
  // seeds drop from flower B and sprout in the grass
  if (t > ts - 0.2) { const k = eo(ts - 0.2, ts + 0.9, t), g = eo(ts + 0.8, ts + 2.0, t); const [fx, fy] = fpt(B[0], B[1], FS, FR, 0, 200);
    for (let i = 0; i < 5; i++) { const x = fx - 300 + i * 130, y0 = fy + 20, y = lerp(y0, 1030, k);
      if (g < 1) s += `<ellipse cx="${f1(lerp(fx, x, k))}" cy="${f1(y)}" rx="12" ry="16" fill="#8a5a2b" stroke="${N}" stroke-width="4"/>`;
      if (g > 0) s += `<g transform="translate(${x} 1032) scale(${f1(1.7 * g * 100) / 100})"><path d="M0 0 Q-6 -40 4 -70" stroke="${N}" stroke-width="13" fill="none" stroke-linecap="round"/><path d="M0 0 Q-6 -40 4 -70" stroke="#2f9a4f" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M4 -70 c-30 -10 -40 -30 -30 -40 c16 4 28 16 30 40Z M4 -70 c28 -14 44 -10 44 4 c-14 10 -30 6 -44 -4Z" fill="#4fd06a" stroke="${N}" stroke-width="4"/></g>`; }
    s += fade(fx - 470, 1010, 'SEEDS', t, ts + 0.2, { size: 72, fill: '#fff', stroke: N, sw: 12 }); }
  { const [px, py] = head(t); if (t < tx) s += tag(px, py - 10, px - 160, Math.max(120, py - 230), 'POLLEN', t, tp + 0.2, { col: '#ffe14a' }); }
  if (t > tx) s += big(960, 115, 'POLLEN TAXI', t, tx, { size: 130, fill: '#fff', stroke: N, sw: 18 });
  return s;
}

// 18 brain + memory: x-ray head with the memory part glowing, then a meadow of flowers with refill timers
export function h18(t) {
  const tm = at('h18', 'memory'), tr = at('h18', 'A hummingbird can remember'), tl = at('h18', 'how long');
  const A = () => { const cx = 300, cy = 760, sc = 2.3, [wx, wy] = toB(cx, cy, sc, 670, 164), z = eo(0.1, 0.9, t);
    const mem = t > tm ? 0.6 + 0.4 * Math.sin(t * 6) : 0, BXc = 1480, BYc = 410, BR = 240;
    let s = placeB(cx, cy, sc, birdInside({ brain: 1 }));
    if (z > 0) { const R = BR * z, mx = BXc - 20 * 5.2, my = BYc - 18 * 5.2;
      s += `<path d="M${f1(wx)} ${f1(wy - 58)} L${f1(BXc - R * 0.2)} ${f1(BYc - R)} M${f1(wx)} ${f1(wy + 58)} L${f1(BXc - R * 0.2)} ${f1(BYc + R)}" stroke="#fff" stroke-width="5" stroke-dasharray="10 10" opacity="${f1(z)}"/>`;
      s += `<circle cx="${BXc}" cy="${BYc}" r="${f1(R + 14)}" fill="#ffffff" stroke="${N}" stroke-width="8"/><circle cx="${BXc}" cy="${BYc}" r="${f1(R)}" fill="#3a1830"/>`;
      s += `<clipPath id="bzc"><circle cx="${BXc}" cy="${BYc}" r="${f1(R)}"/></clipPath><g clip-path="url(#bzc)"><g transform="translate(${BXc + 20 * z} ${BYc + 10}) scale(${f1(4.8 * z * 100) / 100})">${birdDefs()}${prettyBrain({ sw: 1.6 })}${mem ? `<ellipse cx="-4" cy="-18" rx="${f1(16 + 3 * mem)}" ry="${f1(9 + 2 * mem)}" fill="${K.yellow}" opacity="${f1(0.55 + 0.35 * mem)}" stroke="${N}" stroke-width="1.4"/>` : ''}</g></g>`;
      s += tag(BXc - 60, BYc - 150, BXc - 330, BYc - 300, 'BRAIN', t, 0.6, { col: '#f7c6cf' });
      s += tag(BXc + 20 - 4 * 4.8, BYc + 10 - 18 * 4.8, BXc, BYc + 370, 'MEMORY', t, tm + 0.1, { col: K.yellow }); }
    s += big(1480, 960, 'VERY BIG!', t, at('h18', 'very big'), { size: 110, fill: '#fff', stroke: N, sw: 14 });
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

// rainbow bands (centre x,y; radius r) incl. violet; uv = 0..1 pale see-through ultraviolet band just inside the violet; k = how much of the arc is drawn
const RB = ['#ff4d4d', '#ff9a3c', '#ffe14a', '#3fd27a', '#3ca8ff', '#5b5bff', '#8a3cff'], BW = 40;
const rainbow = (x, y, r, uv, k = 1) => { let s = '';
  RB.forEach((c, i) => { const R = r - i * BW, a = Math.PI * k; s += `<path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x - R * Math.cos(a))} ${f1(y - R * Math.sin(a))}" stroke="${c}" stroke-width="${BW + 1}" fill="none"/>`; });
  if (uv > 0) { const R = r - RB.length * BW - 2, a = Math.PI * Math.min(1, uv * 1.2);
    s += `<path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x - R * Math.cos(a))} ${f1(y - R * Math.sin(a))}" stroke="#d9c2ff" stroke-width="${BW + 6}" fill="none" opacity=".62"/>
      <path d="M${f1(x - R)} ${y} A${R} ${R} 0 0 1 ${f1(x - R * Math.cos(a))} ${f1(y - R * Math.sin(a))}" stroke="#ffffff" stroke-width="4" fill="none" stroke-dasharray="3 16" stroke-linecap="round" opacity=".8"/>`; }
  return s; };
export const UVR = r => r - RB.length * BW - 2;
// 19 eyes see ultraviolet: rainbow + extra band, then YOU SEE vs BIRD SEES
export function h19(t) {
  const tu = at('h19', 'ultraviolet'), tg = at('h19', 'To a hummingbird');
  const A = () => { const k = eo(0.2, 1.4, t), uv = sm(tu - 0.2, tu + 0.8, t), R = UVR(640), ang = 52 * Math.PI / 180;
    let s = rainbow(960, 960, 640, uv, k);
    s += placeB(960, 870, 0.5, birdSolid() + wings(0, { still: -35, blur: 0 }));
    s += fade(960, 200, "COLORS WE CAN'T SEE", t, at('h19', "colors we can't"), { size: 90, fill: N });
    if (uv > 0.3) s += tag(960 + R * Math.cos(ang), 960 - R * Math.sin(ang), 1560, 420, 'UV', t, tu + 0.3, { col: '#d9b3ff' });
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
