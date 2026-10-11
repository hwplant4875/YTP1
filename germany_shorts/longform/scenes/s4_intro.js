// Short #4 "Friedrichstraße, the one stop": portrait framing of the cold-open scene (see s1_portrait.js).
// cab: the driver's view into the ghost station, lifted for phone screens.
import * as O from './intro.js';
import { wrap } from './s1_portrait.js';
export const { setup, update } = wrap(O, { cab: { exposure: 1.9 } });
