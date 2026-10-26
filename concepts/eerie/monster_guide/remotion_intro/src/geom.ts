// Polyline / ribbon helpers, ported from sf/core/lib_core.js (canvas) to SVG path strings.
export type P = [number, number];
export const TAU = Math.PI * 2;
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const sstep = (k: number) => {
  k = clamp(k);
  return k * k * (3 - 2 * k);
};
export const smoothstep = (e0: number, e1: number, x: number) => sstep((x - e0) / (e1 - e0));
export const n2 = (v: number) => (Math.round(v * 100) / 100).toString();
export const deg = (r: number) => (r * 180) / Math.PI;
export const rad = (d: number) => (d * Math.PI) / 180;

export function cubicPts(p0: P, p1: P, p2: P, p3: P, n: number, out: P[], skipFirst = false) {
  for (let i = skipFirst ? 1 : 0; i <= n; i++) {
    const t = i / n, u = 1 - t, a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
    out.push([a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]]);
  }
  return out;
}
export function quadPts(p0: P, c: P, p2: P, n: number): P[] {
  const out: P[] = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, u = 1 - t;
    out.push([u * u * p0[0] + 2 * u * t * c[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p2[1]]);
  }
  return out;
}
// outward normal = left of travel direction on screen (up for a left->right line)
export function normalsOf(Pts: P[]): P[] {
  const n = Pts.length, out: P[] = new Array(n);
  for (let i = 0; i < n; i++) {
    const p = Pts[Math.max(0, i - 1)], q = Pts[Math.min(n - 1, i + 1)];
    const tx = q[0] - p[0], ty = q[1] - p[1], l = Math.hypot(tx, ty) || 1;
    out[i] = [ty / l, -tx / l];
  }
  return out;
}
export const tangentsOf = (Pts: P[]): P[] => normalsOf(Pts).map((n) => [-n[1], n[0]] as P);
export function arcU(Pts: P[]) {
  const U = [0];
  for (let i = 1; i < Pts.length; i++) U.push(U[i - 1] + Math.hypot(Pts[i][0] - Pts[i - 1][0], Pts[i][1] - Pts[i - 1][1]));
  const L = U[U.length - 1] || 1;
  return U.map((u) => u / L);
}
export type Off = number | number[] | ((u: number, i: number) => number);
const offAt = (o: Off, u: number, i: number) => (typeof o === 'function' ? o(u, i) : Array.isArray(o) ? o[i] : o);

export function polyD(Pts: P[], close = true) {
  let d = '';
  Pts.forEach((p, i) => (d += (i ? 'L' : 'M') + n2(p[0]) + ' ' + n2(p[1])));
  return close ? d + 'Z' : d;
}
// closed ribbon between two signed normal offsets
export function ribbonD(Pts: P[], offA: Off, offB: Off) {
  const N = normalsOf(Pts), U = arcU(Pts), n = Pts.length, out: P[] = [];
  for (let i = 0; i < n; i++) {
    const o = offAt(offA, U[i], i);
    out.push([Pts[i][0] + N[i][0] * o, Pts[i][1] + N[i][1] * o]);
  }
  for (let i = n - 1; i >= 0; i--) {
    const o = offAt(offB, U[i], i);
    out.push([Pts[i][0] + N[i][0] * o, Pts[i][1] + N[i][1] * o]);
  }
  return polyD(out);
}
export function offsetPts(Pts: P[], off: Off): P[] {
  const N = normalsOf(Pts), U = arcU(Pts);
  return Pts.map((p, i) => {
    const o = offAt(off, U[i], i);
    return [p[0] + N[i][0] * o, p[1] + N[i][1] * o] as P;
  });
}
export function slicePts(Pts: P[], u0: number, u1: number): P[] {
  const U = arcU(Pts), out: P[] = [];
  const at = (u: number): P => {
    for (let i = 1; i < Pts.length; i++)
      if (U[i] >= u) {
        const k = (u - U[i - 1]) / (U[i] - U[i - 1] || 1);
        return [lerp(Pts[i - 1][0], Pts[i][0], k), lerp(Pts[i - 1][1], Pts[i][1], k)];
      }
    return [Pts[Pts.length - 1][0], Pts[Pts.length - 1][1]];
  };
  out.push(at(u0));
  for (let i = 0; i < Pts.length; i++) if (U[i] > u0 && U[i] < u1) out.push(Pts[i]);
  out.push(at(u1));
  return out;
}
// variable-width strip along a polyline (width = full width)
export function stripD(Pts: P[], width: Off) {
  const half: Off = typeof width === 'function' ? (u, i) => width(u, i) / 2 : Array.isArray(width) ? width.map((w) => w / 2) : width / 2;
  const neg: Off = typeof half === 'function' ? (u, i) => -half(u, i) : Array.isArray(half) ? half.map((w) => -w) : -half;
  return ribbonD(Pts, neg, half);
}
export const mixPts = (A: P[], B: P[], k: number): P[] => A.map((p, i) => [lerp(p[0], B[i][0], k), lerp(p[1], B[i][1], k)] as P);

// two-bone IK. k = how much of the bend lies in the picture plane (1 = side-on elbow, 0 = elbow pointing at camera)
export function ik(S: P, H: P, L1: number, L2: number, bend: 1 | -1, k = 1): P {
  const dx = H[0] - S[0], dy = H[1] - S[1];
  let d = Math.hypot(dx, dy) || 1;
  const dir: P = [dx / d, dy / d];
  d = Math.min(d, L1 + L2 - 0.01);
  const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, L1 * L1 - a * a)) * k;
  const perp: P = [-dir[1] * bend, dir[0] * bend];
  return [S[0] + dir[0] * a + perp[0] * h, S[1] + dir[1] * a + perp[1] * h];
}

export function mixHex(a: string, b: string, t: number) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const r = Math.round(lerp((pa >> 16) & 255, (pb >> 16) & 255, t));
  const g = Math.round(lerp((pa >> 8) & 255, (pb >> 8) & 255, t));
  const bl = Math.round(lerp(pa & 255, pb & 255, t));
  return '#' + ((1 << 24) | (r << 16) | (g << 8) | bl).toString(16).slice(1);
}
