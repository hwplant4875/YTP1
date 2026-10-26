/* sheet.js : Mimiku v2 model sheet (states). Loads after lib_core.js and mimiku2.js.
 * node render_sf.mjs core/lib_core.js,mimiku2/mimiku2.js,mimiku2/sheet_common.js,mimiku2/sheet.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W;
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const SH = window.M2SHEET;
    SH.bg(ctx, 'MIMIKU', 'v2 · new hire #001 · treasure-chest mimic', 'model sheet · states · all poses same scale · W = chest width');
    const s = 0.7, gy = 905, U = W * s;
    SH.floor(ctx, gy);
    SH.heightGuides(ctx, gy, U, [[2.4, 'knight 2.4 W'], [3.1, 'Mimiku standing 3.1 W']], 100, 1880);
    SH.scaleBar(ctx, 52, gy, U, 4.5);
    const X = { dormant: 160, peek: 432, unfold: 718, stand: 1036, yawn: 1318, knight: 1615 };

    M.draw(ctx, X.dormant, gy, s, { state: 'dormant', yaw: -14, breath: 0.6, t: 0.4 });
    M.draw(ctx, X.peek, gy, s, { state: 'peek', yaw: -14, look: { x: -0.7, y: 0.25 }, t: 0.4 });
    M.draw(ctx, X.unfold, gy, s, { state: 'unfold', unfold: 0.47, yaw: -10, t: 0.2 });
    M.draw(ctx, X.stand, gy, s, { state: 'stand', yaw: -14, t: 0.8, look: { x: -0.25, y: 0.1 }, chain: { sway: 0.06 } });
    // yawn: big stretch on tiptoe, lid wide, tongue curls up, eyes squeezed
    const hipY = -1.98 * W;
    M.draw(ctx, X.yawn, gy, s, {
      state: 'stand', yaw: 8, hip: [0, hipY], pitch: -5, lidOpen: 1.04, expr: 'yawn',
      legs: { L: { foot: [-0.27 * W, -M.DIM.ankle - 0.06 * W], toe: 0.6, kneeOut: -0.3 }, R: { foot: [0.29 * W, -M.DIM.ankle - 0.06 * W], toe: 0.6, kneeOut: -0.3 } },
      arms: {
        L: { hand: [-0.42 * W, hipY - 1.82 * W], handAng: -Math.PI / 2 - 0.35, curl: 0.15, spread: 0.95, curlDir: 1 },
        R: { hand: [0.55 * W, hipY - 1.78 * W], handAng: -Math.PI / 2 + 0.45, curl: 0.2, spread: 0.9, curlDir: -1 },
      },
      tongue: { len: 0.95, ang: Math.PI / 2 - 0.1, curl: -1.25, wave: 0, swing: 0 },
      chain: { sway: 0.03 }, t: 0.3,
    });
    // pounce: airborne over a placeholder knight, diving down-left
    M.knight(ctx, X.knight, gy, s, {});
    const px = X.knight + 0.12 * U;
    M.draw(ctx, px, gy, s, {
      state: 'stand', yaw: -24, hip: [-0.05 * W, -2.72 * W], pitch: 22, tilt: -12, lidOpen: 1.12, expr: 'pounce',
      legs: { L: { foot: [0.86 * W, -3.66 * W], toe: 1.2, kneeOut: 0.4 }, R: { foot: [1.16 * W, -3.16 * W], toe: 1.2, kneeOut: 0.5 } },
      arms: {
        L: { hand: [-1.25 * W, -2.4 * W], handAng: Math.PI * 0.72, curl: 0.5, spread: 1, curlDir: -1, elbowUp: 1 },
        R: { hand: [0.5 * W, -1.95 * W], handAng: Math.PI * 0.4, curl: 0.5, spread: 1, curlDir: 1, elbowUp: 1 },
      },
      tongue: { len: 1.05, ang: -0.7, curl: 1.1, wave: 0.7, phase: 2.2, swing: 0 },
      chain: { swing: -2.6, sag: 0.25, sway: 0.25, t: 0.5 }, t: 0.5,
    });

    // detail insets: the cute layer vs the grotesque layer
    const iy = 122, ih = 250, iw = 262, ix = [104, 386, 668, 950];
    SH.inset(ctx, ix[0], iy, iw, ih, 'CUTE · THE FACE', 'glow eyes · blush · flat wood, one shade', g => {
      g.fillStyle = '#2A2D36'; g.fillRect(ix[0], iy, iw, ih);
      SH.focus(g, ix[0] + iw / 2, iy + ih * 0.52, 1.55, { state: 'stand', yaw: 0, look: { x: 0.15, y: 0.1 }, parts: { arms: false, legs: false } }, a => a.mouth);
    });
    SH.inset(ctx, ix[1], iy, iw, ih, 'GROTESQUE · HAND', '5 long fingers · knuckles · tendons · nails', g => {
      g.fillStyle = '#2A2D36'; g.fillRect(ix[1], iy, iw, ih);
      SH.focus(g, ix[1] + iw * 0.47, iy + ih * 0.3, 2.3, { state: 'stand', yaw: 0, arms: { R: { curl: 0.42, spread: 0.6 } } }, a => a.hands.R);
    });
    SH.inset(ctx, ix[2], iy, iw, ih, 'GROTESQUE · KNEE', 'knobby kneecap · wrinkles · veins', g => {
      g.fillStyle = '#2A2D36'; g.fillRect(ix[2], iy, iw, ih);
      SH.focus(g, ix[2] + iw * 0.5, iy + ih * 0.5, 2.3, { state: 'stand', yaw: -60, parts: { tongue: false } }, a => a.knees.R);
    });
    SH.inset(ctx, ix[3], iy, iw, ih, 'GROTESQUE · TEETH', '19 + 17 long uneven teeth · crooked', g => {
      g.fillStyle = '#2A2D36'; g.fillRect(ix[3], iy, iw, ih);
      SH.focus(g, ix[3] + iw * 0.5, iy + ih * 0.5, 2.2, { state: 'stand', yaw: 0, expr: 'pounce', lidOpen: 1.0, parts: { arms: false, legs: false, tongue: false } }, a => a.mouth);
    });

    SH.inset(ctx, 1232, iy, 648, ih, 'TURNAROUND · ONE RIG', 'yaw 0 · -35 · -65 · +35 · same IK, same scale', g => {
      g.fillStyle = '#2A2D36'; g.fillRect(1232, iy, 648, ih);
      const gy2 = iy + ih - 16, s2 = 0.33;
      g.fillStyle = 'rgba(237,231,242,0.12)'; g.fillRect(1250, gy2, 612, 2);
      [[0, 1372], [-35, 1515], [-65, 1650], [35, 1790]].forEach(([yw, x2]) => M.draw(g, x2, gy2, s2, { state: 'stand', yaw: yw, t: 0.8, chain: { sway: 0.04 } }));
    });
    const L = [[X.dormant, '1', 'DORMANT', 'shut · crooked · chain lies straight'], [X.peek, '2', 'PEEK', 'lid cracked · eyes glow · fingers creep'],
      [X.unfold, '3', 'UNFOLD', 'legs sprout · palms push · chest lifts'], [X.stand, '4', 'STANDING IDLE', 'tongue to the knees · arms dangle'],
      [X.yawn, '5', 'YAWN', 'lid wide · tongue curls · eyes squeezed'], [X.knight + 0.15 * U, '6', 'POUNCE', 'airborne · arms spread · teeth bared']];
    L.forEach(([x, n, a, b]) => SH.stateLabel(ctx, x, gy + 50, n, a, b));
    SH.post(ctx);
  };
})();
