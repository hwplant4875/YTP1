import { chromium } from 'playwright';
import fs from 'fs';
const F = '/tmp/claude-0/-home-user-YTP1/72195fa7-f048-5ed9-a4a5-0cf016be9530/scratchpad/toon/fonts/Montserrat.ttf';
const font = `@font-face{font-family:M;src:url(data:font/ttf;base64,${fs.readFileSync(F).toString('base64')})}`;
const S = 800;
const defs = `<defs>
<radialGradient id="sun" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff6d8"/><stop offset=".55" stop-color="#ffd27a"/><stop offset="1" stop-color="#ff9d4a"/></radialGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2140"/><stop offset=".55" stop-color="#6b4a7a"/><stop offset=".8" stop-color="#ff8a5b"/><stop offset="1" stop-color="#ffc27a"/></linearGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".85"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd9a0"/><stop offset="1" stop-color="#3a3550"/></linearGradient>
</defs>`;
const logos = {
// A: valley V with the sun rising in the notch
A: `<rect width="800" height="800" fill="url(#sky)"/>
<circle cx="400" cy="470" r="230" fill="url(#glow)"/>
<circle cx="400" cy="470" r="92" fill="url(#sun)"/>
<path d="M0 170 L400 560 L800 170 L800 800 L0 800 Z" fill="#0d1020"/>
<path d="M0 260 L400 640 L800 260 L800 800 L0 800 Z" fill="#070912"/>`,
// B: small dark room, one window opening onto sunrise (the founder's story)
B: `<rect width="800" height="800" fill="#0c0e16"/>
<g transform="translate(225 190)"><rect width="350" height="420" rx="10" fill="url(#sky)"/>
<circle cx="175" cy="300" r="140" fill="url(#glow)"/><circle cx="175" cy="300" r="58" fill="url(#sun)"/>
<path d="M0 330 Q90 290 175 320 T350 310 L350 420 L0 420Z" fill="#14182a"/>
<rect x="168" y="0" width="14" height="420" fill="#0c0e16"/><rect x="0" y="200" width="350" height="14" fill="#0c0e16"/>
<rect x="-14" y="-14" width="378" height="448" rx="16" fill="none" stroke="#1d2133" stroke-width="18"/></g>
<path d="M225 610 L60 800 L740 800 L575 610Z" fill="#ffb86b" opacity=".10"/>`,
// C: road in perspective forming an upward point, sun at the end (POV)
C: `<rect width="800" height="800" fill="url(#sky)"/>
<circle cx="400" cy="430" r="250" fill="url(#glow)"/>
<circle cx="400" cy="430" r="80" fill="url(#sun)"/>
<rect y="430" width="800" height="370" fill="#0b0e1a"/>
<path d="M392 430 L408 430 L700 800 L100 800Z" fill="url(#road)"/>
<path d="M399 440 L401 440 L410 800 L390 800Z" fill="#fff3d6" opacity=".9"/>`,
// D: wordmark V: two strokes, the right stroke a road with the sun at the V's base
D: `<rect width="800" height="800" fill="#0b0d16"/>
<circle cx="400" cy="560" r="240" fill="url(#glow)" opacity=".7"/>
<path d="M170 190 L290 190 L400 470 L510 190 L630 190 L455 620 L345 620Z" fill="#f4efe6"/>
<circle cx="400" cy="560" r="44" fill="url(#sun)"/>`,
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: S, height: S } });
for (const [k, v] of Object.entries(logos)) {
  await p.setContent(`<style>${font}body{margin:0}</style><svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">${defs}${v}</svg>`);
  await p.screenshot({ path: `logo_${k}.png` });
}
await b.close();
