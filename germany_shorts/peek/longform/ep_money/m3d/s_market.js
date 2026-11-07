// The stock market as a field of $100-bundle columns, one per company, in the paper studio.
// mode 'day'    (0:31-1:08): S&P 500 -4.4% (every column loses its top), Nasdaq -5.5%, Qualcomm and Arm
//                step forward on their logo plates and lose 9.5% / 13.1%, then the camera pushes into Nvidia.
// mode 'payoff' (2:57-3:10): one price tag hangs over the whole market and turns to -$2.8T.
// mode 'end'    (3:32-3:47): the field again, wide and calm: not stolen, not burned, repriced.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, easeOut, mulberry32, HL } from '../js/iso.js';
import { W, RED, studio, cashMats, stackGeo, tint, logoPlate, camKeys, newCam, canvas, tex } from './common.js';

const c3 = (w, n) => cue('b03', w, n), c8 = (w, n) => cue('b08', w, n), c10 = (w, n) => cue('b10', w, n);

function tagFace(big, small, color) {
  const cv = canvas(1100, 560), g = cv.getContext('2d');
  g.fillStyle = COL.tag;
  g.beginPath(); g.moveTo(190, 20); g.lineTo(1060, 20); g.quadraticCurveTo(1090, 20, 1090, 50); g.lineTo(1090, 510); g.quadraticCurveTo(1090, 540, 1060, 540);
  g.lineTo(190, 540); g.lineTo(20, 280); g.closePath(); g.fill();
  g.lineWidth = 6; g.strokeStyle = 'rgba(43,37,51,0.35)'; g.stroke();
  g.beginPath(); g.arc(150, 280, 30, 0, Math.PI * 2); g.fillStyle = '#E8DCC2'; g.fill(); g.lineWidth = 10; g.strokeStyle = '#C9A55A'; g.stroke();
  g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  g.font = '600 190px Jost'; g.fillText(big, 650, 320);
  g.font = '600 62px Jost'; g.letterSpacing = '12px'; g.fillStyle = COL.ink; g.fillText(small.toUpperCase(), 650, 450); g.letterSpacing = '0px';
  return cv;
}

export class MarketScene {
  constructor(mode = 'day') { this.mode = mode; }
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 9 });
    this.cam = newCam();
    const shared = cashMats();
    const rnd = mulberry32(5005);
    const NX = 25, NZ = 20, DX = 0.37, DZ = 0.25;
    this.slices = [];
    for (let i = 0; i < NX; i++) for (let j = 0; j < NZ; j++) {
      const x = (i - (NX - 1) / 2) * DX + (rnd() - 0.5) * 0.03, z = (j - (NZ - 1) / 2) * DZ - 2.2 + (rnd() - 0.5) * 0.02;
      const big = Math.pow(rnd(), 7);
      let h = 0.08 + rnd() * 0.3 + big * 1.1;
      const nv = i === 12 && j === NZ - 1;
      if (nv) h = 2.3;
      const body = new THREE.Mesh(stackGeo(h * 0.956, 2, 3), nv ? cashMats() : shared);
      body.position.set(x, 0, z); body.castShadow = body.receiveShadow = true; s.add(body);
      const sl = new THREE.Mesh(stackGeo(h * 0.044, 2, 3), cashMats());
      sl.position.set(x, h * 0.956, z); sl.castShadow = true; s.add(sl);
      this.slices.push({ m: sl, x, z, h, y0: h * 0.956, d: rnd(), spin: rnd() - 0.5, nv });
    }
    this.nv = this.slices.find(q => q.nv);
    const nvPlate = logoPlate(D.logos.nv, 0.62, 0.15); nvPlate.position.set(this.nv.x, 0.075, this.nv.z + 0.17); s.add(nvPlate);

    this.front = [];
    if (this.mode === 'day') {
      for (const [k, x, h, loss] of [['qc', -0.75, 0.62, 0.0949], ['arm', 0.75, 0.5, 0.1308]]) {
        const g = new THREE.Group(); g.position.set(x, 0, 0.6); s.add(g);
        const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.08, 0.6), new THREE.MeshStandardMaterial({ color: 0xE6DBC6, roughness: 0.9 }));
        base.position.y = 0.04; base.castShadow = base.receiveShadow = true; g.add(base);
        const body = new THREE.Mesh(stackGeo(h * (1 - loss), 4, 4), cashMats()); body.position.y = 0.08; body.castShadow = body.receiveShadow = true; g.add(body);
        const top = new THREE.Mesh(stackGeo(h * loss, 4, 4), cashMats()); top.position.y = 0.08 + h * (1 - loss); top.castShadow = true; g.add(top);
        const plate = logoPlate(D.logos[k], 0.78, 0.2); plate.position.set(0, 0.16, 0.36); plate.rotation.x = -0.18; g.add(plate);
        this.front.push({ g, top, y0: top.position.y });
      }
    }
    if (this.mode === 'payoff') {
      // one big price tag on a string over the whole market (front: before, back: after)
      const tg = this.tag = new THREE.Group(); s.add(tg);
      const mk = (cv, flip) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.12), new THREE.MeshStandardMaterial({ map: tex(cv), transparent: true, roughness: 0.75, side: THREE.FrontSide }));
        if (flip) m.rotation.y = Math.PI; m.castShadow = true; return m; };
      this.tagA = mk(tagFace('S&P 500', 'price tag', COL.ink)); this.tagB = mk(tagFace('−$2.8T', 'Nov 5, 2026', '#C8503E'), true);
      const pivot = this.tagPivot = new THREE.Group(); pivot.add(this.tagA, this.tagB);
      this.tagA.position.set(0.95, -0.56, 0.005); this.tagB.position.set(0.95, -0.56, -0.005);
      tg.add(pivot);
      const str = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 6, 6), new THREE.MeshStandardMaterial({ color: 0x8a7458 })); str.position.set(0.15, 3, 0); tg.add(str);
      this.tagHome = new THREE.Vector3(-0.7, 2.75, 0.5);
    }
    this.T = { here: cue('b03', "Here's"), sp: c3('S'), fell: c3('fell'), nas: c3('Nasdaq'), half: c3('half'), analysts: c3('Analysts'), chips: c3('chips.'),
      two: c3('Two'), qc: c3('Qualcomm'), arm: c3('Arm,'), dis: c3('disappointed'), whole: c3('whole'), end: cue('b04', 'To'), peek: cue('b04', 'peek'),
      ans: c8('answer'), price: c8('price'), wholeP: c8('whole'), shrank: c8('shrank'), never: c8('never'), b9: cue('b09', 'That'),
      b10: cue('b10', 'So'), stolen: c10('stolen'), burned: c10('burned,'), rep: c10('repriced.'), did: c10('Did'), endT: 227.5 };
  }

  update(t) {
    const T = this.T, m = this.mode;
    if (m === 'day') camKeys(this.cam, [
      [T.here - 0.1, [0.8, 14, 9.0], [0, 0, -2.2], 32],
      [T.sp - 0.3, [-6.2, 4.4, 4.6], [0.0, 0.3, -2.0], 34],
      [T.fell + 2.2, [-4.2, 2.6, 3.4], [0.4, 0.4, -2.2], 34],
      [T.nas + 2.5, [3.6, 3.0, 3.2], [0.0, 0.5, -2.4], 32],
      [T.chips, [2.2, 2.4, 4.4], [0.0, 0.7, -0.6], 34],
      [T.qc + 0.2, [0.1, 1.35, 3.7], [0.0, 0.42, 0.4], 36],
      [T.dis + 1.4, [0.25, 1.15, 3.2], [0.0, 0.4, 0.5], 36],
      [T.whole + 0.4, [-1.2, 3.6, 6.6], [0.0, 0.5, -1.4], 34],
      [T.end + 0.4, [0.6, 2.4, 3.6], [0.0, 1.3, -2.2], 32],
      [T.peek + 0.6, [0.05, 1.7, -0.9], [0.0, 1.5, -2.2], 30],
    ], t);
    else if (m === 'payoff') camKeys(this.cam, [
      [T.ans - 0.6, [-7.5, 6.5, 7.5], [0, 0.6, -2.2], 34],
      [T.price, [-4.6, 4.2, 6.2], [0.0, 1.2, -1.6], 34],
      [T.shrank + 0.2, [2.6, 3.4, 6.4], [0.0, 1.3, -1.4], 34],
      [T.b9 + 1.5, [5.4, 4.4, 5.6], [0.0, 1.0, -1.8], 34],
    ], t);
    else camKeys(this.cam, [
      [T.b10 - 0.6, [6.0, 5.0, 6.0], [0, 0.4, -2.2], 34],
      [T.rep, [-1.5, 3.2, 5.6], [0, 0.6, -2.2], 34],
      [T.endT, [-6.0, 8.5, 8.0], [0, 0.2, -2.2], 34],
    ], t);
    // focus + context while Qualcomm and Arm are named
    const foc = m === 'day' ? clamp((t - T.two + 0.3) / 0.8) * (1 - clamp((t - T.whole) / 1.0)) : 0;
    this.s.fog.near = 10 - 6.8 * foc; this.s.fog.far = 26 - 16 * foc;
    // the top slices: in 'day' they fall at "fell"; in 'payoff' they are gone already and stay gone;
    // in 'end' the field stands repriced (tops gone)
    for (const q of this.slices) {
      if (m !== 'day') { q.m.visible = false; continue; }
      const t0 = T.fell + 0.05 + q.d * 0.7, f = t - t0;
      tint(q.m.material, f > 0 ? clamp(f / 0.12) : 0);
      if (f <= 0.15) { q.m.position.set(q.x, q.y0, q.z); q.m.rotation.set(0, 0, 0); q.m.visible = true; continue; }
      const ff = f - 0.15, y = q.y0 - 4.9 * ff * ff;
      q.m.visible = y > -0.05;
      q.m.position.set(q.x + q.spin * 0.15 * ff, Math.max(y, -0.05), q.z + 0.05 * ff);
      q.m.rotation.set(q.spin * 2.2 * ff, 0, q.spin * 1.6 * ff);
    }
    for (const [k, F] of this.front.entries()) {
      const tn = k === 0 ? T.qc : T.arm, rise = easeOut(clamp((t - tn + 0.35) / 0.7));
      const leave = clamp((t - T.end) / 0.8);
      F.g.position.y = -1.6 * (1 - rise) - 1.6 * leave * leave; F.g.visible = rise > 0 && leave < 1;
      const f = t - (T.dis - 0.1 + k * 0.25);
      tint(F.top.material, f > 0 ? clamp(f / 0.12) : 0);
      if (f <= 0.15) { F.top.position.set(0, F.y0, 0); F.top.rotation.set(0, 0, 0); F.top.visible = true; }
      else { const ff = f - 0.15; F.top.position.set((k ? 0.25 : -0.25) * ff, F.y0 - 4.9 * ff * ff, 0.1 * ff); F.top.rotation.set(0.6 * ff, 0, (k ? -1 : 1) * 1.4 * ff); F.top.visible = F.top.position.y > -0.2; }
    }
    if (this.tag) {
      const drop = easeOut(clamp((t - T.never + 0.2) / 0.9));
      const tt = Math.max(0, t - T.never);
      const sw = Math.sin(tt * 2.1) * Math.exp(-tt * 0.9) * 0.22;
      this.tag.position.set(this.tagHome.x, this.tagHome.y + 4 * (1 - drop), this.tagHome.z);
      const turn = clamp((t - T.shrank - 0.02) / 0.6), rot = Math.PI * (turn * turn * (3 - 2 * turn));
      const jolt = t > T.shrank ? 0.12 * Math.sin((t - T.shrank) * 8) * Math.exp(-(t - T.shrank) * 2.5) : 0;
      this.tagPivot.rotation.set(jolt, rot + sw, 0);
      const k = 1 - 0.18 * easeOut(clamp((t - T.shrank - 0.3) / 0.6));
      this.tagPivot.scale.setScalar(k);
    }
  }

  overlay(g, t) {
    const T = this.T, m = this.mode;
    if (m === 'day') {
      const spA = 1 - clamp((t - T.analysts) / 0.4);
      if (t > T.sp - 0.1 && spA > 0) {
        bigText(g, 'S&P 500', 120, 190, { size: 120, p: clamp((t - T.sp + 0.1) / 0.45), a: spA, align: 'left' });
        bigText(g, [['-4.4%', RED]], 120, 190 + 140, { size: 140, p: clamp((t - T.fell - 0.25) / 0.45), a: spA, align: 'left' });
      }
      if (t > T.nas - 0.1 && spA > 0) {
        bigText(g, 'NASDAQ', W - 120, 190, { size: 120, p: clamp((t - T.nas + 0.1) / 0.45), a: spA, align: 'right' });
        bigText(g, [['-5.5%', RED]], W - 120, 190 + 140, { size: 140, p: clamp((t - T.half + 0.1) / 0.45), a: spA, align: 'right' });
      }
      const fA = 1 - clamp((t - T.whole) / 0.4);
      if (t > T.dis && fA > 0) {
        bigText(g, [['-9.5%', RED]], 330, 300, { size: 130, p: clamp((t - T.dis - 0.2) / 0.45), a: fA });
        bigText(g, [['-13.1%', RED]], W - 330, 300, { size: 130, p: clamp((t - T.dis - 0.45) / 0.45), a: fA });
      }
    } else if (m === 'payoff') {
      const pa = clamp((t - T.price + 0.1) / 0.45), out = 1 - clamp((t - T.b9 + 0.6) / 0.4);
      if (pa > 0 && out > 0) {
        bigText(g, [['A ', '#FFFFFF'], ['PRICE TAG', HL], [',', '#FFFFFF']], W - 100, 850, { size: 112, p: pa, a: out, align: 'right' });
        bigText(g, 'NOT CASH', W - 100, 850 + 126, { size: 112, p: clamp((t - T.price - 0.3) / 0.45), a: out, align: 'right' });
      }
    } else {
      const o1 = 1 - clamp((t - T.did + 0.4) / 0.4);
      if (o1 > 0) {
        bigText(g, 'NOT STOLEN.', 960, 330, { size: 120, p: clamp((t - T.stolen + 0.1) / 0.45), a: o1 });
        bigText(g, 'NOT BURNED.', 960, 470, { size: 120, p: clamp((t - T.burned + 0.1) / 0.45), a: o1 });
        bigText(g, [['REPRICED.', HL]], 960, 650, { size: 170, p: clamp((t - T.rep + 0.1) / 0.45), a: o1 });
      }
      if (t > T.did - 0.2) {
        bigText(g, 'DID YOU CHECK YOUR', 960, 420, { size: 110, p: clamp((t - T.did + 0.1) / 0.45) });
        bigText(g, [['PORTFOLIO', HL], [' ON NOV 5?', '#FFFFFF']], 960, 560, { size: 110, p: clamp((t - T.did - 0.4) / 0.45) });
      }
    }
  }
}
