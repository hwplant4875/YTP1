// Transparent overlay (lie counter, lie cards, subtitles, intro/outro) rendered in headless Chromium as PNG frames.
// usage: node overlay.mjs out.mov [--still t out.png] [--from t0 --to t1]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import http from 'http';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const W = 1920, H = 1080, FPS = 30;
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200); fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const page_js = `
const E = await (await fetch('/counted/edl.json')).json();
for (const [fam, file] of [['YTSans','/fonts/YouTubeSans-Black.otf'],['Pret','/fonts/Pretendard-Bold.otf']]) {
  const f = new FontFace(fam, 'url(' + file + ')'); await f.load(); document.fonts.add(f); }
const c = document.createElement('canvas'); c.width = ${W}; c.height = ${H}; const g = c.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eo = t => 1 - Math.pow(1 - t, 3);
const eob = t => { const k = 1.8; return 1 + (k + 1) * Math.pow(t - 1, 3) + k * Math.pow(t - 1, 2); };
const RED = '#ff3b3b', GREEN = '#3ddc84';
function rr(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function wrap(text, maxW) { const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines; }
const MAIN_END = E.end, TOTAL = E.end + E.outro;
window.draw = (t) => {
  g.clearRect(0, 0, ${W}, ${H});
  const nLies = E.lies.filter(l => l.at <= t).length;
  // ---- intro ----
  if (t < E.intro + 0.6) {
    const a = 1 - clamp((t - E.intro) / 0.6);
    g.fillStyle = 'rgba(0,0,0,' + (0.82 * a) + ')'; g.fillRect(0, 0, ${W}, ${H});
    g.textAlign = 'center'; g.globalAlpha = a * eo(clamp(t / 0.5));
    g.font = '40px YTSans'; g.fillStyle = RED; g.letterSpacing = '10px'; g.fillText('BREAKING BAD', 960, 400); g.letterSpacing = '0px';
    g.font = '104px YTSans'; g.fillStyle = '#fff'; g.fillText('Every lie Walter White tells.', 960, 530);
    const a2 = eob(clamp((t - 1.0) / 0.45));
    g.save(); g.translate(960, 660); g.scale(a2, a2); g.font = '104px YTSans'; g.fillStyle = RED; g.fillText('Counted.', 0, 0); g.restore();
    g.globalAlpha = 1;
  }
  // ---- lie counter (top left) ----
  const cA = eo(clamp((t - E.intro + 0.2) / 0.5)) * (1 - clamp((t - MAIN_END) / 0.4));
  if (cA > 0) {
    g.save(); g.globalAlpha = cA;
    const last = E.lies.filter(l => l.at <= t).pop(), pa = last ? t - last.at : 9;
    const punch = pa < 0.5 ? 1 + 0.25 * Math.sin(clamp(pa / 0.5) * Math.PI) : 1;
    g.fillStyle = 'rgba(10,10,12,0.78)'; rr(48, 44, 300, 128, 22); g.fill();
    g.font = '24px Pret'; g.fillStyle = 'rgba(255,255,255,0.7)'; g.textAlign = 'left'; g.letterSpacing = '4px';
    g.fillText('WALTER WHITE', 76, 92); g.letterSpacing = '0px';
    g.font = '30px YTSans'; g.fillStyle = '#fff'; g.fillText('LIES', 76, 146);
    g.save(); g.translate(258, 130); g.scale(punch, punch);
    g.fillStyle = pa < 0.6 ? RED : '#fff'; g.font = '84px YTSans'; g.textAlign = 'center'; g.fillText(String(nLies).padStart(2, '0'), 0, 30); g.restore();
    if (pa < 0.35) { g.strokeStyle = 'rgba(255,59,59,' + (1 - pa / 0.35) + ')'; g.lineWidth = 6; rr(48, 44, 300, 128, 22); g.stroke(); }
    g.restore();
  }
  // ---- episode tag (top right) at each scene start ----
  for (const s of E.segs) {
    if (!s.scene) continue; const a = t - s.at; if (a < 0 || a > 4.2) continue;
    const al = eo(clamp(a / 0.4)) * (1 - clamp((a - 3.7) / 0.5));
    g.save(); g.globalAlpha = al; g.translate((1 - eo(clamp(a / 0.4))) * 60, 0);
    g.font = '30px YTSans'; const w1 = g.measureText(s.ep[0]).width; g.font = '30px Pret'; const w2 = g.measureText(s.ep[1]).width;
    const w = w1 + w2 + 84, x = ${W} - 48 - w;
    g.fillStyle = 'rgba(10,10,12,0.78)'; rr(x, 52, w, 64, 32); g.fill();
    g.fillStyle = RED; g.font = '30px YTSans'; g.textAlign = 'left'; g.fillText(s.ep[0], x + 30, 95);
    g.fillStyle = '#fff'; g.font = '30px Pret'; g.fillText(s.ep[1], x + 54 + w1, 95);
    g.restore();
  }
  // ---- subtitles ----
  const lieNow = E.lies.find(l => t >= l.at - 0.05 && t <= l.at + 3.0);
  for (const s of E.subs) {
    if (t < s.a || t > s.b + 0.05) continue;
    const isLie = E.lies.some(l => l.at >= s.a - 0.3 && l.at <= s.b);
    g.font = '50px Pret'; g.textAlign = 'center';
    const lines = wrap(s.t, 1400), lh = 64, y0 = ${H} - 70 - (lines.length - 1) * lh;
    lines.forEach((ln, i) => {
      const w = g.measureText(ln).width;
      g.fillStyle = 'rgba(0,0,0,0.55)'; rr(960 - w / 2 - 18, y0 + i * lh - 48, w + 36, 62, 10); g.fill();
      g.fillStyle = isLie && t >= (E.lies.find(l => l.at >= s.a - 0.3 && l.at <= s.b).at) ? '#ffd2d2' : '#fff';
      g.fillText(ln, 960, y0 + i * lh);
    });
  }
  // ---- lie card (right) + stamp ----
  for (const l of E.lies) {
    const a = t - l.at; if (a < 0 || a > 4.6) continue;
    const inA = eo(clamp(a / 0.35)), outA = 1 - clamp((a - 4.1) / 0.5);
    // red flash on the frame edge
    if (a < 0.4) { const k = 1 - a / 0.4; const gr = g.createRadialGradient(960, 540, 400, 960, 540, 1150);
      gr.addColorStop(0, 'rgba(255,0,0,0)'); gr.addColorStop(1, 'rgba(255,30,30,' + (0.35 * k) + ')'); g.fillStyle = gr; g.fillRect(0, 0, ${W}, ${H}); }
    const x = ${W} - 48 - 560, y = 160;
    g.font = '36px YTSans'; const qn = wrap('"' + l.q + '"', 480).length; g.font = '30px Pret'; const tn = wrap(l.truth, 480).length;
    const ch = 148 + qn * 44 + 22 + 42 + (tn - 1) * 38 + 34;
    g.save(); g.globalAlpha = outA; g.translate((1 - inA) * 120, 0);
    g.fillStyle = 'rgba(12,12,14,0.86)'; rr(x, y, 560, ch, 26); g.fill();
    g.fillStyle = RED; rr(x, y, 10, ch, 5); g.fill();
    // stamp
    const sA = eob(clamp(a / 0.3));
    g.save(); g.translate(x + 150, y + 62); g.rotate(-0.06); g.scale(sA * 1, sA * 1);
    g.strokeStyle = RED; g.lineWidth = 5; rr(-110, -36, 220, 72, 10); g.stroke();
    g.fillStyle = RED; g.font = '46px YTSans'; g.textAlign = 'center'; g.fillText('LIE #' + l.n, 0, 17); g.restore();
    g.textAlign = 'left'; g.font = '24px Pret'; g.fillStyle = 'rgba(255,255,255,0.6)'; g.letterSpacing = '3px';
    g.fillText('TOLD TO ' + l.to.toUpperCase(), x + 290, y + 72); g.letterSpacing = '0px';
    g.font = '36px YTSans'; g.fillStyle = '#fff';
    const ql = wrap('"' + l.q + '"', 480); ql.forEach((ln, i) => g.fillText(ln, x + 40, y + 148 + i * 44));
    const ty = y + 148 + ql.length * 44 + 22;
    const tA = clamp((a - 0.9) / 0.4);
    g.globalAlpha = outA * tA;
    g.font = '22px Pret'; g.fillStyle = GREEN; g.letterSpacing = '3px'; g.fillText('THE TRUTH', x + 40, ty); g.letterSpacing = '0px';
    g.font = '30px Pret'; g.fillStyle = 'rgba(255,255,255,0.92)';
    wrap(l.truth, 480).forEach((ln, i) => g.fillText(ln, x + 40, ty + 42 + i * 38));
    g.restore();
  }
  // ---- outro tally ----
  if (t > MAIN_END - 0.3) {
    const a = eo(clamp((t - MAIN_END + 0.3) / 0.6));
    g.fillStyle = 'rgba(0,0,0,' + (0.85 * a) + ')'; g.fillRect(0, 0, ${W}, ${H});
    g.globalAlpha = a; g.textAlign = 'center';
    g.font = '40px YTSans'; g.fillStyle = 'rgba(255,255,255,0.7)'; g.letterSpacing = '8px'; g.fillText('IN JUST 5 SCENES', 960, 300); g.letterSpacing = '0px';
    const n = Math.round(E.lies.length * eo(clamp((t - MAIN_END) / 1.0)));
    g.font = '220px YTSans'; g.fillStyle = RED; g.fillText(String(n), 960, 520);
    g.font = '72px YTSans'; g.fillStyle = '#fff'; g.fillText('LIES', 960, 610);
    const by = {}; E.lies.forEach(l => by[l.to] = (by[l.to] || 0) + 1);
    const items = Object.entries(by).sort((p, q) => q[1] - p[1]);
    const bA = clamp((t - MAIN_END - 0.8) / 0.5); g.globalAlpha = a * bA;
    const cw = 330, x0 = 960 - (items.length * cw) / 2;
    items.forEach(([who, k], i) => {
      const cx = x0 + cw * i + cw / 2;
      g.fillStyle = 'rgba(255,255,255,0.08)'; rr(cx - 140, 690, 280, 150, 20); g.fill();
      g.font = '64px YTSans'; g.fillStyle = '#fff'; g.fillText(String(k), cx, 770);
      g.font = '26px Pret'; g.fillStyle = 'rgba(255,255,255,0.65)'; g.fillText('to ' + who, cx, 815);
    });
    g.globalAlpha = 1;
  }
  return c.toDataURL('image/png');
};
window.TOTAL = TOTAL; window.ready = true;`;

const html = `<!doctype html><html><body style="margin:0;background:transparent"><script type="module">${page_js}</script></body></html>`;
const pageName = `counted/_ov_${process.pid}.html`;
fs.writeFileSync(path.join(root, pageName), html);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => { console.error('[pageerror]', e); process.exit(1); });
await page.goto(`http://localhost:${port}/${pageName}`);
await page.waitForFunction('window.ready === true', null, { timeout: 60000 });
const grab = async t => Buffer.from((await page.evaluate(t => window.draw(t), t)).split(',')[1], 'base64');
const still = opt('still', null);
if (still) fs.writeFileSync(args[0], await grab(+still));
else {
  const total = await page.evaluate(() => window.TOTAL);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'qtrle', '-pix_fmt', 'argb', args[0]], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.ceil(total * FPS);
  for (let i = 0; i < n; i++) { const b = await grab(i / FPS); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 300 === 0) process.stderr.write(`${i}/${n}\n`); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close(); server.close(); fs.unlinkSync(path.join(root, pageName));
