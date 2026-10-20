import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, fade, xfade, count, cross, esc, ICON, sharkSolid } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from './tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, PAL, fly, perched, perchedInner, onBranch, standing, ground, leaf, branch, flowerT, blossom, gauge, readout, card, arrow, bobB, speed, photo, bptB, fpt, stemTo } from './ha.mjs';
import { landPath, proj } from './maps.mjs';
const N = K.navy;
const THROAT = 'M668 214 C700 206 732 202 752 198 L760 300 C730 290 700 262 668 214Z';
// 22 tiny feet: grip a branch, can't walk, flies even a few centimetres
export function h22(t) {
  const tt = at('h22', 'tiny'), tg = at('h22', 'holding on'), tw = at('h22', "can't really walk"), tf = at('h22', 'If it wants to move'), tfl = at('h22', 'it flies');
  const A = () => { const z = eo(0.2, 1.4, t), sc = lerp(1.0, 1.6, z), cx = lerp(820, 900, z), by = lerp(800, 860, z), th = lerp(22, 34, z);
    let s = branch(-100, 2020, by, th) + onBranch(cx, by, sc, { th });
    const fx = cx + (570 - 600) * sc, fy = by - th / 2 - 4;
    const k = pop(tt, t); if (k > 0) s += `<circle cx="${f1(fx)}" cy="${f1(fy - 10)}" r="${f1(110 * k)}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="20 14"/>`;
    s += tag(fx + 60, fy + 30, 1450, 990, 'TINY FEET', t, tt + 0.1, { col: K.yellow });
    // close-up bubble: toes wrapped around the twig (cross-section)
    const g = pop(tg - 0.1, t); if (g > 0) { const bx = 400, byy = 420, R = 180;
      s += `<path d="M${f1(bx + R * 0.72)} ${f1(byy + R * 0.72)} L${f1(fx - 40)} ${f1(fy - 20)}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12" opacity="${f1(Math.min(1, g))}"/>`;
      const arcP = (a0, a1, r) => { let d = ''; for (let i = 0; i <= 16; i++) { const a = (a0 + (a1 - a0) * i / 16) * Math.PI / 180; d += (i ? 'L' : 'M') + f1(Math.cos(a) * r) + ' ' + f1(60 + Math.sin(a) * r); } return d; };
      const claw = (a, r, dir) => { const q = a * Math.PI / 180, x = Math.cos(q) * r, y = 60 + Math.sin(q) * r, tx = -Math.sin(q) * dir, ty = Math.cos(q) * dir; return `<path d="M${f1(x)} ${f1(y)} L${f1(x + tx * 22 - Math.cos(q) * 10)} ${f1(y + ty * 22 - Math.sin(q) * 10)}" stroke="#2a2030" stroke-width="10" stroke-linecap="round"/>`; };
      let b = `<circle cx="0" cy="60" r="78" fill="#8a5a2b" stroke="${N}" stroke-width="9"/><circle cx="0" cy="60" r="54" fill="none" stroke="#a87444" stroke-width="7"/><circle cx="0" cy="60" r="30" fill="none" stroke="#a87444" stroke-width="7"/><circle cx="0" cy="60" r="9" fill="#6e4520"/>`;
      b += `<path d="M-60 -200 L-8 -22" stroke="${N}" stroke-width="30" stroke-linecap="round"/><path d="M-60 -200 L-8 -22" stroke="#3a3348" stroke-width="16" stroke-linecap="round"/>`;
      const toe = (a0, a1, r, dir) => `<path d="${arcP(a0, a1, r)}" stroke="${N}" stroke-width="24" fill="none" stroke-linecap="round"/><path d="${arcP(a0, a1, r)}" stroke="#55506a" stroke-width="11" fill="none" stroke-linecap="round"/>` + claw(a1, r, dir);
      b += toe(-95, 45, 94, 1) + toe(-95, 0, 94, 1) + toe(-95, -200, 94, -1);
      s += `<g transform="translate(${bx} ${byy}) scale(${f1(g * 100) / 100})"><defs><clipPath id="toe22"><circle r="${R}"/></clipPath></defs><circle r="${R + 12}" fill="${N}"/><circle r="${R}" fill="#fff4dc"/><g clip-path="url(#toe22)">${b}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="8"/></g>`;
      s += fade(bx, byy - R - 50, 'GOOD GRIP', t, tg + 0.1, { size: 84, fill: '#fff', stroke: N, sw: 14 }); }
    return s; };
  const GY = 860, x0 = 700, x1 = 1060;
  const B = () => { let s = ground(GY, t);
    const k = sm(tf - 0.1, tfl + 0.3, t);
    if (k <= 0) { const w = 7 * Math.sin(t * 7); s += standing(x0, GY, 0.9, { lean: -14 + w }); s += big(1480, 400, "CAN'T WALK", t, tw, { size: 120, fill: '#fff', stroke: N, sw: 16 }) + cross(1480, 420, 260, t, tw + 0.5); }
    else if (k >= 1) s += standing(x1, GY, 0.9, {});
    else { const x = lerp(x0, x1, k), y = GY - 152 * 0.9 - 30 - 170 * Math.sin(Math.PI * k); s += fly(x, y, 0.9, t, { rate: 9, amp: 55 });
      for (let i = 1; i <= 3; i++) { const kk = Math.max(0, k - i * 0.07), xx = lerp(x0, x1, kk), yy = GY - 152 * 0.9 - 30 - 170 * Math.sin(Math.PI * kk); s += `<circle cx="${f1(xx - 60)}" cy="${f1(yy + 40)}" r="${f1(9 - i * 2)}" fill="#fff" opacity="${f1(0.6 - i * 0.15)}"/>`; } }
    if (t > tf) { const ax = x0 + (570 - 600) * 0.9, bx = x1 + (570 - 600) * 0.9, kk = eo(tf, tf + 0.5, t);
      s += `<g opacity="${f1(kk)}"><path d="M${f1(ax)} 960 L${f1(bx)} 960" stroke="#fff" stroke-width="10" stroke-linecap="round"/><path d="M${f1(ax)} 935 L${f1(ax)} 985 M${f1(bx)} 935 L${f1(bx)} 985" stroke="#fff" stroke-width="10" stroke-linecap="round"/></g>`;
      s += fade((ax + bx) / 2, 1040, 'A FEW CM', t, tf + 0.2, { size: 60, fill: N }); }
    if (t > tf) s += big(1480, 220, 'IT FLIES!', t, tfl, { size: 130, fill: K.yellow, stroke: N, sw: 16 });
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
const UP = u => { const x = lerp(380, 1540, u), y = 150 + 560 * (1 - Math.pow(2 * u - 1, 2)); return [x, y]; };
const hills = () => `<path d="M-40 900 C300 800 600 860 900 840 C1200 820 1500 780 1960 860 L1960 1120 L-40 1120Z" fill="#9fd47a" stroke="${N}" stroke-width="7"/><path d="M-40 990 C400 940 900 980 1300 960 C1600 946 1800 960 1960 950 L1960 1120 L-40 1120Z" fill="#6fbf5f" stroke="${N}" stroke-width="7"/>`;
const sparkle = (x, y, r, o = 1) => `<path d="M${f1(x)} ${f1(y - r)} Q${f1(x + r * 0.18)} ${f1(y - r * 0.18)} ${f1(x + r)} ${f1(y)} Q${f1(x + r * 0.18)} ${f1(y + r * 0.18)} ${f1(x)} ${f1(y + r)} Q${f1(x - r * 0.18)} ${f1(y + r * 0.18)} ${f1(x - r)} ${f1(y)} Q${f1(x - r * 0.18)} ${f1(y - r * 0.18)} ${f1(x)} ${f1(y - r)}Z" fill="#fff" opacity="${f1(o)}"/>`;
// detailed tail feather (pointing along +x, length L) with shaft and barbs
const featherD = (L, w, col = '#3d6450') => { let s = `<path d="M0 ${f1(-w * 0.3)} C${f1(L * 0.3)} ${f1(-w)} ${f1(L * 0.8)} ${f1(-w * 0.8)} ${f1(L)} 0 C${f1(L * 0.8)} ${f1(w * 0.55)} ${f1(L * 0.3)} ${f1(w * 0.7)} 0 ${f1(w * 0.3)}Z" fill="${col}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  for (let i = 1; i < 16; i++) { const x = L * i / 16; s += `<path d="M${f1(x)} 0 L${f1(x + 26)} ${f1(-w * 0.75 * Math.sin(Math.PI * Math.min(1, i / 14)))}" stroke="#fff" stroke-width="2.5" opacity=".35"/><path d="M${f1(x)} 0 L${f1(x + 22)} ${f1(w * 0.5 * Math.sin(Math.PI * Math.min(1, i / 14)))}" stroke="#fff" stroke-width="2.5" opacity=".25"/>`; }
  return s + `<path d="M-30 0 L${f1(L - 10)} 0" stroke="#e8eef0" stroke-width="5" stroke-linecap="round"/>`; };
// 24 Anna's hummingbird: climb, dive at ~100 km/h, tail chirp at the bottom
export function h24(t) {
  const tc = at('h24', 'climbs high'), td = at('h24', 'dives straight down'), tbot = at('h24', 'At the bottom'), tch = at('h24', 'loud chirp'), ta = at('h24', "Anna's");
  const male = (x, y, sc, rot, w, o = {}) => placeB(x, y, sc, birdSolid({ pal: 'anna', ...o }) + w, { rot });
  const prog = () => { if (t < td) return -1; const a = clamp((t - td) / (tbot - td)), b = clamp((t - tbot) / 1.3); return 0.5 * a * a + 0.5 * eo(0, 1, b); };
  const A = () => { let s = `<circle cx="1660" cy="190" r="90" fill="#fff3b0" opacity=".8"/>` + hills() + branch(720, 1200, 1000, 20, { leaves: 0 }) + onBranch(960, 1000, 0.42, { throat: 0, flip: true });
    let d = ''; for (let i = 0; i <= 60; i++) { const [x, y] = UP(i / 60); d += (i ? 'L' : 'M') + f1(x) + ' ' + f1(y); }
    const pk = sm(td - 0.6, td, t); if (pk > 0) s += `<path d="${d}" stroke="#fff" stroke-width="8" fill="none" stroke-dasharray="4 20" stroke-linecap="round" opacity="${f1(0.8 * pk)}"/>`;
    const u = prog(); let x, y, rot = 0;
    if (u < 0) { const k = sm(tc - 0.2, tc + 1.4, t); x = 380 + bobB(t, 4); y = lerp(700, 150, k);
      s += male(x, y, 0.55, -8, wings(t, { rate: 12, amp: 55, blur: 3 }));
      if (k > 0.02 && k < 0.98) s += arrow(x - 170, y + 160, x - 170, y - 40, { w: 14 }); }
    else { const [x1, y1] = UP(u), [x2, y2] = UP(Math.min(1, u + 0.01)); x = x1; y = y1; rot = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
      for (let i = 4; i >= 1; i--) { const [gx, gy] = UP(Math.max(0, u - i * 0.022)); s += placeB(gx, gy, 0.55, `<path d="${BIRD}" fill="#ffffff"/>`, { rot }).replace('<g ', `<g opacity="${f1(0.34 - i * 0.07)}" `); }
      s += `<g transform="rotate(${f1(rot)} ${f1(x)} ${f1(y)})">${speed(x - 90, y, 4, 150, 0.7)}</g>`;
      const shine = 1 - clamp(Math.abs(u - 0.5) / 0.14);
      s += male(x, y, 0.55, rot, wings(0, { still: -70, blur: 0, fill: PAL.anna.b }));
      if (shine > 0) { const [gx, gy] = bptB(x, y, 0.55, rot, 730, 240); for (let i = 0; i < 4; i++) { const a = i * 1.57 + t * 3; s += sparkle(gx + Math.cos(a) * 70, gy + Math.sin(a) * 70, 22 * shine, shine); } } }
    const v = u < 0 ? 0 : Math.round(97 * clamp(u / 0.5));
    if (u >= 0) s += readout(1540, 960, `${v} KM/H`, '', { size: 96 });
    // real photo of the species while its name is said
    const pk2 = t > ta - 0.2 && t < td - 0.1 ? pop(ta - 0.2, t) * (1 - sm(td - 0.5, td - 0.1, t)) : 0;
    s += photo('anna', 1160, 470, 820, 520, pk2, { cap: "ANNA'S HUMMINGBIRD" });
    if (t > tbot - 0.2 && t < tbot + 1.2) { const hk = pop(tbot - 0.2, t); s += `<text x="1080" y="${f1(880 - 60 * sm(tbot, tbot + 1.2, t))}" font-family="Black" font-size="${f1(90 * hk)}" fill="#ff4f8a" stroke="${N}" stroke-width="8" paint-order="stroke" text-anchor="middle" opacity="${f1(1 - sm(tbot + 0.8, tbot + 1.2, t))}">\u2665</text>`; }
    return s; };
  const B = () => { const cx = 1080, cy = 520, sc = 1.5, rot = -8, sp = sm(tbot + 0.8, tbot + 1.4, t), buzz = t > tch - 0.4 ? 1 : 0, vib = 5 * Math.sin(t * 90) * buzz;
    let s = male(cx, cy, sc, rot, wings(0, { still: -20, blur: 0 }), { tailSpread: 1 + 0.9 * sp, tailFan: [-vib, 0, 0, 0, vib] });
    // tip of the outer tail feather (index 4) in screen space
    const a4 = (148 + 14 * (1 + 0.9 * sp)) * Math.PI / 180, [tx, ty] = bptB(cx, cy, sc, rot, 440 + Math.cos(a4) * 220, 374 + Math.sin(a4) * 220);
    if (buzz) for (let i = 0; i < 4; i++) { const r = ((t - tch + 0.4) * 300 + i * 90) % 360; s += `<path d="M${f1(tx - r * 0.7)} ${f1(ty - r * 0.7)} A${f1(r)} ${f1(r)} 0 0 0 ${f1(tx - r * 0.7)} ${f1(ty + r * 0.7)}" stroke="#fff" stroke-width="10" fill="none" opacity="${f1(1 - r / 360)}"/>`; }
    // zoom bubble on one feather
    const g = pop(at('h24', 'tail feathers') - 0.1, t); if (g > 0) { const bx = 400, by = 420, R = 190;
      s += `<path d="M${f1(tx)} ${f1(ty)} L${bx + 60} ${by + R - 6}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12"/>`;
      let f = ''; for (let i = buzz ? 3 : 0; i >= 0; i--) f += `<g transform="translate(-230 ${f1((i ? (i % 2 ? 1 : -1) * i * 9 : 0) + vib * 2)}) rotate(-8)" opacity="${f1(i ? 0.25 : 1)}">${featherD(460, 58, '#3d6450')}</g>`;
      s += `<g transform="translate(${bx} ${by}) scale(${f1(g * 100) / 100})"><defs><clipPath id="fz24"><circle r="${R}"/></clipPath></defs><circle r="${R + 12}" fill="${N}"/><circle r="${R}" fill="#ffe9c2"/><g clip-path="url(#fz24)">${f}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="8"/></g>`;
      s += fade(bx, by - R - 50, 'TAIL FEATHERS', t, at('h24', 'tail feathers'), { size: 70, fill: '#fff', stroke: N, sw: 12 }); }
    if (buzz) s += fade(640, 300, 'BZZZ', t, tch - 0.3, { size: 60, fill: K.yellow, stroke: N, sw: 10 });
    s += big(1480, 900, 'CHIRP!', t, tch, { size: 190, fill: K.yellow, stroke: N, sw: 18, rot: -6 });
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
const bush = (x, y, r) => `<g fill="#3fae5a" stroke="${N}" stroke-width="7"><circle cx="${f1(x - r * 0.6)}" cy="${f1(y + 10)}" r="${f1(r * 0.7)}"/><circle cx="${f1(x + r * 0.6)}" cy="${f1(y + 14)}" r="${f1(r * 0.75)}"/><circle cx="${f1(x)}" cy="${f1(y - r * 0.25)}" r="${f1(r)}"/></g><path d="M${f1(x - r * 0.5)} ${f1(y - r * 0.5)} q${f1(r * 0.3)} -${f1(r * 0.2)} ${f1(r * 0.6)} 0" stroke="#7fe08f" stroke-width="7" fill="none" stroke-linecap="round" opacity=".7"/>`;
// 25 eats until nearly double weight, then crosses the Gulf of Mexico nonstop
export function h25(t) {
  const tr = at('h25', 'ruby-throated'), td = at('h25', 'doubles its weight'), tg = at('h25', 'Then it flies across'), tk = at('h25', 'eight hundred'), tn = at('h25', 'nonstop');
  const A = () => { const fat = sm(td - 1.2, td + 0.4, t), by = 840;
    let s = '';
    // flowers on stems growing out of a bush, mouths toward the bird
    for (const [fx, fy, r] of [[1060, 600, -70], [1160, 700, -58]]) { const [ex, ey] = fpt(fx, fy, 1.0, r, 0, 200); s += stemTo(ex, ey, 1180, 1000); }
    s += bush(1180, 1040, 150);
    for (const [fx, fy, r] of [[1060, 600, -70], [1160, 700, -58]]) s += flowerT(fx, fy, 1.0, { rot: r, stem: 0 });
    s += branch(-60, 1000, by, 26) + onBranch(560, by, 0.95, { puff: 1.7 * fat, th: 26 });
    // nectar sips flying from the flower to the beak
    if (t < td + 0.4) for (let i = 0; i < 3; i++) { const k = ((t * 0.9 + i / 3) % 1); s += `<circle cx="${f1(lerp(1010, 960, k))}" cy="${f1(lerp(590, 575, k))}" r="${f1(9 * (1 - k) + 3)}" fill="#ffd23f" stroke="${N}" stroke-width="3" opacity="${f1(1 - k)}"/>`; }
    const pk = t > tr - 0.2 && t < td - 0.6 ? pop(tr - 0.2, t) * (1 - sm(td - 1.0, td - 0.6, t)) : 0;
    const rk = sm(td - 1.2, td - 0.8, t);
    if (rk > 0) s += `<g opacity="${f1(rk)}">${readout(1600, 470, `${(3 + 3 * fat * 0.95).toFixed(1)} G`, '', { size: 130 })}</g>`;
    s += big(1620, 880, 'ALMOST x2', t, td, { size: 100, fill: K.yellow, stroke: N, sw: 14 });
    s += photo('ruby', 1420, 470, 760, 500, pk, { cap: 'RUBY-THROATED' });
    s += big(960, 130, 'FUEL UP!', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  const B = () => { const v = { lon0: -103, lon1: -76, lat0: 14, lat1: 34, x: 120, y: 90, w: 1100, h: 900 }, P = proj(v);
    let s = mapCard(v, 'mc25');
    // little waves on the gulf
    for (const [lo, la] of [[-93, 27], [-87, 26.5], [-95, 23], [-91, 23.5], [-86, 24], [-92, 20.5]]) { const [x, y] = P(lo, la); s += `<path d="M${f1(x - 30)} ${f1(y)} q15 -12 30 0 q15 12 30 0" stroke="#fff" stroke-width="5" fill="none" opacity=".7" stroke-linecap="round"/>`; }
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
  const rufous = birdSolid({ pal: 'rufous' });
  s += svg + `<g transform="translate(${f1(hx)} ${f1(hy)}) rotate(${f1(ang)})">${placeB(0, 0, 0.18, rufous + wings(t, { rate: 7, amp: 50, blur: 1 }))}</g>`;
  s += photo('rufous', 1665, 330, 380, 400, pop(0.3, t), { cap: 'RUFOUS', rot: 2 });
  if (t > tm - 0.2) s += readout(1670, 790, count(6000, t, tm - 0.2, 1.4) + '+', 'KM', { size: 110 });
  s += big(1665, 990, 'EPIC TRIP!', t, tl, { size: 74, fill: K.yellow, stroke: N, sw: 14 });
  return s;
}

// walnut half (top view) with wrinkles and a shine
const walnut = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><path d="M-150 0 C-150 -90 -80 -140 0 -140 C80 -140 150 -90 150 0 C150 30 120 40 0 40 C-120 40 -150 30 -150 0Z" fill="#b07a3e" stroke="${N}" stroke-width="9"/>
  <path d="M-110 -20 C-96 -60 -70 -84 -40 -96 C-50 -70 -30 -50 -40 -20 M-60 10 C-40 -40 0 -60 40 -70 C30 -40 50 -20 30 6 M20 20 C40 -20 80 -50 110 -40 C96 -20 110 0 100 20 M0 -130 C10 -100 -10 -80 0 -50 M-120 10 C-100 0 -80 -10 -60 -6 M60 -110 C70 -90 90 -86 110 -90" stroke="#7d5226" stroke-width="8" fill="none" stroke-linecap="round"/>
  <path d="M-100 -90 C-70 -118 -30 -128 10 -126" stroke="#e0b07a" stroke-width="10" fill="none" stroke-linecap="round" opacity=".8"/>
  <path d="M-150 0 C-150 30 -120 40 0 40 C120 40 150 30 150 0 C120 14 -120 14 -150 0Z" fill="#8a5a2b" stroke="${N}" stroke-width="6"/></g>`;
// woven nest cup (side view): fibres, lichen flakes outside, soft plant-down rim, spider silk wraps. inner = svg drawn inside the cup (chicks, eggs)
const nest = (x, y, s, { fluff = 1, silk = 1, wide = 1, inner = '' } = {}) => { const CUP = 'M-160 -60 C-160 60 -90 120 0 120 C90 120 160 60 160 -60 C100 -40 -100 -40 -160 -60Z', id = 'nc' + Math.round(x * 10 + y);
  let g = `<ellipse cx="0" cy="-60" rx="160" ry="30" fill="#6e4f2c" stroke="${N}" stroke-width="8"/><ellipse cx="0" cy="-54" rx="130" ry="18" fill="#4f3820"/>` + inner;
  g += `<defs><clipPath id="${id}"><path d="${CUP}"/></clipPath></defs><path d="${CUP}" fill="#b8975f"/><g clip-path="url(#${id})">`;
  seed(12); for (let i = 0; i < 44; i++) { const y0 = -60 + rnd() * 180, x0 = -180 + rnd() * 120, x1 = x0 + 160 + rnd() * 200, ym = y0 + (rnd() - 0.5) * 50;
    g += `<path d="M${f1(x0)} ${f1(y0)} Q${f1((x0 + x1) / 2)} ${f1(ym + 18)} ${f1(x1)} ${f1(ym)}" stroke="${['#a88a5a', '#e0cfa3', '#8f7a4a', '#bfa776', '#9aa86a'][i % 5]}" stroke-width="${f1(3 + rnd() * 4)}" fill="none" stroke-linecap="round" opacity=".9"/>`; }
  for (let i = 0; i < 9; i++) { const a = 0.3 + rnd() * 2.5, r = 0.6 + rnd() * 0.3, cx = Math.cos(a) * 150 * r, cy = -20 + Math.sin(a) * 130 * r, q = 10 + rnd() * 8, col = ['#c3d2ad', '#a9bd94', '#d7e2c6'][i % 3];
    let d = ''; for (let k = 0; k < 7; k++) { const aa = k / 7 * Math.PI * 2, rr = q * (0.7 + 0.5 * ((k * 37 + i * 11) % 10) / 10); d += (k ? 'L' : 'M') + f1(cx + Math.cos(aa) * rr * 1.4) + ' ' + f1(cy + Math.sin(aa) * rr * 0.7); }
    g += `<path d="${d}Z" fill="${col}" stroke="#6f7f5e" stroke-width="2.5" stroke-linejoin="round"/>`; }
  g += `</g><path d="${CUP}" fill="none" stroke="${N}" stroke-width="9" stroke-linejoin="round"/>`;
  // plant down along the rim: soft white puffs with one shared outline
  if (fluff > 0) { let o = '', w = ''; seed(31); const n = Math.round(14 * Math.min(1, fluff)); for (let i = 0; i < n; i++) { const u = i / 13, px = -160 + 320 * u, py = -56 + 10 * Math.sin(u * Math.PI) + (rnd() - 0.5) * 8, r = 16 + rnd() * 10;
      o += `<circle cx="${f1(px)}" cy="${f1(py)}" r="${f1(r + 5)}"/>`; w += `<circle cx="${f1(px)}" cy="${f1(py)}" r="${f1(r)}"/>`; }
    g += `<g opacity="${f1(Math.min(1, fluff))}"><g fill="${N}">${o}</g><g fill="#fbf6ea">${w}</g></g>`; }
  // spider silk wraps with glints
  if (silk > 0) { for (let i = 0; i < 6; i++) { const y0 = -36 + i * 24, e = 158 - i * 14 - i * i * 1.2; g += `<path d="M${f1(-e)} ${f1(y0)} C-60 ${f1(y0 + 30)} 60 ${f1(y0 - 6)} ${f1(e)} ${f1(y0 + 12)}" stroke="#ffffff" stroke-width="3.5" fill="none" opacity="${f1(0.95 * silk)}"/>`; }
    for (const [gx, gy] of [[-70, 2], [40, 30], [100, -10], [-20, 70]]) g += sparkleS(gx, gy, 12 * silk); }
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * wide * 100) / 100} ${f1(s * 100) / 100})">${g}</g>`; };
const sparkleS = (x, y, r) => r <= 0 ? '' : `<path d="M${f1(x)} ${f1(y - r)} Q${f1(x + r * 0.2)} ${f1(y - r * 0.2)} ${f1(x + r)} ${f1(y)} Q${f1(x + r * 0.2)} ${f1(y + r * 0.2)} ${f1(x)} ${f1(y + r)} Q${f1(x - r * 0.2)} ${f1(y + r * 0.2)} ${f1(x - r)} ${f1(y)} Q${f1(x - r * 0.2)} ${f1(y - r * 0.2)} ${f1(x)} ${f1(y - r)}Z" fill="#fff"/>`;
// fuzzy grey chick (nest-local coords, centre x,y, radius r); open > 0 = gaping yellow beak
const chick = (x, y, r, open = 0, lift = 0) => { let fz = ''; for (let i = 0; i <= 28; i++) { const a = i / 28 * Math.PI * 2, rr = r * (1 + 0.07 * Math.sin(i * 2.7) + 0.05 * (i % 2)); fz += (i ? 'L' : 'M') + f1(x + Math.cos(a) * rr) + ' ' + f1(y + Math.sin(a) * rr * 0.92); }
  const hx = x + r * 0.35, hy = y - r * 0.55 - lift, hr = r * 0.48;
  let s = `<path d="${fz}Z" fill="#8d8f9c" stroke="${N}" stroke-width="5" stroke-linejoin="round"/><ellipse cx="${f1(x + r * 0.1)}" cy="${f1(y + r * 0.25)}" rx="${f1(r * 0.6)}" ry="${f1(r * 0.45)}" fill="#b4b6c2"/>`;
  s += `<circle cx="${f1(hx)}" cy="${f1(hy)}" r="${f1(hr)}" fill="#8d8f9c" stroke="${N}" stroke-width="5"/>`;
  s += `<path d="M${f1(hx - hr * 0.25)} ${f1(hy - hr * 0.95)} q6 -14 12 0 M${f1(hx + hr * 0.1)} ${f1(hy - hr * 0.98)} q6 -12 10 2" stroke="${N}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M${f1(hx - hr * 0.05)} ${f1(hy - hr * 0.15)} q${f1(hr * 0.18)} ${f1(hr * 0.16)} ${f1(hr * 0.36)} 0" stroke="${N}" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  if (open > 0) s += `<path d="M${f1(hx + hr * 0.55)} ${f1(hy - hr * 0.2)} L${f1(hx + hr * 0.9)} ${f1(hy - hr * (1.3 + 0.6 * open))} L${f1(hx + hr * 1.15)} ${f1(hy - hr * 0.3)}Z" fill="#ffd23f" stroke="${N}" stroke-width="4" stroke-linejoin="round"/><path d="M${f1(hx + hr * 0.62)} ${f1(hy - hr * 0.35)} L${f1(hx + hr * 0.9)} ${f1(hy - hr * (1.1 + 0.5 * open))} L${f1(hx + hr * 1.06)} ${f1(hy - hr * 0.4)}Z" fill="#ff7a59"/>`;
  else s += `<path d="M${f1(hx + hr * 0.8)} ${f1(hy - hr * 0.1)} L${f1(hx + hr * 1.6)} ${f1(hy + hr * 0.05)} L${f1(hx + hr * 0.85)} ${f1(hy + hr * 0.3)}Z" fill="#3a3a44" stroke="${N}" stroke-width="3" stroke-linejoin="round"/>`;
  return s; };
// 27 nest: half a walnut, plant fluff, spider silk that stretches as the chicks grow
export function h27(t) {
  const tw = at('h27', 'half a walnut'), tf = at('h27', 'soft plant fluff'), tsk = at('h27', 'spider silk'), tst = at('h27', 'The silk stretches');
  const fl = sm(tf - 0.2, tf + 0.8, t), sk = sm(tsk - 0.2, tsk + 1.0, t), grow = sm(tst, tst + 2.4, t);
  const nx = lerp(960, 1360, sm(tw - 0.4, tw + 0.2, t) * (1 - sm(tf - 0.6, tf - 0.1, t)));
  let s = branch(160, 1780, 900, 34);
  let inner = '';
  if (grow > 0) for (const i of [-1, 1]) inner += chick(i * (44 + 26 * grow) / (1 + 0.3 * grow), -70 - 8 * grow, 30 + 22 * grow, 0);
  s += nest(nx, 760, 2.0, { fluff: Math.max(0.25, fl), silk: sk, wide: 1 + 0.3 * grow, inner });
  if (t > tw - 0.4 && t < tf - 0.1) { const k = sm(tw - 0.4, tw, t) * (1 - sm(tf - 0.6, tf - 0.1, t)); s += `<g opacity="${f1(k)}">${walnut(520, 700, 2.0)}${label(520, 900 + 80, 'HALF A WALNUT', 70)}</g>` + `<text x="940" y="750" font-family="Black" font-size="160" fill="${N}" text-anchor="middle" opacity="${f1(k)}">=</text>`; }
  // zoom bubbles: plant fluff, then spider silk
  const bub = (bx, by, k, body, id) => k <= 0 ? '' : `<g transform="translate(${bx} ${by}) scale(${f1(k * 100) / 100})"><defs><clipPath id="${id}"><circle r="150"/></clipPath></defs><circle r="162" fill="${N}"/><circle r="150" fill="#fff4dc"/><g clip-path="url(#${id})">${body}</g><circle r="150" fill="none" stroke="#fff" stroke-width="8"/></g>`;
  const fb = pop(tf + 0.1, t) * (1 - sm(tsk - 0.3, tsk, t));
  if (fb > 0) { let b = ''; seed(5); for (let i = 0; i < 9; i++) { const x = -110 + rnd() * 220, y = -90 + rnd() * 180; for (let j = 0; j < 12; j++) { const a = j / 12 * Math.PI * 2; b += `<path d="M${f1(x)} ${f1(y)} q${f1(Math.cos(a) * 20)} ${f1(Math.sin(a) * 20 - 8)} ${f1(Math.cos(a) * 40)} ${f1(Math.sin(a) * 40)}" stroke="#d8cfbc" stroke-width="3" fill="none"/>`; } b += `<circle cx="${f1(x)}" cy="${f1(y)}" r="6" fill="#a8916a"/>`; }
    s += bub(400, 330, fb, b, 'fb27') + fade(400, 560, 'PLANT FLUFF', t, tf + 0.2, { size: 64, fill: '#fff', stroke: N, sw: 12 }); }
  const sb = pop(tsk + 0.1, t) * (1 - sm(tst - 0.3, tst, t));
  if (sb > 0) { let b = ''; for (let i = 0; i < 9; i++) b += `<path d="M-160 ${-120 + i * 30} C-60 ${-90 + i * 30} 40 ${-150 + i * 34} 160 ${-110 + i * 32}" stroke="#ffffff" stroke-width="5" fill="none"/><path d="M-160 ${-120 + i * 30} C-60 ${-90 + i * 30} 40 ${-150 + i * 34} 160 ${-110 + i * 32}" stroke="#9fb3c8" stroke-width="2" fill="none" stroke-dasharray="2 10"/>`;
    for (let i = 0; i < 7; i++) b += `<path d="M${-120 + i * 40} -160 L${-100 + i * 36} 160" stroke="#ffffff" stroke-width="3" opacity=".8"/>`;
    s += bub(1520, 330, sb, `<rect x="-160" y="-160" width="320" height="320" fill="#5e6e86"/>` + b + sparkleS(-40, -20, 18) + sparkleS(60, 50, 14), 'sb27') + fade(1520, 560, 'SPIDER SILK', t, tsk + 0.2, { size: 64, fill: '#fff', stroke: N, sw: 12 }); }
  if (t > tst) s += arrow(nx - 420, 1000, nx - 600, 1000, { w: 16 }) + arrow(nx + 420, 1000, nx + 600, 1000, { w: 16 }) + fade(nx, 1010, 'STRETCHES', t, tst + 0.3, { size: 70, fill: '#fff', stroke: N, sw: 12 });
  s += big(960, 130, 'TINY NEST', t, 0.3, { size: 130, fill: '#fff', stroke: N, sw: 16 });
  return s;
}

// glossy jelly bean
const bean = (x, y, r, col) => `<g transform="translate(${x} ${y}) rotate(${r})"><path d="M-70 -20 C-70 -60 -20 -66 0 -44 C20 -66 70 -60 70 -20 C70 30 40 52 0 52 C-40 52 -70 30 -70 -20Z" fill="${col}" stroke="${N}" stroke-width="7"/><path d="M-46 -26 C-40 -44 -24 -46 -14 -36" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" opacity=".75"/></g>`;
// 28 two eggs the size of jelly beans; mom raises the chicks alone
export function h28(t) {
  const tj = at('h28', 'jelly bean'), tm = at('h28', 'The mother raises');
  const A = () => { let s = branch(80, 1200, 900, 32, { leaves: 0 });
    let eggs = ''; for (const [x, y, r] of [[-38, -66, -10], [40, -64, 12]]) eggs += `<ellipse cx="${x}" cy="${y}" rx="28" ry="38" transform="rotate(${r} ${x} ${y})" fill="#fffdf6" stroke="${N}" stroke-width="4"/><ellipse cx="${x - 8}" cy="${y - 14}" rx="7" ry="11" fill="#fff" transform="rotate(${r} ${x} ${y})"/>`;
    s += nest(640, 760, 2.1, { inner: eggs });
    s += `<text x="640" y="330" font-family="Black" font-size="120" fill="#fff" stroke="${N}" stroke-width="14" paint-order="stroke" text-anchor="middle">2 EGGS</text>`;
    if (t > tj - 0.3) { const k = pop(tj - 0.3, t); s += `<g transform="translate(1420 640) scale(${f1(k * 100) / 100})">${bean(-80, 0, -24, '#ff4f7b')}${bean(80, 6, 18, '#7a5bff')}</g>` + label(1420, 830, 'JELLY BEANS', 70) + big(1100, 690, '=', t, tj, { size: 160, fill: N }); }
    return s; };
  const B = () => { let s = branch(60, 1500, 900, 32, { leaves: 1 });
    const feed = Math.sin(t * 5), open = 0.5 + 0.5 * Math.max(0, Math.sin(t * 5 + 1));
    const inner = chick(-46, -86, 46, open, 6) + chick(52, -80, 44, 1 - open * 0.6, 2);
    s += nest(640, 760, 2.1, { wide: 1.1, inner });
    // mother hovering over the chicks, beak down toward the gaping mouth
    s += placeB(880 + 6 * feed, 320 + 10 * feed, 0.72, birdSolid({ throat: 0 }) + wings(t, { rate: 9, amp: 50 }), { rot: -40, flip: true });
    s += big(1480, 560, 'SUPER MOM', t, at('h28', 'all by herself'), { size: 120, fill: '#fff', stroke: N, sw: 16 });
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
const LONGBEAK = 'M745 184 C880 186 1080 194 1230 199 C1080 202 880 206 746 210Z';
export function h30(t) {
  const tb = at('h30', 'beak longer'), tp = at('h30', 'perfect for reaching');
  const sword = (o = {}) => birdSolid({ pal: 'sword', beakD: LONGBEAK, ...o });
  const A = () => { const cx = 640, cy = 520, sc = 1.1, ph = pop(0.2, t) * (1 - sm(tb - 0.3, tb + 0.1, t)), gk = 1 - 0.35 * sm(0.2, 0.6, t) * (1 - sm(tb - 0.3, tb + 0.1, t));
    let g = placeB(cx, cy + bobB(t, 6), sc, sword() + wings(t, { rate: 7, amp: 50 }));
    const yb = 880, [b0] = toB(cx, cy, sc, 420, 0), [b1] = toB(cx, cy, sc, 745, 0), [k1] = toB(cx, cy, sc, 1230, 0), k = eo(tb, tb + 0.8, t);
    if (k > 0) { g += `<rect x="${f1(b0)}" y="${yb - 20}" width="${f1((b1 - b0) * k)}" height="70" rx="35" fill="#fff" stroke="${N}" stroke-width="7"/><rect x="${f1(b1)}" y="${yb + 80}" width="${f1((k1 - b1) * k)}" height="70" rx="35" fill="${K.yellow}" stroke="${N}" stroke-width="7"/>`;
      g += fade(b0 - 24, yb + 10, 'BODY', t, tb + 0.4, { size: 72, fill: N, anchor: 'end' }) + fade(b1 - 24, yb + 110, 'BEAK', t, tb + 0.6, { size: 72, fill: N, anchor: 'end' }); }
    let s = `<g transform="translate(960 560) scale(${f1(gk * 1000) / 1000}) translate(-960 -560)" opacity="${f1(lerp(0.5, 1, (gk - 0.65) / 0.35))}">${g}</g>`;
    s += photo('sword1', 960, 560, 1100, 640, ph, { cap: 'SWORD-BILLED HUMMINGBIRD' });
    s += big(960, 120, 'SWORD-BILLED', t, 0.4, { size: 120, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  const B = () => { const sc = 0.9, ins = sm(tp + 0.2, tp + 1.4, t), cx = lerp(380, 520, ins), cy = 640;
    const [, by] = toB(520, cy, sc, 1230, 199), fx = 1180;
    // long hanging flower in cutaway: vine from the top, tube opening to the left, nectar at the far end
    let g = `<path d="M1980 -20 C1880 120 1900 260 1800 ${f1(by - 120)} C1760 ${f1(by - 40)} 1720 ${f1(by)} 1700 ${f1(by)}" stroke="${N}" stroke-width="26" fill="none" stroke-linecap="round"/><path d="M1980 -20 C1880 120 1900 260 1800 ${f1(by - 120)} C1760 ${f1(by - 40)} 1720 ${f1(by)} 1700 ${f1(by)}" stroke="#2f9a4f" stroke-width="16" fill="none" stroke-linecap="round"/>`;
    g += leaf(1890, 150, -150, 1.4) + leaf(1880, 280, -20, 1.3) + leaf(1820, by - 160, 200, 1.2);
    g += `<path d="M${fx} ${f1(by - 70)} C1400 ${f1(by - 46)} 1600 ${f1(by - 26)} 1700 ${f1(by - 20)} L1700 ${f1(by + 20)} C1600 ${f1(by + 26)} 1400 ${f1(by + 46)} ${fx} ${f1(by + 70)}Z" fill="#fff3a8" fill-opacity=".75" stroke="${N}" stroke-width="8" stroke-linejoin="round"/>`;
    g += `<path d="M1600 ${f1(by - 18)} C1640 ${f1(by - 4)} 1660 ${f1(by + 6)} 1696 ${f1(by + 8)} L1696 ${f1(by + 18)} C1650 ${f1(by + 22)} 1620 ${f1(by + 22)} 1600 ${f1(by + 22)}Z" fill="#ffc21f" opacity=".9"/>`;
    g += `<path d="M${fx} ${f1(by - 70)} C${fx - 40} ${f1(by - 120)} ${fx - 80} ${f1(by - 120)} ${fx - 100} ${f1(by - 100)} C${fx - 60} ${f1(by - 70)} ${fx - 60} ${f1(by + 70)} ${fx - 100} ${f1(by + 100)} C${fx - 80} ${f1(by + 120)} ${fx - 40} ${f1(by + 120)} ${fx} ${f1(by + 70)}" fill="#ffe46a" stroke="${N}" stroke-width="8" stroke-linejoin="round"/>`;
    for (let i = 0; i < 6; i++) g += `<path d="M${1240 + i * 70} ${f1(by - 60 + i * 7)} L${1240 + i * 70} ${f1(by + 60 - i * 7)}" stroke="#e8c84a" stroke-width="4" opacity=".6"/>`;
    g += placeB(cx, cy, sc, sword() + wings(t, { rate: 9, amp: 50 }));
    if (ins > 0.9) g += `<circle cx="1660" cy="${f1(by + 10)}" r="${f1(20 + 14 * Math.sin(t * 8))}" fill="none" stroke="#fff" stroke-width="6" opacity=".9"/>`;
    g += tag(1640, by + 30, 1600, 980, 'NECTAR', t, tp + 1.2, { col: K.yellow, size: 60 });
    const ph = pop(tp + 1.6, t), gk = 1 - 0.35 * sm(tp + 1.5, tp + 1.9, t);
    let s = `<g transform="translate(960 560) scale(${f1(gk * 1000) / 1000}) translate(-960 -560)" opacity="${f1(lerp(0.5, 1, (gk - 0.65) / 0.35))}">${g}</g>`;
    s += photo('sword2', 960, 580, 1060, 640, ph, { rot: 2 });
    s += big(960, 120, 'DEEP FLOWERS', t, tp, { size: 120, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  return t < tp - 0.3 ? A() : xfade(t, tp - 0.3, 0.6, A, B);
}

// dog silhouette (side view, facing right), roughly 760 x 520 around (0,0); feet at y=230
const DOG = `M405 -95 C415 -88 415 -70 400 -64 C370 -56 335 -52 305 -48 C285 -44 270 -30 262 -14 C252 8 244 30 232 52 C228 100 230 170 232 212 C242 216 258 220 262 228 C260 234 240 234 210 232 C208 180 204 110 196 64 C180 70 160 66 150 60
 C80 40 -20 34 -80 40 C-84 70 -90 96 -100 116 C-110 136 -128 156 -134 176 C-136 196 -134 212 -130 222 C-118 224 -106 228 -104 232 C-120 234 -150 234 -166 232 C-170 210 -172 194 -176 180 C-190 150 -214 100 -224 50 C-232 10 -232 -30 -222 -62
 C-262 -90 -300 -150 -282 -214 C-268 -172 -244 -124 -206 -98 C-120 -112 40 -112 150 -102 C190 -110 214 -140 228 -172 L240 -252 L282 -196 C292 -198 302 -198 312 -198 L336 -258 L348 -176 C356 -150 368 -122 382 -114 C394 -108 402 -102 405 -95Z
 M180 60 C178 120 176 190 180 214 C188 218 200 222 204 230 L156 230 C156 190 152 120 150 60Z
 M-50 40 C-50 80 -60 110 -74 130 C-86 150 -92 176 -90 214 C-82 220 -72 224 -70 230 L-108 230 C-112 200 -110 170 -102 150 C-92 120 -90 80 -92 42Z`;
// 31 recap labels on the opened bird, then the next animal as a mystery silhouette
export function h31(t) {
  const tw = at('h31', 'Wings that spin'), th = at('h31', 'A heart'), tt = at('h31', 'A brushy tongue'), tm = at('h31', 'super memory'), to = at('h31', 'switch off'), tp = at('h31', 'Tiny, but'), tq = at('h31', 'What should we open');
  const A = () => { const cx = 900, cy = 600 + bobB(t, 8, 1.6), sc = 1.4, P = n => toB(cx, cy, sc, ...PT[n]);
    const bg = t > tm && t < to ? 1 : 0;
    let s = placeB(cx, cy, sc, birdInside({ tongue: 1, brain: 1, brainGlow: bg, heartK: 1 + 0.12 * Math.max(0, Math.sin(t * 14)), glow: t > th && t < tt ? 'heart' : null }) + wings(t, { rate: 1.1, amp: 22, blur: 0, bones: 1 }));
    s += tag(...P('shoulder'), 300, 430, 'WINGS', t, tw, { col: '#fff' }) + tag(...P('heart'), 1440, 940, 'HEART', t, th, { col: K.red, txt: '#fff' })
      + tag(...toB(cx, cy, sc, 960, 198), 1640, 330, 'TONGUE', t, tt, { col: K.yellow }) + tag(...toB(cx, cy, sc, 670, 140), 1240, 130, 'MEMORY', t, tm, { col: C.brain })
      + tag(...P('liver'), 560, 960, 'NIGHT MODE', t, to, { col: N, txt: '#fff' });
    s += big(1480, 700, 'TINY BUT MIGHTY', t, tp, { size: 84, fill: K.yellow, stroke: N, sw: 14 });
    return s; };
  const B = () => { const k = pop(tq + 0.1, t, 0.6), cx = 960, cy = 560;
    let s = `<defs><radialGradient id="rb31"><stop offset="0" stop-color="#7fd0ff"/><stop offset="1" stop-color="#1f6fd1"/></radialGradient>
      <filter id="paint31" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="16"/><feGaussianBlur stdDeviation="3.5"/></filter></defs>`;
    // spinning ray burst behind (quiz-show style)
    let rays = ''; for (let i = 0; i < 24; i++) { const a0 = (i / 24) * Math.PI * 2 + t * 0.25, a1 = a0 + Math.PI / 24; rays += `<path d="M${cx} ${cy} L${f1(cx + Math.cos(a0) * 1400)} ${f1(cy + Math.sin(a0) * 1400)} L${f1(cx + Math.cos(a1) * 1400)} ${f1(cy + Math.sin(a1) * 1400)}Z" fill="#ffffff" opacity=".16"/>`; }
    s += `<rect x="0" y="0" width="1920" height="1080" fill="url(#rb31)" opacity="${f1(Math.min(1, k))}"/><g opacity="${f1(Math.min(1, k))}">${rays}</g>`;
    if (k > 0) { s += `<g transform="translate(${cx} ${cy + 20}) scale(${f1(k * 100) / 100})"><g filter="url(#paint31)"><path d="${DOG}" fill="#0b0f1e"/>
        <path d="M-330 250 C-200 236 200 240 380 256" stroke="#0b0f1e" stroke-width="22" fill="none" stroke-linecap="round" opacity=".7"/><circle cx="-320" cy="-40" r="14" fill="#0b0f1e" opacity=".8"/><circle cx="420" cy="20" r="10" fill="#0b0f1e" opacity=".8"/></g>
        <text x="40" y="60" font-family="Black" font-size="300" fill="#ffffff" text-anchor="middle">?</text></g>`; }
    s += big(960, 140, 'WHAT NEXT?', t, tq, { size: 150, fill: '#fff', stroke: N, sw: 18 });
    s += big(960, 990, 'TELL US IN THE COMMENTS', t, at('h31', 'Tell us'), { size: 80, fill: N, stroke: '#fff', sw: 12 });
    return s; };
  return t < tq - 0.3 ? A() : xfade(t, tq - 0.3, 0.5, A, B);
}
