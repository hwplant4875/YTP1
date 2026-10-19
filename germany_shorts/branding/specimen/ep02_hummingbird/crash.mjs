import { frame } from './main.mjs';
for (const i of [3856, 11184, 13980]) { const s = frame(i / 60); console.log(i, s.length, (s.match(/r="-[^"]*"|width="-[^"]*"|height="-[^"]*"|rx="-[^"]*"|e[+-]\d+/g) || []).slice(0, 5)); }
