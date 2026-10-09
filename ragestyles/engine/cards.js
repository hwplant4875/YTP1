// Reusable RageStyles graphic components (stat cards, rank badges, comparison bars, year slams).
import { W, H, clamp, ease, lerp, impulse } from '/engine/fx.js';
const RED = '#ff2a2a', YEL = '#FFD400';

// glassy stat panel: rows [[label, value], ...] sliding in from side
export function statPanel(R, rows, t, t0, { x = 60, y = 1000, w = 430, side = 'left', accent = RED, title = null } = {}) {
  const a = clamp((t - t0) / .3); if (a <= 0) return;
  const dx = (1 - ease.outExpo(a)) * (side === 'left' ? -w - 80 : w + 80);
  const rh = 104, h = rows.length * rh + (title ? 86 : 30);
  R.box(x + dx, y, w, h, { fill: 'rgba(8,8,10,.62)', stroke: 'rgba(255,255,255,.16)', sw: 2, r: 26, blurBg: 18 });
  R.box(x + dx, y + 26, 8, h - 52, { fill: accent, r: 4 });
  let yy = y + (title ? 58 : 30);
  if (title) R.text(title, x + dx + 34, y + 46, { size: 34, font: 'Mont', weight: 800, color: accent, align: 'left', track: 5 });
  rows.forEach(([lbl, val], i) => {
    const ra = clamp((t - t0 - .12 - i * .1) / .22); if (ra <= 0) return;
    const off = (1 - ease.out(ra)) * 30;
    R.text(lbl, x + dx + 34, yy + 26, { size: 28, font: 'Mont', weight: 800, color: '#9b9ba3', align: 'left', track: 4, alpha: ra });
    R.text(val, x + dx + 34 + off, yy + 72, { size: 56, font: 'Anton', color: '#fff', align: 'left', alpha: ra });
    yy += rh;
  });
}

// rank badge "#3"
export function rankBadge(R, n, x, y, t, t0, { size = 210, color = YEL } = {}) {
  const a = clamp((t - t0) / .2); if (a <= 0) return;
  const sc = 1 + 1.2 * Math.pow(1 - ease.outExpo(a), 2);
  R.text('#' + n, x, y, { size, font: 'Anton', color, stroke: '#000', sw: size * .12, glow: 40, scale: sc, alpha: Math.min(1, a * 2), rot: -.05 });
}

// name plate with underline sweep
export function namePlate(R, name, sub, x, y, t, t0, { size = 96, align = 'center' } = {}) {
  const a = clamp((t - t0) / .25); if (a <= 0) return;
  const w = R.measure(name, size, 'Anton');
  R.text(name, x, y, { size, font: 'Anton', color: '#fff', stroke: '#000', sw: size * .14, glow: 30, alpha: a, align, scale: .85 + .15 * ease.outBack(a) });
  const lx = align === 'center' ? x - w / 2 : x;
  R.box(lx, y + size * .58, w * ease.outExpo(clamp((t - t0 - .1) / .35)), 8, { fill: RED, r: 4 });
  if (sub) R.text(sub, align === 'center' ? x : x, y + size * .58 + 50, { size: 38, font: 'Mont', weight: 800, color: '#ddd', align, alpha: clamp((t - t0 - .2) / .25), track: 4, stroke: '#000', sw: 8 });
}

// big year slam with streaks
export function yearSlam(R, year, x, y, t, t0, { size = 260, color = '#fff' } = {}) {
  const a = clamp((t - t0) / .16); if (a <= 0) return;
  const sc = 1 + 2.2 * Math.pow(1 - ease.outExpo(a), 2);
  R.text(String(year), x, y, { size, font: 'Anton', color, stroke: 'rgba(0,0,0,.9)', sw: size * .08, glow: 60, glowColor: 'rgba(0,0,0,.9)', scale: sc, alpha: Math.min(1, a * 2), track: 4 });
}

// horizontal comparison bars [{label, value, color}] scaled to max
export function compareBars(R, items, t, t0, { x = 90, y = 1100, w = 900, unit = '', max = null } = {}) {
  const mx = max || Math.max(...items.map(i => i.value));
  items.forEach((it, i) => {
    const a = clamp((t - t0 - i * .15) / .5); if (a <= 0) return;
    const yy = y + i * 150, bw = w * (it.value / mx) * ease.outExpo(a);
    R.text(it.label, x, yy, { size: 40, font: 'Mont', weight: 800, color: '#fff', align: 'left', alpha: clamp(a * 3), stroke: '#000', sw: 8 });
    R.box(x, yy + 30, w, 56, { fill: 'rgba(255,255,255,.1)', r: 28 });
    R.box(x, yy + 30, Math.max(56, bw), 56, { fill: it.color || RED, r: 28, glow: 24, glowColor: it.color || RED });
    R.text(`${Math.round(it.value * ease.out(a))}${unit}`, x + Math.max(56, bw) - 24, yy + 59, { size: 40, font: 'Anton', color: '#fff', align: 'right', alpha: clamp(a * 3) });
  });
}

// cut-out photo card with white border + shadow, slight tilt (scrapbook / edit style)
export function photoCard(R, img, cx, cy, w, t, t0, { rot = -.04, border = 14, from = 'bottom', h = null } = {}) {
  const a = clamp((t - t0) / .35); if (a <= 0 || !img) return;
  const hh = h || w * img.height / img.width;
  const dy = (1 - ease.outBack(a, 1.4)) * (from === 'bottom' ? 500 : -500);
  const g = R.g; g.save(); g.translate(cx, cy + dy); g.rotate(rot * ease.out(a) + (1 - a) * .2);
  g.shadowColor = 'rgba(0,0,0,.75)'; g.shadowBlur = 50; g.shadowOffsetY = 20;
  g.fillStyle = '#f4f1ea'; g.fillRect(-w / 2 - border, -hh / 2 - border, w + border * 2, hh + border * 2);
  g.shadowColor = 'transparent';
  // cover-fit image inside
  const s = Math.max(w / img.width, hh / img.height), dw = img.width * s, dh = img.height * s;
  g.beginPath(); g.rect(-w / 2, -hh / 2, w, hh); g.clip();
  g.drawImage(img, -dw / 2, -dh / 2, dw, dh);
  g.restore();
}
