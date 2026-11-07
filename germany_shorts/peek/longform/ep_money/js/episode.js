// The whole episode on one clock: scenes in order, joined by dissolves (or the PEEK keyhole).
import { W, H, clamp, smoother, easeIn, easeOut, bigText, measureBig, HL } from './iso.js';
import { Opening, mainTake } from './opening.js';
import { cue, END } from './cue.js';

// opening take (17 s) stretched onto the narration of beats 1 + 2 (v = voice-over clock, T = take clock)
const WARP = [[0, 0], [2.6, 2.6], [4.4, 3.25], [5.6, 3.55], [7.0, 4.5], [8.3, 6.0], [9.2, 6.33], [12.7, 6.62], [13.4, 6.75],
  [15.3, 7.6], [16.6, 8.7], [18.4, 9.85], [20.2, 11.3], [20.8, 11.45], [22.6, 13.25], [23.1, 13.8], [31.9, 17.0]];

export class Episode {
  async init(assetBase, extra = []) {
    const open = mainTake(WARP);
    const tNobody = cue('b02', 'nobody');
    this.hookOut = Math.min(cue('b01', 'If') - 0.4, 4.85);   // gone before the stack readout climbs into it
    open.ghost = (v) => smoother((v - tNobody + 0.05) / 0.75);
    this.opening = new Opening(open); await this.opening.init(assetBase);
    // [t0, t1, scene, transition-in]
    this.list = [[0, 31.95, { render: (ctx, t) => this.opening.render(ctx, t) }, null]];
    for (const e of extra) { if (e[2].init) await e[2].init(assetBase, this); this.list.push(e); }
    this.list.sort((a, b) => a[0] - b[0]);
    this.DUR = END;
    this.off = document.createElement('canvas'); this.off.width = W; this.off.height = H;
    this.octx = this.off.getContext('2d');
  }
  render(ctx, t) {
    const act = this.list.filter(e => t >= e[0] && t < e[1]);
    if (!act.length) { ctx.fillStyle = '#F2EADB'; ctx.fillRect(0, 0, W, H); return; }
    const [a0, a1, A] = act[0];
    ctx.save(); A.render(ctx, t); ctx.restore();
    if (act.length > 1) {
      const [b0, b1, B, tr] = act[1];
      const o = this.octx; o.save(); o.setTransform(1, 0, 0, 1, 0, 0); B.render(o, t); o.restore();
      const end = Math.min(a1, b1), p = clamp((t - b0) / Math.max(1e-6, end - b0));
      if (tr && tr.type === 'keyhole') this.keyhole(ctx, p, tr.at ? tr.at(t) : [W / 2, H / 2]);
      else { ctx.save(); ctx.globalAlpha = smoother(p); ctx.drawImage(this.off, 0, 0); ctx.restore(); }
    }
    this.hook(ctx, t);
  }
  // the hook line as big key text: complete on frame 0 (it is also the cover), out as the stacking line starts
  hook(ctx, t) {
    const a = 1 - clamp((t - this.hookOut) / 0.35);
    if (a <= 0) return;
    const parts = [['$2.8 TRILLION', HL], [' VANISHED', '#FFFFFF']];
    const size = Math.min(132, 132 * 1680 / measureBig(ctx, '$2.8 TRILLION VANISHED', 132));
    bigText(ctx, parts, W / 2, 172, { size, p: 1, a });
  }
  // PEEK keyhole: the next scene shows through a keyhole that opens out from `at` until it fills the frame
  keyhole(ctx, p, at) {
    const e = easeIn(p) * 0.92 + p * 0.08, s = 18 + e * 2600, [cx, cy] = at;
    const x = cx + (W / 2 - cx) * smoother(p), y = cy + (H / 2 - cy) * smoother(p);
    const circ = new Path2D(), slot = new Path2D(), path = new Path2D();
    circ.arc(x, y - s * 0.18, s * 0.42, 0, Math.PI * 2);
    slot.moveTo(x - s * 0.2, y + s * 0.02); slot.lineTo(x + s * 0.2, y + s * 0.02); slot.lineTo(x + s * 0.34, y + s * 0.78); slot.lineTo(x - s * 0.34, y + s * 0.78); slot.closePath();
    path.addPath(circ); path.addPath(slot);
    const outside = (shape) => { const q = new Path2D(); q.rect(-20, -20, W + 40, H + 40); q.addPath(shape); return q; };
    ctx.save();
    ctx.globalAlpha = clamp(p * 6);
    ctx.fillStyle = 'rgba(27,22,34,' + (0.22 * Math.sin(Math.PI * clamp(p * 1.4))).toFixed(3) + ')'; ctx.fillRect(0, 0, W, H);
    ctx.clip(path, 'nonzero'); ctx.drawImage(this.off, 0, 0);
    ctx.restore();
    ctx.save(); ctx.strokeStyle = '#2B2533'; ctx.lineWidth = 6 + 10 * (1 - p); ctx.globalAlpha = clamp(p * 6) * (1 - smoother((p - 0.7) / 0.3));
    ctx.save(); ctx.clip(outside(slot), 'evenodd'); ctx.stroke(circ); ctx.restore();
    ctx.save(); ctx.clip(outside(circ), 'evenodd'); ctx.stroke(slot); ctx.restore();
    ctx.restore();
  }
}
