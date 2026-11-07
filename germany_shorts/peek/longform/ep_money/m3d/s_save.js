// b09 "That doesn't mean the drop didn't matter." Retirement accounts and pension funds hold the same
// companies (small fields of bundle columns in two trays, with the same logos); their savings shrink on paper.
// A paper loss becomes a cash loss only when someone sells below what they paid: $200.13 -> $181.60.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, smoother, mulberry32, HL } from '../js/iso.js';
import { RED, studio, camKeys, newCam, cashMats, stackGeo, card, logoPlate, tint } from './common.js';

export class SaveScene {
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 5, sunPos: [-4, 9, 6] });
    this.cam = newCam();
    this.cols = [];
    const r = mulberry32(909);
    for (const [x, label] of [[-1.25, 'RETIREMENT ACCOUNTS'], [1.25, 'PENSION FUNDS']]) {
      const g = new THREE.Group(); g.position.x = x; s.add(g);
      const m = new THREE.MeshStandardMaterial({ color: 0xE6DBC6, roughness: 0.9 });
      const base = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.06, 1.5), m); base.position.y = 0.03; base.castShadow = base.receiveShadow = true; g.add(base);
      const lb = card([{ text: label, font: '600 92px Jost', y: 150, ls: '14px', color: COL.ink }], { w: 1600, h: 220, sx: 1.9 });
      lb.rotation.x = -Math.PI / 2; lb.position.set(0, 0.003, 1.0); g.add(lb);
      const mats = cashMats();
      for (let i = 0; i < 7; i++) for (let k = 0; k < 4; k++) {
        const h = 0.08 + r() * 0.22 + Math.pow(r(), 6) * 0.5 + (i === 3 && k === 3 ? 0.55 : 0);
        const own = cashMats();
        const c = new THREE.Mesh(stackGeo(h, 2, 3), own); c.position.set((i - 3) * 0.27, 0.06, (k - 1.5) * 0.3); c.castShadow = c.receiveShadow = true; g.add(c);
        this.cols.push({ c, h, own, d: r() });
      }
      const pl = logoPlate(D.logos.nv, 0.44, 0.11); pl.position.set(0, 0.115, 0.69); g.add(pl);
      for (const [lg, px] of [[D.logos.qc, -0.62], [D.logos.arm, 0.62]]) { const p2 = logoPlate(lg, 0.44, 0.11); p2.position.set(px, 0.115, 0.69); g.add(p2); }
    }
    this.T = { start: 190.0, retire: cue('b09', 'Retirement'), pension: cue('b09', 'pension'), own: cue('b09', 'own'), saw: cue('b09', 'saw'),
      shrink: cue('b09', 'shrink'), paper: cue('b09', 'paper,'), loss: cue('b09', 'loss'), only: cue('b09', 'only'), loss2: cue('b09', 'loss', 2),
      sells: cue('b09', 'sells'), paid: cue('b09', 'paid.'), end: 206.6 };
  }
  update(t) {
    const T = this.T;
    camKeys(this.cam, [
      [T.start, [0, 4.6, 4.4], [0, 0.2, 0], 34],
      [T.own, [-1.6, 2.6, 3.4], [-0.4, 0.3, 0], 34],
      [T.paper, [1.6, 2.2, 3.0], [0.6, 0.3, 0], 34],
      [T.end, [2.4, 2.4, 2.6], [1.0, 0.25, 0], 34],
    ], t);
    for (const q of this.cols) {
      const k = smoother(clamp((t - T.shrink + 0.2 - q.d * 0.4) / 0.9));
      q.c.scale.y = 1 - 0.06 * k;
      tint(q.own, 0.45 * k * (1 - 0.6 * clamp((t - T.loss - 0.5) / 1.5)));
    }
  }
  overlay(g, t) {
    const T = this.T, o = 1 - clamp((t - T.only + 0.2) / 0.4);
    if (t > T.saw - 0.2 && o > 0) {
      bigText(g, 'SAVINGS SHRANK', 960, 190, { size: 120, p: clamp((t - T.saw + 0.1) / 0.45), a: o });
      bigText(g, [['ON PAPER', HL]], 960, 340, { size: 140, p: clamp((t - T.paper + 0.3) / 0.45), a: o });
    }
    if (t > T.only - 0.2) {
      bigText(g, 'BOUGHT $200.13', 110, 180, { size: 100, p: clamp((t - T.only + 0.1) / 0.45), align: 'left' });
      bigText(g, 'SOLD $181.60', 110, 300, { size: 100, p: clamp((t - T.loss2 + 0.1) / 0.45), align: 'left' });
      bigText(g, [['= -$18.53 IN CASH', RED]], 110, 440, { size: 110, p: clamp((t - T.sells + 0.1) / 0.45), align: 'left' });
    }
  }
}
