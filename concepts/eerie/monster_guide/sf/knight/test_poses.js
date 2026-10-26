// knight/test_poses.js : every pose for every type in a grid (rig QA).
// node render_sf.mjs core/lib_core.js,knight/knight.js,knight/test_poses.js out.png [t] 1920 1500
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, K = window.KNIGHT;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#1A2329'; ctx.fillRect(0, 0, cv.width, cv.height);
    const types = ['hammer', 'spear', 'shield'];
    const poses = window.TEST_POSES || [['walk', { phase: 0 }], ['walk', { phase: 0.25 }], ['knock', { k: 0.1 }], ['knock', { k: 0.5 }], ['knock', { k: 0.9 }], ['notebook', { variant: 'k404' }], ['backaway', { k: 0.3 }], ['nod', { k: 0.5 }]];
    const s = 0.55, colW = cv.width / poses.length, rowH = cv.height / 3;
    types.forEach((ty, r) => {
      const gy = rowH * (r + 1) - 40;
      ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fillRect(0, gy, cv.width, 2);
      poses.forEach(([pose, o], c) => {
        const x = colW * (c + 0.4);
        if (pose === 'knock') {
          const dx = K.chestDX(ty) * s;
          S.roundRect(ctx, x + dx - 90 * s, gy - 150 * s, 180 * s, 150 * s, 20 * s, '#A0866B');
        }
        K.draw(ctx, x, gy, s, Object.assign({ type: ty, pose, t: t || 0 }, o));
      });
    });
  };
})();
