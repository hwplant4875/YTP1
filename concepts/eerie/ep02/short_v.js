// Vertical 9:16 wrapper around the EP02 engine: camera per shot, own captions, title, glitch on cuts.
(() => {
const cv = document.getElementById('c'), X = cv.getContext('2d'), VW = cv.width, VH = cv.height;
const oST = X.setTransform.bind(X);
let CAM = new DOMMatrix();
X.setTransform = function (a, b, c, d, e, f) {
  const m = typeof a === 'object' ? new DOMMatrix([a.a, a.b, a.c, a.d, a.e, a.f]) : new DOMMatrix([a, b, c, d, e, f]);
  oST(CAM.multiply(m));
};
X.resetTransform = function () { oST(CAM); };
const SH = window.SH, SY = 1000;
const srcT = t => { for (const [a, b, o] of SH.pieces) if (t + 1e-6 >= a + o && t < b + o) return t - o; const p = SH.pieces[SH.pieces.length - 1]; return p[1] - 1e-3; };
const ease = k => k * k * (3 - 2 * k);
function cam(st) {
  let i = 0; for (let j = 0; j < SH.cams.length; j++) if (SH.cams[j][0] <= st + 1e-6) i = j;
  const k = SH.cams[i]; let [, x, y, s, d] = k;
  if (d > 0 && i > 0 && st < k[0] + d) { const p = SH.cams[i - 1], u = ease((st - k[0]) / d); x = p[1] + (x - p[1]) * u; y = p[2] + (y - p[2]) * u; s = p[3] + (s - p[3]) * u; }
  return new DOMMatrix().translate(VW / 2, SY).scale(s).translate(-x, -y);
}
function txt(s, x, y, font, fill, lw) {
  X.font = font; X.textAlign = 'center'; X.textBaseline = 'alphabetic'; X.lineJoin = 'round';
  if (lw) { X.lineWidth = lw; X.strokeStyle = '#000'; X.strokeText(s, x, y); }
  X.fillStyle = fill; X.fillText(s, x, y);
}
function glitch(t) {
  let c = -9; for (const q of SH.cuts) if (q <= t) c = q;
  const dt = t - c, dur = 0.17; if (dt < 0 || dt > dur) return;
  const k = 1 - dt / dur, tmp = glitch.c || (glitch.c = document.createElement('canvas'));
  tmp.width = VW; tmp.height = VH; tmp.getContext('2d').drawImage(cv, 0, 0);
  X.save(); X.globalCompositeOperation = 'lighter'; X.globalAlpha = 0.45 * k; X.drawImage(tmp, 14 * k, 0); X.globalAlpha = 0.3 * k; X.drawImage(tmp, -10 * k, 2); X.restore();
  let seed = Math.round(t * 30) * 9301 + 49297; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < 5; i++) { const y = rnd() * VH, h = 10 + rnd() * 60, dx = (rnd() - 0.5) * 80 * k; X.drawImage(tmp, 0, y, VW, h, dx, y, VW, h); }
}
window.drawV = function (t) {
  const st = srcT(t);
  oST(1, 0, 0, 1, 0, 0); X.globalAlpha = 1; X.fillStyle = '#000'; X.fillRect(0, 0, VW, VH);
  CAM = cam(st); const CAM0 = CAM;
  // keep the engine inside its 16:9 rect: its screen-space overlays only cover that rect
  oST(CAM); X.save(); X.beginPath(); X.rect(0, 0, 1920, 1080); X.clip();
  window.draw(st);
  X.restore();
  CAM = new DOMMatrix(); oST(1, 0, 0, 1, 0, 0); X.globalAlpha = 1; X.globalCompositeOperation = 'source-over'; X.filter = 'none'; X.setLineDash([]); X.shadowBlur = 0;
  // soften the edges of the 16:9 scene so it melts into the black frame
  { const r = CAM0.transformPoint(new DOMPoint(0, 0)), q = CAM0.transformPoint(new DOMPoint(1920, 1080)), F = 160;
    const edge = (x0, y0, x1, y1, w, h) => { const g = X.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, '#000'); g.addColorStop(1, 'rgba(0,0,0,0)'); X.fillStyle = g; X.fillRect(Math.min(x0, x1), Math.min(y0, y1), w, h); };
    if (r.y > -F) edge(0, r.y, 0, r.y + F, VW, F);
    if (q.y < VH + F) edge(0, q.y, 0, q.y - F, VW, F);
    if (r.x > -F) { const g = X.createLinearGradient(r.x, 0, r.x + F, 0); g.addColorStop(0, '#000'); g.addColorStop(1, 'rgba(0,0,0,0)'); X.fillStyle = g; X.fillRect(r.x, 0, F, VH); }
    if (q.x < VW + F) { const g = X.createLinearGradient(q.x, 0, q.x - F, 0); g.addColorStop(0, '#000'); g.addColorStop(1, 'rgba(0,0,0,0)'); X.fillStyle = g; X.fillRect(q.x - F, 0, F, VH); } }
  glitch(t);
  // film grain, a slow light band and a vignette over the whole vertical frame
  if (!window._gr) { window._gr = [0, 1, 2, 3].map(() => { const g = document.createElement('canvas'); g.width = 540; g.height = 960; const gx = g.getContext('2d'), im = gx.createImageData(540, 960);
    for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } gx.putImageData(im, 0, 0); return g; }); }
  X.globalAlpha = 0.06; X.drawImage(window._gr[Math.round(t * 30) % 4], 0, 0, VW, VH); X.globalAlpha = 1;
  const by = ((t * 120) % (VH + 300)) - 150; let lb = X.createLinearGradient(0, by - 90, 0, by + 90);
  lb.addColorStop(0, 'rgba(255,255,255,0)'); lb.addColorStop(0.5, 'rgba(255,255,255,0.025)'); lb.addColorStop(1, 'rgba(255,255,255,0)'); X.fillStyle = lb; X.fillRect(0, by - 90, VW, 180);
  const vg = X.createRadialGradient(VW / 2, SY, 380, VW / 2, SY, 1150); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(0.6, 'rgba(0,0,0,0.3)'); vg.addColorStop(1, 'rgba(0,0,0,0.85)');
  X.fillStyle = vg; X.fillRect(0, 0, VW, VH);
  // fades behind title and captions so text always reads
  let g = X.createLinearGradient(0, 0, 0, 560); g.addColorStop(0, 'rgba(0,0,0,0.95)'); g.addColorStop(0.7, 'rgba(0,0,0,0.75)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  X.fillStyle = g; X.fillRect(0, 0, VW, 560);
  g = X.createLinearGradient(0, 1380, 0, 1920); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.25, 'rgba(0,0,0,0.8)'); g.addColorStop(1, 'rgba(0,0,0,0.95)');
  X.fillStyle = g; X.fillRect(0, 1380, VW, 540);
  X.letterSpacing = '-1px';
  const fit = (s, px, max) => { X.font = `900 ${px}px M`; return Math.min(px, px * max / X.measureText(s).width); };
  txt(SH.title[0], VW / 2, 300, `900 ${fit(SH.title[0], 92, 960)}px M`, '#ffffff', 0);
  txt(SH.title[1], VW / 2, 408, `900 ${fit(SH.title[1], 100, 980)}px M`, '#ff2a2a', 0);
  X.letterSpacing = '0px';
  // outro: the question for the comments, over the last seconds
  if (SH.outro && t > SH.total - 2.4) { const k = Math.min(1, (t - (SH.total - 2.4)) / 0.35);
    X.globalAlpha = 0.88 * k; X.fillStyle = '#000'; X.fillRect(0, 0, VW, VH); X.globalAlpha = k; X.letterSpacing = '-1px';
    txt(SH.outro[0], VW / 2, 960, `900 ${fit(SH.outro[0], 110, 960)}px M`, '#ffffff', 0);
    if (SH.outro[1]) txt(SH.outro[1], VW / 2, 1080, `900 ${fit(SH.outro[1], 60, 900)}px M`, '#ff2a2a', 0);
    X.globalAlpha = 1; X.letterSpacing = '0px'; return; }
  // captions: one chunk at a time, current word bright
  let c = null; for (const k of SH.caps) if (t >= k.s - 0.08 && t <= k.e + 0.35) c = k;
  if (c) {
    X.font = '900 76px M'; const parts = c.w.map(w => w[0].toUpperCase()), sp = X.measureText(' ').width;
    const ws = parts.map(p => X.measureText(p).width), tw = ws.reduce((a, b) => a + b, 0) + sp * (parts.length - 1);
    const sc = Math.min(1, 900 / tw); X.save(); X.translate(VW / 2, 1520); X.scale(sc, sc);
    let x = -tw / 2;
    parts.forEach((p, i) => { const on = t >= c.w[i][1] - 0.05; X.textAlign = 'left'; X.lineJoin = 'round'; X.lineWidth = 14; X.strokeStyle = '#000'; X.strokeText(p, x, 0);
      X.fillStyle = on ? '#ffffff' : 'rgba(255,255,255,0.45)'; X.fillText(p, x, 0); x += ws[i] + sp; });
    X.restore();
  }
};
})();
