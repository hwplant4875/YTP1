// Market value = latest price x every share. One cube = 100 million Nvidia shares; 242 cubes = ~24.2 billion.
// mode 'value' (1:45-2:15): Nvidia's own cash sits untouched (cash lost: $0); then one share with its tag,
//               the block of 242 cubes builds, the tag drops $18.53 and the whole block reprices at once.
// mode 'trade' (2:27-2:43): only ~1 share in 80 traded (3 cubes lift out), the other 79 never moved,
//               yet a repricing wave sweeps every cube to the new last price, $181.60.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { COL } from '../js/objects.js';
import { bigText, clamp, easeOut, backOut, smoother, mulberry32, HL } from '../js/iso.js';
import { W, H, RED, studio, camKeys, newCam, cashMats, stackGeo, logoPlate, tint, canvas, tex, toScreen } from './common.js';

const NX = 11, NY = 2, NZ = 11, S = 0.14, G = 0.016;    // 242 cubes

function cubeTex(logo) {
  const cv = canvas(512, 512), g = cv.getContext('2d');
  g.fillStyle = '#FBF6EA'; g.fillRect(0, 0, 512, 512);
  g.strokeStyle = 'rgba(43,37,51,0.25)'; g.lineWidth = 10; g.strokeRect(5, 5, 502, 502);
  const lw = 400, lh = lw * logo.height / logo.width; g.drawImage(logo, 56, 256 - lh / 2, lw, lh);
  return cv;
}
function tagCanvas(price, sub, color) {
  const cv = canvas(1024, 440), g = cv.getContext('2d');
  g.fillStyle = COL.tag;
  g.beginPath(); g.moveTo(150, 16); g.lineTo(1000, 16); g.lineTo(1000, 424); g.lineTo(150, 424); g.lineTo(16, 220); g.closePath(); g.fill();
  g.lineWidth = 6; g.strokeStyle = 'rgba(43,37,51,0.35)'; g.stroke();
  g.beginPath(); g.arc(120, 220, 24, 0, Math.PI * 2); g.fillStyle = '#E8DCC2'; g.fill(); g.lineWidth = 8; g.strokeStyle = '#C9A55A'; g.stroke();
  g.fillStyle = color; g.textAlign = 'center'; g.font = '600 200px Jost'; g.fillText(price, 590, 270);
  g.font = '600 52px Jost'; g.letterSpacing = '10px'; g.fillStyle = COL.ink; g.fillText(sub, 590, 370); g.letterSpacing = '0px';
  return cv;
}

export class ValueScene {
  constructor(mode) { this.mode = mode; }
  async init(D) {
    const s = this.s = new THREE.Scene();
    studio(s, { shadow: 4, sunPos: [-4, 8, 6] });
    this.cam = newCam();
    const face = new THREE.MeshStandardMaterial({ map: tex(cubeTex(D.logos.nv)), roughness: 0.7 });
    const side = new THREE.MeshStandardMaterial({ color: 0xF3ECDD, roughness: 0.8 });
    this.mk = () => { const f = face.clone(), sd = side.clone(); const m = new THREE.Mesh(new THREE.BoxGeometry(S, S, S), [sd, sd, f, sd, f, sd]); m.castShadow = m.receiveShadow = true; m.userData.m = [f, sd]; return m; };
    // the block of 242 cubes at x = +0.9
    this.cubes = [];
    const r = mulberry32(80);
    for (let j = 0; j < NY; j++) for (let k = 0; k < NZ; k++) for (let i = 0; i < NX; i++) {
      const c = this.mk(); s.add(c);
      const home = new THREE.Vector3(0.9 + (i - (NX - 1) / 2) * (S + G), S / 2 + j * (S + G), (k - (NZ - 1) / 2) * (S + G));
      this.cubes.push({ c, home, d: (i + k) / (NX + NZ) + r() * 0.08, ord: j * NX * NZ + k * NX + i, r: r() });
    }
    // the 3 traded cubes (1 in 80): top layer, spread out
    this.traded = [NX * NZ + 2 * NX + 3, NX * NZ + 5 * NX + 7, NX * NZ + 8 * NX + 4].map(i => this.cubes[i]);
    // one share on its own, with a tag
    this.one = this.mk(); this.one.scale.setScalar(1.6); s.add(this.one);
    const tagM = (cv) => new THREE.MeshStandardMaterial({ map: tex(cv), transparent: true, roughness: 0.75, side: THREE.DoubleSide });
    this.tagA = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.266), tagM(tagCanvas('$200.13', 'WED CLOSE', COL.ink)));
    this.tagB = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.266), tagM(tagCanvas('$181.60', 'THU CLOSE', '#C8503E')));
    for (const tg of [this.tagA, this.tagB]) { tg.castShadow = true; s.add(tg); }
    // Nvidia's own cash pile (mode 'value' opening): a broad stack of bundles behind its logo plate
    if (this.mode === 'value') {
      const pile = this.pile = new THREE.Group(); s.add(pile);
      const pm = cashMats();
      for (let i = 0; i < 5; i++) for (let k = 0; k < 3; k++) {
        const h = 0.55 + ((i * 7 + k * 3) % 5) * 0.06;
        const b = new THREE.Mesh(stackGeo(h, 2, 4), pm); b.position.set((i - 2) * 0.33, 0, (k - 1) * 0.29); b.castShadow = b.receiveShadow = true; pile.add(b);
      }
      const pl = logoPlate(D.logos.nv, 1.1, 0.27); pl.position.set(0, 0.135, 0.62); pile.add(pl);
    }
    const c = (b, w, n) => cue(b, w, n);
    this.T = this.mode === 'value' ? {
      start: 105.5, strange: c('b05', 'strange'), lose: c('b05', 'lose'), cash: c('b05', 'cash'), see: c('b05', 'see'), value: c('b05', 'value'),
      mult: c('b05', 'multiplication,'), latest: c('b05', 'latest'), times: c('b05', 'times'), every: c('b05', 'every'), has: c('b05', 'has'),
      tf: c('b05', 'twenty-four'), sh: c('b05', 'shares,'), drops: c('b05', 'drops'), e1: c('b05', 'eighteen'), whole: c('b05', 'whole'), drops2: c('b05', 'drops', 2),
      e2: c('b05', 'eighteen', 2), times2: c('b05', 'times', 2), tf2: c('b05', 'twenty-four', 2), all: c('b05', 'all'), end: 135.2,
    } : {
      start: 147.3, only: c('b06', 'only'), one: c('b06', 'one'), eighty: c('b06', 'eighty.'), other: c('b06', 'other'), never: c('b06', 'never'),
      yet: c('b06', 'yet'), rep: c('b06', 'repriced'), lower: c('b06', 'lower'), because: c('b06', 'because', 2), buyer: c('b06', 'buyer'),
      becomes: c('b06', 'becomes'), every: c('b06', 'every', 2), end: 163.2,
    };
  }

  update(t) {
    const T = this.T, v = this.mode === 'value';
    if (v) camKeys(this.cam, [
      [T.start, [-0.6, 1.3, 3.0], [-1.6, 0.4, 0], 32],
      [T.see, [0.6, 1.4, 2.8], [-1.4, 0.4, 0], 32],
      [T.latest, [-0.9, 0.95, 2.0], [-0.75, 0.35, 0], 34],
      [T.has, [-0.6, 1.2, 2.4], [-0.5, 0.3, 0], 34],
      [T.tf + 0.5, [0.2, 2.2, 4.2], [0.1, 0.3, 0], 36],
      [T.drops2, [1.2, 2.4, 4.0], [0.3, 0.2, 0], 36],
      [T.end, [2.2, 2.9, 3.6], [0.5, 0.15, 0], 36],
    ], t);
    else camKeys(this.cam, [
      [T.start, [-1.6, 2.6, 3.6], [0.9, 0.2, 0], 34],
      [T.never, [-0.6, 1.8, 2.6], [0.9, 0.35, 0], 34],
      [T.rep + 0.4, [2.6, 2.3, 3.0], [0.9, 0.3, 0], 34],
      [T.end, [3.2, 2.6, 2.4], [0.9, 0.3, 0], 34],
    ], t);
    // Nvidia's cash pile: stays whole, then slides off when the multiplication starts
    if (this.pile) { const go = smoother(clamp((t - T.value) / 1.1)); this.pile.position.set(-1.6 - 2.4 * go, 0, -0.2 * go); this.pile.visible = go < 1; }
    // one share (value: from "latest"; trade: hidden)
    const onA = v ? backOut(clamp((t - T.mult + 0.3) / 0.5)) : 0;
    this.one.visible = onA > 0.001;
    this.one.position.set(-1.1, 0.112 + (1 - onA) * 0.6, 0.2); this.one.rotation.y = 0.35;
    // tags: value -> above the single share; trade -> above the block
    const flipT = v ? T.drops : T.rep;
    const tagOn = v ? clamp((t - T.mult) / 0.4) : clamp((t - T.yet) / 0.4);
    const fl = smoother(clamp((t - flipT) / 0.5));
    const tp = v ? new THREE.Vector3(-1.1, 0.62, 0.2) : new THREE.Vector3(0.9, 0.62, -1.15);
    for (const [tg, a] of [[this.tagA, 1 - fl], [this.tagB, fl]]) {
      tg.visible = tagOn > 0 && a > 0.01; tg.material.opacity = tagOn * a;
      tg.position.copy(tp).add(new THREE.Vector3(0, 0.04 * Math.sin(t * 1.3), 0)); tg.rotation.set(-0.15, (v ? 0.3 : -0.25) + (a < 1 ? (1 - a) * 0.0 : 0), 0);
      tg.scale.setScalar(v ? 1 : 1.35);
    }
    // the block
    const build0 = v ? T.tf - 0.2 : -1e9, build1 = v ? T.sh + 0.3 : -1e9;
    const lift = v ? 0 : easeOut(clamp((t - T.one + 0.2) / 0.8));
    const settle = v ? 0 : smoother(clamp((t - T.becomes) / 1.0));
    for (const q of this.cubes) {
      const a = v ? backOut(clamp((t - (build0 + (build1 - build0) * q.ord / 242)) / 0.35)) : 1;
      q.c.visible = a > 0.001;
      q.c.scale.setScalar(Math.max(0.001, a));
      q.c.position.copy(q.home);
      // repricing: value -> at the 2nd "drops" a wave across the block; trade -> at "repriced"
      const tw = v ? T.drops2 : T.rep;
      const hot = clamp((t - tw - q.d * 0.8) / 0.15) * (v ? 1 : 1);
      const isT = this.traded.includes(q);
      if (isT && !v) {
        q.c.position.y += 0.5 * lift * (1 - settle); q.c.position.z += 0.0;
        q.c.rotation.y = 0.6 * lift * (1 - settle);
      } else q.c.rotation.y = 0;
      // focus + context in 'trade': while the 3 traded cubes are named, the 239 others pale out
      const pale = v ? 0 : clamp((t - T.one + 0.2) / 0.5) * (1 - clamp((t - T.yet) / 0.5));
      const [f, sd] = q.c.userData.m;
      for (const m of [f, sd]) {
        m.color.setRGB(1, 1 - 0.45 * hot, 1 - 0.55 * hot);
        if (pale > 0 && !isT) m.color.lerp(new THREE.Color(0xF2EADB), 0.6 * pale);
        m.transparent = false;
      }
    }
    if (v) { const hot1 = clamp((t - T.drops - 0.1) / 0.15); for (const m of this.one.userData.m) m.color.setRGB(1, 1 - 0.45 * hot1, 1 - 0.55 * hot1); }
  }

  overlay(g, t) {
    const T = this.T;
    if (this.mode === 'value') {
      const o1 = 1 - clamp((t - T.value) / 0.4);
      if (t > T.lose - 0.2 && o1 > 0) {
        bigText(g, "NVIDIA'S CASH LOST", 960, 200, { size: 100, p: clamp((t - T.lose + 0.1) / 0.45), a: o1 });
        bigText(g, [['$0', HL]], 960, 380, { size: 200, p: clamp((t - T.cash + 0.1) / 0.45), a: o1 });
      }
      const o2 = 1 - clamp((t - T.drops + 0.3) / 0.4);
      if (t > T.latest - 0.2 && o2 > 0) {
        bigText(g, [['PRICE', HL], [' × ', '#FFFFFF'], ['EVERY SHARE', HL]], 960, 180, { size: 110, p: clamp((t - T.latest + 0.1) / 0.45), a: o2 });
        if (t > T.tf - 0.2) bigText(g, '= MARKET VALUE', 960, 310, { size: 100, p: clamp((t - T.tf + 0.1) / 0.45), a: o2 });
      }
      if (t > T.has) {
        const a = clamp((t - T.tf - 0.3) / 0.4);
        const [x, y] = toScreen(this.cam, new THREE.Vector3(0.9, 0.36, 0.8));
        g.save(); g.globalAlpha = a * (1 - clamp((t - T.drops + 0.3) / 0.4)); g.font = '600 50px Jost'; g.letterSpacing = '6px'; g.textAlign = 'center';
        g.lineWidth = 9; g.strokeStyle = 'rgba(242,234,219,0.95)'; g.strokeText('24.2 BILLION SHARES', x, y + 120); g.fillStyle = COL.ink; g.fillText('24.2 BILLION SHARES', x, y + 120);
        g.font = '500 36px Jost'; g.strokeText('1 CUBE = 100 MILLION SHARES', x, y + 172); g.fillText('1 CUBE = 100 MILLION SHARES', x, y + 172); g.restore();
      }
      if (t > T.e1 - 0.2) bigText(g, [['-$18.53', RED], [' PER SHARE', '#FFFFFF']], 960, 180, { size: 110, p: clamp((t - T.e1 + 0.1) / 0.45), a: 1 - clamp((t - T.e2 + 0.2) / 0.3) });
      if (t > T.e2 - 0.2) {
        bigText(g, [['$18.53', RED], [' × 24.2B', '#FFFFFF']], 960, 180, { size: 120, p: clamp((t - T.e2 + 0.1) / 0.45) });
        bigText(g, [['= -$448 BILLION', RED]], 960, 320, { size: 120, p: clamp((t - T.tf2 + 0.3) / 0.45) });
      }
    } else {
      const o = 1 - clamp((t - T.yet) / 0.4);
      if (t > T.one - 0.2 && o > 0) bigText(g, [['1 IN 80', HL], [' TRADED', '#FFFFFF']], 960, 190, { size: 130, p: clamp((t - T.one + 0.1) / 0.45), a: o });
      if (t > T.other - 0.2 && o > 0) bigText(g, '79 NEVER MOVED', 960, 340, { size: 110, p: clamp((t - T.never + 0.1) / 0.45), a: o });
      if (t > T.rep - 0.3) bigText(g, [['ALL REPRICED', RED]], 960, 190, { size: 130, p: clamp((t - T.rep + 0.1) / 0.45), a: 1 - clamp((t - T.because + 0.2) / 0.4) });
      if (t > T.buyer - 0.3) {
        bigText(g, 'LAST TRADE PRICE', 960, 190, { size: 110, p: clamp((t - T.buyer + 0.1) / 0.45) });
        bigText(g, [['= EVERY SHARE', HL]], 960, 320, { size: 110, p: clamp((t - T.becomes + 0.1) / 0.45) });
      }
    }
  }
}
