// ORBIS banner (2560x1440, no text): the world map as a stone slab, with cave-like underground floors
// stacked beneath it, cut open at the front: tunnels, chambers and shafts lit by lamps.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const MW = 36, LAT0 = 82, LAT1 = -45;            // slab width (units) and latitude span shown
const MD = MW * (LAT0 - LAT1) / 360;              // slab depth keeps the map's proportions
const LON0 = -180;
const CRUST = 0.4, GAP = 0.3, LAYERS = [0.85, 0.95, 1.05], STEP = 0.7;   // upper floors sit further back: terraces of a dig

let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

async function mapTexture(THREE) {
  // rastered offline by branding/world_map_texture.py (large 2D-canvas paths lose the WebGL context here)
  const t = await new THREE.TextureLoader().loadAsync('/scenes/data/world_map.png');
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}

// front cut face of one underground floor: rock strata with tunnels, chambers and lamps
function caveFace(THREE, h, tone, depthIdx) {
  const W = 4096, H = Math.round(W * h / MW * 2);
  const col = document.createElement('canvas'); col.width = W; col.height = H;
  const emi = document.createElement('canvas'); emi.width = W; emi.height = H;
  const g = col.getContext('2d'), e = emi.getContext('2d');
  e.fillStyle = '#000'; e.fillRect(0, 0, W, H);
  const rg = g.createLinearGradient(0, 0, 0, H); rg.addColorStop(0, tone[0]); rg.addColorStop(1, tone[1]);
  g.fillStyle = rg; g.fillRect(0, 0, W, H);
  // thin sediment bands and grit
  for (let i = 0; i < 9; i++) {
    const y = rnd() * H; g.strokeStyle = `rgba(0,0,0,${0.12 + rnd() * 0.12})`; g.lineWidth = 2 + rnd() * 5;
    g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= W; x += 100) g.lineTo(x, y + Math.sin(x / (150 + i * 45) + i) * 6); g.stroke();
  }
  for (let i = 0; i < 20000; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '0,0,0' : '255,240,220'},${0.05 + rnd() * 0.07})`; g.fillRect(rnd() * W, rnd() * H, 2 + rnd() * 3, 2 + rnd() * 3); }
  // voids: long galleries, round chambers, and narrow crawls, each lit from inside
  const voids = [];
  for (let x = 60; x < W - 150;) {
    const kind = rnd(); const w = kind < 0.25 ? 130 + rnd() * 120 : 250 + rnd() * 550;
    const vh = kind < 0.25 ? H * (0.55 + rnd() * 0.2) : H * (0.28 + rnd() * 0.22);
    const y = H * 0.5 - vh / 2 + (rnd() - 0.5) * H * 0.2;
    voids.push({ x, y, w, h: vh, arch: kind < 0.25 ? vh / 2 : vh * 0.45 });
    x += w + 60 + rnd() * 250;
  }
  for (const v of voids) {
    const shape = new Path2D(); shape.roundRect(v.x, v.y, v.w, v.h, [v.arch, v.arch, 10, 10]);
    const ig = g.createLinearGradient(0, v.y, 0, v.y + v.h); ig.addColorStop(0, '#0a0706'); ig.addColorStop(1, '#2a1708');
    g.fillStyle = ig; g.fill(shape);
    g.strokeStyle = 'rgba(0,0,0,0.7)'; g.lineWidth = 8; g.stroke(shape);
    // lamp glow on the void floor (emissive)
    e.save(); e.clip(shape);
    const n = Math.max(1, Math.round(v.w / 260));
    for (let k = 0; k < n; k++) {
      const lx = v.x + v.w * (k + 0.5) / n, ly = v.y + v.h * 0.42;
      const lg = e.createRadialGradient(lx, ly, 0, lx, ly, v.h * 1.1);
      lg.addColorStop(0, 'rgba(255,200,120,1)'); lg.addColorStop(0.05, 'rgba(255,170,80,0.85)'); lg.addColorStop(0.4, 'rgba(200,100,30,0.35)'); lg.addColorStop(1, 'rgba(120,50,10,0)');
      e.fillStyle = lg; e.fillRect(v.x, v.y, v.w, v.h);
    }
    e.restore();
  }
  // vertical shafts with ladders between floors
  for (let i = 0; i < 5; i++) {
    const x = 200 + rnd() * (W - 400), w = 24;
    g.fillStyle = '#0b0807'; g.fillRect(x, 0, w, H);
    g.strokeStyle = 'rgba(160,110,60,0.6)'; g.lineWidth = 4;
    for (let y = 6; y < H; y += 18) { g.beginPath(); g.moveTo(x + 5, y); g.lineTo(x + w - 5, y); g.stroke(); }
    e.fillStyle = 'rgba(255,160,70,0.25)'; e.fillRect(x, 0, w, H);
  }
  const t = new THREE.CanvasTexture(col), te = new THREE.CanvasTexture(emi);
  t.colorSpace = te.colorSpace = THREE.SRGBColorSpace; t.anisotropy = te.anisotropy = 8;
  return { map: t, emissiveMap: te };
}

export async function setup(THREE, renderer, W, H) {
  const scene = new THREE.Scene();
  const c = document.createElement('canvas'); c.width = 16; c.height = 512;
  const g = c.getContext('2d'), grd = g.createLinearGradient(0, 0, 0, 512);
  grd.addColorStop(0, '#04070d'); grd.addColorStop(0.5, '#0b1322'); grd.addColorStop(1, '#030509');
  g.fillStyle = grd; g.fillRect(0, 0, 16, 512);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;

  const camera = new THREE.PerspectiveCamera(22, W / H, 1, 400);
  camera.position.set(1.5, 17, 44); camera.lookAt(1.5, -1.6, -0.8);

  scene.add(new THREE.HemisphereLight(0xc8d6ff, 0x1a120c, 0.55));
  const key = new THREE.DirectionalLight(0xfff1dc, 2.8); key.position.set(-14, 22, 18); scene.add(key);
  const rim = new THREE.DirectionalLight(0x7fa6d6, 0.6); rim.position.set(16, 6, -10); scene.add(rim);

  const dark = new THREE.MeshStandardMaterial({ color: 0x15100c, roughness: 1 });
  // the map slab
  const top = new THREE.MeshStandardMaterial({ map: await mapTexture(THREE), roughness: 0.92 });
  const crustFace = caveFace(THREE, CRUST, ['#6b5a46', '#4a3b2c'], 0);
  const crustMat = new THREE.MeshStandardMaterial({ map: crustFace.map, roughness: 1 });
  const insetC = STEP * LAYERS.length;
  const slab = new THREE.Mesh(new THREE.BoxGeometry(MW, CRUST, MD - insetC), [dark, dark, top, dark, crustMat, dark]);
  slab.position.set(0, -CRUST / 2, -insetC / 2); scene.add(slab);
  const ledgeMat = new THREE.MeshStandardMaterial({ color: 0x4a3a2a, roughness: 1 });
  const lc = document.createElement('canvas'); lc.width = lc.height = 64;
  const lg = lc.getContext('2d'), lgr = lg.createRadialGradient(32, 32, 0, 32, 32, 32);
  lgr.addColorStop(0, 'rgba(255,215,150,1)'); lgr.addColorStop(0.12, 'rgba(255,170,80,0.9)'); lgr.addColorStop(0.4, 'rgba(255,130,40,0.25)'); lgr.addColorStop(1, 'rgba(255,110,30,0)');
  lg.fillStyle = lgr; lg.fillRect(0, 0, 64, 64);
  const lampMat = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(lc), blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true });

  // underground floors, each a little deeper and darker; warm light leaks out of the gaps
  const tones = [['#5a4734', '#3f3123'], ['#463728', '#30251b'], ['#352a20', '#211a14']];
  let y = -CRUST - GAP;
  LAYERS.forEach((h, i) => {
    const f = caveFace(THREE, h, tones[i], i + 1);
    const front = new THREE.MeshStandardMaterial({ map: f.map, emissiveMap: f.emissiveMap, emissive: 0xffffff, emissiveIntensity: 1.4, roughness: 1 });
    const inset = STEP * (LAYERS.length - 1 - i);
    const m = new THREE.Mesh(new THREE.BoxGeometry(MW, h, MD - inset), [dark, dark, ledgeMat, dark, front, dark]);
    m.position.set(0, y - h / 2, -inset / 2); scene.add(m);
    // glow strip in the gap above this floor
    const strip = new THREE.Mesh(new THREE.PlaneGeometry(MW, GAP * 0.9), new THREE.MeshBasicMaterial({ color: 0xff9a40, transparent: true, opacity: 0.3 - i * 0.06, blending: THREE.AdditiveBlending, depthWrite: false }));
    strip.position.set(0, y + GAP / 2, MD / 2 - inset - STEP - 0.4); scene.add(strip);
    // lanterns along the ledge
    for (let k = 0; k < 22; k++) {
      const sp = new THREE.Sprite(lampMat); sp.scale.set(0.38, 0.38, 1);
      sp.position.set(-MW / 2 + 0.8 + rnd() * (MW - 1.6), y + 0.2, MD / 2 - inset - STEP * (0.3 + rnd() * 0.4)); scene.add(sp);
    }
    // pillars holding the floors apart
    for (let k = 0; k < 14; k++) {
      const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, GAP + 0.02, 0.12), dark);
      p.position.set(-MW / 2 + 1 + k * (MW - 2) / 13, y + GAP / 2, MD / 2 - inset - STEP - 0.15); scene.add(p);
    }
    y -= h + GAP;
  });

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.55, 0.6, 0.72));
  composer.addPass(new OutputPass());
  return { scene, camera, composer };
}

export function update() {}
