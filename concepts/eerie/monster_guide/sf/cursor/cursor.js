/* =====================================================================================================================
 * cursor.js : window.CURSOR, "Pip" the floating mouse-cursor presenter (alternative host concept for Monster HR, EP1).
 * Owner idea: to push the GAME element, the presenter is just a floating cursor that explains things, flies around,
 * hovers / clicks / drags things and swaps the background like a game menu.
 * Needs core/lib_core.js (window.SFX). Plain canvas 2D, deterministic (no Math.random; time comes in through opts.t).
 *
 * LOOK: our own chunky game-UI pointer (not an OS copy): a short fat arrow with soft rounded corners and a stubby tail,
 * white body with ONE hard cool-grey shade on the bottom-right (show rule: light from the top-left), a thick ink edge,
 * one soft floating drop shadow (further down-right than ground characters: it hovers). It emotes ONLY through simple
 * means: two dot eyes (or none), tilt, squash / stretch, wiggle, a click ripple, a hover glow. No mouth by default.
 *
 * UNITS: s = 1 -> the arrow is ~108 px tall (0.6 W of the show's common scale, W = chest width 180 px).
 * (x, y) is always the HOTSPOT: the arrow tip / the hand's index fingertip / the fist centre for 'grab'.
 *
 * API
 *   CURSOR.draw(ctx, x, y, s = 1, opts)  draws the cursor as one group (one shadow). opts (all optional):
 *     state     'point' (default) | 'click' | 'drag' | 'hand' | 'grab' | 'loading' | 'forbidden'
 *     expr      'neutral' | 'happy' (∩∩) | 'blink' | 'wow' (big dots) | 'worried' | 'annoyed' | 'smug' | 'focus'
 *               | 'dizzy' | 'love' | 'none' (no face at all: pure UI pointer)
 *     look      [lx, ly] -1..1 gaze shift of the dots;  blink 0..1 (1 = shut, overrides the dots with lines)
 *     tilt      radians, rotates around the hotspot (+ = clockwise)
 *     squash    -1..1 (+ squashes along the arrow axis and widens, - stretches);  stretchDir radians: stretch along a
 *               motion direction instead (pass the velocity angle with squash < 0 while flying)
 *     wiggle    0..1 amplitude of a fast tilt wobble (uses t);  t seconds
 *     ripple    0..1 click ripple progress (two expanding rings + 4 ticks at the hotspot); null = none
 *     glow      0..1 hover glow (warm halo behind the pointer);  glowColor '#FFE08A'
 *     press     0..1 (click / grab) pushes the body toward the hotspot a little
 *     spin      seconds or phase for the loading badge (defaults to t)
 *     from      [x, y] (state 'drag') selection-box anchor corner; the box is drawn from it to the hotspot
 *     alpha     group alpha;  shadow true | false;  ink '#15131A', body '#FFFFFF', shade '#C9CEDC'
 *   CURSOR.selection(ctx, x0, y0, x1, y1, o)   marquee selection: translucent fill, marching-ant dashed edge, corner
 *               handles. o: t (ants), color '#7FD3FF', fill alpha 0.12, handles true, lw 3
 *   CURSOR.target(ctx, x, y, w, h, o)          game "target lock" corner brackets around a box. o: t, pop 0..1 (snap-in),
 *               color '#FFE08A', len 0.22 (fraction of the short side), lw 7
 *   CURSOR.tooltip(ctx, x, y, o)               game tooltip panel, top-left at (x, y). o: title, sub, lines [...],
 *               rarity ('common' | 'rare' | 'cursed' | '???'), w, pop 0..1, icon (fn(ctx, cx, cy, r) or null)
 *   CURSOR.panel(ctx, x, y, w, h, o)           game UI window: dark slate body, gold double border, header bar.
 *               o: title, pop 0..1, alpha
 *   CURSOR.card(ctx, x, y, w, h, o)            rule card (RULE n + text), drawn centred at (x, y). o: num, text, rot,
 *               lift 0..1 (held: bigger shadow), glow 0..1
 *   CURSOR.ripple(ctx, x, y, s, k, o)          the click ripple alone
 *   CURSOR.EXPRS / CURSOR.STATES               names, for sheets
 *
 * v2 : GAME-UI ICON SWAPS (owner request: the cursor keeps swapping icons like a game UI)
 *   extra states   'hourglass' busy icon (white caps + posts, pale glass, gold sand; the dots sit on the top cap).
 *                    It is centred on the arrow's visual centre (HG_C), so a swap point -> hourglass pops in place.
 *                    opts.sand 0..1 (0 = all on top, 1 = all run down; default loops with t), opts.flip 0..1 (the
 *                    half-turn flip, easeInOutBack; at flip = 1 the glass is upside down = full again, so the caller
 *                    resets sand to 0 and flip to 0 on the next frame)
 *                  'rclick' / 'dclick'  pointer + a tiny mouse badge with the right / left button lit ('dclick'
 *                    adds a ×2 tag). Pair 'dclick' with opts.dbl.
 *   opts.swap      seconds since the last icon swap (null = none): scale-in spring + squash -> stretch -> settle and
 *                  a little poof of dots around the pivot. Pass it for ~0.5 s after every state change.
 *   opts.dbl       0..1 double-click effect (two quick ripples, the second gold, + tiny impact sparks); drawn at the
 *                  hotspot. Also CURSOR.dblclick(ctx, x, y, s, k, o) alone.
 *   CURSOR.menu(ctx, x, y, o)         right-click context menu, top-left corner at (x, y) (= the click point).
 *               o: items [{label, key, color}] | ['Open', ...], title, w=340, pop 0..1 (springs out of the corner),
 *               hover (row index, fractional = the highlight bar sliding), pick 0..1 (the chosen row flashes)
 *               CURSOR.menuRow(x, y, i, o) -> [x, y] a good hotspot over row i
 *   CURSOR.button(ctx, x, y, w, h, o) chunky game button (top-left x, y). o: label, size, color '#FFC83D', press 0..1
 *               (the cap sinks into its base), icon fn(ctx, cx, cy, r), glow 0..1, textColor
 *   CURSOR.tabs(ctx, x, y, o)         tab strip. o: tabs ['MAP', 'BAG', 'RULES'], active, prev, k 0..1 (switch progress:
 *               the gold underline slides prev -> active), press {i, k}, tw=150, th=54
 *               CURSOR.tabAt(x, y, i, o) -> [x, y] centre of tab i
 *   CURSOR.slider(ctx, x, y, w, o)    value slider, track centre-left at (x, y). o: value 0..1, grab 0..1 (knob grows,
 *               value bubble), label.  CURSOR.sliderKnob(x, y, w, v) -> [x, y]
 *   CURSOR.minimap(ctx, x, y, o)      corner HUD: room grid + "you are here" pip + a MOVE arrow button. o: rooms
 *               [[col, row, name]], at [col, row] (fractional while moving), visited count, press 0..1, glow 0..1,
 *               title. CURSOR.MINIMAP.w / h, CURSOR.MINIMAP.btn(x, y) -> [x, y] centre of the MOVE button
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX, C = S.color, TAU = Math.PI * 2;
  const clamp = S.clamp, lerp = S.lerp;
  const INK = '#15131A', BODY = '#FFFFFF', SHADE = '#C9CEDC', GOLD = '#FFE08A', RED = '#E2475A';
  const K = window.CURSOR = {};
  K.STATES = ['point', 'click', 'drag', 'hand', 'grab', 'loading', 'forbidden', 'hourglass', 'rclick', 'dclick'];
  K.EXPRS = ['neutral', 'happy', 'blink', 'wow', 'worried', 'annoyed', 'smug', 'focus', 'dizzy', 'love', 'none'];

  // ---------------------------------------------------------------- shapes (hotspot at 0,0, s = 1)
  // chunky arrow: tip, left edge, notch, tail, notch, wing. Rounded per corner (the tip stays sharp-ish).
  const ARROW = [[0, 0], [0, 86], [21, 69], [34, 102], [55, 94], [42, 62], [70, 60]];
  const ARROW_R = [5, 9, 4, 8, 8, 4, 9];
  const ARROW_C = [22, 50];                  // visual centre of the head (face, squash pivot)
  const addArrow = g => S.addRoundPoly(g, ARROW, ARROW_R);

  // pointing hand: index finger up (tip = hotspot), three folded fingers, thumb out to the left, a cuff
  const addHand = g => {
    S.addCapsule(g, 0, 9, 0, 58, 25);                       // index
    S.addRoundRect(g, -14, 46, 64, 60, [14, 18, 22, 22]);    // palm
    S.addCapsule(g, 22, 50, 22, 60, 22);                     // folded fingers (bumps)
    S.addCapsule(g, 38, 54, 38, 62, 20);
    S.addCapsule(g, -10, 80, -26, 62, 21);                   // thumb
  };
  const addCuff = g => S.addRoundRect(g, -10, 100, 56, 17, 6);
  // grab fist: hotspot at its middle
  const addFist = g => {
    S.addRoundRect(g, -34, -24, 66, 58, [16, 16, 22, 22]);
    for (let i = 0; i < 4; i++) S.addCapsule(g, -24 + i * 15.5, -24, -24 + i * 15.5, -18, 18);
    S.addCapsule(g, -40, 2, -30, -6, 20);
  };
  const addFistCuff = g => S.addRoundRect(g, -27, 30, 54, 16, 6);

  // ink edge (outside only) + white body + one hard shade crescent
  // fill = optional extra sub-paths added to the shifted (lit) mask so inner notches (thumb / palm) stay clean
  function solid(g, pathFn, o, lw = 9, fill) {
    g.beginPath(); pathFn(g);
    g.lineJoin = 'round'; g.lineCap = 'round';
    g.strokeStyle = o.ink; g.lineWidth = lw; g.stroke();
    // shade = whole shape, then the lit body = the shape shifted up-left (nonzero union, so overlapping parts
    // such as finger + palm never leave shade islands), clipped to the shape
    g.beginPath(); pathFn(g); g.fillStyle = o.shade || o.body; g.fill();
    if (!o.shade) return;
    const d = 4.5;
    g.save(); g.beginPath(); pathFn(g); g.clip();
    g.beginPath(); g.translate(-d, -d); pathFn(g); g.translate(d, d);
    if (fill) fill(g);
    g.fillStyle = o.body; g.fill('nonzero');
    g.restore();
  }
  const handFill = g => { g.moveTo(-40, 40); g.lineTo(10, 40); g.lineTo(10, 96); g.lineTo(-40, 96); g.closePath(); };

  // ---------------------------------------------------------------- face (two dots and nothing else)
  function face(g, cx, cy, o, sz = 1) {
    const e = o.expr || 'neutral';
    if (e === 'none') return;
    const gap = 8.5 * sz, r = 4.6 * sz, lx = (o.look ? o.look[0] : 0) * 3.2 * sz, ly = (o.look ? o.look[1] : 0) * 3 * sz;
    const shut = (o.blink ?? 0) > 0.55 || e === 'blink';
    g.save(); g.fillStyle = o.ink; g.strokeStyle = o.ink; g.lineCap = 'round'; g.lineJoin = 'round';
    const X = [cx - gap + lx, cx + gap + lx], Y = cy + ly;
    const line = (pts, lw = 3.4 * sz) => { g.lineWidth = lw; g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]))); g.stroke(); };
    if (shut) X.forEach(x => line([[x - r, Y], [x + r, Y]]));
    else if (e === 'happy') X.forEach(x => { g.lineWidth = 3.4 * sz; g.beginPath(); g.arc(x, Y + r * 0.6, r * 1.05, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); });
    else if (e === 'smug') X.forEach(x => { g.lineWidth = 3.4 * sz; g.beginPath(); g.arc(x, Y - r * 0.9, r * 1.05, Math.PI * 0.15, Math.PI * 0.85); g.stroke(); });
    else if (e === 'dizzy') X.forEach(x => { line([[x - r * 0.8, Y - r * 0.8], [x + r * 0.8, Y + r * 0.8]], 3 * sz); line([[x + r * 0.8, Y - r * 0.8], [x - r * 0.8, Y + r * 0.8]], 3 * sz); });
    else if (e === 'love') X.forEach(x => {
      const h = r * 1.15; g.beginPath(); g.moveTo(x, Y + h * 0.9);
      g.bezierCurveTo(x - h * 1.5, Y - h * 0.1, x - h * 0.7, Y - h * 1.2, x, Y - h * 0.35);
      g.bezierCurveTo(x + h * 0.7, Y - h * 1.2, x + h * 1.5, Y - h * 0.1, x, Y + h * 0.9);
      g.fillStyle = RED; g.fill();
    });
    else {
      const rr = e === 'wow' ? r * 1.35 : e === 'focus' ? r * 0.85 : r;
      X.forEach(x => S.circle(g, x, Y, rr, o.ink));
      if (e === 'wow') X.forEach(x => S.circle(g, x - rr * 0.35, Y - rr * 0.35, rr * 0.32, '#fff'));
      if (e === 'worried') { line([[X[0] - r * 1.1, Y - r * 1.5], [X[0] + r * 0.9, Y - r * 2.3]], 2.8 * sz); line([[X[1] - r * 0.9, Y - r * 2.3], [X[1] + r * 1.1, Y - r * 1.5]], 2.8 * sz); }
      if (e === 'annoyed') { g.save(); g.fillStyle = o.body; X.forEach(x => g.fillRect(x - r * 1.3, Y - r * 1.4, r * 2.6, r * 1.15)); g.restore(); X.forEach(x => line([[x - r * 1.2, Y - r * 0.3], [x + r * 1.2, Y - r * 0.3]], 2.8 * sz)); }
      if (e === 'focus') { line([[X[0] - r * 1.1, Y - r * 2.2], [X[0] + r * 1.0, Y - r * 1.5]], 2.8 * sz); line([[X[1] - r * 1.0, Y - r * 1.5], [X[1] + r * 1.1, Y - r * 2.2]], 2.8 * sz); }
    }
    if (o.blush) X.forEach((x, i) => S.ellipse(g, x + (i ? 4 : -4) * sz, Y + r * 2.1, r * 1.2, r * 0.6, 0, C.rgba('#FF8FA3', 0.55 * o.blush)));
    g.restore();
  }

  // ---------------------------------------------------------------- badges (loading spinner, forbidden)
  function badge(g, bx, by, o, kind) {
    const R = 21;
    g.save();
    S.circle(g, bx, by, R + 4.5, o.ink);
    S.circle(g, bx, by, R, o.body);
    if (kind === 'loading') {
      const ph = (o.spin ?? o.t ?? 0) * 1.6;
      for (let i = 0; i < 8; i++) {
        const a = (i / 8) * TAU + Math.floor(ph * 8) / 8 * TAU, k = ((i + 8) % 8) / 7;
        S.circle(g, bx + Math.cos(a) * R * 0.6, by + Math.sin(a) * R * 0.6, 2.2 + 2.3 * k, C.rgba(o.ink, 0.15 + 0.85 * k));
      }
    } else {
      g.strokeStyle = RED; g.lineWidth = 6; g.lineCap = 'butt';
      g.beginPath(); g.arc(bx, by, R * 0.66, 0, TAU); g.stroke();
      g.beginPath(); g.moveTo(bx - R * 0.47, by - R * 0.47); g.lineTo(bx + R * 0.47, by + R * 0.47); g.stroke();
    }
    g.restore();
  }

  // ---------------------------------------------------------------- hourglass (busy icon, v2)
  const HG_C = [24, 48];                     // centred on the arrow's visual centre so swaps pop in place
  const SAND = '#FFC83D', SAND_SH = '#E0962E', GLASS = '#DDF0FF', GLASS_SH = '#B7D3EA';
  const HG_GLASS = [[-25, -40], [25, -40], [5, -3], [5, 3], [25, 40], [-25, 40], [-5, 3], [-5, -3]];
  const addGlass = g => S.addRoundPoly(g, HG_GLASS, [7, 7, 4, 4, 7, 7, 4, 4]);
  function hourglass(g, o) {
    const fl = clamp(o.flip || 0), ang = S.ease.easeInOutBack(fl, 1.3) * Math.PI;
    const sand = clamp(o.sand ?? (((o.t || 0) % 1.8) / 1.8));
    g.save(); g.translate(HG_C[0], HG_C[1]); g.rotate(ang);
    // glass: ink edge, pale fill, one hard shade on the right
    g.beginPath(); addGlass(g); g.lineJoin = 'round'; g.strokeStyle = o.ink; g.lineWidth = 9; g.stroke();
    g.fillStyle = GLASS; g.fill();
    S.clip(g, addGlass, cg => {
      cg.fillStyle = GLASS_SH; cg.beginPath(); cg.moveTo(12, -40); cg.lineTo(30, -40); cg.lineTo(30, 40); cg.lineTo(12, 40); cg.lineTo(2, 0); cg.closePath(); cg.fill();
      // sand on top (sits on the neck, shrinks), pile at the bottom (grows), the stream between
      const yT = lerp(-33, -2, sand);
      if (sand < 0.995) { cg.fillStyle = SAND; cg.fillRect(-30, yT, 60, -yT); cg.fillStyle = SAND_SH; cg.fillRect(8, yT, 22, -yT); }
      const h = 34 * sand;
      if (h > 0.5) {
        cg.fillStyle = SAND; cg.beginPath(); cg.moveTo(-30, 41); cg.lineTo(-30, 41 - h * 0.5); cg.quadraticCurveTo(0, 41 - h * 1.35, 30, 41 - h * 0.5); cg.lineTo(30, 41); cg.closePath(); cg.fill();
        cg.fillStyle = SAND_SH; cg.beginPath(); cg.moveTo(9, 41); cg.lineTo(9, 41 - h * 0.86); cg.quadraticCurveTo(20, 41 - h * 0.7, 30, 41 - h * 0.5); cg.lineTo(30, 41); cg.closePath(); cg.fill();
      }
      if (sand > 0.01 && sand < 0.99 && fl === 0) {
        cg.strokeStyle = SAND; cg.lineWidth = 3.6; cg.lineCap = 'round';
        cg.beginPath(); cg.moveTo(0, -2); cg.lineTo(0, 41 - h * 0.95); cg.stroke();
        cg.setLineDash([3, 7]); cg.lineDashOffset = -(o.t || 0) * 140; cg.strokeStyle = '#FFF2C4'; cg.lineWidth = 2.2;
        cg.beginPath(); cg.moveTo(0, -2); cg.lineTo(0, 41 - h * 0.95); cg.stroke(); cg.setLineDash([]);
      }
      // glass glint (top-left)
      S.capsule(cg, -15, -31, -9, -18, 5, 4, 'rgba(255,255,255,0.9)');
    });
    // posts + caps (the hourglass frame, same white / shade / ink as the arrow)
    [-30, 30].forEach(px => solid(g, c => S.addCapsule(c, px, -44, px, 44, 8), o, 7));
    solid(g, c => S.addRoundRect(c, -36, -58, 72, 19, 8), o);
    solid(g, c => S.addRoundRect(c, -36, 39, 72, 19, 8), o);
    face(g, 0, -48.5, o, 0.72);
    g.restore();
  }

  // tiny mouse badge (rclick / dclick): which = 'L' | 'R'
  function mouseBadge(g, bx, by, o, which, x2) {
    const w = 34, h = 46, x0 = bx - w / 2, y0 = by - h / 2;
    g.save();
    S.roundRect(g, x0 - 4.5, y0 - 4.5, w + 9, h + 9, 19, o.ink);
    S.roundRect(g, x0, y0, w, h, 15, o.body);
    S.clip(g, c => S.addRoundRect(c, x0, y0, w, h, 15), cg => {
      cg.fillStyle = o.shade; cg.fillRect(x0 + w - 7, y0, 7, h); cg.fillRect(x0, y0 + h - 6, w, 6);
      const flash = 0.75 + 0.25 * Math.sin((o.t || 0) * 30);
      cg.fillStyle = C.rgba(GOLD, flash); cg.fillRect(which === 'R' ? bx : x0, y0, w / 2, h * 0.42);
    });
    g.strokeStyle = o.ink; g.lineWidth = 3; g.lineCap = 'round';
    g.beginPath(); g.moveTo(bx, y0 + 1); g.lineTo(bx, y0 + h * 0.42); g.moveTo(x0 + 1, y0 + h * 0.42); g.lineTo(x0 + w - 1, y0 + h * 0.42); g.stroke();
    if (x2) {
      S.roundRect(g, bx + 6, by + 8, 38, 26, 9, o.ink);
      S.label(g, '×2', bx + 25, by + 21, 19, { color: GOLD, weight: 1000 });
    }
    g.restore();
  }

  // swap poof: little dots bursting out of the pivot when the icon changes
  function poof(ctx, x, y, s, e) {
    const q = clamp(e / 0.34); if (q <= 0 || q >= 1) return;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    for (let i = 0; i < 7; i++) {
      const a = i / 7 * TAU - 0.4, r = 38 + S.ease.easeOutCubic(q) * 46;
      S.circle(ctx, Math.cos(a) * r, Math.sin(a) * r, 6.5 * (1 - q) + 1, C.rgba(i % 2 ? GOLD : '#FFFFFF', 1 - q));
    }
    ctx.restore();
  }

  // double click: two quick ripples (white, then gold) + tiny impact sparks at each click
  K.dblclick = (ctx, x, y, s, k, o = {}) => {
    if (k == null || k <= 0 || k >= 1) return;
    const r1 = k / 0.6, r2 = (k - 0.28) / 0.6;
    if (r1 > 0 && r1 < 1) K.ripple(ctx, x, y, s * 0.8, r1, { color: '#FFFFFF' });
    if (r2 > 0 && r2 < 1) K.ripple(ctx, x, y, s * 1.05, r2, { color: GOLD });
    [[0, 0], [0.28, 1]].forEach(([d, j]) => {
      const q = (k - d) / 0.36; if (q <= 0 || q >= 1) return;
      const e = S.ease.easeOutCubic(q);
      ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
      for (let i = 0; i < 6; i++) {
        const a = i / 6 * TAU + 0.26 + j * 0.52, r0 = 16 + e * 58, len = 18 * (1 - q) + 2;
        ctx.strokeStyle = C.rgba(INK, 0.5 * (1 - q)); ctx.lineWidth = 7;
        ctx.beginPath(); ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); ctx.lineTo(Math.cos(a) * (r0 + len), Math.sin(a) * (r0 + len)); ctx.stroke();
        ctx.strokeStyle = C.rgba(j ? GOLD : '#FFFFFF', 1 - q * q); ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); ctx.lineTo(Math.cos(a) * (r0 + len), Math.sin(a) * (r0 + len)); ctx.stroke();
      }
      for (let i = 0; i < 3; i++) {
        const a = i / 3 * TAU + 0.8 + j, r = 30 + e * 44;
        S.sparkle(ctx, Math.cos(a) * r, Math.sin(a) * r, 11 * (1 - q) + 1, j ? GOLD : '#FFFFFF', q * 1.5);
      }
      ctx.restore();
    });
  };

  // ---------------------------------------------------------------- the ripple (click feedback)
  K.ripple = (ctx, x, y, s, k, o = {}) => {
    if (k == null || k <= 0 || k >= 1) return;
    const col = o.color || '#FFFFFF';
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    [0, 0.22].forEach((d, i) => {
      const q = clamp((k - d) / (1 - d)); if (q <= 0) return;
      const r = 10 + S.ease.easeOutCubic(q) * (i ? 46 : 64), a = (1 - q) * (i ? 0.7 : 1);
      ctx.strokeStyle = C.rgba(INK, a * 0.6); ctx.lineWidth = 9 * (1 - q) + 2;
      ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
      ctx.strokeStyle = C.rgba(col, a); ctx.lineWidth = 5 * (1 - q) + 1;
      ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
    });
    const q = S.ease.easeOutQuad(k);
    ctx.strokeStyle = C.rgba(col, 1 - k); ctx.lineWidth = 5; ctx.lineCap = 'round';
    for (let i = 0; i < 4; i++) {
      const a = -Math.PI * 0.75 + i * Math.PI / 2 + Math.PI * 0.25 * 0, r0 = 22 + q * 40, r1 = r0 + 14 * (1 - k);
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); ctx.lineTo(Math.cos(a) * r1, Math.sin(a) * r1); ctx.stroke();
    }
    ctx.restore();
  };

  // ---------------------------------------------------------------- main draw
  K.draw = (ctx, x, y, s = 1, opts = {}) => {
    const o = Object.assign({ state: 'point', expr: 'neutral', t: 0, ink: INK, body: BODY, shade: SHADE, glowColor: GOLD }, opts);
    const st = o.state;
    if (st === 'drag' && o.from) K.selection(ctx, o.from[0], o.from[1], x, y, { t: o.t });
    if (o.ripple != null) K.ripple(ctx, x, y, s, o.ripple);
    if (o.dbl != null) K.dblclick(ctx, x, y, s, o.dbl);
    let tilt = (o.tilt || 0) + (o.wiggle ? o.wiggle * 0.22 * Math.sin(o.t * 19) * (0.6 + 0.4 * Math.sin(o.t * 5.3)) : 0);
    let sq = o.squash || 0;
    if (st === 'click') sq = Math.max(sq, 0.16 * (o.press ?? 1));
    const isHand = st === 'hand' || st === 'grab', isHG = st === 'hourglass';
    const piv = st === 'grab' ? [0, 0] : isHand ? [16, 66] : isHG ? HG_C : ARROW_C;
    // icon swap pop: scale-in spring + squash -> stretch -> settle, and a poof of dots
    let popSc = 1;
    if (o.swap != null && o.swap >= 0 && o.swap < 0.7) {
      popSc = 0.6 + 0.4 * S.spring(o.swap, 3.4, 0.3);
      sq += 0.5 * S.wobble(o.swap, 3.4, 6.5);
      const pv = S.rot(piv[0] * s, piv[1] * s, tilt);
      poof(ctx, x + pv[0], y + pv[1], s, o.swap);
    }

    // hover glow: soft warm halo behind
    if (o.glow > 0) {
      ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(tilt);
      const gx = piv[0], gy = piv[1] + (st === 'grab' ? 0 : -8);
      const gr = ctx.createRadialGradient(gx, gy, 10, gx, gy, 105);
      gr.addColorStop(0, C.rgba(o.glowColor, 0.55 * o.glow)); gr.addColorStop(0.5, C.rgba(o.glowColor, 0.2 * o.glow)); gr.addColorStop(1, C.rgba(o.glowColor, 0));
      ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = gr;
      ctx.beginPath(); ctx.arc(gx, gy, 105, 0, TAU); ctx.fill();
      ctx.restore();
    }

    S.shadowGroup(ctx, g => {
      g.save(); g.translate(x, y); g.scale(s, s); g.rotate(tilt);
      // squash / stretch about the pivot. Default axis = the arrow's own axis (tip -> tail ~ 62 deg); stretchDir
      // overrides it with a screen direction (motion), undoing the tilt so the stretch follows the path.
      const ax = o.stretchDir != null ? o.stretchDir - tilt : (isHand || isHG ? Math.PI / 2 : Math.atan2(ARROW_C[1], ARROW_C[0]));
      const k = 1 - sq * 0.5, kw = 1 / Math.sqrt(Math.max(0.3, k)) * (sq < 0 ? 1 : 1 + sq * 0.15);
      g.translate(piv[0], piv[1]); g.scale(popSc, popSc); g.rotate(ax); g.scale(k, kw); g.rotate(-ax); g.translate(-piv[0], -piv[1]);
      if ((o.press || 0) > 0 && st !== 'grab') g.translate(-3 * o.press, -6 * o.press);
      if (isHG) hourglass(g, o);
      else if (isHand) {
        if (st === 'hand') {
          solid(g, addCuff, Object.assign({}, o, { body: '#E9ECF4', shade: '#B9BFCF' }));
          solid(g, addHand, o, 9, handFill);
          // finger seams + knuckle lines (thin ink, cartoon glove)
          g.strokeStyle = o.ink; g.lineWidth = 3.2; g.lineCap = 'round';
          g.beginPath(); g.moveTo(12.5, 50); g.lineTo(12.5, 61); g.moveTo(30, 52); g.lineTo(30, 62); g.stroke();
          face(g, 22, 84, o, 1.05);
        } else {
          solid(g, addFistCuff, Object.assign({}, o, { body: '#E9ECF4', shade: '#B9BFCF' }));
          solid(g, addFist, o);
          g.strokeStyle = o.ink; g.lineWidth = 3.2; g.lineCap = 'round';
          g.beginPath();
          for (let i = 1; i < 4; i++) { const fx = -24 + i * 15.5 - 7.75; g.moveTo(fx, -26); g.lineTo(fx, -12); }
          g.stroke();
          face(g, 2, 10, o, 1.05);
        }
      } else {
        solid(g, addArrow, o);
        face(g, ARROW_C[0] - 1, ARROW_C[1] + 1, o);
        if (st === 'loading') badge(g, 64, 98, o, 'loading');
        if (st === 'forbidden') badge(g, 64, 98, o, 'forbidden');
        if (st === 'rclick' || st === 'dclick') mouseBadge(g, 66, 96, o, st === 'rclick' ? 'R' : 'L', st === 'dclick');
      }
      g.restore();
    }, { scale: s, dx: 10, dy: 14, blur: 12, color: 'rgba(0,0,0,0.42)', alpha: o.alpha ?? 1, shadow: o.shadow !== false });
  };

  // ---------------------------------------------------------------- UI pieces
  K.selection = (ctx, x0, y0, x1, y1, o = {}) => {
    const col = o.color || '#7FD3FF', lw = o.lw ?? 3;
    const X = Math.min(x0, x1), Y = Math.min(y0, y1), w = Math.abs(x1 - x0), h = Math.abs(y1 - y0);
    if (w < 1 || h < 1) return;
    ctx.save();
    ctx.fillStyle = C.rgba(col, o.fill ?? 0.12); ctx.fillRect(X, Y, w, h);
    ctx.lineWidth = lw + 3; ctx.strokeStyle = 'rgba(8,10,16,0.55)'; ctx.strokeRect(X, Y, w, h);
    ctx.lineWidth = lw; ctx.strokeStyle = '#FFFFFF'; ctx.strokeRect(X, Y, w, h);
    ctx.setLineDash([12, 10]); ctx.lineDashOffset = -(o.t || 0) * 40; ctx.strokeStyle = col; ctx.strokeRect(X, Y, w, h);
    ctx.setLineDash([]);
    if (o.handles !== false) [[X, Y], [X + w, Y], [X, Y + h], [X + w, Y + h], [X + w / 2, Y], [X + w / 2, Y + h], [X, Y + h / 2], [X + w, Y + h / 2]]
      .forEach(([hx, hy]) => { ctx.fillStyle = '#0D1018'; ctx.fillRect(hx - 7, hy - 7, 14, 14); ctx.fillStyle = '#FFFFFF'; ctx.fillRect(hx - 5, hy - 5, 10, 10); });
    ctx.restore();
  };

  K.target = (ctx, x, y, w, h, o = {}) => {
    const pop = o.pop ?? 1; if (pop <= 0) return;
    const col = o.color || GOLD, e = S.ease.easeOutBack(pop, 2.2), grow = (1 - e) * 60 + Math.sin((o.t || 0) * 4) * 3;
    const L = Math.min(w, h) * (o.len ?? 0.22), lw = o.lw ?? 7;
    const X0 = x - grow, Y0 = y - grow, X1 = x + w + grow, Y1 = y + h + grow;
    ctx.save(); ctx.globalAlpha *= clamp(pop * 3); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const corners = [[X0, Y0, 1, 1], [X1, Y0, -1, 1], [X0, Y1, 1, -1], [X1, Y1, -1, -1]];
    const path = () => { ctx.beginPath(); corners.forEach(([cx, cy, dx, dy]) => { ctx.moveTo(cx + dx * L, cy); ctx.lineTo(cx, cy); ctx.lineTo(cx, cy + dy * L); }); };
    path(); ctx.strokeStyle = 'rgba(8,10,16,0.6)'; ctx.lineWidth = lw + 6; ctx.stroke();
    path(); ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.stroke();
    ctx.restore();
  };

  const RAR = { common: ['COMMON', '#B9C2D6'], rare: ['RARE', '#7FD3FF'], cursed: ['CURSED', '#E2475A'], '???': ['???', '#C59BFF'] };
  K.tooltip = (ctx, x, y, o = {}) => {
    const pop = o.pop ?? 1; if (pop <= 0) return;
    const w = o.w || 380, lines = o.lines || [], rar = RAR[o.rarity || 'common'] || RAR.common;
    const h = 72 + (o.sub ? 34 : 0) + lines.length * 34 + (lines.length ? 14 : 0);
    const e = S.ease.easeOutBack(pop, 1.8);
    ctx.save(); ctx.translate(x, y + (1 - e) * 16); ctx.globalAlpha *= clamp(pop * 2.5);
    ctx.translate(0, 0); ctx.scale(lerp(0.85, 1, e), lerp(0.85, 1, e));
    S.shadowGroup(ctx, g => {
      S.roundRect(g, 0, 0, w, h, 14, '#0E1119');
      g.strokeStyle = '#3A3F52'; g.lineWidth = 3; S.roundRect(g, 1.5, 1.5, w - 3, h - 3, 13, null, '#3A3F52', 3);
      S.roundRect(g, 7, 7, w - 14, h - 14, 9, null, C.rgba(GOLD, 0.5), 2);
      // rarity stripe
      S.roundRect(g, 7, 7, 8, h - 14, [9, 0, 0, 9], rar[1]);
    }, { scale: 1, dx: 8, dy: 10, blur: 14, color: 'rgba(0,0,0,0.5)' });
    let ty = 44;
    if (o.icon) o.icon(ctx, w - 44, 44, 24);
    S.label(ctx, o.title || '', 32, ty, 36, { align: 'left', color: '#FFF4D6', weight: 900 });
    if (o.sub) { ty += 34; S.label(ctx, o.sub, 32, ty, 21, { align: 'left', color: rar[1], weight: 800 }); }
    lines.forEach((l, i) => S.label(ctx, l, 32, ty + 36 + i * 34, 23, { align: 'left', color: 'rgba(225,230,242,0.82)', weight: 700 }));
    ctx.restore();
  };

  K.panel = (ctx, x, y, w, h, o = {}) => {
    const pop = o.pop ?? 1; if (pop <= 0) return;
    const e = S.ease.easeOutBack(pop, 1.4);
    ctx.save(); ctx.globalAlpha *= clamp(pop * 3) * (o.alpha ?? 1);
    ctx.translate(x + w / 2, y + h / 2); ctx.scale(lerp(0.9, 1, e), lerp(0.9, 1, e)); ctx.translate(-w / 2, -h / 2);
    S.shadowGroup(ctx, g => {
      S.roundRect(g, 0, 0, w, h, 22, '#141826');
      S.roundRect(g, 0, 0, w, 74, [22, 22, 0, 0], '#1E2436');
      g.fillStyle = '#0B0E16'; g.fillRect(0, 74, w, 4);
      S.roundRect(g, 3, 3, w - 6, h - 6, 20, null, '#C9A24A', 4);
      S.roundRect(g, 12, 12, w - 24, h - 24, 14, null, C.rgba(GOLD, 0.28), 2);
    }, { scale: 1, dx: 12, dy: 16, blur: 24, color: 'rgba(0,0,0,0.6)' });
    if (o.title) S.label(ctx, o.title, 36, 40, 30, { align: 'left', color: '#FFE9B8', weight: 900 });
    // window buttons, game style
    [['#E2475A', 0], ['#FFC83D', 1]].forEach(([c, i]) => { S.circle(ctx, w - 40 - i * 34, 40, 11, '#0B0E16'); S.circle(ctx, w - 40 - i * 34, 40, 8, c); });
    ctx.restore();
  };

  K.card = (ctx, x, y, w, h, o = {}) => {
    const lift = o.lift || 0;
    ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(1 + lift * 0.06, 1 + lift * 0.06);
    if (o.glow > 0) {
      const gr = ctx.createRadialGradient(0, 0, Math.min(w, h) * 0.3, 0, 0, Math.max(w, h) * 0.85);
      gr.addColorStop(0, C.rgba('#FFC83D', 0.45 * o.glow)); gr.addColorStop(1, C.rgba('#FFC83D', 0));
      ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = gr; ctx.fillRect(-w, -h, w * 2, h * 2); ctx.restore();
    }
    S.shadowGroup(ctx, g => {
      S.roundRect(g, -w / 2, -h / 2, w, h, 18, '#F3E7CC');
      S.cel(g, c => S.addRoundRect(c, -w / 2, -h / 2, w, h, 18), '#F3E7CC', '#DCCBA6', 6, 6);
      S.roundRect(g, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 11, null, '#B08A45', 3);
      S.roundRect(g, -w / 2 + 12, -h / 2 + 12, w - 24, 70, [11, 11, 0, 0], '#1A1620');
    }, { scale: 1, dx: 8 + lift * 14, dy: 10 + lift * 22, blur: 12 + lift * 18, color: `rgba(0,0,0,${0.45 + lift * 0.1})` });
    ctx.font = `400 50px Anton`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const tag = 'RULE ', num = String(o.num ?? 1), tw = ctx.measureText(tag + num).width, nw = ctx.measureText(num).width;
    ctx.fillStyle = '#FFFFFF'; ctx.textAlign = 'left';
    ctx.fillText(tag, -tw / 2, -h / 2 + 49);
    ctx.fillStyle = '#FFC83D'; ctx.fillText(num, -tw / 2 + tw - nw, -h / 2 + 49);
    const lines = o.text || [];
    lines.forEach((l, i) => S.label(ctx, l, 0, -h / 2 + 122 + i * 40, 29, { color: '#2A2230', weight: 900 }));
    if (o.stamp) {
      ctx.save(); ctx.translate(w * 0.18, h / 2 - 58); ctx.rotate(-0.16);
      S.roundRect(ctx, -86, -24, 172, 48, 8, null, '#C8323F', 4);
      S.label(ctx, o.stamp, 0, 1, 24, { color: '#C8323F', weight: 1000 });
      ctx.restore();
    }
    ctx.restore();
  };
  // ================================================================ v2 game-UI widgets (our own design: dark slate,
  // gold trim, chunky ink-edged caps; nothing copied from an OS or a specific game)
  const SLATE = '#141826', SLATE2 = '#1E2436', TRIM = '#C9A24A', TXT = '#E8ECF6';

  // ---- right-click context menu
  const MENU_HEAD = 46, MENU_ROW = 52, MENU_PAD = 10;
  const menuItems = o => (o.items || ['Open', 'Inspect']).map(it => (typeof it === 'string' ? { label: it } : it));
  K.menuRow = (x, y, i, o = {}) => [x + (o.w || 340) * 0.42, y + MENU_HEAD + MENU_PAD + i * MENU_ROW + MENU_ROW / 2];
  K.menu = (ctx, x, y, o = {}) => {
    const pop = o.pop ?? 1; if (pop <= 0) return;
    const items = menuItems(o), w = o.w || 340, h = MENU_HEAD + MENU_PAD * 2 + items.length * MENU_ROW;
    const e = S.ease.easeOutBack(clamp(pop), 2.0);
    ctx.save(); ctx.translate(x, y); ctx.scale(lerp(0.25, 1, e), lerp(0.1, 1, e)); ctx.globalAlpha *= clamp(pop * 3);
    S.shadowGroup(ctx, g => {
      S.roundRect(g, -4, -4, w + 8, h + 8, 18, INK);
      S.roundRect(g, 0, 0, w, h, 14, SLATE);
      S.roundRect(g, 0, 0, w, MENU_HEAD, [14, 14, 0, 0], SLATE2);
      g.fillStyle = '#0B0E16'; g.fillRect(0, MENU_HEAD, w, 3);
      S.roundRect(g, 6, 6, w - 12, h - 12, 10, null, C.rgba(GOLD, 0.35), 2);
      // the "corner" tab that points at the click
      S.poly(g, [[0, 0], [26, 0], [0, 26]], TRIM);
    }, { scale: 1, dx: 8, dy: 11, blur: 14, color: 'rgba(0,0,0,0.5)' });
    S.label(ctx, o.title || 'ACTIONS', 36, MENU_HEAD / 2 + 1, 19, { align: 'left', color: GOLD, weight: 1000 });
    // hover bar (fractional index slides between rows)
    const hv = o.hover;
    if (hv != null && hv >= 0) {
      const hy = MENU_HEAD + MENU_PAD + hv * MENU_ROW;
      const fl = o.pick > 0 && o.pick < 1 ? (Math.sin(o.pick * Math.PI * 6) > 0 ? 1 : 0) : 0;
      S.roundRect(ctx, 8, hy + 4, w - 16, MENU_ROW - 8, 10, fl ? '#FFFFFF' : GOLD);
      S.roundRect(ctx, 8, hy + MENU_ROW - 12, w - 16, 8, [0, 0, 10, 10], fl ? '#E9ECF4' : '#E0A93A');
    }
    items.forEach((it, i) => {
      const ry = MENU_HEAD + MENU_PAD + i * MENU_ROW + MENU_ROW / 2;
      const on = hv != null && Math.abs(hv - i) < 0.5;
      const col = on ? INK : (it.color || TXT);
      // row gem
      ctx.save(); ctx.translate(30, ry); ctx.rotate(Math.PI / 4);
      S.roundRect(ctx, -6, -6, 12, 12, 3, on ? INK : (it.color || '#6E7894'));
      ctx.restore();
      S.label(ctx, it.label, 50, ry, 24, { align: 'left', color: col, weight: 900 });
      if (it.key) {
        const kw = 12 + it.key.length * 12;
        S.roundRect(ctx, w - 22 - kw, ry - 14, kw, 28, 7, on ? C.rgba(INK, 0.18) : 'rgba(255,255,255,0.08)');
        S.label(ctx, it.key, w - 22 - kw / 2, ry + 1, 16, { color: on ? INK : 'rgba(232,236,246,0.55)', weight: 900 });
      }
    });
    ctx.restore();
  };

  // ---- chunky game button
  K.button = (ctx, x, y, w, h, o = {}) => {
    const p = clamp(o.press || 0), dep = o.depth ?? 10, r = o.r ?? 14;
    const col = o.color || '#FFC83D', side = C.shade(col, -0.42), top = y + dep * p;
    if (o.glow > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      const gr = ctx.createRadialGradient(x + w / 2, y + h / 2, 4, x + w / 2, y + h / 2, Math.max(w, h) * 0.7);
      gr.addColorStop(0, C.rgba(col, 0.5 * o.glow)); gr.addColorStop(1, C.rgba(col, 0));
      ctx.fillStyle = gr; ctx.fillRect(x - w, y - h, w * 3, h * 3); ctx.restore();
    }
    S.shadowGroup(ctx, g => {
      S.roundRect(g, x - 4, top - 4, w + 8, h + dep * (1 - p) + 8, r + 4, INK);
      S.roundRect(g, x, top + 6, w, h + dep * (1 - p) - 6, r, side);
      S.roundRect(g, x, top, w, h, r, col);
      S.roundRect(g, x + 7, top + 5, w - 14, h * 0.34, [r - 5, r - 5, 6, 6], C.rgba('#FFFFFF', 0.3 - 0.15 * p));
    }, { scale: 1, dx: 5 * (1 - p) + 2, dy: 7 * (1 - p) + 3, blur: 8, color: 'rgba(0,0,0,0.45)' });
    const cx = x + w / 2, cy = top + h / 2;
    if (o.icon) o.icon(ctx, o.label ? x + h * 0.5 : cx, cy, h * 0.3);
    if (o.label) S.label(ctx, o.label, o.icon ? x + h * 0.5 + (w - h * 0.5) / 2 : cx, cy + 1, o.size || 24, { color: o.textColor || INK, weight: 1000 });
  };
  // arrow icon for buttons (fat chevron arrow)
  K.arrowIcon = (dir = 0, col = INK) => (ctx, cx, cy, r) => {
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(dir);
    S.roundPoly(ctx, [[-r, -r * 0.38], [r * 0.15, -r * 0.38], [r * 0.15, -r], [r * 1.15, 0], [r * 0.15, r], [r * 0.15, r * 0.38], [-r, r * 0.38]], r * 0.16, col);
    ctx.restore();
  };

  // ---- tab strip
  const tabGeo = o => ({ tw: o.tw || 150, th: o.th || 54, gap: o.gap ?? 8 });
  K.tabAt = (x, y, i, o = {}) => { const { tw, th, gap } = tabGeo(o); return [x + i * (tw + gap) + tw / 2, y + th / 2]; };
  K.tabs = (ctx, x, y, o = {}) => {
    const tabs = o.tabs || ['MAP', 'BAG', 'RULES'], { tw, th, gap } = tabGeo(o);
    const a = o.active ?? 0, pv = o.prev ?? a, k = clamp(o.k ?? 1), W = tabs.length * (tw + gap) - gap;
    S.shadowGroup(ctx, g => {
      S.roundRect(g, x - 10, y + th - 2, W + 20, 16, 8, INK);
      S.roundRect(g, x - 6, y + th + 1, W + 12, 9, 5, SLATE2);
      tabs.forEach((lb, i) => {
        const act = i === a ? k : i === pv ? 1 - k : 0;
        const pr = o.press && o.press.i === i ? clamp(o.press.k) : 0;
        const tx = x + i * (tw + gap), ty = y - 10 * act + 6 * pr, hh = th + 10 * act - 6 * pr;
        S.roundRect(g, tx - 4, ty - 4, tw + 8, hh + 6, [16, 16, 0, 0], INK);
        S.roundRect(g, tx, ty, tw, hh, [12, 12, 0, 0], C.mix(SLATE2, '#FFC83D', act));
        S.roundRect(g, tx, ty + hh - 8, tw, 8, 0, C.mix('#141826', '#E0962E', act));
        S.roundRect(g, tx + 6, ty + 5, tw - 12, 10, 5, C.rgba('#FFFFFF', 0.08 + 0.22 * act));
      });
    }, { scale: 1, dx: 6, dy: 8, blur: 10, color: 'rgba(0,0,0,0.45)' });
    tabs.forEach((lb, i) => {
      const act = i === a ? k : i === pv ? 1 - k : 0;
      const pr = o.press && o.press.i === i ? clamp(o.press.k) : 0;
      S.label(ctx, lb, x + i * (tw + gap) + tw / 2, y + th / 2 - 4 * act + 6 * pr, 22, { color: act > 0.5 ? INK : '#AEB6C9', weight: 1000 });
    });
    // the gold underline slides prev -> active
    const ux = lerp(x + pv * (tw + gap), x + a * (tw + gap), S.ease.easeOutBack(k, 1.6));
    S.roundRect(ctx, ux + 10, y + th + 2, tw - 20, 6, 3, GOLD);
  };

  // ---- slider
  K.sliderKnob = (x, y, w, v) => [x + w * clamp(v), y];
  K.slider = (ctx, x, y, w, o = {}) => {
    const v = clamp(o.value ?? 0.5), gb = clamp(o.grab || 0), kx = x + w * v;
    if (o.label) S.label(ctx, o.label, x, y - 38, 19, { align: 'left', color: 'rgba(232,236,246,0.75)', weight: 900 });
    S.roundRect(ctx, x - 5, y - 12, w + 10, 24, 12, INK);
    S.roundRect(ctx, x, y - 7, w, 14, 7, '#2A3044');
    if (v > 0.01) S.roundRect(ctx, x, y - 7, Math.max(14, w * v), 14, 7, GOLD);
    const R = 19 * (1 + 0.18 * gb);
    S.shadowGroup(ctx, g => {
      S.circle(g, kx, y, R + 4.5, INK);
      S.cel(g, c => { c.moveTo(kx + R, y); c.arc(kx, y, R, 0, TAU); }, '#FFFFFF', SHADE, 4, 4);
      S.circle(g, kx, y, R * 0.36, C.mix('#AEB6C9', GOLD, gb));
    }, { scale: 1, dx: 4 + 4 * gb, dy: 6 + 6 * gb, blur: 8, color: 'rgba(0,0,0,0.45)' });
    if (gb > 0.05) {
      ctx.save(); ctx.globalAlpha *= clamp(gb * 2);
      const by = y - 52 - 8 * gb;
      S.roundRect(ctx, kx - 34, by - 18, 68, 36, 10, INK);
      S.poly(ctx, [[kx - 8, by + 17], [kx + 8, by + 17], [kx, by + 27]], INK);
      S.label(ctx, Math.round(v * 100) + '%', kx, by + 1, 19, { color: GOLD, weight: 1000 });
      ctx.restore();
    }
  };

  // ---- minimap corner HUD with the MOVE button
  const MM = K.MINIMAP = { w: 380, h: 214, btn: (x, y) => [x + 380 - 70, y + 214 - 64] };
  K.minimap = (ctx, x, y, o = {}) => {
    const { w, h } = MM, rooms = o.rooms || [[0, 1, 'ROOM'], [1, 1, 'HALL'], [2, 1, '?'], [1, 0, '?']];
    const at = o.at || [0, 1], vis = o.visited ?? 1, t = o.t || 0;
    S.shadowGroup(ctx, g => {
      S.roundRect(g, x - 4, y - 4, w + 8, h + 8, 20, INK);
      S.roundRect(g, x, y, w, h, 16, 'rgba(16,19,30,0.92)');
      S.roundRect(g, x + 7, y + 7, w - 14, h - 14, 11, null, C.rgba(GOLD, 0.3), 2);
    }, { scale: 1, dx: 8, dy: 10, blur: 14, color: 'rgba(0,0,0,0.5)' });
    S.label(ctx, o.title || 'MAP · B1', x + 24, y + 30, 18, { align: 'left', color: GOLD, weight: 1000 });
    const cell = (cx, cy) => [x + 30 + cx * 74, y + 58 + cy * 54];
    // links
    ctx.strokeStyle = 'rgba(232,236,246,0.25)'; ctx.lineWidth = 6; ctx.lineCap = 'round';
    ctx.beginPath(); rooms.forEach(([cx, cy]) => rooms.forEach(([dx, dy]) => {
      if (Math.abs(cx - dx) + Math.abs(cy - dy) === 1 && (dx > cx || dy > cy)) { const a = cell(cx, cy), b = cell(dx, dy); ctx.moveTo(a[0] + 28, a[1] + 20); ctx.lineTo(b[0] + 28, b[1] + 20); }
    })); ctx.stroke();
    rooms.forEach(([cx, cy, nm], i) => {
      const [px, py] = cell(cx, cy), seen = i < vis + 1;
      S.roundRect(ctx, px, py, 56, 40, 8, seen ? '#2A3044' : '#1A1E2B', i < vis ? null : 'rgba(232,236,246,0.25)', 2);
      S.label(ctx, i < vis ? nm : '?', px + 28, py + 21, 13, { color: i < vis ? 'rgba(232,236,246,0.8)' : 'rgba(232,236,246,0.35)', weight: 900 });
    });
    // you-are-here pip (pulses), gold frame on the current cell
    const [mx, my] = cell(at[0], at[1]);
    S.roundRect(ctx, mx - 3, my - 3, 62, 46, 10, null, GOLD, 3);
    const pr = 0.5 + 0.5 * Math.sin(t * 6);
    S.circle(ctx, mx + 28, my - 10, 8 + 3 * pr, C.rgba(GOLD, 0.3));
    S.circle(ctx, mx + 28, my - 10, 6.5, GOLD, INK, 3);
    // the MOVE button
    const [bx, by] = MM.btn(x, y);
    S.label(ctx, 'MOVE', bx, by - 50, 15, { color: 'rgba(232,236,246,0.7)', weight: 1000 });
    K.button(ctx, bx - 46, by - 30, 92, 56, { press: o.press, glow: o.glow, icon: K.arrowIcon(0, INK), color: '#7FD3FF', depth: 9 });
  };
})();
