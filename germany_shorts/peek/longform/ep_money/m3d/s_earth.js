// "nearly $450 billion ... a stack almost 500 km tall, higher than the space station, from a single company."
// The real Earth (NASA Blue Marble texture), 1 unit = 1000 km. The $100-bill stack rises from Santa Clara
// (Nvidia's home) to 490 km ($448B / $100 x 0.109 mm), past the ISS orbit at ~420 km.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, easeOut, smoother, mulberry32, HL } from '../js/iso.js';
import { W, camKeys, newCam, cashMats, stackGeo, toScreen, img, tex } from './common.js';

const R = 6.371, LAT = 37.37, LON = -121.96;

export class EarthScene {
  async init(D) {
    const s = this.s = new THREE.Scene();
    s.background = new THREE.Color(0x0B1020);
    this.cam = newCam(); this.cam.near = 0.003; this.cam.far = 120; this.cam.updateProjectionMatrix();
    s.add(new THREE.HemisphereLight(0xdde8ff, 0x202638, 0.9));
    const sun = new THREE.DirectionalLight(0xfff4e6, 3.6); sun.position.set(-6, 10, 9); s.add(sun);
    // the globe, turned so Santa Clara sits at the top (+y)
    const day = tex(await img('/germany_shorts/peek/shorts/ep_money/assets/earth_day_3840.jpg'));
    day.wrapS = day.wrapT = THREE.ClampToEdgeWrapping;
    const earth = new THREE.Mesh(new THREE.SphereGeometry(R, 192, 128), new THREE.MeshStandardMaterial({ map: day, roughness: 0.85 }));
    const th = (90 - LAT) * Math.PI / 180, ph = (LON + 180) / 360 * Math.PI * 2;
    const p = new THREE.Vector3(-Math.cos(ph) * Math.sin(th), Math.cos(th), Math.sin(ph) * Math.sin(th));
    const q = new THREE.Quaternion().setFromUnitVectors(p, new THREE.Vector3(0, 1, 0));
    const tw = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0.5);
    earth.quaternion.copy(tw.multiply(q)); s.add(earth);
    // thin atmosphere rim
    const atm = new THREE.Mesh(new THREE.SphereGeometry(R * 1.005, 128, 96), new THREE.ShaderMaterial({
      transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); v = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }',
      fragmentShader: 'varying vec3 n; varying vec3 v; void main(){ float f = pow(1. - abs(dot(n, v)), 3.); gl_FragColor = vec4(0.45,0.7,1.0,1.) * f * 0.7; }',
    }));
    s.add(atm);
    // stars
    const r = mulberry32(42), pts = [];
    for (let i = 0; i < 2500; i++) { const u = r() * 2 - 1, a = r() * Math.PI * 2, k = Math.sqrt(1 - u * u); pts.push(90 * k * Math.cos(a), 90 * u, 90 * k * Math.sin(a)); }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    s.add(new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xffffff, size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0.7 })));
    // the stack (width exaggerated so it reads); grows by scale.y
    const st = this.stack = new THREE.Mesh(stackGeo(0.49, 1, 2), cashMats());
    st.scale.set(0.12, 1, 0.12); st.position.y = R - 0.002; s.add(st);
    // ISS orbit ring (plane through the stack) and a small station model
    const ring = this.ring = new THREE.Mesh(new THREE.TorusGeometry(R + 0.42, 0.0016, 8, 720), new THREE.MeshBasicMaterial({ color: 0xFFD23F, transparent: true, opacity: 0 }));
    ring.rotation.y = 0.35; s.add(ring);
    const iss = this.iss = new THREE.Group();
    const m = (c) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.5, metalness: 0.4 });
    const truss = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.0025, 0.0025), m(0xD8D8D8)); iss.add(truss);
    for (const x of [-0.012, -0.006, 0.006, 0.012]) { const pnl = new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.0004, 0.016), m(0x3A4C8A)); pnl.position.x = x; iss.add(pnl); }
    const mod = new THREE.Mesh(new THREE.CylinderGeometry(0.0016, 0.0016, 0.014, 12), m(0xEDEDED)); mod.rotation.x = Math.PI / 2; iss.add(mod);
    iss.scale.setScalar(2.2);
    s.add(iss);
    this.T = { start: 89.4, because: cue('b04', 'Because'), earth: cue('b04', 'Earth,'), nearly: cue('b04', 'nearly'), billion: cue('b04', 'billion'),
      bills: cue('b04', 'hundred-dollar'), stack: cue('b04', 'stack'), five: cue('b04', 'five'), km: cue('b04', 'kilometers'), higher: cue('b04', 'higher'),
      station: cue('b04', 'station,'), single: cue('b04', 'single'), end: 106.2 };
  }
  issPos(t) {
    const a = 0.055 - 0.004 * (t - this.T.higher);
    const v = new THREE.Vector3(Math.sin(a) * (R + 0.42), Math.cos(a) * (R + 0.42), 0);
    return v.applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.35);
  }
  update(t) {
    const T = this.T;
    camKeys(this.cam, [
      [T.start, [-2.6, R + 3.8, 9.5], [0, R - 0.6, 0], 34],
      [T.nearly, [-0.9, R + 1.0, 3.2], [0, R + 0.05, 0], 32],
      [T.bills, [-0.25, R + 0.05, 0.75], [0, R + 0.08, 0], 34],
      [T.km, [-0.5, R + 0.42, 1.25], [0, R + 0.3, 0], 34],
      [T.station + 0.4, [-0.9, R + 0.55, 1.9], [0, R + 0.3, 0], 34],
      [T.end, [-1.6, R + 0.9, 3.4], [0, R + 0.22, 0], 34],
    ], t, 0.15);
    const g = smoother(clamp((t - T.bills) / (T.km + 0.6 - T.bills)));
    this.stack.scale.y = Math.max(0.0005, g);
    this.stack.visible = t > T.bills - 0.1;
    this.ring.material.opacity = 0.75 * clamp((t - T.higher + 0.4) / 0.6);
    this.iss.position.copy(this.issPos(t)); this.iss.lookAt(0, 0, 0);
    this.iss.visible = t > T.higher - 0.6;
  }
  overlay(g, t) {
    const T = this.T;
    const o1 = 1 - clamp((t - T.bills + 0.2) / 0.4);
    if (t > T.nearly - 0.2 && o1 > 0) {
      bigText(g, 'NEARLY', 960, 420, { size: 110, p: clamp((t - T.nearly + 0.1) / 0.45), a: o1 });
      bigText(g, [['$450 BILLION', '#FF6B57']], 960, 590, { size: 190, p: clamp((t - T.billion + 0.3) / 0.45), a: o1 });
    }
    if (t > T.five - 0.2) {
      bigText(g, [['490 KM', HL], [' OF $100 BILLS', '#FFFFFF']], 110, 180, { size: 110, p: clamp((t - T.five + 0.1) / 0.45), align: 'left' });
    }
    const a = clamp((t - T.higher) / 0.4);
    if (a > 0) {
      const [x, y] = toScreen(this.cam, this.issPos(t));
      g.save(); g.globalAlpha = a; g.font = '600 46px Jost'; g.letterSpacing = '6px'; g.textAlign = 'left'; g.textBaseline = 'middle';
      g.strokeStyle = '#fff'; g.lineWidth = 3; g.beginPath(); g.moveTo(x + 14, y - 10); g.lineTo(x + 90, y - 70); g.lineTo(x + 120, y - 70); g.stroke();
      g.fillStyle = '#fff'; g.fillText('ISS  420 KM', x + 132, y - 70); g.restore();
      const top = toScreen(this.cam, new THREE.Vector3(0, R + 0.49, 0));
      g.save(); g.globalAlpha = a; g.font = '600 46px Jost'; g.letterSpacing = '6px'; g.textAlign = 'right'; g.textBaseline = 'middle';
      g.strokeStyle = '#fff'; g.lineWidth = 3; g.beginPath(); g.moveTo(top[0] - 14, top[1]); g.lineTo(top[0] - 110, top[1] - 50); g.lineTo(top[0] - 140, top[1] - 50); g.stroke();
      g.fillStyle = '#FFD23F'; g.fillText('NVIDIA  490 KM', top[0] - 152, top[1] - 50); g.restore();
    }
  }
}
