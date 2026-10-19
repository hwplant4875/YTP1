import { chromium } from 'playwright';
import { spawn } from 'child_process';
import { FONTS } from './eng.mjs';
import { frameSVG } from './timeline.mjs';
// usage: node render.mjs fps startSec endSec out.mp4   |  node render.mjs still t1,t2,... prefix
const [a0, a1, a2, a3] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
const show = async T => { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, frameSVG(T)); };
if (a0 === 'still') {
  for (const T of a1.split(',').map(Number)) { await show(T); await p.waitForTimeout(60); await p.screenshot({ path: `${a2}_${T}.png` }); }
} else {
  const fps = Number(a0), s0 = Number(a1), s1 = Number(a2);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), a3]);
  const n0 = Math.round(s0 * fps), n1 = Math.round(s1 * fps);
  for (let i = n0; i < n1; i++) { await show(i / fps); ff.stdin.write(await p.screenshot({ type: 'png' })); if (i % 150 === 0) console.log(a3, i); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await b.close();
