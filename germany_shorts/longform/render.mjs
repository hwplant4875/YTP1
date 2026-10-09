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

const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
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
const ctx = await S.setup(THREE, renderer, ${W}, ${H});
window.frameAt = async (t) => { S.update(ctx, t);
  if (ctx.finish) ctx.finish.uniforms.time.value = t;
  if (ctx.composer) ctx.composer.render(); else renderer.render(ctx.scene, ctx.camera);
  return renderer.domElement.toDataURL('image/jpeg', 0.93); };
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
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
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
