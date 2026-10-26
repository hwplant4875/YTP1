// host/test_motion.js : motion test. Walk in, ease into idle (antenna kick), static wipe to pleased,
// remote-at-head -> Rule slide while talking, stamp APPROVED. 5.4 s.
// node render_seq.mjs core/lib_core.js,host/helen.js,host/test_motion.js out.mp4 5.4 30
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  const BL = 0.33; // pose blend length (10 frames at 30 fps)
  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329' });
    const gy = 980, s = 1.5, walkEnd = 2.0;
    const stride = HL.STRIDE * HL.H * s * 2; // px per walk cycle at turn 1
    const xEnd = 300 + stride * walkEnd;
    let o = { t, turn: 1, face: 'neutral' }, x = xEnd;
    if (t < walkEnd) { o.pose = 'walk'; o.phase = t % 1; x = 300 + stride * t; }
    else {
      o.pose = 'idle-clipboard'; o.antT = t - walkEnd;
      if (t < walkEnd + BL) { o.from = { pose: 'walk', phase: walkEnd % 1 }; o.blend = (t - walkEnd) / BL; }
    }
    if (t >= 2.5) { o.face = 'pleased'; const w = HL.wipeAt(t, 2.5); if (w != null) { o.prevFace = 'neutral'; o.wipe = w; } o.antT = t - 2.5; }
    if (t >= 3.0) {
      o.pose = 'remote-at-head'; o.face = t < 3.35 ? 'pleased' : 'slide'; o.slide = { n: 10, text: 'When they knock, open wide.' };
      if (t < 3.0 + BL) { o.from = { pose: 'idle-clipboard' }; o.blend = (t - 3.0) / BL; }
      const w = HL.wipeAt(t, 3.35); if (w != null) { o.prevFace = 'pleased'; o.wipe = w; }
      if (t >= 3.35) { o.antT = t - 3.35; o.mouth = ['none', 'o', 'wide', 'u', '~', 'none'][Math.floor(t * 8) % 6]; }
    }
    if (t >= 4.1) {
      o.pose = 'stamp'; o.face = 'pleased'; o.mouth = null; o.slide = null;
      if (t < 4.1 + BL) { o.from = { pose: 'remote-at-head' }; o.blend = (t - 4.1) / BL; o.stampK = 0; }
      else o.stampK = t < 4.6 ? (t - 4.43) / 0.17 : Math.max(0, 1 - (t - 4.7) * 2.5);
      o.stampMark = t >= 4.6; if (t >= 4.6) o.antT = t - 4.6;
    }
    HL.draw(ctx, x, gy, s, o);
    S.label(ctx, `t ${t.toFixed(2)}  ${o.pose}${o.from ? ' <- ' + o.from.pose + ' ' + o.blend.toFixed(2) : ''}  ${o.face}${o.wipe != null ? ' wipe ' + o.wipe.toFixed(2) : ''}`, 40, 40, 22, { align: 'left' });
  };
})();
