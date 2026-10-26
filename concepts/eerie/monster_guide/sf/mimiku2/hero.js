/* hero.js : Mimiku v2 hero mood shot in the SF3 dungeon room, under the spotlight, three-quarter view.
 * node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,mimiku2/mimiku2.js,mimiku2/hero.js <out.png>   (SMALL=1 for the 168 check)
 * Layer order (so the character keeps full-saturation flat fills): room back + floor pool -> spotlight BEAM (no
 * motes) -> cast shadow -> Mimiku -> dust motes only -> foreground chains -> vignette + grain. The beam never veils
 * the character. */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, D = window.DUNGEON, W = M.DIM.W;
  // the hero pose: 3/4 toward screen-left, a little hunched and knock-kneed, the far hand up in a shy little wave by
  // its face, the near (too big, too long) hand dangling OUTSIDE the thigh with the fingers curling; tongue to the
  // knees; a happy-shy look at its new colleague just off screen-left
  window.MIMIKU2_HERO_POSE = (t = 0) => {
    const yaw = -28, F = M.yawFrame(yaw), s0 = M.pose('stand', 1, yaw);
    const hip = [0.02 * W, -1.72 * W];
    return M.merge(s0, {
      yaw, hip, pitch: 12, tilt: -5, lidOpen: 0.98, expr: 'neutral', blush: 1.0, eyeLift: 0.06, teeth: 1.35,
      eye: { h: 0.8, irisScale: 0.72, pupilScale: 1.1, highlight2: true }, t,
      legs: {
        L: { foot: [F.ground(-0.38 * W, 0.12 * W)[0], -M.DIM.ankle], kneeOut: -0.5, toe: 0, splay: 0.5 },
        R: { foot: [F.ground(0.36 * W, -0.1 * W)[0], -M.DIM.ankle], kneeOut: -0.4, toe: 0, splay: 0.75 },
      },
      arms: {
        // near hand: hangs long outside the near thigh, palm in, fingers curling (a little too big: toward the camera)
        R: { hand: [hip[0] + 0.98 * W, hip[1] + 0.62 * W], handAng: Math.PI / 2 - 0.12, curl: 0.34, spread: 0.6, curlDir: -1, elbowUp: 0.9, handScale: 1.3, thumb: 0.5 },
        // far hand up by the face: the shy wave (fingers splayed)
        L: { hand: [hip[0] - 0.95 * W, hip[1] - 1.05 * W], handAng: -Math.PI / 2 - 0.35, curl: 0.16, spread: 1, curlDir: 1, elbowUp: 0.2 },
      },
      tongue: { len: 1.3, curl: 0.45, swing: 0.02, wave: 0.26, phase: 1.1, width: 0.82 },
      chain: { sway: 0.06 }, look: { x: -0.35, y: 0.12 },
      fx: { sparkle: 0 },
    });
  };
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    const cam = { zoom: 1.5, fx: 860, fy: 540, y: -168 };          // push in: Mimiku fills the frame height (reads at 168 px)
    const spot = { x: 860, floorY: 620, alpha: 0.85, rx: 260, ry: 76, topW: 150, topY: -60, beam: 0.5, t };
    const pose = window.MIMIKU2_HERO_POSE(t);
    const o = { spot, cam, post: false, fgChain: false };
    const info = D.roomBack(ctx, t, o);
    const gy = info.contactY + 22;
    ctx.save(); D.fitDesign(ctx); D.cam(ctx, cam, 1);
    D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', motes: 0 }));       // the cone BEHIND the character
    M.castShadow(ctx, 860, gy, 1, pose, { alpha: 0.45, squash: 0.22, skew: 0.62, blur: 9 });
    M.draw(ctx, 860, gy, 1, Object.assign({}, pose, {
      shadow: 'ground',
      // only a crisp warm key edge on the top-left and a cool rim on the right: no veil, no falloff haze
      light: { key: '#FFE2B0', keyA: 0.5, keyD: 0.03 * W, keyDir: [-0.6, -1], rim: '#8FA8D8', rimA: 0.45, rimD: 0.02 * W, rimDir: [1, -0.1] },
    }));
    D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', beam: 0, motes: 22, seed: 43 }));   // dust only, in front
    ctx.restore();
    D.roomFront(ctx, t, Object.assign({}, o, { spot: false, fgChain: true }));
    D.post(ctx, t, { vignette: 0.6, vigX: 880, vigY: 470 });
  };
})();
