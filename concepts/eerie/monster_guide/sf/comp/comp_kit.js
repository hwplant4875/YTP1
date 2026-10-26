/* comp_kit.js : window.COMP, shared scene plumbing for the EP1 composites (style_frames/v2/comp_*.png).
 * Loads after core/lib_core.js, dungeon/dungeon.js, dungeon/props_hr.js and whichever rigs the scene uses.
 *
 * COMP.room(ctx, t, o) -> info   the SF3 room with the cast between the layers, in the order that keeps the spotlight
 *   beam from veiling characters (same as mimiku2/hero.js):
 *     roomBack (wall, arch + o.doorway, floor, spot pool) -> PROPS_HR wall + floor -> o.under(ctx, info) (design + cam
 *     space: cast shadows, things on the floor) -> beam (no motes) -> o.actors(ctx, info) -> motes only ->
 *     o.over(ctx, info) (design + cam) -> o.overArch(ctx, info) (design + the arch's 0.8 camera depth: hands on the
 *     door jamb) -> roomFront (fg chains) -> post -> o.screen(ctx)
 *     (raw canvas space: titles, insets).
 *   o: cam, spot (DUNGEON spot opts or false), props (PROPS_HR wall opts; false = none), floorProps (PROPS_HR floor
 *      opts; false = none), doorway, fgChain, post {vignette, vigX, vigY, grain}, beam (beam strength), motes.
 * COMP.ruler(ctx, x, gy, U, n, o)   W-unit height ruler (ticks every W, labels "1 W").
 * COMP.nameTag(ctx, text, x, y, o)  small pill label under a character.
 * COMP.glint(ctx, x, y, r, a)       soft gold point light (the eyes in the lid crack).
 * COMP.floorChain(anchor, floorY, s, ring) -> pts   dormant chain from the chest anchor to a floor ring (opts.chain.pts).
 * COMP.keyLit(ctx, drawFn, bounds, o)   top-left key on a group: lighter left / top, darker right side face.
 * COMP.outlineText(ctx, text, x, y, o)  big thumbnail text: white fill + thick dark stroke + drop shadow.
 */
(function () {
  'use strict';
  const S = window.SFX, D = window.DUNGEON, PR = window.PROPS_HR, C = S.color;
  const K = window.COMP = {};

  K.room = (ctx, t = 0, o = {}) => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    const cam = o.cam || { zoom: 1 };
    const spot = o.spot === false ? false : Object.assign({ x: 860, floorY: 620, alpha: 0.5, rx: 300, ry: 66, topW: 180, topY: -80, t }, o.spot || {});
    const base = { spot, cam, post: false, fgChain: false, doorway: o.doorway, skulls: o.skulls, seed: o.seed };
    const info = D.roomBack(ctx, t, base);
    if (o.props !== false && PR) PR.roomWall(ctx, t, Object.assign({ cam }, o.props || {}));
    if (o.floorProps !== false && PR) PR.roomFloor(ctx, t, Object.assign({ cam }, o.floorProps || {}));
    ctx.save(); D.fitDesign(ctx); D.cam(ctx, cam, 1);
    if (o.under) o.under(ctx, info);
    if (spot) D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', motes: 0, beam: o.beam ?? 0.5 }));
    if (o.actors) o.actors(ctx, info);
    if (spot && (o.motes ?? 22) > 0) D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', beam: 0, motes: o.motes ?? 22, seed: 43 }));
    if (o.over) o.over(ctx, info);
    ctx.restore();
    if (o.overArch) { ctx.save(); D.fitDesign(ctx); D.cam(ctx, cam, 0.8); o.overArch(ctx, info); ctx.restore(); }
    D.roomFront(ctx, t, { cam, spot: false, fgChain: o.fgChain !== false });
    if (o.post !== false) D.post(ctx, t, Object.assign({ vignette: 0.62, vigX: 900, vigY: 500 }, o.post || {}));
    if (o.screen) { ctx.save(); D.fitDesign(ctx); o.screen(ctx, info); ctx.restore(); }
    return info;
  };

  // a dormant chain run from the chest's chain anchor down to the floor and along it to a floor ring (absolute pts for
  // MIMIKU2 opts.chain.pts). anchor = M.anchors(...).chain, floorY = where the links lie, ring = [x, y] end point.
  K.floorChain = (anchor, floorY, s, ring) => {
    const pitch = 0.09 * 180 * 0.7 * s, pts = [anchor.slice()];
    let q = anchor.slice();
    while (q[1] + pitch < floorY) { q = [q[0] + (pts.length === 1 ? 0.01 * 180 * s : 0), q[1] + pitch]; pts.push(q); }
    q = [q[0] + pitch * 0.6, floorY]; pts.push(q);
    const d = [ring[0] - q[0], ring[1] - q[1]], L = Math.hypot(d[0], d[1]), n = Math.max(1, Math.round(L / pitch));
    for (let i = 1; i <= n; i++) pts.push([q[0] + d[0] * i / n, q[1] + d[1] * i / n]);
    return pts;
  };

  // top-left KEY LIGHT on a drawn group: draws drawFn(g) into a layer, then ramps it lighter on the left / top and
  // darker on the right (the lit left face, the shaded right side face), so every shot shares one key direction.
  // bounds = {x, y, w, h} in ctx coords around the subject; o: lite=0.16 (warm screen on the left), dark=0.32
  K.keyLit = (ctx, drawFn, bounds, o = {}) => {
    const L = S.layer(ctx, drawFn, bounds, 10);
    if (!L) return;
    const g = L.canvas.getContext('2d');
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    const m = ctx.getTransform(), X = q => m.a * q[0] + m.c * q[1] + m.e - L.x, Y = q => m.b * q[0] + m.d * q[1] + m.f - L.y;
    const p0 = [bounds.x + bounds.w * (o.x0 ?? 0.15), bounds.y + bounds.h * 0.2], p1 = [bounds.x + bounds.w * (o.x1 ?? 0.95), bounds.y + bounds.h * 0.75];
    const lg = g.createLinearGradient(X(p0), Y(p0), X(p1), Y(p1));
    lg.addColorStop(0, `rgba(10,10,18,0)`); lg.addColorStop(0.5, 'rgba(10,10,18,0)'); lg.addColorStop(1, `rgba(10,10,22,${o.dark ?? 0.32})`);
    g.globalCompositeOperation = 'source-atop'; g.fillStyle = lg; g.fillRect(0, 0, L.w, L.h);
    const lw = g.createLinearGradient(X(p0), Y(p0), X(p1), Y(p1));
    lw.addColorStop(0, C.rgba(o.warm || '#FFE2B0', o.lite ?? 0.16)); lw.addColorStop(0.45, C.rgba(o.warm || '#FFE2B0', 0));
    g.fillStyle = lw; g.fillRect(0, 0, L.w, L.h);
    g.restore();
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x, L.y, L.w, L.h); ctx.restore();
    L.release();
  };

  // dark separation halo: the silhouette of drawFn(g) dilated by px (device px) in color, drawn BEFORE the subject so
  // overlapping look-alike shapes (stacked helms) stay countable
  K.halo = (ctx, drawFn, px = 6, color = '#06080A') => {
    const L = S.layer(ctx, drawFn, null, 0);
    if (!L) return;
    const g = L.canvas.getContext('2d');
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-in'; g.fillStyle = color; g.fillRect(0, 0, L.w, L.h); g.restore();
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; ctx.drawImage(L.canvas, 0, 0, L.w, L.h, L.x + Math.cos(a) * px, L.y + Math.sin(a) * px, L.w, L.h); }
    ctx.restore();
    L.release();
  };

  K.glint = (ctx, x, y, r, a = 1, col = '#FFC83D') => {
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    let g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
    g.addColorStop(0, C.rgba(col, 0.55 * a)); g.addColorStop(0.35, C.rgba(col, 0.18 * a)); g.addColorStop(1, C.rgba(col, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 4, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    ctx.save();
    S.ellipse(ctx, x, y, r, r * 0.42, 0, C.rgba('#FFE9A8', Math.min(1, a)));
    S.ellipse(ctx, x, y, r * 0.45, r * 0.22, 0, C.rgba('#FFFFFF', Math.min(1, a * 0.9)));
    ctx.restore();
  };

  K.ruler = (ctx, x, gy, U, n = 4, o = {}) => {
    const col = o.color || 'rgba(237,231,242,0.55)';
    ctx.save();
    ctx.fillStyle = col; ctx.fillRect(x - 1.5, gy - n * U, 3, n * U);
    for (let i = 0; i <= n; i++) {
      const y = gy - i * U;
      ctx.fillRect(x - 12, y - 1.5, 24, 3);
      if (i < n) ctx.fillRect(x - 6, y - U / 2 - 1, 12, 2);
      S.label(ctx, `${i} W`, x - 20, y, o.size || 20, { align: 'right', color: col, weight: 800 });
    }
    (o.marks || []).forEach(([h, txt, c]) => {
      const y = gy - h * U;
      ctx.strokeStyle = c || 'rgba(255,200,61,0.5)'; ctx.lineWidth = 2; ctx.setLineDash([10, 9]);
      ctx.beginPath(); ctx.moveTo(x + 16, y); ctx.lineTo(o.x1 || x + 1700, y); ctx.stroke(); ctx.setLineDash([]);
      S.label(ctx, txt, x + 24, y - 16, 18, { align: 'left', color: c || 'rgba(255,200,61,0.85)', weight: 800 });
    });
    ctx.restore();
  };

  K.nameTag = (ctx, text, x, y, o = {}) => {
    S.label(ctx, text, x, y, o.size || 22, { color: o.color || '#EDE7F2', weight: 900, bg: o.bg || 'rgba(12,15,20,0.72)', pad: 0.5 });
    if (o.sub) S.label(ctx, o.sub, x, y + (o.size || 22) * 1.35, (o.size || 22) * 0.68, { color: 'rgba(237,231,242,0.6)', weight: 800 });
  };

  K.outlineText = (ctx, text, x, y, o = {}) => {
    const size = o.size || 200, font = o.font || 'Anton';
    ctx.save();
    ctx.font = `${o.weight || 400} ${size}px ${font}`; ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'alphabetic';
    if (o.track) ctx.letterSpacing = `${o.track}px`;
    ctx.lineJoin = 'round'; ctx.miterLimit = 2;
    // drop shadow (down-right like every group shadow in the show)
    ctx.save(); ctx.translate(o.sdx ?? 10, o.sdy ?? 12); ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.filter = 'blur(6px)';
    ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.lineWidth = (o.stroke ?? 24); ctx.strokeText(text, x, y); ctx.fillText(text, x, y); ctx.restore();
    ctx.strokeStyle = o.strokeColor || '#0B0D10'; ctx.lineWidth = o.stroke ?? 24; ctx.strokeText(text, x, y);
    ctx.fillStyle = o.color || '#FFFFFF'; ctx.fillText(text, x, y);
    const w = ctx.measureText(text).width;
    ctx.restore();
    return w;
  };
})();
