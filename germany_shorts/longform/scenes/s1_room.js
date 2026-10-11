import * as O from './ghost_watch.js';
import { wrap } from './s1_portrait.js';
// guardroom: lifted for phone screens (the platform guards were lost in the dark)
export const { setup, update } = wrap(O, { guardroom: { exposure: 1.7 } });
