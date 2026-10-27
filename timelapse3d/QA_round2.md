# QA round 2 (autopilot self-QA, 10/28)

## Part 1 (master_onetake_v3, 3:20)
- [~] Total 3:20 < 3:30 target -> slower KEY moments only (segtime TMAP): g3 march 1.6, g5 head 1.0 + punch 1.3, g6 lift 1.5 /
      blond titan 1.3 / rise+hug 1.4, g7 volley 1.3, g8 slam 1.4 + herd kill 1.3 -> 3:30.5. Renders g3 v9, g5 v7, g6 v5, g7 v4, g8 v6.
- [~] g3 v9: nights readable except a 1 s near-black dusk after the march -> DUSK2 elev 2->6 (next g3 render).
- [ ] g6: long static stretch on the HQ square (~30 s same framing) -> check after v5 whether to tighten.

## Part 2-3
- (after chain_qa1: f1 v2, f3 v2, s1 v2, s2 v2 reviews)
- [x] g5 v8: head hold ~2.5 s, AT sprint/punch zoomed (68 mm) and readable.
- [x] g6 v6: zooms at the blond titan (56 mm) and Eren/Mikasa (50 mm); still far by owner choice, acceptable.
- [x] s1 v3: Female rise, Plan C harpoon pin and rampage readable at ~85 m.
- [x] f1 v4: Female + riders readable, no slab trails, textured plain, smoke-column flares (purple drifts).
- [x] s2 v3: chase readable (~0.55x distance), crane above the roofs, face ending holds.
- [~] f3 v3: Blender crashed repeatedly at 480p in the dense forest (GTX 1060) -> 234 unique of 755 frames (duplicates = 'frozen'); glossy swamp = blue disc -> v4 at 640x360 (as v1), swamp = dull mud.
- [~] f3: ROOT CAUSE of the "frozen" f3 v3/v4: grazing views across the canopy put thousands of trees in the frustum -> GPU
      time over the Windows driver timeout -> Blender died at t 4.5 / 20.6 (gaps filled with duplicates). Fix: camera far clip
      900 m for 3.6-46.6 s (stills 4.6 / 12 / 20.7 OK), crown-layer corridor 34 m. f3 v5 at 640x360.
