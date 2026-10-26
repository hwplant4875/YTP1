/* motion2.js : cursor-host motion test v2 (~9.6 s), the game-UI icon swaps.
 * Pip flies in and hovers the lone chest -> RIGHT-CLICK (rclick icon, context menu pops, picks "Inspect") -> HOURGLASS
 * while inspecting (sand runs, flips) -> result tooltip -> DOUBLE-CLICK the chest (two ripples + sparks, the chest jolts:
 * LOCKED) -> flies to the corner minimap, presses MOVE -> the background slides to the corridor -> presses the RULES tab
 * -> the RULE 1 card pops up. Every icon swap pops (CURSOR opts.swap).
 * Loads after cursor/scene.js (reuses CURSOR_SCENE) and needs dungeon/dungeon.js for the corridor plate.
 * node render_seq.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,comp/frame0.js,cursor/cursor.js,cursor/scene.js,cursor/motion2.js <out.mp4> 9.6 30
 * Stills: render_sf.mjs with the same list and t. */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, K = window.CURSOR, CS = window.CURSOR_SCENE, F = window.FRAME0, D = window.DUNGEON, C = S.color, E = S.ease;
  const P = S.prog, lerp = S.lerp, clamp = S.clamp;
  const bez = (a, b, cc, k) => [lerp(lerp(a[0], cc[0], k), lerp(cc[0], b[0], k), k), lerp(lerp(a[1], cc[1], k), lerp(cc[1], b[1], k), k)];
  const SC = 1.35;

  // ---------------------------------------------------------------- layout
  const HOV = [1004, 430];
  const MENU = [HOV[0] + 4, HOV[1] + 4], MW = 340;
  const ITEMS = [{ label: 'Open', key: 'E' }, { label: 'Inspect', key: 'I' }, { label: 'Is this a mimic?', key: '?', color: '#C59BFF' }, { label: 'Report to HR', key: 'HR', color: '#FF8A96' }];
  const ROW1 = K.menuRow(MENU[0], MENU[1], 1, { w: MW });
  const PICK = [ROW1[0] + 40, ROW1[1] + 2];
  const DC = [872, 520];                                   // double-click spot on the chest lid
  const MMX = 1500, MMY = 730, BTN = K.MINIMAP.btn(MMX, MMY), BTN_P = [BTN[0] + 4, BTN[1] - 4];
  const TABW = 150, TX = 1920 - 40 - (3 * TABW + 16), TY = 44, TAB = K.tabAt(TX, TY, 2, { tw: TABW }), TAB_P = [TAB[0] + 6, TAB[1] + 2];
  const REST = [1210, 440];
  const CW = 330, CH = 430, CARD = [960, 600];

  // ---------------------------------------------------------------- timeline (s)
  const T = {
    fly: 0.8, rswap: 1.2, rclick: 1.32, menu: 1.38, pswap1: 1.55, toRow: 1.62, atRow: 2.05, pick: 2.15, close: 2.45,
    hg: 2.55, flip: 3.25, flipEnd: 3.55, hgEnd: 3.95, tipOut: 5.6,
    toDC: 4.2, atDC: 4.55, dswap: 4.55, dbl: 4.68, pswap2: 5.5,
    toBtn: 5.55, atBtn: 6.15, hswap: 6.15, press: 6.32, slide: 6.45, slideEnd: 7.25,
    pswap3: 7.3, toTab: 7.35, atTab: 7.85, tswap: 7.85, tpress: 8.0, card: 8.12, toRest: 8.55, atRest: 9.05, end: 9.6,
  };
  const DUR = T.end;

  // cursor path: [t0, t1, from, to, ctrl]
  const PATH = [
    [0, T.fly, [2080, 60], HOV, [1560, 40], 'back'],
    [T.toRow, T.atRow, HOV, PICK, [HOV[0] + 40, PICK[1] - 10], 'io'],
    [T.close + 0.02, T.atDC - 0.1, PICK, DC, [1040, 640], 'io'],   // runs after the hourglass (it waits below)
    [T.toBtn, T.atBtn, DC, BTN_P, [1500, 640], 'io'],
    [T.toTab, T.atTab, BTN_P, TAB_P, [1900, 420], 'io'],
    [T.toRest, T.atRest, TAB_P, REST, [1420, 240], 'io'],
  ];
  function pos(t) {
    // the hourglass phase holds the cursor on the Inspect row, then it moves to the chest
    if (t >= T.close && t < T.toDC) return PICK;
    let last = PATH[0][2];
    for (const [t0, t1, a, b, cc, ez] of PATH) {
      let A0 = t0, A1 = t1;
      if (a === PICK && b === DC) { A0 = T.toDC; A1 = T.atDC - 0.05; }
      if (t < A0) return last;
      if (t <= A1) { const k = P(t, A0, A1 - A0); return bez(a, b, cc, ez === 'back' ? E.easeOutBack(k, 1.25) : E.easeInOutCubic(k)); }
      last = b;
    }
    return last;
  }
  // which icon and when it was swapped in
  const SWAPS = [[0, 'point'], [T.rswap, 'rclick'], [T.pswap1, 'point'], [T.hg, 'hourglass'], [T.hgEnd, 'point'], [T.dswap, 'dclick'],
    [T.pswap2, 'point'], [T.hswap, 'hand'], [T.pswap3, 'point'], [T.tswap, 'hand'], [T.card + 0.25, 'point']];
  function icon(t) { let cur = SWAPS[0]; for (const s of SWAPS) if (t >= s[0]) cur = s; return { state: cur[1], swap: cur[0] > 0 ? t - cur[0] : null }; }

  // ---------------------------------------------------------------- offscreen layers for the background slide
  let LA = null, LB = null;
  const layer = () => { const cv = document.createElement('canvas'); cv.width = c.width; cv.height = c.height; return cv; };

  function roomScene(ctx, t) {
    const B = CS.box;
    // chest jolts on each click of the double click
    const hop = t > T.dbl ? Math.max(0, Math.sin(P(t, T.dbl, 0.16) * Math.PI)) * 12 + Math.max(0, Math.sin(P(t, T.dbl + 0.2, 0.18) * Math.PI)) * 16 : 0;
    const jx = t > T.dbl && t < T.dbl + 0.8 ? 4 * S.wobble(t - T.dbl - 0.2, 6, 6) : 0;
    let gl = 0.85;
    if (t > T.fly) gl += 0.15 * clamp((t - T.fly) * 3);
    if (t > T.hg && t < T.hgEnd) gl += 0.25 * (0.5 + 0.5 * Math.sin(t * 9));            // something inside reacts
    if (t > T.dbl && t < T.dbl + 0.6) gl += 0.8 * Math.sin(P(t, T.dbl, 0.6) * Math.PI);
    CS.room(ctx, t, {
      glint: gl, glintR: 6 + (gl - 0.85) * 4,
      room: {
        actors: (g, info) => F.chest(g, F.x + jx / 1.5, info.contactY + 12 - hop / 1.5, F.s, t, { glint: gl, glintR: 6 + (gl - 0.85) * 4 }),
        screen: g => {
          const ui = 1 - P(t, T.slide - 0.05, 0.2);
          if (t > T.fly - 0.05 && ui > 0) {
            g.save(); g.globalAlpha *= ui;
            K.target(g, B.x, B.y, B.w, B.h, { pop: P(t, T.fly - 0.05, 0.28), t, color: '#7FD3FF', lw: 6 });
            // inspect result tooltip
            if (t > T.hgEnd && t < T.tipOut + 0.3) CS.tip(g, 1150, 356, P(t, T.hgEnd + 0.02, 0.35) * (1 - P(t, T.tipOut, 0.25)));
            g.restore();
          }
        },
      },
    });
  }
  function corridorScene(ctx, t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    D.corridor(ctx, t, {});
  }

  // ---------------------------------------------------------------- overlays
  function inspectBar(ctx, t) {
    const a = P(t, T.hg, 0.15) * (1 - P(t, T.hgEnd, 0.15)); if (a <= 0) return;
    const x = 690, y = 790, w = 370;
    ctx.save(); ctx.globalAlpha *= a;
    S.roundRect(ctx, x - 4, y - 4, w + 8, 64, 16, '#15131A');
    S.roundRect(ctx, x, y, w, 56, 12, 'rgba(20,24,38,0.95)');
    const dots = '.'.repeat(1 + Math.floor(t * 4) % 3);
    S.label(ctx, 'INSPECTING' + dots, x + 18, y + 18, 17, { align: 'left', color: '#FFE08A', weight: 1000 });
    S.roundRect(ctx, x + 18, y + 34, w - 36, 10, 5, '#2A3044');
    const k = E.easeInOutSine(P(t, T.hg + 0.05, T.hgEnd - T.hg - 0.15));
    S.roundRect(ctx, x + 18, y + 34, Math.max(10, (w - 36) * k), 10, 5, '#FFC83D');
    ctx.restore();
  }
  function lockedPop(ctx, t) {
    const q = P(t, T.dbl + 0.32, 1.0); if (q <= 0 || q >= 1) return;
    const e = E.easeOutBack(P(t, T.dbl + 0.32, 0.3), 2.2), a = 1 - S.smoothstep(0.75, 1, q);
    ctx.save(); ctx.globalAlpha *= a; ctx.translate(700, 380 - q * 30); ctx.rotate(-0.08); ctx.scale(e, e);
    S.roundRect(ctx, -134, -34, 268, 68, 16, '#15131A');
    S.roundRect(ctx, -130, -30, 260, 60, 13, '#E2475A');
    S.label(ctx, 'LOCKED', 0, -6, 30, { color: '#FFFFFF', weight: 1000 });
    S.label(ctx, '(from the inside?)', 0, 18, 15, { color: '#FFE3E6', weight: 900 });
    ctx.restore();
  }
  function slideFX(ctx, k) {
    if (k <= 0 || k >= 1) return;
    const a = Math.sin(k * Math.PI);
    ctx.save(); ctx.lineCap = 'round';
    for (let i = 0; i < 9; i++) {
      const y = 120 + i * 105 + (S.hash(i * 7.1) - 0.5) * 50, len = 260 + S.hash(i * 3.3) * 320, x = 1920 - ((k * 2600 + S.hash(i) * 1900) % 2600);
      ctx.strokeStyle = `rgba(255,255,255,${0.22 * a})`; ctx.lineWidth = 5 + S.hash(i * 1.7) * 6;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + len, y); ctx.stroke();
    }
    ctx.restore();
  }
  // corridor name banner once the slide lands
  function roomBanner(ctx, t) {
    const q = P(t, T.slideEnd - 0.05, 1.1); if (q <= 0 || q >= 1) return;
    const e = E.easeOutBack(P(t, T.slideEnd - 0.05, 0.3), 1.6), a = 1 - S.smoothstep(0.7, 1, q);
    ctx.save(); ctx.globalAlpha *= a * clamp(e * 2);
    ctx.translate(960, 230); ctx.scale(lerp(0.8, 1, e), lerp(0.8, 1, e));
    S.roundRect(ctx, -260, -46, 520, 92, 18, 'rgba(10,12,18,0.78)');
    S.roundRect(ctx, -252, -38, 504, 76, 12, null, 'rgba(255,224,138,0.45)', 2);
    S.label(ctx, 'B1 · THE LONG HALL', 0, -10, 32, { color: '#FFF4D6', weight: 1000 });
    S.label(ctx, 'room 2 of ?', 0, 22, 18, { color: '#C59BFF', weight: 900 });
    ctx.restore();
  }

  const RULE = { num: 1, text: ['If a chest is alone', 'in an empty room,', 'do NOT open it.'], stamp: 'MANDATORY' };

  window.draw = t => {
    t = Math.min(t || 0, DUR);
    const ctx = c.getContext('2d');
    const kz = c.width / 1920;
    const slideK = E.easeInOutCubic(P(t, T.slide, T.slideEnd - T.slide));

    // ---- background: room -> slides left, corridor slides in from the right
    if (slideK <= 0) roomScene(ctx, t);
    else if (slideK >= 1) corridorScene(ctx, t);
    else {
      LA = LA || layer(); LB = LB || layer();
      roomScene(LA.getContext('2d'), t); corridorScene(LB.getContext('2d'), t);
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
      const off = Math.round(slideK * c.width);
      ctx.drawImage(LA, -off, 0); ctx.drawImage(LB, c.width - off, 0);
      ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(c.width - off - 6 * kz, 0, 12 * kz, c.height); // seam
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.scale(kz, kz);
    slideFX(ctx, slideK);

    // ---- in-world overlays
    inspectBar(ctx, t);
    lockedPop(ctx, t);
    roomBanner(ctx, t);
    // context menu
    if (t >= T.menu && t < T.close + 0.2) {
      const pop = t < T.close ? P(t, T.menu, 0.32) : 1 - P(t, T.close, 0.15);
      const p = pos(t);
      let hover = null;
      const rowTop = MENU[1] + 56;
      if (p[0] > MENU[0] + 8 && p[1] > rowTop) hover = clamp((p[1] - rowTop) / 52 - 0.5, 0, 3);
      if (t >= T.atRow) hover = 1;
      K.menu(ctx, MENU[0], MENU[1], { items: ITEMS, title: 'TREASURE CHEST?', w: MW, pop, hover, pick: t >= T.pick ? P(t, T.pick, 0.3) : 0 });
    }

    // ---- HUD: quest tracker, minimap (bottom-right), tabs (top-right)
    const learned = t >= T.card + 0.3;
    CS.hud(ctx, { rules: learned ? 1 : 0, line: learned ? 'RULE 1 learned!' : undefined });
    if (learned) { const q = P(t, T.card + 0.3, 0.6); S.label(ctx, '+1', 500, 66 - q * 24, 26, { color: '#FFC83D', weight: 1000, alpha: 1 - S.smoothstep(0.6, 1, q) }); }
    const btnPress = t >= T.press ? Math.sin(P(t, T.press, 0.26) * Math.PI) : 0;
    K.minimap(ctx, MMX, MMY, { at: [lerp(0, 1, slideK), 1], visited: slideK >= 1 ? 2 : 1, press: btnPress, glow: t > T.atBtn - 0.2 && t < T.slideEnd ? 0.7 : 0, t });
    const tabK = P(t, T.tpress + 0.05, 0.3);
    K.tabs(ctx, TX, TY, { tabs: ['MAP', 'BAG', 'RULES'], active: t >= T.tpress + 0.05 ? 2 : 0, prev: 0, k: t >= T.tpress + 0.05 ? tabK : 1, tw: TABW,
      press: t >= T.tpress ? { i: 2, k: Math.sin(P(t, T.tpress, 0.26) * Math.PI) } : null });

    // ---- RULE 1 card: springs out of the RULES tab to centre
    if (t >= T.card) {
      const k = E.easeOutBack(P(t, T.card, 0.45), 1.5), kp = E.easeOutCubic(P(t, T.card, 0.4));
      const cx = lerp(TAB[0], CARD[0], kp), cy = lerp(TAB[1] + 30, CARD[1], kp), sc = lerp(0.15, 1, k);
      // dim the room behind it a little
      ctx.fillStyle = `rgba(6,8,14,${0.4 * kp})`; ctx.fillRect(0, 0, 1920, 1080);
      ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc);
      K.card(ctx, 0, 0, CW, CH, Object.assign({ rot: lerp(0.3, -0.03, kp) + 0.02 * Math.sin(t * 2.2) * kp, glow: 1 - 0.5 * P(t, T.card + 0.5, 0.6), lift: 0.4 }, RULE));
      ctx.restore();
      const q = P(t, T.card + 0.3, 0.6);
      if (q > 0 && q < 1) for (let i = 0; i < 10; i++) {
        const an = i / 10 * Math.PI * 2 + 0.3, r0 = 250 + E.easeOutCubic(q) * 120;
        S.sparkle(ctx, CARD[0] + Math.cos(an) * r0 * 0.85, CARD[1] + Math.sin(an) * r0, 16 * (1 - q), i % 2 ? '#FFE08A' : '#FFFFFF', q * 2);
      }
      // the card covers the HUD tabs? redraw the quest HUD on top (it is the payoff)
      CS.hud(ctx, { rules: learned ? 1 : 0, line: learned ? 'RULE 1 learned!' : undefined });
    }

    // ---- Pip
    const p = pos(t).slice(), ic = icon(t);
    const a = pos(Math.max(0, t - 1 / 60)), b = pos(t + 1 / 60);
    const vx = (b[0] - a[0]) * 30, vy = (b[1] - a[1]) * 30, sp = Math.hypot(vx, vy);
    const o = { state: ic.state, swap: ic.swap, expr: 'focus', t, look: [0, 0] };
    if (sp > 250) { o.squash = -clamp(sp / 4500, 0, 0.45); o.stretchDir = Math.atan2(vy, vx); o.tilt = clamp(vx / 7000, -0.35, 0.35); }
    if (t < T.fly && sp > 300) {   // speed lines on the entrance
      ctx.save(); ctx.strokeStyle = `rgba(255,255,255,${clamp(sp / 4000) * 0.6})`; ctx.lineWidth = 5; ctx.lineCap = 'round';
      const ux = vx / sp, uy = vy / sp;
      [[-14, 30], [10, 55], [32, 40]].forEach(([nx, ny], i) => {
        const x0 = p[0] + nx * SC + 40, y0 = p[1] + ny * SC;
        ctx.beginPath(); ctx.moveTo(x0 - ux * 30, y0 - uy * 30); ctx.lineTo(x0 - ux * (90 + i * 30), y0 - uy * (90 + i * 30)); ctx.stroke();
      });
      ctx.restore();
    }
    // per-phase acting
    if (t >= T.fly && t < T.toRow) {        // hover the chest, then right-click
      o.glow = clamp((t - T.fly) * 3) * 0.75; o.look = [-0.6, 0.5]; o.expr = 'wow';
      o.tilt = S.deg(-6) + 0.06 * S.wobble(t - T.fly, 3, 4);
      if (t >= T.rclick) { o.press = Math.sin(P(t, T.rclick, 0.2) * Math.PI); o.ripple = P(t, T.rclick, 0.45); o.expr = 'smug'; }
    }
    if (t >= T.toRow && t < T.close) { o.expr = t >= T.atRow ? 'happy' : 'focus'; o.look = [0, 0.6];
      if (t >= T.pick) { o.press = Math.sin(P(t, T.pick, 0.2) * Math.PI); o.ripple = P(t, T.pick, 0.45); o.state = t < T.pick + 0.2 ? 'click' : o.state; } }
    if (ic.state === 'hourglass') {
      o.expr = 'blink'; o.look = [-0.4, 0.4];
      // sand: run, flip, run again
      if (t < T.flip) { o.sand = P(t, T.hg + 0.1, T.flip - T.hg - 0.12); }
      else if (t < T.flipEnd) { o.sand = 1; o.flip = P(t, T.flip, T.flipEnd - T.flip); o.expr = 'dizzy'; }
      else { o.sand = P(t, T.flipEnd, 0.6); }
      o.tilt = 0.08 * Math.sin(t * 3.2);
    }
    if (t >= T.hgEnd && t < T.toDC) { o.expr = 'wow'; o.look = [0.6, -0.3]; o.tilt = S.deg(-4); }
    if (t >= T.toDC && t < T.pswap2) {
      o.expr = 'focus'; o.look = [-0.3, 0.6];
      if (t >= T.dbl) {
        o.dbl = P(t, T.dbl, 0.75);
        o.press = Math.max(Math.sin(P(t, T.dbl, 0.12) * Math.PI), Math.sin(P(t, T.dbl + 0.21, 0.12) * Math.PI));
        o.expr = t > T.dbl + 0.4 ? 'worried' : 'focus';
        if (t > T.dbl + 0.4) o.wiggle = 0.6 * (1 - P(t, T.dbl + 0.4, 0.6));
      }
    }
    if (ic.state === 'hand' && t < T.slideEnd + 0.05) {
      o.expr = t < T.press ? 'focus' : 'wow'; o.look = [-0.5, 0];
      if (t >= T.press) { o.press = btnPress; o.squash = 0.18 * btnPress; }
      if (t >= T.slide) o.tilt = -0.18 * Math.sin(slideK * Math.PI);
    }
    if (t >= T.pswap3 && t < T.tswap) o.expr = 'happy';
    if (ic.state === 'hand' && t >= T.tswap) {
      o.expr = 'focus'; o.look = [0, -0.4];
      if (t >= T.tpress) { const pr = Math.sin(P(t, T.tpress, 0.26) * Math.PI); o.press = pr; o.squash = 0.18 * pr; o.expr = 'happy'; }
    }
    if (t >= T.card + 0.25) { o.expr = t > T.atRest ? 'happy' : 'wow'; o.look = [-0.7, 0.5]; o.blush = P(t, T.atRest, 0.3);
      if (t > T.atRest) { o.tilt = S.deg(-8) + 0.1 * Math.sin((t - T.atRest) * 4); p[1] += Math.sin((t - T.atRest) * 5) * 4; } }
    if (t > 1.0 && t < 1.1) o.blink = 1;
    K.draw(ctx, p[0], p[1], SC, o);
  };
})();
