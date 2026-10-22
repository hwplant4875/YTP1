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
