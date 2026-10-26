/* sheet_common.js : shared backdrop + labels for the Mimiku v2 sheets (window.M2SHEET). Loads after lib_core.js and
 * mimiku2.js. Calm dark dungeon-tone backdrop, header, palette chips, height guides, scale bar, state labels. */
(function () {
  const S = window.SFX, M = window.MIMIKU2, C = S.color;
  const INK = '#EDE7F2', SUB = 'rgba(237,231,242,0.55)', DIMC = 'rgba(237,231,242,0.32)';
  const SH = window.M2SHEET = {};

  SH.bg = (ctx, title, sub1, sub2, o = {}) => {
    const Wc = ctx.canvas.width, Hc = ctx.canvas.height;
    const g = ctx.createLinearGradient(0, 0, 0, Hc);
    g.addColorStop(0, '#191B22'); g.addColorStop(1, '#13141A');
    ctx.fillStyle = g; ctx.fillRect(0, 0, Wc, Hc);
    // faint stone courses (dungeon tone, very low contrast)
    ctx.save(); ctx.globalAlpha = 0.28;
    const r = S.rng('sheet-stones');
    for (let y = 0, row = 0; y < Hc; y += 60, row++) {
      for (let x = -((row % 2) * 70); x < Wc; x += 140) {
        const k = r.range(-0.012, 0.012);
        ctx.fillStyle = C.shade('#1C1E26', k * 10);
        S.roundRect(ctx, x + 2, y + 2, 136, 56, 4, ctx.fillStyle);
      }
    }
    ctx.restore();
    ctx.fillStyle = 'rgba(19,20,26,0.55)'; ctx.fillRect(0, 0, Wc, Hc);
    if (title) {
      S.title(ctx, title, 48, 62, 62, { align: 'left', color: INK, weight: 600 });
      const tw = (() => { ctx.save(); ctx.font = '600 62px Fredoka'; const w = ctx.measureText(title).width; ctx.restore(); return w; })();
      S.label(ctx, sub1, 48 + tw + 26, 50, 24, { align: 'left', color: INK, weight: 800 });
      S.label(ctx, sub2, 48 + tw + 26, 80, 19, { align: 'left', color: SUB, weight: 700 });
    }
    if (o.palette !== false) SH.palette(ctx, Wc - 40, 52);
  };

  SH.palette = (ctx, xr, y) => {
    const P = M.COL;
    const chips = [['wood', P.wood], ['shade', P.woodShade], ['iron', P.iron], ['gold', P.gold], ['mouth', P.mouth], ['eye glow', P.glow],
      ['skin', P.skin], ['skin shade', P.skinShade], ['knuckle', P.pink], ['tongue', P.tongue], ['tooth', P.tooth]];
    let x = xr;
    for (let i = chips.length - 1; i >= 0; i--) {
      const [n, col] = chips[i];
      S.circle(ctx, x - 11, y - 8, 11, col);
      if (col === P.mouth) S.circle(ctx, x - 11, y - 8, 11, null, 'rgba(255,255,255,0.25)', 1.5);
      S.label(ctx, n, x - 11, y + 16, 11, { color: SUB, weight: 800 });
      S.label(ctx, col.toUpperCase(), x - 11, y + 29, 9, { color: DIMC, weight: 700 });
      x -= 62;
    }
  };

  SH.floor = (ctx, gy) => {
    const Wc = ctx.canvas.width;
    ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(0, gy, Wc, ctx.canvas.height - gy);
    ctx.fillStyle = 'rgba(237,231,242,0.18)'; ctx.fillRect(40, gy, Wc - 80, 2);
  };

  SH.heightGuides = (ctx, gy, U, lines, x0, x1) => {
    ctx.save();
    lines.forEach(([h, txt], i) => {
      const y = gy - h * U;
      ctx.strokeStyle = i ? 'rgba(255,200,61,0.42)' : 'rgba(170,176,186,0.5)'; ctx.lineWidth = 2; ctx.setLineDash([12, 10]);
      ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
      S.label(ctx, txt, x0 + 4, y - 14, 15, { align: 'left', color: i ? 'rgba(255,214,110,0.85)' : 'rgba(200,205,214,0.8)', weight: 800 });
    });
    ctx.restore();
  };

  SH.scaleBar = (ctx, x, gy, U, maxW) => {
    ctx.fillStyle = 'rgba(237,231,242,0.55)';
    ctx.fillRect(x, gy - maxW * U, 3, maxW * U);
    for (let i = 0; i <= maxW * 2; i++) {
      const y = gy - i * 0.5 * U, major = i % 2 === 0;
      ctx.fillRect(x - (major ? 12 : 6), y - 1, major ? 15 : 9, 2);
      if (major) S.label(ctx, `${i / 2} W`, x + 12, y, 14, { align: 'left', color: SUB, weight: 800 });
    }
  };

  SH.stateLabel = (ctx, x, y, n, a, b) => {
    S.circle(ctx, x - (a.length * 9.5) / 2 - 22, y, 13, INK);
    S.label(ctx, n, x - (a.length * 9.5) / 2 - 22, y + 1, 16, { color: '#17161c', weight: 900 });
    S.label(ctx, a, x - (a.length * 9.5) / 2 - 2, y + 1, 23, { align: 'left', color: INK, weight: 900 });
    S.label(ctx, b, x, y + 30, 14.5, { color: SUB, weight: 700 });
  };

  SH.speed = (ctx, x, y, U) => {
    ctx.save(); ctx.strokeStyle = 'rgba(237,231,242,0.28)'; ctx.lineCap = 'round';
    [[-0.2, 0.0, 0.9], [0.15, 0.25, 0.7], [0.4, -0.15, 0.55]].forEach(([dy, dx, l]) => {
      ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x + (0.9 + dx) * U, y + dy * U); ctx.lineTo(x + (0.9 + dx + l) * U, y + (dy - l * 0.55) * U); ctx.stroke();
    });
    ctx.restore();
  };

  // a rounded detail panel; fn(ctx) draws inside a clip
  SH.inset = (ctx, x, y, w, h, title, sub, fn, o = {}) => {
    S.shadowGroup(ctx, g => S.roundRect(g, x, y, w, h, 18, o.bg || '#20222B'), { blur: 18, dx: 6, dy: 6, color: 'rgba(0,0,0,0.5)' });
    ctx.save(); ctx.beginPath(); S.addRoundRect(ctx, x, y, w, h, 18); ctx.clip(); fn(ctx); ctx.restore();
    S.roundRect(ctx, x + 10, y + 10, Math.min(w - 20, title.length * 9.6 + 22), 26, 13, 'rgba(14,14,19,0.72)');
    S.label(ctx, title, x + 21, y + 23.5, 13, { align: 'left', color: o.tc || INK, weight: 900, track: 1.2 });
    if (sub) S.label(ctx, sub, x + w / 2, y + h + 17, 12.5, { color: SUB, weight: 700 });
  };
  // draw the rig so that the anchor picked by pick(anchors) lands on (cx, cy)
  SH.focus = (ctx, cx, cy, s, opts, pick) => {
    const a = M.anchors(0, 0, s, opts), q = pick(a);
    M.draw(ctx, cx - q[0], cy - q[1], s, opts);
  };

  SH.post = ctx => { S.vignette(ctx, 0.45, { inner: 0.55 }); S.grain(ctx, 0.04, 3); };
})();
