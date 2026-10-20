import { FONTS } from '/tmp/claude-0/sp2/eng2.mjs'; export { FONTS };
export const DOG = `M405 -95 C415 -88 415 -70 400 -64 C370 -56 335 -52 305 -48 C285 -44 270 -30 262 -14 C252 8 244 30 232 52 C228 100 230 170 232 212 C242 216 258 220 262 228 C260 234 240 234 210 232 C208 180 204 110 196 64 C180 70 160 66 150 60
 C80 40 -20 34 -80 40 C-84 70 -90 96 -100 116 C-110 136 -128 156 -134 176 C-136 196 -134 212 -130 222 C-118 224 -106 228 -104 232 C-120 234 -150 234 -166 232 C-170 210 -172 194 -176 180 C-190 150 -214 100 -224 50 C-232 10 -232 -30 -222 -62
 C-262 -90 -300 -150 -282 -214 C-268 -172 -244 -124 -206 -98 C-120 -112 40 -112 150 -102 C190 -110 214 -140 228 -172 L240 -252 L282 -196 C292 -198 302 -198 312 -198 L336 -258 L348 -176 C356 -150 368 -122 382 -114 C394 -108 402 -102 405 -95Z
 M180 60 C178 120 176 190 180 214 C188 218 200 222 204 230 L156 230 C156 190 152 120 150 60Z
 M-50 40 C-50 80 -60 110 -74 130 C-86 150 -92 176 -90 214 C-82 220 -72 224 -70 230 L-108 230 C-112 200 -110 170 -102 150 C-92 120 -90 80 -92 42Z`;
export const svg = (f) => `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#5fb0ff"/>
<defs><filter id="p" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="16"/><feGaussianBlur stdDeviation="3.5"/></filter></defs>
<g transform="translate(500 560) scale(1.1)"><path d="${DOG}" fill="#0b0f1e" fill-rule="nonzero"/></g>
<g transform="translate(1400 560) scale(1.1)"><g filter="url(#p)"><path d="${DOG}" fill="#0b0f1e"/></g></g></svg>`;
