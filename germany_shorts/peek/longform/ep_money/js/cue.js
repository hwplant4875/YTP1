// Narration cues: the global time of a spoken word, looked up by beat + word text (+ occurrence)
import { WORDS, OFF } from './words.js';
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9'-]/g, '');
function find(beat, word, n) {
  const L = WORDS[beat], q = norm(word);
  let c = 0;
  for (const it of L) if (norm(it[0]) === q && ++c === n) return it;
  c = 0;
  for (const it of L) if (norm(it[0]).startsWith(q) && ++c === n) return it;
  throw new Error(`cue not found: ${beat} "${word}" #${n}`);
}
export const cue = (beat, word, n = 1) => find(beat, word, n)[1];
export const cueEnd = (beat, word, n = 1) => find(beat, word, n)[2];
export const beatStart = (beat) => OFF[beat];
export const beatEnd = (beat) => { const L = WORDS[beat]; return L[L.length - 1][2]; };
export const END = OFF.end;
