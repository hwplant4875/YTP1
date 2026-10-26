/* scene.js : cursor-host style frame. Pip the cursor hovers the lone dormant chest in the EP1 room (frame-0 set piece),
 * a marquee selection around the chest and a game tooltip "Treasure Chest?". Mimiku stays dormant (lid shut, glints).
 * Loads after frame0.js (reuses FRAME0.chest and replaces window.draw).
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,comp/frame0.js,cursor/cursor.js,cursor/scene.js <out.png>
 * window.CURSOR_SCENE: shared room/HUD helpers for cursor/motion.js. */
(function () {
  const c = document.getElementById('c');
  const S = window.SFX, CK = window.COMP, F = window.FRAME0, K = window.CURSOR, C = S.color;
  const CAM = { zoom: 1.5, fx: 860, fy: 560, y: -20 };
  const CS = window.CURSOR_SCENE = {
    CAM,
    // the chest's screen box under CAM (measured from comp_frame0): lid top ~388, feet ~726
    box: { x: 648, y: 368, w: 452, h: 380 },
    room: (ctx, t, o = {}) => CK.room(ctx, t, Object.assign({
      cam: CAM,
      spot: { alpha: 0.62, rx: 270, ry: 64, topW: 160, topY: -80 },
      floorProps: { bones: [{ x: 1330, y: 760, s: 0.9, rot: 0.3 }], floorScratch: [{ x: 1500, y: 900, s: 1.2, rot: 1.1 }] },
      actors: (g, info) => F.chest(g, F.x, info.contactY + 12, F.s, t, { glint: o.glint ?? 0.85, glintR: o.glintR ?? 6, breath: o.breath }),
      post: { vignette: 0.7, vigX: 870, vigY: 520 },
    }, o.room || {})),
    // small quest tracker, top-left (the "this is a game" HUD hint)
    hud: (ctx, o = {}) => {
      const a = o.alpha ?? 1; if (a <= 0) return;
      ctx.save(); ctx.globalAlpha *= a;
      S.roundRect(ctx, 40, 36, 470, 96, 14, 'rgba(10,12,18,0.72)');
      S.roundRect(ctx, 40, 36, 8, 96, [14, 0, 0, 14], '#FFC83D');
      S.label(ctx, 'QUEST · ONBOARDING', 68, 66, 20, { align: 'left', color: '#FFC83D', weight: 900 });
      S.label(ctx, o.line || 'Learn the rules of the dungeon', 68, 100, 23, { align: 'left', color: '#E8ECF6', weight: 800 });
      const n = o.rules ?? 0;
      for (let i = 0; i < 10; i++) S.roundRect(ctx, 324 + i * 17, 58, 11, 11, 3, i < n ? '#FFC83D' : 'rgba(255,255,255,0.18)');
      ctx.restore();
    },
    tip: (ctx, x, y, pop = 1) => K.tooltip(ctx, x, y, {
      title: 'Treasure Chest?', sub: 'UNIDENTIFIED · ???', rarity: '???', w: 410, pop,
      lines: ['Contents: loot (probably)', 'Weight: ...breathing?'],
      icon: (g, cx, cy, r) => { S.circle(g, cx, cy, r, '#2A2140'); S.label(g, '?', cx, cy + 1, 30, { color: '#C59BFF', weight: 1000 }); },
    }),
    keys: (ctx, x, y, pop = 1) => {
      if (pop <= 0) return;
      ctx.save(); ctx.globalAlpha *= S.clamp(pop * 2);
      const key = (k, lbl, kx) => {
        S.roundRect(ctx, kx, y, 58, 40, 8, '#E8ECF6'); S.roundRect(ctx, kx, y + 32, 58, 8, [0, 0, 8, 8], '#AEB6C9');
        S.label(ctx, k, kx + 29, y + 18, 18, { color: '#15131A', weight: 1000 });
        return kx + 70 + S.label(ctx, lbl, kx + 70, y + 20, 22, { align: 'left', color: '#E8ECF6', weight: 800, bg: 'rgba(10,12,18,0.6)', pad: 0.35 }) + 30;
      };
      const x2 = key('LMB', 'Open', x);
      key('RMB', 'Inspect', x2);
      ctx.restore();
    },
  };

  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    const B = CS.box;
    CS.room(ctx, t, {
      glint: 1, glintR: 7,
      room: {
        screen: g => {
          // the chest is selected: marquee from the top-left corner to the bottom-right corner
          K.selection(g, B.x, B.y, B.x + B.w, B.y + B.h, { t, fill: 0.07 });
          CS.hud(g, { rules: 0 });
          CS.tip(g, 1150, 356);
          CS.keys(g, 1156, 572);
          // Pip hovers over the lid, glowing, eyes on the crack (the glints)
          K.draw(g, 1004, 430, 1.35, { state: 'point', expr: 'wow', look: [-0.6, 0.5], glow: 0.75, tilt: S.deg(-6), t });
        },
      },
    });
  };
})();
