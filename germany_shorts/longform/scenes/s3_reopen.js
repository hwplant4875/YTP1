import * as O from './reopen.js';
import { wrap } from './s1_portrait.js';
// stop: the train arriving out of the dark tunnel; lift the platform for phones
export const { setup, update } = wrap(O, { stop: { exposure: 1.35 } });
