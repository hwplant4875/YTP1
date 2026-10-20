// X-RAY ZOO banner v3: plain blueprint background + wordmark, one render per Google font
import { chromium } from 'playwright';
import fs from 'fs';
const FD = '/tmp/claude-0/fonts/', OUT = '/tmp/claude-0/brand2/';
const FONTS = ['Unbounded', 'Fredoka', 'BricolageGrotesque', 'LilitaOne'];
const face = FONTS.map(f => `@font-face{font-family:'${f}';src:url(data:font/woff2;base64,${fs.readFileSync(FD + f + '.woff2').toString('base64')}) format('woff2');}`).join('');
const N = '#0d1b3a', CY = '#8ff0ff';
const grid = (st, o) => { let s = ''; for (let x = 0; x <= 2560; x += st) s += `<path d="M${x} 0 V1440" stroke="#fff" opacity="${o}"/>`; for (let y = 0; y <= 1440; y += st) s += `<path d="M0 ${y} H2560" stroke="#fff" opacity="${o}"/>`; return s; };
const banner = (font, size, ls, a = 'X-RAY', b = 'ZOO') => `<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440"><rect width="2560" height="1440" fill="#1d5fae"/>${grid(40, 0.1)}${grid(200, 0.2)}
  <text x="1280" y="760" font-family="${font}" font-size="${size}" text-anchor="middle" fill="#fff" letter-spacing="${ls}">${a} <tspan fill="${CY}">${b}</tspan></text>
  <path d="M640 ${a === "X-RAY" ? 812 : 842} L1920 ${a === "X-RAY" ? 812 : 842}" stroke="${CY}" stroke-width="8" stroke-dasharray="28 18" stroke-linecap="round"/>
  <text x="1280" y="${a === "X-RAY" ? 890 : 916}" font-family="${font}" font-size="54" text-anchor="middle" fill="#ffffff" opacity=".92" letter-spacing="6">SEE WHAT'S INSIDE ANIMALS</text></svg>`;
const SZ = { Unbounded: [170, 4], Fredoka: [230, 4], BricolageGrotesque: [230, 0], LilitaOne: [240, 6] };
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2560, height: 1440 } });
for (const f of FONTS) { await p.setContent(`<style>${face}body{margin:0}</style>${banner(f, ...SZ[f])}`); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await p.screenshot({ path: `${OUT}banner_${f}.png` }); }
await p.setContent(`<style>${face}body{margin:0}</style>${banner('Fredoka', 250, 2, 'X-Ray', 'Zoo')}`); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150); await p.screenshot({ path: `${OUT}banner_Fredoka_mixed.png` });
await b.close(); console.log('ok');
