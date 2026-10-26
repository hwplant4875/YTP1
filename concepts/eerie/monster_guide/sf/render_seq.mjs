// node render_seq.mjs <a.js,b.js,...> <out.mp4> <seconds> [fps=30] [W=1920] [H=1080]
// Motion-test companion to render_sf.mjs: same page setup, but calls window.draw(t) once per frame
// (t = frame / fps) and encodes the frames to an H.264 mp4 with ffmpeg. Silent; for checking motion, not final renders.
import { chromium } from 'playwright';
import { writeFileSync, readFileSync, mkdirSync, mkdtempSync, rmSync, unlinkSync } from 'fs';
import { execFileSync } from 'child_process';
import os from 'os';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const [list, out, secs, fps = '30', W = '1920', H = '1080'] = process.argv.slice(2);
if (!list || !out || !secs) { console.error('usage: node render_seq.mjs <a.js,b.js> <out.mp4> <seconds> [fps] [W] [H]'); process.exit(1); }
const fonts = path.join(here, '..', 'fonts');
const ff = (fam, file, w = 'normal') => `@font-face{font-family:'${fam}';font-weight:${w};src:url(file://${path.join(fonts, file)})}`;
const css = [
  ff('Nunito', 'Nunito.ttf', '200 1000'), ff('Fredoka', 'Fredoka.ttf', '300 700'), ff('Anton', 'Anton.ttf'),
  ff('BlackOps', 'BlackOpsOne.ttf'), ff('Courier', 'CourierPrime.ttf', '400'), ff('Courier', 'CourierPrime-Bold.ttf', '700'),
].join('\n');
const scripts = list.split(',').map(f => `<script>${readFileSync(path.resolve(f), 'utf8')}\n</script>`).join('\n');
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head>
<body style="margin:0;background:#000"><canvas id="c" width="${W}" height="${H}"></canvas>${scripts}</body></html>`;
const tmp = path.join(here, `_page_seq_${process.pid}.html`);
writeFileSync(tmp, html);
const frames = mkdtempSync(path.join(os.tmpdir(), 'sfseq-'));
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +W, height: +H } });
const errs = [];
p.on('pageerror', e => errs.push(e.message));
p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('file://' + tmp);
await p.evaluate(async () => {
  for (const f of ['800 20px Nunito', '600 20px Fredoka', '20px Anton', '20px BlackOps', '20px Courier', '700 20px Courier']) await document.fonts.load(f);
  await document.fonts.ready;
});
const n = Math.round(+secs * +fps);
for (let i = 0; i < n; i++) {
  const d = await p.evaluate(async tt => { await window.draw(tt); return document.getElementById('c').toDataURL('image/png'); }, i / +fps);
  writeFileSync(path.join(frames, `f${String(i).padStart(5, '0')}.png`), Buffer.from(d.split(',')[1], 'base64'));
  if (errs.length) break;
}
await b.close();
unlinkSync(tmp);
if (errs.length) { rmSync(frames, { recursive: true, force: true }); console.error('PAGE ERRORS:\n' + errs.join('\n')); process.exit(2); }
mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', fps, '-i', path.join(frames, 'f%05d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', out]);
rmSync(frames, { recursive: true, force: true });
console.log('wrote', out, `(${n} frames @ ${fps} fps)`);
