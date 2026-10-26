/* sheet.js : cursor model sheet (states, expressions, emotes, v2 game-UI swaps + widgets). 1920x1700.
 * Loads after lib_core.js and cursor/cursor.js.
 * SMALL=1 node render_sf.mjs core/lib_core.js,cursor/cursor.js,cursor/sheet.js <out.png> 0 1920 1700 */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, K = window.CURSOR;
  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, c.width, c.height, { bg: '#1B1E2A', title: 'PIP · the cursor host (alt concept)', subtitle: 'game-UI pointer that explains things · white body, one hard shade, ink edge · emotes only with two dots, tilt, squash, wiggle, ripple, glow · hotspot = tip · v2: icon swaps pop (squash/stretch)' });
    const row = (y, label) => {
      S.label(ctx, label, 50, y, 20, { align: 'left', color: '#FFE08A', weight: 900 });
      ctx.fillStyle = 'rgba(255,255,255,0.07)'; ctx.fillRect(50, y + 18, 1820, 2);
    };
    const tag = (txt, x, y) => S.label(ctx, txt, x, y, 19, { color: 'rgba(240,242,250,0.7)', weight: 800 });

    // ---- row 1: states
    row(135, 'STATES  (v2: hourglass · right-click · double-click)');
    const st = [
      ['point', {}], ['click', { ripple: 0.22, press: 1, expr: 'focus' }], ['drag', { expr: 'focus' }],
      ['hand', { expr: 'happy' }], ['grab', { expr: 'focus' }], ['loading', { expr: 'blink', spin: 0.3 }], ['forbidden', { expr: 'annoyed' }],
      ['hourglass', { expr: 'neutral', sand: 0.45, t: 0.2 }], ['rclick', { expr: 'wow' }], ['dclick', { expr: 'focus' }],
    ];
    st.forEach(([name, o], i) => {
      const cx = 110 + i * 186, s = 1.38;
      let hx = cx - 34, hy = 215;
      if (name === 'hand') { hx = cx - 18; hy = 210; }
      if (name === 'grab') { hx = cx - 4; hy = 280; }
      if (name === 'drag') { hx = cx + 30; hy = 250; o.from = [hx - 120, hy - 70]; }
      K.draw(ctx, hx, hy, s, Object.assign({ state: name, t }, o));
      tag(name, cx, 400);
    });

    // ---- row 2: expressions
    row(445, 'EXPRESSIONS (two dots or none)');
    ['neutral', 'happy', 'blink', 'wow', 'worried', 'annoyed', 'smug', 'focus', 'dizzy', 'love', 'none'].forEach((e, i) => {
      const cx = 120 + i * 168;
      K.draw(ctx, cx - 26, 500, 1.1, { expr: e, blush: e === 'love' || e === 'happy' ? 1 : 0, look: e === 'worried' ? [-0.5, 0.3] : null });
      tag(e, cx, 650);
    });

    // ---- row 3: emotes + the icon-swap pop
    row(695, 'EMOTES                                                                                                    ICON SWAP POP  (point -> hourglass: scale-in spring, squash -> stretch -> settle, poof)');
    const em = [
      ['tilt -20°', { tilt: S.deg(-20), expr: 'smug' }],
      ['tilt +25°', { tilt: S.deg(25), expr: 'wow' }],
      ['squash', { squash: 0.45, expr: 'happy' }],
      ['stretch (fly)', { squash: -0.55, stretchDir: S.deg(-150), expr: 'focus', tilt: S.deg(-10) }],
      ['wiggle', { wiggle: 1, t: 0.07, expr: 'worried' }],
      ['hover glow', { glow: 1, expr: 'wow', look: [0.4, 0.5] }],
    ];
    em.forEach(([name, o], i) => {
      const cx = 110 + i * 150;
      if (name === 'wiggle') [-1, 1].forEach(sg => K.draw(ctx, cx - 30, 765, 1.1, { tilt: sg * 0.2, expr: 'worried', alpha: 0.28, shadow: false }));
      K.draw(ctx, cx - 30, 765, 1.1, Object.assign({ t }, o));
      tag(name, cx, 930);
    });
    [[0.0, 'point'], [0.04, 'swap 0.04 s'], [0.09, '0.09 s'], [0.16, '0.16 s'], [0.26, '0.26 s'], [0.6, 'settled']].forEach(([sw, lb], i) => {
      const cx = 1040 + i * 152, isP = i === 0;
      K.draw(ctx, cx - 30, 770, 1.15, { state: isP ? 'point' : 'hourglass', expr: isP ? 'focus' : 'neutral', sand: 0.3, swap: isP ? null : sw, t: 0.3 });
      tag(lb, cx, 930);
      if (i < 5) S.label(ctx, '›', cx + 76, 830, 30, { color: 'rgba(255,224,138,0.5)', weight: 900 });
    });

    // ---- row 4: game-UI actions
    row(975, 'GAME UI  ·  right-click menu  ·  double-click  ·  hourglass (sand runs, flips)  ·  map move button');
    const items = [{ label: 'Open', key: 'E' }, { label: 'Inspect', key: 'I' }, { label: 'Is this a mimic?', key: '?', color: '#C59BFF' }, { label: 'Report to HR', key: 'HR', color: '#FF8A96' }];
    K.menu(ctx, 90, 1035, { items, title: 'TREASURE CHEST?', hover: 1, w: 330 });
    const mr = K.menuRow(90, 1035, 1, { w: 330 });
    K.draw(ctx, mr[0] + 120, mr[1] + 6, 1.0, { state: 'point', expr: 'happy', t });
    K.ripple(ctx, 90, 1035, 0.6, 0.45);
    tag('right-click menu (hover slides, pick flashes)', 255, 1355);
    // double click
    K.draw(ctx, 560, 1160, 1.2, { state: 'dclick', expr: 'focus', dbl: 0.36, press: 0.6, t });
    tag('double-click: 2 ripples + sparks', 625, 1355);
    // hourglass cycle
    [['sand 0.1', { sand: 0.1 }], ['sand 0.6', { sand: 0.6 }], ['flip', { sand: 1, flip: 0.5 }], ['flipped', { sand: 0, flip: 0 }]].forEach(([lb, o], i) => {
      const cx = 820 + i * 118;
      K.draw(ctx, cx - 26, 1130, 1.0, Object.assign({ state: 'hourglass', expr: i === 2 ? 'dizzy' : 'blink', t: 0.37 }, o));
      tag(lb, cx, 1300);
    });
    tag('hourglass: sand flows, then flips', 995, 1355);
    // minimap + move button pressed by the hand
    K.minimap(ctx, 1330, 1060, { at: [0.55, 1], visited: 2, press: 0.85, glow: 0.6, t });
    const mb = K.MINIMAP.btn(1330, 1060);
    K.draw(ctx, mb[0] + 26, mb[1] + 12, 1.0, { state: 'hand', expr: 'focus', press: 0.8, squash: 0.15, t });
    tag('map move: corner minimap, MOVE button sinks, pip slides to the next room', 1520, 1355);

    // ---- row 5: on-screen UI
    row(1400, 'ON-SCREEN UI  ·  buttons depress  ·  tabs switch  ·  slider drags');
    [['idle', 0, 0], ['hover', 0, 0.8], ['pressed', 1, 0.4]].forEach(([lb, pr, gl], i) => {
      const bx = 70 + i * 230;
      K.button(ctx, bx, 1470, 190, 64, { label: 'OPEN', press: pr, glow: gl, color: i === 2 ? '#FFD86B' : '#FFC83D' });
      if (i) K.draw(ctx, bx + 160, 1508 + pr * 10, 0.85, { state: i === 2 ? 'hand' : 'point', expr: i === 2 ? 'focus' : 'happy', press: pr, t });
      tag(lb, bx + 95, 1650);
    });
    K.tabs(ctx, 820, 1480, { tabs: ['MAP', 'BAG', 'RULES'], active: 2, prev: 0, k: 0.8, press: { i: 2, k: 0.7 }, tw: 140 });
    const ta = K.tabAt(820, 1480, 2, { tw: 140 });
    K.draw(ctx, ta[0] + 48, ta[1] + 16, 0.9, { state: 'hand', expr: 'happy', press: 0.7, t });
    tag('tab switch (underline slides MAP -> RULES)', 1040, 1650);
    K.slider(ctx, 1420, 1530, 400, { value: 0.62, grab: 1, label: 'TORCH BRIGHTNESS' });
    const kn = K.sliderKnob(1420, 1530, 400, 0.62);
    K.draw(ctx, kn[0], kn[1], 0.85, { state: 'grab', expr: 'focus', t });
    tag('slider drag (knob grows, value bubble)', 1620, 1650);
  };
})();
