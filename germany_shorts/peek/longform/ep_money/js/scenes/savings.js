// S8 (beat 9): savings. Two portfolios (retirement accounts, pension funds) hold the same companies;
// millions more appear around them; all shrink on paper. A sale turns the paper loss into cash
// (coral), and the next day Nvidia climbs back 2.8% on the portfolio that still holds it.
import { W, H, Cam, rgb, css, mix, box, pin, dashedBox, camPath, applyCam, clamp, lerp, sstep, smoother, easeOut, backOut, mulberry32 } from '../iso.js';
import { COL, T, paper, lattice, board, chipTop, tag } from '../objects.js';
import { cue } from '../cue.js';

const PITCH = 1.35, BS = 1.0, DROP = { nvda: 0.093, other: 0.044 };
const KIND = { grey: null, tech: COL.tech, chip: COL.chip, nvda: COL.nvda };
const MAIN = [
  { cx: 3.6, cy: -3.6, cells: ['grey', 1.2, 'tech', 1.9, 'grey', 1.0, 'chip', 1.5, 'grey', 1.3, 'tech', 1.6, 'grey', 0.9, 'grey', 1.1, 'nvda', 2.6] },
  { cx: -3.6, cy: 3.6, cells: ['tech', 1.7, 'grey', 1.1, 'chip', 1.4, 'grey', 1.0, 'grey', 1.5, 'grey', 1.2, 'tech', 1.3, 'grey', 0.9, 'nvda', 2.4] },
];
const tonesOf = (c) => ({ top: css(mix(c, [255, 248, 236], 0.2)), left: css(c), right: css(mix(c, [35, 26, 44], 0.22)) });

export class Savings {
  constructor() { this.cam = new Cam(); }
  init() {
    const c = (w, n) => cue('b09', w, n);
    const S = this.S = {
      that: c('That'), matter: c('matter'), ret: c('Retirement'), pension: c('pension'), own: c('own'), same: c('same'),
      millions: c('millions'), savings: c('savings'), shrink: c('shrink'), paper: c('paper'), loss: c('loss'), paper2: c('paper', 2),
      cash: c('cash'), sells: c('sells'), less: c('less'), paid: c('paid'), prices: c('Prices'), next: c('next'), nvidia: c('Nvidia'),
      up: c('up'), three: c('three'), percent: c('percent'),
    };
    const rnd = mulberry32(906);
    // blocks of the two main portfolios
    this.main = MAIN.map((m, k) => {
      const blocks = [];
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        const n = i * 3 + j, kind = m.cells[n * 2], h = m.cells[n * 2 + 1];
        const base = KIND[kind] ? mix(rgb(KIND[kind]), [255, 255, 255], kind === 'tech' ? rnd() * 0.2 : 0) : rgb(COL.grey[(rnd() * COL.grey.length) | 0]);
        blocks.push({ i, j, kind, h, base, x0: m.cx + (i - 1) * PITCH - BS / 2, y0: m.cy + (j - 1) * PITCH - BS / 2 });
      }
      return { ...m, k, blocks, nv: blocks.find(b => b.kind === 'nvda') };
    });
    // a field of small portfolios ("millions of people")
    this.minis = [];
    for (let gx = -6; gx <= 6; gx++) for (let gy = -6; gy <= 6; gy++) {
      const x = gx * 3.6 + (rnd() - 0.5) * 0.6, y = gy * 3.6 + (rnd() - 0.5) * 0.6;
      if (MAIN.some(m => Math.abs(x - m.cx) < 4.6 && Math.abs(y - m.cy) < 4.6)) continue;
      if (Math.abs(y - x) > 30 || Math.abs(x + y) > 26) continue;
      const bl = [];
      for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) {
        const r = rnd(), kind = r < 0.1 ? 'nvda' : r < 0.3 ? 'tech' : 'grey';
        bl.push({ i, j, kind, h: 0.35 + rnd() * 0.75, base: KIND[kind] ? rgb(KIND[kind]) : rgb(COL.grey[(rnd() * COL.grey.length) | 0]) });
      }
      this.minis.push({ x, y, bl, d: Math.hypot(x, y) });
    }
    const R = this.main[0].nv, P = this.main[1].nv;
    const rc = [R.x0 + 0.5, R.y0 + 0.5, R.h * 0.85], pc = [P.x0 + 0.5, P.y0 + 0.5, P.h * 0.85];
    this.camAt = camPath([
      [S.matter - 1.0, 0, 0, 0.9, 12.9], [S.own, 0, 0, 0.9, 12.4], [S.millions + 0.9, 0, 0, 0.6, 18.5], [S.paper + 0.2, 0, 0, 0.6, 18.0],
      [S.cash - 0.2, rc[0] - 0.9, rc[1] + 0.9, rc[2], 7.6], [S.paid + 0.9, rc[0] - 0.9, rc[1] + 0.9, rc[2], 7.4],
      [S.next + 0.2, pc[0] - 0.9, pc[1] + 0.9, pc[2], 7.6], [S.percent + 1.4, pc[0] - 0.9, pc[1] + 0.9, pc[2], 7.0],
    ]);
  }
  dropT(x, y) { return this.S.shrink - 0.05 + clamp((x + y + 18) / 36) * 0.55; }
  render(ctx, t) {
    const S = this.S, cam = this.cam;
    applyCam(cam, this.camAt(t));
    paper(ctx); lattice(ctx, cam, 1, -1.6);
    // everything sorted back to front by its plinth centre
    const items = [];
    for (const m of this.minis) items.push([m.x + m.y, () => this.mini(ctx, t, m)]);
    for (const m of this.main) items.push([m.cx + m.cy, () => this.portfolio(ctx, t, m)]);
    items.sort((a, b) => a[0] - b[0]);
    for (const [, f] of items) f();
    this.labels(ctx, t);
  }
  slice(b, t, x, y) {
    // shrink on paper: coral flash, then a dashed ghost of the lost slice
    const fr = b.kind === 'nvda' ? DROP.nvda : DROP.other, td = this.dropT(x, y);
    const q = easeOut(clamp((t - td - 0.15) / 0.35));
    const coral = t > td ? clamp((t - td) / 0.1) * (1 - clamp((t - td - 0.35) / 0.25)) : 0;
    const g = t > td ? clamp((t - td - 0.2) / 0.1) : 0;
    return { f: 1 - fr * q, fr, coral, g };
  }
  portfolio(ctx, t, m) {
    const S = this.S, cam = this.cam;
    const t0 = S.matter - 0.62 + m.k * 0.22, pr = backOut(clamp((t - t0) / 0.5));
    if (pr <= 0.01) return;
    const off = (1 - easeOut(clamp((t - t0) / 0.5))) * 2.5;
    board(ctx, cam, m.cx - 2.2 + off, m.cy - 2.2 + off, 4.4, 4.4, 0.7, { lift: 0.8, shadow: 0.2 * pr });
    const bump = (b) => Math.sin(Math.PI * clamp((t - S.same + 0.1 - 0.05 * (b.i + b.j)) / 0.32)) * 0.22;
    for (const b of m.blocks) {
      const tb = t0 + 0.25 + (b.i + b.j) * 0.07, r = backOut(clamp((t - tb) / 0.4));
      if (r <= 0.01) continue;
      const s = this.slice(b, t, b.x0, b.y0), z0 = bump(b);
      const h = b.h * r * s.f, full = b.h * r;
      box(ctx, cam, b.x0 + off, b.y0 + off, z0, BS, BS, h, tonesOf(b.base), 0.6);
      const nvR = b === this.main[0].nv, nvP = b === this.main[1].nv;
      // still held (portfolio 2): Nvidia climbs back 2.8% the next day
      let hg = 0;
      if (nvP && t > S.nvidia) {
        hg = h * 0.0278 * easeOut(clamp((t - S.nvidia) / 0.6));
        box(ctx, cam, b.x0, b.y0, z0 + h, BS, BS, hg, T(COL.gain), 0.4);
      }
      if (b.kind !== 'grey' && b.kind !== 'tech') chipTop(ctx, cam, b.x0 + off, b.y0 + off, z0 + h + hg, BS, BS, r);
      if (s.coral > 0) { ctx.save(); ctx.globalAlpha = s.coral; box(ctx, cam, b.x0, b.y0, z0 + h, BS, BS, full - h, T(COL.loss), 0.4); ctx.restore(); }
      // sold (portfolio 1): the paper slice turns into a solid coral loss
      const real = nvR ? easeOut(clamp((t - S.paid + 0.05) / 0.3)) : 0;
      if (real > 0) { ctx.save(); ctx.globalAlpha = real; box(ctx, cam, b.x0, b.y0, z0 + h, BS, BS, full - h, T(COL.loss), 0.5); ctx.restore(); }
      if (s.g > 0.01 && real < 1) dashedBox(ctx, cam, b.x0, b.y0, z0 + h + hg, BS, BS, full - h - hg, { a: s.g * (1 - real), lw: 1.6, dash: [5, 4], noBottom: true });
      if (nvP && t > S.nvidia) {
        const gl = Math.sin(Math.PI * clamp((t - S.nvidia) / 0.9));
        if (gl > 0) { ctx.save(); ctx.globalAlpha = 0.35 * gl; box(ctx, cam, b.x0 - 0.04, b.y0 - 0.04, z0 + h - 0.02, BS + 0.08, BS + 0.08, hg + 0.04, T('#7FE0C8'), 0); ctx.restore(); }
      }
      if (nvR) {
        // the price tag on the shares that get sold
        const tp = clamp((t - S.paper2 + 0.2) / 0.5), flip = smoother(clamp((t - S.sells - 0.05) / 0.5));
        if (tp > 0) tag(ctx, cam, b.x0 + 0.1, b.y0 + BS, z0 + h * 0.97, 2.9, '$200.13', '$181.60', { p: tp, flip, subA: 'paid', subB: 'sold', drop: 0.16, dx: 0.04, swing: 0.05 * Math.sin((t - S.sells) * 4) * (t > S.sells ? Math.exp(-(t - S.sells) * 1.5) : 0) });
      }
    }
  }
  mini(ctx, t, m) {
    const S = this.S, cam = this.cam;
    const t0 = S.millions - 0.15 + m.d * 0.03, pr = backOut(clamp((t - t0) / 0.45));
    if (pr <= 0.01) return;
    const [sx, sy] = cam.p(m.x, m.y, 0);
    if (sx < -200 || sx > W + 200 || sy < -200 || sy > H + 260) return;
    const s = 1.6 * pr, th = 0.35;
    const P = rgb(COL.paper), fade = 0.45;
    box(ctx, cam, m.x - s / 2, m.y - s / 2, -th, s, s, th, tonesOf(mix(rgb(COL.board), P, fade)), 0.6);
    for (const b of m.bl) {
      const x0 = m.x - 0.62 + b.i * 0.7, y0 = m.y - 0.62 + b.j * 0.7;
      const sl = this.slice(b, t, m.x, m.y), h = b.h * pr * sl.f, full = b.h * pr;
      box(ctx, cam, x0, y0, 0, 0.54, 0.54, h, tonesOf(mix(b.base, P, fade)), 0.5);
      if (sl.coral > 0) { ctx.save(); ctx.globalAlpha = sl.coral; box(ctx, cam, x0, y0, h, 0.54, 0.54, full - h, T(COL.loss), 0.3); ctx.restore(); }
      if (sl.g > 0.01) dashedBox(ctx, cam, x0, y0, h, 0.54, 0.54, full - h, { a: sl.g * 0.8, lw: 1.1, dash: [3, 3], noBottom: true });
    }
  }
  labels(ctx, t) {
    const S = this.S, cam = this.cam, pc = { ink: COL.ink, paper: COL.paper, halo: COL.paper };
    const wideA = 1 - clamp((t - S.loss) / 0.5);
    if (wideA > 0) {
      const R = this.main[0], P = this.main[1];
      let [x, y] = cam.p(R.cx - 1.35, R.cy - 1.35, 1.25);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.ret + 0.1) / 0.6), a: wideA, dir: 1, lead: 150, rule: 380, title: 'Retirement accounts', titleSize: 30 });
      [x, y] = cam.p(P.cx - 1.35, P.cy - 1.35, 1.75);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.pension + 0.1) / 0.6), a: wideA, dir: 1, lead: 150, rule: 300, title: 'Pension funds', titleSize: 30 });
    }
    // the sale: a real loss in cash
    const R = this.main[0].nv;
    if (t > S.paid - 0.1) {
      const [x, y] = cam.p(R.x0 + 0.5, R.y0, R.h * 0.95);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.paid + 0.1) / 0.6), a: 1 - clamp((t - S.prices - 0.4) / 0.5), dir: -1, lead: 215, rule: 330, num: '-$18.53', numColor: '#C8503E', title: 'Real loss, per share', numSize: 84, titleSize: 28 });
    }
    // the next day
    const P = this.main[1].nv;
    if (t > S.nvidia - 0.1) {
      const [x, y] = cam.p(P.x0 + 0.5, P.y0, P.h * 0.93);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.nvidia) / 0.6), tp: clamp((t - S.up) / 0.45), dir: -1, lead: 215, rule: 330, num: '+2.8%', numColor: '#2E8B79', title: 'Nvidia, the next day', numSize: 84, titleSize: 28 });
    }
  }
}
