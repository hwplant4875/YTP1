# g7_trost_cannon_pyxis: cannon basin standoff, half-shift, Armin's salute, Pyxis, wall-top walk, speech, deployment

Owner rules (BRIEF.md, HANDOFF 09:37 (10/25) item "CANNON", 13:49/15:29 QA) win over the anime.
Tags: `[EV]` = I opened the frame myself; `[LOG]` = from the Sonnet logs, not re-checked; `[INF]` = my inference.
Frame aliases: `F09/` = /tmp/claude-0/aot/anime/frames/ep09/, and the same for F10 and F11.
Coordinates are in g4's MASTER frame M: origin at the outer-gate centre, +X east, +Y north, +Z up, town ground Z = 0. Wall Rose has its centreline at Y 870, its Trost (south) face at Y 865, its north face at Y 875, and its top at Z 50. The canal centreline is X 400 (X 387..413). trost.py set frame = (X, Y - 870).

**Headline finding.** In the anime the basin, the standoff, the half-shift and Pyxis's troop square are all NORTH of Wall Rose, in the Rose interior. Three pieces of evidence show it:
- F09/000031091: seen from inside Trost, the steam column rises from behind the unbroken face of Wall Rose, a little right (east) of the inner gate.
- F10/000003981 and F10/000005610: the same squad stands in a half-timbered street that ends at the closed inner gate, seen from the north.
- F11/000019523: the troop square lies in the shadow of the wall.

The owner explicitly wants the basin "inside Trost" (HANDOFF 09:37). So I **mirror the anime basin onto the Trost (south) face of Wall Rose**, at the canal's water gate. Compass E/W is kept and N/S is flipped. Pyxis's troop square stays north of the wall, as g4 already decided (default (a)). The wall-top talk (S1) is on the Rose top above the INNER GATE (caption "Trost District Inner Gate", ep10 18:35.4), so the group walks west from the basin hoist to it in a time-lapse. See section 9.

---------------------------------------------------------------------------------------------------------------------

## 1. Lore summary of the beats, in order, with evidence

1. **The trio is already on the basin floor, surrounded, when Eren comes to.** Eren wakes on the floor (close-ups ep09 11:29.0-11:44.4, mossy cobbles behind him). At 11:45.3 Armin holds Eren up while Mikasa stands guard with her blades ALREADY drawn; Garrison soldiers sit and stand on the steps above them, looking down. They do not walk down a stair: they stand on the floor facing the bank. `[EV]` ep09 11:45.3 F09/000016910.
   - How the 104th got here is shown in a grey flashback: cadets on the crenellated Rose top `[EV]` ep09 13:43.5 F09/000019744, beside a timber A-frame derrick with a wheel `[EV]` 13:47.5 F09/000019840, then lowered in an open basket hung on 4 chains, which faces the plinth and the stepped bank `[EV]` 13:51.5 F09/000019936 and 13:55.5 F09/000020032. This is the evidence for the basin hoist L_K (2b).
   - The basin floor is a big sunken mossy court at the very foot of the Wall, between two massive battered buttress piers. Water (the canal) and a barred water gate are on one side. The trio is tiny at the centre and the Garrison stands on the stepped bank and a projecting plinth. `[EV]` ep09 11:51.3 F09/000017054 and ep09 15:14.0 F09/000021915 (= the owner's trost_cannon_canal_ref.png).
2. **The cannon is aimed at them.**
   - It stands on a raised paved terrace (a bastion against the Wall face) with a rail spur and a round turntable. A pale bell tower is beside it and houses lie below its deck. `[EV]` ep09 15:31.8 F09/000022341 (looking down on the gun with roofs below), ep10 10:16.9 F10/000014792, ep11 00:18.8 F11/000000451 (the gun deck, tower at its left, Wall face at its right, steam ahead).
   - Gun details: muzzle `[EV]` ep09 16:59.2 F09/000024436; looking down from it to the tiny trio far below on the floor `[EV]` ep09 19:58.4 F09/000028733.
   - From below, the gun deck reads as the flat top of a tall pier projecting from the Wall face: the barrel and its crew stand on the pier top against the sky, with the Wall face continuing higher behind `[EV]` ep09 19:57.9 F09/000028720 (a lone signaller standing on the pier top beside the gun) and 21:26.3 F09/000030840 (gun and crew on the pier top, the Wall face to the left).
   - The crew is 4 (one at the breech, one crouched at the turntable, one standing, one holding a long rammer/sponge pole) `[EV]` F10/000014792; two more sit on the turntable rim in F09/000022341.
3. **The standoff.**
   - The stepped bank has two stair flights with a raised square plinth between them, and a Garrison building and a half-timbered range behind `[EV]` ep09 17:19.5 F09/000024922.
   - Mikasa holds her blades drawn throughout `[EV]` 11:45.3 F09/000016910, 11:51.3 F09/000017054; at 17:28.8-17:32.8 she plants her stance (a puff of floor dust) and raises them, which is why the floor in F09/000024922 is hazed with low dust. Seen from above, the whole Garrison line forms an L along the bank, the boats are moored at the water edge, and a bell tower stands at the corner `[EV]` ep09 19:31.0 F09/000028075 and 19:35.0 F09/000028171.
4. **Fire.**
   - The captain (bearded, "Captain Felman" in these subs `[EV]` ep10 17:13.5) first raises his arm at ep09 19:56.9-19:57.4 F09/000028696 / F09/000028708; a signaller on the gun pier answers `[EV]` 19:57.9 F09/000028720. He gives the fire signal on the plinth `[EV]` ep09 21:08.6 F09/000030416.
   - The muzzle flash is huge yellow-white `[EV]` ep09 21:14.3 F09/000030553, followed by a grey-brown smoke puff at the muzzle `[EV]` ep09 21:15.7 F09/000030586.
5. **Half-shift.**
   - Eren bites his hand (spark) `[EV]` ep09 21:29.7 F09/000030923. In the anime 15 s of flashback (Grisha, the key) sit between the flash (21:14.3) and the bite; the order is flash, bite, arm, impact. We play it in real time (fire at 15.00, impact at 15.35).
   - The bone and rib arm swings up through dust `[EV]` 21:31.4 F09/000030963. A black silhouette arm sweeps `[EV]` 21:32.5 F09/000030990. Red muscle arm `[EV]` 21:33.9 F09/000031022.
   - The orange fireball of the shell hitting it `[EV]` 21:34.8 F09/000031044.
6. **Steam.**
   - A single thick white-brown column rises over the district, seen from inside Trost `[EV]` ep09 21:36.8 F09/000031091 and 21:39.3 F09/000031151.
   - Five 104th cadets (training-corps emblems, not Garrison) stand on a high pale paved ledge and stare into the billows `[EV]` 21:51.3 F09/000031440; Kitz is swallowed by steam on the plinth `[EV]` 21:48.4 F09/000031370. Mikasa and Armin crouch under a bone arm `[EV]` 21:56.3 F09/000031560.
   - The skeleton itself: skull, red muscle on the shoulders and upper arm, gold-cream ribcage, no lower body `[EV]` 22:13.6 F09/000031975 and the owner's eren_halfshift_skeleton_ref.png.
7. **The aftermath in the steam.**
   - The steam swallows the plinth `[EV]` ep10 05:26.7 F10/000007834. Soldiers stand waist-deep in steam on the bank `[EV]` ep10 05:15.7 F10/000007570.
   - Inside: the ribs arch overhead like branches, with violet flowers on the ground `[EV]` ep10 06:12.5 F10/000008930 and 18:04.4 F10/000025999.
   - Eren tears himself free of the skeleton's nape (muscle fibres snapping) `[EV]` ep10 05:53.6-06:00.7 (sheet_09); he is out BEFORE Armin's walk.
   - The Garrison lines the top edge of the bank with blades drawn in front of the steam; "Captain, the high-explosive shell is almost loaded" `[EV]` ep10 10:02.9-10:06.9 (sheet_14). Armin judges the reload needs "at least another 20 seconds" `[EV]` ep10 10:32.3. Our second fire order at t 38.5 (23.5 s after the first shot) fits this.
   - Across the dark mossy floor, the trio is tiny beside the skeleton arm, with rubble lumps `[EV]` ep10 10:32.3 F10/000015159.
8. **Armin walks out alone, hands up.** `[EV]` ep10 14:38.5 F10/000021062.
   - He stands about 10 m in front of the plinth, where 2 riflemen kneel and the captain stands `[EV]` ep10 17:09.5 F10/000024684 and 14:42.5 F10/000021158.
   - The plinth, the flights and the buildings seen from his position `[EV]` ep10 15:57.1 F10/000022947 = the owner's trost_armin_salute_steps_ref.png.
   - The riflemen kneeling at the plinth's front edge and the clock-gable building `[EV]` ep10 16:16.4 F10/000023409. The plinth top is FLAT to its edge (no parapet or coping): the two riflemen kneel right at the front corners `[EV]` F10/000024684.
9. **Armin's salute** (right fist to the heart): "I am a soldier that has long since offered his life for the revival of mankind!" `[EV]` ep10 16:38.5-16:43.0 F10/000024047.
10. **The captain orders fire again.** The red-tinted sequence (ep10 17:19-17:28, sheet_23). **Pyxis** appears from the ranks and catches the raised arm: "as feeble as a fawn" `[EV]` ep10 17:36.5 F10/000025331.
    - Pyxis is bald, with a red sash, and has riflemen and his aide Anka behind him `[EV]` 17:38.5 F10/000025379.
    - He emerges from among the soldiers (Anka and riflemen behind him); where he came from is not shown. He walks across the pale flagstones with Kitz and 2 riflemen `[EV]` 17:43.5 F10/000025499, and talks with Kitz down on the mossy floor `[EV]` 17:49.7-18:02.1 (sheet_23). Eren and Mikasa wait by violet flowers `[EV]` 18:04.4 F10/000025999.
11. **Pyxis takes them up Wall Rose, at the INNER GATE.**
    - The scene opens on the caption "Trost District Inner Gate" over the gate face, with naked titans heaped at its foot, reaching up `[EV]` ep10 18:35.4 F10/000026743 and 18:51.5 F10/000027129. **The wall-top talk therefore takes place on the Rose top above the inner gate**, not above the basin. A second check: in F10/000029703 Pyxis looks south and the outer gate stands a little LEFT (east) of his line of sight. That fits a spot near X -120 (the inner gate is at X -140), not X 302, where the outer gate would be far to his right.
    - Kitz, down at the wall foot, looks up: "How could he accompany such suspicious people up there?" `[EV]` ep10 19:04.1-19:13.3 (sheet_24).
    - Pyxis stands at the wall-top edge with smoke columns behind him `[EV]` 18:41.0 F10/000026877. The trio is by the rails `[EV]` 18:45.0 F10/000026973.
    - **The wall-top walk**: Pyxis walks along the rails past the turntable cannons and crates `[EV]` 19:29.4 F10/000028037 and 19:54.2 F10/000028633 (two tracks, turntable guns, crate stacks, a hoist cage hanging over the edge at top right).
    - He stands hands behind his back, looking SOUTH over Trost (smoke columns, the far outer wall with the outer gate, hills) `[EV]` 20:38.9 F10/000029703.
    - Then they turn NORTH: Pyxis and Eren sit on the north parapet while Mikasa and Armin stand by the rails, all looking over the Rose interior (towers, a canal with arched bridges, hills) `[EV]` 21:45.6 and 21:49.6 F10/000031399. (They are not walking away.)
    - Later (ep11 05:40-06:47) Pyxis and Eren talk again on the wall top among upright cannons and crates, with two elite officers `[EV]` ep11 sheet_08/09.
12. **Pyxis's speech.**
    - Before the speech the troops mass at the foot of the inner gate's NORTH face (the tall framed gate panel) `[EV]` ep11 03:58.4 and 04:02.4 (sheet_07; "Isn't entering Trost District just suicide?").
    - The troops crowd a square with an obelisk fountain, half in the wall's shadow `[EV]` ep11 07:09.9 F11/000010308 and 04:46.8 F11/000006876.
    - Pyxis stands on the wall-top edge with **EREN beside him** (white shirt and harness, not an aide), cannons and dark-green banners behind `[EV]` 07:16.5 F11/000010466. He presents him: "Belonging to the Training Corps, this is Eren Jaeger!" `[EV]` 07:51.3-07:59.4 (sheet_10).
    - Looking down from the wall-top cannon deck onto the crowded square, with a dark building with pointed turret roofs at the wall foot `[EV]` 13:34.3 F11/000019523.
    - Climax, Pyxis from behind facing the packed square AND a long street packed with troops running away from the wall `[EV]` 20:35.4 F11/000029621 ("...mankind will recapture territory from the Titans for the first time in history!").
13. **Deployment.**
    - The elite squads are briefed among the wall-top cannons `[EV]` ep11 15:16.6 F11/000021977, 16:42.6 F11/000024038 (crates and a cannon row) and 14:19.8 F11/000020615 (rails, a row of upright cannons, a timber truss walkway).
    - The wall top is packed with hundreds of soldiers, with a red-roofed hoist hut and a cage over the edge `[EV]` 18:31.9 F11/000026658.
    - Titans press against the wall face with arms up while soldiers climb on ODM wires `[EV]` 18:35.9 F11/000026754.
    - The elites run along a stone parapet and leap ("Let's go!") `[EV]` 20:43.0 F11/000029803, 20:44.0 F11/000029826; Eren and the squads drop off the wall top over the roofs `[EV]` 20:44.9 F11/000029847 and fly on over Trost `[EV]` 21:19.2 F11/000030669.
    - A flare gun is raised and fired skyward `[EV]` 20:57.6 F11/000030153; a **green flare** goes up from the far (south) part of town, under 5-6 dark smoke columns at sunset `[EV]` 21:02.5 F11/000030270. Pyxis, Anka (with a brass telescope) and officers watch from a wall-top post with a timber railing `[EV]` 21:04.3 F11/000030312.
    - **The green flare belongs to g8** (it fires it at g8 t 7.5 from GF (330, 140, 50)). g7 ends with the leap-off; HANDOFF to the boulder group.

**Log correction:** the ep10 Sonnet log calls the half-shift site a "wall-top terrace" and the plinth a "dais". That is wrong. F10/000015159 and F10/000024684 show the same mossy basin floor and plinth as ep09. Only the cannon sits on a raised terrace.

## 2. Layout and geography (M frame, top-down)

### 2a. Disagreements with g4 (please reconcile in the master map)
| # | g4 says | anime / owner says | proposal |
|---|---|---|---|
| G1 | Basin K centre (345, 810), floor X 320..370, Y 785..835. It opens east onto the canal and sits 30 m clear of the Wall. | The floor lies AT the Wall foot. The Wall face, with two huge battered piers, is the basin's back wall (F09/000017054, F09/000028171). The canal runs along one side of the floor and dives through a barred water gate in the Wall (owner ref, top-left). | **Floor X 340..385, Y 833..865.** The Wall face is its north edge, and the canal (X 387..413) is its east edge, entering the Wall Rose water gate at (400, 865). |
| G2 | Canal water at Z -3 | The basin floor is about 3.6 m below the bank top (12 steps of 0.3 m, F10/000022947), and the boats float just below the floor edge (F09/000028171) | Floor Z -3.6; **canal water Z -4.2** for its whole inner run (deepen g4's banks by 1.2 m). |
| G3 | Inner-face pilasters 7 x 3 m at 28 m centres everywhere | The two piers framing the basin are far more massive and battered (sloped faces), and one stands with its foot in the water (F09/000017054, F09/000028171) | Two special **water-gate piers** (2b). Regular pilasters elsewhere. |
| G4 | Wall Rose cannons every about 60 m, a single track on the inner side | The Rose top seen from above has TWO tracks with turntables about every 15-20 m, alternating (F11/000007976, F10/000028633). There is a row of upright guns and a timber truss walkway (F11/000020615). | Keep 60 m in general. On the stretches we show close (the hoist stretch X 300..350, and S1 + S2: X -160..+40), put cannons every 20 m on both edges, plus crates, banners and huts. |
| G5 | Lifts L at (-380), (-40) and (260, 870), plus O | The 104th are lowered into the basin from the Rose top in an open basket on 4 chains, worked from a timber A-frame derrick with a wheel on the wall top (ep09 13:47.5 F09/000019840, 13:51.5 F09/000019936). The deployment uses hoist cages (F11/000026658). | Add **L_K**, a chain hoist down the west pier face, from the basin floor to the wall top (2b). Add 3 cage hoists on the Rose NORTH face at X -60, -20 and +20 for the troops at A. |
| G6 | No tower near K | A pale 4-storey bell tower with a red pyramid roof stands at the basin corner beside the gun bastion (F09/000028171, F10/000014792, F11/000000451) | Add **T_K** at (322, 818) (2b). It counts toward the 16-20 towers. |
| G7 | Pyxis at (-20, 870, 50), facing NORTH over square A (-20, 935) | Agreed for the speech (F11/000019523, F11/000029621). The anime also has an earlier wall-top talk where he faces SOUTH over Trost (F10/000029703), and it is captioned "Trost District Inner Gate" (ep10 18:35.4). | Two spots: **S1** = the Rose top's south edge just EAST of the inner gate, (-120, 866, 50), for the talk and the look south; **S2** = g4's (-20, 874, 50) at the north edge, for the speech. |
| G9 | No titans recorded along Wall Rose's Trost face except at the inner gate | ep09 14:00.7 F09/000020157 and 14:04.7 F09/000020253: from the Rose top, dozens of titans pack the Trost-side wall foot along a long stretch ("A defensive wall of flesh using the Titans themselves"); F10/000027129 shows the heap at the inner gate. | Mass them along the Rose foot from the decoy corner to about X +100, densest at the inner gate (X -170..-110). Keep X 200..480 clear so the mirrored basin stays plausible (owner override, section 9). |
| G10 | Square A centre (-20, 935), "just north of the inner gate" | The anime troops face the inner gate's north face (ep11 03:58.4, 04:02.4), but g4's inner gate is at X -140, 120 m west of A's centre. | g4 decides. If g4 recentres A on the inner gate, move S2 to (-140, 874, 50) and shift C12-C13 120 m west; nothing else changes. |
| G8 | "Pyxis through the boulder: golden late afternoon, sun low W/NW" | The basin frames are bright, warm and golden with long shadows (F09/000024922, F09/000017054). By the deployment it is sunset (F11/000030270). | Sun azimuth about 255° (WSW to W), not NW, so the south face of Rose (our basin) gets grazing light. Elevation 28° at the basin, falling to 12° at the green flare. |

### 2b. Placement (this beat's own objects)
| id | what | position / extent (M) | size / notes | evidence |
|---|---|---|---|---|
| KF | **basin floor** | X 340..385, Y 833..865, Z -3.6 | 45 x 32 m. Flat mossy cobbles. The east edge is a 0.6 m stone lip down to the water (Z -4.2), with 4 iron mooring rings. | F09/000017054, F09/000021915, F09/000028171 |
| PW | **west pier** (water-gate buttress) | X 331..340, Y 857..865 at its foot | 9 m wide, projecting 8 m at the floor. Its faces are battered (sloped about 8°), narrowing to 7 x 4 m at Z 30, where it joins the normal pilaster to the top (Z 50 + cap). Its corners are rounded and weathered. | F09/000017054 (right pier), owner ref |
| PE | **east pier** | X 385..393, Y 857..865, its foot standing in the canal's west edge | same profile as PW | F09/000028171 (the left pier rises from the water) |
| WG | **Wall Rose water gate** | arch over the canal, X 393..411, Y 865..875 | 18 m wide, crown at Z 7 above the water. An iron portcullis grid of 0.35 m bars at 1.5 m centres reaches down to 1 m above the water, with a dark tunnel behind. | owner ref (top-left), F09/000021915 |
| SB | **stepped bank (south)** | X 340..385, Y 821..833 | 12 steps, rise 0.3 m and tread 1.0 m, from Z -3.6 up to the top terrace at Z 0. Pale ashlar with darker worn nosings. At its east end the lowest steps run on past the floor's lip and down into the canal water, so seen from the floor the east flight rises straight out of the water `[EV]` ep09 18:05.8 F09/000026033. | F10/000022947, F09/000024922, F09/000026033 |
| PL | **plinth** (the "dais") | X 357..367, Y 828..838 | A 10 x 10 m square block projecting 5 m into the floor from the bank. Top at Z -0.6, so the front face is 3.0 m tall. Sharp corners and a 0.4 m carved band with a wavy relief just under the rim. The top is flat paving right to the edge: **no parapet or coping**; the 2 riflemen kneel at the front corners. The flights left and right of it are each about 17 m wide. | F10/000022947, F10/000023409, F10/000024684 |
| SW | **west stepped bank** | X 340..348, Y 833..855, steps down eastward from a ledge at Z 0 | a short 8 m-wide flight along the gun bastion's foot. It gives the Garrison line its "L" (F09/000028171). | F09/000028171, F09/000028075 |
| TT | **top terrace / quay street** | Y 813..821 along the bank, continuing east as the canal's west quay and west to the tower | 8 m wide, pale paving, iron bollards on the canal side | F09/000024922 |
| GB | **cannon bastion (pier top)** | X 308..338, Y 849..865, deck at Z 20 | A tall stone pier-bastion projecting 16 m from the Wall face, built in one with PW (same battered faces and weathering), so that from the floor it reads as a pier with the gun standing on its top against the sky and the Wall face rising another 30 m behind it (F09/000028720, F09/000030840). Its deck is pale limestone with ochre stains. It carries a 2-rail spur (1.5 m gauge, dark sleepers) and a 3.5 m wooden turntable. A 1.2 m parapet runs on its east and south edges, and a stair tower (P2) stands at its SW corner. | F09/000022341, F10/000014792, F11/000000451, F09/000028720, F09/000030840 |
| CN | **the cannon** | turntable centre (318, 857, 20); the muzzle reaches about (321, 857, 21.8) | Aimed at the trio (362, 852, -3.6): bearing about 95° (east), depression about 27°, slant range about 48 m. | F09/000028733 (steep look down) |
| T_K | **bell tower** | (322, 818), 8 x 8 m | 4 storeys of pale cream stone #d6c7a2 with cornices; an arched belfry stage (2 openings per side) at Z 20-26 (level with the gun deck); a red-tile pyramid roof to Z 33 | F09/000028171, F10/000014792 |
| GH | **Garrison building (clock gable)** | X 341..377, Y 792..812, long facade facing north onto TT | 3 storeys plus a dormered attic, eave Z 13, ridge Z 21, cream sandstone #cdb48a. Green-framed tall arched windows. Its west end is a gabled pavilion with a round clock oculus facing the basin. Orange tile roof with 5-6 dormers. | F10/000023409, F10/000022947 |
| HT | **half-timbered range** | X 377..387, Y 770..813, along the canal quay, plus 2 more bays east of the bank | 4 storeys, cream plaster with dark timber, many dormers, orange tile | F09/000024922 (right), F09/000026033 |
| BT | **2 rowing boats** | moored in the canal against the floor's east lip, centres (389, 843) and (389, 851), long axis N-S (clear of PE, which starts at Y 857) | each 7 x 1.8 m, dark wood #5a4030, pointed bow, no mast | F09/000028171 |
| L_K | **basin hoist** | down PW's east face, basket stop on the floor at (342, 861); derrick on the Rose top at (338, 868, 50) | An open timber basket platform, 4 x 4 m with a low rail, hung on 4 chains that meet at a hook (F09/000019936); on the wall top a timber A-frame derrick with a big wheel and a counterweight (F09/000019840), beside a small winch hut with a red-tile roof (F11/000026658) | F09/000019840, F09/000019936, F09/000020032, F11/000026658 |
| S1 | **Pyxis talk spot** | Rose top, south edge, just east of the inner-gate bastion, (-120, 866, 50); the inner gate is at X -140 | 2 turntable cannons at X -130 and -110 on the south edge, 3 crate stacks, 1 hut at X -95; the titan heap at the inner-gate foot directly below (G9) | ep10 18:35.4 caption, F10/000026743, F10/000028037, F10/000029703, F10/000026973 |
| S2 | **Pyxis speech spot** | Rose top, north edge, (-20, 874, 50) (g4) | 6 dark-green banners on 8 m poles along the parapet from X -45 to +5; cannons on both edges | F11/000010466, F11/000019523 |
| A | troop square (g4) | open forecourt centre (-20, 935), 90 x 60 m, obelisk fountain | g4 owns it | F11/000010308 |

```
 ASCII top-down, 1 char = 5 m, north up (X 300..415, Y 790..880)
 Y875  ###################################################   Wall Rose (north face at 875; Rose top Z 50; S1 is off-map at X -120)
 Y865  #######################PPPPWWWWWWWWWPPP===grille===#  south face 865. P piers, W wall face, grille = water gate
 Y860  ......GGGGGGGG.......Hh..........xx.........E~~~~~~~   G gun bastion (deck Z 20), C cannon at (318,857)
 Y855  ......GGGCGGGG.......ss......xxXxx.........Bb~~~~~~   h hoist basket, x skeleton footprint, X trio (362,852)
 Y850  ......GGGGGGGG.......ss........ffff........Bb~~~~~~   B boats, ~ canal (X 387..413, water Z -4.2)
 Y845  .....................ss....floor (Z -3.6)..........~   ss west stepped bank (L of the Garrison line)
 Y838  .....................ss.........[PL].............~~   PL plinth 10x10, top Z -0.6
 Y833  ......................=====steps==[PL]==steps=======~   SB 12 steps up to Z 0
 Y821  ...T_K...........----top terrace / quay (Z 0)-------q   q canal west quay
 Y812  ...T_K.............GGGG Garrison building GGGG HHHHH   clock gable at the west end; HHH half-timbered range
 Y792  .....................................................
```

**Orientation of the action.** The gun fires roughly W→E and downward. The skeleton faces west-southwest toward the gun. The Garrison faces north toward the Wall. Armin faces south toward the plinth. Seen from our camera (SSW of the basin, looking NNE): the Wall face rises behind, the gun bastion and tower are on the left, the canal and boats are on the right, and the bank, plinth and Garrison building are in the foreground. This is the mirror of F09/000028171, which looks from the town side toward the Wall with the water on the left.

## 3. Set dressing and materials
- **Basin floor:** square cobbles 0.5 m. The sunlit near (south) part is sandy-pale #b9ae8c; the far part near the Wall is mossy green #5d6b3e (shade) to #8a8f5a (sun). There is grass in the joints and a few 1 m rubble lumps after the blast (F10/000015159). `[EV]` F09/000017054 (pale near half, green far half).
- **Wall face behind the floor:** pale warm grey #bdb5a3. The lower 12 m is damp and darker #6f6a58, with vertical moss and ivy streaks #4d5a32 climbing in blotches. `[EV]` owner ref, F09/000021915. This is the owner's 13:49 QA: "damp darker lower walls and moss streaks".
- **Piers:** lighter ashlar #c4b99c with weathered rounded arrises, and moss at the foot `[EV]` owner ref.
- **Bank, plinth, terrace:** cream ashlar #cdbf9a in large blocks (1.2 x 0.6 m). Step nosings are a darker #8f8670 so the step edges read from the air (owner QA). Moss sits in the joints of the lower 4 steps. The plinth cornice is a slightly lighter band. `[EV]` F10/000022947, F10/000023409.
- **Gun bastion deck:** pale limestone #cfc4a8 with ochre/rust stains under the rails. Rails are dark iron on brown sleepers #4a3427. `[EV]` F10/000014792.
- **Cannon:** barrel about 4.2 m long, dark gunmetal #4a4c4e with steel highlights #9a9a96. It has a thick reinforcing ring at the muzzle, 3 bands on the chase, a breech knob and a hand-wheel elevating screw at the rear. Carriage: a **wooden drum/cradle** of alternating light #d8a870 and dark #a86a3a slats with iron bands #5a5a5a, sitting on a round 3.5 m turntable over crossing rails. `[EV]` F09/000022341, F09/000024436, F09/000030586.
- **Water gate:** a dark iron portcullis grid #2f3236 over a black tunnel. Water #6f9a7c, darker #3f5f5a under the arch. `[EV]` owner ref.
- **Boats:** see BT.
- **Garrison building:** sandstone with pilasters; green #3e6b52 sashes in arched windows; a clock oculus with a white face in the west gable; orange roof #b4532f with dormers and chimneys. **Half-timbered range:** cream plaster #d8cbb0 with dark beams #4a3427. `[EV]` F10/000023409, F09/000024922.
- **Rose top (S1, S2):**
  - Pale limestone #cfc4a8 with ochre staining and cracks `[EV]` F10/000028037, F11/000007976.
  - Two tracks, turntable cannons, plain slatted crates #b08a5a in stacks of 2-6 `[EV]` F10/000028037.
  - Huts with red-tile roofs; hoist huts with cages `[EV]` F11/000026658.
  - At S2, banners: dark green #2f5a3a cloth about 2.5 x 4 m with a pale shield emblem, on 8 m poles `[EV]` F11/000010466.
- **Violet flowers** (P2; invisible from the air): a scatter of #7a4fa8 dots on the floor inside the ribcage `[EV]` F10/000008930.

## 4. Characters and titans
**All humans are true scale (1.65-1.8 m), faceless and toon-shaded, built from asset models.**

| who | count | where (M) | pose / motion | evidence |
|---|---|---|---|---|
| **Eren** | 1 | already on the floor at (362, 852) when the camera arrives | Light olive shirt with a brown harness and no jacket. Seated, then gets up held by Armin, then kneels. At the half-shift he is fused into the skeleton's nape (hidden); he tears himself out as the blanket thins (t 26-29, a tiny figure on the skeleton's back) and climbs down beside the ribs. | F10/000026973, F09/000016910, ep10 05:53.6-06:00.7, F10/000015159 |
| **Mikasa** | 1 | (361, 849), 3 m south of Eren, between him and the plinth | Red scarf, brown jacket. Blades drawn from the start (2 glints at t 11 as she sets her stance), in a crouched guard facing south. | F09/000016910, F09/000017054, ep09 17:28.8-17:32.8 `[EV]` |
| **Armin** | 1 | (364, 853) beside Eren | Blond bob, brown jacket. Kneeling. Then he walks out to (361, 846) (t 31-34), with hands up and then the salute. | F10/000021062, F10/000024684, F10/000024047 |
| **Captain** (Kitz Woerman, "Felman" in these subs) | 1 | centre of the plinth top, (362, 832, -0.6) | Bearded. Raises his right arm (t 13), drops it (t 15). Raises it again (t 38.5); Pyxis catches it (t 42). | F09/000030416, F10/000024684 |
| **Garrison** | 48 | 6 on PL (2 riflemen kneeling at the front corners, the captain, an aide and 2 standing); 10 on SB's west flight and 10 on its east flight (some seated, then standing); 14 along TT (in 2 rows at the plinth's back); 5 on SW (the L) | Orange-tan jackets #c98a4b, white trousers, ODM gear, red-rose emblem. Mix of blades and muskets. They step back up 2-3 steps when the steam hits. | F09/000017054, F09/000024922, F09/000028171 |
| **gun crew** | 4 + 1 | on GB around the turntable | One at the breech, one crouched at the turntable, one standing, one with a long rammer/sponge pole; plus a signaller standing at the pier-top edge who relays the captain's arm | F10/000014792, F09/000022341, F09/000028720 |
| **Pyxis** | 1 (+ Anka, + Gustav) | enters along TT from the west (by T_K) at t 40.5 `[INF]` (the anime only shows him stepping out from among the soldiers, F10/000025379); then onto PL; then down the east flight to the floor with Kitz; then L_K; then S1; then S2 | Bald, white moustache, red sash diagonally over a brown Garrison jacket, hands clasped behind his back when still. Unhurried walk, 1.3 m/s. | F10/000025379, F10/000025499, F10/000029703, F11/000010466 |
| **cadet onlookers** (P2) | 4-6 | on the Garrison building roof ridge, plus 5 on the bastion deck edge | standing (104th uniforms) | F10/000007043, F09/000031440 |
| **troops at A** | about 2,000 | g4's square A | Loose blocks facing south toward the wall. 20-40 figures drift north (would-be deserters), stop and turn back during the speech `[INF]` from ep11 04:46.8 F11/000006876. Fist-raise ripple at the climax. | F11/000010308, F11/000029621 |
| **elite squads + Eren + Mikasa** | about 16 | they gather at the Rose top's south edge (-30..0, 866, 50) | They run along the parapet and leap off south on ODM in a staggered line (t 108), then fly SSE over the roofs toward g8's Boulder Court B0 (290, 262) | F11/000021977, F11/000029803, F11/000029847, F11/000030669 |
| **Pyxis's command post** | Pyxis, Anka, 4-5 officers | Rose top south edge at about (-20, 866, 50), behind a timber railing | stand and watch the squads go; Anka lifts a brass telescope | F11/000030312 |
| **the skeleton** (half-shift) | 1 | footprint X 354..372, Y 848..862 | see below | F09/000031975, owner ref |

**Half-shift skeleton (the asset; one mesh).**
- **Torso only:** it rises out of the floor from about the pelvis. There are no legs; ribs and roots fuse into the cobbles.
- **Size:** the skull top sits at about Z +6.5 above the floor (10 m tall in all); the skull is 2.2 m wide; the ribcage is 6 m wide and 5 m deep.
- **Posture:** hunched forward 30°, facing west-southwest (bearing about 250°, toward the gun). Ribs arch over Eren's spot; Mikasa and Armin crouch under them.
- **Right arm:** humerus wrapped in red muscle, raised and curled across the front as a shield, with the forearm bones and a bony hand ending low at about (354, 851, 2). A blackened scorch patch on the forearm marks the impact.
- **Left arm:** bones lie on the floor along the south side.
- **Materials:**
  - Bone: gold-cream #e6d3a8, shaded #b89d6a; the skull is slightly darker #cdb88c, with deep black eye sockets.
  - Muscle: #9a1f24 with fibre streak highlights #d8463e, on the skull's sides, the jaw hinge, the neck, the trapezius, the shoulders and the upper arm.
- **Growth:** 0.3 s from the floor (t 15.05-15.35), with the black silhouette sweep first.
- **Afterwards:** it steams from the muscle surfaces until the end of our time at the basin. `[EV]` F09/000031975, F10/000007924, F10/000008930, owner ref.

**Titans.** None within about 250 m of the basin during this beat. The owner moved the basin into Trost, so the Garrison has evidently cleared this corner `[INF]`. In the anime the titans pack the Trost-side foot of Wall Rose along a long stretch ("a defensive wall of flesh") `[EV]` ep09 14:00.7 F09/000020157, 14:04.7 F09/000020253. We place about 40 of them (3-10 m) in a loose band along the Rose foot from X -330 to X +100, Y 840..865, and the densest heap, about 12 titans of 3-9 m, at the south foot of the inner gate (X -170..-110), arms raised, one standing on the others `[EV]` F10/000027129, F10/000026743. From our cameras north of the wall (C9-C15) the 50 m wall hides the whole foot strip, so they matter only for C1-C8 (none in frame there either, since they stay west of X +100) and for continuity with g5/g8. Do not move the camera south just to show them. The decoy-corner mass belongs to the decoy group (D).

## 5. FX, lighting, time of day
- **Light:** golden late afternoon. Sun azimuth about 255°, elevation 28° at the basin, dropping to about 12° by the handoff (time-lapse during the C9→C11 walk west and the C11→C12 crossing).
  - The west pier and gun bastion cast long shadows ENE across the floor, a diagonal like F09/000017054. Sky: blue-teal with warm cumulus `[EV]` F09/000024922.
  - By the speech the light is warmer, #ffcf8a. Sunset glow at the deployment `[EV]` F11/000030270.
- **Muzzle flash (t 15.00-15.08):**
  - A yellow-white 4-point star card #fff3b0 → #ffd040, 4 m, lasting 2 frames.
  - A point light (energy spike, 1 frame) that lights the Wall face.
  - Then a grey-brown muzzle puff #b8ad98 of 4-6 m cards that drifts east and fades over 3 s `[EV]` F09/000030553, F09/000030586.
  - The barrel recoils 0.5 m and returns over 1 s.
- **Shell:** a 0.4 m dark ball over 0.35 s (about 140 m/s), with at most a faint 0.1 s motion streak. **No** white line from the gun (today's render has one).
- **Half-shift ignition (t 15.05):** a small yellow lightning flicker #ffd75a (2 forks, 8-10 m tall, 3 frames) at the trio, plus a ring of dust (pale tan #b9ae8c cards, r 8 m) `[EV]` F09/000030923, F09/000030963.
- **Impact (t 15.35):**
  - An orange fireball, core #ffe08a, mid #ffb030, edge #ff7a1a, radius 6-8 m, 0.25 s, at the curled forearm (355, 851, 5).
  - 30-60 spark embers #ffc860 that fall over 1.5 s.
  - A brief black-brown smoke shred #4a4038 that the steam swallows `[EV]` F09/000031044.
- **STEAM ("LOTS"):** cauliflower billows `[EV]` F10/000007570, F10/000007834, F09/000031151, F09/000031440.
  - Colours: sunlit tops #efe2c4 (warm white), body #d9d6c8, shadow side olive-grey #8f907c, deep core #6d6a5c. Golden ember specks drift in the column (F09/000031151).
  - **Burst** (t 15.4-16.6): the steam expands from the skeleton to r 25 m with ease-out. It fills the floor, climbs the Wall face to about Z 35, and rolls over the bank so that the Garrison stands waist-deep (F10/000007570).
  - **Column** (t 16-40): a single pillar about 12 m wide at the base, rising to Z 85-95 and widening to about 30 m at the top. It leans about 10° east (wind) and its top flattens. Seen from the town it rises in front of Wall Rose (F09/000031091, mirrored).
  - **Blanket** (t 16-31): 4-6 m deep over the floor, thinning to patchy wisps by t 31 so that the skeleton reads. After that, 6-10 thin wisps rise from the muscles.
- **Steam from the HQ** (g6's corpses) stays as 6-8 thin columns in the background.
- **Town smoke:** 10-15 thin smoke columns across Trost (g4), dark grey-black closer up, rising nearly vertically (F10/000029703).
- **Green flare: NOT in g7.** g8 fires it at g8 t 7.5 from GF (330, 140, 50) with its own colours (smoke #6fae4f, head #b8ff7a) `[EV]` F11/000030270. Firing it here as well would put two green flares in the take.
- **ODM:** thin dark wire lines (render as 0.12 m emissive-dark cylinders so they hold 1-2 px at 300 m) and white gas puffs (#f2f2f2 cards, 1 m) at each launch.
- **Blood:** none needed in this beat.

## 6. Choreography timeline for OUR one take
t = 0 is g6's handoff (H8). The full version is 116 s; the tight version is at the end.

| t (s) | where | what happens |
|---|---|---|
| 0-7 | transit HQ → basin; the HQ steam stays behind | The sun turns golden. Below, the trio is already on the floor at (362, 852) (anime: Eren wakes there, ep09 11:29-11:45): Eren seated, Armin kneeling beside him, Mikasa standing guard. All 48 Garrison are in place on the bank, plinth, terrace and west flight, some seated on the steps (F09/000016910). The chain-hoist basket hangs empty at the foot of PW. The gun crew turns the turntable 40° to bear on the floor (t 3-6). |
| 7-13 | basin | Eren gets up, held by Armin, then kneels again; Mikasa steps 3 m south between them and the plinth and sets her stance (a small dust puff, blade glints at t 11). Seated soldiers on the flights stand. A ripple of drawn blades runs along the flights (glints). The 2 plinth riflemen kneel and aim. |
| 13-15 | plinth, GB | The captain raises his right arm and holds it (2 s); the signaller on the pier-top edge of GB raises his arm in answer (F09/000028720). |
| **15.00** | gun bastion | The arm drops: **FIRE**. Muzzle flash, light spike on the Wall, smoke puff, recoil. |
| 15.05-15.35 | floor | Lightning flicker and dust ring at the trio. A black arm sweeps up (0.15 s), and the skeleton erupts to full size. The shell flies. |
| **15.35** | forearm | The shell hits the curled forearm: fireball and sparks. HUD caption **"Eren blocks the cannonball"** at t 15.5-18.5 (existing graphics). |
| 15.4-24 | whole basin | The steam bursts, fills the basin and spills over the bank; the column climbs past the Wall top (Z 50) by t 20. The Garrison recoils 2-3 steps up and 4 soldiers on TT scatter back. The gun crew reloads (one figure rams the bore, t 20-23). |
| 24-31 | basin | The blanket thins. The skeleton emerges, read as skull, ribcage arch and curled arm, steaming. Mikasa and Armin are visible under the ribs. At t 26-29 Eren tears himself out of the nape (a tiny figure on the skeleton's back, red fibres snapping) and climbs down beside them (ep10 05:53.6-06:00.7). The Garrison re-forms along the top edge of the bank, blades drawn (ep10 10:02.9). |
| 31-34 | floor → (361, 846) | **Armin walks out alone** (1.2 m/s, 7 m) and raises both hands (t 33). |
| 34-38.5 | (361, 846) | **SALUTE**: right fist to the heart, left hand behind the back, chest out, facing the plinth. He holds it for 4.5 s. HUD tag "Armin". Soldiers on the flights lower their blades slightly (t 36). |
| 38.5-41 | plinth, GB | The captain raises his arm again and the gun crew re-aims (turntable twitch 3°). |
| 40.5-42 | TT west → plinth | **Pyxis** (red sash) with Anka and 2 riflemen walks east along TT from beside T_K `[INF]`. At t 42 he catches the captain's raised arm; the arm comes down slowly by t 43. The riflemen lower their muskets and the gun crew stands back. HUD tag "Pyxis". |
| 43-47 | east flight → floor | Pyxis walks down the east flight to Armin (1.3 m/s), Kitz and 2 riflemen with him (F10/000025499). Eren and Mikasa wait by the ribs (F10/000025999). Pyxis, Anka and the trio walk west across the floor to the L_K basket at (342, 861); Kitz stays on the floor. |
| 47-55 | L_K | **Time-lapse step:** the chain basket rises up PW's face from Z -3.6 to Z 50 (8 s, eased). The camera orbits up and around the basin to the north (section 7). The skeleton keeps steaming. The steam column thins and leans. |
| 55-77 | Rose top, X 338 → -120 | **Wall-top walk west, time-lapse** (the take's motivated transit). The group steps off at the derrick (55-56) and walks west along the south rails past turntable cannons and crate stacks: Pyxis leads, the trio follows and Anka is at the rear. Profile: ease in 56-58, cruise about 24 m/s apparent (walk cycle ×18) 58-75, ease out 75-77; positions about X 266 at t 60, X 25 at t 70, X -120 at t 77. They never teleport. The sun drops toward 15°. North of the wall, square A fills from sparse to about 1,500 troops. |
| 77-82 | S1 (-120, 866, 50), above the inner gate | Real speed. Pyxis stops at the south parapet, hands behind his back, looking SOUTH over Trost (smoke columns, the far outer wall with the outer gate a little left of his line, hills; F10/000029703). Eren sits on the rail beside a cannon (F10/000026973); Mikasa and Armin stand beside him. At t 80 Pyxis and Eren turn and sit on the north parapet, all four facing north (F10/000031399). |
| 82-88 | S1 → S2 | **Time-lapse** (×12). The group crosses the 10 m wall top and walks 100 m east along the north edge to S2. Square A finishes filling (about 2,000). Banners rise on poles at S2. |
| 88-100 | S2 / square A | **SPEECH:** Pyxis on the north parapet facing north, with **Eren standing beside him** (presented to the troops, ep11 07:51-07:59); Anka 2 m behind; Mikasa, Armin and the elite squads further back among the cannons. Normal speed. 20-40 would-be deserters near the back drift north, stop and turn back (t 90-95). Climax at t 97.5: a fist-raise ripple runs across the square and up the packed street behind it, front to back (pose swap, staggered 0.6 s). |
| 100-108 | A → Rose top | **Deployment** (time-lapse ×10). Troops stream to the 3 north-face hoists (cages rising) and ODM up the north face (thin wires, puffs). The Rose top fills and a dense column marches west along it toward the decoy corner D. Cannon crews man every gun. The elite squads, Eren and Mikasa gather at the south edge (-30..0, 866). Pyxis, Anka and officers take post behind a timber railing at (-20, 866) (F11/000030312). Armin stays on the wall top with the Garrison (lore). |
| 108-116 | south edge → Trost roofs | Eren, Mikasa and about 14 elites run along the parapet and **leap off south** on ODM in a staggered line (puffs, wire arcs), then skim the roofs SSE toward g8's Boulder Court B0 (290, 262). Normal speed. Pyxis's group watches. **No flare here:** the green flare is g8's (g8 t 7.5). HANDOFF to the boulder group at t 116. |

**Tight version (about 82 s):** 0-5 transit, 5-10 setup, 10.0 fire, the steam holds to t 17, Armin's salute 22-27, Pyxis 27-31, basket 31-36, time-lapse walk west to S1 36-50, S1 hold 50-53, crossing to S2 53-57, speech 57-67, deployment 67-77, leap 77-82. Do not shorten the fire, impact and steam burst, or the 4 s salute hold. For the owner's pace budget see section 9 ("Duration").

## 7. Sky-observer CAMERA plan
**Rules:**
- Positions and look-ats are on separate arc-length Catmull-Rom/Hermite splines. Lens is interpolated in log space. No roll.
- Heights 86-205 m. Pitch 28-36°, except the handoff key C15 at 25.6° (a wide look into Trost, inside g4's 20-35° rule). The brief closer aerial framings (C5-C7, the salute and Pyxis) are 37-40°, as in g6.
- Lens 30-42 mm. Peak yaw rate is about 12°/s, only in the C7→C9 orbit.
- No chase, no faces, no cuts. A 1.7 m human is never more than about 26 px tall at 1080p (not over-zoomed).

| key | t | position (X, Y, Z) | look-at | lens | pitch↓ | slant / frame width | move to this key | notes |
|---|---|---|---|---|---|---|---|---|
| C0 | 0 | (220, 650, 130) | (345, 810, 0) | 32 | 32.6° | 241 / 271 m | (entry) | **= g6 H8**, velocity (25, 8, 0) m/s, dlnlens 0 |
| C1 | 7 | (262, 712, 112) | (358, 846, 0) | 34 | 34.2° | 199 / 211 m | 77 m, 11 m/s, easing | basin, Wall face, GB and T_K on the left, canal on the right |
| C2 | 12 | (282, 738, 96) | (361, 849, -2) | 38 | 35.7° | 168 / 159 m | 36 m, 7 m/s, ease-in | standoff framing (mirror of F09/000028171): the trio at centre, Garrison L, plinth, gun deck at the left edge |
| C3 | 15 | (283, 740, 96) | (361, 850, 4) | 38 | 34.3° | 163 / 155 m | almost static | **FIRE at 15.0**. The look-at rises 6 m so the skeleton fits. The camera does NOT push in. |
| C4 | 24 | (266, 720, 122) | (363, 855, 24) | 32 | 30.5° | 193 / 217 m | 37 m, 4 m/s, ease-out start | pull back and up for the steam burst and column (the column exits the frame top above Z 80, which is fine) |
| C5 | 31 | (290, 758, 88) | (362, 848, -2) | 42 | 38.0° | 146 / 125 m | 56 m, 8 m/s | closer aerial (owner exception) as the skeleton emerges from the thinning steam |
| C6 | 40 | (296, 752, 90) | (360, 842, -1) | 40 | 39.5° | 143 / 129 m | 1 m/s drift | **salute hold** (Armin 25 px) with the plinth below him in frame; Pyxis enters from frame left on TT |
| C7 | 47 | (330, 742, 105) | (350, 852, 10) | 38 | 40.4° | 147 / 139 m | 5.5 m/s, yaw -25° | the group crosses the floor to the basket; the orbit starts |
| C8 | 53 | (452, 800, 132) | (343, 862, 40) | 36 | 36.3° | 156 / 156 m | 138 m, 23 m/s, yaw -71° (11.8°/s) | east of the canal, rising with the basket up the pier face |
| C9 | 60 | (422, 962, 150) | (275, 867, 48) | 36 | 30.2° | 203 / 203 m | 166 m, 24 m/s, yaw -63° (9°/s) | crosses the wall line at X ≈ 437, Z ≈ 141 (91 m clear of the top). The basket has arrived; the walk west is under way (group at about X 266, left of centre) |
| C10 | 70 | (100, 1050, 155) | (25, 867, 45) | 34 | 29.1° | 226 / 240 m | 334 m, 33 m/s (the beat's fastest move, motivated by the time-lapse walk; peak about 38 m/s), yaw -35° | north of the wall looking SSW, pacing the group (at about X 25) along the rails; square A filling in the lower left |
| C11 | 77 | (-20, 1042, 145) | (-118, 846, 28) | 34 | 28.1° | 249 / 263 m | 121 m, 17 m/s, ease-in to the hold | S1 above the inner gate: Pyxis from behind (13 px) at the south parapet, Trost and the far outer wall beyond (the F10/000029703 composition from the air) |
| C11b | 82 | (-14, 1044, 147) | (-118, 846, 28) | 34 | 28.0° | 252 / 267 m | 1.3 m/s drift | S1 hold (5 s); they turn and sit on the north parapet facing us |
| C12 | 88 | (15, 1090, 148) | (-20, 905, 28) | 33 | 32.5° | 223 / 244 m | 54 m, 9 m/s, eased both ends, yaw -17° | the time-lapse crossing to S2; A fills to 2,000; banners rise |
| C13 | 100 | (30, 1100, 142) | (-20, 900, 32) | 36 | 28.1° | 234 / 234 m | 19 m, 1.6 m/s slow push | **speech**: square A in the foreground and middle, the Wall face behind it, Pyxis with Eren beside him and the banners on the crest, smoke columns from Trost rising beyond the Wall (F10/000026877) |
| C14 | 108 | (-20, 1000, 190) | (-35, 730, 5) | 32 | 34.4° | 328 / 369 m | 122 m, 15 m/s, rising | rises over the crest: the packed Rose top and the westward column below, Trost opens up beyond; the squads leap |
| C15 | 116 | (-40, 960, 205) | (40, 540, 0) | 30 | 25.6° | 474 / 569 m | 47 m, 6 m/s | ODM arcs over the roofs heading SSE toward B0. **HANDOFF** to the boulder group: velocity about (-2.5, -5, +2) m/s, lens 30, dlnlens 0. The line of sight over the Wall clears it (Z 161 at Y 870). **g8's K0 must equal this key** (today g8 K0 is g4's old anchor (-20, 1080, 130); see the critical issues). |

**Notes:**
- Validate the C7→C9 orbit in the viewport. It is the beat's only fast yaw (a 147° half-orbit in 13 s). If it feels busy, stretch C7→C9 by 3 s.
- During C9→C11, keep the group in the left-centre of the frame. Their apparent 24 m/s cruise is close to the camera's look-at speed (about 25 m/s), so they stay roughly in place on screen while the wall top and square A stream past. This is the motivated time-lapse. If 33 m/s feels brisk at 150 m, add 3 s to t 60-77 and take them from the S1 hold (keep at least 4 s of hold).

## 8. Current render vs anime: gap list
Checked: trost_p2_sheet.jpg row 4 (basin, 6 frames) and row 5 cells 1 and 4-6 (basin exit, Rose top/Pyxis). Owner refs: trost_cannon_canal_ref.png, trost_armin_salute_steps_ref.png, eren_halfshift_skeleton_ref.png. Code: trost.py puts the basin at set (494..543, -225..-175) = M (494..543, 645..695), 170 m south of the Wall, with its floor at street level and 6 m terraces; render_trost_action.py uses cannon_square at set (22, -40).

| # | P | what is wrong now | change to |
|---|---|---|---|
| 1 | P0 | **The basin is detached from Wall Rose.** It is a free-standing 50 x 50 m court mid-town; nothing rises behind its floor. | Move it to the Wall foot (KF X 340..385, Y 833..865). The Rose face is its back wall, with the two battered piers PW/PE and the barred water gate WG. Floor Z -3.6 (sunken), not at street level. |
| 2 | P0 | **The skeleton** is an upright full-height capsule: a white ball head on a red-and-white striped tube, standing in the middle of the floor. | A torso-only, hunched skeleton rising from the floor: skull with red muscle strips, gold-cream ribcage arched over the trio, right arm curled across as a shield, left arm bones on the floor, about 10 m tall (section 4). |
| 3 | P0 | **Steam** is a handful of small white puffs plus a thin white streak. | A massive cauliflower burst filling the basin and spilling over the bank, a 90 m column, and a lingering blanket (section 5). The owner said "LOTS". |
| 4 | P0 | **No cannon is visible**, and the "shot" is a straight white line from the north stepped terrace. | The gun on its turntable on the 20 m bastion GB, west of the floor, beside tower T_K: flash, puff, recoil, shell, orange fireball on the forearm. |
| 5 | P0 | **No Garrison ring:** one tiny figure on the floor, and the steps are empty. | 48 Garrison on the plinth, both flights, the terrace and the west bank (the L), the 3 gun crew, and the trio at (362, 852). |
| 6 | P0 | **Stepped banks** are thin dark-grey ribbed strips on the north and south sides with no plinth; the stone is flat grey. | One cream ashlar bank on the town side: 12 steps with dark nosings and a 10 x 10 m plinth (3 m face, cornice, coping) between the two flights; the short west flight; moss in the joints (owner QA 13:49). |
| 7 | P0 | **Armin's salute** cannot be read: no separation, no plinth, no closer framing. | Armin alone 8 m in front of the plinth, fist on heart, 4.5 s hold at C6 (25 px) with a HUD tag. |
| 8 | P1 | **Canal and water:** a saturated blue band along the whole east side, a white slab at its north end, one boat in mid-canal. | g4 green water, a darker reach under the portcullis arch, the canal entering WG at the Wall, 2 rowing boats moored at the floor's east lip, water 0.6 m below the floor. |
| 9 | P1 | **No surrounding architecture.** Generic detached houses come right up to the basin. | Tower T_K (red pyramid roof), the clock-gable Garrison building GH and the half-timbered range HT along the quay, as in the owner's salute ref. |
| 10 | P1 | **Floor** is a uniform grey-green plane. | A pale sandy near half and a mossy green far half, cobble texture, rubble lumps after the blast, damp darker Wall base with moss streaks. |
| 11 | P1 | **Lighting** is flat grey-blue. | Golden late afternoon from about 255°, with long pier and bastion shadows diagonally across the floor; warmer by the speech; sunset at the leap. |
| 12 | P1 | **Rose top / Pyxis** (row 5 cells 4-6): a plain grey concrete wall with blocky caps and 3 small windows. Three tiny figures stand on a cap; there are no rails, cannons, crates, huts or banners; the north side is empty green. | Limestone top with 2 tracks, turntable cannons every 20 m on the S1/S2 stretches, crates, a hoist hut and cage, dark-green banners at S2. Pyxis with a red sash at the edge. Square A with about 2,000 troops and the obelisk fountain (g4). |
| 13 | P1 | **No wall-top walk and no deployment.** | The L_K chain basket, the time-lapse walk west to S1 above the inner gate and the crossing to S2 per section 6; troops up the hoists and west to D; the ODM leap-off SSE. (No green flare here: g8 owns it.) |
| 14 | P2 | Missing details | violet flowers inside the ribs; cadet onlookers on the Garrison roof; pigeons on the Rose crest (F10/000005610); the titan heap at the inner-gate foot and the wall-foot titan band (F10/000027129, F09/000020157); gun reload action; the pier-top signaller |

## 9. Owner-rule overrides (intentional differences from the anime)
- **Basin inside Trost (owner, HANDOFF 09:37).** The anime basin is north of Wall Rose (section 1 headline). We mirror it N-S onto Rose's Trost face at the canal water gate, keeping E/W, so the steam column now rises in front of the Wall when seen from Trost.
  - Consequence: in lore the area is safe behind the wall. We keep it plausible by having no titans within about 250 m during the beat.
  - **Owner check:** if the owner prefers lore accuracy here, the same block can be built on Rose's north face at X 340..385, Y 875..907 (it needs about 4 buildings north of Rose, which breaks the "only Trost and Shiganshina have buildings" rule).
- **Camera.** Every anime shot in this sequence is a close-up or ground-level. We show it all from 86-205 m. The salute and Pyxis's arrival are the brief closer aerial framings (25 px humans). There are no face shots, and the anime's red-tinted flash-insert sequence (ep10 17:19-17:30) is not used.
- **The anime cuts between places; we use one take.** The basin, the talk at the inner gate (S1) and the speech (S2) are linked by a time-lapse walk, not a cut. The group visibly walks the 458 m from the basin hoist to S1 at time-lapse speed, then 100 m on to S2. Owner check: this long walk exists only because the owner's basin sits at the canal (X 340-385) while the anime's talk is at the inner gate (X -140). The anime itself suggests the basin lies near the inner gate: the steam column rises just right of the inner gate seen from Trost (F09/000031091). Moving the basin and canal water gate west is a g4 decision; it is not proposed here.
- **Duration (OWNER DECISION).** The owner asked for this stretch to be quick: "quick cut to the cannon being fired → Eren's partial titan blocks the shot → Armin in the salute giving a fast speech" (HANDOFF 05:58, item 4). The EP1 budget is 8-10 min with Trost ≈ 2:45 in all (HANDOFF 15:51 and Scope). This beat is 116 s (82 s tight); with g6 (74 s) and g8 (136 s) Trost far exceeds 2:45. A pace version of about 45 s keeps every must-have: 0-3 transit, 3.0 fire, 3.35 impact, steam to 8, salute 9-13 (4 s hold), Pyxis 13-16, basket and time-lapse walk to S1 16-27, S1 3 s, crossing 30-32, speech 32-38 with the fist ripple, deployment and leap 38-45. Its camera would need re-keying (the same key positions with times scaled about 0.4, the fastest move then about 80 m/s, so the C9-C11 transit should be raised to about 250 m).
- **Time compression.** The basket climb (8 s), the walk west, the crossing to S2 and the deployment run at time-lapse speed. The fire-to-impact sequence and the salute run at true speed.
- **Pyxis's troop square** stays north of the Wall (g4 default (a): an open forecourt, no houses). If the owner picks g4 option (c) (square inside Trost), move S2 to the south edge at (-20, 866, 50) facing south, and drop the C9 crossing.
- **Green flare.** The anime shows it right after the leap (ep11 21:02.5). It is staged once, by g8 (g8 t 7.5), so g7 ends on the leap.
- **Eren's escape plan** (ep10: climb the wall and go to the basement) and the dialogue inside the ribs are not staged. They are dialogue only.
- **Skeleton detail.** The anime shows vines, roots and flowers inside it. We keep only the bone and muscle read from the air; the flowers are P2.

## 10. Must-have lore details checklist
- [ ] The floor is sunken at the very foot of the Wall, with the Wall face plus 2 massive battered piers as its back wall (F09/000017054, owner ref).
- [ ] Canal along one side of the floor, entering a barred iron water gate in the Wall; 2 rowing boats moored at the floor edge (F09/000028171, owner ref).
- [ ] Mossy green floor in the shade, pale cobbles in the sun, a damp moss-streaked Wall base (F09/000017054, F09/000021915).
- [ ] A 12-step bank on the town side with a square plinth between two flights; the Garrison on the steps, plinth and quay in an L (F10/000022947, F09/000024922, F09/000028171).
- [ ] 2 riflemen kneeling at the plinth's front edge, the bearded captain signalling with a raised arm (F10/000024684, F09/000030416).
- [ ] The cannon on the top of a tall pier-bastion against the Wall, on a round turntable with a rail spur and a slatted wooden drum carriage, a signaller at its edge, and a pale bell tower with a red pyramid roof next to it (F09/000022341, F10/000014792, F09/000028171, F09/000028720).
- [ ] The trio is already on the floor when the scene opens; the 104th's chain-hung hoist basket from the Rose top (F09/000016910, F09/000019936).
- [ ] The clock-gable sandstone Garrison building and a half-timbered dormered range behind the bank (F10/000023409, F09/000024922).
- [ ] Order: captain's arm and the pier-top signaller, then flash and puff, then the bite spark, then the black arm sweep, then the red-muscle arm, then the orange fireball (F09/000030553 → F09/000030923 → F09/000030990 → F09/000031022 → F09/000031044).
- [ ] The skeleton: torso only, skull with red muscle strips, gold-cream ribs over the trio, a muscled shielding arm (F09/000031975, owner ref).
- [ ] Huge cauliflower steam swallowing the basin and the Garrison to the waist, with one tall column visible from across the district (F10/000007570, F09/000031091).
- [ ] Armin alone in front of the plinth, hands up, then the fist-on-heart salute (F10/000021062, F10/000024047).
- [ ] The captain raises his arm again; Pyxis (bald, red sash) catches it and walks down to the trio (F10/000025331, F10/000025379, F10/000025499).
- [ ] The wall-top walk along the rails past turntable cannons and crates to the Rose top above the INNER GATE (titans heaped at its foot); Pyxis looks south over Trost, hands behind his back; then they sit facing north (ep10 18:35.4 caption, F10/000028037, F10/000029703, F10/000031399).
- [ ] The speech from the wall-top edge with dark-green banners and cannons, EREN standing beside Pyxis, to a packed square with an obelisk fountain and a packed street below, north of the Wall (F11/000010466, ep11 07:51.3, F11/000010308, F11/000019523, F11/000029621).
- [ ] Deployment: the wall top packed with soldiers, hoist huts with cages, ODM up the face; titans pressed at the wall foot with arms raised; the squads run along the parapet and leap off over the roofs; Pyxis and Anka (telescope) watch (F11/000026658, F11/000026754, F11/000029803, F11/000029847, F11/000030312).
- [ ] The green flare at sunset is g8's (F11/000030270); it is not fired in g7.

## Eevee / GTX 1060 build notes
- **Basin set:** about 40k tris in one modular mesh: the floor, 2 pier meshes, the bank with plinth, the bastion and the water-gate arch.
  - Use a trim sheet: cobble, ashlar, step-nosing strip and moss decal. Do the damp gradient and moss streaks with vertex colour and one tiling mask. No sculpting.
  - The portcullis is one instanced bar mesh.
- **Skeleton:** one mesh of 25-40k tris (ribs as bevelled curves converted to mesh; the skull from an asset skull scaled ×9; the muscle as a shell with a fibre-stripe texture and toon ramp). It grows with a scale/shape key over 0.3 s. Six to ten steam wisp cards are parented to the muscles.
- **Steam:** cards only by default.
  - The burst: 60-90 camera-facing cards (from a 4x4 cauliflower atlas at 2k), spawned with Geometry Nodes at t 15.4, scaling from 3 to 18 m, rising 2-4 m/s, fading out.
  - The column: 25-35 cards stacked along a bent curve with scrolling noise UVs.
  - The blanket: 12-20 large 20-30 m cards near the floor.
  - Shading: toon ramp plus 0.15 emission so the shadow side never goes black. Dithered alpha (Eevee Next) to avoid sort popping. Keep the overdraw at 40 layers or fewer per pixel.
  - Optional: one low-res volume box (50 x 40 x 30 m, tile size 8, 32 samples) for the base. Default it OFF; test frame time at C3/C4 first.
- **Fire:** flash = emissive star card plus a point light keyed for 1 frame. Fireball = 8-frame emissive flipbook on 3 cards. Sparks = GN points with emission and gravity.
- **Crowds:**
  - The 48 Garrison and the hero figures use asset LODs (hero LOD at 3k tris or less within 200 m).
  - The about 2,000 at A and the about 600 on the Rose top use instanced 300-tri LODs with 6 poses: stand, seated, kneel-aim, blade-ready, fist-raised, walk. Give each instance a random time offset; the fist ripple is a per-instance pose swap driven by distance from the front.
  - The time-lapse crowd flow uses GN points along curves (wall-top path to D, hoist queues) with instanced figures.
- **ODM:** wires are 0.12 m dark emissive cylinders that stretch 0.4 s per launch; gas puffs are cards.
- **Flare:** none in g7 (g8 builds it).
- **Wall-foot titans (G9):** the wall hides them from every g7 key, so exclude that collection from rendering for t 0-116 (it stays in the scene for g5/g8 continuity). This saves the Alembic cache reads.
- **Chain basket:** 4 chain curves (array of a 2-link mesh along a curve) plus a 4 x 4 m plank platform, parented to one empty animated up the pier.
- **Shadows:** the basin is a small area. Give the sun a 0.05 m resolution limit only while the camera is within 250 m (C1-C11), then relax it to 0.1 m for C12-C15. Keep the shadow pool at 512 MB or less.

## 11. Verification log (adversarial review, 2026-10-26)
I opened every cited frame (2x montages at 640x360) and the owner refs. I also read the ep09 sheets 16-27, ep10 sheets 09, 14 and 20-27, and ep11 sheets 07-10 and 24-25, and checked the plan against BRIEF.md, HANDOFF.md (05:58 storyline, 09:37, 13:49, 15:29, 15:51), g4, g6 (H8) and g8 (K0, flare, B0). Changes, in spec order:
1. **Headline and item 11:** the wall-top talk is at the **inner gate**, not above the basin. Evidence: the caption "Trost District Inner Gate" (ep10 18:35.4 F10/000026743) opens the scene, and in F10/000029703 the outer gate stands slightly left (east) of Pyxis's southward view, which fits X ≈ -120, not X 302. **S1 moves from (302, 866, 50) to (-120, 866, 50).** The 2a G4/G7 stretches, the 2b S1 row, the timeline 55-88 and the camera keys C9-C12 are rewritten to match. Added F09/000031091's "just east of the inner gate" note.
2. **Item 1:** the trio is NOT "brought in down a stair". Eren wakes on the floor (ep09 11:29-11:44) and is already surrounded at 11:45.3; Mikasa's blades are drawn from the start. Timeline 0-13: the invented escort is removed, so all 48 Garrison and the trio are in place when the camera arrives.
3. **Item 1 / G5 / L_K:** new evidence for the basin hoist. The 104th are lowered in an open basket on 4 chains facing the plinth (ep09 13:51.5 F09/000019936, 13:55.5 F09/000020032), worked from a timber A-frame derrick with a wheel (13:47.5 F09/000019840). L_K becomes a chain basket plus derrick; it was a timber truss cage with no basin evidence.
4. **Item 2 / GB:** the gun deck reads from below as the top of a tall pier projecting from the Wall face, with a signaller at its edge (ep09 19:57.9 F09/000028720, 21:26.3 F09/000030840). GB is made compact (X 308..338, Y 849..865) and built in one with PW. The gun crew is 4, not 3 (F10/000014792), plus the signaller. Added the signaller to the timeline (t 13-15) and the checklist.
5. **Item 3:** Mikasa's blades are `[EV]` from 11:45.3 (they were `[LOG]` at 17:32.8). The dust haze on the floor in F09/000024922 is her stance (17:28.8).
6. **Item 4:** the captain is bearded and is "Captain Felman" in these subs (ep10 17:13.5); he first raises his arm at 19:56.9.
7. **Item 5:** noted the 15 s flashback between the flash (21:14.3) and the bite (21:29.7); the order flash → bite → arm → impact is unchanged.
8. **Item 6:** F09/000031440 shows five **104th cadets** on a high paved ledge, not "Garrison soldiers on the paved edge". Added Kitz in the steam (F09/000031370) and the cadets to the onlooker row.
9. **Item 7 and the Eren row:** Eren tears himself out of the nape at ep10 05:53-06:00, BEFORE Armin's walk. The old "reappears at t 44" is now t 26-29. Added the Garrison line re-forming on the bank (ep10 10:02.9) and Armin's "at least another 20 seconds" reload (ep10 10:32.3), which matches our 23.5 s gap to the second fire order.
10. **Item 8 / PL:** the plinth top is flat to its edge with **no coping or parapet** (F10/000024684). The riflemen kneel at the front corners. The band under the rim has a wavy relief (owner salute ref).
11. **Item 10:** Pyxis's entry along TT is now `[INF]` (the anime only shows him stepping out of the ranks, F10/000025379). Kitz walks down to the floor with him (F10/000025499, sheet_23).
12. **Item 11:** F10/000031399 does not show "the trio walking away". Pyxis and Eren sit on the north parapet and all four look NORTH over the Rose interior. Added Kitz looking up from the wall foot (19:04-19:13) and the later talk (ep11 05:40-06:47).
13. **Item 12:** in F11/000010466 the figure beside Pyxis is **Eren**, not an aide. Pyxis presents him to the troops (ep11 07:51.3-07:59.4). The speech staging (timeline 88-100, C13 note, checklist) now puts Eren beside Pyxis. Added the troops massing at the inner gate's north face (ep11 03:58.4, 04:02.4) and the packed street behind the square (F11/000029621).
14. **Item 13 and section 5:** the **green flare is removed from g7**. g8 already fires it at g8 t 7.5 from GF (330, 140, 50), so keeping it here would put two flares in the take. Added the leap run-up (F11/000029803), the flight over Trost (F11/000030669) and Pyxis/Anka watching with a telescope (F11/000030312).
15. **Leap direction:** "SSW toward B0 (contested)" is now **SSE toward g8's B0 (290, 262)**. C15's look-at moves from (-80, 520, 0) to (40, 540, 0) (pitch 25.6°, line of sight clears the wall at Z 161).
16. **2b BT:** the boats were placed ON the floor (X 384 < the floor's east edge at 385), and one overlapped the east pier PE. They are now in the water at (389, 843) and (389, 851).
17. **2b SB:** the bank's east flight runs down into the canal water (ep09 18:05.8 F09/000026033).
18. **G9 / Titans:** the anime packs titans along the Trost-side foot of Wall Rose ("a defensive wall of flesh", ep09 14:00.7 F09/000020157), not only at the inner gate. Added a band from X -330 to +100, the densest heap at the inner gate, and the basin stretch kept clear. Geometry check: the 50 m wall hides the whole foot strip from every g7 key north of the wall, so the band is not rendered in g7 (build note).
19. **G10:** g4 itself is inconsistent: A is centred at X -20 but described as "just north of the inner gate" (X -140). Flagged; S2 stays at g4's (-20, 874).
20. **Timeline 55-116 and camera C9-C15 (one take re-checked):** the walk is basket → time-lapse walk west 458 m (t 55-77, cruise about 24 m/s apparent) → S1 hold (77-82) → crossing to S2 (82-88) → the speech and deployment, unchanged. New keys: C9 look-at (275, 867, 48); C10 (100, 1050, 155); C11 (-20, 1042, 145); a new C11b hold; C12 (15, 1090, 148). Every pitch is 28-36° except C15. The fastest move is C9→C10 at 33 m/s (motivated by the time-lapse). Yaw is ≤ 9°/s outside the C7→C9 orbit, and humans are 13-14 px at S1/S2. C0 = g6 H8 is unchanged. The tight version is updated.
21. **Section 9:** added the Duration owner decision (HANDOFF 05:58 "quick cut… fast speech", and the 15:51 8-10 min / Trost ≈ 2:45 budget) with a 45 s pace outline, and an owner check on the basin-to-inner-gate distance.
22. **Build notes:** removed the flare; added the chain basket and the hidden wall-foot titans (excluded from rendering in g7).
23. **Checked and unchanged:** the north-of-Rose headline and the mirror override; the basin floor, piers and water gate (owner ref = F09/000017054/21915); the Garrison L and the tower at the floor's SW corner (F09/000028171); the cannon form (F09/000022341, F09/000024436, F09/000030586); the half-shift order and skeleton (F09/000030923-31044, 31975); steam (F10/000007570, 7834); flowers (F10/000008930, 25999); Armin's walk and salute (F10/000021062, 24684, 22947, 24047); the red-tinted catch (F10/000025331); the titan heap at the inner gate (F10/000027129); the wall-top tracks, crates and cannons (F10/000028037, 28633, F11/000020615, 21977, 24038); the deployment (F11/000026658, 26754, 29847); the caption "Eren blocks the cannonball"; faceless true-scale humans; no close-ups or cuts; the C0-C8 keys.
