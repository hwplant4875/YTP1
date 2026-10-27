# EP03 background music (ElevenLabs Music, generated 2026-10-26 on the channel's paid ElevenLabs plan)

- `eleven_ghostface_bed.mp3`: raw output, 150 s, model music_v2_5, force_instrumental. Prompt in `eleven_ghostface_bed.json`.
  It builds from about -29 to -21 dB RMS over the first 80 s and fades out at ~145 s.
- `eleven_ghostface_bed_loop.mp3`: 132 s seamless loop for render_v2.py (`-stream_loop`). Levelled with
  `dynaudnorm=f=3000:g=9:p=0.5:m=4`, cut 8..140 s, the last 5 s equal-power crossfaded into the 5 s before 8 s.
  QA: -23.9 LUFS integrated (render_v2 brings it to about -27 with the high-shelf), L/R correlation 0.23 (kept stereo),
  almost nothing above 3 kHz (0.02 %), no silence inside the loop. Low strings pulse about every 0.4 s, 13 dB under the mids.
Owner rules (10/26 15:19): free copyright-safe horror music or ElevenLabs only, no added hits ("dum dum") on the music.

- `eleven_ghostface_bed2.mp3` (10/27, shorts-factory key, owner's choice): same prompt family, "slightly more urgent, menacing", 150 s.
  Bass-heavier than bed 1 (low/mid +5 dB raw). `eleven_ghostface_bed2_loop.mp3`: low-shelf -6 dB at 150 Hz, same levelling and
  8..140 s loop with a 5 s equal-power crossfade; -23.5 LUFS, low/mid +2.2 dB (bed 1 loop: -4.8 dB). Meant for #4 to #1 and the outro.

- `eleven_musicbox_ambience.mp3` (10/27, shorts-factory key, owner's request "오르골 공포 앰비언스, 잔잔하게"): slow detuned music box
  over soft low strings, 60 BPM A minor, 150 s (quiet first 35 s and last 35 s). `eleven_musicbox_ambience_loop.mp3`: same levelling,
  8..140 s loop with a 5 s equal-power crossfade.
