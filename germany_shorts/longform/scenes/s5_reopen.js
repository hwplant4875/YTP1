// Short #5 "Frozen for 28 years": portrait framing of the 1989 reopening scene (see s1_portrait.js).
import * as O from './reopen.js';
import { wrap } from './s1_portrait.js';
// stop: the train arriving out of the dark tunnel; bornholmer: night bridge crowd. Both lifted for phones
export const { setup, update } = wrap(O, { stop: { exposure: 1.35 }, bornholmer: { exposure: 1.5 } });
