// The thumbnail scene: the thing on the ceiling reaching down over you, its face a lit red screen with a lens.
window.drawThumb = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ln(WALL, CEIL, W + 40, CEIL, 5, '#3a3a3a'); ln(WALL, CEIL, WALL, FY, 5, '#3a3a3a'); ln(WALL, FY, W + 40, FY, 5, '#3a3a3a');
  bed(BX, FY, 1.05, 'sleep', {});
  cornerThing(0, { vis: 1, lit: 1, face: 'lens', red: 1, reach: o.reach ?? 1, breath: 0, body: '#e8e8e8', edge: '#ffffff', faceFill: '#ff2a2a' });
  ctx.save(); ctx.setLineDash([18, 14]); ctx.lineCap = 'round'; ln(LENS.x, LENS.y + 14, HEAD_S.x + 6, HEAD_S.y - 30, 8, '#ff2a2a'); ctx.restore();
  ctx.save(); redGlow(20); circ(LENS.x, LENS.y, 8, '#ff2a2a'); ctx.restore();
};
// Thumbnail v2 (user): black background, the top of the phone very large, the AI's photo of you asleep clearly visible.
window.drawThumbPhoneRed = () => window.drawThumbPhone({ red: true });
window.drawThumbPhone = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const s = o.s ?? 1.9, px = o.x ?? 540;
  if (o.red) { const g = ctx.createRadialGradient(px, 560, 300, px, 560, 720); g.addColorStop(0, 'rgba(255,30,40,0.5)'); g.addColorStop(1, 'rgba(255,30,40,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  phone(px, 14 + (SH / 2 + 10) * s, s, () => chatScreen(9, [{ ...M_AWAKE }, { photo: PHOTO('03:00:41', 1.15), pw: 286, ph: 310, at: -1 }], { time: '3:00' }), { rot: o.rot ?? -0.05 });
};
// Thumbnail v3 (user): the phone wide in the centre of a black frame, only its top half in view, the title above it.
// A compact chat screen so the photo of you asleep fills what is visible.
window.drawThumbWideRed = () => window.drawThumbWide({ red: true });
window.drawThumbWide = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const s = o.s ?? 2.65, top = o.top ?? 238;
  if (o.red) { const g = ctx.createRadialGradient(W / 2, 1000, 300, W / 2, 1000, 1100); g.addColorStop(0, 'rgba(255,30,40,0.55)'); g.addColorStop(1, 'rgba(255,30,40,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  phone(W / 2, top + (SH / 2 + 16) * s, s, () => {
    rr(0, 0, SW, SH, 0, '#0a0a0a'); statusBar('3:00');
    pthS('M26,74 l-10,10 l10,10', '#bdbdbd', 3.5); aiAvatar(58, 84, 15); text('Assistant', 84, 91, `600 20px ${UI}`, '#f2f2f2', 'left');
    ln(0, 112, SW, 112, 1.5, '#222');
    aiAvatar(28, 140, 11); rr(48, 120, 182, 42, 20, '#262626'); text('Are you awake?', 64, 148, `500 21px ${UI}`, '#f2f2f2', 'left');
    aiAvatar(28, 194, 11);
    const x = 48, y = 176, w = 300, h = 230;
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 18); ctx.clip(); ceilPhoto(x, y, w, h, { zoom: o.zoom ?? 1.9 }); ctx.restore(); rrS(x, y, w, h, 18, '#333', 2);
    ctx.save(); redGlow(6); text('03:00:41', x + w - 12, y + 30, '600 19px Plex', '#ff4a2a', 'right'); ctx.restore();   // the time stamp, moved to the top so it stays in view
  });
};
