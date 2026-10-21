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
// v2 (user 10/21: more eye-catching): close on the glass. Your reflection writes RUN while the tall thing stands right behind it,
// red eyes over its head, long grey fingers on its shoulders. The back of your head in the lower left. Clean frame for the colour mapping in thumbs_v2.py.
window.drawThumb2 = (o = {}) => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const c = { x: o.cx ?? 0.42, y: o.cy ?? 1.62, z: o.cz ?? 1.55, yaw: o.yaw ?? 0.12, pitch: o.pitch ?? 0.06, f: o.f ?? 1250 };
  const dy = o.dy ?? 0.16, tip = [RUN_END[0], RUN_END[1] + dy, RUN_END[2]];
  const rp = o.run === false ? poseOf({ x: o.rx ?? 0.05, z: o.rz ?? 0.6 }) : writerPose(tip), me = o.same ? rp : poseOf({ x: o.mx ?? -0.25, z: o.mz ?? 0.95 });
  ctx.save(); ctx.translate(o.tx ?? 0, o.ty ?? 0);
  if (o.layer) {   // one figure alone on black (for the flat white thumbnail): thing | refl | fingers | me
    setCam(c); const th = { x: o.thx ?? 0.2, z: o.thz ?? -1.15, t: 0, col: '#ffffff', eyes: '#ff2a2a', sc: o.thsc ?? 1.08 };
    if (o.layer === 'me') { if (me.z < CAM.z - 0.2) body3(me, {}); }
    else { ctx.save(); if (clipGlass()) { ctx.fillStyle = '#000'; ctx.fillRect(-W, -H, 3 * W, 3 * H);
      if (o.layer === 'thing') thing3(th.x, th.z, th);
      if (o.layer === 'refl') body3(rp, { mirror: true, col: '#ffffff' });
      if (o.layer === 'fingers') heldBack(skeleton(rp), 1); } ctx.restore(); }
    ctx.restore(); return;
  }
  bathroom(0, { cam: c, me, refl: rp, door: 0, thing: { x: o.thx ?? 0.2, z: o.thz ?? -1.15, t: 0, col: '#c8c8ce', eyes: '#ff2a2a', sc: o.thsc ?? 1.08 }, light: 1,
    inMirror: () => { heldBack(skeleton(rp), 1); if (o.run !== false) reflFinger(rp, tip); }, glassFx: () => { }, front: () => {} });
  if (o.run !== false) { ctx.save(); redGlow(30); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const s of runStrokes()) { const sp = s.pts.map(p => prj([p[0], p[1] + dy, 0])); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]);
    ctx.strokeStyle = '#ff2030'; ctx.lineWidth = 0.03 * sp[0][3]; ctx.stroke(); } ctx.restore(); }
  ctx.restore();
};
window.drawT2a = () => drawThumb2({ run: false, thx: 0.38, thsc: 0.98, cx: 0.3, cz: 1.9, f: 1350, yaw: 0.08, mx: -0.35, mz: 1.05 });
window.drawT2b = () => drawThumb2({ run: false, thx: 0.0, thz: -1.0, thsc: 1.0, rx: 0.05, cx: 0.25, cz: 1.9, f: 1450, yaw: 0.06, pitch: 0.08, mx: -0.4, mz: 1.1 });
window.drawT2c = () => drawThumb2({ thx: 0.45, thsc: 0.95, dy: 0.12, cx: 0.3, cz: 1.9, f: 1300, yaw: 0.08, mx: -0.35, mz: 1.05 });

window.drawT2d = () => drawThumb2({ run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.0, thz: -1.0, thsc: 1.0, cx: 0.32, cy: 1.75, cz: 1.55, f: 1500, yaw: 0.17, pitch: 0.02 });
window.drawT2e = () => drawThumb2({ run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.02, thz: -0.95, thsc: 1.0, cx: 0.42, cy: 1.8, cz: 1.75, f: 1750, yaw: 0.2, pitch: 0.0 });
window.drawT2f = () => drawThumb2({ run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.0, thz: -1.0, thsc: 1.0, cx: 0.25, cy: 1.72, cz: 1.4, f: 1300, yaw: 0.14, pitch: 0.05 });
window.drawT2g = () => drawThumb2({ run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.02, thz: -0.95, thsc: 1.0, cx: 0.42, cy: 1.8, cz: 1.75, f: 2050, yaw: 0.2, pitch: 0.0, tx: -260, ty: -60 });
window.T2G = { run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.02, thz: -0.95, thsc: 1.0, cx: 0.42, cy: 1.8, cz: 1.75, f: 2050, yaw: 0.2, pitch: 0.0, tx: -260, ty: -60 };
for (const l of ['thing', 'refl', 'fingers', 'me']) window['drawT2g_' + l] = () => drawThumb2({ ...window.T2G, layer: l });
// POV: your own eyes in the mirror; you are not drawn, your reflection faces you, the thing stands right behind it
window.T2P = { run: false, same: true, rx: 0.0, rz: 0.6, thx: 0.05, thz: -1.0, thsc: 1.0, cx: 0.0, cy: 1.66, cz: 0.62, f: 1500, yaw: 0.0, pitch: 0.06, tx: -230, ty: 0 };
window.drawT2p = () => drawThumb2({ ...window.T2P });
for (const l of ['thing', 'refl', 'fingers', 'me']) window['drawT2p_' + l] = () => drawThumb2({ ...window.T2P, layer: l });
