import fs from 'fs';
import { C, W, H, f1, clamp, sm, eo, lerp, open, close, grid, mono, txt, typed, words, draw, dot, cycle, header, label, seed, rnd, esc } from './eng.mjs';
import { SHARK, anatomy } from '/tmp/claude-0/hc/specimen.mjs';
import { at } from './tl.mjs';
import { cap } from './cap.mjs';
const MAP = JSON.parse(fs.readFileSync('/tmp/claude-0/sp/map.json'));
const sharkLine = (ox, oy, sc, { stroke = C.ink, w = 2.4, fill = 'none', rot = 0, flip = false } = {}) =>
  `<g transform="translate(${f1(ox)} ${f1(oy)}) rotate(${rot}) scale(${flip ? -sc : sc} ${sc})"><path d="${SHARK}" fill="${fill}" stroke="${stroke}" stroke-width="${f1(w / sc)}"/><circle cx="905" cy="190" r="7" fill="${stroke}"/></g>`;

// 09 fins: wing, keel, crescent tail
export function s09(t, len) {
  let s = open(C.navy) + grid() + header(t, 'fins', 9);
  const tw = at('s09', 'They work like the wings'), tk = at('s09', 'The tall fin'), tt = at('s09', 'And the tail'), tsp = at('s09', 'Speed.');
  const ph = t < tk - 0.2 ? 0 : t < tt - 0.2 ? 1 : 2;
  if (ph === 0) {
    s += sharkLine(560, 250, 0.8, { stroke: C.dim });
    s += `<path d="M${560 + 640 * 0.8} ${250 + 262 * 0.8} l60 70" stroke="${C.acc}" stroke-width="3"/>` + mono(560 + 640 * 0.8 + 70, 250 + 262 * 0.8 + 96, 'PECTORAL FIN · cross-section ↓', { size: 16, fill: C.acc });
    // airfoil
    const ax = 560, ay = 720, k = sm(tw - 0.2, tw + 0.5, t);
    const foil = `M${ax} ${ay} C${ax + 60} ${ay - 70} ${ax + 300} ${ay - 60} ${ax + 640} ${ay + 6} C${ax + 300} ${ay + 20} ${ax + 60} ${ay + 26} ${ax} ${ay}Z`;
    s += draw(foil, eo(0.4, 2, t), { stroke: C.ink, w: 3, fill: k > 0 ? '#1d2140' : 'none' });
    if (k > 0) { for (let i = 0; i < 7; i++) { const yy = ay - 150 + i * 50, bend = i < 3 ? -40 * (1 - i / 3) : 18 * (i - 3) / 4, off = ((t * 260 + i * 90) % 900);
        const d = `M${ax - 200} ${yy} C${ax + 100} ${yy + bend} ${ax + 500} ${yy + bend} ${ax + 860} ${yy + bend * 0.4}`;
        s += `<path d="${d}" stroke="${C.acc}" stroke-width="2" fill="none" opacity="${f1(0.35 * k)}"/><path d="${d}" pathLength="900" stroke="${C.acc}" stroke-width="4" fill="none" stroke-dasharray="60 840" stroke-dashoffset="${f1(-off)}" opacity="${f1(k)}"/>`; }
      const lk = sm(at('s09', 'creates lift'), at('s09', 'creates lift') + 0.4, t);
      s += `<g opacity="${f1(lk)}"><path d="M${ax + 260} ${ay - 40} L${ax + 260} ${ay - 230}" stroke="${C.gold}" stroke-width="6"/><path d="M${ax + 260} ${ay - 250} l-16 26 l32 0Z" fill="${C.gold}"/>${txt(ax + 290, ay - 200, 'LIFT', { font: 'Black', size: 54, fill: C.gold })}</g>`;
    }
    s += mono(ax, ay + 110, 'FIG. 9a — pectoral fin works like a wing', { size: 16 });
  } else if (ph === 1) {
    // front view: body ellipse with dorsal fin, roll test
    const cx = 760, cy = 600, rk = Math.sin((t - tk) * 2.2) * 26 * (1 - sm(tk + 1.2, tk + 3, t)) + Math.sin((t - tk) * 2.2) * 4;
    s += `<g transform="rotate(${f1(rk)} ${cx} ${cy})"><ellipse cx="${cx}" cy="${cy}" rx="150" ry="190" fill="#1d2140" stroke="${C.ink}" stroke-width="3"/>
      <path d="M${cx - 40} ${cy - 175} L${cx} ${cy - 400} L${cx + 40} ${cy - 175}Z" fill="${C.acc}" opacity=".9"/>
      <path d="M${cx - 140} ${cy + 60} L${cx - 330} ${cy + 140} L${cx - 120} ${cy + 110}Z M${cx + 140} ${cy + 60} L${cx + 330} ${cy + 140} L${cx + 120} ${cy + 110}Z" fill="#2a2e4a" stroke="${C.ink}" stroke-width="2"/></g>`;
    s += `<path d="M${cx - 260} ${cy - 330} A300 300 0 0 1 ${cx + 260} ${cy - 330}" fill="none" stroke="${C.warm}" stroke-width="3" stroke-dasharray="10 10"/>` + mono(cx, cy - 430 + 0, '', {});
    s += label(cx, cy - 300, 1160, 330, 'DORSAL FIN', 'works like a keel', sm(tk, tk + 0.4, t));
    s += `<g opacity="${f1(sm(at('s09', 'It stops'), at('s09', 'It stops') + 0.3, t))}">${mono(1160, 470, 'ROLL', { size: 20, fill: C.warm })}<text x="1160" y="560" font-family="Black" font-size="90" fill="${C.ink}">${f1(Math.abs(rk))}°</text>${mono(1160, 600, 'stabilised', { size: 18, fill: C.acc })}</g>`;
    s += mono(cx, 900, 'FIG. 9b — front view', { size: 16, anchor: 'middle' });
  } else {
    // crescent tail, symmetric lobes
    const cx = 700, cy = 560, k = eo(tt, tt + 1.4, t);
    const tail = `M${cx} ${cy - 40} C${cx + 60} ${cy - 160} ${cx + 160} ${cy - 290} ${cx + 300} ${cy - 330} C${cx + 210} ${cy - 220} ${cx + 160} ${cy - 90} ${cx + 160} ${cy} C${cx + 160} ${cy + 90} ${cx + 210} ${cy + 210} ${cx + 290} ${cy + 310} C${cx + 150} ${cy + 270} ${cx + 60} ${cy + 150} ${cx} ${cy + 40}Z`;
    s += `<g transform="translate(${-2 * cx - 300} 0) scale(-1 1)" opacity="1">` + `</g>`;
    s += draw(tail, k, { stroke: C.ink, w: 3, fill: k >= 1 ? '#1d2140' : 'none' });
    s += `<path d="M${cx - 360} ${cy - 40} L${cx} ${cy - 40} M${cx - 360} ${cy + 40} L${cx} ${cy + 40}" stroke="${C.ink}" stroke-width="3" opacity="${f1(k)}"/>`;
    const sk = sm(at('s09', 'almost the same'), at('s09', 'almost the same') + 0.4, t);
    s += `<g opacity="${f1(sk)}"><path d="M${cx - 380} ${cy} L${cx + 420} ${cy}" stroke="${C.acc}" stroke-width="2" stroke-dasharray="12 10"/>${mono(cx + 430, cy + 6, 'axis of symmetry', { size: 16, fill: C.acc })}
      ${mono(cx + 320, cy - 300, 'UPPER LOBE', { size: 18, fill: C.ink })}${mono(cx + 310, cy + 300, 'LOWER LOBE', { size: 18, fill: C.ink })}</g>`;
    if (t > tsp - 0.1) { const kk = eo(tsp - 0.1, tsp + 0.2, t);
      s += `<text x="1640" y="${f1(620 + 30 * (1 - kk))}" font-family="Black" font-size="190" fill="${C.acc}" text-anchor="end" opacity="${f1(kk)}">SPEED</text>`; }
    s += mono(cx, 960, 'FIG. 9c — crescent-shaped (lunate) tail', { size: 16, anchor: 'middle', op: 0 });
  }
  s += cap('s09', [['Now look at the fins.', {}], ['are not paddles.', { 2: C.acc }], ['They work like the wings of a plane.', { 4: C.acc }], ['creates lift,', { 1: C.gold }], ['The tall fin on its back works like a keel.', { 8: C.acc }], ['It stops the body from rolling.', {}], ['shaped like a crescent moon,', { 3: C.acc, 4: C.acc }], ['That shape is built for one thing.', {}]], t, { size: 56 });
  return s + close();
}

// 10 sprint gauge + breach
export function s10(t, len) {
  let s = open(C.navy) + grid() + header(t, 'speed', 10);
  const tc = at('s10', 'Off the coast'), ta = at('s10', 'Two tons');
  if (t < tc - 0.1) {
    const cx = 960, cy = 640, r = 330, v = 40 * eo(at('s10', 'sprint at'), at('s10', 'forty') + 0.8, t) + (t > at('s10', 'forty') + 0.8 ? Math.sin(t * 13) * 0.6 : 0);
    const a0 = Math.PI * 1.15, a1 = -Math.PI * 0.15, ang = a => lerp(a0, a1, a / 60);
    s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 1 1 ${f1(cx + r * Math.cos(a1))} ${f1(cy - r * Math.sin(a1))}" fill="none" stroke="${C.faint}" stroke-width="22"/>`;
    const av = ang(v); s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 ${a0 - av > Math.PI ? 1 : 0} 1 ${f1(cx + r * Math.cos(av))} ${f1(cy - r * Math.sin(av))}" fill="none" stroke="${C.acc}" stroke-width="22"/>`;
    for (let k = 0; k <= 60; k += 5) { const a = ang(k), big = k % 10 === 0; s += `<path d="M${f1(cx + (r - 40) * Math.cos(a))} ${f1(cy - (r - 40) * Math.sin(a))} L${f1(cx + (r - (big ? 70 : 55)) * Math.cos(a))} ${f1(cy - (r - (big ? 70 : 55)) * Math.sin(a))}" stroke="${C.ink}" stroke-width="${big ? 3 : 1.5}"/>`;
      if (big) s += mono(cx + (r - 105) * Math.cos(a), cy - (r - 105) * Math.sin(a) + 7, String(k), { size: 20, fill: C.ink, anchor: 'middle' }); }
    s += `<path d="M${cx} ${cy} L${f1(cx + (r - 60) * Math.cos(av))} ${f1(cy - (r - 60) * Math.sin(av))}" stroke="${C.warm}" stroke-width="6" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="14" fill="${C.warm}"/>`;
    s += `<text x="${cx}" y="${cy + 170}" font-family="Black" font-size="120" fill="#fff" text-anchor="middle">≈${Math.round(Math.max(0, v))}</text>` + mono(cx, cy + 210, 'km/h · short bursts', { size: 20, fill: C.acc, anchor: 'middle' });
  } else {
    const wl = 430;
    s += `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="#0a1f33"/>`;
    for (let i = 0; i < 6; i++) s += `<path d="M0 ${wl + 80 + i * 90} L${W} ${wl + 80 + i * 90}" stroke="#3fd0ff" opacity=".05"/>`;
    s += `<path d="M0 ${wl} ${Array.from({ length: 49 }, (_, i) => `L${i * 40} ${f1(wl + 5 * Math.sin(i * 0.7 + t * 3))}`).join(' ')}" stroke="${C.acc}" stroke-width="2" fill="none"/>`;
    s += mono(40, wl - 14, 'SURFACE', { size: 16, fill: C.acc });
    // seal on surface
    s += `<ellipse cx="1150" cy="${wl - 8}" rx="60" ry="18" fill="#c9cde0"/>` + mono(1150, wl - 40, 'SEAL', { size: 16, fill: C.ink, anchor: 'middle' });
    // trajectory: from deep (700,1000) up to apex (1180,180)
    const t0 = at('s10', 'by rushing up'), t1 = at('s10', 'launch') + 0.6, u = eo(t0, t1, t);
    const P = u => { const x = lerp(620, 1220, u), y = u < 0.75 ? lerp(1020, wl, Math.pow(u / 0.75, 1.3)) : wl - 260 * Math.sin((u - 0.75) / 0.25 * Math.PI / 2); return [x, y]; };
    let path = 'M'; for (let k = 0; k <= 40; k++) { const [x, y] = P(u * k / 40); path += `${f1(x)} ${f1(y)} `; }
    s += `<path d="${path}" stroke="${C.warm}" stroke-width="2" stroke-dasharray="8 8" fill="none"/>`;
    const [x, y] = P(u), [x2, y2] = P(Math.max(0, u - 0.02)), rot = Math.atan2(y - y2, x - x2) * 180 / Math.PI;
    s += `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(u > 0 ? rot : -60)}) scale(0.32) translate(-985 -212)"><path d="${SHARK}" fill="#e9e6f2"/><circle cx="905" cy="190" r="9" fill="${C.navy}"/></g>`;
    if (y < wl) for (let i = 0; i < 12; i++) { seed(i + 3); const a = rnd() * Math.PI, d = 40 + rnd() * 160 * sm(t1 - 0.6, t1 + 0.5, t); s += `<circle cx="${f1(1150 + Math.cos(a) * d)}" cy="${f1(wl - Math.sin(a) * d * 0.8)}" r="${f1(3 + rnd() * 6)}" fill="${C.acc}" opacity=".7"/>`; }
    const ak = sm(ta - 0.1, ta + 0.3, t);
    s += `<g opacity="${f1(ak)}">${mono(1400, 190, 'MASS', { size: 18 })}<text x="1400" y="270" font-family="Black" font-size="80" fill="#fff">2,000 kg</text>${mono(1400, 310, 'height above water: all of it', { size: 18, fill: C.acc })}</g>`;
    s += mono(80, 160, 'FIG. 10 — breach, seen from the side · False Bay, South Africa', { size: 16, fill: C.dim });
  }
  s += cap('s10', [['a great white can sprint', {}], ['forty kilometers per hour', { 0: C.acc, 1: C.acc }], ['Off the coast of South Africa,', {}], ['they hunt seals', { 2: C.acc }], ['launch their whole body out of the water.', { 0: C.acc }], ['Two tons, completely airborne.', { 2: C.acc }]], t, { size: 56 });
  return s + close();
}

// 11 gill-flow dashboard
export function s11(t, len) {
  let s = open(C.navy) + grid() + header(t, 'breathing', 11);
  const ts = at('s11', 'Stop swimming'), stop = sm(ts, ts + 1.2, t);
  const speed = 1 - stop;
  // head schematic (big head, left)
  const ox = -620, oy = 160, sc = 1.25;
  s += `<g transform="translate(${ox} ${oy}) scale(${sc})"><path d="${SHARK}" fill="#1d2140" stroke="${C.ink}" stroke-width="2"/><circle cx="905" cy="190" r="7" fill="${C.ink}"/>
    ${[0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 176 C${722 + i * 17} 210 ${720 + i * 17} 245 ${712 + i * 17} 264" stroke="${C.acc}" stroke-width="3" fill="none" opacity="${f1(0.4 + 0.6 * sm(at('s11', 'five gill'), at('s11', 'five gill') + 0.2 + i * 0.15, t))}"/>`).join('')}</g>`;
  // flow particles: mouth (x≈950,y≈232) → gills (790) → out slits
  const fk = sm(at('s11', 'Water goes in'), at('s11', 'Water goes in') + 0.4, t);
  if (fk > 0) { seed(11); for (let i = 0; i < 26; i++) { const ph = rnd(), yo = rnd() * 30 - 15; const u = ((ph + (t * 0.35) * speed + (stop > 0 ? (ts - t0Shift) : 0)) % 1);
      const bx = lerp(990, 700, u), by = 232 + yo + (u > 0.55 ? (u - 0.55) * 60 : 0); const [X, Y] = [ox + bx * sc, oy + by * sc];
      s += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="4" fill="${u > 0.5 ? C.dim : C.acc}" opacity="${f1(fk * (0.4 + 0.6 * speed))}"/>`; } }
  s += mono(ox + 990 * sc - 10, oy + 300 * sc, 'MOUTH ← water in', { size: 16, fill: C.acc, anchor: 'end', op: fk });
  s += mono(ox + 730 * sc, oy + 140 * sc, 'GILLS · O₂ taken', { size: 16, fill: C.acc, anchor: 'middle', op: fk });
  // dashboard
  const dx = 1080, dy = 220;
  s += `<rect x="${dx}" y="${dy}" width="720" height="560" rx="8" fill="#10132a" stroke="${C.faint}" stroke-width="2"/>` + mono(dx + 30, dy + 46, 'RAM VENTILATION MONITOR', { size: 18, fill: C.ink }) + mono(dx + 690, dy + 46, stop > 0.5 ? '● ALERT' : '● LIVE', { size: 16, fill: stop > 0.5 ? C.red : C.acc, anchor: 'end' });
  const sp = (3.2 * speed).toFixed(1);
  s += mono(dx + 30, dy + 120, 'SWIM SPEED', { size: 16 }) + `<text x="${dx + 30}" y="${dy + 210}" font-family="Black" font-size="90" fill="#fff">${sp}</text>` + mono(dx + 220, dy + 210, 'km/h', { size: 20 });
  s += mono(dx + 380, dy + 120, 'WATER FLOW', { size: 16 }) + `<text x="${dx + 380}" y="${dy + 210}" font-family="Black" font-size="90" fill="#fff">${Math.round(100 * speed)}%</text>`;
  // O2 strip chart
  const ox2 = dx + 30, oy2 = dy + 280, cw = 660, ch = 220;
  s += `<rect x="${ox2}" y="${oy2}" width="${cw}" height="${ch}" fill="none" stroke="${C.faint}"/>` + mono(ox2, oy2 - 12, 'OXYGEN IN BLOOD', { size: 16 });
  let pth = 'M'; for (let i = 0; i <= 120; i++) { const tt = t - 6 + i * 6 / 120; const st = sm(ts, ts + 1.2, tt), drop = clamp((tt - ts - 0.6) / 4) * st;
    const v = 0.8 - 0.65 * drop + 0.02 * Math.sin(tt * 9); pth += `${f1(ox2 + i * cw / 120)} ${f1(oy2 + ch - v * ch)} `; }
  s += `<path d="${pth}" fill="none" stroke="${stop > 0.3 ? C.red : C.acc}" stroke-width="3"/>`;
  const cl = sm(at('s11', 'It has to keep swimming'), at('s11', 'It has to keep swimming') + 0.4, t);
  s += mono(dx + 30, dy + 540, 'mouth slightly open · must keep moving', { size: 16, fill: C.acc, op: cl });
  s += cap('s11', [['Behind the head, five gill slits on each side.', { 3: C.acc, 4: C.acc }], ['Water goes in through the mouth,', {}], ['The gills pull the oxygen out of it.', { 4: C.acc }], ["But a great white can't pump water", { 4: C.warm }], ['It has to keep swimming,', { 3: C.acc, 4: C.acc }], ['Stop swimming, and the water stops.', { 0: C.red, 1: C.red, 5: C.red }]], t, { size: 54 });
  return s + close();
}
const t0Shift = 0;

// 12 single-loop circulation circuit (paper)
export function s12(t, len) {
  let s = open(C.paper) + header(t, 'heart', 12, { dark: false });
  const th = at('s12', 'Your heart'), tsh = at('s12', "A shark's heart");
  const box = (x, y, w, h, tx, col = C.pInk, fill = '#fff') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${col}" stroke-width="3"/>${mono(x + w / 2, y + h / 2 + 7, tx, { size: 20, fill: col, anchor: 'middle' })}`;
  // heart drawing first
  const hk = 1 - sm(th - 0.3, th, t);
  if (hk > 0) { const beat = 1 + 0.06 * Math.max(0, Math.sin(t * 7)), y = 500;
    const ch = [['SINUS', 300, 130, 90, C.pDim], ['ATRIUM', 560, 210, 150, C.red], ['VENTRICLE', 900, 250, 190, C.red], ['CONUS', 1220, 150, 80, C.pDim]];
    s += `<g opacity="${f1(hk)}"><path d="M200 ${y} L1420 ${y}" stroke="${C.pInk}" stroke-width="6" opacity=".25"/>`;
    ch.forEach(([n, x, w, h, col], i) => { const main = i === 1 || i === 2, sc = main ? beat : 1;
      s += `<g transform="translate(${x} ${y}) scale(${f1(sc * 1000) / 1000})"><ellipse rx="${w / 2}" ry="${h / 2}" fill="${main ? col : '#fff'}" fill-opacity="${main ? 0.85 : 1}" stroke="${C.pInk}" stroke-width="3"/></g>${mono(x, y + h / 2 + 40, n, { size: 18, fill: main ? C.red : C.pDim, anchor: 'middle' })}`; });
    s += `<path d="M1420 ${y} l-22 -12 l0 24Z" fill="${C.pInk}"/>${mono(200, y - 60, 'from body →', { size: 16, fill: C.pDim })}${mono(1420, y - 60, '→ to gills', { size: 16, fill: C.pDim, anchor: 'end' })}
      ${mono(730, 300, 'TWO MAIN CHAMBERS', { size: 22, fill: C.pInk, anchor: 'middle' })}<path d="M560 330 L560 400 M900 330 L900 380 M560 330 L900 330" stroke="${C.pInk}" stroke-width="2" fill="none"/></g>`; }
  // human: two loops
  const hu = sm(th - 0.2, th + 0.3, t);
  if (hu > 0) { const x = 300, y = 280;
    s += `<g opacity="${f1(hu)}">${mono(x, y - 40, 'HUMAN · 2 loops', { size: 22, fill: C.pInk })}${box(x + 150, y + 180, 140, 80, 'HEART', C.red)}${box(x + 150, y, 140, 70, 'LUNGS')}${box(x + 150, y + 380, 140, 70, 'BODY')}
      <path d="M${x + 150} ${y + 200} L${x + 60} ${y + 200} L${x + 60} ${y + 35} L${x + 150} ${y + 35} M${x + 290} ${y + 35} L${x + 380} ${y + 35} L${x + 380} ${y + 200} L${x + 290} ${y + 200}" fill="none" stroke="${C.pInk}" stroke-width="3"/>
      <path d="M${x + 150} ${y + 240} L${x + 60} ${y + 240} L${x + 60} ${y + 415} L${x + 150} ${y + 415} M${x + 290} ${y + 415} L${x + 380} ${y + 415} L${x + 380} ${y + 240} L${x + 290} ${y + 240}" fill="none" stroke="${C.pInk}" stroke-width="3"/></g>`; }
  // shark: one loop with moving dot
  const sk = sm(tsh - 0.2, tsh + 0.3, t);
  if (sk > 0) { const x = 1120, y = 260;
    const pts = [[x + 80, y + 400], [x + 80, y + 60], [x + 560, y + 60], [x + 560, y + 400], [x + 80, y + 400]];
    s += `<g opacity="${f1(sk)}">${mono(x, y - 20, 'SHARK · 1 loop', { size: 22, fill: C.pInk })}<path d="M${pts.map(p => p.join(' ')).join(' L')}" fill="none" stroke="${C.pInk}" stroke-width="3"/>
      ${box(x + 10, y + 360, 140, 80, 'HEART', C.red)}${box(x + 250, y + 25, 140, 70, 'GILLS', '#1a6f9a')}${box(x + 490, y + 360, 140, 80, 'BODY')}</g>`;
    const seq = [['heart,', 0], ['gills,', 1], ['body,', 2], ['back to the heart.', 4]];
    // dot runs the loop: param by time
    const u = (((t - tsh) * 0.22) % 1 + 1) % 1; const segs = [0, 0.25, 0.5, 0.75, 1]; let i = Math.floor(u * 4), f = u * 4 - i;
    const [a, b] = [pts[i], pts[i + 1]]; const X = lerp(a[0], b[0], f), Y = lerp(a[1], b[1], f);
    s += `<g opacity="${f1(sk)}">${dot(X, Y, { r: 9, col: C.red, glow: C.red })}</g>`; }
  s += cap('s12', [['a small heart with two main chambers.', { 4: C.red, 5: C.red }], ['Your heart sends blood around two loops.', { 5: C.red }], ["A shark's heart sends it around just one:", { 6: C.red, 7: C.red }], ['heart, gills, body, and back to the heart.', {}]], t, { size: 56, fill: C.pInk });
  return s + close(false);
}

// 13 thermal camera + counter-current exchanger
export function s13(t, len) {
  let s = open('#07080f') + header(t, 'warm muscle', 13);
  const tx = at('s13', 'Around its swimming'), t14 = at('s13', 'Parts of its body'), tf = at('s13', 'Warm muscles are');
  const ph = t < tx - 0.2 ? 0 : t < t14 - 0.2 ? 1 : 2;
  const warm = sm(at('s13', "A great white isn't."), at('s13', "A great white isn't.") + 1.2, t);
  const thermalShark = (ox, oy, sc, w) => `<defs><radialGradient id="th13" cx=".42" cy=".55" r=".45"><stop offset="0" stop-color="${w > 0.5 ? '#ffffff' : '#3a4cff'}"/><stop offset=".25" stop-color="${w > 0.5 ? '#ffd24a' : '#2a3cc0'}"/><stop offset=".55" stop-color="${w > 0.5 ? '#ff5a2a' : '#1a2a90'}"/><stop offset="1" stop-color="#1a2a90"/></radialGradient>
      <clipPath id="c13"><path d="${SHARK}"/></clipPath></defs><g transform="translate(${ox} ${oy}) scale(${sc})"><rect width="1000" height="400" fill="#121f6a" clip-path="url(#c13)"/><rect width="1000" height="400" fill="url(#th13)" clip-path="url(#c13)" opacity="${f1(w)}"/><path d="${SHARK}" fill="none" stroke="#000" stroke-width="1" opacity=".4"/></g>`;
  if (ph === 0 || ph === 2) {
    // thermal camera UI
    s += `<rect x="0" y="0" width="${W}" height="${H}" fill="#0e1550"/>`;
    seed(13); for (let i = 0; i < 60; i++) s += `<rect x="${f1(rnd() * W)}" y="${f1(rnd() * H)}" width="${f1(80 + rnd() * 200)}" height="${f1(20 + rnd() * 60)}" fill="#1a2a90" opacity=".25" filter="url(#b20)"/>`;
    s += thermalShark(330, 260, 1.25, ph === 2 ? 1 : warm);
    // corner brackets & scale bar
    s += `<path d="M120 160 L120 120 L160 120 M1800 160 L1800 120 L1760 120 M120 920 L120 960 L160 960 M1800 920 L1800 960 L1760 960" stroke="#fff" stroke-width="3" fill="none"/>`;
    s += `<defs><linearGradient id="sc13" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#1a2a90"/><stop offset=".5" stop-color="#ff5a2a"/><stop offset=".8" stop-color="#ffd24a"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>`;
    s += `<rect x="1740" y="300" width="24" height="420" fill="url(#sc13)"/>` + mono(1730, 300, '30°', { size: 16, fill: '#fff', anchor: 'end' }) + mono(1730, 724, '10°', { size: 16, fill: '#fff', anchor: 'end' });
    s += mono(150, 200, '● REC   IR · 7.5–14 µm', { size: 16, fill: '#fff' });
    const water = 12, body = water + (ph === 2 ? 14 * eo(t14, t14 + 1.5, t) : 14 * warm * 0.7);
    s += mono(150, 900, `WATER ${water.toFixed(1)} °C`, { size: 22, fill: '#9fb4ff' }) + mono(560, 900, `MUSCLE ${body.toFixed(1)} °C`, { size: 22, fill: '#ffd24a', op: Math.max(warm, ph === 2 ? 1 : 0) });
    s += `<circle cx="${330 + 420 * 1.25}" cy="${260 + 220 * 1.25}" r="22" fill="none" stroke="#fff" stroke-width="2"/><path d="M${330 + 420 * 1.25 - 34} ${260 + 220 * 1.25} h68 M${330 + 420 * 1.25} ${260 + 220 * 1.25 - 34} v68" stroke="#fff" stroke-width="2"/>`;
    if (ph === 2) { const k = eo(t14 - 0.1, t14 + 0.4, t); s += `<text x="1640" y="${f1(560 + 20 * (1 - k))}" font-family="Black" font-size="170" fill="#fff" text-anchor="end" opacity="${f1(k)}">+${Math.round(14 * eo(t14, t14 + 1.2, t))} °C</text>`;
      s += mono(1640, 610, 'up to · above the water', { size: 20, fill: '#ffd24a', anchor: 'end', op: k });
      const fk = sm(tf, tf + 0.3, t); s += mono(1640, 660, 'warm muscle = fast muscle', { size: 20, fill: '#fff', anchor: 'end', op: fk }); }
  } else {
    // counter-current exchanger schematic
    s += grid('#ffffff', 0.04);
    const y1 = 420, y2 = 600, x0 = 300, x1 = 1620;
    s += `<defs><linearGradient id="hot" x1="0" x2="1"><stop offset="0" stop-color="${C.red}"/><stop offset="1" stop-color="#ff9b6a"/></linearGradient><linearGradient id="cold" x1="0" x2="1"><stop offset="0" stop-color="#ff9b6a"/><stop offset="1" stop-color="#3a6cff"/></linearGradient></defs>`;
    const k = eo(tx, tx + 1.2, t);
    s += `<rect x="${x0}" y="${y1 - 40}" width="${f1((x1 - x0) * k)}" height="80" fill="url(#hot)" opacity=".9"/><rect x="${f1(x1 - (x1 - x0) * k)}" y="${y2 - 40}" width="${f1((x1 - x0) * k)}" height="80" fill="url(#cold)" opacity=".9"/>`;
    s += mono(x0, y1 - 60, 'WARM BLOOD · leaving the muscle →', { size: 18, fill: C.warm }) + mono(x1, y2 + 80, '← COLD BLOOD · coming in from the gills', { size: 18, fill: '#8fb0ff', anchor: 'end' });
    const hk = sm(at('s13', 'Warm blood leaving'), at('s13', 'Warm blood leaving') + 0.5, t);
    for (let i = 0; i < 9; i++) { const x = x0 + 120 + i * 140, off = ((t * 60 + i * 10) % 60);
      s += `<path d="M${x} ${y1 + 44} L${x} ${y2 - 44}" stroke="#ffd24a" stroke-width="3" stroke-dasharray="10 8" stroke-dashoffset="${f1(-off)}" opacity="${f1(hk)}"/><path d="M${x - 8} ${y2 - 58} l8 14 l8 -14" stroke="#ffd24a" stroke-width="3" fill="none" opacity="${f1(hk)}"/>`; }
    s += mono(960, 760, 'HEAT CROSSES OVER · stays inside the body', { size: 20, fill: '#ffd24a', anchor: 'middle', op: hk });
    s += mono(960, 820, 'FIG. 13 — counter-current heat exchanger (rete mirabile)', { size: 16, anchor: 'middle', op: k });
  }
  s += cap('s13', [['And now something most fish can\'t do.', {}], ['Fish are usually the same temperature', {}], ["A great white isn't.", { 2: C.warm }], ['works like a heat exchanger.', { 3: C.warm, 4: C.warm }], ['so the heat stays inside.', { 2: C.warm }], ['up to about fourteen degrees warmer', { 3: C.warm, 4: C.warm, 5: C.warm }], ['Warm muscles are faster muscles.', { 3: C.warm }], ['explode upward from below.', { 0: C.warm }]], t, { size: 56, fill: '#ffffff' });
  return s + close();
}

// 14 stomach + spiral valve (paper)
export function s14(t, len) {
  let s = open(C.paper) + header(t, 'digestion', 14, { dark: false });
  const ts = at('s14', 'After the stomach'), tc = at('s14', 'Instead of a long'), tsp = at('s14', 'Food has to spin');
  if (t < ts - 0.2) {
    // U-shaped stomach, everting
    const ev = sm(at('s14', 'push their stomach out'), at('s14', 'push their stomach out') + 1.2, t) * (1 - sm(at('s14', 'pull it back in'), at('s14', 'pull it back in') + 1, t));
    s += `<g transform="translate(560 300)"><path d="M0 0 C0 300 420 300 420 120 L420 0" fill="none" stroke="${C.pInk}" stroke-width="60" stroke-linecap="round" opacity=".12"/>
      ${draw('M0 0 C0 300 420 300 420 120 L420 0', eo(0.3, 2, t), { stroke: '#8b6bb0', w: 46 })}
      <path d="M0 0 L${f1(-140 - 160 * ev)} ${f1(-60 * ev)}" stroke="#8b6bb0" stroke-width="40" stroke-linecap="round" opacity="${f1(0.3 + 0.7 * ev)}"/>
      ${mono(210, 340, 'U-SHAPED STOMACH', { size: 20, fill: C.pInk, anchor: 'middle' })}${mono(-40, -40, '← to mouth', { size: 16, fill: C.pDim, anchor: 'end' })}${mono(460, 0, '→ spiral valve', { size: 16, fill: C.pDim })}</g>`;
    s += mono(960, 820, ev > 0.1 ? 'GASTRIC EVERSION · stomach turned out, rinsed, pulled back' : '', { size: 18, fill: C.red, anchor: 'middle', op: ev });
  } else {
    // ours vs theirs
    const ck = sm(tc - 0.2, tc + 0.3, t);
    let coil = 'M240 300'; for (let i = 0; i < 9; i++) coil += ` C${280 + i * 40} ${i % 2 ? 300 : 520} ${300 + i * 40} ${i % 2 ? 520 : 300} ${320 + i * 40} ${i % 2 ? 300 : 520}`;
    s += `<g opacity="${f1(ck)}">${mono(240, 250, 'HUMAN GUT · long, coiled', { size: 18, fill: C.pDim })}${draw(coil, eo(tc, tc + 1.5, t), { stroke: C.pDim, w: 14, op: 0.6 })}</g>`;
    // corkscrew valve
    const vx = 900, vy = 420, vw = 760, vh = 180;
    s += `<rect x="${vx}" y="${vy - vh / 2}" width="${vw}" height="${vh}" rx="${vh / 2}" fill="#fff" stroke="${C.pInk}" stroke-width="3"/>`;
    const turns = 9, k = eo(ts, ts + 1.8, t);
    let back = '', front = '';
    for (let i = 0; i < turns; i++) { const x = vx + 50 + i * (vw - 100) / turns, w = (vw - 100) / turns;
      back += `<path d="M${f1(x)} ${vy + vh / 2 - 12} C${f1(x + w * 0.2)} ${vy} ${f1(x + w * 0.3)} ${vy - vh / 2 + 12} ${f1(x + w * 0.5)} ${vy - vh / 2 + 12}" stroke="#c8b6dc" stroke-width="10" fill="none"/>`;
      front += `<path d="M${f1(x + w * 0.5)} ${vy - vh / 2 + 12} C${f1(x + w * 0.7)} ${vy - vh / 2 + 12} ${f1(x + w * 0.8)} ${vy} ${f1(x + w)} ${vy + vh / 2 - 12}" stroke="#8b6bb0" stroke-width="12" fill="none"/>`; }
    s += `<defs><clipPath id="v14"><rect x="${vx}" y="${vy - vh / 2}" width="${f1(vw * k)}" height="${vh}"/></clipPath></defs><g clip-path="url(#v14)">${back}${front}</g>`;
    s += mono(vx, vy - vh / 2 - 24, 'SPIRAL VALVE · short, twisted inside', { size: 20, fill: C.pInk });
    // food dot spiralling
    const fk = sm(tsp - 0.2, tsp + 0.2, t);
    if (fk > 0) { const u = ((t - tsp) * 0.12) % 1, x = vx + 50 + u * (vw - 100), y = vy - Math.cos(u * turns * 2 * Math.PI) * (vh / 2 - 24);
      s += dot(x, y, { r: 10, col: C.liver, glow: C.liver });
      s += mono(vx + vw / 2, vy + vh / 2 + 50, 'path length ×' + (1 + 3 * eo(tsp, tsp + 2, t)).toFixed(1) + ' · more time to absorb', { size: 18, fill: C.pInk, anchor: 'middle', op: fk }); }
  }
  s += cap('s14', [['Food goes down into a U-shaped stomach.', { 5: '#8b6bb0', 6: '#8b6bb0' }], ['push their stomach out through their mouth', { 0: C.red, 1: C.red, 2: C.red }], ['the strangest organ of all:', {}], ['the spiral valve.', { 1: '#8b6bb0', 2: '#8b6bb0' }], ['twisted inside like a corkscrew.', { 4: '#8b6bb0' }], ['Food has to spin its way through,', { 3: '#8b6bb0' }]], t, { size: 56, fill: C.pInk });
  return s + close(false);
}

// 14b tooth morph with growth
export function s14b(t, len) {
  let s = open(C.navy) + grid() + header(t, 'diet', 15);
  const t3 = at('s14b', 'But once they pass'), tsh = at('s14b', 'from narrow'), ts = at('s14b', 'Perfect for seals');
  const L = 1.2 + 3.0 * eo(t3 - 0.3, t3 + 2, t);
  // ruler
  const rx = 160, ry = 300, pxm = 260;
  s += `<path d="M${rx} ${ry} L${rx + 6 * pxm} ${ry}" stroke="${C.ink}" stroke-width="2"/>`;
  for (let m = 0; m <= 6; m++) s += `<path d="M${rx + m * pxm} ${ry - 12} L${rx + m * pxm} ${ry + 12}" stroke="${C.ink}" stroke-width="2"/>${mono(rx + m * pxm, ry + 40, m + ' m', { size: 16, anchor: 'middle' })}`;
  s += `<path d="M${rx + 3 * pxm} ${ry - 140} L${rx + 3 * pxm} ${ry + 60}" stroke="${C.warm}" stroke-width="2" stroke-dasharray="8 8"/>` + mono(rx + 3 * pxm + 10, ry - 120, '≈ 3 m · the switch', { size: 16, fill: C.warm });
  s += sharkLine(rx, ry - 20 - 0.4 * L * pxm * 0.4, L * pxm / 1000, { stroke: C.ink, fill: '#1d2140', w: 2 });
  // tooth morph
  const k = sm(tsh - 0.2, tsh + 1.4, t), cx = 620, cy = 820;
  const nar = [[-30, 0], [-6, -190], [6, -190], [30, 0]], brd = [[-90, 0], [-10, -170], [10, -170], [90, 0]];
  const pts = nar.map((p, i) => [lerp(p[0], brd[i][0], k), lerp(p[1], brd[i][1], k)]);
  let ser = ''; if (k > 0.3) for (let i = 1; i < 10; i++) { const u = i / 10; const [ax, ay] = [lerp(pts[0][0], pts[1][0], u), lerp(pts[0][1], pts[1][1], u)], [bx, by] = [lerp(pts[3][0], pts[2][0], u), lerp(pts[3][1], pts[2][1], u)];
    ser += `<path d="M${f1(cx + ax)} ${f1(cy + ay)} l-8 -4 M${f1(cx + bx)} ${f1(cy + by)} l8 -4" stroke="${C.ink}" stroke-width="2" opacity="${f1((k - 0.3) / 0.7)}"/>`; }
  s += `<path d="M${pts.map(p => f1(cx + p[0]) + ' ' + f1(cy + p[1])).join(' L')}Z" fill="#f4efe6" stroke="${C.ink}" stroke-width="3"/>${ser}`;
  s += mono(cx, cy + 40, k < 0.5 ? 'NARROW · POINTED' : 'BROAD · SERRATED', { size: 18, fill: C.acc, anchor: 'middle' });
  // menu card
  const mk = sm(at('s14b', 'Its menu'), at('s14b', 'Its menu') + 0.4, t);
  s += `<g opacity="${f1(mk)}" transform="translate(1080 520)"><rect width="640" height="360" fill="#10132a" stroke="${C.faint}" stroke-width="2"/>${mono(30, 50, 'MENU', { size: 20, fill: C.ink })}
    ${mono(30, 120, 'young  (< 3 m)', { size: 18 })}${txt(330, 124, 'fish', { font: 'SerifI', size: 52, fill: t < t3 + 1 ? C.acc : C.dim })}
    ${mono(30, 230, 'adult  (> 3 m)', { size: 18 })}${txt(330, 234, 'seals', { font: 'SerifI', size: 52, fill: t > tsh + 1 ? C.acc : C.faint })}
    ${t > ts ? `<path d="M320 250 L560 250" stroke="${C.acc}" stroke-width="3"/>${mono(30, 320, '+ dolphins, whale carcasses …', { size: 16 })}` : ''}</g>`;
  s += cap('s14b', [['Its menu changes as it grows.', { 1: C.acc }], ['Young great whites mostly eat fish.', { 5: C.acc }], ['But once they pass about three meters,', { 5: C.warm, 6: C.warm }], ['from narrow and pointed to broad and serrated.', { 5: C.acc, 7: C.acc }], ['Perfect for seals.', { 2: C.acc }]], t, { size: 56 });
  return s + close();
}

// 15 Nicole's migration (map traceroute)
export function s15(t, len) {
  let s = open(C.navy);
  s += MAP.grat.map(d => `<path d="${d}" stroke="#ffffff" opacity=".06" fill="none"/>`).join('');
  s += `<path d="${MAP.land}" fill="#1b1f36" stroke="${C.dim}" stroke-width="1.2"/>`;
  s += header(t, 'migration', 16);
  const tt = at('s15', 'scientists tagged'), to = at('s15', 'She swam'), tb = at('s15', 'and came back'), tk = at('s15', 'About twenty');
  const [sx, sy] = MAP.sa, [ax, ay] = MAP.au;
  s += `<g opacity="${f1(sm(tt - 0.3, tt + 0.3, t))}">${dot(sx, sy, { r: 8 })}${mono(sx + 16, sy + 34, 'GANSBAAI, SOUTH AFRICA', { size: 16, fill: C.ink })}${mono(sx + 16, sy + 56, 'tagged · Nov 2003', { size: 14, fill: C.acc })}</g>`;
  const ko = eo(to, to + 2.2, t), kb = eo(tb, tb + 2.2, t);
  s += draw(MAP.out, ko, { stroke: C.acc, w: 3 }) + draw(MAP.back, kb, { stroke: C.warm, w: 3, extra: 'stroke-linecap="round"' });
  if (ko > 0.98) s += `${dot(ax, ay, { r: 8, glow: C.warm })}${mono(ax + 16, ay - 14, 'WESTERN AUSTRALIA', { size: 16, fill: C.ink })}${mono(ax + 16, ay + 8, 'Feb 2004 · 99 days', { size: 14, fill: C.acc })}`;
  // terminal panel
  const px = 1240, py = 130;
  s += `<rect x="${px}" y="${py}" width="600" height="300" fill="#07080f" stroke="${C.faint}" opacity=".95"/>`;
  s += typed(px + 24, py + 44, '$ traceroute shark_P12', t, tt, { size: 18, fill: C.acc, cps: 30, cursor: false });
  const hops = [['1', 'Gansbaai, ZA', tt + 1.0], ['2', 'Indian Ocean (open water)', to + 0.6], ['3', 'Exmouth, AU', to + 2.0], ['4', 'Indian Ocean', tb + 0.6], ['5', 'Gansbaai, ZA  · home', tb + 2.0]];
  hops.forEach(([n, h, th], i) => { if (t > th) s += mono(px + 24, py + 84 + i * 30, `${n}  ${h}`, { size: 17, fill: C.ink }); });
  if (t > tk - 0.1) s += mono(px + 24, py + 250, 'total ≈ ' + cycle('20,000', t, tk, 0.8) + ' km  ·  < 9 months', { size: 20, fill: C.gold });
  s += `<text x="80" y="230" font-family="Black" font-size="66" fill="#fff" opacity="${f1(sm(tt, tt + 0.3, t))}">"Nicole"</text>` + mono(84, 270, 'adult female great white · satellite tag', { size: 16, op: sm(tt, tt + 0.3, t) });
  s += cap('s15', [['That oil-filled liver also lets great whites travel incredibly far.', { 1: C.liver }], ['scientists tagged a female named Nicole', { 5: C.acc }], ['She swam all the way to Australia,', { 5: C.acc }], ['and came back.', { 1: C.warm }], ['About twenty thousand kilometers,', { 1: C.gold, 2: C.gold }], ['in under nine months.', {}]], t, { size: 50, y: 1020 });
  return s + close();
}

// 16 ampullae + oscilloscope
export function s16(t, len) {
  let s = open(C.navy) + grid() + header(t, 'electric sense', 17);
  const tp = at('s16', 'Those dark dots'), tc = at('s16', 'Each one leads'), te = at('s16', 'They sense electricity'), th = at('s16', 'Even a fish hiding'), tn = at('s16', 'These pores');
  if (t < te - 0.2) {
    // snout close-up: shark scaled big, head in view
    const sc = 3.2, ox = 960 - 900 * sc, oy = 560 - 210 * sc;
    s += `<g transform="translate(${f1(ox)} ${f1(oy)}) scale(${sc})"><path d="${SHARK}" fill="#c9cde0" stroke="${C.ink}" stroke-width="0.8"/><circle cx="905" cy="190" r="7" fill="${C.navy}"/>
      <path d="M915 228 C935 232 960 230 975 222" stroke="${C.navy}" stroke-width="1.6" fill="none"/></g>`;
    seed(16); const pk = sm(tp - 0.2, tp + 0.6, t);
    for (let i = 0; i < 60; i++) { const bx = 925 + rnd() * 58, by = 196 + rnd() * 26 - (bx - 925) * 0.12; const [X, Y] = [ox + bx * sc, oy + by * sc];
      if (Y > oy + 222 * sc || bx > 980) continue; s += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="${f1(3 + rnd() * 3)}" fill="#1b1f36" opacity="${f1(pk)}"/>`; }
    const ck = sm(tc - 0.2, tc + 0.4, t);
    if (ck > 0) { s += `<g opacity="${f1(ck)}"><circle cx="1500" cy="300" r="190" fill="#10132a" stroke="${C.acc}" stroke-width="2"/><path d="M${f1(ox + 950 * sc)} ${f1(oy + 205 * sc)} L1350 420" stroke="${C.acc}" stroke-width="1.5"/>
        <path d="M1380 200 C1440 260 1460 320 1470 400" stroke="#e8e0c4" stroke-width="26" fill="none" stroke-linecap="round"/><ellipse cx="1480" cy="430" rx="60" ry="40" fill="#e8e0c4"/>${mono(1500, 520, 'AMPULLA OF LORENZINI', { size: 16, fill: C.acc, anchor: 'middle' })}${mono(1500, 545, 'jelly-filled canal', { size: 14, anchor: 'middle' })}</g>`; }
  } else {
    // sand + hidden fish + field lines, oscilloscope
    const sy = 520;
    s += `<rect x="0" y="${sy}" width="980" height="300" fill="#2a2618"/>`; seed(4); for (let i = 0; i < 220; i++) s += `<circle cx="${f1(rnd() * 980)}" cy="${f1(sy + rnd() * 300)}" r="${f1(1 + rnd() * 2)}" fill="#4a432c"/>`;
    const fk = sm(th - 0.3, th + 0.3, t), fx = 480, fy = sy + 90;
    s += `<g opacity="${f1(fk)}"><ellipse cx="${fx}" cy="${fy}" rx="90" ry="26" fill="none" stroke="${C.ink}" stroke-width="2" stroke-dasharray="6 6"/>${mono(fx, fy + 70, 'FLATFISH · buried', { size: 16, fill: C.ink, anchor: 'middle' })}</g>`;
    const ek = sm(te - 0.2, te + 0.6, t);
    for (let i = 1; i <= 4; i++) { const r = i * 60 + ((t * 30) % 60); s += `<ellipse cx="${fx}" cy="${fy}" rx="${f1(r * 1.4)}" ry="${f1(r)}" fill="none" stroke="${C.acc}" stroke-width="1.6" opacity="${f1(ek * (1 - r / 300) * 0.9)}"/>`; }
    s += `<g opacity="${f1(ek)}" transform="translate(${fx - 340} ${sy - 360}) scale(0.5)"><path d="${SHARK}" fill="#c9cde0"/><circle cx="905" cy="190" r="9" fill="${C.navy}"/></g>`;
    // oscilloscope
    const ox = 1060, oy = 220, ow = 740, oh = 520;
    s += `<rect x="${ox}" y="${oy}" width="${ow}" height="${oh}" rx="10" fill="#081410" stroke="${C.faint}" stroke-width="2"/>`;
    for (let i = 1; i < 10; i++) s += `<path d="M${ox + i * ow / 10} ${oy} L${ox + i * ow / 10} ${oy + oh}" stroke="${C.acc}" opacity=".08"/>`;
    for (let i = 1; i < 8; i++) s += `<path d="M${ox} ${oy + i * oh / 8} L${ox + ow} ${oy + i * oh / 8}" stroke="${C.acc}" opacity=".08"/>`;
    let p = 'M'; for (let i = 0; i <= 200; i++) { const x = i / 200, tt = t * 1.4 + x * 3; const beat = Math.exp(-Math.pow(((tt % 1) - 0.3) * 18, 2)) - 0.4 * Math.exp(-Math.pow(((tt % 1) - 0.36) * 22, 2));
      seed(Math.floor(tt * 60) + i); const noise = (rnd() - 0.5) * 0.08; p += `${f1(ox + x * ow)} ${f1(oy + oh / 2 - (beat * 0.6 * fk + noise) * oh / 2)} `; }
    s += `<path d="${p}" stroke="${C.acc}" stroke-width="3" fill="none"/><path d="${p}" stroke="${C.acc}" stroke-width="10" fill="none" opacity=".18" filter="url(#b3)"/>`;
    s += mono(ox + 20, oy + 36, 'CH1  E-FIELD   source: muscle (heartbeat)', { size: 15, fill: C.acc }) + mono(ox + ow - 20, oy + oh - 20, '5 nV/cm · div', { size: 15, fill: C.acc, anchor: 'end' });
    const nk = sm(tn, tn + 0.4, t);
    s += `<g opacity="${f1(nk)}"><text x="${ox}" y="${oy + oh + 130}" font-family="Black" font-size="110" fill="#fff">5 nV/cm</text>${mono(ox, oy + oh + 170, 'about five billionths of a volt per cm', { size: 18, fill: C.acc })}</g>`;
  }
  if (t < te - 0.2) s += `<rect x="0" y="900" width="${W}" height="180" fill="${C.navy}" opacity=".8"/>`;
  s += cap('s16', [['Now the senses.', {}], ['Those dark dots are pores.', { 2: C.acc }], ['a jelly-filled canal called an ampulla of Lorenzini.', { 4: C.acc, 5: C.acc, 6: C.acc }], ['They sense electricity.', { 2: C.acc }], ['give off a tiny electric field.', { 4: C.acc, 5: C.acc }], ['Even a fish hiding under the sand.', { 3: C.acc }], ['a few billionths of a volt.', { 2: C.acc }]], t, { size: 54 });
  return s + close();
}
