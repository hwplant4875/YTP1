// knight/test_walk.js : walk cycle motion test (three types walking in place + moving).
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), K = window.KNIGHT;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#1A2329'; ctx.fillRect(0, 0, cv.width, cv.height);
    const gy = 1000, cyc = 1.1; // seconds per walk cycle
    ['hammer', 'spear', 'shield'].forEach((ty, i) => {
      const ph = t / cyc + i * 0.21;
      const x = 1700 - ((t / cyc) * K.stride(ty) * 0.9 + i * 520) % 1700;
      K.draw(ctx, x, gy, 0.9, { type: ty, pose: 'walk', phase: ph, t, facing: -1 });
      // ground ticks so foot sliding is visible
    });
    ctx.fillStyle = 'rgba(255,255,255,0.15)'; for (let x = 0; x < cv.width; x += 60) ctx.fillRect(x, gy, 2, 12);
  };
})();
