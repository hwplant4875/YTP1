import { chromium } from 'playwright'; import { landPath } from './maps.mjs';
const vs = { am: { lon0: -170, lon1: -25, lat0: -58, lat1: 75, x: 560, y: 40, w: 800, h: 1000 }, gulf: { lon0: -102, lon1: -72, lat0: 12, lat1: 38, x: 160, y: 60, w: 1600, h: 960 }, ruf: { lon0: -175, lon1: -80, lat0: 12, lat1: 72, x: 260, y: 40, w: 1400, h: 1000 } };
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
for (const [k, v] of Object.entries(vs)) { const d = landPath(v, k !== 'am');
  await p.setContent(`<body style="margin:0"><svg width="1920" height="1080"><rect width="1920" height="1080" fill="#7cc8f0"/><path d="${d}" fill="#7fd36e" stroke="#0d1b3a" stroke-width="5" stroke-linejoin="round"/></svg>`); await p.screenshot({ path: `chk/map_${k}.png` }); }
await b.close();
