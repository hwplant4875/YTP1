// usage: node video.mjs <page.html rel> out.mp4 [fps=30] [t0] [t1] [WxH]
import { openPage } from './browser.mjs';
import { spawn } from 'child_process';
const [rel, out, fpsS, t0S, t1S, size] = process.argv.slice(2);
const fps = Number(fpsS || 30); const [W, H] = (size || '1080x1920').split('x').map(Number);
const [relPath, qs] = rel.split('?');
const P = await openPage(relPath, W, H, qs || '');
const DUR = await P.page.evaluate(() => window.DUR);
const t0 = Number(t0S || 0), t1 = Number(t1S || DUR);
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
const n0 = Math.round(t0 * fps), n1 = Math.round(t1 * fps); const T = Date.now();
for (let i = n0; i < n1; i++) {
  await P.page.evaluate(async t => { await window.render(t); }, i / fps);
  const buf = await P.page.screenshot({ type: 'jpeg', quality: 95, timeout: 600000 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if ((i - n0) % 60 === 0) console.log(`frame ${i}/${n1} ${((Date.now() - T) / Math.max(1, i - n0 + 1)).toFixed(0)}ms/f`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
if (P.errs.length) console.error(P.errs.join('\n'));
await P.close(); console.log('done', out);
