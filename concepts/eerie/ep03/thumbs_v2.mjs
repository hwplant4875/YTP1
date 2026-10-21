// EP03 thumbnails v2: the mapped stills from thumbs_v2.py with DON'T LOOK BACK stacked on the right.
// node thumbs_v2.mjs dir   (dir holds b_bw.png, b_green.png, b_red.png; writes v2_bw_red.jpg, v2_green_rec.jpg, v2_red.jpg)
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const here = path.dirname(new URL(import.meta.url).pathname), out = process.argv[2];
const V = { v2_bw_red: { bg: 'b_bw', rec: false, hot: '#ff1f2e' }, v2_green_rec: { bg: 'b_green', rec: true, hot: '#ff1f2e' }, v2_red: { bg: 'b_red', rec: false, hot: '#000' } };
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
for (const [n, v] of Object.entries(V)) {
  fs.writeFileSync(here + '/_thw.html', `<html><head><style>
@font-face{font-family:M;font-weight:900;src:url(../fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../../mindset/fonts/ibm-plex-mono-600.woff2)}
body{margin:0;width:1280px;height:720px;overflow:hidden;background:url(file://${out}/${v.bg}.png) center/1280px 720px;position:relative}
.t{position:absolute;right:34px;top:50%;transform:translateY(-52%);text-align:right;font:900 136px/0.96 M;letter-spacing:-3px;color:#fff;text-shadow:0 0 22px rgba(0,0,0,0.9), 0 5px 8px #000}
.t span{color:${v.hot}${v.hot === "#000" ? ";text-shadow:none" : ""}}
.r{position:absolute;left:34px;top:28px;font:34px Plex;color:#f2f2f2;display:flex;align-items:center;gap:12px;text-shadow:0 2px 10px #000}
.r i{width:24px;height:24px;border-radius:50%;background:#ff2a2a;display:block}
</style></head><body><div class="t">DON'T<br>LOOK<br><span>BACK</span></div>${v.rec ? '<div class="r"><i></i>REC 03:00:12</div>' : ''}</body></html>`);
  await p.goto('file://' + here + '/_thw.html', { waitUntil: 'load' });
  await p.evaluate(() => Promise.all([document.fonts.load('900 100px M'), document.fonts.load('30px Plex')]));
  await p.screenshot({ path: `${out}/${n}.jpg`, type: 'jpeg', quality: 92 });
}
await b.close();
