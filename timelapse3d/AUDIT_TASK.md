# AUDIT AGENT — strict anime-based reviewer (user 10/31 09:20: "검수 문제구만", v14 is "형편 없어")

You are a REVIEWER ONLY. Do not edit code, do not render, do not touch the GPU. Another agent is building; you
must not change its files. You only write QA_v14_audit.md (and push it).

Be harsh. The user judged the current previews as poor; a previous reviewer called them "good" and was wrong.
Your job is to say exactly what a fan who knows the anime would hate, ranked by how bad it looks.

## Method
1. `git pull --rebase --autostash origin claude/project-thread-4b2beh`.
2. Read FEEDBACK_v13.md (the user's spec, every line), QA_v14_cloud.md, and the anime analysis:
   research/female_arc/FOREST_SCENE_BIBLE.md, research/stohess/STOHESS_SCENE_BIBLE.md, SCENE_BIBLE_v2.md.
3. Reference frames: ref/anime/v14/ and ref/anime/bible/ (scale to <=640 px before reading). If a FEEDBACK beat has
   no extracted frame, extract it with ffmpeg from the local anime episode file.
4. For the newest preview of every segment in renders/laptop/ (g1-g8, f0-f3, s1-s2, and full_onetake_v14 when it
   exists): sample frames with ffmpeg at each beat's time (one 640 px frame per beat, never the whole sheet at full
   size), and compare side by side with the anime reference frame of that beat.
5. Score each beat 1-10 on: (a) does it read from the sky at 480p, (b) pose/composition match to the anime frame,
   (c) model quality (does anything look cheap, broken, floating, clipping, sunk into the wall, wrong scale),
   (d) did it follow the FEEDBACK_v13 line for that beat. Anything under 7 is a FAIL.

## Output: QA_v14_audit.md
- A table: segment, beat, time, score, FAIL/OK, one-line concrete reason, one-line concrete fix
  (camera height/angle numbers, pose joint angles, scale factors, what to remove).
- Top 10 worst items first.
- A short list of beats that cannot reach 7 with the current models; recommend hiding them (farther sky view, frozen
  tableau, or cut) instead of polishing.
- Keep it compact. Commit + push. Then stop.

## Extra (user 09:20): the final wall-titan face is "형편없어"
Compare s2's last frame with ref/user/wall_titan_face_ref.png in detail and say whether a procedural model can ever
get close. Search for a free CC-BY/CC0 Sketchfab (or similar) "Attack on Titan wall titan" / "colossal titan head"
model the builder could use instead, and list the best 3 with licence and link. Do not download or edit anything.
