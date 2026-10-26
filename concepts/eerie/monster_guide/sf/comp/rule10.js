/* rule10.js : the Rule-10 money shot, "WHEN THEY KNOCK, OPEN WIDE."
 * A Guest has just test-knocked the chest; Mimiku has burst open: lid flung WIDE (~140 deg, a clear V jaw with teeth on
 * both lips, the dark mouth and the big gold eyes facing the knocker), the tall gaunt fleshy body unfolded mid-pounce
 * over him (hands either side of the helm, legs trailing back, tongue streaming). The other two Guests back away to the
 * right (torsos leaning back, feet scrambling, dust puffs). The spotlight cone and pool sit ON the knock spot, so the
 * action is the brightest area. Inset (top-right, over the dark arch top): Helen's screen face, pleased, APPROVED.
 * SMALL=1 node render_sf.mjs core/lib_core.js,dungeon/dungeon.js,dungeon/props_hr.js,mimiku2/mimiku2.js,host/helen.js,knight/knight.js,comp/comp_kit.js,comp/rule10.js <out.png> */
(function () {
  const c = document.getElementById('c');
  const M = window.MIMIKU2, S = window.SFX, D = window.DUNGEON, K = window.KNIGHT, HL = window.HELEN, CK = window.COMP;
  const W0 = 180;
  window.RULE10 = {
    s: 0.9,
    kx: 1010,                // the knocker's ground point (design px)
    gy: 905,                 // the forward floor line (design px) = the spotlight pool centre
    mdx: 0.85,               // chest ground point offset left of the helm (W)
  };
  const rimWarm = { color: '#FFD9A8', alpha: 0.8, dir: [-1, -0.55], width: 3.2 };

  // the dive. The chest is posed in its own 3D frame as a clear 3/4 open mouth (lid flung back ~143 deg, the dark mouth,
  // both tooth rows and the eyes all facing the camera-right), then the WHOLE character is rotated in screen space by
  // ROT so that the jaw V opens down-right onto the helm. Targets are solved in the un-rotated local frame.
  const ROT = 0.72;                              // radians, clockwise screen rotation of the whole dive
  const rotAbout = (q, c, a) => { const dx = q[0] - c[0], dy = q[1] - c[1], cs = Math.cos(a), sn = Math.sin(a); return [c[0] + dx * cs - dy * sn, c[1] + dx * sn + dy * cs]; };
  function pounceOpts(mx, gy, s, helmLocal) {
    const target = [(helmLocal[0] - mx) / s, (helmLocal[1] - gy) / s];
    const p = M.pouncePose({ dir: 1, target, grab: 0.5 });
    const hip = [0, -2.5 * W0];
    return M.merge(p, {
      hip, yaw: 22, pitch: 40, tilt: 20, lidOpen: 1.31,
      t: 0.5, shadow: 'drop', teeth: 1.55, blush: 1, flesh: 1, eyeLift: 0.08,
      eye: { h: 0.86, irisScale: 0.58, highlight2: true },
      fx: { drool: 1, sweat: 0 },
      // legs trail back (screen-left), knees bent: the frog-leap silhouette
      legs: {
        L: { foot: [hip[0] - 1.25 * W0, hip[1] + 0.2 * W0], toe: 1.9, kneeOut: 0.5, grow: 1, splay: 0.4 },
        R: { foot: [hip[0] - 1.6 * W0, hip[1] + 0.75 * W0], toe: 1.6, kneeOut: 0.6, grow: 1, splay: 0.5 },
      },
      tongue: { len: 0.8, ang: Math.PI * 0.62, curl: 0.35, wave: 0.3, phase: 2.2, swing: 0, behind: true },
      chain: { swing: 1.2, sag: 0.45, sway: 0.18, t: 0.5 },
      light: { key: '#FFE2B0', keyA: 0.55, keyD: 0.03 * W0, keyDir: [-0.6, -1], rim: '#8FA8D8', rimA: 0.45, rimD: 0.02 * W0, rimDir: [1, -0.1] },
    });
  }

  function dust(g, x, y, s, n, seed, a = 0.5) {
    const r = S.rng(seed);
    for (let i = 0; i < n; i++) {
      const dx = r.range(-1, 1) * 40 * s, dy = -r.range(0, 1) * 22 * s, rr = r.range(12, 24) * s;
      g.save(); g.filter = `blur(${3 * s}px)`;
      S.ellipse(g, x + dx, y + dy, rr, rr * 0.72, 0, `rgba(176,170,150,${a * r.range(0.4, 0.8)})`);
      S.ellipse(g, x + dx - rr * 0.25, y + dy - rr * 0.25, rr * 0.55, rr * 0.38, 0, `rgba(226,218,196,${a * 0.5})`);
      g.restore();
    }
  }

  window.draw = t => {
    t = t || 0;
    const ctx = c.getContext('2d'), R = window.RULE10, s = R.s, T = 7.3 + t;
    const cam = { zoom: 1.1, fx: 1060, fy: 560, x: 0, y: 0 };
    CK.room(ctx, t, {
      cam, motes: 16,
      // the cone + pool sit on the knock spot: the money shot is the brightest thing in frame
      spot: { x: R.kx - 60, floorY: R.gy, alpha: 0.78, rx: 380, ry: 84, topW: 230, topY: -80 },
      beam: 0.62,
      props: { poster: { x: 120, y: 150, s: 0.9 }, board: { x: 360, y: 250 }, plate: false, dim: 1.3 },
      floorProps: { bones: [{ x: 260, y: 990, s: 1.2, rot: -0.3 }], floorScratch: false },
      actors: (g, info) => {
        const gy = info.contactY, kx = R.kx;
        // ---- the knocker: just knocked (rebound -> recoiling), leaning back, sweating
        const ko = { type: 'hammer', pose: 'knock', k: 0.66, facing: -1, t: T, lean: -12, tilt: -16, sweat: 3, lines: 1, rim: rimWarm };
        const kn = K.solve(kx, gy, s, ko);
        const helm = { x: kn.helm.x - 0.02 * W0 * s, y: kn.helm.y - 0.04 * W0 * s };
        // ---- the two others, backing off to the right: torsos thrown back, rear feet scrambling right, dust
        const bk = [
          { x: 1400, y: gy - 46, sc: s * 0.9, type: 'shield', k: 0.62, t: T + 0.3, lean: -16 },
          { x: 1640, y: gy - 18, sc: s * 0.95, type: 'spear', k: 0.12, t: T + 0.6, lean: -18, spearLen: 360 },
        ];
        bk.forEach((b, i) => {
          dust(g, b.x + 70 * b.sc, b.y + 2, b.sc, 4, 'r10-dust' + i, 0.42);
          K.draw(g, b.x, b.y, b.sc, { type: b.type, pose: 'backaway', k: b.k, facing: -1, t: b.t, sweat: 2, lines: 1, lean: b.lean, rim: rimWarm, spearLen: b.spearLen, tint: i ? null : { color: '#0B0F12', amount: 0.06 } });
          // little scramble streaks behind the heels (toward screen-right: the direction they move)
          for (let j = 0; j < 3; j++) {
            const yy = b.y - (18 + j * 16) * b.sc, x0 = b.x + (95 + j * 8) * b.sc;
            S.strip(g, [[x0, yy], [x0 + (46 - j * 8) * b.sc, yy]], u => 3.2 * b.sc * Math.sin(Math.PI * u), 'rgba(230,236,240,0.45)');
          }
        });
        // ---- Mimiku, airborne over the knocker: the open mouth right over the helm
        const sm = s * 1.3;
        const mx = helm.x - R.mdx * W0 * sm, pivot = [mx, gy - 2.62 * W0 * sm];
        const helmLocal = rotAbout([helm.x, helm.y], pivot, -ROT);
        const po = pounceOpts(mx, gy, sm, helmLocal);
        const anL = M.anchors(mx, gy, sm, po);
        const an0 = { hip: rotAbout(anL.hip, pivot, ROT), mouth: rotAbout(anL.mouth, pivot, ROT), feet: Object.fromEntries(Object.entries(anL.feet).map(([k, q]) => [k, rotAbout(q, pivot, ROT)])) };
        window.RULE10_DBG = { helm, mouth: an0.mouth, feet: an0.feet, lidTop: rotAbout(anL.lidTop, pivot, ROT), bounds: anL.bounds };
        // burst streaks: from the floor spot where the chest sat, up into the dive (behind the character)
        g.save();
        const floorX = kx - K.chestDX('hammer') * s, hipC = an0.hip, r = S.rng('rule10-burst');
        for (let i = 0; i < 4; i++) {
          const off = (i - 1.5) * 30 * s;
          const p0 = [floorX - 20 * s + off * 0.6, gy - 30 * s];
          const p2 = [hipC[0] - 150 * s + off, hipC[1] + 60 * s + off * 0.8];
          const p1 = [p0[0] - 110 * s + off, (p0[1] + p2[1]) / 2 - 10 * s];
          const pts = [];
          for (let k = 0; k <= 16; k++) { const u = k / 16, a = (1 - u) * (1 - u), b = 2 * u * (1 - u), cc = u * u; pts.push([a * p0[0] + b * p1[0] + cc * p2[0], a * p0[1] + b * p1[1] + cc * p2[1]]); }
          const seg = pts.slice(Math.floor(r.range(2, 5)), 15 - Math.floor(r.range(0, 3)));
          S.strip(g, seg, u => (3 + 7 * u) * s, `rgba(255,240,205,${0.2 + 0.06 * i})`);
        }
        g.restore();
        dust(g, floorX - 10 * s, gy - 4, s * 1.2, 5, 'r10-floor', 0.35);
        S.groundShadow(g, (mx + kx) / 2, gy + 4, 1.7 * W0 * s, 0.26 * W0 * s, 0.34);
        // ---- the knocker under the dive, then Mimiku over him
        K.draw(g, kx, gy, s, ko);
        g.save(); g.translate(pivot[0], pivot[1]); g.rotate(ROT); g.translate(-pivot[0], -pivot[1]);
        M.draw(g, mx, gy, sm, po);
        g.restore();
      },
      post: { vignette: 0.66, vigX: 980, vigY: 600 },
      screen: (g) => {
        // ---- inset (top-right, over the dark arch top): Helen's screen face, pleased, APPROVED stamped across it
        const iw = 340, ih = 264, ix = 1920 - iw - 52, iy = 44;
        S.shadowGroup(g, gg => {
          S.roundRect(gg, ix, iy, iw, ih, 26, '#E8DCC8');
          S.roundRect(gg, ix + 10, iy + 10, iw - 20, ih - 20, 18, '#1B2228');
        }, { scale: 1.2 });
        S.clip(g, cc => S.addRoundRect(cc, ix + 10, iy + 10, iw - 20, ih - 20, 18), gg => {
          const rg = gg.createRadialGradient(ix + iw / 2, iy + ih * 0.5, 10, ix + iw / 2, iy + ih * 0.5, iw * 0.7);
          rg.addColorStop(0, '#2E4148'); rg.addColorStop(1, '#151C21');
          gg.fillStyle = rg; gg.fillRect(ix, iy, iw, ih);
          HL.drawHead(gg, ix + iw / 2 - 6, iy + ih - 20, 1.52, { face: 'pleased', t: 1.2, blink: 1, bloom: 0.9, headTilt: -6, antenna: { ang: 30, still: true } });
        });
        g.save(); g.translate(ix + iw - 88, iy + ih - 38); g.scale(4.2, 4.2);
        HL.stampMark(g, 0, 0, 62, 'APPROVED', -0.2);
        g.restore();
        S.label(g, 'RULE 10', ix + 16, iy + ih + 34, 26, { align: 'left', color: '#FFD978', weight: 900, bg: 'rgba(12,15,20,0.72)', pad: 0.4 });
      },
    });
  };
})();
