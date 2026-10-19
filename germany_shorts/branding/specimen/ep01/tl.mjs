// timeline: scene order, durations and word timing from the narration alignment
import fs from 'fs';
const A = '/tmp/claude-0/sp/audio/';
export const LEAD = 0.35, GAP = 1.8;
export const SC = JSON.parse(fs.readFileSync(A + 'scenes2.json'));
const al = {}; for (const s of SC) al[s.id] = JSON.parse(fs.readFileSync(A + `a_${s.id}.json`));
let t = 0;
for (const s of SC) { s.start = t; s.len = LEAD + s.dur + (s.id === 's23' ? 3.5 : GAP); t += s.len; }
export const TOTAL = t;
// local time (scene clock) when `phrase` starts being spoken (nth occurrence)
export function at(id, phrase, n = 0) {
  const a = al[id]; const text = a.characters.join(''); let i = -1;
  for (let k = 0; k <= n; k++) { i = text.indexOf(phrase, i + 1); if (i < 0) throw new Error(`phrase not found in ${id}: ${phrase}`); }
  return LEAD + a.character_start_times_seconds[i];
}
export const endOf = (id, phrase) => { const a = al[id]; const text = a.characters.join(''); const i = text.indexOf(phrase); if (i < 0) throw new Error(`not found ${id}: ${phrase}`);
  return LEAD + a.character_end_times_seconds[i + phrase.length - 1]; };
// words list with times for on-screen lyric lines
export function W(id, phrase) {
  const a = al[id]; const text = a.characters.join(''); const i0 = text.indexOf(phrase); if (i0 < 0) throw new Error(`not found ${id}: ${phrase}`);
  const out = []; let i = i0;
  for (const w of phrase.split(' ')) { const j = text.indexOf(w, i); out.push([w, LEAD + a.character_start_times_seconds[j]]); i = j + w.length; }
  return out;
}
export const sceneAt = T => { for (const s of SC) if (T < s.start + s.len) return [s, T - s.start]; const s = SC[SC.length - 1]; return [s, T - s.start]; };
