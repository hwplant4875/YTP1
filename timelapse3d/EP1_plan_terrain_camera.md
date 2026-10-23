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
