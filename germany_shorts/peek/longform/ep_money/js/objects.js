// Shared iso objects for the story scenes: paper ground, floating boards, $100 bundles,
// share cubes, chips, data centres, vaults and price tags. Units are free (scene units).
import {
  W, H, C30, SQ15, tones, rgb, css, mix, poly, box, texQuad, faceFrame, dashedBox, discZ,
  clamp, lerp, sstep, easeOut, backOut, mulberry32,
} from './iso.js';

export const COL = {
  paper: '#F2EADB', dot: '#CDBFA4', ink: '#2B2533', cream: '#F4EEE2',
  board: '#E6DBC6', strata: ['#D9CBB0', '#CDBB9C', '#C1AC8B'],
  grey: ['#C3CAD2', '#B7C0CA', '#CCD1D6', '#B0B9C4', '#C9C6C2', '#D2C7BC', '#BDC3C9'],
  tech: '#A9A2DA', chip: '#7F72CB', nvda: '#6A5BC0', loss: '#E2705C', gain: '#3FA796',
  billTop: '#DAE8CC', billInk: '#3F6B4B', long: '#95BE84', end: '#6E9A64', strap: '#D9A53A',
  slate: '#8C99AF', steel: '#AEB7C4', brass: '#D9A53A', glow: '#7FE3F0', tag: '#FBF5E6', sand: '#D8C29A',
};
export const T = (hex) => tones(hex);
const lg = Math.log10;

// ---------- paper ground: plain paper with a faint iso dot lattice at several scales ----------
export function paper(ctx) { ctx.fillStyle = COL.paper; ctx.fillRect(0, 0, W, H); }
export function lattice(ctx, cam, alpha = 1, z = 0) {
  if (alpha <= 0.01) return;
  const k = cam.k;
  const lo = Math.floor(lg(14 / k)), hi = Math.ceil(lg(800 / k));
  const inv = (sx, sy) => { const A = (sx - cam.ox) / (C30 * k), B = 2 * (sy - cam.oy) / k + 2 * z; return [(B - A) / 2, (A + B) / 2]; };
  const cs = [inv(0, 0), inv(W, 0), inv(0, H), inv(W, H)];
  const xmin = Math.min(...cs.map(c => c[0])), xmax = Math.max(...cs.map(c => c[0]));
  const ymin = Math.min(...cs.map(c => c[1])), ymax = Math.max(...cs.map(c => c[1]));
  ctx.fillStyle = COL.dot;
  for (let L = lo; L <= hi; L++) {
    const s = Math.pow(10, L), d = s * k;
    const a = sstep(14, 38, d) * (1 - sstep(320, 800, d)) * alpha;
    if (a < 0.01) continue;
    const r = 1.5 + 1.1 * sstep(60, 400, d);
    ctx.globalAlpha = a; ctx.beginPath();
    const i0 = Math.floor(xmin / s), i1 = Math.ceil(xmax / s), j0 = Math.floor(ymin / s), j1 = Math.ceil(ymax / s);
    if ((i1 - i0) * (j1 - j0) > 60000) continue;
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
      if (L < hi && (i % 10 === 0) && (j % 10 === 0) && sstep(14, 38, d * 10) * (1 - sstep(320, 800, d * 10)) > 0.01) continue;
      const x = i * s, y = j * s, sx = cam.px(x, y), sy = cam.py(x, y, z);
      if (sx < -4 || sx > W + 4 || sy < -4 || sy > H + 4) continue;
      ctx.moveTo(sx + r, sy); ctx.arc(sx, sy, r, 0, Math.PI * 2);
    }
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

// ---------- floating diorama board: top at z = 0, slab th thick, strata on the two front faces ----------
export function board(ctx, cam, x0, y0, sx, sy, th = 1, o = {}) {
  const x1 = x0 + sx, y1 = y0 + sy, Tb = T(o.color || COL.board), lift = o.lift ?? th * 1.4;
  // soft shadow on the paper below
  ctx.save(); ctx.filter = `blur(${Math.max(2, 0.5 * th * cam.k).toFixed(1)}px)`; ctx.globalAlpha = o.shadow ?? 0.22;
  poly(ctx, cam, [[x0 + 0.3, y0 + 0.3, -th - lift], [x1 + 0.6, y0 + 0.3, -th - lift], [x1 + 0.6, y1 + 0.6, -th - lift], [x0 + 0.3, y1 + 0.6, -th - lift]], 'rgb(70,52,40)', 0);
  ctx.restore();
  poly(ctx, cam, [[x1, y0, -th], [x1, y1, -th], [x1, y1, 0], [x1, y0, 0]], Tb.left);
  poly(ctx, cam, [[x0, y1, -th], [x1, y1, -th], [x1, y1, 0], [x0, y1, 0]], Tb.right);
  // strata bands where the section meets the edge
  const S = o.strata || COL.strata, n = S.length;
  for (let i = 0; i < n; i++) {
    const za = -th * (0.18 + i * 0.27), zb = za - th * 0.12;
    const Ts = T(S[i]);
    poly(ctx, cam, [[x1, y0, zb], [x1, y1, zb], [x1, y1, za], [x1, y0, za]], Ts.left, 0.6);
    poly(ctx, cam, [[x0, y1, zb], [x1, y1, zb], [x1, y1, za], [x0, y1, za]], Ts.right, 0.6);
  }
  poly(ctx, cam, [[x0, y0, 0], [x1, y0, 0], [x1, y1, 0], [x0, y1, 0]], o.top || Tb.top);
  // thin light rim on the top edge
  ctx.save(); ctx.strokeStyle = 'rgba(255,250,240,0.7)'; ctx.lineWidth = 1.4; ctx.beginPath();
  const a = cam.p(x1, y0, 0), b = cam.p(x1, y1, 0), c = cam.p(x0, y1, 0);
  ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.stroke(); ctx.restore();
}

// ---------- $100 bundles ----------
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
export function billTexture() {
  const c = document.createElement('canvas'); c.width = 1560; c.height = 663;
  const g = c.getContext('2d');
  g.fillStyle = COL.billTop; g.fillRect(0, 0, 1560, 663);
  g.strokeStyle = COL.billInk; g.lineWidth = 12; rr(g, 30, 30, 1500, 603, 26); g.stroke();
  g.lineWidth = 3; rr(g, 58, 58, 1444, 547, 18); g.stroke();
  g.globalAlpha = 0.22; g.lineWidth = 2;
  for (let x = 70; x < 1500; x += 14) { g.beginPath(); g.moveTo(x, 64); g.lineTo(x + 30, 100); g.stroke(); g.beginPath(); g.moveTo(x, 600); g.lineTo(x + 30, 564); g.stroke(); }
  g.globalAlpha = 1;
  g.fillStyle = '#CADCBB'; g.beginPath(); g.ellipse(560, 331, 170, 215, 0, 0, Math.PI * 2); g.fill();
  g.lineWidth = 9; g.strokeStyle = COL.billInk; g.stroke();
  g.lineWidth = 2.5; g.beginPath(); g.ellipse(560, 331, 140, 185, 0, 0, Math.PI * 2); g.stroke();
  g.fillStyle = '#4C82C7'; g.fillRect(968, 58, 44, 547);
  g.fillStyle = 'rgba(255,255,255,0.45)'; for (let y = 80; y < 590; y += 46) g.fillRect(976, y, 28, 14);
  g.fillStyle = '#B8763E'; rr(g, 1080, 300, 130, 130, 18); g.fill();
  g.fillStyle = '#D79A5C'; rr(g, 1106, 326, 78, 78, 12); g.fill();
  g.font = '600 150px Jost'; g.fillStyle = '#B8763E'; g.textAlign = 'right'; g.fillText('100', 1480, 590);
  g.font = '600 96px Jost'; g.fillStyle = COL.billInk; g.textAlign = 'left';
  g.fillText('100', 90, 170); g.textAlign = 'right'; g.fillText('100', 1470, 170);
  g.textAlign = 'left'; g.fillText('100', 90, 580);
  g.lineWidth = 6; g.strokeStyle = COL.billInk; g.beginPath(); g.arc(260, 360, 70, 0, Math.PI * 2); g.stroke();
  return c;
}
export function withStrap(bill) {
  const c = document.createElement('canvas'); c.width = 1560; c.height = 663;
  const g = c.getContext('2d');
  g.drawImage(bill, 0, 0);
  g.fillStyle = '#E3B44F'; g.fillRect(640, 0, 280, 663);
  g.fillStyle = 'rgba(120,80,20,0.25)'; g.fillRect(640, 0, 6, 663); g.fillRect(914, 0, 6, 663);
  g.save(); g.translate(780, 331); g.rotate(-Math.PI / 2);
  g.font = '600 92px Jost'; g.fillStyle = '#7A5418'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('$10,000', 0, 0); g.restore();
  return c;
}
export function sideTexture(w, base, line, strap) {
  const c = document.createElement('canvas'); c.width = w; c.height = 110;
  const g = c.getContext('2d');
  g.fillStyle = base; g.fillRect(0, 0, w, 110);
  const rnd = mulberry32(w);
  for (let y = 4; y < 106; y += 7) { g.fillStyle = line; g.globalAlpha = 0.25 + rnd() * 0.35; g.fillRect(0, y, w, 1.6); }
  g.globalAlpha = 1;
  if (strap) { g.fillStyle = strap; g.fillRect(640, 0, 280, 110); g.fillStyle = 'rgba(120,80,20,0.25)'; g.fillRect(640, 0, 280, 5); g.fillRect(640, 105, 280, 5); }
  g.fillStyle = 'rgba(40,50,30,0.18)'; g.fillRect(0, 0, w, 3);
  return c;
}
let MONEY = null;
export function money() {
  if (MONEY) return MONEY;
  const bill = billTexture();
  MONEY = {
    top: withStrap(bill), long: sideTexture(1560, COL.long, '#7FA86F', '#CF9A30'), end: sideTexture(663, COL.end, '#5D8655', null),
    Tl: T(COL.long), Te: T(COL.end), Ts: T(COL.strap), Tb: T(COL.billTop),
  };
  return MONEY;
}
// one $10,000 bundle centred at (x, y), bottom at z; s = scene units per metre (bundle 6.6 x 15.6 x 1.1 cm)
export const BUNDLE = { w: 0.0663, l: 0.156, t: 0.010922 };
export function bundle(ctx, cam, x, y, z, s, o = {}) {
  const M = money(), k = cam.k, sq = o.sq ?? 1;
  const bw = BUNDLE.w * s * (1 + (1 - sq) * 0.25), bl = BUNDLE.l * s * (1 + (1 - sq) * 0.12), t = BUNDLE.t * s * sq;
  const rot = o.rot || 0; // 0: long side along y; 1: long side along x
  const sxw = rot ? bl : bw, syl = rot ? bw : bl;
  const xa = x - sxw / 2, xb = x + sxw / 2, ya = y - syl / 2, yb = y + syl / 2, z1 = z + t;
  if (syl * k < 40 || o.flat) {
    box(ctx, cam, xa, ya, z, sxw, syl, t, { top: M.Tb.top, left: rot ? M.Te.left : M.Tl.left, right: rot ? M.Tl.left : M.Te.left }, 0.6);
    const sa = (rot ? x : y) - 0.019 * s, sb = (rot ? x : y) + 0.019 * s;
    if (!rot) {
      poly(ctx, cam, [[xb, sa, z], [xb, sb, z], [xb, sb, z1], [xb, sa, z1]], M.Ts.left, 0.5);
      poly(ctx, cam, [[xa, sa, z1], [xb, sa, z1], [xb, sb, z1], [xa, sb, z1]], M.Ts.top, 0.5);
    } else {
      poly(ctx, cam, [[sa, yb, z], [sb, yb, z], [sb, yb, z1], [sa, yb, z1]], M.Ts.left, 0.5);
      poly(ctx, cam, [[sa, ya, z1], [sb, ya, z1], [sb, yb, z1], [sa, yb, z1]], M.Ts.top, 0.5);
    }
    return;
  }
  if (!rot) {
    texQuad(ctx, M.long, cam.p(xb, ya, z1), [bl * C30 * k, bl * 0.5 * k], [0, t * k]);
    texQuad(ctx, M.end, cam.p(xa, yb, z1), [-bw * C30 * k, bw * 0.5 * k], [0, t * k]);
    texQuad(ctx, M.top, cam.p(xa, ya, z1), [bl * C30 * k, bl * 0.5 * k], [-bw * C30 * k, bw * 0.5 * k]);
  } else {
    texQuad(ctx, M.end, cam.p(xb, ya, z1), [bw * C30 * k, bw * 0.5 * k], [0, t * k]);
    texQuad(ctx, M.long, cam.p(xb, yb, z1), [-bl * C30 * k, bl * 0.5 * k], [0, t * k]);
    texQuad(ctx, M.top, cam.p(xb, ya, z1), [-bl * C30 * k, bl * 0.5 * k], [bw * C30 * k, bw * 0.5 * k]);
  }
}
// a neat pile of bundles: nx x ny bundles per layer, nz layers
export function pile(ctx, cam, x, y, z, s, nx, ny, nz, o = {}) {
  const dx = BUNDLE.w * s * 1.06, dy = BUNDLE.l * s * 1.03, dz = BUNDLE.t * s;
  const rnd = mulberry32(o.seed || 3);
  for (let l = 0; l < nz; l++) for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    const jx = (rnd() - 0.5) * 0.06 * dx, jy = (rnd() - 0.5) * 0.04 * dy;
    bundle(ctx, cam, x + (i - (nx - 1) / 2) * dx + jx, y + (j - (ny - 1) / 2) * dy + jy, z + l * dz, s, { flat: o.flat });
  }
}

// ---------- chip top: package, gold pins and die drawn on a block's top face ----------
let CHIP = null;
export function chipTexture() {
  if (CHIP) return CHIP;
  const c = document.createElement('canvas'); c.width = 256; c.height = 256;
  const g = c.getContext('2d');
  // gold pins along the four edges
  g.fillStyle = '#D9B25A';
  for (let i = 0; i < 9; i++) {
    const p = 40 + i * 22;
    g.fillRect(p, 10, 10, 26); g.fillRect(p, 220, 10, 26); g.fillRect(10, p, 26, 10); g.fillRect(220, p, 26, 10);
  }
  g.fillStyle = '#3A3450'; rr(g, 34, 34, 188, 188, 14); g.fill();
  g.fillStyle = '#4A4363'; rr(g, 44, 44, 168, 168, 10); g.fill();
  g.fillStyle = '#B9C0CF'; rr(g, 82, 82, 92, 92, 6); g.fill();
  g.fillStyle = '#D7DCE5'; rr(g, 82, 82, 92, 30, 6); g.fill();
  g.strokeStyle = 'rgba(58,52,80,0.35)'; g.lineWidth = 3;
  for (let i = 1; i < 4; i++) { g.beginPath(); g.moveTo(82 + i * 23, 90); g.lineTo(82 + i * 23, 166); g.stroke(); }
  CHIP = c; return c;
}
export function chipTop(ctx, cam, x0, y0, z, sx, sy, a = 1) {
  if (a <= 0.01) return;
  const [O, E1, E2] = faceFrame(cam, 'top', x0, y0, z - 0.0001, sx, sy, 0.0001);
  ctx.save(); ctx.globalAlpha = a; texQuad(ctx, chipTexture(), O, E1, E2); ctx.restore();
}

// ---------- price tag: a real paper tag on a string, drawn on a vertical plane facing +y ----------
const TAGS = new Map();
export function tagTexture(main, sub, color = COL.ink, size = 132) {
  const key = main + '|' + sub + '|' + color + '|' + size;
  if (TAGS.has(key)) return TAGS.get(key);
  const c = document.createElement('canvas'); c.width = 640; c.height = 300;
  const g = c.getContext('2d');
  // card with a cut corner end (string hole on the left)
  g.fillStyle = 'rgba(60,40,30,0.18)';
  tagPath(g, 10, 14, 620, 280); g.fill();
  g.fillStyle = COL.tag; tagPath(g, 4, 4, 620, 280); g.fill();
  g.strokeStyle = 'rgba(43,37,51,0.55)'; g.lineWidth = 4; tagPath(g, 4, 4, 620, 280); g.stroke();
  g.fillStyle = COL.paper; g.beginPath(); g.arc(70, 144, 20, 0, Math.PI * 2); g.fill();
  g.strokeStyle = '#C9A05A'; g.lineWidth = 8; g.beginPath(); g.arc(70, 144, 24, 0, Math.PI * 2); g.stroke();
  g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  g.font = `500 ${size}px Jost`; g.fillText(main, 365, sub ? 178 : 196);
  if (sub) { g.font = '600 40px Jost'; g.letterSpacing = '6px'; g.fillStyle = 'rgba(43,37,51,0.7)'; g.fillText(sub.toUpperCase(), 365, 246); g.letterSpacing = '0px'; }
  TAGS.set(key, c); return c;
}
function tagPath(g, x, y, w, h) {
  const c = h * 0.32;
  g.beginPath(); g.moveTo(x + c, y); g.lineTo(x + w - 18, y); g.quadraticCurveTo(x + w, y, x + w, y + 18);
  g.lineTo(x + w, y + h - 18); g.quadraticCurveTo(x + w, y + h, x + w - 18, y + h); g.lineTo(x + c, y + h); g.lineTo(x, y + h - c); g.lineTo(x, y + c); g.closePath();
}
// tag hung from world point (ax, ay, az); the card hangs below-right in the x-z plane at y = ay.
// w = card width in scene units; flip 0..1 turns the card over (text switches at 0.5); swing = small sway
export function tag(ctx, cam, ax, ay, az, w, a, b, o = {}) {
  const p = o.p ?? 1, flip = o.flip ?? 0;
  if (p <= 0) return;
  const tex = tagTexture(flip < 0.5 ? a : b, flip < 0.5 ? (o.subA ?? '') : (o.subB ?? ''), o.color);
  const h = w * 300 / 640, drop = (o.drop ?? 0.5) * w, sc = backOut(clamp(p / 0.6));
  const turn = Math.abs(Math.cos(flip * Math.PI));
  // card plane: x decreases to the right on screen (text rises to the right)
  const hx = ax - (o.dx ?? 0.25) * w, hz = az - drop;         // hole position
  const [hxs, hys] = cam.p(hx, ay, hz);
  ctx.save();
  ctx.globalAlpha = clamp(p * 3) * (o.a ?? 1);
  // string from the anchor to the hole
  const [sxa, sya] = cam.p(ax, ay, az);
  ctx.strokeStyle = COL.ink; ctx.lineWidth = Math.max(1.2, 0.012 * w * cam.k); ctx.beginPath(); ctx.moveTo(sxa, sya);
  ctx.quadraticCurveTo((sxa + hxs) / 2 - 4, Math.max(sya, hys) + 6, hxs, hys); ctx.stroke();
  // card: image (0..640, 0..300) with the hole at (70, 144)
  const k = cam.k, ex = [w * C30 * k * turn * sc, -w * 0.5 * k * turn * sc], ez = [0, h * k * sc];
  const sw = o.swing || 0;
  const ez2 = [ez[0] + sw * ez[1], ez[1]];
  const O = [hxs - ex[0] * 70 / 640 - ez2[0] * 144 / 300, hys - ex[1] * 70 / 640 - ez2[1] * 144 / 300];
  texQuad(ctx, tex, O, ex, ez2);
  if (turn < 0.999) { // darken the card while it is edge-on
    ctx.globalAlpha *= (1 - turn) * 0.35; ctx.fillStyle = COL.ink; ctx.beginPath();
    ctx.moveTo(O[0], O[1]); ctx.lineTo(O[0] + ex[0], O[1] + ex[1]); ctx.lineTo(O[0] + ex[0] + ez2[0], O[1] + ex[1] + ez2[1]); ctx.lineTo(O[0] + ez2[0], O[1] + ez2[1]); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

// ---------- share cube (one cube = 100 million Nvidia shares unless said otherwise) ----------
export function cube(ctx, cam, x, y, z, s, Tc, o = {}) {
  const h = s * (o.hs ?? 1), sq = o.sq ?? 1;
  const w = s * (1 + (1 - sq) * 0.3), hh = h * sq;
  box(ctx, cam, x - w / 2, y - w / 2, z, w, w, hh, Tc, 0.7);
  if (o.ghost > 0) dashedBox(ctx, cam, x - w / 2, y - w / 2, z + hh, w, w, (o.ghostH ?? 0), { a: o.ghost, color: o.ghostColor || COL.ink, lw: o.lw || 1.6, dash: o.dash || [5, 4], noBottom: true });
}

// ---------- data centre: long slate hall, rack-striped facade, roof fans ----------
let DCTEX = null;
function dcTexture() {
  if (DCTEX) return DCTEX;
  const c = document.createElement('canvas'); c.width = 512; c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = '#8C99AF'; g.fillRect(0, 0, 512, 128);
  for (let i = 0; i < 16; i++) {
    const x = 12 + i * 31;
    g.fillStyle = '#5F6B80'; g.fillRect(x, 20, 22, 92);
    for (let j = 0; j < 7; j++) { g.fillStyle = (i * 7 + j) % 5 === 0 ? '#BFF6FF' : '#7FE3F0'; g.fillRect(x + 4, 28 + j * 12, 4, 4); g.fillStyle = 'rgba(255,255,255,0.18)'; g.fillRect(x + 11, 29 + j * 12, 8, 2); }
  }
  g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(0, 0, 512, 6);
  DCTEX = c; return c;
}
export function dataCenter(ctx, cam, x0, y0, sx, sy, h, o = {}) {
  const r = o.rise ?? 1; if (r <= 0) return;
  const hh = h * r, Ts = T(COL.slate);
  box(ctx, cam, x0, y0, 0, sx, sy, hh, Ts, 0.7);
  // facade racks on both visible faces (the right face darker)
  let [O, E1, E2] = faceFrame(cam, 'x', x0, y0, 0, sx, sy, hh); texQuad(ctx, dcTexture(), O, E1, E2);
  [O, E1, E2] = faceFrame(cam, 'y', x0, y0, 0, sx, sy, hh); texQuad(ctx, dcTexture(), O, E1, E2);
  poly(ctx, cam, [[x0, y0 + sy, 0], [x0 + sx, y0 + sy, 0], [x0 + sx, y0 + sy, hh], [x0, y0 + sy, hh]], 'rgba(35,26,44,0.22)', 0);
  // roof fans
  const n = Math.max(1, Math.round(sy / 1.6)), m = Math.max(1, Math.round(sx / 1.6));
  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
    const cx = x0 + (i + 0.5) * sx / m, cy = y0 + (j + 0.5) * sy / n;
    box(ctx, cam, cx - 0.55, cy - 0.55, hh, 1.1, 1.1, 0.18, T('#9AA6BA'), 0.5);
    discZ(ctx, cam, cx, cy, hh + 0.19, 0.42, '#5F6B80');
    discZ(ctx, cam, cx, cy, hh + 0.2, 0.12, '#C9D2DF');
  }
}

// ---------- vault: steel block with a round door on its right (+y) face ----------
let VTEX = null;
function vaultTexture() {
  if (VTEX) return VTEX;
  const c = document.createElement('canvas'); c.width = 400; c.height = 400;
  const g = c.getContext('2d');
  g.fillStyle = COL.steel; g.fillRect(0, 0, 400, 400);
  g.fillStyle = '#98A2B2'; g.beginPath(); g.arc(200, 210, 150, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#C3CAD5'; g.beginPath(); g.arc(200, 210, 128, 0, Math.PI * 2); g.fill();
  g.strokeStyle = '#7D8798'; g.lineWidth = 6; g.beginPath(); g.arc(200, 210, 128, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = COL.brass; g.lineWidth = 14; g.lineCap = 'round';
  for (let i = 0; i < 3; i++) { const a = i * Math.PI * 2 / 3 + 0.4; g.beginPath(); g.moveTo(200, 210); g.lineTo(200 + Math.cos(a) * 80, 210 + Math.sin(a) * 80); g.stroke(); }
  g.fillStyle = COL.brass; g.beginPath(); g.arc(200, 210, 26, 0, Math.PI * 2); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.3)'; g.fillRect(0, 0, 400, 8);
  VTEX = c; return c;
}
export function vault(ctx, cam, x0, y0, s, h, o = {}) {
  const Tv = T(o.color || COL.steel);
  box(ctx, cam, x0, y0, 0, s, s, h, Tv, 0.7);
  if (o.door === 'x') {
    // door on the +x (left, lit) face
    const [O, E1, E2] = faceFrame(cam, 'x', x0, y0 + s * 0.12, h * 0.06, s, s * 0.76, h * 0.8);
    texQuad(ctx, vaultTexture(), O, E1, E2);
  } else {
    const [O, E1, E2] = faceFrame(cam, 'y', x0 + s * 0.12, y0, h * 0.06, s * 0.76, s, h * 0.8);
    texQuad(ctx, vaultTexture(), O, E1, E2);
    poly(ctx, cam, [[x0 + s * 0.12, y0 + s, h * 0.06], [x0 + s * 0.88, y0 + s, h * 0.06], [x0 + s * 0.88, y0 + s, h * 0.86], [x0 + s * 0.12, y0 + s, h * 0.86]], 'rgba(35,26,44,0.16)', 0);
  }
  // roof rim
  box(ctx, cam, x0 - 0.06 * s, y0 - 0.06 * s, h, s * 1.12, s * 1.12, 0.06 * s, T(o.rim || '#C9D0DA'), 0.5);
}

// ---------- route line between world points, drawn ahead of whatever travels on it ----------
export function routePts(pts, n = 48) {
  // smooth path through control points (Catmull-Rom), returns sampled world points + cumulative length
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let j = 0; j < n; j++) {
      const t = j / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1, 2].map(c => 0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3)));
    }
  }
  out.push(pts[pts.length - 1].slice());
  const L = [0];
  for (let i = 1; i < out.length; i++) L.push(L[i - 1] + Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1], out[i][2] - out[i - 1][2]));
  return { pts: out, L, len: L[L.length - 1] };
}
export function routeAt(R, u) {
  const d = clamp(u) * R.len; let i = 1;
  while (i < R.L.length - 1 && R.L[i] < d) i++;
  const a = R.pts[i - 1], b = R.pts[i], f = (d - R.L[i - 1]) / Math.max(1e-9, R.L[i] - R.L[i - 1]);
  return [lerp(a[0], b[0], f), lerp(a[1], b[1], f), lerp(a[2], b[2], f)];
}
export function routeDraw(ctx, cam, R, u0, u1, o = {}) {
  if (u1 <= u0) return;
  ctx.save(); ctx.globalAlpha = o.a ?? 1;
  ctx.strokeStyle = o.color || COL.ink; ctx.lineWidth = o.lw || 2.4; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (o.dash) { ctx.setLineDash(o.dash); ctx.lineDashOffset = o.offset || 0; }
  ctx.beginPath();
  const n = 80;
  for (let i = 0; i <= n; i++) { const p = routeAt(R, u0 + (u1 - u0) * i / n), [x, y] = cam.p(p[0], p[1], p[2]); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }
  ctx.stroke(); ctx.restore();
}
