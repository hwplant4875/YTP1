/* motion.js : Mimiku v2 motion sheet (walk cycle, 8 frames with onion skins + a jump, 6 frames along its arc).
 * node render_sf.mjs core/lib_core.js,mimiku2/mimiku2.js,mimiku2/sheet_common.js,mimiku2/motion.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W;
  const INK = '#EDE7F2', SUB = 'rgba(237,231,242,0.55)';
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const SH = window.M2SHEET;
    SH.bg(ctx, 'MIMIKU', 'v2 · motion · walk + jump', 'gangly, bouncy, a little too many joints · same rig, same scale (s = 0.45)', { palette: false });

    // ---------------------------------------------------------------- WALK: 8 frames, two steps, faint onion skins
    const s = 0.45, U = W * s, gyW = 560, yaw = 35;
    const sp = 232, x0 = 150;                                    // walks screen-right: frame 1 on the left, rows read left to right
    ctx.fillStyle = 'rgba(237,231,242,0.16)'; ctx.fillRect(60, gyW, 1800, 2);
    S.label(ctx, 'WALK CYCLE', 60, 150, 26, { align: 'left', color: INK, weight: 900, track: 1.5 });
    S.label(ctx, '8 frames · 2 steps · chest bobs DOWN after each contact · tongue + chain lag a beat · arms swing loose from the mouth corners', 60, 180, 15, { align: 'left', color: SUB, weight: 700 });
    const keys = ['contact', 'down', 'pass', 'up', 'contact', 'down', 'pass', 'up'];
    for (let i = 0; i < 8; i++) {
      const ph = i / 8, x = x0 + i * sp;
      // onion skins: the two in-betweens before this frame
      [[-1 / 16, 0.2], [-2 / 16, 0.12]].forEach(([d, a]) => M.draw(ctx, x, gyW, s, Object.assign(M.walkPose(ph + d, { yaw, t: (ph + d) * 1.1 }), { alpha: a, silhouette: '#C7DCF5', shadow: 'none', parts: { chain: false } })));
      M.draw(ctx, x, gyW, s, Object.assign(M.walkPose(ph, { yaw, t: ph * 1.1 }), { shadow: 'ground' }));
      S.label(ctx, `${i + 1}`, x, gyW + 30, 18, { color: INK, weight: 900 });
      S.label(ctx, keys[i], x, gyW + 52, 13.5, { color: SUB, weight: 800 });
    }
    // direction arrow
    ctx.save(); ctx.strokeStyle = 'rgba(255,214,110,0.6)'; ctx.fillStyle = 'rgba(255,214,110,0.6)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(1660, 150); ctx.lineTo(1850, 150); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(1860, 150); ctx.lineTo(1844, 141); ctx.lineTo(1844, 159); ctx.closePath(); ctx.fill(); ctx.restore();
    S.label(ctx, 'walks right · yaw +35', 1755, 172, 13, { color: 'rgba(255,214,110,0.75)', weight: 800 });

    // ---------------------------------------------------------------- JUMP: 6 frames along the arc
    const gyJ = 1010, ks = [0.2, 0.29, 0.55, 0.74, 0.86, 0.95];
    const names = [['anticipate', 'deep crouch · lid shuts'], ['launch', 'legs snap · lid flies open'], ['apex', 'legs tucked · tongue trails'], ['fall', 'tongue flaps up and back'], ['land', 'knees deep · knuckles on floor'], ['recover', 'bounce up · happy']];
    ctx.fillStyle = 'rgba(237,231,242,0.16)'; ctx.fillRect(60, gyJ, 1800, 2);
    S.label(ctx, 'JUMP', 60, 640, 26, { align: 'left', color: INK, weight: 900, track: 1.5 });
    S.label(ctx, 'jumpPose(k) · 6 key frames', 60, 668, 15, { align: 'left', color: SUB, weight: 700 });
    const jx0 = 210, jsp = 300;
    ctx.save(); ctx.strokeStyle = 'rgba(255,214,110,0.6)'; ctx.fillStyle = 'rgba(255,214,110,0.6)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(1660, 640); ctx.lineTo(1850, 640); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(1860, 640); ctx.lineTo(1844, 631); ctx.lineTo(1844, 649); ctx.closePath(); ctx.fill(); ctx.restore();
    S.label(ctx, 'jumps right · 2.2 W far, 1 W high', 1750, 662, 13, { color: 'rgba(255,214,110,0.75)', weight: 800 });
    const P = ks.map((k, i) => { const o = M.jumpPose(k, { yaw }); const x = jx0 + i * jsp; return { o, x, a: M.anchors(x, gyJ, s, o) }; });
    // the arc: dashed curve through the chest centres, plus a tiny shadow on the floor per frame
    ctx.save(); ctx.strokeStyle = 'rgba(255,200,61,0.35)'; ctx.lineWidth = 2.5; ctx.setLineDash([10, 9]);
    ctx.beginPath(); S.addCurve(ctx, P.map(q => [q.a.hip[0], q.a.hip[1] - 0.3 * U])); ctx.stroke(); ctx.restore();
    P.forEach(({ o, x }, i) => {
      M.draw(ctx, x, gyJ, s, Object.assign({}, o, { shadow: 'ground', t: ks[i] * 3 }));
      S.label(ctx, `${i + 1}  ${names[i][0]}`, x, gyJ + 30, 17, { color: INK, weight: 900 });
      S.label(ctx, names[i][1], x, gyJ + 52, 13.5, { color: SUB, weight: 700 });
    });
    SH.post(ctx);
  };
})();
