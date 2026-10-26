/* motion.js : cursor-host motion test (~5 s). Pip flies in, hovers the lone dormant chest (selection + tooltip), clicks,
 * the background swaps to a game menu (iris wipe from the click point), Pip grabs a RULE 1 card peeking from the bottom
 * edge and drags it into the handbook slot. Loads after cursor/scene.js (reuses CURSOR_SCENE).
 * node render_seq.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,comp/frame0.js,cursor/cursor.js,cursor/scene.js,cursor/motion.js <out.mp4> 5
 * Stills: render_sf.mjs with the same list and t. */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, K = window.CURSOR, CS = window.CURSOR_SCENE, F = window.FRAME0, C = S.color, E = S.ease;
  const P = S.prog, lerp = S.lerp;
  const bez = (a, b, cc, k) => [lerp(lerp(a[0], cc[0], k), lerp(cc[0], b[0], k), k), lerp(lerp(a[1], cc[1], k), lerp(cc[1], b[1], k), k)];

  // ---------------------------------------------------------------- timeline (s)
  const T = { fly: 0.95, hover: 0.95, click: 1.95, wipe: 2.2, wipeEnd: 2.7, cardIn: 2.45, reach: 2.95, grab: 3.08, drop: 4.1 };
  const HOV = [1004, 430], CLICK = HOV;
  const CW = 330, CH = 430, SLOT = [1300, 566];
  const CARD0 = [540, 1112];                       // card centre while it peeks from the bottom edge
  const GRAB_DY = -CH / 2 + 6;                     // grab point relative to the card centre
  const DRAG_C = [700, 560];                       // drag curve control

  function dragK(t) { return E.easeInOutCubic(P(t, T.grab, T.drop - T.grab)); }
  function grabPt(t) {
    const a = [CARD0[0], CARD0[1] + GRAB_DY], b = [SLOT[0], SLOT[1] + GRAB_DY];
    return bez(a, b, DRAG_C, dragK(t));
  }
  // cursor hotspot + pose for time t
  function cursorAt(t) {
    if (t < T.hover) {
      const k = E.easeOutBack(P(t, 0, T.fly), 1.25);
      return { p: bez([2080, 60], HOV, [1560, 40], k), state: 'point', expr: 'focus' };
    }
    if (t < T.wipe) {
      const bob = Math.sin((t - T.hover) * 5) * 4;
      return { p: [HOV[0], HOV[1] + bob * (t < T.click ? 1 : 0)], state: t >= T.click && t < T.click + 0.22 ? 'click' : 'point', expr: t >= T.click ? 'happy' : 'wow' };
    }
    if (t < T.reach) {
      const k = E.easeInOutCubic(P(t, T.wipe + 0.05, T.reach - T.wipe - 0.05));
      const g = [CARD0[0] + 6, CARD0[1] + GRAB_DY + 4];
      return { p: bez(HOV, g, [760, 980], k), state: 'point', expr: k > 0.7 ? 'wow' : 'focus' };
    }
    if (t < T.grab) return { p: [CARD0[0] + 6, CARD0[1] + GRAB_DY + 4], state: 'hand', expr: 'happy' };
    if (t < T.drop) return { p: grabPt(t), state: 'grab', expr: 'focus' };
    const k = E.easeOutCubic(P(t, T.drop + 0.12, 0.6));
    return { p: bez([SLOT[0], SLOT[1] + GRAB_DY], [1600, 330], [1520, SLOT[1] + GRAB_DY], k), state: 'point', expr: 'happy' };
  }

  // ---------------------------------------------------------------- game menu backdrop + window
  function menuBG(g, t) {
    const gr = g.createLinearGradient(0, 0, 1920, 1080);
    gr.addColorStop(0, '#221A3A'); gr.addColorStop(1, '#0C1020');
    g.fillStyle = gr; g.fillRect(0, 0, 1920, 1080);
    g.save(); g.globalAlpha = 0.05; g.fillStyle = '#FFFFFF';
    const off = (t * 40) % 80;
    for (let x = -1200; x < 1920; x += 80) { g.beginPath(); g.moveTo(x + off, 0); g.lineTo(x + off + 40, 0); g.lineTo(x + off + 40 + 1080, 1080); g.lineTo(x + off + 1080, 1080); g.closePath(); g.fill(); }
    g.restore();
    g.fillStyle = 'rgba(255,255,255,0.035)';
    for (let x = 0; x < 1920; x += 48) g.fillRect(x, 0, 1, 1080);
    for (let y = 0; y < 1080; y += 48) g.fillRect(0, y, 1920, 1);
  }
  function menu(g, t, pop, dropped) {
    menuBG(g, t);
    const PX = 150, PY = 150, PW = 1620, PH = 800;
    K.panel(g, PX, PY, PW, PH, { title: 'EMPLOYEE HANDBOOK  ·  RULES', pop });
    if (pop <= 0) return;
    g.save(); g.globalAlpha *= S.clamp((pop - 0.2) * 2);
    // portrait slot: the chest, still dormant, under its own little spotlight
    const fx = 210, fy = 260, fw = 700, fh = 640;
    S.roundRect(g, fx, fy, fw, fh, 16, '#0A0D15');
    S.clip(g, c2 => S.addRoundRect(c2, fx, fy, fw, fh, 16), cg => {
      const rg = cg.createRadialGradient(fx + fw / 2, fy + fh * 0.72, 10, fx + fw / 2, fy + fh * 0.72, fw * 0.6);
      rg.addColorStop(0, 'rgba(255,233,180,0.32)'); rg.addColorStop(1, 'rgba(255,233,180,0)');
      cg.fillStyle = rg; cg.fillRect(fx, fy, fw, fh);
      F.chest(cg, fx + fw / 2 - 70, fy + fh - 130, 1.6, t, { glint: 0.9 + 0.1 * Math.sin(t * 3), glintR: 6, ring: [0.95 * 180, 0.08 * 180] });
    });
    S.roundRect(g, fx, fy, fw, fh, 16, null, '#3A3F52', 3);
    S.label(g, 'ITEM 001  ·  Treasure Chest?', fx + 26, fy + 38, 26, { align: 'left', color: '#FFF4D6', weight: 900 });
    S.label(g, 'STATUS: dormant (?)', fx + 26, fy + 74, 20, { align: 'left', color: '#C59BFF', weight: 800 });
    // card slot
    if (!dropped) {
      g.save(); g.setLineDash([16, 12]); g.lineDashOffset = -t * 30;
      S.roundRect(g, SLOT[0] - CW / 2 - 14, SLOT[1] - CH / 2 - 14, CW + 28, CH + 28, 22, 'rgba(255,224,138,0.05)', 'rgba(255,224,138,0.55)', 4);
      g.restore();
      S.label(g, 'DRAG RULE HERE', SLOT[0], SLOT[1], 28, { color: 'rgba(255,224,138,0.6)', weight: 900 });
    }
    S.label(g, 'Read before opening ANYTHING.', SLOT[0], PY + PH - 50, 22, { color: 'rgba(232,236,246,0.6)', weight: 800 });
    g.restore();
  }

  const RULE = { num: 1, text: ['If a chest is alone', 'in an empty room,', 'do NOT open it.'], stamp: 'MANDATORY' };

  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    const B = CS.box;
    const wipeK = E.easeInCubic(P(t, T.wipe, T.wipeEnd - T.wipe)), R = wipeK * 2300;
    const dropped = t >= T.drop;
    const cur = cursorAt(t);
    // velocity (for stretch while flying / card swing while dragging)
    const a = cursorAt(Math.max(0, t - 1 / 60)).p, b = cursorAt(t + 1 / 60).p;
    const vx = (b[0] - a[0]) * 30, vy = (b[1] - a[1]) * 30, sp = Math.hypot(vx, vy);

    // ---- background: the room (until the wipe has covered it)
    const screenUI = g => {
      // hover UI on the chest (fades as the wipe starts)
      const ui = 1 - S.clamp(wipeK * 4);
      if (t > T.hover - 0.05 && ui > 0) {
        g.save(); g.globalAlpha *= ui;
        const sel = E.easeOutCubic(P(t, T.hover - 0.05, 0.3));
        K.target(g, B.x, B.y, B.w, B.h, { pop: P(t, T.hover - 0.05, 0.28), t, color: '#7FD3FF', lw: 6 });
        if (sel >= 1) K.selection(g, B.x, B.y, B.x + B.w, B.y + B.h, { t, fill: 0.07, handles: P(t, T.hover + 0.3, 0.1) > 0.5 });
        CS.tip(g, 1150, 356, P(t, T.hover + 0.15, 0.35));
        CS.keys(g, 1156, 572, P(t, T.hover + 0.4, 0.3));
        g.restore();
      }
    };
    if (wipeK < 1) {
      const gl = t < T.hover ? 0.85 : 0.85 + 0.15 * S.clamp((t - T.hover) * 3) + (t > T.click && t < T.click + 0.3 ? 0.6 * Math.sin(P(t, T.click, 0.3) * Math.PI) : 0);
      CS.room(ctx, t, { glint: gl, glintR: 6 + (gl - 0.85) * 4, room: { screen: screenUI } });
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const k = c.width / 1920; ctx.scale(k, k);
    // ---- the menu, revealed by an iris from the click point
    if (wipeK > 0) {
      ctx.save();
      if (wipeK < 1) { ctx.beginPath(); ctx.arc(CLICK[0], CLICK[1], R, 0, Math.PI * 2); ctx.clip(); }
      menu(ctx, t, P(t, T.wipe + 0.22, 0.35), dropped);
      ctx.restore();
      if (wipeK < 1) { ctx.save(); ctx.strokeStyle = 'rgba(255,224,138,0.85)'; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(CLICK[0], CLICK[1], R, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); }
    }
    // ---- the RULE 1 card
    if (t >= T.cardIn) {
      let cx, cy, rot = 0, lift = 0, sc = 1, glow = 0;
      if (t < T.grab) {
        const kk = E.easeOutBack(P(t, T.cardIn, 0.4), 1.4);
        cx = CARD0[0]; cy = lerp(1400, CARD0[1], kk); rot = -0.1 + 0.03 * Math.sin(t * 6);
        glow = t > T.reach - 0.1 ? 0.8 : 0.4;
      } else if (!dropped) {
        const g0 = grabPt(t);
        rot = S.clamp(vx * 0.00022, -0.32, 0.32) - 0.1 * (1 - dragK(t));
        const off = S.rot(0, -GRAB_DY, rot);
        cx = g0[0] + off[0]; cy = g0[1] + off[1]; lift = 1; glow = 0.5;
      } else {
        const kk = P(t, T.drop, 0.5);
        cx = SLOT[0]; cy = SLOT[1]; rot = 0.08 * S.wobble(t - T.drop, 3, 5); sc = 1 + 0.08 * (1 - S.spring(t - T.drop, 3, 0.35)) * -1 + 0.0;
        sc = 0.94 + 0.06 * S.spring(t - T.drop, 3.2, 0.3); glow = 1 - kk * 0.6;
      }
      ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc);
      K.card(ctx, 0, 0, CW, CH, Object.assign({ rot, lift, glow }, RULE));
      ctx.restore();
      if (dropped) { // drop burst
        const q = P(t, T.drop, 0.55);
        if (q < 1) for (let i = 0; i < 10; i++) {
          const an = i / 10 * Math.PI * 2 + 0.3, r0 = 240 + E.easeOutCubic(q) * 120;
          S.sparkle(ctx, SLOT[0] + Math.cos(an) * r0 * 0.85, SLOT[1] + Math.sin(an) * r0, 16 * (1 - q), i % 2 ? '#FFE08A' : '#FFFFFF', q * 2);
        }
      }
    }
    // ---- HUD (always on top of backgrounds)
    CS.hud(ctx, { rules: dropped ? 1 : 0, line: dropped ? 'RULE 1 learned!' : undefined });
    if (dropped) {
      const q = P(t, T.drop, 0.6);
      S.label(ctx, '+1', 500, 66 - q * 24, 26, { color: '#FFC83D', weight: 1000, alpha: 1 - S.smoothstep(0.6, 1, q) });
    }
    // ---- Pip
    const st = cur.state;
    const flying = t < T.hover;
    const o = { state: st, expr: cur.expr, t, look: [0, 0] };
    if (flying) {
      o.squash = -S.clamp(sp / 4000, 0, 0.5); o.stretchDir = Math.atan2(vy, vx); o.tilt = S.clamp(vx / 6000, -0.4, 0.4);
      // speed lines
      if (sp > 300) {
        ctx.save(); ctx.strokeStyle = `rgba(255,255,255,${S.clamp(sp / 4000) * 0.6})`; ctx.lineWidth = 5; ctx.lineCap = 'round';
        const ux = vx / sp, uy = vy / sp;
        [[-14, 30], [10, 55], [32, 40]].forEach(([nx, ny], i) => {
          const x0 = cur.p[0] + nx * 1.35 + 40, y0 = cur.p[1] + ny * 1.35;
          ctx.beginPath(); ctx.moveTo(x0 - ux * 30, y0 - uy * 30); ctx.lineTo(x0 - ux * (90 + i * 30), y0 - uy * (90 + i * 30)); ctx.stroke();
        });
        ctx.restore();
      }
    }
    if (t >= T.hover && t < T.wipe) {
      o.glow = S.clamp((t - T.hover) * 3) * 0.75; o.look = [-0.6, 0.5];
      o.blink = t > 1.42 && t < 1.53 ? 1 : 0;
      o.tilt = S.deg(-6) + 0.06 * S.wobble(t - T.hover, 3, 4);
      if (t >= T.click) { o.ripple = P(t, T.click, 0.5); o.press = Math.sin(P(t, T.click, 0.22) * Math.PI); }
    }
    if (t >= T.wipe && t < T.reach) { const kk = P(t, T.wipe, T.reach - T.wipe); o.tilt = Math.sin(kk * Math.PI) * -0.3; o.squash = -0.2 * Math.sin(kk * Math.PI); o.stretchDir = Math.atan2(vy, vx); o.look = [-0.4, 0.6]; }
    if (st === 'hand') { o.glow = 0.6; o.squash = 0.1 * S.wobble(t - T.reach, 4, 6); }
    if (st === 'grab') { o.squash = 0.18 * (1 - P(t, T.grab, 0.15)) + 0.05; o.tilt = S.clamp(vx * 0.00012, -0.2, 0.2); }
    if (t >= T.drop) { o.tilt = S.deg(-8) + 0.25 * S.wobble(t - T.drop - 0.5, 3, 3); o.squash = 0.3 * S.wobble(t - T.drop, 4, 5); o.blush = 1; }
    K.draw(ctx, cur.p[0], cur.p[1], 1.35, o);
  };
})();
