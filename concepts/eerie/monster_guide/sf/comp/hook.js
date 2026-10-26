/* hook.js : EP1 hook beat (~3.2 s): the lone chest still under the spotlight; through the arch doorway three Guest
 * helms, stacked like a totem around the right-hand jamb, peek in at it. Helms are drawn in the passage via DUNGEON
 * roomBack's doorway hook; the gripping gauntlets sit on the jamb face in front of the stone.
 * v2 fixes: the camera is pushed in (the floor strip is cropped) so totem and chest share the frame at thumbnail size;
 * the plumed shield helm is on TOP (the plume streams up and back, never between helms); each helm gets a dark
 * separation halo + a warm rim from the room so all three are countable at 168 px.
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,knight/knight.js,comp/comp_kit.js,comp/frame0.js,comp/hook.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, D = window.DUNGEON, K = window.KNIGHT, CK = window.COMP;
  const KS = 0.76;                                    // knights in the doorway (back wall depth)
  // the totem, bottom -> top: [type, peekH, peekOut, tilt, handH]
  const TOTEM = [
    ['hammer', 56, 66, 12, 124],
    ['spear', 192, 98, 26, 276],
    ['shield', 330, 62, 4, 396],
  ];
  const rim = { color: '#FFD9A8', alpha: 0.95, dir: [-1, -0.25], width: 3.4 };
  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d'), F = window.FRAME0, T = 3.2 + t;
    const cam = { zoom: 1.84, fx: 1262, fy: 560, x: 0, y: -118 };
    let edge = null;
    CK.room(ctx, t, {
      cam,
      spot: { alpha: 0.58, rx: 270, ry: 64, topW: 160, topY: -80 },
      props: { poster: false, board: { x: 330, y: 240, s: 0.9 }, plate: false },
      floorProps: { bones: [{ x: 1180, y: 650, s: 0.8, rot: 0.3 }], floorScratch: false },
      doorway: (g, inf) => {
        // helms lean out of the BACK opening edge (behind the wall-thickness reveal); hands grip the FRONT jamb face
        edge = { x: inf.backCx + inf.backR, y: inf.backFloorY, fx: inf.cx + inf.r, fy: inf.floorY };
        // the passage is lit a little warmer right behind the jamb: the helms read on the void
        D.lightPool(g, edge.x - 60, edge.y - 230, 320, T, { seed: 12, alpha: 0.6, hot: 0.16 });
        TOTEM.forEach(([type, ph, po, tilt]) => {
          const o = { type, pose: 'peek', peekH: ph, peekOut: po, tilt, facing: -1, part: 'helm', t: T, nod: 0.08, shadow: false };
          // dark separation halo: the helm silhouette dilated by ~6 px in the passage colour, so stacked helms never
          // merge into one grey cluster
          CK.halo(g, gg => K.draw(gg, edge.x, edge.y, KS, Object.assign({}, o, { cast: false })), 5, '#0D0B0C');
          K.draw(g, edge.x, edge.y, KS, Object.assign({}, o, { rim, grade: { color: '#FFE2B8', amount: 0.18, mode: 'screen' } }));
        });
      },
      actors: (g, info) => {
        F.chest(g, F.x, info.contactY + 12, F.s, T, { breath: 0.2, glint: 0.7, glintR: 6 });
      },
      overArch: (g) => {
        if (!edge) return;
        TOTEM.forEach(([type, ph, po, tilt, hh]) => {
          K.draw(g, edge.x, edge.y, KS, { type, pose: 'peek', peekH: ph, handH: hh, facing: -1, part: 'hand', t: T, rim });
        });
      },
      post: { vignette: 0.66, vigX: 1060, vigY: 520 },
    });
  };
})();
