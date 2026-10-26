# g4_trost_geography: the Trost master map (850), plus the Trost establishing beat

Owner rules (BRIEF.md, HANDOFF 09:37 (10/25) and later) win over the anime. Tags: `[EV]` = seen in a frame I opened myself, `[LOG]` = taken from the Sonnet logs and not re-checked, `[INF]` = my inference.
Frame aliases: `F04` = /tmp/claude-0/aot/anime/frames/ep04/, and the same pattern for F06, F08, F09, F10, F11, F12 and F13. Frame time = frame number / 23.976.

**Coordinate frames used in this spec (all metres)**
- **MASTER frame M** (all coordinates below): the origin is the outer-gate centre on the wall centreline at ground level. +X is east, +Y is north into the city and +Z is up. Town ground is Z = 0.
- **trost.py set frame:** set = (X, Y - 870). Wall Rose runs along set y = 0 and the outer gate is at set (0, -870). Today's code uses this frame, and so does g3.
- **world.py frame:** world = (X, Y + 4130), because the Trost set origin sits at world (0, 5000).

**Scale note.** The district is built at true scale (1:1). It has to be, because humans are 1.65 m, titans are 3-15 m and the wall is 50 m. Only the distances between the rings are scaled. The owner's world map uses K = 0.05 (1/20): Rose radius 380 km becomes 19 km, and the 100 km Maria-Rose gap becomes 5 km. So Trost's outer gate is 4.13 km north of Shiganshina's inner gate on the laptop, against about 100 km in canon. Canon gives no figure for a district's size, only the wall radii and the 50 m height. The district size below is read from the anime aerials by counting buttress bays, house rows and the HQ size against the wall. Both my "canon-ish" metres and the laptop metres are therefore this 1:1 layout. The laptop's only scaling is the world-level offset.

---------------------------------------------------------------------------------------------------------------------

## 1. Lore summary of the beat(s), in order, with evidence

g4 owns the shared Trost MAP and the short ESTABLISHING beat (Trost, 850, the morning of the attack) up to the instant the Colossal appears. Later Trost beats are listed only for their map anchors (section 2f), because other groups own them.

1. **Graduation night to the next morning, Trost seen whole.** Trost is a walled U-shaped bulge on the south side of Wall Rose, packed with terracotta roofs. About 16-20 slender square bell towers stand evenly through it (F04/000029323), the supply HQ keep with its tall turret is in the inner (north) third, ONE green canal runs down the east side a block or two in from the east wall and leaves through the east wall, and fields and farm hamlets lie outside. `[EV]` layout from ep09 02:10.0 F09/000003117, ep11 07:38.7 F11/000010998, ep11 02:33.1 F11/000003670, ep13 15:11.6 F13/000021857. **Caution:** all four of these aerials are taken DURING or AFTER the battle (10-15 thin smoke columns rise across the district; F13/000021857 is dusk). Use them for layout only. The calm pre-attack look (clear sky, no smoke) is in ep04 20:23.0 F04/000029323 and 20:27.0 F04/000029419.
2. **The Survey Corps rides out.** A mounted column goes south down the main avenue toward the outer gate, with civilians lining the street. `[EV]` ep04 17:23.5 F04/000025018 (the avenue ends at the outer gate slot; an arc of about 10-12 slab barricades stands across the gate square) and ep04 17:27.5 F04/000025114 (the column on the avenue, caption "It's the main force of the Survey Corps!"). The Corps is absent during the battle. `[EV]` ep09 02:14.0 F09/000003213 (caption "The absence of the elite Survey Corps"). Same-morning timing is `[EV]`: ep09 02:26.5 (sheet_04), caption "Just earlier that morning, the Survey Corps had departed for an expedition beyond the walls". The scene before it, ep04 17:12.7, is at night (graduation night).
3. **Cadets on cannon duty on the outer wall top.** Eren's squad works on the rail-mounted cannons on the south wall top near the gate and looks north over the district. `[EV]` ep04 20:23.0 F04/000029323 and 20:27.0 F04/000029419. This is late morning, not dawn: ep04 20:17.5 (sheet_27) has the caption "We've still got a while until lunch". Sky: deep blue with many bright cumulus.
4. **The Colossal appears** behind the outer wall at the gate, its head above the wall top, beside a cannon, crates and a tiled wall-top house (a half-timbered upper storey on a stone base). A yellow lightning flash comes first. `[EV]` ep04 20:42.7-20:43.4 (sheet_28, the flash), ep04 20:44.8 F04/000029845. HANDOFF to the kick beat (another group).
5. Context for the other groups' map use only:
   - The gate is kicked. Anime order: Colossal head (20:44.8), then the kick hits the gatehouse base (20:55.6 F04/000030104 intact, 20:56.2 debris), the spiked slab barricades are blown back (20:56.5 F04/000030127), and debris flies over the gate square (20:57.9 F04/000030160) and over the wall top (21:01.1). The Colossal grips the wall top (21:27.2), and seen down the avenue the breach glows at the gate base while its head still shows over the wall (21:37.1 F04/000031099). Afterwards the gatehouse shows a tall smashed hole with rubble, and 2 large craters with rising steam lie in front of it (23:55.8 F04/000034425).
   - Evacuation jam at the inner gate `[EV]` ep06 05:46.5 F06/000008308.
   - HQ siege `[EV]` ep08 10:23.0 F08/000014937.
   - Cannon basin and half-shift; smoke rises from the town near the inner wall `[EV]` ep09 21:36.8 F09/000031091.
   - Pyxis above the obelisk square `[EV]` ep11 13:34.3 F11/000019523. **The square is NORTH of Wall Rose (Rose interior), not in Trost.** The soldiers have already been pulled out of Trost ("Isn't entering Trost District just suicide?" ep11 04:02.4; "I'm not going back there!" ep11 04:50.8). The same obelisk fountain appears in ep09 12:50.8 F09/000018481, captioned "Within Wall Rose", right after "So that's how we refilled our gas and got out of Trost District" (ep09 12:54.8). See the owner decision in section 9.
   - Titans lured into the wall corner `[EV]` ep12 03:36.1 F12/000005181 (caption "We somehow managed to lure the majority of the Titans to the corner of the town"), ep12 13:14.7 F12/000019053. Hundreds of soldiers pack the wall top above them `[EV]` ep11 18:31.9 F11/000026658.
   - The boulder in a courtyard `[EV]` ep11 18:23.9 F11/000026466. Its location in the district is uncertain; see 2d, B0.
   - The gate's ring pit `[EV]` ep11 10:05.0 F11/000014506, ep13 08:43.5 F13/000012552.
   - The push `[EV]` ep13 12:28.4 F13/000017944.
   - The seal `[EV]` ep13 13:16.5 F13/000019098, ep13 13:20.5 F13/000019194. A yellow flare confirms it ("Yellow signal confirmed", ep13 13:08.5; the thin flare trail rises from the gate end, ep13 13:04.5 F13/000018810).

## 2. Layout and geography (MASTER frame M; top-down)

### 2a. District outline and wall
- **Shape: a U (stadium end), not a flat D.** The aerials show long straight side walls running from Wall Rose and a roughly semicircular south end. Width is about the same as depth. `[EV]` F09/000003117, F11/000010998, F13/000021857.
- **Target outline:**
  - Wall Rose is straight along Y = 870 from X = -480 to +480.
  - The side walls run along X = ±480 from Y = 870 to Y = 480.
  - The south end is a half circle of R = 480 centred on (0, 480).
  - The tip is the outer gate O = (0, 0).
  - Overall size is **960 m wide x 870 m deep** (about 0.74 km² inside).
  - From the anime: about 17-18 inner buttress bays along Wall Rose at about 30-35 m each, about 50 rows of houses across, and the HQ keep at about 1/30 of the width, which gives about 0.6-1.0 km `[INF]`.
  - In trost.py terms: **W = 480, S = 390, R = 480**. Today it is W 620 / S 250 / R 620 (1240 x 870, a flat D). This change is P1 (see section 8). If it is not done, every coordinate below still holds except the east-side canal (section 2c, variant).
- **Wall:** 50 m tall and 10 m thick (WALL_T); the wall-top walk is 10 m wide.
  - **Inner face:** projecting stone pilasters 7 m wide and 3 m deep, at about **28 m** centres. Each pilaster ends in a block cap that rises about 3 m above the parapet, so the wall top steps up and down. `[EV]` F09/000003609 and F13/000012552 (huge pilasters), ep11 21:02.5 F11/000030270 (stepped wall-top blocks), F12/000005181.
  - **Outer face:** flat with recessed dark counterfort grooves 3 m wide at about **20 m** centres (measured against the 50 m wall height in F09/000011497). Dead, leafless root or vine tendrils hang down from the coping along the whole wall top, not only over the gate. `[EV]` ep09 07:59.5 F09/000011497.
  - **Wall-top silhouette:** the bulge wall top carries square block merlons or caps at every pilaster, which read as a toothed rim in the aerials `[EV]` F11/000003670, F09/000003117.
- **Junction corners:**
  - NW corner (-480, 870) and NE corner (480, 870), where the side walls meet Wall Rose at 90°.
  - The anime shows the titan decoy mass packed into such a corner `[EV]` F12/000005181, F12/000019053.
  - **Decoy corner D = the NW pocket, X -475..-360, Y 760..865** `[INF]`. No frame tells NW from NE: the light in F12/000019053, where the right-hand wall face is lit, would fit either. NW is kept because it is away from the canal and the HQ-to-gate traffic.

### 2b. Gates
- **Outer gate O (0, 0).**
  - **From outside:** a tall rust-red riveted iron gate frame set in the flat wall, about 20 m wide overall (clear opening about 11 m), rising to about 45 m, with a cross-transom at about 26 m. After the kick the door below the transom is a dark ragged hole, and titans walk in from the fields. `[EV]` F09/000011497 (post-kick; measured against the 50 m wall).
  - **Town side:** a **brick gatehouse tower** 34 m wide (X -17..+17) that projects 10 m north (Y 5..15) and rises 40 m in **3 tiers**. Each tier has a pale stone cornice and a row of small round-arched windows. It is flanked by two giant sandstone pilasters, each 10 m wide (X ±17..±27, 6 m deep), which curve out at the foot. At the base are 2 arched wooden doors with iron straps (a small one and a large one) and a crest plaque (shield with the wall goddess's head) between them. `[EV]` F09/000003609, ep13 13:16.5 F13/000019098, ep13 13:20.5 F13/000019194, ep04 20:55.6 F04/000030104.
  - **After the kick:** a tall ragged breach about 15 m wide at ground (X -7.5..+7.5). Its sides are roughly straight and it has a broken, rounded top above the second cornice, at about Z 30-34 (F04/000034425). Torn brick, broken floor beams inside and radiating cracks. A rubble heap of red brick and grey stone spills 15-20 m north. `[EV]` F04/000034425. Seen down the avenue on kick day, only a small glowing hole shows at the base (F04/000031099). This is an anime inconsistency; build the big breach.
  - **After the seal:** a dark plug of steaming titan remains, with root-like tendrils spreading over the brick, fills the hole. It reads as a **tapering spire (Λ)**: widest at the base, narrowing to a point near the top cornice, about Z 38. The round boulder sits wedged at the base. `[EV]` F13/000019098, F13/000019194, ep13 12:42.6 F13/000018285.
- **Inner gate I (-140, 870)**, at the current X.
  - **Gatehouse:** a stepped brick bastion 26 m wide, projecting 12 m south (Y 853..865 off the 865 inner face; Wall Rose is centred on Y 870 and 10 m thick) and 38 m tall. Grey stone quoins, narrow slit windows and a **shield crest** above the opening. `[EV]` F06/000008308 (Trost/south face). ep09 12:50.8 F09/000018481 shows the same kind of bastion from the NORTH (Rose) side, captioned "Within Wall Rose". It is valid only as a style match, not for Trost-side surroundings.
  - **Passage:** an open round arch (owner: OPEN, no door) 6 m wide x 8 m tall at the base.
  - A grassy slope with shrubs and trees runs along the wall foot east of the gatehouse `[EV]` F06/000008308 (the right side of the frame; dark shrubs also show at the left edge).
  - It sits roughly on the line of the avenue's north end: from the south it appears just right of the HQ keep `[EV]` F09/000031091.
- **Water gates** (barred, stone-arched portals): one where the canal enters through Wall Rose at about (400, 870) `[INF]`, since the canal starts at Wall Rose in F11/000010998. A second where it leaves through the east wall at about (445, 300) `[EV]`: the canal visibly passes through the east wall in F11/000003670 and F09/000003117. The barred arch in F09/000018481 is on the north face of Wall Rose; do not use it as Trost evidence.

### 2c. Canals (the river N-S through all walls)
- **Evidence (corrected: there is ONE canal, not two):**
  - A single stone-lined canal with green water runs down the EAST part of the district, parallel to the east wall. It leaves through the east wall a little past where the straight side wall starts to curve. `[EV]` F11/000010998, F09/000003117, F11/000003670 (zoomed: one water channel, crossed at intervals by bridge portals made of paired tall pale stone pillars).
  - It does NOT run at the wall foot. A strip of houses 2-3 rows deep (about 50-60 m) plus a quay road lies between the canal and the east wall. `[EV]` ep11 21:02.5 F11/000030270 and ep13 13:04.5 F13/000018810. In both, the camera looks south along the east wall toward the outer-gate end: outside fields and hamlets are on the left (east) and the evening sun is ahead-right (SW-W).
  - Width is about 2-3 house widths, roughly 25-30 m, with paved quays and rows of posts or bollards along the edges `[EV]` F11/000030270.
  - Outside the wall the canal carries straight on to the SE across the fields, with more pillar-portal bridges and small red-roofed hamlets beside it `[EV]` F11/000003670, F09/000003117.
- **The canal:** 26 m wide, centreline **X = +400**, running straight N-S from the Wall Rose water gate (400, 870) down to Y ≈ 330. It then bends gently SE to the east-wall water gate at about **(445, 300)**. The strip from X 413 to X 475 holds a 10 m quay road on the canal side plus 2-3 rows of terraces against the wall (the wall-foot road stays at the wall).
- **Construction:** water surface at Z -3; banks are stone, stepped 2 x 1.5 m, with a quay rail or bollard row at the top.
- **Bridges:** 4 bridge portals across the inner run at Y ≈ 420, 560, 700 and 820. Each is a flat stone deck 8-10 m wide with a pair of tall pale stone pillars (about 8-10 m) at each bank, joined overhead by a beam, as in the aerials `[EV]` F11/000010998, F11/000003670. The arched bridges in ep10 21:49.6 F10/000031399 are on the north (Rose-interior) side; do not use them.
- **Outside:** from the exit gate the canal runs straight SE (bearing about 135°) for about 400 m with 2 more pillar portals, then joins the world river heading south (tell g3/G: today their river meets Trost at set (556, -524) = M (556, 346), so move that join to the new exit at (445, 300)).
- **Variant if W stays 620:** put the canal about 80 m in from the east wall (X ≈ +540). Bend it SE where it meets the curved wall, and exit about 180 m south of the point where the side wall starts to curve. Keep the single canal and the house strip next to the wall.

### 2d. Streets, squares and landmarks
| id | what | position (M) | size / notes | evidence |
|---|---|---|---|---|
| O | outer gate (breach) | (0, 0) | see 2b | F09/000011497 |
| GS | **outer-gate square** | semicircle r 70 on O, Y > 0 | grass with a worn-earth path; pale paved **ring road** 8 m wide at r 70-78; the town starts at r ≈ 80 | F04/000030160, F09/000003609 |
| P | **ring pit ("sunken ground")** | centre (0, 36), on the gate axis | see 2e | F11/000014506, F13/000012552, F09/000003609 |
| AV | **main avenue** | (0, 78) → (-15, 300) → C (-60, 470) → (-140, 805) | 14 m wide, pale cobbles; straight in segments with gentle kinks of about 6-8°; terraces line it continuously; ground-floor arcades | F04/000025018, F09/000003620, F04/000025114 |
| C | **central (market) plaza** | (-60, 470) | r 45, pale paving, well; tower T1 on its west side | F11/000010998 (concentric rings) `[INF]` |
| H | **supply HQ** | keep centre (-165, 640); warehouse centre (-215, 640), long axis E-W | keep 30 x 30 x 24 m (turret top 49 m) on the **avenue (east) side**; warehouse wing 70 x 30 m, 5 storeys, at its west end. Forecourt "HQ plaza" X -150..-108, Y 600..690 (pale beige paving). The anime is inconsistent: F11/000010998 puts a long low wing WEST of the keep, F09/000031091 puts a slate-roofed wing EAST of it. The owner refs decide | F08/000014937, F08/000009331, F09/000031091, F11/000010998 |
| E | **inner-gate forecourt (evacuation jam)** | X -178..-102, Y 800..853 | paved; the crowd blob is about 30 x 40 m in front of the arch; a street leaves east | F06/000008308 |
| A | **assembly square (Pyxis)**. **OWNER DECISION, section 9** | anime: NORTH of Wall Rose, in the Rose-interior town behind the inner gate. Default until the owner decides: Pyxis on the wall top at (-20, 870, 50); the troops (about 2,000) stand on an open paved forecourt just NORTH of the wall, centre (-20, 935), 90 x 60 m, around a free-standing **obelisk fountain** (round basin r 6, obelisk 10 m). This needs no houses. | earthen or pale paved square, obelisk fountain, troops packed shoulder to shoulder; a tower with a pyramid roof stands at one corner (F11/000019523) | F11/000006876, F11/000019523, ep09 12:50.8 F09/000018481 ("Within Wall Rose": the same obelisk), ep11 03:58.4 / 04:02.4 (troops at the wall foot facing the inner gate's north face) |
| K | **cannon basin** | suggested centre (345, 810), floor X 320..370, Y 785..835, opening on its east side onto the single canal's west quay (X ≈ 387). This replaces (280, 810), which hung off the deleted Canal B | sunken stone dock with stepped banks running down to water; the barred water gate is at its NE rear. Owned by the basin group | ep09 18:05.8 (sheet_22, stepped stone banks down to water), ep09 18:15.1 (grassy sunken floor below a wall); F09/000031091 (steam column right of the inner gate seen from the south) |
| B0 | **boulder start** | (-150, 230) in "Boulder Court" r 25 `[INF]`. **Location contested (section 9):** ep11 21:02.5 F11/000030270 shows a pale round mass with a thin steam wisp one or two blocks WEST of the east canal at about mid-depth, roughly M (330, 420), at the moment the operation's green flare goes up. That is very likely the boulder. | a cobbled courtyard ringed by 4-storey terraces with dormers and a stepped-gable house, a square belfry at one corner, a second smaller rock beside the boulder | F11/000026466, F11/000030270, ep13 00:26.4 F13/000000632 `[LOG]` |
| BR | **boulder route** | B0 → east along the cross street Y 230 → AV at (-8, 230) → south on AV → ring road (0, 78) → across GS around the pit's east flank (passing between the pit and the east crater at (32, 20)) → the at-grade strip between the pit's C-opening and the gatehouse → breach O | about 330 m. The C's closed back faces the town, so the titan must go round it, not over the trenches | F13/000017944 |
| D | decoy corner | NW pocket X -475..-360, Y 760..865 | the titan mass presses here; hundreds of soldiers pack both wall tops above, shoulder to shoulder | F12/000005181, F11/000026658 |
| T1-T8 (+ about 10 more) | bell towers | anchors: T1 (-110, 470), T2 (-320, 300), T3 (180, 330), T4 (-300, 800, church), T5 (120, 620), T6 (-380, 520), T7 (-180, 235), T8 (300, 560). **Add about 8-12 more** on a loose 150-180 m grid so the total is **16-20** | see section 3 | F04/000029323 and F04/000029419 (16-20 slender towers visible across the district from the outer wall top) |
| L | wall lifts (timber-cage hoists) | (-380, 870), (-40, 870), (260, 870) (today's), plus one at O, west of the gatehouse at (-35, 6) | timber truss and cage up the wall face; red-roofed winch hut on top; crane derrick with a counterweight beside it | F10/000028037, ep11 18:31.9 F11/000026658 |

- **Street pattern:** **concentric rings plus radials** around C, as in the aerial `[EV]` F11/000010998.
  - Ring streets at r ≈ 130, 240 and 350 m around C, each 9 m wide.
  - Radials every about 30-40°, 9 m wide.
  - Alleys 4-5 m wide inside blocks `[EV]` F07 15:01 `[LOG]`.
  - Secondary streets 8-10 m wide `[LOG]` ep06 06:48.9, ep11 19:06.9.
- **Wall-foot strip:** a 6 m wall road along the inner wall faces. Grass verges with trees only in places: east of the inner gate (F06/000008308), and 2-4 dark conifers flanking the outer gatehouse (F13/000019194). Elsewhere terraces come right up to the wall road (F11/000030270, F12/000019053, F13/000018810).

### 2e. The outer-gate square in detail (the owner's "sunken ground")
- **Before the kick** `[EV]` F09/000003609 (02:30.5) and F04/000025018:
  - A grass clearing with a round **sunken ring pit** in front of the gatehouse, on the gate axis. F09/000003609 looks SOUTH, so the pit reading slightly LEFT of the gatehouse there means slightly EAST, not west. F13/000012552 shows it right of the breach from an oblique viewpoint. Both offsets are perspective, so centre it on the axis.
  - In front of the pit stand **4 huge trapezoidal timber barricade slabs** in an arc, with 2 more on a timber scaffold heap to the EAST (on the left in the south-looking F09/000003609).
  - Log-crib lattice fences (crossed logs about 3 m tall) run between the slabs.
  - F04/000025018 (looking south down the avenue) shows one long arc of about 10-12 slabs across the square between the avenue mouth and the gate. Build one arc of 8 slabs across the avenue mouth plus the 6 by the pit, 14 in all.
  - **The slabs ARE the "spiked barricades".** Each is a tall trapezoid plank box: pale tan planks in dark timber frames, a row of black iron spikes on the lower front, small iron wheels at the base. Height is about 2-3 house storeys (10-13 m). `[EV]` ep04 20:56.5 F04/000030127.
  - A straight pale paved path runs from the ring road to the pit's plank bridge `[EV]` F04/000030160 (top-down).
- **Ring pit P, centre (0, 36)**, like a small arena of concentric C-trenches. Both C openings face the gate (the gap sector is about 90°, centred on the bearing from P to O). `[EV]` F11/000014506 (top-down), F13/000012552 (stepped, plank-topped), F04/000030160.
  - **Outer trench:** annulus r 17-24 m, 7 m deep. Dark vertical plank retaining walls (posts every 2 m), plus 2 plank-capped setback steps of 1.5 m on the outer wall (ep13 reads as stepped).
  - **Middle ring:** r 11-17 at grade, with plank decking at the edges.
  - **Inner trench:** r 7-11, 4 m deep.
  - **Central disc:** r 7 at grade.
  - **Plank bridge:** 4 m wide x 16 m long, from the town side over the outer trench onto the middle ring (bearing about 315° from P `[INF]`; the frames do not fix the compass side).
  - **Floor:** dark mud with puddles.
  - A low wooden railing runs along the top step on the town side.
  - Titans fall into it. One titan lies sprawled on the middle ring at the mouth of the inner trench, and another stands between the pit and the gate `[EV]` F11/000014506. Later 5 titans mill at the pit's town-side lip `[EV]` F13/000012552, and 5 stand on the grass in front of the sealed gate `[EV]` F13/000019098.
- **After the kick** `[EV]` F04/000034425, F11/000014506, F04/000030160:
  - **Impact craters:** 2 large bowl craters, about 6-10 m across and 2 m deep with ragged turf lips, in the grass in front of the gatehouse, one on each side, at X ≈ ±32, Y ≈ 20 (just outside the pit's flanks and clear of the pilaster feet), each with a thin twisting steam or smoke wisp `[EV]` F04/000034425. Optionally 2-3 smaller ones (3-5 m) further out `[INF]`. The top-down F11/000014506 shows NO craters east of the pit, so the earlier "3 to the east of P" claim is removed.
  - **Barricades:** toppled and collapsed slabs, splintered log-crib fences, broken crates and planks, scattered round lids or wheels and small crossed-timber X stakes (about 2 m) strewn over the square `[EV]` F11/000014506.
  - **Rubble fan:** red brick and grey stone blocks in a fan in front of the breach; grey stone chunks also fall on the grass and ring road at kick time (F04/000030160).
  - **Avenue mouth:** 2 slab barricades lean, wrecked, at the avenue mouth either side of the street, and stone chunks litter the avenue `[EV]` F04/000031099.
  - Blood stains on the turf near the pit `[EV]` F13/000012552. Keep them small and dark, per the owner's "tasteful".
- **Boulder end state:**
  - The boulder (owner: a round ball, 13-15 m) sits in the breach base, centre (0, 4, 7).
  - The Attack Titan pushes it in from the pit-gap side `[EV]` F13/000017944, and afterwards slumps steaming against it `[EV]` F13/000018285.
  - **Bollards:** short round dark-grey stone posts, about 1.5 m tall, in a row across the gatehouse front at Y ≈ 22, spaced about 4-6 m; a plank deck edge lies in front of them `[EV]` ep13 12:42.6 F13/000018285.
- **Gate-foot hamlet outside (P2):** 4-6 farmhouses with red-tile roofs at the foot of the wall outside, at X ±40..90, Y -20..-50, plus a few more along the outside canal `[EV]` F09/000011497 (post-kick), F11/000003670. This needs an owner check against the "only districts have buildings" rule (g3 raised the same question).

### 2f. Map anchors for the other Trost beats (shared; the owning groups decide the details)
| beat | anchor in M |
|---|---|
| Colossal | stands outside at (0, -25), facing north; hands on the wall top at X ±25 |
| titan pour | from O north along AV, then fanning into the ring streets; the first 300 m fills in about 60 s of story time (sped up) |
| evacuation | crowd flows north on AV/C toward E; cart jammed in the inner-gate arch (-140, 860) |
| Mikasa falls / Attack Titan arrives | the west half between C and H, around (-260, 430) `[INF]` (the narrow alley ends in rubble at a wall section `[LOG]` ep07 15:01) |
| HQ lift op | H and its plaza |
| Eren emerges | HQ plaza (-130, 640) `[INF]` |
| cannon + half-shift | K (345, 810); steam column rises there (seen from the south as right of the inner gate `[EV]` F09/000031091) |
| Pyxis | wall top (-20, 870, 50), facing NORTH over A (default; see section 9) |
| boulder | B0 → BR → O (B0 contested; see 2d and section 9) |
| flares | green flare starts the boulder operation (ep11 21:02.5 F11/000030270, a tall green smoke column rising from the far, southern part of town in that south-looking shot); red flare = failure, fired in golden afternoon light (ep12 05:03.3, sheet_09); yellow flare = success (ep13 13:04.5 F13/000018810 and 13:08.5) |
| decoy | D |
| Levi mop-up / pyres | the south half and GS; pyres in C and GS `[INF]` |

### 2g. ASCII top-down (1 char = 20 m E-W, 1 row = 40 m N-S; north up)
```
  870   #################I##########################w####   Wall Rose (I inner gate, w canal water gate)
  830   #..D.............E..........................~...#   D decoy corner, E evac forecourt (Pyxis square A lies NORTH of the wall)
  790   #........T.......|.......................K..~...#   K cannon basin (opens onto the canal), T bell towers (+8-12 more)
  750   #.................|.........................~...#   | main avenue, ~ the single canal (X 400)
  710   #.................|.........................~...#
  670   #..................|........................~...#
  630   #...........HHHHH..|..........T.............~...#   H supply HQ (keep at its east end, plaza east of it)
  590   #...................|.......................~...#
  550   #...................|..................T....~...#
  510   #....T...............|......................~...#
  470   #.................T..C......................~...#   C central plaza
  430   ##....................|.....................~..##
  390   ##....................|.....................~..##
  350   ##.....................|.........T..........~..##
  310    ##.....T..............|.....................~##   canal leaves the east wall at (445, 300), runs on SE outside
  270     ##...................|.....................##
  230      ##..........TB......|....................##   B boulder start (contested, see 2d)
  190       ###.................|.................###
  150         ###...............|...............###
  110          ####.............|.............####
   70             ####........ooooo........####   o ring road around the gate square
   30                #######.o..P..o.#######   P ring pit (sunken, centre 0, 36)
    0                        ###O###   O outer gate (gatehouse projects north 10 m)
```

## 3. Set dressing and materials
- **Town fabric.** Continuous **terraces** that follow the street lines, not detached cubes. `[EV]` F04/000029323 (Trost), F11/000006876 (north of Wall Rose; same style), ep12 05:09 F12/000008120 `[LOG]`.
  - Height mix: 4 storeys 60% (eaves 13 m, ridge 19 m); 3 storeys 25% (10 / 15 m); 5 storeys 15% (16 / 22 m). Bell towers rise to about 2x the houses.
  - Roofs: steep (50-55°) with 2-4 dormers per face, chimneys, some stepped gables `[EV]` F11/000026466 (F09/000018481 shows the same style, but north of Wall Rose), and some hipped corners.
  - Facades: cream plaster #d8cbb0, sandstone #c9b48e and grey stone #9b9486 with corner quoins. Upper storeys are half-timbered (dark beams #4a3427) on about 40% of houses, more in the south half `[EV]` F04/000025114.
  - Ground floors: arcades of round arches along AV and C `[LOG]` ep07 01:35, ep12 05:09.
  - Roof colours: terracotta #b4532f, #a2472a, #c46a3c and #8e4a30, with about 5% darker brown #6e3b28 patches. Big civic buildings get slate blue-grey #4f5a66 (about 6%).
  - Small trees in yards (about 3% of the cover) `[EV]` F09/000003620.
- **Streets.** Pale beige cobbles #b9ab8f, with the avenue lighter at #c8bb9c and large two-tone setts in squares `[LOG]` ep12 18:07. Plazas are pale sandy paving #cdbf9f `[EV]` F08/000014937.
- **Bell towers (16-20 in all: T1-T8 plus about 8-12 fillers).** Slender and square, 7-9 m on a side, mostly cream sandstone #d6c7a2 (about 70%) with some brown brick #8a5a40. Count `[EV]` F04/000029323, F04/000029419.
  - Heights: shaft 30-42 m; a belfry stage with 1-3 round-arched openings per side and a cornice; then a **pyramid or hipped cap**, slate blue-grey #56606c or copper-brown. Total 40-55 m.
  - One (T4, the church by the inner gate) has a stepped-gable nave.
  - No needle spires, no white Lutheran church. `[EV]` F04/000029323, ep04 13:10.6 F04/000018956 `[LOG]`, F06/000031870 `[LOG]`. F10/000031399 looks NORTH over the Rose interior (no smoke, open hills, no outer wall), so it is a style reference only.
- **Supply HQ.** Owner refs (trost_hq_*_ref.png) plus `[EV]` F08/000014937 and F09/000018289.
  - The keep is warm sandstone #cdb48a with block texture, a crenellated parapet, a row of 7 arched windows, and square corner turrets with slate-blue pyramid roofs #5a6b7e. It has a taller central block and a bell/clock turret with a small cupola (top 49 m).
  - The warehouse wing is 5 storeys of sandstone with a steep DARK slate gable roof #3d434b, a rusticated arched plinth and rows of small windows.
  - The anime also shows mansard slate wings and a front terrace with a stair onto the plaza (F08/000014937). Add a front stair terrace (P2).
- **Wall.**
  - Pale warm grey-beige stone #bdb5a3 with faint 1.2 m block courses and horizontal panel seams.
  - Lower 6 m: damp darker #8f887a with moss streaks #5f6b45 and rust-brown run-off stains under the wall-top rails `[LOG]` ep10 18:35.
  - Pilasters slightly lighter #c9c1ae.
- **Wall top** `[EV]` F04/000029845, F10/000028037, F09/000018289, F11/000019523, F04/000029323.
  - Paving, **bulge (outer) walls**: red-brown brick pavers #8e5a48 laid in a running/basket pattern over the whole wall top, as where the cadets stand and the Colossal appears `[EV]` F04/000029323, F04/000029845, ep04 20:13.5 and 20:59.8 (sheet_27/28).
  - Paving, **Wall Rose**: pale limestone slabs #cfc4a8 with ochre stains `[EV]` F10/000028037, F11/000019523, F09/000018289.
  - Track: a **narrow-gauge iron track** (1.5 m gauge, dark timber sleepers) along the inner side, with curved spurs every about 30 m to **cannon turntables**. Each turntable is a 3.5 m disc with ribbed timber and striped cream-brown boards.
  - **Cannons:** black iron barrels on timber bogie carriages, every about 30 m on the bulge walls and every about 60 m on Wall Rose.
  - Plain light-wood crate stacks; green Garrison flags on poles every about 60 m along the speech stretch.
  - **Wall-top houses/huts** every about 150 m: 4-6 m square, 1-2 storeys, brick or a half-timbered upper storey on a stone base, red tile roof `[EV]` F04/000029845, F10/000028037.
  - Crane derricks with counterweights at the lifts; an outer parapet with merlons about 1.5 m tall.
- **Gate square props.**
  - **Spiked slab barricades (one prop type, 14 in all: 6 by the pit, 8 across the avenue mouth):** trapezoid plank boxes, 8 W x 12 H x 4 D m at the base, with braced frames at the back. Mid-tan planks #9a7a55 (pale tan #b89a6a in sun) in dark frames #4a3427, rows of black iron spikes on the lower front, small iron wheels `[EV]` F04/000030127, F09/000003609. There is NO separate small barricade type.
  - Log-crib fences.
  - The pit's plank walls #3b2f25.
  - Turf #6f8a4c with worn earth #8a7a5c.
  - Bollards in dark grey stone, about 1.5 m tall (F13/000018285).
  - 2-4 dark conifers (spruce, 8-12 m) at the wall foot either side of the gatehouse (F13/000019194).
- **Canal (one).** Green water #6f9a7c (darker #4e6e62 in shade), cream-grey stone banks #a9a291, paved quays with post or bollard rows, pale stone pillar-portal bridges. 1-2 moored boats `[INF]`.
- **Outside the wall.** A green patchwork of fields with hedgerows and straight field roads. Small farm hamlets of red-roofed houses lie on the east, along the straight outside canal heading SE (`[EV]` F09/000003117, F11/000003670), and at the gate foot (F09/000011497). No mountains behind (owner); low hills only.

## 4. Characters and titans

### 4a. In the establishing beat (pre-attack)
- **Survey Corps column.**
  - About 120 riders with green cloaks, 2 abreast, 5 m spacing, so the column is about 300 m long. 2-3 supply wagons with pale canvas hoods follow at the rear `[LOG]` ep07 01:35.
  - It moves south on AV at a 4 m/s trot and passes out through O, which is open for this moment.
  - It is gone over the fields before the Colossal appears `[INF]`.
- **Civilians.** About 600 line both sides of AV between Y 100 and 450 (1-2 deep). There is sparse traffic elsewhere (about 1 person per 300 m²) and market stalls in C.
- **Garrison.** Pairs at the cannon posts along the wall tops (every about 60 m) and guards at both gates.
- **Cadets.** 7 cadets (Eren, Sasha, Connie, Thomas, Mina, Samuel, Mylius `[INF]` from canon) at the cannons on the outer wall top, X -60..+60 near O.
- **Scale and style.** All humans are faceless at true 1.65 m and use downloaded asset models only. Use LOD/instanced crowds for the civilians.

### 4b. Titans (shared reference for all Trost beats)
- **None inside before the kick.** The **Colossal** (60 m) rises outside at (0, -25). Its skull shows above the wall top (Z 50-62), with steam.
- **After the pour** `[EV]` F12/000005181, F12/000019053, ep09 02:17.5 F09/000003297 `[LOG]`, ep13 09:06 `[LOG]`:
  - Size mix: 3-4 m 25%, 5-7 m 45%, 8-10 m 20%, 12-15 m 10%.
  - Mostly slow walkers; a few run as abnormals; some sit, kneel or crawl.
  - At the decoy corner D: a mass of 60-100+ titans packed shoulder to shoulder along both walls of the corner, arms raised to the wall top `[EV]` F12/000005181, F12/000019053. Hundreds of soldiers line the wall tops above.
  - At the gate pit: 3-5 titans stand at the lip, 1 lies sprawled on the middle ring, and 1 stands between the pit and the gate `[EV]` F11/000014506, F13/000012552.
  - Coming in from outside, titans (5-10 m) walk across the fields to the smashed gate and through it `[EV]` F09/000011497.

## 5. FX, lighting and time of day
- **Time-of-day arc for all of Trost** `[EV]` F04/000029323, F04/000029845, ep06 notes `[LOG]`, F13/000018810, F11/000030270:
  - **Survey Corps departure:** early morning, crisp pale-blue light `[EV]` F04/000025018.
  - **Cadets / Colossal:** clear LATE morning ("We've still got a while until lunch", ep04 20:17.5), sun from the SE at about 45-50° elevation, deep blue sky with many bright cumulus `[EV]` ep04 sheet_27, F04/000029845.
  - **Evacuation through HQ:** overcast grey.
  - **Pyxis through the boulder:** golden late afternoon, sun low in the W/NW, warm haze.
  - **Pyres:** dusk.
  - No rain in our take (the anime's rain belongs to a flashback).
- **Establishing FX** (cheap cards):
  - Thin chimney smoke wisps from about 40 houses, pale grey, drifting.
  - Birds near the wall top (optional).
  - Low morning haze over the fields (Eevee volumetric off; use mist pass/fog colour #c9d4dd).
  - Steam at the Colossal's head appears only at the handoff.
- **Later beats (summary only):**
  - Smoke columns: 10-15 thin, tall, near-vertical columns spread across the whole district in the wide aerials (pale grey, tinted olive-yellow by the haze) `[EV]` F09/000003117, F11/000010998, F11/000003670. Closer up they read dark grey-black, 5-6 in frame `[EV]` F11/000030270. They rise from the first hours of the battle onward (F09/000011497 already shows them from outside the wall).
  - Green signal flare: a tall green smoke column that starts the boulder operation `[EV]` F11/000030270.
  - Red flare (failure), fired in golden afternoon light, not at dusk `[EV]` ep12 05:03.3 (sheet_09). Yellow flare (success) `[EV]` ep13 13:04.5 F13/000018810 (a thin bright trail rising from the gate end) and ep13 13:08.5 ("Yellow signal confirmed").
  - Flares are thin smoke trails, not translucent boxes.

## 6. Choreography timeline for OUR one take (g4 establishing, 20 s; t = 0 is g3's FT7)
| t (s) | where | what happens |
|---|---|---|
| 0-3 | training camp, NW of Trost (inside Rose) | Night-to-dawn time-lapse begins: camp lamps fade and the eastern sky pales. The camera drifts SE (g3 handoff) and starts yawing toward Trost. |
| 3-8 | over Rose fields, approaching the NW corner | Sunrise: Wall Rose lights up warm. The Trost bulge appears beyond the wall: bell towers, HQ turret, the canal glinting on the east side. Chimney smoke starts. The sun climbs quickly (time-lapse) toward its late-morning position. |
| 8-13 | crossing Wall Rose near (-600..-450, 870) at about t = 10.8 | **Master overview** (composition like F11/000010998, mirrored from the north): the whole U, the avenue axis, C, H, the canal, the outer gate at the far tip, fields and the faint sea band on the horizon. The Survey Corps column appears on AV near C, riding south; civilians line the street. |
| 13-17 | descending over the west-centre (H → C) | Overtake the column at a calm height. The column reaches GS and passes out through O (door open). Riders spread onto the south road. |
| 17-20 | above AV around Y 330, looking south at GS and O | The gate closes. Lighting has reached late morning (section 5). Cadets are tiny at the wall-top cannons above O, on the red-brick wall top, with the slabs and ring pit legible. No smoke columns yet. Settle and hold, drifting slowly south. **At 20.0** the lightning flash and the Colossal's skull rise above the gatehouse: handoff to the kick beat. |

## 7. Sky-observer camera plan
- **Rules:** heights 150-330 m, pitch 20-35° down (checked for every key and anchor below), lens 28-32 mm, no roll, Catmull-Rom or Hermite positions and look-at points, lens in log space, yaw ≤ 30°/s, eased start and end.
- **Positions** are in M (add (0, -870) for the set frame, or (0, +4130) for world).

| key | t | position (X, Y, Z) | look-at | lens | pitch | speed | notes |
|---|---|---|---|---|---|---|---|
| G0 | 0.0 | (-1570, 1190, 170) | (-1450, 1490, 0) | 30 | 28 | 20 m/s SE, vz 0 | = g3 FT7 exactly (set (-1570, 320, 170)) |
| G1 | 4.1 | (-1380, 1060, 230) | (-860, 760, 0) | 29 | 21 | about 95 | yaws about 100° clockwise over 4.1 s (about 24°/s); Trost's NW corner enters |
| G2 | 9.1 | (-760, 1010, 320) | (-80, 480, 0) | 28 | 20 | about 130 (cruise) | north of Wall Rose (wall top at 50 m, clearance 270 m); full master overview |
| G3 | 12.4 | (-400, 760, 290) | (-20, 260, 0) | 28 | 25 | about 130 | over the HQ's west side; the Survey Corps column is in the lower-middle third |
| G4 | 16.8 | (-110, 430, 200) | (0, 40, 20) | 30 | 24 | about 65, easing | above C, looking SSE down AV to GS/O |
| G5 | 20.0 | (-40, 330, 170) | (0, 0, 30) | 32 | 23 | 8 m/s S, vz -1 | **handoff**: the wall top at (0, 0, 50) sits in the upper third; anything above Z ≈ 41 at Y = -25 is visible, so the Colossal's head and shoulders show over the wall as in F04/000029845 / F04/000031099. Grazing the 1.5 m outer merlons instead raises that line to about Z 46, which still shows the head and upper shoulders |

- **Pacing check (corrected).** The path G0→G5 is about 1,880 m long (segments 238, 628, 439, 448 and 126 m). The old key times and speeds did not fit these distances: the segment averages were 60, 140, 98, 112 and 42 m/s, against listed key speeds that implied 40, 100, 125, 75 and 24. Retimed for one smooth profile: accelerate from 20 m/s to about 130 m/s by t = 6, cruise to t ≈ 13, then ease down to 8 m/s at t = 20. In Blender, drive the camera along the spline by arc length (Follow Path with an animated offset, or a baked Hermite) so no key produces a speed kink. Owner check: about 130 m/s at 290-320 m with a 28 mm lens moves the ground about 11% of the frame width per second (frame about 1.2 km wide at the look-at). That is brisk for a "calm observer". If it feels rushed, stretch this beat to about 26 s with the same keys, which caps the cruise at about 100 m/s (g3's FT7 velocity and the G5 handoff stay the same).

- **Handoff to the kick group:**
  - Pass G5's position, look-at, lens 32, velocity (1.3, -8, -1) m/s and dlnlens 0.
  - The kick and pour should stay above 150 m and pull back, not push in. Do not go above about 400 m; do not zoom past 40 mm.
  - From here until the Attack Titan arrives, the camera stays aerial (owner).
- **Suggested aerial anchors for the other groups** (calm, at the moderate height):

| beat | camera position (M) | look-at (M) | lens |
|---|---|---|---|
| evac | (-20, 640, 150) | (-140, 830, 10) | 32 |
| HQ | (-20, 470, 160) | (-180, 645, 15) | 30 |
| basin | (220, 650, 130) | (345, 810, 0) | 32 |
| Pyxis (default, troops north of the wall) | (-20, 1080, 130) | (-20, 900, 20) | 32 |
| Pyxis (if the owner keeps the square in Trost) | (-20, 690, 120) | (-20, 860, 45) | 32 |
| decoy corner | (-250, 600, 180) | (-430, 815, 20) | 30 |
| boulder carry (B0 as drawn) | (110, 380, 170) | (-60, 160, 0) | 30 |
| seal | (80, 175, 125) | (0, 12, 15) | 32 |

(The old evac, HQ, basin, decoy, boulder and seal anchors pitched 36-41° down, steeper than the 20-35° rule. They are moved back so all are now 24-32°.)

## 8. Current render vs anime: gap list
Renders checked: trost_set_overview.png, trost_set_v2_sheet.jpg, trost_set_belltower.png, trost_p1_sheet.jpg, trost_p2_sheet.jpg and trost_p3_sheet.jpg.

| # | P | what is wrong now | change to |
|---|---|---|---|
| 1 | P0 | **Outer gate inside face** is a plain grey slab with a small arched hole (p1 rows 2-4, p3 row 4). | Brick 3-tier gatehouse between 2 sandstone pilasters, crest, arched doors; a tall ragged breach about 15 m wide up to Z 30-34 (Λ-shaped dark plug after the seal); brick/stone rubble fan (2b). |
| 2 | P0 | **Gate square** is a flat grey gravel apron (p1, p3 rows 4-5), with no sunken ground. | Grass semicircle with ring road; **ring pit P** with C-trenches, plank walls and bridge; 14 spiked slab barricades (6 by the pit, 8 across the avenue mouth) plus log-crib fences; after the kick, 2 large steaming craters before the gatehouse, toppled slabs, strewn debris (2e). |
| 3 | P0 | **Houses** are detached 2-3 storey cubes at random rotations, with gaps (p3 rows 1-3, overview). | Continuous 3-5 storey terraces aligned to the streets, dormers, chimneys, arcades on AV; height mix per section 3. Biggest single read in every aerial. |
| 4 | P0 | **Inner gate** is a grey wall with a plain green-lit arch (v2 panel 6, p1 rows 4-5, p2 row 6). | Stepped brick bastion with the Garrison crest and an open arch at its base; a grassy slope with trees beside it (2b). |
| 5 | P0 | **Wall** is flat blue-grey concrete with thin shallow pilasters; nothing reads on the wall top from the air (p1 rows 2-3, p2 row 5). | Warm pale stone with courses and damp/moss base; big inner pilasters (7 x 3 m, 28 m) with caps above the parapet; outer counterfort grooves; wall-top rails, turntables, cannons, huts and flags visible from 200 m. |
| 6 | P0 | **Bell towers:** one white church with a needle spire and slate nave (trost_set_belltower.png); no tower skyline (overview). | 16-20 slender square sandstone (some brick) towers with arched belfries and dark pyramid/hipped caps, 40-55 m, spread evenly (T1-T8 + fillers). |
| 7 | P1 | **District shape** is a flat wide D, 1240 x 870 (overview, v2 panel 5). | U, 960 x 870 (W 480, S 390, R 480). Also update world.py DISTRICT["rose"], the lifts and labels. |
| 8 | P1 | **Canal:** one straight blue canal on the east; reads blue-grey (p2 row 4). | ONE green canal at X ≈ 400, 2-3 house rows in from the east wall, with stepped stone banks, quays, pillar-portal bridges, a Rose water gate and an exit through the east wall at about (445, 300), continuing SE outside (2c). Today's single canal is right in count; fix its colour, position, banks and exit. |
| 9 | P1 | **HQ position:** mid-east, 380 m from Rose, keep on the west end away from the avenue (p2 row 1). | Keep (-165, 640) on the avenue side, warehouse west; pale plaza east of it, at the end of the AV vista `[INF]` (F08/000009331 shows the HQ on a rise in front of Wall Rose but no avenue). |
| 10 | P1 | **Streets:** dark gravel grey, no ring/radial reading; avenue is a straight diagonal (overview). | Pale cobbles; AV with kinks; ring streets around C and radials. |
| 11 | P1 | **Boulder:** smooth blue-grey plastic sphere alone in an empty gravel square (v2 panel 4, p3 rows 1-3). | Round per the owner, but rough cracked grey-beige stone with dark marbling and a rubble skirt, in Boulder Court among 4-storey terraces next to T7 (F11/000026466; texture ep13 10:3x `[LOG]`). |
| 12 | P1 | **Fountain** is a flat white disc in the market plaza (p1 row 6, p2 row 1). | Remove the plaza disc. Obelisk fountain in square A, which per the anime is NORTH of Wall Rose (owner decision, section 9). |
| 13 | P1 | **Flares** render as wide red translucent beams/boxes (p3 row 1). | Thin smoke trails with a bright head (flare group). |
| 14 | P1 | **Lighting** is flat grey-blue in every Trost render. | Early morning (Corps), then late morning with cumulus (cadets/Colossal), then overcast, then golden hour, then dusk (section 5). |
| 15 | P2 | Missing: the gate-foot hamlet outside, the conifers beside the outer gatehouse, the HQ front stair terrace, a slight rise toward the HQ (`[EV]` F07/000006613 "HQ on a rise" `[LOG]`), and yard trees. | Add if the budget allows. |

## 9. Owner-rule overrides (we intentionally differ from the anime)
- **Boulder shape.** The anime is inconsistent: craggy lump in ep11/12 (F11/000026466) versus a near-sphere in ep13 (F13/000017944). The owner says a near-perfect ROUND ball, 12-15 m. We keep the sphere and borrow the anime's surface (cracked, marbled, steaming) and the courtyard setting.
- **Inner gate.** The anime has a small arched door with the cart jammed in it. Owner: an OPEN passage, and the cart is shoved a little to the side.
- **Mountains.** The anime shows mountains behind the walls (F08/000009331, F09/000018289). Owner: gentle hills only, plus the sea band far south.
- **District size and canal geometry.** The anime is inconsistent between shots. We fix one plan (U 960 x 870, ONE canal down the east side) and accept that some shots will not match.
- **HQ.** The anime changes the HQ's look and position between shots (palace against the north wall in F04/000029323, a free keep in the aerials). We follow the owner's HQ refs and place it at the end of the avenue vista, 230 m south of Wall Rose.
- **People and titans.**
  - Faceless toon humans from downloaded assets only, at true scale; no red-cape giants.
  - Titans at true heights, kept tasteful.
- **Camera.** The anime's rooftop, chase and close-up shots become calm aerial observer shots, in one continuous take with no cuts.
- **Training camp.** It sits next to Trost (owner); the anime puts it in the mountains.
- **Ring pit.** The anime's pit is a pre-existing timber trap structure, not a kick crater. We build both: the ring pit (pre-existing) and the 2 large kick craters before the gatehouse (F04/000034425). Together they satisfy the owner's "cratered/sunken ground where titans fall".
- **OWNER DECISION: Pyxis's square is outside Trost.** In the anime the troops hear Pyxis in a square NORTH of Wall Rose (evidence in section 1, item 5, and 2d, A). Our world has no buildings north of Rose. Options: (a) default in this spec: troops on an open paved forecourt with the obelisk fountain just north of the inner gate, no houses, and the camera rises over Wall Rose to see them; (b) also add one small block of terraces around that square (breaks "only Shiganshina and Trost have buildings"); (c) move the square into Trost at the wall foot as the spec first had it (not lore-accurate).
- **OWNER DECISION: boulder start B0.** The spec places it west of the avenue at (-150, 230) `[INF]`. F11/000030270 suggests it lies one or two blocks west of the east canal at about mid-depth (about (330, 420)). Moving it changes the route (about 530 m south-west to the gate, down the canal-side streets and onto AV) and the boulder-carry camera anchor.
- **Breach shape.** The kick-day breach is a tall straight-sided ragged hole (F04/000034425). The Λ shape belongs to the post-seal plug (F13/000019098). Build the hole first and add the plug mass at the seal.

## 10. Must-have lore details checklist
- [ ] U-shaped bulge with straight side walls, Wall Rose straight behind it, 50 m walls with big inner pilasters (F11/000010998, F09/000003609).
- [ ] The outer gate at the tip: from outside, a tall rust-red riveted iron frame with roots hanging along the wall top (F09/000011497); from inside, a 3-tier brick gatehouse between sandstone pilasters, flanked by conifers (F13/000019194).
- [ ] The tall ragged breach with a rubble fan and 2 steaming craters in the grass in front of it (F04/000034425); later the Λ-shaped dark plug with the boulder at its base (F13/000019098).
- [ ] The ring pit in front of the gate: concentric C-trenches, plank retaining walls, plank bridge, a titan lying in it (F11/000014506, F13/000012552).
- [ ] Giant trapezoidal spiked slab barricades on small wheels in an arc in the gate square, plus at the avenue mouth (F09/000003609, F04/000025018, F04/000030127).
- [ ] The main avenue from the outer gate north, lined with terraces (F09/000003620, F04/000025114); the Survey Corps rides out down it (F04/000025114).
- [ ] The HQ keep with its turret rises above the roofs on a slight rise, with a pale plaza around it (F08/000009331, F08/000014937).
- [ ] 16-20 slender square bell towers spread evenly through the roof field (F04/000029323, F04/000029419).
- [ ] ONE green canal down the east side, 2-3 house rows in from the wall, with pillar-portal bridges, leaving through the east wall and running on SE outside (F11/000010998, F11/000003670, F11/000030270, F13/000018810).
- [ ] The inner gate as a brick bastion with a crest and a grassy slope with trees beside it (F06/000008308).
- [ ] The obelisk fountain square below the wall top where Pyxis speaks, north of Wall Rose per the anime (F11/000006876, F11/000019523, F09/000018481); see the owner decision in section 9.
- [ ] Wall-top rails, cannon turntables, crates, tiled huts and green flags; red-brick paving on the bulge wall tops, pale stone on Wall Rose (F04/000029845, F04/000029323, F10/000028037, F11/000019523).
- [ ] The decoy titan mass packed in a wall corner, arms raised (F12/000005181, F12/000019053).
- [ ] The boulder waits in a courtyard among 4-storey terraces next to a belfry (F11/000026466).
- [ ] The cannon basin near Wall Rose, east of the inner gate, opening onto the canal; steam seen from the south (F09/000031091).
- [ ] Farm fields and hamlets outside the east wall; the canal exits ESE and runs straight SE (F09/000003117, F11/000003670).
- [ ] Flares as thin smoke trails: green (operation start), red (failure, afternoon), yellow (success) (F11/000030270, ep12 05:03.3, F13/000018810).
- [ ] Pre-attack Trost is smoke-free; 10-15 thin smoke columns appear only after the kick (F04/000029323 against F11/000010998).

## Eevee / GTX 1060 build notes
- **Instancing:**
  - Houses: 8-12 terrace-segment variants (3, 4 and 5 storeys x 2 facade styles x 2 roof colours), placed along street polylines as Geometry Nodes or collection instances. Merge per block for culling.
  - Bell towers: 2 meshes (sandstone, brick) x 16-20 instances.
  - Spiked slab barricades: 1 mesh x 14 (plus 1 broken variant for the post-kick state). Cannons and turntables: 1 linked set x about 90.
  - **Poly budget (GTX 1060, 3-6 GB):** the 0.74 km² district needs about 3,000-4,000 terrace segments. Use 3 LODs: hero at 3k tris or less within about 250 m of the camera path (the avenue, gate square, HQ and inner-gate corridor); mid at 600 tris or less with a baked facade texture; far at 150 tris or less (box plus roof prism with an atlas). Keep the visible total around 3-5 M tris and textures at 2k or below on trim sheets/atlases. Instance everything (collection or GN instances share memory).
- **Ring pit:** one modelled mesh (about 3k tris) with a tiled plank texture. Craters: displaced discs with a dark decal; no sculpting.
- **Wall:** one bay module (pilaster plus panel) instanced around the outline; detail from a trim sheet, damp/moss as a vertex-colour gradient.
- **Crowds:** the 600 civilians and 120 riders as low-poly instanced asset LODs (300 tris or less; at 150-330 m a 1.65 m person is only a few pixels tall). Riders far away can be cards. The same applies to the hundreds of soldiers on the decoy wall tops and the Pyxis assembly.
- **Titans at the decoy (60-100+):** do not give each one its own rig. Bake 6-8 looping arm-raise/sway cycles to Alembic (Mesh Sequence Cache) and place copies with per-object frame offsets and random scale (3-15 m), giving about 0.5 M tris in total. Instanced armatures would all share one pose.
- **Lighting/shadows (Eevee):** one sun plus world. On a 2 km set, Eevee's virtual shadow maps can exhaust a small shadow pool. Keep the shadow pool modest (512 MB or less on a 3-6 GB card), give the sun a coarse resolution limit (about 0.1 m), and test-render the widest key (G2) first. Fake distance haze with the mist pass (as noted in section 5) rather than volumetrics.
- **FX:** smoke and chimney wisps as alpha cards or flipbooks; the canal as a flat plane with a green gradient and screen-space reflections off.

## 11. Verification log (adversarial review, 2026-10-26)
I opened every cited frame plus the ep04, ep09, ep10, ep11, ep12 and ep13 contact sheets around each beat. Changes, in spec order:
1. **Section 1, item 1:** the four "Trost seen whole" aerials (F09/000003117, F11/000010998, F11/000003670, F13/000021857) all show the battle or its aftermath: 10-15 smoke columns, and the last one at dusk. They are now marked layout-only. The pre-attack look comes from F04/000029323/29419.
2. **Section 1, item 2:** the Survey Corps leaving the same morning is now `[EV]` (ep09 02:26.5 caption). The ep04 scene before it is graduation night (17:12.7).
3. **Section 1, item 3 and section 5:** the cadet/Colossal time is LATE morning (ep04 20:17.5 "We've still got a while until lunch"), with many cumulus. The sun moves from ESE 35° to SE 45-50°. Added an early-morning light state for the Corps departure.
4. **Section 1, item 5:** added the anime order of the kick (20:44.8 head, then 20:55.6 / 20:56.2 / 20:56.5 / 20:57.9 / 21:01.1 / 21:27.2 / 21:37.1 / 23:55.8) and the yellow lightning flash (20:42.7-20:43.4).
5. **Pyxis square:** it is NORTH of Wall Rose. Evidence: ep09 12:50.8 F09/000018481 "Within Wall Rose" shows the same obelisk fountain, after "got out of Trost District" (12:54.8); the troops say "Isn't entering Trost District just suicide?" (ep11 04:02.4) and "I'm not going back there!" (04:50.8). Square A was rewritten with a no-buildings default, and an owner decision was added to section 9.
6. **F09/000018481 and F10/000031399** both look at the north (Rose-interior) side. They no longer count as Trost evidence: removed the windmill WM, the Trost water-gate citation, the arched-bridge citation and one tower citation.
7. **Canals:** TWO canals became **ONE**. Zoomed aerials show a single channel. It lies 2-3 house rows plus a quay road in from the east wall, NOT at the wall foot (F11/000030270, F13/000018810). Its bridges are pillar portals, not arched spans. It exits through the east wall at about (445, 300) and runs on straight SE outside past hamlets. Updated 2b, 2c, 2d, 2g, 3, 8 and 10.
8. **Cannon basin K:** moved to (345, 810) so it opens onto the single canal (the deleted Canal B had been its water link). Evidence: stepped banks down to water, ep09 18:05.8.
9. **Bell towers:** 8 became **16-20** (F04/000029323/29419 show 16-20 slender towers; the old note said "5-6"). Updated 2d, 3, 8, 10 and the build notes.
10. **Wall Rose inner face:** it is at Y = 865 (centreline 870, 10 m thick), not 858. The inner-gate bastion is now Y 853..865, forecourt E reaches Y 853, and the cart sits at (-140, 860).
11. **Outer wall, outside face:** the groove spacing is about 20 m, not 25 (measured against the 50 m height). Roots hang along the whole wall top, not just the lintel. The gate is a rust-red riveted iron frame about 20 x 45 m with a transom at about 26 m and a smashed lower door; titans walk in from outside (F09/000011497 is post-kick).
12. **Gatehouse, town side:** F04/000030104 is now `[EV]`: 2 arched strap doors (small and large) with a wall-goddess crest plaque, and curved pilaster feet. The seal timestamp is corrected to 13:20.5, and F13/000019098 is added.
13. **Breach shape:** the kick-day hole is tall, straight-sided and ragged, to Z 30-34 (F04/000034425). The Λ / spire shape belongs to the post-seal plug, which reaches about Z 38 (F13/000019098).
14. **Ring pit:** the centre moves from (-6, 36) to (0, 36). The "left = west" reading was wrong, because F09/000003609 looks south, so left is east. The apparent offsets in both views are perspective. The 2 heaped slabs are on the EAST. The plank-bridge bearing is now `[INF]`. Titan positions are refined (one sprawled on the middle ring, one by the gate, 3-5 at the lip). Added the paved path to the bridge (F04/000030160).
15. **Barricades:** the "slabs" and the "spiked wheeled barricades" are ONE prop: tall trapezoid plank boxes with black spikes and small wheels (F04/000030127). The separate 4 x 3 x 2 m type is removed. The count is fixed at 14 (6 by the pit, 8 across the avenue mouth), which resolves the 6 / 8 / 14-16 mismatch between sections 2e, 3 and the build notes. Colour is now mid/pale tan, not dark.
16. **Craters:** "6-8 craters, 3 east of P" became 2 large (6-10 m) steaming craters in front of the gatehouse (F04/000034425). The top-down F11/000014506 shows none east of the pit. Optional smaller ones are `[INF]`. Added the post-kick debris types (crossed X stakes, lids/wheels, crates, broken fences) and the small blood stains. Route BR now goes round the pit's east flank, because the C's closed back faces the town; the old "down into the pit gap" contradicted the at-grade gap.
17. **Bollards:** dark grey, about 1.5 m, with a plank deck edge in front; now `[EV]` F13/000018285.
18. **Boulder B0:** F11/000030270 shows a pale round mass with a steam wisp beside the east canal, at about (330, 420). Flagged as an owner decision; B0 is kept as drawn.
19. **Decoy corner:** the "NW" choice is now explicitly `[INF]` (the lighting fits either corner). Added the soldiers packed on the wall tops (F11/000026658) and the ep12 03:36.1 caption.
20. **Wall-foot strip:** "grass verge along every wall" was unsupported. There are trees only by the inner gate and conifers by the outer gatehouse; elsewhere terraces come up to the wall road.
21. **Wall top:** the bulge wall tops are paved in red-brown BRICK (ep04); Wall Rose's is pale stone. Huts are 4-6 m, 1-2 storeys, half-timbered on stone. Added the toothed merlon rim seen in the aerials.
22. **Smoke and flares:** 10-15 thin columns in the aerials, not 4-6. Red flare = ep12 05:03.3 in golden afternoon light, not dusk. Yellow flare = `[EV]` ep13 13:04.5 / 13:08.5 (it was "canon `[INF]`").
23. **HQ:** the "closes the AV vista" claim had no avenue in its cited frame (F08/000009331); now `[INF]`. Noted that the anime puts the wing west of the keep in one aerial and east of it in another.
24. **Camera:** the key speeds did not match the key spacing. Retimed G1 4.1 / G2 9.1 / G3 12.4 / G4 16.8 with a smooth 20 → 130 → 8 m/s profile and arc-length drive. G1's pitch was 18°, below the 20° rule; its look-at moves to (-860, 760). Six of the other-group anchors pitched 36-41°; all are now 24-32°. Added a Pyxis anchor north of the wall and a pacing note for the owner. One-take continuity is intact: G0 = g3 FT7 and G5 is the unchanged handoff, with the merlon line-of-sight checked (Colossal head visible above about Z 46).
25. **Build notes:** added a poly/LOD budget for about 3-4k terrace segments, baked Alembic titan crowds (not 100 rigs), crowd LODs and Eevee shadow-pool advice for a GTX 1060.
26. **Unchanged after checking:** the U outline, wall height and pilasters, gatehouse tiers and pilasters, ring-pit form, avenue and gate-square ring road, inner-gate bastion and crest (F06/000008308), HQ placement (owner refs), Survey Corps on AV (F04/000025114), the Colossal handoff framing, and the owner overrides (round boulder, open inner gate with the cart shoved aside, no mountains, faceless true-scale humans, skipped close beats).
