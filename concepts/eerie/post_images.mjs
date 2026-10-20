import { chromium } from 'playwright';
import fs from 'fs';
const C = process.cwd(), PO = '/tmp/claude-0/-home-user-YTP1/db7b424d-ffe5-5abf-bc8b-b81061ddb974/scratchpad/eerie/ep01/post', OUT = '/tmp/claude-0/-home-user-YTP1/db7b424d-ffe5-5abf-bc8b-b81061ddb974/scratchpad/posts';
// [name, frame, crop centre x, centre y, crop size, html overlay]
const items = [
  ['p1_opt1_open', 't0052.95.jpg', 1000, 560, 1000, ''],
  ['p1_opt2_keyhole', 't0083.00.jpg', 980, 520, 900, ''],
  ['p1_opt3_asleep', 't0120.50.jpg', 560, 540, 1080, ''],
  ['p1_opt4_bark', 't0203.00.jpg', 640, 560, 1060, ''],
  ['p2_rule4', 't0019.50.jpg', 950, 600, 1200, '<div class="band">READ RULE 4<br><span>BEFORE 3 AM</span></div>'],
];
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
for (const [n, f, cx, cy, sz, ov] of items) {
  const s = 1080 / sz;
  fs.writeFileSync(C + '/_post.html', `<html><head><style>@font-face{font-family:M;font-weight:900;src:url(fonts/montserrat-900.woff2)}
body{margin:0;width:1080px;height:1080px;overflow:hidden;background:#000 url(file://${PO}/${f}) no-repeat;background-size:${1920*s}px ${1080*s}px;background-position:${540-cx*s}px ${540-cy*s}px;position:relative}
body:after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.7) 100%)}
.band{position:absolute;left:0;right:0;bottom:0;padding:34px 0 40px;background:#ff1f2e;color:#fff;text-align:center;font:900 92px/1 M;letter-spacing:-2px;z-index:2}
.band span{color:#000;font-size:70px}</style></head><body>${ov}</body></html>`);
  await p.goto('file://' + C + '/_post.html'); await p.evaluate(() => document.fonts.load('900 100px M'));
  await p.screenshot({ path: `${OUT}/${n}.jpg`, type: 'jpeg', quality: 93 });
}
await b.close();
