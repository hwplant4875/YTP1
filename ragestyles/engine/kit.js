// Shared helpers for RageStyles specs: VO loading, caption groups, clips with speed ramps, counters.
import { clamp, ease, W, H } from '/engine/fx.js';

export async function loadVO(dir, ids) {
  const out = {};
  for (const id of ids) out[id] = await (await fetch(`/@work/${dir}/${id}.json`)).json();
  return out;
}

// split timed words into caption groups (≤ maxWords, break after punctuation)
export function groups(words, t0, { maxWords = 3, maxChars = 16, hl = [], big = [] } = {}) {
  const gs = []; let cur = [];
  const clean = w => w.replace(/[".,!?…]+/g, '').replace(/^"|"$/g, '');
  words.forEach((w, i) => {
    const txt = clean(w.w).toUpperCase(); if (!txt) return;
    const key = txt.replace(/[^A-Z0-9']/g, '');
    cur.push({ w: txt, t: t0 + w.s, e: t0 + w.e, hl: hl.includes(key), big: big.includes(key) });
    const chars = cur.reduce((a, x) => a + x.w.length + 1, 0);
    const punct = /[.,!?…]$/.test(w.w);
    if (cur.length >= maxWords || chars >= maxChars || punct || i === words.length - 1) { gs.push(cur); cur = []; }
  });
  gs.forEach((g, i) => { g.end = i < gs.length - 1 ? gs[i + 1][0].t - 0.02 : g.at(-1).e + 0.35; });
  return gs;
}
export function drawGroups(R, gs, t, opts = {}) {
  gs.forEach((g, i) => {
    const next = gs[i + 1] ? gs[i + 1][0].t : Infinity;
    if (t >= g[0].t - 0.001 && t < next && t <= g.end + 0.15) R.caption(g, t, { ...opts, end: g.end });
  });
}

// clip playback: source time for timeline t with in-point, speed and optional freeze
export const srcTime = (t, start, { in: inp = 0, speed = 1, ramp = null, freezeAt = null } = {}) => {
  let st = (t - start);
  if (ramp) {   // ramp: [[timelineOffset, speed], ...] piecewise-constant speed
    let acc = 0, prevT = 0, prevS = ramp[0][1];
    for (const [rt, rs] of ramp) { if (st <= rt) break; acc += (rt - prevT) * prevS; prevT = rt; prevS = rs; }
    st = acc + (st - prevT) * prevS;
  } else st *= speed;
  if (freezeAt != null) st = Math.min(st, freezeAt);
  return inp + st;
};

// fallback card when a clip isn't available yet
export function placeholder(R, label, t) {
  const g = R.g; const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#1a1a1d'); gr.addColorStop(1, '#070708');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  R.text('[ ' + label + ' ]', W / 2, H * .45, { size: 54, font: 'Mont', weight: 800, color: '#555' });
}

// rolling number formatter
export const fmt = n => Math.round(n).toLocaleString('en-US');

// cue collector
export function cueList() {
  const list = [];
  const add = (file, t, db = 0, extra = {}) => { list.push({ file, t: +t.toFixed(3), db, ...extra }); };
  return { list, add };
}
