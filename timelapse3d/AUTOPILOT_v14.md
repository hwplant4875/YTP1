# AUTOPILOT v14 — implement FEEDBACK_v13.md (user 10/31). Runs on Opus 5.5, medium effort, until done or budget ends.

Nobody answers questions mid-run: decide yourself within the rules. Be credit-efficient (short tool output, small
edits, scale images to <=1024 px before reading, few stills).

## Start
1. `git pull --rebase --autostash origin claude/project-thread-4b2beh`. Read FEEDBACK_v13.md (the spec), HANDOFF.md
   (latest RESUME notes), REPORT_FOR_USER.md, ref/user/wall_titan_face_ref.png (scaled).
2. Check that no render is running (GPU lock, blender processes) before starting one.
3. Extract the anime reference frames listed in FEEDBACK_v13.md to ref/anime/v14/ (ffmpeg -ss, one frame each, 640 px).

## Order (P0 first; commit + push + 2-line HANDOFF note after each item)
1. Frozen-tableau toolkit: a reusable helper (pose library for the Female/Eren/Scouts rigs, Track-To camera rig on an
   empty, 2-3 s slow partial orbit/dolly, then ultra-fast fly-out). Pose check: one 270p still per pose.
2. Part 2 rebuild per FEEDBACK §2 (formation graphic EP17 06:21-06:25, all frozen tableaux, fire-can spin, forest floor
   blend + richer forest detail, lightning-only transformations, skip the cart scene).
3. Part 3 per FEEDBACK §3 (sky-view Stohess, frozen punch, wall climb with Mikasa, Eren on top, wall titan face 99%
   like the reference).
4. Part 1 per FEEDBACK §1 (opening zoom, no orange arcs, "Colossal Titan" title, evacuation sky view, 0:30 seam,
   bigger captions, farm camera side, wide static 250k, training-ground rollback from git history, 1:14 fixes, cut
   Eren's titan-pull, water, cannons left, red flare, ARMIN/LEVI tags, struggling 5 s carry, mop-up at wall corner +
   night burning corpses, faster eastward move).
5. Render changed segments (480p 15 fps, detached, GPU lock), review each contact sheet against FEEDBACK_v13, fix
   until right, then concat full_onetake_v14_preview.mp4 (+ sheet, keymoments jpg) and push.
6. If budget remains: a self-QA round on v14 (QA_v14.md), fix, re-render, v15.

## Binding rules (unchanged)
- Only inside E:\YTP2; never delete files you did not make; no uploads; no final/hi-res render; previews 480p 15 fps.
- One continuous sky camera take, TOON=0, true-scale faceless humans, titans keep faces, name tags Russo One max 3,
  captions New Rocker, no anime footage in the video, no music/voice.
- Wait for renders with Bash sleeps up to 9 min.
- At the end of every item update REPORT_FOR_USER.md (Korean, short): what changed, newest preview links, what is weak.
