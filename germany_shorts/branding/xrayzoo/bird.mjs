// X-RAY ZOO hummingbird drawing v2 (side view, facing right, 1000x600 box) + air background
// v2: feathered fan tail, iridescent back + gorget, real feet (FOOT_Y is the ground line),
// x-ray shows the BODY only: the cute head stays solid behind a dashed neck line, no eyes inside.
import { K, f1, seed, rnd, W, H } from '/tmp/claude-0/sp2/eng2.mjs';

export const C = { back: '#2fbf71', back2: '#1f8f55', backHi: '#5fe39b', belly: '#f6f8f3', flank: '#cfdcc9', throat: '#e8243f', throat2: '#9e0f2c', tailc: '#24603f', tailTip: '#14302a',
  wing: '#9aa2c4', wing2: '#c9cee6', wingLine: '#5f678c',
  flesh: '#4a1f33', muscle: '#9e2a44', fibre: '#f2a7a0', heart: '#ff4d58', lung: '#ff9fb4', sac: '#8ff0ff', liver: '#b5523b', gizz: '#9b7bd8',
  gut: '#c27aa8', crop: '#f2b632', brain: '#f7c6cf', bone: '#f4efe6', tongue: '#ff7a9a', beak: '#16203d' };
const N = K.navy;

// air background: warm orange sky with soft drifting clouds
export const bgAir = (t, v = 'air') => {
  const g = v === 'night' ? ['#1d2a5c', '#0b1433'] : v === 'dusk' ? ['#ffb36b', '#ff6f61'] : ['#ffc46b', '#ff8f45'];
  let s = `<defs><linearGradient id="bgA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgA)"/>`;
  if (v === 'night') { seed(9); for (let i = 0; i < 40; i++) { const x = rnd() * W, y = rnd() * H * 0.8, r = 2 + rnd() * 3; s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="#fff" opacity="${f1(0.3 + 0.5 * Math.abs(Math.sin(t + i)))}"/>`; } return s; }
  seed(31); for (let i = 0; i < 6; i++) { const w = 260 + rnd() * 220, y = 80 + rnd() * 880, x = ((rnd() * (W + 600) + t * (12 + rnd() * 10)) % (W + 600)) - 300;
    s += `<g opacity="0.16" fill="#fff"><ellipse cx="${f1(x)}" cy="${f1(y)}" rx="${f1(w / 2)}" ry="${f1(w / 7)}"/><ellipse cx="${f1(x - w / 6)}" cy="${f1(y - w / 9)}" rx="${f1(w / 5)}" ry="${f1(w / 6)}"/><ellipse cx="${f1(x + w / 8)}" cy="${f1(y - w / 8)}" rx="${f1(w / 4.5)}" ry="${f1(w / 5)}"/></g>`; }
  return s;
};

// silhouette: head + body in one path (box coords), beak separate
export const BIRD = 'M748 176 C742 144 712 126 680 130 C646 134 622 160 606 190 C580 214 520 246 474 290 C446 318 428 346 420 372 C470 410 560 428 628 396 C680 372 712 322 716 270 C732 252 746 232 750 210 Z';
export const BEAK = 'M745 182 C820 184 920 191 992 199 C920 203 820 207 746 212Z';
export const TAIL_BASE = [440, 374];
export const FOOT_Y = 452; // feet rest on this line (box coords)
export const SHOULDER = [600, 226];
// neck cut: head is up/right of this line, body down/left
const NECK = [[606, 190], [716, 270]];
const HEADPOLY = 'M56 -210 L1156 590 L1600 590 L1600 -400 L56 -400Z', BODYPOLY = 'M56 -210 L1156 590 L1156 1000 L-400 1000 L-400 -210Z';

let _id = 0; const uid = p => p + (_id++ % 100000);
// species palettes: [backHi, back, back2, belly, flank, throatA, throatB, throatC, tailA, tailB, tailC, crown?]
export const PAL = {
  ruby: { bh: '#5fe39b', b: '#2fbf71', b2: '#1f8f55', belly: '#f6f8f3', flank: '#cfdcc9', t: ['#ff5a74', '#e8243f', '#9e0f2c'], tl: ['#2f9a62', '#24603f', '#14302a'], crown: null, scale: '#9af5c2' },
  anna: { bh: '#7fe0a0', b: '#3fae6e', b2: '#26804e', belly: '#eef1ee', flank: '#bcd2bf', t: ['#ff7ac0', '#ff2f8a', '#a8105c'], tl: ['#5a8a6e', '#3d6450', '#22382d'], crown: ['#ff7ac0', '#ff2f8a', '#a8105c'], scale: '#b4f0c8' },
  rufous: { bh: '#ffb070', b: '#e0782f', b2: '#b0521c', belly: '#fbf6ef', flank: '#f2c79a', t: ['#ffd36a', '#ff8a2a', '#d9431b'], tl: ['#f08a3a', '#c8601f', '#7a3412'], crown: null, scale: '#ffd0a0' },
  sword: { bh: '#9fd88a', b: '#4f9a5a', b2: '#2f6a3c', belly: '#d9e8cf', flank: '#a9c79a', t: ['#5fbf7a', '#2f8a4f', '#1a5a32'], tl: ['#5a7a4a', '#3d5a34', '#24361f'], crown: ['#c9a25a', '#9a7a3a', '#6a5226'], scale: '#c8f0b0' } };
const palDefs = (n = 'ruby') => { const P = PAL[n], sf = n === 'ruby' ? '' : n;
  return `<linearGradient id="gBack${sf}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${P.bh}"/><stop offset=".55" stop-color="${P.b}"/><stop offset="1" stop-color="${P.b2}"/></linearGradient>
  <linearGradient id="gThroat${sf}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${P.t[0]}"/><stop offset=".5" stop-color="${P.t[1]}"/><stop offset="1" stop-color="${P.t[2]}"/></linearGradient>
  <linearGradient id="gTail${sf}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${P.tl[0]}"/><stop offset=".55" stop-color="${P.tl[1]}"/><stop offset="1" stop-color="${P.tl[2]}"/></linearGradient>
  ${P.crown ? `<linearGradient id="gCrown${sf}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${P.crown[0]}"/><stop offset=".5" stop-color="${P.crown[1]}"/><stop offset="1" stop-color="${P.crown[2]}"/></linearGradient>` : ''}`; };
const defs = (n = 'ruby') => `<defs>${palDefs(n)}
  <radialGradient id="gHeart" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#ff8a92"/><stop offset=".55" stop-color="#f0404f"/><stop offset="1" stop-color="#b81f34"/></radialGradient>
  <radialGradient id="gBrain" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#ffe0e6"/><stop offset="1" stop-color="#f09aac"/></radialGradient></defs>`;
export const birdDefs = defs;

// one tapered feather along +x (length L, width w)
const feather = (L, w) => `M0 ${f1(-w * 0.35)} C${f1(L * 0.3)} ${f1(-w)} ${f1(L * 0.78)} ${f1(-w * 0.85)} ${f1(L)} 0 C${f1(L * 0.78)} ${f1(w * 0.85)} ${f1(L * 0.3)} ${f1(w)} 0 ${f1(w * 0.35)}Z`;
// fan tail of five feathers (forked: outer ones longer); rot lifts (+) or drops (-) the whole tail
export const tail = ({ rot = 0, spread = 1, sw = 6, col = 'url(#gTail)', oc = N, fan = null } = {}) => {
  const A = [134, 141, 148, 155, 162].map(a => 148 + (a - 148) * spread), L = [238, 214, 198, 214, 238];
  if (fan) fan.forEach((d, i) => { A[i] += d; });
  let s = `<g transform="translate(${TAIL_BASE[0]} ${TAIL_BASE[1]}) rotate(${f1(rot)})">`;
  for (const i of [0, 4, 1, 3, 2]) s += `<g transform="rotate(${f1(A[i])})"><path d="${feather(L[i], 26)}" fill="${col}" stroke="${oc}" stroke-width="${sw}" stroke-linejoin="round"/><path d="M10 0 L${L[i] - 18} 0" stroke="#ffffff" stroke-width="2.5" opacity=".35" stroke-linecap="round"/>
    <path d="M${f1(L[i] * 0.72)} -14 C${f1(L[i] * 0.84)} -8 ${f1(L[i] * 0.92)} -3 ${f1(L[i] - 4)} 0" stroke="#000" stroke-width="3" fill="none" opacity=".18"/></g>`;
  return s + '</g>';
};

// near wing, raised up and back, drawn relative to the shoulder (0,0)
export const WING = 'M0 0 C6 -60 -50 -140 -170 -196 C-210 -214 -244 -222 -262 -222 C-236 -196 -206 -168 -176 -146 C-150 -126 -122 -104 -96 -82 C-70 -58 -46 -30 -26 10 Z';
const wingDetail = () => {
  let s = `<path d="M0 0 C4 -30 -10 -60 -40 -84 C-36 -50 -26 -24 -14 6Z" fill="${C.back}"/>`; // small green shoulder patch
  for (let i = 0; i < 9; i++) { const u = i / 8, x0 = -40 - u * 150, y0 = -72 - u * 112, x1 = -96 - u * 166, y1 = -96 - u * 124;
    s += `<path d="M${f1(x0)} ${f1(y0)} L${f1(x1)} ${f1(y1)}" stroke="${C.wingLine}" stroke-width="3" opacity=".55" stroke-linecap="round"/>`; }
  s += `<path d="M-30 -60 C-80 -110 -150 -160 -240 -212" stroke="#ffffff" stroke-width="4" opacity=".35" fill="none" stroke-linecap="round"/>`;
  return s;
};
const wingBones = (c = C.bone) => `<g stroke="${c}" stroke-linecap="round" fill="none"><path d="M-6 -10 L-14 -36" stroke-width="7"/><path d="M-14 -36 L-26 -90" stroke-width="5"/><path d="M-9 -34 L-20 -88" stroke-width="3.5"/><path d="M-26 -90 L-70 -128 L-120 -162" stroke-width="5"/>
  ${[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => `<path d="M${-30 - i * 9} ${-86 - i * 7} L${-150 - i * 13} ${-122 - i * 10}" stroke-width="2.5" opacity=".5"/>`).join('')}</g>`;
const wingOne = (a, o, { fill, sw, bones, oc, detail }) => `<g transform="translate(${SHOULDER[0]} ${SHOULDER[1]}) rotate(${f1(a)})" opacity="${f1(o)}"><path d="${WING}" fill="${bones ? '#ffffff' : fill}" ${bones ? 'fill-opacity=".28"' : ''} stroke="${oc}" stroke-width="${sw}" stroke-linejoin="round"/>${detail ? (bones ? wingBones() : wingDetail()) : ''}</g>`;
// wings: rate in beats/s; above ~9 beats/s the eye only sees a fan-shaped blur. phase (beats) overrides t*rate.
export const wings = (t, { rate = 8, blur = 3, amp = 55, still = null, fill = C.wing2, sw = 7, bones = 0, oc = N, phase = null } = {}) => {
  const o = { fill, sw, bones, oc, detail: 1 };
  if (still != null) return wingOne(still, 1, o);
  const ph = phase != null ? phase : t * rate;
  const fan = Math.min(1, Math.max(0, (rate - 9) / 10));
  let s = '';
  if (fan > 0) for (let i = 0; i <= 10; i++) { const a = -amp + 2 * amp * i / 10; s += wingOne(a, 0.13 * fan, { ...o, detail: 0, sw: sw * 0.6 }); }
  const sol = 1 - fan * 0.85;
  for (let i = blur; i >= 1; i--) s += wingOne(amp * Math.sin((ph - i * 0.012 * Math.min(rate, 9)) * 2 * Math.PI), sol * 0.22 / i, { ...o, detail: 0 });
  s += wingOne(amp * Math.sin(ph * 2 * Math.PI), sol, o);
  return s;
};

// eye with highlights + the little white spot behind it
const eyeO = (r = 15) => `<circle cx="714" cy="168" r="${r}" fill="${N}"/><circle cx="719" cy="162" r="${f1(r * 0.34)}" fill="#fff"/><circle cx="709" cy="174" r="${f1(r * 0.14)}" fill="#fff" opacity=".7"/><circle cx="694" cy="178" r="5" fill="#fff"/>`;
// feet: short legs, three toes forward, one back; toes touch FOOT_Y
export const feet = (c = N) => `<g stroke="${c}" stroke-linecap="round" stroke-linejoin="round" fill="none">
  <path d="M556 412 L552 446" stroke-width="7"/><path d="M584 408 L582 446" stroke-width="7"/>
  <path d="M552 446 C562 452 574 452 584 450 M552 446 L578 446 M552 446 C546 451 538 452 532 451" stroke-width="5"/>
  <path d="M582 446 C592 452 604 452 614 450 M582 446 L608 446 M582 446 C576 451 568 452 562 451" stroke-width="5"/></g>`;
const body = (sw, throat, id, pal = 'ruby') => { const P = PAL[pal], sf = pal === 'ruby' ? '' : pal;
  return `<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath></defs><path d="${BIRD}" fill="${P.belly}"/>
  <g clip-path="url(#${id})"><path d="M520 400 C560 380 620 380 660 400 L660 460 L480 460Z" fill="${P.flank}" opacity=".7"/>
    <path d="M380 360 C470 300 560 236 640 214 C690 200 730 196 760 192 L760 100 L380 100Z" fill="url(#gBack${sf})"/>
    ${[16, 38, 60].map((o, r) => [0, 1, 2, 3, 4, 5, 6].map(c => { const u = (c + (r % 2) * 0.5) / 7, x = 440 + 190 * u, y = 340 - 120 * u - o; return `<path d="M${f1(x)} ${f1(y)} q8 8 16 0" stroke="${P.scale}" stroke-width="3" fill="none" opacity=".55"/>`; }).join('')).join('')}
    ${P.crown ? `<path d="M628 176 C640 146 676 128 708 128 C736 130 752 152 752 178 C730 170 700 162 670 164 C654 166 640 170 628 176Z" fill="url(#gCrown${sf})"/>` : ''}
    <path d="M640 150 C670 136 710 134 736 150" stroke="#ffffff" stroke-width="6" fill="none" opacity=".3" stroke-linecap="round"/>
    ${throat ? `<g opacity="${throat}"><path d="${pal === 'anna' ? 'M664 206 C700 198 732 196 754 194 L762 300 C720 300 680 270 650 236 C654 222 658 212 664 206Z' : 'M670 212 C700 204 732 200 752 196 L760 300 C728 292 698 262 670 212Z'}" fill="url(#gThroat${sf})"/>
      ${[0, 1, 2].map(r => [0, 1, 2, 3].map(c => `<path d="M${690 + c * 16 + r * 8} ${222 + r * 16} q6 6 12 0" stroke="#ffffff" stroke-width="2.5" fill="none" opacity=".45"/>`).join('')).join('')}
      <path d="M692 218 C708 214 726 212 740 210" stroke="#ffffff" stroke-width="5" opacity=".5" fill="none" stroke-linecap="round"/></g>` : ''}</g>
  <path d="${BIRD}" fill="none" stroke="${N}" stroke-width="${sw}" stroke-linejoin="round"/>`; };
const beak = () => `<path d="${BEAK}" fill="${C.beak}" stroke="${N}" stroke-width="4" stroke-linejoin="round"/><path d="M752 188 C830 190 910 194 970 197" stroke="#ffffff" stroke-width="3" opacity=".35" fill="none" stroke-linecap="round"/>`;

// colourful bird (no wings; call wings() separately). tailRot lifts the tail (positive) e.g. +25 when standing on a flat surface
export const birdSolid = ({ sw = 8, throat = 1, tailRot = 0, legs = 1, pal = 'ruby', beakD = null, tailSpread = 1, tailFan = null } = {}) =>
  `${defs(pal)}${tail({ rot: tailRot, sw: sw * 0.75, col: `url(#gTail${pal === 'ruby' ? '' : pal})`, spread: tailSpread, fan: tailFan })}${beakD ? `<path d="${beakD}" fill="${C.beak}" stroke="${N}" stroke-width="4" stroke-linejoin="round"/>` : beak()}${body(sw, throat, uid('bs'), pal)}${eyeO()}${legs ? feet() : ''}`;

// points of interest (box coords)
export const PT = { heart: [648, 300], muscle: [676, 366], keel: [640, 400], lung: [548, 262], sac: [500, 318], liver: [585, 322], stomach: [520, 352], crop: [676, 244],
  brain: [670, 164], tongue: [992, 199], hyoid: [652, 152], eye: [714, 168], throat: [720, 240], feet: [570, 450], shoulder: SHOULDER, wing: [420, 40], beak: [880, 196], tail: [240, 490], spine: [520, 290], neck: [661, 230] };

// vertebra chain along a cubic curve
const chain = (p, n, w, h, col) => { let s = ''; for (let i = 0; i <= n; i++) { const t = i / n, m = 1 - t;
  const x = m * m * m * p[0] + 3 * m * m * t * p[2] + 3 * m * t * t * p[4] + t * t * t * p[6], y = m * m * m * p[1] + 3 * m * m * t * p[3] + 3 * m * t * t * p[5] + t * t * t * p[7];
  s += `<rect x="${f1(x - w / 2)}" y="${f1(y - h / 2)}" width="${w}" height="${h}" rx="3" fill="${col}"/>`; } return s; };

// pretty anatomical heart, centred at 0,0, about 90 x 150 units; k scales the muscle (pulse)
export const prettyHeart = (k = 1, { sw = 2.6, oc = N } = {}) => `<g>
  <path d="M8 -72 L6 -90 M20 -75 L22 -93 M32 -72 L38 -88" stroke="${oc}" stroke-width="10" stroke-linecap="round"/><path d="M8 -72 L6 -90 M20 -75 L22 -93 M32 -72 L38 -88" stroke="#e0344a" stroke-width="6" stroke-linecap="round"/>
  <path d="M-6 -40 C-8 -66 10 -78 34 -72 C46 -68 52 -58 50 -48 L40 -46 C40 -54 34 -60 24 -60 C12 -60 6 -52 6 -40Z" fill="#e0344a" stroke="${oc}" stroke-width="${sw}"/>
  <path d="M-34 -30 C-46 -40 -48 -56 -40 -66 L-28 -62 C-32 -54 -30 -44 -22 -38Z" fill="#6f86e0" stroke="${oc}" stroke-width="${sw}"/>
  <g transform="scale(${f1(k * 1000) / 1000})">
    <path d="M-36 -26 C-48 -36 -40 -50 -26 -46 C-20 -52 -10 -50 -6 -42 L-8 -30Z" fill="#c42a42" stroke="${oc}" stroke-width="${sw}"/>
    <path d="M30 -30 C44 -40 54 -30 48 -18 L36 -16Z" fill="#c42a42" stroke="${oc}" stroke-width="${sw}"/>
    <path d="M-2 -36 C26 -40 44 -18 38 8 C32 32 14 50 -2 58 C-18 48 -38 26 -40 2 C-42 -20 -26 -34 -2 -36Z" fill="url(#gHeart)" stroke="${oc}" stroke-width="${sw}"/>
    <path d="M6 -32 C14 -8 12 22 0 54" stroke="#f6d36b" stroke-width="5" fill="none" opacity=".85"/><path d="M6 -32 C14 -8 12 22 0 54" stroke="#b8283a" stroke-width="2" fill="none"/>
    <path d="M10 -6 C18 0 24 6 28 16 M8 18 C14 24 18 30 20 38" stroke="#b8283a" stroke-width="1.8" fill="none" opacity=".8"/>
    <path d="M-26 -16 C-32 -4 -32 12 -24 26" stroke="#ffffff" stroke-width="6" fill="none" opacity=".5" stroke-linecap="round"/><circle cx="-20" cy="-22" r="3.5" fill="#fff" opacity=".7"/></g>
  <path d="M-16 -42 C-14 -58 0 -64 16 -60 L14 -50 C4 -54 -4 -50 -4 -40Z" fill="#6f86e0" stroke="${oc}" stroke-width="${sw}"/></g>`;

// pretty brain (side view, facing right), centred at 0,0, about 90 x 70 units
export const prettyBrain = ({ sw = 2.4, oc = N, glow = 0 } = {}) => `<g>
  ${glow ? `<ellipse cx="0" cy="2" rx="${f1(50 + 10 * glow)}" ry="${f1(38 + 10 * glow)}" fill="#fff6a8" opacity="${f1(0.55 * glow)}"/>` : ''}
  <path d="M-8 22 C-10 34 -2 42 8 40 L10 24Z" fill="#e88aa0" stroke="${oc}" stroke-width="${sw}"/>
  <path d="M-38 14 C-46 18 -48 30 -40 34 C-32 38 -24 32 -24 22Z" fill="#f3a9b8" stroke="${oc}" stroke-width="${sw}"/><path d="M-42 22 L-28 22 M-42 28 L-30 28" stroke="#d9667f" stroke-width="1.6"/>
  <path d="M-34 10 C-44 -8 -30 -30 -6 -32 C18 -34 36 -22 36 -4 C36 12 22 22 4 22 C-10 22 -24 20 -34 10Z" fill="url(#gBrain)" stroke="${oc}" stroke-width="${sw}"/>
  <path d="M-22 -18 C-14 -12 -18 -4 -10 0 M-4 -26 C2 -18 -6 -10 2 -6 C8 -2 4 6 12 8 M14 -24 C20 -16 14 -10 22 -6 M-26 2 C-18 6 -14 12 -6 12" stroke="#d9667f" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  <ellipse cx="10" cy="16" rx="12" ry="8" fill="#f8b9c6" stroke="${oc}" stroke-width="${f1(sw * 0.8)}"/>
  <path d="M-16 -22 C-8 -28 6 -28 14 -24" stroke="#fff" stroke-width="3.5" fill="none" opacity=".6" stroke-linecap="round"/></g>`;

// sagittal anatomy of the BODY (draw inside a clip of BIRD and the body side of the neck)
export const anatomyB = ({ col = 1, heartK = 1, glow = null } = {}) => {
  const c = col ? C : Object.fromEntries(Object.keys(C).map(k => [k, '#ffffff']));
  const gl = n => glow === n ? ` stroke="#ffffff" stroke-width="7"` : '';
  let s = `<path d="${BIRD}" fill="${col ? C.flesh : 'none'}"/>`;
  s += `<path d="M512 254 C540 236 588 236 600 252 C596 270 560 282 520 278 C508 272 504 262 512 254Z" fill="${c.lung}"${gl('lung')}/>`;
  for (let i = 0; i < 9; i++) s += `<circle cx="${524 + (i % 5) * 14}" cy="${256 + Math.floor(i / 5) * 12}" r="3" fill="${col ? '#d9667f' : '#fff'}"/>`;
  s += `<path d="M708 270 C722 318 704 368 660 396 C620 420 566 428 528 420 C548 396 576 372 600 360 C640 340 668 300 676 268 C686 258 700 258 708 270Z" fill="${c.muscle}"${gl('muscle')}/>`;
  for (let i = 0; i < 9; i++) s += `<path d="M${548 + i * 18} ${420 - i * 7} Q${640 + i * 2} ${360 - i * 6} ${690 + i * 1} ${278 + i * 3}" stroke="${c.fibre}" stroke-width="2.2" fill="none" opacity=".4"/>`;
  s += `<path d="M714 292 C710 344 678 390 620 414 C584 428 552 428 524 424" stroke="${c.bone}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M560 318 C586 300 624 304 636 326 C640 348 612 362 586 360 C566 358 548 340 560 318Z" fill="${c.liver}"/><path d="M590 312 C592 330 590 346 584 360" stroke="${col ? '#7d3424' : '#fff'}" stroke-width="2.5" fill="none"/>`;
  s += `<ellipse cx="516" cy="352" rx="27" ry="21" fill="${c.gizz}"/><path d="M506 340 C514 350 526 356 536 356" stroke="#fff" stroke-width="2.5" fill="none" opacity=".45"/><path d="M496 366 C478 382 470 362 456 374 C444 386 468 398 448 406" stroke="${c.gut}" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M690 246 C670 270 610 310 540 344" stroke="${c.gut}" stroke-width="6" fill="none" opacity=".9"/>`;
  s += `<path d="M668 276 C650 290 620 270 600 262" stroke="${col ? '#cfe8ff' : '#fff'}" stroke-width="5" fill="none" stroke-dasharray="4 3"/>`;
  s += chain([630, 210, 624, 220, 618, 228, 612, 232], 3, 9, 9, c.bone) + chain([606, 236, 570, 254, 520, 280, 476, 320], 12, 10, 10, c.bone) + chain([470, 326, 456, 340, 446, 352, 434, 366], 4, 9, 9, c.bone);
  s += `<path d="M430 370 L410 384" stroke="${c.bone}" stroke-width="12" stroke-linecap="round"/>`;
  for (let i = 0; i < 4; i++) { const x = 586 - i * 22, y = 246 + i * 12; s += `<path d="M${x} ${y} C${x + 4} ${y + 18} ${x + 10} ${y + 32} ${x + 18} ${y + 44}" stroke="${c.bone}" stroke-width="4" fill="none" opacity=".8"/>`; }
  s += `<path d="M500 300 C470 320 456 350 462 376" stroke="${c.bone}" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M540 372 L552 412 M552 412 L548 420" stroke="${c.bone}" stroke-width="6" stroke-linecap="round" fill="none"/>`;
  // heart last so it sits on top: detailed anatomical heart
  const hs = f1(heartK * 0.6 * 1000) / 1000;
  s += `<g transform="translate(642 304) rotate(-26) scale(${hs})">${glow === 'heart' ? prettyHeart(1, { sw: 16, oc: '#ffffff' }) : ''}${col ? prettyHeart(1, { sw: 4 }) : `<path d="M-2 -36 C26 -40 44 -18 38 8 C32 32 14 50 -2 58 C-18 48 -38 26 -40 2 C-42 -20 -26 -34 -2 -36Z" fill="#fff"/>`}</g>`;
  return s;
};

// cutaway bird: cute solid head, dashed neck line, x-ray body. tongue: extra tongue length out of the beak (0..2).
// brain: 0..1 shows the brain through a dashed window in the crown; hyoid: 0..1 draws the tongue's path around the head
export const birdInside = ({ sw = 8, tongue = 0, col = 1, heartK = 1, glow = null, skin = 1, oc = N, tailRot = 0, brain = 0, hyoid = 0, throat = 1, brainGlow = 0 } = {}) => {
  const id = uid('bi'), hid = uid('bh'), bid = uid('bb');
  const tl = 992 + tongue * 40;
  let s = `${defs()}<defs><clipPath id="${id}"><path d="${BIRD}"/></clipPath><clipPath id="${hid}"><path d="${HEADPOLY}"/></clipPath><clipPath id="${bid}"><path d="${BODYPOLY}"/></clipPath></defs>
  ${tail({ rot: tailRot, sw: sw * 0.75 })}${beak()}
  <path d="M748 196 C830 196 920 198 ${f1(tl)} 199" stroke="${C.tongue}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <g clip-path="url(#${hid})">${body(sw, throat, uid('bx'))}${eyeO()}</g>
  <g clip-path="url(#${bid})"><g clip-path="url(#${id})">${anatomyB({ col, heartK, glow })}</g>
    ${skin ? `<path d="${BIRD}" fill="none" stroke="#ffffff" stroke-width="${sw + 8}" stroke-linejoin="round" clip-path="url(#${id})"/>` : ''}
    <path d="${BIRD}" fill="none" stroke="${oc}" stroke-width="${sw}" stroke-linejoin="round"/></g>
  <g clip-path="url(#${id})"><path d="M${NECK[0][0] - 20} ${NECK[0][1] - 15} L${NECK[1][0] + 20} ${NECK[1][1] + 15}" stroke="${N}" stroke-width="11" stroke-dasharray="16 11" stroke-linecap="round"/><path d="M${NECK[0][0] - 20} ${NECK[0][1] - 15} L${NECK[1][0] + 20} ${NECK[1][1] + 15}" stroke="#ffffff" stroke-width="6" stroke-dasharray="16 11" stroke-linecap="round"/></g>`;
  if (hyoid) s += `<path d="M746 199 C724 206 704 210 690 206 C664 200 648 182 650 160 C652 138 676 124 704 128 C722 132 736 142 744 156" stroke="#ff7a9a" stroke-width="7" fill="none" stroke-linecap="round" opacity="${f1(hyoid)}"/><path d="M746 199 C724 206 704 210 690 206 C664 200 648 182 650 160 C652 138 676 124 704 128 C722 132 736 142 744 156" stroke="#fff" stroke-width="2.5" fill="none" stroke-dasharray="6 6" opacity="${f1(hyoid)}"/>`;
  if (brain > 0) s += brainWindow(brain, brainGlow);
  return s + feet(oc);
};
// dashed round window in the crown with the brain inside (the eye stays outside the window)
export const brainWindow = (k = 1, glow = 0) => { const r = f1(25 * Math.min(1, k) + 0.01);
  return `<g><circle cx="670" cy="164" r="${r}" fill="#3a1830"/>
  <g transform="translate(670 165) scale(${f1(0.5 * Math.min(1, k) * 1000) / 1000})">${prettyBrain({ glow, sw: 3.4 })}</g>
  <circle cx="670" cy="164" r="${r}" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="7 5"/></g>`; };

// place the 1000x600 box with body centre (BX,BY) at (cx, cy)
export const BX = 600, BY = 300;
export const placeB = (cx, cy, sc, inner, { rot = 0, flip = false } = {}) => `<g transform="translate(${f1(cx)} ${f1(cy)}) rotate(${f1(rot)}) scale(${flip ? -sc : sc} ${sc}) translate(${-BX} ${-BY})">${inner}</g>`;
export const toB = (cx, cy, sc, x, y) => [cx + (x - BX) * sc, cy + (y - BY) * sc];
// place a standing bird so its toes rest exactly on ground y (screen)
export const standB = (cx, groundY, sc, inner, opt = {}) => placeB(cx, groundY - (FOOT_Y - BY) * sc, sc, inner, opt);
