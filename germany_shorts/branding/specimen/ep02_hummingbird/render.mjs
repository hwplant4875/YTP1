import { chromium } from 'playwright';
import { spawn } from 'child_process';
const [mod, fps, s0, s1, out] = process.argv.slice(2);
const m = await import('./' + mod);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: m.W, height: m.H } });
await p.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', fps, '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', fps, out]);
let pg = p;
const shot = async (i) => { for (let k = 0; k < 4; k++) { try { await pg.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.frame(i / fps)); return await pg.screenshot({ type: 'png' }); }
  catch (e) { console.log('retry', i, k, String(e).slice(0, 80)); try { await pg.close(); } catch {} pg = await b.newPage({ viewport: { width: m.W, height: m.H } }); await pg.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style><div id="c"></div>`); } } throw new Error('frame failed ' + i); };
for (let i = Math.round(s0 * fps); i < Math.round(s1 * fps); i++) { const buf = await shot(i); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('done', out);
