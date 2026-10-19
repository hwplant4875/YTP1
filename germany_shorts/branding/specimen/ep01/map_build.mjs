import fs from 'fs'; import { geoNaturalEarth1, geoPath, geoInterpolate } from 'd3-geo'; import { feature } from 'topojson-client';
const land = feature(JSON.parse(fs.readFileSync('node_modules/world-atlas/land-110m.json')), 'land');
// frame the Indian Ocean: Africa to Australia
const pr = geoNaturalEarth1().center([67, -22]).scale(880).translate([900, 560]);
const d = geoPath(pr)(land);
const sa = [19.35, -34.6], au = [114.1, -21.9];
const route = [];
// outbound: south of the Indian Ocean (south of ~ -35), back slightly north
const wp1 = [[19.35,-34.6],[30,-38],[50,-40],[75,-40],[95,-37],[108,-31],[114.1,-21.9]];
const wp2 = [[114.1,-21.9],[105,-27],[85,-33],[60,-36],[38,-37],[25,-35.5],[19.6,-34.8]];
const line = wp => { const pts=[]; for (let i=0;i<wp.length-1;i++){ const f=geoInterpolate(wp[i],wp[i+1]); for(let k=0;k<20;k++) pts.push(pr(f(k/20))); } pts.push(pr(wp[wp.length-1])); return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L'); };
fs.writeFileSync('../map.json', JSON.stringify({ land: d, out: line(wp1), back: line(wp2), sa: pr(sa), au: pr(au), grat: [-60,-45,-30,-15,0,15].map(lat=>{const pts=[];for(let lo=-20;lo<=160;lo+=4)pts.push(pr([lo,lat]));return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L');}).concat([0,20,40,60,80,100,120,140].map(lo=>{const pts=[];for(let la=-70;la<=40;la+=4)pts.push(pr([lo,la]));return 'M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L');})) }));
console.log(d.length, pr(sa), pr(au));
