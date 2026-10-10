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
const radius = pop => 0.38 * Math.pow(pop / 50, 0.25);
const FPS = 60, DT = 1 / 120;

// ---------- track (all static geometry as polylines / circles / kinematic bars) ----------
function buildTrack() {
  const T = { walls: [], pegs: [], spinners: [], gate: null, sections: [] };
  const wall = (pts, kind = 'ramp') => T.walls.push({ pts, kind });
  const W = 8;
  // hopper
  wall([[-W, 0], [-2.2, -2.2]]); wall([[W, 0], [2.2, -2.2]]);
  T.gate = { x1: -2.2, x2: 2.2, y: -2.2 };
  // zigzag ramps
  let y = -4.0;
  T.sections.push({ name: 'ZIGZAG', y: -3 });
  for (let i = 0; i < 5; i++) {
    const toRight = i % 2 === 0; // marbles roll toward +x on even ramps
    if (toRight) wall([[-W, y], [W - 3.4, y - 3.4]]); else wall([[W, y], [-W + 3.4, y - 3.4]]);
    y -= 5.0;
  }
  // deflector: steer the drop from the last ramp back toward the middle of the peg field
  wall([[W, y - 0.6], [1.0, y - 2.4]]);
  // plinko
  y -= 3.4;
  T.sections.push({ name: 'PEG FIELD', y: y + 1 });
  for (let r = 0; r < 7; r++) {
    const off = r % 2 ? 1.3 : 0;
    for (let x = -W + 1.3 + off; x < W - 0.9; x += 2.6) T.pegs.push({ x, y, r: 0.24 });
    y -= 2.0;
  }
  // size gate: V funnel whose centre gap only lets small marbles through until the lips slide open
  y -= 0.5;
  T.sections.push({ name: 'THE SIZE GATE', y: y });
  wall([[-W, y], [-1.2, y - 4.2]]); wall([[W, y], [1.2, y - 4.2]]);
  T.lips = { y: y - 4.2, inner: 0.57, outer: 1.2, openTo: 1.45 };
  y -= 7.5;
  // spinners
  T.sections.push({ name: 'SPINNERS', y: y + 1.5 });
  for (let i = 0; i < 3; i++) {
    const sy = y - i * 5.2;
    T.spinners.push({ x: -3.5, y: sy, len: 4.6, w: 0.28, speed: 1.15 * (i % 2 ? -1 : 1) });
    T.spinners.push({ x: 3.5, y: sy - 2.6, len: 4.6, w: 0.28, speed: 1.15 * (i % 2 ? 1 : -1) });
  }
  y -= 15.5;
  // final funnel, then the home straight down to the finish on the left
  T.sections.push({ name: 'FINAL STRAIGHT', y: y });
  wall([[-W, y], [-1.2, y - 4]]); wall([[W, y], [1.2, y - 4]]);
  y -= 6;
  wall([[W, y + 0.5], [-W + 3.0, y - 3.6]]);
  T.finishX = -W + 3.0; T.finishY = y - 3.6; T.finishTop = y + 0.5;
  // catch tray
  wall([[-W, y - 4.5], [-W, y - 9]], 'side'); wall([[-W, y - 9], [-W + 9, y - 9.4]], 'side'); wall([[-W + 9, y - 9.4], [-W + 9, y - 6.5]], 'side');
  wall([[-W, 0], [-W, y - 4.5]], 'side'); wall([[W, 0], [W, y + 0.5]], 'side');
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
  const L = T.lips;
  const lipL = world.createKinematicBody(), lipR = world.createKinematicBody();
  lipL.createFixture(Edge(Vec2(-L.outer, L.y), Vec2(-L.inner, L.y - 0.5)), { friction: 0.3, restitution: 0.3 });
  lipR.createFixture(Edge(Vec2(L.outer, L.y), Vec2(L.inner, L.y - 0.5)), { friction: 0.3, restitution: 0.3 });
  let firstThrough = null, lipOpen = 0, lipT = null;
  const gate = world.createBody(); gate.createFixture(Edge(Vec2(T.gate.x1, T.gate.y), Vec2(T.gate.x2, T.gate.y)));
  const spin = T.spinners.map(sp => {
    const b = world.createKinematicBody({ position: Vec2(sp.x, sp.y) });
    b.createFixture(Box(sp.len / 2, sp.w / 2), { friction: 0.3, restitution: 0.3 });
    b.createFixture(Box(sp.w / 2, sp.len / 2), { friction: 0.3, restitution: 0.3 });
    b.setAngularVelocity(sp.speed); b.setAngle(rnd() * Math.PI); return b;
  });
  const order = COUNTRIES.map((c, i) => i).sort(() => rnd() - 0.5);
  const balls = COUNTRIES.map(([code, name, pop], i) => {
    const r = radius(pop), k = order.indexOf(i);
    const b = world.createDynamicBody({ position: Vec2(-6 + (k % 6) * 2.3 + rnd() * 0.3, 0.6 + Math.floor(k / 6) * 1.7), bullet: true, angularDamping: 0.05 });
    b.createFixture(Circle(r), { density: 1, friction: 0.3, restitution: 0.45 });
    return { code, name, pop, r, b, finish: null };
  });
  const frames = [], spinFrames = [];
  let t = 0, done = 0, fi = 0, gateOpen = false;
  const GATE_T = 1.6, MAXT = 80;
  while (t < MAXT) {
    if (!gateOpen && t >= GATE_T) { world.destroyBody(gate); gateOpen = true; }
    if (firstThrough !== null && lipT === null && t > firstThrough + 4.5) lipT = t;
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
      if (m.still > 1.0 && m.finish === null && gateOpen) { const ms = m.b.getMass(); m.b.applyLinearImpulse(Vec2((rnd() - 0.5) * 4 * ms, 5 * ms), p, true); m.still = 0; m.nudges = (m.nudges || 0) + 1; }
    }
    if (keep && t >= fi / FPS) {
      frames.push(balls.map(m => { const p = m.b.getPosition(); return [+p.x.toFixed(4), +p.y.toFixed(4), +m.b.getAngle().toFixed(4)]; }));
      spinFrames.push([...spin.map(b => +b.getAngle().toFixed(4)), +lipOpen.toFixed(4)]);
      fi++;
    }
    if (done === balls.length && t > (Math.max(...balls.map(b => b.finish)) + 3)) break;
  }
  const res = balls.map(m => ({ code: m.code, name: m.name, pop: m.pop, r: m.r, finish: m.finish, nudges: m.nudges || 0 }));
  T.lipT = lipT; T.firstThrough = firstThrough;
  return { T, res, frames, spinFrames, t };
}

// leader changes, for picking an exciting seed
function leadChanges(sim) {
  let prev = -1, n = 0;
  sim.frames.forEach((f, k) => { if (k % 15) return; let best = 0; f.forEach((p, i) => { if (p[1] < f[best][1]) best = i; }); if (best !== prev) { n++; prev = best; } });
  return n;
}
function stats(sim) {
  const rank = sim.res.map((r, i) => [r.finish ?? 1e9, i]).sort((a, b) => a[0] - b[0]);
  return { lc: sim.frames.length ? leadChanges(sim) : -1, order: rank.map(r => sim.res[r[1]].code).join(','), winner: sim.res[rank[0][1]].name, first: rank[0][0], last: rank[rank.length - 1][0], unfinished: sim.res.filter(r => r.finish === null).length };
}

const args = process.argv.slice(2);
if (args.includes('--search')) {
  const n = +args[args.indexOf('--search') + 1];
  for (let seed = 1; seed <= n; seed++) {
    const sim = simulate(seed, true); const st = stats(sim);
    console.log(seed, st.winner, st.first.toFixed(1), st.last.toFixed(1), st.unfinished, 'lc', st.lc, st.order);
  }
} else if (args.length) {
  const seed = +args[0]; const sim = simulate(seed);
  console.log(stats(sim), sim.frames.length);
  fs.writeFileSync(new URL('./race.json', import.meta.url), JSON.stringify({ seed, fps: FPS, track: sim.T, res: sim.res, frames: sim.frames, spin: sim.spinFrames }));
}
