import * as O from './ghost_watch.js';
import { wrap } from './s1_portrait.js';
// nostop: the train passes on the right, outside a 9:16 crop; widen and turn towards it, keep the guard in frame
export const { setup, update } = wrap(O, { nostop: { yaw: -0.07, fov: 60 } });
