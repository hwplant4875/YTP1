import * as O from './ghost_watch.js';
import { wrap } from './s1_portrait.js';
// boots: the train pulling in, lifted a little; eachother: the guard seen from behind, lifted for phone screens
export const { setup, update } = wrap(O, { boots: { exposure: 1.2 }, eachother: { exposure: 1.5 } });
