// VISUALIZE flat POV engine: perspective camera + flat SVG shapes
import fs from 'fs';
export const W = 1920, H = 1080;
const FD = '/tmp/claude-0/vz/flat/fonts/';
const ff = (n, f, fmt = 'woff2') => `@font-face{font-family:${n};src:url(data:font/${fmt};base64,${fs.readFileSync(f.startsWith('/') ? f : FD + f).toString('base64')})}`;
export const FONTS = ff('Mono', 'mono.woff2') + ff('SerifI', 'serif_i.woff2') + ff('Inter', 'inter.woff2') + ff('InterB', 'interb.woff2')
  + ff('Seg', '/tmp/claude-0/vz/fonts/fonts-DSEG_v046/DSEG7-Classic/DSEG7Classic-Bold.ttf', 'ttf');

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
export const smooth = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
export const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
export const mix = (c1, c2, t) => { const A = hex(c1), B = hex(c2); t = clamp(t);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
export const f1 = v => (Math.round(v * 10) / 10).toString();
let _seed = 1;
export const seed = s => { _seed = s; };
export const rnd = () => (_seed = (_seed * 16807) % 2147483647) / 2147483647;

// camera: X right, Y up, Z forward. yaw (rad, +right), pitch (rad, +up), roll (deg on screen)
export class Cam {
  constructor({ x = 0, y = 1.7, z = 0, yaw = 0, pitch = 0, f = 980, cx = 960, cy = 540, near = 0.12 } = {}) {
    Object.assign(this, { x, y, z, yaw, pitch, f, cx, cy, near });
  }
  toCam([X, Y, Z]) {
    let dx = X - this.x, dy = Y - this.y, dz = Z - this.z;
    const cy = Math.cos(this.yaw), sy = Math.sin(this.yaw);
    let x1 = dx * cy - dz * sy, z1 = dx * sy + dz * cy;
    const cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
    let y2 = dy * cp - z1 * sp, z2 = dy * sp + z1 * cp;
    return [x1, y2, z2];
  }
  scr([x, y, z]) { return [this.cx + this.f * x / z, this.cy - this.f * y / z]; }
  p(P) { const c = this.toCam(P); return this.scr([c[0], c[1], Math.max(c[2], 1e-3)]); }
  depth(P) { return this.toCam(P)[2]; }
  // clip polygon (world pts) at near plane, return screen pts
  clip(pts) {
    const c = pts.map(p => this.toCam(p)); const out = []; const n = this.near;
    for (let i = 0; i < c.length; i++) {
      const a = c[i], b = c[(i + 1) % c.length];
      const ain = a[2] >= n, bin = b[2] >= n;
      if (ain) out.push(a);
      if (ain !== bin) { const t = (n - a[2]) / (b[2] - a[2]); out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, n]); }
    }
    return out.map(q => this.scr(q));
  }
  poly(pts, fill, extra = '') {
    const s = this.clip(pts); if (s.length < 3) return '';
    return `<path d="M${s.map(q => f1(q[0]) + ' ' + f1(q[1])).join(' L')}Z" fill="${fill}" ${extra}/>`;
  }
  line(a, b, stroke, w, extra = '') {
    const s = this.clip([a, b, b]); if (s.length < 2) return '';
    return `<path d="M${f1(s[0][0])} ${f1(s[0][1])} L${f1(s[1][0])} ${f1(s[1][1])}" stroke="${stroke}" stroke-width="${w}" ${extra}/>`;
  }
  // world-sized dot facing camera
  disc(P, r, fill, extra = '') { const z = this.depth(P); if (z < this.near) return ''; const [x, y] = this.p(P);
    return `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(this.f * r / z)}" fill="${fill}" ${extra}/>`; }
  px(r, P) { return this.f * r / Math.max(this.depth(P), 1e-3); }
}
// rectangle on a plane: origin o, axis u, axis v (world vectors), sizes
export const quad = (o, u, v) => [o, [o[0] + u[0], o[1] + u[1], o[2] + u[2]], [o[0] + u[0] + v[0], o[1] + u[1] + v[1], o[2] + u[2] + v[2]], [o[0] + v[0], o[1] + v[1], o[2] + v[2]]];
// axis-aligned box faces visible from camera, back to front: returns svg
export function box(cam, [x0, y0, z0], [x1, y1, z1], cols) {
  // cols: {top, front, side, back}
  const F = [];
  const add = (pts, col, cx, cy, cz) => { if (col) F.push({ pts, col, d: cam.depth([cx, cy, cz]) }); };
  if (cam.y > y1) add([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], cols.top, (x0 + x1) / 2, y1, (z0 + z1) / 2);
  if (cam.y < y0) add([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], cols.bottom, (x0 + x1) / 2, y0, (z0 + z1) / 2);
  if (cam.z < z0) add([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], cols.front, (x0 + x1) / 2, (y0 + y1) / 2, z0);
  if (cam.z > z1) add([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], cols.back || cols.front, (x0 + x1) / 2, (y0 + y1) / 2, z1);
  if (cam.x < x0) add([[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], cols.side, x0, (y0 + y1) / 2, (z0 + z1) / 2);
  if (cam.x > x1) add([[x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0]], cols.side2 || cols.side, x1, (y0 + y1) / 2, (z0 + z1) / 2);
  F.sort((a, b) => b.d - a.d);
  return F.map(f => cam.poly(f.pts, f.col)).join('');
}
// common defs
export const DEFS = `<defs>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05040d" stop-opacity=".6"/></radialGradient>
<radialGradient id="glowW" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe2b0" stop-opacity=".9"/><stop offset="1" stop-color="#ffc98a" stop-opacity="0"/></radialGradient>
<radialGradient id="glowB" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#8fb4ff" stop-opacity=".75"/><stop offset="1" stop-color="#5a7cd6" stop-opacity="0"/></radialGradient>
<radialGradient id="glowC" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#bfe6ff" stop-opacity=".85"/><stop offset="1" stop-color="#bfe6ff" stop-opacity="0"/></radialGradient>
<filter id="b4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="b12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="b30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
</defs>`;
export const wrap = (body, { roll = 0, sway = 0, scale = 1.04, defs = '' } = {}) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${DEFS}${defs}
<g transform="translate(${f1(sway)} 0) rotate(${roll.toFixed(3)} 960 540) translate(960 540) scale(${scale}) translate(-960 -540)">${body}</g>`;
// overlay text helpers (screen space, after the world group)
export const hudText = (x, y, txt, { size = 20, op = 0.75, fill = '#f4ecff', anchor = 'start' } = {}) =>
  `<text x="${x}" y="${y}" font-family="Mono" font-size="${size}" fill="${fill}" opacity="${op}" text-anchor="${anchor}">${txt}</text>`;
export const bigLine = (txt, a, { y = 930, size = 54, fill = '#fff3e4' } = {}) => a <= 0 ? '' :
  `<text x="960" y="${y + (1 - a) * 12}" text-anchor="middle" font-family="SerifI" font-size="${size}" fill="${fill}" opacity="${a.toFixed(3)}">${txt}</text>`;
