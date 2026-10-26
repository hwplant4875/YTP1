# SCENE BIBLE v2: EP1 one take, Shiganshina 845 to the Trost seal (lore-accurate build spec for the laptop)

Merged from the 8 verified anime specs g1-g8 (/tmp/claude-0/aot/anime/design/), HANDOFF.md owner rules and BRIEF.md.
Integrator rules applied: **owner rules beat the anime; the Trost master map (section C) beats every other position.**
Evidence is cited as `epNN mm:ss.s` (frames under /tmp/claude-0/aot/anime/frames/epNN/). `[INF]` = placed by inference, no frame fixes it.
Every camera key below was re-checked with a numpy copy of `render_fast._Channel` (chord Hermite + PCHIP arc length); the peak
values quoted are from that check.

**Frames.** World (Shiganshina) frame W: Wall Maria line y = 0, Shiganshina inner gate (0, 0), outer gate OG (0, -720), +y north.
Trost master frame M: Trost outer gate O (0, 0), +Y north, Wall Rose centreline Y 870 (south face 865, north face 875).
`M = W - (0, 4130)`; trost.py set frame `= (X, Y - 870)`; WORLD_K = 0.05 (Trost set origin = world (0, 5000)). Z = metres up.

**Global owner rules (binding, latest wins).** One take, no cuts/wipes/cloud transitions; seams match position, look-at, lens
and velocity (09:37 10/25). Calm sky observer at moderate height, no chase, no face close-ups, lens <= 50 mm, over-zoom pulled
back (00:44 10/26). No camera behind the Colossal's back (15:07). Pace is everything ("속도감은 생명", 09:06). Humans: true
1.65 m, faceless, downloaded assets only, no red-cape giants (04:53, 07:19, 08:12, 09:37). Titans keep their faces (07:19:
"Titan assets stay as they are"); the Armored's eye glow and the Attack Titan's green eyes are allowed as <= 2 px emissive.
Only Shiganshina and Trost have buildings (09:37), with the exceptions in section E. No mountains; sea on the far south
horizon. Walls: flat tops with a low plain parapet, no merlons/crenellations (23:45 10/23, 16:58); pilasters rise as flat
square-topped stubs; one warm pale beige albedo (about #CEC3A6) with a damp, darker, mossy lower 6-12 m. Toon "less orange".
Blood: tasteful, small dark decals only. HUD/name tags exist; do not redesign graphics; no full-screen graphics (17:41).

---------------------------------------------------------------------------------------------------------------------

## A. One-take overview

### A1. Segments (default = TIGHT; FULL kept for reference)
| # | segment | tight s | full s | tight global start | content |
|---|---|---|---|---|---|
| g1 | Opening + Shiganshina fall | 32.0 | 32.0 | 0:00.0 | tree (locked) → crane to 92-125 m → bolt → hands, head → kick 11.0 → pour → fly left → Carla |
| g2 | Armored ram + ferries | 32.0 | 32.0 | 0:32.0 | Armored runs up the avenue under fire, shoulder-rams the intact inner gate, ferries flee north at dusk |
| g3 | Flight north, camps, march, camp | 78.4 | 78.4 | 1:04.0 | flight 12.9, camps 18.4, march846 18.0 (KEEP), flight to camp 14.1, 104th camp 847-850 15.0 |
| g4 | Trost 850 establishing | 20.0 | 20.0 | 2:22.4 | dawn → Survey Corps rides out → cadets on the outer wall top → Eren "I can do it" → bolt |
| g5 | Trost breach, evacuation, Mikasa, Attack Titan | 70.0 | 84.0 | 2:42.4 | Colossal returns, kick, pour; cart jam; Abnormal kill; Mikasa falls; AT punch; fight #2 |
| g6 | Supply HQ, lift op, Eren emerges | 69.5 | 74.0 | 3:52.4 | AT rampage on the plaza; cutaway lift op; collapse; Eren out of the nape |
| g7 | Cannon basin, half-shift, salute, Pyxis | 45.0 | 116.0 | 5:01.9 | owner said "quick" (05:58 #4): PACE version is the default |
| g8 | Boulder, seal, Levi, mop-up, pyres | 75.0 | 136.0 | 5:46.9 | top-effort beat; tight version keeps every must-have |
| | **Total** | **421.9 (7:02)** | **572.4 (9:32)** | end 7:01.9 | owner budget title→end of Trost ≈ 4:30 (17:01), EP1 8-10 min (15:51): see E1 |

### A2. Seams (exact; position / look-at / lens / velocity)
| seam | frame | camera | look-at | lens | velocity (m/s) |
|---|---|---|---|---|---|
| g1 K12 = g2 K0 (= `render_fall2.SEAM_IN`) | W | (-130, -686, 114) | (-165, -594, 0) | 28 | **0 (at rest)**; g1 adds a guide key at 33.0 equal to it |
| g2 K9 = g3 FA0 | W | (175, 480, 240) | (228, 1050, 0) | 28 | 45 heading N, vz +8 |
| g3 CAM_IN = march846.CAM_IN | M (set: (170, -700, 125)) | (170, 170, 125) | (-10, -60, 0) | 27 | (16.7, -61.1, 5.6) |
| march846.CAM_OUT = g3 FT0 | M (set: (260, -1920, 640)) | (260, -1050, 640) | (0, 150, 40) | 28 | (0, 95, 22) |
| g3 FT7 = g4 G0 | M (set: (-1570, 320, 170)) | (-1570, 1190, 170) | (-1450, 1490, 0) | 30 | 20 heading SE, vz 0 (≈ (14, -14, 0)) |
| g4 G5 = g5 C0 | M | (-40, 330, 170) | (0, 0, 30) | 32 | (1.3, -8, -1) |
| g5 C10 = g6 H0 | M | (-345, 455, 175) | (-185, 640, 15) | 30 | (3, 5, 0) |
| g6 H8 = g7 C0 | M | (220, 650, 130) | (345, 810, 0) | 32 | (25, 8, 0) |
| g7 C15 = g8 K0 | M | (-40, 960, 205) | (40, 540, 0) | 30 | (-2.5, -5, 2) |
| g8 E2 (END) | M | (200, 760, 240) | (-20, 300, 0) | 28 | 0 (guide key +1 s) |
All seams: dlnlens = 0. FA4 = W (60, 4300, 300) = M (60, 170, 300).

### A3. How to build the camera (applies to all segments)
- Build position and look-at as **separate arc-length channels** (`render_fast._Channel`), lens in log space. `_pchip_m` sets the
  first tangent to 0 and the last to the last secant, so: a seam AT REST needs a duplicate guide key 1 s later; a MOVING seam
  needs a guide key at `seam ± v·Δt`, or better (P0) give `_Channel` optional `v_in/v_out` like `march846._tangents` already has.
- Recommended runs (verified as single channels): **A1** g1 alone (ends at rest); **A2** g2 + g3 flight + camps up to CAM_IN
  (+ guide key at 31.8 = CAM_IN + 0.5·v); **march846** unchanged (own spline, CAM_IN/CAM_OUT contracts); **B** FT0 → g8 E2 as ONE
  channel (lead-in guide key at FT0 − 1 s = M (260, -1145, 618)). Measured peaks (tight): g2 78 m/s / 30°/s; g3 flight 412 m/s
  (see g3 note); flight to camp 298 m/s; g4 141 m/s / 32°/s; g5 43 m/s / 29°/s; g6 39 / 25; g7 104 / 26; g8 67 / 30.
- Rules: travel height 90-380 m (never > 650), pitch 17-45° (cutaway 51° allowed), yaw ≤ 30°/s, lens 27-50 mm, the look-at
  path must never pass under the camera (that is what caused every yaw flip found in review; bridge keys below fix them).
- The shake rule: at most 0.15-0.3° for 0.3 s at the Shiganshina bolt and kick (owner 15:07 #5 asks for a shake; g1 caps it).

---------------------------------------------------------------------------------------------------------------------

## B. Per segment

### g1. Opening + Shiganshina fall (32.0 s, frame W) — KICK AT 11.0 (owner 09:06 exact timing)
**Layout.** District = current elongated U/stadium (owner 06:05 "elongated U"; do not reshape). OG (0, -720) facing south;
avenue x = 0, 14-18 m packed earth, gentle bend in the dense part; plaza (-20, -360) r 40 bare dirt; canal EAST at x = +228,
24-28 m (district.py's west canal is wrong); belfry (5 x 5 m, 30-35 m, arched openings, pointed cap) at (+25, -540); onion-spire
church (35 m) at (+70, -560); Yeager house YH **(-165, -585)** (LEFT as seen from the Colossal, owner 00:44 10/26; do not move,
SEAM_IN is built on it). Tree hill 300-400 m north of the inner wall; between tree and wall: the hamlet (≤ 10 red-roof
farmhouses, windmills, cypress clumps) per the owner's opening ref (17:45, hill_tree_wall_opening_ref.png).
**Set dressing.** Wall Maria: pale warm sandstone, pilasters 3.5 m wide every 16 m projecting 2 m, rising 2-3 m above the
parapet as flat square stubs; string courses at about 11-12 m and 23 m; grime streaks. **Outer gatehouse = owner 16:58 flat
version**: two barely projecting pilasters (1-2 m) with flat square tops, a flat recessed panel with a row of small vent slots
near the top; NO tower block, NO dome winch-house (g1's domed block from ep01 19:14.2 is overruled). Inside face: brick plinth
25 x 10-12 m, cream cornice, goddess crest pier, 2 barred arched doors 3 x 6 m (ep01 18:47.9). Houses: terraced 2-4 storeys,
cream plaster #DCCFAE, dark timber posts/braces (not uniform X-lattice), steep terracotta roofs lit #B5703F, crow-stepped
gables, dense to the wall foot; lanes 5-8 m; well squares 20 m. Yeager ruin: rock terrace +4-5 m at the HEAD of a stone
stair-lane (5-6 m wide, 20-25 steps over 30 m, rising south), covered well, external stair, 8 m tree, roof slumped forward,
**a 9 m rough rock on the ruin** and a 5 m one just beyond (ep01 21:17.4, 20:14.5). Thrown rocks: rough rounded lumps 2-10 m
#BDB49A (never cubes). Breach rubble fan 60-90 m deep flattening the houses in front of the hole. Outside: grass slopes,
conifer clumps, sea on the horizon.
**Characters/titans.** Colossal 60 m: skinless red #CB604B/#8B2D1D, white cheek plates, teeth; anatomical head (≈ 8 m chin to
crown; drop the 1.8x HEAD); stands flush against the outer face; **wall at his collarbone: only the head and a sliver of
shoulders clear the parapet**, teeth at about 50 m, crown 60 m (23:45, ep01 18:29.4). **LEFT palm grips first, RIGHT a
little later** (15:07 #4), fingers over the town-side edge. Kick: only the right leg moves, left planted (06:12); lands at
GATE height; only the gate opening breaks (15:07 #6). After the kick he stands steaming, arms spread 45° down, then vanishes in a
steam burst drifting WEST. Pour: 20-25 inside by the end, mixed 3-15 m, 4-6 m/s lumbering, incl. the laughing titan (ep02
02:57.6); 8-12 more crossing the grass from SE/SW/S. Smiling Titan ≈ 13 m (CARLA_TITAN_H 16 → 13), shoulder-length light-brown
/dark-blond hair, alone (no titan within 80 m), comes from the wall side, 90° waist bend at the stair head. Carla 1.6 m under
the beam. Crowd: 600-1000 instanced; plaza 40-60 looking up; after the kick streams of 20-60 flee north at 3-5 m/s. Colourful
minimal plaza people are owner-loved (15:07) — palette per E2.
**FX.** Mackerel gold-green sky; ONE thick unbranched S-curved yellow-white bolt behind the outer wall (core #FCFA95), screen
briefly darkens (owner 15:07 #5: "yellow-orange, the screen briefly darkens"), green-gold tint 0.8 s; Colossal steam leaning
WEST; kick: street gust 40 m/s, orange-brown dust dome 90-110 m wide to parapet height with an 80 m plume, 4-6 long debris arcs
fanning ±60° (apex 80-120 m, landing 100-350 m, one on YH), smaller stones with smooth in-betweens (15:07 #6); roof hits as
progressive collapse with dust bursts, never a 1-frame swap (15:07 #7); 5-8 thin wavy smoke columns (2-3 near-black) with
embers and ground fires; breach reads DARK (not green); golden light S/SSW 20-30°, head shadow falls north; no blood.
**Choreography (fallback timeline, kick 11.0).** 0-2.05 locked tree (Eren seated waking, Mikasa walking; very slow zoom-out) ·
2.05 crane up · **3.3 bolt** (+ darken + 0.2° shake) · 4.5 left palm on the top · **5.0-8.0 head rises** · 6.0 right hand grips
· 7.0 head shadow on the roofs · 9.6-10.8 right-leg wind-up behind the wall · **11.0 KICK** (+ 0.2° shake) · 11-14 dust dome ·
12.0-15.0 stands, arms spread · **13.5 first titans** out of the dust (every 0.6-0.8 s for 8 s) · 14.5-16.5 rock hits, roof
collapses · **15.0-17.5 steam vanish** (drifts west) · 16-24 smoke columns one by one · 20-23 fly LEFT (camera drifts SW, the
pour stays frame-left) · 21.5 Smiling Titan on the upper lane · **25.5 bend · 26.6 grab · 26.8-27.6 lift · 28.4 bite** (hidden
by head/hair) · 28.8-32 it turns away, camera settles at SEAM_IN.
**Camera keys (W).** K0 0.00 locked close · K1 2.00-2.05 locked tree framing ≈ (-480, 338, 7).
| key | t | camera | look-at | lens |
|---|---|---|---|---|
| K2 | 3.9 | (-456, 298, 92) | (-40, -600, 40) | 30 |
| K3 | 5.8 | (-330, 135, 106) | (-15, -700, 50) | 34 |
| K4 | 7.8 | (-185, -60, 116) | (-8, -700, 55) | 42 |
| K5 | 10.0 | (-78, -215, 124) | (-5, -705, 45) | 50 (hold; 500 m from OG, frame ≈ 356 m wide) |
| K6 | 13.0 | (-62, -250, 124) | (-10, -680, 30) | 45 |
| K7 | 16.5 | (-60, -320, 125) | (-15, -690, 15) | 40 |
| K8 | 20.0 | (-78, -425, 121) | (-60, -650, 8) | 36 |
| K9 | 23.0 | (-92, -478, 119) | (-140, -600, 4) | 32 |
| K10 | 26.0 | (-86, -545, 117) | (-160, -592, 3) | 30 |
| K11 | 29.0 | (-98, -625, 115) | (-165, -593, 2) | 29 |
| K12 | 32.0 | (-130, -686, 114) | (-165, -594, 0) | 28 = SEAM_IN; guide key 33.0 identical |
Verified: peak 129 m/s (crane-up ≈ 75 m/s), ≈ 22 m/s at the kick, ≤ 34 m/s afterwards; no key looks from behind the Colossal.
**Must-have lore.** Bolt then green-gold flash (ep01 17:40.5, 17:40.7) · mackerel sky (17:36.8) · hand over the town-side edge
(18:14.1, 18:29.4) · only the head clears the wall, steaming skull (18:29.4, 18:33.4) · head shadow north on a well square
(18:25.8) · gate crest between his feet (18:36.9) · dust dome + debris arcs both sides (18:50.3-18:59.3) · ragged dark hole at
ground level 14-15 x 16-20 m, wall above intact (19:08.2, ep02 05:12.7) · arms spread, steam west, titans walking in from SE/SW/S
(19:08.2, 19:12.2) · thin wavy smoke columns + ground fires (19:17.7, ep02 02:31.9, 02:23.0) · mixed titans incl. laughing one
(ep02 02:57.6) · 9 m rock on the Yeager ruin, stair-lane terrace, covered well (21:17.4, 20:14.5, 20:36.2) · Smiling Titan bend
and lift (22:40.0, 22:49.8) · east canal with twin water-gate arches (00:54.8, ep02 05:25.5).

### g2. Armored Titan ram + ferries (32.0 s, frame W)
**Layout.** Avenue x = 0 (26 m dirt, ruts, 3 m verges) lined tight with 3-4 storey houses to the gate apron. Apron y -60..-13,
|x| < 54. Field battery 6 guns at x ±12, ±26, ±40, y -34, muzzles south (refugee lanes in the gaps). Wall-top guns x ±25, ±60,
±95, y -2, z 50 on 5 m round stone pads with sleeper rails. Gatehouse fronts y -13 (south) / +13 (north). North side: gate road
x = 0 (12 m earth); water strip y +15..+21 (x -250..+145) with a timber road bridge; quay apron x +150..+213, y +8..+110; canal
centre x = 228, **30 m**, sunken (quay top 3.5-4 m above water), quays x 193..213 / 243..263, west lower berth, stair landings
(west y +60, +150, +260; east y +100, +210), cypresses every 25-40 m; twin water arches x 220 / 236 (spans 11-13 m, crowns
8-9 m, grilles raised) replacing the single 24 m gap; high bridge y +40 on 3 square pylons (x 211, 228, 245; 16-18 m, orange
pyramid caps, deck 14 m above water); north of y +450 the canal widens to a 70-110 m river. **Hamlet ALLOWED** (owner opening
ref): cottages at (-60, 40), (-115, 70), (-45, 115), (-150, 125), (55, 135), (95, 190), (130, 60), (300, 80), (325, 170);
windmill (-95, 165) (14 m rust tower, 4 lattice sails r 10, 0.12 rev/s).
**Set dressing.** Inner gatehouse BOTH faces: low red-orange brick front 32 x 9-10 m (#b4643f, cream double cornice #e3d5b5),
wings with small tile lean-to roofs and pointed doors; passage = pointed arch with green trim, **anime 5 x 7 m** (fallback:
keep 14 x 20 m with a 16 x 22 m leaf); **crest leaf** (drop gate) 10 x 12 m brick block with the goddess shield and a corbel row,
hanging on 2 chains in the pilaster bay above the passage. Wall: tan sandstone, 3.5 m pilasters every 16 m as **flat square
stubs** (not g2's stepped merlons), string course at 12 m, ivy near the gate. Field guns: 3.2 m bronze-grey barrel, box
carriage, 2 spoked wheels 2.0-2.4 m, 4 crew each. Ferries: 34 x 10 m oval dark hull, 20 x 5.5 x 3 m cabin with window row, red-
brown barrel roof with 2 rows of discs, A-frame end trusses, lantern, packed deck (≈ 500). Breach after the ram: TALL NARROW arch
12-14 x 24-26 m (replace INNER_HOLE 25 m wide), side wings survive, crack decals 15-30 m.
**Characters.** Armored 15 m (Tripo model, rotate to face +y), plates #e2c47a, red gaps, eye glow allowed ≤ 2 px. Normal upright
run 29 m/s (1.55 steps/s, 18-19 m stride), dust puff per footfall; **only the last 0.4 s**: torso twists 30-40°, **RIGHT shoulder**
leads (owner 11:38 10/26), root never rotates (13:40 10/25); after the hit his momentum carries him into a long forward SLIDE
through the breach (feet skidding, two dust furrows, rubble ploughed ahead) before he stops and straightens (owner 11:38 10/26). Followers: 3 titans 5/7/9 m 120-250 m behind. South: ~150 stragglers through the gun gaps
by 11 s; ~10 freeze at house fronts. Garrison: 24 gun crew (scatter at 12.4), 10 across the apron at 11.8, 12 on the wall top.
North: 3-4k instanced refugees (one 300-600 tri figure via GN, baked flipbook phase) on quays/apron; panic wave 8 m/s from
(0, 30) at impact. Ferries F1 y +300 moving, F2 y +150 moving, F3 moored west landing y +60 (casts off 10.0), F4 east landing
y +100 still loading; 8 m/s timelapse.
**FX.** Golden hour, sun az 245°, el 4-8° (raise to 6-8° if shadows alias); 6-8 smoke columns over Shiganshina bending EAST up
high; muzzle flash + smoke balls; **ricochets**: gold streak 0.12 s, 40 sparks (at least 1 clearly readable); 2 misses = small
fireball + dirt kick; impact: 3-frame white-gold flash, 40-60 keyframed chunks fanning north (6-8 peaking 60-80 m so they read
above the wall), 8-10 boulders left on the lawn; lumpy ochre dust ball 10 → 40 m by (0, +55); south dust ring; mouth steam after.
**Choreography.** Run front y(t) = -400 + 20t + 3t² (t ≤ 1.5), then -363 + 29(t - 1.5): y -320 @3, -233 @6, -146 @9, -88 @11,
-30 @13 · 0-10 ferries glide · 5.8/6.3/6.9/7.4 wall guns fire (hits 6.0 chest, 7.1 shoulder) · 9.0 first field volley, 9.15
shell glances off his FACE · 10.0 F3 casts off · 11.0 second volley · 11.8 crest leaf starts sliding down · 12.4 crews scatter,
12.8 a carriage kicked over · 13.1-13.5 shoulder drop · **13.5 IMPACT** · 13.5-16 he SLIDES through on momentum to y ≈ +45 (feet skidding, dust furrows, rubble ploughed ahead, right shoulder still forward) · 18-23 stands
upright steaming in the dust · 23-32 ferries north, light toward dusk, camera passes them.
**Camera keys (W).** K0 0 (-130, -686, 114)→(-165, -594, 0) 28 · K1 3.5 (-180, -590, 118)→(0, -310, 10) 32 · K2 7.5
(-215, -440, 120)→(0, -190, 10) 35 · K3 11.0 (-225, -275, 118)→(0, -80, 14) 38 · K4 13.5 (-215, -185, 118)→(0, -8, 18) 38 ·
K5 16.0 (-195, -140, 132)→(10, 30, 12) 35 · K6 20.0 (-110, -5, 170)→(45, 125, 0) 32 · K7 24.0 (-15, 130, 205)→(160, 290, 0) 30 ·
K8 28.0 (105, 300, 222)→(228, 580, 0) 30 · K9 32.0 (175, 480, 240)→(228, 1050, 0) 28. Framing locked on him K1-K4 (≤ 1° off
centre); never directly behind him (rear three-quarter at most). Verified (as run A2): ≤ 78 m/s, ≤ 30°/s.
**Must-have lore.** Brick gatehouse both faces + crest leaf on chains (ep02 05:56.4, 06:39.4, 10:01.8; ep01 05:12.6) · gun line
across the apron (10:01.8) · shell glancing off as a gold streak (09:37.4) · crews scatter under his legs (09:49.4) · gate
closing ordered, leaf sliding (09:56.2) · flung blocks + a soldier (10:07.7) · tall arch breach with surviving wings (10:22.2,
10:45.6) · top-down ochre dust ball with boulders and the water strip (10:25.1) · him standing in the haze, mouth steam
(10:35.7) · quays packed, ferries loading/leaving, gangways (05:36.4, 05:40.4, 07:13.1) · twin water arches + 3-pylon bridge
(05:25.5, 05:29.5) · lone ferry at dusk on the widening river (13:36.2).

### g3. Flight north, refugee camps, 846 march, 104th camp (78.4 s)
**Layout.** Maria plain W y 0..5000: river 90-110 m wide teal (#4e6e62; dusk #3c372a), meander amplitude 150 m / λ 1.5 km,
x ≈ +200..+560, **joins Trost's canal at the new east exit M (445, 300)** and runs NW→ the Rose water gate inside Trost (move
today's join at M (556, 346)). Two girder bridges at W y ≈ 1600 and 3000 (3 square stone piers ≈ 25 m, 2 spans, deck 8 m);
straight main road Trost O → Shiganshina inner gate (x ≈ 0) + 6-8 winding tracks; Voronoi fields 80-250 m with hedgerows and
conifer woods; farmsteads/town: see E3. **Relief complex (845-846): M centre (-268, 805), footprint X -333..-203, Y 760..850**
(moved off g3's set (-420, -75), which overlapped decoy corner D and the W480 side wall): cloister courtyard 80 x 45 m inside
2-storey ranges with arcades, east range a 3-storey hall, NE tower raised to ≈ 40 m (cream, pyramid roof; replaces church T4),
NW belfry 15 m, well kiosk, SE stair of 6-8 steps; olive sandstone #9a8f74, maroon roofs #6b4636. Shelter camp: 6-8 barns
30 x 10 m + ≤ 120 drab tents (#9c9480, never white) at **M X -500..-100, Y 960..1130** (north of Rose, clear of square A).
Clearing (winter): **M X -900..+100, Y 1170..1630**, grey mud #64615c, snow patches, 8-10 contour benches, black conifer edge
retreating north. **104th camp C = M (-1450, 1520)** (u east, v north): sunken quarry bowl, floor ellipse 230 x 170 m, rim 14 m
(18-22 m SW), vertically fluted cliffs (lit #a3958c, shade #4a4550), inner rock step 1.5-3 m; back terrace (v +70) with 6 huts at
u -100, -78, -5, +17, +39, +61; lattice watchtower 20 m at (u -45, v +70) with enclosed diagonal stair on its east face; east
terrace u +70..+110 (7 huts); cliff-cut road NE (u +95, v +85) → SE (u +100, v -60); ramp (u +60, v -70); pole field 16 x 8
poles centred (u +25, v +5); mess hall 26 x 8 m at (u -15, v -45) with 8-window band, veranda, porch lantern, chimney; huts
(u -95, v -50), (u -110, v -5); 4 A-frame rigs at v +38, u -10/+12/+34/+56 (steel #5c6570, apex 7-8 m); barbed post fence W→mid-N,
3.5-4 m pointed palisade mid-N→E continuing 300-400 m east; lake 250 x 150 m at (u +150, v +420). Graduation: stone stair 12-15
steps x 30 m on the mess-hall front, 2 tripod braziers. Wall Rose 650 m south is the skyline. Sunset ridge for the march: set
(-600, -2700) = M (-600, -1830), 10-12 titans backlit.
**Characters.** 845-846 refugees drab hooded (E2 decides the march palette); Garrison ration booth; MP (unicorn, dark cloaks) at
the enlistment file. March: 60k agents x 4, 24-30 m wide column, ragged 100-200 m head, ≤ 150 carts (not 1600), ~20 % upright
3 m pikes, titans arrive from horizon/woods (none standing in rows at t 0), 6+ base meshes, no grey "golem" LOD tint, no white
paper chips. Camp: 250 recruits (10 x 25) + Shadis walking the front; rig: Eren UPSIDE DOWN on rig 2, Mikasa balanced on rig 1;
30 sparring pairs, runners, wagon on the cut road; 218 graduates (9 x ~23) + top 10 in a row at the stair foot.
**FX/light.** Dusk (#d9867a, purple zenith) → night (Trost window dots, wall-top torches) → clear sunny morning (no snow) at the
relief complex → grey overcast + falling snow at the clearing → overcast 846 gathering → march overcast, gold sunset 11-18 s
(sky #f5f2cd) → spring morning camp → seasons cycle ×3 → graduation night (braziers, lit windows). Shiganshina smoke recedes.
**Choreography (group-local).** 0-12.9 flight (ferries pass below 0-3.7; night 5-9 with HUD "845: territory reduced to Wall
Rose"; dawn 9-12.9) · 12.9-17.7 decelerate to hover H · 17.7-21 relief courtyard packed, ration queue, then the clearing beyond
Rose; lens eases 28→40 · 21-27.2 time-lapse winter 845 → spring 846 while the view pans ≈ 160° via the WEST; the avenue fills
with the hooded 846 crowd (HUD "846: retake Wall Maria") · 27.2-31.3 run to CAM_IN · **31.3-49.3 march846 (unchanged)**; at
t 15 its look-at goes to (-400, -2600, 10) to catch the ridge and the low sun · 49.3-63.4 flight to camp · 63.4 enlistment ·
66.7-69.2 rig · 69.2-74.0 seasons orbit · 74.0-78.4 graduation night, drift SE to the seam.
**Camera keys.** Flight (W): FA0 0 (175, 480, 240)→(228, 1050, 0) 28 · FA1 3.7 (300, 1250, 320)→(330, 2000, 0) 28 · FA2 7.3
(380, 2600, 380)→(250, 3700, 0) 28 · FA3 10.6 (200, 3750, 320)→(-100, 4600, 0) 30. Camps (M): FA4 12.9 (60, 170, 300)→
**(-268, 805, 0)** 30 · H 17.7 (-145, 605, 250)→(-330, 1020, 0) 28 (at rest) · H2 21.0 (-150, 620, 255)→(-300, 1430, 0) 28→40 ·
**P1 22.55 (-145.5, 613, 253)→(-686, 1058, 0) · P2 24.1 (-132, 592, 248)→(-732, 582, 0) · P3 25.65 (-105, 550, 238)→(-464, 232,
0)** (new pan bridges; without them the look-at swept under the camera at 623°/s) · H3 27.2 (-60, 480, 220)→**(-110, 130, 0)**
40→28 · CAM_IN 31.3 (170, 170, 125)→(-10, -60, 0) 27 · guide 31.8 (178.4, 139.5, 127.8). Flight-to-camp (M): FT0 49.3
(260, -1050, 640)→(0, 150, 40) 28 · FT1 55.8 (-350, 370, 520)→(-900, 1270, 0) 28 · FT2 60.2 (-1250, 1020, 260)→(-1450, 1520, 0)
30 · FT3 63.4 (-1410, 1260, 95)→(-1450, 1530, 0) 32 · FT4 66.7 (-1425, 1320, 85)→(-1445, 1520, 0) 32 · FT5 69.2 (-1480, 1410,
70)→(-1430, 1558, 4) 40 · FT6 74.0 (-1660, 1350, 150)→(-1450, 1530, 0) 30 · FT7 78.4 (-1570, 1190, 170)→(-1450, 1490, 0) 30.
Pan peak now 32°/s. **Speed note:** PCHIP on FA0-FA4 peaks at 412 m/s at 320-380 m; drive 0-17.7 with g3's explicit profile
instead (ramp 45→369 m/s over 0-3.7, cruise to 9.0, one constant deceleration ≈ 42 m/s² to rest at H). This replaces S2/S3
(900 m, 350 m/s), the S5 1.9 km detour and S7 (-3000, 950+DY, 900).
**Must-have lore.** Ferries on a wide teal river under a 3-pier bridge (ep02 13:36.2) · Shiganshina smoke behind (13:44.2) ·
relief cloister packed, maroon roofs, at the Rose foot (19:20.1, 16:26.0) · ration booth (15:28.3) · snowy clearing, hoe lines
(19:26.8) · drab hooded crowds, MP at enlistment (19:29.3, 19:40.3) · one dense column out of the gate on a straight road
(19:54.9) · pikes (19:58.9) · 250,000 → ~100 (20:01.9) · ridge titans against the sun (20:09.0) · sunken striated bowl,
palisade, pale cracked floor (21:24.8, 22:17.0) · watchtower with external stair (22:17.0, ep03 08:23.3) · pole field (22:17.0) ·
mess hall 8 windows (ep03 13:08.0) · rigs + Eren upside down (ep03 11:34.8, 12:07.3) · 218 graduates, stair + braziers, top 10
row (ep04 13:04.8, 13:18.6).

### g4. Trost 850 establishing (20.0 s, frame M)
**Layout/dressing.** Map = section C. Pre-attack: smoke-free, chimney wisps from ~40 houses, low morning haze (mist pass
#c9d4dd). Wall tops: bulge walls paved red-brown brick #8e5a48, Wall Rose pale limestone #cfc4a8; narrow-gauge track (1.5 m) with
spurs to 3.5 m turntables; cannons every ~30 m on bulge walls, 60 m on Rose (20 m on the shown Rose stretches, see C); crate
stacks; wall-top huts every ~150 m (4-6 m, half-timber on stone, red tile); green Garrison flags; outer parapet = **low plain
parapet** (g4's 1.5 m merlons are overruled), pilaster block caps stay; dead root tendrils hanging along the outer coping.
**Characters.** Survey Corps: ~120 riders 2 abreast + 2-3 hooded wagons, 4 m/s south on AV, out through O (door open), gone
before the bolt; ~600 civilians lining AV Y 100-450; Garrison pairs at the guns; 7 cadets at the outer-wall guns X -60..+60 near
O. **Owner order (05:58 #2, 17:01):** Eren (tiny, name tag) stands on the cannon rail above O in the confident "I can do it" pose
→ bolt → the Colossal's skull rises right behind him.
**Light.** Early-morning crisp blue for the departure → clear LATE morning (sun SE, 45-50°, deep blue sky, bright cumulus).
**Choreography.** 0-3 camp lamps fade, dawn · 3-8 Wall Rose lights up; the U appears · 8-13 crossing Rose at ≈ 10.8, master
overview; Corps on AV near C · 13-17 overtake the column; it exits O · 17-19.5 gate closes; Eren's pose on the rail · **20.0
bolt** = seam.
**Camera keys (M).** G0 0 (-1570, 1190, 170)→(-1450, 1490, 0) 30 · **G0b 1.8 (-1495, 1135, 192)→(-1100, 1320, 0) 30** (new yaw
bridge: the opening swing was 48-51°/s, now 32°/s) · G1 4.1 (-1380, 1060, 230)→(-860, 760, 0) 29 · G2 9.1 (-760, 1010, 320)→
(-80, 480, 0) 28 · G3 12.4 (-400, 760, 290)→(-20, 260, 0) 28 · G4 16.8 (-110, 430, 200)→(0, 40, 20) 30 · G5 20.0 (-40, 330, 170)→
(0, 0, 30) 32. Peak 141 m/s at 300 m (if it feels rushed: stretch to 24 s, peak 118 m/s; costs 4 s).
**Must-have lore.** U bulge, straight side walls, big inner pilasters (ep11 07:38.7, ep09 02:30.5) · 16-20 slender bell towers
(ep04 20:23.0, 20:27.0) · HQ keep on a rise (ep08 05:4x F08/000009331) · one green canal down the east side (ep11 07:38.7,
02:33.1) · Corps riding out down AV, slabs across the gate square (ep04 17:23.5, 17:27.5) · cadets at rail cannons on the outer
wall, late morning (ep04 20:23.0, "a while until lunch" 20:17.5) · Colossal skull at the wall edge beside a cannon and a tiled hut
(20:44.8).

### g5. Trost breach, evacuation, Mikasa, Attack Titan (tight 70.0 / full 84.0 s, frame M)
**Layout additions.** Colossal feet Y -18..-28, chin at wall top (Z 50-52), crown Z 60, face 4-8 m outside the parapet. Right-
fist grip X +22..+30 on the coping (fingers over the INNER edge, cracks 8 m on the inner face). Left-forearm sweep WEST over
X 0 → -35 only (true-scale reach), debris flung to X ≈ -70. Kick breach: 15 m at ground (X -7.5..+7.5), straight sides, broken
round top Z 30-34, 3 layers of broken floor beams, iron gate leaf under the outside transom (Z 26) smashed; rubble fan 15-20 m
north, 3 m high. Debris: 20-30 chunks 1-3 m within r 20-90 (2 make the craters), ~80 medium to r 150-220, ~150 plank cards.
Slabs at the blast only rock/roll 2-5 m north on their wheels; titans knock them into the end state during the pour (pit group:
3 toppled, 2 leaning, 1 upright shoved 15 m; avenue-mouth group: 2 leaning at (±9, 80), 4 toppled, 2 standing); ~10 X-stakes.
Titan lanes L1 (over the pit gap) / L2-L3 (pit flanks → AV) / L4-L5 (ring road → radials); ≤ 3 abreast in the hole, 2-2.5/s.
Inner gate and E, MA, SS, Q2, tower T, roof R, BT: see section C.
**Set dressing.** Inner bastion brick #7a4a3a, quoins/cornices #8d8a82, crest relief at Z 20-23; arch 5.0 x 6.5 m, grey
voussoirs, **dark 22 m tunnel, no green field visible**; E paved dark setts #6f6c66; corner turret (-140, 790), pyramid-tower
building (-95, 815); east grass slope X -105..-60 rising 0→4 m with 3-4 dark trees, terrace X -105..-60, Y 820..840, ledge
X -133..-105, Y 849..853; west: pilaster, wall face, one tree at X ≈ -172. **Cart:** flatbed 5.4 x 4.0 m at 1.1 m, 4 spoked wheels
1.6 m (track 4.8 m), 2 dark horses in the tunnel facing NORTH; load = 12 burlap sacks in a rope lattice, 5.0 L x **5.3 W** x 2.8 H
(wider than the arch, wedged against both jambs). **End state: backed out 6 m, swung east 40°, load centre (-122, 842), yaw 320°,
horses' heads ≈ (-127, 848); clear lane X -146..-134. It never drives through (owner 00:44).** Fallen Abnormal prone at
(-96, 794), head NW. MA: flagstones, 5 steps at Y 440-443, 6 m rubble heap of 30-40 dark blocks against a jagged end wall ≤ 10 m;
west side blank dark 20 m face, east side light ashlar 18 m with arched windows and a 6 x 8 m stain at Y ≈ 445. Q2 pale limestone,
domed arcade on its north side; tower T 8 x 8 x 34 m, top 8 m bursts. Remove the white plaza fountain disc and the white needle
church (both wrong).
**Characters/titans.** Colossal (as g1, right-hand grip, left sweep, steam + 200 embers). Pour P1-P35 (3-4 m 25 %, 5-7 m 45 %,
8-10 m 20 %, 12-15 m 10 %), locomotion at 2x with matched stride; 2 abnormals 8-10 m/s up AV. Abnormal AB 12-13 m pot-bellied,
10-11 m/s with a dust cloud as tall as itself. CAP 8-9 m stocky bowl-cut grin; LH 7 m long-haired; CC ≈ 12 m crew cut; TR1 5-7 m
bald; BT 10 m bearded; AT 15 m (long dark-brown hair, pointed ears, patchy red muscle, green eyes ≤ 2 px in roar/stomps). Humans:
Mikasa (red scarf #8e1f1f must read at 10-14 px) + 1 Garrison soldier; merchant (bald, brown coat) + 3 guards (#2e3440);
crowd ≈ 5,500 in E (≈ 1.6/m²) + AV tail 300 + 50 on EVS, arms raised at the load, 4-6 m gap at the cart rear; defence lines:
vanguard ≈ 30 on roofs ringing GS, middle guard 12-16 squads Y 250-520, rear guard ≈ 20 around E/HQ; 104th stream 20-25 cadets
behind Mikasa; Armin + Connie.
**FX/light.** Clear late morning (sun 135°, 45-50°) → cloud roll-in 14-30 (full) → dark overcast at E → breaking overcast with
2-3 sun shafts in the alley. Bolt: yellow-gold, 2-frame spike, 1-frame near-black, 1 more spike. Kick: sepia shock ring 60 m/s to
r 120, 60-80 m dust column, dust sheet along the wall top, grey smoke from the hole; crater wisps 15-20 m; 10-15 smoke columns
from t 14 (dark grey-black near source); wall-top grapeshot from t 12; ODM puffs; corpses steam and shrink (BT → skeleton in a dark
pool); AT emergence = small 25 m gold bolt at BT + 25 m steam burst (not a world flash); tower burst 20-30 m tan cloud. Rain:
optional P2, default OFF.
**Choreography (full → tight).** 0-0.5 bolt · 0-2.5 skull rises · **5.5 → 4.0 KICK** · 7.0 → 5.5 right-hand grip · **8.0 → 6.5
first titan through** · 8.5-10.5 → 7-9 left-arm sweep, Eren (tiny) runs up the forearm · **10.5 → 9.0 Colossal steam explosion**
· 10-26 vanguard engages, 3 nape kills · 14-30 smoke columns + clouds · **31 → 26 AB enters EVS** at (-18, 709), Mikasa + soldier
follow · 31-40 → 26-33.8 the jam · **40.0 → 33.8 kill** at (-85, 782), skid to (-96, 794) · 41.5 → 35 she stands on its back ·
43 → 36.5 ODM hop over the crowd, lands (-138, 838) · 44 → 37.5 walks through the opened lane · 46 → 38.5 bodyguard shoved ·
**47.5-50.5 → 39.4-41.6 "Move the wagon": cart backs out and swings to its end state** · 50.5-61 → 41.6-51 crowd drains from the
arch outward (≈ 6x arch flow so the plaza visibly empties) · 59 → 50 the 104th stream flies north · 60.3 → 51 TR1 killed ·
62 → 52.5 gas sputters · **63 → 53.3 Mikasa falls** at (-262, 400) · 63.5-64.5 → 53.6-54.4 CAP and LH climb in over the rubble ·
64.5 → 54.5 BT torn open · 65-68.5 → 54.8-57.4 AT sprints along SS · **68.5 → 57.4 punch** · 70 → 58.3 roar · 71.5-72 → 59.1-59.5
stomps · 72-75 → 59.5-62.1 Armin/Connie lift Mikasa to roof R · 77.5 → 64.3 boxer stance · **78.8 → 65.5 tower slam** · 80.3 →
66.8 nape stamp · 84 → 70.0 AT walking NNE at (-222, 531), 6 m/s = seam.
**Camera keys (M; t full / tight).** C0 0/0 (-40, 330, 170)→(0, 0, 30) 32 · C1 5.5/4.0 (-33, 290, 166)→(0, 5, 26) 32 · C2 14/12
(-75, 370, 200)→(0, 40, 8) 28 · C3 23/18 (-20, 470, 205)→(-15, 150, 0) 28 · **C3b 27/22 (10, 530, 200)→(-330, 420, 5) 29 (new)**
· C4 31/26 (40, 590, 195)→(-170, 790, 10) 30 · C5 35/30 (10, 600, 170)→(-130, 815, 8) 32 · C6 47/39 (-45, 690, 125)→(-138, 838,
6) 34 · C7 51/42 (-48, 693, 125)→(-139, 837, 6) 34 · **C7b 55/46 (-165, 690, 140)→(-400, 600, 5) 32 (new)** · C8 59/50 (-275, 655,
155)→(-262, 425, 0) 30 · C9 67/56.5 (-270, 640, 150)→(-262, 422, 0) 33 · C9' 72/59.5 (-280, 655, 148)→(-258, 440, 0) 33 · C9b
80/66.5 (-420, 455, 140)→(-236, 505, 10) 32 · C10 84/70 (-345, 455, 175)→(-185, 640, 15) 30. The two bridge keys fix yaw flips
of 46°/s (C3→C4) and 81°/s (C7→C8); now ≤ 29°/s, ≤ 43 m/s, heights 125-205 m.
**Must-have lore.** Yellow/black flicker then skull at the wall edge beside a cannon (ep04 20:42.7-20:44.8) · steam + embers
(22:18.0) · gatehouse bursts, slabs rocked, blocks on the grass (20:56.2-20:57.9) · soldiers flung off the wall top (21:01.1) ·
fingers over the inner edge with cracks (21:27.2) · forearm sweep, cadet on the forearm (22:10.5, 22:14.0) · breach + rubble +
2 jagged steaming craters (23:55.8) · leaning slabs at the avenue mouth (21:37.1) · loose titans in the square, one on the pit,
X-stakes (ep07 01:21.7) · smoke columns all over (ep09 02:10.0) · bastion with crest, east-wing door, pilasters both sides,
grass slope (ep06 05:46.5) · sacks overlapping both jambs, men pushing (05:56.0) · gap at the merchant (06:26.1) · Abnormal
charging with a dust cloud (06:52.9) · corpse at the crowd's edge, Mikasa on it (07:29.0, 07:35.7) · lane through the crowd
(08:17.5) · cart end state east of the arch, horses facing the arch (09:03.9) · alley canyon dead end, steps + boulders + broken
wall (ep07 13:00.1, 15:01.4) · CAP, LH (13:28.3, 16:37.3) · punch from the side (17:23.0-17:29.5) · stomp (18:03.2) · roof
rescue (18:52.2) · CC in the square, boxing, tower top bursts, nape stamp (18:59.0, 19:29.1, 19:34.1, 19:52.0).

### g6. Supply HQ, lift operation, Eren emerges (tight 69.5 / full 74.0 s, frame M)
**Layout (integrator ruling: g6 orientation; the only compass frame is ep09 21:36.8 F09/000031091).** Keep HK at the WEST end,
centre (-250, 640): tier 1 X -266..-234, Y 624..656 to Z 28, roof walk with crenellated parapet (merlons 1.2 m; the keep's
crenellation is the owner's HQ ref and stays), 4 corner turrets 6 x 6 m to Z 33, slate-blue pyramid caps to Z 37; tier 2
20 x 20 m (X -260..-240, Y 634..654) to Z 44 carrying the **7 round-arched windows** (Z 34-37) on its south face, 4 small turrets
to Z 49; clock/bell tower 10 x 10 m to Z 54, cap Z 58, white clock face south. Terrace HT X -270..-230, Y 612..624, Z 2.5 on a
battered podium, stair on its west side. Wing HW X -234..-136, Y 628..652, eave Z 24, ridge Z 41 (55°), rusticated ground storey
with 12 round arches + a large arched door at the storeroom's west end, pilaster strips, dark slate #3d434b, 4 brick chimneys.
Storeroom HS X -205..-169, Y 631..651 (floor Z 0, rafters Z 6.0 every 6 m, brick groin vaults to Z 9.5); lift room HU above
(floor Z 10); lift shaft/cage centre **(-187, 641)**. Plaza PZ: south apron X -275..-100, Y 570..624 (opens east onto AV at
X ≈ -95) + west strip X -300..-266, Y 570..660, pale sand setts #cdbf9f. Gutted house GH at (-200, 566) (5 m black slot, rubble
cone r 8). Back range + courtyard (P2) X -234..-150, Y 652..700. Hall hole 3-4 m in tier 2's south face at Z 29-33.
**Interior.** Dark red brick #6b3528, brick piers 1.2 m every 6 m, rafters #4a3427 (cutters crouch on them), plank/stone floor,
upright dark-bronze gas cylinders with brass valves in timber stalls (NOT blue chairs), 10 torches. Cage 5.5 x 5.5 m (plank
floor, planked sides + baluster rail), 4 chains to a pulley block with a lantern, X-braced timber guide tower; firing level Z 2.8.
Cutaway: ONLY the 36 m bay dissolves (Dithered alpha step over 2 s, reverse later); south wall cut to Z 4.5 with dark caps
#2b2420; shadow-only proxy keeps the sun out (Ray Visibility: Camera off, Shadow on).
**Characters/titans.** AT 15 m, always OUTSIDE ("won't be attacked as long as it's rampaging outside", ep08 11:01.2). 14
exterior titans at t 0 (6 at the facades, 2 on the keep roof walk peering into the hole, 2 climbing the keep, 4 wandering);
later 3-4 small biters, bearded 8 m, pot-bellied 8 m (kept out of frame), blond long-haired. Storeroom: exactly 7 titans 3-4 m
→ ring r ≈ 4.5 m. ≈ 30 gunners kneeling in the cage; 7 cutters (Mikasa, Annie, Reiner, Bertolt, Jean, Sasha, Connie) on
rafters, **Sasha and Connie miss, Mikasa and Annie finish**; Jean's 8 crash through windows; ≈ 12 burst out of the west arched
door and line the wing roof by the chimneys. Eren (olive shirt, harness, no ODM, no jacket) rises from the nape, THEN Mikasa
drops in. Keep-roof tableau: Mikasa + Armin kneeling by Eren, Jean, Reiner, Bertolt, Annie standing.
**FX/light.** Overcast mist → clearing (sun SW 40°) → warm gold 28°; volley: 30 star flashes in one 2-frame burst + 2,000 W
spike + powder puffs; steam = thin wavy ribbon columns 40-80 m per corpse (NO opaque blob); collapse: beige dust bow wave, 3 s
white-out, embers; corpses darken to scorched brown; 2-4 town smoke columns; window glints.
**Choreography (full → tight).** 0-10.5 → 0-8 AT from (-222, 531): walk 6 m/s, one street punch (≈ 4 → 3), run to the plaza
entry (-230, 572); Jean's squad crashes in (4.5/5.2 → 3.5/4.0) · 12.4-14 → 9.9-11.5 leap up the keep face, punch through the hall
hole, tackle both roof-walk titans to the apron · 14-24 → 11.5-19.5 rampage (4 → 3 kills), corpses C1 (-232, 600), C2 (-212,
596), C3 (-192, 594), C4 (-252, 606); cutaway dissolve 21-23 → 17-19 · 24-27 → 19.5-22.5 cage descends Z 10 → 2.8 · 27-32 →
22.5-27.5 ring forms · **32.0 → 27.5 VOLLEY** · 32.3-33.3 → 27.8-28.8 cutters drop · 34.8/35.2 → 30.3/30.7 Mikasa, Annie finish ·
38-40 → 33.5-35.5 roof returns · 38.5 → 34 breakout · 36-43 → 31.5-38.5 swarm, bearded-titan nape bite · 43-46.5 → 38.5-42
roar, arms hanging · 46.5-49.5 → 42-45 collapse, skid 10 m east, nape at (-178, 619) · 53-55 → 48.5-50.5 Eren rises · 55-58 →
50.5-53.5 Mikasa drops in, hugs him · 60-64 → 55.5-59.5 tableau on the keep roof · 64-74 → 59.5-69.5 exit east to the basin.
**Camera keys (M; full / tight).** H0 0/0 (-345, 455, 175)→(-185, 640, 15) 30 · H1 9/7 (-330, 470, 150)→(-225, 605, 10) 30 · H2
17/14.5 (-255, 470, 120)→(-205, 600, 6) 32 · H3 24/19.5 (-198, 565, 100)→(-187, 643, 1) 38 (pitch 51°, cutaway) · H3b 38/33.5
(-194, 562, 100)→(-186, 642, 1) 38 · H4 43/38.5 (-150, 495, 110)→(-185, 620, 8) 32 · H5 51/46.5 (-110, 515, 105)→(-182, 617, 4) 35
· H6 57/52.5 (-130, 540, 90)→(-180, 619, 4) 40 · H7 64/59.5 (-90, 560, 115)→(-215, 615, 18) 32 · H8 74/69.5 (220, 650, 130)→
(345, 810, 0) 32. Verified ≤ 39 m/s, ≤ 25°/s, ≥ 90 m.
**Must-have lore.** 3-tier keep on a rise, wing east (owner refs, F09/000031091) · titans at the facades and on the roof walk
peering in (ep08 08:25-09:15) · punch through the hall hole + tackle (09:15.7, 09:20.4) · brick storeroom, rafters, torches,
cylinders (ep08 13:5x F08/000020366) · 7 titans of 3-4 m (11:43.7) · cage on 4 chains with lantern, guide tower (F08/000020462,
F08/000021520) · volley then 7 drops (15:14.9-15:21) · Sasha/Connie miss (15:25-16:00) · breakout + wing roof (17:34.1, 17:40.7)
· swarm biting him (17:56.0) · roar arms down, collapse along the wing base (19:33.4-19:37.7) · Eren rises, then Mikasa (20:02.4-
20:21.5) · gutted house (18:5x) · end tableau with steaming corpses (F08/000031928).

### g7. Cannon basin, half-shift, salute, Pyxis (PACE 45.0 s default; full 116 s kept in g7 spec, frame M)
**CORRECTION (owner 15:25 10/26, supersedes the layout coordinates below): LORE POSITION + HANDEDNESS.** In the anime the basin is
on the NORTH face of Wall Rose (Rose interior), beside the canal water gate; seen from the Garrison bank looking at the wall, the
water and barred water gate are on the LEFT (owner's capture = ep09 F09/000028171). The earlier N-S mirror into Trost flipped
left/right and is CANCELLED. Build it on Rose's north face: apply Y' = 1740 - Y to every basin element below (X unchanged):
floor KF X 340..385, Y 875..907, Z -3.6; bank SB Y 907..919; top terrace TT Y 919..927; plinth PL Y 902..912; west flight SW
Y 885..907; GB X 308..338, Y 875..891, deck Z 20; cannon (318, 883, 20); T_K (322, 922); GH X 341..377, Y 928..948; half-timbered
range X 377..387, Y 927..970; boats (389, 897) and (389, 889); L_K derrick (338, 872, 50) on the Rose top; water gate WG stays in the
wall at X 393..411 with the canal continuing NORTH at X 400. Check from the bank camera: canal on the left (east), tower T_K at the
near right. These few basin buildings north of Rose are an allowed exception (lore). No titans north of Rose (safe interior).
Camera: re-key g7 0-19.5 s on the NORTH side (mirror the listed keys with Y' = 1740 - Y, then smooth the g6 H8 → g7 crossing over
the wall with the speed/turn checker); keys from 23.5 s on are already north of the wall.
**Old layout (coordinates superseded, details still valid; owner: basin INSIDE Trost at the Rose foot, mirrored N-S from the anime).** Floor KF X 340..385, Y 833..865,
**Z -3.6** (mossy cobbles: pale sandy south half, green north half); canal water **Z -4.2** for the whole inner run (deepen g4's
banks by 1.2 m); west pier PW X 331..340, east pier PE X 385..393 (foot in the canal), both battered 8° to Z 30; water gate WG
X 393..411 (18 m, crown Z 7, iron portcullis); bank SB X 340..385, Y 821..833, 12 steps (0.3 / 1.0 m), darker nosings; plinth PL
X 357..367, Y 828..838, top Z -0.6, flat to the edge (no parapet), wavy relief band; west flight SW X 340..348, Y 833..855 (the L);
top terrace TT Y 813..821; gun bastion GB X 308..338, Y 849..865, deck Z 20 (one with PW), 2-rail spur + 3.5 m turntable, cannon
at (318, 857, 20) aimed at the trio (bearing 95°, depression 27°, 48 m); bell tower **T_K (322, 818)** 8 x 8 m, cream, belfry Z
20-26, red pyramid to Z 33; Garrison building GH X 341..377, Y 792..812 (clock oculus in the west gable, green sashes); half-
timbered range X 377..387, Y 770..813; 2 rowing boats (389, 843) and (389, 851); hoist **L_K**: basket stop (342, 861), A-frame
derrick + wheel + winch hut at **(338, 868, 50)**. Pyxis spots: **S1 (-120, 866, 50)** (south edge, just east of the inner gate:
talk, looking south) and **S2 (-20, 874, 50)** (north edge: speech, 6 dark-green banners X -45..+5). Square A (-20, 935).
Titans: none within 250 m of the basin; ≈ 40 packed along the Rose foot from D to X ≈ +100, densest X -170..-110.
**Dressing.** Wall face pale #bdb5a3, lower 12 m damp #6f6a58 with moss/ivy streaks (owner 13:49 QA); piers lighter ashlar,
rounded arrises; bank cream ashlar #cdbf9a. Cannon 4.2 m gunmetal on a slatted wooden drum carriage. Rose top: limestone, two
tracks, cannons every 20 m on both edges at X 300..350 and X -160..+40, crates, red-tile huts, hoist cages.
**Characters.** Trio on the floor from the start at (362, 852): Eren seated, Armin kneeling, Mikasa (361, 849) on guard, blades
drawn; captain (bearded) on PL; 48 Garrison (6 on PL incl. 2 riflemen at the front corners; 10 + 10 on the flights; 14 on TT; 5 on
SW); gun crew 4 + signaller on the pier top; Pyxis (bald, red sash) + Anka + 2 riflemen; ≈ 2,000 troops at A; ≈ 16 elites.
Half-shift skeleton: torso only from the floor, 10 m, skull 2.2 m, ribcage 6 x 5 m arched over Eren's spot, hunched 30°, facing
250°; right arm curled as a shield (forearm hand low at (354, 851, 2), scorch patch), left arm bones on the floor; bone #e6d3a8,
muscle #9a1f24 on skull sides, neck, shoulders, upper arm.
**FX/light.** Golden late afternoon, sun az 255°, el 28° → 12° by the leap; muzzle star + puff + recoil, shell 0.35 s (no white
line); ignition flicker + dust ring; orange fireball r 6-8 m on the forearm; **steam "LOTS"**: burst to r 25 m in 1.2 s, column
12 → 30 m wide to Z 85-95 leaning 10° east, blanket 4-6 m deep (Garrison waist-deep), thins by ~8 s (pace); 10-15 town smoke
columns; HQ steam behind. No green flare here (g8 owns it).
**Choreography (PACE, owner 05:58 #4 "quick").** 0-3 transit, trio already on the floor, turntable swings 40° · 1.5 captain's
arm + pier-top signaller · **3.00 FIRE** · 3.05 black arm sweep, skeleton erupts · **3.35 IMPACT** fireball; caption "Eren blocks
the cannonball" 3.5-6.5 · 3.4-8 steam burst + column, Garrison recoils, reload · 7-8 Eren tears out of the nape · 8-9 Armin walks
out alone, hands up · **9-13 SALUTE** (4 s hold, fist on heart) · 12.5 captain raises his arm again · **13.5 Pyxis catches it**,
walks down to the floor 13.5-16 · 16-19.5 L_K basket rises to the Rose top · 19.5-27 time-lapse walk west on the rails · 27-30 S1:
Pyxis looks south, hands behind back; Eren on the rail; they turn and sit facing north · 30-33 crossing to S2; A fills to 2,000,
banners · **33-38 speech**, Eren beside Pyxis; deserters stop and turn back; fist ripple at 37 · 38-42 deployment (hoist cages,
ODM up the north face, column west toward D; Pyxis's post behind a timber railing at (-20, 866)) · 42-45 elites leap off south
over the roofs toward B0 = seam.
**Camera keys (PACE, M; verified ≤ 104 m/s at 190-230 m, ≤ 26°/s, ≥ 90 m).**
| t | camera | look-at | lens | note |
|---|---|---|---|---|
| 0.0 | (220, 650, 130) | (345, 810, 0) | 32 | = g6 H8 |
| 3.0 | (283, 740, 96) | (361, 850, 4) | 38 | FIRE; no push-in |
| 8.0 | (266, 720, 122) | (363, 855, 24) | 32 | steam burst + column |
| 11.0 | (296, 752, 90) | (360, 842, -1) | 40 | salute hold (Armin ≈ 25 px) |
| 13.0 | (297, 753, 90) | (360, 842, -1) | 40 | Pyxis enters frame left on TT |
| 16.0 | (330, 742, 105) | (350, 852, 10) | 38 | to the basket |
| 19.5 | (450, 805, 150) | (343, 862, 40) | 36 | east of the canal, rising with the basket |
| 23.5 | (250, 1010, 230) | (20, 867, 48) | 34 | over the wall line, pacing the walk west |
| 27.0 | (-20, 1046, 190) | (-118, 846, 28) | 34 | S1: Pyxis from behind, Trost beyond |
| 30.0 | (-14, 1050, 188) | (-118, 846, 28) | 34 | S1 hold |
| 33.0 | (15, 1090, 165) | (-20, 905, 28) | 33 | crossing to S2, A filling |
| 38.0 | (30, 1100, 150) | (-20, 900, 32) | 36 | speech |
| 42.0 | (-20, 1000, 190) | (-35, 730, 5) | 32 | rising over the crest, deployment |
| 45.0 | (-40, 960, 205) | (40, 540, 0) | 30 | = C15 = g8 K0 |
**Must-have lore.** Sunken floor at the Wall foot between battered piers (ep09 11:51.3, 15:14.0) · canal + barred water gate + 2
boats (19:35.0) · trio already there, Mikasa blades drawn (11:45.3) · bank, plinth, Garrison L (ep10 15:57.1, ep09 17:19.5) ·
riflemen kneeling at the plinth corners, captain's arm (ep10 17:09.5, ep09 21:08.6) · gun on the pier-top bastion, signaller,
tower beside it (ep09 15:31.8, 19:57.9; ep10 10:16.9) · order flash → bite → black arm → red arm → fireball (ep09 21:14.3-21:34.8)
· torso skeleton, gold ribs (22:13.6) · steam swallowing the basin, one column seen across town (ep10 05:15.7, ep09 21:36.8) ·
Armin alone, salute (ep10 14:38.5, 16:38.5) · Pyxis catches the arm (17:36.5) · walk on the rails past turntable guns to the
inner-gate top, looking south, then sitting north (18:35.4, 19:29.4, 20:38.9, 21:45.6) · speech with Eren beside him, banners,
packed square with obelisk (ep11 07:16.5, 07:51.3, 13:34.3, 20:35.4) · packed wall top, hoist cages, leap off (18:31.9, 20:43.0,
20:44.9).

### g8. Boulder, seal, Levi, mop-up, pyres (tight 75.0 / full 136.0 s, frame M) — TOP EFFORT
**Layout (integrator ruling: B0 = (290, 262), east side, opposite decoy D; g4's (-150, 230) and the code's (-68, 420) are
dropped).** Boulder Court X 225..318, Y 236..292, cobbled, ringed by 4-storey terraces (eaves 13, ridges 19) with dormers and a
stepped-gable house on the north; belfry 8 x 8 m at (228, 290), 42 m, red-tile pyramid cap; raised octagonal lawn bed 30 m across,
0.6 m kerb, centred (290, 262), ring of 14 dark angular rocks, shrubs, 2 cypress-like trees + 1 leafy tree at its NW edge; ball
D 14 m at (290, 262, 7.4) sunk 0.2 m into the bed, rubble skirt 14-20 rocks, second rock 6 m at (308, 247); approach lane NW
(232, 300) → (180, 360) with a green hanging sign; exit gap 16 m at (284, 236). Route BR (438 m) and gate square: section C.
Wall-foot strip on the SE curve widened to 38 m of dusty open ground (r 437..475, phi 8°-37°) with X-fences, plank ramps, 3-4
sheds, crates, toppled slabs. Gate-side lift moved to (-62, 10).
**Dressing.** Ball: 14.0 x 14.0 x 13.6, low-frequency ±0.25 m only (stays round, owner 15:29), warm grey #8f8a82, dark charcoal
marbling #3b3a3a, pale patches #c9c4b8, fine cracks; **one radius 7.0 everywhere** (today 6.0 / 6.5 / 7.6 / 15.2 mismatch).
Mikasa's roof (252, 300) caves in (10 x 8 m hole). Footfall crack decals, dropped blades/canisters, small dark stains. Gatehouse
town face: brick #8a4f3c in 3 tiers with pale cornices #cfc3a6, small round-arched windows, sandstone pilasters #c9b48e, dead
vines. Plug Λ: ≈ 60 instanced dark tendril curves #2a1f1b from the ball to Z 38, base 15 m, tendrils 5-10 m over the brick, 2
smoke cards. Mop-up: 6-8 tall grey crane pylons with gear wheels at D; hoist scaffold at D. Captured-titan frames 12 x 8 x 10 m and
8 x 6 x 7 m with 12-16 diagonal poles + ropes. Cleanup: covered-body rows (2 x 0.6 m, dark cloth) along AV Y 120..400 and the GS
ring road; handcarts; pyres 6 x 4 x 2 m log stacks. Skip the vomit ball.
**Characters.** Eren (ODM transform on the roof at (262, 300, 19)); Mikasa; Armin; Ian's squad 4 (40-80 m ahead); Rico's squad 4
(40-60 m behind; Rico = silver bob, NO glasses); Mitabi's squad 4; 6 trainees (roof ridge 60 m north of the court, later on foot
near (150, 120)); ≈ 400 decoy soldiers on the wall tops at D (20-30 on wires, hoist cage); Pyxis + 5 at PY; Levi (Survey cloak);
≈ 40 Survey Corps on day 2; ≈ 60 cleanup workers with white face cloths. AT: skin strips to red muscle (vertex mask 0 → 0.9:
torso and thighs raw by mid-carry); berserk at (260, 289); sits against the ball on its bed; lift: squat, chest, overhead, hands at
9-10 and 2-3 o'clock, head bowed; loaded walk 7 m steps, 1.5 Hz, lean 15-20°, bob 0.4 m, sway ±0.6 m, dust + crack per plant;
seal: roar, drop to (0, 17.5, 7), crouch-shove, slump. Escort titans 12-14 (4-8 m 70 %, 9-10 m 20 %, one 12 m class, one crawler);
gate-square titans (5 at the pit lip, 1 lying in the pit, 2-3 entering, 5 facing the plug after the seal: big 10 m on the west, two
thin ones in the centre, one clawing); decoy mass 60 → 100 at D, arms up.
**FX/light.** Golden late afternoon (sun WSW 12°) → red flare still golden (10°) → carry warmer/redder (8° → 3°) → yellow at
sunset → Levi at pink-violet dusk → night/day time-lapse mop-up (cannon pulses at night are `[INF]`) → hazy day cleanup → golden
end. Flares = thin vertical smoke trails with a bright head (80 m/s, stop at 200 m in 2.6 s, drift, widen 1.2 → 6 m): **GREEN**
#6fae4f from GF, 20 s; **RED** #c8422c from RF with a white shock ring, lingers ≈ 60 s; **YELLOW** #f2d03c from YF, 25 s (+
optional relay at PY 1.5 s later). Transformation: yellow bolt 300 m, 30 m flash sphere, 40 m steam/dust dome. Breach glows orange
until the ball lands. Seal burst 40 cards to r 30 m + 30 chunks. Steam ribbons on the ball. Blade streaks #cfe8ff 0.15 s.
Pyres: flame cards 6-10 m, black-brown columns 150-200 m, 2,000 W lights (≤ 8 live point lights).
**Choreography (tight 75 s; full times in g8 spec section 6).** 0-4 hand-off, decoy at D in the distance · **3.0 GREEN** (Rico, GF)
· **4.5 transformation** on the roof beside the ball · 6.0 fist smashes Mikasa's roof · 7.0 second swing misses · **8.0 RED**
(Rico, RF; before the self-punch) · **9.5 self-punch** · 10-11 staggers back, **sits against the ball** on its bed · 11-15 squads
on the ridges, 7 m titan killed, 12 m class killed by Rico's squad; **12.0 Armin lands on the nape, 13.5 stab** · 15 wakes (steam
surge) · 15-19 stand, turn, squat, lift overhead · **19-47 CARRY**: R1 ≈ 20.5, R2 ≈ 26, R3 ≈ 30, along the wall-foot arc 30-42
(titans down a brick street from the west, trainees lure them; 38 a 6 m titan falls into the pit's outer trench), R4 ≈ 43, Ian
grabbed at IA ≈ 43.5, crouching 10-12 m titan at (44, 27) killed by Mikasa 44.8, R5 44.5, R5b 45.5, R6 47 · **47-52 PLUG**: roar 47,
drop 47.5-48.5, shove 48.5-49.3, **jam 49.5** (dust burst, glow cuts out), slump 50-52 · 50-54 Λ spire grows, 5 titans face it ·
**53.0 YELLOW** (Rico, YF) · 55-60 Levi drops at LV (55.5), two cuts (56.3, 56.7), stands on the corpse (57.5) · 60-66 mop-up time-
lapse (night pulses at D 60-63, day + Survey Corps 63-66, captured titans appear 65) · 66-71 cleanup: body rows, pyres light one by
one (C, AV, (150, 330), GS east) · 71-75 golden end hold.
**Camera keys (M).**
| key | t tight | t full | camera | look-at | lens |
|---|---|---|---|---|---|
| K0 | 0.0 | 0 | (-40, 960, 205) | (40, 540, 0) | 30 |
| K1 | — | 6 | (-140, 950, 190) | (-410, 800, 15) | 30 |
| K2 | 6.0 | 12 | (-40, 760, 210) | (230, 320, 0) | 28 |
| K3 | 12.0 | 22 | (120, 470, 150) | (290, 262, 8) | 35 |
| K4 | 15.5 | 30 | (160, 420, 120) | (288, 262, 10) | 42 |
| K5 | 19.0 | 37 | (175, 395, 105) | (282, 215, 12) | 40 |
| C1 | 28.0 | 50 | (95, 290, 105) | (275, 150, 12) | 38 |
| C2 | 38.0 | 64 | (40, 230, 100) | (180, 62, 12) | 38 |
| C3 | 45.0 | 78 | (-60, 175, 95) | (40, 24, 12) | 40 |
| S1 | 49.5 | 86 | (-75, 150, 90) | (3, 14, 12) | 42 |
| S2 | 54.0 | 95 | (-95, 225, 135) | (0, 20, 40) | 32 |
| L1 | 58.0 | 104 | (-105, 245, 140) | (0, 30, 15) | 34 |
| **B1 (new)** | 62.0 | 110 | (-60, 330, 200) | tight (-280, 170, 10) / full (-330, 230, 10) | 30 |
| M1 | 66.0 | 116 | (-60, 430, 290) | (-410, 800, 20) | 28 |
| E1 | 71.0 | 126 | (150, 600, 190) | tight **(-120, 420, 0)** / full (-40, 300, 0) | 30 |
| E2 | 75.0 (+76.0 guide) | 136 (+137) | (200, 760, 240) | (-20, 300, 0) | 28 |
Carry keys C1-C3: 170-230 m from the titan, 90-105 m up, pitch 22-26°, side/front three-quarter from the town side (never behind
his back), so the legs and both raised arms read under the ball. B1 fixes a 96°/s (full) / 176°/s (tight) yaw flip L1→M1. Verified:
full ≤ 40 m/s, ≤ 30°/s; tight ≤ 67 m/s, ≤ 30°/s; min height 89 m.
**Must-have lore.** Ball round, ≈ 14 m, marbled, steaming (ep13 07:59.5, 12:28.4) · court among 4-storey terraces with belfry,
second rock, wall close behind (ep11 18:23.9, 08:31.9) · decoy: packed wall tops, wires, 60-100 titans in the corner (18:31.9; ep12
03:36.1) · GREEN by Rico (ep11 20:57.6, 21:02.5) · transformation beside the ball (21:27.7, 21:54.9) · berserk: roof smash → red
→ self-punch → sits against the ball on its rock-ringed bed (ep11 22:16.8; ep12 05:03.3, 05:12.2, 05:25.8) · red lingering over the
town (05:59.6, 06:14.8) · Armin stabs the nape, eye glow (15:49.8, 16:37.9, 22:12.9) · lift and overhead carry (ep13 08:28.8,
10:01.9) · carry along the wall, pilasters behind, open dusty ground, X-fences (10:17.7, 10:24.2) · deaths kept small (10:31.1,
10:48.1, 11:48.1) · sunken pit with plank C-trenches, titans at the lip, one lying in it (08:43.5; ep11 10:05.0) · Mikasa kills the
crouching titan (12:03.9) · the push, dust (12:28.4, 12:28.8) · slump, bollards in front, Rico on the deck (12:42.6) · YELLOW from
the gate, seen from the Rose top (12:57.7, 13:04.5, 13:08.5) · Λ plug, ball at its base, 5 titans, spruces west, bushy tree east,
dark holes (13:16.5, 13:20.5) · Levi's two cuts, dusk silhouette (14:05.7, 14:37.8) · cannons around the clock, cranes, mass at the
wall foot (15:19.2, 15:24.3, 15:20.3) · 2 captured titans in pole frames (15:47.2) · body rows, face cloths, pyres (16:21.4, 17:21.2,
18:52.1).

---------------------------------------------------------------------------------------------------------------------

## C. Trost master map (frame M; X east, Y north, Z up; O = (0, 0))

**Outline and walls.** U bulge: Wall Rose straight Y 870 from X -480..+480 (south face 865, north 875); side walls X ±480 from
Y 870 to 480; south half circle R 480 about (0, 480); tip = O. 960 x 870 m (trost.py W 480, S 390, R 480; today W 620 / S 250 /
R 620). Walls 50 m tall, 10 m thick, 10 m wall walk. Inner face pilasters 7 x 3 m at 28 m centres with block caps 3 m above the
parapet; outer face flat with 3 m counterfort grooves every 20 m; low plain outer parapet (no merlons). Wall-foot road 6 m
(except the SE 38 m strip and the gate square).

| id | element | position / extent (M) | notes |
|---|---|---|---|
| O | outer gate | (0, 0) | outside: rust-red riveted iron frame 20 m wide, ≈ 11 m clear, to 45 m, transom Z 26; town side: brick gatehouse 3 tiers, X -17..+17, Y 5..15, 40 m, round-arched windows, 2 arched strap doors + crest plaque; sandstone pilasters X ±17..±27 (6 m deep) |
| — | kick breach | **OWNER 16:51 10/26: ball-sized, 14-15 m wide x 15-16 m tall with a round/broken top so the 14 m ball fills it snugly** (was: X -7.5..+7.5, top Z 30-34) | broken beams, roots; glows orange before the seal |
| BALL | boulder rest | centre (0, 8, 7), r 7 | front flush with the gatehouse face; crushed-brick ring 1.5 m; Λ plug to Z 38 above it |
| Col | Colossal | feet Y -18..-28 on X 0 | chin Z 50-52, crown 60; right fist X +22..+30; left sweep X 0 → -35 |
| GS | gate square | semicircle r 70 on O (Y > 0) | turf #6f8a4c + worn earth; pale paved ring road r 70-78; town starts r ≈ 80 |
| P | ring pit | centre (0, 36) | C-trenches open toward O (gap ±45° about due south): outer trench r 17-24, 7 m deep, plank walls, 2 stepped 1.5 m setbacks; middle ring r 11-17 at grade with plank-deck edges; inner trench r 7-11, 4 m deep; central disc r 7; plank bridge 4 x 16 m at bearing ≈ 315° from P; mud floor, puddles; railing on the town-side step; plank boxes (4 x 4 x 2.5 m) at (-24, 40) and (22, 52) |
| SL | spiked slab barricades | 6 by the pit (arc) + 8 across the avenue mouth (Y ≈ 80) | 8 W x 12 H x 4 D m plank boxes, black spikes, small iron wheels; log-crib fences between |
| CRw / CRe | kick craters | W (-32, 20), E (34, 30) | r 4.5, 2 m deep, jagged splintered rims, 15-20 m steam wisps |
| H1-H3 | small holes | (-34, 32), (-30, 50), (38, 44) | r 1.5-2.5, 2-3 m deep |
| BO | bollards | Y 30 at X -30, -25, -15, -10, +10, +15, +25 | dark stone 1.5 m x 0.6 m; 20 m push gap X -10..+10 |
| TR | trees | spruces (-34, 10), (-40, 13); bushy tree (34, 10) | 8-12 m |
| LG | gate-side lift | (-62, 10) | moved from (-35, 6), clear of the spruces |
| AV | main avenue | (0, 78) → (-15, 300) → C (-60, 470) → (-140, 805) → enters E at its SW corner (-150, 800) | 14 m, pale cobbles #c8bb9c, kinks 6-8°, continuous terraces, ground-floor arcades |
| C | central plaza | (-60, 470), r 45 | pale paving, well (NO white monument disc); pyre site |
| rings | ring streets / radials | rings r 130, 240, 350 about C, 9 m; radials every 30-40°, 9 m; alleys 4-5 m | — |
| E | inner-gate forecourt | X -178..-102, Y 800..853 | dark setts #6f6c66; corner turret (-140, 790); pyramid-tower building (-95, 815) |
| EVS | Abnormal's street | (-102, 800) → (0, 690), 10 m | bearing ≈ 137° from E |
| I | inner gate bastion | X -153..-115, Y 853..865 (central block X -147..-133 to Y 851), 38 m tall | arch 5.0 x 6.5 m at X -140 (OPEN, dark 22 m tunnel); crest Z 20-23; west wing door 1.5 x 3.5 m; east-wing door 3.5 x 5.5 m centre X -124; pilasters X -163..-153 and -115..-105; grass slope X -105..-60, Y 840..865 + trees; terrace Y 820..840; ledge X -133..-105, Y 849..853; tree X ≈ -172 |
| CART | cart end state | load centre (-122, 842), yaw 320° | horses' heads ≈ (-127, 848); lane X -146..-134 stays clear |
| AB | Abnormal kill / corpse | kill (-85, 782); corpse (-96, 794), head NW | — |
| MA | Mikasa's alley | X -266.5..-257.5 (centre -262), Y 380..458 | mouth on ring r 240; steps Y 440-443; rubble heap Y 443-458 against a ≤ 10 m broken end wall; Mikasa lands (-262, 400) |
| SS | side street | Y 418..428 from X -257.5 to -150 | BT stands at (-205, 423) |
| Q2 | fight-2 square | X -252..-222, Y 490..520, floor Z +5 | tower **T (-218, 522)** 8 x 8 x 34 m; roof **R** ridge (-258, 505, 25) |
| HQ | supply HQ | keep (-250, 640); wing X -234..-136, Y 628..652; storeroom X -205..-169; lift (-187, 641) | terrace X -270..-230, Y 612..624; plaza apron X -275..-100, Y 570..624 + west strip X -300..-266, Y 570..660; GH (-200, 566); back range Y 676..700 (P2); AT approach (-222, 531) → (-230, 572) → leap (-240, 600); Eren's nape (-178, 619) |
| RC | 845 relief complex | centre (-268, 805), X -333..-203, Y 760..850 | its NE tower (≈ 40 m) + east hall replace church T4; in 850 it is just part of the town |
| D | decoy corner | NW pocket X -475..-360, Y 760..865 | ≈ 400 soldiers on the Rose and west wall tops (X -480..-300 / Y 700..870) |
| K | cannon basin (NORTH face of Rose, corrected 15:25 10/26) | floor X 340..385, Y 875..907, Z -3.6 | water/canal on the viewer's LEFT from the bank; T_K (322, 922); GB X 308..338, Y 875..891, Z 20; cannon (318, 883, 20); GH X 341..377, Y 928..948; L_K derrick (338, 872, 50) |
| CAN | canal (single) | centreline X 400, 26 m, from the Rose water gate (400, 870) to Y ≈ 330, bending SE to the east-wall exit (445, 300), then straight SE (≈ 135°) ≈ 400 m to join the world river | water Z -4.2 (inner run), green #6f9a7c; stepped stone banks, quays + bollards; pillar-portal bridges at Y ≈ 420, 560, 700, 820 (+2 outside); X 413..475 = quay road + 2-3 house rows to the wall |
| WG | water gates | Rose (393..411, 865..875) under the basin; east-wall exit (445, 300) | barred stone arches |
| B0 | Boulder Court | ball (290, 262, 7.4); court X 225..318, Y 236..292 | belfry (228, 290); lawn bed 30 m; second rock (308, 247); lane (232, 300) → (180, 360); exit (284, 236) |
| BR | carry route (438 m) | B0 (290, 262) → R1 (284, 232) → R2 (280, 160) (18 m radial) → R3 (274, 117) → arc r 455 about (0, 480): (228, 86), (185, 64), (141, 47), (95, 35) → R4 (63, 29) → R5 (36, 21) → R5b (18, 18.5) → R6 (4, 23) | cumulative 0/31/103/147/202/250/297/345/377/405/423/438; R5b keeps the ball 1.5 m off the east pilaster face (Y 11) and out of the outer trench; collision-check in the script |
| FL | flare points | GF (334, 136, 50) green; RF (306, 300, 19) red; YF (-24, 40, 2.5) yellow; PY (-20, 870, 50) relay | — |
| G8 misc | — | LV (-40, 2, 50) Levi entry; CT frames (-45, 45), (-55, 32); MI (-60..-75, 14..22); IA (-36, 56); crouching titan (44, 27) → falls to (52, 36) | — |
| PYR | pyres | C (-60, 470); GS ring road east (50, 55); AV (-12, 250); (150, 330) | — |
| A | Pyxis troop square (north of Rose) | centre (-20, 935), 90 x 60 m | paved forecourt, obelisk fountain (basin r 6, obelisk 10 m), no houses (E3) |
| S1 / S2 | Pyxis spots | S1 (-120, 866, 50); S2 (-20, 874, 50) | Pyxis post behind a timber railing at (-20, 866) |
| SH | 845 shelter camp | X -500..-100, Y 960..1130 | 6-8 barns + ≤ 120 drab tents |
| CL | 845-846 clearing | X -900..+100, Y 1170..1630 | — |
| CAMP | 104th camp | C (-1450, 1520) | quarry bowl, see g3 |
| L | wall lifts | (-380, 870), (-40, 870), (260, 870), L_K (338, 868), LG (-62, 10); Rose north-face hoists X -60, -20, +20 | timber truss + cage, red-roofed winch hut, counterweight derrick |
| T | bell towers (16-20) | T1 (-110, 470), T2 (-320, 300), T3 (180, 330), T5 (120, 620), T6 (-380, 520), T7 (-180, 235), T8 (300, 560), T_K (322, 818), court belfry (228, 290), tower T (-218, 522), RC NE tower (-213, 845), filler (-310, 560) + 6-8 fillers on a 150-180 m grid | 7-9 m square, 40-55 m, arched belfry stage; caps ≈ 60 % red/copper, 40 % slate; NO needle spires / white church; T4 removed |
| WT | wall-top dressing | bulge walls: brick pavers, track + turntables, cannons every ≈ 30 m; Rose: limestone, cannons every 60 m, **every 20 m on both edges at X 300..350 and X -160..+40** | crates, red-tile huts every ≈ 150 m, green flags, hoist cages |
| TW | titans at the Rose foot (g7/g8 time) | from D to X ≈ +100, densest X -170..-110 | none within 250 m of K |

**Contradictions resolved here.** HQ: g6 layout (keep west) over g4 (keep east). Inner bastion 38 m (g5) over 26 m; arch 5 x 6.5 m
over 6 x 8. Basin: Rose NORTH face at the canal (anime position, corrected 15:25 10/26). B0: g8 (290, 262) over g4
(-150, 230). East crater (34, 30) over (32, 20). Bollards Y 30 with a gap over Y 22 continuous. Ball rest (0, 8, 7) over (0, 4, 7).
Craters jagged (g5) not smooth. Canal water Z -4.2 over -3. Rain: optional P2, default off (g4 "no rain" vs g5 evidence). Relief
complex (-268, 805) over g3's (-420, -75 set). Sun at the basin 255° (g7) over "W/NW" (g4).

---------------------------------------------------------------------------------------------------------------------

## D. Implementation list for the laptop (P0 first; each item: segment · file / current render → change)

### P0 (wrong lore, owner-rule breach, or broken one take)
1. **ALL · master_timeline.py, render_fast._Channel.** SEAMS S0-S8 (S2 (180, 165, 215), S3 at 900 m, S5 detour, S7 (-3000,
   950+DY, 900), S8 (-1013, 322+DY, 300) pitch 70° at 196 m/s) → replace with the A2 seams and the B keys; add `v_in/v_out` to
   `_Channel` (or guide keys); build runs A1 / A2 / march846 / B (A3); re-time SEGMENTS to the A1 table (tight).
2. **g1 · render_fast.py, seq_colossal.py, flight.py.** Opening keys reach 28-72 m at ≈ 400 m/s and push 210 mm at 8.0 s → fallback
   K2-K12 (kick 11.0, ≤ 50 mm, ≥ 92 m, 129 m/s peak) + guide key 33.0.
3. **g1 · colossal / render_fast.HEAD.** opening_still_7.8s/11.7s: chest and shoulders above the wall, head 1.8x, crown 66 m → sink
   the root so the wall is at the collarbone, anatomical head (crown 60 m); left palm 4.5, right 6.0; kick at gate height with only
   the right leg; stand 12-15 then steam vanish 15-17.5 drifting west (today he fades 11.6-13.0).
4. **g1 · states845.OUTER_HOLE, fx845.** fall_still_5.0s: round green hole half-way up → ragged dark hole at ground, half-width 7.5,
   height 18-19; outer gatehouse = flat 16:58 version (no dome block); dust dome + 4-6 debris arcs; small smooth-flying stones;
   progressive roof collapse; remove the blood blob (fall_still_15.0s); golden S/SSW light (today dusk-blue); no mountains, sea
   horizon; bolt: one unbranched channel + brief darken + ≤ 0.3° shake.
5. **g1 · district.py / scene.py / seq_carla.py.** fall_still_13.3s/15.0s: lone cottage on a lawn → Yeager ruin on the rock terrace
   at the stair-lane head with the 9 m rock; Smiling Titan 13 m, alone; canal EAST everywhere (district.py has it west).
6. **g2 · render_fall2.py, walls.py.** fall3_still_armored: featureless grey recess, aftermath only → red-brick gatehouse both faces +
   crest leaf on chains; the run, guns, ricochets and impact on K1-K4 framed and locked on him; INNER_HOLE → narrow arch 12-14 x
   24-26 m with surviving wings; dust ball + south ring; 6 field guns + 6 wall-top guns + crews; Tripo Armored facing +y.
7. **g2 · render_fall2.py.** fall3_still_ferries/vow: 5 rafts in a line, blue ribbon canal, rainbow single file, vow hold → 4 ferries
   (34 x 10 m) in the stated states; 30 m sunken stone canal with quays, twin arches, 3-pylon bridge; 3-4k instanced refugees;
   remove the vow hold (K6-K9 aerial instead).
8. **g3 · render_interlude.py.** interlude_still_camps_smoke: 1.4 x 0.7 km white tent grid → relief complex at M (-268, 805) +
   small drab shelter camp; S3 900 m / 350 m/s map view → g3 flight keys at 240-380 m with the explicit speed profile.
9. **g3 · render_interlude.py (camp).** interlude_still_lookout/paddock: flat pine clearing, oval track, paddock, flag, green lawn →
   sunken quarry bowl at M (-1450, 1520), cracked pale floor #e2d8c2, watchtower, pole field, mess hall, huts, rigs; delete track,
   paddock, flag.
10. **g4/g5/g8 · trost.py (set).** trost_set_overview / p1 / p3: grey slab outer gate, gravel apron, detached cubes, grey inner gate with
    a green field through it, flat blue-grey walls → section C: brick gatehouse + pilasters; GS with ring pit P, 14 slabs, craters,
    holes, bollards, trees; continuous 3-5 storey terraces; 38 m bastion with an open 5 x 6.5 m dark arch; warm beige walls with
    damp bases, inner pilasters with caps, low plain outer parapet; wall-top rails, turntables, cannons, huts; 16-20 towers (remove
    the white needle church and the white plaza disc).
11. **g5 · render_trost_action.py, trost_action.py.** trost_part1_preview 20.0→21.5 s and 27→28 s whip transits (≈ 500 m/s) →
    C0-C10 with bridges C3b, C7b; breach + pour (35 titans by the front at Y 200-260); Colossal chin at the wall top, right-hand
    grip, westward sweep, steam explosion.
12. **g5 · trost_action.py (evac).** trost_p1_still_evacuation: white hooded wagon, ~500 rainbow figures in single file → sack flatbed
    wedged in the arch, backed out to (-122, 842, yaw 320°); ≈ 5,500 in a solid jam, palette per E2 (colourful, no pure primaries); Abnormal + Mikasa kill + corpse
    at the plaza mouth; crowd drains from the arch outward.
13. **g5 · trost_action.py (alley).** AT arrival in an open plaza by a fountain disc, house-sized AT → MA dead-end alley with steps and
    rubble, BT torn open in SS, 15 m AT, punch → roar → stomp; Armin/Connie to roof R; fight #2 in Q2 with tower T bursting.
14. **g6 · render_trost.py, trost.py (HQ).** trost_action_still_lift / trost_set_hq_cut: AT inside the storeroom, cutters on long ropes,
    white roofless box, whole wing opened, blob steam, flat platform lift, no ring/volley, houses packed to the HQ → AT outside;
    cutters on rafters (Sasha/Connie miss); 36 m bay dither cutaway with shadow proxy; brick vaults, torches, cylinders; chained cage
    + guide tower; 7-titan ring + 30-flash volley; ribbon steam; L plaza; keep moved to (-250, 640), wing east (today M (240, 490)).
15. **g7 · trost.py, render_trost_action.py (basin).** trost_p2 row 4: free-standing court 170 m south of the Wall at street level, capsule
    skeleton, puff steam, no cannon (white line from the north) → basin at the Wall foot (KF Z -3.6) with piers, water gate, bank,
    plinth, GB + cannon, T_K, GH; torso skeleton; massive steam; 48 Garrison + trio; Armin's salute hold; PACE timing (45 s).
16. **g8 · render_trost.py (carry), attack_titan.py.** trost_p3_still_carry: top-down 55-70°, ball hides the titan → C1-C3 side/three-
    quarter at 22-26° pitch, 170-230 m; ball radius 7.0 everywhere (boulder_anchor 6.0, boulder_r 6.5, SEAL_R 7.6, BOULDER_SIZE 15.2
    today); stone material (marbled, cracked, steaming) instead of blue-grey plastic.
17. **g8 · trost.py / render_trost.py (start, seal, flares, beats).** BOULDER (-68, 420) alone in gravel → Boulder Court at (290, 262)
    on its lawn bed; trost_p3_still_seal grey wall + small hole → gate-square set (C) + Λ plug + rubble + 5 titans; flares (red beams/
    boxes, red during the carry) → thin trails: green 3.0, red 8.0 (before the self-punch), yellow 53.0 (tight); add berserk, sitting
    collapse, stab, lift, roar, push, slump; light golden → sunset → dusk (today flat grey).
18. **ALL Trost · characters.** Remove every custom red-cape giant and the translucent red "flying blobs" over the HQ (trost_p2 rows
    1, 3); only downloaded asset humans at 1.65 m (09:37, 04:53).

### P1 (clearly visible quality / lore gaps)
19. g1 · scene.py: wall look (sandstone, 16 m pilaster stubs, string courses, no window-slot crenellations); town fabric (terraces,
    orange-reading roofs, mixed timber, crow-step gables, well squares); belfry (+25, -540) and onion church (+70, -560) replace the
    white plaza monument; mixed pour titans incl. the laughing one; smoke as 5-8 thin columns.
20. g1 · shot_opening.py: hamlet (≤ 10 farmhouses + windmills + cypress) between the tree hill and the inner wall (owner 17:45 ref);
    grass clumps, dirt road, scattered trees (15:07 #2).
21. g2 · avenue lined tight with 3-4 storey houses; debris fans north with 6-8 chunks reading above the wall; follower titans; Armored
    standing in the dust north of the wall (not frozen in the hole); stragglers freezing; golden-hour light → dusk; water strip + road
    bridge in the 10:25.1 frame.
22. g3 · flight: villages/farmsteads per E3, hedgerows, 2 girder bridges, river 90-110 m teal joining the canal at (445, 300), ferries
    continuing north, titans spreading north, dusk → night → morning time-lapse, Trost night lights.
23. g3 · clearing: snow, black conifers, terraces, 8-12 hoe lines; march: titans arrive from the horizon (not rows at t 0), varied
    meshes (no grey golems), no white chips, continuous 24-30 m column, gold sunset + ridge silhouettes at 15-18 s.
24. g3 · camp: 4 A-frame rigs with Eren upside down; HUD cadets ≈ 250 → 218; graduation night stair + braziers.
25. g4 · district U 960 x 870 (W 480, S 390, R 480) + world.py DISTRICT["rose"], lifts, labels; canal X 400 green with stepped banks,
    portal bridges, Rose water gate, exit (445, 300); pale cobbles, ring + radial streets, AV kinks; Survey Corps column + cadets +
    Eren's rail pose; late-morning light.
26. g5 · defence activity (roof squads, gas puffs, wall-top grapeshot); 10-15 smoke columns from t 14; light arc clear → overcast →
    sun shafts; corpse steam + shrink.
27. g6 · 3-tier keep (turrets, 7 arches, clock tower, terrace stair); wing with rusticated arcade, pilaster strips, dark slate roof,
    dormers, chimneys; exterior siege (Jean crash-in, punch-and-tackle, rampage, swarm, collapse); camera ≥ 80 m (no dive over the
    roof); cylinders (not blue chairs); torch light.
28. g7 · canal green, darker under the portcullis, 2 boats; T_K, GH clock gable, half-timbered range; floor pale/mossy halves; golden
    light 255°; Rose top dressing at S1/S2 (2 tracks, cannons every 20 m, crates, huts, banners); square A with obelisk + 2,000
    troops; L_K basket, walk west, deployment, leap.
29. g8 · route BR with the 38 m wall-foot strip; carry gait (bent knees, bob, sway, dust + cracks); 3 squads + trainees with kills;
    Mitabi/Ian grabs (tiny); titan into the trench; Levi; pyres with black columns and body rows; mop-up night pulses + captured
    titans; decoy mass at D.
30. ALL · flares and ODM: thin trails with bright heads; ODM wires as 0.12 m dark cylinders, white puffs.

### AUDIT CORRECTIONS (10/26, orientation audit vs the anime frames; these OVERRIDE the text above)
1. g1 spec note: ep02 05:25.5 is shot from NORTH of Wall Maria looking south (frame-left = EAST). The anime is consistent: canal EAST (x +228). Do not move it.
2. g2 smoke: the columns over Shiganshina bend WEST (-x) up high, not east (ep02 07:46.0: plumes rise from the wall top at frame lower-left and stream to frame-right = west when facing south). Use the same west wind as g1, ≈ (-1.5..-3, +0.3..0.6).
3. g2 hamlet: east-heavy, as in the 05:25 pan. Move the west-of-road cottages east of x 0, between the road (x > 15) and the quay apron (x < 145), y 30..200, e.g. (-60,40)->(40,45), (-45,115)->(35,110), (-115,70)->(85,95).
4. C row P: the ring-pit plank bridge is at bearing ≈ 25-30° (NNE) from P, not 315° (ep09 F09/000003609, ep04 20:30, F11/000014506).
5. g5 punch in MA/SS: the AT enters from the SS junction (punch key (-258.5, 420.5)) and the blow travels SOUTH and slightly west. CAP is hurled 15-18 m SSW into the WEST alley wall at Y ≈ 400-405 (chips and decal there).
6. C row L: add a fifth Rose lift, "RoseHQ" at (-195, 870) on the south face west of the inner bastion: two tall brown posts with a lintel and crossbar, near full wall height (behind the HQ in ep09 21:36.8).
7. C row FL: YF (Rico's yellow flare) = (22, 52, 2.5), on top of the EAST plank box. Rico stays east of the push gap (deck X +12..+20, Y 32-40) during the slump.
8. g8 sun: keep az 255° / el 12° at the g7→g8 hand-off and the green flare, then swing the azimuth smoothly to ≈ 200-205° during the carry (el 8° → 3°), so the low sun sits behind the gate, slightly east of it, by the seal and the yellow flare.

### P2 (polish)
31. g1: wall-top guns on round turntable pits; brick plinth details on the OG inside face; ≈ 50 people in the plaza looking up.
32. g2: ferry lanterns and roof discs; flung soldier; 2-pier truss bridge north; passage 5 x 7 m if GATE_W/H is cheap.
33. g3: ration carts, cooking smoke, 846 avenue gathering crowd; lake, wagon, sparring pairs; ≤ 150 carts; pikes on near LOD.
34. g4: conifers beside the outer gatehouse; HQ front stair; yard trees; wall-top birds.
35. g5: embers, optional rain (52-60, off by default), blood decals ≤ 3 m, X-stakes.
36. g6: keep crack, hall hole glints, back range + courtyard, smashed west-strip door.
37. g7: violet flowers in the ribs, cadet onlookers on GH, pigeons on the Rose crest, gun reload, pier-top signaller.
38. g8: dead titans shrink to 0.85; captured-titan frames detail; crane pylons at D.

---------------------------------------------------------------------------------------------------------------------

## E. Owner decisions still open (only real ones; defaults are already built into this bible)

1. **Length.** Tight cut = 7:02 from the opening to the end of Trost (Trost alone 4:40) vs the owner's own budget of ≈ 4:30 title→end
   of Trost (Trost ≈ 2:45) inside an 8-10 min EP1. **Default: the 7:02 tight cut** (every must-have kept). A further cut toward
   ≈ 5:15-5:30 is possible only by dropping events (e.g. g3 seasons/graduation to 8 s, g5 fight #2, g6 rampage to 1 kill, g8 mop-up +
   cleanup into 6 s); which ones is the owner's call.
2. **Crowd palette.** SUPERVISOR RULING: keep colourful (owner loved it), no pure primaries, everywhere incl. the Trost jam. The owner loved the colourful minimal plaza people (15:07) and the march (09:37), but the anime is muted (845
   refugees, 846 march, Trost evacuation; ep02 07:05.1, 19:54.9; ep06 05:49-06:08). **Default: keep colourful, but remove pure
   primaries** (no #ff0000 / #0000ff / #ffff00; dusty saturated tones); a fully muted look is the alternative.
3. **Buildings outside the two districts.** SUPERVISOR RULING (owner rule 09:37 stands: only Shiganshina and Trost have buildings):
   (a) Maria-plain farmsteads: NONE; (b) river-bridge town: NONE (the two girder bridges stay, they are not buildings);
   (c) Trost gate-foot hamlet: NONE; (d) Pyxis forecourt: YES (open paved square + obelisk fountain, no houses); the Shiganshina
   hamlet + windmill stay (owner's own opening ref); the 845 shelter camp north of Rose stays (barns/tents = the refugee-camp beat
   the owner asked to keep). Re-open only if the owner asks.

---------------------------------------------------------------------------------------------------------------------

## F. Key anime reference frames (40; copied into the repo as ref/anime/bible/epNN_<frame>.jpg)
Any other citation `epNN mm:ss.s`: grab it on the laptop from the S1 files with `ffmpeg -ss mm:ss.s -i "...NN [720p][AAC].mp4" -frames:v 1 out.jpg` (reference only, never in the video). The full per-group specs (more detail than this bible) are in design_specs/g1..g8_*.md.

| # | path | what to take from it |
|---|---|---|
| 1 | ep01/000026599.jpg | Colossal from inside: only the head above the wall, left hand over the town-side edge |
| 2 | ep01/000027530.jpg | breach from outside: arms spread, steam leaning west, ragged dark hole, titans walking in across grass |
| 3 | ep01/000027316.jpg | kick dust dome at parapet height with debris arcs fanning both ways |
| 4 | ep01/000025427.jpg | the single thick unbranched bolt behind the wall |
| 5 | ep01/000030626.jpg | Yeager ruin with the 9 m rough rock on it, Smiling Titan beyond |
| 6 | ep01/000032607.jpg | Smiling Titan bent 90° at the stair head, wall behind |
| 7 | ep02/000007498.jpg | Shiganshina wall face, pilasters, gate recess, houses packed to the wall foot |
| 8 | ep02/000003643.jpg | thin wavy smoke columns and the pale belfry |
| 9 | ep02/000004257.jpg | mixed titan column incl. the laughing titan, ground fires |
| 10 | ep02/000014428.jpg | avenue to the brick inner gatehouse with the field-gun line |
| 11 | ep02/000011688.jpg | crest leaf hanging over the pointed passage, brick wings |
| 12 | ep02/000014988.jpg | top-down ochre dust ball north of the gate, boulders, water strip |
| 13 | ep02/000014917.jpg | tall narrow arch breach, surviving wings |
| 14 | ep02/000008066.jpg | top-down ferries, quays, landings, lower berth |
| 15 | ep02/000013843.jpg | shell glancing off the Armored as a gold streak |
| 16 | ep02/000027814.jpg | relief cloister courtyard at the Rose foot, maroon roofs, towers |
| 17 | ep02/000027976.jpg | snowy clearing, terraces, hoe line, black conifers |
| 18 | ep02/000028650.jpg | march column out of the gate on a straight road |
| 19 | ep02/000028988.jpg | sunset ridge with titan silhouettes |
| 20 | ep02/000032057.jpg | 104th camp bowl: watchtower, pole field, mess hall, huts, palisade |
| 21 | ep04/000019148.jpg | graduation night: stone stair, braziers, ranks, top-10 row |
| 22 | ep04/000029323.jpg | pre-attack Trost from the outer wall: 16-20 bell towers, smoke-free |
| 23 | ep11/000010998.jpg | Trost layout aerial: U, avenue, rings, HQ, single east canal |
| 24 | ep09/000003609.jpg | outer gatehouse town face, ring pit, slab barricades |
| 25 | ep11/000014506.jpg | ring pit top-down: C-trenches, plank bridge, toppled slabs, X-stakes, titan lying in it |
| 26 | ep04/000034425.jpg | kick breach through the 3-tier gatehouse, rubble heap, 2 jagged steaming craters |
| 27 | ep06/000008308.jpg | inner-gate bastion, crest, east-wing door, pilasters both sides, jammed crowd, SE street |
| 28 | ep06/000008536.jpg | sack load wedged against both jambs, men pushing at the tailboard |
| 29 | ep06/000013040.jpg | cart end state east of the arch, horses facing the arch, crowd into the tunnel |
| 30 | ep07/000021613.jpg | Mikasa's dead-end alley: steps, boulder heap, broken wall |
| 31 | ep08/000014937.jpg | HQ aerial: keep, titans at the facades, pale plaza |
| 32 | ep08/000020462.jpg | lift cage on chains with lantern, ≈ 30 gunners, titans below |
| 33 | ep09/000028171.jpg | basin from above: piers, floor, Garrison L, boats, tower at the corner |
| 34 | ep13/000019194.jpg | sealed gate: Λ plug, ball at its base, 5 titans, spruces west, bushy tree east, holes |
| 35 | ep11/000026466.jpg | Boulder Court from above: terraces, belfry, second rock, leafy tree |
| 36 | ep13/000014432.jpg | carry pose: ball overhead, both arms up, stripped muscle, tower beside him |
| 37 | ep13/000017944.jpg | crouch-and-shove of the ball into the breach |
| 38 | ep12/000005181.jpg | decoy corner: titan mass with arms up, packed wall tops |
| 39 | ep13/000012552.jpg | stepped plank pit before the breach, titans at the lip, blood on the turf |
| 40 | ep12/000007811.jpg | titan sitting against the ball on its rock-ringed lawn bed |

Spares: ep09/000011497.jpg (outer gate from outside: iron frame, roots, titans entering), ep04/000030127.jpg (spiked slab on
wheels), ep01/000029118.jpg (stair-lane rising to the Yeager ruin).
