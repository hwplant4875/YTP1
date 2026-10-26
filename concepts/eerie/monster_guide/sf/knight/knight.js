/* =====================================================================================================================
 * knight.js : window.KNIGHT, the "Guests" of Monster HR: faceless full-plate knights (adventurers).
 * Needs core/lib_core.js (window.SFX) loaded first. Plain canvas 2D, deterministic (SFX.hash / SFX.rng, never
 * Math.random). Spec: plan_v2_changes.md section B "Guests" + owner decisions 2026-10-26.
 *
 * LOOK
 *   Generic gothic full plate (fluted breastplate, ogee plackart, fan-winged couters / poleyns, pointed sabatons) in
 *   the show's cute construction: chunky stubby proportions with a BIG helm (~3.2 heads tall), rounded shapes, flat
 *   fills, ONE hard shade per plate (bottom-right) plus a thin top-left light edge so it reads as metal, no outlines,
 *   one group drop shadow. FACELESS: the visor slit is pure #0B0C0F, nothing is ever visible inside. They act only
 *   through helm tilt / nod, hands, posture, sweat drops and little motion lines.
 *   Plate #7A7E86, shade #5A5D64, light edge / rim #A9AEB5 (plan B). One muted cloth accent per type.
 *   Avoided on purpose: onion helms, stone-slab armour, blue tabards (no specific game set).
 *
 * TYPES (H = the plan's helm unit, 136 px; shoulder widths follow plan B)
 *   'hammer'  wide (shoulders ~1.6 H), flat-topped bucket great helm with a cross brace, big two-handed maul,
 *             rust sash.
 *   'spear'   thin (shoulders ~1.0 H), tall pointed sugarloaf helm, long winged spear with a pennon, olive half-cape.
 *   'shield'  medium (shoulders ~1.3 H), round helm with a tall stepped crest + wine plume, big heater shield (key
 *             emblem) on the far arm and a lantern in the near hand.
 *   At s = 1 (chest width W = 180 px) the helm dome tops out at ~2.4 W = 432 px; the spear point and the crest go higher.
 *
 * VARIANTS
 *   'normal'  as above.
 *   'k404'    the recurring 404 knight (any type; the show uses the spear knight): a jagged scratch on the left of the
 *             helm, a small notebook "PROTOCOL 404" and a quill at the belt (the notebook pose uses that notebook).
 *   'horror'  dark plate #2B2D33, one accent line #A8443A (belt), one cold light line #E2FFFA glowing in the slit.
 *             Still faceless: only the line, never eyes.
 *
 * API
 *   KNIGHT.draw(ctx, x, y, s = 1, o = {}) -> R    whole knight as ONE shadow group. (x, y) = ground point between the
 *                                                  feet (pose 'peek': the foot of the edge it peeks around).
 *     type      'hammer' | 'spear' | 'shield'                       variant  'normal' | 'k404' | 'horror'
 *     pose      'idle' | 'walk' | 'ready' | 'knock' | 'notebook' | 'backaway' | 'nod' | 'peek'
 *     phase     walk cycle 0..1 (two steps). One cycle covers KNIGHT.stride(type) * s px: move x yourself.
 *     k         0..1 progress for 'knock' (0 wind-up, 0.5 contact, 0.62 rebound, 1 listening) and 'nod'
 *               (0 up, 0.5 down, 1 up again). 'backaway' k = retreat cycle (shuffle) phase.
 *     knockAt   [dx, dy] contact point relative to (x, y) in px at s = 1 along the facing (default
 *               KNIGHT.knockAt(type): the lid top of a dormant chest whose centre is KNIGHT.chestDX(type) ahead)
 *     facing    1 = faces screen-right (default), -1 = screen-left (mirrors; light stays top-left)
 *     tilt      extra helm tilt in degrees (+ = top of the helm toward the facing side)
 *     nod       extra helm nod 0..1 (slit drops, helm pitches forward)
 *     lean      extra torso lean in degrees (+ = forward)
 *     t         seconds: idle breathing, lantern swing + flicker, pennon / plume / sash flutter, tremble
 *     sweat     0..3 sweat drops by the helm (backaway defaults to 2)
 *     lines     0..1 motion / tremble lines (backaway defaults to 1)
 *     impact    0..1 knock impact burst at the contact point (knock sets it automatically around k = 0.5)
 *     rim       false | { color, alpha, width, dir } rim light (use on stone, the plate is only 2.75:1 there)
 *     shadow    group drop shadow (default true);  cast  contact shadow (default true);  alpha  whole-figure fade
 *     tint      { color, amount, mode } colour laid over the figure only: depth fog (normal blend) for knights further
 *               back;  grade  same, applied first, for light colour (e.g. { color: '#FFB46A', amount: .3, mode: 'soft-light' })
 *     lantern   { lit (default true, false in horror), glow (default 1) } for the shield knight
 *     spearLen  spear length in px at s = 1 (default 540; trim it for tight shots and crowded sheets)
 *     peek options (pose 'peek'):  peekH = height of the helm centre above y (px at s = 1, default standing),
 *               peekOut = how far the helm centre is past the edge (default 0.5 helm widths), handH = height of the
 *               gripping hand (default peekH - 0.55 helm height), part = 'all' | 'helm' | 'hand' (draw only that part,
 *               e.g. the helm inside a doorway clip and the fingers on the wall face), clip = fn(ctx) adding the
 *               visible-region sub-path in CANVAS coordinates (the helm is clipped to it, the fingers are not).
 *               The edge is at x; the hidden body is on the -facing side, the helm leans out toward +facing.
 *   KNIGHT.solve(x, y, s, o) -> { helm: {x, y, w, h, top}, hands: {near, far}, contact, lantern, bounds }  canvas px
 *   KNIGHT.stride(type) -> ground px per walk cycle at s = 1;   KNIGHT.knockAt(type), KNIGHT.chestDX(type)
 *   KNIGHT.drawHelm(ctx, x, y, s, o)   helm only (callouts / close-ups). (x, y) = helm bottom centre. o: type, variant,
 *               tilt, nod, facing, t.
 *   KNIGHT.drawProp(ctx, name, x, y, s, o)   'hammer' | 'spear' | 'shield' | 'lantern' | 'notebook' | 'quill' (callouts)
 *   KNIGHT.TYPES, KNIGHT.COL, KNIGHT.POSES, KNIGHT.W (180), KNIGHT.H (136)
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX;
  if (!S) throw new Error('knight.js needs lib_core.js (window.SFX) loaded first');
  const C = S.color, TAU = Math.PI * 2, RAD = Math.PI / 180, clamp = S.clamp, lerp = S.lerp, E = S.ease;
  const W = 180, HU = 136;

  // ------------------------------------------------------------------------------------------------ palette
  const COL = {
    normal: {
      plate: '#7A7E86', shade: '#5A5D64', light: '#A9AEB5', deep: '#3E4148', slit: '#0B0C0F', rivet: '#B4B9C1',
      mail: '#4A4D55', mailShade: '#383B41',
      leather: '#5B4537', leatherShade: '#3F2F26', brass: '#A88A54', brassShade: '#7A6238',
      wood: '#6E5644', woodShade: '#4E3D30', woodLight: '#8A715C',
      accent: null,
    },
    horror: {
      plate: '#2B2D33', shade: '#1D1F23', light: '#454850', deep: '#141518', slit: '#060708', rivet: '#4C4F57',
      mail: '#1E2024', mailShade: '#141518',
      leather: '#222126', leatherShade: '#17161A', brass: '#3A3B40', brassShade: '#2A2B30',
      wood: '#2A2629', woodShade: '#1C1A1C', woodLight: '#38333A',
      accent: '#A8443A', slitLight: '#E2FFFA',
    },
    cloth: {
      hammer: ['#7A4536', '#5A3128'], spear: ['#57573F', '#3F3F2E'], shield: ['#7A3338', '#582328'],
    },
    clothHorror: ['#1E1F23', '#151619'],
    shieldField: ['#6B3A36', '#4E2926'], emblem: ['#D8CFBD', '#B3A994'],
    flame: ['#FFF3C4', '#FFD27A', '#FFB04A'], glass: '#FFCF7A', glassShade: '#E9A94E',
    paper: '#F4EFE6', paperLine: '#CEC5B6', book: '#3B2E2B', bookShade: '#2A201E', bookLabel: '#E9E1CF', ink: '#1C1519',
    quill: '#ECE5D6', quillShade: '#CBC1AE', sweat: '#a9dcff',
  };

  // ------------------------------------------------------------------------------------------------ types
  // all lengths in px at s = 1. hip = hip-joint height, torso = hip joint -> neck, helm = dome height above the neck.
  const TYPES = {
    hammer: {
      name: 'hammer', helm: 'bucket', helmW: 134, helmH: 138, hip: 136, torso: 158,
      waistW: 112, chestW: 166, shX: 74, shDrop: 30, paulR: 47, armU: 54, armL: 50, armW: 40, fist: 23,
      legX: 30, legW: 50, thigh: 68, shin: 60, ankle: 16, foot: 64, footH: 26, stance: 34, strideA: 24, lift: 22,
      knockDX: 168, chestDX: 208,
    },
    spear: {
      name: 'spear', helm: 'point', helmW: 102, helmH: 120, point: 52, hip: 160, torso: 148,
      waistW: 74, chestW: 112, shX: 47, shDrop: 26, paulR: 30, armU: 58, armL: 54, armW: 29, fist: 18,
      legX: 20, legW: 35, thigh: 80, shin: 70, ankle: 15, foot: 56, footH: 21, stance: 24, strideA: 30, lift: 24,
      knockDX: 168, chestDX: 208,
    },
    shield: {
      name: 'shield', helm: 'crest', helmW: 118, helmH: 128, crest: 58, hip: 148, torso: 152,
      waistW: 92, chestW: 138, shX: 60, shDrop: 28, paulR: 37, armU: 56, armL: 52, armW: 34, fist: 21,
      legX: 25, legW: 42, thigh: 74, shin: 64, ankle: 16, foot: 60, footH: 24, stance: 28, strideA: 27, lift: 23,
      knockDX: 120, chestDX: 160,
    },
  };

  let LX = 1;     // facing of the knight being drawn (light-aware offsets in mirrored local space)
  let P = COL.normal;

  // ------------------------------------------------------------------------------------------------ small math
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, k) => [a[0] * k, a[1] * k];
  const rot = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
  const ang = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]);
  const dist = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  const lp = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
  const polar = (p, a, l) => [p[0] + Math.cos(a) * l, p[1] + Math.sin(a) * l];
  const frac = v => v - Math.floor(v);

  // two-bone IK: returns [joint, end]. bend +1 bends the joint to the left of a->b (screen: knee forward for a leg
  // pointing down when facing right), -1 the other way.
  function ik(a, b, l1, l2, bend) {
    let d = dist(a, b);
    const dmax = l1 + l2 - 0.5, dmin = Math.abs(l1 - l2) + 0.5;
    let e = b;
    if (d > dmax) { e = polar(a, ang(a, b), dmax); d = dmax; }
    if (d < dmin) { e = polar(a, ang(a, b), dmin); d = dmin; }
    const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
    const base = ang(a, e);
    return [polar(a, base - bend * A, l1), e];
  }

  // ------------------------------------------------------------------------------------------------ paint helpers
  // plate: flat base + ONE hard shade (bottom-right) + thin light edge (top-left) = brushed metal in the show's style
  function plate(g, path, o = {}) {
    const sd = o.sd ?? 6, ld = o.ld ?? 2.4;
    S.cel(g, path, o.base || P.plate, o.shade === false ? null : (o.shadeCol || P.shade), sd * LX, sd);
    if (ld > 0 && o.light !== false) {
      g.save(); g.beginPath(); path(g); g.clip();
      g.beginPath(); g.rect(-1e5, -1e5, 2e5, 2e5);
      g.translate(ld * LX, ld); path(g); g.translate(-ld * LX, -ld);
      g.fillStyle = o.lightCol || P.light; g.fill('evenodd');
      g.restore();
    }
  }
  const flat = (g, path, col) => { g.beginPath(); path(g); g.fillStyle = col; g.fill(); };
  function line(g, pts, col, w, tension) {
    g.save(); g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round';
    g.beginPath();
    if (tension) S.addCurve(g, pts, tension); else pts.forEach((p, i) => (i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])));
    g.stroke(); g.restore();
  }
  function rivet(g, x, y, r) {
    S.circle(g, x, y, r, P.rivet);
    S.circle(g, x + 0.3 * r * LX, y + 0.3 * r, r * 0.6, P.shade);
    S.circle(g, x - 0.1 * r * LX, y - 0.1 * r, r * 0.55, P.rivet);
  }
  // hard occlusion shadow: the part about to be drawn darkens what is ALREADY drawn behind it (source-atop keeps it
  // off the background), offset down-right like the show's light. Call right before drawing the part.
  function occl(g, path, d = 7, a = 0.34) {
    g.save(); g.globalCompositeOperation = 'source-atop';
    g.translate(d * LX, d); g.beginPath(); path(g); g.fillStyle = 'rgba(12,14,20,' + a + ')'; g.fill();
    g.restore();
  }
  // a capsule plate between two points (limb armour)
  const capPath = (a, b, w1, w2) => g => S.addCapsule(g, a[0], a[1], b[0], b[1], w1, w2);

  // ------------------------------------------------------------------------------------------------ helms
  // helm-local: origin = helm bottom centre (neck), up = -y. f = feature shift toward the face (3/4 view), nod 0..1.
  function helmGeo(T) {
    const w = T.helmW, h = T.helmH;
    return { w, h, f: 0.13 * w };
  }

  function drawHelmLocal(g, T, o) {
    const { w, h, f } = helmGeo(T);
    const nod = o.nod || 0, ny = nod * 0.1 * h, t = o.t || 0;
    const horror = o.variant === 'horror';
    if (T.helm === 'bucket') {
      // flat-topped great helm, barrel sides
      const body = c => S.addRoundPoly(c, [[-w * 0.47, -h], [w * 0.47, -h], [w * 0.52, -h * 0.55], [w * 0.5, 0], [-w * 0.5, 0], [-w * 0.52, -h * 0.55]], [w * 0.2, w * 0.2, w * 0.3, w * 0.1, w * 0.1, w * 0.3]);
      plate(g, body, { sd: 9, ld: 3 });
      g.save(); g.beginPath(); body(g); g.clip(); // every feature stays inside the barrel
      // top plate rim (flat top seen almost edge-on)
      g.fillStyle = P.light; g.globalAlpha = 0.55; g.beginPath(); g.ellipse(0, -h + 2, w * 0.4, 6, 0, Math.PI, TAU); g.fill(); g.globalAlpha = 1;
      // crown band
      flat(g, c => c.rect(-w, -h * 0.86, 2 * w, 5), P.shade);
      flat(g, c => c.rect(-w, -h * 0.86 - 3, 2 * w, 3), P.light);
      // bottom band
      flat(g, c => c.rect(-w, -h * 0.13, 2 * w, h * 0.13), P.shade);
      flat(g, c => c.rect(-w, -h * 0.13, 2 * w, 3), P.light);
      for (let i = 0; i < 5; i++) rivet(g, -w * 0.38 + i * w * 0.19 + f * 0.4, -h * 0.065, 3.4);
      // brow plate + eye slits + cross brace
      const sy = -h * 0.56 + ny, sh = h * 0.085;
      const brow = c => S.addRoundRect(c, -w * 0.47 + f * 0.5, sy - sh * 1.6, w * 0.95, sh * 1.25, 4);
      plate(g, brow, { sd: 3, ld: 2 });
      // slits (pure dark): left one longer (we see more of it), the far one wraps around the barrel
      const slitL = c => S.addRoundRect(c, -w * 0.4 + f, sy - sh / 2, w * 0.34, sh, sh / 2);
      const slitR = c => S.addRoundRect(c, f + w * 0.07, sy - sh / 2, w * 0.3, sh, sh / 2);
      flat(g, slitL, P.slit); flat(g, slitR, P.slit);
      if (horror) coldSlit(g, [[-w * 0.36 + f, sy], [f + w * 0.33, sy]], sh, t);
      // vertical brace down the middle (the cross)
      const brace = c => S.addRoundRect(c, f - w * 0.055, -h * 0.97, w * 0.11, h * 0.84, 5);
      plate(g, brace, { sd: 3, ld: 2 });
      rivet(g, f, -h * 0.78, 3.2); rivet(g, f, sy - sh * 1.0 + 2, 3.2); rivet(g, f, -h * 0.3, 3.2);
      // breaths: small holes on the face side, low
      for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) S.circle(g, f + w * (0.15 + j * 0.09) , -h * (0.38 - i * 0.075) + ny * 0.5, 2.6, P.slit);
      g.restore();
    } else if (T.helm === 'point') {
      const pt = T.point;
      // aventail / bevor flare at the bottom
      const bev = c => S.addRoundPoly(c, [[-w * 0.5, -h * 0.34], [w * 0.5, -h * 0.34], [w * 0.56, 0], [-w * 0.56, 0]], [10, 10, 8, 8]);
      plate(g, bev, { sd: 6, ld: 2 });
      // sugarloaf skull rising to a point (tip leans slightly back)
      const tipX = -w * 0.06;
      const body = c => {
        c.moveTo(-w * 0.5, -h * 0.18);
        c.bezierCurveTo(-w * 0.53, -h * 0.66, -w * 0.38, -h * 0.98, tipX, -h - pt);
        c.bezierCurveTo(w * 0.36, -h * 0.98, w * 0.53, -h * 0.66, w * 0.5, -h * 0.18);
        c.quadraticCurveTo(0, -h * 0.1, -w * 0.5, -h * 0.18);
        c.closePath();
      };
      plate(g, body, { sd: 8, ld: 3 });
      // comb ridge from the tip down to the brow
      line(g, [[tipX + 1, -h - pt + 10], [f * 0.55, -h * 0.85], [f * 0.9, -h * 0.62]], P.light, 3, 0.5);
      line(g, [[tipX + 4, -h - pt + 14], [f * 0.55 + 3, -h * 0.84], [f * 0.9 + 3, -h * 0.62]], P.shade, 2, 0.5);
      // visor: a plate across the face with one slit at its top edge
      const sy = -h * 0.52 + ny, sh = h * 0.08;
      const visor = c => S.addRoundPoly(c, [[-w * 0.46 + f * 0.6, sy - sh * 0.2], [w * 0.46 + f * 0.4, sy - sh * 0.2], [w * 0.5 + f * 0.2, -h * 0.22], [f + w * 0.05, -h * 0.13], [-w * 0.48 + f * 0.4, -h * 0.22]], [6, 6, 10, 6, 10]);
      plate(g, visor, { sd: 5, ld: 2.2 });
      const slit = c => S.addRoundRect(c, -w * 0.39 + f, sy - sh / 2 - sh * 0.4, w * 0.76, sh, sh / 2);
      flat(g, slit, P.slit);
      if (horror) coldSlit(g, [[-w * 0.35 + f, sy - sh * 0.4], [w * 0.33 + f, sy - sh * 0.4]], sh, t);
      // visor pivot rivet on the side + two small breath dots low on the far side
      rivet(g, -w * 0.4, -h * 0.42 + ny * 0.5, 4.5);
      S.circle(g, f + w * 0.27, -h * 0.3 + ny * 0.5, 2.3, P.slit); S.circle(g, f + w * 0.27, -h * 0.24 + ny * 0.5, 2.3, P.slit);
    } else { // crest
      const ch = T.crest;
      const sw = Math.sin(t * 2.1);
      const cloth = o.variant === 'horror' ? COL.clothHorror : COL.cloth.shield;
      // plume: a bushy horsehair comma hanging off the back of the crest
      const plume = c => S.addBlob(c, [[-w * 0.08, -h - ch * 0.98], [-w * 0.5, -h - ch * 0.98], [-w * 0.8 + sw * 2, -h * 0.82], [-w * 0.74 + sw * 4, -h * 0.34], [-w * 0.6 + sw * 2, -h * 0.62], [-w * 0.42, -h * 0.92], [-w * 0.2, -h - ch * 0.62]], 0.5);
      S.cel(g, plume, cloth[0], cloth[1], 8 * LX, 6);
      line(g, [[-w * 0.4, -h - ch * 0.8], [-w * 0.64 + sw * 2, -h * 0.9], [-w * 0.7 + sw * 3, -h * 0.55]], C.shade(cloth[0], 0.2), 3, 0.5);
      // crest: a tall fluted fan of plate running front to back over the dome, scalloped top edge
      const cw2 = w * 0.36, cb = -h * 0.9, ctop = -h - ch;
      const fin = c => {
        c.moveTo(cw2, cb);
        const n = 5;
        for (let i = 0; i <= n; i++) {
          const u = i / n, x = lerp(cw2 * 1.05, -cw2 * 1.05, u), y = ctop + 22 * Math.pow(Math.abs(u - 0.4) * 1.6, 1.6) * 1.0;
          if (i === 0) c.lineTo(x, y + 18);
          const xn = lerp(cw2 * 1.05, -cw2 * 1.05, (i + 0.5) / n);
          if (i < n) c.quadraticCurveTo(xn, y - 14, lerp(cw2 * 1.05, -cw2 * 1.05, (i + 1) / n), ctop + 22 * Math.pow(Math.abs((i + 1) / n - 0.4) * 1.6, 1.6));
        }
        c.lineTo(-cw2, cb);
        c.closePath();
      };
      plate(g, fin, { sd: 6, ld: 2.8 });
      g.save(); g.beginPath(); fin(g); g.clip();
      for (let i = 1; i < 5; i++) { const x = lerp(cw2, -cw2, i / 5); line(g, [[x * 0.35, cb], [x * 1.05, ctop + 14]], P.shade, 2); line(g, [[x * 0.35 - 2 * LX, cb], [x * 1.05 - 2 * LX, ctop + 14]], P.light, 1.2); }
      g.restore();
      // round dome
      const body = c => {
        c.moveTo(-w * 0.5, -h * 0.2);
        c.lineTo(-w * 0.5, -h * 0.55);
        c.bezierCurveTo(-w * 0.5, -h * 1.03, w * 0.5, -h * 1.03, w * 0.5, -h * 0.55);
        c.lineTo(w * 0.5, -h * 0.2);
        c.quadraticCurveTo(0, -h * 0.12, -w * 0.5, -h * 0.2);
        c.closePath();
      };
      plate(g, body, { sd: 8, ld: 3 });
      // cheek / bevor plates at the bottom (flared)
      const bev = c => S.addRoundPoly(c, [[-w * 0.5, -h * 0.3], [w * 0.5, -h * 0.3], [w * 0.55, 0], [-w * 0.55, 0]], [10, 10, 8, 8]);
      plate(g, bev, { sd: 6, ld: 2 });
      line(g, [[-w * 0.5, -h * 0.15], [w * 0.5, -h * 0.15]], P.shade, 2.2);
      // visor: pointed (V) lower edge, slit along its top
      const sy = -h * 0.5 + ny, sh = h * 0.08;
      const visor = c => S.addRoundPoly(c, [[-w * 0.48 + f * 0.5, sy], [w * 0.47 + f * 0.5, sy], [w * 0.44 + f * 0.4, -h * 0.3], [f, -h * 0.17 + ny * 0.4], [-w * 0.44 + f * 0.4, -h * 0.3]], [6, 6, 8, 5, 8]);
      plate(g, visor, { sd: 5, ld: 2.2 });
      line(g, [[f, sy + sh * 0.9], [f, -h * 0.2 + ny * 0.4]], P.shade, 2.4);
      const slit = c => S.addRoundRect(c, -w * 0.42 + f, sy - sh, w * 0.8, sh, sh / 2);
      flat(g, slit, P.slit);
      if (horror) coldSlit(g, [[-w * 0.38 + f, sy - sh / 2], [w * 0.34 + f, sy - sh / 2]], sh, t);
      rivet(g, -w * 0.43, sy + sh * 0.6, 4.2); rivet(g, w * 0.45, sy + sh * 0.6, 3.6);
    }
    // the 404 knight's scratch: one jagged gash on the left of the helm
    if (o.variant === 'k404') {
      const sx = -w * 0.3, syy = -h * 0.82;
      const pts = [[sx - 10, syy - 4], [sx - 2, syy + 10], [sx - 8, syy + 16], [sx + 6, syy + 34], [sx + 2, syy + 40], [sx + 12, syy + 54]];
      S.strip(g, pts.map(p => [p[0] + 1.5 * LX, p[1] + 1.5]), u => 5.2 * Math.sin(Math.PI * clamp(u * 0.9 + 0.05)) ** 0.6, P.light);
      S.strip(g, pts, u => 4.2 * Math.sin(Math.PI * clamp(u * 0.9 + 0.05)) ** 0.6, '#2A2C31');
    }
  }
  // horror: a single cold line of light inside the slit (the glow is added after the group, see emissive())
  function coldSlit(g, pts, sh) {
    S.strip(g, pts, u => sh * 0.34 * (0.4 + 0.6 * Math.sin(Math.PI * u) ** 0.4), P.slitLight || '#E2FFFA');
  }

  // ------------------------------------------------------------------------------------------------ props
  function drawHammer(g, p0, a, o = {}) { // p0 = pommel end, a = direction pommel -> head
    const L = o.len || 250;
    const p1 = polar(p0, a, L);
    const hw = 15;
    // haft
    plate(g, capPath(p0, p1, hw, hw), { base: P.wood, shadeCol: P.woodShade, lightCol: P.woodLight, sd: 3, ld: 1.6 });
    // leather grip wraps near the pommel
    for (let i = 0; i < 5; i++) {
      const c = polar(p0, a, 22 + i * 10);
      g.save(); g.translate(c[0], c[1]); g.rotate(a);
      S.roundRect(g, -3.5, -hw * 0.62, 7, hw * 1.24, 2.5, P.leather);
      g.fillStyle = P.leatherShade; g.fillRect(1.5, -hw * 0.62, 2, hw * 1.24);
      g.restore();
    }
    // langets (metal strips) under the head
    g.save(); g.translate(p1[0], p1[1]); g.rotate(a);
    plate(g, c => S.addRoundRect(c, -76, -hw * 0.6, 50, hw * 1.2, 4), { sd: 2, ld: 1.5 });
    rivet(g, -62, 0, 2.8); rivet(g, -42, 0, 2.8);
    // the head: a big block across the haft, banded faces
    const hl = 66, hh = 124;
    const head = c => S.addRoundRect(c, -hl * 0.55, -hh / 2, hl, hh, 12);
    plate(g, head, { sd: 8, ld: 3 });
    // striking faces (end caps)
    plate(g, c => S.addRoundRect(c, -hl * 0.62, -hh / 2 - 6, hl * 1.14, 18, 7), { base: P.shade, shadeCol: P.deep, lightCol: P.plate, sd: 4, ld: 2 });
    plate(g, c => S.addRoundRect(c, -hl * 0.62, hh / 2 - 12, hl * 1.14, 18, 7), { base: P.shade, shadeCol: P.deep, lightCol: P.plate, sd: 4, ld: 2 });
    // collar
    flat(g, c => S.addRoundRect(c, -hl * 0.55 - 4, -10, hl + 8, 20, 6), P.shade);
    flat(g, c => S.addRoundRect(c, -hl * 0.55 - 4, -10, hl + 8, 4, 2), P.light);
    rivet(g, -hl * 0.05, 0, 3.6);
    g.restore();
    // pommel knob
    plate(g, c => c.arc(p0[0], p0[1], 11, 0, TAU), { sd: 3, ld: 2 });
    return { p0, p1 };
  }

  function drawSpear(g, p0, a, o = {}) { // p0 = butt end, a = direction butt -> tip
    const L = o.len || 540, t = o.t || 0;
    const p1 = polar(p0, a, L);
    const sw = 10;
    plate(g, capPath(p0, polar(p0, a, L - 70), sw, sw), { base: P.wood, shadeCol: P.woodShade, lightCol: P.woodLight, sd: 2.5, ld: 1.4 });
    // butt ferrule (the "pommel" that knocks)
    plate(g, capPath(p0, polar(p0, a, 22), 14, 12), { sd: 3, ld: 1.6 });
    // grip wrap mid-shaft
    for (let i = 0; i < 4; i++) {
      const c = polar(p0, a, L * 0.42 + i * 9);
      g.save(); g.translate(c[0], c[1]); g.rotate(a); S.roundRect(g, -3, -sw * 0.65, 6, sw * 1.3, 2, P.leather); g.restore();
    }
    // pennon (cloth accent) below the head, flutters with t
    if (o.pennon !== false) {
      const cloth = o.variant === 'horror' ? COL.clothHorror : COL.cloth.spear;
      const b0 = polar(p0, a, L - 92), b1 = polar(p0, a, L - 128);
      const n = [Math.cos(a - Math.PI / 2), Math.sin(a - Math.PI / 2)];
      const back = -LX; // the pennon streams away from the facing direction
      const fl = Math.sin(t * 3.1) * 6;
      const tail = [b0[0] + back * 58, b0[1] + 12 + fl], tail2 = [b0[0] + back * 46, b0[1] + 22 + fl * 0.6];
      g.beginPath(); g.moveTo(b0[0], b0[1]); g.quadraticCurveTo(b0[0] + back * 30, b0[1] + 2 + fl * 0.5, tail[0], tail[1]);
      g.lineTo(tail2[0] - back * 4, tail2[1] - 2); g.lineTo(tail2[0], tail2[1] + 8);
      g.quadraticCurveTo(b1[0] + back * 22, b1[1] + 10 + fl * 0.3, b1[0], b1[1]); g.closePath();
      g.fillStyle = cloth[0]; g.fill();
      g.save(); g.clip(); g.fillStyle = cloth[1]; g.fillRect(Math.min(b0[0], tail[0]) - 80, b1[1] + 12, 300, 60); g.restore();
      void n;
    }
    // socket + lugs + leaf blade
    g.save(); g.translate(p1[0], p1[1]); g.rotate(a);
    plate(g, c => S.addRoundRect(c, -96, -sw * 0.75, 30, sw * 1.5, 4), { sd: 2, ld: 1.4 });
    plate(g, c => { c.moveTo(-74, -3); c.lineTo(-66, -15); c.lineTo(-60, -3); c.lineTo(-60, 3); c.lineTo(-66, 15); c.lineTo(-74, 3); c.closePath(); }, { sd: 2, ld: 1.2 });
    const blade = c => { c.moveTo(-66, -4); c.bezierCurveTo(-48, -17, -16, -14, 0, 0); c.bezierCurveTo(-16, 14, -48, 17, -66, 4); c.closePath(); };
    plate(g, blade, { base: P.light, shadeCol: P.plate, lightCol: '#D5D9DF', sd: 4, ld: 1.6 });
    line(g, [[-62, 0], [-6, 0]], P.plate, 1.6);
    g.restore();
    return { p0, p1 };
  }

  function shieldPath(w, h) {
    return c => {
      c.moveTo(-w / 2 + 10, -h / 2);
      c.lineTo(w / 2 - 10, -h / 2);
      c.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + 10);
      c.lineTo(w / 2, -h * 0.08);
      c.bezierCurveTo(w / 2, h * 0.22, w * 0.2, h * 0.42, 0, h / 2);
      c.bezierCurveTo(-w * 0.2, h * 0.42, -w / 2, h * 0.22, -w / 2, -h * 0.08);
      c.lineTo(-w / 2, -h / 2 + 10);
      c.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + 10, -h / 2);
      c.closePath();
    };
  }
  function drawShield(g, c, r, o = {}) { // heater shield, face toward the viewer. c = centre, r = rotation
    const w = o.w || 132, h = o.h || 164;
    g.save(); g.translate(c[0], c[1]); g.rotate(r);
    plate(g, shieldPath(w, h), { sd: 9, ld: 3 });
    // painted field inside the iron rim
    const field = shieldPath(w - 22, h - 24);
    g.save(); g.translate(0, -1);
    const fc = o.variant === 'horror' ? ['#232428', '#1A1B1E'] : COL.shieldField;
    S.cel(g, field, fc[0], fc[1], 7 * LX, 7);
    // key emblem (treasure hunters), bone paint
    if (o.variant !== 'horror') {
      g.save(); g.scale(LX, 1); // emblem never mirrors
      const em = COL.emblem;
      const key = k => {
        k.moveTo(0, -h * 0.25 + 20); k.arc(0, -h * 0.25, 20, Math.PI / 2, Math.PI / 2 + TAU);
        S.addRoundRect(k, -6, -h * 0.25 + 12, 12, h * 0.48, 4);
        S.addRoundRect(k, 0, h * 0.12, 22, 9, 3);
        S.addRoundRect(k, 0, h * 0.02, 16, 9, 3);
      };
      S.cel(g, key, em[0], em[1], 3, 3);
      S.circle(g, 0, -h * 0.25, 8.5, fc[0]);
      g.restore();
    }
    g.restore();
    // rim rivets
    for (const [x, y] of [[-w * 0.4, -h * 0.43], [w * 0.4, -h * 0.43], [-w * 0.44, h * 0.02], [w * 0.44, h * 0.02], [0, h * 0.44]]) rivet(g, x, y, 3.6);
    g.restore();
  }

  function drawLantern(g, hand, swing, o = {}) { // hangs from the hand; swing = angle of the hang (0 = straight down)
    const lit = o.lit !== false;
    g.save(); g.translate(hand[0], hand[1]); g.rotate(swing);
    // bail (wire handle)
    g.strokeStyle = P.deep; g.lineWidth = 3.5; g.beginPath(); g.arc(0, 12, 12, Math.PI * 1.05, Math.PI * 1.95, false); g.stroke();
    line(g, [[-11, 14], [-13, 22]], P.deep, 3); line(g, [[11, 14], [13, 22]], P.deep, 3);
    // cap
    plate(g, c => { c.moveTo(-6, 16); c.lineTo(6, 16); c.lineTo(19, 30); c.lineTo(-19, 30); c.closePath(); }, { sd: 3, ld: 1.5 });
    S.circle(g, 0, 15, 4, P.plate);
    // glass body
    const glass = c => S.addRoundRect(c, -15, 30, 30, 36, 5);
    if (lit) {
      S.cel(g, glass, COL.glass, COL.glassShade, 4 * LX, 3);
      S.ellipse(g, 0, 52, 6, 10, 0, COL.flame[1]); S.ellipse(g, 0, 54, 3.4, 6, 0, COL.flame[0]);
    } else S.cel(g, glass, '#3A3530', '#2A2622', 4 * LX, 3);
    // cage bars
    for (const x of [-15, -5, 5, 15]) flat(g, c => c.rect(x - 2, 30, 4, 36), P.shade);
    // base
    plate(g, c => S.addRoundRect(c, -19, 64, 38, 9, 3), { sd: 2.5, ld: 1.4 });
    plate(g, c => S.addRoundRect(c, -12, 72, 24, 6, 2), { sd: 2, ld: 1 });
    g.restore();
    return polar(hand, swing + Math.PI / 2, 50); // glass centre (for light)
  }

  function drawNotebook(g, c, r, o = {}) { // closed or held: cover toward the viewer. c = centre
    const w = o.w || 50, h = o.h || 64;
    g.save(); g.translate(c[0], c[1]); g.rotate(r);
    // page block edge
    flat(g, k => S.addRoundRect(k, -w / 2 + 4, -h / 2 - 3, w, h, 4), COL.paper);
    for (let i = 0; i < 3; i++) flat(g, k => k.rect(-w / 2 + 6, -h / 2 - 1 + i * 2.2, w - 6, 0.9), COL.paperLine);
    S.cel(g, k => S.addRoundRect(k, -w / 2, -h / 2, w, h, [3, 6, 6, 3]), COL.book, COL.bookShade, 4 * LX, 4);
    // spine
    flat(g, k => k.rect(-w / 2, -h / 2, 6, h), COL.bookShade);
    // strap
    flat(g, k => k.rect(w * 0.28, -h / 2, 5, h), P.leather);
    // label plate (never mirrored)
    g.save(); g.scale(LX, 1);
    S.roundRect(g, -w * 0.36, -h * 0.34, w * 0.62, h * 0.5, 3, COL.bookLabel);
    S.label(g, 'PROTOCOL', -w * 0.05, -h * 0.22, Math.max(5, w * 0.11), { color: COL.ink, weight: 900 });
    S.label(g, '404', -w * 0.05, -h * 0.02, w * 0.27, { color: '#8E1F2E', weight: 900 });
    g.restore();
    g.restore();
  }

  function drawQuill(g, p, a, o = {}) { // p = nib point, a = direction nib -> feather end
    const L = o.len || 58;
    const e = polar(p, a, L);
    const n = [Math.cos(a + Math.PI / 2), Math.sin(a + Math.PI / 2)];
    // vane
    const v0 = polar(p, a, L * 0.3);
    g.beginPath(); g.moveTo(v0[0], v0[1]);
    const m1 = polar(p, a, L * 0.65), m2 = polar(p, a, L * 0.6);
    g.quadraticCurveTo(m1[0] + n[0] * 10, m1[1] + n[1] * 10, e[0], e[1]);
    g.quadraticCurveTo(m2[0] - n[0] * 7, m2[1] - n[1] * 7, v0[0], v0[1]); g.closePath();
    g.fillStyle = COL.quill; g.fill();
    g.save(); g.clip(); g.translate(-n[0] * 4, -n[1] * 4); g.fillStyle = COL.quillShade; g.beginPath(); g.moveTo(v0[0], v0[1]); g.quadraticCurveTo(m2[0] - n[0] * 7, m2[1] - n[1] * 7, e[0], e[1]); g.lineTo(e[0] - n[0] * 20, e[1] - n[1] * 20); g.lineTo(v0[0] - n[0] * 20, v0[1] - n[1] * 20); g.closePath(); g.fill(); g.restore();
    // shaft + nib
    line(g, [p, e], COL.quillShade, 1.6);
    line(g, [p, polar(p, a, 9)], COL.ink, 2.6);
  }

  // ------------------------------------------------------------------------------------------------ hands
  // hand frame: origin = wrist, +x = toward the knuckles. side = +1/-1 which side the thumb shows on.
  function drawHand(g, wr, a, T, shape = 'fist', side = 1) {
    const f = T.fist;
    g.save(); g.translate(wr[0], wr[1]); g.rotate(a);
    // flared cuff (toward the elbow)
    plate(g, c => S.addRoundPoly(c, [[-f * 1.05, -f * 0.98], [f * 0.18, -f * 0.74], [f * 0.18, f * 0.74], [-f * 1.05, f * 0.98]], [f * 0.3, 3, 3, f * 0.3]), { sd: 3.5, ld: 1.8 });
    flat(g, c => c.rect(-f * 0.25, -f * 0.8, f * 0.16, f * 1.6), P.shade);
    if (shape === 'open') {
      plate(g, c => S.addRoundRect(c, f * 0.05, -f * 0.68, f * 0.95, f * 1.36, f * 0.4), { sd: 3, ld: 1.6 });
      for (let i = -1; i <= 1; i++) {
        const fa = i * 0.2, b = [f * 0.86, i * f * 0.46], tip = polar(b, fa, f * 0.95);
        plate(g, capPath(b, tip, f * 0.46, f * 0.42), { sd: 2.5, ld: 1.4 });
        const mid = lp(b, tip, 0.5);
        g.save(); g.translate(mid[0], mid[1]); g.rotate(fa); flat(g, c => c.rect(-1, -f * 0.2, 2, f * 0.4), P.shade); g.restore();
      }
      plate(g, capPath([f * 0.35, side * f * 0.55], [f * 0.8, side * f * 1.15], f * 0.44, f * 0.38), { sd: 2.5, ld: 1.4 });
    } else if (shape === 'point') {
      plate(g, c => S.addRoundRect(c, f * 0.05, -f * 0.7, f * 1.3, f * 1.4, f * 0.55), { sd: 3, ld: 1.6 });
      plate(g, capPath([f * 1.1, -side * f * 0.4], [f * 2.1, -side * f * 0.45], f * 0.42, f * 0.38), { sd: 2.5, ld: 1.4 });
    } else { // fist / grip / knock
      plate(g, c => S.addRoundRect(c, f * 0.02, -f * 0.74, f * 1.42, f * 1.48, f * 0.56), { sd: 3.5, ld: 1.8 });
      // knuckle plate
      plate(g, c => S.addRoundRect(c, f * 0.72, -f * 0.7, f * 0.4, f * 1.4, f * 0.18), { sd: 2, ld: 1.4 });
      // finger lines
      for (const yy of [-0.24, 0.24]) flat(g, c => c.rect(f * 1.12, yy * f - 0.9, f * 0.3, 1.8), P.shade);
      // thumb
      plate(g, capPath([f * 0.3, side * f * 0.62], [f * 0.95, side * f * 0.72], f * 0.48, f * 0.42), { sd: 2.5, ld: 1.4 });
    }
    g.restore();
  }

  // ------------------------------------------------------------------------------------------------ body parts
  function drawLeg(g, R, T, L) {
    const hip = L.hip, knee = L.knee, ank = L.ank;
    // under-mail
    plate(g, c => S.addLimb(c, [hip, knee, ank], [T.legW * 0.82, T.legW * 0.7, T.legW * 0.55]), { base: P.mail, shadeCol: P.mailShade, sd: 4, light: false });
    // greave (shin)
    plate(g, capPath(knee, ank, T.legW * 0.84, T.legW * 0.66), { sd: 5, ld: 2 });
    // cuisse (thigh)
    plate(g, capPath(hip, lp(hip, knee, 0.92), T.legW, T.legW * 0.86), { sd: 6, ld: 2.4 });
    // sabaton (pointed toe), along the ground
    const fa = L.toe || 0;
    g.save(); g.translate(ank[0], ank[1]); g.rotate(fa);
    const fl = T.foot, fh = T.footH;
    const shoe = c => { c.moveTo(-fl * 0.32, -fh * 0.55); c.quadraticCurveTo(fl * 0.2, -fh * 0.8, fl * 0.5, -fh * 0.25); c.quadraticCurveTo(fl * 0.68, -fh * 0.1, fl * 0.74, fh * 0.42); c.quadraticCurveTo(fl * 0.3, fh * 0.62, -fl * 0.3, fh * 0.58); c.quadraticCurveTo(-fl * 0.42, fh * 0.1, -fl * 0.32, -fh * 0.55); c.closePath(); };
    plate(g, shoe, { sd: 5, ld: 2 });
    // lames across the instep
    for (let i = 0; i < 3; i++) { const x = fl * (0.02 + i * 0.13); line(g, [[x, -fh * 0.55 + i * 3], [x + fl * 0.06, fh * 0.5]], P.shade, 2); }
    g.restore();
    // poleyn (knee cop) with a fan wing on the outer side
    const ka = ang(hip, knee);
    g.save(); g.translate(knee[0], knee[1]); g.rotate(ka - Math.PI / 2);
    const r = T.legW * 0.47;
    plate(g, c => c.ellipse(r * 0.75, 0, r * 0.62, r * 0.85, 0, 0, TAU), { sd: 3, ld: 1.6 });
    plate(g, c => c.arc(0, 0, r, 0, TAU), { sd: 4, ld: 2 });
    rivet(g, 0, 0, r * 0.2);
    g.restore();
  }

  function drawArm(g, R, T, A, part) {
    const sh = A.sh, el = A.el, wr = A.wr;
    if (part !== 'hand') {
      // rerebrace
      plate(g, capPath(sh, lp(sh, el, 0.9), T.armW, T.armW * 0.86), { sd: 5, ld: 2 });
      // vambrace
      plate(g, capPath(lp(el, wr, 0.1), wr, T.armW * 0.86, T.armW * 0.74), { sd: 4.5, ld: 2 });
      // couter with fan
      const ea = ang(sh, el);
      g.save(); g.translate(el[0], el[1]); g.rotate(ea);
      const r = T.armW * 0.5;
      plate(g, c => c.arc(0, 0, r * 0.86, 0, TAU), { sd: 3.5, ld: 1.8 });
      rivet(g, 0, 0, r * 0.18);
      g.restore();
    }
    if (part !== 'arm') drawHand(g, wr, A.handAng, T, A.shape, A.thumb);
  }

  function drawPauldron(g, R, T, A, near) {
    const sh = A.sh, r = T.paulR * (near ? 1 : 0.9);
    const ua = ang(sh, A.el) - Math.PI / 2; // 0 = arm hanging straight down
    const pa = clamp(ua * 0.5, -1.1, 1.1);
    g.save(); g.translate(sh[0], sh[1]); g.rotate(pa);
    const ox = near ? -r * 0.1 : r * 0.08;
    // two lames under the cap (lowest first): curved bands hugging the arm
    const band = (y0, ww, hh) => c => { c.moveTo(ox - ww, y0); c.quadraticCurveTo(ox, y0 + r * 0.26, ox + ww, y0); c.lineTo(ox + ww * 0.94, y0 + hh); c.quadraticCurveTo(ox, y0 + hh + r * 0.28, ox - ww * 0.94, y0 + hh); c.closePath(); };
    plate(g, band(r * 0.5, r * 0.84, r * 0.3), { sd: 3, ld: 1.8 });
    plate(g, band(r * 0.22, r * 0.96, r * 0.32), { sd: 3, ld: 1.8 });
    // the cap: a rounded dome over the shoulder
    const cap = c => { c.moveTo(ox - r * 1.06, r * 0.24); c.ellipse(ox, r * 0.24, r * 1.06, r * 0.98, 0, Math.PI, TAU); c.quadraticCurveTo(ox, r * 0.56, ox - r * 1.06, r * 0.24); c.closePath(); };
    plate(g, cap, { sd: 6, ld: 2.8 });
    // raised edge line + rivet
    line(g, [[ox - r * 0.86, r * 0.22], [ox, r * 0.38], [ox + r * 0.86, r * 0.22]], P.shade, 2.2, 0.5);
    rivet(g, ox + (near ? -r * 0.42 : r * 0.42), -r * 0.24, 3.4);
    g.restore();
  }

  function torsoXf(g, R) { g.translate(R.hipP[0], R.hipP[1]); g.rotate(R.lean); }

  function drawTorso(g, R, T, o) {
    const tw = T.torso, ww = T.waistW, cw = T.chestW, fx = 0.12 * cw; // ridge shift toward the face
    g.save(); torsoXf(g, R);
    // faulds (skirt of lames) + tassets
    const fy0 = -26, fy1 = 26;
    const fauld = c => S.addRoundPoly(c, [[-ww * 0.54, fy0], [ww * 0.54, fy0], [ww * 0.64, fy1], [-ww * 0.64, fy1]], [6, 6, 8, 8]);
    plate(g, fauld, { sd: 5, ld: 2 });
    for (let i = 1; i <= 2; i++) { const y = fy0 + i * (fy1 - fy0) / 3; line(g, [[-ww * 0.6, y], [ww * 0.6, y]], P.shade, 2.2); }
    for (const sd of [-1, 1]) { // tassets hang over each thigh
      const tx = sd * ww * 0.3 + (sd > 0 ? 4 : 0), rr = R.tasset[sd > 0 ? 1 : 0];
      g.save(); g.translate(tx, fy1 - 6); g.rotate(rr);
      const tw2 = ww * (sd < 0 ? 0.5 : 0.44);
      plate(g, c => S.addRoundPoly(c, [[-tw2 / 2, 0], [tw2 / 2, 0], [tw2 / 2 + 3, 30], [0, 36], [-tw2 / 2 - 3, 30]], [4, 4, 8, 6, 8]), { sd: 4, ld: 2 });
      line(g, [[-tw2 / 2 + 2, 13], [tw2 / 2 - 2, 13]], P.shade, 2);
      g.restore();
    }
    // breastplate
    const by0 = -24, ty = -tw + 16;
    const breast = c => S.addRoundPoly(c, [
      [-ww * 0.5, by0], [ww * 0.5, by0],
      [cw * 0.5, -tw * 0.58], [cw * 0.42, ty], [cw * 0.2, ty - 12], [-cw * 0.2, ty - 12], [-cw * 0.42, ty], [-cw * 0.5, -tw * 0.58],
    ], [8, 8, cw * 0.3, 18, 10, 10, 18, cw * 0.3]);
    plate(g, breast, { sd: 9, ld: 3 });
    g.save(); g.beginPath(); breast(g); g.clip();
    // gothic fluting: fan of lines from the waist
    for (let i = -2; i <= 2; i++) {
      if (i === 0) continue;
      const x0 = fx * 0.6 + i * ww * 0.13, x1 = fx + i * cw * 0.2;
      line(g, [[x0, by0 - 6], [x1, -tw * 0.72]], P.shade, 2.2, 0);
      line(g, [[x0 - 2.5 * LX, by0 - 6], [x1 - 2.5 * LX, -tw * 0.72]], P.light, 1.4, 0);
    }
    // medial ridge
    line(g, [[fx * 0.55, by0], [fx, -tw * 0.6], [fx * 0.9, ty - 8]], P.light, 3, 0.5);
    line(g, [[fx * 0.55 + 3, by0], [fx + 3, -tw * 0.6], [fx * 0.9 + 3, ty - 8]], P.shade, 2, 0.5);
    g.restore();
    // plackart (ogee point up the belly)
    const pk = c => { c.moveTo(-ww * 0.46, by0 + 2); c.lineTo(ww * 0.46, by0 + 2); c.bezierCurveTo(ww * 0.46, -tw * 0.22, fx * 0.7 + 10, -tw * 0.32, fx * 0.7, -tw * 0.47); c.bezierCurveTo(fx * 0.7 - 10, -tw * 0.32, -ww * 0.46, -tw * 0.22, -ww * 0.46, by0 + 2); c.closePath(); };
    plate(g, pk, { sd: 5, ld: 2.2 });
    rivet(g, fx * 0.7, -tw * 0.42, 3);
    // gorget (collar lames under the helm)
    const gw = T.helmW * 0.42;
    plate(g, c => S.addRoundRect(c, -gw, -tw - 2, gw * 2, 22, 9), { sd: 4, ld: 2 });
    plate(g, c => S.addRoundRect(c, -gw * 1.12, -tw + 14, gw * 2.24, 14, 7), { sd: 3, ld: 1.8 });
    // belt
    const accent = P.accent;
    flat(g, c => S.addRoundRect(c, -ww * 0.56, by0 - 4, ww * 1.12, 13, 4), accent || P.leather);
    flat(g, c => S.addRoundRect(c, -ww * 0.56, by0 + 5, ww * 1.12, 4, 2), accent ? C.shade(accent, -0.3) : P.leatherShade);
    plate(g, c => S.addRoundRect(c, fx * 0.55 - 9, by0 - 6, 18, 17, 4), { base: P.brass, shadeCol: P.brassShade, sd: 2.5, ld: 1.4, lightCol: C.shade(P.brass, 0.3) });
    flat(g, c => S.addRoundRect(c, fx * 0.55 - 4.5, by0 - 1.5, 9, 8, 2), accent || P.leather);
    g.restore();
  }

  function drawSash(g, R, T, t) { // hammer knight: rust sash knotted on the near hip, tails flutter
    const cloth = R.variant === 'horror' ? COL.clothHorror : COL.cloth.hammer;
    g.save(); torsoXf(g, R);
    const ww = T.waistW, y = -22;
    flat(g, c => { c.moveTo(-ww * 0.6, y - 10); c.quadraticCurveTo(0, y - 2, ww * 0.6, y - 12); c.lineTo(ww * 0.62, y + 6); c.quadraticCurveTo(0, y + 14, -ww * 0.62, y + 8); c.closePath(); }, cloth[0]);
    flat(g, c => { c.moveTo(-ww * 0.62, y + 3); c.quadraticCurveTo(0, y + 10, ww * 0.62, y + 1); c.lineTo(ww * 0.62, y + 6); c.quadraticCurveTo(0, y + 14, -ww * 0.62, y + 8); c.closePath(); }, cloth[1]);
    // knot + tails on the near hip
    const kx = -ww * 0.5, sw = Math.sin(t * 2.4) * 4 + R.sashSwing * 22;
    S.strip(g, [[kx, y], [kx - 8, y + 26], [kx - 6 + sw * 0.5, y + 52], [kx - 12 + sw, y + 74]], u => 15 * (1 - u * 0.45), cloth[1]);
    S.strip(g, [[kx + 4, y], [kx + 8, y + 24], [kx + 4 + sw * 0.4, y + 46], [kx + 10 + sw * 0.8, y + 62]], u => 13 * (1 - u * 0.4), cloth[0]);
    S.ellipse(g, kx, y + 1, 11, 9, 0.2, cloth[0]);
    S.ellipse(g, kx + 2 * LX, y + 3, 6, 5, 0.2, cloth[1]);
    g.restore();
  }

  function drawCape(g, R, T, t) { // spear knight: short olive half-cape behind the near shoulder
    const cloth = R.variant === 'horror' ? COL.clothHorror : COL.cloth.spear;
    g.save(); torsoXf(g, R);
    const tw = T.torso, sw = Math.sin(t * 1.7) * 4 + R.capeSwing * 26;
    const top = [-T.shX * 0.2, -tw + 14];
    const path = c => {
      c.moveTo(top[0] + 26, top[1]);
      c.quadraticCurveTo(-T.shX - 30, top[1] - 4, -T.shX - 34 + sw * 0.3, -tw * 0.45);
      c.lineTo(-T.shX - 30 + sw, -tw * 0.18);
      c.lineTo(-T.shX - 12 + sw * 0.8, -tw * 0.24);
      c.lineTo(-T.shX - 6 + sw * 0.7, -tw * 0.12);
      c.lineTo(-T.shX + 14 + sw * 0.5, -tw * 0.22);
      c.quadraticCurveTo(-4, -tw * 0.5, top[0] + 26, top[1]);
      c.closePath();
    };
    S.cel(g, path, cloth[0], cloth[1], 7 * LX, 7);
    g.restore();
  }

  function drawBeltKit(g, R, T, o) { // k404: notebook + quill on the near hip
    g.save(); torsoXf(g, R);
    const ww = T.waistW, y = -8;
    drawQuill(g, [-ww * 0.4, y + 22], -Math.PI / 2 - 0.35, { len: 54 });
    drawNotebook(g, [-ww * 0.52, y + 10], 0.08, { w: 34, h: 44 });
    g.restore();
  }

  // ------------------------------------------------------------------------------------------------ pose solver
  const POSES = ['idle', 'walk', 'ready', 'knock', 'notebook', 'backaway', 'nod', 'peek'];

  function solve(T, o) {
    const type = T.name, t = o.t || 0, pose = o.pose || 'idle';
    const R = {
      type, variant: o.variant || 'normal', pose, spearLen: o.spearLen || 540,
      hipX: 0, hipY: T.hip, lean: 0, tilt: 0, nod: 0, helmDX: 0, helmDY: 0,
      feet: { near: { p: [-T.stance, -T.ankle], toe: 0 }, far: { p: [T.stance * 0.9, -T.ankle], toe: 0 } },
      arms: { near: null, far: null },
      props: [], fx: { sweat: 0, lines: 0, impact: 0, impactAt: null },
      tasset: [0, 0], sashSwing: 0, capeSwing: 0, lanternSwing: 0, lantern: null,
    };
    const breath = Math.sin(t * TAU * 0.45);
    R.hipY += breath * 1.2;
    const sh = side => { // shoulder in ground space for the current hip / lean (call after setting them)
      const p = side === 'near' ? [-T.shX, -T.torso + T.shDrop] : [T.shX * 0.8, -T.torso + T.shDrop];
      return add([R.hipX, -R.hipY], rot(p, R.lean));
    };
    const torsoPt = p => add([R.hipX, -R.hipY], rot(p, R.lean));
    const arm = (side, wr, o2 = {}) => Object.assign({ wr, bend: side === 'near' ? -1 : -1, shape: 'fist', handAng: null, z: side === 'near' ? 'front' : 'back', thumb: side === 'near' ? -1 : 1 }, o2);
    const hang = (side, dx = 0, dy = 0) => { const s0 = sh(side); return arm(side, [s0[0] + (side === 'near' ? -10 : 8) + dx, s0[1] + T.armU + T.armL - 10 + dy], { handAng: Math.PI / 2 + (side === 'near' ? 0.12 : -0.12) }); };

    if (pose === 'walk' || pose === 'backaway') {
      const ph = pose === 'walk' ? (o.phase ?? 0) : (o.k ?? 0.3);
      const A = pose === 'walk' ? T.strideA : T.strideA * 0.7;
      const leg = u => {
        u = frac(u);
        if (u < 0.5) return { x: A - 4 * A * u, y: 0, toe: 0 };
        const k = (u - 0.5) * 2, ek = E.easeInOutSine(k);
        return { x: -A + 2 * A * ek, y: -T.lift * Math.sin(Math.PI * k), toe: -0.22 * Math.sin(Math.PI * k) + 0.12 * Math.sin(TAU * k) };
      };
      const dirm = pose === 'walk' ? 1 : -1; // backaway: the cycle runs backwards (feet move toward the facing)
      const ln = leg(dirm > 0 ? ph : 1 - ph), lf = leg(dirm > 0 ? ph + 0.5 : 0.5 - ph);
      const lane = T.legX * (pose === 'walk' ? 0.45 : 0.9); // walking feet track closer to the centre line
      R.feet.near.p = [-lane + ln.x, -T.ankle + ln.y]; R.feet.near.toe = ln.toe;
      R.feet.far.p = [lane + lf.x, -T.ankle + lf.y]; R.feet.far.toe = lf.toe;
      const bob = (1 - Math.cos(4 * Math.PI * ph)) / 2;
      R.hipY = T.hip - 7 + bob * 6;
      R.lean = 0.05 + 0.015 * Math.sin(4 * Math.PI * ph);
      R.tilt = 0.03 * Math.sin(TAU * ph);
      R.tasset = [ln.x / A * -0.12, lf.x / A * -0.12];
      const swing = Math.sin(TAU * ph); // + when the near foot is going back
      R.sashSwing = -Math.cos(TAU * ph) * 0.4; R.capeSwing = -0.4 - 0.2 * Math.sin(4 * Math.PI * ph);
      if (pose === 'backaway') {
        R.hipY = T.hip - 16 + bob * 4; R.hipX = -12; R.lean = -0.2; R.tilt = -0.2;
        R.fx.sweat = 2; R.fx.lines = 1;
        R.nod = 0;
      }
      const sw = pose === 'walk' ? swing : 0;
      if (type === 'hammer') {
        if (pose === 'walk') {
          // maul over the near shoulder: near hand on the haft in front of the chest, head behind the back
          const hand = torsoPt([T.shX * 0.15, -T.torso * 0.5]);
          const a = -Math.PI * 0.73;
          R.arms.near = arm('near', hand, { handAng: a + Math.PI, bend: 1, handZ: 'top' });
          R.props.push({ kind: 'hammer', p0: polar(hand, a, -34), a, z: 9.5 });
          R.arms.far = hang('far', 10 * sw, 0); R.arms.far.wr = add(R.arms.far.wr, [14 * sw, 0]);
        } else {
          // backaway: maul held up across the body as a barrier, both hands
          const hn = torsoPt([-T.shX * 0.2, -T.torso * 0.55]), hf = torsoPt([T.shX * 1.0, -T.torso * 0.72]);
          const a = ang(hn, hf);
          R.props.push({ kind: 'hammer', p0: polar(hn, a, -30), a, z: 8.5 });
          R.arms.near = arm('near', hn, { handAng: a - Math.PI / 2, bend: 1 });
          R.arms.far = arm('far', hf, { handAng: a - Math.PI / 2, bend: 1, z: 'front' });
        }
      } else if (type === 'spear') {
        if (pose === 'walk') {
          const hand = add(sh('near'), [-26, T.armU + 8]);
          const a = -Math.PI / 2 + 0.1;
          R.arms.near = arm('near', hand, { handAng: Math.PI, bend: -1 });
          R.props.push({ kind: 'spear', p0: polar(hand, a, -T.hip * 0.62), a, z: 9.5 });
          R.arms.far = hang('far'); R.arms.far.wr = add(R.arms.far.wr, [14 * sw, -2 * Math.abs(sw)]);
        } else {
          // backaway: spear pointed at the threat, shaky, both hands
          const hn = torsoPt([-T.shX * 0.3, -T.torso * 0.35]), hf = torsoPt([T.shX * 1.6, -T.torso * 0.5]);
          const a = ang(hn, hf) + 0.04 * Math.sin(t * 40);
          R.props.push({ kind: 'spear', p0: polar(hn, a, -150), a, z: 8.5 });
          R.arms.near = arm('near', hn, { handAng: a - Math.PI / 2, bend: 1 });
          R.arms.far = arm('far', hf, { handAng: a - Math.PI / 2, bend: 1, z: 'front' });
        }
      } else { // shield
        if (pose === 'walk') {
          const sc = torsoPt([T.shX * 0.95, -T.torso * 0.3]);
          R.props.push({ kind: 'shield', c: sc, r: 0.04 + 0.02 * sw, z: 8.5 });
          R.arms.far = arm('far', add(sc, [-8, -14]), { z: 'back' });
          const hn = add(sh('near'), [-12 - 16 * sw, T.armU + T.armL - 14]);
          R.arms.near = arm('near', hn, { handAng: Math.PI / 2 + 0.2, bend: -1 });
          R.lanternSwing = 0.3 * sw + 0.05 * Math.sin(t * 3);
          R.lantern = { hand: 'near', z: 9.4 };
        } else {
          const sc = torsoPt([T.shX * 1.25, -T.torso * 0.5]);
          R.props.push({ kind: 'shield', c: sc, r: -0.12, z: 8.5 });
          R.arms.far = arm('far', add(sc, [-10, -10]), { z: 'back' });
          const hn = torsoPt([-T.shX * 1.5, -T.torso * 0.65]);
          R.arms.near = arm('near', hn, { handAng: -Math.PI / 2 - 0.5, bend: 1 });
          R.lanternSwing = 0.25 + 0.08 * Math.sin(t * 9);
          R.lantern = { hand: 'near', z: 9.4 };
        }
      }
    } else if (pose === 'ready') {
      R.feet.near.p = [-T.stance * 1.5, -T.ankle]; R.feet.far.p = [T.stance * 1.5, -T.ankle];
      R.hipY = T.hip - 18;
      if (type === 'hammer') {
        R.lean = -0.1; R.tilt = 0.14;
        const hn = torsoPt([-T.shX * 0.5, -T.torso * 0.9]), a = -Math.PI * 0.6;
        const hf = polar(hn, a, 30);
        R.props.push({ kind: 'hammer', p0: polar(hn, a, -26), a, z: 6.5 });
        R.arms.near = arm('near', hn, { handAng: a + Math.PI / 2, bend: 1 });
        R.arms.far = arm('far', hf, { handAng: a + Math.PI / 2, bend: 1, z: 'front' });
      } else if (type === 'spear') {
        R.lean = 0.1; R.tilt = 0.06; R.feet.near.p = [-T.stance * 2.2, -T.ankle]; R.feet.far.p = [T.stance * 1.9, -T.ankle];
        const hn = torsoPt([-T.shX * 0.4, -T.torso * 0.28]), a = -0.62;
        const hf = polar(hn, a, 92);
        R.props.push({ kind: 'spear', p0: polar(hn, a, -120), a, z: 8.5 });
        R.arms.near = arm('near', hn, { handAng: a + Math.PI / 2, bend: 1 });
        R.arms.far = arm('far', hf, { handAng: a + Math.PI / 2, bend: 1, z: 'front' });
      } else {
        // shield up in front, lantern held high beside the helm: searching
        R.lean = 0.06; R.tilt = 0.16;
        const sc = torsoPt([T.shX * 1.05, -T.torso * 0.36]);
        R.props.push({ kind: 'shield', c: sc, r: -0.06, z: 8.5 });
        R.arms.far = arm('far', add(sc, [-8, -12]), { z: 'back' });
        const hn = add(sh('near'), [-34, -T.armU - T.armL + 16]);
        R.arms.near = arm('near', hn, { handAng: -Math.PI / 2 - 0.1, bend: 1, z: 'front', thumb: 1 });
        R.lanternSwing = 0.12 + 0.05 * Math.sin(t * 2.6);
        R.lantern = { hand: 'near', z: 10.6 }; // raised: it hangs in front of the forearm
      }
    } else if (pose === 'knock') {
      const k = clamp(o.k ?? 0.5);
      const K = o.knockAt || [T.knockDX, -150];
      // timing: 0-0.4 wind-up -> contact at 0.5 (easeIn), rebound to 0.62, then settle and listen (tilt)
      let up; // 0 = at contact, 1 = fully raised
      if (k < 0.5) up = 1 - E.easeInQuad(k / 0.5);
      else if (k < 0.62) up = 0.28 * Math.sin(Math.PI * (k - 0.5) / 0.12);
      else up = 0.12 * E.easeOutCubic((k - 0.62) / 0.38);
      R.fx.impact = k >= 0.48 && k < 0.66 ? 1 - (k - 0.48) / 0.18 : 0;
      R.fx.impactAt = K;
      const listen = E.easeInOutCubic(clamp((k - 0.62) / 0.3));
      R.lean = 0.14 + 0.04 * (1 - up); R.tilt = 0.06 + 0.22 * listen; R.hipY = T.hip - 6;
      R.feet.near.p = [-T.stance * 1.2, -T.ankle]; R.feet.far.p = [T.stance * 1.4, -T.ankle];
      if (type === 'hammer') {
        // choked-up grip in front of the chest; the haft pivots in the hands (a wrist tap) so the maul head's lower
        // face lands on K. The pommel end sticks out behind the knight.
        const hh2 = 62, aC = 0.08, gripToHead = 130, gripToPommel = 120;
        const headC = add(K, [hh2 * Math.sin(aC), -hh2 * Math.cos(aC)]);
        const grip = add(polar(headC, aC + Math.PI, gripToHead), [-6 * up, -24 * up]);
        const a = aC - up * 1.0;
        const p0 = polar(grip, a + Math.PI, gripToPommel);
        const hn = polar(grip, a, -16), hf = polar(grip, a, 20);
        R.props.push({ kind: 'hammer', p0, a, z: 8.5 });
        R.arms.near = arm('near', hn, { handAng: a + Math.PI / 2, bend: 1 });
        R.arms.far = arm('far', hf, { handAng: a + Math.PI / 2, bend: 1, z: 'front' });
      } else if (type === 'spear') {
        // reversed spear: the butt ferrule taps the lid; the shaft slides along its axis
        const a = Math.PI + 0.62; // butt -> tip points up-back
        const p0 = polar(K, a, up * 46 - 2);
        const hn = polar(p0, a, 130), hf = polar(p0, a, 60);
        R.props.push({ kind: 'spear', p0, a, z: 8.5 });
        R.arms.near = arm('near', hn, { handAng: a - Math.PI / 2, bend: 1 });
        R.arms.far = arm('far', hf, { handAng: a - Math.PI / 2, bend: 1, z: 'front' });
      } else {
        // knuckles: fist comes down onto the lid; the lantern waits on the floor
        const fist = add(K, [-T.fist * 0.4, -T.fist * 1.1 - up * 52]);
        R.arms.near = arm('near', fist, { handAng: Math.PI / 2 - 0.25 + up * 0.5, bend: 1, shape: 'fist', z: 'front' });
        const sc = torsoPt([T.shX * 0.6, -T.torso * 0.2]);
        R.props.push({ kind: 'shield', c: add(sc, [-6, 30]), r: 0.1, z: 1.5 });
        R.arms.far = arm('far', add(sc, [-14, 6]), { z: 'back' });
        R.props.push({ kind: 'lanternFloor', p: [-T.stance * 2.6, 0], z: 3.5 });
      }
    } else if (pose === 'notebook') {
      // the notebook held up in front of the chest (cover toward us), quill scribbling over its top edge
      R.tilt = 0.24; R.nod = 0.6; R.lean = 0.06;
      const nb = torsoPt([T.shX * 0.7 + 36, -T.torso * 0.6]);
      R.props.push({ kind: 'notebookHeld', c: nb, r: -0.08, z: 8.6 });
      R.arms.far = arm('far', add(nb, [30, 22]), { handAng: -Math.PI / 2 + 0.3, bend: 1, shape: 'fist', z: 'back', thumb: -1 });
      const wq = 0.5 + 0.5 * Math.sin(t * 9), wq2 = Math.sin(t * 23) * 2;
      const pen = add(nb, [-16 + wq * 22, -42 + wq2]);
      R.arms.near = arm('near', add(pen, [-8, -22]), { handAng: 0.9, bend: 1, shape: 'fist', z: 'front' });
      R.props.push({ kind: 'quillHeld', p: pen, a: -Math.PI * 0.6, z: 10.5 });
      if (type === 'hammer') { const head = [-T.stance * 3.1, -36], p0 = polar(head, -Math.PI / 2 + 0.38, 250); R.props.push({ kind: 'hammer', p0, a: ang(p0, head), z: 4.5 }); }
      if (type === 'spear') R.props.push({ kind: 'spear', p0: [-T.stance * 2.4, -2], a: -Math.PI / 2 + 0.16, z: 0.5 });
      if (type === 'shield') R.props.push({ kind: 'shield', c: torsoPt([-T.shX * 0.55, -T.torso * 0.62]), r: -0.18, z: 0.5 });
      R.noBeltKit = true;
    } else if (pose === 'peek') {
      // handled in drawPeek
    } else { // idle / nod
      let nodK = 0;
      if (pose === 'nod') { nodK = Math.sin(Math.PI * clamp(o.k ?? 0.5)); R.nod = nodK; R.lean = 0.05 * nodK; R.hipY -= 2 * nodK; }
      if (type === 'hammer') {
        // maul stood on its head in front, both gauntlets on the haft (guard pose), pommel up under the helm
        const head = [72, -64], a = Math.PI / 2 - 0.24; // pommel -> head direction (pommel leans toward the body)
        const p0 = polar(head, a + Math.PI, 250);
        R.props.push({ kind: 'hammer', p0, a, z: 8.5 });
        R.arms.far = arm('far', polar(p0, a, 100 + breath), { handAng: Math.PI + 0.1, bend: 1, z: 'front', thumb: -1 });
        R.arms.near = arm('near', polar(p0, a, 60 + breath), { handAng: Math.PI + 0.05, bend: 1, thumb: -1 });
      } else if (type === 'spear') {
        const hand = add(sh('near'), [-34, T.armU + 6]);
        R.arms.near = arm('near', hand, { handAng: Math.PI, bend: -1 });
        R.props.push({ kind: 'spear', p0: [hand[0] - 2, -2], a: -Math.PI / 2 + 0.015, z: 9.5 });
        R.arms.far = hang('far');
      } else {
        // shield stands on its point at the far side, gauntlet on its top; lantern hangs from the near hand
        const sc = [T.shX + 38, -84];
        R.props.push({ kind: 'shield', c: sc, r: 0.06, z: 8.5 });
        R.arms.far = arm('far', add(sc, [-14, -72]), { handAng: 0.2, bend: 1, z: 'back' });
        R.arms.near = hang('near', -4, -12);
        R.lanternSwing = 0.06 * Math.sin(t * 1.9);
        R.lantern = { hand: 'near', z: 9.4 };
      }
    }
    R.tilt += (o.tilt || 0) * RAD;
    R.nod = clamp(R.nod + (o.nod || 0));
    R.lean += (o.lean || 0) * RAD;
    if (o.sweat != null) R.fx.sweat = o.sweat;
    if (o.lines != null) R.fx.lines = o.lines;
    if (o.impact != null) R.fx.impact = o.impact;

    // ---- derived skeleton
    R.hipP = [R.hipX, -R.hipY];
    R.neck = torsoPt([0, -T.torso]);
    for (const side of ['near', 'far']) {
      const F = R.feet[side];
      const hp = add(R.hipP, rot([side === 'near' ? -T.legX : T.legX * 0.85, 0], R.lean * 0.4));
      const [knee, ank] = ik(hp, F.p, T.thigh, T.shin, 1);
      F.hip = hp; F.knee = knee; F.ank = ank;
      const A = R.arms[side];
      if (A) {
        A.sh = sh(side);
        const [el, wr] = ik(A.sh, A.wr, T.armU, T.armL, A.bend);
        A.el = el; A.wr = wr;
        if (A.handAng == null) A.handAng = ang(el, wr);
      }
    }
    return R;
  }

  // ------------------------------------------------------------------------------------------------ draw
  function propDraw(g, R, T, pr, t) {
    if (pr.kind === 'hammer') drawHammer(g, pr.p0, pr.a, { len: pr.len });
    else if (pr.kind === 'spear') drawSpear(g, pr.p0, pr.a, { t, variant: R.variant, len: R.spearLen });
    else if (pr.kind === 'shield') drawShield(g, pr.c, pr.r, { variant: R.variant, w: T.name === 'shield' ? 132 : 112, h: T.name === 'shield' ? 164 : 140 });
    else if (pr.kind === 'notebookHeld') drawNotebook(g, pr.c, pr.r, { w: 62, h: 78 });
    else if (pr.kind === 'quillHeld') drawQuill(g, pr.p, pr.a, { len: 62 });
    else if (pr.kind === 'lanternFloor') { R.lanternPt = drawLantern(g, add(pr.p, [0, -80]), 0, { lit: R.lanternLit }); }
  }

  // silhouettes used for the occlusion shadows
  const armSil = (T, A) => c => {
    S.addLimb(c, [A.sh, A.el, A.wr], [T.armW, T.armW * 0.86, T.armW * 0.74]);
    const hc = polar(A.wr, A.handAng, T.fist * 0.7); c.moveTo(hc[0] + T.fist, hc[1]); c.arc(hc[0], hc[1], T.fist * 0.95, 0, TAU);
  };
  const legSil = (T, L) => c => S.addLimb(c, [L.hip, L.knee, L.ank], [T.legW, T.legW * 0.86, T.legW * 0.66]);
  function propSil(T, pr) {
    if (pr.kind === 'hammer') { const p1 = polar(pr.p0, pr.a, pr.len || 250); return c => { S.addCapsule(c, pr.p0[0], pr.p0[1], p1[0], p1[1], 15, 15); c.moveTo(p1[0] + 46, p1[1]); c.arc(p1[0], p1[1], 46, 0, TAU); }; }
    if (pr.kind === 'spear') { const p1 = polar(pr.p0, pr.a, pr.len || 540); return c => S.addCapsule(c, pr.p0[0], pr.p0[1], p1[0], p1[1], 10, 10); }
    if (pr.kind === 'shield') { const w = T.name === 'shield' ? 132 : 112, h = T.name === 'shield' ? 164 : 140; return c => { c.save(); c.translate(pr.c[0], pr.c[1]); c.rotate(pr.r); shieldPath(w, h)(c); c.restore(); }; }
    if (pr.kind === 'notebookHeld') return c => { c.save(); c.translate(pr.c[0], pr.c[1]); c.rotate(pr.r); S.addRoundRect(c, -31, -39, 62, 78, 5); c.restore(); };
    return null;
  }

  function drawFigure(g, R, T, o) {
    const t = o.t || 0;
    const items = [];
    const push = (z, fn) => items.push({ z, fn });
    const helmXf = gg => { gg.translate(R.neck[0], R.neck[1]); gg.rotate(R.lean + R.tilt + R.nod * 0.12); gg.translate(R.helmDX + R.nod * 6, R.helmDY + R.nod * 4); };
    const { w: hw, h: hh } = helmGeo(T);
    if (T.name === 'spear') push(0.2, gg => drawCape(gg, R, T, t));
    // far side
    push(1, gg => { if (R.arms.far && R.arms.far.z === 'back') drawArm(gg, R, T, R.arms.far); });
    push(1.2, gg => { if (R.arms.far) drawPauldron(gg, R, T, R.arms.far, false); });
    push(2, gg => drawLeg(gg, R, T, R.feet.far));
    push(3, gg => { occl(gg, legSil(T, R.feet.near), 5, 0.3); drawLeg(gg, R, T, R.feet.near); });
    push(5, gg => drawTorso(gg, R, T, o));
    if (T.name === 'hammer' && R.variant !== 'horror') push(5.5, gg => drawSash(gg, R, T, t));
    if (R.variant === 'k404' && !R.noBeltKit) push(5.6, gg => drawBeltKit(gg, R, T, o));
    push(7, gg => {
      gg.save(); helmXf(gg);
      occl(gg, c => S.addRoundRect(c, -hw * 0.5, -hh, hw, hh, hw * 0.2), 8, 0.36);
      drawHelmLocal(gg, T, { nod: R.nod, variant: R.variant, t }); gg.restore();
    });
    push(9, gg => { if (R.arms.far && R.arms.far.z === 'front') { occl(gg, armSil(T, R.arms.far), 6); drawArm(gg, R, T, R.arms.far); } });
    push(10, gg => {
      const A = R.arms.near; if (!A) return;
      occl(gg, armSil(T, A), 7);
      drawArm(gg, R, T, A, A.handZ === 'top' ? 'arm' : 'all');
      occl(gg, c => c.arc(A.sh[0] - T.paulR * 0.1, A.sh[1], T.paulR, 0, TAU), 5, 0.28);
      drawPauldron(gg, R, T, A, true);
    });
    if (R.arms.near && R.arms.near.handZ === 'top') push(10.8, gg => drawHand(gg, R.arms.near.wr, R.arms.near.handAng, T, R.arms.near.shape, R.arms.near.thumb));
    R.props.forEach(pr => { if (pr.kind === 'spear') pr.len = R.spearLen; }); R.props.forEach(pr => push(pr.z, gg => { const sil = pr.z > 4 ? propSil(T, pr) : null; if (sil) occl(gg, sil, 7, 0.32); propDraw(gg, R, T, pr, t); }));
    if (R.lantern) {
      const A = R.arms[R.lantern.hand];
      push(R.lantern.z, gg => { R.lanternPt = drawLantern(gg, add(A.wr, polar([0, 0], A.handAng, T.fist * 0.7)), R.lanternSwing, { lit: R.lanternLit }); });
    }
    items.sort((a, b) => a.z - b.z).forEach(it => it.fn(g));
  }

  // fx in canvas space (outside the shadow group): sweat, tremble lines, impact, lantern light, cold slit glow
  function fxPass(ctx, R, T, X, o) {
    const t = o.t || 0;
    const { w, h } = helmGeo(T);
    const helmTop = X([R.neck[0] + R.helmDX, R.neck[1] - h * 0.95]);
    const helmSide = X([R.neck[0] + w * 0.55, R.neck[1] - h * 0.75]);
    const helmBack = X([R.neck[0] - w * 0.58, R.neck[1] - h * 0.7]);
    const s = X.s;
    if (R.fx.sweat > 0) {
      const spots = [[helmSide, 0.5, 22], [helmBack, -0.5, 18], [X([R.neck[0] + w * 0.5, R.neck[1] - h * 1.02]), 0.3, 16]];
      for (let i = 0; i < Math.min(3, R.fx.sweat); i++) {
        const [p, a, sz] = spots[i];
        const drip = frac(t * 0.9 + i * 0.37) * 10;
        S.sweat(ctx, p[0] + Math.sign(a) * X.dir * 8 * s, p[1] + drip * s, sz * s, { angle: a * X.dir });
      }
    }
    if (R.fx.lines > 0) {
      ctx.save(); ctx.strokeStyle = 'rgba(232,236,244,' + (0.75 * R.fx.lines) + ')'; ctx.lineWidth = 3.2 * s; ctx.lineCap = 'round';
      const jit = Math.sin(t * 50) * 2 * s;
      for (const sd of [-1, 1]) for (let i = 0; i < 3; i++) {
        const c = X([R.neck[0] + sd * (w * 0.62 + i * 7), R.neck[1] - h * (0.3 + i * 0.22)]);
        ctx.beginPath(); ctx.moveTo(c[0] + jit, c[1] - 9 * s); ctx.quadraticCurveTo(c[0] + sd * X.dir * 6 * s + jit, c[1], c[0] + jit, c[1] + 9 * s); ctx.stroke();
      }
      ctx.restore();
    }
    if (R.fx.impact > 0 && R.fx.impactAt) {
      const c = X(R.fx.impactAt), k = R.fx.impact;
      ctx.save(); ctx.strokeStyle = 'rgba(255,244,214,' + (0.95 * k) + ')'; ctx.lineCap = 'round'; ctx.lineWidth = 4.5 * s;
      for (let i = 0; i < 5; i++) {
        const a = -Math.PI / 2 + (i - 2) * 0.48, r0 = (18 + (1 - k) * 12) * s, r1 = r0 + (14 + 10 * k) * s;
        ctx.beginPath(); ctx.moveTo(c[0] + Math.cos(a) * r0, c[1] + Math.sin(a) * r0); ctx.lineTo(c[0] + Math.cos(a) * r1, c[1] + Math.sin(a) * r1); ctx.stroke();
      }
      ctx.restore();
    }
    if (R.lanternPt && R.lanternLit !== false && (o.lantern?.glow ?? 1) > 0) {
      const c = X(R.lanternPt), gl = o.lantern?.glow ?? 1, fl = 1 + 0.06 * Math.sin(t * 11) + 0.04 * Math.sin(t * 17.3);
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      const rg = ctx.createRadialGradient(c[0], c[1], 0, c[0], c[1], 150 * s * fl);
      rg.addColorStop(0, 'rgba(255,214,140,' + (0.55 * gl) + ')'); rg.addColorStop(0.25, 'rgba(255,190,110,' + (0.22 * gl) + ')'); rg.addColorStop(1, 'rgba(255,170,90,0)');
      ctx.fillStyle = rg; ctx.fillRect(c[0] - 160 * s, c[1] - 160 * s, 320 * s, 320 * s);
      ctx.restore();
    }
    void helmTop;
  }

  let _rim = null;
  function rimPass(g, rim, s) {
    const cv = g.canvas, w = cv.width, h = cv.height;
    if (!_rim) _rim = document.createElement('canvas');
    const m = _rim; if (m.width < w || m.height < h) { m.width = Math.max(m.width, w); m.height = Math.max(m.height, h); }
    const mc = m.getContext('2d');
    mc.setTransform(1, 0, 0, 1, 0, 0); mc.globalCompositeOperation = 'source-over'; mc.clearRect(0, 0, m.width, m.height);
    mc.drawImage(cv, 0, 0);
    mc.globalCompositeOperation = 'source-in'; mc.fillStyle = rim.color || '#C9D2E0'; mc.fillRect(0, 0, w, h);
    const d = rim.dir || [-1, -0.6], L = Math.hypot(d[0], d[1]) || 1, wd = (rim.width ?? 3) * s;
    mc.globalCompositeOperation = 'destination-out';
    mc.drawImage(cv, -d[0] / L * wd, -d[1] / L * wd);
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-atop'; g.globalAlpha = rim.alpha ?? 0.6;
    g.drawImage(m, 0, 0, w, h, 0, 0, w, h);
    g.restore();
  }

  // colour laid over the figure only. mode = any canvas blend ('soft-light', 'multiply', 'overlay'...) or normal
  function tintPass(g, tn) {
    const cv = g.canvas, w = cv.width, h = cv.height;
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    if (!tn.mode || tn.mode === 'normal' || tn.mode === 'source-over') {
      g.globalCompositeOperation = 'source-atop'; g.globalAlpha = tn.amount ?? 0.3; g.fillStyle = tn.color || '#0B0D12'; g.fillRect(0, 0, w, h);
    } else {
      if (!_rim) _rim = document.createElement('canvas');
      const m = _rim; if (m.width < w || m.height < h) { m.width = Math.max(m.width, w); m.height = Math.max(m.height, h); }
      const mc = m.getContext('2d');
      mc.setTransform(1, 0, 0, 1, 0, 0); mc.globalCompositeOperation = 'source-over'; mc.clearRect(0, 0, m.width, m.height);
      mc.drawImage(cv, 0, 0); mc.globalCompositeOperation = 'source-in'; mc.fillStyle = tn.color || '#FFB46A'; mc.fillRect(0, 0, w, h);
      g.globalCompositeOperation = tn.mode; g.globalAlpha = tn.amount ?? 0.3; g.drawImage(m, 0, 0, w, h, 0, 0, w, h);
      mc.globalCompositeOperation = 'source-over';
    }
    g.restore();
  }

  function setPal(variant) { P = variant === 'horror' ? COL.horror : COL.normal; }

  function draw(ctx, x, y, s = 1, o = {}) {
    const T = TYPES[o.type || 'hammer'];
    if (!T) throw new Error('KNIGHT: unknown type ' + o.type);
    const dir = o.facing === -1 ? -1 : 1;
    if ((o.pose || 'idle') === 'peek') return drawPeek(ctx, x, y, s, o, T, dir);
    setPal(o.variant);
    const R = solve(T, o);
    R.lanternLit = o.lantern?.lit ?? (o.variant !== 'horror');
    const X = p => [x + dir * p[0] * s, y + p[1] * s]; X.s = s; X.dir = dir;
    const ext = 1.6 * T.helmH + 300;
    const bounds = { x: x - (T.name === 'spear' ? 640 : 420) * s, y: y - (T.name === 'spear' ? 760 : 620) * s, w: (T.name === 'spear' ? 1280 : 840) * s, h: (T.name === 'spear' ? 800 : 680) * s };
    void ext;
    if (o.cast !== false) S.groundShadow(ctx, x + dir * 6 * s, y + 2 * s, (T.stance * 2 + T.foot * 1.4) * s, 22 * s, 0.5);
    LX = dir;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s * dir, s);
      drawFigure(g, R, T, o);
      g.restore();
      if (o.rim) rimPass(g, o.rim === true ? {} : o.rim, s);
      if (o.grade) tintPass(g, o.grade);   // e.g. warm torchlight: { color: '#FFB46A', amount: 0.3, mode: 'soft-light' }
      if (o.tint) tintPass(g, o.tint);     // e.g. depth fog: { color: '#0A0B10', amount: 0.4 } (normal blend)
    }, { scale: s, bounds, shadow: o.shadow !== false, alpha: o.alpha ?? 1 });
    // emissive: the horror slit glow (light only, no face)
    if (R.variant === 'horror') {
      const { w, h } = helmGeo(T);
      S.glow(ctx, gg => {
        gg.save(); gg.translate(x, y); gg.scale(s * dir, s);
        gg.translate(R.neck[0], R.neck[1]); gg.rotate(R.lean + R.tilt + R.nod * 0.12); gg.translate(R.helmDX + R.nod * 6, R.helmDY + R.nod * 4);
        const sy = (T.helm === 'bucket' ? -h * 0.56 : T.helm === 'point' ? -h * 0.52 - h * 0.032 : -h * 0.54) + R.nod * 0.1 * h;
        const f = 0.13 * w;
        S.strip(gg, [[-w * 0.36 + f, sy], [w * 0.33 + f, sy]], u => h * 0.03 * Math.sin(Math.PI * u) ** 0.4, COL.horror.slitLight);
        gg.restore();
      }, { blur: 14 * s, alpha: 0.9, bounds: { x: x - 200 * s, y: y - 500 * s, w: 400 * s, h: 300 * s } });
    }
    LX = dir;
    fxPass(ctx, R, T, X, o);
    LX = 1;
    R.X = X;
    return R;
  }

  // ---- peek: only the helm (leaning out past an edge) and one gripping hand
  function drawPeek(ctx, x, y, s, o, T, dir) {
    setPal(o.variant);
    const { w, h } = helmGeo(T);
    const peekH = o.peekH ?? (T.hip + T.torso + h * 0.5);
    const out = o.peekOut ?? 0.5 * w;
    const tilt = (o.tilt ?? 22) * RAD;
    const nod = clamp(o.nod ?? 0);
    const handH = o.handH ?? (peekH - h * 0.55);
    const part = o.part || 'all';
    const t = o.t || 0;
    LX = dir;
    S.shadowGroup(ctx, g => {
      // helm (clipped to the visible region if given)
      if (part !== 'hand') {
        g.save();
        if (o.clip) { g.beginPath(); o.clip(g); g.clip(); }
        g.translate(x, y); g.scale(s * dir, s);
        // the helm pivots around a point below it (the hidden neck), so it swings out of the edge
        g.translate(out - Math.sin(tilt) * h * 0.2, -peekH + h * 0.5);
        g.rotate(tilt + nod * 0.14);
        g.translate(nod * 5, nod * 5);
        // a sliver of the gorget under the helm
        plate(g, c => S.addRoundRect(c, -w * 0.4, -6, w * 0.8, 20, 8), { sd: 3, ld: 1.6 });
        drawHelmLocal(g, T, { nod, variant: o.variant, t });
        g.restore();
      }
      if (part !== 'helm') {
        g.save(); g.translate(x, y); g.scale(s * dir, s);
        const f = T.fist * 1.2, hy = -handH;
        // back of the gauntlet just inside the opening, three plated fingers curling over the edge onto the wall face
        occl(g, c => S.addRoundRect(c, -f * 1.0, hy - f * 0.8, f * 2.3, f * 1.6, f * 0.5), 5, 0.4);
        plate(g, c => S.addRoundPoly(c, [[f * 1.35, hy - f * 0.95], [f * 0.5, hy - f * 0.8], [f * 0.5, hy + f * 0.8], [f * 1.35, hy + f * 0.98]], [4, 3, 3, 4]), { sd: 3, ld: 1.6 });
        plate(g, c => S.addRoundRect(c, -f * 0.1, hy - f * 0.78, f * 0.95, f * 1.56, f * 0.5), { sd: 3.5, ld: 1.8 });
        for (let i = -1; i <= 1; i++) {
          const fy = hy + i * f * 0.5;
          plate(g, c => S.addRoundRect(c, -f * 0.95, fy - f * 0.23, f * 1.15, f * 0.46, f * 0.23), { sd: 2.5, ld: 1.4 });
          flat(g, c => c.rect(-f * 0.45, fy - f * 0.2, 2, f * 0.4), P.shade);
        }
        g.restore();
      }
    }, { scale: s, bounds: { x: x - 300 * s, y: y - (peekH + h + 120) * s, w: 600 * s, h: (peekH + h + 160) * s }, shadow: o.shadow !== false });
    if (o.variant === 'horror' && part !== 'hand') {
      S.glow(ctx, gg => {
        if (o.clip) { gg.beginPath(); o.clip(gg); gg.clip(); }
        gg.translate(x, y); gg.scale(s * dir, s);
        gg.translate(out - Math.sin(tilt) * h * 0.2, -peekH + h * 0.5); gg.rotate(tilt + nod * 0.14); gg.translate(nod * 5, nod * 5);
        const sy = (T.helm === 'bucket' ? -h * 0.56 : -h * 0.53) + nod * 0.1 * h, f = 0.13 * w;
        S.strip(gg, [[-w * 0.36 + f, sy], [w * 0.33 + f, sy]], u => h * 0.03 * Math.sin(Math.PI * u) ** 0.4, COL.horror.slitLight);
      }, { blur: 12 * s, alpha: 0.9, bounds: { x: x - 300 * s, y: y - (peekH + h + 120) * s, w: 600 * s, h: (peekH + h + 160) * s } });
    }
    if ((o.sweat || 0) > 0) {
      const hc = [x + dir * (out + w * 0.55) * s, y - (peekH + h * 0.2) * s];
      for (let i = 0; i < o.sweat; i++) S.sweat(ctx, hc[0] + dir * i * 16 * s, hc[1] - i * 18 * s, (18 - i * 3) * s, { angle: 0.4 * dir });
    }
    LX = 1;
    return { helm: { x: x + dir * out * s, y: y - peekH * s, w: w * s, h: h * s } };
  }

  function drawHelm(ctx, x, y, s = 1, o = {}) {
    const T = TYPES[o.type || 'hammer'], dir = o.facing === -1 ? -1 : 1;
    setPal(o.variant); LX = dir;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s * dir, s); g.rotate((o.tilt || 0) * RAD);
      drawHelmLocal(g, T, { nod: o.nod || 0, variant: o.variant, t: o.t || 0 });
      g.restore();
    }, { scale: s, bounds: { x: x - 200 * s, y: y - 260 * s, w: 400 * s, h: 300 * s }, shadow: o.shadow !== false });
    if (o.variant === 'horror') {
      const { w, h } = helmGeo(T);
      S.glow(ctx, gg => {
        gg.translate(x, y); gg.scale(s * dir, s); gg.rotate((o.tilt || 0) * RAD);
        const sy = (T.helm === 'bucket' ? -h * 0.56 : -h * 0.53) + (o.nod || 0) * 0.1 * h, f = 0.13 * w;
        S.strip(gg, [[-w * 0.36 + f, sy], [w * 0.33 + f, sy]], u => h * 0.03 * Math.sin(Math.PI * u) ** 0.4, COL.horror.slitLight);
      }, { blur: 12 * s, alpha: 0.9, bounds: { x: x - 200 * s, y: y - 260 * s, w: 400 * s, h: 300 * s } });
    }
    LX = 1;
  }

  function drawProp(ctx, name, x, y, s = 1, o = {}) {
    setPal(o.variant); LX = 1;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s, s);
      if (name === 'hammer') drawHammer(g, [0, 0], o.a ?? -Math.PI / 2, o);
      else if (name === 'spear') drawSpear(g, [0, 0], o.a ?? -Math.PI / 2, o);
      else if (name === 'shield') drawShield(g, [0, 0], o.r || 0, o);
      else if (name === 'lantern') drawLantern(g, [0, 0], o.swing || 0, o);
      else if (name === 'notebook') drawNotebook(g, [0, 0], o.r || 0, o);
      else if (name === 'quill') drawQuill(g, [0, 0], o.a ?? -Math.PI / 2, o);
      g.restore();
    }, { scale: s, bounds: { x: x - 700 * s, y: y - 700 * s, w: 1400 * s, h: 1400 * s }, shadow: o.shadow !== false });
  }

  function solvePublic(x, y, s = 1, o = {}) {
    const T = TYPES[o.type || 'hammer'], dir = o.facing === -1 ? -1 : 1;
    const R = solve(T, o);
    const X = p => [x + dir * p[0] * s, y + p[1] * s];
    const { w, h } = helmGeo(T);
    const top = T.helm === 'point' ? h + T.point : T.helm === 'crest' ? h + T.crest : h;
    return {
      helm: { x: X(R.neck)[0], y: X(R.neck)[1] - h * 0.5 * s, w: w * s, h: h * s, top: X(R.neck)[1] - top * s },
      hands: { near: R.arms.near ? X(R.arms.near.wr) : null, far: R.arms.far ? X(R.arms.far.wr) : null },
      contact: R.fx.impactAt ? X(R.fx.impactAt) : null,
      bounds: { x: x - 160 * s, y: y - (T.hip + T.torso + top) * s, w: 320 * s, h: (T.hip + T.torso + top) * s },
    };
  }

  window.KNIGHT = {
    version: '1.0', W, H: HU, TYPES, COL, POSES,
    draw, drawHelm, drawProp, solve: solvePublic,
    stride: type => TYPES[type || 'hammer'].strideA * 4,
    knockAt: type => [TYPES[type || 'hammer'].knockDX, -150],
    chestDX: type => TYPES[type || 'hammer'].chestDX,
  };
})();
