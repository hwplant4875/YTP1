// S2 (beat 3): the U.S. market as a board of 500 company blocks. It falls 4.4%, the chip makers
// light up, Qualcomm and Arm drop, a question hangs over the market and money pours into AI data
// centres. Then (beat 4 opening) the camera closes in on Nvidia for the PEEK keyhole.
import { W, H, C30, SQ15, Cam, tones, rgb, css, mix, poly, box, pin, dashedBox, camPath, applyCam, bigText, clamp, lerp, sstep, smoother, easeOut, easeIn, backOut, mulberry32, HL } from '../iso.js';
import { COL, T, paper, lattice, board, bundle, chipTop, dataCenter, tagTexture, routePts, routeAt, routeDraw } from '../objects.js';
import { cue } from '../cue.js';

const NX = 25, NY = 20, FP = 0.78;
const capOf = (rank) => 4.8 * Math.pow(rank, -0.8);                 // $ trillions, illustrative spread
const hOf = (rank) => 0.4 + 3.4 * Math.pow(capOf(rank), 0.55);
const inTech = (i, j) => i >= 3 && i <= 10 && j >= 4 && j <= 12;
const inChip = (i, j) => i >= 5 && i <= 8 && j >= 6 && j <= 9;
const NVDA = [5, 6], QCOM = [7, 9];

export class Market {
  constructor(mode = 'story') { this.mode = mode; this.cam = new Cam(); }
  init() {
    const rnd = mulberry32(1105);
    const cells = [];
    for (let i = 0; i < NX; i++) for (let j = 0; j < NY; j++) cells.push([i, j]);
    // ranks: Nvidia #1, chips drawn from the top 100, tech from the top 160, the rest from what is left
    const pool = []; for (let r = 2; r <= 500; r++) pool.push(r);
    const take = (maxRank) => { const c = pool.filter(r => r <= maxRank); const r = c[(rnd() * c.length) | 0]; pool.splice(pool.indexOf(r), 1); return r; };
    const B = [];
    const order = cells.slice().sort((a, b) => (inChip(...b) - inChip(...a)) || (inTech(...b) - inTech(...a)));
    for (const [i, j] of order) {
      let kind = inChip(i, j) ? 'chip' : inTech(i, j) ? 'tech' : 'other', rank;
      if (i === NVDA[0] && j === NVDA[1]) { kind = 'nvda'; rank = 1; }
      else if (kind === 'chip') rank = take(110);
      else if (kind === 'tech') rank = take(170);
      else rank = take(501);
      if (i === QCOM[0] && j === QCOM[1]) { kind = 'qcom'; rank = 60; }
      const base = kind === 'other' ? rgb(COL.grey[(rnd() * COL.grey.length) | 0])
        : kind === 'tech' ? mix(rgb(COL.tech), rgb('#FFFFFF'), rnd() * 0.25)
          : kind === 'nvda' ? rgb(COL.nvda) : mix(rgb(COL.chip), rgb('#FFFFFF'), rnd() * 0.12);
      const jx = (rnd() - 0.5) * 0.08, jy = (rnd() - 0.5) * 0.08;
      B.push({ i, j, kind, rank, h: hOf(rank) * (0.92 + rnd() * 0.16), base, x0: i + (1 - FP) / 2 + jx, y0: j + (1 - FP) / 2 + jy, jit: rnd() });
    }
    B.sort((a, b) => (a.i + a.j) - (b.i + b.j) || a.i - b.i);
    this.B = B;
    this.nv = B.find(b => b.kind === 'nvda'); this.qc = B.find(b => b.kind === 'qcom');
    this.arm = { x0: -2.4 - FP / 2, y0: 8.6 - FP / 2, h: hOf(70) * 1.05, base: mix(rgb(COL.chip), rgb('#FFFFFF'), 0.05) };
    // cue times
    const c = (w, n) => cue('b03', w, n);
    this.tDate = c('Thursday'); this.tSP = c('S'); this.tCity0 = c("Here's") + 0.05; this.tCity1 = this.tSP; this.tPop0 = c('The'); this.tPop1 = c('companies');
    this.tFell = c('fell'); this.tTech = c('tech-heavy'); this.tNas = c('Nasdaq'); this.tAnalysts = c('Analysts');
    this.tChips = c('chips'); this.tQ = c('Qualcomm'); this.tArm = c('Arm'); this.tDis = c('disappointed');
    this.tQuest = c('question'); this.tHuge = c('huge'); this.tSums = c('sums'); this.tAI = c('AI'); this.tDC = c('centers'); this.tPay = c('pay');
    const d = (w, n) => cue('b04', w, n);
    this.tFind = d('To'); this.tPeek = d('peek');
    // camera: [t, x, y, z, frame height]
    this.camAt = camPath([
      [this.tDate - 3.5, 12.0, 10.6, 1.2, 31],
      [this.tPop1, 12.0, 10.4, 1.4, 28.5],
      [this.tTech - 0.2, 12.0, 10.4, 1.4, 28.5],
      [this.tAnalysts, 8.5, 9.5, 2.0, 21],
      [this.tChips + 0.2, 6.6, 7.6, 2.2, 12.5],
      [this.tArm + 0.3, 4.2, 7.4, 2.0, 13.5],
      [this.tDis + 1.6, 4.4, 7.6, 2.0, 13.5],
      [this.tQuest + 0.9, 9.5, 15.5, 2.0, 33],
      [this.tPay + 0.6, 9.5, 15.2, 2.0, 32],
      [this.tPeek - 0.1, 5.6, 6.5, 5.5, 7.0],
      [this.tPeek + 2, 5.6, 6.5, 6.0, 5.5],
    ]);
    // money route from the tech district to the data centre
    this.dc = { x0: 3.6, y0: 23.6, sx: 5.2, sy: 6.4, h: 2.4 };
    this.route = routePts([[9.6, 12.4, 0.35], [9.4, 17.0, 1.4], [8.4, 21.0, 2.2], [7.2, 24.6, 2.6]]);
  }
  // screen position of the Nvidia block's right face (where the keyhole opens)
  nvidiaScreen(t) {
    applyCam(this.cam, this.camAt(t));
    const b = this.nv; return this.cam.p(b.x0 + FP * 0.5, b.y0 + FP, b.h * 0.62);
  }
  heightAt(b, t) {
    // pop-in wave (back to front) while the date is said, then the 4.4% drop wave, then bigger drops for Qualcomm and Arm
    const tp = this.tCity0 + 0.15 + ((b.i + b.j) / 43) * (this.tCity1 - this.tCity0 - 0.5) + b.jit * 0.12;
    const r = backOut(clamp((t - tp) / 0.38));
    const td = this.tFell + 0.05 + ((b.i + b.j) / 43) * 0.45;
    let f = 1 - 0.044 * easeOut((t - td - 0.22) / 0.35), g = 0, gH = 0, coral = 0;
    if (t > td) { coral = clamp((t - td) / 0.12) * (1 - clamp((t - td - 0.3) / 0.25)); g = clamp((t - td - 0.2) / 0.1) * (1 - clamp((t - td - 1.3) / 0.8)); gH = 0.044; }
    if (b.kind === 'qcom') {
      const tq = this.tDis + 0.1, q = easeOut((t - tq - 0.22) / 0.35);
      if (t > tq) { f = 1 - 0.044 - (0.095 - 0.044) * q; coral = clamp((t - tq) / 0.12) * (1 - clamp((t - tq - 0.3) / 0.25)); g = clamp((t - tq - 0.2) / 0.1) * (1 - clamp((t - tq - 2.6) / 0.8)); gH = 0.095; }
    }
    return { r, f, g, gH, coral, td };
  }
  render(ctx, t) {
    const cam = this.cam;
    applyCam(cam, this.camAt(t));
    paper(ctx); lattice(ctx, cam, 1, -2.6);
    board(ctx, cam, -0.6, -0.6, NX + 1.2, NY + 1.2, 1.2, { lift: 1.4 });
    // focus: everything but tech fades at "tech-heavy"; tech fades too at "chips"; all but Nvidia before the keyhole
    const fadeO = sstep(this.tTech, this.tTech + 0.6, t) * 0.55, fadeT = sstep(this.tChips - 0.1, this.tChips + 0.5, t) * 0.5;
    const fadeN = sstep(this.tFind, this.tFind + 1.2, t) * 0.6, chipOn = sstep(this.tChips - 0.1, this.tChips + 0.25, t);
    const P = rgb('#EFE7D7');
    const ghosts = [];
    for (const b of this.B) {
      const s = this.heightAt(b, t);
      if (s.r <= 0.001) continue;
      let fade = b.kind === 'other' ? fadeO : b.kind === 'tech' ? Math.max(fadeO * 0.15, fadeT) : 0;
      if (b.kind !== 'nvda') fade = Math.max(fade, fadeN);
      const col = mix(b.base, P, fade), Tb = { top: css(mix(col, [255, 248, 236], 0.2)), left: css(col), right: css(mix(col, [35, 26, 44], 0.22)) };
      const h = b.h * s.r * s.f, full = b.h * s.r;
      const chipBump = (b.kind === 'chip' || b.kind === 'qcom' || b.kind === 'nvda') ? Math.sin(Math.PI * clamp((t - this.tChips - 0.02 * (b.i + b.j - 11)) / 0.3)) * 0.25 : 0;
      box(ctx, cam, b.x0, b.y0, chipBump, FP, FP, h, Tb, 0.6);
      if (s.coral > 0) { ctx.save(); ctx.globalAlpha = s.coral; box(ctx, cam, b.x0, b.y0, chipBump + h, FP, FP, full - h, T(COL.loss), 0.4); ctx.restore(); }
      if ((b.kind === 'chip' || b.kind === 'qcom' || b.kind === 'nvda') && chipOn > 0) chipTop(ctx, cam, b.x0, b.y0, chipBump + h, FP, FP, chipOn * (1 - fadeN * 0.6));
      if (s.g > 0.01) dashedBox(ctx, cam, b.x0, b.y0, chipBump + b.h * s.r * (1 - s.gH), FP, FP, b.h * s.r * s.gH, { a: s.g * (1 - fade * 0.6), lw: 1.4, dash: [4, 3], noBottom: true, color: COL.ink });
    }
    // Arm: not in the S&P 500, so it sits on its own plinth beside the board
    const ta = this.tArm - 0.25, ar = backOut(clamp((t - ta) / 0.45));
    if (t > ta + 0.01) {
      const A = this.arm, pl = easeOut(clamp((t - ta + 0.2) / 0.4));
      board(ctx, cam, A.x0 - 0.45, A.y0 - 0.45, FP + 0.9, FP + 0.9, 0.5 * pl, { lift: 0.6, shadow: 0.18 * pl });
      const tq = this.tDis + 0.25, q = easeOut((t - tq - 0.22) / 0.35);
      const h = A.h * ar * (1 - 0.131 * q), col = mix(A.base, P, fadeN), Tb = { top: css(mix(col, [255, 248, 236], 0.2)), left: css(col), right: css(mix(col, [35, 26, 44], 0.22)) };
      box(ctx, cam, A.x0, A.y0, 0, FP, FP, h, Tb, 0.6);
      const coral = t > tq ? clamp((t - tq) / 0.12) * (1 - clamp((t - tq - 0.3) / 0.25)) : 0;
      if (coral > 0) { ctx.save(); ctx.globalAlpha = coral; box(ctx, cam, A.x0, A.y0, h, FP, FP, A.h * ar - h, T(COL.loss), 0.4); ctx.restore(); }
      chipTop(ctx, cam, A.x0, A.y0, h, FP, FP, ar * (1 - fadeN));
      const g = t > tq ? clamp((t - tq - 0.2) / 0.1) * (1 - clamp((t - tq - 2.6) / 0.8)) : 0;
      if (g > 0) dashedBox(ctx, cam, A.x0, A.y0, A.h * (1 - 0.131), FP, FP, A.h * 0.131, { a: g, lw: 1.4, dash: [4, 3], noBottom: true });
    }
    // AI data centre on its own plinth; the money route and bundles pour into it
    const dcIn = t - this.tHuge;
    if (dcIn > -0.2 && t < this.tPeek + 0.5) {
      const D = this.dc, pl = easeOut(clamp((dcIn + 0.2) / 0.7)), off = (1 - pl) * 6;
      ctx.save(); ctx.globalAlpha = 1 - fadeN;
      board(ctx, cam, D.x0 - 1.0 + off, D.y0 - 1.0 + off, D.sx + 2.0, D.sy + 2.0, 0.8, { lift: 1.0 });
      const r = backOut(clamp((t - this.tAI + 0.15) / 0.5));
      if (r > 0) { ctx.save(); ctx.translate(0, 0); dataCenter(ctx, cam, D.x0 + off, D.y0 + off, D.sx, D.sy, D.h, { rise: r }); ctx.restore(); }
      // route line leads, bundles follow
      const lu = easeOut(clamp((t - this.tHuge) / 0.6));
      routeDraw(ctx, cam, this.route, 0, lu, { dash: [9, 7], offset: -t * 30, lw: 2.2 });
      if (t > this.tSums) {
        for (let n = 0; n < 40; n++) {
          const t0 = this.tSums + n * 0.11, u = (t - t0) / 1.25;
          if (u <= 0 || u >= 1) continue;
          const p = routeAt(this.route, easeIn(u) * 0.35 + u * 0.65);
          bundle(ctx, cam, p[0], p[1], p[2] + 0.05, 8.5, { flat: true });
        }
      }
      ctx.restore();
    }
    this.pins(ctx, t, fadeN);
    this.question(ctx, t);
  }
  pins(ctx, t, fadeN) {
    const cam = this.cam, ink = COL.ink, paperC = COL.paper;
    const base = { ink, paper: paperC, halo: paperC };
    // date
    if (t < this.tFell + 0.2) {
      const [x, y] = cam.p(0.2, 14.0, 0);
      pin(ctx, x, y, { ...base, p: clamp((t - this.tDate + 0.25) / 0.7), a: 1 - clamp((t - this.tSP - 0.6) / 0.4), dir: 1, lead: 150, rule: 250, num: 'NOV 5', unit: '2026', title: 'Thursday', numSize: 72, titleSize: 26 });
    }
    // S&P 500 -> -4.4%
    if (t > this.tSP - 0.2 && t < this.tAnalysts + 0.6) {
      const [x, y] = cam.p(17.2, -0.6, 0), sw = this.tFell + 0.05;
      const before = t < sw;
      const tp = before ? clamp((t - this.tSP) / 0.5) * (1 - clamp((t - sw + 0.25) / 0.25)) : clamp((t - sw - 0.05) / 0.35);
      const ttp = before ? clamp((t - this.tSP - 0.9) / 0.5) * (1 - clamp((t - sw + 0.25) / 0.25)) : clamp((t - sw - 0.2) / 0.35);
      pin(ctx, x, y, {
        ...base, p: clamp((t - this.tSP + 0.2) / 0.6), a: 1 - clamp((t - this.tAnalysts) / 0.5), tp, ttp, dir: 1, lead: Math.max(120, y - 120), rule: 330,
        num: before ? 'S&P 500' : '−4.4%', numColor: before ? ink : '#C8503E', title: before ? '500 largest U.S. companies' : 'S&P 500, one day', numSize: 84, titleSize: 24,
      });
    }
    // Nasdaq
    if (t > this.tNas - 0.2 && t < this.tAnalysts + 0.6) {
      const b = this.B.find(q => q.i === 9 && q.j === 12), [x, y] = cam.p(b.x0 + FP / 2, b.y0 + FP / 2, b.h * 0.956);
      pin(ctx, x, y, { ...base, p: clamp((t - this.tNas + 0.1) / 0.6), a: 1 - clamp((t - this.tAnalysts) / 0.5), tp: clamp((t - cue('b03', 'five', 3)) / 0.4), dir: 1, lead: 165, rule: 300, num: '−5.5%', numColor: '#C8503E', title: 'Nasdaq (tech-heavy)', numSize: 84, titleSize: 26 });
    }
    // Qualcomm and Arm
    const qa = 1 - clamp((t - this.tQuest) / 0.5);
    if (t > this.tQ - 0.2 && qa > 0) {
      const b = this.qc, [x, y] = cam.p(b.x0 + FP / 2, b.y0 + FP / 2, b.h * (t > this.tDis ? 0.905 : 0.956));
      pin(ctx, x, y, { ...base, p: clamp((t - this.tQ + 0.15) / 0.6), a: qa, tp: clamp((t - this.tDis - 0.3) / 0.4), dir: 1, lead: 175, rule: 290, num: '−9.5%', numColor: '#C8503E', title: 'Qualcomm', numSize: 80, titleSize: 28 });
    }
    if (t > this.tArm - 0.1 && qa > 0) {
      const A = this.arm, [x, y] = cam.p(A.x0 + FP / 2, A.y0 + FP / 2, A.h * (t > this.tDis ? 0.869 : 1));
      pin(ctx, x, y, { ...base, p: clamp((t - this.tArm) / 0.6), a: qa, tp: clamp((t - this.tDis - 0.45) / 0.4), dir: 1, lead: 110, rule: 290, num: '−13.1%', numColor: '#C8503E', title: 'Arm', numSize: 80, titleSize: 28 });
    }
    // AI data centres
    if (t > this.tAI - 0.1 && t < this.tFind + 0.6) {
      const D = this.dc, [x, y] = cam.p(D.x0 + D.sx * 0.3, D.y0 + D.sy * 0.7, D.h + 0.2);
      pin(ctx, x, y, { ...base, p: clamp((t - this.tAI) / 0.6), a: 1 - clamp((t - this.tFind) / 0.5), dir: 1, lead: 120, rule: 300, title: 'AI data centers', titleSize: 30 });
    }
  }
  // a big question mark hangs over the whole market on a string, and swings
  question(ctx, t) {
    const t0 = this.tQuest - 0.15;
    if (t < t0) return;
    const out = easeIn(clamp((t - this.tFind) / 0.8));
    const drop = easeOut(clamp((t - t0) / 0.55)), bounce = Math.sin(clamp((t - t0 - 0.4) / 1.4) * Math.PI * 3) * Math.exp(-clamp((t - t0 - 0.4) / 1.4) * 3);
    const len = 150 + 120 * drop + 18 * bounce - 600 * out;
    const sw = 0.06 * Math.sin((t - t0) * 2.1) * Math.exp(-(t - t0) * 0.25) + 0.05 * Math.sin(clamp((t - this.tPay) / 0.9) * Math.PI * 2) * (t > this.tPay ? Math.exp(-(t - this.tPay) * 1.5) : 0);
    const px = 1180, py = -10;
    ctx.save();
    ctx.translate(px, py); ctx.rotate(sw);
    ctx.strokeStyle = COL.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, len); ctx.stroke();
    ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.arc(0, len + 4, 6, 0, Math.PI * 2); ctx.fill();
    bigText(ctx, '?', 0, len + 250, { size: 300, p: clamp((t - t0) / 0.4) });
    ctx.restore();
  }
  // ---------- beat 8: the price tag on the whole market ----------
  // The board at full height; at "price tag" a big tag drops in on a string (where the "?" hung);
  // at "whole market" a dashed line runs round the board; at "shrank" the board drops 4.4% and
  // the tag turns over to the day's loss.
  renderPayoff(ctx, t, S) {
    const cam = this.cam;
    if (!this.camP) this.camP = camPath([[S.price - 1.0, 12.5, 10.5, 0, 32.5, 790, 600], [S.shrank + 2.9, 12.5, 10.5, 0, 31.4, 790, 605]]);
    applyCam(cam, this.camP(t));
    paper(ctx); lattice(ctx, cam, 1, -2.6);
    board(ctx, cam, -0.6, -0.6, NX + 1.2, NY + 1.2, 1.2, { lift: 1.4 });
    // "the whole market": a dashed line runs round the board's rim
    const ru = easeOut(clamp((t - S.whole + 0.1) / 0.8)), ra = 1 - clamp((t - S.shrank) / 0.5);
    if (ru > 0 && ra > 0) {
      const a0 = -0.35, a1x = NX + 0.35, a1y = NY + 0.35;
      const P = [[a0, a0], [a1x, a0], [a1x, a1y], [a0, a1y], [a0, a0]].map(([x, y]) => cam.p(x, y, 0));
      const segs = [];
      let L = 0; for (let k = 1; k < P.length; k++) { const d = Math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]); segs.push(d); L += d; }
      ctx.save(); ctx.globalAlpha = ra; ctx.strokeStyle = COL.ink; ctx.lineWidth = 3.2; ctx.lineCap = 'round'; ctx.setLineDash([12, 9]); ctx.lineDashOffset = -t * 40;
      ctx.beginPath(); ctx.moveTo(P[0][0], P[0][1]);
      let left = ru * L;
      for (let k = 1; k < P.length && left > 0; k++) {
        const f = Math.min(1, left / segs[k - 1]);
        ctx.lineTo(lerp(P[k - 1][0], P[k][0], f), lerp(P[k - 1][1], P[k][1], f)); left -= segs[k - 1];
      }
      ctx.stroke(); ctx.restore();
    }
    const dropT = (b) => S.shrank - 0.05 + ((b.i + b.j) / 43) * 0.45;
    for (const b of this.B) {
      const td = dropT(b), q = easeOut(clamp((t - td - 0.15) / 0.35)), f = 1 - 0.044 * q;
      const coral = t > td ? clamp((t - td) / 0.1) * (1 - clamp((t - td - 0.35) / 0.25)) : 0;
      const g = t > td ? clamp((t - td - 0.2) / 0.1) : 0;
      const col = b.base, Tb = { top: css(mix(col, [255, 248, 236], 0.2)), left: css(col), right: css(mix(col, [35, 26, 44], 0.22)) };
      box(ctx, cam, b.x0, b.y0, 0, FP, FP, b.h * f, Tb, 0.6);
      if (coral > 0) { ctx.save(); ctx.globalAlpha = coral; box(ctx, cam, b.x0, b.y0, b.h * f, FP, FP, b.h * (1 - f), T(COL.loss), 0.4); ctx.restore(); }
      if (g > 0.01) dashedBox(ctx, cam, b.x0, b.y0, b.h * (1 - 0.044), FP, FP, b.h * 0.044, { a: g, lw: 1.3, dash: [4, 3], noBottom: true });
      if (b.kind === 'nvda' || b.kind === 'chip' || b.kind === 'qcom') chipTop(ctx, cam, b.x0, b.y0, b.h * f, FP, FP, 1);
    }
    this.hangTag(ctx, t, S);
    const pa = clamp((t - S.price + 0.1) / 0.45), out = 1 - clamp((t - S.shrank - 0.55) / 0.4);
    if (pa > 0 && out > 0) {
      bigText(ctx, [['A ', '#FFFFFF'], ['PRICE TAG', HL], [',', '#FFFFFF']], W - 70, 852, { size: 106, p: pa, a: out, align: 'right' });
      bigText(ctx, 'NOT CASH', W - 70, 852 + 120, { size: 106, p: clamp((t - S.price - 0.3) / 0.45), a: out, align: 'right' });
    }
  }
  // a big price tag on a string, hung from above the frame; it turns over at "shrank"
  hangTag(ctx, t, S) {
    const t0 = S.price - 0.12;
    if (t < t0) return;
    const drop = easeOut(clamp((t - t0) / 0.55)), u = clamp((t - t0 - 0.4) / 1.4);
    const bounce = Math.sin(u * Math.PI * 3) * Math.exp(-u * 3);
    const len = 70 + 150 * drop + 16 * bounce;
    const jolt = t > S.shrank ? 0.05 * Math.sin((t - S.shrank) * 7) * Math.exp(-(t - S.shrank) * 2.2) : 0;
    const sw = 0.06 * Math.sin((t - t0) * 2.0) * Math.exp(-(t - t0) * 0.4) + jolt;
    const f = clamp((t - S.shrank - 0.02) / 0.55), turn = Math.cos(smoother(f) * Math.PI), back = turn < 0;
    const tex = back ? tagTexture('−$2.8T', 'Nov 5', '#C8503E', 132) : tagTexture('S&P 500', 'price tag', COL.ink, 116);
    const cw = 520, sc = cw / 640, ch = 300 * sc;
    ctx.save();
    ctx.translate(1400, -10); ctx.rotate(sw);
    ctx.strokeStyle = COL.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, len); ctx.stroke();
    ctx.translate(0, len); ctx.scale(Math.max(0.02, Math.abs(turn)), 1); ctx.rotate(0.3 - sw * 0.6);
    ctx.globalAlpha = clamp((t - t0) / 0.15);
    ctx.drawImage(tex, -70 * sc, -144 * sc, cw, ch);
    if (Math.abs(turn) < 0.999) { ctx.globalAlpha *= (1 - Math.abs(turn)) * 0.35; ctx.fillStyle = COL.ink; ctx.fillRect(-70 * sc + 4, -144 * sc + 4, cw - 8, ch - 8); }
    ctx.restore();
  }
}
