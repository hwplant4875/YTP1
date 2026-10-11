// France 2026 lycée protests: 3D relief map of metropolitan France + Corsica.
// Data baked by episodes/02_france_protests/prep_map.py (AWS terrain tiles, Natural Earth, IGN regions/départements,
// data.education.gouv.fr lycée directory). 1 unit = 10 km. North = -z.
// shots (?shot=name or name:seconds to stretch the timeline):
//   spark       (8 s)  close and low over Créteil, SE of Paris. At 1.2 s one amber point ignites and keeps pulsing.
//   spread      (6 s)  18 Sept -> 1 Oct. Créteil, then the 93/94 suburbs (24-25 Sept), then Marseille, Lille, Lyon,
//                      Riviera (28 Sept), then the 1 Oct flood to 1,027 lycées. Lit lycée count follows the Interior
//                      Ministry series; which lycées light is modelled (nearest dated city). City columns = number of
//                      lit lycées within 30 km. Arcs leave Créteil. Camera pulls from Île-de-France out to all France.
//                      Day-by-day timing is exported to episodes/02_france_protests/map/spread_timeline.json.
//   oct6        (6 s)  6 Oct police counts as glowing columns (linear in marchers; Paris 56,000 tallest).
//   red_orange  (6 s)  114 red + 400 orange lycées (illustrative distribution, weighted by SNES-FSU shortage academies).
//   creteil_hold        same framing as the end of spark, without the ignite (for the outro "pull back in").
import { AMBER } from './lib.js';
import { makeComposer, glow } from './look.js';
import { AMBER_HI, CREAM, shotArgs, path, clamp01, sstep, fontsReady, label } from './france_lib.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';

const BASE = '/episodes/02_france_protests/map/';
const RED = 0xff4a36;

export async function setup(THREE, renderer, W, H) {
  const { name: shot, len } = shotArgs('spread');
  await fontsReady();
  const [places, lines, hbuf, colorTex] = await Promise.all([
    fetch(BASE + 'places.json').then(r => r.json()), fetch(BASE + 'lines.json').then(r => r.json()),
    fetch(BASE + 'height.bin').then(r => r.arrayBuffer()), new THREE.TextureLoader().loadAsync(BASE + 'color.jpg')]);
  colorTex.colorSpace = THREE.SRGBColorSpace; colorTex.anisotropy = 8;
  const heights = new Float32Array(hbuf);
  const [GW, GH] = places.grid, [X0, Z0, WU, HU] = places.extent;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060708);
  scene.fog = new THREE.FogExp2(0x060708, shot === 'spark' || shot === 'creteil_hold' ? 0.01 : 0.0022);
  const camera = new THREE.PerspectiveCamera(shot === 'spark' || shot === 'creteil_hold' ? 32 : 28, W / H, 0.05, 2000);

  // ---------------------------------------------------------------- terrain
  const geo = new THREE.PlaneGeometry(WU, HU, GW - 1, GH - 1);
  geo.rotateX(-Math.PI / 2);
  geo.translate(X0 + WU / 2, 0, Z0 + HU / 2);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) pos.setY(i, heights[i]);
  geo.computeVertexNormals();
  const terrainMat = new THREE.MeshStandardMaterial({ map: colorTex, roughness: 0.93, metalness: 0.0 });
  const terrain = new THREE.Mesh(geo, terrainMat); terrain.receiveShadow = true; scene.add(terrain);
  const under = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshBasicMaterial({ color: 0x08090b }));
  under.rotation.x = -Math.PI / 2; under.position.y = -0.08; scene.add(under);
  const hAt = (x, z) => {
    const u = (x - X0) / WU * (GW - 1), v = (z - Z0) / HU * (GH - 1);
    const i = Math.max(0, Math.min(GW - 2, Math.floor(u))), j = Math.max(0, Math.min(GH - 2, Math.floor(v))), fu = u - i, fv = v - j;
    const at = (a, b) => heights[b * GW + a];
    return at(i, j) * (1 - fu) * (1 - fv) + at(i + 1, j) * fu * (1 - fv) + at(i, j + 1) * (1 - fu) * fv + at(i + 1, j + 1) * fu * fv;
  };

  // lights: a low warm key from the north-west (agrees with the baked hillshade), cold faint fill
  const key = new THREE.DirectionalLight(0xfff0dc, 2.3); key.position.set(-60, 45, -50); scene.add(key);
  const fill = new THREE.DirectionalLight(0x7d8ba0, 0.35); fill.position.set(60, 30, 60); scene.add(fill);
  scene.add(new THREE.HemisphereLight(0x8a919c, 0x0a0908, 0.35));

  // ---------------------------------------------------------------- draped lines
  const lineMats = [];
  const addLines = (arr, color, width, opacity, lift = 0) => {
    const mat = new LineMaterial({ color, linewidth: width, transparent: true, opacity, depthWrite: false, worldUnits: false, fog: true });
    mat.resolution.set(W, H); lineMats.push(mat);
    const grp = new THREE.Group();
    for (const p of arr) {
      if (p.length < 6) continue;
      const g = new LineGeometry(); g.setPositions(lift ? p.map((v, i) => i % 3 === 1 ? v + lift : v) : p);
      const l = new Line2(g, mat); l.computeLineDistances(); l.renderOrder = 2; grp.add(l);
    }
    scene.add(grp); return mat;
  };
  const close = shot === 'spark' || shot === 'creteil_hold';
  const mCoast = addLines(lines.coast, 0xe9dcc2, close ? 2.2 : 1.5, 0.75);
  const mBorder = addLines(lines.border, 0xe9dcc2, close ? 1.6 : 1.1, 0.42);
  const mRegions = addLines(lines.regions, 0xe9dcc2, close ? 1.2 : 1.0, close ? 0.2 : 0.2);
  const mDepts = addLines(lines.depts, 0xe9dcc2, 1.0, close ? 0.16 : 0.0);
  const mNb = addLines(lines.neighbours, 0xbdb6a8, 1.0, 0.12);
  const mRiv = addLines(lines.rivers, 0x8f9aa6, close ? 1.3 : 1.0, close ? 0.22 : 0.16);

  // ---------------------------------------------------------------- lycée points (one Points object, shader-driven)
  // day at which the national series reaches n lycées (inverse of the piecewise-linear ministry series)
  const S = places.series;
  const dayOfRank = (r) => {
    for (let i = 0; i < S.length - 1; i++) if (r + 1 <= S[i + 1][1]) {
      const [d0, n0] = S[i], [d1, n1] = S[i + 1];
      return d0 + (d1 - d0) * Math.max(0, (r + 1 - n0)) / (n1 - n0);
    }
    return S[S.length - 1][0];
  };
  const nAt = (day) => {
    for (let i = 0; i < S.length - 1; i++) if (day <= S[i + 1][0]) { const [d0, n0] = S[i], [d1, n1] = S[i + 1]; return n0 + (n1 - n0) * Math.max(0, day - d0) / (d1 - d0); }
    return S[S.length - 1][1];
  };
  const LY = places.lycees, ALL = places.all_lycees;
  // base layer: every lycée as a faint cream speck (reads like town lights), then the flagged ones on top
  const mkPoints = (list, attrs, frag, uniforms, size) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(list.flatMap(q => [q[0], q[1] + 0.06, q[2]]), 3));
    for (const [k, fn] of Object.entries(attrs)) g.setAttribute(k, new THREE.Float32BufferAttribute(list.map(fn), 1));
    const m = new THREE.ShaderMaterial({
      uniforms: { uScale: { value: H / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))) }, uSize: { value: size }, uMaxPx: { value: 40 }, uNormal: { value: 0 }, uCore: { value: 0.26 }, ...uniforms },
      vertexShader: `uniform float uScale, uSize, uMaxPx; ${Object.keys(attrs).map(k => `attribute float ${k};`).join('')}
        ${frag.vdecl || ''} varying float vA; varying vec3 vC;
        void main(){ vec4 mv = modelViewMatrix * vec4(position,1.0); ${frag.vmain}
          gl_PointSize = clamp(sz * uSize * uScale / -mv.z, 1.5, uMaxPx); gl_Position = projectionMatrix * mv; }`,
      fragmentShader: `uniform float uNormal, uCore; varying float vA; varying vec3 vC; void main(){ vec2 c = gl_PointCoord - 0.5; float d = length(c)*2.0;
          float core = 1.0 - smoothstep(uCore, uCore + 0.12, d); float halo = pow(max(0.0, 1.0 - d), 2.0) * 0.3; float a = core * 0.9 + halo; if (a*vA < 0.003) discard; gl_FragColor = uNormal > 0.5 ? vec4(vC * (0.6 + 0.4 * core), clamp(a * vA, 0.0, 1.0)) : vec4(vC * a * vA, 1.0); }`,
      transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
    });
    const p = new THREE.Points(g, m); p.renderOrder = 5; p.frustumCulled = false; scene.add(p); return m;
  };
  const baseMat = mkPoints(ALL, {}, { vdecl: 'uniform float uBase;', vmain: `float sz = 1.0; vA = uBase; vC = vec3(0.93,0.88,0.78);` }, { uBase: { value: 0.0 } }, 0.16); baseMat.uniforms.uMaxPx.value = 3.5;
  const seedOf = (i) => ((Math.sin(i * 91.7 + 3.1) * 43758.5453) % 1 + 1) % 1;
  const lyMat = mkPoints(LY.map((q, i) => [...q, i]), {
    aDay: q => q[3] >= 0 ? dayOfRank(q[3]) : 999., aRO: q => q[4], aSeed: q => seedOf(q[5]),
  }, {
    vdecl: 'uniform float uDay, uMode, uRO, uTime;',
    vmain: `float sz = 0.0; vA = 0.0; vC = vec3(1.0);
      if (uMode < 1.5) {                       // spread
        float age = uDay - aDay;
        float on = step(0.0, age);
        float flash = on * exp(-max(age, 0.0) * 5.0);
        sz = on * (1.0 + 2.2 * flash); vA = on * (0.85 + 1.6 * flash) * uMode;
        vC = mix(vec3(1.0, 0.62, 0.25), vec3(1.0, 0.9, 0.7), flash);
      } else {                                 // red / orange
        float r = step(1.5, aRO), o = step(0.5, aRO) * (1.0 - r);
        float t0 = (r > 0.5 ? 0.0 : 0.35) + aSeed * 0.55;
        float on = smoothstep(t0, t0 + 0.08, uRO);
        float flash = on * (1.0 - smoothstep(t0 + 0.02, t0 + 0.25, uRO));
        sz = on * (r > 0.5 ? 2.0 : 1.25) * (1.0 + flash * 1.2); vA = on * (1.0 + flash) * step(0.5, aRO);
        vC = r > 0.5 ? vec3(0.92, 0.09, 0.05) : vec3(1.0, 0.36, 0.04);
      }`,
  }, { uDay: { value: 0 }, uMode: { value: 0 }, uRO: { value: 0 }, uTime: { value: 0 } }, 0.5);

  if (shot === 'red_orange') { lyMat.blending = THREE.NormalBlending; lyMat.uniforms.uNormal.value = 1; lyMat.uniforms.uSize.value = 0.78; lyMat.uniforms.uCore.value = 0.42; }
  // ---------------------------------------------------------------- cities
  const C = places.cities;
  const cityByName = Object.fromEntries(C.map(c => [c.name, c]));
  const near = C.map(c => LY.filter(q => q[3] >= 0 && Math.hypot(q[0] - c.x, q[2] - c.z) < 3.0).map(q => dayOfRank(q[3])).sort((a, b) => a - b));
  const columnMat = (color, op) => new THREE.ShaderMaterial({
    uniforms: { color: { value: new THREE.Color(color) }, op: { value: op } },
    vertexShader: `varying float vY; varying vec3 vN; varying vec3 vV; void main(){ vY = uv.y; vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform vec3 color; uniform float op; varying float vY; varying vec3 vN; varying vec3 vV;
      void main(){ float edge = pow(1.0 - abs(dot(vN, vV)), 1.5); float core = pow(abs(dot(vN, vV)), 6.0);
        float fade = pow(1.0 - vY, 1.4) * smoothstep(0.0, 0.02, vY);
        gl_FragColor = vec4(color * (0.35 + 0.9*core + 0.5*edge) * op * fade, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  });
  const ringTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    const grd = g.createRadialGradient(128, 128, 90, 128, 128, 126);
    grd.addColorStop(0, 'rgba(255,255,255,0)'); grd.addColorStop(0.75, 'rgba(255,255,255,1)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c);
  })();
  const mkRing = (color) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: ringTex, color, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false, opacity: 0, fog: false }));
    m.rotation.x = -Math.PI / 2; m.renderOrder = 6; return m;
  };
  const cityObjs = C.map((c) => {
    const g = new THREE.Group(); g.position.set(c.x, c.y + 0.03, c.z); scene.add(g);
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 1, 28, 1, true).translate(0, 0.5, 0), columnMat(AMBER_HI, 1.0));
    col.scale.set(1, 0.001, 1); col.renderOrder = 7; g.add(col);
    const coreM = new THREE.MeshBasicMaterial({ color: 0xffd8a0, transparent: true, opacity: 0, fog: false, blending: THREE.AdditiveBlending, depthWrite: false });
    const core = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1, 10, 1, true).translate(0, 0.5, 0), coreM); core.scale.set(1, 0.001, 1); g.add(core);
    const halo = glow(THREE, AMBER, 1, 1); halo.material.opacity = 0; halo.renderOrder = 8; halo.position.y = 0.08; g.add(halo);
    const top = glow(THREE, 0xffd9a8, 1, 1); top.material.opacity = 0; top.renderOrder = 8; g.add(top);
    const rings = [mkRing(AMBER_HI), mkRing(AMBER_HI)]; rings.forEach(r => { r.position.y = 0.04; g.add(r); });
    return { c, g, col, core, halo, top, rings, lab: null };
  });
  const addLabel = (name, opts = {}, dy = 0.0) => {
    const o = cityObjs.find(o => o.c.name === name); if (!o) return null;
    const l = label(THREE, opts.text ?? name, opts); l.position.set(0, 0.25 + dy, 0); o.g.add(l); o.lab = l; return l;
  };

  // ---------------------------------------------------------------- arcs from Créteil
  const cre = cityByName['Créteil'];
  const arcTargets = C.filter(c => c.day >= 6 && Math.hypot(c.x - cre.x, c.z - cre.z) > 2.5 && c.label);
  const arcs = arcTargets.map((c) => {
    const a = new THREE.Vector3(cre.x, cre.y + 0.1, cre.z), b = new THREE.Vector3(c.x, c.y + 0.1, c.z);
    const d = a.distanceTo(b), mid = a.clone().lerp(b, 0.5); mid.y += d * 0.22;
    const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
    const m = new THREE.ShaderMaterial({
      uniforms: { prog: { value: 0 }, fadeAll: { value: 0 }, color: { value: new THREE.Color(AMBER_HI) } },
      vertexShader: `varying float vU; void main(){ vU = uv.x; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
      fragmentShader: `uniform float prog, fadeAll; uniform vec3 color; varying float vU;
        void main(){ if (vU > prog) discard; float head = exp(-(prog - vU) * 14.0); float a = (0.10 + 1.2*head) * fadeAll;
          gl_FragColor = vec4(color * a + vec3(1.0,0.9,0.75)*head*0.5*fadeAll, 1.0); }`,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 96, 0.045, 6, false), m); tube.renderOrder = 4; scene.add(tube);
    return { c, m, tube };
  });

  // ---------------------------------------------------------------- Créteil spark (hero point)
  const spark = new THREE.Group(); spark.position.set(cre.x, cre.y + 0.05, cre.z); scene.add(spark);
  const sparkCore = glow(THREE, 0xffe2b8, 1, 1); sparkCore.renderOrder = 9; spark.add(sparkCore);
  const sparkHalo = glow(THREE, AMBER, 1, 1); sparkHalo.renderOrder = 9; spark.add(sparkHalo);
  const sparkRings = [0, 1, 2].map(() => { const r = mkRing(AMBER_HI); spark.add(r); return r; });
  const sparkLight = new THREE.PointLight(AMBER, 0, 8, 1.6); sparkLight.position.set(0, 0.6, 0); spark.add(sparkLight);
  const beacon = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1, 12, 1, true).translate(0, 0.5, 0), columnMat(0xffc27a, 1.0));
  beacon.renderOrder = 7; beacon.scale.y = 0.001; spark.add(beacon);

  // ---------------------------------------------------------------- per-shot labels
  if (shot === 'spark' || shot === 'creteil_hold') {
    addLabel('Paris', { size: 0.024, color: '#d9d0bd' });
    const l = addLabel('Créteil', { size: 0.03, gap: 70 }); if (l) l.material.opacity = 0;
  } else if (shot === 'spread') {
    for (const n of ['Paris', 'Marseille', 'Lyon', 'Lille', 'Toulouse', 'Bordeaux', 'Nantes', 'Rennes', 'Strasbourg', 'Nice']) {
      const l = addLabel(n, { size: 0.021, color: '#e6dcc6' }); l.material.opacity = 0;
    }
    const l = addLabel('Créteil', { size: 0.023, anchor: 'right' }); l.material.opacity = 0;
  } else if (shot === 'oct6') {
    const fmt = (n) => n.toLocaleString('en-US');
    for (const o of cityObjs) if (o.c.police6oct && o.c.police6oct >= 3000) {
      const l = label(THREE, o.c.name, { size: o.c.police6oct > 10000 ? 0.03 : 0.024, sub: fmt(o.c.police6oct), anchor: o.c.name === 'Aix-en-Provence' ? 'right' : 'left' });
      l.material.opacity = 0; o.g.add(l); o.lab = l;
    }
  } else if (shot === 'red_orange') {
    for (const n of ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nantes', 'Lille']) { const l = addLabel(n, { size: 0.019, color: '#cfc6b3', gap: n === 'Paris' ? 90 : 34 }); }
  }

  // ---------------------------------------------------------------- cameras
  const cx = cre.x, cz = cre.z, cy = cre.y;
  const cams = {
    spark: path([[0, [cx + 4.5, cy + 11, cz + 17, cx, cy, cz - 0.6]], [8, [cx + 1.6, cy + 3.6, cz + 6.2, cx, cy, cz - 0.2]]]),
    creteil_hold: path([[0, [cx + 1.8, cy + 3.9, cz + 6.6, cx, cy, cz - 0.2]], [8, [cx + 1.5, cy + 3.5, cz + 6.0, cx, cy, cz - 0.2]]]),
    spread: path([[0, [cx + 6, cy + 16, cz + 24, cx - 0.5, cy, cz]], [1.0, [cx + 6, cy + 18, cz + 27, cx - 0.5, cy, cz]],
      [3.1, [-8, 150, 120, -7, 0, 4]], [6, [-6, 145, 115, -7.5, 0, 4]]]),
    oct6: path([[0, [-30, 66, 132, -9, 5, -4]], [6, [-24, 62, 124, -9, 5, -5]]]),
    red_orange: path([[0, [-8, 180, 80, -6, 0, -1]], [6, [-7, 174, 76, -6, 0, -1]]]),
  };
  const camF = cams[shot] ?? cams.spread;
  const tl = len ? len / 6 : 1;              // timeline stretch
  const dof = close ? { focus: 7, aperture: 0.0012, maxblur: 0.005 } : null;
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.85, bloomRadius: 0.6, bloomThreshold: 0.55, exposure: 1.0, dof });
  post.finish.uniforms.vignette.value = 0.6;
  // labels render after bloom/DOF on their own layer so the type stays crisp
  const labelCam = camera.clone(); labelCam.layers.set(1);
  scene.traverse(o => { if (o.isSprite && o.material.sizeAttenuation === false) o.layers.set(1); });
  const lp = new RenderPass(scene, labelCam); lp.clear = false; lp.clearDepth = true;
  const lpRender = lp.render.bind(lp);
  lp.render = (...args) => { const bg = scene.background; scene.background = null; lpRender(...args); scene.background = bg; };
  post.composer.insertPass(lp, post.composer.passes.length - 2);
  return { THREE, scene, camera, labelCam, shot, tl, camF, cityObjs, arcs, lyMat, baseMat, nAt, near, spark, sparkCore, sparkHalo, sparkRings, sparkLight,
    lineMats: { mCoast, mDepts }, beacon, ...post };
}

// spread: seconds (6 s base) -> day since 18 Sept
const SPREAD_KEYS = [[0, 0], [1.0, 0], [2.0, 7], [2.9, 10], [3.5, 12], [4.6, 13.15]];
export function spreadDay(ts) {
  const K = SPREAD_KEYS; if (ts <= K[0][0]) return 0;
  for (let i = 0; i < K.length - 1; i++) if (ts <= K[i + 1][0]) { const s = (ts - K[i][0]) / (K[i + 1][0] - K[i][0]); return K[i][1] + (K[i + 1][1] - K[i][1]) * s; }
  return K[K.length - 1][1];
}

function pulseRing(r, phase, maxS, op) {
  const p = ((phase % 1) + 1) % 1;
  r.scale.setScalar(0.2 + p * maxS); r.material.opacity = op * (1 - p) * (1 - p);
}

export function update(ctx, t) {
  const { THREE, camera, shot, tl, camF, cityObjs, arcs, lyMat, baseMat, spark, sparkCore, sparkHalo, sparkRings, sparkLight } = ctx;
  const ts = t / tl;                     // timeline seconds on the 6 s base
  const c = camF(ts);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]);
  ctx.labelCam.position.copy(camera.position); ctx.labelCam.quaternion.copy(camera.quaternion);
  const camDist = camera.position.distanceTo(spark.position);

  // ---------------- Créteil spark
  let sparkOn = 0;
  if (shot === 'spark') sparkOn = sstep(1.2, 1.5, t);
  else if (shot === 'creteil_hold') sparkOn = 1;
  else if (shot === 'spread') sparkOn = 1;
  const flare = shot === 'spark' ? Math.exp(-Math.max(0, t - 1.25) * 2.2) * sparkOn : 0;
  const beat = 0.85 + 0.15 * Math.sin(t * 4.2);
  const k = camDist * 0.06;              // keep the spark a similar size on screen
  sparkCore.scale.setScalar(k * (0.35 + 0.9 * flare) * sparkOn); sparkCore.material.opacity = sparkOn;
  sparkHalo.scale.setScalar(k * (1.6 + 3 * flare) * beat * sparkOn); sparkHalo.material.opacity = 0.75 * sparkOn;
  sparkLight.intensity = sparkOn * (6 + 25 * flare) * beat;
  sparkLight.distance = Math.max(8, camDist * 0.9);
  ctx.beacon.scale.set(k * 1.2, (shot === 'spark' || shot === 'creteil_hold') ? sparkOn * (0.4 + 1.0 * sstep(1.2, 2.6, shot === 'spark' ? t : 9)) : 0.001, k * 1.2);
  sparkRings.forEach((r, i) => pulseRing(r, (t - 1.2) / 2.4 + i / 3, Math.min(k * 6, 7), 0.32 * sparkOn * (shot === 'spread' ? 1 - 0.7 * clamp01((ts - 1) / 2) : 1)));
  if (shot === 'spark' || shot === 'creteil_hold') {
    const lab = cityObjs.find(o => o.c.name === 'Créteil').lab; if (lab) lab.material.opacity = shot === 'spark' ? sstep(2.0, 2.8, t) : 1;
  }

  // ---------------- per shot
  for (const o of cityObjs) { o.col.scale.y = 0.001; o.core.material.opacity = 0; o.halo.material.opacity = 0; o.top.material.opacity = 0; o.rings.forEach(r => r.material.opacity = 0); }
  arcs.forEach(a => { a.m.uniforms.fadeAll.value = 0; });
  lyMat.uniforms.uMode.value = 0;
  baseMat.uniforms.uBase.value = shot === 'red_orange' ? 0.07 : shot === 'oct6' ? 0.08 : (shot === 'spark' || shot === 'creteil_hold') ? 0.5 : 0.12;

  if (shot === 'spread') {
    const day = spreadDay(ts);
    lyMat.uniforms.uMode.value = 1; lyMat.uniforms.uDay.value = day;
    const wide = clamp01((ts - 1.0) / 2.1);
    cityObjs.forEach((o, i) => {
      const cc = o.c; if (cc.name === 'Créteil') return;
      const age = day - cc.day; if (age < 0) return;
      const lit = ctx.near[i].filter(d => d <= day).length;
      const hgt = (0.25 + Math.sqrt(lit) * 0.42) * (0.4 + 0.6 * wide) * sstep(0, 0.6, age);
      const big = cc.label || cc.w >= 0.5;
      o.col.scale.y = big ? hgt : 0.001; o.core.material.opacity = big ? 0.6 * sstep(0, 0.5, age) : 0; o.core.scale.y = o.col.scale.y * 0.85;
      o.halo.scale.setScalar((big ? 3.2 : 1.8) * (0.5 + 0.5 * wide)); o.halo.material.opacity = 0.55 * sstep(0, 0.4, age);
      o.top.position.y = hgt; o.top.scale.setScalar(1.6 * (0.5 + 0.5 * wide)); o.top.material.opacity = big ? 0.5 * sstep(0, 0.6, age) : 0;
      pulseRing(o.rings[0], clamp01(age / 0.6), 6 * (0.5 + 0.5 * wide), age < 0.6 ? 0.8 : 0);
      if (o.lab) { o.lab.material.opacity = sstep(0.1, 0.8, age) * sstep(2.0, 2.8, ts); o.lab.position.y = hgt + 0.5; }
    });
    const creo = cityObjs.find(o => o.c.name === 'Créteil'); if (creo.lab) { creo.lab.material.opacity = 1 - sstep(1.5, 2.5, ts); creo.lab.position.y = 0.6; }
    arcs.forEach(a => { const p = clamp01((day - (a.c.day - 1.0)) / 1.0); a.m.uniforms.prog.value = p; a.m.uniforms.fadeAll.value = p > 0 ? (0.25 + 0.75 * (1 - sstep(0.3, 2.0, day - a.c.day))) : 0; });
  } else if (shot === 'oct6') {
    const max = 56000;
    cityObjs.forEach((o, i) => {
      const n = o.c.police6oct; if (!n) return;
      const grow = sstep(0.3 + i * 0.02, 2.2 + i * 0.02, t);
      const hgt = 19 * (n / max) * grow + 0.05;
      o.col.scale.set(n > 10000 ? 1.6 : 1.2, hgt, n > 10000 ? 1.6 : 1.2); o.core.material.opacity = 0.9; o.core.scale.set(1.4, hgt, 1.4);
      o.halo.scale.setScalar(4.5); o.halo.material.opacity = 0.7;
      o.top.position.y = hgt; o.top.scale.setScalar(n > 10000 ? 3.6 : 2.4); o.top.material.opacity = 0.9 * grow;
      if (o.lab) { o.lab.position.y = hgt + 0.9; o.lab.material.opacity = sstep(1.4, 2.4, t); }
    });
  } else if (shot === 'red_orange') {
    lyMat.uniforms.uMode.value = 2; lyMat.uniforms.uRO.value = clamp01(t / 4.2);
  }
  lyMat.uniforms.uTime.value = t;
}
