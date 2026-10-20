// Render EP02 frames with headless Chromium.
// node render.mjs timeline.json still out.jpg t
// node render.mjs timeline.json clip out.mp4 t0 t1 [workers]
// node render.mjs timeline.json stills outdir t1,t2,...   (contact sheet frames named by time)
import { chromium } from 'playwright';
import { writeFileSync, readFileSync, rmSync, mkdirSync } from 'fs';
import { execSync, spawn } from 'child_process';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const [tlPath, mode, out, a, b, wk] = process.argv.slice(2);
const FPS = parseInt(process.env.FPS || '30');
const tl = readFileSync(tlPath, 'utf8');
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:M;font-weight:900;src:url(../fonts/montserrat-900.woff2)}
@font-face{font-family:Plex;src:url(../../mindset/fonts/ibm-plex-mono-600.woff2)}
@font-face{font-family:I;font-weight:400;src:url(../../mindset/fonts/inter-400.woff2)}
@font-face{font-family:I;font-weight:500 600;src:url(../../mindset/fonts/inter-600.woff2)}
body{margin:0;background:#000}</style></head><body><canvas id="c" width="1920" height="1080"></canvas>
<script>window.TL=${tl};</script><script src="engine.js"></script></body></html>`;
const page_ = path.join(dir, '_page.html'); writeFileSync(page_, html);

async function openPage(browser) {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + page_);
  await p.evaluate(async () => { for (const f of ['900 50px M', '30px Plex', '600 30px Plex', '400 20px I', '600 20px I', '500 20px I']) await document.fonts.load(f); });
  return p;
}
const grab = async (p, t) => Buffer.from((await p.evaluate(tt => { window.draw(tt); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, t)).split(',')[1], 'base64');

const browser = await chromium.launch();
if (mode === 'still') {
  const p = await openPage(browser); writeFileSync(out, await grab(p, parseFloat(a)));
} else if (mode === 'stills') {
  const p = await openPage(browser); mkdirSync(out, { recursive: true });
  for (const v of a.split(',')) writeFileSync(path.join(out, `t${parseFloat(v).toFixed(2).padStart(7, '0')}.jpg`), await grab(p, parseFloat(v)));
} else {
  const t0 = parseFloat(a), t1 = parseFloat(b), n = Math.round((t1 - t0) * FPS), workers = parseInt(wk || '4');
  const per = Math.ceil(n / workers), tmp = out + '_parts'; rmSync(tmp, { recursive: true, force: true }); mkdirSync(tmp);
  await Promise.all([...Array(workers).keys()].map(async w => {
    const p = await openPage(browser), f0 = w * per, f1 = Math.min(n, f0 + per);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(tmp, `p${w}.mp4`)]);
    for (let f = f0; f < f1; f++) { const buf = await grab(p, t0 + f / FPS); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  writeFileSync(path.join(tmp, 'list.txt'), [...Array(workers).keys()].map(w => `file 'p${w}.mp4'`).join('\n'));
  execSync(`ffmpeg -y -loglevel error -f concat -safe 0 -i ${tmp}/list.txt -c copy ${out}`);
  rmSync(tmp, { recursive: true, force: true });
}
await browser.close(); rmSync(page_, { force: true });
console.log('done', out);
