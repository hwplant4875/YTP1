(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, cv.width, cv.height, { bg: '#1A2329', title: 'dir = -1 (mirrored) + rim' });
    const gy = 1000, s = 1.5;
    HL.draw(ctx, 250, gy, s, { dir: -1, turn: 1, pose: 'idle-clipboard', face: 'neutral', t: 0.4, rim: true });
    HL.draw(ctx, 700, gy, s, { dir: -1, turn: 1, pose: 'remote-at-head', face: 'slide', slide: { n: 4, text: 'If you are charmed to sleep, nap.' }, t: 0.4, rim: true });
    HL.draw(ctx, 1150, gy, s, { dir: -1, pose: 'present-point', face: 'number', number: '7°', t: 0.4 });
    HL.draw(ctx, 1650, gy, s, { dir: -1, turn: 0.6, pose: 'stamp', face: 'annoyed', stampText: 'DENIED', stampK: 0.1, stampMark: true, t: 0.4 });
  };
})();
