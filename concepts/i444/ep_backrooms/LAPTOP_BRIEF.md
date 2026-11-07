# Horror Ranked Backrooms special: laptop brief (11/7 KST)

The owner approved script v1 on 11/7 at 18:23 KST with one cold-open edit and "뭐 이후에는 알아서 잘 편집해서 가자" (produce the
episode). This laptop session owns only the Backrooms edit. Do the phases in order, push after each phase, then report. Do not start other tasks.

**Done in the cloud:** script_v1.md (owner-approved), clip_sources.txt (43 clips, all HD and not age-restricted per the Data API),
qa/fetch_clips.py, qa/sheet.py, qa/strip.py. Voice, shot plan, EDL builder and renderer come next from the cloud (Phase B and C below
are added to this file; `git pull` before each phase).

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
