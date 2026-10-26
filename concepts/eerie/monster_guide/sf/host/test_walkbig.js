(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    [0, 0.125, 0.25, 0.375].forEach((ph, i) => {
      ctx.save(); ctx.beginPath(); ctx.rect(i * 480, 0, 480, 1080); ctx.clip();
      HL.draw(ctx, 200 + i * 480, 1040, 2.3, { pose: 'walk', phase: ph, turn: 1, face: 'neutral', t: ph, autoBlink: false });
      ctx.restore();
      S.label(ctx, `phase ${ph}`, 240 + i * 480, 1066, 22, {});
    });
  };
})();
