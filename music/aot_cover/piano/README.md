# Guren no Yumiya: solo piano (test, cover 0:00–0:30 = original 0:21 onward)

- `piano_arrange.py` writes `guren_piano_0-30.mid`, a two-hand arrangement made from our own transcription (`../midi/guren_from_0m21_full.mid`). No third-party piano MIDI was used.
  - RH: the chant/riff melody in octaves, the verse melody an octave up with a chord tone below on the beats, and chord stabs on harmony changes.
  - LH: driving octave 8ths on the guitar accents (intro/riff) and rolling broken-chord 8ths in the verse. LH notes are chord tones only.
  - Sustain pedal re-pedals on every harmony change; velocity and timing are humanized.
- `piano_preview.py` renders the MIDI through sfizz + the Salamander Grand Piano V3, adds a light Valhalla Supermassive hall and gentle compression, and runs loudnorm to -14 LUFS / -1 dBTP.
- `sfizz_host.py` loads an SFZ into the sfizz VST3 headlessly.
- `arrange.py` and `jb64.py` are shared helpers.

Run: `python piano_arrange.py guren_piano_0-30.mid && python piano_preview.py guren_piano_0-30.mid piano_test_intro_v1`
