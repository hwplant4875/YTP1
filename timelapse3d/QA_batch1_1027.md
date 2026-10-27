# QA batch 1 (10/27 14:40 UTC, cloud supervisor) — fix list for the next edit pass
Rules: edit code first, render all later in one batch (480p 15fps previews). TOON=0.

## Part 1 (master v2)
- MISSING: master_onetake_v2_preview.mp4 was never pushed. Check logs/queue_master_v2.log + chain_all.log, concat latest g1 v5, g2 v5, g3 v6, g4 v4, g5 latest, g6 v4, g7 v3, g8 v3, push.
- g1 v5 (P0): opening still zoomed in. Start at the anime opening still's height/angle, zoom out slightly, then rise. Colossal reveal: camera low above crowd heads is right, but the FACE must fill ~1/3 of frame (move nearer the wall / longer lens; smoke must not hide the face at the reveal). Lightning = thin orange squiggles; needs ref/user/lightning_spec.md: thick wavy golden bolt + dome shockwave + white-yellow flash + orange arcs, then smoke column, then Colossal.
- g3 v6 (P1): first ~5 s of night nearly black (lift exposure / moonlight / fire glow). Trost morning + farm beat GOOD. March: thin distant line, ~25 s, hazy -> near top-down hold, column FULL FRAME, ~10 s, no haze. Training camp still a white bowl/stadium -> wooden barracks + yard.
- g8 v3 (P1): middle section near black (brighten). Green flare = thin laser beam -> rising GREEN SMOKE trail with bright head. Boulder carry hard to read (closer, slower moment). Mop-up in a wall corner must read: titans herded into the corner, killed together.

## Part 2-3
- f1 v1 (P0): huge empty flat green plain with dark polygon shadow shapes; riders/formation/Female/village almost invisible; purple flare beam; forest a dark blob; 48 s too long. -> lower, closer camera on the formation (long-range scouting wedge, readable riders), Female running in visible with tag, smoke flares (not beams), cut to ~25 s.
- f2 v1 (P2): readable forest + Female + harpoon web. OK; smoke puffs fine.
- f3 v1 (P1): duel readable (Eren vs Female in forest). But big white/blue steam "bubbles" cover the action for many seconds (transform + nape bite) -> smaller, shorter, semi-transparent. Pond-like blue discs on the ground look odd. Middle forest-floor section long and empty with tiny figures -> shorten. Lightning bolts in canopy at start too thin. Ending dusk fade OK.
- s1 v1 (P1): ~8 s of dark/empty plain at start (pink->navy->orange sky over nothing) -> cut to ~2 s. Stohess approach + church/fight good. White transform flash fine. Last ~10 s repetitive top-down city with small steam puffs -> shorten / zoom to the fight.
- s2 v1 (P2): city chase + climb readable; ending face in the wall reads well (good last shot). Wall climb section: Female small on the wall -> slight zoom. Consider holding final face ~2 s, not 4.

## Added 15:00 UTC (master v2 3:27 now pushed)
- g5 v4 (P1): Colossal #2 above the Trost gate hardly visible (only a smoke puff + thin orange arcs) -> large Colossal head over the wall for ~1.5 s, then vanish in steam; lightning per spec. Middle/late section (district fly-over) too dark/murky, with odd diagonal light shafts -> brighten, remove the shafts. Overall master v2 = 3:27, keep the total at 3:30-4:00 after fixes.

## STATUS (autopilot 10/28)
- [x] g1 -> g1_fall_v7: tree-still opening OK, golden bolt + flash + sparks + arcs read, smoke before the head, FACE ~1/3 frame (285 mm).
- [~] g3 v7 reviewed: night start OK, Trost/farm OK; march still thin strip, post-march night black, camp still round -> v8 rendering.
- [~] g8 v4 reviewed: middle bright, green smoke flares OK, carry readable; herd-kill corner titans too small -> v5 rendering (closer cam).
- [~] g4 v5: opened near black -> v6 (night grade lifted, flat camp) rendering.
