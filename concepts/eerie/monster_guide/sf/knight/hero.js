// knight/hero.js : the three Guests entering through the torch-lit corridor (SF4 plate), single file out of the
// centre arch toward camera-left. The spear knight in the middle is the 404 knight (scratch + notebook: the
// "find the hidden knight" easter egg).
// SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,knight/knight.js,knight/hero.js knights_hero.png [t]
(function () {
  'use strict';
  const cv = document.getElementById('c'), S = window.SFX, D = window.DUNGEON, K = window.KNIGHT;
  const CYC = 1.25; // seconds per walk cycle
  window.draw = t => {
    t = t || 0;
    const ctx = cv.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, cv.width, cv.height);
    const T = 0.6 + t;
    const cam = { zoom: 1.14, fx: 900, fy: 640, x: 0, y: 10 };
    const rimWarm = { color: '#FFD9A8', alpha: 0.8, dir: [-1, -0.55], width: 3.4 };
    // single file: back (in the arch mouth) -> front (leading, lantern)
    const cast = [
      { type: 'hammer', x: 1215, y: 812, s: 0.66, ph: 0.55, tint: { color: '#141822', amount: 0.3 } },
      { type: 'spear', variant: 'k404', x: 1000, y: 902, s: 0.9, ph: 0.25, tint: { color: '#0A0B10', amount: 0.14 } },
      { type: 'shield', x: 690, y: 976, s: 1.2, ph: 0.0, tint: null },
    ];
    D.corridor(ctx, T, {
      cam, vigY: 600,
      actors: (g, info) => {
        g.save(); D.cam(g, cam, 1);
        // the leading lantern lights the floor ahead of them
        const lead = cast[2];
        D.lightPool(g, lead.x - 70, lead.y + 4, 520, T, { seed: 31, alpha: 0.7, hot: 0.14, squash: 0.26 });
        cast.forEach(k => {
          const ph = k.ph + t / CYC;
          K.draw(g, k.x - t / CYC * K.stride(k.type) * k.s, k.y, k.s, {
            type: k.type, variant: k.variant || 'normal', pose: 'walk', phase: ph, facing: -1, t: T,
            rim: Object.assign({}, rimWarm, { alpha: k.tint ? 0.75 : 0.85 }), tint: k.tint,
            // a light, slightly cool-neutral grade: the plate stays a touch cooler than the warm stone so it separates
            grade: { color: '#E6DED6', amount: 0.4, mode: 'multiply' }, lantern: { glow: 1.6 },
          });
        });
        g.restore();
      },
    });
  };
})();
