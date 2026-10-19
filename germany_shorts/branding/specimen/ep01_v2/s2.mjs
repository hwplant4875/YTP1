import fs from 'fs';
import { K, W, H, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, place, toScr, sharkSolid, sharkInside, sharkXray, bob, PT, icon, ICON, cross, count, SHARK } from './eng2.mjs';
import { at } from './tl2.mjs';
const MAP = JSON.parse(fs.readFileSync('/tmp/claude-0/sp/map.json'));
const LIVER = 'M445 238 C480 226 620 222 712 236 C690 262 640 284 560 286 C500 288 460 270 445 238Z';

// 10 biggest organ: not heart, not stomach → liver, 1/4
export function n10(t) {
  const cx = 960, cy = 640, sc = 1.42, y = cy + bob(t, 5);
  const tl = at('n10', "It's the liver"), tq = at('n10', 'a quarter');
  const glow = sm(tl, tl + 0.4, t), puls = 1 + 0.04 * Math.sin(t * 6) * glow;
  let s = place(cx, y, sc, sharkInside({}, K.navy, 5.5));
  if (glow > 0) { const [lx, ly] = PT.liver; s += place(cx, y, sc, `<g transform="translate(${lx} ${ly}) scale(${f1(puls * 100) / 100}) translate(${-lx} ${-ly})"><path d="${LIVER}" fill="${K.yellow}" stroke="#fff" stroke-width="${f1(6 * glow)}"/></g>`); }
  const P = n => toScr(cx, y, sc, ...PT[n]);
  if (t < tl) s += big(960, 200, '?', t, at('n10', 'can you guess'), { size: 230, fill: K.yellow, stroke: K.navy, sw: 12 });
  const th = at('n10', 'not the heart'), ts = at('n10', 'not the stomach');
  if (t < tl) { s += tag(...P('heart'), 1480, 300, 'HEART', t, th, { col: K.red, txt: '#fff' }) + cross(1480, 300, 70, t, th + 0.5);
    s += tag(...P('stomach'), 560, 300, 'STOMACH', t, ts, { col: K.purple, txt: '#fff' }) + cross(560, 300, 70, t, ts + 0.5); }
  s += tag(...P('liver'), 760, 990, 'LIVER', t, tl, { col: K.yellow, size: 90 });
  if (t > tq) { const k = pop(tq, t), a = Math.PI * 0.5 * eo(tq + 0.2, tq + 0.9, t);
    s += `<g transform="translate(1340 220) scale(${f1(k * 100) / 100})"><circle r="120" fill="#fff" stroke="${K.navy}" stroke-width="9"/><path d="M0 0 L0 -120 A120 120 0 0 1 ${f1(120 * Math.sin(a))} ${f1(-120 * Math.cos(a))}Z" fill="${K.yellow}" stroke="${K.navy}" stroke-width="6"/></g>`;
    s += big(1580, 220, '1/4', t, tq + 0.3, { size: 150, stroke: K.navy, sw: 14 }); }
  return s;
}

// 11 liver full of oil → float; fish use air, sharks use liver
export function n11(t) {
  const tf = at('n11', 'so the liver'), tm = at('n11', 'Most fish');
  let s = '';
  if (t < tf - 0.15) {
    const gx = 960, gy = 600, k = eo(at('n11', 'full of oil'), at('n11', 'full of oil') + 2.5, t);
    s += `<path d="M${gx - 260} ${gy - 340} L${gx - 220} ${gy + 330} L${gx + 220} ${gy + 330} L${gx + 260} ${gy - 340}" fill="#bfe8ff" fill-opacity=".55" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>`;
    seed(11); for (let i = 0; i < 18; i++) { const x = gx - 180 + rnd() * 360, y0 = gy + 280 - rnd() * 100, y = lerp(y0, gy - 230 + rnd() * 40, clamp(k * 1.3 - rnd() * 0.3)); s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(14 + rnd() * 10)}" fill="${K.yellow}" stroke="${K.navy}" stroke-width="3"/>`; }
    if (k > 0.8) s += `<rect x="${gx - 250}" y="${gy - 300}" width="500" height="${f1(90 * sm(0.8, 1, k))}" fill="${K.yellow}" opacity=".9"/>`;
    s += tag(gx + 250, gy - 250, 1560, 260, 'OIL', t, at('n11', 'Oil is lighter'), { col: K.yellow }) + tag(gx + 230, gy + 150, 1560, 760, 'WATER', t, at('n11', 'than water'), { col: '#fff' });
  } else if (t < tm - 0.15) {
    const wl = 600, cx = 960, sc = 1.35, y = wl - 20 + 10 * Math.sin(t * 1.8);
    s += `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="${K.deep}" opacity=".45"/>`;
    s += place(cx, y, sc, `<path d="${SHARK}" fill="#fff" stroke="${K.navy}" stroke-width="6"/><path d="${LIVER}" fill="${K.yellow}" stroke="${K.navy}" stroke-width="4"/><circle cx="905" cy="190" r="9" fill="${K.navy}"/>`);
    s += `<path d="M0 ${wl} ${Array.from({ length: 49 }, (_, i) => `L${i * 40} ${f1(wl + 8 * Math.sin(i * 0.5 + t * 2.5))}`).join(' ')}" stroke="#fff" stroke-width="6" fill="none"/>`;
    s += tag(...toScr(cx, y, sc, ...PT.liver), 960, 920, 'LIVER = FLOAT', t, at('n11', 'pool float') - 0.3, { col: K.yellow, size: 84 });
    const k = pop(at('n11', 'pool float'), t); if (k > 0) s += `<g transform="translate(1640 250) rotate(${f1(8 * Math.sin(t * 2))}) scale(${f1(k * 100) / 100})"><circle r="120" fill="none" stroke="${K.red}" stroke-width="62"/><circle r="120" fill="none" stroke="#fff" stroke-width="62" stroke-dasharray="94 94"/><circle r="151" fill="none" stroke="${K.navy}" stroke-width="6"/><circle r="89" fill="none" stroke="${K.navy}" stroke-width="6"/></g>`;
  } else {
    const ts = at('n11', "Sharks don't have one"), tu = at('n11', 'They use their liver');
    s += `<g transform="translate(560 560) scale(2.3)">${ICON.fish()}<ellipse cx="0" cy="0" rx="42" ry="22" fill="#fff" stroke="${K.navy}" stroke-width="4" opacity="${f1(sm(tm + 0.5, tm + 0.9, t))}"/></g>`;
    s += tag(560, 560, 560, 220, 'AIR BUBBLE', t, at('n11', 'a bubble of air'), { col: '#fff' });
    if (t > ts - 0.1) { s += place(1400, 560, 0.75, `<path d="${SHARK}" fill="#fff" stroke="${K.navy}" stroke-width="8"/><path d="${LIVER}" fill="${K.yellow}" stroke="${K.navy}" stroke-width="6" opacity="${f1(sm(tu, tu + 0.3, t))}"/><circle cx="905" cy="190" r="10" fill="${K.navy}"/>`);
      s += big(1400, 230, 'NO BUBBLE', t, ts, { size: 100, fill: K.red, stroke: '#fff', sw: 12 }) + tag(...toScr(1400, 560, 0.75, ...PT.liver), 1400, 880, 'LIVER', t, tu, { col: K.yellow }); }
  }
  return s;
}

// 12 liver oil = fuel
export function n12(t) {
  const cx = 960, cy = 640, r = 330, tb = at('n12', 'burns it');
  const lev = 1 - 0.7 * eo(tb, tb + 3, t), a = Math.PI * (1 - lev);
  let s = `<path d="M${cx - r} ${cy} A${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="#fff" stroke-width="60" opacity=".35" stroke-linecap="round"/>`;
  s += `<path d="M${cx - r} ${cy} A${r} ${r} 0 0 1 ${f1(cx - r * Math.cos(a))} ${f1(cy - r * Math.sin(a))}" fill="none" stroke="${K.yellow}" stroke-width="60" stroke-linecap="round"/>`;
  s += `<path d="M${cx} ${cy} L${f1(cx - (r - 70) * Math.cos(a))} ${f1(cy - (r - 70) * Math.sin(a))}" stroke="${K.navy}" stroke-width="22" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="36" fill="${K.navy}"/>`;
  s += big(cx - r, cy + 90, 'E', t, -1, { size: 90 }) + big(cx + r, cy + 90, 'F', t, -1, { size: 90 });
  s += big(cx, 170, 'FUEL', t, at('n12', 'also fuel'), { size: 200, fill: K.yellow, stroke: K.navy, sw: 16 });
  const sx = lerp(-200, 2100, ((t * 0.12) % 1));
  s += place(sx, 930, 0.28, sharkSolid('#fff', K.navy, 18));
  s += icon('car', 1580, 860, 0.7, t, at('n12', 'like a car'));
  return s;
}

// 13 Nicole's trip
export function n13(t) {
  const tt = at('n13', 'Nicole'), to = at('n13', 'She swam'), tb = at('n13', 'and back again'), tk = at('n13', 'About twenty');
  let s = `<g transform="translate(0 40)"><path d="${MAP.land}" fill="${K.sand}" stroke="${K.navy}" stroke-width="4" stroke-linejoin="round"/>`;
  const [sx, sy0] = MAP.sa, [ax, ay0] = MAP.au, sy = sy0 + 40, ay = ay0 + 40;
  const ko = eo(to, to + 2.6, t), kb = eo(tb, tb + 2.4, t);
  const dr = (d, k, c) => k <= 0 ? '' : `<path d="${d}" pathLength="1" stroke="${c}" stroke-width="14" fill="none" stroke-linecap="round" stroke-dasharray="${f1(k * 1000) / 1000} 2"/>`;
  s += dr(MAP.out, ko, '#fff') + dr(MAP.back, kb, K.yellow) + `</g>`;
  s += `<circle cx="${f1(sx)}" cy="${f1(sy)}" r="22" fill="${K.red}" stroke="#fff" stroke-width="7"/>`;
  if (ko > 0.97) s += `<circle cx="${f1(ax)}" cy="${f1(ay)}" r="22" fill="${K.red}" stroke="#fff" stroke-width="7"/>`;
  s += tag(sx, sy, 400, 1000, 'SOUTH AFRICA', t, at('n13', 'South Africa'), { size: 54 });
  s += tag(ax, ay, 1560, 900, 'AUSTRALIA', t, at('n13', 'Australia'), { size: 54 });
  s += tag(sx, sy, 560, 200, 'NICOLE', t, tt, { col: K.yellow, size: 90 });
  if (t > tk - 0.1) s += `<rect x="1040" y="90" width="820" height="300" rx="40" fill="${K.navy}" opacity="${f1(0.85 * sm(tk - 0.1, tk + 0.2, t))}"/>` + big(1450, 200, count(20000, t, tk, 1.2) + ' KM', t, tk, { size: 120 }) + big(1450, 320, 'IN 9 MONTHS', t, at('n13', 'nine months'), { size: 76, fill: K.yellow });
  return s;
}

// 14 fins: wings, balance, engine
export function n14(t) {
  const te = at('n14', 'the engine'), wag = t > te ? 5 * Math.sin((t - te) * 9) : 0;
  const cx = 960, cy = 560, sc = 1.42, y = cy + bob(t, 6);
  let s = place(cx, y, sc, sharkSolid('#fff', K.navy, 6), { rot: wag * 0.3 });
  const tw = at('n14', 'airplane wings'), tl = at('n14', 'They lift'), tr = at('n14', 'stops it from rolling');
  const P = n => toScr(cx, y, sc, ...PT[n]);
  s += tag(...P('pec'), 1260, 960, 'WINGS', t, tw, { col: K.cyan });
  if (t > tl) { const k = sm(tl, tl + 0.4, t), [px, py] = P('pec'); s += `<g opacity="${f1(k)}"><path d="M${f1(px)} ${f1(py - 40)} L${f1(px)} ${f1(py - 300)}" stroke="${K.yellow}" stroke-width="22" stroke-linecap="round"/><path d="M${f1(px - 45)} ${f1(py - 280)} L${f1(px)} ${f1(py - 350)} L${f1(px + 45)} ${f1(py - 280)}Z" fill="${K.yellow}"/></g>` + big(px + 180, py - 300, 'LIFT', t, tl, { size: 100, fill: K.yellow, stroke: K.navy, sw: 12 }); }
  s += tag(...P('dorsal'), 760, 150, 'BALANCE', t, tr, { col: '#fff' });
  s += tag(...P('tail'), 330, 950, 'ENGINE', t, te, { col: K.red, txt: '#fff' });
  return s;
}

// 15 40 km/h → breach
export function n15(t) {
  const tc = at('n15', 'Off the coast'); let s = '';
  if (t < tc - 0.15) {
    const cx = 960, cy = 680, r = 400, t0 = at('n15', 'can reach'), v = 40 * eo(t0, at('n15', 'forty') + 0.8, t) + (t > at('n15', 'forty') + 0.8 ? Math.sin(t * 14) * 0.7 : 0);
    const a0 = Math.PI * 1.1, a1 = -Math.PI * 0.1, ang = x => lerp(a0, a1, x / 50), av = ang(Math.max(0, v));
    s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 1 1 ${f1(cx + r * Math.cos(a1))} ${f1(cy - r * Math.sin(a1))}" fill="none" stroke="#fff" stroke-width="50" opacity=".3"/>`;
    if (v > 0.2) s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 ${a0 - av > Math.PI ? 1 : 0} 1 ${f1(cx + r * Math.cos(av))} ${f1(cy - r * Math.sin(av))}" fill="none" stroke="${K.yellow}" stroke-width="50"/>`;
    s += `<path d="M${cx} ${cy} L${f1(cx + (r - 80) * Math.cos(av))} ${f1(cy - (r - 80) * Math.sin(av))}" stroke="${K.navy}" stroke-width="22" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="38" fill="${K.navy}"/>`;
    s += big(cx, cy + 190, Math.max(0, Math.round(v)) + ' KM/H', t, Math.min(t0, 0.3), { size: 150, stroke: K.navy, sw: 14 });
  } else {
    const wl = 640, t0 = at('n15', 'shoot up'), t1 = at('n15', 'fly right out') + 0.7, u = eo(t0, t1, t);
    s += `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="${K.deep}" opacity=".55"/>`;
    const P = u => { const x = lerp(1000, 1400, u), y = u < 0.7 ? lerp(1250, wl, Math.pow(u / 0.7, 1.2)) : wl - 380 * Math.sin((u - 0.7) / 0.3 * Math.PI / 2); return [x, y]; };
    const [x, y] = P(Math.max(u, 0.001)), [x2, y2] = P(Math.max(0, u - 0.03)), rot = u > 0.03 ? Math.atan2(y - y2, x - x2) * 180 / Math.PI : -70;
    s += `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(0.55) translate(-985 -212)"><path d="${SHARK}" fill="#fff" stroke="${K.navy}" stroke-width="12"/><circle cx="905" cy="190" r="12" fill="${K.navy}"/></g>`;
    const sealX = t > t1 - 0.3 ? 1480 + 300 * eo(t1 - 0.3, t1 + 0.6, t) : 1480;
    s += `<g transform="translate(${f1(sealX)} ${wl - 10})">${ICON.seal()}</g>`;
    if (y < wl) { seed(15); for (let i = 0; i < 18; i++) { const a = Math.PI * (0.1 + 0.8 * rnd()), d = 60 + rnd() * 260 * sm(t1 - 0.8, t1, t); s += `<circle cx="${f1(1380 + Math.cos(a) * d)}" cy="${f1(wl - Math.sin(a) * d * 0.8)}" r="${f1(8 + rnd() * 12)}" fill="#fff" opacity=".85"/>`; } }
    s += `<path d="M0 ${wl} ${Array.from({ length: 49 }, (_, i) => `L${i * 40} ${f1(wl + 8 * Math.sin(i * 0.5 + t * 2.5))}`).join(' ')}" stroke="#fff" stroke-width="6" fill="none"/>`;
    s += big(430, 230, '2 TONS', t, at('n15', 'Two tons'), { size: 140, stroke: K.navy, sw: 12 }) + big(430, 380, 'IN THE AIR!', t, at('n15', 'in the air'), { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
  }
  return s;
}

// 15b fish when small, seals after 3 m
export function n15b(t) {
  const t3 = at('n15b', 'once they grow'), tt = at('n15b', 'their teeth'), ts = at('n15b', 'hunting seals');
  const L = 1.4 + 3.6 * eo(t3 - 0.2, t3 + 2.2, t), x0 = 200, pxm = 250, ry = 520;
  let s = `<path d="M${x0} ${ry} L${x0 + 6 * pxm} ${ry}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`;
  for (let m = 0; m <= 6; m++) s += `<path d="M${x0 + m * pxm} ${ry - 20} L${x0 + m * pxm} ${ry + 20}" stroke="#fff" stroke-width="8"/>`;
  s += `<path d="M${x0 + 3 * pxm} ${ry - 330} L${x0 + 3 * pxm} ${ry + 40}" stroke="${K.yellow}" stroke-width="8" stroke-dasharray="20 16"/>` + big(x0 + 3 * pxm, ry + 90, '3 M', t, t3, { size: 90, fill: K.yellow, stroke: K.navy, sw: 10 });
  const sc = L * pxm / 970; s += `<g transform="translate(${f1(x0 - 15 * sc)} ${f1(ry - 40 - 330 * sc)}) scale(${f1(sc * 1000) / 1000})">${sharkSolid('#fff', K.navy, 6 / sc)}</g>`;
  s += icon('fish', 520, 830, 1.1, t, at('n15b', 'mostly eat fish')) + big(520, 990, 'FISH', t, at('n15b', 'mostly eat fish') + 0.2, { size: 90 });
  s += icon('seal', 1420, 830, 1.15, t, ts) + big(1420, 990, 'SEALS', t, ts + 0.2, { size: 90 });
  if (t > tt) { const k = sm(tt, tt + 1.2, t), w = lerp(40, 110, k); s += `<g transform="translate(960 900) scale(1.1)"><path d="M${f1(-w)} 0 L-8 -220 L8 -220 L${f1(w)} 0Z" fill="#fff" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/></g>`; }
  return s;
}

// 16 gills: water in, oxygen out, keep swimming
export function n16(t) {
  const ts = at('n16', 'If it stops'), stop = sm(ts, ts + 1, t), speed = 1 - stop;
  const cx = 100, cy = 520, sc = 2.6, y = cy + bob(t, 4) * speed;
  let s = place(cx, y, sc, sharkSolid('#fff', K.navy, 4));
  const gk = sm(at('n16', 'five gill'), at('n16', 'five gill') + 0.4, t);
  s += place(cx, y, sc, [0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 178 C${722 + i * 17} 210 ${720 + i * 17} 240 ${712 + i * 17} 258" stroke="${K.red}" stroke-width="7" fill="none" opacity="${f1(gk)}" stroke-linecap="round"/>`).join(''));
  s += tag(...toScr(cx, y, sc, 750, 178), 700, 130, '5 GILLS', t, at('n16', 'five gill'), { col: K.red, txt: '#fff' });
  const wk = sm(at('n16', 'Water goes in'), at('n16', 'Water goes in') + 0.4, t);
  if (wk > 0) { seed(16); for (let i = 0; i < 30; i++) { const ph = rnd(), yo = rnd() * 36 - 18; const u = (ph + (t * 0.3) * speed) % 1;
      const bx = lerp(1040, 680, u), by = 232 + yo + (u > 0.55 ? (u - 0.55) * 70 : 0); const [X, Y] = toScr(cx, y, sc, bx, by);
      s += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="10" fill="${u > 0.62 ? '#fff' : K.cyan}" stroke="${K.navy}" stroke-width="3" opacity="${f1(wk * (0.3 + 0.7 * speed))}"/>`; } }
  s += big(1690, 330, 'O₂', t, at('n16', 'pull oxygen'), { size: 170, fill: K.cyan, stroke: K.navy, sw: 14 });
  if (t < ts) s += big(960, 1000, 'KEEP SWIMMING', t, at('n16', 'keep swimming'), { size: 100, fill: K.yellow, stroke: K.navy, sw: 12 });
  if (t > ts) { const k = pop(ts, t); s += `<g transform="translate(1690 760) scale(${f1(k * 100) / 100})"><path d="M-110 -265 L110 -265 L265 -110 L265 110 L110 265 L-110 265 L-265 110 L-265 -110Z" transform="scale(.55)" fill="${K.red}" stroke="#fff" stroke-width="14"/><text y="36" font-family="Black" font-size="100" fill="#fff" text-anchor="middle">STOP</text></g>`; }
  return s;
}

// 17 heart: you = 2 loops, shark = 1 loop
export const heartShape = (c = K.red) => `<path d="M0 90 C-160 -10 -150 -140 -60 -140 C-20 -140 0 -110 0 -90 C0 -110 20 -140 60 -140 C150 -140 160 -10 0 90Z" fill="${c}" stroke="${K.navy}" stroke-width="9" stroke-linejoin="round"/>`;
export function n17(t) {
  const ty = at('n17', 'Your heart'), tsk = at('n17', "A shark's heart"); let s = '';
  if (t < ty - 0.15) { const b = 1 + 0.08 * Math.max(0, Math.sin(t * 7)); s += `<g transform="translate(960 520) scale(${f1(b * 2.2 * 100) / 100})">${heartShape()}</g>` + big(960, 900, 'HEART', t, 0.3, { size: 150 }); }
  else if (t < tsk - 0.15) {
    s += `<path d="M960 540 C760 300 560 300 560 540 C560 780 760 780 960 540 C1160 300 1360 300 1360 540 C1360 780 1160 780 960 540Z" fill="none" stroke="#fff" stroke-width="22"/>`;
    s += `<g transform="translate(960 540) scale(.7)">${heartShape()}</g>` + big(960, 170, 'YOU: 2 LOOPS', t, ty, { size: 120 }) + big(560, 880, 'LUNGS', t, ty + 0.5, { size: 70, fill: K.cyan }) + big(1360, 880, 'BODY', t, ty + 0.5, { size: 70, fill: K.cyan });
  } else {
    const cx = 960, cy = 580, R = 300;
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#fff" stroke-width="24"/>`;
    const st = [['HEART', Math.PI * 0.5, K.red, at('n17', 'Heart,')], ['GILLS', Math.PI * 1.17, K.cyan, at('n17', 'gills,')], ['BODY', Math.PI * 1.83, K.yellow, at('n17', 'body,')]];
    st.forEach(([n, a, c, tn]) => { const x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R, k = 1 + 0.25 * (1 - sm(tn, tn + 0.5, t)) * (t > tn ? 1 : 0);
      s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(70 * k)}" fill="${c}" stroke="${K.navy}" stroke-width="9"/>` + tag(x, y, x + (Math.cos(a) > 0.1 ? 330 : Math.cos(a) < -0.1 ? -330 : 0), y + (Math.sin(a) > 0 ? 150 : -60), n, t, tsk + 0.3, { col: c, line: false, size: 64 }); });
    const u = (t - tsk) * 0.35, a = Math.PI * 0.5 + u * Math.PI * 2; s += `<circle cx="${f1(cx + Math.cos(a) * R)}" cy="${f1(cy + Math.sin(a) * R)}" r="30" fill="${K.red}" stroke="#fff" stroke-width="8"/>`;
    s += big(960, 120, 'SHARK: 1 LOOP', t, tsk, { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
  }
  return s;
}

// 18 warm-bodied: thermal view, +14°C
export function n18(t) {
  const tm = at('n18', 'Most fish are'), tw = at('n18', 'But a great white'), t14 = at('n18', 'fourteen degrees'), tf = at('n18', 'fast muscles');
  let s = '';
  if (t < tw - 0.15) {
    s += big(960, 220, 'MOST FISH', t, tm, { size: 120 });
    if (t > tm) s += `<g transform="translate(960 600) scale(2.6)">${ICON.fish('#5a8cff')}</g>` + big(960, 930, 'COLD', t, at('n18', 'as cold'), { size: 140, fill: K.cyan, stroke: K.navy, sw: 12 });
  } else {
    const cx = 860, cy = 560, sc = 1.3, w = sm(tw, tw + 1.5, t);
    s += place(cx, cy + bob(t, 5), sc, `<defs><radialGradient id="th18" cx=".45" cy=".55" r=".5"><stop offset="0" stop-color="#fff6c0"/><stop offset=".3" stop-color="#ffcf3a"/><stop offset=".6" stop-color="#ff5a2a"/><stop offset="1" stop-color="#3a3cc8"/></radialGradient><clipPath id="c18"><path d="${SHARK}"/></clipPath></defs>
      <path d="${SHARK}" fill="#3a3cc8"/><rect width="1000" height="400" fill="url(#th18)" clip-path="url(#c18)" opacity="${f1(w)}"/><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="6"/>`);
    s += big(860, 170, 'WARM', t, tw + 0.5, { size: 170, fill: '#ffcf3a', stroke: K.navy, sw: 14 });
    const lv = eo(t14, t14 + 1.4, t), tx = 1730, ty0 = 820, ty1 = 300;
    s += `<rect x="${tx - 40}" y="${ty1 - 40}" width="80" height="${ty0 - ty1 + 40}" rx="40" fill="#fff" stroke="${K.navy}" stroke-width="8"/><circle cx="${tx}" cy="${ty0 + 40}" r="80" fill="${K.red}" stroke="${K.navy}" stroke-width="8"/>
      <rect x="${tx - 22}" y="${f1(lerp(ty0 - 120, ty1, lv))}" width="44" height="${f1(ty0 + 40 - lerp(ty0 - 120, ty1, lv))}" fill="${K.red}"/>`;
    s += big(1450, 230, '+14°C', t, t14, { size: 120, fill: '#fff', stroke: K.navy, sw: 12 });
    s += big(860, 960, 'FAST!', t, tf, { size: 140, fill: K.yellow, stroke: K.navy, sw: 12 });
  }
  return s;
}
