# EP1 deliverables for the DaVinci Resolve edit

Files on the laptop: `C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\deliver\` (the big ones are not in git).

| File | What | Size |
|---|---|---|
| ep01_music_only.wav | suite v2, 29:24, 48 kHz 24-bit, about -17 LUFS | 508 MB |
| ep01_music_plus_fire.wav | same + fireplace bed 15 LU under (looped, 3 s equal-power crossfades) | 508 MB |
| ep01_music_plus_fire_preview.mp3 | 320k preview of the fire version | 71 MB |
| ep01_spectrum_overlay_black.mp4 | 1920x1080, 30 fps, H.264 CRF 16, pure black + warm off-white (246,238,224) spectrum at 100 %, no audio; use Screen/Add and set opacity (35 % = Blender look) | 17 MB |
| ep01_watermark_you_elsewhere.png | 1920x1080 transparent, Allura 60 px, 64 px margins, 80 % + soft shadow (in git) | 32 KB |
| dust_overlay_60s_* | dust motes only, seamless 60 s loop on black (+ ProRes 4444 alpha) | see report |

The spectrum is driven by the music only (not the fire), with the same analysis as Blender v3: 64 mirrored sharp spikes, 40 Hz-1.5 kHz, 50/180 ms.
It sits right of the watermark, exactly as in the v3 preview. No opening fade is baked into anything.

## Suite v2 track list (4 s crossfades)
| Start | Track | Length |
|---|---|---|
| 00:00 | 01 Hedwig's Theme, trio (hedwig_trio_sfz_v1, 88 BPM) | 2:02 |
| 01:58 | 02 Common Room Waltz (original, D minor, 92) | 2:42 |
| 04:36 | 03 Lake Window, medium swing (original, F, 96) | 2:45 |
| 07:18 | 04 Green Scarf (original, G minor waltz, 94) | 2:38 |
| 09:53 | 05 Fireside Letters, medium swing (original, A minor, 90) | 3:07 |
| 12:56 | 06 Hedwig's Theme in G minor (90) | 2:46 |
| 15:38 | 07 Rain on the Glass, medium swing (original, C minor, 94) | 2:49 |
| 18:23 | 08 Common Room Waltz in E minor (88) | 2:49 |
| 21:09 | 09 Lake Window in G (92) | 2:52 |
| 23:58 | 10 Green Scarf in A minor (96) | 2:35 |
| 26:29 | 11 Hedwig's Theme, reprise (86) | 2:54 |

All tracks use the v1 trio sound: Salamander piano, FL acoustic bass, FL HQ Jazz Kit ride and pedal hat, and the same EQ and Chamber Warm reverb.
