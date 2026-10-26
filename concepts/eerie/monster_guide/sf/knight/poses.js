// knight/poses.js : GUESTS pose sheet (peek totem, knock sequence on a dormant Mimiku, notebook, backaway, walk).
// SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,mimiku2/mimiku2.js,knight/knight.js,knight/poses.js knights_poses.png
// mimiku2.js and dungeon.js are optional (a plain chest / plain stone is drawn when they are missing).
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, K = window.KNIGHT, C = S.color;
  const D = window.DUNGEON, M = window.MIMIKU2;
  const W = cv.width, H = cv.height;
  const BG = '#1A2329', CARD = '#212C33', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.34)';
  const T0 = 0.35;

  function bg() {
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
  }
  function header() {
    S.title(ctx, 'GUESTS', 56, 62, 60, { align: 'left', color: INK, track: 2 });
    S.label(ctx, 'pose sheet  ·  acting without a face', 318, 50, 22, { align: 'left', color: INK });
    S.label(ctx, 'helm tilt · hands · posture · sweat · motion lines  ·  KNIGHT.draw(ctx, x, y, s, { type, variant, pose, k, phase, facing, tilt })', 318, 78, 16, { align: 'left', color: MUTED, weight: 700 });
  }
  function card(x, y, w, h, title, sub, col = CARD) {
    S.roundRect(ctx, x, y, w, h, 18, col);
    if (title) S.label(ctx, title, x + 22, y + 26, 15, { align: 'left', color: FAINT, weight: 800, track: 2 });
    if (sub) S.label(ctx, sub, x + w - 22, y + 26, 14, { align: 'right', color: MUTED, weight: 700 });
  }
  const clipCard = (x, y, w, h, fn) => { ctx.save(); S.addRoundRect && (ctx.beginPath(), S.addRoundRect(ctx, x, y, w, h, 18), ctx.clip()); fn(); ctx.restore(); };
  function frameLabel(x, y, n, text) {
    ctx.fillStyle = 'rgba(242,238,246,0.85)'; ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI * 2); ctx.fill();
    S.label(ctx, n, x, y + 1, 14, { color: BG, weight: 900 });
    S.label(ctx, text, x + 20, y + 1, 16, { align: 'left', color: INK, weight: 800 });
  }

  // ---------------------------------------------------------------- PEEK: the totem around an arch jamb
  function peek(x, y, w, h) {
    card(x, y, w, h, 'PEEK  ·  THE TOTEM', 'helm + one hand each · they nod together');
    clipCard(x, y, w, h, () => {
      const ex = x + 250, top = y + 50, gy = y + h - 26;
      // passage behind the opening: dark, a faint torch far in
      ctx.fillStyle = '#05080A'; ctx.fillRect(ex, top, x + w - ex, gy - top + 30);
      const lg = ctx.createRadialGradient(ex + 230, gy - 150, 10, ex + 230, gy - 150, 260);
      lg.addColorStop(0, 'rgba(255,170,90,0.16)'); lg.addColorStop(1, 'rgba(255,170,90,0)');
      ctx.fillStyle = lg; ctx.fillRect(ex, top, x + w - ex, gy - top);
      ctx.fillStyle = '#10171B'; ctx.fillRect(ex, gy - 8, x + w - ex, 40);
      // the jamb: stone wall face on the left with a reveal at the edge
      ctx.save(); ctx.beginPath(); ctx.rect(x, top, ex - x, gy - top + 30); ctx.clip();
      if (D) D.stoneWall(ctx, { x: x - 40, y: top - 20, w: ex - x + 40, h: gy - top + 50, bw: 112, bh: 52, gap: 3, set: D.STONE.room, seed: 9, stepped: 0.16, shadeW: 6 });
      else { ctx.fillStyle = '#2E3A42'; ctx.fillRect(x, top, ex - x, gy - top + 30); }
      ctx.restore();
      ctx.fillStyle = '#1B252C'; ctx.fillRect(ex - 16, top, 16, gy - top + 30); // reveal (wall thickness)
      ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(ex - 16, top, 4, gy - top + 30);
      // three knights, stacked. Bottom = hammer (crouched), middle = spear, top = shield. Same nod value.
      const nod = 0.35, s = 0.82;
      const clip = c => c.rect(ex, 0, 4000, 4000);
      const stack = [
        { type: 'hammer', peekH: 96, peekOut: 70, tilt: 14, handH: 132 },
        { type: 'spear', peekH: 228, peekOut: 76, tilt: 22, handH: 262 },
        { type: 'shield', peekH: 362, peekOut: 66, tilt: 12, handH: 400 },
      ];
      stack.slice().reverse().forEach(k => K.draw(ctx, ex, gy, s, Object.assign({ pose: 'peek', part: 'helm', clip, nod, t: T0 }, k)));
      stack.forEach(k => K.draw(ctx, ex, gy, s, Object.assign({ pose: 'peek', part: 'hand', t: T0 }, k)));
    });
  }

  // ---------------------------------------------------------------- KNOCK: three frames on a dormant chest
  function chest(cx, gy, s, o = {}) {
    if (M) {
      M.draw(ctx, cx, gy, s, Object.assign({ state: 'dormant', yaw: -12, t: T0 }, o));
      const a = M.anchors(cx, gy, s, Object.assign({ state: 'dormant', yaw: -12 }, o));
      return a.lidTop[1];
    }
    const w = 180 * s, h = 120 * s;
    S.shadowGroup(ctx, g => {
      S.cel(g, c => S.addRoundRect(c, cx - w / 2, gy - h, w, h, 14 * s), '#A0866B', '#7A6652', 8 * s);
      S.cel(g, c => S.addRoundRect(c, cx - w / 2 - 4 * s, gy - h - 40 * s, w + 8 * s, 46 * s, [24 * s, 24 * s, 6 * s, 6 * s]), '#A0866B', '#7A6652', 8 * s);
    }, { scale: s });
    return gy - h - 40 * s;
  }
  function knock(x, y, w, h) {
    card(x, y, w, h, 'KNOCK  ·  RULE 10 TEST', 'pommel / maul head / knuckles · KNIGHT.knockAt(type)');
    const fw = (w - 40) / 3, s = 0.76, gy = y + h - 34;
    const frames = [[0.3, '1', 'wind-up'], [0.5, '2', 'KNOCK'], [0.92, '3', 'listen…']];
    frames.forEach(([k, n, label], i) => {
      const fx = x + 20 + i * fw;
      if (i) { ctx.fillStyle = 'rgba(242,238,246,0.08)'; ctx.fillRect(fx, y + 50, 2, h - 70); }
      ctx.fillStyle = 'rgba(242,238,246,0.1)'; ctx.fillRect(fx + 10, gy, fw - 20, 2);
      const kx = fx + 96, cx = kx + K.chestDX('hammer') * s;
      ctx.save(); ctx.beginPath(); ctx.rect(fx, y + 40, fw, h - 40); ctx.clip();
      const lidY = chest(cx, gy, s, i === 2 ? { breath: 0.9 } : {});
      // the knock point is on the lid top, a little in from the near edge
      const ka = [(cx - 40 * s - kx) / s, (lidY - gy) / s + 4];
      K.draw(ctx, kx, gy, s, { type: 'hammer', pose: 'knock', k, knockAt: ka, t: T0 + i * 0.4 });
      if (i === 1) S.label(ctx, 'tok!', cx + 70 * s, lidY - 70 * s, 24, { color: 'rgba(255,244,214,0.95)', weight: 900 });
      if (i === 2) S.label(ctx, '…?', kx + 130 * s, gy - 470 * s, 30, { color: INK, weight: 900 });
      ctx.restore();
      frameLabel(fx + 24, y + 64, n, label);
    });
  }

  // ---------------------------------------------------------------- WALK: four frames, spaced by the stride
  function walk(x, y, w, h) {
    card(x, y, w, h, 'WALK  ·  4 FRAMES', 'contact · down · passing · up  ·  stride = KNIGHT.stride(type)');
    const s = 0.74, gy = y + h - 30;
    ctx.fillStyle = 'rgba(242,238,246,0.1)'; ctx.fillRect(x + 20, gy, w - 40, 2);
    const step = (w - 260) / 3;
    [0, 0.125, 0.25, 0.375].forEach((ph, i) => {
      const fx = x + 150 + i * step;
      K.draw(ctx, fx, gy, s, { type: 'spear', pose: 'walk', phase: ph, t: T0 + ph, spearLen: 400 });
      S.label(ctx, 'phase ' + ph, fx, gy + 16, 13, { color: MUTED, weight: 800 });
    });
  }

  // ---------------------------------------------------------------- NOTEBOOK
  function notebook(x, y, w, h) {
    card(x, y, w, h, 'NOTEBOOK', '404 knight · writes down the tell');
    const s = 0.8, gy = y + h - 30;
    ctx.fillStyle = 'rgba(242,238,246,0.1)'; ctx.fillRect(x + 20, gy, w - 40, 2);
    K.draw(ctx, x + 170, gy, s, { type: 'spear', variant: 'k404', pose: 'notebook', t: T0 });
    // what he writes (a page insert)
    const px = x + w - 150, py = y + 120;
    S.shadowGroup(ctx, g => {
      g.save(); g.translate(px, py); g.rotate(0.06);
      S.roundRect(g, -78, -46, 156, 112, 6, '#F4EFE6');
      for (let i = 0; i < 5; i++) g.fillRect(-64, -24 + i * 18, 128, 1.2);
      g.fillStyle = 'rgba(206,197,182,1)';
      S.label(g, 'PROTOCOL 404', 0, -32, 12, { color: '#8E1F2E', weight: 900 });
      g.font = '700 13px Courier'; g.fillStyle = '#1C1519'; g.textAlign = 'left';
      g.fillText("don't hit it.", -64, -8); g.fillText('wait.', -64, 10); g.fillText('breathes every', -64, 28); g.fillText('10 sec ✓', -64, 46);
      g.restore();
    }, { scale: 0.6 });
  }

  // ---------------------------------------------------------------- BACKAWAY
  function backaway(x, y, w, h) {
    card(x, y, w, h, 'BACKAWAY', 'scared retreat · sweat · tremble');
    const s = 0.8, gy = y + h - 30;
    clipCard(x, y, w, h, () => {
      // the threat: two gold glints in the dark at the right edge
      const rx = x + w;
      const dg = ctx.createRadialGradient(rx - 10, gy - 150, 10, rx - 10, gy - 150, 230);
      dg.addColorStop(0, 'rgba(4,5,7,0.95)'); dg.addColorStop(1, 'rgba(4,5,7,0)');
      ctx.fillStyle = dg; ctx.fillRect(rx - 260, gy - 400, 260, 420);
      S.glow(ctx, g => {
        for (const ex of [rx - 70, rx - 30]) { g.fillStyle = '#FFC83D'; g.beginPath(); g.ellipse(ex, gy - 170, 9, 12, 0, 0, Math.PI * 2); g.fill(); g.fillStyle = '#3A2400'; g.fillRect(ex - 1.5, gy - 179, 3, 18); }
      }, { blur: 10, alpha: 0.9 });
      ctx.fillStyle = 'rgba(242,238,246,0.1)'; ctx.fillRect(x + 20, gy, w - 40, 2);
      K.draw(ctx, x + 190, gy, s, { type: 'shield', pose: 'backaway', k: 0.3, t: T0 });
      // retreat arrow
      ctx.save(); ctx.strokeStyle = 'rgba(242,238,246,0.55)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(x + 120, gy + 14); ctx.lineTo(x + 50, gy + 14); ctx.moveTo(x + 62, gy + 4); ctx.lineTo(x + 50, gy + 14); ctx.lineTo(x + 62, gy + 24); ctx.stroke();
      ctx.restore();
    });
  }

  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    bg(); header();
    const yA = 104, hA = 470, yB = 590, hB = 470;
    peek(40, yA, 560, hA);
    knock(616, yA, W - 656, hA);
    walk(40, yB, 880, hB);
    notebook(936, yB, 470, hB);
    backaway(1422, yB, W - 1462, hB);
  };
})();
