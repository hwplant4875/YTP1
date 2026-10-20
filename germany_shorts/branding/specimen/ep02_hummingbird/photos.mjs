// real photos as <symbol>s, injected once per page (outside the per-frame SVG) so frames stay light
import fs from 'fs';
const D = '/tmp/claude-0/hb2/photos/web/';
export const PHOTO_DEFS = () => {
  if (!fs.existsSync(D + 'sizes.json')) return '';
  const S = JSON.parse(fs.readFileSync(D + 'sizes.json', 'utf8'));
  return `<svg width="0" height="0" style="position:absolute"><defs>${Object.entries(S).map(([n, [w, h]]) =>
    `<symbol id="P_${n}" viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid slice"><image width="${w}" height="${h}" href="data:image/jpeg;base64,${fs.readFileSync(D + n + '.jpg').toString('base64')}"/></symbol>`).join('')}</defs></svg>`;
};
