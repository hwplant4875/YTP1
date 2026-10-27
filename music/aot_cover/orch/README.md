# Guren no Yumiya: orchestral cover (BBC SO Discover)

The source is `../midi/guren_from_0m21_full.mid`. Cover t=0 is 0:21 in the original, at 180.676 BPM.

- `arrange.py` rearranges the rock-band MIDI into orchestral parts and renders each stem through Spitfire BBC Symphony Orchestra Discover (VST3, hosted by Spotify pedalboard).
  - The choir uses the VPO mixed-choir SFZ samples, played by a small built-in player.
  - `SEG=intro` renders cover 0–30 s; `SEG=chorus` renders 46.8–68 s.
- `bbc.py` loads a chosen BBC instrument and articulation headlessly. It does this by injecting the NKS preset XML into the plugin's VST3 state.
- `jb64.py` is the JUCE base64 codec used for that plugin state.
- `mix.py` balances the stems, adds a Valhalla Supermassive hall send, applies glue compression and limiting, then two-pass loudnorm to -14 LUFS / -1 dBTP. It writes WAV and MP3 (320k).

Run: `SEG=intro python arrange.py && SEG=intro python mix.py <out_basename>`

`orch_test_intro_v1.mp3` is the first test: cover 0:00–0:30.
