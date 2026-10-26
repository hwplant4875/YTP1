// knight/test_peek.js : peek totem + horror + 404 check.
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, K = window.KNIGHT;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#1A2329'; ctx.fillRect(0, 0, cv.width, cv.height);
    const gy = 960, ex = 420;
    // dark doorway to the right of the edge, wall to the left
    ctx.fillStyle = '#07090B'; ctx.fillRect(ex, 200, 500, gy - 200);
    ctx.fillStyle = '#2E3A42'; ctx.fillRect(ex - 260, 160, 260, gy - 160);
    const clip = c => c.rect(ex, 0, 2000, 2000);
    const k = 0.5 + 0.5 * Math.sin((t || 0) * 3);
    K.draw(ctx, ex, gy, 1, { type: 'hammer', pose: 'peek', peekH: 80, peekOut: 50, tilt: 18, clip, part: 'helm', nod: 0 });
    K.draw(ctx, ex, gy, 1, { type: 'shield', pose: 'peek', peekH: 225, peekOut: 58, tilt: 24, clip, part: 'helm' });
    K.draw(ctx, ex, gy, 1, { type: 'spear', pose: 'peek', peekH: 360, peekOut: 44, tilt: 14, clip, part: 'helm' });
    K.draw(ctx, ex, gy, 1, { type: 'hammer', pose: 'peek', peekH: 80, handH: 150, part: 'hand' });
    K.draw(ctx, ex, gy, 1, { type: 'shield', pose: 'peek', peekH: 225, handH: 290, part: 'hand' });
    K.draw(ctx, ex, gy, 1, { type: 'spear', pose: 'peek', peekH: 360, handH: 420, part: 'hand' });
    K.draw(ctx, 1100, gy, 1, { type: 'hammer', variant: 'horror', pose: 'idle', t });
    K.draw(ctx, 1450, gy, 1, { type: 'shield', variant: 'horror', pose: 'walk', phase: 0.2, t });
    K.draw(ctx, 1760, gy, 1, { type: 'spear', variant: 'k404', pose: 'notebook', t });
  };
})();
