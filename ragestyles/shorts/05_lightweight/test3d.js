import { makeStage, fridge, barbell, stands, THREE } from '/engine/stage3d.js';
export const duration = 6;
let S, fr = [], bar;
export async function setup(R) {
  S = await makeStage({});
  bar = barbell(); bar.position.set(0, 1.35, 0); S.scene.add(bar);
  const st = stands(1.2, 1.45); S.scene.add(st);
  for (let i = 0; i < 3; i++) { const f = fridge(); f.position.set((i - 1) * .82, 0, 1.6); S.scene.add(f); fr.push(f); }
  const car = await S.load('covered_car'); car.position.set(3.5, 0, -2); S.scene.add(car);
}
export async function draw(R, t) {
  S.camera.position.set(Math.sin(t * .2) * 1.5 + 1.2, 1.9, 6.2); S.camera.lookAt(0, 1.1, .6);
  R.g.drawImage(S.render(), 0, 0);
  R.vignette(.5); R.grain(.05, t);
}
