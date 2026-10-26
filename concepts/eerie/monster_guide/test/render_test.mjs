// node render_test.mjs out_dir fps seconds  -> PNG frames of mimic_test.js (then ffmpeg them)
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname), [out, fps = 30, secs = 6] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
writeFileSync(path.join(dir, '_page.html'), `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:I;font-weight:400;src:url(../../../mindset/fonts/inter-400.woff2)}
@font-face{font-family:I;font-weight:500 700;src:url(../../../mindset/fonts/inter-600.woff2)}
@font-face{font-family:S;src:url(../../../mindset/fonts/instrument-serif-400.woff2)}
</style></head><body style="margin:0"><canvas id="c" width="1920" height="1080"></canvas><script src="mimic_test.js"></script></body></html>`);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.error('PAGEERR', e.message));
await p.goto('file://' + path.join(dir, '_page.html'));
await p.evaluate(async () => { for (const f of ['400 20px I', '600 20px I', '20px S']) await document.fonts.load(f); });
for (let i = 0; i < fps * secs; i++) {
  const d = await p.evaluate(t => { window.draw(t); return document.getElementById('c').toDataURL('image/png'); }, i / fps);
  writeFileSync(path.join(out, `f${String(i).padStart(4, '0')}.png`), Buffer.from(d.split(',')[1], 'base64'));
}
await b.close();
