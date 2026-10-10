// Render a Three.js scene module frame by frame in headless Chromium and pipe to ffmpeg.
// usage: node render.mjs scenes/x.js out.mp4 --dur 6 --fps 30 [--w 1920 --h 1080] [--still 2.5 out.png]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import http from 'http';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const [sceneFile, out] = args;
const W = +opt('w', 1920), H = +opt('h', 1080), FPS = +opt('fps', 30), DUR = +opt('dur', 5);
const still = opt('still', null);
const SHOT = opt('shot', ''), T0 = +opt('t0', 0);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname));

const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.otf': 'font/otf', '.ttf': 'font/ttf', '.bin': 'application/octet-stream', '.f16': 'application/octet-stream' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const html = `<!doctype html><html><body style="margin:0;background:#000">
<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js","three/addons/":"/node_modules/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import * as S from '/${sceneFile}';
const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
renderer.setSize(${W}, ${H}); renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);
for (const [fam, file] of [['YTSans','/fonts/YouTubeSans-Black.otf'],['Pret','/fonts/Pretendard-Bold.otf'],['TikTok','/fonts/TikTokSans-Black.ttf']]) {
  const f = new FontFace(fam, 'url(' + file + ')'); await f.load(); document.fonts.add(f); }
const ctx = await S.setup(THREE, renderer, ${W}, ${H});
const ov = document.createElement('canvas'); ov.width = ${W}; ov.height = ${H}; const g2 = ov.getContext('2d');
window.frameAt = async (t) => { S.update(ctx, t);
  if (ctx.finish) ctx.finish.uniforms.time.value = t;
  if (ctx.composer) ctx.composer.render(); else renderer.render(ctx.scene, ctx.camera);
  if (S.post) S.post(ctx, renderer, t);
  if (!S.overlay) return renderer.domElement.toDataURL('image/jpeg', 0.93);
  g2.setTransform(1,0,0,1,0,0); g2.drawImage(renderer.domElement, 0, 0); S.overlay(ctx, g2, t);
  return ov.toDataURL('image/jpeg', 0.94); };
window.ready = true;
</script></body></html>`;
const pageName = `_page_${process.pid}.html`;
fs.writeFileSync(path.join(root, pageName), html);

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => { console.error('[pageerror]', e); process.exit(1); });
await page.goto(`http://localhost:${port}/${pageName}?shot=${encodeURIComponent(SHOT)}`);
await page.waitForFunction('window.ready === true', null, { timeout: 120000 });

const grab = async t => Buffer.from((await page.evaluate(t => window.frameAt(t), t + T0)).split(',')[1], 'base64');
if (still) {
  fs.writeFileSync(out, await grab(+still));
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(DUR * FPS), t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const buf = await grab(i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 30 === 0) process.stderr.write(`\r${i}/${n} ${((Date.now() - t0) / (i + 1)).toFixed(0)}ms/f`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  process.stderr.write('\n');
}
await browser.close(); server.close(); fs.unlinkSync(path.join(root, pageName));
console.log(out);
