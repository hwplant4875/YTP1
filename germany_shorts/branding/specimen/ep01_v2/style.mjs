import { chromium } from 'playwright';
import { FONTS } from '/tmp/claude-0/sp/eng.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
const W = 1920, H = 1080, NAVY = '#0d1b3a';
const bg = () => `<defs><linearGradient id="og" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4cb3e8"/><stop offset="1" stop-color="#1f7fc4"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#og)"/>`;
// big label: pill with Black text, thick leader line to a point
const tag = (px, py, tx, ty, word, col = '#fff', txt = NAVY, size = 72) => { const w = word.length * size * 0.66 + 70, h = size + 40;
  return `<path d="M${px} ${py} L${tx} ${ty}" stroke="#fff" stroke-width="6"/><circle cx="${px}" cy="${py}" r="14" fill="#fff" stroke="${NAVY}" stroke-width="5"/>
  <rect x="${tx - w / 2}" y="${ty - h / 2}" width="${w}" height="${h}" rx="${h / 2}" fill="${col}"/><text x="${tx}" y="${ty + size * 0.36}" font-family="Black" font-size="${size}" fill="${txt}" text-anchor="middle">${word}</text>`; };
const S = {
  hero: `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${bg()}${sharkOpen(190, 330, 1.55, { cut: 812, id: 'h', skin: '#ffffff', stroke: NAVY, sw: 5 })}
    ${tag(190 + 580 * 1.55, 330 + 262 * 1.55, 1000, 960, 'LIVER', '#f2b632')}${tag(190 + 770 * 1.55, 330 + 272 * 1.55, 1500, 960, 'HEART', '#ff5a4f', '#fff')}${tag(190 + 500 * 1.55, 330 + 170 * 1.55, 760, 190, 'SPINE')}</svg>`,
  bones: `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${bg()}<g transform="translate(260 330) scale(1.4)"><defs><clipPath id="c"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#fff" opacity=".18"/><g clip-path="url(#c)">${anatomy({ organs: 0, muscle: 0, col: 0 })}</g><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="5"/></g>
    <text x="960" y="250" font-family="Black" font-size="230" fill="#fff" text-anchor="middle">0 BONES</text>${tag(260 + 600 * 1.4, 330 + 168 * 1.4, 1500, 980, 'CARTILAGE', NAVY, '#fff', 64)}</svg>`,
  float: `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${bg()}<path d="M0 560 Q480 530 960 560 T1920 560 L1920 1080 L0 1080Z" fill="#1667a8" opacity=".55"/>
    <g transform="translate(160 260) scale(1.2)"><defs><clipPath id="l"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#fff"/><g clip-path="url(#l)"><path d="M445 238 C480 226 620 222 712 236 C690 262 640 284 560 286 C500 288 460 270 445 238Z" fill="#f2b632"/></g><path d="${SHARK}" fill="none" stroke="${NAVY}" stroke-width="4"/></g>
    ${tag(160 + 580 * 1.2, 260 + 260 * 1.2, 900, 900, 'LIVER = FLOAT', '#f2b632', NAVY, 80)}
    <g transform="translate(1600 330)"><circle r="150" fill="none" stroke="#ff5a4f" stroke-width="70"/><circle r="150" fill="none" stroke="#fff" stroke-width="70" stroke-dasharray="118 118"/></g></svg>`,
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
await p.setContent(`<style>${FONTS}body{margin:0}</style><div id="c"></div>`);
for (const [k, s] of Object.entries(S)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, s); await p.waitForTimeout(50); await p.screenshot({ path: `/mnt/project-files/plans/halfcut/v2_specimen/ep01/v2/style_${k}.png` }); }
await b.close();
