// Cutaway thumbnail (cat stands and knocks, person asleep) in several colour palettes.
// node thumbs2.mjs outdir   -> outdir/c_{red,cctv,blood,moon}.jpg
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, rmSync } from 'fs';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const out = process.argv[2] || path.join(dir, 'out');
mkdirSync(out, { recursive: true });

const P = {
  red:   { bg: '#ff2a2a', t1: '#fff', t2: '#000', fig: '#fff', sec: '#ffd0d0', bedG: '#d9d9d9', leg: '#a8a8a8', wall: '#b31616', floor: '#b31616', knock: '#fff', eye: '#000', slit: '#ff2a2a', glow: false },
  cctv:  { bg: '#0c2e14', t1: '#eaffea', t2: '#ff2a2a', fig: '#d8ffdc', sec: '#8fd99a', bedG: '#a9e6b2', leg: '#6fb27a', wall: '#164a22', floor: '#1d5a2a', knock: '#ff2a2a', eye: '#ff2a2a', slit: '#000', glow: true, cctv: true },
  blood: { bg: '#3d0000', t1: '#fff', t2: '#ff2a2a', fig: '#fff', sec: '#e0bcbc', bedG: '#d4d4d4', leg: '#9a8a8a', wall: '#6a0b0b', floor: '#6a0b0b', knock: '#ff2a2a', eye: '#ff2a2a', slit: '#000', glow: true },
  moon:  { bg: '#0b1640', t1: '#fff', t2: '#ff2a2a', fig: '#eef2ff', sec: '#b8c4ee', bedG: '#c9d2f0', leg: '#8a96c4', wall: '#1b2a66', floor: '#22327a', knock: '#ffd23a', eye: '#ffd23a', slit: '#000', glow: true },
};

function svg(p) {
  const G = p.glow ? 'filter="url(#bloom)"' : '';
  const Gk = p.glow ? 'filter="url(#glow)"' : '';
  const { fig: W, sec: S } = p;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bloom" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="14" result="b"/><feComponentTransfer in="b" result="c"><feFuncA type="linear" slope="0.4"/></feComponentTransfer><feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.5"/></radialGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity="0.18"/></pattern>
</defs>
<rect width="1280" height="720" fill="${p.bg}"/>
<text x="640" y="150" text-anchor="middle" font-family="M" font-weight="900" font-size="132" letter-spacing="-2" fill="${p.t1}">DON'T <tspan fill="${p.t2}">OPEN</tspan></text>
<line x1="0" y1="690" x2="1280" y2="690" stroke="${p.floor}" stroke-width="4"/>
<g ${G}>
  <rect x="70" y="420" width="36" height="270" rx="14" fill="${W}"/>
  <rect x="70" y="566" width="480" height="58" rx="16" fill="${p.bedG}"/>
  <rect x="96" y="620" width="24" height="66" rx="6" fill="${p.leg}"/><rect x="510" y="620" width="24" height="66" rx="6" fill="${p.leg}"/>
  <ellipse cx="158" cy="556" rx="50" ry="15" fill="${p.bedG}"/>
  <circle cx="168" cy="522" r="40" fill="${W}"/>
  <path d="M186,560 C196,522 268,504 340,510 C420,516 480,528 552,548 L552,590 L186,590 Z" fill="${W}"/>
</g>
<path d="M178,516 q9,8 18,0" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round"/>
<g font-family="M" font-weight="900" fill="${W}" ${G}><text x="214" y="470" font-size="30">z</text><text x="240" y="440" font-size="40">z</text><text x="272" y="400" font-size="52">Z</text></g>
<rect x="690" y="186" width="48" height="504" fill="${p.wall}"/>
<g ${G}>
  <rect x="696" y="232" width="36" height="452" rx="4" fill="${W}"/>
  <rect x="676" y="452" width="22" height="16" rx="6" fill="${W}"/><circle cx="676" cy="460" r="11" fill="${W}"/>
  <rect x="730" y="452" width="22" height="16" rx="6" fill="${W}"/><circle cx="752" cy="460" r="11" fill="${W}"/>
</g>
<g ${G}>
  <path d="M948,560 C1012,556 1030,488 1004,436" fill="none" stroke="${S}" stroke-width="18" stroke-linecap="round"/>
  <line x1="928" y1="556" x2="946" y2="676" stroke="${S}" stroke-width="24" stroke-linecap="round"/>
  <ellipse cx="958" cy="682" rx="26" ry="9" fill="${S}"/>
  <line x1="896" y1="420" x2="884" y2="520" stroke="${S}" stroke-width="22" stroke-linecap="round"/>
  <ellipse cx="904" cy="470" rx="54" ry="112" transform="rotate(-6 904 470)" fill="${W}"/>
  <line x1="900" y1="556" x2="892" y2="676" stroke="${W}" stroke-width="26" stroke-linecap="round"/>
  <ellipse cx="878" cy="682" rx="28" ry="10" fill="${W}"/>
  <path d="M854,300 L860,236 L896,290 Z" fill="${W}"/><path d="M890,292 L928,246 L930,310 Z" fill="${W}"/>
  <circle cx="884" cy="334" r="50" fill="${W}"/>
  <ellipse cx="846" cy="348" rx="14" ry="12" fill="${W}"/>
  <line x1="872" y1="404" x2="762" y2="326" stroke="${W}" stroke-width="26" stroke-linecap="round"/>
  <circle cx="760" cy="324" r="17" fill="${W}"/>
</g>
<path d="M832,342 l8,0 l-4,6 z" fill="#000"/>
<g ${p.eye === '#000' ? '' : Gk}><ellipse cx="860" cy="322" rx="10" ry="9" fill="${p.eye}"/></g>
<rect x="858" y="314" width="4" height="16" rx="2" fill="${p.slit}"/>
<g stroke="${p.knock}" stroke-width="9" stroke-linecap="round" ${Gk}>
  <line x1="664" y1="296" x2="630" y2="276"/><line x1="660" y1="330" x2="620" y2="330"/><line x1="664" y1="364" x2="630" y2="384"/>
</g>
${p.cctv ? `<rect width="1280" height="720" fill="url(#scan)"/>
<g font-family="Plex" font-size="30" fill="#eaffea"><circle cx="1110" cy="214" r="11" fill="#ff2a2a"/><text x="1130" y="225">REC</text><text x="1040" y="672">03:12 AM</text></g>` : ''}
${p.glow ? '<rect width="1280" height="720" fill="url(#vig)"/>' : ''}<rect width="1280" height="720" filter="url(#grain)"/>
</svg>`;
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
for (const [k, p] of Object.entries(P)) {
  const f = path.join(dir, `_c${k}.html`);
  writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:M;font-weight:900;src:url(fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../mindset/fonts/ibm-plex-mono-600.woff2)}
html,body{margin:0}</style></head><body>${svg(p)}</body></html>`);
  await page.goto('file://' + f);
  await page.evaluate(() => Promise.all([document.fonts.load('900 100px M'), document.fonts.load('30px Plex')]));
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, `c_${k}.jpg`), type: 'jpeg', quality: 92 });
  rmSync(f);
}
await browser.close();
console.log('done', out);
