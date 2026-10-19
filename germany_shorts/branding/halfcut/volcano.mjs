// HALFCUT style frame: a volcano cut in half (9:16)
import fs from 'fs';
const FD = '/tmp/claude-0/vz/flat/fonts/';
const ff = (n, f, fmt = 'woff2') => `@font-face{font-family:${n};src:url(data:font/${fmt};base64,${fs.readFileSync(f).toString('base64')})}`;
export const FONTS = ff('Mono', FD + 'mono.woff2') + ff('Inter', FD + 'inter.woff2') + ff('InterB', FD + 'interb.woff2')
  + ff('Black', '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', 'otf');
export const W = 1080, H = 1920;
const f1 = v => (Math.round(v * 10) / 10).toString();
let S = 7; const rnd = () => (S = (S * 16807) % 2147483647) / 2147483647;

// cone profile: concave slopes from base (x0..x1 at yb) to crater rim (cx±cw at yt)
const GY = 1080;                 // front ground edge
const cone = (k = 0) => {        // k = inset (for layers)
  const yb = GY, yt = 560 + k * 1.2, cx = 540, cw = 70 - k * 0.15, x0 = 20 + k * 1.9, x1 = 1060 - k * 1.9;
  return `M${f1(x0)} ${yb} C${f1(x0 + 260)} ${yb - 60} ${f1(cx - cw - 120)} ${f1(yt + 140)} ${f1(cx - cw)} ${f1(yt)} L${f1(cx + cw)} ${f1(yt)} C${f1(cx + cw + 120)} ${f1(yt + 140)} ${f1(x1 - 260)} ${yb - 60} ${f1(x1)} ${yb}Z`;
};
const label = (x, y, side, ty, a, b, op = 1) => {
  const w = Math.max(a.length * 21, b.length * 16.2), tx = side === 'L' ? 60 : 1020, lx = side === 'L' ? tx + w + 16 : tx - w - 16;
  const an = side === 'L' ? 'start' : 'end';
  return `<g opacity="${op}">
  <path d="M${x} ${y} L${f1(lx)} ${ty} L${side === 'L' ? tx : tx} ${ty}" stroke="#fff4e6" stroke-width="2" fill="none" opacity=".7"/>
  <circle cx="${x}" cy="${y}" r="7" fill="#fff4e6"/><circle cx="${x}" cy="${y}" r="16" fill="#fff4e6" opacity=".25"/>
  <text x="${tx}" y="${ty - 14}" font-family="InterB" font-size="34" fill="#fff4e6" text-anchor="${an}">${a}</text>
  <text x="${tx}" y="${ty + 32}" font-family="Mono" font-size="26" fill="#ffb36b" text-anchor="${an}">${b}</text></g>`; };
export function frame(t = 0, { title = true, labels = 1, erupt = 0.35 } = {}) {
  const pulse = 0.5 + 0.5 * Math.sin(t * 3);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121633"/><stop offset=".45" stop-color="#2f2a5c"/><stop offset=".8" stop-color="#9a5f86"/><stop offset="1" stop-color="#f2b48d"/></linearGradient>
  <radialGradient id="mag" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#fff1b8"/><stop offset=".35" stop-color="#ffb02e"/><stop offset=".75" stop-color="#ff5a1f"/><stop offset="1" stop-color="#c2261b"/></radialGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff7a2a" stop-opacity=".75"/><stop offset="1" stop-color="#ff7a2a" stop-opacity="0"/></radialGradient>
  <linearGradient id="vent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff4d1c"/><stop offset=".5" stop-color="#ffd36b"/><stop offset="1" stop-color="#ff4d1c"/></linearGradient>
  <clipPath id="coneclip"><path d="${cone()}"/></clipPath>
  <clipPath id="groundclip"><rect x="0" y="${GY}" width="${W}" height="${H - GY}"/></clipPath>
  <filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05040d" stop-opacity=".55"/></radialGradient>
  </defs>`;
  s += `<rect width="${W}" height="${H}" fill="url(#sky)"/>`;
  // stars
  S = 3; for (let i = 0; i < 70; i++) s += `<circle cx="${f1(rnd() * W)}" cy="${f1(rnd() * 600)}" r="${f1(0.8 + rnd() * 1.6)}" fill="#fff" opacity="${f1(0.2 + rnd() * 0.5)}"/>`;
  // distant hills in haze
  s += `<path d="M0 960 C150 900 300 930 420 905 C560 880 700 940 830 900 C930 870 1010 900 1080 890 L1080 1000 L0 1000Z" fill="#7b5a86"/>`;
  // ground top surface (receding plane)
  s += `<path d="M0 ${GY} L0 985 L1080 985 L1080 ${GY}Z" fill="#4a3d63"/>`;
  // back half of the cone peeking (depth), then ash plume
  s += `<g transform="translate(26 -46)"><path d="${cone()}" fill="#2a2342"/></g>`;
  // ash plume (behind crater rim)
  S = 11; const puffs = [];
  for (let i = 0; i < 26; i++) { const k = i / 25; puffs.push([540 + (rnd() - 0.5) * (60 + k * 300) + k * 330, 520 - k * 300 - erupt * 60 * k, 45 + k * 95 + rnd() * 25]); }
  puffs.forEach(([x, y, r], i) => { s += `<circle cx="${f1(x + 6 * Math.sin(t + i))}" cy="${f1(y - t * 8)}" r="${f1(r)}" fill="${i % 3 ? '#5b4b6e' : '#6c5a7e'}"/>`; });
  puffs.forEach(([x, y, r], i) => { if (i % 2) s += `<circle cx="${f1(x + 6 * Math.sin(t + i) + r * 0.25)}" cy="${f1(y - t * 8 - r * 0.25)}" r="${f1(r * 0.6)}" fill="#a87f93" opacity=".55"/>`; });
  // crater glow + lava fountain
  s += `<ellipse cx="540" cy="560" rx="260" ry="140" fill="url(#glow)" opacity="${f1(0.6 + 0.3 * pulse)}"/>`;
  S = 19; for (let i = 0; i < 18; i++) { const a = -Math.PI / 2 + (rnd() - 0.5) * 1.2, d = 40 + rnd() * 160 * (0.5 + erupt);
    s += `<circle cx="${f1(540 + Math.cos(a) * d)}" cy="${f1(550 + Math.sin(a) * d)}" r="${f1(5 + rnd() * 10)}" fill="${rnd() < 0.5 ? '#ffb02e' : '#ff6a1f'}"/>`; }
  // underground cut face: crust layers
  s += `<g clip-path="url(#groundclip)">`;
  const layers = ['#5b4436', '#6e5141', '#4f3a31', '#7a5845', '#5a3f35', '#6b4337', '#7d3f2c', '#8e3b22'];
  for (let i = 0; i < layers.length; i++) { const y = GY + i * 110;
    s += `<path d="M0 ${y} C200 ${y + 25} 380 ${y - 20} 560 ${y + 10} C760 ${y + 40} 900 ${y - 10} 1080 ${y + 15} L1080 ${H} L0 ${H}Z" fill="${layers[i]}"/>`; }
  // pebbles in strata
  S = 31; for (let i = 0; i < 90; i++) s += `<ellipse cx="${f1(rnd() * W)}" cy="${f1(GY + 30 + rnd() * 760)}" rx="${f1(4 + rnd() * 10)}" ry="${f1(3 + rnd() * 6)}" fill="#000" opacity=".14"/>`;
  // magma chamber
  const my = 1560;
  s += `<ellipse cx="540" cy="${my}" rx="440" ry="250" fill="url(#glow)" opacity="${f1(0.7 + 0.2 * pulse)}"/>`;
  s += `<path d="M180 ${my + 20} C200 ${my - 140} 360 ${my - 190} 540 ${my - 180} C720 ${my - 190} 880 ${my - 120} 900 ${my + 10} C910 ${my + 140} 740 ${my + 190} 540 ${my + 180} C340 ${my + 190} 170 ${my + 150} 180 ${my + 20}Z" fill="url(#mag)"/>`;
  // bubbles in magma
  S = 41; for (let i = 0; i < 14; i++) { const bx = 260 + rnd() * 560, by = my - 80 + rnd() * 200 - ((t * 40 + i * 30) % 120);
    s += `<circle cx="${f1(bx)}" cy="${f1(by)}" r="${f1(6 + rnd() * 14)}" fill="#fff1b8" opacity=".5"/>`; }
  s += `</g>`;
  // ground cut edge highlight
  s += `<path d="M0 ${GY} L1080 ${GY}" stroke="#ffd2a6" stroke-width="3" opacity=".6"/>`;
  // cone cut face: layered strata following the slopes
  s += `<g clip-path="url(#coneclip)">`;
  const cl = ['#6e5141', '#5b4436', '#7a5845', '#4f3a31', '#6b4a3c', '#59403a', '#73503f', '#4c372f'];
  for (let k = 0; k < 14; k++) s += `<path d="${cone(k * 19)}" fill="${cl[k % 8]}"/>`;
  s += `</g>`;
  // conduit from chamber to crater, and a side dike
  const vent = `M520 ${my - 175} C500 1300 560 1150 528 1000 C505 860 560 720 525 565 L555 565 C590 720 535 860 558 1000 C590 1150 530 1300 560 ${my - 175}Z`;
  s += `<path d="${vent}" fill="url(#vent)"/><path d="${vent}" fill="#ffd36b" opacity="${f1(0.15 + 0.25 * pulse)}" filter="url(#b6)"/>`;
  s += `<path d="M530 900 C470 860 380 840 300 760 L310 748 C392 826 480 846 540 884Z" fill="#ff7a2a"/>`;
  // cone silhouette rim light + cut edge
  s += `<path d="${cone()}" fill="none" stroke="#ffd2a6" stroke-width="3" opacity=".55"/>`;
  s += `<rect width="${W}" height="${H}" fill="url(#vig)"/>`;
  if (labels) {
    s += label(530, 700, 'L', 640, 'MAIN VENT', 'the way up', labels);
    s += label(318, 762, 'L', 860, 'SIDE DIKE', 'a sneaky shortcut', labels);
    s += label(780, my - 60, 'R', 1330, 'MAGMA CHAMBER', '≈ 1,200 °C', labels);
    s += label(880, 1140, 'R', 1200, 'CRUST', 'solid rock', labels);
  }
  if (title) s += `<text x="540" y="250" text-anchor="middle" font-family="Mono" font-size="32" letter-spacing="10" fill="#ffd2a6">CUT IN HALF</text>
  <text x="540" y="350" text-anchor="middle" font-family="Black" font-size="104" fill="#fff4e6">A VOLCANO</text>`;
  return s + '</svg>';
}
