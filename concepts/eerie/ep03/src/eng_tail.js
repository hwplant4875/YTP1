// ---------- HUD, captions, texture ----------
let grainC = null, vig = null;
function initTex() {
  grainC = [0, 1, 2, 3].map(() => { const g = document.createElement('canvas'); g.width = 480; g.height = 270; const gx = g.getContext('2d');
    const im = gx.createImageData(480, 270); for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    gx.putImageData(im, 0, 0); return g; });
}
function chunks(seg) {
  if (seg._ch) return seg._ch;
  const out = []; let cur = [];
  seg.words.forEach(w => { cur.push(w); if (/[.?!]$/.test(w.w) || (cur.length >= 4 && /,$/.test(w.w)) || cur.length >= 10) { out.push(cur); cur = []; } });
  if (cur.length) out.push(cur);
  return (seg._ch = out);
}
function caption(t, seg) {
  if (t > seg.end + 0.3) return;
  const ch = chunks(seg); let c = null;
  for (const k of ch) if (t >= k[0].s - 0.08) c = k;
  if (!c) return;
  const s = c.map(w => w.w).join(' ').toUpperCase();
  ctx.font = '800 34px M'; ctx.letterSpacing = '1.5px'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  // dark band only where the scene behind the caption is bright (white bed, body)
  const tw = ctx.measureText(s).width + 60, px = ctx.getImageData(960 - tw / 2, 958, tw, 56).data;
  let lum = 0; for (let i = 0; i < px.length; i += 16) lum += px[i]; lum /= px.length / 16;
  if (lum > 50) { ctx.fillStyle = `rgba(0,0,0,${Math.min(0.72, 0.35 + (lum - 50) / 200)})`; ctx.beginPath(); ctx.roundRect(960 - tw / 2, 958, tw, 56, 10); ctx.fill(); }
  ctx.lineJoin = 'round'; ctx.lineWidth = 8; ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.strokeText(s, 960, 1000);
  ctx.fillStyle = '#ffffff'; ctx.fillText(s, 960, 1000); ctx.letterSpacing = '0px';
}
// shot boundaries for glitch transitions: every segment start plus the extra cuts inside segments
// shot boundaries for glitch transitions come from timeline.py
const cutTimes = () => window.TL.cuts || window.TL.segments.map(s => s.start);
function glitch(t, f) {
  let cut = -9; for (const c of cutTimes()) if (c <= t) cut = c;
  const dt = t - cut, dur = 0.17; if (dt < 0 || dt > dur || cut < 1) return;
  const k = 1 - dt / dur;
  const tmp = glitch.c || (glitch.c = document.createElement('canvas')); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
  // RGB split
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.5 * k;
  ctx.drawImage(tmp, 14 * k, 0); ctx.globalAlpha = 0.35 * k; ctx.drawImage(tmp, -10 * k, 2); ctx.restore();
  let seed = f * 9301 + 49297; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < 10; i++) { const y = rnd() * H, h = 6 + rnd() * 50, dx = (rnd() - 0.5) * 160 * k; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); }
  ctx.globalAlpha = 0.4 * k; ctx.fillStyle = '#fff'; for (let i = 0; i < 5; i++) ctx.fillRect(0, rnd() * H, W, 1 + rnd() * 3); ctx.globalAlpha = 1;
}

// analog interference ("지지직"): short random tears, stronger around knocks, meows, the reveal and the error
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function disturbance(t) {
  let I = 0;
  const b = Math.floor(t * 3); if (hash(b) < 0.08 && (t * 3 - b) < 0.3) I = 0.45;      // a stray tear every few seconds
  I = Math.max(I, knockPulse(t) * 0.6);
  for (const e of window.TL.events) {
    const d = t - e.t;
    if (e.type === 'meow1' || e.type === 'meow2') { if (d > 0 && d < 2.8) I = Math.max(I, 0.2 + 0.2 * Math.abs(Math.sin(d * 7))); }
    if (e.type === 'boom' && d > 0 && d < 0.4) I = Math.max(I, 0.8 * (1 - d / 0.4));
    if (e.type === 'error' && d > -0.1 && d < 1.6) I = Math.max(I, d < 0.25 ? 0.9 : 0.3);
    if (e.type === 'tapestop' && d > 0 && d < 0.8) I = Math.max(I, 0.7);
    if (e.type === 'morph' && d > 0 && d < 0.75) I = Math.max(I, d < 0.5 ? 0.85 : 0.85 * (1 - (d - 0.5) / 0.25));
  }
  return I;
}
function interfere(t, f, I) {
  if (I <= 0.02) return;
  const tmp = interfere.c || (interfere.c = document.createElement('canvas')); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
  let seed = f * 7919 + 13; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha = 0.28 * I;
  ctx.drawImage(tmp, 12 * I + rnd() * 6 * I, 0); ctx.globalAlpha = 0.18 * I; ctx.drawImage(tmp, -9 * I, 1);
  ctx.restore();
  for (let i = 0; i < Math.round(4 + 12 * I); i++) { const y = rnd() * H, h = 3 + rnd() * 40 * I, dx = (rnd() - 0.5) * 140 * I; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); }
  ctx.globalAlpha = 0.5 * I; ctx.fillStyle = '#fff'; for (let i = 0; i < 6; i++) ctx.fillRect(0, rnd() * H, W, 1 + rnd() * 2);
  ctx.globalAlpha = 0.1 * I; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
}

window.draw = (t) => {
  if (!grainC) initTex();
  const f = Math.round(t * 30);  // texture/glitch seed changes 30x a second even at 60 fps
  const segs = window.TL.segments; let seg = segs[0];
  for (const s of segs) if (s.start <= t + 1e-6) seg = s;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow(); ctx.setLineDash([]);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  // slow handheld drift so no frame is ever perfectly still
  ctx.translate(W / 2 + Math.sin(t * 0.53) * 5 + Math.sin(t * 1.7) * 1.2, H / 2 + Math.cos(t * 0.41) * 4);
  ctx.rotate(Math.sin(t * 0.29) * 0.0025); ctx.translate(-W / 2, -H / 2);
  (S[seg.id] || S.h1)(t, seg);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow();
  glitch(t, f);
  interfere(t, f, disturbance(t));
  caption(t, seg);
  ctx.globalAlpha = 0.07; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
  const by = ((t * 90) % (H + 300)) - 150, bg = ctx.createLinearGradient(0, by - 80, 0, by + 80);
  bg.addColorStop(0, 'rgba(255,255,255,0)'); bg.addColorStop(0.5, 'rgba(255,255,255,0.025)'); bg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = bg; ctx.fillRect(0, by - 80, W, 160);
  if (!vig) { vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.38, W / 2, H / 2, H * 1.05); vig.addColorStop(0, 'rgba(0,0,0,0)'); vig.addColorStop(0.6, 'rgba(0,0,0,0.32)'); vig.addColorStop(1, 'rgba(0,0,0,0.82)'); }
  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);
  // blackouts: the screen dies until the next line starts
  for (const e of window.TL.events) if (e.type === 'blackout' && t >= e.t) {
    const nx = segs.find(sg => sg.start > e.t); if (!nx || t < nx.start - 0.001) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
  }
};
})();
