// TH=drawThumb|drawThumbPhone node thumbstill.mjs out.png  -> a thumbnail scene from thumb_scene.js at 1920x1080 (needs engine_th.js: the engine sources + thumb_scene.js)
import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname);
writeFileSync(path.join(dir, '_thumb.html'), `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:M;font-weight:900;src:url(../fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../../mindset/fonts/ibm-plex-mono-600.woff2)}
@font-face{font-family:I;font-weight:400;src:url(../../mindset/fonts/inter-400.woff2)}
@font-face{font-family:I;font-weight:500 600;src:url(../../mindset/fonts/inter-600.woff2)}
</style></head><body style="margin:0"><canvas id="c" width="1920" height="1080"></canvas>
<script>window.TL={segments:[{id:'h1',start:0,end:1,words:[]}],events:[],cuts:[],total:1};</script><script src="engine_th.js"></script></body></html>`);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('PAGEERR', e.message));
await p.goto('file://' + path.join(dir, '_thumb.html'));
await p.evaluate(async () => { for (const f of ['900 50px M', '30px Plex', '600 30px Plex', '400 20px I', '600 20px I', '500 20px I']) await document.fonts.load(f); });
const d = await p.evaluate(fn => { window[fn](); return document.getElementById('c').toDataURL('image/png'); }, process.env.TH || 'drawThumb');
writeFileSync(process.argv[2], Buffer.from(d.split(',')[1], 'base64')); await b.close();
