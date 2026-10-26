/* sheet.js : cursor model sheet (states, expressions, emotes). Loads after lib_core.js and cursor/cursor.js.
 * SMALL=1 node render_sf.mjs core/lib_core.js,cursor/cursor.js,cursor/sheet.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, K = window.CURSOR;
  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, 1920, 1080, { bg: '#1B1E2A', title: 'PIP · the cursor host (alt concept)', subtitle: 'game-UI pointer that explains things · white body, one hard shade, ink edge · emotes only with two dots, tilt, squash, wiggle, ripple, glow · hotspot = tip' });
    const row = (y, label) => {
      S.label(ctx, label, 50, y, 20, { align: 'left', color: '#FFE08A', weight: 900 });
      ctx.fillStyle = 'rgba(255,255,255,0.07)'; ctx.fillRect(50, y + 18, 1820, 2);
    };
    const tag = (txt, x, y) => S.label(ctx, txt, x, y, 19, { color: 'rgba(240,242,250,0.7)', weight: 800 });

    // ---- row 1: states
    row(140, 'STATES');
    const st = [
      ['point', {}], ['click', { ripple: 0.38, press: 1, expr: 'focus' }], ['drag', { from: [-150, -120], expr: 'focus' }],
      ['hand', { expr: 'happy' }], ['grab', { expr: 'focus' }], ['loading', { expr: 'blink', spin: 0.3 }], ['forbidden', { expr: 'annoyed' }],
    ];
    st.forEach(([name, o], i) => {
      const cx = 170 + i * 262, cy = 240, s = 1.55;
      let hx = cx - 40, hy = cy;
      if (name === 'hand') { hx = cx - 20; hy = cy - 10; }
      if (name === 'grab') { hx = cx - 4; hy = cy + 70; }
      if (name === 'drag') { hx = cx + 30; hy = cy + 40; o.from = [hx - 150, hy - 110]; }
      K.draw(ctx, hx, hy, s, Object.assign({ state: name, t }, o));
      tag(name, cx, 470);
    });

    // ---- row 2: expressions
    row(530, 'EXPRESSIONS (two dots or none)');
    const ex = ['neutral', 'happy', 'blink', 'wow', 'worried', 'annoyed', 'smug', 'focus', 'dizzy', 'love', 'none'];
    ex.forEach((e, i) => {
      const cx = 130 + i * 168;
      K.draw(ctx, cx - 30, 590, 1.3, { expr: e, blush: e === 'love' || e === 'happy' ? 1 : 0, look: e === 'worried' ? [-0.5, 0.3] : null });
      tag(e, cx, 770);
    });

    // ---- row 3: emotes
    row(820, 'EMOTES');
    const em = [
      ['tilt -20°', { tilt: S.deg(-20), expr: 'smug' }],
      ['tilt +25°', { tilt: S.deg(25), expr: 'wow' }],
      ['squash', { squash: 0.45, expr: 'happy' }],
      ['stretch (fly)', { squash: -0.55, stretchDir: S.deg(-150), expr: 'focus', tilt: S.deg(-10) }],
      ['wiggle', { wiggle: 1, t: 0.07, expr: 'worried' }],
      ['hover glow', { glow: 1, expr: 'wow', look: [0.4, 0.5] }],
      ['click ripple', { ripple: 0.55, state: 'click', expr: 'happy' }],
    ];
    em.forEach(([name, o], i) => {
      const cx = 170 + i * 262;
      if (name === 'wiggle') { // ghost frames to show the shake
        [-1, 1].forEach(sg => K.draw(ctx, cx - 40, 880, 1.25, { tilt: sg * 0.2, expr: 'worried', alpha: 0.28, shadow: false }));
      }
      K.draw(ctx, cx - 40, 880, 1.25, Object.assign({ t }, o));
      tag(name, cx, 1052);
    });
  };
})();
