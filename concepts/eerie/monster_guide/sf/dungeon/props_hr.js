/* =====================================================================================================================
 * props_hr.js : window.PROPS_HR, set dressing for the SF3 dungeon room (Monster HR). Loads after lib_core.js and
 * dungeon.js. Does NOT change the dungeon kit: it draws extra layers you call between DUNGEON.roomBack and the cast.
 *
 * Brief: cute + grotesque. The set stays CALMER and DARKER than the characters: every prop is desaturated, dimmed
 * toward the room stone and very slightly softened, so it reads as background at 1080p and disappears at 168 px.
 *   grotesque-ish dungeon traces: claw scratches (wall + floor), a few loose bones, cobwebs, a wet drool trail
 *   cute HR-office touches on the stone: "DAYS WITHOUT AN INCIDENT: 0" board, a "HANG IN THERE" poster (a little
 *   skeleton hanging from a bar by both hands), a brass "MONSTER HR / ONBOARDING" nameplate by the arch.
 *
 * API (design space 1920x1080, same camera object as DUNGEON.room*; each call applies fitDesign + its own depth)
 *   PROPS_HR.roomWall(ctx, t, o)    wall layer (depth 0.35, like the far wall) + nameplate at the arch depth (0.8).
 *     o.cam                camera (same object you pass to DUNGEON.roomBack)
 *     o.board  = true | {x, y, s}     days-without-incident board (default x 420, y 250, s 1; x, y = top-left)
 *     o.poster = true | {x, y, s}     motivational poster (default x 150, y 150)
 *     o.plate  = true | {x, y, s}     brass nameplate (default x 1215, y 330, arch depth)
 *     o.webs   = true                 cobwebs (top-left corner + over the arch)
 *     o.scratches = true | [{x, y, s, rot}]   claw gouges in the stone
 *     o.dim    = 1                    0..1 extra darkening of the whole wall-prop layer (1 = default calm look)
 *     Any item can be false. Defaults keep the clear zone x 560..1160 empty.
 *   PROPS_HR.roomFloor(ctx, t, o)   floor layer (depth 1). Call before the cast (after the spotlight floor pool).
 *     o.cam, o.bones = true | [{x, y, s, rot}], o.drool = false | {pts:[[x,y]...], w}, o.floorScratch = true | [{x,y,s,rot}]
 *   PROPS_HR.days(ctx, x, y, s, o)  the board alone (callouts);  PROPS_HR.poster(...), PROPS_HR.plate(...)
 *   PROPS_HR.floorRing(ctx, x, y, s, {part})  iron ring + staple plate bolted to the floor (chain restraint point;
 *                                   part 'back' before the chain end, 'front' after it, default 'all')
 *   PROPS_HR.PAL
 * =====================================================================================================================
 */
(function () {
  'use strict';
  const S = window.SFX, D = window.DUNGEON;
  if (!S || !D) throw new Error('props_hr.js needs lib_core.js and dungeon.js loaded first');
  const C = S.color, TAU = Math.PI * 2;
  const P = window.PROPS_HR = {};

  // muted, dark: everything sits between the wall stone (#182128..#2F3B44) and the characters
  P.PAL = {
    frame: '#3E352E', frameShade: '#2A231E', slate: '#17201F', slateShade: '#111817', chalk: '#AEB7B2',
    card: '#B8AE9A', cardShade: '#8F8673', red: '#A8443A',
    paper: '#8E8A80', paperShade: '#6F6B63', paperInk: '#2A2E33', paperPic: '#3E4E57', pin: '#7A3A40',
    brass: '#7C6C4E', brassShade: '#574B36', brassLight: '#9C8B66', brassInk: '#2B2416',
    web: 'rgba(170,186,196,0.16)', groove: '#0B1013', grooveLight: 'rgba(88,104,114,0.55)',
    bone: '#5A5E5C', boneShade: '#3E4341', socket: '#0B0F12',
    drool: 'rgba(150,190,205,0.18)', droolEdge: 'rgba(170,210,225,0.22)', droolHi: 'rgba(225,245,255,0.55)',
  };
  const PL = P.PAL;
  const pick = (v, d) => (v === false ? null : Object.assign({}, d, v === true || v == null ? {} : v));

  // ------------------------------------------------------------------ text helper
  function txt(g, s, x, y, size, font, color, o = {}) {
    g.save();
    g.font = `${o.weight || 800} ${size}px ${font}`; g.fillStyle = color;
    g.textAlign = o.align || 'center'; g.textBaseline = o.base || 'middle';
    if (o.maxW) { const w = g.measureText(s).width; if (w > o.maxW) { g.translate(x, y); g.scale(o.maxW / w, 1); g.fillText(s, 0, 0); g.restore(); return; } }
    g.fillText(s, x, y); g.restore();
  }

  // ------------------------------------------------------------------ DAYS WITHOUT AN INCIDENT: 0
  // (x, y) = top-left, 240 x 156 at s = 1
  P.days = (g, x, y, s = 1, o = {}) => {
    g.save(); g.translate(x, y); g.scale(s, s); g.rotate((o.rot ?? -1.2) * Math.PI / 180);
    const w = 240, h = 156;
    // hanging string + nail
    g.strokeStyle = '#2B2A2C'; g.lineWidth = 2.2; g.beginPath(); g.moveTo(26, 6); g.lineTo(w / 2, -34); g.lineTo(w - 26, 6); g.stroke();
    S.circle(g, w / 2, -34, 4.5, '#4A4C52');
    S.cel(g, c => S.addRoundRect(c, 0, 0, w, h, 10), PL.frame, PL.frameShade, 5);
    S.cel(g, c => S.addRoundRect(c, 11, 11, w - 22, h - 22, 5), PL.slate, PL.slateShade, 4);
    txt(g, 'DAYS WITHOUT', w / 2, 34, 21, 'Fredoka', PL.chalk, { weight: 600, maxW: w - 40 });
    txt(g, 'AN INCIDENT', w / 2, 58, 21, 'Fredoka', PL.chalk, { weight: 600, maxW: w - 40 });
    // the flip card with the number (cream, the one brighter thing on the board)
    const cx = w / 2, cy = 104;
    S.cel(g, c => S.addRoundRect(c, cx - 30, cy - 30, 60, 58, 6), PL.card, PL.cardShade, 4);
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(cx - 30, cy - 1, 60, 2);
    txt(g, String(o.n ?? 0), cx, cy + 2, 50, 'Anton', PL.red, { weight: 400 });
    // chalk tally scribbles, scrubbed out (somebody kept trying)
    g.strokeStyle = C.rgba(PL.chalk, 0.35); g.lineWidth = 2;
    for (let i = 0; i < 4; i++) { g.beginPath(); g.moveTo(26 + i * 9, 86); g.lineTo(28 + i * 9, 118); g.stroke(); }
    g.beginPath(); g.moveTo(20, 112); g.lineTo(64, 92); g.stroke();
    for (let i = 0; i < 2; i++) { g.beginPath(); g.moveTo(178 + i * 9, 88); g.lineTo(180 + i * 9, 118); g.stroke(); }
    g.beginPath(); g.moveTo(172, 116); g.lineTo(206, 90); g.stroke();
    g.restore();
  };

  // ------------------------------------------------------------------ HANG IN THERE poster
  // (x, y) = top-left, 176 x 236 at s = 1
  P.poster = (g, x, y, s = 1, o = {}) => {
    g.save(); g.translate(x, y); g.scale(s, s); g.rotate((o.rot ?? 2.2) * Math.PI / 180);
    const w = 176, h = 236;
    // paper with a torn bottom-right corner (curled flap = one hard shade)
    const paper = c => { c.moveTo(0, 0); c.lineTo(w, 0); c.lineTo(w, h - 34); c.lineTo(w - 30, h); c.lineTo(0, h); c.closePath(); };
    S.cel(g, paper, PL.paper, PL.paperShade, 5);
    S.poly(g, [[w, h - 34], [w - 30, h], [w - 26, h - 30]], C.shade(PL.paper, 0.12));
    // picture panel
    S.roundRect(g, 14, 14, w - 28, 150, 4, PL.paperPic);
    g.fillStyle = C.shade(PL.paperPic, -0.18); g.fillRect(14, 120, w - 28, 44);
    // classic cat-poster gag: a little skeleton dangling from a horizontal bar by BOTH hands (arms straight up, the
    // skull well below the bar, never near it), feet kicking
    const ax = w / 2, barY = 38;
    g.lineCap = 'round';
    g.strokeStyle = '#2A3036'; g.lineWidth = 6; g.beginPath(); g.moveTo(22, barY); g.lineTo(w - 22, barY); g.stroke();
    g.lineWidth = 3; g.beginPath(); g.moveTo(26, 14); g.lineTo(30, barY); g.moveTo(w - 26, 14); g.lineTo(w - 30, barY); g.stroke();
    const bone = '#C9C2B4', bs = '#9F978A';
    const limb = (pts, wd) => { g.strokeStyle = bone; g.lineWidth = wd; g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); pts.slice(1).forEach(p => g.lineTo(p[0], p[1])); g.stroke(); };
    // hands on the bar
    S.circle(g, ax - 22, barY + 1, 5, bone); S.circle(g, ax + 20, barY + 1, 5, bone);
    limb([[ax - 22, barY + 4], [ax - 20, barY + 30], [ax - 12, barY + 52]], 5);   // left arm, straight up
    limb([[ax + 20, barY + 4], [ax + 18, barY + 30], [ax + 10, barY + 52]], 5);   // right arm
    limb([[ax, barY + 70], [ax + 2, barY + 104]], 7);                              // spine
    g.strokeStyle = bone; g.lineWidth = 3;
    for (let i = 0; i < 3; i++) { g.beginPath(); g.moveTo(ax - 11, barY + 76 + i * 8); g.quadraticCurveTo(ax, barY + 71 + i * 8, ax + 11, barY + 76 + i * 8); g.stroke(); }
    limb([[ax - 4, barY + 106], [ax - 16, barY + 118], [ax - 12, barY + 126]], 5);  // legs, one kicking
    limb([[ax + 6, barY + 106], [ax + 22, barY + 112], [ax + 30, barY + 104]], 5);
    // skull between the arms, low (the arms frame it), cute big low-set sockets
    S.cel(g, c => { c.moveTo(ax + 16, barY + 58); c.ellipse(ax, barY + 58, 16, 14, 0, 0, TAU); }, bone, bs, 3);
    S.circle(g, ax - 6, barY + 61, 4.4, '#1C2023'); S.circle(g, ax + 6, barY + 61, 4.4, '#1C2023');
    txt(g, 'HANG IN', w / 2, 186, 26, 'Fredoka', PL.paperInk, { weight: 600, maxW: w - 30 });
    txt(g, 'THERE', w / 2, 214, 26, 'Fredoka', PL.paperInk, { weight: 600, maxW: w - 30 });
    // pins
    S.circle(g, 12, 10, 5, PL.pin); S.circle(g, w - 12, 10, 5, PL.pin);
    g.restore();
  };

  // ------------------------------------------------------------------ brass nameplate
  // (x, y) = top-left, 170 x 58 at s = 1
  P.plate = (g, x, y, s = 1, o = {}) => {
    g.save(); g.translate(x, y); g.scale(s, s);
    const w = 170, h = 58;
    S.cel(g, c => S.addRoundRect(c, 0, 0, w, h, 6), PL.brass, PL.brassShade, 4);
    g.fillStyle = C.rgba(PL.brassLight, 0.6); g.fillRect(6, 4, w - 12, 2);
    S.circle(g, 9, h / 2, 3, PL.brassShade); S.circle(g, w - 9, h / 2, 3, PL.brassShade);
    txt(g, o.line1 || 'MONSTER HR', w / 2, 21, 19, 'Fredoka', PL.brassInk, { weight: 600, maxW: w - 34 });
    txt(g, o.line2 || 'ONBOARDING', w / 2, 41, 13, 'Nunito', C.rgba(PL.brassInk, 0.85), { weight: 900, maxW: w - 40 });
    g.restore();
  };

  // ------------------------------------------------------------------ cobweb (corner = anchor, fans toward ang)
  P.web = (g, x, y, r, ang0, ang1, seed = 1) => {
    const rr = S.rng(seed), n = 6;
    g.save(); g.strokeStyle = PL.web; g.lineWidth = 1.4; g.lineCap = 'round';
    const spokes = [];
    for (let i = 0; i < n; i++) {
      const a = ang0 + (ang1 - ang0) * (i / (n - 1)) + rr.range(-0.05, 0.05), L = r * rr.range(0.8, 1.05);
      spokes.push([a, L]);
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke();
    }
    for (let k = 1; k <= 4; k++) {
      const f = k / 4.6;
      g.beginPath();
      spokes.forEach(([a, L], i) => {
        const q = [x + Math.cos(a) * L * f, y + Math.sin(a) * L * f];
        if (i === 0) g.moveTo(q[0], q[1]);
        else { const [pa, pL] = spokes[i - 1], pm = (a + pa) / 2, sag = L * f * 0.82; g.quadraticCurveTo(x + Math.cos(pm) * sag, y + Math.sin(pm) * sag, q[0], q[1]); }
      });
      g.stroke();
    }
    g.restore();
  };

  // ------------------------------------------------------------------ claw gouges (3-4 parallel strokes)
  P.scratch = (g, x, y, s = 1, rot = 0.35, n = 4, o = {}) => {
    g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s * (o.squash ?? 1));
    for (let i = 0; i < n; i++) {
      const dx = i * 16 - (n - 1) * 8, L = 96 - Math.abs(i - (n - 1) / 2) * 14;
      const pts = [[dx - 4, -L / 2], [dx + 2, 0], [dx + 8, L / 2]];
      S.strip(g, pts, u => 5.5 * Math.sin(Math.PI * Math.min(1, u * 1.05)) + 0.4, o.groove || PL.groove);
      g.save(); g.translate(1.8, 2.4); S.strip(g, pts.map(p => [p[0], p[1]]), u => 1.6 * Math.sin(Math.PI * u), o.light || PL.grooveLight); g.restore();
    }
    g.restore();
  };

  // ------------------------------------------------------------------ drool trail (wet, glossy)
  P.drool = (g, pts, w = 26, t = 0) => {
    g.save();
    S.strip(g, pts, u => w * (0.35 + 0.65 * Math.sin(Math.PI * Math.min(1, 0.15 + u))) , PL.drool);
    S.strip(g, pts.map(p => [p[0] + 2, p[1] + 1]), u => w * 0.22 * Math.sin(Math.PI * u), PL.droolEdge);
    S.strip(g, pts.map(p => [p[0] - 3, p[1] - 2]), u => 2.4 * Math.sin(Math.PI * u), PL.droolHi);
    // a few drops beside the trail
    const r = S.rng(77);
    for (let i = 1; i < pts.length; i++) {
      const p = pts[i], q = pts[i - 1], m = [(p[0] + q[0]) / 2 + r.range(-w, w), (p[1] + q[1]) / 2 + r.range(-w * 0.4, w * 0.4)];
      const rr = r.range(3, 7);
      S.ellipse(g, m[0], m[1], rr * 1.6, rr * 0.6, 0, PL.drool);
      S.ellipse(g, m[0] - rr * 0.5, m[1] - rr * 0.15, rr * 0.5, rr * 0.18, 0, PL.droolHi);
    }
    g.restore();
  };

  // ------------------------------------------------------------------ iron floor ring (the chain's restraint point)
  // (x, y) = ring centre on the floor (design px), s = scale. A square iron plate bolted into the flagstone, a staple
  // eye, and a heavy ring lying flat (seen from the 7 deg camera: a squashed ellipse). part: 'back' | 'front' | 'all'
  // (draw 'back' before the chain end and 'front' after it so the last link passes THROUGH the ring).
  P.floorRing = (g, x, y, s = 1, o = {}) => {
    const part = o.part || 'all', iron = o.iron || '#59606C', ironS = o.ironShade || '#353A43', ironL = o.ironLight || '#8A93A1';
    g.save(); g.translate(x, y); g.scale(s, s);
    const sq = 0.36, R = 26, r = 7;
    if (part !== 'front') {
      S.groundShadow(g, 2, 6, 92, 22, 0.5);
      // bolted plate (foreshortened square)
      S.cel(g, c => { c.moveTo(-40, -8); c.lineTo(38, -12); c.lineTo(44, 12); c.lineTo(-44, 14); c.closePath(); }, '#2C3138', '#1A1D22', 3);
      [[-34, -4], [32, -7], [36, 8], [-36, 10]].forEach(q => S.circle(g, q[0], q[1], 3.2, iron));
      // staple eye
      S.cel(g, c => { c.moveTo(-10, 0); c.arc(0, 0, 10, Math.PI, 0); c.lineTo(5, 0); c.arc(0, 0, 5, 0, Math.PI, true); c.closePath(); }, iron, ironS, 2);
      // back half of the ring
      g.save(); g.scale(1, sq);
      g.lineWidth = r * 2; g.strokeStyle = ironS; g.beginPath(); g.arc(14, 10 / sq, R, Math.PI, 0); g.stroke();
      g.restore();
    }
    if (part !== 'back') {
      g.save(); g.scale(1, sq);
      g.lineWidth = r * 2; g.strokeStyle = iron; g.beginPath(); g.arc(14, 10 / sq, R, 0, Math.PI); g.stroke();
      g.lineWidth = 2.4; g.strokeStyle = ironL; g.beginPath(); g.arc(14, 10 / sq, R - 3, 0.35, Math.PI - 0.6); g.stroke();
      g.restore();
    }
    g.restore();
  };

  // ==================================================================== layers
  P.roomWall = (ctx, t = 0, o = {}) => {
    const cam = o.cam, dim = o.dim ?? 1;
    ctx.save(); D.fitDesign(ctx);
    // far wall plane (depth 0.35, softened 1 px so it sits with the blurred stone)
    ctx.save(); D.cam(ctx, cam, 0.35);
    D.filtered(ctx, g => {
      const pst = pick(o.poster, { x: 150, y: 150, s: 1 });
      if (pst) P.poster(g, pst.x, pst.y, pst.s, pst);
      const bd = pick(o.board, { x: 400, y: 250, s: 1 });
      if (bd) P.days(g, bd.x, bd.y, bd.s, bd);
      if (o.webs !== false) {
        P.web(g, -10, -10, 230, 0.05, 1.5, 3);
        P.web(g, 1930, 40, 170, Math.PI - 1.45, Math.PI - 0.05, 5);
      }
      const sc = o.scratches === false ? [] : Array.isArray(o.scratches) ? o.scratches : [{ x: 330, y: 470, s: 0.85, rot: 0.42 }, { x: 1090, y: 170, s: 0.7, rot: -0.3 }];
      sc.forEach(q => P.scratch(g, q.x, q.y, q.s ?? 1, q.rot ?? 0.3, q.n ?? 4));
      // calm it down: pull the whole layer toward the wall colour
      g.save(); g.globalCompositeOperation = 'source-atop'; g.fillStyle = `rgba(12,18,22,${0.5 * dim})`; g.fillRect(-500, -300, 3000, 1700); g.restore();
    }, { blur: 0.8 });
    ctx.restore();
    // arch plane (depth 0.8): nameplate on the stone beside the door
    const pl = pick(o.plate, { x: 1066, y: 330, s: 1 });
    if (pl || o.webs !== false) {
      ctx.save(); D.cam(ctx, cam, 0.8);
      D.filtered(ctx, g => {
        if (pl) P.plate(g, pl.x, pl.y, pl.s, pl);
        if (o.webs !== false) P.web(g, 1330 + 4, 290, 120, -0.1, 1.1, 9);
        g.save(); g.globalCompositeOperation = 'source-atop'; g.fillStyle = `rgba(12,18,22,${0.5 * dim})`; g.fillRect(-500, -300, 3000, 1700); g.restore();
      }, { blur: 0.5 });
      ctx.restore();
    }
    ctx.restore();
  };

  P.roomFloor = (ctx, t = 0, o = {}) => {
    ctx.save(); D.fitDesign(ctx); D.cam(ctx, o.cam, 1);
    const fs = o.floorScratch === false ? [] : Array.isArray(o.floorScratch) ? o.floorScratch : [{ x: 1560, y: 930, s: 1.3, rot: 1.1 }];
    fs.forEach(q => P.scratch(ctx, q.x, q.y, q.s ?? 1, q.rot ?? 1.2, 4, { squash: 0.45, groove: 'rgba(8,12,14,0.75)', light: 'rgba(80,96,104,0.45)' }));
    if (o.drool) P.drool(ctx, o.drool.pts, o.drool.w ?? 24, t);
    const bones = o.bones === false ? [] : Array.isArray(o.bones) ? o.bones : [
      { x: 1290, y: 700, s: 1, rot: 0.3 }, { x: 1340, y: 716, s: 0.8, rot: -0.9 }, { x: 330, y: 905, s: 1.25, rot: -0.2 },
    ];
    bones.forEach(b => {
      const L = 54 * (b.s ?? 1), c = Math.cos(b.rot ?? 0), sn = Math.sin(b.rot ?? 0) * 0.5;
      S.groundShadow(ctx, b.x, b.y + 7 * (b.s ?? 1), L * 1.25, L * 0.22, 0.45);
      D.bone(ctx, b.x - c * L / 2, b.y - sn * L / 2, b.x + c * L / 2, b.y + sn * L / 2, 9 * (b.s ?? 1), PL.bone, PL.boneShade);
    });
    ctx.restore();
  };
})();
