// Render style-draft scenes with headless Chromium.
// node run.mjs still A out.jpg [t]   |   node run.mjs clip out.mp4 "A:0-4,B:0-4,C:0-4" [fps]
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, rmSync } from 'fs';
import { execSync } from 'child_process';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const [mode, a1, a2, a3] = process.argv.slice(2);
const W = +(process.env.RW || 1080), H = +(process.env.RH || 1920);
const html = `<!doctype html><html><head><style>
@font-face{font-family:PatrickHand;src:url(fonts/patrick-hand.woff2)}
@font-face{font-family:Caveat;font-weight:700;src:url(fonts/caveat700.woff2)}
@font-face{font-family:Caveat;src:url(fonts/caveat700.woff2)}
@font-face{font-family:PMarker;src:url(fonts/permanent-marker.woff2)}
@font-face{font-family:Gaegu;src:url(fonts/gaegu.woff2)}
body{margin:0;background:#000}</style></head><body>
<canvas id="c" width="${W}" height="${H}"></canvas>
<script src="ink.js"></script><script src="scenes.js"></script><script src="scenes2.js"></script><script src="scenes3.js"></script><script src="stick.js"></script></body></html>`;
writeFileSync(path.join(dir, 'page.html'), html);

const browser = await chromium.launch();
const errs = [];
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => console.error('PAGEERR', e.message));
await page.goto('file://' + path.join(dir, 'page.html'));
await page.evaluate(async () => {
  await document.fonts.load('80px PatrickHand'); await document.fonts.load('700 80px Caveat'); await document.fonts.load('80px PMarker'); await document.fonts.load('80px Gaegu'); await document.fonts.load('80px Caveat');
});
const grab = async (name, t, q = 0.92) => {
  const url = await page.evaluate(([n, tt, qq]) => { window.draw(n, tt); return document.getElementById('c').toDataURL('image/jpeg', qq); }, [name, t, q]);
  return Buffer.from(url.split(',')[1], 'base64');
};

if (mode === 'still') {
  writeFileSync(a2, await grab(a1, parseFloat(a3 || '0.6'), 0.93));
} else {
  const fps = parseInt(a3 || '30');
  const tmp = path.join(dir, 'frames'); rmSync(tmp, { recursive: true, force: true }); mkdirSync(tmp);
  let n = 0;
  for (const part of a2.split(',')) {
    const [name, rng] = part.split(':'); const [t0, t1] = rng.split('-').map(Number);
    for (let f = 0; f < Math.round((t1 - t0) * fps); f++) {
      writeFileSync(path.join(tmp, `f${String(n++).padStart(5, '0')}.jpg`), await grab(name, t0 + f / fps));
    }
  }
  execSync(`ffmpeg -y -loglevel error -framerate ${fps} -i ${tmp}/f%05d.jpg -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart ${a1}`);
  rmSync(tmp, { recursive: true, force: true });
}
await browser.close();
