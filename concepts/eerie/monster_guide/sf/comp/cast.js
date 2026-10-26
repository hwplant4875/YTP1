/* cast.js : EP1 cast line-up on the SF3 dungeon floor, everyone at the COMMON SCALE (one s for all: W = 180 * s px).
 * Helen (clipboard) | Mimiku dormant | Mimiku standing (tall) | hammer, spear, shield knights | the 404 knight.
 * A W-unit ruler on the left and dashed height marks show the size contrast (Mimiku 3.1 W > Helen 2.5 W > knights 2.4 W).
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,host/helen.js,knight/knight.js,comp/comp_kit.js,comp/cast.js <out.png>
 * Host variant: window.CAST_HOST = 'cursor' (set by comp/cast_cursor.js, loaded after cursor/cursor.js and this file)
 * swaps Helen for Pip, the floating cursor host (alt concept): Pip hovers in Helen's slot, tilted to point at standing
 * Mimiku, with a hover glow and gold target-lock brackets on Mimiku's chest. Helen's height mark becomes Pip's hover
 * height. host/helen.js is then not needed. */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, D = window.DUNGEON, HL = window.HELEN, K = window.KNIGHT, CK = window.COMP;
  const s = 0.7, W = 180 * s, GY = 935;
  const rimCool = { color: '#B8C8E8', alpha: 0.55, dir: [1, -0.4], width: 2.6 };
  const rimWarm = { color: '#FFD9A8', alpha: 0.7, dir: [-1, -0.55], width: 3 };
  const X = { ruler: 92, helen: 250, dorm: 470, stand: 720, hammer: 1010, spear: 1250, shield: 1475, k404: 1730 };

  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    const T = 0.6 + t;
    const cursorHost = window.CAST_HOST === 'cursor', P = window.CURSOR;
    let pip = null;   // Pip's hotspot + target box (cursor host), filled in actors, drawn on top in over
    CK.room(ctx, t, {
      cam: { zoom: 1 },
      spot: false, fgChain: false, skulls: false, motes: 0,
      props: { scratches: [{ x: 1090, y: 170, s: 0.7, rot: -0.3 }], dim: 1.6 },   // wall dressing dimmed behind the line-up
      floorProps: { bones: [{ x: 1880, y: 1040, s: 1, rot: 0.25 }], floorScratch: false },
      under: (g) => {
        // a soft overhead wash along the line-up (light, not a set piece) + floor line
        D.lightPool(g, 960, GY + 4, 980, 0, { color: '#FFE9A8', alpha: 0.16, steady: true, hot: 0, squash: 0.16 });
        D.lightPool(g, 960, GY - 260, 900, 0, { color: '#FFE9A8', alpha: 0.08, steady: true, hot: 0, squash: 0.5 });
      },
      actors: (g) => {
        if (!cursorHost) {
          // ---- Helen, clipboard, pleased, turned a little toward the new hire
          // black stockings (v3 monochrome outfit: black / ivory / white): only the monster wears the pale-skin language
          Object.assign(HL.COL, { legs: '#2E2D32', legsShade: '#1D1C20' });
          try { HL.draw(g, X.helen, GY, s, { pose: 'idle-clipboard', face: 'pleased', turn: 0.35, dir: 1, t: T, blink: 1, look: { x: 0.5, y: 0.1 }, rim: rimWarm, bloom: 0.5, spill: 0.4 }); }
          finally { delete HL.COL.legs; delete HL.COL.legsShade; }
        }
        // ---- Mimiku dormant (the chest is the 1 W unit)
        M.draw(g, X.dorm, GY, s, Object.assign(M.pose('dormant', 0, -10), { breath: 0.6, t: T, chain: { floor: true }, shadow: 'drop' }));
        // ---- Mimiku standing: front-ish, a shy wave, tongue to the knees
        const yaw = -12, F = M.yawFrame(yaw), hip = [0, -1.8 * 180];
        const st = M.merge(M.pose('stand', 1, yaw), {
          hip, lidOpen: 0.98, expr: 'neutral', blush: 1.1, eye: { h: 0.8, irisScale: 0.72, highlight2: true }, t: T, teeth: 1.45, flesh: 1,
          legs: {
            L: { foot: [F.ground(-0.34 * 180, 0.06 * 180)[0], -M.DIM.ankle], kneeOut: -0.45, splay: 0.55 },
            R: { foot: [F.ground(0.34 * 180, -0.06 * 180)[0], -M.DIM.ankle], kneeOut: -0.35, splay: 0.7 },
          },
          arms: {
            L: { hand: [hip[0] - 0.95 * 180, hip[1] - 1.0 * 180], handAng: -Math.PI / 2 - 0.3, curl: 0.15, spread: 1, curlDir: 1, elbowUp: 0.2 },
            R: { hand: [hip[0] + 0.9 * 180, hip[1] + 0.7 * 180], handAng: Math.PI / 2 - 0.15, curl: 0.35, spread: 0.6, curlDir: -1, elbowUp: 0.9 },
          },
          tongue: { len: 1.2, swing: 0.32, curl: 0.35, wave: 0.2, phase: 1.1 },   // hangs off one side: the lower tooth row shows
          look: { x: -0.4, y: 0.1 }, shadow: 'drop',
          light: { key: '#FFE2B0', keyA: 0.35, keyD: 0.03 * 180, keyDir: [-0.6, -1], rim: '#8FA8D8', rimA: 0.4, rimD: 0.02 * 180, rimDir: [1, -0.1] },
        });
        M.draw(g, X.stand, GY, s, st);
        if (cursorHost) {
          // Pip points at standing Mimiku: aim the arrow tip at the chest head (the lid box)
          const an = M.anchors(X.stand, GY, s, st), eye = [(an.eyes[0][0] + an.eyes[1][0]) / 2, (an.eyes[0][1] + an.eyes[1][1]) / 2];
          const hot = [X.helen + 175, GY - 2.15 * W + 6 * Math.sin(T * 2.2)];
          const tipAng = Math.atan2(-50, -22);                     // the arrow's own tip direction (centre -> tip)
          const tilt = Math.atan2(eye[1] - hot[1], eye[0] - hot[0]) - tipAng;
          pip = { hot, tilt, box: { x: an.lidTop[0] - 0.62 * W, y: an.lidTop[1] - 0.08 * W, w: 1.24 * W, h: 1.12 * W } };
          // the hover shadow on the floor (soft, far below: it floats)
          g.save(); g.globalAlpha = 0.32; g.filter = 'blur(6px)';
          S.ellipse(g, X.helen + 20, GY + 2, 64, 11, 0, '#05060A'); g.filter = 'none'; g.restore();
        }
        // ---- the Guests, looking left at the new hire
        K.draw(g, X.hammer, GY, s, { type: 'hammer', pose: 'idle', facing: -1, t: T, rim: rimWarm });
        K.draw(g, X.spear, GY, s, { type: 'spear', pose: 'idle', facing: -1, t: T + 0.4, rim: rimWarm, spearLen: 470 });
        K.draw(g, X.shield, GY, s, { type: 'shield', pose: 'idle', facing: -1, t: T + 0.8, rim: rimWarm });
        K.draw(g, X.k404, GY, s, { type: 'spear', variant: 'k404', pose: 'notebook', facing: -1, t: T + 1.2, rim: rimWarm, spearLen: 470 });
      },
      over: (g) => {
        if (!pip) return;
        P.target(g, pip.box.x, pip.box.y, pip.box.w, pip.box.h, { t: T, len: 0.2, lw: 6 });
        P.draw(g, pip.hot[0], pip.hot[1], 1.45, { state: 'point', expr: 'happy', tilt: pip.tilt, glow: 0.7, t: T });
      },
      post: { vignette: 0.45, vigX: 960, vigY: 560, vigInner: 0.55 },
      screen: (g) => {
        // header
        S.title(g, 'MONSTER HR', 48, 64, 56, { align: 'left', color: '#EDE7F2', weight: 600 });
        S.label(g, 'EP1 cast · common scale · W = chest width', 48, 112, 22, { align: 'left', color: 'rgba(237,231,242,0.62)', weight: 800 });
        // ruler + height marks
        CK.ruler(g, X.ruler, GY, W, 4, { x1: 1880, size: 18, marks: [] });
        const mark = (h, txt, col, lx, x0 = X.ruler + 16, x1 = 1880, above = true) => {
          const y = GY - h * W;
          g.save(); g.strokeStyle = col; g.lineWidth = 2; g.setLineDash([10, 9]);
          g.beginPath(); g.moveTo(x0, y); g.lineTo(x1, y); g.stroke(); g.restore();
          S.label(g, txt, lx, y + (above ? -15 : 15), 17, { align: 'left', color: col, weight: 800, bg: 'rgba(12,15,20,0.55)', pad: 0.3 });
        };
        mark(3.1, 'Mimiku standing 3.1 W', 'rgba(255,200,61,0.85)', 120);
        if (cursorHost) mark(2.15, 'Pip hovers ~2 W', 'rgba(143,230,216,0.8)', 120, X.ruler + 16, 250);
        else mark(2.5, 'Helen 2.5 W', 'rgba(143,230,216,0.8)', 330, X.ruler + 16, 600);
        mark(2.4, 'knight 2.4 W', 'rgba(205,210,218,0.75)', 1585, 880, 1880);
        const ty = GY + 50;
        if (cursorHost) CK.nameTag(g, 'PIP', X.helen, ty, { sub: 'host · the cursor' });
        else CK.nameTag(g, 'HELEN', X.helen, ty, { sub: 'HR manager' });
        CK.nameTag(g, 'MIMIKU', X.dorm, ty, { sub: 'dormant · 1 W' });
        CK.nameTag(g, 'MIMIKU', X.stand, ty, { sub: 'standing · 3.1 W', color: '#FFD978' });
        CK.nameTag(g, 'HAMMER', X.hammer, ty, { sub: 'Guest' });
        CK.nameTag(g, 'SPEAR', X.spear, ty, { sub: 'Guest' });
        CK.nameTag(g, 'SHIELD', X.shield, ty, { sub: 'Guest' });
        CK.nameTag(g, '404', X.k404, ty, { sub: 'the one taking notes', color: '#FF9C8C' });
      },
    });
  };
})();
