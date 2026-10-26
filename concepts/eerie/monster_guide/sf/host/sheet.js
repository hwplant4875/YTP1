// host/sheet.js : HELEN model sheet (front, 3/4, four poses, head construction, props, palette).
// node render_sf.mjs core/lib_core.js,host/helen.js,host/sheet.js out.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, HL = window.HELEN, COL = HL.COL;
  const W = cv.width, H = cv.height, UH = HL.H;
  const BG = '#1A2329', CARD = '#212C33', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.34)';
  const SC = 1.18, GY = 742;
  const FIG = [
    { x: 150, n: '1', name: 'FRONT', sub: 'idle · weight on one leg', o: { pose: 'idle-clipboard', face: 'neutral', look: { x: 0, y: 0.1 } } },
    { x: 452, n: '2', name: 'THREE-QUARTER', sub: 'turn 35° · neutral', o: { pose: 'idle-clipboard', face: 'neutral', turn: 1 } },
    { x: 790, n: '3', name: 'REMOTE AT HEAD', sub: 'switches to a Rule slide', o: { pose: 'remote-at-head', face: 'slide', slide: { n: 10, text: 'When they knock, open wide.' }, mouth: 'o' } },
    { x: 1150, n: '4', name: 'PRESENT / POINT', sub: 'head turns to the remote', o: { pose: 'present-point', face: 'neutral', mouth: 'wide', look: { x: -0.7, y: 0 } } },
    { x: 1478, n: '5', name: 'STAMP · APPROVED', sub: 'wind-up, ink on the form', o: { pose: 'stamp', face: 'pleased', stampK: 0, stampMark: true, antT: 0.12 } },
    { x: 1762, n: '6', name: 'WALK', sub: 'bouncy pencil-skirt steps', o: { pose: 'walk', phase: 0.04, turn: 1, face: 'neutral' } },
  ];

  function bg() {
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
  }
  function header() {
    S.title(ctx, 'HELEN', 56, 66, 70, { align: 'left', color: INK, track: 2 });
    S.label(ctx, 'HR manager  ·  TV head  ·  Monster HR host', 300, 54, 22, { align: 'left', color: INK });
    S.label(ctx, 'model sheet  ·  H = TV head height  ·  all figures same scale', 300, 84, 18, { align: 'left', color: MUTED, weight: 700 });
    // scale bar: 1 H
    const len = UH * 1.1 * SC, x1 = W - 70, x0 = x1 - len;
    ctx.fillStyle = MUTED; ctx.fillRect(x0, 72, len, 3); ctx.fillRect(x0, 62, 3, 22); ctx.fillRect(x1 - 3, 62, 3, 22);
    S.label(ctx, '1 H (head)', (x0 + x1) / 2, 48, 18, { color: MUTED, weight: 800 });
  }
  function badgeNum(x, y, n) {
    ctx.fillStyle = 'rgba(242,238,246,0.85)'; ctx.beginPath(); ctx.arc(x, y, 13, 0, Math.PI * 2); ctx.fill();
    S.label(ctx, n, x, y + 1, 16, { color: BG, weight: 900 });
  }
  function figures() {
    ctx.fillStyle = 'rgba(242,238,246,0.12)'; ctx.fillRect(40, GY, W - 80, 2);
    FIG.forEach(f => {
      HL.draw(ctx, f.x, GY, SC, Object.assign({ t: 0.4, autoBlink: false, bloom: 0.45 }, f.o));
      const tw = (() => { ctx.save(); ctx.font = '800 21px Nunito'; const w = ctx.measureText(f.name).width; ctx.restore(); return w; })();
      badgeNum(f.x - tw / 2 - 14, GY + 34, f.n);
      S.label(ctx, f.name, f.x + 8, GY + 34, 21, { color: INK, weight: 800 });
      S.label(ctx, f.sub, f.x, GY + 60, 16, { color: MUTED, weight: 700 });
    });
  }

  function card(x, y, w, h, title) {
    S.roundRect(ctx, x, y, w, h, 18, CARD);
    if (title) S.label(ctx, title, x + 22, y + 26, 15, { align: 'left', color: FAINT, weight: 800, track: 2 });
  }
  function dim(x0, y0, x1, y1, text, side = 'top') {
    ctx.save(); ctx.strokeStyle = 'rgba(242,238,246,0.55)'; ctx.fillStyle = 'rgba(242,238,246,0.55)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    const tick = (x, y) => { ctx.beginPath(); if (y0 === y1) { ctx.moveTo(x, y - 6); ctx.lineTo(x, y + 6); } else { ctx.moveTo(x - 6, y); ctx.lineTo(x + 6, y); } ctx.stroke(); };
    tick(x0, y0); tick(x1, y1);
    ctx.restore();
    if (y0 === y1) S.label(ctx, text, (x0 + x1) / 2, y0 + (side === 'top' ? -12 : 14), 13, { color: MUTED, weight: 800 });
    else S.label(ctx, text, x0 + (side === 'left' ? -10 : 10), (y0 + y1) / 2, 13, { color: MUTED, weight: 800, align: side === 'left' ? 'right' : 'left' });
  }

  function construction(x, y, w, h) {
    card(x, y, w, h, 'HEAD  ·  SCREEN 4:3');
    const s = 0.86, hh = UH * 1.1 * s, hw = 1.3 * hh, cx = x + w / 2 + 6, by = y + h - 40;
    HL.drawHead(ctx, cx, by, s, { face: 'neutral', t: 0.4, autoBlink: false, bloom: 0.3, look: { x: 0, y: 0 } });
    dim(cx - hw / 2, by + 16, cx + hw / 2, by + 16, '1.3 H', 'bottom');
    dim(cx + hw / 2 + 16, by - hh, cx + hw / 2 + 16, by, 'H', 'right');
    dim(cx - hw / 2 - 16, by - hh - 0.47 * hh, cx - hw / 2 - 16, by - hh, '0.45 H', 'left');
  }

  function props(x, y, w, h) {
    card(x, y, w, h, 'PROPS');
    [86, 230, 374, 518].forEach(px => S.roundRect(ctx, x + px - 64, y + 44, 128, h - 80, 14, '#2A3840'));
    HL.drawRemote(ctx, x + 78, y + 128, 2.3, { ang: -38, press: false });
    S.label(ctx, 'remote · red button', x + 86, y + h - 22, 13, { color: MUTED, weight: 800 });
    HL.drawClipboard(ctx, x + 230, y + 122, 1.5, { rot: 0, mark: 'APPROVED' });
    S.label(ctx, 'clipboard · form', x + 230, y + h - 22, 13, { color: MUTED, weight: 800 });
    HL.drawStamp(ctx, x + 374, y + 112, 1.6);
    S.label(ctx, 'rubber stamp', x + 374, y + h - 22, 13, { color: MUTED, weight: 800 });
    HL.drawBadge(ctx, x + 518, y + 72, 2.3);
    S.label(ctx, 'badge · lanyard', x + 518, y + h - 22, 13, { color: MUTED, weight: 800 });
  }

  function palette(x, y, w, h) {
    card(x, y, w, h, 'PALETTE');
    const sw = [
      ['case', COL.case], ['case shade', COL.caseShade], ['bezel / pumps', COL.bezel], ['screen', COL.screen],
      ['face line', COL.line], ['mint (signature)', COL.mint], ['blazer + skirt', COL.blazer], ['cloth shade', COL.blazerShade],
      ['blouse', COL.blouse], ['bow', COL.bow], ['skin', COL.skin], ['remote button', COL.red],
    ];
    const cols = 3, cw = (w - 40) / cols;
    sw.forEach(([n, c], i) => {
      const cx = x + 22 + (i % cols) * cw, cy = y + 52 + Math.floor(i / cols) * 44;
      S.roundRect(ctx, cx, cy, 30, 30, 8, c);
      S.label(ctx, n, cx + 40, cy + 9, 13, { align: 'left', color: INK, weight: 800 });
      S.label(ctx, c.toUpperCase(), cx + 40, cy + 25, 11, { align: 'left', color: MUTED, weight: 700 });
    });
  }

  function notes(x, y, w, h) {
    card(x, y, w, h, 'READ ON DARK SETS');
    const cr = (a, b) => S.color.contrast(a, b).toFixed(1);
    const L = [
      `blazer ${COL.blazer} vs room wall #1A2329  ${cr(COL.blazer, '#1A2329')} : 1`,
      `case ${COL.case} vs wall  ${cr(COL.case, '#1A2329')} : 1`,
      'screen light spills mint on collar + hands',
      'rim light option for torch-lit corridors',
      'mint ONLY on screen, lanyard, one dial',
    ];
    L.forEach((t, i) => S.label(ctx, t, x + 22, y + 58 + i * 30, 14, { align: 'left', color: i < 2 ? INK : MUTED, weight: 800 }));
  }

  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    bg(); header(); figures();
    const y = 830, h = 232;
    construction(40, y, 300, h);
    props(356, y, 600, h);
    palette(972, y, 520, h);
    notes(1508, y, W - 1548, h);
  };
})();
