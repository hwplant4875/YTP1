import { chromium } from 'playwright';
import { FONTS } from './eng.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
const T = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${b}</svg>`;
// shark box 1000x400 at scale 1.06 → 1060 wide; visual centre sits slightly below frame centre
const SX = 110, SY = 225, SC = 1.06;
const grid = (c, o, st) => { let s = ''; for (let x = 0; x <= 1280; x += st) s += `<path d="M${x} 0 V720" stroke="${c}" opacity="${o}"/>`; for (let y = 0; y <= 720; y += st) s += `<path d="M0 ${y} H1280" stroke="${c}" opacity="${o}"/>`; return s; };
const V = {
  a_ocean: T(`<defs><linearGradient id="og" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4fb6ea"/><stop offset="1" stop-color="#1f86c9"/></linearGradient></defs><rect width="1280" height="720" fill="url(#og)"/>
    ${sharkOpen(SX, SY, SC, { cut: 812, id: 'ta', skin: '#ffffff', stroke: '#0d1b3a', sw: 5 })}
    <text x="640" y="165" font-family="Black" font-size="136" fill="#fff" text-anchor="middle">INSIDE A <tspan fill="#0d1b3a">SHARK</tspan></text>`),
  a_blueprint: T(`<rect width="1280" height="720" fill="#1d5fae"/>${grid('#ffffff', 0.12, 32)}${grid('#ffffff', 0.22, 160)}
    <g transform="translate(${SX} ${SY}) scale(${SC})"><defs><clipPath id="bp"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#ffffff" opacity=".12"/>
    <g clip-path="url(#bp)">${anatomy({ col: 1 })}</g><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="7"/></g>
    <text x="640" y="165" font-family="Black" font-size="136" fill="#fff" text-anchor="middle">INSIDE A <tspan fill="#0d1b3a">SHARK</tspan></text>`),
  b: T(`<rect width="1280" height="720" fill="#ff2e3c"/><g transform="translate(${SX} ${SY}) scale(${SC})"><defs><clipPath id="tbx"><path d="${SHARK}"/></clipPath></defs>
     <path d="${SHARK}" fill="#ffffff" opacity=".18"/><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="5"/><g clip-path="url(#tbx)">${anatomy({ organs: 0, muscle: 0, col: 0 })}</g></g>
     <text x="640" y="185" font-family="Black" font-size="190" fill="#fff" text-anchor="middle">0 BONES</text>`),
  c: T(`<rect width="1280" height="720" fill="#eeeae1"/>${sharkOpen(SX, SY, SC, { cut: 1000, stroke: '#111', sw: 5, id: 'tc' })}
     <text x="640" y="165" font-family="Black" font-size="150" fill="#111" text-anchor="middle">CUT <tspan fill="#e0482f">OPEN</tspan></text>`),
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
await p.setContent(`<style>${FONTS}body{margin:0}</style><div id="c"></div>`);
for (const [k, svg] of Object.entries(V)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, svg); await p.waitForTimeout(50); await p.screenshot({ path: `/mnt/project-files/plans/halfcut/v2_specimen/ep01/v2/thumb_${k}.png` }); }
await b.close();
