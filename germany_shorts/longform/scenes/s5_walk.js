// Short #5 "Frozen for 28 years": portrait framing of the ghost-walk scene (see s1_portrait.js).
import * as O from './ghost_walk.js';
import { wrap } from './s1_portrait.js';
// title: the lit platform sits right of centre; turn towards it and lift it for phones
export const { setup, update } = wrap(O, { title: { yaw: -0.2, exposure: 1.45 } });
