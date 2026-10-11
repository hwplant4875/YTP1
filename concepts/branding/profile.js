// Channel profile picture: a glossy globe marble racing two small marbles. Land from Natural Earth via world-atlas (public domain).
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// minimal TopoJSON -> list of rings ([lon, lat] arrays) for a MultiPolygon/Polygon object
export function topoRings(topo, name) {
  const { scale, translate } = topo.transform;
  const arcs = topo.arcs.map(a => { let x = 0, y = 0; return a.map(([dx, dy]) => { x += dx; y += dy; return [x * scale[0] + translate[0], y * scale[1] + translate[1]]; }); });
  const arc = i => i >= 0 ? arcs[i] : arcs[~i].slice().reverse();
  const ring = idx => idx.flatMap((i, k) => (k ? arc(i).slice(1) : arc(i)));
  const out = [];
  const add = g => { if (g.type === 'Polygon') g.arcs.forEach(r => out.push(ring(r))); else if (g.type === 'MultiPolygon') g.arcs.forEach(p => p.forEach(r => out.push(ring(r)))); else if (g.type === 'GeometryCollection') g.geometries.forEach(add); };
  add(topo.objects[name]);
  return out;
}

export function globeTexture(THREE, rings, w = 4096) {
  const h = w / 2, c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  const sea = g.createLinearGradient(0, 0, 0, h); sea.addColorStop(0, '#1d5fe0'); sea.addColorStop(0.5, '#2b8bff'); sea.addColorStop(1, '#1d5fe0');
  g.fillStyle = sea; g.fillRect(0, 0, w, h);
  const P = ([lon, lat]) => [(lon + 180) / 360 * w, (90 - lat) / 180 * h];
  const path = () => { g.beginPath(); for (const r of rings) { r.forEach((p, i) => { const [x, y] = P(p); i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.closePath(); } };
  // shallow-water rim; skip segments that wrap around the map edge (they would draw straight lines across the globe)
  g.beginPath(); for (const r of rings) r.forEach((p, i) => { const [x, y] = P(p); if (!i || Math.abs(x - P(r[i - 1])[0]) > w / 2 || y > h * 0.97 || y < h * 0.05) g.moveTo(x, y); else g.lineTo(x, y); });
  g.lineJoin = 'round'; g.lineCap = 'round'; g.strokeStyle = '#9fe9ff'; g.lineWidth = w / 300; g.stroke();
  path(); const land = g.createLinearGradient(0, 0, 0, h); land.addColorStop(0, '#e8f6ff'); land.addColorStop(0.07, '#6fd85c'); land.addColorStop(0.5, '#33c04a'); land.addColorStop(0.88, '#6fd85c'); land.addColorStop(1, '#f4fbff');
  g.fillStyle = land; g.fill('evenodd');
  // soft ice caps (also hides polar seam artefacts of the projected land rings)
  for (const [y0, y1] of [[0, h * 0.13], [h, h * 0.87]]) { const ic = g.createLinearGradient(0, y0, 0, y1); ic.addColorStop(0, '#f2fbff'); ic.addColorStop(0.75, 'rgba(235,248,255,0.92)'); ic.addColorStop(1, 'rgba(235,248,255,0)'); g.fillStyle = ic; g.fillRect(0, Math.min(y0, y1), w, Math.abs(y1 - y0)); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}

export async function setup(THREE, renderer, W, H) {
  const topo = await (await fetch('/branding/land-50m.json')).json();
  const scene = new THREE.Scene();
  const bc = document.createElement('canvas'); bc.width = bc.height = 1024; const bg = bc.getContext('2d');
  const rg = bg.createRadialGradient(470, 430, 40, 512, 512, 720); rg.addColorStop(0, '#2b3f8f'); rg.addColorStop(0.45, '#151d47'); rg.addColorStop(1, '#070a1c');
  bg.fillStyle = rg; bg.fillRect(0, 0, 1024, 1024);
  const bgt = new THREE.CanvasTexture(bc); bgt.colorSpace = THREE.SRGBColorSpace; scene.background = bgt;
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 100); camera.position.set(0, -0.15, 10.6); renderer.toneMapping = THREE.NeutralToneMapping; camera.lookAt(0, 0, 0);
  const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(-4, 5, 6); scene.add(key);
  const rim = new THREE.DirectionalLight(0x8fb8ff, 1.6); rim.position.set(5, -2, -3); scene.add(rim);

  const globe = new THREE.Mesh(new THREE.SphereGeometry(1.55, 128, 64), new THREE.MeshPhysicalMaterial({ map: globeTexture(THREE, topoRings(topo, 'land')), roughness: 0.4, clearcoat: 0.7, clearcoatRoughness: 0.06, envMapIntensity: 0.35 }));
  globe.position.set(-0.2, 0.35, 0); globe.rotation.set(0.38, -1.75, -0.18); scene.add(globe);
  const small = (r, c, x, y) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 64, 32), new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.15, clearcoat: 1, clearcoatRoughness: 0.03, sheen: 0.2 })); m.position.set(x, y, 0.4); scene.add(m); return m; };
  const sm = [small(0.46, 0xffb020, 1.35, -1.25), small(0.32, 0xff3d7f, 0.45, -1.72)];

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.12, 0.4, 0.9));
  composer.addPass(new OutputPass());
  return { scene, camera, composer, W, H, sm };
}
export function update() {}
export function overlay(ctx, g) {
  const { W, H } = ctx, s = W / 800;
  // speed streaks behind the two small marbles (they race the globe)
  g.save(); g.globalCompositeOperation = 'lighter'; g.lineCap = 'round';
  for (const [m, c] of [[ctx.sm[0], '255,190,60'], [ctx.sm[1], '255,90,150']]) {
    const q = m.position.clone().project(ctx.camera), x = (q.x + 1) / 2 * 800, y = (1 - q.y) / 2 * 800;
    const e = m.position.clone(); e.y += m.geometry.parameters.radius; const qe = e.project(ctx.camera), r = Math.abs((1 - qe.y) / 2 * 800 - y);
    for (let k = 0; k < 3; k++) {
      const yy = (y + (k - 1) * r * 0.55) * s, gr = g.createLinearGradient((x - r) * s, 0, (x - r - 170) * s, 0);
      gr.addColorStop(0, `rgba(${c},0.55)`); gr.addColorStop(1, `rgba(${c},0)`);
      g.strokeStyle = gr; g.lineWidth = (k === 1 ? 9 : 5) * s; g.beginPath(); g.moveTo((x - r - 8) * s, yy); g.lineTo((x - r - 170 + Math.abs(k - 1) * 50) * s, yy); g.stroke();
    }
  }
  g.restore();
}
