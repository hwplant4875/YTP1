// Nvidia (beats 4-6). S3: the tower behind the keyhole, one share's price tag drops 9.3%, the top
// 9.3% of the tower ($450B) breaks off and turns into bills. S4: the cash inside is untouched; the
// tower is 242 share cubes (1 cube = 100M shares); price x shares; all cubes drop at once.
// S5: only 3 cubes (1 in 80) traded, yet every cube is re-priced at the agreed price.
import { W, H, C30, Cam, rgb, css, mix, poly, box, pin, dashedBox, camPath, applyCam, bigText, clamp, lerp, sstep, smoother, easeOut, easeIn, backOut, discZ, HL } from '../iso.js';
import { COL, T, paper, lattice, board, bundle, pile, chipTop, dataCenter, tag, routePts, routeAt, routeDraw } from '../objects.js';
import { cue } from '../cue.js';

const N = 242, LAY = 27;
const SLOTS = [];
for (let L = 0; L < LAY; L++) for (let m = 0; m < 9; m++) { if (L === LAY - 1 && m === 0) continue; SLOTS.push([(m % 3) - 1, Math.floor(m / 3) - 1, L]); }
const GRID = (n) => [((n % 11) - 5) * 1.25, (Math.floor(n / 11) - 10.5) * 1.25, 0];
const TRADED = [5 * 11 + 3, 12 * 11 + 7, 17 * 11 + 2];
const easeIO = (u) => smoother(u);
const RED = '#C8503E';

export class Nvidia {
  constructor() { this.cam = new Cam(); }
  init() {
    const a = (w, n) => cue('b04', w, n), b = (w, n) => cue('b05', w, n), c = (w, n) => cue('b06', w, n);
    const S = this.S = {};
    // S3
    S.peek = a('peek'); S.nv = a('Nvidia'); S.chip = a('chip'); S.whose = a('whose'); S.ai = a('AI');
    S.wed = a('Wednesday'); S.share = a('share'); S.two = a('two'); S.thu = a("Thursday's"); S.e82 = a('eighty-two');
    S.drop = a('drop'); S.big = a('biggest'); S.because = a('Because'); S.valuable = a('valuable');
    S.nine2 = a('nine', 2); S.nearly = a('nearly'); S.fifty = a('fifty'); S.which = a('which'); S.bills = a('bills');
    // S4
    S.but = b('But'); S.cut = b('Nvidia'); S.didnt = b("didn't"); S.cash = b('cash'); S.see = b('see'); S.value = b('value');
    S.mult = b('multiplication'); S.price = b('price'); S.single = b('single', 2); S.times = b('times'); S.every = b('every');
    S.tw = b('twenty-four'); S.shares = b('shares'); S.drops = b('drops'); S.e18 = b('eighteen'); S.whole = b('whole');
    S.e18b = b('eighteen', 2); S.times2 = b('times', 2); S.bil2 = b('billion', 2); S.once = b('once');
    // S5
    S.and6 = c('And'); S.thurs6 = c('Thursday'); S.three = c('three'); S.changed = c('changed'); S.tw6 = c('twenty-four');
    S.one = c('one'); S.other = c('other'); S.re = c('repriced'); S.lower = c('lower'); S.buyer = c('buyer'); S.seller = c('seller');
    S.agree = c('agree'); S.becomes = c('becomes'); S.end6 = cue('b06', 'share', 3) + 0.6;
    S.fly = S.value + 0.55;
    this.cam3 = camPath([
      [S.peek, 0, 0, 13.5, 33], [S.nv, 0, 1.2, 14.0, 38], [S.whose + 0.3, 0.5, 0.8, 11, 44], [S.ai + 0.6, 0.5, 0.8, 11, 44],
      [S.share, -0.9, 5.3, 1.9, 9.5], [S.drop + 0.4, -0.9, 5.2, 1.8, 9.0], [S.because, -0.9, 5.2, 1.8, 8.6],
      [S.valuable + 0.4, 0, 2.6, 14.0, 40], [S.fifty, 0, 2.8, 13.5, 40], [S.bills + 0.6, 0, 4.6, 4.0, 18],
    ]);
    const drift = (k) => Object.assign(k, { lin: true }); // slow linear push-in through the long grid hold
    this.cam4 = camPath([
      [S.but - 0.6, 0, 0, 13.5, 36], [S.cut + 0.3, 0.6, 0.6, 4.2, 15], [S.see + 0.3, 0.6, 0.6, 4.2, 15],
      [S.value, 0, 0, 13, 37], drift([S.fly + 1.4, -1.6, 2.4, 0.4, 31.5, 1180, 705]), [S.lower + 1.0, -1.6, 2.4, 0.4, 29.8, 1180, 705],
      [S.buyer - 0.5, ...this.gpos(TRADED[1], 0.6), 12, W / 2, H / 2 + 60], [S.becomes + 0.3, ...this.gpos(TRADED[1], 0.6), 12, W / 2, H / 2 + 60],
      [S.end6, -1.6, 2.4, 0.4, 31.5, 1180, 705],
    ]);
    // routes
    this.r1 = routePts([[0.1, 1.2, 0.02], [-0.2, 3.8, 0.02], [-0.5, 6.2, 0.02]]);
    this.slabR = routePts([[0, 0, 27.4], [0, 3.4, 27.0], [0, 6.2, 8], [0, 6.4, 0]]);
    this.dcs = [[3.4, -11.6, 3.4, 4.2], [-6.6, 6.2, 3.4, 4.2], [3.6, 8.4, 3.4, 4.0]];
    this.dcR = this.dcs.map(([x, y, sx, sy]) => routePts([[0.6 * Math.sign(x + 0.01), 0.6 * Math.sign(y), 0.05], [(x + sx / 2) * 0.5, (y + sy / 2) * 0.5, 0.05], [x + sx / 2, y + sy / 2, 0.05]]));
  }
  gpos(n, z = 0) { const g = GRID(n); return [g[0], g[1], z]; }

  render(ctx, t) {
    const S = this.S, cam = this.cam;
    const s3 = t < S.but - 1;
    applyCam(cam, s3 ? this.cam3(t) : this.cam4(t));
    paper(ctx); lattice(ctx, cam, 1, -2.6);
    board(ctx, cam, -7.6, -14.6, 15.2, 29.2, 1.4, { lift: 1.2 });
    if (s3) this.drawS3(ctx, t); else this.drawS45(ctx, t);
  }

  // ---------- tower ----------
  towerSolid(ctx, x0, z0, h, o = {}) {
    // one box with faint seams every cube layer, a chip roof, optional coral cap
    const cam = this.cam, Tn = T(COL.nvda);
    box(ctx, cam, -1.5, -1.5, z0, 3, 3, h, Tn, 0.7);
    ctx.save(); ctx.strokeStyle = 'rgba(30,22,60,0.18)'; ctx.lineWidth = 1; ctx.beginPath();
    const lh = o.lh || 1;
    for (let z = z0 + lh; z < z0 + h - 0.01; z += lh) {
      const p1 = cam.p(1.5, -1.5, z), p2 = cam.p(1.5, 1.5, z), p3 = cam.p(-1.5, 1.5, z);
      ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.lineTo(p3[0], p3[1]);
    }
    for (const v of [-0.5, 0.5]) {
      const a1 = cam.p(1.5, v, z0), a2 = cam.p(1.5, v, z0 + h); ctx.moveTo(a1[0], a1[1]); ctx.lineTo(a2[0], a2[1]);
      const b1 = cam.p(v, 1.5, z0), b2 = cam.p(v, 1.5, z0 + h); ctx.moveTo(b1[0], b1[1]); ctx.lineTo(b2[0], b2[1]);
    }
    ctx.stroke(); ctx.restore();
    if (!o.noChip) chipTop(ctx, cam, -1.5, -1.5, z0 + h, 3, 3, 1);
  }

  drawS3(ctx, t) {
    const S = this.S, cam = this.cam;
    // data centres the chips run in, with packets flowing out along routes
    const dcR = backOut(clamp((t - S.whose) / 0.5)) * (1 - easeIn(clamp((t - S.wed) / 0.6)));
    if (dcR > 0.001) {
      for (let i = 0; i < 3; i++) {
        const R = this.dcR[i], lu = easeOut(clamp((t - S.whose - 0.1 * i) / 0.5));
        routeDraw(ctx, cam, R, 0, lu, { dash: [8, 6], offset: -t * 30, lw: 2, a: dcR > 0.99 ? 1 : dcR });
        for (let n = 0; n < 14; n++) {
          const u = ((t - S.whose - 0.4) * 0.7 - n / 14) % 1;
          if (t - S.whose - 0.4 < n / 14 / 0.7 || u < 0) continue;
          const p = routeAt(R, u);
          discZ(ctx, cam, p[0], p[1], p[2] + 0.05, 0.28, 'rgba(127,227,240,0.35)');
          discZ(ctx, cam, p[0], p[1], p[2] + 0.06, 0.13, '#3FC6DA');
        }
      }
    }
    // the slab of lost value: coral cap -> breaks off -> lands -> turns into bundles
    const tC = S.nine2, tLift = S.nearly - 0.1, tLand = S.fifty - 0.15;
    const capH = 27 * 0.093;
    const lift = clamp((t - tLift) / (tLand - tLift));
    let slab = null;
    if (t > tLift) {
      const p = routeAt(this.slabR, easeIO(lift)), sq = t > tLand ? 1 - 0.18 * Math.sin(Math.PI * clamp((t - tLand) / 0.16)) : 1;
      slab = [p[0], p[1], p[2], sq];
    }
    const towerH = t > tLift ? 27 - capH : 27;
    const drawDC = (i) => { const [x, y, sx, sy] = this.dcs[i]; if (dcR > 0.001) dataCenter(ctx, cam, x, y, sx, sy, 1.7, { rise: dcR }); };
    drawDC(0);
    this.towerSolid(ctx, 0, 0, towerH, { noChip: t > tLift });
    drawDC(1); drawDC(2);
    if (t <= tLift) {
      const cA = clamp((t - tC) / 0.25);
      if (cA > 0) { ctx.save(); ctx.globalAlpha = cA; box(ctx, cam, -1.5, -1.5, 27 - capH, 3, 3, capH, T(COL.loss), 0.5); ctx.restore(); }
    } else {
      dashedBox(ctx, cam, -1.5, -1.5, towerH, 3, 3, capH, { a: clamp((t - tLift) / 0.3), lw: 2, dash: [8, 6], noBottom: true });
    }
    // one share: a white cube slides out along a line, a tag hangs from it, the price drops
    const sOut = clamp((t - S.wed - 0.15) / 0.8), rLine = easeOut(clamp((t - S.wed) / 0.5));
    const sBack = clamp((t - S.because - 0.1) / 0.7);
    if (t > S.wed && sBack < 1) {
      const lineA = Math.max(1 - clamp((t - S.share - 0.2) / 0.5), clamp((t - S.because) / 0.2)) * (1 - sBack);
      routeDraw(ctx, cam, this.r1, 0, rLine, { dash: [7, 5], lw: 2, a: lineA });
      const u = sBack > 0 ? 1 - easeIO(sBack) : easeIO(sOut), p = routeAt(this.r1, u);
      const land = S.wed + 0.95, sq = t > land && t < land + 0.2 ? 1 - 0.18 * Math.sin(Math.PI * (t - land) / 0.16) : 1;
      const drop = easeOut(clamp((t - S.e82 - 0.15) / 0.35)), hs = 1 - 0.093 * drop;
      box(ctx, cam, p[0] - 0.5, p[1] - 0.5, 0, 1, 1, hs * sq, T('#F4F1EA'), 0.6);
      const coral = clamp((t - S.e82) / 0.1) * (1 - clamp((t - S.e82 - 0.35) / 0.25));
      if (coral > 0) { ctx.save(); ctx.globalAlpha = coral; box(ctx, cam, p[0] - 0.5, p[1] - 0.5, hs, 1, 1, 1 - hs, T(COL.loss), 0.4); ctx.restore(); }
      if (drop > 0) dashedBox(ctx, cam, p[0] - 0.5, p[1] - 0.5, hs, 1, 1, 0.093, { a: clamp((t - S.e82 - 0.2) / 0.1) * (1 - sBack), lw: 1.6, dash: [5, 4], noBottom: true });
      // tag
      const flip = clamp((t - S.thu - 0.05) / 0.45);
      tag(ctx, cam, p[0] - 0.45, p[1] + 0.5, hs * sq, 3.4, '$200.13', '$181.60', { p: clamp((t - S.two + 0.4) / 0.5) * (1 - sBack), flip, subA: 'Wednesday close', subB: 'Thursday close', drop: 0.18, dx: 0.05, swing: 0.04 * Math.sin((t - S.two) * 3) * Math.exp(-(t - S.two) * 1.2) });
      if (sOut > 0.6 && t < S.e82 + 0.3) {
        const [x, y] = cam.p(p[0] + 0.5, p[1] - 0.5, 1);
        pin(ctx, x, y, { ink: COL.ink, paper: COL.paper, halo: COL.paper, p: clamp((t - S.share) / 0.5), a: 1 - clamp((t - S.e82) / 0.3), dir: -1, lead: 120, rule: 250, title: 'One Nvidia share', titleSize: 28 });
      }
      if (t > S.drop - 0.2) {
        const [x, y] = cam.p(p[0] + 0.5, p[1] - 0.5, 0.95);
        pin(ctx, x, y, { ink: COL.ink, paper: COL.paper, halo: COL.paper, p: 1, tp: clamp((t - S.drop) / 0.4), ttp: clamp((t - S.big) / 0.4), a: 1 - clamp((t - S.because) / 0.3), dir: -1, lead: 120, rule: 250, num: '−9.3%', numColor: RED, title: 'Biggest drop since April 2025', numSize: 96, titleSize: 22 });
      }
    }
    // slab and its bundles
    if (slab) {
      const [x, y, z, sq] = slab, wipe = clamp((t - S.which) / Math.max(0.3, S.bills - S.which + 0.3));
      const hS = capH * sq;
      if (wipe < 1) { ctx.save(); box(ctx, cam, x - 1.5, y - 1.5, z + hS * wipe, 3, 3, hS * (1 - wipe), T(COL.loss), 0.6); ctx.restore(); }
      if (wipe > 0) {
        // bundles stack up layer by layer as the coral slab above them gives way
        const nz = Math.round(capH / (0.010922 * 15));
        pile(ctx, cam, x, y, z, 15, 3, 1, Math.max(1, Math.round(nz * wipe)), { seed: 7 });
      }
    }
    // pins on the tower
    const pc = { ink: COL.ink, paper: COL.paper, halo: COL.paper };
    if (t > S.nv - 0.3 && t < S.wed + 0.5) {
      const [x, y] = cam.p(-1.2, 1.5, 21);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.nv + 0.25) / 0.6), ttp: clamp((t - S.chip) / 0.4), a: 1 - clamp((t - S.wed) / 0.4), dir: 1, lead: 40, rule: 330, off: 26, num: 'NVIDIA', title: 'Chip maker behind today’s AI', numSize: 96, titleSize: 28 });
    }
    if (t > S.valuable - 0.3 && t < S.nearly + 0.5) {
      const [x, y] = cam.p(-1.2, 1.5, 20);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.valuable + 0.2) / 0.6), a: 1 - clamp((t - S.nearly) / 0.4), dir: 1, lead: 40, rule: 360, off: 26, num: '$4.8', unit: 'TRILLION', title: 'Nvidia’s value, Wednesday', numSize: 96, titleSize: 28 });
    }
    // the lost value in one number
    if (t > S.fifty - 0.1) {   // right of the tower, two lines, so the text never crosses it
      bigText(ctx, 'NEARLY', W * 0.72, 330, { size: 112, p: clamp((t - S.fifty + 0.1) / 0.45) });
      bigText(ctx, [['$450 BILLION', HL]], W * 0.72, 330 + 138, { size: 124, p: clamp((t - S.fifty) / 0.45) });
    }
  }

  // ---------- S4 + S5: cash inside, cubes, price x shares, re-pricing ----------
  cubeState(n, t) {
    const S = this.S, s = SLOTS[n], g = GRID(n);
    const e = easeOut(clamp((t - S.value) / 0.5));
    const ex = [s[0] * (1 + e * 0.75), s[1] * (1 + e * 0.75), s[2] * (1 + e * 0.3) + e * 0.6];
    const L = s[2], ts = S.fly + (LAY - 1 - L) / (LAY - 1) * 1.25 + ((n * 7) % 9) * 0.015, u = clamp((t - ts) / 0.72);
    let x, y, z, sq = 1;
    if (u <= 0) { x = ex[0]; y = ex[1]; z = ex[2]; }
    else {
      const k = easeIO(u);
      x = lerp(ex[0], g[0], k); y = lerp(ex[1], g[1], k); z = lerp(ex[2], g[2], k) + Math.sin(Math.PI * k) * 3.0;
      if (u >= 1) { const v = (t - ts - 0.72) / 0.16; if (v < 1) sq = 1 - 0.18 * Math.sin(Math.PI * v); }
    }
    return { x, y, z, sq, landed: u >= 1, ts };
  }
  heightFactor(n, t) {
    // 1.0 = Wednesday price; 0.907 = Thursday price
    const S = this.S;
    const g = GRID(n);
    // all at once (S4)
    let f = 1, coral = 0, ghost = 0;
    const tA = S.once;
    if (t > tA && t < S.and6 + 1.2) {
      const q = easeOut(clamp((t - tA - 0.12) / 0.3)); f = 1 - 0.093 * q;
      coral = clamp((t - tA) / 0.08) * (1 - clamp((t - tA - 0.3) / 0.25)); ghost = clamp((t - tA - 0.15) / 0.1);
      // rewind for beat 6
      const rw = easeIO(clamp((t - S.and6 - 0.2) / 0.8)); f = lerp(f, 1, rw); ghost *= 1 - rw;
    }
    // re-priced wave from the traded cubes (S5)
    if (t > S.re - 0.3) {
      let d = 1e9; for (const m of TRADED) { const h = GRID(m); d = Math.min(d, Math.hypot(g[0] - h[0], g[1] - h[1])); }
      const tw = S.re + d * 0.055, q = easeOut(clamp((t - tw - 0.1) / 0.3));
      if (t > tw) { f = 1 - 0.093 * q; coral = clamp((t - tw) / 0.08) * (1 - clamp((t - tw - 0.3) / 0.25)); ghost = clamp((t - tw - 0.15) / 0.1) * (1 - clamp((t - S.becomes - 0.6) / 0.6)); }
    }
    return { f, coral, ghost };
  }
  drawS45(ctx, t) {
    const S = this.S, cam = this.cam, pc = { ink: COL.ink, paper: COL.paper, halo: COL.paper };
    const exploded = t > S.value;
    if (!exploded) {
      // cutaway of the lower tower: dashed cut lines, the front skin rolls down, cash inside
      const cutL = clamp((t - S.cut) / 0.6), roll = easeIO(clamp((t - S.didnt) / 0.7)) * (1 - easeIO(clamp((t - S.see) / 0.6)));
      const R = 8;
      if (roll > 0.001) {
        const Tn = T(COL.nvda), dark = css(mix(rgb(COL.nvda), [20, 14, 40], 0.45)), darker = css(mix(rgb(COL.nvda), [20, 14, 40], 0.6));
        // inner back walls and floor
        poly(ctx, cam, [[-1.38, -1.38, 0], [-1.38, 1.5, 0], [-1.38, 1.5, R], [-1.38, -1.38, R]], dark);
        poly(ctx, cam, [[-1.38, -1.38, 0], [1.5, -1.38, 0], [1.5, -1.38, R], [-1.38, -1.38, R]], darker);
        poly(ctx, cam, [[-1.38, -1.38, 0.02], [1.5, -1.38, 0.02], [1.5, 1.5, 0.02], [-1.38, 1.5, 0.02]], '#D9D2E8');
        // the company's cash, untouched
        pile(ctx, cam, -0.55, -0.35, 0.03, 9.5, 2, 1, 22, { seed: 11 });
        pile(ctx, cam, 0.75, 0.55, 0.03, 9.5, 2, 1, 14, { seed: 12 });
        // remaining skin (rolling down into the floor)
        const hS = R * (1 - roll);
        if (hS > 0.01) {
          poly(ctx, cam, [[1.5, -1.5, 0], [1.5, 1.5, 0], [1.5, 1.5, hS], [1.5, -1.5, hS]], Tn.left);
          poly(ctx, cam, [[-1.5, 1.5, 0], [1.5, 1.5, 0], [1.5, 1.5, hS], [-1.5, 1.5, hS]], Tn.right);
        }
        // upper tower
        this.towerSolid(ctx, 0, R, 27 - R);
        // ceiling edge
        poly(ctx, cam, [[1.5, -1.5, R - 0.12], [1.5, 1.5, R - 0.12], [1.5, 1.5, R], [1.5, -1.5, R]], css(mix(rgb(COL.nvda), [255, 248, 236], 0.25)));
        poly(ctx, cam, [[-1.5, 1.5, R - 0.12], [1.5, 1.5, R - 0.12], [1.5, 1.5, R], [-1.5, 1.5, R]], css(mix(rgb(COL.nvda), [255, 248, 236], 0.1)));
      } else this.towerSolid(ctx, 0, 0, 27);
      if (cutL > 0 && roll < 0.999) {
        ctx.save(); ctx.strokeStyle = COL.ink; ctx.lineWidth = 2.4; ctx.setLineDash([9, 7]); ctx.lineDashOffset = -t * 25;
        ctx.globalAlpha = 1 - clamp((t - S.see - 0.5) / 0.3);
        const pts = [[1.5, -1.5, 0.15], [1.5, -1.5, R], [1.5, 1.5, R], [-1.5, 1.5, R], [-1.5, 1.5, 0.15]];
        ctx.beginPath(); const n = 60;
        for (let i = 0; i <= n * cutL; i++) {
          const f = i / n * (pts.length - 1), j = Math.min(pts.length - 2, Math.floor(f)), w = f - j;
          const q = [lerp(pts[j][0], pts[j + 1][0], w), lerp(pts[j][1], pts[j + 1][1], w), lerp(pts[j][2], pts[j + 1][2], w)], [x, y] = cam.p(...q);
          if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
        }
        ctx.stroke(); ctx.restore();
      }
      if (t > S.cash - 0.3 && t < S.see + 0.6) {
        const [x, y] = cam.p(-0.55, -0.35, 2.6);
        pin(ctx, x, y, { ...pc, p: clamp((t - S.cash + 0.2) / 0.6), a: 1 - clamp((t - S.see) / 0.4), dir: -1, lead: 150, rule: 560, off: 230, num: '$0', title: 'Cash Nvidia lost that day', numSize: 110, titleSize: 30 });
      }
    } else {
      // cubes: exploded tower -> grid; drawn back to front
      const list = [];
      for (let n = 0; n < N; n++) {
        const st = this.cubeState(n, t), hf = this.heightFactor(n, t);
        list.push([st.x + st.y + st.z * 0.9, n, st, hf]);
      }
      list.sort((a, b) => a[0] - b[0]);
      const trA = clamp((t - S.three + 0.1) / 0.35), dim = sstep(S.other - 0.1, S.other + 0.5, t) * (1 - sstep(S.re - 0.2, S.re + 0.6, t));
      const ripple = (n) => { const g = GRID(n), d = Math.hypot(g[0] + 6.25, g[1] + 13.1); const u = (t - S.every - d * 0.03) / 0.35; return u > 0 && u < 1 ? Math.sin(Math.PI * u) * 0.5 : 0; };
      for (const [, n, st, hf] of list) {
        const traded = TRADED.includes(n);
        let base = rgb(COL.nvda);
        if (traded && trA > 0) base = mix(base, rgb('#F2C230'), trA);
        else if (dim > 0) base = mix(base, rgb('#E6DEF0'), dim * 0.55);
        const Tc = { top: css(mix(base, [255, 248, 236], 0.22)), left: css(base), right: css(mix(base, [35, 26, 44], 0.24)) };
        let z = st.z + ripple(n);
        if (traded && t > S.changed - 0.1) { const u = clamp((t - S.changed - TRADED.indexOf(n) * 0.12) / 0.75); z += Math.sin(Math.PI * u) * 2.2; }
        if (traded && t > S.three - 0.1 && t < S.changed) z += backOut(clamp((t - S.three) / 0.3)) * 0.35 * (1 - clamp((t - S.changed + 0.3) / 0.3));
        const h = hf.f * st.sq, w = 1 + (1 - st.sq) * 0.3;
        box(ctx, cam, st.x - w / 2, st.y - w / 2, z, w, w, h, Tc, 0.6);
        if (hf.coral > 0) { ctx.save(); ctx.globalAlpha = hf.coral; box(ctx, cam, st.x - 0.5, st.y - 0.5, z + h, 1, 1, Math.max(0, 1 - h), T(COL.loss), 0.4); ctx.restore(); }
        if (hf.ghost > 0.01 && h < 0.999) dashedBox(ctx, cam, st.x - 0.5, st.y - 0.5, z + h, 1, 1, 1 - h, { a: hf.ghost, lw: 1.3, dash: [4, 3], noBottom: true });
      }
      // tags on every cube once the agreed price "becomes the price of every share"
      if (t > S.agree - 0.2) {
        const g0 = GRID(TRADED[1]);
        for (const [, n, st, hf] of list) {
          const g = GRID(n), d = Math.hypot(g[0] - g0[0], g[1] - g0[1]);
          const tp = n === TRADED[1] ? S.agree : S.becomes + d * 0.045;
          const p = clamp((t - tp) / 0.4);
          if (p <= 0) continue;
          tag(ctx, cam, st.x - 0.42, st.y + 0.5, hf.f, n === TRADED[1] ? 2.6 : 1.5, '$181.60', '$181.60', { p, subA: n === TRADED[1] ? 'agreed price' : '', drop: 0.2, dx: 0.05 });
        }
      }
    }
    this.drawS4Overlay(ctx, t, pc);
  }
  drawS4Overlay(ctx, t, pc) {
    const S = this.S, cam = this.cam;
    // one share (white cube on the paper, left of the grid) with its price tag
    const inA = clamp((t - S.price + 0.5) / 0.6), outA = clamp((t - S.and6 - 0.1) / 0.7);
    if (inA > 0 && outA < 1) {
      const bx = 4.4 + easeIn(outA) * 6, by = -19.6 - easeIn(outA) * 6, r = backOut(inA);
      const flip = clamp((t - S.drops - 0.05) / 0.45), drop = easeOut(clamp((t - S.drops - 0.25) / 0.35)), hs = 1 - 0.093 * drop;
      const Z = 1.5;   // one share drawn at 1.5x so its tag reads
      board(ctx, cam, bx - 1.9, by - 1.9, 3.8, 3.8, 0.7 * r, { lift: 0.9, shadow: 0.18 * r });
      box(ctx, cam, bx - Z / 2, by - Z / 2, 0, Z, Z, Z * hs * r, T('#F4F1EA'), 0.6);
      if (drop > 0) dashedBox(ctx, cam, bx - Z / 2, by - Z / 2, Z * hs, Z, Z, Z * 0.093, { a: drop, lw: 1.6, dash: [5, 4], noBottom: true });
      tag(ctx, cam, bx - Z * 0.45, by + Z / 2, Z * hs * r, 8.0, '$200.13', '$181.60', { p: clamp((t - S.price) / 0.5), flip, subA: 'Wednesday close', subB: 'Thursday close', drop: 0.12, dx: 0.04 });
      const [x, y] = cam.p(bx + Z / 2, by - Z / 2, Z);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.price + 0.3) / 0.6), a: 1 - outA, ttp: clamp((t - S.price) / 0.4), tp: clamp((t - S.e18) / 0.4), dir: -1, lead: 110, rule: 210, num: '−$18.53', numColor: RED, title: 'One share', numSize: 72, titleSize: 30 });
    }
    // legend + totals on the grid
    const gA = 1 - clamp((t - S.one + 0.2) / 0.4);
    if (t > S.every - 0.2 && t < S.drops) {
      const [x, y] = cam.p(...this.gpos(65, 0.5));
      pin(ctx, x, y, { ...pc, p: clamp((t - S.every) / 0.6), a: 1 - clamp((t - S.drops + 0.4) / 0.4), ttp: clamp((t - S.every) / 0.5), tp: clamp((t - S.tw) / 0.4), dir: -1, lead: -150, rule: 400, num: '24.2', unit: 'BILLION SHARES', title: '1 cube = 100 million shares', numSize: 84, titleSize: 28 });
    }
    if (t > S.three - 0.2 && gA > 0) {
      const [x, y] = cam.p(...this.gpos(TRADED[0], 1.4));
      pin(ctx, x, y, { ...pc, p: clamp((t - S.three + 0.1) / 0.6), a: gA, dir: 1, lead: 120, rule: 320, num: '306', unit: 'MILLION', title: 'Nvidia shares traded Nov 5', numSize: 84, titleSize: 28 });
    }
    if (t > S.tw6 - 0.2 && gA > 0) {
      const [x, y] = cam.p(...this.gpos(241, 1));
      pin(ctx, x, y, { ...pc, p: clamp((t - S.tw6 + 0.1) / 0.6), a: gA, dir: 1, lead: 165, rule: 320, num: '24.2', unit: 'BILLION', title: 'Nvidia shares in total', numSize: 84, titleSize: 28 });
    }
    // buyer and seller around the traded cube
    if (t > S.buyer - 0.3 && t < S.becomes + 1.0) {
      const g = GRID(TRADED[1]), fa = 1 - clamp((t - S.becomes - 0.4) / 0.5);
      const [x1, y1] = cam.p(g[0] + 0.5, g[1] - 0.5, 0.5), [x2, y2] = cam.p(g[0] - 0.5, g[1] + 0.5, 0.5);
      pin(ctx, x1, y1, { ...pc, p: clamp((t - S.buyer + 0.1) / 0.5), a: fa, dir: -1, lead: -90, rule: 200, title: 'Buyer', titleSize: 34 });
      pin(ctx, x2, y2, { ...pc, p: clamp((t - S.seller + 0.1) / 0.5), a: fa, dir: 1, lead: -90, rule: 200, title: 'Seller', titleSize: 34 });
    }
    // equations
    const y0 = 150;
    if (t > S.price - 0.1 && t < S.drops + 0.5) {
      const a = 1 - clamp((t - S.drops) / 0.4);
      const parts = [['$200.13', '#FFFFFF']];
      if (t > S.times - 0.05) parts.push([' × ', '#FFFFFF']);
      if (t > S.tw - 0.05) parts.push(['24.2 BILLION', '#FFFFFF']);
      if (t > S.shares - 0.05) parts.push([' = ', '#FFFFFF'], ['$4.8 TRILLION', HL]);
      bigText(ctx, parts, W / 2, y0, { size: 84, p: 1, a });
    }
    if (t > S.e18b - 0.1 && t < S.and6 + 0.6) {
      const a = 1 - clamp((t - S.and6) / 0.4);
      const parts = [['-$18.53', '#FF8A73']];
      if (t > S.times2 - 0.05) parts.push([' × 24.2 BILLION', '#FFFFFF']);
      bigText(ctx, parts, W / 2, y0, { size: 84, p: 1, a });
      if (t > S.bil2 + 0.1) bigText(ctx, [['= ', '#FFFFFF'], ['-$448 BILLION', HL]], W / 2, y0 + 128, { size: 112, p: clamp((t - S.bil2 - 0.1) / 0.4), a });
    }
    if (t > S.one - 0.1 && t < S.re + 0.2) {
      bigText(ctx, [['1', HL], [' IN 80', '#FFFFFF']], W / 2, y0 + 20, { size: 150, p: clamp((t - S.one + 0.1) / 0.4), a: 1 - clamp((t - S.re + 0.2) / 0.4) });
    }
  }
}
