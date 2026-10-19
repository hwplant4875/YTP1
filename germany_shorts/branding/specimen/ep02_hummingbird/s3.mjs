import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross, esc, ICON, sharkSolid } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from './tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, fly, perched, branch, flowerT, blossom, gauge, readout, card, arrow, bobB, speed } from './ha.mjs';
import { landPath, proj } from './maps.mjs';
const N = K.navy;
const THROAT = 'M668 214 C700 206 732 202 752 198 L760 300 C730 290 700 262 668 214Z';
// head recolour (for other species), drawn over birdSolid in box coords
const headCap = (col) => `<path d="M652 146 C668 126 712 122 734 140 C748 152 750 172 746 186 L740 210 C720 222 690 220 670 206 C652 192 644 166 652 146Z" fill="${col}" stroke="${N}" stroke-width="8"/><circle cx="714" cy="168" r="13" fill="${N}"/><circle cx="718" cy="164" r="4" fill="#fff"/>`;

// 22 tiny feet: grip a branch, can't walk, flies even a few centimetres
export function h22(t) {
  const tt = at('h22', 'tiny'), tg = at('h22', 'holding on'), tw = at('h22', "can't really walk"), tf = at('h22', 'If it wants to move'), tfl = at('h22', 'it flies');
  const A = () => { const z = eo(0.2, 1.4, t), sc = lerp(1.0, 1.6, z), cx = lerp(900, 980, z), cy = lerp(520, 400, z);
    let s = branch(-100, 2020, cy + 146 * sc + 22) + perched(cx, cy, sc, {});
    const [fx, fy] = toB(cx, cy, sc, 560, 440);
    const k = pop(tt, t); if (k > 0) s += `<circle cx="${f1(fx)}" cy="${f1(fy)}" r="${f1(130 * k)}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="20 14"/>`;
    s += tag(fx - 120, fy, 420, 900, 'TINY FEET', t, tt + 0.1, { col: K.yellow });
    s += big(1450, 900, 'GOOD GRIP', t, tg, { size: 110, fill: '#fff', stroke: N, sw: 14 });
    return s; };
  const B = () => { let s = `<path d="M0 860 L1920 860" stroke="${N}" stroke-width="10"/><rect x="0" y="864" width="1920" height="220" fill="#d9a066" opacity=".45"/>`;
    const fx = 0.5 * sm(tf - 0.2, tfl + 0.2, t), hop = Math.sin(Math.min(1, fx * 2) * Math.PI) * 120;
    if (t < tf - 0.2) { const w = 6 * Math.sin(t * 6); s += placeB(760, 700, 0.9, birdSolid() + wings(0, { still: -76, blur: 0, fill: C.back }), { rot: w }); s += big(1480, 420, "CAN'T WALK", t, tw, { size: 120, fill: '#fff', stroke: N, sw: 16 }) + cross(1480, 440, 260, t, tw + 0.5); }
    else { const x = lerp(760, 1080, sm(tf, tfl + 0.4, t)); s += fly(x, 700 - hop, 0.9, t, { rate: 7, amp: 55 });
      s += `<path d="M560 960 L880 960" stroke="#fff" stroke-width="10" stroke-linecap="round"/><path d="M560 935 L560 985 M880 935 L880 985" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`;
      s += fade(720, 1040, 'A FEW CM', t, tf + 0.2, { size: 60, fill: N });
      s += big(1500, 400, 'IT FLIES!', t, tfl, { size: 130, fill: K.yellow, stroke: N, sw: 16 }); }
    return s; };
  return t < tw - 0.4 ? A() : xfade(t, tw - 0.4, 0.5, A, B);
}

// 23 the red throat has no red paint: layers bounce light; turn the bird and it flashes on and off
export function h23(t) {
  const tp = at('h23', 'no red paint'), tl = at('h23', 'tiny layers'), t1 = at('h23', 'Turn the bird'), t2 = at('h23', 'Turn it again');
  const rot = lerp(0, -10, sm(t1 - 0.2, t1 + 0.5, t)) + lerp(0, 22, sm(t2 - 0.2, t2 + 0.5, t));
  const on = t < t1 ? 0.75 : t < t2 ? 1 : lerp(1, 0, sm(t2, t2 + 0.5, t));
  const cx = 520, cy = 620, sc = 2.3, id = 'th23';
  const thr = `<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath></defs><g clip-path="url(#${id})"><path d="${THROAT}" fill="#2a0d18"/><path d="${THROAT}" fill="#ff1f45" opacity="${f1(on)}"/>${on > 0.9 ? `<path d="M690 226 L730 214 M700 246 L746 236 M716 268 L752 262" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>` : ''}</g>`;
  let s = placeB(cx, cy, sc, birdSolid({ throat: 0 }) + thr + wings(0, { still: -60, blur: 0 }), { rot });
  const [tx, ty] = toB(cx, cy, sc, 724, 250);
  if (on > 0.95 && t > t1) { const k = (t * 3) % 1; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6, r = 40 + 80 * k; s += `<path d="M${f1(tx + Math.cos(a) * r)} ${f1(ty + Math.sin(a) * r - 20)} l0 -26 M${f1(tx + Math.cos(a) * r - 13)} ${f1(ty + Math.sin(a) * r - 33)} l26 0" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="${f1(1 - k)}"/>`; } }
  if (t < tp - 0.3) s += tag(tx, ty, 1350, 780, 'RED THROAT', t, 0.4, { col: K.red, txt: '#fff' });
  // paint can, crossed out
  if (t > tp - 0.3 && t < tl - 0.2) { const k = sm(tp - 0.3, tp, t) * (1 - sm(tl - 0.5, tl - 0.2, t));
    s += `<g opacity="${f1(k)}" transform="translate(1440 520)"><path d="M-130 -110 L130 -110 L110 150 L-110 150Z" fill="#dfe6f0" stroke="${N}" stroke-width="10" stroke-linejoin="round"/><path d="M-130 -110 C-60 -60 60 -60 130 -110 L130 -40 C60 10 -60 10 -130 -40Z" fill="${K.red}"/><path d="M-60 -60 C-60 0 -40 40 -40 80" stroke="${K.red}" stroke-width="22" stroke-linecap="round"/><path d="M-130 -110 C-130 -220 130 -220 130 -110" stroke="${N}" stroke-width="10" fill="none"/></g>` + (k > 0.5 ? cross(1440, 520, 210, t, tp + 0.2) : '');
    s += fade(1440, 840, 'NO PAINT!', t, tp, { size: 110, fill: '#fff', stroke: N, sw: 14 }); }
  // magnifier: stacked layers bounce light
  if (t > tl - 0.2 && t < t1 - 0.2) { const k = sm(tl - 0.2, tl + 0.2, t) * (1 - sm(t1 - 0.5, t1 - 0.2, t)), mx = 1560, my = 640;
    let m = `<circle cx="${mx}" cy="${my}" r="270" fill="#1a0f2e" stroke="#fff" stroke-width="14"/><path d="M${f1(tx + 30)} ${f1(ty)} L${mx - 260} ${my + 150}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12"/>`;
    for (let i = 0; i < 6; i++) m += `<rect x="${mx - 200}" y="${my + 20 + i * 32}" width="400" height="16" rx="8" fill="${['#ff6b8a', '#ff3d5e', '#e8243f', '#c41f45', '#a01438', '#7d0f2c'][i]}"/>`;
    const r = clamp((t - tl) / 0.8);
    m += `<path d="M${mx - 180} ${my - 180} L${f1(lerp(mx - 180, mx - 20, r))} ${f1(lerp(my - 180, my + 20, r))}" stroke="#ffe27a" stroke-width="14" stroke-linecap="round"/>`;
    if (r >= 1) { const r2 = clamp((t - tl - 0.8) / 0.6); m += `<path d="M${mx - 20} ${my + 20} L${f1(lerp(mx - 20, mx + 170, r2))} ${f1(lerp(my + 20, my - 170, r2))}" stroke="#ff1f45" stroke-width="16" stroke-linecap="round"/>`; }
    s += `<g opacity="${f1(k)}">${m}<text x="${mx}" y="${my + 360}" font-family="Black" font-size="72" fill="#fff" stroke="${N}" stroke-width="12" paint-order="stroke" text-anchor="middle">TINY LAYERS</text></g>`; }
  if (t > t1) s += big(1500, 860, on > 0.5 ? 'ON!' : 'OFF', t, on > 0.5 ? t1 + 0.3 : t2 + 0.3, { size: 220, fill: on > 0.5 ? K.red : '#2a0d18', stroke: '#fff', sw: 18 });
  s += big(1300, 110, 'SHINY THROAT', t, 0.2, { size: 110, fill: '#fff', stroke: N, sw: 16 });
  return s;
}

// U-shaped courtship dive path: p(u) for u in [0,1]
const UP = u => { const x = lerp(360, 1560, u), y = 160 + 760 * (1 - Math.pow(2 * u - 1, 2)); return [x, y]; };
// 24 Anna's hummingbird: climb, dive at ~100 km/h, tail chirp at the bottom
export function h24(t) {
  const tc = at('h24', 'climbs high'), td = at('h24', 'dives straight down'), tbot = at('h24', 'At the bottom'), tch = at('h24', 'loud chirp'), ta = at('h24', "Anna's");
  const male = (x, y, sc, rot, w) => placeB(x, y, sc, birdSolid() + headCap('#ff2f8a') + `<path d="${THROAT}" fill="#ff2f8a"/>` + w, { rot });
  const A = () => { let s = branch(760, 1160, 1010, 18) + perched(960, 880, 0.42, {});
    let d = ''; for (let i = 0; i <= 60; i++) { const [x, y] = UP(i / 60); d += (i ? 'L' : 'M') + f1(x) + ' ' + f1(y); }
    s += `<path d="${d}" stroke="#fff" stroke-width="8" fill="none" stroke-dasharray="4 20" stroke-linecap="round" opacity=".8"/>`;
    let x, y, rot = 0, w;
    if (t < td) { const k = sm(tc - 0.2, tc + 1.2, t); [x, y] = UP(0); y = lerp(760, y, k); x = x + bobB(t, 4); w = wings(t, { rate: 7, amp: 55 }); }
    else { const u = clamp(eo(0, 1, (t - td) / (tbot + 0.6 - td))) * 0.5 + clamp((t - tbot - 0.6) / 1.0) * 0.5, [x1, y1] = UP(u), [x2, y2] = UP(Math.min(1, u + 0.01));
      x = x1; y = y1; rot = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI; w = wings(0, { still: -15, blur: 0 }); }
    s += male(x, y, 0.55, rot, w);
    if (t > td) s += speed(x - 60 * Math.cos(rot * Math.PI / 180), y - 60 * Math.sin(rot * Math.PI / 180), 3, 120, 0.6);
    const v = t < td ? 0 : Math.round(97 * eo(td, tbot, t));
    if (t > td) s += readout(1540, 640, `${v} KM/H`, '', { size: 110 });
    if (t < td) s += tag(x, y - 60, 1300, 200, "ANNA'S HUMMINGBIRD", t, ta, { col: '#ff2f8a', txt: '#fff', size: 56 });
    else s += tag(0, 0, 1300, 200, "ANNA'S HUMMINGBIRD", t, ta, { col: '#ff2f8a', txt: '#fff', size: 56, line: false });
    return s; };
  const B = () => { const cx = 900, cy = 560, sc = 1.6, sp = sm(tbot + 0.8, tbot + 1.4, t), vib = 6 * Math.sin(t * 70) * sp;
    let fan = ''; for (let i = 0; i < 5; i++) { const a = (150 + i * 14 + (i === 4 ? vib : 0)) * Math.PI / 180, L = 240; fan += `<path d="M444 380 L${f1(444 + Math.cos(a) * L)} ${f1(380 + Math.sin(a) * L)} L${f1(444 + Math.cos(a + 0.1) * L)} ${f1(380 + Math.sin(a + 0.1) * L)}Z" fill="${i === 4 ? '#3fbf6a' : C.tailc}" stroke="${N}" stroke-width="6" stroke-linejoin="round" opacity="${f1(sp)}"/>`; }
    let s = male(cx, cy, sc, -10, wings(0, { still: -20, blur: 0 }) + fan);
    const [tx, ty] = toB(cx, cy, sc, 300, 470);
    if (t > tch - 0.2) for (let i = 0; i < 4; i++) { const r = ((t - tch + 0.2) * 300 + i * 90) % 360; s += `<path d="M${f1(tx - r * 0.7)} ${f1(ty - r * 0.7)} A${f1(r)} ${f1(r)} 0 0 0 ${f1(tx - r * 0.7)} ${f1(ty + r * 0.7)}" stroke="#fff" stroke-width="10" fill="none" opacity="${f1(1 - r / 360)}"/>`; }
    s += tag(tx, ty, 380, 220, 'TAIL FEATHERS', t, at('h24', 'tail feathers'), { col: '#fff' });
    s += big(1480, 820, 'CHIRP!', t, tch, { size: 190, fill: K.yellow, stroke: N, sw: 18, rot: -6 });
    return s; };
  return t < tbot + 0.7 ? A() : xfade(t, tbot + 0.7, 0.5, A, B);
}

const mapCard = (v, id, hi = true, ocean = '#7cc8f0') => `<defs><clipPath id="${id}"><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40"/></clipPath></defs><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40" fill="${ocean}"/><g clip-path="url(#${id})"><path d="${landPath(v, hi)}" fill="#7fd36e" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40" fill="none" stroke="${N}" stroke-width="9"/>`;
const label = (x, y, txt, size = 50, col = N) => `<text x="${f1(x)}" y="${f1(y)}" font-family="Black" font-size="${size}" fill="${col}" text-anchor="middle" stroke="#fff" stroke-width="8" paint-order="stroke">${esc(txt)}</text>`;
// polyline through projected waypoints, drawn to fraction k; returns [svg, head x, head y, heading]
const route = (P, pts, k, col = '#fff') => { const q = pts.map(([a, b]) => P(a, b)); let L = 0; const seg = []; for (let i = 1; i < q.length; i++) { const d = Math.hypot(q[i][0] - q[i - 1][0], q[i][1] - q[i - 1][1]); seg.push(d); L += d; }
  let rem = L * k, d = `M${f1(q[0][0])} ${f1(q[0][1])}`, hx = q[0][0], hy = q[0][1], ang = Math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]);
  for (let i = 1; i < q.length; i++) { const s = seg[i - 1]; ang = Math.atan2(q[i][1] - q[i - 1][1], q[i][0] - q[i - 1][0]); if (rem >= s) { d += ` L${f1(q[i][0])} ${f1(q[i][1])}`; rem -= s; hx = q[i][0]; hy = q[i][1]; } else { const f = rem / s; hx = lerp(q[i - 1][0], q[i][0], f); hy = lerp(q[i - 1][1], q[i][1], f); d += ` L${f1(hx)} ${f1(hy)}`; break; } }
  return [`<path d="${d}" stroke="${N}" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" stroke="${col}" stroke-width="10" fill="none" stroke-dasharray="2 18" stroke-linecap="round" stroke-linejoin="round"/>`, hx, hy, ang * 180 / Math.PI]; };
// 25 eats until nearly double weight, then crosses the Gulf of Mexico nonstop
export function h25(t) {
  const td = at('h25', 'doubles its weight'), tg = at('h25', 'Then it flies across'), tk = at('h25', 'eight hundred'), tn = at('h25', 'nonstop');
  const A = () => { const fat = sm(td - 1.2, td + 0.4, t);
    let s = branch(200, 1100, 840) + `<g transform="translate(640 700) scale(${f1((1 + 0.25 * fat) * 100) / 100} ${f1((1 + 0.3 * fat) * 100) / 100}) translate(-640 -700)">${perched(640, 700, 0.95, {})}</g>`;
    s += flowerT(1160, 520, 1.1, { rot: -62 });
    s += readout(1620, 470, `${(3 + 3 * fat * 0.95).toFixed(1)} G`, '', { size: 130 });
    s += big(1620, 720, 'ALMOST x2', t, td, { size: 110, fill: K.yellow, stroke: N, sw: 14 });
    s += big(960, 130, 'FUEL UP!', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  const B = () => { const v = { lon0: -103, lon1: -76, lat0: 14, lat1: 34, x: 120, y: 90, w: 1100, h: 900 }, P = proj(v);
    let s = mapCard(v, 'mc25');
    s += label(...P(-98, 31.5), 'USA', 60) + label(...P(-101.5, 19.5), 'MEXICO', 60) + label(...P(-94.6, 25.6), 'GULF OF', 44, '#1f5f9c') + label(...P(-94.6, 24.6), 'MEXICO', 44, '#1f5f9c');
    const k = sm(tg + 0.4, tn + 1.0, t), [svg, hx, hy] = route(P, [[-90.3, 29.6], [-89.9, 25.5], [-89.0, 21.4]], k);
    s += svg + `<g transform="translate(${f1(hx)} ${f1(hy)}) rotate(70)">${placeB(0, 0, 0.16, birdSolid() + wings(t, { rate: 7, amp: 50, blur: 1 }))}</g>`;
    if (t > tk - 0.2) s += readout(1570, 460, count(800, t, tk - 0.2, 1.2), 'KM', { size: 170 });
    s += big(1570, 760, 'NONSTOP!', t, tn, { size: 120, fill: K.yellow, stroke: N, sw: 16 });
    return s; };
  return t < tg - 0.2 ? A() : xfade(t, tg - 0.2, 0.6, A, B);
}

// 26 rufous: Alaska to Mexico, 6,000+ km
export function h26(t) {
  const tm = at('h26', 'More than six thousand'), tl = at('h26', 'longest trips');
  const v = { lon0: -172, lon1: -74, lat0: 12, lat1: 66, x: 120, y: 90, w: 1300, h: 900 }, P = proj(v);
  let s = mapCard(v, 'mc26', true);
  s += label(...P(-152, 64), 'ALASKA', 56) + label(...P(-99, 27), 'MEXICO', 56);
  const k = sm(0.6, tm + 0.8, t), [svg, hx, hy, ang] = route(P, [[-150, 61], [-140, 59.5], [-134, 57], [-130, 53.5], [-125, 49], [-124, 44], [-122, 38], [-117, 33], [-112, 28.5], [-106, 23.5], [-102, 19.5]], k);
  const rufous = birdSolid() + `<path d="${BIRD}" fill="#d9692a" opacity=".85"/><path d="${THROAT}" fill="#ff7a1a"/><path d="${BIRD}" fill="none" stroke="${N}" stroke-width="8"/><circle cx="714" cy="168" r="13" fill="${N}"/>`;
  s += svg + `<g transform="translate(${f1(hx)} ${f1(hy)}) rotate(${f1(ang)})">${placeB(0, 0, 0.18, rufous + wings(t, { rate: 7, amp: 50, blur: 1 }))}</g>`;
  s += placeB(1640, 300, 0.4, rufous + wings(t, { rate: 7, amp: 50 }));
  s += `<text x="1660" y="480" font-family="Black" font-size="64" fill="${N}" text-anchor="middle">RUFOUS</text>`;
  if (t > tm - 0.2) s += readout(1670, 700, count(6000, t, tm - 0.2, 1.4) + '+', 'KM', { size: 120 });
  s += big(1665, 960, 'EPIC TRIP!', t, tl, { size: 74, fill: K.yellow, stroke: N, sw: 14 });
  return s;
}

// walnut half (top view), nest cup (side view) with fluff and silk
const walnut = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M-150 0 C-150 -90 -80 -140 0 -140 C80 -140 150 -90 150 0 C150 30 120 40 0 40 C-120 40 -150 30 -150 0Z" fill="#b07a3e" stroke="${N}" stroke-width="9"/><path d="M-110 -20 C-90 -70 -60 -90 -20 -100 M-60 10 C-40 -40 0 -60 40 -70 M20 20 C40 -20 80 -50 110 -40 M-120 10 C-100 0 -80 -10 -60 -6" stroke="#7d5226" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M-150 0 C-150 30 -120 40 0 40 C120 40 150 30 150 0 C120 14 -120 14 -150 0Z" fill="#8a5a2b" stroke="${N}" stroke-width="6"/></g>`;
const nest = (x, y, s, { fluff = 1, silk = 1, wide = 1 } = {}) => { let g = `<path d="M-160 -60 C-160 60 -90 120 0 120 C90 120 160 60 160 -60 C100 -40 -100 -40 -160 -60Z" fill="#cbb48a" stroke="${N}" stroke-width="9" stroke-linejoin="round"/><ellipse cx="0" cy="-60" rx="160" ry="30" fill="#8a6a3e" stroke="${N}" stroke-width="8"/>`;
  seed(12); for (let i = 0; i < 26 * fluff; i++) { const a = rnd() * Math.PI, r = rnd(); g += `<circle cx="${f1(-140 + rnd() * 280)}" cy="${f1(-40 + rnd() * 140 * Math.sin(a) * 0.9)}" r="${f1(8 + r * 10)}" fill="${['#e8dcc0', '#9fbf8f', '#f5efe0', '#b9cfa8'][i % 4]}" opacity=".95"/>`; }
  for (let i = 0; i < 6 * silk; i++) { const y0 = -40 + i * 26; g += `<path d="M${-158 + i * 8} ${y0} C-60 ${y0 + 30} 60 ${y0 - 10} ${158 - i * 10} ${y0 + 14}" stroke="#fff" stroke-width="3" fill="none" opacity=".95"/>`; }
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * wide * 100) / 100} ${f1(s * 100) / 100})">${g}</g>`; };
// 27 nest: half a walnut, plant fluff, spider silk that stretches as the chicks grow
export function h27(t) {
  const tw = at('h27', 'half a walnut'), tf = at('h27', 'soft plant fluff'), tsk = at('h27', 'spider silk'), tst = at('h27', 'The silk stretches');
  const fl = sm(tf - 0.2, tf + 0.8, t), sk = sm(tsk - 0.2, tsk + 1.0, t), grow = sm(tst, tst + 2.4, t);
  let s = branch(300, 1620, 760, 30);
  const nx = lerp(960, 1360, sm(tw - 0.4, tw + 0.2, t) * (1 - sm(tf - 0.6, tf - 0.1, t)));
  if (grow > 0) for (let i = -1; i <= 1; i += 2) { const cx = nx + i * 80 * (1 + 0.4 * grow), cy = 560 - 50 * grow, r = 44 + 40 * grow;
    s += `<circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(r)}" fill="#8f8f9a" stroke="${N}" stroke-width="7"/><circle cx="${f1(cx + r * 0.3)}" cy="${f1(cy - r * 0.2)}" r="6" fill="${N}"/><path d="M${f1(cx + r * 0.7)} ${f1(cy)} L${f1(cx + r * 0.7 + 40)} ${f1(cy + 4)}" stroke="${N}" stroke-width="8" stroke-linecap="round"/>`; }
  s += nest(nx, 640, 2.0, { fluff: Math.max(0.3, fl), silk: sk, wide: 1 + 0.3 * grow });
  if (t > tw - 0.4 && t < tf - 0.1) { const k = sm(tw - 0.4, tw, t) * (1 - sm(tf - 0.6, tf - 0.1, t)); s += `<g opacity="${f1(k)}">${walnut(520, 640, 2.0)}${label(520, 900, 'HALF A WALNUT', 70)}</g>` + `<text x="940" y="690" font-family="Black" font-size="160" fill="${N}" text-anchor="middle" opacity="${f1(k)}">=</text>`; }
  s += tag(nx - 160, 640, 420, 330, 'PLANT FLUFF', t, tf + 0.2, { col: '#e8dcc0' });
  s += tag(nx + 200, 660, 1560, 330, 'SPIDER SILK', t, tsk + 0.2, { col: '#fff' });
  if (t > tst) s += arrow(nx - 420, 960, nx - 600, 960, { w: 16 }) + arrow(nx + 420, 960, nx + 600, 960, { w: 16 }) + fade(nx, 960, 'STRETCHES', t, tst + 0.3, { size: 70, fill: N });
  s += big(960, 130, 'TINY NEST', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  return s;
}

// 28 two eggs the size of jelly beans; mom raises the chicks alone
export function h28(t) {
  const tj = at('h28', 'jelly bean'), tm = at('h28', 'The mother raises');
  const A = () => { let s = nest(640, 740, 2.1, {});
    for (const [x, y, r] of [[560, 590, -10], [720, 594, 12]]) s += `<ellipse cx="${x}" cy="${y}" rx="56" ry="76" transform="rotate(${r} ${x} ${y})" fill="#fffdf6" stroke="${N}" stroke-width="7"/>`;
    s += `<text x="640" y="360" font-family="Black" font-size="120" fill="#fff" stroke="${N}" stroke-width="14" paint-order="stroke" text-anchor="middle">2 EGGS</text>`;
    if (t > tj - 0.3) { const k = pop(tj - 0.3, t); s += `<g transform="translate(1380 600) scale(${f1(k * 100) / 100})"><rect x="-130" y="-60" width="100" height="130" rx="50" transform="rotate(-20 -80 5)" fill="#ff4f7b" stroke="${N}" stroke-width="7"/><rect x="20" y="-60" width="100" height="130" rx="50" transform="rotate(16 70 5)" fill="#7a5bff" stroke="${N}" stroke-width="7"/></g>` + label(1380, 830, 'JELLY BEANS', 70) + big(1110, 620, '=', t, tj, { size: 160, fill: N }); }
    return s; };
  const B = () => { let s = branch(100, 1400, 860, 26) + nest(640, 740, 2.1, { wide: 1.1 });
    for (let i = -1; i <= 1; i += 2) { const cx = 640 + i * 100, cy = 600, r = 70; s += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#8f8f9a" stroke="${N}" stroke-width="7"/><circle cx="${cx + 18}" cy="${cy - 14}" r="7" fill="${N}"/><path d="M${cx + 40} ${cy - 30} L${cx + 70} ${cy - 90} L${cx + 56} ${cy - 30}Z" fill="${K.yellow}" stroke="${N}" stroke-width="5"/>`; }
    const feed = 30 * Math.sin(t * 5);
    s += placeB(1113, 394 + feed * 0.2, 0.75, birdSolid({ throat: 0 }) + wings(t, { rate: 7, amp: 50 }), { rot: -35, flip: true });
    s += big(960, 140, 'SUPER MOM', t, at('h28', 'all by herself'), { size: 130, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tm - 0.3 ? A() : xfade(t, tm - 0.3, 0.5, A, B);
}

// 29 360+ kinds, only in the Americas
export function h29(t) {
  const ta = at('h29', 'only in the Americas'), tk = at('h29', 'Alaska');
  const v = { lon0: -170, lon1: -30, lat0: -57, lat1: 72, x: 300, y: 60, w: 780, h: 960 }, P = proj(v);
  const hl = sm(ta - 0.3, ta + 0.6, t);
  let s = `<defs><clipPath id="mc29"><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40"/></clipPath></defs><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40" fill="#7cc8f0"/><g clip-path="url(#mc29)"><path d="${landPath(v)}" fill="${hl > 0.5 ? '#ffe14a' : '#7fd36e'}" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g><rect x="${v.x}" y="${v.y}" width="${v.w}" height="${v.h}" rx="40" fill="none" stroke="${N}" stroke-width="9"/>`;
  const pts = [[-150, 61], [-135, 58], [-122, 47], [-118, 35], [-110, 31], [-103, 21], [-99, 19], [-90, 16], [-84, 10], [-79, 8], [-75, 5], [-74, 0], [-77, -2], [-66, -10], [-60, -3], [-56, -12], [-48, -15], [-43, -22], [-64, -25], [-70, -33], [-68, -41], [-70, -50], [-68, -54], [-83, 35], [-90, 40]];
  pts.forEach(([lo, la], i) => { const k = pop(0.3 + i * 0.12, t, 0.3); if (k > 0) { const [x, y] = P(lo, la); s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(14 * k)}" fill="#ff3d6e" stroke="${N}" stroke-width="4"/>`; } });
  s += readout(1460, 400, count(360, t, 0, 2.5) + '+', 'KINDS', { size: 200 });
  s += big(1460, 760, 'ONLY HERE', t, ta, { size: 120, fill: K.yellow, stroke: N, sw: 16 });
  if (t > tk) s += tag(0, 0, 1460, 930, 'ALASKA TO THE TIP', t, tk, { col: '#fff', size: 56, line: false });
  return s;
}

// 30 sword-billed: beak longer than its body; reaches deep into long flowers
export function h30(t) {
  const tb = at('h30', 'beak longer'), tp = at('h30', 'perfect for reaching');
  const long = `<path d="M745 184 C880 186 1080 194 1230 199 C1080 202 880 206 746 210Z" fill="${C.beak}" stroke="${N}" stroke-width="4" stroke-linejoin="round"/>`;
  const sword = long + birdSolid() + headCap('#2f8f6a');
  const A = () => { const cx = 640, cy = 520, sc = 1.1;
    let s = placeB(cx, cy + bobB(t, 6), sc, sword + wings(t, { rate: 7, amp: 50 }));
    const yb = 880, [b0] = toB(cx, cy, sc, 420, 0), [b1] = toB(cx, cy, sc, 745, 0), [k1] = toB(cx, cy, sc, 1230, 0), k = eo(tb, tb + 0.8, t);
    if (k > 0) { s += `<rect x="${f1(b0)}" y="${yb - 20}" width="${f1((b1 - b0) * k)}" height="70" rx="35" fill="#fff" stroke="${N}" stroke-width="7"/><rect x="${f1(b1)}" y="${yb + 80}" width="${f1((k1 - b1) * k)}" height="70" rx="35" fill="${K.yellow}" stroke="${N}" stroke-width="7"/>`;
      s += fade(b0 - 24, yb + 10, 'BODY', t, tb + 0.4, { size: 72, fill: N, anchor: 'end' }) + fade(b1 - 24, yb + 110, 'BEAK', t, tb + 0.6, { size: 72, fill: N, anchor: 'end' }); }
    s += big(960, 140, 'SWORD-BILLED', t, 0.4, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  const B = () => { const sc = 0.9, ins = sm(tp + 0.2, tp + 1.4, t), cx = lerp(380, 520, ins), cy = 560;
    const [bx, by] = toB(520, cy, sc, 1230, 199);
    let s = `<g transform="translate(1180 ${f1(by)}) rotate(-90)"><path d="M-70 0 C-60 120 -30 330 -14 520 L14 520 C30 330 60 120 70 0 C40 -20 -40 -20 -70 0Z" fill="#fff3a8" stroke="${N}" stroke-width="8"/><path d="M-70 0 C-110 -30 -120 -60 -100 -80 C-60 -50 60 -50 100 -80 C120 -60 110 -30 70 0Z" fill="#fff3a8" stroke="${N}" stroke-width="8"/></g><path d="M1700 ${f1(by)} C1780 ${f1(by)} 1820 ${f1(by - 120)} 1840 ${f1(by - 300)}" stroke="#2f9a4f" stroke-width="16" fill="none" stroke-linecap="round"/>`;
    s += placeB(cx, cy, sc, sword + wings(t, { rate: 7, amp: 50 }));
    s += `<g opacity=".55"><path d="M1180 ${f1(by - 70)} L1700 ${f1(by - 14)} L1700 ${f1(by + 14)} L1180 ${f1(by + 70)}Z" fill="#fff3a8"/></g>`;
    s += big(960, 140, 'DEEP FLOWERS', t, tp, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tp - 0.3 ? A() : xfade(t, tp - 0.3, 0.6, A, B);
}

// 31 recap labels on the opened bird, then "what should we open next?"
export function h31(t) {
  const tw = at('h31', 'Wings that spin'), th = at('h31', 'A heart'), tt = at('h31', 'A brushy tongue'), tm = at('h31', 'super memory'), to = at('h31', 'switch off'), tp = at('h31', 'Tiny, but'), tq = at('h31', 'What should we open');
  const A = () => { const cx = 900, cy = 600 + bobB(t, 8, 1.6), sc = 1.4, P = n => toB(cx, cy, sc, ...PT[n]);
    let s = placeB(cx, cy, sc, birdInside({ tongue: 1, heartK: 1 + 0.12 * Math.max(0, Math.sin(t * 14)), glow: t > th && t < tt ? 'heart' : t > tm && t < to ? 'brain' : null }) + wings(t, { rate: 1.1, amp: 22, blur: 0, bones: 1 }));
    s += tag(...P('shoulder'), 300, 430, 'WINGS', t, tw, { col: '#fff' }) + tag(...P('heart'), 1440, 940, 'HEART', t, th, { col: K.red, txt: '#fff' })
      + tag(...P('tongue'), 1640, 330, 'TONGUE', t, tt, { col: K.yellow }) + tag(...P('brain'), 1240, 130, 'MEMORY', t, tm, { col: C.brain })
      + tag(...P('liver'), 560, 960, 'NIGHT MODE', t, to, { col: N, txt: '#fff' });
    s += big(1480, 700, 'TINY BUT MIGHTY', t, tp, { size: 84, fill: K.yellow, stroke: N, sw: 14 });
    return s; };
  const B = () => { let s = '';
    const cards = [[460, 'SHARK'], [960, '?'], [1460, '?']];
    cards.forEach(([x], i) => { const k = pop(tq + 0.1 + i * 0.25, t); if (k <= 0) return;
      s += `<g transform="translate(${x} 560) scale(${f1(k * 100) / 100})">${card(-210, -260, 420, 520, i ? '#fff' : '#bfe6ff', 0.95)}`;
      if (i === 0) s += `<g transform="scale(0.32) translate(-500 -215)">${sharkSolid('#ffffff', N, 14)}</g><text x="0" y="200" font-family="Black" font-size="60" fill="${N}" text-anchor="middle">DONE</text>`;
      else s += `<text x="0" y="70" font-family="Black" font-size="260" fill="${N}" text-anchor="middle">?</text>`;
      s += `</g>`; });
    s += big(960, 150, 'WHAT NEXT?', t, tq, { size: 150, fill: '#fff', stroke: N, sw: 18 });
    s += big(960, 960, 'TELL US IN THE COMMENTS', t, at('h31', 'Tell us'), { size: 80, fill: N, stroke: '#fff', sw: 12 });
    return s; };
  return t < tq - 0.3 ? A() : xfade(t, tq - 0.3, 0.5, A, B);
}
