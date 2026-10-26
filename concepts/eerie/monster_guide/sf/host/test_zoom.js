// close-up check of the rig at large scale. node render_sf.mjs core/lib_core.js,host/helen.js,host/test_zoom.js out.png
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    HL.draw(ctx, 330, 1060, 2.0, { pose: 'idle-clipboard', face: 'neutral', t: 0.4, autoBlink: false });
    HL.draw(ctx, 960, 1060, 2.0, { pose: 'stamp', face: 'pleased', stampK: 0.1, stampMark: true, antT: 0.12, t: 0.4 });
    HL.draw(ctx, 1600, 1060, 2.0, { pose: 'stamp', face: 'pleased', stampK: 1, stampMark: true, t: 0.4 });
  };
})();
