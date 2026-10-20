// node thumbstill.mjs out.png  -> the thumbnail scene from thumb_scene.js at 1920x1080
import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname);
writeFileSync(path.join(dir, '_thumb.html'), `<!doctype html><html><body style="margin:0"><canvas id="c" width="1920" height="1080"></canvas>
<script>window.TL={segments:[{id:'h1',start:0,end:1,words:[]}],events:[],cuts:[],total:1};</script><script src="engine_th.js"></script></body></html>`);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('PAGEERR', e.message));
await p.goto('file://' + path.join(dir, '_thumb.html'));
const d = await p.evaluate(() => { window.drawThumb(); return document.getElementById('c').toDataURL('image/png'); });
writeFileSync(process.argv[2], Buffer.from(d.split(',')[1], 'base64')); await b.close();
