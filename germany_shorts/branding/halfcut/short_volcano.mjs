// HALFCUT #1 "A Volcano, Cut in Half" (9:16, timed to vo.mp3)
export { FONTS } from './volcano.mjs';
export const W = 1080, H = 1920, DUR = 38.5;
const f1 = v => (Math.round(v * 10) / 10).toString();
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const mix = (a, b, k) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * clamp(k)).toString(16).padStart(2, '0')).join(''); };
let S = 7; const rnd = () => (S = (S * 16807) % 2147483647) / 2147483647;

const GY = 1080, MY = 1560;
const cone = (k = 0) => {
  const yb = GY, yt = 560 + k * 1.2, cx = 540, cw = 70 - k * 0.15, x0 = 20 + k * 1.9, x1 = 1060 - k * 1.9;
  return `M${f1(x0)} ${yb} C${f1(x0 + 260)} ${yb - 60} ${f1(cx - cw - 120)} ${f1(yt + 140)} ${f1(cx - cw)} ${f1(yt)} L${f1(cx + cw)} ${f1(yt)} C${f1(cx + cw + 120)} ${f1(yt + 140)} ${f1(x1 - 260)} ${yb - 60} ${f1(x1)} ${yb}Z`;
};
// open slopes (crater rim → base) for the fresh lava layer
const slopeL = `M470 560 C350 700 280 1020 20 1080`, slopeR = `M610 560 C730 700 800 1020 1060 1080`;
const VENTC = `M540 ${MY - 175} C522 1300 548 1150 543 1000 C530 860 552 720 540 565`;

// camera keyframes [t, cx, cy, zoom]
const CAM = [[0, 540, 960, 1.0], [3.0, 540, 980, 1.06], [6.0, 540, 1500, 1.75], [10.6, 540, 1520, 1.85], [12.0, 540, 1540, 2.5], [14.0, 540, 1540, 2.6],
  [15.6, 540, 1250, 1.7], [18.0, 540, 820, 1.55], [20.8, 540, 700, 1.6], [21.3, 540, 820, 1.0], [22.6, 540, 900, 1.05], [26.5, 560, 840, 1.25],
  [29.0, 540, 830, 1.3], [31.0, 420, 850, 1.7], [34.0, 450, 830, 1.65], [36.0, 540, 960, 1.0], [99, 540, 960, 1.0]];
const cam = t => { let i = 0; while (CAM[i + 1][0] <= t) i++; const [t0, ...a] = CAM[i], [t1, ...b] = CAM[i + 1]; const k = sm(t0, t1, t);
  return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)]; };

function world(t, P) {
  const pulse = 0.5 + 0.5 * Math.sin(t * 3), E = P.erupt;
  let s = `<rect x="-600" y="-600" width="2280" height="3120" fill="url(#sky)"/>`;
  S = 3; for (let i = 0; i < 90; i++) s += `<circle cx="${f1(rnd() * 1400 - 160)}" cy="${f1(rnd() * 700 - 100)}" r="${f1(0.8 + rnd() * 1.6)}" fill="#fff" opacity="${f1(0.2 + rnd() * 0.5)}"/>`;
  s += `<path d="M-200 960 C150 900 300 930 420 905 C560 880 700 940 830 900 C930 870 1010 900 1280 890 L1280 1000 L-200 1000Z" fill="#7b5a86"/>`;
  s += `<path d="M-200 ${GY} L-200 985 L1280 985 L1280 ${GY}Z" fill="#4a3d63"/>`;
  s += `<g transform="translate(26 -46)"><path d="${cone()}" fill="#2a2342"/></g>`;
  // ash plume
  S = 11; for (let i = 0; i < 30; i++) { const k = i / 29, r0 = rnd(), r1 = rnd(), r2 = rnd();
    const x = 540 + (r0 - 0.5) * (60 + k * 300 * (0.6 + 0.6 * E)) + k * 330, y = 520 - k * (220 + 260 * E) - ((t * 14 + i * 9) % 30), r = (40 + k * 95 + r1 * 25) * (0.7 + 0.5 * E);
    s += `<circle cx="${f1(x + 6 * Math.sin(t + i))}" cy="${f1(y)}" r="${f1(r)}" fill="${i % 3 ? '#5b4b6e' : '#6c5a7e'}"/>`;
    if (i % 2) s += `<circle cx="${f1(x + 6 * Math.sin(t + i) + r * 0.25)}" cy="${f1(y - r * 0.25)}" r="${f1(r * 0.6)}" fill="#a87f93" opacity=".55"/>`; }
  // crater glow + lava bombs (ballistic, looping)
  s += `<ellipse cx="540" cy="560" rx="${f1(260 + 120 * E)}" ry="${f1(140 + 60 * E)}" fill="url(#glow)" opacity="${f1(clamp(0.5 + 0.3 * pulse + 0.3 * E))}"/>`;
  S = 19; const nb = Math.round(10 + 26 * E);
  for (let i = 0; i < nb; i++) { const vx = (rnd() - 0.5) * 380 * (0.5 + E), vy = 300 + rnd() * 300 * (0.4 + E), ph = rnd(), per = 1.2 + rnd() * 0.6;
    const tt = ((t / per + ph) % 1) * per, x = 540 + vx * tt, y = 555 - vy * tt + 0.5 * 900 * tt * tt;
    if (y < 600) s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(5 + (i % 4) * 3)}" fill="${i % 2 ? '#ffb02e' : '#ff6a1f'}"/>`; }
  // underground
  s += `<g clip-path="url(#groundclip)">`;
  const layers = ['#5b4436', '#6e5141', '#4f3a31', '#7a5845', '#5a3f35', '#6b4337', '#7d3f2c', '#8e3b22', '#9a3a1e'];
  for (let i = 0; i < layers.length; i++) { const y = GY + i * 110;
    s += `<path d="M-200 ${y} C200 ${y + 25} 380 ${y - 20} 560 ${y + 10} C760 ${y + 40} 900 ${y - 10} 1280 ${y + 15} L1280 2400 L-200 2400Z" fill="${layers[i]}"/>`; }
  S = 31; for (let i = 0; i < 110; i++) s += `<ellipse cx="${f1(rnd() * 1400 - 160)}" cy="${f1(GY + 30 + rnd() * 900)}" rx="${f1(4 + rnd() * 10)}" ry="${f1(3 + rnd() * 6)}" fill="#000" opacity=".14"/>`;
  s += `<ellipse cx="540" cy="${MY}" rx="460" ry="270" fill="url(#glow)" opacity="${f1(0.7 + 0.2 * pulse)}"/>`;
  const wob = k => f1(k + 6 * Math.sin(t * 2 + k));
  s += `<path d="M180 ${MY + 20} C200 ${wob(MY - 140)} 360 ${MY - 190} 540 ${wob(MY - 180)} C720 ${MY - 190} 880 ${wob(MY - 120)} 900 ${MY + 10} C910 ${wob(MY + 140)} 740 ${MY + 190} 540 ${MY + 180} C340 ${MY + 190} 170 ${MY + 150} 180 ${MY + 20}Z" fill="url(#mag)"/>`;
  // gas bubbles rising inside the chamber
  S = 41; const bs = P.bubbles; s += `<g clip-path="url(#chclip)">`;
  for (let i = 0; i < 22; i++) { const bx = 250 + rnd() * 580, sp = 40 + rnd() * 60 * (1 + bs), r = (5 + rnd() * 12) * (1 + 0.6 * bs), base = MY + 120 - rnd() * 40;
    const by = base - ((t * sp + i * 37) % 260);
    s += `<circle cx="${f1(bx + 6 * Math.sin(t * 3 + i))}" cy="${f1(by)}" r="${f1(r)}" fill="#fff1b8" opacity=".55"/><circle cx="${f1(bx - r * 0.3)}" cy="${f1(by - r * 0.3)}" r="${f1(r * 0.3)}" fill="#fff" opacity=".6"/>`; }
  s += `</g></g><path d="M-200 ${GY} L1280 ${GY}" stroke="#ffd2a6" stroke-width="3" opacity=".6"/>`;
  // cone strata
  s += `<g clip-path="url(#coneclip)">`;
  const cl = ['#6e5141', '#5b4436', '#7a5845', '#4f3a31', '#6b4a3c', '#59403a', '#73503f', '#4c372f'];
  for (let k = 0; k < 14; k++) s += `<path d="${cone(k * 19)}" fill="${cl[k % 8]}"/>`;
  // "old eruptions" highlight: a glowing edge sweeps through the layers from outside in
  if (P.strata > 0) for (let k = 1; k < 14; k++) { const a = clamp(Math.sin((P.strata * 16 - k) * 0.9) * 1.2) * clamp(P.strata * 6) * (1 - sm(0.92, 1, P.strata));
    if (a > 0.01) s += `<path d="${cone(k * 19)}" fill="none" stroke="#ffd2a6" stroke-width="5" opacity="${f1(a)}"/>`; }
  s += `</g>`;
  // vent + rising magma slug + side dike
  const vent = `M520 ${MY - 175} C500 1300 560 1150 528 1000 C505 860 560 720 525 565 L555 565 C590 720 535 860 558 1000 C590 1150 530 1300 560 ${MY - 175}Z`;
  s += `<path d="${vent}" fill="url(#vent)"/><path d="${vent}" fill="#ffd36b" opacity="${f1(0.15 + 0.25 * pulse + 0.4 * P.press)}" filter="url(#b6)"/>`;
  if (P.rise > 0 && P.rise < 1) s += `<path d="${VENTC}" pathLength="1" stroke="#fff6d0" stroke-width="34" stroke-linecap="round" fill="none" stroke-dasharray="0.09 3" stroke-dashoffset="${f1(-P.rise * 0.95 * 100) / 100}"/>
     <path d="${VENTC}" pathLength="1" stroke="#ffd36b" stroke-width="80" stroke-linecap="round" fill="none" opacity=".45" filter="url(#b6)" stroke-dasharray="0.09 3" stroke-dashoffset="${f1(-P.rise * 0.95 * 100) / 100}"/>`;
  s += `<path d="M530 900 C470 860 380 840 300 760 L310 748 C392 826 480 846 540 884Z" fill="${mix('#ff7a2a', '#ffe08a', P.dike)}"/>`;
  // fresh lava layer running down both slopes, then cooling into rock
  if (P.flow > 0) { const c = mix('#ffb02e', '#7a5845', P.cool), g = (1 - P.cool);
    for (const sl of [slopeL, slopeR]) {
      s += `<path d="${sl}" pathLength="1" stroke="${c}" stroke-width="22" stroke-linecap="round" fill="none" stroke-dasharray="${f1(P.flow * 100) / 100} 2"/>`;
      if (g > 0.02) s += `<path d="${sl}" pathLength="1" stroke="#ff7a2a" stroke-width="60" fill="none" opacity="${f1(0.5 * g)}" filter="url(#b6)" stroke-dasharray="${f1(P.flow * 100) / 100} 2"/>`; } }
  s += `<path d="${cone()}" fill="none" stroke="#ffd2a6" stroke-width="3" opacity=".55"/>`;
  return s;
}

const DEFS = `<defs>
  <linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="-100" x2="0" y2="1000"><stop offset="0" stop-color="#121633"/><stop offset=".45" stop-color="#2f2a5c"/><stop offset=".8" stop-color="#9a5f86"/><stop offset="1" stop-color="#f2b48d"/></linearGradient>
  <radialGradient id="mag" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#fff1b8"/><stop offset=".35" stop-color="#ffb02e"/><stop offset=".75" stop-color="#ff5a1f"/><stop offset="1" stop-color="#c2261b"/></radialGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff7a2a" stop-opacity=".75"/><stop offset="1" stop-color="#ff7a2a" stop-opacity="0"/></radialGradient>
  <linearGradient id="vent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff4d1c"/><stop offset=".5" stop-color="#ffd36b"/><stop offset="1" stop-color="#ff4d1c"/></linearGradient>
  <clipPath id="chclip"><path d="M180 ${MY + 20} C200 ${MY - 140} 360 ${MY - 190} 540 ${MY - 180} C720 ${MY - 190} 880 ${MY - 120} 900 ${MY + 10} C910 ${MY + 140} 740 ${MY + 190} 540 ${MY + 180} C340 ${MY + 190} 170 ${MY + 150} 180 ${MY + 20}Z"/></clipPath>
  <clipPath id="coneclip"><path d="${cone()}"/></clipPath>
  <clipPath id="groundclip"><rect x="-200" y="${GY}" width="1480" height="1400"/></clipPath>
  <filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05040d" stop-opacity=".55"/></radialGradient>
  <radialGradient id="boom" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff1b8" stop-opacity=".9"/><stop offset=".4" stop-color="#ffb02e" stop-opacity=".6"/><stop offset="1" stop-color="#ff5a1f" stop-opacity="0"/></radialGradient>
</defs>`;

// screen-space label pinned to a world point
const label = (C, wx, wy, side, ty, a, b, op) => { if (op <= 0.01) return '';
  const [cx, cy, z] = C, x = (wx - cx) * z + 540, y = (wy - cy) * z + 960;
  const w = Math.max(a.length * 25, b.length * 19.5), tx = side === 'L' ? 70 : 1010, lx = side === 'L' ? tx + w + 18 : tx - w - 18, an = side === 'L' ? 'start' : 'end';
  return `<g opacity="${f1(op)}"><path d="M${f1(x)} ${f1(y)} L${f1(lx)} ${ty} L${tx} ${ty}" stroke="#fff4e6" stroke-width="2.5" fill="none" opacity=".75"/>
  <circle cx="${f1(x)}" cy="${f1(y)}" r="9" fill="#fff4e6"/><circle cx="${f1(x)}" cy="${f1(y)}" r="20" fill="#fff4e6" opacity=".25"/>
  <text x="${tx}" y="${ty - 16}" font-family="InterB" font-size="42" fill="#fff4e6" text-anchor="${an}">${a}</text>
  <text x="${tx}" y="${ty + 38}" font-family="Mono" font-size="32" fill="#ffb36b" text-anchor="${an}">${b}</text></g>`; };
const fadeIO = (t, a, b, d = 0.35) => Math.min(sm(a, a + d, t), 1 - sm(b - d, b, t));
const big = (txt, y, op, size = 150, fill = '#ffd36b') => op <= 0.01 ? '' :
  `<text x="540" y="${y + (1 - op) * 20}" text-anchor="middle" font-family="Black" font-size="${size}" fill="${fill}" stroke="#14112a" stroke-width="12" paint-order="stroke" opacity="${f1(op)}">${txt}</text>`;

function soda(t, op) { if (op <= 0.01) return '';
  const sh = 6 * Math.sin(t * 40) * sm(11.3, 11.8, t), r = 200;
  let s = `<g opacity="${f1(op)}" transform="translate(540 520) scale(${f1(0.85 + 0.15 * op)})"><circle r="${r}" fill="#fff4e6"/><circle r="${r}" fill="none" stroke="#ffb36b" stroke-width="8"/>
  <g transform="rotate(${f1(sh)})"><rect x="-55" y="-120" width="110" height="250" rx="40" fill="#5fae7a"/><rect x="-28" y="-170" width="56" height="70" rx="12" fill="#5fae7a"/>
  <rect x="-32" y="-190" width="64" height="26" rx="6" fill="#c2261b"/><rect x="-55" y="-20" width="110" height="70" fill="#f3e3cf"/>`;
  S = 77; for (let i = 0; i < 14; i++) { const by = 110 - ((t * (120 + rnd() * 120) + i * 40) % 220); s += `<circle cx="${f1((rnd() - 0.5) * 80)}" cy="${f1(by)}" r="${f1(4 + rnd() * 6)}" fill="#fff" opacity=".8"/>`; }
  return s + `</g></g>`; }

function gauge(t, k, op) { if (op <= 0.01) return '';
  const a0 = Math.PI * 0.8, a1 = Math.PI * 2.2, a = a0 + (a1 - a0) * k, r = 120, cx = 540, cy = 1420;
  const arc = (from, to, col, w) => { const x0 = cx + r * Math.cos(from), y0 = cy + r * Math.sin(from), x1 = cx + r * Math.cos(to), y1 = cy + r * Math.sin(to);
    return `<path d="M${f1(x0)} ${f1(y0)} A${r} ${r} 0 ${to - from > Math.PI ? 1 : 0} 1 ${f1(x1)} ${f1(y1)}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`; };
  const jit = k > 0.85 ? 0.04 * Math.sin(t * 60) : 0;
  return `<g opacity="${f1(op)}"><circle cx="${cx}" cy="${cy}" r="${r + 40}" fill="#14112a" opacity=".85"/>${arc(a0, a1, '#3a3566', 18)}${arc(a0, a + 0.001, mix('#ffb02e', '#ff3b1f', k), 18)}
  <path d="M${cx} ${cy} L${f1(cx + (r - 30) * Math.cos(a + jit))} ${f1(cy + (r - 30) * Math.sin(a + jit))}" stroke="#fff4e6" stroke-width="8" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="14" fill="#fff4e6"/>
  <text x="${cx}" y="${cy + 92}" text-anchor="middle" font-family="Mono" font-size="30" letter-spacing="6" fill="#ffd2a6">PRESSURE</text></g>`; }

export function frame(t) {
  const P = {
    erupt: 0.45 + 0.15 * sm(18.3, 21, t) + 1.0 * sm(21.0, 21.4, t) - 0.7 * sm(24, 30, t),
    bubbles: sm(11, 12, t) * (1 - sm(14, 15, t)), rise: sm(14.3, 18.6, t) * (t < 18.7 ? 1 : 0), dike: sm(15.5, 16.5, t) * (1 - sm(18, 19, t)),
    press: sm(18.3, 21, t) * (1 - sm(21.2, 22, t)), flow: sm(22.1, 24.6, t), cool: sm(24.6, 27.4, t), strata: clamp((t - 30.9) / 3.4),
  };
  let [cx, cy, z] = cam(t);
  const shake = 14 * sm(19.5, 21, t) * (1 - sm(21, 23, t)) + 30 * Math.exp(-((t - 21.05) ** 2) / 0.08);
  const sx = shake * Math.sin(t * 53), sy = shake * Math.cos(t * 47);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${DEFS}`;
  s += `<g transform="translate(${f1(540 + sx)} ${f1(960 + sy)}) scale(${z.toFixed(4)}) translate(${f1(-cx)} ${f1(-cy)})">${world(t, P)}</g>`;
  // boom burst
  const bo = Math.exp(-((t - 21.15) ** 2) / 0.15);
  if (bo > 0.01) s += `<circle cx="540" cy="${f1((560 - cy) * z + 960)}" r="${f1(300 + 900 * sm(20.9, 21.8, t))}" fill="url(#boom)" opacity="${f1(bo)}"/>`;
  s += `<rect width="${W}" height="${H}" fill="url(#vig)"/>`;
  const C = [cx, cy, z];
  // title (frame 0 already full)
  const ti = 1 - sm(2.6, 3.2, t);
  if (ti > 0.01) s += `<g opacity="${f1(ti)}"><text x="540" y="250" text-anchor="middle" font-family="Mono" font-size="34" letter-spacing="10" fill="#ffd2a6">CUT IN HALF</text>
    <text x="540" y="355" text-anchor="middle" font-family="Black" font-size="112" fill="#fff4e6" stroke="#14112a" stroke-width="10" paint-order="stroke">A VOLCANO</text></g>`;
  s += label(C, 760, MY - 60, 'R', 1270, 'MAGMA CHAMBER', 'melted rock', fadeIO(t, 7.0, 11.0));
  s += big('1,200 °C', 640, fadeIO(t, 8.1, 11.0));
  s += soda(t, fadeIO(t, 11.0, 14.3));
  s += label(C, 541, 1000, 'L', 720, 'MAIN VENT', 'the way up', fadeIO(t, 15.0, 18.4));
  s += label(C, 318, 762, 'L', 560, 'SIDE DIKE', 'a sneaky crack', fadeIO(t, 16.0, 18.4));
  s += gauge(t, sm(18.3, 20.9, t), fadeIO(t, 18.4, 21.3, 0.25));
  s += big('BOOM', 520, fadeIO(t, 21.0, 22.3, 0.12), 210, '#fff1b8');
  s += label(C, 205, 1000, 'L', 1260, 'NEW LAYER', 'fresh rock', fadeIO(t, 25.0, 28.6));
  s += big('+1 LAYER', 470, fadeIO(t, 27.6, 30.6), 120, '#fff4e6');
  s += big('OLD ERUPTIONS', 470, fadeIO(t, 32.2, 34.5), 104, '#ffd36b');
  const eo = sm(34.6, 35.4, t);
  if (eo > 0.01) s += `<g opacity="${f1(eo)}"><text x="540" y="300" text-anchor="middle" font-family="Black" font-size="84" fill="#fff4e6" stroke="#14112a" stroke-width="10" paint-order="stroke">WHAT SHOULD WE</text>
    <text x="540" y="395" text-anchor="middle" font-family="Black" font-size="84" fill="#ffd36b" stroke="#14112a" stroke-width="10" paint-order="stroke">CUT IN HALF NEXT?</text>
    <g transform="translate(400 500)"><path d="M-8 -60 A60 60 0 0 0 -8 60Z" fill="#fff4e6"/>${[[1, '#8e5a44'], [0.75, '#c2261b'], [0.5, '#ff6a1f'], [0.25, '#ffd36b']].map(([k, c]) => `<path d="M8 ${-60 * k} A${60 * k} ${60 * k} 0 0 1 8 ${60 * k}Z" fill="${c}"/>`).join('')}</g>
    <text x="490" y="520" font-family="Black" font-size="58" letter-spacing="6" fill="#fff4e6" stroke="#14112a" stroke-width="8" paint-order="stroke">HALFCUT</text></g>`;
  return s + '</svg>';
}
