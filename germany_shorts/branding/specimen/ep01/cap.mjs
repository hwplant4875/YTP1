// narration caption: shows the most recent phrase that has started, words appearing as spoken
import { words, C } from './eng.mjs';
import { W } from './tl.mjs';
const cache = {};
export const cap = (id, list, t, { x = 110, y = 1000, size = 58, fill = C.ink } = {}) => {
  let cur = null;
  for (const [p, hi] of list) { const k = id + '|' + p; const w = cache[k] || (cache[k] = W(id, p)); if (t >= w[0][1] - 0.05) cur = [w, hi]; }
  return cur ? words(x, y, cur[0], t, { size, fill, hi: cur[1] || {} }) : '';
};
