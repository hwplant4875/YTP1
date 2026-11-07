// S6 (beat 7): where the cash went. Seller (left) and buyer (right) accounts are two vaults.
// The share hops from the seller to the buyer, real money slides back; then many trades stream across.
import { W, H, Cam, pin, camPath, applyCam, box, clamp, lerp, easeOut, easeIn, smoother, backOut } from '../iso.js';
import { COL, T, paper, lattice, board, pile, vault, routePts, routeAt, routeDraw } from '../objects.js';
import { cue } from '../cue.js';

const SHARE = T('#F4F1EA');
const SV = { x0: 2.1, y0: -5.1, s: 3.0, h: 2.8 }, BV = { x0: -5.1, y0: 2.1, s: 3.0, h: 2.8 };

export class Cash {
  constructor() { this.cam = new Cam(); }
  init() {
    const c = (w, n) => cue('b07', w, n);
    this.S = {
      so: c('So'), cashQ: c('cash'), every: c('Every'), share: c('share'), sold: c('sold'), bought: c('bought'), else: c('else'),
      buyer: c('buyer'), paid: c('paid'), real: c('real'), money: c('money'), cash2: c('cash', 2), vanish: c('vanish'),
      moved: c('moved'), account: c('account'), another: c('another'),
    };
    const S = this.S;
    this.camAt = camPath([
      [S.so - 0.6, 0.4, 0.4, -0.4, 16.8], [S.every, 0.2, 0.2, -0.3, 15.6], [S.money + 0.8, 0.2, 0.2, -0.3, 15.0],
      [S.moved, 0.2, 0.2, -0.3, 15.4], [S.another + 1.6, 0.2, 0.2, -0.3, 16.4],
    ]);
    this.laneA = routePts([[2.35, -1.5, 0.03], [0.42, 0.42, 0.03], [-1.5, 2.35, 0.03]]);
    this.laneB = routePts([[-1.05, 4.2, 0.03], [1.58, 1.58, 0.03], [4.2, -1.05, 0.03]]);
  }
  render(ctx, t) {
    const S = this.S, cam = this.cam;
    applyCam(cam, this.camAt(t));
    paper(ctx); lattice(ctx, cam, 1, -2.4);
    board(ctx, cam, -5.7, -5.7, 11.4, 11.4, 1.2, { lift: 1.0 });
    // the two accounts rise in
    const rs = backOut(clamp((t - S.so) / 0.5)), rb = backOut(clamp((t - S.so - 0.18) / 0.5));
    if (rs > 0.01) vault(ctx, cam, SV.x0, SV.y0, SV.s, SV.h * rs);
    if (rb > 0.01) vault(ctx, cam, BV.x0, BV.y0, BV.s, BV.h * rb, { door: 'x' });
    // lanes: the share's lane leads at "Every", the cash lane at "buyer"
    const la = easeOut(clamp((t - S.every) / 0.6)), lb = easeOut(clamp((t - S.buyer) / 0.6));
    routeDraw(ctx, cam, this.laneA, 0, la, { dash: [10, 8], offset: -t * 34, lw: 2.6 });
    routeDraw(ctx, cam, this.laneB, 0, lb, { dash: [10, 8], offset: -t * 34, lw: 2.6, color: COL.billInk });
    // lane A items (behind lane B on screen)
    const ua = clamp((t - S.sold) / 1.2), shareIn = backOut(clamp((t - S.share + 0.15) / 0.45));
    if (shareIn > 0.01) {
      const pa = routeAt(this.laneA, smoother(ua)), hop = Math.sin(Math.PI * smoother(ua)) * 1.1;
      const land = S.sold + 1.2, sq = t > land && t < land + 0.18 ? 1 - 0.2 * Math.sin(Math.PI * (t - land) / 0.18) : 1;
      const z = 1.05 * shareIn;
      box(ctx, cam, pa[0] - z / 2, pa[1] - z / 2, 0.03 + hop, z, z, z * sq, SHARE, 0.6);
    }
    this.stream(ctx, t, this.laneA, (p, a) => { const z = 0.8; ctx.save(); ctx.globalAlpha = a; box(ctx, cam, p[0] - z / 2, p[1] - z / 2, p[2] + p[3], z, z, z, SHARE, 0.6); ctx.restore(); }, 0);
    // lane B items: the cash
    const cashIn = clamp((t - S.cashQ + 0.1) / 0.5);
    if (cashIn > 0) {
      const ub = clamp((t - S.paid) / 1.2), pb = routeAt(this.laneB, smoother(ub)), hop = Math.sin(Math.PI * smoother(ub)) * 0.5;
      const layers = Math.max(1, Math.round(5 * easeOut(cashIn)));
      const pulse = 1 + 0.06 * Math.sin(Math.PI * clamp((t - S.cash2) / 0.35));
      pile(ctx, cam, pb[0], pb[1], 0.03 + hop, 13 * pulse, 2, 1, layers, { seed: 21 });
    }
    this.stream(ctx, t, this.laneB, (p, a) => { ctx.save(); ctx.globalAlpha = a; pile(ctx, cam, p[0], p[1], p[2] + p[3] * 0.5, 11, 2, 1, 3, { seed: 7 }); ctx.restore(); }, 0.15);
    // labels
    const pc = { ink: COL.ink, paper: COL.paper, halo: COL.paper };
    {
      const [x, y] = cam.p(SV.x0 + SV.s * 0.5, SV.y0 + SV.s * 0.5, SV.h);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.sold + 0.3) / 0.6), ttp: clamp((t - S.paid - 1.25) / 0.45), dir: -1, lead: 120, rule: 330, num: 'SELLER', title: 'gets the cash', numSize: 72, titleSize: 28 });
    }
    {
      const [x, y] = cam.p(BV.x0 + BV.s * 0.5, BV.y0 + BV.s * 0.5, BV.h);
      pin(ctx, x, y, { ...pc, p: clamp((t - S.bought + 0.2) / 0.6), ttp: clamp((t - S.sold - 1.25) / 0.45), dir: 1, lead: 120, rule: 330, num: 'BUYER', title: 'gets the share', numSize: 72, titleSize: 28 });
    }
  }
  // many trades: from "moved", items stream along a lane (fade in and out at the ends)
  stream(ctx, t, R, draw, phase) {
    const t0 = this.S.moved - 0.1 + phase;
    if (t < t0) return;
    for (let n = 0; n < 10; n++) {
      const u = (t - t0 - n * 0.34) / 0.95;
      if (u <= 0 || u >= 1) continue;
      const p = routeAt(R, smoother(u)), a = clamp(u / 0.15) * clamp((1 - u) / 0.15);
      draw([p[0], p[1], 0.03, Math.sin(Math.PI * u) * 0.7], a);
    }
  }
}
