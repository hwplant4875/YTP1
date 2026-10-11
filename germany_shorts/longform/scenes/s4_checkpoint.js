// Short #4 "Friedrichstraße, the one stop": portrait framing of the March 1974 checkpoint scene (see s1_portrait.js).
// shot: turn right and widen so the hidden officer stepping out on the right stays in the narrow frame.
import * as O from './checkpoint.js';
import { wrap } from './s1_portrait.js';
export const { setup, update } = wrap(O, {
  bomb: { exposure: 1.1 },
  shot: { yaw: -0.13, fovScale: 1.12, exposure: 1.2 },
  steps: { exposure: 1.25 },
});
