---
name: horror-ranked-episode
description: Make a Horror Ranked (formerly Instruction 444) "Every <villain> Ranked by Your Chance of Surviving" long-form episode the EP01 Myers / EP02 Jason / EP03 Ghostface way - word-synced cold open with big centre captions on every cut, rules card, countdown with stat card + survival % + tier, outro, render, QA, thumbnails, srt, upload kit. Use for any new Horror Ranked episode or when re-cutting one.
---

# Horror Ranked episode (EP01-EP03 method)

Repo: `concepts/i444/` on the project branch (worktree `C:\Users\hw549\Downloads\YTP1\i444_wt`). Code to reuse:
`ep01/gfx.py` (word_tag, title, rank_card, film_label; YouTube Sans Black), `ep03/anim.py` (animated stat card, tiers),
`ep03/build_edl_v2.py` (EDL builder pattern), `ep03/render_v2.py` (frame-exact renderer), `ep03/make_srt_v2.py`, `ep03/thumbs_v2.py` (C layout).
Big files (clips, renders) only on `E:\YTP2\Instruction444\{clips,renders}\<episode>`; never commit video.

## 1. The cold open is the core (owner: "that's the key")
The first ~15-20 s is a run of short punchy beats, each one = **one hard cut + one big centre caption, landing on the spoken word**.
- Script it as a list the narrator can rattle off: EP02 "Hacked, hanged, drowned, electrocuted, blown to pieces, frozen, and, umm, thrown into space?";
  EP03 "He's been shot, stabbed, set on fire, run over by a car, shot in the head...". Then a twist line, then the count ("11 JASONS", "16 GHOSTFACES").
- For every beat: shot starts at `onset(word) - 0.08 s` (LEAD) on the first frame of that action, villain clearly visible;
  `('word', 'Hacked', 'hacked', 'hanged')` = centre caption (`gfx.word_tag`, white, f(170), shadow) from this word to the next, capped at **0.9 s**
  (`ov[3] = min(ov[3], ov[2] + 0.9)`), so captions flash one after another and cut out - never two at once, never late.
  Phrases ("Mauled by a werewolf") may stay up to 1.5 s and must fit the frame: shrink to <= 1760 px or split over two lines
  (`fit_word` in `ep_halloween/render_hw.py`). Check the open at 10 fps from the render: no caption off-screen, no stray frame of
  the next trailer cut or a black flash inside a beat (slow the shot down instead).
- Close the open with a `title` card (2 lines max, `!` prefix = red line) on the count / channel line. Clip audio under the open at about -20 dB.
- Word onsets: whisper word timestamps (`faster_whisper`, `word_timestamps=True`, decode with ffmpeg to 16 kHz float) are the cut anchors;
  the ElevenLabs alignment drifts up to 0.7 s near pauses. Use the alignment only where whisper drops a word (spoken numbers).

## 2. Structure
s00 cold open -> s01 rules (stat card demo from frame 0: bars fill as each stat is named, "??%" on "survival rate") -> one section per entry,
countdown from the easiest to the deadliest -> outro (CTA title "YOUR #1?" / next villain teaser).
Per entry: `rank` card 0-2.9 s, film label top-right per run of one film (gone when the card comes in), then the animated `stats` card from
the last beat to the end (4 bars 0-10, % stamps on the spoken number, tier cell in the tier colour). Stats: STRENGTH, INTELLIGENCE,
KILL COUNT + one fitting 4th (DECEPTION for Ghostface, SUPERNATURAL for mixed villains). Tiers: Slaughtered <=25, Almost Dead <=40,
Better Run <=50, Close Call <=60, Don't Worry <=80, Easy. SFX: whoosh -16 dB on card, fill -20, stamp -12 on the %.

## 3. Script and voice
- Research every kill count / survival rate on the film's plot page; viewers push back on soft ratings.
- Natural flowing sentences, viral-friend tone; no choppy "X. But Y." fragments (owner: sounds AI). Every entry ends "Survival rate: N percent."
- Voice: ElevenLabs Adam `s3TPKV1kjDlVtZbl4Ksh`, `eleven_v4`, one take per section with previous/next text, `/with-timestamps` (key in env
  `ELEVENLABS_JC_API_KEY`; if it is not set on this machine, ask the project assistant to voice it). Pad 0.5 s (0.9 s on ranked entries).

## 4. Clips and edit rules
- Official sources only (studio/distributor channels, Movieclips, official trailers); yt-dlp `<=1080p mp4`; age-gated ones are skipped and listed.
- Cut on the word, action from its first frame, villain visible. No trailer title cards, ratings cards, countdowns or black frames inside a shot:
  check every shot at 15 % and 85 % of its span from the source (contact sheets lie on fast trailer cuts; verify with a real `-ss` grab).
  Use speed < 1 (slow motion) to stretch a short good shot instead of letting it run into the next trailer cut.
- No explicit gore frames (Terrifier etc.): cut on reactions. No nudity.
- Watermarks: the only allowed treatment is the black bottom bar over the Movieclips/Fandango mark (y=980). Never blur or delogo a bug
  (e.g. Prime Video) - pick another source instead. No mosaic unless the owner asks.
- Grade: scale/crop 1920x1080, slow push-in 1.04 -> 1.07, contrast 1.05, sat 0.92, gamma 1.12 (1.28 for dark sources), vignette.

## 5. Music and mix
ElevenLabs dark-ambient beds only (`ep03/music/*_loop.mp3`; music-box ambience suits Halloween); no stock libraries, no script-made
scores, no hits. Music at -39 LUFS with a 3 kHz high-shelf -4 dB, voice -15 LUFS, limiter 0.95. Final ~ -15 LUFS integrated.

## 6. Render, QA, deliver
1. `python build_edl.py` -> `edl.json`; `python render_hw.py edl.json <clips> voice <music> E:/YTP2/Instruction444/renders/<ep>_vN.mp4`
   (render_v2 copy with a per-clip `bar` height; ~2.5 min per section).
2. QA grid of one frame per shot from the render (`qa/shots.py`) + the cold open frame by frame against the word onsets; loudness check.
3. Phone copy (1280x720 crf 28, ~27 MB) and show the owner before any upload; upload only after their OK.
4. Thumbnails: C layout 1280x720, three panels 427/426/427, black gutters, f(182) % in tier colours (green/yellow/red), the deadliest face biggest,
   from HD frames of the official clips. Plus a single-villain variant with a huge red %.
5. `make_srt.py` (alignment, cues <= 42 chars / 2.8 s), chapters from the section starts into `upload/upload_kit_vN.md`. Tags: short popular words.
6. Commit scripts, md, tiles, thumbs, srt; push the branch. Report in max 3 lines per milestone.
