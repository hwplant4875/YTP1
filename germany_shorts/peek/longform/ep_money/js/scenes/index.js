import { Market } from './market.js';
import { Nvidia } from './nvidia.js';
import { Cash } from './cash.js';
import { PayoffColumn, PayoffBoard } from './payoff.js';
import { Savings } from './savings.js';
import { Ending } from './ending.js';
import { Opening, nvidiaTake } from '../opening.js';
import { cue } from '../cue.js';

// Nvidia's one-day loss as a stack of bills (the opening's engine with another take)
class Column {
  constructor(t0) { this.t0 = t0; this.op = new Opening(nvidiaTake()); }
  async init(base) { await this.op.init(base); }
  render(ctx, t) { this.op.render(ctx, t - this.t0); }
}

// [start, end, scene, transition into it]; overlapping entries dissolve unless a transition says otherwise
export function SCENES() {
  const market = new Market(), nvidia = new Nvidia();
  const peek = cue('b04', 'peek'), bills = cue('b04', 'bills'), but = cue('b05', 'But');
  const s6 = cue('b06', 'share', 3), price = cue('b08', 'price'), shrank = cue('b08', 'shrank');
  const did = cue('b10', 'So') - 0.45;
  return [
    [31.45, peek + 1.35, market, null],
    [peek, bills + 0.45, nvidia, { type: 'keyhole', at: (t) => market.nvidiaScreen(t) }],
    [bills - 0.15, but + 0.2, new Column(bills - 0.2), null],
    [but - 0.35, s6 + 1.4, nvidia, null],
    [s6 + 0.9, cue('b07', 'another') + 1.2, new Cash(), null],
    [cue('b07', 'another') + 0.7, price + 0.1, new PayoffColumn(), null],
    [price - 0.4, shrank + 2.9, new PayoffBoard(market), null],
    [shrank + 2.3, did + 0.8, new Savings(), null],
    [did, 999, new Ending(did), null],
  ];
}
