// HALFCUT logo drafts (800x800) + banner (2560x1440)
export { FONTS } from './volcano.mjs';
const BG = `<defs><radialGradient id="bg" cx=".5" cy=".42" r=".7"><stop offset="0" stop-color="#262a5a"/><stop offset="1" stop-color="#11142c"/></radialGradient>
<linearGradient id="shell" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6a5f9e"/><stop offset="1" stop-color="#2a2550"/></linearGradient>
<radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff1b8"/><stop offset=".6" stop-color="#ffb02e"/><stop offset="1" stop-color="#ff6a1f"/></radialGradient>
<filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter></defs>
<rect width="800" height="800" fill="url(#bg)"/>`;
const svg = (b, w = 800, h = 800) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${b}</svg>`;

// 1: a planet-like sphere with the front-right half sliced off, layers on the cut face
export function L1() {
  const cx = 400, cy = 400, r = 250, ex = 120;
  let s = BG + `<circle cx="${cx}" cy="${cy}" r="${r + 60}" fill="#ff7a2a" opacity=".12" filter="url(#gl)"/>`;
  // hemisphere shell: left semicircle + right side along the cut ellipse
  s += `<path d="M${cx} ${cy - r} A${r} ${r} 0 0 0 ${cx} ${cy + r} A${ex} ${r} 0 0 0 ${cx} ${cy - r}Z" fill="url(#shell)"/>`;
  s += `<path d="M${cx} ${cy - r} A${r} ${r} 0 0 0 ${cx - r * 0.5} ${cy + r * 0.866}" stroke="#ffd2a6" stroke-width="5" fill="none" opacity=".5"/>`;
  // cut face (ellipse) with layers
  const L = [[1, '#f3e3cf'], [0.9, '#8e5a44'], [0.62, '#ff6a1f'], [0.38, 'url(#core)']];
  L.forEach(([k, c]) => { s += `<ellipse cx="${cx}" cy="${cy}" rx="${ex * k}" ry="${r * k}" fill="${c}"/>`; });
  return svg(s);
}
// 2: a bold H sliced diagonally, halves slid apart, glowing inside
export function L2() {
  const T = `<text x="400" y="560" text-anchor="middle" font-family="Black" font-size="470" fill="#fff4e6">H</text>`;
  let s = BG + `<defs><clipPath id="up"><path d="M0 0 L800 0 L800 250 L0 560Z"/></clipPath><clipPath id="dn"><path d="M0 560 L800 250 L800 800 L0 800Z"/></clipPath></defs>`;
  s += `<path d="M90 560 L710 300" stroke="#ff7a2a" stroke-width="40" opacity=".55" filter="url(#gl)"/>`;
  s += `<g clip-path="url(#dn)" transform="translate(14 18)"><g>${T}</g></g>`;
  s += `<g transform="translate(-14 -18)"><g clip-path="url(#up)">${T.replace('#fff4e6', '#ffb36b')}</g></g>`;
  s += `<path d="M150 541 L650 334" stroke="#fff1b8" stroke-width="5" opacity=".9"/>`;
  return svg(s);
}
// 3: a disc split in two: left half solid, right half reveals the rings inside
export function L3() {
  const cx = 400, cy = 400, r = 250, g = 16;
  let s = BG + `<circle cx="${cx + g}" cy="${cy}" r="${r + 40}" fill="#ff7a2a" opacity=".14" filter="url(#gl)"/>`;
  s += `<path d="M${cx - g} ${cy - r} A${r} ${r} 0 0 0 ${cx - g} ${cy + r}Z" fill="#fff4e6"/>`;
  const R = [[1, '#8e5a44'], [0.8, '#c2261b'], [0.6, '#ff6a1f'], [0.4, '#ffb02e'], [0.2, '#fff1b8']];
  R.forEach(([k, c]) => { s += `<path d="M${cx + g} ${cy - r * k} A${r * k} ${r * k} 0 0 1 ${cx + g} ${cy + r * k}Z" fill="${c}"/>`; });
  return svg(s);
}
export function banner() {
  const W = 2560, H = 1440;
  let s = `<defs><linearGradient id="bb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#11142c"/><stop offset=".7" stop-color="#2f2a5c"/><stop offset="1" stop-color="#9a5f86"/></linearGradient>
  <filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <clipPath id="up"><path d="M0 0 L2560 0 L2560 640 L0 800Z"/></clipPath><clipPath id="dn"><path d="M0 800 L2560 640 L2560 1440 L0 1440Z"/></clipPath></defs>
  <rect width="${W}" height="${H}" fill="url(#bb)"/>`;
  // half-cut icons scattered outside the text (left and right)
  const halfDisc = (cx, cy, r, cols) => { let g = `<path d="M${cx - 6} ${cy - r} A${r} ${r} 0 0 0 ${cx - 6} ${cy + r}Z" fill="#3a3566"/>`;
    cols.forEach((c, i) => { const k = 1 - i / cols.length; g += `<path d="M${cx + 6} ${cy - r * k} A${r * k} ${r * k} 0 0 1 ${cx + 6} ${cy + r * k}Z" fill="${c}"/>`; }); return g; };
  s += halfDisc(600, 720, 80, ['#8e5a44', '#ff6a1f', '#ffb02e', '#fff1b8']) + halfDisc(1960, 720, 80, ['#d9e7ef', '#7fb3d5', '#2f6f9f', '#123b5c']);
  const T = `<text x="1280" y="770" text-anchor="middle" font-family="Black" font-size="180" letter-spacing="6" fill="#fff4e6">HALFCUT</text>`;
  s += `<path d="M900 763 L1660 667" stroke="#ff7a2a" stroke-width="40" opacity=".5" filter="url(#gl)"/>`;
  s += `<g transform="translate(8 10)"><g clip-path="url(#dn)">${T}</g></g><g transform="translate(-8 -10)"><g clip-path="url(#up)">${T.replace('#fff4e6', '#ffb36b')}</g></g>`;
  s += `<text x="1280" y="860" text-anchor="middle" font-family="Mono" font-size="44" letter-spacing="10" fill="#ffd2a6">EVERYTHING, CUT IN HALF</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${s}</svg>`;
}
