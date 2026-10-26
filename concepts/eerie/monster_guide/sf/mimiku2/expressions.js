/* expressions.js : Mimiku v2 expression sheet, 8 chest close-ups with labels.
 * node render_sf.mjs core/lib_core.js,mimiku2/mimiku2.js,mimiku2/sheet_common.js,mimiku2/expressions.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, W = M.DIM.W;
  const INK = '#EDE7F2', SUB = 'rgba(237,231,242,0.55)';
  // per expression: the lid does half the acting
  const X = [
    ['happy', 'HAPPY', 'smile-squint eyes · big blush · lid bounces', { lidOpen: 0.95, look: { x: 0, y: 0 } }],
    ['nervous', 'NERVOUS', 'tiny slit pupils · sweat · lid half shut', { lidOpen: 0.62, tilt: -4 }],
    ['hungry', 'HUNGRY', 'star pupils · drool · teeth show', { lidOpen: 1.0 }],
    ['annoyed', 'ANNOYED', 'half-lidded · side-eye · lid lowered', { lidOpen: 0.5, tilt: 3 }],
    ['scared', 'SCARED', 'pin pupils · lid clamps down · tears', { lidOpen: 0.56, tilt: -3 }],
    ['sleepy', 'SLEEPY', 'shut eyes · lid droops · zzz', { lidOpen: 0.45, pitch: 6, t: 0.2 }],
    ['smitten', 'SMITTEN', 'heart pupils · blush lines · hearts', { lidOpen: 0.92, tilt: 4 }],
    ['pounce', 'POUNCE', 'cream-gold eyes · lid flung wide · tongue out', { lidOpen: 1.2, pitch: 18 }],
  ];
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const SH = window.M2SHEET;
    SH.bg(ctx, 'MIMIKU', 'v2 · expressions', 'the cute layer lives in the mouth: glowing eyes, blush, and the lid acting like eyelids', { palette: false });
    const cols = 4, pw = 430, ph = 420, gx = 24, gy = 30, x0 = (1920 - cols * pw - (cols - 1) * gx) / 2, y0 = 128;
    X.forEach(([ex, name, sub, extra], i) => {
      const x = x0 + (i % cols) * (pw + gx), y = y0 + Math.floor(i / cols) * (ph + gy);
      SH.inset(ctx, x, y, pw, ph - 34, name, sub, g => {
        g.fillStyle = '#272A33'; g.fillRect(x, y, pw, ph);
        const o = Object.assign({ state: 'stand', yaw: -8, expr: ex, t: 1.3 + i * 0.37, shadow: 'none', parts: { legs: false, arms: false, tongue: ex === 'hungry' || ex === 'happy' || ex === 'smitten' || ex === 'pounce', chain: true } }, extra);
        if (o.parts.tongue) o.tongue = ex === 'pounce' ? { len: 0.8, ang: Math.PI / 2 - 0.25, curl: 0.55, wave: 0.5, swing: 0 } : { len: 0.55, curl: 0.25, swing: 0.1 };
        SH.focus(g, x + pw / 2, y + (ph - 34) * 0.54, 1.6, o, a => [a.mouth[0], a.mouth[1] + 0.05 * W * 1.6]);
      });
    });
    SH.post(ctx);
  };
})();
