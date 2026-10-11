// Portrait reframing for Shorts: wraps an episode scene and nudges its camera per shot when the frame is taller
// than wide (exposure multiplies the tone-mapping exposure; yaw/pitch in radians, positive yaw turns left; fov replaces the vertical fov; fovScale multiplies it).
// Landscape renders pass through untouched. The tweak is applied on top of whatever the scene set this frame.
export function wrap(O, tweaks) {
  let portrait = false;
  const setup = async (THREE, renderer, W, H) => {
    portrait = W < H;
    const ctx = await O.setup(THREE, renderer, W, H);
    ctx._tweak = portrait ? tweaks[ctx.shot] : null;
    if (ctx._tweak && ctx._tweak.exposure) renderer.toneMappingExposure *= ctx._tweak.exposure;   // phone screens: lift dark shots
    return ctx;
  };
  const update = (ctx, t) => {
    const cam = ctx.camera, tw = ctx._tweak;
    if (tw && ctx._base) { cam.quaternion.copy(ctx._base.q); cam.fov = ctx._base.fov; }
    O.update(ctx, t);
    if (!tw) return;
    ctx._base = { q: cam.quaternion.clone(), fov: cam.fov };
    const at = typeof tw === 'function' ? tw(t) : tw;
    if (at.yaw) cam.rotateY(at.yaw);
    if (at.pitch) cam.rotateX(at.pitch);
    if (at.fov || at.fovScale) { cam.fov = at.fov || cam.fov * at.fovScale; cam.updateProjectionMatrix(); }
  };
  return { setup, update };
}
