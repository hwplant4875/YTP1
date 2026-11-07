// Per-pixel orthographic Earth for the iso camera. The scene origin is the column base
// (lower Manhattan); the Earth centre sits at (0, 0, -R). Land masks are rasterised
// Natural Earth polygons (public domain), mip-mapped for clean minification.
import { W, H, SQ15, rgb, mulberry32 } from './iso.js';

export const R_E = 6371000;
export const BASE = { lat: 40.7069, lon: -74.0113 };

async function loadMip(url) {
  const blob = await fetch(url).then(r => r.blob());
  const bmp = await createImageBitmap(blob, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' });
  const c = new OffscreenCanvas(bmp.width, bmp.height);
  const g = c.getContext('2d', { willReadFrequently: true });
  g.drawImage(bmp, 0, 0);
  const src = g.getImageData(0, 0, bmp.width, bmp.height).data;
  let w = bmp.width, h = bmp.height;
  const d0 = new Float32Array(w * h);
  for (let i = 0, j = 0; i < d0.length; i++, j += 4) d0[i] = src[j] / 255;
  const levels = [{ w, h, d: d0 }];
  while (w > 64 && h > 64) {
    const pw = w, prev = levels[levels.length - 1].d;
    w = w >> 1; h = h >> 1;
    const d = new Float32Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = (2 * y) * pw + 2 * x;
      d[y * w + x] = (prev[i] + prev[i + 1] + prev[i + pw] + prev[i + pw + 1]) * 0.25;
    }
    levels.push({ w, h, d });
  }
  return levels;
}

function bilin(L, fx, fy) {
  const w = L.w, h = L.h, d = L.d;
  if (fx < 0) fx = 0; if (fy < 0) fy = 0;
  if (fx > w - 1.001) fx = w - 1.001; if (fy > h - 1.001) fy = h - 1.001;
  const x0 = fx | 0, y0 = fy | 0, tx = fx - x0, ty = fy - y0, i = y0 * w + x0;
  const a = d[i] + (d[i + 1] - d[i]) * tx, b = d[i + w] + (d[i + w + 1] - d[i + w]) * tx;
  return a + (b - a) * ty;
}

export class Globe {
  async init(base) {
    this.g = await loadMip(base + 'land_global.png');
    this.r = await loadMip(base + 'land_ne.png');
    this.img = new ImageData(W, H);
    const D = Math.PI / 180, f = BASE.lat * D, l = BASE.lon * D;
    this.U = [Math.cos(f) * Math.cos(l), Math.cos(f) * Math.sin(l), Math.sin(f)];
    this.E = [-Math.sin(l), Math.cos(l), 0];
    this.N = [-Math.sin(f) * Math.cos(l), -Math.sin(f) * Math.sin(l), Math.cos(f)];
    // star field (screen space), alpha 0..1
    const c = new OffscreenCanvas(W, H), g = c.getContext('2d', { willReadFrequently: true });
    const rnd = mulberry32(77);
    g.fillStyle = '#fff';
    for (let y = 0; y < H; y += 46) for (let x = 0; x < W; x += 46) {
      if (rnd() > 0.5) continue;
      const r = 0.8 + rnd() * 1.5;
      g.globalAlpha = 0.25 + rnd() * 0.6;
      g.beginPath(); g.arc(x + rnd() * 46, y + rnd() * 46, r, 0, Math.PI * 2); g.fill();
    }
    const sd = g.getImageData(0, 0, W, H).data;
    this.stars = new Float32Array(W * H);
    for (let i = 0; i < this.stars.length; i++) this.stars[i] = sd[i * 4 + 3] / 255;
  }

  // sample land (0..1) with trilinear mip selection; texScreen = screen px per level-0 texel
  _land(levels, fx, fy, texScreen) {
    let lod = texScreen >= 1 ? 0 : Math.log2(1 / texScreen);
    const maxL = levels.length - 2;
    if (lod > maxL) lod = maxL;
    const l0 = Math.floor(lod), fr = lod - l0;
    const s0 = Math.pow(2, l0);
    let v = bilin(levels[l0], (fx + 0.5) / s0 - 0.5, (fy + 0.5) / s0 - 0.5);
    let sharp0 = Math.max(1, texScreen * s0);
    let a = (v - 0.5) * sharp0 * 1.15 + 0.5; a = a < 0 ? 0 : a > 1 ? 1 : a;
    if (fr > 0.001) {
      const s1 = s0 * 2;
      const v1 = bilin(levels[l0 + 1], (fx + 0.5) / s1 - 0.5, (fy + 0.5) / s1 - 0.5);
      let b = (v1 - 0.5) * Math.max(1, texScreen * s1) * 1.15 + 0.5; b = b < 0 ? 0 : b > 1 ? 1 : b;
      a = a + (b - a) * fr;
    }
    return a;
  }

  // o: { mapA (0..1 map visibility), paper, ocean, space, atmo, starA }
  render(ctx, cam, o) {
    const R = R_E, k = cam.k, S = SQ15 * k, ox = cam.ox, oy = cam.oy;
    const data = this.img.data;
    const i2 = 1 / Math.SQRT2, i6 = 1 / Math.sqrt(6), i3 = 1 / Math.sqrt(3);
    const PAP = o.paper, OCE = o.ocean, SPA = o.space, ATM = o.atmo, mapA = o.mapA;
    const U = this.U, E = this.E, N = this.N;
    const texG = (2 * Math.PI * R / this.g[0].w) * S, texR = (0.004 * Math.PI / 180 * R) * S;
    const gw = this.g[0].w, gh = this.g[0].h, rw = this.r[0].w, rh = this.r[0].h;
    // light from upper-left-front, in scene coords
    let Lx = 0.6 * i2 - 0.6 * i6 + 0.5 * i3, Ly = -0.6 * i2 - 0.6 * i6 + 0.5 * i3, Lz = 1.2 * i6 + 0.5 * i3;
    const ln = Math.hypot(Lx, Ly, Lz); Lx /= ln; Ly /= ln; Lz /= ln;
    const RD = 180 / Math.PI, atmT = 0.024 * R, starA = o.starA;
    const R2_3 = R * R / 3, sR3 = R * i3;
    for (let j = 0; j < H; j++) {
      const b = -(j + 0.5 - oy) / S;
      for (let i = 0; i < W; i++) {
        const a = (i + 0.5 - ox) / S;
        const px = -a * i2 - b * i6, py = a * i2 - b * i6, pz = 2 * b * i6;
        const disc = R2_3 - (a * a + b * b) - 2 * R * pz;
        let r, g, bl;
        const q = (j * W + i) * 4;
        if (disc >= 0) {
          const s = -sR3 + Math.sqrt(disc), si = s * i3;
          const nx = (px + si) / R, ny = (py + si) / R, nz = (pz + R + si) / R;
          let lr = 1;
          if (mapA > 0.001) {
            const e = (ny - nx) * i2, nn = -(nx + ny) * i2;
            const X = e * E[0] + nn * N[0] + nz * U[0], Y = e * E[1] + nn * N[1] + nz * U[1], Z = e * E[2] + nn * N[2] + nz * U[2];
            const lat = Math.asin(Z > 1 ? 1 : Z < -1 ? -1 : Z) * RD, lon = Math.atan2(Y, X) * RD;
            let land;
            if (lon > -81.9 && lon < -62.1 && lat > 32.1 && lat < 49.9) {
              land = this._land(this.r, (lon + 82) / 20 * rw - 0.5, (50 - lat) / 18 * rh - 0.5, texR);
            } else {
              land = this._land(this.g, (lon + 180) / 360 * gw - 0.5, (90 - lat) / 180 * gh - 0.5, texG);
            }
            const dB = R * Math.sqrt(Math.max(0, 2 * (1 - nz)));   // distance from the column base
            if (dB < 3000) land = Math.max(land, 1 - Math.max(0, (dB - 1500) / 1500));
            lr = 1 - mapA * (1 - land);
          }
          const sh = 1 + 0.07 * ((nx * Lx + ny * Ly + nz * Lz) - Lz) + 0.08 * ((nx + ny + nz) * i3 - i3);
          r = (OCE[0] + (PAP[0] - OCE[0]) * lr) * sh;
          g = (OCE[1] + (PAP[1] - OCE[1]) * lr) * sh;
          bl = (OCE[2] + (PAP[2] - OCE[2]) * lr) * sh;
          const rim = 1 - (nx + ny + nz) * i3;
          if (rim > 0.5) {
            const t = Math.pow((rim - 0.5) * 2, 3) * 0.55;
            r += (ATM[0] - r) * t; g += (ATM[1] - g) * t; bl += (ATM[2] - bl) * t;
          }
        } else {
          const d = Math.sqrt(-disc + R * R) ; // closest-approach distance to Earth centre
          const st = this.stars[j * W + i] * starA;
          r = SPA[0] + (255 - SPA[0]) * st * 0.85; g = SPA[1] + (250 - SPA[1]) * st * 0.85; bl = SPA[2] + (240 - SPA[2]) * st * 0.85;
          const t = (d - R) / atmT;
          if (t < 1) {
            const al = Math.pow(1 - t, 2.2) * 0.85;
            r += (ATM[0] - r) * al; g += (ATM[1] - g) * al; bl += (ATM[2] - bl) * al;
          }
        }
        data[q] = r; data[q + 1] = g; data[q + 2] = bl; data[q + 3] = 255;
      }
    }
    ctx.putImageData(this.img, 0, 0);
  }
}
