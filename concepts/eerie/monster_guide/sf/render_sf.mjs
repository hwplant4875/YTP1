// node render_sf.mjs <a.js,b.js,...> <out.png> [t=0] [W=1920] [H=1080]
// Loads the scripts in order into a page with a W×H canvas#c, calls window.draw(t), saves a PNG.
// The scripts get the canvas as document.getElementById('c'); window.draw(t) must paint the whole frame.
// Fonts: concepts/eerie/monster_guide/fonts/ (git-ignored by repo convention; a copy lives in /mnt/project-files/eerie_rules/monster_guide/fonts/).
// SMALL=1 also writes <out>_168.png (168 px wide, YouTube small-thumb size) and <out>_gray.png (greyscale).
import { chromium } from 'playwright';
import { writeFileSync, readFileSync, mkdirSync, unlinkSync } from 'fs';
import { execFileSync } from 'child_process';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const [list, out, t = '0', W = '1920', H = '1080'] = process.argv.slice(2);
if (!list || !out) { console.error('usage: node render_sf.mjs <a.js,b.js> <out.png> [t] [W] [H]'); process.exit(1); }
const fonts = path.join(here, '..', 'fonts');
const ff = (fam, file, w = 'normal') => `@font-face{font-family:'${fam}';font-weight:${w};src:url(file://${path.join(fonts, file)})}`;
const css = [
  ff('Nunito', 'Nunito.ttf', '200 1000'), ff('Fredoka', 'Fredoka.ttf', '300 700'), ff('Anton', 'Anton.ttf'),
  ff('BlackOps', 'BlackOpsOne.ttf'), ff('Courier', 'CourierPrime.ttf', '400'), ff('Courier', 'CourierPrime-Bold.ttf', '700'),
].join('\n');
const scripts = list.split(',').map(f => `<script>${readFileSync(path.resolve(f), 'utf8')}\n</script>`).join('\n');
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head>
<body style="margin:0;background:#000"><canvas id="c" width="${W}" height="${H}"></canvas>${scripts}</body></html>`;
const tmp = path.join(here, `_page_sf_${process.pid}.html`);
writeFileSync(tmp, html);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +W, height: +H } });
const errs = [];
p.on('pageerror', e => errs.push(e.message));
p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('file://' + tmp);
await p.evaluate(async () => {
  for (const f of ['800 20px Nunito', '600 20px Fredoka', '20px Anton', '20px BlackOps', '20px Courier', '700 20px Courier']) await document.fonts.load(f);
  await document.fonts.ready;
});
const d = await p.evaluate(async tt => { await window.draw(tt); return document.getElementById('c').toDataURL('image/png'); }, +t);
await b.close();
unlinkSync(tmp);
if (errs.length) { console.error('PAGE ERRORS:\n' + errs.join('\n')); }
mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
writeFileSync(out, Buffer.from(d.split(',')[1], 'base64'));
if (process.env.SMALL) {
  const base = out.replace(/\.png$/, '');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=168:-1:flags=area', base + '_168.png']);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', out, '-vf', 'format=gray', base + '_gray.png']);
}
console.log('wrote', out, errs.length ? `(${errs.length} page errors)` : '');
if (errs.length) process.exit(2);
