// S7 (beat 8): the answer. The $2.8T column from the opening goes hollow ("never a pile of cash"),
// then the market board gets a price tag, and the tag shrinks with the market.
import { smoother } from '../iso.js';
import { cue } from '../cue.js';

export class PayoffColumn {
  init(base, ep) {
    this.ep = ep;
    this.t0 = cue('b07', 'another') + 0.7; this.never = cue('b08', 'never');
  }
  render(ctx, t) {
    const op = this.ep.opening;
    op.ghostOverride = smoother((t - this.never - 0.05) / 0.8);
    op.render(ctx, 27.2 + (t - this.t0) * 0.55);
    op.ghostOverride = undefined;
  }
}
export class PayoffBoard {
  constructor(market) { this.m = market; }
  init() {
    const c = (w, n) => cue('b08', w, n);
    this.S = { price: c('price'), tag: c('tag'), whole: c('whole'), market: c('market'), nov: c('November'), price2: c('price', 2), shrank: c('shrank') };
  }
  render(ctx, t) { this.m.renderPayoff(ctx, t, this.S); }
}
