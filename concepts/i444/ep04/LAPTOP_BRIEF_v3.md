# EP04 Freddy v3: laptop brief (11/7 KST)

The owner approved script v3 on 11/7 at 01:35 KST ("좋다. 진행.") and wants the full episode produced. This laptop session owns only the
EP04 Freddy edit below. Do these phases in order, push after each phase, then stop and report. Do not start other tasks.

**Already done in the cloud:**
- Voice: voice/, Adam, one full take per section, whisper QA in voice/verify_v3.txt.
- Music bed v2 (11/7 owner rule: real free tracks, never generated music): music/make_bed_v2.py downloads three Mixkit tracks and builds
  `1_work\music\freddy_bed_v2.mp3` on the laptop (never commit it). Do not use music/freddy_bed_v1.mp3 (ElevenLabs Music).
- Clip list: clip_sources_v3.txt, 140 clips, all HD and none age-restricted (checked with the Data API).
- Shot plan: shot_plan_v3.md.
- shots_v3.py skeleton, generated from that plan.
- build_edl_v3.py, the renderer (render_fk.py), srt, kit, poster wall and tile scripts, qa/.
- Thumbnails are made in the cloud. Do not make them here.

**Laptop paths.** All three live under the episode folder `E:\YTP2\Horror Ranked\EP04 Freddy Krueger`:
- `1_work` for clips, posters and scratch.
- `2_renders` for the final render only.
- `3_upload` for the srt and the kit.
The repo is the laptop clone in `C:\Users\hw549\Downloads\YTP1`, folder `concepts\i444\ep04`, branch `claude/project-thread-u0vu84`.

**Standing rules from the owner:**
- On E:, touch nothing outside `E:\YTP2`.
- Never move or delete existing files in `C:\Users\hw549\Downloads\YTP1`. Only the repo folder concepts\i444\ep04 changes.
- Video sources must be at least 720p, ideally 1080p.
- No trailer graphics, title cards, logos or channel bugs inside a used span.
- The only approved cover is the renderer's black bottom bar (the Movieclips mark). Never blur or delogo a bug. Pick another moment or clip instead.
- No DRM rips, no full films, no watermark removal.
- Gore is fine, but never the most extreme frame (cut on the hit or the reaction). No nudity.
- Never commit film video or audio, posters or downloaded images. Text, json, our own tiles PNGs and the srt are fine.
- Nothing gets uploaded to YouTube. The owner uploads himself.

## Phase A: clips (start here)

1. `git pull origin claude/project-thread-u0vu84` in the laptop clone.
2. Find the 7 clips from 10/27 inside `E:\YTP2` only:
   - The clips are n2_bus, n2_kill_for_me, n3_wizard, n5_baby, n5_back_to_hell, n5_force_feed and r10_bath.
   - They were in the old Instruction444 clips\ep04 folder before the 10/31 tidy-up.
   - Copy (do not move) them into `1_work\clips` if they are not there yet.
3. Download every line of `clip_sources_v3.txt` to `1_work\clips\<name>.mp4`, skipping files that already exist:
   `yt-dlp -S res:1080 -f "bv*+ba/b" --merge-output-format mp4 -o "<clips folder>\<name>.%(ext)s" https://www.youtube.com/watch?v=<id>`
   - Always pass the -S res:1080 selector (11/4: an RC run defaulted to 720p).
   - If ffprobe shows an HDR transfer (smpte2084 or arib-std-b67), re-download that clip's SDR format from `yt-dlp -F`. The washed-out HDR colours were an EP07 lesson.
4. Write `qa/clips_report_v3.txt` with one line per clip: name, height, fps, duration, SDR or HDR, OK or the problem.
   - Flag anything under 720p, any failed download, any clip that is not the film its prefix says, and any clip with a burned-in logo or a "Rotten Tomatoes" or "ClipZone" bug.
   - Commit and push it.

## Phase B: verified beats and the shot list

5. Work through shot_plan_v3.md section by section. For each line, find the moment on real frames.
   - Use `python qa/sheet.py <clip> <out> 1` contact sheets, then 10 fps strips around the in-point (`qa/strip.py`).
   - Write the verified spans per clip into `beats_v3.md`, like ../ep07_pinhead/beats_v7.md.
   - When a planned beat is not in the candidates, search the other clips of the same film first.
   - If it is still missing, use the closest true moment and list the change at the top of beats_v3.md.
   - Never show another film's Freddy than the one the line is about.
6. Fill shots_v3.py: replace every TODO pair with the verified in-point and the negative clean span, in the EP07 shots_v8.py format.
   - Keep each comment true to what is on screen.
   - Add cuts where a shot would run past about 3 s, anchored to exact script phrases. build_edl_v3.py raises KeyError for a phrase that is not in voice/words.json.
   - Keep the stat-card shots (L) with the subject left or centre.
   - Never use the same moment twice.
7. Tiles:
   - Fill T in make_tiles_fk.py with one clear, bright Freddy face per film, for keys n1 n2 n3 n4 n5 n6 n7 fj r10.
   - Run it to get tiles/<key>.png at 400x400.
8. Poster wall:
   - Download the 9 official theatrical posters from TMDB (release posters only, never fan art) to `1_work\posters\<key>_poster.jpg`.
   - Use the same keys as the tiles, in release order 1984 to 2010.
   - Run `python make_posterwall_fk.py "<posters folder>" "<clips folder>\still_posterwall.mp4"`.
9. Build and check:
   - `python build_edl_v3.py` writes edl.json. Read its WARN lines.
   - `python qa/caption_coverage.py` must end with "caption coverage OK".
   - Push shots_v3.py, beats_v3.md, the tiles and edl.json.

## Phase C: render, QA, kit

10. Build the music bed, then render 1080p30:
    `python music\make_bed_v2.py "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\music" "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\music\freddy_bed_v2.mp3"`
    `set LEAN=1` then `python render_fk.py edl.json "<clips folder>" voice "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\music\freddy_bed_v2.mp3" "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\2_renders\ep04_freddy_v3.mp4"`
    - MUSIC_LUFS stays at the default -39.
    - The renderer imports ../ep01/gfx.py and ../ep03/anim.py and uses ../ep03/sfx.
11. One careful QA pass before reporting:
    - **Shots and the open:**
      - One frame per shot (qa/shots.py) and 8 frames over every used span (qa/spans.py).
      - The cold open at 10 fps against the word onsets. Frame 0 is Freddy plus the caption "HE WILL", and every chunk shows its meaning from its first frame.
    - **Footage:**
      - No trailer or title graphics, logos, black frames or scene cuts inside a span.
      - All sources at least 720p.
    - **Overlays:**
      - The stat card says FREDDY KRUEGER with STRENGTH, INTELLIGENCE, KILL COUNT and DREAM POWER, and the % and tier match stats.json: 95 Easy, 65 Don't Worry, 55 Close Call, 45 Better Run, 38 and 30 Almost Dead, 22, 12 and 5 Slaughtered.
      - Film labels are right.
    - **Audio:**
      - No silence over 1.5 s.
      - Narration clearly on top of the music.
    - Fix what you find, re-render only the sections that changed (ONLY=s05,s09 and so on, then the full join), and check again.
12. Kit:
    - `python make_srt.py` writes upload\freddy_ranked_en_v3.srt.
    - `python make_kit_v3.py` writes upload\upload_kit_v3.md.
    - Copy both into `3_upload`.
    - Push everything except video and audio.
13. Report back in a few lines:
    - The render path and its length.
    - QA results.
    - Every beat you replaced and why.
    - Anything you could not solve, such as a missing must-have moment.
