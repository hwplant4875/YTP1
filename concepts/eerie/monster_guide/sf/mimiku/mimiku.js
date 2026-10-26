/* =====================================================================================================================
 * mimiku.js : window.MIMIKU, the parametric rig for Mimiku (treasure-chest mimic, Monster HR new hire #001).
 * Needs lib_core.js (window.SFX) loaded first. Plain canvas 2D, deterministic (no Math.random).
 *
 * Design (plan_v1 4-2, brief SF2). W = chest width. The rig works in W units; 1 W = 200 px at scale 1.
 *   chest: base 0.40 W high, depth 0.60 W, lid 0.20 W + 0.05 W barrel dome, lid overhang 0.03 W, walls 0.05 W.
 *   The chest is a real (orthographic) box: yaw turns it (0 front, 35 three-quarter, 90 side), the camera looks down
 *   8 degrees, the lid hinges at the back edge. Mouth = everything between the base rim and the lid's inner rim.
 *   eyes 0.26 W wide at +-0.17 W, 53 % down the opening; < 35 deg lid shows two glints instead.
 *   arms: upper 0.55 W, forearm 0.95 W (long), from the mouth corners; elbows rise above the lid (2-bone IK).
 *   legs: thigh 0.72 W + shin 0.70 W, bony capsules with knee knobs and joint dots (2-bone IK, knees out).
 *   teeth: 13 upper / 12 lower rounded pegs, alternating long/short; flat tongue with a centre groove.
 *   chain: 10 links from an iron hasp on the right side, sticking STRAIGHT FORWARD (the tell).
 *
 * API
 *   MIMIKU.draw(ctx, p)       draws the whole character as ONE shadow group. p (all optional except x, y):
 *     x, y            ground point in canvas px (centre between the feet / under the chest)
 *     scale=1         1 = W 200 px
 *     pose='stand'    preset: 'dormant' | 'peek' | 'stand' | 'crouch' | 'pounce' | 'yawn' | 'rest' (turnaround)
 *     expr            'default' | 'nervous' | 'greedy' | 'happy' | 'creepy' | 'dizzy' | 'sleep' | 'yawn' | 'hunt'
 *     yaw=0           degrees, 0 front, 35 three-quarter, 90 side (shows the right side, faces screen-left)
 *     lid             lid angle in degrees (0 shut .. 90 yawn)
 *     tilt            body roll in degrees (+ clockwise)
 *     hip=[x, h]      hip (chest bottom centre) offset in W: x right, h = height above the ground
 *     sit=false       true: chest rests on the floor (hip height solved so the lowest corner touches y = 0)
 *     legs            { L: { foot: [x, y], bend: 1 }, R: { foot: [x, y], bend: -1 } }  foot = ankle target in W,
 *                     world space relative to the ground point (y up is negative). null = legs folded away.
 *     arms            { L: { wrist: [x, y], bend, hand, handAng, handBend, spread, curl, z }, R: {...} } wrist in W,
 *                     bend +-1 picks the elbow side, hand = 'hang' | 'open' | 'wave' | 'grab' | 'tap' | 'limp',
 *                     handAng = absolute hand direction (deg, 0 = right, 90 = down), handBend = relative to the
 *                     forearm, z = 'front' (default) | 'back'. null = arm hidden.
 *     tongue          { len, pitch: [deg...], lat: [deg...], width, floor, floorDir }  pitch 0 = forward, 90 = down,
 *                     180 = back; lat = sideways. Keys are spread along the part outside the mouth. null = no tongue.
 *     chain           { mode: 'forward' | 'trail', links=10, droop: [deg, deg], sway, t }
 *     look {x, y}     gaze -1..1    blink 0..1 (1 open)    eyeAt 0.53 (eye centre, fraction down the opening)
 *     fx              { sweat, drool, sparkle, zzz, tear, wave, speed, tap } booleans (expr presets switch some on)
 *     parts           { legs, arms, chain, tongue, fx } false = skip (close-ups)
 *     shadow=true     group drop shadow (down-right)        t = time (s) for secondary motion
 *     skip            debug only: array of paint-pass names to leave out ('ring', 'lidRing', 'lidTop', 'lidSide',
 *                     'lidFront', 'clasp'); used to bisect drawing bugs, leave unset in production.
 *   MIMIKU.solve(p) -> { hip, eyes: [[x,y],[x,y]], mouth: [x,y], lidTop: y, bounds } in canvas px (for layouts)
 *   MIMIKU.drawHand(ctx, x, y, angDeg, type, side, size)      one mitten hand (callouts)
 *   MIMIKU.drawTooth(ctx, x, y, len, w, down)                 one peg tooth (callouts)
 *   MIMIKU.drawClasp(ctx, x, y, size)                         the brass heart clasp (callouts)
 *   MIMIKU.drawChain(ctx, pts, sizes)                         links with per-link size (callouts)
 *   MIMIKU.POSES, MIMIKU.EXPR, MIMIKU.COL, MIMIKU.DIM
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX;
  if (!S) throw new Error('mimiku.js needs lib_core.js (window.SFX) loaded first');
  const C = S.color, TAU = Math.PI * 2, RAD = Math.PI / 180;
  const clamp = S.clamp, lerp = S.lerp, sstep = S.smoothstep;
  const { normalsOf, arcU } = S._poly;

  const COL = {
    wood: '#A0866B', woodShade: '#7A6652', woodRim: '#C2A98E', seam: '#7A6652', seamSide: '#64533F',
    iron: '#4B5160', ironShade: '#3A3F4C', rivet: '#8A91A0',
    brass: '#D9A93F', brassShade: '#AE8226', brassLight: '#F3D27A', keyhole: '#3A2310',
    limb: '#D8CCE0', limbShade: '#A8979C', claw: '#EFE4D6', clawShade: '#C9BBA8', joint: '#A8979C',
    tooth: '#F3E9D2', toothShade: '#CDBF9F',
    mouth: '#3A0F1E', mouthShade: '#2A0914', gum: '#6E1D33',
    tongue: '#E2566E', tongueShade: '#C4455E', groove: '#B23A52',
    glint: '#FFC83D', ink: '#140a0e', brow: '#F3E9D2', blush: '#FF7F98',
    sweat: '#a9dcff', drool: '#d9efff', droolShade: '#a9cfe9',
  };
  const DIM = {
    U: 200, hb: 0.40, dep: 0.60, T: 0.20, dome: 0.05, o: 0.03, tw: 0.045, elev: 8, lift: 0.8,
    eyeW: 0.26, eyeX: 0.17, upper: 0.55, fore: 0.95, thigh: 0.72, shin: 0.70, hipX: 0.19,
    armW: [0.1, 0.084, 0.064], legW: [0.098, 0.076, 0.072, 0.056],
  };

  // ------------------------------------------------------------------ small math
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, k) => [a[0] * k, a[1] * k];
  const rot2 = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
  const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const dir2 = a => [Math.cos(a), Math.sin(a)];
  function crArr(arr, u) { // Catmull-Rom through evenly spaced scalar keys
    if (!Array.isArray(arr)) return arr || 0;
    const n = arr.length - 1; if (n < 1) return arr[0];
    const f = clamp(u) * n, i = Math.min(n - 1, Math.floor(f)), t = f - i;
    const p0 = arr[Math.max(0, i - 1)], p1 = arr[i], p2 = arr[i + 1], p3 = arr[Math.min(n, i + 2)];
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t);
  }
  function hull(pts) {
    const P = pts.map(p => p.slice()).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const p of P) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 1e-9) lo.pop(); lo.push(p); }
    for (let i = P.length - 1; i >= 0; i--) { const p = P[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 1e-9) up.pop(); up.push(p); }
    up.pop(); lo.pop();
    return lo.concat(up);
  }
  function ik(A, T, l1, l2, bend) {
    const dx = T[0] - A[0], dy = T[1] - A[1], d0 = Math.hypot(dx, dy);
    const d = clamp(d0, Math.abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3);
    const a0 = Math.atan2(dy, dx), ca = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d);
    const a = a0 + bend * Math.acos(clamp(ca, -1, 1));
    const J = [A[0] + Math.cos(a) * l1, A[1] + Math.sin(a) * l1];
    const a2 = Math.atan2(T[1] - J[1], T[0] - J[0]);
    return { J, E: [J[0] + Math.cos(a2) * l2, J[1] + Math.sin(a2) * l2], a1: a, a2 };
  }

  // ------------------------------------------------------------------ paint helpers (union-safe cel shading)
  let LS = 1; // light sign (flips the shade offsets when the rig is mirrored, so light stays top-left)
  function cel(g, pathFn, base, shade, dx, dy, rim, rx, ry) {
    g.save();
    g.beginPath(); pathFn(g); g.clip();
    g.fillStyle = shade || base; g.fillRect(-50, -50, 100, 100);
    if (rim) {
      g.save(); g.translate(-dx * LS, -dy); g.beginPath(); pathFn(g); g.restore(); g.clip();
      g.fillStyle = rim; g.fillRect(-50, -50, 100, 100);
      g.translate(rx * LS, ry); g.beginPath(); pathFn(g); g.fillStyle = base; g.fill();
    } else {
      g.translate(-dx * LS, -dy); g.beginPath(); pathFn(g); g.fillStyle = base; g.fill();
    }
    g.restore();
  }
  const clipIn = (g, pathFn, fn) => { g.save(); g.beginPath(); pathFn(g); g.clip(); fn(g); g.restore(); };
  function pillow(c, x0, y0, x1, y1, r, bow) { // rounded rect with gently bowed edges; r = [tl,tr,br,bl], bow = [t,r,b,l]
    const k = 0.5523, [tl, tr, br, bl] = r, [bt, brr, bb, bll] = bow || [0, 0, 0, 0];
    c.moveTo(x0 + tl, y0);
    c.quadraticCurveTo((x0 + x1) / 2, y0 - bt * 2, x1 - tr, y0);
    c.bezierCurveTo(x1 - tr + tr * k, y0, x1, y0 + tr - tr * k, x1, y0 + tr);
    c.quadraticCurveTo(x1 + brr * 2, (y0 + y1) / 2, x1, y1 - br);
    c.bezierCurveTo(x1, y1 - br + br * k, x1 - br + br * k, y1, x1 - br, y1);
    c.quadraticCurveTo((x0 + x1) / 2, y1 + bb * 2, x0 + bl, y1);
    c.bezierCurveTo(x0 + bl - bl * k, y1, x0, y1 - bl + bl * k, x0, y1 - bl);
    c.quadraticCurveTo(x0 - bll * 2, (y0 + y1) / 2, x0, y0 + tl);
    c.bezierCurveTo(x0, y0 + tl - tl * k, x0 + tl - tl * k, y0, x0 + tl, y0);
    c.closePath();
  }
  function roundPolyAdd(c, P, r) { // robust rounded polygon: near-straight corners are skipped (arcTo overshoots there)
    const n = P.length; if (n < 3) return;
    const pts = [];
    for (let i = 0; i < n; i++) {
      const a = P[(i - 1 + n) % n], b = P[i], d = P[(i + 1) % n];
      const ux = b[0] - a[0], uy = b[1] - a[1], vx = d[0] - b[0], vy = d[1] - b[1];
      const lu = Math.hypot(ux, uy), lv = Math.hypot(vx, vy);
      if (lu < 1e-6 || lv < 1e-6) continue;
      const cr = (ux * vy - uy * vx) / (lu * lv), dt = (ux * vx + uy * vy) / (lu * lv);
      const turn = Math.atan2(Math.abs(cr), dt); // 0 = straight
      if (turn < 0.06) continue;
      const t = Math.min(r * Math.tan(turn / 2), lu * 0.48, lv * 0.48);
      pts.push({ A: [b[0] - ux / lu * t, b[1] - uy / lu * t], V: b, B: [b[0] + vx / lv * t, b[1] + vy / lv * t] });
    }
    if (pts.length < 3) { c.moveTo(P[0][0], P[0][1]); for (let i = 1; i < n; i++) c.lineTo(P[i][0], P[i][1]); c.closePath(); return; }
    c.moveTo(pts[0].A[0], pts[0].A[1]);
    for (let i = 0; i < pts.length; i++) { const q = pts[i]; c.lineTo(q.A[0], q.A[1]); c.quadraticCurveTo(q.V[0], q.V[1], q.B[0], q.B[1]); }
    c.closePath();
  }
  function ribbonAdd(c, P, half) { // closed ribbon around a polyline; half = fn(u, i) half-width
    const N = normalsOf(P), U = arcU(P), n = P.length;
    for (let i = 0; i < n; i++) { const h = half(U[i], i); const X = P[i][0] + N[i][0] * h, Y = P[i][1] + N[i][1] * h; i ? c.lineTo(X, Y) : c.moveTo(X, Y); }
    for (let i = n - 1; i >= 0; i--) { const h = half(U[i], i); c.lineTo(P[i][0] - N[i][0] * h, P[i][1] - N[i][1] * h); }
    c.closePath();
  }
  function smoothPts(P, it = 2) { // Chaikin, keeps the ends
    let Q = P;
    for (let k = 0; k < it; k++) {
      const R = [Q[0]];
      for (let i = 0; i < Q.length - 1; i++) { const a = Q[i], b = Q[i + 1]; R.push([a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25], [a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75]); }
      R.push(Q[Q.length - 1]); Q = R;
    }
    return Q;
  }

  // ------------------------------------------------------------------ view / projection
  function makeView(p) {
    const ps = (p.yaw || 0) * RAD, th = clamp(p.lid ?? 0, 0, 115) * RAD, e = (p.elev ?? DIM.elev) * RAD;
    const v = { cp: Math.cos(ps), sp: Math.sin(ps), ce: Math.cos(e), se: Math.sin(e), ct: Math.cos(th), st: Math.sin(th), lid: p.lid ?? 0 };
    v.cam = [v.sp * v.ce, v.se, v.cp * v.ce];
    const h = DIM.dep / 2;
    v.P = (x, y, z) => { const zc = z + h; return [x * v.cp - zc * v.sp, -y * v.ce + (x * v.sp + zc * v.cp) * v.se]; };
    v.Pl = (x, y, z) => [x * v.cp - z * v.sp, -y * v.ce + (x * v.sp + z * v.cp) * v.se]; // linear part (vectors)
    const kL = DIM.lift; // 2D cheat: the lid lifts less than a rigid 0.6 W lid would, so the eyes own the opening
    v.L = (x, y, z) => { const ry = y - DIM.hb, rz = z + DIM.dep; return [x, DIM.hb + ry * v.ct + rz * v.st * kL, -DIM.dep - ry * v.st + rz * v.ct]; };
    v.Lv = (x, y, z) => [x, y * v.ct + z * v.st * kL, -y * v.st + z * v.ct];
    v.PL = (x, y, z) => v.P(...v.L(x, y, z));
    v.vis = n => dot3(n, v.cam);
    return v;
  }
  // run fn with ctx mapped so local (u, w) -> 3D o + u*U + w*V (projected). Returns false if edge-on.
  function inFace(g, v, o, Uv, Vv, fn) {
    const O = v.P(o[0], o[1], o[2]), A = v.Pl(Uv[0], Uv[1], Uv[2]), B = v.Pl(Vv[0], Vv[1], Vv[2]);
    if (Math.abs(A[0] * B[1] - A[1] * B[0]) < 1e-5) return false;
    g.save(); g.transform(A[0], A[1], B[0], B[1], O[0], O[1]); fn(g); g.restore();
    return true;
  }

  // ------------------------------------------------------------------ presets
  const EXPR = {
    default: { eye: { irisScale: 0.66, pupil: 'slit', h: 0.7 }, brow: { tilt: 0.06, arch: 0.2 }, blush: 0.62 },
    nervous: { eye: { irisScale: 0.3, pupil: 'slit', pupilScale: 0.75, h: 0.76, look: { x: 0.35, y: -0.05 } }, brow: { tilt: 0.5, arch: 0.08, dy: -0.012 }, blush: 0.35, fx: { sweat: true } },
    greedy: { eye: { irisScale: 0.74, pupil: 'star', pupilScale: 1.12, h: 0.74, highlight2: true }, brow: { tilt: -0.05, arch: 0.32, dy: -0.016 }, blush: 0.6, fx: { drool: true, sparkle: true } },
    happy: { eye: { closed: 'smile', lashes: 3 }, brow: { tilt: 0.12, arch: 0.32, dy: -0.01 }, blush: 0.7 },
    creepy: { eye: { irisScale: 0.6, pupil: 'slit', pupilScale: 0.75, highlight: false, darkCircle: 1, open: 0.74, lowerRaise: 0.2, h: 0.66 }, brow: { tilt: -0.5, arch: 0.02, dy: 0.012 }, blush: 0, rings: true },
    dizzy: { eye: { pupil: 'swirl', highlight: false, irisScale: 0.74, h: 0.72 }, brow: { tilt: 0.3, arch: 0.15, L: { tilt: 0.55, dy: -0.01 }, R: { tilt: -0.15, dy: 0.008 } }, blush: 0.45, tongue: 'loll' },
    sleep: { eye: { closed: 'sleep', lashes: 3 }, brow: { tilt: 0.12, arch: 0.15, dy: 0.01 }, blush: 0.45, fx: { zzz: true } },
    yawn: { eye: { closed: 'flat', lashes: 3 }, brow: { tilt: 0.35, arch: 0.12 }, blush: 0.45, fx: { zzz: true, tear: true } },
    hunt: { eye: { irisScale: 0.46, pupil: 'slit', pupilScale: 0.85, open: 0.8, lowerRaise: 0.28, h: 0.66, look: { x: 0, y: 0.35 } }, brow: { tilt: -0.3, arch: 0.06 }, blush: 0.25 },
  };
  const TONGUE_LOLL = { len: 0.62, pitch: [20, 75, 95, 85, 60], lat: [0, 12, 30, 45, 55], width: 0.24 };

  const POSES = {
    dormant: { lid: 8, tilt: -6, sit: true, legs: null, arms: null, tongue: null, expr: 'default', chain: { mode: 'forward' } },
    peek: {
      lid: 40, tilt: 3, sit: true, legs: null, expr: 'nervous', tongue: null, chain: { mode: 'forward' },
      arms: { R: null, L: { root: [-0.36, 0.12, 0.0], l1: 0.3, l2: 0.5, wrist: [-0.72, -0.1], bend: 1, hand: 'tap', handAng: 110, z: 'front' } }, fx: { tap: 'L' },
      look: { x: -0.55, y: 0.35 },
    },
    stand: {
      lid: 70, hip: [0, 1.32], legs: { L: { foot: [-0.36, -0.035], bend: 1 }, R: { foot: [0.36, -0.035], bend: -1 } },
      arms: { L: { wrist: [-1.33, -1.84], bend: 1, hand: 'wave', handAng: -118 }, R: { wrist: [1.04, -1.5], bend: -1, hand: 'hang', handBend: 8 } },
      tongue: { len: 0.46, pitch: [25, 80, 95, 70], lat: [0, 4, 10, 16] }, expr: 'happy', fx: { wave: 'L' },
    },
    rest: { // neutral standing pose for the turnaround
      lid: 70, hip: [0, 1.32], legs: { L: { foot: [-0.34, -0.035], bend: 1 }, R: { foot: [0.34, -0.035], bend: -1 } },
      arms: { L: { wrist: [-0.96, -1.52], bend: 1, hand: 'hang', handBend: -8 }, R: { wrist: [0.96, -1.52], bend: -1, hand: 'hang', handBend: 8 } },
      tongue: { len: 0.42, pitch: [25, 85, 92, 80], lat: [0, 0, 4, 8] }, expr: 'default',
    },
    crouch: {
      lid: 45, hip: [0, 0.6], legs: { L: { foot: [-0.98, -0.035], bend: 1 }, R: { foot: [0.98, -0.035], bend: -1 } },
      arms: { L: { wrist: [-1.12, -0.78], bend: 1, hand: 'grab', handBend: -10 }, R: { wrist: [1.12, -0.78], bend: -1, hand: 'grab', handBend: 10 } },
      tongue: { len: 1.0, pitch: [30, 88, 92, 90, 86], lat: [0, 3, -4, 3, 8] }, expr: 'hunt', shoulderK: 0.5,
    },
    pounce: {
      lid: 80, yaw: 30, hip: [0.2, 1.3], tilt: -18,
      legs: { L: { foot: [0.95, -0.9], bend: -1 }, R: { foot: [1.28, -1.2], bend: -1 } },
      arms: { L: { wrist: [-1.55, -1.9], bend: 1, hand: 'grab', handBend: -14 }, R: { wrist: [-1.05, -2.85], bend: 1, hand: 'grab', handBend: -24 } },
      tongue: { len: 1.15, pitch: [30, 70, 120, 160, 172], lat: [0, -14, 8, 26, 12], width: 0.19 },
      chain: { mode: 'trail' }, expr: 'greedy', fx: { speed: true }, airborne: true,
    },
    yawn: {
      lid: 90, hip: [0, 1.3], legs: { L: { foot: [-0.3, -0.035], bend: 1 }, R: { foot: [0.3, -0.035], bend: -1 } },
      arms: { L: { wrist: [-0.8, -3.42], bend: -1, hand: 'open', handBend: -6, spread: 12 }, R: { wrist: [0.74, -1.22], bend: -1, hand: 'limp', handBend: 10 } },
      tongue: { len: 0.95, pitch: [30, 88, 100, 40, -60], lat: [0, 0, 15, 40, 50], width: 0.24 }, expr: 'yawn', tilt: 2,
    },
  };

  const HANDS = {
    hang: { spread: 8, curl: 20, thumb: 52, thumbCurl: 14 },
    open: { spread: 16, curl: 4, thumb: 72, thumbCurl: 0 },
    wave: { spread: 17, curl: -6, thumb: 78, thumbCurl: -4 },
    grab: { spread: 22, curl: 34, thumb: 64, thumbCurl: 26 },
    tap: { spread: 10, curl: 14, thumb: 48, thumbCurl: 14, curls: [-46, 6, 12] },
    limp: { spread: 5, curl: 30, thumb: 40, thumbCurl: 22 },
  };

  // ------------------------------------------------------------------ resolve params
  const isObj = o => o && typeof o === 'object' && !Array.isArray(o);
  function resolve(params) {
    const base = POSES[params.pose || 'stand'] || POSES.stand;
    const p = JSON.parse(JSON.stringify(base));
    for (const k of Object.keys(params)) {
      const val = params[k];
      if ((k === 'arms' || k === 'legs') && isObj(val) && isObj(p[k])) {
        for (const s of ['L', 'R']) if (s in val) p[k][s] = val[s] === null ? null : Object.assign({}, p[k][s] || {}, val[s]);
      } else if ((k === 'tongue' || k === 'chain' || k === 'fx' || k === 'parts') && isObj(val) && isObj(p[k])) p[k] = Object.assign({}, p[k], val);
      else p[k] = val;
    }
    const ex = EXPR[p.expr] || EXPR.default;
    p._ex = ex;
    p.fx = Object.assign({}, ex.fx || {}, p.fx || {});
    if (ex.tongue === 'loll' && params.tongue === undefined) p.tongue = Object.assign({}, TONGUE_LOLL);
    p.parts = Object.assign({ legs: true, arms: true, chain: true, tongue: true, fx: true }, p.parts || {});
    p.scale = p.scale ?? 1;
    return p;
  }

  // ------------------------------------------------------------------ solve: every point the painter needs (world W units, y down)
  function solve(p, v) {
    const hb = DIM.hb, dep = DIM.dep, o = DIM.o, tw = DIM.tw;
    const tilt = (p.tilt || 0) * RAD;
    const hip = [p.hip ? p.hip[0] : 0, p.hip ? -p.hip[1] : 0];
    const R = { v, tilt, hip };
    R.B = q => add(hip, rot2(q, tilt));
    if (p.sit) { // lowest corner of the chest touches the ground
      let maxY = -1e9;
      const rb = 0.1;
      for (const sx of [-1, 1]) for (const z of [0, -dep]) for (let a = 0; a <= 90; a += 10) {
        const q = v.P(sx * (0.5 - rb + rb * Math.sin(a * RAD)), rb - rb * Math.cos(a * RAD), z);
        maxY = Math.max(maxY, rot2(q, tilt)[1]);
      }
      hip[1] = -maxY + (p.sink || 0);
    }
    // mouth geometry (3D)
    const lidFront = v.L(0, hb, o - tw);                     // lid inner front edge (centre)
    R.yTop = lidFront[1]; R.zTop = lidFront[2];
    R.gapK = clamp((R.yTop - hb) / 0.3);                      // 0 shut .. 1 well open
    R.mp = (u, f, d = 0) => v.P(u, lerp(hb, R.yTop, f), lerp(0, R.zTop, f) - d); // point on the mouth plane (body 2D)
    // hull of the mouth: base top inner rim + lid inner face
    const xi = 0.5 - tw, xl = 0.5 + o - tw;
    const H3 = [[-xi, hb, 0], [xi, hb, 0], [-xi, hb, -dep + tw], [xi, hb, -dep + tw],
      v.L(-xl, hb, o - tw), v.L(xl, hb, o - tw), v.L(-xl, hb, -dep + tw), v.L(xl, hb, -dep + tw)];
    R.hull = hull(H3.map(q => v.P(q[0], q[1], q[2])));
    // eyes
    const eyeAt = p.eyeAt ?? 0.53;
    R.eyes = [-1, 1].map(s => R.mp(s * DIM.eyeX, 1 - eyeAt, 0.07));
    // shoulders, hips (body 2D -> world)
    const sk = p.shoulderK ?? 0.56;
    const sx = p.shoulderX ?? 0.5;
    R.shoulder = { L: R.B(R.mp(-sx, sk, 0.06)), R: R.B(R.mp(sx, sk, 0.06)) };
    R.hipJ = { L: R.B(v.P(-DIM.hipX, 0.035, -dep / 2)), R: R.B(v.P(DIM.hipX, 0.035, -dep / 2)) };
    // arms
    R.arms = {};
    if (p.parts.arms && p.arms) for (const s of ['L', 'R']) {
      const a = p.arms[s]; if (!a) continue;
      const Sh = a.root ? R.B(R.mp(a.root[0], a.root[1], a.root[2] || 0)) : R.shoulder[s];
      const k = ik(Sh, a.wrist, DIM.upper * (a.l1 || 1), DIM.fore * (a.l2 || 1), a.bend ?? (s === 'L' ? 1 : -1));
      let hAng = a.handAng !== undefined ? a.handAng * RAD : k.a2 + (a.handBend || 0) * RAD;
      R.arms[s] = { S: Sh, E: k.J, W: k.E, hAng, a, side: s === 'L' ? 1 : -1 };
    }
    // legs
    R.legs = {};
    if (p.parts.legs && p.legs) for (const s of ['L', 'R']) {
      const l = p.legs[s]; if (!l) continue;
      const k = ik(R.hipJ[s], l.foot, DIM.thigh, DIM.shin, l.bend ?? (s === 'L' ? 1 : -1));
      R.legs[s] = { H: R.hipJ[s], K: k.J, A: k.E, l, side: s === 'L' ? -1 : 1 };
    }
    // tongue
    R.tongue = p.parts.tongue && p.tongue && p.tongue.len > 0 ? tongueSpine(p, v, R) : null;
    // hasp / chain anchor
    R.hasp3 = [0.5, hb - 0.12, -0.12];
    R.hasp = R.B(v.P(0.5 + 0.035, hb - 0.12, -0.12));
    R.chain = p.parts.chain && p.chain !== null ? chainPts(p, v, R) : null;
    R.lidTop = R.B(v.PL(0, hb + DIM.T + DIM.dome, -dep / 2));
    return R;
  }

  function tongueSpine(p, v, R) {
    const t = p.tongue, n = 30, L = t.len, s0 = 0.17, seg = L / n;
    let q = [0, DIM.hb + 0.04, -0.15];
    const P3 = [q.slice()];
    const keys = t.pitch || [25, 85, 90];
    for (let i = 0; i < n; i++) {
      const s = (i + 0.5) * seg;
      let ph, la;
      if (s < s0) { ph = lerp(-10, keys[0], sstep(0, 1, s / s0)); la = 0; }
      else {
        const u = (s - s0) / Math.max(1e-3, L - s0);
        ph = crArr(keys, u); la = crArr(t.lat || [0], u);
        if (t.wag) ph += t.wag * Math.sin(TAU * (t.wagF || 0.9) * (p.t || 0) - u * 3.2) * u;
      }
      ph *= RAD; la *= RAD;
      const d = [Math.sin(la), -Math.sin(ph) * Math.cos(la), Math.cos(ph) * Math.cos(la)];
      q = [q[0] + d[0] * seg, q[1] + d[1] * seg, q[2] + d[2] * seg];
      P3.push(q.slice());
    }
    let W = P3.map(q3 => R.B(v.P(q3[0], q3[1], q3[2])));
    if (t.floor) { // pool on the floor: once it touches, the rest lies flat and slides sideways
      const fy = -0.022, dir = t.floorDir || 1;
      let hit = -1;
      for (let i = 1; i < W.length; i++) if (W[i][1] > fy) { hit = i; break; }
      if (hit > 0) {
        const remain = (W.length - 1 - hit) * seg;
        for (let i = hit; i < W.length; i++) {
          const k = (i - hit) / Math.max(1, W.length - 1 - hit);
          W[i] = [W[hit - 1][0] + dir * remain * k * 0.9 + dir * 0.02, fy - 0.035 * Math.sin(Math.PI * k) * (1 - k)];
        }
        W = smoothPts(W, 1);
      }
    }
    return W;
  }

  function chainPts(p, v, R) {
    const c = p.chain || {}, n = c.links ?? 8, L0 = c.size ?? 0.07, pitch = L0 * 0.72;
    const pts = [R.hasp.slice()], sizes = [];
    const front = clamp(1 - Math.abs(p.yaw || 0) / 28); // front view: forward is invisible, so cheat it obliquely
    let q = R.hasp3.slice(); q[0] += 0.035;
    const t = p.t || 0;
    for (let i = 0; i < n; i++) {
      const u = (i + 0.5) / n;
      let d3;
      if (c.mode === 'trail') {
        const ph = lerp(-6, 30, u) * RAD + 0.5 * Math.sin(u * 5.5 - t * 6) * u;
        d3 = [0.18 + 0.1 * Math.sin(u * 4), -Math.sin(ph), -Math.cos(ph)];
      } else {
        const dr = lerp((c.droop || [5, 26])[0], (c.droop || [5, 26])[1], u ** 1.6) * RAD + (c.sway || 0) * Math.sin(TAU * 0.6 * t - u * 2) * u;
        d3 = [0.16, -Math.sin(dr), Math.cos(dr)];
      }
      const l = Math.hypot(d3[0], d3[1], d3[2]);
      q = [q[0] + d3[0] / l * pitch, q[1] + d3[1] / l * pitch, q[2] + d3[2] / l * pitch];
      let P2 = v.P(q[0], q[1], q[2]);
      const zf = q[2] - R.hasp3[2];
      if (c.mode !== 'trail' && front > 0) P2 = [P2[0] + zf * 0.5 * front, P2[1] + zf * 0.42 * front];
      pts.push(R.B(P2));
      const persp = c.mode === 'trail' ? 1 : 1 + 0.55 * clamp(zf / (pitch * n)) * (0.4 + 0.6 * front);
      sizes.push(L0 * persp);
    }
    return { pts, sizes };
  }

  const skip = (p, k) => Array.isArray(p.skip) && p.skip.includes(k);
  // ------------------------------------------------------------------ parts: chest
  function strapsAndRivets(g, xs, y0, y1, w, rivY, colA, colB) {
    for (const x of xs) {
      cel(g, c => c.rect(x - w / 2, y0 - 0.2, w, y1 - y0 + 0.4), colA, colB, 0.016, 0.0);
      for (const ry of rivY) S.circle(g, x - 0.004, ry, 0.0135, COL.rivet);
    }
  }
  function drawBaseFront(g, p) {
    const hb = DIM.hb;
    const path = c => pillow(c, -0.5, 0, 0.5, hb, [0.05, 0.05, 0.12, 0.12], [0, 0.012, 0.014, 0.012]);
    cel(g, path, COL.wood, COL.woodShade, 0.034, 0.036, COL.woodRim, 0.024, 0);
    clipIn(g, path, gg => {
      // plank seams + two butt joints
      gg.fillStyle = COL.seam;
      for (const [y, x0, x1] of [[0.135, -0.5, 0.5], [0.268, -0.5, 0.5]]) gg.fillRect(x0, y - 0.0065, x1 - x0, 0.013);
      gg.fillRect(-0.12, 0.135, 0.012, 0.133); gg.fillRect(0.08, 0.0, 0.012, 0.135); gg.fillRect(0.13, 0.268, 0.012, 0.2);
      strapsAndRivets(gg, [-0.3, 0.3], 0, hb, 0.074, [0.055, 0.2, 0.345], COL.iron, COL.ironShade);
    });
  }
  function drawBaseSide(g, p) {
    const hb = DIM.hb, dep = DIM.dep;
    const path = c => pillow(c, 0, 0, dep, hb, [0.02, 0.05, 0.11, 0.03], [0, 0.01, 0.012, 0]);
    cel(g, path, COL.woodShade, C.shade(COL.woodShade, -0.16), 0.03, 0.03);
    clipIn(g, path, gg => {
      gg.fillStyle = COL.seamSide;
      for (const y of [0.135, 0.268]) gg.fillRect(0, y - 0.006, dep, 0.012);
      strapsAndRivets(gg, [dep * 0.62], 0, hb, 0.07, [0.07, 0.33], C.shade(COL.iron, -0.12), C.shade(COL.ironShade, -0.15));
      // hasp plate
      const hx = 0.12, hy = 0.12;
      cel(gg, c => S.addRoundRect(c, hx - 0.05, hy - 0.06, 0.1, 0.12, 0.022), C.shade(COL.iron, -0.05), COL.ironShade, 0.012, 0.012);
      S.circle(gg, hx - 0.026, hy - 0.035, 0.011, COL.rivet); S.circle(gg, hx + 0.026, hy + 0.035, 0.011, COL.rivet);
    });
  }
  function drawLidFront(g, p) {
    const T = DIM.T, w = 0.5 + DIM.o;
    const path = c => pillow(c, -w, 0, w, T, [0.05, 0.05, 0.03, 0.03], [0.008, 0.01, 0, 0.01]);
    cel(g, path, COL.wood, COL.woodShade, 0.03, 0.032, COL.woodRim, 0.024, 0.0);
    clipIn(g, path, gg => {
      gg.fillStyle = COL.seam; gg.fillRect(-w, T * 0.52 - 0.006, 2 * w, 0.012);
      gg.fillRect(-0.06, 0, 0.012, T * 0.52);
      strapsAndRivets(gg, [-0.3, 0.3], 0, T, 0.074, [0.05, 0.145], COL.iron, COL.ironShade);
      // a darker lip line along the bottom edge (front wall rim)
      gg.fillStyle = C.rgba(COL.woodShade, 0.9); gg.fillRect(-w, T - 0.022, 2 * w, 0.03);
    });
  }
  function drawLidSide(g, p) {
    const T = DIM.T, dd = DIM.dep + DIM.o;
    const path = c => pillow(c, 0, 0, dd, T, [0.07, 0.07, 0.02, 0.02], [DIM.dome, 0, 0, 0]);
    cel(g, path, COL.woodShade, C.shade(COL.woodShade, -0.16), 0.026, 0.026, COL.wood, 0.0, 0.022);
    clipIn(g, path, gg => {
      strapsAndRivets(gg, [dd * 0.6], -0.1, T, 0.07, [0.07], C.shade(COL.iron, -0.12), C.shade(COL.ironShade, -0.15));
    });
  }
  function ringPath(c, x0, y0, x1, y1, t, r) {
    S.addRoundRect(c, x0, y0, x1 - x0, y1 - y0, r);
    // inner hole, opposite winding
    const a = x0 + t, b = y0 + t, cc = x1 - t, d = y1 - t, rr = Math.max(0, r - t);
    c.moveTo(a + rr, b); c.arcTo(a, b, a, d, rr); c.arcTo(a, d, cc, d, rr); c.arcTo(cc, d, cc, b, rr); c.arcTo(cc, b, a, b, rr); c.closePath();
  }

  // ------------------------------------------------------------------ parts: teeth, clasp, chain
  function toothPath(c, x, len, w, lean) { // peg hanging DOWN from (x, 0); rounded tip
    const r = w * 0.4, tx = x + Math.sin(lean) * len;
    c.moveTo(x - w / 2, -0.02);
    c.lineTo(x - w / 2, 0);
    c.quadraticCurveTo(x - w * 0.5, len * 0.55, tx - r, len - r);
    c.arc(tx, len - r, r, Math.PI, 0, true);
    c.quadraticCurveTo(x + w * 0.5, len * 0.55, x + w / 2, 0);
    c.lineTo(x + w / 2, -0.02);
    c.closePath();
  }
  function drawTooth(g, x, len, w, lean) {
    const path = c => toothPath(c, x, len, w, lean || 0);
    g.beginPath(); path(g); g.fillStyle = COL.tooth; g.fill();
    clipIn(g, path, gg => { gg.fillStyle = COL.toothShade; gg.fillRect(x + w * 0.12, -0.05, w, len + 0.1); });
  }
  function teethRow(g, n, x0, x1, longL, shortL, w, seed, skip) {
    for (let i = 0; i < n; i++) {
      if (skip && skip(i, n)) continue;
      const x = lerp(x0, x1, (i + 0.5) / n), j = S.hash(seed * 31 + i);
      const L = (i % 2 ? shortL : longL) * (0.9 + 0.2 * j);
      drawTooth(g, x, L, w * (0.94 + 0.12 * S.hash(seed * 7 + i)), (j - 0.5) * 0.12 + (x / 0.5) * 0.05);
    }
  }
  function claspPath(c, w, h) { // our own brass hasp: a rounded shield hanging from a small hinge barrel
    c.moveTo(-w * 0.5, h * 0.22);
    c.lineTo(w * 0.5, h * 0.22);
    c.bezierCurveTo(w * 0.52, h * 0.6, w * 0.32, h * 0.92, 0, h);
    c.bezierCurveTo(-w * 0.32, h * 0.92, -w * 0.52, h * 0.6, -w * 0.5, h * 0.22);
    c.closePath();
  }
  function drawClaspLocal(g, w, h) {
    // hinge barrel
    cel(g, c => S.addRoundRect(c, -w * 0.3, 0, w * 0.6, h * 0.26, h * 0.1), C.shade(COL.brass, -0.08), COL.brassShade, w * 0.06, h * 0.05);
    cel(g, c => claspPath(c, w, h), COL.brass, COL.brassShade, w * 0.1, h * 0.07, COL.brassLight, w * 0.07, h * 0.0);
    // heart keyhole (our mark)
    const hx = 0, hy = h * 0.56, s = w * 0.3;
    g.beginPath();
    g.moveTo(hx, hy + s * 0.55);
    g.bezierCurveTo(hx - s * 0.95, hy - s * 0.05, hx - s * 0.5, hy - s * 0.78, hx, hy - s * 0.3);
    g.bezierCurveTo(hx + s * 0.5, hy - s * 0.78, hx + s * 0.95, hy - s * 0.05, hx, hy + s * 0.55);
    g.closePath(); g.fillStyle = COL.keyhole; g.fill();
    S.circle(g, -w * 0.3, h * 0.36, w * 0.045, COL.brassLight);
  }
  function linkRing(c, L, th) {
    S.addRoundRect(c, -L / 2, -L * 0.31, L, L * 0.62, L * 0.31);
    const a = -L / 2 + th, b = -L * 0.31 + th, w = L - 2 * th, h = L * 0.62 - 2 * th, r = Math.max(0.0001, L * 0.31 - th);
    c.moveTo(a + r, b); c.arcTo(a, b, a, b + h, r); c.arcTo(a, b + h, a + w, b + h, r); c.arcTo(a + w, b + h, a + w, b, r); c.arcTo(a + w, b, a, b, r); c.closePath();
  }
  function drawChainLinks(g, pts, sizes, cols) {
    const col = cols || { base: '#8A91A0', shade: '#5B6170', light: '#B9C0CC' };
    const seg = i => { const a = pts[i], b = pts[i + 1]; return { cx: (a[0] + b[0]) / 2, cy: (a[1] + b[1]) / 2, a: Math.atan2(b[1] - a[1], b[0] - a[0]) }; };
    for (let pass = 1; pass >= 0; pass--) for (let i = pass; i < pts.length - 1; i += 2) {
      const s = seg(i), L = sizes[Math.min(i, sizes.length - 1)], th = L * 0.2;
      g.save(); g.translate(s.cx, s.cy); g.rotate(s.a);
      if (pass === 1) { // edge-on bar
        S.capsule(g, -L * 0.5 + th * 0.6, 0, L * 0.5 - th * 0.6, 0, th * 1.35, th * 1.35, col.shade);
        S.capsule(g, -L * 0.5 + th * 0.9, -th * 0.2, L * 0.5 - th * 0.9, -th * 0.2, th * 0.45, th * 0.45, col.base);
      } else { // face-on ring with one hard shade at the screen bottom-right
        g.beginPath(); linkRing(g, L, th); g.fillStyle = col.base; g.fill();
        g.save(); g.beginPath(); linkRing(g, L, th); g.clip();
        g.rotate(-s.a); g.translate(th * 0.5 * LS, th * 0.5); g.rotate(s.a);
        g.beginPath(); g.rect(-L, -L, 2 * L, 2 * L); S.addRoundRect(g, -L / 2 - th * 0.15, -L * 0.31 - th * 0.15, L, L * 0.62, L * 0.31);
        g.fillStyle = col.shade; g.fill('evenodd');
        g.restore();
      }
      g.restore();
    }
  }

  // ------------------------------------------------------------------ parts: limbs
  function handGeom(wr, ang, side, type, a) {
    const H = HANDS[type] || HANDS.hang, k = (a && a.size) || 1.08;
    const cs = Math.cos(ang), sn = Math.sin(ang);
    const T = (x, y) => [wr[0] + (x * cs - y * side * sn) * k, wr[1] + (x * sn + y * side * cs) * k];
    const spread = ((a && a.spread) ?? H.spread) * RAD, curl = ((a && a.curl) ?? H.curl) * RAD;
    const parts = [], claws = [];
    const lens = [0.95, 1.06, 0.9];
    for (let j = 0; j < 3; j++) {
      const by = (j - 1) * 0.036 + 0.006, base = [0.085, by];
      let A = (j - 1) * spread + 0.12 * (j - 1) * 0;
      const c = curl + ((H.curls && H.curls[j]) || 0) * RAD;
      const l1 = 0.064 * lens[j], l2 = 0.06 * lens[j];
      const p1 = [base[0] + Math.cos(A) * l1, base[1] + Math.sin(A) * l1];
      const A2 = A + c, p2 = [p1[0] + Math.cos(A2) * l2, p1[1] + Math.sin(A2) * l2];
      const A3 = A2 + c * 0.4, tip = [p2[0] + Math.cos(A3) * 0.016, p2[1] + Math.sin(A3) * 0.016];
      parts.push({ pts: [T(...base), T(...p1), T(...p2)], w: [0.05 * k, 0.047 * k, 0.042 * k] });
      claws.push({ a: T(p2[0] - Math.cos(A3) * 0.008, p2[1] - Math.sin(A3) * 0.008), b: T(...tip), w: 0.03 * k });
    }
    // thumb (on the -y side)
    const ta = -(H.thumb * RAD), tc = -(H.thumbCurl * RAD);
    const t0 = [0.04, -0.034], t1 = [t0[0] + Math.cos(ta) * 0.05, t0[1] + Math.sin(ta) * 0.05];
    const t2 = [t1[0] + Math.cos(ta + tc) * 0.04, t1[1] + Math.sin(ta + tc) * 0.04];
    const tt = [t2[0] + Math.cos(ta + tc) * 0.014, t2[1] + Math.sin(ta + tc) * 0.014];
    parts.push({ pts: [T(...t0), T(...t1), T(...t2)], w: [0.052 * k, 0.046 * k, 0.04 * k] });
    claws.push({ a: T(t2[0] - Math.cos(ta + tc) * 0.006, t2[1] - Math.sin(ta + tc) * 0.006), b: T(...tt), w: 0.028 * k });
    // palm (a soft rounded box)
    const palm = [];
    for (let i = 0; i < 20; i++) { const th = i / 20 * TAU * side; palm.push(T(0.05 + Math.cos(th) * 0.058, Math.sin(th) * 0.054 + 0.004)); }
    return { parts, claws, palm };
  }
  function addHand(c, hg) {
    S.addBlob(c, hg.palm, 0.5);
    for (const pt of hg.parts) S.addLimb(c, pt.pts, pt.w);
  }
  function drawClaws(g, hg, col, shade) {
    cel(g, c => { for (const cl of hg.claws) S.addCapsule(c, cl.a[0], cl.a[1], cl.b[0], cl.b[1], cl.w, cl.w * 0.72); }, col || COL.claw, shade || COL.clawShade, 0.008, 0.008);
  }
  function limbCols(far) {
    return far ? { base: C.mix(COL.limb, COL.limbShade, 0.55), shade: C.shade(COL.limbShade, -0.18), claw: C.shade(COL.claw, -0.15), clawShade: C.shade(COL.clawShade, -0.15) }
      : { base: COL.limb, shade: COL.limbShade, claw: COL.claw, clawShade: COL.clawShade };
  }
  function drawArm(g, A, far) {
    const col = limbCols(far), w = DIM.armW;
    const hg = handGeom(A.W, A.hAng, A.side, A.a.hand || 'hang', A.a);
    cel(g, c => { S.addLimb(c, [A.S, A.E, A.W], [w[0], w[1], w[2]]); S.addCapsule(c, A.E[0], A.E[1], A.E[0], A.E[1], 0.1, 0.1); addHand(c, hg); }, col.base, col.shade, 0.02, 0.02);
    S.circle(g, A.E[0] + 0.004, A.E[1] + 0.004, 0.016, col.shade);
    drawClaws(g, hg, col.claw, col.clawShade);
    return hg;
  }
  function drawLeg(g, Lg, far, v) {
    const col = limbCols(far), w = DIM.legW, s = Lg.side;
    // foot: small oval pointing outward (front view) or forward (side view)
    const fwd = -v.sp, out = s * v.cp;
    const fd = Math.hypot(out * 0.06 + fwd * 0.11, 0) > 0 ? 1 : 1;
    const fx = Lg.A[0] + out * 0.045 + fwd * 0.07, fy = Lg.A[1] + 0.024;
    const frx = 0.07 + 0.045 * Math.abs(v.sp), fry = 0.036;
    const fr = (out * 0.12 + fwd * 0.05) * fd;
    cel(g, c => {
      S.addLimb(c, [Lg.H, Lg.K, Lg.A], [w[0], w[1], w[3]]);
      S.addCapsule(c, Lg.K[0], Lg.K[1], Lg.K[0], Lg.K[1], 0.088, 0.088);           // knee knob
      S.addCapsule(c, Lg.A[0], Lg.A[1], Lg.A[0], Lg.A[1], 0.062, 0.062);           // ankle knob
      c.moveTo(fx + frx, fy); c.ellipse(fx, fy, frx, fry, fr, 0, TAU);
    }, col.base, col.shade, 0.02, 0.02);
    S.circle(g, Lg.K[0] + 0.004, Lg.K[1] + 0.004, 0.016, col.shade);
    // two toe nubs
    for (const k of [0.45, 0.8]) {
      const tx = fx + Math.cos(fr) * frx * k * (out + fwd >= 0 ? 1 : -1) * 0.9, ty = fy + 0.008;
      S.circle(g, tx, ty + fry * 0.55, 0.008, C.rgba(col.shade, 0.0));
    }
  }

  // ------------------------------------------------------------------ the painter
  function paintBody(g, p, R) {
    const v = R.v, hb = DIM.hb, dep = DIM.dep, T = DIM.T, o = DIM.o, tw = DIM.tw;
    const ex = p._ex;
    // --- base side face (shows when turned)
    if (v.vis([1, 0, 0]) > 0.02) inFace(g, v, [0.5, hb, 0], [0, 0, -1], [0, -1, 0], gg => drawBaseSide(gg, p));
    // --- base front face
    if (v.vis([0, 0, 1]) > 0.02) inFace(g, v, [0, hb, 0], [1, 0, 0], [0, -1, 0], gg => drawBaseFront(gg, p));
    // --- base top rim and the lid's wall edges: both sit BEHIND the mouth contents
    if (v.lid > 3 && !skip(p, 'ring')) inFace(g, v, [0, hb, -dep], [1, 0, 0], [0, 0, 1], gg => { gg.beginPath(); ringPath(gg, -0.5, 0, 0.5, dep, tw, 0.05); gg.fillStyle = COL.woodRim; gg.fill(); });
    const nb = v.Lv(0, -1, 0);
    if (v.lid > 3 && v.vis(nb) > 0.01 && !skip(p, 'lidRing')) inFace(g, v, v.L(0, hb, -dep), v.Lv(1, 0, 0), v.Lv(0, 0, 1), gg => {
      gg.beginPath(); ringPath(gg, -(0.5 + o), 0, 0.5 + o, dep + o, tw, 0.04); gg.fillStyle = COL.woodShade; gg.fill();
    });
    // --- the mouth
    const hullPath = c => roundPolyAdd(c, R.hull, 0.07);
    const open = v.lid > 0.5;
    if (open) {
      clipIn(g, hullPath, gg => {
        gg.fillStyle = COL.mouthShade; gg.fillRect(-5, -5, 10, 10);
        gg.save(); gg.translate(0.035 * LS, 0.06); gg.beginPath(); hullPath(gg); gg.fillStyle = COL.mouth; gg.fill(); gg.restore();
        if (v.lid >= 35) drawEyes(gg, p, R);
        // gums + teeth (front rows; side rows foreshorten away in the front view)
        const xA = v.Pl(1, 0, 0);
        const rowAt = (O, down, fn) => { gg.save(); gg.transform(xA[0], xA[1], 0, down ? 1 : -1, O[0], O[1]); fn(gg); gg.restore(); };
        const lowO = v.P(0, hb, 0), upO = v.PL(0, hb, o - tw);
        const gk = sstep(2, 30, v.lid);
        rowAt(lowO, false, c => {
          S.roundRect(c, -0.5, -0.012, 1.0, 0.034 + 0.014 * gk, 0.018, COL.gum);
          teethRow(c, 12, -0.445, 0.445, 0.054, 0.04, 0.043, 2, null);
        });
        rowAt(upO, true, c => {
          S.roundRect(c, -0.55, -0.012, 1.1, 0.036 + 0.014 * gk, 0.018, COL.gum);
          teethRow(c, 13, -0.465, 0.465, 0.074, 0.054, 0.043, 5, null);
        });
        // side rows (three pegs near the front corner, visible when turned)
        if (v.sp > 0.15) {
          const zA = v.Pl(0, 0, -1);
          gg.save(); const O = v.P(0.5 - tw, hb, -0.02); gg.transform(zA[0], zA[1], 0, -1, O[0], O[1]);
          S.roundRect(gg, -0.02, -0.01, 0.34, 0.028, 0.012, COL.gum);
          teethRow(gg, 4, 0.0, 0.3, 0.05, 0.036, 0.034, 9, null); gg.restore();
          const lz = v.Pl(...v.Lv(0, 0, -1)); gg.save(); const O2 = v.PL(0.5 + o - tw, hb, o - tw - 0.02); gg.transform(lz[0], lz[1], 0, 1, O2[0], O2[1]);
          S.roundRect(gg, -0.02, -0.01, 0.36, 0.03, 0.012, COL.gum);
          teethRow(gg, 4, 0.0, 0.32, 0.07, 0.05, 0.034, 11, null); gg.restore();
        }
        if (v.lid >= 35) drawBrows(gg, p, R);
        if (v.lid < 35) drawGlints(gg, p, R);
      });
    }
  }
  function paintLid(g, p, R) {
    const v = R.v, hb = DIM.hb, dep = DIM.dep, T = DIM.T, o = DIM.o, tw = DIM.tw, dome = DIM.dome;
    // top surface (barrel lid): visible when nearly shut
    const nt = v.Lv(0, 1, 0);
    if (v.vis(nt) > 0.005 && !skip(p, 'lidTop')) {
      const w = 0.5 + o, rows = [];
      for (let i = 0; i <= 8; i++) { const zz = lerp(o, -dep, i / 8), yy = hb + T + dome * Math.sin(Math.PI * i / 8); rows.push([zz, yy]); }
      const pts = [];
      for (const [zz, yy] of rows) { pts.push(v.PL(-w + 0.02, yy, zz)); pts.push(v.PL(w - 0.02, yy, zz)); }
      const hp = hull(pts);
      const path = c => roundPolyAdd(c, hp, 0.03);
      g.beginPath(); path(g); g.fillStyle = COL.woodRim; g.fill();
      if (v.sp < 0.6) clipIn(g, path, gg => {
        for (const sx of [-0.3, 0.3]) {
          const strip = [];
          for (const [zz, yy] of rows) strip.push(v.PL(sx - 0.037, yy + 0.002, zz));
          for (let i = rows.length - 1; i >= 0; i--) strip.push(v.PL(sx + 0.037, rows[i][1] + 0.002, rows[i][0]));
          S.poly(gg, strip, C.mix(COL.iron, COL.rivet, 0.25));
        }
        // plank seam lines along the top
        for (const sx of [-0.1, 0.1]) { const ln = rows.map(([zz, yy]) => v.PL(sx, yy, zz)); S.curve(gg, ln, C.rgba(COL.woodShade, 0.55), 0.008); }
      });
    }
    // side face (shows the barrel arch)
    if (v.vis(v.Lv(1, 0, 0)) > 0.02 && !skip(p, 'lidSide')) inFace(g, v, v.L(0.5 + o, hb + T, o), v.Lv(0, 0, -1), v.Lv(0, -1, 0), gg => drawLidSide(gg, p));
    // front face
    const nf = v.Lv(0, 0, 1);
    if (v.vis(nf) > 0.01 && !skip(p, 'lidFront')) inFace(g, v, v.L(0, hb + T, o), v.Lv(1, 0, 0), v.Lv(0, -1, 0), gg => drawLidFront(gg, p));
  }
  function paintClasp(g, p, R) {
    const v = R.v, A = v.PL(0, DIM.hb + 0.045, DIM.o + 0.006);
    const sw = (p.claspSwing || 0) * RAD - R.tilt * 0.85;
    g.save(); g.translate(A[0], A[1]); g.rotate(sw); g.scale(Math.max(0.22, v.cp), 1);
    drawClaspLocal(g, 0.115, 0.135);
    g.restore();
  }
  function paintHasp(g, p, R) {
    const v = R.v, c = v.P(0.5 + 0.03, DIM.hb - 0.12, -0.12);
    // a little iron staple sticking out of the side
    g.save(); g.translate(c[0], c[1]);
    const w = 0.03 + 0.02 * v.cp;
    g.beginPath(); g.ellipse(0, 0, w, 0.032, 0, 0, TAU); g.ellipse(0, 0, w - 0.013, 0.019, 0, 0, TAU, true);
    g.fillStyle = COL.iron; g.fill();
    g.restore();
  }

  function eyeOpts(p, R, s) {
    const ex = p._ex, e = Object.assign({}, ex.eye);
    const o = {
      x: 0, y: 0, w: DIM.eyeW, iris: S.PAL.iris.gold, pupilColor: '#2A1206', ink: COL.ink, mirror: s > 0,
      lid: 0.16, wing: 0.22, lashes: 3, lashLen: 0.34, teeth: 3, crease: 2, creaseColor: '#b79aa8',
    };
    Object.assign(o, e);
    if (p.look) o.look = p.look;
    if (p.blink !== undefined && !o.closed) o.open = Math.min(o.open ?? 1, p.blink);
    if (o.pupil === 'star') o.pupilColor = '#FFF4C8';
    if (o.pupil === 'swirl') o.pupilColor = '#2A1206';
    return o;
  }
  function eyeFrame(g, R, i, fn) {
    const v = R.v, c = R.eyes[i], ax = v.Pl(1, 0, 0);
    const far = i === 0, sc = v.cp < 0.4 ? (far ? 0 : Math.max(0.42, v.cp)) : 1;
    if (sc === 0) return;
    g.save(); g.translate(c[0], c[1]);
    if (sc === 1) g.transform(ax[0], ax[1], 0, 1, 0, 0); else g.transform(sc, 0, 0, 1, 0, 0);
    fn(g); g.restore();
  }
  function drawEyes(g, p, R) {
    const ex = p._ex, ew = DIM.eyeW;
    for (let i = 0; i < 2; i++) {
      const s = i === 0 ? -1 : 1;
      eyeFrame(g, R, i, gg => {
        const o = eyeOpts(p, R, s), eh = ew * (o.h ?? 0.6);
        if (ex.rings) { // creepy: dark sunken rings
          gg.beginPath(); gg.ellipse(0, 0.012, ew * 0.62, eh * 0.95, 0, 0, TAU); gg.fillStyle = 'rgba(12,2,6,0.55)'; gg.fill();
        }
        if (ex.blush > 0) S.blush(gg, s * 0.02, eh * 0.62 + 0.035, ew * 0.82, ex.blush, COL.blush);
        S.eye(gg, o);
      });
    }
  }
  // floating brow strokes: painted AFTER the teeth so the upper pegs never hide them
  function drawBrows(g, p, R) {
    const ex = p._ex, ew = DIM.eyeW;
    for (let i = 0; i < 2; i++) {
      const s = i === 0 ? -1 : 1;
      eyeFrame(g, R, i, gg => {
        const o = eyeOpts(p, R, s), eh = ew * (o.h ?? 0.6);
        const b = Object.assign({}, ex.brow || {}, (ex.brow && ex.brow[s < 0 ? 'L' : 'R']) || {});
        if (b && b.show !== false) S.brow(gg, s * 0.022, -eh * 0.5 - 0.04 + (b.dy || 0), ew * 0.42, { tilt: b.tilt || 0, arch: b.arch ?? 0.12, thick: 0.2, mirror: s > 0, color: COL.brow });
      });
    }
  }
  function drawGlints(g, p, R) {
    const v = R.v, k = clamp(v.lid / 6);
    if (k <= 0) return;
    const pts = [-1, 1].map(s => R.mp(s * DIM.eyeX, 0.42, 0.02));
    S.glow(g, gg => {
      for (const c of pts) {
        gg.beginPath(); gg.ellipse(c[0], c[1], 0.03 * k, 0.016 * k, 0, 0, TAU); gg.fillStyle = COL.glint; gg.fill();
        gg.beginPath(); gg.ellipse(c[0] - 0.006, c[1] - 0.002, 0.01 * k, 0.006 * k, 0, 0, TAU); gg.fillStyle = '#FFF3C4'; gg.fill();
      }
    }, { blur: 0.03 * DIM.U * (p.scale || 1), alpha: 0.9, crispAlpha: 1 });
  }
  function paintTongue(g, p, R) {
    const P = R.tongue; if (!P) return;
    const v = R.v, t = p.tongue, W0 = (t.width ?? 0.25) * (0.2 + 0.8 * Math.abs(v.cp)) + 0.05 * Math.abs(v.sp);
    const n = P.length;
    const half = (u, i) => {
      let w = W0 * (1 - 0.14 * u);
      if (u < 0.05) w *= 0.7 + 0.3 * Math.sqrt(u / 0.05);
      const tipU = 1 - Math.min(0.2, 0.1 / Math.max(0.2, t.len));
      if (u > tipU) w *= Math.sqrt(Math.max(0, 1 - ((u - tipU) / (1 - tipU)) ** 2));
      return w / 2;
    };
    const path = c => ribbonAdd(c, P, half);
    // contact shadow on whatever the tongue lies over (separates tongue from wood in grey)
    g.save(); g.translate(0.022, 0.03); g.fillStyle = 'rgba(42,9,20,0.42)'; g.beginPath(); path(g); g.fill(); g.restore();
    cel(g, path, COL.tongue, COL.tongueShade, 0.026, 0.02);
    // centre groove
    const U = arcU(P), G = P.filter((_, i) => U[i] > 0.1 && U[i] < 0.8);
    if (G.length > 2) S.strip(g, G, u => 0.017 * Math.sin(Math.PI * u) ** 0.6, COL.groove);
  }
  function paintFx(g, p, R) {
    const fx = p.fx || {}, v = R.v;
    const lidTL = R.B(v.PL(-0.5, DIM.hb + DIM.T, DIM.o));
    const lidTR = R.B(v.PL(0.5, DIM.hb + DIM.T, DIM.o));
    if (fx.sweat) S.sweat(g, lidTR[0] + 0.1, lidTR[1] + 0.02, 0.12, { angle: 0.25 });
    if (fx.zzz) {
      const z0 = [R.lidTop[0] + 0.55, R.lidTop[1] - 0.12];
      [[0, 0, 0.13], [0.13, -0.15, 0.1], [0.23, -0.28, 0.075]].forEach(([dx, dy, sz], i) => {
        S.title(g, 'z', z0[0] + dx, z0[1] + dy, sz, { color: i ? 'rgba(216,204,224,0.75)' : '#D8CCE0', weight: 600 });
      });
    }
    if (fx.drool) {
      const a = R.B(R.mp(-0.2, 0.0, 0)), b = [a[0] - 0.012, a[1] + 0.13];
      S.strip(g, [a, [a[0] - 0.01, a[1] + 0.06], b], u => 0.024 * (1 - 0.35 * u), COL.drool);
      S.sweat(g, b[0], b[1] + 0.02, 0.07, { color: COL.drool, shade: COL.droolShade });
    }
    if (fx.sparkle) {
      for (const [dx, dy, r] of [[-0.6, -0.1, 0.05], [0.62, -0.2, 0.055], [0.56, 0.12, 0.035]]) {
        const c = R.B(R.mp(dx, 0.55, 0)); S.sparkle(g, c[0], c[1], r, '#FFE58A');
      }
    }
    if (fx.tear) {
      for (const s of [-1, 1]) { const c = R.B(R.mp(s * (DIM.eyeX + 0.14), 0.5, 0.05)); S.sweat(g, c[0], c[1], 0.05, { color: '#bfe3ff', shade: '#8cc4ee' }); }
    }
    if (fx.wave) {
      const A = R.arms[fx.wave]; if (A) {
        const c = add(A.W, mul(dir2(A.hAng), 0.14));
        g.save(); g.strokeStyle = 'rgba(216,204,224,0.8)'; g.lineCap = 'round';
        for (const [r, w] of [[0.2, 0.016], [0.27, 0.012]]) { g.lineWidth = w; g.beginPath(); g.arc(c[0], c[1], r, -Math.PI * 0.95, -Math.PI * 0.62); g.stroke(); g.beginPath(); g.arc(c[0], c[1], r, -Math.PI * 0.38, -Math.PI * 0.05); g.stroke(); }
        g.restore();
      }
    }
    if (fx.tap) {
      const A = R.arms[fx.tap === 'R' ? 'R' : 'L']; if (A) {
        const sg = A.side, tip = add(A.W, mul(dir2(A.hAng), 0.16)); g.save(); g.strokeStyle = 'rgba(216,204,224,0.8)'; g.lineCap = 'round'; g.lineWidth = 0.014;
        for (const [dx, dy, ex2, ey2] of [[0.09, -0.06, 0.15, -0.1], [0.11, 0.02, 0.18, 0.02], [0.02, -0.11, 0.04, -0.18]]) { g.beginPath(); g.moveTo(tip[0] - sg * dx, tip[1] + dy); g.lineTo(tip[0] - sg * ex2, tip[1] + ey2); g.stroke(); }
        g.restore();
      }
    }
    if (fx.speed) {
      g.save(); g.strokeStyle = 'rgba(216,204,224,0.35)'; g.lineCap = 'round';
      const c = R.B([0, -0.4]);
      for (const [dy, l, w] of [[-0.5, 0.4, 0.016], [-0.2, 0.6, 0.014], [0.1, 0.36, 0.016], [0.4, 0.5, 0.012]]) { g.lineWidth = w; g.beginPath(); g.moveTo(c[0] + 0.72, c[1] + dy); g.lineTo(c[0] + 0.72 + l, c[1] + dy + l * 0.08); g.stroke(); }
      g.restore();
    }
  }

  function draw(ctx, params) {
    const p = resolve(params);
    const v = makeView(p), R = solve(p, v);
    const U = DIM.U * p.scale, flip = p.flip ? -1 : 1;
    const paint = g => {
      g.save(); g.translate(p.x, p.y); g.scale(U * flip, U);
      LS = flip;
      const far = v.sp > 0.55; // side-ish: the left limbs are behind the chest
      // 1. legs (behind the chest), far ones first
      if (R.legs.L && far) drawLeg(g, R.legs.L, true, v);
      if (R.legs.L && !far) drawLeg(g, R.legs.L, false, v);
      if (R.legs.R) drawLeg(g, R.legs.R, false, v);
      for (const s of ['L', 'R']) { const A = R.arms[s]; if (A && A.a.z !== 'front' && !(s === 'R' && far && false)) drawArm(g, A, far && s === 'L'); }
      // 2. chest
      g.save(); g.translate(R.hip[0], R.hip[1]); g.rotate(R.tilt);
      paintBody(g, p, R);
      g.restore();
      // 3. tongue, lid, clasp
      paintTongue(g, p, R);
      g.save(); g.translate(R.hip[0], R.hip[1]); g.rotate(R.tilt);
      paintLid(g, p, R);
      if (!skip(p, 'clasp')) paintClasp(g, p, R);
      if (p.parts.chain && p.chain !== null) paintHasp(g, p, R);
      g.restore();
      // 4. arms in front, chain, fx
      for (const s of ['L', 'R']) { const A = R.arms[s]; if (A && A.a.z === 'front') drawArm(g, A, false); }
      if (R.chain) drawChainLinks(g, R.chain.pts, R.chain.sizes);
      if (p.parts.fx) paintFx(g, p, R);
      g.restore();
      LS = 1;
    };
    if (p.shadow === false) paint(ctx);
    else S.shadowGroup(ctx, paint, { scale: p.scale, blur: 20, dx: 9, dy: 9, bounds: { x: p.x - 2.6 * U, y: p.y - 3.6 * U, w: 5.2 * U, h: 4.0 * U } });
    return R;
  }

  function solvePublic(params) {
    const p = resolve(params), v = makeView(p), R = solve(p, v);
    const U = DIM.U * p.scale, f = p.flip ? -1 : 1;
    const toPx = q => [p.x + q[0] * U * f, p.y + q[1] * U];
    return {
      hip: toPx(R.hip), eyes: R.eyes.map(e => toPx(R.B(e))), mouth: toPx(R.B(R.mp(0, 0.5, 0))),
      lidTop: toPx(R.lidTop), U, R,
      top: (() => { let m = 1e9; const v = R.v; for (const x of [-0.5, 0.5]) for (const z of [DIM.o, -DIM.dep / 2, -DIM.dep]) { const y = DIM.hb + DIM.T + (z === -DIM.dep / 2 ? DIM.dome : 0); m = Math.min(m, R.B(v.PL(x, y, z))[1]); } return p.y + m * U; })(),
    };
  }

  window.MIMIKU = {
    draw, solve: solvePublic, POSES, EXPR, COL, DIM, HANDS,
    drawHand(ctx, x, y, angDeg, type, side = 1, size = 1) {
      ctx.save(); ctx.translate(x, y); ctx.scale(size, size);
      const hg = handGeom([0, 0], angDeg * RAD, side, type, {});
      cel(ctx, c => addHand(c, hg), COL.limb, COL.limbShade, 0.02, 0.02);
      drawClaws(ctx, hg); ctx.restore();
    },
    drawTooth(ctx, x, y, len, w, down = true) { ctx.save(); ctx.translate(x, y); if (!down) ctx.scale(1, -1); drawTooth(ctx, 0, len, w, 0); ctx.restore(); },
    drawClasp(ctx, x, y, size) { ctx.save(); ctx.translate(x, y); ctx.scale(size, size); drawClaspLocal(ctx, 1, 1.17); ctx.restore(); },
    drawChain(ctx, pts, sizes) { drawChainLinks(ctx, pts, sizes); },
    cel,
  };
})();
