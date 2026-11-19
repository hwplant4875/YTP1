# EP08 shot audit, v6 render (conjuring_ranked_v6.mp4, script_v3)

Method (11/19): the middle frame of every one of the {N} shots, grabbed from the final v6 render. The contact sheets are in 2_renders\audit_v6\s00.jpg to s11.jpg (480 px tiles labelled with shot id, time, clip@in-point and the words spoken; made by qa/audit_sheets.py, not committed). Frames darker than luma 45 were brightened to look at them, and every doubtful shot was checked again on frame strips of its source clip. New shots for the script_v3 lines were picked from qa/scene_library_v2.md and frame-checked before the render.

Order change: s07 is #4 The Devil Made Me Do It 35%, s08 #3 Annabelle: Creation 25%, s09 #2 The Nun 12%, s10 #1 The Nun II 5%. Each film's shot list moved with it and every shot was re-anchored to the new word timings. Rank cards, stat cards (stats.json), tier labels, film labels, kit chapters and srt follow the new order.

Pass 1 (full render) found 4 shots to fix. All were re-cut and their sections re-rendered (pass 2 and 3):
- s06 "because of it": dark frames before the lightning; it now starts on the flash with the entity crouched over Lorraine.
- s06 "and she's brought back": near-black; now Lorraine bent over Judy against the lit stair rails.
- s03 "is Evelyn's": it started on John and Mia; now Evelyn close.
- s11 "the Valak that burned a priest alive in midair": now Jacques watching, Noiret burning in the air, Jacques screaming. s10 "and burns him alive" keeps the first half of the scream; no span is shared.

Pass 4 (11/19, db69c75): the s03 line "and throw you across the room" (no true footage, was under needs reword) was reworded to "and drag you across the floor" and s03 re-voiced; its shot is now Mia dragging herself across the smoky floor in the fire scene (a14_fire 2:08-2:13, a span used nowhere else). s03 re-rendered, the video is now 8:17.6.

Rules checked:
- qa/dupes.py: 0 repeated spans (re-uploads mapped, including c2_name = c2_cz_finale - 412.6 and n1_ar_defeats = co_valak0 + 43.3, both measured on frames for v6).
- No suicide act: no Evelyn fall, no Higgins throat, no rope, attic or hanging Judy. The s06 hang line shows possessed Judy crawling and Ed after the attic.
- No graphic blood frame: cr_end 0:46 is zoomed so the wall smear stays out; the Creation adoptive-couple shots are bloodless.
- Audio: integrated -15.1 LUFS, true peak -1.5 dBFS, no silence over 1.5 s; the three film-line inserts sit 1-3 dB under the narration.

**Final counts: MATCH {MATCH}, WEAK {WEAK}, WRONG 0.**

## Needs reword (no true footage exists; a neutral true shot of that film's demon is used)

- s09 "and even then, Valak gets away, hiding inside Frenchie" (carried from v5): the escape into Frenchie and the inverted cross are in no clip (the Movieclips ending is age-gated). On screen: Frenchie (co_valak0 2:48).
- s02 "The Ferryman chases the babysitter" (partial, carried from v5): the Ferryman is only a small dark skull face; Mary Ellen dragged and running is clear.

## Every shot

| shot | time | words | clip@in | verdict | on screen |
|---|---|---|---|---|---|
