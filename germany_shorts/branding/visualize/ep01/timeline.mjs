import { W, H, clamp, lerp, smooth, f1, bigLine, hudText } from './eng.mjs';
import { scale } from './s_scale.mjs';
import { room } from './s_room.mjs';
import { phone, fridge, door } from './s_phone.mjs';
import { river } from './s_river.mjs';
import { salad, gym, track, mountain } from './s_life.mjs';

// music grid: 144 bpm, beat at 40.415 s → bar = 1.6667 s
const BAR = 4 * 60 / 144, M0 = 58.332, MBARS = 21, M1 = M0 + MBARS * BAR;

// integrate a speed profile v(t) → distance (for runs that slow down and stop)
const integ = (v, t, dt = 1 / 120) => { let z = 0; for (let x = 0; x < t; x += dt) z += v(x) * Math.min(dt, t - x); return z; };

const lab = (txt, op = 0.75) => hudText(80, 92, txt, { op });
const sub = (txt, op = 0.45) => hudText(80, 124, txt, { op });
const lineAt = (t, a, b, txt, o) => { const k = Math.min(smooth(a, a + 0.6, t), 1 - smooth(b - 0.6, b, t)); if (k <= 0) return '';
  return `<rect y="700" width="1920" height="380" fill="url(#oband)" opacity="${(0.75 * k).toFixed(3)}"/>` + bigLine(txt, k, o); };
const ODEFS = `<defs><linearGradient id="oband" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0b18" stop-opacity="0"/><stop offset=".6" stop-color="#0a0b18" stop-opacity=".55"/><stop offset="1" stop-color="#0a0b18" stop-opacity=".7"/></linearGradient>
<filter id="ob30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter></defs>`;

// first run: slow, heavy, stops at 0.80 km
const v1 = x => 2.1 * (1 - smooth(7.2, 10.2, x));
const v1End = integ(v1, 12.5);
// final run: fast, eases to a walk after 5.00 km
const v2 = x => 3.7 * (1 - 0.7 * smooth(11.5, 14.5, x));

const montage = [
  ['gym', 0], ['salad', 0], ['river', 'predawn'], ['track', 0], ['mountain', 0], ['gym', 5], ['river', 'rain'],
  ['salad', 4], ['track', 3], ['mountain', 6], ['river', 'predawn', 30], ['gym', 9], ['salad', 8], ['river', 'rain', 20],
  ['track', 7], ['mountain', 12], ['gym', 13], ['river', 'dawn', 10], ['track', 11], ['mountain', 18], ['river', 'dawn', 40],
];
const mScene = (k, t) => {
  const [kind, a, b] = montage[k];
  if (kind === 'river') return river(t + (b || 0), { mood: a, hud: false, speed: 3.2 });
  return { gym, salad, track, mountain }[kind](t + a);
};

// segments: [start, end, render(tLocal) → svg body (open <svg>), overlay(tLocal) → svg text, fadeIn, fadeOut]
export const SEG = [
  [0, 5, t => scale(t, { kg: '100.0', belly: 1 }), t => lab('07:02 AM'), 0, 0.4],
  [5, 14, t => room(t, { mode: 'night', push: 0.02 }), t => lab('11:48 PM') + lineAt(t, 2.5, 8.4, 'Another day.'), 0.4, 0.3],
  [14, 20, t => phone(t, { mode: 'feed', clock: '1:37' }), t => lab('01:37 AM'), 0.3, 0.3],
  [20, 26, t => fridge(t), t => lab('02:14 AM'), 0.3, 0.5],
  [26, 33, t => scale(t + 5, { kg: '100.0', belly: 1 }), t => lab('07:04 AM') + lineAt(t, 1.6, 6.6, 'You know this isn’t you.'), 0.5, 0.6],
  [33, 40, t => phone(t, { mode: 'alarm', clock: '11:58' }), t => {
    const a = smooth(4.6, 5.2, t), b = smooth(5.2, 5.8, t) * (1 - smooth(6.6, 7, t));
    return `<rect width="1920" height="1080" fill="#000" opacity="${a.toFixed(3)}"/>` +
      `<text x="960" y="560" text-anchor="middle" font-family="Mono" font-size="64" letter-spacing="14" fill="#ffd2a6" opacity="${b.toFixed(3)}">DAY 001</text>`;
  }, 0.6, 0],
  [40, 46, t => door(t), t => lab('05:38 AM'), 0.4, 0.3],
  [46, M0, t => river(t, { mood: 'predawn', zAt: integ(v1, t), bob: 0.055 * Math.max(0.15, v1(t) / 2.1), step: 2.2,
      km: 0.62 + 0.18 * integ(v1, t) / v1End, sec: 7 * 60 + 14 + t, day: 1, clock: '05:41 AM' }),
    t => lineAt(t, 9.3, 12.3, 'Day one. You stopped at 800 m.'), 0.3, 0],
  [M0, M1, t => { const k = Math.min(MBARS - 1, Math.floor(t / BAR)); return mScene(k, t - k * BAR); }, t => {
    const p = clamp(t / (M1 - M0)), day = Math.round(lerp(14, 300, p)), kg = 98.4 - 16.0 * (1 - Math.pow(1 - p, 1.4));
    return `<g font-family="Mono"><text x="80" y="92" font-size="20" fill="#f4ecff" opacity=".75">DAY ${String(day).padStart(3, '0')} / 365</text>
      <text x="80" y="140" font-size="34" fill="#ffd2a6">${kg.toFixed(1)} kg</text></g>`;
  }, 0, 0],
  [M1, 104.5, t => river(t, { mood: 'rain', speed: 2.8, day: 301, clock: '05:32 AM', km0: 1.2, sec0: 6 * 60 + 5 }),
    t => lineAt(t, 2.0, 10.6, 'The days you don’t want to are the days that count.', { size: 50 }), 0, 0.5],
  [104.5, 122, t => river(t, { mood: 'dawn', zAt: integ(v2, t), speed: 3.7, bob: 0.03 * (1 - 0.5 * smooth(11.5, 14.5, t)), step: 3.0,
      km: Math.min(5, 4.80 + 0.2 * t / 11.5), sec: 24 * 60 + 31 + Math.min(t, 11.5), day: 365, clock: '06:12 AM' }),
    t => lineAt(t, 12.6, 17.2, 'Five kilometres. Before breakfast.'), 0.5, 0.5],
  [122, 130, t => scale(t, { kg: '80.0', belly: 0, warm: 1 }), t => lab('07:02 AM') + sub('DAY 365') + lineAt(t, 2.2, 7.5, '−20 kg.'), 0.5, 0.4],
  [130, 136.5, t => room(t, { mode: 'morning', push: 0.02 }), t => lab('07:30 AM') + lineAt(t, 1.4, 6.2, 'Same room. Different life.'), 0.4, 0.4],
  [136.5, 144, t => river(t + 3, { mood: 'dawn', hud: false, speed: 1.4, bob: 0.012 }), t => {
    const a = smooth(0.6, 1.6, t), b = smooth(1.8, 2.8, t);
    return `<ellipse cx="960" cy="560" rx="620" ry="170" fill="#0e1024" opacity="${(0.5 * a).toFixed(3)}" filter="url(#ob30)"/>
      <text x="960" y="560" text-anchor="middle" font-family="InterB" font-size="112" letter-spacing="22" fill="#fff3e4" opacity="${a.toFixed(3)}">VISUALIZE</text>
      <text x="960" y="632" text-anchor="middle" font-family="SerifI" font-size="46" fill="#ffd2a6" opacity="${b.toFixed(3)}">This could be you in 365 days.</text>`;
  }, 0.4, 2.0],
];
export const TOTAL = 144;

export function frameSVG(T) {
  const i = SEG.findIndex(s => T >= s[0] && T < s[1]); const s = SEG[Math.max(0, i)];
  const t = T - s[0], d = s[1] - s[0];
  const fade = Math.min(s[4] > 0 ? smooth(0, s[4], t) : 1, s[5] > 0 ? 1 - smooth(d - s[5], d, t) : 1);
  const body = s[2](t), over = s[3](t);
  const dark = fade < 1 ? `<rect width="1920" height="1080" fill="#000" opacity="${(1 - fade).toFixed(3)}"/>` : '';
  return body + ODEFS + over + dark + '</svg>';
}
