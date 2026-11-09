# EP08 The Conjuring Universe: laptop brief v1 (11/9 KST)

The owner said on 11/9 at 21:42 KST "그래 시작. Max 노력으로" (start EP08 Conjuring with maximum effort). This laptop session owns only the
EP08 edit. Do the phases in order, push after each one, then report in a few lines and stop. Say in one line what will run before running it.

**Paths.** List `E:\YTP2` and `E:\YTP2\Horror Ranked` first: the owner is adding number prefixes to folder names. The episode folder is
`<Horror Ranked>\EP08 Conjuring` (written below as `<EP08>`), with `1_work\clips`, `1_work\tiles`, `1_work\posters`, `1_work\music`,
`2_renders` and `3_upload`. The repo is the laptop clone `C:\Users\hw549\Downloads\YTP1`, folder `concepts\i444\ep08_conjuring`, branch
`claude/project-thread-u0vu84`.

**Owner rules that apply here:**
- On E:, touch nothing outside `E:\YTP2`. Never move or delete existing files in `C:\Users\hw549\Downloads\YTP1`.
- Sources at least 720p (ideally 1080p), SDR. No trailer graphics, title cards, logos, channel bugs or burned subtitles inside a used span.
  The only allowed cover is a black bottom bar over a mark at the very bottom (BAR in shots_grade.py). Never blur or delogo.
- **The cold open must sync exactly**: every caption's shot shows that exact action from its first frame (owner 11/7: "초반부에 싱크가
  중요하다니까"). **Never substitute a shot silently**: if no clip shows a line, write GAP and tell the cloud; the owner would rather give
  us the film file than see a stand-in (Backrooms v2 lesson).
- **Real film lines and scene audio**: the owner loved them on Backrooms ("매우 좋아, 앞으로도 더 많이"). Plan about one short film line
  per entry where a clip has a clean, famous one (see Phase B, step 3).
- Gore is fine, but never the most extreme frame (cut on the hit or the reaction). No nudity.
- **Never show a suicide act**: Evelyn (Annabelle 2014), Father Gordon (Last Rites), Jessica's fall (The Devil Made Me Do It), Sister
  Victoria's hanging (The Nun), Bathsheba's hanging, Annabelle Higgins, Janet or Judy at a window or rope. Cut away before.
- Never commit film video, audio, frames, posters, tiles or music. Text, json and the srt are fine. Nothing gets uploaded to YouTube.
- If the owner puts film files in `<EP08>`, index them (and their subtitle tracks) and prefer them for every GAP.

## Phase A2: prep that does not need the voice (now)

Phase A is done (beats_v1.md, 6dfaa02). While the owner decides on the script, the credits and the film files:
1. Thumbnails into the upload folder: `set SD=<EP08>\1_work\tmdb\` and `set OUT=<EP08>\3_upload\`, then `python thumbs_ep08.py`
   (it downloads the 9 official TMDB stills itself and writes conjuring_thumb_a/b/c.jpg plus a sheet). Never commit them.
2. Poster wall: Phase B step 5 below.
3. Tiles: Phase B step 4 below. Suggested frames from beats_v1.md (check each, the face big, sharp and bright): ach = ach_devil_cz 297.5
   (doll in the case) or ach_end 57.7; a14 = a14_basement 122-125 (the ghost at the window) or the a14_baby crib doll; c1 = co_mother_b
   263.5-265.5 (Bathsheba's face); c2 = c2_painting 136.5-138.8 (Valak); lr = lr_exorcism 514.8-515.4 (the mirror demon); cr = cr_wheel
   536-544 (the doll); dm = dm_promise 49.5-53.5 (Isla, crop the logo bars); n2 = n2_exorcise 2.0-3.5 or n2_lucy 19.5-21 (Valak);
   n1 = co_valak0 30.1-31.6 (Valak).
4. Music bed: Phase C step 7 below.
5. Film lines: Phase B step 3 below. Write what you find into beats_v1.md (clip, in, dur, the exact words).
6. If the owner drops film files into `<EP08>`: list them with ffprobe (resolution, length, subtitle tracks), then find every GAP of
   beats_v1.md in them (subtitles help: search the line's words) and add the spans to beats_v1.md.
Push (text only) and report in a few lines.

## Phase B: shot list (after the cloud pushes the voice and the shots.py skeleton)

The cloud voices script_v1.md (Adam) once the owner OKs it, and pushes `voice/` plus a `shots.py` skeleton built from `beats_v1.md`.
1. `git pull`. For every shot in shots.py: confirm the in-point on real frames (`python qa\sheet.py <clip> <out> 1`, then
   `qa\strip.py` 10 fps strips around it), set the negative clean span (seconds of clean picture from the in-point: no scene cut, no text,
   no logo), and keep the comment true to what is on screen. Use the other candidates of the same film when a shot does not hold.
2. Cold open (s00): one hard cut per caption, the caption's action visible from the shot's first frame; frame 0 is Valak's face with
   the caption THESE DEMONS. Check `python qa\caption_coverage.py` ends with "caption coverage OK".
3. Film lines: `python qa\find_line.py <clip> <t0> <t1> "<words>"` finds a spoken line with word times and prints the `ins(...)` values.
   Candidates (verify each word; skip any line that is not clean speech over clean picture):
   - s04 The Conjuring: the hide-and-clap game (the claps and the line around it).
   - s05 The Conjuring 2: Lorraine naming the demon ("Valak") and condemning it back to Hell, right after "just by saying it".
   - s07 Annabelle: Creation: "What do you want?" / "Your soul!" (clip cr_soul).
   - s08 The Devil Made Me Do It: Arne's "Take me!" at David's exorcism, or the "not guilty by reason of demonic possession" plea.
   - s10 The Nun: "God ends here" (the abbey door inscription, Finit hic Deo).
   - s11 outro: the two claps from the hide-and-clap scene after "don't play along" (no subtitle).
   Each insert goes BEFORE the entry's card phrase (build_edl.py warns otherwise). Use opts `lufs=-17`; the subtitle is the line exactly as spoken.
4. Tiles: fill T in make_tiles.py with one clear, bright face of each entry's demon (the stat card names it: Annabelle, the Annabelle demon,
   Bathsheba, Valak, the mirror demon, the Annabelle demon, the Occultist's demon, Valak, Valak), then `set CLIPS=<EP08>\1_work\clips` and
   `python make_tiles.py` (writes `<EP08>\1_work\tiles\<key>.png`, which render_cj.py finds).
5. Poster wall: download the 9 official theatrical posters from TMDB (release posters only, never fan art) as `<EP08>\1_work\posters\<key>_poster.jpg`
   with keys c1 a14 c2 cr n1 ach dm n2 lr (release order 2013 to 2025), then
   `python make_posterwall.py "<EP08>\1_work\posters" "<EP08>\1_work\clips\still_posterwall.mp4"`.
6. `python build_edl.py` writes edl.json: read every WARN line. Then `python qa\caption_coverage.py` and `python qa\gaps.py` (no gap over
   1.5 s). Push shots.py, edl.json and any shots_grade.py.

## Phase C: render, QA, kit

7. Music (downloaded Mixkit tracks only, never generated): `python music\make_bed.py "<EP08>\1_work\music" "<EP08>\1_work\music\conjuring_bed.mp3"`.
8. Render 1080p30: `set LEAN=1` then
   `python render_cj.py edl.json "<EP08>\1_work\clips" voice "<EP08>\1_work\music\conjuring_bed.mp3" "<EP08>\2_renders\conjuring_ranked_v1.mp4"`.
9. One careful QA pass (owner rule: one pass before every delivery):
   - Picture: `python qa\shots_grid.py <render> <prefix>` (one frame per shot, film lines at 15% and 85%) and `python qa\spans.py` on any
     doubtful section; the cold open at 10 fps with `python qa\coldopen.py <render> <prefix> 10 18` against the word onsets.
   - No trailer or title graphics, logos, black frames or scene cuts inside a span; no suicide act on screen; all sources 720p+.
   - Overlays: each stat card names its demon, with STRENGTH, INTELLIGENCE, KILL COUNT and POSSESSION, and the % and tier match stats.json:
     95 Easy, 80 and 65 Don't Worry, 55 Close Call, 45 Better Run, 40 and 30 Almost Dead, 12 and 5 Slaughtered. Film labels are right.
   - Audio: `python qa\audio_qa.py <render>`: about -15 LUFS, no silence over 1.5 s, film lines level with the narration, no clicks at cuts.
   - Fix, re-render only what changed (`set ONLY=s05,s09`, then a full run with `set REUSE=` for the unchanged sections), check again.
10. Kit: `python make_srt.py` and `python make_kit.py` (upload\conjuring_ranked_en.srt and upload\conjuring_kit.md), copy both into
    `<EP08>\3_upload`, push everything except video and audio.
11. Report: the render path and length, QA results, every GAP or replaced beat and why, and anything unsolved.
