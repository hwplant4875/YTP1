# EP1 must-have beats: "Attack on Titan Season 1 through Eren's eyes"

> **SUPERSEDED (user, 2026-10-24): too detailed. The active plan is `EP1_plan_v2.md`, a 3D-timelapse cut built from world events and map data graphics. Keep this file only as a reference for beat details.**

> **Binding user direction (2026-10-24), see `EP1_user_notes.md`:**
> - Every beat where Eren (or another key character) speaks a line gets a dialogue-overlay hold: a slow camera, the frame centre fairly clear, and no instant transition. The user will overlay the faint anime clip and voice there.
> - S14 "Yamero": about 2 s on Eren's outstretched arm, then transition.
> - S18 oath "every last one": about 3 s hold.
> - Grisha's injection (2): injection and key necklace, then a static/glitch/blur transition, because Eren does not remember it.
> - Marco: T46 (Jean finds his body) and H11 (his pyre) are both must.

This is the shot plan for Part 1. It merges the story survey with the critic's additions and corrections, with duplicates removed. Beats are in in-world story order, the order the video plays. The anime's episode number is given for each beat. Flashbacks sit at their in-world year, as `ep1_canon_events.json` already does: 844 Mikasa first, and the stomach shift before the rogue Titan.

**Rules for every beat.** The video is one continuous drone flight with no close-ups. Humans are faceless and read by hair, outfit and colour only. Titans are the stars. Where a "who" must be recognised, give the figure a slightly over-sized read cue: Mikasa's red scarf, the Wings of Freedom cloak decal, Erwin's bright blond hair, Levi's small black undercut, Pyxis's bald head with a white moustache.

**Priority.** `must` means a viewer would notice it was missing. `should` stays in if there is time, or is folded into a neighbouring shot. `nice` is cut first.

**Coverage key.** Entries in the last column refer to these:

- **scene.py**: Shiganshina world (walls, U district, canal, gates).
- **flight.py**: the hill opening and the set-B camera.
- **seq_colossal.py**: tree to gate to Colossal rise, kick, steam fade and inflow.
- **cast845.py**: titans outside the walls, the inflow including the Smiling Titan, the Armored charge.
- **states845.py**: the intact, kicked, armored and night states, the Yeager house crush, smoke, rubble and fires.
- **colossal_asset.py**: the Sidaivan Colossal.
- **Assets on disk:**
  - Colossal x4
  - Armored (PotBin)
  - Female Titan in 5 versions, default pose only, no rig
  - wall cannon (Skipperino)
  - Eren's house (Solarliu)
  - itch.io rigged pure-titan pack, 5 titans
- **Other aot modules:** characters.py (faceless kids), district.py, walls.py, pure_titans.py, shifters.py.
- **NEW**: has to be built.

**Corrections applied from the critic and the wiki check:**

1. **Erwin's casualty warning.** He gives the next expedition's expected death rate for new recruits, about 30%, plus the past toll: most Scouts have died within four years (episode guides quote 60%). The "60% in four years" alone is not the recruit figure. Caption both numbers.
2. **The cadets who stay.** About 20 cadets of the 104th stay. The fandom anime page says 18 and the manga says 21. Model 20; nobody can count them from the sky. Annie (Military Police), Marco (dead) and Eren (in Scout custody) are absent.
3. **Rage-form eyes.** The Attack Titan's eyes are glowing green in every beat. Design bible section 3.6 notes that the wiki says the burning form's eyes are blue. Green is used for consistency, and the owner can override.
4. **The Wall Titan beat.** Pastor Nick and Hange are on the wall top, but Nick's panic and Hange grabbing him open S2E26 (canon file chapter 50). Part 1 shows only two small figures looking down at the face, with no grab and no moving eye.
5. **Added beats:**
   - the 845 night injection (Grisha gives Eren the key)
   - the spoon experiment and the squad biting their hands, placed in the month before the 57th
   - Annie and Armin's "good person" talk before the ceremony
   - Eren's mess-hall speech (nice)
   - Sasha's meat on the wall, folded into the Colossal's return
6. **Merged beats:**
   - Ep10 "boulder plan on the wall" and Ep11 "Eren accepts the gamble" are one wall-top beat.
   - The Ep9 stomach-shift memory is placed in-world before the rogue Titan, so it is not repeated.
   - The Ep9 basement-key flash is a caption, not a shot.

---

## Set 1: Shiganshina, 844-845 (opening)

| # | Ep | Pri | Beat | Who and how to read them from the air | Action from above | Sky camera | Props, states, FX | Covered by / build |
|---|---|---|---|---|---|---|---|---|
| S1 | 6 (fb) | must | 844: Eren saves Mikasa, red scarf | Grisha (tall, dark ponytail, doctor's bag), small dark-haired Eren, Mikasa (black hair, then a red dot of scarf), 3 traffickers, Military Police with lanterns | Grisha and Eren find the cabin. Eren slips off to the hut. Light and shadow flicker in the doorway and the violence stays off-frame. Military Police lanterns arrive. Three walk away together, now with a red scarf. | 60 m, 45°, slow orbit from the cabin to the hut, pull back as they leave, 10 s | two log cabins, cold dusk, light snow, lanterns | NEW small set C (cabins, forest) + characters.py |
| S2 | 1 | must | Cold-open tease: a red hand grips Wall Maria | the Colossal's hand only, faceless crowd frozen in the street | Calm town. A steaming red hand curls over the rim and the crowd freezes. Then a "that morning" card. | 40 m, 250 m inside the town looking south up at the wall, push in, 4 s (flash-forward) | intact gate, steam, warm light | seq_colossal (re-use the hand frame early) + colossal_asset |
| S3 | 1 | should | Scouts fight a Titan in the 845 forest | ~20 green cloaks, bald Shadis in front, one 10-15 m pure titan | The column splits and the Scouts fly on wires toward the titan | 60 m, chase over the treetops, 4 s | gas puffs, grapple lines | NEW: rider kit + ODM FX, itch titan |
| S4 | 1 | must | Eren wakes crying under the tree | child Eren with a firewood frame, Mikasa with a red scarf | Mikasa wakes him and they walk toward the gate | existing high U-overview, then the swoop to the hill end-framing, 20 s | noon, wind in the grass | **DONE** flight.py (shorten from 30 s to 20 s) |
| S5 | 1 | should | Drunk Garrison: "like cattle" | Hannes (blond stubble, red-brown Garrison jacket), Eren, Mikasa | guards drinking at the gate post; Eren argues and stomps off | 30 m oblique, slide along the street, 3 s | bottles, table | NEW: Garrison kit, gate-post props |
| S6 | 1 | must | Scouts return in defeat; Moses's arm; Erwin glimpsed | bald, bearded Shadis; Erwin (blond side part) in the column; thin bloodied column; crowd; kids at the roadside | Bells ring and the gate opens. A short, battered column rides in through a silent crowd. A mother receives a wrapped arm and Shadis bows. Eren hits a heckler, then Mikasa drags him off. | 35 m tracking the column up the avenue, 8 s | bandages, riderless horse, wrapped bundle | flight.py ch3 camera exists; NEW: column + crowd |
| S7 | 1 | should | Family evening; Grisha leaves, basement promise | Grisha with his bag, Carla (long brown hair, apron) at the door | Lit window, chimney smoke; Grisha's cart rolls to the inner gate | rooftop 25 m, slow orbit of the house, 3 s (establishes the house) | intact house | Eren's house asset + states845 YEAGER_HOUSE; NEW cart |
| S8 | 1 | should | Armin bullied; the trio by the canal | blond child Armin, 3 bullies, Eren, Mikasa | The bullies scatter when Mikasa follows, then the trio sits on the canal steps | 30 m glide along the canal, 4 s | canal steps, golden light | flight.py ch5 camera; NEW: kids posed (characters.py) |
| S9 | 1 | must | The Colossal appears over the wall | 60 m skinless red head + hand above the 50 m wall, tiny crowd | flash, tremor, steam plume, head rises, hand grips, crowd looks up | 120 m inside the town looking south, slow pull back, 8 s | lightning bolt, mushroom steam, embers | **DONE** seq_colossal T_RISE + colossal_asset; add the bolt FX |
| S10 | 1 | must | The kick: the outer gate shatters | the Colossal's leg, fleeing specks | the leg swings, the gate bursts, blocks arc over the roofs (one hits the Yeager house), the Colossal vanishes in steam | 150 m, 400 m inside, side-on to the gate, 6 s | ballistic blocks, dust, fading steam column | **DONE** seq_colossal T_KICK/T_FADE + states845 kicked |
| S11 | 1 | must | Pure titans pour through the breach | 5-8 varied grinning titans, crowd streaming north | titans walk in and spread through the streets | 80 m above the breach, tilted toward the inner gate, follow, 5 s | dust, first fires | **DONE** cast845 inflow + seq_colossal T_INFLOW |
| S12 | 1 | must | Carla trapped under the crushed house | Carla's brown hair under the beams, two kids pulling, Hannes running in with blades | the kids heave at the beams; the Smiling Titan comes into view behind | 35 m, slight oblique, descend and hold, 5 s | block in the ruin, dust | states845 yeager crush; NEW: Carla/kids/Hannes poses |
| S13 | 1 | must | Hannes freezes before the Smiling Titan and runs | Smiling Titan (12-15 m, light chin-length hair, fixed grin), Hannes carrying Eren (facing back) and Mikasa | Hannes charges, stops, sheathes his blades, scoops up the kids and runs | 40 m side-on: Hannes runs one way while the titan faces the other, 4 s | none | cast845 Smiling Titan (walk only); NEW: crouch and lift anim, carry pose |
| S14 | 1 | must | Carla eaten; Eren reaches back: "Yamero!" | the Smiling Titan holding Carla up in profile against the sunset; Eren's outstretched arm over Hannes's shoulder | lift, crush, bite: a stylised red silhouette; Eren's arm stretches back as they run | 50 m wide, both in one frame, slow pull away, 6 s | red sunset sky, stylised blood mist | NEW: Smiling Titan lift/bite anim, sun elevation control (sunset) |
| S15 | 2 | nice | Titans eat the townsfolk; crows | pure titans, crowd | titans pick people out of the streets | 70 m sweep, 3 s | fires, crows, smoke | cast845 + states845 smoke |
| S16 | 2 | nice | Eren punches Hannes | the three figures | a brief pass | 30 m, 2 s | none | fold into S17 |
| S17 | 2 | should | Refugee ferries at the inner gate | packed crowd, Armin and his grandfather, the trio reunited on a boat, a cannon on the wall | the crowd crushes onto rail-guided ferries; a cannon fires at a titan | 60 m along the river toward the gate, 4 s (opens S18) | sail-less ferries, cannon smoke | ferries in shot_thumbs.py, port to the set; cannon asset |
| S18 | 2 | must | The Armored Titan bursts the inner gate; "I'll kill every last one" | Armored (15 m, khaki plates, blond crew cut); Eren standing at a boat's bow | sprint up the avenue, cannonballs bounce off, gate impact; crane up as the boats pull away north | 80 m side-on tracking into the impact, crane up to the boats, 8 s | gate debris, hole in Wall Maria | **DONE** cast845 armored + states845 armored; boats NEW |
| S19 | 2 | must | Wall Maria lost: night pull-up to the map | burning town, titan dots spreading north | big pull-up; the Maria belt turns grey on the map | flight.py ch9 move, 8 s | night fires, embers | **DONE** states845 night + flight.py; map set A NEW |

## Set 2: Refugees and training, 845-850

| # | Ep | Pri | Beat | Who and how to read them from the air | Action from above | Sky camera | Props, states, FX | Covered by / build |
|---|---|---|---|---|---|---|---|---|
| R1 | 2 (dream) | should | Night forest: Grisha injects Eren, gives him the key | Grisha (ponytail, glasses), child Eren, lantern | the key goes on, the needle glints, Eren falls | 45 m through a canopy gap, top-down to 50°, 4 s | lantern, cart, syringe glint | NEW tiny forest set (re-use set C trees) |
| R2 | 2 | should | Refugee storehouse: Eren wakes with the key; ration lines | the trio, a key glint on Eren | tents, queues; Armin pulls Eren away from a soldier | 50 m pass over the tents, 3 s | tents, carts | NEW set D (storehouses) |
| R3 | 2 | should | 846 "retake Wall Maria": 250,000 sent out, about 100 return | a vast grey column, the trio watching from the wall | time-lapse of the column filing out of a Rose gate | 200 m high, pull out, 4 s | grey sky; caption "250,000 → ~100" | NEW gate set (re-use walls.py) + crowd instancer |
| R4 | 2-3 | must | 847: the trio enlists in the 104th; Shadis's initiation | ~200 brown-jacket cadets in rows, bald Shadis pacing | rows at attention; Shadis walks the line | 40 m slow tilt down, 5 s | barracks, dirt field, forest | NEW set D camp + cadet kit |
| R5 | 3 | should | Sasha's potato and her sunset laps | brown ponytail; the lone runner circling the field | she offers half a potato, then runs laps at sunset | 35 m along the line, then a wide sunset shot, 4 s | potato (just a pose) | camp set + time-of-day light |
| R6 | 3 | should | Balance rig: Eren fails, then succeeds on swapped gear | Eren upside down in a ring of cadets | he hangs upside down, then upright, and the ring cheers | 25 m slight orbit, 3 s | wooden frame | NEW rig prop |
| R7 | 3 | nice | ODM forest training and wooden titan cut-outs | Eren and Mikasa side by side | flying the course, slashing the dummies | 30 m chase, 3 s | cut-outs with leather napes | camp forest |
| R8 | 4 | should | Annie throws Eren, then Reiner | Annie (blonde bun, hoodie), big blond Reiner | sweep, throw | 25 m oblique, 3 s | wooden knives | camp set; seasons timelapse in the same orbit |
| R9 | 4 | must | 850 graduation: top-10 ranking, heart salute | torch-lit ranks, Shadis on a stage, the top ten in front (Mikasa first, Eren fifth) | names called; ranks salute together | 50 m crane down over the torches, 6 s | torches, stage, night | NEW stage (**build once, re-use for the ceremony H15**) |
| R10 | 4 | nice | Eren's mess-hall speech wins Thomas and Mina over to the Scouts | lit hall | lit windows; Eren storms out | 35 m pass, 2 s | lanterns | fold into R11 |
| R11 | 4 | should | The trio under the stars; all three choose the Scouts | three figures on the steps, the wall behind | a shooting star crosses over the wall | 40 m behind and above, tilt up, 3 s | stars, a streak | camp set |

## Set 3: Trost, 850

| # | Ep | Pri | Beat | Who and how to read them from the air | Action from above | Sky camera | Props, states, FX | Covered by / build |
|---|---|---|---|---|---|---|---|---|
| T1 | 4 | should | The Scouts ride out of Trost: Erwin, Levi, Hange; Hannes now a captain | blond Erwin at the head, small black-haired Levi, Hange's ponytail; the trio and Hannes in the crowd | a cheering crowd; the column exits the south gate | 40 m along the street, rise over the gate, 4 s | green cloaks, open gate | NEW Trost (district.py re-use) + rider kit |
| T2 | 4-5 | must | The Colossal returns over Trost (Sasha's meat folded in) | cadets as specks on the cannon rail, Eren standing alone on the crest | 2 s of the cannon crew (meat), then lightning, the head beside them, a steam blast throws cadets off; they grapple back; Sasha saves Samuel | 40 m along the wall top, then 80 m out over the field looking north at the wall face, 7 s | lightning, steam blast, cannons | seq_colossal re-staged at Trost + cannon asset |
| T3 | 4-5 | must | The Trost gate is kicked in | the Colossal's leg | gate hole, debris into the district | 150 m wide side angle, 4 s | 8 m hole | seq_colossal kick + states845 breach_gate on the Trost gate |
| T4 | 5 | must | Eren duels the Colossal on the wall | Eren as a speck on wires | the arm sweeps the cannon rail; Eren runs up the arm to the nape and slashes; steam, and he cuts empty air | 100 m orbit behind at nape height, 6 s | broken cannons, gouge, steam burst | NEW: Colossal arm-sweep keyframes, ODM wire FX |
| T5 | 5 | should | Troops mobilise; Mikasa sent to the rear ("Don't die") | squads in the square, Mikasa leaving, civilians streaming north | assembly and evacuation | 60 m over the square, 3 s | carts | Trost set + crowd |
| T6 | 5 | must | Squad 34: Thomas eaten, Eren loses his leg | 6 cadets over the rooftops, the long-limbed grinning Abnormal | the Abnormal leaps and takes Thomas; Eren charges, is bitten and falls on a roof | 45 m following across the roofs, 6 s | small blood on the tiles | itch rigged titans (jump anim NEW) |
| T7 | 5 | must | Eren saves Armin and is swallowed | bearded ~7 m titan, Armin thrown onto the roof, Eren's raised arm | Eren throws Armin out and holds the jaw; it snaps shut; the arm is severed | 40 m slight oblique, titan head and Armin in frame, pull up, 6 s | severed arm (tiny) | itch titan + NEW mouth open/close |
| T8 | 6 | must | Mikasa clears the jammed inner gate | red scarf; merchant's cart wedged in the gate; sea of civilians; ~7 m Abnormal | the Abnormal sprints at the crowd; one nape pass; she lands on the cart; the crowd floods through | 50 m high three-quarter down the street into the gate, push in, 6 s | huge cart, steam from the corpse | Trost north gate + crowd + cart NEW |
| T9 | 6 | should | Retreat bell; Mikasa turns south alone | red scarf against the soldiers climbing the wall | everyone goes up the wall; she flies the other way | 80 m tracking her wire arcs, 3 s | bell tower | ODM FX |
| T10 | 7 | should | Stranded cadets; titans at the supply HQ | cadets crouched on the roofs, titan heads at the HQ windows | some try for the wall and are grabbed | 100 m establishing orbit of the HQ, 4 s | tall HQ tower | NEW supply HQ (with cutaway roof) |
| T11 | 7 | must | Armin tells Mikasa Eren is dead; "I am strong"; the charge | blond Armin hunched, Mikasa standing, Jean | stillness, then she launches alone; Jean shouts and everyone follows | 40 m low side, then rise and follow the stream of gas trails, 6 s | red scarf, many gas trails | ODM FX (multi) |
| T12 | 7 | must | Mikasa out of gas, gives up, then hears "Fight!" | small red scarf in the street, a ~10 m titan's shadow crossing her | crash onto a stall; she drops her blades, then grips them again | 30 m top-down, shadow crossing, 5 s | collapsed awning, empty canisters | market props |
| T13 | 9 (in-world here) | must | Inside the stomach: Eren's first shift | a huge arm bursts from a pure titan's mouth | lightning, the 15 m Attack Titan tears free and stamps the titan flat | 50 m side view, 5 s | bolt, steam explosion | NEW **Attack Titan asset** (shifters.py) + shift FX |
| T14 | 7 | must | The rogue Titan kills titans | 15 m, long dark hair, pointed ears, glowing green eyes; Mikasa below | punch to the jaw, stamp, roar; a head flies into the bell tower; it ignores the humans | 60 m three-quarter slow circle, 7 s | head stuck in the bell tower, stamp shockwave | Attack Titan + fight anims NEW |
| T15 | 7 | should | Armin gives Mikasa his gas; plan to use the Titan | Armin, Mikasa, Connie on a roof, the Titan fighting behind | canisters swapped; they point toward the HQ | 50 m wide, 3 s | canisters | fold into T14 tail |
| T16 | 8 | should | Jean leads the dash; they crash through the HQ windows | the cadet swarm | through the gap; glass bursts; some snatched | 70 m swoop with the swarm, 4 s | glass, gas trails | supply HQ |
| T17 | 8 | should | The rogue Titan arrives at the HQ | Mikasa and Armin flying ahead as bait | it pounds the titans around the HQ | 80 m wide orbit, 3 s (shares a shot with T16) | dust, cracked walls | Attack Titan |
| T18 | 8 | must | Armin's supply-room plan: lift, eye shots, seven drop from the ceiling | a ring of cadets on the lift; seven 3-4 m titans; seven strikers in the rafters | volley of muzzle flashes into the eyes, the drop onto 7 napes, Mikasa and Annie save Sasha and Connie, refuel | 25 m top-down through the cutaway roof to read the ring, lean to 45° for the drop, 8 s | gun-smoke cloud, steam, canisters | NEW HQ interior + cutaway, muzzle FX, 7 small titans (itch) |
| T19 | 8 | nice | Cadets burst out refuelled | gas-trail burst | they fly to the wall | 90 m pull back, 2 s | trails | fold into T20 opening |
| T20 | 8 | must | The rogue Titan kills Thomas's eater, roars, collapses | armless Attack Titan, the grinning Abnormal, rooftop watchers in the foreground | pinned and gnawed, it bites through the Abnormal's neck, swings the body, final roar, falls | 60 m three-quarter orbit, 7 s | steaming stumps, heavy steam | Attack Titan anims |
| T21 | 8 | must | Eren emerges from the nape; Mikasa sobs | tiny Eren in the steaming nape, Mikasa holding him, Armin, cadets on the roofs | Eren slides out with his limbs back; she hugs him | 35 m slow descending orbit through the steam, wide, 7 s | huge steam cloud, flesh strands | steam sim + nape strands NEW |
| T22 | 9 | nice | Erwin sees titans heading north and turns back | column on the plains | Erwin orders the return | 150 m, 3 s | distant titans | cut, or put in a map inset |
| T23 | 9 | must | Woermann's ring: "human or Titan?" | heavyset Woermann, a ring of Garrison blades, Mikasa standing over Eren, cannons turning on the wall | ring closes; cannons swing round | 60 m, 50°, ring composition, 5 s | harpoon nets holding titans at the north gate (background) | Trost north wall + cannon asset |
| T24 | 9 | must | The cannonball near-miss; Eren's half-shift | ribcage and one arm, no skin, curled over Mikasa and Armin | the cannon fires; the skeleton half-Titan erupts, catches the ball, steam pillar blooms | 70 m, wall-side, cannon in the foreground, rise with the steam, 7 s | muzzle flash, ball in the skeletal hand, white pillar | NEW half-Titan skeleton mesh |
| T25 | 9-10 | should | Key flash; Eren's two choices; Armin decides | the steam dome | hold on the dome (caption: "the basement") | 40 m hold, 3 s | dissolving ribcage | fold into T24 tail |
| T26 | 10 | must | Armin walks out of the steam and salutes | a lone small blond figure, fist on heart, against white steam; ring of blades | he drops his blades and salutes; Woermann raises his hand again | 45 m frontal-high, Armin centred, 6 s | steam column, reloaded cannon | characters + steam |
| T27 | 10 | must | Pyxis stops the second shot | bald, white moustache, commander's coat | he grabs Woermann's arm | 50 m drift from the street up to the wall top, 4 s | cannon stands down | Pyxis kit NEW |
| T28 | 10-11 | must | Wall top: the boulder plan; Eren accepts | Pyxis, Eren, Mikasa, Armin on the crest; Hannes's squad further along | Armin points to the boulder, Eren looks over the titan-filled district and agrees | 120 m behind the group, tilt over the city to the boulder and on to the breach, 6 s | boulder (13 × 11 × 9 m), 8 m hole | Trost + boulder prop NEW |
| T29 | 11 | must | Desertions; Pyxis's speech brings the army back | two specks on the wall edge, a crowd below with streams peeling away, then flowing back | deserters leave; the speech; they return to their posts | 60 m inner side looking at the wall, slow push in, 8 s | long wall shadows | crowd flow instancer NEW |
| T30 | 11 | should | Plan map: lure corner, escort, boulder, breach | overlay | dashed escort route | 300 m straight down, 4 s | map overlay | HUD overlay (hud.py) |
| T31 | 11 | nice | "I'm not your little brother" | the trio splitting into two lines | the teams part | 50 m, 3 s | none | fold into T32 |
| T32 | 11 | should | Green flare: escort runs the rooftops; the lure cannons start | ~10 specks on wires, Rico's silver hair | rooftop dash; cannon smoke at the far corner | 40 m chase, 4 s | green smoke | smoke-signal system NEW (re-used in the 57th) |
| T33 | 11 | must | Eren shifts at the boulder and swings at Mikasa | Attack Titan, boulder, Mikasa leaping clear | lightning, Titan forms, looks at the boulder, punches the roof where she stood | 70 m three-quarter, boulder + Titan, hold, 6 s | lightning, roof debris | Attack Titan + boulder |
| T34 | 12 | must | Mikasa on his face; the Titan punches itself | red scarf on the cheek | the self-punch; it slumps steaming against the boulder | 50 m side-on, 5 s | crushed steaming face (silhouette) | Attack Titan anims |
| T35 | 12 | must | Red flare: mission failed; Ian orders them to defend Eren | red column above central Trost, the wall far off | flare up; Armin leaves the wall alone | pull up to 200 m, red column + wall in frame, 4 s | red smoke | smoke system |
| T36 | 12 | should | The lure corner bleeds | titans packed against the corner, cannon smoke | soldiers snatched off the wall face | 120 m wide oblique, 4 s | cannon smoke, dust | itch titans (crowd) |
| T37 | 12 | should | Elites and Mikasa hold the ring around the slumped Eren | titans converging from several streets | nape kills, steam puffs | 90 m slow orbit of the boulder, 5 s | steam | shares the orbit with T38 |
| T38 | 12 | must | Armin stabs the nape: "Because I was born into this world" | blond Armin kneeling on the nape | blade in, steam, the eyes light up and the Titan rises | 35 m three-quarter rear of the nape, pull back as it rises, 6 s | blade, steam, optional sky flame flicker | Attack Titan (rise anim) |
| T39 | 12-13 | should | Jean's gear fails; Marco saves him (Marco's last moment) | Jean running; Marco (dark hair, freckles); Connie; Annie's clean nape cut | Jean on foot, buckling the dead man's gear; Marco distracts a titan; all four lift onto the wall | 50 m arc over the building, 4 s | Annie's steam burst | itch titans |
| T40 | 13 | must | Eren lifts the boulder and walks to the gate | Titan bent under the boulder, Mikasa and Armin flying alongside, soldiers on every roof | step by step up the main street, dust at every step | rising crane at 100 m, behind to side view, breach ahead, 10 s | dust, steam trail | Attack Titan carry anim + boulder |
| T41 | 13 | must | Ground decoys: Mitabi and Ian die | figures on foot, titan fists rising | Mitabi crushed in a hand, Ian grabbed; the boulder Titan crosses behind | 70 m fixed side view, carrier in the background, 6 s | silhouettes, no gore | itch titans grab anim NEW |
| T42 | 13 | must | Rico and Mikasa clear the last titan; the boulder seals the gate | Rico slashes the eyes, Mikasa the nape; the drop | impact shockwave, the hole plugged, the Titan slumps | 120 m from inside toward the gate, push in on the drop, 7 s | dust blast from the gate | boulder + states845-style dust burst |
| T43 | 13 | must | Yellow flare: "They did not die in vain" | yellow column, sealed gate, wall | Rico fires; Pyxis sends rescuers | pull up to 250 m, 4 s | yellow smoke | smoke system |
| T44 | 13 | must | Levi's entrance: the Wings of Freedom | small Levi standing on a fallen titan, cloak emblem toward the camera; Mikasa holding Eren | two titans fall in a blur; he lands with his back to them | 30 m behind and above Levi, emblem centred, 6 s | over-sized cloak decal, steam | NEW Levi kit + spin-cut FX |
| T45 | 13 | should | Mop-up; two titans captured alive | green cloaks on roofs, steam plumes going out one by one, two titans staked | Day 0-1 time-lapse | 400 m high time-lapse, 4 s | stakes, wires | steam plume instancer |
| T46 | 13 | must | Corpse collection: Jean finds Marco | a lone still figure at a slumped body, medic, stretchers, Annie and Reiner nearby | slow overhead drift ending on Jean | 40 m overhead drift, 5 s | sheeted rows, carts, grey light | props |

## Set 4: Trial, Survey Corps HQ and the 57th expedition, 850

| # | Ep | Pri | Beat | Who and how to read them from the air | Action from above | Sky camera | Props, states, FX | Covered by / build |
|---|---|---|---|---|---|---|---|---|
| H1 | 13-14 | should | Dungeon: Erwin and Levi; Eren says "Survey Corps" | lit cellar grate (the key is in Erwin's hand) | caption only | 60 m descent to the courthouse, 3 s | lit low window | NEW courthouse exterior |
| H2 | 14 | nice | Erwin and Pyxis on the morning wall; Hange and Mike escort Eren | two figures on the wall; Hange's goggles, tall Mike | none | 40-70 m, 3 s | sealed gate below | cut |
| H3 | 14 | should | The trial: MP vs Survey Corps | kneeling chained Eren at the centre, Zachary on the high bench, factions either side | Nile, Pastor Nick, the merchant, Mikasa's testimony; "Just let me fight!" | 25 m top-down through the skylight or cutaway roof, 4 s | courtroom cutaway | NEW courtroom cutaway |
| H4 | 14 | must | Levi beats Eren; Erwin's proposal wins | small Levi kicking, Mikasa held back, Erwin's raised hand | kick, tooth; Erwin raises his hand; the gavel | same skylight, held, 5 s | tooth | shares the set with H3 |
| H5 | 14 | nice | Tooth regrown | none | none | 2 s | none | cut |
| H6 | 15 | must | Ride to the old castle with Squad Levi | 6 green cloaks: Levi in front, Petra (ginger bob), Oruo, Eld (blond top-knot), Gunther, Eren | the castle grows on the horizon; Oruo bites his tongue | 100 m long track, 6 s | stone castle, Wings banners | NEW set F castle + rider kit |
| H7 | 15 | nice | Cleaning the castle | buckets, rugs airing | dust out of the windows | 60 m orbit, 3 s | rugs | fold into H6 tail |
| H8 | 15 | should | Hange's all-night Titan talk: Sawney and Beane | one lit window, night to dawn | time-lapse | 80 m time-lapse, 4 s | lit window, sky gradient | castle + sky |
| H9 | 15 | must | Sawney and Beane murdered: "Who is the enemy?" | two steaming skeletons, Hange on her knees, Erwin beside Eren | dawn, the crowd arrives, Hange screams; Erwin's quiet question | 70 m push in, ending on Erwin and Eren, 6 s | skeletons, broken stakes, wires | NEW stockade + 4 m and 7 m skeleton meshes (re-use the half-Titan skeleton) |
| H10 | 16 | should | Gear inspection | rows of cadets, Annie calm, Connie fumbling | MPs check every ODM rig | 60 m, 35°, drift from the skeletons to the rows, 4 s | racks of gear | shares the stockade with H9 |
| H11 | 16 | must | Jean at Marco's pyre | a lone figure at one of several glowing pyres, Connie and Sasha nearby | Jean holds a bone and says he will join the Scouts | 80 m pull back at 30°, push in to 40 m, 6 s | pyres, embers, smoke columns, dusk | NEW pyre FX (fire + embers from states845 night) |
| H12 | 16 | should | Annie and Armin before the ceremony: "You're a good person" | blonde bun + blond bob; cadets streaming past | they talk; Annie peels off toward the MP side | 40 m, 45°, one figure walks off alone, 3 s | distant torches being lit | ceremony set |
| **H13** | 16 | **must (top)** | **Erwin's recruitment speech: the basement, the casualty warning** | Erwin: bright blond side part catching the torchlight, tall, Survey Corps jacket and green cape, against a Wings of Freedom banner; ~200 cadets; Annie, Marco and Eren absent | Erwin names the Jaeger basement in Shiganshina as the goal and gives the warning: ~30% of recruits die on the next expedition, most within four years. He tells those who want to leave to go. The crowd drains into the dark in 2-3 visible waves. Some who stay tremble, cry or retch (Connie, Sasha, Jean). | 50 m, 40° oblique from behind the crowd toward the stage, slow descent to 30 m as the crowd drains, 10 s | stage, braziers, torches on poles, banner, warm pool of light | NEW **ceremony set** (stage from R9) + crowd drain instancer + Erwin kit |
| **H14** | 16 | **must (top)** | **About 20 stay and salute: "Shinzou wo sasageyo!"** | small block: Mikasa (red scarf), Armin, Jean (two-tone undercut), Connie (buzz cut), Sasha (ponytail), Reiner (broad, blond), Bertholdt (tallest), Christa (small, blond), Ymir (tall, freckles) + ~11 others; every right fist on the heart | Erwin asks if they would die if ordered; they say they don't want to but stand firm; he calls them Scouts and leads the cry; all fists hit their chests together | 35 m slow orbit from the stage side, the empty ground between them, end over Erwin's shoulder, 9 s | trampled empty ground, cooler light, faint mist, flickering torches | same set; NEW salute pose |
| H15 | 16 | should | Friends reach the castle; green cloaks; Eren learns Marco is dead | courtyard of small figures putting on green cloaks; Levi by the wall | Jean says they are counting on him | 70 m, 45°, drift, 4 s | cloaks in the wind | castle set |
| H16 | 19 (fb, in-world here) | should | Spoon experiment: half-arm in the courtyard; the squad bites their hands | a huge steaming arm by an overturned table, a ring of blades, Levi between them | well test fails; the arm erupts; blades drawn; Hange sees the spoon; the four bite their hands | 50 m slow orbit of the courtyard, 5 s | dry well, arm mesh, tiny spoon | Attack Titan arm (partial) + castle |
| H17 | 17 | must | The 57th rides out of Karanes | Erwin at the head, Squad Levi in the centre around Eren | bells, gate rises, the column pours out; support riders lure a small titan | 150 m over the half-circle wall descending to 60 m outside the gate looking back, 7 s | portcullis, dust trail, dawn sun | NEW Karanes (district.py) + 128-rider instancer |
| H18 | 17 | must | Long-range scouting formation with signal smoke | dozens of rider groups in a kilometres-wide arc, wagons in the centre | red smoke on the flanks for titans; a green flare from the centre relayed down the line; the arc bends | 300-400 m near top-down tilting to 60°, drift forward, 9 s | red/green/black smoke columns, dust, ruined old town behind | NEW plains + formation layout + smoke system |
| H19 | 17 | nice | Sasha and the crawling titan | an emaciated titan on all fours | it chases her group; lured into a tree | 60 m, 3 s | ruined village | cut |
| H20 | 17 | must | The Female Titan wrecks the right wing | 14 m lean sprinter, short blonde hair, red muscle; horde behind; black smoke one column after another | the right wing collapses; Ness and Cis struck down from the air | 120 m, 40°, tracking alongside her stride, drop to 60 m for the strike, 8 s | black smoke, riderless horses | NEW **Female Titan rig** (Sketchfab mesh, auto-rig, sprint cycle) |
| H21 | 17 | must | She lifts Armin's hood and spares him | Armin lying by his horse, the kneeling Female | fingertip lifts the hood, she runs on | 45 m, 45°, pull up as she leaves, 5 s | horse, black smoke behind | Female crouch pose |
| H22 | 17 | must | Reiner and Jean attack; Armin's bluff | three hooded riders | she freezes at the bluff, grabs Reiner, he cuts his way out, she turns toward the centre | 70 m, 40° orbit, end on her running toward the far smoke, 6 s | blood/steam spurt | Female grab anim |
| H23 | 18 | should | Purple flare; Christa brings horses | a small blonde rider leading horses | a purple column; ride after the formation | 80 m, 50°, 3 s | purple smoke | smoke system |
| H24 | 18 | must | Green flare: course change into the Forest of Giant Trees | arc bends; only the centre column enters; Scouts perched on branches above titans at the edge | course change, then the canopy edge with titans clawing the trunks | 250 m banking with the turn, down to 100 m along the canopy edge, 7 s | 80 m+ trees, forest road | NEW set G giant forest (instanced trunks) |
| H25 | 18 | must | The Female bursts out behind Squad Levi | riders on the road between huge trunks, the Female closing, Scouts on wires swatted | black flare, crash onto the road, Scouts smashed into trees, Levi's sound flare | 60 m behind and above her, both in frame, 8 s | black smoke, sound-flare puff, blood splats on bark | Female sprint + swat |
| H26 | 19 | must | Eren's choice: trust the squad | Eren in the middle of the diamond, his hand at his mouth, the titan closing | he lowers his hand; they ride on while Scouts die behind | 40 m side, slightly ahead, matching speed, 6 s | none | rider kit |
| H27 | 19 | must | The harpoon trap fires and pins the Female | Female stopped mid-stride; Erwin and veterans high in the branches; Levi lands above her | volleys of cable spears from every side; the web holds her upright | 70 m, 30° swinging into an orbit, end wide on the cable web, 8 s | launcher banks, cables, launch smoke, skid dust | NEW **cable-volley FX** + launcher props |
| H28 | 20 | should | Hardened nape; Levi's taunt | Levi crouched on her head, Mike and Erwin on branches | blades shatter on crystal; explosives called for | 35 m orbit of her neck, 4 s | opal hardening patch, blade glints | hardening shader NEW |
| H29 | 20 | must | Her scream: titans swarm in and eat her | lines of titans streaming in from all sides past the Scouts | swarm, devour, steam column above the canopy; Erwin orders the retreat | 200 m, fast drop to 80 m, follow the lines in, end on the swarm, 8 s | shaking branches, steam column, blue retreat flare | itch titans en masse + run cycle |
| H30 | 20 | must | Hooded figure escapes and kills Gunther | a small cloaked figure between the trunks; Gunther hanging limp from his wire | swoop past; Eld shouts; a lightning flash in the trees | 50 m above the road, follow, hold on Gunther, 6 s | steam trail, limp body on the cable | ODM FX |
| H31 | 21 | must | Second shift on the forest road | riders in a diamond; lightning column behind | the Female lands on the road and charges | 70 m over the canopy gap looking back, 35°, tilt to the flash, 6 s | yellow lightning, steam through the canopy | shift FX |
| H32 | 21 | must | The squad blinds her | Petra and Oruo at eye level, Eld circling, Eren looking back | both eyes cut; she slumps against a trunk covering her nape | 45 m, 40° slow orbit, Eren at the frame edge, 6 s | steam from the eyes | Female slump pose |
| H33 | 21 | must | Squad Levi wiped out | Eld in her jaws, Petra crushed against the trunk, Oruo's blades shatter on the nape | three deaths read one after another; hold on Petra upside down at the trunk base | same orbit pulled out to 60 m, hold, 10 s | crystal nape, minimal dark blood | Female bite/stamp/kick anims |
| H34 | 21 | must | Eren's rage shift: "I'll kill you!" | lightning column on the road; Attack Titan vs Female 60 m apart; his horse bolts | roar, charge | 80 m, 35°, fast push in from the canopy, 6 s | lightning, steam dome, leaves blasting out | Attack Titan + shift FX |
| H35 | 21 | must | Titan duel: broken fists, the uppercut | both full-body; crystal flashes on her fist and shin | blows trade, his fists break, his mouth is torn; he slams her into trunks, uppercut, mounts her | 55 m, 45°, 90° orbit, 12 s | splintered trunks, steam | NEW fight mocap/keyframe set (both rigs) |
| H36 | 21 | must | Stance recognised; head kicked off; Eren taken | Annie's raised guard; the kick arc in silhouette | he hesitates; roundhouse; head flies; she bites him out of the nape and runs | 70 m side-on, follow her 3 s, 8 s | headless body sinks into steam | fight set |
| H37 | 21 | should | Mikasa gives chase, Levi behind | red scarf and small Levi on wires | none | 50 m chase from behind her, 4 s | gas trails | fold into H38 opening |
| H38 | 22 | must | Levi's whirlwind rescue | spiral of steam cuts down her body; Levi carrying slimed Eren | eyes and arms cut faster than she can harden; he pushes Mikasa clear and cuts Eren from her mouth | 40 m, 45°, slow orbit following the spiral, 8 s | spiral cut FX, wires | spin-cut FX (from T44) |
| H39 | 22 | should | The Female sheds a tear | her whole upper body against the trunk, a glint on her cheek | Levi and Mikasa fly off | 35 m three-quarter front, drift back, 4 s | highlight on the cheek | fold into H38 tail |
| H40 | 22 | must | Bodies dumped to escape the titans | column of horses and wagons, two titans behind, white shrouds tumbling | bodies thrown; titans stop to pick them up; the column gets away | 90 m behind and above, 30°, crane up, 7 s | shrouds, late light | rider kit + itch titans |
| H41 | 22 | nice | Eren dreams of 845 (he has become the defeated Scouts) | desaturated cut to the S6 framing | crossfade | 4 s | re-use S6 | optional re-use of S6 frames |
| H42 | 22 | must | Return to Karanes in disgrace; Petra's father | short torn column, Erwin in front, Levi with a man walking beside his horse, Eren slumped on a wagon | jeering crowd lines the street; two children wave | 50 m, 40° lateral track, 8 s | empty saddles, torn cloaks | Karanes set + crowd |
| H43 | 22 | should | Erwin summoned; route to Stohess | map line Karanes → Stohess | none | 300 m map crane, 5 s (the set transition) | map overlay | set A map + hud.py |

## Set 5: Stohess, 850 (finale)

| # | Ep | Pri | Beat | Who and how to read them from the air | Action from above | Sky camera | Props, states, FX | Covered by / build |
|---|---|---|---|---|---|---|---|---|
| X1 | 23 | should | Annie's Military Police life in Stohess | blonde bun + white hoodie under the MP unicorn jacket, Hitch, Marlo | she walks the rich streets | 120 m establishing drift toward Wall Sina, down to 40 m, 5 s | cream stucco, mansards, spires | NEW set H Stohess (district.py, rich variant) |
| X2 | 23 | should | Convoy enters; Jean disguised as Eren | carriage, MPs, two hooded figures dropping into an alley | the door opens briefly, two slip away | 60 m, 40°, track, then pan to the alley, 4 s | crowded avenue | Stohess + rider kit |
| X3 | 23 | should | Armin asks Annie for help | four small figures in quiet alleys | they walk together | 35 m, 50°, follow, 3 s | empty alleys | none |
| X4 | 23 | must | Annie refuses the tunnel: the reveal | Annie alone in sunlight at the top of the stairs; three in the shadow below | the confrontation; her laugh ("you won your bet") | 25-30 m, 60° down, hold, 6 s | hard light/shadow split | NEW stairwell + tunnel mouth |
| X5 | 23 | must | Pinned; ring blade; the Female shifts in Stohess | Annie under a pile of green cloaks | flare; Scouts pin and gag her; the ring blade; lightning blows the street apart; Mikasa throws the boys into the tunnel | pull from 40 m to 150 m as the blast goes off, 6 s | flare, lightning column, rubble ring | shift FX + Female |
| X6 | 24 | must | Eren can't transform | the Female's foot through the street; Eren small at the bottom of the hole | stomp kills two Scouts; Mikasa and Armin fly up | 40 m looking down into the hole, 5 s | collapsed paving, light shaft | NEW street-cave-in state |
| X7 | 24 | should | Mikasa harasses her; the roof kicked in on Eren | red scarf around her head | rooftops collapse | 55 m, 40°, 60° orbit, 4 s | dust | Female kick |
| X8 | 24 | should | Erwin held at gunpoint by Nile | calm blond Erwin in a ring of MP rifles; Jean unmasked; dust behind | none | 45 m, 45°, ring, 3 s | rifles | crowd kit |
| X9 | 24 | should | Hange's restraint-net trap | Hange's goggles on a roof, cables converging, the Female netted in the street | pinned for a moment, then she kicks free | 60 m down the street, 45°, 5 s | barbed net, cables | cable FX (from H27) |
| X10 | 24 | must | Eren, impaled under the rubble, remembers Armin and shifts | lightning column from under the street | he pushes off the beam; the Attack Titan sprints out of the steam and punches her into a facade | 90 m, 35°, fast push in after the flash, end on the punch, 7 s | orange flash from below, facade burst | Attack Titan + destructible facade NEW |
| X11 | 25 | must | Church collapse; rampage toward Wall Sina | two titans, civilians scattering, Hitch and Marlo on a roof | she crashes onto the Wall-cult church; chase through the crowds; he throws her into a building | 150 m wide tracking flight along the avenue, 10 s | spire falling, rubble trench, dust | NEW church + rubble-trench state |
| X12 | 25 | nice | Erwin handcuffed | none | none | 40 m, 2 s | none | cut |
| X13 | 25 | must | Eren beaten down, then the rage form overpowers her | her boxing guard and hardened shins; Eren darkened, steaming, flesh strands, **glowing green eyes** | lower leg kicked off, pounded down; he flares, rises, tackles her from behind, smashes her face into the ground | 60 m, 40°, 120° orbit during the flare, 10 s | burn shader, flesh strands, craters | NEW burning-state material on the Attack Titan |
| X14 | 25 | must | Annie climbs Wall Sina | the Female two-thirds up the 50 m face, Eren reaching from the base, Garrison specks on top | hardened fingers punch handholds; she tears free, losing a leg | 70 m out from the wall, 40 m high, rising with her, 7 s | handholds, cracked stone | walls.py Sina + climb anim |
| X15 | 25 | must | Mikasa cuts her fingers: "Annie, fall" | red scarf on her face near the top | spin; fingers cut; she falls backward | wall-top level 55 m, 60 m out, three-quarter side, 6 s | finger steam, stone chips | Female fall anim |
| X16 | 25 | must | Eren rips into the nape and sees Annie crying | the Attack Titan over the Female; tiny Annie in the nape | he tears off the head and arm, bites open the nape, freezes | 45 m, 50°, slow descent, no close-up, 6 s | steam, fusing strands | fight set |
| X17 | 25 | must | Annie in crystal; Levi cuts Eren out | faceted ~2.5 m egg; small Levi; Jean striking it; Hange's net | crystal grows; the bodies fuse; Levi cuts Eren free; the crystal is netted away | 35 m, 45°, slow pull back, 6 s | crystal shader (bible 3.7), wire net | NEW crystal mesh |
| X18 | 25 | must | A Titan in the Wall (final shot) | the huge static face in the cracked Wall Sina; two small figures on the wall top (Hange, Pastor Nick) | stone crumbles away; hold; end card. No grab and no moving eye (S2E26). | push in from 150 m out at 50 m height to 80 m out, hold, 8 s + end card | falling stone, evening light | NEW wall-face sculpt (re-use a pure-titan head, scaled) |

---

## Beat count

| Priority | S | R | T | H | X | Total |
|---|---|---|---|---|---|---|
| must | 12 | 2 | 29 | 26 | 11 | **80** |
| should | 5 | 7 | 14 | 12 | 6 | **44** |
| nice | 2 | 2 | 3 | 5 | 1 | **13** |
| all | 19 | 11 | 46 | 43 | 18 | **137** |

## Timing table (target 14:00 = 840 s, 30 fps)

Every `must` beat has its own seconds. Some `should` beats are kept because they cost 2-4 s, or because they share a `must` shot (marked +). "Bridge" is drone travel or a map climb between places. All `nice` beats are cut except where noted.

| Block | Shots (beats sharing a shot are joined with +) | Seconds |
|---|---|---|
| Title + map push | title card over the island map | 8 |
| 844 | S1 | 10 |
| Shiganshina 845 | S2 4 · S4 20 · S6 8 · S7+S8 (should) 5 · S9 8 · S10 6 · S11 5 · S12 5 · S13 4 · S14 6 · S17+S18 10 · S19 8 | 89 |
| Refugees and training | bridge 4 · R1 3 · R3 4 · R4 5 · R5+R8 (seasons orbit) 5 · R9 6 · R11 3 | 30 |
| Trost: fall | bridge 4 · T1 3 · T2 7 · T3 4 · T4 6 · T6 6 · T7 6 | 36 |
| Trost: Mikasa and the HQ | T8 6 · T11 6 · T12 5 · T13 5 · T14+T15 8 · T16+T17 4 · T18 8 · T20 7 · T21 7 | 56 |
| Trost: human or Titan | T23 5 · T24+T25 8 · T26 6 · T27 4 · T28 6 · T29 8 · T30 3 | 40 |
| Trost: the boulder | T32 3 · T33 6 · T34 5 · T35 4 · T36+T37 5 · T38 6 · T39 3 · T40 10 · T41 6 · T42 7 · T43 4 · T44 6 · T45 3 · T46 5 | 73 |
| Trial and castle | bridge 4 · H1 2 · H3+H4 6 · H6+H7 6 · H8 3 · H9+H10 7 · H11 6 | 34 |
| **Ceremony** | H12 3 · **H13 10** · **H14 9** · H15 3 · H16 5 | 30 |
| 57th: plains | bridge 4 · H17 7 · H18 9 · H20 8 · H21 5 · H22 6 · H23 2 · H24 7 | 48 |
| 57th: forest | H25 8 · H26 6 · H27 8 · H28 3 · H29 8 · H30 6 · H31 6 · H32 6 · H33 10 · H34 6 · H35 12 · H36 8 · H37+H38 9 · H39 3 | 99 |
| 57th: return | H40 7 · H42 8 · H43 (map to Stohess) 5 | 20 |
| Stohess | X1 4 · X2+X3 5 · X4 6 · X5 6 · X6 5 · X7 3 · X8 2 · X9 4 · X10 7 · X11 10 · X13 10 · X14 7 · X15 6 · X16 6 · X17 6 · X18 8 | 95 |
| Bridges inside sets (drone travel between beats, about 1 s average × 125 shots) | eased in and out, no hard cuts | 125 |
| End card + credits (Sketchfab CC-BY credits) | | 15 |
| **Total** | | **808 s = 13:28** |

There is **32 s of slack** to 14:00. Spend it on the top-priority beats, in this order:

1. ceremony H13/H14: +4 s
2. Carla S14: +3 s
3. boulder carry T40: +3 s
4. Squad Levi H33: +3 s
5. Stohess climb X14/X15: +3 s

If the cut runs long, drop the `should` items with + first: S7/S8, R1, R5/R8, T1, T30, T39, T45, H1, H8, H15, H23, H28, H39, X1-X3, X7-X9. That saves about 60 s. The `must` beats alone plus bridges and cards are about 12:20.


## Build order (biggest viewer impact first)

1. **Attack Titan asset + shift FX** (shifters.py). Rigged 15 m Eren Titan, glowing green eyes, plus the lightning column, flash, steam dome and the burning-state material. It is needed by about 22 beats, T13 through X17, and nothing on disk covers it.
2. **Faceless human kit + ODM FX** (characters.py). Outfit presets (cadet, Garrison, Survey cloak with an over-sized Wings decal, MP unicorn), named read-presets (Erwin, Levi, Mikasa's scarf, Armin, Hannes, Pyxis, Petra, Jean, Annie), a crowd and rider instancer with drain/flow paths, and wire lines + gas-trail particles. It is in almost every beat after S4.
3. **Finish Shiganshina's emotional beats** (cast845/states845). Carla, the kids and Hannes posed; the Smiling Titan crouch, lift and bite; the carry run; the Scout return column + crowd; the ferries ported from shot_thumbs.py; the lightning bolt on the Colossal's rise. Add **sun-elevation / time-of-day control** to scene.py, which the sunset, night ceremony, pyres and dusk beats all need. This set is the opening minutes and is already 70% built.
4. **Recruitment ceremony set** (user's top priority, cheap). Torch square, stage, braziers, Wings banner, 200-cadet drain in waves, a ~20-cadet salute pose and Erwin's lit hair. The stage is re-used for graduation R9.
5. **Trost set** (district.py re-using the Shiganshina build). Outer gate breach state, cannon rail (cannon asset), north gate with crowd and cart, supply HQ with a cutaway roof and interior, the boulder, lure corner, plus the Colossal re-staged with an arm-sweep key. It holds the most `must` beats: 30.
6. **Female Titan rig + anims.** Auto-rig the best Sketchfab Female mesh (default pose only today). Sprint, crouch and hood lift, grab, swat, slump, bite, stamp, kick, boxing guard, climb, fall. Add the hardening opal shader and the crystal egg. Used in 24 beats.
7. **Forest of Giant Trees + harpoon trap.** 80 m+ instanced trunks, forest road, launcher banks, the cable-volley FX (re-used for Hange's net X9), and run cycles for the titan swarm. Use the itch rigged pack for the crowd.
8. **Titan-vs-titan fight keyframe set.** Forest duel H35/H36 and Stohess X10-X16: punch, uppercut, roundhouse, tackle, nape tear, destructible facades and splintering trunks.
9. **Plains + long-range formation + smoke-signal system.** Rider-group arc layout and coloured smoke columns (red, green, black, purple, yellow, blue). The same system drives the Trost flares T32/T35/T43, and the Karanes gate set.
10. **Stohess set.** Rich district variant, Wall-cult church with a collapsing spire, stairwell and tunnel mouth, street cave-in, rubble trench, Wall Sina climb handholds, and the Wall Titan face sculpt for the final shot.
11. Half-Titan skeleton mesh (T24), re-used for Sawney and Beane's skeletons (H9) and the spoon arm (H16).
12. Castle (set F), courtroom cutaway, refugee storehouse and training camp (set D), Ackerman cabins (set C), plus the map set A transitions with hud.py overlays.

Sources checked: fandom S1 episode pages via `ep1_canon_events.json`, and Ep16 casualty figures cross-checked on animeoshi.com/anime/attack-on-titan/episode/16 ("60% veteran casualties, 30% for new recruits"). The fandom page itself returned HTTP 402 during this pass.
