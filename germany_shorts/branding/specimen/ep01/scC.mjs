import { C, W, H, f1, clamp, sm, eo, lerp, open, close, grid, mono, txt, typed, words, draw, dot, cycle, header, label, seed, rnd, esc } from './eng.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
import { at } from './tl.mjs';
import { cap } from './cap.mjs';
const sk = (ox, oy, sc, { fill = '#1d2140', stroke = C.ink, w = 2 } = {}) => `<g transform="translate(${f1(ox)} ${f1(oy)}) scale(${sc})"><path d="${SHARK}" fill="${fill}" stroke="${stroke}" stroke-width="${f1(w / sc)}"/><circle cx="905" cy="190" r="7" fill="${stroke}"/></g>`;

// 17 lateral line seismograph
export function s17(t, len) {
  let s = open(C.navy) + grid() + header(t, 'lateral line', 18);
  const ox = 180, oy = 160, sc = 0.8;
  s += sk(ox, oy, sc);
  // lateral line draws along the flank
  const ll = 'M180 190 C350 186 550 188 700 196 C780 200 860 196 900 200';
  s += `<g transform="translate(${ox} ${oy}) scale(${sc})">${draw(ll, eo(0.3, 2.2, t), { stroke: C.acc, w: 4 })}
    ${Array.from({ length: 30 }, (_, i) => { const x = 190 + i * 24; return `<circle cx="${x}" cy="${f1(188 + (x > 700 ? (x - 700) * 0.04 : 0))}" r="3" fill="${C.acc}" opacity="${f1(sm(0.3 + i * 0.06, 0.5 + i * 0.06, t))}"/>`; }).join('')}</g>`;
  s += label(ox + 500 * sc, oy + 188 * sc, ox + 520 * sc, oy - 10, 'LATERAL LINE', 'pressure sensors', sm(0.6, 1, t));
  // struggling fish on the right, ripples spreading
  const tf = at('s17', 'A struggling fish'), fx = 1620, fy = 340;
  const rk = sm(tf - 0.2, tf + 0.3, t);
  if (rk > 0) { s += `<g opacity="${f1(rk)}" transform="translate(${fx} ${fy}) rotate(${f1(18 * Math.sin(t * 14))})"><path d="M-40 0 C-20 -18 20 -18 40 0 C20 18 -20 18 -40 0Z M40 0 L62 -14 L62 14Z" fill="#c9cde0"/></g>`;
    for (let i = 0; i < 6; i++) { const r = ((t - tf) * 220 + i * 120) % 720; if (t - tf < 0) break; s += `<circle cx="${fx}" cy="${fy}" r="${f1(r)}" fill="none" stroke="${C.ink}" stroke-width="1.6" opacity="${f1(rk * 0.7 * (1 - r / 720))}"/>`; } }
  // seismograph strip
  const gx = 120, gy = 620, gw = 1680, gh = 220;
  s += `<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="#f4f1ea"/>`;
  for (let i = 0; i <= 28; i++) s += `<path d="M${gx + i * gw / 28} ${gy} L${gx + i * gw / 28} ${gy + gh}" stroke="#c9b9a0" stroke-width="1"/>`;
  const arrive = tf + 1.6;
  let p = 'M'; for (let i = 0; i <= 400; i++) { const x = i / 400, tt = t - (1 - x) * 5; seed(Math.floor(tt * 80)); let v = (rnd() - 0.5) * 0.06;
    if (tt > arrive) v += Math.sin(tt * 40) * 0.6 * Math.exp(-((tt - arrive) % 1.3) * 2.2); p += `${f1(gx + x * gw)} ${f1(gy + gh / 2 - v * gh / 2)} `; }
  s += `<path d="${p}" stroke="${C.red}" stroke-width="2" fill="none"/><circle cx="${gx + gw}" cy="${gy + gh / 2}" r="6" fill="${C.pInk}"/>`;
  s += mono(gx, gy - 14, 'LATERAL LINE · PRESSURE SIGNAL', { size: 16, fill: C.ink }) + mono(gx + gw, gy - 14, t > arrive ? 'SIGNAL DETECTED · target not yet visible' : 'listening…', { size: 16, fill: t > arrive ? C.warm : C.dim, anchor: 'end' });
  s += cap('s17', [['Along both sides of the body runs a line of sensors', {}], ['called the lateral line.', { 2: C.acc, 3: C.acc }], ['It feels pressure waves in the water.', { 3: C.acc, 4: C.acc }], ['A struggling fish far away', { 2: C.warm }], ['before it ever sees it.', { 3: C.warm }]], t, { size: 56 });
  return s + close();
}

// 18 brain: olfactory bulbs
export function s18(t, len) {
  let s = open(C.paper) + header(t, 'brain', 19, { dark: false });
  const tf = at('s18', 'But look at the front'), tb = at('s18', 'These two bulbs'), tg = at('s18', 'In great whites'), tr = at('s18', 'It reads it');
  const z = 1 + 0.25 * eo(tf - 0.2, tf + 1.2, t);
  // dorsal view, brain pointing right
  s += `<g transform="translate(860 500) scale(${f1(z * 1000) / 1000}) translate(-860 -500)">`;
  const ink = C.pInk, hi = sm(tb - 0.2, tb + 0.4, t);
  // hindbrain / cerebellum / midbrain / forebrain
  s += `<ellipse cx="560" cy="500" rx="90" ry="70" fill="#fff" stroke="${ink}" stroke-width="3"/><ellipse cx="700" cy="500" rx="80" ry="88" fill="#fff" stroke="${ink}" stroke-width="3"/>
    <ellipse cx="830" cy="470" rx="58" ry="46" fill="#fff" stroke="${ink}" stroke-width="3"/><ellipse cx="830" cy="530" rx="58" ry="46" fill="#fff" stroke="${ink}" stroke-width="3"/>
    <ellipse cx="960" cy="470" rx="62" ry="54" fill="#fff" stroke="${ink}" stroke-width="3"/><ellipse cx="960" cy="530" rx="62" ry="54" fill="#fff" stroke="${ink}" stroke-width="3"/>
    <path d="M440 480 L470 480 M440 520 L470 520" stroke="${ink}" stroke-width="3"/>`;
  // olfactory tracts + bulbs
  const bulb = (y) => `<path d="M1015 ${y} C1080 ${y} 1140 ${y + (y < 500 ? -60 : 60)} 1220 ${y + (y < 500 ? -110 : 110)}" stroke="${hi > 0.1 ? C.red : ink}" stroke-width="12" fill="none"/><ellipse cx="1270" cy="${y + (y < 500 ? -130 : 130)}" rx="${f1(70 + 8 * hi)}" ry="${f1(52 + 6 * hi)}" fill="${hi > 0.1 ? C.red : '#fff'}" fill-opacity="${f1(0.15 + 0.7 * hi)}" stroke="${hi > 0.1 ? C.red : ink}" stroke-width="3"/>`;
  s += bulb(470) + bulb(530) + `</g>`;
  s += label(560, 430, 420, 300, 'HINDBRAIN', '', 1 - hi * 0.6, { dark: false, anchor: 'end' }) + label(700, 412, 640, 260, 'CEREBELLUM', '', 1 - hi * 0.6, { dark: false }) + label(960, 416, 1000, 240, 'FOREBRAIN', '', 1 - hi * 0.6, { dark: false });
  s += `<g opacity="${f1(hi)}">${mono(1480, 480, 'OLFACTORY BULBS', { size: 22, fill: C.red })}${mono(1480, 508, 'smell only', { size: 18, fill: C.pInk })}</g>`;
  // share bar
  const gk = sm(tg - 0.1, tg + 0.4, t);
  if (gk > 0) { const share = eo(tg, tg + 1.2, t);
    s += `<g opacity="${f1(gk)}" transform="translate(1280 800)"><rect width="520" height="40" fill="#fff" stroke="${C.pInk}" stroke-width="2"/><rect width="${f1(520 * 0.18 * share)}" height="40" fill="${C.red}"/>
      ${mono(0, -14, 'SHARE OF BRAIN USED FOR SMELL', { size: 16, fill: C.pInk })}${mono(0, 70, 'compared with most sharks: larger', { size: 16, fill: C.pDim })}</g>`; }
  const rk = sm(tr - 0.1, tr + 0.3, t);
  if (rk > 0) s += `<text x="1800" y="1010" font-family="Black" font-size="110" fill="${C.red}" text-anchor="end" opacity="${f1(rk)}">READS</text>`;
  s += mono(860, 900, 'FIG. 19 — brain, dorsal view · front →', { size: 16, fill: C.pDim, anchor: 'middle' });
  s += cap('s18', [['Inside the head, the brain is small.', { 5: C.red }], ['But look at the front of it.', { 4: C.red }], ['These two bulbs are just for smell.', { 6: C.red }], ['they make up a big share of the whole brain.', { 4: C.red, 5: C.red }], ["It doesn't just smell the ocean.", {}], ['It reads it.', { 1: C.red }]], t, { size: 56, fill: C.pInk });
  return s + close(false);
}

// 19 eye: tapetum + roll-back
export function s19(t, len) {
  let s = open(C.navy) + grid() + header(t, 'eyes', 20);
  const tr = at('s19', 'And when it bites'), tb = at('s19', 'For that split');
  if (t < tr - 0.2) {
    const cx = 760, cy = 540, R = 280;
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="#151a33" stroke="${C.ink}" stroke-width="3"/>`;
    // retina + tapetum arc on the back (left side)
    s += `<path d="M${cx - R * 0.5} ${cy - R * 0.866} A${R} ${R} 0 0 0 ${cx - R * 0.5} ${cy + R * 0.866}" stroke="#d64c7a" stroke-width="16" fill="none"/>`;
    s += `<path d="M${cx - (R - 18) * 0.5} ${cy - (R - 18) * 0.866} A${R - 18} ${R - 18} 0 0 0 ${cx - (R - 18) * 0.5} ${cy + (R - 18) * 0.866}" stroke="#d8f0ff" stroke-width="8" fill="none" opacity="${f1(0.4 + 0.6 * sm(0.4, 1.4, t))}"/>`;
    s += `<ellipse cx="${cx + R - 70}" cy="${cy}" rx="70" ry="90" fill="#cfd8ff" opacity=".5" stroke="${C.ink}" stroke-width="2"/>`;
    s += label(cx - R + 12, cy - 120, 300, 260, 'TAPETUM LUCIDUM', 'mirror layer', sm(0.6, 1.2, t), { anchor: 'end' }) + label(cx + R - 70, cy - 90, 1150, 250, 'LENS', '', sm(0.6, 1.2, t));
    // rays: enter, hit back, bounce
    const rk = sm(at('s19', 'bounces light'), at('s19', 'bounces light') + 0.5, t);
    for (let i = -2; i <= 2; i++) { const y = cy + i * 40, ph = ((t * 0.7 + i * 0.13) % 1 + 1) % 1;
      const xin = lerp(1400, cx - R + 30, Math.min(1, ph * 2)), back = ph > 0.5 ? lerp(cx - R + 30, cx + R + 200, (ph - 0.5) * 2) : null;
      s += `<path d="M1400 ${y} L${f1(xin)} ${f1(y * 1 - (xin < cx + R - 70 ? (i * 10) : 0))}" stroke="${C.gold}" stroke-width="3" opacity=".8"/>`;
      if (back !== null) s += `<path d="M${cx - R + 30} ${y - i * 10} L${f1(back)} ${f1(y - i * 10 - i * 6)}" stroke="${C.gold}" stroke-width="3" opacity="${f1(0.9 * rk)}" stroke-dasharray="10 8"/>`; }
    s += mono(1400, cy - 140, 'LIGHT IN →', { size: 16, fill: C.gold, anchor: 'end' }) + mono(1400, cy + 160, '← reflected, second chance to see', { size: 16, fill: C.gold, anchor: 'end', op: rk });
  } else {
    // eye roll-back sequence, three frames like a contact sheet
    const fr = (x, k, tag) => { const ey = 520, w = 420, roll = k; return `<g transform="translate(${x} 0)"><rect x="-${w / 2}" y="300" width="${w}" height="420" fill="#151a33" stroke="${C.faint}"/>
      <ellipse cx="0" cy="${ey}" rx="120" ry="70" fill="#f1ece6" stroke="${C.ink}" stroke-width="3"/>
      <circle cx="${f1(-60 * roll)}" cy="${ey}" r="${f1(62 * (1 - roll * 0.9))}" fill="#0a0a0a"/>
      ${mono(0, 680, tag, { size: 18, fill: k > 0.8 ? C.red : C.ink, anchor: 'middle' })}</g>`; };
    const k = eo(tr + 0.6, tr + 2.2, t);
    s += fr(500, 0, 'APPROACH · eye open') + (k > 0.2 ? fr(960, Math.min(1, k * 1.6) * 0.6, 'CONTACT · rolling back') : '') + (k > 0.6 ? fr(1420, 1, 'BITE · eye protected') : '');
    const bk = sm(tb - 0.1, tb + 0.3, t);
    if (bk > 0) s += `<text x="960" y="250" font-family="Black" font-size="120" fill="${C.red}" text-anchor="middle" opacity="${f1(bk)}">BITES BLIND</text>`;
  }
  s += cap('s19', [['Behind each eye sits a mirror-like layer', { 5: C.acc }], ['so it can see in dim water.', { 4: C.acc }], ['a great white rolls its eyes back into its head', { 3: C.red, 6: C.red }], ['to protect them.', {}], ['For that split second, it bites blind.', { 6: C.red }]], t, { size: 56 });
  return s + close();
}

// 19b spy-hopping: periscope viewfinder
export function s19b(t, len) {
  let s = open(C.navy) + header(t, 'spy-hopping', 21);
  const tl = at('s19b', 'Sometimes a shark'), tn = at('s19b', 'Scientists call it');
  const wl = 640;
  s += `<rect x="0" y="0" width="${W}" height="${wl}" fill="#121729"/><rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="#0a1f33"/>`;
  s += `<path d="M0 ${wl} ${Array.from({ length: 49 }, (_, i) => `L${i * 40} ${f1(wl + 6 * Math.sin(i * 0.6 + t * 2.5))}`).join(' ')}" stroke="${C.acc}" stroke-width="2" fill="none"/>`;
  // boat silhouette far away
  s += `<path d="M1450 ${wl - 6} L1640 ${wl - 6} L1610 ${wl + 14} L1480 ${wl + 14}Z M1520 ${wl - 6} L1520 ${wl - 70} L1580 ${wl - 6}Z" fill="#2a2f4a"/>`;
  // shark rising vertically: head up
  const up = eo(tl - 0.2, tl + 1.6, t) * (1 - 0.0) + 0.02 * Math.sin(t * 2);
  const hx = 820, hy = lerp(wl + 380, wl - 240, up);
  s += `<defs><clipPath id="sea19"><rect x="0" y="${wl}" width="${W}" height="${H - wl}"/></clipPath></defs>`;
  s += `<g transform="translate(${hx} ${f1(hy)}) rotate(-90) scale(0.62) translate(-985 -212)"><path d="${SHARK}" fill="#c9cde0" stroke="${C.ink}" stroke-width="3"/><circle cx="905" cy="190" r="10" fill="${C.navy}"/></g>`;
  s += `<g clip-path="url(#sea19)"><rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="#0a1f33" opacity=".55"/></g>`;
  // viewfinder
  s += `<circle cx="${hx + 40}" cy="${f1(hy - 120)}" r="${f1(110)}" fill="none" stroke="${C.acc}" stroke-width="2" opacity="${f1(sm(tl + 1, tl + 1.5, t))}"/>`;
  s += mono(hx + 170, hy - 210, 'HEAD ABOVE SURFACE', { size: 18, fill: C.acc, op: sm(tl + 1, tl + 1.5, t) }) + mono(hx + 170, hy - 184, 'looking around', { size: 15, op: sm(tl + 1, tl + 1.5, t) });
  const nk = sm(tn - 0.1, tn + 0.4, t);
  if (nk > 0) s += `<text x="1820" y="300" font-family="Black" font-size="120" fill="#fff" text-anchor="end" opacity="${f1(nk)}">SPY-HOPPING</text>`;
  s += cap('s19b', [["Great whites don't only look underwater.", { 5: C.acc }], ['Sometimes a shark lifts its head straight out of the water', { 5: C.acc, 6: C.acc }], ['and looks around at the surface.', {}], ['Scientists call it spy-hopping.', { 3: C.acc }]], t, { size: 54, y: 1010 });
  return s + close();
}

// 20 hunting sequence: distance ladder
export function s20(t, len) {
  let s = open(C.navy) + grid() + header(t, 'hunting sequence', 22);
  const st = [['SMELL', 'far away', at('s20', 'Smell works')], ['LATERAL LINE', 'movement', at('s20', 'Then the lateral')], ['EYES', 'lock on', at('s20', 'Then the eyes')], ['ELECTRICITY', 'last few cm', at('s20', 'electricity guides')]];
  const x0 = 180, x1 = 1740, y = 520;
  s += `<path d="M${x0} ${y} L${x1} ${y}" stroke="${C.ink}" stroke-width="2"/>` + mono(x0, y + 50, 'FAR', { size: 16 }) + mono(x1, y + 50, 'CONTACT', { size: 16, anchor: 'end' });
  const prog = st.reduce((a, [, , tt], i) => t > tt ? i : a, -1);
  // prey dot at the right, shark moving left->right
  const sx = lerp(x0, x1 - 160, eo(st[0][2] - 0.5, st[3][2] + 1.6, t));
  s += `<g transform="translate(${f1(sx - 140)} ${y - 60}) scale(0.16)"><path d="${SHARK}" fill="#c9cde0"/></g>` + dot(x1, y, { r: 9, col: C.warm, glow: C.warm });
  st.forEach(([n, d, tt], i) => { const x = lerp(x0 + 80, x1 - 120, i / 3), k = sm(tt - 0.1, tt + 0.3, t), on = i === prog;
    s += `<g opacity="${f1(0.25 + 0.75 * k)}"><path d="M${f1(x)} ${y - 20} L${f1(x)} ${y - 120}" stroke="${on ? C.acc : C.dim}" stroke-width="2"/>
      <rect x="${f1(x - 150)}" y="${y - 290}" width="300" height="160" fill="${on ? C.acc : '#141729'}" stroke="${C.faint}"/>
      ${mono(x - 130, y - 250, 'STAGE ' + (i + 1), { size: 14, fill: on ? C.navy : C.dim })}
      <text x="${f1(x - 130)}" y="${y - 185}" font-family="Black" font-size="${n.length > 9 ? 38 : 48}" fill="${on ? C.navy : '#fff'}">${n}</text>${mono(x - 130, y - 150, d, { size: 16, fill: on ? C.navy : C.acc })}</g>`;
    if (k > 0) s += `<path d="M${f1(x)} ${y + 20} L${f1(x)} ${y + 120}" stroke="${on ? C.acc : C.faint}" stroke-width="40" opacity=".35"/>`; });
  s += cap('s20', [['Put all of these senses together,', {}], ['and you get a hunting sequence.', { 4: C.acc, 5: C.acc }], ['Smell works from far away.', { 0: C.acc }], ['Then the lateral line feels the movement.', { 2: C.acc, 3: C.acc }], ['Then the eyes lock on.', { 2: C.acc }], ['when the eyes roll back,', {}], ['electricity guides the bite.', { 0: C.acc }]], t, { size: 56 });
  return s + close();
}

// 21 ultrasound pups
export function s21(t, len) {
  let s = open('#000000');
  s += header(t, 'reproduction', 23);
  const tf = at('s21', 'the pups feed'), tp = at('s21', 'Pregnancy may'), tbn = at('s21', "When they're finally"), ta = at('s21', 'And they swim away');
  if (t < ta - 0.2) {
    const cx = 900, cy = 160, R = 760, a = 0.5;
    const fan = `M${cx} ${cy} L${f1(cx - Math.sin(a) * R)} ${f1(cy + Math.cos(a) * R)} A${R} ${R} 0 0 0 ${f1(cx + Math.sin(a) * R)} ${f1(cy + Math.cos(a) * R)}Z`;
    s += `<defs><clipPath id="fan"><path d="${fan}"/></clipPath><radialGradient id="us" cx="${cx}" cy="${cy}" r="${R}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#111"/><stop offset=".5" stop-color="#2a2a2a"/><stop offset="1" stop-color="#151515"/></radialGradient></defs>`;
    s += `<g clip-path="url(#fan)"><rect width="${W}" height="${H}" fill="url(#us)"/>`;
    seed(Math.floor(t * 12) + 1); for (let i = 0; i < 700; i++) s += `<rect x="${f1(cx - 400 + rnd() * 800)}" y="${f1(cy + 80 + rnd() * 680)}" width="${f1(2 + rnd() * 8)}" height="2" fill="#fff" opacity="${f1(rnd() * 0.25)}"/>`;
    // womb outline + pups
    s += `<ellipse cx="${cx}" cy="${cy + 470}" rx="330" ry="190" fill="#060606" stroke="#bbb" stroke-width="4" opacity=".9"/>`;
    const pk = sm(0.8, 2, t);
    [[-150, 430, 0.22, 10], [90, 500, 0.24, -8]].forEach(([dx, dy, sc, r], i) => { const wob = Math.sin(t * 1.2 + i) * 4;
      s += `<g opacity="${f1(pk * 0.9)}" transform="translate(${cx + dx} ${f1(cy + dy + wob)}) rotate(${r}) scale(${sc}) translate(-500 -200)"><path d="${SHARK}" fill="#d9d9d9" opacity=".75"/></g>`; });
    // egg dots
    const ek = sm(tf - 0.2, tf + 0.5, t);
    seed(21); for (let i = 0; i < 18; i++) s += `<circle cx="${f1(cx - 260 + rnd() * 520)}" cy="${f1(cy + 360 + rnd() * 220)}" r="${f1(5 + rnd() * 6)}" fill="#f0e0a0" opacity="${f1(ek * 0.8)}"/>`;
    s += `</g><path d="${fan}" fill="none" stroke="#666" stroke-width="2"/>`;
    s += mono(80, 200, 'ULTRASOUND · OB · SPECIMEN 001', { size: 16, fill: '#aaa' }) + mono(80, 226, 'Carcharodon carcharias ♀', { size: 16, fill: '#aaa' });
    s += mono(1440, 300, 'PUPS', { size: 16, fill: '#aaa' }) + `<text x="1440" y="370" font-family="Black" font-size="64" fill="#fff">2 – 10</text>`;
    if (t > tf) s += mono(1440, 430, 'FEED: unfertilized eggs', { size: 18, fill: C.gold });
    if (t > tp) s += mono(1440, 500, 'GESTATION', { size: 16, fill: '#aaa' }) + `<text x="1440" y="570" font-family="Black" font-size="64" fill="#fff">${cycle('12+', t, tp, 0.6)}</text>` + mono(1440, 604, 'months · maybe more', { size: 16, fill: '#aaa' });
    if (t > tbn) s += mono(1440, 680, 'LENGTH AT BIRTH', { size: 16, fill: '#aaa' }) + `<text x="1440" y="750" font-family="Black" font-size="64" fill="#fff">${cycle('> 1 m', t, tbn, 0.6)}</text>` + mono(1440, 784, 'full set of teeth', { size: 16, fill: C.acc });
  } else {
    // newborn swims off, alone
    s += `<rect width="${W}" height="${H}" fill="${C.navy}"/>` + grid() + header(t, 'reproduction', 23);
    const u = eo(ta, ta + 6, t);
    s += `<g transform="translate(${f1(lerp(420, 1400, u))} 420) scale(0.36)"><path d="${SHARK}" fill="#c9cde0" stroke="${C.ink}" stroke-width="5"/><circle cx="905" cy="190" r="12" fill="${C.navy}"/></g>`;
    s += `<path d="M120 680 L1800 680" stroke="${C.ink}" stroke-dasharray="4 10" opacity=".4"/>` + mono(120, 710, 'DAY 1', { size: 16 });
    const t1 = at('s21', 'No parents'), t2 = at('s21', 'No lessons');
    s += mono(1300, 300, '', {}) + (t > t1 ? `<text x="1800" y="250" font-family="Black" font-size="90" fill="#fff" text-anchor="end" opacity="${f1(sm(t1, t1 + 0.3, t))}">NO PARENTS.</text>` : '')
      + (t > t2 ? `<text x="1800" y="350" font-family="Black" font-size="90" fill="${C.acc}" text-anchor="end" opacity="${f1(sm(t2, t2 + 0.3, t))}">NO LESSONS.</text>` : '');
  }
  s += cap('s21', [['And one last part, found only in females.', { 6: C.acc }], ['Great white babies grow inside their mother.', { 4: C.acc }], ['the pups feed on unfertilized eggs', { 4: C.gold, 5: C.gold }], ['Pregnancy may last more than a year.', { 6: C.acc }], ["they're already over a meter long,", { 3: C.acc, 4: C.acc }], ['with a full set of teeth.', { 3: C.acc }], ['And they swim away on their own.', { 5: C.acc, 6: C.acc }]], t, { size: 54, fill: '#ffffff' });
  return s + close();
}

// 22 deep-time timeline (paper)
export function s22(t, len) {
  let s = open(C.paper) + header(t, 'deep time', 24, { dark: false });
  const x0 = 140, x1 = 1780, y = 470, mya = m => lerp(x0, x1, 1 - m / 460);
  const k = eo(0.2, 2.0, t);
  s += `<path d="M${x0} ${y} L${f1(lerp(x0, x1, k))} ${y}" stroke="${C.pInk}" stroke-width="4"/>`;
  for (let m = 450; m >= 0; m -= 50) { const x = mya(m); if (x > lerp(x0, x1, k)) continue; s += `<path d="M${f1(x)} ${y - 10} L${f1(x)} ${y + 10}" stroke="${C.pInk}" stroke-width="2"/>${mono(x, y + 40, m === 0 ? 'now' : m + ' Mya', { size: 15, fill: C.pDim, anchor: 'middle' })}`; }
  const ev = [['first sharks', '> 400 million years', 430, at('s22', 'Sharks, as a group'), C.red, -1], ['first trees', '≈ 385 million years', 385, at('s22', "That's older than trees"), '#3f7a4a', 1], ['dinosaurs', '≈ 230', 230, at('s22', "That's older than trees") + 0.8, C.pDim, -1], ['humans', '≈ 0.3', 1, at('s22', "That's older than trees") + 1.4, C.pDim, 1]];
  ev.forEach(([a, b, m, tt, col, side]) => { const kk = sm(tt - 0.1, tt + 0.3, t); if (kk <= 0) return; const x = mya(m), ty = y + side * 120;
    s += `<g opacity="${f1(kk)}"><path d="M${f1(x)} ${y} L${f1(x)} ${ty + (side < 0 ? 26 : -40)}" stroke="${col}" stroke-width="2"/><circle cx="${f1(x)}" cy="${y}" r="9" fill="${col}"/>
      ${txt(x + (m < 50 ? -12 : 12), ty + (side < 0 ? 0 : 0), a, { font: 'SerifI', size: 44, fill: col, anchor: m < 50 ? 'end' : 'start' })}${mono(x + (m < 50 ? -12 : 12), ty + 28, b, { size: 15, fill: C.pDim, anchor: m < 50 ? 'end' : 'start' })}</g>`; });
  // female life bar
  const tf = at('s22', 'Females may not'), lk = sm(tf - 0.2, tf + 0.3, t);
  if (lk > 0) { const lx = 600, ly = 780, lw = 900, ax = n => lx + lw * n / 70;
    s += `<g opacity="${f1(lk)}">${mono(lx, ly - 30, 'FEMALE GREAT WHITE · LIFESPAN (years)', { size: 16, fill: C.pInk })}<rect x="${lx}" y="${ly}" width="${lw}" height="34" fill="#fff" stroke="${C.pInk}" stroke-width="2"/>
      <rect x="${lx}" y="${ly}" width="${f1((ax(30) - lx) * eo(tf, tf + 1.2, t))}" height="34" fill="${C.pDim}" opacity=".35"/>
      <path d="M${f1(ax(30))} ${ly - 14} L${f1(ax(30))} ${ly + 48}" stroke="${C.red}" stroke-width="4"/>${mono(ax(30), ly + 74, 'first pups · 30+', { size: 16, fill: C.red, anchor: 'middle' })}
      ${[0, 10, 20, 30, 40, 50, 60, 70].map(n => mono(ax(n), ly - 6, '', {})).join('')}${mono(lx, ly + 74, '0', { size: 14, fill: C.pDim })}${mono(lx + lw, ly + 74, '70+', { size: 14, fill: C.pDim, anchor: 'end' })}</g>`; }
  s += cap('s22', [['Sharks, as a group,', {}], ['more than four hundred million years.', { 2: C.red, 3: C.red, 4: C.red }], ["That's older than trees.", { 2: '#3f7a4a', 3: '#3f7a4a' }], ['great whites take their time.', { 3: C.red }], ['until they\'re over thirty.', { 3: C.red }], ['This design has been tested longer', { 4: C.red }]], t, { size: 56, fill: C.pInk });
  return s + close(false);
}

// 23 terminal summary → close specimen
export function s23(t, len) {
  let s = open('#06070d');
  s += `<rect x="60" y="60" width="1800" height="960" rx="28" fill="#0a0d18" stroke="#1d2238" stroke-width="3"/>`;
  for (let y = 70; y < 1010; y += 4) s += `<path d="M70 ${y} L1850 ${y}" stroke="#000" opacity=".22"/>`;
  s += mono(110, 130, 'specimen@lab:~$', { size: 22, fill: C.acc }) + mono(330, 130, 'cat specimen_001/summary.txt', { size: 22, fill: C.ink });
  const L = [['no bones', 'No bones.'], ['teeth on its skin', 'Teeth on its skin.'], ['a liver that floats', 'A liver that floats.'], ['muscles that run warm', 'Muscles that run warm.'], ['a sixth sense for electricity', 'A sixth sense']];
  L.forEach(([a, ph], i) => { const ti = at('s23', ph); s += typed(110, 210 + i * 56, `[${String(i + 1).padStart(2, '0')}]  ${a}`, t, ti, { size: 30, fill: i === 4 ? C.acc : C.ink, cps: 40, cursor: false }); });
  const tw = at('s23', "This is what's inside"), tn = at('s23', 'Next specimen?');
  // small open shark on the right
  const k = sm(tw - 0.2, tw + 0.5, t);
  if (k > 0) s += `<g opacity="${f1(k)}">${sharkOpen(980, 160, 0.78, { cut: 1000, id: 'e23', sw: 2, skin: '#1b1f36', stroke: '#e9e6f2' })}</g>`;
  s += typed(110, 560, "> This is what's inside a great white shark.", t, tw, { size: 34, fill: '#fff', cps: 26, cursor: false });
  s += typed(110, 660, '> close specimen_001', t, tw + 2.4, { size: 30, fill: C.acc, cps: 16, cursor: t < tn });
  if (t > tw + 4) s += mono(110, 710, 'specimen_001 closed · 25 sections logged', { size: 20, fill: C.dim });
  if (t > tn) { s += typed(110, 820, '> next specimen: ', t, tn, { size: 30, fill: C.ink, cps: 24 });
    s += mono(110, 880, 'tell us in the comments what we should open', { size: 20, fill: C.dim, op: sm(tn + 1, tn + 1.4, t) }); }
  return s + `<rect width="${W}" height="${H}" fill="url(#vig)"/></svg>`;
}
