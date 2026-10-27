# AUTOPILOT — AoT 3D timelapse, run until the budget is spent (user 10/27 15:15 UTC)

The user is away until Saturday and wants this ONE run to use the whole budget (~$200) on QUALITY.
Nobody will answer questions: decide yourself, following the rules below, and keep going.
Do NOT end the run early. When one round is done, start the next round. Stop only when the budget runs out.

## Start
1. `git pull --rebase --autostash origin claude/project-thread-4b2beh`.
2. Read HANDOFF.md (RESUME 10/27 + PART2-3), QA_batch1_1027.md (the fix list), ref/user/lightning_spec.md,
   research/female_arc/FOREST_SCENE_BIBLE.md, research/stohess/STOHESS_SCENE_BIBLE.md.
3. Check whether a render chain is already running (GPU lock, blender processes, logs/). Never start a second one;
   wait for it, and edit code meanwhile.

## Loop (repeat until the budget ends)
1. Fix the next open item of QA_batch1_1027.md (P0 first: g1, f1; then g3, g5, g8, f3, s1; then P2). Small targeted edits.
2. DRY-build check, then render that segment's 480p 15 fps preview DETACHED (GPU lock), plus one contact sheet.
3. While it renders, edit the next item.
4. Review each new sheet yourself (scale to <=1280 px with ffmpeg BEFORE reading any image). Compare with the
   user feedback in HANDOFF and the bibles. If it is still wrong, fix again. Mark items done in QA_batch1_1027.md.
5. Commit + push every render (version-labelled, renders/laptop/), and append 2 lines to HANDOFF.md.
6. When every item is done: re-concat master_onetake_v3_preview.mp4 (Part 1) and part2_3_onetake_v2_preview.mp4,
   and a full 3-part one-take full_onetake_v1_preview.mp4. Push them (>95 MB: higher-CRF 480p copy).
7. Then a self-QA round on the full one-take: seams continuous, nothing too dark, key moments readable
   (Colossal faces, Reiner grab with REINER tag, Female capture, Eren vs Female, Stohess, titan in the wall),
   pace fast (Part 1 3:30-4:00). Write new items into QA_round2.md and loop again.

## Binding rules
- Work only inside E:\YTP2. Never delete files you did not make. No uploads. No final/hi-res render (the user
  approves that on Saturday). Previews 480p 15 fps only.
- Style: calm far sky camera, one continuous take, fast pace with a slight zoom-in at key moments, TOON=0,
  true-scale faceless humans, titans keep faces, name tags Russo One max 3, no anime footage in the video,
  no music/voice (the user adds them).
- Wait for renders with Bash sleeps of up to 9 minutes; keep tool output short (tail logs, never dump images).
- At the end of every round, update REPORT_FOR_USER.md (Korean, short): what changed, links to the newest
  previews, what is still weak. That file is what the user reads on Saturday.
