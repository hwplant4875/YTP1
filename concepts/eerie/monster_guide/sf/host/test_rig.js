// quick look: node render_sf.mjs core/lib_core.js,host/helen.js,host/test_rig.js out.png
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329', title: 'HELEN rig test' });
    const gy = 960, s = 1.25;
    const cfg = [
      { x: 170, o: { pose: 'idle-clipboard', face: 'neutral' } },
      { x: 470, o: { pose: 'idle-clipboard', face: 'neutral', turn: 1 } },
      { x: 800, o: { pose: 'remote-at-head', face: 'slide', slide: { n: 10, text: 'When they knock, open wide.' } } },
      { x: 1180, o: { pose: 'present-point', face: 'pleased' } },
      { x: 1470, o: { pose: 'stamp', face: 'pleased', stampK: 0.12, stampMark: true, antT: 0.1 } },
      { x: 1760, o: { pose: 'walk', phase: 0.15, turn: 1, face: 'neutral' } },
    ];
    cfg.forEach(c => HL.draw(ctx, c.x, gy, s, Object.assign({ t: 0.4 }, c.o)));
    ctx.fillStyle = 'rgba(255,255,255,0.2)'; ctx.fillRect(0, gy, cv.width, 1);
  };
})();
