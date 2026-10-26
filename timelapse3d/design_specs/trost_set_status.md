# Trost set v3 status (aot/trost.py) — for the g5-g8 segment agents

Latest first.

## Update 5 (g7 agent, 10/27): cannon basin K moved to Wall Rose's NORTH face (owner 15:25 10/26 + cloud ruling)
- **Position.** The basin is at its anime position on Rose's north face beside the canal water gate, built as the old
  south layout mirrored about Y 870 (`TR.K_MIRROR_Y = 1740`, `TR._kmy(y)`; `build_basin` authors the old numbers and
  `_kmirror()` reflects the bmesh). Floor KF X 340..385, Y 875..907 (Z -3.6; mossy half against the wall, sandy half
  toward the bank); bank SB Y 907..919 (12 steps); terrace TT Y 919..927; plinth PL X 357..367, Y 902..912 (top -0.6);
  west flight SW Y 885..907; piers PW X 331..340 / PE X 385..393 on the north face; gun bastion GB X 308..338, Y 875..891
  (deck Z 20); **TrostCannon_K at (318, 883, 20), bearing 85 deg** (old 95 mirrored); T_K (322, 922); GH X 341..377,
  Y 928..948; half-timbered range Y 927..970; boats (389, 889/897); derrick L_K (338, 872, 50) with its chain on the north
  side; **TrostBasket_K stop (342, 879, -3.6)** (`set_basket(frac)` unchanged, 1 = Z 50).
- Seen from the Garrison bank (north, looking south at the wall) the canal, barred water gate and boats are on the LEFT.
- **API kept** (names and signatures): ANCHORS_M K_* keys hold the north numbers (+ new K_BANK, K_TT, K_SW, K_HT, K_BOATS,
  K_PIERS); `CANNON_BASIN` keeps its keys (`steps_s` = the bank rows, now on the floor's north side; `cannon_aim`
  (1.0, 0.09); new `side="north"`, `mirror_y`). `ground_z_m`, `walkable_m`, `height_patch` and the terrain holes follow.
- **Water gate north face**: barred grille at Y 875.4 + an east narrowing pier (415, 879); the south side got a west
  narrowing pier (389, 861) in place of the moved PE.
- **Canal north of Rose**: `CANAL_NORTH_M` (X 400, Y 875 -> 1330), `canal_dist_m` covers it; objects
  TrostCanalNorthBanks / TrostCanalNorthWater / TrostCanalNorthFill (not "Canal*", which world.py trims); the west bank and
  fill stop at the basin (Y < 921) so the floor meets the water over a low ledge (lip), as in ep09 19:35.
- Terrain: the 5 m fine grid now runs to M Y 1340 (was 990) for the canal hole; a town-floor apron X 296..420, Y 874..975.
- **Old site** (X 301..377, Y 769..856 at the Rose SOUTH foot): `_infill_old_basin()` places terraces there AFTER the main
  layout with its own RNG (Random(2026)), so every other house in town is unchanged (the site stays reserved for the main
  generator; the yard-tree pass is unaffected).  Still camera `v3_basin` = the north view, `v3_basin_old_site` = g6 H8.
- Note for g6: its exit (H8 = g7 C0, looking at (345, 810)) now frames those terraces, not a basin.

## Update 4 (g8 agent, owner 10/27 + audit; API unchanged)
- **Breach is BOULDER-SIZED**: OuterGateBroken hole 15.6 m wide through the gatehouse with a broken round top at Z ~16
  (was 15 x 32-34 m), ~13 m in the wall body; OuterGate_Glow card resized to the hole; TrostBreachTimbers moved to the new
  hole top; **OuterGate_Plug** now grows UP from the ball top (origin (0, 12, 14.5) M; set_plug(frac) unchanged) and stands
  on the brick face above the wedged ball.
- Ring-pit plank bridge at compass bearing ~28 deg (NNE) from P (AUDIT 4; was 315), railing gap moved with it.
- 5th Rose lift **RoseHQ** at M (-195, 870), south face (AUDIT 6): two tall brown posts + lintel + crossbar; appended to
  WALL_LIFTS (index 4: existing indices unchanged), LIFT_PTS and ANCHORS_M["L"]; platform TrostLift_RoseHQ_Platform.

## Update 3 (g8 agent, cloud QA vs ref/anime/bible/ep13_000019194.jpg; API unchanged)
- Walls (Trost only): TrostWallStone base pre-warmed (#c3b18c) so the lit toon band reads #CEC3A6; damp foot #6f6a58 with
  moss and vertical damp streaks 6-12 m (stone_mat damp_k / damp_streaks); TrostPilaster lighter (#d8caa6) so the
  pilaster shading reads against the recessed panels.
- Breach front: the radiating crack tubes are gone; OuterGate_Beams is now **TrostBreachTimbers** (6 chunky dark-brown
  broken beams with splintered ends + 5 dark root strands), renamed because toon.py inks every "*Gate*" object with a
  0.25 m hull (the thin tubes read as thick black bars). set_breach() shows/hides it as before.
- Seal: **OuterGate_SealRubble** is now a low skirt only at the ball's sides (dark brick #5e3428 / grey stone), so the
  ball's front face stays visible at the base of the Λ plug; set_seal(True) also shows **TrostBallContactSeal**.
- Ball weight: **TrostBallContactB0** (darker contact patch + dust ring on the lawn bed under the ball at B0) and
  TrostBallContactSeal (same at the seal rest, front ring only). g8 hides the B0 one when the ball is lifted.
- Note for g8-time renders: g8 also flattens OuterGateRubble (scale z 0.45, pressed to ~0.2 by the jam) at run time.

## Update 2: blocks 5-9 filled in (build ≈ 19-26 s; stills 1.4-2.0 s/frame after the first-frame shader compile)
- `TR.set_hq_cutaway(frac)` now dissolves TrostHQ_Bay with a dithered alpha (0 < frac < 1; installed lazily after toon),
  1 hides it; TrostHQ_BayShadow (camera-invisible, shadow-only) keeps the sun out of the storeroom.
- `TR.set_mopup(on, pyres=None)`: hidden day-2 props TrostCapturedFrames (CT anchors), TrostCranesD (7 grey pylons with
  gear wheels at D), TrostPyres (log stacks at the 4 PYR anchors).
- `TR.set_basket(frac)`: basin hoist basket TrostBasket_K, 0 = floor (Z -3.6), 1 = Rose top.
- Plaza C: covered well at (-44, 482) + 9 market stalls round the edge (TrostPlazaC); pyre site at the centre is free.
- TrostYardTrees (~170 small yard trees), TrostReliefComplex (RC cloister, NE tower (-213, 845), NW belfry).
- world.py DISTRICT["rose"] = (480, 390, 480).

## Block 1-4 + first pass of 5-9 built (build ≈ 26 s, Eevee still ≈ 1.2-1.5 s/frame at 854x480)

How to get it: `AOT_SET=trost blender -b -P aot/scene.py -P <your script>`; scene.build() calls `trost.build_set()`.
`import trost as TR` after that. **Write positions in M** and convert with `TR.M(x, y, z)` (set = M with Y - 870).
`TR.ANCHORS_M` holds every bible-C anchor (O, P, CRw/CRe, H1-3, BO, TR, LG, AV, C, E, I, CART_*, MA, SS, Q2, TOWER_T,
ROOF_R, HQ_*, K_*, CAN, B0, COURT, BED, ROCK2, BR, STRIP, GF/RF/YF/PY, LV, CT, MI, IA, CROUCH, PYR, A, S1/S2, L, TOWERS).
Note: AV's last leg now runs (-60,470) -> (-128,735) -> (-153,803) so it enters E at the SW corner east of nothing
(the corner turret (-140,790) is beside it, not on it).

### g8 (boulder / seal)
- Ball: object **TrostBoulder**, origin at its CENTRE, location `TR.M(*TR.BOULDER_CENTER_M)` = M (290, 262, 7.4).
  `TR.BALL_R = 7.0`, `TR.BOULDER_SIZE = (14.0, 14.0, 13.6)`; `TR.boulder_mesh(name, origin="center"|"bottom")` makes a copy;
  `TR.marble_mat()` its material. Rest in the breach: `TR.BALL_REST_M = (0, 8, 7)`.
- Route: `TR.BOULDER_ROUTE_M` (B0, R1, R2, R3, arc..., R4, R5, R5b, R6) and `TR.BR_NAMES`; `TR.BOULDER_ROUTE` in set coords.
  `TR.check_route()` prints the min house distance to the route centreline (now 8.8 m >= 7.5 → OK). R1->R3 is an 18 m street.
- Boulder Court: lawn bed (TrostBoulderBed: octagon 30 m, kerb 0.6, 14-rock ring, rubble skirt, shrubs), TrostBedTrees,
  TrostRock2 (6 m second rock, origin on the ground at (308, 247)), TrostCourtBelfry (228, 290, 42 m, red pyramid),
  4-storey terraces round the court (instanced in TrostTown), exit gap X 270..298 on the south side, lane (232,300)->(180,360).
- Mikasa's roof: **TrostMikasaRoof** (origin at the eave line centre (252, 299, 12.85)); broken version
  **TrostMikasaRoofBroken** (hidden). `TR.set_mikasa_roof(broken=True)` swaps them. House body = TrostMikasaHouse.
- SE wall-foot strip (r 437..475, phi 8-37): TrostStripProps (X-fences r 440, 4 sheds + plank ramps against the wall,
  crates) + TrostStripSlab0/1 (toppled). The lane r 446..464 is clear.
- Gate square: TrostRingPit (C-trenches, plank walls, bridge NW, railing, puddles), TrostGateProps (plank boxes at (-24,40),
  (22,52), bollards Y 30 with the 20 m gap, crib fences), TrostGateTrees (2 spruces W, bushy tree E), lift TrostLift_Gate.
- Slabs: **TrostSlab_P1..P6** (pit arc) and **TrostSlab_A1..A8** (ring road / avenue mouth): one object each, origin = base
  centre, local -Y = spiked front. Initial poses in `TR.SLABS = {name: (X, Y, yaw_deg)}` (M). 8 W x 12 H x 4 D.
- Breach: `TR.set_breach(True)` hides OuterGate / OuterGate_Door / OuterGate_Iron and shows **OuterGateBroken**
  (15 m hole X -7.5..7.5 through the gatehouse, 13 m in the wall body, broken round top Z 30-34), **OuterGateRubble**
  (fan 15-20 m north), **OuterGate_Beams**, craters **GS_Crater0/1** + holes **GS_Crater2..4** (caps GS_CraterCap* hide).
- Glow: **OuterGate_Glow** (orange card in the hole). `TR.set_glow(v)` v 0..1 (0 hides it). set_breach(True) sets 1.
- Plug: **OuterGate_Plug** (Λ spire to Z 38, ~60 tendril tubes, origin (0, 12, 0) M). Hidden. `TR.set_plug(frac)` grows it
  (scale z). `TR.set_seal(True, plug=1.0)` = glow off + **OuterGate_SealRubble** (crushed-brick ring) + plug.
- Craters: CRw (-32,20), CRe (34,30) r 4.5, 2 m deep with splintered lips; holes H1-3. Ground query: `TR.ground_z_m(X, Y)`
  (pit floors -7 / -4, setbacks, craters, canal -4.2, basin -3.6, Q2 +5, E terraces).
- Wall-top: brick pavers, 1.5 m track, turntable cannons (TrostCannon_bulge*), huts, crates, green flags (TrostGarrison).
- Rico's spots: GF (334, 136, 50) on the curved wall top, RF (306, 300, 19) = ridge of the court's NE terrace, YF = top of the
  plank box (-24, 40, 2.5). Pyres PYR anchors are kept free of houses.

### g5 (inner gate / evacuation / alley)
- **TrostCart** = parent EMPTY at the LOAD CENTRE, local +Y = forward (horses). Children TrostCart_Body / _Load / _Horses.
  `TR.set_cart("start"|"end")` or `TR.set_cart(frac=0..1)`; `TR.CART_STATES` (load centre M, compass yaw): start
  (-140, 851.5) yaw 0 (wedged in the arch, horses in the tunnel), end (-122, 842) yaw 320. Hidden by default:
  `TR.set_wagon(True)` shows it. Rotation: `rotation_euler.z = -radians(compass_yaw)`.
- InnerGate (bastion + wall block, open 5.0 x 6.5 arch at X -140, dark 22 m tunnel shut by a dark curtain at Y 872.5),
  InnerGateYard (ledge, terrace edges, slope trees, west tree), InnerGateBuildings (corner turret, pyramid-tower building).
- MA: TrostAlleyMA (dark W face, ashlar E face + stain, 5 steps Y 440-443, rubble heap, broken end wall ≤ 10 m).
- Q2: TrostQ2Buildings (W terrace with roof R ridge (-258, 505, 25), S terrace, domed arcade N), TrostTowerT (shaft) +
  **TrostTowerT_Top** (top 8 m, origin at its base centre (-218, 522, base+26)).

### g6 (HQ)
- TrostHQ_Keep, TrostHQ_Wing (static), TrostHQ_Store (storeroom: brick piers, rafters Z 6, vaults, cylinders, torches,
  guide tower), **TrostHQ_Bay** (the 36 m bay above the storeroom, dissolves) + **TrostHQ_BayShadow** (shadow-only proxy),
  **TrostHQ_Cage** (origin = cage floor centre at (-187, 641); `TR.set_hq_lift(frac)` 0 = Z 10, 1 = Z 2.8).
  `TR.set_hq_cutaway(frac)` 0 = closed, 1 = gone (dither in between is a TODO; see gaps).
- TrostHQ_Back: back range + courtyard tree + gutted house GH (-200, 566).

### g7 (basin) -- SUPERSEDED by Update 5: the basin is on Rose's NORTH face (Y' = 1740 - Y)
- TrostBasin (floor Z -3.6, piers, bank + nosings, plinth, SW flight, GB deck Z 20, T_K, GH, half-timbered range),
  **TrostCannon_K** at (318, 883, 20) aimed 85 deg, TrostBoats_K, TrostHoist_K, **TrostBasket_K** (`TR.set_basket(frac)`).
- `TR.CANNON_BASIN` (set coords): trio, cannon, plinth/landing, steps_s rows, basket, derrick.

### Known gaps
- Town ≈ 2,600 instanced terrace houses (dense in the aerials; some interior blocks have small cobbled yards).
- Chimney smoke, steam, embers, flares, people, titans are not part of the set (FX / segment agents).
- render_interlude.py: TR.town_points() now returns the v3 layout mapped to its variants; TR.build_church is a no-op.
- The old render_trost.py pipeline still imports (old names kept) but its hard-coded positions are pre-v3.
- Stills: E:/YTP2/3D Timelapse/renders/trost_set_v3/ + trost_set_v3_sheet.jpg.
