import { SC, at, LEAD, TOTAL } from './tl2.mjs';
import fs from 'fs';
const st = id => SC.find(s => s.id === id).start;
const ev = []; const E = (f, id, p, v, off = 0) => ev.push([f, +(st(id) + (typeof p === 'number' ? p : at(id, p)) + off).toFixed(3), v]);
const voice = SC.map(s => [`audio/v_${s.id}.mp3`, +(s.start + LEAD).toFixed(3), s.dur]);
SC.forEach((s, i) => { if (i) ev.push(['mus/sfx_whoosh.mp3', +(s.start - 0.15).toFixed(3), 0.22]); });
const D = 'mus/sfx_ding.mp3', P = 'mus/sfx_pop.mp3';
[['n02', 'six meters'], ['n02', 'two tons'], ['n03', 'zero bones'], ['n05', 'seventy'], ['n07', 'three hundred'], ['n07', 'conveyor belt'], ['n09', 'eighteen times'], ['n10', "It's the liver"], ['n10', 'a quarter'],
 ['n13', 'About twenty'], ['n15', 'forty'], ['n18', 'fourteen degrees'], ['n26', 'a year'], ['n27b', 'so they are protected']].forEach(([id, p]) => E(D, id, p, 0.28));
[['n03', 'cartilage'], ['n03', 'nose'], ['n03', 'ears'], ['n06', 'denticles'], ['n07b', 'for cutting'], ['n07b', 'for holding'], ['n10', 'not the heart'], ['n10', 'not the stomach'], ['n11', 'pool float'], ['n14', 'airplane wings'], ['n14', 'stops it from rolling'], ['n14', 'the engine'],
 ['n16', 'five gill'], ['n19', 'spiral valve'], ['n19', 'gross one'], ['n20', 'feel electricity'], ['n21', 'lateral line'], ['n22', 'two nostrils'], ['n23', 'mirror'], ['n24', 'spy-hopping'],
 ['n25', 'it smells'], ['n25', 'feels the movement'], ['n25', 'it sees'], ['n25', 'uses electricity'], ['n28', 'No bones'], ['n28', 'Teeth on its skin'], ['n28', 'A liver that floats'], ['n28', 'Muscles that stay'], ['n28', 'sixth sense']].forEach(([id, p]) => E(P, id, p, 0.3, 0.1));
E('mus/sfx_splash.mp3', 'n15', 'fly right out', 0.45, -0.05); E('mus/sfx_splash.mp3', 'n15', 'fly right out', 0.28, 2 * 1100 / 1250 / 0.6 - 0.05); E('mus/sfx_bubbles.mp3', 'n11', 'full of oil', 0.3); E('mus/sfx_bubbles.mp3', 'n16', 'Water goes in', 0.25);
fs.writeFileSync('mixplan.json', JSON.stringify({ total: TOTAL, voice, ev }));
console.log(voice.length, ev.length, TOTAL);
