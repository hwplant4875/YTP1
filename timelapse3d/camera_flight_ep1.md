# EP1 camera flight, set B (Shiganshina, chapters 2-9)

The camera is one continuous drone flight with no cuts, following `EP1_plan_terrain_camera.md` section 2, rows 3-9 (0:25-4:00). The flight is implemented in `aot/flight.py`. Enable it with `AOT_PLUGINS=flight`, usually together with `cast845,states845`.

- Frames are **global EP1 frames** at 30 fps: g750 = 0:25, the first frame of chapter 2.
- The opening module uses **flight frames** f = g - 750.
- Positions, look-at points and lenses follow a Catmull-Rom spline through the keys.
- A move with three or more keys is a timed waypoint move. Every key is hit exactly at its frame, and a monotone cubic time map gives zero speed at the start and end of the move, so the camera slows in and out without stopping at the waypoints in between.
- A two-key move is eased (smootherstep) and re-timed by "perceived distance": metres divided by (height above ground + 25 m). High glides travel fast and the last metres over the grass are slow.
- There is a hold between two moves wherever a gap is listed.
- Checked over every frame g750-7200:
  - The lowest camera height above ground is 0.55 m, at the end framing.
  - The lowest height when crossing Wall Maria is 73 m (the wall is 50 m).
  - The camera never comes closer than 25 m to the tree.

## How to use it

| What | Command / API |
|---|---|
| Still of any opening frame | `AOT_PLUGINS=flight bash render.sh flight_f0815 out.png 960x540 32` (f0000-f0900; the kids' pose follows the frame) |
| Still of any set-B frame | `AOT_PLUGINS=flight,cast845,states845 AOT_STATE=... AOT_EVENT=... bash render.sh ep1_g03600 out.png ...` (g00750-g07200) |
| Animated camera, opening | `flight.build_flight_camera(0, 900)`, one key per frame, scene range 0..900 |
| Animated camera, all of set B | `flight.build_setb_camera(750, 7200)` |
| Camera or state at a frame | `flight.flight_at(f)`, `flight.setb_at(g)` -> (loc, look_at, lens); `flight.state_at(g)` -> AOT_STATE / AOT_EVENT / AOT_ARC_T / chapter / light |

Recommended light for chapter 2: `SUN_AZ=-102`. This puts the sun front-right of the end camera, behind the wall. The wall face is then in shade (blue-grey), the kids read as silhouettes and the tree is back-lit, as in the anime still. scene.py's default `SUN_AZ=25` lights the wall face directly, which looks less like the still. The sun elevation is fixed at 38 deg in scene.py, so the golden-hour and dusk chapters need an elevation control that scene.py does not have yet (see the open items).

## The hill set (chapter 2)

The hill is built by `flight.py`, with `REPLACES={"hill","kids"}`. scene.py's HILL at (330, 820) is not used.

- **End camera:** (-480, 338, 5.8), eye 0.55 m above the flower bank, 50 mm, level.
  - It looks along yaw 28 deg east of due south, toward (-292, -15) on Wall Maria.
  - This is the framing of `refs/user/ep1_tree_hill_wall.png`.
  - Wall Maria is about 340 m away at the frame centre, about 300 m at the right edge and about 500 m at the left edge.
  - The wall top sits at about 25 % of the frame height on the left and 16 % on the right. The reference has 25 % and 14 %.
- **The tree:** trunk base at (-466, 317) on a rise, about 317 m north of the wall and 24 m from the camera, at screen x 0.17.
  - About 10 m tall, with the fork at 2.5 m.
  - The crown is a broad dome that starts about 2.7 m up and covers the top-left quarter of the frame. It is made of leaf clumps plus leaf sprigs scattered by geometry nodes.
- **The terrain:** `height_patch` adds the tree's rise, the camera bank, a rise toward the left, and a pale ridge in the lower right. The added height fades to zero 420-670 m from the camera, so nothing changes near the wall line.
  - The coarse base terrain under the hill is cut out. It is replaced by `HillGround`, a warped grid about 1 m per quad near the camera and 4 m at 300 m.
  - `HillGround` uses a meadow copy of the terrain material that blends back to scene.py's colours at the patch edge.
- **The kids:** `characters.place_opening`, ray-cast against the trunk.
  - Eren lies asleep until f750, sits up at f810, crouches at f850 and stands at f870.
  - Mikasa stands with her red scarf and her firewood frame, and has been moved 0.9 m closer to the trunk than the default placement, as in the still.
  - Both are about 70 px tall at 960x540 and faceless.
- **Props between the tree and the wall** (placed by screen position from the end camera):
  - 2 windmills at screen x 0.60 and 0.72, 290 m away
  - 10 small red-roof farmhouses near the wall foot
  - cypress groves at screen x 0.84-1.0, 190-310 m away
  - dark broad-leaf clumps mid-valley
  - woods along the wall foot on the right
- **Wall details:**
  - a watch tower on the wall top at the frame centre
  - dark vertical slab joints every 12 m on the wall's north face between x = -760 and x = -40, which is the strongest pattern on the anime wall
- **Background:** a hazy mountain backdrop 10-19 km to the south-south-east, beyond scene.py's 9 km terrain, and a high cloud layer.
  - The mountains are a green hill just clearing the wall a little left of centre and a blue range on the right, sized by the angle they make above the end camera.
  - From the high opening views they read as a distant range.
  - The cloud layer is at 1.9 km, visible to the camera only and casts no shadow.
- **Foreground:**
  - grass tufts within 62 m of the camera, thinning with distance
  - white and yellow flower drifts on the slope
  - a bed of blue bellflowers 1.7-6.5 m in front of the lens
  - a Poly Haven boulder (already in `assets/polyhaven`) in the bed
- **Removed:** scene.py's small settlement inside Wall Maria has tall town houses. The 112 of them west of x = -105 are hidden by setting `dead`, so the hill looks onto farmland.
  - The settlement around the inner gate road and the canal is kept.

## Shot list

Columns: global frame (g), flight frame (f, chapter 2 only), camera position, look-at, lens, what is on screen, and the plug-in state.

The plug-in state is the env for `cast845` (`AOT_EVENT`) and `states845` (`AOT_STATE`, `AOT_ARC_T`). `flight.state_at(g)` returns the same values.

### Chapter 2, "A Very Long Dream" (g750-1650, 0:25-0:55)

**State:** year 845, `AOT_STATE=intact`, `AOT_EVENT=intact`, morning, `SUN_AZ=-102`.

| g | f | Position | Look-at | Lens | On screen |
|---|---|---|---|---|---|
| 750 | 0 | (-250, -60, 1500) | (20, -520, 0) | 26 | Very high over the north end of the district. The whole U-shaped Shiganshina is in frame, as in `shiganshina_aerial.png`: canal side, plaza, outer gate at the far end, Wall Maria crossing the bottom of the frame. Move A starts: glide north over the inner wall. |
| 1050 | 300 | (-470, 660, 760) | (10, -420, 0) | 30 | The oblique map view of the aerial still, seen from inside Wall Maria: the U reaches away to the south-east and the hill is below the bottom of the frame. Hold 1 s. |
| 1080 | 330 | same | same | 30 | Move B starts: the swoop down onto the hill. |
| 1310 | 560 | (-560, 560, 120) | (-300, 40, 30) | 40 | Low over the farmland, descending. Wall Maria now fills the frame and the district has dropped behind it. The tree rises in from the bottom left. |
| 1470 | 720 | (-480, 338, 5.8) | (-292, -15, 5.8) | 50 | The end framing, matched to `ep1_tree_hill_wall.png`. The tree is on the left, Wall Maria runs across the frame close behind, and the camera is low in the flowers. Windmills, farmhouses and cypresses lie between the tree and the wall. Hold. |
| 1500 / 1560 / 1620 | 750 / 810 / 870 | held | held | 50 | Eren lies asleep (750), sits up (810), crouches (850) and stands (870). Mikasa waits. HUD: "845 · Eren, age 10". |

### Chapter 3, "The Survey Corps Return" (g1650-2400, 0:55-1:20)

**State:** `AOT_STATE=intact`, `AOT_EVENT=intact`, morning. Bells; the crowd and riders are not modelled yet.

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 1650 | (-480, 338, 5.8) | (-292, -15, 5.8) | 50 | Hill end framing. Move C starts. |
| 1760 | (-490, 352, 32) | (-290, -30, 26) | 42 | Rising straight up behind the tree (clear of the crown). The kids shrink below and the wall top comes level. |
| 1950 | (-170, -90, 165) | (0, -600, 10) | 30 | Over the Wall Maria walk (cannons, rails). The town opens up beyond with the main avenue running to the outer gate. |
| 2100 | (40, -460, 70) | (0, -720, 18) | 32 | Outer gate seen from inside the town while it rises; the green-cloak column rides in. Move D starts at once. |
| 2400 | (-40, -430, 30) | (0, -300, 4) | 30 | The camera turns to follow the column north up the main avenue toward the plaza. |

### Chapter 4, "Father's Promise" (g2400-2700, 1:20-1:30)

**State:** `AOT_STATE=intact`, `AOT_EVENT=intact`, midday.

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 2400 | (-40, -430, 30) | (0, -300, 4) | 30 | End of the avenue track. Move E starts. |
| 2700 | (-20, -70, 38) | (-72, -118, 3) | 32 | The Yeager house (`states845.YEAGER_HOUSE`, same framing as the states845 `yeager` camera), intact, in a dense block near the inner gate. Optional: Grisha's cart rolls north through the inner gate. |

### Chapter 5, "Armin by the River" (g2700-3150, 1:30-1:45)

**State:** `AOT_STATE=intact`, `AOT_EVENT=intact`, late afternoon (warm, lower sun).

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 2700 | (-20, -70, 38) | (-72, -118, 3) | 32 | Move F starts. |
| 2820 | (150, -100, 30) | (228, -300, 4) | 30 | Swing east to the canal. |
| 3150 | (205, -480, 12) | (228, -700, 6) | 28 | Low and slow south along the stone-banked canal toward the outer wall (the three kids on the bank). The heading sets up the look south for chapter 6. |

### Chapter 6, "The Colossal Titan" (g3150-4500, 1:45-2:30)

**State:**
- g3150-3449: `AOT_STATE=intact`, `AOT_EVENT=intact`.
- From g3450: `AOT_EVENT=colossal`, golden hour.
- From g4080: `AOT_STATE=kicked`, with `AOT_ARC_T=(g-4080)/90` capped at 1, so the blocks are in the air for 3 s.
- From g4290: `AOT_EVENT=armored`, the Colossal gone in steam and the titans pouring in.

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 3150 | (205, -480, 12) | (228, -700, 6) | 28 | Move G starts: rise off the canal. |
| 3450 | (60, -330, 38) | (0, -740, 62) | 28 | Hold looking south over the roofs at the outer wall: the quake, steam beyond the wall, then the head rises over the parapet. The Colossal is static in cast845, so its rise needs a keyed z offset (open item). |
| 4050 | (32, -525, 25) | (-6, -735, 49) | 45 | Slow push to the thumbnail framing: the Colossal's head and hand over the wall, looking into the town. This is near the cast845 `colossal_town` camera. |
| 4080-4170 | easing back | | | The kick. Blocks arc over the rooftops (`AOT_ARC_T` 0 to 1) and dust columns rise. |
| 4500 | (46, -450, 80) | (-2, -710, 6) | 30 | The breach seen from inside (states845 `breach_inside`): the jagged hole, the rubble fan and the first pure titans entering. |

### Chapter 7, "Mother" (g4500-5400, 2:30-3:00)

**State:** `AOT_STATE=kicked`, `AOT_EVENT=armored` (inflow including the Smiling Titan), late afternoon. The Armored is part of the cast845 `armored` state; hide it or keep it at the breach until chapter 8.

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 4500 | (46, -450, 80) | (-2, -710, 6) | 30 | Move H starts. |
| 4950 | (-20, -70, 38) | (-72, -118, 3) | 32 | The Yeager house crushed under a thrown block (states845), with dust in the air. Hold to g5400 while the Smiling Titan walks in from the avenue (cast845 sends it west toward the house). Hannes carrying the kids is not modelled. The eating stays off camera. |

### Chapter 8, "The Armored Titan" (g5400-6300, 3:00-3:30)

**State:**
- g5400-6059: `AOT_STATE=kicked`, `AOT_EVENT=armored`, dusk.
- From g6060: `AOT_STATE=armored` (inner gate burst, debris fanning north).

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 5400 | (-20, -70, 38) | (-72, -118, 3) | 32 | Move I starts: swing back over the roofs. |
| 5700 | (62, -385, 26) | (-6, -505, 9) | 30 | The Armored charging north up the avenue (the same offset as the cast845 `armored_gate` camera, for the Armored near y = -500). |
| 6000 | (62, -120, 30) | (0, -40, 15) | 30 | Tracking it to the inner gate square; cannon smoke on the wall. |
| 6150 | (60, 60, 95) | (0, -20, 22) | 30 | Up over Wall Maria to the north side (no cut). |
| 6300 | (52, 215, 26) | (-2, 0, 15) | 30 | The north side of the inner gate (states845 `inner_burst`): the gate bursts, titans spill into the farmland, and the ferries crowd the canal water gate at x = 228. The ferries exist in shot_thumbs.py, not in this set. |

### Chapter 9, "Wall Maria Is Lost" (g6300-7200, 3:30-4:00)

**State:** `AOT_STATE=night`, `AOT_EVENT=armored`, night.

| g | Position | Look-at | Lens | On screen |
|---|---|---|---|---|
| 6300 | (52, 215, 26) | (-2, 0, 15) | 30 | Move J starts: the big pull-up. |
| 6750 | (-470, 330, 330) | (40, -360, 0) | 27 | Burning, smoking Shiganshina at night (states845 `town_burning`). |
| 7200 | (230, 1400, 2200) | (228, 6000, 0) | 26 | Climbing north along the river toward the lights of Wall Rose, with titan dots fanning out over the farmland behind. Hand-off to set A (the island map), where the Maria belt turns grey. |

## Checks done

The renders are in `E:/YTP2/3D Timelapse/renders/flight/`.

- **End framing, ten render-and-compare passes** (`end_v1` to `end_v10`, side-by-sides `sbs_v2` to `sbs_v10`). The final pair is `end_final_f0815.png` and `sbs_final.png`, at 960x540 and 32 samples with `SUN_AZ=-102`. The geometry was confirmed with ray-cast and projection debug scripts.
  - Camera at (-480, 338, 5.83).
  - Tree trunk at screen x 0.17; reference 0.17.
  - Crown in the top-left quarter, right edge at about 0.50; reference about 0.50.
  - Watch tower just right of the crown at 0.53; reference 0.50.
  - Wall top 0.25 / 0.16; reference 0.25 / 0.14.
  - Horizon at the frame centre (level camera), wall foot just below it; the same in the reference.
  - Kids at 0.24 / 0.29; reference 0.21 / 0.27.
  - Windmills at 0.60 / 0.72; the same in the reference.
  - Flower bed fills the bottom third; the same in the reference.
- **Opening strip:** six frames at 640x360, 16 samples (`strip2_f0000`, `f0150`, `f0300`, `f0480`, `f0620`, `f0720`), assembled in `strip_sheet.png`.
- **Set-B path:** checked numerically. Every key is hit at its frame, the camera stays clear of the ground and Wall Maria, and both animated cameras build. No set-B frames after the opening have been rendered yet. Their keys are taken from the other plug-ins' camera positions.

## Open items

- **Colossal and the kick:** the Colossal's rise (g3450-3750) and its fade into steam (g4200-4290) need keyed transforms in cast845. Today it is static.
- **Lighting per chapter:** scene.py fixes the sun elevation at 38 deg. The chapter light needs a time-of-day control (midday, golden hour, dusk); night is handled by states845.
- **Not modelled yet:**
  - the Survey Corps column and crowd (ch3)
  - Grisha's cart (ch4)
  - the three kids at the canal (ch5)
  - Hannes carrying the kids (ch7)
  - the ferries in this set (ch8-9; they exist in shot_thumbs.py)
- **Global side effects of `AOT_PLUGINS=flight`:** the mountain backdrop and the cloud layer show in every shot that looks south-south-east, including the chapter 6 views behind the Colossal. `FL_MOUNTAINS=0` and `FL_CLOUDS=0` turn them off.
  - The plug-in also adds the dark slab joints on Wall Maria's north face, hides 112 settlement houses west of x = -105, and adds the wall tower.
- **Hill tree in the swoop:** seen from the side at about f620 the crown reads as a rounded mass, like a topiary. The leaf sprigs help, but the silhouette needs gaps and drooping masses.
