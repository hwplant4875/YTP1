/* =====================================================================================================================
 * lib_core.js : window.SFX, the shared drawing kit for the Monster HR show (Protocol 404 pivot).
 * Every character and set loads this first so they all look like one show:
 *   no black outlines around shapes, flat fills with ONE hard shade tone per material, one soft drop shadow per
 *   character GROUP (down-right), big low-set 귤멍-style eyes, light always from the top-left.
 * Plain canvas 2D, no dependencies, deterministic (never uses Math.random). Load order: lib_core.js, then rigs, then scene.
 *
 * Conventions
 *   - Points may be [x, y] arrays or {x, y} objects everywhere a point is taken.
 *   - Colours are any canvas colour string; the colour helpers parse '#rgb', '#rrggbb', '#rrggbbaa', 'rgb()', 'rgba()'.
 *   - Shape helpers come in two forms: SFX.addX(ctx, ...) appends a sub-path to the current path (no beginPath, no fill),
 *     SFX.x(ctx, ..., fill, stroke, lineWidth) does beginPath + addX + fill/stroke. Pass fill = null to only build the path.
 *   - Sub-paths built by addRoundRect / addCapsule / addLimb / circle all wind the same way, so several of them filled
 *     together form a union (nonzero rule).
 *
 * ---------------------------------------------------------------------------------------------------------------------
 * MATH, TIME, RANDOM
 *   SFX.TAU                               2π
 *   SFX.clamp(v, a=0, b=1)                clamp
 *   SFX.lerp(a, b, k)                     linear interpolation
 *   SFX.lerpPt(p, q, k) -> [x, y]         point interpolation
 *   SFX.prog(t, t0, dur) -> 0..1          progress of t through [t0, t0+dur], clamped
 *   SFX.smoothstep(a, b, x)               Hermite step
 *   SFX.deg(d)                            degrees -> radians
 *   SFX.xy(p) -> [x, y]                   normalise a point
 *   SFX.rot(x, y, ang) -> [x, y]          rotate a vector
 *   SFX.fk(base, segs) -> [[x,y],...]     forward kinematics. base = point, segs = [[length, angle], ...] where each
 *                                         angle (radians, 0 = +x, +π/2 = straight down) is RELATIVE to the previous
 *                                         segment (the first is absolute). Returns base + every joint.
 *   SFX.rng(seed) -> r()                  seeded PRNG (mulberry32), seed = number or string. r() in [0,1). Also
 *                                         r.range(a,b), r.int(a,b) inclusive, r.pick(arr), r.sign(), r.gauss().
 *   SFX.hash(n) -> [0,1)                  stateless hash of a number (for per-index jitter without an RNG)
 *   SFX.ease.{linear, easeInQuad, easeOutQuad, easeInOutQuad, easeInCubic, easeOutCubic, easeInOutCubic,
 *             easeInBack(k, s=1.70158), easeOutBack(k, s=1.70158), easeInOutBack, easeInOutSine, easeOutElastic}
 *                                         all take k (clamped to 0..1) and return the eased value.
 *   SFX.spring(t, freq=2.2, damping=0.35) step response of a damped spring, 0 at t<=0, overshoots, settles at 1.
 *                                         Use for pops: scale = SFX.spring(t - t0, 3, 0.3).
 *   SFX.wobble(t, freq=3, decay=4)        damped sine (0 at t<=0) for after-shocks: angle = 0.2 * SFX.wobble(t - hitT).
 *   SFX.blinkAt(t, seed=1, every=3.2) -> open 0..1   deterministic idle blink curve (0.13 s blinks every 2.5-4 s).
 *
 * COLOUR
 *   SFX.color.parse(c) -> [r,g,b,a]       SFX.color.hex(r,g,b) -> '#rrggbb'
 *   SFX.color.rgba(c, a)                  same colour with alpha a
 *   SFX.color.mix(c1, c2, k)              mix, k=0 -> c1
 *   SFX.color.shade(c, k)                 k<0 darkens toward black, k>0 lightens toward white (k in -1..1)
 *   SFX.color.lum(c), SFX.color.contrast(c1, c2)   WCAG relative luminance / contrast ratio (for the 3:1 checks)
 *   SFX.PAL                               shared palette (plan sections 3 + 4): ink, sclera, crease, skin, mouth, blush,
 *                                         blood, dungeon stones, torch, room, paper, stamp, chain ... and
 *                                         SFX.PAL.iris.{blue, gold, rose, green, violet, teal, grey, red} (dark -> light)
 *
 * SHAPES
 *   SFX.version                                        library version string
 *   SFX.paint(ctx, fill, stroke, lw)                   fill and/or stroke the CURRENT path (round joins and caps)
 *   SFX.addRoundRect(ctx, x, y, w, h, r)               r = number or [tl, tr, br, bl]
 *   SFX.roundRect(ctx, x, y, w, h, r, fill, stroke, lw)
 *   SFX.addCapsule(ctx, x1, y1, x2, y2, w1, w2=w1)     limb between two points, round ends, w = DIAMETER at each end
 *   SFX.capsule(ctx, x1, y1, x2, y2, w1, w2, fill, stroke, lw)
 *   SFX.addLimb(ctx, pts, widths) / SFX.limb(ctx, pts, widths, fill)   chain of capsules through pts (shoulder, elbow,
 *                                         wrist...), widths = one diameter per point (or a single number)
 *   SFX.addBlob(ctx, pts, tension=0.5) / SFX.blob(ctx, pts, fill, tension, stroke, lw)
 *                                         smooth CLOSED shape through every point (Catmull-Rom -> cubic bezier)
 *   SFX.addCurve(ctx, pts, tension=0.5, moveFirst=true) / SFX.curve(ctx, pts, color, lw, tension)
 *                                         smooth OPEN curve through points (stroked with round caps)
 *   SFX.addPoly(ctx, pts, close=true) / SFX.poly(ctx, pts, fill, stroke, lw)
 *   SFX.addRoundPoly(ctx, pts, r) / SFX.roundPoly(ctx, pts, r, fill, stroke, lw)
 *                                         polygon with rounded corners (r = number or one radius per corner): the
 *                                         default for clothes and props ("straight polygons, slightly softened")
 *   SFX.circle(ctx, x, y, r, fill, stroke, lw)  /  SFX.ellipse(ctx, x, y, rx, ry, rot, fill, stroke, lw)
 *   SFX.strip(ctx, pts, width, fill)      ribbon along a polyline; width = number or fn(u) with u = 0..1 along the
 *                                         line (tapered strokes, seams, brows)
 *   SFX.clip(ctx, pathFn, drawFn)         clip to the path built by pathFn(ctx), run drawFn(ctx), restore
 *   SFX.cel(ctx, pathFn, base, shade, dx=8, dy=dx)   flat fill + ONE hard shade crescent on the bottom-right
 *                                         (the shape minus itself shifted up-left by dx,dy, i.e. light from the
 *                                         top-left). pathFn(ctx) must only ADD sub-paths (use SFX.addX helpers,
 *                                         never ctx.beginPath inside it); it is called twice.
 *
 * GROUPS, LIGHT, SCREEN FX
 *   SFX.shadowGroup(ctx, drawFn, opts)    draws drawFn(g) into an offscreen layer (same transform as ctx) and
 *                                         composites it ONCE with a soft drop shadow, so parts inside a character
 *                                         never shadow each other. drawFn MUST draw with the g it receives.
 *       opts.scale=1      multiplies blur and offset (use the character's on-screen scale)
 *       opts.color='rgba(0,0,0,0.45)', opts.blur=20, opts.dx=8, opts.dy=8   (pixels at scale 1)
 *       opts.alpha=1      fade the whole group as one piece (no see-through overlaps)
 *       opts.shadow=true  false = only group/alpha, no shadow
 *       opts.bounds       optional {x,y,w,h} in ctx coordinates that surely contains the drawing (smaller = faster)
 *   SFX.layer(ctx, drawFn, bounds) -> {canvas, x, y, w, h, release()}   low-level: same offscreen layer, you composite
 *                                         (in device pixels, identity transform) and then MUST call release().
 *   SFX.groundShadow(ctx, x, y, w, h=0.16w, alpha=0.5)  soft contact ellipse under feet/boxes (top-lit scenes)
 *   SFX.grain(ctx, amount=0.06, seed=1)   film grain over the whole frame (overlay noise, ~1-2 % at 0.06)
 *   SFX.vignette(ctx, strength=0.55, opts{inner=0.45, outer=1.05, color='#000', cx, cy})  elliptical edge darkening
 *   SFX.scanlines(ctx, x, y, w, h, gap=4, alpha=0.16, color='#000')   CRT lines (TV faces / monitors)
 *   SFX.glow(ctx, drawFn, opts{blur=12, alpha=0.8, bounds, crispAlpha=1, wide=true})   draws drawFn(g) crisp, then
 *                                         adds blurred 'lighter' bloom copies (emissive things: lenses, screens, torches)
 *
 * FACE
 *   SFX.eye(ctx, o)        the 귤멍 eye recipe (plan 3-2), drawn back to front: sclera, iris bands, pupil, highlight,
 *                          lid shade, lower lid line + teeth, crease, black upper-lid band with pointed outer wing and
 *                          inner-corner wrap, lash spikes. o:
 *       x, y              centre of the eye (px)                     w        eye width (px)
 *       h=0.6             height/width: 0.45 half-lidded, 0.5 almond, 0.6 default, 0.8 round/innocent
 *       mirror=false      false: the outer corner (wing) points to the viewer's LEFT (the eye on the left of the face)
 *                         true: wing points RIGHT (the eye on the right of the face)
 *       tilt=0            radians, + raises the outer corner (angry/sly), - drops it (sad/tired)
 *       iris=PAL.iris.blue   2-4 colours, dark top -> light bottom (horizontal bands that bow like a smile)
 *       irisScale=0.62    iris diameter / eye width (0.3 smug/eerie ... 0.7 cute), or 'dot' (fear: small dark dot)
 *       irisY=-0.1        rest height of the iris centre (fraction of eye height, - = up, so the lid covers its top)
 *       pupil='oval'      'oval' | 'slit' | 'star' | 'dot' | 'swirl' | 'heart' | 'none'
 *       pupilColor        default: iris[0] darkened (light tint for 'star')     pupilScale=1   dilation
 *       highlight=true    one small white blob, always upper-LEFT on screen (light from top-left), even when the
 *                         rig mirrors the whole character with scale(-1, 1)
 *       highlight2=false  optional tiny second glint, lower right of the iris
 *       highlightSize=0.13  diameter / iris diameter
 *       look={x:0,y:0}    gaze in -1..1, in the eye's parent coordinates (x + = right, y + = down)
 *       open=1            upper lid position 1 open .. 0 shut (<0.12 draws the 'flat' closed eye: use for blinks)
 *       lowerRaise=0      0..1 lower lid pushes up (smug, squint, eerie smile)
 *       lid=0.15          lid band thickness as a fraction of the nominal eye height (0.6 w)
 *       wing=0.2, wingAngle=0.3     outer wing length (fraction of w) and lift (radians)
 *       innerWrap=0.15    how far the band wraps down the inner corner (0..0.5)
 *       lashes=3, lashLen=0.32      lash spike count and length (fraction of nominal eye height)
 *       crease=2          thin grey double-lid arcs above the band (0, 1, 2)
 *       lower=0.66        lower-lid line length along the bottom from the outer corner (0 = none)
 *       teeth=3           tiny downward triangles on the lower-lid line (0-4)
 *       lowerCrease=true  faint grey line under the lower lid
 *       closed=false      'smile' (∩ happy/content), 'flat' (blink/sleep), 'sleep' (∪ soft), or false
 *       lidShade=0        alpha of an optional hard shade band under the upper lid (the ref keeps whites flat)
 *       darkCircle=0      0..1 eerie under-eye crescent          tears=0   0..1 water welling at the bottom (fear)
 *       glow=false        render as LIGHT on a dark screen (TV face): sclera dim, lines and iris emissive, bloom
 *       glowColor='#8ff7ff', glowBlur=0.07 (fraction of w), screen='#06090c' (pupil = screen colour in glow mode)
 *       ink='#1c1519', sclera='#ffffff', creaseColor='#b3a6b0'   line / white / crease colours
 *       advanced: irisStretch=1.06 (iris height/width), irisBow=0.12 (band curve), irisRing=0 (alpha of a thin inner
 *                 ring), lashFrom=0.07 / lashTo=0.5 (lash span along the lid), t (time, animates the tear wave)
 *     returns {ix, iy, ir}: the iris centre and radius in the eye's parent coordinates (for sparkles, tears).
 *   SFX.eyePair(ctx, o)    both eyes: o.x,o.y = midpoint, o.w = eye width, o.gap=0.34 (gap / eye width),
 *                          o.turn=0 (-1..1 three-quarter turn: far eye 0.85 width, pair shifts 0.12 toward the turn),
 *                          o.L / o.R = per-eye overrides (L = eye on the viewer's left). Everything else goes to both.
 *   SFX.EXPR               eye presets to spread into SFX.eye: neutral, happy, content, nervous, greedy, eerie, fear,
 *                          bored, shock, angry, sad, smug, dizzy, sleepy.  e.g. SFX.eye(ctx, {...base, ...SFX.EXPR.fear})
 *   SFX.brow(ctx, x, y, w, o{tilt=0, thick=0.09, color=ink, mirror=false, arch=0.15})  thin tapered brow; tilt + lifts
 *                          the INNER end (worried), - drops it (angry). mirror like SFX.eye.
 *   SFX.mouth(ctx, x, y, w, type, o{color=PAL.mouth, inner=PAL.mouthIn, ink, open=1})
 *                          type: 'none' | 'smile' (pink crescent) | 'o' | 'open' (D shape + tongue) | 'u' | 'flat' |
 *                          'wave' (worried ~) | 'cat' (w) | 'fang' (o + one tiny tooth) | 'tri' (shouting)
 *   SFX.blush(ctx, x, y, w, alpha=0.35, color=PAL.blush, o{lines=0})   soft oval w x 0.44w (the ONLY face gradient)
 *   SFX.sweat(ctx, x, y, size, o{angle=0, color, shade, alpha=1})       teardrop (size = height), hard shade + glint
 *   SFX.tear(ctx, x, y, len, w, o{color})                               tear streak running down from (x, y)
 *   SFX.sparkle(ctx, x, y, r, color='#fff', rot=0)                      4-point star sparkle
 *   SFX.anger(ctx, x, y, size, color='#e2475a')                         popping-vein mark
 *
 * CHAIN (secondary motion, the mimic's tell, badge lanyards...)
 *   SFX.chainPoints(anchor, dir, links, linkSize, sag=0.5, o{t=0, sway=0, swayFreq=0.6, lag=2.2, pitch=0.7})
 *                          -> links+1 points. dir = radians (0 = right, π/2 = down) or a vector. sag 0 = straight
 *                          along dir, 1 = the tip hangs straight down. sway (radians) = travelling wave toward the tip.
 *                          pitch = link spacing / linkSize (links overlap).
 *   SFX.drawChain(ctx, pts, linkSize, colours)   links along any polyline: face-on rings and edge-on bars alternate,
 *                          each with one hard shade. colours = '#base' | [base, shade] | {base, shade, light}
 *   SFX.springChain(ctx, anchor, dir, links, linkSize, sag, colours, o) = drawChain(chainPoints(...)), returns pts.
 *   SFX.simChain(o{key, n, seg, t, anchor:(t)=>({x,y,angle}), gravity=1800, damping=0.985, iter=6})
 *                          deterministic verlet chain simulated from t=0 to t at 1/120 s steps (cached per key for
 *                          sequential frames) -> points. Use when you need real lag/whip; chainPoints otherwise.
 *
 * TEXT, BUBBLES, SHEETS
 *   SFX.label(ctx, text, x, y, size=30, o{color='#fff', align='center', base='middle', weight=800, bg, pad=0.45,
 *             alpha=1, maxW})   Nunito label, optional pill background. Returns the text width.
 *   SFX.title(ctx, text, x, y, size=64, o{color, align, base, weight=600, track})   Fredoka title
 *   SFX.bubble(ctx, o{x, y, w, h, tail:[x,y], lines:[...] or text, size=40, fill='#fff', color='#1b1a1f', shape='ellipse'|'round',
 *             scale=1, pop=1})   white speech bubble with one group drop shadow (pop = 0..1 animates with easeOutBack)
 *   SFX.sheetBG(ctx, W, H, o{bg='#17161c', grid=true, title, subtitle})   model-sheet backdrop + header
 *
 * USAGE (a rig)
 *   window.MIMIKU = { draw(ctx, p) {                         // p = {x, y, scale, pose, expr, t, ...}
 *     SFX.shadowGroup(ctx, g => {                              // ONE soft shadow for the whole character
 *       g.save(); g.translate(p.x, p.y); g.scale(p.scale, p.scale);
 *       SFX.cel(g, c => SFX.addRoundRect(c, -100, -80, 200, 160, 40), SFX.PAL.wood, SFX.PAL.woodShade, 10);
 *       SFX.eyePair(g, { x: 0, y: -10, w: 50, iris: SFX.PAL.iris.gold, pupil: 'slit', ...SFX.EXPR[p.expr] });
 *       g.restore();
 *     }, { scale: p.scale });
 *   } };
 *   Tests: core/test.js (kit sheet) and core/test_eyes.js (eye QA: hero, blink, gaze, sizes, presets, flipped rig).
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const SFX = {};
  window.SFX = SFX;
  const TAU = Math.PI * 2;
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const xy = p => (Array.isArray(p) ? p : [p.x, p.y]);
  SFX.version = '1.0';
  SFX.TAU = TAU;
  SFX.clamp = clamp;
  SFX.lerp = lerp;
  SFX.xy = xy;
  SFX.lerpPt = (p, q, k) => { p = xy(p); q = xy(q); return [lerp(p[0], q[0], k), lerp(p[1], q[1], k)]; };
  SFX.prog = (t, t0, d) => clamp((t - t0) / d);
  SFX.smoothstep = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  SFX.deg = d => d * Math.PI / 180;
  SFX.rot = (x, y, a) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];
  SFX.fk = (base, segs) => {
    const out = [xy(base).slice()];
    let ang = 0;
    segs.forEach(([len, a], i) => {
      ang = i === 0 ? a : ang + a;
      const p = out[out.length - 1];
      out.push([p[0] + Math.cos(ang) * len, p[1] + Math.sin(ang) * len]);
    });
    return out;
  };

  // ---------------------------------------------------------------- random
  function hashStr(s) { let h = 2166136261 >>> 0; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  SFX.rng = function (seed = 1) {
    let s = (typeof seed === 'string' ? hashStr(seed) : Math.floor(seed * 2654435761) >>> 0) || 0x9e3779b9;
    const r = () => {
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    r.range = (a, b) => a + (b - a) * r();
    r.int = (a, b) => Math.floor(a + (b - a + 1) * r());
    r.pick = arr => arr[Math.floor(r() * arr.length)];
    r.sign = () => (r() < 0.5 ? -1 : 1);
    r.gauss = () => { let u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v); };
    return r;
  };
  SFX.hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123; return x - Math.floor(x); };

  // ---------------------------------------------------------------- easing / springs
  SFX.ease = {
    linear: k => clamp(k),
    easeInQuad: k => (k = clamp(k)) * k,
    easeOutQuad: k => 1 - (1 - clamp(k)) ** 2,
    easeInOutQuad: k => { k = clamp(k); return k < 0.5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2; },
    easeInCubic: k => clamp(k) ** 3,
    easeOutCubic: k => 1 - (1 - clamp(k)) ** 3,
    easeInOutCubic: k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - (-2 * k + 2) ** 3 / 2; },
    easeInBack: (k, s = 1.70158) => { k = clamp(k); return (s + 1) * k * k * k - s * k * k; },
    easeOutBack: (k, s = 1.70158) => { k = clamp(k); return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2; },
    easeInOutBack: (k, s = 1.70158) => {
      k = clamp(k); const c2 = s * 1.525;
      return k < 0.5 ? ((2 * k) ** 2 * ((c2 + 1) * 2 * k - c2)) / 2 : ((2 * k - 2) ** 2 * ((c2 + 1) * (k * 2 - 2) + c2) + 2) / 2;
    },
    easeInOutSine: k => -(Math.cos(Math.PI * clamp(k)) - 1) / 2,
    easeOutElastic: k => { k = clamp(k); if (k === 0 || k === 1) return k; return 2 ** (-10 * k) * Math.sin((k * 10 - 0.75) * (TAU / 3)) + 1; },
  };
  SFX.spring = (t, freq = 2.2, damping = 0.35) => {
    if (t <= 0) return 0;
    const w = TAU * freq, z = clamp(damping, 0.01, 0.99), wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z / Math.sqrt(1 - z * z)) * Math.sin(wd * t));
  };
  SFX.wobble = (t, freq = 3, decay = 4) => (t <= 0 ? 0 : Math.exp(-decay * t) * Math.sin(TAU * freq * t));
  SFX.blinkAt = (t, seed = 1, every = 3.2) => {
    // blink windows: start times jittered 2.5-4 s apart, each 0.13 s (close 40 %, open 60 %)
    let t0 = 0.6 + SFX.hash(seed) * 1.5, i = 0;
    while (t0 + 0.13 < t && i < 10000) { t0 += every * (0.78 + 0.47 * SFX.hash(seed * 31 + i)); i++; }
    const k = (t - t0) / 0.13;
    if (k < 0 || k > 1) return 1;
    return k < 0.4 ? 1 - k / 0.4 : (k - 0.4) / 0.6;
  };

  // ---------------------------------------------------------------- colour
  const C = SFX.color = {};
  const _cc = {};
  C.parse = c => {
    if (Array.isArray(c)) return c;
    if (_cc[c]) return _cc[c];
    let r = 0, g = 0, b = 0, a = 1;
    const s = String(c).trim();
    if (s[0] === '#') {
      let h = s.slice(1);
      if (h.length === 3 || h.length === 4) h = h.split('').map(ch => ch + ch).join('');
      r = parseInt(h.slice(0, 2), 16); g = parseInt(h.slice(2, 4), 16); b = parseInt(h.slice(4, 6), 16);
      if (h.length === 8) a = parseInt(h.slice(6, 8), 16) / 255;
    } else {
      const m = s.match(/rgba?\(([^)]+)\)/);
      if (m) { const p = m[1].split(',').map(parseFloat); [r, g, b] = p; if (p.length > 3) a = p[3]; }
    }
    return (_cc[c] = [r, g, b, a]);
  };
  const h2 = v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0');
  C.hex = (r, g, b) => '#' + h2(r) + h2(g) + h2(b);
  C.rgba = (c, a) => { const [r, g, b] = C.parse(c); return `rgba(${Math.round(r)},${Math.round(g)},${Math.round(b)},${a})`; };
  C.mix = (c1, c2, k) => { const p = C.parse(c1), q = C.parse(c2); return C.hex(lerp(p[0], q[0], k), lerp(p[1], q[1], k), lerp(p[2], q[2], k)); };
  C.shade = (c, k) => (k < 0 ? C.mix(c, '#000000', -k) : C.mix(c, '#ffffff', k));
  C.lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; const [r, g, b] = C.parse(c); return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  C.contrast = (c1, c2) => { const a = C.lum(c1), b = C.lum(c2); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };

  SFX.PAL = {
    ink: '#1c1519', sclera: '#ffffff', crease: '#b3a6b0', skin: '#f6e6e8', skinShade: '#ebd0d6',
    mouth: '#e78191', mouthIn: '#6e2233', tongue: '#f08a9c', blush: '#ff7f96', blood: '#720000', bloodDecal: '#8E1F2E',
    shadow: 'rgba(0,0,0,0.45)',
    void: '#14121A', mortar: '#1C1A22', stoneDark: '#2A2733', stone: '#3D3946', stoneEdge: '#57525F',
    torchCore: '#FFD27A', torchFlame: '#FFB04A', torchOuter: '#FF7A2F', torchPool: '#6B4A3A',
    roomWall: '#1A2329', roomFloor: '#26323A', spot: '#FFE9A8', fog: '#CFD6E6', itemGlow: '#EAF4FF', itemHalo: '#9FD3FF',
    paper: '#F4EFE6', stamp: '#D83A4A', lens: '#E2FFFA',
    iron: '#4B5160', rivet: '#8A91A0', brass: '#D9A93F', wood: '#A0866B', woodShade: '#7A6652', woodRim: '#C2A98E',
    chain: ['#8A91A0', '#5B6170', '#B9C0CC'],
    sweat: '#a9dcff', sweatShade: '#74b8ea',
    iris: {
      blue: ['#4d5dae', '#6a78c8', '#8f9ce0'],
      gold: ['#B8860B', '#FFC83D', '#FFE58A'],
      rose: ['#d4475f', '#ef7d7f', '#ffbf9f'],
      green: ['#2f8a63', '#4fbf86', '#a6e8b8'],
      violet: ['#6a3fb0', '#9465d8', '#c7a6f2'],
      teal: ['#1f7d8c', '#36b2bd', '#9fe6e6'],
      grey: ['#5d5a66', '#8a8794', '#c4c1cc'],
      red: ['#8e1f2e', '#c8323f', '#f07a6a'],
    },
  };

  // ---------------------------------------------------------------- shapes
  function paint(ctx, fill, stroke, lw) {
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 2; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
  }
  SFX.paint = paint;

  SFX.addRoundRect = (ctx, x, y, w, h, r = 0) => {
    if (w < 0) { x += w; w = -w; }
    if (h < 0) { y += h; h = -h; }
    let [tl, tr, br, bl] = Array.isArray(r) ? [r[0], r[1] ?? r[0], r[2] ?? r[0], r[3] ?? r[1] ?? r[0]] : [r, r, r, r];
    const m = Math.min(w, h) / 2;
    tl = clamp(tl, 0, m); tr = clamp(tr, 0, m); br = clamp(br, 0, m); bl = clamp(bl, 0, m);
    ctx.moveTo(x + tl, y);
    ctx.lineTo(x + w - tr, y); if (tr) ctx.arc(x + w - tr, y + tr, tr, -Math.PI / 2, 0);
    ctx.lineTo(x + w, y + h - br); if (br) ctx.arc(x + w - br, y + h - br, br, 0, Math.PI / 2);
    ctx.lineTo(x + bl, y + h); if (bl) ctx.arc(x + bl, y + h - bl, bl, Math.PI / 2, Math.PI);
    ctx.lineTo(x, y + tl); if (tl) ctx.arc(x + tl, y + tl, tl, Math.PI, Math.PI * 1.5);
    ctx.closePath();
  };
  SFX.roundRect = (ctx, x, y, w, h, r, fill, stroke, lw) => { ctx.beginPath(); SFX.addRoundRect(ctx, x, y, w, h, r); paint(ctx, fill, stroke, lw); };

  SFX.addCapsule = (ctx, x1, y1, x2, y2, w1, w2 = w1) => {
    const r1 = Math.max(0.01, w1 / 2), r2 = Math.max(0.01, w2 / 2), dx = x2 - x1, dy = y2 - y1, d = Math.hypot(dx, dy);
    if (d <= Math.abs(r1 - r2) + 1e-6) {
      const [cx, cy, r] = r1 >= r2 ? [x1, y1, r1] : [x2, y2, r2];
      ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, TAU); ctx.closePath(); return;
    }
    const a = Math.atan2(dy, dx), phi = Math.acos(clamp((r1 - r2) / d, -1, 1));
    ctx.moveTo(x1 + r1 * Math.cos(a + phi), y1 + r1 * Math.sin(a + phi));
    ctx.arc(x1, y1, r1, a + phi, a + TAU - phi);
    ctx.arc(x2, y2, r2, a - phi, a + phi);
    ctx.closePath();
  };
  SFX.capsule = (ctx, x1, y1, x2, y2, w1, w2, fill, stroke, lw) => { ctx.beginPath(); SFX.addCapsule(ctx, x1, y1, x2, y2, w1, w2 ?? w1); paint(ctx, fill, stroke, lw); };
  SFX.addLimb = (ctx, pts, widths) => {
    const P = pts.map(xy), W = Array.isArray(widths) ? widths : P.map(() => widths);
    for (let i = 0; i < P.length - 1; i++) SFX.addCapsule(ctx, P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], W[i], W[i + 1] ?? W[i]);
  };
  SFX.limb = (ctx, pts, widths, fill, stroke, lw) => { ctx.beginPath(); SFX.addLimb(ctx, pts, widths); paint(ctx, fill, stroke, lw); };

  SFX.addBlob = (ctx, pts, tension = 0.5) => {
    const P = pts.map(xy), n = P.length;
    if (n < 3) return;
    const k = tension / 3;
    ctx.moveTo(P[0][0], P[0][1]);
    for (let i = 0; i < n; i++) {
      const p0 = P[(i - 1 + n) % n], p1 = P[i], p2 = P[(i + 1) % n], p3 = P[(i + 2) % n];
      ctx.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k, p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k, p2[0], p2[1]);
    }
    ctx.closePath();
  };
  SFX.blob = (ctx, pts, fill, tension = 0.5, stroke, lw) => { ctx.beginPath(); SFX.addBlob(ctx, pts, tension); paint(ctx, fill, stroke, lw); };
  SFX.addCurve = (ctx, pts, tension = 0.5, moveFirst = true) => {
    const P = pts.map(xy), n = P.length;
    if (!n) return;
    if (moveFirst) ctx.moveTo(P[0][0], P[0][1]); else ctx.lineTo(P[0][0], P[0][1]);
    if (n === 2) { ctx.lineTo(P[1][0], P[1][1]); return; }
    const k = tension / 3;
    for (let i = 0; i < n - 1; i++) {
      const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(n - 1, i + 2)];
      ctx.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k, p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k, p2[0], p2[1]);
    }
  };
  SFX.curve = (ctx, pts, color, lw = 3, tension = 0.5) => { ctx.beginPath(); SFX.addCurve(ctx, pts, tension); paint(ctx, null, color, lw); };
  SFX.addPoly = (ctx, pts, close = true) => {
    const P = pts.map(xy);
    P.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    if (close) ctx.closePath();
  };
  SFX.poly = (ctx, pts, fill, stroke, lw) => { ctx.beginPath(); SFX.addPoly(ctx, pts); paint(ctx, fill, stroke, lw); };
  SFX.addRoundPoly = (ctx, pts, r = 6) => {
    const P = pts.map(xy), n = P.length;
    const R = Array.isArray(r) ? r : P.map(() => r);
    const m0 = [(P[n - 1][0] + P[0][0]) / 2, (P[n - 1][1] + P[0][1]) / 2];
    ctx.moveTo(m0[0], m0[1]);
    for (let i = 0; i < n; i++) {
      const pv = P[(i - 1 + n) % n], c = P[i], nx = P[(i + 1) % n];
      const lim = Math.min(Math.hypot(c[0] - pv[0], c[1] - pv[1]), Math.hypot(nx[0] - c[0], nx[1] - c[1])) * 0.5;
      ctx.arcTo(c[0], c[1], nx[0], nx[1], Math.min(R[i] || 0, lim));
    }
    ctx.closePath();
  };
  SFX.roundPoly = (ctx, pts, r, fill, stroke, lw) => { ctx.beginPath(); SFX.addRoundPoly(ctx, pts, r); paint(ctx, fill, stroke, lw); };
  SFX.circle = (ctx, x, y, r, fill, stroke, lw) => { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, TAU); paint(ctx, fill, stroke, lw); };
  SFX.ellipse = (ctx, x, y, rx, ry, rot = 0, fill, stroke, lw) => { ctx.beginPath(); ctx.ellipse(x, y, Math.max(0, rx), Math.max(0, ry), rot, 0, TAU); paint(ctx, fill, stroke, lw); };

  // polyline machinery (used by strips, the eye, chains)
  function normalsOf(P) { // outward = (ty, -tx): points LEFT of the travel direction on screen (up for a left->right line)
    const n = P.length, out = new Array(n);
    for (let i = 0; i < n; i++) {
      const p = P[Math.max(0, i - 1)], q = P[Math.min(n - 1, i + 1)];
      const tx = q[0] - p[0], ty = q[1] - p[1], l = Math.hypot(tx, ty) || 1;
      out[i] = [ty / l, -tx / l];
    }
    return out;
  }
  function arcU(P) {
    const U = [0];
    for (let i = 1; i < P.length; i++) U.push(U[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
    const L = U[U.length - 1] || 1;
    return U.map(u => u / L);
  }
  function ribbon(ctx, P, offA, offB) { // closed ribbon between two signed normal offsets (number | fn(u,i) | array)
    const N = normalsOf(P), U = arcU(P), n = P.length;
    const f = (o, i) => (typeof o === 'function' ? o(U[i], i) : Array.isArray(o) ? o[i] : o);
    for (let i = 0; i < n; i++) { const o = f(offA, i); const X = P[i][0] + N[i][0] * o, Y = P[i][1] + N[i][1] * o; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); }
    for (let i = n - 1; i >= 0; i--) { const o = f(offB, i); ctx.lineTo(P[i][0] + N[i][0] * o, P[i][1] + N[i][1] * o); }
    ctx.closePath();
  }
  function offsetPts(P, off) {
    const N = normalsOf(P), U = arcU(P);
    return P.map((p, i) => { const o = typeof off === 'function' ? off(U[i], i) : Array.isArray(off) ? off[i] : off; return [p[0] + N[i][0] * o, p[1] + N[i][1] * o]; });
  }
  function slicePts(P, u0, u1) { // sub-polyline between arc fractions
    const U = arcU(P), out = [];
    const at = u => { for (let i = 1; i < P.length; i++) if (U[i] >= u) { const k = (u - U[i - 1]) / ((U[i] - U[i - 1]) || 1); return [lerp(P[i - 1][0], P[i][0], k), lerp(P[i - 1][1], P[i][1], k)]; } return P[P.length - 1].slice(); };
    out.push(at(u0));
    for (let i = 0; i < P.length; i++) if (U[i] > u0 && U[i] < u1) out.push(P[i]);
    out.push(at(u1));
    return out;
  }
  function pointAt(P, u) { return slicePts(P, u, u)[0]; }
  SFX._poly = { normalsOf, arcU, ribbon, offsetPts, slicePts, pointAt };

  SFX.strip = (ctx, pts, width, fill) => {
    const P = pts.map(xy);
    const half = typeof width === 'function' ? (u, i) => width(u, i) / 2 : width / 2;
    ctx.beginPath();
    ribbon(ctx, P, typeof half === 'function' ? (u, i) => -half(u, i) : -half, half);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  };
  SFX.clip = (ctx, pathFn, drawFn) => { ctx.save(); ctx.beginPath(); pathFn(ctx); ctx.clip(); drawFn(ctx); ctx.restore(); };
  SFX.cel = (ctx, pathFn, base, shade, dx = 8, dy = dx) => {
    ctx.beginPath(); pathFn(ctx); ctx.fillStyle = base; ctx.fill();
    if (!shade) return;
    ctx.save(); ctx.clip();
    ctx.beginPath(); ctx.rect(-1e5, -1e5, 2e5, 2e5);
    ctx.translate(-dx, -dy); pathFn(ctx); ctx.translate(dx, dy);
    ctx.fillStyle = shade; ctx.fill('evenodd');
    ctx.restore();
  };

  // ---------------------------------------------------------------- offscreen layers, groups
  const _pool = [];
  let _depth = 0;
  function acquire(w, h) {
    let c = _pool[_depth];
    if (!c) { c = document.createElement('canvas'); c.width = 8; c.height = 8; _pool[_depth] = c; }
    if (c.width < w || c.height < h) { c.width = Math.max(c.width, w); c.height = Math.max(c.height, h); }
    _depth++;
    const g = c.getContext('2d');
    if (g.reset) g.reset();
    else { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.shadowColor = 'rgba(0,0,0,0)'; g.shadowBlur = 0; }
    g.clearRect(0, 0, w, h);
    return c;
  }
  SFX.layer = (ctx, drawFn, bounds, pad = 6) => {
    const m = ctx.getTransform(), cw = ctx.canvas.width, ch = ctx.canvas.height;
    let x0 = 0, y0 = 0, x1 = cw, y1 = ch;
    if (bounds) {
      const xs = [], ys = [];
      for (const [bx, by] of [[bounds.x, bounds.y], [bounds.x + bounds.w, bounds.y], [bounds.x, bounds.y + bounds.h], [bounds.x + bounds.w, bounds.y + bounds.h]]) {
        xs.push(m.a * bx + m.c * by + m.e); ys.push(m.b * bx + m.d * by + m.f);
      }
      x0 = Math.max(0, Math.floor(Math.min(...xs) - pad)); y0 = Math.max(0, Math.floor(Math.min(...ys) - pad));
      x1 = Math.min(cw, Math.ceil(Math.max(...xs) + pad)); y1 = Math.min(ch, Math.ceil(Math.max(...ys) + pad));
    }
    const w = x1 - x0, h = y1 - y0;
    if (w <= 0 || h <= 0) return null;
    const c = acquire(w, h), g = c.getContext('2d');
    g.setTransform(m.a, m.b, m.c, m.d, m.e - x0, m.f - y0);
    let released = false;
    try { drawFn(g); } catch (e) { _depth--; released = true; throw e; }
    return { canvas: c, x: x0, y: y0, w, h, release() { if (!released) { released = true; _depth--; } } };
  };
  function blit(ctx, L, setup) {
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (setup) setup(ctx);
    ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x, L.y, L.w, L.h);
    ctx.restore();
  }
  SFX.shadowGroup = (ctx, drawFn, o = {}) => {
    const L = SFX.layer(ctx, drawFn, o.bounds);
    if (!L) return;
    const s = o.scale ?? 1;
    blit(ctx, L, c => {
      if (o.shadow !== false) {
        c.shadowColor = o.color || 'rgba(0,0,0,0.45)';
        c.shadowBlur = (o.blur ?? 20) * s;
        c.shadowOffsetX = (o.dx ?? 8) * s;
        c.shadowOffsetY = (o.dy ?? 8) * s;
      }
      c.globalAlpha *= o.alpha ?? 1;
    });
    L.release();
  };
  SFX.glow = (ctx, drawFn, o = {}) => {
    const L = SFX.layer(ctx, drawFn, o.bounds, (o.blur ?? 12) * 3);
    if (!L) return;
    blit(ctx, L, c => { c.globalAlpha *= o.crispAlpha ?? 1; });
    blit(ctx, L, c => { c.globalCompositeOperation = 'lighter'; c.filter = `blur(${o.blur ?? 12}px)`; c.globalAlpha *= o.alpha ?? 0.8; });
    if (o.wide !== false) blit(ctx, L, c => { c.globalCompositeOperation = 'lighter'; c.filter = `blur(${(o.blur ?? 12) * 3}px)`; c.globalAlpha *= (o.alpha ?? 0.8) * 0.45; });
    L.release();
  };
  SFX.groundShadow = (ctx, x, y, w, h, alpha = 0.5) => {
    h = h ?? w * 0.16;
    ctx.save(); ctx.translate(x, y); ctx.scale(1, h / w);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, w / 2);
    g.addColorStop(0, `rgba(0,0,0,${alpha})`); g.addColorStop(0.55, `rgba(0,0,0,${alpha * 0.75})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, w / 2, 0, TAU); ctx.fill();
    ctx.restore();
  };

  const _grain = {};
  function grainTile(seed) {
    const key = ((seed % 12) + 12) % 12;
    if (_grain[key]) return _grain[key];
    const S = 256, c = document.createElement('canvas'); c.width = S; c.height = S;
    const g = c.getContext('2d'), im = g.createImageData(S, S), r = SFX.rng(1000 + key);
    for (let i = 0; i < S * S; i++) { const v = clamp(128 + r.gauss() * 46, 0, 255); im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
    g.putImageData(im, 0, 0);
    return (_grain[key] = c);
  }
  SFX.grain = (ctx, amount = 0.06, seed = 1) => {
    const tile = grainTile(Math.floor(seed)), r = SFX.rng(seed + 7);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = clamp(amount * 2.2);
    const p = ctx.createPattern(tile, 'repeat');
    ctx.translate(-Math.floor(r() * 256), -Math.floor(r() * 256));
    ctx.fillStyle = p; ctx.fillRect(0, 0, ctx.canvas.width + 256, ctx.canvas.height + 256);
    ctx.restore();
  };
  SFX.vignette = (ctx, strength = 0.55, o = {}) => {
    const W = ctx.canvas.width, H = ctx.canvas.height, cx = o.cx ?? W / 2, cy = o.cy ?? H / 2, R = Math.hypot(W, H) / 2;
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.translate(cx, cy); ctx.scale(1, (o.aspect ?? H / W) * 1.25);
    const g = ctx.createRadialGradient(0, 0, R * (o.inner ?? 0.45), 0, 0, R * (o.outer ?? 1.05));
    const col = o.color || '#000';
    g.addColorStop(0, C.rgba(col, 0)); g.addColorStop(0.6, C.rgba(col, strength * 0.55)); g.addColorStop(1, C.rgba(col, strength));
    ctx.fillStyle = g; ctx.fillRect(-W * 2, -H * 4, W * 4, H * 8);
    ctx.restore();
  };
  SFX.scanlines = (ctx, x, y, w, h, gap = 4, alpha = 0.16, color = '#000') => {
    ctx.save(); ctx.fillStyle = C.rgba(color, alpha);
    for (let yy = y; yy < y + h; yy += gap) ctx.fillRect(x, yy, w, Math.max(1, gap * 0.45));
    ctx.restore();
  };

  // ---------------------------------------------------------------- the eye (plan 3-2)
  function cubicPts(p0, p1, p2, p3, n, out, skipFirst) {
    for (let i = skipFirst ? 1 : 0; i <= n; i++) {
      const t = i / n, u = 1 - t, a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
      out.push([a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]]);
    }
    return out;
  }
  function quadPts(p0, c, p2, n) {
    const out = [];
    for (let i = 0; i <= n; i++) { const t = i / n, u = 1 - t; out.push([u * u * p0[0] + 2 * u * t * c[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p2[1]]); }
    return out;
  }
  const EN = 24; // samples per half curve
  // Eye outline in local units: outer corner on the LEFT (-a), inner corner on the right (+a), a = w/2, b = eye height/2.
  // top and bottom both run outer -> inner with the same sample count so they can be blended point by point.
  function eyeOutline(a, b) {
    const O = [-a, -0.22 * b], T = [-0.08 * a, -b], I = [a, 0.1 * b], B = [0.04 * a, b];
    const top = [], bot = [];
    cubicPts(O, [-0.84 * a, -0.74 * b], [-0.5 * a, -b], T, EN, top);
    cubicPts(T, [0.42 * a, -b], [a, -0.6 * b], I, EN, top, true);
    cubicPts(O, [-0.93 * a, 0.42 * b], [-0.56 * a, b], B, EN, bot);
    cubicPts(B, [0.62 * a, b], [a, 0.74 * b], I, EN, bot, true);
    return { top, bot, O, I };
  }
  const mixPts = (P, Q, k) => P.map((p, i) => [lerp(p[0], Q[i][0], k), lerp(p[1], Q[i][1], k)]);
  const sstep = k => { k = clamp(k); return k * k * (3 - 2 * k); };
  function bandProfile(s) { // lid band thickness along the lid, outer (0) -> inner (1)
    if (s < 0.25) return lerp(1.05, 1.16, sstep(s / 0.25));
    if (s < 0.65) return lerp(1.16, 1.0, sstep((s - 0.25) / 0.4));
    return lerp(1.0, 0.86, sstep((s - 0.65) / 0.35));
  }
  function yOnPolyAt(P, x) { // y of a left->right-ish polyline at x
    for (let i = 1; i < P.length; i++) {
      const p = P[i - 1], q = P[i];
      if ((p[0] - x) * (q[0] - x) <= 0 && p[0] !== q[0]) return lerp(p[1], q[1], (x - p[0]) / (q[0] - p[0]));
    }
    return null;
  }
  function lashPath(ctx, base, tan, nrmv, len, bw, lean, curl) {
    // a thin curved spike: rises along the normal, leans toward the outer corner (-tan) and curls further at the tip
    const d1 = [nrmv[0] * Math.cos(lean) - tan[0] * Math.sin(lean), nrmv[1] * Math.cos(lean) - tan[1] * Math.sin(lean)];
    const l2 = lean + curl, d2 = [nrmv[0] * Math.cos(l2) - tan[0] * Math.sin(l2), nrmv[1] * Math.cos(l2) - tan[1] * Math.sin(l2)];
    const mid = [base[0] + d1[0] * len * 0.55, base[1] + d1[1] * len * 0.55];
    const tip = [mid[0] + d2[0] * len * 0.5, mid[1] + d2[1] * len * 0.5];
    const p = [-d1[1], d1[0]], sg = p[0] * tan[0] + p[1] * tan[1] > 0 ? 1 : -1;
    const b1 = [base[0] + tan[0] * bw, base[1] + tan[1] * bw], b2 = [base[0] - tan[0] * bw, base[1] - tan[1] * bw];
    const c1 = [mid[0] + p[0] * sg * bw * 0.45, mid[1] + p[1] * sg * bw * 0.45], c2 = [mid[0] - p[0] * sg * bw * 0.45, mid[1] - p[1] * sg * bw * 0.45];
    ctx.moveTo(b1[0], b1[1]);
    ctx.quadraticCurveTo(c1[0], c1[1], tip[0], tip[1]);
    ctx.quadraticCurveTo(c2[0], c2[1], b2[0], b2[1]);
    ctx.closePath();
  }
  function toothPath(ctx, base, tan, nrmv, len, bw, lean) { // small triangle hanging off a line along -normal
    const d = [-nrmv[0] * Math.cos(lean) - tan[0] * Math.sin(lean), -nrmv[1] * Math.cos(lean) - tan[1] * Math.sin(lean)];
    ctx.moveTo(base[0] + tan[0] * bw, base[1] + tan[1] * bw);
    ctx.lineTo(base[0] + d[0] * len, base[1] + d[1] * len);
    ctx.lineTo(base[0] - tan[0] * bw, base[1] - tan[1] * bw);
    ctx.closePath();
  }
  function tangentsOf(P) { const N = normalsOf(P); return N.map(n => [-n[1], n[0]]); } // travel direction

  function starPath(ctx, cx, cy, rx, ry, pinch) {
    for (let i = 0; i < 4; i++) {
      const a0 = -Math.PI / 2 + i * Math.PI / 2, a1 = a0 + Math.PI / 2, am = a0 + Math.PI / 4;
      const p0 = [cx + Math.cos(a0) * rx, cy + Math.sin(a0) * ry], p1 = [cx + Math.cos(a1) * rx, cy + Math.sin(a1) * ry];
      const c = [cx + Math.cos(am) * Math.min(rx, ry) * pinch, cy + Math.sin(am) * Math.min(rx, ry) * pinch];
      if (i === 0) ctx.moveTo(p0[0], p0[1]);
      ctx.quadraticCurveTo(c[0], c[1], p1[0], p1[1]);
    }
    ctx.closePath();
  }
  function heartPath(ctx, cx, cy, s) {
    ctx.moveTo(cx, cy + s * 0.55);
    ctx.bezierCurveTo(cx - s * 0.9, cy - s * 0.05, cx - s * 0.5, cy - s * 0.75, cx, cy - s * 0.3);
    ctx.bezierCurveTo(cx + s * 0.5, cy - s * 0.75, cx + s * 0.9, cy - s * 0.05, cx, cy + s * 0.55);
    ctx.closePath();
  }

  function eyePalette(o) {
    const P = SFX.PAL;
    if (!o.glow) {
      const iris = o.iris || P.iris.blue;
      return {
        ink: o.ink || P.ink, sclera: o.sclera || P.sclera, crease: o.creaseColor || P.crease, iris,
        pupil: o.pupilColor || (o.pupil === 'star' || o.pupil === 'heart' ? C.mix(iris[iris.length - 1], '#ffffff', 0.72) : C.shade(iris[0], -0.42)),
        hi: '#ffffff', lidShade: `rgba(52,30,70,${o.lidShade ?? 0})`, lowerCrease: C.rgba(o.creaseColor || P.crease, 0.75),
      };
    }
    const g = o.glowColor || '#8ff7ff';
    return {
      ink: C.mix(g, '#ffffff', 0.5), sclera: C.rgba(g, 0.16), crease: C.rgba(g, 0.55),
      iris: o.iris || [C.shade(g, -0.25), g, C.mix(g, '#ffffff', 0.5)],
      pupil: o.pupilColor || o.screen || '#06090c', hi: '#ffffff', lidShade: null, lowerCrease: C.rgba(g, 0.35),
    };
  }

  function drawEyeCore(ctx, o, pal) {
    const w = o.w, a = w / 2, h = o.h ?? 0.6, b = (w * h) / 2, H0 = w * 0.6;
    const sx = o.mirror ? -1 : 1;
    const m = ctx.getTransform(), dev = Math.hypot(m.a, m.b) || 1, px = 1 / dev; // one device pixel in local units
    const hs = sx * ((m.a * m.d - m.b * m.c) < 0 ? -1 : 1); // keeps the highlight on the SCREEN left even in a flipped rig
    const thick = (o.lid ?? 0.15) * H0;
    ctx.save();
    ctx.translate(o.x, o.y);
    ctx.scale(sx, 1);
    ctx.rotate(o.tilt || 0);
    const { top, bot } = eyeOutline(a, b);
    const closedMode = o.closed || ((o.open ?? 1) < 0.12 ? 'flat' : false);
    if (closedMode) { drawClosed(ctx, o, a, b, H0, thick, pal, closedMode, top, bot, px); ctx.restore(); return { ix: o.x, iy: o.y, ir: 0 }; }

    const open = clamp(o.open ?? 1);
    // closing target: the bottom curve, flattened toward the corner-to-corner chord on the inner side so a
    // half-closed lid does not hook up the rounded inner corner
    const Mt = top.length - 1;
    const closedT = bot.map((p, i) => { const sN = i / Mt, k = SFX.smoothstep(0.45, 1, sN) * 0.85; return [p[0], lerp(p[1], lerp(top[0][1], top[Mt][1], sN), k)]; });
    const lid = mixPts(top, closedT, (1 - open) * 0.94);
    const botR = (o.lowerRaise || 0) > 0 ? mixPts(bot, lid, clamp(o.lowerRaise) * 0.42) : bot;
    const M = lid.length - 1;
    const visible = c => { c.moveTo(lid[0][0], lid[0][1]); for (let i = 1; i <= M; i++) c.lineTo(lid[i][0], lid[i][1]); for (let i = M; i >= 0; i--) c.lineTo(botR[i][0], botR[i][1]); c.closePath(); };

    // 0. eerie dark circle (behind everything)
    if (o.darkCircle > 0 && !o.glow) {
      const dc = slicePts(botR, 0.06, 0.9);
      ctx.beginPath(); ribbon(ctx, dc, u => -0.025 * w, u => -(0.025 * w + 0.1 * w * Math.sin(Math.PI * u) ** 0.8));
      ctx.fillStyle = `rgba(70,40,85,${0.32 * clamp(o.darkCircle)})`; ctx.fill();
    }
    // 1. sclera
    ctx.beginPath(); visible(ctx); ctx.fillStyle = pal.sclera; ctx.fill();
    // 2-4. iris, pupil, highlight, tears, lid shade (clipped to the visible white)
    const lookX = clamp((o.look && o.look.x) || 0, -1, 1) * sx, lookY = clamp((o.look && o.look.y) || 0, -1, 1);
    const isDot = o.irisScale === 'dot';
    const irisScale = isDot ? 0.2 : (o.irisScale ?? 0.62);
    const r = irisScale * a, ry = r * (o.irisStretch ?? 1.06);
    const maxDx = (a - r) * 0.9 + 0.1 * a;
    const icx = lookX * maxDx, icy = ((o.irisY ?? -0.1) * 2 * b) + lookY * 0.36 * b;
    ctx.save();
    ctx.beginPath(); visible(ctx); ctx.clip();
    if (isDot) {
      const dr = 0.085 * w * (o.pupilScale ?? 1), dcy = icy + 0.12 * b;
      ctx.beginPath(); ctx.ellipse(icx, dcy, dr, dr * 1.12, 0, 0, TAU); ctx.fillStyle = o.glow ? pal.iris[2] : (o.pupilColor || C.shade(pal.iris[0], -0.6)); ctx.fill();
      if (o.highlight !== false) { ctx.beginPath(); ctx.ellipse(icx - 0.38 * dr * hs, dcy - 0.4 * dr, dr * 0.3, dr * 0.26, -0.5 * hs, 0, TAU); ctx.fillStyle = pal.hi; ctx.fill(); }
    } else {
      const cs = pal.iris, n = cs.length;
      ctx.beginPath(); ctx.ellipse(icx, icy, r, ry, 0, 0, TAU); ctx.fillStyle = cs[0]; ctx.fill();
      ctx.save(); ctx.beginPath(); ctx.ellipse(icx, icy, r, ry, 0, 0, TAU); ctx.clip();
      const fr = n === 2 ? [0.56] : n === 3 ? [0.47, 0.73] : [0.42, 0.61, 0.8];
      const bow = (o.irisBow ?? 0.12) * ry;
      for (let k = 1; k < n; k++) {
        const y0 = icy - ry + 2 * ry * fr[k - 1];
        ctx.beginPath(); ctx.moveTo(icx - r - 2, y0);
        for (let j = 0; j <= 16; j++) { const t = -1 + j / 8, yy = y0 + bow * (1 - t * t); ctx.lineTo(icx + t * r, yy); }
        ctx.lineTo(icx + r + 2, y0); ctx.lineTo(icx + r + 2, icy + ry + 2); ctx.lineTo(icx - r - 2, icy + ry + 2); ctx.closePath();
        ctx.fillStyle = cs[k]; ctx.fill();
      }
      if (o.irisRing) { ctx.beginPath(); ctx.ellipse(icx, icy, r * 0.84, ry * 0.84, 0, 0, TAU); ctx.strokeStyle = C.rgba(C.shade(cs[0], -0.3), o.irisRing); ctx.lineWidth = Math.max(px, 0.02 * w); ctx.stroke(); }
      // pupil
      const ps = o.pupilScale ?? 1, pcx = icx, pcy = icy - 0.06 * ry, pupil = o.pupil || 'oval';
      ctx.fillStyle = pal.pupil; ctx.beginPath();
      if (pupil === 'oval') ctx.ellipse(pcx, pcy, 0.3 * r * ps, 0.46 * ry * ps, 0, 0, TAU);
      else if (pupil === 'dot') ctx.arc(pcx, pcy + 0.04 * ry, 0.2 * r * ps, 0, TAU);
      else if (pupil === 'slit') { const hh = 0.8 * ry * Math.min(1.2, 0.6 + 0.4 * ps), hw = 0.11 * r * ps; ctx.moveTo(pcx, pcy - hh); ctx.quadraticCurveTo(pcx + hw * 2, pcy, pcx, pcy + hh); ctx.quadraticCurveTo(pcx - hw * 2, pcy, pcx, pcy - hh); ctx.closePath(); }
      else if (pupil === 'star') starPath(ctx, pcx, pcy + 0.04 * ry, 0.66 * r * ps, 0.6 * ry * ps, 0.1);
      else if (pupil === 'heart') heartPath(ctx, pcx, pcy + 0.06 * ry, 0.62 * r * ps);
      if (pupil !== 'swirl' && pupil !== 'none') ctx.fill();
      if (pupil === 'swirl') {
        ctx.beginPath();
        const turns = 2.6, R = 0.92 * r;
        for (let j = 0; j <= 120; j++) { const t = j / 120, ang = t * turns * TAU * sx, rr = 0.06 * r + (R - 0.06 * r) * t; const X = pcx + Math.cos(ang) * rr, Y = icy + Math.sin(ang) * rr * (ry / r); j ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); }
        ctx.strokeStyle = pal.pupil; ctx.lineWidth = 0.12 * r; ctx.lineCap = 'round'; ctx.stroke();
      }
      ctx.restore();
      // highlight: always screen upper-left
      if (o.highlight !== false && pupil !== 'swirl') {
        const hr = (o.highlightSize ?? 0.13) * r;
        const hx = icx - 0.4 * r * hs;
        let hy = icy - 0.3 * ry;
        const ly = yOnPolyAt(lid, hx);
        if (ly !== null) hy = Math.max(hy, ly + hr * 1.7);
        ctx.beginPath(); ctx.ellipse(hx, hy, hr * 1.18, hr, -0.55 * hs, 0, TAU); ctx.fillStyle = pal.hi; ctx.fill();
        if (o.highlight2) { ctx.beginPath(); ctx.arc(icx + 0.36 * r * hs, icy + 0.42 * ry, hr * 0.45, 0, TAU); ctx.fill(); }
      }
    }
    // tears welling up from the bottom
    if (o.tears > 0 && !o.glow) {
      const lvl = clamp(o.tears), yTop = b - lvl * 0.75 * b;
      ctx.beginPath(); ctx.moveTo(-a * 1.1, yTop);
      for (let j = 0; j <= 48; j++) { const x = -a * 1.1 + (2.2 * a * j) / 48; ctx.lineTo(x, yTop + Math.sin(j * 0.55 + (o.t || 0) * 6) * 0.014 * w); }
      ctx.lineTo(a * 1.1, b * 1.2); ctx.lineTo(-a * 1.1, b * 1.2); ctx.closePath();
      ctx.fillStyle = 'rgba(160,212,255,0.78)'; ctx.fill();
      ctx.beginPath(); ctx.ellipse(-0.35 * a * sx, yTop + 0.06 * w, 0.14 * w, 0.014 * w, 0, 0, TAU); ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.fill();
    }
    // one hard shade band right under the upper lid (sclera and iris top)
    if (pal.lidShade && (o.lidShade ?? 0) > 0) {
      ctx.beginPath(); ribbon(ctx, lid, u => -1 * px, u => -(0.16 * b + 0.05 * w) * Math.sin(Math.PI * clamp(u * 1.05)) ** 0.6);
      ctx.fillStyle = pal.lidShade; ctx.fill();
    }
    ctx.restore();

    // 5. lower lid: faint crease, the line, tiny teeth
    const lowLen = o.lower ?? 0.66;
    if (lowLen > 0) {
      const gap = 0.012 * w;
      const lowPts = offsetPts(slicePts(botR, 0, lowLen), -gap); // bottom runs outer->inner, its "left" normal points into the eye, so negative = outside
      if (o.lowerCrease !== false) {
        const lc = offsetPts(slicePts(botR, 0.12, Math.min(0.92, lowLen + 0.18)), -(gap + 0.045 * w));
        SFX.strip(ctx, lc, u => Math.max(px * 1.1, 0.008 * w) * Math.sin(Math.PI * u) ** 0.5, pal.lowerCrease);
      }
      const lw = Math.max(px * 1.6, 0.022 * w);
      SFX.strip(ctx, lowPts, u => lw * (u < 0.12 ? lerp(1.5, 1, u / 0.12) : u < 0.72 ? 1 : Math.max(0, (1 - u) / 0.28) ** 0.7), pal.ink);
      const nt = Math.round(o.teeth ?? 3);
      if (nt > 0) {
        const N = normalsOf(lowPts), T = tangentsOf(lowPts), U = arcU(lowPts);
        ctx.beginPath();
        for (let j = 0; j < nt; j++) {
          const u = nt === 1 ? 0.4 : lerp(0.16, 0.66, j / (nt - 1));
          let i = U.findIndex(v => v >= u); if (i < 0) i = U.length - 1;
          const nn = [-N[i][0], -N[i][1]]; // outward (down)
          const base = [lowPts[i][0] + nn[0] * lw * 0.3, lowPts[i][1] + nn[1] * lw * 0.3];
          toothPath(ctx, base, T[i], [-nn[0], -nn[1]], 0.075 * w * (j % 2 ? 0.78 : 1), 0.021 * w, 0.22);
        }
        ctx.fillStyle = pal.ink; ctx.fill();
      }
    }

    // 6. crease lines above the lid band
    const nCrease = o.crease ?? 2;
    if (nCrease > 0) {
      const base = mixPts(top, lid, 0.4);
      for (let c = 0; c < nCrease; c++) {
        const u0 = c ? 0.28 : 0.12, u1 = c ? 0.74 : 0.9, off = thick * 1.16 + (0.024 + c * 0.026) * w;
        const cp = offsetPts(slicePts(base, u0, u1), off);
        SFX.strip(ctx, cp, u => Math.max(px * 1.1, (c ? 0.0065 : 0.009) * w) * Math.sin(Math.PI * u) ** 0.5, pal.crease);
      }
    }

    // 7. the heavy upper-lid band: along the lid, wrapping down the inner corner, with the pointed outer wing
    const wrapN = Math.max(0, Math.round(EN * 2 * (o.innerWrap ?? 0.15) * SFX.smoothstep(0.3, 0.85, open)));
    const S = lid.slice();
    for (let j = 1; j <= wrapN; j++) S.push(botR[M - j]);
    const endK = lerp(0.55, 1, SFX.smoothstep(0.3, 0.85, open));
    const prof = S.map((p, i) => i <= M ? thick * bandProfile(i / M) * (i / M > 0.7 ? lerp(1, endK, (i / M - 0.7) / 0.3) : 1) : thick * 0.86 * endK * (1 - (i - M) / wrapN) ** 0.9);
    ctx.beginPath(); ribbon(ctx, S, -0.6 * px, prof); ctx.fillStyle = pal.ink; ctx.fill();
    // wing
    const Nl = normalsOf(S), U0 = [S[0][0] + Nl[0][0] * prof[0], S[0][1] + Nl[0][1] * prof[0]];
    const o1 = [S[1][0] + Nl[1][0] * prof[1], S[1][1] + Nl[1][1] * prof[1]];
    const td = (() => { const dx = U0[0] - o1[0], dy = U0[1] - o1[1], l = Math.hypot(dx, dy) || 1; return [dx / l, dy / l]; })();
    const wl = (o.wing ?? 0.2) * w, wa = o.wingAngle ?? 0.3;
    const O = lid[0];
    const tip = [O[0] - Math.cos(wa) * wl, O[1] - Math.sin(wa) * wl];
    const dU = Math.hypot(tip[0] - U0[0], tip[1] - U0[1]);
    const bi = 3, bN = normalsOf(botR)[bi], below = [botR[bi][0] - bN[0] * 0.01 * w, botR[bi][1] - bN[1] * 0.01 * w];
    ctx.beginPath();
    ctx.moveTo(S[4][0], S[4][1]);
    ctx.lineTo(S[4][0] + Nl[4][0] * prof[4], S[4][1] + Nl[4][1] * prof[4]);
    ctx.lineTo(o1[0], o1[1]);
    ctx.lineTo(U0[0], U0[1]);
    ctx.quadraticCurveTo(U0[0] + td[0] * dU * 0.55, U0[1] + td[1] * dU * 0.55, tip[0], tip[1]);
    const mid = [lerp(tip[0], below[0], 0.5) + 0.07 * a, lerp(tip[1], below[1], 0.5) - 0.02 * b];
    ctx.quadraticCurveTo(mid[0], mid[1], below[0], below[1]);
    ctx.lineTo(O[0] + 0.02 * a, O[1]);
    ctx.closePath();
    ctx.fill();
    // lashes on top of the band, leaning to the outer corner
    const nl = Math.round(o.lashes ?? 3);
    if (nl > 0) {
      const lidOuter = S.slice(0, M + 1).map((p, i) => [p[0] + Nl[i][0] * prof[i], p[1] + Nl[i][1] * prof[i]]);
      const N2 = normalsOf(lidOuter), T2 = tangentsOf(lidOuter), U2 = arcU(lidOuter);
      const L = (o.lashLen ?? 0.32) * H0;
      ctx.beginPath();
      for (let j = 0; j < nl; j++) {
        const k = nl === 1 ? 0.5 : j / (nl - 1);
        const u = lerp(o.lashFrom ?? 0.07, o.lashTo ?? 0.5, k);
        let i = U2.findIndex(v => v >= u); if (i < 0) i = U2.length - 1;
        const bw = 0.024 * w;
        const base = [lidOuter[i][0] - N2[i][0] * bw * 1.2, lidOuter[i][1] - N2[i][1] * bw * 1.2];
        lashPath(ctx, base, T2[i], N2[i], L * lerp(1.0, 0.8, k), bw, lerp(1.0, 0.45, k), lerp(0.6, 0.45, k));
      }
      ctx.fillStyle = pal.ink; ctx.fill();
    }
    ctx.restore();
    // iris centre in parent coordinates
    const cos = Math.cos(o.tilt || 0), sin = Math.sin(o.tilt || 0);
    return { ix: o.x + sx * (icx * cos - icy * sin), iy: o.y + (icx * sin + icy * cos), ir: r };
  }

  function drawClosed(ctx, o, a, b, H0, thick, pal, mode, top, bot, px) {
    const w = 2 * a;
    let P;
    if (mode === 'smile') P = quadPts([-0.98 * a, 0.2 * b], [-0.06 * a, -1.05 * b], [0.92 * a, 0.3 * b], 2 * EN);
    else if (mode === 'sleep') P = quadPts([-a, -0.05 * b], [0, 0.95 * b], [0.94 * a, 0.0 * b], 2 * EN);
    else P = quadPts([-a, 0.1 * b], [-0.02 * a, 0.62 * b], [0.94 * a, 0.16 * b], 2 * EN);
    const th = thick * (mode === 'flat' ? 0.85 : 0.95);
    const prof = P.map((p, i) => th * bandProfile(i / (P.length - 1)) * (i === P.length - 1 ? 0.6 : 1));
    // crease
    if ((o.crease ?? 2) > 0) {
      const cp = offsetPts(slicePts(P, 0.14, 0.86), th * 1.12 + 0.05 * w);
      SFX.strip(ctx, cp, u => Math.max(px * 1.1, 0.01 * w) * Math.sin(Math.PI * u) ** 0.5, pal.crease);
    }
    // band
    ctx.beginPath(); ribbon(ctx, P, u => -0.18 * th * Math.sin(Math.PI * u), prof); ctx.fillStyle = pal.ink; ctx.fill();
    // wing
    const N = normalsOf(P), T = tangentsOf(P);
    const U0 = [P[0][0] + N[0][0] * prof[0], P[0][1] + N[0][1] * prof[0]];
    const wl = (o.wing ?? 0.2) * w, wa = (o.wingAngle ?? 0.3) + (mode === 'smile' ? 0.3 : mode === 'flat' ? -0.12 : 0.05);
    const tip = [P[0][0] - Math.cos(wa) * wl, P[0][1] - Math.sin(wa) * wl];
    const lo = [P[3][0] - N[3][0] * th * 0.2, P[3][1] - N[3][1] * th * 0.2];
    ctx.beginPath(); ctx.moveTo(P[3][0] + N[3][0] * prof[3], P[3][1] + N[3][1] * prof[3]); ctx.lineTo(U0[0], U0[1]);
    ctx.quadraticCurveTo(lerp(U0[0], tip[0], 0.5) - T[0][0] * 0.0, lerp(U0[1], tip[1], 0.5) - 0.02 * w, tip[0], tip[1]);
    ctx.quadraticCurveTo(lerp(tip[0], lo[0], 0.5) + 0.03 * w, lerp(tip[1], lo[1], 0.5) - 0.01 * w, lo[0], lo[1]);
    ctx.closePath(); ctx.fill();
    // lashes up
    const nl = Math.round(o.lashes ?? 3);
    if (nl > 0) {
      const outer = P.map((p, i) => [p[0] + N[i][0] * prof[i], p[1] + N[i][1] * prof[i]]);
      const N2 = normalsOf(outer), T2 = tangentsOf(outer), U2 = arcU(outer), L = (o.lashLen ?? 0.3) * H0;
      ctx.beginPath();
      for (let j = 0; j < nl; j++) {
        const k = nl === 1 ? 0.5 : j / (nl - 1), u = lerp(0.14, 0.6, k);
        let i = U2.findIndex(v => v >= u); if (i < 0) i = U2.length - 1;
        const bw = 0.02 * w, base = [outer[i][0] - N2[i][0] * bw * 1.2, outer[i][1] - N2[i][1] * bw * 1.2];
        lashPath(ctx, base, T2[i], N2[i], L * lerp(1, 0.85, k), bw, lerp(0.9, 0.4, k), 0.5);
      }
      ctx.fill();
    }
    // lower lashes (little teeth hanging under the closed lid)
    const nt = Math.round(o.teeth ?? 3);
    if (nt > 0) {
      const U = arcU(P);
      ctx.beginPath();
      for (let j = 0; j < nt; j++) {
        const u = nt === 1 ? 0.4 : lerp(0.2, 0.66, j / (nt - 1));
        let i = U.findIndex(v => v >= u); if (i < 0) i = U.length - 1;
        toothPath(ctx, [P[i][0] + N[i][0] * th * 0.1, P[i][1] + N[i][1] * th * 0.1], T[i], N[i], 0.06 * w * (j % 2 ? 0.8 : 1), 0.022 * w, 0.3);
      }
      ctx.fill();
    }
  }

  SFX.eye = (ctx, o) => {
    const pal = eyePalette(o);
    if (!o.glow) return drawEyeCore(ctx, o, pal);
    const w = o.w, hb = w * ((o.h ?? 0.6) * 0.5 + 0.35);
    let info = null;
    const blur = (o.glowBlur ?? 0.07) * w * Math.hypot(ctx.getTransform().a, ctx.getTransform().b);
    const L = SFX.layer(ctx, g => { info = drawEyeCore(g, o, pal); }, { x: o.x - w * 0.8, y: o.y - hb, w: w * 1.6, h: hb * 2 }, blur * 3 + 4);
    if (!L) return info;
    blit(ctx, L, c => { c.globalCompositeOperation = 'lighter'; c.filter = `blur(${blur * 2.6}px)`; c.globalAlpha *= 0.55; });
    blit(ctx, L, c => { c.globalCompositeOperation = 'lighter'; c.filter = `blur(${blur}px)`; c.globalAlpha *= 0.9; });
    blit(ctx, L, null);
    L.release();
    return info;
  };

  SFX.eyePair = (ctx, o) => {
    const w = o.w, gap = (o.gap ?? 0.34) * w, turn = clamp(o.turn || 0, -1, 1);
    const sL = 1 - 0.15 * Math.max(0, turn), sR = 1 - 0.15 * Math.max(0, -turn);
    const cx = o.x + turn * 0.12 * (2 * w + gap);
    const xl = cx - gap / 2 - (w * sL) / 2, xr = cx + gap / 2 + (w * sR) / 2;
    const base = Object.assign({}, o); delete base.L; delete base.R;
    const l = SFX.eye(ctx, Object.assign({}, base, { x: xl, w: w * sL, mirror: false }, o.L || {}));
    const r = SFX.eye(ctx, Object.assign({}, base, { x: xr, w: w * sR, mirror: true }, o.R || {}));
    return { L: l, R: r, xl, xr };
  };

  SFX.EXPR = {
    neutral: {},
    happy: { closed: 'smile' },
    content: { closed: 'smile', lashes: 3 },
    nervous: { irisScale: 0.3, pupil: 'slit', pupilScale: 0.7, h: 0.66 },
    greedy: { irisScale: 0.7, pupil: 'star', h: 0.66 },
    eerie: { irisScale: 0.6, highlight: false, darkCircle: 1, open: 0.82, iris: null },
    fear: { irisScale: 'dot', tears: 0.45, h: 0.74, open: 1 },
    bored: { open: 0.52, look: { x: 0.2, y: 0.25 } },
    shock: { h: 0.8, irisScale: 0.36, pupil: 'dot' },
    angry: { tilt: 0.2, open: 0.78, lowerRaise: 0.2 },
    sad: { tilt: -0.18, open: 0.85, look: { x: 0, y: 0.35 } },
    smug: { open: 0.62, lowerRaise: 0.35, irisScale: 0.5 },
    dizzy: { pupil: 'swirl', highlight: false },
    sleepy: { closed: 'sleep' },
  };
  Object.keys(SFX.EXPR).forEach(k => { const e = SFX.EXPR[k]; Object.keys(e).forEach(p => { if (e[p] === null) delete e[p]; }); });

  SFX.brow = (ctx, x, y, w, o = {}) => {
    const sx = o.mirror ? -1 : 1, tilt = o.tilt || 0, arch = o.arch ?? 0.15, th = (o.thick ?? 0.09) * w;
    // local: outer end at -w/2, inner at +w/2; tilt + lifts the inner end
    const pts = [];
    for (let j = 0; j <= 16; j++) { const u = j / 16, X = (u - 0.5) * w; pts.push([X, -arch * w * Math.sin(Math.PI * u) - tilt * w * (u - 0.5)]); }
    ctx.save(); ctx.translate(x, y); ctx.scale(sx, 1);
    SFX.strip(ctx, pts, u => th * (0.35 + 0.65 * Math.sin(Math.PI * clamp(u * 0.85 + 0.12)) ** 0.7), o.color || SFX.PAL.ink);
    ctx.restore();
  };

  SFX.mouth = (ctx, x, y, w, type = 'smile', o = {}) => {
    if (!type || type === 'none') return;
    const col = o.color || SFX.PAL.mouth, inner = o.inner || SFX.PAL.mouthIn, ink = o.ink || SFX.PAL.ink, op = o.open ?? 1;
    ctx.save(); ctx.translate(x, y);
    const lw = Math.max(1.5, 0.13 * w);
    const line = pts => { ctx.beginPath(); SFX.addCurve(ctx, pts); ctx.strokeStyle = o.lineColor || C.shade(col, -0.25); ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); };
    if (type === 'smile') { // pink crescent
      ctx.beginPath(); ctx.moveTo(-w / 2, -0.08 * w);
      ctx.bezierCurveTo(-w * 0.42, w * 0.5, w * 0.42, w * 0.5, w / 2, -0.08 * w);
      ctx.bezierCurveTo(w * 0.3, w * 0.16, -w * 0.3, w * 0.16, -w / 2, -0.08 * w);
      ctx.fillStyle = col; ctx.fill();
    } else if (type === 'o' || type === 'fang') {
      const rx = w * 0.32, ry = w * 0.4 * op;
      SFX.ellipse(ctx, 0, 0, rx, ry, 0, inner);
      ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, TAU); ctx.clip(); SFX.ellipse(ctx, 0, ry * 0.95, rx * 0.8, ry * 0.55, 0, SFX.PAL.tongue); ctx.restore();
      if (type === 'fang') SFX.poly(ctx, [[-rx * 0.55, -ry * 0.82], [-rx * 0.05, -ry * 0.92], [-rx * 0.32, -ry * 0.25]], '#ffffff');
    } else if (type === 'open' || type === 'tri') {
      const hh = w * 0.55 * op;
      ctx.beginPath();
      if (type === 'open') { ctx.moveTo(-w / 2, 0); ctx.lineTo(w / 2, 0); ctx.bezierCurveTo(w * 0.45, hh * 1.25, -w * 0.45, hh * 1.25, -w / 2, 0); }
      else { ctx.moveTo(-w / 2, -hh * 0.1); ctx.lineTo(w / 2, -hh * 0.1); ctx.quadraticCurveTo(w * 0.1, hh * 1.1, 0, hh); ctx.quadraticCurveTo(-w * 0.1, hh * 1.1, -w / 2, -hh * 0.1); }
      ctx.closePath(); ctx.fillStyle = inner; ctx.fill();
      ctx.save(); ctx.clip(); SFX.ellipse(ctx, 0, hh * 0.95, w * 0.34, hh * 0.45, 0, SFX.PAL.tongue); ctx.restore();
    } else if (type === 'u') line([[-w * 0.35, -w * 0.1], [0, w * 0.18], [w * 0.35, -w * 0.1]]);
    else if (type === 'flat') line([[-w * 0.4, 0], [w * 0.4, 0]]);
    else if (type === 'wave') line([[-w * 0.5, 0], [-w * 0.25, -w * 0.12], [0, 0], [w * 0.25, w * 0.12], [w * 0.5, 0]]);
    else if (type === 'cat') line([[-w * 0.5, -w * 0.08], [-w * 0.25, w * 0.14], [0, -w * 0.02], [w * 0.25, w * 0.14], [w * 0.5, -w * 0.08]]);
    ctx.restore();
  };

  // ---------------------------------------------------------------- face FX
  SFX.blush = (ctx, x, y, w, alpha = 0.35, color = SFX.PAL.blush, o = {}) => {
    ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.44);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, w / 2);
    g.addColorStop(0, C.rgba(color, alpha)); g.addColorStop(0.55, C.rgba(color, alpha * 0.75)); g.addColorStop(1, C.rgba(color, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, w / 2, 0, TAU); ctx.fill();
    ctx.restore();
    const n = o.lines || 0;
    for (let i = 0; i < n; i++) {
      const lx = x + (i - (n - 1) / 2) * w * 0.16;
      SFX.capsule(ctx, lx + w * 0.05, y - w * 0.07, lx - w * 0.05, y + w * 0.07, Math.max(1.5, w * 0.035), Math.max(1.5, w * 0.035), C.rgba(C.shade(color, -0.2), Math.min(1, alpha * 2)));
    }
  };
  SFX.sweat = (ctx, x, y, size, o = {}) => {
    const col = o.color || SFX.PAL.sweat, sh = o.shade || SFX.PAL.sweatShade, s = size;
    ctx.save(); ctx.translate(x, y); ctx.rotate(o.angle || 0); ctx.globalAlpha *= o.alpha ?? 1;
    const path = c => { c.moveTo(0, -s * 0.5); c.bezierCurveTo(s * 0.1, -s * 0.2, s * 0.36, s * 0.02, s * 0.36, s * 0.2); c.arc(0, s * 0.2, s * 0.36, 0, Math.PI); c.bezierCurveTo(-s * 0.36, s * 0.02, -s * 0.1, -s * 0.2, 0, -s * 0.5); c.closePath(); };
    SFX.cel(ctx, path, col, sh, s * 0.1, s * 0.07);
    SFX.ellipse(ctx, -s * 0.13, s * 0.14, s * 0.07, s * 0.13, 0.35, 'rgba(255,255,255,0.95)');
    ctx.restore();
  };
  SFX.tear = (ctx, x, y, len, w, o = {}) => {
    const col = o.color || 'rgba(160,212,255,0.9)';
    const pts = [[x, y], [x - w * 0.15, y + len * 0.35], [x + w * 0.1, y + len * 0.7], [x, y + len]];
    SFX.strip(ctx, pts, u => w * (0.55 + 0.45 * u), col);
    SFX.circle(ctx, x, y + len, w * 0.62, col);
  };
  SFX.sparkle = (ctx, x, y, r, color = '#ffffff', rot = 0) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.beginPath(); starPath(ctx, 0, 0, r, r, 0.12); ctx.fillStyle = color; ctx.fill(); ctx.restore();
  };
  SFX.anger = (ctx, x, y, size, color = '#e2475a') => {
    ctx.save(); ctx.translate(x, y); ctx.strokeStyle = color; ctx.lineWidth = size * 0.13; ctx.lineCap = 'round';
    for (let i = 0; i < 4; i++) {
      ctx.save(); ctx.rotate(i * Math.PI / 2 + Math.PI / 4);
      ctx.beginPath(); ctx.moveTo(size * 0.14, -size * 0.36); ctx.quadraticCurveTo(size * 0.14, -size * 0.14, size * 0.36, -size * 0.14); ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  };

  // ---------------------------------------------------------------- chains
  SFX.chainPoints = (anchor, dir, links, linkSize, sag = 0.5, o = {}) => {
    const A = xy(anchor), pitch = linkSize * (o.pitch ?? 0.7);
    let a0 = typeof dir === 'number' ? dir : Math.atan2(xy(dir)[1], xy(dir)[0]);
    let dDown = Math.PI / 2 - a0; while (dDown > Math.PI) dDown -= TAU; while (dDown < -Math.PI) dDown += TAU;
    const pts = [A.slice()];
    const t = o.t || 0, sway = o.sway || 0, f = o.swayFreq ?? 0.6, lag = o.lag ?? 2.2;
    for (let i = 0; i < links; i++) {
      const u = (i + 0.5) / links;
      const ang = a0 + dDown * clamp(sag) * (1 - (1 - u) ** 1.8) + sway * u * Math.sin(TAU * f * t - u * lag);
      const p = pts[pts.length - 1];
      pts.push([p[0] + Math.cos(ang) * pitch, p[1] + Math.sin(ang) * pitch]);
    }
    return pts;
  };
  function chainCols(c) {
    if (!c) c = SFX.PAL.chain;
    if (typeof c === 'string') return { base: c, shade: C.shade(c, -0.3), light: C.shade(c, 0.35) };
    if (Array.isArray(c)) return { base: c[0], shade: c[1] || C.shade(c[0], -0.3), light: c[2] || C.shade(c[0], 0.35) };
    return { base: c.base, shade: c.shade || C.shade(c.base, -0.3), light: c.light || C.shade(c.base, 0.35) };
  }
  SFX.drawChain = (ctx, pts, linkSize, colours) => {
    const P = pts.map(xy), col = chainCols(colours), L = linkSize, th = L * 0.19;
    const seg = i => { const p = P[i], q = P[i + 1]; return { cx: (p[0] + q[0]) / 2, cy: (p[1] + q[1]) / 2, a: Math.atan2(q[1] - p[1], q[0] - p[0]) }; };
    // edge-on links first (odd), face-on rings on top (even)
    for (let i = 1; i < P.length - 1; i += 2) {
      const s = seg(i);
      ctx.save(); ctx.translate(s.cx, s.cy); ctx.rotate(s.a);
      SFX.capsule(ctx, -L * 0.5 + th * 0.65, 0, L * 0.5 - th * 0.65, 0, th * 1.3, th * 1.3, col.shade);
      SFX.capsule(ctx, -L * 0.5 + th * 0.9, -th * 0.22, L * 0.5 - th * 0.9, -th * 0.22, th * 0.42, th * 0.42, col.base);
      ctx.restore();
    }
    for (let i = 0; i < P.length - 1; i += 2) {
      const s = seg(i);
      ctx.save(); ctx.translate(s.cx, s.cy); ctx.rotate(s.a);
      const ring = c => { SFX.addRoundRect(c, -L / 2, -L * 0.31, L, L * 0.62, L * 0.31); c.moveTo(L / 2 - th, 0); SFX.addRoundRect(c, -L / 2 + th, -L * 0.31 + th, L - 2 * th, L * 0.62 - 2 * th, L * 0.31 - th); };
      ctx.beginPath(); ring(ctx); ctx.fillStyle = col.base; ctx.fill('evenodd');
      // one hard shade: bottom-right of the ring in screen space
      ctx.save(); ctx.beginPath(); ring(ctx); ctx.clip('evenodd');
      ctx.rotate(-s.a); ctx.beginPath(); ctx.rect(-L, -L, 2 * L, 2 * L); ctx.translate(-th * 0.55, -th * 0.55); ctx.rotate(s.a); SFX.addRoundRect(ctx, -L / 2, -L * 0.31, L, L * 0.62, L * 0.31);
      ctx.fillStyle = col.shade; ctx.fill('evenodd'); ctx.restore();
      ctx.restore();
    }
  };
  SFX.springChain = (ctx, anchor, dir, links, linkSize, sag, colours, o = {}) => {
    const pts = SFX.chainPoints(anchor, dir, links, linkSize, sag, o);
    SFX.drawChain(ctx, pts, linkSize, colours);
    return pts;
  };
  const _sims = {};
  SFX.simChain = (o) => {
    const key = o.key || 'chain', n = o.n || 10, seg = o.seg || 20, dt = 1 / 120, g = o.gravity ?? 1800, damp = o.damping ?? 0.985, iter = o.iter ?? 6;
    let s = _sims[key];
    const anchorAt = tt => o.anchor(tt);
    if (!s || s.t > o.t + 1e-9 || s.n !== n) {
      const A = anchorAt(0), ang = A.angle ?? Math.PI / 2;
      const pts = []; for (let i = 0; i <= n; i++) pts.push([A.x + Math.cos(ang) * seg * i, A.y + Math.sin(ang) * seg * i]);
      s = _sims[key] = { t: 0, n, pts, prev: pts.map(p => p.slice()) };
    }
    while (s.t + dt <= o.t + 1e-9) {
      s.t += dt;
      const A = anchorAt(s.t);
      for (let i = 1; i <= n; i++) {
        const p = s.pts[i], q = s.prev[i], vx = (p[0] - q[0]) * damp, vy = (p[1] - q[1]) * damp;
        q[0] = p[0]; q[1] = p[1];
        p[0] += vx; p[1] += vy + g * dt * dt;
      }
      s.pts[0][0] = A.x; s.pts[0][1] = A.y;
      for (let k = 0; k < iter; k++) {
        if (A.angle !== undefined && A.stiff) { // stiff root: second point follows the anchor angle
          s.pts[1][0] = lerp(s.pts[1][0], A.x + Math.cos(A.angle) * seg, A.stiff); s.pts[1][1] = lerp(s.pts[1][1], A.y + Math.sin(A.angle) * seg, A.stiff);
        }
        for (let i = 0; i < n; i++) {
          const p = s.pts[i], q = s.pts[i + 1], dx = q[0] - p[0], dy = q[1] - p[1], d = Math.hypot(dx, dy) || 1, diff = (d - seg) / d;
          if (i === 0) { q[0] -= dx * diff; q[1] -= dy * diff; }
          else { p[0] += dx * diff * 0.5; p[1] += dy * diff * 0.5; q[0] -= dx * diff * 0.5; q[1] -= dy * diff * 0.5; }
        }
      }
    }
    return s.pts.map(p => p.slice());
  };

  // ---------------------------------------------------------------- text, bubbles, sheets
  function txt(ctx, text, x, y, font, o) {
    ctx.save();
    ctx.font = font; ctx.textAlign = o.align || 'center'; ctx.textBaseline = o.base || 'middle';
    ctx.globalAlpha *= o.alpha ?? 1;
    if (o.track) { try { ctx.letterSpacing = o.track + 'px'; } catch (e) { /* older canvas */ } }
    const wdt = ctx.measureText(text).width;
    if (o.bg) {
      const size = o.size, pad = (o.pad ?? 0.45) * size, hh = size * 1.25;
      const left = ctx.textAlign === 'center' ? x - wdt / 2 : ctx.textAlign === 'right' ? x - wdt : x;
      SFX.roundRect(ctx, left - pad, y - hh / 2 - (ctx.textBaseline === 'middle' ? 0 : 0), wdt + 2 * pad, hh, hh / 2, o.bg);
    }
    ctx.fillStyle = o.color || '#ffffff';
    if (o.maxW) ctx.fillText(text, x, y, o.maxW); else ctx.fillText(text, x, y);
    ctx.restore();
    return wdt;
  }
  SFX.label = (ctx, text, x, y, size = 30, o = {}) => txt(ctx, text, x, y, `${o.weight || 800} ${size}px Nunito`, Object.assign({ size }, o));
  SFX.title = (ctx, text, x, y, size = 64, o = {}) => txt(ctx, text, x, y, `${o.weight || 600} ${size}px Fredoka`, Object.assign({ size }, o));
  SFX.bubble = (ctx, o) => {
    const k = SFX.ease.easeOutBack(o.pop ?? 1), s = (o.scale ?? 1) * k;
    if (s <= 0.001) return;
    SFX.shadowGroup(ctx, g => {
      g.save(); g.translate(o.x, o.y); g.scale(s, s);
      const w = o.w, h = o.h, fill = o.fill || '#ffffff';
      g.fillStyle = fill;
      g.beginPath();
      if (o.shape === 'round') SFX.addRoundRect(g, -w / 2, -h / 2, w, h, Math.min(w, h) * 0.32); else g.ellipse(0, 0, w / 2, h / 2, 0, 0, TAU);
      g.fill();
      if (o.tail) {
        g.beginPath();
        const tx = (o.tail[0] - o.x) / s, ty = (o.tail[1] - o.y) / s, ang = Math.atan2(ty, tx), r = Math.min(w, h) * 0.13;
        const ex = Math.cos(ang) * w * 0.36, ey = Math.sin(ang) * h * 0.36;
        g.moveTo(ex + Math.cos(ang + Math.PI / 2) * r, ey + Math.sin(ang + Math.PI / 2) * r);
        g.quadraticCurveTo(lerp(ex, tx, 0.55), lerp(ey, ty, 0.55), tx, ty);
        g.quadraticCurveTo(lerp(ex, tx, 0.45), lerp(ey, ty, 0.45), ex + Math.cos(ang - Math.PI / 2) * r, ey + Math.sin(ang - Math.PI / 2) * r);
        g.closePath(); g.fill();
      }
      const lines = o.lines || (o.text ? [o.text] : []), size = o.size || 40;
      lines.forEach((ln, i) => {
        const L = typeof ln === 'string' ? { text: ln } : ln;
        SFX.label(g, L.text, 0, (i - (lines.length - 1) / 2) * size * 1.22, L.size || size, { color: L.color || o.color || '#1b1a1f', weight: L.weight || 800 });
      });
      g.restore();
    }, { scale: o.shadowScale ?? 1, alpha: clamp((o.pop ?? 1) * 4) });
  };
  SFX.sheetBG = (ctx, W, H, o = {}) => {
    ctx.fillStyle = o.bg || '#17161c'; ctx.fillRect(0, 0, W, H);
    if (o.grid !== false) {
      ctx.fillStyle = 'rgba(255,255,255,0.035)';
      for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
      for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
    }
    if (o.title) SFX.title(ctx, o.title, 48, 48, 44, { align: 'left', color: '#f2eef6' });
    if (o.subtitle) SFX.label(ctx, o.subtitle, 50, 88, 20, { align: 'left', color: 'rgba(242,238,246,0.55)', weight: 700 });
  };
})();
