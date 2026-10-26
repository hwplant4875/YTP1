// mimiku/sheet.js : SF2 model sheet 1 for Mimiku (six poses on one ground line + turnaround + callouts).
// node ../render_sf.mjs core/lib_core.js,mimiku/mimiku.js,mimiku/sheet.js out.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height, S = window.SFX, M = window.MIMIKU, COL = M.COL;
  const BG = '#1A2329', CARD = '#212C33', CARD2 = '#26323A', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.32)';

  const SC = 0.74, UW = 200 * SC;      // one W in px for the pose row
  const GY = 646;                        // pose ground line
  const POSES = [
    { x: 112, pose: 'dormant', n: '1', name: 'DORMANT', sub: ['shut · 6° crooked · glints'] },
    { x: 382, pose: 'peek', n: '2', name: 'PEEK', sub: ['lid 40° · taps the floor'] },
    { x: 700, pose: 'stand', n: '3', name: 'REVEAL / STAND', sub: ['lid 70° · small wave'] },
    { x: 1040, pose: 'crouch', n: '4', name: 'SPIDER CROUCH', sub: ['lid 45° · tongue hangs low'] },
    { x: 1422, pose: 'pounce', n: '5', name: 'POUNCE', sub: ['lid 80° · airborne lunge'] },
    { x: 1738, pose: 'yawn', n: '6', name: 'SLEEP / YAWN', sub: ['lid 90° · stretch'] },
  ];

  function background() {
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
  }
  function header() {
    S.title(ctx, 'MIMIKU', 56, 70, 74, { align: 'left', color: INK, weight: 600, track: 2 });
    const tw = (() => { ctx.save(); ctx.font = '600 74px Fredoka'; try { ctx.letterSpacing = '2px'; } catch (e) { } const w = ctx.measureText('MIMIKU').width; ctx.restore(); return w; })();
    S.label(ctx, 'new hire #001  ·  treasure-chest mimic  ·  Monster HR', 56 + tw + 26, 58, 22, { align: 'left', color: INK, weight: 800 });
    S.label(ctx, 'SF2 model sheet  ·  W = chest width  ·  all poses same scale', 56 + tw + 26, 88, 18, { align: 'left', color: MUTED, weight: 700 });
    // scale bar
    const x0 = W - 56 - UW;
    ctx.fillStyle = FAINT; ctx.fillRect(x0, 74, UW, 3); ctx.fillRect(x0, 66, 3, 19); ctx.fillRect(x0 + UW - 3, 66, 3, 19);
    S.label(ctx, '1 W', x0 + UW / 2, 52, 18, { color: MUTED, weight: 800 });
  }
  function poseRow() {
    ctx.fillStyle = 'rgba(242,238,246,0.14)'; ctx.fillRect(40, GY, W - 80, 2);
    for (const P of POSES) {
      const air = P.pose === 'pounce';
      S.groundShadow(ctx, P.x + (air ? 0.25 * UW : 0), GY + 2, (air ? 1.3 : 1.25) * UW, 0.16 * UW, air ? 0.28 : 0.42);
      M.draw(ctx, { x: P.x, y: GY, scale: SC, pose: P.pose, t: 0 });
      const lx = P.x + (P.lx || 0);
      ctx.save(); ctx.font = '800 21px Nunito'; const nw = ctx.measureText(P.name).width; ctx.restore();
      const left = lx - (nw + 34) / 2;
      S.circle(ctx, left + 11, GY + 34, 12, 'rgba(242,238,246,0.88)');
      S.label(ctx, P.n, left + 11, GY + 35, 15, { color: BG, weight: 900 });
      S.label(ctx, P.name, left + 32, GY + 35, 21, { align: 'left', color: INK, weight: 800 });
      P.sub.forEach((t, i) => S.label(ctx, t, lx, GY + 62 + i * 20, 15.5, { color: MUTED, weight: 700 }));
    }
  }

  // ---------------------------------------------------------------- bottom band
  const BY = 736; // band top
  function card(x, y, w, h, title) {
    S.roundRect(ctx, x, y, w, h, 18, CARD);
    if (title) S.label(ctx, title, x + 18, y + 24, 15, { align: 'left', color: FAINT, weight: 900, track: 2 });
  }
  function turnaround() {
    const x0 = 40, w = 760, h = H - BY - 26;
    card(x0, BY, w, h, 'TURNAROUND');
    const sc = 0.45, U = 200 * sc, gy = BY + h - 16;
    // height guides (W units), measured from the rig
    const top = M.solve({ x: 0, y: 0, scale: sc, pose: 'rest' }).top;
    const guides = [[0, 'ground'], [1.32, 'hip 1.32 W'], [-top / U, 'top ' + (-top / U).toFixed(2) + ' W']];
    ctx.save();
    for (const [hh, lab] of guides) {
      const y = gy - hh * U;
      ctx.setLineDash([6, 7]); ctx.strokeStyle = 'rgba(242,238,246,0.16)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x0 + 120, y); ctx.lineTo(x0 + w - 18, y); ctx.stroke();
      ctx.setLineDash([]);
      S.label(ctx, lab, x0 + 108, y, 14, { align: 'right', color: FAINT, weight: 800 });
    }
    ctx.restore();
    const views = [
      { x: x0 + 250, cap: 'FRONT', o: { yaw: 0 } },
      { x: x0 + 470, cap: '3/4', o: { yaw: 35, legs: { L: { foot: [-0.24, -0.035] }, R: { foot: [0.42, -0.035] } }, arms: { L: { wrist: [-0.8, -1.52] }, R: { wrist: [1.06, -1.5] } } } },
      { x: x0 + 655, cap: 'SIDE', o: { yaw: 90, legs: { L: { foot: [0.16, -0.035], bend: 1 }, R: { foot: [-0.2, -0.035], bend: 1 } }, arms: { L: { wrist: [0.42, -1.5], bend: -1 }, R: { wrist: [0.22, -1.46], bend: -1 } } } },
    ];
    for (const V of views) {
      S.groundShadow(ctx, V.x, gy + 2, 1.1 * U, 0.15 * U, 0.4);
      M.draw(ctx, Object.assign({ x: V.x, y: gy, scale: sc, pose: 'rest', t: 0 }, V.o));
      S.label(ctx, V.cap, V.x, BY + 26, 15, { color: MUTED, weight: 900, track: 1.5 });
    }
  }
  function callouts() {
    const x0 = 820, y0 = BY, h = H - BY - 26;
    const cw = [178, 178, 232, 168], gap = 14;
    let x = x0;
    // (a) peg teeth
    card(x, y0, cw[0], h, 'PEG TEETH');
    {
      const cx = x + cw[0] / 2, k = 700; // px per W
      ctx.save(); ctx.translate(cx, y0 + 66);
      S.roundRect(ctx, -70, -14, 140, 26, 12, COL.gum);
      [[-45, 0.074], [-15, 0.054], [15, 0.074], [45, 0.054]].forEach(([dx, L]) => M.drawTooth(ctx, dx, 4, L * k, 0.043 * k, true));
      ctx.restore();
      ctx.save(); ctx.translate(cx, y0 + 196);
      S.roundRect(ctx, -70, -12, 140, 26, 12, COL.gum);
      [[-45, 0.054], [-15, 0.04], [15, 0.054], [45, 0.04]].forEach(([dx, L]) => M.drawTooth(ctx, dx, -4, L * k, 0.043 * k, false));
      ctx.restore();
      S.label(ctx, '13 up · 12 down', cx, y0 + h - 42, 15, { color: MUTED, weight: 800 });
      S.label(ctx, 'long/short, round tips', cx, y0 + h - 21, 13.5, { color: FAINT, weight: 700 });
    }
    x += cw[0] + gap;
    // (b) mitten hand
    card(x, y0, cw[1], h, 'MITTEN HAND');
    {
      const cx = x + cw[1] / 2;
      M.drawHand(ctx, cx - 4, y0 + 52, 90, 'open', 1, 500);
      S.label(ctx, '3 lumps + thumb', cx, y0 + h - 42, 15, { color: MUTED, weight: 800 });
      S.label(ctx, 'blunt claw tips', cx, y0 + h - 21, 13.5, { color: FAINT, weight: 700 });
    }
    x += cw[1] + gap;
    // (c) the tell: chain sticks forward (side view crop)
    card(x, y0, cw[2], h, 'THE TELL');
    {
      ctx.save();
      ctx.beginPath(); S.addRoundRect(ctx, x, y0, cw[2], h, 18); ctx.clip();
      S.groundShadow(ctx, x + 140, y0 + h - 66, 150, 22, 0.45);
      M.draw(ctx, { x: x + 140, y: y0 + h - 66, scale: 1.0, pose: 'dormant', yaw: 90, tilt: 0, lid: 7, parts: { legs: false, arms: false } });
      ctx.restore();
      S.label(ctx, 'chain sticks FORWARD', x + cw[2] / 2, y0 + h - 42, 15, { color: MUTED, weight: 800 });
      S.label(ctx, 'stiff, never hangs down', x + cw[2] / 2, y0 + h - 21, 13.5, { color: FAINT, weight: 700 });
    }
    x += cw[2] + gap;
    // (d) our clasp
    card(x, y0, cw[3], h, 'OUR CLASP');
    {
      const cx = x + cw[3] / 2;
      M.drawClasp(ctx, cx, y0 + 60, 104);
      S.label(ctx, 'brass heart hasp', cx, y0 + h - 42, 15, { color: MUTED, weight: 800 });
      S.label(ctx, 'our own shape, swings', cx, y0 + h - 21, 13.5, { color: FAINT, weight: 700 });
    }
    x += cw[3] + gap;
    // (e) palette
    const pw = W - 40 - x;
    card(x, y0, pw, h, 'PALETTE');
    {
      const chips = [
        ['wood', COL.wood], ['wood shade', COL.woodShade], ['rim light', COL.woodRim], ['iron', COL.iron], ['brass', COL.brass], ['limb', COL.limb],
        ['limb shade', COL.limbShade], ['mouth', COL.mouth], ['gum', COL.gum], ['tooth', COL.tooth], ['tongue', COL.tongue], ['gold iris', '#FFC83D'],
      ];
      const cols = 2, cwid = (pw - 30) / cols, rh = 38;
      chips.forEach(([n, c], i) => {
        const cx = x + 16 + (i % cols) * cwid, cy = y0 + 44 + Math.floor(i / cols) * rh;
        S.roundRect(ctx, cx, cy, 28, 28, 8, c);
        S.label(ctx, n, cx + 36, cy + 8, 12.5, { align: 'left', color: MUTED, weight: 800 });
        S.label(ctx, c.toUpperCase(), cx + 36, cy + 22, 11, { align: 'left', color: FAINT, weight: 700 });
      });
    }
  }

  window.draw = function (t) {
    background();
    header();
    poseRow();
    turnaround();
    callouts();
    S.vignette(ctx, 0.22, { inner: 0.6, outer: 1.15 });
    S.grain(ctx, 0.03, 3);
  };
})();
