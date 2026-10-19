import fs from 'fs'; import { SC, LEAD } from './tl.mjs';
const out = []; const ts = s => { const ms = Math.round(s * 1000), h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, se = Math.floor(ms / 1000) % 60; return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(se).padStart(2, '0')},${String(ms % 1000).padStart(3, '0')}`; };
for (const s of SC) { const a = JSON.parse(fs.readFileSync(`audio/a_${s.id}.json`)); const ch = a.characters, st = a.character_start_times_seconds, en = a.character_end_times_seconds;
  // words
  const ws = []; let cur = null; ch.forEach((c, i) => { if (c === ' ') { if (cur) ws.push(cur); cur = null; } else { if (!cur) cur = { w: '', s: st[i], e: en[i] }; cur.w += c; cur.e = en[i]; } }); if (cur) ws.push(cur);
  let line = []; const flush = () => { if (!line.length) return; out.push([s.start + LEAD + line[0].s, s.start + LEAD + line[line.length - 1].e, line.map(x => x.w).join(' ')]); line = []; };
  for (const w of ws) { const len = line.map(x => x.w).join(' ').length + w.w.length; if (len > 42) flush(); line.push(w); if (/[.?!:…]$/.test(w.w)) flush(); else if (/,$/.test(w.w) && line.map(x => x.w).join(' ').length > 20) flush(); }
  flush(); }
fs.writeFileSync('out/specimen001.srt', out.map(([a, b, t], i) => `${i + 1}\n${ts(a)} --> ${ts(Math.max(b, a + 0.6))}\n${t}\n`).join('\n'));
console.log(out.length); const ch = SC.map(s => [s.id, s.start]); console.log(JSON.stringify(ch));
