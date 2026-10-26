(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    const L = [
      { face: 'neutral' }, { face: 'surprised', antT: 0.12 }, { face: 'annoyed' }, { face: 'pleased' }, { face: 'neutral', turn: 1 },
      { face: 'off', offK: 1 }, { face: 'eerie', eerieSmile: true, t: 4 }, { face: 'neutral', mouth: 'wide' }, { face: 'neutral', mouth: 'u' }, { face: 'neutral', blink: 0.4 },
    ];
    L.forEach((o, i) => {
      const x = 200 + (i % 5) * 380, y = 470 + Math.floor(i / 5) * 520;
      HL.drawHead(ctx, x, y, 2.4, Object.assign({ t: 0.4, autoBlink: false, bloom: 0.4 }, o));
    });
  };
})();
