// EP04 thumbnail scenes (concatenated into engine_th.js by build.sh). Close and from above, as the security camera would catch it:
// the long pale head out from under the sofa, one red eye up at you, its many-jointed arm dragging someone in by the ankle.
// o.look: 'white' (flat white on black), 'cam' (the grey security-camera picture with REC), 'red' (red background)
window.drawThumb4 = (o = {}) => {
  const look = o.look || 'white';
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); if (look !== 'red') { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
  const ankle = [SPOT.x - 0.1, SPOT.z + 0.03];
  setCam(o.cam || { ...CAMS.cctv, yaw: 0.8, pitch: -0.5, f: 1380 });
  const inv = look === 'red', fig = inv ? '#111' : '#f4f4f6', thing = inv ? '#1a1a1a' : '#8e8e95';
  ctx.save(); ctx.translate(o.dx ?? -190, o.dy ?? 215);
  if (inv) { sofa4(); } else living(0.4, { moon: 0 });
  ctx.save(); ctx.globalAlpha = 0.9; polyW([[SOFA.x0 + 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 + 0.1], [SOFA.x0 + 0.04, 0.003, SOFA.z1 + 0.1]], '#000', null); ctx.restore();
  body3(poseOf({ look: 0.5 }), { col: fig, top: fig, hood: true, glow: inv ? 'rgba(0,0,0,0)' : undefined });
  thingArm(0.4, { k: 1, to: ankle, grip: true, col: thing });
  if (!o.noHead) thingHead(0.4, THING_X, 1, { col: thing, size: o.size || 2.75 });
  ctx.restore();
  // the security camera's marks: corners, REC, tomorrow's date
  const tx = look === 'red' ? '#111' : '#f2f2f2';
  ctx.save(); ctx.lineWidth = 8; ctx.strokeStyle = tx; ctx.lineCap = 'square';
  for (const [x, y, sx, sy] of [[70, 70, 1, 1], [W - 70, 70, -1, 1], [70, H - 70, 1, -1], [W - 70, H - 70, -1, -1]]) { ctx.beginPath(); ctx.moveTo(x, y + sy * 110); ctx.lineTo(x, y); ctx.lineTo(x + sx * 110, y); ctx.stroke(); }
  ctx.restore();
  if (look !== 'white') { ctx.save(); if (look === 'cam') redGlow(16); circ(W - 260, H - 135, 22, look === 'red' ? '#111' : C.red); ctx.restore(); text('REC', W - 222, H - 112, '700 64px Plex', tx, 'left'); }
  ctx.save(); if (look !== 'red') redGlow(18); text('TOMORROW', 600, H - 112, '700 64px Plex', look === 'red' ? '#111' : C.red, 'right'); ctx.restore();
  text('03:02', 640, H - 112, '700 64px Plex', tx, 'left');
  // the title
  ctx.save(); ctx.font = '900 178px M'; const a = "DON'T BE ", b = 'HOME', wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = W / 2 - (wa + wb) / 2;
  if (look !== 'red') { ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 30; }
  text(a, x0, 230, '900 178px M', look === 'red' ? '#111' : '#fff', 'left');
  if (look !== 'red') redGlow(24); text(b, x0 + wa, 230, '900 178px M', look === 'red' ? '#fff' : C.red, 'left'); ctx.restore();
  if (look === 'cam') { ctx.save(); ctx.globalCompositeOperation = 'color'; ctx.globalAlpha = 0.35; ctx.fillStyle = '#7a8a86'; ctx.fillRect(0, 0, W, H); ctx.restore();
    ctx.save(); ctx.globalAlpha = 0.08; for (let y = 0; y < H; y += 6) rr(0, y, W, 2, 0, '#000'); ctx.restore(); }
  if (look === 'red') { ctx.save(); ctx.globalCompositeOperation = 'destination-over'; ctx.fillStyle = '#e01818'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.05); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, look === 'red' ? 'rgba(60,0,0,0.6)' : 'rgba(0,0,0,0.75)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
};
window.drawThumb4w = () => window.drawThumb4({ look: 'white' });
window.drawThumb4c = () => window.drawThumb4({ look: 'cam' });
window.drawThumb4r = () => window.drawThumb4({ look: 'red' });
window.drawThumb4n = () => window.drawThumb4({ look: 'white', noHead: true });
