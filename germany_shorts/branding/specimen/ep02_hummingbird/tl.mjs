// timeline v2: scene order, durations and word timing from the Will narration alignment
import fs from 'fs';
const A = '/tmp/claude-0/hb2/audio/';
export const LEAD = 0.25, GAP = 0.5, TAIL = 3.0;
export const SC = JSON.parse(fs.readFileSync(A + 'scenes.json'));
const al = {}; for (const s of SC) al[s.id] = JSON.parse(fs.readFileSync(A + `a_${s.id}.json`));
let t = 0;
for (const [i, s] of SC.entries()) { s.idx = i + 1; s.start = t; s.len = LEAD + s.dur + (i === SC.length - 1 ? TAIL : GAP); t += s.len; }
export const TOTAL = t;
const txt = id => al[id].characters.join('');
// local time when `phrase` starts being spoken (nth occurrence)
export function at(id, phrase, n = 0) {
  const s = txt(id); let i = -1;
  for (let k = 0; k <= n; k++) { i = s.indexOf(phrase, i + 1); if (i < 0) throw new Error(`phrase not found in ${id}: ${phrase}`); }
  return LEAD + al[id].character_start_times_seconds[i];
}
export const endOf = (id, phrase) => { const s = txt(id), i = s.indexOf(phrase); if (i < 0) throw new Error(`not found ${id}: ${phrase}`);
  return LEAD + al[id].character_end_times_seconds[i + phrase.length - 1]; };
export const sceneAt = T => { for (const s of SC) if (T < s.start + s.len) return [s, T - s.start]; const s = SC[SC.length - 1]; return [s, T - s.start]; };
