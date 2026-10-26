// walk cycle strip (8 phases) + a front strip. node render_sf.mjs core/lib_core.js,host/helen.js,host/test_walk.js out.png
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    for (let i = 0; i < 8; i++) {
      HL.draw(ctx, 140 + i * 235, 1000, 1.45, { pose: 'walk', phase: i / 8, turn: 1, face: 'neutral', t: i / 8, autoBlink: false });
      S.label(ctx, `phase ${(i / 8).toFixed(3)}`, 140 + i * 235, 1040, 18, {});
    }
  };
})();
