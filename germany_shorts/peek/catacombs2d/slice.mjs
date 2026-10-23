// PEEK. Paris catacombs, 2.5D "cake slice" cross-section (clean, minimal, Apple-like)
export const W = 1920, H = 1080;
import { readFileSync } from 'fs';
const b64 = p => readFileSync(p).toString('base64');
export const FONTS = `@font-face{font-family:ID;src:url(data:font/otf;base64,${b64('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf')})}
@font-face{font-family:IDM;src:url(data:font/otf;base64,${b64('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf')})}`;

export const C = {
  bg0: '#fbfbfd', bg1: '#e9eaef', ink: '#1d1d1f', sub: '#6e6e73', line: '#86868b',
  grass: '#9cc58a', grassTop: '#b9d9a8', soil: '#8c6a50', sand: '#d9c3a0', lime: '#ece0c8', limeDark: '#d8c8a8',
  marl: '#b7b9a4', clay: '#7f8796', cave: '#2a2420', caveLit: '#4a3d33', bone: '#efe6d2', boneShade: '#cbbd9f',
  water: '#7fb4e6', tower: '#3a3a3c', accent: '#ff9f0a',
};

// slice geometry: front face from x0..x1, ground at gy, bottom at by; top face skewed back by (dx, dy)
export const G = { x0: 200, x1: 1660, gy: 470, by: 930, dx: 170, dy: -120 };
// layer boundaries (y on the front face)
export const LAY = [
  ['grass', 470, 480], ['soil', 480, 515], ['sand', 515, 565], ['lime', 565, 820], ['marl', 820, 878], ['clay', 878, 930],
];

const f = n => n.toFixed(1);
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
export const lerp = (a, b, k) => a + (b - a) * k;

function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

export function defs() {
  return `<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.bg0}"/><stop offset="1" stop-color="${C.bg1}"/></linearGradient>
  <linearGradient id="topg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9cf98"/><stop offset="1" stop-color="#c3e0b4"/></linearGradient>
  <linearGradient id="sideg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity=".30"/></linearGradient>
  <linearGradient id="faceShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="#000" stop-opacity=".10"/></linearGradient>
  <radialGradient id="lamp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd38a" stop-opacity=".75"/><stop offset="1" stop-color="#ffd38a" stop-opacity="0"/></radialGradient>
  <linearGradient id="caveg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b322b"/><stop offset="1" stop-color="#231d19"/></linearGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="18"/><feOffset dy="22"/><feComponentTransfer><feFuncA type="linear" slope=".22"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="tiny" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="3"/><feOffset dy="3"/><feComponentTransfer><feFuncA type="linear" slope=".25"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>`;
}

// ---- the earth block -------------------------------------------------------
export function block() {
  const { x0, x1, gy, by, dx, dy } = G;
  let s = `<g filter="url(#soft)">`;
  // right side face
  s += `<path d="M${x1} ${gy} L${x1 + dx} ${gy + dy} L${x1 + dx} ${by + dy} L${x1} ${by} Z" fill="${C.lime}"/>`;
  for (const [k, a, b] of LAY) s += `<path d="M${x1} ${a} L${x1 + dx} ${a + dy} L${x1 + dx} ${b + dy} L${x1} ${b} Z" fill="${C[k]}"/>`;
  s += `<path d="M${x1} ${gy} L${x1 + dx} ${gy + dy} L${x1 + dx} ${by + dy} L${x1} ${by} Z" fill="url(#sideg)"/>`;
  // top face (grass)
  s += `<path d="M${x0} ${gy} L${x0 + dx} ${gy + dy} L${x1 + dx} ${gy + dy} L${x1} ${gy} Z" fill="url(#topg)"/>`;
  // front face layers
  for (const [k, a, b] of LAY) s += `<rect x="${x0}" y="${a}" width="${x1 - x0}" height="${b - a}" fill="${C[k]}"/>`;
  s += `</g>`;
  // limestone bedding lines (fine detail)
  const r = rng(7);
  for (let y = 580; y < 816; y += 16 + r() * 10) {
    let d = `M${x0} ${f(y)}`;
    for (let x = x0; x <= x1; x += 60) d += ` L${x} ${f(y + Math.sin(x * 0.004 + y) * 2.2)}`;
    s += `<path d="${d}" stroke="${C.limeDark}" stroke-width="1.4" fill="none" opacity=".75"/>`;
  }
  // soil pebbles
  for (let i = 0; i < 70; i++) { const x = x0 + 10 + r() * (x1 - x0 - 20), y = 520 + r() * 42; s += `<ellipse cx="${f(x)}" cy="${f(y)}" rx="${f(2 + r() * 3)}" ry="${f(1.5 + r() * 2)}" fill="#c4ab84"/>`; }
  for (let i = 0; i < 50; i++) { const x = x0 + 10 + r() * (x1 - x0 - 20), y = 484 + r() * 26; s += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(1 + r() * 1.6)}" fill="#76563f"/>`; }
  s += `<rect x="${x0}" y="${gy}" width="${x1 - x0}" height="${by - gy}" fill="url(#faceShade)"/>`;
  return s;
}

// ---- city on top -----------------------------------------------------------
function building(x, y, w, h, depth = 26) {
  // haussmann block: front, side, mansard roof
  const dx = depth * G.dx / 120, dy = depth * G.dy / 120, rf = Math.min(16, h * 0.28);
  let s = `<g filter="url(#tiny)">`;
  s += `<path d="M${f(x + w)} ${f(y)} l${f(dx)} ${f(dy)} v${f(-h)} l${f(-dx)} ${f(-dy)} Z" fill="#d6d3cc"/>`;
  s += `<rect x="${f(x)}" y="${f(y - h)}" width="${f(w)}" height="${f(h)}" fill="#f2efe8"/>`;
  s += `<path d="M${f(x)} ${f(y - h)} l${f(dx)} ${f(dy)} h${f(w)} l${f(-dx)} ${f(-dy)} Z" fill="#9aa3ad"/>`;
  s += `<rect x="${f(x)}" y="${f(y - h - 2)}" width="${f(w)}" height="${f(rf * 0.25 + 2)}" fill="#8b949e"/>`;
  // windows
  for (let wy = y - h + rf * 0.6; wy < y - 12; wy += 12) for (let wx = x + 5; wx < x + w - 6; wx += 9) s += `<rect x="${f(wx)}" y="${f(wy)}" width="4" height="6.5" rx="1" fill="#c9c4b8"/>`;
  s += `</g>`;
  return s;
}

export function tower(cx, base, h, k = 1) {
  // Eiffel tower: exponential profile silhouette, arch cut out, fine lattice. k = build progress (bottom-up)
  const w = y => 0.25 * Math.exp(-3.2 * y);
  const P = (x, y) => `${f(cx + x * h)} ${f(base - y * h)}`;
  let out = 'M' + P(-w(0), 0);
  for (let y = 0.02; y <= 0.93; y += 0.02) out += ' L' + P(-w(y), y);
  out += ' L' + P(-0.006, 0.97) + ' L' + P(0.006, 0.97);
  for (let y = 0.93; y >= 0; y -= 0.02) out += ' L' + P(w(y), y);
  out += ' L' + P(w(0), 0) + ' Z';
  // arch between the legs
  let arch = 'M' + P(0.155, 0);
  for (let a = 0; a <= Math.PI; a += Math.PI / 24) arch += ' L' + P(0.155 * Math.cos(a), 0.125 * Math.sin(a));
  arch += ' Z';
  // window between first and second platform
  let win = 'M' + P(0.055, 0.2) + ' L' + P(0.0, 0.33) + ' L' + P(-0.055, 0.2) + ' Z';
  const id = 'tw' + Math.round(cx);
  let s = `<defs><linearGradient id="${id}g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5a5650"/><stop offset=".5" stop-color="#3d3a36"/><stop offset="1" stop-color="#2a2826"/></linearGradient>
  <clipPath id="${id}c"><path d="${out} ${arch} ${win}" clip-rule="evenodd"/></clipPath>
  <clipPath id="${id}k"><rect x="${f(cx - h)}" y="${f(base - h * 1.1 * k - 2)}" width="${f(2 * h)}" height="${f(h * 1.1 * k + 4)}"/></clipPath></defs>`;
  s += `<g clip-path="url(#${id}k)"><path d="${out} ${arch} ${win}" fill="url(#${id}g)" fill-rule="evenodd"/>`;
  // lattice: diagonal hatching clipped to the silhouette
  let d = '';
  for (let i = -60; i < 60; i++) { const x = cx + i * 9; d += `M${f(x)} ${f(base)} L${f(x + h)} ${f(base - h)} M${f(x)} ${f(base)} L${f(x - h)} ${f(base - h)} `; }
  s += `<g clip-path="url(#${id}c)"><path d="${d}" stroke="#a8a29a" stroke-width="0.9" opacity=".45"/></g>`;
  // platforms
  for (const [y, ww] of [[0.18, 0.165], [0.37, 0.085], [0.88, 0.022]]) s += `<rect x="${f(cx - ww * h)}" y="${f(base - y * h - 3)}" width="${f(2 * ww * h)}" height="6" rx="2" fill="#24221f"/>`;
  s += `<rect x="${f(cx - 1.2)}" y="${f(base - h * 1.05)}" width="2.4" height="${f(h * 0.09)}" fill="#24221f"/>`;
  return s + `</g>`;
}

export function city(t = 0) {
  const { x0, x1, gy, dx, dy } = G;
  let s = '';
  const at = (x, k) => [x + dx * k, gy + dy * k];
  const sy0 = 0.6, sy1 = 0.74;
  s += `<path d="M${f(x0 + dx * sy0)} ${f(gy + dy * sy0)} L${f(x1 + dx * sy0)} ${f(gy + dy * sy0)} L${f(x1 + dx * sy1)} ${f(gy + dy * sy1)} L${f(x0 + dx * sy1)} ${f(gy + dy * sy1)} Z" fill="${C.water}"/>`;
  const r = rng(3);
  for (let x = x0 + 40; x < x1 - 110; x += 84 + r() * 24) { const [bx, by] = at(x, 0.9); s += building(bx, by, 50 + r() * 14, 26 + r() * 14, 12); }
  for (let x = x0 + 40; x < x1 - 30; x += 80 + r() * 22) { if (x > 700 && x < 1180) continue; const [bx, by] = at(x, 0.45); s += building(bx, by, 50 + r() * 12, 30 + r() * 14, 14); }
  for (let x = x0 + 20; x < x1 - 60; x += 82 + r() * 24) { if (x > 640 && x < 1220) continue; if (x > 1340 && x < 1460) continue; const [bx, by] = at(x, 0.12); s += building(bx, by, 52 + r() * 12, 34 + r() * 14, 16); }
  // Champ de Mars lawn and the tower
  const [tx, ty] = at(870, 0.32);
  s += `<ellipse cx="${f(tx)}" cy="${f(ty + 2)}" rx="150" ry="16" fill="#5f8a52" opacity=".25"/>`;
  s += tower(tx, ty, 380);
  return s;
}

// ---- catacombs inside the limestone ---------------------------------------
function skull(cx, cy, sz, tilt = 0) {
  return `<g transform="translate(${f(cx)} ${f(cy)}) rotate(${f(tilt)})"><path d="M${f(-sz * 0.5)} ${f(sz * 0.05)} C${f(-sz * 0.5)} ${f(-sz * 0.62)} ${f(sz * 0.5)} ${f(-sz * 0.62)} ${f(sz * 0.5)} ${f(sz * 0.05)} C${f(sz * 0.5)} ${f(sz * 0.3)} ${f(sz * 0.3)} ${f(sz * 0.32)} ${f(sz * 0.28)} ${f(sz * 0.5)} L${f(-sz * 0.28)} ${f(sz * 0.5)} C${f(-sz * 0.3)} ${f(sz * 0.32)} ${f(-sz * 0.5)} ${f(sz * 0.3)} ${f(-sz * 0.5)} ${f(sz * 0.05)} Z" fill="${C.bone}"/>`
    + `<ellipse cx="${f(-sz * 0.2)}" cy="${f(sz * 0.06)}" rx="${f(sz * 0.14)}" ry="${f(sz * 0.12)}" fill="#3a2f27"/><ellipse cx="${f(sz * 0.2)}" cy="${f(sz * 0.06)}" rx="${f(sz * 0.14)}" ry="${f(sz * 0.12)}" fill="#3a2f27"/>`
    + `<path d="M0 ${f(sz * 0.2)} l${f(-sz * 0.06)} ${f(sz * 0.12)} h${f(sz * 0.12)} Z" fill="#3a2f27"/></g>`;
}
function skullRow(x, y, w, sz, seed) {
  const r = rng(seed); let s = '';
  for (let cx = x + sz * 0.6; cx < x + w - sz * 0.5; cx += sz * 1.08) s += skull(cx, y + (r() - 0.5) * 1.5, sz, (r() - 0.5) * 8);
  return s;
}
function boneRow(x, y, w, hgt, seed) {
  // stacked long bones seen end-on: rows of knobs
  const r = rng(seed);
  let s = `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(hgt)}" fill="#8f7f66"/>`;
  const rows = Math.max(2, Math.round(hgt / 7));
  for (let k = 0; k < rows; k++) for (let cx = x + 4 + (k % 2) * 3.5; cx < x + w - 3; cx += 7) s += `<circle cx="${f(cx + (r() - .5))}" cy="${f(y + 3.5 + k * (hgt - 7) / (rows - 1))}" r="${f(2.6 + r() * 0.6)}" fill="${r() < .15 ? C.boneShade : C.bone}"/>`;
  return s;
}
function vault(x, y, w, h) {
  const r = Math.min(h * 0.5, 26);
  return `M${x} ${y + h} V${y + r} Q${x} ${y} ${x + r} ${y} H${x + w - r} Q${x + w} ${y} ${x + w} ${y + r} V${y + h} Z`;
}
export function ossuary(x, y, w, h) {
  const id = 'oss' + x;
  let s = `<clipPath id="${id}"><path d="${vault(x, y, w, h)}"/></clipPath><path d="${vault(x, y, w, h)}" fill="url(#caveg)"/><g clip-path="url(#${id})">`;
  // back wall: bone bands with two skull bands (the famous pattern)
  const top = y + 30, bot = y + h - 14;
  s += boneRow(x, top, w, 22, 1) + skullRow(x, top + 34, w, 22, 2) + boneRow(x, top + 48, w, 26, 3) + skullRow(x, top + 86, w, 22, 4) + boneRow(x, top + 100, w, bot - top - 100, 5);
  s += `<rect x="${x}" y="${bot}" width="${w}" height="14" fill="#5a4b3e"/>`;
  // warm lamp pools from the ceiling
  for (let i = 0; i < 3; i++) { const lx = x + w * (0.2 + i * 0.3); s += `<ellipse cx="${f(lx)}" cy="${f(y + 6)}" rx="${f(w * 0.2)}" ry="${f(h * 0.9)}" fill="url(#lamp)" opacity=".7"/><circle cx="${f(lx)}" cy="${y + 8}" r="3" fill="#ffe2a8"/>`; }
  s += `<path d="${vault(x, y, w, h)}" fill="none" stroke="#000" stroke-opacity=".15" stroke-width="3"/>`;
  return s + `</g>`;
}
export function tunnel(x, y, w, h, lamp = true) {
  const id = `tn${x}_${y}`;
  let s = `<clipPath id="${id}"><path d="${vault(x, y, w, h)}"/></clipPath><path d="${vault(x, y, w, h)}" fill="url(#caveg)"/><g clip-path="url(#${id})"><rect x="${x}" y="${y + h - 6}" width="${w}" height="6" fill="#5a4b3e"/>`;
  if (lamp && w > 120) s += `<ellipse cx="${f(x + w / 2)}" cy="${y + 4}" rx="${f(Math.min(w * 0.3, 90))}" ry="${f(h)}" fill="url(#lamp)" opacity=".6"/><circle cx="${f(x + w / 2)}" cy="${y + 7}" r="2.5" fill="#ffe2a8"/>`;
  return s + `</g>`;
}
export function catacombs() {
  let s = '';
  s += tunnel(240, 610, 300, 46) + tunnel(510, 610, 46, 128, false) + tunnel(510, 690, 250, 48);
  s += ossuary(760, 618, 520, 150);
  s += tunnel(1280, 700, 200, 46) + tunnel(1450, 608, 46, 138, false) + tunnel(1450, 608, 160, 44);
  s += tunnel(300, 718, 170, 42);
  // spiral stair: 131 steps down from the entrance pavilion
  const sx = 1386, sy = 482, ey = 742;
  s += `<rect x="${sx}" y="${sy}" width="40" height="${ey - sy}" fill="url(#caveg)"/>`;
  for (let y = sy + 6, k = 0; y < ey - 4; y += 8, k++) s += `<rect x="${sx + (k % 2 ? 17 : 5)}" y="${y}" width="18" height="2.6" rx="1" fill="#8a7663"/>`;
  s += `<g filter="url(#tiny)"><rect x="${sx - 26}" y="${sy - 50}" width="92" height="50" fill="#f2efe8"/><path d="M${sx - 30} ${sy - 50} h100 l-12 -14 h-76 Z" fill="#9aa3ad"/><rect x="${sx + 8}" y="${sy - 32}" width="24" height="32" rx="12" fill="#3b322b"/></g>`;
  return s;
}

// ---- labels ----------------------------------------------------------------
export function label(x, y, tx, ty, title, sub, k = 1, anchor = 'start') {
  if (k <= 0) return '';
  const o = sm(0, 1, k);
  const midx = tx;
  return `<g opacity="${f(o)}"><circle cx="${x}" cy="${y}" r="5" fill="${C.ink}"/><circle cx="${x}" cy="${y}" r="11" fill="none" stroke="${C.ink}" stroke-width="1.5" opacity=".35"/>`
    + `<path d="M${x} ${y} L${midx} ${ty}" stroke="${C.ink}" stroke-width="1.6" fill="none"/>`
    + `<text x="${tx + (anchor === 'end' ? -10 : 10)}" y="${ty - 6}" text-anchor="${anchor}" font-family="ID" font-size="34" fill="${C.ink}" letter-spacing="-0.5">${title}</text>`
    + (sub ? `<text x="${tx + (anchor === 'end' ? -10 : 10)}" y="${ty + 26}" text-anchor="${anchor}" font-family="IDM" font-size="22" fill="${C.sub}">${sub}</text>` : '') + `</g>`;
}
export function depthRuler(k = 1) {
  const x = G.x0 - 46; let s = `<g opacity="${f(k)}"><path d="M${x} ${G.gy} V${G.by}" stroke="${C.line}" stroke-width="1.5"/>`;
  const marks = [[G.gy, '0 m'], [565, '10 m'], [690, '20 m'], [820, '30 m']];
  for (const [y, t] of marks) s += `<path d="M${x - 8} ${y} H${x + 8}" stroke="${C.line}" stroke-width="1.5"/><text x="${x - 16}" y="${y + 7}" text-anchor="end" font-family="IDM" font-size="20" fill="${C.sub}">${t}</text>`;
  return s + `</g>`;
}

export function frame(t) {
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${defs()}<rect width="${W}" height="${H}" fill="url(#bg)"/>`;
  s += block() + catacombs() + city(t) + depthRuler();
  s += label(925, 210, 1130, 150, 'Eiffel Tower', '330 m');
  s += label(1020, 700, 1180, 1010, 'Ossuary', '6,000,000 people');
  return s + `</svg>`;
}
