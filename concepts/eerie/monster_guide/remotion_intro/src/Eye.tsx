// The 귤멍-style eye (plan 3-2), an SVG port of SFX.eye from sf/core/lib_core.js.
// Back to front: sclera, banded iris + pupil + one highlight (clipped to the open white), lower lid line with
// tiny teeth, crease lines, heavy upper-lid band with a pointed outer wing, 3 lash spikes.
import React from 'react';
import {
  P, TAU, arcU, clamp, cubicPts, lerp, mixPts, n2, normalsOf, offsetPts, polyD, quadPts, ribbonD,
  slicePts, smoothstep, sstep, stripD, tangentsOf,
} from './geom';

export const GOLD = ['#B8860B', '#FFC83D', '#FFE58A'];
const INK = '#1c1519';
const CREASE = '#b3a6b0';

export type EyeProps = {
  uid: string;
  x: number; y: number; w: number;
  h?: number; mirror?: boolean; tilt?: number; open?: number;
  closed?: 'smile' | 'flat' | false;
  irisScale?: number | 'dot'; irisStretch?: number; irisY?: number; irisBow?: number;
  iris?: string[]; pupil?: 'slit' | 'dot' | 'oval'; pupilScale?: number; pupilColor?: string;
  look?: { x: number; y: number };
  highlight?: boolean; highlightSize?: number; highlight2?: boolean; sparkle?: number;
  lid?: number; wing?: number; wingAngle?: number; lashes?: number; lashLen?: number;
  lower?: number; teeth?: number; crease?: number; lidShade?: number; innerWrap?: number;
  px?: number; // one device pixel in local units (keeps hairlines visible)
};

const EN = 24;
function eyeOutline(a: number, b: number) {
  const O: P = [-a, -0.22 * b], T: P = [-0.08 * a, -b], I: P = [a, 0.1 * b], B: P = [0.04 * a, b];
  const top: P[] = [], bot: P[] = [];
  cubicPts(O, [-0.84 * a, -0.74 * b], [-0.5 * a, -b], T, EN, top);
  cubicPts(T, [0.42 * a, -b], [a, -0.6 * b], I, EN, top, true);
  cubicPts(O, [-0.93 * a, 0.42 * b], [-0.56 * a, b], B, EN, bot);
  cubicPts(B, [0.62 * a, b], [a, 0.74 * b], I, EN, bot, true);
  return { top, bot };
}
function bandProfile(s: number) {
  if (s < 0.25) return lerp(1.05, 1.16, sstep(s / 0.25));
  if (s < 0.65) return lerp(1.16, 1.0, sstep((s - 0.25) / 0.4));
  return lerp(1.0, 0.86, sstep((s - 0.65) / 0.35));
}
function yOnPolyAt(Pts: P[], x: number) {
  for (let i = 1; i < Pts.length; i++) {
    const p = Pts[i - 1], q = Pts[i];
    if ((p[0] - x) * (q[0] - x) <= 0 && p[0] !== q[0]) return lerp(p[1], q[1], (x - p[0]) / (q[0] - p[0]));
  }
  return null;
}
function lashD(base: P, tan: P, nrm: P, len: number, bw: number, lean: number, curl: number) {
  const d1: P = [nrm[0] * Math.cos(lean) - tan[0] * Math.sin(lean), nrm[1] * Math.cos(lean) - tan[1] * Math.sin(lean)];
  const l2 = lean + curl;
  const d2: P = [nrm[0] * Math.cos(l2) - tan[0] * Math.sin(l2), nrm[1] * Math.cos(l2) - tan[1] * Math.sin(l2)];
  const mid: P = [base[0] + d1[0] * len * 0.55, base[1] + d1[1] * len * 0.55];
  const tip: P = [mid[0] + d2[0] * len * 0.5, mid[1] + d2[1] * len * 0.5];
  const p: P = [-d1[1], d1[0]], sg = p[0] * tan[0] + p[1] * tan[1] > 0 ? 1 : -1;
  const b1: P = [base[0] + tan[0] * bw, base[1] + tan[1] * bw], b2: P = [base[0] - tan[0] * bw, base[1] - tan[1] * bw];
  const c1: P = [mid[0] + p[0] * sg * bw * 0.45, mid[1] + p[1] * sg * bw * 0.45];
  const c2: P = [mid[0] - p[0] * sg * bw * 0.45, mid[1] - p[1] * sg * bw * 0.45];
  return `M${n2(b1[0])} ${n2(b1[1])}Q${n2(c1[0])} ${n2(c1[1])} ${n2(tip[0])} ${n2(tip[1])}Q${n2(c2[0])} ${n2(c2[1])} ${n2(b2[0])} ${n2(b2[1])}Z`;
}
function toothD(base: P, tan: P, nrm: P, len: number, bw: number, lean: number) {
  const d: P = [-nrm[0] * Math.cos(lean) - tan[0] * Math.sin(lean), -nrm[1] * Math.cos(lean) - tan[1] * Math.sin(lean)];
  return polyD([
    [base[0] + tan[0] * bw, base[1] + tan[1] * bw],
    [base[0] + d[0] * len, base[1] + d[1] * len],
    [base[0] - tan[0] * bw, base[1] - tan[1] * bw],
  ]);
}
const idxAt = (U: number[], u: number) => {
  const i = U.findIndex((v) => v >= u);
  return i < 0 ? U.length - 1 : i;
};
export function sparkleD(cx: number, cy: number, r: number, pinch = 0.12) {
  let d = '';
  for (let i = 0; i < 4; i++) {
    const a0 = -Math.PI / 2 + (i * Math.PI) / 2, a1 = a0 + Math.PI / 2, am = a0 + Math.PI / 4;
    const p0 = [cx + Math.cos(a0) * r, cy + Math.sin(a0) * r], p1 = [cx + Math.cos(a1) * r, cy + Math.sin(a1) * r];
    const c = [cx + Math.cos(am) * r * pinch, cy + Math.sin(am) * r * pinch];
    if (i === 0) d += `M${n2(p0[0])} ${n2(p0[1])}`;
    d += `Q${n2(c[0])} ${n2(c[1])} ${n2(p1[0])} ${n2(p1[1])}`;
  }
  return d + 'Z';
}

const ClosedEye: React.FC<{ o: EyeProps; a: number; b: number; H0: number; thick: number; px: number }> = ({ o, a, b, H0, thick, px }) => {
  const w = 2 * a;
  const mode = o.closed || 'flat';
  const Pts = mode === 'smile'
    ? quadPts([-0.98 * a, 0.2 * b], [-0.06 * a, -1.05 * b], [0.92 * a, 0.3 * b], 2 * EN)
    : quadPts([-a, 0.1 * b], [-0.02 * a, 0.62 * b], [0.94 * a, 0.16 * b], 2 * EN);
  const th = thick * (mode === 'flat' ? 0.85 : 0.95);
  const prof = Pts.map((_, i) => th * bandProfile(i / (Pts.length - 1)) * (i === Pts.length - 1 ? 0.6 : 1));
  const els: React.ReactNode[] = [];
  if ((o.crease ?? 2) > 0) {
    const cp = offsetPts(slicePts(Pts, 0.14, 0.86), th * 1.12 + 0.05 * w);
    els.push(<path key="cr" d={stripD(cp, (u) => Math.max(px * 1.1, 0.01 * w) * Math.sin(Math.PI * u) ** 0.5)} fill={CREASE} />);
  }
  els.push(<path key="band" d={ribbonD(Pts, (u) => -0.18 * th * Math.sin(Math.PI * u), prof)} fill={INK} />);
  const N = normalsOf(Pts), T = tangentsOf(Pts);
  const U0: P = [Pts[0][0] + N[0][0] * prof[0], Pts[0][1] + N[0][1] * prof[0]];
  const wl = (o.wing ?? 0.2) * w, wa = (o.wingAngle ?? 0.3) + (mode === 'smile' ? 0.3 : -0.12);
  const tip: P = [Pts[0][0] - Math.cos(wa) * wl, Pts[0][1] - Math.sin(wa) * wl];
  const lo: P = [Pts[3][0] - N[3][0] * th * 0.2, Pts[3][1] - N[3][1] * th * 0.2];
  const s3: P = [Pts[3][0] + N[3][0] * prof[3], Pts[3][1] + N[3][1] * prof[3]];
  els.push(
    <path key="wing" fill={INK}
      d={`M${n2(s3[0])} ${n2(s3[1])}L${n2(U0[0])} ${n2(U0[1])}Q${n2(lerp(U0[0], tip[0], 0.5))} ${n2(lerp(U0[1], tip[1], 0.5) - 0.02 * w)} ${n2(tip[0])} ${n2(tip[1])}Q${n2(lerp(tip[0], lo[0], 0.5) + 0.03 * w)} ${n2(lerp(tip[1], lo[1], 0.5) - 0.01 * w)} ${n2(lo[0])} ${n2(lo[1])}Z`} />,
  );
  const nl = Math.round(o.lashes ?? 3);
  if (nl > 0) {
    const outer = Pts.map((p, i) => [p[0] + N[i][0] * prof[i], p[1] + N[i][1] * prof[i]] as P);
    const N2 = normalsOf(outer), T2 = tangentsOf(outer), U2 = arcU(outer), L = (o.lashLen ?? 0.3) * H0;
    let d = '';
    for (let j = 0; j < nl; j++) {
      const k = nl === 1 ? 0.5 : j / (nl - 1), u = lerp(0.14, 0.6, k);
      const i = idxAt(U2, u), bw = 0.02 * w;
      const base: P = [outer[i][0] - N2[i][0] * bw * 1.2, outer[i][1] - N2[i][1] * bw * 1.2];
      d += lashD(base, T2[i], N2[i], L * lerp(1, 0.85, k), bw, lerp(0.9, 0.4, k), 0.5);
    }
    els.push(<path key="lash" d={d} fill={INK} />);
  }
  const nt = Math.round(o.teeth ?? 3);
  if (nt > 0) {
    const U = arcU(Pts);
    let d = '';
    for (let j = 0; j < nt; j++) {
      const u = nt === 1 ? 0.4 : lerp(0.2, 0.66, j / (nt - 1));
      const i = idxAt(U, u);
      d += toothD([Pts[i][0] + N[i][0] * th * 0.1, Pts[i][1] + N[i][1] * th * 0.1], T[i], N[i], 0.06 * w * (j % 2 ? 0.8 : 1), 0.022 * w, 0.3);
    }
    els.push(<path key="teeth" d={d} fill={INK} />);
  }
  return <>{els}</>;
};

export const Eye: React.FC<EyeProps> = (o) => {
  const w = o.w, a = w / 2, h = o.h ?? 0.6, b = (w * h) / 2, H0 = w * 0.6;
  const sx = o.mirror ? -1 : 1;
  const px = o.px ?? 0.5;
  const hs = sx;
  const thick = (o.lid ?? 0.15) * H0;
  const tf = `translate(${n2(o.x)} ${n2(o.y)}) scale(${sx} 1) rotate(${n2(((o.tilt || 0) * 180) / Math.PI)})`;
  const { top, bot } = eyeOutline(a, b);
  const closedMode = o.closed || ((o.open ?? 1) < 0.12 ? 'flat' : false);
  if (closedMode) {
    return (
      <g transform={tf}>
        <ClosedEye o={{ ...o, closed: closedMode }} a={a} b={b} H0={H0} thick={thick} px={px} />
      </g>
    );
  }
  const iris = o.iris || GOLD;
  const open = clamp(o.open ?? 1);
  const Mt = top.length - 1;
  const closedT = bot.map((p, i) => {
    const sN = i / Mt, k = smoothstep(0.45, 1, sN) * 0.85;
    return [p[0], lerp(p[1], lerp(top[0][1], top[Mt][1], sN), k)] as P;
  });
  const lid = mixPts(top, closedT, (1 - open) * 0.94);
  const botR = bot;
  const M = lid.length - 1;
  const visible = polyD([...lid, ...botR.slice().reverse()]);
  const clipId = `ec-${o.uid}`;

  const lookX = clamp((o.look && o.look.x) || 0, -1, 1) * sx, lookY = clamp((o.look && o.look.y) || 0, -1, 1);
  const isDot = o.irisScale === 'dot';
  const irisScale = isDot ? 0.2 : ((o.irisScale as number) ?? 0.62);
  const r = irisScale * a, ry = r * (o.irisStretch ?? 1.06);
  const maxDx = (a - r) * 0.9 + 0.1 * a;
  const icx = lookX * maxDx, icy = (o.irisY ?? -0.1) * 2 * b + lookY * 0.36 * b;

  const inner: React.ReactNode[] = [];
  if (isDot) {
    const dr = 0.085 * w * (o.pupilScale ?? 1), dcy = icy + 0.12 * b;
    inner.push(<ellipse key="dot" cx={icx} cy={dcy} rx={dr} ry={dr * 1.12} fill={o.pupilColor || '#2A1206'} />);
    if (o.highlight !== false)
      inner.push(<ellipse key="dhi" cx={icx - 0.38 * dr * hs} cy={dcy - 0.4 * dr} rx={dr * 0.3} ry={dr * 0.26} fill="#fff" transform={`rotate(${n2(-0.5 * hs * 57.3)} ${n2(icx - 0.38 * dr * hs)} ${n2(dcy - 0.4 * dr)})`} />);
  } else {
    const n = iris.length;
    const fr = n === 2 ? [0.56] : n === 3 ? [0.47, 0.73] : [0.42, 0.61, 0.8];
    const bow = (o.irisBow ?? 0.12) * ry;
    const irisClip = `ic-${o.uid}`;
    inner.push(
      <clipPath key="icp" id={irisClip}>
        <ellipse cx={icx} cy={icy} rx={r} ry={ry} />
      </clipPath>,
    );
    inner.push(<ellipse key="ib" cx={icx} cy={icy} rx={r} ry={ry} fill={iris[0]} />);
    const bands: React.ReactNode[] = [];
    for (let k = 1; k < n; k++) {
      const y0 = icy - ry + 2 * ry * fr[k - 1];
      const pts: P[] = [[icx - r - 2, y0]];
      for (let j = 0; j <= 16; j++) {
        const t = -1 + j / 8;
        pts.push([icx + t * r, y0 + bow * (1 - t * t)]);
      }
      pts.push([icx + r + 2, y0], [icx + r + 2, icy + ry + 2], [icx - r - 2, icy + ry + 2]);
      bands.push(<path key={'band' + k} d={polyD(pts)} fill={iris[k]} />);
    }
    const ps = o.pupilScale ?? 1, pcx = icx, pcy = icy - 0.06 * ry, pupil = o.pupil || 'slit';
    const pc = o.pupilColor || '#2A1206';
    let pupilEl: React.ReactNode = null;
    if (pupil === 'oval') pupilEl = <ellipse cx={pcx} cy={pcy} rx={0.3 * r * ps} ry={0.46 * ry * ps} fill={pc} />;
    else if (pupil === 'dot') pupilEl = <circle cx={pcx} cy={pcy + 0.04 * ry} r={0.2 * r * ps} fill={pc} />;
    else {
      const hh = 0.8 * ry * Math.min(1.2, 0.6 + 0.4 * ps), hw = 0.11 * r * ps;
      pupilEl = <path d={`M${n2(pcx)} ${n2(pcy - hh)}Q${n2(pcx + hw * 2)} ${n2(pcy)} ${n2(pcx)} ${n2(pcy + hh)}Q${n2(pcx - hw * 2)} ${n2(pcy)} ${n2(pcx)} ${n2(pcy - hh)}Z`} fill={pc} />;
    }
    inner.push(
      <g key="ibands" clipPath={`url(#${irisClip})`}>
        {bands}
        {pupilEl}
      </g>,
    );
    if (o.highlight !== false) {
      const hr = (o.highlightSize ?? 0.13) * r;
      const hx = icx - 0.4 * r * hs;
      let hy = icy - 0.3 * ry;
      const ly = yOnPolyAt(lid, hx);
      if (ly !== null) hy = Math.max(hy, ly + hr * 1.7);
      inner.push(<ellipse key="hi" cx={hx} cy={hy} rx={hr * 1.18} ry={hr} fill="#fff" transform={`rotate(${n2(-0.55 * hs * 57.3)} ${n2(hx)} ${n2(hy)})`} />);
      if (o.highlight2) inner.push(<circle key="hi2" cx={icx + 0.36 * r * hs} cy={icy + 0.42 * ry} r={hr * 0.5} fill="#fff" />);
      if ((o.sparkle ?? 0) > 0.01) {
        const sr = r * 0.34 * (o.sparkle ?? 0);
        inner.push(<path key="spk" d={sparkleD(icx + 0.22 * r * hs, icy - 0.05 * ry, sr, 0.14)} fill="#fff" />);
      }
    }
  }
  if ((o.lidShade ?? 0) > 0) {
    inner.push(
      <path key="lshade" fill={`rgba(52,30,70,${o.lidShade})`}
        d={ribbonD(lid, -1 * px, (u) => -(0.16 * b + 0.05 * w) * Math.sin(Math.PI * clamp(u * 1.05)) ** 0.6)} />,
    );
  }

  // 5. lower lid line + tiny teeth
  const lowLen = o.lower ?? 0.66;
  const lowerEls: React.ReactNode[] = [];
  if (lowLen > 0) {
    const gap = 0.012 * w;
    const lowPts = offsetPts(slicePts(botR, 0, lowLen), -gap);
    const lc = offsetPts(slicePts(botR, 0.12, Math.min(0.92, lowLen + 0.18)), -(gap + 0.045 * w));
    lowerEls.push(<path key="lc" d={stripD(lc, (u) => Math.max(px * 1.1, 0.008 * w) * Math.sin(Math.PI * u) ** 0.5)} fill="rgba(179,166,176,0.75)" />);
    const lw = Math.max(px * 1.6, 0.022 * w);
    lowerEls.push(<path key="ll" d={stripD(lowPts, (u) => lw * (u < 0.12 ? lerp(1.5, 1, u / 0.12) : u < 0.72 ? 1 : Math.max(0, (1 - u) / 0.28) ** 0.7))} fill={INK} />);
    const nt = Math.round(o.teeth ?? 3);
    if (nt > 0) {
      const N = normalsOf(lowPts), T = tangentsOf(lowPts), U = arcU(lowPts);
      let d = '';
      for (let j = 0; j < nt; j++) {
        const u = nt === 1 ? 0.4 : lerp(0.16, 0.66, j / (nt - 1));
        const i = idxAt(U, u);
        const nn: P = [-N[i][0], -N[i][1]];
        const base: P = [lowPts[i][0] + nn[0] * lw * 0.3, lowPts[i][1] + nn[1] * lw * 0.3];
        d += toothD(base, T[i], [-nn[0], -nn[1]], 0.075 * w * (j % 2 ? 0.78 : 1), 0.021 * w, 0.22);
      }
      lowerEls.push(<path key="lt" d={d} fill={INK} />);
    }
  }
  // 6. crease lines
  const creaseEls: React.ReactNode[] = [];
  const nCrease = o.crease ?? 2;
  if (nCrease > 0) {
    const base = mixPts(top, lid, 0.4);
    for (let c = 0; c < nCrease; c++) {
      const u0 = c ? 0.28 : 0.12, u1 = c ? 0.74 : 0.9, off = thick * 1.16 + (0.024 + c * 0.026) * w;
      const cp = offsetPts(slicePts(base, u0, u1), off);
      creaseEls.push(<path key={'cr' + c} d={stripD(cp, (u) => Math.max(px * 1.1, (c ? 0.0065 : 0.009) * w) * Math.sin(Math.PI * u) ** 0.5)} fill={CREASE} />);
    }
  }
  // 7. heavy upper lid band + wing + lashes
  const wrapN = Math.max(0, Math.round(EN * 2 * (o.innerWrap ?? 0.15) * smoothstep(0.3, 0.85, open)));
  const S = lid.slice();
  for (let j = 1; j <= wrapN; j++) S.push(botR[M - j]);
  const endK = lerp(0.55, 1, smoothstep(0.3, 0.85, open));
  const prof = S.map((_, i) =>
    i <= M
      ? thick * bandProfile(i / M) * (i / M > 0.7 ? lerp(1, endK, (i / M - 0.7) / 0.3) : 1)
      : thick * 0.86 * endK * (1 - (i - M) / wrapN) ** 0.9,
  );
  const bandD = ribbonD(S, -0.6 * px, prof);
  const Nl = normalsOf(S);
  const U0: P = [S[0][0] + Nl[0][0] * prof[0], S[0][1] + Nl[0][1] * prof[0]];
  const o1: P = [S[1][0] + Nl[1][0] * prof[1], S[1][1] + Nl[1][1] * prof[1]];
  const tdl = Math.hypot(U0[0] - o1[0], U0[1] - o1[1]) || 1;
  const td: P = [(U0[0] - o1[0]) / tdl, (U0[1] - o1[1]) / tdl];
  const wl = (o.wing ?? 0.2) * w, wa = o.wingAngle ?? 0.3;
  const O = lid[0];
  const tip: P = [O[0] - Math.cos(wa) * wl, O[1] - Math.sin(wa) * wl];
  const dU = Math.hypot(tip[0] - U0[0], tip[1] - U0[1]);
  const bN = normalsOf(botR)[3];
  const below: P = [botR[3][0] - bN[0] * 0.01 * w, botR[3][1] - bN[1] * 0.01 * w];
  const mid: P = [lerp(tip[0], below[0], 0.5) + 0.07 * a, lerp(tip[1], below[1], 0.5) - 0.02 * b];
  const s4o: P = [S[4][0] + Nl[4][0] * prof[4], S[4][1] + Nl[4][1] * prof[4]];
  const wingD =
    `M${n2(S[4][0])} ${n2(S[4][1])}L${n2(s4o[0])} ${n2(s4o[1])}L${n2(o1[0])} ${n2(o1[1])}L${n2(U0[0])} ${n2(U0[1])}` +
    `Q${n2(U0[0] + td[0] * dU * 0.55)} ${n2(U0[1] + td[1] * dU * 0.55)} ${n2(tip[0])} ${n2(tip[1])}` +
    `Q${n2(mid[0])} ${n2(mid[1])} ${n2(below[0])} ${n2(below[1])}L${n2(O[0] + 0.02 * a)} ${n2(O[1])}Z`;
  let lashesD = '';
  const nl = Math.round(o.lashes ?? 3);
  if (nl > 0) {
    const lidOuter = S.slice(0, M + 1).map((p, i) => [p[0] + Nl[i][0] * prof[i], p[1] + Nl[i][1] * prof[i]] as P);
    const N2 = normalsOf(lidOuter), T2 = tangentsOf(lidOuter), U2 = arcU(lidOuter);
    const L = (o.lashLen ?? 0.32) * H0;
    for (let j = 0; j < nl; j++) {
      const k = nl === 1 ? 0.5 : j / (nl - 1);
      const u = lerp(0.07, 0.5, k);
      const i = idxAt(U2, u);
      const bw = 0.024 * w;
      const base: P = [lidOuter[i][0] - N2[i][0] * bw * 1.2, lidOuter[i][1] - N2[i][1] * bw * 1.2];
      lashesD += lashD(base, T2[i], N2[i], L * lerp(1.0, 0.8, k), bw, lerp(1.0, 0.45, k), lerp(0.6, 0.45, k));
    }
  }
  return (
    <g transform={tf}>
      <defs>
        <clipPath id={clipId}>
          <path d={visible} />
        </clipPath>
      </defs>
      <path d={visible} fill="#ffffff" />
      <g clipPath={`url(#${clipId})`}>{inner}</g>
      {lowerEls}
      {creaseEls}
      <path d={bandD} fill={INK} />
      <path d={wingD} fill={INK} />
      {lashesD ? <path d={lashesD} fill={INK} /> : null}
    </g>
  );
};

// soft blush: the only gradient on a face (plan 3-1)
export const Blush: React.FC<{ uid: string; x: number; y: number; w: number; alpha: number }> = ({ uid, x, y, w, alpha }) => (
  <>
    <defs>
      <radialGradient id={`bl-${uid}`}>
        <stop offset="0" stopColor="#ff7f96" stopOpacity={alpha} />
        <stop offset="0.6" stopColor="#ff7f96" stopOpacity={alpha * 0.55} />
        <stop offset="1" stopColor="#ff7f96" stopOpacity={0} />
      </radialGradient>
    </defs>
    <ellipse cx={x} cy={y} rx={w * 0.5} ry={w * 0.22} fill={`url(#bl-${uid})`} />
  </>
);
export { TAU };
