import { makeStage, THREE } from '/engine/stage3d.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
export const duration = 2;
let S; const mixers = [];
const people = [[1.75, 1], [1.75, 1.45], [2.03, 1.55], [2.06, 1.7], [2.18, 1.3]];
export async function setup(R) {
  S = await makeStage({ envIntensity: .8, bloom: .15 });
  const g = await new GLTFLoader().loadAsync('/@work/3d/xbot/xbot.glb');
  const box = new THREE.Box3().setFromObject(g.scene); const h0 = box.max.y - box.min.y;
  const idle = g.animations.find(a => /idle/i.test(a.name));
  people.forEach(([h, b], i) => {
    const m = SkeletonUtils.clone(g.scene); const k = h / h0; m.scale.set(k * b, k, k * Math.sqrt(b));
    m.position.x = (i - 2) * .9; S.scene.add(m);
    m.traverse(o => { if (o.isMesh) { o.castShadow = true; console.log(o.name);
      o.material = /joint/i.test(o.name) ? new THREE.MeshStandardMaterial({ color: 0x0c0c0e, metalness: .9, roughness: .3 })
        : new THREE.MeshPhysicalMaterial({ color: i === 0 ? 0x8a8d93 : 0x2a2b30, metalness: .2, roughness: .35, clearcoat: 1, clearcoatRoughness: .15 }); } });
    const mx = new THREE.AnimationMixer(m); mx.clipAction(idle).play(); mixers.push(mx);
  });
  console.log(g.animations.map(a => a.name).join(','));
}
export async function draw(R, t) {
  mixers.forEach((m, i) => m.setTime(t + i * .7));
  S.camera.fov = 34; S.camera.updateProjectionMatrix();
  S.camera.position.set(.8, 1.2, 12.5); S.camera.lookAt(0, 1.2, 0);
  R.g.drawImage(S.render(), 0, 0); R.vignette(.5);
}
