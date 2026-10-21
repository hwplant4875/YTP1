// EP06 thumbnail scenes (concatenated into engine_th.js by build.sh): Halloween night, he stands under the streetlight
// across the street, big and centred, looking straight at your window. Title DON'T LOOK AWAY with AWAY in red.
// o.look: 'street' (the whole street, close on him), 'window' (seen through your window), 'black' (black, one cone of light, red glow)
window.drawThumb6 = (o = {}) => {
  const look = o.look || 'street';
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const him = { x: 1080, y: 642, s: 0.42, knife: 1, tilt: 0.1 };
  if (look === 'street') {
    streetScene(0, { scr: [960, 640], cam: [3.3, 1080, 480], him, kids: null });
  } else if (look === 'window') {
    windowPOV(0, { x0: 330, x1: 1590, y0: 250, y1: 1010, cross: false, close: 0,
      fn: () => streetScene(0, { scr: [960, 650], cam: [2.0, 1080, 520], him }) });
  } else {
    { const rg = ctx.createRadialGradient(960, 560, 40, 960, 600, 620); rg.addColorStop(0, 'rgba(170,14,14,0.75)'); rg.addColorStop(0.55, 'rgba(110,6,6,0.35)'); rg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H); }
    const g = ctx.createLinearGradient(0, 120, 0, 1080); g.addColorStop(0, 'rgba(255,250,235,0.20)'); g.addColorStop(1, 'rgba(255,250,235,0.03)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(900, 120); ctx.lineTo(1020, 120); ctx.lineTo(1420, 1080); ctx.lineTo(500, 1080); ctx.closePath(); ctx.fill();
    ctx.save(); ctx.globalAlpha = 0.3; ell(960, 1040, 420, 50, 0, '#fff7e6'); ctx.restore();
    myers(960, 1240, 1.45, { knife: 1, tilt: 0.1, red: 1 });
  }
  // the title
  const ty = look === 'window' ? 175 : 175;
  ctx.save(); ctx.font = '900 168px M'; const a = "DON'T LOOK ", b = 'AWAY', wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = W / 2 - (wa + wb) / 2;
  ctx.shadowColor = 'rgba(0,0,0,0.95)'; ctx.shadowBlur = 34;
  text(a, x0, ty, '900 168px M', '#fff', 'left'); redGlow(24); text(b, x0 + wa, ty, '900 168px M', C.red, 'left'); ctx.restore();
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.05); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.7)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
};
window.drawThumb6s = () => window.drawThumb6({ look: 'street' });
window.drawThumb6w = () => window.drawThumb6({ look: 'window' });
window.drawThumb6b = () => window.drawThumb6({ look: 'black' });
// design check: the man big on grey, front and profile
window.drawMaskTest = () => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#0a0a0c'; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(560, 1500); ctx.scale(2.6, 2.6); maskHead(0, -505, 1, {}); ctx.restore();
  myers(1150, 1050, 1.5, { knife: 1 });
  myersSide(1650, 1050, 1.5, { dir: -1, knife: 1 });
};
// EP04 CCTV, benchmark style: pure black, one flat white sofa, a long pale hand reaching out from the dark gap under it, two red eyes
window.drawCctvSimple = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const F = '#f4f4f6';
  ctx.save(); glow('rgba(255,255,255,0.45)', 40);
  rr(370, 470, 900, 230, 40, F);                 // back
  rr(300, 560, 150, 280, 40, F); rr(1190, 560, 150, 280, 40, F);   // arms
  rr(420, 660, 800, 150, 26, F);                 // seat
  noGlow(); ctx.restore();
  ln(820, 668, 820, 800, 6, '#000');             // the two cushions
  rr(340, 840, 960, 80, 0, '#000');             // the dark gap under it
  rr(330, 840, 50, 75, 8, F); rr(1260, 840, 50, 75, 8, F);   // feet
  // two red eyes in the gap
  ctx.save(); redGlow(30); ell(780, 880, 20, 9, 0, C.red); ell(860, 880, 20, 9, 0, C.red); noGlow(); ctx.restore();
  // a long thin pale arm out along the floor, its hand around your ankle
  ctx.save(); redGlow(22);
  pthS('M920,882 C1200,892 1380,902 1560,900', C.red, 20);
  for (const k of [0, 1, 2, 3]) pthS(`M1555,${890 + k * 6} C1590,${862 + k * 8} 1620,${870 + k * 9} 1612,${906 + k * 3}`, C.red, 8);
  noGlow(); ctx.restore();
  rr(1260, 840, 50, 75, 8, F);
  me(1640, 915, 1.25, { face: 'front' });
  // title
  ctx.save(); ctx.font = '900 190px M'; const a = "DON'T BE ", b = 'HOME', wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = W / 2 - (wa + wb) / 2;
  text(a, x0, 250, '900 190px M', '#fff', 'left'); redGlow(26); text(b, x0 + wa, 250, '900 190px M', C.red, 'left'); ctx.restore();
};
// more EP04 CCTV thumbnails for "If You Ever See Yourself in the Security Camera… DON'T BE HOME AT 3 AM"
function cctvTitle(a, b, y, size) {
  ctx.save(); ctx.font = `900 ${size}px M`; const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = W / 2 - (wa + wb) / 2;
  text(a, x0, y, `900 ${size}px M`, '#fff', 'left'); redGlow(26); text(b, x0 + wa, y, `900 ${size}px M`, C.red, 'left'); ctx.restore();
}
function camBrackets(x0, y0, x1, y1, col = '#f2f2f2', L = 70, w = 7) {
  ctx.save(); ctx.lineWidth = w; ctx.strokeStyle = col; ctx.lineCap = 'square';
  for (const [x, y, sx, sy] of [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]]) { ctx.beginPath(); ctx.moveTo(x, y + sy * L); ctx.lineTo(x, y); ctx.lineTo(x + sx * L, y); ctx.stroke(); }
  ctx.restore();
}
function simpleSofa(x, y, s, F = '#f4f4f6') {   // origin = floor at the sofa's centre
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.45)', 40);
  rr(-450, -450, 900, 230, 40, F); rr(-520, -360, 150, 280, 40, F); rr(370, -360, 150, 280, 40, F); rr(-400, -260, 800, 150, 26, F);
  noGlow(); ln(0, -252, 0, -120, 6, '#000'); rr(-480, -80, 960, 80, 0, '#000'); rr(-490, -80, 50, 75, 8, F); rr(440, -80, 50, 75, 8, F);
  ctx.restore();
}
// 2: the camera's picture: brackets, REC, 03:00, you asleep on the sofa, red eyes under it
window.drawCctv2 = () => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  camBrackets(70, 70, W - 70, H - 70);
  simpleSofa(960, 930, 0.95, '#55555c');
  // you, lying on the sofa
  ctx.save(); glow('rgba(255,255,255,0.4)', 20); circ(600, 600, 46, '#fff'); rr(640, 575, 520, 60, 28, '#fff'); noGlow(); circ(612, 592, 6, '#000'); circ(590, 592, 6, '#000'); ctx.restore();
  ctx.save(); redGlow(30); ell(905, 893, 20, 9, 0, C.red); ell(985, 893, 20, 9, 0, C.red); noGlow(); ctx.restore();
  ctx.save(); redGlow(16); circ(W - 270, 160, 22, C.red); ctx.restore(); text('REC', W - 232, 183, '700 64px Plex', '#f2f2f2', 'left');
  ctx.save(); redGlow(18); text('03:00 AM', 140, 183, '700 64px Plex', C.red, 'left'); ctx.restore();
  cctvTitle("DON'T BE ", 'HOME', 400, 170);
};
// 3: a huge red 3:00 AM, you small in the camera's brackets
window.drawCctv3 = () => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ctx.save(); redGlow(40); text('3:00 AM', W / 2, 560, '900 330px M', C.red, 'center'); ctx.restore();
  camBrackets(1380, 640, 1700, 1010, '#f2f2f2', 50, 6);
  me(1540, 980, 0.9, { face: 'front' });
  ctx.save(); redGlow(14); circ(1420, 690, 12, C.red); ctx.restore();
  ctx.save(); ctx.font = '900 120px M'; text("DON'T BE HOME", 120, 900, '900 120px M', '#fff', 'left'); ctx.restore();
};
// 4: a white security camera on the wall, a red light, its view cone onto you standing in the dark
window.drawCctv4 = () => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createLinearGradient(400, 380, 1300, 1000); g.addColorStop(0, 'rgba(255,255,255,0.16)'); g.addColorStop(1, 'rgba(255,255,255,0.02)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(470, 400); ctx.lineTo(1500, 760); ctx.lineTo(1000, 1080); ctx.lineTo(430, 470); ctx.closePath(); ctx.fill();
  ctx.save(); glow('rgba(255,255,255,0.45)', 30); rr(150, 300, 50, 160, 10, '#f4f4f6');
  ctx.translate(200, 380); ctx.rotate(0.45); rr(0, -60, 300, 120, 30, '#f4f4f6'); rr(280, -48, 50, 96, 12, '#f4f4f6'); noGlow(); circ(316, 0, 30, '#000'); ctx.restore();
  ctx.save(); redGlow(18); circ(245, 470, 13, C.red); ctx.restore();
  me(1180, 960, 1.15, { face: 'front' });
  cctvTitle("DON'T BE ", 'HOME', 210, 170);
  ctx.save(); redGlow(18); text('AT 3 AM', W / 2 + 120, 340, '900 90px M', C.red, 'center'); ctx.restore();
};
