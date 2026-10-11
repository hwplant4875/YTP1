// 2D physics for the "size = population" country marble race. Writes track + per-frame states to race.json.
// usage: node sim.mjs [seed] [--search N]
import planck from 'planck';
import fs from 'fs';
const { World, Vec2, Edge, Circle, Box, Polygon } = planck;

export const COUNTRIES = [ // code, name, population (millions, 2024 UN WPP rounded)
  ['in', 'India', 1451], ['cn', 'China', 1419], ['us', 'USA', 345], ['id', 'Indonesia', 283], ['ng', 'Nigeria', 233],
  ['br', 'Brazil', 212], ['mx', 'Mexico', 131], ['jp', 'Japan', 124], ['de', 'Germany', 84], ['fr', 'France', 66],
  ['gb', 'UK', 69], ['kr', 'South Korea', 52], ['au', 'Australia', 27], ['nl', 'Netherlands', 18], ['pt', 'Portugal', 10], ['ie', 'Ireland', 5.3],
];
// dataset: env DATA=data/area.json etc. (default: population). Radius spans 0.22..0.88 whatever the data range.
export const META = process.env.DATA ? JSON.parse(fs.readFileSync(new URL(process.env.DATA, import.meta.url))) : { key: 'pop', subtitle: 'Marble size = Population', label: 'population', prefix: 'pop. ', items: COUNTRIES };
const VALS = META.items.map(c => c[2]), VMAX = Math.max(...VALS), VMIN = Math.min(...VALS);
const RMAX = META.rmax || 0.88, RMIN = META.rmin || 0.22;
const EXP = Math.log(RMAX / RMIN) / Math.log(VMAX / VMIN);
const radius = v => RMAX * Math.pow(v / VMAX, EXP);
const FPS = 60, DT = 1 / 120;

// ---------- track v3: colourful themed sections (sec = colour theme index used by the scene) ----------
function buildTrack() {
  const T = { walls: [], pegs: [], spinners: [], bumpers: [], gate: null, sections: [] };
  let sec = 0;
  const wall = (pts, kind = 'ramp') => T.walls.push({ pts, kind, sec });
  const W = 8;
  // 0 hopper
  wall([[-W, 0], [-2.2, -2.2]]); wall([[W, 0], [2.2, -2.2]]);
  // 1 zigzag
  sec = 1; let y = -4.0;
  T.sections.push({ name: 'ZIGZAG', y: -3, sec });
  for (let i = 0; i < 3; i++) {
    if (i % 2 === 0) wall([[-W, y], [W - 3.4, y - 3.4]]); else wall([[W, y], [-W + 3.4, y - 3.4]]);
    y -= 5.0;
  }
  // 2 bumper field: bouncy round bumpers scatter the pack
  sec = 2; y -= 1.5;
  T.sections.push({ name: 'BUMPERS', y, sec });
  wall([[-W, y + 2.5], [-3.5, y - 0.2]]);
  const rows = [[-4.0, 0, 4.0], [-2.0, 2.0, 5.4], [-5.4, -1.6, 2.6]];
  rows.forEach((xs, r) => { for (const x of xs) T.bumpers.push({ x, y: y - 2.6 - r * 3.4, r: 0.8 }); });
  y -= 2.6 + 3 * 3.4;
  // 3 fork: a wedge splits the pack into a switchback lane (left) and a spinner lane (right)
  sec = 3;
  T.sections.push({ name: 'FORK', y, sec });
  wall([[-3, y - 2.6], [0, y], [3, y - 2.6]]);
  wall([[0, y - 2.6], [0, y - 13]], 'side');
  wall([[-1.0, y - 4.4], [-6.0, y - 6.6]]);
  wall([[-W, y - 8.4], [-2.2, y - 10.8]]);
  for (let r = 0; r < 4; r++) for (const x of (r % 2 ? [3.9] : [2.6, 5.3])) T.pegs.push({ x, y: y - 4.4 - r * 2.1, r: 0.3, c: 3 });
  y -= 13;
  // 4 merge funnel + size gate
  sec = 4;
  T.sections.push({ name: 'THE SIZE GATE', y, sec });
  wall([[-W, y], [-1.2, y - 4.2]]); wall([[W, y], [1.2, y - 4.2]]);
  T.lips = { y: y - 4.2, inner: 0.57, outer: 1.2, openTo: 1.45 };
  y -= 6.2;
  // 5 wave run: bumpy downhill rails, there and back
  sec = 5;
  T.sections.push({ name: 'WAVES', y, sec });
  const wave = (x0, x1, y0, drop, n) => { const pts = []; for (let k = 0; k <= n; k++) { const f = k / n, x = x0 + (x1 - x0) * f; pts.push([+x.toFixed(3), +(y0 - drop * f + 0.2 * Math.sin(f * Math.PI * 2 * 3)).toFixed(3)]); } return pts; };
  wall(wave(-W, W - 3.2, y, 4.0, 64));
  wall(wave(W, -W + 3.2, y - 6.0, 4.0, 64));
  y -= 11.5;
  // 6 rainbow peg field
  sec = 6;
  T.sections.push({ name: 'PEG FIELD', y: y + 1, sec });
  wall([[W, y + 1.2], [1.5, y - 1.0]]);
  y -= 2.6;
  for (let r = 0; r < 5; r++) {
    for (const x of (r % 2 ? [-3.9, -1.3, 1.3, 3.9] : [-5.2, -2.6, 0, 2.6, 5.2])) T.pegs.push({ x, y, r: 0.24, c: r });
    y -= 2.0;
  }
  // 7 spinner pair right before the finish: last chance for a comeback
  sec = 7; y -= 1.0;
  T.sections.push({ name: 'SPINNERS', y, sec });
  wall([[-W, y + 0.5], [-1.4, y - 2.6]]); wall([[W, y + 0.5], [1.4, y - 2.6]]);
  y -= 5.4;
  T.spinners.push({ x: -3.2, y, len: 4.4, w: 0.28, speed: 1.2 });
  T.spinners.push({ x: 3.2, y: y - 0.3, len: 4.4, w: 0.28, speed: -1.2 });
  y -= 4.2;
  // 8 final funnel, home straight to the finish on the left
  sec = 8;
  T.sections.push({ name: 'FINAL STRAIGHT', y, sec });
  wall([[-W, y], [-1.2, y - 4]]); wall([[W, y], [1.2, y - 4]]);
  y -= 6;
  wall([[W, y + 0.5], [-W + 3.0, y - 3.6]]);
  // the flipper: a one-armed paddle hinged IN the home-straight floor, spinning clockwise. While its arm is above the
  // floor it scoops marbles up and back (up-right), so a leader can be thrown back up the ramp; while it is below
  // the floor the lane is clear.
  if (!process.env.NO_SWEEPER) {
    const sx = +(process.env.SWEEP_X || -2.2), rampY = x => (y + 0.5) + (x - W) * (4.1 / (2 * W - 3.0));
    T.spinners.push({ x: sx, y: rampY(sx), len: +(process.env.SWEEP_LEN || 1.4), w: 0.26, speed: -(+(process.env.SWEEP_SPEED || 2.0)), arms: 1, sweeper: true });
    T.walls[T.walls.length - 1].slot = sx;
  }
  T.finishX = -W + 3.0; T.finishY = y - 3.6; T.finishTop = y + 0.5;
  sec = 0;
  wall([[-W, y - 4.5], [-W, y - 9]], 'side'); wall([[-W, y - 9], [-W + 9, y - 9.4]], 'side'); wall([[-W + 9, y - 9.4], [-W + 9, y - 6.5]], 'side');
  wall([[-W, 8], [-W, y - 4.5]], 'side'); wall([[W, 8], [W, y + 0.5]], 'side');
  T.bottom = y - 10;
  return T;
}

export function simulate(seed, keep = true) {
  let s = seed >>> 0; const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  const T = buildTrack();
  const world = new World({ gravity: Vec2(0, -14) });
  const ground = world.createBody();
  for (const w of T.walls) for (let i = 0; i < w.pts.length - 1; i++)
    ground.createFixture(Edge(Vec2(...w.pts[i]), Vec2(...w.pts[i + 1])), { friction: 0.25, restitution: 0.35 });
  for (const p of T.pegs) ground.createFixture(Circle(Vec2(p.x, p.y), p.r), { friction: 0.2, restitution: 0.55 });
  for (const b of T.bumpers) ground.createFixture(Circle(Vec2(b.x, b.y), b.r), { friction: 0.1, restitution: 0.95 });
  const L = T.lips;
  const lipL = world.createKinematicBody(), lipR = world.createKinematicBody();
  lipL.createFixture(Edge(Vec2(-L.outer, L.y), Vec2(-L.inner, L.y - 0.5)), { friction: 0.3, restitution: 0.3 });
  lipR.createFixture(Edge(Vec2(L.outer, L.y), Vec2(L.inner, L.y - 0.5)), { friction: 0.3, restitution: 0.3 });
  let firstThrough = null, lipOpen = 0, lipT = null;
    const spin = T.spinners.map(sp => {
    const b = world.createKinematicBody({ position: Vec2(sp.x, sp.y) });
    if (sp.arms === 1) { b.createFixture(Box(sp.len / 2, sp.w / 2, Vec2(sp.len / 2, 0), 0), { friction: 0.3, restitution: 0.5 }); b.createFixture(Circle(Vec2(0, 0), 0.16), { friction: 0.3, restitution: 0.3 }); b.sweeper = true; }
    else {
      b.createFixture(Box(sp.len / 2, sp.w / 2), { friction: 0.3, restitution: 0.3 });
      b.createFixture(Box(sp.w / 2, sp.len / 2), { friction: 0.3, restitution: 0.3 });
    }
    b.setAngularVelocity(sp.speed); b.setAngle(sp.sweeper ? 0 : rnd() * Math.PI); return b;
  });
  const sweeps = []; // [time, marble index] whenever the sweeper arm touches a marble
  world.on('begin-contact', c => {
    const a = c.getFixtureA().getBody(), b = c.getFixtureB().getBody();
    const sw = a.sweeper ? a : b.sweeper ? b : null; if (!sw) return;
    const other = sw === a ? b : a, i = balls.findIndex(m => m.b === other);
    if (i >= 0 && (!sweeps.length || sweeps[sweeps.length - 1][1] !== i || t - sweeps[sweeps.length - 1][0] > 0.4)) sweeps.push([+t.toFixed(3), i]);
  });
  const order = META.items.map((c, i) => i).sort(() => rnd() - 0.5);
  const balls = META.items.map(([code, name, pop], i) => {
    const r = radius(pop), k = order.indexOf(i);
    // no starting gate: marbles are dropped from above the hopper so the video opens mid-fall
    const b = world.createDynamicBody({ position: Vec2(-5.8 + (k % 6) * 2.3 + rnd() * 0.3, 2.0 + Math.floor(k / 6) * 1.6 + rnd() * 0.4), linearVelocity: Vec2((rnd() - 0.5) * 1.5, -2), bullet: true, angularDamping: 0.05 });
    b.createFixture(Circle(r), { density: 1, friction: 0.3, restitution: 0.45 });
    return { code, name, pop, r, b, finish: null };
  });
  const frames = [], spinFrames = [];
  let t = 0, done = 0, fi = 0;
  const MAXT = 80, GATE_HOLD = +(process.env.GATE_HOLD || 2.2);
  while (t < MAXT) {
    if (firstThrough !== null && lipT === null && t > firstThrough + GATE_HOLD) lipT = t;
    const target = lipT === null ? 0 : Math.min(1, (t - lipT) / 0.6);
    const v = (target - lipOpen) / DT * (L.openTo - L.inner) * 0; // positions set directly (kinematic teleport is fine for slow moves)
    lipOpen = target;
    lipL.setPosition(Vec2(-lipOpen * (L.openTo - L.inner), 0)); lipR.setPosition(Vec2(lipOpen * (L.openTo - L.inner), 0));
    world.step(DT, 8, 3); t += DT;
    for (const m of balls) {
      const p = m.b.getPosition();
      if (m.finish === null && p.x < T.finishX && p.y < T.finishTop) { m.finish = t; done++; }
      if (firstThrough === null && p.y < L.y - 1.0) firstThrough = t;
      // nudge anything stuck (zero velocity for long) so the race never stalls
      const v = m.b.getLinearVelocity();
      m.still = (Math.abs(v.x) + Math.abs(v.y) < 0.05) ? (m.still || 0) + DT : 0;
      if (m.still > 1.0 && m.finish === null) { const ms = m.b.getMass(); m.b.applyLinearImpulse(Vec2((rnd() - 0.5) * 4 * ms, 5 * ms), p, true); m.still = 0; m.nudges = (m.nudges || 0) + 1; }
    }
    if (keep && t >= fi / FPS) {
      frames.push(balls.map(m => { const p = m.b.getPosition(); return [+p.x.toFixed(4), +p.y.toFixed(4), +m.b.getAngle().toFixed(4)]; }));
      spinFrames.push([...spin.map(b => +b.getAngle().toFixed(4)), +lipOpen.toFixed(4)]);
      fi++;
    }
    if (done === balls.length && t > (Math.max(...balls.map(b => b.finish)) + 3)) break;
  }
  const res = balls.map((m, i) => ({ code: m.code, name: m.name, pop: m.pop, disp: META.items[i][3], r: m.r, finish: m.finish, nudges: m.nudges || 0 }));
  T.lipT = lipT; T.firstThrough = firstThrough; T.sweeps = sweeps;
  return { T, res, frames, spinFrames, t, sweeps };
}

// leader changes, for picking an exciting seed
function leadChanges(sim) {
  let prev = -1, n = 0;
  sim.frames.forEach((f, k) => { if (k % 15) return; let best = 0; f.forEach((p, i) => { if (p[1] < f[best][1]) best = i; }); if (best !== prev) { n++; prev = best; } });
  return n;
}
function stats(sim) {
  const rank = sim.res.map((r, i) => [r.finish ?? 1e9, i]).sort((a, b) => a[0] - b[0]);
  return { lc: sim.frames.length ? leadChanges(sim) : -1, order: rank.map(r => sim.res[r[1]].code).join(','), winner: sim.res[rank[0][1]].name, first: rank[0][0], last: rank[rank.length - 1][0], unfinished: sim.res.filter(r => r.finish === null).length, nudges: sim.res.reduce((a, r) => a + r.nudges, 0) };
}

const args = import.meta.url === new URL('file://' + process.argv[1]).href ? process.argv.slice(2) : [];
if (args.includes('--search')) {
  const n = +args[args.indexOf('--search') + 1];
  for (let seed = 1; seed <= n; seed++) {
    const sim = simulate(seed, true); const st = stats(sim);
    console.log(seed, st.winner, st.first.toFixed(1), st.last.toFixed(1), st.unfinished, 'lc', st.lc, 'n', st.nudges, st.order);
  }
} else if (args.length) {
  const seed = +args[0]; const sim = simulate(seed);
  console.log(stats(sim), sim.frames.length);
  const { items, ...meta } = META;
  fs.writeFileSync(new URL(process.env.OUT || './race.json', import.meta.url), JSON.stringify({ seed, fps: FPS, meta, track: sim.T, res: sim.res, frames: sim.frames, spin: sim.spinFrames }));
}
