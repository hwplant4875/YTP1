# EP08 shot audit, v6 render (conjuring_ranked_v6.mp4, script_v3)

Method (11/19): the middle frame of every one of the 279 shots, grabbed from the final v6 render. The contact sheets are in 2_renders\audit_v6\s00.jpg to s11.jpg (480 px tiles labelled with shot id, time, clip@in-point and the words spoken; made by qa/audit_sheets.py, not committed). Frames darker than luma 45 were brightened to look at them, and every doubtful shot was checked again on frame strips of its source clip. New shots for the script_v3 lines were picked from qa/scene_library_v2.md and frame-checked before the render.

Order change: s07 is #4 The Devil Made Me Do It 35%, s08 #3 Annabelle: Creation 25%, s09 #2 The Nun 12%, s10 #1 The Nun II 5%. Each film's shot list moved with it and every shot was re-anchored to the new word timings. Rank cards, stat cards (stats.json), tier labels, film labels, kit chapters and srt follow the new order.

Pass 1 (full render) found 4 shots to fix. All were re-cut and their sections re-rendered (pass 2 and 3):
- s06 "because of it": dark frames before the lightning; it now starts on the flash with the entity crouched over Lorraine.
- s06 "and she's brought back": near-black; now Lorraine bent over Judy against the lit stair rails.
- s03 "is Evelyn's": it started on John and Mia; now Evelyn close.
- s11 "the Valak that burned a priest alive in midair": now Jacques watching, Noiret burning in the air, Jacques screaming. s10 "and burns him alive" keeps the first half of the scream; no span is shared.

Rules checked:
- qa/dupes.py: 0 repeated spans (re-uploads mapped, including c2_name = c2_cz_finale - 412.6 and n1_ar_defeats = co_valak0 + 43.3, both measured on frames for v6).
- No suicide act: no Evelyn fall, no Higgins throat, no rope, attic or hanging Judy. The s06 hang line shows possessed Judy crawling and Ed after the attic.
- No graphic blood frame: cr_end 0:46 is zoomed so the wall smear stays out; the Creation adoptive-couple shots are bloodless.
- Audio: integrated -15.1 LUFS, true peak -1.5 dBFS, no silence over 1.5 s; the three film-line inserts sit 1-3 dB under the narration.

**Final counts: MATCH 243, WEAK 36, WRONG 0.**

## Needs reword (no true footage exists; a neutral true shot of that film's demon is used)

- s03 "It will burn your home and throw you across the room": nobody is thrown across a room in any Annabelle (2014) clip. The only throw is Father Perez hurled off the church steps (a14_wb_want 5:26), already used on "hurls a priest through the air". On screen now: the doll's face on Perez's car seat (a14_wb_want 4:36.5). A true alternative would be "...and claw your arm" (the scratches at a14_cz_attic 3:12 and 5:20).
- s09 "and even then, Valak gets away, hiding inside Frenchie" (carried from v5): the escape into Frenchie and the inverted cross are in no clip (the Movieclips ending is age-gated). On screen: Frenchie (co_valak0 2:48).
- s02 "The Ferryman chases the babysitter" (partial, carried from v5): the Ferryman is only a small dark skull face; Mary Ellen dragged and running is clear.

## Every shot

| shot | time | words | clip@in | verdict | on screen |
|---|---|---|---|---|---|
| s00#00 | 0:00.00 | These demons | c2_painting@136.97 | MATCH | 136.5-136.93 is a dark, barely visible Valak face from the previous shot (hard cut at 136.95); the bright face runs 136.97-138.70. s04 'survival rate' c2_painting 137.2-138.8 is now the same moment: s04 needs another span |
| s00#01 | 0:00.64 | will burn you alive | co_burn_4k@157.5 | MATCH | Father Noiret burning, his head and arms inside the flames; hard cut at 158.2 to an all-fire shot (the old span crossed it) |
| s00#02 | 0:01.72 | in midair, | co_burn_4k@154.9 | MATCH | cut at 156.03 to a boy in the pews |
| s00#03 | 0:02.80 | bury you alive, | co_buried_b@102.4 | MATCH | one shot 99.5-105.85, but the lighter is only lit from ~102.4 (100-102 is near-black) |
| s00#04 | 0:04.05 | snap your neck, | n2_deliv@137.71 | MATCH | Last Rites: hands seize Heather's throat and head from behind, one shot 255.8-260.8+ (B1b: clearer than n2_deliv 137.8; letterboxed, z 1.25 keeps 640 rows) |
| s00#05 | 0:05.33 | make you stab | dm_vision@153.15 | MATCH | 153.0-153.1 is an arm only; the bloody knife is in frame from 153.15; cut to Jessica at 154.05 |
| s00#06 | 0:06.01 | your best friend | dm_vision@160.0 | MATCH | cut to Lorraine at 160.89 |
| s00#07 | 0:06.77 | twenty-two times, | dm_vision@157.1 | MATCH | 156.7-157.0 her eyes are down; the white eyes show from 157.1; cut to Lorraine at ~159.0 |
| s00#08 | 0:08.05 | or turn your own mother | co_mother_c@305.9 | MATCH | The Conjuring: possessed Carolyn's grinning face next to Roger |
| s00#09 | 0:09.54 | against you. | universe@659.1 | MATCH | possessed Carolyn raising the scissors in the crawlspace, going for April |
| s00#10 | 0:10.46 | And sometimes, | universe@904.0 | MATCH | the Annabelle doll close-up (The Conjuring's prologue) |
| s00#11 | 0:11.54 | all it takes | ach_devil_cz@297.5 | MATCH | Annabelle Comes Home: the whole doll seated in the open glass case |
| s00#12 | 0:12.37 | is a doll. | cr_wheel@535.9 | MATCH | Annabelle: Creation: the doll in a carved chair, daylight, sharp, centred |
| s00#13 | 0:13.26 | We're ranking every Conjuring demon by your chance of surviving it. | still_posterwall@0.0 | MATCH | the 9 posters pop in (release order) and hold to the end |
| s01#00 | 0:16.97 | Here's the rule. Tonight, the demon from one of these movies | ach_room@44.0 | MATCH | ACH: Daniela among the cursed artifacts, dark |
| s01#01 | 0:20.46 | is in your room, | ach_hands@2.0 | MATCH | ACH: Judy asleep in her bed at night (0:00-0:13) |
| s01#02 | 0:21.59 | and it wants you. | n2_deliv@126.2 | MATCH | Nun II: Valak at the end of a hallway that turns red |
| s01#03 | 0:22.93 | And every one is different. | c2_grave@118.82 | MATCH | C2: Janet on the sofa |
| s01#04 | 0:24.65 | One is a doll | ach_devil_cz@298.32 | MATCH | ACH: Judy's hand on the glass, Annabelle inside |
| s01#05 | 0:25.58 | that wakes up every cursed thing in the house, | ach_room@298.5 | MATCH | ACH: the haunted TV shows Daniela a moment ahead of her (4:58-5:22) |
| s01#06 | 0:27.87 | one wants you to give up your own life, | a14_baby@35.88 | MATCH | Annabelle: "her SOUL" scrawled on the nursery ceiling |
| s01#07 | 0:30.04 | and one wiped | co_valak0@93.0 | MATCH | The Nun: Valak |
| s01#08 | 0:30.96 | out an entire abbey of nuns. | n1_pray@2.15 | MATCH | The Nun: nuns praying, Valak at the altar |
| s01#09 | 0:33.11 | So we score each one on | lr_end@46.0 | MATCH | Last Rites: Ed walks in |
| s01#10 | 0:34.55 | strength, | co_mother_c@248.0 | MATCH | Conjuring: sheeted Carolyn's chair in the cellar as it rises (4:08) |
| s01#11 | 0:35.18 | intelligence, | dm_altar@128.0 | MATCH | DMMDI: the occultist behind her altar |
| s01#12 | 0:36.30 | kill count, | cr_wheel@567.12 | MATCH | Creation: Samuel's body on the floor, wide |
| s01#13 | 0:36.94 | and possession, which is how completely it | lr_end@99.43 | MATCH | Last Rites: possessed Judy's bloody grin |
| s01#14 | 0:39.26 | can take over your body. | dm_david@315.93 | MATCH | DMMDI: possessed David screaming |
| s01#15 | 0:40.51 | Put it all together, and you get one number, your survival rate. | spooky_nun@1112.0 | MATCH | The Nun: Irene with a candle |
| s02#00 | 0:44.13 | Number nine, Annabelle Comes Home. | ach_case@61.0 | MATCH | the Annabelle doll grinning on the back seat (1:01-1:03) |
| s02#01 | 0:46.75 | This Annabelle is the weakest demon of them all, | ach_hands@51.4 | MATCH | the doll seen through the blue lamp lens (0:51.4-0:53) |
| s02#02 | 0:49.51 | because even when it gets loose | ach_room@12.5 | MATCH | the samurai armor in the dark artifact room (0:12-0:22) |
| s02#03 | 0:51.23 | and wakes up every cursed object | ach_cz_stabs@100.0 | MATCH | the typewriter typing "miss me?" by itself (1:40-1:43) |
| s02#04 | 0:52.83 | in the Warrens' house, | ach_room@212.5 | MATCH | a ghost hand plays the piano beside Daniela's (3:32-3:43) |
| s02#05 | 0:54.07 | it doesn't manage to kill a single person. | ach_case@152.5 | MATCH | Ed and Lorraine standing together, alive, after the truck (2:32-2:35) |
| s02#06 | 0:56.66 | The Ferryman chases | ach_ferry@118.0 | WEAK | the Ferryman is only a small dark skull face among the coin-eyed souls |
| s02#07 | 0:57.59 | the babysitter, | ach_ferry@126.5 | WEAK | Mary Ellen in the dark hallway, flashlight flare |
| s02#08 | 0:58.59 | the Bride takes over | ach_cz_stabs@209.0 | WEAK | the Bride face to face with Daniela, dark |
| s02#09 | 0:59.63 | her friend, | ach_devil_cz@146.0 | WEAK | veiled Daniela seen from behind |
| s02#10 | 1:00.43 | and a hellhound claws through the roof of a car | ach_wolf@43.0 | MATCH | claws rake the car and tear through the convertible roof (0:43-0:50) |
| s02#11 | 1:02.69 | with the little girl inside. | ach_wolf@20.0 | MATCH | Judy inside the car, terrified (0:16-0:42) |
| s02#12 | 1:04.16 | The doll turns up in her bed, | ach_hands@32.0 | MATCH | v6: under the sheet, the doll lying right beside Judy in her bed (0:32-0:34) |
| s02#13 | 1:05.84 | and later the demon behind it | ach_hands@74.0 | MATCH | v6: the horned demon's silhouette over Judy's bed in the red lamp light (1:14-1:16) |
| s02#14 | 1:07.53 | tries to take her soul. | ach_end@14.0 | MATCH | v6: the horned demon draws the soul-mist out of Judy's mouth (0:14-0:17) |
| s02#15 | 1:08.93 | In the end, two teenagers and a little girl | ach_devil_cz@324.0 | MATCH | the three girls in the artifact room after it is over (5:24-5:30) |
| s02#16 | 1:11.41 | beat it on their own, | ach_end@62.0 | MATCH | Judy and Mary Ellen pressed against the case, Annabelle behind the glass |
| s02#17 | 1:12.69 | by forcing the doll back into its case | ach_end@45.0 | WEAK | the case door being forced, hard to read at mid-shot |
| s02#18 | 1:14.77 | and locking it. | ach_end@80.0 | MATCH | the key turns in the case lock, Daniela's cuff (1:20-1:22) |
| s02#19 | 1:15.72 | Even loose in your room all night, it will scare you half to death, | ach_hands@54.0 | MATCH | Judy in her room in the lamp's coloured light (0:54-1:03) |
| s02#20 | 1:19.53 | but you'll almost certainly see morning. | ach_end@95.0 | MATCH | Judy close, calm (1:35-1:39) |
| s02#21 | 1:21.82 | Survival rate, ninety-five percent. | ach_case@149.0 | WEAK | the doll on the back seat is small |
| s03#00 | 1:24.27 | Number eight, Annabelle. | a14_wb_want@52.0 | MATCH | the Annabelle doll in the nursery cabinet, close (0:52-1:01) |
| s03#01 | 1:26.16 | This demon is more dangerous than the last one, | a14_cz_soul@36.0 | MATCH | the old man in the hall turns: a demonic face (0:36-0:37) |
| s03#02 | 1:28.99 | because it doesn't just scare you, | a14_cz_soul@44.0 | MATCH | the stereo and record player switch on by themselves (0:44-0:51) |
| s03#03 | 1:30.79 | it hurts you, | a14_cz_attic@193.4 | MATCH | fresh claw scratches on Mia's forearm (3:13.4-3:15) |
| s03#04 | 1:31.79 | inside your own home. | a14_cz_soul@112.0 | MATCH | the nursery, trashed (1:12-1:13) |
| s03#05 | 1:33.63 | It sets your kitchen on fire | a14_fire@87.2 | MATCH | the popcorn bursts into flames across the stove (1:27.2-1:29.4) |
| s03#06 | 1:35.21 | and hurls a priest through the air | a14_wb_want@326.3 | MATCH | Father Perez hurled backwards off the church steps (5:26.3-5:27.9) |
| s03#07 | 1:37.01 | at the door of his own church. | a14_wb_want@328.0 | MATCH | the church's open door after (5:28-5:31) |
| s03#08 | 1:39.05 | But it has one big weakness. | a14_wb_want@92.0 | MATCH | the doll close on the chair (1:32-1:35) |
| s03#09 | 1:41.06 | In this whole movie, | a14_cz_soul@248.0 | WEAK | "In this whole movie": the demon taking Leah, unhurt, stands in for its not killing |
| s03#10 | 1:42.45 | it never kills anyone | a14_cz_attic@306.14 | WEAK | the horned demon is on screen only ~0.6 s at the start, then Mia fleeing |
| s03#11 | 1:43.77 | with its own hands. | a14_cz_attic@320.0 | MATCH | v6: its claw marks on Mia's forearm, she is alive (5:20-5:21.6) |
| s03#12 | 1:45.12 | Five people die, | a14_cz_invasion@336.0 | WEAK | the cult girl with the doll stands in for "five people die" (no deaths shown on purpose) |
| s03#13 | 1:46.48 | but four of them die | a14_cz_invasion@388.3 | MATCH | v6: the cultist Annabelle Higgins lunges at Mia (6:28.3-6:29.7; no blood, never 6:30+) |
| s03#14 | 1:47.44 | at human hands, | a14_cz_invasion@415.6 | MATCH | v6: the cultist grinning in the nursery doorway (6:55.6-6:57.2; no blood, no killing) |
| s03#15 | 1:48.66 | and the only life the demon gets | a14_wb_baby@292.0 | WEAK | the life-size Annabelle figure at the window |
| s03#16 | 1:50.41 | is Evelyn's, | a14_cz_soul@480.0 | MATCH | v6: Evelyn kneeling by John and Mia, close (8:00-8:01.9; John and Mia before and after) |
| s03#17 | 1:51.33 | when she gives up her own life in Mia's place. | a14_cz_soul@510.0 | MATCH | Evelyn in the open window holding the doll, her decision (8:30-8:35.5; never 8:36+) |
| s03#18 | 1:54.04 | It will burn your home | a14_fire@108.0 | MATCH | the kitchen engulfed, Mia small in the doorway (1:48-1:51) |
| s03#19 | 1:55.22 | and throw you across the room, | a14_wb_want@276.5 | WEAK | NEEDS REWORD: nobody is thrown across a room in any clip; the doll's face is a neutral true shot |
| s03#20 | 1:56.79 | but it has never taken a life by force, | a14_cz_soul@160.5 | MATCH | v6: the doll alone in the living-room armchair (2:40.5-2:43.5) |
| s03#21 | 1:59.22 | so you'll probably live. | a14_cz_attic@0.0 | MATCH | Mia lays Leah safely in her crib (0:00-0:07) |
| s03#22 | 2:00.91 | Survival rate, eighty percent. | a14_wb_want@44.0 | MATCH | the doll seated in the cabinet (0:44-0:51) |
| s04#00 | 2:03.03 | Number seven, The Conjuring. | c1_sheets@22.8 | MATCH | the farmhouse, a sheet flying off the line onto the house |
| s04#01 | 2:05.17 | This demon is far more dangerous than Annabelle, | co_mother_c@288.0 | WEAK | Roger and the sheet, generic |
| s04#02 | 2:08.16 | because it doesn't need a doll or a deal, | c1_cz_annstory@31.0 | MATCH | the Annabelle doll, extreme close-up (Conjuring 2013 prologue) |
| s04#03 | 2:10.42 | it gets inside your body, | c1_dog_b@310.0 | MATCH | the dark figure dropping onto Carolyn in bed (5:10-5:12) |
| s04#04 | 2:12.28 | and moving out won't save you. | c1_dog_b@368.0 | MATCH | the family leaves the house (6:08-6:10) |
| s04#05 | 2:14.22 | Bathsheba was a witch | c1_bedroom@110.5 | MATCH | Bathsheba crouched on top of the wardrobe, then lunging (1:50.5-1:52) |
| s04#06 | 2:15.52 | who gave her own baby to the devil, | c1_land@84.5 | MATCH | the old album photo of a baby and a woman (1:24-1:29); the zoom keeps the burned-in subtitle out |
| s04#07 | 2:17.63 | and she curses anyone who lives on her land. | c1_dog_b@14.75 | MATCH | the Perrons unloading at the farmhouse |
| s04#08 | 2:20.27 | She stops every clock in the house at three oh seven, | c1_dog_b@74.5 | MATCH | the grandfather clock stopped at 3:07 (1:14.5-1:17.5) |
| s04#09 | 2:23.23 | leaves bruises on | c1_cz_hideclip@13.0 | MATCH | bruises on Carolyn's arm and shoulder at the mirror (0:13-0:16) |
| s04#10 | 2:24.27 | you while you sleep, | c1_dog_b@56.0 | MATCH | Carolyn's bruised legs as she sits on the bed (0:56-0:58) |
| s04#11 | 2:25.28 | yanks the girls' feet in bed | c1_sleep@1.9 | MATCH | v6: Christine asleep, her leg jerked toward the foot of the bed (0:02.3-0:02.8) |
| s04#12 | 2:26.72 | and drags one across the room by her hair, | co_mother_b@362.0 | MATCH | v6: Nancy dragged across the floor, then her hair yanked straight up (6:02-6:07) |
| s04#13 | 2:29.26 | and on the very first morning, | c1_dog_b@24.5 | MATCH | Sadie on the porch, refusing to go in (0:24-0:29) |
| s04#14 | 2:30.91 | the family dog is found dead in the yard. | c1_dog_b@54.0 | MATCH | MORNING: Sadie lying dead in the yard, Carolyn holding April, Roger running in (0:54-0:56) |
| s04#15 | 2:33.32 | Then she takes over | co_mother_c@292.2 | MATCH | possessed Carolyn laughing |
| s04#16 | 2:34.44 | the mother, Carolyn, | co_mother_c@300.35 | MATCH | possessed Carolyn grinning |
| s04#17 | 2:35.40 | completely, | universe@477.5 | MATCH | Carolyn held down by the men, screaming |
| s04#18 | 2:36.47 | and makes her try to kill her own children. | universe@445.8 | MATCH | possessed Carolyn with the scissors over her daughter |
| s04#19 | 2:39.08 | The Perrons only survive | c1_dog_b@474.0 | MATCH | Carolyn hugs April; the family safe in the yard (7:54-8:00) |
| s04#20 | 2:40.58 | because Lorraine reaches Carolyn | universe@694.2 | MATCH | Lorraine close, in tears, talking to Carolyn |
| s04#21 | 2:42.02 | with a happy memory, | universe@698.8 | MATCH | the mother in red running on the beach with her girl |
| s04#22 | 2:43.26 | and Ed does the exorcism himself. | co_mother_c@10.0 | MATCH | Ed reads the rite in the cellar |
| s04#23 | 2:45.33 | She will follow you, hurt you, | c1_cz_clap@290.0 | MATCH | Carolyn lit by her match in the cellar (4:50) |
| s04#24 | 2:47.33 | and climb inside you, | c1_exorcism_b@92.0 | MATCH | Ed's hand on possessed Carolyn's forehead, screaming (1:32-1:38) |
| s04#25 | 2:48.84 | but in her own movie she never manages to kill a single one of the Perrons. | c1_exorcism_b@120.0 | WEAK | freed Carolyn with April in the dark crawlspace |
| s04#26 | 2:53.41 | Survival rate, sixty-five percent. | universe@715.6 | MATCH | possessed Carolyn screaming |
| s05#00 | 2:55.97 | Number six, The Conjuring Two. | universe@1086.0 | MATCH | Janet on the sofa |
| s05#01 | 2:58.47 | This is the movie that introduced Valak, | c2_painting@203.0 | MATCH | the Valak painting |
| s05#02 | 3:00.87 | and Valak is much smarter than Bathsheba, | c2_painting@58.2 | MATCH | Lorraine with Valak looming behind her |
| s05#03 | 3:03.48 | even though nobody in the haunted house dies. | c2_cz_finale@528.0 | MATCH | aftermath: Peggy hugs Janet, everyone alive (8:48-8:53) |
| s05#04 | 3:06.04 | It hides behind the ghost of an old man, | c2_vision@56.0 | MATCH | Valak standing right behind Bill Wilkins in his chair (0:56-0:57) |
| s05#05 | 3:08.42 | Bill Wilkins, | c2_vision@2.0 | MATCH | Bill Wilkins's ghost in his chair (0:00-0:55) |
| s05#06 | 3:09.46 | so everyone thinks it's just a ghost. | c2_cz_billy@186.0 | MATCH | the BBC sofa interview, Janet in the old man's voice (3:06-3:23) |
| s05#07 | 3:11.45 | It blocks Lorraine's visions and attacks her inside them, | c2_cz_vision@372.0 | MATCH | Valak in the mirror choking Lorraine in her Amityville vision (6:12-6:23; never 6:24+) |
| s05#08 | 3:14.49 | throws Janet out of her | c2_cz_voices@473.0 | MATCH | v6: Janet in her red pyjamas flung through the air of her bedroom (7:53-7:54.4) |
| s05#09 | 3:15.77 | bed at night, | c2_cz_voices@388.5 | WEAK | Janet waking on the floor at night, dark close-up |
| s05#10 | 3:16.47 | and takes over her body | c2_janet@220.3 | MATCH | possessed Janet's face |
| s05#11 | 3:17.69 | completely. | c2_cz_billy@242.0 | WEAK | possessed Janet in Bill's chair, quiet moment |
| s05#12 | 3:18.60 | Ed has to fight his way in to save her. | c2_cz_finale@18.0 | MATCH | Ed thrown back by wind and debris in the house (0:18-0:23) |
| s05#13 | 3:20.99 | But Valak has one fatal weakness. | c2_cz_finale@226.8 | MATCH | Lorraine's Bible, the name VALAK scratched into the page (3:46.8-3:49.3) |
| s05#14 | 3:23.33 | If you know its name, you have power over | c2_name_b@58.3 | MATCH | Lorraine bent over the Bible |
| s05#15 | 3:25.81 | [film] You are Valak. | c2_name@39.75 | MATCH |  |
| s05#16 | 3:27.78 | it, and Lorraine sends it back to Hell just by saying it. | c2_name@43.699 | MATCH |  |
| s05#17 | 3:30.77 | [film] I condemn you back to hell. | c2_name@52.81 | MATCH |  |
| s05#18 | 3:32.90 | It's smarter than you, and it | c2_name@55.59 | MATCH |  |
| s05#19 | 3:34.45 | will fool everyone you call for help, | c2_cz_finale@24.0 | MATCH | the neighbour with an axe, Lorraine at the door in the rain (0:24-0:31) |
| s05#20 | 3:36.30 | but in its whole movie | c2_cz_finale@495.0 | WEAK | Lorraine on the wrecked floor, dark |
| s05#21 | 3:37.60 | it never kills a single person, | c2_cz_finale@500.0 | MATCH | v6: Vic and Lorraine in the wrecked room, everyone alive (8:20-8:24) |
| s05#22 | 3:39.85 | and the moment someone says its name, | c2_cz_finale@232.3 | MATCH | v6: the VALAK page in Lorraine's Bible, a second look (3:52.3-3:53.3) |
| s05#23 | 3:41.69 | it's sent straight back to Hell. | c2_cz_finale@459.3 | MATCH | v6: Valak screams and is pulled backward into the dark (7:39.3-7:41) |
| s05#24 | 3:43.36 | Survival rate, fifty-five percent. | c2_painting@189.6 | MATCH | Valak's face over Lorraine's shoulder |
| s06#00 | 3:45.77 | Number five, Last Rites. | lr_family@102.2 | MATCH | the Smurl street at night |
| s06#01 | 3:48.13 | This demon is stronger | lr_end@42.0 | MATCH | the ornate mirror, glowing |
| s06#02 | 3:49.45 | than that Valak, | c2_painting@206.88 | MATCH | callback: Valak (Conjuring 2) |
| s06#03 | 3:50.49 | and it's the only one | lr_s01_baby@18.3 | WEAK | Lorraine's evil reflection in the mirror stands in for "the only one" |
| s06#04 | 3:51.56 | that has ever left a Warren dead, | lr_birth@55.0 | MATCH | v6: the still newborn laid on Lorraine's chest (0:55-1:01) |
| s06#05 | 3:53.68 | even if only for a moment. | lr_birth@104.5 | MATCH | v6: warm light, the baby starts crying, revived (1:44.5-1:47.5) |
| s06#06 | 3:55.36 | It lives inside an old mirror, | lr_s01_baby@2.0 | MATCH | the old mirror (0:00-0:10; never 0:21-0:23) |
| s06#07 | 3:57.39 | and in nineteen sixty-four, | lr_birth@20.05 | MATCH | Lorraine in labour |
| s06#08 | 3:59.02 | Judy Warren was born dead | lr_birth@41.0 | MATCH | the silent newborn (0:40-0:47) |
| s06#09 | 4:00.70 | because of it, | lr_s01_baby@141.3 | MATCH | v6: the lightning flash, the barefoot mirror entity in a gown crouched over Lorraine's bed (2:21.3-2:22.05; dark before and after) |
| s06#10 | 4:01.43 | until Ed and Lorraine prayed | lr_birth@76.0 | MATCH | v6: Lorraine praying, Ed's hand on her face (1:16-1:22) |
| s06#11 | 4:02.95 | her back to life. | lr_birth@117.0 | MATCH | v6: Lorraine holds the crying newborn (1:57-2:03) |
| s06#12 | 4:04.09 | Twenty-two years later, it comes back for her. | lr_judy@50.0 | MATCH | adult Judy in the mirror maze of brides |
| s06#13 | 4:06.61 | It hides behind | lr_cz_comp@92.0 | WEAK | the old woman ghost, very dark |
| s06#14 | 4:07.49 | three ghosts, | lr_axe@234.75 | MATCH | a ghost's face lunging at the camera |
| s06#15 | 4:08.59 | makes a girl cough up | lr_s03_blood@171.0 | MATCH | Dawn at the sink with the family, wide (2:51; never the close-ups) |
| s06#16 | 4:09.71 | blood and broken glass, | lr_s03_blood@200.0 | MATCH | Heather's horrified face (3:20-3:21.6; never the sink close-up at 3:18) |
| s06#17 | 4:11.18 | drives the priest who tries to help | lr_priest@31.0 | MATCH | Father Gordon alone at his desk |
| s06#18 | 4:12.86 | to his death, | lr_priest@138.45 | MATCH | fire in his glasses (never 2:22-2:37) |
| s06#19 | 4:13.86 | locks Lorraine in the basement, | lr_exorcism@4.0 | WEAK | Lorraine on the basement floor, very dark |
| s06#20 | 4:15.48 | and takes over Judy | lr_s09_possessed@100.0 | MATCH | possessed Judy, white eyes, bloody mouth (1:40-1:41) |
| s06#21 | 4:16.58 | and makes her hang herself, | lr_s09_possessed@40.2 | WEAK | possessed Judy crawling stands in for the hanging (rope and attic never shown, by rule) |
| s06#22 | 4:18.04 | until Ed cuts her down | lr_exorcism@261.5 | WEAK | Ed in silhouette after the attic; the cut-down itself is never shown (rope rule) |
| s06#23 | 4:19.36 | and she's brought back | lr_exorcism@311.3 | MATCH | v6: Lorraine bent over Judy, praying, backlit by the stair rails (5:11.3-5:12.4; the mirror faces cut in at 5:13) |
| s06#24 | 4:20.28 | a second time. | lr_exorcism@318.6 | MATCH | v6: Judy opens her eyes, held by Lorraine (5:18.6-5:23) |
| s06#25 | 4:21.39 | Ed's exorcism doesn't | lr_end@24.0 | MATCH | Ed reading the rite, hand raised |
| s06#26 | 4:22.75 | even work, | lr_end@80.8 | MATCH | the Bible burns in Ed's hands |
| s06#27 | 4:23.63 | and only the whole family together, Ed, Lorraine and Judy, | lr_end@166.0 | MATCH | three pairs of hands on the mirror (2:46-2:55) |
| s06#28 | 4:27.41 | can break the mirror. | lr_end@183.0 | MATCH | the mirror's ghosts screaming against the cracking glass (3:03) |
| s06#29 | 4:28.48 | Throwing the mirror away won't save | lr_s03_blood@102.0 | MATCH | the mirror thrown into the garbage truck (1:42-1:50) |
| s06#30 | 4:30.66 | you, and neither will a priest, | lr_priest@2.0 | WEAK | Father Gordon's hand, face out of frame |
| s06#31 | 4:31.96 | but it only takes two lives in its whole movie, | lr_priest@122.5 | MATCH | v6: Father Gordon by his match flame, before his death (2:02.5-2:06.5) |
| s06#32 | 4:34.81 | and the one it possessed came back, | lr_end@202.5 | MATCH | v6: Judy close, in tears, free (3:22.5-3:27.5) |
| s06#33 | 4:36.62 | so you've got close to an even chance. | lr_end@226.0 | MATCH | v6: aftermath on the landing, Ed standing (3:46-3:53) |
| s06#34 | 4:38.61 | Survival rate, forty-five percent. | lr_judy@232.0 | MATCH | Judy's demonic grin in the cracked mirror |
| s07#00 | 4:41.10 | Number four, The Devil Made Me Do It. | dm_promise@19.85 | MATCH | the occultist Isla |
| s07#01 | 4:43.63 | This one is smarter than the mirror demon, | dm_calvary@64.0 | WEAK | Isla and Lorraine face to face in the dark, Lorraine in front |
| s07#02 | 4:46.02 | because it doesn't have to kill you itself, | co_stab@104.0 | MATCH | Isla's face, clearest (1:44-1:47) |
| s07#03 | 4:47.97 | it makes you do it. | dm_david@301.12 | MATCH | Arne on the floor, the demon in him |
| s07#04 | 4:49.27 | A witch hides a cursed charm | dm_cz_nightmare@418.0 | MATCH | the witch's totem under the house (6:58-6:59) |
| s07#05 | 4:50.87 | in your home, | dm_cz_nightmare@430.0 | MATCH | Lorraine photographs the totem (7:10-7:19) |
| s07#06 | 4:51.78 | and from then on, | dm_bruno_b@30.0 | MATCH | Arne at the party, before |
| s07#07 | 4:52.82 | the killer is you. | dm_bruno_b@156.3 | MATCH | the knife on the floor |
| s07#08 | 4:54.28 | [film] Take me! | dm_david@319.77 | MATCH |  |
| s07#09 | 4:55.38 | Arne Johnson stabs | dm_bruno_b@144.305 | MATCH |  |
| s07#10 | 4:56.71 | his landlord | dm_cz_archie@60.0 | MATCH | Bruno, the landlord, in daylight (0:56-1:09) |
| s07#11 | 4:57.43 | twenty-two times. | dm_bruno_it@208.5 | MATCH | Arne on the road after, dazed (3:28.5-3:32.5) |
| s07#12 | 4:58.94 | A girl named Jessica | dm_vision@102.6 | MATCH | Jessica smiling |
| s07#13 | 5:00.01 | stabs her best friend Katie | dm_vision@106.0 | WEAK | hands with a rosary (the stabbing is never shown) |
| s07#14 | 5:01.33 | twenty-two times, | dm_vision@185.47 | MATCH | the bloody hand with a rosary |
| s07#15 | 5:02.30 | and then dies too. | co_stab@36.8 | MATCH | the sheet-covered body in the morgue |
| s07#16 | 5:03.67 | The witch kills her own father, | dm_altar@52.42 | MATCH | a ringed hand grips Kastner's head |
| s07#17 | 5:05.67 | and turns Ed against Lorraine | dm_final@102.65 | MATCH | Ed possessed, bleeding eyes |
| s07#18 | 5:07.32 | until he nearly kills her himself. | dm_ar_love@0.0 | MATCH | Ed swings the sledgehammer at Lorraine in the tunnel (0:00-0:06) |
| s07#19 | 5:09.35 | And when the witch fails, | dm_promise@40.0 | MATCH | Isla twisted by her demon, wide (0:40-0:41) |
| s07#20 | 5:10.74 | her own demon twists her body until she's dead. | dm_promise@58.0 | MATCH | Isla collapsing (0:58-1:04; never 0:56-0:57) |
| s07#21 | 5:13.70 | You can't fight it and you can't run, | dm_cz_herself@31.0 | WEAK | the knife attack in the tunnel, motion blur |
| s07#22 | 5:15.83 | because the hands holding the knife are yours, | dm_vision@186.2 | MATCH | the bloody knife in the hay |
| s07#23 | 5:18.50 | and only smashing the witch's altar can break it. | dm_ar_love@104.0 | MATCH | Ed smashes the witch's altar (1:44-1:54) |
| s07#24 | 5:21.27 | Survival rate, thirty-five percent. | dm_promise@49.5 | MATCH | Isla's pale face in the dark |
| s08#00 | 5:23.57 | Number three, Annabelle Creation. | cr_sam@29.3 | MATCH | the Annabelle doll in a chair, bright |
| s08#01 | 5:26.07 | This is where the Annabelle demon began, | cr_wasnt@0.0 | MATCH | Bee at her tea table with the doll |
| s08#02 | 5:28.47 | and it's even more violent than the witch's curse, | cr_scarecrow@26.0 | MATCH | the scarecrow (0:26-0:52) |
| s08#03 | 5:31.24 | because it doesn't need anyone else's hands, | cr_well@96.0 | WEAK | the hand pulling Linda at the well, dark |
| s08#04 | 5:33.56 | it kills people itself. | cr_trapped@350.0 | MATCH | possessed Janice lunges with a knife (5:50-5:53) |
| s08#05 | 5:35.23 | It pretends to be Bee, | cr_esther_scenes@136.0 | MATCH | Bee at the tea table (2:16-2:22) |
| s08#06 | 5:36.72 | the dead daughter of a doll maker, | cr_esther_scenes@60.0 | WEAK | Esther before the accident stands in for "the dead daughter" |
| s08#07 | 5:38.54 | so her heartbroken parents | cr_wasnt@39.1 | MATCH | Esther, grieving |
| s08#08 | 5:40.14 | let it into the doll. | cr_wasnt@60.8 | MATCH | the doll's face, sinister |
| s08#09 | 5:41.56 | Then it goes after the orphan girls who move in. | cr_sam@37.8 | MATCH | Sister Charlotte and the orphans unloading the truck |
| s08#10 | 5:44.33 | It comes for Janice on her stairlift | cr_rt_chair@38.0 | MATCH | Janice on the stairlift riding up in the dark (0:36-0:58) |
| s08#11 | 5:46.15 | and leaves her in a wheelchair, | cr_stair@1.0 | MATCH | Janice in her wheelchair in the sun, eyes closed (0:00-0:06) |
| s08#12 | 5:47.85 | then wheels her into a barn, | cr_stair@30.0 | MATCH | the hooded "Charlotte" wheels Janice across the field into the barn (0:24-0:39) |
| s08#13 | 5:49.63 | and takes over her body for good. | cr_stair@125.6 | MATCH | the black bile forced into Janice's mouth |
| s08#14 | 5:51.62 | Through her, it snaps the doll maker's fingers | cr_sam@16.0 | MATCH | Samuel's fingers bend back around the crucifix (cut by 0:19) |
| s08#15 | 5:54.10 | and kills him. | cr_sam@59.8 | MATCH | his body on the floor, wide |
| s08#16 | 5:55.27 | Then it tears his wife in half, | cr_esther_scenes@78.0 | WEAK | Esther in the dark: her death is voiced only, never shown (gore rule) |
| s08#17 | 5:57.51 | and twelve years later, | cr_end@9.05 | MATCH | the Higgins photos |
| s08#18 | 5:58.79 | through Janice and her cultist boyfriend, | cr_end@46.0 | MATCH | v6: grown Janice in white and her bearded cultist boyfriend at the Higgins' bedroom door (0:46-0:48); the zoom keeps the wall's red smear at the right edge out of frame |
| s08#19 | 6:00.95 | it kills the couple | cr_end@19.0 | MATCH | the Higgins couple woken in bed |
| s08#20 | 6:01.81 | who adopted her. | cr_end@37.3 | MATCH | Pete Higgins at the bedroom door, seen from behind, before the attack (0:35.5-0:38.9); the knife enters at 0:39.0, never past 0:38.8 |
| s08#21 | 6:02.94 | A nun and five girls make it out, | cr_well@116.4 | MATCH | Sister Charlotte holding Linda in the field |
| s08#22 | 6:05.00 | but only because the nun locks it in a closet, | cr_trapped@372.0 | WEAK | Sister Charlotte at the closet, dark |
| s08#23 | 6:07.61 | and the demon stays inside Janice. | cr_trapped@256.3 | MATCH | possessed Janice, a sly smile, holding a doll |
| s08#24 | 6:09.82 | It doesn't want to scare you, it wants your body, | cr_cz_orphan@156.0 | MATCH | possessed Janice walking upright (2:36-2:56) |
| s08#25 | 6:12.78 | and it never gives one back. | cr_soul@140.6 | MATCH | Janice on the dark landing |
| s08#26 | 6:14.53 | Survival rate, twenty-five percent. | cr_cz_released@264.0 | MATCH | the doll in the closet lined with Bible pages (4:24-4:34) |
| s09#00 | 6:17.00 | Number two, The Nun. | co_valak0@4.0 | MATCH | Valak rising out of the water |
| s09#01 | 6:18.92 | This is Valak | spooky_nun@1049.3 | MATCH | Valak |
| s09#02 | 6:20.12 | loose from a doorway | spooky_nun@1117.8 | MATCH | the "Finit hic Deo" door |
| s09#03 | 6:21.00 | to | spooky_nun@1092.45 | MATCH | Valak roaring |
| s09#04 | 6:21.65 | Hell under an abbey in Romania. | n1_hl_abbess@216.0 | MATCH | the abbey at dusk (3:36-3:38) |
| s09#05 | 6:23.46 | Before Irene even arrives, | n1_open@38.0 | MATCH | the nun in the corridor, screaming (never 1:16+) |
| s09#06 | 6:25.46 | every nun in the abbey is already dead, | spooky_nun@999.0 | MATCH | overhead: the dead nuns |
| s09#07 | 6:27.84 | and the sisters she prays | n1_pray@21.0 | MATCH | Irene praying among the nuns |
| s09#08 | 6:29.33 | with were never really there. | n1_pray@39.0 | MATCH | the empty habits on the floor |
| s09#09 | 6:30.68 | It buries Father Burke alive | co_buried_b@75.6 | MATCH | Burke in the coffin with his lighter |
| s09#10 | 6:32.32 | in a coffin, | co_buried_b@98.0 | MATCH | Burke pulls the bell string in the coffin (1:38-1:48) |
| s09#11 | 6:33.32 | and it drowns Irene until she stops breathing, | co_valak0@26.1 | MATCH | Irene held under the water |
| s09#12 | 6:36.11 | and Frenchie has to pump her chest | n1_cz_possessed@461.8 | MATCH | Frenchie bent over Irene, pumping her chest (7:41.8-7:43.8) |
| s09#13 | 6:37.80 | to bring her back. | n1_cz_possessed@469.0 | MATCH | Frenchie breathing into her, she comes back (7:49-7:53) |
| s09#14 | 6:38.70 | The Church sent | co_valak0@64.0 | MATCH | the relic in Irene's hands |
| s09#15 | 6:39.42 | a priest | spooky_nun@317.2 | MATCH | Father Burke |
| s09#16 | 6:39.98 | and a nun, | spooky_nun@1080.42 | MATCH | Irene |
| s09#17 | 6:40.84 | they found the actual blood of Christ | co_valak0@84.65 | MATCH | the vial of Christ's blood on its chain |
| s09#18 | 6:42.60 | in the abbey, | n1_cz_fight@284.0 | MATCH | the vial held up in the flooded crypt (4:44) |
| s09#19 | 6:43.60 | and even then, Valak gets away, | co_valak0@96.5 | MATCH | Valak's face soaked in the blood |
| s09#20 | 6:45.84 | hiding inside Frenchie. | co_valak0@168.35 | WEAK | Frenchie (the escape into him is in no clip) |
| s09#21 | 6:47.42 | It wiped out a whole abbey, | n1_pray@47.0 | MATCH | overhead: the empty habits on the chapel floor (0:47-0:57) |
| s09#22 | 6:49.39 | and the three people who lived through | n1_hl_abbess@3.0 | MATCH | v6: Burke, Irene and Frenchie walk into the candle-lit hall of tombs (0:03-0:08) |
| s09#23 | 6:51.10 | it only made it because they found | n1_ar_defeats@134.3 | WEAK | Irene takes hold of Valak; the blood in her mouth is not readable at this size |
| s09#24 | 6:52.57 | the actual blood of Christ, | co_valak0@98.2 | MATCH | v6: the blood of Christ bursts red over the water around Valak (1:38.2-1:39.7) |
| s09#25 | 6:54.12 | so alone in your room, you're almost certainly next. | co_valak0@118.0 | MATCH | Valak clawing |
| s09#26 | 6:57.62 | Survival rate, twelve percent. | co_valak0@87.2 | MATCH | Valak close-up holding the vial |
| s10#00 | 6:59.70 | And number one, The Nun Two. | n2_maurice@160.5 | MATCH | Valak's silhouette |
| s10#01 | 7:02.23 | This is Valak at its strongest, | n2_exorcise@2.0 | MATCH | Valak's snarl |
| s10#02 | 7:04.60 | stronger than any demon on this list. | n2_lucy@3.45 | MATCH | Valak, glowing eyes |
| s10#03 | 7:07.05 | It's hunting for the eyes of Saint Lucy, | n2_cz_returns@46.6 | WEAK | the reliquary's glowing rim in a hand, dark |
| s10#04 | 7:09.40 | a holy relic | co_neck_b@191.9 | MATCH | the reliquary held in two hands |
| s10#05 | 7:10.13 | that would make it even stronger, | n2_lucy@9.5 | MATCH | Valak |
| s10#06 | 7:12.06 | and it has been hiding inside Frenchie, | n2_maurice@38.5 | MATCH | Maurice (Frenchie) possessed |
| s10#07 | 7:14.30 | the man who saved Irene, for four years. | n2_maurice@118.5 | MATCH | Maurice grinning, possessed |
| s10#08 | 7:17.44 | It lifts a priest into the air | n2_burn@370.5 | MATCH | Father Noiret rises above the altar (6:10.5-6:12; s00 holds 372.1-373.2) |
| s10#09 | 7:19.09 | and burns him alive, | n2_burn@376.35 | WEAK | Jacques screaming, the burning only as firelight (the burning itself is in s00 and s11) |
| s10#10 | 7:20.77 | snaps the | n2_deliv@138.5 | MATCH | the delivery kid lifted by the throat, feet dangling (2:18.5-2:19.7; cut before the snap) |
| s10#11 | 7:21.45 | neck of a kid making deliveries, | n2_deliv@47.0 | MATCH | the delivery kid in a cap at the shelves, earlier (0:47-0:50) |
| s10#12 | 7:23.33 | and kills the headmistress | n2_altar@89.0 | MATCH | Madame Laurent |
| s10#13 | 7:24.45 | of a boarding school. | n2_cz_goat@283.5 | MATCH | the school dormitory, rows of schoolgirls in nightgowns with Sister Debra between the beds (4:43-4:46.5) |
| s10#14 | 7:25.92 | Sister Irene only survives | n2_lucy@24.0 | MATCH | Irene in mid-air above the fire |
| s10#15 | 7:27.52 | being set on fire | n2_lucy@41.1 | MATCH | Irene burning in mid-air |
| s10#16 | 7:28.73 | because she comes from Saint Lucy's own family, | n2_exorcise@75.0 | MATCH | little Irene in her mother's arms (1:15-1:17) |
| s10#17 | 7:31.42 | and it takes a miracle, | n2_lucy@50.0 | MATCH | Irene unhurt as the fire dies |
| s10#18 | 7:33.18 | wine turning into the blood of Christ, | n2_exorcise@86.0 | MATCH | the wine barrels burst red over Valak (1:26-1:36) |
| s10#19 | 7:35.29 | to drive it out. | n2_exorcise@102.0 | MATCH | Valak goes up in a column of fire (1:42-1:44) |
| s10#20 | 7:36.33 | It burned a priest alive in midair, | n2_burn@378.3 | MATCH | v6: Noiret's body bursts into a fireball above the altar (6:18.3-6:19.4) |
| s10#21 | 7:38.94 | and the only person who ever walked out of its fire | n2_lucy@30.0 | MATCH | Irene burning in mid-air (0:30-0:38) |
| s10#22 | 7:41.61 | was a descendant of Saint Lucy, | n2_burn@136.5 | MATCH | v6: the painting of Saint Lucy in the Tarascon church (2:16.5-2:22) |
| s10#23 | 7:43.47 | so for anyone else in that room, | n2_exorcise@98.0 | MATCH | Valak's rotted face |
| s10#24 | 7:45.26 | the fire wins. | n2_exorcise@122.6 | MATCH | v6: a burst of fire fills the frame (2:02.6-2:04.9) |
| s10#25 | 7:46.41 | Survival rate, five percent. | n2_exorcise@23.15 | MATCH | Valak close-up |
| s11#00 | 7:48.60 | So that's every Conjuring demon, | still_posterwall@1.0 | MATCH | all 9 posters (callback to the cold open) |
| s11#01 | 7:50.70 | from the doll that two teenagers and a little girl | ach_end@82.0 | MATCH | ACH: Mary Ellen, Daniela and Judy together after the lock (1:22-1:26) |
| s11#02 | 7:53.26 | locked back in its case, | ach_end@93.2 | MATCH | ACH: Annabelle locked in the case behind Daniela (1:33.2-1:34) |
| s11#03 | 7:54.83 | to the Valak | n2_burn@373.3 | WEAK | Jacques watching, the burning priest above him is off frame |
| s11#04 | 7:55.67 | that burned a priest alive | n2_burn@375.5 | WEAK | the priest in the flames, mostly fire by mid-shot |
| s11#05 | 7:57.07 | in midair. | n2_burn@377.35 | WEAK | Jacques screaming up at the burning priest |
| s11#06 | 7:58.12 | Which one would you least want in your room tonight? | universe@22.5 | MATCH |  |
| s11#07 | 8:00.58 | Tell me in the comments, along with the horror franchise I should rank next. | universe@136.4 | MATCH |  |
| s11#08 | 8:04.34 | I went through every death in all nine movies to get this ranking right, | universe@151.0 | MATCH |  |
| s11#09 | 8:08.39 | and we're a small channel, so every subscribe really helps. | universe@153.82 | MATCH |  |
| s11#10 | 8:12.06 | Thanks for watching, and if you hear a clap in the dark, don't play along. | universe@157.0 | MATCH |  |
| s11#11 | 8:16.00 | [film] clap | universe@159.6 | MATCH |  |
