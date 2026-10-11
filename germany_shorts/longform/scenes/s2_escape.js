// Short #2 "The Escape": portrait framing of the escape scene (see s1_portrait.js). Dark tunnel shots are lifted
// for phone screens; flag turns slightly right so the technician with his lamp is fully in frame.
import * as O from './escape.js';
import { wrap } from './s1_portrait.js';
export const { setup, update } = wrap(O, {
  teaser: { exposure: 1.15 },
  tech: { exposure: 1.5 },
  plan: { exposure: 1.3 },
  allowed: { exposure: 1.3 },
  flag: { yaw: -0.09, exposure: 1.15 },
  west: { exposure: 1.3 },
});
