/* frame0.js : EP1 frame 0 = the thumbnail A base. The lone dormant chest in the empty SF3 room under the spotlight.
 * The lid is SHUT to a thin dark crack: no teeth, no eyes, only two small gold glints in the seam. v3: the chain shows
 * THE TELL (it slides forward round the front corner and curls up on the floor IN FRONT of the chest, where a real
 * chest's chain lies coiled at the back: the detail commenters should catch), top-left key light on the chest (lit
 * left face, darker right side face). Nothing else.
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,comp/comp_kit.js,comp/frame0.js <out.png>
 *
 * window.FRAME0 (shared with thumbA.js / hook.js):
 *   FRAME0.chest(g, x, gy, s, t, o)  draws the whole dormant set piece at ground point (x, gy): cast shadow,
 *     key-lit chest with the tell chain curled in front, glints. o: tell=true (false: v2 chain run to an iron floor
 *     ring), chain (extra MIMIKU2 chain opts for the tell: coilSq, tiltFront), ring=[dx, dy] ring offset (tell=false), glint=0.8 (alpha), glintR=6, breath=0.12 (0..0.3: the crack), light (MIMIKU2 light opts), key (keyLit o)
 */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, CK = window.COMP, PR = window.PROPS_HR;
  const W0 = 180;
  const F = window.FRAME0 = {
    x: 860, s: 1.32, yaw: -14,
    pose: (t, k = {}) => M.merge(M.pose('dormant', 0, F.yaw), {
      lidOpen: 0, breath: k.breath ?? 0.24, teeth: 0.001, tilt: 4, t, shadow: 'ground',
    }),
    // the two glints sit in the seam at the eye columns (the eyes themselves stay hidden behind the lid)
    glints: (ctx, x, gy, s, pose, a = 1, r = 6) => {
      const an = M.anchors(x, gy, s, pose);
      const seamY = an.lip[1] - 1.5 * s;
      an.eyes.forEach((e, i) => CK.glint(ctx, e[0], seamY + (i ? 1.0 : 0) * s, r * s * (i ? 0.8 : 1), a * (i ? 0.75 : 1)));
    },
    chest: (g, x, gy, s, t, o = {}) => {
      const pose = F.pose(t, { breath: o.breath });
      const an = M.anchors(x, gy, s, pose);
      // v3: THE TELL by default (the rig's dormant floor chain: slid forward round the front corner, curled up in
      // front of the chest). o.tell = false brings back the v2 run to the iron floor ring.
      const tell = o.tell !== false;
      const rd = o.ring || [1.35 * W0, 0.12 * W0];
      const ring = [x + rd[0] * s, gy + rd[1] * s];
      const rs = s * 0.8;
      if (tell) pose.chain = Object.assign({ floor: true }, o.chain || {});
      else pose.chain = { pts: CK.floorChain(an.chain, gy - 0.03 * W0 * s + 0.04 * W0 * s, s, [ring[0] + 4 * rs, ring[1] + 2 * rs]) };
      M.castShadow(g, x, gy, s, pose, { alpha: 0.42, squash: 0.2, skew: 0.5, blur: 8 });
      if (!tell) PR.floorRing(g, ring[0], ring[1], rs, { part: 'back' });
      const b = tell ? { x: x - 0.8 * W0 * s, y: gy - 1.05 * W0 * s, w: 1.75 * W0 * s, h: 1.65 * W0 * s }
        : { x: x - 0.75 * W0 * s, y: gy - 1.05 * W0 * s, w: 1.5 * W0 * s + (ring[0] - x) + 40 * s, h: 1.25 * W0 * s };
      // the crack stays a DARK line: the lower gum band (normally a red lip inside an open mouth) is darkened for this
      // shot only (MIMIKU2.COL is restored right after)
      const COL = M.COL, keep = { gum: COL.gum, gumLight: COL.gumLight };
      COL.gum = '#1E1116'; COL.gumLight = '#2A161D';
      try {
        CK.keyLit(g, gg => M.draw(gg, x, gy, s, Object.assign({}, pose, o.light ? { light: o.light } : {})), b, Object.assign({ x0: 0.0, x1: 0.55, dark: 0.42, lite: 0.2 }, o.key || {}));
      } finally { Object.assign(COL, keep); }
      if (!tell) PR.floorRing(g, ring[0], ring[1], rs, { part: 'front' });
      F.glints(g, x, gy, s, pose, o.glint ?? 0.8, o.glintR ?? 6);
      return { pose, an, ring: tell ? null : ring };
    },
  };
  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d');
    const cam = { zoom: 1.5, fx: 860, fy: 560, y: -20 };
    CK.room(ctx, t, {
      cam,
      spot: { alpha: 0.62, rx: 270, ry: 64, topW: 160, topY: -80 },
      // frame 0 is "nothing else": the wall dressing stays (it is the room), floor clutter is kept far from the chest
      floorProps: { bones: [{ x: 1330, y: 760, s: 0.9, rot: 0.3 }], floorScratch: [{ x: 1500, y: 900, s: 1.2, rot: 1.1 }] },
      actors: (g, info) => {
        F.chest(g, F.x, info.contactY + 12, F.s, t, { glint: 0.85, glintR: 6 });
      },
      post: { vignette: 0.7, vigX: 870, vigY: 520 },
    });
  };
})();
