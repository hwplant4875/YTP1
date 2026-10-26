// knight/sheet.js : GUESTS model sheet (three types idle + signature pose, the 404 knight, the horror variant,
// helm / prop / palette callouts, 2.4 W height line).
// SMALL=1 node render_sf.mjs core/lib_core.js,knight/knight.js,knight/sheet.js knights_sheet.png
(function () {
  'use strict';
  const cv = document.getElementById('c'), ctx = cv.getContext('2d'), S = window.SFX, K = window.KNIGHT, C = S.color;
  const W = cv.width, H = cv.height;
  const BG = '#1A2329', CARD = '#212C33', CARD2 = '#2A3840', INK = '#F2EEF6', MUTED = 'rgba(242,238,246,0.56)', FAINT = 'rgba(242,238,246,0.34)';
  const GOLD = 'rgba(255,200,90,0.75)';
  const SC = 0.8, GY = 716, UW = K.W * SC; // one W in px on this sheet
  const T0 = 0.35;
  const FIG = [
    { x: 186, n: '1', name: 'HAMMER', sub: 'idle · maul planted', o: { type: 'hammer', pose: 'idle' } },
    { x: 446, n: '2', name: 'HAMMER', sub: 'shoulders the maul', o: { type: 'hammer', pose: 'ready' } },
    { x: 628, n: '3', name: 'SPEAR', sub: 'idle · thin + tall', o: { type: 'spear', pose: 'idle' } },
    { x: 846, n: '4', name: 'SPEAR', sub: 'levels the spear', o: { type: 'spear', pose: 'ready', spearLen: 350 } },
    { x: 1116, n: '5', name: 'SHIELD', sub: 'idle · lantern', o: { type: 'shield', pose: 'idle' } },
    { x: 1342, n: '6', name: 'SHIELD', sub: 'lantern up · searching', o: { type: 'shield', pose: 'ready' } },
    { x: 1560, n: '7', name: '404 KNIGHT', sub: 'scratch · notebook · quill', o: { type: 'spear', pose: 'notebook', variant: 'k404' } },
    { x: 1790, n: '8', name: 'HORROR', sub: 'dark plate · cold slit line', o: { type: 'hammer', pose: 'idle', variant: 'horror', tilt: -4 } },
  ];

  function bg() {
    ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let x = 0; x < W; x += 40) ctx.fillRect(x, 0, 1, H);
    for (let y = 0; y < H; y += 40) ctx.fillRect(0, y, W, 1);
  }
  function header() {
    S.title(ctx, 'GUESTS', 56, 66, 70, { align: 'left', color: INK, track: 2 });
    S.label(ctx, 'faceless full-plate knights  ·  the adventurers of Monster HR', 330, 54, 22, { align: 'left', color: INK });
    S.label(ctx, 'model sheet  ·  all figures same scale  ·  W = chest width (180 px at s = 1)', 330, 84, 18, { align: 'left', color: MUTED, weight: 700 });
    // legend top-right
    S.label(ctx, 'acting = helm tilt · hands · posture · sweat · motion lines', W - 60, 54, 17, { align: 'right', color: MUTED, weight: 800 });
    S.label(ctx, 'the visor slit is pure #0B0C0F: nothing inside, ever', W - 60, 82, 17, { align: 'right', color: INK, weight: 800 });
  }
  function dashed(y, x0, x1, col, dash = [10, 8], lw = 2) {
    ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.setLineDash(dash);
    ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke(); ctx.restore();
  }
  function ruler() {
    const x = 46;
    ctx.fillStyle = 'rgba(242,238,246,0.3)'; ctx.fillRect(x, GY - 3.2 * UW, 2, 3.2 * UW);
    for (let i = 0; i <= 3; i++) {
      const y = GY - i * UW;
      ctx.fillRect(x - 6, y - 1, 14, 2);
      S.label(ctx, i + ' W', x + 14, y, 13, { align: 'left', color: FAINT, weight: 800 });
    }
    dashed(GY - 2.4 * UW, 70, W - 40, GOLD);
    S.label(ctx, 'knight 2.4 W  (helm dome)', 72, GY - 2.4 * UW - 14, 14, { align: 'left', color: 'rgba(255,214,130,0.95)', weight: 800 });
    dashed(GY - 3.1 * UW, 70, W - 40, 'rgba(242,238,246,0.18)', [4, 10]);
    S.label(ctx, 'Mimiku standing 3.1 W', 76, GY - 3.1 * UW - 14, 15, { align: 'left', color: FAINT, weight: 800 });
  }
  function badgeNum(x, y, n) {
    ctx.fillStyle = 'rgba(242,238,246,0.85)'; ctx.beginPath(); ctx.arc(x, y, 13, 0, Math.PI * 2); ctx.fill();
    S.label(ctx, n, x, y + 1, 16, { color: BG, weight: 900 });
  }
  function textW(t, font) { ctx.save(); ctx.font = font; const w = ctx.measureText(t).width; ctx.restore(); return w; }
  function figures() {
    ctx.fillStyle = 'rgba(242,238,246,0.12)'; ctx.fillRect(40, GY, W - 80, 2);
    // horror gets a darker backing so the cold line reads as light
    const hx = FIG[7].x;
    const g = ctx.createRadialGradient(hx, GY - 200, 20, hx, GY - 200, 260);
    g.addColorStop(0, 'rgba(6,8,10,0.75)'); g.addColorStop(1, 'rgba(6,8,10,0)');
    ctx.fillStyle = g; ctx.fillRect(hx - 280, GY - 470, 560, 480);
    FIG.forEach(f => {
      K.draw(ctx, f.x, GY, SC, Object.assign({ t: T0 }, f.o));
      const tw = textW(f.name, '800 21px Nunito');
      badgeNum(f.x - tw / 2 - 14, GY + 34, f.n);
      S.label(ctx, f.name, f.x + 8, GY + 34, 21, { color: INK, weight: 800 });
      S.label(ctx, f.sub, f.x, GY + 60, 15, { color: MUTED, weight: 700 });
    });
  }

  function card(x, y, w, h, title, col = CARD) {
    S.roundRect(ctx, x, y, w, h, 18, col);
    if (title) S.label(ctx, title, x + 22, y + 26, 15, { align: 'left', color: FAINT, weight: 800, track: 2 });
  }

  function helms(x, y, w, h) {
    card(x, y, w, h, 'HELMS  ·  FACELESS');
    const by = y + h - 34, s = 0.84;
    [['hammer', 'bucket great helm', x + 92], ['spear', 'pointed sugarloaf', x + 244], ['shield', 'fluted crest + plume', x + 404]].forEach(([ty, nm, hx], i) => {
      K.drawHelm(ctx, hx, by - 4, s, { type: ty, tilt: [-4, 6, -8][i], t: T0 });
      S.label(ctx, nm, hx, by + 14, 13, { color: MUTED, weight: 800 });
    });
  }
  function marks404(x, y, w, h) {
    card(x, y, w, h, '404 KNIGHT  ·  RECURRING');
    const by = y + h - 34;
    K.drawHelm(ctx, x + 90, by - 4, 0.84, { type: 'spear', variant: 'k404', t: T0, tilt: -6 });
    S.label(ctx, 'scratch, left of the helm', x + 90, by + 14, 13, { color: MUTED, weight: 800 });
    K.drawProp(ctx, 'notebook', x + 226, y + 124, 1.2, { w: 62, h: 78, r: -0.06 });
    K.drawProp(ctx, 'quill', x + 282, y + 186, 1.1, { a: -Math.PI / 2 + 0.3, len: 64 });
    S.label(ctx, 'notebook + quill', x + 236, by + 14, 13, { color: MUTED, weight: 800 });
  }
  function horror(x, y, w, h) {
    card(x, y, w, h, 'HORROR', '#15191D');
    const by = y + h - 34;
    K.drawHelm(ctx, x + w / 2, by - 4, 0.84, { type: 'hammer', variant: 'horror', t: T0, tilt: 4 });
    S.label(ctx, 'one cold line, no eyes', x + w / 2, by + 14, 13, { color: MUTED, weight: 800 });
  }
  function props(x, y, w, h) {
    card(x, y, w, h, 'PROPS');
    ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
    K.drawProp(ctx, 'hammer', x + 26, y + 172, 0.6, { a: -0.5 });
    S.label(ctx, 'maul', x + 92, y + h - 22, 13, { color: MUTED, weight: 800 });
    K.drawProp(ctx, 'spear', x + 176, y + 196, 0.5, { a: -Math.PI / 2 + 0.42, len: 290, t: 0.35 });
    S.label(ctx, 'winged spear', x + 214, y + h - 22, 13, { color: MUTED, weight: 800 });
    K.drawProp(ctx, 'shield', x + 300, y + 124, 0.7, { r: 0.06 });
    S.label(ctx, 'heater · key', x + 300, y + h - 22, 13, { color: MUTED, weight: 800 });
    K.drawProp(ctx, 'lantern', x + 380, y + 56, 1.05, { swing: 0.05 });
    S.label(ctx, 'lantern', x + 380, y + h - 22, 13, { color: MUTED, weight: 800 });
    ctx.restore();
  }
  function palette(x, y, w, h) {
    card(x, y, w, h, 'PALETTE  ·  CONTRAST');
    const N = K.COL.normal, Hh = K.COL.horror;
    const sw = [
      ['plate', N.plate], ['shade', N.shade], ['edge / rim', N.light],
      ['slit', N.slit], ['leather', N.leather], ['sash', K.COL.cloth.hammer[0]],
      ['cape', K.COL.cloth.spear[0]], ['plume', K.COL.cloth.shield[0]], ['shield', K.COL.shieldField[0]],
      ['horror', Hh.plate], ['accent', Hh.accent], ['cold line', Hh.slitLight],
    ];
    const cols = 3, cw = (w - 30) / cols;
    sw.forEach(([n, c], i) => {
      const cx = x + 20 + (i % cols) * cw, cy = y + 44 + Math.floor(i / cols) * 36;
      S.roundRect(ctx, cx, cy, 24, 24, 6, c);
      ctx.save(); ctx.strokeStyle = 'rgba(242,238,246,0.22)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.roundRect(cx + 0.5, cy + 0.5, 23, 23, 6); ctx.stroke(); ctx.restore();
      S.label(ctx, n, cx + 31, cy + 7, 12, { align: 'left', color: INK, weight: 800 });
      S.label(ctx, c.toUpperCase(), cx + 31, cy + 20, 10, { align: 'left', color: MUTED, weight: 700 });
    });
    const cr = (a, b) => C.contrast(a, b).toFixed(2);
    S.label(ctx, `plate vs room wall #1A2329   ${cr(N.plate, '#1A2329')} : 1`, x + 20, y + h - 40, 12, { align: 'left', color: INK, weight: 800 });
    S.label(ctx, `plate vs corridor stone #3D3946   ${cr(N.plate, '#3D3946')} : 1  →  rim on`, x + 20, y + h - 20, 12, { align: 'left', color: MUTED, weight: 800 });
  }

  window.draw = () => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    bg(); header(); ruler(); figures();
    const y = 818, h = 242;
    helms(40, y, 500, h);
    marks404(556, y, 330, h);
    horror(902, y, 186, h);
    props(1104, y, 430, h);
    palette(1550, y, W - 1590, h);
  };
})();
