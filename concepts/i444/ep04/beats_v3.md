# EP04 Freddy v3: verified HD beats (11/7)

Every in-point in shots_v3.py was picked on real frames (1 s contact sheets with qa/sheet.py, 8-frame strips with qa/strip.py at the
in-point). Times are seconds into the clip in `E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\clips`. All used sources are 1080p
SDR, except r10_m1..m4 (720p Movieclips). The four sub-720p fan backups and fj_intro (a portrait phone recording of a TV) are not used.

## Changes vs shot_plan_v3.md

Edit decisions on top of the per-film checks:
- s11 'every death in all': n5_force_feed 28.60 (Freddy crushing Greta) instead of n4_kiss (the wide kiss is only 1.65 s clean).
- s10 NEW CUT 'his own reflection' (n4_death mirror, 0.85 s) dropped: it would play at 0.6x. The shard shot carries the line.
- s03 'his claws burst out': n2_bus 84.30 (Kerry, then the claws burst from ~85.2), plays at 0.77x. The burst itself is the last 1.2 s of the shot.
- n1_opening (window-boxed credits footage) is zoomed to fill the frame with z=1.8, dy=-123 (new dy option in render_fk.py).
- RT-channel clips that carry the grey RT MOVIECLIPS mark get the black bottom bar from y 885 (shots_v3_grade.py).

### n1: A Nightmare on Elm Street (1984)

- s00 `and all he needs`: n1_wall, n1_boiler and n1_preview4k have no bright "Freddy grinning, glove up" moment. I used **n1_tina_chase 29.70**: alley close-up, Freddy grinning with the glove raised beside his face against the blue sky. It is the best Freddy shot in the film.
- s00 `is for you`: the bath close-up has her eyes already shut and dozing, not closing on camera. I used the start of the dozing close-up (0.10).
- s01 `0`: n1_screw_sleep 33.20 is Nancy drinking coffee in front of her mother. It matches the plan ("coffee") better than n1_plan, which is Nancy dozing in bed with Glen.
- s01 `and that movie's freddy` uses boiler 272.90 (Freddy's hat in silhouette in the boiler room). s01 `is waiting for you` uses boiler 270.70 (the glove dragging along the pipe). Both shots are in the plan's candidates.
- s08 `0` (rank card): n1_preview4k is the 1984 opening credits only. Its Freddy is just the glove and silhouettes, with credit text over most of it. n1_wall has no clear Freddy face either. I used **n1_tina_chase 57.10** instead: Freddy's face lit, hand raised (the "This is God" moment), with a 4.3 s clean span.
- s08 `from nineteen eighty-four`: n1_opening 49.10, the finished glove on Freddy's hand (credits glove montage). The opening credits are window-boxed: a small picture in the centre of a black frame, about x 420–1500, y 115–720.
- s08 `this freddy isn't as strong`: the long-arms alley shot runs only 1.9 s, so I split it. NEW CUT at `the last one` shows Freddy's hat silhouette, a different alley shot.
- s08 `he barely talks`: n1_opening has no clear silent Freddy shot (credits only, plus Tina's back). I used boiler 288.55, an extreme close-up of Freddy's face in the boiler room.
- s08 `and nobody believes you`: there is no police moment in n1_plan. I used n1_screw_sleep 81.00: Nancy beside her mother in the kitchen, Marge not believing her.
- s08 `drags him into the real`: split with NEW CUT at `real world`. First Nancy grapples Freddy in the bushes, then she thrashes awake in bed (she pulls him out of the dream).
- s08 `and finally turns her back`: the two-shot is only 1.87 s, so I split it. NEW CUT at `on him` shows her hand going to the doorknob as she walks away from him.
- s08 `he still takes her mother`: the close shot is too short, so I split it. NEW CUT at `her mother` is the wide shot of Marge yanked through the door window.
- s08 `unless you're as` (L): n1_screw_sleep 74.00, a bright, determined Nancy close-up (5.2 s clean) instead of n1_plan. The two n1_plan Nancy close-ups are already used for `nancy only survives` and `to learn his rules`.
- s08 `he gets you` (L): n1_god 78.20 is the close-up of Freddy's lit face during the attack. The "This is God" face shot (H) is already the rank card.
- s08 `survival rate` (L): n1_wall 305.40, Freddy behind the gate bars in Nancy's dream. It is dark but readable.
- s11 `and honestly`: n1_wall 380.20, Freddy's face at the front-door window, instead of n1_god. All of n1_god's good Freddy moments are already used (H as the rank card via tina_chase, F in the cold open, S for `he gets you`).
- Every other shot keeps the planned clip and moment.

### n2: Freddy's Revenge (1985)

- s01 "one needs a teenager's body": uses n2_emerge 147.20 (Freddy's head rising out of Jesse's chest), with custom L dx=40 because the head sits at source x≈600. n2_brain does NOT contain the emergence (n2_brain is the opening gym/locker scene plus the "you've got the body" hallway scene).
- s03 "because he doesn't need": n2_emerge has no clean Freddy close-up of 2 s or longer (the lamp shots run 1.6–1.8 s). Uses n2_creepiest 1053.45 instead: a frontal Freddy close-up with the glove in the boiler room, 3.5 s.
- s03 "he takes over a teenager": n2_kill4k 7.00 is Jesse waking up sweating in bed.
- s03 "named jesse": n2_kill4k 141.45 is Jesse in the bright kitchen.
- s03 "then his friend grady": n2_kill4k does not hold Grady's death (it runs from the morning kitchen and car scene to the power plant and the Angela bedroom, then a WB 4K end card). Uses n2_emerge 180.90 instead: Grady in boxers with Freddy in the doorway beside him.
- s03 "he kills jesse's gym teacher" / "in the showers": nudity-safe choices. "gym teacher" = n2_creepiest 79.50, a wide shot of Coach Schneider tied to the floor by his wrists with jump ropes (tank top and trousers on). "in the showers" = n2_creepiest 96.60, a close-up of the coach's upside-down screaming face on the shower tiles (only his face and bare arm show). His bare body and the whipping never appear in either span.
- s03 "then a whole group": n2_pool 55.60 is Freddy slashing a fleeing kid by the pool lanterns. It is one victim in the middle of the mass attack, with other kids in the background.
- s03 "and in the very last scene" / "his claws burst out" / "on the school bus": these use n2_bus, which is the real FINAL bus scene (Jesse, Kerry with dark curls, Lisa with a red ponytail). n2_creepiest 252–335 holds the same scene, but n2_bus is cleaner and longer. "on the school bus" = n2_bus 46.22, the yellow school bus driving down the street toward the camera in the same final scene. I chose it over the 86–105 desert dust shot because the bus is clearly readable.
- s03 "and you'll probably be fine" (L): n2_kill4k 349.20 is a bright Jesse + Lisa two-shot at the power plant. The creepiest ending (1200–1217, Lisa with the charred Jesse) is too dark.
- s03 "survival rate" (L): n2_pool 327.50 is the large Freddy close-up from the kitchen scene, custom dx=160. In n2_brain, Freddy sits at x≈1400–1700, outside the L window, and his only centred shot (287–291) is near-black.
- s03 "this freddy is far more" / "and kills more people" / "he barely uses": all n2_pool as planned. The fog silhouette, the boiling-pool panic and the flame column are different moments.
- s11 "we're a small channel": n2_party 547.40 is Freddy standing among the parents at the party. It is a different moment from every s03 shot.

### n3: Dream Warriors (1987)

- s01 `you fall asleep`: **n3_real 11.00** (Kristen dozing off in her hospital bed, eyes closed) instead of n3_kristen/n3_bed. Neither of those clips has anyone falling asleep. n3_kristen is the same dream-house footage as n3_heres, and n3_bed is Joey's bed-to-hell scene.
- s01 `intelligence`: n3_heres 196.00 is the faucet handles turning into Freddy's claws, which is the "trick" moment. n3_heres has no clear Freddy face at all. The clip is Kristen's opening dream: the house, the girl on the trike, the faucet claw.
- s01 `and dream power`: the worm-Freddy face shot is only about 1.6 s long, so it is split with a **NEW CUT** on `is how dangerous` that uses the second worm-face shot.
- s09 `0` (rank card): **n3_joey 1.70**, a bright Freddy in his sweater in Joey's room, instead of n3_heres, which has no usable Freddy.
- s09 `this freddy is deadlier`: **n3_souls 100.30** (Freddy close-up, boiler room) instead of n3_real. The only Freddy in n3_real is the worm-Freddy face, the same footage as n3_worm 109–113 already used in s01.
- s09 `still can't stop`: n3_souls 141.55 (Freddy medium shot, warm light), a different shot from 100.30.
- s09 `he hunts the last children`: n3_best4k 153.00, the Westin Hills kids crowding the wire-mesh window.
- s09 `in a mental hospital`: n3_best4k 140.45, a wide shot of the lit Westin Hills nurses' station. n3_wizard has no hospital corridor; its corridor is the dream corridor.
- s09 `and will`: **n3_joey 120.20**, where Will is sitting in his wheelchair behind the doctor in the group-therapy room. n3_wizard_rt only shows the empty wheelchair, then Will standing beside it in the dream.
- s09 `then his skeleton kills`: the attack shot is 2.05 s, so there is a **NEW CUT** on `nancy's father` using the wide junkyard shot of the skeleton and Donald (skeleton 81.05).
- s09 `and freddy kills nancy`: the Freddy/Nancy stab shot is only about 1.4 s, so there is a **NEW CUT** on `herself` (Freddy at Nancy's throat, before the blood close-up).
- s09 `while pretending to be`: n3_nancy 8.50, a close-up of "Dad" smiling, which is Freddy in disguise. It is brighter and longer than the hug shot.
- s09 `the kids who survived`: **n3_creepiest 1024.60**. Joey hugs Kincaid, then Kristen and Nancy join them in the mirror hall. n3_best4k has no shot of only the three survivors. Note that **Nancy is also in this frame**.
- s09 `and it still took` / `on his bones`: **n3_nancy 96.10** (Neil in the grave with the holy-water bottle over the bones) and **n3_nancy 106.85** (Freddy bursting with light beams as the bones are consecrated). n3_skeleton ends after Donald's death and the skeleton in the fog; it has no holy water and no burning.
- s09 `you don't have` (L): n3_souls 125.70, a Freddy close-up grinning in the boiler room.
- s09 `survival rate` (L): **n3_taryn 110.60**, a low-angle Freddy face under the lights. n3_real is ruled out (worm footage only).
- s11 `along with the killer`: **n3_taryn 54.90**, Freddy face to face with Taryn, turning to grin. n3_heres has no usable Freddy.

### n4: The Dream Master (1988)

- **s00 frame 0**: uses `n4_beach` at 36.60, not junkyard/soulfood. It is the brightest, largest Freddy face in any n4 clip: daylight, hat and burned face filling the frame, grinning while he holds his sunglasses. The junkyard Freddy is a near-black silhouette, and the soulfood Freddy is darker and in profile.
- **s00 "crush you"**: no clip has the roach motel. `n4_roach` ends on the cockroach at 169 s, then the RT end card. I used Freddy forcing the barbell down on Debbie (Freddy, bar and lamp) instead. This is the closest real "crush" moment.
- **s00 "like a bug"**: close-up of the finished Debbie-cockroach (roach 166.45). The crush itself is not in any clip.
- **s01 "to wipe out kids"**: uses `n4_junkyard` (Freddy grinning with his claw on Dream Warrior Kincaid's chest), not `n4_karate`. In the karate clip Freddy is invisible, so only Rick being thrown around is visible. `n4_hell` is too dark, and its furnace moment is already used in s10.
- **s10 "and kristen"**: shows Kristen buried in the beach sand with Freddy's legs beside her (beach 40.45). This is a different moment from the frame-0 shot.
- **s10 "the kids who survived"**: the throw into the furnace is not in `n4_hell`. The clip shows the run-up (Kristen and Alice in the boiler room), then the burning furnace, then Freddy with Kristen's soul on his back. I split it: Kristen lunging, green-lit (NEW CUT "the last freddy"), then the burning furnace.
- **s10 "are all dead early"**: split at "in the movie" (NEW CUT). Freddy close-up by the chains, then Freddy's back covered in the faces of the souls he has taken.
- **s10 "then he goes through alice's"**: `n4_alice` has only Alice and Freddy, so I used `n4_kiss`. First Rick, Dan and their friends in the classroom, then the wide classroom shot with Alice and Sheila (NEW CUT "one by one").
- **s10 "and every soul he takes"**: uses `n4_soulfood`, not `n4_soulpizza`. They are the same scene, but soulpizza is a shorter edit with the same footage. The soul meatball on Freddy's claw, then Kincaid's face screaming in the pizza (NEW CUT "stays trapped").
- **s10 "alice only wins"**: split at "by taking on" (NEW CUT). Alice glowing in close-up, then the wide shot of Alice firing the blast at Freddy.
- **s10 "and showing freddy"**: Alice raising the stained-glass shard at Freddy (torn 28.10), then Freddy's own reflection in the mirror (NEW CUT "his own reflection", from `n4_death`).
- **s10 "if the kids"**: split at "couldn't survive" (NEW CUT, L), because the doctor-clip Freddy shot is only about 2 s long.
- **s11 "every death in all"**: uses the wide shot of Freddy's kiss of death on Sheila. Its clean span is 1.65 s against 1.92 s needed, so it is slowed to 0.86x. `n5_forcefed4k` (the plan's other choice) may fit better.
- **n4_nurse**: not used for a shot. Its bright nurse-Freddy close-up is used for the Tile only. The plan says it shows Joey, but the patient on screen is Kristen. I take the clip as n4 because the Freddy makeup matches and the n4 credits in `n4_death` list a "Nurse". This was not otherwise confirmed.

### n5: The Dream Child (1989)

- **s01 kill count**: `n5_force_feed` (the older clean copy of the same scene) instead of `n5_forcefed4k`. Same footage and timing, but there is no RT MOVIECLIPS mark.
- **s04 this freddy kills fewer**: `n5_back_to_hell` instead of `n5_hell4k`. Identical footage, no mark.
- **s04 but he's far smarter**: `n5_itsaboy` 50.55 (close-up of Freddy grinning, bright) instead of `n5_superfreddy`. Super Freddy is greyscale, dark and has no clear smirk.
- **s04 he finds a sneaky**: no shot of a pregnant Alice exists in any n5 clip. The closest true moment is `n5_back_to_hell` 155.0: in the film's last scene, after taking Jacob's glowing spirit back into her body, Alice has both hands on her belly (the unborn baby).
- **s04 through the dreams**: split in two because 3.05 s is needed. `through the dreams` → son4k 46.10, Jacob with Freddy beside him. NEW CUT `unborn son` → son4k 23.00, Jacob alone with Freddy's glove at his throat.
- **s04 even while she's wide**: `n5_son4k` 34.85 (bright close-up of Alice, scared, 4.5 s clean) instead of `n5_tricks`. The Alice shots in n5_tricks are dark and at most about 1.9 s / 1.3 s long.
- **s04 into part of his own**: `n5_motorcycle` 70.40, Dan's body already fused into the bike (flesh, cables, skull). The wires-into-skin shot (34.98–about 37.0) is only about 1.9 s long, below the 2.0 s needed.
- **s04 force-feeds greta / until she chokes**: `n5_force_feed` (clean copy).
  - "force-feeds" = the wide table shot, Freddy as waiter spooning food into Greta.
  - "chokes" = cut on the reaction: Greta in profile with stuffed cheeks, before Freddy grabs her. Not the stuffed-face close-up at 18–19 s.
- **s04 before slicing him**: split. `before slicing him` → superfreddy 45.80, Freddy's glove slashing paper Mark. NEW CUT `pieces` → superfreddy 48.15, Mark screaming in torn paper strips. Each shot in that scene lasts about 1.1 s.
- **s04 but alice has beaten**: `n5_son4k` 30.60 (Alice in the boiler/tower set, 2.6 s) instead of `n5_tricks`. The tricks shot of Alice yelling is only about 1.3 s.
- **s04 and in the end**: `n5_back_to_hell` 138.20, a close-up of Amanda the nun. The 98.3 close-up is only 2.0 s.
- **s04 jacob uses the power / to destroy him**: split.
  - `jacob uses the power` → back_to_hell 29.10, Jacob's face.
  - NEW CUT `freddy gave him` → back_to_hell 74.10, the souls tearing out of Freddy.
  - `to destroy him` → back_to_hell 79.30, Freddy stretched apart by the souls.
- **s04 he only gets three**: `n5_itsaboy` 60.65 (WB, no mark) instead of `n5_baby4k`.
- **s04 survival rate**: `n5_baby` 127.00, Freddy with arms spread in front of the church window, lit, 3.1 s. Used instead of `n5_son4k`, whose Freddy close-up at 48.21–50.43 is only 2.18 s (< 2.27).
- **s11 every death in all**: the preferred clip is `n4_kiss` (n4 agent). The n5 alternative is a different moment from s01/s04: force_feed 28.60, Freddy crushing Greta from behind.

### n6: Freddy's Dead (1991)

- s05 "has the biggest body count" / "before the movie even starts": none of the n6 clips have the empty Springwood, the carnival, the strange adults or missing-children posters. n6_town is mostly Maggie's dream of the Krueger house (0:92-5:00), not the empty town. Closest true moments used instead: "has the biggest body count" = the "Welcome to SPRINGWOOD" sign at night (n6_doom 32.40). "before the movie even starts" = an empty, rainy night street (n6_town 36.80, dark but readable).
- s05 "almost every child": no posters/school. Used the "NINE, TEN, NEVER SLEEP AGAIN" newspaper headline in its box (n6_town 61.85). Clean is 2.75 s against 2.70 needed, so there is only a little slack.
- s05 "and he plays with his victims": I used n6_playground (WB). It is the same John Doe parachute scene as n6_doom, and the moment is Freddy hanging beside John, cutting his cords. I did not use n6_game here because it is a soft fan upload. Do not use n6_doom 118.17-120.76 anywhere: it is the same moment from another upload.
- s05 "he turns up carlos's": n6_ear has no hearing-aid close-up that is not gory (its 126 s is the ear-cut gore). Used n6_nice 22.55: Carlos, cheerful, fiddling with the hearing aid in his ear.
- s05 "and drops john doe": no single John-falling shot is longer than about 0.9 s. Split it: on "and drops john doe", Freddy's claw slicing the parachute cord (n6_doom 120.80). On "john doe" (NEW CUT, 23.14), John screaming as he falls (n6_doom 132.03). That clean is 0.80 s against 0.83 needed, so the renderer slows it to about 0.96x. After about 132.85 the shot whites out into fog.
- s05 "the last teenager": n6_busrt 57.75. John Doe lies on the empty daylight road outside Springwood after the bus nightmare (bright and clear).
- s05 "tracy gets woken" / "before he can finish": order changed to fit the words. "tracy gets woken" = dream Freddy snarling right over Tracy (n6_father 136.05). "before he can finish" = Tracy jolting awake in bed after burning her hand on the stove (n6_father 159.05), not "fights him off".
- s05 "in the end his own daughter": used n6_blood (WB) rather than n6_daughter (ClipZone, which has bumpers). The moment is adult Maggie in her child's dress in Freddy's dream.
- s05 "drags him into the real": the pull-out itself is in none of the clips (n6_maggie starts already in the real-world basement, and n6_brain ends in the 1940s school flashback). Closest true moment: n6_maggie 0.05, Freddy, now in the real world, grabbing Maggie in the basement (wide).
- s05 "he's deadly but" (L): no n6_brain Freddy shot at the planned spot fits L. Used n6_brain 43.60: Freddy's face bursts out of the demon wall, screaming, then the camera pushes into his eyes. It is centred, so the default L works.
- s05 "and that time is" (L): n6_maggie 229.85. Freddy's screaming head is in the middle of the explosion, then breaks up into debris at about 231.4.

### n7: New Nightmare (1994)

- **s07 "this freddy is stronger"**: n7_missme -> **n7_coming_uk 101.80**. The missme Freddy is nearly black. This one is a bright Freddy face peering through the doorway.
- **s07 NEW CUT "and smarter"** (3.71): splits the 3.33 s shot. n7_coming_uk 36.45: Freddy's head comes through the window toward Dylan.
- **s07 "he hunts a whole family"**: n7_dylan -> **n7_hand 5.80**. n7_dylan (and n7_handbed, the same scene) never has Heather, Dylan and Chase in one frame. In n7_hand they are together at the FX workshop, with Chase holding Dylan next to Heather. It is the effects workshop, not their house.
- **s07 "he goes after heather"**: n7_stalks -> **n7_missme 11.40**. n7_stalks is only the claw-in-bed scene, with no scared Heather. missme 11.4 is a bright close-up of Heather looking up in fear as the earthquake starts.
- **s07 "the actress who played"**: uses the second candidate **n7_dylan 6.20** (bright Heather close-up on the phone). This keeps n7_funeral for the next shot.
- **s07 "he kills two special"**: n7_hand 91.20 shows the glove slashing an effects man on the floor. "working on a new" uses n7_hand 30.50: an effects man drinking coffee behind the animatronic glove rig on the set. Both are the plan's first clip, at different moments.
- **s07 "then her husband" / "while he's driving"**: n7_bloodiest. Chase yawns and nods off at the wheel (1121.00), then the claws rise through the seat (1116.00). The crash in bloodiest (1147–1150) is shots under 1 s, and the claw-through-chest frame (1145) is the most extreme gore, so I left both out. The claws carry "while he's driving".
- **s07 "right into his world"**: n7_end -> **n7_coming_uk 1.68** (Dylan climbs the lair's temple stairs). n7_end starts inside the lair with Heather reading the script and has no establishing shot of the lair.
- **s07 "to push him into"**: n7_end -> **n7_coming_uk 226.80**. n7_end has no furnace. This shot is Freddy's face as the furnace flames engulf him. The actual shove (coming_uk 215.09–216.75) gives only 1.62 s against the 1.70 s needed.
- **s07 "he only gets four"**: n7_surgery -> **n7_missme 81.66**. The doctor-Freddy in n7_surgery lasts only about 0.55 s (72.75–73.30), and the same is true in bloodiest around 792. missme 81.66 is Freddy's face rising out of the dark (dark blue, but readable).
- **s07 "but if he picks"**: n7_son -> **n7_coming_uk 43.85**. n7_son is the traffic scene again, and its only Freddy is 1.5 s on the moon. In coming_uk 43.85 Freddy reaches his claw out of the window toward Dylan.
- **s07 NEW CUT "the people you love"** (34.76): splits the 3.28 s shot. n7_julie 31.10: Freddy flexes the glove behind Julie, the babysitter.
- **s11 "to get this ranking"**: n7_missme -> **n7_traffic 95.88**. missme's Freddy moments are now used, and its other Freddy close-up (109.5) shows only a shadowed mouth. traffic 95.88 is Freddy on the moon and clouds above the freeway.
- Small changes in meaning: "and he doesn't just hunt" shows the claw over Heather's sleeping face (n7_stalks). "it takes heather and dylan" shows the two of them hugging in the lair (n7_end).

### fj: Freddy vs. Jason (2003)

- **fj_intro rejected entirely.** It is 720x1280 portrait: a phone filming a TV in a room (wall, towels and the set-top box are visible around a small, blurry TV image). It also includes the opening montage of the 1984-1991 films' Freddy. It cannot be used for any shot. Its planned shots were moved:
  - s02 #2 'because his town forgot': Springwood house exterior at night from **fj_notstrong** 63.70 (Blake's porch-lit house).
  - s02 #3 'the adults erased': Lori's father (Dr. Campbell, the adult covering it up) at the front door, **fj_back** 163.80.
  - s02 #4 'every trace of him': **no newspaper clippings exist in any usable fj clip.** Closest true moment: the night exterior of Lori's house (the old 1428 Elm St house) from **fj_back** 214.40.
  - s02 #5 'and anyone who still dreams': Westin Hills ward of sedated patients, **fj_influence** 60.25. The ward shot is only 1.9 s, so I added a NEW CUT at 'about him' to Westin Hills patients with taped eyes (influence 71.40).
- s02 #9 'bring jason back': **the Pamela-disguise scene is in none of the fj clips.** fj_mom and fj_mommy are both the boiler-room dream fight (plus a Blu-ray end card), and fj_dreaming and fj_childhood are both the Crystal Lake camp flashback. Closest true moment: Jason rising out of Crystal Lake, **fj_world** 144.40 (from the end of the film; it does not overlap the head/wink moment used at #17).
- s02 #10 'to scare people': fj_mommy and fj_dreaming have no "Jason walking into Springwood" shot. Used **fj_crash** 21.10 instead: Jason's mask looming over Trey in the Elm St bedroom (the next shot after the s01 crash moment, so it is a different moment). It ends before the Gibb shower shot at 23.05.
- s02 #11 'in a movie with his own name': **fj_battle** 241.00 (Freddy in the foreground stalking Will and Lori at Crystal Lake). Moved off fj_kicks because the only long kicks close-ups are needed for #0 and #20, and the world Freddy shots are too short.
- s02 #12 'jason does nearly all': **fj_cornfield** instead of fj_rave. They show the same footage, but cornfield has no Movieclips mark. Every burning-Jason shot is about 2.0 s, so I added a NEW CUT at 'the killing'.
- s02 #15-#17 (Lori, swing, head + wink): the ending is in **fj_world**, not fj_hell or fj_construction. fj_hell is the dock fight and explosion before it, and fj_construction is the construction-site fight.
- s02 #18 'if you've never heard' (L): **fj_battle** 230.60 (Freddy raising the glove) instead of a 4th moment of the single fj_notstrong Freddy shot.
- s02 #20 'survival rate' (L): fj_kicks 166.60, the green Freddy close-up near frame centre. The 189-197 close-up has Freddy at x ≈ 1300-1500, outside the L window, so it went to #0 (no L) instead.

### r10: A Nightmare on Elm Street (2010)

- **s06 `0` (rank card)**: uses r10_dreaming 364.98, not creepiest/unavoidable. The bright Freddy faces in creepiest are needed for s01, idx19 and the mirror stand-in. unavoidable's only Freddy is a glove shot, which idx1 already uses. Freddy raises the glove in the classroom dream (Kris), 2.8 s clean.
- **s06 `this freddy is the opposite`**: in r10_unavoidable (the Dean diner dream) Freddy only appears as a gloved hand rising in front of the kitchen fire (101.45–105.8). Freddy's face is never readable there. The line uses the glove.
- **s06 `and he has a trick` / `go too long without`**: r10_m3 is Nancy's store micro-nap, but it opens with Quentin at the pharmacy counter buying pills. Quentin's close-up is used for "trick" and the wide shot of Quentin at the counter, tired, for "pills".
- **s06 `that makes staying awake`, `by the time nancy figures`**: r10_m4 is Kris and Jesse in Kris's bedroom ("same dream") with no Nancy, and r10_m2 is Dean's diner dream. Nancy comes from r10_m1 (Nancy and Quentin at the library table with the preschool book), two different moments.
- **s06 `for a few seconds`**: the store/boiler Freddy shots near 42–49 s are all shorter than 1.45 s. Instead it uses Freddy with the fireball behind him in the store-turned-boiler (m3 64.15, 3.05 s).
- **s06 `without you even noticing`**: the shots of Nancy waking on the store floor (67.28–68.44, 71.1–71.6) are 0.5–1.15 s and intercut with boiler flashes. The line uses Nancy in the bright store at night, startled and looking around (m3 12.12, 3.05 s).
- **s06 `except her and quentin`**: no two-shot in m4 or m1. It uses r10_dreaming 248.70: Quentin (beanie, back to camera) and Nancy at her school locker.
- **s06 `he gets dean`**: **r10_preview is NOT the 2010 film.** It is the 1984 original's opening (New Line credits, Heather Langenkamp, Robert Englund credit, Tina in the boiler room), so it is unusable for r10. Dean in the diner comes from r10_unavoidable 43.0 (Kellan Lutz alone in the night diner). r10_m2 is also Dean's diner dream (backup).
- **s06 `kris in her bedroom`**: r10_creepiest 524.10, Kris flung through the air across her bedroom (handheld, no blood).
- **s06 `and jesse in a jail cell`**: the in-cell moments (Jesse convulsing in front of the cellmate, 732.65–733.32, and lying on the floor, 738.40–739.70) are each under 1.3 s and gory. The line uses Jesse in his orange jumpsuit in the jail cell corridor, from behind, turning his head (564.0, 10.6 s).
- **s06 `and even after nancy drags` + NEW CUT**: the pull-out runs as a chain of short shots. idx16 is Nancy on the floor with Freddy on top of her, gripping her, after she wakes (1169.20). A NEW CUT at `him into the real world` shows Freddy lying on the rug in the real world (1171.72).
- **s06 `and cuts his throat`**: the slash itself is not shown. The line uses the next shot: Freddy standing, the black blood just starting to pour from his throat (1241.40, cut on the start of the flow).
- **s06 `he comes back through` (mirror attack on Nancy's mother): MISSING from every r10 clip.** r10_creepiest ends (1429–1445) on Nancy hiding in a closet at home, then the WB "own now" card. Boyfriend, unavoidable, dreaming and m1–m4 have no mirror either. Closest true moment: a Freddy close-up in the fire-lit boiler room (1372.05). Fix this line if a mirror-ending clip is fetched.
- **s06 `staying awake won't` (L)**: uses r10_creepiest 1028.60 (Freddy at a child's bedroom window, face at x≈640), not boyfriend. Boyfriend already has idx2, and its real-world Freddy shot (130.1–132.1) is only 2.0 s.
- **s06 `survival rate` (L)**: uses r10_boyfriend 1.45 (Freddy's face over Nancy, face x≈760), not dreaming. Every dreaming Freddy sits at x≈1250–1350, which is outside the L zone.

## Verified beats per film

### n1: A Nightmare on Elm Street (1984)

All clips are 1920x1080, bt709 (SDR). I saw no channel bug or watermark in any span I used. I did not see the grey "RT MOVIECLIPS" mark in any n1 clip.

**n1_tina_kill** (218.6 s): this is the same Tina scene as n1_tina_chase and n1_god.
- 64–132: alley chase.
- 112–114: Freddy's lit face with hand raised (the same moment as tina_chase H; not used from here).
- 133–162: Tina and Rod in bed, then Tina slashed.
- 162.4–162.95: Rod on the floor.
- 163.0–164.28: Tina dragged up the wall by the window. USED in s00.
- 164.3–166.1: Rod.
- 166.15–167.88: Tina higher on the wall. USED in s08.
- 168.0–168.85: Rod.
- 168.9–184.05: wide of the ceiling, Tina dragged across it, Rod in the foreground. USED 179.5–183.8.
- 184.1–185.8: Nancy in bed (dark).
- 185.85–~187.0: close of Tina on the ceiling. USED 185.9–186.9.
- ~187.0–187.8: other angle of the ceiling.
- 187.9–188.3: Rod screaming.
- 188.3–189.5: ceiling smeared with blood, Tina falls.
- 190+: bloody bed; then Nancy at 194–217.

**n1_tina_chase** (102 s):
- 0–11.9: Tina in the alley.
- 12.05–14.2: Freddy's hat silhouette (A1).
- 14.4–16.0: Tina.
- 16.05–18.2: long-arms silhouette (B1).
- 18.4–20.3: hat silhouette (A2).
- 20.4–21.9: Tina.
- 22.0–23.6: long arms.
- 23.9–25.6: glove blades scraping the fence.
- ~25.9–26.6: hat.
- 26.7–28.0: Tina.
- 28.04–31.2: Freddy grinning, glove up by his face, bright blue (F).
- 31.3: Tina; 31.5–55: chase in the dark.
- 52–55: Freddy among the trees.
- 55.0–56.8: Tina close.
- ~57.0–61.5: Freddy's lit face, hand raised (H, the "This is God" moment).
- 61.8: Tina crying.
- 64–79: struggle.
- 75.2–78.1: Freddy's face close.
- 80+: Rod's bedroom.

**n1_god** (161 s): another upload of the same scene, about 2–4 s later than tina_chase and not a constant offset.
- 59.8–64+: H.
- ~78.1–80.95: close of Freddy's lit face during the struggle (S). USED 78.2–80.8.
- 81.1: Tina.
- 82–160: the Rod/Tina bedroom and ceiling, the same footage as tina_kill 134–212.

**n1_glen_bed** (165 s): the same scene as n1_glen, about 8 s earlier.
- 0–104: Nancy on the phone and the house.
- 104–~121.0: Glen asleep with headphones (close, then wide).
- ~121.3–~131: close of Glen pulled down into the bed (one continuous shot). USED 123.55–125.55.
- 136–148: blood geyser (avoid).
- 150–165: Glen's mother screaming.

**n1_glen** (173.8 s):
- 0–111: Nancy on the phone and the stairs.
- 112–129.05: Glen asleep (wide from ~120).
- ~129.1: cut to close; arms grab him and pull him under; empty bed by ~136.
- 140–143.4: Nancy screaming.
- 143.47: cut to the geyser (143.5–157, AVOID).
- 158–172: mother screaming.
- USED 126.65–129.0 and 134.2–136.2. Both end long before 143.47.

**n1_bathroom** (162.9 s):
- 0–29.65: close of Nancy dozing, washcloth in hand.
- 29.65–43.43: wide between her knees. Blade tips appear about 32.5, the glove rises 36–43, foam covers her body, only knees and head visible.
- 43.46–45.0: a different angle of the glove.
- 45–51.4: Marge.
- 51.43–55.5: Nancy asleep, close.
- 55.5–64: Marge and Nancy.
- 64–79.5: Nancy sliding down, behind the glass door.
- 80–83: she goes under.
- 84–99: underwater (dark).
- 100–117: Marge at the door, Nancy surfacing.
- 118–148: Nancy in a towel with Marge. Her shoulders and back are bare, so there is some nudity risk here: do not use.
- 150–160: Nancy in a robe.
- 160: Stay Awake pills.
- No nudity in the spans used (0.1–3.1, 36–37.1, 38.2–43.4, 51.55–55.35).

**n1_bathtub2**: not used and not checked frame by frame.

**n1_boiler** (296.4 s):
- 0–96: classroom; 68–70: Tina in a body bag (gore).
- 96–190: school hallway; 132–146: Tina in Freddy's sweater with the glove.
- 190–226: boiler-room entry.
- 225.9–226.9: wide of Freddy standing among the boilers.
- 227–228.9: Nancy.
- 229.0–230.0: Freddy medium.
- 230–232.1: close of the pipe and glove.
- 232.17–235.65: Freddy medium in the shadows, raises the glove (B3). USED.
- 235.7: Nancy.
- 242–244: glove dark.
- 266–267.9: Nancy.
- ~268–272.75: glove scraping along the pipe (B4). USED 270.7–272.6.
- 272.8–275.2: Freddy's hat silhouette (B5). USED 272.9–275.0.
- 275.4–278: Nancy.
- 278–281: Freddy walking in the background (dark).
- 282–288: Nancy.
- ~288.3–290.6: extreme close of Freddy's face (B7). USED 288.55–290.35.
- 290.8–292: Nancy.
- 292: Freddy's face again.
- 294–296: Nancy's arm on the pipe.

**n1_opening** (248.4 s): opening credits.
- 0–52: glove forging, window-boxed (the picture is a small inset, about x 420–1500, y 115–720, inside a black frame).
- Credit text appears at 4–9 ("New Line Cinema…"), 22–26.7 ("a Robert Shaye production") and 44–48.3 ("a Wes Craven film").
- Clean forging spans: 28.0–30.2, 30.3–32.2, 32.3–33.6, 33.7–38.4, ~38.5–42.3 (blade in the vise, USED 38.7–42.1), 42.4–44.0, and ~48.6–51.8 (the finished glove on his hand, USED 49.1–51.5).
- The "NIGHTMARE" title rises from about 51.9; the title card runs 52–57.
- 58–63: Tina on white.
- 64–190: Tina in the boiler room, with a credit name over almost every shot (64–175). Avoid.
- 190–248: Tina waking up with Marge.

**n1_preview4k** (603 s): the same 1984 opening, about the first 10 minutes of the film: credits glove 0–52, title 54, Tina's boiler-room nightmare 60–200 with credits, then the morning, school, Nancy, Glen and the phone call. No other film is mixed in, but nearly all Freddy footage carries credit text, so I used none of it.

**n1_wall** (517.2 s): Glen at Nancy's house, then Nancy's nightmare.
- 0–128: the same footage as n1_plan from 24 s on.
- 299.95–302.4: Freddy approaching in the jail, red and green sweater.
- 302.6–304.6: Nancy behind the bars.
- ~305.0–308.8: Freddy behind the gate bars. USED 305.4–308.7.
- 309–: Nancy.
- 348: Freddy.
- 352: Freddy (dark).
- 380.12–381.95: Freddy's face at the door window. USED 380.2–381.9.
- 400–432: bed attack.
- 482–507: Nancy wakes, Marge.
- **ClipZone end card from about 507.5 to the end. Do not use.**

**n1_fight** (199.8 s):
- 0–21: Nancy in the dream yard.
- 22: "TIMER 10:00" alarm clock.
- 27.37–28.85: dark wide of the struggle.
- 28.9–30.35: close of Nancy grappling Freddy in the bushes. USED 28.95–30.3.
- 30.4–~32.25: Nancy thrashing in bed as she wakes. USED 30.45–32.15.
- 32.3–60: Nancy in bed.
- 62–66: Freddy leaps at her.
- 84–92: police outside.
- 96–135: house chase; Freddy's face on the stairs at 128–135 (dark).
- 136: explosion.
- 138–152: window bars.
- 154–200: basement; Freddy burning at 174–198.

**n1_no_fear** (228.8 s):
- 0–60: fire and the police.
- 60–155: bedroom with her father.
- 162–172: sheet rising and blue mist.
- 174–217: Nancy close.
- 206–207: Freddy (dark).
- 219.0–220.95: Freddy behind Nancy as she turns away. USED 219.08–220.93.
- 220.95–~222.25: close of her hand on the doorknob. USED 221.0–222.2.
- 222.3–222.85: Freddy lunging, close.
- 222.9–228.8: wide; Freddy dissolves into blue sparks at 223, Nancy alone. USED 222.95–228.65.

**n1_ending** (114.4 s):
- 1.1–9.4: Nancy on the porch.
- 9.4–13.97: Marge close. USED 10.3–13.7.
- 14–50: Nancy and Marge at the door, the car.
- 52–80: friends in the car, which is in Freddy's colours.
- 86.4–88.65: close of Marge; the glass breaks at 87.1 and Freddy's arm grabs her. USED 87.1–88.6.
- 88.67–90.03: wide, Marge pulled through the window. USED 88.72–89.97.
- 90.03–~95.4: girls skipping rope. USED 90.15–95.25.
- Fades to black about 95.4–96.
- **End credits on black from 102. Do not use.**

**n1_rod** (215 s):
- 0–83: Nancy's room and the police station.
- ~83.1–94: the cell, the sheet creeping over the bunk, bars behind. USED 86.0–91.0.
- 95–99: Rod asleep.
- 100–145: police station.
- 146–159: Rod on the bunk.
- ~159.9–162.6: Rod choking, sheet at his throat. USED 160.45–162.4.
- 162.9–170.3: struggle.
- 170.4–172.3: Rod hanging (ceiling view).
- 172–176: feet by the sink.
- 176–212: discovery.

**n1_plan** (265.9 s): despite its title, this is Glen watching over Nancy at night, the same footage as n1_wall minus 24 s.
- 0: Stay Awake pills.
- 6–14: Nancy dozing.
- 16–22: TV.
- 24–152: the bedroom with Glen.
- 94.3–~104.9: Nancy close. USED 95.0–97.7.
- 127.2–~135.8: Nancy close. USED 128.0–130.0.
- 152–264: Nancy's dream walk outside.

**n1_screw_sleep** (172.5 s):
- 12–28: Nancy comes home.
- ~29–46: kitchen, Nancy drinking coffee with Marge watching. USED 33.2–36.7.
- 48–73: kitchen.
- 73.4–79.4: Nancy close. USED 74.0–79.2.
- 79.6–80.57: Marge close.
- 80.6–~89.5: two-shot of Marge and Nancy. USED 81.0–83.4.
- 90–163: the hat argument.

**n1_dark_story** (192.8 s):
- 0–3: bridge.
- 3–10.3: Nancy walking.
- 10.3–11.6: house.
- ~11.6–14.6: Nancy alone on the street. USED 11.9–14.3.
- 15–39: house door and windows.
- 40–90: hallway with Marge.
- 72–90: basement.

**n1_traps** (231.7 s):
- 0–60: police outside.
- 60–165: Nancy and her father on the phone.
- 166.2–~170.0: Nancy with the glass ball / lightbulb trap. USED 166.65–169.95.
- 170–176: hands rigging the trap (dark).
- 176–182: tripwire (dark).
- 182–190: floor.

**n1_creepiest** and **n1_boyfriend**: not used and not checked.

**Tile:** `('n1_tina_chase', 59.00, 910, 440, 500)`
The crop gives Freddy's lit face filling the frame, eyes visible and grinning under the hat brim, sharp. I checked it by viewing the 400x400 crop at `E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\beats\n1\tile_final.jpg`. It is a bit dark (blue night light), so a small brightness lift would help.

**Problems:**

- The 1984 film is dark overall. These shots are dim, though Freddy is readable: s08 `he barely talks` (boiler 288.55, dark red extreme close-up), s08 `survival rate` (wall 305.4), s11 `and honestly` (wall 380.2), and s01 `and that movie's freddy` (a silhouette, as planned).
- The n1_opening glove-forging footage (s01 `so we score`, s08 `from nineteen eighty-four`) is a small window-boxed picture with black around it. Even at z=1.35 there will be black borders, so a stronger zoom is needed if the renderer allows it.
- Cut points: a few were found from 0.1–0.4 s strips, not frame-exact: no_fear 220.95, ending 88.66, tina_chase 31.2. The spans stop 0.05–0.1 s short of them.
- n1_creepiest, n1_boyfriend and n1_bathtub2 were not reviewed because none of my shots needed them.

### n2: Freddy's Revenge (1985)

Moments used once each (no duplicates): brain 276 hallway, pool 71 fog, cr 1053 boiler close-up, kill4k 7 bed, kill4k 141 kitchen, emerge 139.6 / 147.2 emergence (two different shots), pool 21.9 boiling pool, party 553 crowd walk, cr 79.5 coach tied, cr 96.6 coach face, emerge 180.9 Grady, pool 55.6 slash, bus 9 / 46 / 85, party 522 fire pose, pool 117.9 flame column, cr 1009 / 1020 / 1038 / 1094, kill4k 308 / 349, pool 327.5, party 547.4. Mirror moments NOT to reuse elsewhere: party 489–497 = pool 71–79 (fog); party 516–526 = pool 96–107 (fire pose); party 526–530 = pool 118–122 (flame column); party 551–557 = pool 133–137 (crowd walk); creepiest 252–335 = bus 6–86 (final bus scene); creepiest 210–240 = brain 272–299 (hallway).

**n2_brain** (53sAUUWlOKs, 1920x1080 SDR, 307.8 s)
- 0–63: Jesse and Grady doing push-ups, coach's office, gym class. 63–95: locker room. 96–235: night, Jesse sleepwalks (dark). 236–272: hallway, Jesse at the door (dark).
- 272.73–287.08: ONE shot, Jesse on the left / Freddy on the right in profile, claw at Jesse's lips and face. Freddy x≈1400–1700.
- 287.08–290.92: Freddy's eyes extreme close-up, near-black. 290.92–299.88: Jesse against the stairs, Freddy's claw at his throat (Freddy right edge).
- 299.9–end: WB "LOOK FOR IT ON 4K" end card. No logo or bug before it.

**n2_emerge** (QRxDJ_KE5nw, ClipZone, 1920x1080 SDR, 284.4 s)
- 0: TV screen with text (credits on a TV). 0–120: Jesse in his room, then Grady's room, Jesse's agony (sweating, 57–90).
- Cuts: 122.33 125.21 126.00 127.25 129.63 131.05 132.22 133.30 134.18 136.14 137.10 139.60 141.31 142.35 143.85 146.86 149.11 150.94 153.78 160.62 163.70 164.87 169.25 170.92 173.26 174.88 176.72 179.14 180.85 183.18 183.93 187.65 188.56 189.81 191.61 192.98 194.53 200.16 207.37.
- 139.60–141.31: wide, Freddy's torso bursting out of Jesse's chest. 142.35–143.85: same, closer. 146.86–149.11: Jesse lying, Freddy's head rises out of his chest (head x≈300→700). 150.94–153.78: lamp, then Freddy rises into frame under the lamp. 173.26–174.88 and 179.14–180.85: Freddy under the lamp (short). 180.85–183.18: Grady in boxers + Freddy in the doorway. 183.93–200: Freddy's claw at Grady's throat (gore), parents at the door.
- 207–270: Jesse bloody in the room. 273: black/white flash, 276–end: ClipZone outro card. No bug during the film part.

**n2_kill4k** (Fg9RDgnPxxU, WB 4K, 1920x1080 SDR, 434.6 s)
- 0–6.92: Elm St. house exterior at night. 6.92–~9.8: Jesse wakes in bed, sweating (then another bed angle to 11.39). 12–40: Jesse shirtless in his room, glove in the drawer (30). 42–84: hallway, sister's room (dark blue).
- 87–175: breakfast kitchen (bright). 141.35–144.23: Jesse in the kitchen. 177–216: car drive to the power plant. 219–322: Jesse + Lisa at the power plant. 307–319: Jesse close-up, Lisa behind (continuous, no cut found).
- Cuts 322.57 325.78 331.96 338.30 343.47 346.47 349.10 352.14 354.65 355.86 357.44 358.73 360.86. 349.10–352.14: Jesse + Lisa close two-shot, bright.
- 366–428: boiler/basement, sister Angela in bed, glove at the bed (423–427). 429–end: WB 4K end card. Grady's death is NOT in this clip.

**n2_pool** (C73xsVyZf_c, WB UK Horror, 1920x1080 SDR, 339.2 s)
- Cuts: 1.63 2.25 3.42 6.92 7.59 8.55 10.30 11.39 (13–16 short shots, missed by the detector) 21.81 24.61 26.36 29.41 35.24 39.96 43.71 46.38 48.42 50.47 53.22 54.55 (~55.4) 59.60 62.52 63.65 66.57 71.11 78.79 81.33 95.51 97.39 99.77 104.10 111.19 ... 117.78 121.95 ... 133.09 ...
- 3.42–6.92: Freddy among the fleeing crowd at the pool. AVOID: there are swimsuit backs in skimpy bottoms in frame.
- 21.81–24.61: pool boils, kids scramble. 55.4–59.60: Freddy slashes a kid, the kid staggers with a bloody chest. 71.11–78.79: Freddy silhouette in the fog. 96–107: Freddy's fire pose (crowd shots in between). 117.78–121.95: flame column + Freddy + parents. 133–137: Freddy walks through the swimsuit crowd.
- 144–270: Jesse/Lisa house, Lisa chased by Freddy. 270–332: kitchen knife scene. 292.25 293.58 294.30 295.50 ... 322.57 327.41 332.04. 327.41–332.04: big Freddy close-up (face x≈720).
- 333–end: Freddy at the door. No logo or bug seen.

**n2_party** (Ks2K3owHdyI, ClipZone, 1920x1080 SDR, 584.6 s)
- 0–92: Jesse bloody with Lisa on the stairs. 93–135: pool party starts. 135–290: same house and chase material as n2_pool. 290–375: kitchen scene. 375–575: pool massacre.
- Cuts (420–562): 420.55 421.71 425.22 425.88 426.84 428.60 429.68 431.26 431.97 435.44 440.11 442.90 444.65 447.70 451.87 453.54 454.91 458.25 462.00 464.67 466.72 468.76 471.51 472.85 477.89 480.81 481.94 484.86 489.40 497.08 498.33 499.62 509.93 513.80 515.68 518.06 522.40 526.73 529.49 (flame flicker 530–542) 544.88 (+ one around 546.8, missed by the detector) 551.38 556.64 558.01 560.39 570.74.
- 464.67–466.72: Freddy hurls a chair into the crowd. 522.40–526.73: Freddy's fire pose, arms spread. 547.3–551.38: Freddy among the parents (darkens to silhouette by 549). 551.38–556.64: Freddy walks through the crowd (visible from ~553.3).
- 576–end: ClipZone outro card.

**n2_creepiest** (ieRxL6VBrwo, WB UK Horror, 1920x1080 SDR, 1232 s)
- 0–2.13: coach in his office (tank top). 4.84–7.80: coach face close-up. 13–78: coach attacked by balls and racks (tank top).
- 78.75: vent, then a whip pan to 79.3. 79.3–85.00: coach tied by jump ropes on the floor, wide, then dolly in to his back (blurry from ~83). Safe.
- 85.00–92.97: Jesse in the shower (bare upper body only in frame). 93–96.5: lockers wide. 96.51–99.64: coach's upside-down face screaming on the shower tiles (safe to 98.6; from 99 dark leather/skin, I did not use it). 99.64–110: Jesse in the shower and the steam. NOT used: anything after 99 in this scene.
- 114–250: Jesse sleepwalks / hallway (same as brain 272–299 at 210–240). 252–334.54: the final bus scene (same as n2_bus). 336–528: opening school-bus nightmare (same as n2_schoolbus). 534–550: kitchen. 552–880: pool party and kitchen-knife scene. 882–1000: Lisa in the boiler room.
- 1008.51–1017.06: Lisa close-up. 1017.06–1018.60: Freddy. 1018.60–1042.62: ONE shot, Lisa + Freddy, she lifts his hat (1026), the kiss (~1033–1042).
- 1042–1062: Freddy reacts, steam. 1053.39–1057.01: Freddy frontal close-up with the glove. 1062–1100: fire (the detector fires constantly on the flames). 1090.34–1091.72: Freddy's burning face. 1094.64–~1097.9: Freddy screaming in flames, then Lisa. 1100–1200: flames, Freddy's husk. 1200.12–~1217: Lisa with the charred Jesse (dark).
- ~1217–end: "OWN NOW ON DIGITAL OR DISC" card.

**n2_bus** (older download, Rotten Tomatoes clip, 1920x1080 SDR, 115.6 s)
- Thin black letterbox strip at the bottom. No RT MOVIECLIPS mark seen at bottom-left in any frame I checked (10, 20, 85.6, 90). Ends with a Rotten Tomatoes blue splat end card at 105.52–end.
- Cuts: 0.46 6.76 25.44 29.49 46.17 47.80 52.59 57.39 65.06 67.07 71.15 72.74 86.17 105.52.
- 6.76–25.44: final scene three-shot, Jesse / Kerry / Lisa. 25.44–29.49: school bus on the street. 29.49–46.17: three-shot again. 46.17–47.80: bus drives toward the camera. 52–72: the bus speeds up, Jesse at the driver. 72.74–86.17: three-shot; Kerry leans in, the claws burst out of her chest at ~85.2 (claw clear from 85.5). 86.17–105.52: desert, dust, the bus in the dust (~89–95), Joshua tree.

**n2_schoolbus** (6RphK0cEI6Y, WB 4K, 1920x1080, 335.7 s): the OPENING nightmare (two blonde girls, Jesse, the bus into the desert, the claws) at 0–205, then breakfast, then a WB 4K end card at 330. Not used, so it doesn't mix with the final scene.
**n2_kill_for_me** (older RT download, 68.5 s): Jesse, the glove in the drawer, the hallway, sister's room (same as kill4k 30–84). RT end card from 57. Not used.
**n2_kiss_fan** (1280x648) and **n2_kerry_fan** (1280x656): under 720p, not used, per the brief. **n2_grady_fan**: not used (Grady covered by n2_emerge).

**Tile:** ('n2_pool', 329.50, 690, 530, 1060)  # verified crop E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\beats\n2\tileC.jpg: big Freddy face with hat, eye visible, sharp, fills the frame (3/4 view, a little dim/red)
Alternative frontal one (eyes half-closed): ('n2_creepiest', 1053.60, 1120, 350, 700) -> tileD.jpg

**Problems:**

- "his claws burst out" (need 2.32 s): the burst is the very end of a shot in both copies (n2_bus 84.95–86.17, creepiest ~333.4–334.54). Only 1.20 s is usable, so the renderer slows it to ~0.52x (above the 0.4x floor). Adding an extra cut at "lisa's friend kerry" (24.11) would leave only one fresh option: the same burst from creepiest, which is a duplicate. So I left it as one slowed shot. If the slow-mo looks bad, starting earlier (84.30, Kerry leaning in) gives 1.87 s, but then the claws only show from ~85.2.
- "climbs right out" n2_emerge 139.64 has 1.65 s clean for a need of 1.63 (no margin). The renderer keeps it at about 1.0x.
- s03 "in the showers" span is a face close-up (coach's mouth open, tiles visible). It is a true shower-room moment, but it does not show Freddy.
- "on the school bus" uses the bus arriving (46.22), not literally "speeding off". The speeding-off shot (n2_bus 86.17–105.5) is mostly a dust cloud with a tiny bus.

### n3: Dream Warriors (1987)

All n3 clips are 1920x1080, 23.976 fps, bt709 (SDR). None is under 720p and none is HDR.

Marks and graphics:
- **Grey MOVIECLIPS mark, bottom-left (y ≈ 885–970).** Present on n3_marionette, n3_primetime, n3_taryn, n3_wizard_rt, n3_skeleton, n3_nancy, n3_souls, n3_heres, n3_worm, n3_bed and n3_best4k. Faces and action in the chosen spans stay above y ≈ 860.
- **Rotten Tomatoes blue bumper at the clip end** (none of the chosen spans reaches it):
  - n3_marionette from 183
  - n3_primetime from 59
  - n3_taryn from 115
  - n3_wizard and n3_wizard_rt from 55
  - n3_skeleton from 102
  - n3_nancy from 148
  - n3_souls from 143.5
  - n3_heres from 207
  - n3_worm from 133
  - n3_bed and n3_joey from 125.5
  - n3_best4k from 592
- **No mark seen:** n3_marionette_uk, n3_primetime_wb, n3_wizard (old download), n3_real, n3_kristen, n3_creepiest and n3_joey (any mark there is under the bar).
- **End cards:** n3_primetime_wb has a dark frame plus a Blu-ray end card from 41. n3_real has a 4K end card from 296. n3_creepiest has an "own now" card from 1035.

Per clip:
- **n3_marionette** (vgbE09-4GTo): 0–4 puppets on the shelf · 4–8 Freddy-puppet face · 8–11 puppet claw · 11–13 Phillip asleep · 14–18 puppet walks · 19–44 Phillip in bed / Freddy · **44.3–45.07 wrist slit, veins emerging** · 45.14+ long bloody arm · 47 strings · 64–72 Phillip on strings in the ward · 73–84 strings / feet (gory) · 85–91 nurse · **92.3–94.9 Phillip walking on strings** · 99–117 Kincaid and Phillip's room · 133–141 nurses' station · 142–151 corridor · 152–160 kids at mesh · 161–170 Phillip at the window · 171–175 Freddy on the tower · 176+ fall · 179–182 kids · 183 bumper.
- **n3_marionette_uk** (no mark, about +1 s offset from the RT copy): **66.0–72.9 Phillip with vein strings, ward behind** · **172.1–~175.5 Freddy at the tower top pulling the strings (dark)** · 176 Phillip falling · ends 182.
- **n3_primetime**: 0 TV static · 1–17 Jennifer · 18–28 TV on the wall · 29–30 close · 31–34.5 TV arm sparks · **34.55–35.55 arms grab her (wide)** · 35.6–38.2 lifted to the TV · 39–50.5 Jennifer / TV-Freddy cut-ins (44–48 Freddy head) · **50.53–51.85 Freddy over the TV, then impact sparks (impact ~50.73)** · 51.9 dark door · 53–54 Kincaid · 55–58 aftermath · 59 bumper.
- **n3_primetime_wb**: same scene. 16 sparks · 17–20 lifted · 26–27 and 30–31 Freddy head · 33 impact · 35–36 Kincaid · **37.4–40.5 aftermath** · 41 end card.
- **n3_taryn**: 0–50 alley, Taryn · **52.8–57.8 Taryn and Freddy in profile** · 58–61 Taryn · 62–63 Freddy · 64–83 knife fight · 84–85 Taryn · **85.5–89.5 Freddy's syringe fingers** · 90 Taryn · 93–98 arm and syringe marks · 103–104 syringes in her arm · **110.4–114.9 low-angle Freddy face** · 115 bumper.
- **n3_wizard / n3_wizard_rt** (identical cut; _rt has the mark):
  - 0–1.2 empty wheelchair in the dream corridor
  - **1.37–2.8 Will next to the wheelchair**
  - 10, 31–32 Freddy silhouette
  - 23–25 green lightning
  - 26–28 flash
  - **32.9–36.5 Will in wizard robe, green magic growing in his hands**
  - 36.6 flash
  - 37–38 Freddy hit by green
  - 45–54 Freddy kills Will
  - 55 bumper
- **n3_skeleton** (dark): 0–33 junkyard, Donald and Neil · **35.86–37.9 Donald walking the junkyard** · 39 Donald · 40–48 skeleton · 50–53 Neil · 54–55 skull · 66–76 · **78.5–80.6 skeleton attacks Donald (handheld)** · **80.8–84 wide skeleton and Donald** · 85–87 Donald falls · 88–98 skeleton in the fog · 99–101 · 102 bumper.
- **n3_nancy**:
  - 0–3 "Dad" materialising
  - 4–7 Nancy enters
  - **8.4–12.9 "Dad" close-up**
  - 13–36 dialogue
  - 37.1–39.0 hug
  - **43.85–45.35 Freddy revealed, stabbing Nancy**
  - 45.4–46.0 reverse shot
  - 46.3–46.9 blood close-up (avoid)
  - **47.0–47.9 Freddy at her throat**
  - 48–52 Freddy dark
  - 53–73 Kristen fights
  - 74–82 Neil in the grave
  - 83–86 bones in the grave
  - **96.0–98.9 Neil with the holy-water bottle**
  - 100–108 Freddy hit by light
  - **106.83–109.4 Freddy bursting with light (wide)**
  - 109.8–112.4 Neil with the cross
  - 113–121 Freddy disintegrating / white flash
  - **122.2–127.0 Kristen holding the dying Nancy**
  - 128–147 Kincaid, Joey, Kristen and Nancy
  - 148 bumper
- **n3_worm**: 0–62 Kristen in the house (dark) · 63–68 worm swallowing Kristen · 72–95 Nancy and the Kristen sessions · **109.0–110.7 worm-Freddy face** · 111–112 Kristen and Nancy · **112.25–113.75 worm-Freddy face** · 114–132 · 133 bumper.
- **n3_souls** (red/orange lit):
  - 0–99 boiler room fight
  - 66 Freddy and Joey
  - **100.1–104.6 Freddy close-up**
  - 105–119 Freddy with a stick
  - 123–124 stick in his mouth
  - **125.0–132.9 Freddy grinning close-up**
  - 133–140 chest of souls
  - **141.5–143.4 Freddy medium shot**
  - 143.5 bumper
- **n3_heres**: Kristen's dream house (0–148), very little Freddy (149–150 a dark burnt figure) · 151–206 Kristen wakes and the bathroom · **194.6–~198 faucet handles become claws (claws from ~196.0)** · 207 bumper.
- **n3_kristen**: the same content as n3_heres, with no mark.
- **n3_real** (WB 4K, no mark): **0–21 Kristen in bed drawing, dozing (one shot from ~8, 4–7 drawing insert)** · 22–55 tricycle · 56–176 dream house · 178–194 Nancy · 214–215 and 218–219 worm-Freddy (= n3_worm footage) · 242–294 Nancy and Kristen's office talk · 296 end card.
- **n3_joey** (= n3_bed footage, same length): 0–1.6 Joey in bed · **1.63–5.6 Freddy in his sweater, bright** · 6–36 bed over the hell pit · 38–108 group dream / fire · 110–118 Dr. Simms and Neil · **120.0–125.2 Dr. Simms over Joey, Will in his wheelchair behind** · 125.5 bumper.
- **n3_best4k**: a compilation of the RT clips. 0–180 marionette scene · **140.3–142.3 nurses' station wide** · 142.4–149 corridor · **151.9–159.2 kids at the mesh window** · 180–240 primetime · 240–340 Taryn · 344–396 wizard · 400–496 skeleton · **504.4–506.9 Dream Warriors group in the dream house** · 508–590 mirror hall · 592 bumper.
- **n3_creepiest** (no mark, scanned at 5 s steps): it repeats the marionette, primetime, skeleton, dream house, worm, bed, souls and mirror-hall scenes. **1022.2–~1029 Joey hugs Kincaid, then Kristen and Nancy join (one shot)** · 1030 Nancy · 1035+ end card.

**Tile:** `('n3_joey', 4.20, 720, 290, 500)`. Checked by cropping and viewing: Freddy's face in a bright room, his own eye visible, sharp, natural colour, with the hat brim slightly cropped at the top. The face is turned three-quarters to the right, not straight to camera. The only front-facing Freddy faces are red-lit (n3_souls 100–104, 125–132), and the souls crop looked worse.

**Problems:**

- **The surviving trio:** no shot of only Kristen, Kincaid and Joey was found. The chosen mirror-hall shot also shows Nancy.
- **"Bones burning":** no literal shot exists in these clips. The line uses Freddy's body bursting with light as Neil consecrates the bones.
- **Tight spans** (clean picture is only slightly longer than the screen time needed):
  - s00 `turn you into` (0.65 vs 0.60)
  - s00 `through a tv` (1.15 vs 1.12)
  - s09 `herself` (0.80 vs ~0.72)
  - s01 `is how dangerous` (1.40 vs ~1.28)
- **Dark spans:** marionette_uk 172.20 (Freddy on the tower) and the skeleton junkyard shots are dark. They are readable but are not bright frames.

### n4: The Dream Master (1988)

**n4_junkyard** (RT Horror 4K, 1080p, 176.0 s): 0–7 red title/hell visuals plus one white frame; 8–34 Kincaid and the dog in the dark junkyard; **35.9–40.3 Freddy silhouette rising (hat), blue sky**; 40–53 Kincaid (84.8–87.0 Kincaid shouting, clean); 54–66 Freddy from behind walking among the cars (dark); 90–135 the car pile-up, sparks, aerial of the car grave; 136–137 Freddy grabs Kincaid; 138–141 Freddy and Kincaid (dark); 142–144 closer; **146.8–153.8 Freddy grinning, claw on Kincaid's chest**; 155–165 Joey's bedroom; **165.5+ blue RT end card**. No mark at the bottom-left.

**n4_reborn** (Flashback FM fan, 1080p, 264.4 s): the same junkyard scene plus extra red hell-resurrection footage (32–100). Offset about +98 s from junkyard (junkyard 138 = reborn ~236). 236.3–239+ Freddy holding Kincaid (one shot, dark). 244–250 = junkyard 147–153 (do not reuse). No logo seen.

**n4_waterbed** (Warner Bros., 1080p, 48.2 s): 0–3.2 Joey pressing on the waterbed from above (dark); **3.4–4.8 Joey's face under the surface**; 5–7 Freddy bursting out; 8–12 Freddy holding Joey (bright); 13–33 Joey dragged in; **from 43 a WB "Nightmare collection Blu-ray, March 5" end card**. No nudity seen in 0–14.

**n4_nurse** (RT, 1080p, 69.3 s): bright hospital room, nurse with glasses and Kristen in bed; 42–45 blood on the nurse's back; **45.9–48.9 nurse-Freddy close-up, very bright, front-facing, hat, eyes wide** (Tile); 50 Freddy full figure; 51–52 syringe; **from 59 the RT end card**. Not used for shots (see Changes).

**n4_beach** (RT, 1080p, 138.2 s): 0–17 water, the glove fin, Kristen sunbathing (bikini, no nudity); 18–35 beach, Kristen sinking in the sand; **36.4–38.85 bright Freddy close-up with sunglasses (frame 0)**; 39.0–40.1 Kristen screaming close-up; **40.3–42.9 Kristen in the sand, Freddy's legs**; 43–57 Freddy overhead, Kristen pulled under, Freddy laughing; 58–126 dark/green boiler-room dream; **from 127 the RT end card**.

**n4_hell** (Flashback FM fan, 1080p, 260.4 s; a long compilation of the Kristen dream): 0–85 the same beach footage as n4_beach (do not reuse those moments); 88–180 dark boiler room, green-lit Kristen; **182.45–184.2 Freddy close-up, chains, red light**; 184–185 furnace; 186–201 Kristen and Alice embrace (196.9–199.4 Freddy with glove, dark green); **202.3–203.8 Kristen and Alice running, Kristen green-lit**; 204–206 Freddy dark close-up; 207.2 Alice; **207.6–209.0 furnace burning**; 209–210 Alice; 210.7–215 Freddy at the furnace, Kristen's soul glowing on his back; 216.6 Freddy wide; 217.2 white flash; **217.5–219.0 Freddy's back with soul faces**; 219.3 Alice; 224–256 Alice at home, "Greetings from Hell" postcard. No logo seen.

**n4_kiss** (RT, 1080p, 189.6 s): classroom; 0–44 Sheila with glasses, test paper "Learning is Fun with Freddy" (blood on the paper at 42–46); **46.2–47.9 wide classroom: Alice, Sheila, classmates**; 48 Alice; 54–56 claw on the paper (overhead); 76–92 apple and Freddy's claw; 96–104 Freddy at the blackboard; 113–121 Sheila profile, finger at her lips; **123–127.9 Freddy's face closes in on Sheila**; 128–132.6 profiles; **132.7–134.4 wide, Freddy's kiss on Sheila**; 134.5–135 brain-like close-up; 135.2–136.9 Freddy and Sheila; 137–145 Sheila's corpse face, Alice screaming, Freddy wide; **169.1–171.6 Rick, Dan and friends**; 172–178 classroom; **from 179 the RT end card**.

**n4_karate** (RT, 1080p, 188.9 s): 0–80 Rick at school, lift, Kristen in the dream; 82–110 dojo, fog; 112–119 Rick hit and thrown by the invisible Freddy (fast cuts); 120–125.6 Rick on the floor; **125.8–127.8 Rick close-up**; 128–167 Rick with stick, the claw-glove on the ground; 170–176 classroom; **from 178 the RT end card**. Freddy is invisible throughout the fight.

**n4_roach** (RT, 1080p, 179.7 s): 0–29 Debbie bench-pressing, Freddy over the lamp (3, 21–24, 35.2–36.9 Freddy forces the bar down), **10.8–12.9 Debbie's face**; 25–28 elbow and bar on her throat; 29–36 car outside the gym; 37–47 Debbie's arms snap (gore at 44–47; avoid); 48–100 Debbie, the diner, the bike (101–117 cuts every ~1–3 s); **105.3–107.8 Debbie with roach legs out of her arms**; 118–129 stuck in goo; 130–136 head becoming the roach (dark); 136–154 Alice and Dan outside the diner; 155–157 roach close-up; **157.6–161.9 full roach Debbie on the floor**; 162–165.9 roach in front of the eye on screen; **166.4–168.7 roach-head close-up**; 169 wide; **from 169.6 the RT end card**. **No roach-motel shot is in this clip.**

**n4_alice** (RT, 1080p, 169.7 s): church finale, dark green/red. 16–19 Freddy wide (dark); 30 and 32 Freddy laughing; **39.7–41.9 Freddy screaming/laughing close-up, green behind**; 54–60 fight; 62 and 68 Freddy close-up; **97.0–108.5 Freddy creeping behind Alice (one long shot)**; 110–115 dead body; **124.4–126.9 Alice glowing close-up**; **129.0–131.0 Freddy close-up**; 133–136 claw; 137–141 Alice charges; 142–144 the blast hits Freddy; **146.1–149.5 wide, Alice firing the blast**; 150 Freddy screaming; 156–159 Freddy's chest of souls; **from 159.5 the RT end card**.

**n4_soulfood** (RT, 1080p, 96.2 s): diner, bright but blue-grey. 0–44 Alice, waitress; 45–54 Freddy and Alice at the table; 55–56 pizza; **59.1–60.45 soul faces in the pizza**; **63.1–64.6 Kincaid's face in the pizza**; 66–67 the claw takes a meatball; **68.0–71.9 Freddy close-up with the soul meatball** (tilt-up from 68.0, hat visible from 68.6); 72 Alice; **73.1–74.9 screaming soul meatball on the claw**; **75.0–77.9 Freddy eating it**; 78–82 Alice; **83.0–85.9 Freddy close-up**; **from 86 the RT end card**.

**n4_soulpizza** (Warner Bros., 1080p, 78.2 s): a shorter edit of the same diner footage (pizza souls at 35, Kincaid at 39, meatball at 49–50, Freddy eating at 51–53); **from 73 the WB Blu-ray end card**. Not used, so diner moments are not duplicated.

**n4_doctor** (RT, 1080p, 135.8 s): Dan in hospital (0–13, mask Freddy at 4–10); Alice; green hospital, the tunnel; **56.8–58.9 Freddy close-up, red background, claw raised**; 59–79 silhouettes, tunnel, stained glass; 80–110 church, Dan wounded; 116–124 surgery; **from 126 the RT end card**.

**n4_torn** (RT, 1080p, 126.5 s): 0–4 Freddy (dark); 5–21 Alice by the wall; 22–23 souls on the balcony; **28.0–33.2 Alice lifts the stained-glass shard toward Freddy** (Alice's reflection in it); 33–35 Alice close-up; 36–37 Freddy; 38 white flash; 39 Freddy screaming; 40–53 red/white flash (avoid); 54 Freddy eye; 56–59 Freddy convulsing; 60–62 Alice; **72.0–73.9 Freddy, claws up, souls writhing in his chest**; 84–96 arms bursting out of him (cuts every ~0.3–1 s; blood); **97.5–98.9 arms pulling him apart**; 99–114 face splitting (avoid as the most extreme); **from 116 the RT end card**.

**n4_death** (Flashback FM fan, 1080p, 291.5 s): extended ending: 0–1 souls on the balcony; 2–6 Alice; 7–11 the shard; 12–14 Alice; 15–16 Freddy; 16.25–17.0 Alice raising the shard; 17.0 flash; 17.45–17.8 Freddy screaming; 17.85–18.3 Freddy face with shard and Alice; **18.45–19.3 Freddy's reflection in the mirror (push-in to the mouth)**; 19.4–30 red flash; 32–115 souls tearing him (gore); 116–196 the light, the church; 200–265 fountain epilogue; **from ~276 end credits**.

Marks: I checked full-frame bottom crops (y 780–1080) of beach, soulfood, kiss, roach, alice, hell, waterbed and reborn. None of the n4 clips showed the grey "RT MOVIECLIPS" mark, a channel bug or a ClipZone bumper. The only graphics are the RT blue end cards and the WB Blu-ray end cards at the clip ends listed above, and the credits on n4_death.

**Tile:** `('n4_nurse', 47.00, 1250, 560, 860)`: nurse-Freddy, front-facing, very bright, eyes wide open, hat brim at the top. Checked with `crop=860:860:820:130,scale=400:400` → `beats\n4\tile.jpg`.

**Problems:**

- **No roach-motel shot in any n4 clip**, so "crush you" is the barbell crush and "like a bug" is the finished cockroach. If the roach motel is required, another source would be needed (I downloaded nothing).
- **The actual furnace throw is not in n4_hell**. It is shown only as Kristen's run-up, then the burning furnace.
- Short spans that the renderer will slow: "his own reflection" (about 0.63x; drop this NEW CUT if that is unwanted, and the torn shard shot covers the whole phrase, since its clean span is 4.9 s), the s11 kiss (about 0.86x), "so the souls inside" (about 0.94x), "stays trapped" (about 0.96x).
- I assumed n4_nurse is n4 (see Changes). It is used only for the Tile.
- Many n4 finale shots are dark (junkyard silhouette, torn, hell). The brightest Freddy shots went to frame 0 and the L shots.

### n5: The Dream Child (1989)

Every clip is 1920x1080 bt709 SDR. The 4K-titled RT uploads are 1080p files.

The RT MOVIECLIPS mark (grey, bottom-left) is on n5_forcefed4k, n5_son4k, n5_hell4k, n5_baby4k, n5_drunk and n5_motorcycle.

These clips have no mark: n5_force_feed, n5_back_to_hell, n5_baby (older copies), n5_tricks and n5_pool. n5_superfreddy, n5_itsaboy and n5_schoolsout are WB uploads with no bug until the end card.

End cards:
- RT clips: blue Rotten Tomatoes end card in the last about 8–10 s (forcefed4k/force_feed from 80, motorcycle from 88, drunk from 88, tricks from 104, son4k from 206, hell4k/back_to_hell from 160, baby4k/baby from 144, pool from 144).
- WB clips: Blu-ray "March 5" end card (superfreddy from about 67, itsaboy from about 65, schoolsout from about 47).

**n5_force_feed** (1080, clean; same timing as n5_forcefed4k after 4 s)
- 0–2: mother's face. 4–6.38: glove over the table food.
- 6.38–about 8.5: wide table shot, Freddy spoon-feeds Greta. Cut before 8.77 (closer two-shot).
- 12.47–14.22: Freddy close-up grinning. 14.22–about 15.9: glove hand on Greta's head, spoon in her mouth. Cut, then the mother (16–17).
- 18–19: stuffed-face close-up (extreme, avoid). 19.77–20.85: man laughing.
- 20.85–22.5: man and woman eating.
- 22.5–about 28.2, one shot: Greta in profile with stuffed cheeks. Freddy enters about 22.9 and grabs her face (23.5–28).
- 28.2: face-to-face. Then about 28.4–34.6 from behind: Freddy crushing Greta.
- 35–43: various reactions (37.45–39 bearded man, 39–40.17 mother, 40.17–43.4 Freddy with Greta).
- 45–68: Alice's kitchen / fridge. 72–75: Greta screaming at the table. 80+: end card.

**n5_forcefed4k**: same as above with the RT mark. 0–about 2: glove close-up.

**n5_tricks** (no mark, dark)
- 0–3: Freddy in the corridor. 4–18: corridor wides (very dark).
- 20.0–about 21.8: Freddy close. He turns: 21.6 back → 22.0 face. Continuous to about 26.0.
- 26–30: Freddy walking away.
- about 47–53: Freddy crawling, face turning to camera, bright (best face 51.2). 54: Freddy climbing.
- 56–80: souls' hands. 66–67.3: Alice crouching. 82.5–84.3: Alice yelling. 104+: end card.

**n5_back_to_hell** (= n5_hell4k without the mark)
- 5–7: Freddy and Jacob on the stairs. 9–13: Jacob.
- 24.0–about 26.0: Jacob close. 26–28.7: Freddy and Alice.
- about 28.9–31.1: Jacob close (eye makeup). 31.4: Freddy.
- 36–40.1: Freddy and Alice. 40.1–about 45: Freddy close; the crane pulls back to show Freddy and Jacob.
- 46: Jacob. 49–50: nun on the stairs (wide). 53–54.3: Freddy. 54.45–55.65: Jacob. 55.7–57.8: Freddy.
- 58.6–63: Freddy's face distorting. 64–65: Alice.
- 73.7–76: souls tearing out of Freddy. 77–78.9: nun on the stairs.
- 79.2–about 81.9: Freddy stretched apart. 82: Freddy screaming.
- 98.2–100.27: nun close-up. 100: Freddy face (stained glass).
- 106–116: Freddy shredding / baby-Freddy. 117–131: baby Freddy, nun's robe.
- 132–137.5: Alice picks up the baby. 138.1–141.05: nun close-up. 141–143: glow/white flash.
- 146–147: nun. 148–153: Alice and the glowing baby. 153–159.5: Alice, hands on her belly.

**n5_son4k** (RT mark)
- 0–10.3: Jacob in the tower. 10.3–22.9: Freddy and Jacob at the stained-glass window (wide).
- 22.94–25.65: Jacob, glove at his throat. 25.65–27.07: glove and Jacob. 27.07–about 30.3: Jacob holding the glove.
- about 30.3–33.24: Alice in the boiler/tower set. 34.78–39.46: Alice close-up (bright).
- 39.46–46.0: upside-down stair wides. 46.05–48.21: Jacob with Freddy beside him.
- 48.21–50.43: Freddy crouching by the window.
- 54–62: Freddy upside-down stairs. 66–98: Dan/Alice M. C. Escher stairs.
- 100–140: dark set, glowing floor. 142: Jacob. 144–152: Alice. 164–200: Freddy/Alice merging faces. 206+: end card.

**n5_superfreddy** (WB, dark, greyscale scene)
- 0–5.7: Freddy in the dark. 8.3–10.3: Freddy. 12–24: Super Freddy and sparks.
- 26.23–about 27.4: Freddy. About 27.5–29.99: pan up Mark, half paper.
- 29.99–36.04: Mark turning to paper (tilt down to his paper legs).
- 36–43: Freddy / paper Mark. 44.88–45.7: paper Mark's face (two short shots).
- 45.75–46.93: Freddy's glove slashing. 46.96–48.13: Mark screaming, glove tearing paper.
- 48.13–49.30: Mark screaming in strips. 49.3–55: shreds / Freddy.
- 56–66: comic book, bloody hand. 67+: Blu-ray end card.

**n5_motorcycle** (RT mark)
- about 0.6–3.5: Dan on his bike. 4–7: tyres burnout. 8–13: smoke and road.
- 22–29: Dan's face and the glove at the bars. 30–33: road.
- 33.9–34.97: Dan's face, bloody. 34.98–about 37.0: wires into his shoulder. 37.2: speedometer.
- 44: Freddy-bike face. 54–56: arm fused. 58: Dan screaming.
- 62.48–63.15: Dan fused, cables. 69.7–73.2: the Dan/bike creature (flesh, skull).
- 74–80: bike on the road. 84–86: skull close-up (extreme, avoid). 88+: end card.

**n5_drunk** (RT mark)
- 0–7: Dan driving. 8–9: radio. 10–19: Dan. 20–41: road and the truck. 42–48: Freddy's hands.
- 48.34–50.1: Dan. 50.2–53.4: Freddy at the wheel with a bottle. 53.6: Dan.
- 56–70: struggle. 72: Dan. 78–86: crash / pool. 88+: end card.

**n5_pool** (no mark)
- 10–22: Yvonne climbing to the diving board. 24–30: pool / Yvonne in her swimsuit from behind (no nudity). 34–38: Yvonne screaming.
- 52: diving board over the abyss. 54–62: Yvonne falling. 70: splash.
- 74–100: Alice in the boiler water. about 102.5–106.1: Freddy's head rising from the water. 106: Alice.
- 108–116: Freddy. 120: Freddy with Yvonne chained (wet clothes, no nudity).
- 126–130: Freddy and the pipe. about 135.6–137.9: Freddy lunging, arms out. 144+: end card.

**n5_baby / n5_baby4k** (same footage; the 4K copy has the mark)
- 0–9 and 20–25: baby Freddy screaming. 24: Alice. 26–135: church collapse (very dark/blue).
- 120–about 130.2: Freddy, arms spread before the church window. 132–141: Alice. 144+: end card.

**n5_itsaboy** (WB)
- 0–3: glove. 4: Alice. 12–27: Freddy silhouette at the window. 30–38: Alice.
- 40: Alice and Freddy. 44–49: nun in the doorway.
- 50.51–52.22: Freddy close-up grinning. 52.2–53.1: Alice. 54: nun. 56: Alice and Freddy.
- 60.6–about 63.0: Freddy under the hat, glove up, fog; the fog darkens the frame after 63.
- 65+: Blu-ray end card.

**n5_schoolsout** (WB): the same tower scene as back_to_hell 0–47 (Freddy/Jacob/Alice), darker. 47+: end card. Not used.

**Tile:** `('n5_tricks', 51.2, 1185, 585, 600)`: front-facing Dream Child Freddy, both eyes visible, lit, sharp.

Verified crop: beats\n5\tile.jpg. The frame has thin letterbox bars (y < about 20, y > about 1060).

**Problems:**

- The film has no pregnant-Alice shot in the clips. "he finds a sneaky" uses Alice with her hands on her belly from the ending (back_to_hell 155.0), and is flagged above.
- Some spans are close to the time needed:
  - and in the end: 2.85 vs 2.77
  - through the dreams after the split: the shot is 2.05 s for 1.44 needed, fine
  - before slicing him / pieces: 1.12 vs 1.00 / 0.90
  - jacob uses the power: 1.8 vs 1.12, fine
- n5_superfreddy 45.80–46.9 is mostly motion blur: Freddy's glove is readable at about 46.1–46.4 only.
- The Dan/bike creature (motorcycle 70.4) is gory but medium, not the skull close-up at 84–86.
- s11: n5 only offers the alternative line; the plan prefers `n4_kiss`.

### n6: Freddy's Dead (1991)

All 17 n6 clips are 1920x1080 bt709 (not HDR). n6_game is an SD source upscaled into 1080p (soft, about 0.69 Mb/s, 24.05 fps).
Bottom-left marks: only **n6_maggie** carries the grey "RT MOVIECLIPS" mark (y about 885-970, the whole clip). I checked n6_forever, father, doom, nice, busrt, brain and game at those coordinates: no mark. Rotten Tomatoes clips (forever, father, busrt, ear, nice, drug, doom, brain, maggie) end in a blue RT end card. WB clips (oz, playground, chalk, blood) end in a "NIGHTMARE ON ELM STREET Collection - March 5" Blu-ray card. n6_town ends in a "Look for it on 4K" card.

**n6_forever** (oRc1Pcmujf0, 1080p) - Doc vs Freddy in Doc's room
- 0-26.9: Doc alone with a punching bag and lockers (dark). 28-33.5: Freddy wide in the room. 33.5-35.5: Freddy close-up. 38-64: fight, Freddy on the floor, baseball bat.
- 66.97-75.81: Freddy close-up, front, grinning, x about 760 (USED s01). 77.25-83.84: Freddy close-up, glove at his chin (USED s11). 83.84-85.09: Doc.
- 85.09-92.24: big Freddy close-up, finger raised (USED s05 rank). 93.74-99.25: Freddy medium, ceiling slats.
- 99.25-104.50: big Freddy face, side-lit, laughing (USED "all those jokes"). 105.67-116.60: Freddy medium under the slats, flexing claws (USED "survival rate").
- 118.5-124.3: Freddy/Doc wide and medium. 126.6-133.1: low-key Freddy face. 134-143: Freddy grabs Doc. 144-147: Doc wakes. 147.5-end: RT end card.
- Tile frame 70.0.

**n6_father** (9G9YrZ3WWJI) - Tracy's dream of her father
- 0-94: Tracy's father harasses her in the kitchen (no nudity, a hand grabs her). 94.18-99.63: father's burned face. 99.63-109.22: Tracy, then Freddy.
- 111.47-117.48: Freddy with his glove up, sneering (USED). 117.48-135.70: fight, short cuts.
- 135.70 to about 141.4: Freddy snarling close, Tracy behind him (USED 136.05, clean taken to 140.75). About 141.5-143.26: Tracy and Freddy's hand.
- 150.38-158.97: Tracy burns her hand on the stove to wake. 158.97-162.76: Tracy jolts awake in bed, Maggie enters (USED). 163.9-168: Maggie and Tracy. 168-end: RT card.

**n6_town** (Wt9aXGoNvOE, WB 4K trailer cut) - does NOT show the empty Springwood
- 0-6: Doc and Tracy with the punching bag. 8-35: Maggie with the newspaper, talking to a counsellor.
- 36.76-39.76: empty rainy night street, a car passes (USED). 39.76-42.55: taxi in the rain. 42.5-61.5: near-black alley, a woman, a skull graffito.
- About 61.6-64.62: "NINE, TEN, NEVER SLEEP AGAIN" newspaper box, push-in, readable from 61.85 (USED). 64.62-70: clouds.
- 70-90: Tracy restless in bed. 90-92: Maggie asleep. 92-200: sunny 1950s yard, Fred Krueger human (124-132), young Maggie, the shed. 200-296: Freddy and Maggie in the shed (the same scene as n6_blood/n6_daughter). 296-300: Elm St sign, Maggie wakes. 301.6-end: 4K ad card.

**n6_oz** (TN7BmVcVMgI, WB) - 0-32: Spencer's room wrecked. 32.78-36.46: Spencer at the window. 37.55-44.97: Freddy on the broomstick outside the window (USED). 44.97-46: Spencer. 46-end: Blu-ray ad.

**n6_playground** (OBFSVlf7KRQ, WB) - John Doe's parachute dream (same scene as n6_doom 64-135)
- 0-16: John hanging under the parachute (shirtless, no nudity). 16-48: Freddy appears on the cords.
- 48.26-49.59: Freddy close. 49.59-52.18: Freddy dangling beside John, slicing his cords (USED). 52.18-53.64: claw on a cord.
- 61.35-62.42: wide sky. 62.42-63.42: John screaming as he falls. 63.4-66: falling into fog. 66-end: Blu-ray ad.

**n6_ear** (nCPo6RIL--Q) - Carlos in the shelter hallway; Carlos's mother with a cotton swab 94-100. 104-126: Freddy grabs Carlos by the ear, and there is ear gore at about 126 (not used). 152-end: RT card.

**n6_earcheck** (h3F1b7vsG84, ClipZone, 7 min, scanned at a 4 s step) - Carlos's whole sequence, the same footage as n6_ear and n6_nice. Not used.

**n6_nice** (f10YpGCYqBo) - the Carlos boiler room
- 20.0-22.27: Carlos on the grating. 22.27-26.59: Carlos's head moves into frame and he fiddles with the hearing aid (readable from 22.55, USED). 26.82-28.07: hearing aid in the ear, close.
- 34: hearing aid close-up (morphing). 124-150: Freddy at the chalkboard, claws close. 152-157.88: Carlos. 157.88-159.63: ear close (gory morph).
- 159.63-162.17: Carlos screaming, clutching his head (USED). 164.3-166: distorted face. 167-168.5: explosion and dark frames (avoid). 169.3-177.5: Freddy laughing. 178-end: RT card.

**n6_chalk** (H8u6YTg-Vm4, WB) - 0-3.6: Freddy's claws by the blackboard. 4-13.68: Freddy at the board, wide. 13.68-16.85: claws on the blue chalkboard, close (USED). 16.85-35: Carlos reacts and his face distorts (31.7-35 is the most extreme). 36-43: Freddy. 44-end: Blu-ray ad.

**n6_game** (X-zwfV7O5a8, fan upload): an SD upscale in a 1080p frame, soft but clean. No watermark or channel bug seen at 8, 108 or 150 s, or in the 2 s sheet.
- 0-1.71: Spencer in the game. 1.71-6.40: the TV and the game. 6.40-10.30: Spencer as a sprite jumping in the factory level (USED). 10.3-10.45: crossfade. 10.45-13.27: the next level.
- 18, 22, 30, 36: Freddy at the controls. 52-54: Freddy close.
- 105.12-112.06: Freddy close-up, Power Glove on his claw hand, glove visible from 107.7 (USED 107.70). 116-154: more Power Glove close-ups. 136 and 148: "FREDDY / SPENCER" score screens.

**n6_drug** (HLp--dS6hj4) - 0-20: Maggie, Tracy and Carlos outside the house at night. 20-56: Spencer stoned in front of the TV, the PSA on the TV, Freddy on the TV at 48 and 56. 58-60: the room. 60-end: RT card. Spencer being pulled into the TV is NOT in this clip.

**n6_doom** (-0Abt9-xYx4) - John Doe
- 0-28: John in the shelter, a fire dream. 28.09-32.34: dark.
- 32.34-40.35: "Welcome to SPRINGWOOD" sign, dolly to the road (USED 32.40). 40-60: John asleep in the van, the parachute begins.
- 64-118: parachute, Freddy on the cords. 118.17-120.76: Freddy dangling and cutting (the same moment as playground 49.6, do not use). 120.76-122.22: claw slicing a cord (USED).
- 125.18-125.72: John. 128.60-129.60: Freddy. 131.01-132.01: Freddy laughing. 132.01-about 132.85: John screaming as he falls (USED), whites out into fog at about 133.4.
- 135.84-141.22: Freddy rolling the bed of spikes into place on the dark road (USED). 144.6-148.3: rapid falling shots and a spike-bed insert (about 147.8, avoid). 148.77-151: John screaming. 152-end: RT card.

**n6_busrt** (HZKvV93kSTs) - 0-5.17: John at the ticket booth. 5.17-26.8: the bus driver and John. 28-50: the bus ride, Freddy driving (38). 54.84-56.38: John flung past the Springwood sign. 56.38-57.67: John lands on the road. 57.67-59.93: John lying on the daylight road (USED). 63-76: the ghost-boy effect and Freddy. 78-85: Freddy by the bus. 86-end: RT card.

**n6_maggie** (ZeKr2ioH84E) - RT MOVIECLIPS mark bottom-left for the whole clip
- 0-2.42: Freddy grabs Maggie in the basement, wide (USED). 2.42-36: the fight.
- 134.59-135.97: an arrow. 135.97-137.80: Freddy close (1.8 s).
- 204.51-207.80: Maggie jamming the pipe bomb into Freddy's chest, Freddy screaming (USED). 213.9-219: Maggie and Freddy face to face. 219-225: Doc and Tracy. 225.66-228.78: Freddy's shocked face.
- 228.78-229.8: fireball. 229.8-about 231.3: Freddy's head in the explosion (USED). About 231.3-232.82: debris. 232.82-end: RT card.

**n6_brain** (E7gprpahuPs) - 0-43: Maggie with 3D glasses, the dream-demon carving. 43.4-47.26: Freddy's face bursts out of the demon wall screaming, push into his eyes (USED 43.60). 47.5-48.8: black. 48-128: the inside of Freddy's mind (dark, effects). 130-195: 1940s school flashback, young Fred, the strange adults and kids at 174-176. 196-end: RT card.

**n6_blood** (O0bb2X4dGPA, WB) - 0-6.8: black. 7-18: Freddy's legs, sweater and hat. 18-23: young Maggie arrives. 23.4-27: Freddy with the drawing. 28.70-33.83: Maggie in her child's dress, close (USED). 34-90: "you are my blood" dialogue. 94-end: Blu-ray ad.

**n6_daughter** (W2hGXPJOXao, ClipZone, scanned at a 4 s step) - 0-28: Tracy and Maggie in bed. 28-130: the 1950s yard and young Maggie. 130-230: the shed with Freddy (the same footage as n6_blood/n6_town). 236-380: Tracy at the sink, then the father dream (the same as n6_father). Not used.

**Tile:** `('n6_forever', 70.00, 760, 420, 760)` - Freddy front-facing close-up in Doc's room, both eyes visible, sharp. Checked the crop `crop=760:760:380:40,scale=400:400` (tile.jpg in beats\n6\).

**Problems:**

- The empty Springwood, carnival, strange adults and missing-children posters are not in any downloaded n6 clip. I substituted the Springwood sign, the empty rainy street and the "NINE, TEN, NEVER SLEEP AGAIN" headline. n6_town 36.80 is a dark shot.
- The "drags him into the real" pull-out is not in any clip; I used the start of the real-world basement fight instead.
- Two shots are slightly short: 'john doe' NEW CUT (0.80 s against 0.83, about 0.96x) and 'almost every child' (2.75 s against 2.70, about 0.05 s slack).
- n6_game is soft (SD upscale). It is used only for two 1 s shots.

### n7: New Nightmare (1994)

All 15 clips are 1920x1080, 23.976 fps, SDR (bt709). None is under 720p.

**RT mark:** none of the Rotten Tomatoes Horror clips used here (julie, funeral, missme, stalks, end, surgery, traffic) shows the grey "RT MOVIECLIPS" mark. I checked bottom-left crops every 8 s and every chosen in-point frame. These clips have thin black letterbox bars (about 20 px top and bottom). Each one ends on the blue Rotten Tomatoes end card: julie 144+, funeral 138+, missme 138+, stalks 82+, end 142+, surgery 106+, traffic 168+.

**n7_coming** (WB 4K, 326.6 s; the lair finale)
- 0–9.2: dark pink-lit Freddy-skin wall / lair spikes, Heather enters
- 10–56: Heather swims through the flooded temple, then in the lair
- 132–153: script pages on screen (text inserts)
- 186.54–188.63: Freddy face close, snarling (s01)
- 250.42–251.25: Freddy, blue light, only 0.83 s
- 305.25–308.05: Freddy rises out of the smoke (rank card)
- 320–326: "LOOK FOR IT ON 4K" end card. Do not use.
- Dark scenes produce many false cuts; trust the strips.

**n7_coming_uk** (WB UK, 301.1 s; the same finale, a different cut)
- 0–1.63: Dylan walks into the jungle part of the lair
- 1.63–4.92: Dylan climbs the temple stairs
- 20–22: Freddy leaning in. This is the same moment as coming 305; do not use both.
- 36.38–40.13: Freddy's head through the window, Dylan at right
- 43.81–45.77: Freddy reaches his claw toward Dylan. Same window setup as 36.4, a different moment.
- 51.73–~54.85: Freddy face close, claws
- 101.75–103.42: Freddy peering round the door, striped arm out
- 111.01–113.35: Freddy screaming close-up
- 116–124: Freddy's mouth stretched huge
- 154–196: tongue/snake attack behind the lattice
- 206.5–208.2: Heather and Dylan together, with Freddy's claw at right
- 215.09–216.75: Freddy shoved into the flames
- 226.77–231.09: Freddy engulfed in the furnace
- 232–236: demon Freddy burning
- 240–268: escape and explosion
- 270–285: waking in the bedroom
- 286–301: "OWN NOW ON DIGITAL OR DISC" end card

**n7_dylan** (WB 4K, 397.2 s)
- 0–118: Heather and Robert Englund on the phone. This is Englund out of makeup, not Freddy.
- 6.08–16.30: Heather close-up, one continuous shot drifting to the window
- 98, 118–128: Englund's Freddy paintings
- 128–330: night; Dylan's bed; claws in Heather's bed (same as n7_stalks); Dylan with the glove
- 330–388: day; Heather wakes; kitchen with Dylan
- 390–397: "LOOK FOR IT ON 4K" end card

**n7_handbed** (ClipZone, 439.4 s): the same material as n7_dylan.
- 428–439: ClipZone bumper. Do not use.
- No ClipZone bug seen in the sampled frames before 428. Not used.

**n7_end** (RT, 152.1 s)
- 0–36: Heather in the lair with the script (script-page inserts 14–35)
- 39.29–43.71: Heather and Dylan hug
- 52–80: Freddy attacks, Heather wounded
- 116, 132: Freddy
- 142+: RT end card
- No furnace in this clip.

**n7_funeral** (RT, 147.7 s)
- 0–5.25: the casket
- 5.25–19.14: one dolly shot, Heather then the whole family (Dylan, Julie)
- 34–36: "BONES" grave
- 44–110: Freddy's claws drag Heather into the grave (the claw is short)
- 138+: RT end card

**n7_hand** (WB UK, 162.0 s)
- 0–1.42: two effects men with the glove rig
- 4.13–9.22: Chase, Dylan and Heather at the FX workshop
- 16.18–17.31: glove rig close
- 30.46–33.50: effects man with his mug behind the rig
- 46–53: rig close-ups
- 84.75–86.21: the glove crawls on the floor past an ankle
- 88.09–89.59: effects man clutching his throat
- 89.59–91.13: second man screaming, slash on his shirt
- 91.13–93.25: glove slashing the man on the floor
- 98–146: Heather's nightmare, Chase hugs Heather
- 148–162: WB logo and "OWN NOW" end card

**n7_julie** (RT, 154.8 s)
- 0–10: Julie and Dylan in the hospital room
- 11.75–15.00: Julie, Freddy appears behind her
- 15.00–16.42: Freddy, low angle
- 31.06–34.52 and 35.88–37.75: Freddy with the glove behind Julie
- 40–58: Heather and the doctors (bright)
- 64–69: Freddy kneels over Julie
- 73.33–75.55: Julie dragged, feet on the wall, blood
- 76.50–79.55: Freddy walks up the wall and ceiling dragging her
- 84–112: blood on the ceiling. Avoid.
- 122–132: Heather in the corridor
- 140–143: Julie dead (gore)
- 144+: RT end card

**n7_missme** (RT, 147.6 s)
- 0–20: bright; Heather with coffee and the TV
- 11.33–13.96: Heather looks up in fear
- 22–138: dark blue bedroom attack
- ~81.55–83.23: Freddy's face rises out of the dark
- 104.5–107.6: Freddy grabs Heather (short shots)
- 109.51–111.34: Freddy lower face, deep shadow
- 138+: RT end card

**n7_stalks** (RT, 91.9 s)
- 0–24: covers in Dylan's bed
- 18–26: claws through the sheets
- 28–35: Heather asleep, cut on her cheek
- 42.59–45.34: claw over Heather's face
- 45.34–58.3: claw shots
- 60–80: Heather wakes in the bed
- 82+: RT end card
- No scared-Heather moment.

**n7_surgery** (RT, 116.0 s)
- 0–70: Dylan in the oxygen tent, Heather sedated
- 70.92–72.75: the doctor with the glove
- 72.75–73.30: Freddy as the doctor (about 0.55 s only)
- 73.3–75: claws at the ceiling light
- 76–104: doctors argue
- 106+: RT end card

**n7_son** (WB UK, 182.9 s): the same sequence as n7_traffic.
- 0–22: hospital corridor
- 24–50: Heather driving
- 96: Freddy on the moon
- 98–166: freeway
- 168–183: "OWN NOW" end card
- No usable Freddy close-up. Not used.

**n7_traffic** (RT, 178.0 s)
- 0–22: hospital
- 24–50: driving
- 72.61–73.74: Dylan close-up, night
- 82.42–85.67: Dylan walks across the freeway between cars
- 95.88–97.35: Freddy on the moon and clouds
- 98–166: freeway chase; Heather hit at about 134
- 168+: RT end card

**n7_bloodiest** (WB UK compilation, 1516.0 s)
- I checked every 6 s across the whole runtime, plus 1 s over 1036–1160 and 0.5 s over 1278–1312.
- **No title cards, captions or chapter graphics between the segments.** The only graphics are the WB logo at about 1500 and "OWN NOW ON DIGITAL OR DISC" over 1500–1516.
- Segment order, all New Nightmare footage:
  - 0–140: lair finale
  - 144–282: Julie in the hospital
  - 288–425: FX workshop and the effects men killed
  - 432–700: lair finale again
  - 702–720: bedroom
  - 720–822: surgery
  - 828–955: funeral
  - 960–1040: claws in bed
  - 1044–1150: **Chase**. Truck at night 1047–1060; Chase driving 1048–1113 (dark); claws under the seat 1114.04–1120.51; Chase yawning and nodding off 1120.51–1126.26; claws again 1126–1135; claw through his chest at 1145 (extreme gore, do not use); truck off the road 1147–1150 (shots under 1 s)
  - 1151–1330: Heather at home, bedroom attack (short, dark cuts)
  - 1332–1500: hospital, freeway
- Chase scenes are very dark; the first few frames after 1120.51 are close to black.

**n7_chase_fan** (fan upload "Adam The Prowler", 105.1 s)
- 1920x1080 but visibly softer (upscaled).
- No watermark or channel bug seen in the frames I checked (75 s, 100 s, the 2 s sheet).
- Same Chase footage as bloodiest: yawning 74–78, claws under the seat 68–72, chest gore at about 98, truck 100.
- 104–105: Heather on the sofa; cuts at 104.06 and 104.52.
- Not needed; bloodiest has the same material sharper.

**Moments used by n7, each once:**
- coming: 186.6, 305.3
- coming_uk: 1.68, 36.45, 43.85, 51.78, 101.8, 111.03, 226.8
- stalks: 42.65
- hand: 5.8, 30.5, 91.2
- missme: 11.4, 81.66
- dylan: 6.2
- funeral: 12.8
- bloodiest: 1116, 1121
- julie: 11.8, 31.1, 76.55
- traffic: 82.5, 95.88
- end: 39.5

Do not also use: coming_uk 20–22 (same moment as coming 305), coming 157–162 (same hug as end 39.5), coming 284–290 (same stairs as coming_uk 1.68).

**Tile:** `('n7_julie', 36.60, 780, 430, 400)`
- Crop verified (`beats\n7\tile_b.jpg`).
- Bright, near-frontal Freddy face filling the frame, under the hat, teeth bared, eye visible, sharp.
- Alternative: `('n7_julie', 31.60, 720, 380, 400)` (`tile_a.jpg`).

**Problems:**

- "while he's driving": the crash itself is not usable (shots under 1 s, and the gore frame at 1145). The shot shows the claws coming through the seat instead.
- "to push him into": the shove itself is 1.62 s, below the 1.70 s needed. Used the furnace-engulf shot instead.
- Several Freddy shots are dark:
  - missme 81.66: dark blue
  - bloodiest Chase shots: very dark
  - stalks claw: dark blue
  - The rest are bright.
- coming_uk 36.45 ("and smarter") and 43.85 ("but if he picks") are different moments of the same window setup, 13 shots apart. If they look repetitive, swap one for n7_traffic 95.88 or n7_coming 250.42 (0.83 s only).
- Three s07 shots come from the Julie hospital scene (11.80, 31.10, 76.55), two of them with Freddy behind Julie. They are different moments, but there is a similar look at "babysitter" and at "the people you love".
- The frame-difference cut finder over-fires on dark and flickering-fire footage. I set every in-point and clean span from the strips, keeping a margin of about 0.05–0.1 s before the next cut.

### fj: Freddy vs. Jason (2003)

All clips are 1920x1080 SDR (bt709) except fj_intro. The RT/Movieclips clips are 2.35 letterboxed. The WB UK clips (notstrong, crash, influence, construction, cornfield) fill the frame or nearly so.

**fj_notstrong** (WB UK, 146.6 s, no bug in picture; WB logo card 132, "OWN NOW ON DIGITAL OR DISC" end card 134-146)
- 0-4 Blake's dad on porch; 8-57 Blake on porch / dad (cuts 17.81, 20.15, 21.52, 23.31, 26.90, 35.12, 44.75)
- 58.27-63.5 porch from the bushes; **63.6-~67.3 house exterior, porch lights (clean)**; 68-70 bushes; 70-73 Blake walks out; 78-80 goat; 84-92 Blake in the dark street (cuts 83.96, 85.21, 87.30, 89.88)
- 92.59-94.55 Freddy partial silhouette, glove at right
- **94.55-109.40 one continuous Freddy shot**: front-facing, glove flexing (95-102), leaning toward camera (104-109). Face drifts from x≈360 to x≈1000.
- 109.4-131.5 Blake reacts, Jason in the house, blood on the wall (128-131, gore)
**fj_decap** (RT Horror): the same Blake/Freddy scene as notstrong, but with the RT MOVIECLIPS mark bottom-left. Not used.

**fj_crash** (WB UK, 89.7 s): Trey's death. 0-12 Trey in bed; 12-15 Jason mask; 16-17 stab with blood spray (gore, avoid); **18.27-20.90 Jason raises the machete over Trey (lightning flashes change exposure; same camera shot)**; **20.90-23.02 Jason mask close, dark**; **23.05-50 Gibb in the shower and the aftermath: NUDITY RISK, do not use**; 56-73 rain, cops; 74-89 end card. fj_aftersex (RT) = the same scene with the RT mark.

**fj_world** (RT Horror, Movieclips mark bottom-left the whole clip; RT/Fandango end bumper 177+)
- 0-20 burning dock, Jason/Freddy fight; **21.3-~23.0 Freddy profile close**; 24-44 swings, splash, kids
- 44-50 Freddy with Jason's arm and glove (dark)
- **51.9-54.6 Freddy on the dock, fire-lit, face x≈1000-1100**
- 54.6-~56.2 machete in frame; **~56.2-58.8 Lori holding Jason's machete**; 58.9-60.4 Freddy; **60.45-62.2 Lori swings**; 62-66 Lori, Freddy's body; 66-72 water; 73-78 Freddy's head flying (blue)
- 82-110 Jason's body, Lori and Will; 112-122 burning lake; 122-128 black
- **143-149 Jason rising from the lake**; 149-165 Jason wades out with Freddy's head at his side; 165.5-170.4 Jason silhouette
- **170.43-173.0 Freddy's severed head, wink**; 173.1 black; 177 RT bumper

**fj_hell** (RT, mark): the dock fight before the ending. 0-90 Freddy/Jason/Will on the dock; 92-96 Lori with a torch; 100-140 Freddy is stabbed with his own arm; 140-178 propane explosion; 180+ RT bumper. No decapitation or wink in it.

**fj_kicks** (RT, mark): red boiler-room fight 0-160; 160-165 sprinkler; **166.46-~171.0 Freddy close-up (green), face x≈800-1050**; 171-189 Jason/Freddy two-shots and Jason close; **189.64-196.85 Freddy close-up grinning, face x≈1300-1500**; 197-202 two-shot; 202-204 Freddy with blade in mouth; 204+ RT bumper.
**fj_collide** (ClipZone): the same footage as kicks without the mark, offset by about +14 s. **210.9-216.3 two-shot, Jason left and Freddy right, through the water**; ClipZone end card 221.4+.
**fj_mom / fj_mommy** (WB): 0-7 Jason's mask with a tranquilizer dart, 8-47 red boiler room; Blu-ray "Own the complete collection" card at 48+. **No Pamela scene.**
**fj_dreaming / fj_childhood** (WB): identical clips: Lori/Will in the car (blue), then the Camp Crystal Lake flashback 40-73; Blu-ray card at 74+.

**fj_cornfield** (WB, no visible mark) = **fj_rave** (RT, mark; RT bumper 130+): cornfield party.
- 0-17 teens; 17.64-18.8 Jason mask close; 24-47 Jason stalks; **44.4-45.85 Jason mask close**; 47.4-48.3 Jason splashed with beer; 50-65 teen sets Jason on fire
- 66-110 burning cornfield, rave
- **112.49-114.49 burning Jason with the machete among ravers**; 114.5-115.2 fire; **115.25-117.24 burning Jason swings at the kids**; 117.24-119.2 Jason walks past the ravers; 119-128 more (cuts 120.33, 123.04, 124.29)

**fj_back** (ClipZone; ClipZone end card from 474.3; no bug during the film)
- **0-~5 Springwood street at night, Jeep headlights**; 6-34 Kia and Lori at the Jeep; 34-82 Will and Lori in the Jeep; 82-91 Will at the window
- 96-131 rain fight; 132-158 Lori in the hallway
- **159-165.37 Lori's father at the door (lightning flashes; clean from 163.8)**; 165-213 hallway, chase
- **214.2-216.26 house exterior at night**; 216-246 rain, kiss; 246-272 car, Will and Lori
- 272-290 Mark with a photo; 290-400 Mark's bathroom/bath dream (Bobby shirtless in a bloody bath, 354-384: not used; worms and gore 388-390); 396-416 Will and Lori arrive
- 410-418 Mark's arm wounds (gore)
- **419.6-439.36 Freddy behind Mark, glove at his throat** (cut between 419.5 and 419.6)
- 439-452 fire, Freddy in the room; 452-467 Lori and Will at the gate
- 467.6-~469.8 Mark's smoking back, wide; **~469.8-473.3 "FREDDY'S BACK" carved close**; 474.3+ ClipZone card

**fj_influence** (WB UK; WB logo 158, end card 160+) = **fj_pillar** (RT, mark): Freeburg and the caterpillar Freddy 0-47; **50.3-~58.3 observation room window**; 59-60.2 Freeburg; **60.2-~62.1 ward of sedated patients**; 62.2-63.5 Freeburg; 63.7-69 taped-eye patients (dark); 70.4 Freeburg; **~71.2-73.4 two taped-eye patients**; 74-84 Freeburg; 84-88 drug cabinet; **88.25-~95 Freeburg holding the Hypnocil bottles**; 96-157 Jason at Westin Hills, electrical sparks (flashes 120-141).

**fj_battle** (ClipZone, 654.8 s; ClipZone card 645+): a compilation from the cabin fire to the dock.
- 0-40 cabin; 45-75 Jason and Freddy dream fight; 110-160 burning cabin; 165-225 Kia and Will in the woods
- **230.44-~232.6 Freddy raising the glove, face x≈960**; 233-236 Kia; 236-238 Freddy profile
- **~239.5-248.5 Freddy in the foreground, Will and Lori behind**; 250-300 Freddy vs Kia (alternating shots)
- 305-330 Lori, Will, Kia; 335-490 construction-site fight; 490-580 dock fight; 585 Lori with a torch; 600-640 propane explosion

**fj_construction** (WB, full 16:9 frame): construction fight 0-196. 28 Freddy; 38-43 Freddy vs Jason; **86.67-87.9 bright front Freddy close-up (tile)**; 88-92 Jason mask close; 94-95 Freddy close.
**fj_apesh** (RT, mark): cabin fire 0-55, Kia and Will 57-117, Freddy 123-135, RT bumper 138+.

**fj_intro**: 720x1280 portrait phone recording of a TV. The room, towels and set-top box are visible, and the film image is small, blurry and skewed. The New Line titles are at the end (420-428) and the old-film montage runs about 46-190 (other films' Freddys). **Unusable.**

RT MOVIECLIPS mark (bottom-left, y≈885-970) is present on: fj_world, fj_kicks, fj_hell, fj_rave, fj_apesh, fj_pillar, fj_aftersex, fj_decap. In every line used from world/kicks, faces and action sit above y≈860. RT/Fandango bumpers sit at clip ends (world 177+, kicks 204+, hell 180+, rave 130+, apesh 138+). ClipZone cards sit at clip ends (back 474+, collide 221+, battle 645+). WB end cards: notstrong 132+, crash 74+, influence 158+; Blu-ray cards: mom/mommy 48+, dreaming/childhood 74+.

**Tile:** `('fj_construction', 87.10, 1040, 580, 900)`: front-facing 2003 Englund Freddy, eyes open and sharp, hat brim in frame, natural colour. Verified with the crop `crop=900:900:590:130,scale=400:400` (beats/fj/tile.jpg).

**Problems:**

- There is no Freddy-as-Pamela scene and no newspaper-clipping or file-erasing footage in any usable fj clip. #9 uses Jason rising from the lake, and #4 uses the Elm St house exterior (closest true moments). If the Pamela moment matters, a new clip is needed (the film's opening, Jason at Crystal Lake / "Mother").
- fj_intro, the only source for the opening monologue, is a phone video of a TV: unusable.
- s02 #1, #8 and s01 #5 are three different moments of one continuous 15 s Freddy shot (notstrong 94.55-109.40). This is allowed, but it looks similar. If it feels repetitive, #8 could move to construction 94.0 (Freddy laughing close, about 1.3 s, short).
- s02 #14 ("FREDDY'S BACK" carved into Mark's back) is burned-skin gore, but not the kill frame.
- s02 #17: the wink is at about 172.2-172.5 by the 0.25 s strip. The 170.43-173.0 head shot is only 2.6 s, so the span ends at 172.9, before black.

### r10: A Nightmare on Elm Street (2010)

**r10_m1** 1280x720 (Movieclips, "MOVIECLIPS.com" in the bottom letterbox, covered by the bar). 0–1.63 Quentin; 1.63–6.17 the preschool class drawing in the Pied Piper book; 6.17–8.68 Quentin; 8.68–12.05 Nancy reading, looks up ~11.4; 12.05–~16.3 book/Quentin; ~16.3–21.27 Nancy looking down; 21.27–40 alternating Nancy/Quentin singles (cuts 23.86 24.90 27.74 32.99 34.87 38.20); ~47 on: Movieclips end card.
**r10_m2** 1280x720 Movieclips. Dean's diner dream (Kellan Lutz) in the kitchen fire with Freddy's glove 0–40; Dean and Nancy in the diner 42–62 (cuts 45.00 50.01 53.34 54.93 56.22 58.89 60.98 62.81), then hand cut with the knife; ~63 on: end card.
**r10_m3** 1280x720 Movieclips. 0–4.42 Nancy at night by the store window; 4.42–6.92 Quentin close-up at the pharmacy; 6.92–8.05 pharmacist; 8.05–12.05 Quentin wide at the counter (walks off ~11.0); 12.05–15.22 Nancy startled in the bright store; 15.22–27.44 Nancy in the aisle, from behind, turns, light flicker on her face ~23.7–24.4; 27.44–35.45 empty aisle, darkens to the orange boiler corridor ~31.5; 35.45 Nancy in the boiler; 38.33–42.58 glove on the pipes; 42.58–44.00 Freddy silhouette scraping sparks; 45.88–49.59 sparks/Freddy face (each under 1.3 s); 53.85–64.11 rapid intercut store/boiler; 64.11–67.23 Freddy, fireball behind; 67.28–68.44 Nancy on the store floor (wide); 70.57–71.07 Freddy sparking in the store aisle; 71–75 flash intercut; 75.6 on: end card / Movieclips logo.
**r10_m4** 1280x720 Movieclips. Kris's bedroom: Kris and Jesse ("same dream") 0–96, no Nancy; ~97 on: end card.
**r10_unavoidable** 1920x1080 ClipZone. Full Dean diner opening. 0–6.7 Springwood Diner exterior; 6.7–41.5 Dean in the empty diner; 41.54–52.59 Dean standing, looking around (bright, clean); kitchen fire 86–99; ~101.2–105.81 Freddy's glove rising before the fire (silhouette); 123 on: Dean/Nancy/Kris/Quentin in the diner; 299.09–300.93 Nancy (waitress) close-up; 305.10–317.69 Dean close-up; 382–405 Freddy attack and the knife-to-throat (gore ~402, avoid); 405.0 on: ClipZone outro bumper. No logo inside the film part.
**r10_dreaming** 1920x1080 ClipZone. Kris: photo album 0–55; bed/attic 56–225 (dark); school 228; 242.87–244.66 and 248.62–255.42 Quentin (beanie) and Nancy at the locker; classroom 284–330; dream classroom: 332.75–334.79 Freddy silhouette; 344.18–345.72 Freddy at the chalkboard; 358.27–361.19 Kris; 361.19–363.53 Freddy standing (right of centre, x~1280); 364.91–367.83 Freddy raises the glove (x~1250); then Kris wakes in class, drive home, etc.; 531 on: ClipZone outro bumper.
**r10_boyfriend** 1920x1080 ClipZone, very dark teal. Nancy's dream bed: 0.9–4.88 Freddy face over Nancy (face x~760); 11.09–16.31 Freddy face close-up; 30.16–33.62 Freddy face; 46–50 Quentin with the adrenaline syringe; 61.64–62.81 overhead bed, Nancy and Freddy vanish; 62.81–~64.4 Nancy on the floor with Freddy (real world); 65.32–66.27 Freddy on the rug; 100–122 basement fight (glove cut off, ~120.75–122.16); 130.1–132.1 Freddy standing (front); 135.01 on: black blood from his throat; 174 the fire; 180.5 on: ClipZone outro bumper.
**r10_creepiest** 1920x1080 Warner Bros. UK compilation, no bug in the film part; 1445.5 on: black, then the WB shield and "Own now on digital or disc" end card. 0–118 Kris's classroom dream (Freddy 48–90); 120–176 Nancy bath scene: **wide shots ~156–170 show bare legs/body in the bath, avoid**; 186–300 Nancy's snow dream; 306–420 diner (Dean's death ~414, gore); 420–560 Kris's death (507 bed, 523.36 Jesse screaming, **524.0–~527.2 Kris thrown around the room**, 528.32–532.45 more flying, 535–547 blood on the bed, avoid); 563.94–574.66 Jesse in the jail corridor; 576–766 Jesse's boiler dream and death in the cell (728–740 gore; 741.32–747.16 cellmate at the cell-door window); 766–775 Quentin shirtless at the industrial site (no nudity); 858–869 red-lit flashback; 892–930 burning of Freddy; 936 gym-class boys, shirtless; 1020–1100 child-bedroom flashback with Freddy (1026.73–1031.70 Freddy at the window, face x~640); 1160–1290 **real-world finale**: 1168.0–1169.17 overhead empty bed, 1169.17–~1170.85 Nancy on the floor under Freddy, 1171.67–1172.63 Freddy on the rug, 1227.1–1228.5 the severed glove, 1241.37–1251.00 black blood from Freddy's throat, 1278–1282 fire; 1290–1344 Nancy asleep, Quentin; 1344–1428 boiler-room dream fight (1366.24–1368.41 Freddy face; 1372.00–1374.71 Freddy profile in the fire; 1412.33–1414.08 Freddy face, frontal; 1419.00–~1421.88 Freddy face); 1429–1445 Nancy hiding in the closet at home (no mirror, no mother).
**r10_preview** 1920x1080 (WB): **the 1984 original's opening credits, not the 2010 film.** Unusable for r10 (it might fit the n1 agent).
**r10_dean_fan / r10_kris_fan** 1280x544: not used (per instructions). **r10_bath / r10_bath_uk**: not used.
No HDR (all bt709). Under-720p sources: none used (m1–m4 are 720p).

**Tile:** `('r10_creepiest', 1412.90, 1100, 520, 1040)`. Frontal, fire-lit Freddy face filling the square, left eye visible, sharp. Checked with the ffmpeg crop to 400x400 (beats/r10/tile.jpg).

**Problems:**

- The mirror attack on Nancy's mother (`he comes back through`) is not in any r10 clip. A Freddy close-up stands in. Fetch the ending ("Freddy kills Nancy's mom" / "mirror ending") if this beat must be literal.
- r10_preview is mislabelled: it is the 1984 opening.
- The NEW CUT `him into the real world` has 0.88 s of clean picture against ~1.0 s needed (renders at about 0.88x). No longer real-world Freddy shot exists in the clips.
- The boyfriend and creepiest finale shots are dark (teal/green). The brighter Freddy faces are in the boiler-room dream (creepiest 1366–1421) and the dreaming classroom.
- The "throat cut" frame is the aftermath (black blood starting), not the slash itself.

