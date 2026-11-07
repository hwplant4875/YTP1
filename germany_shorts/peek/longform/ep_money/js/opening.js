// Cold open, one take: $100 bundles slam onto the ground, the stack shoots up and the
// camera pulls out on a log zoom past the city, clouds, an airliner, the edge of space and
// the space station, ending on the curved Earth: $2.8 trillion = 3,058 km of $100 bills.
import {
  W, H, C30, SQ15, Cam, tones, rgb, css, mix, poly, box, frustum, texQuad, label, pin,
  clamp, lerp, sstep, smoother, easeOut, backOut, monotone, mulberry32,
} from './iso.js';
import { Globe, R_E } from './globe.js';

export const PAL = {
  paper: '#F2EADB', dot: '#CDBFA4', ink: '#2B2533', ocean: '#A9CDE2', space: '#1B2140', atmo: '#BFE3F5', cream: '#F4EEE2',
  billTop: '#DAE8CC', billInk: '#3F6B4B', long: '#95BE84', end: '#6E9A64', strap: '#D9A53A',
  bldg: ['#C3CAD2', '#B7C0CA', '#CCD1D6', '#B0B9C4', '#C9C6C2', '#D2C7BC'], tower: '#8FB0D2',
  tree: '#A5B99C', trunk: '#9D8775', cloud: '#FFFFFF', plane: '#E4E9EF', iss: '#CBD0D8', panel: '#46557E',
  hydrant: '#C7675B', lamp: '#5E5868', shadow: 'rgba(70,52,40,0.20)',
};

const BT = 0.010922;           // one $10,000 bundle = 100 bills x 0.10922 mm
const BL = 0.156, BW = 0.0663;  // bill length (along y) and width (along x), metres
const BILL_M = 0.10922e-3;      // one bill
export const TOPH = 2.8e12 / 100 * BILL_M;  // 3,058 km
export const DUR = 17.0;

// ---------------- timeline ----------------
const lg = Math.log10;
const TA = 2.8;                       // the camera starts tracking the stack top
const FALL = 0.26, DROP = 0.42, RAIN_END = 3.1;
// stack height over the whole take (log10 metres); bundles 0 and 1 lie on the ground at t=0
const topLog = monotone([
  [0, lg(2 * BT)], [1.0, lg(6 * BT)], [2.0, lg(12 * BT)], [TA, lg(24 * BT)], [4.0, lg(6 / 1.8)], [5.2, lg(100 / 1.8)],
  [6.3, lg(1100 / 1.8)], [7.4, lg(2.0e4 / 1.8)], [8.5, lg(1.8e5 / 1.8)], [9.7, lg(7.6e5 / 1.8)], [11.3, lg(TOPH)], [13, lg(TOPH)],
]);
const hv = (t) => Math.min(TOPH, Math.pow(10, topLog(t)));
// landing time of each bundle in the rain: bundle i lands when the stack reaches i+1 bundles
const LAND = [];
{ let i = 2; for (let t = 0; t < RAIN_END; t += 0.0005) { while (hv(t) >= (i + 1) * BT - 1e-9) { LAND[i] = t; i++; } } }
// camera frame height: slow drift during the first slams, then the stack top is held at a fixed
// screen height (frame = 1.8 x stack), then a last ease-out pull-back once the top is reached
const lc = (t) => lg(1.8) + (lg(2.35) - lg(1.8)) * smoother((t - 11) / 3.5) + (lg(2.42) - lg(2.35)) * smoother((t - 14.5) / 2.5);
const camKeys = [[0, lg(0.30)], [1.5, lg(0.33)]];
for (let t = TA; t <= 11.8; t += 0.4) camKeys.push([t, lc(t) + topLog(t)]);
const camLogA = monotone(camKeys);
const camLog = (t) => (t <= 11.4 ? camLogA(t) : lc(t) + topLog(t));
function stackTop(t) { return hv(t); }
function baseScreen(t) {
  const y = t < TA ? lerp(700, 930, smoother(t / TA)) : t < 10 ? 930 : lerp(930, 650, smoother((t - 10) / 4.5));
  const x = t < 10 ? 900 : lerp(900, 960, smoother((t - 10) / 4));
  return [x, y];
}

// ---------------- textures ----------------
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function billTexture() {
  const c = document.createElement('canvas'); c.width = 1560; c.height = 663;
  const g = c.getContext('2d');
  g.fillStyle = PAL.billTop; g.fillRect(0, 0, 1560, 663);
  g.strokeStyle = PAL.billInk; g.lineWidth = 12; rr(g, 30, 30, 1500, 603, 26); g.stroke();
  g.lineWidth = 3; rr(g, 58, 58, 1444, 547, 18); g.stroke();
  // fine guilloche hatching in the border band
  g.globalAlpha = 0.22; g.lineWidth = 2;
  for (let x = 70; x < 1500; x += 14) { g.beginPath(); g.moveTo(x, 64); g.lineTo(x + 30, 100); g.stroke(); g.beginPath(); g.moveTo(x, 600); g.lineTo(x + 30, 564); g.stroke(); }
  g.globalAlpha = 1;
  // portrait medallion (plain, stylised)
  g.fillStyle = '#CADCBB'; g.beginPath(); g.ellipse(560, 331, 170, 215, 0, 0, Math.PI * 2); g.fill();
  g.lineWidth = 9; g.strokeStyle = PAL.billInk; g.stroke();
  g.lineWidth = 2.5; g.beginPath(); g.ellipse(560, 331, 140, 185, 0, 0, Math.PI * 2); g.stroke();
  // blue security ribbon
  g.fillStyle = '#4C82C7'; g.fillRect(968, 58, 44, 547);
  g.fillStyle = 'rgba(255,255,255,0.45)'; for (let y = 80; y < 590; y += 46) g.fillRect(976, y, 28, 14);
  // copper inkwell + big 100
  g.fillStyle = '#B8763E'; rr(g, 1080, 300, 130, 130, 18); g.fill();
  g.fillStyle = '#D79A5C'; rr(g, 1106, 326, 78, 78, 12); g.fill();
  g.font = '600 150px Jost'; g.fillStyle = '#B8763E'; g.textAlign = 'right'; g.fillText('100', 1480, 590);
  g.font = '600 96px Jost'; g.fillStyle = PAL.billInk; g.textAlign = 'left';
  g.fillText('100', 90, 170); g.textAlign = 'right'; g.fillText('100', 1470, 170);
  g.textAlign = 'left'; g.fillText('100', 90, 580);
  // seal
  g.lineWidth = 6; g.strokeStyle = PAL.billInk; g.beginPath(); g.arc(260, 360, 70, 0, Math.PI * 2); g.stroke();
  return c;
}
function withStrap(bill) {
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
function sideTexture(w, base, line, strap) {
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

// ---------------- scene objects ----------------
function buildCity() {
  const rnd = mulberry32(2805), B = [];
  const bw = 64, bl = 150, sw = 22;
  for (let gx = -34; gx < 34; gx++) for (let gy = -16; gy < 16; gy++) {
    const x0 = gx * (bw + sw) + sw / 2, y0 = gy * (bl + sw) + sw / 2;
    const cx = x0 + bw / 2, cy = y0 + bl / 2, r = Math.hypot(cx, cy);
    if (r > 2900) continue;
    const park = rnd() < 0.05 && r > 250;
    if (park) { B.push({ park: true, x0: x0 + 2, y0: y0 + 2, sx: bw - 4, sy: bl - 4, h: 0.6, key: cx + cy }); continue; }
    const lots = rnd() < 0.55 ? 2 : 3;
    for (let l = 0; l < lots; l++) {
      const ly0 = y0 + l * bl / lots + 2.5 + rnd() * 3, ly1 = y0 + (l + 1) * bl / lots - 2.5 - rnd() * 3;
      const lx0 = x0 + 2 + rnd() * 5, lx1 = x0 + bw - 2 - rnd() * 5;
      const mx = (lx0 + lx1) / 2, my = (ly0 + ly1) / 2, rr = Math.hypot(mx, my);
      if (Math.abs(my - mx) < 56 || rr < 110) continue;       // avenue through the column + plaza
      if (Math.hypot(mx - 260, my + 330) < 75) continue;       // the tall tower's lot
      if (rnd() > Math.exp(-Math.pow(rr / 2100, 3))) continue; // the city thins out at its edge
      const d = Math.hypot(mx - 150, my + 150);
      let h = (14 + 120 * Math.exp(-d / 750)) * (0.5 + rnd() * 0.85) * (1 - 0.65 * sstep(900, 2600, rr));
      if (rnd() < 0.04 && d < 1400) h = Math.min(h * 1.9, 290);
      B.push({ x0: lx0, y0: ly0, sx: lx1 - lx0, sy: ly1 - ly0, h, T: tones(PAL.bldg[(rnd() * PAL.bldg.length) | 0]), key: mx + my });
    }
  }
  B.sort((a, b) => a.key - b.key);
  return B;
}
function buildClouds() {
  const rnd = mulberry32(42), C = [];
  for (let i = 0; i < 16; i++) {
    const a = rnd() * Math.PI * 2, r = 2500 + rnd() * 9000;
    const x = Math.cos(a) * r, y = Math.sin(a) * r;
    if (Math.abs(y - x) < 2600 && x + y > -4000) continue;   // keep the column's line of sight clear
    const puffs = [];
    const n = 4 + ((rnd() * 4) | 0), size = 500 + rnd() * 700;
    for (let j = 0; j < n; j++) puffs.push({ dx: (rnd() - 0.5) * size * 2.2, dy: (rnd() - 0.5) * size * 1.2, dz: rnd() * size * 0.35, r: size * (0.45 + rnd() * 0.45) });
    C.push({ x, y, z: 1500 + rnd() * 1100, puffs, key: x + y });
  }
  return C;
}
const TREES = [];
{ const rnd = mulberry32(9);
  for (let i = 0; i < 60 && TREES.length < 26; i++) {
    const a = rnd() * Math.PI * 2, r = 24 + rnd() * 70, x = Math.cos(a) * r, y = Math.sin(a) * r;
    if (Math.abs(y - x) < 24) continue;
    TREES.push({ x, y, h: 3.0 + rnd() * 1.6, r: 1.8 + rnd() * 0.8 }); } }

export class Opening {
  async init(assetBase) {
    this.cam = new Cam();
    this.globe = new Globe(); await this.globe.init(assetBase);
    const bill = billTexture();
    this.texTop = withStrap(bill);
    this.texLong = sideTexture(1560, PAL.long, '#7FA86F', '#CF9A30');
    this.texEnd = sideTexture(663, PAL.end, '#5D8655', null);
    this.city = buildCity(); this.clouds = buildClouds(); this.Tpark = tones('#C9D6B6');
    this.Tl = tones(PAL.long); this.Te = tones(PAL.end); this.Ts = tones(PAL.strap); this.Tb = tones(PAL.billTop);
    this.paper = rgb(PAL.paper); this.ocean = rgb(PAL.ocean); this.space = rgb(PAL.space); this.atmo = rgb(PAL.atmo);
    const rnd = mulberry32(5); this.jit = []; for (let i = 0; i < 400; i++) this.jit.push([(rnd() - 0.5) * 0.0045, (rnd() - 0.5) * 0.0045]);
  }

  // ---------- ground ----------
  lattice(ctx, alpha) {
    if (alpha <= 0.01) return;
    const cam = this.cam, k = cam.k;
    const lo = Math.floor(lg(14 / k)), hi = Math.ceil(lg(800 / k));
    const inv = (sx, sy) => { const A = (sx - cam.ox) / (C30 * k), B = 2 * (sy - cam.oy) / k; return [(B - A) / 2, (A + B) / 2]; };
    const cs = [inv(0, 0), inv(W, 0), inv(0, H), inv(W, H)];
    const xmin = Math.min(...cs.map(c => c[0])), xmax = Math.max(...cs.map(c => c[0]));
    const ymin = Math.min(...cs.map(c => c[1])), ymax = Math.max(...cs.map(c => c[1]));
    ctx.fillStyle = PAL.dot;
    for (let L = lo; L <= hi; L++) {
      const s = Math.pow(10, L), d = s * k;
      const a = sstep(14, 38, d) * (1 - sstep(320, 800, d)) * alpha;
      if (a < 0.01) continue;
      const r = 1.5 + 1.1 * sstep(60, 400, d);
      ctx.globalAlpha = a; ctx.beginPath();
      const i0 = Math.floor(xmin / s), i1 = Math.ceil(xmax / s), j0 = Math.floor(ymin / s), j1 = Math.ceil(ymax / s);
      if ((i1 - i0) * (j1 - j0) > 60000) continue;
      for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
        if (L < hi && (i % 10 === 0) && (j % 10 === 0) && sstep(14, 38, d * 10) * (1 - sstep(320, 800, d * 10)) > 0.01) continue; // drawn by the coarser level
        const x = i * s, y = j * s, sx = cam.px(x, y), sy = cam.py(x, y, 0);
        if (sx < -4 || sx > W + 4 || sy < -4 || sy > H + 4) continue;
        ctx.moveTo(sx + r, sy); ctx.arc(sx, sy, r, 0, Math.PI * 2);
      }
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  // ---------- the money ----------
  drawBundle(ctx, x0, y0, z0, sq = 1, tex = true) {
    const cam = this.cam, k = cam.k;
    const bw = BW * (1 + (1 - sq) * 0.25), bl = BL * (1 + (1 - sq) * 0.12), t = BT * sq;
    const xa = x0 - bw / 2, xb = x0 + bw / 2, ya = y0 - bl / 2, yb = y0 + bl / 2, z1 = z0 + t;
    if (!tex) {
      box(ctx, cam, xa, ya, z0, bw, bl, t, { top: this.Tb.top, left: this.Tl.left, right: this.Te.left });
      const sa = y0 - 0.019, sb = y0 + 0.019;
      poly(ctx, cam, [[xb, sa, z0], [xb, sb, z0], [xb, sb, z1], [xb, sa, z1]], this.Ts.left, 0.6);
      poly(ctx, cam, [[xa, sa, z1], [xb, sa, z1], [xb, sb, z1], [xa, sb, z1]], this.Ts.top, 0.6);
      return;
    }
    // long face (+x), end face (+y), top
    texQuad(ctx, this.texLong, cam.p(xb, ya, z1), [bl * C30 * k, bl * 0.5 * k], [0, t * k]);
    texQuad(ctx, this.texEnd, cam.p(xa, yb, z1), [-bw * C30 * k, bw * 0.5 * k], [0, t * k]);
    texQuad(ctx, this.texTop, cam.p(xa, ya, z1), [bl * C30 * k, bl * 0.5 * k], [-bw * C30 * k, bw * 0.5 * k]);
  }

  drawStack(ctx, t, h) {
    const cam = this.cam, k = cam.k, bk = BT * k;
    const discA = sstep(2.0, 3.0, bk);          // individual bundles fade over the solid column
    let f = 1;
    if (discA < 1) f = this.drawColumn(ctx, h);
    if (discA > 0) {
      const n = Math.floor(h / BT + 1e-9);
      ctx.save(); ctx.globalAlpha = discA; ctx.filter = `blur(${Math.max(1, 0.012 * k).toFixed(1)}px)`;
      poly(ctx, cam, [[-BW / 2 - 0.004, -BL / 2, 0], [BW / 2 + 0.01, -BL / 2, 0], [BW / 2 + 0.01, BL / 2 + 0.03, 0], [-BW / 2 - 0.004, BL / 2 + 0.03, 0]], PAL.shadow, 0);
      ctx.restore();
      const texA = sstep(5.5, 8.5, bk);
      for (let i = 0; i < n; i++) {
        let sq = 1;
        const lt = LAND[i];
        if (lt !== undefined) { const u = (t - lt) / 0.13; if (u >= 0 && u < 1) sq = 1 - 0.2 * Math.sin(Math.PI * u) * (1 - u * 0.5); }
        const j = this.jit[i % this.jit.length];
        if (texA < 1) { ctx.globalAlpha = discA; this.drawBundle(ctx, j[0], j[1], i * BT, sq, false); }
        if (texA > 0) { ctx.globalAlpha = discA * texA; this.drawBundle(ctx, j[0], j[1], i * BT, sq, true); }
      }
      ctx.globalAlpha = 1;
    }
    return { f };
  }

  // continuous column: footprint kept at least ~19 px wide on screen; returns the footprint scale
  drawColumn(ctx, h) {
    const cam = this.cam, k = cam.k;
    const f = Math.max(1, 19 / ((BW + BL) * C30 * k));
    const xa = -BW * f / 2, xb = BW * f / 2, ya = -BL * f / 2, yb = BL * f / 2, sa = -0.019 * f * 1.1, sb = 0.019 * f * 1.1;
    poly(ctx, cam, [[xb, ya, 0], [xb, yb, 0], [xb, yb, h], [xb, ya, h]], this.Tl.left);
    poly(ctx, cam, [[xb, sa, 0], [xb, sb, 0], [xb, sb, h], [xb, sa, h]], this.Ts.left, 0.6);
    poly(ctx, cam, [[xa, yb, 0], [xb, yb, 0], [xb, yb, h], [xa, yb, h]], this.Te.left);
    const la = sstep(1.0, 3.2, BT * k) * 0.45;
    if (la > 0.01) {
      ctx.save(); ctx.globalAlpha = la; ctx.strokeStyle = '#4E7046'; ctx.lineWidth = 1;
      const zTop = Math.min(h, (cam.oy + (xb + ya) * 0.5 * k) / k), zBot = Math.max(0, (cam.oy - H + (xb + yb) * 0.5 * k) / k);
      ctx.beginPath();
      for (let z = Math.ceil(zBot / BT) * BT; z < zTop; z += BT) {
        ctx.moveTo(cam.px(xb, ya), cam.py(xb, ya, z)); ctx.lineTo(cam.px(xb, yb), cam.py(xb, yb, z)); ctx.lineTo(cam.px(xa, yb), cam.py(xa, yb, z));
      }
      ctx.stroke(); ctx.restore();
    }
    if (BL * f * k > 90) texQuad(ctx, this.texTop, cam.p(xa, ya, h), [BL * f * C30 * k, BL * f * 0.5 * k], [-BW * f * C30 * k, BW * f * 0.5 * k]);
    else {
      poly(ctx, cam, [[xa, ya, h], [xb, ya, h], [xb, yb, h], [xa, yb, h]], this.Tb.top);
      poly(ctx, cam, [[xa, sa, h], [xb, sa, h], [xb, sb, h], [xa, sb, h]], this.Ts.top, 0.6);
    }
    return f;
  }

  drawFalling(ctx, t) {
    if (t >= RAIN_END + FALL) return;
    const texOn = BT * this.cam.k > 5.5;
    for (let i = 2; i < LAND.length; i++) {
      const lt = LAND[i], u = (t - (lt - FALL)) / FALL;
      if (u < 0 || u >= 1) continue;
      const z = i * BT + DROP * (1 - u * u);
      const j = this.jit[i % this.jit.length];
      this.drawBundle(ctx, j[0], j[1], z, 1, texOn);
    }
  }

  // ---------- context props ----------
  drawTaxi(ctx, a) {
    if (a <= 0.01) return;
    const cam = this.cam, x0 = 5.2, y0 = -6.2, Ty = tones('#E8C24C'), Tg = tones('#55617A'), Tw = tones('#302B37'), Ts = tones('#F4F1EA');
    ctx.globalAlpha = a;
    box(ctx, cam, x0 + 1.75, y0 + 0.65, 0, 0.22, 0.7, 0.62, Tw); box(ctx, cam, x0 + 1.75, y0 + 3.55, 0, 0.22, 0.7, 0.62, Tw);
    box(ctx, cam, x0, y0, 0.28, 1.9, 4.8, 0.66, Ty);
    box(ctx, cam, x0 + 0.12, y0 + 1.35, 0.94, 1.66, 2.25, 0.5, Tg);
    box(ctx, cam, x0 + 0.1, y0 + 1.3, 1.42, 1.7, 2.35, 0.1, Ty);
    box(ctx, cam, x0 + 0.65, y0 + 2.2, 1.52, 0.6, 0.5, 0.22, Ts);
    ctx.globalAlpha = 1;
  }
  drawProps(ctx, a) {
    if (a <= 0.01) return;
    const cam = this.cam; ctx.globalAlpha = a;
    // hydrant
    const Th = tones(PAL.hydrant);
    box(ctx, cam, 2.1, -2.45, 0, 0.3, 0.3, 0.62, Th); box(ctx, cam, 2.05, -2.5, 0.62, 0.4, 0.4, 0.08, Th); box(ctx, cam, 2.15, -2.4, 0.7, 0.2, 0.2, 0.12, Th);
    // lamp post
    const Tl = tones(PAL.lamp);
    box(ctx, cam, 3.6, -1.1, 0, 0.16, 0.16, 4.6, Tl); box(ctx, cam, 3.0, -1.1, 4.6, 0.8, 0.16, 0.12, Tl); box(ctx, cam, 2.95, -1.18, 4.42, 0.3, 0.32, 0.18, tones('#F1D98A'));
    ctx.globalAlpha = 1;
  }
  drawTrees(ctx, a) {
    if (a <= 0.01) return;
    const cam = this.cam, k = cam.k, Tt = tones(PAL.trunk), Tc = tones(PAL.tree);
    ctx.globalAlpha = a;
    const list = TREES.slice().sort((p, q) => (p.x + p.y) - (q.x + q.y));
    for (const tr of list) {
      box(ctx, cam, tr.x - 0.18, tr.y - 0.18, 0, 0.36, 0.36, tr.h, Tt);
      const [cx, cy] = cam.p(tr.x, tr.y, tr.h + tr.r * 0.55), r = tr.r * k * SQ15 * 0.82;
      ctx.fillStyle = Tc.right; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.clip();
      ctx.fillStyle = Tc.left; ctx.beginPath(); ctx.arc(cx - r * 0.18, cy - r * 0.2, r * 0.9, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = Tc.top; ctx.beginPath(); ctx.arc(cx - r * 0.38, cy - r * 0.42, r * 0.55, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
    ctx.globalAlpha = 1;
  }
  drawCity(ctx, a, drawColumn) {
    const cam = this.cam, k = cam.k;
    let colDone = false;
    const tower = { key: -70 };
    const items = this.city;
    ctx.globalAlpha = a;
    for (let i = 0; i <= items.length; i++) {
      const b = items[i];
      const key = b ? b.key : Infinity;
      if (!tower.done && tower.key <= key) { this.drawTower(ctx); tower.done = true; }
      if (!colDone && key > 0) { ctx.globalAlpha = 1; drawColumn(); ctx.globalAlpha = a; colDone = true; }
      if (!b) break;
      if (b.h * k < 1.2 && b.sx * k < 1.2) continue;
      const sx = cam.px(b.x0 + b.sx, b.y0), ex = cam.px(b.x0, b.y0 + b.sy);
      if (ex < -10 || sx > W + 10) continue;
      const ty = cam.py(b.x0, b.y0, b.h), by = cam.py(b.x0 + b.sx, b.y0 + b.sy, 0);
      if (by < -10 || ty > H + 10) continue;
      if (b.park) { box(ctx, cam, b.x0, b.y0, 0, b.sx, b.sy, b.h, this.Tpark, 0.7); continue; }
      box(ctx, cam, b.x0, b.y0, 0, b.sx, b.sy, b.h, b.T, 0.7);
    }
    tower.done = false;
    ctx.globalAlpha = 1;
  }
  drawTower(ctx) {
    const cam = this.cam, T = tones(PAL.tower);
    const cx = 260, cy = -330;
    box(ctx, cam, cx - 31, cy - 31, 0, 62, 62, 58, T, 0.7);
    frustum(ctx, cam, cx, cy, 58, 417, 31, 20, T);
    box(ctx, cam, cx - 9, cy - 9, 417, 18, 18, 14, tones('#8AA7C6'));
    box(ctx, cam, cx - 1.6, cy - 1.6, 431, 3.2, 3.2, 110, tones('#7E95AF'));
  }
  drawClouds(ctx, a, behind) {
    if (a <= 0.01) return;
    const cam = this.cam, k = cam.k;
    for (const c of this.clouds) {
      if ((c.key < 0) !== behind) continue;
      const pts = c.puffs.map(p => { const [x, y] = cam.p(c.x + p.dx, c.y + p.dy, c.z + p.dz); return [x, y, p.r * k * SQ15 * 0.75]; });
      const mxr = Math.max(...pts.map(p => p[2]));
      if (mxr < 1.5) continue;
      if (pts.every(p => p[0] + p[2] < 0 || p[0] - p[2] > W || p[1] + p[2] < 0 || p[1] - p[2] > H)) continue;
      ctx.globalAlpha = a;
      ctx.fillStyle = '#DCE5EE'; ctx.beginPath(); for (const p of pts) { ctx.moveTo(p[0] + p[2], p[1] + p[2] * 0.22); ctx.arc(p[0], p[1] + p[2] * 0.22, p[2], 0, Math.PI * 2); } ctx.fill();
      ctx.fillStyle = '#EEF3F7'; ctx.beginPath(); for (const p of pts) { ctx.moveTo(p[0] + p[2], p[1]); ctx.arc(p[0], p[1], p[2], 0, Math.PI * 2); } ctx.fill();
      ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); for (const p of pts) { ctx.moveTo(p[0] - p[2] * 0.12 + p[2] * 0.82, p[1] - p[2] * 0.16); ctx.arc(p[0] - p[2] * 0.12, p[1] - p[2] * 0.16, p[2] * 0.82, 0, Math.PI * 2); } ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  // icons: unit models drawn with their own camera scale, anchored in screen space
  drawPlane(ctx, ax, ay, size, a) {
    if (a <= 0.01 || size < 3) return;
    const c = new Cam(); c.set(ax, ay, size); ctx.globalAlpha = a;
    const Tp = tones(PAL.plane), Tw = tones('#D3DAE2'), Tf = tones('#7F93B5');
    // nose points -y (screen up-left). fuselage, wings, tail
    box(ctx, c, -0.42, 0.02, -0.02, 0.84, 0.03, 0.012, Tw);            // wing
    box(ctx, c, -0.16, 0.42, 0.02, 0.32, 0.06, 0.01, Tw);               // stabiliser
    box(ctx, c, -0.05, -0.5, -0.05, 0.10, 1.0, 0.10, Tp);               // fuselage
    box(ctx, c, -0.01, 0.38, 0.05, 0.02, 0.12, 0.16, Tf);               // fin
    ctx.globalAlpha = 1;
  }
  drawISS(ctx, ax, ay, size, a) {
    if (a <= 0.01 || size < 3) return;
    const c = new Cam(); c.set(ax, ay, size); ctx.globalAlpha = a;
    const Tt = tones(PAL.iss), Tp = tones(PAL.panel), Tm = tones('#E6E9EE'), Tr = tones('#F2F4F6');
    for (const xc of [-0.45, -0.31]) { box(ctx, c, xc - 0.05, -0.44, 0, 0.1, 0.4, 0.008, Tp); }
    box(ctx, c, -0.5, -0.02, -0.02, 1.0, 0.04, 0.04, Tt);                // truss
    box(ctx, c, -0.045, -0.26, -0.045, 0.09, 0.56, 0.09, Tm);            // modules
    box(ctx, c, -0.17, 0.05, 0, 0.07, 0.18, 0.006, Tr); box(ctx, c, 0.1, 0.05, 0, 0.07, 0.18, 0.006, Tr);
    for (const xc of [-0.45, -0.31, 0.31, 0.45]) { box(ctx, c, xc - 0.05, 0.04, 0, 0.1, 0.4, 0.008, Tp); }
    for (const xc of [0.31, 0.45]) { box(ctx, c, xc - 0.05, -0.44, 0, 0.1, 0.4, 0.008, Tp); }
    ctx.globalAlpha = 1;
  }

  // ---------- frame ----------
  render(ctx, t) {
    const cam = this.cam;
    const Hm = Math.pow(10, camLog(t)), k = H / Hm;
    const [bx, by] = baseScreen(t);
    cam.set(bx, by, k);
    const h = stackTop(t), lH = lg(Hm);

    // background: plain paper, or the per-pixel Earth once the map or the limb shows
    const mapA = sstep(lg(2.5e4), lg(1.0e5), lH);
    if (mapA > 0.001) this.globe.render(ctx, cam, { mapA, paper: this.paper, ocean: this.ocean, space: this.space, atmo: this.atmo, starA: sstep(lg(1.2e6), lg(3e6), lH) });
    else { ctx.fillStyle = PAL.paper; ctx.fillRect(0, 0, W, H); }

    this.lattice(ctx, 1 - sstep(lg(1.5e4), lg(6e4), lH));

    const propsA = sstep(lg(0.45), lg(0.9), lH) * (1 - sstep(lg(40), lg(140), lH));
    const treeA = sstep(lg(8), lg(20), lH) * (1 - sstep(lg(260), lg(800), lH));
    const taxiA = sstep(lg(2), lg(5), lH) * (1 - sstep(lg(120), lg(300), lH));
    const cityA = 1 - sstep(lg(8e3), lg(2.5e4), lH);
    const cloudA = sstep(lg(700), lg(2200), lH) * (1 - sstep(lg(3e4), lg(9e4), lH));

    // Karman ring (back half), clouds behind
    const ringT = clamp((t - 8.05) / 0.7), ringA = sstep(lg(4e4), lg(9e4), lH) * (1 - sstep(lg(1.2e6), lg(2.4e6), lH));
    const ringR = 70e3;
    const ring = (front) => {
      if (ringA < 0.01 || ringT <= 0) return;
      const [cx, cy] = cam.p(0, 0, 100e3), rx = ringR * SQ15 * k, ry = ringR * Math.SQRT1_2 * k;
      ctx.save(); ctx.globalAlpha = ringA; ctx.strokeStyle = PAL.ink; ctx.lineWidth = 2.4; ctx.setLineDash([10, 9]);
      ctx.beginPath();
      const a0 = front ? 0 : Math.PI, span = Math.PI * ringT;
      ctx.ellipse(cx, cy, rx, ry, 0, a0, a0 + span); ctx.stroke(); ctx.restore();
    };
    ring(false);
    this.drawClouds(ctx, cloudA, true);

    const drawColumn = () => {
      const r = this.drawStack(ctx, t, h);
      this.colF = r.f;
      if (t < RAIN_END + FALL) this.drawFalling(ctx, t);
    };
    if (cityA > 0.01) this.drawCity(ctx, cityA, drawColumn); else drawColumn();
    this.drawTrees(ctx, treeA);
    this.drawTaxi(ctx, taxiA);
    this.drawProps(ctx, propsA);
    this.drawClouds(ctx, cloudA, false);
    ring(true);

    // airliner (flies toward screen up-left)
    const plA = sstep(lg(4e3), lg(9e3), lH) * (1 - sstep(lg(1.1e5), lg(3e5), lH));
    if (plA > 0.01) {
      const py = -4600 - 950 * (t - 7.4), [ax, ay] = cam.p(2800, py, 11000);
      const size = 118 * Math.pow(k / (H / 2.0e4), 0.45);
      this.drawPlane(ctx, ax, ay, size, plA);
      this.planeAnchor = [ax, ay, size];
    }

    // space station: glides in from the left, then becomes the first of seven
    const issIn = easeOut((t - 9.2) / 0.7);
    const kPass = H / 7.6e5;
    const sizeAt = (kk) => 125 * Math.pow(kk / kPass, 0.47);
    const issSize = sizeAt(k);
    const [cx420, cy420] = cam.p(0, 0, 420e3);
    const off = 0.95 * issSize + 26 * Math.pow(k / kPass, 0.3);
    let issX = cx420 - off - (1 - issIn) * 900, issY = cy420;
    if (t > 9.2) this.drawISS(ctx, issX, issY, issSize, 1);

    // seven stations up the column
    if (t > 11.9) {
      const cols = [];
      for (let i = 2; i <= 7; i++) {
        const tp = 12.0 + (i - 2) * 0.3, p = clamp((t - tp) / 0.45);
        if (p <= 0) continue;
        const [cx, cy] = cam.p(0, 0, 420e3 * i);
        const s = issSize * backOut(p);
        cols.push([cx, cy, s, p]);
      }
      for (const [cx, cy, s, p] of cols) {
        // tick line leads the icon
        const sp = this.skyMix(cy);
        ctx.strokeStyle = css(mix(rgb(PAL.ink), rgb(PAL.cream), sp)); ctx.lineWidth = 2; ctx.globalAlpha = clamp(p * 2);
        ctx.beginPath(); ctx.moveTo(cx - 12, cy); ctx.lineTo(cx - 12 - (off - 14) * easeOut(p * 1.6), cy); ctx.stroke(); ctx.globalAlpha = 1;
        this.drawISS(ctx, cx - off, cy, s, clamp(p * 3));
      }
    }

    this.drawPins(ctx, t, h, Hm, { issX, issY, issSize, off });
  }

  // 0 on the ground, 1 against space, by screen height relative to the Earth's glowing limb
  skyMix(y) {
    const cam = this.cam, limb = cam.oy - (SQ15 - 1) * R_E * cam.k, glow = 0.024 * R_E * SQ15 * cam.k;
    return sstep(limb - glow * 0.5, limb - glow - 60, y);
  }
  pinColors(y) {
    const s = this.skyMix(y), ha = Math.abs(1 - 2 * s);
    return {
      ink: css(mix(rgb(PAL.ink), rgb(PAL.cream), s)),
      paper: css(s < 0.5 ? rgb(PAL.paper) : rgb(PAL.space)),
      halo: css(s < 0.5 ? rgb(PAL.paper) : rgb(PAL.space), Math.max(0.001, ha)),
    };
  }

  drawPins(ctx, t, h, Hm, iss) {
    const cam = this.cam, k = cam.k, f = this.colF || 1;
    // running readout at the stack top (right corner of the top face)
    const [ax, ay] = cam.p(-BW * f / 2, BL * f / 2, h);
    const dollars = h / BILL_M * 100;
    const [num, unit] = fmtMoney(dollars, t < RAIN_END ? Math.floor(h / BT + 1e-9) * 1e4 : null, h >= TOPH * 0.9995);
    const c = this.pinColors(ay - 80);
    pin(ctx, ax + 4, ay, { ...c, dir: 1, lead: 70, rule: 360, num, unit, numSize: 76, title: fmtHeight(h), titleSize: 26 });

    // landmark pins (left side)
    const show = (t0, t1) => clamp((t - t0) / 0.6) * (1 - clamp((t - t1) / 0.35));
    const towerP = show(5.85, 7.25);
    if (towerP > 0) {
      const [x, y] = cam.p(260, -330, 541);
      pin(ctx, x, y, { ...this.pinColors(y - 60), p: clamp((t - 5.85) / 0.6), a: 1 - clamp((t - 7.25) / 0.35), dir: -1, lead: 54, rule: 300, num: '541', unit: 'M', title: 'Tallest U.S. building', numSize: 60, titleSize: 22 });
    }
    if (this.planeAnchor && t > 7.15 && t < 8.6) {
      const [x, y, s] = this.planeAnchor;
      pin(ctx, x - s * 0.12, y - s * 0.08, { ...this.pinColors(y - 60), p: clamp((t - 7.2) / 0.6), a: 1 - clamp((t - 8.2) / 0.35), dir: -1, lead: 54, rule: 280, num: '11', unit: 'KM', title: 'Airliner', numSize: 60, titleSize: 22 });
    }
    if (t > 8.3 && t < 9.9) {
      const [cx, cy] = cam.p(0, 0, 100e3), rx = 70e3 * SQ15 * k;
      pin(ctx, cx - rx, cy, { ...this.pinColors(cy - 60), p: clamp((t - 8.35) / 0.6), a: 1 - clamp((t - 9.5) / 0.35), dir: -1, lead: 54, rule: 300, num: '100', unit: 'KM', title: 'Edge of space', numSize: 60, titleSize: 22 });
    }
    if (t > 9.7 && t < 12.2) {
      const x = iss.issX - iss.issSize * 0.55, y = iss.issY;
      pin(ctx, x, y, { ...this.pinColors(y - 60), p: clamp((t - 9.75) / 0.6), a: 1 - clamp((t - 11.8) / 0.35), dir: -1, lead: 54, rule: 300, num: '420', unit: 'KM', title: 'Space station', numSize: 60, titleSize: 22 });
    }
    // "7x" call-out once all seven stations are up
    if (t > 13.7) {
      const p = clamp((t - 13.75) / 0.7);
      const [cx, cy] = cam.p(0, 0, 420e3 * 7);
      const x = cx - iss.off - iss.issSize * 0.75, y = cy;
      pin(ctx, x, y, { ...this.pinColors(y - 60), p, dir: -1, lead: 1, rule: 1, dot: 0.001, num: '7×', title: 'higher than the space station', numSize: 70, titleSize: 22 });
    }
    if (t > 12.6) {
      const p = clamp((t - 12.6) / 0.7);
      const [bx, byy] = cam.p(0, 0, 0);
      pin(ctx, bx, byy, { ...this.pinColors(byy + 40), p, dir: 1, lead: -54, rule: 170, dot: 6, title: 'New York', titleSize: 20 });
    }
  }
}

function commas(n) { return Math.round(n).toLocaleString('en-US'); }
function sig3(v) { const s = v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2); return s.includes('.') ? s.replace(/0+$/, '').replace(/\.$/, '') : s; }
function fmtMoney(d, exact, final) {
  if (final) return ['$2.8', 'TRILLION'];
  if (exact !== null) return ['$' + commas(exact), ''];
  if (d < 1e6) { const p = Math.pow(10, Math.floor(Math.log10(d)) - 2); return ['$' + commas(Math.round(d / p) * p), '']; }
  for (const [u, n] of [[1e12, 'TRILLION'], [1e9, 'BILLION'], [1e6, 'MILLION']]) if (d >= u) return ['$' + sig3(d / u), n];
}
function fmtHeight(h) {
  if (h < 1) return `${(h * 100).toFixed(h < 0.1 ? 1 : 0)} cm tall`;
  if (h < 1000) return `${h < 10 ? h.toFixed(1) : commas(h)} m tall`;
  const km = h / 1000;
  return `${km < 10 ? km.toFixed(1) : commas(km)} km tall`;
}
