// core/test.js : model-sheet test for lib_core.js (window.SFX). Renders every eye mode and helper on one 1920x1080 frame.
// node ../render_sf.mjs core/lib_core.js,core/test.js out.png [t]
(function () {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const S = window.SFX, P = S.PAL, I = P.iris;
  const CARD = '#222128', MUTED = 'rgba(236,230,242,0.62)';

  const rowTitle = (txt, x, y) => S.label(ctx, txt, x, y, 17, { align: 'left', color: 'rgba(236,230,242,0.45)', weight: 800, track: 2 });
  const cap = (txt, x, y, o = {}) => S.label(ctx, txt, x, y, 17, Object.assign({ color: MUTED, weight: 700 }, o));
  const pill = (txt, x, y) => S.label(ctx, txt, x, y, 16, { align: 'left', color: '#f2eef6', bg: 'rgba(0,0,0,0.42)', weight: 800 });

  // one skin band with six eyes on it (eyes live on pale skin, like the show)
  function eyeRow(y0, title, cells) {
    rowTitle(title, 44, y0 - 14);
    S.roundRect(ctx, 40, y0, 1200, 160, 20, P.skin);
    cells.forEach((c, i) => {
      const cx = 140 + i * 200, cy = y0 + 84;
      S.eye(ctx, Object.assign({ x: cx, y: cy, w: 136 }, c.o));
      if (c.blush) S.blush(ctx, cx + 6, cy + 62, 104, 0.32);
      cap(c.label, cx, y0 + 180);
    });
  }

  // bangs: narrow strands with thin gaps so skin shows between them (ref v1 t_004)
  function bangs(g, xa, xb, yTop, base, vary, col, seed, sw = 15, gap = 3) {
    const r = S.rng(seed);
    g.beginPath();
    for (let x = xa; x < xb; x += sw + gap) {
      const k = (x - xa) / (xb - xa), len = base + vary * r() + Math.sin(k * Math.PI) * vary * 0.4, tipX = x + sw * (0.35 + r() * 0.3);
      g.moveTo(x, yTop - 4); g.lineTo(x + sw, yTop - 4); g.lineTo(x + sw, yTop + len - sw * 0.5); g.quadraticCurveTo(x + sw, yTop + len, tipX, yTop + len + sw * 0.15); g.quadraticCurveTo(x, yTop + len, x, yTop + len - sw * 0.4); g.closePath();
    }
    g.fillStyle = col; g.fill();
  }

  // the canonical 귤멍-style close-up face, built only from SFX helpers (reference: v1 t_004)
  function faceCard(t) {
    const x0 = 1280, y0 = 140, cw = 600, ch = 340, cx = x0 + cw / 2;
    S.roundRect(ctx, x0, y0, cw, ch, 22, '#3a3a3f');
    S.clip(ctx, c => S.addRoundRect(c, x0, y0, cw, ch, 22), c => {
      // flat grey city behind (the ref's world): stepped blocks, no detail
      S.poly(c, [[x0, y0 + 120], [x0 + 90, y0 + 120], [x0 + 90, y0 + 60], [x0 + 150, y0 + 60], [x0 + 150, y0 + ch], [x0, y0 + ch]], '#4a4a50');
      S.poly(c, [[x0 + cw, y0 + 40], [x0 + cw - 110, y0 + 40], [x0 + cw - 110, y0 + 90], [x0 + cw - 170, y0 + 90], [x0 + cw - 170, y0 + ch], [x0 + cw, y0 + ch]], '#46464c');
      S.shadowGroup(c, g => {
        const HAIR = '#3b3a41', HAIRS = '#2f2e35', TIP = '#5662cf';
        // back hair with blue tips
        S.clip(g, gg => S.addBlob(gg, [[cx - 270, y0 + 420], [cx - 285, y0 + 150], [cx - 150, y0 - 10], [cx + 150, y0 - 10], [cx + 285, y0 + 150], [cx + 270, y0 + 420]]), gg => {
          S.roundRect(gg, cx - 320, y0 - 40, 640, 480, 0, HAIR);
          S.roundRect(gg, cx - 320, y0 + 300, 640, 140, 0, TIP);
        });
        // face (skin) with one hard shade along the jaw (light from top-left)
        S.cel(g, gg => S.addBlob(gg, [[cx - 206, y0 + 40], [cx + 206, y0 + 40], [cx + 202, y0 + 330], [cx + 120, y0 + 430], [cx, y0 + 460], [cx - 120, y0 + 430], [cx - 202, y0 + 330]], 0.5), P.skin, P.skinShade, 10, 10);
        // bangs: a solid cap plus strips that let skin show between them
        S.blob(g, [[cx - 236, y0 + 70], [cx - 150, y0 - 30], [cx + 150, y0 - 30], [cx + 236, y0 + 70], [cx, y0 + 60]], HAIR);
        bangs(g, cx - 212, cx + 212, y0 + 54, 92, 22, HAIR, 4, 16, 3);
        S.blob(g, [[cx - 200, y0 + 30], [cx - 120, y0 - 40], [cx + 120, y0 - 40], [cx + 200, y0 + 30], [cx, y0 + 18]], HAIRS);
        // side locks, signature colour at the tips
        for (const s of [-1, 1]) {
          const lock = gg => S.addBlob(gg, [[cx + s * 178, y0 + 30], [cx + s * 252, y0 + 70], [cx + s * 272, y0 + 300], [cx + s * 240, y0 + 470], [cx + s * 194, y0 + 300], [cx + s * 180, y0 + 140]], 0.5);
          S.clip(g, lock, gg => { gg.fillStyle = HAIR; gg.fillRect(cx - 400, y0, 800, 600); gg.fillStyle = TIP; gg.fillRect(cx - 400, y0 + 352, 800, 200); });
        }
        // eyes, blush, mouth
        const ey = y0 + 236, ew = 150;
        const info = S.eyePair(g, { x: cx, y: ey, w: ew, gap: 0.34, look: { x: -0.85, y: 0.12 }, iris: I.blue, irisScale: 0.64 });
        S.blush(g, info.xl + 4, ey + 70, ew * 0.8, 0.36);
        S.blush(g, info.xr - 4, ey + 70, ew * 0.8, 0.36);
        S.mouth(g, cx + 2, ey + 104, 20, 'smile');
      }, { scale: 1 });
    });
    S.bubble(ctx, { x: x0 + 506, y: y0 + 92, w: 140, h: 92, text: '...?', size: 34, tail: [x0 + 446, y0 + 150], pop: 1 });
    pill('eyePair · look left · ref t_004 scale', x0 + 16, y0 + 24);
  }

  function tvCard(t) {
    const x0 = 1280, y0 = 500, cw = 290, ch = 266, cx = x0 + cw / 2, cy = y0 + 126;
    S.roundRect(ctx, x0, y0, cw, ch, 18, CARD);
    S.shadowGroup(ctx, g => {
      // casing (cream plastic, one hard shade), antennae, screen
      S.capsule(g, cx - 18, cy - 62, cx - 52, cy - 96, 6, 4, '#8d8f99'); S.capsule(g, cx + 18, cy - 62, cx + 46, cy - 100, 6, 4, '#8d8f99');
      S.circle(g, cx - 52, cy - 96, 6, '#c8323f'); S.circle(g, cx + 46, cy - 100, 6, '#c8323f');
      S.cel(g, c => S.addRoundRect(c, cx - 104, cy - 66, 208, 138, 26), '#e3dbcf', '#bdb2a2', 8, 8);
      S.roundRect(g, cx - 88, cy - 52, 176, 110, 20, '#081016');
      S.clip(g, c => S.addRoundRect(c, cx - 88, cy - 52, 176, 110, 20), c => {
        const gr = c.createRadialGradient(cx, cy, 10, cx, cy, 110); gr.addColorStop(0, 'rgba(70,200,210,0.16)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
        c.fillStyle = gr; c.fillRect(cx - 90, cy - 54, 180, 114);
        S.eyePair(c, { x: cx, y: cy - 6, w: 60, gap: 0.42, glow: true, glowColor: '#8ff7ff', look: { x: 0.3, y: 0 }, lashes: 2, crease: 1, teeth: 2, lowerCrease: false });
        S.glow(c, cc => S.mouth(cc, cx + 2, cy + 34, 16, 'smile', { color: '#8ff7ff' }), { blur: 4, alpha: 0.9, bounds: { x: cx - 20, y: cy + 20, w: 40, h: 30 } });
        S.scanlines(c, cx - 88, cy - 52, 176, 110, 4, 0.22);
      });
      S.roundRect(g, cx - 30, cy + 74, 60, 10, 4, '#a39887');
    }, { scale: 0.7 });
    pill('glow mode · TV face', x0 + 14, y0 + ch - 22);
  }

  function smallFaceCard(t) {
    const x0 = 1590, y0 = 500, cw = 290, ch = 266, cx = x0 + 150, cy = y0 + 150;
    S.roundRect(ctx, x0, y0, cw, ch, 18, CARD);
    S.clip(ctx, c => S.addRoundRect(c, x0, y0, cw, ch, 18), c => {
      S.shadowGroup(c, g => {
        const HS = '#8a6a58', HSD = '#6f5446', TIPC = '#ef7d9a';
        S.blob(g, [[cx - 128, cy + 50], [cx - 142, cy - 60], [cx - 64, cy - 136], [cx + 72, cy - 136], [cx + 148, cy - 60], [cx + 136, cy + 50], [cx, cy + 70]], HSD);
        S.cel(g, c2 => S.addBlob(c2, [[cx - 100, cy - 86], [cx + 108, cy - 86], [cx + 102, cy + 16], [cx + 40, cy + 84], [cx - 50, cy + 80], [cx - 104, cy + 12]]), P.skin, P.skinShade, 6, 6);
        S.blob(g, [[cx - 124, cy - 36], [cx - 62, cy - 128], [cx + 72, cy - 128], [cx + 130, cy - 36], [cx, cy - 74]], HS);
        bangs(g, cx - 100, cx + 104, cy - 80, 30, 14, HS, 9, 13, 3);
        for (const sd of [-1, 1]) {
          const lock = c2 => S.addBlob(c2, [[cx + 3 + sd * 100, cy - 70], [cx + 3 + sd * 132, cy - 34], [cx + 3 + sd * 128, cy + 62], [cx + 3 + sd * 112, cy + 96], [cx + 3 + sd * 96, cy + 10]]);
          S.clip(g, lock, c2 => { c2.fillStyle = HS; c2.fillRect(cx - 200, cy - 150, 400, 300); c2.fillStyle = TIPC; c2.fillRect(cx - 200, cy + 58, 400, 60); });
        }
        const p = S.eyePair(g, { x: cx + 6, y: cy + 4, w: 74, turn: 0.5, look: { x: 0.9, y: -0.1 }, iris: I.rose, pupil: 'star', irisScale: 0.66, lashes: 3 });
        S.blush(g, p.xl + 4, cy + 38, 56, 0.4); S.blush(g, p.xr - 2, cy + 38, 50, 0.4);
        S.mouth(g, cx + 22, cy + 56, 13, 'o');
      }, { scale: 0.7 });
    });
    pill('look right · turn 0.5 · star', x0 + 14, y0 + ch - 22);
  }

  // helper cards along the bottom
  function helperCards(t) {
    const y0 = 812, ch = 236, n = 6, gap = 16, cw = (1840 - gap * (n - 1)) / n;
    rowTitle('HELPERS', 44, y0 - 14);
    const box = i => ({ x: 40 + i * (cw + gap), y: y0, w: cw, h: ch, cx: 40 + i * (cw + gap) + cw / 2, cy: y0 + ch / 2 - 10 });
    for (let i = 0; i < n; i++) { const b = box(i); S.roundRect(ctx, b.x, b.y, b.w, b.h, 18, CARD); }

    // 1. blush, brows, every mouth type
    let b = box(0);
    S.roundRect(ctx, b.x + 16, b.y + 20, b.w - 32, 172, 16, P.skin);
    S.brow(ctx, b.cx - 66, b.y + 50, 64, { tilt: 0.28 });
    S.brow(ctx, b.cx + 66, b.y + 50, 64, { tilt: 0.28, mirror: true });
    S.blush(ctx, b.cx - 66, b.y + 92, 96, 0.35);
    S.blush(ctx, b.cx + 66, b.y + 92, 96, 0.4, P.blush, { lines: 3 });
    ['smile', 'o', 'open', 'u', 'wave', 'cat', 'fang', 'tri'].forEach((m, i) => S.mouth(ctx, b.x + 44 + i * 29.5, b.y + 150, 20, m));
    cap('brow · blush · lines 3 · 8 mouths', b.cx, b.y + 212);

    // 2. sweat, tear, sparkle, anger
    b = box(1);
    S.sweat(ctx, b.cx - 84, b.cy - 6, 74, { angle: -0.15 });
    S.tear(ctx, b.cx - 14, b.cy - 40, 70, 12);
    S.sparkle(ctx, b.cx + 46, b.cy - 30, 26, '#fff6c8');
    S.sparkle(ctx, b.cx + 70, b.cy + 4, 13, '#fff6c8', 0.3);
    S.anger(ctx, b.cx + 96, b.cy + 52, 52);
    cap('sweat · tear · sparkle · anger', b.cx, b.y + 212);

    // 3. chains: the mimic tell (straight forward) and a hanging one that sways
    b = box(2);
    S.cel(ctx, c => S.addRoundRect(c, b.x + 22, b.y + 34, 34, 64, 8), P.iron, '#363a46', 4, 4);
    S.circle(ctx, b.x + 39, b.y + 50, 5, P.rivet);
    S.springChain(ctx, [b.x + 48, b.y + 58], 0.05, 7, 30, 0.22, P.chain);
    S.cel(ctx, c => S.addRoundRect(c, b.x + 216, b.y + 26, 56, 20, 6), P.iron, '#363a46', 3, 3);
    S.springChain(ctx, [b.x + 244, b.y + 40], Math.PI / 2, 8, 26, 1, P.chain, { t, sway: 0.25 });
    cap('springChain  sag 0.2 / 1.0', b.cx, b.y + 212);

    // 4. capsule limb (spider elbow), cel shade, joint dot, mitten hand
    b = box(3);
    S.shadowGroup(ctx, g => {
      const sh = [b.x + 40, b.y + 150], el = [b.x + 130, b.y + 52], wr = [b.x + 214, b.y + 150];
      const limb = c => S.addLimb(c, [sh, el, wr], [30, 24, 20]);
      S.cel(g, limb, '#D8CCE0', '#A8979C', 5, 5);
      S.circle(g, el[0], el[1], 5, '#A8979C');
      const hand = c => S.addBlob(c, [[wr[0] - 16, wr[1] - 6], [wr[0] + 14, wr[1] - 10], [wr[0] + 30, wr[1] + 14], [wr[0] + 26, wr[1] + 40], [wr[0] + 4, wr[1] + 46], [wr[0] - 18, wr[1] + 28]]);
      S.cel(g, hand, '#D8CCE0', '#A8979C', 5, 5);
      g.strokeStyle = '#A8979C'; g.lineWidth = 2.5; g.lineCap = 'round';
      g.beginPath(); g.moveTo(wr[0] + 8, wr[1] + 26); g.lineTo(wr[0] + 12, wr[1] + 42); g.moveTo(wr[0] + 18, wr[1] + 20); g.lineTo(wr[0] + 23, wr[1] + 36); g.stroke();
    }, { scale: 0.6 });
    cap('capsule limb + cel + group shadow', b.cx, b.y + 212);

    // 5. blob monster: Catmull-Rom body, cel shade, house eyes
    b = box(4);
    S.shadowGroup(ctx, g => {
      const bx = b.cx, by = b.cy + 14, wob = Math.sin(t * 3) * 4;
      const body = c => S.addBlob(c, [[bx - 96, by + 62], [bx - 92, by - 6], [bx - 50, by - 66 - wob], [bx + 14, by - 74 + wob], [bx + 74, by - 40], [bx + 98, by + 30], [bx + 70, by + 66]], 0.55);
      S.cel(g, body, '#7ccf8f', '#57a86d', 9, 9);
      const p = S.eyePair(g, { x: bx - 2, y: by + 4, w: 54, gap: 0.3, iris: I.green, pupil: 'oval', irisScale: 0.66, look: { x: 0.2, y: 0.1 }, lashes: 2, crease: 1 });
      S.blush(g, p.xl, by + 32, 40, 0.4); S.blush(g, p.xr, by + 32, 40, 0.4);
      S.mouth(g, bx, by + 44, 12, 'fang');
    }, { scale: 0.7 });
    cap('blob (Catmull-Rom) + cel', b.cx, b.y + 212);

    // 6. shadowGroup vs per-part shadows
    b = box(5);
    const mini = (g, x, y) => {
      S.roundRect(g, x - 36, y - 2, 72, 76, 18, '#e7a3b0');
      S.circle(g, x, y - 40, 44, '#f6e6e8');
      S.blob(g, [[x - 50, y - 44], [x - 40, y - 92], [x + 40, y - 92], [x + 50, y - 44], [x, y - 66]], '#3b3a41');
      S.eyePair(g, { x, y: y - 26, w: 30, gap: 0.36, lashes: 2, crease: 0, teeth: 2, lowerCrease: false });
    };
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 12; ctx.shadowOffsetX = 7; ctx.shadowOffsetY = 7;
    mini(ctx, b.cx - 66, b.cy + 22);
    ctx.restore();
    S.shadowGroup(ctx, g => mini(g, b.cx + 66, b.cy + 22), { scale: 0.75, color: 'rgba(0,0,0,0.6)' });
    cap('per part (no)', b.cx - 66, b.y + 212); cap('shadowGroup', b.cx + 66, b.y + 212);
  }

  window.draw = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    S.sheetBG(ctx, W, H, { title: 'SFX core · shared kit test', subtitle: 'lib_core.js v' + S.version + '  ·  귤멍 eye recipe (plan 3-2)  ·  flat fills, one hard shade, one group shadow' });

    eyeRow(140, 'PUPILS  (irisScale 0.62)', [
      { label: "oval · blue", o: { iris: I.blue, pupil: 'oval' } },
      { label: "slit · gold", o: { iris: I.gold, pupil: 'slit', pupilColor: '#2A1206' } },
      { label: "star · rose", o: { iris: I.rose, pupil: 'star' } },
      { label: "dot · green", o: { iris: I.green, pupil: 'dot' } },
      { label: "swirl · violet", o: { iris: I.violet, pupil: 'swirl' } },
      { label: "none · teal", o: { iris: I.teal, pupil: 'none', mirror: true } },
    ]);
    eyeRow(364, 'IRIS SIZE  ·  EYE SHAPE', [
      { label: 'iris 0.3 (smug, eerie)', o: { iris: I.gold, irisScale: 0.3, pupil: 'slit', pupilColor: '#2A1206' } },
      { label: 'iris 0.65', o: { iris: I.gold, irisScale: 0.65, pupil: 'slit', pupilColor: '#2A1206' } },
      { label: "iris 'dot' + tears", o: { ...S.EXPR.fear, iris: I.blue } },
      { label: 'h 0.45 half-lid', o: { h: 0.45, iris: I.violet } },
      { label: 'h 0.5 almond', o: { h: 0.5, iris: I.violet } },
      { label: 'h 0.8 round', o: { h: 0.8, iris: I.violet, mirror: true } },
    ]);
    eyeRow(588, 'LIDS  ·  CLOSED  ·  EXPRESSIONS', [
      { label: "closed 'smile'", o: { closed: 'smile' }, blush: true },
      { label: "closed 'flat' (blink)", o: { closed: 'flat' } },
      { label: 'open 0.5 (bored)', o: { ...S.EXPR.bored, iris: I.teal } },
      { label: 'eerie: no glint, dark circle', o: { ...S.EXPR.eerie, iris: I.red } },
      { label: 'angry (tilt +)', o: { ...S.EXPR.angry, iris: I.rose } },
      { label: 'smug (lower raise)', o: { ...S.EXPR.smug, iris: I.gold, pupil: 'slit', pupilColor: '#2A1206', mirror: true } },
    ]);

    faceCard(t);
    tvCard(t);
    smallFaceCard(t);
    helperCards(t);

    S.vignette(ctx, 0.35);
    S.grain(ctx, 0.05, 3 + Math.floor(t * 24));
  };
})();
