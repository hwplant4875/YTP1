// The 3D half of the episode (0:31.85 to the end) on one clock: scenes in order, joined by crossfades.
// Each scene owns a THREE.Scene + camera; update(t) poses it, overlay(g, t) draws big key text in 2D.
import * as THREE from 'three';
import { W, H, img, canvas } from './common.js';
import { smoother, clamp } from '../js/iso.js';

export class Director {
  constructor(gl, ov) { this.gl = gl; this.ov = ov; this.g = ov.getContext('2d'); }
  async init(list) {
    const r = this.r = new THREE.WebGLRenderer({ canvas: this.gl, antialias: true, preserveDrawingBuffer: true });
    r.setSize(W, H, false); r.setPixelRatio(1);
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
    r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
    this.logos = { nv: await img('../assets/logos/nvidia.svg'), qc: await img('../assets/logos/qualcomm.svg'), arm: await img('../assets/logos/arm.png') };
    this.data = await (await fetch('../data/prices.json')).json();
    this.list = list;
    for (const e of list) await e[2].init(this);
    const rt = () => new THREE.WebGLRenderTarget(W, H, { samples: 4, type: THREE.HalfFloatType });
    this.ra = rt(); this.rb = rt();
    this.fade = new THREE.ShaderMaterial({
      uniforms: { a: { value: null }, b: { value: null }, p: { value: 0 } },
      vertexShader: 'varying vec2 v; void main(){ v = uv; gl_Position = vec4(position.xy, 0., 1.); }',
      // tone-map and encode each scene first, then mix in display space (a linear-light mix washes out)
      fragmentShader: 'uniform sampler2D a, b; uniform float p; varying vec2 v;\nvec4 enc(vec4 c){ c.rgb = toneMapping(c.rgb); return linearToOutputTexel(c); }\nvoid main(){ gl_FragColor = mix(enc(texture2D(a, v)), enc(texture2D(b, v)), p); }',
      depthTest: false, depthWrite: false,
    });
    this.fs = new THREE.Scene(); this.fs.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.fade));
    this.fcam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.oa = canvas(W, H); this.ob = canvas(W, H);
  }
  render(t) {
    const act = this.list.filter(e => t >= e[0] && t < e[1]);
    const g = this.g; g.clearRect(0, 0, W, H);
    if (!act.length) return;
    const A = act[0][2];
    A.update(t);
    if (act.length === 1) {
      this.r.setRenderTarget(null); this.r.render(A.s, A.cam);
      A.overlay(g, t);
      return;
    }
    const B = act[1][2], p = smoother(clamp((t - act[1][0]) / Math.max(1e-6, Math.min(act[0][1], act[1][1]) - act[1][0])));
    B.update(t);
    this.r.setRenderTarget(this.ra); this.r.render(A.s, A.cam);
    this.r.setRenderTarget(this.rb); this.r.render(B.s, B.cam);
    this.r.setRenderTarget(null);
    this.fade.uniforms.a.value = this.ra.texture; this.fade.uniforms.b.value = this.rb.texture; this.fade.uniforms.p.value = p;
    this.r.render(this.fs, this.fcam);
    for (const [S, o, al] of [[A, this.oa, 1 - p], [B, this.ob, p]]) {
      const c = o.getContext('2d'); c.clearRect(0, 0, W, H); S.overlay(c, t);
      g.save(); g.globalAlpha = al; g.drawImage(o, 0, 0); g.restore();
    }
  }
}
