// lib_human.js: realistic rigged humans for STRATA 3D shorts.
//
// Source: Microsoft Rocketbox Avatar Library (MIT licence, commercial use and redistribution allowed),
// https://github.com/microsoft/Microsoft-Rocketbox. The "_facial" FBX exports carry 175 blendshapes
// (52 ARKit "AK_*", FACS "AU_*", 15 visemes "AA_VI_*") plus a 3ds Max biped skeleton ("Bip01_*").
// Assets live in assets/rocketbox/<Avatar>/ (FBX + textures converted from TGA to JPG/PNG, see README there).
//
//   const h = await loadHuman(THREE, { avatar: 'Male_Adult_03', tex: 'm004' });
//   scene.add(h.root);
//   h.pose(POSES.shock, 1);                 // body pose (world-space deltas from the bind T-pose)
//   h.expr(EXPR.shock, 0.9);                // facial blendshapes, 0..1 weight
//   h.setSphereHead(true, { color: 0xe8c4a8 });  // minimalist fallback: plain sphere instead of the face
//   h.update(t);                            // idle breathing + blinks + sphere follow (call every frame)
//
// Units: metres (FBX is in cm, scaled 0.01). The character stands at the origin facing +z.
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

const BASE = '/assets/rocketbox/';

// ARKit-style expressions (keys are the AK_ names without prefix/number). Values 0..1.
export const EXPR = {
  neutral: {},
  // ARKit shapes alone are subtle on these heads, so the FACS action units (AU_*) are stacked on top
  shock: { EyeWideLeft: 1, EyeWideRight: 1, BrowInnerUp: 1, BrowOuterUpLeft: 1, BrowOuterUpRight: 1,
    AU_InnerBrowRaiser: 0.8, AU_OuterBrowRaiser: 0.8, AU_UpperLidRaiser: 1,
    JawOpen: 0.45, AU_JawDrop: 0.35, MouthFunnel: 0.2, MouthStretchLeft: 0.3, MouthStretchRight: 0.3, MouthLowerDownLeft: 0.5, MouthLowerDownRight: 0.5 },
  fear: { EyeWideLeft: 0.9, EyeWideRight: 0.9, BrowInnerUp: 1, BrowDownLeft: 0.15, BrowDownRight: 0.15,
    MouthStretchLeft: 0.7, MouthStretchRight: 0.7, JawOpen: 0.2, MouthFrownLeft: 0.3, MouthFrownRight: 0.3, MouthLowerDownLeft: 0.3, MouthLowerDownRight: 0.3 },
  anger: { BrowDownLeft: 1, BrowDownRight: 1, EyeSquintLeft: 0.6, EyeSquintRight: 0.6, NoseSneerLeft: 0.6, NoseSneerRight: 0.6,
    MouthPressLeft: 0.5, MouthPressRight: 0.5, JawForward: 0.2, MouthUpperUpLeft: 0.3, MouthUpperUpRight: 0.3 },
  sad: { BrowInnerUp: 0.8, MouthFrownLeft: 0.7, MouthFrownRight: 0.7, EyeLookDownLeft: 0.4, EyeLookDownRight: 0.4, MouthShrugLower: 0.4, EyeSquintLeft: 0.2, EyeSquintRight: 0.2 },
  smile: { MouthSmileLeft: 0.8, MouthSmileRight: 0.8, CheekSquintLeft: 0.4, CheekSquintRight: 0.4, EyeSquintLeft: 0.3, EyeSquintRight: 0.3 },
  scream: { JawOpen: 1, EyeWideLeft: 1, EyeWideRight: 1, BrowInnerUp: 1, MouthStretchLeft: 0.6, MouthStretchRight: 0.6, MouthUpperUpLeft: 0.5, MouthUpperUpRight: 0.5 },
};

// Body poses: list of [bone, worldAxis xyz, degrees], applied in order (parents first) on top of the bind T-pose.
// Character faces +z, his left arm points to +x; the bind pose is an A-pose (arms ~45 deg down).
const X = [1, 0, 0], Y = [0, 1, 0], Z = [0, 0, 1];
export const POSES = {
  stand: [
    ['Bip01_L_UpperArm', Z, -36], ['Bip01_R_UpperArm', Z, 36],
    ['Bip01_L_UpperArm', X, -5], ['Bip01_R_UpperArm', X, -5],
    ['Bip01_L_Forearm', X, -12], ['Bip01_R_Forearm', X, -12],
  ],
  // recoiling in shock: hands come up in front of the chest, upper body and head pulled back a little
  shock: [
    ['Bip01_Spine1', X, -5], ['Bip01_Head', X, -6],
    ['Bip01_L_UpperArm', Z, -48], ['Bip01_R_UpperArm', Z, 48],
    ['Bip01_L_UpperArm', X, -40], ['Bip01_R_UpperArm', X, -40],
    ['Bip01_L_Forearm', X, -90], ['Bip01_R_Forearm', X, -90],
    ['Bip01_L_Forearm', Y, 70], ['Bip01_R_Forearm', Y, -70],
    ['Bip01_L_Hand', X, -20], ['Bip01_R_Hand', X, -20],
  ],
};

const FINGERS = ['1', '2', '3', '4'];

export async function loadHuman(THREE, { avatar = 'Male_Adult_03', tex = 'm004', anisotropy = 8 } = {}) {
  const dir = BASE + avatar + '/';
  // FBX references D:\...\*.tga; give it a dummy handler so it does not warn or fetch them, we assign our own maps.
  const manager = new THREE.LoadingManager();
  manager.addHandler(/\.tga$/i, { load: () => new THREE.Texture(), setPath() { return this; }, setCrossOrigin() { return this; } });
  const fbx = await new FBXLoader(manager).loadAsync(dir + avatar + '_facial.fbx');
  const tl = new THREE.TextureLoader();
  const T = async (name, srgb) => {
    const t = await tl.loadAsync(dir + tex + '_' + name);
    t.flipY = true; t.anisotropy = anisotropy; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t;
  };
  const [bc, bn, br, hc, hn, hr, op] = await Promise.all([
    T('body_color.jpg', true), T('body_normal.jpg'), T('body_rough.jpg'),
    T('head_color.jpg', true), T('head_normal.jpg'), T('head_rough.jpg'), T('opacity_color.png', true)]);
  const mats = {
    body: new THREE.MeshStandardMaterial({ name: 'body', map: bc, normalMap: bn, roughnessMap: br, roughness: 0.9, normalScale: new THREE.Vector2(1, 1) }),
    // skin: a touch of sheen + warm emissive lift fakes subsurface scattering so the face does not look like plastic
    head: new THREE.MeshPhysicalMaterial({ name: 'head', map: hc, normalMap: hn, roughnessMap: hr, roughness: 0.7,
      sheen: 0.2, sheenRoughness: 0.6, sheenColor: new THREE.Color(0xff8a70), normalScale: new THREE.Vector2(0.8, 0.8) }),
    hair: new THREE.MeshStandardMaterial({ name: 'hair', map: op, alphaTest: 0.42, side: THREE.DoubleSide, roughness: 0.7, alphaToCoverage: true }),
  };
  let mesh = null;
  fbx.traverse(o => {
    if (!o.isSkinnedMesh) return;
    mesh = o; o.castShadow = true; o.receiveShadow = true; o.frustumCulled = false;
    o.material = [].concat(o.material).map(m => /head/i.test(m.name) ? mats.head : /opacity/i.test(m.name) ? mats.hair : mats.body);
  });
  fbx.scale.setScalar(0.01);
  const root = new THREE.Group(); root.add(fbx);

  const bones = {}; fbx.traverse(o => { if (o.isBone) bones[o.name] = o; });
  const bind = {}; for (const k in bones) bind[k] = bones[k].quaternion.clone();
  // blendshape index by short name: "blendShape1.AK_25_JawOpen" -> "JawOpen", also "AU_26_JawDrop" -> "AU_JawDrop"
  const morph = {};
  for (const [k, i] of Object.entries(mesh.morphTargetDictionary)) {
    const m = k.match(/(AK|AU|AA_VI|HB)_\d+_(.+)$/); if (!m) continue;
    morph[m[1] === 'AK' ? m[2] : m[1] + '_' + m[2]] = i;
  }

  const qa = new THREE.Quaternion(), qp = new THREE.Quaternion(), qb = new THREE.Quaternion(), ax = new THREE.Vector3();
  function rotWorld(b, axis, deg) {
    b.parent.updateWorldMatrix(true, false); b.updateWorldMatrix(false, false);
    b.parent.getWorldQuaternion(qp); b.getWorldQuaternion(qb);
    qa.setFromAxisAngle(ax.set(...axis).normalize(), deg * Math.PI / 180);
    b.quaternion.copy(qp.invert().multiply(qa.multiply(qb)));
  }
  let curPose = [], curW = 1, curExpr = {}, curExprW = 0, sphere = null, sphereOn = false;
  const h = {
    root, mesh, bones, morph, mats,
    // apply a pose (array of [bone, axis, deg]) blended by w (0..1); optional extra list appended after
    pose(list, w = 1, extra = []) {
      curPose = list; curW = w;
      for (const k in bones) bones[k].quaternion.copy(bind[k]);
      for (const [n, a, d] of [...list, ...extra]) if (bones[n]) rotWorld(bones[n], a, d * w);
      // relaxed fingers
      for (const s of ['L', 'R']) for (const f of FINGERS) for (const j of ['', '1', '2']) {
        const b = bones[`Bip01_${s}_Finger${f}${j}`]; if (b) b.rotateZ((j === '' ? 0.25 : 0.35));
      }
    },
    expr(dict, w = 1, blink = 0) {
      curExpr = dict; curExprW = w;
      const inf = mesh.morphTargetInfluences; inf.fill(0);
      for (const [k, v] of Object.entries(dict)) if (k in morph) inf[morph[k]] = Math.min(1, v * w);
      if (blink > 0) { inf[morph.EyeBlinkLeft] = Math.max(inf[morph.EyeBlinkLeft], blink); inf[morph.EyeBlinkRight] = Math.max(inf[morph.EyeBlinkRight], blink); }
    },
    // replace the face with a plain smooth sphere (head bone collapsed, sphere follows it)
    setSphereHead(on, { color = 0xcf9f86, radius = 0.118, roughness = 0.62, lift = 0.07 } = {}) {
      sphereOn = on; h.sphereLift = lift;
      if (!sphere) {
        sphere = new THREE.Mesh(new THREE.SphereGeometry(radius, 96, 64), new THREE.MeshPhysicalMaterial({ color, roughness, sheen: 0.25, sheenRoughness: 0.5, sheenColor: new THREE.Color(0xff9a80) }));
        sphere.castShadow = true; root.add(sphere);
      }
      sphere.visible = on;
      mats.hair.visible = !on;
      bones.Bip01_Head.scale.setScalar(on ? 0.001 : 1);
    },
    // per-frame: breathing + blinks; t in seconds
    update(t, { breathe = 1, blinkAt = [1.7, 4.3, 6.9] } = {}) {
      h.pose(curPose, curW, [['Bip01_Spine2', X, Math.sin(t * 2.1) * 1.2 * breathe], ['Bip01_Neck', X, Math.sin(t * 2.1 + 0.6) * 0.6 * breathe]]);
      let bl = 0; for (const b of blinkAt) { const d = Math.abs(t - b); if (d < 0.09) bl = Math.max(bl, 1 - d / 0.09); }
      h.expr(curExpr, curExprW, bl);
      h.syncHead && h.syncHead();
      if (sphere && sphereOn) {
        root.updateMatrixWorld(true);
        const hb = bones.Bip01_Head; const p = new THREE.Vector3(); hb.getWorldPosition(p);
        root.worldToLocal(p); sphere.position.copy(p).add(new THREE.Vector3(0, h.sphereLift, 0.015));
      }
    },
  };
  // head-mounted props (hats, monocles, collars): a group in root space that follows the head bone.
  // Children are authored in metres in an upright frame: origin at the head bone pivot (top of the neck), +y up, +z forward.
  const headGroup = new THREE.Group(); root.add(headGroup); h.headGroup = headGroup;
  const _m = new THREE.Matrix4(), _p = new THREE.Vector3(), _q = new THREE.Quaternion(), _s = new THREE.Vector3();
  const headRel = () => { root.updateMatrixWorld(true); _m.copy(root.matrixWorld).invert().multiply(bones.Bip01_Head.matrixWorld); _m.decompose(_p, _q, _s); return [_p.clone(), _q.clone()]; };
  const headBindQInv = headRel()[1].invert();
  h.syncHead = () => { const [p, q] = headRel(); headGroup.position.copy(p); headGroup.quaternion.copy(q.multiply(headBindQInv)); };
  // per-material colour tint (e.g. recolour the modern jacket into a period coat): h.tint('body', 0x553322)
  h.tint = (which, color) => { mats[which].color.set(color); };
  h.pose(POSES.stand);
  return h;
}
