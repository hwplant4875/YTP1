// SPECIMEN v2 engine: big, simple, kid-friendly graphics (16:9, 60 fps)
export { FONTS } from '/tmp/claude-0/sp/eng.mjs';
import { SHARK, anatomy, sharkOpen } from '/tmp/claude-0/hc/specimen.mjs';
export { SHARK, anatomy, sharkOpen };
export const W = 1920, H = 1080;
export const K = { navy: '#0d1b3a', white: '#ffffff', yellow: '#f2b632', red: '#ff5a4f', green: '#2fd47a', purple: '#9b7bd8', cyan: '#8ff0ff', deep: '#0f4f86',
  sea1: '#4cb3e8', sea2: '#1f7fc4', muscle: '#5a2a3c', sand: '#e9d29a' };
export const f1 = v => (Math.round(v * 10) / 10).toString();
export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
export const eo = (a, b, t) => { const x = clamp((t - a) / (b - a)); return 1 - Math.pow(1 - x, 3); };
// ease-out-back for pops (overshoot)
export const pop = (a, t, d = 0.45) => { const x = clamp((t - a) / d); const c = 1.9; return x <= 0 ? 0 : 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
export const lerp = (a, b, k) => a + (b - a) * k;
export const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
let _S = 1; export const seed = s => { _S = s; }; export const rnd = () => (_S = (_S * 16807) % 2147483647) / 2147483647;

// background: ocean gradient, soft light rays, rising bubbles
export const bg = (t, v = 'sea') => {
  const g = v === 'deep' ? ['#1a5f9c', '#0b3866'] : v === 'night' ? ['#123a66', '#08203f'] : v === 'sand' ? ['#f6eedb', '#efe2c2'] : [K.sea1, K.sea2];
  let s = `<defs><linearGradient id="bgG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgG)"/>`;
  if (v === 'sand') return s;
  for (let i = 0; i < 4; i++) { const x = 300 + i * 420 + 60 * Math.sin(t * 0.3 + i); s += `<path d="M${f1(x)} -20 L${f1(x + 160)} -20 L${f1(x + 420)} ${H} L${f1(x + 120)} ${H}Z" fill="#ffffff" opacity="0.045"/>`; }
  seed(77); for (let i = 0; i < 26; i++) { const x0 = rnd() * W, sp = 30 + rnd() * 50, r = 3 + rnd() * 7, ph = rnd() * 2000;
    const y = H + 40 - ((t * sp + ph) % (H + 120)); const x = x0 + 14 * Math.sin(t * 1.3 + i);
    s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.28"/>`; }
  return s;
};
// big word that pops in around its anchor
export const big = (x, y, word, t, t0, { size = 160, fill = K.white, anchor = 'middle', stroke = K.navy, sw = 0, rot = 0 } = {}) => {
  const k = pop(t0, t); if (k <= 0) return '';
  return `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${rot}) scale(${f1(k * 1000) / 1000})"><text x="0" y="${f1(size * 0.36)}" font-family="Black" font-size="${size}" fill="${fill}" text-anchor="${anchor}"${sw ? ` stroke="${stroke}" stroke-width="${sw}" paint-order="stroke"` : ''}>${esc(word)}</text></g>`;
};
// pill label with a thick leader line to a point on the drawing
export const tag = (px, py, tx, ty, word, t, t0, { col = K.white, txt = K.navy, size = 70, line = true } = {}) => {
  if (t < t0) return '';
  const lk = eo(t0, t0 + 0.3, t), k = pop(t0 + 0.12, t), w = word.length * size * 0.64 + 72, h = size + 42;
  const lx = lerp(px, tx, lk), ly = lerp(py, ty, lk);
  return (line ? `<path d="M${f1(px)} ${f1(py)} L${f1(lx)} ${f1(ly)}" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/><circle cx="${f1(px)}" cy="${f1(py)}" r="15" fill="#fff" stroke="${K.navy}" stroke-width="6"/>` : '')
    + (k > 0 ? `<g transform="translate(${f1(tx)} ${f1(ty)}) scale(${f1(k * 1000) / 1000})"><rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${h}" rx="${h / 2}" fill="${col}" stroke="${K.navy}" stroke-width="5"/>
      <text x="0" y="${f1(size * 0.36)}" font-family="Black" font-size="${size}" fill="${txt}" text-anchor="middle">${esc(word)}</text></g>` : '');
};
// shark helpers: place the 1000x400 shark box with its body centre at (cx, cy)
export const SCX = 500, SCY = 215;
export const place = (cx, cy, sc, inner, { rot = 0, flip = false } = {}) => `<g transform="translate(${f1(cx)} ${f1(cy)}) rotate(${f1(rot)}) scale(${flip ? -sc : sc} ${sc}) translate(${-SCX} ${-SCY})">${inner}</g>`;
export const toScr = (cx, cy, sc, x, y) => [cx + (x - SCX) * sc, cy + (y - SCY) * sc];
let _id = 0;
export const sharkSolid = (fill = '#ffffff', stroke = K.navy, sw = 8) => `<path d="${SHARK}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/><circle cx="905" cy="190" r="9" fill="${K.navy}"/>
  <path d="M915 232 C935 236 960 234 976 226" stroke="${K.navy}" stroke-width="4" fill="none" stroke-linecap="round"/>${[0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 178 C${722 + i * 17} 210 ${720 + i * 17} 240 ${712 + i * 17} 258" stroke="${K.navy}" stroke-width="4" fill="none" opacity=".55"/>`).join('')}`;
export const sharkInside = (opt = {}, stroke = K.navy, sw = 8) => { const id = 'si' + (_id++ % 1000);
  return `<defs><clipPath id="${id}"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#ffffff"/><g clip-path="url(#${id})">${anatomy({ col: 1, ...opt })}</g><path d="${SHARK}" fill="none" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`; };
export const sharkXray = (sw = 6) => { const id = 'sx' + (_id++ % 1000);
  return `<defs><clipPath id="${id}"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="${K.navy}" opacity=".45"/><g clip-path="url(#${id})">${anatomy({ organs: 0, muscle: 0, col: 0 })}</g><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="${sw}" stroke-linejoin="round"/>`; };
export const bob = (t, a = 8, f = 1.1) => a * Math.sin(t * f);
// organ points in shark-box coordinates
export const PT = { liver: [575, 258], heart: [774, 272], spine: [500, 168], stomach: [626, 226], valve: [420, 230], gills: [750, 215], brain: [848, 176], snout: [955, 205], eye: [905, 190], tail: [70, 200], dorsal: [500, 70], pec: [640, 300], jaw: [945, 238], muscle: [300, 200] };

// simple chunky icons (drawn around 0,0, about 200 px wide)
export const ICON = {
  car: (c = '#fff') => `<path d="M-230 40 L-230 -10 Q-220 -40 -170 -45 L-110 -100 Q-90 -115 -40 -115 L60 -115 Q100 -115 130 -90 L190 -45 Q230 -40 235 -5 L235 40Z" fill="${c}" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><path d="M-95 -50 L-55 -92 L10 -92 L10 -50Z M30 -50 L30 -92 L80 -92 L135 -50Z" fill="${K.cyan}" stroke="${K.navy}" stroke-width="6"/><circle cx="-130" cy="45" r="42" fill="${K.navy}"/><circle cx="135" cy="45" r="42" fill="${K.navy}"/><circle cx="-130" cy="45" r="16" fill="#ccc"/><circle cx="135" cy="45" r="16" fill="#ccc"/>`,
  rhino: (c = '#b9c0cc') => `<path d="M-200 30 Q-215 -60 -150 -95 Q-60 -130 60 -110 Q120 -100 150 -70 L190 -100 L185 -60 Q230 -50 240 -10 Q245 20 215 30 L190 30 L185 90 L145 90 L140 40 L-110 40 L-115 90 L-155 90 L-160 40Z" fill="${c}" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><path d="M215 -25 L268 -95 L240 -18Z" fill="#fff" stroke="${K.navy}" stroke-width="6"/><circle cx="170" cy="-40" r="7" fill="${K.navy}"/><path d="M120 -95 L135 -140 L150 -92" fill="${c}" stroke="${K.navy}" stroke-width="6"/>`,
  fish: (c = K.yellow) => `<path d="M-90 0 C-50 -55 50 -55 90 0 C50 55 -50 55 -90 0Z" fill="${c}" stroke="${K.navy}" stroke-width="7"/><path d="M85 0 L140 -45 L140 45Z" fill="${c}" stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"/><circle cx="-45" cy="-10" r="9" fill="${K.navy}"/>`,
  seal: (c = '#8a8f9c') => `<path d="M-150 20 Q-160 -40 -100 -60 Q-20 -80 60 -50 Q120 -25 150 20 Q120 45 40 45 L-90 45 Q-140 45 -150 20Z" fill="${c}" stroke="${K.navy}" stroke-width="7"/><circle cx="-110" cy="-20" r="8" fill="${K.navy}"/><path d="M140 15 L190 -20 L185 40Z" fill="${c}" stroke="${K.navy}" stroke-width="6"/><path d="M-40 40 L-10 80 L20 40" fill="${c}" stroke="${K.navy}" stroke-width="6"/>`,
  tree: () => `<rect x="-22" y="20" width="44" height="120" fill="#8a5a2b" stroke="${K.navy}" stroke-width="7"/><circle cx="0" cy="-30" r="95" fill="${K.green}" stroke="${K.navy}" stroke-width="7"/><circle cx="-60" cy="20" r="55" fill="${K.green}" stroke="${K.navy}" stroke-width="7"/><circle cx="60" cy="20" r="55" fill="${K.green}" stroke="${K.navy}" stroke-width="7"/>`,
  dino: () => `<path d="M-200 60 Q-120 40 -80 -10 Q-40 -60 20 -60 Q60 -60 80 -110 Q90 -170 140 -175 Q200 -178 205 -140 Q205 -115 165 -115 L140 -110 Q120 -40 110 0 Q100 60 60 70 L60 120 L25 120 L25 75 L-40 75 L-40 120 L-75 120 L-78 70 Q-140 75 -200 60Z" fill="#7ac36a" stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"/><circle cx="170" cy="-150" r="7" fill="${K.navy}"/>`,
  eye: (c = '#fff') => `<path d="M-120 0 Q0 -95 120 0 Q0 95 -120 0Z" fill="${c}" stroke="${K.navy}" stroke-width="8"/><circle r="42" fill="${K.navy}"/><circle cx="-14" cy="-14" r="12" fill="#fff"/>`,
  nose: () => `<path d="M-30 -110 Q10 -40 70 20 Q80 50 40 55 L-40 55" fill="none" stroke="${K.navy}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>`,
  bolt: (c = K.yellow) => `<path d="M30 -130 L-70 15 L-5 15 L-35 130 L75 -25 L10 -25Z" fill="${c}" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/>`,
  wave: (c = '#fff') => `<path d="M-120 -30 Q-90 -70 -60 -30 T0 -30 T60 -30 T120 -30 M-120 30 Q-90 -10 -60 30 T0 30 T60 30 T120 30" fill="none" stroke="${c}" stroke-width="14" stroke-linecap="round"/>`,
  shield: (c = K.green) => `<path d="M0 -150 L130 -100 Q130 60 0 150 Q-130 60 -130 -100Z" fill="${c}" stroke="${K.navy}" stroke-width="9" stroke-linejoin="round"/><path d="M-55 0 L-15 40 L60 -45" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>`,
  smell: () => `<path d="M-60 60 Q-90 0 -60 -40 Q-30 -80 -60 -120 M0 60 Q-30 0 0 -40 Q30 -80 0 -120 M60 60 Q30 0 60 -40 Q90 -80 60 -120" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round"/>`,
  head: () => `<path d="M-90 120 L-90 60 Q-160 20 -150 -60 Q-140 -170 -20 -175 Q100 -178 120 -80 Q125 -50 150 -10 Q160 10 135 18 L125 20 Q130 60 100 70 Q80 75 60 72 L60 120Z" fill="#ffd9b8" stroke="${K.navy}" stroke-width="8" stroke-linejoin="round"/><circle cx="60" cy="-60" r="10" fill="${K.navy}"/>`,
};
export const icon = (name, x, y, s, t, t0, { rot = 0, arg } = {}) => { const k = pop(t0, t); if (k <= 0) return '';
  return `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(${f1(s * k * 1000) / 1000})">${ICON[name](arg)}</g>`; };
// big red X
export const cross = (x, y, r, t, t0) => { const k = eo(t0, t0 + 0.25, t); if (k <= 0) return '';
  return `<path d="M${x - r} ${y - r} L${f1(x - r + 2 * r * k)} ${f1(y - r + 2 * r * k)}" stroke="${K.red}" stroke-width="28" stroke-linecap="round"/>` + (k >= 1 ? `<path d="M${x + r} ${y - r} L${f1(x + r - 2 * r * eo(t0 + 0.2, t0 + 0.45, t))} ${f1(y - r + 2 * r * eo(t0 + 0.2, t0 + 0.45, t))}" stroke="${K.red}" stroke-width="28" stroke-linecap="round"/>` : ''); };
// counter that rolls up to a number
export const count = (to, t, t0, d = 1.0, fmt = v => Math.round(v).toLocaleString('en-US')) => t < t0 ? '' : fmt(to * eo(t0, t0 + d, t));
