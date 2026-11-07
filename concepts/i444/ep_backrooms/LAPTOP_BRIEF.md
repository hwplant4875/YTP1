# Horror Ranked Backrooms special: laptop brief (11/7 KST)

The owner approved script v1 on 11/7 at 18:23 KST with one cold-open edit and "뭐 이후에는 알아서 잘 편집해서 가자" (produce the
episode). This laptop session owns only the Backrooms edit. Do the phases in order, push after each phase, then report. Do not start other tasks.

**Done in the cloud:** script_v1.md (owner-approved), clip_sources.txt, qa/fetch_clips.py, qa/sheet.py, qa/strip.py, the voice
(voice/, Adam, whisper-checked, 9:26), and now the edit tooling: shot_plan.md, shots.py (skeleton), build_edl.py, render_br.py,
gfx_br.py (overlays), music/make_bed.py, make_srt.py, make_kit.py, qa/find_line.py, qa/spans.py, qa/caption_coverage.py,
qa/gaps.py, qa/coldopen.py, qa/phrase.py. Phase A is done (qa/clips_report.txt, e51cd94). `git pull` before each phase.

**Laptop paths.**
- First list `E:\YTP2` and find the Horror Ranked channel folder. The owner is adding number prefixes to channel folders
  (11/7), so use the folder's current name, e.g. `E:\YTP2\<n>_Horror Ranked`. Call it HR below.
- Episode folder: `HR\EP08 Backrooms` with `1_work\clips`, `1_work\music`, `2_renders`, `3_upload`. Create them if missing.
- Repo: the laptop clone `C:\Users\hw549\Downloads\YTP1`, folder `concepts\i444\ep_backrooms`, branch `claude/project-thread-u0vu84`.

**Standing rules from the owner:**
- On E:, touch nothing outside `E:\YTP2`. Never move or delete existing files in `C:\Users\hw549\Downloads\YTP1`; only the repo
  folder `concepts\i444\ep_backrooms` changes.
- Say in one line what you are about to run before running it.
- Video sources at least 720p, ideally 1080p. HDR uploads must be re-fetched as SDR (fetch_clips.py does it).
- No trailer graphics, title cards, logos or channel bugs inside a used span. Never blur or delogo a bug; pick another moment or clip.
- No DRM rips, no full films, no watermark removal.
- Gore is fine, but never the most extreme frame (cut on the hit or the reaction). No nudity. Kat's head in the fridge is never shown.
- Never commit film video or audio, frames, posters or downloaded images or music. Text, json and our own overlay PNGs are fine.
- Nothing gets uploaded to YouTube. The owner uploads himself.

## Phase A: clips (start here)

1. `git pull origin claude/project-thread-u0vu84` in the laptop clone.
2. `python qa\fetch_clips.py "HR\EP08 Backrooms\1_work\clips"` (4 downloads at a time, `-S res:1080`, SDR re-fetch for HDR).
3. It writes `qa\clips_report.txt`: name, height, fps, duration, SDR/HDR, status. Flag anything under 720p, any failed download and
   any clip that does not hold what its line in clip_sources.txt says (look at a contact sheet: `python qa\sheet.py <clip> <out> 4`).
   Note burned-in logos or channel bugs per clip (where and when) in the report.
4. **The one check that matters before voicing the outro:** on `op_joblo_1990` (and op_fan_a/b if needed), find the giant that
   chases Naren (about 4:30 to 5:25). Write in `qa\clips_report.txt` what the figure looks like on the clearest frames
   (tall, pirate hat, peg leg, coat, or only a shadow). The outro says "the only giant it ever shows you is Captain Clark".
5. Also note in the report: Kat's exact words behind the window (`s3_joblo_pullup` 5:21-6:20), and which still life runs off just
   before Captain Clark walks into the dining room (`s7_dinner_full` / `s7_joblo_reveal`).
6. Commit and push qa\clips_report.txt (text only), then report in a few lines.

## Phase B: shots (after Phase A, 11/7 evening)

Read shot_plan.md first. HR = `E:\YTP2\Horror Ranked` (no number prefix yet; re-check `E:\YTP2` in case the owner renamed it).
CLIPS = `HR\EP08 Backrooms\1_work\clips`.
1. `git pull origin claude/project-thread-u0vu84`.
2. Film lines first: for each of the seven lines in shot_plan.md run `python qa\find_line.py "<CLIPS>\<clip>.mp4" <t0> <t1> "<words>"`,
   check the frames (`python qa\strip.py` / `qa\sheet.py`), then set the insert's in-point, its length and `sub` (the words exactly as
   spoken) in shots.py. Speaker on screen, no talk-over, no swearing inside the span.
3. Fill every `TODO` in shots.py (in-point and `-clean` span) from contact sheets (`python qa\sheet.py <clip> <out> 2` for a frame every
   2 s, then 0.5 s sheets around the moment). Keep each comment true to what is on screen; swap clips or add cuts on exact script
   phrases (`python qa\phrase.py sNN` lists the words) when it makes the picture match the sentence better.
4. `python build_edl.py` (no TODO, no WARN), `python qa\caption_coverage.py` (OK, a cut on every caption), `python qa\gaps.py` (OK),
   then `python qa\spans.py "<CLIPS>" <out.jpg> sNN` for every section and look at every row. Fix and repeat until every row is right.
   Dark shots go in shots_grade.py (DARK / VDARK lists, gamma 1.25 / 1.4), as in EP04.
5. Commit and push shots.py, shots_grade.py and edl.json (text only, never frames or sheets), then report in a few lines: shot count,
   the seven film lines as heard (words + clip + time), anything that had no good source.

## Phase C: render, QA, kit (right after Phase B; say in one line what runs before running it)
1. Music: `python music\make_bed.py "HR\EP08 Backrooms\1_work\music" "HR\EP08 Backrooms\1_work\music\backrooms_bed_v1.mp3"`
   (downloads three Mixkit tracks; never commit them).
2. Render 1080p30: `set LEAN=1` then `python render_br.py edl.json "<CLIPS>" voice "HR\EP08 Backrooms\1_work\music\backrooms_bed_v1.mp3"
   "HR\EP08 Backrooms\2_renders\backrooms_v1.mp4" 30`. A single section can be re-rendered with `ONLY=s05` for checks, and a full
   render after a fix can keep untouched sections with `REUSE=s00,s01,...`.
3. QA on the render (look at the images yourself):
   - `python qa\coldopen.py "<render>" <out_prefix> 10 15.8`: frame 0 is Captain Clark with FIVE PEOPLE on screen, every caption sits
     on its own cut and on its word, every shot literally shows its word.
   - One frame from the middle of every shot of every section, plus frames at 15% and 85% of each film line: no end card, no text,
     no logo, no gore beyond the rule, Kat's head never, overlays readable (corner number, place names, choice, subtitles, dates,
     1 OF 5), the corner never missing or doubled at a section join, nothing covering a face that matters.
   - Audio: integrated about -14 to -15 LUFS, true peak under -1 dBTP; the film lines clear and not louder than the narration; the
     music quiet under the voice and nearly gone in the near-silence before Captain Clark; no clicks at the insert cuts.
4. Independent review: give a fresh subagent the render's frames (cold open at 10 fps, one per shot) and make_srt's transcript, with
   the owner's rules (frame 0 cover, every cold-open word captioned, a new shot every 2-3 s that matches the sentence, no trailer
   graphics or logos, HD only, gore and Kat rules, no silence over 1.5 s, quiet music, no boxes or pills), and fix what it finds once.
5. Kit: `python make_srt.py edl.json voice "HR\EP08 Backrooms\3_upload\backrooms_survival_en.srt"` and
   `python make_kit.py edl.json "HR\EP08 Backrooms\3_upload\backrooms_kit.md"`; also copy both into the repo's `upload\` folder.
6. Commit and push the text outputs (edl.json, upload\*.srt, upload\*.md, QA notes as text), then report: render path, length,
   loudness, what the QA and the review found and fixed. The owner reviews and uploads himself. Nothing is uploaded anywhere.
