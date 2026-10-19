import { chromium } from 'playwright';
import { FONTS, K, tag, big, f1 } from '/tmp/claude-0/sp2/eng2.mjs';
import { bgAir, birdSolid, birdInside, wings, placeB, toB, PT, C } from './bird.mjs';
const OUT = '/mnt/project-files/plans/halfcut/v2_specimen/ep02_hummingbird/';
const svg = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">${b}</svg>`;
const T = 5; // all pops finished
const cx = 940, cy = 600, sc = 1.75;
const P = n => toB(cx, cy, sc, ...PT[n]);
const flower = (x, y, s) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 0 L0 420" stroke="#2f9a4f" stroke-width="14"/><path d="M0 200 C60 160 120 180 140 220 C90 240 40 230 0 200Z" fill="#3fbf6a" stroke="${K.navy}" stroke-width="6"/>
  <path d="M-55 -150 C-70 -60 -40 0 0 10 C40 0 70 -60 55 -150 C30 -110 15 -120 0 -160 C-15 -120 -30 -110 -55 -150Z" fill="#ff4f7b" stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"/></g>`;
const frames = {
  hero: bgAir(2) + placeB(cx, cy, sc, birdInside({ tongue: 1 }) + wings(0, { still: 0, blur: 0, bones: 1 }))
    + tag(...P('heart'), 1480, 900, 'HEART', T, 0, { col: K.red, txt: '#fff' })
    + tag(...P('muscle'), 700, 990, 'MUSCLE', T, 0)
    + tag(...P('hyoid'), 1500, 200, 'TONGUE', T, 0, { col: K.yellow }),
  wings: bgAir(4) + placeB(1000, 700, 1.25, wings(0.013, { blur: 5, amp: 60 }) + birdSolid())
    + big(960, 120, '50 PER SECOND', T, 0, { size: 150, sw: 18 }),
  flower: bgAir(6) + flower(1470, 520, 1.25).replace('<g transform="translate(1470 520) scale(1.25)">','<g transform="translate(1470 520) rotate(-35) scale(1.25)">') + placeB(840, 470, 1.15, wings(0.02, { blur: 4, amp: 55 }) + birdSolid(), { rot: 4 })
    + big(560, 930, 'NECTAR', T, 0, { size: 150, fill: K.yellow, sw: 18 }),
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0}</style><div id="c"></div>`);
for (const [n, s] of Object.entries(frames)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, svg(s)); await p.waitForTimeout(40); await p.screenshot({ path: OUT + `style_${n}.png` }); }
await b.close(); console.log('ok');
