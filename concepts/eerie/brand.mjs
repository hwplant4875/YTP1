// Channel branding: profile picture (800x800) and banner (2560x1440, safe area 1546x423).
// node brand.mjs outdir "NIGHT CAM" "RULES"
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, rmSync } from 'fs';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const out = process.argv[2] || path.join(dir, 'out');
const N1 = process.argv[3] || 'NIGHT CAM', N2 = process.argv[4] || 'RULES';
mkdirSync(out, { recursive: true });

const C = { bg: '#0c2e14', fig: '#d8ffdc', sec: '#8fd99a', bedG: '#a9e6b2', leg: '#6fb27a', wall: '#164a22', floor: '#1d5a2a', red: '#ff2a2a', txt: '#eaffea' };
const defs = `<defs>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bloom" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="14" result="b"/><feComponentTransfer in="b" result="c"><feFuncA type="linear" slope="0.4"/></feComponentTransfer><feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="shine" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="22" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="72%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.6"/></radialGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity="0.18"/></pattern>
</defs>`;

// same drawing as the thumbnails, in thumbnail coordinates (floor at y=690)
const bed = `<g filter="url(#bloom)">
  <rect x="70" y="420" width="36" height="270" rx="14" fill="${C.fig}"/>
  <rect x="70" y="566" width="480" height="58" rx="16" fill="${C.bedG}"/>
  <rect x="96" y="620" width="24" height="66" rx="6" fill="${C.leg}"/><rect x="510" y="620" width="24" height="66" rx="6" fill="${C.leg}"/>
  <ellipse cx="150" cy="556" rx="50" ry="15" fill="${C.bedG}"/>
  <circle cx="204" cy="456" r="40" fill="${C.fig}"/>
  <path d="M150,568 C150,522 176,498 214,498 C262,498 300,506 340,510 C420,516 480,528 552,548 L552,590 L150,590 Z" fill="${C.fig}"/>
</g><circle cx="230" cy="450" r="9" fill="#000"/>`;
const catDoor = `<rect x="690" y="186" width="48" height="504" fill="${C.wall}"/>
<g filter="url(#bloom)">
  <rect x="696" y="232" width="36" height="452" rx="4" fill="${C.fig}"/>
  <rect x="676" y="452" width="22" height="16" rx="6" fill="${C.fig}"/><circle cx="676" cy="460" r="11" fill="${C.fig}"/>
  <rect x="730" y="452" width="22" height="16" rx="6" fill="${C.fig}"/><circle cx="752" cy="460" r="11" fill="${C.fig}"/>
  <path d="M948,560 C1012,556 1030,488 1004,436" fill="none" stroke="${C.sec}" stroke-width="18" stroke-linecap="round"/>
  <line x1="928" y1="556" x2="946" y2="676" stroke="${C.sec}" stroke-width="24" stroke-linecap="round"/>
  <ellipse cx="958" cy="682" rx="26" ry="9" fill="${C.sec}"/>
  <line x1="896" y1="420" x2="884" y2="520" stroke="${C.sec}" stroke-width="22" stroke-linecap="round"/>
  <ellipse cx="904" cy="470" rx="54" ry="112" transform="rotate(-6 904 470)" fill="${C.fig}"/>
  <line x1="900" y1="556" x2="892" y2="676" stroke="${C.fig}" stroke-width="26" stroke-linecap="round"/>
  <ellipse cx="878" cy="682" rx="28" ry="10" fill="${C.fig}"/>
  <path d="M854,300 L860,236 L896,290 Z" fill="${C.fig}"/><path d="M890,292 L928,246 L930,310 Z" fill="${C.fig}"/>
  <circle cx="884" cy="334" r="50" fill="${C.fig}"/>
  <ellipse cx="846" cy="348" rx="14" ry="12" fill="${C.fig}"/>
  <line x1="872" y1="404" x2="762" y2="326" stroke="${C.fig}" stroke-width="26" stroke-linecap="round"/>
  <circle cx="760" cy="324" r="17" fill="${C.fig}"/>
</g>
<path d="M832,342 l8,0 l-4,6 z" fill="#000"/>
<g filter="url(#glow)"><ellipse cx="860" cy="322" rx="10" ry="9" fill="${C.red}"/></g>
<rect x="858" y="314" width="4" height="16" rx="2" fill="#000"/>
<g stroke="${C.red}" stroke-width="9" stroke-linecap="round" filter="url(#glow)">
  <line x1="664" y1="296" x2="630" y2="276"/><line x1="660" y1="330" x2="620" y2="330"/><line x1="664" y1="364" x2="630" y2="384"/>
</g>`;

// profile: one glowing red cat eye inside a night-cam viewfinder
const profile = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">${defs}
<rect width="800" height="800" fill="${C.bg}"/>
<g fill="none" stroke="${C.txt}" stroke-width="16" stroke-linecap="square" opacity="0.9">
  <path d="M190,250 v-60 h60 M610,250 v-60 h-60 M190,550 v60 h60 M610,550 v60 h-60"/></g>
<g filter="url(#shine)"><path d="M232,400 C300,300 500,300 568,400 C500,500 300,500 232,400 Z" fill="${C.red}"/></g>
<path d="M232,400 C300,300 500,300 568,400 C500,500 300,500 232,400 Z" fill="${C.red}"/>
<path d="M400,322 C424,360 424,440 400,478 C376,440 376,360 400,322 Z" fill="#000"/>
<circle cx="452" cy="372" r="12" fill="#fff" opacity="0.85"/>
<g font-family="Plex" font-size="44" fill="${C.txt}"><circle cx="318" cy="168" r="16" fill="${C.red}"/><text x="346" y="183">REC</text></g>
<rect width="800" height="800" fill="url(#scan)"/><rect width="800" height="800" fill="url(#vig)"/><rect width="800" height="800" filter="url(#grain)"/>
</svg>`;

// banner: name in the safe area, bed on the left and the knocking cat on the right inside the desktop strip
const banner = `<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">${defs}
<rect width="2560" height="1440" fill="${C.bg}"/>
<line x1="0" y1="922" x2="2560" y2="922" stroke="${C.floor}" stroke-width="4"/>
<g transform="translate(250,404) scale(0.75)">${bed}</g>
<g transform="translate(1530,404) scale(0.75)">${catDoor}</g>
<text x="1280" y="690" text-anchor="middle" font-family="M" font-weight="900" font-size="120" letter-spacing="-2" fill="${C.txt}">${N1} <tspan fill="${C.red}">${N2}</tspan></text>
<text x="1280" y="770" text-anchor="middle" font-family="Plex" font-size="40" fill="${C.txt}" opacity="0.85">THE CAMERA SAW IT. NOW YOU KNOW THE RULES.</text>
<g font-family="Plex" font-size="36" fill="${C.txt}"><circle cx="533" cy="556" r="13" fill="${C.red}"/><text x="556" y="568">REC</text><text x="1960" y="568" text-anchor="end">03:12 AM</text></g>
<rect width="2560" height="1440" fill="url(#scan)"/><rect width="2560" height="1440" fill="url(#vig)"/><rect width="2560" height="1440" filter="url(#grain)"/>
</svg>`;

const browser = await chromium.launch();
for (const [name, svg, w, h] of [['profile', profile, 800, 800], ['banner', banner, 2560, 1440]]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const f = path.join(dir, `_b${name}.html`);
  writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:M;font-weight:900;src:url(fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../mindset/fonts/ibm-plex-mono-600.woff2)}
html,body{margin:0}</style></head><body>${svg}</body></html>`);
  await page.goto('file://' + f);
  await page.evaluate(() => Promise.all([document.fonts.load('900 100px M'), document.fonts.load('30px Plex')]));
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, `${name}.png`) });
  rmSync(f); await page.close();
}
await browser.close();
console.log('done', out);
