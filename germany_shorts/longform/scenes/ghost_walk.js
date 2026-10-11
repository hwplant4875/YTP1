// Ghost walk: inside a sealed East Berlin U-Bahn station (Rosenthaler Platz style: tiled walls, side
// platforms, riveted steel columns between the tracks), frozen since August 1961.
// shots (?shot=):
//   walk  (12 s)   first-person torch walk down the dark platform. 0-2.4 beam on the floor ahead, 2.4-5 beam lifts
//                  into the dark towards two almost-dead amber bulbs, 5-7.6 a stopped platform clock, then a wall
//                  calendar "AUGUST 1961", 7.6-12+ the beam lingers on a row of faded, peeling 1961 posters
//                  (detergent, Kino, Ostsee travel, cigarettes, BVG notice, beer).
//   wire  (12.7 s) four clean beats: 0-3 low glide along concertina barbed wire coils on the platform edge;
//                  3-5.9 an emergency exit ("NOTAUSGANG") being welded shut: arc, sparks, amber seams cooling;
//                  5.9-8.6 a steel roller shutter lowers over the track tunnel; 8.6+ light barriers across the
//                  track switch on one by one, one beam flickers as if something crossed it.
//   line  (8.7 s)  train-headlight POV through the tunnel: a hand-painted white border line (wall, ceiling, wall,
//                  drips, "SEKTORENGRENZE" stencil). Crossing it (~5.2 s) the warm work lamps give way to cold
//                  grey ones and a border guard stands far ahead.
//   years (3 s)    time-lapse on a bench under a peeling poster: dust settles on the bench, the bulb stutters,
//                  the poster curls away from the wall, cobweb grows.
import { AMBER, concreteTex, canvasTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, borderGuard, smooth } from './look.js';

const L = 120, HW = 8, HT = 5.4, PX = HW - 3.6;   // platform edge at x = 4.4
const TORCH = 0xffd6a6, COLD = 0xc9d2da;

// hermite path through timed keys; keeps moving at the last velocity after the final key
function path(keys) {
  const n = keys.length;
  const tan = keys.map((k, i) => {
    const a = keys[Math.max(0, i - 1)], b = keys[Math.min(n - 1, i + 1)], dt = b[0] - a[0];
    return k[1].map((_, j) => dt > 0 ? (b[1][j] - a[1][j]) / dt : 0);
  });
  return (t) => {
    if (t <= keys[0][0]) return keys[0][1].slice();
    if (t >= keys[n - 1][0]) { const k = keys[n - 1]; return k[1].map((v, j) => v + tan[n - 1][j] * (t - k[0]) * 0.6); }
    let i = 0; while (keys[i + 1][0] < t) i++;
    const [t0, p0] = keys[i], [t1, p1] = keys[i + 1], h = t1 - t0, s = (t - t0) / h;
    const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
    return p0.map((v, j) => h00 * v + h10 * h * tan[i][j] + h01 * p1[j] + h11 * h * tan[i + 1][j]);
  };
}
const nz = (t, s) => Math.sin(t * 1.31 + s) * 0.5 + Math.sin(t * 2.73 + s * 2.1) * 0.3 + Math.sin(t * 0.61 + s * 3.7) * 0.6;
const hash = (k) => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// ---------------------------------------------------------------- textures
function tiles(THREE, seed, repeat, tone = 168) {
  const r = rng(seed);
  const map = canvasTex(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = 'rgb(122,119,112)'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 64) {
      const v = tone + r() * 24 - (r() < 0.05 ? 38 : 0);
      g.fillStyle = `rgb(${v},${v - 3},${v - 10})`; g.fillRect(x + 2, y + 2, 60, 28);
      g.fillStyle = `rgba(255,252,240,${0.05 + r() * 0.06})`; g.fillRect(x + 4, y + 4, 54, 5);
      if (r() < 0.06) { g.fillStyle = `rgba(60,55,48,${0.6 + r() * 0.4})`; g.beginPath(); g.ellipse(x + 4 + r() * 56, y + 3 + r() * 24, 2 + r() * 7, 1.5 + r() * 4, r() * 3, 0, 7); g.fill(); }
      if (r() < 0.03) { g.strokeStyle = 'rgba(40,38,34,0.7)'; g.lineWidth = 1; g.beginPath(); g.moveTo(x + r() * 60, y + 2); g.lineTo(x + r() * 60, y + 30); g.stroke(); }
    }
    for (let i = 0; i < 170; i++) {
      const x = r() * w, len = 80 + r() * 700, a = 0.1 + r() * 0.3;
      const grd = g.createLinearGradient(0, 0, 0, len);
      grd.addColorStop(0, `rgba(34,30,24,${a})`); grd.addColorStop(1, 'rgba(34,30,24,0)');
      g.fillStyle = grd; g.fillRect(x, 0, 1 + r() * 7, len);
    }
    for (let i = 0; i < 40; i++) {
      const x = r() * w, y = r() * h, rad = 30 + r() * 140;
      const grd = g.createRadialGradient(x, y, 0, x, y, rad);
      grd.addColorStop(0, `rgba(40,34,26,${0.1 + r() * 0.18})`); grd.addColorStop(1, 'rgba(40,34,26,0)');
      g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
  }, repeat);
  const normal = normalFromHeight(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff';
    for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 64) g.fillRect(x + 2, y + 2, 60, 28);
  }, 1.2, repeat);
  return { map, normal };
}

function dustyFloor(THREE, repeat, seed) {
  const r = rng(seed);
  return canvasTex(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = 'rgb(112,109,103)'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 14000; i++) { const v = 70 + r() * 90; g.fillStyle = `rgba(${v},${v - 2},${v - 6},${0.1 + r() * 0.15})`; g.fillRect(r() * w, r() * h, 1 + r() * 4, 1 + r() * 4); }
    for (let i = 0; i < 70; i++) { const x = r() * w, y = r() * h, rad = 20 + r() * 120; const grd = g.createRadialGradient(x, y, 0, x, y, rad);
      grd.addColorStop(0, `rgba(30,27,22,${0.15 + r() * 0.3})`); grd.addColorStop(1, 'rgba(30,27,22,0)'); g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); }
    // slab joints
    g.strokeStyle = 'rgba(30,28,25,0.6)'; g.lineWidth = 2;
    for (let y = 0; y < h; y += 256) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    for (let i = 0; i < 30; i++) { g.strokeStyle = `rgba(35,32,28,${0.3 + r() * 0.4})`; g.lineWidth = 1; g.beginPath(); let x = r() * w, y = r() * h; g.moveTo(x, y);
      for (let k = 0; k < 6; k++) { x += (r() - 0.5) * 60; y += (r() - 0.5) * 60; g.lineTo(x, y); } g.stroke(); }
  }, repeat);
}

// age a printed sheet: yellowed, faded, stained, scuffed, torn edges (alpha)
function agePaper(g, w, h, r, { tear = 1, fade = 0.35 } = {}) {
  g.globalCompositeOperation = 'multiply';
  g.fillStyle = 'rgb(236,222,190)'; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'screen';
  g.fillStyle = `rgba(120,112,98,${fade})`; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'source-over';
  for (let i = 0; i < 9; i++) { const x = r() * w, y = h * (0.3 + r() * 0.8), rad = 40 + r() * 160; const grd = g.createRadialGradient(x, y, rad * 0.6, x, y, rad);
    grd.addColorStop(0, 'rgba(120,96,60,0.0)'); grd.addColorStop(0.85, `rgba(110,84,50,${0.12 + r() * 0.2})`); grd.addColorStop(1, 'rgba(110,84,50,0)'); g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); }
  const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, 'rgba(60,50,36,0.25)'); grd.addColorStop(0.3, 'rgba(60,50,36,0)'); grd.addColorStop(0.85, 'rgba(60,50,36,0)'); grd.addColorStop(1, 'rgba(60,50,36,0.35)');
  g.fillStyle = grd; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 1500; i++) { const v = 60 + r() * 120; g.fillStyle = `rgba(${v},${v - 8},${v - 20},${r() * 0.2})`; g.fillRect(r() * w, r() * h, 1 + r() * 5, 1 + r() * 2); }
  for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(250,240,220,${0.15 + r() * 0.25})`; g.lineWidth = 0.6 + r() * 1.5; g.beginPath(); const x = r() * w, y = r() * h; g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 120, y + (r() - 0.5) * 40); g.stroke(); }
  // folds / creases
  for (let i = 0; i < 3; i++) { const y = h * (0.2 + r() * 0.6); g.fillStyle = 'rgba(255,250,235,0.12)'; g.fillRect(0, y, w, 2); g.fillStyle = 'rgba(40,32,22,0.15)'; g.fillRect(0, y + 2, w, 2); }
  // torn chunks: punch alpha holes along the edges
  g.globalCompositeOperation = 'destination-out';
  const chunks = Math.floor(3 + r() * 5 * tear);
  for (let i = 0; i < chunks; i++) {
    const side = Math.floor(r() * 4), s = r();
    let x = side === 0 ? s * w : side === 1 ? w : side === 2 ? s * w : 0, y = side === 0 ? 0 : side === 1 ? s * h : side === 2 ? h : s * h;
    g.beginPath(); g.moveTo(x, y); const n = 7 + Math.floor(r() * 6), rad = (20 + r() * 70) * tear;
    for (let k = 0; k <= n; k++) { const a = k / n * Math.PI * 2; const rr = rad * (0.5 + r() * 0.7); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    g.closePath(); g.fill();
  }
  g.globalCompositeOperation = 'source-over';
}

function txt(g, s, x, y, font, fill, align = 'center') { g.font = font; g.textAlign = align; g.textBaseline = 'alphabetic'; g.fillStyle = fill; g.fillText(s, x, y); }

function posterTex(THREE, kind, seed) {
  const r = rng(seed);
  return canvasTex(THREE, 640, 900, (g, w, h) => {
    const C = '"DejaVu Sans Condensed", sans-serif', S = '"DejaVu Serif", serif';
    if (kind === 'lumin') {
      const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#1f4f8f'); gr.addColorStop(1, '#9cc4e6'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.save(); g.translate(w / 2, 420);
      for (let i = 0; i < 24; i++) { g.rotate(Math.PI / 12); g.fillStyle = i % 2 ? 'rgba(255,240,170,0.35)' : 'rgba(255,255,255,0.12)'; g.beginPath(); g.moveTo(0, 0); g.lineTo(-60, -700); g.lineTo(60, -700); g.fill(); }
      g.restore();
      // the box
      g.fillStyle = '#e9772a'; g.fillRect(190, 420, 260, 330); g.fillStyle = '#b8541a'; g.beginPath(); g.moveTo(450, 420); g.lineTo(510, 380); g.lineTo(510, 700); g.lineTo(450, 750); g.fill();
      g.fillStyle = '#f6a650'; g.beginPath(); g.moveTo(190, 420); g.lineTo(250, 380); g.lineTo(510, 380); g.lineTo(450, 420); g.fill();
      g.fillStyle = '#fff'; g.beginPath(); g.arc(320, 520, 80, 0, 7); g.fill();
      txt(g, 'LUMIN', 320, 540, `bold 54px ${C}`, '#1f4f8f');
      txt(g, 'Waschpulver', 320, 680, `italic 30px ${S}`, '#fff');
      // headline
      g.lineWidth = 12; g.strokeStyle = '#13294a'; g.font = `bold 170px ${C}`; g.textAlign = 'center'; g.strokeText('LUMIN', w / 2, 200);
      txt(g, 'LUMIN', w / 2, 200, `bold 170px ${C}`, '#ffffff');
      txt(g, 'wäscht strahlend weiß!', w / 2, 290, `bold italic 46px ${S}`, '#fff3c4');
      g.fillStyle = '#13294a'; g.fillRect(0, 790, w, 110); txt(g, 'Für die ganze Wäsche der Familie', w / 2, 858, `bold 34px ${C}`, '#fff');
    } else if (kind === 'kino') {
      g.fillStyle = '#16120f'; g.fillRect(0, 0, w, h);
      const gr = g.createRadialGradient(320, 430, 10, 320, 430, 330); gr.addColorStop(0, '#e8c27a'); gr.addColorStop(1, 'rgba(232,194,122,0)'); g.fillStyle = gr; g.fillRect(0, 100, w, 700);
      // two faces in profile, close together
      g.fillStyle = '#1b1612';
      g.beginPath(); g.ellipse(250, 430, 95, 120, -0.2, 0, 7); g.fill(); g.beginPath(); g.ellipse(395, 410, 90, 118, 0.25, 0, 7); g.fill();
      g.fillRect(170, 520, 160, 300); g.fillRect(330, 500, 160, 320);
      g.fillStyle = '#e8c27a'; g.beginPath(); g.ellipse(322, 360, 14, 40, 0.1, 0, 7); g.fill();
      txt(g, 'KINO', w / 2, 140, `bold 150px ${C}`, '#f0e2c0');
      txt(g, 'Sterne über der Spree', w / 2, 705, `bold italic 50px ${S}`, '#f4d99a');
      txt(g, 'Ein DEFA-Film', w / 2, 750, `24px ${S}`, '#cdbb98');
      g.fillStyle = '#f0e2c0'; g.fillRect(40, 780, w - 80, 3);
      txt(g, 'Täglich 16.00 · 18.30 · 21.00 Uhr', w / 2, 830, `bold 32px ${C}`, '#f0e2c0');
      txt(g, 'Lichtspiele am Rosenthaler Platz', w / 2, 872, `26px ${C}`, '#cdbb98');
    } else if (kind === 'ostsee') {
      const gr = g.createLinearGradient(0, 0, 0, 520); gr.addColorStop(0, '#f1b04c'); gr.addColorStop(1, '#fbe6b0'); g.fillStyle = gr; g.fillRect(0, 0, w, 520);
      g.fillStyle = '#fff4c8'; g.beginPath(); g.arc(440, 330, 90, 0, 7); g.fill();
      g.fillStyle = '#2f6a8c'; g.fillRect(0, 470, w, 220);
      g.strokeStyle = 'rgba(255,255,255,0.7)'; g.lineWidth = 4;
      for (let y = 500; y < 680; y += 26) { g.beginPath(); for (let x = 0; x <= w; x += 10) g.lineTo(x, y + Math.sin(x * 0.05 + y) * 5); g.stroke(); }
      g.fillStyle = '#e8d29a'; g.beginPath(); g.moveTo(0, 690); g.quadraticCurveTo(320, 640, 640, 700); g.lineTo(640, 900); g.lineTo(0, 900); g.fill();
      // sail boat
      g.fillStyle = '#5a3a20'; g.beginPath(); g.moveTo(130, 540); g.lineTo(250, 540); g.lineTo(230, 565); g.lineTo(150, 565); g.fill();
      g.fillStyle = '#fbf6ea'; g.beginPath(); g.moveTo(192, 535); g.lineTo(192, 380); g.lineTo(255, 530); g.fill(); g.beginPath(); g.moveTo(186, 535); g.lineTo(186, 400); g.lineTo(140, 530); g.fill();
      g.strokeStyle = '#3a2c20'; g.lineWidth = 4; for (const [x, y] of [[300, 230], [350, 260], [270, 290]]) { g.beginPath(); g.moveTo(x - 18, y - 6); g.quadraticCurveTo(x - 8, y - 12, x, y); g.quadraticCurveTo(x + 8, y - 12, x + 18, y - 6); g.stroke(); }
      // beach chair
      g.fillStyle = '#c96a32'; g.fillRect(430, 720, 120, 110); g.fillStyle = '#7a4424'; g.beginPath(); g.ellipse(490, 722, 64, 40, 0, Math.PI, 0); g.fill();
      for (let i = 0; i < 5; i++) { g.fillStyle = i % 2 ? '#f3e2c0' : '#c96a32'; g.fillRect(434 + i * 23, 730, 20, 96); }
      txt(g, 'Reisen an die', w / 2, 92, `italic bold 54px ${S}`, '#5a2e12');
      txt(g, 'OSTSEE', w / 2, 210, `bold 150px ${C}`, '#2a3f5a');
      txt(g, 'Ferienplätze Sommer 1961', 220, 790, `bold 30px ${C}`, '#3a2a18');
      txt(g, 'Reisebüro Berlin', 220, 835, `30px ${S}`, '#3a2a18');
    } else if (kind === 'oval') {
      g.fillStyle = '#c9a36a'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 18; i++) { g.fillStyle = i % 2 ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.05)'; g.fillRect(i * 36, 0, 36, h); }
      // pack
      g.fillStyle = '#efe6d2'; g.fillRect(150, 360, 300, 400); g.fillStyle = '#c8bda4'; g.beginPath(); g.moveTo(450, 360); g.lineTo(500, 330); g.lineTo(500, 720); g.lineTo(450, 760); g.fill();
      g.fillStyle = '#7a2f1f'; g.beginPath(); g.ellipse(300, 540, 120, 75, 0, 0, 7); g.fill(); g.strokeStyle = '#d9b06a'; g.lineWidth = 6; g.stroke();
      txt(g, 'OVAL', 300, 562, `bold 70px ${S}`, '#f3e0b0');
      // cigarettes sticking out with smoke
      g.fillStyle = '#fbf8f0'; g.fillRect(200, 300, 34, 70); g.fillRect(250, 280, 34, 90); g.fillStyle = '#d8a060'; g.fillRect(250, 280, 34, 20);
      g.strokeStyle = 'rgba(255,255,255,0.6)'; g.lineWidth = 8; g.beginPath(); g.moveTo(217, 296);
      for (let k = 0; k < 10; k++) g.quadraticCurveTo(217 + (k % 2 ? 50 : -50), 270 - k * 22, 217 + (k % 2 ? 10 : -10), 255 - k * 22); g.stroke();
      txt(g, 'OVAL', w / 2, 190, `bold italic 160px ${S}`, '#5a1e12');
      txt(g, 'die Milde mit dem vollen Aroma', w / 2, 830, `italic 34px ${S}`, '#3b1a10');
      txt(g, 'Eine Zigarette von Format', w / 2, 872, `bold 26px ${C}`, '#3b1a10');
    } else if (kind === 'bvg') {
      g.fillStyle = '#efe9da'; g.fillRect(0, 0, w, h);
      g.strokeStyle = '#222'; g.lineWidth = 6; g.strokeRect(20, 20, w - 40, h - 40);
      g.fillStyle = '#222'; g.beginPath(); g.arc(110, 110, 60, 0, 7); g.fill(); txt(g, 'BVG', 110, 128, `bold 44px ${C}`, '#efe9da');
      txt(g, 'Berliner', 190, 92, `bold 38px ${C}`, '#222', 'left'); txt(g, 'Verkehrs-Betriebe', 190, 140, `bold 38px ${C}`, '#222', 'left');
      g.fillRect(40, 190, w - 80, 4);
      txt(g, 'Bekanntmachung', w / 2, 270, `bold 58px ${S}`, '#111');
      const lines = ['Ab 1. August 1961 verkehren die Züge der', 'Linie D (Gesundbrunnen – Leinestraße)', 'werktags von 4.30 Uhr bis 1.00 Uhr', 'im Abstand von 5 Minuten.', '', 'Fahrgäste werden gebeten, den Anweisungen', 'des Betriebspersonals Folge zu leisten', 'und die Bahnsteigkante freizuhalten.', '', 'Das Rauchen auf den Bahnsteigen', 'ist nicht gestattet.'];
      lines.forEach((s, i) => txt(g, s, 60, 340 + i * 38, `27px ${S}`, '#222', 'left'));
      txt(g, 'Berlin, im Juli 1961', 60, 820, `italic 28px ${S}`, '#222', 'left'); txt(g, 'Die Direktion', w - 60, 820, `italic 28px ${S}`, '#222', 'right');
    } else if (kind === 'pils') {
      g.fillStyle = '#26402e'; g.fillRect(0, 0, w, h);
      const gr = g.createRadialGradient(320, 500, 20, 320, 500, 300); gr.addColorStop(0, 'rgba(240,200,110,0.6)'); gr.addColorStop(1, 'rgba(240,200,110,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.fillStyle = '#e2a73c'; g.beginPath(); g.moveTo(230, 330); g.lineTo(410, 330); g.lineTo(380, 760); g.lineTo(260, 760); g.fill();
      g.fillStyle = '#fbf3de'; g.beginPath(); g.ellipse(320, 330, 100, 40, 0, 0, 7); g.fill(); g.beginPath(); g.arc(270, 310, 40, 0, 7); g.arc(330, 300, 45, 0, 7); g.arc(380, 315, 38, 0, 7); g.fill();
      for (let i = 0; i < 30; i++) { g.fillStyle = 'rgba(255,240,200,0.6)'; g.beginPath(); g.arc(260 + r() * 120, 380 + r() * 360, 2 + r() * 4, 0, 7); g.fill(); }
      txt(g, 'Spree-Pils', w / 2, 170, `bold italic 110px ${S}`, '#f2dca0');
      txt(g, 'Das Bier für Berlin', w / 2, 240, `bold 42px ${C}`, '#f2dca0');
      txt(g, 'Gebraut in Berlin seit 1872', w / 2, 850, `28px ${S}`, '#e0cfa0');
    }
    agePaper(g, w, h, r, { tear: kind === 'bvg' ? 0.6 : 1, fade: 0.3 + r() * 0.15 });
  });
}

function calendarTex(THREE) {
  const r = rng(61);
  return canvasTex(THREE, 512, 768, (g, w, h) => {
    const C = '"DejaVu Sans Condensed", sans-serif', S = '"DejaVu Serif", serif';
    g.fillStyle = '#f2ecdc'; g.fillRect(0, 0, w, h);
    // picture of the month: a woodcut-style view of the Fernsehturm-less skyline with a church
    g.fillStyle = '#8a7a60'; g.fillRect(30, 30, w - 60, 230);
    g.fillStyle = '#3a3226'; g.beginPath(); g.moveTo(30, 260);
    for (let x = 30; x <= w - 30; x += 16) g.lineTo(x, 200 - (hash(x) * 50) - (x > 300 && x < 330 ? 110 : 0)); g.lineTo(w - 30, 260); g.fill();
    g.fillStyle = '#d8c69a'; g.beginPath(); g.arc(140, 100, 34, 0, 7); g.fill();
    txt(g, 'AUGUST', w / 2, 345, `bold 92px ${C}`, '#1c1a16');
    txt(g, '1961', w / 2, 425, `bold 70px ${C}`, '#1c1a16');
    const days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
    days.forEach((d, i) => txt(g, d, 62 + i * 65, 480, `bold 24px ${C}`, i === 6 ? '#8a2a1a' : '#333'));
    for (let d = 1; d <= 31; d++) {
      const idx = d + 0, col = (idx) % 7, row = Math.floor((idx) / 7);   // 1 Aug 1961 = Tuesday
      txt(g, String(d), 62 + col * 65, 525 + row * 44, `${col === 6 ? 'bold ' : ''}28px ${S}`, col === 6 ? '#8a2a1a' : '#222');
    }
    // the last day anyone tore off: the 13th ringed in pencil
    const c13 = (13) % 7, r13 = Math.floor(13 / 7);
    g.strokeStyle = 'rgba(40,40,40,0.85)'; g.lineWidth = 3; g.beginPath(); g.ellipse(62 + c13 * 65, 516 + r13 * 44, 30, 21, -0.1, 0, 7); g.stroke();
    txt(g, 'Kalender des Berliner Verlags', w / 2, 750, `italic 18px ${S}`, '#555');
    agePaper(g, w, h, r, { tear: 0.35, fade: 0.25 });
  });
}

function clockTex(THREE) {
  return canvasTex(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = '#16140f'; g.fillRect(0, 0, w, h);
    const gr = g.createRadialGradient(256, 256, 0, 256, 256, 250); gr.addColorStop(0, '#efebe0'); gr.addColorStop(0.9, '#d9d3c2'); gr.addColorStop(1, '#a8a190');
    g.fillStyle = gr; g.beginPath(); g.arc(256, 256, 246, 0, 7); g.fill();
    g.fillStyle = '#141414';
    for (let i = 0; i < 60; i++) { g.save(); g.translate(256, 256); g.rotate(i * Math.PI / 30); if (i % 5 === 0) g.fillRect(-9, -232, 18, 62); else g.fillRect(-3, -232, 6, 20); g.restore(); }
    g.font = 'bold 22px "DejaVu Sans Condensed", sans-serif'; g.textAlign = 'center'; g.fillText('BVG', 256, 180);
    const r = rng(9);
    for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(60,50,30,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 2 + r() * 6, 2 + r() * 6); }
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, 'rgba(80,66,40,0.35)'); grd.addColorStop(0.5, 'rgba(80,66,40,0)'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
    // cracked glass
    g.strokeStyle = 'rgba(255,255,255,0.55)'; g.lineWidth = 1.5;
    for (let k = 0; k < 7; k++) { g.beginPath(); g.moveTo(330, 140); let x = 330, y = 140; const a = k * 0.9 + 0.3; for (let s = 0; s < 6; s++) { x += Math.cos(a + (r() - 0.5) * 0.7) * 26; y += Math.sin(a + (r() - 0.5) * 0.7) * 26; g.lineTo(x, y); } g.stroke(); }
  });
}

function signTex(THREE) {
  return canvasTex(THREE, 1536, 256, (g, w, h) => {
    g.fillStyle = '#e6e1d2'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#1a1a1a'; g.lineWidth = 14; g.strokeRect(10, 10, w - 20, h - 20);
    txt(g, 'Rosenthaler Platz', w / 2, 170, 'bold 132px "DejaVu Sans", sans-serif', '#151515');
    const r = rng(4);
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(60,46,28,${0.3 + r() * 0.5})`; g.beginPath(); g.arc(r() * w, r() * h, 2 + r() * 9, 0, 7); g.fill(); }  // enamel chips
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(50,40,26,0.35)'); gr.addColorStop(1, 'rgba(50,40,26,0.05)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  });
}

function newspaperTex(THREE) {
  const r = rng(77);
  return canvasTex(THREE, 512, 700, (g, w, h) => {
    g.fillStyle = '#e4dccb'; g.fillRect(0, 0, w, h);
    txt(g, 'ABENDPOST', w / 2, 70, 'bold 64px "DejaVu Serif", serif', '#151515');
    txt(g, 'Sonnabend, 12. August 1961 · 15 Pf', w / 2, 100, '18px "DejaVu Serif", serif', '#222');
    g.fillStyle = '#151515'; g.fillRect(20, 112, w - 40, 3);
    txt(g, 'Ferienverkehr', w / 2, 170, 'bold 52px "DejaVu Sans Condensed", sans-serif', '#151515');
    txt(g, 'in der ganzen Stadt', w / 2, 215, 'bold 34px "DejaVu Sans Condensed", sans-serif', '#151515');
    g.fillStyle = '#6a655c'; g.fillRect(30, 240, 220, 150);
    for (let c = 0; c < 3; c++) for (let l = 0; l < 30; l++) { const x = c === 0 ? 30 : 30 + c * 157, y = c === 0 && l < 9 ? -1 : 250 + l * 14; if (y < 0) continue; g.fillStyle = 'rgba(30,30,30,0.6)'; g.fillRect(x, y, 140 * (0.7 + r() * 0.3), 5); }
    agePaper(g, w, h, r, { tear: 0.5, fade: 0.2 });
  });
}

function backingTex(THREE, seed) {
  const r = rng(seed);
  return canvasTex(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = '#5d5850'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 26; i++) { const v = 120 + r() * 80; g.fillStyle = `rgba(${v},${v - 6},${v - 18},${0.4 + r() * 0.5})`; g.beginPath(); const x = r() * w, y = r() * h; g.moveTo(x, y);
      for (let k = 0; k < 8; k++) g.lineTo(x + (r() - 0.5) * 140, y + (r() - 0.5) * 140); g.fill(); }
    for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(30,28,24,${r() * 0.2})`; g.fillRect(r() * w, r() * h, 2, 2); }
  });
}

// poster mesh whose corner can peel away from the wall (rolls on a small cylinder)
function peelPoster(THREE, map, w, h, corner = [1, -1]) {
  const geo = new THREE.PlaneGeometry(w, h, 24, 32);
  const base = geo.attributes.position.array.slice();
  const mat = new THREE.MeshStandardMaterial({ map, roughness: 0.92, alphaTest: 0.5, side: THREE.DoubleSide });
  mat.onBeforeCompile = (s) => {
    s.fragmentShader = s.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n if (!gl_FrontFacing) diffuseColor.rgb = vec3(0.62, 0.58, 0.5) * (0.8 + 0.2 * diffuseColor.a);');
  };
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true; mesh.receiveShadow = true;
  const [cx, cy] = corner, c = [cx * w / 2, cy * h / 2];
  const dl = Math.hypot(1, 0.8), dn = [-cx / dl, -cy * 0.8 / dl];
  mesh.userData.setPeel = (A) => {
    const p = geo.attributes.position.array;
    const R = 0.05 + 0.12 * A, phiM = Math.PI * 0.95;
    for (let i = 0; i < p.length; i += 3) {
      const x = base[i], y = base[i + 1];
      const s = (x - c[0]) * dn[0] + (y - c[1]) * dn[1];
      let sp = s, z = 0;
      if (A > 0 && s < A) {
        const e = A - s, phi = e / R;
        if (phi <= phiM) { sp = A - R * Math.sin(phi); z = R * (1 - Math.cos(phi)); }
        else { const rem = e - R * phiM; sp = A - R * Math.sin(phiM) - rem * Math.cos(phiM); z = R * (1 - Math.cos(phiM)) + rem * Math.sin(phiM); }
      }
      p[i] = x + dn[0] * (sp - s); p[i + 1] = y + dn[1] * (sp - s); p[i + 2] = z;
    }
    geo.attributes.position.needsUpdate = true; geo.computeVertexNormals();
  };
  return mesh;
}

// dust motes that only show where a light cone (torch / headlight) passes through them
function dustCloud(THREE, n, min, max, seed, size, H, fov, color = 0xffdcb0) {
  const r = rng(seed), pos = new Float32Array(n * 3), sd = new Float32Array(n);
  for (let i = 0; i < n; i++) { for (let j = 0; j < 3; j++) pos[i * 3 + j] = min[j] + r() * (max[j] - min[j]); sd[i] = r() * 100; }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('seed', new THREE.BufferAttribute(sd, 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 }, scale: { value: H / 2 / Math.tan(fov * Math.PI / 360) }, size: { value: size }, color: { value: new THREE.Color(color) },
      lp: { value: [new THREE.Vector3(), new THREE.Vector3()] }, ld: { value: [new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, -1)] },
      lc: { value: [0.95, 0.95] }, li: { value: [0, 0] }, amb: { value: 0.0 }, fall: { value: 0 }, ymin: { value: min[1] }, yh: { value: max[1] - min[1] },
    },
    vertexShader: `uniform float time, scale, size, amb, fall, ymin, yh; uniform vec3 lp[2]; uniform vec3 ld[2]; uniform float lc[2]; uniform float li[2];
      attribute float seed; varying float vB;
      void main(){
        vec3 p = position;
        p.x += sin(time*0.13 + seed)*0.25; p.z += cos(time*0.11 + seed)*0.25;
        p.y += sin(time*0.09 + seed*1.7)*0.2;
        p.y = ymin + mod(p.y - ymin - time*fall*(0.6 + fract(seed*5.3)), yh);
        vec3 wp = (modelMatrix*vec4(p,1.0)).xyz;
        float b = amb;
        for (int i = 0; i < 2; i++) { vec3 d = wp - lp[i]; float r = max(length(d), 0.01); float c = dot(d/r, ld[i]);
          b += li[i] * smoothstep(lc[i], lc[i] + (1.0 - lc[i])*0.7, c) / (1.0 + r*r*0.05); }
        float tw = 0.45 + 0.55*abs(sin(time*1.7 + seed*13.0));
        vec4 mv = viewMatrix*vec4(wp,1.0); float z = -mv.z;
        vB = b*tw*smoothstep(0.2, 0.7, z);
        gl_PointSize = clamp(size*(0.5 + fract(seed*3.7))*scale/max(z,0.05), 1.0, 40.0);
        gl_Position = projectionMatrix*mv;
      }`,
    fragmentShader: `uniform vec3 color; varying float vB;
      void main(){ float d = length(gl_PointCoord - 0.5); float a = smoothstep(0.5, 0.0, d); a *= a; gl_FragColor = vec4(color*a*vB, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false;
  return pts;
}

function aimBeam(THREE, bm, from, to) {
  bm.position.copy(from);
  const d = new THREE.Vector3().subVectors(to, from).normalize();
  bm.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), d);
}

// ======================================================================== setup
export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'walk';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020202);
  scene.fog = new THREE.FogExp2(0x070605, shot === 'line' ? 0.03 : 0.045);
  const fov = shot === 'walk' ? 54 : shot === 'line' ? 52 : 40;
  const camera = new THREE.PerspectiveCamera(fov, W / H, 0.03, 400);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });
  const add = (geo, mat, x, y, z, parent = scene) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); parent.add(m); return m; };
  const ctx = { THREE, scene, camera, shot, W, H };
  const steel = std({ color: 0x34342f, metalness: 0.6, roughness: 0.5 });
  const darkMetal = std({ color: 0x1d1c1a, metalness: 0.5, roughness: 0.55 });
  const bulbMat = new THREE.MeshBasicMaterial({ color: 0xffd6a0 });

  // hanging bare bulb with a shade, light and halo
  const lamps = [];
  const hangBulb = (x, y, z, { color = AMBER, inten = 3, dist = 14, halo = 1.2, shadow = false, spot = false } = {}) => {
    const b = add(new THREE.SphereGeometry(0.06, 12, 8), bulbMat.clone(), x, y, z);
    const shade = add(new THREE.ConeGeometry(0.26, 0.17, 20, 1, true), std({ color: 0x1e1e1e, side: THREE.DoubleSide, metalness: 0.4, roughness: 0.5 }), x, y + 0.1, z);
    add(new THREE.CylinderGeometry(0.008, 0.008, Math.max(0.05, HT - y - 0.15)), steel, x, (HT + y + 0.15) / 2, z);
    const h = glow(THREE, color, halo, 0.9); h.position.set(x, y - 0.02, z); scene.add(h);
    let light;
    if (spot) {
      light = new THREE.SpotLight(color, inten, dist, 1.1, 0.7, 1.6); light.position.set(x, y - 0.08, z); light.target.position.set(x, 0, z); scene.add(light.target);
      if (shadow) { light.castShadow = true; light.shadow.mapSize.set(1024, 1024); light.shadow.bias = -0.0008; light.shadow.camera.near = 0.2; }
    } else light = new THREE.PointLight(color, inten, dist, 1.6), light.position.set(x, y - 0.1, z);
    scene.add(light);
    const l = { bulb: b, halo: h, light, base: inten, color: new THREE.Color(color) }; lamps.push(l); return l;
  };
  const setLamp = (l, v) => { l.light.intensity = l.base * v; l.halo.material.opacity = Math.min(1, v * 1.1); l.bulb.material.color.copy(l.color).multiplyScalar(0.12 + 0.88 * Math.min(1, v)); l.bulb.material.color.lerp(new THREE.Color(1, 0.95, 0.85), Math.min(1, v) * 0.5); };
  ctx.setLamp = setLamp; ctx.lamps = lamps;

  if (shot !== 'line') {
    // ------------------------------------------------------------ the station box
    const T = tiles(THREE, 11, [L / 3.84, HT / 3.84]);
    const wallMat = std({ map: T.map, normalMap: T.normal, normalScale: new THREE.Vector2(0.45, 0.45), roughness: 0.32, metalness: 0.0 });
    const bandT = tiles(THREE, 12, [L / 3.84, 0.35 / 3.84], 120);
    const bandMat = std({ map: bandT.map, normalMap: bandT.normal, normalScale: new THREE.Vector2(0.45, 0.45), roughness: 0.35, color: 0x8c877c });
    for (const sx of [-1, 1]) {
      const wall = add(new THREE.PlaneGeometry(L, HT), wallMat, sx * HW, HT / 2, 0); wall.rotation.y = -sx * Math.PI / 2; wall.receiveShadow = true;
      for (const by of [1.17, 4.25]) { const b = add(new THREE.PlaneGeometry(L, 0.35), bandMat, sx * (HW - 0.006), by, 0); b.rotation.y = -sx * Math.PI / 2; b.receiveShadow = true; }
      const floorMat = std({ map: dustyFloor(THREE, [1.2, 40], 5 + sx), roughness: 0.85 });
      const p = add(new THREE.BoxGeometry(3.6, 1, L), floorMat, sx * (HW - 1.8), 0.5, 0); p.receiveShadow = true;
      const edge = add(new THREE.BoxGeometry(0.3, 0.02, L), std({ color: 0xcfc9b8, roughness: 0.6 }), sx * (PX + 0.15), 1.011, 0); edge.receiveShadow = true;
      const lip = add(new THREE.BoxGeometry(0.06, 0.08, L), std({ color: 0x5a5852, roughness: 0.7 }), sx * (PX + 0.02), 0.96, 0);
      // third rail with its wooden cover on the outer side of each track
      add(new THREE.BoxGeometry(0.08, 0.1, L), steel, sx * (PX - 0.45), 0.42, 0);
      add(new THREE.BoxGeometry(0.22, 0.03, L), std({ color: 0x2a2520 }), sx * (PX - 0.45), 0.5, 0);
    }
    const ceil = add(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [3, 20], 11, 70), roughness: 0.95 }), 0, HT, 0); ceil.rotation.x = Math.PI / 2;
    const bed = add(new THREE.PlaneGeometry(PX * 2, L + 300), std({ map: concreteTex(THREE, [4, 120], 9, 50) }), 0, 0, 0); bed.rotation.x = -Math.PI / 2; bed.receiveShadow = true;
    const rail = std({ color: 0x9a9a98, metalness: 1, roughness: 0.3 });
    for (const tx of [-2.1, 2.1]) for (const o of [-0.72, 0.72]) add(new THREE.BoxGeometry(0.07, 0.14, L + 300), rail, tx + o, 0.22, -150 + L / 2);
    const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), std({ color: 0x1f1d1a }), 720);
    const m4 = new THREE.Matrix4(); let k = 0;
    for (const tx of [-2.1, 2.1]) for (let i = 0; i < 360; i++) { m4.makeTranslation(tx, 0.08, -L / 2 - 210 + i * 0.75); sl.setMatrixAt(k++, m4); }
    scene.add(sl);
    // riveted I-section columns between the tracks, cross girders under the ceiling
    const colPaint = std({ color: 0x3a3c37, metalness: 0.55, roughness: 0.55 });
    const rivets = new THREE.InstancedMesh(new THREE.SphereGeometry(0.018, 6, 4), colPaint, 2000); let ri = 0;
    for (let z = -L / 2 + 4; z < L / 2; z += 6.5) {
      for (const fz of [-0.14, 0.14]) { const f = add(new THREE.BoxGeometry(0.34, HT, 0.025), colPaint, 0, HT / 2, z + fz); f.castShadow = true; }
      add(new THREE.BoxGeometry(0.025, HT, 0.26), colPaint, 0, HT / 2, z);
      add(new THREE.BoxGeometry(0.5, 0.06, 0.5), colPaint, 0, 0.03, z);
      add(new THREE.BoxGeometry(0.5, 0.08, 0.42), colPaint, 0, HT - 0.42, z);
      for (let y = 0.4; y < HT - 0.5; y += 0.32) for (const fz of [-0.155, 0.155]) for (const fx of [-0.11, 0.11]) { if (ri < 2000) { m4.makeTranslation(fx, y, z + fz); rivets.setMatrixAt(ri++, m4); } }
      add(new THREE.BoxGeometry(HW * 2, 0.36, 0.22), colPaint, 0, HT - 0.18, z);
    }
    rivets.count = ri; scene.add(rivets);
    add(new THREE.BoxGeometry(0.3, 0.3, L), colPaint, 0, HT - 0.5, 0);
    // cable runs along the top of the walls
    for (const sx of [-1, 1]) for (const [dy, rr] of [[0, 0.025], [0.07, 0.018], [0.13, 0.03]]) { const c = add(new THREE.CylinderGeometry(rr, rr, L, 6), std({ color: 0x151412, roughness: 0.6 }), sx * (HW - 0.08), 4.6 + dy, 0); c.rotation.x = Math.PI / 2; }
    // end walls with the two tunnel mouths
    const endMat = std({ map: concreteTex(THREE, [3, 2], 41, 70), roughness: 0.9 });
    for (const zs of [-1, 1]) {
      const zE = zs * L / 2;
      for (const sx of [-1, 1]) { const e = add(new THREE.PlaneGeometry(HW - PX, HT), wallMat, sx * (PX + (HW - PX) / 2), HT / 2, zE); e.rotation.y = zs < 0 ? 0 : Math.PI; }
      const lint = add(new THREE.PlaneGeometry(PX * 2, HT - 4.4), endMat, 0, 4.4 + (HT - 4.4) / 2, zE); lint.rotation.y = zs < 0 ? 0 : Math.PI;
      add(new THREE.BoxGeometry(0.5, 4.4, 0.5), endMat, 0, 2.2, zE);
      // tunnels beyond
      const tun = std({ map: concreteTex(THREE, [40, 2], 31, 55), roughness: 0.95 });
      for (const sx of [-1, 1]) { const w = add(new THREE.PlaneGeometry(200, 4.4), tun, sx * PX, 2.2, zE + zs * 100); w.rotation.y = -sx * Math.PI / 2; }
      const c = add(new THREE.PlaneGeometry(PX * 2, 200), tun, 0, 4.4, zE + zs * 100); c.rotation.x = Math.PI / 2;
      const mid = add(new THREE.BoxGeometry(0.4, 4.4, 200), tun, 0, 2.2, zE + zs * 100);
    }
    // station name boards
    const sign = std({ map: signTex(THREE), roughness: 0.4 });
    for (const sx of [-1, 1]) for (const z of [-40, 23.2]) {
      const b = add(new THREE.PlaneGeometry(3.0, 0.5), sign, sx * (HW - 0.03), 3.55, z); b.rotation.y = -sx * Math.PI / 2;
      const fr = add(new THREE.BoxGeometry(0.03, 0.56, 3.06), darkMetal, sx * (HW - 0.015), 3.55, z);
    }
    // benches: wooden slats on cast iron legs
    const wood = std({ color: 0x5b4a38, roughness: 0.75 });
    ctx.bench = (z, len = 2.0, sx = 1) => {
      const g = new THREE.Group(); g.position.set(sx * (HW - 0.42), 1, z); scene.add(g);
      for (let i = 0; i < 4; i++) { const s = add(new THREE.BoxGeometry(0.085, 0.03, len), wood, (i - 1.5) * 0.095, 0.45, 0, g); s.castShadow = true; s.receiveShadow = true; }
      for (let i = 0; i < 3; i++) { const s = add(new THREE.BoxGeometry(0.03, 0.085, len), wood, sx * 0.2, 0.62 + i * 0.1, 0, g); s.castShadow = true; }
      for (const lz of [-len / 2 + 0.15, len / 2 - 0.15]) {
        add(new THREE.BoxGeometry(0.42, 0.04, 0.05), darkMetal, 0, 0.42, lz, g);
        for (const lx of [-0.16, 0.16]) { const leg = add(new THREE.BoxGeometry(0.04, 0.44, 0.05), darkMetal, lx, 0.21, lz, g); leg.rotation.z = lx * 0.4; leg.castShadow = true; }
        add(new THREE.BoxGeometry(0.04, 0.42, 0.05), darkMetal, sx * 0.22, 0.62, lz, g);
      }
      return g;
    };
    ctx.bench(23.3, 2.2); ctx.bench(-26, 2.2, -1); ctx.bench(4.8, 2.0);
    // poster row on the right wall (in boards), a few on the far wall
    const kinds = ['lumin', 'kino', 'ostsee', 'oval', 'bvg', 'pils'];
    ctx.posters = [];
    const backing = std({ map: backingTex(THREE, 3), roughness: 0.95 });
    const putPoster = (kind, sx, z, y, peelCorner, peel, seed) => {
      const pw = 1.36, ph = 1.91;
      const bk = add(new THREE.PlaneGeometry(pw + 0.12, ph + 0.12), backing, sx * (HW - 0.012), y, z); bk.rotation.y = -sx * Math.PI / 2; bk.receiveShadow = true;
      for (const [fy, fz, fw, fh] of [[ph / 2 + 0.075, 0, pw + 0.2, 0.035], [-ph / 2 - 0.075, 0, pw + 0.2, 0.035], [0, pw / 2 + 0.085, 0.035, ph + 0.18], [0, -pw / 2 - 0.085, 0.035, ph + 0.18]]) {
        const f = add(new THREE.BoxGeometry(0.03, fh, fw), darkMetal, sx * (HW - 0.015), y + fy, z + fz * sx); f.castShadow = true;
        if (fh < 0.1) f.scale.set(1, 1, 1);
      }
      const m = peelPoster(THREE, posterTex(THREE, kind, seed), pw, ph, peelCorner);
      m.position.set(sx * (HW - 0.024), y, z); m.rotation.y = -sx * Math.PI / 2; scene.add(m);
      m.userData.setPeel(peel); ctx.posters.push(m); return m;
    };
    const pz = [17.6, 15.9, 14.2, 12.5, 10.8, 9.1];
    const peels = [[[1, -1], 0.32], [[-1, 1], 0.12], [[1, 1], 0.22], [[-1, -1], 0.08], [[1, -1], 0.0], [[-1, 1], 0.3]];
    kinds.forEach((kd, i) => putPoster(kd, 1, pz[i], 2.55, peels[i][0], peels[i][1], 100 + i));
    // the poster above the 'years' bench
    ctx.yearsPoster = putPoster('oval', 1, 5.2, 2.75, [-1, -1], 0.05, 140);
    putPoster('kino', 1, 3.5, 2.75, [1, 1], 0.1, 141);
    for (let i = 0; i < 6; i++) putPoster(kinds[(i + 2) % 6], -1, 14 - i * 1.7, 2.55, [1, -1], 0.1 + (i % 3) * 0.1, 120 + i);
    // the calendar hanging on a nail
    const cal = add(new THREE.PlaneGeometry(0.56, 0.84), std({ map: calendarTex(THREE), roughness: 0.9, alphaTest: 0.5 }), HW - 0.025, 2.45, 19.35);
    cal.rotation.y = -Math.PI / 2; cal.rotation.x = 0.03; cal.castShadow = true;
    add(new THREE.SphereGeometry(0.012, 8, 6), steel, HW - 0.03, 2.9, 19.35);
    // timetable board next to it
    const ttTex = canvasTex(THREE, 512, 640, (g, w, h) => {
      g.fillStyle = '#e8e2d2'; g.fillRect(0, 0, w, h); txt(g, 'Fahrplan', w / 2, 70, 'bold 56px "DejaVu Serif", serif', '#111');
      txt(g, 'Rosenthaler Platz  →  Leinestraße', w / 2, 112, '24px "DejaVu Sans Condensed", sans-serif', '#222');
      for (let i = 0; i < 20; i++) { const hh = 4 + Math.floor(i / 1); txt(g, String(hh + 1).padStart(2, '0'), 50, 160 + i * 23, 'bold 18px "DejaVu Sans Mono", monospace', '#222', 'left');
        txt(g, '02  07  12  17  22  27  32  37  42  47  52  57', 100, 160 + i * 23, '18px "DejaVu Sans Mono", monospace', '#333', 'left'); }
      agePaper(g, w, h, rng(5), { tear: 0.2, fade: 0.25 });
    });
    const tt = add(new THREE.PlaneGeometry(0.62, 0.78), std({ map: ttTex, roughness: 0.6, alphaTest: 0.5 }), HW - 0.034, 2.5, 20.5); tt.rotation.y = -Math.PI / 2;
    add(new THREE.BoxGeometry(0.03, 0.84, 0.68), darkMetal, HW - 0.012, 2.5, 20.5);
    // hanging platform clocks, stopped
    const dial = std({ map: clockTex(THREE), roughness: 0.25, metalness: 0.1 });
    ctx.clock = (x, y, z, hhh = 1, mmm = 47) => {
      const g = new THREE.Group(); g.position.set(x, y, z); scene.add(g);
      const body = add(new THREE.CylinderGeometry(0.4, 0.4, 0.16, 40), darkMetal, 0, 0, 0, g); body.rotation.x = Math.PI / 2; body.castShadow = true;
      for (const s of [-1, 1]) {
        const d = add(new THREE.CircleGeometry(0.36, 40), dial, 0, 0, s * 0.081, g); if (s < 0) d.rotation.y = Math.PI;
        const ha = (hhh % 12 + mmm / 60) / 12 * Math.PI * 2, ma = mmm / 60 * Math.PI * 2;
        const hand = (len, wid, a) => { const p = new THREE.Group(); p.position.set(0, 0, s * 0.092); p.rotation.z = -a * s; g.add(p); const m = add(new THREE.BoxGeometry(wid, len, 0.008), darkMetal, 0, len / 2 - 0.05, 0, p); m.castShadow = true; };
        hand(0.24, 0.042, ha); hand(0.33, 0.03, ma);
        add(new THREE.CylinderGeometry(0.02, 0.02, 0.02, 12), darkMetal, 0, 0, s * 0.095, g).rotation.x = Math.PI / 2;
      }
      add(new THREE.CylinderGeometry(0.018, 0.018, HT - y - 0.4), steel, 0, 0.4 + (HT - y - 0.4) / 2, 0, g);
      add(new THREE.BoxGeometry(0.1, 0.05, 0.1), steel, 0, 0.42, 0, g);
      return g;
    };
    ctx.clock(6.0, 4.15, 19.0);
    if (shot === 'years') ctx.clock(6.1, 4.3, 7.4, 4, 12);
    // a newspaper dropped on the platform
    const np = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.56, 6, 8), std({ map: newspaperTex(THREE), roughness: 0.95, alphaTest: 0.5, side: THREE.DoubleSide }));
    { const p = np.geometry.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, Math.max(0, Math.sin(p.getX(i) * 9) * 0.02 + p.getY(i) * p.getY(i) * 0.15)); np.geometry.computeVertexNormals(); }
    np.rotation.x = -Math.PI / 2; np.rotation.z = 0.5; np.position.set(5.2, 1.012, 22.4); np.receiveShadow = true; np.castShadow = true; scene.add(np);
    ctx.newspaper = np;
    // scattered paper scraps
    const scr = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.08, 0.06), std({ color: 0x9a9284, side: THREE.DoubleSide }), 60); const rs = rng(8);
    for (let i = 0; i < 60; i++) { const o = new THREE.Object3D(); o.position.set(4.6 + rs() * 3.3, 1.013, -30 + rs() * 60); o.rotation.set(-Math.PI / 2, 0, rs() * 6); o.scale.setScalar(0.5 + rs()); o.updateMatrix(); scr.setMatrixAt(i, o.matrix); }
    scene.add(scr);
    scene.add(new THREE.HemisphereLight(0x8a8f98, 0x0a0908, shot === 'walk' ? 0.06 : 0.07));
  }

  // ======================================================================== walk
  if (shot === 'walk') {
    ctx.far = [hangBulb(6.1, 4.75, 1.2, { inten: 9, dist: 14, halo: 1.0 }), hangBulb(-6.1, 4.75, -12, { inten: 8, dist: 14, halo: 0.9 })];
    const torch = new THREE.SpotLight(TORCH, 17, 0, 0.32, 0.55, 2);
    torch.castShadow = true; torch.shadow.mapSize.set(1024, 1024); torch.shadow.bias = -0.0004; torch.shadow.normalBias = 0.03; torch.shadow.camera.near = 0.1; torch.shadow.camera.far = 40;
    scene.add(torch, torch.target);
    const tb = beam(THREE, TORCH, 9, 2.1, 0.04); scene.add(tb);
    const bounce = new THREE.PointLight(TORCH, 0.7, 6, 2); scene.add(bounce); ctx.bounce = bounce;
    const dust = dustCloud(THREE, 2200, [4.4, 1.0, 8], [8, 5.4, 28], 17, 0.016, H, fov); scene.add(dust);
    Object.assign(ctx, { torch, tb, dust });
    ctx.camP = path([[0, [5.75, 2.62, 26.6]], [4, [5.8, 2.62, 23.6]], [7.6, [6.0, 2.6, 21.0]], [12, [6.15, 2.58, 18.1]], [14, [6.2, 2.58, 17.0]]]);
    ctx.lookP = path([[0, [5.0, 1.6, 19]], [2.4, [4.3, 2.2, 12]], [3.6, [4.0, 2.5, 10]], [4.6, [5.2, 3.3, 17]], [5.8, [5.95, 3.8, 20.6]], [6.9, [7.3, 2.8, 20.2]], [8.0, [7.95, 2.6, 18.9]], [10, [7.95, 2.55, 17.7]], [12, [7.95, 2.55, 16.4]], [14, [7.95, 2.55, 15.4]]]);
    ctx.aimP = path([[0, [5.3, 1.0, 21.5]], [1.6, [4.9, 1.1, 19.5]], [2.4, [3.9, 1.0, 19.5]], [3.5, [3.6, 1.8, 15.0]], [4.4, [4.6, 3.4, 15.5]], [5.2, [6.0, 4.15, 19.0]], [6.0, [6.0, 4.1, 19.0]], [6.8, [7.95, 2.5, 19.35]], [7.5, [7.95, 2.45, 19.35]], [8.3, [7.95, 2.75, 18.0]], [9.4, [7.95, 2.3, 17.3]], [10.6, [7.95, 2.6, 16.2]], [12.0, [7.95, 2.45, 15.3]], [13.5, [7.95, 2.5, 14.3]]]);
  }

  // ======================================================================== years
  if (shot === 'years') {
    ctx.yb = hangBulb(6.6, 4.7, 4.6, { inten: 14, dist: 12, halo: 1.3, spot: true, shadow: true });
    ctx.yb.light.angle = 0.9; ctx.yb.light.target.position.set(7.4, 1.4, 4.9);
    hangBulb(-6.1, 4.75, -10, { inten: 1.5, dist: 10, halo: 0.8 });
    // dust layer settling on the bench (alpha plane over the slats) and on the newspaper
    const dustLayerTex = canvasTex(THREE, 512, 128, (g, w, h) => { const r = rng(31); g.clearRect(0, 0, w, h);
      for (let i = 0; i < 9000; i++) { const v = 150 + r() * 60; g.fillStyle = `rgba(${v},${v - 4},${v - 12},${r() * 0.5})`; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1 + r() * 3); } });
    dustLayerTex.wrapS = dustLayerTex.wrapT = THREE.ClampToEdgeWrapping; dustLayerTex.repeat.set(1, 1);
    ctx.dustLayer = add(new THREE.PlaneGeometry(0.4, 1.95), new THREE.MeshStandardMaterial({ map: dustLayerTex, transparent: true, opacity: 0, depthWrite: false, roughness: 1, color: 0xd8d0c0 }), HW - 0.42, 1.468, 4.8);
    ctx.dustLayer.rotation.x = -Math.PI / 2; ctx.dustLayer.rotation.z = Math.PI / 2; ctx.dustLayer.receiveShadow = true;
    // newspaper left on the bench
    ctx.newspaper.position.set(HW - 0.45, 1.475, 4.3); ctx.newspaper.rotation.set(-Math.PI / 2, 0, 1.3); ctx.newspaper.scale.setScalar(0.8);
    // cobweb in the corner between bench leg and wall
    const webTex = canvasTex(THREE, 512, 512, (g, w, h) => { g.clearRect(0, 0, w, h); g.strokeStyle = 'rgba(235,230,220,0.85)'; g.lineWidth = 1.4;
      const cx = 0, cy = 0; for (let a = 0; a < 12; a++) { const an = a / 11 * Math.PI / 2; g.beginPath(); g.moveTo(cx, cy); g.lineTo(Math.cos(an) * 520, Math.sin(an) * 520); g.stroke(); }
      for (let rr = 30; rr < 520; rr += 26 + rr * 0.05) { g.beginPath(); for (let a = 0; a < 12; a++) { const an = a / 11 * Math.PI / 2, q = rr * (0.92 + 0.08 * Math.sin(a * 3)); a ? g.lineTo(Math.cos(an) * q, Math.sin(an) * q) : g.moveTo(Math.cos(an) * q, Math.sin(an) * q); } g.stroke(); } });
    webTex.wrapS = webTex.wrapT = THREE.ClampToEdgeWrapping;
    ctx.web = add(new THREE.PlaneGeometry(0.6, 0.6), new THREE.MeshBasicMaterial({ map: webTex, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, color: 0xbdb5a8 }), HW - 0.35, 1.72, 5.83);
    ctx.web.rotation.y = 0.0;
    const dust = dustCloud(THREE, 2500, [5.2, 1.0, 2.0], [8, 5.2, 7.5], 23, 0.01, H, fov); scene.add(dust);
    dust.material.uniforms.amb.value = 0.25; ctx.dust = dust;
  }

  // ======================================================================== wire
  if (shot === 'wire') {
    // --- beat 1: concertina coils on the platform edge
    const wireMat = std({ color: 0xcfcbc2, metalness: 0.35, roughness: 0.32 });
    const cz0 = -24, cz1 = 18, cR = 0.4, pitch = 0.3, ccx = PX + 0.55, ccy = 1.0 + cR * 0.95;
    const turns = (cz1 - cz0) / pitch;
    const coilCurve = (sgn, ph) => {
      const c = new THREE.Curve();
      c.getPoint = (u, tgt = new THREE.Vector3()) => {
        const tt = u * turns, a = (tt * Math.PI * 2 + ph) * sgn, k = Math.floor(tt);
        const rr = cR * (0.93 + 0.07 * Math.sin(k * 2.3 + sgn) + 0.03 * Math.sin(a * 3));
        return tgt.set(ccx + Math.cos(a) * rr, ccy + Math.sin(a) * rr * 0.97, cz0 + u * (cz1 - cz0) + Math.sin(a) * 0.05 * sgn);
      };
      return c;
    };
    const barbGeo = new THREE.OctahedronGeometry(1, 0); barbGeo.scale(0.024, 0.005, 0.009);
    const barbs = new THREE.InstancedMesh(barbGeo, wireMat, 12000); let bi = 0;
    const o3 = new THREE.Object3D(), up = new THREE.Vector3(), tg = new THREE.Vector3(), q = new THREE.Vector3();
    const rb = rng(55);
    for (const [sgn, ph] of [[1, 0], [-1, 1.7]]) {
      const curve = coilCurve(sgn, ph);
      const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.floor(turns * 30), 0.0055, 4, false), wireMat); tube.castShadow = true; scene.add(tube);
      const N = Math.floor(turns * 2.6 / 0.07);
      for (let i = 0; i < N && bi < 12000; i++) {
        const u = i / N; curve.getPoint(u, o3.position); curve.getPoint(Math.min(1, u + 0.0005), tg); tg.sub(o3.position).normalize();
        up.set(rb() - 0.5, rb() - 0.5, rb() - 0.5).cross(tg).normalize();
        q.copy(o3.position).add(up); o3.up.copy(tg); o3.lookAt(q); o3.rotateZ(rb() * 3);
        o3.updateMatrix(); barbs.setMatrixAt(bi++, o3.matrix);
      }
    }
    barbs.count = bi; scene.add(barbs);
    // angle-iron posts through the coil with two strands of twisted barbed wire
    const strandBarbs = new THREE.InstancedMesh(new THREE.BoxGeometry(0.004, 0.004, 0.045), wireMat, 4000); let si = 0;
    for (let z = cz0 + 1; z < cz1; z += 3.0) {
      for (const [ox, oz] of [[0, 0], [0.025, 0.025]]) add(new THREE.BoxGeometry(ox ? 0.05 : 0.006, 1.25, ox ? 0.006 : 0.05), std({ color: 0x3a3631, metalness: 0.6, roughness: 0.6 }), ccx - 0.3 + ox, 1.62, z + oz).castShadow = true;
    }
    for (const sy of [1.95, 2.18]) {
      const pts = []; for (let z = cz0 + 1; z <= cz1; z += 0.25) { const ph = ((z - cz0 - 1) % 3) / 3; pts.push(new THREE.Vector3(ccx - 0.3, sy - 0.05 * Math.sin(ph * Math.PI), z)); }
      const cv = new THREE.CatmullRomCurve3(pts);
      for (const tw of [0, 1]) { const tb2 = new THREE.Mesh(new THREE.TubeGeometry(cv, 400, 0.0035, 4), wireMat); tb2.position.y = tw * 0.004; scene.add(tb2); }
      for (let z = cz0 + 1; z <= cz1 && si < 4000; z += 0.13) {
        const ph = ((z - cz0 - 1) % 3) / 3, y = sy - 0.05 * Math.sin(ph * Math.PI);
        for (let k = 0; k < 2; k++) { o3.position.set(ccx - 0.3, y, z); o3.rotation.set(0.4, k * Math.PI / 2 + 0.6, 0); o3.updateMatrix(); strandBarbs.setMatrixAt(si++, o3.matrix); }
      }
    }
    strandBarbs.count = si; scene.add(strandBarbs);
    // --- beat 2: emergency exit, welded shut
    const DZ = -30, DW = 1.05, DH = 2.15, DX = HW - 0.035;
    const doorN = normalFromHeight(THREE, 256, 512, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.fillRect(28, 30, w - 56, 200); g.fillRect(28, 270, w - 56, 210); }, 1.5);
    const doorTex = canvasTex(THREE, 256, 512, (g, w, h) => { const r = rng(91); g.fillStyle = '#6f6d66'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(${40 + r() * 60},${36 + r() * 50},${30 + r() * 30},${r() * 0.25})`; g.fillRect(r() * w, r() * h, 1 + r() * 5, 1 + r() * 5); }
      for (let i = 0; i < 25; i++) { const x = r() * w, len = 30 + r() * 200, y = r() * h; const gr = g.createLinearGradient(0, y, 0, y + len); gr.addColorStop(0, 'rgba(90,50,20,0.5)'); gr.addColorStop(1, 'rgba(90,50,20,0)'); g.fillStyle = gr; g.fillRect(x, y, 2 + r() * 5, len); } });
    const doorMat = std({ map: doorTex, normalMap: doorN, metalness: 0.55, roughness: 0.55 });
    const door = add(new THREE.BoxGeometry(0.05, DH, DW), doorMat, DX - 0.01, 1 + DH / 2, DZ); door.receiveShadow = true;
    add(new THREE.BoxGeometry(0.06, DH + 0.1, DW + 0.14), std({ color: 0x050505 }), DX + 0.01, 1 + DH / 2 + 0.03, DZ);   // dark gap behind
    for (const [y, z, h, w] of [[1 + DH + 0.07, DZ, 0.1, DW + 0.24], [1 + DH / 2, DZ - DW / 2 - 0.07, DH + 0.04, 0.1], [1 + DH / 2, DZ + DW / 2 + 0.07, DH + 0.04, 0.1]])
      add(new THREE.BoxGeometry(0.08, h, w), std({ color: 0x4a4943, metalness: 0.6, roughness: 0.5 }), DX - 0.02, y, z);
    const lever = add(new THREE.CylinderGeometry(0.018, 0.018, 0.22, 10), steel, DX - 0.08, 1 + 1.05, DZ - DW / 2 + 0.16); lever.rotation.x = Math.PI / 2;
    add(new THREE.BoxGeometry(0.03, 0.18, 0.06), steel, DX - 0.05, 1 + 1.05, DZ - DW / 2 + 0.07);
    // two flat bars welded across door and frame
    const bars = [1 + 0.75, 1 + 1.55];
    for (const by of bars) { const b = add(new THREE.BoxGeometry(0.018, 0.09, DW + 0.42), std({ color: 0x55534d, metalness: 0.7, roughness: 0.45 }), DX - 0.06, by, DZ); b.castShadow = true; }
    const ntTex = canvasTex(THREE, 512, 128, (g, w, h) => { g.fillStyle = '#2e5a3a'; g.fillRect(0, 0, w, h); g.strokeStyle = '#eee'; g.lineWidth = 6; g.strokeRect(8, 8, w - 16, h - 16); txt(g, 'NOTAUSGANG', w / 2, 86, 'bold 66px "DejaVu Sans Condensed", sans-serif', '#f2f2ea'); agePaper(g, w, h, rng(3), { tear: 0, fade: 0.1 }); });
    const nt = add(new THREE.PlaneGeometry(0.9, 0.22), std({ map: ntTex, roughness: 0.4 }), HW - 0.03, 1 + DH + 0.35, DZ); nt.rotation.y = -Math.PI / 2;
    // weld beads: positions + time each one was laid
    const beads = [];
    const seam = (p0, p1, tw0, tw1, step = 0.022) => { const n = Math.max(2, Math.round(p0.distanceTo(p1) / step)); for (let i = 0; i <= n; i++) beads.push({ p: p0.clone().lerp(p1, i / n), tw: lerp(tw0, tw1, i / n) }); };
    const V = (y, z, x = DX - 0.035) => new THREE.Vector3(x, y, z);
    seam(V(1.02, DZ - DW / 2 - 0.005), V(1 + DH, DZ - DW / 2 - 0.005), -14, -9);                       // far edge, long cold
    seam(V(1 + DH, DZ - DW / 2), V(1 + DH, DZ + DW / 2), -7, -3.5);                                   // top edge
    for (const by of bars) for (const zz of [DZ - DW / 2 - 0.19, DZ - DW / 2 + 0.02, DZ + DW / 2 - 0.02, DZ + DW / 2 + 0.19])
      seam(V(by - 0.05, zz, DX - 0.075), V(by + 0.05, zz, DX - 0.075), 0.8 + (by - 1.75) * 1.6 + (zz - DZ) * 0.8, 1.2 + (by - 1.75) * 1.6 + (zz - DZ) * 0.8, 0.012);
    seam(V(1.02, DZ + DW / 2 + 0.005), V(1 + DH - 0.02, DZ + DW / 2 + 0.005), 3.0, 5.35, 0.02);           // near edge: being welded now
    const beadGeo = new THREE.SphereGeometry(0.016, 8, 6);
    const heat = new Float32Array(beads.length);
    beadGeo.setAttribute('heat', new THREE.InstancedBufferAttribute(heat, 1));
    const beadMat = std({ color: 0x3b3833, metalness: 0.6, roughness: 0.45 });
    beadMat.onBeforeCompile = (s) => {
      s.vertexShader = 'attribute float heat;\nvarying float vHeat;\n' + s.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n vHeat = heat;');
      s.fragmentShader = 'varying float vHeat;\n' + s.fragmentShader.replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        float hh = clamp(vHeat, 0.0, 1.0);
        totalEmissiveRadiance += vec3(1.0, 0.36 + 0.55*hh, 0.08 + 0.7*hh*hh) * (hh*hh*9.0 + hh*1.2);`);
    };
    const beadMesh = new THREE.InstancedMesh(beadGeo, beadMat, beads.length); scene.add(beadMesh);
    const arcLight = new THREE.PointLight(0xffe2bc, 0, 9, 1.6); scene.add(arcLight);
    const arcGlow = glow(THREE, 0xfff0d8, 0.5, 1); scene.add(arcGlow);
    const arcGlow2 = glow(THREE, AMBER, 1.6, 0.6); scene.add(arcGlow2);
    // sparks: streaks with deterministic ballistic paths
    const NS = 260, rsp = rng(66), sparks = [];
    for (let i = 0; i < NS; i++) sparks.push({ t0: 3.0 + (i / NS) * 2.4 + rsp() * 0.01, v: [-(0.4 + rsp() * 1.8), (rsp() - 0.2) * 2.2, (rsp() - 0.5) * 2.4], life: 0.35 + rsp() * 0.7 });
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(NS * 6), 3)); sg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(NS * 6), 3));
    const sparkLines = new THREE.LineSegments(sg, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
    sparkLines.frustumCulled = false; scene.add(sparkLines);
    Object.assign(ctx, { beads, beadMesh, heat, arcLight, arcGlow, arcGlow2, sparks, sparkLines });
    // --- beat 3: roller shutter over the right track tunnel
    const SZ = -L / 2 + 0.42, SX0 = 0.25, SX1 = PX, SH = 4.4;
    const slatN = normalFromHeight(THREE, 64, 256, (g, w, h) => { for (let y = 0; y < h; y++) { const v = Math.floor(127 + 127 * Math.sin((y % 32) / 32 * Math.PI * 2)); g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(0, y, w, 1); } }, 4, [6, 6.1]);
    const slatTex = canvasTex(THREE, 256, 256, (g, w, h) => { const r = rng(5); for (let y = 0; y < h; y += 32) { const gr = g.createLinearGradient(0, y, 0, y + 32); gr.addColorStop(0, '#8d8a82'); gr.addColorStop(0.5, '#a8a49b'); gr.addColorStop(1, '#55534e'); g.fillStyle = gr; g.fillRect(0, y, w, 32); }
      for (let i = 0; i < 40; i++) { const x = r() * w, y = r() * h, len = 20 + r() * 120; const gr = g.createLinearGradient(0, y, 0, y + len); gr.addColorStop(0, 'rgba(70,45,25,0.6)'); gr.addColorStop(1, 'rgba(70,45,25,0)'); g.fillStyle = gr; g.fillRect(x, y, 2 + r() * 6, len); }
      for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(30,28,25,${r() * 0.2})`; g.fillRect(r() * w, r() * h, 2, 2); } }, [6, 6.1]);
    const clip = [new THREE.Plane(new THREE.Vector3(0, -1, 0), SH + 0.02)];
    const shutter = add(new THREE.PlaneGeometry(SX1 - SX0, SH), std({ map: slatTex, normalMap: slatN, metalness: 0.6, roughness: 0.45, side: THREE.DoubleSide, clippingPlanes: clip }), (SX0 + SX1) / 2, SH * 1.5, SZ);
    shutter.receiveShadow = true;
    const bottomBar = add(new THREE.BoxGeometry(SX1 - SX0, 0.1, 0.08), std({ color: 0x2c2b28, metalness: 0.7, roughness: 0.4, clippingPlanes: clip }), (SX0 + SX1) / 2, SH, SZ); bottomBar.castShadow = true;
    add(new THREE.BoxGeometry(SX1 - SX0 + 0.3, 0.75, 0.6), std({ color: 0x3a3833, metalness: 0.5, roughness: 0.6 }), (SX0 + SX1) / 2, SH + 0.36, SZ + 0.1).castShadow = true;
    for (const gx of [SX0 + 0.04, SX1 - 0.04]) add(new THREE.BoxGeometry(0.1, SH, 0.16), std({ color: 0x2f2e2a, metalness: 0.6, roughness: 0.5 }), gx, SH / 2, SZ);
    // the left tunnel mouth: already shut
    const lsh = add(new THREE.PlaneGeometry(SX1 - SX0, SH), std({ map: slatTex, normalMap: slatN, metalness: 0.6, roughness: 0.5 }), -(SX0 + SX1) / 2, SH / 2, SZ);
    add(new THREE.BoxGeometry(SX1 - SX0 + 0.3, 0.75, 0.6), std({ color: 0x3a3833, metalness: 0.5, roughness: 0.6 }), -(SX0 + SX1) / 2, SH + 0.36, SZ + 0.1);
    const shutLamp = new THREE.SpotLight(AMBER, 0, 14, 0.85, 0.6, 1.4); shutLamp.position.set(3.4, 5.15, -55.0); shutLamp.target.position.set(2.2, 1.2, SZ);
    shutLamp.castShadow = true; shutLamp.shadow.mapSize.set(1024, 1024); shutLamp.shadow.bias = -0.0003; shutLamp.shadow.normalBias = 0.05; scene.add(shutLamp, shutLamp.target);
    const sb = add(new THREE.SphereGeometry(0.06, 12, 8), bulbMat.clone(), 3.4, 5.1, -55.0); const sbH = glow(THREE, AMBER, 1.3, 0.9); sbH.position.set(3.4, 5.08, -55.0); scene.add(sbH);
    add(new THREE.CylinderGeometry(0.008, 0.008, 0.3), steel, 3.4, 5.25, -55.0);
    const tunLamp = new THREE.PointLight(AMBER, 0, 16, 1.5); tunLamp.position.set(3.2, 3.5, -74); scene.add(tunLamp);
    const tunGlow = glow(THREE, AMBER, 2.2, 0.9); tunGlow.position.set(4.1, 3.6, -74); scene.add(tunGlow);
    Object.assign(ctx, { shutter, bottomBar, shutLamp, SH, tunLamp, tunGlow });
    // --- beat 4: light barriers across the right track
    const lbz = [-38, -41.2, -44.4, -47.6, -50.8];
    ctx.barriers = [];
    const boxMat = std({ color: 0x2b2a26, metalness: 0.4, roughness: 0.55 });
    const ledMat = () => new THREE.MeshBasicMaterial({ color: 0x110a04 });
    for (const [bi2, z] of lbz.entries()) for (const y of [0.45, 0.95]) {
      const ex = 0.42, rx = PX - 0.04;
      add(new THREE.BoxGeometry(0.16, 0.2, 0.14), boxMat, ex, y, z).castShadow = true;
      add(new THREE.BoxGeometry(0.04, y - 0.1, 0.04), boxMat, ex - 0.03, (y - 0.1) / 2, z);
      add(new THREE.BoxGeometry(0.12, 0.2, 0.14), boxMat, rx - 0.06, y, z);
      const lens1 = add(new THREE.CircleGeometry(0.035, 16), new THREE.MeshBasicMaterial({ color: 0x221a10 }), ex + 0.081, y, z); lens1.rotation.y = Math.PI / 2;
      const lens2 = add(new THREE.CircleGeometry(0.035, 16), new THREE.MeshBasicMaterial({ color: 0x221a10 }), rx - 0.121, y, z); lens2.rotation.y = -Math.PI / 2;
      const len = rx - 0.12 - (ex + 0.08);
      const core = add(new THREE.CylinderGeometry(0.0035, 0.0035, len, 6), new THREE.MeshBasicMaterial({ color: 0xfff0d8, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }), (ex + 0.08 + rx - 0.12) / 2, y, z); core.rotation.z = Math.PI / 2;
      const halo = add(new THREE.CylinderGeometry(0.022, 0.022, len, 10, 1, true), new THREE.MeshBasicMaterial({ color: 0xffb870, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }), core.position.x, y, z); halo.rotation.z = Math.PI / 2;
      const g1 = glow(THREE, 0xffe8c8, 0.22, 1); g1.position.set(ex + 0.09, y, z); scene.add(g1);
      const g2 = glow(THREE, 0xffe8c8, 0.16, 1); g2.position.set(rx - 0.13, y, z); scene.add(g2);
      const led = add(new THREE.SphereGeometry(0.012, 8, 6), ledMat(), rx - 0.06, y + 0.13, z - 0.04);
      const ledG = glow(THREE, AMBER, 0.12, 1); ledG.position.copy(led.position); scene.add(ledG);
      ctx.barriers.push({ core, halo, g1, g2, led, ledG, i: bi2, y, z, lens1, lens2 });
    }
    ctx.platBulbs = [hangBulb(6.2, 4.75, -6, { inten: 4, dist: 16, halo: 1.2 }), hangBulb(6.2, 4.75, 8, { inten: 3, dist: 14, halo: 1.1 }), hangBulb(6.2, 4.75, -20, { inten: 3, dist: 14, halo: 1.1 }),
      hangBulb(6.5, 4.75, -28.6, { inten: 7, dist: 12, halo: 1.0 }), hangBulb(-6.2, 4.75, -14, { inten: 2, dist: 12, halo: 0.9 }), hangBulb(1.5, 4.85, -45, { inten: 2.4, dist: 12, halo: 1.0 })];
    const dust = dustCloud(THREE, 3000, [0.3, 0.1, -54], [7.8, 4.5, 10], 29, 0.011, H, fov); dust.material.uniforms.amb.value = 0.18; scene.add(dust); ctx.dust = dust;
    const coilKey = new THREE.SpotLight(AMBER, 0, 20, 0.5, 0.6, 1.3); coilKey.position.set(6.6, 4.6, -4); coilKey.target.position.set(4.9, 1.3, 4);
    coilKey.castShadow = true; coilKey.shadow.mapSize.set(1024, 1024); coilKey.shadow.bias = -0.0005; scene.add(coilKey, coilKey.target);
    const coilFill = new THREE.PointLight(0xffc890, 0, 8, 1.5); coilFill.position.set(6.4, 2.6, 8.5); scene.add(coilFill);
    const lbFill = new THREE.PointLight(AMBER, 0, 14, 1.4); lbFill.position.set(3.2, 3.2, -41); scene.add(lbFill);
    Object.assign(ctx, { coilKey, coilFill, lbFill });
  }

  // ======================================================================== line (tunnel)
  if (shot === 'line') {
    const TW = 3.9, TH = 4.3, LZ = -12;
    ctx.LZ = LZ;
    const wallTex = canvasTex(THREE, 1024, 512, (g, w, h) => { const r = rng(71); g.fillStyle = 'rgb(98,96,90)'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 9000; i++) { const v = 60 + r() * 80; g.fillStyle = `rgba(${v},${v},${v - 4},${0.08 + r() * 0.12})`; g.fillRect(r() * w, r() * h, 1 + r() * 5, 1 + r() * 4); }
      for (let y = 64; y < h; y += 96) { g.fillStyle = 'rgba(30,30,28,0.35)'; g.fillRect(0, y, w, 2); }                        // formwork lines
      for (let x = 0; x < w; x += 170) { g.fillStyle = 'rgba(30,30,28,0.3)'; g.fillRect(x, 0, 2, h); }
      for (let i = 0; i < 60; i++) { const x = r() * w, len = 60 + r() * 400; const gr = g.createLinearGradient(0, 0, 0, len); gr.addColorStop(0, `rgba(30,26,20,${0.2 + r() * 0.35})`); gr.addColorStop(1, 'rgba(30,26,20,0)'); g.fillStyle = gr; g.fillRect(x, 0, 3 + r() * 20, len); }
      const gr = g.createLinearGradient(0, h * 0.6, 0, h); gr.addColorStop(0, 'rgba(25,22,18,0)'); gr.addColorStop(1, 'rgba(25,22,18,0.7)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    }, [24, 1]);
    const tunMat = std({ map: wallTex, roughness: 0.92 });
    const TL = 200, TZc = -60;
    for (const sx of [-1, 1]) { const w = add(new THREE.PlaneGeometry(TL, TH), tunMat, sx * TW, TH / 2, TZc); w.rotation.y = -sx * Math.PI / 2; w.receiveShadow = true; }
    const ceilT = add(new THREE.PlaneGeometry(TW * 2, TL), std({ map: concreteTex(THREE, [3, 60], 72, 62), roughness: 0.95 }), 0, TH, TZc); ceilT.rotation.x = Math.PI / 2;
    const bedT = add(new THREE.PlaneGeometry(TW * 2, TL), std({ map: concreteTex(THREE, [3, 80], 73, 46) }), 0, 0, TZc); bedT.rotation.x = -Math.PI / 2; bedT.receiveShadow = true;
    const rail = std({ color: 0xa5a5a2, metalness: 1, roughness: 0.28 });
    for (const tx of [-1.85, 1.85]) for (const o of [-0.72, 0.72]) add(new THREE.BoxGeometry(0.07, 0.14, TL), rail, tx + o, 0.22, TZc);
    const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), std({ color: 0x1d1b18 }), 540); const m4 = new THREE.Matrix4(); let k = 0;
    for (const tx of [-1.85, 1.85]) for (let i = 0; i < 270; i++) { m4.makeTranslation(tx, 0.08, 30 - i * 0.75); sl.setMatrixAt(k++, m4); } scene.add(sl);
    for (const sx of [-1, 1]) { add(new THREE.BoxGeometry(0.08, 0.1, TL), steel, sx * (TW - 0.55), 0.42, TZc); add(new THREE.BoxGeometry(0.22, 0.03, TL), std({ color: 0x2a2520 }), sx * (TW - 0.55), 0.5, TZc); }
    // central steel columns and transverse ceiling girders
    const colPaint = std({ color: 0x2c2e2a, metalness: 0.3, roughness: 0.6 });
    const cols = new THREE.InstancedMesh(new THREE.BoxGeometry(0.3, TH, 0.26), colPaint, 80);
    const gird = new THREE.InstancedMesh(new THREE.BoxGeometry(TW * 2, 0.26, 0.18), colPaint, 160); let ci = 0, gi = 0;
    for (let z = 28; z > -150; z -= 3.0) { m4.makeTranslation(0, TH / 2, z); cols.setMatrixAt(ci++, m4); }
    for (let z = 29; z > -150; z -= 1.5) { m4.makeTranslation(0, TH - 0.13, z); gird.setMatrixAt(gi++, m4); }
    cols.count = ci; gird.count = gi; cols.castShadow = true; scene.add(cols, gird);
    // cable bundles on brackets along both walls
    const cableMat = std({ color: 0x141312, roughness: 0.55 });
    const cables = [];
    for (const sx of [-1, 1]) for (const [y, rr] of [[2.55, 0.03], [2.68, 0.024], [2.8, 0.034], [2.93, 0.022]]) { const c = add(new THREE.CylinderGeometry(rr, rr, TL, 8), cableMat, sx * (TW - 0.12 - rr), y, TZc); c.rotation.x = Math.PI / 2; cables.push([sx, y, rr]); }
    const brk = new THREE.InstancedMesh(new THREE.BoxGeometry(0.22, 0.03, 0.05), steel, 500); let bk = 0;
    for (const sx of [-1, 1]) for (let z = 29; z > -150; z -= 1.5) for (const y of [2.5, 2.98]) { m4.makeTranslation(sx * (TW - 0.11), y, z); brk.setMatrixAt(bk++, m4); }
    brk.count = bk; scene.add(brk);
    // refuge niches
    for (const z of [8, -32, -56]) for (const sx of [1, -1]) add(new THREE.BoxGeometry(0.05, 2.0, 1.2), std({ color: 0x050505 }), sx * (TW - 0.02), 1.0, z + (sx < 0 ? 12 : 0));
    // ---- the white line: right wall, ceiling, left wall, painted over the cables too
    const paint = (seed, wpx, hpx, drips = true) => canvasTex(THREE, wpx, hpx, (g, w, h) => {
      const r = rng(seed); g.clearRect(0, 0, w, h);
      const cx = w / 2, half = w * 0.16;
      // main body: overlapping vertical brush strokes
      for (let s = 0; s < 34; s++) {
        const x = cx + (r() - 0.5) * half * 1.6, bw = half * (0.35 + r() * 0.5);
        const y0 = -20 + r() * h * 0.05, y1 = h + 20 - r() * h * 0.04;
        g.fillStyle = `rgba(242,240,232,${0.55 + r() * 0.45})`;
        g.beginPath(); g.moveTo(x - bw / 2, y0);
        for (let y = y0; y <= y1; y += 24) g.lineTo(x - bw / 2 + Math.sin(y * 0.01 + s) * 4 + (r() - 0.5) * 3, y);
        for (let y = y1; y >= y0; y -= 24) g.lineTo(x + bw / 2 + Math.sin(y * 0.013 + s) * 4 + (r() - 0.5) * 3, y);
        g.fill();
      }
      // dry-brush bristle streaks: thin gaps and thin overshoots
      for (let i = 0; i < 120; i++) { const x = cx + (r() - 0.5) * half * 2.2, y = r() * h, len = 40 + r() * 300;
        g.fillStyle = Math.abs(x - cx) > half * 0.95 ? `rgba(240,238,230,${0.3 + r() * 0.4})` : `rgba(0,0,0,0)`; g.fillRect(x, y, 1 + r() * 2, len);
        if (Math.abs(x - cx) < half * 0.9 && r() < 0.5) { g.save(); g.globalCompositeOperation = 'destination-out'; g.fillStyle = `rgba(0,0,0,${0.3 + r() * 0.5})`; g.fillRect(x, y, 1 + r() * 2, len * 0.6); g.restore(); } }
      // drips
      if (drips) for (let i = 0; i < 18; i++) { const x = cx + (r() - 0.5) * half * 1.9, y = r() * h * 0.95, len = 30 + r() * 240 * (r() < 0.3 ? 2 : 1), dw = 3 + r() * 6;
        g.fillStyle = 'rgba(242,240,232,0.95)'; g.fillRect(x - dw / 2, y, dw, len); g.beginPath(); g.ellipse(x, y + len, dw * 0.85, dw * 1.2, 0, 0, 7); g.fill(); }
      // splatter
      for (let i = 0; i < 80; i++) { const x = cx + (r() - 0.5) * half * 7, y = r() * h, rr = 0.8 + r() * 3.5; g.fillStyle = `rgba(242,240,232,${0.5 + r() * 0.5})`; g.beginPath(); g.arc(x, y, rr, 0, 7); g.fill(); }
      // grime over the paint
      for (let i = 0; i < 900; i++) { g.save(); g.globalCompositeOperation = 'source-atop'; g.fillStyle = `rgba(80,74,62,${r() * 0.3})`; g.fillRect(r() * w, r() * h, 2 + r() * 6, 2 + r() * 10); g.restore(); }
      g.save(); g.globalCompositeOperation = 'source-atop'; const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(60,54,44,0.0)'); gr.addColorStop(0.8, 'rgba(60,54,44,0.1)'); gr.addColorStop(1, 'rgba(60,54,44,0.55)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.restore();
    });
    const lineMat = (seed, drips) => { const t = paint(seed, 512, 2048, drips); t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; return std({ map: t, emissiveMap: t, emissive: 0x8a8a86, transparent: true, alphaTest: 0.08, roughness: 0.55, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }); };
    const LWm = 2.0;    // decal width in metres (the stroke itself is ~0.48 m)
    for (const sx of [-1, 1]) { const d = add(new THREE.PlaneGeometry(LWm, TH), lineMat(sx > 0 ? 3 : 4, true), sx * (TW - 0.01), TH / 2, LZ); d.rotation.y = -sx * Math.PI / 2; d.receiveShadow = true; }
    const dc = add(new THREE.PlaneGeometry(LWm, TW * 2), lineMat(5, false), 0, TH - 0.01, LZ); dc.rotation.set(Math.PI / 2, 0, Math.PI / 2);
    // paint over the cables, the column face and the sleepers' ends at the line
    const paintSolid = std({ color: 0xe8e5dc, roughness: 0.6 });
    for (const [sx, y, rr] of cables) { const c = add(new THREE.CylinderGeometry(rr + 0.003, rr + 0.003, 0.46, 10), paintSolid, sx * (TW - 0.12 - rr), y, LZ); c.rotation.x = Math.PI / 2; }
    // stencil on the west side of the line
    const stTex = canvasTex(THREE, 1024, 256, (g, w, h) => { g.clearRect(0, 0, w, h); g.font = 'bold 104px "DejaVu Sans Condensed", sans-serif'; g.textAlign = 'center'; g.fillStyle = 'rgba(236,234,226,0.92)'; g.fillText('SEKTORENGRENZE', w / 2, 160);
      g.save(); g.globalCompositeOperation = 'destination-out'; g.fillStyle = '#000'; for (let x = 40; x < w; x += 61) g.fillRect(x, 50, 5, 130); const r = rng(8); for (let i = 0; i < 400; i++) g.fillRect(r() * w, r() * h, 2 + r() * 5, 2 + r() * 5); g.restore(); });
    stTex.wrapS = stTex.wrapT = THREE.ClampToEdgeWrapping;
    const st = add(new THREE.PlaneGeometry(2.2, 0.55), std({ map: stTex, transparent: true, alphaTest: 0.1, roughness: 0.6, depthWrite: false }), TW - 0.012, 1.75, LZ + 1.75); st.rotation.y = -Math.PI / 2;
    // small enamel kilometre plates
    const kmTex = (s) => canvasTex(THREE, 256, 128, (g, w, h) => { g.fillStyle = '#e8e4d8'; g.fillRect(0, 0, w, h); g.strokeStyle = '#111'; g.lineWidth = 8; g.strokeRect(6, 6, w - 12, h - 12); txt(g, s, w / 2, 90, 'bold 70px "DejaVu Sans Condensed", sans-serif', '#111'); agePaper(g, w, h, rng(s.length), { tear: 0, fade: 0.2 }); });
    for (const [z, s] of [[6, '4,6'], [-28, '4,8'], [-62, '5,0']]) { const p = add(new THREE.PlaneGeometry(0.36, 0.18), std({ map: kmTex(s), roughness: 0.4 }), TW - 0.015, 1.9, z); p.rotation.y = -Math.PI / 2; }
    // work lamps: warm on the west side, cold and weak beyond the line
    const cage = (x, y, z, col, inten, dist) => {
      const sx = Math.sign(x);
      add(new THREE.BoxGeometry(0.1, 0.22, 0.16), darkMetal, x - sx * 0.05, y, z);
      const b = add(new THREE.SphereGeometry(0.06, 10, 8), new THREE.MeshBasicMaterial({ color: col }), x - sx * 0.14, y, z);
      for (let i = 0; i < 4; i++) { const ring = add(new THREE.TorusGeometry(0.075, 0.004, 4, 16), darkMetal, x - sx * 0.14, y, z); ring.rotation.y = i * Math.PI / 4; }
      const h = glow(THREE, col, 1.4, 0.85); h.position.set(x - sx * 0.18, y, z); scene.add(h);
      const l = new THREE.PointLight(col, inten, dist, 1.5); l.position.set(x - sx * 0.3, y, z); scene.add(l);
      return { b, h, l, base: inten };
    };
    ctx.warm = [cage(TW, 3.3, 10, AMBER, 5, 11), cage(-TW, 3.3, 1, AMBER, 4, 10), cage(TW, 3.45, -9.4, AMBER, 6, 9)];
    ctx.cold = [cage(TW, 3.3, -16.5, COLD, 2.2, 9), cage(-TW, 3.3, -28, COLD, 2.0, 10), cage(-TW, 3.6, -42.5, COLD, 6, 9)];
    // the guard far ahead on the cold side, backlit
    const gmat = std({ color: 0x0b0b0b, roughness: 0.95 });
    const guard = borderGuard(THREE, gmat); guard.group.position.set(-2.9, 0.5, -40.5); guard.group.rotation.y = 0.35; scene.add(guard.group);
    add(new THREE.BoxGeometry(1.2, 0.5, 2.4), std({ color: 0x2a2a28 }), -3.3, 0.25, -40.5);   // walkway ledge he stands on
    ctx.guard = guard;
    // headlight carried with the camera
    const head = new THREE.SpotLight(0xfff0dc, 45, 0, 0.5, 0.6, 1.4);
    head.castShadow = true; head.shadow.mapSize.set(1024, 1024); head.shadow.bias = -0.0006; head.shadow.camera.near = 0.3; head.shadow.camera.far = 60;
    scene.add(head, head.target);
    const hb = beam(THREE, 0xfff0dc, 20, 4.0, 0.03); scene.add(hb);
    const dust = dustCloud(THREE, 4500, [-3.8, 0.2, -40], [3.8, 4.2, 8], 37, 0.014, H, fov, 0xfff0dc); scene.add(dust);
    scene.add(new THREE.HemisphereLight(0x8a8f98, 0x0a0908, 0.05));
    Object.assign(ctx, { head, hb, dust });
  }

  const post = makeComposer(THREE, renderer, scene, camera, W, H, {
    bloom: 0.85, bloomRadius: 0.75, bloomThreshold: 0.6, exposure: shot === 'walk' ? 1.2 : 1.1,
    dof: shot === 'years' ? { focus: 3.4, aperture: 0.0016, maxblur: 0.007 } : shot === 'wire' ? { focus: 3.0, aperture: 0.0014, maxblur: 0.008 } : null,
  });
  Object.assign(ctx, post);
  return ctx;
}

// ======================================================================== update
export function update(ctx, t) {
  const { THREE, camera, shot } = ctx;
  const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
  if (ctx.dust) ctx.dust.material.uniforms.time.value = t;

  if (shot === 'walk') {
    // handheld walk: steps, sway, slow drift
    const p = V(ctx.camP(t)), look = V(ctx.lookP(t));
    const step = t * 1.75 * Math.PI * 2;
    p.y += Math.abs(Math.sin(step / 2)) * 0.03 - 0.015 + nz(t, 1) * 0.01;
    p.x += Math.sin(step / 2) * 0.012 + nz(t, 2) * 0.01;
    look.x += nz(t * 0.8, 3) * 0.06; look.y += nz(t * 0.9, 4) * 0.05; look.z += nz(t * 0.7, 5) * 0.06;
    camera.position.copy(p); camera.lookAt(look);
    camera.rotateZ(nz(t * 0.6, 6) * 0.008);
    // torch in the right hand, below and right of the eye
    const tp = new THREE.Vector3(0.24, -0.34, -0.15).applyQuaternion(camera.quaternion).add(p);
    const aim = V(ctx.aimP(t)); aim.x += nz(t * 1.4, 7) * 0.08; aim.y += nz(t * 1.6, 8) * 0.07 + Math.sin(step / 2) * 0.03; aim.z += nz(t * 1.2, 9) * 0.08;
    ctx.torch.position.copy(tp); ctx.torch.target.position.copy(aim);
    aimBeam(THREE, ctx.tb, tp, aim);
    ctx.bounce.position.copy(aim).lerp(tp, 0.3);
    const u = ctx.dust.material.uniforms; u.lp.value[0].copy(tp); u.ld.value[0].subVectors(aim, tp).normalize(); u.lc.value[0] = Math.cos(0.3); u.li.value[0] = 1.1;
    // the far bulbs: dim, and dimming further on "dimmed to almost nothing"
    const dim = 1 - 0.55 * smooth((t - 2.6) / 2.2);
    ctx.far.forEach((l, i) => ctx.setLamp(l, dim * (0.8 + 0.2 * Math.sin(t * 7 + i) * Math.sin(t * 2.3 + i * 3)) * (hash(Math.floor(t * 12) + i * 50) < 0.06 ? 0.3 : 1)));
    // the posters breathe a hair in the draught
    ctx.posters[0].userData.setPeel(0.32 + 0.012 * Math.sin(t * 1.3));
    ctx.posters[5].userData.setPeel(0.3 + 0.01 * Math.sin(t * 1.1 + 2));
  } else if (shot === 'years') {
    // time-lapse: 28 years in a few seconds
    const k = smooth(t / 3.2), k2 = Math.min(1, t / 3.6);
    camera.position.set(lerp(5.05, 5.35, k2), lerp(1.95, 1.9, k2), lerp(1.3, 1.75, k2));
    camera.lookAt(7.6, lerp(2.2, 2.15, k2), lerp(5.0, 5.0, k2));
    ctx.yearsPoster.userData.setPeel(0.05 + 0.75 * smooth(t / 3.4) + 0.05 * Math.max(0, t - 3.4));
    ctx.dustLayer.material.opacity = 0.95 * k;
    ctx.web.material.opacity = 0.9 * smooth((t - 0.6) / 2.4);
    ctx.web.scale.setScalar(0.4 + 0.6 * smooth((t - 0.4) / 2.6));
    ctx.newspaper.material.color.setRGB(1 - 0.2 * k, 1 - 0.26 * k, 1 - 0.38 * k);
    // the bulb stutters like a time-lapse: frames of on, dim and off
    const fr = Math.floor(t * 15), hv = hash(fr);
    const v = hv < 0.12 ? 0.08 : hv < 0.3 ? 0.55 : 0.9 + 0.1 * hash(fr + 99);
    ctx.setLamp(ctx.yb, v);
    ctx.dust.material.uniforms.fall.value = 0.9;
    ctx.dust.material.uniforms.amb.value = 0.12 + 0.25 * v;
    const u = ctx.dust.material.uniforms; u.lp.value[0].copy(ctx.yb.light.position); u.ld.value[0].set(0, -1, 0); u.lc.value[0] = Math.cos(1.0); u.li.value[0] = 1.5 * v;
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(new THREE.Vector3(7.6, 1.8, 4.7));
  } else if (shot === 'wire') {
    updateWire(ctx, t);
  } else if (shot === 'line') {
    updateLine(ctx, t);
  }
}

function updateWire(ctx, t) {
  const { THREE, camera } = ctx;
  const u = ctx.dust.material.uniforms;
  const base = (l, v) => ctx.setLamp(l, v * (0.92 + 0.08 * Math.sin(t * 8 + l.base * 3) * Math.sin(t * 2.1 + l.base)));
  ctx.platBulbs.forEach(l => base(l, 1));
  let focus = 3;
  // reset per-beat elements
  ctx.arcLight.intensity = 0; ctx.arcGlow.material.opacity = 0; ctx.arcGlow2.material.opacity = 0;
  ctx.shutLamp.intensity = 0; ctx.tunLamp.intensity = 0; ctx.coilKey.intensity = 0; ctx.coilFill.intensity = 0; ctx.lbFill.intensity = 0;
  if (t < 3.0) {
    // low glide along the coils, the bulbs ahead rim-light the wire
    const k = t / 3.0;
    camera.position.set(5.75 + Math.sin(t * 0.7) * 0.02, 1.42 + Math.sin(t * 0.9) * 0.01, lerp(6.2, 3.4, k));
    camera.lookAt(lerp(4.55, 4.75, k), 1.38, camera.position.z - 12);
    camera.rotateZ(-0.03);
    focus = 2.6; ctx.coilKey.intensity = 40; ctx.coilFill.intensity = 1.6;
  } else if (t < 5.9) {
    const k = (t - 3.0) / 2.9;
    camera.position.set(lerp(5.1, 5.35, k), lerp(1.9, 1.95, k), lerp(-26.9, -27.4, k));
    camera.lookAt(7.95, lerp(2.35, 2.4, k), lerp(-29.75, -29.85, k));
    focus = camera.position.distanceTo(new THREE.Vector3(7.95, 2.0, -29.6));
    
  } else if (t < 8.6) {
    const k = (t - 5.9) / 2.7;
    camera.position.set(lerp(2.6, 2.45, k), lerp(1.75, 1.85, k), lerp(-49.4, -50.6, k));
    camera.lookAt(2.2, 2.0, -60);
    focus = 9;
    ctx.shutLamp.intensity = 48; ctx.tunLamp.intensity = 14;
  } else {
    const k = (t - 8.6) / 4.1;
    camera.position.set(lerp(3.75, 3.6, k), lerp(0.85, 0.8, k), lerp(-32.2, -35.0, k));
    camera.lookAt(lerp(1.2, 1.4, k), 0.55, -50);
    focus = 6; ctx.lbFill.intensity = 18;
  }
  // weld seams: deposited at tw, glowing and cooling afterwards
  const dummy = new THREE.Object3D(); let arcAt = null;
  ctx.beads.forEach((b, i) => {
    const age = t - b.tw;
    const s = age < 0 ? 0.0001 : Math.min(1, 0.4 + age * 6);
    dummy.position.copy(b.p); dummy.scale.set(0.7 * s, s, 1.15 * s); dummy.rotation.set(0, 0, 0); dummy.updateMatrix(); ctx.beadMesh.setMatrixAt(i, dummy.matrix);
    ctx.heat[i] = age < 0 ? 0 : Math.exp(-age / 0.9) * 0.95 + Math.exp(-age / 4.5) * 0.25;
    if (age >= 0 && age < 0.06 && t > 3.0 && t < 5.4) arcAt = b.p;
  });
  ctx.beadMesh.instanceMatrix.needsUpdate = true; ctx.beadMesh.geometry.attributes.heat.needsUpdate = true;
  if (arcAt) {
    const fl = 0.55 + 0.45 * hash(Math.floor(t * 40));
    ctx.arcLight.position.set(arcAt.x - 0.45, arcAt.y, arcAt.z); ctx.arcLight.intensity = 2.0 * fl;
    ctx.arcGlow.position.set(arcAt.x - 0.03, arcAt.y, arcAt.z); ctx.arcGlow.material.opacity = fl; ctx.arcGlow.scale.setScalar(0.35 + 0.25 * fl);
    ctx.arcGlow2.position.copy(ctx.arcGlow.position); ctx.arcGlow2.material.opacity = 0.6 * fl;
  }
  // sparks
  const sp = ctx.sparkLines.geometry.attributes.position.array, sc = ctx.sparkLines.geometry.attributes.color.array;
  const seamAt = (tt) => { const b = ctx.beads.reduce((best, x) => Math.abs(x.tw - tt) < Math.abs(best.tw - tt) ? x : best); return b.p; };
  ctx.sparks.forEach((s, i) => {
    const age = t - s.t0; let a = 0;
    if (age > 0 && age < s.life && t < 6.2) {
      if (!s.o) s.o = seamAt(s.t0).clone();
      const pos = (tt) => [s.o.x - 0.03 + s.v[0] * tt, Math.max(1.0, s.o.y + s.v[1] * tt - 4.9 * tt * tt), s.o.z + s.v[2] * tt];
      const p1 = pos(age), p0 = pos(Math.max(0, age - 0.035));
      sp.set([...p0, ...p1], i * 6); a = (1 - age / s.life);
    } else sp.set([0, -10, 0, 0, -10, 0], i * 6);
    const c = [1.6 * a, 0.95 * a * a, 0.45 * a * a * a];
    sc.set([...c, ...c], i * 6);
  });
  ctx.sparkLines.geometry.attributes.position.needsUpdate = true; ctx.sparkLines.geometry.attributes.color.needsUpdate = true;
  // roller shutter comes down from 5.9 s
  const sk = smooth((t - 6.0) / 3.0);
  const yb = lerp(ctx.SH - 0.15, 0.0, sk) + (sk > 0 && sk < 1 ? Math.sin(t * 23) * 0.006 : 0);
  ctx.shutter.position.y = yb + ctx.SH / 2; ctx.bottomBar.position.y = yb + 0.05;
  ctx.tunGlow.material.opacity = ctx.tunLamp.intensity > 0 ? 0.8 : 0;
  // light barriers switch on one by one, then one flickers (something crossed it)
  ctx.barriers.forEach((b) => {
    const on = t - (9.3 + b.i * 0.28 + (b.y > 0.6 ? 0.12 : 0));
    let v = on < 0 ? 0 : on < 0.25 ? (hash(Math.floor(on * 40) + b.i * 7) > 0.4 ? 1 : 0.1) : 1;
    let tripped = false;
    if (b.i === 1 && b.y < 0.6 && t > 11.3 && t < 12.05) { const ph = Math.floor((t - 11.3) * 14); v = (ph % 3 === 1 || ph === 5 || ph === 6) ? 0.05 : 1; tripped = true; }
    if (b.i === 1 && b.y < 0.6 && t > 11.3 && t < 13.5) tripped = true;
    v *= 0.94 + 0.06 * Math.sin(t * 31 + b.i);
    b.core.material.opacity = 0.9 * v; b.halo.material.opacity = 0.09 * v; b.g1.material.opacity = v; b.g2.material.opacity = 0.7 * v;
    b.lens1.material.color.setRGB(0.13 + 0.85 * v, 0.1 + 0.75 * v, 0.06 + 0.6 * v);
    const led = on < 0 ? 0 : tripped ? (Math.floor(t * 6) % 2 ? 1 : 0.15) : 0.35;
    b.led.material.color.setRGB(0.07 + led, 0.04 + led * 0.6, 0.02 + led * 0.25); b.ledG.material.opacity = led;
  });
  u.lp.value[0].set(0, -100, 0); u.li.value[0] = 0;
  ctx.dust.visible = !(t >= 5.9 && t < 8.6);
  if (ctx.bokeh) { ctx.bokeh.uniforms.focus.value = focus; ctx.bokeh.uniforms.aperture.value = t < 3.0 ? 0.0014 : 0.0005; }
}

function updateLine(ctx, t) {
  const { THREE, camera, LZ } = ctx; const TWL = 3.9;
  // slow train: ~2.85 m/s, crossing the line at ~5.6 s
  const z = 4.0 - 2.85 * t;
  const sway = Math.sin(t * 2.1) * 0.012 + Math.sin(t * 5.3) * 0.005;
  camera.position.set(1.85 + sway, 2.3 + Math.sin(t * 7.1) * 0.006, z);
  // the driver turns his head to watch the line come up on the right, then looks ahead into the East
  const w = smooth((t - 1.2) / 2.0) * (1 - smooth((t - 5.0) / 1.8));
  const yaw = w * Math.min(0.62, Math.atan2(TWL - 1.85, Math.max(0.3, z - LZ)) * 0.95);
  const pitch = 0.05 * w - 0.04;
  camera.lookAt(camera.position.x + Math.sin(yaw) * 10, camera.position.y + pitch * 10, z - Math.cos(yaw) * 10);
  camera.rotateZ(sway * 0.4);
  const dir = new THREE.Vector3(); camera.getWorldDirection(dir);
  const hp = new THREE.Vector3(1.85, 1.15, z - 0.4);
  const ht = new THREE.Vector3(1.6, 1.1, z - 25);
  ctx.head.position.copy(hp); ctx.head.target.position.copy(ht);
  aimBeam(THREE, ctx.hb, hp, ht);
  const u = ctx.dust.material.uniforms; u.lp.value[0].copy(hp); u.ld.value[0].subVectors(ht, hp).normalize(); u.lc.value[0] = Math.cos(0.42); u.li.value[0] = 1.6;
  // mood: warm before the line, cold grey after
  const past = smooth((LZ + 1.0 - z) / 3.0);
  ctx.finish.uniforms.keepWarm.value = lerp(1.0, 0.25, past);
  ctx.scene.fog.color.setRGB(lerp(0.03, 0.022, past), lerp(0.024, 0.024, past), lerp(0.018, 0.026, past));
  ctx.warm.forEach((l, i) => { l.l.intensity = l.base * (0.9 + 0.1 * Math.sin(t * 9 + i)); });
  ctx.cold.forEach((l, i) => { const f = hash(Math.floor(t * 10) + i * 13) < 0.08 ? 0.3 : 1; l.l.intensity = l.base * f; l.h.material.opacity = 0.75 * f; });
  ctx.guard.head.rotation.y = smooth((t - 6) / 2) * 0.5;
}
