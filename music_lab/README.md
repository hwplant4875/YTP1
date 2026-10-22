# music_lab — "slowed + reverb" phonk made by script

Goal: original workout / everyday-listening tracks in the style of LONOWN "worry (Slowed)" and akiaura "Sleepwalker (Slowed)".
Everything is rendered by Python scripts: no DAW GUI.

## What the references are (measured from the audio)
| | worry (Slowed) — LONOWN, riserayss | Sleepwalker (Slowed) — akiaura, LONOWN, STM |
|---|---|---|
| Tempo (slowed) | ~117 BPM | ~99 BPM |
| Key (slowed) | A major / C# minor colour (D – C#m – A loop) | C minor (G – A# – C motif, 2-bar loop) |
| Low end | 33% of energy below 60 Hz | 48% below 60 Hz: huge distorted 808 with glides |
| Feel | dreamy, bright chords, vocal | dark, hypnotic loop, vocal |
| Loudness | -9.1 LUFS | -6.7 LUFS |

`refs/` holds the two reference WAVs for analysis only (not for reuse or upload).

## How a track is built
- `src/engine.py`: numpy synths (808 with glide + saturation, kick, clap, snare, hats, cowbell, supersaw pad, pluck, FM bell, formant "ooh" voice) and `sfz_render()` for sampled instruments through `sfizz_render` (Rhodes, Salamander grand, VPO strings).
- `src/track01.py`: arrangement + mix. Written at 125 BPM in E minor, then **slowed ×0.8 by resampling** (100 BPM, pitch ~-3.9 st, lands in C minor like Sleepwalker), and the reverb (Valhalla Supermassive) is added **after** slowing, like real "slowed + reverb" edits.
- `src/mastering.py`: 4x-oversampled limiter + static gain to -9.5 LUFS, true peak -1.2 dBFS.
- VST3 plugins load in `pedalboard` via the inner binary path, e.g. `C:/Program Files/Common Files/VST3/TAL-Chorus-LX.vst3/Contents/x86_64-win/TAL-Chorus-LX.vst3` (the bundle folder path fails). Valhalla Supermassive loads from the plain `.vst3` path.

Render: `python -I src/track01.py out` (about 1 minute).

## Track 01 v1 (2:28)
Intro (sad piano + "ooh" voices + vinyl) → build (arp, hats, riser) → drop A (808 + bell melody + Rhodes stabs) → break (piano, strings, held 808) → drop B (adds pluck double, cowbell riff, strings) → outro.
