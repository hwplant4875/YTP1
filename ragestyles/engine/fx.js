// RageStyles FX library: footage, camera moves, edit-style effects, kinetic type.
export const W = 1080, H = 1920;

// ---------- easing / envelopes ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const ease = {
  lin: t => t,
  inOut: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  out: t => 1 - Math.pow(1 - t, 3),
  in: t => t * t * t,
  outExpo: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
  inExpo: t => t <= 0 ? 0 : Math.pow(2, 10 * t - 10),
  outBack: (t, s = 1.70158) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
  outElastic: t => t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1,
};
// progress of t through [a, a+d], eased
export const prog = (t, a, d, e = ease.lin) => e(clamp((t - a) / d));
// attack/hold/release envelope: 0 → 1 → 0
export const env = (t, a, att, hold, rel, e = ease.out) => {
  if (t < a) return 0;
  if (t < a + att) return e((t - a) / att);
  if (t < a + att + hold) return 1;
  return 1 - ease.inOut(clamp((t - a - att - hold) / rel));
};
// decaying impulse at t0 (for punches / flashes)
export const impulse = (t, t0, decay = 8) => t < t0 ? 0 : Math.exp(-(t - t0) * decay);

// deterministic smooth noise
const hash = n => { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); };
export const noise1 = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };
export const shake = (t, amp, freq = 18, seed = 0) => ({
  x: noise1(t * freq + seed) * amp, y: noise1(t * freq + 31.7 + seed) * amp, r: noise1(t * freq * .7 + 77 + seed) * amp * 0.0009,
});

export function makeCtx(cv) {
  const g = cv.getContext('2d', { alpha: false, willReadFrequently: false });
  const R = { cv, g, W, H, ease, prog, env, impulse, shake, clamp, lerp };
  const cache = new Map();
  const off = (w = W, h = H) => { const c = new OffscreenCanvas(w, h); return [c, c.getContext('2d')]; };
  const [tmpA, gA] = off(), [tmpB, gB] = off(), [tmpC, gC] = off();

  // ---------- media ----------
  R.image = async url => {
    if (cache.has(url)) return cache.get(url);
    const p = fetch(url).then(r => { if (!r.ok) throw new Error('404 ' + url); return r.blob(); }).then(b => createImageBitmap(b));
    cache.set(url, p); return p;
  };
  // footage as frame sequence (ffmpeg -> dir/%05d.jpg). info.json holds {n, fps, w, h}
  R.clip = async (dir, opts = {}) => {
    const info = await (await fetch(`/@work/${dir}/info.json`)).json();
    const c = { dir, ...info, ...opts };
    c.at = async (st) => {   // st = seconds into the source
      const i = clamp(Math.round(st * c.fps), 0, c.n - 1) + 1;
      const url = `/@work/${dir}/${String(i).padStart(5, '0')}.jpg`;
      const img = await R.image(url);
      // drop far-behind frames to bound memory
      if (i % 30 === 0) for (const k of cache.keys()) if (k.startsWith(`/@work/${dir}/`) && Math.abs(parseInt(k.slice(-9, -4)) - i) > 90) cache.delete(k);
      return img;
    };
    return c;
  };

  // draw an image cover-fit, with camera {zoom, x, y (fraction offsets), rot, focusX, focusY}
  R.draw = (img, cam = {}, gg = g) => {
    const { zoom = 1, x = 0, y = 0, rot = 0, fx = .5, fy = .5, alpha = 1, filter = 'none', fit = 'cover', comp = 'source-over' } = cam;
    const s = (fit === 'cover' ? Math.max(W / img.width, H / img.height) : Math.min(W / img.width, H / img.height)) * zoom;
    const dw = img.width * s, dh = img.height * s;
    // focus point of the source placed at screen center, then offset
    let cx = W / 2 - (fx - .5) * dw + x * W, cy = H / 2 - (fy - .5) * dh + y * H;
    if (fit === 'cover') {   // keep frame covered
      cx = clamp(cx, W - dw / 2, dw / 2); cy = clamp(cy, H - dh / 2, dh / 2);
    }
    gg.save(); gg.globalAlpha = alpha; gg.filter = filter; gg.globalCompositeOperation = comp;
    gg.translate(cx + 0, cy); gg.rotate(rot); gg.drawImage(img, -dw / 2, -dh / 2, dw, dh); gg.restore();
  };
  // blurred background fill + framed foreground (for 16:9 sources in a 9:16 frame)
  R.drawFramed = (img, cam = {}) => {
    R.draw(img, { zoom: 1.15, filter: 'blur(28px) brightness(.45) saturate(1.2)' });
    const { zoom = 1, x = 0, y = 0, rot = 0, frameY = 0, round = 0 } = cam;
    const s = W / img.width * zoom, dw = img.width * s, dh = img.height * s;
    g.save(); g.translate(W / 2 + x * W, H / 2 + frameY * H + y * H); g.rotate(rot);
    g.shadowColor = 'rgba(0,0,0,.7)'; g.shadowBlur = 60;
    if (round) { g.beginPath(); g.roundRect(-dw / 2, -dh / 2, dw, dh, round); g.clip(); }
    g.drawImage(img, -dw / 2, -dh / 2, dw, dh); g.restore();
  };

  // ---------- post effects on the whole canvas ----------
  const snap = () => { gA.globalCompositeOperation = 'copy'; gA.filter = 'none'; gA.globalAlpha = 1; gA.drawImage(cv, 0, 0); gA.globalCompositeOperation = 'source-over'; return tmpA; };
  R.grade = (filter) => { snap(); g.save(); g.filter = filter; g.globalCompositeOperation = 'copy'; g.drawImage(tmpA, 0, 0); g.restore(); };
  R.flash = (a, color = '#fff', comp = 'screen') => { if (a <= 0.003) return; g.save(); g.globalAlpha = clamp(a); g.globalCompositeOperation = comp; g.fillStyle = color; g.fillRect(0, 0, W, H); g.restore(); };
  R.fill = (color, a = 1) => { g.save(); g.globalAlpha = a; g.fillStyle = color; g.fillRect(0, 0, W, H); g.restore(); };
  R.bloom = (amt = .5, radius = 24, thresh = 'brightness(1.1) contrast(1.6)') => {
    if (amt <= 0) return;
    gB.globalCompositeOperation = 'copy'; gB.filter = `${thresh} blur(${radius}px)`; gB.drawImage(cv, 0, 0); gB.filter = 'none';
    g.save(); g.globalCompositeOperation = 'screen'; g.globalAlpha = amt; g.drawImage(tmpB, 0, 0); g.restore();
  };
  // RGB split: px offset horizontally (and optional vertical)
  R.rgbSplit = (px, py = 0) => {
    if (Math.abs(px) < .5 && Math.abs(py) < .5) return;
    snap();
    const chan = (col, dx, dy) => {
      gB.globalCompositeOperation = 'copy'; gB.drawImage(tmpA, 0, 0);
      gB.globalCompositeOperation = 'multiply'; gB.fillStyle = col; gB.fillRect(0, 0, W, H);
      g.drawImage(tmpB, dx, dy);
    };
    g.save(); g.globalCompositeOperation = 'copy'; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'lighter';
    chan('#f00', px, py); chan('#0f0', 0, 0); chan('#00f', -px, -py); g.restore();
  };
  // directional motion blur (whip pans / zoom streaks): n ghost copies
  R.motionBlur = (dx, dy, n = 8) => {
    if (Math.hypot(dx, dy) < 1) return;
    snap(); g.save(); g.globalCompositeOperation = 'copy'; g.globalAlpha = 1; g.drawImage(tmpA, 0, 0); g.globalCompositeOperation = 'source-over';
    for (let i = 1; i <= n; i++) { g.globalAlpha = 1 / (i + 1); const k = i / n - .5; g.drawImage(tmpA, dx * k, dy * k); }
    g.restore();
  };
  // radial zoom blur toward center
  R.zoomBlur = (amt, n = 7, cx = W / 2, cy = H / 2) => {
    if (amt < .003) return;
    snap(); g.save();
    for (let i = 1; i <= n; i++) {
      const s = 1 + amt * i / n; g.globalAlpha = 1 / (i + 1);
      g.setTransform(s, 0, 0, s, cx - cx * s, cy - cy * s); g.drawImage(tmpA, 0, 0);
    }
    g.restore();
  };
  R.vignette = (a = .55, inner = .45) => {
    const gr = g.createRadialGradient(W / 2, H / 2, W * inner, W / 2, H / 2, H * .75);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(0,0,0,${a})`);
    g.save(); g.fillStyle = gr; g.fillRect(0, 0, W, H); g.restore();
  };
  const grains = [];
  for (let k = 0; k < 6; k++) {
    const [c, gc] = off(540, 960); const id = gc.createImageData(540, 960);
    for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    gc.putImageData(id, 0, 0); grains.push(c);
  }
  R.grain = (a = .06, t = 0) => { g.save(); g.globalAlpha = a; g.globalCompositeOperation = 'overlay'; g.drawImage(grains[Math.floor(t * 24) % 6], 0, 0, W, H); g.restore(); };
  // warm light leak sweeping
  R.leak = (a, t, color = '255,140,40') => {
    if (a <= 0) return;
    const x = W * (.2 + .6 * noise1(t * .4 + 3) * .5 + .3), y = H * (.3 + .3 * noise1(t * .3 + 9));
    const gr = g.createRadialGradient(x, y, 0, x, y, H * .55);
    gr.addColorStop(0, `rgba(${color},${.8 * a})`); gr.addColorStop(1, `rgba(${color},0)`);
    g.save(); g.globalCompositeOperation = 'screen'; g.fillStyle = gr; g.fillRect(0, 0, W, H); g.restore();
  };
  R.letterbox = (frac) => { if (frac <= 0) return; g.save(); g.fillStyle = '#000'; g.fillRect(0, 0, W, H * frac); g.fillRect(0, H * (1 - frac), W, H * frac); g.restore(); };

  // ---------- typography ----------
  // text with stroke + shadow/glow. opts: size, font, weight, color, stroke, sw, glow, glowColor, align, scale, alpha, track, rot, base
  R.text = (str, x, y, o = {}) => {
    const { size = 120, font = 'Anton', weight = 400, color = '#fff', stroke = null, sw = 0, glow = 0, glowColor = 'rgba(0,0,0,.85)',
      align = 'center', scale = 1, alpha = 1, track = 0, rot = 0, base = 'middle', italic = false, maxW = W * .9, grad = null, skew = 0 } = o;
    if (alpha <= 0 || scale <= 0) return 0;
    g.save(); g.globalAlpha = clamp(alpha); g.translate(x, y); g.rotate(rot); if (skew) g.transform(1, 0, skew, 1, 0, 0);
    g.font = `${italic ? 'italic ' : ''}${weight} ${size}px '${font}'`; g.letterSpacing = `${track}px`;
    let w = g.measureText(str).width; const fit = w > maxW ? maxW / w : 1;
    g.scale(scale * fit, scale * fit); g.textAlign = align; g.textBaseline = base; g.lineJoin = 'round';
    if (glow) { g.shadowColor = glowColor; g.shadowBlur = glow; }
    if (stroke && sw) { g.strokeStyle = stroke; g.lineWidth = sw; g.strokeText(str, 0, 0); g.shadowBlur = 0; }
    if (grad) { const gr = g.createLinearGradient(0, -size / 2, 0, size / 2); grad.forEach(([s, c]) => gr.addColorStop(s, c)); g.fillStyle = gr; } else g.fillStyle = color;
    g.fillText(str, 0, 0);
    g.restore(); return w * fit * scale;
  };
  R.measure = (str, size, font = 'Anton', weight = 400, track = 0) => { g.save(); g.font = `${weight} ${size}px '${font}'`; g.letterSpacing = `${track}px`; const w = g.measureText(str).width; g.restore(); return w; };

  // kinetic word-by-word caption. words: [{w:'LIGHT', t:1.2, hl:true}], shown in a line group until group end.
  // style: edit-caption (white, thick black stroke, highlight yellow, pop with overshoot)
  R.caption = (words, t, o = {}) => {
    const { y = H * .62, size = 104, font = 'YTS', weight = 900, hl = '#FFD400', color = '#fff', end = Infinity, gap = 22, maxW = W * .88, out = .12 } = o;
    const vis = words.filter(w => t >= w.t);
    if (!vis.length || t > end + out) return;
    const fade = 1 - clamp((t - end) / out);
    // layout words into lines
    const sp = R.measure(' ', size, font, weight); const lines = [[]]; let lw = 0;
    for (const w of words) { const ww = R.measure(w.w, size, font, weight); if (lw + ww > maxW && lines.at(-1).length) { lines.push([]); lw = 0; } lines.at(-1).push({ ...w, ww }); lw += ww + sp; }
    const lh = size * 1.12; let yy = y - (lines.length - 1) * lh / 2;
    for (const line of lines) {
      const tot = line.reduce((a, w) => a + w.ww, 0) + sp * (line.length - 1); let xx = W / 2 - tot / 2;
      for (const w of line) {
        if (t >= w.t) {
          const p = clamp((t - w.t) / .16); const sc = ease.outBack(p, 2.6) * (w.big ? 1.12 : 1);
          R.text(w.w, xx + w.ww / 2, yy, { size, font, weight, color: w.hl ? (w.color || hl) : color, stroke: '#000', sw: size * .2, glow: 24, scale: .55 + .45 * sc, alpha: Math.min(p * 3, 1) * fade, rot: w.rot || 0 });
        }
        xx += w.ww + sp;
      }
      yy += lh;
    }
  };

  // pill / label box
  R.box = (x, y, w, h, o = {}) => {
    const { r = 18, fill = 'rgba(0,0,0,.6)', stroke = null, sw = 3, alpha = 1, glow = 0, glowColor = 'rgba(0,0,0,.6)', blurBg = 0 } = o;
    g.save(); g.globalAlpha = alpha;
    if (blurBg) { g.save(); g.beginPath(); g.roundRect(x, y, w, h, r); g.clip(); snap(); g.filter = `blur(${blurBg}px)`; g.drawImage(tmpA, 0, 0); g.restore(); }
    g.beginPath(); g.roundRect(x, y, w, h, r);
    if (glow) { g.shadowColor = glowColor; g.shadowBlur = glow; }
    g.fillStyle = fill; g.fill(); g.shadowBlur = 0;
    if (stroke) { g.strokeStyle = stroke; g.lineWidth = sw; g.stroke(); }
    g.restore();
  };

  R.begin = async t => { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); };
  R.end = t => { g.setTransform(1, 0, 0, 1, 0, 0); };
  R.off = off;
  return R;
}
