# OoT remake playlist (Player's Playlist EP02) - render spec

Work dir on laptop: E:\YTP2\Game OST Playlist\EP02_OoT_Remake_Playlist (create). Sources: E:\YTP2\Game OST Playlist\Zelda Ocarina of Time\remake_full\remake_full.webm (audio), ...\trailers\*.mp4 (4K official Nintendo trailers, video only). Never touch other E: folders.

## Audio
- tracks.json lists 29 tracks in final order. start/end are seconds in remake_full.webm. source "extra" = download audio of that YouTube id (yt-dlp -f 251) into work\extra\KEY.webm and use the whole file (trim leading/trailing silence).
- Cap each track at max_len seconds (300): if longer, end it at a low-energy phrase boundary before max_len with a 4 s fade-out.
- Joins: 2.5 s equal-power crossfade between tracks. Trim silence at track edges first. No gaps, no clicks.
- Loudness: each track to -16 LUFS integrated, true peak ceiling -1.5 dBTP with a gentle limiter. Keep STEREO, 48 kHz.
- Final audio AAC 384k with -aac_tns 0 -aac_pns 0.

## Visuals (1920x1080, 30 fps, H.264 CRF 18)
- Per track show official trailer footage of THAT place (Gerudo Valley/Fortress, Lost Woods, Great Fairy fountain, Kokiri village, Hyrule Field, Lon Lon Ranch, windmill, Kakariko, castle town market, Zelda courtyard, Temple of Time, Zora's Domain, Goron City, Kaepora the owl, potion shop, Deku Tree, temples, Ganon's castle/tower, Ganon fight, ending skies). Pick by viewing frames. If a place is not in any trailer, use the closest mood shot. Never reuse the same shot twice in the whole video.
- Only clean cinematic shots: no on-screen text, logos, ratings, dates, menus or HUD, no hard cut inside a used shot. Prefer slow camera moves and wide scenery; fast action only in battle tracks.
- Play shots at 0.5x speed (60 fps source to smooth 30 fps), each shot 6-12 s, 1.5 s cross dissolves; loop a track's 2-4 shots (ping-pong allowed) to fill the track.
- Look: very light grade (slight warmth, soft 15% vignette). No particles, boxes or bars.
- Title: bottom-left, 64 px from left and bottom edges, font Cinzel (OFL, google/fonts repo ofl/cinzel), white, size 46, thin dark shadow, no box; fades in 1 s after track start, stays 8 s, fades out 1 s. Above it "Now Playing", Cinzel 24, 80% white.
- Visual change between tracks: 1.0 s crossfade aligned to the audio crossfade.
