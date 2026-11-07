// "Let's peek inside ... Nvidia": an AI accelerator package in the paper studio, Nvidia logo on its lid.
// The lid lifts off (exploded view) to show the GPU die between its HBM memory stacks on the substrate.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { clamp, easeOut, smoother, mulberry32 } from '../js/iso.js';
import { studio, camKeys, newCam, canvas, tex, toScreen } from './common.js';

function lidTex(logo) {
  const cv = canvas(2048, 1536), g = cv.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 2048, 1536);
  gr.addColorStop(0, '#E4E6E8'); gr.addColorStop(0.5, '#C9CDD2'); gr.addColorStop(1, '#DADDE0');
  g.fillStyle = gr; g.fillRect(0, 0, 2048, 1536);
  const r = mulberry32(7);
  g.globalAlpha = 0.05; for (let i = 0; i < 1400; i++) { g.fillStyle = r() < 0.5 ? '#fff' : '#555'; g.fillRect(0, r() * 1536, 2048, 1); } g.globalAlpha = 1;
  const lw = 1300, lh = lw * logo.height / logo.width;
  g.drawImage(logo, (2048 - lw) / 2, (1536 - lh) / 2 - 60, lw, lh);
  g.font = '500 64px Jost'; g.fillStyle = '#5A5F66'; g.textAlign = 'center'; g.letterSpacing = '10px';
  g.fillText('AI ACCELERATOR', 1024, 1536 / 2 + lh / 2 + 80); g.letterSpacing = '0px';
  return cv;
}
function dieTex() {
  const cv = canvas(1600, 1200), g = cv.getContext('2d');
  g.fillStyle = '#2A2440'; g.fillRect(0, 0, 1600, 1200);
  const r = mulberry32(11);
  for (let i = 0; i < 12; i++) for (let j = 0; j < 8; j++) {
    const x = 40 + i * 128, y = 50 + j * 140;
    g.fillStyle = ['#463C70', '#3E5A78', '#5A4A86'][Math.floor(r() * 3)]; g.fillRect(x, y, 112, 122);
    g.fillStyle = 'rgba(160,200,255,0.18)'; g.fillRect(x + 8, y + 8, 96, 40);
    g.fillStyle = 'rgba(255,210,120,0.25)'; g.fillRect(x + 8, y + 60, 44, 54);
  }
  g.strokeStyle = 'rgba(217,165,58,0.55)'; g.lineWidth = 6; g.strokeRect(20, 30, 1560, 1140);
  return cv;
}
function pcbTex() {
  const cv = canvas(2048, 2048), g = cv.getContext('2d');
  g.fillStyle = '#2F5A3F'; g.fillRect(0, 0, 2048, 2048);
  const r = mulberry32(3);
  g.strokeStyle = 'rgba(160,200,140,0.25)'; g.lineWidth = 4;
  for (let i = 0; i < 220; i++) { const x = r() * 2048, y = r() * 2048; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 300, y); g.lineTo(x + (r() - 0.5) * 300, y + (r() - 0.5) * 300); g.stroke(); }
  g.fillStyle = '#D9A53A';
  for (let i = 0; i < 64; i++) { g.fillRect(40 + i * 31, 20, 18, 36); g.fillRect(40 + i * 31, 1992, 18, 36); g.fillRect(20, 40 + i * 31, 36, 18); g.fillRect(1992, 40 + i * 31, 36, 18); }
  return cv;
}

export class ChipScene {
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 3, sunPos: [-3, 7, 4], near: 8, far: 22 });
    this.cam = newCam();
    const std = (o) => new THREE.MeshStandardMaterial(o);
    // substrate
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.08, 2.4), [std({ color: 0x24482F }), std({ color: 0x24482F }), std({ map: tex(pcbTex()), roughness: 0.6 }), std({ color: 0x24482F }), std({ color: 0x24482F }), std({ color: 0x24482F })]);
    pcb.position.y = 0.04; pcb.castShadow = pcb.receiveShadow = true; s.add(pcb);
    // small capacitors around the edge
    const capM = std({ color: 0xC9B48A, roughness: 0.5, metalness: 0.3 }), rr = mulberry32(21);
    for (let i = 0; i < 46; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.025), capM); const a = i / 46 * Math.PI * 2;
      c.position.set(Math.max(-1.08, Math.min(1.08, Math.cos(a) * 1.5)), 0.095, Math.max(-1.08, Math.min(1.08, Math.sin(a) * 1.5))); c.rotation.y = rr() * 3; s.add(c); }
    // interposer + die + 6 HBM stacks
    const inter = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.04, 1.1), std({ color: 0x8A8F96, roughness: 0.4, metalness: 0.5 }));
    inter.position.y = 0.1; inter.castShadow = inter.receiveShadow = true; s.add(inter);
    const die = this.die = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.05, 0.6), [std({ color: 0x2A2440 }), std({ color: 0x2A2440 }), std({ map: tex(dieTex()), roughness: 0.25, metalness: 0.4 }), std({ color: 0x2A2440 }), std({ color: 0x2A2440 }), std({ color: 0x2A2440 })]);
    die.position.y = 0.145; die.castShadow = true; s.add(die);
    this.hbm = [];
    for (const sx of [-1, 1]) for (const k of [-1, 0, 1]) {
      const h = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.08, 0.3), std({ color: 0x3B3F46, roughness: 0.35, metalness: 0.3 }));
      h.position.set(sx * 0.58, 0.16, k * 0.34); h.castShadow = true; s.add(h); this.hbm.push(h);
    }
    // the lid (integrated heat spreader) with the logo
    const lidSide = std({ color: 0xB8BDC3, roughness: 0.35, metalness: 0.7 });
    const lid = this.lid = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.1, 1.28), [lidSide, lidSide, std({ map: tex(lidTex(D.logos.nv)), roughness: 0.35, metalness: 0.55 }), lidSide, lidSide, lidSide]);
    lid.castShadow = true; s.add(lid);
    this.T = { start: 68.0, nv: cue('b04', 'Nvidia,'), chip: cue('b04', 'chip'), proc: cue('b04', 'processors'), ai: cue('b04', 'AI.'), on: cue('b04', 'On') };
  }
  update(t) {
    const T = this.T;
    camKeys(this.cam, [
      [T.start, [0.0, 2.6, 1.6], [0, 0.2, 0], 30],
      [T.nv + 0.3, [1.6, 2.4, 2.6], [0, 0.25, 0], 32],
      [T.proc + 0.4, [2.6, 2.6, 2.3], [0, 0.5, 0], 32],
      [T.on + 0.5, [2.6, 2.6, 1.0], [0, 0.4, 0], 32],
    ], t);
    const up = smoother(clamp((t - T.nv - 0.2) / 1.2));
    this.lid.position.set(0, 0.24 + 1.05 * up, 0); this.lid.rotation.set(-0.12 * up, 0, 0.05 * up);
    const hb = easeOut(clamp((t - T.proc + 0.2) / 0.8));
    this.die.position.y = 0.145 + 0.35 * hb;
    for (const h of this.hbm) h.position.y = 0.16 + 0.22 * hb * (0.8 + 0.1 * Math.sign(h.position.x));
  }
  pin(g, txt, v, a, side) {
    if (a <= 0) return;
    const [x, y] = toScreen(this.cam, v), X = x + side * 160, Y = y - 110;
    g.save(); g.globalAlpha = a; g.strokeStyle = COL.ink; g.lineWidth = 3;
    g.beginPath(); g.moveTo(x, y); g.lineTo(X, Y); g.lineTo(X + side * 30, Y); g.stroke();
    g.beginPath(); g.arc(x, y, 7, 0, Math.PI * 2); g.fillStyle = COL.ink; g.fill();
    g.font = '600 46px Jost'; g.letterSpacing = '6px'; g.textAlign = side > 0 ? 'left' : 'right'; g.textBaseline = 'middle';
    g.lineWidth = 9; g.strokeStyle = 'rgba(242,234,219,0.95)'; g.strokeText(txt, X + side * 44, Y); g.fillStyle = COL.ink; g.fillText(txt, X + side * 44, Y);
    g.restore();
  }
  overlay(g, t) {
    const T = this.T, a = clamp((t - T.proc - 0.4) / 0.4) * (1 - clamp((t - T.on + 0.2) / 0.3));
    this.pin(g, 'GPU DIE', this.die.position.clone().add(new THREE.Vector3(0.1, 0.03, 0.1)), a, -1);
    this.pin(g, 'HBM MEMORY', this.hbm[5].position.clone().add(new THREE.Vector3(0, 0.04, 0.05)), clamp((t - T.proc - 0.7) / 0.4) * (1 - clamp((t - T.on + 0.2) / 0.3)), 1);
  }
}
