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
  rhino: (c = '#b9c0cc') => { const d = '#99a1b0', o = `stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"`;
    return `<path d="M50 40 L46 104 L84 104 L86 40Z M-112 40 L-116 104 L-80 104 L-78 40Z" fill="${d}" ${o}/>
    <path d="M-205 -18 C-226 -8 -234 12 -228 32" stroke="${K.navy}" stroke-width="7" fill="none" stroke-linecap="round"/>
    <path d="M152 -76 C142 -100 148 -122 162 -134 C172 -118 172 -98 166 -78Z" fill="${c}" ${o}/>
    <path d="M196 -56 C200 -74 206 -88 214 -98 C216 -82 216 -66 214 -50Z" fill="#efe9dc" ${o}/>
    <path d="M226 -38 C236 -78 250 -110 270 -130 C264 -96 260 -62 254 -28Z" fill="#efe9dc" ${o}/>
    <path d="M86 40 L82 112 L128 112 L132 40Z M-148 32 L-156 112 L-108 112 L-102 40Z" fill="${c}" ${o}/>
    <path d="M-210 22 C-232 -40 -200 -100 -130 -116 C-60 -132 40 -126 100 -106 C128 -96 146 -84 156 -66 C184 -72 214 -60 234 -36 C250 -20 262 0 260 20 C258 38 240 48 220 46 C204 46 190 42 176 44 C164 62 150 72 136 74 C100 72 64 62 40 62 L-120 62 C-162 62 -200 50 -210 22Z" fill="${c}" ${o}/>
    <path d="M80 -112 C68 -62 74 -12 94 40 M-118 -114 C-108 -62 -110 -12 -100 48 M136 -88 C126 -58 126 -22 140 8" stroke="${K.navy}" stroke-width="4" fill="none" opacity=".45" stroke-linecap="round"/>
    <path d="M222 30 C232 34 244 32 252 26" stroke="${K.navy}" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="194" cy="-26" r="7" fill="${K.navy}"/>
    <path d="M90 110 l8 -10 M106 111 l6 -10 M-146 110 l8 -10 M-130 111 l6 -10" stroke="${K.navy}" stroke-width="4" stroke-linecap="round"/>`; },
  fish: (c = K.yellow) => `<path d="M-90 0 C-50 -55 50 -55 90 0 C50 55 -50 55 -90 0Z" fill="${c}" stroke="${K.navy}" stroke-width="7"/><path d="M85 0 L140 -45 L140 45Z" fill="${c}" stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"/><circle cx="-45" cy="-10" r="9" fill="${K.navy}"/>`,
  seal: (c = '#6f6458') => { const o = `stroke="${K.navy}" stroke-width="6" stroke-linejoin="round"`;
    return `<defs><linearGradient id="sealG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a5047"/><stop offset=".55" stop-color="${c}"/><stop offset="1" stop-color="#b9a68e"/></linearGradient></defs>
    <path d="M150 18 C178 2 200 -6 214 -2 C206 14 196 28 176 36 C196 44 210 56 212 70 C194 70 172 60 150 44Z" fill="#4e463e" ${o}/>
    <path d="M-176 -6 C-170 -34 -146 -52 -118 -54 C-96 -56 -80 -48 -66 -40 C-20 -52 60 -50 120 -24 C150 -10 162 20 152 42 C120 52 60 56 0 52 C-50 50 -90 44 -116 30 C-138 32 -160 26 -172 14 C-178 8 -178 2 -176 -6Z" fill="url(#sealG)" ${o}/>
    <path d="M-40 34 C-34 60 -20 84 6 96 C-12 98 -36 92 -50 78 C-60 66 -60 48 -56 36Z" fill="#4e463e" ${o}/>
    <path d="M-104 -50 C-102 -60 -96 -64 -90 -60" stroke="${K.navy}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <circle cx="-136" cy="-28" r="8" fill="${K.navy}"/><circle cx="-139" cy="-31" r="2.5" fill="#fff"/><ellipse cx="-172" cy="-4" rx="7" ry="5" fill="${K.navy}"/>
    <path d="M-160 4 L-204 -6 M-160 8 L-206 8 M-158 12 L-200 22" stroke="#fff" stroke-width="2.5" opacity=".85" stroke-linecap="round"/>`; },
  tree: () => { const o = `stroke="${K.navy}" stroke-width="7" stroke-linejoin="round"`;
    return `<path d="M-30 150 C-22 90 -24 40 -14 -10 L14 -10 C24 40 22 90 34 150 C10 156 -8 156 -30 150Z" fill="#8a5a2b" ${o}/>
    <path d="M-8 20 C-40 0 -60 -20 -70 -40 M6 0 C34 -20 56 -40 66 -60 M-6 130 C-4 100 -10 70 -4 40 M12 120 C14 90 8 60 12 30" stroke="${K.navy}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M-150 -10 C-190 -20 -200 -80 -160 -100 C-170 -150 -110 -180 -80 -150 C-70 -200 10 -215 30 -170 C70 -200 140 -170 130 -120 C180 -110 190 -40 150 -20 C150 20 90 40 60 10 C30 40 -30 40 -50 10 C-90 30 -150 20 -150 -10Z" fill="#2fb36a" ${o}/>
    <path d="M-120 -40 C-110 -70 -80 -80 -60 -70 M-10 -120 C10 -140 40 -140 60 -120 M60 -60 C80 -80 110 -80 120 -60 M-70 -10 C-50 -30 -20 -30 0 -14" stroke="#1d8a4e" stroke-width="10" fill="none" stroke-linecap="round"/>
    <circle cx="-60" cy="-110" r="12" fill="#5fd38d"/><circle cx="70" cy="-140" r="10" fill="#5fd38d"/><circle cx="110" cy="-40" r="9" fill="#5fd38d"/><circle cx="-120" cy="-20" r="8" fill="#5fd38d"/>`; },
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

// word that fades in softly (no pop)
export const fade = (x, y, word, t, t0, { size = 160, fill = K.white, anchor = 'middle', stroke = K.navy, sw = 0, d = 0.5 } = {}) => {
  const k = sm(t0, t0 + d, t); if (k <= 0) return '';
  return `<text x="${f1(x)}" y="${f1(y + size * 0.36)}" font-family="Black" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${f1(k)}"${sw ? ` stroke="${stroke}" stroke-width="${sw}" paint-order="stroke"` : ''}>${esc(word)}</text>`;
};
// cross-dissolve between two scene parts over [t0, t0 + d]
export const xfade = (t, t0, d, A, B) => { const k = sm(t0, t0 + d, t);
  return (k < 1 ? `<g opacity="${f1(1 - k)}">${A()}</g>` : '') + (k > 0 ? `<g opacity="${f1(k)}">${B()}</g>` : ''); };
