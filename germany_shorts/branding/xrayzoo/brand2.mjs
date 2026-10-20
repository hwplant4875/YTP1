// X-RAY ZOO branding v2: 6 profile options, banner, hummingbird thumbnails (new bird design)
import { chromium } from 'playwright';
import { FONTS, K, sharkSolid } from '/tmp/claude-0/sp2/eng2.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
import { birdInside, wings, placeB, birdDefs } from './bird.mjs';
const OUT = '/tmp/claude-0/brand2/';
const N = '#0d1b3a', CY = '#8ff0ff';
const grad = (id, a, b, v = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${v ? 0 : 1}" y2="${v ? 1 : 0}"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
const SQ = b => `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">${b}</svg>`;
const ocean = `<defs>${grad('og', '#4fb6ea', '#1f86c9')}</defs><rect width="800" height="800" fill="url(#og)"/>`;
const sky = `<defs>${grad('sk', '#ffc46b', '#ff8f45')}</defs><rect width="800" height="800" fill="url(#sk)"/>`;
const bone = (len, w) => `<path d="M${-len / 2} ${-w * 0.35} L${len / 2} ${-w * 0.35} A${w * 0.42} ${w * 0.42} 0 1 1 ${len / 2 + w * 0.3} ${-w * 0.02} A${w * 0.42} ${w * 0.42} 0 1 1 ${len / 2} ${w * 0.35} L${-len / 2} ${w * 0.35} A${w * 0.42} ${w * 0.42} 0 1 1 ${-len / 2 - w * 0.3} ${w * 0.02} A${w * 0.42} ${w * 0.42} 0 1 1 ${-len / 2} ${-w * 0.35}Z" fill="#fff" stroke="${N}" stroke-width="14" stroke-linejoin="round"/>`;
const P = {
  // 1 shark head close-up, x-ray body behind the dashed neck line (user idea)
  p1_shark_head: SQ(`<rect width="800" height="800" fill="#3a9fdc"/>${sharkOpen(-1710, -90, 2.4, { cut: 812, id: 'p1', skin: '#ffffff', stroke: N, sw: 3.5 })}
    <g transform="translate(-1710 -90) scale(2.4)"><circle cx="902" cy="186" r="3" fill="#fff"/></g>`),
  // 2 the whole x-ray shark from the EP01 thumbnail
  p2_shark_full: SQ(`${ocean}${sharkOpen(68, 262, 0.665, { cut: 812, id: 'p2', skin: '#ffffff', stroke: N, sw: 7 })}`),
  // 3 hummingbird close-up: cute head + x-ray body
  p3_bird: SQ(`${sky}${placeB(318, 480, 1.3, birdDefs() + birdInside({ tongue: 0, brain: 0 }) + wings(0, { still: -35, blur: 0, bones: 1 }))}`),
  // 4 magnifier over a white shark: inside the lens you see the x-ray
  p4_lens: SQ(`${ocean}<defs><clipPath id="p4s"><path d="${SHARK}"/></clipPath><clipPath id="p4l"><circle cx="560" cy="210" r="175"/></clipPath></defs>
    <g transform="translate(-150 200) scale(0.95)"><path d="${SHARK}" fill="#ffffff" stroke="${N}" stroke-width="7"/><circle cx="905" cy="190" r="10" fill="${N}"/>
      <g clip-path="url(#p4l)"><g clip-path="url(#p4s)"><path d="${SHARK}" fill="#1a1426"/>${anatomy({ col: 1 })}</g><path d="${SHARK}" fill="none" stroke="${N}" stroke-width="7"/></g>
      <g transform="translate(560 210)"><g transform="rotate(135)"><rect x="-44" y="196" width="88" height="230" rx="30" fill="${K.yellow}" stroke="${N}" stroke-width="12"/></g>
      <circle r="175" fill="none" stroke="#fff" stroke-width="30"/><circle r="193" fill="none" stroke="${N}" stroke-width="9"/><circle r="158" fill="none" stroke="${N}" stroke-width="9"/>
      <path d="M-110 -95 Q-80 -135 -25 -150" stroke="#fff" stroke-width="18" stroke-linecap="round" fill="none" opacity=".5"/></g></g>`),
  // 5 stacked wordmark with a scan line
  p5_wordmark: SQ(`<defs>${grad('p5', '#1f7fc4', '#0b3866')}</defs><rect width="800" height="800" fill="url(#p5)"/>
    <text x="400" y="375" font-family="Black" font-size="170" fill="${CY}" text-anchor="middle" stroke="${N}" stroke-width="16" paint-order="stroke">X-RAY</text>
    <path d="M70 420 L730 420" stroke="${CY}" stroke-width="10" stroke-dasharray="30 18" stroke-linecap="round"/>
    <text x="400" y="600" font-family="Black" font-size="200" fill="#fff" text-anchor="middle" stroke="${N}" stroke-width="16" paint-order="stroke">ZOO</text>`),
  // 6 crossed-bones X monogram
  p6_bones: SQ(`<defs><radialGradient id="p6"><stop offset="0" stop-color="#5fd6ff"/><stop offset="1" stop-color="#1f6fd1"/></radialGradient></defs><rect width="800" height="800" fill="url(#p6)"/>
    <g transform="translate(400 345)"><g transform="rotate(45)">${bone(330, 74)}</g><g transform="rotate(-45)">${bone(330, 74)}</g></g>
    <text x="400" y="660" font-family="Black" font-size="150" fill="#fff" text-anchor="middle" stroke="${N}" stroke-width="16" paint-order="stroke">ZOO</text>`),
};
// banner 2560x1440; everything important inside the desktop strip (y 508-931), text in the 1546-wide safe centre
const DOG = (await import('/tmp/claude-0/hb3/t_dog.mjs')).DOG;
const banner = `<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440"><defs>${grad('w', '#4fb6ea', '#1f86c9')}${grad('l', '#8fdc72', '#3e9f4f')}${grad('a', '#ffc46b', '#ff8f45')}
  <filter id="pt" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="12"/><feGaussianBlur stdDeviation="2.5"/></filter></defs>
  <rect width="854" height="1440" fill="url(#w)"/><rect x="853" width="854" height="1440" fill="url(#l)"/><rect x="1706" width="854" height="1440" fill="url(#a)"/>
  ${sharkOpen(10, 595, 0.6, { cut: 812, id: 'bn', skin: '#ffffff', stroke: N, sw: 7 })}
  ${placeB(2140, 740, 0.7, birdDefs() + birdInside({ tongue: 0 }) + wings(0, { still: -35, blur: 0, bones: 1 }))}
  <text x="1280" y="745" font-family="Black" font-size="190" text-anchor="middle" fill="#fff" stroke="${N}" stroke-width="20" paint-order="stroke">X-RAY <tspan fill="${CY}">ZOO</tspan></text>
  <text x="1280" y="860" font-family="Black" font-size="62" text-anchor="middle" fill="#fff" stroke="${N}" stroke-width="10" paint-order="stroke">SEE WHAT'S INSIDE ANIMALS</text></svg>`;
// hummingbird thumbnails with the new design; bird slightly below centre
const T = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${b}</svg>`;
const grid = (c, o, st) => { let s = ''; for (let x = 0; x <= 1280; x += st) s += `<path d="M${x} 0 V720" stroke="${c}" opacity="${o}"/>`; for (let y = 0; y <= 720; y += st) s += `<path d="M0 ${y} H1280" stroke="${c}" opacity="${o}"/>`; return s; };
const ecg = (y, c, o = 1) => `<path d="M0 ${y} L300 ${y} L330 ${y - 30} L360 ${y + 20} L380 ${y} L860 ${y} L890 ${y - 120} L925 ${y + 90} L955 ${y} L1280 ${y}" stroke="${c}" stroke-width="12" fill="none" stroke-linejoin="round" opacity="${o}"/>`;
const X = 650, Y = 430, S = 1.0, BI = o => placeB(X, Y, S, birdDefs() + birdInside({ tongue: 0, ...o }) + wings(0, { still: -35, blur: 0, bones: 1, ...(o.w || {}) }));
const TH = {
  thumb_a_orange: T(`<defs>${grad('sk', '#ffc46b', '#ff8f45')}</defs><rect width="1280" height="720" fill="url(#sk)"/>${BI({})}
    <text x="640" y="150" font-family="Black" font-size="140" fill="${N}" text-anchor="middle">HUMMINGBIRD</text>`),
  thumb_b_heart: T(`<rect width="1280" height="720" fill="#14183a"/>${ecg(500, '#ff4d58', 0.9)}${BI({ heartK: 1.5, glow: 'heart', oc: '#ffffff', w: { oc: '#ffffff' } })}
    <text x="640" y="150" font-family="Black" font-size="150" fill="#fff" text-anchor="middle"><tspan fill="#ff4d58">1,200</tspan> BPM</text>`),
  thumb_c_blueprint: T(`<rect width="1280" height="720" fill="#1d5fae"/>${grid('#ffffff', 0.12, 32)}${grid('#ffffff', 0.22, 160)}${BI({ w: { fill: '#ffffff' } })}
    <text x="640" y="150" font-family="Black" font-size="140" fill="#fff" text-anchor="middle">HUMMINGBIRD</text>`),
};
const b = await chromium.launch();
const shot = async (n, s, w, h) => { const p = await b.newPage({ viewport: { width: w, height: h } }); await p.setContent(`<style>${FONTS}body{margin:0}</style>${s}`); await p.waitForTimeout(80); await p.screenshot({ path: OUT + n + '.png' }); await p.close(); };
for (const [n, s] of Object.entries(P)) await shot(n, s, 800, 800);
await shot('banner', banner, 2560, 1440);
for (const [n, s] of Object.entries(TH)) await shot(n, s, 1280, 720);
await b.close(); console.log('ok');
