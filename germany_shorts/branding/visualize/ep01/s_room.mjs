import { Cam, wrap, box, quad, mix, f1, clamp, seed, rnd } from './eng.mjs';
// Living room POV from the couch. mode 'night' (TV, junk food, feet up) | 'morning' (TV off, sunlight, shoes, bottle)
export function room(t, { mode = 'night', push = 0 } = {}) {
  const N = mode === 'night';
  const cam = new Cam({ x: 0.02 * Math.sin(t * 0.4), y: 1.08 + 0.004 * Math.sin(t * 1.1), z: 0 + push * t, pitch: -0.13, yaw: 0.03 * Math.sin(t * 0.25), f: 1000 });
  const fl = N ? 0.85 + 0.15 * (Math.sin(t * 7.1) * 0.5 + Math.sin(t * 2.3) * 0.5) : 1;
  const P = N ? { wall: '#20253a', wall2: '#1b2032', floor: '#232839', line: '#1c2030', ceil: '#171b2a', cab: '#121521', table: '#2c3247', tableS: '#1f2435' }
    : { wall: '#d8c3b4', wall2: '#cbb3a3', floor: '#b99c88', line: '#a88b78', ceil: '#e6d6ca', cab: '#5b4a52', table: '#efe3d8', tableS: '#cdbdb1' };
  let s = `<rect width="1920" height="1080" fill="${P.wall}"/>`;
  const Z = 4.0, XL = -2.3, XR = 2.5, YC = 2.6;
  s += cam.poly([[XL, YC, -1], [XR, YC, -1], [XR, YC, Z], [XL, YC, Z]], P.ceil);
  s += cam.poly([[XL, 0, Z], [XR, 0, Z], [XR, YC, Z], [XL, YC, Z]], P.wall);
  s += cam.poly([[XL, 0, -1], [XL, 0, Z], [XL, YC, Z], [XL, YC, -1]], P.wall2);
  s += cam.poly([[XR, 0, -1], [XR, 0, Z], [XR, YC, Z], [XR, YC, -1]], P.wall2);
  s += cam.poly([[XL, 0, -1], [XR, 0, -1], [XR, 0, Z], [XL, 0, Z]], P.floor);
  for (let x = XL; x < XR; x += 0.22) s += cam.line([x, 0, 0.3], [x, 0, Z], P.line, 2);
  // window on right wall
  const wz0 = 1.2, wz1 = 2.6, wy0 = 0.95, wy1 = 2.1;
  s += cam.poly([[XR - 0.01, wy0, wz0], [XR - 0.01, wy0, wz1], [XR - 0.01, wy1, wz1], [XR - 0.01, wy1, wz0]], N ? '#2d2f55' : '#ffe9c8');
  if (N) for (let i = 0; i < 6; i++) s += cam.disc([XR - 0.02, 1.2 + (i % 3) * 0.25, 1.4 + i * 0.2], 0.02, '#ffd9a0', 'opacity=".6"');
  for (let y = wy0 + 0.08; y < wy1; y += 0.09) s += cam.line([XR - 0.02, y, wz0], [XR - 0.02, y, wz1], N ? '#1a1d34' : '#e9cfae', 3);
  if (!N) { // sunbeam on floor
    s += cam.poly([[XR, 0.001, wz0], [XR, 0.001, wz1], [0.3, 0.001, wz1 + 0.6], [0.6, 0.001, wz0 + 0.4]], '#fff4dc', 'opacity=".45"');
    s += cam.poly([[XR - 0.01, wy0, wz0], [XR - 0.01, wy1, wz0], [-0.6, 1.4, Z], [0.2, 0.2, Z]], '#fff4dc', 'opacity=".10"');
  }
  // TV glow on wall + floor
  if (N) { const [gx, gy] = cam.p([0, 1.05, Z]);
    s += `<ellipse cx="${f1(gx)}" cy="${f1(gy)}" rx="700" ry="420" fill="url(#glowB)" opacity="${(0.55 * fl).toFixed(2)}" filter="url(#b30)"/>`; }
  // cabinet + TV
  s += box(cam, [-1.0, 0, 3.55], [1.0, 0.45, 3.95], { top: N ? '#1d2133' : '#7a6870', front: P.cab, side: P.cab });
  s += cam.poly([[-0.8, 0.6, 3.9], [0.8, 0.6, 3.9], [0.8, 1.5, 3.9], [-0.8, 1.5, 3.9]], '#0a0b12');
  const scr = [[-0.76, 0.64, 3.89], [0.76, 0.64, 3.89], [0.76, 1.46, 3.89], [-0.76, 1.46, 3.89]];
  if (N) {
    s += cam.poly(scr, mix('#5d7ad0', '#9fc0ff', 0.5 + 0.5 * Math.sin(t * 1.7)));
    // abstract show on screen: a person-less talk set: desk + moving light bars
    const sp = (u, v) => [-0.76 + 1.52 * u, 0.64 + 0.82 * v, 3.885];
    s += cam.poly([sp(0, 0), sp(1, 0), sp(1, 0.35), sp(0, 0.35)], '#3b4f9a');
    s += cam.poly([sp(0.3, 0.35), sp(0.7, 0.35), sp(0.66, 0.5), sp(0.34, 0.5)], '#2b3a78');
    for (let k = 0; k < 4; k++) { const u = (k * 0.27 + t * 0.07) % 1; s += cam.poly([sp(u, 0.55), sp(u + 0.06, 0.55), sp(u + 0.06, 0.95), sp(u, 0.95)], '#cfe0ff', 'opacity=".35"'); }
    const [sx, sy] = cam.p([0, 1.05, 3.88]);
    s += `<rect x="${f1(sx - 260)}" y="${f1(sy - 160)}" width="520" height="320" fill="#cfe0ff" opacity="${(0.08 * fl).toFixed(2)}"/>`;
  } else {
    s += cam.poly(scr, '#14151d');
    s += cam.poly([[-0.76, 1.46, 3.885], [-0.2, 1.46, 3.885], [-0.76, 0.9, 3.885]], '#ffffff', 'opacity=".06"');
  }
  // plant left (morning) / lamp off
  if (!N) { s += box(cam, [-1.9, 0, 3.2], [-1.6, 0.35, 3.5], { top: '#c98f6b', front: '#b77c5b', side: '#a96f50' });
    seed(4); for (let i = 0; i < 7; i++) s += cam.disc([-1.75 + (rnd() - 0.5) * 0.3, 0.55 + rnd() * 0.45, 3.35], 0.13, i % 2 ? '#6f8f6a' : '#5d7c5a'); }
  // coffee table
  const T0 = 1.25, T1 = 1.95, TY = 0.42;
  s += box(cam, [-0.6, 0.38, T0], [0.6, TY, T1], { top: P.table, front: P.tableS, side: P.tableS });
  for (const [lx, lz] of [[-0.55, T0 + 0.05], [0.55, T0 + 0.05]]) s += box(cam, [lx - 0.025, 0, lz], [lx + 0.025, 0.38, lz + 0.05], { front: P.tableS, side: P.tableS });
  if (N) {
    // pizza box (open lid leaning back)
    s += box(cam, [0.05, TY, 1.55], [0.45, TY + 0.04, 1.92], { top: '#c79a6a', front: '#a87d52', side: '#b58a5e' });
    s += cam.poly([[0.07, TY + 0.045, 1.6], [0.43, TY + 0.045, 1.6], [0.43, TY + 0.045, 1.88], [0.07, TY + 0.045, 1.88]], '#d9b07c');
    for (let i = 0; i < 3; i++) s += cam.poly([[0.12 + i * 0.1, TY + 0.046, 1.66], [0.2 + i * 0.1, TY + 0.046, 1.7], [0.13 + i * 0.1, TY + 0.046, 1.8]], '#c4583f', 'opacity=".8"');
    // cans
    const can = (x, z, lying) => {
      if (lying) { s += box(cam, [x - 0.06, TY, z - 0.03], [x + 0.06, TY + 0.065, z + 0.03], { top: '#b8433d', front: '#8f3330', side: '#c9cdd6' }); return; }
      const [a, b] = cam.p([x, TY, z]), [, c] = cam.p([x, TY + 0.12, z]); const r = cam.px(0.033, [x, TY, z]);
      s += `<rect x="${f1(a - r)}" y="${f1(c)}" width="${f1(2 * r)}" height="${f1(b - c)}" fill="#b8433d"/><rect x="${f1(a - r)}" y="${f1(c)}" width="${f1(r * 0.6)}" height="${f1(b - c)}" fill="#d55a51" opacity=".7"/>
      <ellipse cx="${f1(a)}" cy="${f1(c)}" rx="${f1(r)}" ry="${f1(r * 0.35)}" fill="#c9cdd6"/><ellipse cx="${f1(a)}" cy="${f1(b)}" rx="${f1(r)}" ry="${f1(r * 0.35)}" fill="#8f3330"/>`;
    };
    can(-0.38, 1.75); can(-0.25, 1.85); can(-0.45, 1.5, true); can(0.5, 1.4);
    // chips bag
    s += cam.poly([[-0.2, TY + 0.005, 1.35], [0.0, TY + 0.005, 1.33], [0.02, TY + 0.03, 1.52], [-0.22, TY + 0.03, 1.55]], '#e3b341');
  } else {
    // water bottle + phone face down
    const [a, b] = cam.p([-0.2, TY, 1.6]), [, c] = cam.p([-0.2, TY + 0.24, 1.6]); const r = cam.px(0.035, [-0.2, TY, 1.6]);
    s += `<rect x="${f1(a - r)}" y="${f1(c)}" width="${f1(2 * r)}" height="${f1(b - c)}" rx="${f1(r * 0.5)}" fill="#8ec5d6" opacity=".85"/><rect x="${f1(a - r * 0.6)}" y="${f1(c - r * 0.6)}" width="${f1(r * 1.2)}" height="${f1(r * 0.8)}" fill="#2e3a4a"/>`;
    s += box(cam, [0.15, TY, 1.5], [0.23, TY + 0.01, 1.66], { top: '#22252f', front: '#1a1c24', side: '#1a1c24' });
    // running shoes on the floor by the table
    for (const [sx0, sz] of [[0.75, 1.1], [0.95, 1.18]]) {
      s += box(cam, [sx0, 0, sz], [sx0 + 0.11, 0.04, sz + 0.28], { top: '#f2f2f2', front: '#e6e6e6', side: '#dcdcdc' });
      s += box(cam, [sx0 + 0.01, 0.04, sz + 0.02], [sx0 + 0.1, 0.1, sz + 0.2], { top: '#ff8a5b', front: '#f07a4c', side: '#e86f42' });
    }
  }
  // feet up on the table (night): legs from the bottom of the frame
  if (N) {
    for (const sg of [-1, 1]) {
      const x = sg * 0.15;
      const leg = [[x - 0.085, 0.62, 0.15], [x + 0.085, 0.62, 0.15], [x + 0.055, TY + 0.08, 1.4], [x - 0.055, TY + 0.08, 1.4]];
      s += cam.poly(leg, '#3a4057');
      s += cam.poly([leg[0], [x - 0.01, 0.63, 0.15], [x - 0.005, TY + 0.085, 1.4], leg[3]], '#454c66', 'opacity=".8"');
      // sock: heel on the table, toes up, splayed outward
      const fx = x + sg * 0.01, hz = 1.45, top = TY + 0.17, sp = sg * 0.035;
      s += cam.poly([[fx - 0.045, TY + 0.0, hz - 0.05], [fx + 0.045, TY + 0.0, hz - 0.05], [fx + 0.052 + sp, top, hz + 0.03], [fx - 0.052 + sp, top, hz + 0.03]], '#2e3344');
      s += cam.disc([fx + sp, top, hz + 0.03], 0.052, '#2e3344');
      s += cam.disc([fx + sp - sg * 0.018, top + 0.012, hz + 0.02], 0.026, '#3c4257');
      s += cam.poly([[fx - 0.05, TY + 0.0, hz - 0.07], [fx + 0.05, TY + 0.0, hz - 0.07], [fx + 0.05, TY + 0.05, hz - 0.06], [fx - 0.05, TY + 0.05, hz - 0.06]], '#454b62');
    }
    // couch armrests framing the view
    s += box(cam, [-1.2, 0.0, -0.4], [-0.66, 0.66, 0.95], { top: '#2b3044', front: '#22273a', side: '#262b3f', side2: '#30364b' });
    s += box(cam, [0.66, 0.0, -0.4], [1.2, 0.66, 0.95], { top: '#2b3044', front: '#22273a', side: '#30364b', side2: '#262b3f' });
    // t-shirt / belly at the bottom
    s += `<ellipse cx="960" cy="1290" rx="1150" ry="330" fill="#262b3d"/><ellipse cx="900" cy="1310" rx="1000" ry="320" fill="#2f354b" opacity=".7"/>`;
  }
  s += `<rect width="1920" height="1080" fill="url(#vig)"/>`;
  return wrap(s, { roll: -0.8, scale: 1.03 });
}
