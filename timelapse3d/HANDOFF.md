# Who edits what (cloud session <-> laptop session)

- Laptop session owns `aot/scene.py`, `hud.py` and rendering (Eevee, GTX 1060). The cloud session does not edit these.
- Cloud session writes NEW modules only: `aot/characters.py` (child Eren asleep under the tree, Mikasa with red scarf, firewood frame; exposes `make_eren()`, `make_mikasa()`), plus the wiki design bible.
- Building blocks already pushed (c1af15e), use them instead of starting over:
  - `aot/district.py`: U-shaped Shiganshina matched to `ref/shiganshina_anime_ref.png` (WD=380, LS=700, outer gate (0,-1080), inner gate (0,0), canal x=-338 w=28 with 2-arch water gates in both walls, plaza + white monument (0,-540)). Replaces scene.py's R=520 semicircle.
  - `aot/walls.py`: `build_wall` (16 m slabs on a core + pilaster strips, use for Wall Maria too), `arch_gate` (arched tunnel + iron-banded door or water gate), `wall_top_props` (twin rails, cannons every 4 slabs at the outer edge, barrel clusters; ref `ref/walltop_cannons_ref.png`). Syntax-checked, not render-tested.
  - `aot/titans.py`: MPFB2 titans `make_titan(kind)` pure/colossal/armored/attack/female, `walk_pose`, `relax_pose`, `steam`. Needs MPFB2 2.0.18 + MakeHuman CC0 system assets.
  - `hud.py` font set D (Ditty + Pirata One) is the default.
- Canon: all walls 50 m. 845: Colossal (60 m) at the outer gate kicks it in; Armored breaks the inner gate. Pure titans 3-15 m, odd proportions, no genitals. Forest of Giant Trees between Maria and Rose (80 m+ trees). Eren's tree on the hill at HILL=(330,820) north of the inner gate.
- Review screenshots: commit to `timelapse3d/renders/` and push; the cloud session forwards them to the user.

## Update 17:30 UTC (cloud)
- `aot/characters.py` is ready for the opening: `eren_tree(base)` (mossy broad-leaf tree, returns trunk, crown, radius) and
  `place_opening(base, facing=..., trunk=trunk_obj)` (Eren asleep against the bark found by ray cast, Mikasa standing with the red scarf,
  two firewood frames). Needs the same MPFB setup as titans.py. Example:
  `trunk, crown, r = characters.eren_tree(HILL_BASE); characters.place_opening(HILL_BASE, facing=angle_towards_town, trunk=trunk)`
- `aot/ep1_canon_events.json`: 50 verified S1 chapters in Eren-POV order (year, episode, place, caption, what happens, 3D visuals),
  plus map notes (Sina 250 / Rose 380 / Maria 480 km radii; Trost ~100 km north of Shiganshina with a river and pulley ferries;
  Karanes east of Rose; Forest of Giant Trees ~20-30 km E/ESE of Karanes; Stohess east of Sina).
- `ref/wiki/`: anime stills for Shiganshina (U shape, canal bridges, inner-gate fortress, the hill tree) and the walls
  (wall-top cannons on turntables with rails and crates, brick inner gatehouse with the wall emblem, inner-face pilasters).

## Update 17:45 UTC (cloud) - user feedback on the opening
- People are FACELESS (smooth head, no eyes/nose/mouth/ears); only hair and iconic outfits. characters.py now does this.
- Outfits from `ref/eren_mikasa_845_outfits_ref.png`: Eren olive shirt + long open dark-red coat + charcoal trousers; Mikasa long white dress + long pale-pink cardigan + dark red scarf, shoulder-length black hair; Mikasa carries her firewood frame on her back.
- Eren is animated: lies asleep (frame start), sits up (+60), crouches (+100), stands (+120). `place_opening(base, facing, trunk=trunk, start=frame)`.
- The hill tree must sit much closer to Wall Maria than HILL=(330,820): about 300-400 m north of the wall, on a flowered slope, with windmills, small red-roof farmhouses and cypress/conifer clumps between the tree and the wall (see `ref/hill_tree_wall_opening_ref.png`). Shot is distant, faces never readable.

## WORK SPLIT (18:00 UTC) - please follow to avoid doing everything twice
Cloud already runs these; the laptop should NOT start its own agents for them:
- Research: S1 still library -> /mnt/project-files/plans/3d_timelapse/ref/s1_stills/ (in progress); design bible DONE -> timelapse3d/design_bible.md;
  story/canon DONE -> aot/ep1_canon_events.json; terrain/camera plan DONE -> /mnt/project-files/plans/3d_timelapse/EP1_plan_terrain_camera.md (copy below).
- Titan designs: aot/colossal.py, aot/pure_titans.py (+ walk action), aot/shifters.py (armored/female/attack) - in progress, will be pushed here.
- Opening hill shot matched to ref/hill_tree_wall_opening_ref.png: aot/shot_opening.py - in progress.
Laptop owns: scene.py/hud.py (Shiganshina + walls + terrain states per year), placing the titans from the modules above, the opening fly-over INTO the hill shot,
the other sets in the plan, and the GPU preview stills / thumbnail candidates (Colossal looking over the wall into town + 3 more). No final render.

## Cloud -> laptop (10/23 21:40 UTC)
- Thumbnails: the laptop owns them (thumbs.py, in-world, GPU). shot_thumbs.py T2-T4 (f2ebf73) are composition references only. Please port its stone-course wall material: 2.4 m horizontal courses, a dark weathered base and a lighter band under the parapet. It removes the "vertical planks" look.
- Colossal: the default is colossal.py round 4. colossal_mpfb_experiment.py (round 5) is reference only. Both are still far from the anime face, so keep the Colossal small in frame or wrapped in steam.
- Opening: shot_opening.py round 3 has smaller, sparser flowers than round 1. Re-render that version before judging the flowers.
- Your _find_mpfb() fallback and the AOT_POLYHAVEN line will be kept in cloud edits.
- No final render tonight (user's rule).

## Cloud -> laptop (10/23 22:30 UTC): Sketchfab assets
The shortlist is at /mnt/project-files/plans/3d_timelapse/assets/sketchfab_shortlist.md. All entries are CC-BY, downloadable and credited in the description. The user is asked to create a Sketchfab account and run `setx SKETCHFAB_TOKEN "..."` on the laptop. Once the token exists (open a new cmd so the variable is loaded):
1. Download each model with the API: GET https://api.sketchfab.com/v3/models/{uid}/download with the header `Authorization: Token %SKETCHFAB_TOKEN%`, then fetch the gltf zip URL it returns.
2. Save to E:\YTP2\3D Timelapse\assets\sketchfab\{uid}\.
3. Start with the Colossal by Sidaivan (e031a57fd4bf411f8e893361676b4544), then the other Colossal entries and Armored/Female/Smiling.
4. Import into Blender, scale the Colossal to 60 m, and render the same wall-top thumbnail as colossal_thumb_test.jpg so it can be compared against our procedural one.
Never put the token in the repo, logs or chat.
- 22:40: Titan pack: use it directly in cast845 on the laptop, where the pack is local. Mix it with pure_titans.py presets. No need to push it to the repo, since its licence is unclear. Credit Freestorm-Dev in the description.

## 22:24 UTC: user approved the ASSET route ("에셋 쓰는게 훨씬 좋겠다. 가자")
- SKETCHFAB_TOKEN is now set in the user's cmd (setx). Open a NEW shell to pick it up.
- Laptop: download the shortlist (assets/sketchfab_shortlist.md), Colossal Sidaivan first. Unzip with a script; the user does not open zips. Then make the Colossal wall-top thumbnail with the downloaded model and compare it with colossal.py round 4.
- The cloud stopped the procedural Colossal (round 6). colossal.py round 4 stays as the fallback only.
- Keep a CREDITS.md listing each used model, author, licence and URL, for the description.
- 22:24 user: they have ALREADY downloaded Sketchfab zip(s) into C:\Users\hw549\Downloads. COPY (do not move or delete) the *.zip files there into E:\YTP2\3D Timelapse\assets\sketchfab\, unzip them by script and use them. Fall back to the API token only for the models that are missing.

## Cloud review of colossal_asset_face_v6.png (23:45 UTC)
The face is good. Canon fixes:
1. HEIGHT VS WALL: in the anime S1E1 shot, the 50 m wall comes up to the Colossal's collarbone or lower neck. Only the HEAD (plus a sliver of the shoulders) rises over the wall, and the fingers curl over the top. In v6 the whole torso down to the waist is above the wall, so it reads as a 90 m titan. Keep the scale up (bigger head is fine for readability), but sink the root so the wall top sits at the clavicles.
2. WALL TOP: the AoT outer wall top is a flat walkway with a low parapet, rails, cannons and kegs, not crenellations (merlons). Use walls.wall_top_props and remove the merlon blocks near the gate.
3. HAND: the fingers wrap OVER the parapet edge and hang down toward the camera side, so the knuckles sit on top. Steam pours off the arm and the shoulders.
4. LIGHT: the scene is the 845 afternoon. Use a warm, low sun from the west and a hazy sky. Steam backlit by the sun is the money shot for the thumbnail.
5. For the thumbnail angle (low, over the town roofs looking up), frame the head large: about 35-45% of the frame height, with the wall edge diagonal across the frame.
- 00:0x UTC, v7/v8 check: the 23:45 review above still applies to both. v7: the torso is still above the wall and the merlons are still there. v8: the head is about 6% of the frame height and needs 35-45%. Use a longer lens (85-135 mm) from the main street so the wall compresses behind the roofs, and sink the Colossal so the wall line sits at its collarbones. Then add the warm backlight and steam.

## 03:31 UTC 10/24: user decision on the opening -> Colossal sequence
The user is happy with the titan looks. Camera rule: avoid close-ups and keep a moderate high aerial angle looking down.
Plan (cloud proposed it to the user; the default is to skip chapters 3-5 unless the user objects):
1. ONE-TAKE: start on the hill tree, glide down the hill and pass LOW through the Shiganshina inner (north) gate. Fly south along the main street at a moderate height. During the flight the light shifts from morning to afternoon (timelapse). At the outer south wall, the Colossal's HEAD rises above the wall top (reveal, with steam).
2. Crane up to the sky view and orbit OVER the wall to BEHIND the Colossal (outside, south). On the KICK impact: the outer gate collapses, stone blocks fly into the town and smash roofs, and boulders roll down the streets (rigid-body sim). Steam explodes. The Colossal vanishes in steam. Then pure titans pour in through the breach up the main avenue.
CONFIRMED by user 03:33: skip chapters 3-5 and go straight from the tree to the Colossal.

## 04:27 UTC 10/24: user's MUST-HAVE scenes
See section 6 of timelapse3d/EP1_plan_terrain_camera.md (K1-K14). Every beat is a sky view at a moderate height, with no close-ups. K1 (Carla eaten by the Smiling Titan, Eren reaching back on Hannes's shoulders) belongs right after the Colossal kick and the titans entering, before the Armored, so put it in the current one-take next.
- Your request for explicit shots is done: section 6 (K1-K14) of timelapse3d/EP1_plan_terrain_camera.md lists the chapter, place, who and what, the sky-view staging and the readability cues. The Sasageyo question went to the user. Default: in EP1, use the S1E16 night recruitment speech with all the cadets saluting (K3, verified as S1E16). The S3P2 charge belongs in a later episode.
- 04:30: user confirmed Sasageyo = S1E16 recruitment. Section 7 of the plan (V1-V23) adds every must-not-miss beat for viewers, with a running order. Build them in that order after the opening one-take.
- 04:31: the cloud already finished the full S1 story audit (plan section 7, V1-V23). A Workflow re-audit is not needed; the user was told they may decline it to save usage.
- User 04:30: the Sketchfab "Female Titan - Tilt Brush" by juliusprod (uid f7da1238b6ae4e76944d1da72156c808, CC-BY) shows her BOUND in cables, so use it for K11 (the trap). Download it with the token and test it at sky distance next to the other assets. Tilt Brush strokes may look painterly; if it clashes, use it as the pose and cable-layout reference for our Female asset. Add it to CREDITS.
- 04:38 user: see plan section 8 (dialogue overlay hold windows). Applies NOW to the Shiganshina one-take: K1 "Yamero" needs about 2 s of Eren's reaching arm visible before the transition. Keep a timing sheet (renders/timing_sheet.csv: beat, frame_in, frame_out, line).
- NAMU WIKI: the S1 plot summary page is 403 from the cloud. Please fetch it from the laptop and save it as text to timelapse3d/ref/namu_s1_plot.txt, then push: https://namu.wiki/w/진격의%20거인(애니메이션%201기)/줄거리 . The cloud will cross-check the plan against it.
- 04:50: please push the 16-frame Colossal sequence contact sheet (one JPG, under 2 MB) to renders/laptop/ so it can be shown to the user. Canon checks for the fixes: (a) the Colossal kicks with its right leg FORWARD through the gate, from outside toward the town, and the debris flies INTO the town (north); (b) after the kick it vanishes in an expanding steam cloud over about 3 s, with no sinking; (c) inflow titans walk through the breach, not over the wall.

## 05:00 UTC: USER TRIMMED THE PLAN
timelapse3d/EP1_beats_final.md (30 beats) now SUPERSEDES plan sections 6-7 and EP1_must_have_beats.md. The user said "too many unnecessary things; the earlier plan was better". Focus on the 3D TIMELAPSE: big-picture events from outside, maps, armies, destruction, and NUMBERS AS GRAPHICS (for example the 250,000 counter). Drop the private moments and dialogue scenes. Keep only the user-named emotional beats with their overlay holds. Do not build anything from the 137 list that isn't in the 30.
- 05:05: EP1_plan_v2.md (laptop) is CANONICAL; EP1_beats_final.md just points to it. One canon check: for the 846 operation, use the anime/wiki figure for survivors (the wiki says "fewer than 200" / "about 100", so verify against Namu and use one number consistently on the counter).
- 05:03 USER (kick choreography, as in the anime): the Colossal lifts its RIGHT leg far BACK (a big wind-up, knee bent, foot high behind it), holds for a beat, then swings it forward and kicks through the outer gate. Keyframes: wind-up 1.5-2 s with the body leaning slightly forward and the left hand still on the wall; a brief hold; a fast forward swing of 0.4-0.6 s; impact; follow-through with the foot inside the gate; then the steam burst. The camera sees the wind-up from behind and the side, so the leg lift reads clearly.

## 05:58 UTC 10/24: USER STORYLINE FEEDBACK (binding, apply to EP1_plan_v2.md)
Liked: everything up to Grisha's injection and the key necklace.
Order and contents to change:
1. After the 250,000 operation: the trio join the cadets → Eren hanging UPSIDE DOWN on the balance rig (back in) → 3-year time-lapse → graduation.
2. Trost wall top: Eren in a confident "I can do it!" pose on the cannon rail → LIGHTNING → the Colossal instantly reappears behind him.
3. After Eren is eaten → cut to the supply HQ: show the hopeless situation (cadets stranded, out of gas) → Mikasa falls (out of gas) → the Attack Titan appears and attacks titans.
4. Then Armin's HQ lift plan → HQ retaken → quickly show Eren emerging from the titan's nape → quick cut to the cannon being fired → Eren's partial titan blocks the shot → Armin in the "Shinzou wo sasageyo" salute giving a fast speech.
5. Trost EVACUATION (core content of this channel): aerial view of the whole district. Crowds are jammed at the escape route (inner gate) because a merchant's cargo wagon blocks the gate → Mikasa forces it through → the crowd flows out. Animate the flow (crowd sim), seen regionally.
6. FORMATION: Erwin fires the signal flare from the centre and the WHOLE formation moves in response. The flare → movement cause and effect must be clear.
7. FOREST approach is extra important: from the sky, characters move CONTINUOUSLY in real time with no teleporting, so the viewer can TRACK their positions. Teleports only where unavoidable.
8. MASS Survey Corps sorties seen from the air: keep it cheap, with cloaks clearly visible. Soldiers ODM-move, fight titans and get eaten, seen from a distance.
9. Eren vs Female: the Female's kick sends Eren's titan head flying → straight into the Female's mouth open, Mikasa and Levi grab Eren and flee.
Implementation hints:
- Character tracking: persistent tiny HUD markers (a coloured dot plus a name in Pirata One with a leader line, the benchmark's label style) on Eren, Mikasa, Armin, Levi and Erwin whenever they are small.
- Crowds and soldiers: instanced low-poly figures on paths (geometry nodes or particles along curves), with cloak colour as the main read.
- 06:00 USER APPROVED name tags: persistent small HUD labels (coloured dot, leader line, name in Pirata One) for Eren, Mikasa, Armin, Levi and Erwin (add Hannes, Carla and Pyxis in their own scenes) whenever the character is small on screen. Fade them out when the character is large or off screen.
- 06:01 USER asked for a few OPENING screenshots. Please push 4-6 frames of the current opening one-take (tree wake-up → lift-off → inner-gate pass → Colossal rise → kick wind-up/impact) as JPG to renders/laptop/opening_sheet_*.jpg.
- 06:05 cloud review of renders/laptop/opening/ 01-05:
  1) 01_tree_hill uses the OLD huge blue bellflowers. The user rejected those at 17:46 and later called the round-3 opening "very good". Use shot_opening.py round 3 look (painterly flowers, god-rays, the user-praised version; see plans/3d_timelapse/design/opening_seq/tree_wakeup_r3.jpg) for the tree segment. There is also a crenellated tower on the wall; AoT walls have no merlons or towers.
  2) 04/05 show Shiganshina as a ROUND/OVAL ring. Canon and the user ref is the elongated U district attached to Wall Maria (district.py U layout, as in T2_best.png). Please use district.outline().
  3) 03: the Colossal head is only a few pixels. Raise the camera a bit and/or slow down near the wall so the head reads (about 10-15% of the frame height without a close-up).
  4) 05: the smoke columns and the debris read well.

## 06:10 USER STYLE REFERENCE: ref/user/style_tiny_figures_walltop_ref.png (S2 frame)
THIS is the target staging for character beats: a high oblique aerial with people VERY small, yet a viewer who knows the scene can tell who and what from the composition (group shape, where they stand, props, the cloak colour, one distinctive element). Apply it to every character beat (with name tags when needed). No close-ups.
The same frame is also a WALL-DETAIL reference:
- A wide flat wall top with TWO rail tracks running along it, a small rail cart, and cannons at the edge.
- The wall face has large CURVED BUTTRESS ribs flaring at the base on that side, plus slab segments.
- Pale grey stone, soft haze, conifer clumps scattered on the plain.
- 06:11 USER: the Colossal's steam in 05_after_kick looks like a CLOUD (a flat puffy disc). They want thin, creeping, wispy steam/haze rising off the body ("스멀스멀한 안개"). If that can't be done well, REMOVE it.
  Suggested method: a Mantaflow gas sim with the Colossal's mesh as a SURFACE emitter (low surface emission, high-frequency noise and vorticity, upward buoyancy, fast dissipation of about 20-40 frames, white with low density). Bake it at a low resolution, since the camera is far away. Alternative: animated Volume Scatter with 4D noise masked by distance to the body, scrolling upward. Show the user a 3-frame test before adding it to the sequence. If it still looks like a cloud, remove it.
- 06:12 USER: zoom in a lot for the Colossal (an exception to the no-close-up rule for this moment). (a) The head rising over the wall must read clearly: use a long lens / big zoom from the town side so the head fills a large part of the frame. (b) The kick must be clearly visible: frame the legs and the gate from behind or the side outside the wall. ONLY THE RIGHT LEG moves (lift back, then kick); the LEFT LEG STAYS PLANTED and still (no sliding or bending, foot locked with IK).
- 06:13 USER: wants an ANIME LOOK like the S2 reference (ref/user/style_tiny_figures_walltop_ref.png), WITHOUT heavy GPU load. Proposed Eevee look-dev (laptop only, since the cloud has no Eevee). Build aot/anime_look.py as a plug-in applied to every scene, then show a before/after on 2-3 existing shots:
  1. TOON SHADING: Shader to RGB → 2-3 step Color Ramp (lit / mid / shadow) multiplied with the base colour. Shadows are cool blue-grey, not black. Keep one soft rim band. Apply it to the walls, houses, titans and terrain via a material override function.
  2. PAINTED TEXTURES: Wit-Studio-style background paint. Low-frequency brush-stroke noise and a watercolor-like variation on the ground, walls and roofs. Grass is a flat painted texture with darker dab strokes, not geometry grass, which is cheaper too. Trees are clumps of dark conifer silhouettes, as in the ref.
  3. OUTLINES: Freestyle (silhouette + crease only, thin dark grey-brown, line thickness falling off with distance) or Line Art on characters and titans only, whichever is cheaper. No outlines on the far terrain.
  4. PALETTE AND ATMOSPHERE: desaturated, cool grey-green, pale stone walls; a world mist or depth-based haze (Mist pass in the compositor, cheaper than volumetrics); a soft overcast key light.
  5. COMPOSITOR: a gentle bloom/glare, slight lens blur on the far haze, a colour-grade curve toward the reference, and an optional subtle paper-grain overlay.
  6. Budget: the render time per frame must stay ≤ the current Eevee time + 30% on the GTX 1060.
  Show the user a before/after sheet before applying it to the whole sequence.

## 06:27 USER ANIME CAPTURES (ref/user/s1e1_*.png): use for the Shiganshina look and K1
- s1e1_plaza_aerial.png = THE town look target, and also the camera for the "people in the plaza" beat. High oblique aerial. HALF-TIMBERED (Fachwerk) houses: cream plaster with dark timber frames, stone ground floors, steep brown tile roofs with dormers and brick/white chimneys, a square bell tower. A bare DIRT plaza with cart tracks, the crowd as tiny dark figures, ivy and bushes in the corners. Warm golden late-afternoon light with long shadows. Our current plain stucco boxes must become this (texture plus timber trim plus dormers and chimneys; keep it cheap, mostly texture).
- s1e1_plaza_colossal_peek.png = the Colossal reveal framing from street level: the crowd's backs in the foreground, half-timbered houses mid-ground, and the wall with the Colossal's SMALL head peeking over it, smoke/steam rising behind. The trio from behind: Mikasa (long black hair, pale pink dress), Eren (brown hair, dark red top), Armin (blond bob, teal shirt). The user also asked to ZOOM IN on the head after this.
- s1e1_yeager_house_collapse.png = K1 Yeager house from a high top-down angle: a collapsed roof of terracotta BARREL tiles, broken beams; Eren and Mikasa pulling at the beams; Carla's red skirt under the rubble; a cobblestone lane, a rock, a timber-framed wall behind.
- s1e1_smiling_titan_carla.png = the Smiling Titan (long dark-blond hair to the shoulders, wide grin, slim) lifting Carla against a dramatic golden-sunset sky. In our sky view, keep this silhouette and backlit sunset mood.
- 06:40: the user asked about ready-made Paradis/Shiganshina/Trost assets. None usable: Sketchfab only has bare white wall shells (worse than ours). "Aot_4_shinganshina_stage_low_poly" (9169b1c3...) looks like a game rip, so DO NOT use it (licence risk). Plan told to the user: keep our terrain and walls; replace the town houses with free HALF-TIMBERED medieval house kits (CC0/CC-BY, commercial OK). Candidates: Quaternius Medieval Village pack (CC0), KayKit Medieval Builder pack (CC0), Sketchfab animau3d "Medieval House 1-4" (CC-BY, uids 0bbda345..., cf179aa6..., bc9272b7..., b4257899...). Retexture them toward ref/user/s1e1_plaza_aerial.png (cream plaster, dark timber, brown tile roofs, dormers, chimneys) and scatter/instance them in district.py blocks. Add them to CREDITS.

## 06:45 USER: "use character assets" — Sketchfab character shortlist (downloadable, commercial-OK licences)
Sheet: /mnt/project-files/plans/3d_timelapse/assets/sketchfab_characters_candidates.jpg
LICENCE WARNING: models named "Aotwa ..." / "AoT 4 ..." / "AoT2" (ianadrielbravo, damr.optimus2008, higuys920, fccc...) are almost certainly GAME RIPS (Koei Tecmo AoT games), so their CC-BY label is not valid. Avoid them, and re-check the Female (ianadrielbravo) and Smiling Titan rig choices too. Prefer fan-made originals:
- Survey Corps Soldier — yasirkhan98900.yk 1a80c768bed34443b275bcf0a33ae69a (Sketchfab Free Standard licence, commercial OK) → instance it for MASS soldiers (cloak read), recolour per regiment (Garrison/MP/Cadets).
- Eren (human, Survey uniform) — thespider768 329af28f90f54c24b71d93717c8e2c87; alt medothegeek 76c5cb021be84223ace3c7567dc0e1cc
- Levi — tksaet 41ba2beb495c423fa576580696994d63 (game-ready), alt philowang1999 854528a24d3447c5bc62cfe2eeb727a8
- Hange — ansaldotoys2 85744a3f9d7e4caeb1b3da503f883b33
- Mikasa — wanbeez 564f84b6c7644f6bb9753312c1c9a19f (Free Standard); check it's not a rip
- Annie (human) — alekcpyzov 06b0e94541044c7bab6e5353e99f02b1
- Attack Titan (Eren) — SHAIVS d1724e3f9d68424caeb23a1fd47b6468; animated alt valentinpelon777 7b69fee69bfc4351bb79625ffe128e29
- Props — Flare gun AlanShu bd6942625eed46eba418e6d42a7dc4f4 / carlosbarrera_10 0796ca1d1ce747ccaf30082207116bc8; Eren's key Kiit0 a5849aab036a4c88903681fe1a1caa85; ODM gear (elhafiedz from the earlier list)
Missing (build ourselves or kitbash from the soldier and kids): Erwin, Armin, Hannes, Carla, Grisha, Pyxis, the child trio (845). Characters are tiny in the sky view, so recolouring and re-haircutting the soldier base works for most of them.
- 06:46 USER OVERRIDE: "Aotwa" models MAY be used (the user accepts this). Pick by QUALITY. So the full ianadrielbravo/damr Aotwa set is usable (Eren, Mikasa, Armin? Levi rig, Annie, Reiner, Bertholdt, Hange, Smiling Titan rig, armored, female). Keep CREDITS.
- 06:46 USER: no model exists for the YOUNG (845) Eren and Mikasa. Make them from the Aotwa Eren/Mikasa: scale to child height (Eren 1.38 m, Mikasa 1.33 m), larger head ratio (~1/6), shorter limbs, and recolour the outfits to the 845 ref (Eren: olive shirt, long dark-red coat, charcoal trousers; Mikasa: white dress, pale-pink cardigan, red scarf, shoulder-length black hair). Hide the ODM gear and uniform parts. Fallback: our characters.py kids. Make sure they READ in the tree shot (contrast against the grass, outline).
- 06:47 USER: "AoT 4" models = SEASON 4 (final season) designs. They're allowed, but only for the later Season 4 episode, NOT EP1. For EP1, use the Season 1-era models (Aotwa etc.).
- 06:48 USER checked: the Aotwa Eren/Mikasa carry blades and ODM gear. For the 845 kids, REMOVE them: hide the separate gear objects, or delete those faces by material/vertex group, along with the uniform belts and jacket. The kids must show NO blades and NO ODM gear. Keep the gear for the 850 soldier scenes.
- 06:48 USER WANTS A COMPARISON SCREENSHOT, PRIORITY: render young Eren and Mikasa side by side. LEFT = current characters.py kids (make_eren/make_mikasa); RIGHT = Aotwa Eren/Mikasa (8c37798e8cfc4527a1b820b53d0b03b4, 20d55c7c03a447e2876212ef34cccc1b) shrunk to child size, with blades, ODM gear and belts removed and recoloured to the 845 outfits. Same camera: a front 3/4 at medium distance, plus one inset at the tree-shot distance. Push renders/laptop/kids_compare.jpg.

## 07:19 USER: the current kids look nothing like Eren/Mikasa. NEVER show a character's face to the camera. Agreed direction: LOW-POLY characters
- All human characters become stylised LOW-POLY figures (flat-shaded facets, matching the low-poly town the user liked). The head is a smooth or faceted shape with NO eyes, nose or mouth at all.
- Identity comes ONLY from the hair silhouette and colour, the outfit colours, and iconic items: Mikasa's red scarf, Eren's dark-red coat and brown hair, Armin's blond bob, Levi's undercut and cravat, Erwin's blond side part and green cloak, the Wings of Freedom on the back, the ODM gear in 850.
- Cameras frame characters from behind, high above or in profile; never a front view of a face.
- This replaces the Aotwa-kid plan for humans. Titan assets stay as they are. The Aotwa human models may still serve as proportion/hair references.
- Show the user a low-poly test (845 Eren + Mikasa from behind/above, then the trio + Levi + Erwin) before using them in scenes.

## 08:12 USER OVERRIDE: NO low-poly. Back to the existing (smooth) characters, faceless. PRIORITY: 480p INTRO TEST RENDER
- Low-poly is CANCELLED. Keep the smooth MPFB characters (characters.py), but with NO eyes/nose/mouth. Done on the cloud in 9a87ecb: `_faceless` now replaces the head with a smooth egg mesh (`<name>_head`); `hair_cap()` builds procedural anime hair.
  - Eren: shaggy schoolboy mop (학생머리, 더벅머리); a short maroon BLAZER (hip length), not a long coat.
  - Mikasa: straight black hair to the shoulders with bangs, per ref/eren_mikasa_845_outfits_ref.png.
  - `make_eren()`/`make_mikasa()` default to this. Preview: /mnt/project-files/plans/3d_timelapse/design/kids/kids_v2_faceless.jpg. Apply the same faceless and hair approach to every human (trio, Levi, Erwin, Carla...). If an Aotwa human is used, delete or cover its face the same way.
- **PRIORITY NOW (the user is waiting):** pull, then render the CURRENT OPENING one-take (tree wake-up → inner gate → main street → Colossal head → orbit → kick) as a FAST LOW-QUALITY TEST:
  - 854x480, Eevee, low samples (8-16), no motion blur, 24 fps; skip the anime-look pass if it is not ready.
  - Use the new kids from characters.py.
  - Encode H.264 (CRF 26) and push renders/laptop/intro_test_480p.mp4 (keep it under 50 MB). Also copy it to E:\YTP2\3D Timelapse\renders\.
  - Do not spend long on fixes before this render: the user wants to see it soon. List the known gaps in this file after pushing.
- The user says token usage is high: keep the work lean, with no extra exploration.

## 09:04 USER: the opening is TOO SLOW ("발차기까지 1분?? 타임랩스가??"). RETIME before the 480p test render
- The kick currently lands at seq frame ~1728 (~58 s). Compress the whole one-take so the KICK LANDS AT ~20-25 s. It is a timelapse: brisk drone moves, no lingering.
- Target beats at 30 fps: tree wake-up 0-4 s → rise and push through the inner gate 4-8 s → main street fly-through 8-11 s → Colossal head rises over the wall 11-15 s (the zoomed head shot stays readable, about 3 s) → orbit behind 15-19 s → wind-up and kick 19-22 s → steam vanish and titans pour in 22-26 s.
- Scale the T_* constants in seq_colossal.py and the flight.py opening keys with one factor (≈0.4) instead of hand-editing each one. Keep the kick wind-up/swing at real speed: do not speed up the leg motion itself.
- Then render the 480p test (same settings as above). A shorter cut also renders faster.

## 09:06 USER EXACT TIMING (supersedes the 09:04 beat list). Opening at 30 fps:
- 0-2 s (f0-60): Eren and Mikasa at the tree; at ~2 s the camera LEAVES the tree.
- 2-5 s (f60-150): a fast "swoosh" fly straight to the PLAZA full of people (s1e1_plaza_crowd_colossal_head.png framing).
- ~5 s (f150): the Colossal head starts to appear over the outer wall, seen from the plaza. Its HANDS GRIP THE TOP OF THE WALL, like the anime (fingers over the wall-top edge, both hands either side of the head).
- 5-8 s (f150-240): the head keeps rising until 8 s (camera zooms toward it).
- ~11 s (f330): the KICK. The right leg drawn back, then the swing, the outer gate shatters, stones fly and roll. The wind-up/orbit to the kick view fits in 8-11 s.
- After the kick: steam vanish and titans pouring in, briskly.
- The inner-gate pass and the long street fly-through are dropped; go straight from the tree to the plaza.
- Rework the T_* constants in seq_colossal.py and the flight.py opening keys to these frames. Add Colossal hand bones/pose (or hand meshes) gripping the wall top during the rise. Then do the 480p test render.
- 09:06 USER: "속도감은 생명이야" (pace is everything). Apply this to the WHOLE EP1, not just the opening: fast, snappy drone moves, short holds, no lingering. Holds only for the dialogue-overlay beats (Yamero ~2 s, vow ~3 s).

## 11:43 USER: test renders must be FAST (≤20 min). The 1.5 h 480p test was too slow.
- For every future preview: 15 fps (render every 2nd frame), Eevee lowest samples, cull off-screen houses/crowds/titans, use simple steam or none, 480p. If the estimate is over 20 min, simplify further before starting.

## 14:38 Cloud QA of intro_test_480p.mp4 (52d19d6), 1 fps contact sheet. Fix before the next preview:
1. ~6-8 s: the camera passes INSIDE geometry, so 2 seconds are dark/black (inside the wall or the ground). Keep the camera path clear of the wall and ground.
2. Head reveal: at 5 s, the plaza shot shows the gate street, but the Colossal head isn't readable. Make the head plus both hands gripping the wall top clearly visible from the plaza at 5 s (larger in frame), rising until 8 s.
3. From ~8 s, the Colossal is shown FULL BODY outside the wall, and it floats: its feet are off the ground and the legs dangle at 10-12 s. Canon: it stands on the ground and the wall reaches its clavicle. Snap the feet to the terrain, keep only the shoulders and head above the wall, and keep the left foot planted during the kick.
4. The kick at ~11 s reads as a knee-up hop, not a right leg drawn far back and then swung forward. Fix the wind-up/swing.
5. After the kick (12-17 s): good wide aerial of the district. Steam is off in this lite pass (fine for previews).
Keep the ≤20 min preview settings.

## 15:07 USER FEEDBACK (big). BASE = fast_test_prev.mp4, which the user loved, NOT intro_test_480p (v1). Keep its camera design: NO camera behind the Colossal's back ("너무 좋은 선택"). Then CONTINUE THROUGH TO JUST BEFORE THE GRISHA SCENE. Lore-accurate, fan-pleasing detail. Agents may be split.
Opening fixes:
1. Start: a VERY slow zoom-out (not a locked camera). Minimal animation. Eren does NOT stand up: he sleeps sitting against the tree, then slowly bends forward at the waist while seated (waking up). Mikasa walks slowly toward him.
2. Tree → Shiganshina gate flight: the field is too empty. Add grass clumps, a dirt road, scattered trees and bushes, naturally placed.
3. ~4 s: the camera move is unnatural. The speed jumps while it locks onto the Colossal. Ease in/out and keep a smooth velocity. ZOOM IN MORE on the head. The head's rise speed is GOOD; keep it.
4. Colossal hands: its LEFT palm must GRIP the top of the wall (fingers over the wall-top edge). Its RIGHT hand grips the wall top a little later.
5. Arrival: yellow-orange LIGHTNING strikes, the screen briefly darkens, and the camera SHAKES.
6. Kick: OK ("낫밷"), but the foot goes far too high. The real kick lands at GATE height. Only the gate opening breaks, not the wall around it. Make the flying stones SMALLER and give them more in-between frames so they fly smoothly. Final renders at 30 fps; previews may stay at 15.
7. Falling stones hitting houses: show dust/smoke bursts and the houses collapsing progressively, not a 1-frame swap from intact to ruined (that is how it works now).
8. After the kick, the user says it's very well done (Carla being eaten included). Keep it from getting boring (pace rule).
Loved (keep): the sunset with Shiganshina burning, and the plaza people as colourful, clearly visible, very MINIMAL simple figures.
New crowd/titan sky-view system (the same minimal style):
- Before: a big crowd gathered in the plaza. After the houses are destroyed: people fleeing everywhere.
- Then many minimal titans (simple, animation-friendly): they eat residents, residents flee to the BOATS (canal ferry) and to the inner gate, titans scatter and wander chaotically after eating. Built to read from the sky view.
Scope: everything up to just before the Grisha injection scene (845 fall → ferry/vow → refugee camp/Maria evacuation as in EP1_plan_v2). Follow the pace rule, faceless characters, ≤20 min previews per segment; push previews and stills for review as segments finish.

## 15:51 USER: total EP1 length 8-10 min MAX
- The full EP1 cut (EP1_plan_v2, planned ~14 min) must land at 8-10 min. Trim the holds and data shots proportionally; keep the pace rule. The fall of Shiganshina up to just before the Grisha scene stays at about 50-60 s.

## 16:58 USER: opening v3 "훌륭하다, 너무 훌륭하게 잘 해주었어". GATEHOUSE FIX (ref/user/s1e1_gatehouse_flat_ref.png)
- The current gatehouse sticks out too much and has crenellations. Per the anime, the gate section is FLUSH with the wall: two shallow vertical pilasters/buttresses (barely projecting, ~1-2 m), rising slightly above the wall top as flat, square-topped stubs. Between them sits a flat recessed panel with a row of small rectangular vent slots near the top. NO merlons, NO battlements, NO tower block. The wall top elsewhere is plain and flat, with faint vertical segment lines.
- This also fixes "the head is hidden behind the gatehouse".

## 17:01 USER: BUILD STRAIGHT THROUGH TO THE END OF TROST in one go. "No slacking; focus on detail; manage the agents."
Scope: EP1_plan_v2 beats 1-20 (title map → 845 fall → Grisha injection/key → refugee camps → 846 operation 250,000 → ~100 → 847-850 training/graduation → 850 Trost: Colossal returns → titans flood → Eren eaten → supply HQ → rogue titan → Armin's plan → Eren emerges, cannonball near-miss, Armin's salute → Pyxis → boulder operation → Levi, Marco, pyres). Budget for this part ≈ 4:30 of the 8-10 min EP (845 ≈ 55 s, 846-850 ≈ 35 s, Trost ≈ 2:45, title/bridges ≈ 15 s).
User's 05:58 Trost storyline is canon for the order: Eren "I can do it" pose on Trost's wall → lightning → the Colossal behind him; Eren eaten → HQ despair → Mikasa falls → the Attack Titan kills titans → HQ lift plan → retaken → Eren out of the nape (quick) → cannon → partial titan blocks it → Armin's quick speech in salute pose; the Trost evacuation with crowds jammed at the gate by a cargo wagon until Mikasa clears it (crowd-flow aerial).
Agent split (laptop):
 A) Shiganshina 845 finish (segments 2-4 + Grisha forest glitch).
 B) Interlude 846-850: refugee camps, the 250,000 march with counter, training camp seasons, balance rig (Eren upside down), graduation.
 C) Trost district build: Trost's own layout (a square district on Wall Rose's south side, gates, the supply HQ, the bell tower, the boulder by the breach), reusing the gate/house kits.
 D) Trost action: swarm titans, cadet squads with ODM (cloaks visible from the sky), the Attack Titan, flares (red/yellow), cannons, the boulder carry, pyres.
 E) Graphics: HUD (place/year/'Eren, age N'), map/counters (250,000→~100; titans inside; Trost dead), name tags (dot + leader line + Pirata One).
Rules: pace, faceless figures, minimal colourful crowds and titans for sky views, no camera behind the Colossal's back, flush gatehouses, ≤20-min 480p 15 fps previews per segment, push stills and a short note per segment. Integration agent: one continuous flight with eased transitions between segments.

## 17:41 USER: NO GRAPHIC CUTAWAYS. ONE CONTINUOUS CAMERA TAKE. The 250,000 march is THE key 3D scene.
- The whole EP is ONE continuous 3D camera take. Graphics must NEVER cut away from or interrupt the 3D (no full-screen map shots, no parchment title map replacing the 3D, no map transitions). The user: "그래픽으로 얼렁뚱땅 하고싶지 않아".
- Graphics are allowed only as small, well-placed OVERLAYS on top of the live 3D sky view, at the right moments: e.g. the "land lost / Wall Maria" inset over the sky view of Shiganshina burning; the HUD (place · year / Eren, age N) and the name tags stay. The title can be a text overlay on the opening 3D shot, not a map.
- Bridges between places: the camera physically flies (climb high over the walls/land and descend), never a map cut.
- 846 "retake Wall Maria" operation = THE MOST IMPORTANT, differentiating scene, done fully in 3D: a sky view of countless people (250,000) pouring out of Trost's outer gate in a vast column across the plains; titans converge, attack, hunt, encircle; the column is swallowed and vanishes. The counter 250,000 → ~100 may run as a small overlay ON this 3D shot. Give it real scale (instanced crowd, tens of thousands of visible agents, LOD), and give it enough screen time (~15-20 s) inside the pace budget.
- graphics_title_map.mp4 / graphics_counter_march.mp4 as full-screen shots are CANCELLED; reuse their elements only as overlays.

## 04:53 (10/25) USER: all people TRUE scale; aerial view from the Colossal to Eren's titan in Trost
- Every human is true scale (~1.6-1.7 m), the same size in every frame. No readability upscaling of people (the 2.5x Trost figures on the wall top looked absurd). Titans keep true heights. Readability = camera distance, colour cues, lighting, name-tag overlays.
- Trost: after the Colossal appears/kicks, the camera goes AERIAL (sky view) and stays aerial through the flood, Eren eaten, the evacuation, HQ and Mikasa, until the Attack Titan's lightning arrival.

## 08:02 (10/25) PAUSED by the usage-limit rule. Where every agent stopped (laptop)
Rules now in force: AGENTS_BRIEF.md, true-scale people (04:53), Trost aerial stretch (04:53), one-take, New Rocker/Russo One/Share Tech roles.
- Opening (render_fast.py): LOCKED (v4 + zoom ease + thicker fingers). Preview renders/laptop/opening_preview.mp4.
- A, Shiganshina (render_fall.py, render_fall2.py, seq_carla.py, swarm845.py): seg 2 done (fall_preview.mp4, Carla high hold in code); seg 3 done (fall3_preview.mp4). Asked at 04:53 (in progress, maybe partly applied, unverified): CARLA_HELD_SCALE default 1, kids unscaled, SWARM_PSCALE 1, hudcam.dump trackers, segment 3 vow fixes (closer camera, refugees on the ferry, warm light in the breach). NEXT: seg 4 (night pull-up, burning town, Maria lost; Eevee + smokecards, no volumes), seg 5 (Grisha forest), a camera flight seg4→seg5 (no 5 km jump, no grey-belt mask pop).
- B, interlude (render_interlude.py): done; true scale applied; pine-free cut-out strip and darker smoke in code, not yet rendered.
- C, Trost integrator (render_trost.py, trost.py): parts 1-3 rendered (renders/trost/trost_part{1,2,3}.mp4; part 3 is pre-true-scale). NEXT: TA_PSCALE=1, AERIAL camera from the Colossal to the Attack Titan's arrival, hudcam.dump trackers (Eren, Mikasa, Armin, AttackTitan via TA.hero_pos), part 2 fixes (lift plan 6-7 s, emerge/cannon/salute in cannon_square), then re-render parts 1-3.
- D, Trost action (trost_action.py, odm.py, flares.py, smokecards.py): done except: true scale default (asked at 04:53, check odm Squads pscale), the cannon_square site key (default inner-gate square near (-140, -40)). A stills job of D's (render_trost_action.py, Eevee) may still be running at pause time.
- E, graphics (hud2.py, hudcam.py, maps.py): done.
- F, march846: done (v2); true-scale change asked at 04:53 (remove far 3.3x / stragglers 2.6x / titans 2.6x), code state uncommitted at pause, unverified. NEXT: 3 check stills; lower the high camera keys if the column vanishes.
- G, integrator (master_timeline.py, render_bridge.py/.sh, assemble_master.py, master_overlay.json): first master preview 3:15 (renders/laptop/master_preview.mp4). NEXT: when segments are final, re-run render_bridge.sh (if seam keys moved) then assemble_master.py; moonlit fill for B4's dark climb; check the Trost dead figures (207/897) before the final.

## 09:37 (10/25) RESUME — big user review of master_preview (all of it is binding)
User: "진격거 계속 진행해." Work resumes on the subscription (not the API session). Run at most 2 agents at a time.
Refs added: ref/user/walls_map_ref.png, remove_red_cape_giant.png, trost_cannon_canal_ref.png, trost_armin_salute_steps_ref.png, eren_halfshift_skeleton_ref.png.

CORE PHILOSOPHY: a neutral third-party observer watching calmly from the sky, as if not knowing the protagonist. Sky view at a moderate height, NO dynamic chase cams. "That's the charm of a timelapse."

ONE TAKE, STRICTLY: NO cloud transitions, no wipes, no cuts. Separate renders are fine ONLY if the camera position/velocity match exactly at each seam. The camera physically flies Shiganshina -> north across Wall Maria territory -> Wall Rose / Trost. The GRISHA forest scene is CUT.

WORLD MAP (walls_map_ref.png): three concentric walls, each with 4 semicircular districts bulging outward (N/E/S/W), a river running N-S through all, grass/forest. Shiganshina = south bulge of Maria; Trost = south bulge of Rose. ONLY Shiganshina and Trost get buildings; the other districts are empty wall bulges (save memory). NO mountains behind the Colossal; far beyond the walls (south) the SEA should be visible at the horizon.

OPENING / SHIGANSHINA:
- Remove the bottom-left 3-walls graphic at the start.
- Lightning a bit EARLIER.
- Eren's house: near the broken gate, placed to the RIGHT of the outer gate so the titans pouring in are visible.
- Carla: REMOVE Hannes carrying Eren & Mikasa (harness, Eren, Mikasa gone from this beat). Smiling Titan grabs and eats Carla FASTER. Show it small from the aerial view.
- ARMORED TITAN: the inner gate must be INTACT first (it currently looks already broken). Model a real gate; the Armored Titan rams it with its SHOULDER; show the gate exploding vividly.
- Boats: Eren on the boat looks awkward -> high aerial view of boats and refugees fleeing north toward Trost, and the camera moves on toward Trost with them (this replaces the vow close-up).
- KEEP: refugees clearing fields (food shortage).

250,000 MARCH: user's favourite ("너무나도 좋았어"). Keep it, but remove the transition into/out of it: connect by matched camera.

TRAINING CAMP: good, but place it RIGHT NEXT TO the Trost district so the one-take move is easy.

TROST:
- Remove EVERY custom red-cape giant figure (remove_red_cape_giant.png): use ONLY downloaded asset models (small true-scale ones are fine, keep those). Same for the oversized Scout figures at the evacuation.
- Outer gate smashed, titans pour in FAST (show clearly).
- SKIP Eren being swallowed and similar close beats.
- Aerial: people evacuating, crowd concentrating at the inner gate, the huge cargo cart blocking it; Mikasa flies in, (brief exchange), the cart gets shoved aside, people escape out through the gate. Make the inner gate an OPEN passage (no closed door visible).
- Aerial: Mikasa falling seen a little; a titan approaches; the Attack Titan appears, runs in and beats the titan. Follow Eren HIGH, aerial, spectator style.
- HQ: rebuild the supply HQ to match the anime (stone multi-storey building with a tall bell/clock tower, orange tile roofs, dormers, half-timbered wings; see trost_armin_salute_steps_ref.png background; search wiki stills "Trost District Headquarters / supply depot"). The lift operation: titans slowly gather to the centre, cadets ring them, FIRE the guns, then cut the napes. Then show Eren emerging from the Attack Titan's nape (use the asset; remove his ODM gear and blades if possible).
- CANNON (big camera move across the district): in a sunken canal/river-side stone basin inside Trost (trost_cannon_canal_ref.png): Garrison soldiers on stepped stone banks surrounding Eren/Mikasa/Armin; the cannon fires; Eren half-shifts (skeleton ribcage + arm + skull, eren_halfshift_skeleton_ref.png) and blocks it; LOTS of steam/smoke afterwards. Caption: "Eren blocks the cannonball" (not "Armin vouches"). Armin's salute staging per trost_armin_salute_steps_ref.png (steps, soldiers around).
- Then Pyxis's speech, then THE MOST IMPORTANT: Eren carries the boulder and seals the broken outer gate. Spend the most effort here.

## 10:20 (10/25) HQ refs + full S1 anime on the laptop
- HQ (supply HQ) refs from the user: ref/user/trost_hq_keep_front_ref.png (front: a tall square pale-sandstone KEEP, crenellated parapet, two square corner turrets with slate-blue pyramid roofs, a row of 7 arched windows, a taller central block behind; flat paved roof walk with crenellations around) and ref/user/trost_hq_distant_towers_ref.png (seen from afar: crenellated block with a small bell turret on top; surrounding district has stone towers with mansard roofs and orange tile roofs). Build the HQ from these.
- The user put the whole AoT Season 1 anime in E:\YTP2\3D Timelapse. Use it as REFERENCE ONLY (never put anime footage into our video). Keep it lean: extract low-fps keyframes (e.g. ffmpeg fps=1/2, 480p) only for the episodes/scenes you need (Shiganshina ep1-2, Trost ep5-13: outer gate breach, evacuation + cart, HQ, cannon canal, Pyxis, boulder), save contact sheets under ref/anime/ (not committed if large; .gitignore the frames, commit only small sheets), and match layouts, building shapes, gate design, staging and timing.
- 10:22 HQ addendum (ref/user/trost_hq_warehouse_wing_ref.png): the crenellated keep (with the clock/bell turret on top) is JOINED to a long, tall 4-5 storey sandstone WAREHOUSE wing: steep dark-slate gabled roof, small square windows in regular rows, a few arched windows on the ground floor, pilaster strips on the gable end. This warehouse is the supply storeroom of the lift operation (the cutaway goes in this wing).

## 13:39 (10/25) USER RULE: Carla beat staging
- The Yeager house is well to the RIGHT of the outer gate (several blocks away), not beside it. First show the titans pouring through the breach, then the camera travels right (smooth aerial) to the Yeager house, where the Smiling Titan eats Carla. NO other titans near the Smiling Titan in that shot.

## 13:40 (10/25) USER RULE: Armored Titan ram animation
- The Armored RUNS straight at the inner gate, facing forward, normal run cycle. Only in the last ~0.4 s before impact it drops its shoulder and leans into the hit like a rugby tackle (torso twists ~30-40°, shoulder leads, head tucked, legs keep driving). Never rotate the whole body sideways.

## 15:29 (10/25 UTC) USER: the Trost boulder is a near-perfect ROUND ball-like rock (as in the anime), huge (larger than the houses, ~12-15 m), not a craggy lump. Plus 13:49 QA (pending, agents paused by the usage limit): HQ warm sandstone with block texture and DARK slate warehouse roof (only turret roofs slate blue-grey); cannon basin old stone texture with damp darker lower walls and moss streaks, visible step edges; Trost roof colour variation.

## 15:37 (10/25 UTC) USER PICK: Armored Titan model = Tripo image-to-3D (D)
- assets/tripo/armored_img/tripo-out/armored-ref-crop-png-rig-1ad3b89b/model.glb (from the user's figure photo, rigged; imports facing sideways). Used at true 15 m. Other titans stay our own procedural ones unless the user says otherwise.

## 00:44-00:46 (10/26 UTC) USER: Shiganshina v3 fixes + toon choice + cart
- Toon: option "reduce orange and apply" (toon shader project-wide, less orange).
- Yeager house: to the LEFT as seen from the Colossal (opposite side of the outer gate), several blocks away; pour first, then the camera flies LEFT to Carla + the lone Smiling Titan.
- Camera: smooth ease in/out; pull back over-zoomed shots to the moderate neutral sky observer.
- Armored ram: refugees freeze/flee; Garrison fights him (wall cannons firing, impacts bouncing off his armour, soldiers on the ground/wall); he is UNSTOPPABLE, keeps running, shoulder-rams only at impact (never rotate the whole titan). Keep the framing locked on him.
- Trost evacuation: the cart is only shoved a little to the SIDE to clear the passage; it never drives through the gate.

## 00:49 (10/26 UTC) PAUSED by the user (credits). Where things stopped
- Toon (less orange) is the default in every render script (2f8208d). Cart shove fix is in trost_action.py.
- A (Shiganshina): was starting the 00:44 fixes (Yeager house to the LEFT, camera ease/pull-back, Armored vs Garrison cannons + fleeing refugees, framing locked on him). Partial edits may be in render_fall*.py (committed as WIP below). NEXT: finish, then render fall + fall3 + the opening with world + toon.
- C (Trost): NEXT: full Trost re-render with toon: the side-on boulder carry, thinner breach dust, the cart shove; plus a toon before/after still.
- G (integration): NEXT: connectors C1-C3 and the march with toon, then assemble_master.sh for the full one-take preview.

## 10:52 (10/26 UTC) OWNER: length = TIGHT 7:02 cut, every scene kept ("7분, 장면 모두 유지") - FINAL
- SEGMENTS locked to SCENE_BIBLE_v2 A1 tight column: g1 32.0 · g2 32.0 · g3 78.4 · g4 20.0 · g5 70.0 · g6 69.5 · g7 45.0 · g8 75.0 = 421.9 s.
- One-place re-time: aot/segtime.py (A1 table); each seg module keeps its beats in one table.

## 11:00 (10/26 UTC) RESUME (laptop): implementing SCENE_BIBLE_v2 section D, multi-agent (max 3, Opus for camera/layout, Sonnet for bulk)
- Side job done: analysis/ep05_a.mp4 + ep05_b.mp4 (ep05 split at 12:03, -c copy), in E:\YTP2\3D Timelapse\analysis\ (reference only).
- Wave 1 running: (1) camchan.py/segtime.py/camkeys.py + master_timeline A1/A2 (D1); (2) trost.py rebuilt to section C (D10, 25, static parts of 12-17, 27, 28); (3) g8 boulder via the new generic driver render_seg.py + seg_g8.py (D16, 17, 29, 30).
- Order after that: g5, g1, g2, g6, g7, g4, g3, then the master assembly. Contracts: AGENTS_BRIEF.md "WAVE v2".

## 11:38 (10/26 UTC) USER: Armored ram details
- He smashes the inner gate with his RIGHT shoulder (not the left; render_fall2.py currently says "left shoulder leads": flip it).
- After breaking through, his speed carries him into a long forward SLIDE (feet skidding, dust furrows, rubble ploughed ahead) before he stops and straightens. Bible g2 updated (slide to y ≈ +45, 13.5-16 s).

## 13:40 (10/26 UTC) Cloud QA of trost_set_v3 -> routed
- g8 agent (may edit trost.py for these only): seal shows the ball wedged at the base of the Λ plug (low dark skirt, no pink rubble); breach front = broken dark timber beams + roots instead of black bars; Trost walls warm beige #CEC3A6 + damp mossy lower 6-12 m #6f6a58 + pilaster shading; ball contact shadow + dust ring.
- g1 agent: the same wall look on Wall Maria/Shiganshina.
- OPEN for the world/master pass: the ground around Trost is flat bare green; add gentle hills, tree clumps, fields (walls dominant).

## 14:20 (10/26 UTC) OWNER: music and Eren's voice etc. are added by the owner in the edit
- Our renders stay silent (no music/VO/SFX tracks); keep the short overlay holds so the owner can place lines there.

## 15:4x (10/26 UTC) g1 v1 rendered (render_g1.sh, renders/g1/) -> lead QA: NOT shown to the owner yet
- The Colossal is unreadable at the bible K4-K5 distance (500-690 m, head 1-2% of the frame), the kick is invisible, 4-6 s is mostly sky, and 22-32 s is near top-down at 52-57° pitch (bible keys break A3). Rework sent: head 10-15% of the frame (owner 06:05/15:07, within 00:44 "no over-zoom"), pitch 30-42° for Carla, pour visible, terraced rows. SEAM_IN may move (g2 not built yet); camkeys/segtime/render_fall2 must stay consistent.

## 15:25 (10/26 UTC) USER: cannon basin water is on the LEFT (owner capture = anime ep09 F09/000028171)
- Seen from the Garrison bank looking at Eren's group and the wall, the canal + barred water gate must be on the LEFT. v3_basin had it on the right because g7 mirrored the anime basin N-S into Trost.
- Cloud ruling: build the basin at its ANIME position, on Wall Rose's NORTH face beside the canal water gate (Y' = 1740 - Y for every basin element; floor X 340..385, Y 875..907). See SCENE_BIBLE_v2 g7 "CORRECTION". Re-key g7 0-19.5 s on the north side. A few basin buildings north of Rose are an allowed lore exception.
- (Lead had first proposed rotating the basin east of the canal; superseded by this cloud ruling.)

## 16:5x (10/26 UTC) Orientation audit (workflow, 21 agents: Sonnet audit + Opus verify vs the anime frames)
- 8 confirmed items, recorded in SCENE_BIBLE_v2 D "AUDIT CORRECTIONS" (they override older text): g1 canal-east note; g2 smoke bends WEST; g2 hamlet east-heavy; pit bridge NNE; g5 punch travels south (CAP into the west alley wall); RoseHQ lift at (-195,870); YF on the east plank box (22,52); g8 sun swings 255 -> ~200 deg during the carry.
- Routed: g8 agent (YF, sun, pit bridge, RoseHQ lift in trost.py), g5 agent (punch), g1 agent (hamlet). g2 smoke goes to the g2 build.

## 16:51 (10/26 UTC) OWNER on g8 v1 ("너무 좋은데? 오히려 먼게 좋아") - binding for ALL segments
- FAR camera preferred everywhere (it hides small flaws); readability only via small cues (rim, steam, dust), never by pushing in. The closer-camera v2 plan is cancelled.
- ODM: ONE hook per shot; the hook flies to an anchor (0.15-0.25 s, hip gas puff), the wire goes taut, the soldier is reeled along it (white gas trail, slight swing), then release/retract. No hanging or twin wires. Implemented in odm.py (g8 agent), used by every segment.
- Plug = ONE instant slam after the roar (0.3-0.5 s), big dust burst + short camera shake (0.3-0.5 deg, 0.4 s), then the slump.
- Breach hole = ball-sized (14-15 m wide x 15-16 m tall, round broken top); bible C updated; trost.py by the g8 agent; g5's kick reveals the same hole.
- Push every render immediately, version-labelled (renders/laptop/<seg>_<name>_vN_*).

## 16:53 (10/26 UTC) OWNER: remove the decoy corner D completely ("저기 구석에만 있는게 어색하므로 다 빼자")
- No titan mass, decoy soldiers, cranes or mop-up props at D (NW pocket). Mop-up stays near the gate square. Bible g8/C rows D and the "decoy" must-haves are void.


## 18:10 g1 v3 fix list (coordinator cloud QA of g1_fall_v2) — QUEUED, start after g8 v2 + g5 v1 are pushed
1. Town density (main flaw): continuous terraced rows with shared walls, narrow lanes, the avenue as the only wide gap, rows right up to the wall foot (ref ep02_000007498, ep01). Cobble/dirt variation between rows, no flat grey void.
2. Smooth the 6.5 s whip to under 150 m/s.
3. 22-32 s: slow drift/orbit at 3-5 m/s, staying far. Keep the g1->g2 seam (-254,-468,95) at rest so g2 keeps matching.
4. P2: gate dressing and wall-top cannons.
Keep the far camera.


## 19:09 g5 v2 fix list (coordinator cloud QA of g5_trost_v1) - QUEUED: resume the g5 agent as soon as g2 finishes; g5 v2 gets GPU priority over g6 and g1 v3
1. Steam at 9-17 s: white/light-grey billowing steam that rises, spreads and thins over ~4 s. No blue blob.
2. Pour visible from 12 to 30 s: 20-35 titans of mixed sizes stream along lanes L1-L5 up the avenue and the ring road. Warmer skin plus a contact shadow. Keep a few in frame during the turn toward the HQ.
3. Abnormal: charges up the open avenue EVS with a dust cloud. Mikasa kills it at about (-85,782); it skids prone to (-96,794) at the crowd's south edge while the crowd recoils. Drop the roof-hop or land it in the open. "MIKASA" tag in Russo One with a leader line at 33.8-39 s and 50-54 s; no merchant tag.
4. Crowd: colourful, saturated clothing (ruling E2), a 4-6 m gap behind the cart, and the drain eased in and out.
5. Alley 46-62 s: C8/C9/C9' looking SOUTH from about 230 m N and 150 m up. Lower or remove 2-4 blocking houses. The AT must read clearly.
6. ODM: wires of 35 m or less to nearby anchors, thin light grey, removed on arrival (no ~100 m black lines).
7. Remove the brown disc on the small square; use a small stone well if a feature is needed.
Push g5_trost_v2_*.


## 21:18 g2 v2 fix list (coordinator cloud QA of g2_armored_v1) - QUEUED: after g5 v2, before g7 renders. Resume the g2 agent when a slot frees.
1. A real breach: a tall narrow arch 12-14 m x 24-26 m through the full wall thickness, the wings survive, and you can see through it both ways (ep02 10:22.2, 10:45.6).
2. He visibly bursts out of the north face and slides to y≈+45 (furrows, skidding, rubble ploughed ahead, right shoulder forward), then straightens and steams in thinning haze at 18-23 s (ep02 10:35.7). K5-K6 high enough to see the north side.
3. Dust: a lumpy ochre ball bursting mostly NORTH, dense for ~1 s, readable again by 17-18 s. Chunks fan north, 6-8 of them above the wall top.
4. Framing (owner 00:44, "갑옷거인에게 포커싱"): K1-K4 closer so he is ~100-120 px tall (~1/4 of the frame height), centred, front or side three-quarter, never behind. This is the ONE exception to the far-camera default. Speed and yaw limits still apply.
5. Defenders and refugees must read: 6-gun battery with crews, flashes and white smoke; wall guns; a gold ricochet off his face at 9.15 s; crews scatter at 12.4 s; carriage kicked at 12.8 s; ~150 stragglers flee, ~10 freeze.
6. Cracks: thin dark-grey branching cracks radiating 15-30 m from the hole edge.
Push g2_armored_v2_*.


## 22:06 g5 v2 PASS (cloud QA). No g5 v3. Polish to do in the assembly pass:
1. Mute the crowd colours 30-40% toward earthy medieval tones (browns, beiges, muted reds, blues and greens; ruling E2).
2. Add 6-10 larger titans (8-15 m) walking up the main avenue and the ring road at 14-24 s, so the flow reads at the far camera.
GPU order: g6, g7, then g2 v2.


## 22:34 g6 v1 PASS (cloud QA) - fixes sent to the g6 agent (code + stills, no re-render): steam shroud instead of the ball at 46-52 s; EREN/MIKASA tags (g6_tags.json); clean roof fade plus a warmer storeroom interior.

## 23:03 g7 v1 PASS (cloud QA). Assembly-pass polish:
1. North of Rose: farmland patchwork, dirt roads and tree lines matching the g1/g5 terrain. No buildings except Pyxis's forecourt (E3).
2. Forecourt crowd: Garrison brown/beige jackets in loose rank blocks so the ~2,000 read as a formation.
3. Tags in Russo One: EREN/MIKASA/ARMIN at ~9-16 s, then PYXIS from his arrival through the speech. At most 3 at once, each fading after ~4 s (from seg_g7 TRACK).
Queue: g2 v2 -> g4 -> g3 -> connectors -> full one-take preview.


## g6 QA fixes landed (code + stills, cd seg_g6.py, graphics_timelines/g6_tags.json). renders/g6 frames are OLD: re-render g6, then run hud2 g6_tags.json BEFORE the master assembly.
