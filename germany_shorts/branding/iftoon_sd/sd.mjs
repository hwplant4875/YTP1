import { chromium } from 'playwright';
import fs from 'fs';
const INK='#1E1724', SKIN='#FFE6D4', SKIN_SH='#F4C2A8', HAIR='#2E2838', HAIR_SH='#1B1622', HAIR_HI='#5A5070',
 HOOD='#F5B83A', HOOD_SH='#D58C1F', HOOD_HI='#FFD77A', PANT='#2D3654', PANT_SH='#1E253C', SHOE='#FFFFFF', SHOE_SH='#D5D9E2';
const LW=5;

function head(eyes){ // head drawn in a 500-wide box, head centre ~ (250,230)
  const eyeL = eyes==='sharp' ? sharpEye(196,258,-1) : cuteEye(194,252,-1);
  const eyeR = eyes==='sharp' ? sharpEye(304,258,1) : cuteEye(306,252,1);
  const mouth = eyes==='sharp'
    ? `<path d="M232 322 Q250 334 272 318" fill="none" stroke="${INK}" stroke-width="4.5" stroke-linecap="round"/>
       <path d="M262 321 l6 -3" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`
    : `<path d="M234 316 Q250 344 266 316 Z" fill="#7A2E3A" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/>
       <path d="M241 329 Q250 337 259 329 Q250 325 241 329Z" fill="#F07C86"/>`;
  return `
  <!-- back hair -->
  <path d="M92 230 C78 96 176 34 252 34 C332 34 424 96 410 230 C414 300 400 352 382 372 C372 330 366 300 360 262 L142 262 C136 300 130 332 120 372 C100 350 88 300 92 230Z" fill="${HAIR_SH}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <!-- face -->
  <path d="M122 214 C122 122 378 122 378 214 C380 300 330 368 250 370 C170 368 120 300 122 214Z" fill="${SKIN}" stroke="${INK}" stroke-width="${LW}"/>
  <clipPath id="faceclip${eyes}"><path d="M122 214 C122 122 378 122 378 214 C380 300 330 368 250 370 C170 368 120 300 122 214Z"/></clipPath>
  <g clip-path="url(#faceclip${eyes})">
    <path d="M110 150 L400 150 L400 232 C360 214 330 206 300 212 C270 220 240 214 210 208 C170 200 140 210 110 236Z" fill="${SKIN_SH}" opacity="0.9"/>
    <path d="M340 230 C370 270 360 330 300 362 L400 400 L400 220Z" fill="${SKIN_SH}" opacity="0.7"/>
  </g>
  <!-- blush -->
  <ellipse cx="160" cy="300" rx="26" ry="13" fill="#FF8C8C" opacity="0.45"/><ellipse cx="340" cy="300" rx="26" ry="13" fill="#FF8C8C" opacity="0.45"/>
  <g stroke="#E5606A" stroke-width="2.6" stroke-linecap="round"><path d="M146 306 l8 -12 M158 306 l8 -12 M170 306 l8 -12"/><path d="M326 306 l8 -12 M338 306 l8 -12 M350 306 l8 -12"/></g>
  ${eyeL}${eyeR}
  <path d="M248 292 l4 4" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>
  ${mouth}
  <!-- front bangs -->
  <path d="M106 228 C108 118 186 66 256 66 C338 66 400 124 396 228
           Q386 196 372 176 Q368 214 352 236 Q346 196 330 168 Q320 212 300 232 Q298 190 284 160 Q270 204 250 226 Q246 186 236 158
           Q220 202 198 232 Q196 194 186 168 Q170 206 150 230 Q148 200 138 182 Q124 206 106 228Z"
        fill="${HAIR}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <!-- side locks -->
  <path d="M112 200 C104 250 110 300 128 340 Q132 300 142 270 Q140 240 138 214Z" fill="${HAIR}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M390 200 C398 250 392 300 374 340 Q370 300 360 270 Q362 240 364 214Z" fill="${HAIR}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <!-- hair shine -->
  <path d="M168 112 Q210 90 254 92 Q232 100 214 116 Q190 112 168 112Z" fill="${HAIR_HI}"/>
  <path d="M286 96 Q330 102 358 132 Q330 120 300 118Z" fill="${HAIR_HI}"/>
`;
}
function cuteEye(cx,cy,s){
  const id='ig'+cx;
  return `<defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1A12"/><stop offset="0.55" stop-color="#7A4420"/><stop offset="1" stop-color="#E0A050"/></linearGradient></defs>
  <ellipse cx="${cx}" cy="${cy+4}" rx="31" ry="40" fill="#FFFFFF"/>
  <ellipse cx="${cx}" cy="${cy+6}" rx="26" ry="36" fill="url(#${id})"/>
  <ellipse cx="${cx}" cy="${cy+4}" rx="12" ry="17" fill="#1A0F0A"/>
  <ellipse cx="${cx-9}" cy="${cy-12}" rx="10" ry="12" fill="#FFF"/>
  <circle cx="${cx+11}" cy="${cy+20}" r="5" fill="#FFF"/>
  <path d="M${cx-36} ${cy-22} Q${cx} ${cy-50} ${cx+36} ${cy-24} L${cx+s*0+38} ${cy-18} Q${cx} ${cy-40} ${cx-34} ${cy-14}Z" fill="${INK}"/>
  <path d="M${cx+s*36} ${cy-22} l${s*12} -10" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>
  <path d="M${cx-18} ${cy+46} Q${cx} ${cy+50} ${cx+18} ${cy+46}" fill="none" stroke="${INK}" stroke-width="2.5" stroke-linecap="round"/>`;
}
function sharpEye(cx,cy,s){
  const id='sg'+cx;
  return `<defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C1418"/><stop offset="1" stop-color="#C0453A"/></linearGradient></defs>
  <path d="M${cx-34} ${cy} Q${cx} ${cy-26} ${cx+34} ${cy-4} Q${cx} ${cy+24} ${cx-34} ${cy}Z" fill="#FFF"/>
  <clipPath id="ec${cx}"><path d="M${cx-34} ${cy} Q${cx} ${cy-26} ${cx+34} ${cy-4} Q${cx} ${cy+24} ${cx-34} ${cy}Z"/></clipPath>
  <g clip-path="url(#ec${cx})"><ellipse cx="${cx+s*4}" cy="${cy}" rx="17" ry="22" fill="url(#${id})"/><ellipse cx="${cx+s*4}" cy="${cy}" rx="6" ry="10" fill="#120A0C"/><circle cx="${cx+s*4-6}" cy="${cy-8}" r="4.5" fill="#FFF"/></g>
  <path d="M${cx-38} ${cy+2} Q${cx} ${cy-30} ${cx+38} ${cy-8}" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>
  <path d="M${cx+s*36} ${cy-6} l${s*10} -6" stroke="${INK}" stroke-width="4" stroke-linecap="round"/>
  <path d="M${cx-14} ${cy+18} Q${cx+6} ${cy+20} ${cx+24} ${cy+12}" fill="none" stroke="${INK}" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M${cx-30} ${cy-40} Q${cx} ${cy-50} ${cx+30} ${cy-36}" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round" transform="rotate(${s*-6} ${cx} ${cy})"/>`;
}
function cuteBody(){ // head-to-body 1:2 ; head occupies y 0..372, body 350..700
  return `
  <!-- legs -->
  <path d="M200 592 L196 650 L238 650 L240 592Z" fill="${PANT}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M262 592 L264 650 L306 650 L302 592Z" fill="${PANT}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M184 646 C176 646 168 664 172 676 C176 690 240 690 244 676 L244 650Z" fill="${SHOE}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M258 650 L258 676 C262 690 326 690 330 676 C334 664 326 646 318 646Z" fill="${SHOE}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M176 672 Q210 680 242 672" stroke="${SHOE_SH}" stroke-width="6" fill="none"/><path d="M260 672 Q292 680 326 672" stroke="${SHOE_SH}" stroke-width="6" fill="none"/>
  <!-- left arm (down) -->
  <path d="M166 392 C138 420 124 470 120 520 L156 528 C160 486 172 450 190 424Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <circle cx="136" cy="534" r="20" fill="${SKIN}" stroke="${INK}" stroke-width="${LW}"/>
  <!-- hoodie body -->
  <path d="M180 360 C150 368 140 410 142 450 L138 566 C138 600 168 606 250 606 C332 606 362 600 362 566 L358 450 C360 410 350 368 320 360 Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <clipPath id="hc"><path d="M180 360 C150 368 140 410 142 450 L138 566 C138 600 168 606 250 606 C332 606 362 600 362 566 L358 450 C360 410 350 368 320 360 Z"/></clipPath>
  <g clip-path="url(#hc)"><path d="M300 360 C330 420 330 520 300 610 L380 610 L380 360Z" fill="${HOOD_SH}"/><path d="M150 590 Q250 560 350 590 L350 620 L150 620Z" fill="${HOOD_SH}"/><path d="M160 400 Q170 380 190 372 Q176 420 172 470 Q160 440 160 400Z" fill="${HOOD_HI}"/></g>
  <path d="M138 572 Q250 588 362 572" fill="none" stroke="${INK}" stroke-width="3"/>
  <!-- pocket + logo -->
  <path d="M196 500 L304 500 L318 556 L182 556Z" fill="${HOOD_SH}" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/>
  <!-- hood collar -->
  <path d="M170 356 Q250 420 330 356 Q348 380 316 398 Q250 426 184 398 Q152 380 170 356Z" fill="${HOOD_SH}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M214 396 L210 448 M286 396 L290 448" stroke="#FFF" stroke-width="5" stroke-linecap="round"/><circle cx="210" cy="452" r="5" fill="#FFF" stroke="${INK}" stroke-width="2"/><circle cx="290" cy="452" r="5" fill="#FFF" stroke="${INK}" stroke-width="2"/>
  <!-- right arm (waving) -->
  <path d="M322 392 C352 384 380 360 404 324 L432 346 C406 390 370 422 334 432Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <g transform="translate(424 318) rotate(-20)"><path d="M-20 10 C-24 -10 -16 -26 -4 -26 L-4 -38 C-4 -46 8 -46 8 -38 L8 -24 C20 -22 24 -6 18 10 C14 22 -16 22 -20 10Z" fill="${SKIN}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/></g>
  <g stroke="${INK}" stroke-width="4" stroke-linecap="round"><path d="M452 286 l14 -10 M460 306 l18 -2 M444 268 l8 -14"/></g>`;
}
function tallBody(){ // head scaled separately; body from y 340 to 980 (1:3.5)
  return `
  <!-- legs long -->
  <path d="M206 640 L196 900 L240 900 L250 650Z" fill="${PANT}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M250 650 L262 900 L306 900 L296 640Z" fill="${PANT}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M276 650 L286 900 L306 900 L296 640Z" fill="${PANT_SH}"/>
  <path d="M250 650 L250 760" stroke="${INK}" stroke-width="3"/>
  <path d="M180 896 C170 898 164 916 168 928 C172 942 242 942 246 928 L244 900Z" fill="${SHOE}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M258 900 L256 928 C260 942 330 942 334 928 C338 916 330 898 320 896Z" fill="${SHOE}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M172 924 Q208 932 244 924" stroke="${SHOE_SH}" stroke-width="6" fill="none"/><path d="M258 924 Q296 932 332 924" stroke="${SHOE_SH}" stroke-width="6" fill="none"/>
  <!-- hoodie (long, oversized) -->
  <path d="M186 372 C150 380 132 420 132 470 L128 640 C128 668 160 676 250 676 C340 676 372 668 372 640 L368 470 C368 420 350 380 314 372Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <clipPath id="hc2"><path d="M186 372 C150 380 132 420 132 470 L128 640 C128 668 160 676 250 676 C340 676 372 668 372 640 L368 470 C368 420 350 380 314 372Z"/></clipPath>
  <g clip-path="url(#hc2)"><path d="M306 372 C340 450 340 580 310 680 L380 680 L380 372Z" fill="${HOOD_SH}"/><path d="M140 640 Q250 620 360 640 L360 690 L140 690Z" fill="${HOOD_SH}"/></g>
  <path d="M128 646 Q250 662 372 646" fill="none" stroke="${INK}" stroke-width="3"/>
  <!-- arms bent into pocket -->
  <path d="M150 400 C126 440 120 500 140 560 L196 590 L206 560 L172 530 C164 490 168 450 180 420Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M350 400 C374 440 380 500 360 560 L304 590 L294 560 L328 530 C336 490 332 450 320 420Z" fill="${HOOD}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M332 410 C352 450 356 510 344 548 L330 540 C340 500 336 460 322 430Z" fill="${HOOD_SH}"/>
  <path d="M190 560 L310 560 L322 616 L178 616Z" fill="${HOOD_SH}" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M172 368 Q250 430 328 368 Q348 394 316 412 Q250 440 184 412 Q152 394 172 368Z" fill="${HOOD_SH}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <path d="M216 410 L212 470 M284 410 L288 470" stroke="#FFF" stroke-width="5" stroke-linecap="round"/><circle cx="212" cy="474" r="5" fill="#FFF" stroke="${INK}" stroke-width="2"/><circle cx="288" cy="474" r="5" fill="#FFF" stroke="${INK}" stroke-width="2"/>`;
}
const sticker = `<filter id="sticker" x="-20%" y="-20%" width="140%" height="140%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="11" result="d1"/><feFlood flood-color="#FFFFFF"/><feComposite in2="d1" operator="in" result="white"/>
  <feMorphology in="SourceAlpha" operator="dilate" radius="14" result="d2"/><feFlood flood-color="${INK}"/><feComposite in2="d2" operator="in" result="dark"/>
  <feDropShadow in="dark" dx="0" dy="8" stdDeviation="6" flood-color="#000" flood-opacity="0.25" result="ds"/>
  <feMerge><feMergeNode in="ds"/><feMergeNode in="white"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`;
const cute = (x,y,sc)=>`<g transform="translate(${x} ${y}) scale(${sc})" filter="url(#sticker)"><g>${cuteBody()}</g><g>${head('cute')}</g></g>`;
const tall = (x,y,sc)=>`<g transform="translate(${x} ${y}) scale(${sc})" filter="url(#sticker)"><g>${tallBody()}</g><g transform="translate(250 380) scale(0.78) translate(-250 -366)">${head('sharp')}</g></g>`;
const halftone = (id,c1,c2)=>`<pattern id="${id}" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="${c1}"/><circle cx="9" cy="9" r="3.2" fill="${c2}"/></pattern>`;
const html = `<!doctype html><html><head><style>@font-face{font-family:YT;src:url('file:///home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf')}
@font-face{font-family:PT;src:url('file:///home/user/YTP1/germany_shorts/fonts/Pretendard-ExtraBold.otf')} body{margin:0}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1500" viewBox="0 0 1800 1500"><defs>${sticker}${halftone('ht1','#EDEAF2','#DCD6E6')}${halftone('ht2','#2C2346','#3A2F5C')}</defs>
<rect width="1800" height="1500" fill="url(#ht1)"/>
<text x="900" y="70" text-anchor="middle" font-family="PT" font-size="44" fill="${INK}">IF TOON · 코드로 그린 SD 캐릭터 시안</text>
${tall(40,110,1.08)}
${cute(980,250,1.2)}
<text x="310" y="1210" text-anchor="middle" font-family="PT" font-size="38" fill="${INK}">A. 비율형 SD (1 : 3.5)</text>
<text x="1280" y="1210" text-anchor="middle" font-family="PT" font-size="38" fill="${INK}">B. 귀여운 SD (1 : 2)</text>
<rect x="0" y="1250" width="1800" height="250" fill="url(#ht2)"/>
<text x="40" y="1290" font-family="PT" font-size="26" fill="#FFF">어두운 썸네일 위 작은 크기 테스트 →</text>
${tall(520,1262,0.24)}${cute(760,1275,0.31)}
<text x="1000" y="1400" font-family="YT" font-size="96" fill="#FFD23F" stroke="${INK}" stroke-width="6" paint-order="stroke">10x FASTER?</text>
</svg></body></html>`;
fs.writeFileSync('sd.html', html);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 1800, height: 1500 }, deviceScaleFactor: 1 });
await p.goto('file://' + process.cwd() + '/sd.html'); await p.waitForTimeout(500);
await p.screenshot({ path: 'sd_v1.png' }); await b.close();
