import { Cam, wrap, box, quad, mix, f1, clamp, smooth, seed, rnd } from './eng.mjs';

// top-down salad bowl on a table, morning light
export function salad(t) {
  const dx = 8 * Math.sin(t * 0.6), sc = 1 + 0.02 * t;
  let s = `<rect width="1920" height="1080" fill="#d8b994"/>`;
  for (let i = 0; i < 9; i++) s += `<rect x="-100" y="${i * 140 - 40}" width="2200" height="4" fill="#c9a882" opacity=".7"/>`;
  s += `<g transform="translate(${960 + dx} 560) scale(${sc})">
   <ellipse cx="30" cy="40" rx="430" ry="410" fill="#9f7f5f" opacity=".35" filter="url(#b12)"/>
   <circle r="400" fill="#f3efe8"/><circle r="350" fill="#e6dfd4"/><circle r="340" fill="#7da35d"/>`;
  seed(21);
  for (let i = 0; i < 46; i++) { const a = rnd() * 6.28, r = rnd() * 300, w = 50 + rnd() * 50;
    s += `<ellipse cx="${f1(Math.cos(a) * r)}" cy="${f1(Math.sin(a) * r)}" rx="${f1(w)}" ry="${f1(w * 0.45)}" transform="rotate(${f1(rnd() * 180)} ${f1(Math.cos(a) * r)} ${f1(Math.sin(a) * r)})" fill="${['#8fbf63', '#6e9a4c', '#a6cf73', '#5e8a42'][i % 4]}"/>`; }
  for (let i = 0; i < 7; i++) { const a = i * 0.9 + 0.3, r = 150 + (i % 3) * 50; s += `<circle cx="${f1(Math.cos(a) * r)}" cy="${f1(Math.sin(a) * r)}" r="34" fill="#e2483d"/><circle cx="${f1(Math.cos(a) * r - 10)}" cy="${f1(Math.sin(a) * r - 10)}" r="9" fill="#f7a39a"/>`; }
  for (let i = 0; i < 5; i++) s += `<path d="M${-60 + i * 30} ${-40 + i * 24} q 90 -40 160 20 q -80 30 -160 -20Z" fill="#c9d77a" stroke="#4f6b2e" stroke-width="6" transform="rotate(${-30 + i * 6})"/>`;
  for (let i = 0; i < 6; i++) { const a = -2.2 + i * 0.35; s += `<rect x="${f1(Math.cos(a) * 200 - 30)}" y="${f1(Math.sin(a) * 200 - 14)}" width="60" height="28" rx="6" fill="#f2e7c9" transform="rotate(${f1(a * 57)} ${f1(Math.cos(a) * 200)} ${f1(Math.sin(a) * 200)})"/>`; }
  s += `</g>`;
  // fork + glass of water
  s += `<g transform="translate(${1440 + dx} 600) rotate(8)"><rect x="-14" y="-260" width="28" height="420" rx="14" fill="#c9ccd4"/><rect x="-30" y="-330" width="60" height="90" rx="10" fill="#c9ccd4"/>${[0, 1, 2].map(k => `<rect x="${-22 + k * 17}" y="-420" width="10" height="110" rx="5" fill="#c9ccd4"/>`).join('')}</g>`;
  s += `<circle cx="${380 + dx}" cy="300" r="120" fill="#bfe1ee" opacity=".55"/><circle cx="${380 + dx}" cy="300" r="120" fill="none" stroke="#ffffff" stroke-width="8" opacity=".6"/><circle cx="${350 + dx}" cy="270" r="40" fill="#ffffff" opacity=".35"/>`;
  s += `<rect width="1920" height="1080" fill="url(#vig)" opacity=".7"/>`;
  return wrap(s, { roll: 0, scale: 1 });
}

// gym: walking past a dumbbell rack toward the window light
export function gym(t) {
  const cam = new Cam({ x: 0.2, y: 1.68 + 0.01 * Math.abs(Math.sin(t * 5)), z: 0.6 * t, pitch: -0.12, yaw: -0.1, f: 950 });
  let s = `<rect width="1920" height="1080" fill="#2a2d3d"/>`;
  const Z = 14;
  s += cam.poly([[-3, 3.2, -1], [3, 3.2, -1], [3, 3.2, Z], [-3, 3.2, Z]], '#262938');
  for (let z = 1; z < Z; z += 2.4) s += cam.poly([[-1.5, 3.18, z], [1.5, 3.18, z], [1.5, 3.18, z + 0.25], [-1.5, 3.18, z + 0.25]], '#f6f1e8');
  s += cam.poly([[-3, 0, -1], [3, 0, -1], [3, 0, Z], [-3, 0, Z]], '#30333f');
  for (let z = 0; z < Z; z += 1) s += cam.line([-3, 0, z], [3, 0, z], '#2a2c37', 2);
  s += cam.poly([[-3, 0, Z], [3, 0, Z], [3, 3.2, Z], [-3, 3.2, Z]], '#3a3e52');
  // big windows on the right with morning light
  s += cam.poly([[3, 0, -1], [3, 0, Z], [3, 3.2, Z], [3, 3.2, -1]], '#3a3e52');
  for (let z = 1; z < Z - 1; z += 3) s += cam.poly([[2.99, 0.7, z], [2.99, 0.7, z + 2.4], [2.99, 2.8, z + 2.4], [2.99, 2.8, z]], '#ffd9b0');
  for (let z = 1; z < Z - 1; z += 3) s += cam.poly([[2.98, 0.001, z], [2.98, 0.001, z + 2.4], [0.4, 0.002, z + 3.2], [0.4, 0.002, z + 0.8]], '#ffe2c0', 'opacity=".18"');
  // mirror wall left + rack
  s += cam.poly([[-3, 0, -1], [-3, 0, Z], [-3, 3.2, Z], [-3, 3.2, -1]], '#4a4f68');
  s += cam.poly([[-2.99, 0.4, 0], [-2.99, 0.4, Z - 0.5], [-2.99, 2.6, Z - 0.5], [-2.99, 2.6, 0]], '#5b6180');
  s += box(cam, [-2.95, 0, 0.5], [-2.35, 0.75, Z - 2], { top: '#1f212b', front: '#1a1c25', side: '#22242f', side2: '#22242f' });
  for (let z = 1; z < Z - 2.2; z += 0.55) {
    for (const yy of [0.82, 0.5]) {
      const c = cam.p([-2.6, yy, z]); const r = cam.px(0.09 + (z % 1.1) * 0.03, [-2.6, yy, z]);
      const c2 = cam.p([-2.6, yy, z + 0.3]); const r2 = cam.px(0.09 + (z % 1.1) * 0.03, [-2.6, yy, z + 0.3]);
      s += `<line x1="${f1(c[0])}" y1="${f1(c[1])}" x2="${f1(c2[0])}" y2="${f1(c2[1])}" stroke="#7d8196" stroke-width="${f1(r * 0.4)}"/>`;
      s += `<ellipse cx="${f1(c2[0])}" cy="${f1(c2[1])}" rx="${f1(r2 * 0.55)}" ry="${f1(r2)}" fill="#14151c"/><ellipse cx="${f1(c[0])}" cy="${f1(c[1])}" rx="${f1(r * 0.55)}" ry="${f1(r)}" fill="#1c1d26"/>`;
    }
  }
  // bench + barbell ahead
  s += box(cam, [-0.3, 0.3, 7], [0.3, 0.45, 8.4], { top: '#c4583f', front: '#9e4532', side: '#a84a36' });
  s += box(cam, [-0.05, 0, 7.6], [0.05, 0.3, 7.8], { front: '#20222c', side: '#20222c' });
  s += cam.line([-1.2, 1.1, 8.6], [1.2, 1.1, 8.6], '#9a9eb0', 6);
  for (const x of [-1.05, 1.05]) s += cam.disc([x, 1.1, 8.6], 0.24, '#1b1c25');
  for (const x of [-1.3, 1.3]) s += box(cam, [x - 0.04, 0, 8.55], [x + 0.04, 1.4, 8.65], { front: '#2a2c38', side: '#2a2c38' });
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -0.8 + 0.4 * Math.sin(t * 2.5), scale: 1.03 });
}

// stadium running track at sunrise, lane 3, entering the bend
export function track(t, { speed = 4.2 } = {}) {
  const d = speed * t + 6;
  const R0 = 36.5, L = 60; // straight length
  // centerline param: s along lane; straight along +z then bend to the left
  const lanePt = (sd, off) => {
    if (sd < L) return [off, 0, sd];
    const a = (sd - L) / (R0 + off * -1 + 0);
    const R = R0 - off;
    const ang = (sd - L) / R0;
    return [-R0 + (R0 + off) * Math.cos(ang), 0, L + (R0 + off) * Math.sin(ang)];
  };
  const pos = lanePt(d, 3.6), ahead = lanePt(d + 6, 3.6);
  const yaw = Math.atan2(ahead[0] - pos[0], ahead[2] - pos[2]);
  const ph = Math.PI * 3.0 * t;
  const cam = new Cam({ x: pos[0], y: 1.68 + 0.035 * (Math.abs(Math.sin(ph)) - 0.5), z: pos[2], yaw, pitch: -0.07, f: 980 });
  let s = `<defs><linearGradient id="tsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a78"/><stop offset=".6" stop-color="#d98a8a"/><stop offset="1" stop-color="#ffd2a6"/></linearGradient></defs>`;
  s += `<rect width="1920" height="1080" fill="url(#tsky)"/>`;
  const [hx, hy] = cam.p([pos[0] + Math.sin(yaw) * 5000, 0, pos[2] + Math.cos(yaw) * 5000]);
  s += `<circle cx="${f1(hx + 380)}" cy="${f1(hy - 10)}" r="380" fill="url(#glowW)" opacity=".7"/><circle cx="${f1(hx + 380)}" cy="${f1(hy + 4)}" r="44" fill="#fff1d6"/>`;
  s += `<rect x="-200" y="${f1(hy)}" width="2400" height="900" fill="#3d6a55"/>`;
  // stands (ring of blocks around the stadium)
  for (let k = 0; k < 28; k++) { const a = k / 28 * 6.283; const cx = -R0 + 90 * Math.cos(a), cz = L / 2 + 90 * Math.sin(a);
    s += box(cam, [cx - 9, 0, cz - 9], [cx + 9, 6 + (k % 3) * 1.2, cz + 9], { top: '#5d5277', front: '#4a4266', side: '#544a70', side2: '#544a70' }); }
  // infield grass + track surface as strips
  const strip = (o0, o1, col) => { let pts0 = [], pts1 = [];
    for (let sd = Math.max(0, d - 3); sd < d + 140; sd += 2) { pts0.push(lanePt(sd, o0)); pts1.push(lanePt(sd, o1)); }
    for (let i = pts0.length - 2; i >= 0; i--) s += cam.poly([pts0[i], pts0[i + 1], pts1[i + 1], pts1[i]], col);
  };
  strip(-20, 0, '#4f8a5f');
  strip(0, 9.8, '#c9573f');
  strip(9.8, 13, '#4f8a5f');
  for (let ln = 0; ln <= 8; ln++) { const o = ln * 1.22; let prev = null;
    for (let sd = Math.max(0, d - 2); sd < d + 140; sd += 2) { const p = lanePt(sd, o); p[1] = 0.003; if (prev) s += cam.line(prev, p, '#fbeee6', ln === 0 || ln === 8 ? 3 : 2.2, 'opacity=".9"'); prev = p; } }
  // floodlight poles
  for (const [x, z] of [[-10, 20], [-62, 20], [-10, 100], [-62, 100]]) { s += cam.line([x, 0, z], [x, 26, z], '#3a3550', 3); s += box(cam, [x - 1.5, 26, z - 0.3], [x + 1.5, 28, z + 0.3], { front: '#2b2740', side: '#2b2740' }); }
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -1 + 0.5 * Math.sin(ph), sway: 5 * Math.sin(ph / 2), scale: 1.04 });
}

// mountain trail at sunrise, walking/running uphill with switchbacks of distant ridges
export function mountain(t) {
  const sp = 2.2, d = sp * t;
  const pathX = z => 1.4 * Math.sin(z * 0.09) + 0.6 * Math.sin(z * 0.23);
  const pathY = z => z * 0.12;
  const cz = d, cx = pathX(cz), ahead = cz + 6;
  const yaw = Math.atan2(pathX(ahead) - cx, 6), pitchUp = Math.atan2(pathY(ahead) - pathY(cz), 6);
  const ph = Math.PI * 2.6 * t;
  const cam = new Cam({ x: cx, y: pathY(cz) + 1.68 + 0.03 * Math.abs(Math.sin(ph)), z: cz, yaw, pitch: pitchUp - 0.06, f: 960 });
  let s = `<defs><linearGradient id="msky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d3268"/><stop offset=".55" stop-color="#c77b8c"/><stop offset="1" stop-color="#ffcf9e"/></linearGradient></defs>`;
  s += `<rect width="1920" height="1080" fill="url(#msky)"/>`;
  const hy = cam.p([cx + Math.sin(yaw) * 9000, pathY(cz) + 1.68, cz + Math.cos(yaw) * 9000])[1];
  s += `<circle cx="1180" cy="${f1(hy - 70)}" r="420" fill="url(#glowW)" opacity=".75"/><circle cx="1180" cy="${f1(hy - 60)}" r="50" fill="#fff3dc"/>`;
  // distant ridges (screen space, parallax by yaw)
  const ridge = (base, amp, fr, col, par) => { let p = `M-100 1080 L-100 ${f1(base)}`;
    for (let x = -100; x <= 2020; x += 40) { const xx = x + yaw * par; p += ` L${x} ${f1(base - amp * (0.5 + 0.5 * Math.sin(xx * fr) * Math.cos(xx * fr * 0.37 + 1)))}`; }
    return `<path d="${p} L2020 1080Z" fill="${col}"/>`; };
  s += ridge(hy - 10, 200, 0.004, '#8a6f99', 300) + ridge(hy + 30, 160, 0.006, '#6b5585', 600) + ridge(hy + 80, 120, 0.009, '#4c4068', 900);
  // slope + trail
  s += cam.poly([[cx - 80, pathY(cz - 2) - 0.5, cz - 2], [cx + 80, pathY(cz - 2) - 0.5, cz - 2], [cx + 80, pathY(cz + 90) - 0.5, cz + 90], [cx - 80, pathY(cz + 90) - 0.5, cz + 90]], '#3c3a5c');
  for (let z = Math.floor(cz) + 90; z > cz - 1; z -= 1) {
    const a = [pathX(z) - 0.8, pathY(z), z], b = [pathX(z) + 0.8, pathY(z), z], c = [pathX(z + 1) + 0.8, pathY(z + 1), z + 1], e = [pathX(z + 1) - 0.8, pathY(z + 1), z + 1];
    s += cam.poly([a, b, c, e], z % 4 < 2 ? '#a07f86' : '#9a7a82');
  }
  // pine trees on both sides
  seed(5);
  const trees = []; for (let i = 0; i < 120; i++) { const z = rnd() * 100, side = rnd() < 0.5 ? -1 : 1; trees.push([pathX(z) + side * (2.2 + rnd() * 14), z, 3 + rnd() * 5]); }
  trees.map(([x, z, h]) => [x, z + Math.floor((cz - z + 2) / 100 + 1) * 100 * ((z < cz - 1) ? 1 : 0), h]).filter(([x, z]) => z > cz + 1 && z < cz + 100)
    .sort((a, b) => b[1] - a[1]).forEach(([x, z, h]) => {
      const y0 = pathY(z) - 0.3, fog = clamp((z - cz) / 80), col = mix('#26233d', '#8a6f99', fog * 0.8), hi = mix('#4a3f5f', '#a688a8', fog);
      const b0 = cam.p([x, y0, z]), tp = cam.p([x, y0 + h, z]), w = cam.px(h * 0.28, [x, y0, z]);
      for (let k = 0; k < 3; k++) { const yy = b0[1] + (tp[1] - b0[1]) * (0.25 + k * 0.25), ww = w * (1 - k * 0.25);
        s += `<path d="M${f1(b0[0] - ww)} ${f1(yy + (b0[1] - tp[1]) * 0.25)} L${f1(tp[0])} ${f1(yy - (b0[1] - tp[1]) * 0.35)} L${f1(b0[0] + ww)} ${f1(yy + (b0[1] - tp[1]) * 0.25)}Z" fill="${col}"/>
        <path d="M${f1(tp[0])} ${f1(yy - (b0[1] - tp[1]) * 0.35)} L${f1(b0[0] + ww)} ${f1(yy + (b0[1] - tp[1]) * 0.25)} L${f1(b0[0] + ww * 0.4)} ${f1(yy + (b0[1] - tp[1]) * 0.25)}Z" fill="${hi}" opacity=".6"/>`; }
    });
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -0.8 + 0.4 * Math.sin(ph), sway: 4 * Math.sin(ph / 2), scale: 1.04 });
}
