// stamp sequence check (stampK 0 .. 1) at medium scale
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    [0, 0.6, 0.8, 0.9, 0.95, 1].forEach((k, i) => {
      HL.draw(ctx, 230 + i * 300, 1000, 1.45, { pose: 'stamp', face: 'pleased', stampK: k, stampMark: i === 0, t: 0.4, autoBlink: false });
      S.label(ctx, `stampK ${k}`, 200 + i * 310, 1040, 18, {});
    });
  };
})();
