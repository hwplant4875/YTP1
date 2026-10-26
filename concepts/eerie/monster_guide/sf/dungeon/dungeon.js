/* =====================================================================================================================
 * dungeon.js : window.DUNGEON, the dungeon set kit for the Monster HR show (style frames SF3 "empty room", SF4 corridor).
 * Needs core/lib_core.js (window.SFX) loaded first. Plain canvas 2D, deterministic (seeded RNG only), every animated
 * part takes t (seconds) so torches flicker the same way on every render.
 *
 * Look (plan 4-3 + 귤멍 rules): flat fills, ONE hard shade tone per material (bottom-right, light from the top-left),
 * no outlines, stepped "pixel" corners on architecture, gradients only for light, fog, blur and vignette, 1-2 % grain.
 *
 * SCENES (full frame, 1920x1080 design space; other canvas sizes are scaled to cover)
 *   DUNGEON.room(ctx, t, o)        SF3 "empty room": cool wall + floor, round arch doorway (right), ONE top-down spotlight.
 *   DUNGEON.corridor(ctx, t, o)    SF4 torch-lit corridor: arcade of arches, receding tunnel, torches, chains, candles.
 *     Both run  xxxBack -> o.actors(ctx, info) -> xxxFront -> DUNGEON.post  and return info. To put characters
 *     between the layers yourself, call the parts (each part applies the design-space fit itself; actors get the
 *     design space too):
 *       DUNGEON.roomBack(ctx, t, o)      L1 far wall (blur 8 px, cached) -> L2 arch doorway (o.doorway(ctx, info) is
 *                                        called clipped inside the doorway, after the passage: knights peeking) ->
 *                                        L3 floor + spotlight floor pool + skull corner
 *       DUNGEON.roomFront(ctx, t, o)     spotlight beam + dust (screen blend: it lights whatever is under it) and
 *                                        L4 foreground chains (blur 3.5 px)
 *       DUNGEON.corridorBack / DUNGEON.corridorFront   same split (L1 far hall + tunnel blur 8 px, L2 arcade + torches
 *                                        + wall chains, L3 floor + candles + skulls, L4 foreground chains blur 4 px)
 *       DUNGEON.post(ctx, t, o)          always-on vignette + grain (o.vignette=0.62, o.grain=0.05 ≈ 1-2 %, o.vigX/vigY)
 *     Shared options:
 *       cam = {x:0, y:0, zoom:1, fx:960, fy:540}   parallax camera: depth 0.35 far, 0.8 arch/torches, 1 floor,
 *                                                  1.45 foreground; zoom pushes in around (fx, fy) per layer
 *       seed = 7                 block jitter / layout seed (the far layer is cached per seed)
 *       spill = {color, amount:0..1, x, y, r}   soft off-screen light from the left (the hook's mint TV glow)
 *       post = false             skip vignette + grain (when compositing more on top, then call DUNGEON.post last)
 *       actors(ctx, info)        draw the cast between back and front
 *     Room options:  spot = {x:860, floorY:620, alpha:0.35, rx:300, ry:60, topW:210, topY:-90} (false = none),
 *                    door = {cx:1500, span:340, springY:286, ring:58}, doorway(ctx, info), skulls=true, skullX=215,
 *                    fgChain=true, farBlur=8, archBlur=0, floorY=540 (wall/floor seam)
 *     Corridor options: torches, candles, skulls, chains, fgChains, window (all default true), floorY=780,
 *                    springY=560, torchY=470, piers=[420, 1500], farBlur=8
 *     info:  room {floorY, contactY (spot floorY = chest contact line), spot, door (arch info), clear:[560, 1160]}
 *            corridor {floorY, contactY, torches:[{x, y}] (flame centres), arches:[arch info], clear:[640, 1280]}
 *
 * BUILDING BLOCKS (ctx in its CURRENT transform; sizes in px at scale 1)
 *   DUNGEON.PAL, DUNGEON.STONE.{dungeon, room}   palettes (stone set = {mortar, base:[dark, mid], edge, shade, void,
 *                                        floor:[a, b], floorMortar})
 *   DUNGEON.flicker(t, seed) -> {n, slow, k, a, lean}     8-12 Hz torch noise (n in -1..1), k = size, a = alpha mult.
 *   DUNGEON.stoneWall(ctx, {x, y, w, h, bw=120, bh=56, gap=3, set, seed, stepped=0.16, shadeW, shade=true, tint(col,x,y)})
 *                                        staggered courses laid from the bottom, per-block value jitter ±6 %, one hard
 *                                        shade (bottom-right), stepped "pixel stair" notches on some corners
 *   DUNGEON.blockPoly(x, y, w, h, notch) / DUNGEON.drawBlock(ctx, x, y, w, h, col, shade, shadeW, notch)
 *   DUNGEON.arch(ctx, o) -> info         round arch in a wall face. o: cx, floorY, span, springY, ring=0.16*span,
 *                                        n=9 voussoirs (odd: keystone), set, seed, stone, stoneShade, vp={x,y} +
 *                                        depth=0.12 (wall-thickness reveal toward the vanishing point), revealCol,
 *                                        passFloorCol, voidCol (null = leave what is behind), inside(ctx, info),
 *                                        bars=0 (cell bars), quoins / imposts / keystone / threshold = true.
 *                                        Voussoirs have a stepped (square-cut) extrados.
 *                                        info: {opening(ctx), back(ctx) (sub-paths for clipping), cx, r, springY,
 *                                        floorY, backCx, backR, backSpringY, backFloorY, vp, kb}
 *   DUNGEON.archOpening(ctx, cx, floorY, r, springY)   adds the opening sub-path
 *   DUNGEON.floor(ctx, {y0, y1, x0, x1, vp:{x,y}, rows=7, sw=150, set, seed, gap=2, lip=0.09, cracks=0.07, ao=true})
 *                                        flagstones in perspective, one hard shade on each slab's front lip
 *   DUNGEON.torch(ctx, x, y, s, t, {seed, dir=1, lit=true, embers=3, wind=0}) -> {flame:[x,y], base:[x,y]}
 *                                        iron sconce (plate, arm, strut, cup) + wrapped torch + flame; (x, y) = plate centre
 *   DUNGEON.flame(ctx, x, y, w, h, t, {seed, layers=3, lean, glow=true})   3-layer teardrop (#FFD27A/#FFB04A/#FF7A2F),
 *                                        bottom centre at (x, y); flickers with t
 *   DUNGEON.addTeardrop(ctx, x, y, w, h, lean)          teardrop sub-path
 *   DUNGEON.lightPool(ctx, x, y, r, t, {seed, color=PAL.pool, alpha=0.5, hot=0.16, hotColor, squash=1, steady, mode})
 *                                        soft radial light, screen blend, flickering unless steady
 *   DUNGEON.spill(ctx, {color, amount, x, y, r, squash})  steady off-screen light
 *   DUNGEON.spotlight(ctx, o)            top-down cone. o: x, floorY, topY=-80, topW=200, rx=300, ry=0.2*rx,
 *                                        color='#FFE9A8', alpha=0.35, beam=0.52 (cone strength), soft=16 (edge blur),
 *                                        motes=26, seed, t, part='all'|'floor'|'beam' ('floor' before the cast,
 *                                        'beam' after it so the light falls on them)
 *   DUNGEON.hangChain(ctx, x, y, len, t, {link=22, sway=0.035, swayFreq=0.45, cols, end='shackle'|'hook'|'ring'|'none'})
 *   DUNGEON.swagChain(ctx, p0, p1, sag, {link=20, cols})   DUNGEON.bolt(ctx, x, y, s)   (chains use SFX.drawChain)
 *   DUNGEON.skull(ctx, x, y, r, {rot, look, bone, boneShade, socket})   cute skull (big low-set sockets)
 *   DUNGEON.bone(ctx, x1, y1, x2, y2, w, col, shade)   DUNGEON.skullPile(ctx, x, y, s, {bone, boneShade, socket, layout})
 *   DUNGEON.candles(ctx, x, y, s, t, {seed, n=4, defs:[[dx, h, w]...], lit=true}) -> flame points; (x, y) = floor centre
 *   DUNGEON.cellWindow(ctx, x, y, w, h, {set, bars=4, light=0, skyTop, skyBottom, seed})   barred window, (x, y) =
 *                                        top-left of the opening
 *   DUNGEON.filtered(ctx, drawFn, {blur, mode, alpha, bounds})   draw into a layer, composite once with blur/blend
 *   DUNGEON.cached(key, w, h, drawFn, blur) / DUNGEON.clearCache()   offscreen canvas drawn (and blurred) once
 *   DUNGEON.cam(ctx, cam, depth)  DUNGEON.fitDesign(ctx)  DUNGEON.jitter(col, k)
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX;
  if (!S) throw new Error('dungeon.js needs lib_core.js (window.SFX) loaded first');
  const C = S.color, TAU = Math.PI * 2, clamp = S.clamp, lerp = S.lerp;
  const D = window.DUNGEON = {};
  D.version = '1.0';

  // ------------------------------------------------------------------------------------------------ palette
  D.PAL = {
    void: '#14121A', mortar: '#1C1A22', dark: '#2A2733', mid: '#3D3946', edge: '#57525F',
    torchCore: '#FFD27A', torchFlame: '#FFB04A', torchOuter: '#FF7A2F', pool: '#6B4A3A',
    roomWall: '#1A2329', roomFloor: '#26323A', spot: '#FFE9A8',
    iron: '#3A3D46', ironShade: '#24262D', ironLight: '#5E636E',
    chain: { base: '#4C505B', shade: '#2C2E35', light: '#6E7380' },
    chainFG: { base: '#2B2A33', shade: '#16151B', light: '#3A3844' },
    bone: '#A39A8B', boneShade: '#7A7366', socket: '#18141A',
    wax: '#AFA592', waxShade: '#81786A', wick: '#2A2224',
    wood: '#4A3D33', woodShade: '#32291F', wrap: '#2E2622', wrapLight: '#443830',
  };
  D.STONE = {
    dungeon: { mortar: '#1C1A22', base: ['#2A2733', '#3D3946'], edge: '#57525F', shade: '#221F2A', void: '#14121A', floor: ['#25222E', '#2C2835'], floorMortar: '#1D1A24' },
    room: { mortar: '#121A1F', base: ['#182128', '#1D272E'], edge: '#2F3B44', shade: '#121A1F', void: '#080B0E', floor: ['#232E35', '#27323A'], floorMortar: '#1C252B' },
  };

  // ------------------------------------------------------------------------------------------------ helpers
  const jitter = (col, k) => { const [r, g, b] = C.parse(col); return C.hex(r * (1 + k), g * (1 + k), b * (1 + k)); };
  D.jitter = jitter;

  D.flicker = (t, seed = 1) => {
    const h = S.hash;
    const f1 = 8 + 4 * h(seed * 3.1), f2 = 8 + 4 * h(seed * 5.7 + 1), f3 = 8 + 4 * h(seed * 7.3 + 2);
    const n = 0.5 * Math.sin(TAU * f1 * t + h(seed + 11) * TAU) + 0.3 * Math.sin(TAU * f2 * t + h(seed + 12) * TAU)
      + 0.2 * Math.sin(TAU * f3 * t + h(seed + 13) * TAU);
    const slow = 0.6 * Math.sin(TAU * 1.3 * t + h(seed + 14) * TAU) + 0.4 * Math.sin(TAU * 2.1 * t + h(seed + 15) * TAU);
    return { n, slow, k: 1 + 0.07 * n, a: 1 + 0.1 * n, lean: 0.09 * slow + 0.035 * n };
  };

  const _cache = {};
  D.cached = (key, w, h, drawFn, blur = 0) => {
    if (_cache[key]) return _cache[key];
    const a = document.createElement('canvas'); a.width = w; a.height = h;
    drawFn(a.getContext('2d'));
    if (!blur) return (_cache[key] = a);
    const b = document.createElement('canvas'); b.width = w; b.height = h;
    const g = b.getContext('2d'); g.filter = `blur(${blur}px)`; g.drawImage(a, 0, 0);
    return (_cache[key] = b);
  };
  D.clearCache = () => { for (const k in _cache) delete _cache[k]; };

  D.cam = (ctx, cam, depth) => {
    if (!cam) return;
    const z = 1 + ((cam.zoom ?? 1) - 1) * depth, fx = cam.fx ?? 960, fy = cam.fy ?? 540;
    ctx.translate(fx, fy); ctx.scale(z, z); ctx.translate(-fx - (cam.x || 0) * depth, -fy - (cam.y || 0) * depth);
  };

  // draw fn into an offscreen layer and composite it once with a CSS filter (blur) and/or blend mode
  D.filtered = (ctx, drawFn, { blur = 0, mode = 'source-over', alpha = 1, bounds } = {}) => {
    const L = S.layer(ctx, drawFn, bounds, blur * 3 + 4);
    if (!L) return;
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = mode; ctx.globalAlpha *= alpha;
    if (blur) ctx.filter = `blur(${blur}px)`;
    ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x, L.y, L.w, L.h);
    ctx.restore();
    L.release();
  };

  // ------------------------------------------------------------------------------------------------ stone blocks
  // polygon of a block with an optional stepped notch on one corner (귤멍 pixel-stair grammar)
  function blockPoly(x, y, w, h, notch) {
    if (!notch) return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
    const { corner, s, steps } = notch; // corner 0 tl, 1 tr, 2 br, 3 bl
    if (corner === 0) return stairTL(x, y, w, h, s, steps);
    if (corner === 1) return mirrorX(stairTL(0, y, w, h, s, steps), x, w);
    if (corner === 2) return mirrorY(mirrorX(stairTL(0, 0, w, h, s, steps), x, w), y, h);
    return mirrorY(stairTL(x, 0, w, h, s, steps), y, h);
  }
  function dedupe(P) { return P.filter((p, i) => i === 0 || p[0] !== P[i - 1][0] || p[1] !== P[i - 1][1]); }
  function stairTL(x, y, w, h, s, steps) { // block with its top-left corner cut into `steps` stairs of size s
    const Q = [[x, y + h], [x, y + s * steps]];
    for (let i = 0; i < steps; i++) { Q.push([x + s * (i + 1), y + s * (steps - i)]); Q.push([x + s * (i + 1), y + s * (steps - i - 1)]); }
    Q.push([x + w, y]); Q.push([x + w, y + h]);
    return dedupe(Q);
  }
  function mirrorX(P, x, w) { return P.map(([px, py]) => [x + w - px, py]).reverse(); }
  function mirrorY(P, y, h) { return P.map(([px, py]) => [px, y + h - py]).reverse(); }
  D.blockPoly = blockPoly;

  // one flat block + one hard shade (bottom-right) + optional notch
  function drawBlock(ctx, x, y, w, h, col, shadeCol, shadeW, notch) {
    const P = blockPoly(x, y, w, h, notch);
    if (shadeCol && shadeW > 0) S.cel(ctx, c => S.addPoly(c, P), col, shadeCol, shadeW, shadeW);
    else S.poly(ctx, P, col);
  }
  D.drawBlock = drawBlock;

  D.stoneWall = (ctx, o) => {
    const set = o.set || D.STONE.dungeon, r = S.rng(o.seed ?? 3);
    const x = o.x, y = o.y, w = o.w, h = o.h, bw = o.bw ?? 120, bh = o.bh ?? 56, gap = o.gap ?? 3;
    const stepped = o.stepped ?? 0.16, sh = o.shade === false ? 0 : (o.shadeW ?? Math.max(2, Math.round(bh * 0.1)));
    const shadeCol = o.shadeCol || set.shade;
    ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
    ctx.fillStyle = o.mortar || set.mortar; ctx.fillRect(x, y, w, h);
    const rows = Math.ceil(h / bh) + 1;
    for (let row = 0; row < rows; row++) {
      const yy = y + h - (row + 1) * bh + (o.yOff || 0); // rows laid from the bottom up (courses sit on the floor)
      let xx = x - ((row % 2) ? bw * 0.5 : 0) - bw * r.range(0, 0.35);
      while (xx < x + w) {
        const ww = bw * r.pick([0.7, 0.85, 1, 1, 1.15, 1.3]);
        const k = r.range(-0.06, 0.06);
        const base = C.mix(set.base[0], set.base[1], o.mix ?? r.range(0.15, 0.85));
        let col = jitter(base, k);
        if (o.tint) col = o.tint(col, xx + ww / 2, yy + bh / 2);
        const notch = r() < stepped ? { corner: r.int(0, 3), s: Math.max(3, Math.round(bh * r.pick([0.14, 0.18]))), steps: r.pick([1, 2, 2]) } : null;
        drawBlock(ctx, xx + gap / 2, yy + gap / 2, ww - gap, bh - gap, col, o.shade === false ? null : jitter(shadeCol, k * 0.5), sh, notch);
        xx += ww;
      }
    }
    ctx.restore();
  };

  // ------------------------------------------------------------------------------------------------ arch
  D.archOpening = (ctx, cx, floorY, r, springY) => {
    ctx.moveTo(cx - r, floorY); ctx.lineTo(cx - r, springY); ctx.arc(cx, springY, r, Math.PI, TAU, false);
    ctx.lineTo(cx + r, floorY); ctx.closePath();
  };
  const scaleAbout = (p, vp, k) => [vp.x + (p[0] - vp.x) * k, vp.y + (p[1] - vp.y) * k];

  D.arch = (ctx, o) => {
    const set = o.set || D.STONE.dungeon, rng = S.rng(o.seed ?? 5);
    const cx = o.cx, floorY = o.floorY, span = o.span, r = span / 2, springY = o.springY;
    const ring = o.ring ?? span * 0.16, n = o.n ?? 9;
    const vp = o.vp || { x: 960, y: springY }, kb = 1 - (o.depth ?? 0.12); // back face = front scaled toward vp
    const stoneA = o.stone || C.mix(set.base[1], set.edge, 0.45), stoneShade = o.stoneShade || set.shade;
    const shW = Math.max(2, Math.round(ring * 0.11));
    const info = {
      cx, r, span, springY, floorY, ring,
      opening: c => D.archOpening(c, cx, floorY, r, springY),
      back: c => { // back-face opening (what you see through); runs down past the floor so the inside can use it
        const bc = scaleAbout([cx, springY], vp, kb);
        c.moveTo(bc[0] - r * kb, floorY + 400); c.lineTo(bc[0] - r * kb, bc[1]); c.arc(bc[0], bc[1], r * kb, Math.PI, TAU, false);
        c.lineTo(bc[0] + r * kb, floorY + 400); c.closePath();
      },
      backFloorY: scaleAbout([cx, floorY], vp, kb)[1],
      backCx: scaleAbout([cx, springY], vp, kb)[0], backSpringY: scaleAbout([cx, springY], vp, kb)[1], backR: r * kb, vp, kb,
    };
    const BIG = 1e4;

    // 1. reveal (wall thickness: front opening minus back opening), inside, passage floor
    ctx.save();
    ctx.beginPath(); info.opening(ctx); ctx.clip();
    ctx.beginPath(); ctx.rect(cx - BIG, springY - BIG, 2 * BIG, 2 * BIG); info.back(ctx);
    ctx.fillStyle = o.revealCol || C.mix(set.shade, set.base[0], 0.5); ctx.fill('evenodd');
    // voussoir joints on the reveal run toward the vanishing point
    ctx.save(); ctx.beginPath(); ctx.rect(cx - BIG, springY - BIG, 2 * BIG, 2 * BIG); info.back(ctx); ctx.clip('evenodd');
    ctx.strokeStyle = set.mortar; ctx.lineWidth = 2.5;
    for (let i = 1; i < n; i++) {
      const a = Math.PI + (i / n) * Math.PI, p = [cx + Math.cos(a) * r, springY + Math.sin(a) * r], q = scaleAbout(p, vp, kb);
      ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke();
    }
    ctx.restore();
    ctx.save(); ctx.beginPath(); info.back(ctx); ctx.clip();
    if (o.voidCol !== null) { ctx.fillStyle = o.voidCol || set.void; ctx.fillRect(cx - r - 10, springY - r - 10, span + 20, floorY - springY + r + 420); }
    if (o.inside) o.inside(ctx, info);
    ctx.restore();
    // passage floor (the wall's thickness at floor level) in front of whatever is inside
    ctx.fillStyle = o.passFloorCol || (set.floor && set.floor[0]) || set.base[0];
    ctx.fillRect(cx - r - 10, info.backFloorY, span + 20, floorY - info.backFloorY + 4);
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(cx - r - 10, info.backFloorY, span + 20, 3);
    ctx.restore();

    // 2. cell bars (in the front face plane)
    if (o.bars) {
      const nb = o.bars, bwid = Math.max(6, span * 0.022);
      ctx.save(); ctx.beginPath(); info.opening(ctx); ctx.clip();
      for (let i = 0; i < nb; i++) {
        const bx = cx - r + (span / (nb + 1)) * (i + 1);
        S.cel(ctx, c => S.addRoundRect(c, bx - bwid / 2, springY - r - 20, bwid, floorY - springY + r + 20, bwid / 2), D.PAL.iron, D.PAL.ironShade, bwid * 0.35, 0);
      }
      for (const yy of [springY + (floorY - springY) * 0.12, floorY - (floorY - springY) * 0.18]) {
        S.cel(ctx, c => S.addRoundRect(c, cx - r, yy - bwid * 0.6, span, bwid * 1.2, bwid * 0.4), D.PAL.iron, D.PAL.ironShade, 0, bwid * 0.4);
        for (let i = 0; i < nb; i++) { const bx = cx - r + (span / (nb + 1)) * (i + 1); S.circle(ctx, bx, yy, bwid * 0.42, D.PAL.ironLight); }
      }
      ctx.restore();
    }

    // 3. jamb quoins (alternating long/short, stepped outline) from the floor to the springline
    if (o.quoins !== false) {
      const qh = ring * 0.92, rows = Math.max(1, Math.round((floorY - springY) / qh)), hq = (floorY - springY) / rows;
      for (const side of [-1, 1]) {
        for (let i = 0; i < rows; i++) {
          const long = (i % 2 === 0), qw = ring * (long ? 1.18 : 0.8), yy = floorY - (i + 1) * hq;
          const x0 = side < 0 ? cx - r - qw : cx + r;
          const col = jitter(stoneA, rng.range(-0.06, 0.06));
          drawBlock(ctx, x0 + 1.5, yy + 1.5, qw - 3, hq - 3, col, stoneShade, shW, null);
        }
      }
    }
    // 4. imposts (springline caps, stepped two-tier)
    if (o.imposts !== false) {
      const ih = ring * 0.3;
      for (const side of [-1, 1]) {
        const w1 = ring * 1.5, x1 = side < 0 ? cx - r - w1 + ring * 0.12 : cx + r - ring * 0.12;
        drawBlock(ctx, x1, springY - ih * 0.15, w1, ih, jitter(set.edge, -0.04), stoneShade, shW, null);
        const w2 = ring * 1.25, x2 = side < 0 ? cx - r - w2 + ring * 0.02 : cx + r - ring * 0.02;
        drawBlock(ctx, x2, springY + ih * 0.85, w2, ih * 0.55, jitter(stoneA, -0.05), stoneShade, Math.max(2, shW * 0.6), null);
      }
    }
    // 5. voussoirs with a stepped extrados (square-cut outer ends) + keystone
    const R0 = r, R1 = r + ring, gapA = 2.4 / r;
    for (let i = 0; i < n; i++) {
      const isKey = o.keystone !== false && i === (n - 1) / 2;
      let a0 = Math.PI + (i / n) * Math.PI + gapA / 2, a1 = Math.PI + ((i + 1) / n) * Math.PI - gapA / 2;
      const am = (a0 + a1) / 2;
      if (isKey) { const ext = (a1 - a0) * 0.18; a0 -= ext; a1 += ext; }
      const R1k = isKey ? R1 + ring * 0.28 : R1;
      const p0 = [cx + Math.cos(a0) * R0, springY + Math.sin(a0) * R0], p1 = [cx + Math.cos(a1) * R0, springY + Math.sin(a1) * R0];
      const q0 = [cx + Math.cos(a0) * R1k, springY + Math.sin(a0) * R1k], q1 = [cx + Math.cos(a1) * R1k, springY + Math.sin(a1) * R1k];
      let corner;
      if (isKey) corner = null;
      else if (Math.cos(am) < 0) corner = [q0[0], q1[1]]; // left half: up from q0, then right to q1
      else corner = [q1[0], q0[1]];                        // right half: right from q0, then down to q1
      const P = [p0];
      const steps = 12;
      for (let k = 1; k < steps; k++) { const a = lerp(a0, a1, k / steps); P.push([cx + Math.cos(a) * R0, springY + Math.sin(a) * R0]); }
      P.push(p1, q1);
      if (isKey) { const topY = Math.min(q0[1], q1[1]) - ring * 0.05, e = ring * 0.05; P.push([q1[0] + e, topY], [q0[0] - e, topY]); }
      else P.push(corner);
      P.push(q0);
      const col = isKey ? jitter(set.edge, 0.03) : jitter(stoneA, rng.range(-0.06, 0.06));
      S.cel(ctx, c => S.addPoly(c, P), col, stoneShade, shW, shW);
    }
    // 6. threshold slab
    if (o.threshold !== false) {
      const th = Math.max(8, ring * 0.22);
      drawBlock(ctx, cx - r - ring * 0.3, floorY - th * 0.35, span + ring * 0.6, th, jitter(stoneA, -0.08), stoneShade, Math.max(2, shW * 0.6), null);
    }
    return info;
  };

  // ------------------------------------------------------------------------------------------------ floor
  D.floor = (ctx, o) => {
    const set = o.set || D.STONE.dungeon, r = S.rng(o.seed ?? 9);
    const y0 = o.y0, y1 = o.y1, x0 = o.x0 ?? -400, x1 = o.x1 ?? 2320, vp = o.vp || { x: 960, y: y0 - 240 };
    const rowsN = o.rows ?? 7, sw = o.sw ?? 150;
    const ratio = (y1 - vp.y) / (y0 - vp.y), g = Math.pow(ratio, 1 / rowsN);
    const ys = []; for (let i = 0; i <= rowsN; i++) ys.push(vp.y + (y0 - vp.y) * Math.pow(g, i));
    ctx.fillStyle = set.floorMortar || set.mortar; ctx.fillRect(x0, y0, x1 - x0, y1 - y0 + 40);
    const X = (u, y) => vp.x + (u - vp.x) * (y - vp.y) / (y0 - vp.y); // u = x on the seam row
    for (let i = 0; i < rowsN; i++) {
      const ya = ys[i], yb = ys[i + 1], sc = (ya - vp.y) / (y0 - vp.y), gp = (o.gap ?? 2) * sc;
      const ua0 = vp.x + (x0 - vp.x) / ((ya - vp.y) / (y0 - vp.y)), ua1 = vp.x + (x1 - vp.x) / ((ya - vp.y) / (y0 - vp.y));
      let u = ua0 - sw * ((i % 2) ? 0.5 : 0) - sw * r.range(0, 0.3);
      while (u < ua1) {
        const w = sw * r.pick([0.8, 1, 1, 1.2, 1.4]);
        const k = r.range(-0.06, 0.06);
        const col = jitter(C.mix(set.floor[0], set.floor[1], r()), k);
        const ga = gp, gb = gp * (yb - vp.y) / (ya - vp.y);
        const P = [[X(u, ya) + ga, ya + ga * 0.6], [X(u + w, ya) - ga, ya + ga * 0.6], [X(u + w, yb) - gb, yb - gb * 0.6], [X(u, yb) + gb, yb - gb * 0.6]];
        const fc = o.tint ? o.tint(col, (P[0][0] + P[2][0]) / 2, (ya + yb) / 2) : col;
        S.poly(ctx, P, fc);
        // one hard shade: the front lip of the slab (toward the camera)
        if (o.lip !== false) {
          const lh = (yb - ya) * (o.lip ?? 0.09);
          S.poly(ctx, [[P[3][0] + (P[0][0] - P[3][0]) * lh / (yb - ya), P[3][1] - lh], [P[2][0] + (P[1][0] - P[2][0]) * lh / (yb - ya), P[2][1] - lh], P[2], P[3]], C.shade(fc, -0.22));
        }
        // a few hairline cracks (stepped, pixel grammar)
        if (r() < (o.cracks ?? 0.07) && yb - ya > 70) {
          const cxm = (P[0][0] + P[1][0] + P[2][0] + P[3][0]) / 4, cym = (ya + yb) / 2, hh = yb - ya, ww = Math.abs(P[1][0] - P[0][0]);
          const pts = [[cxm - ww * 0.3, cym - hh * 0.2]]; let qx = pts[0][0], qy = pts[0][1];
          for (let k = 0; k < 4; k++) { qx += ww * r.range(0.08, 0.16); pts.push([qx, qy]); qy += hh * r.pick([-0.12, 0.12, 0.16]); pts.push([qx, qy]); }
          ctx.beginPath(); S.addPoly(ctx, pts, false); ctx.strokeStyle = C.shade(fc, -0.3); ctx.lineWidth = Math.max(1.5, hh * 0.035); ctx.lineJoin = 'miter'; ctx.stroke();
        }
        // occasional stepped chip on a front corner (pixel grammar)
        if (r() < (o.chips ?? 0)) {
          const s = (yb - ya) * 0.16, left = r() < 0.5, bx = left ? P[3][0] : P[2][0], by = P[3][1], d = left ? 1 : -1;
          S.poly(ctx, [[bx, by], [bx + d * s * 2, by], [bx + d * s * 2, by - s], [bx + d * s, by - s], [bx + d * s, by - s * 2], [bx, by - s * 2]], set.floorMortar || set.mortar);
        }
        u += w;
      }
    }
    if (o.ao !== false) { // contact darkness under the wall
      const gr = ctx.createLinearGradient(0, y0, 0, y0 + (o.aoH ?? 60));
      gr.addColorStop(0, 'rgba(0,0,0,0.55)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = gr; ctx.fillRect(x0, y0, x1 - x0, o.aoH ?? 60);
    }
    return { rows: ys };
  };

  // ------------------------------------------------------------------------------------------------ light
  D.lightPool = (ctx, x, y, r, t = 0, o = {}) => {
    const f = D.flicker(t, o.seed ?? 1), a = (o.alpha ?? 0.5) * (o.steady ? 1 : f.a), rr = r * (o.steady ? 1 : 1 + 0.02 * f.n);
    ctx.save();
    ctx.globalCompositeOperation = o.mode || 'screen';
    ctx.translate(x, y); ctx.scale(1, o.squash ?? 1);
    const col = o.color || D.PAL.pool;
    let g = ctx.createRadialGradient(0, 0, 0, 0, 0, rr);
    g.addColorStop(0, C.rgba(col, a)); g.addColorStop(0.3, C.rgba(col, a * 0.62)); g.addColorStop(0.62, C.rgba(col, a * 0.22)); g.addColorStop(1, C.rgba(col, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rr, 0, TAU); ctx.fill();
    const hot = (o.hot ?? 0.16) * (o.steady ? 1 : f.a);
    if (hot > 0) {
      const hr = rr * 0.38, hc = o.hotColor || D.PAL.torchFlame;
      g = ctx.createRadialGradient(0, 0, 0, 0, 0, hr);
      g.addColorStop(0, C.rgba(hc, hot)); g.addColorStop(0.5, C.rgba(hc, hot * 0.4)); g.addColorStop(1, C.rgba(hc, 0));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, hr, 0, TAU); ctx.fill();
    }
    ctx.restore();
  };
  D.spill = (ctx, o = {}) => {
    const amt = o.amount ?? 0; if (amt <= 0) return;
    D.lightPool(ctx, o.x ?? -160, o.y ?? 700, o.r ?? 900, 0, { color: o.color || '#3FC9B5', alpha: 0.32 * amt, hot: 0, steady: true, squash: o.squash ?? 0.75 });
  };

  // teardrop: bottom centre (x, y), width w, height h, tip lean (fraction of h)
  function addTeardrop(ctx, x, y, w, h, lean = 0) {
    const r = w / 2, cy = y - r, tx = x + lean * h, ty = y - h;
    ctx.moveTo(tx, ty);
    ctx.bezierCurveTo(tx + r * 0.2, ty + h * 0.32, x + r * 1.04, cy - r * 0.9, x + r, cy);
    ctx.arc(x, cy, r, 0, Math.PI, false);
    ctx.bezierCurveTo(x - r * 1.04, cy - r * 0.9, tx - r * 0.2, ty + h * 0.32, tx, ty);
    ctx.closePath();
  }
  D.addTeardrop = addTeardrop;

  D.flame = (ctx, x, y, w, h, t = 0, o = {}) => {
    const f = D.flicker(t, o.seed ?? 1), lean = (o.lean ?? 0) + f.lean;
    const k = f.k, hk = h * (1 + 0.1 * f.n), wk = w * (1 - 0.03 * f.n);
    const L = [[D.PAL.torchOuter, 1, 1, 0], [D.PAL.torchFlame, 0.72, 0.74, 0.05], [D.PAL.torchCore, 0.44, 0.47, 0.1]].slice(0, o.layers ?? 3);
    const drawIt = g => {
      for (const [col, sw, shh, lift] of L) {
        g.beginPath(); addTeardrop(g, x, y - h * lift * k, wk * sw, hk * shh, lean * (0.6 + 0.4 * sw)); g.fillStyle = col; g.fill();
      }
    };
    if (o.glow === false) drawIt(ctx);
    else S.glow(ctx, drawIt, { blur: Math.max(4, w * 0.35), alpha: 0.55 * f.a, bounds: { x: x - w * 2, y: y - h * 1.6, w: w * 4, h: h * 2 } });
    return { tip: [x + lean * hk, y - hk], base: [x, y] };
  };

  // ------------------------------------------------------------------------------------------------ torch
  D.torch = (ctx, x, y, s = 1, t = 0, o = {}) => {
    const dir = o.dir ?? 1, P = D.PAL, seed = o.seed ?? 1;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    const cupX = 42 * dir, cupY = -10, lean = 0.1 * dir;
    // strut + arm, then the wall plate over their ends
    S.capsule(ctx, 0, 26, cupX * 0.82, cupY + 8, 7, 7, P.ironShade);
    S.cel(ctx, c => S.addCapsule(c, 0, cupY + 2, cupX, cupY + 2, 11), P.iron, P.ironShade, 0, 3.5);
    S.cel(ctx, c => S.addRoundRect(c, -15, -36, 30, 72, 7), P.iron, P.ironShade, 4, 4);
    S.circle(ctx, 0, -24, 3.6, P.ironLight); S.circle(ctx, 0, 24, 3.6, P.ironLight);
    // torch: stick, wrapped head, then the cup ring holding it
    ctx.save(); ctx.translate(cupX, cupY); ctx.rotate(lean);
    S.cel(ctx, c => { c.moveTo(-5, 30); c.lineTo(5, 30); c.lineTo(8, -40); c.lineTo(-8, -40); c.closePath(); }, P.wood, P.woodShade, 3, 0);
    S.cel(ctx, c => S.addRoundRect(c, -13, -72, 26, 36, 9), P.wrap, '#1E1916', 4, 3);
    ctx.beginPath(); ctx.moveTo(-12, -61); ctx.lineTo(12, -55); ctx.moveTo(-12, -49); ctx.lineTo(12, -43); S.paint(ctx, null, P.wrapLight, 3);
    S.cel(ctx, c => { c.moveTo(-15, -6); c.lineTo(15, -6); c.lineTo(10, 14); c.lineTo(-10, 14); c.closePath(); }, P.iron, P.ironShade, 3, 3);
    S.roundRect(ctx, -16, -9, 32, 6, 3, P.ironLight);
    ctx.restore();
    const tip = SFXrot(cupX, cupY, 0, -70, lean);
    if (o.lit !== false) {
      ctx.save(); ctx.translate(tip[0], tip[1]);
      D.flame(ctx, 0, 2, 44, 96, t, { seed, lean: lean * 0.8 + (o.wind || 0) });
      const r = S.rng(seed * 13 + 1);
      for (let i = 0; i < (o.embers ?? 3); i++) { // embers rising
        const per = r.range(0.9, 1.6), ph = r(), u = ((t / per + ph) % 1);
        const ex = r.range(-10, 10) + Math.sin((t + ph) * 5 + i) * 6 * u + lean * 60 * u, ey = -70 - u * 90;
        ctx.globalAlpha = (1 - u) * 0.9;
        S.circle(ctx, ex, ey, 2.4 * (1 - u * 0.6), P.torchCore);
      }
      ctx.restore();
    }
    ctx.restore();
    const fx = x + tip[0] * s, fy = y + tip[1] * s;
    return { flame: [fx, fy - 38 * s], base: [fx, fy] };
  };
  function SFXrot(px, py, dx, dy, a) { const [rx, ry] = S.rot(dx, dy, a); return [px + rx, py + ry]; }

  // ------------------------------------------------------------------------------------------------ chains
  D.bolt = (ctx, x, y, s = 1) => {
    const P = D.PAL;
    S.cel(ctx, c => S.addRoundRect(c, x - 11 * s, y - 11 * s, 22 * s, 22 * s, 5 * s), P.iron, P.ironShade, 3 * s, 3 * s);
    S.circle(ctx, x, y, 4 * s, P.ironLight);
  };
  function resample(pts, step) {
    const out = [pts[0].slice()]; let acc = 0;
    for (let i = 1; i < pts.length; i++) {
      let [ax, ay] = pts[i - 1]; const [bx, by] = pts[i];
      let d = Math.hypot(bx - ax, by - ay);
      while (acc + d >= step) {
        const k = (step - acc) / d; ax = ax + (bx - ax) * k; ay = ay + (by - ay) * k; out.push([ax, ay]); d = Math.hypot(bx - ax, by - ay); acc = 0;
      }
      acc += d;
    }
    return out;
  }
  D.swagChain = (ctx, p0, p1, sag, o = {}) => {
    const link = o.link ?? 20, pts = [];
    for (let i = 0; i <= 60; i++) { const u = i / 60; pts.push([lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) + sag * 4 * u * (1 - u)]); }
    const R = resample(pts, link * 0.7);
    S.drawChain(ctx, R, link, o.cols || D.PAL.chain);
    return R;
  };
  D.hangChain = (ctx, x, y, len, t = 0, o = {}) => {
    const link = o.link ?? 22, n = Math.max(2, Math.round(len / (link * 0.7)));
    const pts = S.chainPoints([x, y], Math.PI / 2, n, link, 1, { t, sway: o.sway ?? 0.035, swayFreq: o.swayFreq ?? 0.45, lag: 1.6 });
    const cols = o.cols || D.PAL.chain;
    S.drawChain(ctx, pts, link, cols);
    const e = pts[pts.length - 1], pe = pts[pts.length - 2], a = Math.atan2(e[1] - pe[1], e[0] - pe[0]) - Math.PI / 2;
    const cc = typeof cols === 'string' ? { base: cols, shade: C.shade(cols, -0.3) } : cols;
    ctx.save(); ctx.translate(e[0], e[1]); ctx.rotate(a);
    const L = link;
    if (o.end === 'hook') {
      ctx.beginPath(); S.addCurve(ctx, [[0, 0], [0, L * 0.9], [-L * 0.1, L * 1.5], [-L * 0.65, L * 1.45], [-L * 0.7, L * 1.05]], 0.5);
      S.paint(ctx, null, cc.shade, L * 0.3); ctx.beginPath();
      S.addCurve(ctx, [[0, 0], [0, L * 0.9], [-L * 0.1, L * 1.5], [-L * 0.65, L * 1.45], [-L * 0.7, L * 1.05]], 0.5); S.paint(ctx, null, cc.base, L * 0.16);
    } else if (o.end === 'shackle' || o.end === 'ring') {
      const R = L * (o.end === 'ring' ? 0.55 : 0.8), th = L * 0.26;
      ctx.beginPath(); ctx.arc(0, R * 0.9, R, 0, TAU); ctx.arc(0, R * 0.9, R - th, 0, TAU, true); ctx.fillStyle = cc.shade; ctx.fill();
      ctx.beginPath(); ctx.arc(-th * 0.25, R * 0.9 - th * 0.25, R - th * 0.25, 0, TAU); ctx.arc(-th * 0.25, R * 0.9 - th * 0.25, R - th * 0.8, 0, TAU, true);
      ctx.fillStyle = cc.base; ctx.fill();
      if (o.end === 'shackle') S.cel(ctx, c => S.addRoundRect(c, -th * 1.1, R * 0.9 - R - th * 0.5, th * 2.2, th * 1.3, th * 0.4), cc.base, cc.shade, 2, 2);
    }
    ctx.restore();
    return pts;
  };

  // ------------------------------------------------------------------------------------------------ skulls
  D.skull = (ctx, x, y, r, o = {}) => {
    const P = D.PAL, bone = o.bone || P.bone, sh = o.boneShade || P.boneShade, sock = o.socket || P.socket;
    ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0);
    const lx = (o.look || 0) * r * 0.08;
    S.cel(ctx, c => {
      c.moveTo(r, 0); c.arc(0, 0, r, 0, TAU);
      S.addRoundRect(c, -r * 0.62, r * 0.25, r * 1.24, r * 0.78, [r * 0.12, r * 0.12, r * 0.3, r * 0.3]);
    }, bone, sh, r * 0.16, r * 0.14);
    // big low-set sockets (our eye rule), nose, teeth
    S.ellipse(ctx, -r * 0.4 + lx, r * 0.2, r * 0.3, r * 0.34, 0, sock);
    S.ellipse(ctx, r * 0.4 + lx, r * 0.2, r * 0.3, r * 0.34, 0, sock);
    ctx.beginPath(); ctx.moveTo(lx - r * 0.1, r * 0.52); ctx.lineTo(lx + r * 0.1, r * 0.52); ctx.lineTo(lx, r * 0.66); ctx.closePath(); ctx.fillStyle = sock; ctx.fill();
    ctx.fillStyle = sh;
    for (let i = -1; i <= 1; i++) ctx.fillRect(lx + i * r * 0.2 - r * 0.025, r * 0.8, r * 0.05, r * 0.2);
    ctx.restore();
  };
  function bone(ctx, x1, y1, x2, y2, w, col, sh) {
    const a = Math.atan2(y2 - y1, x2 - x1), nx = -Math.sin(a) * w * 0.45, ny = Math.cos(a) * w * 0.45;
    S.cel(ctx, c => {
      S.addCapsule(c, x1, y1, x2, y2, w * 0.7);
      for (const [px, py] of [[x1, y1], [x2, y2]]) { c.moveTo(px + nx + w * 0.5, py + ny); c.arc(px + nx, py + ny, w * 0.5, 0, TAU); c.moveTo(px - nx + w * 0.5, py - ny); c.arc(px - nx, py - ny, w * 0.5, 0, TAU); }
    }, col, sh, w * 0.18, w * 0.18);
  }
  D.bone = bone;
  D.skullPile = (ctx, x, y, s = 1, o = {}) => {
    const P = D.PAL, col = o.bone || P.bone, sh = o.boneShade || P.boneShade;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    S.groundShadow(ctx, 0, 0, 230, 34, 0.55);
    bone(ctx, -110, -8, -30, -22, 15, col, sh);
    bone(ctx, 40, -14, 120, -4, 14, col, sh);
    const skulls = o.layout || [
      [-62, -30, 30, -0.15, -1], [0, -32, 33, 0.05, 0], [62, -28, 29, 0.2, 1],
      [-30, -80, 29, -0.1, -1], [32, -78, 28, 0.14, 1], [2, -124, 27, 0.04, 0],
    ];
    for (const [sx, sy, r, rot, look] of skulls) D.skull(ctx, sx, sy, r, { rot, look, bone: col, boneShade: sh, socket: o.socket });
    bone(ctx, -96, -2, 4, 4, 13, col, sh);
    ctx.restore();
  };

  // ------------------------------------------------------------------------------------------------ candles
  D.candles = (ctx, x, y, s = 1, t = 0, o = {}) => {
    const P = D.PAL, r = S.rng(o.seed ?? 21), n = o.n ?? 4;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    S.groundShadow(ctx, 6, 0, 150, 26, 0.5);
    // wax puddle
    S.blob(ctx, [[-62, -2], [-40, -10], [0, -12], [44, -9], [64, -1], [30, 7], [-20, 7]], P.waxShade);
    const defs = o.defs || [[-36, 92, 24], [0, 128, 28], [34, 70, 22], [58, 44, 18]].slice(0, n);
    const flames = [];
    for (const [cx, h, w] of defs) {
      const top = -h;
      // body + one hard shade on the right
      S.cel(ctx, c => { S.addRoundRect(c, cx - w / 2, top, w, h, [w * 0.2, w * 0.2, 3, 3]); }, P.wax, P.waxShade, w * 0.22, 0);
      // melted rim + drips (blobby, flat)
      const nd = r.int(1, 3);
      for (let i = 0; i < nd; i++) {
        const dx = cx + r.range(-w * 0.38, w * 0.38), dl = r.range(h * 0.12, h * 0.42), dw = r.range(w * 0.16, w * 0.24);
        S.capsule(ctx, dx, top + 2, dx, top + dl, dw, dw * 1.25, P.wax);
      }
      S.ellipse(ctx, cx, top + 2, w * 0.5, w * 0.16, 0, P.waxShade);
      ctx.fillStyle = P.wick; ctx.fillRect(cx - 1.5, top - 9, 3, 10);
      flames.push([cx, top - 6, w]);
    }
    for (const [fx, fy, w] of flames) {
      if (o.lit === false) continue;
      D.flame(ctx, fx, fy, w * 0.62, w * 1.45, t, { seed: (o.seed ?? 21) + fx * 0.13, layers: 3, glow: true });
    }
    ctx.restore();
    return flames.map(([fx, fy]) => [x + fx * s, y + fy * s]);
  };

  // ------------------------------------------------------------------------------------------------ cell window
  D.cellWindow = (ctx, x, y, w, h, o = {}) => {
    const set = o.set || D.STONE.dungeon, P = D.PAL, nb = o.bars ?? 4, rr = S.rng(o.seed ?? 31);
    const st = C.mix(set.base[1], set.edge, 0.45), sh = set.shade;
    // stepped stone frame: sill, lintel, side quoins
    drawBlock(ctx, x - 26, y + h - 4, w + 52, 26, jitter(st, -0.03), sh, 4, null);
    drawBlock(ctx, x - 14, y + h + 18, w + 28, 14, jitter(st, -0.1), sh, 3, null);
    drawBlock(ctx, x - 30, y - 34, w + 60, 34, jitter(set.edge, -0.05), sh, 5, { corner: 0, s: 8, steps: 2 });
    for (let i = 0; i < 3; i++) {
      const qh = h / 3;
      drawBlock(ctx, x - 26, y + i * qh + 2, 26, qh - 3, jitter(st, rr.range(-0.06, 0.06)), sh, 4, null);
      drawBlock(ctx, x + w, y + i * qh + 2, 26, qh - 3, jitter(st, rr.range(-0.06, 0.06)), sh, 4, null);
    }
    // opening: cool dim night
    const g = ctx.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, o.skyTop || '#424A5C'); g.addColorStop(1, o.skyBottom || '#262B37');
    ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(x, y, w, h * 0.12); // lintel shadow
    const bw = Math.max(6, w * 0.075);
    for (let i = 0; i < nb; i++) {
      const bx = x + (w / (nb + 1)) * (i + 1);
      S.cel(ctx, c => S.addRoundRect(c, bx - bw / 2, y - 2, bw, h + 4, bw / 2), P.iron, P.ironShade, bw * 0.35, 0);
    }
    S.cel(ctx, c => S.addRoundRect(c, x - 2, y + h * 0.38, w + 4, bw, bw / 2), P.iron, P.ironShade, 0, bw * 0.35);
    // faint cool light falling out of the window (down-right, light from the top-left convention)
    if (o.light) {
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      const lg = ctx.createLinearGradient(x, y, x + w * 1.6, y + h * 3.2);
      lg.addColorStop(0, `rgba(150,165,190,${0.1 * o.light})`); lg.addColorStop(1, 'rgba(150,165,190,0)');
      ctx.fillStyle = lg; ctx.beginPath(); ctx.moveTo(x, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w * 2.3, y + h * 3.6); ctx.lineTo(x + w * 0.9, y + h * 3.6); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  };

  // ------------------------------------------------------------------------------------------------ spotlight
  D.spotlight = (ctx, o = {}) => {
    const x = o.x ?? 860, fy = o.floorY ?? 620, topY = o.topY ?? -80, topW = o.topW ?? 200, rx = o.rx ?? 300, ry = o.ry ?? rx * 0.2;
    const col = o.color || D.PAL.spot, A = o.alpha ?? 0.35, part = o.part || 'all', t = o.t || 0;
    const breathe = 1 + 0.015 * Math.sin(TAU * 0.35 * t);
    if (part === 'all' || part === 'floor') {
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      ctx.translate(x, fy); ctx.scale(1, ry / rx);
      let g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx * 1.25);
      g.addColorStop(0, C.rgba(col, A * 1.1 * breathe)); g.addColorStop(0.5, C.rgba(col, A * 0.95)); g.addColorStop(0.78, C.rgba(col, A * 0.42)); g.addColorStop(1, C.rgba(col, 0));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rx * 1.25, 0, TAU); ctx.fill();
      // wide faint bounce on the floor around the pool
      g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx * 2.6);
      g.addColorStop(0, C.rgba(col, A * 0.22)); g.addColorStop(1, C.rgba(col, 0));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rx * 2.6, 0, TAU); ctx.fill();
      ctx.restore();
    }
    if (part === 'all' || part === 'beam') {
      const cone = c => {
        c.moveTo(x - topW / 2, topY); c.lineTo(x + topW / 2, topY);
        c.lineTo(x + rx, fy); c.ellipse(x, fy, rx, ry, 0, 0, Math.PI, false); c.closePath();
      };
      const coreC = c => {
        const k = 0.55; c.moveTo(x - topW * k / 2, topY); c.lineTo(x + topW * k / 2, topY);
        c.lineTo(x + rx * k, fy); c.ellipse(x, fy, rx * k, ry * k, 0, 0, Math.PI, false); c.closePath();
      };
      D.filtered(ctx, g => {
        const lg = g.createLinearGradient(0, topY, 0, fy + ry);
        lg.addColorStop(0, C.rgba(col, 1)); lg.addColorStop(0.45, C.rgba(col, 0.6)); lg.addColorStop(0.8, C.rgba(col, 0.24)); lg.addColorStop(1, C.rgba(col, 0.16));
        g.fillStyle = lg; g.beginPath(); cone(g); g.fill();
        const cg = g.createLinearGradient(0, topY, 0, fy); cg.addColorStop(0, C.rgba(col, 0.4)); cg.addColorStop(1, C.rgba(col, 0.05));
        g.fillStyle = cg; g.beginPath(); coreC(g); g.fill();
      }, { blur: o.soft ?? 16, mode: 'screen', alpha: A * (o.beam ?? 0.52) * breathe, bounds: { x: x - rx - 60, y: topY - 40, w: rx * 2 + 120, h: fy - topY + ry + 80 } });
      // dust motes drifting in the beam
      const nm = o.motes ?? 26, r = S.rng(o.seed ?? 41);
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      for (let i = 0; i < nm; i++) {
        const v = r(), per = r.range(9, 16), ph = r(), u = ((ph + t / per) % 1);
        const yy = lerp(topY + 60, fy - 10, (v + u) % 1), wHalf = lerp(topW / 2, rx, (yy - topY) / (fy - topY)) * 0.85;
        const xx = x + (r() * 2 - 1) * wHalf + Math.sin(t * 0.6 + i) * 8;
        const tw = 0.5 + 0.5 * Math.sin(t * r.range(1, 3) + i * 1.7);
        ctx.fillStyle = C.rgba(col, (0.18 + 0.22 * tw) * (A / 0.35));
        ctx.beginPath(); ctx.arc(xx, yy, r.range(1.4, 3.2), 0, TAU); ctx.fill();
      }
      ctx.restore();
    }
  };

  // ------------------------------------------------------------------------------------------------ post
  D.post = (ctx, t = 0, o = {}) => {
    S.vignette(ctx, o.vignette ?? 0.62, { inner: o.vigInner ?? 0.42, outer: 1.05, cx: o.vigX, cy: o.vigY });
    if ((o.grain ?? 0.05) > 0) S.grain(ctx, o.grain ?? 0.05, Math.floor(t * 24) + 1);
  };

  // =============================================================================================== SCENE: ROOM
  const DW = 1920, DH = 1080;
  function fitDesign(ctx) { // map the 1920x1080 design space onto the actual canvas
    const W = ctx.canvas.width, H = ctx.canvas.height, k = Math.max(W / DW, H / DH);
    ctx.translate((W - DW * k) / 2, (H - DH * k) / 2); ctx.scale(k, k);
  }
  D.fitDesign = fitDesign;
  const PADX = 420, PADY = 260;

  D.roomBack = (ctx, t = 0, o = {}) => {
    const set = D.STONE.room, P = D.PAL, seed = o.seed ?? 7, cam = o.cam;
    const floorY = o.floorY ?? 540;
    const spot = o.spot === false ? null : Object.assign({ x: 860, floorY: 620, alpha: 0.35, rx: 300, ry: 60, topW: 210, topY: -90, t }, o.spot || {});
    const door = Object.assign({ cx: 1500, span: 340, springY: 286 }, o.door || {});
    const info = { floorY, contactY: spot ? spot.floorY : 620, spot, door: null, clear: [560, 1160] };

    ctx.save(); fitDesign(ctx);
    // ---- layer 1: far (back wall) blurred + cached
    const far = D.cached(`room_far_${seed}`, DW + PADX * 2, DH + PADY * 2, g => {
      g.translate(PADX, PADY);
      g.fillStyle = set.mortar; g.fillRect(-PADX, -PADY, DW + PADX * 2, DH + PADY * 2);
      D.stoneWall(g, { x: -PADX, y: -PADY, w: DW + PADX * 2, h: floorY + PADY, bw: 150, bh: 64, gap: 4, set, seed, stepped: 0.14, shadeW: 8 });
      // plinth course: one protruding row at the base of the wall (darker, stepped top)
      D.stoneWall(g, { x: -PADX, y: floorY - 46, w: DW + PADX * 2, h: 46, bw: 220, bh: 46, gap: 4, set: Object.assign({}, set, { base: [C.shade(set.base[0], -0.12), C.shade(set.base[1], -0.1)] }), seed: seed + 1, stepped: 0, shadeW: 5 });
      g.fillStyle = set.edge; g.globalAlpha = 0.55; g.fillRect(-PADX, floorY - 50, DW + PADX * 2, 5); g.globalAlpha = 1;
    }, o.farBlur ?? 8);
    ctx.save(); D.cam(ctx, cam, 0.35); ctx.drawImage(far, -PADX, -PADY); ctx.restore();
    // vertical light falloff on the wall: darker toward the ceiling (gradient = light, so allowed)
    const wg = ctx.createLinearGradient(0, 0, 0, floorY);
    wg.addColorStop(0, 'rgba(4,6,8,0.55)'); wg.addColorStop(0.55, 'rgba(4,6,8,0.12)'); wg.addColorStop(1, 'rgba(4,6,8,0)');
    ctx.fillStyle = wg; ctx.fillRect(-PADX, -PADY, DW + PADX * 2, floorY + PADY);
    // spotlight spill on the back wall behind the beam (soft, wide)
    if (spot) D.lightPool(ctx, spot.x, floorY - 40, 520, t, { color: P.spot, alpha: 0.075 * (spot.alpha / 0.35), hot: 0, steady: true, squash: 0.85 });

    // ---- layer 2: arch doorway (crisp, very slightly softened so it stays behind the cast)
    ctx.save(); D.cam(ctx, cam, 0.8);
    D.filtered(ctx, g => {
      info.door = D.arch(g, {
        cx: door.cx, floorY, span: door.span, springY: door.springY, ring: door.ring ?? 58, n: 9, set, seed: seed + 2,
        vp: { x: 960, y: 380 }, depth: 0.12, stone: '#25313A', stoneShade: '#141C21', voidCol: set.void,
        revealCol: '#1B252C', passFloorCol: '#1F2A31',
        inside: (c, inf) => {
          // the passage beyond: a corridor receding toward the vanishing point; we see its right wall and floor,
          // faintly lit by a torch further in (unseen). Knights peeking (o.doorway) are drawn on top of this.
          const vpp = inf.vp, top = inf.backSpringY - inf.backR - 40, bx1 = inf.backCx + inf.backR, bf = inf.backFloorY, kf = 0.74;
          const far = (x, y) => [vpp.x + (x - vpp.x) * kf, vpp.y + (y - vpp.y) * kf];
          c.fillStyle = '#05080A'; c.fillRect(inf.cx - inf.r - 80, top - 80, inf.span + 160, floorY - top + 300);
          // floor of the passage
          const f0 = far(inf.cx - inf.r - 80, bf), f1 = far(bx1, bf);
          c.fillStyle = '#10171B'; c.beginPath(); c.moveTo(inf.cx - inf.r - 80, bf); c.lineTo(bx1, bf); c.lineTo(f1[0], f1[1]); c.lineTo(f0[0], f0[1]); c.closePath(); c.fill();
          // right wall of the passage (receding plane) with stone courses converging to the vp
          const w0 = far(bx1, top), w1 = far(bx1, bf);
          c.fillStyle = '#121A1F'; c.beginPath(); c.moveTo(bx1, top); c.lineTo(bx1, bf); c.lineTo(w1[0], w1[1]); c.lineTo(w0[0], w0[1]); c.closePath(); c.fill();
          c.strokeStyle = '#0C1215'; c.lineWidth = 2.5;
          for (let yy = bf - 44; yy > top; yy -= 44) { const q = far(bx1, yy); c.beginPath(); c.moveTo(bx1, yy); c.lineTo(q[0], q[1]); c.stroke(); }
          for (const kk of [0.93, 0.85, 0.78]) { // vertical joints, staggered per course
            const xa = vpp.x + (bx1 - vpp.x) * kk; c.beginPath(); c.moveTo(xa, vpp.y + (top - vpp.y) * kk); c.lineTo(xa, vpp.y + (bf - vpp.y) * kk); c.stroke();
          }
          // far end of the passage: darkness, then the torch glow on the right wall half way in
          const wl = far(bx1, (top + bf) / 2);
          D.lightPool(c, (bx1 + wl[0]) / 2 + 10, (top + bf) / 2 + 30, inf.backR * 1.25, t, { seed: 77, alpha: 0.6, hot: 0.12 });
          if (o.doorway) o.doorway(c, inf);
        },
      });
    }, { blur: o.archBlur ?? 0 });
    ctx.restore();

    // ---- layer 3: floor
    ctx.save(); D.cam(ctx, cam, 1);
    D.floor(ctx, { y0: floorY, y1: DH + 40, vp: { x: 960, y: floorY - 230 }, rows: 9, sw: 128, set, seed: seed + 4, gap: 2, aoH: 70, cracks: o.cracks ?? 0 });
    // floor falls off toward the camera (gradient = light)
    const fg = ctx.createLinearGradient(0, floorY, 0, DH);
    fg.addColorStop(0, 'rgba(4,6,8,0)'); fg.addColorStop(1, 'rgba(4,6,8,0.45)');
    ctx.fillStyle = fg; ctx.fillRect(-PADX, floorY, DW + PADX * 2, DH - floorY + 60);
    if (o.spill) D.spill(ctx, Object.assign({ x: -180, y: 760, r: 980 }, o.spill));
    if (spot) D.spotlight(ctx, Object.assign({}, spot, { part: 'floor' }));
    // corner props (dim): skull pile at the wall base, far left
    if (o.skulls !== false) {
      const dimBone = { bone: '#4E5456', boneShade: '#353B3E', socket: '#0B0F12' };
      D.skullPile(ctx, o.skullX ?? 215, floorY + 22, 0.62, dimBone);
      D.skull(ctx, (o.skullX ?? 215) + 120, floorY + 30, 15, { rot: 0.5, bone: '#4A5052', boneShade: '#33393C', socket: '#0B0F12' });
    }
    ctx.restore();
    ctx.restore();
    return info;
  };

  D.roomFront = (ctx, t = 0, o = {}) => {
    const spot = o.spot === false ? null : Object.assign({ x: 860, floorY: 620, alpha: 0.35, rx: 300, ry: 60, topW: 210, topY: -90, t }, o.spot || {});
    ctx.save(); fitDesign(ctx);
    if (spot) { ctx.save(); D.cam(ctx, o.cam, 1); D.spotlight(ctx, Object.assign({}, spot, { part: 'beam' })); ctx.restore(); }
    if (o.fgChain !== false) {
      ctx.save(); D.cam(ctx, o.cam, 1.45);
      D.filtered(ctx, g => {
        D.hangChain(g, 1838, -30, 470, t, { link: 46, cols: D.PAL.chainFG, end: 'shackle', sway: 0.03, swayFreq: 0.3 });
        D.hangChain(g, 1730, -30, 250, t + 1.3, { link: 42, cols: D.PAL.chainFG, end: 'hook', sway: 0.03, swayFreq: 0.33 });
      }, { blur: 3.5 });
      ctx.restore();
    }
    ctx.restore();
  };

  D.room = (ctx, t = 0, o = {}) => {
    const info = D.roomBack(ctx, t, o);
    if (o.actors) { ctx.save(); fitDesign(ctx); o.actors(ctx, info); ctx.restore(); }
    D.roomFront(ctx, t, o);
    if (o.post !== false) D.post(ctx, t, Object.assign({ vignette: 0.66, vigX: (o.spot && o.spot.x) || 900, vigY: 520 }, o));
    return info;
  };

  // =============================================================================================== SCENE: CORRIDOR
  D.corridorBack = (ctx, t = 0, o = {}) => {
    const set = D.STONE.dungeon, P = D.PAL, seed = o.seed ?? 7, cam = o.cam;
    const floorY = o.floorY ?? 780;
    const piers = o.piers || [420, 1500];
    const span = piers[1] - piers[0] - 260, springY = o.springY ?? 560; // centre arch opening
    const r = span / 2, cxC = (piers[0] + piers[1]) / 2;
    const torchY = o.torchY ?? 470;
    const info = { floorY, contactY: floorY + 130, torches: [], arches: [], clear: [640, 1280] };

    ctx.save(); fitDesign(ctx);
    // ---- layer 1: far (seen through the arches), blurred + cached: receding hall in the centre, far wall to the right
    const far = D.cached(`corr_far_${seed}`, DW + PADX * 2, DH + PADY * 2, g => {
      g.translate(PADX, PADY);
      g.fillStyle = set.void; g.fillRect(-PADX, -PADY, DW + PADX * 2, DH + PADY * 2);
      // far wall of the next hall (dim stones)
      const dimSet = { mortar: '#18161D', base: ['#2A2733', '#34303D'], shade: '#201E27', edge: '#423D4B' };
      D.stoneWall(g, { x: -PADX, y: -PADY, w: DW + PADX * 2, h: floorY - 120 + PADY, bw: 96, bh: 44, gap: 3, set: dimSet, seed: seed + 10, stepped: 0.2, shadeW: 4 });
      // stepped ruined top silhouette against the darker vault (귤멍 stepped skyline)
      const rr = S.rng(seed + 11); let sx = -PADX; g.fillStyle = set.void; g.beginPath(); g.moveTo(-PADX, -PADY);
      let sy = 330; g.lineTo(-PADX, sy);
      while (sx < DW + PADX) { const w = rr.range(40, 120); g.lineTo(sx, sy); sx += w; g.lineTo(sx, sy); sy = clamp(sy + rr.pick([-44, -22, 22, 44]), 280, 420); }
      g.lineTo(DW + PADX, -PADY); g.closePath(); g.fill();
      // far floor
      g.fillStyle = '#1B1922'; g.fillRect(-PADX, floorY - 120, DW + PADX * 2, 400);
      // far hall seen through the right arch: a small barred window
      D.cellWindow(g, 1752, 440, 90, 112, { set: dimSet, bars: 3, light: 0, skyTop: '#5E6880', skyBottom: '#394052', seed: seed + 12 });
      // cool moonlight shaft from the far window onto the far floor (light from the top-left convention: falls down-right)
      const sh = g.createLinearGradient(1752, 552, 1900, floorY - 60);
      sh.addColorStop(0, 'rgba(150,162,188,0.3)'); sh.addColorStop(1, 'rgba(150,162,188,0.06)');
      g.fillStyle = sh; g.beginPath(); g.moveTo(1752, 552); g.lineTo(1842, 552); g.lineTo(1990, floorY - 70); g.lineTo(1830, floorY - 70); g.closePath(); g.fill();
      g.fillStyle = 'rgba(150,162,188,0.12)'; g.beginPath(); g.ellipse(1910, floorY - 62, 110, 20, 0, 0, TAU); g.fill();
      // receding tunnel through the centre arch: nested arch frames scaled toward the vanishing point
      const vp = { x: cxC, y: 590 }, N = 6, q = 0.68;
      const frame = k => ({ R: r * k, cx: vp.x + (cxC - vp.x) * k, sy: vp.y + (springY - vp.y) * k, fy: vp.y + (floorY - vp.y) * k });
      for (let i = 0; i <= N; i++) {
        const A0 = frame(Math.pow(q, i)), A1 = frame(Math.pow(q, i + 1)), dim = Math.min(1, (i + 0.5) / N);
        g.fillStyle = C.mix('#24212C', '#0F0D13', dim); g.beginPath(); D.archOpening(g, A0.cx, A0.fy, A0.R, A0.sy); g.fill();         // vault + side walls
        g.fillStyle = C.mix('#2A2733', '#121017', dim); g.beginPath(); g.moveTo(A0.cx - A0.R, A0.fy); g.lineTo(A0.cx + A0.R, A0.fy);  // floor (lit)
        g.lineTo(A1.cx + A1.R, A1.fy); g.lineTo(A1.cx - A1.R, A1.fy); g.closePath(); g.fill();
        g.fillStyle = C.mix('#3A3644', '#17151C', dim); g.beginPath();                                                                // next frame's face
        D.archOpening(g, A1.cx, A1.fy, A1.R * 1.13, A1.sy); D.archOpening(g, A1.cx, A1.fy, A1.R, A1.sy); g.fill('evenodd');
      }
      const E = frame(Math.pow(q, N + 1));
      const fgx = g.createRadialGradient(E.cx, E.fy - E.R * 0.8, 0, E.cx, E.fy - E.R * 0.8, r * 0.42);
      fgx.addColorStop(0, 'rgba(150,156,175,0.32)'); fgx.addColorStop(1, 'rgba(150,156,175,0)');
      g.fillStyle = fgx; g.fillRect(vp.x - r, vp.y - r, r * 2, r * 2);
    }, o.farBlur ?? 8);
    ctx.save(); D.cam(ctx, cam, 0.35); ctx.drawImage(far, -PADX, -PADY);
    // distant torch glows in the tunnel and the far hall (uncached, they flicker)
    for (const [gx, gy, gr, sd, al] of [[cxC - r * 0.5, 470, 190, 3, 0.75], [1680, 560, 170, 5, 0.35]]) {
      D.lightPool(ctx, gx, gy, gr, t, { seed: sd, alpha: al, hot: 0.18 });
    }
    ctx.restore();

    // ---- layer 2: the arcade wall (crisp)
    ctx.save(); D.cam(ctx, cam, 0.8);
    const archR = r, arches = [cxC - (piers[1] - piers[0]), cxC, cxC + (piers[1] - piers[0])];
    // wall face with three openings cut out
    ctx.save();
    ctx.beginPath(); ctx.rect(-PADX, -PADY, DW + PADX * 2, floorY + PADY);
    for (const ax of arches.slice(1)) D.archOpening(ctx, ax, floorY, archR, springY);
    ctx.clip('evenodd');
    D.stoneWall(ctx, { x: -PADX, y: -PADY, w: DW + PADX * 2, h: floorY + PADY, bw: 112, bh: 52, gap: 3, set, seed: seed + 20, stepped: 0.16, shadeW: 6 });
    // plinth course
    D.stoneWall(ctx, { x: -PADX, y: floorY - 40, w: DW + PADX * 2, h: 40, bw: 170, bh: 40, gap: 3, set: Object.assign({}, set, { base: ['#25222D', '#2E2A37'] }), seed: seed + 21, stepped: 0, shadeW: 5 });
    // light falloff toward the vault
    const wg = ctx.createLinearGradient(0, 0, 0, floorY);
    wg.addColorStop(0, 'rgba(8,6,12,0.6)'); wg.addColorStop(0.45, 'rgba(8,6,12,0.15)'); wg.addColorStop(1, 'rgba(8,6,12,0.1)');
    ctx.fillStyle = wg; ctx.fillRect(-PADX, -PADY, DW + PADX * 2, floorY + PADY);
    ctx.restore();
    // left: solid wall section with a barred cell window + wall shackles
    if (o.window !== false) D.cellWindow(ctx, 92, 250, 136, 150, { set, bars: 3, light: 0.7, seed: seed + 22 });
    // arches: centre (open to the tunnel) and right (open to the far hall); the inside is the far layer
    for (const ax of arches.slice(1)) {
      info.arches.push(D.arch(ctx, {
        cx: ax, floorY, span, springY, ring: 74, n: 13, set, seed: seed + 30 + ax, vp: { x: 960, y: 520 }, depth: 0.08,
        stone: '#423D4B', stoneShade: '#26232E', revealCol: '#211E28', passFloorCol: '#1E1C25',
        voidCol: null, // the far layer (already drawn) shows through
      }));
    }
    ctx.restore();

    // torches + their light pools on the wall
    ctx.save(); D.cam(ctx, cam, 0.8);
    if (o.torches !== false) {
      piers.forEach((px, i) => { // pools first (approximate flame spot), then the crisp torch on top
        const dir = i === 0 ? -1 : 1;
        D.lightPool(ctx, px + 44 * dir, torchY - 80, 560, t, { seed: 11 + i * 7, alpha: 0.95, hot: 0.3 });
      });
      piers.forEach((px, i) => {
        const tr = D.torch(ctx, px, torchY, 1.05, t, { seed: 11 + i * 7, dir: i === 0 ? -1 : 1 });
        info.torches.push({ x: tr.flame[0], y: tr.flame[1] });
      });
    }
    // wall chains
    if (o.chains !== false) {
      D.bolt(ctx, 118, 470, 1); D.bolt(ctx, 205, 470, 1);
      D.hangChain(ctx, 118, 470, 150, t, { link: 26, end: 'shackle', sway: 0.02, seed: 1 });
      D.hangChain(ctx, 205, 470, 118, t + 0.8, { link: 26, end: 'shackle', sway: 0.02, seed: 2 });
      D.bolt(ctx, piers[1] - 80, 610, 0.9); D.bolt(ctx, piers[1] + 86, 616, 0.9);
      D.swagChain(ctx, [piers[1] - 80, 610], [piers[1] + 86, 616], 64, { link: 24 });
      // a hook chain hanging from the centre arch, left of the clear zone
      D.hangChain(ctx, cxC - r * 0.86, springY - r * 0.47, 130, t + 0.4, { link: 24, end: 'hook', sway: 0.04, seed: 3 });
    }
    ctx.restore();

    // ---- layer 3: floor
    ctx.save(); D.cam(ctx, cam, 1);
    D.floor(ctx, { y0: floorY, y1: DH + 40, vp: { x: 960, y: floorY - 300 }, rows: 8, sw: 140, set, seed: seed + 40, gap: 2, aoH: 50 });
    const fg = ctx.createLinearGradient(0, floorY, 0, DH);
    fg.addColorStop(0, 'rgba(8,6,12,0)'); fg.addColorStop(1, 'rgba(8,6,12,0.4)');
    ctx.fillStyle = fg; ctx.fillRect(-PADX, floorY, DW + PADX * 2, DH - floorY + 60);
    // torchlight reaching the floor
    for (const tf of info.torches) D.lightPool(ctx, tf.x, floorY + 46, 480, t, { seed: 5, alpha: 0.6, hot: 0.08, squash: 0.26 });
    if (o.spill) D.spill(ctx, Object.assign({ x: -180, y: 900, r: 980 }, o.spill));
    // floor props (outside the clear middle third)
    if (o.skulls !== false) D.skullPile(ctx, 205, floorY + 34, 0.72, {});
    if (o.candles !== false) {
      const c1 = D.candles(ctx, 520, floorY + 40, 0.9, t, { seed: 21 });
      const c2 = D.candles(ctx, 1720, floorY + 52, 1.0, t, { seed: 22, defs: [[-40, 64, 22], [-6, 108, 28], [30, 84, 24], [62, 40, 18]] });
      for (const [fx, fy] of c1.concat(c2)) D.lightPool(ctx, fx, fy, 150, t, { seed: fx, alpha: 0.35, hot: 0.12 });
    }
    ctx.restore();
    ctx.restore();
    return info;
  };

  D.corridorFront = (ctx, t = 0, o = {}) => {
    if (o.fgChains === false) return;
    ctx.save(); fitDesign(ctx); D.cam(ctx, o.cam, 1.45);
    D.filtered(ctx, g => {
      D.hangChain(g, 46, -30, 250, t, { link: 50, cols: D.PAL.chainFG, end: 'hook', sway: 0.03, swayFreq: 0.28 });
      D.swagChain(g, [1560, -40], [1990, 90], 170, { link: 48, cols: D.PAL.chainFG });
      D.hangChain(g, 1858, -30, 300, t + 1.1, { link: 46, cols: D.PAL.chainFG, end: 'hook', sway: 0.03, swayFreq: 0.31 });
    }, { blur: 4 });
    ctx.restore();
  };

  D.corridor = (ctx, t = 0, o = {}) => {
    const info = D.corridorBack(ctx, t, o);
    if (o.actors) { ctx.save(); fitDesign(ctx); o.actors(ctx, info); ctx.restore(); }
    D.corridorFront(ctx, t, o);
    if (o.post !== false) D.post(ctx, t, Object.assign({ vignette: 0.6, vigY: 560 }, o));
    return info;
  };
})();
