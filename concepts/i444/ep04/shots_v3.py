# EP04 Freddy v3 shot list, read by build_edl_v3.py. A shot is (phrase, clip, in_s, -clean_s[, opts]).
# GENERATED SKELETON from shot_plan_v3.md (cloud, 11/7). On the laptop, replace every TODO pair with the verified in-point and the
# negative clean span (seconds of clean picture from the in-point, no title card, logo or scene cut inside), as in EP07 shots_v8.py.
# Change the clip to another candidate when the first one does not hold the moment, and keep the comment true (what is on screen).
# Extra cuts may be added on other exact script phrases. L = subject left of the stat card.
TODO = None
# ---- s00 cold open (14.8 s) ----
X.append(sec('s00', [
  (0, 'n4_beach', 36.60, -2.25),  # FRAME 0: huge bright daylight Freddy close-up, hat + burned face, grinning, holding sunglasses (no sunglasses on yet)
  ('drag you across', 'n1_tina_kill', 163.05, -1.20),  # Tina hauled up the bedroom wall by the window, invisible force
  ('the ceiling', 'n1_tina_kill', 185.90, -1.00),  # close: bloody Tina pinned on the ceiling, Rod's lamp behind
  ('turn you into', 'n3_marionette', 44.38, -0.65),  # the Freddy puppet's claw has slit Phillip's wrist, veins pulling out (before the long bloody-arm shot)
  ('a puppet', 'n3_marionette', 92.40, -2.40),  # Phillip walking the hall like a marionette on his vein strings
  ('smash your head', 'n3_primetime', 34.62, -0.90),  # the TV's arms wrap around Jennifer and grab her
  ('through a tv', 'n3_primetime', 50.70, -1.15),  # TV-Freddy drives her head into the screen, sparks on impact
  ('crush you', 'n4_roach', 35.30, -1.50),  # Freddy (hat, lamp behind) forcing the barbell down onto Debbie
  ('like a bug', 'n4_roach', 166.45, -2.20),  # close-up of the giant cockroach Debbie became (antennae, shiny head)
  ('or pull you down', 'n1_glen_bed', 123.55, -2.00),  # close: Glen flailing as the bed pulls him under, pillow flying
  ('into your own bed', 'n1_glen', 134.20, -2.00),  # his legs vanish into the mattress, bed closes (geyser is 10 s later, not shown)
  ('and all he needs', 'n1_tina_chase', 29.70, -1.45),  # Freddy grinning, glove raised beside his face, blue sky
  ('is for you', 'n1_bathroom', 0.10, -3.00),  # Nancy in the bath, eyes shut, dozing off
  ('to fall asleep', 'n1_bathroom', 36.00, -1.10),  # the glove's blades rise out of the bubbles between her knees
  ("we're ranking", 'still_posterwall', 0.0, -5.0),  # the 9 posters pop in (release order) and hold to the end
  ], extra=[('word', w, a, b) for w, a, b in [
    ('He will', 0, 'drag you across'),
    ('Drag you across', 'drag you across', 'the ceiling'),
    ('The ceiling', 'the ceiling', 'turn you into'),
    ('Turn you into', 'turn you into', 'a puppet'),
    ('A puppet', 'a puppet', 'smash your head'),
    ('Smash your head', 'smash your head', 'through a tv'),
    ('Through a TV', 'through a tv', 'crush you'),
    ('Crush you', 'crush you', at('s00', 'like a bug') - 0.04),   # "you" (5.91 s) runs into the 0.08 s lead of "like", so this switch
    ('Like a bug', at('s00', 'like a bug') - 0.04, 'or pull you down'),   # sits 0.04 s before "like" instead (caption_coverage)
    ('Or pull you down', 'or pull you down', 'into your own bed'),
    ('Into your own bed', 'into your own bed', 'and all he needs'),
    ('And all he needs', 'and all he needs', 'is for you'),
    ('Is for you', 'is for you', 'to fall asleep'),
    ('To fall asleep', 'to fall asleep', "we're ranking"),
    ("We're ranking", "we're ranking", 'every freddy'),
    ('Every Freddy', 'every freddy', 'by your chance'),
    ('By your chance', 'by your chance', 'of surviving'),
    ('Of surviving him', 'of surviving', 999),
  ]], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out (one word 0.9 s, a phrase 1.6 s max); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.6))
# ---- s01 rules (26.5 s) ----
s01_end = vdur('s01') + 0.05
X.append(sec('s01', [
  (0, 'n1_screw_sleep', 33.20, -3.50, 'z=1.35,dx=40'),  # Nancy gulping coffee to stay awake, mother watching
  ('you fall asleep', 'n3_real', 11.00, -3.00, L),  # Kristen dozing off in her hospital bed, eyes closed
  ("and that movie's freddy", 'n1_boiler', 272.90, -2.10, L),  # Freddy's hat in silhouette in the boiler room
  ('is waiting for you', 'n1_boiler', 270.70, -1.90, L),  # the glove dragging along the boiler-room pipe
  ('and every freddy is different', 'r10_creepiest', 1419.05, -2.80, L),  # Freddy face close-up, fire-lit boiler room, face x~960
  ('one is so weak', 'fj_notstrong', 95.10, -1.40, 'z=1.35,dx=150'),  # Freddy in the moonlit street, glove up (face x≈560-760)
  ('he needs jason', 'fj_crash', 18.35, -2.45, 'z=1.35,dx=-160'),  # Jason raises the machete over Trey in bed (lightning flicker, same camera shot; Jason x≈250-480)
  ('one needs a teenager\'s body', 'n2_emerge', 147.20, -1.90, 'z=1.35,dx=40'),  # Freddy's head rises out of Jesse's chest (need 1.87)
  ('and one is strong enough', 'n4_soulfood', 68.70, -3.10, L),  # Dream Master Freddy close-up in the diner, hat, claw holding the soul meatball
  ('to wipe out kids', 'n4_junkyard', 147.00, -6.50, L),  # Freddy grinning, claw on Dream Warrior Kincaid's chest (junkyard, fire behind)
  ('so we score', 'n1_opening', 38.70, -3.40, 'z=1.8,dy=-123'),  # the glove being forged, blade in the vise (window-boxed credits footage, zoomed to fill)
  ('intelligence', 'n3_heres', 196.00, -1.50, L),  # the faucet handles turn into Freddy's claws
  ('kill count', 'n5_force_feed', 25.20, -2.8, L),  # Freddy gripping Greta's face at the table (Freddy x~640, Greta x~1440)
  ('and dream power', 'n3_worm', 109.10, -1.50, L),  # the giant worm with Freddy's face
  ('is how dangerous', 'n3_worm', 112.30, -1.40, L),  # NEW CUT  worm-Freddy face, second angle
  ('once your eyes close', 'n1_bathroom', 51.55, -3.80, L),  # Nancy asleep in the tub, eyes closed, mouth open
  ('put it all together', 'n6_forever', 67.20, -8.61, L),  # Freddy close-up, front, grinning (Doc's room); subject x~760
  ('your survival rate', 'n7_coming', 186.60, -1.95, L),  # New Nightmare Freddy close-up, burned face snarling, lair firelight (centre x~800)
  ]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'FREDDY KRUEGER', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'DREAM POWER': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'dream power')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# ---- s02 #9 Freddy vs. Jason 95% (36.6 s, card from "if you've never heard") ----
X.append(sec('s02', [
  (0, 'fj_kicks', 189.80, -3.20),  # FvJ Freddy close-up grinning, green boiler room (face right of centre)
  ('this freddy is the weakest', 'fj_notstrong', 98.10, -2.60),  # Freddy alone in the street, flexing the glove ("not strong enough yet")
  ('because his town forgot', 'fj_notstrong', 63.70, -3.00),  # quiet Springwood house at night, porch lights on
  ('the adults erased', 'fj_back', 163.80, -1.50),  # Lori's father at the front door (the adult who covers it up)
  ('every trace of him', 'fj_back', 214.40, -1.75),  # dark exterior of the old Elm St house (Lori's house)
  ('and anyone who still dreams', 'fj_influence', 60.25, -1.85),  # Westin Hills ward, rows of sedated patients
  ('about him', 'fj_influence', 71.40, -1.80),  # NEW CUT  Westin Hills patients with taped eyes
  ('gets locked away', 'fj_influence', 51.00, -3.00),  # Westin Hills observation room window onto the ward
  ('and kept on a drug', 'fj_influence', 88.40, -3.00),  # Freeburg holding the Hypnocil bottles
  ("he's so weak", 'fj_notstrong', 104.60, -2.00),  # Freddy leaning in, claws raised, can't kill yet
  ('bring jason back', 'fj_world', 144.40, -2.50),  # Jason rises out of Crystal Lake (Pamela scene not in clips)
  ('to scare people', 'fj_crash', 21.10, -1.80),  # Jason's mask looming over Trey on Elm St (ends before the shower shot)
  ('in a movie with his own name', 'fj_battle', 241.00, -3.00),  # Freddy in the foreground stalking Will and Lori
  ('jason does nearly all', 'fj_cornfield', 112.55, -1.90),  # burning Jason wading into the rave kids
  ('the killing', 'fj_cornfield', 115.45, -1.75),  # NEW CUT  burning Jason swings the machete at the ravers
  ('and freddy kills exactly', 'fj_back', 419.70, -2.00),  # Freddy appears behind Mark, glove at his throat
  ('one person himself', 'fj_back', 470.00, -2.40),  # "FREDDY'S BACK" burned into Mark's back (close, after the kill)
  ('in the end lori', 'fj_world', 56.80, -1.75),  # Lori holding Jason's machete on the burning dock
  ('cuts his head off', 'fj_world', 60.55, -1.50),  # Lori swings the machete (cut on the swing)
  ("with jason's machete", 'fj_world', 171.20, -1.70),  # Freddy's severed head in Jason's hand, the wink (ends before black at 173.1)
  ("if you've never heard", 'fj_battle', 230.60, -1.90, L),  # Freddy raising the glove in the blue fog (face x≈960)
  ("he can't even find", 'fj_world', 52.10, -2.35, L),  # Freddy on the dock, fire-lit (face x≈1000-1100)
  ('survival rate', 'fj_kicks', 166.60, -3.60, L),  # Freddy close-up, green light (face x≈800-1050)
  ]))
# ---- s03 #8 Freddy's Revenge 65% (42.9 s, card from "stay far away") ----
X.append(sec('s03', [
  (0, 'n2_brain', 276.50, -10.50),  # Freddy leans in, claw at Jesse's lips in the hallway ("you've got the body")
  ('this freddy is far more', 'n2_pool', 71.30, -7.45),  # Freddy silhouette in the fog by the pool, a kid raises his hand
  ('because he doesn\'t need', 'n2_creepiest', 1053.45, -3.50),  # frontal Freddy close-up, glove by his face (boiler room)
  ('he takes over a teenager', 'n2_kill4k', 7.00, -2.60),  # Jesse wakes in bed, sweating, shirtless (cut at ~9.8)
  ('named jesse', 'n2_kill4k', 141.45, -2.75),  # Jesse in the bright kitchen
  ('climbs right out', 'n2_emerge', 139.64, -1.65),  # wide: Freddy's torso bursting out of Jesse's chest (need 1.63)
  ('and kills more people', 'n2_pool', 21.90, -2.65),  # the pool boils, kids scramble out in panic
  ('than any other freddy', 'n2_party', 553.40, -3.20),  # Freddy walks through the crowd of kids at the party
  ('he kills jesse\'s gym teacher', 'n2_creepiest', 79.50, -3.00),  # Coach Schneider tied to the floor by jump ropes (tank top on, wide)
  ('in the showers', 'n2_creepiest', 96.60, -2.00),  # coach's upside-down screaming face on the shower tiles (face only)
  ('then his friend grady', 'n2_emerge', 180.90, -2.25),  # Grady in his bedroom with Freddy beside him in the doorway
  ('then a whole group', 'n2_pool', 55.60, -3.95),  # Freddy slashes a fleeing kid at the pool party
  ('and in the very last scene', 'n2_bus', 9.00, -16.40),  # final bus scene: Jesse, Kerry and Lisa laughing
  ('his claws burst out', 'n2_bus', 84.30, -1.87),  # Kerry on the bus, then the claws burst out of her chest (from ~85.2)
  ('on the school bus', 'n2_bus', 46.22, -1.55),  # yellow school bus drives toward the camera
  ('but he\'s also the dumbest', 'n2_party', 522.50, -4.20),  # Freddy poses, arms spread, fire bursting behind him
  ('he barely uses', 'n2_pool', 117.90, -4.00),  # Freddy stands in the real-world party beside the flame column
  ('and he can be beaten', 'n2_creepiest', 1020.00, -5.50),  # Lisa face to face with Freddy, claw raised
  ('lisa tells jesse', 'n2_creepiest', 1009.00, -8.00),  # Lisa close-up, talking to Jesse/Freddy
  ('kisses freddy', 'n2_creepiest', 1038.20, -4.40),  # Lisa kisses Freddy
  ('and he burns to ash', 'n2_creepiest', 1094.70, -3.10),  # Freddy's melting face screaming in flames
  ('stay far away', 'n2_kill4k', 308.00, -3.00, L),  # Jesse close-up at the power plant (x≈870), Lisa behind
  ('and you\'ll probably be fine', 'n2_kill4k', 349.20, -2.90, L),  # Jesse + Lisa two-shot, bright (Jesse x≈480, Lisa x≈1380)
  ('survival rate', 'n2_pool', 327.50, -4.50, 'z=1.35,dx=160'),  # big Freddy close-up, face centre x≈720
  ]))
# ---- s04 #7 The Dream Child 55% (39.9 s, card from "he only gets three") ----
X.append(sec('s04', [
  (0, 'n5_tricks', 50.30, -2.6),  # Dream Child Freddy close-up, face turning to camera, bright (rank card)
  ('this freddy kills fewer', 'n5_back_to_hell', 40.45, -2.9),  # Freddy close-up, lit, crane pulls back
  ("but he's far smarter", 'n5_itsaboy', 50.55, -1.65),  # Freddy close-up grinning under the hat
  ('and much stronger', 'n5_pool', 103.60, -2.4),  # Freddy's head rises out of the dream pool, spitting water
  ('he finds a sneaky', 'n5_back_to_hell', 155.00, -4.2),  # Alice with both hands on her belly (the unborn baby)
  ('through the dreams', 'n5_son4k', 46.10, -2.05),  # Jacob with Freddy leaning in beside him
  ('unborn son', 'n5_son4k', 23.00, -2.6),  # NEW CUT  Jacob, Freddy's glove blades at his throat
  ('so he can come', 'n5_drunk', 50.25, -3.0),  # Freddy at the wheel of the truck with a bottle
  ("even while she's wide", 'n5_son4k', 34.85, -4.5),  # Alice close-up, scared
  ('he turns dan', 'n5_motorcycle', 0.80, -2.5),  # Dan getting on his motorcycle
  ('into part of his own', 'n5_motorcycle', 70.40, -2.8),  # Dan's body fused into the bike (flesh/cables)
  ('force-feeds greta', 'n5_force_feed', 6.45, -1.85),  # Freddy as waiter spooning food into Greta at the table
  ('until she chokes', 'n5_force_feed', 22.60, -5.5),  # Greta in profile, cheeks stuffed, choking (reaction)
  ('and turns mark', 'n5_superfreddy', 28.10, -1.8),  # Mark half turned to comic paper, Freddy behind
  ('into a paper drawing', 'n5_superfreddy', 32.30, -3.6),  # Mark's body turning into a paper drawing (tilt down)
  ('before slicing him', 'n5_superfreddy', 45.80, -1.12),  # Freddy's glove slashing paper Mark
  ('pieces', 'n5_superfreddy', 48.15, -1.12),  # NEW CUT  paper Mark screaming, torn into strips
  ('but alice has beaten', 'n5_son4k', 30.60, -2.6),  # Alice standing in the boiler/tower set
  ('and in the end', 'n5_back_to_hell', 138.20, -2.85),  # Amanda Krueger (the nun) close-up
  ('jacob uses the power', 'n5_back_to_hell', 29.10, -1.8),  # Jacob's face, turning on Freddy
  ('freddy gave him', 'n5_back_to_hell', 74.10, -1.8),  # NEW CUT  the souls tearing out of Freddy
  ('to destroy him', 'n5_back_to_hell', 79.30, -2.4),  # Freddy stretched apart by the souls
  ('he only gets three', 'n5_itsaboy', 60.65, -2.35, L),  # Freddy under the hat, glove up, fog behind (x~800)
  ('so if he comes', 'n5_tricks', 22.30, -3.5, L),  # Freddy turned to camera in the corridor (x~840)
  ('survival rate', 'n5_baby', 127.00, -3.1, L),  # Freddy arms spread before the church window (x~880)
  ]))
# ---- s05 #6 Freddy's Dead 45% (45.3 s, card from "he's deadly but") ----
X.append(sec('s05', [
  (0, 'n6_forever', 85.20, -7.04),  # big Freddy close-up, finger raised, talking (rank card)
  ("unlike the last one", 'n6_father', 111.60, -5.88),  # Freddy in Tracy's kitchen, glove up, sneering
  ('has the biggest body count', 'n6_doom', 32.40, -7.95),  # "Welcome to SPRINGWOOD" sign at night (camera drifts off it after ~35.0)
  ('before the movie even starts', 'n6_town', 36.80, -2.96),  # empty rainy night street, lit shop window, a car passes
  ('almost every child', 'n6_town', 61.85, -2.75),  # newspaper box "NINE, TEN, NEVER SLEEP AGAIN" (slow push-in)
  ("but he's also the silliest", 'n6_oz', 37.60, -7.37),  # Freddy flying past the window on a witch's broomstick (Wizard of Oz gag)
  ('and he plays with his victims', 'n6_playground', 49.65, -2.53),  # Freddy dangling beside John in the sky, slicing his parachute cords
  ("he turns up carlos's", 'n6_nice', 22.55, -4.04),  # Carlos smiling, fiddling with the hearing aid in his ear
  ('until one scratch', 'n6_chalk', 13.75, -3.10),  # Freddy's claws poised on the blue chalkboard
  ('kills him', 'n6_nice', 159.70, -2.47),  # Carlos screaming, clutching his head (cut well before the explosion)
  ('traps spencer inside', 'n6_game', 6.45, -3.85),  # Spencer as a live sprite inside the factory video-game level
  ('a video game', 'n6_game', 107.70, -4.36),  # Freddy grinning with the Power Glove on his claw hand
  ('and drops john doe', 'n6_doom', 120.80, -1.42),  # Freddy's claw slicing the parachute cord against the sky
  ('john doe', 'n6_doom', 132.03, -0.80),  # NEW CUT  John screaming as he falls through the clouds
  ('the last teenager', 'n6_busrt', 57.75, -2.18),  # John Doe lying on the empty road outside Springwood, daylight
  ('onto a bed of spikes', 'n6_doom', 135.95, -5.27),  # Freddy rolling the bed of spikes into place on the dark road (no impact)
  ('all those jokes', 'n6_forever', 99.35, -5.15),  # big Freddy face laughing, finger up
  ('tracy gets woken', 'n6_father', 136.05, -4.70),  # dream Freddy snarling right over Tracy (she is behind him)
  ('before he can finish', 'n6_father', 159.05, -3.71),  # Tracy jolts awake in bed, Maggie rushes in
  ('in the end his own daughter', 'n6_blood', 28.75, -5.08),  # Maggie in her childhood dress in Freddy's dream house
  ('drags him into the real', 'n6_maggie', 0.05, -2.37),  # real-world basement: Freddy grabs Maggie (wide)
  ('and shoves a pipe bomb', 'n6_maggie', 204.55, -3.25),  # Maggie jamming the pipe bomb into Freddy's chest, Freddy screaming
  ("he's deadly but", 'n6_brain', 43.60, -3.66, L),  # Freddy's face bursts screaming from the demon wall, push in to his eyes; centred
  ('and that time is', 'n6_maggie', 229.85, -2.97, L),  # Freddy's screaming head in the explosion, then debris; centred x~960
  ('survival rate', 'n6_forever', 105.75, -10.85, L),  # Freddy medium shot under the ceiling slats, flexing his claws; x~860
  ]))
# ---- s06 #5 the 2010 remake 38% (39.3 s, card from "staying awake won't") ----
X.append(sec('s06', [
  (0, 'r10_dreaming', 364.98, -2.80),  # rank card: Freddy raises the glove in the dream classroom
  ("this freddy is the opposite", 'r10_unavoidable', 101.45, -4.30),  # dark: Freddy's gloved hand rises in front of the diner kitchen fire
  ("he's dark mean", 'r10_boyfriend', 11.20, -5.05),  # Freddy's burned face close-up over Nancy (dark teal)
  ('and serious', 'r10_dreaming', 361.22, -2.28),  # Freddy standing in the classroom dream, stone-faced
  ('and he has a trick', 'r10_m3', 4.50, -2.38),  # Quentin at the pharmacy counter, close-up
  ('that makes staying awake', 'r10_m1', 16.50, -4.70),  # Nancy looking down, heavy-eyed, at the library table
  ('go too long without', 'r10_m3', 8.10, -3.90),  # Quentin slumped at the counter asking the pharmacist for pills
  ('and your brain drops', 'r10_m3', 30.60, -4.80),  # the store aisle goes dark and turns into the orange boiler corridor
  ('for a few seconds', 'r10_m3', 64.15, -3.05),  # Freddy in the store-turned-boiler, fireball behind him
  ('without you even noticing', 'r10_m3', 12.12, -3.05),  # Nancy in the bright store, startled, looking around
  ('by the time nancy figures', 'r10_m1', 8.75, -3.25),  # Nancy reading, then looking up
  ('every other kid', 'r10_m1', 1.70, -4.40),  # the preschool class drawing in the Pied Piper book
  ('except her and quentin', 'r10_dreaming', 248.70, -6.65),  # Quentin (beanie) and Nancy at her school locker
  ('he gets dean', 'r10_unavoidable', 43.00, -9.50),  # Dean alone in the night diner, looking around
  ('kris in her bedroom', 'r10_creepiest', 524.10, -1.60),  # Kris flung through the air across her bedroom
  ('and jesse in a jail cell', 'r10_creepiest', 564.00, -10.60),  # Jesse in his orange jumpsuit in the jail cell corridor
  ('and even after nancy drags', 'r10_creepiest', 1169.20, -1.60),  # Nancy awake on the floor, Freddy on top of her, gripping her
  ('him into the real world', 'r10_creepiest', 1171.72, -0.88),  # NEW CUT  Freddy lying on the rug in the real world
  ('and cuts his throat', 'r10_creepiest', 1241.40, -9.50),  # Freddy, black blood just starting from his cut throat (cut on the flow, not the worst)
  ('he comes back through', 'r10_creepiest', 1372.05, -2.60),  # STAND-IN (mirror ending missing): Freddy close-up, boiler fire
  ("staying awake won't", 'r10_creepiest', 1028.60, -3.00, L),  # Freddy at a child's bedroom window, face x~640
  ('survival rate', 'r10_boyfriend', 1.45, -3.40, L),  # Freddy's face close over Nancy, face x~760
  ]))
# ---- s07 #4 New Nightmare 30% (38.9 s, card from "he only gets four") ----
X.append(sec('s07', [
  (0, 'n7_coming', 305.30, -2.60),  # Freddy rises out of the lair smoke and leans in to camera (rank card)
  ('this freddy is stronger', 'n7_coming_uk', 101.80, -1.58),  # bright Freddy face peering round the doorway, striped arm reaching
  ('and smarter', 'n7_coming_uk', 36.45, -3.10),  # NEW CUT  Freddy's head slides through the window toward Dylan
  ("and he doesn't just hunt", 'n7_stalks', 42.65, -2.60),  # the claw hovers over Heather's sleeping face (dark blue)
  ('he hunts a whole family', 'n7_hand', 5.80, -3.35),  # Chase lifts Dylan next to Heather at the FX workshop, all three in frame
  ('he goes after heather', 'n7_missme', 11.40, -2.50),  # Heather close-up, looking up in fear as the quake hits
  ('the actress who played', 'n7_dylan', 6.20, -8.00),  # Heather Langenkamp close-up on the phone, bright
  ('and picks off the people', 'n7_funeral', 12.80, -6.20),  # the funeral: Heather, Dylan and Julie in the mourners, dolly out
  ('he kills two special', 'n7_hand', 91.20, -2.00),  # the new glove slashes the effects man on the workshop floor (cut before the worst)
  ('working on a new', 'n7_hand', 30.50, -2.95),  # on set: effects man with his FX mug behind the animatronic glove rig
  ('then her husband', 'n7_bloodiest', 1121.00, -5.15),  # Chase driving at night, yawning, nodding off (dark)
  ("while he's driving", 'n7_bloodiest', 1116.00, -4.45),  # the claws rise through the truck seat beside his leg
  ("then her son's babysitter", 'n7_julie', 11.80, -3.15),  # Julie in the hospital, Freddy appears behind her
  ('dragging her up the wall', 'n7_julie', 76.55, -2.85),  # Freddy walks up the wall and ceiling dragging Julie (camera rolled)
  ('then he takes her little', 'n7_traffic', 82.50, -3.10),  # Dylan sleepwalks across the freeway as cars pass
  ('right into his world', 'n7_coming_uk', 1.68, -3.15),  # Dylan climbs the stairs of Freddy's lair temple
  ('it takes heather and dylan', 'n7_end', 39.50, -4.10),  # Heather and Dylan hug in the lair
  ('to push him into', 'n7_coming_uk', 226.80, -4.20),  # Freddy's face as the furnace flames engulf him
  ('he only gets four', 'n7_missme', 81.66, -1.55, L),  # Freddy's face rises out of the dark (blue night light; centre x~710)
  ('but if he picks', 'n7_coming_uk', 43.85, -1.88, L),  # Freddy reaches his claw out of the window toward Dylan (Freddy x~720, claw x~1080)
  ('the people you love', 'n7_julie', 31.10, -3.35, L),  # NEW CUT  Freddy flexes the glove behind Julie (Freddy face x~720)
  ('survival rate', 'n7_coming_uk', 111.03, -2.28, L),  # Freddy screaming close-up, firelit (face x~800)
  ]))
# ---- s08 #3 the 1984 original 22% (42.2 s, card from "unless you're as") ----
X.append(sec('s08', [
  (0, 'n1_tina_chase', 57.10, -4.30),  # rank card: Freddy's lit face, hand raised in the alley ("This is God")
  ('from nineteen eighty-four', 'n1_opening', 49.10, -2.40, 'z=1.8,dy=-123'),  # the finished glove on Freddy's hand (credits footage, zoomed to fill)
  ("this freddy isn't as strong", 'n1_tina_chase', 16.15, -1.85),  # Freddy's silhouette in the alley, impossibly long arms
  ('the last one', 'n1_tina_chase', 18.45, -1.70),  # NEW CUT: Freddy's hat silhouette, face half lit
  ("but he's the scariest", 'n1_boiler', 232.25, -3.35),  # Freddy standing in the boiler room's shadows, raising the glove
  ('he barely talks', 'n1_boiler', 288.55, -1.80),  # extreme close-up of Freddy's face, silent
  ('he stays in the shadows', 'n1_tina_chase', 12.20, -1.80),  # Freddy in silhouette, face barely lit under the hat
  ('and nobody believes you', 'n1_screw_sleep', 81.00, -2.40),  # Nancy beside her doubting mother in the kitchen
  ("until it's too late", 'n1_dark_story', 11.90, -2.40),  # Nancy alone on the dusk street, looking around
  ('he drags tina', 'n1_tina_kill', 166.20, -1.65),  # Tina slid up the wall by the window, upside down
  ('across the ceiling', 'n1_tina_kill', 179.50, -4.30),  # wide: Tina dragged across the ceiling, Rod reaching up
  ('strangles rod', 'n1_rod', 160.45, -1.95),  # Rod screaming, the bedsheet tight at his throat
  ('in a jail cell', 'n1_rod', 86.00, -5.00),  # the cell: bars behind, the sheet snaking up off the bunk
  ('and pulls glen down', 'n1_glen', 126.65, -2.35),  # wide: Glen asleep in bed with headphones and the TV
  ('nancy only survives', 'n1_plan', 95.00, -2.70),  # Nancy close-up in bed, thinking
  ('to learn his rules', 'n1_plan', 128.00, -2.00),  # Nancy explaining to Glen, working it out
  ('she sets traps', 'n1_traps', 166.65, -3.30),  # Nancy rigging the lightbulb/glass-ball trap
  ('drags him into the real', 'n1_fight', 28.95, -1.35),  # Nancy grappling Freddy in the bushes as the alarm goes
  ('real world', 'n1_fight', 30.45, -1.70),  # NEW CUT: Nancy thrashes awake in her bed, pulling him out
  ('and finally turns her back', 'n1_no_fear', 219.08, -1.85),  # Nancy in front of Freddy, turning away from him
  ('on him', 'n1_no_fear', 221.00, -1.20),  # NEW CUT: her back to him, she reaches for the doorknob
  ('taking away the fear', 'n1_no_fear', 222.95, -5.70),  # wide: Freddy lunges at her back and dissolves into blue sparks
  ('and even then', 'n1_ending', 10.30, -3.40),  # Marge on the sunny porch, close
  ('he still takes her mother', 'n1_ending', 87.10, -1.50),  # the door glass bursts, Freddy's arm grabs Marge
  ('her mother', 'n1_ending', 88.72, -1.25),  # NEW CUT: wide, Marge yanked through the door window
  ("unless you're as", 'n1_screw_sleep', 74.00, -5.20, L),  # Nancy close-up, determined (bright)
  ('he gets you', 'n1_god', 78.20, -2.60, L),  # close: Freddy's lit, burned face under the hat brim
  ('survival rate', 'n1_wall', 305.40, -3.30, L),  # Freddy behind the gate bars in Nancy's dream
  ]))
# ---- s09 #2 Dream Warriors 12% (40.3 s, card from "you don't have") ----
X.append(sec('s09', [
  (0, 'n3_joey', 1.70, -3.60),  # bright Freddy in his sweater in Joey's room (rank card)
  ('this freddy is deadlier', 'n3_souls', 100.30, -2.80),  # Freddy close-up in the boiler room
  ('because kids who learn', 'n3_best4k', 504.95, -1.90),  # the Dream Warriors walking together in the dream house
  ("still can't stop", 'n3_souls', 141.55, -1.75),  # Freddy medium shot, warm light
  ('he hunts the last children', 'n3_best4k', 153.00, -2.30),  # Westin Hills kids crowded at the wire-mesh window
  ('in a mental hospital', 'n3_best4k', 140.45, -1.80),  # wide shot of the Westin Hills nurses' station
  ('he turns phillip', 'n3_marionette_uk', 66.20, -1.90),  # Phillip with the vein strings rising from his arms
  ('using his own veins', 'n3_marionette_uk', 172.20, -2.00),  # Freddy on top of the tower working the vein strings (dark)
  ("smashes jennifer's head", 'n3_primetime_wb', 37.60, -2.60),  # aftermath: Jennifer hanging with her head inside the TV
  ('and kills taryn', 'n3_taryn', 86.40, -2.60),  # Freddy raises his syringe fingers
  ('and will', 'n3_joey', 120.20, -1.00),  # Will in his wheelchair behind the doctor (group room)
  ('even after they find', 'n3_wizard', 34.05, -2.40),  # Will as the Wizard Master, green magic charging in his hands
  ('then his skeleton kills', 'n3_skeleton', 78.55, -2.00),  # the skeleton attacks Donald, Donald reels back
  ("nancy's father", 'n3_skeleton', 81.05, -1.00),  # NEW CUT  wide junkyard: skeleton on Donald
  ('in the real world', 'n3_skeleton', 35.95, -1.60),  # Donald walking through the junkyard at night
  ('and freddy kills nancy', 'n3_nancy', 43.95, -1.35),  # Freddy's true face appears as he stabs Nancy
  ('herself', 'n3_nancy', 47.05, -0.80),  # NEW CUT  Freddy at Nancy's throat, she screams (cut before the blood close-up)
  ('while pretending to be', 'n3_nancy', 8.50, -2.40),  # "Dad" smiling: Freddy disguised as her father
  ('so even the girl', 'n3_nancy', 122.40, -3.60),  # Kristen cradling the dying Nancy
  ('the kids who survived', 'n3_creepiest', 1024.60, -2.80),  # Joey and Kincaid embrace, then Kristen (and Nancy) join them in the mirror hall
  ('and it still took', 'n3_nancy', 96.10, -2.20),  # Neil in the grave with the holy-water bottle over the bones
  ('on his bones', 'n3_nancy', 106.85, -2.30),  # Freddy bursting with light beams as his bones are consecrated
  ("you don't have", 'n3_souls', 125.70, -2.20, L),  # Freddy close-up grinning, boiler room
  ('survival rate', 'n3_taryn', 110.60, -2.60, L),  # low-angle Freddy face under the lights
  ]))
# ---- s10 #1 The Dream Master 5% (38.1 s, card from "if the kids") ----
X.append(sec('s10', [
  (0, 'n4_junkyard', 36.40, -3.80),  # Freddy reborn: hat-and-shoulders silhouette rising against the blue smoky sky
  ('this freddy is the strongest', 'n4_reborn', 236.40, -2.60),  # Freddy holding Kincaid by the shirt, fire behind (moment before the s01 shot)
  ('the one who wiped out', 'n4_soulfood', 75.00, -2.80),  # Freddy eating the screaming soul meatball off his claw, Alice beside him
  ('kincaid', 'n4_junkyard', 84.80, -2.00),  # Kincaid in the junkyard, shouting up at Freddy
  ('joey', 'n4_waterbed', 3.50, -1.30),  # Joey's face pressed up under the waterbed's surface
  ('and kristen', 'n4_beach', 40.45, -2.40),  # Kristen sunk in the beach sand, Freddy's legs beside her
  ('the kids who survived', 'n4_hell', 202.40, -1.40),  # Kristen (and Alice) running through the boiler room chains, Kristen green-lit
  ('the last freddy', 'n4_hell', 207.80, -1.10),  # NEW CUT — the furnace burning (Kristen's fate)
  ('are all dead early', 'n4_hell', 182.50, -1.70),  # Freddy close-up among the red-lit chains
  ('in the movie', 'n4_hell', 217.60, -1.30),  # NEW CUT — Freddy's back, covered in the faces of the souls he took, furnace glow
  ('then he goes through alice\'s', 'n4_kiss', 169.20, -2.30),  # Rick, Dan and their friends in the classroom
  ('one by one', 'n4_kiss', 46.50, -1.40),  # NEW CUT — wide classroom: Alice, Sheila (yellow) and classmates at their desks
  ('sheila', 'n4_kiss', 125.30, -2.40),  # Freddy's face closing in on Sheila, claws at her chin (kiss of death)
  ('rick', 'n4_karate', 125.90, -1.80),  # Rick in his gi, close, after being thrown in the karate fight
  ('and debbie', 'n4_roach', 10.90, -1.80),  # Debbie's face, bench-pressing, scared (not the s00 moment)
  ('who he turns into', 'n4_roach', 105.40, -2.40),  # Debbie with the roach legs bursting from her arms
  ('a cockroach', 'n4_roach', 158.00, -3.60),  # NEW CUT — Debbie fully a cockroach on the floor, light behind
  ('and every soul he takes', 'n4_soulfood', 73.15, -1.75),  # the screaming soul meatball on Freddy's claw over the pizza
  ('stays trapped', 'n4_soulfood', 63.10, -1.50),  # NEW CUT — Kincaid's face screaming inside the soul pizza
  ('alice only wins', 'n4_alice', 124.70, -2.20),  # Alice, glowing close-up in the church
  ('by taking on', 'n4_alice', 146.20, -3.20),  # NEW CUT — wide: Alice firing the blue power blast into Freddy's chest
  ('and showing freddy', 'n4_torn', 28.10, -4.90),  # Alice raising the stained-glass shard toward Freddy (Freddy in foreground)
  ('so the souls inside', 'n4_torn', 72.10, -1.85),  # Freddy, claws up, the souls writhing and bursting in his chest
  ('and tear him apart', 'n4_torn', 97.60, -1.30),  # the souls' arms pulling Freddy's body apart
  ('if the kids', 'n4_doctor', 56.95, -1.90, L),  # Freddy close-up against the red tunnel, claw raised
  ('couldn\'t survive', 'n4_alice', 129.20, -1.75, L),  # NEW CUT — Freddy close-up, hat, in the church
  ('you won\'t either', 'n4_alice', 40.60, -1.30, L),  # Freddy laughing/screaming close-up, green light behind
  ('survival rate', 'n4_soulfood', 83.10, -2.70, L),  # Freddy close-up in the diner, hat, Alice's head at right
  ]))
# ---- s11 outro (24.2 s) ----
X.append(sec('s11', [
  (0, 'still_posterwall', 3.0, -2.0),  # callback to the cold open: the full poster wall
  ('from the one who needed', 'fj_collide', 211.20, -3.60),  # Freddy and Jason face off through the water spray, boiler room two-shot
  ('to the one who wiped', 'n4_alice', 99.00, -6.00),  # Freddy leaning in behind Alice, burned face over her shoulder
  ('which freddy would', 'n7_coming_uk', 51.78, -2.95),  # Freddy's face tilted, slowly opening the claws
  ('tell me in the comments', 'n6_forever', 77.35, -6.49),  # Freddy close-up, glove at his chin, smirking
  ('along with the killer', 'n3_taryn', 54.90, -2.60),  # Freddy face to face with Taryn, turning to grin
  ('and honestly', 'n1_wall', 380.20, -1.70),  # Freddy's face at the front-door window
  ('every death in all', 'n5_force_feed', 28.60, -2.9),  # Freddy crushing Greta from behind at the table (n4_kiss wide was 1.65 s clean, too short)
  ('to get this ranking', 'n7_traffic', 95.88, -1.45),  # Freddy on the moon above the clouds, glove up
  ('we\'re a small channel', 'n2_party', 547.40, -3.95),  # Freddy standing among the parents at the party
  ('thanks for watching', 'n1_ending', 90.15, -5.10),  # the girls in white skipping rope on the lawn
  ("don't fall asleep", 'n1_bathroom', 38.20, -5.20),  # the glove fully risen out of the bath water, held to the cut
  ], pad=2.0,
  extra=[('title', ['WHICH FREDDY', '!WOULD YOU LEAST', '!WANT TO MEET?'], 'which freddy would', 'tell me in the comments'),
         ('png', 'tiles/subscribe.png', 'every subscribe', 'thanks for watching'),
         ('title', ["DON'T FALL", '!ASLEEP'], "don't fall asleep", 999)]))
