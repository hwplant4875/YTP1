// "Data Marble Race" preview: 16 countries, marble size scaled by population, physics precomputed in sim.mjs.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = t => 1 - Math.pow(1 - t, 3);
const easeOutBack = t => { const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
export const LEAD = 0.8;          // seconds of video before the sim starts
const POP = p => p >= 1000 ? (p / 1000).toFixed(2).replace(/0$/, '') + 'B' : (p >= 10 ? Math.round(p) : p.toFixed(1)) + 'M';

const FinishShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, fade: { value: 1 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time, fade; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time*37.1)*43758.5453); }
    void main(){ vec2 c = vUv-0.5; vec3 col = texture2D(tDiffuse, vUv).rgb;
      col *= 1.0 - 0.38*smoothstep(0.1, 0.7, dot(c*vec2(1.3,1.0), c*vec2(1.3,1.0))*2.2);
      col += (hash(vUv*vec2(1080.0,1920.0)) - 0.5)*0.014;
      gl_FragColor = vec4(col*fade, 1.0); }`,
};

export async function setup(THREE, renderer, W, H) {
  const R = await (await fetch('/marble/race.json')).json();
  const T = R.track, N = R.res.length, F = R.frames.length;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1020);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(38, W / H, 1, 400);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // lights
  scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x20182a, 0.55));
  const key = new THREE.DirectionalLight(0xfff2e0, 2.4);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -14, right: 14, top: 22, bottom: -22, near: 1, far: 80 });
  key.shadow.bias = -0.0004; key.shadow.radius = 4;
  scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0x7aa7ff, 0.9); rim.position.set(-10, 6, -6); scene.add(rim);

  // back board with a soft grid
  const gc = document.createElement('canvas'); gc.width = gc.height = 512; const gg = gc.getContext('2d');
  gg.fillStyle = '#141b2e'; gg.fillRect(0, 0, 512, 512);
  gg.strokeStyle = 'rgba(255,255,255,0.05)'; gg.lineWidth = 2;
  for (let i = 0; i <= 512; i += 64) { gg.beginPath(); gg.moveTo(i, 0); gg.lineTo(i, 512); gg.stroke(); gg.beginPath(); gg.moveTo(0, i); gg.lineTo(512, i); gg.stroke(); }
  const gridTex = new THREE.CanvasTexture(gc); gridTex.wrapS = gridTex.wrapT = THREE.RepeatWrapping;
  const boardH = -T.bottom + 30;
  gridTex.repeat.set(20 / 4, boardH / 4); gridTex.colorSpace = THREE.SRGBColorSpace;
  const board = new THREE.Mesh(new THREE.PlaneGeometry(20, boardH), new THREE.MeshStandardMaterial({ map: gridTex, roughness: 0.9, metalness: 0 }));
  board.position.set(0, -boardH / 2 + 15, -0.75); board.receiveShadow = true; scene.add(board);
  // far backdrop so the edges never show
  const back = new THREE.Mesh(new THREE.PlaneGeometry(200, 400), new THREE.MeshBasicMaterial({ color: 0x090d18 }));
  back.position.set(0, -50, -6); scene.add(back);

  // track pieces
  const railMat = new THREE.MeshPhysicalMaterial({ color: 0xc9d3e6, roughness: 0.38, clearcoat: 0.5, clearcoatRoughness: 0.25 });
  const sideMat = new THREE.MeshPhysicalMaterial({ color: 0x2a3552, roughness: 0.5, metalness: 0.2 });
  const seg = (a, b, th, depth, mat) => {
    const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
    const m = new THREE.Mesh(new RoundedBoxGeometry(L + th, th, depth, 3, th * 0.45), mat);
    m.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0); m.rotation.z = Math.atan2(dy, dx);
    m.castShadow = m.receiveShadow = true; scene.add(m); return m;
  };
  // walls are offset by half thickness so the visual surface matches the physics edge
  for (const w of T.walls) for (let i = 0; i < w.pts.length - 1; i++) {
    const a = w.pts[i], b = w.pts[i + 1], th = w.kind === 'side' ? 0.5 : 0.22;
    const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy); let nx = -dy / L, ny = dx / L;
    if (w.kind === 'side') { nx = a[0] < 0 ? -1 : 1; ny = 0; } else if (ny > 0) { nx = -nx; ny = -ny; } // push below the rolling surface
    const o = th / 2;
    seg([a[0] + nx * o, a[1] + ny * o], [b[0] + nx * o, b[1] + ny * o], th, 1.3, w.kind === 'side' ? sideMat : railMat);
  }
  const pegMat = new THREE.MeshPhysicalMaterial({ color: 0xffc04a, metalness: 1, roughness: 0.22 });
  for (const p of T.pegs) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(p.r, p.r, 1.3, 32), pegMat);
    m.rotation.x = Math.PI / 2; m.position.set(p.x, p.y, 0); m.castShadow = true; scene.add(m);
  }
  const spinMat = new THREE.MeshPhysicalMaterial({ color: 0xff5a3c, roughness: 0.35, clearcoat: 0.8 });
  const spinners = T.spinners.map(sp => {
    const g = new THREE.Group(); g.position.set(sp.x, sp.y, 0);
    const a = new THREE.Mesh(new RoundedBoxGeometry(sp.len, sp.w, 1.1, 3, 0.1), spinMat);
    const b = new THREE.Mesh(new RoundedBoxGeometry(sp.w, sp.len, 1.1, 3, 0.1), spinMat);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 1.3, 32), pegMat); hub.rotation.x = Math.PI / 2;
    for (const m of [a, b, hub]) { m.castShadow = true; g.add(m); }
    scene.add(g); return g;
  });
  // size-gate lips
  const L = T.lips, lipMat = new THREE.MeshPhysicalMaterial({ color: 0xff2d55, roughness: 0.3, clearcoat: 1, emissive: 0x400010 });
  const mkLip = s => { const g = new THREE.Group(); const m = seg([s * L.outer, L.y], [s * L.inner, L.y - 0.5], 0.24, 1.35, lipMat); scene.remove(m); g.add(m); scene.add(g); return g; };
  const lips = [mkLip(-1), mkLip(1)];
  // finish line: chequered strip on the board
  const fc = document.createElement('canvas'); fc.width = 64; fc.height = 512; const fg = fc.getContext('2d');
  for (let y = 0; y < 16; y++) for (let x = 0; x < 2; x++) { fg.fillStyle = (x + y) % 2 ? '#111' : '#fff'; fg.fillRect(x * 32, y * 32, 32, 32); }
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 4), new THREE.MeshStandardMaterial({ map: new THREE.CanvasTexture(fc), roughness: 0.6 }));
  fl.position.set(T.finishX, T.finishY + 1.6, -0.7); scene.add(fl);

  // marbles with flag textures
  const tl = new THREE.TextureLoader();
  const flags = {};
  const marbles = await Promise.all(R.res.map(r => new Promise(res => tl.load(`/marble/flags/${r.code}.png`, tex => {
    flags[r.code] = tex.image;
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
    tex.wrapS = THREE.RepeatWrapping; tex.repeat.set(2, 1); tex.offset.set(0.25, 0);
    const mat = new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 0.9 });
    const m = new THREE.Mesh(new THREE.SphereGeometry(r.r, 64, 32), mat);
    m.castShadow = true; scene.add(m); res(m);
  }))));

  // smoothed camera path: follow the leader, pulled toward the pack, low-pass filtered
  const camY = new Float32Array(F), camX = new Float32Array(F);
  for (let k = 0; k < F; k++) {
    const live = R.frames[k].map((p, i) => [p, i]).filter(([p, i]) => !(R.res[i].finish !== null && k / R.fps > R.res[i].finish + 0.5)).sort((a, b) => a[0][1] - b[0][1]);
    const lead = live.length ? live[0][0] : [T.finishX, T.finishY - 3], med = live.length ? live[Math.floor(live.length / 3)][0] : lead;
    camY[k] = Math.min(-5, lead[1] * 0.7 + med[1] * 0.3 + 3.5);
    camX[k] = clamp(lead[0] * 0.6 + med[0] * 0.4, -2.2, 2.2);
  }
  const smooth = (a, rad) => { const o = new Float32Array(F); for (let k = 0; k < F; k++) { let s = 0, w = 0; for (let j = -rad; j <= rad; j++) { const q = clamp(k + j, 0, F - 1), ww = Math.exp(-(j * j) / (2 * (rad / 2.2) ** 2)); s += a[q] * ww; w += ww; } o[k] = s / w; } return o; };
  const sm = smooth(camY, 50), smx = smooth(camX, 70);
  const pipCam = new THREE.PerspectiveCamera(30, 1, 1, 200);

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.22, 0.4, 0.92));
  composer.addPass(new OutputPass());
  const finish = new ShaderPass(FinishShader); composer.addPass(finish);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  return { THREE, scene, camera, composer, finish, R, T, marbles, spinners, lips, camY: sm, camX: smx, pipCam, key, flags, W, H, rows: {} };
}

const frameOf = (ctx, t) => clamp(Math.round((t - LEAD) * ctx.R.fps), 0, ctx.R.frames.length - 1);
export const DURATION = 51;

export function update(ctx, t) {
  const { R, camera, marbles, spinners, lips, key } = ctx;
  const k = frameOf(ctx, t), f = R.frames[k], sp = R.spin[k];
  f.forEach((p, i) => { marbles[i].position.set(p[0], p[1], 0); marbles[i].rotation.set(0, 0, p[2]); });
  spinners.forEach((g, i) => g.rotation.z = sp[i]);
  const open = sp[spinners.length] * (ctx.T.lips.openTo - ctx.T.lips.inner);
  lips[0].position.x = -open; lips[1].position.x = open;
  const cy = ctx.camY[k], cx = ctx.camX[k];
  const sway = Math.sin(t * 0.4) * 0.8;
  camera.position.set(cx + sway, cy + 1.6, 31); camera.lookAt(cx + sway * 0.4, cy, 0);
  key.position.set(8, cy + 14, 18); key.target.position.set(0, cy, 0);
  ctx.finish.uniforms.fade.value = clamp(t / 0.4) * clamp((DURATION - t) / 0.5);
  ctx.k = k;
}

// picture-in-picture replay of the size gate while the camera follows the leaders
const PIP = { x: 560, y: 1060, w: 480, h: 480 };
function pipAlpha(ctx, tt) { const T = ctx.T; return clamp((tt - (T.firstThrough - 1.2)) / 0.4) * (1 - clamp((tt - (T.lipT + 2.6)) / 0.4)); }
export function post(ctx, renderer, t) {
  const tt = ctx.k / ctx.R.fps, a = pipAlpha(ctx, tt);
  if (a <= 0.02) return;
  const { W, H, T, pipCam } = ctx, L = T.lips;
  const s = 0.7 + 0.3 * easeOut(a), w = PIP.w * s, h = PIP.h * s, x = PIP.x + (PIP.w - w) / 2, y = PIP.y + (PIP.h - h) / 2;
  pipCam.position.set(0.4, L.y + 1.6, 13); pipCam.lookAt(0, L.y + 0.4, 0);
  renderer.setScissorTest(true); renderer.setScissor(x, H - y - h, w, h); renderer.setViewport(x, H - y - h, w, h);
  renderer.render(ctx.scene, pipCam);
  renderer.setScissorTest(false); renderer.setViewport(0, 0, W, H);
}

// ---------- overlay ----------
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function flagDot(g, img, x, y, r) {
  g.save(); g.beginPath(); g.arc(x, y, r, 0, 7); g.clip();
  const s = (2 * r) / img.height; g.drawImage(img, x - img.width * s / 2, y - r, img.width * s, 2 * r); g.restore();
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, r, 0, 7); g.stroke();
}
function standings(ctx, k) {
  const { R } = ctx, tt = k / R.fps;
  return R.res.map((r, i) => ({ i, key: r.finish !== null && r.finish <= tt ? -1e6 + r.finish : R.frames[k][i][1] }))
    .sort((a, b) => a.key - b.key).map(o => o.i);
}

export function overlay(ctx, g, t) {
  const { W, H, R, T, camera, marbles, flags } = ctx, k = ctx.k, tt = k / R.fps;
  g.textBaseline = 'alphabetic';
  const tg = g.createLinearGradient(0, 0, 0, 640); tg.addColorStop(0, 'rgba(5,8,16,0.85)'); tg.addColorStop(1, 'rgba(5,8,16,0)');
  g.fillStyle = tg; g.fillRect(0, 0, W, 640);

  // name tags under/over marbles
  g.font = '26px Pret'; g.textAlign = 'center';
  const top3 = new Set(standings(ctx, k).slice(0, 3));
  const lastIdx = R.res.map((r, i) => [r.finish, i]).sort((a, b) => b[0] - a[0])[0][1];
  R.res.forEach((r, i) => {
    if (!(top3.has(i) || r.r > 0.55) || (r.finish !== null && r.finish < tt - 0.3 && i !== lastIdx)) return;
    const v = marbles[i].position.clone(); v.y += r.r + 0.35; const q = v.project(camera);
    const x = (q.x + 1) / 2 * W, y = (1 - q.y) / 2 * H;
    if (y < 380 || y > H - 40) return;
    const label = r.name.toUpperCase(), w = g.measureText(label).width + 20;
    g.globalAlpha = 0.9; g.fillStyle = 'rgba(8,10,18,0.72)'; rr(g, x - w / 2, y - 30, w, 34, 17); g.fill();
    g.fillStyle = '#fff'; g.fillText(label, x, y - 5); g.globalAlpha = 1;
  });

  // title
  const a0 = easeOut(clamp(t / 0.5)), sh = easeOut(clamp((t - 4) / 0.7));
  g.textAlign = 'center'; g.globalAlpha = a0;
  g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 20;
  g.font = '30px YTSans'; g.fillStyle = '#ffc04a'; g.letterSpacing = '7px'; g.fillText('MARBLE SIZE = POPULATION', W / 2, lerp(228, 200, sh)); g.letterSpacing = '0px';
  g.font = `${Math.round(lerp(82, 56, sh))}px YTSans`; g.fillStyle = '#fff'; g.fillText('Which country wins?', W / 2, lerp(320, 268, sh));
  g.shadowColor = 'transparent'; g.globalAlpha = 1;

  // countdown before the gate opens
  const gateT = LEAD + 1.6;
  if (t < gateT + 0.6) {
    const n = Math.ceil(gateT - t); const ph = (gateT - t) % 1;
    const txt = t < gateT ? String(Math.max(1, Math.min(3, n))) : 'GO!';
    const s = t < gateT ? 1 + 0.4 * (1 - easeOut(clamp(1 - ph))) : easeOutBack(clamp((t - gateT) / 0.3));
    g.save(); g.translate(W / 2, 760); g.scale(s, s); g.globalAlpha = t < gateT ? 1 : 1 - clamp((t - gateT - 0.3) / 0.3);
    g.font = '150px YTSans'; g.fillStyle = t < gateT ? '#fff' : '#3ddc84'; g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 30;
    g.fillText(txt, 0, 50); g.restore();
  }

  // live leaderboard (top 5) with smooth row moves
  const st = standings(ctx, k);
  const bx = 40, by = lerp(400, 320, easeOut(clamp((t - 4) / 0.7))), rowH = 64;
  g.fillStyle = 'rgba(8,10,18,0.7)'; rr(g, bx, by, 330, rowH * 5 + 24, 24); g.fill();
  for (let pos = 0; pos < st.length; pos++) {
    const i = st[pos], r = R.res[i];
    const row = ctx.rows[i] ?? (ctx.rows[i] = { y: pos });
    row.y = lerp(row.y, pos, 0.22);
    if (row.y > 4.6) continue;
    const y = by + 12 + row.y * rowH, a = clamp(4.9 - row.y);
    g.globalAlpha = a;
    g.font = '30px YTSans'; g.textAlign = 'left'; g.fillStyle = pos === 0 ? '#ffc04a' : 'rgba(255,255,255,0.7)';
    g.fillText(String(pos + 1), bx + 22, y + 42);
    flagDot(g, flags[r.code], bx + 82, y + 32, 20);
    g.font = '28px YTSans'; g.fillStyle = '#fff'; g.fillText(r.name, bx + 114, y + 33);
    g.font = '20px Pret'; g.fillStyle = 'rgba(255,255,255,0.55)'; g.fillText('pop. ' + POP(r.pop), bx + 114, y + 55);
    if (r.finish !== null && r.finish <= tt) { g.fillStyle = '#3ddc84'; g.font = '26px YTSans'; g.textAlign = 'right'; g.fillText('✓', bx + 312, y + 42); }
  }
  g.globalAlpha = 1;

  const pa = pipAlpha(ctx, tt);
  if (pa > 0.02) {
    const s = 0.7 + 0.3 * easeOut(pa), w = PIP.w * s, h = PIP.h * s, x = PIP.x + (PIP.w - w) / 2, y = PIP.y + (PIP.h - h) / 2;
    g.save(); g.globalAlpha = pa; g.strokeStyle = '#fff'; g.lineWidth = 6; rr(g, x, y, w, h, 18); g.stroke();
    g.fillStyle = '#ff2d55'; rr(g, x + 16, y + 16, 196, 44, 10); g.fill();
    g.fillStyle = '#fff'; g.font = '26px YTSans'; g.textAlign = 'left'; g.fillText('● SIZE GATE', x + 30, y + 47);
    g.restore();
  }
  // size gate callouts
  const ft = T.firstThrough, lt = T.lipT;
  if (tt > ft - 2.5 && tt < lt + 1.2) {
    const a = clamp((tt - (ft - 2.5)) / 0.4) * (1 - clamp((tt - lt - 0.8) / 0.4));
    banner(g, W, a, tt < lt ? 'THE SIZE GATE' : 'GATE OPEN!', tt < lt ? 'Too big? You wait.' : 'Big marbles released', tt < lt ? '#ff2d55' : '#3ddc84', PIP.x + PIP.w / 2);
  }
  // winner card
  const order = R.res.map((r, i) => [r.finish, i]).sort((a, b) => a[0] - b[0]);
  const win = order[0], last = order[order.length - 1];
  if (tt > win[0]) {
    const a = easeOutBack(clamp((tt - win[0]) / 0.6)), fade = 1 - clamp((tt - win[0] - 5.5) / 0.5);
    if (fade > 0) {
      const r = R.res[win[1]];
      g.save(); g.globalAlpha = fade; g.translate(W / 2, 1080); g.scale(a, a);
      g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 40; g.fillStyle = 'rgba(255,255,255,0.97)'; rr(g, -380, -170, 760, 340, 40); g.fill(); g.shadowColor = 'transparent';
      flagDot(g, flags[r.code], 0, -80, 62);
      g.textAlign = 'center'; g.fillStyle = '#111'; g.font = '72px YTSans'; g.fillText(r.name.toUpperCase() + ' WINS', 0, 60);
      g.font = '32px Pret'; g.fillStyle = '#666'; g.fillText('population ' + POP(r.pop), 0, 115);
      g.restore();
    }
  }
  if (tt > last[0] - 0.2) {
    const a = easeOut(clamp((tt - last[0] + 0.2) / 0.5)), r = R.res[last[1]];
    banner(g, W, a, `${r.name.toUpperCase()} FINISHED LAST`, `The biggest marble: ${POP(r.pop)} people`, '#ffc04a');
  }
}

function banner(g, W, a, big, small, color, cx = W / 2) {
  g.save(); g.globalAlpha = a; g.translate(0, (1 - a) * 30);
  g.textAlign = 'center'; g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 22;
  g.font = '64px YTSans'; g.fillStyle = color; g.fillText(big, cx, 1625);
  g.font = '40px YTSans'; g.fillStyle = '#fff'; g.fillText(small, cx, 1685);
  g.restore();
}
