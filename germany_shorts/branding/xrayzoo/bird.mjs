// SPECIMEN 002 hummingbird drawing (side view, facing right, 1000x600 box) + air background
import { K, f1, seed, rnd, W, H } from '/tmp/claude-0/sp2/eng2.mjs';

export const C = { back: '#2fbf71', back2: '#1f8f55', belly: '#f4f7f2', throat: '#e8243f', tailc: '#24603f',
  flesh: '#4a1f33', muscle: '#9e2a44', fibre: '#f2a7a0', heart: '#ff4d58', lung: '#ff9fb4', sac: '#8ff0ff', liver: '#b5523b', gizz: '#9b7bd8',
  gut: '#c27aa8', crop: '#f2b632', brain: '#f2d3c4', bone: '#f4efe6', tongue: '#ff7a9a', beak: '#16203d' };

// air background: warm orange sky with soft drifting clouds
export const bgAir = (t, v = 'air') => {
  const g = v === 'night' ? ['#1d2a5c', '#0b1433'] : v === 'dusk' ? ['#ffb36b', '#ff6f61'] : ['#ffc46b', '#ff8f45'];
  let s = `<defs><linearGradient id="bgA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgA)"/>`;
  if (v === 'night') { seed(9); for (let i = 0; i < 40; i++) { const x = rnd() * W, y = rnd() * H * 0.8, r = 2 + rnd() * 3; s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="#fff" opacity="${f1(0.3 + 0.5 * Math.abs(Math.sin(t + i)))}"/>`; } return s; }
  seed(31); for (let i = 0; i < 6; i++) { const w = 260 + rnd() * 220, y = 80 + rnd() * 880, x = ((rnd() * (W + 600) + t * (12 + rnd() * 10)) % (W + 600)) - 300;
    s += `<g opacity="0.16" fill="#fff"><ellipse cx="${f1(x)}" cy="${f1(y)}" rx="${f1(w / 2)}" ry="${f1(w / 7)}"/><ellipse cx="${f1(x - w / 6)}" cy="${f1(y - w / 9)}" rx="${f1(w / 5)}" ry="${f1(w / 6)}"/><ellipse cx="${f1(x + w / 8)}" cy="${f1(y - w / 8)}" rx="${f1(w / 4.5)}" ry="${f1(w / 5)}"/></g>`; }
  return s;
};

// silhouette: head + body in one path (box coords), beak and tail separate
export const BIRD = 'M748 176 C742 144 712 126 680 130 C646 134 622 160 606 190 C580 214 520 246 474 290 C446 318 428 346 420 372 C470 410 560 428 628 396 C680 372 712 322 716 270 C732 252 746 232 750 210 Z';
export const BEAK = 'M745 184 C820 185 920 191 990 199 C920 202 820 206 746 210Z';
export const TAIL = 'M440 362 L236 452 L262 478 L214 500 L250 512 L230 540 L446 410Z';
const tailFeathers = (c, sw) => [[236, 452, 262, 478], [214, 500, 250, 512], [230, 540, 300, 520]].map(([x1, y1, x2, y2], i) => `<path d="M${440 + i * 2} ${370 + i * 16} L${x1} ${y1} L${x2} ${y2} Z" fill="${c}" stroke="${K.navy}" stroke-width="${sw}" stroke-linejoin="round"/>`).join('');
export const SHOULDER = [600, 226];
// near wing, raised up and back, drawn relative to the shoulder (0,0)
export const WING = 'M0 0 C6 -60 -50 -140 -170 -196 C-210 -214 -244 -222 -262 -222 C-236 -196 -206 -168 -176 -146 C-150 -126 -122 -104 -96 -82 C-70 -58 -46 -30 -26 10 Z';
const wingBones = (c = C.bone) => `<defs><clipPath id="wcl"><path d="${WING}"/></clipPath></defs><g clip-path="url(#wcl)" stroke="${c}" stroke-linecap="round" fill="none">
  ${[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => `<path d="M${-30 - i * 9} ${-86 - i * 7} L${-150 - i * 13} ${-122 - i * 10}" stroke-width="2.5" opacity=".55"/>`).join('')}</g>
  <g stroke="${c}" stroke-linecap="round" fill="none"><path d="M-6 -10 L-14 -36" stroke-width="7"/><path d="M-14 -36 L-26 -90" stroke-width="5"/><path d="M-9 -34 L-20 -88" stroke-width="3.5"/><path d="M-26 -90 L-70 -128 L-120 -162" stroke-width="5"/></g>`;
export const wings = (t, { rate = 8, blur = 3, amp = 55, still = null, fill = '#ffffff', sw = 7, bones = 0, oc = K.navy } = {}) => {
  const base = still != null ? still : amp * Math.sin(t * rate * 2 * Math.PI);
  let s = '';
  for (let i = blur; i >= 0; i--) { const a = still != null ? base : amp * Math.sin((t - i * 0.012) * rate * 2 * Math.PI);
    s += `<g transform="translate(${SHOULDER[0]} ${SHOULDER[1]}) rotate(${f1(a)})" opacity="${i ? f1(0.22 / i) : 1}"><path d="${WING}" fill="${fill}" ${bones ? 'fill-opacity=".28"' : ''} stroke="${oc}" stroke-width="${sw}" stroke-linejoin="round"/>
      ${i ? '' : bones ? wingBones() : `<path d="M-24 -90 C-80 -130 -140 -170 -220 -210 M-40 -60 C-90 -100 -130 -130 -170 -150 M-40 -40 C-70 -66 -96 -86 -120 -102" stroke="${K.navy}" stroke-width="3" fill="none" opacity=".3"/>`}</g>`; }
  return s;
};

const eyeO = (r = 14) => `<circle cx="714" cy="168" r="${r}" fill="${K.navy}"/><circle cx="719" cy="163" r="${r * 0.32}" fill="#fff"/>`;
const feet = (c = K.navy) => `<g stroke="${c}" stroke-width="6" stroke-linecap="round" fill="none"><path d="M548 418 L538 446 M578 414 L572 444 M526 448 L552 446 M560 446 L588 444"/></g>`;

let _id = 0;
// colourful bird (no wings; call wings() separately)
export const birdSolid = ({ sw = 8, throat = 1 } = {}) => { const id = 'bs' + (_id++ % 1000);
  return `<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath></defs>
  ${tailFeathers(C.tailc, sw * 0.8)}
  <path d="${BEAK}" fill="${C.beak}" stroke="${K.navy}" stroke-width="4" stroke-linejoin="round"/>
  <path d="${BIRD}" fill="${C.belly}"/>
  <g clip-path="url(#${id})"><path d="M380 360 C470 300 560 236 640 214 C690 200 730 196 760 192 L760 100 L380 100Z" fill="${C.back}"/>
    <path d="M400 360 C480 310 560 250 640 224" stroke="${C.back2}" stroke-width="18" fill="none" opacity=".5"/>
    ${throat ? `<path d="M668 214 C700 206 732 202 752 198 L760 300 C730 290 700 262 668 214Z" fill="${C.throat}" opacity="${throat}"/>` : ''}</g>
  <path d="${BIRD}" fill="none" stroke="${K.navy}" stroke-width="${sw}" stroke-linejoin="round"/>${eyeO()}${feet()}`;
};

// points of interest (box coords)
export const PT = { heart: [648, 300], muscle: [676, 366], keel: [640, 400], lung: [548, 262], sac: [500, 318], liver: [585, 322], stomach: [520, 352], crop: [676, 244],
  brain: [686, 158], tongue: [990, 199], hyoid: [652, 152], eye: [714, 168], throat: [720, 240], feet: [560, 446], shoulder: SHOULDER, wing: [420, 40], beak: [880, 196], tail: [240, 490], spine: [520, 290] };

// vertebra chain along a cubic curve
const chain = (p, n, w, h, col) => { let s = ''; for (let i = 0; i <= n; i++) { const t = i / n, m = 1 - t;
  const x = m * m * m * p[0] + 3 * m * m * t * p[2] + 3 * m * t * t * p[4] + t * t * t * p[6], y = m * m * m * p[1] + 3 * m * m * t * p[3] + 3 * m * t * t * p[5] + t * t * t * p[7];
  s += `<rect x="${f1(x - w / 2)}" y="${f1(y - h / 2)}" width="${w}" height="${h}" rx="3" fill="${col}"/>`; } return s; };

// sagittal anatomy inside the bird (draw inside a clipPath of BIRD)
export const anatomyB = ({ col = 1, heartK = 1, glow = null } = {}) => {
  const c = col ? C : Object.fromEntries(Object.keys(C).map(k => [k, '#ffffff']));
  const gl = n => glow === n ? ` stroke="#ffffff" stroke-width="7"` : '';
  let s = `<path d="${BIRD}" fill="${col ? C.flesh : 'none'}"/>`;
  // lungs (spongy) tucked under the spine
  s += `<path d="M512 254 C540 236 588 236 600 252 C596 270 560 282 520 278 C508 272 504 262 512 254Z" fill="${c.lung}"${gl('lung')}/>`;
  for (let i = 0; i < 9; i++) s += `<circle cx="${524 + (i % 5) * 14}" cy="${256 + Math.floor(i / 5) * 12}" r="3" fill="${col ? '#d9667f' : '#fff'}"/>`;
  // flight muscle (pectoralis): one big mass filling the breast, fibres fan from keel to shoulder
  s += `<path d="M708 270 C722 318 704 368 660 396 C620 420 566 428 528 420 C548 396 576 372 600 360 C640 340 668 300 676 268 C686 258 700 258 708 270Z" fill="${c.muscle}"${gl('muscle')}/>`;
  for (let i = 0; i < 9; i++) s += `<path d="M${548 + i * 18} ${420 - i * 7} Q${640 + i * 2} ${360 - i * 6} ${690 + i * 1} ${278 + i * 3}" stroke="${c.fibre}" stroke-width="2.2" fill="none" opacity=".4"/>`;
  // keel (sternum edge) along the breast + wishbone
  s += `<path d="M714 292 C710 344 678 390 620 414 C584 428 552 428 524 424" stroke="${c.bone}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  // liver (two lobes), gizzard, intestine
  s += `<path d="M560 318 C586 300 624 304 636 326 C640 348 612 362 586 360 C566 358 548 340 560 318Z" fill="${c.liver}"/><path d="M590 312 C592 330 590 346 584 360" stroke="${col ? '#7d3424' : '#fff'}" stroke-width="2.5" fill="none"/>`;
  s += `<ellipse cx="516" cy="352" rx="27" ry="21" fill="${c.gizz}"/><path d="M506 340 C514 350 526 356 536 356" stroke="#fff" stroke-width="2.5" fill="none" opacity=".45"/><path d="M496 366 C478 382 470 362 456 374 C444 386 468 398 448 406" stroke="${c.gut}" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  // oesophagus + crop (nectar) and trachea down the neck
  s += `<path d="M736 214 C716 222 700 232 690 246 C670 270 610 310 540 344" stroke="${c.gut}" stroke-width="6" fill="none" opacity=".9"/><ellipse cx="692" cy="248" rx="14" ry="10" fill="${c.crop}"/>`;
  s += `<path d="M732 224 C712 236 690 252 668 276 C650 290 620 270 600 262" stroke="${col ? '#cfe8ff' : '#fff'}" stroke-width="5" fill="none" stroke-dasharray="4 3"/>`;
  // heart: anatomical shape, big, just above the keel
  s += `<g transform="translate(642 306) scale(${f1(heartK * 100) / 100}) rotate(-28)"${gl('heart')}><path d="M-10 -34 C-12 -54 8 -64 24 -54 L20 -44 C10 -50 2 -46 2 -34Z" fill="${col ? '#d63a46' : '#fff'}"/><path d="M8 -36 C14 -50 30 -50 34 -40 L28 -34Z" fill="${col ? '#7a8fd6' : '#fff'}"/>
    <path d="M-2 -36 C24 -40 38 -18 32 6 C26 28 10 44 -2 52 C-16 42 -32 22 -34 0 C-36 -20 -24 -34 -2 -36Z" fill="${c.heart}"/><path d="M2 -30 C8 -6 6 22 -2 48" stroke="${col ? '#b8283a' : '#fff'}" stroke-width="3" fill="none"/>
    <path d="M-22 -18 C-28 -6 -28 8 -22 20" stroke="#fff" stroke-width="5" fill="none" opacity=".45" stroke-linecap="round"/></g>`;
  // skeleton: skull, neck vertebrae, back, pelvis, tail
  s += `<path d="M652 146 C668 126 712 122 734 140 C748 152 750 172 746 186 L740 204 C720 214 690 214 670 204 C652 192 644 166 652 146Z" fill="none" stroke="${c.bone}" stroke-width="5"/>`;
  s += `<ellipse cx="682" cy="160" rx="24" ry="20" fill="${c.brain}"${gl('brain')}/><path d="M666 170 C672 178 684 180 694 176" stroke="${col ? '#c9a89a' : '#fff'}" stroke-width="2.5" fill="none"/><ellipse cx="660" cy="176" rx="10" ry="9" fill="${c.brain}"/>`;
  s += `<circle cx="714" cy="168" r="18" fill="none" stroke="${c.bone}" stroke-width="3" stroke-dasharray="3 3"/>`;
  s += chain([652, 186, 640, 206, 630, 220, 612, 232], 6, 9, 9, c.bone) + chain([606, 236, 570, 254, 520, 280, 476, 320], 12, 10, 10, c.bone) + chain([470, 326, 456, 340, 446, 352, 434, 366], 4, 9, 9, c.bone);
  s += `<path d="M430 370 L410 384" stroke="${c.bone}" stroke-width="12" stroke-linecap="round"/>`;
  for (let i = 0; i < 4; i++) { const x = 586 - i * 22, y = 246 + i * 12; s += `<path d="M${x} ${y} C${x + 4} ${y + 18} ${x + 10} ${y + 32} ${x + 18} ${y + 44}" stroke="${c.bone}" stroke-width="4" fill="none" opacity=".8"/>`; }
  s += `<path d="M500 300 C470 320 456 350 462 376" stroke="${c.bone}" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M540 372 L552 412 M552 412 L548 420" stroke="${c.bone}" stroke-width="6" stroke-linecap="round" fill="none"/>`;
  // tongue + hyoid horns that wrap around the back of the skull
  s += `<path d="M746 199 C724 206 704 210 690 206 C664 200 648 182 650 160 C652 138 676 124 704 128 C722 132 736 142 744 156" stroke="${c.tongue}" stroke-width="5" fill="none" stroke-linecap="round"${gl('hyoid')}/>`;
  return s;
};

// cutaway bird: anatomy inside the silhouette, beak shows the tongue inside
export const birdInside = ({ sw = 8, tongue = 0, col = 1, heartK = 1, glow = null, skin = 1, oc = K.navy } = {}) => { const id = 'bi' + (_id++ % 1000);
  const tl = 990 + tongue * 40;
  return `<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath></defs>
  ${tailFeathers(C.tailc, sw * 0.8)}
  <path d="${BEAK}" fill="${C.beak}" stroke="${K.navy}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M748 192 C830 194 920 197 ${f1(tl)} 199" stroke="${C.tongue}" stroke-width="4" fill="none" stroke-linecap="round"/>${tongue > 0 ? `<path d="M${f1(tl - 2)} 199 L${f1(tl + 22)} 191 M${f1(tl - 2)} 199 L${f1(tl + 22)} 207" stroke="${C.tongue}" stroke-width="4" stroke-linecap="round"/>` : ''}
  <path d="M750 188 C830 190 920 194 984 198 M750 206 C830 204 920 202 984 200" stroke="${C.bone}" stroke-width="2.5" fill="none" opacity=".6"/>
  <g clip-path="url(#${id})">${anatomyB({ col, heartK, glow })}</g>
  ${skin ? `<path d="${BIRD}" fill="none" stroke="#ffffff" stroke-width="${sw + 8}" stroke-linejoin="round" clip-path="url(#${id})"/>` : ''}
  <path d="${BIRD}" fill="none" stroke="${oc}" stroke-width="${sw}" stroke-linejoin="round"/>${feet(oc)}`;
};

// place the 1000x600 box with body centre (BX,BY) at (cx, cy)
export const BX = 600, BY = 300;
export const placeB = (cx, cy, sc, inner, { rot = 0, flip = false } = {}) => `<g transform="translate(${f1(cx)} ${f1(cy)}) rotate(${f1(rot)}) scale(${flip ? -sc : sc} ${sc}) translate(${-BX} ${-BY})">${inner}</g>`;
export const toB = (cx, cy, sc, x, y) => [cx + (x - BX) * sc, cy + (y - BY) * sc];
