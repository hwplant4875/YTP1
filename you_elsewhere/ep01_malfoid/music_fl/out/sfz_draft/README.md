# Hedwig trio, SFZ draft (no FL Studio)

`hedwig_trio_sfz_v1.mp3` was rendered offline because FL Studio could not be driven remotely.

- Piano: Salamander Grand Piano V3 (SFZ+FLAC, freepats) through sfizz 1.2.3 `sfizz_render`.
- Bass: FL Studio's bundled "Acoustic Bass" samples mapped in `bass.sfz` (one sample per major third, E1 to C4).
- Drums: FL Studio "HQ Jazz Kit" ride (51) and pedal hat (44) only, round robin (`brushless_kit.sfz`).
  No brush kit was available, so the snare swirls (note 40) are left out as FL_BRIEF.md allows.
- Mix: `mix.sh` (ffmpeg): warm EQ, highshelf -3 dB at 6 kHz on piano, bass about 6.5 LU and drums about 13 LU
  under the piano, convolution send with FL's "Evnt - Chamber Warm" impulse, -18.9 LUFS, peaks -1.5 dBFS, no limiter.

FL's samples are Ogg Vorbis inside WAV; `convert_fl_samples.py` extracts and decodes them to FLAC locally.
The samples themselves are not committed.

## v2 (`hedwig_trio_sfz_v2.mp3`, 2:32, MIDI v2 at 66 BPM)
- `v2/split_soften.py`: piano velocities compressed to 30-54 so Salamander plays its soft, mellow layers.
- `v2/mix_v2.sh`: piano lowpassed at ~5 kHz with highshelf -2.5 dB, gentle transient taming (2.2:1, 1.5 ms attack),
  warm low-mid lift; FL "Evnt - Hall Warm" impulse (long hall) with 25 ms pre-delay, wet about 5 LU under the dry piano.
  Bass about 7 LU and ride/hat about 14 LU under the piano. -18.3 LUFS, peaks -1.5 dBFS, no limiter.
