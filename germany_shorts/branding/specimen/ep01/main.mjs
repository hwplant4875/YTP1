import * as A from './scA.mjs'; import * as B from './scB.mjs'; import * as Cc from './scC.mjs';
import { sceneAt, TOTAL } from './tl.mjs';
export { FONTS, W, H } from './eng.mjs';
export { TOTAL };
const F = { ...A, ...B, ...Cc };
export const frame = T => { const [s, t] = sceneAt(T); return F[s.id](t, s.len); };
