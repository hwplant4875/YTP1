/* motion_test.js : Mimiku v2 motion test in the SF3 dungeon room (about 5.4 s).
 * dormant chest breathes -> lid cracks, eyes dart, fingers creep -> unfolds (legs sprout, palms push, chest lifts)
 * -> stands, blinks -> walks three steps left -> crouches, jumps -> lands in a deep squash (knuckles on the floor)
 * -> bounces back up, happy.
 *   node render_seq.mjs core/lib_core.js,dungeon/dungeon.js,mimiku2/mimiku2.js,mimiku2/motion_test.js <out.mp4> 5.4 30
 *   (single frames: node render_sf.mjs <same scripts> <out.png> <t>)                                                  */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W, E = S.ease;
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const io = k => E.easeInOutCubic(clamp(k)), oc = k => E.easeOutCubic(clamp(k));
  const yaw = -30, s = 0.78, X0 = 1085;
  const cam = { zoom: 1.15, fx: 860, fy: 640 };                         // a gentle push-in, the floor line stays put
  const T = { wake: 0.75, peekEnd: 1.35, stand: 2.3, walk0: 2.62, walkDur: 0.8, steps: 1.5, jump0: 3.95, jumpDur: 1.1, end: 5.4 };
  const F = M.yawFrame(yaw);

  function shot(t) {
    let x = X0, o;
    const walkEnd = T.walk0 + T.walkDur * T.steps;
    const advPx = F.ground(0, M.walkPose(0, { yaw }).advance)[0];          // screen px per cycle at s = 1
    if (t < T.wake) {
      // dormant: breathing (teeth + glints in the seam), one hungry little jolt
      const jolt = Math.exp(-((t - 0.5) ** 2) / 0.004);
      o = M.merge(M.pose('dormant', 0, yaw), { breath: 0.35 + 0.35 * Math.sin(t * 7), tilt: 4 * jolt * Math.sin(t * 60), hip: [0, -0.04 * W * jolt] });
    } else if (t < T.stand) {
      // lid cracks + peek (hold, eyes dart), then the push-up and rise
      const u = t < T.peekEnd ? 0.18 * oc((t - T.wake) / 0.35) : 0.18 + 0.82 * io((t - T.peekEnd) / (T.stand - T.peekEnd));
      o = M.pose('unfold', u, yaw);
      if (t < T.peekEnd) o = M.merge(o, { look: { x: Math.sin(t * 9) > 0 ? -0.8 : 0.6, y: 0.3 }, eye: { open: 0.9 } });
    } else if (t < walkEnd) {
      const st = M.merge(M.pose('stand', 1, yaw), { blink: S.blinkAt(t + 0.9, 3, 0.8), look: { x: 0.3, y: 0.05 } });
      if (t < T.walk0) o = st;
      else {
        const ph = (t - T.walk0) / T.walkDur, w = M.walkPose(ph, { yaw, t });
        o = M.lerpPose(st, w, io((t - T.walk0) / 0.18));
        o.expr = 'neutral';
        x = X0 + advPx * s * ph;
      }
    } else {
      const xw = X0 + advPx * s * T.steps;
      if (t < T.jump0) {                                                 // settle from the walk into the stand
        const w = M.walkPose(T.steps, { yaw, t }), st = M.pose('stand', 1, yaw);
        o = M.lerpPose(w, st, io((t - walkEnd) / (T.jump0 - walkEnd)));
        x = xw;
      } else {
        const k = (t - T.jump0) / T.jumpDur;
        const j = M.jumpPose(Math.min(k, 1), { yaw, dist: 1.7 });
        o = j; x = xw + j.dx * s;
        if (k >= 1) {                                                     // after the landing: happy little wiggle
          const kk = (t - T.jump0 - T.jumpDur);
          o = M.merge(M.pose('stand', 1, yaw), { expr: kk < 0.35 ? 'happy' : 'neutral', tongue: { swing: 0.25 * Math.sin(kk * 14) * Math.exp(-kk * 3), curl: 0.3 }, lidOpen: 0.9 + 0.08 * Math.sin(kk * 16) * Math.exp(-kk * 4), blink: S.blinkAt(t, 5, 0.8) });
        }
      }
    }
    return { x, o: Object.assign(o, { t, shadow: 'ground' }) };
  }
  window.MIMIKU2_MOTION_SHOT = shot;

  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    DUNGEON.room(ctx, t, {
      spot: { x: 860, floorY: 620, alpha: 0.4 }, cam,
      actors: (g, info) => {
        const { x, o } = shot(t);
        g.save(); DUNGEON.cam(g, cam, 1);
        M.draw(g, x, info.contactY + 18, s, o);
        g.restore();
      },
    });
  };
})();
