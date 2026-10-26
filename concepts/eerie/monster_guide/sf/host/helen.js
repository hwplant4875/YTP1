/* =====================================================================================================================
 * helen.js : window.HELEN, the parametric rig for HELEN, the TV-head HR manager of Monster HR (host, the CUTE layer).
 * Needs core/lib_core.js (window.SFX) loaded first. Plain canvas 2D, deterministic (SFX.rng / SFX.hash, never
 * Math.random). Spec: plan_v2_changes.md section B ("Telly" = Helen), owner decisions 2026-10-26.
 *
 * DESIGN (H = TV head height = 104 px at s = 1; the show scale is s = 1 -> chest width W = 180 px)
 *   case top 458 px above the ground at s = 1 (~2.5 W; the head is drawn 1.1x, HS, for a cuter read); the
 *   rabbit-ear antennae reach ~504 px. HELEN.solve() gives exact headTop / screen / hands / bounds per pose.
 *   head    rounded CRT: 1.3 H wide, corner r 0.15 H, 3/4 side depth 0.35 H. Case cream #E8DCC8, bezel inside #2A2230.
 *           screen 0.96 x 0.72 H (4:3), convex, bezel top 0.1 / sides 0.17 / bottom 0.18 H. Bottom bezel: speaker
 *           grille left, dials right (mint #3FC9B5 + grey #8C8F96). Antennae 0.45 H at +-0.15 H, 25 deg, ball tips,
 *           springy (they act like an ahoge).
 *   screen  dark teal #0F3B36, line art #8FE6D8 glowing #3FC9B5 (SFX.eye glow mode = the 귤멍 eye recipe as light),
 *           scanlines (6 px period at 1080p, 15 %), CRT vignette, glass glare top-left. Mint is used ONLY on the screen,
 *           the lanyard and one dial.
 *   body    lavender blazer + knee-length pencil skirt #958BB0 / shade #736A8C, blouse #F2EEE8 with a plum bow
 *           #3A2A3E, skin #F6E6E8, low pumps #2A2230. Props: mint lanyard + badge "HELEN / HR MANAGER", clipboard
 *           #8C8F96 with paper #F4EFE6, TV remote #2A2230 with a red #D83A4A button, rubber stamp.
 *   look    flat fills, ONE hard shade per material (light from the top-left), no outlines, one group drop shadow,
 *           mint screen spill on collar / shoulders / hands, optional rim light for dark sets.
 *
 * API
 *   HELEN.draw(ctx, x, y, s = 1, o = {})   whole character as ONE shadow group. (x, y) = ground point between the feet.
 *     face        'neutral' | 'pleased' | 'surprised' | 'annoyed' | 'eerie' | 'panic' (alias 'panic-colourbars')
 *                 | 'thinking' ('thinking-spinner') | 'number' | 'slide' | 'off' | 'error404' ('404').
 *                 A string that starts with a digit (e.g. '7°', '9.9') is shorthand for face 'number'.
 *     number      text for the number face ('7°', '9.9', '0:10' ...)      numberLabel  optional small caption above it
 *     slide       { n: 10, text: 'WHEN THEY KNOCK, OPEN WIDE.' }   Rule card filling the screen; a tiny face window in
 *                 the bottom-right corner keeps lip-syncing (mouth / blink / look apply to it).
 *     mouth       lip-sync shape: 'none' (the face's closed mouth) | 'o' | 'u' | 'wide' | '~'
 *     look        {x, y} gaze -1..1 in SCREEN space (x + = screen right). Default: straight, or toward the turn.
 *     blink       1 open .. 0 shut. Default: automatic idle blink from t (SFX.blinkAt) when t is given, else 1.
 *     prevFace, wipe   static wipe between faces: wipe 0..1 sweeps a noise band down the screen; above it the new
 *                 face, below it prevFace. Use HELEN.wipeAt(t, tChange) for the 2-3 frame timing.
 *     offK        'off' face progress 0..1 (collapse to a line, then to a white dot, then dark). Default 1 (dark).
 *     pose        'idle-clipboard' (default) | 'idle-hip' ('hand-on-hip') | 'remote-at-head' | 'present-point'
 *                 | 'stamp' | 'walk' | 'stand'
 *     phase       walk cycle 0..1 (one full cycle = two steps). Move x yourself: one cycle covers HELEN.STRIDE * 2 * s.
 *     stampK      stamp pose: 0 raised .. 1 down on the paper.   stampText 'APPROVED' | 'DENIED'
 *     stampMark   true = the imprint is on the paper (default: stampK >= 0.97)
 *     turn        0 front .. 1 three-quarter (35 deg).            dir  1 faces screen-right, -1 screen-left (mirror)
 *     headTurn    head turn on its own, -1..1, independent of the body (present-point turns the head to the hand).
 *                 Default: follows `turn`. Signed: - = toward screen-left in body space.
 *     weight      0..1 contrapposto: hips shift, one knee softens, the shoulders counter-tilt. Default 1 standing,
 *                 forced 0 while walking. Pairs well with pose 'idle-hip' + headTilt 6-8 for hero shots.
 *     eerieSmile  force the eerie face's flickering smile strip on (default: a deterministic 2-frame flicker from t).
 *     t           seconds: idle breathing, antenna sway, static flicker, spinner, auto blink.
 *     antT        seconds since the last antenna impulse (springy kick: a face change, a stop, a stamp hit ...)
 *     antenna     override { ang: deg, bend, still: bool } for both rods
 *     headTilt    degrees (+ = clockwise on screen when dir = 1)      lean  degrees, upper body around the hips
 *     from, blend pose transition: from = the options that differ in the previous pose (e.g. { pose: 'walk', phase }),
 *                 blend 0..1 (eased inside with easeInOutCubic; 8-12 frames per plan 8). Joints lerp, props swap at 0.5.
 *     arms        per-arm override { near: { wrist: [x, y] (H units, body space), bend: 1 | -1, hand, rAng }, far: {..} }
 *                 near = her right arm (screen-left when dir = 1, holds the remote); far = her left (clipboard).
 *     props       { clipboard: true, remote: true, badge: true }
 *     spill       0..1 mint screen light on collar / shoulders / hands (default 0.3)
 *     bloom       0..1 soft screen halo drawn into the scene around the head (default 0.35)
 *     rim         false | { color = '#DCE8FF', alpha = 0.55, width = 2.6 (px at s = 1), dir = [-1, -0.6] } rim light on
 *                 the silhouette edge facing dir (screen space). Default false; turn it on for dark sets.
 *     shadow      group drop shadow (default true)        cast = contact shadow on the floor (default true)
 *   HELEN.drawHead(ctx, x, y, s, o)   head only (close-ups, face sheets). (x, y) = bottom centre of the case.
 *   HELEN.solve(x, y, s, o) -> { screen: {x, y, w, h}, headTop, neck, hands: {near, far}, bounds } in canvas px
 *   HELEN.wipeAt(t, tChange, frames = 3, fps = 30) -> 0..1 wipe value during the switch, null outside it
 *   HELEN.drawClipboard / drawRemote / drawStamp / drawBadge (ctx, x, y, s, o)   props alone (callouts)
 *   HELEN.FACES, HELEN.POSES, HELEN.MOUTHS, HELEN.COL, HELEN.H, HELEN.STRIDE
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX;
  if (!S) throw new Error('helen.js needs lib_core.js (window.SFX) loaded first');
  const C = S.color, TAU = Math.PI * 2, RAD = Math.PI / 180, clamp = S.clamp, lerp = S.lerp;
  const H = 104;
  const STRIDE = 0.34; // H units per step
  const HS = 1.1;       // head drawn 10 % over the 4.3-head canon (cuter read; total stays ~2.55 W at s = 1)

  const COL = {
    case: '#E8DCC8', caseShade: '#CDBFA8', caseSide: '#D5C7AF', caseSideShade: '#BBAC92', grille: '#A3957E',
    caseSideLit: '#EFE5D3', caseSideLitShade: '#D9CDB7',
    bezel: '#2A2230', screen: '#0F3B36', screenDeep: '#0A2B27', line: '#8FE6D8', mint: '#3FC9B5', mintShade: '#2A9C8B',
    grey: '#8C8F96', greyShade: '#6E7178', ant: '#9EA2AA', antShade: '#7C8088', ball: '#E8DCC8', ballShade: '#C2B49B',
    blazer: '#958BB0', blazerShade: '#736A8C', crease: '#736A8C', button: '#3A2A3E',
    blouse: '#F2EEE8', blouseShade: '#D9D0CB', bow: '#3A2A3E', bowShade: '#2A1E2D',
    skin: '#F6E6E8', skinShade: '#EBD0D6', shoe: '#2A2230', shoeShade: '#1B1520', shoeLight: '#51465A',
    board: '#8C8F96', boardShade: '#6E7178', paper: '#F4EFE6', paperLine: '#CEC5B6', ink: '#2A2230', clip: '#C3C9D3', clipShade: '#8A91A0',
    remote: '#2A2230', remoteShade: '#17121B', remoteKey: '#5A5262', red: '#D83A4A', redShade: '#A52A38',
    wood: '#A0866B', woodShade: '#7A6652', blush: '#F29BB0', stamp: '#D83A4A', badge: '#F4EFE6', lens: '#E2FFFA',
  };

  const FACE_ALIAS = {
    'panic-colourbars': 'panic', 'panic-colorbars': 'panic', colourbars: 'panic', colorbars: 'panic', bars: 'panic',
    'thinking-spinner': 'thinking', spinner: 'thinking', loading: 'thinking', '404': 'error404', error: 'error404',
    rule: 'slide', happy: 'pleased', shock: 'surprised', angry: 'annoyed', default: 'neutral', bored: 'neutral',
  };
  const FACES = ['neutral', 'pleased', 'surprised', 'annoyed', 'eerie', 'panic', 'thinking', 'number', 'slide', 'off', 'error404'];
  const POSES = ['idle-clipboard', 'remote-at-head', 'present-point', 'stamp', 'walk', 'stand'];
  const MOUTHS = ['none', 'o', 'u', 'wide', '~'];

  let LX = 1; // rig mirror (dir). Hard shades are offset by LX so the light stays top-left on screen.
  const cel = (g, fn, base, shade, k = 0.045) => S.cel(g, fn, base, shade, k * H * LX, k * H);
  // union-safe cel for paths made of OVERLAPPING sub-paths (limbs, hands): SFX.cel's evenodd trick would punch the
  // overlaps. Base fill, then inside the shape: shade everywhere, base again shifted up-left.
  const celU = (g, fn, base, shade, k = 0.045) => {
    const dx = k * H * LX, dy = k * H;
    g.beginPath(); fn(g); g.fillStyle = base; g.fill();
    g.save(); g.clip();
    g.fillStyle = shade; g.fill();
    g.translate(-dx, -dy); g.beginPath(); fn(g); g.fillStyle = base; g.fill();
    g.restore();
  };
  // run fn in a frame that undoes the rig mirror around x = cx (text, dials, badge keep their design side)
  const upright = (g, cx, fn) => {
    const saved = LX;
    g.save(); if (LX < 0) { g.translate(cx, 0); g.scale(-1, 1); g.translate(-cx, 0); }
    LX = 1; try { fn(); } finally { LX = saved; g.restore(); }
  };
  const devScale = g => { const m = g.getTransform(); return Math.sqrt(Math.abs(m.a * m.d - m.b * m.c)) || 1; };
  const rotAbout = (p, c, a) => { const ca = Math.cos(a), sa = Math.sin(a), dx = p[0] - c[0], dy = p[1] - c[1]; return [c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca]; };
  const add = (p, q) => [p[0] + q[0], p[1] + q[1]];
  const dirv = a => [Math.cos(a), Math.sin(a)];

  function ik2(a, b, l1, l2, bend) {
    const dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1e-6;
    const dc = clamp(d, Math.abs(l1 - l2) + 1e-3, (l1 + l2) * 0.9995);
    const base = Math.atan2(dy, dx);
    const A = Math.acos(clamp((l1 * l1 + dc * dc - l2 * l2) / (2 * l1 * dc), -1, 1));
    const ang = base - bend * A;
    const e = [a[0] + Math.cos(ang) * l1, a[1] + Math.sin(ang) * l1];
    const a2 = Math.atan2(b[1] - e[1], b[0] - e[0]);
    return { e, w: [e[0] + Math.cos(a2) * l2, e[1] + Math.sin(a2) * l2] };
  }

  // ================================================================================================= static noise
  const _noise = [];
  function noiseTile(i) {
    i = ((i % 8) + 8) % 8;
    if (_noise[i]) return _noise[i];
    const W = 96, Hh = 72, c = document.createElement('canvas'); c.width = W; c.height = Hh;
    const x = c.getContext('2d'), im = x.createImageData(W, Hh), r = S.rng(4040 + i * 17);
    for (let y = 0; y < Hh; y++) {
      const row = r() < 0.14 ? r.range(0.45, 1.5) : 1;
      for (let k = 0; k < W; k++) {
        const v = clamp(r() * 255 * row, 0, 255), j = (y * W + k) * 4;
        im.data[j] = v; im.data[j + 1] = v; im.data[j + 2] = v; im.data[j + 3] = 255;
      }
    }
    x.putImageData(im, 0, 0);
    return (_noise[i] = c);
  }
  function drawNoise(g, x, y, w, h, seed, alpha) {
    g.save(); g.globalAlpha *= alpha; g.imageSmoothingEnabled = false;
    g.drawImage(noiseTile(seed), x, y, w, h);
    g.restore();
  }

  // ================================================================================================= screen faces
  // Screen eyes: the 귤멍 recipe reduced to what reads as LIGHT on a small screen. ONE bold glowing upper-lid line with an
  // outer wing, 2 bold outer-corner lash spikes, a big SOLID iris hanging under the lid (no sclera fill, no lower-lid
  // line, no rings), a dark pupil and one 2-tone highlight (upper-left on screen).
  //   lid   lid peak height (0.05 flat .. 1 round)     iris  iris radius / eye width     show  visible part of the iris
  //   gap   iris floats this far under the lid (surprised)     tilt  + raises the outer corner     closed 'smile' | 'flat'
  const EYE_W = 0.3 * H, EYE_GAP = 0.4;
  const FACE_EYES = {
    neutral: { lid: 0.34, iris: 0.36, show: 0.6 },
    pleased: { closed: 'smile' },
    surprised: { lid: 1.0, iris: 0.25, show: 1, gap: 0.075, pupil: 'dot', lashK: 1.15 },
    annoyed: { lid: 0.06, iris: 0.34, show: 0.4, tilt: 0.2, lashK: 0.8 },
  };
  const FACE_MOUTH = { neutral: 'flat', pleased: 'smile', surprised: 'o', annoyed: 'frown' };
  const SW = 0.96 * H, SH = 0.72 * H; // screen size
  const EYE_Y = 0.03 * H, MOUTH_Y = 0.215 * H;
  const EYE_LINE = '#E6FFFA', IRIS = COL.mint, IRIS_LO = COL.line, PUPIL = '#072421';

  function glowLines(g, fn, o = {}) {
    const dev = devScale(g);
    S.glow(g, fn, { blur: (o.blur ?? 0.03) * H * dev, alpha: o.alpha ?? 0.85, bounds: { x: -SW / 2, y: -SH / 2, w: SW, h: SH }, wide: o.wide ?? true });
  }

  function bez3(P0, P1, P2, P3, n) {
    const out = [];
    for (let i = 0; i <= n; i++) {
      const t = i / n, u = 1 - t, a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
      out.push([a * P0[0] + b * P1[0] + c * P2[0] + d * P3[0], a * P0[1] + b * P1[1] + c * P2[1] + d * P3[1]]);
    }
    return out;
  }
  const yAt = (P, x) => { for (let i = 1; i < P.length; i++) { const p = P[i - 1], q = P[i]; if ((p[0] - x) * (q[0] - x) <= 0 && p[0] !== q[0]) return lerp(p[1], q[1], (x - p[0]) / (q[0] - p[0])); } return P[x < P[0][0] ? 0 : P.length - 1][1]; };
  // eye-local frame: outer corner at -x. Upper-lid curve, outer -> inner.
  function lidCurve(w, lid, open = 1) {
    const a = w / 2, O = [-a, 0.02 * w], I = [0.88 * a, 0.1 * w], top = -lid * 0.52 * w;
    const P = bez3(O, [-0.88 * a, top], [0.42 * a, top * 1.04], I, 22);
    if (open >= 1) return P;
    const shut = bez3(O, [-0.6 * a, 0.2 * w], [0.4 * a, 0.22 * w], I, 22); // where the lid lands when shut
    return P.map((p, i) => [p[0], lerp(p[1], shut[i][1], 1 - open)]);
  }
  function spike(g, base, ang, len, bw, curl) { // tapered, slightly curled lash spike
    const d = [Math.cos(ang), Math.sin(ang)], n = [-d[1], d[0]];
    const mid = [base[0] + d[0] * len * 0.55, base[1] + d[1] * len * 0.55];
    const a2 = ang + curl, tip = [mid[0] + Math.cos(a2) * len * 0.5, mid[1] + Math.sin(a2) * len * 0.5];
    g.moveTo(base[0] + n[0] * bw, base[1] + n[1] * bw);
    g.quadraticCurveTo(mid[0] + n[0] * bw * 0.5, mid[1] + n[1] * bw * 0.5, tip[0], tip[1]);
    g.quadraticCurveTo(mid[0] - n[0] * bw * 0.5, mid[1] - n[1] * bw * 0.5, base[0] - n[0] * bw, base[1] - n[1] * bw);
    g.closePath();
  }
  // lid line + wing + outer lashes along a curve P (outer -> inner), bright line colour
  function lidStroke(g, P, w, o = {}) {
    const th = (o.th ?? 0.034) * H, k = o.lashK ?? 1;
    S.strip(g, P, u => th * (u < 0.7 ? lerp(1.12, 1, u / 0.7) : lerp(1, 0.55, (u - 0.7) / 0.3)), EYE_LINE);
    const O = P[0], O2 = P[2], dx = O[0] - O2[0], dy = O[1] - O2[1], a0 = Math.atan2(dy, dx); // outward tangent at the corner
    g.fillStyle = EYE_LINE; g.beginPath();
    spike(g, O, Math.PI + 0.42, 0.25 * w * k, th * 0.62, 0.22);        // the wing: out and up from the outer corner
    [[0.1, 0.24, 0.45], [0.25, 0.18, 0.28]].forEach(([f, L, lean]) => { // two bold lash spikes leaning to the outer corner
      const i = Math.round((P.length - 1) * f), p = P[i], q = P[i + 1], ta = Math.atan2(q[1] - p[1], q[0] - p[0]);
      spike(g, p, ta - Math.PI / 2 - lean, L * w * k, th * 0.58, -0.32);
    });
    g.fill();
  }
  // one eye; returns { glow(gg), crisp(gg) } painters that set up their own local frame (outer corner at -x, mirrored
  // for the eye on the screen right). The highlight stays upper-LEFT on screen in both eyes.
  function screenEye(x, y, w, fe, look, open, mirror) {
    const hs = mirror ? -1 : 1;
    const frame = (gg, fn) => { gg.save(); gg.translate(x, y); gg.scale(hs, 1); gg.rotate(fe.tilt || 0); fn(gg); gg.restore(); };
    if (fe.closed || open < 0.12) {
      const a = w / 2, mode = fe.closed || 'flat';
      const P = mode === 'smile'
        ? bez3([-a, 0.1 * w], [-0.6 * a, -0.3 * w], [0.5 * a, -0.3 * w], [0.88 * a, 0.1 * w], 22)
        : bez3([-a, 0.08 * w], [-0.5 * a, 0.16 * w], [0.4 * a, 0.17 * w], [0.88 * a, 0.1 * w], 22);
      return { glow: gg => frame(gg, c => lidStroke(c, P, w, { lashK: 0.85 })), crisp: () => {} };
    }
    const P = lidCurve(w, fe.lid ?? 0.34, open);
    const lx = clamp(look.x, -1, 1) * hs, ly = clamp(look.y, -1, 1);
    const r = (fe.iris ?? 0.36) * w, icx = lx * 0.16 * w;
    const lidY = yAt(P, icx);
    const icy = fe.gap != null ? lidY + fe.gap * w + r + ly * 0.04 * w : lidY + (fe.show ?? 0.6) * 2 * r - r + ly * 0.06 * w;
    const below = c => { c.moveTo(P[0][0] - w, P[0][1] + 0.3 * w); c.lineTo(P[0][0], P[0][1]); P.forEach(p => c.lineTo(p[0], p[1])); c.lineTo(P[P.length - 1][0] + w, P[P.length - 1][1]); c.lineTo(w * 2, w * 3); c.lineTo(-w * 2, w * 3); c.closePath(); };
    return {
      glow: gg => frame(gg, c => {
        c.save(); c.beginPath(); below(c); c.clip();
        c.beginPath(); c.ellipse(icx, icy, r, r * 1.04, 0, 0, TAU); c.fillStyle = IRIS; c.fill();
        c.save(); c.clip(); // lower light band that bows like a smile: the 귤멍 iris gradient as two flat tones
        c.beginPath(); c.moveTo(icx - r * 1.2, icy + 0.16 * r);
        c.quadraticCurveTo(icx, icy + 0.44 * r, icx + r * 1.2, icy + 0.16 * r); c.lineTo(icx + r * 1.2, icy + r * 1.3); c.lineTo(icx - r * 1.2, icy + r * 1.3); c.closePath();
        c.fillStyle = IRIS_LO; c.fill(); c.restore();
        c.restore();
        lidStroke(c, P, w, { lashK: fe.lashK });
      }),
      crisp: gg => frame(gg, c => { // pupil + highlight over the bloom, so they stay crisp
        c.save(); c.beginPath(); below(c); c.clip();
        c.fillStyle = PUPIL; c.beginPath();
        if (fe.pupil === 'dot') c.arc(icx, icy + 0.04 * r, 0.32 * r, 0, TAU);
        else c.ellipse(icx + lx * 0.05 * r, icy - 0.02 * r, 0.36 * r, 0.52 * r, 0, 0, TAU);
        c.fill();
        const hr = (fe.pupil === 'dot' ? 0.3 : 0.25) * r, hx = icx - 0.42 * r * hs, hy = Math.max(icy - 0.34 * r, yAt(P, hx) + hr * 1.45);
        c.fillStyle = 'rgba(214,255,248,0.8)'; c.beginPath(); c.ellipse(hx, hy, hr * 1.3, hr * 1.05, -0.5 * hs, 0, TAU); c.fill();
        c.fillStyle = '#ffffff'; c.beginPath(); c.ellipse(hx - 0.14 * hr * hs, hy - 0.12 * hr, hr * 0.66, hr * 0.52, -0.5 * hs, 0, TAU); c.fill();
        c.restore();
      }),
    };
  }
  function screenEyes(g, cx, cy, fe, look, open) {
    const dx = EYE_W / 2 + EYE_GAP * EYE_W / 2;
    const eyes = [screenEye(cx - dx, cy, EYE_W, fe, look, open, false), screenEye(cx + dx, cy, EYE_W, fe, look, open, true)];
    glowLines(g, gg => eyes.forEach(e => e.glow(gg)), { blur: 0.028, alpha: 0.8 });
    eyes.forEach(e => e.crisp(g));
  }

  const MS = 1.4; // lip-sync mouths read in medium shots
  function mouthShape(g, x, y, type, k = 1) {
    g.save(); g.translate(x, y); g.scale(k * MS, k * MS);
    g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = COL.line; g.lineWidth = 0.024 * H;
    const fillDim = C.rgba(COL.mint, 0.3);
    const sk = () => g.stroke();
    switch (type) {
      case 'flat': g.beginPath(); g.moveTo(-0.05 * H, 0); g.lineTo(0.05 * H, 0); sk(); break;
      case 'frown': g.beginPath(); g.moveTo(-0.048 * H, 0.014 * H); g.quadraticCurveTo(0, -0.02 * H, 0.048 * H, 0.014 * H); sk(); break;
      case 'smile': g.beginPath(); g.moveTo(-0.05 * H, -0.012 * H); g.quadraticCurveTo(0, 0.045 * H, 0.05 * H, -0.012 * H); sk(); break;
      case 'o': g.beginPath(); g.ellipse(0, 0.012 * H, 0.03 * H, 0.05 * H, 0, 0, TAU); g.fillStyle = fillDim; g.fill(); sk(); break;
      case 'u': g.beginPath(); g.ellipse(0, 0.004 * H, 0.016 * H, 0.02 * H, 0, 0, TAU); g.fillStyle = fillDim; g.fill(); sk();
        g.lineWidth = 0.012 * H; g.beginPath(); g.moveTo(-0.036 * H, -0.008 * H); g.lineTo(-0.028 * H, 0.004 * H); g.moveTo(0.036 * H, -0.008 * H); g.lineTo(0.028 * H, 0.004 * H); sk();
        break;
      case 'wide': {
        g.beginPath(); g.moveTo(-0.058 * H, -0.02 * H); g.lineTo(0.058 * H, -0.02 * H);
        g.quadraticCurveTo(0.06 * H, 0.085 * H, 0, 0.088 * H); g.quadraticCurveTo(-0.06 * H, 0.085 * H, -0.058 * H, -0.02 * H); g.closePath();
        g.fillStyle = fillDim; g.fill(); sk();
        g.beginPath(); g.moveTo(-0.026 * H, 0.068 * H); g.quadraticCurveTo(0, 0.04 * H, 0.026 * H, 0.068 * H); g.lineWidth = 0.014 * H; sk();
        break;
      }
      case '~': case 'wave': {
        g.beginPath();
        for (let i = 0; i <= 24; i++) { const u = i / 24, X = (u - 0.5) * 0.11 * H, Y = -0.012 * H * Math.sin(u * TAU * 1.5); i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
        sk(); break;
      }
      default: break;
    }
    g.restore();
  }

  // the face proper (eyes + mouth + extras) for the four "drawn" faces; used by the slide's corner window too
  function drawDrawnFace(g, key, R, k = 1, ox = 0, oy = 0) {
    const look = R.look, blink = R.blink, ht = R.hTurn * R.hDir;
    const fe = FACE_EYES[key] || FACE_EYES.neutral;
    const lk = look ? { x: look.x, y: (look.y ?? 0) + (key === 'neutral' ? 0.2 : 0) } : { x: ht * 0.45, y: key === 'neutral' ? 0.25 : 0 };
    g.save(); g.translate(ox, oy); g.scale(k, k);
    if (key === 'pleased') { // blush dots (the only face gradient), drawn under the line art
      g.save(); g.globalCompositeOperation = 'lighter';
      S.blush(g, -0.28 * H, 0.12 * H, 0.17 * H, 0.65, COL.blush);
      S.blush(g, 0.28 * H, 0.12 * H, 0.17 * H, 0.65, COL.blush);
      g.restore();
    }
    screenEyes(g, 0.03 * H * ht, EYE_Y, fe, lk, fe.closed ? 1 : blink);
    const mType = (R.mouth && R.mouth !== 'none') ? R.mouth : FACE_MOUTH[key] || 'flat';
    glowLines(g, gg => {
      mouthShape(gg, 0.05 * H * ht, MOUTH_Y, mType);
      if (key === 'annoyed') S.anger(gg, 0.31 * H, -0.2 * H, 0.13 * H, COL.line);
    });
    g.restore();
  }

  function screenBG(g, col = COL.screen, glowA = 0.16) {
    g.fillStyle = col; g.fillRect(-SW, -SH, SW * 2, SH * 2);
    const rg = g.createRadialGradient(0, 0.02 * H, 0, 0, 0.02 * H, SW * 0.6);
    rg.addColorStop(0, C.rgba(COL.mint, glowA)); rg.addColorStop(1, C.rgba(COL.mint, 0));
    g.fillStyle = rg; g.fillRect(-SW, -SH, SW * 2, SH * 2);
  }

  function fitText(g, text, font, size, maxW) {
    let s = size;
    for (let i = 0; i < 30; i++) { g.font = font.replace('#', s.toFixed(2)); if (g.measureText(text).width <= maxW) break; s *= 0.94; }
    return s;
  }
  function wrapLines(g, words, maxW) {
    const lines = []; let cur = '';
    for (const w of words) { const tst = cur ? cur + ' ' + w : w; if (g.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst; }
    if (cur) lines.push(cur);
    return lines;
  }

  function drawFace(g, key, R) {
    const t = R.t, fr = Math.floor(t * 30);
    switch (key) {
      case 'neutral': case 'pleased': case 'surprised': case 'annoyed':
        screenBG(g); drawDrawnFace(g, key, R); break;
      case 'eerie': {
        screenBG(g, '#06201D', 0.08);
        drawNoise(g, -SW / 2, -SH / 2, SW, SH, fr, 0.34);
        g.fillStyle = 'rgba(4,20,18,0.35)'; g.fillRect(-SW / 2, -SH / 2, SW, SH);
        // slow rolling bright bar
        const ry = ((t * 0.35) % 1.4 - 0.2) * SH - SH / 2;
        const lg = g.createLinearGradient(0, ry - 0.08 * H, 0, ry + 0.08 * H);
        lg.addColorStop(0, 'rgba(180,255,240,0)'); lg.addColorStop(0.5, 'rgba(180,255,240,0.10)'); lg.addColorStop(1, 'rgba(180,255,240,0)');
        g.fillStyle = lg; g.fillRect(-SW / 2, ry - 0.08 * H, SW, 0.16 * H);
        // an over-wide smile line flickers in the static for 2 frames now and then (or always, with eerieSmile)
        const smileOn = R.eerieSmile ?? ((fr % 53) < 2);
        if (smileOn) {
          S.glow(g, gg => {
            gg.globalAlpha = 0.55;
            S.strip(gg, bez3([-0.36 * H, 0.1 * H], [-0.2 * H, 0.27 * H], [0.2 * H, 0.27 * H], [0.36 * H, 0.1 * H], 30), u => 0.016 * H * Math.sin(Math.PI * u) ** 0.4, COL.lens);
            gg.globalAlpha = 1;
          }, { blur: 0.03 * H * devScale(g), alpha: 0.6, bounds: { x: -SW / 2, y: -SH / 2, w: SW, h: SH } });
          drawNoise(g, -SW / 2, 0.12 * H, SW, 0.06 * H, fr + 5, 0.35);
        }
        // two light dots where the eyes were: not quite the same size, drifting apart very slowly
        const drift = 0.5 - 0.5 * Math.cos(TAU * t / 9);
        const gx = 0.19 * H + 0.04 * H * drift, lx = R.look ? R.look.x * 0.04 * H : 0;
        S.glow(g, gg => {
          gg.fillStyle = COL.lens;
          gg.beginPath(); gg.arc(-gx + lx, EYE_Y - 0.004 * H, 0.03 * H, 0, TAU); gg.fill();
          gg.beginPath(); gg.arc(gx + lx + 0.01 * H * drift, EYE_Y + 0.012 * H, 0.021 * H, 0, TAU); gg.fill();
        }, { blur: 0.05 * H * devScale(g), alpha: 1, bounds: { x: -SW / 2, y: -SH / 2, w: SW, h: SH } });
        break;
      }
      case 'panic': {
        const jx = 0.012 * H * Math.sin(fr * 2.7) * (fr % 2 ? 1 : -1);
        g.save(); g.translate(jx, 0);
        const top = ['#D6D6D6', '#E2D24A', '#4FCFD2', '#5BC85E', '#CF5FC6', '#DE524F', '#4A5AD0'];
        const mid = ['#4A5AD0', '#16141A', '#CF5FC6', '#16141A', '#4FCFD2', '#16141A', '#D6D6D6'];
        const bw = SW / 7, x0 = -SW / 2 - 0.02 * H;
        top.forEach((c, i) => { g.fillStyle = c; g.fillRect(x0 + i * bw, -SH / 2 - 2, bw + 1, SH * 0.66 + 2); });
        mid.forEach((c, i) => { g.fillStyle = c; g.fillRect(x0 + i * bw, -SH / 2 + SH * 0.66, bw + 1, SH * 0.09); });
        const bot = [['#1E2F5E', 1.25], ['#F2F2F2', 1.25], ['#3A1F66', 1.25], ['#16141A', 2.0], ['#0E0D12', 0.42], ['#16141A', 0.41], ['#26242C', 0.42]];
        let bx = x0;
        bot.forEach(([c, wv]) => { g.fillStyle = c; g.fillRect(bx, -SH / 2 + SH * 0.75, bw * wv + 1, SH * 0.3); bx += bw * wv; });
        g.restore();
        // tear line
        const ty = (SH * ((fr * 0.37) % 1)) - SH / 2;
        g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(-SW / 2, ty, SW, 0.012 * H);
        break;
      }
      case 'thinking': {
        screenBG(g, COL.screen, 0.12);
        const n = 8, r = 0.15 * H, head = Math.floor(t * 9) % n;
        glowLines(g, gg => {
          for (let i = 0; i < n; i++) {
            const a = -Math.PI / 2 + (i / n) * TAU, age = (head - i + n) % n, k = Math.max(0.18, 1 - age / 5);
            gg.globalAlpha = k; gg.fillStyle = COL.line;
            gg.beginPath(); gg.arc(Math.cos(a) * r, -0.005 * H + Math.sin(a) * r, 0.03 * H * (0.65 + 0.35 * k), 0, TAU); gg.fill();
          }
          gg.globalAlpha = 1;
        });
        break;
      }
      case 'number': {
        screenBG(g, COL.screen, 0.14);
        const txt = String(R.number ?? '9.9');
        glowLines(g, gg => {
          gg.fillStyle = COL.line; gg.textAlign = 'center'; gg.textBaseline = 'middle';
          const lab = R.numberLabel;
          const sz = fitText(gg, txt, '600 #px Fredoka', 0.42 * H, SW * 0.8);
          gg.font = `600 ${sz}px Fredoka`;
          gg.fillText(txt, 0, lab ? 0.07 * H : 0.03 * H);
          if (lab) { gg.font = `800 ${0.075 * H}px Nunito`; try { gg.letterSpacing = `${0.01 * H}px`; } catch (e) { /**/ } gg.fillText(lab, 0, -0.2 * H); }
        }, { blur: 0.035 });
        break;
      }
      case 'slide': {
        const sl = R.slide || {};
        g.fillStyle = '#EAE3D4'; g.fillRect(-SW, -SH, SW * 2, SH * 2);
        // mint header band
        const hb = SH * 0.25;
        g.fillStyle = COL.mint; g.fillRect(-SW, -SH / 2 - 2, SW * 2, hb + 2);
        g.fillStyle = COL.mintShade; g.fillRect(-SW, -SH / 2 + hb, SW * 2, 0.018 * H);
        g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillStyle = '#ffffff'; g.font = `${0.115 * H}px Anton`;
        try { g.letterSpacing = `${0.012 * H}px`; } catch (e) { /**/ }
        g.fillText(`RULE ${sl.n ?? 10}`, 0, -SH / 2 + hb * 0.55);
        try { g.letterSpacing = '0px'; } catch (e) { /**/ }
        // rule text: wrapped, lines that reach the face window (bottom-right) are kept short of it
        const text = (sl.text || 'WHEN THEY KNOCK, OPEN WIDE.').toUpperCase();
        const fw = SW * 0.27, fh = SH * 0.33, fx = SW / 2 - fw - 0.04 * H, fy = SH / 2 - fh - 0.035 * H;
        const ax = -SW / 2 + 0.07 * H, ay = -SH / 2 + hb + 0.05 * H, aw = SW - 0.14 * H, ah = SH / 2 - 0.05 * H - ay;
        const words = text.split(/\s+/);
        let size = 0.15 * H, lines = [];
        for (let it = 0; it < 30; it++) {
          g.font = `${size}px Anton`; lines = []; let cur = '', li = 0, ok = true;
          const maxW = i => (ay + (i + 1) * size * 1.06 > fy - 0.01 * H ? fx - ax - 0.04 * H : aw);
          for (const w of words) {
            const tst = cur ? cur + ' ' + w : w;
            if (g.measureText(tst).width > maxW(li) && cur) { lines.push(cur); li++; cur = w; } else cur = tst;
            if (g.measureText(cur).width > maxW(li)) ok = false;
          }
          if (cur) lines.push(cur);
          if (ok && lines.length * size * 1.06 <= ah) break;
          size *= 0.94;
        }
        g.fillStyle = COL.ink; g.textAlign = 'left';
        lines.forEach((ln, i) => g.fillText(ln, ax, ay + size * 0.53 + i * size * 1.06));
        // face window bottom-right
        S.roundRect(g, fx - 0.012 * H, fy - 0.012 * H, fw + 0.024 * H, fh + 0.024 * H, 0.03 * H, COL.bezel);
        g.save(); g.beginPath(); S.addRoundRect(g, fx, fy, fw, fh, 0.022 * H); g.clip();
        g.translate(fx + fw / 2, fy + fh / 2);
        screenBG(g, COL.screen, 0.12);
        drawDrawnFace(g, 'neutral', Object.assign({}, R, { turn: 0 }), 0.29, 0, -0.012 * H);
        g.restore();
        break;
      }
      case 'off': {
        const k = clamp(R.offK ?? 1);
        g.fillStyle = '#0B1A19'; g.fillRect(-SW, -SH, SW * 2, SH * 2);
        if (k < 1) {
          const bright = C.mix(COL.lens, '#ffffff', 0.4);
          let w = SW, h = SH, a = 1;
          if (k < 0.45) { const q = S.ease.easeInCubic(k / 0.45); h = lerp(SH, 0.014 * H, q); }
          else if (k < 0.8) { const q = S.ease.easeInOutCubic((k - 0.45) / 0.35); h = 0.014 * H + q * 0.03 * H; w = lerp(SW, 0.045 * H, q); }
          else { w = 0.045 * H; h = 0.045 * H; a = 1 - (k - 0.8) / 0.2; }
          S.glow(g, gg => {
            gg.globalAlpha = a; gg.fillStyle = bright;
            if (w < 0.06 * H) { gg.beginPath(); gg.arc(0, 0, w / 2, 0, TAU); gg.fill(); }
            else S.roundRect(gg, -w / 2, -h / 2, w, h, Math.min(h / 2, 0.06 * H), bright);
          }, { blur: 0.05 * H * devScale(g), alpha: 0.9 * a, bounds: { x: -SW / 2, y: -SH / 2, w: SW, h: SH } });
        }
        break;
      }
      case 'error404': {
        screenBG(g, '#0A2522', 0.08);
        drawNoise(g, -SW / 2, -SH / 2, SW, SH, fr + 3, 0.12);
        const sz = 0.36 * H, ty = -0.02 * H;
        g.save();
        g.font = `600 ${sz}px Fredoka`; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.globalCompositeOperation = 'lighter';
        g.fillStyle = 'rgba(255,70,100,0.75)'; g.fillText('404', -0.022 * H, ty);
        g.fillStyle = 'rgba(70,240,255,0.75)'; g.fillText('404', 0.022 * H, ty);
        g.restore();
        glowLines(g, gg => {
          gg.font = `600 ${sz}px Fredoka`; gg.textAlign = 'center'; gg.textBaseline = 'middle'; gg.fillStyle = COL.lens;
          const slices = [[-0.5, -0.12, 0], [-0.12, -0.04, 0.05], [-0.04, 0.07, -0.03], [0.07, 0.5, 0]];
          slices.forEach(([a, b, dx]) => {
            gg.save(); gg.beginPath(); gg.rect(-SW / 2, ty + a * sz * 1.6, SW, (b - a) * sz * 1.6); gg.clip();
            gg.fillText('404', dx * H, ty); gg.restore();
          });
          gg.font = `800 ${0.07 * H}px Nunito`; try { gg.letterSpacing = `${0.02 * H}px`; } catch (e) { /**/ }
          gg.fillText('ERROR', 0, 0.245 * H);
        }, { blur: 0.03 });
        // glitch bands
        const r = S.rng(900 + (fr % 7));
        for (let i = 0; i < 3; i++) {
          const y = r.range(-0.5, 0.5) * SH, h = r.range(0.01, 0.035) * H;
          drawNoise(g, -SW / 2, y, SW, h, fr + i, 0.5);
        }
        break;
      }
      default: screenBG(g); drawDrawnFace(g, 'neutral', R);
    }
  }

  function screenPath(c, x, y, w, h, r, b) { // rounded rect whose straight edges bow OUT by b (convex CRT glass)
    c.moveTo(x + r, y);
    c.quadraticCurveTo(x + w / 2, y - b, x + w - r, y);
    c.quadraticCurveTo(x + w, y, x + w, y + r);
    c.quadraticCurveTo(x + w + b, y + h / 2, x + w, y + h - r);
    c.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    c.quadraticCurveTo(x + w / 2, y + h + b, x + r, y + h);
    c.quadraticCurveTo(x, y + h, x, y + h - r);
    c.quadraticCurveTo(x - b, y + h / 2, x, y + r);
    c.quadraticCurveTo(x, y, x + r, y);
    c.closePath();
  }

  function drawScreen(g, R, cx, cy, fs) {
    g.save();
    g.translate(cx, cy); g.scale(fs * LX, 1); // undo the rig mirror (text reads), squash for the 3/4 turn
    g.beginPath(); screenPath(g, -SW / 2, -SH / 2, SW, SH, 0.1 * H, 0.022 * H); g.clip();
    const key = R.faceKey;
    if (R.wipe != null && R.wipe > 0 && R.wipe < 1 && R.prevFace) {
      const bandH = SH * 0.42, yb = lerp(-SH / 2 - bandH / 2, SH / 2 + bandH / 2, R.wipe);
      g.save(); g.beginPath(); g.rect(-SW, -SH, SW * 2, SH / 2 + yb - bandH / 2 + SH / 2); g.clip(); drawFace(g, key, R); g.restore();
      g.save(); g.beginPath(); g.rect(-SW, yb + bandH / 2, SW * 2, SH * 2); g.clip(); drawFace(g, R.prevFace, Object.assign({}, R, { mouth: null })); g.restore();
      g.save(); g.beginPath(); g.rect(-SW, yb - bandH / 2, SW * 2, bandH); g.clip();
      g.fillStyle = '#1b2b2a'; g.fillRect(-SW, -SH, SW * 2, SH * 2);
      drawNoise(g, -SW / 2 - 0.03 * H, yb - bandH / 2, SW + 0.06 * H, bandH, Math.floor(R.wipe * 7) + 2, 0.85);
      g.fillStyle = 'rgba(230,255,250,0.55)'; g.fillRect(-SW, yb + bandH / 2 - 0.012 * H, SW * 2, 0.012 * H);
      g.restore();
    } else drawFace(g, key, R);
    // CRT finish: scanlines, edge falloff, glass glare (top-left, the key light)
    const gap = Math.max(6 / devScale(g), 0.04 * H);
    S.scanlines(g, -SW / 2, -SH / 2 - 2, SW, SH + 4, gap, key === 'slide' ? 0.1 : 0.15, '#000');
    const vg = g.createRadialGradient(0, 0, SH * 0.32, 0, 0, SW * 0.66);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, key === 'slide' ? 'rgba(20,10,30,0.28)' : 'rgba(0,0,0,0.42)');
    g.fillStyle = vg; g.fillRect(-SW, -SH, SW * 2, SH * 2);
    g.save();
    g.fillStyle = 'rgba(255,255,255,0.07)';
    g.beginPath(); g.ellipse(-0.16 * SW, -0.3 * SH, 0.42 * SW, 0.2 * SH, -0.12, 0, TAU); g.fill();
    g.strokeStyle = 'rgba(255,255,255,0.34)'; g.lineCap = 'round';
    g.lineWidth = 0.028 * H; g.beginPath(); g.moveTo(-0.39 * SW, -0.2 * SH); g.lineTo(-0.3 * SW, -0.36 * SH); g.stroke();
    g.lineWidth = 0.016 * H; g.beginPath(); g.moveTo(-0.33 * SW, -0.12 * SH); g.lineTo(-0.27 * SW, -0.23 * SH); g.stroke();
    g.restore();
    g.restore();
  }

  // ================================================================================================= antennae
  function antennaParams(R, sd) {
    const t = R.t, aT = R.antT, f = R.faceKey;
    let th = 25, bend = 0.15, sway = 0.035, swayF = 0.42, nod = 0;
    switch (f) {
      case 'pleased': th = 13; bend = -0.25; break;
      case 'surprised': th = 34; bend = 0.0; break;
      case 'annoyed': th = -34; bend = 0.12; sway = 0.008; break;
      case 'eerie': th = 21; bend = 0; sway = 0; break;
      case 'panic': th = 29; bend = 0.2; break;
      case 'thinking': th = 25; nod = 0.18 * Math.sin(TAU * 0.4 * t); break;
      case 'off': // limp and asymmetric: each rod flops forward over its top corner, tips at different heights
        th = sd < 0 ? 128 : 78; bend = sd < 0 ? 0.35 : 1.25; sway = 0.006; break;
      case 'error404': th = 3; bend = 0; sway = 0; break;
      default: break;
    }
    if (R.antenna) { if (R.antenna.ang != null) th = R.antenna.ang; if (R.antenna.bend != null) bend = R.antenna.bend; if (R.antenna.still) sway = 0; }
    let a = th * RAD + sway * Math.sin(TAU * swayF * t + (sd > 0 ? 0.9 : 0));
    if (f === 'panic') a += 0.07 * Math.sin(TAU * 17 * t + sd * 1.3) + 0.04 * Math.sin(TAU * 23 * t);
    const kick = aT != null ? S.wobble(aT, 2.4, 3.0) : 0;
    const kickLag = aT != null ? S.wobble(aT - 0.05, 2.4, 3.0) : 0;
    a += 0.32 * kick;
    bend += -1.1 * kickLag + (R.walkBounce || 0);
    return { a: sd * a + nod, bend: sd * bend };
  }
  function antennaPoints(base, ang, bend, len, n = 14) {
    const pts = [base.slice()];
    let p = base.slice();
    for (let i = 1; i <= n; i++) {
      const u = (i - 0.5) / n, a = ang + bend * u;
      p = [p[0] + Math.sin(a) * len / n, p[1] - Math.cos(a) * len / n];
      pts.push(p);
    }
    return pts;
  }
  function drawAntennae(g, R, cx, topY) {
    const len = 0.45 * H;
    R.tips = [];
    [-1, 1].forEach(sd => {
      const { a, bend } = antennaParams(R, sd);
      const pts = antennaPoints([cx + sd * 0.15 * H, topY + 0.02 * H], a, bend, len);
      S.strip(g, pts, u => lerp(0.034, 0.022, u) * H, COL.ant);
      const tip = pts[pts.length - 1];
      cel(g, c => c.arc(tip[0], tip[1], 0.042 * H, 0, TAU), COL.ball, COL.ballShade, 0.016);
      R.tips.push(tip);
    });
  }

  // ================================================================================================= head
  function drawHeadLocal(g, R) {
    const ang = 35 * RAD * R.hTurn, fs = Math.cos(ang), d = 0.35 * H * Math.sin(ang);
    const cw = 1.3 * H * fs, x0 = -(cw + d) / 2 + d, fcx = x0 + cw / 2, top = -H;
    // neck mount (a little grey swivel under the case)
    cel(g, c => S.addRoundRect(c, fcx - d * 0.35 - 0.085 * H, -0.04 * H, 0.17 * H, 0.1 * H, 0.03 * H), COL.grey, COL.greyShade, 0.02);
    if (R.faceKey !== 'off') drawAntennae(g, R, fcx - d * 0.45, top);
    // side panel: the near side shows when the head turns (tapers toward the back like a CRT)
    if (d > 0.5) {
      const bx = x0 - d, lit = LX > 0; // the side panel faces the top-left key light only when it is on the screen left
      const sideC = lit ? COL.caseSideLit : COL.caseSide, sideS = lit ? COL.caseSideLitShade : COL.caseSideShade;
      cel(g, c => S.addRoundPoly(c, [[x0 + 0.2 * H, top], [bx, top + 0.075 * H], [bx, -0.06 * H], [x0 + 0.2 * H, 0]], [0, 0.07 * H, 0.06 * H, 0]), sideC, sideS, 0.04);
      for (let i = 0; i < 4; i++) S.roundRect(g, bx + d * 0.25, top + 0.3 * H + i * 0.07 * H, d * 0.5, 0.022 * H, 0.011 * H, lit ? COL.caseSideShade : COL.caseSideShade);
    }
    // case front
    cel(g, c => S.addRoundRect(c, x0, top, cw, H, 0.15 * H), COL.case, COL.caseShade, 0.055);
    // antenna base pill on top
    const pb = fcx - d * 0.45;
    cel(g, c => S.addRoundRect(c, pb - 0.24 * H, top - 0.06 * H, 0.48 * H, 0.09 * H, 0.045 * H), COL.grey, COL.greyShade, 0.022);
    // screen recess: inset wall (shade) + dark bezel lip
    const sx = x0 + 0.17 * H * fs, sy = top + 0.1 * H, sw = 0.96 * H * fs, sh = 0.72 * H;
    S.roundRect(g, sx - 0.04 * H * fs, sy - 0.04 * H, sw + 0.08 * H * fs, sh + 0.08 * H, 0.13 * H, COL.caseShade);
    S.roundRect(g, sx - 0.022 * H * fs, sy - 0.022 * H, sw + 0.044 * H * fs, sh + 0.044 * H, 0.11 * H, COL.bezel);
    R.screenLocal = [sx + sw / 2, sy + sh / 2];
    drawScreen(g, R, sx + sw / 2, sy + sh / 2, fs);
    // bottom bezel: speaker grille (left) + two dials (right), kept on their design side when mirrored
    upright(g, fcx, () => {
    for (let i = 0; i < 3; i++) S.roundRect(g, x0 + 0.2 * H * fs, -0.112 * H + i * 0.03 * H, 0.27 * H * fs, 0.014 * H, 0.007 * H, COL.grille);
    const dial = (x, col, shade, a) => {
      cel(g, c => c.ellipse(x, -0.075 * H, 0.045 * H * fs, 0.045 * H, 0, 0, TAU), col, shade, 0.014);
      g.save(); g.translate(x, -0.075 * H); g.scale(fs, 1); g.rotate(a);
      g.fillStyle = C.shade(shade, -0.35); g.fillRect(-0.006 * H, -0.04 * H, 0.012 * H, 0.03 * H);
      g.restore();
    };
    const off = R.faceKey === 'off' && (R.offK ?? 1) >= 1;
    dial(x0 + cw - 0.42 * H * fs, COL.mint, COL.mintShade, off ? -0.9 : 0.6);
    dial(x0 + cw - 0.25 * H * fs, COL.grey, COL.greyShade, -0.4);
    });
    if (R.faceKey === 'off') drawAntennae(g, R, fcx - d * 0.45, top); // limp rods flop forward over the top corners
    // little extras
    if (R.faceKey === 'surprised' && R.tips) R.tips.forEach((p, i) => S.sparkle(g, p[0] + (i ? 0.07 : -0.07) * H, p[1] - 0.06 * H, 0.05 * H, '#FFF6D8', 0.2));
    if (R.faceKey === 'panic' || R.sweat) S.sweat(g, x0 + cw + 0.05 * H, top + 0.2 * H, 0.17 * H, { angle: 0.25 });
    return { fs, d, cw, x0, fcx };
  }

  // ================================================================================================= props
  function drawRemoteLocal(g, ang, press) { // origin = grip point, ang = pointing direction
    g.save(); g.rotate(ang);
    const L0 = -0.1 * H, L1 = 0.27 * H, w = 0.085 * H;
    cel(g, c => S.addRoundRect(c, L0, -w / 2, L1 - L0, w, 0.035 * H), COL.remote, COL.remoteShade, 0.014);
    // keys: red button near the front, small grey keys behind it, IR lens at the tip
    g.fillStyle = COL.remoteKey;
    [[0.06, -0.013], [0.06, 0.013], [0.1, -0.013], [0.1, 0.013]].forEach(([x, y]) => { g.beginPath(); g.arc(x * H, y * H, 0.0075 * H, 0, TAU); g.fill(); });
    cel(g, c => c.arc(0.19 * H, 0, 0.022 * H * (press ? 0.85 : 1), 0, TAU), COL.red, COL.redShade, 0.007);
    if (press) { g.fillStyle = 'rgba(255,120,120,0.35)'; g.beginPath(); g.arc(0.19 * H, 0, 0.04 * H, 0, TAU); g.fill(); }
    g.fillStyle = '#4b4453'; S.roundRect(g, L1 - 0.022 * H, -w * 0.32, 0.016 * H, w * 0.64, 0.006 * H, '#4b4453');
    g.restore();
  }
  function drawStampLocal(g, tilt = 0) { // origin = grip point (neck), pad hangs down. tilt: shows the rubber face
    cel(g, c => c.ellipse(0, -0.1 * H, 0.075 * H, 0.062 * H, 0, 0, TAU), COL.wood, COL.woodShade, 0.02);
    S.roundRect(g, -0.03 * H, -0.06 * H, 0.06 * H, 0.17 * H, 0.02 * H, COL.woodShade);
    const fh = 0.03 * H + 0.05 * H * clamp(Math.abs(tilt) / 0.35); // the red face foreshortens open as the stamp tips
    S.roundRect(g, -0.12 * H, 0.165 * H, 0.24 * H, fh, Math.min(fh / 2, 0.02 * H), COL.red);
    if (fh > 0.04 * H) S.roundRect(g, -0.1 * H, 0.165 * H + fh * 0.35, 0.2 * H, fh * 0.3, fh * 0.15, COL.redShade);
    cel(g, c => S.addRoundRect(c, -0.13 * H, 0.1 * H, 0.26 * H, 0.075 * H, 0.018 * H), COL.bezel, COL.shoeShade, 0.016);
  }
  function stampMark(g, w, text, alpha = 0.92) {
    const red = COL.stamp;
    g.save();
    g.globalAlpha *= alpha;
    const sz = fitText(g, text, '#px BlackOps', 0.12 * H, w * 0.82);
    g.font = `${sz}px BlackOps`;
    const tw = g.measureText(text).width, bw = tw + sz * 0.7, bh = sz * 1.45;
    g.strokeStyle = red; g.lineWidth = sz * 0.13; g.lineJoin = 'round';
    g.beginPath(); S.addRoundRect(g, -bw / 2, -bh / 2, bw, bh, sz * 0.25); g.stroke();
    g.fillStyle = red; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, 0, sz * 0.04);
    // dry-ink speckle
    g.globalCompositeOperation = 'destination-out';
    const r = S.rng('ink' + text);
    for (let i = 0; i < 26; i++) { g.beginPath(); g.arc(r.range(-bw / 2, bw / 2), r.range(-bh / 2, bh / 2), r.range(0.003, 0.009) * H, 0, TAU); g.fill(); }
    g.restore();
  }
  function drawClipboardLocal(g, o = {}) { // origin = board centre
    const w = 0.56 * H, h = 0.74 * H;
    cel(g, c => S.addRoundRect(c, -w / 2, -h / 2, w, h, 0.045 * H), COL.board, COL.boardShade, 0.03);
    const px = -w / 2 + 0.045 * H, py = -h / 2 + 0.085 * H, pw = w - 0.09 * H, ph = h - 0.125 * H;
    S.roundRect(g, px + 0.012 * H, py + 0.012 * H, pw, ph, 0.012 * H, 'rgba(40,30,50,0.25)');
    S.roundRect(g, px, py, pw, ph, 0.012 * H, COL.paper);
    // paper content: ID photo of the new hire (a tiny chest), title bar, lines, check boxes
    S.roundRect(g, px + 0.035 * H, py + 0.07 * H, 0.13 * H, 0.11 * H, 0.012 * H, COL.wood);
    S.roundRect(g, px + 0.035 * H, py + 0.07 * H, 0.13 * H, 0.035 * H, [0.012 * H, 0.012 * H, 0, 0], COL.woodShade);
    g.fillStyle = '#2A1416'; g.fillRect(px + 0.05 * H, py + 0.112 * H, 0.1 * H, 0.012 * H);
    g.fillStyle = 'rgba(42,34,48,0.75)'; g.fillRect(px + 0.2 * H, py + 0.075 * H, 0.18 * H, 0.022 * H);
    g.fillStyle = COL.paperLine;
    for (let i = 0; i < 2; i++) g.fillRect(px + 0.2 * H, py + 0.125 * H + i * 0.035 * H, 0.2 * H - i * 0.05 * H, 0.014 * H);
    for (let i = 0; i < 4; i++) {
      const y = py + 0.24 * H + i * 0.075 * H;
      g.strokeStyle = COL.paperLine; g.lineWidth = 0.012 * H; g.strokeRect(px + 0.04 * H, y, 0.04 * H, 0.04 * H);
      g.fillRect(px + 0.11 * H, y + 0.013 * H, pw - 0.16 * H - (i % 2) * 0.06 * H, 0.014 * H);
      if (i < 2) { g.strokeStyle = 'rgba(42,34,48,0.7)'; g.lineWidth = 0.013 * H; g.beginPath(); g.moveTo(px + 0.045 * H, y + 0.02 * H); g.lineTo(px + 0.06 * H, y + 0.035 * H); g.lineTo(px + 0.088 * H, y - 0.005 * H); g.stroke(); }
    }
    if (o.mark) { g.save(); g.translate(0.005 * H, 0.1 * H); g.rotate(-0.2); stampMark(g, pw * 1.18, o.mark); g.restore(); }
    // clip
    cel(g, c => S.addRoundRect(c, -0.15 * H, -h / 2 - 0.035 * H, 0.3 * H, 0.11 * H, 0.03 * H), COL.clip, COL.clipShade, 0.018);
    S.roundRect(g, -0.06 * H, -h / 2 - 0.06 * H, 0.12 * H, 0.05 * H, 0.025 * H, COL.clipShade);
    g.fillStyle = C.shade(COL.clipShade, -0.3); g.beginPath(); g.arc(0, -h / 2 + 0.02 * H, 0.016 * H, 0, TAU); g.fill();
  }

  function drawBadgeLocal(g, R) { // origin = clip point; card hangs below
    const w = 0.24 * H, h = 0.31 * H;
    S.roundRect(g, -0.03 * H, -0.02 * H, 0.06 * H, 0.05 * H, 0.012 * H, COL.clip);
    cel(g, c => S.addRoundRect(c, -w / 2, 0.02 * H, w, h, 0.03 * H), COL.badge, '#D9D2C4', 0.014);
    S.roundRect(g, -w / 2, 0.02 * H, w, 0.075 * H, [0.03 * H, 0.03 * H, 0, 0], COL.mint);
    S.roundRect(g, -0.035 * H, 0.04 * H, 0.07 * H, 0.016 * H, 0.008 * H, COL.mintShade);
    // tiny TV-head ID photo
    S.roundRect(g, -w / 2 + 0.025 * H, 0.115 * H, 0.085 * H, 0.08 * H, 0.012 * H, COL.case);
    S.roundRect(g, -w / 2 + 0.035 * H, 0.125 * H, 0.065 * H, 0.048 * H, 0.008 * H, COL.screen);
    g.fillStyle = COL.line; g.fillRect(-w / 2 + 0.048 * H, 0.143 * H, 0.012 * H, 0.008 * H); g.fillRect(-w / 2 + 0.075 * H, 0.143 * H, 0.012 * H, 0.008 * H);
    // text: HELEN / HR MANAGER (bars when too small to read)
    const dev = devScale(g);
    g.save();
    if (0.06 * H * dev >= 5) {
      g.fillStyle = COL.ink; g.textAlign = 'left'; g.textBaseline = 'middle';
      g.font = `700 ${0.052 * H}px Courier`; g.fillText('HELEN', -w / 2 + 0.12 * H, 0.158 * H, w * 0.48);
      g.fillStyle = COL.paperLine; g.fillRect(-w / 2 + 0.03 * H, 0.215 * H, w - 0.06 * H, 0.008 * H);
      g.fillStyle = COL.ink; g.textAlign = 'center'; g.font = `700 ${0.034 * H}px Courier`; g.fillText('HR MANAGER', 0, 0.258 * H, w * 0.86);
      if (0.03 * H * dev >= 6) { g.fillStyle = '#ffffff'; g.font = `800 ${0.026 * H}px Nunito`; g.fillText('MONSTER HR', 0, 0.083 * H, w * 0.8); }
    } else {
      g.fillStyle = 'rgba(42,34,48,0.7)'; g.fillRect(-w / 2 + 0.12 * H, 0.13 * H, 0.09 * H, 0.025 * H);
      g.fillStyle = COL.paperLine; g.fillRect(-w / 2 + 0.03 * H, 0.235 * H, w - 0.06 * H, 0.02 * H);
    }
    g.restore();
  }

  // ================================================================================================= hands
  // local frame: origin at the wrist, +x along the hand. ts = thumb side (+1 / -1 in local y).
  function drawHandLocal(g, type, ts = -1, pal = null) {
    const sk = pal ? pal.sk : COL.skin, sh = pal ? pal.sh : COL.skinShade, k = 0.018;
    switch (type) {
      case 'fist': case 'remote': case 'stamp': case 'grip':
        celU(g, c => { S.addRoundRect(c, -0.01 * H, -0.075 * H, 0.17 * H, 0.15 * H, 0.06 * H); }, sk, sh, k);
        cel(g, c => S.addCapsule(c, 0.03 * H, ts * 0.06 * H, 0.12 * H, ts * 0.03 * H, 0.055 * H, 0.05 * H), sk, sh, 0.01);
        g.fillStyle = sh; g.fillRect(0.125 * H, -0.045 * H, 0.012 * H, 0.09 * H);
        break;
      case 'point':
        celU(g, c => { S.addRoundRect(c, -0.01 * H, -0.07 * H, 0.16 * H, 0.14 * H, 0.06 * H); S.addCapsule(c, 0.1 * H, -ts * 0.035 * H, 0.3 * H, -ts * 0.045 * H, 0.055 * H, 0.048 * H); }, sk, sh, k);
        cel(g, c => S.addCapsule(c, 0.03 * H, ts * 0.06 * H, 0.12 * H, ts * 0.035 * H, 0.055 * H, 0.05 * H), sk, sh, 0.01);
        break;
      case 'open':
        celU(g, c => {
          S.addRoundRect(c, -0.01 * H, -0.075 * H, 0.18 * H, 0.15 * H, 0.06 * H);
          [-0.045, 0, 0.045].forEach((y, i) => S.addCapsule(c, 0.12 * H, y * H, 0.29 * H - Math.abs(i - 1) * 0.03 * H, y * 1.5 * H, 0.055 * H, 0.048 * H));
          S.addCapsule(c, 0.04 * H, ts * 0.06 * H, 0.14 * H, ts * 0.13 * H, 0.055 * H, 0.048 * H);
        }, sk, sh, k);
        break;
      case 'clip': // back of the hand, fingers wrapped over a board edge
        celU(g, c => { S.addRoundRect(c, -0.01 * H, -0.072 * H, 0.17 * H, 0.144 * H, 0.06 * H); S.addCapsule(c, 0.11 * H, 0.0, 0.19 * H, ts * -0.012 * H, 0.13 * H, 0.11 * H); }, sk, sh, k);
        g.fillStyle = sh; g.fillRect(0.13 * H, -0.05 * H, 0.011 * H, 0.085 * H); g.fillRect(0.175 * H, -0.045 * H, 0.011 * H, 0.075 * H);
        cel(g, c => S.addCapsule(c, 0.045 * H, ts * 0.06 * H, 0.125 * H, ts * 0.082 * H, 0.062 * H, 0.054 * H), sk, sh, 0.01); // thumb on the board front
        break;
      default: // relaxed mitten, fingers curl slightly to the palm side
        celU(g, c => {
          S.addRoundRect(c, -0.01 * H, -0.072 * H, 0.2 * H, 0.144 * H, 0.06 * H);
          S.addCapsule(c, 0.14 * H, -ts * 0.005 * H, 0.27 * H, -ts * 0.03 * H, 0.13 * H, 0.1 * H);
        }, sk, sh, k);
        cel(g, c => S.addCapsule(c, 0.04 * H, ts * 0.06 * H, 0.15 * H, ts * 0.075 * H, 0.055 * H, 0.048 * H), sk, sh, 0.01);
    }
  }

  // ================================================================================================= pose solve
  // canonical body space (H units): ground y = 0, up is negative, facing +x when turned; "near" = her right arm
  // hugged clipboard: the far forearm crosses the board and the fingers wrap its LEFT edge (thumb bump in front).
  // At runtime the board and that hand slide right by HUG_SEP (and the badge left) so the badge always shows.
  const CLIP_ARM = { wrist: [0.25, -2.42], bend: 1, hand: 'clip', handAng: 188, hug: true };
  const CLIP_HUG = { at: [0.28, -2.58], rot: -6 };
  const HUG_SEP = tn => 0.06 - 0.02 * tn, BADGE_SEP = tn => -0.05 - 0.05 * tn;
  const POSE_DEF = {
    'stand': {
      near: { wrist: [-0.5, -1.9], bend: -1, hand: 'relax', handAng: 96 },
      far: { wrist: [0.5, -1.9], bend: 1, hand: 'relax', handAng: 84 },
      weight: 1,
    },
    'idle-clipboard': {
      near: { wrist: [-0.47, -1.9], bend: -1, hand: 'remote', handAng: 94, rAng: 112 },
      far: CLIP_ARM, clip: CLIP_HUG, weight: 1,
    },
    'idle-hip': { // remote hand on the hip, elbow out: the hero / "listening" pose
      near: { wrist: [-0.43, -2.2], bend: -1, hand: 'remote', handAng: 18, rAng: 104 },
      far: CLIP_ARM, clip: CLIP_HUG, weight: 1, headTilt: 6,
    },
    'remote-at-head': {
      near: { wrist: [-1.06, -3.5], bend: 1, hand: 'remote', handAng: -78, rAng: -16, press: true, signal: true, thumb: 1 },
      far: CLIP_ARM, clip: CLIP_HUG, headTilt: 4, weight: 1,
    },
    'present-point': { // the head turns toward the pointing hand (headTurn < 0 = toward body -x)
      near: { wrist: [-1.5, -3.0], bend: 1, hand: 'remote', handAng: 186, rAng: 190 },
      far: CLIP_ARM, clip: CLIP_HUG,
      lean: -2, headTilt: -6, headTurn: -0.7, weight: 1,
    },
    'stamp': { // stampK 0 raised .. 1 on the paper. The near arm is FK-swung from upFK [upper-arm deg, forearm deg] to the
      // IK solution on `wrist` (elbow OUT, screen-left): the upper arm drops through the left side, the forearm chops down.
      near: { wrist: [-0.11, -2.235], upFK: [-135, -95], elbowOut: true, hand: 'stamp', upHand: 202, tilt: 0.36 },
      far: { wrist: [0.45, -1.86], bend: 1, hand: 'clip', handAng: 206 },
      clip: { at: [-0.02, -2.08], rot: 0, flat: 0.9, scale: 1.12 },
    },
    'walk': {
      near: { wrist: [-0.46, -1.92], bend: -1, hand: 'remote', handAng: 94, rAng: 112 },
      far: CLIP_ARM, clip: CLIP_HUG,
    },
  };
  POSE_DEF['idle'] = POSE_DEF['idle-clipboard'];
  POSE_DEF['hand-on-hip'] = POSE_DEF['idle-hip'];
  POSE_DEF['remote'] = POSE_DEF['remote-at-head'];
  POSE_DEF['present'] = POSE_DEF['present-point'];
  POSE_DEF['point'] = POSE_DEF['present-point'];

  // both two-bone solutions (bend +1 / -1)
  function ik2pick(a, b, l1, l2, pick) {
    const s1 = ik2(a, b, l1, l2, 1), s2 = ik2(a, b, l1, l2, -1);
    return pick(s1.e, s2.e) ? s1 : s2;
  }

  // walk: one leg at cycle position u (0 contact with the foot forward, 0.5 toe-off, swing back to the front)
  // returns the ankle (H units, relative to the foot's base x) plus the pump angle (+ = toe down when facing +x)
  const BALL = [0.24, 0.13], HEEL = [-0.06, 0.13];
  function walkFoot(u, strideX, TH = 22, LIFT = 0.22) {
    let fx, lift = 0, th = 0;
    if (u < 0.5) {
      fx = lerp(strideX / 2, -strideX / 2, u / 0.5);
      th = TH * S.smoothstep(0.3, 0.5, u) - 6 * (1 - S.smoothstep(0, 0.07, u));   // heel peels up at the end of stance
    } else {
      const q = (u - 0.5) / 0.5;
      fx = lerp(-strideX / 2, strideX / 2, S.ease.easeInOutSine(q));
      lift = LIFT * Math.sin(Math.PI * Math.min(1, q * 1.08)) ** 1.2;
      th = q < 0.8 ? lerp(TH, -10, S.smoothstep(0, 0.8, q)) : lerp(-10, -6, (q - 0.8) / 0.2);
    }
    const a = th * RAD, ca = Math.cos(a), sa = Math.sin(a), piv = th >= 0 ? BALL : HEEL;
    const pv = [fx + piv[0], -lift];   // pivot on (or above) the ground
    return { p: [pv[0] - (piv[0] * ca - piv[1] * sa), pv[1] - (piv[0] * sa + piv[1] * ca)], lift, foot: a };
  }

  function resolve(o) {
    const R = {};
    R.dir = o.dir === -1 ? -1 : 1;
    R.turn = clamp(o.turn ?? 0);
    R.t = o.t ?? 0;
    R.antT = o.antT;
    let face = o.face ?? 'neutral';
    if (typeof face === 'string' && /^[0-9\-+:.]/.test(face)) { R.number = face; face = 'number'; }
    R.faceKey = FACE_ALIAS[face] || face;
    R.prevFace = o.prevFace ? (FACE_ALIAS[o.prevFace] || o.prevFace) : null;
    R.wipe = o.wipe;
    R.number = R.number ?? o.number; R.numberLabel = o.numberLabel; R.slide = o.slide; R.offK = o.offK;
    R.mouth = o.mouth; R.look = o.look || null; R.eerieSmile = o.eerieSmile;
    R.blink = o.blink ?? (o.t != null && o.autoBlink !== false ? S.blinkAt(o.t, 11, 3.4) : 1);
    R.antenna = o.antenna; R.sweat = o.sweat;
    const poseName = o.pose || 'idle-clipboard';
    const P = POSE_DEF[poseName] || POSE_DEF['idle-clipboard'];
    R.pose = poseName;
    const walk = poseName === 'walk';
    const ph = ((o.phase ?? 0) % 1 + 1) % 1;
    R.phase = ph;
    // head turn: signed, + = the body's facing (+x). Default follows the body; a pose may turn the head on its own.
    const hT = clamp(o.headTurn ?? P.headTurn ?? R.turn, -1, 1);
    R.hTurn = Math.abs(hT); R.hDir = (hT < 0 ? -1 : 1) * R.dir;
    const stampE = poseName === 'stamp' ? (() => { const k = clamp(o.stampK ?? 0.6); return k < 1 ? S.ease.easeInCubic(k) : 1; })() : 1;
    const breath = walk ? 0 : 0.008 * Math.sin(TAU * R.t / 3.6);
    // walk bob: lowest just after each contact (the "down"), highest at push-off (the "up"); knees always a bit bent
    const WK = o._walk || {};
    const bob = walk ? (WK.d0 ?? 0.03) + (WK.d1 ?? 0.03) * Math.cos(TAU * 2 * (ph - 0.06)) : 0;
    R.walkBounce = walk ? 0.4 * Math.sin(TAU * 2 * ph - 1.2) : 0;
    // weight shift (contrapposto) for the standing poses: hips out toward the stance leg (far), shoulders counter-tilt
    const tn = R.turn;
    const wt = walk ? 0 : clamp(o.weight ?? P.weight ?? 0);
    R.hipX = 0.03 * wt;
    R.hipY = -2.025 + bob + 0.004 * wt;
    R.lean = ((o.lean ?? P.lean ?? (walk ? 3 : 0)) - 1.4 * wt * (1 - tn) + (walk ? 1.2 * Math.sin(TAU * 2 * ph) : 0)) * RAD;
    R.headTilt = ((o.headTilt ?? P.headTilt ?? 0) + 1.2 * wt * (1 - tn) + (walk ? 2.2 * Math.sin(TAU * 2 * ph - 0.8) : 1.6 * Math.sin(TAU * R.t / 4.2))) * RAD;
    // 3/4 mapping: centre line moves toward +x, far half compresses
    const kn = 1 + 0.02 * tn, kf = 1 - 0.24 * tn, cs = 0.09 * tn;
    R.mx = (x, w = 0.48) => (x < 0 ? x * kn : x * kf) + cs * Math.max(0, 1 - Math.abs(x) / w);
    R.cs = cs;
    // legs. In 3/4 the two hip joints sit close together so a stride makes an inverted V, never an X.
    const hipK = walk ? 1 - 0.62 * tn : 1;
    const hipJ = [[R.mx(-0.115 * hipK) + R.hipX, R.hipY + 0.012 * wt], [R.mx(0.115 * hipK) + R.hipX, R.hipY - 0.012 * wt]];
    let ank;
    if (walk) {
      const strideX = STRIDE * (0.25 + 0.75 * tn);
      ank = [0, 1].map(i => {
        const u = (ph + i * 0.5) % 1, f = walkFoot(u, strideX, WK.th ?? 26, WK.lift ?? 0.22);
        // the far foot stays a little behind (up) and to the right of the near one
        const bx = WK.bx ?? 0.06, baseX = i ? lerp(0.1, hipJ[0][0] + 0.03 + bx, tn) : lerp(-0.1, hipJ[0][0] - 0.02 + bx, tn);
        return { p: [baseX + f.p[0], f.p[1] - (i ? 0.03 * tn : 0)], lift: f.lift, u, foot: f.foot };
      });
    } else {
      ank = [{ p: [-0.105 + 0.03 * tn + 0.03 * wt * (1 - tn), -0.13 - 0.008 * wt * (1 - tn)], lift: 0 },
        { p: [0.105 - 0.02 * tn + 0.025 * wt * (1 - tn), -0.15 * (tn > 0 ? 1 : 0.87)], lift: 0 }];
    }
    R.legs = [0, 1].map(i => {
      const a = ank[i].p, hj = hipJ[i];
      const bend = tn > 0.3 || walk ? 1 : (i ? 1 : (wt > 0 ? 1 : -1)); // relaxed front knee bends IN
      const s = ik2(hj, a, 1.0, 0.9, bend);
      let knee = s.e, ankle = s.w;
      if (!walk && tn <= 0.3) { // front stance: place the knees directly (two-bone IK is too touchy near full extension)
        knee = [lerp(hj[0], a[0], 0.53) + (i ? 0.006 : 0.05 * wt * (1 - tn)), lerp(hj[1], a[1], 0.53)]; ankle = a;
      } else if (walk) { // soft knees: cap how far the knee juts off the hip-ankle line (stance ~0.1 H, swing up to 0.24 H)
        const m = [lerp(hj[0], a[0], 0.53), lerp(hj[1], a[1], 0.53)], v = [knee[0] - m[0], knee[1] - m[1]], L = Math.hypot(v[0], v[1]);
        const cap = lerp(WK.capS ?? 0.12, WK.capW ?? 0.24, clamp(ank[i].lift / 0.15));
        if (L > cap) knee = [m[0] + v[0] * cap / L, m[1] + v[1] * cap / L];
        ankle = a;
      }
      return { hip: hj, knee, ankle, lift: ank[i].lift, u: ank[i].u, foot: ank[i].foot || 0 };
    });
    // arms
    const shrug = poseName === 'stamp' ? 0.08 * (1 - stampE) : 0;
    R.shoulder = { near: [R.mx(-0.37), -3.06 + breath - shrug], far: [R.mx(0.37) - 0.03 * tn, -3.06 + breath] };
    const armCfg = side => Object.assign({}, P[side], (o.arms && o.arms[side]) || {});
    R.arms = {};
    ['near', 'far'].forEach(side => {
      const A = armCfg(side);
      let wr = A.wrist.slice();
      let fk = null;
      if (poseName === 'stamp' && side === 'near' && A.upFK) {
        const e = stampE, sh = R.shoulder.near, wd = [R.mx(wr[0], 0.6), wr[1]];
        const sD = ik2pick(sh, wd, 0.65, 0.6, (e1, e2) => e1[0] <= e2[0]);
        let th2 = Math.atan2(sD.e[1] - sh[1], sD.e[0] - sh[0]) / RAD, ph2 = Math.atan2(sD.w[1] - sD.e[1], sD.w[0] - sD.e[0]) / RAD;
        const th1 = A.upFK[0], ph1 = A.upFK[1];
        while (th2 > th1) th2 -= 360;            // upper arm swings down through the screen-left side
        while (ph2 < ph1) ph2 += 360;            // forearm chops over the top toward the board
        // the elbow leads (drops early), the forearm drags and chops down last, like a hammer blow
        const th = lerp(th1, th2, 1 - (1 - e) ** 2.5) * RAD, phi = lerp(ph1, ph2, e ** 1.6) * RAD, st = lerp(1.04, 1, e);
        const el = [sh[0] + Math.cos(th) * 0.65 * st, sh[1] + Math.sin(th) * 0.65 * st];
        fk = { e: el, w: [el[0] + Math.cos(phi) * 0.6 * st, el[1] + Math.sin(phi) * 0.6 * st] };
        A.stampRot = (A.tilt ?? 0.36) * (1 - e); // raised: the fist cocks outward and the stamp tips so its red face shows
      }
      if (walk && side === 'near') { const sw = -Math.cos(TAU * ph); wr = [wr[0] + sw * 0.2 * (0.3 + 0.7 * tn), wr[1] - Math.abs(sw) * 0.04]; }
      if (A.hug) wr[0] += HUG_SEP(tn);
      wr = [R.mx(wr[0], 0.6), wr[1]];
      const sh = R.shoulder[side];
      let l1 = 0.65, l2 = 0.6;
      if (A.stretch) { const d = Math.hypot(wr[0] - sh[0], wr[1] - sh[1]), k = clamp(d / (1.25 * 0.985), 1, 1.07); l1 *= k; l2 *= k; }
      const s = fk || (A.elbowOut ? ik2pick(sh, wr, l1, l2, (e1, e2) => e1[0] <= e2[0]) : ik2(sh, wr, l1, l2, A.bend ?? 1));
      const backSide = side === 'far' && tn > 0.3;
      let ha = A.handAng != null ? A.handAng : Math.atan2(s.w[1] - s.e[1], s.w[0] - s.e[0]) / RAD;
      if (A.upHand != null && poseName === 'stamp') { let d = (ha - A.upHand) % 360; if (d > 180) d -= 360; if (d < -180) d += 360; ha = A.upHand + d * stampE; }
      R.arms[side] = Object.assign({}, A, { sh, el: s.e, wr: s.w, handAng: ha,
        zU: A.zU || (backSide ? 'back' : 'front'), zL: A.zL || (backSide && A.hand !== 'clip' ? 'back' : 'front') });
    });
    R.clip = P.clip ? Object.assign({}, P.clip, (o.clip || {})) : null;
    if (R.clip) R.clip.at = [R.mx(R.clip.at[0], 0.6) + (R.clip.flat ? 0 : HUG_SEP(tn)), R.clip.at[1]];
    R.badgeSep = BADGE_SEP(tn);
    R.stampK = o.stampK ?? 0.6;
    R.stampText = o.stampText || 'APPROVED';
    R.stampMark = o.stampMark ?? (R.stampK >= 0.97);
    R.props = Object.assign({ clipboard: true, remote: true, badge: true }, o.props || {});
    R.neck = [R.mx(0) * 0.6 + 0.0, -3.3];
    return R;
  }

  // pose transition: blend two resolved rigs (joint positions lerp, so bend flips never pop)
  function blendR(A, B, k) {
    if (k >= 1) return B;
    const L = (p, q) => [lerp(p[0], q[0], k), lerp(p[1], q[1], k)];
    const La = (a, b) => { let d = (b - a) % 360; if (d > 180) d -= 360; if (d < -180) d += 360; return a + d * k; };
    const R = Object.assign({}, B);
    R.hipY = lerp(A.hipY, B.hipY, k); R.lean = lerp(A.lean, B.lean, k); R.headTilt = lerp(A.headTilt, B.headTilt, k);
    R.walkBounce = lerp(A.walkBounce, B.walkBounce, k);
    R.hipX = lerp(A.hipX, B.hipX, k); R.badgeSep = lerp(A.badgeSep, B.badgeSep, k);
    const hs = lerp(A.hTurn * A.hDir, B.hTurn * B.hDir, k);
    R.hTurn = Math.abs(hs); R.hDir = hs < 0 ? -1 : hs > 0 ? 1 : B.hDir;
    R.legs = B.legs.map((l, i) => Object.assign({}, k < 0.5 ? A.legs[i] : l, { hip: L(A.legs[i].hip, l.hip), knee: L(A.legs[i].knee, l.knee), ankle: L(A.legs[i].ankle, l.ankle), foot: lerp(A.legs[i].foot || 0, l.foot || 0, k) }));
    if (A.pose === 'walk' && B.pose !== 'walk') R.pose = k < 0.5 ? 'walk' : B.pose;
    R.arms = {};
    ['near', 'far'].forEach(sd => {
      const a = A.arms[sd], b = B.arms[sd], pick = k < 0.5 ? a : b;
      R.arms[sd] = Object.assign({}, pick, {
        sh: L(a.sh, b.sh), el: L(a.el, b.el), wr: L(a.wr, b.wr),
        handAng: a.handAng != null && b.handAng != null ? La(a.handAng, b.handAng) : pick.handAng,
        rAng: a.rAng != null && b.rAng != null ? La(a.rAng, b.rAng) : pick.rAng,
        signal: b.signal && k > 0.85, press: b.press && k > 0.85,
        stampRot: lerp(a.stampRot || 0, b.stampRot || 0, k),
      });
    });
    if (A.clip && B.clip) R.clip = { at: L(A.clip.at, B.clip.at), rot: lerp(A.clip.rot || 0, B.clip.rot || 0, k), flat: lerp(A.clip.flat || 1, B.clip.flat || 1, k), scale: lerp(A.clip.scale || 1, B.clip.scale || 1, k) };
    else R.clip = k < 0.5 ? A.clip : B.clip;
    if (B.pose === 'stamp' && A.pose !== 'stamp') R.stampMark = false;
    return R;
  }

  // ================================================================================================= body parts (px space)
  const px = p => [p[0] * H, p[1] * H];

  function drawShoe(g, R, leg, i) {
    const a = px(leg.ankle), tn = R.turn;
    if (tn < 0.35) { // front view pump
      g.save(); g.translate(a[0], a[1] + 0.13 * H); g.rotate((i ? 1 : -1) * 0.12); g.scale(1.15, 1.1);
      cel(g, c => S.addCapsule(c, 0, -0.17 * H, 0, -0.055 * H, 0.078 * H, 0.105 * H), COL.skin, COL.skinShade, 0.016);
      cel(g, c => {
        c.moveTo(-0.08 * H, -0.07 * H);
        c.quadraticCurveTo(0, -0.035 * H, 0.08 * H, -0.07 * H);
        c.quadraticCurveTo(0.1 * H, -0.03 * H, 0.085 * H, -0.005 * H);
        c.quadraticCurveTo(0, 0.012 * H, -0.085 * H, -0.005 * H);
        c.quadraticCurveTo(-0.1 * H, -0.03 * H, -0.08 * H, -0.07 * H);
        c.closePath();
      }, COL.shoe, COL.shoeShade, 0.016);
      g.fillStyle = COL.shoeLight; g.beginPath(); g.ellipse(-0.04 * H, -0.04 * H, 0.022 * H, 0.009 * H, -0.3, 0, TAU); g.fill();
      g.restore();
      return;
    }
    // profile-ish pump pointing +x (the turn direction)
    const fa = leg.foot || 0; // + = heel up / toe down (push-off), - = toe up (heel strike)
    g.save(); g.translate(a[0], a[1]); g.rotate(fa);
    celU(g, c => { S.addCapsule(c, 0, -0.04 * H, 0.15 * H, 0.06 * H, 0.08 * H, 0.06 * H); }, COL.skin, COL.skinShade, 0.014);
    cel(g, c => {
      c.moveTo(-0.075 * H, 0.0);
      c.quadraticCurveTo(-0.09 * H, 0.08 * H, -0.06 * H, 0.13 * H);
      c.lineTo(0.27 * H, 0.13 * H);
      c.quadraticCurveTo(0.34 * H, 0.13 * H, 0.32 * H, 0.085 * H);
      c.quadraticCurveTo(0.29 * H, 0.04 * H, 0.17 * H, 0.06 * H);
      c.quadraticCurveTo(0.04 * H, 0.085 * H, -0.02 * H, 0.03 * H);
      c.closePath();
    }, COL.shoe, COL.shoeShade, 0.014);
    S.roundRect(g, -0.07 * H, 0.1 * H, 0.06 * H, 0.05 * H, 0.012 * H, COL.shoeShade);
    g.fillStyle = COL.shoeLight; g.beginPath(); g.ellipse(0.22 * H, 0.075 * H, 0.03 * H, 0.009 * H, -0.2, 0, TAU); g.fill();
    g.restore();
  }

  function drawLeg(g, R, leg, i) {
    const h = px(leg.hip), k = px(leg.knee), a = px(leg.ankle);
    const out = R.turn > 0.3 ? -1 : (i ? 1 : -1);
    const calf = [lerp(k[0], a[0], 0.3) + out * 0.01 * H, lerp(k[1], a[1], 0.3)];
    const shin = [lerp(k[0], a[0], 0.68), lerp(k[1], a[1], 0.68)];
    const far = R.turn > 0.3 && i === 1;
    celU(g, c => S.addLimb(c, [h, k, calf, shin, a], [0.24 * H, 0.165 * H, 0.18 * H, 0.13 * H, 0.1 * H]), far ? COL.skinShade : COL.skin, far ? C.shade(COL.skinShade, -0.06) : COL.skinShade, 0.025);
  }

  function drawSkirt(g, R) {
    const mx = R.mx, k0 = R.legs[0].knee, k1 = R.legs[1].knee, kB = k0[0] <= k1[0] ? k0 : k1, kT = kB === k0 ? k1 : k0;
    // pencil skirt: the hem follows the knees' average (not the outermost knee), widening only a little with the stride
    const hc = [lerp((k0[0] + k1[0]) / 2, R.mx(0) + (R.hipX || 0), 0.25), (k0[1] + k1[1]) / 2 + 0.05];
    const hw = 0.25 + 0.3 * Math.max(0, kT[0] - kB[0] - 0.24), tilt = (kT[1] - kB[1]) * 0.45;
    const hemN = [Math.min(hc[0] - hw, kB[0] - 0.11), hc[1] - tilt / 2], hemF = [Math.max(hc[0] + hw, kT[0] + 0.11), hc[1] + tilt / 2];
    const hy = R.hipY, hx = R.hipX || 0;
    const pts = [[mx(-0.3) + hx, hy - 0.55], [mx(0.3) + hx, hy - 0.55], [mx(0.37) + hx, hy - 0.2 - 0.012 * Math.sign(hx)], [hemF[0], hemF[1]], [hemN[0], hemN[1]], [mx(-0.37) + hx, hy - 0.2 + 0.012 * Math.sign(hx)]].map(px);
    const path = c => S.addRoundPoly(c, pts, [0.02 * H, 0.02 * H, 0.25 * H, 0.03 * H, 0.03 * H, 0.25 * H]);
    cel(g, path, COL.blazer, COL.blazerShade, 0.05);
    // shade band under the blazer hem + centre slit
    g.save(); g.beginPath(); path(g); g.clip();
    g.fillStyle = COL.blazerShade; g.fillRect(-H, (hy - 0.12) * H, 2 * H, 0.05 * H);
    const sx = lerp(hemN[0], hemF[0], 0.5) + R.cs * 0.3, sy = lerp(hemN[1], hemF[1], 0.5);
    g.fillStyle = COL.crease; g.fillRect(sx * H - 0.008 * H, (sy - 0.17) * H, 0.016 * H, 0.2 * H);
    g.restore();
  }

  function torsoPts(R) {
    const mx = R.mx, y0 = 0; // blazer outline (canonical front, H units)
    const raw = [
      [-0.13, -3.235], [-0.4, -3.165], [-0.478, -3.09], [-0.45, -2.86], [-0.31, -2.53], [-0.395, -2.11],
      [-0.075, -2.085], [0.0, -2.42], [0.075, -2.085],
      [0.395, -2.11], [0.31, -2.53], [0.45, -2.86], [0.478, -3.09], [0.4, -3.165], [0.13, -3.235],
    ];
    return raw.map(([x, y]) => [mx(x), y + y0]);
  }

  function drawTorso(g, R) {
    const mx = R.mx, cx = R.cs;
    const pts = torsoPts(R).map(px);
    const rad = [0.02, 0.06, 0.06, 0.12, 0.3, 0.04, 0.02, 0.01, 0.02, 0.04, 0.3, 0.12, 0.06, 0.06, 0.02].map(r => r * H);
    const path = c => S.addRoundPoly(c, pts, rad);
    cel(g, path, COL.blazer, COL.blazerShade, 0.055);
    // blouse V
    const vB = [cx, -2.62];
    const nL = [mx(-0.13), -3.235], nR = [mx(0.13), -3.235];
    const bl = spillMix(R, COL.blouse, px([cx, -3.15])), blS = spillMix(R, COL.blouseShade, px([cx, -3.15]));
    S.poly(g, [nL, nR, vB].map(px), bl);
    g.save(); g.beginPath(); S.addPoly(g, [nL, nR, vB].map(px)); g.clip();
    S.poly(g, [[nR[0] - 0.05, nR[1]], nR, vB, [vB[0] - 0.02, vB[1] - 0.06]].map(px), blS);
    g.restore();
    // lapels (same cloth, crease lines on their outer edges)
    const lapL = [nL, [mx(-0.255), -3.03], [mx(-0.205), -2.985], vB];
    const lapR = [nR, [mx(0.255), -3.03], [mx(0.205), -2.985], vB];
    S.roundPoly(g, lapL.map(px), 0.012 * H, COL.blazer);
    S.roundPoly(g, lapR.map(px), 0.012 * H, COL.blazerShade);
    S.strip(g, [lapL[1], lapL[2], vB].map(px), 0.016 * H, COL.crease);
    S.strip(g, [lapL[0], lapL[1]].map(px), 0.014 * H, COL.crease);
    // collar points + bow
    S.roundPoly(g, [[mx(-0.135), -3.25], [cx - 0.015, -3.2], [mx(-0.085), -3.1]].map(px), 0.01 * H, bl);
    S.roundPoly(g, [[mx(0.135), -3.25], [cx + 0.015, -3.2], [mx(0.085), -3.1]].map(px), 0.01 * H, blS);
    const bw = 0.085 * (1 - 0.15 * R.turn);
    const by = -3.17;
    cel(g, c => {
      S.addRoundPoly(c, [[cx, by], [cx - bw, by - 0.045], [cx - bw, by + 0.045]].map(px), 0.018 * H);
      S.addRoundPoly(c, [[cx, by], [cx + bw * 0.9, by - 0.045], [cx + bw * 0.9, by + 0.045]].map(px), 0.018 * H);
    }, COL.bow, COL.bowShade, 0.012);
    S.capsule(g, cx * H - 0.01 * H, by * H + 0.02 * H, cx * H - 0.03 * H, by * H + 0.1 * H, 0.025 * H, 0.02 * H, COL.bow);
    S.capsule(g, cx * H + 0.01 * H, by * H + 0.02 * H, cx * H + 0.035 * H, by * H + 0.09 * H, 0.025 * H, 0.02 * H, COL.bowShade);
    g.fillStyle = COL.bow; g.beginPath(); g.arc(cx * H, by * H, 0.025 * H, 0, TAU); g.fill();
    // button + pocket flaps
    g.fillStyle = COL.button; g.beginPath(); g.arc(cx * H, -2.47 * H, 0.026 * H, 0, TAU); g.fill();
    g.fillStyle = C.rgba('#ffffff', 0.25); g.beginPath(); g.arc(cx * H - 0.008 * H, -2.478 * H, 0.008 * H, 0, TAU); g.fill();
    S.strip(g, [[mx(-0.33), -2.3], [mx(-0.13), -2.29]].map(px), 0.016 * H, COL.crease);
    S.strip(g, [[mx(0.13), -2.29], [mx(0.33), -2.3]].map(px), 0.016 * H, COL.crease);
  }

  function drawNeck(g, R) {
    const n = px(R.neck);
    cel(g, c => S.addCapsule(c, n[0], n[1] + 0.2 * H, n[0], n[1] - 0.03 * H, 0.14 * H, 0.14 * H), spillMix(R, COL.skin, n, 1.1), COL.skinShade, 0.02);
    g.save(); g.beginPath(); S.addCapsule(g, n[0], n[1] + 0.2 * H, n[0], n[1] - 0.03 * H, 0.14 * H, 0.14 * H); g.clip();
    g.fillStyle = COL.skinShade; g.fillRect(n[0] - H, n[1] - 0.1 * H, 2 * H, 0.14 * H);
    g.restore();
  }

  function drawLanyard(g, R) {
    if (!R.props.badge) return;
    const mx = R.mx, swing = R.pose === 'walk' ? 0.13 * Math.sin(TAU * 2 * R.phase - 1.0) : 0.04 * Math.sin(TAU * R.t / 2.9);
    const clipP = [mx(-0.12, 0.6) + (R.badgeSep ?? -0.05) + Math.sin(swing) * 0.05, -2.84];
    const a = [mx(-0.115), -3.22], b = [mx(0.115), -3.22];
    const sL = [a, [lerp(a[0], clipP[0], 0.5) - 0.035, lerp(a[1], clipP[1], 0.55)], clipP];
    const sR = [b, [lerp(b[0], clipP[0], 0.45) + 0.045, lerp(b[1], clipP[1], 0.55)], clipP];
    const curve = P => { const out = []; for (let i = 0; i <= 12; i++) { const u = i / 12, v = 1 - u; out.push(px([v * v * P[0][0] + 2 * v * u * P[1][0] + u * u * P[2][0], v * v * P[0][1] + 2 * v * u * P[1][1] + u * u * P[2][1]])); } return out; };
    S.strip(g, curve(sR), 0.036 * H, COL.mintShade);
    S.strip(g, curve(sL), 0.036 * H, COL.mint);
    const c = px(clipP);
    g.save(); g.translate(c[0], c[1]); g.rotate(swing); upright(g, 0, () => drawBadgeLocal(g, R)); g.restore();
  }

  function sleevePath(c, A) {
    const sh = px(A.sh), el = px(A.el), wr = px(A.wr);
    S.addCapsule(c, sh[0], sh[1], el[0], el[1], 0.22 * H, 0.19 * H);
    S.addCapsule(c, el[0], el[1], wr[0], wr[1], 0.19 * H, 0.17 * H);
  }

  function drawUpperArm(g, R, side) {
    const A = R.arms[side], sh = px(A.sh), el = px(A.el);
    cel(g, c => S.addCapsule(c, sh[0], sh[1], el[0], el[1], 0.225 * H, 0.195 * H), COL.blazer, COL.blazerShade, 0.035);
  }

  function drawLowerArm(g, R, side) {
    const A = R.arms[side];
    const el = px(A.el), wr = px(A.wr);
    const fa = Math.atan2(wr[1] - el[1], wr[0] - el[0]);
    const handAng = A.handAng != null ? A.handAng * RAD : fa;
    const hp = add(wr, [Math.cos(fa) * 0.03 * H, Math.sin(fa) * 0.03 * H]);
    cel(g, c => S.addCapsule(c, el[0], el[1], wr[0], wr[1], 0.195 * H, 0.17 * H), COL.blazer, COL.blazerShade, 0.035);
    // sleeve-end bands + a thin blouse cuff
    const back = d => add(wr, [-Math.cos(fa) * d * H, -Math.sin(fa) * d * H]);
    const nrm = [-Math.sin(fa), Math.cos(fa)];
    [0.075, 0.11].forEach(d => { const p = back(d); S.strip(g, [add(p, [nrm[0] * 0.08 * H, nrm[1] * 0.08 * H]), add(p, [-nrm[0] * 0.08 * H, -nrm[1] * 0.08 * H])], 0.012 * H, COL.crease); });
    const c0 = back(0.0), c1 = add(wr, [Math.cos(fa) * 0.025 * H, Math.sin(fa) * 0.025 * H]);
    S.capsule(g, c0[0], c0[1], c1[0], c1[1], 0.125 * H, 0.12 * H, spillMix(R, COL.blouse, wr, 1.1));
    // props held in the fist (drawn over the sleeve, under the fingers)
    const grip = add(hp, [Math.cos(handAng) * 0.075 * H, Math.sin(handAng) * 0.075 * H]);
    if (A.hand === 'remote' && R.props.remote) { g.save(); g.translate(grip[0], grip[1]); drawRemoteLocal(g, (A.rAng ?? 90) * RAD, A.press); g.restore(); }
    if (A.hand === 'stamp') {
      const sr = A.stampRot || 0;
      g.save(); g.translate(grip[0], grip[1]); g.rotate(sr); g.scale(1.2, 1.2); drawStampLocal(g, sr); g.restore();
      A.padPt = add(grip, [-Math.sin(sr) * 0.17 * 1.2 * H, Math.cos(sr) * 0.17 * 1.2 * H]);
    }
    // hand
    const ts = A.thumb ?? (Math.cos(handAng) >= 0 ? -1 : 1);
    g.save(); g.translate(hp[0], hp[1]); g.rotate(handAng);
    drawHandLocal(g, A.hand === 'remote' || A.hand === 'stamp' ? 'fist' : A.hand, ts, { sk: spillMix(R, COL.skin, hp, 1.25), sh: spillMix(R, COL.skinShade, hp, 1.25) });
    g.restore();
    A.handPt = hp; A.handDir = handAng;
    // remote signal waves toward the head
    if (A.signal && R.props.remote) {
      const ra = (A.rAng ?? 0) * RAD, tip = add(grip, [Math.cos(ra) * 0.3 * H, Math.sin(ra) * 0.3 * H]);
      g.save(); g.lineCap = 'round';
      [0.07, 0.12, 0.17].forEach((r, i) => {
        g.strokeStyle = `rgba(255,236,190,${0.9 - i * 0.22})`; g.lineWidth = 0.022 * H;
        g.beginPath(); g.arc(tip[0], tip[1], r * H, ra - 0.55, ra + 0.55); g.stroke();
      });
      g.restore();
    }
  }

  function drawClipHeld(g, R) {
    if (!R.clip || !R.props.clipboard) return;
    const c = px(R.clip.at);
    g.save(); g.translate(c[0], c[1]); g.rotate((R.clip.rot || 0) * RAD * LX * LX);
    if (R.clip.scale) g.scale(R.clip.scale, R.clip.scale);
    if (R.clip.flat) g.scale(1, R.clip.flat);
    upright(g, 0, () => drawClipboardLocal(g, { mark: R.stampMark ? R.stampText : null }));
    g.restore();
  }

  // impact lines for the stamp hit
  function drawImpact(g, R) {
    if (R.pose !== 'stamp') return;
    const k = R.stampK;
    // body parts the effect lines must not cross (px, radius)
    const segs = [];
    ['near', 'far'].forEach(sd => { const A = R.arms[sd]; segs.push([px(A.sh), px(A.el), 0.13 * H], [px(A.el), px(A.wr), 0.12 * H]); if (A.handPt) segs.push([px(A.wr), add(A.handPt, [Math.cos(A.handDir) * 0.2 * H, Math.sin(A.handDir) * 0.2 * H]), 0.1 * H]); });
    const segD = (p, a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], l2 = dx * dx + dy * dy || 1, t = clamp(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2); return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy); };
    const clear = (p0, p1) => [0, 0.5, 1].every(t => { const p = [lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t)]; return segs.every(([a, b, r]) => segD(p, a, b) > r); });
    const line = (p0, p1) => { if (!clear(p0, p1)) return; g.beginPath(); g.moveTo(p0[0], p0[1]); g.lineTo(p1[0], p1[1]); g.stroke(); };
    const pad = R.arms.near.padPt;
    if (k < 0.5 && R.stampMark && pad) { // stamp just lifted: short motion trails BESIDE the pad, on the outer side
      g.save(); g.strokeStyle = 'rgba(255,240,200,0.75)'; g.lineCap = 'round'; g.lineWidth = 0.022 * H;
      [[-0.27, 0.0, 0.2], [-0.37, 0.05, 0.13], [0.24, 0.02, 0.12]].forEach(([dx, dy, len]) => line([pad[0] + dx * H, pad[1] + dy * H], [pad[0] + dx * H, pad[1] + (dy + len) * H]));
      g.restore();
    }
    if (k < 0.9 && !(R.stampMark && k > 0.4)) return;
    const c = px(R.clip.at);
    const a = k >= 0.9 ? 1 : 0.6;
    g.save(); g.strokeStyle = `rgba(255,240,200,${0.85 * a})`; g.lineCap = 'round'; g.lineWidth = 0.022 * H;
    [[-1, -0.3], [-1, 0.25], [1, -0.3], [1, 0.25]].forEach(([sx, sy]) => {
      const x0 = c[0] + sx * 0.37 * H, y0 = c[1] + sy * 0.3 * H - 0.02 * H;
      line([x0, y0], [x0 + sx * 0.11 * H, y0 + sy * 0.18 * H]);
    });
    g.restore();
  }

  // ================================================================================================= assembly
  function bodyToCanvas(R, p, x, y, s) { // H-unit body point -> canvas px (lean applied for upper-body points)
    const q = rotAbout(p, [0, R.hipY], R.lean);
    return [x + LX * (q[0] + R.hipX) * H * s, y + q[1] * H * s];
  }

  // screen light on the LIGHT materials (collar, blouse cuffs, neck, hands): a colour mix that falls off over ~2.4 H
  // from the screen centre, so a white collar visibly turns mint while the blazer keeps its lavender.
  const SPILL_COL = '#7FE6D4';
  function spillMix(R, col, p, k = 1) {
    if (!(R.spillA > 0) || !R.scrU || R.faceKey === 'off') return col;
    const d = Math.hypot(p[0] - R.scrU[0], p[1] - R.scrU[1]), f = Math.max(0, 1 - d / (2.4 * H)) ** 1.1;
    const tc = R.faceKey === 'slide' ? '#E4F4EE' : R.faceKey === 'panic' ? '#C9D6FF' : SPILL_COL;
    return C.mix(col, tc, clamp(R.spillA * k * f * 0.95));
  }
  function spillLight(g, R, center, alpha) {
    if (alpha <= 0) return;
    const glowCol = R.faceKey === 'slide' ? '#E8F6EF' : R.faceKey === 'panic' ? '#D8E4FF' : R.faceKey === 'eerie' ? '#BFF5EE' : COL.mint;
    if (R.faceKey === 'off' && (R.offK ?? 1) >= 0.95) return;
    g.save(); g.globalCompositeOperation = 'source-atop';
    const RR = 1.1 * H, rg = g.createRadialGradient(center[0], center[1], 0, center[0], center[1], RR);
    rg.addColorStop(0, C.rgba(glowCol, alpha)); rg.addColorStop(0.55, C.rgba(glowCol, alpha * 0.45)); rg.addColorStop(1, C.rgba(glowCol, 0));
    g.fillStyle = rg; g.fillRect(center[0] - RR, center[1] - RR, 2 * RR, 2 * RR);
    g.restore();
  }

  let _rimCanvas = null;
  function rimPass(g, rim, s) {
    const cv = g.canvas, w = cv.width, h = cv.height;
    if (!_rimCanvas) _rimCanvas = document.createElement('canvas');
    const m = _rimCanvas; if (m.width < w || m.height < h) { m.width = Math.max(m.width, w); m.height = Math.max(m.height, h); }
    const mc = m.getContext('2d');
    mc.setTransform(1, 0, 0, 1, 0, 0); mc.globalCompositeOperation = 'source-over'; mc.clearRect(0, 0, m.width, m.height);
    mc.drawImage(cv, 0, 0);
    mc.globalCompositeOperation = 'source-in'; mc.fillStyle = rim.color || '#DCE8FF'; mc.fillRect(0, 0, w, h);
    const d = rim.dir || [-1, -0.6], L = Math.hypot(d[0], d[1]) || 1, wd = (rim.width ?? 2.6) * s;
    mc.globalCompositeOperation = 'destination-out';
    mc.drawImage(cv, -d[0] / L * wd, -d[1] / L * wd);
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-atop'; g.globalAlpha = rim.alpha ?? 0.55;
    g.drawImage(m, 0, 0, w, h, 0, 0, w, h);
    g.restore();
  }

  function draw(ctx, x, y, s = 1, o = {}) {
    let R = resolve(o);
    if (o.from && (o.blend ?? 1) < 1) R = blendR(resolve(Object.assign({}, o, o.from)), R, S.ease.easeInOutCubic(clamp(o.blend ?? 1)));
    LX = R.dir;
    const spillA = o.spill ?? 0.3;
    const bounds = { x: x - 2.6 * H * s, y: y - 5.3 * H * s, w: 5.2 * H * s, h: 5.6 * H * s };
    if (o.cast !== false) S.groundShadow(ctx, x + LX * 0.02 * H * s, y + 0.01 * H * s, 0.95 * H * s, 0.16 * H * s, 0.45);
    // screen centre in body space (for spill + bloom)
    const hf = R.hDir * R.dir; // +1: head faces the way the body does; -1: head turned the other way (mirrored)
    const tn = R.hTurn, angT = 35 * RAD * tn, fs = Math.cos(angT), dd = 0.35 * H * Math.sin(angT), cwh = 1.3 * H * fs;
    const scrHeadLocal = [hf * ((-(cwh + dd) / 2 + dd) + cwh / 2), -0.54 * H];
    const nk = px(R.neck);
    const scrUpper = add(nk, rotAbout([scrHeadLocal[0] * HS, scrHeadLocal[1] * HS], [0, 0], R.headTilt));
    const scrBody = add(rotAbout(scrUpper, [0, R.hipY * H], R.lean), [R.hipX * H, 0]);
    R.scrU = scrUpper; R.spillA = spillA;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s * LX, s);
      const upper = gg => { gg.translate(R.hipX * H, R.hipY * H); gg.rotate(R.lean); gg.translate(0, -R.hipY * H); };
      // A: everything behind the head, lit by the screen
      S.shadowGroup(g, gA => {
        gA.save(); upper(gA);
        ['far', 'near'].forEach(sd => { if (R.arms[sd].zU === 'back') drawUpperArm(gA, R, sd); if (R.arms[sd].zL === 'back') drawLowerArm(gA, R, sd); });
        gA.restore();
        const order = R.turn > 0.3 ? [1, 0] : [0, 1];
        order.forEach(i => drawLeg(gA, R, R.legs[i], i));
        order.forEach(i => drawShoe(gA, R, R.legs[i], i));
        drawSkirt(gA, R);
        gA.save(); upper(gA);
        drawNeck(gA, R);
        drawTorso(gA, R);
        drawLanyard(gA, R);
        gA.restore();
        spillLight(gA, R, scrBody, spillA * 0.6);
      }, { shadow: false });
      // head
      g.save(); upper(g);
      g.translate(nk[0], nk[1]); g.rotate(R.headTilt); g.scale(HS * hf, HS);
      LX = R.hDir; drawHeadLocal(g, R); LX = R.dir;
      g.restore();
      // B: arms and props in front
      S.shadowGroup(g, gB => {
        gB.save(); upper(gB);
        ['far', 'near'].forEach(sd => { if (R.arms[sd].zU !== 'back') drawUpperArm(gB, R, sd); });
        drawClipHeld(gB, R);
        ['far', 'near'].forEach(sd => { if (R.arms[sd].zL !== 'back') drawLowerArm(gB, R, sd); });
        drawImpact(gB, R);
        gB.restore();
        spillLight(gB, R, scrBody, spillA * 0.7);
      }, { shadow: false });
      g.restore();
      if (o.rim) rimPass(g, o.rim === true ? {} : o.rim, s);
    }, { scale: s, bounds, shadow: o.shadow !== false });
    // soft screen halo into the scene
    const bloom = o.bloom ?? 0.35;
    if (bloom > 0 && !(R.faceKey === 'off' && (R.offK ?? 1) >= 0.95)) {
      const c = [x + LX * scrBody[0] * s, y + scrBody[1] * s];
      const col = R.faceKey === 'panic' ? '#C9D6FF' : R.faceKey === 'slide' ? '#EAF7F0' : COL.mint;
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      const rg = ctx.createRadialGradient(c[0], c[1], 0.3 * H * s, c[0], c[1], 1.25 * H * s);
      rg.addColorStop(0, C.rgba(col, 0.22 * bloom)); rg.addColorStop(1, C.rgba(col, 0));
      ctx.fillStyle = rg; ctx.fillRect(c[0] - 1.3 * H * s, c[1] - 1.3 * H * s, 2.6 * H * s, 2.6 * H * s);
      ctx.restore();
    }
    LX = 1;
    return R;
  }

  function drawHead(ctx, x, y, s = 1, o = {}) {
    const R = resolve(Object.assign({ headTilt: 0 }, o));
    LX = R.hDir;
    const tilt = (o.headTilt ?? 0) * RAD;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s * LX * HS, s * HS); g.rotate(tilt);
      drawHeadLocal(g, R);
      g.restore();
    }, { scale: s, bounds: { x: x - 1.3 * H * HS * s, y: y - 1.8 * H * HS * s, w: 2.6 * H * HS * s, h: 1.95 * H * HS * s }, shadow: o.shadow !== false });
    if ((o.bloom ?? 0) > 0) {
      const c = [x, y - 0.54 * H * HS * s];
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      const rg = ctx.createRadialGradient(c[0], c[1], 0.3 * H * s, c[0], c[1], 1.1 * H * s);
      rg.addColorStop(0, C.rgba(COL.mint, 0.2 * o.bloom)); rg.addColorStop(1, C.rgba(COL.mint, 0));
      ctx.fillStyle = rg; ctx.fillRect(c[0] - 1.2 * H * s, c[1] - 1.2 * H * s, 2.4 * H * s, 2.4 * H * s);
      ctx.restore();
    }
    LX = 1;
    return R;
  }

  function solve(x, y, s = 1, o = {}) {
    let R = resolve(o);
    if (o.from && (o.blend ?? 1) < 1) R = blendR(resolve(Object.assign({}, o, o.from)), R, S.ease.easeInOutCubic(clamp(o.blend ?? 1)));
    LX = R.dir;
    const hf = R.hDir * R.dir;
    const tn = R.hTurn, angT = 35 * RAD * tn, fs = Math.cos(angT), dd = 0.35 * H * Math.sin(angT), cwh = 1.3 * H * fs;
    const nk = px(R.neck);
    const toC = p => { const q = rotAbout(p, [0, R.hipY * H], R.lean); return [x + LX * (q[0] + R.hipX * H) * s, y + q[1] * s]; };
    const headPt = hp => toC(add(nk, rotAbout([hp[0] * HS, hp[1] * HS], [0, 0], R.headTilt)));
    const fcx = hf * ((-(cwh + dd) / 2 + dd) + cwh / 2);
    const scr = headPt([fcx, -0.54 * H]);
    const out = {
      screen: { x: scr[0], y: scr[1], w: 0.96 * H * fs * HS * s, h: 0.72 * H * HS * s },
      headTop: headPt([fcx, -H]), neck: toC(nk),
      hands: { near: toC(px(R.arms.near.wr)), far: toC(px(R.arms.far.wr)) },
      bounds: { x: x - 1.6 * H * s, y: y - 4.85 * H * s, w: 3.2 * H * s, h: 4.85 * H * s },
    };
    LX = 1;
    return out;
  }

  function wipeAt(t, tChange, frames = 3, fps = 30) {
    const k = (t - tChange) * fps / frames;
    return k <= 0 || k >= 1 ? null : k;
  }

  const propWrap = fn => (ctx, x, y, s = 1, o = {}) => {
    S.shadowGroup(ctx, g => { g.save(); g.translate(x, y); g.scale(s, s); fn(g, o); g.restore(); }, { scale: s, bounds: { x: x - 0.8 * H * s, y: y - 0.8 * H * s, w: 1.6 * H * s, h: 1.6 * H * s } });
  };

  window.HELEN = {
    version: '1.0', H, STRIDE, COL, FACES, POSES, MOUTHS,
    draw, drawHead, solve, wipeAt,
    drawClipboard: propWrap((g, o) => { g.rotate((o.rot || 0) * RAD); drawClipboardLocal(g, { mark: o.mark }); }),
    drawRemote: propWrap((g, o) => { LX = 1; drawRemoteLocal(g, (o.ang ?? -20) * RAD, o.press); }),
    drawStamp: propWrap(g => { LX = 1; drawStampLocal(g); }),
    drawBadge: propWrap(g => { LX = 1; drawBadgeLocal(g, {}); }),
    stampMark: (ctx, x, y, w, text = 'APPROVED', rot = -0.2) => { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); stampMark(ctx, w, text); ctx.restore(); },
  };
})();
