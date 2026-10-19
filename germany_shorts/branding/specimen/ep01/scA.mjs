import { C, W, H, f1, clamp, sm, eo, lerp, open, close, grid, mono, txt, typed, words, draw, dot, cycle, header, label, seed, rnd, esc } from './eng.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
import { at, W as WW, endOf } from './tl.mjs';
import { cap } from './cap.mjs';

const P = (ox, oy, sc) => (x, y) => [ox + x * sc, oy + y * sc];

// 01 hero: the opened shark, frame 0 complete
export function s01(t, len) {
  const z = 1 + 0.035 * sm(0, len, t), cx = 960, cy = 520;
  const reveal = sm(at('s01', 'most people'), at('s01', 'most people') + 2.2, t);
  const cut = lerp(812, 1000, reveal);
  let s = open(C.navy) + grid() + header(t, 'full specimen', 1);
  s += `<g transform="translate(${cx} ${cy}) scale(${z.toFixed(4)}) translate(${-cx} ${-cy})">`;
  const ox = 250, oy = 300, sc = 1.15, p = P(ox, oy, sc);
  s += sharkOpen(ox, oy, sc, { cut, id: 'h1', sw: 2.5, skin: '#1b1f36', stroke: '#e9e6f2' });
  const lab = (bx, by, tx, ty, a, b, k, anc) => { const [x, y] = p(bx, by); return label(x, y, tx, ty, a, b, k, { anchor: anc }); };
  const L0 = 1;   // labels already visible at frame 0
  s += lab(300, 180, 330, 250, 'RED MUSCLE', 'runs warm', L0, 'end') + lab(500, 168, 760, 250, 'SPINE', 'cartilage, zero bone', L0) + lab(620, 226, 1010, 250, 'STOMACH', 'U-shaped', L0)
    + lab(560, 262, 820, 850, 'LIVER', 'about 25% of its mass', L0) + lab(420, 230, 470, 850, 'SPIRAL VALVE', 'a corkscrew gut', L0, 'end');
  s += lab(745, 215, 1300, 330, 'GILLS', '5 per side', reveal) + lab(848, 176, 1380, 420, 'BRAIN', 'small, but…', reveal) + lab(950, 205, 1460, 520, 'AMPULLAE', 'electric sense', reveal);
  s += `<path d="M${ox} 790 L${ox + 1150} 790" stroke="${C.dim}" stroke-width="1"/>` + [0, 1, 2, 3, 4, 5, 6].map(k => `<path d="M${ox + k * 191.7} 782 L${ox + k * 191.7} 798" stroke="${C.dim}"/>${mono(ox + k * 191.7, 818, k + ' m', { size: 14, anchor: 'middle' })}`).join('');
  s += `</g>`;
  s += `<text x="80" y="935" font-family="SerifI" font-size="64" fill="${C.ink}">This is a great white shark.</text>`;
  s += words(80, 1005, WW('s01', 'Cut perfectly in half.'), t, { size: 64, fill: C.dim, hi: { 1: C.acc } });
  const tp = at('s01', "Let's open it");
  s += typed(1340, 1000, '> open specimen_001', t, tp + 0.6, { size: 26, fill: C.acc, cps: 16 });
  return s + close();
}

// 02 Specimen Facts label (paper)
export function s02(t, len) {
  let s = open(C.paper) + header(t, 'specimen facts', 2, { dark: false });
  s += `<g transform="translate(110 380) scale(0.82)"><path d="${SHARK}" fill="none" stroke="${C.pInk}" stroke-width="2.4"/><circle cx="905" cy="190" r="7" fill="${C.pInk}"/>
    ${[0, 1, 2, 3, 4].map(i => `<path d="M${712 + i * 17} 176 C${718 + i * 17} 210 ${716 + i * 17} 245 ${708 + i * 17} 264" stroke="${C.pInk}" stroke-width="2" fill="none" opacity=".6"/>`).join('')}</g>`;
  s += mono(110, 790, 'Fig. 2 — lateral view, adult female', { size: 16, fill: C.pDim });
  const zt = at('s02', 'Zero');
  if (t < zt - 0.1) s += words(110, 300, WW('s02', 'First, the basics.'), t, { size: 66, fill: C.pInk });
  if (t > zt - 0.1) s += words(110, 300, [['Zero', zt], ['bones.', zt + 0.25]], t, { size: 66, fill: C.pInk, hi: { 0: C.red, 1: C.red } });
  const rows = [['Length', 'up to 6.0 m', at('s02', 'Length')], ['Weight', 'up to 2,000 kg', at('s02', 'Weight')], ['Teeth right now', '≈ 300', at('s02', 'Teeth')], ['Bones', '0', zt]];
  const bx = 1120, by = 170;
  s += `<g transform="translate(${bx} ${by})"><rect width="620" height="${150 + 4 * 92 + 60}" fill="#fff" stroke="${C.pInk}" stroke-width="3"/>
    <text x="24" y="76" font-family="Black" font-size="66" fill="${C.pInk}">Specimen Facts</text>
    <text x="24" y="112" font-family="Inter" font-size="22" fill="${C.pInk}">Carcharodon carcharias · 1 per specimen</text>
    <rect x="24" y="128" width="572" height="16" fill="${C.pInk}"/>`;
  rows.forEach(([a, b, tr], i) => { const k = eo(tr - 0.1, tr + 0.25, t), y = 205 + i * 92;
    if (k > 0) s += `<g opacity="${f1(k)}"><text x="24" y="${y}" font-family="InterB" font-size="34" fill="${C.pInk}">${esc(a)}</text>
      <text x="596" y="${y}" font-family="InterB" font-size="${i === 3 ? 48 : 34}" fill="${i === 3 ? C.red : C.pInk}" text-anchor="end">${esc(cycle(b, t, tr, 0.6))}</text></g>`;
    s += `<rect x="24" y="${y + 26}" width="572" height="2" fill="${C.pInk}" opacity=".9"/>`; });
  s += `<text x="24" y="${150 + 4 * 92 + 40}" font-family="Inter" font-size="16" fill="#555">* largest known individuals; most adults are smaller</text></g>`;
  return s + close(false);
}

// 03 skeleton blueprint → vertebra growth rings
export function s03(t, len) {
  const BL = '#0b2350';
  let s = open(BL) + grid('#9fd8ff', 0.08, 40) + header(t, 'skeleton', 3);
  const tz = at('s03', 'The spine is'), zk = sm(tz - 0.4, tz + 0.8, t);
  // shark blueprint (fades/zooms away for the vertebra close-up)
  const ox = 330, oy = 300, sc = 1.25;
  s += `<g opacity="${f1(1 - zk)}" transform="translate(${ox} ${oy}) scale(${sc})">`;
  s += draw(SHARK, eo(0.2, 2.6, t), { stroke: '#cfe9ff', w: 2 });
  s += `<defs><clipPath id="b3c"><path d="${SHARK}"/></clipPath></defs><g clip-path="url(#b3c)" opacity="${f1(sm(1.4, 2.6, t))}">${anatomy({ organs: 0, muscle: 0, col: 0 })}</g></g>`;
  const tc = at('s03', 'cartilage'), tf = at('s03', 'lighter than bone');
  s += label(ox + 600 * sc, oy + 168 * sc, ox + 600 * sc + 60, oy - 40, 'SKELETON', 'cartilage', sm(tc, tc + 0.4, t) * (1 - zk));
  s += label(ox + 945 * sc, oy + 228 * sc, ox + 945 * sc + 40, oy + 360 * sc, 'JAWS', 'cartilage too', sm(tc + 0.8, tc + 1.2, t) * (1 - zk));
  s += mono(110, 850, 'same tissue as: your nose · your ears', { size: 22, fill: '#cfe9ff', op: sm(at('s03', 'the same bendy'), at('s03', 'the same bendy') + 0.4, t) * (1 - zk) });
  // flexible rod bending (lighter, more flexible)
  const fk = sm(tf, tf + 0.5, t) * (1 - zk);
  if (fk > 0) { const b = 70 * Math.sin((t - tf) * 3);
    s += `<g opacity="${f1(fk)}"><path d="M1380 760 Q1560 ${760 - b} 1740 760" stroke="#cfe9ff" stroke-width="10" fill="none" stroke-linecap="round"/>${mono(1560, 820, 'FLEX TEST · cartilage', { size: 16, fill: '#cfe9ff', anchor: 'middle' })}
      <path d="M1380 880 L1740 880" stroke="#ffffff" stroke-width="10" opacity=".35"/>${mono(1560, 920, 'bone · rigid', { size: 16, fill: '#cfe9ff', anchor: 'middle', op: 0.6 })}</g>`; }
  // vertebra rings
  if (zk > 0) {
    const tr = at('s03', 'grows in rings'), tcount = at('s03', 'Scientists count'), tage = at('s03', 'Some great whites');
    const cx = 760, cy = 560, R = 300;
    s += `<g opacity="${f1(zk)}"><circle cx="${cx}" cy="${cy}" r="${R}" fill="#123064" stroke="#cfe9ff" stroke-width="2.5"/><circle cx="${cx}" cy="${cy}" r="${R * 0.18}" fill="${BL}" stroke="#cfe9ff" stroke-width="2"/>`;
    const n = 14; for (let i = 1; i <= n; i++) { const k = sm(tr + i * 0.22, tr + i * 0.22 + 0.3, t); if (k > 0) s += `<circle cx="${cx}" cy="${cy}" r="${f1(R * 0.18 + (R * 0.8) * i / n)}" fill="none" stroke="${i % 2 ? C.acc : '#cfe9ff'}" stroke-width="${i % 2 ? 2 : 1}" opacity="${f1(0.85 * k)}"/>`; }
    s += mono(cx, cy + R + 50, 'FIG. 3 — VERTEBRA, CROSS-SECTION', { size: 16, fill: '#cfe9ff', anchor: 'middle' }) + '</g>';
    const ck = sm(tcount, tcount + 0.3, t);
    if (ck > 0) { const rings = Math.round(lerp(0, 70, eo(tcount, tage + 0.6, t)));
      s += `<g opacity="${f1(ck)}">${mono(1200, 470, 'GROWTH BANDS COUNTED', { size: 20, fill: '#cfe9ff' })}<text x="1200" y="600" font-family="Black" font-size="150" fill="#ffffff">${rings}${t > tage ? '+' : ''}</text>
        ${mono(1200, 650, 'years · estimated age', { size: 20, fill: C.acc })}</g>`; }
  }
  s += cap('s03', [['A great white has no bones at all.', { 4: C.acc, 5: C.acc }], ['Its whole skeleton is cartilage,', { 4: C.acc }], ['lighter than bone and more flexible,', {}], ['The spine is the one place', {}], ['And it grows in rings, like a tree.', { 4: C.acc }], ['Some great whites live past seventy.', { 5: C.acc }]], t, { fill: '#ffffff', size: 56 });
  return s + close();
}

// 04 skin under the microscope
const denticle = (x, y, s, op = 1) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${s})" opacity="${op}"><path d="M-22 -16 C-6 -22 14 -16 26 0 C14 16 -6 22 -22 16 C-16 6 -16 -6 -22 -16Z" fill="#c9cde0"/>
 <path d="M-14 -8 L18 -2 M-14 8 L18 2 M-16 0 L24 0" stroke="#8a90ad" stroke-width="2.2"/></g>`;
export function s04(t, len) {
  let s = open(C.navy) + grid() + header(t, 'skin', 4);
  const cx = 600, cy = 520, R = 330;
  s += `<defs><clipPath id="mic"><circle cx="${cx}" cy="${cy}" r="${R}"/></clipPath></defs>`;
  const zz = 0.6 + 0.5 * eo(0, 2.5, t);
  s += `<circle cx="${cx}" cy="${cy}" r="${R + 14}" fill="#05060c" stroke="${C.ink}" stroke-width="2"/><g clip-path="url(#mic)"><rect x="${cx - R}" y="${cy - R}" width="${2 * R}" height="${2 * R}" fill="#262a40"/>`;
  s += `<g transform="translate(${cx} ${cy}) scale(${zz.toFixed(3)})">`;
  for (let r = -9; r <= 9; r++) for (let c = -10; c <= 10; c++) s += denticle(c * 52 + (r % 2 ? 26 : 0), r * 38, 1, 0.95);
  // flow lines along the grooves
  const tf = at('s04', 'They channel');
  if (t > tf - 0.2) for (let i = 0; i < 9; i++) { const y = -300 + i * 76, ph = ((t - tf) * 220 + i * 70) % 700 - 350;
    s += `<path d="M${f1(ph - 120)} ${y} L${f1(ph + 120)} ${y}" stroke="${C.acc}" stroke-width="5" stroke-linecap="round" opacity="${f1(0.8 * sm(tf - 0.2, tf + 0.4, t))}"/>`; }
  s += `</g></g>`;
  s += mono(cx, cy + R + 50, `MAGNIFICATION ×${Math.round(40 + 260 * eo(0, 2.5, t))}`, { size: 16, anchor: 'middle' });
  const th = at('s04', 'head to tail'), tt = at('s04', 'Tail to head'), tl = at('s04', 'each one is built');
  s += `<g opacity="${f1(sm(th, th + 0.3, t))}"><path d="M1060 330 L1380 330" stroke="${C.ink}" stroke-width="2"/><path d="M1380 330 l-14 -8 l0 16Z" fill="${C.ink}"/>${mono(1060, 300, 'HEAD → TAIL', { size: 18 })}${txt(1420, 342, 'smooth', { font: 'SerifI', size: 46 })}</g>`;
  s += `<g opacity="${f1(sm(tt, tt + 0.3, t))}"><path d="M1060 440 L1380 440" stroke="${C.warm}" stroke-width="2"/><path d="M1060 440 l14 -8 l0 16Z" fill="${C.warm}"/>${mono(1060, 410, 'TAIL → HEAD', { size: 18, fill: C.warm })}${txt(1420, 452, 'sandpaper', { font: 'SerifI', size: 46, fill: C.warm })}</g>`;
  const k = sm(tl, tl + 0.4, t);
  if (k > 0) { s += `<g opacity="${f1(k)}" transform="translate(1260 700)"><path d="M-110 90 L-70 -60 C-40 -110 40 -110 70 -60 L110 90Z" fill="#c9cde0" stroke="${C.ink}" stroke-width="2"/>
      <path d="M-84 60 L-56 -40 C-30 -80 30 -80 56 -40 L84 60Z" fill="#e6d6b8"/><path d="M-30 90 L-20 0 L20 0 L30 90Z" fill="${C.warm}" opacity=".8"/></g>`;
    s += label(1260, 610, 1440, 600, 'CROWN', 'enamel-like', k) + label(1290, 690, 1440, 700, 'DENTINE', 'like a tooth', k) + label(1265, 770, 1440, 800, 'PULP', '', k); }
  s += cap('s04', [['Now the skin.', {}], ['millions of tiny scales called denticles.', { 4: C.acc }], ['each one is built like a tiny tooth.', { 6: C.acc }], ['with less drag.', { 1: C.acc }]], t, { size: 56 });
  return s + close();
}

// 05 jaw as a conveyor belt
export function s05(t, len) {
  let s = open(C.navy) + grid() + header(t, 'teeth', 5);
  const cx = 860, cy = 760, R = 380;
  s += `<path d="M${cx - R - 40} ${cy} A${R + 40} ${R + 40} 0 0 1 ${cx + R + 40} ${cy}" fill="none" stroke="${C.faint}" stroke-width="80"/>`;
  s += `<path d="M${cx - R - 40} ${cy} A${R + 40} ${R + 40} 0 0 1 ${cx + R + 40} ${cy}" fill="none" stroke="${C.ink}" stroke-width="2" opacity=".5"/>`;
  // teeth travel along an arc from inside (folded, angle 160°) to the front edge (angle 20°)
  const tf = at('s05', 'When a front tooth'), conv = at('s05', "It's not a set");
  const speed = 0.06 + 0.25 * sm(tf, tf + 1, t);
  const N = 7;
  for (let i = 0; i < N; i++) {
    let u = ((i / N) + (t - 2) * speed) % 1; if (u < 0) u += 1;      // 0 = deep inside, 1 = front edge
    const ang = Math.PI * (0.92 - 0.82 * u), x = cx + Math.cos(ang) * R, y = cy - Math.sin(ang) * R;
    const fold = (1 - u) * 80, size = 0.6 + 0.6 * u;
    const fall = u > 0.94 ? (u - 0.94) / 0.06 : 0;
    s += `<g transform="translate(${f1(x)} ${f1(y + fall * 120)}) rotate(${f1(-(ang * 180 / Math.PI - 90) - fold + fall * 40)}) scale(${f1(size)})" opacity="${f1(1 - fall)}">
      <path d="M-40 0 L-6 -110 L6 -110 L40 0Z" fill="#f4efe6" stroke="${C.ink}" stroke-width="2"/>${[-30, -14, 2, 18].map(v => `<path d="M${v} -${f1(36 + (v + 30) * 1.6)} l6 6" stroke="#9a9aaa" stroke-width="2"/>`).join('')}</g>`;
  }
  s += label(cx + Math.cos(Math.PI * 0.12) * R, cy - Math.sin(Math.PI * 0.12) * R - 60, 1460, 300, 'FRONT ROW', 'in use', sm(at('s05', 'Behind the front'), at('s05', 'Behind the front') + 0.4, t));
  s += label(cx + Math.cos(Math.PI * 0.85) * R, cy - Math.sin(Math.PI * 0.85) * R - 30, 300, 300, 'SPARE ROWS', 'folded back, waiting', sm(at('s05', 'more rows'), at('s05', 'more rows') + 0.4, t), { anchor: 'end' });
  s += mono(cx, cy + 70, 'FIG. 5 — JAW, CROSS-SECTION · tooth replacement', { size: 16, anchor: 'middle' });
  s += cap('s05', [['Speaking of teeth.', {}], ['folded back and waiting.', {}], ['rolls forward to take its place.', { 0: C.acc }], ["It's not a set of teeth.", {}], ["It's a conveyor belt.", { 2: C.acc, 3: C.acc }]], t, { size: 60 });
  return s + close();
}

// 06 calendar app (light UI)
export function s06(t, len) {
  let s = open('#e9e9ee') + header(t, 'tooth replacement', 6, { dark: false });
  const x0 = 360, y0 = 160, w = 1200, h = 760;
  s += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" rx="18" fill="#ffffff" stroke="#d7d7de"/>`;
  s += txt(x0 + 40, y0 + 64, 'October', { font: 'InterB', size: 34, fill: '#1b1b22' }) + txt(x0 + 210, y0 + 64, 'year 1', { size: 26, fill: '#9a9aa6' });
  s += `<rect x="${x0 + w - 300}" y="${y0 + 30}" width="260" height="44" rx="10" fill="#f2f2f6"/>` + mono(x0 + w - 170, y0 + 60, 'Day  Week  Month', { size: 16, fill: '#666', anchor: 'middle' });
  const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'], cw = (w - 80) / 7, ch = 118;
  days.forEach((d, i) => { s += mono(x0 + 40 + i * cw + 12, y0 + 120, d, { size: 14, fill: '#9a9aa6' }); });
  const tl = at('s06', 'Sharks lose'), tlife = at('s06', 'Over a lifetime');
  seed(5); let lost = 0;
  for (let d = 0; d < 35; d++) { const r = Math.floor(d / 7), c = d % 7, x = x0 + 40 + c * cw, y = y0 + 140 + r * ch;
    s += `<rect x="${f1(x)}" y="${y}" width="${f1(cw - 8)}" height="${ch - 8}" rx="8" fill="#fafafc" stroke="#ececf2"/>` + mono(x + 12, y + 26, String(d + 1), { size: 15, fill: '#9a9aa6' });
    const n = rnd() < 0.55 ? 1 + Math.floor(rnd() * 3) : 0; const td = tl + 0.3 + d * 0.18;
    for (let k = 0; k < n; k++) { const kk = eo(td + k * 0.05, td + k * 0.05 + 0.3, t); if (kk <= 0) continue; lost++;
      const tx = x + 30 + k * 34, ty = y + 50 + (1 - kk) * -40;
      s += `<path d="M${f1(tx - 10)} ${f1(ty + 30)} L${f1(tx - 2)} ${f1(ty)} L${f1(tx + 2)} ${f1(ty)} L${f1(tx + 10)} ${f1(ty + 30)}Z" fill="#ffffff" stroke="#1b1b22" stroke-width="2" opacity="${f1(kk)}"/>`; }
  }
  s += `<g transform="translate(${x0 + w + 40} ${y0 + 40})"><rect width="300" height="200" rx="16" fill="#1b1b22"/>${mono(24, 44, 'TEETH LOST', { size: 16, fill: '#9a9aa6' })}
    <text x="24" y="130" font-family="Black" font-size="80" fill="#ffffff">${t > tlife ? cycle('1,000s', t, tlife, 0.4) : lost}</text>${mono(24, 172, t > tlife ? 'over a lifetime' : 'this month', { size: 16, fill: C.acc })}</g>`;
  const tfo = at('s06', 'Which is why');
  s += `<g opacity="${f1(sm(tfo, tfo + 0.4, t))}" transform="translate(${x0 + w + 40} ${y0 + 290})"><rect width="300" height="160" rx="16" fill="#ffffff" stroke="#d7d7de"/>${mono(24, 40, 'MOST COMMON', { size: 14, fill: '#9a9aa6' })}${mono(24, 64, 'SHARK FOSSIL', { size: 14, fill: '#9a9aa6' })}
     <path d="M110 140 L140 80 L148 80 L178 140Z" fill="#c8b08a" stroke="#1b1b22" stroke-width="2"/>${txt(200, 128, 'teeth', { font: 'SerifI', size: 34, fill: '#1b1b22' })}</g>`;
  s += cap('s06', [['Sharks lose teeth all the time,', {}], ['and they never run out.', { 3: C.red }], ['thousands of them.', { 0: C.red }], ['most common fossils on Earth.', { 2: C.red }]], t, { size: 50, fill: '#1b1b22', x: 360, y: 1010 });
  return s + close(false);
}

// 07 bite force chart
export function s07(t, len) {
  let s = open(C.navy) + grid() + header(t, 'bite force', 7);
  const tm = at('s07', 'computer model'), te = at('s07', 'Their estimate'), th = at('s07', 'A strong human');
  // FEA jaw mesh
  const mk = sm(tm, tm + 0.6, t) * (1 - sm(te + 0.2, te + 0.8, t) * 0.6);
  if (mk > 0) { seed(9); let g = ''; const pts = [];
    for (let i = 0; i < 46; i++) { const a = Math.PI * (0.1 + 0.8 * i / 45); const r1 = 260, r2 = 200; pts.push([500 + Math.cos(a) * r1, 600 - Math.sin(a) * r1 * 0.75], [500 + Math.cos(a) * r2, 600 - Math.sin(a) * r2 * 0.75]); }
    for (let i = 0; i < pts.length - 3; i += 2) { const [a, b, c, d] = [pts[i], pts[i + 1], pts[i + 2], pts[i + 3]]; const heat = Math.abs(Math.sin(i / 9 + t));
      g += `<path d="M${f1(a[0])} ${f1(a[1])} L${f1(b[0])} ${f1(b[1])} L${f1(d[0])} ${f1(d[1])} L${f1(c[0])} ${f1(c[1])}Z" fill="${heat > 0.7 ? C.warm : '#2a2e4a'}" fill-opacity="${f1(0.25 + 0.5 * heat)}" stroke="${C.acc}" stroke-width="1"/>`;
      g += `<path d="M${f1(a[0])} ${f1(a[1])} L${f1(d[0])} ${f1(d[1])}" stroke="${C.acc}" stroke-width=".8" opacity=".6"/>`; }
    s += `<g opacity="${f1(mk)}" transform="translate(-260 -280) scale(1.5)">${g}${mono(500, 690, 'FIG. 7 — JAW MODEL · stress test', { size: 12, anchor: 'middle' })}</g>`; }
  // bars
  const base = 860, x1 = 1150, x2 = 1450, maxH = 600, scale = maxH / 18000;
  s += `<path d="M1040 ${base} L1700 ${base}" stroke="${C.ink}" stroke-width="2"/>`;
  for (let v = 0; v <= 18000; v += 3000) { const y = base - v * scale; s += `<path d="M1040 ${f1(y)} L1700 ${f1(y)}" stroke="${C.ink}" opacity=".08"/>` + mono(1030, y + 5, v.toLocaleString('en-US'), { size: 13, anchor: 'end' }); }
  s += mono(1030, base - maxH - 30, 'NEWTONS', { size: 14, anchor: 'end', fill: C.acc });
  const hs = eo(te, te + 1.6, t) * 18000, hh = eo(th, th + 0.8, t) * 1000;
  s += `<rect x="${x2}" y="${f1(base - hs * scale)}" width="180" height="${f1(hs * scale)}" fill="${C.acc}"/>` + mono(x2 + 90, base + 34, 'GREAT WHITE', { size: 18, anchor: 'middle', fill: C.ink });
  if (t > te) s += `<text x="${x2 + 90}" y="${f1(base - hs * scale - 20)}" font-family="Black" font-size="54" fill="#ffffff" text-anchor="middle">≈${Math.round(hs / 100) * 100 >= 18000 ? '18,000' : Math.round(hs).toLocaleString('en-US')}</text>`;
  s += `<rect x="${x1}" y="${f1(base - hh * scale)}" width="180" height="${f1(hh * scale)}" fill="${C.ink}"/>` + mono(x1 + 90, base + 34, 'HUMAN', { size: 18, anchor: 'middle', fill: C.ink });
  if (t > th) s += `<text x="${x1 + 90}" y="${f1(base - hh * scale - 20)}" font-family="Black" font-size="54" fill="#ffffff" text-anchor="middle">≈${Math.round(hh).toLocaleString('en-US')}</text>`;
  s += cap('s07', [['So how hard can it bite?', { 4: C.acc }], ['a computer model of its jaw.', { 1: C.acc, 2: C.acc }], ['about eighteen thousand newtons.', { 1: C.acc, 2: C.acc }], ['A strong human bite', {}]], t, { size: 56, x: 110, y: 1000 });
  return s + close();
}

// 08 liver: float + fuel tank (paper)
export function s08(t, len) {
  let s = open(C.paper) + header(t, 'liver', 8, { dark: false });
  const tl = at('s08', "It's the liver"), tq = at('s08', 'about a quarter'), tb = at('s08', 'swim bladder'), to = at('s08', 'packed with oil'), tfl = at('s08', 'built-in float'), tfu = at('s08', 'fuel tank');
  const ox = 120, oy = 250 - 40 * sm(tfl, tfl + 1.2, t) + 6 * Math.sin(t * 1.5) * sm(tfl, tfl + 1, t), sc = 0.95;
  const focus = sm(tl - 0.2, tl + 0.4, t);
  s += `<g transform="translate(${ox} ${f1(oy)}) scale(${sc})"><defs><clipPath id="l8"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#ffffff"/>
     <g clip-path="url(#l8)" opacity="${f1(1 - 0.75 * focus)}">${anatomy({ col: 1 })}</g>
     <g clip-path="url(#l8)" opacity="${f1(focus)}"><path d="M445 238 C480 226 620 222 712 236 C690 262 640 284 560 286 C500 288 460 270 445 238Z" fill="${C.liver}"/></g>
     <path d="${SHARK}" fill="none" stroke="${C.pInk}" stroke-width="2.4"/></g>`;
  s += label(ox + 580 * sc, oy + 255 * sc, ox + 640 * sc, oy + 470 * sc, 'LIVER', 'oil-filled', focus, { dark: false });
  // pie 25%
  const pk = sm(tq, tq + 0.3, t);
  if (pk > 0) { const a = 2 * Math.PI * 0.25 * eo(tq, tq + 1, t), cx = 1450, cy = 330, r = 120;
    s += `<g opacity="${f1(pk)}"><circle cx="${cx}" cy="${cy}" r="${r}" fill="#ffffff" stroke="${C.pInk}" stroke-width="2"/><path d="M${cx} ${cy} L${cx} ${cy - r} A${r} ${r} 0 0 1 ${f1(cx + r * Math.sin(a))} ${f1(cy - r * Math.cos(a))}Z" fill="${C.liver}"/>
      ${txt(cx + 160, cy + 10, '≈ 25%', { font: 'Black', size: 64, fill: C.pInk })}${mono(cx + 160, cy + 44, 'of total body weight', { size: 16, fill: C.pDim })}</g>`; }
  // swim bladder: none
  const bk = sm(tb, tb + 0.3, t) * (1 - sm(to - 0.2, to + 0.2, t));
  if (bk > 0) s += `<g opacity="${f1(bk)}" transform="translate(1450 640)"><ellipse rx="110" ry="60" fill="none" stroke="${C.pInk}" stroke-width="3" stroke-dasharray="10 8"/><path d="M-130 -80 L130 80" stroke="${C.red}" stroke-width="8"/>${mono(0, 110, 'SWIM BLADDER · none', { size: 18, fill: C.red, anchor: 'middle' })}</g>`;
  // density tank
  const dk = sm(to - 0.1, to + 0.4, t) * (1 - sm(tfu - 0.2, tfu + 0.2, t));
  if (dk > 0) { const lvl = eo(to, to + 1.6, t);
    s += `<g opacity="${f1(dk)}" transform="translate(1320 520)"><rect width="300" height="300" fill="#ffffff" stroke="${C.pInk}" stroke-width="3"/>
      <rect y="${f1(300 - 300 * lvl)}" width="300" height="${f1(300 * lvl)}" fill="#9cc7e0"/><rect y="${f1(300 - 300 * lvl - 70 * lvl)}" width="300" height="${f1(70 * lvl)}" fill="${C.liver}"/>
      ${mono(320, 300 - 300 * lvl - 30 * lvl, 'OIL  ≈ 0.86', { size: 18, fill: C.pInk })}${mono(320, 200, 'SEAWATER  ≈ 1.03', { size: 18, fill: C.pInk })}${mono(0, 340, 'density, g/cm³', { size: 14, fill: C.pDim })}</g>`; }
  // fuel gauge
  const gk = sm(tfu - 0.1, tfu + 0.4, t);
  if (gk > 0) { const lev = 1 - 0.65 * eo(at('s08', 'On long ocean'), at('s08', 'On long ocean') + 3, t), a = Math.PI * (1 - lev), cx = 1470, cy = 790, r = 150;
    s += `<g opacity="${f1(gk)}"><path d="M${cx - r} ${cy} A${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none" stroke="${C.pInk}" stroke-width="16" opacity=".15"/>
      <path d="M${cx - r} ${cy} A${r} ${r} 0 0 1 ${f1(cx - r * Math.cos(Math.PI * lev))} ${f1(cy - r * Math.sin(Math.PI * lev))}" fill="none" stroke="${C.liver}" stroke-width="16"/>
      <path d="M${cx} ${cy} L${f1(cx - (r - 30) * Math.cos(Math.PI * lev))} ${f1(cy - (r - 30) * Math.sin(Math.PI * lev))}" stroke="${C.pInk}" stroke-width="6" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="10" fill="${C.pInk}"/>
      ${mono(cx - r, cy + 34, 'E', { size: 20, fill: C.pInk })}${mono(cx + r, cy + 34, 'F', { size: 20, fill: C.pInk, anchor: 'end' })}${mono(cx, cy + 60, 'LIVER OIL · fuel', { size: 16, fill: C.pDim, anchor: 'middle' })}</g>`; }
  s += cap('s08', [['Now look at the biggest thing', {}], ["It's not the stomach.", {}], ["It's the liver.", { 2: C.liver }], ['about a quarter', { 1: C.liver }], ["Sharks don't have one.", {}], ['packed with oil,', { 2: C.liver }], ['It works like a built-in float.', { 5: C.liver }], ['it doubles as a fuel tank.', { 4: C.liver, 5: C.liver }], ['burn that oil for energy.', { 2: C.liver }]], t, { size: 58, fill: C.pInk, x: 120 });
  return s + close(false);
}
