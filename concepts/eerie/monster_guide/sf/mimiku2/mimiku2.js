/* =====================================================================================================================
 * mimiku2.js : window.MIMIKU2, Mimiku v2 (Monster HR new hire #001), the cute-and-grotesque treasure-chest mimic.
 * Needs core/lib_core.js (window.SFX). Plain canvas 2D, deterministic (seeded tables only, never Math.random).
 *
 * LOOK (owner decisions): the chest and the face are the CUTE layer (flat fills, one hard shade tone, rounded shapes,
 * big glowing gold eyes + blush low in a dark fleshy mouth). The anatomy is the GROTESQUE layer, drawn in a deliberately
 * more detailed, too-real finish that clashes with the chest: uneven human silhouettes (hollow inner thigh, calf bulge,
 * shin narrowing hard to a thin ankle, forearm swelling below the elbow), matte sickly skin with 2-3 extra tones, raised
 * tendons (one light edge, one deep edge), short crease arcs at every knee and elbow, pinker darker knee / knuckle zones,
 * a pointed elbow bone, a few thick grey-violet veins, and a hard CORE SHADOW band (+ deep edge + lit streak) on the
 * away-from-light side of every limb segment so the masses read at body scale (s = 0.45), separate pink kneecap /
 * ankle / elbow knobs, knobby long fingers with dark nails, long uneven teeth on both
 * lips, a wet fleshy tongue. Never gore.
 *
 * UNITS: px at s = 1, with W = chest width = 180 px. Everything is measured from the GROUND POINT (x, y) passed to
 * draw(): the point on the floor between the feet (screen y grows downward, so "up" is negative).
 *   chest body 0.55 W tall, depth 0.6 W, lid 0.15 W + 0.13 W dome, lid hinges at the back (110 deg at lidOpen = 1).
 *   legs: thigh 0.95 W, shin 0.95 W, foot 0.3 W, hips at +-0.22 W under the chest; standing hip (chest bottom) 1.8 W.
 *   arms: upper 0.8 W, forearm 0.8 W, hand 0.35 W, shoulders inside the mouth gap at the left / right corners.
 *   Standing (lidOpen 0.75, the idle) the top of the lid is ~3.1 W (~560 px): taller than a knight (2.4 W).
 *
 * VIEW: a small orthographic 3D frame for the chest. yaw (deg) turns the character: 0 = front, + = faces screen-right
 * (you see its LEFT side), - = faces screen-left (you see its RIGHT side, where the chain hangs). The camera looks down
 * 7 deg. pitch (deg, + = top tips forward) and tilt (deg, + = clockwise roll) rotate the chest. Limbs are solved with
 * two-bone IK in screen space toward targets the animator places (feet = ankle points, hands = wrist points).
 *
 * API
 *   MIMIKU2.draw(ctx, x, y, s = 1, opts)      draws the whole character as ONE group (one drop shadow). Returns the solve.
 *   opts (all optional; a state preset fills everything, explicit keys override it, nested objects are merged):
 *     state       'dormant' | 'peek' | 'unfold' | 'stand' (default 'stand')
 *     unfold      0..1 with state 'unfold': 0 = flat chest on the floor, 1 = fully standing (keyframed through
 *                 crack -> peek -> push-up -> rise -> stand)
 *     yaw, pitch, tilt   degrees (see VIEW)
 *     hip         [x, y] chest-bottom centre relative to the ground point (stand: [0, -324])
 *     crouch      0..1 lowers the hip toward the feet (knees bend more), applied after everything else
 *     lidOpen     0..1 (1 = 110 deg; up to 1.3 for a yawn / pounce). Idle reads as a MOUTH at ~0.75.
 *     breath      0..1 adds a tiny lid lift (dormant breathing: teeth tips and glints show in the seam)
 *     legs        { L: {...}, R: {...} }  L = the character's own left (object -X; screen-left in front view)
 *                   foot [x, y]   ankle target (ground-relative px). The foot is drawn from the solved ankle; a planted
 *                                 foot pointing at the camera is squashed so its sole sits ON the ground line.
 *                   kneeOut       -1 knock-kneed .. +1 spider-out (front-view bend); the knee always bends forward too
 *                   toe           foot pitch in radians (+ = toes point down: airborne, tiptoe)
                   splay         toe-out angle in radians (default 0.62: duck-footed, so the long toes read)
 *                   grow          0..1 limb length factor (legs sprouting during the unfold); 0 hides the leg
 *     arms        { L: {...}, R: {...} }
 *                   hand [x, y]   wrist target (ground-relative px)
 *                   mode          'arm' (default) | 'hand' (only a hand gripping the lip from inside the gap) | 'none'
 *                   handAng       radians, screen direction wrist -> fingertips (default: forearm direction + bend)
 *                   handBend      radians added to the forearm direction when handAng is not given
 *                   curl 0..1     finger curl (claw);  fingers [i, m, r, p] per-finger curl override (tapping);
 *                   thumb 0..1    thumb curl;  spread 0..1 finger fan;  curlDir +-1 which way they curl
 *                   elbowUp       0..1 how strongly the elbow prefers up (default 0.8);  grow 0..1 like legs
 *                   handScale     >1 fakes a hand coming toward the camera (forearm widens toward it, hand grows)
 *     tongue      (auto-retracts while the lid is shut; drapes over the lower teeth with a rounded fold, a side wall and a
                 contact shadow on the chest front)
                 { len (W, 0 = retracted), ang (rad, root direction, default straight down), swing (rad, rotates the
 *                   whole tongue), curl (rad, bends progressively toward the tip), wave (rad amplitude), phase, width,
 *                   behind (true: drawn behind the chest, streaming back from under it) }
 *     chain       { swing (rad: the hang direction, + = toward screen-left), sway (rad travelling wave), sag 0..1
 *                   (1 = hangs, low = flies straight out), t, links=17, pts (ABSOLUTE canvas points, e.g. from
 *                   SFX.simChain; override), floor (true, dormant: THE TELL, the chain slides forward round the front corner and curls up in front of
 *                   the chest), real (true: the neat side-back coil of a real chest), coilSq (floor-coil squash, 0.5),
 *                   tiltFront (extra floor depth in front of the chest, 0.22) }
 *     realChest   true: a plain chest from the same model (shut, no seam, face, limbs or fx; chain coiled neatly at the
 *                 side-back) for rule gags and side-by-side comparisons with the dormant mimic
 *     expr        'neutral' | 'happy' | 'nervous' | 'hungry' | 'annoyed' | 'scared' | 'sleepy' | 'smitten' | 'pounce'
 *                 | 'yawn' | 'effort'.  nervous / annoyed / scared / pounce draw BRIGHT eyes (cream-gold sclera, tiny
 *                 dark pupil); the rest are glow eyes (light on the dark mouth).
 *     eyeAt       0..1 eye depth from the hinge toward the upper lip (default 0.22);  eyeLift (W, default 0.07) lifts
                 the eyes off the lower tooth row as the lid opens;  teeth  tooth-length multiplier (expr pounce = 1.25)
     look        {x, y} -1..1 gaze;  blink 0..1 (1 = open; use SFX.blinkAt(t));  blush 0..1.3 overrides the expression's blush
 *     eye         extra SFX.eye overrides for both eyes (e.g. {open: 0.7})
 *     fx          { sweat, drool, sparkle, zzz, hearts, tears } booleans/0..1 (expressions switch some on)
 *     t           seconds, for fx motion and the procedural chain sway
 *     shadow      'drop' (default, the show's down-right group shadow) | 'ground' (contact shadows only, for top-lit
 *                 scenes like the spotlight room) | 'none'
 *     light       { key, keyA, keyD, rim, rimA, rimD, rimDir:[x,y], keyDir:[x,y], falloff:{y0, y1, a} } optional mood
 *                 lighting baked on the group in screen space (warm key on the lit edges, cool rim on the shadow
 *                 side, darker toward the feet; y0/y1 are ABSOLUTE canvas y). Used by the hero shot.
 *     flesh       0..1 (default 0): fleshier too-human limbs (fuller calves / thighs / forearms / fingers over the same
                 knobby joints) + a pinkish-grey sickly SKIN palette, so wide / small shots never read as bare bone
     alpha       0..1 whole-character fade;  silhouette: colour = draw a flat one-colour silhouette (onion skins)
 *     parts       { legs, arms, tongue, chain, fx } false = skip (close-ups)
 *   MIMIKU2.pose(state, unfold, yaw) -> opts      the preset itself (to tweak and pass back)
 *   MIMIKU2.walkPose(phase, o) -> opts            gangly bouncy walk cycle, phase 0..1 (two steps). o: yaw=-35,
 *                 stride=0.9 (W, foot sweep), lift=0.32 (W, swing height), bounce=1, t. Returns opts plus .advance =
 *                 ground distance (px at s = 1, along the facing direction) covered per cycle. On screen that is
 *                 MIMIKU2.yawFrame(yaw).ground(0, advance)[0] * s px of x per cycle (see motion_test.js).
 *   MIMIKU2.jumpPose(k, o) -> opts                k 0..1: anticipate (lid clamps shut) .2, launch .29, rise .42, apex
 *                 .55, fall .7, touch .8, land squash .86, recover .93. o: yaw=-35, height=1.0 (W apex), dist=2.2 (W).
 *                 Returns opts plus .dx (ground-point offset in px at s = 1 along the facing direction) and .air.
 *   MIMIKU2.pouncePose(o) -> opts                 the Rule-10 dive ("OPEN WIDE"): airborne, chest nose-down at the
 *                 target, lid wide, both arms reaching down either side of it, legs trailing up and back, tongue and
 *                 chain streaming behind. o: dir=-1 (screen direction it dives), target=[x, y] (ground-relative px,
 *                 e.g. a knight's helmet centre; default [-0.8 W, -2.15 W]), grab=0.3 (W, hands either side).
 *   MIMIKU2.lerpPose(a, b, k)                     numeric blend of two opts objects (strings switch at k = 0.5)
 *   MIMIKU2.anchors(x, y, s, opts) -> { chain, eyes[2], mouth, lip, lidTop, hands, elbows, feet, knees ({L,R}), hip, bounds }
 *                 absolute canvas points (chain = anchor of the chain, for SFX.simChain)
 *   MIMIKU2.castShadow(ctx, x, y, s, opts, o)     flat blurred silhouette laid on the floor from the ground point
 *                 (o: color='#000', alpha=0.5, squash=0.2, skew=0.5, blur=6) for spotlit hero shots
 *   MIMIKU2.knight(ctx, x, y, s, o)               grey placeholder knight silhouette, 2.4 W tall at s (for scale)
 *   MIMIKU2.merge(a, b)                           deep merge of opts (b wins);  MIMIKU2.yawFrame(yaw) -> {vec, ground, view}
 *   MIMIKU2.EXPR, MIMIKU2.COL, MIMIKU2.DIM
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX;
  if (!S) throw new Error('mimiku2.js needs lib_core.js (window.SFX) loaded first');
  const C = S.color, TAU = Math.PI * 2, RAD = Math.PI / 180;
  const clamp = S.clamp, lerp = S.lerp, sstep = S.smoothstep, E = S.ease;
  const W = 180;

  const DIM = {
    W, Hb: 0.55 * W, D: 0.6 * W, Tf: 0.15 * W, dome: 0.13 * W, o: 0.025 * W, rim: 0.05 * W,
    hipX: 0.22 * W, hipY: -0.05 * W,
    shX: 0.485 * W, shY: -0.6 * W, shZ: 0.02 * W,
    thigh: 0.95 * W, shin: 0.95 * W, ankle: 0.085 * W, foot: 0.3 * W,
    upper: 0.8 * W, fore: 0.8 * W, hand: 0.35 * W, handK: 1.2, footK: 1.3,   // handK / footK: drawn size of hands / feet
    eyeW: 0.3 * W, eyeU: 0.245, eyeAt: 0.22,
    lidMax: 110, elev: 7, standHip: 1.8 * W, idleLid: 0.75,
  };

  const COL = {
    wood: '#A0866B', woodShade: '#6F5A47', woodLight: '#B79D80', woodSeam: '#634F3E', woodSide: '#8E765E',
    iron: '#4B5160', ironShade: '#363A45', ironLight: '#6B7383', rivet: '#8A91A0',
    gold: '#E2B248', goldShade: '#B48529', goldLight: '#F8DC8C', keyhole: '#24170E',
    mouth: '#140F14', throat: '#0A070A', palate: '#2B121A', ridge: 'rgba(122,48,66,0.42)', gum: '#4E1B27', gumLight: '#6B2734',
    tooth: '#EEE4CD', toothShade: '#C6B694', toothStain: '#A48C69',
    tongue: '#D45D70', tongueShade: '#A8455B', groove: '#8B3448', tongueDot: '#BF5368', wet: 'rgba(255,240,244,0.82)',
    skin: '#DED4C6', skinShade: '#A99B89', skinMid: '#C6B9A8', skinDeep: '#857565', skinLite: '#ECE6DC',
    pink: '#C9A49B', pinkShade: '#A6847C',
    vein: '#9A90A8', veinDeep: '#6F6683', nail: '#2A2226', nailHi: '#5E5058',
    glow: '#FFC83D', eyeCream: '#FFE9A8', eyeInk: '#E09A2E', blush: '#FF7F96', brow: '#FFE3A0',
    chain: { base: '#5E6370', shade: '#383B44', light: '#8D93A0' },
    sweat: '#a9dcff', drool: '#d6ecff', droolShade: '#9fc6e6', zzz: '#d9e6ff', heart: '#FF8FAE',
  };

  // ------------------------------------------------------------------ small vector math (2D)
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, k) => [a[0] * k, a[1] * k];
  const len = a => Math.hypot(a[0], a[1]);
  const nrm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l]; };
  const perp = a => [-a[1], a[0]];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const lp = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
  const ang = a => Math.atan2(a[1], a[0]);
  const dirA = a => [Math.cos(a), Math.sin(a)];
  const cross3 = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm3 = v => { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
  const LIGHT = norm3([-0.5, -0.75, 0.45]);
  const pos = v => (v > 0 ? v : 0);
  const bump = (u, c, w) => { const x = (u - c) / w; return Math.abs(x) >= 1 ? 0 : Math.cos(x * Math.PI / 2) ** 2; };
  const sgnTurn = (a, b) => (a[0] * b[1] - a[1] * b[0] > 0 ? 1 : -1);    // rotation sign that turns a toward b
  const rot2 = (v, a) => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a)];
  // Catmull-Rom resample of an open polyline (n samples per segment)
  function catmull(P, n = 4) {
    if (P.length < 3) return P.map(q => q.slice());
    const out = [];
    for (let i = 0; i < P.length - 1; i++) {
      const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
      for (let j = 0; j < n; j++) {
        const t = j / n, t2 = t * t, t3 = t2 * t;
        out.push([0, 1].map(k => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
      }
    }
    out.push(P[P.length - 1].slice());
    return out;
  }

  // ------------------------------------------------------------------ the yaw-only frame (for authoring targets)
  function yawFrame(yawDeg) {
    const y = (yawDeg || 0) * RAD, cy = Math.cos(y), sy = Math.sin(y), e = DIM.elev * RAD, ce = Math.cos(e), se = Math.sin(e);
    const view = v => { const x1 = v[0] * cy + v[2] * sy, z1 = -v[0] * sy + v[2] * cy; return [x1, v[1] * ce + z1 * se, -v[1] * se + z1 * ce]; };
    return {
      view, cy, sy, se, ce,
      vec: (x, yy, z) => view([x, yy, z]).slice(0, 2),            // relative vector in screen px
      ground: (x, z) => view([x, 0, z]).slice(0, 2),               // point on the floor (character frame) -> screen
    };
  }

  // ------------------------------------------------------------------ the full chest frame
  function makeFrame(p) {
    const yaw = (p.yaw || 0) * RAD, pit = (p.pitch || 0) * RAD, rol = (p.tilt || 0) * RAD, el = DIM.elev * RAD;
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pit), sp = Math.sin(pit), cr = Math.cos(rol), sr = Math.sin(rol);
    const ce = Math.cos(el), se = Math.sin(el);
    const hx = p.hip[0], hy = p.hip[1];
    const th = (clamp(p.lidOpen ?? 0, -0.05, 1.32) + (p.breath || 0) * 0.045) * DIM.lidMax * RAD;
    const ct = Math.cos(th), st = Math.sin(th);
    const dir = v => {
      let x = v[0], y = v[1], z = v[2];
      let y1 = y * cp + z * sp, z1 = -y * sp + z * cp; y = y1; z = z1;            // pitch: top toward +z
      let x1 = x * cr - y * sr; y1 = x * sr + y * cr; x = x1; y = y1;             // roll (clockwise)
      x1 = x * cy + z * sy; z1 = -x * sy + z * cy; x = x1; z = z1;                 // yaw
      y1 = y * ce + z * se; z1 = -y * se + z * ce;                                  // camera looks down
      return [x, y1, z1];
    };
    const P = v => { const r = dir(v); return [hx + r[0], hy + r[1], r[2]]; };
    const hinge = v => { const dy = v[1] + DIM.Hb, dz = v[2] + DIM.D / 2; return [v[0], -DIM.Hb + dy * ct - dz * st, -DIM.D / 2 + dy * st + dz * ct]; };
    const hingeDir = v => [v[0], v[1] * ct - v[2] * st, v[1] * st + v[2] * ct];
    return { P, dir, LP: v => P(hinge(v)), LD: v => dir(hingeDir(v)), th, yawDeg: p.yaw || 0, cy, sy, se, ce };
  }

  // ------------------------------------------------------------------ IK
  // two-bone IK in screen space; pole3 = preferred bend direction in VIEW space (x, y, z). The limb is assumed to lie
  // in the screen plane, the knee/elbow leaves it along the pole: a forward-bending knee seen from the front barely
  // moves sideways (front view), seen from the side it bends fully (side view).
  function ik(A, T, l1, l2, pole3, stretch = 1.05) {
    let d0 = sub(T, A), d = len(d0);
    const u = d > 1e-6 ? mul(d0, 1 / d) : [0, 1];
    let k = 1;
    if (d > (l1 + l2) * 0.999) { k = Math.min(stretch, d / ((l1 + l2) * 0.999)); l1 *= k; l2 *= k; }
    const dd = clamp(d, Math.abs(l1 - l2) + 1e-3, (l1 + l2) * 0.999);
    const a = (l1 * l1 - l2 * l2 + dd * dd) / (2 * dd), h = Math.sqrt(Math.max(0, l1 * l1 - a * a));
    const pd = pole3[0] * u[0] + pole3[1] * u[1];
    let q = [pole3[0] - pd * u[0], pole3[1] - pd * u[1], pole3[2]];
    const ql = Math.hypot(q[0], q[1], q[2]);
    let off;
    if (ql < 1e-6) off = perp(u); else { q = [q[0] / ql, q[1] / ql, q[2] / ql]; off = [q[0], q[1]]; }
    const J = add(add(A, mul(u, a)), mul(off, h));
    const End = add(A, mul(u, dd));
    return { A, J, E: End, k, l1, l2 };
  }

  // ------------------------------------------------------------------ deep merge / lerp of option objects
  const isObj = v => v && typeof v === 'object' && !Array.isArray(v);
  function merge(a, b) {
    const out = Object.assign({}, a);
    if (!b) return out;
    for (const k of Object.keys(b)) {
      if (b[k] === undefined) continue;
      out[k] = isObj(b[k]) && isObj(a && a[k]) ? merge(a[k], b[k]) : b[k];
    }
    return out;
  }
  function lerpPose(a, b, k) {
    if (typeof a === 'number' && typeof b === 'number') return lerp(a, b, k);
    if (Array.isArray(a) && Array.isArray(b)) return a.map((v, i) => lerpPose(v, b[i] ?? v, k));
    if (isObj(a) && isObj(b)) {
      const out = {};
      for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
        if (!(key in a)) out[key] = b[key]; else if (!(key in b)) out[key] = a[key]; else out[key] = lerpPose(a[key], b[key], k);
      }
      return out;
    }
    if (a === undefined) return b;
    if (b === undefined) return a;
    return k < 0.5 ? a : b;
  }

  // ------------------------------------------------------------------ expressions
  // glow eyes (light on the dark mouth) for the cute range; BRIGHT eyes (cream-gold sclera, tiny dark pupil) for the
  // shocked / tense range so wide eyes stay bright instead of going muddy.
  const EXPR = {
    neutral: { eye: { irisScale: 0.64, pupil: 'oval', pupilScale: 0.95, h: 0.74, highlightSize: 0.22, highlight2: true }, blush: 0.55 },
    happy: { eye: { closed: 'smile' }, blush: 0.85, blushLines: 2 },
    nervous: { bright: 0.85, eye: { irisScale: 0.36, pupil: 'oval', pupilScale: 0.55, h: 0.8, look: { x: 0.5, y: -0.1 }, highlightSize: 0.26 }, blush: 0.35, brows: { tilt: 0.5, arch: 0.1, dy: -0.02 }, fx: { sweat: 1 } },
    hungry: { eye: { irisScale: 0.76, pupil: 'star', pupilColor: '#FFF8DE', pupilScale: 1.1, h: 0.76, highlight2: true }, blush: 0.65, fx: { drool: 1, sparkle: 1 } },
    annoyed: { bright: 0.62, eye: { open: 0.5, lowerRaise: 0.25, irisScale: 0.46, pupil: 'slit', pupilScale: 0.8, look: { x: -0.6, y: 0.15 }, h: 0.66 }, blush: 0.15, brows: { tilt: -0.28, arch: 0.02, dy: 0.06 } },
    scared: { bright: 0.92, eye: { irisScale: 'dot', pupilScale: 0.7, h: 0.88, open: 1, look: { x: 0, y: 0.05 } }, blush: 0.1, brows: { tilt: 0.65, arch: 0.08, dy: -0.06 }, fx: { sweat: 1, tears: 0.6 } },
    sleepy: { eye: { closed: 'sleep' }, blush: 0.45, fx: { zzz: 1 } },
    smitten: { eye: { pupil: 'heart', pupilColor: '#FF9DB8', irisScale: 0.78, h: 0.76, pupilScale: 1.15, highlight2: true }, blush: 1.25, blushLines: 3, fx: { hearts: 1 } },
    pounce: { bright: 0.95, eye: { h: 0.9, irisScale: 0.4, pupil: 'slit', pupilScale: 0.7, tilt: 0.18 }, blush: 0.0, brows: { tilt: -0.45, arch: 0.04, dy: 0.02 }, teeth: 1.25 },
    yawn: { eye: { closed: 'flat', lashes: 3 }, blush: 0.4, fx: { tears: 0.5 } },
    effort: { eye: { open: 0.78, irisScale: 0.5, pupil: 'oval', pupilScale: 0.75, lowerRaise: 0.18, h: 0.66 }, blush: 0.6, brows: { tilt: 0.3, arch: 0.06 } },
  };

  // ------------------------------------------------------------------ state presets
  const ANK = DIM.ankle;
  function standPose(yaw = 0) {
    const F = yawFrame(yaw), hip = [0, -DIM.standHip];
    const leg = sd => ({ foot: add(F.ground(sd * 0.3 * W, 0.0), [0, -ANK]), kneeOut: -0.5, toe: 0, grow: 1 });
    // arms dangle: elbows up and out (DS mimic), long forearms hanging, wrists just below the chest
    const arm = sd => ({ mode: 'arm', hand: add(hip, F.vec(sd * 1.16 * W, -0.22 * W, -0.04 * W)), handAng: Math.PI / 2 - sd * 0.12, curl: 0.24, spread: 0.5, curlDir: -sd, grow: 1 });
    return {
      yaw, hip, tilt: 0, pitch: 0, lidOpen: DIM.idleLid, breath: 0,
      legs: { L: leg(-1), R: leg(1) }, arms: { L: arm(-1), R: arm(1) },
      tongue: { len: 1.32, ang: Math.PI / 2, swing: 0, curl: 0.12, wave: 0.05, phase: 0, width: 1 },
      chain: { sway: 0.05, swing: 0, links: 17 },
      expr: 'neutral', look: { x: Math.sign(yaw) * 0.25, y: 0.05 }, blink: 1,
    };
  }
  function dormantPose(yaw = -10) {
    const p = standPose(yaw);
    return merge(p, {
      yaw, hip: [0, 0], lidOpen: 0, breath: 0, tilt: 0,
      legs: { L: { grow: 0 }, R: { grow: 0 } }, arms: { L: { mode: 'none', grow: 0 }, R: { mode: 'none', grow: 0 } },
      tongue: { len: 0 }, chain: { floor: true, sway: 0 }, expr: 'neutral', look: { x: 0, y: 0 },
    });
  }
  // wrist target inside the gap, just above the lower lip, so the fingers hook over the lip and grip the front wall
  function lipGrip(F, sd, k = 0.33) { return add([0, 0], F.vec(sd * k * W, -DIM.Hb - 0.075 * W, 0.27 * W)); }
  function peekPose(yaw = -10) {
    const p = dormantPose(yaw), F = yawFrame(yaw);
    return merge(p, {
      lidOpen: 0.25, chain: { floor: true },
      arms: {
        L: { mode: 'hand', hand: lipGrip(F, -1, 0.34), handAng: Math.PI / 2 + 0.12, curl: 0.62, spread: 0.5, curlDir: 1, thumb: 0.5, grow: 1 },
        R: { mode: 'hand', hand: lipGrip(F, 1, 0.33), handAng: Math.PI / 2 - 0.1, curl: 0.55, spread: 0.45, curlDir: -1, thumb: 0.5, grow: 1 },
      },
      expr: 'neutral', eye: { open: 0.85 }, look: { x: -0.6, y: 0.3 },
    });
  }
  // the mid-transformation pose: chest lifting, legs half out and spidered, palms pushing on the floor
  function pushPose(yaw = 0) {
    const p = standPose(yaw), F = yawFrame(yaw), hip = [0, -0.62 * W];
    const leg = sd => ({ foot: add(F.ground(sd * 0.62 * W, 0.05 * W), [0, -ANK]), kneeOut: 1, toe: 0.1, grow: 0.82 });
    const arm = sd => ({ mode: 'arm', hand: add(F.ground(sd * 1.02 * W, 0.12 * W), [0, -0.035 * W]), handAng: Math.PI / 2 - sd * 1.15, curl: 0.05, spread: 0.85, curlDir: sd, elbowUp: 1, grow: 0.95 });
    return merge(p, {
      hip, tilt: -5, pitch: 4, lidOpen: 0.6, legs: { L: leg(-1), R: leg(1) }, arms: { L: arm(-1), R: arm(1) },
      tongue: { len: 0.55, curl: 0.25, swing: 0.1 }, chain: { floor: false, sway: 0.1 }, expr: 'effort', look: { x: 0, y: 0.35 },
    });
  }
  function risePose(yaw = 0) {
    const p = standPose(yaw), F = yawFrame(yaw), hip = [0, -1.25 * W];
    const leg = sd => ({ foot: add(F.ground(sd * 0.42 * W, 0.0), [0, -ANK]), kneeOut: 0.35, toe: 0, grow: 1 });
    const arm = sd => ({ mode: 'arm', hand: add(hip, F.vec(sd * 1.05 * W, 0.45 * W, 0.1 * W)), handAng: Math.PI / 2 - sd * 0.5, curl: 0.25, spread: 0.6, curlDir: -sd, grow: 1 });
    return merge(p, { hip, tilt: 3, pitch: 2, lidOpen: 0.7, legs: { L: leg(-1), R: leg(1) }, arms: { L: arm(-1), R: arm(1) }, tongue: { len: 1.0, swing: -0.15 }, expr: 'neutral' });
  }
  function unfoldPose(k, yaw = 0) {
    // keys: 0 dormant, .18 lid cracks + hands creep, .45 push-up (legs sprout), .72 rise, 1 stand
    const keys = [[0, dormantPose(yaw)], [0.18, peekPose(yaw)], [0.45, pushPose(yaw)], [0.72, risePose(yaw)], [1, standPose(yaw)]];
    k = clamp(k);
    for (let i = 1; i < keys.length; i++) {
      if (k <= keys[i][0]) {
        const [k0, a] = keys[i - 1], [k1, b] = keys[i];
        const e = E.easeInOutCubic((k - k0) / (k1 - k0));
        let out = lerpPose(a, b, e);
        if (i === 1) out = merge(out, { arms: { L: { mode: k < 0.08 ? 'none' : 'hand' }, R: { mode: k < 0.08 ? 'none' : 'hand' } } });
        else if (i === 2) {
          // the hands never leave their arms behind: they slide along the lip to the mouth corners (arm still hidden
          // inside), then the arms unfold OUT of the corners and reach for the floor; the IK clamps the wrist to the
          // reach of the growing arm, so a hand is always attached
          const F = yawFrame(yaw), pa = a.arms, pb = b.arms, slide = 0.22;
          const arms = {};
          for (const [key, sd] of [['L', -1], ['R', 1]]) {
            const corner = lipGrip(F, sd, 0.47);
            if (e < slide) {
              const q = e / slide;
              arms[key] = merge(pa[key], { mode: 'hand', hand: lp(pa[key].hand, corner, sstep(0, 1, q)), grow: 1 });
            } else {
              const q = (e - slide) / (1 - slide), qq = sstep(0, 1, q);
              arms[key] = merge(lerpPose(pa[key], pb[key], qq), { mode: 'arm', hand: lp(corner, pb[key].hand, qq), grow: lerp(0.42, pb[key].grow ?? 1, sstep(0, 0.7, q)), elbowUp: 1 });
            }
          }
          out = merge(out, { arms });
        }
        out = merge(out, { chain: { floor: k < 0.3 } });
        return out;
      }
    }
    return standPose(yaw);
  }
  function pose(state = 'stand', unfold = 1, yaw) {
    if (state === 'dormant') return dormantPose(yaw ?? -10);
    if (state === 'peek') return peekPose(yaw ?? -10);
    if (state === 'unfold') return unfoldPose(unfold, yaw ?? 0);
    return standPose(yaw ?? 0);
  }

  // ------------------------------------------------------------------ walk + jump + pounce helpers
  function walkPose(phase, o = {}) {
    const yaw = o.yaw ?? -35, F = yawFrame(yaw), stride = (o.stride ?? 0.9) * W, lift = (o.lift ?? 0.32) * W, bounce = o.bounce ?? 1;
    const fs = Math.sign(yaw || -1);                                // facing: -1 screen-left, +1 screen-right
    const beta = 0.56, ph = ((phase % 1) + 1) % 1;
    const base = standPose(yaw);
    const foot = (sd, off) => {
      const q = (ph + off) % 1;
      let z, up = 0, toe = 0;
      if (q < beta) { z = lerp(stride / 2, -stride / 2, q / beta); toe = q > beta - 0.12 ? lerp(0, 0.5, (q - beta + 0.12) / 0.12) : 0; }
      else {
        const k = (q - beta) / (1 - beta), e = E.easeInOutSine(k);
        z = lerp(-stride / 2, stride / 2, e); up = lift * Math.sin(Math.PI * k) ** 0.85; toe = lerp(0.5, -0.2, sstep(0.2, 1, k));
      }
      return { foot: add(F.ground(sd * 0.25 * W, z), [0, -ANK - up]), toe, kneeOut: 0.1, grow: 1 };
    };
    const L = foot(-1, 0), R = foot(1, 0.5);
    const bob = Math.cos(TAU * 2 * (ph - 0.36));                // -1 = DOWN just after each contact, +1 = UP before the next
    const hip = [F.ground(Math.sin(TAU * ph) * 0.05 * W, 0)[0], -(1.7 * W + 0.13 * W * bounce * bob)];
    const sw = (sd, off) => {                                     // loose pendulum arm, lags the opposite leg, hangs LOW
      const q = TAU * (ph + off) - 0.9;
      return {
        mode: 'arm', hand: add(hip, F.vec(sd * 1.0 * W, 0.5 * W - 0.14 * W * Math.cos(q * 2), 0.78 * W * Math.sin(q))),
        handAng: Math.PI / 2 - sd * 0.08 + 0.42 * Math.sin(q - 0.8) * fs, curl: 0.32 + 0.14 * Math.sin(q - 0.6), spread: 0.32, curlDir: -sd, grow: 1, elbowUp: 0.75,
      };
    };
    const wob = Math.sin(TAU * 2 * ph - 2.0) * bounce;              // the secondary swing, a beat behind the bob
    return merge(base, {
      hip, tilt: 4.5 * Math.sin(TAU * ph) * bounce, pitch: 5 + 2 * bob * bounce, lidOpen: 0.76 + 0.06 * Math.sin(TAU * 2 * ph - 2.2) * bounce,
      legs: { L, R }, arms: { L: sw(-1, 0.5), R: sw(1, 0) },
      // the tongue TRAILS behind the travel direction (tip lags), the chain swings opposite to it
      tongue: { len: 1.2, swing: 0.2 * fs + 0.16 * wob, curl: 0.1 + 0.12 * Math.sin(TAU * 2 * ph - 2.6), wave: 0.14, phase: TAU * 2 * ph },
      chain: { swing: 0.3 * fs - 0.32 * wob, sag: 0.9, sway: 0.2, t: o.t ?? ph * 1.1 },
      look: { x: -fs * 0.35, y: 0.05 }, expr: o.expr || 'neutral', advance: stride / beta,
    });
  }

  function jumpPose(k, o = {}) {
    const yaw = o.yaw ?? -35, F = yawFrame(yaw), Hj = (o.height ?? 1.0) * W, dist = (o.dist ?? 2.2) * W;
    k = clamp(k);
    const fwd = Math.sign(yaw || 1);
    const st = standPose(yaw);
    const legAt = (sd, x, z, lift, toe, ko) => ({ foot: add(F.ground(sd * x * W, z * W), [0, -ANK - lift * W]), toe, kneeOut: ko, grow: 1 });
    const armAt = (sd, x, y, z, ang, curl, spread) => ({ mode: 'arm', hand: F.vec(sd * x * W, y * W, z * W), handAng: ang, curl, spread, curlDir: -sd, grow: 1 });
    // keyframes: hip (W above the feet baseline, + = up), ft [x, z, lift, toe, kneeOut], hand [x, y, z] (z + = forward),
    // hang (hand angle offset), lid, pitch, tongue {ang deg (authored facing screen-left: 0 = back/right), curl, len}
    const K = [
      { t: 0.0, hip: 1.8, lid: 0.75, pitch: 0, ft: [0.29, 0, 0, 0, -0.28], hand: [1.1, -1.56, -0.04], hang: 0.1, curl: 0.34, tl: { ang: 90, curl: 0.12, len: 1.32 }, expr: 'neutral' },
      { t: 0.2, hip: 0.98, lid: 0.0, pitch: 14, ft: [0.4, 0.02, 0, 0, 0.7], hand: [1.0, -0.12, -0.35], hang: 0.9, curl: 0.15, tl: { ang: 90, curl: 0.2, len: 0.0 }, expr: 'effort' },
      { t: 0.29, hip: 2.05, lid: 1.05, pitch: -8, ft: [0.22, -0.3, 0, 0.75, -0.1], hand: [1.35, -2.85, 0.0], hang: -1.45, curl: 0.12, tl: { ang: 75, curl: -0.3, len: 1.3 }, expr: 'pounce' },
      { t: 0.42, hip: 1.45, lid: 1.1, pitch: 4, ft: [0.4, 0.1, 0.55, 0.8, 0.45], hand: [1.15, -2.8, 0.35], hang: -0.9, curl: 0.35, tl: { ang: 40, curl: -0.6, len: 1.2 }, expr: 'pounce' },
      { t: 0.55, hip: 1.25, lid: 1.15, pitch: 8, ft: [0.45, 0.25, 0.95, 0.9, 0.6], hand: [1.2, -2.6, 0.2], hang: -0.6, curl: 0.55, tl: { ang: 22, curl: -0.75, len: 1.15 }, expr: 'happy' },
      { t: 0.7, hip: 1.3, lid: 0.9, pitch: 2, ft: [0.35, 0.05, 0.4, 0.5, 0.35], hand: [1.3, -2.95, 0.0], hang: -0.5, curl: 0.4, tl: { ang: -48, curl: -0.5, len: 1.1 }, expr: 'pounce' },
      { t: 0.8, hip: 1.85, lid: 1.0, pitch: -4, ft: [0.33, 0.05, 0.0, 0.0, 0.2], hand: [1.35, -3.0, -0.1], hang: -0.9, curl: 0.25, tl: { ang: -32, curl: -0.45, len: 1.18 }, expr: 'scared' },
      { t: 0.86, hip: 0.82, lid: 0.45, pitch: 16, ft: [0.5, 0.0, 0, 0, 0.85], hand: [0.85, -0.03, 0.4], hang: 1.25, curl: 0.75, tl: { ang: 80, curl: 0.5, len: 1.0 }, expr: 'scared' },
      { t: 0.93, hip: 1.95, lid: 0.95, pitch: -4, ft: [0.3, 0, 0, 0, -0.2], hand: [0.82, -1.3, 0.3], hang: 0.55, curl: 0.42, tl: { ang: 95, curl: -0.2, len: 1.35 }, expr: 'happy' },
      { t: 1.0, hip: 1.8, lid: 0.75, pitch: 0, ft: [0.29, 0, 0, 0, -0.28], hand: [1.1, -1.56, -0.04], hang: 0.1, curl: 0.34, tl: { ang: 90, curl: 0.12, len: 1.32 }, expr: 'neutral' },
    ];
    let i = 1; while (i < K.length - 1 && k > K[i].t) i++;
    const a = K[i - 1], b = K[i], u = E.easeInOutSine(clamp((k - a.t) / (b.t - a.t)));
    const L = (x, y) => lerp(x, y, u);
    const hipH = L(a.hip, b.hip) * W;
    // flight: the ground point travels and the whole body rises on a parabola between take-off and touch-down
    const t0 = 0.3, t1 = 0.8, fk = clamp((k - t0) / (t1 - t0));
    const air = k > t0 && k < t1 ? 4 * fk * (1 - fk) * Hj : 0;
    const dx = sstep(0.26, 0.82, k) * dist * fwd;
    const ft = a.ft.map((v, j) => L(v, b.ft[j]));
    const hand = a.hand.map((v, j) => L(v, b.hand[j]));
    const hip = [0, -hipH - air];
    const legs = {
      L: legAt(-1, ft[0], ft[1], ft[2] + air / W, ft[3], ft[4]),
      R: legAt(1, ft[0] * 0.92, ft[1] - 0.08, ft[2] * 0.85 + air / W, ft[3], ft[4]),
    };
    const hang = L(a.hang, b.hang);
    const arms = {
      L: armAt(-1, hand[0], hand[1] - air / W, hand[2], Math.PI / 2 + hang, L(a.curl, b.curl), 0.5),
      R: armAt(1, hand[0] * 0.95, hand[1] * 0.97 - air / W, hand[2] - 0.1, Math.PI / 2 - hang, L(a.curl, b.curl), 0.5),
    };
    const flap = k > t0 && k < t1 ? 0.1 * Math.sin(k * 60) : 0;
    // tongue keys are authored facing screen-left (back = screen-right); mirror them when it faces right. During the
    // flight it streams up and BACK (behind the travel direction), never across the eyes.
    const tAng = L(a.tl.ang, b.tl.ang), tCurl = L(a.tl.curl, b.tl.curl);
    const tl = { ang: (fwd < 0 ? tAng : 180 - tAng) * RAD, curl: fwd < 0 ? tCurl : -tCurl, len: L(a.tl.len, b.tl.len), swing: 0, wave: 0.22 * (air > 0 ? 1 : 0.3), phase: k * 40 };
    const out = merge(st, {
      hip, pitch: L(a.pitch, b.pitch), tilt: 0, lidOpen: L(a.lid, b.lid) + flap, legs, arms, tongue: tl,
      chain: { swing: air > 0 ? -0.9 * fwd : 0, sag: air > 0 ? 0.55 : 0.95, sway: 0.25, t: k * 3 }, expr: u < 0.5 ? a.expr : b.expr,
    });
    out.dx = dx; out.air = air;
    return out;
  }

  function pouncePose(o = {}) {
    const dir = o.dir ?? -1;
    const yaw = 20 * dir;
    const target = o.target ? o.target : [0.8 * W * dir, -2.15 * W];
    const grab = (o.grab ?? 0.3) * W;
    const hip = [0.12 * W * -dir, -2.92 * W];
    const p = standPose(yaw);
    // authored diving screen-left (dir = -1); x values flip with dir
    const X = x => x * -dir;
    return merge(p, {
      yaw, hip, pitch: 20, tilt: 40 * dir, lidOpen: 1.16, expr: 'pounce', look: { x: 0.35 * dir, y: 0.55 },
      legs: {
        L: { foot: [hip[0] + X(0.62 * W), hip[1] - 1.5 * W], toe: 2.3, kneeOut: 0.2, grow: 1 },
        R: { foot: [hip[0] + X(1.12 * W), hip[1] - 1.2 * W], toe: 2.1, kneeOut: 0.3, grow: 1 },
      },
      arms: {
        L: { mode: 'arm', hand: [target[0] - X(grab * 1.05), target[1] + 0.02 * W], handAng: Math.PI / 2 + X(0.22), curl: 0.62, spread: 1, curlDir: X(1), elbowUp: 1, thumb: 0.4 },
        R: { mode: 'arm', hand: [target[0] + X(grab), target[1] - 0.04 * W], handAng: Math.PI / 2 - X(0.3), curl: 0.62, spread: 1, curlDir: X(-1), elbowUp: 1, thumb: 0.4 },
      },
      tongue: { len: 1.25, ang: dir < 0 ? -0.18 : Math.PI + 0.18, curl: -0.55 * X(1), wave: 0.35, phase: 2.2, swing: 0, behind: true },
      chain: { swing: -1.9 * X(1), sag: 0.35, sway: 0.18, t: 0.5 },
    });
  }

  // ------------------------------------------------------------------ resolve options
  function resolve(opts) {
    const base = pose(opts.state || 'stand', opts.unfold ?? 1, opts.yaw);
    let p = merge(base, opts);
    if (opts.yaw !== undefined) p.yaw = opts.yaw;
    if (opts.realChest) {
      // a plain chest from the same model: shut, no seam, no limbs, no face, the chain coiled neatly at the side-back
      p = merge(p, { lidOpen: 0, breath: 0, hip: [p.hip[0], 0], pitch: 0, tilt: 0, crouch: 0, tongue: { len: 0 }, chain: { floor: true, real: true, pts: null }, fx: {} });
      p.legs = { L: { grow: 0 }, R: { grow: 0 } }; p.arms = { L: { mode: 'none', grow: 0 }, R: { mode: 'none', grow: 0 } };
      p.realChest = true;
    }
    p.hip = p.hip.slice();
    if (p.crouch) {
      const c = clamp(p.crouch);
      const fy = Math.min(p.legs.L.foot[1], p.legs.R.foot[1]);
      p.hip[1] = lerp(p.hip[1], fy - 0.62 * W, c * 0.75);
    }
    p.ex = merge(EXPR.neutral, EXPR[p.expr] || {});
    if (opts.blush !== undefined) p.ex.blush = opts.blush;              // per-shot blush override (0..1.3)
    p.fx = merge(p.ex.fx || {}, opts.fx || {});
    p.parts = merge({ legs: true, arms: true, tongue: true, chain: true, fx: true }, opts.parts || {});
    if (p.realChest) Object.assign(p.parts, { legs: false, arms: false, tongue: false, fx: false });
    return p;
  }

  // ------------------------------------------------------------------ geometry solve
  function solve(p) {
    const R = makeFrame(p);
    const F = yawFrame(p.yaw || 0);
    const out = { R, F, legs: {}, arms: {} };
    const sideZ = sd => R.dir([sd, 0, 0])[2];          // + = near the camera
    out.near = sideZ(1) > 0.02 ? 1 : sideZ(-1) > 0.02 ? -1 : 0;
    for (const sd of [-1, 1]) {
      const key = sd < 0 ? 'L' : 'R', L = p.legs[key] || {}, g = clamp(L.grow ?? 1);
      if (g <= 0.02) continue;
      const hip = R.P([sd * DIM.hipX, DIM.hipY, 0]).slice(0, 2);
      const ko = L.kneeOut ?? -0.25;
      const pole = F.view([sd * ko * 0.8, -0.05, 1]);
      const sol = ik(hip, L.foot, DIM.thigh * g, DIM.shin * g, pole, 1.06);
      out.legs[key] = { sd, g, hip, knee: sol.J, ankle: sol.E, toe: L.toe || 0, splay: L.splay, pole };
    }
    for (const sd of [-1, 1]) {
      const key = sd < 0 ? 'L' : 'R', A = p.arms[key] || {}, g = clamp(A.grow ?? 1), mode = A.mode || 'arm';
      if (mode === 'none' || g <= 0.02) continue;
      const sh = R.P([sd * DIM.shX, DIM.shY, DIM.shZ]).slice(0, 2);
      if (mode === 'hand') { out.arms[key] = { sd, g, mode, wrist: A.hand, handAng: A.handAng ?? Math.PI / 2, A }; continue; }
      const up = A.elbowUp ?? 0.8;
      const pole = F.view([sd * 1, -up, -0.35]);
      const sol = ik(sh, A.hand, DIM.upper * g, DIM.fore * g, pole, 1.04);
      const fa = ang(sub(sol.E, sol.J));
      out.arms[key] = { sd, g, mode, sh, elbow: sol.J, wrist: sol.E, handAng: A.handAng ?? fa + (A.handBend || 0), A };
    }
    // mouth landmarks
    const th = R.th;
    const lipL = R.P([-W / 2 + 0.02 * W, -DIM.Hb, DIM.D / 2 - 0.02 * W]), lipR = R.P([W / 2 - 0.02 * W, -DIM.Hb, DIM.D / 2 - 0.02 * W]);
    const upL = R.LP([-W / 2 + DIM.rim, -DIM.Hb, DIM.D / 2 + DIM.o - DIM.rim * 0.55]), upR = R.LP([W / 2 - DIM.rim, -DIM.Hb, DIM.D / 2 + DIM.o - DIM.rim * 0.55]);
    out.lip = { L: lipL, R: lipR, uL: upL, uR: upR };
    out.gap = len(sub(lp(upL, upR, 0.5), lp(lipL, lipR, 0.5)));
    out.mouth = lp(lp(lipL, lipR, 0.5), lp(upL, upR, 0.5), 0.5);
    // the eyes sit LOW on the back wall of the mouth, at the hinge (throat), just above the lower teeth: the dark
    // above them is the palate, so the open lid reads as a mouth and not as a screen
    const hgL = R.P([-W / 2 + DIM.rim, -DIM.Hb, -DIM.D / 2]), hgR = R.P([W / 2 - DIM.rim, -DIM.Hb, -DIM.D / 2]);
    // lifted clear of the lower tooth row (the eye bottoms sit on the lip line, not behind the teeth)
    const upV = nrm(sub(lp(upL, upR, 0.5), lp(lipL, lipR, 0.5))).slice(0, 2), lift = (p.eyeLift ?? 0.07) * W * clamp((th - 0.12) / 0.45);
    out.eyes = [-1, 1].map(sd => {
      const u = 0.5 + sd * DIM.eyeU;
      return add(lp(lp(hgL, hgR, u), lp(upL, upR, u), p.eyeAt ?? DIM.eyeAt).slice(0, 2), mul(upV, lift));
    });
    out.lipAng = ang(sub(lipR, lipL));
    out.faceAng = ang(sub(upR, upL));
    out.th = th;
    const T = p.tongue || {};
    const tLen = (T.len ?? 0) * clamp((th - 0.06) / 0.22);
    if (tLen > 0.02 && p.parts.tongue) {
      const root = add(lp(lipL, lipR, 0.5), mul(dirA(out.lipAng - Math.PI / 2), (T.behind ? 0.05 : 0.025) * W));
      const n = 16, Lt = tLen * W, seg = Lt / n;
      const pts = [root];
      const a0 = (T.ang ?? Math.PI / 2) + (T.swing || 0) + (p.tilt || 0) * RAD * 0.3;
      for (let i = 0; i < n; i++) {
        const u = (i + 0.5) / n;
        const a = a0 + (T.curl || 0) * u * u * 2.2 + (T.wave || 0) * Math.sin((T.phase || 0) - u * 3.2) * u;
        pts.push(add(pts[pts.length - 1], mul(dirA(a), seg)));
      }
      out.tongue = { pts, w: (T.width ?? 1) * 0.2 * W * clamp(0.5 + tLen / 0.6), behind: !!T.behind, foldU: clamp(0.04 * W / Lt, 0, 0.5) };
    }
    if (p.parts.chain) {
      const anc = R.P([W / 2 + 0.01 * W, -0.62 * DIM.Hb, 0.12 * DIM.D]);
      out.chainAnchor = anc.slice(0, 2);
      out.chainNear = sideZ(1) >= -0.02;
    }
    return out;
  }

  // ------------------------------------------------------------------ painting helpers
  // rounded polygon that never overshoots: the tangent length at each corner is clamped to 45 % of the shorter
  // neighbouring edge, so projected slivers (faces seen edge-on) stay inside their own outline
  function addSafeRound(g, pts, r) {
    const n = pts.length;
    if (n < 3) return;
    const m0 = [(pts[n - 1][0] + pts[0][0]) / 2, (pts[n - 1][1] + pts[0][1]) / 2];
    g.moveTo(m0[0], m0[1]);
    for (let i = 0; i < n; i++) {
      const pv = pts[(i - 1 + n) % n], c = pts[i], nx = pts[(i + 1) % n];
      const a = [pv[0] - c[0], pv[1] - c[1]], b = [nx[0] - c[0], nx[1] - c[1]];
      const la = Math.hypot(a[0], a[1]), lb = Math.hypot(b[0], b[1]);
      if (la < 1e-6 || lb < 1e-6) { g.lineTo(c[0], c[1]); continue; }
      const cosI = clamp((a[0] * b[0] + a[1] * b[1]) / (la * lb), -1, 1), inter = Math.acos(cosI);
      if (inter < 0.06 || inter > Math.PI - 0.02) { g.lineTo(c[0], c[1]); continue; }
      const tmax = 0.45 * Math.min(la, lb), t = Math.min(r / Math.tan(inter / 2), tmax), rr = t * Math.tan(inter / 2);
      g.arcTo(c[0], c[1], nx[0], nx[1], rr);
    }
    g.closePath();
  }
  const safeRoundPoly = (g, pts, r, fill) => { g.beginPath(); addSafeRound(g, pts, r); g.fillStyle = fill; g.fill(); };
  const pathPts = (g, pts) => { g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath(); };
  function convexHull(pts) {
    const P = pts.map(q => [q[0], q[1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    if (P.length < 3) return P;
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const q of P) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (let i = P.length - 1; i >= 0; i--) { const q = P[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    up.pop(); lo.pop();
    return lo.concat(up);
  }
  function toneOf(n) {
    const k = n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2];
    return k > 0.66 ? 'light' : k > 0.02 ? 'base' : 'shade';
  }
  const woodTone = t => (t === 'light' ? COL.woodLight : t === 'base' ? COL.wood : COL.woodShade);
  function faceFrame(Pf, Df, origin, U, V) {
    const o = Pf(origin), u = Df(U), v = Df(V), n = Df(cross3(U, V));
    return { o, u, v, n, vis: n[2] > 0.005 };
  }
  function withFace(g, f, fn) { g.save(); g.transform(f.u[0], f.u[1], f.v[0], f.v[1], f.o[0], f.o[1]); fn(g); g.restore(); }
  function clipPts(g, pts, fn) { g.save(); g.beginPath(); pathPts(g, pts); g.clip(); fn(); g.restore(); }
  function clipUnion(g, list, fn) { g.save(); g.beginPath(); list.forEach(pts => pathPts(g, pts)); g.clip(); fn(); g.restore(); }

  // ------------------------------------------------------------------ the chest
  function paintLid(g, p, sol) {
    const R = sol.R, { D, Hb, Tf, dome, o } = DIM, X0 = -W / 2 - o, X1 = W / 2 + o, Zf = D / 2 + o, Zb = -D / 2;
    const N = 9, prof = [];
    for (let i = 0; i <= N; i++) { const t = i / N, z = lerp(Zb, Zf, t); prof.push([z, -Hb - Tf - dome * Math.sin(Math.PI * t) ** 0.8]); }
    const side = [[Zb, -Hb], [Zf, -Hb], [Zf, -Hb - Tf], ...prof.slice().reverse().slice(1, N), [Zb, -Hb - Tf]];
    const all = [];
    for (const x of [X0, X1]) for (const q of side) all.push(R.LP([x, q[1], q[0]]));
    const hull = convexHull(all);
    safeRoundPoly(g, hull, 0.04 * W, COL.woodShade);
    // inner face = the ROOF OF THE MOUTH: no bright bezel, a thin dark wood rim at the sides, a gum band at the lip,
    // dark flesh with faint palate ridges, darkest in the throat at the hinge (where the eyes sit)
    const inner = faceFrame(R.LP, R.LD, [X0, -Hb, Zf], [1, 0, 0], [0, 0, -1]);
    if (inner.vis) {
      withFace(g, inner, c => {
        const w = X1 - X0, h = Zf - Zb, rim = 0.024 * W;
        S.roundRect(c, 0, 0, w, h, 0.04 * W, C.shade(COL.woodShade, -0.12));
        c.save(); c.beginPath(); S.addRoundRect(c, rim, 0.004 * W, w - 2 * rim, h + 2, [0.035 * W, 0.035 * W, 0, 0]); c.clip();
        c.fillStyle = COL.mouth; c.fillRect(0, 0, w, h + 2);
        let gr = c.createLinearGradient(0, 0, 0, 0.3 * W);
        gr.addColorStop(0, C.rgba(COL.palate, 1)); gr.addColorStop(1, C.rgba(COL.palate, 0));
        c.fillStyle = gr; c.fillRect(0, 0, w, 0.3 * W);
        for (let i = 0; i < 4; i++) {                                         // palate ridges (rugae), faint, wavy
          const y = (0.1 + i * 0.048) * W, a = 0.9 - i * 0.18, pts = [];
          for (let j = 0; j <= 10; j++) { const u = j / 10; pts.push([lerp(0.2, 0.8, u) * w, y + 0.012 * W * Math.sin(u * 9 + i * 1.7) - 0.02 * W * Math.sin(Math.PI * u)]); }
          S.strip(c, pts, u => 0.011 * W * Math.sin(Math.PI * u) ** 0.6, C.rgba('#7A3042', 0.42 * a));
        }
        S.strip(c, [[w / 2, 0.08 * W], [w / 2 + 0.004 * W, 0.2 * W], [w / 2, 0.3 * W]], u => 0.008 * W * Math.sin(Math.PI * u), C.rgba('#7A3042', 0.3));
        gr = c.createLinearGradient(0, 0, 0, 0.07 * W);                       // gum band inside the upper lip
        gr.addColorStop(0, COL.gum); gr.addColorStop(0.4, C.rgba(COL.gum, 0.85)); gr.addColorStop(1, C.rgba(COL.gum, 0));
        c.fillStyle = gr; c.fillRect(0, 0, w, 0.07 * W);
        gr = c.createLinearGradient(0, h * 0.45, 0, h);                       // throat
        gr.addColorStop(0, C.rgba(COL.throat, 0)); gr.addColorStop(1, C.rgba(COL.throat, 0.85));
        c.fillStyle = gr; c.fillRect(0, h * 0.45, w, h * 0.55 + 2);
        c.restore();
      });
    }
    for (const sd of [-1, 1]) {
      const n = R.LD([sd, 0, 0]);
      if (n[2] <= 0.005) continue;
      const x = sd < 0 ? X0 : X1;
      const pts = side.map(q => R.LP([x, q[1], q[0]]));
      g.beginPath(); addSafeRound(g, pts, 0.025 * W); g.fillStyle = woodTone(toneOf(n)) === COL.woodLight ? COL.wood : woodTone(toneOf(n)); g.fill();
      const band = side.slice(2).map(q => R.LP([x, q[1], q[0]]));
      g.save(); g.beginPath(); addSafeRound(g, pts, 0.025 * W); g.clip();
      g.beginPath(); for (let i = 0; i < band.length; i++) (i ? g.lineTo : g.moveTo).call(g, band[i][0], band[i][1]);
      g.strokeStyle = COL.ironShade; g.lineWidth = 0.05 * W; g.lineJoin = 'round'; g.stroke();
      g.restore();
    }
    const front = faceFrame(R.LP, R.LD, [X0, -Hb - Tf, Zf], [1, 0, 0], [0, 1, 0]);
    if (front.vis) {
      withFace(g, front, c => {
        const w = X1 - X0;
        S.roundRect(c, 0, 0, w, Tf, 0.035 * W, woodTone(toneOf(front.n)));
        S.roundRect(c, 0, Tf - 0.03 * W, w, 0.03 * W, [0, 0, 0.035 * W, 0.035 * W], COL.woodShade);
        for (const sx of [0.2, 0.8]) S.roundRect(c, sx * w - 0.04 * W, 0, 0.08 * W, Tf, 0.01 * W, COL.iron);
        for (const sx of [0.2, 0.8]) S.circle(c, sx * w, Tf * 0.55, 0.014 * W, COL.rivet);
      });
    }
    for (let i = 0; i < N; i++) {
      const a = prof[i], b = prof[i + 1];
      const V = norm3([0, b[1] - a[1], b[0] - a[0]]);
      const f = faceFrame(R.LP, R.LD, [X0, a[1], a[0]], [1, 0, 0], V);
      if (!f.vis) continue;
      const segL = Math.hypot(b[1] - a[1], b[0] - a[0]);
      withFace(g, f, c => {
        const w = X1 - X0, tone = toneOf(f.n);
        c.fillStyle = woodTone(tone); c.fillRect(0, -0.6, w, segL + 1.2);
        c.fillStyle = tone === 'light' ? COL.ironLight : COL.iron;
        for (const sx of [0.2, 0.8]) c.fillRect(sx * w - 0.04 * W, -0.6, 0.08 * W, segL + 1.2);
        if (i === Math.floor(N / 2)) { c.fillStyle = COL.woodSeam; c.fillRect(0.02 * W, segL * 0.5, w * 0.16, 0.012 * W); c.fillRect(w * 0.26, segL * 0.5, w * 0.48, 0.012 * W); c.fillRect(w * 0.86, segL * 0.5, w * 0.12, 0.012 * W); }
      });
    }
    return { hull };
  }

  function paintBody(g, p, sol) {
    const R = sol.R, { D, Hb } = DIM;
    const corners = [];
    for (const x of [-W / 2, W / 2]) for (const y of [-Hb, 0]) for (const z of [-D / 2, D / 2]) corners.push(R.P([x, y, z]));
    const hull = convexHull(corners);
    const rimT = DIM.rim * 0.55, topN = R.dir([0, -1, 0]);
    const cut = sol.th > 0.03 && topN[2] > 0.01;
    if (cut) {
      const topIn = [[-W / 2 + rimT, -Hb, -D / 2 + rimT * 0.6], [W / 2 - rimT, -Hb, -D / 2 + rimT * 0.6], [W / 2 - rimT, -Hb, D / 2 - rimT], [-W / 2 + rimT, -Hb, D / 2 - rimT]].map(q => R.P(q));
      g.save(); g.beginPath(); g.rect(-1e5, -1e5, 2e5, 2e5); pathPts(g, topIn); g.clip('evenodd');
    }
    safeRoundPoly(g, hull, 0.045 * W, COL.woodShade);
    const faces = [
      { key: 'front', f: faceFrame(R.P, R.dir, [-W / 2, -Hb, D / 2], [1, 0, 0], [0, 1, 0]), w: W, h: Hb },
      { key: 'right', f: faceFrame(R.P, R.dir, [W / 2, -Hb, D / 2], [0, 0, -1], [0, 1, 0]), w: D, h: Hb },
      { key: 'left', f: faceFrame(R.P, R.dir, [-W / 2, -Hb, -D / 2], [0, 0, 1], [0, 1, 0]), w: D, h: Hb },
      { key: 'back', f: faceFrame(R.P, R.dir, [W / 2, -Hb, -D / 2], [-1, 0, 0], [0, 1, 0]), w: W, h: Hb },
      { key: 'bottom', f: faceFrame(R.P, R.dir, [-W / 2, 0, D / 2], [1, 0, 0], [0, 0, -1]), w: W, h: D },
    ];
    for (const F of faces) {
      if (!F.f.vis) continue;
      const tone = toneOf(F.f.n);
      withFace(g, F.f, c => {
        const col = F.key === 'bottom' ? COL.woodShade : tone === 'light' ? COL.wood : tone === 'base' ? (F.key === 'front' ? COL.wood : COL.woodSide) : COL.woodShade;
        S.roundRect(c, 0, 0, F.w, F.h, 0.04 * W, col);
        if (F.key === 'bottom') return;
        S.roundRect(c, 0, F.h - 0.05 * W, F.w, 0.05 * W, [0, 0, 0.04 * W, 0.04 * W], tone === 'shade' ? C.shade(COL.woodShade, -0.15) : COL.woodShade);
        const seam = col === COL.woodShade ? C.shade(COL.woodShade, -0.18) : COL.woodSeam;
        c.fillStyle = seam;
        for (const v of [0.36, 0.7]) c.fillRect(0.03 * W, F.h * v, F.w - 0.06 * W, 0.011 * W);
        c.globalAlpha = 0.45;
        const r = S.rng('grain' + F.key);
        for (let i = 0; i < 7; i++) {
          const v = [0.17, 0.53, 0.84][i % 3] + r.range(-0.06, 0.06), u0 = r.range(0.06, 0.7), l = r.range(0.12, 0.26);
          c.fillRect(F.w * u0, F.h * v, F.w * l, 0.007 * W);
        }
        c.globalAlpha = 1;
        const iron = tone === 'shade' ? COL.ironShade : COL.iron;
        if (F.key === 'front' || F.key === 'back') {
          for (const sx of [0.2, 0.8]) {
            S.roundRect(c, sx * F.w - 0.04 * W, 0, 0.08 * W, F.h, 0.012 * W, iron);
            S.circle(c, sx * F.w, F.h * 0.2, 0.014 * W, COL.rivet); S.circle(c, sx * F.w, F.h * 0.8, 0.014 * W, COL.rivet);
          }
        } else {
          S.roundRect(c, F.w * 0.5 - 0.04 * W, 0, 0.08 * W, F.h, 0.012 * W, iron);
          S.circle(c, F.w * 0.5, F.h * 0.82, 0.013 * W, COL.rivet);
        }
        const cb = 0.11 * W, cw = 0.045 * W;
        c.fillStyle = iron;
        c.beginPath(); S.addRoundRect(c, 0, F.h - cb, cw, cb, [0, 0, 0, 0.04 * W]); S.addRoundRect(c, 0, F.h - cw, cb, cw, [0, 0, 0, 0.04 * W]); c.fill();
        c.beginPath(); S.addRoundRect(c, F.w - cw, F.h - cb, cw, cb, [0, 0, 0.04 * W, 0]); S.addRoundRect(c, F.w - cb, F.h - cw, cb, cw, [0, 0, 0.04 * W, 0]); c.fill();
        S.circle(c, cw * 0.55, F.h - cw * 0.55, 0.012 * W, COL.rivet); S.circle(c, F.w - cw * 0.55, F.h - cw * 0.55, 0.012 * W, COL.rivet);
        if (F.key === 'front') {
          const cx = F.w / 2, y0 = 0.07 * W, pw = 0.15 * W, ph = 0.2 * W;
          const plate = cc => { cc.moveTo(cx - pw / 2, y0 + pw / 2); cc.arc(cx, y0 + pw / 2, pw / 2, Math.PI, 0); cc.lineTo(cx + pw / 2, y0 + ph * 0.72); cc.quadraticCurveTo(cx + pw / 2, y0 + ph, cx, y0 + ph); cc.quadraticCurveTo(cx - pw / 2, y0 + ph, cx - pw / 2, y0 + ph * 0.72); cc.closePath(); };
          S.cel(c, plate, COL.gold, COL.goldShade, 0.022 * W, 0.022 * W);
          c.beginPath(); c.arc(cx, y0 + pw * 0.48, 0.022 * W, 0, TAU); c.moveTo(cx - 0.012 * W, y0 + pw * 0.55); c.lineTo(cx + 0.012 * W, y0 + pw * 0.55); c.lineTo(cx + 0.02 * W, y0 + ph * 0.8); c.lineTo(cx - 0.02 * W, y0 + ph * 0.8); c.closePath(); c.fillStyle = COL.keyhole; c.fill();
          S.ellipse(c, cx - pw * 0.24, y0 + pw * 0.3, 0.012 * W, 0.02 * W, 0.5, COL.goldLight);
        }
        if (F.key === 'right') {
          S.roundRect(c, F.w * 0.38 - 0.045 * W, F.h * 0.38 - 0.045 * W, 0.09 * W, 0.09 * W, 0.02 * W, COL.ironShade);
          S.circle(c, F.w * 0.38, F.h * 0.38, 0.015 * W, COL.rivet);
        }
      });
    }
    if (cut) g.restore();
    const lf = sol.lip;
    if (sol.th > 0.02) S.strip(g, [lf.L.slice(0, 2), lf.R.slice(0, 2)], 0.018 * W, COL.woodLight);
    return { hull };
  }

  // the hasp: a gold tab on the lid front. Shut: it lies on the body front. Cracked open: it swings down by gravity
  // from its pivot (so it hangs between the eyes, not over one). Open wide: hidden (it points back over the lid).
  function paintHasp(g, p, sol) {
    const R = sol.R, { Hb, Tf, D, o } = DIM;
    const w = 0.12 * W, h = Tf * 0.55 + 0.075 * W;
    if (sol.th < 0.06) {
      const f = faceFrame(R.LP, R.LD, [-0.06 * W, -Hb - Tf * 0.55, D / 2 + o + 0.004 * W], [1, 0, 0], [0, 1, 0]);
      if (!f.vis) return;
      withFace(g, f, c => {
        S.cel(c, cc => S.addRoundRect(cc, 0, 0, w, h, [0.015 * W, 0.015 * W, 0.05 * W, 0.05 * W]), COL.gold, COL.goldShade, 0.018 * W, 0.018 * W);
        S.circle(c, w / 2, h - 0.04 * W, 0.016 * W, COL.goldShade);
        S.circle(c, w / 2, 0.025 * W, 0.012 * W, COL.goldLight);
      });
      return;
    }
    // open: the tab stays on the lid FRONT face (it rides up with the lid, above the gap, never between the eyes)
    const f = faceFrame(R.LP, R.LD, [-0.05 * W, -Hb - Tf * 0.92, D / 2 + o + 0.004 * W], [1, 0, 0], [0, 1, 0]);
    if (!f.vis) return;
    const hh = Tf * 0.8, ww = 0.1 * W;
    withFace(g, f, c => {
      S.cel(c, cc => S.addRoundRect(cc, 0, 0, ww, hh, [0.012 * W, 0.012 * W, 0.04 * W, 0.04 * W]), COL.gold, COL.goldShade, 0.014 * W, 0.014 * W);
      S.circle(c, ww / 2, hh - 0.035 * W, 0.013 * W, COL.goldShade);
      S.circle(c, ww / 2, 0.02 * W, 0.01 * W, COL.goldLight);
    });
  }

  // cavity polygon (the dark mouth) and the face inside it
  function mouthPoly(sol) {
    const R = sol.R, { D, Hb } = DIM;
    const lo = [R.P([-W / 2, -Hb, D / 2]), R.P([W / 2, -Hb, D / 2])];
    const back = [R.P([-W / 2, -Hb, -D / 2]), R.P([W / 2, -Hb, -D / 2])];
    const up = [R.LP([-W / 2, -Hb, D / 2]), R.LP([W / 2, -Hb, D / 2])];
    return [lo[0], lo[1], back[1], up[1], up[0], back[0]].map(q => [q[0], q[1]]);
  }

  function eyeOpts(p, sd) {
    const e = Object.assign({
      w: 1, glow: true, glowColor: COL.glow, iris: S.PAL.iris.gold, pupil: 'oval', lid: 0.15, wing: 0.15, lashes: 3,
      lashLen: 0.25, lashTo: 0.42, teeth: 0, crease: 0, lowerCrease: false, lower: 0.5, glowBlur: 0.08,
    }, p.ex.eye || {}, p.eye || {});
    if (p.look) e.look = Object.assign({}, e.look || {}, p.look);
    if (p.blink !== undefined && p.blink < 1 && !e.closed) e.open = Math.min(e.open ?? 1, p.blink);
    e.mirror = sd > 0;
    return e;
  }
  // one eye in eye-local units (w = 1). Bright mode: a cream-gold disc with a tiny dark pupil and a warm gold lid,
  // bloomed; glow mode: the recipe's light-on-dark eye.
  function drawEye(g, o, bright) {
    if (!bright || o.closed) { S.eye(g, o); return; }
    const dev = Math.hypot(g.getTransform().a, g.getTransform().b);
    const b = Object.assign({}, o, {
      glow: false, sclera: C.rgba(C.mix('#D9AE55', COL.eyeCream, clamp(bright)), 0.88), ink: COL.eyeInk, creaseColor: C.rgba(COL.eyeInk, 0.6),
      iris: ['#B87410', '#E59E22', '#F7C548'], pupilColor: '#24110A', lowerCrease: false,
    });
    S.glow(g, gg => S.eye(gg, b), { blur: 0.06 * dev, alpha: 0.2, wide: true, bounds: { x: -0.8, y: -0.7, w: 1.6, h: 1.4 } });
  }

  function paintFace(g, p, sol, poly) {
    const th = sol.th, ew = DIM.eyeW;
    if (th < 0.012) return;
    const gapK = clamp((sol.gap - 0.05 * W) / (0.25 * W));
    const yawK = Math.abs(Math.sin(sol.R.yawDeg * RAD));
    g.save();
    g.beginPath(); pathPts(g, poly); g.clip();
    const ex = p.ex;
    for (let i = 0; i < 2; i++) {
      const sd = i ? 1 : -1, c = sol.eyes[i];
      const far = sol.near !== 0 && sd !== sol.near;
      const sx = lerp(1, far ? 0.7 : 0.92, yawK);
      const o = eyeOpts(p, sd);
      g.save(); g.translate(c[0], c[1]); g.rotate(sol.faceAng); g.scale(sx * ew, ew);
      const eh = o.h ?? 0.6;
      if (gapK < 0.18 && !o.closed) {
        S.glow(g, gg => { gg.beginPath(); gg.ellipse(0, -0.05, 0.22, 0.09, 0, 0, TAU); gg.fillStyle = COL.glow; gg.fill(); S.ellipse(gg, -0.07, -0.07, 0.06, 0.03, 0, '#FFF6D0'); }, { blur: 0.05 * ew, alpha: 0.9 });
      } else {
        if ((ex.blush ?? 0.5) > 0) {
          g.save(); g.globalCompositeOperation = 'screen';
          const bl = ex.blush;
          S.blush(g, sd * 0.06, eh * 0.5 + 0.02, 0.7 + 0.12 * Math.min(bl, 1.3), clamp(0.95 * bl, 0, 0.9), COL.blush, { lines: 0 });
          g.restore();
          for (let j = 0, n = ex.blushLines || 0; j < n; j++) {
            const lx = sd * 0.06 + (j - (n - 1) / 2) * 0.1, ly = eh * 0.5 + 0.02;
            S.capsule(g, lx + 0.03, ly - 0.045, lx - 0.03, ly + 0.045, 0.018, 0.018, C.rgba('#FF9FB2', 0.85));
          }
        }
        drawEye(g, Object.assign({ x: 0, y: 0 }, o), ex.bright);
        if (ex.brows) {
          const b = ex.brows;
          S.glow(g, gg => S.brow(gg, sd * 0.02, -eh * 0.5 - 0.17 + (b.dy || 0), 0.5, { tilt: b.tilt || 0, arch: b.arch ?? 0.1, thick: 0.17, mirror: sd > 0, color: COL.brow }), { blur: 0.04 * ew, alpha: 0.7 });
        }
      }
      g.restore();
    }
    g.restore();
  }

  // teeth: deterministic tables
  const TEETH = (() => {
    const r = S.rng('mimiku2-teeth');
    const mk = (n, crookedIdx, shortIdx, longIdx) => Array.from({ length: n }, (_, i) => ({
      u: (i + 0.5) / n + r.range(-0.12, 0.12) / n,
      len: (i % 2 ? 0.8 : 1) * r.range(0.82, 1.12) * (shortIdx.includes(i) ? 0.55 : 1) * (longIdx.includes(i) ? 1.3 : 1),
      w: r.range(0.85, 1.12) * (longIdx.includes(i) ? 1.15 : 1),
      tilt: (crookedIdx.includes(i) ? r.sign() * r.range(0.22, 0.36) : r.range(-0.06, 0.06)),
      bend: r.range(-0.18, 0.18), stain: r() < 0.3,
    }));
    return { up: mk(19, [3, 11, 16], [8], [1, 17]), lo: mk(17, [5, 12], [2, 14], [4, 9]) };
  })();
  function tooth(g, base, dir, L, w, bend, stain) {
    const d = dirA(dir), n = perp(d);
    const P = (a, b) => [base[0] + d[0] * a + n[0] * b, base[1] + d[1] * a + n[1] * b];
    const bw = w / 2, cv = bend * L;
    const shape = (k) => {
      const b0 = P(-0.15 * L, -bw * k), b1 = P(-0.15 * L, bw * k);
      g.beginPath(); g.moveTo(b0[0], b0[1]);
      const m0 = P(0.55 * L, -bw * 0.62 * k + cv), tip = P(L, cv * 1.6), m1 = P(0.55 * L, bw * 0.62 * k + cv);
      g.quadraticCurveTo(m0[0], m0[1], tip[0], tip[1]);
      g.quadraticCurveTo(m1[0], m1[1], b1[0], b1[1]);
      g.closePath();
    };
    shape(1); g.fillStyle = COL.toothShade; g.fill();
    g.save(); g.translate(-n[0] * bw * 0.28 * Math.sign(n[0] || 1), 0); shape(0.6); g.fillStyle = COL.tooth; g.fill(); g.restore();
    if (stain) { const s0 = P(0.0, 0), s1 = P(0.22 * L, 0); S.capsule(g, s0[0], s0[1], s1[0], s1[1], w * 0.7, w * 0.5, C.rgba(COL.toothStain, 0.6)); }
  }
  function paintTeeth(g, p, sol, which, poly) {
    const th = sol.th;
    if (th < 0.012) return;
    const { L: lL, R: lR, uL, uR } = sol.lip;
    const gap = sol.gap;
    const big = p.teeth ?? (p.ex.teeth || 1);
    if (which === 'up') {
      const dn = nrm(sub(lp(lL, lR, 0.5), lp(uL, uR, 0.5)));
      const maxL = Math.max(2, gap * 0.52);
      for (const t of TEETH.up) {
        const b = lp(uL, uR, t.u).slice(0, 2);
        const Lt = Math.min(0.13 * W * t.len * big, maxL * t.len);
        tooth(g, b, ang(dn) + t.tilt, Lt, 0.034 * W * t.w, t.bend, t.stain);
      }
    } else {
      const upd = nrm(sub(lp(uL, uR, 0.5), lp(lL, lR, 0.5)));
      const maxL = Math.max(2, gap * 0.5);
      // gum band inside the lower lip (flesh, fading up into the dark)
      if (poly) {
        g.save(); g.beginPath(); pathPts(g, poly); g.clip();
        const m = lp(lL, lR, 0.5), gw = 0.075 * W, gr = g.createLinearGradient(m[0], m[1], m[0] + upd[0] * gw, m[1] + upd[1] * gw);
        gr.addColorStop(0, COL.gum); gr.addColorStop(0.45, C.rgba(COL.gum, 0.8)); gr.addColorStop(1, C.rgba(COL.gum, 0));
        g.beginPath(); pathPts(g, [lL, lR, add(lR, mul(upd, gw)), add(lL, mul(upd, gw))].map(q => [q[0], q[1]])); g.fillStyle = gr; g.fill();
        g.restore();
      }
      const g0 = add(lL.slice(0, 2), mul(upd, 0.004 * W)), g1 = add(lR.slice(0, 2), mul(upd, 0.004 * W));
      S.strip(g, [g0, g1], 0.026 * W, COL.gum);
      for (const t of TEETH.lo) {
        const b = add(lp(lL, lR, 0.03 + t.u * 0.94).slice(0, 2), mul(upd, 0.006 * W));
        const uu = 0.03 + t.u * 0.94, eyeF = 1 - 0.62 * clamp((th - 0.2) / 0.3) * Math.max(bump(uu, 0.5 - DIM.eyeU, 0.17), bump(uu, 0.5 + DIM.eyeU, 0.17));
        const Lt = Math.min(0.12 * W * t.len * big, maxL * t.len) * eyeF;
        tooth(g, b, ang(upd) + t.tilt, Lt, 0.033 * W * t.w * lerp(1, 0.85, 1 - eyeF), t.bend, t.stain);
      }
    }
  }

  // the tongue: thick at the root, a slight waist, a spatulate widening ~70 % down, a ROUND tip; centre groove the
  // whole length, one hard shade on the lower-right edge (cel), a short soft comma-shaped wet highlight
  function paintTongue(g, p, sol) {
    const T = sol.tongue; if (!T) return;
    const P = catmull(T.pts, 3), w0 = T.w;
    const N = S._poly.normalsOf(P), U = S._poly.arcU(P), n = P.length;
    const half = u => (w0 / 2) * (1.02 - 0.17 * bump(u, 0.36, 0.34) + 0.13 * bump(u, 0.74, 0.28) - 0.08 * sstep(0.88, 1, u));
    const outline = c => {
      for (let i = 0; i < n; i++) { const h = half(U[i]); const X = P[i][0] + N[i][0] * h, Y = P[i][1] + N[i][1] * h; i ? c.lineTo(X, Y) : c.moveTo(X, Y); }
      const e = P[n - 1], hE = half(1), aN = ang(N[n - 1]), fwd = nrm(sub(P[n - 1], P[n - 2])), sg = sgnTurn(N[n - 1], fwd);
      for (let j = 1; j < 14; j++) { const a = aN + sg * Math.PI * j / 14; c.lineTo(e[0] + Math.cos(a) * hE, e[1] + Math.sin(a) * hE); }
      for (let i = n - 1; i >= 0; i--) { const h = half(U[i]); c.lineTo(P[i][0] - N[i][0] * h, P[i][1] - N[i][1] * h); }
      { // rounded back of the tongue at the root (it bulges out of the throat, never a flat cut)
        const h0 = half(0), b0 = nrm(sub(P[0], P[1])), a0 = ang(mul(N[0], -1)), sg0 = sgnTurn(mul(N[0], -1), b0);
        for (let j = 1; j < 12; j++) { const a = a0 + sg0 * Math.PI * j / 12; c.lineTo(P[0][0] + Math.cos(a) * h0, P[0][1] + Math.sin(a) * h0 * 0.38); }
      }
      c.closePath();
    };
    // it DRAPES: a soft contact shadow on the chest front, a dark side wall on the right (thickness), then the top
    if (sol.bodyHull && !T.behind) {
      g.save(); g.beginPath(); pathPts(g, sol.bodyHull); g.clip();
      g.translate(0.035 * W, 0.03 * W); g.beginPath(); outline(g); g.fillStyle = 'rgba(30,16,20,0.38)'; g.fill();
      g.restore();
    }
    g.save(); g.translate(0.022 * W, 0.014 * W); g.beginPath(); outline(g); g.fillStyle = C.shade(COL.tongueShade, -0.18); g.fill(); g.restore();
    S.cel(g, outline, COL.tongue, COL.tongueShade, 0.04 * W, 0.03 * W);
    g.save(); g.beginPath(); outline(g); g.clip();
    // darker root where it leaves the throat
    S.strip(g, S._poly.slicePts(P, 0, 0.14), u => w0 * 1.3 * (1 - u) ** 1.4, C.rgba(COL.groove, 0.55));
    // centre groove, root to near the tip
    S.strip(g, S._poly.slicePts(P, 0.03, 0.9), u => 0.024 * W * (0.5 + 0.5 * Math.sin(Math.PI * clamp(u * 1.1))) * (u > 0.85 ? (1 - u) / 0.15 : 1), COL.groove);
    // taste buds: sparse
    const r = S.rng('tongue-dots');
    for (let i = 0; i < 14; i++) {
      const u = r.range(0.12, 0.8), side = r.range(-0.78, 0.78);
      if (Math.abs(side) < 0.22) continue;
      const q = S._poly.pointAt(P, u), ni = N[Math.min(n - 1, Math.round(u * (n - 1)))];
      S.circle(g, q[0] + ni[0] * side * half(u), q[1] + ni[1] * side * half(u), 0.0065 * W, COL.tongueDot);
    }
    // wet highlight: a short soft comma on the upper-left half
    const mid = N[Math.floor(n * 0.3)], sL = (mid[0] * -0.6 + mid[1] * -0.8) >= 0 ? 1 : -1;
    const hp = u => { const q = S._poly.pointAt(P, u), ni = N[Math.min(n - 1, Math.round(u * (n - 1)))]; return [q[0] + ni[0] * sL * half(u) * 0.46, q[1] + ni[1] * sL * half(u) * 0.46]; };
    let Lt = 0; for (let i = 1; i < n; i++) Lt += len(sub(P[i], P[i - 1]));
    const du = clamp(0.055 * W / Math.max(1, Lt), 0.01, 0.1);
    const head = hp(0.22), tail = [head, hp(0.22 + du * 0.5), add(hp(0.22 + du), mul(N[Math.round((0.22 + du) * (n - 1))], -sL * 0.012 * W))];
    S.strip(g, tail, u => 0.03 * W * (1 - u) ** 1.1, COL.wet);
    S.circle(g, head[0], head[1], 0.016 * W, COL.wet);
    S.circle(g, ...hp(0.22 + du * 2.2), 0.005 * W, C.rgba('#FFF0F4', 0.55));
    if (FL > 0) {                                                          // flesh mode: a long wet specular streak + beads
      const seg = []; for (let j = 0; j <= 14; j++) seg.push(hp(0.34 + 0.44 * j / 14));
      S.strip(g, seg, u => 0.014 * W * Math.sin(Math.PI * u) ** 0.8 * FL, C.rgba('#FFF4F7', 0.7 * FL));
      const seg2 = []; for (let j = 0; j <= 8; j++) seg2.push(hp(0.82 + 0.1 * j / 8));
      S.strip(g, seg2, u => 0.01 * W * Math.sin(Math.PI * u) * FL, C.rgba('#FFF4F7', 0.55 * FL));
      S.circle(g, ...hp(0.8), 0.006 * W, C.rgba('#FFFFFF', 0.8 * FL));
    }
    if (!T.behind && T.foldU > 0.01) {                                     // the rounded roll where it leaves the lip
      const uf = T.foldU, i = Math.min(n - 1, Math.round(uf * (n - 1))), c0 = P[i], nf = N[i], fw = nrm(sub(P[Math.min(n - 1, i + 1)], P[Math.max(0, i - 1)]));
      const hh = half(uf), arc = (off, bow) => { const q = []; for (let j = 0; j <= 10; j++) { const k = -1 + j / 5; q.push(add(add(c0, mul(nf, k * hh * 1.1)), mul(fw, off + bow * (1 - k * k)))); } return q; };
      const back = len(sub(c0, P[0]));                                     // the back of the tongue, in the throat's shadow
      S.strip(g, arc(-back - 0.02 * W, -0.02 * W), u => 0.075 * W * Math.sin(Math.PI * u) ** 0.4, C.rgba(C.shade(COL.tongueShade, -0.3), 0.92));
      S.strip(g, arc(-0.03 * W, -0.012 * W), u => 0.04 * W * Math.sin(Math.PI * u) ** 0.6, C.rgba(COL.groove, 0.75));
      S.strip(g, arc(0.006 * W, 0.016 * W), u => 0.03 * W * Math.sin(Math.PI * u) ** 0.8, C.rgba('#F08A9C', 0.95));
      S.strip(g, arc(0.03 * W, 0.022 * W), u => 0.012 * W * Math.sin(Math.PI * u) ** 0.8, C.rgba(COL.groove, 0.5));
    }
    g.restore();
  }

  // ------------------------------------------------------------------ the grotesque limbs
  // FLESH (opts.flesh 0..1, default 0 = the v2.2 look): fleshier too-human limbs for wide / small shots, so the anatomy
  // never reads as bare bone: thicker calves, thighs and forearms over the same knobby joints, fuller fingers with
  // softer joints, and a sickly pinkish-grey SKIN palette (bone is ivory; skin is flesh) with mauve shade tones.
  let FL = 0;
  const FLESH = { skin: '#D7BBB0', skinShade: '#9F8282', skinMid: '#C4A79F', skinDeep: '#735A66', skinLite: '#E9D6CC', pink: '#D0918F', pinkShade: '#A26C72' };
  const skinC = key => FL > 0 && FLESH[key] ? C.mix(COL[key], FLESH[key], FL) : COL[key];
  function tonesOf(far) {
    const k = far ? -0.13 : 0;
    return {
      base: C.shade(skinC('skin'), k), shade: C.shade(skinC('skinShade'), k), core: C.shade(skinC('skinShade'), k + 0.02), mid: C.shade(skinC('skinMid'), k), deep: C.shade(skinC('skinDeep'), k),
      lite: C.shade(skinC('skinLite'), k), zone: C.shade(C.mix(skinC('skin'), skinC('pink'), 0.55), k - 0.05), zoneShade: C.shade(skinC('pinkShade'), k - 0.06),
    };
  }
  // outline of one straight bone with an UNEVEN silhouette: w1(u) is the half width on the side of perp(d), w2(u) on
  // the other side (u = 0 at A .. 1 at B); round caps at both ends
  function limbOutline(A, B, w1, w2, N = 24) {
    const d = nrm(sub(B, A)), L = len(sub(B, A)), n = perp(d);
    const s1 = [], s2 = [];
    for (let i = 0; i <= N; i++) { const u = i / N, c = add(A, mul(d, L * u)); s1.push(add(c, mul(n, w1(u)))); s2.push(add(c, mul(n, -w2(u)))); }
    const out = s1.slice();
    const cap = (c, r, from, sweep) => { for (let j = 1; j < 9; j++) out.push(add(c, mul(dirA(from + sweep * j / 9), r))); };
    const r1 = (w1(1) + w2(1)) / 2, c1 = add(B, mul(n, (w1(1) - w2(1)) / 2));
    cap(c1, r1, ang(n), Math.PI * sgnTurn(n, d));
    for (let i = N; i >= 0; i--) out.push(s2[i]);
    const r0 = (w1(0) + w2(0)) / 2, c0 = add(A, mul(n, (w1(0) - w2(0)) / 2)), nn = mul(n, -1);
    cap(c0, r0, ang(nn), Math.PI * sgnTurn(nn, mul(d, -1)));
    return { pts: out, A, B, d, n, L, w1, w2 };
  }
  // side point: fraction u along the bone, k of the half width toward side i (1 = +n, 2 = -n)
  const sidePt = (seg, i, u, k) => add(add(seg.A, mul(seg.d, seg.L * u)), mul(seg.n, (i === 1 ? 1 : -1) * k * (i === 1 ? seg.w1(u) : seg.w2(u))));
  // half-width profiles (px at s = 1). fr = anterior score of that side (-1 posterior .. 1 anterior), md = medial score
  function profThigh(u, fr, md) {
    // heavy at the hip, tapering hard to a pinched knee (the kneecap is a separate knob on top)
    let h = 0.092 - 0.066 * Math.pow(u, 0.7);
    h += pos(md) * (-0.02 * bump(u, 0.58, 0.34) + 0.006 * bump(u, 0.04, 0.12));      // hollow inner thigh
    h += pos(-md) * 0.022 * bump(u, 0.3, 0.42);                                         // outer sweep
    h += pos(fr) * 0.018 * bump(u, 0.42, 0.42);                                         // quads
    h += pos(-fr) * (0.016 * bump(u, 0.32, 0.42) - 0.008 * bump(u, 0.94, 0.1));        // hamstrings, hollow behind the knee
    h -= 0.004 * bump(u, 0.9, 0.1);                                                     // pinch just above the knee
    h += 0.01 * bump(u, 1, 0.14);                                                       // condyles
    h *= 1 + FL * 0.42 * (1 - bump(u, 1, 0.16));
    return h * W;
  }
  function profShin(u, fr, md) {
    let h = lerp(0.026, 0.011, sstep(0.0, 1, u));                                       // knee-pinched, narrows to a thin ankle
    h += pos(-fr) * 0.062 * bump(u, 0.3, 0.32);                                         // big calf bulge
    h += pos(fr) * 0.006 * bump(u, 0.25, 0.3);                                          // tibia ridge
    h += pos(md) * 0.042 * bump(u, 0.3, 0.3) + pos(-md) * 0.028 * bump(u, 0.24, 0.28);  // calf heads (front view)
    h += 0.012 * bump(u, 0, 0.16);                                                      // tibial plateau
    h += 0.006 * bump(u, 1, 0.08);                                                      // ankle flare
    h += pos(-fr) * 0.011 * bump(u, 0.9, 0.16);                                         // Achilles stands off the back
    h += FL * (0.02 * bump(u, 0.32, 0.42) + pos(-fr) * 0.026 * bump(u, 0.3, 0.3) + 0.01 * bump(u, 0.58, 0.32));   // flesh: full calf
    return h * W;
  }
  function profUpper(u, out) {
    // stringy: a lump of shoulder at the root, a thin bone-and-cord middle, knobby at the elbow
    let h = 0.036 - 0.016 * sstep(0, 0.6, u);
    h += 0.01 * bump(u, 0.08, 0.2);
    h += pos(out) * 0.01 * bump(u, 0.36, 0.3) + pos(-out) * (0.012 * bump(u, 0.45, 0.32) - 0.005 * bump(u, 0.94, 0.1));
    h += 0.012 * bump(u, 1, 0.14);                                                      // epicondyles
    h += FL * (0.024 * bump(u, 0.42, 0.5) + pos(-out) * 0.01 * bump(u, 0.45, 0.3) + 0.006 * bump(u, 0.1, 0.2));    // flesh: biceps / triceps
    return h * W;
  }
  function profFore(u, out) {
    let h = lerp(0.026, 0.012, sstep(0, 1, u));
    h += pos(out) * 0.028 * bump(u, 0.22, 0.3) + pos(-out) * 0.022 * bump(u, 0.24, 0.3) + 0.009 * bump(u, 0.12, 0.2); // swell below the elbow
    h += 0.007 * bump(u, 1, 0.08);                                                      // wrist knobs
    h += FL * (0.024 * bump(u, 0.26, 0.4) + 0.008 * bump(u, 0.66, 0.34));               // flesh: forearm belly
    return h * W;
  }
  // THE CORE SHADOW: a hard, wide band of skin-shade along the side of a segment that faces away from the top-left
  // light (the back edge), plus a deep edge inside it and a lit streak on the other side: 3 skin tones that read at
  // body scale (s = 0.45), so the limbs never flatten into pale pipes
  const KEY = nrm([-0.55, -0.83]);
  function coreShade(g, seg, T, o = {}) {
    const sd = dot(seg.n, KEY) > 0 ? 2 : 1;                // the side facing away from the light
    const N = 24, inn = [], out = [], deep = [], lit = [], litIn = [];
    const k0 = o.k0 ?? -0.12, kd = o.kd ?? 0.5;
    for (let j = 0; j <= N; j++) {
      const u = j / N;
      inn.push(sidePt(seg, sd, u, k0)); out.push(sidePt(seg, sd, u, 1.4)); deep.push(sidePt(seg, sd, u, kd));
      lit.push(sidePt(seg, 3 - sd, u, 0.42)); litIn.push(sidePt(seg, 3 - sd, u, 0.74));
    }
    g.beginPath(); pathPts(g, inn.concat(out.slice().reverse())); g.fillStyle = T.core; g.fill();
    g.beginPath(); pathPts(g, deep.concat(out.slice().reverse())); g.fillStyle = C.rgba(T.deep, o.deepA ?? 0.9); g.fill();
    if (o.lit !== false) { g.beginPath(); pathPts(g, lit.concat(litIn.slice().reverse())); g.fillStyle = C.rgba(T.lite, 0.8); g.fill(); }
  }
  // mid tone on every muscle bulge (the extra half width a side gets from its directional term), a shade sliver along
  // every hollow: the 2nd and 3rd skin tones that make the masses read as too-real anatomy
  function massTones(g, seg, baseFn, T) {
    for (const i of [1, 2]) {
      const fn = i === 1 ? seg.w1 : seg.w2, sg = i === 1 ? 1 : -1, N = 24, inner = [], outer = [], hin = [];
      let any = false, anyH = false;
      for (let j = 0; j <= N; j++) {
        const u = j / N, c = add(seg.A, mul(seg.d, seg.L * u)), w = fn(u), b = w - baseFn(u);
        if (b > 0.004 * W) any = true;
        if (b < -0.004 * W) anyH = true;
        inner.push(add(c, mul(seg.n, sg * (w - 0.8 * pos(b)))));
        hin.push(add(c, mul(seg.n, sg * (w - 0.9 * pos(-b)))));
        outer.push(add(c, mul(seg.n, sg * (w + 2))));
      }
      if (any) { g.beginPath(); pathPts(g, inner.concat(outer.slice().reverse())); g.fillStyle = C.rgba(T.mid, 0.9); g.fill(); }
      if (anyH) { g.beginPath(); pathPts(g, hin.concat(outer.slice().reverse())); g.fillStyle = C.rgba(T.shade, 0.55); g.fill(); }
    }
  }
  // a cord under the skin: deep edge toward the shade (bottom-right), light edge toward the light, body in between
  function raised(g, pts, w, T, a = 1) {
    if (a <= 0.02) return;
    const P = catmull(pts, 4), N = S._poly.normalsOf(P), m = N[Math.floor(N.length / 2)];
    const sh = (m[0] * 0.6 + m[1] * 0.8) >= 0 ? 1 : -1;
    const tap = u => Math.sin(Math.PI * clamp(u)) ** 0.55;
    S.strip(g, S._poly.offsetPts(P, sh * w * 0.48), u => w * 0.6 * tap(u), C.rgba(T.deep, 0.62 * a));
    S.strip(g, P, u => w * tap(u), C.rgba(T.base, 0.95 * a));
    S.strip(g, S._poly.offsetPts(P, -sh * w * 0.3), u => w * 0.36 * tap(u), C.rgba(T.lite, 0.75 * a));
  }
  // a thick, slightly raised grey-violet vein (+ optional fork)
  function vein(g, pts, w, T, fork) {
    const one = (Q, ww) => {
      const P = catmull(Q, 5), N = S._poly.normalsOf(P), m = N[Math.floor(N.length / 2)];
      const sh = (m[0] * 0.6 + m[1] * 0.8) >= 0 ? 1 : -1, tap = u => 0.3 + 0.7 * Math.sin(Math.PI * clamp(u)) ** 0.5;
      S.strip(g, S._poly.offsetPts(P, sh * ww * 0.45), u => ww * 0.7 * tap(u), C.rgba(COL.veinDeep, 0.55));
      S.strip(g, P, u => ww * tap(u), C.rgba(COL.vein, 0.85));
      S.strip(g, S._poly.offsetPts(P, -sh * ww * 0.3), u => ww * 0.34 * tap(u), C.rgba(T.lite, 0.6));
    };
    one(pts, w);
    if (fork) one(fork, w * 0.68);
  }
  function crease(g, pts, w, col, a) { S.strip(g, catmull(pts, 4), u => w * Math.sin(Math.PI * clamp(u)) ** 0.7, C.rgba(col, a)); }
  // a second, narrower shade step inside the hard shade (bottom-right): the extra tone that rounds the bone
  function deepRim(g, pts, d, col, a) {
    g.save(); g.beginPath(); pathPts(g, pts); g.clip();
    g.beginPath(); g.rect(-1e5, -1e5, 2e5, 2e5); pathPts(g, pts.map(q => [q[0] - d, q[1] - d])); g.fillStyle = C.rgba(col, a); g.fill('evenodd');
    g.restore();
  }
  // soft pink-dark flush (knees, elbows): skin colour change, not a lighting gradient
  function flush(g, c, r, col, a) {
    const gr = g.createRadialGradient(c[0], c[1], 0, c[0], c[1], r);
    gr.addColorStop(0, C.rgba(col, a)); gr.addColorStop(0.55, C.rgba(col, a * 0.7)); gr.addColorStop(1, C.rgba(col, 0));
    g.fillStyle = gr; g.beginPath(); g.arc(c[0], c[1], r, 0, TAU); g.fill();
  }
  // short crease arcs stacked across a limb axis (knee / elbow skin folds)
  function foldArcs(g, c, axis, n, gap, L, bow, w, col, a) {
    const ac = perp(axis);
    for (let i = 0; i < n; i++) {
      const m = add(c, mul(axis, i * gap)), l = L * (1 - i * 0.18);
      crease(g, [add(m, mul(ac, -l)), add(m, mul(axis, bow)), add(m, mul(ac, l))], w, col, a * (1 - i * 0.22));
    }
  }

  function paintLeg(g, Lg, far, F) {
    const { hip, knee, ankle, sd } = Lg, s = Lg.g, T = tonesOf(far), kk = W * s;
    const kv = nrm(sub(knee, hip)), av = nrm(sub(ankle, knee));
    const front = F.vec(0, 0, 1), medial = F.vec(-sd, 0, 0);
    const bend = Math.abs(kv[0] * av[1] - kv[1] * av[0]);
    const scT = n => ({ fr: clamp(-4 * dot(n, av) + dot(n, front), -1, 1), md: dot(n, medial) });
    const scS = n => ({ fr: clamp(4 * dot(n, kv) + dot(n, front), -1, 1), md: dot(n, medial) });
    const nT = perp(kv), nS = perp(av), t1 = scT(nT), t2 = scT(mul(nT, -1)), s1 = scS(nS), s2 = scS(mul(nS, -1));
    const thigh = limbOutline(hip, knee, u => s * profThigh(u, t1.fr, t1.md), u => s * profThigh(u, t2.fr, t2.md));
    const shin = limbOutline(knee, ankle, u => s * profShin(u, s1.fr, s1.md), u => s * profShin(u, s2.fr, s2.md));
    // ---- shin (the thigh overlaps it at the knee)
    S.cel(g, c => pathPts(c, shin.pts), T.base, T.shade, 0.02 * W, 0.02 * W);
    deepRim(g, shin.pts, 0.009 * W, T.deep, 0.55);
    clipPts(g, shin.pts, () => {
      massTones(g, shin, u => s * profShin(u, 0, 0), T);
      coreShade(g, shin, T);
      const post = s1.fr < s2.fr ? 1 : 2, postSc = Math.min(s1.fr, s2.fr), ant = 3 - post;
      crease(g, [sidePt(shin, ant, 0.12, 0.62), sidePt(shin, ant, 0.45, 0.6), sidePt(shin, ant, 0.82, 0.48)], 0.008 * W, T.deep, 0.4);   // tibia edge
      if (postSc < -0.2) {                                                      // Achilles cord + the hollow in front of it
        const a = clamp(-postSc * 1.6);
        raised(g, [sidePt(shin, post, 0.62, 0.45), sidePt(shin, post, 0.8, 0.55), sidePt(shin, post, 1.0, 0.45)], 0.02 * kk, T, a);
        crease(g, [sidePt(shin, post, 0.66, -0.05), sidePt(shin, post, 0.82, 0.05), sidePt(shin, post, 0.97, 0.05)], 0.011 * W, T.deep, 0.6 * a);
      }
      const ms = s1.md > s2.md ? 1 : 2;                                          // one wandering vein, medial-front of the shin
      vein(g, [sidePt(shin, ms, 0.3, -0.1), sidePt(shin, ms, 0.38, 0.3), sidePt(shin, ms, 0.47, 0.0), sidePt(shin, ms, 0.56, 0.38), sidePt(shin, ms, 0.66, 0.1)], 0.02 * kk, T,
        [sidePt(shin, ms, 0.45, 0.08), sidePt(shin, ms, 0.52, -0.4), sidePt(shin, ms, 0.6, -0.5)]);
    });
    // ---- thigh
    S.cel(g, c => pathPts(c, thigh.pts), T.base, T.shade, 0.024 * W, 0.024 * W);
    deepRim(g, thigh.pts, 0.01 * W, T.deep, 0.5);
    clipPts(g, thigh.pts, () => {
      massTones(g, thigh, u => s * profThigh(u, 0, 0), T);
      coreShade(g, thigh, T);
      const post = t1.fr < t2.fr ? 1 : 2, postSc = Math.min(t1.fr, t2.fr);
      if (postSc < -0.22) {                                                     // hamstring cords running into the knee pit
        const a = clamp(-postSc * 1.5);
        raised(g, [sidePt(thigh, post, 0.52, 0.42), sidePt(thigh, post, 0.78, 0.6), sidePt(thigh, post, 1.0, 0.5)], 0.024 * kk, T, a);
        raised(g, [sidePt(thigh, post, 0.6, -0.05), sidePt(thigh, post, 0.82, 0.18), sidePt(thigh, post, 1.0, 0.22)], 0.018 * kk, T, a * 0.85);
      }
      const ms = t1.md > t2.md ? 1 : 2;                                          // the hollow of the inner thigh
      if (Math.max(t1.md, t2.md) > 0.4) crease(g, [sidePt(thigh, ms, 0.34, 0.5), sidePt(thigh, ms, 0.56, 0.36), sidePt(thigh, ms, 0.8, 0.46)], 0.01 * W, T.deep, 0.4);
      const fs = t1.fr > t2.fr ? 1 : 2;                                          // the long sartorius groove across the front
      crease(g, [sidePt(thigh, fs, 0.12, 0.2), sidePt(thigh, fs, 0.45, -0.1), sidePt(thigh, fs, 0.8, -0.45)], 0.008 * W, T.deep, 0.28);
    });
    // ---- knee: pinker darker zone, a bony patella (flat shield, not a ball), skin folds, the knee pit
    const legAx = nrm(sub(ankle, hip)), bendV = nrm(sub(knee, lp(hip, ankle, 0.5)));
    const antOff = add(mul(bendV, 0.03 * kk * clamp(bend * 3)), mul(front, 0.032 * kk));
    const pc = add(knee, add(antOff, mul(legAx, -0.012 * kk)));
    clipUnion(g, [thigh.pts, shin.pts], () => flush(g, pc, 0.1 * kk, T.zone, 0.85));
    g.save(); g.translate(pc[0], pc[1]); g.rotate(ang(legAx) - Math.PI / 2);
    const pw = 0.046 * kk, ph = 0.052 * kk;
    S.cel(g, c => { c.moveTo(0, -ph); c.bezierCurveTo(pw * 1.25, -ph * 0.95, pw * 1.05, ph * 0.55, 0, ph); c.bezierCurveTo(-pw * 1.05, ph * 0.55, -pw * 1.25, -ph * 0.95, 0, -ph); c.closePath(); },
      T.zone, T.zoneShade, 0.016 * kk, 0.014 * kk);
    S.ellipse(g, -pw * 0.3, -ph * 0.35, pw * 0.28, ph * 0.2, -0.4, C.rgba(T.lite, 0.55));
    g.restore();
    foldArcs(g, add(pc, mul(legAx, -0.05 * kk)), mul(legAx, -1), 3, 0.016 * kk, 0.032 * kk, 0.009 * kk, 0.009 * W, T.deep, 0.72);
    foldArcs(g, add(pc, mul(legAx, 0.05 * kk)), legAx, 2, 0.015 * kk, 0.026 * kk, 0.007 * kk, 0.008 * W, T.deep, 0.6);
    if (bend > 0.12 || Math.abs(front[0]) > 0.35) {                              // knee pit crease (side-ish views)
      const bk = add(knee, add(mul(bendV, -0.034 * kk * clamp(bend * 3)), mul(front, -0.032 * kk)));
      crease(g, [add(bk, mul(kv, -0.03 * kk)), bk, add(bk, mul(av, 0.03 * kk))], 0.009 * W, T.deep, 0.65);
    }
  }

  function paintFoot(g, Lg, F, far) {
    const { ankle, sd } = Lg, s = Lg.g * DIM.footK, T = tonesOf(far);
    const splay = sd * (Lg.splay ?? 0.62), tp = Lg.toe || 0;
    const cs = Math.cos(splay), sn = Math.sin(splay), ct = Math.cos(tp), st = Math.sin(tp);
    const FP0 = (a, c, h) => {                                              // foot-local (fwd, lateral, down) in W
      const a1 = a * ct - h * st, h1 = a * st + h * ct;
      const x = c * cs + a1 * sn, z = -c * sn + a1 * cs;
      const v = F.view([x * W * s, h1 * W * s, z * W * s]);
      return [ankle[0] + v[0], ankle[1] + v[1]];
    };
    const inner = -sd;
    const hullSrc = [[-0.035, 0, -0.03], [0.035, 0, -0.03], [-0.068, 0, 0.04], [-0.05, 0, 0.074], [0.06, inner * 0.034, 0.074], [0.06, -inner * 0.038, 0.074],
      [0.175, inner * 0.06, 0.066], [0.165, -inner * 0.055, 0.068], [0.0, 0.034, 0.02], [0.0, -0.034, 0.02], [0.11, 0, 0.03]];
    const toes = [[0.058, 0.32, 0.036], [0.032, 0.315, 0.027], [0.007, 0.295, 0.025], [-0.018, 0.272, 0.023], [-0.043, 0.245, 0.021]];
    // floor clamp: in this orthographic camera a planted foot that points at the camera projects BELOW the ground line;
    // squash it about the ankle so the sole and toe tips sit on the line (a short front-on wedge)
    let ky = 1;
    if (ankle[1] > -DIM.ankle - 0.05 * W) {
      const raw = hullSrc.map(q => FP0(...q)).concat(toes.map(([c0, tipA]) => FP0(tipA, inner * c0 * 1.15, 0.074)));
      const maxY = Math.max(...raw.map(q => q[1]));
      if (maxY > 0.5) ky = clamp((0.5 - ankle[1]) / (maxY - ankle[1]), 0.2, 1);
    }
    const FP = (a, c, h) => { const q = FP0(a, c, h); return [q[0], ankle[1] + (q[1] - ankle[1]) * ky]; };
    const outline = convexHull(hullSrc.map(q => FP(...q)));
    S.cel(g, c => addSafeRound(c, outline, 0.03 * W * s), T.base, T.shade, 0.018 * W, 0.018 * W);
    const fwdLen = len(sub(FP(0.17, 0, 0.06), FP(0, 0, 0.06)));
    if (fwdLen > 0.05 * W) {                                                  // extensor tendons pushing up the top of the foot
      for (let i = 0; i < 3; i++) {
        const c0 = inner * (0.034 - i * 0.032);
        raised(g, [FP(0.03, c0 * 0.3, -0.004), FP(0.09, c0 * 0.75, 0.03), FP(0.15, c0, 0.052)], 0.012 * W * s, T, 0.6);
      }
    }
    for (const [c0, tipA, tw] of toes) {
      const cc = inner * c0, b = FP(0.16, cc, 0.06);
      let m = FP(0.215, cc * 1.08, 0.052), t = FP(tipA, cc * 1.15, 0.074);
      const tv = sub(t, b), minL = 0.03 * W * s;
      if (len(tv) < minL) {                                                   // toe pointing at the camera: a knobby bump
        const q = add(b, [0, Math.min(0.012 * W * s, 0.5 - b[1])]);
        S.cel(g, c => { c.moveTo(q[0] + tw * 0.62 * W * s, q[1]); c.arc(q[0], q[1], tw * 0.62 * W * s, 0, TAU); }, T.base, T.shade, 0.006 * W * s, 0.006 * W * s);
        S.circle(g, q[0], q[1] - tw * 0.18 * W * s, tw * 0.3 * W * s, C.mix(T.base, COL.pink, 0.55));
        S.ellipse(g, q[0], q[1] + tw * 0.22 * W * s, tw * 0.36 * W * s, tw * 0.2 * W * s, 0, COL.nail);
        continue;
      }
      S.limb(g, [b, m, t], [tw * W * s, tw * 0.84 * W * s, tw * 0.8 * W * s], T.shade);
      S.limb(g, [b, m, t].map(q => add(q, [-0.0035 * W, -0.0035 * W])), [tw * 0.85 * W * s, tw * 0.7 * W * s, tw * 0.66 * W * s], T.base);
      S.circle(g, m[0], m[1], tw * 0.52 * W * s, T.zone);
      const nd = nrm(sub(t, m)), nb = add(t, mul(nd, -0.006 * W * s)), ne = add(t, mul(nd, 0.016 * W * s));
      S.capsule(g, nb[0], nb[1], ne[0], ne[1], tw * 0.62 * W * s, tw * 0.28 * W * s, COL.nail);
    }
    // ankle bones (malleoli): knobs either side, pinkish, no shine
    const kn = perp(nrm(sub(Lg.knee, ankle)));
    for (const sg of [-1, 1]) {
      const q = add(ankle, mul(kn, sg * 0.024 * W * Lg.g)), r = (sg === inner ? 0.03 : 0.025) * W * Lg.g;
      S.cel(g, c => { c.moveTo(q[0] + r, q[1]); c.arc(q[0], q[1], r, 0, TAU); }, T.zone, T.zoneShade, 0.01 * W, 0.01 * W);
    }
  }

  function paintArm(g, Ar, far, opt = {}) {
    const s = Ar.g, T = tonesOf(far), kk = W * s, A = Ar.A || {};
    if (Ar.mode === 'arm') {
      const { sh, elbow, wrist } = Ar;
      const uv = nrm(sub(elbow, sh)), fv = nrm(sub(wrist, elbow));
      const bend = Math.abs(uv[0] * fv[1] - uv[1] * fv[0]), bk = clamp(bend * 4);
      const outV = nrm(sub(elbow, lp(sh, wrist, 0.5)));
      const sc = n => clamp(3 * dot(n, outV), -1, 1) * bk;
      const hs = A.handScale || 1;
      const nU = perp(uv), nF = perp(fv), oU1 = sc(nU), oU2 = sc(mul(nU, -1)), oF1 = sc(nF), oF2 = sc(mul(nF, -1));
      const foK = u => lerp(1, hs, u * u);
      const upper = limbOutline(sh, elbow, u => s * profUpper(u, oU1), u => s * profUpper(u, oU2));
      const fore = limbOutline(elbow, wrist, u => s * profFore(u, oF1) * foK(u), u => s * profFore(u, oF2) * foK(u));
      // forearm
      S.cel(g, c => pathPts(c, fore.pts), T.base, T.shade, 0.02 * W, 0.02 * W);
      deepRim(g, fore.pts, 0.008 * W, T.deep, 0.5);
      clipPts(g, fore.pts, () => {
        massTones(g, fore, u => s * profFore(u, 0, 0) * foK(u), T);
        coreShade(g, fore, T);
        const ins = oF1 < oF2 ? 1 : 2, ot = 3 - ins;                            // inner (flexor) / outer (extensor) side
        raised(g, [sidePt(fore, ins, 0.56, 0.1), sidePt(fore, ins, 0.8, 0.22), sidePt(fore, ins, 0.99, 0.12)], 0.016 * kk * lerp(1, hs, 0.7), T, 0.85);   // wrist tendons
        raised(g, [sidePt(fore, ins, 0.62, -0.32), sidePt(fore, ins, 0.84, -0.22), sidePt(fore, ins, 0.99, -0.3)], 0.012 * kk * lerp(1, hs, 0.7), T, 0.7);
        vein(g, [sidePt(fore, ot, 0.34, 0.25), sidePt(fore, ot, 0.44, -0.2), sidePt(fore, ot, 0.55, 0.15), sidePt(fore, ot, 0.66, -0.25), sidePt(fore, ot, 0.8, 0.0)], 0.02 * kk * lerp(1, hs, 0.6), T,
          [sidePt(fore, ot, 0.5, 0.0), sidePt(fore, ot, 0.6, 0.5), sidePt(fore, ot, 0.72, 0.62)]);
        crease(g, [sidePt(fore, ot, 0.08, 0.55), sidePt(fore, ot, 0.3, 0.62), sidePt(fore, ot, 0.48, 0.45)], 0.008 * W, T.deep, 0.38);
      });
      // upper arm
      S.cel(g, c => pathPts(c, upper.pts), T.base, T.shade, 0.02 * W, 0.02 * W);
      deepRim(g, upper.pts, 0.008 * W, T.deep, 0.5);
      clipPts(g, upper.pts, () => {
        massTones(g, upper, u => s * profUpper(u, 0), T);
        coreShade(g, upper, T);
        raised(g, [sidePt(upper, 1, 0.12, 0.1), sidePt(upper, 1, 0.5, -0.15), sidePt(upper, 1, 0.9, 0.05)], 0.014 * kk, T, 0.8);   // a stringy cord
        // the root comes out of the dark mouth: socket shadow fading along the first ~0.12 W
        if (opt.socket) {
          g.beginPath(); pathPts(g, opt.socket); g.clip();
          const gr = g.createRadialGradient(sh[0], sh[1], 0, sh[0], sh[1], 0.075 * kk);
          gr.addColorStop(0, C.rgba(COL.mouth, 0.95)); gr.addColorStop(0.45, C.rgba(COL.mouth, 0.6)); gr.addColorStop(1, C.rgba(COL.mouth, 0));
          g.fillStyle = gr; g.fillRect(sh[0] - 0.2 * kk, sh[1] - 0.2 * kk, 0.4 * kk, 0.4 * kk);
        }
      });
      // elbow: pinker darker zone, a POINTED olecranon on the outside of the bend, folds, the crook
      clipUnion(g, [upper.pts, fore.pts], () => flush(g, add(elbow, mul(outV, 0.014 * kk)), 0.08 * kk, T.zone, 0.85));
      const ep = add(elbow, mul(outV, 0.024 * kk * bk));
      g.save(); g.translate(ep[0], ep[1]); g.rotate(bk > 0.1 ? ang(outV) : ang(uv) + Math.PI / 2);
      const ok = lerp(0.6, 1, bk);
      S.cel(g, c => { c.moveTo(0.05 * kk * ok, 0); c.quadraticCurveTo(0.006 * kk, 0.036 * kk, -0.03 * kk, 0.032 * kk); c.lineTo(-0.03 * kk, -0.032 * kk); c.quadraticCurveTo(0.006 * kk, -0.036 * kk, 0.05 * kk * ok, 0); c.closePath(); },
        T.zone, T.zoneShade, 0.012 * kk, 0.012 * kk);
      g.restore();
      const ov = bk > 0.1 ? outV : perp(uv);
      foldArcs(g, add(elbow, mul(ov, -0.004 * kk)), mul(ov, -1), 3, 0.014 * kk, 0.024 * kk, -0.008 * kk, 0.0085 * W, T.deep, 0.72);
      if (bk > 0.2) {
        const crook = add(elbow, mul(ov, -0.03 * kk));
        crease(g, [add(crook, mul(uv, -0.024 * kk)), add(crook, mul(ov, -0.006 * kk)), add(crook, mul(fv, 0.026 * kk))], 0.008 * W, T.deep, 0.6);
      }
      // wrist knob (ulna head)
      const wk = add(wrist, mul(perp(fv), (dot(perp(fv), outV) > 0 ? 1 : -1) * 0.02 * kk * hs));
      S.cel(g, c => { c.moveTo(wk[0] + 0.016 * kk * hs, wk[1]); c.arc(wk[0], wk[1], 0.016 * kk * hs, 0, TAU); }, T.zone, T.zoneShade, 0.005 * kk, 0.005 * kk);
    }
    paintHand(g, Ar, T);
  }

  function nail(g, tip, dd, w, L) {
    const nb = add(tip, mul(dd, -L * 0.35)), ne = add(tip, mul(dd, L * 0.65));
    S.capsule(g, nb[0], nb[1], ne[0], ne[1], w, w * 0.18, COL.nail);
    const n = perp(dd), hb = add(nb, mul(n, -w * 0.2)), he = add(lp(nb, ne, 0.45), mul(n, -w * 0.2));
    S.capsule(g, hb[0], hb[1], he[0], he[1], w * 0.24, w * 0.12, COL.nailHi);
  }
  // knobby digit: joints wider than the phalanx middles, one hard shade rim
  function knobby(g, pts, wf, T, k) {
    if (FL > 0) { const mx = Math.max(...wf.slice(1)); wf = wf.map((w, i) => (i ? lerp(w, (w + mx * 0.8) / 2, FL * 0.6) : w) * (1 + 0.3 * FL)); }
    S.limb(g, pts, wf, T.shade);
    S.limb(g, pts.map(q => add(q, [-0.0042 * k, -0.0042 * k])), wf.map(w => w * 0.8), T.base);
  }
  function paintHand(g, Ar, T) {
    const A = Ar.A || {}, sd = Ar.sd, hsc = A.handScale || 1, s = Ar.g * hsc * DIM.handK, k = W * s;
    const wr = Ar.wrist, ha = Ar.handAng, d = dirA(ha), n = perp(d);
    const curl = clamp(A.curl ?? 0.3), spread = clamp(A.spread ?? 0.35), cdir = A.curlDir ?? -sd, fc = A.fingers || [];
    const tside = dot(n, [-sd, 0]) >= 0 ? 1 : -1;                         // thumb toward the body centre
    const H = (a, c) => add(wr, add(mul(d, a * k), mul(n, c * k)));
    // thumb (its root tucks under the back of the hand)
    {
      const tc = clamp(A.thumb ?? curl);
      const b = H(0.035, 0.044 * tside), a0 = ha + tside * (0.72 - 0.28 * tc);
      const p1 = add(b, mul(dirA(a0), 0.095 * k)), p2 = add(p1, mul(dirA(a0 - tside * (0.3 + 0.55 * tc)), 0.078 * k));
      const pts = [b, lp(b, p1, 0.5), p1, lp(p1, p2, 0.55), p2];
      knobby(g, pts, [0.05, 0.028, 0.031, 0.021, 0.019].map(v => v * k), T, k);
      S.circle(g, p1[0], p1[1], 0.013 * k, C.rgba(T.zone, 0.9));
      nail(g, p2, nrm(sub(p2, p1)), 0.019 * k * (1 + 0.4 * FL), 0.034 * k * (1 + 0.3 * FL));
    }
    // back of the hand
    const pk = 1 + 0.22 * FL;
    const palm = [H(-0.02, -0.034 * pk), H(0.05, -0.058 * pk), H(0.125, -0.068 * pk), H(0.152, -0.04 * pk), H(0.16, 0.0), H(0.152, 0.04 * pk), H(0.125, 0.068 * pk), H(0.05, 0.058 * pk), H(-0.02, 0.034 * pk)];
    S.cel(g, c => S.addBlob(c, palm, 0.55), T.base, T.shade, 0.014 * k, 0.014 * k);
    // long knobby fingers, index (thumb side) .. pinky
    const FD = [[0.047, 0.205], [0.016, 0.228], [-0.016, 0.214], [-0.046, 0.168]];
    const bases = [];
    FD.forEach(([c0, Lf], i) => {
      const b = H(0.138 - Math.abs(c0) * 0.35, c0 * tside);
      let a = ha + (i - 1.5) * -tside * (0.05 + 0.2 * spread);
      const cu = clamp(fc[i] ?? curl);
      const segs = [0.45, 0.31, 0.24], bends = [0.3, 0.55, 0.45], J = [b];
      for (let j = 0; j < 3; j++) { a += cdir * cu * bends[j] * 1.25; J.push(add(J[j], mul(dirA(a), segs[j] * Lf * k))); }
      const pts = [J[0], lp(J[0], J[1], 0.5), J[1], lp(J[1], J[2], 0.5), J[2], lp(J[2], J[3], 0.55), J[3]];
      const wf = [0.034, 0.021, 0.028, 0.018, 0.023, 0.0165, 0.0145].map(v => v * k);
      knobby(g, pts, wf, T, k);
      for (const j of [1, 2]) {                                             // pinkish knobbly joints + creases
        const q = J[j], dd = nrm(sub(J[j + 1], J[j - 1])), nn = perp(dd), r = wf[j * 2] * 0.42;
        S.circle(g, q[0] - 0.003 * k, q[1] - 0.003 * k, r * (1 + 0.25 * FL), C.rgba(T.zone, 0.9 - 0.35 * FL));
        for (const off of [-0.006, 0.006]) { const m = add(q, mul(dd, off * k)); crease(g, [add(m, mul(nn, -r * 0.8)), add(m, mul(dd, 0.002 * k)), add(m, mul(nn, r * 0.8))], 0.0042 * k, T.deep, 0.5); }
      }
      nail(g, J[3], nrm(sub(J[3], J[2])), 0.02 * k * (1 + 0.4 * FL), 0.036 * k * (1 + 0.3 * FL));
      bases.push(J[0]);
    });
    // extensor tendons pushing up the skin (subtle raised cords fanning from the wrist to each knuckle) + one vein
    bases.forEach((b, i) => { const w0 = H(0.0, FD[i][0] * 0.4 * tside); raised(g, [lp(w0, b, 0.12), lp(w0, b, 0.5), lp(w0, b, 0.84)], 0.012 * k, T, 0.8); });
    vein(g, [H(-0.01, -0.022 * tside), H(0.04, -0.012 * tside), H(0.085, 0.006 * tside), H(0.118, 0.024 * tside)], 0.014 * k, T, [H(0.05, -0.01 * tside), H(0.1, -0.034 * tside)]);
    // big knuckles: the metacarpal heads push up the skin (pinker, darker, one hard shade each)
    const kz = C.mix(T.base, T.zone, 0.75), kr = [0.019, 0.021, 0.018, 0.0145];
    bases.forEach((b, i) => { const r = kr[i] * k, q = add(b, mul(d, -0.006 * k)); S.cel(g, c => { c.moveTo(q[0] + r, q[1]); c.ellipse(q[0], q[1], r, r * 0.86, ha, 0, TAU); }, kz, T.zoneShade, 0.0065 * k, 0.0065 * k); });
  }

  // ------------------------------------------------------------------ chain
  // resample a screen polyline at equal arc length (link pitch); returns the points and, for each, the source flag
  function resample(poly, flags, step) {
    const out = [poly[0].slice()], fl = [flags[0]];
    let i = 0, q = poly[0].slice(), rest = step;
    while (i < poly.length - 1) {
      const b = poly[i + 1], d = len(sub(b, q));
      if (d >= rest) { q = add(q, mul(sub(b, q), rest / d)); out.push(q.slice()); fl.push(flags[i + 1]); rest = step; }
      else { rest -= d; q = b.slice(); i++; }
    }
    return { pts: out, flags: fl };
  }
  // DORMANT CHAIN (the tell, chain.floor = true). Both versions hang from the same side lock.
  //   mimic  : the chain slides FORWARD down the side face, rounds the front corner on the floor and ends in a loose
  //            curl lying IN FRONT of the chest (visible from the front 3/4: the thing viewers learn to spot).
  //   real   : (opts.realChest / chain.real) the chain drops straight down the side and is coiled up neatly on the
  //            floor at the side-BACK, like a chest somebody actually packed.
  // Floor coils are drawn with a cartoon tilt (coilSq: vertical squash of the coil, much rounder than the true 7 deg
  // camera would give) so the curl reads at small sizes. Points are in px at s = 1, relative to the ground point.
  function floorChain(p, sol, c, ls, pitch) {
    const R = sol.R, F = sol.F, A = sol.chainAnchor, hx = p.hip[0];
    const real = !!(c.real ?? p.realChest);
    // floor point; in front of the chest the floor depth is exaggerated a little (cartoon tilt) so a curl lying there
    // drops clear of the chest's bottom edge instead of climbing onto its front face
    const gnd = (x, z) => add(F.ground(x, z), [hx, Math.max(0, z - DIM.D / 2) * (c.tiltFront ?? 0.22)]);
    const xS = W / 2, D2 = DIM.D / 2;
    const sq = c.coilSq ?? 0.5;
    const pts = [A.slice()], fr = [0];
    const push = (q, f) => { pts.push(q); fr.push(f); };
    // hanging part: quadratic sag from the lock to where it touches the floor
    const hang = (T, bulge) => {
      const ctl = [lerp(A[0], T[0], 0.35) + bulge[0], lerp(A[1], T[1], 0.8) + bulge[1]];
      for (let i = 1; i <= 12; i++) { const u = i / 12, a = lerp(A[0], ctl[0], u), b = lerp(A[1], ctl[1], u), a2 = lerp(ctl[0], T[0], u), b2 = lerp(ctl[1], T[1], u); push([lerp(a, a2, u), lerp(b, b2, u)], 0); }
    };
    // a flat spiral on the floor around a centre (screen), from radius r0 to r1 over `turns`, starting at angle a0,
    // turning in direction dir (+1 = clockwise on screen)
    const spiral = (cen, r0, r1, a0, turns, dir, f) => {
      const n = Math.ceil(turns * 40);
      for (let i = 1; i <= n; i++) {
        const u = i / n, a = a0 + dir * u * turns * TAU, r = lerp(r0, r1, Math.pow(u, 0.9));
        push([cen[0] + Math.cos(a) * r, cen[1] + Math.sin(a) * r * sq], f);
      }
    };
    if (real) {
      // straight drop toward the back, then a neat stacked coil (a low helix: each turn sits on the one below)
      const T = gnd(xS + 0.05 * W, -0.45 * D2);
      hang(T, [0.03 * W, 0]);
      const cen = gnd(xS + 0.2 * W, -0.75 * D2), rr = 0.15 * W, turns = 2.4, rise = 0.042 * W;
      const a0 = Math.atan2((T[1] - cen[1]) / sq, T[0] - cen[0]);
      const n = Math.ceil(turns * 40);
      for (let i = 1; i <= n; i++) {
        const u = i / n, a = a0 - u * turns * TAU, r = rr * (1 - 0.12 * u);
        push([cen[0] + Math.cos(a) * r, cen[1] + Math.sin(a) * r * sq - u * turns * rise], 0);
      }
    } else {
      // forward: touches down near the front of the side face, rounds the front corner, curls up in front
      const T = gnd(xS + 0.07 * W, 0.45 * D2);
      hang(T, [0.05 * W, 0.02 * W]);
      const K = gnd(xS + 0.1 * W, D2 + 0.12 * W);
      push(lp(T, K, 0.5).slice(0, 2), 1); push(K, 1);
      const cen = gnd(xS - 0.06 * W, D2 + 0.34 * W), r0 = 0.18 * W;
      const a0 = Math.atan2((K[1] - cen[1]) / sq, K[0] - cen[0]);
      // from the corner it sweeps toward the camera and back in on itself: a loose 1.3-turn curl
      spiral(cen, r0, 0.035 * W, a0, 1.5, 1, 1);
    }
    const r = resample(pts, fr, pitch);
    // index where the in-front-of-the-chest part starts (even, so ring / bar alternation stays continuous)
    let k = r.flags.indexOf(1);
    if (k > 0 && k % 2) k -= 1;
    r.pts.front = k > 0 ? k : -1;
    return r.pts;
  }
  function chainPts(p, sol) {
    const c = p.chain || {};
    if (c.pts) return c.pts.map(q => [(q[0] - sol.X) / sol.Sc, (q[1] - sol.Y) / sol.Sc]);
    const A = sol.chainAnchor, links = c.links ?? 17, ls = 0.09 * W, pitch = ls * 0.7;
    const hang = Math.PI / 2 + (c.swing || 0), sag = clamp(c.sag ?? 1), start = hang - 0.75 * sag;
    const t = c.t ?? p.t ?? 0, sway = c.sway ?? 0.05;
    if (c.floor) return floorChain(p, sol, c, ls, pitch);
    const pts = [A.slice()];
    for (let i = 0; i < links; i++) {
      const u = (i + 0.5) / links;
      const a = lerp(start, hang, 1 - (1 - u) ** 1.8) + sway * u * Math.sin(TAU * 0.55 * t - u * 2.4);
      const q = pts[pts.length - 1];
      pts.push([q[0] + Math.cos(a) * pitch, q[1] + Math.sin(a) * pitch]);
    }
    return pts;
  }

  // ------------------------------------------------------------------ fx
  function paintFx(g, p, sol) {
    const fx = p.fx, t = p.t || 0, R = sol.R;
    const lidTop = R.LP([W / 2, -DIM.Hb - DIM.Tf - DIM.dome, 0]);
    if (fx.sweat) S.sweat(g, lidTop[0] + 0.12 * W, lidTop[1] + 0.12 * W + 0.03 * W * Math.sin(t * 3), 0.13 * W, { angle: 0.25 });
    if (fx.drool && sol.th > 0.1) {
      // a glossy strand that thickens into a hanging drop
      const b = lp(sol.lip.L, sol.lip.R, 0.72).slice(0, 2), Ld = 0.2 * W * (0.85 + 0.15 * Math.sin(t * 2)), dr = 0.075 * W;
      const pts = [b, [b[0] + 0.006 * W, b[1] + Ld * 0.45], [b[0] - 0.002 * W, b[1] + Ld]];
      S.strip(g, pts, u => 0.022 * W * (1 - 0.45 * u), COL.drool);
      S.strip(g, S._poly.offsetPts(pts, 0.006 * W), u => 0.007 * W * Math.sin(Math.PI * u), C.rgba(COL.droolShade, 0.9));
      S.sweat(g, b[0] - 0.002 * W, b[1] + Ld + dr * 0.32, dr, { color: COL.drool, shade: COL.droolShade });
    }
    if (fx.sparkle) {
      const e = sol.eyes;
      [[e[0][0] - 0.38 * W, e[0][1] - 0.3 * W, 0.06], [e[1][0] + 0.38 * W, e[1][1] - 0.34 * W, 0.075], [e[1][0] + 0.48 * W, e[1][1] - 0.1 * W, 0.04]].forEach(([x, y, r], i) => S.sparkle(g, x, y, r * W * (0.8 + 0.2 * Math.sin(t * 6 + i * 2)), '#FFE58A', 0.2 * i));
    }
    if (fx.zzz) {
      for (let i = 0; i < 3; i++) {
        const k = ((t * 0.35 + i / 3) % 1);
        S.label(g, 'z', sol.mouth[0] + 0.4 * W + k * 0.2 * W, lidTop[1] - 0.2 * W - k * 0.28 * W, (0.12 + 0.1 * k) * W, { color: COL.zzz, alpha: Math.sin(Math.PI * k), weight: 900 });
      }
    }
    if (fx.hearts) {
      for (let i = 0; i < 3; i++) {
        const k = ((t * 0.3 + i / 3) % 1), x = lidTop[0] + (i - 1) * 0.35 * W - 0.4 * W, y = lidTop[1] - 0.02 * W - k * 0.45 * W, sz = (0.07 + 0.03 * i) * W;
        g.save(); g.globalAlpha *= Math.sin(Math.PI * k) * 0.95; g.translate(x, y);
        g.beginPath(); g.moveTo(0, sz * 0.55); g.bezierCurveTo(-sz * 0.9, -sz * 0.05, -sz * 0.5, -sz * 0.75, 0, -sz * 0.3); g.bezierCurveTo(sz * 0.5, -sz * 0.75, sz * 0.9, -sz * 0.05, 0, sz * 0.55); g.fillStyle = COL.heart; g.fill();
        g.restore();
      }
    }
    if (fx.tears && sol.th > 0.1) {
      for (let i = 0; i < 2; i++) { const e = sol.eyes[i]; S.tear(g, e[0] + (i ? 1 : -1) * 0.1 * W, e[1] + 0.03 * W, 0.06 * W * fx.tears, 0.022 * W); }
    }
  }

  // ------------------------------------------------------------------ main paint
  function paint(g, p, sol) {
    FL = clamp(p.flesh ?? 0);
    const near = sol.near, sideOn = Math.abs(sol.R.yawDeg) > 12;
    const legKeys = Object.keys(sol.legs), armKeys = Object.keys(sol.arms);
    const farKey = near === 0 ? null : near > 0 ? 'L' : 'R';
    const drawLeg = (k, far) => { const Lg = sol.legs[k]; paintLeg(g, Lg, far, sol.F); paintFoot(g, Lg, sol.F, far); };
    let chain = null;
    if (p.parts.chain && sol.chainAnchor) chain = chainPts(p, sol);
    const chainBack = chain && chain.front > 0 ? chain.slice(0, chain.front + 1) : chain;
    const chainFront = chain && chain.front > 0 ? chain.slice(chain.front) : null;
    if (chainBack && !sol.chainNear) S.drawChain(g, chainBack, 0.09 * W, COL.chain);
    const isFarArm = k => k === farKey && sideOn;
    if (p.parts.arms && farKey && sol.arms[farKey] && sol.arms[farKey].mode === 'arm' && sideOn) paintArm(g, sol.arms[farKey], true);
    if (p.parts.legs) {
      const order = legKeys.slice().sort((a, b) => (a === farKey ? -1 : b === farKey ? 1 : 0));
      order.forEach(k => drawLeg(k, k === farKey));
    }
    const poly = mouthPoly(sol);
    if (p.parts.tongue && sol.tongue && sol.tongue.behind) paintTongue(g, p, sol);
    if (sol.th > 0.012) S.poly(g, poly, COL.mouth);
    paintLid(g, p, sol);
    paintFace(g, p, sol, poly);
    paintTeeth(g, p, sol, 'up');
    sol.bodyHull = paintBody(g, p, sol).hull;
    paintHasp(g, p, sol);
    // near arms: the root is re-covered by the box walls and the upper tooth row, so the arm comes OUT of the mouth
    // gap at the corner instead of sitting on the outside of the box
    if (p.parts.arms) armKeys.forEach(k => {
      const Ar = sol.arms[k];
      if (Ar.mode !== 'arm' || isFarArm(k)) return;
      paintArm(g, Ar, false, { socket: sol.th > 0.15 ? poly : null });
      g.save(); g.beginPath(); g.arc(Ar.sh[0], Ar.sh[1], 0.17 * W, 0, TAU); g.clip();
      g.save(); g.beginPath(); g.rect(-1e5, -1e5, 2e5, 2e5); pathPts(g, poly); g.clip('evenodd'); paintBody(g, p, sol); g.restore();
      paintTeeth(g, p, sol, 'up');
      g.restore();
    });
    paintTeeth(g, p, sol, 'lo', poly);
    if (p.parts.tongue && sol.tongue && !sol.tongue.behind) paintTongue(g, p, sol);
    // gripping hands (peek): only below the upper lip line, so the lid edge stays in front of the wrists
    if (p.parts.arms) armKeys.forEach(k => {
      const Ar = sol.arms[k];
      if (Ar.mode !== 'hand') return;
      const { uL, uR } = sol.lip, dv = nrm(sub(uR, uL)), dn = perp(dv), sg = dot(dn, [0, 1]) >= 0 ? 1 : -1;
      const a = add(uL.slice(0, 2), mul(dv, -2 * W)), b = add(uR.slice(0, 2), mul(dv, 2 * W));
      g.save(); g.beginPath(); pathPts(g, [a, b, add(b, mul(dn, sg * 3 * W)), add(a, mul(dn, sg * 3 * W))]); g.clip();
      paintHand(g, Ar, tonesOf(false));
      g.restore();
    });
    if (chainBack && sol.chainNear) S.drawChain(g, chainBack, 0.09 * W, COL.chain);
    if (chainFront) S.drawChain(g, chainFront, 0.09 * W, COL.chain);
    if (p.parts.fx) paintFx(g, p, sol);
    sol.chain = chain;
  }

  function boundsOf(sol, p) {
    const pts = [];
    const R = sol.R;
    for (const x of [-W / 2 - 10, W / 2 + 10]) for (const y of [0, -DIM.Hb - DIM.Tf - DIM.dome - DIM.D]) for (const z of [-DIM.D, DIM.D]) pts.push(R.P([x, y, z]));
    Object.values(sol.legs).forEach(L => pts.push(L.hip, L.knee, L.ankle, add(L.ankle, [0, 0.12 * W])));
    Object.values(sol.arms).forEach(A => { if (A.sh) pts.push(A.sh, A.elbow); pts.push(A.wrist); });
    if (sol.tongue) pts.push(...sol.tongue.pts);
    if (sol.chain) pts.push(...sol.chain);
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const q of pts) { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); }
    const pad = 0.6 * W;
    return { x: x0 - pad, y: y0 - pad, w: x1 - x0 + 2 * pad, h: y1 - y0 + 2 * pad };
  }

  // ------------------------------------------------------------------ screen-space mood light on the rendered group
  let _tmp = null;
  function scratch(w, h) {
    if (!_tmp) _tmp = document.createElement('canvas');
    if (_tmp.width < w || _tmp.height < h) { _tmp.width = Math.max(_tmp.width, w); _tmp.height = Math.max(_tmp.height, h); }
    const g = _tmp.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none'; g.clearRect(0, 0, w, h);
    return _tmp;
  }
  function applyLight(L, o, dev) {
    const c = L.canvas, g = c.getContext('2d'), w = L.w, h = L.h;
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    if (o.falloff) {                                                            // darker away from the overhead light
      g.globalCompositeOperation = 'source-atop';
      const lg = g.createLinearGradient(0, o.falloff.y0 - L.y, 0, o.falloff.y1 - L.y);
      lg.addColorStop(0, 'rgba(12,10,18,0)'); lg.addColorStop(1, `rgba(12,10,18,${o.falloff.a ?? 0.45})`);
      g.fillStyle = lg; g.fillRect(0, 0, w, h);
    }
    const edge = (v, dpx, col, a, blur) => {
      if (!col || !a) return;
      const t = scratch(w, h), tg = t.getContext('2d');
      tg.drawImage(c, 0, 0, w, h, 0, 0, w, h);
      tg.globalCompositeOperation = 'destination-out'; tg.drawImage(c, 0, 0, w, h, -v[0] * dpx, -v[1] * dpx, w, h);
      tg.globalCompositeOperation = 'source-in'; tg.fillStyle = col; tg.fillRect(0, 0, w, h);
      g.globalCompositeOperation = 'screen'; g.globalAlpha = a; g.filter = blur ? `blur(${blur}px)` : 'none';
      g.drawImage(t, 0, 0, w, h, 0, 0, w, h);
      g.filter = 'none'; g.globalAlpha = 1;
    };
    edge(nrm(o.keyDir || [-0.45, -1]), (o.keyD ?? 0.05 * W) * dev, o.key, o.keyA ?? 0.4, 2 * dev);
    edge(nrm(o.rimDir || [1, -0.15]), (o.rimD ?? 0.022 * W) * dev, o.rim, o.rimA ?? 0.6, 0.8 * dev);
    g.restore();
  }

  function prep(x, y, s, opts) {
    const p = resolve(opts), sol = solve(p);
    sol.X = x; sol.Y = y; sol.Sc = s;
    if (p.parts.chain && sol.chainAnchor) sol.chain = chainPts(p, sol);
    const b = boundsOf(sol, p);
    return { p, sol, bounds: { x: x + b.x * s, y: y + b.y * s, w: b.w * s, h: b.h * s } };
  }

  function draw(ctx, x, y, s = 1, opts = {}) {
    const { p, sol, bounds } = prep(x, y, s, opts);
    const shadow = p.shadow || 'drop';
    if (shadow === 'ground' && !p.silhouette) {
      const feet = Object.values(sol.legs).filter(L => L.ankle[1] > -0.35 * W);
      ctx.save(); ctx.globalAlpha *= p.alpha ?? 1;
      const legs = Object.values(sol.legs);
      if (p.hip[1] > -0.3 * W || !legs.length) S.groundShadow(ctx, x + p.hip[0] * s, y, 1.25 * W * s, 0.2 * W * s, 0.55);
      else if (!feet.length) {
        const h = -Math.max(...legs.map(L => L.ankle[1])), k = clamp(1 - h / (1.8 * W));
        S.groundShadow(ctx, x + p.hip[0] * s, y, (0.7 + 0.5 * k) * W * s, (0.12 + 0.06 * k) * W * s, 0.18 + 0.32 * k);
      }
      feet.forEach(L => { const k = clamp(1 + L.ankle[1] / (0.35 * W)); S.groundShadow(ctx, x + L.ankle[0] * s + 0.06 * W * s * Math.sign(sol.R.sy || 0.0001), y + 0.01 * W * s, 0.42 * W * s, 0.09 * W * s, 0.5 * k); });
      ctx.restore();
    }
    const body = g => { g.save(); g.translate(x, y); g.scale(s, s); paint(g, p, sol); g.restore(); };
    if (p.silhouette || p.light) {
      const L = S.layer(ctx, body, bounds, 8);
      if (!L) return sol;
      const lc = L.canvas.getContext('2d');
      if (p.silhouette) { lc.save(); lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'source-in'; lc.fillStyle = p.silhouette; lc.fillRect(0, 0, L.w, L.h); lc.restore(); }
      else applyLight(L, p.light, Math.hypot(ctx.getTransform().a, ctx.getTransform().b));
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha *= p.alpha ?? 1;
      ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x, L.y, L.w, L.h);
      ctx.restore(); L.release();
      return sol;
    }
    if (shadow === 'drop') S.shadowGroup(ctx, body, { scale: s, alpha: p.alpha ?? 1, bounds });
    else S.shadowGroup(ctx, body, { shadow: false, alpha: p.alpha ?? 1, bounds });
    return sol;
  }

  // flat blurred silhouette laid on the floor from the ground point (falls toward the camera, skewed)
  function castShadow(ctx, x, y, s = 1, opts = {}, o = {}) {
    const { p, sol, bounds } = prep(x, y, s, opts);
    const L = S.layer(ctx, g => { g.save(); g.translate(x, y); g.scale(s, s); paint(g, p, sol); g.restore(); }, bounds, 8);
    if (!L) return;
    const lc = L.canvas.getContext('2d');
    lc.save(); lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'source-in'; lc.fillStyle = o.color || '#000'; lc.fillRect(0, 0, L.w, L.h); lc.restore();
    const m = ctx.getTransform(), gx = m.a * x + m.c * y + m.e, gy = m.b * x + m.d * y + m.f;
    const sq = o.squash ?? 0.2, sk = o.skew ?? 0.5;
    ctx.save(); ctx.setTransform(1, 0, -sk, -sq, sk * gy, gy + sq * gy);
    ctx.globalAlpha *= o.alpha ?? 0.5; ctx.filter = `blur(${o.blur ?? 6}px)`;
    ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x, L.y, L.w, L.h);
    ctx.restore(); L.release();
  }

  function anchors(x, y, s = 1, opts = {}) {
    const p = resolve(opts), sol = solve(p);
    const T = q => [x + q[0] * s, y + q[1] * s];
    const R = sol.R;
    const hands = {}, feet = {}, knees = {}, elbows = {};
    Object.entries(sol.arms).forEach(([k, A]) => { hands[k] = T(A.wrist); if (A.elbow) elbows[k] = T(A.elbow); });
    Object.entries(sol.legs).forEach(([k, L]) => { feet[k] = T(L.ankle); knees[k] = T(L.knee); });
    sol.X = x; sol.Y = y; sol.Sc = s;
    const b = boundsOf(sol, p);
    return {
      chain: sol.chainAnchor ? T(sol.chainAnchor) : null, eyes: sol.eyes.map(T), mouth: T(sol.mouth), hip: T(p.hip),
      lidTop: T(R.LP([0, -DIM.Hb - DIM.Tf - DIM.dome, 0])), hands, feet, knees, elbows, lip: T(lp(sol.lip.L, sol.lip.R, 0.5)), bounds: { x: x + b.x * s, y: y + b.y * s, w: b.w * s, h: b.h * s },
    };
  }

  // ------------------------------------------------------------------ placeholder knight (2.4 W tall), flat grey
  function knight(ctx, x, y, s = 1, o = {}) {
    const H = 2.4 * W, col = o.color || '#7A7E86', sh = o.shade || '#5A5D64', sl = '#0B0C0F';
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s * (o.flip ? -1 : 1), s);
      const u = H / 6;
      S.roundRect(g, -0.62 * u, -2.3 * u, 0.5 * u, 2.3 * u, 0.12 * u, sh);
      S.roundRect(g, 0.12 * u, -2.3 * u, 0.5 * u, 2.3 * u, 0.12 * u, col);
      S.roundRect(g, -0.75 * u, -0.28 * u, 0.7 * u, 0.28 * u, 0.1 * u, sh); S.roundRect(g, 0.05 * u, -0.28 * u, 0.72 * u, 0.28 * u, 0.1 * u, col);
      S.roundPoly(g, [[-1.0 * u, -4.6 * u], [1.0 * u, -4.6 * u], [0.85 * u, -2.6 * u], [-0.85 * u, -2.6 * u]], 0.18 * u, col);
      S.roundPoly(g, [[-0.9 * u, -2.8 * u], [0.9 * u, -2.8 * u], [1.05 * u, -1.9 * u], [-1.05 * u, -1.9 * u]], 0.12 * u, sh);
      S.roundRect(g, -1.45 * u, -4.75 * u, 0.75 * u, 0.6 * u, 0.25 * u, col); S.roundRect(g, 0.7 * u, -4.75 * u, 0.75 * u, 0.6 * u, 0.25 * u, col);
      S.roundRect(g, -1.38 * u, -4.3 * u, 0.42 * u, 1.9 * u, 0.15 * u, sh); S.roundRect(g, 0.96 * u, -4.3 * u, 0.42 * u, 1.9 * u, 0.15 * u, sh);
      S.roundRect(g, -0.55 * u, -5.95 * u, 1.1 * u, 1.3 * u, [0.35 * u, 0.35 * u, 0.12 * u, 0.12 * u], col);
      S.roundRect(g, -0.42 * u, -5.45 * u, 0.84 * u, 0.09 * u, 0.04 * u, sl);
      S.roundRect(g, -0.05 * u, -5.36 * u, 0.1 * u, 0.4 * u, 0.04 * u, sl);
      g.restore();
    }, { scale: s, alpha: o.alpha ?? 1 });
  }

  window.MIMIKU2 = { draw, pose, walkPose, jumpPose, pouncePose, lerpPose, anchors, castShadow, knight, merge, yawFrame, EXPR, COL, DIM, version: '2.2' };
})();
