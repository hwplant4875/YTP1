// EP02 thumbnails v3: the phone wide in the centre (thumbstill.mjs TH=drawThumbWide / drawThumbWideRed), DON'T REPLY above it.
// node thumbs_wide.mjs dir   (dir holds wide.png and wide_red.png; writes w1_bw_red.jpg, w2_rec.jpg, w3_redglow.jpg)
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const here = path.dirname(new URL(import.meta.url).pathname), out = process.argv[2];
const V = { w1_bw_red: { bg: 'wide', rec: false }, w2_rec: { bg: 'wide', rec: true }, w3_redglow: { bg: 'wide_red', rec: false } };
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
for (const [n, v] of Object.entries(V)) {
  fs.writeFileSync(here + '/_thw.html', `<html><head><style>
@font-face{font-family:M;font-weight:900;src:url(../fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../../mindset/fonts/ibm-plex-mono-600.woff2)}
body{margin:0;width:1280px;height:720px;overflow:hidden;background:url(file://${out}/${v.bg}.png) center/1280px 720px;position:relative}
.t{position:absolute;left:0;right:0;top:6px;text-align:center;font:900 150px/1 M;letter-spacing:-4px;color:#fff;text-shadow:0 0 18px #000, 0 4px 6px #000}
.t span{color:#ff1f2e}
.r{position:absolute;left:34px;bottom:30px;font:34px Plex;color:#f2f2f2;display:flex;align-items:center;gap:12px;text-shadow:0 2px 10px #000}
.r i{width:24px;height:24px;border-radius:50%;background:#ff2a2a;display:block}
</style></head><body><div class="t">DON'T <span>REPLY</span></div>${v.rec ? '<div class="r"><i></i>REC</div>' : ''}</body></html>`);
  await p.goto('file://' + here + '/_thw.html', { waitUntil: 'load' });
  await p.evaluate(() => Promise.all([document.fonts.load('900 100px M'), document.fonts.load('30px Plex')]));
  await p.screenshot({ path: `${out}/${n}.jpg`, type: 'jpeg', quality: 92 });
}
await b.close();
