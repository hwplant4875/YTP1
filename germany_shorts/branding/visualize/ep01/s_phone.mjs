import { wrap, f1, mix, clamp, smooth, seed, rnd, Cam, box } from './eng.mjs';
// POV: phone held in bed at night (screen space). mode 'feed' (endless scroll at 1:37 AM) | 'alarm' (setting 05:30)
const phoneBody = (inner, glowCol, { tilt = -3, x = 960, y = 560, sc = 1 } = {}) => {
  const w = 430 * sc, h = 880 * sc, r = 64 * sc;
  return `<g transform="translate(${x} ${y}) rotate(${tilt})">
  <ellipse cx="0" cy="${h * 0.15}" rx="${w * 1.1}" ry="${h * 0.6}" fill="${glowCol}" opacity=".07" filter="url(#b30)"/>
  <rect x="${-w / 2 - 14}" y="${-h / 2 - 14}" width="${w + 28}" height="${h + 28}" rx="${r + 12}" fill="#0b0c12"/>
  <rect x="${-w / 2 - 14}" y="${-h / 2 - 14}" width="${w + 28}" height="${h + 28}" rx="${r + 12}" fill="none" stroke="#2c2f3d" stroke-width="3"/>
  <clipPath id="scr"><rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="${r}"/></clipPath>
  <g clip-path="url(#scr)">${inner(w, h)}</g>
  <rect x="${-55 * sc}" y="${-h / 2 + 16}" width="${110 * sc}" height="${30 * sc}" rx="${15 * sc}" fill="#000"/>
  <!-- thumbs -->
  <path d="M${w / 2 + 40} ${h * 0.18} C${w / 2 - 30} ${h * 0.1} ${w / 2 - 60} ${h * 0.2} ${w / 2 - 70} ${h * 0.27} C${w / 2 - 60} ${h * 0.36} ${w / 2 + 10} ${h * 0.4} ${w / 2 + 60} ${h * 0.42} Z" fill="#c08a72"/>
  <path d="M${w / 2 - 30} ${h * 0.16} C${w / 2 - 55} ${h * 0.2} ${w / 2 - 66} ${h * 0.24} ${w / 2 - 68} ${h * 0.27}" stroke="#e0ab92" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
  <path d="M${-w / 2 - 40} ${h * 0.05} C${-w / 2 + 10} ${h * 0.02} ${-w / 2 + 20} ${h * 0.12} ${-w / 2 + 14} ${h * 0.2} C${-w / 2} ${h * 0.3} ${-w / 2 - 30} ${h * 0.34} ${-w / 2 - 60} ${h * 0.36} Z" fill="#b37e67"/>
  </g>`;
};
const status = (w, h, clock, dark = true) => `<text x="${-w / 2 + 44}" y="${-h / 2 + 40}" font-family="InterB" font-size="20" fill="${dark ? '#fff' : '#111'}">${clock}</text>
  <rect x="${w / 2 - 74}" y="${-h / 2 + 26}" width="34" height="16" rx="4" fill="none" stroke="${dark ? '#fff' : '#111'}" stroke-width="2"/><rect x="${w / 2 - 71}" y="${-h / 2 + 29}" width="${clock === '1:37' ? 7 : 26}" height="10" rx="2" fill="${clock === '1:37' ? '#ff5a4f' : (dark ? '#fff' : '#111')}"/>`;
export function phone(t, { mode = 'feed', clock = '1:37', set = 0 } = {}) {
  let s = `<rect width="1920" height="1080" fill="#0d0f1a"/>`;
  // blanket folds at the bottom, ceiling darkness
  s += `<path d="M0 860 C300 800 600 900 960 870 C1300 840 1600 900 1920 850 L1920 1080 L0 1080Z" fill="#1d2131"/>
  <path d="M0 950 C400 900 700 990 1100 960 C1450 930 1700 990 1920 960 L1920 1080 L0 1080Z" fill="#252a3d"/>`;
  if (mode === 'feed') {
    const scroll = t * 520 + 400 * Math.max(0, Math.sin(t * 2.2));
    s += `<ellipse cx="960" cy="950" rx="700" ry="140" fill="#8fb4ff" opacity=".12" filter="url(#b30)"/>`;
    s += phoneBody((w, h) => {
      let g = `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" fill="#101218"/>`;
      seed(11); const cards = [];
      for (let i = 0; i < 40; i++) cards.push([rnd(), rnd(), rnd()]);
      const ch = 330;
      cards.forEach(([a, b, c], i) => {
        const y = -h / 2 + 70 + i * ch - (scroll % (ch * 30));
        if (y < -h / 2 - ch || y > h / 2) return;
        const hue = ['#5a6fd8', '#d86a8a', '#e0a24c', '#4cb6a0', '#8a62d0'][Math.floor(a * 5)];
        g += `<circle cx="${-w / 2 + 40}" cy="${y + 26}" r="16" fill="${hue}" opacity=".9"/>
        <rect x="${-w / 2 + 66}" y="${y + 16}" width="${110 + b * 80}" height="10" rx="5" fill="#d9dbe6" opacity=".8"/>
        <rect x="${-w / 2 + 66}" y="${y + 32}" width="70" height="8" rx="4" fill="#8a8ea3" opacity=".7"/>
        <rect x="${-w / 2 + 20}" y="${y + 56}" width="${w - 40}" height="210" rx="14" fill="${hue}" opacity=".55"/>
        <circle cx="${-w / 2 + 20 + (w - 40) * (0.3 + c * 0.4)}" cy="${y + 140}" r="${36 + c * 30}" fill="#fff" opacity=".18"/>
        <rect x="${-w / 2 + 20}" y="${y + 280}" width="${w * 0.7}" height="9" rx="4" fill="#b8bccc" opacity=".55"/>`;
      });
      g += status(w, h, clock);
      return g;
    }, '#8fb4ff', { tilt: -3 + Math.sin(t * 0.7) * 0.8, y: 520 + Math.sin(t * 0.9) * 6 });
  } else {
    // alarm: wheel turns from 01:37 to 05:30, toggle switches on
    const k = smooth(0.2, 1.6, t), on = smooth(2.0, 2.4, t);
    const hh = Math.round(1 + 4 * k), mm = Math.round(37 + (30 - 37) * k);
    s += `<ellipse cx="960" cy="950" rx="700" ry="140" fill="#ffd2a6" opacity="${(0.08 + 0.1 * on).toFixed(2)}" filter="url(#b30)"/>`;
    s += phoneBody((w, h) => `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" fill="#08090d"/>
      ${status(w, h, clock)}
      <text x="${-w / 2 + 36}" y="${-h / 2 + 130}" font-family="InterB" font-size="44" fill="#fff">Alarm</text>
      <rect x="${-w / 2 + 24}" y="-150" width="${w - 48}" height="190" rx="22" fill="#16171e"/>
      <text x="${-w / 2 + 52}" y="-30" font-family="Inter" font-size="86" fill="${mix('#6b6f80', '#ffffff', on)}">${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}</text>
      <text x="${-w / 2 + 56}" y="15" font-family="Inter" font-size="20" fill="#8a8ea3">Every day · Run</text>
      <rect x="${w / 2 - 128}" y="-88" width="84" height="50" rx="25" fill="${mix('#3a3c48', '#ffb48a', on)}"/>
      <circle cx="${w / 2 - 103 + 34 * on}" cy="-63" r="21" fill="#fff"/>
      <text x="0" y="200" font-family="Mono" font-size="20" text-anchor="middle" fill="#ffd2a6" opacity="${on.toFixed(2)}">ALARM IN 3 HR 53 MIN</text>`, '#ffd2a6', { tilt: -2, y: 520 });
  }
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: 0, scale: 1 });
}
// dark kitchen, the fridge door swings open and light spills out
export function fridge(t) {
  const cam = new Cam({ y: 1.6, z: -0.9, pitch: -0.12, f: 1000, x: 0.02 * Math.sin(t) });
  const op = smooth(0.3, 1.4, t);
  let s = `<rect width="1920" height="1080" fill="#11131e"/>`;
  s += cam.poly([[-3, 0, -1], [3, 0, -1], [3, 0, 3], [-3, 0, 3]], '#161a28');
  s += cam.poly([[-3, 0, 2.4], [3, 0, 2.4], [3, 2.6, 2.4], [-3, 2.6, 2.4]], '#151827');
  // counters
  s += box(cam, [-2.5, 0, 1.8], [-0.55, 0.9, 2.4], { top: '#232838', front: '#1a1e2c', side: '#1d2130' });
  s += box(cam, [0.55, 0, 1.8], [2.5, 0.9, 2.4], { top: '#232838', front: '#1a1e2c', side: '#1d2130' });
  // light spill on floor
  s += cam.poly([[-0.5, 0.002, 1.75], [0.5, 0.002, 1.75], [1.1, 0.002, 0.2], [-1.1, 0.002, 0.2]], '#fff3d8', `opacity="${(0.28 * op).toFixed(2)}"`);
  // fridge body
  s += box(cam, [-0.5, 0, 1.8], [0.5, 1.9, 2.4], { top: '#2a2f42', front: '#22273a', side: '#22273a' });
  // interior (lit)
  const IN = (u, v) => [-0.45 + 0.9 * u, 0.1 + 1.7 * v, 1.82];
  s += cam.poly([IN(0, 0), IN(1, 0), IN(1, 1), IN(0, 1)], mix('#22273a', '#fff6e2', op));
  for (const v of [0.3, 0.55, 0.8]) s += cam.poly([IN(0, v), IN(1, v), IN(1, v + 0.015), IN(0, v + 0.015)], mix('#22273a', '#d9d2c4', op));
  if (op > 0.05) {
    const it = (u, v, w, h, c) => s += cam.poly([IN(u, v), IN(u + w, v), IN(u + w, v + h), IN(u, v + h)], c, `opacity="${op.toFixed(2)}"`);
    it(0.08, 0.315, 0.18, 0.2, '#e8b04a'); it(0.32, 0.315, 0.12, 0.17, '#c4483f'); it(0.5, 0.315, 0.35, 0.09, '#f4e3c8');
    it(0.1, 0.565, 0.3, 0.12, '#9b5a3c'); it(0.5, 0.565, 0.1, 0.2, '#6a8bd6'); it(0.65, 0.565, 0.1, 0.2, '#6a8bd6');
    it(0.15, 0.815, 0.5, 0.1, '#e6dccd'); it(0.2, 0.06, 0.6, 0.18, '#d6ccbc');
  }
  // door swinging toward the camera (hinged on the left)
  const ang = op * 1.75, dx = Math.cos(ang) * 1.0, dz = -Math.sin(ang) * 1.0;
  s += cam.poly([[-0.5, 0.05, 1.8], [-0.5 + dx, 0.05, 1.8 + dz], [-0.5 + dx, 1.85, 1.8 + dz], [-0.5, 1.85, 1.8]], mix('#2a2f42', '#6d7088', op));
  const [gx, gy] = cam.p([0, 1.0, 1.85]);
  s += `<ellipse cx="${f1(gx)}" cy="${f1(gy)}" rx="420" ry="360" fill="#fff3d8" opacity="${(0.14 * op).toFixed(2)}" filter="url(#b30)"/>`;
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -0.6, scale: 1.03 });
}
// front door opening onto blue pre-dawn, shoes on the mat
export function door(t) {
  const cam = new Cam({ y: 1.62, z: -0.6 + smooth(2.2, 3.8, t) * 0.7, pitch: -0.2, f: 1000 });
  const op = smooth(0.6, 2.2, t);
  let s = `<rect width="1920" height="1080" fill="#151827"/>`;
  s += cam.poly([[-1, 0, -1], [1, 0, -1], [1, 0, 2.6], [-1, 0, 2.6]], '#1e2233');
  s += cam.poly([[-1, 0, -1], [-1, 0, 2.6], [-1, 2.5, 2.6], [-1, 2.5, -1]], '#23283b');
  s += cam.poly([[1, 0, -1], [1, 0, 2.6], [1, 2.5, 2.6], [1, 2.5, -1]], '#262b3f');
  for (const [hx, hz] of [[-0.98, 1.2], [-0.98, 1.6]]) s += cam.poly([[hx, 1.5, hz], [hx, 1.5, hz + 0.25], [hx + 0.02, 0.9, hz + 0.3], [hx + 0.02, 0.9, hz - 0.05]], '#3a4160');
  s += cam.poly([[-1, 0, 2.6], [1, 0, 2.6], [1, 2.5, 2.6], [-1, 2.5, 2.6]], '#1c2031');
  // doorway: outside pre-dawn
  const D = (u, v) => [-0.45 + 0.9 * u, 2.05 * v, 2.6];
  s += cam.poly([D(0, 0), D(1, 0), D(1, 1), D(0, 1)], '#7d8fd0');
  s += cam.poly([D(0, 0.55), D(1, 0.55), D(1, 1), D(0, 1)], '#a7a6dc');
  s += cam.poly([D(0, 0), D(1, 0), D(1, 0.33), D(0, 0.33)], '#3c4778');
  for (let i = 0; i < 4; i++) s += cam.poly([D(0.05 + i * 0.25, 0.33), D(0.2 + i * 0.25, 0.33), D(0.2 + i * 0.25, 0.42 + (i % 2) * 0.06), D(0.05 + i * 0.25, 0.42 + (i % 2) * 0.06)], '#55609a');
  // light spill
  s += cam.poly([[-0.45, 0.002, 2.6], [0.45, 0.002, 2.6], [0.8, 0.002, 1.0], [-0.8, 0.002, 1.0]], '#a9b8f0', `opacity="${(0.3 * op).toFixed(2)}"`);
  // door leaf swinging inward (hinge right)
  const ang = op * 1.5, dx = -Math.cos(ang) * 0.9, dz = -Math.sin(ang) * 0.9;
  s += cam.poly([[0.45, 0, 2.6], [0.45 + dx, 0, 2.6 + dz], [0.45 + dx, 2.05, 2.6 + dz], [0.45, 2.05, 2.6]], '#2b3047');
  s += cam.disc([0.45 + dx * 0.9, 1.0, 2.6 + dz * 0.9], 0.03, '#c9a46a');
  // mat + running shoes
  s += cam.poly([[-0.4, 0.004, 1.9], [0.4, 0.004, 1.9], [0.4, 0.004, 2.4], [-0.4, 0.004, 2.4]], '#2a2f45');
  for (const [x, z] of [[-0.2, 2.0], [0.05, 2.05]]) {
    s += box(cam, [x, 0, z], [x + 0.11, 0.04, z + 0.28], { top: '#f2f2f2', front: '#e1e1e6', side: '#d4d4dc' });
    s += box(cam, [x + 0.01, 0.04, z + 0.03], [x + 0.1, 0.1, z + 0.22], { top: '#ff8a5b', front: '#f07a4c', side: '#e86f42' });
  }
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -0.8, scale: 1.03 });
}
