EP03 "Every Ghostface Ranked" - stat card / tier board sound effects
=====================================================================

All four files were generated for this channel with the ElevenLabs
sound-generation API (POST /v1/sound-generation, prompt_influence 0.5) on
2026-10-26. They are our own generated audio, not film audio.

Format: 48 kHz, stereo, 16-bit PCM WAV. Peak normalised to -1.0 dBFS
(true peak also -1.0 dBTP). Left/right levels balanced so nothing leans to
one side; all are mono-compatible (fold-down loss 0.5 dB or less).

Processing on the chosen take: 25 Hz high-pass + DC removal, leading
silence trim (none was present), 1 ms fade-in (the takes start on a
non-zero sample), cut to length with a raised-cosine fade-out, L/R
balance, peak normalise.

Two takes were generated per sound; the pick was made by measuring peak,
RMS, duration, spectral centroid, noise floor and L/R correlation.

whoosh.wav  (0.55 s)  card or board sliding in
  duration_seconds 0.8
  prompt: "A single quick dark cinematic whoosh, soft airy swish passing by,
  smooth and low, a card sliding into frame, clean, no ticking, no drone,
  no music"
  pick: take A. Swells to a peak at 0.19 s and then fades, dark and low
  (centroid about 150 Hz). Take B was rejected because it was wide and
  partly out of phase (L/R correlation 0.39, 1.6 dB loss in mono).

slam.wav  (0.65 s)  face tile slamming into a tier row
  duration_seconds 1.0
  prompt: "One deep punchy cinematic impact thud, a heavy tile slamming down
  onto a board, soft low boom with a short dark tail, warm not harsh, no
  metal clang, no music"
  pick: take B. Immediate attack, clean tail (noise floor -76 dB vs
  -66 dB), centred. Take A had a second bump in the tail at about 0.5 s.

fill.wav  (0.45 s)  stat bars filling
  duration_seconds 0.7
  prompt: "A subtle soft rising swoosh blip, a short smooth upward whoosh
  like a progress bar filling, gentle and clean user interface sound,
  quiet, no beeps, no music"
  pick: take A. Pitch rises smoothly (about 1 kHz up to 10 kHz) as it
  fades out. Take B was rejected: brighter and hissier (47% of energy
  above 6 kHz) and it cut off abruptly at 0.23 s.

stamp.wav  (0.55 s)  survival percentage landing
  duration_seconds 0.9
  prompt: "One heavy cinematic stamp hit, a big rubber stamp pressed down
  hard on a desk, deep solid thump with a soft low boom, punchy but not
  harsh, no music"
  pick: take B. Deep and solid (centroid about 210 Hz), centred, decays
  over about 0.4 s. Take A was rejected: it sat 3 dB to the left, its
  sample peak was already at -0.1 dBFS, and its tail ended at 0.28 s.

Cost: 8 generations, 76 credits in total.
