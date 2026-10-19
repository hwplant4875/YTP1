// X-RAY ZOO branding: profile pictures + banner
import { chromium } from 'playwright';
import { FONTS, K, ICON, place, sharkSolid, sharkInside } from '/tmp/claude-0/sp2/eng2.mjs';
import { birdSolid, birdInside, wings, placeB } from './bird.mjs';
const OUT = '/mnt/project-files/plans/halfcut/xrayzoo/branding/';
const N = K.navy, CY = '#8ff0ff';
const grad = (id, a, b, v = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${v ? 0 : 1}" y2="${v ? 1 : 0}"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
// fish skeleton drawn around (0,0), about 420 wide
const fishBones = (c = '#fff', sw = 14) => `<g fill="none" stroke="${c}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">
  <path d="M-150 0 L130 0"/>${[-110, -70, -30, 10, 50, 90].map(x => `<path d="M${x} 0 Q${x + 18} -55 ${x + 6} -92 M${x} 0 Q${x + 18} 55 ${x + 6} 92"/>`).join('')}
  <path d="M-150 0 L-215 -70 L-200 0 L-215 70Z"/>
  <path d="M130 0 C150 -70 230 -80 250 -10 C255 30 220 60 170 55 C150 50 135 30 130 0Z"/></g><circle cx="200" cy="-12" r="${sw * 0.9}" fill="${c}"/>`;
const lens = (bones) => `<circle r="230" fill="url(#lensG)"/><g clip-path="url(#lensC)">${bones}</g>
  <circle r="230" fill="none" stroke="#fff" stroke-width="40"/><circle r="252" fill="none" stroke="${N}" stroke-width="10"/><circle r="208" fill="none" stroke="${N}" stroke-width="10"/>
  <path d="M-150 -120 Q-110 -175 -40 -195" stroke="#fff" stroke-width="22" stroke-linecap="round" fill="none" opacity=".55"/>`;
const handle = `<g transform="rotate(45)"><rect x="-48" y="250" width="96" height="230" rx="30" fill="${K.yellow}" stroke="${N}" stroke-width="12"/></g>`;
const defsLens = `${grad('lensG', '#1f7fc4', '#0b3866')}<clipPath id="lensC"><circle r="225"/></clipPath>`;

const P = {
  // profile A: magnifier x-ray lens on orange
  profile_a: `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><defs>${grad('bg', '#ffc46b', '#ff8f45')}${defsLens}</defs>
    <rect width="800" height="800" fill="url(#bg)"/><g transform="translate(501 299) scale(0.85)">${handle}${lens(`<g transform="scale(0.82) translate(-20 0)">${fishBones()}</g>`)}</g></svg>`,
  // profile B: same lens on habitat tri-colour
  profile_b: `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><defs>${defsLens}</defs>
    <rect width="800" height="800" fill="#4cb3e8"/><path d="M0 800 L0 470 L800 330 L800 800Z" fill="#5fc068"/><path d="M0 0 L800 0 L800 170 L0 300Z" fill="#ffa955"/>
    <g transform="translate(501 299) scale(0.85)">${handle}${lens(`<g transform="scale(0.82) translate(-20 0)">${fishBones()}</g>`)}</g></svg>`,
  // profile C: stacked wordmark
  profile_c: `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><defs>${grad('bg', '#1f7fc4', '#0b3866')}</defs>
    <rect width="800" height="800" fill="url(#bg)"/>
    <text x="400" y="390" font-family="Black" font-size="165" fill="${CY}" text-anchor="middle" stroke="${N}" stroke-width="16" paint-order="stroke">X-RAY</text>
    <text x="400" y="575" font-family="Black" font-size="190" fill="#fff" text-anchor="middle" stroke="${N}" stroke-width="16" paint-order="stroke">ZOO</text></svg>`,
};

// banner 2560x1440; safe area for all devices is the centre 1546x423 (y 508-931)
const panel = (x, w, a, b, id) => `${grad(id, a, b)}`;
const banner = () => {
  const s = `<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440"><defs>${grad('w', '#4cb3e8', '#1f7fc4')}${grad('l', '#7fd36e', '#3e9f4f')}${grad('a', '#ffc46b', '#ff8f45')}
    ${grad('scan', 'rgba(143,240,255,0)', 'rgba(143,240,255,.0)')}</defs>
    <rect x="0" y="0" width="854" height="1440" fill="url(#w)"/><rect x="853" y="0" width="854" height="1440" fill="url(#l)"/><rect x="1706" y="0" width="854" height="1440" fill="url(#a)"/>
    ${place(310, 735, 0.56, sharkInside())}
    ${placeB(2230, 745, 0.6, wings(0, { still: -25, blur: 0 }) + birdInside({ tongue: 0 }))}
    <text x="1280" y="735" font-family="Black" font-size="210" text-anchor="middle" fill="#fff" stroke="${N}" stroke-width="22" paint-order="stroke">X-RAY <tspan fill="${CY}">ZOO</tspan></text>
    <text x="1280" y="845" font-family="Black" font-size="66" text-anchor="middle" fill="${N}">SEE WHAT'S INSIDE ANIMALS</text></svg>`;
  return s;
};
P.banner = banner();
const b = await chromium.launch();
for (const [n, s] of Object.entries(P)) { const [w, h] = n === 'banner' ? [2560, 1440] : [800, 800];
  const p = await b.newPage({ viewport: { width: w, height: h } }); await p.setContent(`<style>${FONTS}body{margin:0}</style>${s}`); await p.waitForTimeout(60);
  await p.screenshot({ path: OUT + n + '.png' }); await p.close(); }
await b.close(); console.log('ok');
