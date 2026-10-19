import { Cam, wrap, box, quad, mix, f1, clamp, smooth, hudText } from './eng.mjs';
// POV looking down at a bathroom scale. opts: kg (string), belly 0..1, warm 0..1 (night cold → morning warm)
export function scale(t, { kg = '100.0', belly = 1, warm = 0, look = 0 } = {}) {
  const bob = 0.004 * Math.sin(t * 1.3);
  const cam = new Cam({ x: 0.01 * Math.sin(t * 0.7), y: 1.62 + bob, z: -0.02, pitch: -1.38 + look, f: 1900 });
  const C = (cold, wm) => mix(cold, wm, warm);
  let s = `<rect width="1920" height="1080" fill="${C('#8d93a8', '#d9c3b0')}"/>`;
  // wall at the back
  s += cam.poly([[-3, 0, 0.95], [3, 0, 0.95], [3, 2.6, 0.95], [-3, 2.6, 0.95]], C('#6f7590', '#c9a998'));
  s += cam.poly([[-3, 0, 0.95], [3, 0, 0.95], [3, 0.1, 0.95], [-3, 0.1, 0.95]], C('#5b6079', '#b08f80'));
  // floor + tile grout
  s += cam.poly([[-3, 0, -1], [3, 0, -1], [3, 0, 0.95], [-3, 0, 0.95]], C('#b7bccb', '#ecdccb'));
  const T = 0.3;
  for (let x = -3; x <= 3; x += T) s += cam.line([x, 0, -1], [x, 0, 0.95], C('#9ea3b5', '#d6c2b0'), 2.2);
  for (let z = -0.9; z <= 0.95; z += T) s += cam.line([-3, 0, z], [3, 0, z], C('#9ea3b5', '#d6c2b0'), 2.2);
  // overhead light pool
  const [lx, ly] = cam.p([0.15, 0, 0.35]);
  s += `<ellipse cx="${f1(lx)}" cy="${f1(ly)}" rx="900" ry="520" fill="${warm > 0.5 ? '#fff4e2' : '#eef3ff'}" opacity=".28" filter="url(#b30)"/>`;
  // bath mat
  s += cam.poly(quad([-0.85, 0.004, -0.2], [0.42, 0, 0], [0, 0, 0.62]), C('#7d8aa8', '#e8b9a4'));
  for (let i = 1; i < 7; i++) s += cam.line([-0.85 + i * 0.06, 0.006, -0.17], [-0.85 + i * 0.06, 0.006, 0.39], C('#71809f', '#dcab96'), 2);
  // scale
  const S0 = [-0.17, 0, -0.05], S1 = [0.17, 0.03, 0.35];
  // soft shadow
  s += cam.poly(quad([-0.18, 0.001, -0.06], [0.37, 0, 0], [0, 0, 0.42]), '#3a3f55', 'opacity=".25" filter="url(#b4)"');
  s += box(cam, S0, S1, { top: '#20232f', front: '#14161e', side: '#181a24' });
  // glass rim highlight
  s += cam.line([-0.165, 0.031, 0.345], [0.165, 0.031, 0.345], '#5d6380', 2.5);
  s += cam.line([0.165, 0.031, -0.045], [0.165, 0.031, 0.345], '#454a62', 2);
  // display window
  const dz = 0.305;
  s += cam.poly(quad([-0.075, 0.031, dz - 0.03], [0.15, 0, 0], [0, 0, 0.058]), '#0b0c12');
  const [tx, ty] = cam.p([0, 0.031, dz]);
  const [, ty2] = cam.p([0, 0.031, dz + 0.04]); const [tx3] = cam.p([0.04, 0.031, dz]);
  const sx = (tx3 - tx) / 0.04, sy = (ty - ty2) / 0.04, fs = 0.036 * sx;
  const sq = (sy / sx).toFixed(3);
  s += `<g transform="translate(${f1(tx)} ${f1(ty)}) scale(1 ${sq})">
   <text x="${f1(-0.004 * sx)}" y="${f1(fs * 0.5)}" font-family="Seg" font-size="${f1(fs)}" text-anchor="middle" fill="#1a2a2e">888.8</text>
   <text x="${f1(-0.004 * sx)}" y="${f1(fs * 0.5)}" font-family="Seg" font-size="${f1(fs)}" text-anchor="middle" fill="#bdf3ff">${kg}</text>
   <text x="${f1(0.06 * sx)}" y="${f1(fs * 0.5)}" font-family="Inter" font-size="${f1(fs * 0.36)}" text-anchor="middle" fill="#bdf3ff">kg</text></g>`;
  s += `<circle cx="${f1(tx)}" cy="${f1(ty)}" r="${f1(fs * 2.2)}" fill="#bdf3ff" opacity=".10" filter="url(#b12)"/>`;
  // feet in socks (top view): heel at back, toes forward
  const circ = (cx, cz, r, y, n = 22) => Array.from({ length: n }, (_, i) => [cx + r * Math.cos(2 * Math.PI * i / n), y, cz + r * Math.sin(2 * Math.PI * i / n)]);
  for (const sg of [-1, 1]) {
    const hx = sg * 0.07, y = 0.034, col = C('#2c3142', '#3a3550'), hi = C('#3d4459', '#514a6e');
    const heel = [hx, 0.03], ball = [hx + sg * 0.008, 0.17], toe = [hx - sg * 0.004, 0.215];
    s += cam.poly([[heel[0] - 0.031, y, heel[1]], [heel[0] + 0.031, y, heel[1]], [ball[0] + 0.045, y, ball[1]], [ball[0] - 0.045, y, ball[1]]], col);
    s += cam.poly(circ(heel[0], heel[1], 0.032, y), col);
    s += cam.poly(circ(ball[0], ball[1], 0.046, y), col);
    s += cam.poly(circ(toe[0], toe[1], 0.036, y), col);
    s += cam.poly(circ(toe[0] - sg * 0.016, toe[1] + 0.006, 0.026, y + 0.001), hi, 'opacity=".55"');
    s += cam.poly(circ(ball[0] - sg * 0.01, ball[1] - 0.02, 0.03, y + 0.001), hi, 'opacity=".35"');
  }
  // belly / t-shirt at the bottom of the frame (screen space)
  if (belly > 0.01) {
    const top = 1080 - 480 * belly, rx = 980 + 200 * belly;
    s += `<g><ellipse cx="960" cy="${f1(top + 560)}" rx="${f1(rx)}" ry="560" fill="${C('#262b3d', '#3a3550')}"/>
     <ellipse cx="900" cy="${f1(top + 590)}" rx="${f1(rx * 0.86)}" ry="545" fill="${C('#30364c', '#4a4362')}"/>
     <ellipse cx="960" cy="${f1(top + 610)}" rx="${f1(rx * 0.97)}" ry="540" fill="${C('#262b3d', '#3a3550')}"/>
     <path d="M620 ${f1(top + 120)} Q760 ${f1(top + 60)} 900 ${f1(top + 95)}" stroke="#1d2131" stroke-width="5" fill="none" opacity=".7"/>
     <path d="M1150 ${f1(top + 110)} Q1290 ${f1(top + 70)} 1400 ${f1(top + 130)}" stroke="#1d2131" stroke-width="4" fill="none" opacity=".6"/></g>`;
  } else {
    // shirt hem barely at the bottom edge
    s += `<ellipse cx="960" cy="1330" rx="1100" ry="300" fill="${C('#262b3d', '#3a3550')}"/>`;
  }
  return wrap(s + `<rect width="1920" height="1080" fill="url(#vig)"/>`, { roll: -1.2 + 0.4 * Math.sin(t * 0.9), scale: 1.03 });
}
