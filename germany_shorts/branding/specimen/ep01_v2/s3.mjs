import { K, W, H, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, place, toScr, sharkSolid, sharkInside, sharkOpen, bob, PT, icon, ICON, cross, count, SHARK, fade, xfade } from './eng2.mjs';
import { at } from './tl2.mjs';
const wave = (wl, t, c = '#fff') => `<path d="M0 ${wl} ${Array.from({ length: 49 }, (_, i) => `L${i * 40} ${f1(wl + 8 * Math.sin(i * 0.5 + t * 2.5))}`).join(' ')}" stroke="${c}" stroke-width="6" fill="none"/>`;

// 19 U stomach → spiral valve → stomach turned inside out
export function n19(t) {
  const tv = at('n19', 'something really weird'), tg = at('n19', "And here's a gross");
  let s = '';
  if (t < tv - 0.15) {
    const d = 'M760 260 C760 760 1160 760 1160 420 L1160 300';
    s += `<path d="${d}" fill="none" stroke="${K.navy}" stroke-width="150" stroke-linecap="round"/><path d="${d}" fill="none" stroke="${K.purple}" stroke-width="130" stroke-linecap="round"/>`;
    seed(19); for (let i = 0; i < 6; i++) { const u = ((t * 0.25 + i / 6) % 1); const y = lerp(120, 600, u); s += `<circle cx="${f1(760 + 8 * Math.sin(i))}" cy="${f1(y)}" r="22" fill="${K.yellow}" stroke="${K.navy}" stroke-width="5" opacity="${f1(sm(0, 0.1, u) * (1 - sm(0.85, 1, u)))}"/>`; }
    s += tag(1160, 520, 1560, 640, 'STOMACH', t, at('n19', 'stomach'), { col: K.purple, txt: '#fff' }) + big(960, 960, 'U', t, at('n19', 'letter U'), { size: 200, fill: K.yellow, stroke: K.navy, sw: 14 });
  } else if (t < tg - 0.15) {
    const vx = 260, vy = 540, vw = 1400, vh = 300, turns = 6, k = eo(tv, tv + 1.6, t);
    s += `<rect x="${vx}" y="${vy - vh / 2}" width="${vw}" height="${vh}" rx="${vh / 2}" fill="#f3e8ff" stroke="${K.navy}" stroke-width="10"/>`;
    let back = '', front = '';
    for (let i = 0; i < turns; i++) { const x = vx + 80 + i * (vw - 160) / turns, w = (vw - 160) / turns;
      back += `<path d="M${f1(x)} ${vy + vh / 2 - 20} C${f1(x + w * 0.2)} ${vy} ${f1(x + w * 0.3)} ${vy - vh / 2 + 20} ${f1(x + w * 0.5)} ${vy - vh / 2 + 20}" stroke="#c9b4ec" stroke-width="22" fill="none" stroke-linecap="round"/>`;
      front += `<path d="M${f1(x + w * 0.5)} ${vy - vh / 2 + 20} C${f1(x + w * 0.7)} ${vy - vh / 2 + 20} ${f1(x + w * 0.8)} ${vy} ${f1(x + w)} ${vy + vh / 2 - 20}" stroke="${K.purple}" stroke-width="26" fill="none" stroke-linecap="round"/>`; }
    s += `<defs><clipPath id="v19"><rect x="${vx}" y="${vy - vh / 2 - 20}" width="${f1(vw * k)}" height="${vh + 40}"/></clipPath></defs><g clip-path="url(#v19)">${back}${front}</g>`;
    const tf = at('n19', 'so food spins');
    if (t > tf - 0.3) { const u = ((t - tf + 0.3) * 0.16) % 1, x = vx + 80 + u * (vw - 160), y = vy - Math.cos(u * turns * 2 * Math.PI) * (vh / 2 - 40); s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="30" fill="${K.yellow}" stroke="${K.navy}" stroke-width="7"/>`; }
    s += big(960, 190, 'SPIRAL VALVE', t, at('n19', 'spiral valve'), { size: 140 });
    s += big(960, 900, 'CORKSCREW!', t, at('n19', 'corkscrew'), { size: 130, fill: K.yellow, stroke: K.navy, sw: 14 });
  } else {
    const cx = 260, cy = 560, sc = 2.2, out = sm(at('n19', 'push their stomach'), at('n19', 'push their stomach') + 1, t) * (1 - sm(at('n19', 'pull it back'), at('n19', 'pull it back') + 1, t));
    s += place(cx, cy, sc, sharkSolid('#fff', K.navy, 4));
    const [mx, my] = toScr(cx, cy, sc, 975, 232);
    if (out > 0.01) s += `<g transform="translate(${f1(mx)} ${f1(my)}) scale(${f1(out * 100) / 100})"><path d="M0 0 C120 -60 300 -40 320 40 C330 120 160 140 0 30Z" fill="${K.purple}" stroke="${K.navy}" stroke-width="9"/></g>`;
    s += big(1450, 230, 'EWW!', t, at('n19', 'gross one'), { size: 200, fill: K.green, stroke: K.navy, sw: 16, rot: -6 });
    s += tag(mx + 160 * out, my + 40, 1500, 900, 'STOMACH', t, at('n19', 'push their stomach') + 0.4, { col: K.purple, txt: '#fff' });
  }
  return s;
}

// 20 electric sense
export function n20(t) {
  const te = at('n20', 'Every living'); let s = '';
  if (t < te - 0.15) {
    const cx = 100, cy = 560, sc = 2.6;
    s += place(cx, cy, sc, sharkSolid('#dfe6f0', K.navy, 4));
    const pk = sm(at('n20', 'dots'), at('n20', 'dots') + 0.6, t), ek = sm(at('n20', 'feel electricity'), at('n20', 'feel electricity') + 0.4, t);
    seed(20); let g = '';
    for (let i = 0; i < 46; i++) { const bx = 925 + rnd() * 55, by = 198 + rnd() * 26 - (bx - 925) * 0.12; if (bx > 978) continue; const [X, Y] = toScr(cx, cy, sc, bx, by);
      g += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="${f1(6 + 4 * ek * Math.max(0, Math.sin(t * 8 + i)))}" fill="${ek > 0 ? K.yellow : K.navy}" opacity="${f1(pk)}"/>`; }
    s += g + tag(...toScr(cx, cy, sc, 955, 205), 1560, 300, 'PORES', t, at('n20', 'tiny pores'), { col: '#fff' });
    s += icon('bolt', 1600, 720, 1.3, t, at('n20', 'feel electricity')) + big(1100, 930, 'ELECTRIC SENSE', t, at('n20', 'feel electricity') + 0.2, { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
    s += big(960, 130, 'SUPERPOWERS', t, 0.3, { size: 110 });
  } else {
    const sy = 760, fx = 1240;
    s += `<rect x="0" y="${sy}" width="${W}" height="${H - sy}" fill="${K.sand}"/><path d="M0 ${sy} ${Array.from({ length: 25 }, (_, i) => `L${i * 80} ${sy + 10 * Math.sin(i)}`).join(' ')}" stroke="${K.navy}" stroke-width="6" fill="none"/>`;
    const ek = sm(te, te + 0.5, t);
    for (let i = 0; i < 4; i++) { const r = ((t * 120 + i * 80) % 320); s += `<ellipse cx="${fx}" cy="${sy + 50}" rx="${f1(r * 1.6)}" ry="${f1(r)}" fill="none" stroke="${K.yellow}" stroke-width="7" opacity="${f1(ek * (1 - r / 320))}"/>`; }
    s += `<g transform="translate(${fx} ${sy + 60}) scale(1.4)"><path d="M-90 0 C-50 -55 50 -55 90 0" fill="#c9a86a" stroke="${K.navy}" stroke-width="6"/><circle cx="-40" cy="-22" r="10" fill="#fff" stroke="${K.navy}" stroke-width="4"/><circle cx="-40" cy="-22" r="4" fill="${K.navy}"/></g>`;
    const tc = at('n20', "can't hide"), u = eo(at('n20', 'So even'), tc + 0.6, t);
    s += place(lerp(300, fx - 300, u), lerp(330, 560, u), 0.62, sharkSolid('#fff', K.navy, 11), { rot: lerp(0, 18, u) });
    s += tag(fx, sy + 20, 1560, 300, 'HIDDEN FISH', t, at('n20', 'a fish hiding'), { col: '#fff' });
    s += big(960, 130, 'FOUND YOU!', t, tc, { size: 140, fill: K.yellow, stroke: K.navy, sw: 14 });
  }
  return s;
}

// 21 lateral line
export function n21(t) {
  const cx = 820, cy = 540, sc = 1.25, y = cy + bob(t, 5);
  let s = place(cx, y, sc, sharkSolid('#fff', K.navy, 6));
  const lk = eo(at('n21', 'a line of sensors') - 0.2, at('n21', 'a line of sensors') + 1.4, t);
  if (lk > 0) s += place(cx, y, sc, `<path d="M170 192 C350 186 550 188 700 196 C780 200 860 196 900 200" pathLength="1" stroke="${K.yellow}" stroke-width="14" fill="none" stroke-linecap="round" stroke-dasharray="${f1(lk * 1000) / 1000} 2"/>`);
  s += tag(...toScr(cx, y, sc, 450, 188), 820, 150, 'LATERAL LINE', t, at('n21', 'lateral line'), { col: K.yellow });
  const tf = at('n21', 'A fish splashing'), fx = 1760, fy = 300;
  if (t > tf) { s += `<g transform="translate(${fx} ${fy}) rotate(${f1(20 * Math.sin(t * 16))}) scale(0.9)">${ICON.fish()}</g>`;
    for (let i = 0; i < 5; i++) { const r = ((t - tf) * 300 + i * 200) % 1000; s += `<circle cx="${fx}" cy="${fy}" r="${f1(r)}" fill="none" stroke="#fff" stroke-width="8" opacity="${f1(0.8 * (1 - r / 1000))}"/>`; } }
  s += big(820, 960, 'FEELS IT!', t, at('n21', 'The shark feels'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14 });
  return s;
}

// 22 smell: nostrils only for smelling, big smell brain
export function n22(t) {
  const tb = at('n22', 'The brain is small'); let s = '';
  if (t < tb - 0.15) {
    const cx = 100, cy = 560, sc = 2.6;
    s += place(cx, cy, sc, sharkSolid('#fff', K.navy, 4));
    const [nx, ny] = toScr(cx, cy, sc, 945, 214);
    s += `<ellipse cx="${f1(nx)}" cy="${f1(ny)}" rx="26" ry="12" fill="${K.navy}"/>`;
    s += tag(nx, ny, 1560, 280, 'NOSTRIL', t, at('n22', 'two nostrils'), { col: '#fff' });
    if (t > at('n22', 'They\'re only')) s += `<g transform="translate(${f1(nx + 200)} ${f1(ny + 40)}) rotate(-90) scale(1.1)">${ICON.smell()}</g>`;
    s += big(1100, 930, 'ONLY FOR SMELL', t, at('n22', "They're only"), { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
    if (t > at('n22', "doesn't breathe")) s += cross(1640, 560, 80, t, at('n22', "doesn't breathe")) + big(1640, 700, 'NO AIR', t, at('n22', "doesn't breathe"), { size: 70 });
  } else {
    // top view of the head with the real brain layout: spinal cord, cerebellum, optic lobes, forebrain, long smell tracts, huge smell bulbs
    const hi = sm(at('n22', 'the part used'), at('n22', 'the part used') + 0.5, t), puls = 1 + 0.06 * Math.sin(t * 6) * hi;
    const B = '#f2d3c4', o = `stroke="${K.navy}" stroke-width="6"`, sm1 = hi > 0 ? K.red : B;
    let g = `<path d="M-620 -250 C-300 -262 100 -240 340 -160 C480 -110 570 -44 592 0 C570 44 480 110 340 160 C100 240 -300 262 -620 250Z" fill="#fff" fill-opacity=".14" stroke="#fff" stroke-width="7"/>`;
    g += [-1, 1].map(sg => `<ellipse cx="170" cy="${sg * 182}" rx="34" ry="22" fill="${K.navy}"/><circle cx="178" cy="${sg * 186}" r="7" fill="#fff"/>`).join('');
    g += `<path d="M-640 -20 L-330 -20 C-300 -40 -270 -50 -250 -46 L-250 46 C-270 50 -300 40 -330 20 L-640 20Z" fill="${B}" ${o}/>`;  // cord + medulla
    g += `<ellipse cx="-196" cy="0" rx="74" ry="92" fill="${B}" ${o}/><path d="M-250 -40 C-220 -30 -170 -30 -140 -44 M-262 0 C-220 10 -170 10 -126 0 M-250 40 C-220 30 -170 30 -140 44" stroke="${K.navy}" stroke-width="4" fill="none" opacity=".6"/>`;  // cerebellum
    g += [-1, 1].map(sg => `<ellipse cx="-70" cy="${sg * 58}" rx="66" ry="54" fill="${B}" ${o}/>`).join('');  // optic lobes
    g += [-1, 1].map(sg => `<ellipse cx="78" cy="${sg * 52}" rx="74" ry="60" fill="${B}" ${o}/><path d="M40 ${sg * 30} C70 ${sg * 50} 100 ${sg * 50} 120 ${sg * 30}" stroke="${K.navy}" stroke-width="4" fill="none" opacity=".5"/>`).join('');  // forebrain
    g += [-1, 1].map(sg => `<path d="M140 ${sg * 40} C220 ${sg * 50} 280 ${sg * 110} 330 ${sg * 160}" stroke="${K.navy}" stroke-width="30" fill="none" stroke-linecap="round"/><path d="M140 ${sg * 40} C220 ${sg * 50} 280 ${sg * 110} 330 ${sg * 160}" stroke="${sm1}" stroke-width="18" fill="none" stroke-linecap="round"/>
      <g transform="translate(372 ${sg * 168}) scale(${f1(puls * 100) / 100})"><ellipse rx="${f1(62 + 14 * hi)}" ry="${f1(46 + 10 * hi)}" fill="${sm1}" ${o}/></g>
      <g transform="translate(470 ${sg * 150})"><ellipse rx="44" ry="26" fill="#fff" ${o}/>${[-24, -12, 0, 12, 24].map(dx => `<path d="M${dx} -20 L${dx} 20" stroke="${K.navy}" stroke-width="3"/>`).join('')}</g>`).join('');  // smell tracts, bulbs, nose rosettes
    s += `<g transform="translate(860 500) scale(1.25)">${g}</g>`;
    const [bx, by] = [860 + 372 * 1.25, 500 - 168 * 1.25];
    s += tag(bx, by, 1640, 120, 'SMELL', t, at('n22', 'the part used'), { col: K.red, txt: '#fff', size: 80 });
    s += tag(860 - 196 * 1.25, 500 - 92 * 1.25, 330, 130, 'BRAIN', t, tb, { col: '#fff' });
    s += big(1100, 960, 'SUPER NOSE', t, at('n22', 'faint smells'), { size: 120, fill: K.yellow, stroke: K.navy, sw: 12 });
  }
  return s;
}

// 23 eye mirror → eyes roll back, bites blind
export function n23(t) {
  const tr = at('n23', 'And right when'); let s = '';
  if (t < tr - 0.15) {
    const cx = 760, cy = 540, R = 330;
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="#16304f" stroke="#fff" stroke-width="12"/>`;
    s += `<path d="M${cx - R * 0.5} ${cy - R * 0.866} A${R} ${R} 0 0 0 ${cx - R * 0.5} ${cy + R * 0.866}" stroke="#e6f6ff" stroke-width="40" fill="none" stroke-linecap="round"/>`;
    s += `<ellipse cx="${cx + R - 90}" cy="${cy}" rx="80" ry="110" fill="#bfe8ff" opacity=".8" stroke="${K.navy}" stroke-width="6"/>`;
    const rk = sm(at('n23', 'mirror'), at('n23', 'mirror') + 0.5, t);
    for (let i = -2; i <= 2; i++) { const yy = cy + i * 55, ph = ((t * 0.6 + i * 0.13) % 1 + 1) % 1, xb = cx - R + 40;
      const xin = lerp(1800, xb, Math.min(1, ph * 2)); s += `<path d="M1800 ${yy} L${f1(xin)} ${yy}" stroke="${K.yellow}" stroke-width="10" stroke-linecap="round" opacity=".9"/>`;
      if (ph > 0.5) s += `<path d="M${xb} ${yy} L${f1(lerp(xb, 1800, (ph - 0.5) * 2))} ${f1(yy - i * 30 * (ph - 0.5))}" stroke="#fff" stroke-width="8" stroke-dasharray="20 14" opacity="${f1(rk)}"/>`; }
    s += tag(cx - R + 10, cy - 160, 320, 170, 'MIRROR', t, at('n23', 'mirror'), { col: '#fff' }) + big(1400, 930, 'SEES IN THE DARK', t, at('n23', 'dark water'), { size: 90, fill: K.yellow, stroke: K.navy, sw: 10 });
  } else {
    const tro = at('n23', 'rolls its eyes'), roll = eo(tro, tro + 0.7, t), tb = at('n23', 'it bites blind'), bite = sm(tb - 0.3, tb, t) * (1 - sm(tb + 0.6, tb + 1.0, t));
    const cx = 20, cy = 600, sc = 2.8;
    let g = `<path d="${SHARK}" fill="#fff" stroke="${K.navy}" stroke-width="4" stroke-linejoin="round"/>`;
    g += [0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 178 C${722 + i * 17} 210 ${720 + i * 17} 240 ${712 + i * 17} 258" stroke="${K.navy}" stroke-width="3" fill="none" opacity=".5"/>`).join('');
    // jaw opens for the bite
    const jo = 6 + 34 * bite;
    g += `<path d="M880 236 C905 ${f1(236 + jo * 0.6)} 935 ${f1(236 + jo)} 972 ${f1(228 + jo * 0.6)} L980 226 C950 232 915 234 880 236Z" fill="#3a0f1e" stroke="${K.navy}" stroke-width="3"/>`;
    for (let i = 0; i < 6; i++) { const x = 900 + i * 12; g += `<path d="M${x} 234 l5 ${f1(6 + jo * 0.15)} l5 -${f1(6 + jo * 0.15)}Z" fill="#fff"/>`; }
    // eye: black, then rolls back so the tough white side faces out
    g += `<defs><clipPath id="ey23"><circle cx="905" cy="190" r="14"/></clipPath></defs><circle cx="905" cy="190" r="14" fill="${K.navy}"/>
      <g clip-path="url(#ey23)"><circle cx="${f1(905 + 30 * (1 - roll) + 3 * roll)}" cy="190" r="14" fill="#f2f2ea"/></g><circle cx="905" cy="190" r="14" fill="none" stroke="${K.navy}" stroke-width="3"/>`;
    s += place(cx, cy, sc, g);
    const [ex, ey] = toScr(cx, cy, sc, 905, 190);
    if (roll > 0 && roll < 1) s += `<path d="M${f1(ex + 70)} ${f1(ey - 60)} A90 90 0 0 0 ${f1(ex - 70)} ${f1(ey - 60)}" stroke="${K.yellow}" stroke-width="12" fill="none" stroke-linecap="round" opacity="${f1(Math.sin(Math.PI * roll))}"/>`;
    s += tag(ex, ey, 1500, 170, 'EYES ROLL BACK', t, tro, { col: '#fff', size: 72 });
    s += big(960, 960, 'BITES BLIND!', t, tb, { size: 160, fill: K.red, stroke: '#fff', sw: 16 });
  }
  return s;
}

// 24 spy-hopping
export function n24(t) {
  const wl = 640, tu = at('n24', 'They poke'), up = eo(tu - 0.2, tu + 1.4, t);
  let s = `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="${K.deep}" opacity=".6"/>`;
  const hy = lerp(wl + 500, wl - 300, up) + 6 * Math.sin(t * 2);
  s += `<g transform="translate(960 ${f1(hy)}) rotate(-90) scale(0.75) translate(-985 -212)"><path d="${SHARK}" fill="#fff" stroke="${K.navy}" stroke-width="10"/><circle cx="905" cy="190" r="13" fill="${K.navy}"/></g>`;
  s += `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="${K.deep}" opacity=".35"/>` + wave(wl, t);
  const lk = sm(at('n24', 'look around'), at('n24', 'look around') + 0.3, t);
  if (lk > 0) { const ex = 960, ey = hy - 80, a = Math.sin((t - at('n24', 'look around')) * 2) * 40; s += `<path d="M${ex} ${f1(ey)} L${f1(ex + Math.cos((a - 90) * Math.PI / 180) * 0 + 300 * Math.sin(a * Math.PI / 180))} ${f1(ey - 260)}" stroke="#fff" stroke-width="6" stroke-dasharray="14 12" opacity="${f1(lk)}"/>`; }
  s += big(960, 150, 'ABOVE THE WATER', t, 0.3, { size: 100 });
  s += big(1500, 470, 'SPY-HOP!', t, at('n24', 'spy-hopping'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14, rot: -5 });
  return s;
}

// 25 hunting sequence: smell → feel → see → zap
export function n25(t) {
  const st = [['SMELL', 'smell', at('n25', 'it smells'), K.cyan], ['FEEL', 'wave', at('n25', 'feels the movement'), '#fff'], ['SEE', 'eye', at('n25', 'it sees'), '#fff'], ['ZAP!', 'bolt', at('n25', 'uses electricity'), K.yellow]];
  const cur = st.reduce((a, x, i) => t > x[2] ? i : a, -1);
  let s = big(960, 130, 'THE HUNT', t, 0.3, { size: 120 });
  st.forEach(([n, ic, tn, c], i) => { const x = 330 + i * 420, y = 470, on = i === cur, k = pop(tn, t); if (k <= 0) { s += `<rect x="${x - 170}" y="${y - 170}" width="340" height="340" rx="40" fill="#fff" opacity=".12"/>`; return; }
    s += `<g transform="translate(${x} ${y}) scale(${f1((on ? 1.08 : 0.92) * k * 100) / 100})"><rect x="-170" y="-170" width="340" height="340" rx="40" fill="${on ? K.navy : '#2f6fa8'}" stroke="${on ? K.yellow : '#fff'}" stroke-width="10"/>
      <g transform="translate(0 -30) scale(${ic === 'eye' ? 1.1 : 0.9})">${ICON[ic](c)}</g><text y="130" font-family="Black" font-size="64" fill="#fff" text-anchor="middle">${n}</text></g>`;
    if (i < 3) s += `<path d="M${x + 185} ${y} l40 0" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity="${f1(k)}"/>`; });
  const u = eo(st[0][2] - 0.5, st[3][2] + 1, t), px = 1700, tc = at('n25', 'aim the bite') - 0.5;
  const fx = px + 900 * Math.pow(clamp((t - tc) / 0.7), 1.6), fy = 850 + (t > tc ? 30 * Math.sin((t - tc) * 30) : 0);
  const sx = lerp(260, px - 330, u) + 1200 * Math.pow(clamp((t - tc - 0.15) / 0.8), 1.7);
  s += place(sx, 850, 0.4, sharkSolid('#fff', K.navy, 14)) + `<g transform="translate(${f1(fx)} ${f1(fy)}) rotate(${t > tc ? f1(12 * Math.sin((t - tc) * 30)) : 0}) scale(-.8 .8)">${ICON.fish()}</g>`;
  if (t > tc) for (let i = 0; i < 3; i++) s += `<path d="M${f1(fx - 220 - i * 50)} ${f1(fy - 40 + i * 40)} L${f1(fx - 120 - i * 50)} ${f1(fy - 40 + i * 40)}" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity="${f1(0.7 * (1 - sm(tc + 0.6, tc + 0.9, t)))}"/>`;
  return s;
}

// 26 babies
export function n26(t) {
  const tb = at('n26', "When they're born"), ts = at('n26', 'swim off'); let s = '';
  if (t < tb - 0.15) {
    const cx = 960, cy = 600, sc = 1.42;
    s += place(cx, cy + bob(t, 5), sc, `<path d="${SHARK}" fill="#fff" fill-opacity=".25" stroke="#fff" stroke-width="7"/><circle cx="905" cy="190" r="9" fill="#fff"/><ellipse cx="560" cy="250" rx="190" ry="55" fill="${K.navy}" opacity=".35" stroke="#fff" stroke-width="4" stroke-dasharray="12 10"/>`);
    const tp = at('n26', 'two to ten'), n = t > tp ? 6 : 2;
    for (let i = 0; i < n; i++) { const k = i < 2 ? 1 : pop(tp + (i - 2) * 0.15, t); if (k <= 0) continue; const [x, y] = toScr(cx, cy, 1.42, 440 + (i % 3) * 110, 232 + Math.floor(i / 3) * 40);
      s += place(x, y + bob(t + i, 3, 2), 0.1 * k, sharkSolid('#fff', K.navy, 40)); }
    s += big(960, 170, '1 YEAR+', t, at('n26', 'a year'), { size: 170, fill: K.yellow, stroke: K.navy, sw: 14 });
    s += big(960, 960, '2–10 PUPS', t, tp, { size: 120 });
  } else {
    const u = eo(ts, ts + 3, t), bx = lerp(760, 2300, u * u);
    s += `<path d="M420 760 L${420 + 520} 760" stroke="#fff" stroke-width="12" stroke-linecap="round"/><path d="M420 735 L420 785 M940 735 L940 785" stroke="#fff" stroke-width="12" stroke-linecap="round"/>` + big(680, 850, '1 M+', t, at('n26', 'more than a meter'), { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
    s += place(bx - 80, 600, 0.56, sharkSolid('#fff', K.navy, 11));
    if (t < at('n26', 'on their own')) s += big(1350, 380, 'FULL SET', t, at('n26', 'full set'), { size: 90 }) + big(1350, 490, 'OF TEETH', t, at('n26', 'full set') + 0.2, { size: 90 });
    s += big(960, 200, 'ON ITS OWN!', t, at('n26', 'on their own'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14 });
  }
  return s;
}

// 27 older than trees and dinosaurs
export function n27(t) {
  let s = `<path d="M180 800 L1740 800" stroke="${K.navy}" stroke-width="12" stroke-linecap="round"/><path d="M1700 770 L1760 800 L1700 830Z" fill="${K.navy}"/>`;
  s += big(1600, 880, 'NOW', t, 0.3, { size: 60, fill: K.navy });
  const ts = at('n27', 'Sharks have been'), tt = at('n27', 'older than trees'), td = at('n27', 'dinosaurs');
  if (t > ts) { s += place(380, 600, 0.5, sharkSolid('#fff', K.navy, 14)); s += big(380, 880, '400M+ YEARS', t, at('n27', 'four hundred'), { size: 64, fill: K.red, stroke: '#fff', sw: 0 }); }
  s += big(380, 180, 'SHARKS', t, ts, { size: 90, fill: K.navy });
  s += icon('tree', 950, 580, 1.45, t, tt) + big(950, 180, 'TREES', t, tt, { size: 90, fill: K.navy });
  s += icon('dino', 1470, 600, 1.3, t, td) + big(1470, 180, 'DINOSAURS', t, td, { size: 90, fill: K.navy });
  if (t > tt) s += big(680, 420, '>', t, tt + 0.2, { size: 160, fill: K.red }); if (t > td) s += big(1210, 420, '>', t, td + 0.2, { size: 160, fill: K.red });
  return s;
}

// 27b fewer sharks → protected (safety bubble) → scientists track them (satellite tag)
export function n27b(t) {
  const tf = at('n27b', 'fewer'), tp = at('n27b', 'so they are protected'), tsc = at('n27b', 'Scientists study');
  const A = () => { let s = big(960, 150, 'FEWER SHARKS', t, tf, { size: 120 });
    for (let i = 0; i < 8; i++) { const x = 300 + (i % 4) * 440, y = 430 + Math.floor(i / 4) * 300, gone = [1, 2, 4, 6, 7].includes(i) ? sm(tf + 0.3 + i * 0.12, tf + 0.8 + i * 0.12, t) : 0;
      s += `<g opacity="${f1(1 - 0.75 * gone)}">${place(x + 20 * Math.sin(t + i), y + bob(t + i, 6), 0.3, gone > 0.5 ? `<path d="${SHARK}" fill="none" stroke="#fff" stroke-width="16" stroke-dasharray="40 30"/>` : sharkSolid('#fff', K.navy, 20))}</g>`; }
    return s; };
  const B = () => { const cx = 960, cy = 520, sh = sm(tp, tp + 0.8, t);
    let s = place(cx + 30 * Math.sin(t * 0.8), cy + bob(t, 8), 0.95, sharkSolid('#fff', K.navy, 9));
    if (sh > 0) { const r = 560 * eo(tp, tp + 0.8, t);
      s += `<ellipse cx="${cx}" cy="${cy}" rx="${f1(r)}" ry="${f1(r * 0.55)}" fill="${K.cyan}" fill-opacity=".14" stroke="${K.cyan}" stroke-width="14" opacity="${f1(sh)}"/>`;
      s += `<path d="M${f1(cx - r * 0.7)} ${f1(cy - r * 0.32)} A${f1(r * 0.8)} ${f1(r * 0.45)} 0 0 1 ${f1(cx - r * 0.2)} ${f1(cy - r * 0.5)}" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" opacity="${f1(0.7 * sh)}"/>`; }
    s += icon('shield', 1500, 260, 0.9, t, tp + 0.5);
    // satellite tag on the dorsal fin, blinking, with signal arcs to the sky
    const tk = sm(tsc, tsc + 0.4, t);
    if (tk > 0) { const [dx, dy] = toScr(cx + 30 * Math.sin(t * 0.8), cy + bob(t, 8), 0.95, 520, 70), bl = Math.sin(t * 8) > 0 ? 1 : 0.3;
      s += `<g opacity="${f1(tk)}"><rect x="${f1(dx - 26)}" y="${f1(dy - 8)}" width="52" height="30" rx="8" fill="${K.yellow}" stroke="${K.navy}" stroke-width="6"/><circle cx="${f1(dx + 12)}" cy="${f1(dy + 7)}" r="6" fill="${K.red}" opacity="${bl}"/>
        ${[0, 1, 2].map(i => { const r = 40 + ((t * 80 + i * 45) % 135); return `<path d="M${f1(dx - r * 0.7)} ${f1(dy - r * 0.7)} A${f1(r)} ${f1(r)} 0 0 1 ${f1(dx + r * 0.7)} ${f1(dy - r * 0.7)}" stroke="#fff" stroke-width="7" fill="none" opacity="${f1(1 - (r - 40) / 135)}"/>`; }).join('')}</g>`;
      s += tag(dx, dy - 20, 560, 200, 'TRACKER', t, tsc + 0.3, { col: K.yellow }); }
    s += t < tsc + 0.2 ? big(960, 960, 'PROTECTED', t, tp, { size: 170, fill: K.green, stroke: K.navy, sw: 14 }) : fade(960, 960, 'KEEP THEM SAFE', t, tsc + 0.2, { size: 130, fill: K.green, stroke: K.navy, sw: 14, d: 0.4 });
    return s; };
  return t < tp - 0.3 ? A() : xfade(t, tp - 0.3, 0.5, A, B);
}

// 28 summary on the opened shark → what next?
export function n28(t) {
  const cx = 960, cy = 560, sc = 1.42, y = cy + bob(t);
  const tn = at('n28', 'So, what should');
  let s = `<g transform="translate(${f1(cx - 500 * sc)} ${f1(y - 215 * sc)}) scale(${sc})">${sharkOpen(0, 0, 1, { cut: 1000, id: 'o28', skin: '#ffffff', stroke: K.navy, sw: 5.5 })}</g>`;
  const P = n => toScr(cx, y, sc, ...PT[n]);
  const items = [['0 BONES', 'spine', 'No bones', [700, 160], '#fff', K.navy], ['TOOTH SKIN', 'dorsal', 'Teeth on its skin', [1200, 140], '#fff', K.navy], ['FLOAT LIVER', 'liver', 'A liver that floats', [700, 960], K.yellow, K.navy], ['WARM', 'muscle', 'Muscles that stay', [320, 960], K.red, '#fff'], ['ELECTRIC', 'snout', 'sixth sense', [1520, 960], K.yellow, K.navy]];
  if (t < tn) items.forEach(([w, p, ph, [tx, ty], c, tc]) => { s += tag(...P(p), tx, ty, w, t, at('n28', ph), { col: c, txt: tc, size: 60 }); });
  else { s += `<rect width="${W}" height="${H}" fill="${K.navy}" opacity="${f1(0.7 * sm(tn, tn + 0.3, t))}"/>`;
    s += big(960, 420, 'WHAT SHOULD WE', t, tn, { size: 130 }) + big(960, 600, 'OPEN NEXT?', t, tn + 0.3, { size: 170, fill: K.yellow }) + big(960, 820, 'TELL US IN THE COMMENTS', t, at('n28', 'Tell us'), { size: 70 }); }
  return s;
}
