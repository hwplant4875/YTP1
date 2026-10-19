import { chromium } from 'playwright';
import { spawn } from 'child_process';
const [mod, fps, s0, s1, out] = process.argv.slice(2);
const m = await import('./' + mod);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: m.W, height: m.H } });
await p.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', fps, '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', fps, out]);
for (let i = Math.round(s0 * fps); i < Math.round(s1 * fps); i++) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.frame(i / fps)); ff.stdin.write(await p.screenshot({ type: 'png' })); }
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('done', out);
