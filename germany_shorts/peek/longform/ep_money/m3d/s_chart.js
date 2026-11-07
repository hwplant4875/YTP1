// Real Nvidia (NVDA) daily candles, Sept 4 - Nov 6 2026 (Yahoo Finance), built as a 3D chart that stands
// in the paper studio: price candles on top, volume bars below, a cream wall with the price grid behind.
// Candle colour = change vs the previous close (green up, red down), like most retail apps.
// mode 'drop'   (1:16-1:30): Wed $200.13 marked, then Thursday's candle is drawn live from the real
//                5-minute bars down to $181.60 (-9.3%), the worst day in the window.
// mode 'volume' (2:15-2:28): the volume bars: 306,127,800 shares traded on Nov 5, out of ~24.2 billion.
// mode 'next'   (3:26-3:33): Nov 6 appears: back up 2.8% from Thursday's close.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, easeOut, HL } from '../js/iso.js';
import { W, H, RED, GREEN, RED3, GREEN3, studio, camKeys, newCam, card, toScreen, logoPlate } from './common.js';

const N = 45, DXC = 0.13, Y0 = 0.95, P0 = 176, KY = 0.04;
const py = (p) => Y0 + (p - P0) * KY;
const fmt = (p) => '$' + p.toFixed(2);

export class ChartScene {
  constructor(mode) { this.mode = mode; }
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 7, sunPos: [-4, 8, 7], near: 12, far: 30 });
    this.cam = newCam();
    const rows = this.rows = D.data.NVDA_d.slice(-N);
    this.intra = D.data.NVDA_i.filter(r => r[0].startsWith('2026-11-05'));
    const xs = (i) => (i - (N - 1)) * DXC - DXC;      // Nov 6 at x = 0, Nov 5 at -0.13, Nov 4 at -0.26
    this.xs = xs;
    const up = new THREE.MeshStandardMaterial({ color: GREEN3, roughness: 0.55 });
    const dn = new THREE.MeshStandardMaterial({ color: RED3, roughness: 0.55 });
    const volM = (c) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.8, transparent: true, opacity: 0.55 });
    const vUp = volM(GREEN3), vDn = volM(RED3);
    this.c = [];
    for (let i = 0; i < N; i++) {
      const [d, o, h, l, cl, v] = rows[i], prev = i ? rows[i - 1][4] : o, isUp = cl >= prev;
      const g = new THREE.Group(); g.position.x = xs(i); s.add(g);
      const mat = (isUp ? up : dn).clone();
      const body = new THREE.Mesh(new THREE.BoxGeometry(0.085, 1, 0.085), mat); body.castShadow = true; g.add(body);
      const wick = new THREE.Mesh(new THREE.BoxGeometry(0.014, 1, 0.014), mat); wick.castShadow = true; g.add(wick);
      const vol = new THREE.Mesh(new THREE.BoxGeometry(0.085, 1, 0.085), isUp ? vUp : vDn); vol.castShadow = true; g.add(vol);
      const C = { d, o, h, l, cl, v, g, body, wick, vol, mat };
      this.c.push(C); this.pose(C, o, h, l, cl, v);
    }
    // back wall with the price grid; price labels on its right edge
    const wall = new THREE.Mesh(new THREE.BoxGeometry(7.2, 4.2, 0.05), new THREE.MeshStandardMaterial({ color: 0xF7F1E4, roughness: 0.95 }));
    wall.position.set(-2.6, 2.1, -0.35); wall.receiveShadow = false; s.add(wall);
    const lineM = new THREE.MeshStandardMaterial({ color: 0xD8CCB4, roughness: 1 });
    for (let p = 180; p <= 240; p += 10) {
      const ln = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.008, 0.01), lineM); ln.position.set(-2.75, py(p), -0.32); s.add(ln);
      const lb = card([{ text: '$' + p, font: '600 150px Jost', y: 175, color: '#7A6F63', align: 'left', x: 20 }], { w: 512, h: 256, sx: 0.36 });
      lb.position.set(0.55, py(p) + 0.03, -0.31); s.add(lb);
    }
    // month marks on the floor, and the ticker plate (Nvidia logo) at the chart's left end
    for (let i = 0; i < N; i++) {
      const d = rows[i][0], prev = i ? rows[i - 1][0] : '';
      if (d.slice(5, 7) !== prev.slice(5, 7)) {
        const mo = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][+d.slice(5, 7)];
        const lb = card([{ text: mo, font: '600 170px Jost', y: 190, color: '#6E6458' }], { w: 512, h: 256, sx: 0.5 });
        lb.rotation.x = -Math.PI / 2; lb.position.set(xs(i) + 0.1, 0.004, 0.42); s.add(lb);
      }
    }
    const plate = logoPlate(D.logos.nv, 1.1, 0.27, 0.06); plate.position.set(-5.95, 3.65, -0.3); s.add(plate);
    // the dashed Wednesday-close line
    const dash = this.dash = new THREE.Group(); s.add(dash);
    const dm = new THREE.MeshBasicMaterial({ color: 0x2B2533, transparent: true, opacity: 0.8 });
    for (let k = 0; k < 40; k++) { const q = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.012, 0.012), dm); q.position.set(-5.2 + k * 0.135, 0, 0); dash.add(q); }
    dash.position.set(0, py(200.13), 0.06); dash.visible = false;
    this.T = {
      wed: cue('b04', 'Wednesday,'), two: cue('b04', 'two'), thu: cue('b04', "Thursday's"), close: cue('b04', 'close'), e82: cue('b04', 'eighty-two,'),
      nine: cue('b04', 'nine'), biggest: cue('b04', 'biggest'), april: cue('b04', 'April'), b4end: 89.9,
      v0: cue('b06', 'And'), three: cue('b06', 'three'), changed: cue('b06', 'changed'), tf: cue('b06', 'twenty-four'), because: cue('b06', 'because'),
      prices: cue('b09', 'Prices'), next: cue('b09', 'next'), threeP: cue('b09', 'three'), endN: 212.9,
    };
  }
  pose(C, o, h, l, cl, v) {
    const top = Math.max(o, cl), bot = Math.min(o, cl), bh = Math.max(0.006, (top - bot) * KY);
    C.body.scale.y = bh; C.body.position.y = py(bot) + bh / 2;
    const wh = Math.max(0.006, (h - l) * KY); C.wick.scale.y = wh; C.wick.position.y = py(l) + wh / 2;
    const vh = Math.max(0.004, v / 306127800 * 0.78); C.vol.scale.y = vh; C.vol.position.y = vh / 2;
  }

  update(t) {
    const T = this.T, m = this.mode, c5 = this.c[N - 2], c6 = this.c[N - 1];
    if (m === 'drop') camKeys(this.cam, [
      [75.5, [-5.2, 2.7, 5.6], [-2.6, 2.1, 0], 34],
      [T.wed + 1.2, [-1.2, 2.9, 3.7], [-0.6, 2.3, 0], 32],
      [T.thu, [0.0, 2.5, 3.3], [-0.4, 1.9, 0], 32],
      [T.nine, [0.5, 1.9, 2.8], [-0.3, 1.4, 0], 32],
      [T.biggest + 0.3, [-1.6, 2.6, 5.6], [-2.4, 2.0, 0], 34],
      [T.b4end, [-2.0, 2.7, 6.0], [-2.6, 2.0, 0], 34],
    ], t);
    else if (m === 'volume') camKeys(this.cam, [
      [T.v0 - 0.5, [-4.6, 1.5, 4.8], [-2.4, 0.9, 0], 34],
      [T.three, [0.2, 0.9, 2.6], [-0.25, 0.5, 0], 32],
      [T.tf, [0.6, 1.5, 3.2], [-0.4, 0.8, 0], 34],
      [T.because + 0.6, [0.8, 1.7, 3.4], [-0.4, 0.9, 0], 34],
    ], t);
    else camKeys(this.cam, [
      [T.prices - 0.6, [-1.6, 2.2, 3.4], [-0.5, 1.4, 0], 32],
      [T.next, [0.6, 1.9, 2.6], [-0.15, 1.5, 0], 32],
      [T.endN, [1.0, 2.0, 2.4], [-0.1, 1.6, 0], 32],
    ], t);

    // Thursday's candle: in 'drop' it is drawn live from the real 5-minute bars
    if (m === 'drop') {
      const k = clamp((t - T.thu + 0.2) / (T.e82 + 0.4 - T.thu + 0.2));
      const n = Math.floor(k * (this.intra.length - 1));
      if (t < T.thu - 0.2) { c5.g.visible = false; this.live = 200.13; }
      else {
        c5.g.visible = true;
        let hi = this.intra[0][2], lo = this.intra[0][3];
        for (let i = 0; i <= n; i++) { hi = Math.max(hi, this.intra[i][2]); lo = Math.min(lo, this.intra[i][3]); }
        const cl = k >= 1 ? 181.60 : this.intra[n][4], vol = 306127800 * (n + 1) / this.intra.length;
        this.pose(c5, 196.07, k >= 1 ? 196.25 : hi, k >= 1 ? 181.46 : lo, cl, vol);
        this.live = cl;
      }
    } else c5.g.visible = true;
    // Nov 6 exists only in 'next', and appears at "next"
    if (m === 'next') {
      const k = easeOut(clamp((t - T.next + 0.1) / 0.9));
      c6.g.visible = k > 0;
      const cl = 181.60 + (186.64 - 181.60) * k, o = 191.10;
      this.pose(c6, o, 181.60 + (194.9 - 181.60) * k, Math.min(185.22, cl), cl, 179722400 * k);
      c6.mat.color.set(GREEN3);
    } else c6.g.visible = false;
    // highlight: emissive glow on the candle being talked about
    for (const C of this.c) C.mat.emissive.setRGB(0, 0, 0);
    const glow = (C, a) => C.mat.emissive.copy(C.mat.color).multiplyScalar(0.35 * a);
    if (m === 'drop') { glow(this.c[N - 3], clamp((t - T.wed) / 0.3) * (1 - clamp((t - T.thu) / 0.4))); glow(c5, clamp((t - T.thu) / 0.3)); }
    if (m === 'volume') glow(c5, clamp((t - T.three + 0.3) / 0.4));
    if (m === 'next') glow(c6, clamp((t - T.next) / 0.4));
    this.dash.visible = (m === 'drop' && t > T.wed + 0.1) || m === 'next';
    const dp = m === 'drop' ? easeOut(clamp((t - T.wed - 0.1) / 0.6)) : 1;
    this.dash.scale.x = dp; this.dash.position.x = 0.4 * (1 - dp);
    if (m === 'next') this.dash.position.y = py(181.60);
  }

  label(g, txt, sub, v, color, a, side = 1) {
    if (a <= 0) return;
    const [x, y] = toScreen(this.cam, v);
    g.save(); g.globalAlpha = a; g.textBaseline = 'alphabetic';
    g.font = '600 64px Jost'; g.textAlign = side > 0 ? 'left' : 'right';
    const X = x + side * 34;
    g.lineWidth = 10; g.strokeStyle = 'rgba(242,234,219,0.95)'; g.lineJoin = 'round';
    g.strokeText(txt, X, y + 20); g.fillStyle = color; g.fillText(txt, X, y + 20);
    g.font = '600 34px Jost'; g.letterSpacing = '6px';
    g.strokeText(sub, X, y - 40); g.fillStyle = COL.ink; g.fillText(sub, X, y - 40);
    g.letterSpacing = '0px';
    g.beginPath(); g.arc(x, y, 9, 0, Math.PI * 2); g.fillStyle = color; g.fill(); g.lineWidth = 3; g.strokeStyle = '#fff'; g.stroke();
    g.restore();
  }

  overlay(g, t) {
    const T = this.T, m = this.mode, x5 = this.xs(N - 2), x4 = this.xs(N - 3), x6 = this.xs(N - 1);
    if (m === 'drop') {
      const p = this.live ?? 200.13;
      bigText(g, 'NVDA', 110, 175, { size: 120, p: clamp((t - 75.6) / 0.45), align: 'left' });
      const chg = (p / 200.13 - 1) * 100;
      bigText(g, fmt(p), 470, 175, { size: 120, p: clamp((t - T.two + 0.2) / 0.45), align: 'left' });
      this.label(g, '$200.13', 'WED CLOSE', new THREE.Vector3(x4, py(200.13), 0.06), COL.ink, clamp((t - T.wed - 0.2) / 0.4) * (1 - clamp((t - T.biggest) / 0.4)), -1);
      this.label(g, '$181.60', 'THU CLOSE', new THREE.Vector3(x5, py(181.60), 0.06), '#C8503E', clamp((t - T.e82 - 0.1) / 0.4) * (1 - clamp((t - T.biggest) / 0.4)), 1);
      if (t > T.thu) bigText(g, [[chg.toFixed(1) + '%', RED]], 1060, 175, { size: 120, p: clamp((t - T.thu) / 0.3), a: 1 - clamp((t - T.nine + 0.1) / 0.2), align: 'left' });
      if (t > T.nine - 0.2) bigText(g, [['-9.3%', RED]], 1060, 175, { size: 150, p: clamp((t - T.nine + 0.1) / 0.45), align: 'left' });
      if (t > T.biggest - 0.2) {
        bigText(g, 'WORST DAY SINCE', W - 110, 880, { size: 100, p: clamp((t - T.biggest + 0.1) / 0.45), align: 'right' });
        bigText(g, [['APRIL 2025', HL]], W - 110, 1000, { size: 110, p: clamp((t - T.april + 0.1) / 0.45), align: 'right' });
      }
    } else if (m === 'volume') {
      this.label(g, '306,127,800', 'SHARES TRADED NOV 5', new THREE.Vector3(x5, 0.78, 0.06), '#C8503E', clamp((t - T.three - 0.3) / 0.4), -1);
      if (t > T.changed - 0.3) bigText(g, [['306 MILLION', HL], [' TRADED', '#FFFFFF']], 110, 190, { size: 110, p: clamp((t - T.changed + 0.2) / 0.45), align: 'left' });
      if (t > T.tf - 0.3) bigText(g, 'OUT OF 24.2 BILLION', 110, 320, { size: 110, p: clamp((t - T.tf + 0.1) / 0.45), align: 'left' });
    } else {
      this.label(g, '$181.60', 'THU CLOSE', new THREE.Vector3(x5, py(181.60), 0.06), COL.ink, clamp((t - T.prices) / 0.4), -1);
      this.label(g, '$186.64', 'FRI CLOSE', new THREE.Vector3(x6, py(186.64), 0.06), '#1E8E68', clamp((t - T.next - 0.6) / 0.4), 1);
      if (t > T.threeP - 0.4) bigText(g, [['+2.8%', GREEN]], 110, 200, { size: 170, p: clamp((t - T.threeP + 0.3) / 0.45), align: 'left' });
      if (t > T.next - 0.3) bigText(g, 'THE NEXT DAY', 110, 360, { size: 100, p: clamp((t - T.next + 0.2) / 0.45), align: 'left' });
    }
  }
}
