import { SC, at, LEAD, TOTAL } from './tl.mjs';
import fs from 'fs';
const st = id => SC.find(s => s.id === id).start;
const ev = []; const E = (f, id, p, v, off = 0) => ev.push([f, +(st(id) + (typeof p === 'number' ? p : at(id, p)) + off).toFixed(3), v]);
const voice = SC.map(s => [`audio/v_${s.id}.mp3`, +(s.start + LEAD).toFixed(3), s.dur]);
SC.forEach((s, i) => { if (i) ev.push(['mus/sfx_whoosh.mp3', +(s.start - 0.15).toFixed(3), 0.2]); });
const D = 'mus/sfx_ding.mp3', P = 'mus/sfx_pop.mp3';
[['h02', 'three grams'], ['h03', 'five centimeters'], ['h04', 'fifty times'], ['h04', 'eighty'], ['h05', 'figure eight'], ['h08', 'a quarter'], ['h09', 'twelve hundred'], ['h10', 'two hundred and fifty'],
 ['h14', 'fifteen licks'], ['h15', 'thousands'], ['h18', 'super'.length ? 'A hummingbird can remember' : ''], ['h20', 'torpor'], ['h25', 'eight hundred'], ['h26', 'More than six thousand'], ['h29', 'three hundred and sixty']].forEach(([id, p]) => E(D, id, p, 0.26));
[['h01', 'Today'], ['h02', 'single coin'], ['h03', 'Cuba'], ['h06', 'shoulder'], ['h06', 'twist its wing'], ['h07', 'hover'], ['h07', 'backwards'], ['h07', 'upside down'], ['h08', 'flight muscles'], ['h09', 'huge'], ['h11', 'tiny engine'],
 ['h12', 'Flowers'], ['h12', 'very long tongue'], ['h13', 'split in two'], ['h13', 'open up'], ['h16', 'tiny insects'], ['h16', 'Sugar for energy'], ['h16', 'bugs for building'], ['h17', 'Yellow pollen'], ['h17', 'tiny taxi'],
 ['h18', 'memory'], ['h19', 'ultraviolet'], ['h19', 'patterns'], ['h22', 'tiny'], ['h22', 'it flies'], ['h23', 'no red paint'], ['h23', 'tiny layers'], ['h23', 'Turn the bird'], ['h25', 'doubles its weight'], ['h25', 'nonstop'],
 ['h27', 'half a walnut'], ['h27', 'soft plant fluff'], ['h27', 'spider silk'], ['h28', 'jelly bean'], ['h29', 'only in the Americas'], ['h30', 'beak longer'], ['h31', 'Wings that spin'], ['h31', 'A heart'], ['h31', 'A brushy tongue'], ['h31', 'super memory'], ['h31', 'switch off'], ['h31', 'What should we open']].forEach(([id, p]) => E(P, id, p, 0.28, 0.1));
E('mus/sfx_hum.mp3', 'h04', 'blur', 0.22, -0.5); E('mus/sfx_hum.mp3', 'h04', 'humming sound', 0.28, -0.2);
E('mus/sfx_heart.mp3', 'h09', 'twelve hundred', 0.22, -0.3); E('mus/sfx_lick.mp3', 'h14', 'And it does this', 0.25); E('mus/sfx_lick.mp3', 'h13', 'snap shut', 0.25);
E('mus/sfx_zzz.mp3', 'h20', 'deep sleep', 0.2, 0.6); E('mus/sfx_chirp.mp3', 'h24', 'loud chirp', 0.3, 0.05); E('mus/sfx_whoosh.mp3', 'h24', 'dives straight down', 0.35, 0.2);
fs.writeFileSync('mixplan.json', JSON.stringify({ total: TOTAL, voice, ev }));
console.log(voice.length, ev.length, TOTAL);
