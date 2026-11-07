# Backrooms special: shot plan (11/7 KST)

The owner approved script v1 at 18:23 KST ("뭐 이후에는 알아서 잘 편집해서 가자"). The edit is ours to judge, inside the rules
below. `shots.py` holds every beat as `(phrase, clip, TODO, TODO)  # what must be on screen`. This page explains the design and
how to fill it.

## The format on screen (this episode must not look like the ranking template)
- One continuous journey in the second person. No rank cards, stat cards or tier labels.
- **YOUR SURVIVAL** sits top-right from s01 ("The number in the corner...") at 100%. On every spoken percentage the new number lands
  big in the centre with a stamp, then flies into the corner (green 90/70, yellow 40, red 15 and below).
- **Place names** top-left at each stage start: THE SLIT, THE MAP, THE LAUNDRY ROOM, THE STILL LIFES, AFTER HIM, YOUR OLD HOME,
  THE DINING ROOM, CAPTAIN CLARK, ASYNC.
- **TURN BACK / KEEP GOING** on the four "So what do you do?" beats: both appear on the question, the take pauses 0.9 s, then
  KEEP GOING turns red as the answer starts (s02, s03, s04, s06).
- **Seven film lines** play with their own audio and a bottom subtitle; the narration stops around them.
- **Dates**: JUNE 19, 1990 (s01), JUNE 29, 1990 (s02), and both again in s11 with 10 DAYS LATER.
- **1 OF 5** at the end of s10 ("One out of five.").
- The cold open (s00) keeps the channel's caption style: every word on screen in 19 chunks, one hard cut per chunk.
- All text is YouTube Sans Black, white with a black stroke and a soft shadow (gfx_br.py). No boxes, pills or bars.

## Inserts (set in shots.py with ins(...))
| Section | After | Kind | Clip and line |
|---|---|---|---|
| s01 | "come and get him." | film | Naren, op_joblo_1990 radio call 1:40-2:28: "There's something else in here." |
| s02 | "So what do you do?" | choice | 0.9 s |
| s03 | "So what do you do?" | choice | 0.9 s |
| s03 | "...and on and on." | film | Clark, s2_tells_mary: "Sometimes I'm scared I'll get lost." |
| s04 | "So what do you do?" | choice | 0.9 s |
| s04 | "...standing in the dark." | film | Bobby, s3_laundry (or s3_joblo_pullup 0:05-1:16): "There's someone down there!" |
| s05 | "...picks it up." | film | Kat, s3_joblo_pullup ~6:15-6:22: "Clark, behind you!" |
| s06 | "So what do you do?" | choice | 0.9 s |
| s08 | "...he snaps." | film | Clark, s7_stay_char: "Stay in character!" |
| s08 | end ("panics and runs.") | hum | 0.85 s, the empty dark arch, s7_joblo_reveal 3:39-3:49, room tone only |
| s09 | start | thud | 0.4 s, Captain Clark's first step at the arch (3:50), the step's own sound plus a low slam |
| s09 | "...like a dinner guest." | film | Clark, s7_joblo_reveal ~4:05: "This is Mary. She's our therapist." |
| s10 | "...if they'll let you go." | film | Phil, end_joblo_phil ~4:01: "That decision's not up to me." |

For every film line: `python qa/find_line.py <clip> <t0> <t1> "<words>"` prints the word times and a ready in-point and length.
The speaker should be on screen, nobody else talking over it, no swearing inside the span. Put the words exactly as spoken in `sub`.
The near-silence + thud keep the gap before "Something huge steps into the room" at 1.31 s (rule: never over 1.5 s).

## Picking shots
- A fresh shot every 2-3 s that literally shows the sentence; the comment in shots.py says what must be on screen. Swap the clip
  when another one holds the moment better; many beats in s02 (first trip) are in s1_joblo_first, s1_first_a/b and s1_a24_clip.
- `-clean` = seconds of usable picture from the in-point: no cut to an unrelated scene, no text, never the JoBlo end card (last ~16 s
  of every JoBlo upload). A shot shorter than its slot gets slowed (not below 0.4x), so prefer spans at least as long as the slot.
- The 1990 tape is 4:3 inside the frame: add `T4` (z=1.333) to every op_* shot so it fills the screen.
- Gore: cut on the hit or the reaction. Bobby: the drag and the blood trail, never the body. Clark being eaten: the lift and Mary's
  scream, not the bite. The knife in the guest's neck: the blank face. The choke: short. Kat's head is never on screen (Mary's face or
  the closed fridge). No nudity.
- Not usable: end_phil (574p, watermark), s2_therapy (watermark), s7_dinner_full (burned subtitles), s4_tree_pool (Spanish
  subtitles), trailer/x_a24_c/x_a24_d text and logo spans.
- Frame 0 is the thumbnail-strength image: Captain Clark big and clear (s7_joblo_reveal 3:51-3:56 / 4:07, or the 4K packs
  s8_pack_a/b), with "FIVE PEOPLE" already on screen.
- Clip audio is off by default (the narration and the music carry the sound). Where a shot has a clear real sound with no
  dialogue and no film music (a thud, a door, a scream at the cut), `a=-20` puts it softly under the voice.
- Dark shots: list them in `shots_grade.py` (DARK = [...] gamma 1.25, VDARK = [...] gamma 1.4) after the span check, as in EP04.

## Checks before rendering
1. `python build_edl.py` prints no "TODO shot skipped" and no "WARN too short".
2. `python qa/caption_coverage.py` is OK and every caption has its own cut.
3. `python qa/gaps.py` is OK (no silence over 1.5 s).
4. `python qa/spans.py <clips> <out.jpg> sNN` for every section: each row shows what its comment says, start to end.
