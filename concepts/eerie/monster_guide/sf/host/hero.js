// host/hero.js : HELEN hero still in the torch-lit corridor (three-quarter, clipboard, deadpan).
// SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,host/helen.js,host/hero.js out.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), S = window.SFX, D = window.DUNGEON, HL = window.HELEN;
  window.draw = t => {
    const ctx = cv.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, cv.width, cv.height);
    const T = 0.6 + (t || 0);
    // weight on the far leg (hip out), remote fist on the near hip, head tipped toward the clipboard
    const POSE = {
      pose: 'idle-hip', face: 'neutral', turn: 1, t: T, autoBlink: false, look: { x: 0.55, y: 0.05 }, weight: 1, headTilt: 7,
      rim: { color: '#FFD3A0', alpha: 0.6, dir: [-1, -0.45], width: 2.6 }, bloom: 0.75, spill: 0.55,
    };
    const hx = 700, gy = 1430, s = 2.4; // cut mid-skirt (~1.4 H above the ground), ~220 px of headroom over the rods
    D.corridor(ctx, T, {
      cam: { zoom: 1.12, fx: 1100, fy: 520, x: 40 },
      vigX: 820, vigY: 520,
      actors: (g, info) => {
        // her screen throws a little mint light on the wall around her head
        const sv = HL.solve(hx, gy, s, POSE);
        D.lightPool(g, sv.screen.x + 20, sv.screen.y + 30, 520, 0, { color: '#3FC9B5', alpha: 0.2, steady: true, hot: 0 });
        HL.draw(g, hx, gy, s, POSE);
      },
    });
  };
})();
