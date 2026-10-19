// YouTube-style feed mockup to compare thumbnails with the title.
// node feed.mjs thumbsdir out.jpg A B ...
import { chromium } from 'playwright';
import { writeFileSync, rmSync } from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname);
const [tdir, out, ...keys] = process.argv.slice(2);
const TITLE = 'If Your Cat Ever Knocks On Your Bedroom Door… DO NOT OPEN IT';
const card = (k, w) => `<div class="card" style="width:${w}px">
  <div class="th"><img src="file://${path.join(tdir, `thumb_${k}.jpg`)}"><span class="dur">5:08</span></div>
  <div class="meta"><div class="av"><span></span></div><div>
    <div class="ti" style="font-size:${w > 400 ? 18 : 14}px">${TITLE}</div>
    <div class="sub">Channel Name</div><div class="sub">조회수 0회 · 방금 전</div></div></div>
  <div class="tag">${k}</div></div>`;
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:R;font-weight:400;src:url(fonts/roboto-400.woff2)}
@font-face{font-family:R;font-weight:500;src:url(fonts/roboto-500.woff2)}
body{margin:0;background:#0f0f0f;font-family:R;color:#f1f1f1;padding:36px 40px}
.row{display:flex;gap:28px;align-items:flex-start}
.card{position:relative}.th{position:relative}.th img{width:100%;display:block;border-radius:12px}
.dur{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.8);font-size:12px;font-weight:500;padding:2px 5px;border-radius:4px}
.meta{display:flex;gap:12px;margin-top:12px}.av{flex:0 0 36px;height:36px;border-radius:50%;background:#000;border:1px solid #333;display:flex;align-items:center;justify-content:center}
.av span{width:14px;height:10px;border-radius:50%;background:#ffd23a;box-shadow:0 0 8px #ffd23a}
.ti{font-weight:500;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:4px}
.sub{color:#aaa;font-size:14px;line-height:1.45}
.tag{position:absolute;left:-10px;top:-10px;background:#3ea6ff;color:#000;font-weight:500;font-size:16px;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center}
h3{font-weight:500;color:#aaa;font-size:15px;margin:34px 0 14px}
</style></head><body>
<div class="row">${keys.map(k => card(k, 600)).join('')}</div>
<h3>휴대폰 피드 크기</h3>
<div class="row">${keys.map(k => card(k, 300)).join('')}</div>
</body></html>`;
const f = path.join(dir, '_feed.html'); writeFileSync(f, html);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 80 + keys.length * 628, height: 900 } });
await p.goto('file://' + f); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
await p.screenshot({ path: out, type: 'jpeg', quality: 92, fullPage: true }); await b.close(); rmSync(f);
