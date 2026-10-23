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
