// EP02 thumbnails: title and the "Are you awake?" bubble over the three colour backgrounds from th/bg.py.
// node thumbs.mjs dir   (dir holds bg_1a/1b/1c.png; writes 1a_green_rec.jpg, 1b_bw_red.jpg, 1c_red.jpg)
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const here = path.dirname(new URL(import.meta.url).pathname), out = process.argv[2];
const V = {
  '1a_green_rec': { bg: '1a', t1: '#eaffea', t2: '#ff1f2e', rec: '#eaffea', bub: '#1d3a22', bt: '#eaffea', sh: '0 0 18px #000, 0 4px 6px #000' },
  '1b_bw_red':    { bg: '1b', t1: '#ffffff', t2: '#ff1f2e', rec: null, bub: '#2a2a2a', bt: '#ffffff', sh: '0 0 18px #000, 0 4px 6px #000' },
  '1c_red':       { bg: '1c', t1: '#ffffff', t2: '#0a0000', rec: null, bub: '#0a0000', bt: '#ffffff', dot: '#0a0000', sh: '0 4px 10px #0006' },
};
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
for (const [n, v] of Object.entries(V)) {
  fs.writeFileSync(here + '/_th.html', `<html><head><style>
@font-face{font-family:M;font-weight:900;src:url(../fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../../mindset/fonts/ibm-plex-mono-600.woff2)}
@font-face{font-family:I;font-weight:600;src:url(../../mindset/fonts/inter-600.woff2)}
body{margin:0;width:1280px;height:720px;overflow:hidden;background:url(file://${out}/bg_${v.bg}.png);position:relative}
.t{position:absolute;right:46px;text-align:right;font:900 172px/0.9 M;letter-spacing:-5px;text-shadow:${v.sh}}
.r{position:absolute;left:40px;top:30px;font:38px Plex;color:${v.rec};display:flex;align-items:center;gap:14px;text-shadow:0 2px 10px #000}
.r i{width:26px;height:26px;border-radius:50%;background:#ff2a2a;display:block}
.b{position:absolute;right:52px;top:430px;display:flex;align-items:center;gap:16px}
.b .av{width:58px;height:58px;border-radius:50%;border:6px solid ${v.bt};box-sizing:border-box;display:flex;align-items:center;justify-content:center}
.b .av i{width:16px;height:16px;border-radius:50%;background:${v.dot || '#ff2a2a'};display:block}
.b .m{background:${v.bub};color:${v.bt};font:600 48px I;padding:18px 30px;border-radius:34px;box-shadow:0 6px 24px #0008}
</style></head><body>
<div class="t" style="top:58px;color:${v.t1}">DON'T</div>
<div class="t" style="top:205px;color:${v.t2}">REPLY</div>
<div class="b"><div class="av"><i></i></div><div class="m">Are you awake?</div></div>
${v.rec ? '<div class="r"><i></i>REC 03:00:41</div>' : ''}
</body></html>`);
  await p.goto('file://' + here + '/_th.html', { waitUntil: 'load' });
  await p.evaluate(() => Promise.all([document.fonts.load('900 100px M'), document.fonts.load('30px Plex'), document.fonts.load('600 30px I')]));
  await p.screenshot({ path: `${out}/${n}.jpg`, type: 'jpeg', quality: 92 });
}
await b.close();
