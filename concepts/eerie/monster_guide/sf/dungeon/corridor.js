/* corridor.js : SF4 torch-lit corridor plate for the rule montages. Loads after lib_core.js and dungeon.js.
 * The middle third of the floor (x 640-1280) is kept clear for the cast. window.CORR_DEBUG = true shows it. */
(function () {
  const c = document.getElementById('c');
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    window.CORR_INFO = DUNGEON.corridor(ctx, t, {
      actors: window.CORR_DEBUG ? (g, inf) => {
        g.strokeStyle = '#ff00ff'; g.lineWidth = 2; g.setLineDash([10, 8]);
        g.strokeRect(inf.clear[0], inf.floorY, inf.clear[1] - inf.clear[0], 300);
      } : null,
    });
  };
})();
