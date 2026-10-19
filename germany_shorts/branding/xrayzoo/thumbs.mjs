import { chromium } from 'playwright';
import { FONTS, K } from '/tmp/claude-0/sp2/eng2.mjs';
import { birdSolid, birdInside, anatomyB, wings, placeB, BIRD, C } from './bird.mjs';
const OUT = '/mnt/project-files/plans/halfcut/v2_specimen/ep02_hummingbird/';
const T = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${b}</svg>`;
// bird box centre placed slightly below frame centre
const X = 640, Y = 420, S = 1.15;
const grid = (c, o, st) => { let s = ''; for (let x = 0; x <= 1280; x += st) s += `<path d="M${x} 0 V720" stroke="${c}" opacity="${o}"/>`; for (let y = 0; y <= 720; y += st) s += `<path d="M0 ${y} H1280" stroke="${c}" opacity="${o}"/>`; return s; };
const sky = `<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffc46b"/><stop offset="1" stop-color="#ff8f45"/></linearGradient></defs><rect width="1280" height="720" fill="url(#sk)"/>`;
// ECG trace across the frame with one big spike behind the bird
const ecg = (y, c, o = 1) => `<path d="M0 ${y} L300 ${y} L330 ${y - 30} L360 ${y + 20} L380 ${y} L860 ${y} L890 ${y - 120} L925 ${y + 90} L955 ${y} L1280 ${y}" stroke="${c}" stroke-width="12" fill="none" stroke-linejoin="round" opacity="${o}"/>`;
const V = {
  a_orange: T(`${sky}${placeB(X + 40, Y, S, birdInside({ tongue: 1 }) + wings(0, { still: -35, blur: 0, bones: 1 }))}
    <text x="640" y="150" font-family="Black" font-size="140" fill="${K.navy}" text-anchor="middle">HUMMINGBIRD</text>`),
  b_heart: T(`<rect width="1280" height="720" fill="#14183a"/>${ecg(470, '#ff4d58', 0.9)}
    ${placeB(X + 40, Y + 10, S, birdInside({ tongue: 0, heartK: 1.5, glow: 'heart', oc: '#ffffff' }) + wings(0, { still: -35, blur: 0, bones: 1, oc: '#ffffff' }))}
    <text x="640" y="150" font-family="Black" font-size="150" fill="#fff" text-anchor="middle"><tspan fill="#ff4d58">1,200</tspan> BPM</text>`),
  c_blueprint: T(`<rect width="1280" height="720" fill="#1d5fae"/>${grid('#ffffff', 0.12, 32)}${grid('#ffffff', 0.22, 160)}
    ${placeB(X + 40, Y, S, birdInside({ tongue: 1 }) + wings(0, { still: -35, blur: 0, bones: 1, fill: '#ffffff' }))}
    <text x="640" y="150" font-family="Black" font-size="140" fill="#fff" text-anchor="middle">HUMMINGBIRD</text>`),
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
await p.setContent(`<style>${FONTS}body{margin:0}</style><div id="c"></div>`);
for (const [k, svg] of Object.entries(V)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, svg); await p.waitForTimeout(50); await p.screenshot({ path: OUT + `thumb_${k}.png` }); }
await b.close(); console.log('ok');
