// Thumbnail drafts for "If Your Cat Ever Knocks On Your Bedroom Door… DO NOT OPEN IT".
// node thumbs.mjs outdir   -> outdir/thumb_{A,B,C}.jpg (1280x720)
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const out = process.argv[2] || path.join(dir, 'out');
mkdirSync(out, { recursive: true });

const Y = '#ffd23a', RED = '#ff2a2a';

const defs = `<defs>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bloom" x="-10%" y="-10%" width="120%" height="120%">
  <feGaussianBlur stdDeviation="14" result="b"/><feComponentTransfer in="b" result="c"><feFuncA type="linear" slope="0.45"/></feComponentTransfer>
  <feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft"><feGaussianBlur stdDeviation="3.2"/></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/>
  <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.55"/></radialGradient>
<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff4cf"/><stop offset="1" stop-color="#e2cf8e"/></linearGradient>
<clipPath id="gclip"><rect x="700" y="228" width="240" height="262" rx="8"/></clipPath>
</defs>`;

const title = (w, r, fill2 = RED) => `<text x="640" y="150" text-anchor="middle" font-family="M" font-size="132" letter-spacing="-2" fill="#fff">${w} <tspan fill="${fill2}">${r}</tspan></text>`;

// side-view bed with a person lying awake, eye toward the door
function bed(x = 0, dark = false) {
  const W = dark ? '#111' : '#fff', G = dark ? '#7a1010' : '#cfcfcf', G2 = dark ? '#5a0a0a' : '#9a9a9a';
  return `<g transform="translate(${x},0)">
  <rect x="70" y="420" width="36" height="270" rx="14" fill="${W}"/>
  <rect x="70" y="566" width="480" height="58" rx="16" fill="${G}"/>
  <rect x="96" y="620" width="24" height="66" rx="6" fill="${G2}"/><rect x="510" y="620" width="24" height="66" rx="6" fill="${G2}"/>
  <ellipse cx="158" cy="556" rx="50" ry="15" fill="${G}"/>
  <circle cx="168" cy="518" r="40" fill="${W}"/>
  <circle cx="192" cy="508" r="7" fill="${dark ? '#fff' : '#000'}"/>
  <path d="M188,568 C196,520 268,500 340,506 C420,512 480,524 552,546 L552,590 L188,590 Z" fill="${W}"/>
  <path d="M230,452 C222,466 216,476 220,484 A9,9 0 0 0 238,482 C240,474 236,466 230,452Z" fill="${W}"/>
  </g>`;
}

// B: front-view door with frosted glass; a cat silhouette standing at human height behind it
function thumbB() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${defs}
  <rect width="1280" height="720" fill="#000"/>
  ${title("DON'T", 'OPEN')}
  <line x1="0" y1="690" x2="1280" y2="690" stroke="#333" stroke-width="4"/>
  <g filter="url(#bloom)">${bed(20)}</g>
  <rect x="648" y="180" width="344" height="512" fill="none" stroke="#6d6d6d" stroke-width="8"/>
  <rect x="664" y="196" width="312" height="486" rx="6" fill="#f4f4f4" filter="url(#bloom)"/>
  <rect x="664" y="684" width="312" height="6" fill="#fff2b0" filter="url(#glow)"/>
  <rect x="790" y="683" width="34" height="8" fill="#000"/><rect x="852" y="683" width="34" height="8" fill="#000"/>
  <rect x="700" y="228" width="240" height="262" rx="8" fill="url(#glass)" filter="url(#glow)"/>
  <g clip-path="url(#gclip)">
    <g fill="#1b1410" filter="url(#soft)">
      <path d="M786,300 L796,238 L830,286 Z"/><path d="M846,286 L884,240 L886,304 Z"/>
      <ellipse cx="838" cy="318" rx="56" ry="48"/>
      <rect x="806" y="350" width="64" height="40" rx="20"/>
      <ellipse cx="842" cy="470" rx="74" ry="118"/>
      <line x1="800" y1="410" x2="742" y2="330" stroke="#1b1410" stroke-width="30" stroke-linecap="round"/>
    </g>
    <g fill="#120c08"><circle cx="738" cy="324" r="19"/><circle cx="722" cy="304" r="7"/><circle cx="736" cy="298" r="7"/><circle cx="751" cy="303" r="7"/></g>
    <g filter="url(#glow)"><ellipse cx="818" cy="316" rx="11" ry="8" fill="${Y}"/><ellipse cx="860" cy="316" rx="11" ry="8" fill="${Y}"/></g>
    <rect x="816" y="309" width="4" height="14" rx="2" fill="#000"/><rect x="858" y="309" width="4" height="14" rx="2" fill="#000"/>
  </g>
  <rect x="700" y="228" width="240" height="262" rx="8" fill="none" stroke="#bdbdbd" stroke-width="6"/>
  <rect x="704" y="528" width="104" height="128" rx="6" fill="none" stroke="#cfcfcf" stroke-width="6"/>
  <rect x="832" y="528" width="104" height="128" rx="6" fill="none" stroke="#cfcfcf" stroke-width="6"/>
  <rect x="680" y="540" width="14" height="44" rx="6" fill="#8d8d8d"/><circle cx="687" cy="562" r="13" fill="#7a7a7a"/>
  <g stroke="${Y}" stroke-width="9" stroke-linecap="round" filter="url(#glow)">
    <line x1="636" y1="292" x2="602" y2="272"/><line x1="632" y1="326" x2="592" y2="326"/><line x1="636" y1="360" x2="602" y2="380"/>
  </g>
  <rect width="1280" height="720" fill="url(#vig)"/><rect width="1280" height="720" filter="url(#grain)"/>
  </svg>`;
}

// A / C: cutaway. Door seen edge-on in the wall; the cat stands upright in the hallway and knocks
function cutaway(red) {
  const W = red ? '#fff' : '#fff', D = red ? '#000' : '#000';
  const bg = red ? RED : '#000';
  const glowF = red ? '' : 'filter="url(#bloom)"';
  const knock = red ? '#fff' : Y;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${defs}
  <rect width="1280" height="720" fill="${bg}"/>
  ${title("DON'T", 'OPEN', red ? '#000' : RED)}
  <line x1="0" y1="690" x2="1280" y2="690" stroke="${red ? '#b31616' : '#333'}" stroke-width="4"/>
  <g ${glowF}>${bed(0, false)}</g>
  <rect x="690" y="186" width="48" height="504" fill="${red ? '#b31616' : '#2e2e2e'}"/>
  <g ${glowF}>
    <rect x="696" y="232" width="36" height="452" rx="4" fill="${W}"/>
    <rect x="676" y="452" width="22" height="16" rx="6" fill="${W}"/><circle cx="676" cy="460" r="11" fill="${W}"/>
    <rect x="730" y="452" width="22" height="16" rx="6" fill="${W}"/><circle cx="752" cy="460" r="11" fill="${W}"/>
  </g>
  <g ${glowF}>
    <path d="M948,560 C1012,556 1030,488 1004,436" fill="none" stroke="${red ? '#ffd0d0' : '#cfcfcf'}" stroke-width="18" stroke-linecap="round"/>
    <line x1="928" y1="556" x2="946" y2="676" stroke="${red ? '#ffd0d0' : '#cfcfcf'}" stroke-width="24" stroke-linecap="round"/>
    <ellipse cx="958" cy="682" rx="26" ry="9" fill="${red ? '#ffd0d0' : '#cfcfcf'}"/>
    <line x1="896" y1="420" x2="884" y2="520" stroke="${red ? '#ffd0d0' : '#cfcfcf'}" stroke-width="22" stroke-linecap="round"/>
    <ellipse cx="904" cy="470" rx="54" ry="112" transform="rotate(-6 904 470)" fill="${W}"/>
    <line x1="900" y1="556" x2="892" y2="676" stroke="${W}" stroke-width="26" stroke-linecap="round"/>
    <ellipse cx="878" cy="682" rx="28" ry="10" fill="${W}"/>
    <path d="M854,300 L860,236 L896,290 Z" fill="${W}"/><path d="M890,292 L928,246 L930,310 Z" fill="${W}"/>
    <circle cx="884" cy="334" r="50" fill="${W}"/>
    <ellipse cx="846" cy="348" rx="14" ry="12" fill="${W}"/>
    <line x1="872" y1="404" x2="762" y2="326" stroke="${W}" stroke-width="26" stroke-linecap="round"/>
    <circle cx="760" cy="324" r="17" fill="${W}"/>
  </g>
  <path d="M832,342 l8,0 l-4,6 z" fill="${D}"/>
  ${red ? `<ellipse cx="860" cy="322" rx="10" ry="9" fill="#000"/><rect x="858" y="314" width="4" height="16" rx="2" fill="${RED}"/>`
        : `<g filter="url(#glow)"><ellipse cx="860" cy="322" rx="10" ry="9" fill="${Y}"/></g><rect x="858" y="314" width="4" height="16" rx="2" fill="#000"/>`}
  <g stroke="${knock}" stroke-width="9" stroke-linecap="round" ${red ? '' : 'filter="url(#glow)"'}>
    <line x1="664" y1="296" x2="630" y2="276"/><line x1="660" y1="330" x2="620" y2="330"/><line x1="664" y1="364" x2="630" y2="384"/>
  </g>
  ${red ? '' : '<rect width="1280" height="720" fill="url(#vig)"/>'}<rect width="1280" height="720" filter="url(#grain)"/>
  </svg>`;
}

const thumbs = { A: cutaway(false), B: thumbB(), C: cutaway(true) };
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
for (const [k, svg] of Object.entries(thumbs)) {
  const f = path.join(dir, `_t${k}.html`);
  writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:M;font-weight:900;src:url(fonts/montserrat-900.woff2)}
html,body{margin:0;background:#000}</style></head><body>${svg.replace('font-family="M"', 'font-family="M" font-weight="900"')}</body></html>`);
  await page.goto('file://' + f);
  await page.evaluate(() => document.fonts.load('900 100px M'));
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, `thumb_${k}.jpg`), type: 'jpeg', quality: 92 });
}
await browser.close();
console.log('done', out);
