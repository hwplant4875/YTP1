import * as O from './ghost_walk.js';
import { wrap } from './s1_portrait.js';
// title: the lit platform sits right of centre; turn towards it
export const { setup, update } = wrap(O, { title: { yaw: -0.2 } });
