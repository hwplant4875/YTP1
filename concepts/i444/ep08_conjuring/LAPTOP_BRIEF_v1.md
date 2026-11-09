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

## Phase B0: verify the shot list on frames (now: no voice needed)

The cloud pushed `shots.py` (204 shots from beats_v1.md, both script variants: `pick()` takes the v1.1 shots when the take holds the
script_v1_1.md wording, which is the no-film-file variant) and `shots_grade.py` (marks, bars, framing). Music: the owner picked Mixkit for
Horror Ranked on 11/7 (EP04), so downloaded Mixkit beds are approved; the 10/27 note in your memory is outdated.
1. For every shot: grab its in-point and its in-point + clean span (`python qa\sheet.py <clip> <out> 1`, `qa\strip.py` 10 fps where it
   is tight). Fix the in-point, the clean span and the comment so they are true to the frames. Spans marked `(verify)` came from your
   clip summaries, not from frames: check those first.
2. Fill the TODO picks that only need a choice of span: s01 ach_devil_cz 298.2-305 (the case shut, doll inside), s02 survival (ach_end
   46-81 crucifix fight), s03 a14_fire (Mia at home) and a14_baby (Mia in the nursery with the doll), s05 c2_name_b 0-58 (Lorraine with
   the bible), s08 dm_vision ~185 (the knife). Leave the real GAP lines (clip 'GAP' or an age-gated clip name) as TODO.
3. Framing: each shot after an entry's card phrase (and all of s01) uses L: the subject must sit left of x 840. co_valak0 is 2.39-matted
   (picture rows 140-939, measured in B0), and add any n2 Movieclips clip that carries the mark to MC in shots_grade.py.
4. The two inserts in s05 and the one in s08: Lorraine / Arne should be on screen while speaking; if not, start on the clip where they are
   and keep the words exact (qa\find_line.py). The s11 clap insert: the two claps and the match dying, trimmed where the dark begins.
5. Run `python qa\dupes.py` after a build (Phase B step 6): no moment should be shown twice (s01 and s03 share "her SOUL": look for a
   second angle of the writing after a14_baby 60.4).
Push shots.py and shots_grade.py (text only) and report in a few lines: what changed, every span you could not confirm.

## Phase B0b: shot speeds, one repeat, soft zooms (now: still no voice needed)

B0 made every clean span true to the frames, so many phrases now sit on a shorter span and get slowed (build_edl.py slows a shot to
fit its clean span, down to 0.4x; under that it runs past the cut). New tools: `python qa\synth_voice.py voice_synth script_v1_1.md`
writes a SYNTHETIC take (shaped noise at Adam's pace, git-ignored, never for a render), then `set VOICE=voice_synth`,
`python build_edl.py`, `python qa\dupes.py`, `python qa\caption_coverage.py`, `python qa\gaps.py`. build_edl.py now prints each shot's
anchor phrase in `NOTE slow` (under 0.6x) / `WARN too short` (under 0.4x) and `NOTE soft` / `WARN soft` (fewer than 720 / 640 source rows on
screen: EFFH / z, EFFH in shots_grade.py; add any clip that is not 1920x1080). The cloud run on v1.1 shows 8 WARN too short, 26 NOTE slow,
3 WARN soft and 1 repeat. Goal: no WARN, no repeat; NOTE slow only on near-still shots (a doll in a case, a face that barely moves), never
under 0.45x on anything that moves. Fix in this order, each new span checked on frames as in B0:
1. **Repeat:** s01 'which is how completely' (c2_janet 220.37, z 1.6) is the same moment as s05 'then it takes over janet'. Give s01 another
   body-taken-over shot, L framing, at least 2.9 s clean (or two shots): co_mother_c levitation 240-264 (sheet-covered Carolyn), dm_david
   303-319 / 321-329 / 331.4-342 (David's exorcism), lr_end 100-108 / 110-118 (possessed Judy, not 109.15-109.6).
2. **WARN too short** (split the phrase with a 2nd row anchored on a later word of the same sentence, or a longer span of the moment):
   - s03 'to force a trade' a14_basement 64.0 (0.75 s for "to force a trade, the baby for her soul."): Leah may run from the 63.33 cut;
     'the baby for her soul' could be the doll in Leah's crib (a14_baby 45.8-48) or Mia.
   - s04 'with a happy memory' universe 697.6: two or three beach shots (each beach shot is 0.6 s or less).
   - s05 'so everyone thinks' c2_vision 56.05 (0.7 s for "so everyone thinks it's just a ghost."): 'it's just a ghost' on Bill Wilkins
     in his chair (c2_vision 0-55, a span the s05 rows do not use).
   - s08 'a witch puts a curse' dm_calvary 40.8: 'on you' on the shot after the 41.47 cut (Arne's arm).
   - s08 'twenty-two times' dm_bruno_b 174.75: the grab, then the scream shot inside 174.4-175.9 (each one shot, no black).
   - s09 'and this valak is far' n2_lucy 21.82 (3 s): 'stronger than any demon' on another Valak shot (n2_lucy 10 / 106, n2_deliv 242-245).
   - s09 'it lifts a priest' n2_burn 371.3: the wide lift from ~370.6, then 'into the air' on the close 371.3-371.85.
   - s10 'this is valak at full power' spooky_nun 1092.45: 'at full power' on another Valak shot in 1050-1098 (not 1063.0-1065.15, s11 uses it).
3. **NOTE slow under 0.5x on moving shots:** split the same way where the sentence allows. The longest: s02 'and as long as' (split at
   'it can't touch anyone'), s03 'but it has one big weakness' (at 'it can't just take'), s04 'leaves bruises' (at 'while she sleeps'),
   s04 'then she takes over' (at 'carolyn'), s07 'and unlike the last one' (at 'it kills almost everyone'), s09 'that would give it back'
   (at 'the power it had'), s01 'and one has wiped out' (at 'an entire abbey'). Entries whose card shot runs through "Survival rate"
   (s03 'never offer it your soul', s04 'she only wants the mother') may get their own 'survival rate' row (L, the demon's face).
4. **WARN soft:** dm_final is 720p, so z 1.35 leaves 533 rows: for s08 'and only smashing' and 'can break it' use z 1.1 at most (dx and
   flip to keep the hammer / the break left of x 840; the card may cover the right edge of the table) or a 1080p span of the same moment if
   you find one. n2_lucy is 842p: s09 'survival rate' (z 1.35, 623 rows) needs z 1.3 at most or a 1080p Valak face (n2_exorcise, n2_maurice).
   z 1.5-1.6 on a 1080p clip (675-720 rows) is acceptable when it keeps a face off the card.
5. Run both variants: the v1.1 take (no GAP rows) and `python qa\synth_voice.py voice_synth1 script_v1.md` with `set VOICE=voice_synth1`
   (its WARN lines next to a skipped GAP row are the GAP's, not a span problem). Push shots.py and shots_grade.py (text only) and report:
   the counts before and after, and any line you had to leave slow or soft.

## Phase B1: picture proxy on the synthetic take (now)

The owner chose to wait for the JC credits reset on 11/11 18:27 KST before voicing. Meanwhile the whole picture is rendered and
checked on the v1.1 synthetic take; on voice day only the timing changes.
1. `set VOICE=voice_synth`, `python build_edl.py` (this edl.json comes from the synthetic take: never commit it).
2. `set LEAN=1`, then `python render_cj.py edl.json "<EP08>\1_work\clips" voice_synth "<EP08>\1_work\music\conjuring_bed.mp3"
   "<EP08>\2_renders\proxy\conjuring_PROXY_synthvoice.mp4"`. Its narration is shaped noise: picture QA only, never delivered or uploaded.
3. Picture QA, everything in Phase C step 9 except the narration: `python qa\shots_grid.py <proxy> <prefix>`, and
   `python qa\coldopen.py <proxy> <prefix> 10 18` (VOICE is still set). Check every shot and overlay:
   - rank cards (#, demon, film); stat cards (each entry's own demon, the four stats, the % and tier text and colour of stats.json);
     tiles; film labels (right film, gone once the card is up); the s01 rules card (bars fill on each stat word, "??%"); the insert
     subtitles exactly as spoken; the clap ending; the subscribe png; the poster wall.
   - no logo, mark, burned text, end card, black frame or scene cut inside a shot; every subject left of x 840 under a card; no suicide
     act; gore never the worst frame; dark shots lifted but not washed out (the owner dislikes heavy grading).
   - letterbox bars: the dm_final rows at z 1.1 keep their bars (cloud decision: bars are better than 533-row softness).
4. Audio apart from the narration: the three film lines clear and level (lufs -17), the music ducked under them, the two claps at the end.
5. Fix spans, framing or the VDARK/DARK lists, re-render only what changed (`set ONLY=s05,s09`, then a full run with `set REUSE=`
   listing the unchanged sections), check again.
6. Dry-run the kit format: `python make_kit.py edl.json "<EP08>\1_work\proxy_kit.md"` and
   `python make_srt.py edl.json voice_synth "<EP08>\1_work\proxy.srt"` (fan one-liner, [ Timeline ] chapters, hashtags; timings are
   synthetic). Do not commit these.
7. Push shots.py and shots_grade.py (text only) and report: render time, what QA found and fixed, anything that needs the owner.

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
