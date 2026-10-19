import { frame, TOTAL } from './main.mjs';
let bad = 0; for (let T = 0; T < TOTAL; T += 0.1) { const s = frame(T); if (/NaN|undefined|Infinity/.test(s)) { if (bad++ < 8) console.log('bad at', T.toFixed(1), (s.match(/.{60}(NaN|undefined|Infinity).{30}/) || [''])[0]); } }
console.log('bad', bad, 'TOTAL', TOTAL);
