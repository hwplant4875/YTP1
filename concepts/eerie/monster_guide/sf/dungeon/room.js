/* room.js : SF3 "empty room" (hook frame 0 / thumbnail A plate). Loads after lib_core.js and dungeon.js.
 * Empty on purpose: the chest goes on the spotlight pool at x 860, contact line y 620 in the composite.
 * Optional debug: window.ROOM_DEBUG = true draws the contact line and the clear zone. */
(function () {
  const c = document.getElementById('c');
  window.draw = t => {
    const ctx = c.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height);
    const info = DUNGEON.room(ctx, t, {
      spot: { x: 860, floorY: 620, alpha: 0.35 },
      actors: window.ROOM_DEBUG ? (g, inf) => {
        g.strokeStyle = '#ff00ff'; g.lineWidth = 2; g.setLineDash([10, 8]);
        g.beginPath(); g.moveTo(860 - 190, inf.contactY); g.lineTo(860 + 190, inf.contactY); g.stroke();
        g.strokeRect(860 - 190, inf.contactY - 300, 380, 300);
      } : null,
    });
    window.ROOM_INFO = info;
  };
})();
