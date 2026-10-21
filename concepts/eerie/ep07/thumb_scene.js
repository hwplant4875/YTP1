// EP07 thumbnails, benchmark style: pure black, flat white figures, one red danger element, huge DON'T TELL THE TRUTH.
function thTitle(a, b, y, size, x = W / 2, align = 'center') {
  ctx.save(); ctx.font = `900 ${size}px M`; const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width;
  const x0 = align === 'center' ? x - (wa + wb) / 2 : x;
  text(a, x0, y, `900 ${size}px M`, '#fff', 'left'); redGlow(26); text(b, x0 + wa, y, `900 ${size}px M`, C.red, 'left'); ctx.restore();
}
const thBg = () => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); };
// 1: the panel of three, big, the middle one's eyes red; the title over them
window.drawThumbA = () => {
  thBg();
  const g = ctx.createRadialGradient(960, 600, 60, 960, 700, 900); g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(960, 0); ctx.scale(1.55, 1.55); ctx.translate(-960, -30);
  for (let i = 0; i < 3; i++) suit(560 + i * 400, 905, 1, { arms: i === 1 ? 'desk' : 'board', eyes: i === 1 ? 1 : 0 });
  desk(160, 1760, 620, { n: 3 });
  ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 190, 140);
};
// 2: just the middle one, huge, leaning in; red eyes; title on the left
window.drawThumbB = () => {
  thBg();
  ctx.save(); ctx.translate(1340, 0); ctx.scale(2.6, 2.6); ctx.translate(-960, -205);
  suit(960, 905, 1, { arms: 'desk', eyes: 1, lean: 0.8 });
  ctx.restore();
  ctx.save(); ctx.font = '900 170px M'; text("DON'T", 90, 380, '900 170px M', '#fff', 'left'); text('TELL THE', 90, 560, '900 170px M', '#fff', 'left'); redGlow(28); text('TRUTH', 90, 740, '900 170px M', C.red, 'left'); ctx.restore();
};
// 3: the clipboard: GREATEST WEAKNESS with the answer underlined in red, a faceless interviewer behind
window.drawThumbC = () => {
  thBg();
  ctx.save(); ctx.translate(1380, 0); ctx.scale(1.9, 1.9); ctx.translate(-960, -108); ctx.globalAlpha = 0.9;
  suit(960, 905, 1, { arms: 'desk', eyes: 1 }); ctx.restore();
  ctx.save(); ctx.translate(620, 640); ctx.rotate(-0.06); ctx.scale(3.2, 3.2);
  rr(-80, -88, 160, 180, 8, SUIT.board); rrS(-80, -88, 160, 180, 8, SUIT.line, 3); rr(-70, -70, 140, 154, 2, SUIT.paper);
  rr(-26, -96, 52, 22, 6, '#2a2a2e'); text('GREATEST', -60, -38, '900 17px M', '#222', 'left'); text('WEAKNESS:', -60, -16, '900 17px M', '#222', 'left');
  text('"I GET', -60, 22, '900 20px M', '#d61f1f', 'left'); text('NERVOUS"', -60, 46, '900 20px M', '#d61f1f', 'left');
  ln(-62, 54, 44, 52, 3.5, '#d61f1f'); ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 130);
};
