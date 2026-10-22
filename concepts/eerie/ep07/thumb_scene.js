// EP07 thumbnails, benchmark style: pure black, flat white figures, one red danger element, huge DON'T TELL THE TRUTH.
function thTitle(a, b, y, size, x = W / 2, align = 'center') {
  ctx.save(); ctx.font = `900 ${size}px M`; const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width;
  const x0 = align === 'center' ? x - (wa + wb) / 2 : x;
  text(a, x0, y, `900 ${size}px M`, '#fff', 'left'); redGlow(26); text(b, x0 + wa, y, `900 ${size}px M`, C.red, 'left'); ctx.restore();
}
const thBg = () => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); };
// 1: the three agents at the desk, big; the middle one's lenses red; the title over them
window.drawThumbA = () => {
  thBg();
  const g = ctx.createRadialGradient(960, 700, 60, 960, 760, 900); g.addColorStop(0, 'rgba(255,255,255,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(960, 1080); ctx.scale(1.45, 1.45); ctx.translate(-960, -880);
  agent('young', 560, 760, 1, { arms: 'desk' }); agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1 }); agent('boss', 1360, 760, 1, { arms: 'desk' });
  meetDesk(200, 1720, 760, { items: false });
  ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 140);
};
// 2: just the middle one, huge, red lenses; the title on the left
window.drawThumbB = () => {
  thBg();
  ctx.save(); ctx.translate(1400, 1080); ctx.scale(2.5, 2.5); ctx.translate(-960, -760);
  agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1, lean: 0.3 });
  ctx.restore();
  ctx.save(); text("DON'T", 90, 360, '900 170px M', '#fff', 'left'); text('TELL THE', 90, 550, '900 170px M', '#fff', 'left'); redGlow(28); text('TRUTH', 90, 740, '900 170px M', C.red, 'left'); ctx.restore();
};
// 3: the clipboard, LIVES ALONE underlined twice in red; the agent behind it
window.drawThumbC = () => {
  thBg();
  ctx.save(); ctx.translate(1420, 1080); ctx.scale(2.0, 2.0); ctx.translate(-960, -760); ctx.globalAlpha = 0.95;
  agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1 }); ctx.restore();
  ctx.save(); ctx.translate(560, 660); ctx.rotate(-0.06); clipboard(0, 0, 3.4, 0, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 1]], under: 2, up: 1 });
  ctx.scale(3.4, 3.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width; ln(-62, 40, -58 + w, 39, 3.5, '#d61f1f'); ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 130);
};
// v2 design sketches
window.drawDesign1 = () => {
  thBg(); meetRoom({ clock: [9, 0, 0] });
  agent('young', 560, 700, 1, { arms: 'desk' });
  agent('hr', 960, 700, 1, { arms: 'desk' });
  agent('boss', 1360, 700, 1, { arms: 'laptop', lid: 0 });
  meetDesk(260, 1660, 700);
};
window.drawDesign2 = () => {
  thBg(); meetRoom({ clock: [9, 0, 0] });
  for (const [k, x, o] of [['young', 330, {}], ['hr', 960, { eyes: 1 }], ['boss', 1590, {}]]) { ctx.save(); ctx.translate(x, 480); ctx.scale(2.4, 2.4); ppHead(k, o); ctx.restore(); }
};
window.drawDesign3 = () => {
  thBg(); meetRoom({ clockAt: false });
  agent('young', 560, 1000, 0.8, { stand: 1, arms: 'down' });
  agent('hr', 960, 1000, 0.8, { stand: 1, arms: 'hand', reach: 0.6, eyes: 1 });
  agent('boss', 1360, 1000, 0.8, { stand: 1, arms: 'down' });
};
