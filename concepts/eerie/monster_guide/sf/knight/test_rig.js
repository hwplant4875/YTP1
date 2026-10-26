// knight/test_rig.js : quick rig check (all types, idle + ready + variants) at s = 1 with the 2.4 W line.
// node render_sf.mjs core/lib_core.js,knight/knight.js,knight/test_rig.js out.png [t]
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, K = window.KNIGHT;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#1A2329'; ctx.fillRect(0, 0, cv.width, cv.height);
    const gy = 960, s = 1;
    ctx.fillStyle = 'rgba(255,255,255,0.15)'; ctx.fillRect(0, gy, cv.width, 2);
    ctx.fillStyle = 'rgba(255,200,80,0.5)'; ctx.fillRect(0, gy - 432 * s, cv.width, 2);
    const Q = (window.TEST_FIGS || [
      [180, { type: 'hammer', pose: 'idle' }],
      [470, { type: 'hammer', pose: 'ready' }],
      [760, { type: 'spear', pose: 'idle' }],
      [990, { type: 'spear', pose: 'ready' }],
      [1300, { type: 'shield', pose: 'idle' }],
      [1600, { type: 'shield', pose: 'ready' }],
      [1820, { type: 'spear', pose: 'idle', variant: 'k404' }],
    ]);
    Q.forEach(([x, o]) => K.draw(ctx, x, gy, s, Object.assign({ t: t || 0 }, o)));
  };
})();
