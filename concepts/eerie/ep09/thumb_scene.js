// EP09 thumbnails: pure black, the white dog, human teeth with red gums, huge DON'T SMILE BACK.
function thTitle(a, b, y, size, x = W / 2, align = 'center') {
  ctx.save(); ctx.font = `900 ${size}px M`; const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width;
  const x0 = align === 'center' ? x - (wa + wb) / 2 : x;
  text(a, x0, y, `900 ${size}px M`, '#fff', 'left'); redGlow(26); text(b, x0 + wa, y, `900 ${size}px M`, C.red, 'left'); ctx.restore();
}
const thBg = () => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); };
// A: the dog's face huge on the right, the title on the left in three lines
window.drawThumbA = () => {
  thBg();
  dogFace(1330, 560, 1.95, { smile: 1 });
  ctx.save(); text("DON'T", 80, 380, '900 190px M', '#fff', 'left'); redGlow(30); text('SMILE', 80, 580, '900 190px M', C.red, 'left'); text('BACK', 80, 780, '900 190px M', C.red, 'left'); ctx.restore();
};
// B: the face centred, red eyes, the title above
window.drawThumbB = () => {
  thBg();
  dogFace(960, 650, 1.5, { smile: 1, eye: 1 });
  thTitle("DON'T ", 'SMILE BACK', 170, 150);
};
// C: the dog at your table, sitting up in the chair, smiling; the title above
window.drawThumbC = () => {
  thBg();
  ctx.save(); ctx.translate(1340, 600); ctx.scale(2.3, 2.3); ctx.translate(-1330, -470);
  floorLine(); chair(1420, 1, -1); dog(1424, FL - 176, 1.0, { dir: -1, rear: 1, sit: 1, eye: 1, reach: [1255, 596], reachK: 1, smile: 1 });
  table(620, 1300); plate(1140, 600, 1, { fork: true });
  ctx.restore();
  ctx.save(); text("DON'T", 80, 330, '900 170px M', '#fff', 'left'); redGlow(30); text('SMILE', 80, 510, '900 170px M', C.red, 'left'); text('BACK', 80, 690, '900 170px M', C.red, 'left'); ctx.restore();
};
// design frames for the v2 teeth
window.drawDesFront = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); dogFace(960, 420, 1.9, { smile: 1 }); };
window.drawDesMouth = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.save(); ctx.translate(960, 300); ctx.scale(4.2, 4.2); ctx.translate(0, -90); dogFace(0, 0, 1, { smile: 1 }); ctx.restore(); };
window.drawDesSide = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); dogProfileBig(820, 470, 6.0, { smile: 1 }); };
window.drawDesSteps = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); [0, 0.35, 0.7, 1].forEach((k, i) => dogFace(240 + i * 480, 330, 0.85, { smile: k }));
  [0, 0.4, 0.7, 1].forEach((k, i) => { ctx.save(); ctx.translate(150 + i * 480, 860); ctx.scale(2.2, 2.2); dogHead({ smile: k }); ctx.restore(); }); };
window.drawDesMid = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); floorLine(); dog(1100, FL, 1.3, { sit: 1, smile: 1, dir: -1 }); you(500, FL, 1, {}); };
window.drawDesLost = () => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); dogFace(500, 470, 1.1, { smile: 1, lost: 5, snarl: 1 }); dogFace(1420, 470, 1.1, { smile: 1, lost: 10, fang: 1, snarl: 1 }); };
