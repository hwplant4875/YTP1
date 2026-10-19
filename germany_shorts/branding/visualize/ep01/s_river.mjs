import { chromium } from 'playwright';
import fs from 'fs';
const W = 1920, H = 1080, HZ = 500, CX = 960, F = 980, CH = 1.7;
const ff0 = (n, f) => `@font-face{font-family:${n};src:url(data:font/woff2;base64,${fs.readFileSync('/tmp/claude-0/vz/flat/fonts/' + f).toString('base64')})}`;
const fonts = ff0('Mono', 'mono.woff2') + ff0('SerifI', 'serif_i.woff2') + ff0('Inter', 'inter.woff2');
// perspective: lateral X (m), height Y (m), depth Z (m)
let CZ = 0, BOB = 0;
const P = (X, Y, Z) => { const z = Math.max(0.35, Z - CZ); return [CX + F * X / z, HZ - F * (Y - CH - BOB) / z]; };
const pt = (a) => a.map(v => v.toFixed(1)).join(' ');
const poly = (pts, fill, extra = '') => `<path d="M${pts.map(pt).join(' L')}Z" fill="${fill}" ${extra}/>`;
const fog = (Z, a = 0, b = 1) => Math.min(1, Math.max(0, (Z - CZ - 6) / 70)) * (b - a) + a; // 0 near → 1 far
const mix = (c1, c2, t) => { const h = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16)); const A = h(c1), B = h(c2);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
const HAZE = '#b98a9a';
let s = '';
const defs = `<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#121633"/><stop offset=".45" stop-color="#2f2a5c"/><stop offset=".78" stop-color="#9a5f86"/><stop offset="1" stop-color="#f2b48d"/></linearGradient>
<radialGradient id="sunglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffd9a8" stop-opacity=".95"/><stop offset=".25" stop-color="#ffb889" stop-opacity=".45"/><stop offset="1" stop-color="#f29a8a" stop-opacity="0"/></radialGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8d6585"/><stop offset=".25" stop-color="#4b3b6e"/><stop offset="1" stop-color="#231d42"/></linearGradient>
<linearGradient id="path" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a6f87"/><stop offset=".3" stop-color="#4d4468"/><stop offset="1" stop-color="#2f2a45"/></linearGradient>
<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b5a72"/><stop offset=".25" stop-color="#2f3a4a"/><stop offset="1" stop-color="#1b2433"/></linearGradient>
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9a585"/><stop offset="1" stop-color="#a8705a"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05040d" stop-opacity=".55"/></radialGradient>
<radialGradient id="lampglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe2b0" stop-opacity=".9"/><stop offset="1" stop-color="#ffc98a" stop-opacity="0"/></radialGradient>
<filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
</defs>`;
s = '';
// sky + sun
const SUN = [1330, HZ + 8];
s += `<rect width="${W}" height="${HZ + 2}" fill="url(#sky)"/>`;
s += `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="420" fill="url(#sunglow)"/>`;
s += `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="46" fill="#fff1d6"/>`;
// thin clouds (lines, motion-graphic style)
[[200, 170, 380], [520, 250, 240], [1450, 190, 300], [1650, 300, 180], [880, 120, 200]].forEach(([x, y, w], i) => {
  s += `<rect x="${x}" y="${y}" width="${w}" height="${3 + (i % 2) * 2}" rx="3" fill="#f6c6b0" opacity="${0.12 + 0.05 * (i % 3)}"/>`;
  s += `<rect x="${x + w * 0.25}" y="${y + 12}" width="${w * 0.55}" height="3" rx="2" fill="#f6c6b0" opacity=".1"/>`;
});
// far shore skyline across the river (right) and far tree line (left)
let bx = 1010, seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
while (bx < W) { const bw = 18 + rnd() * 46, bh = 14 + rnd() * 70 * (bx > 1500 && bx < 1750 ? 1.9 : 1);
  s += `<rect x="${bx.toFixed(1)}" y="${(HZ - bh).toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" fill="${mix('#3a2f5a', HAZE, 0.35)}"/>`;
  for (let k = 0; k < 3; k++) if (rnd() < 0.35) s += `<rect x="${(bx + 4 + rnd() * (bw - 8)).toFixed(1)}" y="${(HZ - bh + 6 + rnd() * (bh - 12)).toFixed(1)}" width="3" height="3" fill="#ffd9a0" opacity=".8"/>`;
  bx += bw + 2 + rnd() * 6; }
for (let x = -20; x < 900; x += 26) { const r = 14 + rnd() * 16; s += `<circle cx="${x}" cy="${HZ - r * 0.5}" r="${r}" fill="${mix('#2c2a4a', HAZE, 0.3)}"/>`; }
const SKY = s;

// world-space random details, generated once
const grassStrokes = [], ripples = [];
for (let i = 0; i < 160; i++) grassStrokes.push([-2.2 - rnd() * 25, 1 + rnd() * 90]);
for (let i = 0; i < 80; i++) ripples.push([3.5 + rnd() * 30, 2 + rnd() * 90]);
const refl = []; for (let i = 0; i < 26; i++) refl.push([rnd(), rnd(), rnd()]);
const objs = [];
for (let Z = 160; Z > 11; Z -= 9 + (Z % 5)) objs.push({ t: 'tree', X: -4.2 - (Z % 7) * 0.35, Z, r: 1.6 + (Z % 3) * 0.3 });
for (let Z = 150; Z > 14; Z -= 13 + (Z % 4)) objs.push({ t: 'tree', X: -9.5 - (Z % 5) * 0.8, Z, r: 2.0 + (Z % 4) * 0.3 });
for (let Z = 166; Z > 9; Z -= 16) objs.push({ t: 'lamp', X: -2.1, Z });
objs.sort((a, b) => b.Z - a.Z);
function world(t) {
  let s = '';
  const ZN = CZ + 0.9, ZF = CZ + 400;
  s += poly([P(-60, 0, ZN), P(-60, 0, ZF), P(-1.6, 0, ZF), P(-1.6, 0, ZN)], 'url(#grass)');
  s += poly([P(-1.6, 0, ZN), P(-1.6, 0, ZF), P(1.6, 0, ZF), P(1.6, 0, ZN)], 'url(#path)');
  s += poly([P(1.6, 0, ZN), P(1.6, 0, ZF), P(2.6, 0, ZF), P(2.6, 0, ZN)], 'url(#grass)');
  s += poly([P(2.6, 0, ZN), P(2.6, 0, ZF), P(400, 0, ZF), P(400, 0, ZN)], 'url(#water)');
  const SUN = [1330, HZ + 8 + F * BOB / 400];
  refl.forEach(([a, b, c], i) => { const y = HZ + 6 + i * i * 0.9 + i * 3; if (y > H) return;
    const w = (70 + i * 9 + a * 40) * (0.85 + 0.15 * Math.sin(t * 2.3 + i * 1.7));
    const x = SUN[0] - w / 2 + (b - 0.5) * (10 + i * 6) + Math.sin(t * 1.6 + i) * (2 + i * 0.6);
    const zr = (F * CH) / (y - HZ); if (x + w < P(2.6, 0, CZ + zr)[0] + 30) return;
    s += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${(2 + i * 0.25).toFixed(1)}" rx="2" fill="#ffd2a6" opacity="${(0.75 - i * 0.025).toFixed(2)}"/>`; });
  const wrap = (Z) => { let z = Z; while (z < CZ + 1) z += 90; return z; };
  grassStrokes.forEach(([X, Z0]) => { const Z = wrap(Z0); const [x, y] = P(X, 0, Z); const w = 50 * 6 / (Z - CZ) + 6;
    s += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${Math.max(1, 8 / (Z - CZ)).toFixed(1)}" fill="#8fa0b8" opacity=".10"/>`; });
  ripples.forEach(([X, Z0]) => { const Z = wrap(Z0); const [x, y] = P(X, 0, Z); const w = 60 * 6 / (Z - CZ) + 10;
    s += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="1.5" fill="#b9a2d6" opacity=".22"/>`; });
  s += `<path d="M${pt(P(-1.55, 0, ZN))} L${pt(P(-1.55, 0, ZF))}" stroke="#cdb8c8" stroke-width="2" opacity=".35"/>`;
  s += `<path d="M${pt(P(1.55, 0, ZN))} L${pt(P(1.55, 0, ZF))}" stroke="#cdb8c8" stroke-width="2" opacity=".35"/>`;
  for (let Z = Math.floor(CZ / 3) * 3; Z < CZ + 120; Z += 3) { const a = Math.max(Z, ZN), b = Z + 1.4; if (b <= ZN) continue;
    s += poly([P(-0.05, 0, a), P(-0.05, 0, b), P(0.05, 0, b), P(0.05, 0, a)], '#f3dcc6', `opacity="${(0.75 - fog(Z) * 0.55).toFixed(2)}"`); }
  for (let Z = Math.ceil((CZ + 120) / 2.5) * 2.5; Z >= CZ + 0.8; Z -= 2.5) { const a = P(2.5, 0, Z), b = P(2.5, 1.05, Z);
    s += `<path d="M${pt(a)} L${pt(b)}" stroke="${mix('#1a1530', HAZE, fog(Z) * 0.8)}" stroke-width="${Math.max(1, 70 / (Z - CZ)).toFixed(1)}"/>`; }
  const rail = (Y) => `<path d="M${pt(P(2.5, Y, CZ + 0.8))} L${pt(P(2.5, Y, CZ + 400))}" stroke="#1a1530" stroke-width="3" fill="none"/>`;
  s += rail(1.05) + rail(0.55);
  for (const o of objs) {
    if (o.Z - CZ < 1.5) continue;
    const t2 = fog(o.Z), zr = o.Z - CZ;
    if (o.t === 'tree') {
      s += poly([P(o.X - 0.6, 0, o.Z), P(o.X + 0.6, 0, o.Z), P(o.X - 3.5, 0, Math.max(o.Z - 7, ZN)), P(o.X - 6.0, 0, Math.max(o.Z - 7, ZN))], '#121826', `opacity="${(0.45 * (1 - t2)).toFixed(2)}"`);
      const [tx, ty] = P(o.X, 0, o.Z), [, tt] = P(o.X, 2.9 * o.r * 0.75 - 0.2 * o.r, o.Z);
      const col = mix('#1b2030', HAZE, t2 * 0.85), rim = mix('#e9a88f', HAZE, t2 * 0.6);
      s += `<path d="M${tx.toFixed(1)} ${ty.toFixed(1)} L${tx.toFixed(1)} ${tt.toFixed(1)}" stroke="${col}" stroke-width="${Math.max(1.2, 180 / zr).toFixed(1)}"/>`;
      const blobs = [[0, 3.4, 1], [-0.9, 2.9, 0.75], [0.85, 3.0, 0.7], [0.1, 4.2, 0.7]];
      const id = 'c' + Math.round(o.Z * 10); let g = '';
      blobs.forEach(([dx, y, k]) => { const [cx, cy] = P(o.X + dx * o.r * 0.6, y * o.r * 0.75, o.Z); g += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${(F * o.r * k * 0.62 / zr).toFixed(1)}"/>`; });
      s += `<clipPath id="${id}">${g}</clipPath><g fill="${col}">${g}</g>`;
      const off = (F * o.r * 0.22 / zr).toFixed(1);
      s += `<g clip-path="url(#${id})"><g fill="${rim}" opacity="${(0.55 * (1 - t2 * 0.6)).toFixed(2)}" transform="translate(${off} ${-off * 0.4})">${g}</g><g fill="${col}" transform="translate(${-off * 0.35} ${off * 0.35})">${g}</g></g>`;
    } else {
      s += poly([P(o.X - 0.06, 0, o.Z), P(o.X + 0.06, 0, o.Z), P(o.X - 2.4, 0, Math.max(o.Z - 6, ZN)), P(o.X - 2.6, 0, Math.max(o.Z - 6, ZN))], '#121826', `opacity="${(0.4 * (1 - t2)).toFixed(2)}"`);
      const [x0, y0] = P(o.X, 0, o.Z), [, y1] = P(o.X, 3.6, o.Z), [hx, hy] = P(o.X + 0.45, 3.6, o.Z);
      const col = mix('#151827', HAZE, t2 * 0.85), wpx = Math.max(1, 110 / zr);
      s += `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} L${x0.toFixed(1)} ${y1.toFixed(1)} Q${x0.toFixed(1)} ${(y1 - 12 * 6 / zr).toFixed(1)} ${hx.toFixed(1)} ${hy.toFixed(1)}" stroke="${col}" stroke-width="${wpx.toFixed(1)}" fill="none"/>`;
      const lr = F * 0.17 / zr;
      s += `<circle cx="${hx.toFixed(1)}" cy="${(hy + lr * 0.8).toFixed(1)}" r="${(lr * 5).toFixed(1)}" fill="url(#lampglow)" opacity=".45"/>`;
      s += `<rect x="${(hx - lr).toFixed(1)}" y="${hy.toFixed(1)}" width="${(2 * lr).toFixed(1)}" height="${(lr * 0.9).toFixed(1)}" rx="${(lr * 0.3).toFixed(1)}" fill="#ffe6bf"/>`;
    }
  }
  return s;
}
function hud(t, o) {
  const km = o.km != null ? o.km : o.km0 + t * o.speed / 1000 * (o.kmMul || 1), sec = o.sec != null ? o.sec : o.sec0 + t;
  const mm = Math.floor(sec / 60), ss = (sec % 60).toFixed(2).padStart(5, '0');
  const kmc = Math.min(km, 5), dx = kmc * 112;
  return `<g font-family="Mono" fill="#f4ecff">
 <text x="80" y="92" font-size="20" opacity=".75">DAY ${String(o.day).padStart(3, '0')} / 365</text>
 <text x="80" y="124" font-size="20" opacity=".45">${o.clock} · Riverside</text>
 <text x="80" y="160" font-size="20" fill="#ffd2a6">${mm}:${ss}</text>
 <g transform="translate(1260 86)">
  <path d="M0 0 L560 0" stroke="#f4ecff" stroke-width="1.5" opacity=".45"/>
  ${[0, 1, 2, 3, 4, 5].map(k => `<path d="M${k * 112} -6 L${k * 112} 6" stroke="#f4ecff" stroke-width="1.5" opacity=".45"/><text x="${k * 112}" y="30" font-size="14" text-anchor="middle" opacity=".45">${k === 5 ? '5 km' : k}</text>`).join('')}
  <path d="M0 0 L${dx.toFixed(2)} 0" stroke="#ffd2a6" stroke-width="3"/>
  <circle cx="${dx.toFixed(2)}" cy="0" r="16" fill="#ffd2a6" opacity=".25"/><circle cx="${dx.toFixed(2)}" cy="0" r="6" fill="#fff1d6"/>
  <text x="${dx.toFixed(2)}" y="-22" font-size="16" text-anchor="middle" fill="#ffd2a6">${kmc.toFixed(2)} km</text>
 </g>
</g>`;
}
const RAIN = (() => { const a = []; for (let i = 0; i < 220; i++) a.push([rnd() * 2000 - 40, rnd() * 1100, 30 + rnd() * 60, rnd()]); return a; })();
export function river(t, opts = {}) {
  const o = Object.assign({ speed: 3.0, step: 2.8, bob: 0.035, km0: 3.2, sec0: 18 * 60 + 42, day: 37, clock: '06:12 AM', mood: 'dawn', hud: true, z0: 0, kmMul: 1 }, opts);
  CZ = o.zAt != null ? o.zAt : o.z0 + o.speed * t;
  const ph = Math.PI * o.step * t;
  BOB = o.bob * (Math.abs(Math.sin(ph)) - 0.5);
  const roll = -1.6 + (o.bob / 0.035) * 0.5 * Math.sin(ph);
  const sway = (o.bob / 0.035) * 6 * Math.sin(ph / 2);
  let over = '';
  if (o.mood === 'predawn') over = `<rect width="1920" height="1080" fill="#4d5a96" style="mix-blend-mode:multiply" opacity=".9"/><rect width="1920" height="1080" fill="#1a2350" opacity=".25"/>`;
  if (o.mood === 'rain') {
    over = `<rect width="1920" height="1080" fill="#6d7390" style="mix-blend-mode:multiply" opacity=".95"/><rect width="1920" height="1080" fill="#2a3048" opacity=".2"/>`;
    over += RAIN.map(([x, y, l, k]) => { const yy = ((y + t * (900 + k * 500)) % 1180) - 80; const xx = x - yy * 0.12;
      return `<path d="M${xx.toFixed(1)} ${yy.toFixed(1)} l${(-l * 0.12).toFixed(1)} ${l.toFixed(1)}" stroke="#cfd8f0" stroke-width="${(1 + k * 1.5).toFixed(1)}" opacity="${(0.18 + k * 0.25).toFixed(2)}"/>`; }).join('');
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${defs}
<rect width="${W}" height="${H}" fill="#1b2433"/>
<g transform="translate(${sway.toFixed(2)} 0) rotate(${roll.toFixed(3)} 960 540) scale(1.05) translate(-46 -27)">${SKY}${world(t)}</g>
${over}
<rect width="${W}" height="${H}" fill="url(#vig)"/>
${o.hud ? hud(t, o) : ''}`;
}
export { fonts, W, H };
