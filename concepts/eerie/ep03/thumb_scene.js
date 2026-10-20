// EP03 thumbnail scenes (concatenated into engine_th.js by build.sh). The mirror, close and straight on:
// RUN written in the fog from the other side, your reflection's finger still on it, the tall thing behind it in the doorway, the back of your head in front.
window.drawThumb = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const c = { x: 0.32, y: 1.62, z: 1.75, yaw: 0.06, pitch: 0.03, f: 1500 };
  const dy = 0.2, tip = [RUN_END[0], RUN_END[1] + dy, RUN_END[2]];   // letters raised above the reflection's face so the face stays readable
  const rp = writerPose(tip), me = poseOf({ x: -0.3, z: 1.05 });
  ctx.save(); ctx.translate(-230, 70);
  bathroom(0, { cam: c, me, refl: rp, door: 1, thing: { x: 0.25, z: -3.0, t: 0, inDoor: true, col: '#c8c8ce', eyes: '#ff2a2a' }, fog: 0.8, run: [0, 0, 0], light: 1,
    inMirror: () => reflFinger(rp, tip),
    glassFx: () => { },
    front: () => {} });
  // the letters, lit red where they cut through the fog
  if (o.redRun !== false) { ctx.save(); redGlow(30); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (const s of runStrokes()) { const sp = s.pts.map(p => prj([p[0], p[1] + dy, 0])); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]);
      ctx.strokeStyle = 'rgba(255,40,50,0.9)'; ctx.lineWidth = 0.03 * sp[0][3]; ctx.stroke(); } ctx.restore(); }
  ctx.restore();
  if (o.red) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = '#ff3b3b'; ctx.fillRect(0, 0, W, H); ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.25; ctx.fillStyle = '#5a0006'; ctx.fillRect(0, 0, W, H); ctx.restore();
    // on the red version the letters burn white-hot so they still read against the red
    ctx.save(); ctx.translate(-230, 70); redGlow(40); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (const s of runStrokes()) { const sp = s.pts.map(p => prj([p[0], p[1] + dy, 0])); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]);
      ctx.strokeStyle = '#ffe2e2'; ctx.lineWidth = 0.022 * sp[0][3]; ctx.stroke(); } ctx.restore(); }
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.0); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.8)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
};
window.drawThumbRed = () => window.drawThumb({ red: true });
