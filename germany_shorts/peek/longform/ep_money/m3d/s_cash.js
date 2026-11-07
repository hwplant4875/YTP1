// b07 "So what happened to the actual cash?" Two accounts on the paper floor, a buyer's tray full of bundles
// and a seller's tray holding a share. On "paid" the bundles arc across while the share arcs back: the cash moved.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, easeOut, smoother, HL } from '../js/iso.js';
import { studio, camKeys, newCam, cashMats, stackGeo, card, canvas, tex, BW, BD, BT } from './common.js';

function tray(s, x, label) {
  const g = new THREE.Group(); g.position.x = x; s.add(g);
  const m = new THREE.MeshStandardMaterial({ color: 0xE6DBC6, roughness: 0.9 });
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 0.9), m); base.position.y = 0.025; base.castShadow = base.receiveShadow = true; g.add(base);
  for (const [w, d, px, pz] of [[1.2, 0.05, 0, 0.425], [1.2, 0.05, 0, -0.425], [0.05, 0.9, 0.575, 0], [0.05, 0.9, -0.575, 0]]) {
    const wl = new THREE.Mesh(new THREE.BoxGeometry(w, 0.14, d), m); wl.position.set(px, 0.07, pz); wl.castShadow = wl.receiveShadow = true; g.add(wl);
  }
  const lb = card([{ text: label, font: '600 120px Jost', y: 160, ls: '18px', color: COL.ink }], { w: 1024, h: 256, sx: 1.0 });
  lb.rotation.x = -Math.PI / 2; lb.position.set(0, 0.003, 0.72); g.add(lb);
  return g;
}

export class CashScene {
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 4, sunPos: [-3, 8, 5] });
    this.cam = newCam();
    tray(s, -1.0, 'BUYER'); tray(s, 1.0, 'SELLER');
    this.bundles = [];
    const mats = cashMats(), geo = stackGeo(BT * 6, 1, 1);
    for (let i = 0; i < 18; i++) {
      const b = new THREE.Mesh(geo, mats); b.castShadow = true; b.scale.setScalar(1.5); s.add(b);
      const home = new THREE.Vector3(-1.0 + ((i % 3) - 1) * 0.26, 0.05 + Math.floor(i / 9) * BT * 9, (Math.floor(i / 3) % 3 - 1) * 0.12);
      const dest = new THREE.Vector3(1.0 + ((i % 3) - 1) * 0.26 - 0.1, 0.05 + Math.floor(i / 9) * BT * 9, (Math.floor(i / 3) % 3 - 1) * 0.12);
      this.bundles.push({ b, home, dest, k: i });
    }
    // the share (same cube as the value scene, with the logo on top and front)
    const cv = canvas(512, 512), g = cv.getContext('2d'); g.fillStyle = '#FBF6EA'; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = 'rgba(43,37,51,0.25)'; g.lineWidth = 10; g.strokeRect(5, 5, 502, 502);
    const L = D.logos.nv, lw = 400, lh = lw * L.height / L.width; g.drawImage(L, 56, 256 - lh / 2, lw, lh);
    const f = new THREE.MeshStandardMaterial({ map: tex(cv), roughness: 0.7 }), sd = new THREE.MeshStandardMaterial({ color: 0xF3ECDD, roughness: 0.8 });
    this.share = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.22, 0.22), [sd, sd, f, sd, f, sd]); this.share.castShadow = true; s.add(this.share);
    this.T = { start: 162.5, actual: cue('b07', 'actual'), sold: cue('b07', 'sold'), bought: cue('b07', 'bought'), paid: cue('b07', 'paid'),
      money: cue('b07', 'money,'), didnt: cue('b07', "didn't"), vanish: cue('b07', 'vanish'), moved: cue('b07', 'moved'), another: cue('b07', 'another.'), end: 177.6 };
  }
  update(t) {
    const T = this.T;
    camKeys(this.cam, [
      [T.start, [0, 3.8, 3.2], [0, 0.1, 0], 34],
      [T.paid, [-0.4, 2.2, 3.0], [0, 0.2, 0], 34],
      [T.moved + 0.4, [0.6, 2.0, 2.8], [0.2, 0.15, 0], 34],
      [T.end, [1.0, 2.2, 3.0], [0.3, 0.15, 0], 34],
    ], t);
    // the share goes seller -> buyer at "bought"
    const ks = smoother(clamp((t - T.bought) / 1.0));
    this.share.position.set(1.0 - 2.0 * ks + 0.25, 0.16 + Math.sin(ks * Math.PI) * 0.7, 0.05); this.share.rotation.y = 0.4 + ks * Math.PI;
    // the bundles go buyer -> seller one after another from "paid"
    for (const q of this.bundles) {
      const k = smoother(clamp((t - T.paid - 0.08 * q.k) / 0.9));
      q.b.position.lerpVectors(q.home, q.dest, k); q.b.position.y += Math.sin(k * Math.PI) * (0.8 + 0.02 * q.k);
      q.b.rotation.set(0, Math.sin(k * Math.PI) * 0.5 * Math.sin(q.k), Math.sin(k * Math.PI) * 0.3);
    }
  }
  overlay(g, t) {
    const T = this.T, o = 1 - clamp((t - T.paid + 0.2) / 0.4);
    if (t > T.actual - 0.2 && o > 0) bigText(g, [['WHERE DID THE ', '#FFFFFF'], ['CASH', HL], [' GO?', '#FFFFFF']], 960, 200, { size: 110, p: clamp((t - T.actual + 0.1) / 0.45), a: o });
    if (t > T.vanish - 0.3) {
      bigText(g, "IT DIDN'T VANISH", 960, 190, { size: 120, p: clamp((t - T.vanish + 0.1) / 0.45) });
      bigText(g, [['IT MOVED', HL]], 960, 340, { size: 140, p: clamp((t - T.moved + 0.1) / 0.45) });
    }
  }
}
