/* thumbA.js : thumbnail A "RULE 1" (plan v1 7 + v2 G): the frame-0 state pushed in. One subject (the lone chest, ~52 %
 * of the frame height), one text block ("RULE" white + "1" in the gold accent of the glints), no arrow, no logo,
 * bottom-right kept clear for the duration badge, the text never touches the chest. The two gold glints in the lid
 * crack are the only warm light besides the lock; the chain runs to its iron floor ring.
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,comp/frame0.js,comp/thumbA.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, CK = window.COMP;
  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d'), F = window.FRAME0;
    const X = 1130;                                     // chest centre (design px): the text owns the top-left
    const cam = { zoom: 2.55, fx: X, fy: 560, x: 60, y: -70 };
    CK.room(ctx, t, {
      cam, motes: 12,
      spot: { x: X, alpha: 0.74, rx: 250, ry: 60, topW: 150, topY: -60 },
      props: { poster: false, board: false, plate: false, scratches: false, webs: false },
      floorProps: { bones: false, floorScratch: false },
      skulls: false,
      fgChain: false,
      actors: (g, info) => {
        F.chest(g, X, info.contactY + 10, F.s, t, {
          breath: 0.26, glint: 1, glintR: 8, ring: [0.74 * 180, 0.07 * 180],
          light: { key: '#FFE2B0', keyA: 0.4, keyD: 0.03 * 180, keyDir: [-0.5, -1], rim: '#8FA8D8', rimA: 0.3, rimD: 0.02 * 180, rimDir: [1, -0.1] },
        });
      },
      post: { vignette: 0.8, vigX: 1060, vigY: 600 },
    });
    // ---------- screen space (canvas px; the render is 1920x1080)
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const k = c.width / 1920;
    ctx.scale(k, k);
    // "RULE 1": Anton, cap height ~190 px -> font size ~ 262; "1" carries the gold accent
    const fs = 262, x0 = 60, base = 80 + 190;
    const w1 = CK.outlineText(ctx, 'RULE ', x0, base, { size: fs, stroke: 26, track: 4 });
    const w2 = CK.outlineText(ctx, '1', x0 + w1, base, { size: fs, stroke: 26, track: 4, color: '#FFC83D' });
  };
})();
