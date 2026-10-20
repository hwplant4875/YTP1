// The thumbnail scene: the thing on the ceiling reaching down over you, its face a lit red screen with a lens.
window.drawThumb = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ln(WALL, CEIL, W + 40, CEIL, 5, '#3a3a3a'); ln(WALL, CEIL, WALL, FY, 5, '#3a3a3a'); ln(WALL, FY, W + 40, FY, 5, '#3a3a3a');
  bed(BX, FY, 1.05, 'sleep', {});
  cornerThing(0, { vis: 1, lit: 1, face: 'lens', red: 1, reach: o.reach ?? 1, breath: 0, body: '#e8e8e8', edge: '#ffffff', faceFill: '#ff2a2a' });
  ctx.save(); ctx.setLineDash([18, 14]); ctx.lineCap = 'round'; ln(LENS.x, LENS.y + 14, HEAD_S.x + 6, HEAD_S.y - 30, 8, '#ff2a2a'); ctx.restore();
  ctx.save(); redGlow(20); circ(LENS.x, LENS.y, 8, '#ff2a2a'); ctx.restore();
};
