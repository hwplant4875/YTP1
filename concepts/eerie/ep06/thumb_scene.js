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
