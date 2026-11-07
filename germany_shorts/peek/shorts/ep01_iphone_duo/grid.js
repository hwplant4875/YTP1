// "A small number": a field of identical open phones lying on the floor (Isotype style),
// only a few of them cracked in the same spot.
import * as THREE from 'three';
import { PHONE, MAT, roundedRectShape, makeWallpaper, buildCrack, paintScreen, crackGlowTexture, SCW, SCH } from './phone.js';

export function buildGrid(floorY, { cols = 9, rows = 15, cracked = [[0, 0], [-1, -3], [1, 3]] } = {}) {
  const { W, H, T, R, BS, BT, SW, SH } = PHONE;
  const root = new THREE.Group();
  const gx = W + 1.3, gz = H + 1.3;

  const shape = roundedRectShape(W - 2 * BS, H - 2 * BS, R - BS, R - BS, R - BS, R - BS);
  const bodyGeo = new THREE.ExtrudeGeometry(shape, { depth: T - 2 * BT, bevelEnabled: true, bevelThickness: BT, bevelSize: BS, bevelSegments: 4, curveSegments: 24 });
  bodyGeo.translate(0, 0, -(T - 2 * BT) / 2);
  const screenGeo = new THREE.PlaneGeometry(SW, SH);

  const wall = makeWallpaper();
  const crack = buildCrack();
  const rr = PHONE.SR / PHONE.SW * SCW;
  const mk = () => { const c = document.createElement('canvas'); c.width = SCW; c.height = SCH; return c; };
  const normal = mk(), broken = mk(), glow = mk();
  { const g = normal.getContext('2d'); g.drawImage(wall, 0, 0); g.globalCompositeOperation = 'destination-in'; g.beginPath(); g.roundRect(0, 0, SCW, SCH, rr); g.fill(); }
  paintScreen(broken.getContext('2d'), wall, crack, 1, 1);
  crackGlowTexture(glow.getContext('2d'), crack, 1, 1, 0.3);
  const tex = c => { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const tNormal = tex(normal), tBroken = tex(broken), tGlow = tex(glow);

  const glass = MAT.glass(), ti = MAT.titanium();
  const screenMat = new THREE.MeshPhysicalMaterial({ color: 0x000000, map: tNormal, alphaTest: 0.5, emissive: 0xffffff, emissiveMap: tNormal, emissiveIntensity: 0.55, roughness: 0.32, envMapIntensity: 0.05, specularIntensity: 0.15 });
  const brokenMat = new THREE.MeshStandardMaterial({ color: 0x000000, map: tBroken, alphaTest: 0.5, emissive: 0xffffff, emissiveMap: tBroken, emissiveIntensity: 1.2, roughness: 0.32, envMapIntensity: 0.05 });
  const glowMat = new THREE.MeshBasicMaterial({ map: tGlow, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, color: new THREE.Color(4.5, 4.5, 4.5), polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });

  // a soft red warning glow on the floor around each broken phone (blooms when pulled back)
  const haloTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d');
    const rg = g.createRadialGradient(128, 128, 30, 128, 128, 128);
    rg.addColorStop(0, 'rgba(255,70,45,1)'); rg.addColorStop(0.35, 'rgba(255,50,35,0.45)'); rg.addColorStop(0.7, 'rgba(255,40,30,0.12)'); rg.addColorStop(1, 'rgba(255,30,20,0)');
    g.fillStyle = rg; g.fillRect(0, 0, 256, 256);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const haloGeo = new THREE.PlaneGeometry(W * 2.3, W * 2.3);
  const haloMat = new THREE.MeshBasicMaterial({ map: haloTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, color: new THREE.Color(0, 0, 0) });
  const isCracked = (c, r) => cracked.some(([a, b]) => a === c && b === r);
  const n = cols * rows;
  const bodies = new THREE.InstancedMesh(bodyGeo, [glass, ti], n);
  bodies.castShadow = true; bodies.receiveShadow = true;
  const screens = new THREE.InstancedMesh(screenGeo, screenMat, n - cracked.length);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0)), one = new THREE.Vector3(1, 1, 1);
  const glows = [];
  let i = 0, j = 0;
  const c0 = Math.floor(cols / 2), r0 = Math.floor(rows / 2);
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const cc = c - c0, rw = r - r0;
    const p = new THREE.Vector3(cc * gx, floorY + T / 2 + 0.002, rw * gz);
    m.compose(p, q, one); bodies.setMatrixAt(i++, m);
    const ps = p.clone(); ps.y += T / 2 + 0.004;
    if (isCracked(cc, rw)) {
      const s = new THREE.Mesh(screenGeo, brokenMat); s.position.copy(ps); s.quaternion.copy(q);
      const gl = new THREE.Mesh(screenGeo, glowMat); gl.position.copy(ps); gl.quaternion.copy(q);
      const halo = new THREE.Mesh(haloGeo, haloMat); halo.position.set(p.x, floorY + 0.01, p.z); halo.rotation.x = -Math.PI / 2;
      root.add(s, gl, halo); glows.push(gl, halo);
    } else { m.compose(ps, q, one); screens.setMatrixAt(j++, m); }
  }
  root.add(bodies, screens);

  // dark floor with a wide soft pool of light
  const ft = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 1024;
    const g = c.getContext('2d');
    const rg = g.createRadialGradient(512, 512, 0, 512, 512, 512);
    rg.addColorStop(0, '#15161b'); rg.addColorStop(0.55, '#0a0b0e'); rg.addColorStop(1, '#030304');
    g.fillStyle = rg; g.fillRect(0, 0, 1024, 1024);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(260, 260), new THREE.MeshStandardMaterial({ map: ft, roughness: 0.9, envMapIntensity: 0.1 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = floorY; floor.receiveShadow = true;
  root.add(floor);

  return { root, glows, glowMat, screenMat, haloMat, gx, gz };
}
