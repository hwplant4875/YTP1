// Shared look for every 3D shot: monochrome world, one warm amber light, fog.
export const AMBER = 0xffa64a;

export function canvasTex(THREE, w, h, draw, repeat = [1, 1]) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

// deterministic noise so every render of a shot is identical
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

export function tileTex(THREE, { tile = 32, grout = 3, base = 178, vary = 18, dirt = 0.5, repeat = [8, 2], seed = 3 } = {}) {
  const r = rng(seed);
  return canvasTex(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = 'rgb(60,60,58)'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += tile) for (let x = 0; x < w; x += tile * 2) {
      const v = base - vary / 2 + r() * vary;
      g.fillStyle = `rgb(${v},${v},${v - 4})`;
      g.fillRect(x + grout / 2, y + grout / 2, tile * 2 - grout, tile - grout);
    }
    // grime streaks running down from the ceiling
    for (let i = 0; i < 90; i++) {
      const x = r() * w, len = 60 + r() * 380;
      const grd = g.createLinearGradient(0, 0, 0, len);
      grd.addColorStop(0, `rgba(30,28,24,${0.35 * dirt})`); grd.addColorStop(1, 'rgba(30,28,24,0)');
      g.fillStyle = grd; g.fillRect(x, 0, 2 + r() * 10, len);
    }
  }, repeat);
}

export function concreteTex(THREE, repeat = [4, 4], seed = 7, tone = 120) {
  const r = rng(seed);
  return canvasTex(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = `rgb(${tone},${tone},${tone - 3})`; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 6000; i++) {
      const v = tone - 40 + r() * 80, a = 0.08 + r() * 0.12;
      g.fillStyle = `rgba(${v},${v},${v},${a})`;
      g.fillRect(r() * w, r() * h, 1 + r() * 4, 1 + r() * 4);
    }
    for (let i = 0; i < 25; i++) {
      g.fillStyle = `rgba(20,20,20,${0.05 + r() * 0.1})`;
      g.beginPath(); g.arc(r() * w, r() * h, 10 + r() * 60, 0, 7); g.fill();
    }
  }, repeat);
}

export function textTex(THREE, text, { w = 1024, h = 160, bg = '#e9e6dc', fg = '#151515', font = 'bold 92px "DejaVu Sans Condensed", sans-serif' } = {}) {
  return canvasTex(THREE, w, h, (g) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    g.strokeStyle = fg; g.lineWidth = 10; g.strokeRect(8, 8, w - 16, h - 16);
    g.fillStyle = fg; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(text, w / 2, h / 2 + 4);
  });
}

// low-poly standing person, origin at the feet
export function person(THREE, mat, { height = 1.8, rifle = false, cap = true } = {}) {
  const grp = new THREE.Group();
  const s = height / 1.8;
  const add = (geo, x, y, z, rx = 0, rz = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x * s, y * s, z * s); m.rotation.x = rx; m.rotation.z = rz; m.scale.setScalar(s); grp.add(m); return m; };
  add(new THREE.CapsuleGeometry(0.2, 0.55, 4, 10), 0, 1.22, 0);             // torso (long coat)
  add(new THREE.CylinderGeometry(0.25, 0.3, 0.45, 12), 0, 0.82, 0);         // coat skirt
  add(new THREE.CapsuleGeometry(0.075, 0.62, 4, 8), -0.1, 0.38, 0);        // legs
  add(new THREE.CapsuleGeometry(0.075, 0.62, 4, 8), 0.1, 0.38, 0);
  add(new THREE.CapsuleGeometry(0.065, 0.5, 4, 8), -0.27, 1.18, 0, 0, 0.12); // arms
  add(new THREE.CapsuleGeometry(0.065, 0.5, 4, 8), 0.27, 1.18, 0, 0, -0.12);
  add(new THREE.SphereGeometry(0.115, 16, 12), 0, 1.68, 0);                  // head
  if (cap) {
    add(new THREE.CylinderGeometry(0.13, 0.12, 0.08, 16), 0, 1.79, 0);
    add(new THREE.CylinderGeometry(0.17, 0.17, 0.015, 16), 0, 1.75, 0.04);
  }
  if (rifle) add(new THREE.BoxGeometry(0.05, 0.9, 0.06), 0.24, 1.25, 0.12, 0.1, -0.35);
  return grp;
}

export const ease = t => t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t);
export const lerp = (a, b, t) => a + (b - a) * t;
