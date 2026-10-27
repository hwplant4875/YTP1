import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import {
  CAPTIONS,
  COVER_N,
  END_START,
  H,
  REWIND_END,
  REWIND_START,
  STEP_FRAMES,
  W,
} from "./timeline";

const BASE_H = 1.7; // metres
const GIANT_PX = 900; // on-screen height the camera settles on
const FEET_Y = 1290;
const R_EARTH = 6_371_000;
const STOP_TRAVEL_N = 11;
const FONT = "Pretendard";

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const easeOut = Easing.out(Easing.cubic);
const easeInOut = Easing.inOut(Easing.cubic);

// Horizontal position of the giant for a (continuous) number of doublings.
const travelX = (n: number) => {
  const m = Math.min(n, STOP_TRAVEL_N);
  return 0.714 * (Math.pow(2, m + 1) - 2);
};
const XC = travelX(STOP_TRAVEL_N);

const introN = (f: number) => {
  if (f < REWIND_START) return COVER_N;
  const t = clamp01((f - REWIND_START) / (REWIND_END - REWIND_START));
  return COVER_N * (1 - easeInOut(t));
};

const giantN = (f: number) => {
  let n = introN(f);
  for (const s of STEP_FRAMES) n += easeOut(clamp01((f - s) / 8));
  return n;
};
const camN = (f: number) => {
  let n = introN(f);
  for (const s of STEP_FRAMES) n += easeInOut(clamp01((f - s - 4) / 16));
  return n;
};
const stepsDone = (f: number) => STEP_FRAMES.filter((s) => f >= s).length;

const fmtHeight = (m: number) => {
  if (m < 10) return `${m.toFixed(1)}m`;
  if (m < 1000) return `${Math.round(m).toLocaleString("en-US")}m`;
  const km = m / 1000;
  if (km < 100) return `${km.toFixed(1)}km`;
  return `${Math.round(km).toLocaleString("en-US")}km`;
};

// ---------- colour helpers ----------
const hex = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const A = hex(a);
  const B = hex(b);
  const r = A.map((v, i) => Math.round(v + (B[i] - v) * clamp01(t)));
  return `rgb(${r[0]},${r[1]},${r[2]})`;
};
const ramp = (stops: [number, string][], v: number) => {
  if (v <= stops[0][0]) return mix(stops[0][1], stops[0][1], 0);
  for (let i = 1; i < stops.length; i++) {
    if (v <= stops[i][0]) {
      const [a, ca] = stops[i - 1];
      const [b, cb] = stops[i];
      return mix(ca, cb, (v - a) / (b - a));
    }
  }
  return mix(stops[stops.length - 1][1], stops[stops.length - 1][1], 0);
};

// ---------- world data ----------
type Box = { x: number; w: number; h: number; color: string; windows?: boolean };
const BUILDINGS: Box[] = [
  { x: -30, w: 14, h: 18, color: "#c9d6e3", windows: true },
  { x: 18, w: 12, h: 13, color: "#f2c57c", windows: true },
  ...[0, 1, 2, 3, 4, 5].map((i) => ({
    x: 40 + i * 32,
    w: 22,
    h: 45,
    color: i % 2 ? "#e8edf2" : "#dfe6ee",
    windows: true,
  })),
  ...[0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({
    x: 300 + i * 140 + (i % 3) * 30,
    w: 40 + (i % 3) * 15,
    h: 90 + ((i * 53) % 160),
    color: ["#b8c7d9", "#a9bcd2", "#c4d1e0"][i % 3],
    windows: true,
  })),
  ...[0, 1, 2, 3, 4, 5].map((i) => ({
    x: -80 - i * 120,
    w: 50,
    h: 60 + ((i * 37) % 120),
    color: "#b3c3d6",
    windows: true,
  })),
];
const LOTTE_X = 980;
const LOTTE_H = 555;
const BAEKDU = { x: 7200, half: 6500, h: 2744 };
const EVEREST = { x: -16000, half: 13000, h: 8849 };
const CLOUDS = Array.from({ length: 26 }, (_, i) => ({
  x: -20000 + i * 2300 + ((i * 977) % 1300),
  y: 1600 + ((i * 431) % 1200),
  w: 900 + ((i * 613) % 1800),
}));
const STARS = Array.from({ length: 140 }, (_, i) => ({
  x: (i * 7919) % W,
  y: (i * 104729) % H,
  r: 1 + ((i * 31) % 3) * 0.7,
}));

// ---------- the walking giant (normalised: height 1, feet at 0) ----------
const Person: React.FC<{ phase: number; parity: number }> = ({ phase, parity }) => {
  // phase 0..1 within the current step, parity flips the leading leg.
  const swing = Math.cos(Math.PI * phase); // 1 -> -1
  const a = 14 * swing * (parity ? 1 : -1);
  const lift = Math.sin(Math.PI * phase) * 0.04;
  const leg = (angle: number, back: boolean, raise: number) => (
    <g transform={`translate(0 -0.49) rotate(${angle})`}>
      <rect x={-0.042} y={0} width={0.084} height={0.45 - raise} rx={0.035} fill={back ? "#1b2c47" : "#24395c"} />
      <rect x={-0.05} y={0.43 - raise} width={0.13} height={0.06} rx={0.025} fill={back ? "#dcdcdc" : "#ffffff"} />
    </g>
  );
  const arm = (angle: number, back: boolean) => (
    <g transform={`translate(0 -0.79) rotate(${angle})`}>
      <rect x={-0.032} y={0} width={0.064} height={0.34} rx={0.03} fill={back ? "#c9412a" : "#ff5a36"} />
      <circle cx={0} cy={0.35} r={0.035} fill={back ? "#d9a985" : "#f2c6a0"} />
    </g>
  );
  return (
    <g>
      {arm(a, true)}
      {leg(-a, true, a < 0 ? lift : 0)}
      {leg(a, false, a > 0 ? lift : 0)}
      {/* torso / hoodie */}
      <rect x={-0.085} y={-0.84} width={0.17} height={0.4} rx={0.06} fill="#ff5a36" />
      <rect x={-0.085} y={-0.5} width={0.17} height={0.05} rx={0.02} fill="#e04a2a" />
      {/* neck + head (side view, no face) */}
      <rect x={-0.025} y={-0.88} width={0.05} height={0.06} fill="#f2c6a0" />
      <circle cx={0.01} cy={-0.93} r={0.068} fill="#f2c6a0" />
      <path d="M -0.06 -0.93 A 0.07 0.07 0 0 1 0.075 -0.95 L 0.06 -0.975 A 0.07 0.07 0 0 0 -0.055 -0.96 Z" fill="#2b2522" />
      <path d="M -0.062 -0.95 Q -0.07 -1.0 0.0 -1.0 Q 0.07 -1.0 0.078 -0.945 Q 0.02 -0.975 -0.035 -0.9 Z" fill="#2b2522" />
      <circle cx={0.05} cy={-0.94} r={0.009} fill="#2b2522" />
      <path d="M 0.074 -0.935 Q 0.09 -0.92 0.074 -0.912" fill="#f2c6a0" stroke="#e0ad86" strokeWidth={0.006} />
      {arm(-a, false)}
    </g>
  );
};

// ---------- small helpers ----------
const Label: React.FC<{ x: number; y: number; text: string; sub?: string; opacity: number; side?: 1 | -1 | 0; long?: boolean; dx?: number; dy?: number }> = ({
  x,
  y,
  text,
  sub,
  opacity,
  side = 1,
  long = false,
  dx,
  dy,
}) => {
  const tx = dx !== undefined ? x + dx : x + side * (long ? 150 : 70);
  const ty = dy !== undefined ? y + dy : side === 0 ? y - 110 : y + (long ? 110 : -60);
  return (
    <g opacity={opacity}>
      <circle cx={x} cy={y} r={7} fill="#ffd23f" stroke="#111" strokeWidth={3} />
      <line x1={x} y1={y} x2={tx} y2={side === 0 ? ty + 56 : ty} stroke="#ffd23f" strokeWidth={4} />
      <text
        x={tx + side * 10}
        y={ty - 6}
        textAnchor={side > 0 ? "start" : side < 0 ? "end" : "middle"}
        fontFamily={FONT}
        fontWeight={800}
        fontSize={46}
        fill="#fff"
        stroke="#111"
        strokeWidth={10}
        paintOrder="stroke"
      >
        {text}
      </text>
      {sub ? (
        <text
          x={tx + side * 10}
          y={ty + 42}
          textAnchor={side > 0 ? "start" : side < 0 ? "end" : "middle"}
          fontFamily={FONT}
          fontWeight={800}
          fontSize={40}
          fill="#ffd23f"
          stroke="#111"
          strokeWidth={9}
          paintOrder="stroke"
        >
          {sub}
        </text>
      ) : null}
    </g>
  );
};

// fade a label in while step count is within [a, b]
const labelOpacity = (f: number, a: number, b: number) => {
  const sa = STEP_FRAMES[a - 1] ?? 0;
  const sb = STEP_FRAMES[b] ?? 99999;
  return Math.min(clamp01((f - sa - 8) / 8), clamp01((sb - f) / 8));
};

export const Giant: React.FC = () => {
  const f = useCurrentFrame();
  const n = giantN(f);
  const nc = camN(f);
  const giantH = BASE_H * Math.pow(2, n);
  const camH = BASE_H * Math.pow(2, nc);
  const scale = GIANT_PX / camH;
  const gx = travelX(n);
  const camX = travelX(nc);

  // camera shake on each landing
  let shake = 0;
  for (const s of STEP_FRAMES) {
    const t = f - (s + 7);
    if (t >= 0 && t < 30) shake += 12 * Math.exp(-t / 5) * Math.sin(t * 2.6);
  }
  const ox = W / 2 + shake * 0.4;
  const oy = FEET_Y + shake;
  const sx = (x: number) => ox + (x - camX) * scale;
  const sy = (y: number) => oy - y * scale;

  // which step are we in (for leg phase)
  const k = stepsDone(f);
  const sk = STEP_FRAMES[k - 1];
  const phase = k > 0 && f - sk < 12 ? clamp01((f - sk) / 12) : 1;
  const inRewind = f >= REWIND_START && f < REWIND_END;

  // sky by altitude of the top of frame
  const topAlt = Math.log10(camH * (FEET_Y / GIANT_PX));
  const skyTop = ramp(
    [
      [1, "#7cc8ff"],
      [3.3, "#5aa9f0"],
      [4.2, "#2f6fc4"],
      [4.8, "#16245a"],
      [5.3, "#05071a"],
      [9, "#02030b"],
    ],
    topAlt,
  );
  const skyBot = ramp(
    [
      [1, "#dff3ff"],
      [3.3, "#bfe4ff"],
      [4.2, "#86bdf0"],
      [4.8, "#3a5aa8"],
      [5.3, "#0b1030"],
      [9, "#04050f"],
    ],
    topAlt,
  );
  const starOp = clamp01((topAlt - 4.6) / 0.6);

  const earthR = R_EARTH * scale;
  const flatGround = earthR > 200000;
  const ballT = clamp01((3500 - earthR) / 2500); // 0 = land, 1 = blue marble

  const visible = (px: number) => px > 0.6;

  return (
    <AbsoluteFill style={{ background: skyBot }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={skyTop} />
            <stop offset="1" stopColor={skyBot} />
          </linearGradient>
          <radialGradient id="ocean" cx="0.35" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#5fb2ff" />
            <stop offset="0.6" stopColor="#1f63c4" />
            <stop offset="1" stopColor="#0c2f6e" />
          </radialGradient>
          <radialGradient id="moon" cx="0.35" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#f2f2f2" />
            <stop offset="1" stopColor="#9a9a9a" />
          </radialGradient>
          <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#5f8f4e" />
            <stop offset="1" stopColor="#2f4f2a" />
          </linearGradient>
        </defs>
        <rect width={W} height={H} fill="url(#sky)" />
        {STARS.map((s, i) => (
          <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#fff" opacity={starOp * (0.5 + ((i * 13) % 5) / 10)} />
        ))}

        {/* moon */}
        {(() => {
          const r = Math.max(1737e3 * scale, 9);
          const cx = sx(XC + 110_000e3);
          const cy = sy(384_400e3);
          if (cy > H + r || cy < -r - 400) return null;
          return (
            <g>
              <circle cx={cx} cy={cy} r={r} fill="url(#moon)" />
              <Label x={cx} y={cy} text="달" sub="384,400km" opacity={labelOpacity(f, 26, 40)} side={0} />
            </g>
          );
        })()}

        {/* ISS */}
        {(() => {
          const cx = sx(XC + 260e3);
          const cy = sy(400e3);
          const s = Math.max(100 * scale, 18);
          if (cy < -100 || cy > H + 100) return null;
          return (
            <g>
              <rect x={cx - s} y={cy - s * 0.12} width={s * 2} height={s * 0.24} fill="#c7d3e6" />
              <rect x={cx - s * 0.2} y={cy - s * 0.25} width={s * 0.4} height={s * 0.5} fill="#e6e6e6" />
              <Label x={cx} y={cy} text="우주정거장" sub="400km" opacity={labelOpacity(f, 17, 19)} />
            </g>
          );
        })()}

        {/* edge of space */}
        {(() => {
          const y = sy(100e3);
          if (y < 0 || y > H) return null;
          const op = labelOpacity(f, 15, 17);
          return (
            <g opacity={op}>
              <line x1={0} x2={W} y1={y} y2={y} stroke="#9fd3ff" strokeWidth={4} strokeDasharray="18 14" />
              <text x={40} y={y - 18} fontFamily={FONT} fontWeight={800} fontSize={44} fill="#fff" stroke="#111" strokeWidth={9} paintOrder="stroke">
                우주 시작 100km
              </text>
            </g>
          );
        })()}

        {/* clouds */}
        {CLOUDS.map((c, i) => {
          const w = c.w * scale;
          if (!visible(w) || w > 4000) return null;
          const cx = sx(c.x);
          const cy = sy(c.y);
          if (cx < -w || cx > W + w) return null;
          return (
            <g key={i} opacity={0.85}>
              <ellipse cx={cx} cy={cy} rx={w * 0.5} ry={w * 0.12} fill="#ffffff" />
              <ellipse cx={cx - w * 0.15} cy={cy - w * 0.08} rx={w * 0.22} ry={w * 0.12} fill="#ffffff" />
              <ellipse cx={cx + w * 0.12} cy={cy - w * 0.1} rx={w * 0.18} ry={w * 0.11} fill="#ffffff" />
            </g>
          );
        })}

        {/* plane */}
        {(() => {
          const t = clamp01((f - (STEP_FRAMES[11] ?? 0)) / 160);
          if (t <= 0 || t >= 1) return null;
          const s = Math.max(70 * scale, 60);
          const cx = sx(XC + 9000 - 18000 * t);
          const cy = sy(10000);
          return (
            <g>
              <g transform={`translate(${cx} ${cy}) scale(${s / 100}) scale(-1 1)`}>
                <path d="M -50 -6 L 40 -6 Q 52 0 40 6 L -50 6 Z" fill="#f5f7fa" stroke="#333" strokeWidth={2} />
                <path d="M -5 0 L -25 30 L -12 30 L 15 0 Z" fill="#d7dde6" stroke="#333" strokeWidth={2} />
                <path d="M -40 -4 L -52 -22 L -44 -22 L -30 -4 Z" fill="#d7dde6" stroke="#333" strokeWidth={2} />
              </g>
              <Label x={cx} y={cy} text="비행기" sub="10km" opacity={labelOpacity(f, 12, 14)} side={-1} />
            </g>
          );
        })()}

        {/* mountains */}
        {[EVEREST, BAEKDU].map((m, i) => {
          const hpx = m.h * scale;
          if (!visible(hpx) || !flatGround) return null;
          const l = sx(m.x - m.half);
          const r = sx(m.x + m.half);
          const px = sx(m.x);
          const py = sy(m.h);
          const base = sy(0);
          const isB = m === BAEKDU;
          const crater = isB ? (r - l) * 0.04 : 0;
          return (
            <g key={i}>
              <path
                d={`M ${l} ${base} Q ${(l + px) / 2} ${base - hpx * 0.35} ${px - crater * 2} ${py} L ${px - crater} ${py + crater * 0.6} L ${px + crater} ${py + crater * 0.6} L ${px + crater * 2} ${py} Q ${(r + px) / 2} ${base - hpx * 0.35} ${r} ${base} Z`}
                fill={isB ? "#6d7f5c" : "#7d8794"}
              />
              <path
                d={`M ${px - (r - l) * 0.08} ${py + hpx * 0.18} L ${px - crater * 2} ${py} L ${px + crater * 2} ${py} L ${px + (r - l) * 0.08} ${py + hpx * 0.18} Z`}
                fill="#f4f7fb"
              />
              {isB ? (
                <Label x={px} y={py} text="백두산" sub="2,744m" opacity={labelOpacity(f, 11, 11)} />
              ) : (
                <Label x={px} y={py} text="에베레스트" sub="8,849m" opacity={labelOpacity(f, 13, 14)} side={1} />
              )}
            </g>
          );
        })}

        {/* city */}
        {flatGround &&
          BUILDINGS.map((b, i) => {
            const w = b.w * scale;
            const h = b.h * scale;
            if (!visible(h)) return null;
            const x = sx(b.x - b.w / 2);
            if (x > W + 50 || x + w < -50) return null;
            const y = sy(b.h);
            const rows = Math.floor(b.h / 3);
            const cols = Math.max(2, Math.floor(b.w / 4));
            const showWin = b.windows && h / rows > 5;
            return (
              <g key={i}>
                <rect x={x} y={y} width={w} height={h} fill={b.color} />
                {showWin &&
                  Array.from({ length: rows }).flatMap((_, r) =>
                    Array.from({ length: cols }).map((__, c) => (
                      <rect
                        key={`${r}-${c}`}
                        x={x + (w / cols) * (c + 0.25)}
                        y={y + (h / rows) * (r + 0.3)}
                        width={(w / cols) * 0.5}
                        height={(h / rows) * 0.45}
                        fill="#6f8aa8"
                        opacity={0.55}
                      />
                    )),
                  )}
              </g>
            );
          })}
        {/* Lotte World Tower */}
        {flatGround &&
          (() => {
            const h = LOTTE_H * scale;
            if (!visible(h)) return null;
            const cx = sx(LOTTE_X);
            const b = sy(0);
            const t = sy(LOTTE_H);
            const hw = 34 * scale;
            return (
              <g>
                <path d={`M ${cx - hw} ${b} L ${cx - hw * 0.15} ${t} L ${cx + hw * 0.15} ${t} L ${cx + hw} ${b} Z`} fill="#dfe9f5" />
                <path d={`M ${cx} ${b} L ${cx} ${t}`} stroke="#9fb4cc" strokeWidth={Math.max(1, hw * 0.06)} />
                <Label x={cx} y={t} text="롯데월드타워" sub="555m" opacity={labelOpacity(f, 9, 10)} side={0} />
              </g>
            );
          })()}
        {/* bus + trees + people near the start */}
        {flatGround &&
          (() => {
            const items: React.ReactNode[] = [];
            const busW = 11 * scale;
            if (visible(busW)) {
              const x = sx(3.5);
              const y = sy(3.2);
              const h = 3.2 * scale;
              items.push(
                <g key="bus">
                  <rect x={x} y={y} width={busW} height={h * 0.85} rx={h * 0.15} fill="#2f7fe0" />
                  <rect x={x + busW * 0.05} y={y + h * 0.12} width={busW * 0.9} height={h * 0.3} fill="#cfe7ff" />
                  <circle cx={x + busW * 0.2} cy={y + h * 0.85} r={h * 0.15} fill="#222" />
                  <circle cx={x + busW * 0.8} cy={y + h * 0.85} r={h * 0.15} fill="#222" />
                  <Label x={x + busW / 2} y={y} text="버스" sub="3.2m" opacity={labelOpacity(f, 2, 2)} side={1} />
                </g>,
              );
            }
            for (const tx of [-12, 13, 26, -20]) {
              const h = 6 * scale;
              if (!visible(h)) continue;
              items.push(
                <g key={`t${tx}`}>
                  <rect x={sx(tx) - h * 0.04} y={sy(2.5)} width={h * 0.08} height={2.5 * scale} fill="#7a5a3a" />
                  <circle cx={sx(tx)} cy={sy(4)} r={h * 0.3} fill="#4fa35a" />
                </g>,
              );
            }
            for (const px of [-6, 16]) {
              const h = 1.7 * scale;
              if (!visible(h)) continue;
              items.push(
                <g key={`p${px}`} transform={`translate(${sx(px)} ${sy(0)}) scale(${h})`}>
                  <rect x={-0.07} y={-0.85} width={0.14} height={0.4} rx={0.05} fill="#5b6b8a" />
                  <rect x={-0.05} y={-0.48} width={0.1} height={0.48} rx={0.04} fill="#333" />
                  <circle cx={0} cy={-0.93} r={0.07} fill="#e8b98f" />
                </g>,
              );
            }
            const fourOp = labelOpacity(f, 3, 3);
            if (fourOp > 0)
              items.push(<Label key="l4" x={sx(18)} y={sy(13)} text="4층 건물" sub="13m" opacity={fourOp} />);
            const aptOp = labelOpacity(f, 5, 6);
            if (aptOp > 0)
              items.push(<Label key="la" x={sx(104)} y={sy(45)} text="아파트 15층" sub="45m" opacity={aptOp} />);
            return items;
          })()}

        {/* ground / earth */}
        {flatGround ? (
          <g>
            <rect x={0} y={sy(0)} width={W} height={H} fill="url(#ground)" />
            <rect x={0} y={sy(0)} width={W} height={Math.min(Math.max(3 * scale, 6), 40)} fill="#8a8f96" />
          </g>
        ) : (
          (() => {
            const cx = sx(XC);
            const cy = sy(-R_EARTH);
            return (
              <g>
                <circle cx={cx} cy={cy} r={earthR + Math.max(earthR * 0.035, 3)} fill="#8fd0ff" opacity={0.35} />
                <circle cx={cx} cy={cy} r={earthR} fill="url(#ground)" opacity={1 - ballT} />
                <g opacity={ballT}>
                  <circle cx={cx} cy={cy} r={earthR} fill="url(#ocean)" />
                  <ellipse cx={cx - earthR * 0.3} cy={cy - earthR * 0.25} rx={earthR * 0.28} ry={earthR * 0.2} fill="#4f9a55" />
                  <ellipse cx={cx + earthR * 0.35} cy={cy + earthR * 0.1} rx={earthR * 0.22} ry={earthR * 0.32} fill="#5aa65c" />
                  <ellipse cx={cx - earthR * 0.1} cy={cy + earthR * 0.45} rx={earthR * 0.25} ry={earthR * 0.12} fill="#6aae62" />
                  <ellipse cx={cx + earthR * 0.05} cy={cy - earthR * 0.85} rx={earthR * 0.35} ry={earthR * 0.1} fill="#f4f8ff" opacity={0.9} />
                </g>
                <Label x={cx} y={cy} text="지구" sub="지름 12,742km" opacity={labelOpacity(f, 21, 40)} side={-1} {...(earthR < 60 ? { dx: -190, dy: -30 } : {})} />
              </g>
            );
          })()
        )}

        {/* landing dust ring */}
        {STEP_FRAMES.map((s, i) => {
          const t = (f - (s + 7)) / 16;
          if (t < 0 || t > 1) return null;
          const hp = giantH * scale;
          return (
            <ellipse
              key={i}
              cx={sx(gx) + 0.05 * hp}
              cy={sy(0)}
              rx={hp * (0.12 + 0.55 * easeOut(t))}
              ry={hp * (0.02 + 0.06 * easeOut(t))}
              fill="none"
              stroke="#ffffff"
              strokeWidth={Math.max(3, hp * 0.012)}
              opacity={(1 - t) * 0.8}
            />
          );
        })}

        {/* the giant */}
        <g transform={`translate(${sx(gx)} ${sy(0)}) scale(${giantH * scale})`} opacity={inRewind ? 0.9 : 1}>
          <Person phase={phase} parity={k % 2} />
        </g>
      </svg>

      <Hud f={f} giantH={giantH} />
    </AbsoluteFill>
  );
};

const Hud: React.FC<{ f: number; giantH: number }> = ({ f, giantH }) => {
  const k = stepsDone(f);
  const isCover = f < REWIND_START;
  const hudOp = isCover ? 0 : clamp01((f - REWIND_END) / 8);
  const cap = CAPTIONS.find(([a, b]) => f >= a && f <= b);
  const endOp = clamp01((f - END_START) / 10);
  const last = STEP_FRAMES[k - 1] ?? -100;
  const pop = 1 + 0.18 * Math.exp(-(f - last) / 4) * (f >= last ? 1 : 0);
  const outline: React.CSSProperties = {
    WebkitTextStroke: "12px #111",
    paintOrder: "stroke fill",
  };
  return (
    <AbsoluteFill style={{ fontFamily: FONT, fontWeight: 800, color: "#fff" }}>
      {isCover || f < REWIND_START + 6 ? (
        <div
          style={{
            position: "absolute",
            top: 150,
            width: "100%",
            textAlign: "center",
            opacity: interpolate(f, [REWIND_START - 4, REWIND_START + 6], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div style={{ fontSize: 96, lineHeight: 1.15, ...outline }}>한 걸음마다</div>
          <div style={{ fontSize: 120, lineHeight: 1.15, color: "#ffd23f", ...outline }}>키가 2배?</div>
        </div>
      ) : null}
      <div style={{ position: "absolute", top: 120, width: "100%", textAlign: "center", opacity: hudOp }}>
        <div style={{ fontSize: 56, ...outline }}>{k}걸음</div>
        <div style={{ fontSize: 130, lineHeight: 1.05, color: "#ffd23f", transform: `scale(${pop})`, ...outline }}>
          {fmtHeight(giantH)}
        </div>
      </div>
      {cap && f < END_START ? (
        <div
          style={{
            position: "absolute",
            top: 1380,
            left: 50,
            right: 120,
            textAlign: "center",
            fontSize: 58,
            lineHeight: 1.25,
            ...outline,
          }}
        >
          {cap[2]}
        </div>
      ) : null}
      {endOp > 0 ? (
        <div style={{ position: "absolute", top: 1330, left: 40, right: 120, textAlign: "center", opacity: endOp }}>
          <div style={{ fontSize: 70, ...outline }}>여러분이라면</div>
          <div style={{ fontSize: 84, color: "#ffd23f", ...outline }}>몇 걸음에서 멈출래요?</div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
