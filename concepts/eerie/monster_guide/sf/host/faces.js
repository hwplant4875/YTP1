// host/faces.js : HELEN screen-face sheet (all faces, lip-sync mouths, static wipe).
// node render_sf.mjs core/lib_core.js,host/helen.js,host/faces.js out.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN;
  const W = cv.width, H = cv.height;
  const BG = '#1A2329', CARD = '#212C33', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.34)';
  const card = (x, y, w, h) => S.roundRect(ctx, x, y, w, h, 18, CARD);

  const ROW1 = [
    { f: 'neutral', name: 'NEUTRAL', sub: 'two dots + a line · rods in a V' },
    { f: 'pleased', name: 'PLEASED', sub: '^ ^ arcs + smile · rods perk' },
    { f: 'surprised', name: 'SURPRISED', sub: 'big dots + small o · kick + spark', antT: 0.12 },
    { f: 'annoyed', name: 'ANNOYED', sub: 'slanted strokes · rods cross' },
    { f: 'eerie', name: 'EERIE', sub: 'two lights drift · a smile flickers', eerieSmile: true, t: 4 },
    { f: 'panic', name: 'PANIC', sub: 'colour bars + beep · rods shake', t: 0.37 },
  ];
  const ROW2 = [
    { f: 'thinking', name: 'THINKING', sub: 'loading ring · slow nod', t: 1.1 },
    { f: 'number', number: '7°', name: 'NUMBER  7°', sub: 'angle / score / timer' },
    { f: 'number', number: '9.9', numberLabel: 'SECONDS', name: 'NUMBER  9.9', sub: 'with a caption' },
    { f: 'slide', slide: { n: 10, text: 'When they knock, open wide.' }, name: 'SLIDE', sub: 'Rule card · face keeps talking', mouth: 'o' },
    { f: 'off', offK: 0.74, name: 'OFF', sub: 'shrinks to a dot · rods flop' },
    { f: 'error404', name: 'ERROR 404', sub: 'glitch · rods stand straight', t: 0.2 },
  ];

  function head(x, y, s, o) { HL.drawHead(ctx, x, y, s, Object.assign({ bloom: 0.5, autoBlink: false }, o)); }

  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
    S.title(ctx, 'HELEN', 56, 66, 70, { align: 'left', color: INK, track: 2 });
    S.label(ctx, 'screen faces  ·  HR manager, Monster HR', 300, 54, 22, { align: 'left', color: INK });
    S.label(ctx, 'minimal: two dots + one mouth mark, #C4F5EC on #0F3B36  ·  2-3 frame static wipe on change', 300, 84, 18, { align: 'left', color: MUTED, weight: 700 });

    const cw = 296, ch = 318, gx = 16, x0 = (W - (6 * cw + 5 * gx)) / 2, s = 1.42;
    [[ROW1, 118], [ROW2, 118 + ch + 14]].forEach(([row, y0]) => {
      row.forEach((c, i) => {
        const x = x0 + i * (cw + gx);
        card(x, y0, cw, ch);
        const o = Object.assign({ face: c.f, t: c.t ?? 0.4 }, c);
        head(x + cw / 2, y0 + 248, s, o);
        S.label(ctx, c.name, x + cw / 2, y0 + 276, 21, { color: INK, weight: 800 });
        S.label(ctx, c.sub, x + cw / 2, y0 + 300, 15, { color: MUTED, weight: 700 });
      });
    });

    // bottom strip: lip-sync mouths + static wipe
    const y3 = 118 + 2 * (ch + 14), h3 = H - y3 - 18;
    const mw = 1092;
    card(x0, y3, mw, h3);
    S.label(ctx, 'LIP-SYNC MOUTHS', x0 + 24, y3 + 26, 16, { align: 'left', color: FAINT, weight: 800, track: 2 });
    const M = [['none', 'none (rest)'], ['o', 'o'], ['u', 'u'], ['wide', 'wide'], ['~', '~']];
    M.forEach(([m, lab], i) => {
      const x = x0 + 120 + i * 214;
      head(x, y3 + h3 - 34, 1.0, { face: 'neutral', mouth: m, t: 0.4, bloom: 0.4, look: { x: 0, y: 0 } });
      S.label(ctx, lab, x, y3 + h3 - 16, 15, { color: MUTED, weight: 800 });
    });
    const wx = x0 + mw + gx, ww = W - wx - x0;
    card(wx, y3, ww, h3);
    S.label(ctx, 'STATIC WIPE  ·  neutral → pleased, 3 frames', wx + 24, y3 + 26, 16, { align: 'left', color: FAINT, weight: 800, track: 2 });
    [0.22, 0.5, 0.8].forEach((k, i) => {
      const x = wx + 112 + i * 222;
      head(x, y3 + h3 - 34, 1.0, { face: 'pleased', prevFace: 'neutral', wipe: k, t: 0.4 + i / 30, bloom: 0.4, antT: i / 30 });
      S.label(ctx, `frame ${i + 1}`, x, y3 + h3 - 16, 15, { color: MUTED, weight: 800 });
    });
  };
})();
