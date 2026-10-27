// All timing lives here so it can be re-synced to the narration.
// mix.py reads VO_STARTS / STEP_FRAMES / REWIND_START from this file.
export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const DURATION = 1440;

// Intro: cover pose (already 9 steps big) then a fast rewind to 170 cm.
export const COVER_N = 9;
export const REWIND_START = 140;
export const REWIND_END = 158;

// Frame on which each step (1..28) begins.
export const STEP_FRAMES: number[] = [
  262, 289, 316, // 1-3
  400, 435, // 4-5
  486, 500, 514, 528, // 6-9
  660, 676, // 10-11
  766, 782, // 12-13
  890, 904, 918, // 14-16
  1018, 1026, 1034, 1042, 1050, 1058, 1066, // 17-23
  1180, 1188, 1196, 1204, 1212, // 24-28
];

export const END_START = 1305;

// Narration line i (public/vo/lXX.mp3) starts at VO_STARTS[i].
export const VO_STARTS = [3, 160, 262, 400, 500, 668, 772, 898, 1062, 1182, 1310];

// Captions [start, end, text]
export const CAPTIONS: [number, number, string][] = [
  [160, 250, "시작은 평범한 170cm"],
  [262, 390, "한 걸음, 두 걸음, 세 걸음이면 벌써 4층 건물"],
  [400, 485, "다섯 걸음이면 아파트보다 커지고"],
  [500, 655, "아홉 걸음 만에 870m, 롯데월드타워가 허리 아래"],
  [668, 760, "열한 걸음, 백두산을 넘어섭니다"],
  [772, 886, "열세 걸음, 비행기가 가슴 높이로"],
  [898, 1008, "열여섯 걸음, 머리가 우주에 닿았습니다"],
  [1062, 1172, "스물세 걸음, 이제 지구보다 커졌어요"],
  [1182, 1295, "스물여덟 걸음, 달을 지나쳤습니다"],
];
