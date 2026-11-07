// S9 (beat 10): back on the ground where the video began: a small pile of $100 bundles, the camera
// drifting up. The headline "billions vanished" gets corrected to "repriced", then the question.
import { W, bigText, measureBig, clamp, easeOut, smoother, HL } from '../iso.js';
import { Opening, endTake } from '../opening.js';
import { cue } from '../cue.js';

const fit = (ctx, s, size, max = 1680) => Math.min(size, size * max / measureBig(ctx, s, size));

export class Ending {
  constructor(t0) { this.t0 = t0; this.op = new Opening(endTake()); }
  async init(base) {
    await this.op.init(base);
    const c = (w, n) => cue('b10', w, n);
    this.S = { headline: c('headline'), billions: c('billions'), vanished: c('vanished'), day: c('day'), stolen: c('stolen'), burned: c('burned'), re: c('repriced'), did: c('Did'), nov: c('November'), tell: c('Tell') };
  }
  render(ctx, t) {
    const S = this.S;
    this.op.render(ctx, t - this.t0);
    // the headline, then its correction
    const outA = 1 - clamp((t - S.did + 0.35) / 0.35);
    if (t > S.billions - 0.1 && outA > 0) {
      const size = fit(ctx, 'BILLIONS VANISHED', 124), y = 250;
      const wB = measureBig(ctx, 'BILLIONS ', size), wV = measureBig(ctx, 'VANISHED', size), x0 = W / 2 - (wB + wV) / 2;
      bigText(ctx, 'BILLIONS', x0, y, { size, p: clamp((t - S.billions + 0.1) / 0.4), a: outA, align: 'left' });
      bigText(ctx, 'VANISHED', x0 + wB, y, { size, p: clamp((t - S.vanished + 0.05) / 0.4), a: outA, align: 'left' });
      // strike through "VANISHED" at "repriced"
      const st = easeOut(clamp((t - S.re + 0.15) / 0.35));
      if (st > 0) {
        ctx.save(); ctx.globalAlpha = outA; ctx.lineCap = 'round';
        const ys = y - size * 0.34, xa = x0 + wB - 10, xb = xa + (wV + 20) * st;
        ctx.strokeStyle = '#141018'; ctx.lineWidth = size * 0.2; ctx.beginPath(); ctx.moveTo(xa, ys); ctx.lineTo(xb, ys); ctx.stroke();
        ctx.strokeStyle = '#E2705C'; ctx.lineWidth = size * 0.11; ctx.beginPath(); ctx.moveTo(xa, ys); ctx.lineTo(xb, ys); ctx.stroke();
        ctx.restore();
      }
      if (t > S.re - 0.05) bigText(ctx, 'REPRICED', x0 + wB + wV / 2, y + size * 1.12, { size: size * 1.05, p: clamp((t - S.re + 0.05) / 0.4), a: outA, align: 'center' });
    }
    // the closing question
    if (t > S.did - 0.1) {
      const l1 = 'DID YOU CHECK YOUR PORTFOLIO', s1 = fit(ctx, l1, 104);
      bigText(ctx, l1, W / 2, 230, { size: s1, p: clamp((t - S.did + 0.1) / 0.45) });
      bigText(ctx, [['ON ', '#FFFFFF'], ['NOV 5', HL], ['?', '#FFFFFF']], W / 2, 230 + s1 * 1.25, { size: s1 * 1.15, p: clamp((t - S.nov + 0.1) / 0.45) });
    }
  }
}
