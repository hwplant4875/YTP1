# EP04 Freddy ambience bed v1 (11/7 KST)

- File: freddy_bed_v1.mp3, 8:35, stereo (original stereo kept, no centring), 256 kbps, about -16.6 LUFS integrated, LRA 1.9 LU.
- Generated with ElevenLabs Music (model music_v2_5, JC key) by make_bed.py: a dark nightmare lullaby, a very sparse, slightly
  detuned music box (a few scattered notes, never a full tune), low cello and double bass drones, a soft boiler-room hum, faint steam
  hiss, a dark string pad. Negative: drums, percussion, hits, stingers, risers, choir, vocals, harsh drones, ticking, metallic clanks.
- Takes: A (freddy_bed_a.json) and C (freddy_bed_c.json, "never a steady pulse"). Take B was dropped because its music box notes
  fell on every beat (1.0 s apart, like ticking). Joined A -> C -> A with 10 s equal-power crossfades, each take levelled to -16 LUFS
  first, then high-pass 30 Hz, low shelf -2 dB at 110 Hz, high shelf -4 dB at 3 kHz (same chain as EP07).
- QA: music box onsets are pitched notes (580-1310 Hz, D minor), never hard-panned (within 4 dB L/R on A); 5 s RMS stays between
  -21 and -18 dB over the whole bed (no swells, no silences).
- Mix: the renderer levels it to -39 LUFS (render_fk.py default MUSIC_LUFS=-39) under the narration and loops it if needed.
