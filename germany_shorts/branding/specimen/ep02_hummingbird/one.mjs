import { chromium } from 'playwright'; import * as m from './main.mjs';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${m.FONTS}body{margin:0}</style><div id="c"></div>`);
for (const i of process.argv.slice(2).map(Number)) { try { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.frame(i / 60)); await p.screenshot({ path: `chk/one_${i}.png` }); console.log('ok', i); } catch (e) { console.log('FAIL', i, String(e).slice(0, 60)); break; } }
await b.close();
