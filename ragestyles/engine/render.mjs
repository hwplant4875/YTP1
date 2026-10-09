// RageStyles render engine: draws a 2D canvas timeline (spec module) frame by frame in
// headless Chromium and pipes JPEG frames to ffmpeg.
// usage: node render.mjs <spec.js relative to repo ragestyles/> <out.mp4> [--from 0 --to 30 --fps 30 --still 3.2]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import http from 'http';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const [specFile, out] = args;
const FPS = +opt('fps', 30), still = opt('still', null);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');   // ragestyles/
const W = 1080, H = 1920;

const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.css': 'text/css' };
const server = http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]);
  let p = u.startsWith('/@work/') ? path.join(process.env.RS_WORK || '/home/user/rs_work', u.slice(7)) : path.join(root, u);
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const fontDir = '/engine/node_modules/@fontsource';
const fonts = [['Anton', 'anton/files/anton-latin-400-normal.woff2', 400], ['Bebas', 'bebas-neue/files/bebas-neue-latin-400-normal.woff2', 400],
  ['Mont', 'montserrat/files/montserrat-latin-900-normal.woff2', 900], ['Mont', 'montserrat/files/montserrat-latin-800-normal.woff2', 800],
  ['Mont', 'montserrat/files/montserrat-latin-600-normal.woff2', 600], ['MontI', 'montserrat/files/montserrat-latin-900-italic.woff2', 900],
  ['Oswald', 'oswald/files/oswald-latin-700-normal.woff2', 700], ['Archivo', 'archivo-black/files/archivo-black-latin-400-normal.woff2', 400]];
const css = fonts.map(([f, file, w]) => `@font-face{font-family:'${f}';src:url(${fontDir}/${file});font-weight:${w}}`).join('\n');

const html = `<!doctype html><html><head><style>${css} body{margin:0;background:#000}</style></head><body>
<canvas id=c width=${W} height=${H}></canvas>
<script type="importmap">{"imports":{"three":"/engine/node_modules/three/build/three.module.js","three/addons/":"/engine/node_modules/three/examples/jsm/"}}</script>
<script type="module">
import * as S from '/${specFile}';
import { makeCtx } from '/engine/fx.js';
await Promise.all(${JSON.stringify(fonts.map(f => [f[0], f[2]]))}.map(([f, w]) => document.fonts.load(w + ' 80px ' + f)));
const cv = document.getElementById('c');
const R = makeCtx(cv);
await S.setup(R);
window.DUR = S.duration;
window.CUES = S.cues ? S.cues() : null;
window.frameAt = async t => { await R.begin(t); await S.draw(R, t); R.end(t); return cv.toDataURL('image/jpeg', 0.95); };
window.ready = true;
</script></body></html>`;
const pageName = `_page_${process.pid}.html`;
fs.writeFileSync(path.join(root, pageName), html);

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => { console.error('[pageerror]', e); process.exit(1); });
await page.goto(`http://localhost:${port}/${pageName}`);
await page.waitForFunction('window.ready === true', null, { timeout: 180000 });
const DUR = await page.evaluate('window.DUR');
const CUES = await page.evaluate('window.CUES');
if (CUES && !still) fs.writeFileSync(out.replace(/\.mp4$/, '.cues.json'), JSON.stringify({ duration: DUR, tracks: CUES }, null, 1));
const from = +opt('from', 0), to = +opt('to', DUR);

const grab = async t => Buffer.from((await page.evaluate(t => window.frameAt(t), t)).split(',')[1], 'base64');
try {
  if (still) {
    for (const [i, s] of still.split(',').entries()) {
      const o = still.includes(',') ? out.replace(/(\.\w+)$/, `_${i}$1`) : out;
      fs.writeFileSync(o, await grab(+s)); console.log(o);
    }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round((to - from) * FPS), t0 = Date.now();
    for (let i = 0; i < n; i++) {
      const buf = await grab(from + i / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 30 === 0) process.stderr.write(`\r${i}/${n} ${((Date.now() - t0) / (i + 1)).toFixed(0)}ms/f`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    process.stderr.write('\n'); console.log(out);
  }
} finally {
  await browser.close(); server.close(); fs.unlinkSync(path.join(root, pageName));
}
