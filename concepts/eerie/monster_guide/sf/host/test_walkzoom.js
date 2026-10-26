(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  const W = window.WALKCFG || [{}, {}];
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    W.forEach((cfg, r) => {
      [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875].forEach((ph, i) => {
        HL.draw(ctx, 130 + i * 235, 520 + r * 530, 0.95, { pose: 'walk', phase: ph, turn: 1, face: 'neutral', t: ph, autoBlink: false, _walk: cfg });
      });
      S.label(ctx, JSON.stringify(cfg), 20, 30 + r * 530, 18, { align: 'left' });
    });
  };
})();
