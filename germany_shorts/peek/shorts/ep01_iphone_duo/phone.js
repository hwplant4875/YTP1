// A generic book-style foldable (no logos): two metal-framed halves, a hinge spine,
// one flexible inner screen that bends with the fold, and a crack that can grow.
import * as THREE from 'three';

export const PHONE = {
  W: 6.35, H: 4.55, T: 0.2, R: 0.52, BS: 0.055, BT: 0.06, BEZEL: 0.075, GAP: 0.006,
  crackV: 0.30,   // crack centre, as a fraction of screen height from the bottom
};
PHONE.SW = PHONE.W - 2 * (PHONE.BS + PHONE.BEZEL);
PHONE.SH = PHONE.H - 2 * (PHONE.BS + PHONE.BEZEL);
PHONE.SR = PHONE.R - PHONE.BS - PHONE.BEZEL;

export function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

export function roundedRectShape(w, h, rTL, rTR, rBR, rBL) {
  const s = new THREE.Shape();
  const x0 = -w / 2, y0 = -h / 2, x1 = w / 2, y1 = h / 2;
  s.moveTo(x0 + rBL, y0);
  s.lineTo(x1 - rBR, y0);
  s.absarc(x1 - rBR, y0 + rBR, rBR, -Math.PI / 2, 0, false);
  s.lineTo(x1, y1 - rTR);
  s.absarc(x1 - rTR, y1 - rTR, rTR, 0, Math.PI / 2, false);
  s.lineTo(x0 + rTL, y1);
  s.absarc(x0 + rTL, y1 - rTL, rTL, Math.PI / 2, Math.PI, false);
  s.lineTo(x0, y0 + rBL);
  s.absarc(x0 + rBL, y0 + rBL, rBL, Math.PI, 1.5 * Math.PI, false);
  return s;
}

export const MAT = {
  titanium: () => new THREE.MeshPhysicalMaterial({ color: 0xa9a9b0, metalness: 1.0, roughness: 0.3 }),
  glass: () => new THREE.MeshPhysicalMaterial({ color: 0x040405, metalness: 0.0, roughness: 0.18, clearcoat: 1.0, clearcoatRoughness: 0.06 }),
  backGlass: () => new THREE.MeshPhysicalMaterial({ color: 0xdcdcdf, metalness: 0.0, roughness: 0.55, clearcoat: 0.6, clearcoatRoughness: 0.35 }),
};

export function halfGeometry(side) {
  const { W, H, T, R, BS, BT, GAP } = PHONE;
  const hw = W / 2 - GAP;
  const ri = 0.012, ro = R - BS;
  // left half: rounded on its left (outer) corners; right half mirrored
  const shape = side < 0
    ? roundedRectShape(hw - 2 * BS, H - 2 * BS, ro, ri, ri, ro)
    : roundedRectShape(hw - 2 * BS, H - 2 * BS, ri, ro, ro, ri);
  const g = new THREE.ExtrudeGeometry(shape, { depth: T - 2 * BT, bevelEnabled: true, bevelThickness: BT, bevelSize: BS, bevelSegments: 6, curveSegments: 40 });
  g.translate(side * (hw / 2 + GAP), 0, -(T - 2 * BT) / 2);
  g.computeVertexNormals();
  return g;
}

// ---------- screen textures ----------
export const SCW = 2048, SCH = Math.round(2048 * PHONE.SH / PHONE.SW);
export function makeWallpaper() {
  const c = document.createElement('canvas'); c.width = SCW; c.height = SCH;
  const g = c.getContext('2d');
  const base = g.createLinearGradient(0, 0, SCW, SCH);
  base.addColorStop(0, '#0c1338'); base.addColorStop(0.55, '#080623'); base.addColorStop(1, '#190626');
  g.fillStyle = base; g.fillRect(0, 0, SCW, SCH);
  g.filter = 'blur(70px)';
  const ribbon = (pts, col, wdt, a) => {
    g.globalAlpha = a; g.strokeStyle = col; g.lineWidth = wdt; g.lineCap = 'round';
    g.beginPath(); g.moveTo(pts[0], pts[1]); g.bezierCurveTo(pts[2], pts[3], pts[4], pts[5], pts[6], pts[7]); g.stroke();
  };
  ribbon([-200, 1300, 500, 600, 1100, 1500, 2300, 300], '#6a4bff', 280, 0.9);
  ribbon([-100, 300, 700, 900, 1300, -100, 2200, 900], '#2a7dff', 220, 0.75);
  ribbon([300, 1600, 900, 1000, 1500, 1200, 2300, 1500], '#d04bff', 190, 0.6);
  ribbon([1200, -200, 1400, 500, 1700, 400, 2300, 100], '#ff7a3d', 120, 0.28);
  g.filter = 'none'; g.globalAlpha = 1;
  // the crease: a faint dip of light along the fold line
  const cx = SCW / 2;
  const cg = g.createLinearGradient(cx - 26, 0, cx + 26, 0);
  cg.addColorStop(0, 'rgba(0,0,0,0)'); cg.addColorStop(0.42, 'rgba(0,0,0,0.22)'); cg.addColorStop(0.5, 'rgba(255,255,255,0.10)'); cg.addColorStop(0.58, 'rgba(0,0,0,0.22)'); cg.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = cg; g.fillRect(cx - 26, 0, 52, SCH);
  return c;
}

// Crack geometry, built once from a fixed seed. Paths are polylines in screen-texture pixels.
// The main crack follows the crease (glass breaks along the fold line): short straight runs, small sharp kinks.
export function buildCrack() {
  const rnd = mulberry32(19991023);
  const cx = SCW / 2, cy = SCH * (1 - PHONE.crackV);
  const paths = [];
  const crease = (dir, len) => {
    const p = [[cx, cy]]; let y = cy, x = cx, L = 0;
    while (L < len) {
      const st = 14 + rnd() * 12; y += dir * st; L += st;
      x = cx + Math.max(-7, Math.min(7, (x - cx) * 0.4 + (rnd() - 0.5) * 12));
      p.push([x, y]);
    }
    paths.push({ pts: p, start: 0, len: L, w: 3.0, taper: true });
    return p;
  };
  const up = crease(-1, 400), down = crease(1, 320);
  // splinters: short straight shards leaving the crease at 30-60 degrees
  const shard = (from, side, ang, len, start) => {
    const p = [[from[0], from[1]]]; let x = from[0], y = from[1], a = ang;
    const n = 2 + Math.floor(rnd() * 2);
    for (let i = 0; i < n; i++) { a += (rnd() - 0.5) * 0.35; x += Math.cos(a) * len / n; y += Math.sin(a) * len / n; p.push([x, y]); }
    paths.push({ pts: p, start, len, w: 1.6 });
  };
  const picks = [[up, 3], [up, 7], [up, 12], [down, 2], [down, 6], [down, 10], [up, 18]];
  picks.forEach(([arr, i], k) => {
    const from = arr[Math.min(i, arr.length - 1)];
    const side = k % 2 ? 1 : -1;
    const vert = arr === up ? -1 : 1;
    const ang = Math.atan2(vert * (0.9 + rnd() * 0.8), side);
    shard(from, side, ang, 34 + rnd() * 70, 0.12 + i * 0.03);
  });
  // two hairlines running beside the main crack
  for (const [dx, y0, y1] of [[9, -150, -40], [-8, 30, 140]]) {
    const p = []; for (let y = y0; y <= y1; y += 18) p.push([cx + dx + (rnd() - 0.5) * 4, cy + y]);
    paths.push({ pts: p, start: 0.45, len: y1 - y0, w: 1.0 });
  }
  const blot = []; const n = 48; const ph = [rnd() * 6.28, rnd() * 6.28, rnd() * 6.28];
  for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; blot.push([Math.cos(a), Math.sin(a) * 1.5, 0.78 + 0.12 * Math.sin(a * 3 + ph[0]) + 0.07 * Math.sin(a * 5 + ph[1]) + 0.05 * Math.sin(a * 9 + ph[2])]); }
  return { cx, cy, paths, blot };
}

function strokePaths(g, crack, prog, widthMul) {
  for (const p of crack.paths) {
    const local = (prog - p.start) / Math.max(0.05, 1 - p.start);
    if (local <= 0) continue;
    const upto = Math.min(1, local) * (p.pts.length - 1);
    const n = Math.floor(upto);
    for (let i = 0; i < n + 1 && i < p.pts.length - 1; i++) {
      const f = Math.min(1, upto - i);
      if (f <= 0) break;
      const [x0, y0] = p.pts[i], [x1, y1] = p.pts[i + 1];
      const k = p.taper ? 1 - 0.75 * (i / (p.pts.length - 1)) : 1 - 0.5 * (i / Math.max(1, p.pts.length - 1));
      g.lineWidth = p.w * widthMul * k;
      g.beginPath(); g.moveTo(x0, y0); g.lineTo(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f); g.stroke();
    }
  }
}

// Straight "pixel lines" (dead or stuck rows/columns) that OLED panels show when the layer under the glass breaks.
// [dx0, dy, dx1, colour, width, delay]: horizontal lines run from cx+dx0 to cx+dx1 at row cy+dy;
// vertical lines are written with dy = 'v' and run along the crease column.
const PIXEL_LINES = [
  [0, 14, 'edge', '93,255,138', 4, 0.0],     // the long bright line across one side (reported by owners)
  [-170, -22, 0, '255,90,220', 3, 0.25],
  [8, 46, 210, '120,230,255', 3, 0.4],
  [-90, 58, 0, '255,255,255', 2, 0.55],
];

export function paintScreen(ctx, wallpaper, crack, prog, line) {
  ctx.drawImage(wallpaper, 0, 0);
  if (prog > 0) {
    const { cx, cy } = crack;
    // dead OLED "ink" spreading from the failure point: soft, irregular, darkest in the middle
    const r = 44 * Math.min(1, prog * 1.25);
    ctx.save();
    ctx.filter = 'blur(5px)';
    ctx.fillStyle = 'rgba(0,0,0,0.92)';
    ctx.beginPath();
    crack.blot.forEach(([x, y, k], i) => { const px = cx + x * r * k, py = cy + y * r * k * 0.8; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
    ctx.closePath(); ctx.fill();
    ctx.filter = 'none';
    const rg = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 2.2);
    rg.addColorStop(0, 'rgba(0,0,0,0.55)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rg; ctx.fillRect(cx - r * 2.2, cy - r * 2.2, r * 4.4, r * 4.4);
    // dead rows to the left of the failure
    const hg = ctx.createLinearGradient(cx - 150, 0, cx, 0);
    hg.addColorStop(0, 'rgba(0,0,0,0)'); hg.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = hg; ctx.fillRect(cx - 150 * prog, cy - 12, 150 * prog, 20);
    // dead column down the crease
    const vg = ctx.createLinearGradient(0, cy - 420 * prog, 0, cy + 360 * prog);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(0.5, 'rgba(0,0,0,0.9)'); vg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = vg; ctx.fillRect(cx - 5, cy - 420 * prog, 10, 780 * prog);
    ctx.restore();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = 'rgba(0,0,0,0.85)'; strokePaths(ctx, crack, prog, 2.4);
  }
  // rounded screen corners
  const rr = PHONE.SR / PHONE.SW * SCW;
  ctx.save(); ctx.globalCompositeOperation = 'destination-in';
  ctx.beginPath(); ctx.roundRect(0, 0, SCW, SCH, rr); ctx.fill(); ctx.restore();
}

export function crackGlowTexture(ctx, crack, prog, line, hot) {
  ctx.clearRect(0, 0, SCW, SCH);
  const { cx, cy } = crack;
  if (prog > 0) {
    ctx.save();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = 'rgba(200,225,255,0.9)';
    ctx.shadowColor = 'rgba(170,210,255,0.8)'; ctx.shadowBlur = 6;
    strokePaths(ctx, crack, prog, 0.95);
    ctx.shadowBlur = 0;
    ctx.strokeStyle = 'rgba(255,255,255,1)';
    strokePaths(ctx, crack, prog, 0.5);
    ctx.restore();
    if (hot > 0.45) {
      const k = (hot - 0.45) / 0.55, rr = 10 + 26 * k;
      const rg = ctx.createRadialGradient(cx, cy, 0, cx, cy, rr);
      rg.addColorStop(0, `rgba(255,255,255,${Math.min(1, 0.8 * k)})`); rg.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = rg; ctx.fillRect(cx - rr, cy - rr, rr * 2, rr * 2);
    }
  }
  if (line > 0) {
    for (const [x0, dy, x1raw, col, w, delay] of PIXEL_LINES) {
      const k = Math.min(1, Math.max(0, (line - delay) / (1 - delay + 1e-6)));
      if (k <= 0) continue;
      const x1 = x1raw === 'edge' ? SCW - cx : x1raw;
      const a = cx + x0, b = cx + x0 + (x1 - x0) * k;
      ctx.fillStyle = `rgba(${col},0.95)`;
      ctx.fillRect(Math.min(a, b), cy + dy - w / 2, Math.abs(b - a), w);
    }
  }
}

// ---------- build ----------
export function buildPhone() {
  const { W, H, T, SW, SH } = PHONE;
  const root = new THREE.Group();
  const mats = { titanium: MAT.titanium(), glass: MAT.glass() };

  const pivots = [];
  for (const side of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.set(0, 0, T / 2);
    const mesh = new THREE.Mesh(halfGeometry(side), [mats.glass, mats.titanium]);
    mesh.position.z = -T / 2;
    mesh.castShadow = true; mesh.receiveShadow = true;
    pivot.add(mesh);
    root.add(pivot);
    pivots.push(pivot);
  }

  // hinge spine: half cylinder on the back, hidden inside the halves when open
  const spine = new THREE.Mesh(new THREE.CylinderGeometry(T * 0.985, T * 0.985, H - 0.16, 64, 1, false, Math.PI / 2, Math.PI), mats.titanium);
  spine.position.set(0, 0, T / 2);
  spine.castShadow = true;
  root.add(spine);

  // the inner screen: one bendable sheet
  const geo = new THREE.PlaneGeometry(SW, SH, 160, 80);
  const base = geo.attributes.position.array.slice();
  const wall = makeWallpaper();
  const crack = buildCrack();
  const sc = document.createElement('canvas'); sc.width = SCW; sc.height = SCH;
  const sctx = sc.getContext('2d');
  const gc = document.createElement('canvas'); gc.width = SCW; gc.height = SCH;
  const gctx = gc.getContext('2d');
  const screenTex = new THREE.CanvasTexture(sc); screenTex.colorSpace = THREE.SRGBColorSpace; screenTex.anisotropy = 8;
  const glowTex = new THREE.CanvasTexture(gc); glowTex.colorSpace = THREE.SRGBColorSpace; glowTex.anisotropy = 8;
  const screenMat = new THREE.MeshPhysicalMaterial({ color: 0x000000, map: screenTex, alphaTest: 0.5, emissive: 0xffffff, emissiveMap: screenTex, emissiveIntensity: 1.25, roughness: 0.32, metalness: 0.0, envMapIntensity: 0.07, specularIntensity: 0.22 });
  const screen = new THREE.Mesh(geo, screenMat);
  screen.receiveShadow = false;
  const glowMat = new THREE.MeshBasicMaterial({ map: glowTex, alphaMap: null, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, color: new THREE.Color(2.2, 2.2, 2.2), polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
  const glow = new THREE.Mesh(geo, glowMat);
  root.add(screen, glow);

  const state = { fold: -1, crack: -1, line: -1, hot: -1, bulge: -1 };
  const phone = {
    root, pivots, spine, screen, glow, geo, base, mats, crack, state,
    setCrack(prog, hot = 1, line = prog > 0.8 ? 1 : 0) {
      prog = Math.round(prog * 200) / 200; hot = Math.round(hot * 50) / 50; line = Math.round(line * 100) / 100;
      if (prog === state.crack && hot === state.hot && line === state.line) return;
      state.crack = prog; state.hot = hot; state.line = line;
      paintScreen(sctx, wall, crack, prog, line); screenTex.needsUpdate = true;
      crackGlowTexture(gctx, crack, prog, line, hot); glowTex.needsUpdate = true;
      glow.visible = prog > 0 || line > 0;
      glowMat.color.setScalar(2.0 + 2.5 * Math.max(0, hot - 0.4));
    },
  };
  setFold(phone, 0);
  phone.setCrack(0);
  return phone;
}

// fold: 0 = flat open, 1 = closed (each half turned 90 degrees toward the screen side)
export function setFold(phone, fold, bulge = 0) {
  if (fold === phone.state.fold && bulge === phone.state.bulge) return;
  phone.state.fold = fold; phone.state.bulge = bulge;
  const { T, SH } = PHONE;
  const th = fold * Math.PI / 2;
  phone.pivots[0].rotation.y = th;
  phone.pivots[1].rotation.y = -th;
  const pos = phone.geo.attributes.position.array, base = phone.base;
  const zr = 0.004;
  const yb = -SH / 2 + SH * PHONE.crackV;
  const c = Math.cos(th), s = Math.sin(th);
  for (let i = 0; i < pos.length; i += 3) {
    const x = base[i], y = base[i + 1];
    let z = zr + bulge * 0.05 * Math.exp(-((x / 0.22) ** 2 + ((y - yb) / 0.35) ** 2));
    if (x >= 0) { pos[i] = x * c - z * s; pos[i + 2] = x * s + z * c + T / 2; }
    else { pos[i] = x * c + z * s; pos[i + 2] = -x * s + z * c + T / 2; }
    pos[i + 1] = y;
  }
  phone.geo.attributes.position.needsUpdate = true;
  phone.geo.computeVertexNormals();
}
