# Music tools on the laptop (MainLaptop)

Everything here is free and needs no login or licence key. All of it comes from the official source.
Installed 2026-10-22. Music is made by script renders (sfizz_render + SFZ libraries + ffmpeg), not FL Studio's GUI.

## Renderer
| Tool | Version | Path | Source |
|---|---|---|---|
| sfizz (VST3 for FL) | 1.2.3 | `C:\Program Files\Common Files\VST3\sfizz.vst3` | github.com/sfztools/sfizz-ui releases |
| sfizz_render (CLI: MIDI + SFZ -> WAV) | 1.2.3 | `C:\Users\hw549\Downloads\YTP1\_downloads\sfizz\x\bin\Release\sfizz_render.exe` | github.com/sfztools/sfizz releases |
| ffmpeg | N-126374 | on PATH (WinGet) | mixing, EQ, convolution reverb (`afir`) |

## VST3 plugins (`C:\Program Files\Common Files\VST3\`)
| Plugin | Version | Use | Source |
|---|---|---|---|
| Surge XT | 1.3.4 | big hybrid synth: pads, city-pop leads, Halloween/Christmas textures | surge-synthesizer.github.io |
| Dexed | 1.0.1 | DX7 FM: city-pop e-piano, bells, celesta-like FM | asb2m10.github.io/dexed |
| TAL-NoiseMaker | current | analog-style synth: bass, leads, pads | tal-software.com |
| TAL-Reverb-4 | current | vintage plate-style reverb | tal-software.com |
| TAL-Chorus-LX | current | Juno-60 chorus for city pop | tal-software.com |
| Valhalla Supermassive | 5.0.0 | huge reverbs and echoes | valhalladsp.com |
Skipped: Kilohearts Essentials (needs an account), Spitfire LABS (needs an account).

## SFZ sample libraries (`C:\Users\hw549\Downloads\YTP1\_samples\`)
| Library | Main SFZ | Use |
|---|---|---|
| Salamander Grand Piano V3 (2020-06-02) | `SalamanderGrandPiano-SFZ+FLAC-V3+20200602\SalamanderGrandPiano-V3+20200602.sfz` | acoustic grand (Yamaha C5), 16 velocity layers |
| dsmolken Double Bass (Rubner) | `dsmolken.double-bass-master\d_smolken_rubner_bass_pizz.sfz` (also arco, switched) | real upright bass for jazz |
| Karoryfer Swirly Drums | `karoryfer.swirly-drums-main\Programs\Full_kit.sfz` (+ per-bus programs) | jazz kit with snare stir/flutter, ride, hats |
| Greg Sullivan E-Pianos | `GregSullivan.E-Pianos-master\Wurlitzer EP200\`, `CP80\`, `Pianet T\` | Wurlitzer, CP80 and Pianet for city pop and lo-fi |
| jRhodes3c | `jlearman.jRhodes3c-master\jRhodes3c-looped-flac-sfz\_jRhodes-stereo-looped.sfz` | Rhodes Mk I |
| VSCO 2 Community Edition 1.1.0 (CC0) | `VSCO-2-CE-master\*.sfz` (75 programs: strings, harp, celesta, glockenspiel, winds, brass, percussion) | orchestral colours for Christmas and Halloween |
| Virtual Playing Orchestra 3.2 waves + 3.3 standard scripts | `VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\{Strings,Brass,Woodwinds,Percussion,...}\*.sfz` | full orchestra sections and solos |

## Also on disk
- FL Studio 2026 (26.1.4): `C:\All The Programs\FL Studio\FL64.exe`. Its bundled samples are Ogg-in-WAV; `you_elsewhere/ep01_malfoid/music_fl/out/sfz_draft/convert_fl_samples.py` decodes them to FLAC.
- FL impulse responses (for `afir` reverb): `C:\All The Programs\FL Studio\Data\Patches\Impulses\` (for example `Reverb Devices\IMP Evnt - Chamber Warm.wv`, `Hall Warm.wv`).
- After Effects: `C:\All The Programs\AE`.
