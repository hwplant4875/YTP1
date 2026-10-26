// knight/test_walk4.js : the four walk keys (contact / down / passing / up) for all three types, side by side.
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), K = window.KNIGHT, S = window.SFX;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#212C33'; ctx.fillRect(0, 0, cv.width, cv.height);
    const ph = window.TEST_PH || [0, 0.125, 0.25, 0.375];
    ['hammer', 'spear', 'shield'].forEach((type, r) => {
      const gy = 400 + r * 440;
      ctx.fillStyle = 'rgba(255,255,255,0.15)'; ctx.fillRect(0, gy, cv.width, 2);
      ph.forEach((p, i) => {
        K.draw(ctx, 200 + i * 220, gy, 0.74, { type, pose: 'walk', phase: p, t: 0 });
        S.label(ctx, String(p), 200 + i * 220, gy + 20, 14, { color: '#ccc' });
      });
      ph.forEach((p, i) => K.draw(ctx, 1100 + i * 200 + p * K.stride(type) * 0.74, gy, 0.74, { type, pose: 'walk', phase: p, t: 0, facing: 1 }));
    });
  };
})();
