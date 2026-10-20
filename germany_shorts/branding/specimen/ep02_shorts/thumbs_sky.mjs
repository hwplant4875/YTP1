// hummingbird thumbnails on the video's AIR (alt) sky: #e3f4ff -> #b9e1f7, navy title, soft clouds
import { chromium } from 'playwright';
import { FONTS } from '/tmp/claude-0/sp2/eng2.mjs';
import { birdInside, wings, placeB, birdDefs, toB, PT } from './bird.mjs';
const OUT = '/mnt/project-files/plans/halfcut/v2_specimen/ep02_hummingbird/v3/';
const N = '#0d1b3a', RED = '#ff4d58';
const T = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3f4ff"/><stop offset="1" stop-color="#b9e1f7"/></linearGradient></defs><rect width="1280" height="720" fill="url(#sk)"/>${b}</svg>`;
const cloud = (x, y, w) => `<g fill="#fff" opacity=".8"><ellipse cx="${x}" cy="${y}" rx="${w / 2}" ry="${w / 7}"/><ellipse cx="${x - w / 6}" cy="${y - w / 9}" rx="${w / 5}" ry="${w / 6}"/><ellipse cx="${x + w / 8}" cy="${y - w / 8}" rx="${w / 4.5}" ry="${w / 5}"/></g>`;
const ecg = y => `<path d="M0 ${y} L300 ${y} L330 ${y - 30} L360 ${y + 20} L380 ${y} L860 ${y} L890 ${y - 120} L925 ${y + 90} L955 ${y} L1280 ${y}" stroke="${RED}" stroke-width="12" fill="none" stroke-linejoin="round" opacity=".85"/>`;
const CX = 640, CY = 450, SC = 1.0;
const BI = (o = {}) => placeB(CX, CY, SC, birdDefs() + birdInside({ tongue: 0, ...o }) + wings(0, { still: -35, blur: 0, bones: 1 }));
// analysis callout: dot on the body part, navy leader, white card with part name + big value
const call = (pt, lx, ly, name, val) => { const [px, py] = toB(CX, CY, SC, ...pt), w = Math.max(name.length * 26, val.length * 38) + 50;
  return `<path d="M${px} ${py} L${lx} ${ly}" stroke="${N}" stroke-width="7"/><circle cx="${px}" cy="${py}" r="13" fill="#fff" stroke="${N}" stroke-width="7"/>
  <g transform="translate(${lx} ${ly})"><rect x="${-w / 2}" y="-62" width="${w}" height="124" rx="22" fill="#fff" stroke="${N}" stroke-width="8"/>
  <text y="-16" font-family="Black" font-size="40" fill="${N}" text-anchor="middle">${name}</text><text y="44" font-family="Black" font-size="62" fill="${RED}" text-anchor="middle">${val}</text></g>`; };
const WING = call([430, 182], 190, 330, 'WINGS', '50/SEC'), HEART = call(PT.heart, 1040, 625, 'HEART', '1,200 BPM'), TONGUE = call([975, 199], 1010, 262, 'TONGUE', '15 LICKS/SEC');
const TH = {
  thumb_t1_text: T(`${BI()}<text x="640" y="150" font-family="Black" font-size="140" fill="${N}" text-anchor="middle">HUMMINGBIRD</text>`),
  thumb_t2_notext: T(`${placeB(610, 390, 1.12, birdDefs() + birdInside({ tongue: 0 }) + wings(0, { still: -35, blur: 0, bones: 1 }))}`),
};
const b = await chromium.launch();
for (const [n, s] of Object.entries(TH)) { const p = await b.newPage({ viewport: { width: 1280, height: 720 } }); await p.setContent(`<style>${FONTS}body{margin:0}</style>${s}`); await p.waitForTimeout(80); await p.screenshot({ path: OUT + n + '.png' }); await p.close(); }
await b.close(); console.log('ok');
