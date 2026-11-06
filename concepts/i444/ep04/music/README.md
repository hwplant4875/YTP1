# EP04 Freddy music bed

## v2 (11/7 KST, use this one)

The owner's 11/7 rule for every channel: never generate or assemble BGM ourselves; download fitting ready-made free tracks
(Mixkit). So v1 below (ElevenLabs Music) is replaced by real Mixkit tracks, built by make_bed_v2.py on the laptop (the mp3s are
third-party music and are never committed):
- Piano Horror (671, Francisco Alvear) 0-108 s, then Echoes (188, Andrew Ev) 38-214 s, then Xanthos (633, Eugenio Mininni) 0-200 s.
  Mixkit Stock Music Free License (free for YouTube videos, no attribution needed).
- Picked from Mixkit's horror, creepy and scary pages (90 tracks) for no drums (percussive share under 8%), no steady pulse or
  ticking (onset periodicity 0.24-0.42; Selpan was dropped for regular clicks, Fallen for a steady pulse, Tapis for out-of-phase
  stereo, Fragments of Bangkok for mono), dark tone (spectral centroid 490-680 Hz), real stereo (L/R correlation 0.16-0.56).
- Each segment is cut before its own fade-out (so the joins never dip), levelled to -16 LUFS, joined with 8 s equal-power
  crossfades, then high-pass 30 Hz, low shelf -2 dB at 110 Hz, high shelf -4 dB at 3 kHz, 1.5 s fade in, 8 s fade out.
- Result 7:48 (468 s), -16.6 LUFS, LRA 9.4, stereo correlation 0.26; 5 s RMS mostly -17 to -24 dB. The renderer levels it to -39 LUFS.

## v1 (11/7 KST, replaced by v2)


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
