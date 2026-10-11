// Channel banner 2560x1440 (text kept inside the 1546x423 safe area). Flag marbles racing along a glowing rail.
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const RACERS = [['in', 1451], ['us', 345], ['br', 212], ['jp', 124], ['kr', 52], ['de', 84], ['ng', 233], ['gb', 69], ['mx', 131], ['cn', 1419]];
const radius = pop => 0.5 * Math.pow(pop / 50, 0.25);

export async function setup(THREE, renderer, W, H) {
  renderer.toneMapping = THREE.NeutralToneMapping;
  const scene = new THREE.Scene();
  // board: navy with colour washes and a fine grid
  const bc = document.createElement('canvas'); bc.width = 2560; bc.height = 1440; const bg = bc.getContext('2d');
  bg.fillStyle = '#0d1330'; bg.fillRect(0, 0, 2560, 1440);
  for (const [x, y, r, c] of [[300, 300, 900, '#35d9ff'], [2250, 250, 900, '#ff4fa3'], [1280, 1500, 1100, '#a66bff'], [2300, 1300, 700, '#ffd23f'], [250, 1300, 700, '#6dff7a']]) {
    const g = bg.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, c + '38'); g.addColorStop(1, c + '00'); bg.fillStyle = g; bg.fillRect(0, 0, 2560, 1440);
  }
  bg.strokeStyle = 'rgba(255,255,255,0.05)'; bg.lineWidth = 2;
  for (let x = 0; x <= 2560; x += 64) { bg.beginPath(); bg.moveTo(x, 0); bg.lineTo(x, 1440); bg.stroke(); }
  for (let y = 0; y <= 1440; y += 64) { bg.beginPath(); bg.moveTo(0, y); bg.lineTo(2560, y); bg.stroke(); }
  const bt = new THREE.CanvasTexture(bc); bt.colorSpace = THREE.SRGBColorSpace;
  const pmrem = new THREE.PMREMGenerator(renderer); scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(30, W / H, 1, 200); camera.position.set(0, 0, 40); camera.lookAt(0, 0, 0);
  const vh = 2 * 40 * Math.tan(15 * Math.PI / 180), vw = vh * W / H;
  const board = new THREE.Mesh(new THREE.PlaneGeometry(vw * 1.25, vh * 1.25), new THREE.MeshBasicMaterial({ map: bt })); board.position.z = -2; scene.add(board);
  const key = new THREE.DirectionalLight(0xffffff, 2.0); key.position.set(-6, 10, 14); key.castShadow = true; scene.add(key);
  renderer.shadowMap.enabled = true;

  const rail = (a, b, col, th = 0.28) => {
    const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
    const m = new THREE.Mesh(new RoundedBoxGeometry(L, th, 1.2, 3, th * 0.45), new THREE.MeshPhysicalMaterial({ color: col, emissive: col, emissiveIntensity: 0.35, roughness: 0.3, clearcoat: 0.8 }));
    m.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0); m.rotation.z = Math.atan2(dy, dx); scene.add(m);
  };
  // main race rail just under the title, inside the safe area
  const y0 = -2.75, slope = -0.06;
  rail([-vw / 2 - 1, y0 - 0.14 + slope * (-vw / 2 - 1)], [vw / 2 + 1, y0 - 0.14 + slope * (vw / 2 + 1)], '#ffc04a');
  // decorative rails, pegs and bumpers outside the safe area (desktop/TV only)
  rail([-vw / 2 - 1, 8.5], [-9, 5.6], '#35d9ff'); rail([vw / 2 + 1, 8.6], [9.5, 5.4], '#ff4fa3');
  rail([-vw / 2 - 1, -6.4], [-8, -8.8], '#6dff7a'); rail([vw / 2 + 1, -6.0], [8.5, -8.9], '#a66bff');
  const PEG = ['#ff4d6d', '#ff9f1c', '#ffd23f', '#3ee07a', '#35b7ff', '#a66bff'];
  for (let i = 0; i < 26; i++) {
    const side = i % 2 ? 1 : -1, x = side * (13.2 + (i % 5) * 1.5), y = 7.5 - Math.floor(i / 2) * 1.25 + (i % 5) * 0.2;
    if (Math.abs(y) < 4.2 && Math.abs(x) < 14.5) continue;
    const m = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 1.1, 24), new THREE.MeshPhysicalMaterial({ color: PEG[i % 6], emissive: PEG[i % 6], emissiveIntensity: 0.4, roughness: 0.3, clearcoat: 1 }));
    m.rotation.x = Math.PI / 2; m.position.set(x, y, 0); scene.add(m);
  }
  // finish post on the right
  const fc = document.createElement('canvas'); fc.width = 64; fc.height = 256; const fg = fc.getContext('2d');
  for (let y = 0; y < 8; y++) for (let x = 0; x < 2; x++) { fg.fillStyle = (x + y) % 2 ? '#111' : '#fff'; fg.fillRect(x * 32, y * 32, 32, 32); }
  const ft = new THREE.CanvasTexture(fc); ft.colorSpace = THREE.SRGBColorSpace;
  const fin = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 2.4), new THREE.MeshBasicMaterial({ map: ft })); fin.position.set(12.4, y0 + slope * 12.4 + 1.2, -0.6); scene.add(fin);

  // flag marbles in race formation along the rail (leader on the right)
  const tl = new THREE.TextureLoader(); const marbles = [];
  let x = 11.2;
  for (const [code, pop] of RACERS) {
    const r = radius(pop);
    const tex = await new Promise(res => tl.load(`/marble/flags/${code}.png`, res));
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.wrapS = THREE.RepeatWrapping; tex.repeat.set(2, 1); tex.offset.set(0.25, 0);
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 64, 32), new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 0.8 }));
    x -= r + 0.35 + Math.random() * 0.35;
    m.position.set(x, y0 + slope * x + r, 0); m.rotation.set(0.2, -0.5 + Math.random(), -x * 0.7); m.castShadow = true; scene.add(m); marbles.push({ m, r });
    x -= r;
  }
  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.3, 0.5, 0.85));
  composer.addPass(new OutputPass());
  return { scene, camera, composer, W, H, marbles };
}
export function update() {}
export function overlay(ctx, g) {
  const { W, H, camera, marbles } = ctx;
  // motion streaks behind the marbles
  g.save(); g.globalCompositeOperation = 'lighter'; g.lineCap = 'round';
  for (const { m, r } of marbles) {
    const q = m.position.clone().project(camera), x = (q.x + 1) / 2 * W, y = (1 - q.y) / 2 * H, rp = r / (2 * 40 * Math.tan(15 * Math.PI / 180)) * H;
    for (let k = -1; k <= 1; k++) { const gr = g.createLinearGradient(x - rp, 0, x - rp - 150, 0); gr.addColorStop(0, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.strokeStyle = gr; g.lineWidth = k ? 4 : 7; g.beginPath(); g.moveTo(x - rp - 6, y + k * rp * 0.5); g.lineTo(x - rp - 150 + Math.abs(k) * 40, y + k * rp * 0.5); g.stroke(); }
  }
  g.restore();
  // title block inside the safe area (y 508..931)
  g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 30;
  g.font = '150px YTSans'; g.fillStyle = '#fff'; g.fillText('MARBLE RACE', W / 2, 650);
  g.font = '96px Jua'; g.fillStyle = '#ffc04a'; g.fillText('with Facts', W / 2, 752);
  g.shadowBlur = 0; g.shadowColor = 'transparent';
}
