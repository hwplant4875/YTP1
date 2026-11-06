# EP04 Freddy v3 shot list, read by build_edl_v3.py. A shot is (phrase, clip, in_s, -clean_s[, opts]).
# GENERATED SKELETON from shot_plan_v3.md (cloud, 11/7). On the laptop, replace every TODO pair with the verified in-point and the
# negative clean span (seconds of clean picture from the in-point, no title card, logo or scene cut inside), as in EP07 shots_v8.py.
# Change the clip to another candidate when the first one does not hold the moment, and keep the comment true (what is on screen).
# Extra cuts may be added on other exact script phrases. L = subject left of the stat card.
TODO = None
# ---- s00 cold open (14.8 s) ----
X.append(sec('s00', [
  (0, 'n4_junkyard', TODO, TODO),  # FREDDY close-up, iconic face and hat, bright (frame 0) | also: n3_heres, n4_soulfood
  ('drag you across', 'n1_tina_kill', TODO, TODO),  # Tina dragged up the bedroom wall by the invisible force
  ('the ceiling', 'n1_tina_kill', TODO, TODO),  # Tina on the ceiling
  ('turn you into', 'n3_marionette', TODO, TODO),  # Freddy slices Phillip's arms, the veins come out | also: n3_marionette_uk
  ('a puppet', 'n3_marionette', TODO, TODO),  # Phillip walking like a puppet on his vein strings | also: n3_marionette_uk
  ('smash your head', 'n3_primetime', TODO, TODO),  # the TV Freddy grabs Jennifer's head | also: n3_primetime_wb
  ('through a tv', 'n3_primetime', TODO, TODO),  # her head goes into the TV (cut on the impact) | also: n3_primetime_wb
  ('crush you', 'n4_roach', TODO, TODO),  # Freddy's hand closes the roach motel
  ('like a bug', 'n4_roach', TODO, TODO),  # Debbie as a cockroach / the crush
  ('or pull you down', 'n1_glen_bed', TODO, TODO),  # Glen pulled down into his bed | also: n1_glen
  ('into your own bed', 'n1_glen', TODO, TODO),  # the bed swallows him (cut before the worst of the geyser) | also: n1_glen_bed
  ('and all he needs', 'n1_wall', TODO, TODO),  # Freddy watching, grinning, glove up | also: n1_boiler, n1_preview4k
  ('is for you', 'n1_bathroom', TODO, TODO),  # Nancy in the bath, eyes closing
  ('to fall asleep', 'n1_bathroom', TODO, TODO),  # the glove rises out of the water between her knees
  ("we're ranking", 'still_posterwall', TODO, TODO),  # the 9 posters pop in (release order) and hold to the end
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
  (0, 'n1_screw_sleep', TODO, TODO, L),  # Nancy fighting sleep (coffee, eyes heavy) | also: n1_plan
  ('you fall asleep', 'n3_kristen', TODO, TODO, L),  # a teenager falls asleep in bed | also: n3_bed, r10_m1
  ("and that movie's freddy", 'n1_boiler', TODO, TODO, L),  # the 1984 Freddy in the boiler room | also: n1_opening
  ('is waiting for you', 'n1_opening', TODO, TODO, L),  # Freddy steps out of the shadows / glove on the pipes | also: n1_boiler
  ('and every freddy is different', 'r10_unavoidable', TODO, TODO, L),  # the 2010 Freddy's face | also: r10_creepiest
  ('one is so weak', 'fj_notstrong', TODO, TODO, L),  # the weak Freddy vs. Jason Freddy
  ('he needs jason', 'fj_crash', TODO, TODO, L),  # Jason with the machete | also: fj_rave
  ("one needs a teenager's body", 'n2_brain', TODO, TODO, L),  # Freddy's claws/face coming out of Jesse | also: n2_emerge
  ('and one is strong enough', 'n4_soulfood', TODO, TODO, L),  # the Dream Master Freddy | also: n4_alice
  ('to wipe out kids', 'n4_karate', TODO, TODO, L),  # Freddy beating a Dream Warrior (Rick or Kristen) | also: n4_hell
  ('so we score', 'n1_opening', TODO, TODO, L),  # the glove being forged
  ('intelligence', 'n3_heres', TODO, TODO, L),  # Freddy's trick ("Here's Freddy")
  ('kill count', 'n5_forcefed4k', TODO, TODO, L),  # a Freddy kill | also: n4_kiss
  ('and dream power', 'n3_worm', TODO, TODO, L),  # Freddy turns into the worm
  ('once your eyes close', 'n1_bathroom', TODO, TODO, L),  # eyes closing (another moment than the open) | also: r10_bath_uk
  ('put it all together', 'n6_forever', TODO, TODO, L),  # Freddy close-up
  ('your survival rate', 'n7_coming', TODO, TODO, L),  # the New Nightmare Freddy close-up
  ]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'FREDDY KRUEGER', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'DREAM POWER': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'dream power')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# ---- s02 #9 Freddy vs. Jason 95% (36.6 s, card from "if you've never heard") ----
X.append(sec('s02', [
  (0, 'fj_world', TODO, TODO),  # the Freddy vs. Jason Freddy (rank card over it) | also: fj_notstrong
  ('this freddy is the weakest', 'fj_notstrong', TODO, TODO),  # Freddy weak, powerless in his dream world
  ('because his town forgot', 'fj_intro', TODO, TODO),  # Springwood, a quiet street / houses | also: fj_cornfield
  ('the adults erased', 'fj_intro', TODO, TODO),  # the adults covering it up (cops, parents, files) | also: fj_back
  ('every trace of him', 'fj_intro', TODO, TODO),  # Freddy's past, newspaper clippings or the empty Elm Street house
  ('and anyone who still dreams', 'fj_intro', TODO, TODO),  # the Westin Hills patients (Will, Mark) | also: fj_back
  ('gets locked away', 'fj_back', TODO, TODO),  # Westin Hills hospital | also: fj_influence
  ('and kept on a drug', 'fj_influence', TODO, TODO),  # Hypnocil pills or the injection | also: fj_intro
  ("he's so weak", 'fj_notstrong', TODO, TODO),  # Freddy (frustrated, can't kill)
  ('bring jason back', 'fj_mom', TODO, TODO),  # Freddy disguised as Jason's mother, talking to Jason
  ('to scare people', 'fj_mommy', TODO, TODO),  # Jason rising / walking into Springwood | also: fj_dreaming
  ('in a movie with his own name', 'fj_kicks', TODO, TODO),  # Freddy | also: fj_world
  ('jason does nearly all', 'fj_rave', TODO, TODO),  # Jason slaughtering the rave | also: fj_crash
  ('and freddy kills exactly', 'fj_back', TODO, TODO),  # Freddy goes after Mark
  ('one person himself', 'fj_back', TODO, TODO),  # Mark's death ("Freddy's back" on his back)
  ('in the end lori', 'fj_hell', TODO, TODO),  # Lori with Jason's machete | also: fj_construction
  ('cuts his head off', 'fj_hell', TODO, TODO),  # the swing / Freddy's head (cut on the hit)
  ("with jason's machete", 'fj_hell', TODO, TODO),  # Jason holding Freddy's head, the wink
  ("if you've never heard", 'fj_notstrong', TODO, TODO, L),  # Freddy fading (L)
  ("he can't even find", 'fj_world', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'fj_kicks', TODO, TODO, L),  # Freddy close-up (L)
  ]))
# ---- s03 #8 Freddy's Revenge 65% (42.9 s, card from "stay far away") ----
X.append(sec('s03', [
  (0, 'n2_brain', TODO, TODO),  # the Freddy's Revenge Freddy (rank card)
  ('this freddy is far more', 'n2_pool', TODO, TODO),  # Freddy menacing at the party | also: n2_party
  ("because he doesn't need", 'n2_emerge', TODO, TODO),  # Freddy close-up
  ('he takes over a teenager', 'n2_kill4k', TODO, TODO),  # Jesse possessed, sweating | also: n2_brain
  ('named jesse', 'n2_kill4k', TODO, TODO),  # Jesse
  ('climbs right out', 'n2_brain', TODO, TODO),  # Freddy bursting out of Jesse's body | also: n2_emerge
  ('and kills more people', 'n2_pool', TODO, TODO),  # panic at the pool party
  ('than any other freddy', 'n2_party', TODO, TODO),  # Freddy at the party
  ("he kills jesse's gym teacher", 'n2_creepiest', TODO, TODO),  # Coach Schneider in the showers
  ('in the showers', 'n2_creepiest', TODO, TODO),  # the shower attack
  ('then his friend grady', 'n2_kill4k', TODO, TODO),  # Grady attacked in his bedroom | also: n2_grady_fan
  ('then a whole group', 'n2_pool', TODO, TODO),  # kids attacked at the pool party
  ('and in the very last scene', 'n2_creepiest', TODO, TODO),  # the final bus scene | also: n2_kerry_fan
  ('his claws burst out', 'n2_creepiest', TODO, TODO),  # the claws burst out of Kerry | also: n2_kerry_fan
  ('on the school bus', 'n2_bus', TODO, TODO),  # the bus speeding off | also: n2_schoolbus
  ("but he's also the dumbest", 'n2_party', TODO, TODO),  # Freddy (clumsy, showy)
  ('he barely uses', 'n2_pool', TODO, TODO),  # Freddy in the real world at the pool
  ('and he can be beaten', 'n2_creepiest', TODO, TODO),  # Lisa confronting Freddy | also: n2_kiss_fan
  ('lisa tells jesse', 'n2_creepiest', TODO, TODO),  # Lisa | also: n2_kiss_fan
  ('kisses freddy', 'n2_creepiest', TODO, TODO),  # the kiss | also: n2_kiss_fan
  ('and he burns to ash', 'n2_creepiest', TODO, TODO),  # Freddy burns away | also: n2_kiss_fan
  ('stay far away', 'n2_kill4k', TODO, TODO, L),  # Jesse (L)
  ("and you'll probably be fine", 'n2_creepiest', TODO, TODO, L),  # Lisa and Jesse (L)
  ('survival rate', 'n2_brain', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s04 #7 The Dream Child 55% (39.9 s, card from "he only gets three") ----
X.append(sec('s04', [
  (0, 'n5_tricks', TODO, TODO),  # the Dream Child Freddy (rank card) | also: n5_son4k
  ('this freddy kills fewer', 'n5_hell4k', TODO, TODO),  # Freddy
  ("but he's far smarter", 'n5_superfreddy', TODO, TODO),  # Freddy smirking
  ('and much stronger', 'n5_pool', TODO, TODO),  # Freddy's dream power
  ('he finds a sneaky', 'n5_son4k', TODO, TODO),  # pregnant Alice / the unborn baby | also: n5_itsaboy
  ('through the dreams', 'n5_son4k', TODO, TODO),  # Jacob, the child
  ('so he can come', 'n5_drunk', TODO, TODO),  # Freddy coming for her friends | also: n5_motorcycle
  ("even while she's wide", 'n5_tricks', TODO, TODO),  # Alice awake and scared
  ('he turns dan', 'n5_motorcycle', TODO, TODO),  # Dan on the motorcycle | also: n5_drunk
  ('into part of his own', 'n5_motorcycle', TODO, TODO),  # Dan fused with the bike
  ('force-feeds greta', 'n5_forcefed4k', TODO, TODO),  # Greta force-fed by Freddy | also: n5_force_feed
  ('until she chokes', 'n5_force_feed', TODO, TODO),  # Greta choking | also: n5_forcefed4k
  ('and turns mark', 'n5_superfreddy', TODO, TODO),  # Mark pulled into the comic book
  ('into a paper drawing', 'n5_superfreddy', TODO, TODO),  # Mark as paper
  ('before slicing him', 'n5_superfreddy', TODO, TODO),  # Super Freddy slices him
  ('but alice has beaten', 'n5_tricks', TODO, TODO),  # Alice
  ('and in the end', 'n5_hell4k', TODO, TODO),  # Amanda Krueger, Freddy's mother | also: n5_back_to_hell
  ('jacob uses the power', 'n5_back_to_hell', TODO, TODO),  # Jacob using his power | also: n5_hell4k
  ('to destroy him', 'n5_back_to_hell', TODO, TODO),  # Freddy pulled apart
  ('he only gets three', 'n5_baby4k', TODO, TODO, L),  # Freddy (L) | also: n5_baby
  ('so if he comes', 'n5_tricks', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'n5_son4k', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s05 #6 Freddy's Dead 45% (45.3 s, card from "he's deadly but") ----
X.append(sec('s05', [
  (0, 'n6_forever', TODO, TODO),  # the Freddy's Dead Freddy (rank card)
  ('unlike the last one', 'n6_father', TODO, TODO),  # Freddy
  ('has the biggest body count', 'n6_town', TODO, TODO),  # empty Springwood
  ('before the movie even starts', 'n6_town', TODO, TODO),  # the empty town, the carnival, the strange adults
  ('almost every child', 'n6_town', TODO, TODO),  # missing children posters / empty school
  ("but he's also the silliest", 'n6_oz', TODO, TODO),  # Freddy on the broomstick
  ('and he plays with his victims', 'n6_playground', TODO, TODO),  # Freddy playing with a victim | also: n6_game
  ("he turns up carlos's", 'n6_ear', TODO, TODO),  # Carlos's hearing aid | also: n6_earcheck
  ('until one scratch', 'n6_chalk', TODO, TODO),  # Freddy's claws on the chalkboard | also: n6_nice
  ('kills him', 'n6_nice', TODO, TODO),  # Carlos's reaction (no explosion frame)
  ('traps spencer inside', 'n6_game', TODO, TODO),  # Spencer pulled into the video game | also: n6_drug
  ('a video game', 'n6_game', TODO, TODO),  # Freddy with the Power Glove
  ('and drops john doe', 'n6_doom', TODO, TODO),  # John Doe falling
  ('the last teenager', 'n6_busrt', TODO, TODO),  # John Doe | also: n6_doom
  ('onto a bed of spikes', 'n6_doom', TODO, TODO),  # the spikes (cut before the impact)
  ('all those jokes', 'n6_forever', TODO, TODO),  # Freddy laughing
  ('tracy gets woken', 'n6_father', TODO, TODO),  # Tracy attacked in the dream, then wakes
  ('before he can finish', 'n6_father', TODO, TODO),  # Tracy fights him off
  ('in the end his own daughter', 'n6_daughter', TODO, TODO),  # Maggie | also: n6_blood
  ('drags him into the real', 'n6_maggie', TODO, TODO),  # Maggie pulls him out
  ('and shoves a pipe bomb', 'n6_maggie', TODO, TODO),  # the pipe bomb in his chest
  ("he's deadly but", 'n6_brain', TODO, TODO, L),  # Freddy (L)
  ('and that time is', 'n6_maggie', TODO, TODO, L),  # Freddy blown up / gone (L)
  ('survival rate', 'n6_forever', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s06 #5 the 2010 remake 38% (39.3 s, card from "staying awake won't") ----
X.append(sec('s06', [
  (0, 'r10_creepiest', TODO, TODO),  # the 2010 Freddy (rank card) | also: r10_unavoidable
  ('this freddy is the opposite', 'r10_unavoidable', TODO, TODO),  # the dark 2010 Freddy
  ("he's dark mean", 'r10_boyfriend', TODO, TODO),  # Freddy close-up
  ('and serious', 'r10_dreaming', TODO, TODO),  # Freddy
  ('and he has a trick', 'r10_m3', TODO, TODO),  # Quentin in the store
  ('that makes staying awake', 'r10_m1', TODO, TODO),  # Nancy fighting sleep | also: r10_m2
  ('go too long without', 'r10_m3', TODO, TODO),  # tired eyes, pills
  ('and your brain drops', 'r10_m3', TODO, TODO),  # the micro-nap flicker
  ('for a few seconds', 'r10_m3', TODO, TODO),  # Freddy appears in the store
  ('without you even noticing', 'r10_m3', TODO, TODO),  # snapping back awake
  ('by the time nancy figures', 'r10_m4', TODO, TODO),  # Nancy
  ('every other kid', 'r10_creepiest', TODO, TODO),  # the preschool photo | also: r10_m4
  ('except her and quentin', 'r10_m4', TODO, TODO),  # Nancy and Quentin
  ('he gets dean', 'r10_preview', TODO, TODO),  # Dean in the diner | also: r10_dean_fan
  ('kris in her bedroom', 'r10_creepiest', TODO, TODO),  # Kris thrown around her bedroom | also: r10_kris_fan
  ('and jesse in a jail cell', 'r10_creepiest', TODO, TODO),  # Jesse in the cell
  ('and even after nancy drags', 'r10_creepiest', TODO, TODO),  # Nancy pulls Freddy out
  ('and cuts his throat', 'r10_creepiest', TODO, TODO),  # the throat cut (cut on the move)
  ('he comes back through', 'r10_creepiest', TODO, TODO),  # the mirror attack on Nancy's mother
  ("staying awake won't", 'r10_boyfriend', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'r10_dreaming', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s07 #4 New Nightmare 30% (38.9 s, card from "he only gets four") ----
X.append(sec('s07', [
  (0, 'n7_coming', TODO, TODO),  # the New Nightmare Freddy (rank card)
  ('this freddy is stronger', 'n7_missme', TODO, TODO),  # Freddy
  ("and he doesn't just hunt", 'n7_stalks', TODO, TODO),  # Freddy
  ('he hunts a whole family', 'n7_dylan', TODO, TODO),  # Heather, Dylan and Chase at home
  ('he goes after heather', 'n7_stalks', TODO, TODO),  # Heather scared
  ('the actress who played', 'n7_funeral', TODO, TODO),  # Heather | also: n7_dylan
  ('and picks off the people', 'n7_funeral', TODO, TODO),  # the funeral
  ('he kills two special', 'n7_hand', TODO, TODO),  # the new glove attacks the effects men on set | also: n7_handbed, n7_bloodiest
  ('working on a new', 'n7_hand', TODO, TODO),  # the film set | also: n7_bloodiest
  ('then her husband', 'n7_bloodiest', TODO, TODO),  # Chase driving at night, nodding off | also: n7_chase_fan
  ("while he's driving", 'n7_bloodiest', TODO, TODO),  # the claws, the crash | also: n7_chase_fan
  ("then her son's babysitter", 'n7_julie', TODO, TODO),  # Julie in the hospital
  ('dragging her up the wall', 'n7_julie', TODO, TODO),  # Julie dragged up the wall
  ('then he takes her little', 'n7_traffic', TODO, TODO),  # Dylan | also: n7_dylan
  ('right into his world', 'n7_end', TODO, TODO),  # Freddy's lair
  ('it takes heather and dylan', 'n7_end', TODO, TODO),  # Heather and Dylan together
  ('to push him into', 'n7_end', TODO, TODO),  # the furnace
  ('he only gets four', 'n7_surgery', TODO, TODO, L),  # Freddy (L)
  ('but if he picks', 'n7_son', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'n7_coming_uk', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s08 #3 the 1984 original 22% (42.2 s, card from "unless you're as") ----
X.append(sec('s08', [
  (0, 'n1_preview4k', TODO, TODO),  # the 1984 Freddy (rank card) | also: n1_wall
  ('from nineteen eighty-four', 'n1_opening', TODO, TODO),  # the 1984 glove / Freddy in the boiler room | also: n1_preview4k
  ("this freddy isn't as strong", 'n1_tina_chase', TODO, TODO),  # Freddy in the alley
  ("but he's the scariest", 'n1_boiler', TODO, TODO),  # Freddy in the shadows
  ('he barely talks', 'n1_opening', TODO, TODO),  # silent Freddy
  ('he stays in the shadows', 'n1_tina_chase', TODO, TODO),  # Freddy half hidden in the dark
  ('and nobody believes you', 'n1_plan', TODO, TODO),  # Nancy with her mother or the police | also: n1_screw_sleep
  ("until it's too late", 'n1_dark_story', TODO, TODO),  # Nancy alone
  ('he drags tina', 'n1_tina_kill', TODO, TODO),  # Tina dragged (another moment than the open)
  ('across the ceiling', 'n1_tina_kill', TODO, TODO),  # Tina on the ceiling (another moment than the open)
  ('strangles rod', 'n1_rod', TODO, TODO),  # the bedsheet around Rod's neck
  ('in a jail cell', 'n1_rod', TODO, TODO),  # the cell
  ('and pulls glen down', 'n1_glen', TODO, TODO),  # Glen in bed (another moment than the open)
  ('nancy only survives', 'n1_plan', TODO, TODO),  # Nancy
  ('to learn his rules', 'n1_plan', TODO, TODO),  # Nancy planning
  ('she sets traps', 'n1_traps', TODO, TODO),  # the traps
  ('drags him into the real', 'n1_fight', TODO, TODO),  # Nancy pulls Freddy out
  ('and finally turns her back', 'n1_no_fear', TODO, TODO),  # Nancy turns her back
  ('taking away the fear', 'n1_no_fear', TODO, TODO),  # Freddy vanishes
  ('and even then', 'n1_ending', TODO, TODO),  # Marge
  ('he still takes her mother', 'n1_ending', TODO, TODO),  # Marge pulled through the window
  ("unless you're as", 'n1_plan', TODO, TODO, L),  # Nancy (L)
  ('he gets you', 'n1_god', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'n1_wall', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s09 #2 Dream Warriors 12% (40.3 s, card from "you don't have") ----
X.append(sec('s09', [
  (0, 'n3_heres', TODO, TODO),  # the Dream Warriors Freddy (rank card)
  ('this freddy is deadlier', 'n3_real', TODO, TODO),  # Freddy
  ('because kids who learn', 'n3_best4k', TODO, TODO),  # the Dream Warriors in the dream
  ("still can't stop", 'n3_souls', TODO, TODO),  # Freddy
  ('he hunts the last children', 'n3_best4k', TODO, TODO),  # the group at Westin Hills
  ('in a mental hospital', 'n3_wizard', TODO, TODO),  # the hospital corridor | also: n3_best4k
  ('he turns phillip', 'n3_marionette_uk', TODO, TODO),  # Phillip (another moment than the open)
  ('using his own veins', 'n3_marionette_uk', TODO, TODO),  # Freddy working the vein strings
  ("smashes jennifer's head", 'n3_primetime_wb', TODO, TODO),  # Jennifer and the TV (another moment than the open)
  ('and kills taryn', 'n3_taryn', TODO, TODO),  # Taryn, syringe fingers
  ('and will', 'n3_wizard_rt', TODO, TODO),  # Will in his wheelchair
  ('even after they find', 'n3_wizard', TODO, TODO),  # Will's wizard magic
  ('then his skeleton kills', 'n3_skeleton', TODO, TODO),  # the skeleton attacks Donald
  ('in the real world', 'n3_skeleton', TODO, TODO),  # the junkyard
  ('and freddy kills nancy', 'n3_nancy', TODO, TODO),  # Freddy stabs Nancy
  ('while pretending to be', 'n3_nancy', TODO, TODO),  # Freddy disguised as her father
  ('so even the girl', 'n3_nancy', TODO, TODO),  # Nancy dying
  ('the kids who survived', 'n3_best4k', TODO, TODO),  # Kristen, Kincaid and Joey
  ('and it still took', 'n3_skeleton', TODO, TODO),  # Neil with the holy water
  ('on his bones', 'n3_skeleton', TODO, TODO),  # the bones burning
  ("you don't have", 'n3_heres', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'n3_real', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s10 #1 The Dream Master 5% (38.1 s, card from "if the kids") ----
X.append(sec('s10', [
  (0, 'n4_junkyard', TODO, TODO),  # the Dream Master Freddy reborn (rank card) | also: n4_reborn
  ('this freddy is the strongest', 'n4_reborn', TODO, TODO),  # Freddy
  ('the one who wiped out', 'n4_soulfood', TODO, TODO),  # Freddy
  ('kincaid', 'n4_junkyard', TODO, TODO),  # Kincaid in the junkyard
  ('joey', 'n4_waterbed', TODO, TODO),  # Joey and the waterbed | also: n4_nurse
  ('and kristen', 'n4_beach', TODO, TODO),  # Kristen on the beach
  ('the kids who survived', 'n4_hell', TODO, TODO),  # Kristen thrown into the furnace
  ('are all dead early', 'n4_hell', TODO, TODO),  # Freddy
  ("then he goes through alice's", 'n4_alice', TODO, TODO),  # Alice and her friends
  ('sheila', 'n4_kiss', TODO, TODO),  # Sheila's kiss of death
  ('rick', 'n4_karate', TODO, TODO),  # Rick's karate fight
  ('and debbie', 'n4_roach', TODO, TODO),  # Debbie (another moment than the open)
  ('who he turns into', 'n4_roach', TODO, TODO),  # the roach transformation
  ('and every soul he takes', 'n4_soulpizza', TODO, TODO),  # the souls in his chest | also: n4_soulfood
  ('alice only wins', 'n4_alice', TODO, TODO),  # Alice
  ('and showing freddy', 'n4_death', TODO, TODO),  # the mirror, his reflection | also: n4_torn
  ('so the souls inside', 'n4_torn', TODO, TODO),  # the souls breaking out
  ('and tear him apart', 'n4_torn', TODO, TODO),  # Freddy torn apart
  ('if the kids', 'n4_doctor', TODO, TODO, L),  # Freddy (L)
  ("you won't either", 'n4_alice', TODO, TODO, L),  # Freddy (L)
  ('survival rate', 'n4_soulfood', TODO, TODO, L),  # Freddy (L)
  ]))
# ---- s11 outro (24.2 s) ----
X.append(sec('s11', [
  (0, 'still_posterwall', TODO, TODO),  # callback to the cold open: the poster wall
  ('from the one who needed', 'fj_collide', TODO, TODO),  # Freddy and Jason
  ('to the one who wiped', 'n4_alice', TODO, TODO),  # the Dream Master Freddy
  ('which freddy would', 'n7_coming_uk', TODO, TODO),  # Freddy
  ('tell me in the comments', 'n6_forever', TODO, TODO),  # Freddy
  ('along with the killer', 'n3_heres', TODO, TODO),  # Freddy
  ('and honestly', 'n1_god', TODO, TODO),  # Freddy
  ('every death in all', 'n4_kiss', TODO, TODO),  # a quick kill | also: n5_forcefed4k
  ('to get this ranking', 'n7_missme', TODO, TODO),  # Freddy
  ("we're a small channel", 'n2_party', TODO, TODO),  # Freddy
  ('thanks for watching', 'n1_ending', TODO, TODO),  # the girls skipping rope
  ("don't fall asleep", 'n1_bathroom', TODO, TODO),  # the glove in the bath, hold to the end (pad 2.0 s)
  ], pad=2.0,
  extra=[('title', ['WHICH FREDDY', '!WOULD YOU LEAST WANT TO MEET?'], 'which freddy would', 'tell me in the comments'),
         ('png', 'tiles/subscribe.png', 'every subscribe', 'thanks for watching'),
         ('title', ["DON'T FALL", '!ASLEEP'], "don't fall asleep", 999)]))
