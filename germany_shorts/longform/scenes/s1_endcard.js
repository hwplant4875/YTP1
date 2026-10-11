// Shorts end card: the STRATA sliced-S mark, framed for any aspect ratio, sitting in the upper half so the
// wordmark text (ASS overlay) fits below it. Slow push-in and sway.
import { setup as logoSetup, update as logoUpdate } from './strata_logo.js';

export async function setup(THREE, renderer, W, H) {
  const ctx = await logoSetup(THREE, renderer, W, H);
  // distance so the S (about 2.9 units wide) spans ~44% of the frame width
  const halfW = Math.tan(11 * Math.PI / 180) * W / H;
  ctx.dist = Math.max(19, 1.45 / (0.44 * halfW));
  ctx.halfH = Math.tan(11 * Math.PI / 180);
  return ctx;
}

export function update(ctx, t) {
  logoUpdate(ctx, t);
  const k = 1 - Math.exp(-t / 1.2);
  const d = ctx.dist * (1.1 - 0.1 * k);
  // look below the S so it sits at ~35% from the top
  const off = d * ctx.halfH * 0.3;
  ctx.camera.position.set(0, 0.4 - off, d);
  ctx.camera.lookAt(0, -off, 0);
}
