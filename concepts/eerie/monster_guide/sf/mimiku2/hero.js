/* hero.js : Mimiku v2 hero mood shot in the SF3 dungeon room, under the spotlight, three-quarter view.
 * node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,mimiku2/mimiku2.js,mimiku2/hero.js <out.png>   (SMALL=1 for the 168 check)
 * Uses DUNGEON.room exactly like room.js (spot x 860, contact line 620) and puts Mimiku on the pool via actors. */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W;
  // the hero pose: 3/4 toward screen-left, a little hunched, one too-long hand up in a shy little wave by its face,
  // the other hanging past the knee; knock-kneed; tongue to the knees; smitten-happy eyes at the camera
  window.MIMIKU2_HERO_POSE = (t = 0) => {
    const yaw = -32, F = M.yawFrame(yaw), s0 = M.pose('stand', 1, yaw);
    const hip = [0.02 * W, -1.7 * W];
    return M.merge(s0, {
      yaw, hip, pitch: 12, tilt: -6, lidOpen: 0.86, expr: 'neutral', blush: 1.0, eye: { h: 0.78, irisScale: 0.7, pupilScale: 1.1, highlight2: true }, t,
      legs: {
        L: { foot: [F.ground(-0.36 * W, 0.12 * W)[0], -M.DIM.ankle], kneeOut: -0.45, toe: 0 },
        R: { foot: [F.ground(0.34 * W, -0.1 * W)[0], -M.DIM.ankle], kneeOut: -0.35, toe: 0 },
      },
      arms: {
        // near (its right, screen-right in this yaw) hand: hangs long, fingers curling
        R: { hand: [hip[0] + 0.98 * W, hip[1] + 0.52 * W], handAng: Math.PI / 2 - 0.05, curl: 0.55, spread: 0.45, curlDir: -1, elbowUp: 0.9 },
        // far hand up by the face: the shy wave (fingers splayed, a bit too many knuckles)
        L: { hand: [hip[0] - 0.92 * W, hip[1] - 1.05 * W], handAng: -Math.PI / 2 - 0.35, curl: 0.18, spread: 1, curlDir: 1, elbowUp: 0.2 },
      },
      tongue: { len: 1.3, curl: 0.5, swing: 0.02, wave: 0.28, phase: 1.1, width: 0.85 },
      chain: { sway: 0.06 }, look: { x: 0.25, y: 0.15 },
      fx: { sparkle: 0 },
    });
  };
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    const cam = { zoom: 1.55, fx: 860, fy: 540, y: -178 };         // push in: Mimiku fills the frame height (reads at 168 px)
    DUNGEON.room(ctx, t, {
      spot: { x: 860, floorY: 620, alpha: 0.42 },
      cam,
      actors: (g, info) => {
        g.save(); DUNGEON.cam(g, cam, 1);
        M.draw(g, 860, info.contactY + 22, 1, Object.assign(window.MIMIKU2_HERO_POSE(t), { shadow: 'ground' }));
        g.restore();
      },
    });
  };
})();
