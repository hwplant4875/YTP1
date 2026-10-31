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
- Frame 0: the most famous villain of the episode (e.g. Art the Clown), already moving, and a centre caption on screen from frame 0
  (never an establishing shot, never an empty first second).
- Each beat must literally show its word: "werewolf" = the actual werewolf creature, "hunted by a clown" = the clown chasing/attacking
  with a weapon (not waving), "blown up" = the first frame of the explosion lands with the first syllable. If no clip shows it, rewrite the beat.
- Close the open with a `title` card (2 lines max, `!` prefix = red line) on the count / channel line. Clip audio under the open at about -20 dB.
- Word onsets: whisper word timestamps (`faster_whisper`, `word_timestamps=True`, decode with ffmpeg to 16 kHz float) are the cut anchors;
  the ElevenLabs alignment drifts up to 0.7 s near pauses. Use the alignment only where whisper drops a word (spoken numbers).

## 2. Structure
s00 cold open -> s01 rules (stat card demo from frame 0: bars fill as each stat is named, "??%" on "survival rate") -> one section per entry,
countdown from the easiest to the deadliest -> outro (CTA title "YOUR #1?" / next villain teaser).
Per entry: `rank` card 0-2.9 s, film label top-right per run of one film (gone when the card comes in), then the animated `stats` card from
the last beat to the end (4 bars 0-10, % stamps on the spoken number, tier cell in the tier colour). Stats: STRENGTH, INTELLIGENCE,
KILL COUNT + one fitting 4th (DECEPTION for Ghostface, SUPERNATURAL for mixed villains). Tiers: Slaughtered <=25, Almost Dead <=40,
Better Run <=50, Close Call <=60, Don't Worry <=80, Easy. Tier label (owner 10/31): the initial letter (S/A/B/C/D) big in the tier colour,
the rest of the name in white at normal size, no colour box (`ep03/anim.py` stat_card). SFX: whoosh -16 dB on card, fill -20, stamp -12 on the %.

## 3. Script and voice
- Research every kill count / survival rate on the film's plot page; viewers push back on soft ratings.
  Rate from the viewer's point of view: how likely is *you* to be a target (a killer with a narrow victim list = very high survival,
  e.g. Totally Killer 99%; a curse you can avoid by not wearing the mask = higher; rules that are hard to keep = lower). Give the
  reason in the script ("you could be a target too").
- Natural flowing sentences, viral-friend tone; no choppy "X. But Y." fragments (owner: sounds AI). Every entry ends "Survival rate: N percent."
- Listen for clipped tails: a take can end on the start of a next syllable; the renderer fades each section's voice out over its last
  0.16 s (`render_hw.py`). Transcribe the final mix around every section boundary before sending.
- Voice: ElevenLabs Adam `s3TPKV1kjDlVtZbl4Ksh`, `eleven_v4`, one take per section with previous/next text, `/with-timestamps` (key in env
  `ELEVENLABS_JC_API_KEY`; if it is not set on this machine, ask the project assistant to voice it). Pad 0.5 s (0.9 s on ranked entries).

## 4. Clips and edit rules
- Official highlight/scene clips first (Movieclips "Name (Year) - X Scene (n/9)", studio clip channels, Movieclips Indie, JoBlo / Binge Society
  clip uploads, distributor UK channels, Blu-ray label clips). Trailers only as a last resort and never with a trailer graphic in frame.
- **Never let the viewer notice a source is a trailer** (owner: "this is the core"): no title cards, quotes, "from the producer of",
  release dates, logos, end screens, "subscribe" pages, rating cards - check every shot at 15/85 % of its span and the open at 10 fps.
- **No low-quality footage, ever** (above all in the first minute): sources must be >= 1080p and sharp. Download the best stream, not the
  low-bitrate avc1 mp4: `-f "bv*[height<=1440]+ba/b" -S res,br --merge-output-format mp4` -> `<name>_hd.mp4` (render prefers `_hd`).
  Reject 480p/720p uploads and soft upscales (check `ffprobe` size + bitrate; < ~1 Mbps 1080p is soft).
  If a film has no sharp official footage at all (e.g. an old SD trailer like Ginger Snaps), **drop the film from the ranking** rather
  than use soft footage (owner 10/31: "bad picture quality is never OK"). Judge sharpness by eye on a 1:1 crop, not only by resolution.
- Villain-heavy cutting: show the villain attacking with a weapon, chasing, the iconic/story beats - something must be happening on screen.
- Age-gated clips: ask the owner to run the download with his own logged-in browser (`yt-dlp --cookies-from-browser chrome ...`);
  don't read browser cookies yourself.
- Cut on the word, action from its first frame, villain visible. No trailer title cards, ratings cards, countdowns or black frames inside a shot:
  check every shot at 15 % and 85 % of its span from the source (contact sheets lie on fast trailer cuts; verify with a real `-ss` grab).
  Use speed < 1 (slow motion) to stretch a short good shot instead of letting it run into the next trailer cut.
- No explicit gore frames (Terrifier etc.): cut on reactions. No nudity.
- Watermarks: the only allowed treatment is the black bottom bar over the Movieclips/Fandango mark (y=980). Never blur or delogo a bug
  (e.g. Prime Video) - pick another source instead. No mosaic unless the owner asks.
- Grade: scale/crop 1920x1080, slow push-in 1.04 -> 1.07, contrast 1.05, sat 0.92, gamma 1.12 (1.28 for dark sources), vignette.

## 5. Music and mix
ElevenLabs beds only, matched to the episode's theme (dark ambient for villain episodes; a Halloween special gets a Halloween bed:
music box / celesta / pizzicato / carnival waltz - ask the project assistant to generate it); no stock libraries, no script-made
scores, no hits. Music at -39 LUFS with a 3 kHz high-shelf -4 dB, voice -15 LUFS, limiter 0.95. Final ~ -15 LUFS integrated.

## 6. Render, QA, deliver
1. `python build_edl.py` -> `edl.json`; `python render_hw.py edl.json <clips> voice <music> E:/YTP2/Instruction444/renders/<ep>_vN.mp4`
   (render_v2 copy with a per-clip `bar` height; ~2.5 min per section).
2. QA grid of one frame per shot from the render (`qa/shots.py`) + the cold open frame by frame against the word onsets; loudness check.
3. Phone copy (1280x720 crf 28, ~27 MB) and show the owner before any upload; upload only after their OK.
4. Thumbnails (owner 10/31, standing rule): always 3 variants, each 3 panels (1280x720, 427/426/427, black gutters) with the %
   in f(182): LEFT GREEN, MIDDLE YELLOW, RIGHT RED (by position, whatever the tier). The three variants must look very different
   (e.g. Ghostface: A = Ghostface / character 1 / character 2, B = Ghostface 1 / Ghostface 2 / Ghostface 3). Zoomed in: the face fills
   most of the panel, eyes in the upper third, the % below the face, brighten dark faces a little; sharp HD frames of the official clips
   only (`ep_halloween/thumbs.py`, P(clip, t, cx, cy, face_h, pct, col, ...)).
5. `make_srt.py` (alignment, cues <= 42 chars / 2.8 s), chapters from the section starts into `upload/upload_kit_vN.md`. Tags: short popular words.
6. Commit scripts, md, tiles, thumbs, srt; push the branch. Report in max 3 lines per milestone.
