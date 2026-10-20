// vertical scenes for the hummingbird shorts b04-b06 (see vs1.mjs for the conventions)
import { K, f1, clamp, sm, eo, pop, lerp, big, tag, fade, xfade, count, cross } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from '/tmp/claude-0/hb2/tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, C, BIRD, PAL, fly, onBranch, branch, flowerT, readout, card, arrow, bobB, photo, speed, bptB, fpt, stemTo } from '/tmp/claude-0/hb2/ha.mjs';
import { proj } from '/tmp/claude-0/hb2/maps.mjs';
import { mapCard, route, label, featherD, sparkle, THROAT, bush } from '/tmp/claude-0/hb2/s3.mjs';
import { hat, N, W, H } from './vs1.mjs';

// real photo in a white box that can zoom toward a point (fx, fy as 0..1 of the photo)
export const photoZ = (name, x, y, w, h, z = 1, fx = 0.5, fy = 0.5, id = 'pz') => {
  const px = -w / 2 + fx * w, py = -h / 2 + fy * h;
  return `<g transform="translate(${f1(x)} ${f1(y)})"><rect x="${f1(-w / 2 - 8)}" y="${f1(-h / 2 - 4)}" width="${f1(w + 44)}" height="${f1(h + 44)}" rx="22" fill="#000" opacity=".2"/>
  <rect x="${f1(-w / 2 - 22)}" y="${f1(-h / 2 - 22)}" width="${f1(w + 44)}" height="${f1(h + 44)}" rx="22" fill="#fff" stroke="${N}" stroke-width="7"/>
  <clipPath id="${id}"><rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}" rx="10"/></clipPath>
  <g clip-path="url(#${id})"><g transform="translate(${f1(px)} ${f1(py)}) scale(${f1(z * 1000) / 1000}) translate(${f1(-px)} ${f1(-py)})"><use href="#P_${name}" x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}"/></g></g></g>`; };

// ───────── b04 FLIES BACKWARDS ─────────
const b04h = t => { const ts = hat('b04', 'secret'), tsh = hat('b04', 'shoulder');
  const A = () => { const x = 700 - 110 * t;
    let s = fly(x, 960 + bobB(t, 8), 1.0, t, { rate: 7, amp: 55 });
    for (let i = 0; i < 4; i++) s += `<path d="M${f1(x + 430 + i * 30)} ${f1(860 + i * 60)} L${f1(x + 600 + i * 50)} ${f1(860 + i * 60)}" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".8"/>`;
    s += arrow(820, 560, 260, 560, { col: K.red, w: 22, head: 64 });
    s += big(540, 1430, 'BACKWARDS?!', t, hat('b04', 'backwards'), { size: 120, fill: '#fff', stroke: N, sw: 16 });
    return s; };
  const B = () => { const sc = 1.45, cx = 520, cy = 1080, [sx, sy] = toB(cx, cy, sc, 600, 226);
    let s = placeB(cx, cy, sc, birdInside({}) + wings(0, { still: -30 + 8 * Math.sin(t * 2), blur: 0, bones: 1 }));
    const k = pop(tsh, t);
    if (k > 0) s += `<circle cx="${f1(sx)}" cy="${f1(sy)}" r="${f1(50 * k + 6 * Math.sin(t * 8))}" fill="none" stroke="${K.yellow}" stroke-width="12"/>`;
    s += tag(sx, sy, 540, 1460, 'SHOULDER', t, tsh + 0.1, { col: K.yellow, size: 80 });
    return s; };
  return t < ts - 0.3 ? A() : xfade(t, ts - 0.3, 0.5, A, B); };
// wing seen end-on as a two-tone blade (top white, underside green); the shoulder twist flips it; air goes down both ways
const b04a = t => { const tt = at('h06', 'twist its wing'), tfw = at('h06', 'on the way forward'), tbk = at('h06', 'on the way back');
  const fw = sm(tfw - 0.4, tfw + 0.9, t), bk = sm(tbk - 0.4, tbk + 0.9, t), x = 960 + 330 * fw - 660 * bk;
  const fl = t < tfw - 0.4 ? Math.cos((t - tt) * 2.6) : lerp(1, -1, sm(tbk - 0.7, tbk - 0.1, t));
  let g = `<path d="M240 420 L1680 420" stroke="#fff" stroke-width="6" stroke-dasharray="6 22" stroke-linecap="round" opacity=".7"/>`;
  const tilt = -16 * Math.sign(fl || 1) * Math.min(1, Math.abs(fl) * 2), sy = Math.max(0.12, Math.abs(fl)) * Math.sign(fl || 1);
  g += `<g transform="translate(${f1(x)} 520) rotate(${f1(tilt)}) scale(1.3 ${f1(sy * 130) / 100})"><path d="M-260 0 C-200 -70 180 -58 260 0 Z" fill="#ffffff" stroke="${N}" stroke-width="9" stroke-linejoin="round"/><path d="M-260 0 C-180 34 180 30 260 0 Z" fill="${C.back}" stroke="${N}" stroke-width="9" stroke-linejoin="round"/></g>`;
  if (t < tfw - 0.4 || (t > tbk - 0.8 && t < tbk + 0.2)) g += `<path d="M${f1(x - 120)} 400 A140 110 0 0 1 ${f1(x + 120)} 400" fill="none" stroke="${K.yellow}" stroke-width="14" stroke-linecap="round"/><path d="M${f1(x + 150)} 392 L${f1(x + 108)} 372 L${f1(x + 112)} 420Z" fill="${K.yellow}" stroke="${N}" stroke-width="4"/>`;
  if (t > tfw - 0.4) { const dir = t > tbk - 0.4 ? -1 : 1, ak = sm(tfw - 0.4, tfw + 0.2, t) * (t > tbk - 0.7 && t < tbk - 0.2 ? 1 - sm(tbk - 0.7, tbk - 0.5, t) + sm(tbk - 0.4, tbk - 0.2, t) : 1);
    for (let i = 0; i < 3; i++) { const yy = 556 + i * 46, xd = x + dir * (150 - i * 150), R = 80 + i * 36, x0 = x + dir * 980;
      const d = `M${f1(x0)} ${yy} L${f1(xd + dir * R)} ${yy} Q${f1(xd)} ${yy} ${f1(xd)} ${yy + R} L${f1(xd)} 880`;
      g += `<g opacity="${f1(ak)}"><path d="${d}" stroke="#ffffff" stroke-width="22" fill="none" opacity=".3" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" stroke="#ffffff" stroke-width="22" fill="none" stroke-dasharray="50 50" stroke-dashoffset="${f1(-t * 260 - i * 30)}" stroke-linecap="round"/><path d="M${f1(xd - 32)} 856 L${f1(xd + 32)} 856 L${f1(xd)} 916Z" fill="#fff" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g>`; } }
  g += t > tbk - 0.4 ? arrow(x + 300, 300, x + 80, 300, { w: 16, col: K.yellow }) : t > tfw - 0.4 ? arrow(x - 300, 300, x - 80, 300, { w: 16, col: K.yellow }) : '';
  let s = `<g transform="translate(540 1000) scale(0.74) translate(-960 -600)">${g}</g>`;
  s += fade(60, 790, 'BACK', t, tt, { size: 62, fill: N, anchor: 'start' }) + fade(1020, 790, 'FORWARD', t, tt, { size: 62, fill: N, anchor: 'end' });
  s += big(540, 600, 'TWIST!', t, tt, { size: 150, fill: K.yellow, stroke: N, sw: 18 });
  s += t < tbk ? fade(540, 1430, 'AIR DOWN', t, tfw, { size: 100, fill: '#fff', stroke: N, sw: 14 }) : big(540, 1430, 'AIR DOWN AGAIN', t, tbk, { size: 92, fill: '#fff', stroke: N, sw: 14 });
  return s; };
const b04b = t => { const th = at('h07', 'hover'), tb = at('h07', 'backwards'), tu = at('h07', 'upside down');
  const A = () => fly(540, 960 + bobB(t), 1.05, t, { rate: 7, amp: 55 }) + big(540, 1440, 'NO OTHER BIRD', t, 0.4, { size: 104, fill: '#fff', stroke: N, sw: 16 });
  const B = () => { let s = '';
    for (const [y, w, t0] of [[500, 'HOVER', th], [840, 'BACKWARD', tb], [1180, 'UPSIDE DOWN', tu]]) { const cy = y + 160, k = pop(t0 - 0.2, t);
      if (k <= 0) { s += `<rect x="70" y="${y}" width="940" height="320" rx="40" fill="#fff" opacity=".25"/>`; continue; }
      s += `<g transform="translate(540 ${cy}) scale(${f1(k * 100) / 100}) translate(-540 ${-cy})">${card(70, y, 940, 320, '#fff', 0.92)}`;
      if (w === 'HOVER') s += `<circle cx="290" cy="${cy}" r="130" fill="none" stroke="${K.yellow}" stroke-width="8" stroke-dasharray="10 18"/>` + fly(290, cy + 10 + bobB(t, 4, 3), 0.42, t, { rate: 7, amp: 50 });
      if (w === 'BACKWARD') { const u = ((t - tb) * 0.5) % 1, bx = 370 - 170 * u; s += arrow(400, y + 60, 180, y + 60, { col: K.red, w: 14, head: 40 }) + fly(bx, cy + 30, 0.42, t, { rate: 7, amp: 50 }); }
      if (w === 'UPSIDE DOWN') { const r = 180 * sm(tu, tu + 0.8, t); s += fly(290, cy + 10, 0.42, t, { rate: 7, amp: 50, rot: r }) + `<path d="M170 ${y + 70} A120 120 0 0 1 410 ${y + 70}" fill="none" stroke="${K.red}" stroke-width="12"/>`; }
      s += `<text x="760" y="${cy + 28}" font-family="Black" font-size="${w.length > 9 ? 66 : 80}" fill="${N}" text-anchor="middle">${w}</text></g>`; }
    return s; };
  return t < th - 0.6 ? A() : xfade(t, th - 0.6, 0.5, A, B); };

// ───────── b05 NO RED?! ─────────
const RT = [0.43, 0.43]; // throat in ruby.jpg
const b05h = t => { const tr = hat('b05', 'red throat'), tn = hat('b05', 'no red'), z = lerp(1, 1.5, eo(tr - 0.2, tr + 1.2, t));
  const w = 940, h = 706, x = 540, y = 960;
  let s = photoZ('ruby', x, y, w, h, z, ...RT, 'pz5');
  const k = pop(tr, t), cx = x - w / 2 + RT[0] * w, cy = y - h / 2 + RT[1] * h;
  if (k > 0) s += `<circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(110 * k)}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="22 14"/>`;
  const pk = pop(tn, t);
  if (pk > 0) { s += `<g transform="translate(540 1490) scale(${f1(0.62 * pk * 100) / 100})"><path d="M-130 -110 L130 -110 L110 150 L-110 150Z" fill="#dfe6f0" stroke="${N}" stroke-width="10" stroke-linejoin="round"/><path d="M-130 -110 C-60 -60 60 -60 130 -110 L130 -40 C60 10 -60 10 -130 -40Z" fill="${K.red}"/><path d="M-60 -60 C-60 0 -40 40 -40 80" stroke="${K.red}" stroke-width="22" stroke-linecap="round"/><path d="M-130 -110 C-130 -220 130 -220 130 -110" stroke="${N}" stroke-width="10" fill="none"/></g>`;
    s += cross(540, 1490, 120, t, tn + 0.25); }
  return s; };
const b05a = t => { const tl = at('h23', 'tiny layers'), t1 = at('h23', 'Turn the bird'), t2 = at('h23', 'Turn it again');
  const rot = lerp(0, -10, sm(t1 - 0.2, t1 + 0.5, t)) + lerp(0, 22, sm(t2 - 0.2, t2 + 0.5, t));
  const on = t < t1 ? 0.75 : t < t2 ? 1 : lerp(1, 0, sm(t2, t2 + 0.5, t));
  const cx = 360, cy = 760, sc = 1.5, id = 'th5';
  const thr = `<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath></defs><g clip-path="url(#${id})"><path d="${THROAT}" fill="#2a0d18"/><path d="${THROAT}" fill="#ff1f45" opacity="${f1(on)}"/>${on > 0.9 ? `<path d="M690 226 L730 214 M700 246 L746 236 M716 268 L752 262" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>` : ''}</g>`;
  let s = placeB(cx, cy, sc, birdSolid({ throat: 0 }) + thr + wings(0, { still: -60, blur: 0 }), { rot });
  const [tx, ty] = bptB(cx, cy, sc, rot, 724, 250);
  if (on > 0.95 && t > t1) { const k = (t * 3) % 1; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6, r = 40 + 80 * k; s += `<path d="M${f1(tx + Math.cos(a) * r)} ${f1(ty + Math.sin(a) * r - 20)} l0 -26 M${f1(tx + Math.cos(a) * r - 13)} ${f1(ty + Math.sin(a) * r - 33)} l26 0" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="${f1(1 - k)}"/>`; } }
  if (t < t1 - 0.2) { const k = sm(tl - 0.6, tl - 0.2, t) * (1 - sm(t1 - 0.5, t1 - 0.2, t)), mx = 540, my = 1350;
    let m = `<path d="M${f1(tx)} ${f1(ty + 20)} L${mx + 60} ${my - 220}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12"/><circle cx="${mx}" cy="${my}" r="225" fill="#1a0f2e" stroke="#fff" stroke-width="14"/>`;
    for (let i = 0; i < 6; i++) m += `<rect x="${mx - 190}" y="${my + 10 + i * 30}" width="380" height="15" rx="7" fill="${['#ff6b8a', '#ff3d5e', '#e8243f', '#c41f45', '#a01438', '#7d0f2c'][i]}"/>`;
    const r = clamp((t - tl) / 0.8);
    m += `<path d="M${mx - 170} ${my - 170} L${f1(lerp(mx - 170, mx - 20, r))} ${f1(lerp(my - 170, my + 10, r))}" stroke="#ffe27a" stroke-width="14" stroke-linecap="round"/>`;
    if (r >= 1) { const r2 = clamp((t - tl - 0.8) / 0.6); m += `<path d="M${mx - 20} ${my + 10} L${f1(lerp(mx - 20, mx + 160, r2))} ${f1(lerp(my + 10, my - 160, r2))}" stroke="#ff1f45" stroke-width="16" stroke-linecap="round"/>`; }
    s += `<g opacity="${f1(k)}">${m}</g>` + fade(540, 1060, 'TINY LAYERS', t, tl, { size: 84, fill: '#fff', stroke: N, sw: 14 }); }
  if (t > t1) s += big(540, 1350, on > 0.5 ? 'ON!' : 'OFF', t, on > 0.5 ? t1 + 0.3 : t2 + 0.3, { size: 240, fill: on > 0.5 ? K.red : '#2a0d18', stroke: '#fff', sw: 18 });
  return s; };
// U-shaped courtship dive, laid out tall for 9:16
const UPV = u => [lerp(170, 910, u), 560 + 700 * (1 - Math.pow(2 * u - 1, 2))];
const b05b = t => { const tc = at('h24', 'climbs high'), td = at('h24', 'dives straight down'), tbot = at('h24', 'At the bottom'), tch = at('h24', 'loud chirp'), ta = at('h24', "Anna's");
  const male = (x, y, sc, rot, w, o = {}) => placeB(x, y, sc, birdSolid({ pal: 'anna', ...o }) + w, { rot });
  const prog = () => { if (t < td) return -1; const a = clamp((t - td) / (tbot - td)), b = clamp((t - tbot) / 1.3); return 0.5 * a * a + 0.5 * eo(0, 1, b); };
  const A = () => { let s = branch(380, 700, 1440, 20, { leaves: 0 }) + onBranch(540, 1440, 0.4, { throat: 0, flip: true });
    let d = ''; for (let i = 0; i <= 60; i++) { const [x, y] = UPV(i / 60); d += (i ? 'L' : 'M') + f1(x) + ' ' + f1(y); }
    const pk = sm(td - 0.6, td, t); if (pk > 0) s += `<path d="${d}" stroke="#fff" stroke-width="8" fill="none" stroke-dasharray="4 20" stroke-linecap="round" opacity="${f1(0.8 * pk)}"/>`;
    const u = prog(); let x, y, rot = 0;
    if (u < 0) { const k = sm(tc - 0.2, tc + 1.4, t); x = 200 + bobB(t, 4); y = lerp(1250, 600, k);
      s += male(x, y, 0.5, -8, wings(t, { rate: 12, amp: 55, blur: 3 }));
      if (k > 0.02 && k < 0.98) s += arrow(x + 230, y + 120, x + 230, y - 60, { w: 14 }); }
    else { const [x1, y1] = UPV(u), [x2, y2] = UPV(Math.min(1, u + 0.01)); x = x1; y = y1; rot = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
      for (let i = 4; i >= 1; i--) { const [gx, gy] = UPV(Math.max(0, u - i * 0.022)); s += placeB(gx, gy, 0.5, `<path d="${BIRD}" fill="#ffffff"/>`, { rot }).replace('<g ', `<g opacity="${f1(0.34 - i * 0.07)}" `); }
      s += `<g transform="rotate(${f1(rot)} ${f1(x)} ${f1(y)})">${speed(x - 70, y, 4, 120, 0.7)}</g>`;
      const shine = 1 - clamp(Math.abs(u - 0.5) / 0.14);
      s += male(x, y, 0.5, rot, wings(0, { still: -70, blur: 0, fill: PAL.anna.b }));
      if (shine > 0) { const [gx, gy] = bptB(x, y, 0.5, rot, 730, 240); for (let i = 0; i < 4; i++) { const a = i * 1.57 + t * 3; s += sparkle(gx + Math.cos(a) * 60, gy + Math.sin(a) * 60, 20 * shine, shine); } } }
    if (u >= 0) s += readout(540, 540, `${Math.round(97 * clamp(u / 0.5))} KM/H`, '', { size: 100 });
    const pk2 = t > ta - 0.2 && t < td - 0.1 ? pop(ta - 0.2, t) * (1 - sm(td - 0.5, td - 0.1, t)) : 0;
    s += photo('anna', 540, 930, 900, 600, pk2, { cap: "ANNA'S HUMMINGBIRD" });
    if (t > tbot - 0.2 && t < tbot + 1.2) { const hk = pop(tbot - 0.2, t); s += `<text x="540" y="${f1(1390 - 60 * sm(tbot, tbot + 1.2, t))}" font-family="Black" font-size="${f1(90 * hk)}" fill="#ff4f8a" stroke="${N}" stroke-width="8" paint-order="stroke" text-anchor="middle" opacity="${f1(1 - sm(tbot + 0.8, tbot + 1.2, t))}">♥</text>`; }
    return s; };
  const B = () => { const cx = 620, cy = 930, sc = 1.15, rot = -8, sp = sm(tbot + 0.8, tbot + 1.4, t), buzz = t > tch - 0.4 ? 1 : 0, vib = 5 * Math.sin(t * 90) * buzz;
    let s = male(cx, cy, sc, rot, wings(0, { still: -20, blur: 0 }), { tailSpread: 1 + 0.9 * sp, tailFan: [-vib, 0, 0, 0, vib] });
    const a4 = (148 + 14 * (1 + 0.9 * sp)) * Math.PI / 180, [tx, ty] = bptB(cx, cy, sc, rot, 440 + Math.cos(a4) * 220, 374 + Math.sin(a4) * 220);
    if (buzz) for (let i = 0; i < 4; i++) { const r = ((t - tch + 0.4) * 300 + i * 90) % 360; s += `<path d="M${f1(tx - r * 0.7)} ${f1(ty - r * 0.7)} A${f1(r)} ${f1(r)} 0 0 0 ${f1(tx - r * 0.7)} ${f1(ty + r * 0.7)}" stroke="#fff" stroke-width="10" fill="none" opacity="${f1(1 - r / 360)}"/>`; }
    const g = pop(at('h24', 'tail feathers') - 0.1, t); if (g > 0) { const bx = 560, by = 1390, R = 170;
      s += `<path d="M${f1(tx)} ${f1(ty)} L${bx - 80} ${by - R + 10}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12"/>`;
      let f = ''; for (let i = buzz ? 3 : 0; i >= 0; i--) f += `<g transform="translate(-230 ${f1((i ? (i % 2 ? 1 : -1) * i * 9 : 0) + vib * 2)}) rotate(-8)" opacity="${f1(i ? 0.25 : 1)}">${featherD(460, 58, '#3d6450')}</g>`;
      s += `<g transform="translate(${bx} ${by}) scale(${f1(g * 100) / 100})"><defs><clipPath id="fz5"><circle r="${R}"/></clipPath></defs><circle r="${R + 12}" fill="${N}"/><circle r="${R}" fill="#ffe9c2"/><g clip-path="url(#fz5)">${f}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="8"/></g>`;
      s += fade(860, 1300, 'TAIL', t, at('h24', 'tail feathers'), { size: 64, fill: '#fff', stroke: N, sw: 12 }); }
    if (buzz) s += fade(Math.max(130, tx - 60), ty - 120, 'BZZZ', t, tch - 0.3, { size: 60, fill: K.yellow, stroke: N, sw: 10 });
    s += big(540, 530, 'CHIRP!', t, tch, { size: 150, fill: K.yellow, stroke: N, sw: 18, rot: -6 });
    return s; };
  return t < tbot + 0.7 ? A() : xfade(t, tbot + 0.7, 0.5, A, B); };

// ───────── b06 NO LANDING ─────────
const sea = (y0, t) => { let s = `<defs><linearGradient id="sea6" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4fb6ea"/><stop offset="1" stop-color="#1f6fb0"/></linearGradient></defs><rect x="0" y="${y0}" width="${W}" height="${H - y0}" fill="url(#sea6)"/><path d="M0 ${y0} L${W} ${y0}" stroke="${N}" stroke-width="8"/>`;
  for (let r = 0; r < 6; r++) for (let i = 0; i < 6; i++) { const x = ((i * 220 + r * 110 - t * (60 + r * 20)) % 1320 + 1320) % 1320 - 120, y = y0 + 60 + r * 80;
    s += `<path d="M${f1(x)} ${y} q24 -16 48 0 q24 16 48 0" stroke="#fff" stroke-width="6" fill="none" opacity="${f1(0.75 - r * 0.08)}" stroke-linecap="round"/>`; }
  return s; };
const b06h = t => { const tg = hat('b06', 'three-gram'), tl = hat('b06', 'landing');
  let s = sea(1200, t);
  const x = 540, y = 860 + bobB(t, 10);
  s += fly(x, y, 0.95, t, { rate: 7, amp: 55 });
  for (let i = 0; i < 4; i++) s += `<path d="M${f1(130 - i * 20)} ${f1(800 + i * 55)} L${f1(250 - i * 10)} ${f1(800 + i * 55)}" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".8"/>`;
  s += tag(x - 60, y + 40, 230, 560, '3 GRAMS', t, tg, { col: K.yellow, size: 76 });
  const k = pop(tl, t);
  if (k > 0) s += `<g transform="translate(540 1450) scale(${f1(k * 100) / 100})"><ellipse rx="190" ry="44" fill="#c99a62" stroke="${N}" stroke-width="8"/><path d="M-60 -30 C-40 -110 40 -120 60 -40" stroke="#2f9a4f" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M60 -40 C90 -90 140 -90 160 -70 M60 -40 C30 -90 -20 -96 -40 -80" stroke="#3fbf6a" stroke-width="12" fill="none" stroke-linecap="round"/></g>` + cross(540, 1430, 120, t, tl + 0.2);
  return s; };
const b06a = t => { const tr = at('h25', 'ruby-throated'), td = at('h25', 'doubles its weight'), tg = at('h25', 'Then it flies across'), tk = at('h25', 'eight hundred'), tn = at('h25', 'nonstop');
  const A = () => { const fat = sm(td - 1.2, td + 0.4, t), by = 1180;
    let s = '';
    const sc = 0.85, gy = by - 26 * 0.5 - 4, pp = 1.7 * fat, tipB = [600 + (992 - 600) * (1 + 0.12 * pp), 452 + (199 - 452) * (1 + 0.22 * pp)];
    const [tx, ty] = toB(330, gy - (452 - 300) * sc, sc, ...tipB), ra = -84, [ox, oy] = fpt(0, 0, 0.9, ra, 0, 72), fa = [tx - ox, ty - oy];
    { const [ex, ey] = fpt(900, 860, 0.9, -40, 0, 200); s += stemTo(ex, ey, 880, 2000); }
    { const [ex, ey] = fpt(fa[0], fa[1], 0.9, ra, 0, 200); s += stemTo(ex, ey, 880, 2000); }
    s += flowerT(900, 860, 0.9, { rot: -40, stem: 0 });
    s += branch(-60, 780, by, 26) + onBranch(330, by, sc, { puff: pp, th: 26 });
    s += flowerT(fa[0], fa[1], 0.9, { rot: ra, stem: 0 });
    const rk = sm(td - 1.2, td - 0.8, t);
    if (rk > 0) s += `<g opacity="${f1(rk)}">${readout(540, 560, `${(3 + 3 * fat * 0.95).toFixed(1)} G`, '', { size: 120 })}</g>`;
    s += big(540, 690, 'ALMOST x2', t, td, { size: 90, fill: K.yellow, stroke: N, sw: 14 });
    const pk = t > tr - 0.2 && t < td - 0.6 ? pop(tr - 0.2, t) * (1 - sm(td - 1.0, td - 0.6, t)) : 0;
    s += photo('ruby', 540, 960, 860, 640, pk, { cap: 'RUBY-THROATED' });
    return s; };
  const B = () => { const v = { lon0: -101.5, lon1: -77.7, lat0: 15, lat1: 33, x: 60, y: 460, w: 960, h: 800 }, P = proj(v);
    let s = mapCard(v, 'mc6');
    for (const [lo, la] of [[-93, 27], [-87, 26.5], [-95, 23], [-91, 23.5], [-86, 24], [-92, 20.5]]) { const [x, y] = P(lo, la); s += `<path d="M${f1(x - 30)} ${f1(y)} q15 -12 30 0 q15 12 30 0" stroke="#fff" stroke-width="5" fill="none" opacity=".7" stroke-linecap="round"/>`; }
    s += label(...P(-97, 31.2), 'USA', 56) + label(...P(-99.5, 19.2), 'MEXICO', 52) + label(...P(-94.4, 25.6), 'GULF OF', 40, '#1f5f9c') + label(...P(-94.4, 24.6), 'MEXICO', 40, '#1f5f9c');
    const k = sm(tg + 0.4, tn + 1.0, t), [svg, hx, hy] = route(P, [[-90.3, 29.6], [-89.9, 25.5], [-89.0, 21.4]], k);
    s += svg + `<g transform="translate(${f1(hx)} ${f1(hy)}) rotate(70)">${placeB(0, 0, 0.16, birdSolid() + wings(t, { rate: 7, amp: 50, blur: 1 }))}</g>`;
    if (t > tk - 0.2) s += readout(540, 1390, count(800, t, tk - 0.2, 1.2) + ' KM', '', { size: 130 });
    s += big(540, 1530, 'NONSTOP!', t, tn, { size: 100, fill: K.yellow, stroke: N, sw: 14 });
    return s; };
  return t < tg - 0.2 ? A() : xfade(t, tg - 0.2, 0.6, A, B); };
const b06b = t => { const tm = at('h26', 'More than six thousand'), tl = at('h26', 'longest trips');
  const v = { lon0: -164, lon1: -82.3, lat0: 12, lat1: 66, x: 60, y: 450, w: 960, h: 900 }, P = proj(v);
  let s = mapCard(v, 'mc6b', true);
  s += label(...P(-150, 63), 'ALASKA', 52) + label(...P(-100, 26.5), 'MEXICO', 52);
  const k = sm(0.6, tm + 0.8, t), [svg, hx, hy, ang] = route(P, [[-150, 61], [-140, 59.5], [-134, 57], [-130, 53.5], [-125, 49], [-124, 44], [-122, 38], [-117, 33], [-112, 28.5], [-106, 23.5], [-102, 19.5]], k);
  s += svg + `<g transform="translate(${f1(hx)} ${f1(hy)}) rotate(${f1(ang)})">${placeB(0, 0, 0.2, birdSolid({ pal: 'rufous' }) + wings(t, { rate: 7, amp: 50, blur: 1 }))}</g>`;
  s += photo('rufous', 280, 1080, 300, 320, pop(0.3, t), { cap: 'RUFOUS', rot: -2 });
  if (t > tm - 0.2) s += readout(540, 1480, count(6000, t, tm - 0.2, 1.4) + '+ KM', '', { size: 120 });
  s += big(760, 700, 'EPIC TRIP!', t, tl, { size: 80, fill: K.yellow, stroke: N, sw: 14 });
  return s; };

export const VS2 = { b04: [b04h, b04a, b04b], b05: [b05h, b05a, b05b], b06: [b06h, b06a, b06b] };
