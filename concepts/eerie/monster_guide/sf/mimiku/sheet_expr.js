// mimiku/sheet_expr.js : SF2 model sheet 2 for Mimiku, six open-mouth close-ups (eyes + teeth + tongue).
// node ../render_sf.mjs core/lib_core.js,mimiku/mimiku.js,mimiku/sheet_expr.js out.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height, S = window.SFX, M = window.MIMIKU;
  const BG = '#1A2329', CARD = '#212C33', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.32)';

  // close-up framing: same scale and lid for every panel so the faces compare 1:1
  const SC = 2.1;
  const PANELS = [
    { n: '1', name: 'DEFAULT · CUTE', expr: 'default', notes: 'gold iris 0.66 · slit pupil · one highlight · blush',
      o: { tongue: { len: 0.4, pitch: [25, 86, 95, 84], lat: [0, 2, 6, 10] } } },
    { n: '2', name: 'NERVOUS', expr: 'nervous', notes: 'iris 0.3 · pinpoint pupils · brows up · sweat drop',
      o: { tilt: -3, tongue: null } },
    { n: '3', name: 'GREEDY', expr: 'greedy', notes: 'star pupils · double highlight · drool · sparkles',
      o: { lid: 78, tongue: { len: 0.5, pitch: [15, 55, 40, 10], lat: [0, 30, 62, 82], width: 0.23 } } },
    { n: '4', name: 'HAPPY', expr: 'happy', notes: 'closed arcs + 3 lashes · brows lifted · big blush',
      o: { tilt: 3, tongue: { len: 0.42, pitch: [25, 82, 95, 74], lat: [0, -3, -8, -14] } } },
    { n: '5', name: 'CREEPY', expr: 'creepy', notes: 'no highlight · dark rings · brows down · no blush',
      o: { lid: 60, tongue: { len: 0.95, pitch: [30, 90, 92, 90, 88], lat: [0, 0, 3, -3, 2], width: 0.15 } } },
    { n: '6', name: 'DIZZY', expr: 'dizzy', notes: 'swirl eyes · uneven brows · tongue lolls out',
      o: { tilt: 7 } },
  ];

  function background() {
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
  }
  function header() {
    S.title(ctx, 'MIMIKU', 56, 70, 74, { align: 'left', color: INK, weight: 600, track: 2 });
    ctx.save(); ctx.font = '600 74px Fredoka'; try { ctx.letterSpacing = '2px'; } catch (e) { } const tw = ctx.measureText('MIMIKU').width; ctx.restore();
    S.label(ctx, 'expressions  ·  open-mouth close-ups', 56 + tw + 26, 58, 22, { align: 'left', color: INK, weight: 800 });
    S.label(ctx, 'SF2 model sheet 2  ·  same scale, lid 70° unless noted  ·  the face lives inside the mouth', 56 + tw + 26, 88, 18, { align: 'left', color: MUTED, weight: 700 });
    S.label(ctx, 'lid under 35°: eyes become two glints', W - 56, 58, 17, { align: 'right', color: MUTED, weight: 800 });
    S.label(ctx, 'brows float, never touch the eyes', W - 56, 86, 17, { align: 'right', color: FAINT, weight: 800 });
  }

  const GX = 40, GY = 124, GAP = 20, COLS = 3, ROWS = 2;
  const PW = (W - 2 * GX - (COLS - 1) * GAP) / COLS, PH = (H - GY - 30 - (ROWS - 1) * GAP) / ROWS;
  const LABEL_H = 74;

  function panel(i) {
    const P = PANELS[i], c = i % COLS, r = Math.floor(i / COLS);
    const x = GX + c * (PW + GAP), y = GY + r * (PH + GAP);
    const artH = PH - LABEL_H;
    S.roundRect(ctx, x, y, PW, PH, 20, CARD);
    ctx.save();
    ctx.beginPath(); S.addRoundRect(ctx, x, y, PW, artH + 10, 20); ctx.clip();
    // soft stage light behind the face
    const gr = ctx.createRadialGradient(x + PW / 2, y + artH * 0.46, 10, x + PW / 2, y + artH * 0.46, PW * 0.55);
    gr.addColorStop(0, 'rgba(255,236,214,0.075)'); gr.addColorStop(1, 'rgba(255,236,214,0)');
    ctx.fillStyle = gr; ctx.fillRect(x, y, PW, artH + 10);
    // place the mouth centre at a fixed spot of the panel
    const base = Object.assign({ x: 0, y: 0, scale: SC, pose: 'rest', expr: P.expr, lid: 70, parts: { legs: false, arms: false, chain: false } }, P.o);
    const m = M.solve(base).mouth;
    const tx = x + PW / 2, ty = y + artH * 0.5;
    M.draw(ctx, Object.assign({}, base, { x: tx - m[0], y: ty - m[1], t: 0 }));
    ctx.restore();
    // divider + labels
    ctx.fillStyle = 'rgba(242,238,246,0.08)'; ctx.fillRect(x + 18, y + artH + 10, PW - 36, 2);
    ctx.save(); ctx.font = '800 24px Nunito'; const nw = ctx.measureText(P.name).width; ctx.restore();
    const left = x + PW / 2 - (nw + 38) / 2;
    S.circle(ctx, left + 13, y + artH + 36, 14, 'rgba(242,238,246,0.88)');
    S.label(ctx, P.n, left + 13, y + artH + 37, 17, { color: BG, weight: 900 });
    S.label(ctx, P.name, left + 36, y + artH + 37, 24, { align: 'left', color: INK, weight: 800 });
    S.label(ctx, P.notes, x + PW / 2, y + artH + 62, 15.5, { color: MUTED, weight: 700 });
  }

  window.draw = function (t) {
    background();
    header();
    for (let i = 0; i < PANELS.length; i++) panel(i);
    S.vignette(ctx, 0.2, { inner: 0.6, outer: 1.15 });
    S.grain(ctx, 0.03, 3);
  };
})();
