// outro for every hummingbird short: a payoff line (big text over a payoff prop), then the comment question with a comment pill
import fs from 'fs';
import { K, f1, sm, eo, pop, lerp, esc, xfade } from '/tmp/claude-0/sp2/eng2.mjs';
import { fly, birdHeart } from '/tmp/claude-0/hb2/ha.mjs';
import { battery } from './vs1.mjs';
const N = K.navy;
const SPEC = Object.fromEntries(JSON.parse(fs.readFileSync('/tmp/claude-0/hbs/spec.json')).map(s => [s.id, s]));
const OA = {};
const oat = (sid, phrase) => { OA[sid] ??= JSON.parse(fs.readFileSync(`/tmp/claude-0/hbs/audio/o_${sid}.json`));
  const s = OA[sid].characters.join(''), i = s.indexOf(phrase); if (i < 0) throw new Error(`outro phrase ${sid}: ${phrase}`); return 0.15 + OA[sid].character_start_times_seconds[i]; };
// two stacked lines, popping in one after the other; last line yellow; o = opacity
const lines2 = (ls, t, t0, o) => { const size = Math.min(130, Math.floor(980 / (Math.max(...ls.map(l => l.length)) * 0.66)));
  return `<g opacity="${f1(o)}">` + ls.map((l, i) => { const k = pop(t0 + i * 0.25, t); if (k <= 0) return '';
    return `<g transform="translate(540 ${f1(1140 + i * size * 1.08)}) scale(${f1(k * 1000) / 1000})"><text x="0" y="${f1(size * 0.36)}" font-family="Black" font-size="${size}" fill="${i === ls.length - 1 ? K.yellow : '#fff'}" stroke="${N}" stroke-width="${f1(size * 0.14)}" paint-order="stroke" stroke-linejoin="round" text-anchor="middle">${esc(l)}</text></g>`; }).join('') + '</g>'; };
// comment pill: speech-bubble icon + COMMENT, gently pulsing
const pill = (t, t0, kind) => { const k = pop(t0, t); if (k <= 0) return ''; const p = 1 + 0.04 * Math.sin((t - t0) * 6);
  const ic = kind === 'video' ? `<g transform="translate(-200 0)"><circle r="46" fill="${K.red}"/><path d="M-14 -24 L26 0 L-14 24 Z" fill="#fff"/></g>` : `<g transform="translate(-200 0)"><rect x="-48" y="-40" width="96" height="70" rx="20" fill="${N}"/><path d="M-22 28 L-30 52 L2 28 Z" fill="${N}"/>${[-22, 0, 22].map(x => `<circle cx="${x}" cy="-5" r="8" fill="#fff"/>`).join('')}</g>`;
  return `<g transform="translate(540 1478) scale(${f1(k * p * 1000) / 1000})"><rect x="-290" y="-60" width="580" height="120" rx="60" fill="#fff" stroke="${N}" stroke-width="10"/>${ic}<text x="60" y="24" font-family="Black" font-size="66" fill="${N}" text-anchor="middle">${kind === 'video' ? 'LINK BELOW' : 'COMMENT'}</text></g>`; };
const hover = (t, y = 850) => fly(540, y + 18 * Math.sin(t * 2.2), 1.0, t, { rate: 7, amp: 55 });
// payoff props: b01 beating heart, b02 battery charging back up, everyone else the hovering bird
const PROP = {
  b01: t => birdHeart(540, 880, 4.4, 1 + 0.16 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 3)), 3)),
  b02: t => { const lv = lerp(0.08, 1, eo(0.3, 2.0, t)), sun = pop(0.2, t);
    return `<circle cx="830" cy="560" r="${f1(85 * sun)}" fill="#ffe27a" stroke="#fff" stroke-width="10"/>` + battery(540, 820, 1.7, lv) +
      (lv > 0.98 ? `<path d="M520 760 L575 760 L545 815 L590 815 L515 900 L535 835 L495 835 Z" fill="${K.yellow}" stroke="${N}" stroke-width="8" stroke-linejoin="round" opacity="${f1(sm(2.0, 2.3, t))}"/>` : ''); },
};
export const OUT = sid => (t, lt) => { const S = SPEC[sid], tq = oat(sid, S.oqs), prop = PROP[sid] || hover;
  let s = t < tq - 0.35 ? prop(t) : xfade(t, tq - 0.35, 0.45, () => prop(t), () => hover(t));
  s += lines2(S.op, t, 0.2, 1 - sm(tq - 0.35, tq - 0.1, t));
  if (t > tq - 0.1) s += lines2(S.oq, t, tq - 0.05, 1) + pill(t, tq + 0.35, S.pill);
  return s; };
