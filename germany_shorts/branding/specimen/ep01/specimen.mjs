// SPECIMEN style frames (world.execute(me)-like motion-graphic documents), 16:9
import fs from 'fs';
const FD = '/tmp/claude-0/vz/flat/fonts/';
const ff = (n, f, fmt = 'woff2') => `@font-face{font-family:${n};src:url(data:font/${fmt};base64,${fs.readFileSync(f).toString('base64')})}`;
export const FONTS = ff('Mono', FD + 'mono.woff2') + ff('SerifI', FD + 'serif_i.woff2') + ff('Inter', FD + 'inter.woff2') + ff('InterB', FD + 'interb.woff2')
  + ff('Black', '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', 'otf');
export const W = 1920, H = 1080;
export const C = { navy: '#0d0f1c', ink: '#e9e6f2', dim: '#8a8aa6', acc: '#3fd0ff', warm: '#ff8a7a', paper: '#eeeae1', pink: '#f2a7a0' };
const f1 = v => (Math.round(v * 10) / 10).toString();

// great white side profile, facing right, in a 1000x400 box (origin top-left)
export const SHARK = `M985 212 C975 178 930 152 860 146 C760 140 640 134 572 128 C545 92 520 52 498 18 C488 60 470 100 452 126
 C380 128 300 140 230 150 C226 138 220 126 210 118 C204 132 198 144 190 152 C160 160 135 168 118 176
 C92 140 55 88 18 40 C30 100 45 150 62 196 C48 238 34 290 26 330 C62 290 96 248 118 214
 C150 220 190 228 228 236 C238 250 246 262 262 270 C262 256 262 246 268 236
 C320 246 360 254 392 262 C376 282 360 300 350 314 C390 304 422 288 444 272
 C520 280 590 286 640 290 C610 330 580 370 556 396 C610 374 660 336 700 298
 C760 296 820 290 860 282 C920 270 965 246 985 212Z`;
export const gills = (op = 1) => [0, 1, 2, 3, 4].map(i => `<path d="M${712 + i * 17} ${172 + i * 2} C${718 + i * 17} ${210 + i * 2} ${716 + i * 17} ${245} ${708 + i * 17} ${268 - i * 3}" stroke="${C.ink}" stroke-width="2" fill="none" opacity="${0.6 * op}"/>`).join('');
export const face = () => `<circle cx="905" cy="190" r="7" fill="${C.ink}"/><path d="M955 240 C925 252 880 258 838 254" stroke="${C.ink}" stroke-width="2" fill="none" opacity=".7"/>`;

const grid = (col, op) => { let s = ''; for (let x = 0; x <= W; x += 60) s += `<path d="M${x} 0 L${x} ${H}" stroke="${col}" stroke-width="1" opacity="${op}"/>`;
  for (let y = 0; y <= H; y += 60) s += `<path d="M0 ${y} L${W} ${y}" stroke="${col}" stroke-width="1" opacity="${op}"/>`; return s; };
const mono = (x, y, t, { size = 18, fill = C.dim, anchor = 'start', op = 1 } = {}) => `<text x="${x}" y="${y}" font-family="Mono" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${op}">${t}</text>`;

// cross-section of the body at the cut (ellipse seen 3/4)
export function section(cx, cy, rx, ry, { lab = true } = {}) {
  let s = `<g>`;
  s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#1b1e33" stroke="${C.ink}" stroke-width="2"/>`;
  s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx * 0.9}" ry="${ry * 0.92}" fill="#3a2234" stroke="${C.warm}" stroke-width="1.5" opacity=".95"/>`;           // red muscle band
  // myomere swirls (white muscle)
  for (const sg of [-1, 1]) for (let k = 0; k < 4; k++) s += `<path d="M${cx} ${cy - ry * 0.55 + k * 4} C${cx + sg * rx * (0.3 + k * 0.12)} ${cy - ry * (0.62 - k * 0.05)} ${cx + sg * rx * (0.62 - k * 0.04)} ${cy - ry * 0.2} ${cx + sg * rx * (0.5 - k * 0.06)} ${cy + ry * 0.05}" stroke="${C.pink}" stroke-width="1.5" fill="none" opacity=".55"/>`;
  s += `<circle cx="${cx}" cy="${cy - ry * 0.48}" r="${ry * 0.11}" fill="${C.paper}" stroke="${C.acc}" stroke-width="2"/>`;                          // cartilage spine
  s += `<path d="M${cx - rx * 0.62} ${cy + ry * 0.0} C${cx - rx * 0.6} ${cy + ry * 0.7} ${cx + rx * 0.6} ${cy + ry * 0.7} ${cx + rx * 0.62} ${cy + ry * 0.0} C${cx + rx * 0.3} ${cy - ry * 0.12} ${cx - rx * 0.3} ${cy - ry * 0.12} ${cx - rx * 0.62} ${cy}Z" fill="#c9a24a" opacity=".9"/>`; // liver
  s += `<ellipse cx="${cx + rx * 0.05}" cy="${cy + ry * 0.18}" rx="${rx * 0.2}" ry="${ry * 0.16}" fill="#7c5a8e"/>`;                               // stomach
  s += `</g>`;
  if (lab) {
    const L = (x, y, tx, ty, a, b) => `<path d="M${x} ${y} L${tx} ${ty} L${tx + 160} ${ty}" stroke="${C.ink}" stroke-width="1.5" fill="none" opacity=".6"/><circle cx="${x}" cy="${y}" r="5" fill="${C.acc}"/>
      ${mono(tx, ty - 10, a, { size: 20, fill: C.ink })}${mono(tx, ty + 24, b, { size: 16, fill: C.acc })}`;
    s += L(cx, cy - ry * 0.48, cx + rx + 120, cy - ry - 30, 'SPINE', 'cartilage, not bone');
    s += L(cx + rx * 0.4, cy + ry * 0.25, cx + rx + 120, cy + ry * 0.2, 'LIVER', '≈ 25% of body mass');
    s += L(cx + rx * 0.8, cy - ry * 0.3, cx + rx + 120, cy - ry * 0.45 + 40, 'RED MUSCLE', 'kept warm');
  }
  return s;
}

export function frameHero() {
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs><clipPath id="back"><rect x="0" y="0" width="600" height="400"/></clipPath><clipPath id="front"><rect x="600" y="0" width="420" height="420"/></clipPath>
  <radialGradient id="v" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></radialGradient></defs>
  <rect width="${W}" height="${H}" fill="${C.navy}"/>${grid('#ffffff', 0.035)}`;
  // header like a document
  s += mono(80, 90, 'SPECIMEN 001', { size: 22, fill: C.acc }) + mono(80, 122, 'Carcharodon carcharias · great white shark', { size: 18 });
  s += mono(1840, 90, 'FIG. 1 — SAGITTAL CUT AT 0.60 L', { size: 16, anchor: 'end' }) + mono(1840, 118, 'scale 1 : 12', { size: 16, anchor: 'end' });
  const ox = 250, oy = 300;
  s += sharkOpen(ox, oy, 1.15, { cut: 812, id: 'hero', sw: 2.5, skin: '#1b1f36', stroke: '#e9e6f2' });
  const P = (x, y) => [ox + x * 1.15, oy + y * 1.15];
  const L = (bx, by, tx, ty, a, b, anc = 'start') => { const [x, y] = P(bx, by); return `<path d="M${f1(x)} ${f1(y)} L${tx} ${ty}" stroke="${C.ink}" stroke-width="1.3" fill="none" opacity=".55"/><circle cx="${f1(x)}" cy="${f1(y)}" r="5" fill="${C.acc}"/>
      ${mono(tx + (anc === 'end' ? -8 : 8), ty - 8, a, { size: 18, fill: C.ink, anchor: anc })}${mono(tx + (anc === 'end' ? -8 : 8), ty + 18, b, { size: 14, fill: C.acc, anchor: anc })}`; };
  s += L(500, 172, 760, 260, 'SPINE', 'cartilage, zero bone') + L(560, 262, 820, 850, 'LIVER', 'about 25% of its mass') + L(420, 230, 470, 850, 'SPIRAL VALVE', 'a corkscrew gut')
     + L(620, 226, 1000, 260, 'STOMACH', 'can turn inside out') + L(300, 180, 330, 260, 'RED MUSCLE', 'runs warm', 'end');
  // scale bar + measurements
  s += `<path d="M${ox} 790 L${ox + 1150} 790" stroke="${C.dim}" stroke-width="1"/>${[0, 1, 2, 3, 4, 5, 6].map(k => `<path d="M${ox + k * 191.7} 782 L${ox + k * 191.7} 798" stroke="${C.dim}"/>${mono(ox + k * 191.7, 818, k + ' m', { size: 14, anchor: 'middle' })}`).join('')}`;
  // lyric-style narration line
  s += `<text x="80" y="930" font-family="SerifI" font-size="64" fill="${C.ink}">This is a great white shark.</text>`;
  s += `<text x="80" y="1000" font-family="SerifI" font-size="64" fill="${C.dim}">Cut <tspan fill="${C.acc}">perfectly</tspan> in half.</text>`;
  s += `<rect width="${W}" height="${H}" fill="url(#v)"/>`;
  return s + '</svg>';
}

// light "paper" frame: a nutrition-label-like spec sheet
export function frameSpec() {
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="${C.paper}"/>`;
  s += `<g transform="translate(1080 140)"><rect width="560" height="800" fill="#fff" stroke="#111" stroke-width="3"/>
    <text x="22" y="72" font-family="Black" font-size="62" fill="#111">Specimen Facts</text>
    <text x="22" y="108" font-family="Inter" font-size="22" fill="#111">1 great white shark per ocean</text>
    <rect x="22" y="124" width="516" height="16" fill="#111"/>
    ${[['Length', '6.0 m'], ['Mass', '2,000 kg'], ['Bones', '0'], ['Teeth at once', '≈ 300'], ['Bite force', '≈ 18,000 N'], ['Liver', '≈ 25% of mass'], ['Muscle temp', 'up to +14 °C'], ['Gill slits', '5 per side']].map(([a, b], i) =>
      `<text x="22" y="${190 + i * 72}" font-family="InterB" font-size="30" fill="#111">${a}</text><text x="538" y="${190 + i * 72}" font-family="InterB" font-size="30" fill="${i === 2 ? '#e0482f' : '#111'}" text-anchor="end">${b}</text><rect x="22" y="${208 + i * 72}" width="516" height="${i === 0 ? 6 : 2}" fill="#111"/>`).join('')}
    <text x="22" y="782" font-family="Inter" font-size="16" fill="#444">* adult female, estimates vary by study</text></g>`;
  s += `<g transform="translate(110 420) scale(0.82)"><path d="${SHARK}" fill="none" stroke="#222" stroke-width="2.4"/>${gills().replaceAll(C.ink, '#222')}<circle cx="905" cy="190" r="7" fill="#222"/></g>`;
  s += `<text x="110" y="300" font-family="Mono" font-size="22" fill="#6b6b80">If I'm a shark</text><text x="110" y="370" font-family="SerifI" font-size="62" fill="#111">Then I have <tspan fill="#e0482f">no bones</tspan> at all</text>`;
  s += `<text x="110" y="810" font-family="Mono" font-size="16" fill="#6b6b80">Fig. 2 — Carcharodon carcharias, lateral view</text>`;
  return s + '</svg>';
}

// thumbnails 1280x720
export function thumb(v = 'a') {
  const T = (w, h, b) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${b}</svg>`;
  const sharkCut = (x, y, sc, stroke, fill, gap, glow) => `<g transform="translate(${x} ${y}) scale(${sc})">
    <defs><clipPath id="tb"><rect x="0" y="0" width="600" height="400"/></clipPath><clipPath id="tf"><rect x="600" y="0" width="420" height="420"/></clipPath></defs>
    <g clip-path="url(#tb)"><path d="${SHARK}" fill="${fill}" stroke="${stroke}" stroke-width="5"/></g>
    <g transform="translate(${gap} 0)" clip-path="url(#tf)"><path d="${SHARK}" fill="${fill}" stroke="${stroke}" stroke-width="5"/><circle cx="905" cy="190" r="10" fill="${glow}"/></g>
    ${section(600 + gap, 212, 46, 78, { lab: false })}${section(600, 212, 46, 78, { lab: false })}</g>`;
  if (v === 'a') return T(1280, 720, `<rect width="1280" height="720" fill="#0d0f1c"/>${sharkCut(180, 300, 1.0, '#ffffff', '#ffffff', 120, '#3fd0ff')}
     <text x="60" y="190" font-family="Black" font-size="150" fill="#ffffff">INSIDE A</text><text x="60" y="190" dx="780" font-family="Black" font-size="150" fill="#3fd0ff">SHARK</text>`);
  if (v === 'b') return T(1280, 720, `<rect width="1280" height="720" fill="#ff2e3c"/>${sharkCut(260, 300, 0.95, '#ffffff', '#ffffff', 120, '#111')}
     <text x="60" y="210" font-family="Black" font-size="190" fill="#ffffff">0 BONES</text>`);
  return T(1280, 720, `<rect width="1280" height="720" fill="#eeeae1"/>${sharkCut(200, 290, 1.0, '#111111', '#ffffff', 120, '#111')}
     <text x="60" y="190" font-family="Black" font-size="150" fill="#111">CUT</text><text x="410" y="190" font-family="Black" font-size="150" fill="#e0482f">OPEN</text>`);
}
export const thumbA = () => thumb('a'), thumbB = () => thumb('b'), thumbC = () => thumb('c');

// sagittal anatomy inside the SHARK box (draw inside a clipPath of SHARK)
export function anatomy({ skel = 1, organs = 1, muscle = 1, col = 1 } = {}) {
  const K = col ? { liver: '#d9a640', stom: '#8b6bb0', gut: '#c27aa8', heart: '#ff5a5f', gill: '#ff7a7a', brain: '#f2d3c4', musc: '#5a2a3c', mline: '#f2a7a0', spine: '#f4efe6', jaw: '#f4efe6', cav: '#2a1c2c' }
    : { liver: '#ffffff', stom: '#ffffff', gut: '#ffffff', heart: '#ffffff', gill: '#ffffff', brain: '#ffffff', musc: 'none', mline: '#ffffff', spine: '#ffffff', jaw: '#ffffff', cav: 'none' };
  let s = '';
  if (muscle) { s += `<path d="${SHARK}" fill="${K.musc}"/>`;
    for (let x = 140; x < 820; x += 34) s += `<path d="M${x} 150 L${x + 16} 178 L${x} 205 L${x + 16} 232" stroke="${K.mline}" stroke-width="2" fill="none" opacity=".35"/>`; }
  if (organs) {
    s += `<path d="M450 214 C520 206 640 208 720 216 L720 280 C640 288 520 282 450 262Z" fill="${K.cav}"/>`;                                   // body cavity
    s += `<path d="M445 238 C480 226 620 222 712 236 C690 262 640 284 560 286 C500 288 460 270 445 238Z" fill="${K.liver}"/>`;             // liver
    s += `<path d="M700 214 C640 210 560 212 540 226 C530 240 560 246 600 240 C640 234 690 232 712 226Z" fill="${K.stom}"/>`;             // stomach
    s += `<path d="M538 226 C500 228 470 224 440 228" stroke="${K.gut}" stroke-width="10" fill="none"/>`;
    for (let i = 0; i < 6; i++) s += `<ellipse cx="${430 - i * 9}" cy="230" rx="7" ry="13" fill="none" stroke="${K.gut}" stroke-width="3"/>`;    // spiral valve
    s += `<path d="M402 232 C380 236 340 240 270 244" stroke="${K.gut}" stroke-width="4" fill="none"/>`;
    for (let i = 0; i < 5; i++) s += `<path d="M${716 + i * 17} 178 C${728 + i * 17} 200 ${728 + i * 17} 236 ${716 + i * 17} 258" stroke="${K.gill}" stroke-width="7" fill="none"/>`;                // gill arches
    s += `<path d="M752 262 C770 254 792 258 796 270 C790 282 768 284 752 276Z" fill="${K.heart}"/>`;                                        // heart
    s += `<ellipse cx="848" cy="176" rx="34" ry="11" fill="${K.brain}"/><path d="M880 176 C905 178 925 186 938 196" stroke="${K.brain}" stroke-width="6" fill="none"/><circle cx="940" cy="198" r="8" fill="${K.brain}"/>`;
    for (let i = 0; i < 14; i++) s += `<circle cx="${948 + (i % 4) * 8}" cy="${200 + Math.floor(i / 4) * 10}" r="2.4" fill="${col ? '#3fd0ff' : '#fff'}"/>`;          // ampullae
  }
  if (skel) {
    for (let x = 150; x < 830; x += 13) { const y = 168 + 10 * Math.sin((x - 150) / 680 * Math.PI) * 0 + (x < 230 ? (230 - x) * -0.22 : 0);
      s += `<rect x="${x}" y="${y - 6}" width="10" height="12" rx="3" fill="${K.spine}"/>`; }
    for (let i = 0; i < 9; i++) s += `<rect x="${118 - i * 9}" y="${148 - i * 12}" width="9" height="10" rx="3" fill="${K.spine}" transform="rotate(-50 ${122 - i * 9} ${153 - i * 12})"/>`;   // into upper caudal lobe
    s += `<path d="M960 226 C930 236 880 240 836 238" stroke="${K.jaw}" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M955 246 C925 256 880 260 836 254" stroke="${K.jaw}" stroke-width="8" fill="none" stroke-linecap="round"/>`;
    for (let i = 0; i < 9; i++) { const x = 945 - i * 12; s += `<path d="M${x} ${231 - i * 1} l5 9 l5 -9Z" fill="#fff"/><path d="M${x} ${250 + i * 0.8} l5 -9 l5 9Z" fill="#fff"/>`; }
  }
  return s;
}
export function sharkOpen(x, y, sc, { cut = 820, skin = '#ffffff', stroke = '#ffffff', sw = 4, col = 1, id = 'so' } = {}) {
  // inside anatomy shown for x < cut (shark box coords), skin in front of it
  return `<g transform="translate(${x} ${y}) scale(${sc})"><defs><clipPath id="${id}s"><path d="${SHARK}"/></clipPath><clipPath id="${id}i"><rect x="0" y="0" width="${cut}" height="420"/></clipPath><clipPath id="${id}o"><rect x="${cut}" y="0" width="1000" height="420"/></clipPath></defs>
    <g clip-path="url(#${id}s)"><g clip-path="url(#${id}i)"><path d="${SHARK}" fill="#1a1426"/>${anatomy({ col })}</g>
    <g clip-path="url(#${id}o)"><path d="${SHARK}" fill="${skin}"/></g></g>
    <path d="${SHARK}" fill="none" stroke="${stroke}" stroke-width="${sw}"/>
    <g clip-path="url(#${id}o)"><circle cx="905" cy="190" r="9" fill="${skin === '#ffffff' ? '#111' : '#e9e6f2'}"/>${[0, 1, 2, 3, 4].map(i => `<path d="M${712 + i * 17} ${176} C${718 + i * 17} 210 ${716 + i * 17} 245 ${708 + i * 17} ${264}" stroke="#555" stroke-width="3" fill="none"/>`).join('')}</g>
    <path d="M${cut} 0 L${cut} 420" stroke="${col ? '#3fd0ff' : '#fff'}" stroke-width="${sw * 0.8}" stroke-dasharray="${sw * 3} ${sw * 2}"/></g>`;
}
export function thumb2(v = 'a') {
  const T = b => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${b}</svg>`;
  if (v === 'a') return T(`<rect width="1280" height="720" fill="#0d0f1c"/>${sharkOpen(110, 250, 1.12, { cut: 812, id: 'ta' })}
     <text x="60" y="180" font-family="Black" font-size="140" fill="#fff">INSIDE A <tspan fill="#3fd0ff">SHARK</tspan></text>`);
  if (v === 'b') return T(`<rect width="1280" height="720" fill="#ff2e3c"/><g transform="translate(120 260) scale(1.1)"><defs><clipPath id="tbx"><path d="${SHARK}"/></clipPath></defs>
     <path d="${SHARK}" fill="#ffffff" opacity=".18"/><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="5"/><g clip-path="url(#tbx)">${anatomy({ organs: 0, muscle: 0, col: 0 })}</g></g>
     <text x="60" y="200" font-family="Black" font-size="190" fill="#fff">0 BONES</text>`);
  return T(`<rect width="1280" height="720" fill="#eeeae1"/>${sharkOpen(110, 250, 1.12, { cut: 1000, stroke: '#111', sw: 5, id: 'tc' })}
     <text x="60" y="180" font-family="Black" font-size="150" fill="#111">CUT <tspan fill="#e0482f">OPEN</tspan></text>`);
}
export const t2A = () => thumb2('a'), t2B = () => thumb2('b'), t2C = () => thumb2('c');
export function frameHero2() {
  let s = frameHero().replace('</svg>', '');
  return s;
}
