# EP1 "Attack on Titan Season 1, through Eren's eyes": terrain and camera plan

Target length is 13-15 min at 30 fps. The video is one continuous drone flight. Between sets, the camera climbs to the overview map and then dives into the next place, so there are no hard cuts.

The HUD shows the place top-left, "Year N · Eren, age N" top-right, and a title plus a one-line caption at the bottom (Ditty / Pirata One).

Characters are faceless and seen from a distance. Titans are the stars.

Source for every beat: `ep1_canon_events.json` (50 chapters, verified on the fandom wiki).

## 1. Sets to build (all in the same Blender style)

| Set | Scale | What changes over time | Used in chapters |
|---|---|---|---|
| A. Island map (three rings) | compressed, radii Sina 250 : Rose 380 : Maria 480 | Maria belt goes from green and farmed (845) to grey with titan dots (after 845); route lines and flares drawn on it | 1, 9, 12, 26, 36-37, 45 |
| B. Shiganshina + Wall Maria + hill tree | 1:1 (U district 760 m wide, 1080 m long) | 845 intact → outer gate kicked in, blocks thrown, fires, smoke → inner gate burst, titans spill north → night: burning town | 2-9 |
| C. Ackerman cabin forest | small | dusk cabins (844 flashback) | 1 |
| D. Wall Rose south: refugee landing, storehouses, new fields, training camp | 1:1 small sets | 845 refugees → 846 march out → 847-850 seasons cycling at the camp (snow, spring) | 10-15 |
| E. Trost (Wall Rose outcrop, south) | 1:1, same build as Shiganshina | 850 intact → 8 m hole in the outer gate → titans in the streets, supply HQ, harpoon nets at the north gate → boulder plugs the hole → day 1-2 cleanup and pyre smoke | 16-30 |
| F. Old Survey Corps castle + research stockade | small | horses arrive; Sawney and Beane steam in restraints; dry-well field | 31-35 |
| G. Karanes (east of Rose) + Maria-belt plains + Forest of Giant Trees (80 m+ trees) | 1:1 town, compressed plains | formation crescent with coloured smoke; Female's horde; trap cables; retreat | 36-44 |
| H. Stohess (east of Sina) | 1:1 rich town, church spires, tunnels | Female vs Attack trench of rubble, collapsed church, the wall climb, crystal, the face in Wall Sina | 46-50 |

## 2. Camera flight (EP1 timing)

| # | Time | Chapter(s) | Camera move | Terrain / event state |
|---|---|---|---|---|
| 1 | 0:00-0:12 | title | Very high over the island map, slow push toward Wall Maria's south edge | map, 845 colours |
| 2 | 0:12-0:25 | 1 Red Scarf | Dive to the dusk forest cabins, short orbit | 844 dusk |
| 3 | 0:25-0:55 | 2 Long Dream | **Opening as the user asked:** sweep high over Shiganshina to show the whole U map, then glide north over the inner wall and drop to the flowered hill. End on the exact framing of the anime still (tree left, wall behind, low camera). Eren lies, sits up and stands; Mikasa waits. | 845 morning, intact |
| 4 | 0:55-1:20 | 3 Scouts Return | Lift over the wall to the outer gate as it rises; track the green-cloak column north up the main street | bells, crowd |
| 5 | 1:20-1:45 | 4-5 Promise, River | Low flight along the canal with golden light; pass the Yeager house block | late afternoon |
| 6 | 1:45-2:30 | 6 Colossal | Hold looking south over the town at the outer wall: steam, then the Colossal's head rises over the wall (thumbnail shot), the hand grips the top, the kick, blocks arc into the town | gate gone, roof hits |
| 7 | 2:30-3:00 | 7 Mother | Push to the Yeager block: the collapsed house, the Smiling Titan walking in | titans enter |
| 8 | 3:00-3:30 | 8 Armored | Swing north to the inner gate: crowded ferries, cannon smoke, the Armored charges and the gate bursts | inner gate gone |
| 9 | 3:30-4:00 | 9 Maria Lost | Big pull-up at night over the burning town, then follow the river north to the lights of Wall Rose; titan dots spread over the farmland | Maria belt turns grey on the map |
| 10 | 4:00-4:40 | 10-12 | Forest lantern, then the storehouses, then the 846 march out of a Rose gate (high pull-out) | 845-846 |
| 11 | 4:40-5:20 | 13-15 | Training camp seasons timelapse (snow/spring), ODM cut-out course, graduation torches | 847 → 850 |
| 12 | 5:20-8:10 | 16-30 Trost | Same moves as Shiganshina: Colossal on Trost's wall, cannon rail sweep, titans in the streets, the Attack Titan, the HQ, the half-skeleton, Pyxis, the boulder carry and the plug | all event states keyed by frame |
| 13 | 8:10-9:00 | 31-35 | Courthouse at night, castle HQ, stockade, dry well | 850 |
| 14 | 9:00-11:45 | 36-44 | Karanes gate east, very high shot of the formation with smoke relays, Female sprint, course bend on the map, dive into the giant-tree forest, trap, scream, Levi | forest damage accumulates |
| 15 | 11:45-14:00 | 45-50 | Map route to Stohess, the Stohess fight, Wall Sina climb, crystal, slow push-in to the Titan face in the wall. End frame. | rubble trench |

Moves follow the benchmark: 10-20 s per drone move with slow ease-in and ease-out. Every set change goes through the overview map.

## 3. Titans and placement

- **Outside the walls (845 morning):** 8-12 pure titans wandering south of Shiganshina in the fields and forest edges, 3-15 m, each with the looping walk action at random offsets. None inside the walls before the kick.
- **Colossal (60 m):** stands outside the south outer gate. Its head is about 10 m above the 50 m wall, its hand on the wall top and steam all around. After the kick it vanishes in steam over about 3 s.
- **Smiling Titan:** enters through the broken outer gate and walks to the Yeager house.
- **Armored (15 m):** starts at the outer breach, runs the main avenue north and bursts the inner gate.
- **Pure titans pouring in (845):** 20-30 through the outer gate along the main avenue and the canal road, then through the inner gate into the farmland at dusk.
- **Trost (850):** the Colossal again; 30+ pure titans; Abnormals; the 4 m and 7 m captives later; the Attack Titan and the boulder.
- **Forest (850):** the Female plus a pack of pure titans converging from all sides.

Designs are being made by separate design passes: colossal.py, pure_titans.py and shifters.py. Each is checked against anime stills with side-by-side sheets.

## 4. Thumbnail shots (stills from the scenes, no final render)

1. The Colossal's head and hand over Shiganshina's south wall, looking into the town (main thumbnail).
2. High overview of the U-shaped Shiganshina in 845 with the hill tree in the foreground.
3. The Armored Titan bursting through the inner gate, with titans spilling into the farmland.
4. Trost with the boulder-carrying Attack Titan, or the Colossal on Trost's wall with the cannon rail.

## 5. Open items

- The tree's distance from the wall: the anime still suggests about 300-400 m; to be set when the scene is assembled.
- Which ferry route and landing to show (the river runs north toward Trost; the landing site is not stated in canon).
- Locations for Karanes and the forest are inferences (the forest about 20-30 km east of Karanes); label them loosely.

## 6. MUST-HAVE key scenes (user 10/24 04:27 UTC)
The video follows the anime, so these emotional and highlight beats are required. Each is shown from the sky at a moderate height and angle (no close-ups): the action is readable, the characters are faceless and recognisable by hair, outfit and colour. A beat can be a brief 4-8 s hover before the flight moves on. Canon chapter numbers refer to ep1_canon_events.json.

| # | Beat | Ch. | Sky-view staging | Readability cues |
|---|---|---|---|---|
| K1 | Carla eaten by the Smiling (Dina) Titan; Eren carried off by Hannes, reaching back ("Yamero!") | 7 | Hover above the Yeager street at 25-35 m. The collapsed house is centre frame. The Smiling Titan lifts Carla out of the rubble. Hannes runs off with both kids on his shoulders, Eren's arm stretched back toward the house. | The Smiling Titan's grin and long hair; Carla's skirt; Eren's red coat and Mikasa's red scarf on Hannes's shoulders; the house still burning |
| K2 | Armored Titan bursts the inner gate; ferries leave | 8 | Already in the plan (thumbnail T3) | |
| K3 | Erwin's "Dedicate your hearts!" (Shinzou wo sasageyo) | 34 | Night torch-lit plaza at 15-20 m: Erwin on the stage, cadets below; when the salute lands, every cadet's right fist hits the chest at once. | Erwin's blond side-parted hair, Survey Corps jacket with the Wings of Freedom, green cloak; torches |
| K4 | Eren swallowed, then the Attack Titan emerges and kills Titans | 19-22 | Rooftop height: the rogue 15 m Titan in the market street, steam and the first roar | Long dark hair, lean body, ears pointed |
| K5 | Armin's supply-HQ plan: the lift drops, the cadets shoot the Titans' eyes, others drop from the ceiling and cut the napes | 23 | Cutaway: the HQ roof lifted off, or a high window view looking down into the hall. All 7 Titans are blinded at once, with muzzle flashes in a ring, then 7 cadets drop from the beams at the same moment. | A circle of gun flashes; synchronised drops |
| K6 | Garrison cannon fires at Eren, Mikasa and Armin; Eren half-transforms (the skeleton shield) | 24 | Wall-top cannon in the foreground, the shot arcs, impact smoke, then the steaming ribcage dome protects the three | Smoke puff, the dome of steaming bones |
| K7 | Eren lifts the boulder and seals Trost's gate; the escort squads hold off Titans | 27-29 | High orbit: the boulder carry down the street, green smoke signals, soldiers dying on the rooftops around him, the drop into the gate | The green smoke flare on success |
| K8 | Long-Range Scouting Formation rides out; coloured smoke relays (red = Titan sighted, green = course, black = abnormal) | 36-37 | Very high shot: the crescent formation on the plains, smoke columns relayed along the chain in canon order | Accurate smoke colours and order |
| K9 | The Female Titan tears through the right flank | 38 | Medium-high tracking shot: riders scatter, smoke turns black | Blonde short hair, exposed-muscle face pattern, hard sprint |
| K10 | Forest of Giant Trees: the squads hold the forest edge; Eren's squad rides down the road while soldiers in the rear guard die | 39-40 | Above the canopy gaps, following the road; ODM wires flash between 80 m trunks | Horses on the forest road; green cloaks |
| K11 | THE TRAP: the Female bound by hundreds of harpoon cables fired from the trees | 40 | Overhead at canopy height; the cable volleys fire in waves, then she stands pinned and hardens her nape | Built in Blender as curve cables on our Female asset (no ready-made bound-Female asset is usable) |
| K12 | The scream; Titans swarm and eat her as the shifter escapes | 41 | High, wide shot: pure Titans converging from all sides | |
| K13 | Squad Levi wiped out; Eren transforms in rage; Eren vs the Female and his defeat | 42-43 | Along the forest road: the squad's bodies on the trees, the lightning-strike transformation, the fight and the nape bite | Gold lightning, the steam explosion |
| K14 | Stohess final battle: the rubble trench, the church collapse, the climb up Wall Sina, Mikasa cuts the fingers, the crystal, the Titan's face in the wall | 46-50 | The finale, given the most time (≥2 min). Large aerial orbits over the destroyed streets, then the slow push to the face in the Wall as the end frame | |

Pacing: with these beats EP1 runs about 16-19 min. If it must be cut, compress training (ch. 13-15) and the trial/castle (31-35), never K1-K14.

## 7. Viewer must-not-miss audit (user 10/24 04:29: "check the story again; put in everything a viewer would miss")
K3 is CONFIRMED as the S1E16 recruitment night, where Erwin's speech ends with the cadets saluting. Chapters 3-5 (scouts return, Grisha's promise, the river) stay skipped in the opening one-take, per the user at 03:33.

Every row below is mandatory unless marked optional. They are staged like section 6: sky view, moderate height, 3-8 s, faceless characters recognised by hair, outfit and colour.

| # | Beat (episode) | Ch. | Why a viewer would miss it | Sky-view staging |
|---|---|---|---|---|
| V1 | Eren on the ferry vows to exterminate every Titan (S1E2) | 9 | The core motive of the whole series | Crowded ferry on the dusk river, the burning town behind it; the boy in the red coat standing at the rail, fist clenched |
| V2 | Grisha injects Eren in the dark forest (S1E2/E9) | 10 | The lore hook for the Attack Titan; the basement key | Lantern in a dark forest clearing, two figures; the key glints on Eren's neck |
| V3 | The 846 "retake Wall Maria" operation sends 250,000 refugees out to die (S1E2) | 12 | The cruelty that defines the walls' politics | Very high shot: a long column of civilians marching out of a Rose gate across the grey Maria belt, then the column thins |
| V4 | Training: Keith's initiation and Sasha eating the potato (S1E3) | 13 | A fan-favourite comic beat | Training yard from above: cadet rows, one girl in a ponytail eating at attention, later running laps at sunset |
| V5 | Eren hangs upside down on the balance rig, then succeeds with new gear (S1E3) | 14 | The iconic "Eren can't use ODM" beat | Training yard: one rig with a flipped cadet, then upright |
| V6 | 850: the Colossal reappears on Trost's wall; Eren alone faces it on the cannon rail, it vanishes (S1E4-5) | 17-18 | The "five years later" mirror of 845 | Wall-top rail shot, Colossal's head again, one small green-cloaked cadet flying at its nape, steam burst |
| V7 | Squad 34 wiped out: Thomas eaten, Eren loses his leg saving Armin and is swallowed (S1E5) | 19 | The biggest shock of the first act | Rooftop height: a Titan bites Eren's leg; Armin thrown out of the mouth; the jaw closes |
| V8 | Mikasa learns Eren is "dead", charges, runs out of gas and is saved by the Attack Titan (S1E6-7) | 21-22 | The Attack Titan's first appearance | Rooftops: a red scarf falling into the street, then the 15 m Titan's punch |
| V9 | Armin salutes the Garrison and pleads for Eren (S1E10) | 25 | The emotional turning point | Wall foot: Garrison ring of rifles and swords, one small blond cadet saluting, a steaming ribcage behind him |
| V10 | Pyxis's speech on the wall top before the boulder operation (S1E11) | 26 | The plan and its stakes | Wall top above the inner side, a bald old commander facing thousands of soldiers below |
| V11 | Eren goes berserk and punches at Mikasa; Armin stabs the nape to wake him (S1E12-13) | 27-28 | The drama that makes the plug "earned" | Boulder site: the Titan swings at a red-scarfed figure, a small figure in the nape |
| V12 | Ian's and Rico's squads die holding off Titans; red-to-green smoke at success (S1E13) | 29 | The sacrifice that pays for the victory | Already in K7; make the casualties readable |
| V13 | Levi arrives and cuts down Titans in seconds (S1E13) | 30 | "Humanity's strongest" introduction | Wall top above the sealed gate, a fast spinning streak cutting two napes, Survey Corps cloaks landing |
| V14 | Jean finds Marco's half-eaten body during the cleanup (S1E13) | 30 | The quiet grief beat | Cleanup street with body carts and smoke from the pyres, one cadet standing over a body |
| V15 | Trial: Levi kicks Eren in court; Erwin takes custody (S1E14) | 31 | Changes Eren's fate | Courtroom with the roof cut away, a kneeling figure in chains, a short figure kicking |
| V16 | Sawney and Beane killed at night (S1E15) | 33 | Plants the "enemy inside" mystery | Research grounds at night, two steaming carcasses in restraints |
| V17 | The Female Titan peeks under Armin's hood and spares him (S1E17) | 38 | The clue that Armin uses later | Plains: a crouching Titan lifts a hood, then runs on |
| V18 | The Female eats/kills Squad Levi; Petra pinned to a tree; Eren transforms in fury (S1E21) | 42 | Part of K13; keep Petra readable (copper hair) | Forest road |
| V19 | Mikasa and Levi rescue Eren from her mouth; Levi hurts his leg (S1E22) | 43 | The rescue | Forest edge |
| V20 | Retreat: the dead are thrown off the carts to outrun Titans; jeers at Karanes (S1E22) | 44 | The cost of the expedition | Plains: wagons, bodies tumbling off, a Titan chasing; then Karanes streets with crowds |
| V21 | Stohess: Eren biting his hand again and again under the rubble; Annie's ring (S1E24) | 47 | The struggle to transform | Underground stairway caved in, then steam and lightning |
| V22 | Annie seals herself in crystal; the Titan face in Wall Sina; Pastor Nick's panic (S1E25) | 50 | The cliffhanger ending | End frame (already the finale of K14) |
| V23 (optional) | Hannes and Moses's arm returned to his mother (S1E1) | 3 | Skipped per user in the one-take | Only if a later recap needs it |

Running order: after the opening one-take, go V1 → V2 → V3 → V4/V5 → V6 → V7 → V8 → K5 → K6/V9 → V10 → V11 → K7/V12 → V13 → V14 → V15 → V16 → K3 → K8 → K9/V17 → K10 → K11 → K12 → K13/V18 → V19 → V20 → V21 → K14/V22.

Estimated runtime: 18-22 min. Hold every beat to 3-8 s from the sky. Use training and the trial as short montages.

## 8. Dialogue overlay windows (user 10/24 04:37)
In editing, the user will overlay the matching anime clip, blurred, with its original voice line, on top of our 3D shot. Rules for every beat with a spoken line:
- HOLD WINDOW: keep the shot running for the line length + 1 s before any transition. The camera only drifts slowly; no fast moves or cuts during the window.
- The action stays readable under a blurred overlay: put the subject near the frame centre, keep the background calm and high-contrast, and keep the HUD caption out of the window.
- Never transition the moment an event lands. The default hold after the event is ≥2 s.
- Every window is logged in a timing sheet (frame in/out, line) so the user can drop the clips straight in.

| Beat | Line (anime) | 3D hold |
|---|---|---|
| K1 Carla | Eren reaching back on Hannes's shoulders, "Yamero!" | about 2 s of Eren's reaching arm clearly visible, THEN transition |
| V1 Ferry vow | "I'll exterminate every last one of them" (駆逐してやる) | about 3 s hold on the ferry |
| V2 Grisha's injection | (no line needed) | Syringe → Grisha puts the key necklace on Eren → a static/glitch blur transition (Eren doesn't remember it), then fade into the next scene |
| V6 Eren vs the Colossal at Trost | Eren's line on the wall top | 2-3 s hold before the steam burst |
| V7 Eren saves Armin, is swallowed | Eren's last words to Armin | 2-3 s hold on the closing jaw |
| V9 Armin's salute | Armin's plea | 3-4 s hold |
| V10 Pyxis's speech | Pyxis's lines | 4-6 s hold (slow orbit) |
| K3 Erwin's recruitment salute | "Shinzou wo sasageyo!" | 3 s hold on the salute |
| K13 Eren's rage transformation | Eren's scream | 2 s hold before the lightning |
| V21 Stohess, under the rubble | Eren's line | 2-3 s hold |
Lines the user adds later get the same treatment.
