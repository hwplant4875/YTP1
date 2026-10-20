// builds each short's timeline: hook (new narration over a spectacle moment) then clips of the long-form scenes
import fs from 'fs';
import { SC, at, endOf, LEAD } from '/tmp/claude-0/hb2/tl.mjs';
const SPEC = JSON.parse(fs.readFileSync('/tmp/claude-0/hbs/spec.json'));
const hookEnd = id => JSON.parse(fs.readFileSync(`/tmp/claude-0/hbs/audio/h_${id}.json`)).character_end_times_seconds.slice(-1)[0];
const sc = id => SC.find(s => s.id === id);
export const PLANS = {};
for (const s of SPEC) {
  const parts = []; let T = 0;
  // hook: narration starts at 0.05 s, visuals play the spectacle moment from frame 0
  const hd = hookEnd(s.id), hid = s.parts[0][0], hlen = 0.05 + hd + 0.4;
  parts.push({ kind: 'hook', id: hid, t0: 0, T0: 0, len: hlen, head: s.hh, vo: [`/tmp/claude-0/hbs/audio/h_${s.id}.mp3`, 0.05, 0, hd + 0.05] });
  T = hlen;
  for (const [id, from, to, head] of s.parts.map(p => [...p, s.hh])) {
    const S = sc(id), a = from ? at(id, from) : LEAD, b = to ? endOf(id, to) : LEAD + S.dur;
    const t0 = a - 0.12, len = (b + 0.35) - t0;
    parts.push({ kind: 'clip', id, t0, T0: T, len, head, vo: [`/tmp/claude-0/hb2/audio/v_${id}.mp3`, T + 0.12, a - LEAD, b - a + 0.08], gstart: S.start });
    T += len;
  }
  // outro: payoff line + comment question, then a short hold so the ending lands instead of cutting off
  const O = JSON.parse(fs.readFileSync(`/tmp/claude-0/hbs/audio/o_${s.id}.json`)), od = O.character_end_times_seconds.slice(-1)[0], olen = 0.15 + od + 1.1;
  parts.push({ kind: 'outro', id: 'outro', t0: 0, T0: T, len: olen, head: s.hh, vo: [`/tmp/claude-0/hbs/audio/o_${s.id}.mp3`, T + 0.15, 0, od + 0.05] });
  T += olen;
  PLANS[s.id] = { id: s.id, parts, total: T };
}
if (process.argv[2] === 'dump') { fs.writeFileSync('/tmp/claude-0/hbs/plans.json', JSON.stringify(PLANS, null, 1)); for (const p of Object.values(PLANS)) console.log(p.id, p.total.toFixed(2), p.parts.map(x => x.id + ':' + x.len.toFixed(1)).join(' ')); }
