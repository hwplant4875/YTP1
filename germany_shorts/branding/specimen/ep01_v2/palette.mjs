import { chromium } from 'playwright';
import { FONTS, K, ICON, place, sharkSolid } from './eng2.mjs';
const P = [['WATER', '#4cb3e8', '#1f7fc4', place(320, 300, 0.48, sharkSolid('#fff', K.navy, 12))], ['LAND', '#7fd36e', '#3e9f4f', `<g transform="translate(320 300) scale(1.3)">${ICON.rhino()}</g>`], ['AIR', '#ffc46b', '#ff8f45', `<g transform="translate(320 300) scale(1.6)"><path d="M-120 20 Q-40 -60 60 -10 L140 -40 L90 10 Q40 60 -40 50Z" fill="#fff" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><path d="M-10 -10 Q20 -110 90 -120 Q60 -40 30 0Z" fill="#fff" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><circle cx="85" cy="-20" r="7" fill="${K.navy}"/></g>`], ['AIR (alt)', '#e3f4ff', '#b9e1f7', `<g transform="translate(320 300) scale(1.6)"><path d="M-120 20 Q-40 -60 60 -10 L140 -40 L90 10 Q40 60 -40 50Z" fill="#fff" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><path d="M-10 -10 Q20 -110 90 -120 Q60 -40 30 0Z" fill="#fff" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><circle cx="85" cy="-20" r="7" fill="${K.navy}"/></g>`]];
let s = `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1280">`;
P.forEach(([n, a, b, ic], i) => { const x = (i % 2) * 640, y = Math.floor(i / 2) * 640;
  s += `<defs><linearGradient id="g${i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient></defs><g transform="translate(${x} ${y})"><rect width="640" height="640" fill="url(#g${i})"/>${ic}
  <text x="320" y="110" font-family="Black" font-size="80" fill="#fff" stroke="${K.navy}" stroke-width="10" paint-order="stroke" text-anchor="middle">${n}</text><text x="320" y="560" font-family="Black" font-size="40" fill="${K.navy}" text-anchor="middle">${a} → ${b}</text></g>`; });
s += '</svg>';
const br = await chromium.launch(); const p = await br.newPage({ viewport: { width: 1280, height: 1280 } });
await p.setContent(`<style>${FONTS}body{margin:0}</style>${s}`); await p.waitForTimeout(50);
await p.screenshot({ path: '/mnt/project-files/plans/halfcut/v2_specimen/habitat_colors.png' }); await br.close();
