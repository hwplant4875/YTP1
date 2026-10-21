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
