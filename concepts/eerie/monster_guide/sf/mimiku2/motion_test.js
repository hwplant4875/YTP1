/* motion_test.js : Mimiku v2 motion test in the SF3 dungeon room (about 6.2 s).
 * dormant chest breathes -> lid cracks, eyes dart, fingers tap the lip one at a time -> unfolds in stages (one leg
 * feels for the floor, then the other, palms push, the chest rises with an overshoot) -> stands, blinks -> walks left
 * -> crouches, jumps (apex stays in frame) -> lands in a deep squash mid-pool -> bounces back up, happy.
 * The camera starts pushed in on the chest and pulls out as it stands up.
 *   node render_seq.mjs core/lib_core.js,dungeon/dungeon.js,mimiku2/mimiku2.js,mimiku2/motion_test.js <out.mp4> 6.2 30
 *   (single frames: node render_sf.mjs <same scripts> <out.png> <t>)                                                  */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W, E = S.ease;
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const io = k => E.easeInOutCubic(clamp(k)), oc = k => E.easeOutCubic(clamp(k));
  const yaw = -30, s = 0.78, X0 = 1010, SPOT = 900, STRIDE = 0.75;
  // T: wake (lid cracks) .8, peek hold to 1.5, staged unfold to 2.62, stand, walk, jump, happy tail
  const T = {
    wake: 0.8, peek1: 1.15, peekEnd: 1.5, leg1: 1.95, push: 2.26, stand: 2.66,
    walk0: 3.0, walkDur: 0.82, steps: 1.25, jump0: 4.4, jumpDur: 1.15, end: 6.2,
  };
  const F = M.yawFrame(yaw);
  // camera: pushed in on the chest (centred on the spotlight pool where it wakes), pulls out as it rises, then out
  // again and up for the jump so the raised hands and the tongue tip never leave the frame
  const CK = [[0, 1.95, 980, 700, 0], [0.6, 1.95, 980, 700, 0], [2.5, 1.35, 930, 640, 0], [3.6, 1.3, 870, 630, 0], [4.5, 1.08, 820, 520, -110], [6.2, 1.08, 800, 520, -110]];
  const camAt = t => {
    let i = 1; while (i < CK.length - 1 && t > CK[i][0]) i++;
    const a = CK[i - 1], b = CK[i], k = io((t - a[0]) / (b[0] - a[0]));
    return { zoom: a[1] + (b[1] - a[1]) * k, fx: a[2] + (b[2] - a[2]) * k, fy: a[3] + (b[3] - a[3]) * k, y: a[4] + (b[4] - a[4]) * k };
  };

  function shot(t) {
    let x = X0, o;
    const walkEnd = T.walk0 + T.walkDur * T.steps;
    const advPx = F.ground(0, M.walkPose(0, { yaw, stride: STRIDE }).advance)[0];          // screen px per cycle at s = 1
    if (t < T.wake) {
      // dormant: breathing (teeth + glints in the seam), one hungry little jolt
      const jolt = Math.exp(-((t - 0.5) ** 2) / 0.004);
      o = M.merge(M.pose('dormant', 0, yaw), { breath: 0.35 + 0.35 * Math.sin(t * 7), tilt: 4 * jolt * Math.sin(t * 60), hip: [0, -0.04 * W * jolt] });
    } else if (t < T.peekEnd) {
      // the lid cracks, then it holds there: eyes dart, and the fingers on the lip tap one at a time
      const u = 0.18 * oc((t - T.wake) / 0.3);
      o = M.pose('unfold', u, yaw);
      const tap = (i, sd) => {                                            // one finger lifts at a time, index -> pinky
        const ph = ((t - T.peek1) * 3.1 + (sd > 0 ? 0.5 : 0)) % 1, slot = Math.floor(ph * 4);
        const k = Math.sin(Math.PI * clamp((ph * 4) % 1)) ** 1.6;
        return 0.62 - (slot === i ? 0.42 * k : 0);
      };
      const darts = Math.sin(t * 7.5) > 0 ? -0.8 : 0.55;
      o = M.merge(o, {
        look: { x: t > T.peek1 ? darts : -0.8, y: 0.3 }, eye: { open: 0.9 },
        arms: t > T.peek1 ? {
          L: { fingers: [0, 1, 2, 3].map(i => tap(i, -1)) },
          R: { fingers: [0, 1, 2, 3].map(i => tap(i, 1)) },
        } : {},
      });
    } else if (t < T.stand) {
      // staged unfold: the near leg feels for the floor, then the far one, then the palms push and the chest rises
      let u;
      if (t < T.leg1) u = 0.18 + 0.22 * io((t - T.peekEnd) / (T.leg1 - T.peekEnd));
      else if (t < T.push) u = 0.40 + 0.18 * io((t - T.leg1) / (T.push - T.leg1));
      else u = 0.58 + 0.42 * io((t - T.push) / (T.stand - T.push));
      o = M.pose('unfold', u, yaw);
      if (t < T.leg1) {                                                   // the far leg is still folded inside
        const g = oc((t - T.peekEnd) / 0.3);
        o = M.merge(o, { legs: { L: { grow: 0.1 + 0.25 * g, kneeOut: 1.2 }, R: { toe: 0.25 * (1 - g) } }, tilt: -5 * g, look: { x: 0.2, y: 0.6 } });
      } else if (t < T.push) {
        const g = oc((t - T.leg1) / (T.push - T.leg1));
        o = M.merge(o, { legs: { L: { grow: 0.35 + 0.65 * g } }, expr: 'effort', look: { x: -0.2, y: 0.5 } });
      } else o = M.merge(o, { expr: t < T.push + 0.18 ? 'effort' : 'neutral' });
    } else if (t < walkEnd) {
      const over = Math.exp(-(t - T.stand) * 6) * Math.sin((t - T.stand) * 15);   // the rise overshoots and settles
      const st = M.merge(M.pose('stand', 1, yaw), {
        hip: [0, -1.8 * W - 0.075 * W * over], lidOpen: 0.75 + 0.1 * over,
        blink: S.blinkAt(t + 0.9, 3, 0.8), look: { x: 0.3, y: 0.05 },
      });
      if (t < T.walk0) o = st;
      else {
        const ph = (t - T.walk0) / T.walkDur, w = M.walkPose(ph, { yaw, t, stride: STRIDE });
        o = M.lerpPose(st, w, io((t - T.walk0) / 0.18));
        o.expr = 'neutral';
        x = X0 + advPx * s * ph;
      }
    } else {
      const xw = X0 + advPx * s * T.steps;
      if (t < T.jump0) {                                                 // settle from the walk into the stand
        const w = M.walkPose(T.steps, { yaw, t, stride: STRIDE }), st = M.pose('stand', 1, yaw);
        o = M.lerpPose(w, st, io((t - walkEnd) / (T.jump0 - walkEnd)));
        x = xw;
      } else {
        const k = (t - T.jump0) / T.jumpDur;
        const j = M.jumpPose(Math.min(k, 1), { yaw, dist: 1.25, height: 0.75 });
        o = j; x = xw + j.dx * s;
        if (k >= 1) {                                                     // after the landing: happy little wiggle
          const kk = (t - T.jump0 - T.jumpDur);
          x = xw + M.jumpPose(1, { yaw, dist: 1.25, height: 0.75 }).dx * s;
          o = M.merge(M.pose('stand', 1, yaw), { expr: kk < 0.4 ? 'happy' : 'neutral', tongue: { swing: 0.25 * Math.sin(kk * 14) * Math.exp(-kk * 3), curl: 0.3 }, lidOpen: 0.9 + 0.08 * Math.sin(kk * 16) * Math.exp(-kk * 4), blink: S.blinkAt(t, 5, 0.8) });
        }
      }
    }
    return { x, o: Object.assign(o, { t, shadow: 'ground' }) };
  }
  window.MIMIKU2_MOTION_SHOT = shot;

  window.draw = t => {
    const ctx = c.getContext('2d'), D = window.DUNGEON;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    const cam = camAt(t);
    const spot = { x: SPOT, floorY: 620, alpha: 0.5, rx: 340, ry: 70, t };
    const o = { spot, cam, post: false, fgChain: false };
    const info = D.roomBack(ctx, t, o);
    const { x, o: pose } = shot(t);
    ctx.save(); D.fitDesign(ctx); D.cam(ctx, cam, 1);
    D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', motes: 0 }));          // the cone behind the character
    M.draw(ctx, x, info.contactY + 18, s, pose);
    D.spotlight(ctx, Object.assign({}, spot, { part: 'beam', beam: 0, motes: 22, seed: 43 }));   // dust in front
    ctx.restore();
    D.roomFront(ctx, t, Object.assign({}, o, { spot: false, fgChain: true }));
    D.post(ctx, t, { vignette: 0.62, vigX: 900, vigY: 500 });
  };
})();
