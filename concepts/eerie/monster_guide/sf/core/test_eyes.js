// core/test_eyes.js : eye QA sheet for SFX.eye. Hero scale (bezier smoothness), blink sequence, gaze grid, size ladder,
// expression pairs. node ../render_sf.mjs core/lib_core.js,core/test_eyes.js out.png
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height, S = window.SFX, P = S.PAL, I = P.iris;
  const MUTED = 'rgba(236,230,242,0.6)';
  const cap = (t, x, y, o = {}) => S.label(ctx, t, x, y, 16, Object.assign({ color: MUTED, weight: 700 }, o));
  const head = (t, x, y) => S.label(ctx, t, x, y, 17, { align: 'left', color: 'rgba(236,230,242,0.45)', track: 2 });

  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, W, H, { title: 'SFX.eye · QA', subtitle: 'hero scale · blink · gaze · minimum size · expression pairs' });

    // hero eye, 430 px wide: curves must stay smooth, wing sharp, wrap clean
    head('HERO  w 430', 44, 124);
    S.roundRect(ctx, 40, 136, 700, 420, 22, P.skin);
    const hero = S.eye(ctx, { x: 396, y: 350, w: 430, iris: I.gold, pupil: 'slit', pupilColor: '#2A1206', look: { x: -0.25, y: 0.05 }, mirror: true });
    S.blush(ctx, 390, 500, 340, 0.3);
    S.sparkle(ctx, hero.ix + 120, hero.iy - 150, 16, '#ffffff');

    // blink sequence
    head('BLINK  open 1 → 0', 784, 124);
    S.roundRect(ctx, 780, 136, 1100, 150, 20, P.skin);
    [1, 0.8, 0.6, 0.4, 0.25, 0.14, 0.05].forEach((o, i) => {
      const x = 860 + i * 158;
      S.eye(ctx, { x, y: 206, w: 116, open: o, iris: I.blue });
      cap('open ' + o, x, 302);
    });

    // gaze grid with a pair
    head('GAZE  look x,y ∈ {-1,0,1}', 784, 344);
    S.roundRect(ctx, 780, 356, 1100, 200, 20, P.skin);
    const looks = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, -1]];
    looks.forEach(([lx, ly], i) => {
      const x = 870 + i * 183;
      S.eyePair(ctx, { x, y: 446, w: 60, gap: 0.34, iris: I.green, look: { x: lx, y: ly } });
      cap(`look ${lx},${ly}`, x, 572);
    });

    // size ladder: 45 px is the plan's minimum eye width at 1080p
    head('SIZE LADDER  w 45 / 60 / 90 / 124', 44, 604);
    S.roundRect(ctx, 40, 616, 700, 200, 20, P.skin);
    [[45, 120], [60, 230], [90, 380], [124, 580]].forEach(([w, x]) => {
      S.eye(ctx, { x, y: 716, w, iris: I.violet, look: { x: -0.4, y: 0.1 } });
      cap('w ' + w, x, 834);
    });

    // expression pairs (presets in SFX.EXPR)
    head('SFX.EXPR PAIRS', 784, 604);
    S.roundRect(ctx, 780, 616, 1100, 200, 20, P.skin);
    const ex = [['happy', I.rose], ['nervous', I.gold], ['greedy', I.gold], ['eerie', I.red], ['sad', I.teal], ['dizzy', I.violet]];
    ex.forEach(([name, iris], i) => {
      const x = 870 + i * 183, e = S.EXPR[name];
      const extra = name === 'nervous' || name === 'greedy' ? { pupilColor: name === 'greedy' ? '#fff3c4' : '#2A1206' } : {};
      S.eyePair(ctx, Object.assign({ x, y: 712, w: 60, gap: 0.34, iris }, e, extra));
      if (name === 'happy') { S.blush(ctx, x - 50, 748, 52, 0.4); S.blush(ctx, x + 50, 748, 52, 0.4); }
      if (name === 'nervous') S.sweat(ctx, x + 74, 676, 30, { angle: 0.2 });
      cap(name, x, 834);
    });

    // tilt and mirror, plus a big glow pair on a screen
    head('TILT · MIRROR', 44, 870);
    S.roundRect(ctx, 40, 882, 700, 170, 20, P.skin);
    [[-0.25, 'tilt -0.25'], [0, 'parent scale(-1,1)'], [0.25, 'tilt +0.25']].forEach(([tl, lb], i) => {
      const x = 160 + i * 230;
      ctx.save();
      if (i === 1) { ctx.translate(2 * x, 0); ctx.scale(-1, 1); } // a rig that flips the whole character
      S.eyePair(ctx, { x, y: 960, w: 74, gap: 0.34, tilt: tl, iris: I.rose, look: { x: i === 1 ? 0.8 : 0, y: 0 } });
      ctx.restore();
      cap(lb, x, 1068);
    });
    head('GLOW  w 120', 784, 870);
    S.roundRect(ctx, 780, 882, 1100, 170, 20, '#070b0f');
    S.eyePair(ctx, { x: 1080, y: 964, w: 120, gap: 0.4, glow: true, glowColor: '#8ff7ff', look: { x: 0.2, y: 0 } });
    S.eyePair(ctx, { x: 1560, y: 964, w: 120, gap: 0.4, glow: true, glowColor: '#ffb04a', closed: 'smile' });
    S.scanlines(ctx, 780, 882, 1100, 170, 4, 0.2);
    S.vignette(ctx, 0.3);
  };
})();
