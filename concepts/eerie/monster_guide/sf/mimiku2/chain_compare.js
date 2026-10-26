/* chain_compare.js : the chain tell, side by side in the SF3 dungeon room. A plain chest (MIMIKU2 opts.realChest:
 * chain coiled neatly at the side-back) next to Mimiku dormant (chain slid forward around the front corner, curled up
 * in front of it). Same model, same yaw, same scale: the chain is the only difference. Chalk labels on the floor.
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,mimiku2/chain_compare.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, D = window.DUNGEON, CK = window.COMP;
  const s = 1.45, W = 180 * s, GY = 780;
  const X = { real: 560, mimic: 1270 };

  // chalk scrawl lying on the floor (squashed into the floor plane, a little rough)
  function chalk(g, text, x, y, size, o = {}) {
    g.save();
    g.translate(x, y); g.rotate(o.rot || 0); g.scale(1, 0.62);
    g.font = `600 ${size}px Fredoka`; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (o.track) g.letterSpacing = `${o.track}px`;
    const r = S.rng('chalk-' + text);
    for (let i = 0; i < 3; i++) {
      g.globalAlpha = (o.alpha ?? 0.5) * (i ? 0.35 : 1);
      g.fillStyle = '#E9E4D8';
      g.fillText(text, r.range(-1.2, 1.2) * (i ? 1 : 0), r.range(-1.2, 1.2) * (i ? 1 : 0));
    }
    g.restore();
  }
  function chalkLine(g, x0, x1, y, o = {}) {
    g.save(); g.globalAlpha = o.alpha ?? 0.32; g.strokeStyle = '#E9E4D8'; g.lineWidth = 3; g.lineCap = 'round';
    g.beginPath(); g.moveTo(x0, y); g.quadraticCurveTo((x0 + x1) / 2, y + 3, x1, y - 2); g.stroke(); g.restore();
  }

  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    CK.room(ctx, t, {
      cam: { zoom: 1.12, fx: 930, fy: 760 },
      spot: false, fgChain: false, skulls: false, motes: 0, beam: 0,
      props: { board: false, poster: false, plate: false, scratches: [{ x: 1500, y: 200, s: 0.7, rot: -0.3 }], dim: 1.5 },
      floorProps: { bones: [{ x: 160, y: 1010, s: 0.9, rot: 0.3 }], floorScratch: false, drool: false },
      under: g => {
        // two soft overhead pools, one per chest (same light on both: nothing to tell them apart but the chain)
        for (const x of [X.real, X.mimic]) {
          D.lightPool(g, x + 20, GY + 10, 420, 0, { color: '#FFE9A8', alpha: 0.22, steady: true, hot: 0, squash: 0.2 });
          D.lightPool(g, x, GY - 200, 330, 0, { color: '#FFE9A8', alpha: 0.07, steady: true, hot: 0, squash: 0.6 });
        }
        // a chalk divider down the middle of the floor
        g.save(); g.globalAlpha = 0.18; g.strokeStyle = '#E9E4D8'; g.lineWidth = 3; g.setLineDash([18, 16]);
        g.beginPath(); g.moveTo(930, GY - 150); g.lineTo(915, 1080); g.stroke(); g.restore();
        chalk(g, 'REAL', X.real + 10, GY + 118, 34, { track: 6, rot: -0.02 });
        chalkLine(g, X.real - 52, X.real + 72, GY + 140);
        chalk(g, 'MIMIKU', X.mimic - 10, GY + 118, 34, { track: 6, rot: 0.015 });
        chalkLine(g, X.mimic - 90, X.mimic + 70, GY + 140);
      },
      actors: g => {
        M.draw(g, X.real, GY, s, { realChest: true, yaw: -14, shadow: 'drop' });
        M.draw(g, X.mimic, GY, s, { state: 'dormant', yaw: -14, t: 0.4, shadow: 'drop' });
      },
      post: { vignette: 0.5, vigX: 930, vigY: 640 },
    });
  };
})();
