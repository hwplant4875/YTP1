# Backrooms special shot list, read by build_edl.py (11/7 KST).
# A shot is (phrase, clip, in_s, -clean_s[, opts]): it starts 0.08 s before the first word of the exact script phrase and runs until
# the next shot. in_s = the in-point in the clip (seconds), -clean_s = seconds of clean picture from the in-point (no cut to another
# scene, no text, no end card); the builder slows a shot (never below 0.4x) when the clean span is shorter than its slot.
# opts (string): z=zoom (1.333 fills a 4:3 tape), dx/dy=pan in px, flip=1, g=gamma, a=clip audio dB (real foley under the voice).
# GENERATED SKELETON from shot_plan.md (cloud, 11/7): on the laptop replace every TODO with the verified in-point and clean span,
# switch to another candidate clip when the first one does not hold the moment, and keep each comment true to what is on screen.
# Extra cuts can be added on any other exact script phrase. Do not use: end_phil, s2_therapy, s7_dinner_full, s4_tree_pool (subtitles),
# the trailer and x_a24_c/d text or logo spans, and the last 16 s of every JoBlo clip (end card).
# Inserts: ins(after_phrase, seconds, kind, shots=[(t, clip, in, 1.0, opts)], sub=..., q=...). For a film line, in = 0.25 s before the
# first word, seconds = line length + 0.35 s, opts 'lufs=-17' (the line is levelled), sub = the words exactly as spoken.
TODO = None
T4 = 'z=1.333'   # the 1990 tape is 4:3 inside 16:9: zoom to fill
# ---------------------------------------------------------------- s00 cold open (15.7 s): one hard cut per caption --------------
X.append(sec('s00', [
  (0, 's7_joblo_reveal', TODO, TODO),            # FRAME 0: Captain Clark big and clear (pirate hat, towering) ~3:51-3:56 or 4:07; or s8_pack_a/b
  ('went into', 's3_kids_enter', TODO, TODO),    # someone stepping through the glowing slit into the wall (Kat/Bobby or Clark)
  ('the backrooms', 's1_joblo_first', TODO, TODO),   # the iconic empty yellow rooms, wide, fluorescent ceiling
  ('in this movie', 's8_joblo_fight', TODO, TODO),   # the Escher space: endless floors around the giant drop (wide)
  ('and they got', 's7_joblo_reveal', TODO, TODO),   # Mary terrified (close)
  ('chased', 's8_chase_a', TODO, TODO),          # Mary sprinting down the fake apartment street, Captain Clark behind her
  ('dragged', 's3_joblo_pullup', TODO, TODO),    # Bobby yanked down the ramp on the rope (~1:42), never the body
  ('lost', 's3_joblo_pullup', TODO, TODO),       # Kat behind the glass shouting for Clark (5:15-6:20), or Clark alone in the halls
  ('eaten', 's7_joblo_reveal', TODO, TODO),      # Captain Clark lifts Clark (~4:4x), cut before the bite
  ('and umm', 's7_joblo_reveal', TODO, TODO),    # Clark at the dinner table grinning (a beat of awkward calm)
  ('copied', 's4_tree_b', TODO, TODO),           # a still life's blank, misshapen face (the red-haired woman) or end_mary_still (Mary's copy)
  ('only one of them', 's8_chase_a', TODO, TODO),    # Mary running toward camera
  ('made it back out', 'end_extract', TODO, TODO),   # hazmat men pull Mary out of the gas
  ('and even she', 'end_joblo_phil', TODO, TODO),    # Mary in the Async room (blue/white)
  ('never got to go home', 'end_mary_still', TODO, TODO),  # the copy of Mary's house / her life (ending montage)
  ("now it's your turn", 's1_a24_clip', TODO, TODO),     # the thin line of light glowing in the dark store wall
  ('and how long', 's1_joblo_first', TODO, TODO),    # slow push into a yellow hallway (POV)
  ('would you survive', 's8_pack_a', TODO, TODO),    # Captain Clark's silhouette far down a hall
  ('in the backrooms', 's1_joblo_first', TODO, TODO),  # endless yellow rooms, slow push, hold to the cut
  ], extra=[('cap', w, a, b) for w, a, b in [
    ('Five people', 0, 'went into'), ('Went into', 'went into', 'the backrooms'), ('The Backrooms', 'the backrooms', 'in this movie'),
    ('In this movie', 'in this movie', 'and they got'), ('And they got', 'and they got', 'chased'), ('Chased', 'chased', 'dragged'),
    ('Dragged', 'dragged', 'lost'), ('Lost', 'lost', 'eaten'), ('Eaten', 'eaten', 'and umm'), ('And, umm...', 'and umm', 'copied'),
    ('Copied?', 'copied', 'only one of them'), ('Only one of them', 'only one of them', 'made it back out'),
    ('Made it back out', 'made it back out', 'and even she'), ('And even she', 'and even she', 'never got to go home'),
    ('Never got to go home', 'never got to go home', "now it's your turn"), ("Now it's your turn", "now it's your turn", 'and how long'),
    ('And how long', 'and how long', 'would you survive'), ('Would you survive', 'would you survive', 'in the backrooms'),
    ('In the Backrooms?', 'in the backrooms', 999)]], clip_db=-22))
# ---------------------------------------------------------------- s01 the 1990 tape (35.4 s) ------------------------------------
X.append(sec('s01', [
  (0, 'op_joblo_1990', TODO, TODO, T4),             # the tape: an empty yellow room, VHS look
  ('naren a researcher', 'op_joblo_1990', TODO, TODO, T4),   # Naren (Async researcher) walking, flashlight/radio
  ('has lost his team', 'op_joblo_1990', TODO, TODO, T4),    # Naren alone, turning, calling out
  ("and he's on the radio", 'op_joblo_1990', TODO, TODO, T4),  # Naren with the radio at his mouth (radio call 1:40-2:28)
  ('nobody answers', 'op_joblo_1990', TODO, TODO, T4),       # static, Naren waiting, the hum
  ('down the hall a door', 'op_joblo_1990', TODO, TODO, T4),  # a lit doorway far down the dark corridor (4:36-4:46)
  ('something huge steps out', 'op_joblo_1990', TODO, TODO, T4),  # the black silhouette filling the doorway (5:12.2-5:12.7, slow it)
  ('and naren runs', 'op_joblo_1990', TODO, TODO, T4),       # the camera swings and runs (4:46-4:47 or after 5:12)
  ('a room covered in', 'op_joblo_1990', TODO, TODO, T4),    # the dead end of vacation photos
  ('and the moment he runs back', 'op_joblo_1990', TODO, TODO, T4),  # Naren turning back
  ('he runs straight into it', 'op_joblo_1990', TODO, TODO, T4),     # the scream / the camera dropping (~5:19), nothing graphic
  ('he had training', 'op_joblo_1990', TODO, TODO, T4),      # the tape lying still, the empty hall
  ('and you have none of that', 's1_a24_clip', TODO, TODO),   # Clark alone in his dark furniture store at night
  ('the number in the corner', 's1_joblo_first', TODO, TODO),  # Clark crawling into an empty yellow room (1:31) - the corner appears
  ('and in here', 's1_joblo_first', TODO, TODO),              # endless yellow rooms
  ], inserts=[ins('come and get him', 2.6, 'film', shots=[(0, 'op_joblo_1990', TODO, 1.0, T4 + ',lufs=-17')], sub="There's something else in here.")],
  extra=[('date', ['JUNE 19, 1990'], 'dated june nineteenth', 'naren a researcher')]))
# ---------------------------------------------------------------- s02 THE SLIT (74.2 s) -----------------------------------------
X.append(sec('s02', [
  (0, 's1_commercial', TODO, TODO),            # Clark's store / the in-film commercial (Cap'n Clark at the helm) - the failing store
  ('a failed architect', 's1_a24_clip', TODO, TODO),   # Clark in the store, tired
  ('who sleeps in the back', 's1_rt_clip', TODO, TODO),  # Clark sleeping in the back of the store (check what s1_rt_clip holds)
  ('the lights flicker', 's1_a24_clip', TODO, TODO),     # store lights flickering on their own
  ('there are two breakers', 's1_first_a', TODO, TODO),  # the breaker box / the meterman finding two extra breakers
  ('and one night the tv', 's1_first_a', TODO, TODO),    # the TV glitching
  ('with a figure standing', 's1_first_a', TODO, TODO),  # the security-camera feed: a figure in a doorway
  ('you flip the strange breakers', 's1_a24_clip', TODO, TODO),  # Clark at the breaker box
  ('the store goes dark', 's1_a24_clip', TODO, TODO),    # darkness
  ('and there it is', 's1_a24_clip', TODO, TODO),        # Clark turning, seeing the glow
  ('a thin line of light', 's1_a24_clip', TODO, TODO),   # the glowing slit inside the wall (hold, slow push)
  ('you lean on it', 's1_joblo_first', TODO, TODO),      # Clark leans on the wall and falls through
  ('into an empty yellow room', 's1_joblo_first', TODO, TODO),  # Clark on the floor of a yellow room (1:31)
  ('of melted furniture', 's1_joblo_first', TODO, TODO),  # fused / melted furniture
  ('and since you can step', 's1_joblo_first', TODO, TODO),  # the slit from inside, the store visible through it
  ('you explore', 's1_joblo_first', TODO, TODO),          # Clark walking deeper, yellow halls
  ("there's a backwards stop sign", 's1_joblo_first', TODO, TODO),  # the backwards stop sign
  ('a dead bird', 's1_joblo_first', TODO, TODO),          # the dead bird (not lingering)
  ('and a voice saying hello', 's1_joblo_first', TODO, TODO),  # Clark hearing the voice, turning
  ('in dozens of languages', 's1_joblo_first', TODO, TODO),    # Clark following the sound
  ('coming from a cardboard caveman', 's1_joblo_first', TODO, TODO),  # the caveman cutout with the tape recorder
  ('behind a fake tile', 's1_joblo_first', TODO, TODO),   # Clark lifting a ceiling tile
  ("naren's bag full of tapes", 's1_joblo_first', TODO, TODO),  # Naren's duffel, the tapes
  ('and further in', 's1_joblo_first', TODO, TODO),       # deeper rooms
  ('the chair from your own', 's1_joblo_first', TODO, TODO),  # the copy of the commercial chair
  ('slightly wrong', 's1_joblo_first', TODO, TODO),       # the chair close, wrong
  ('with shoes sticking out', 's1_joblo_first', TODO, TODO),  # shoes sunk into the floor
  ('then the thuds start', 's1_joblo_first', TODO, TODO),  # Clark freezing, listening
  ('the caveman flies', 's1_joblo_first', TODO, TODO),    # the caveman hurled and smashed
  ('and you squeeze through', 's1_joblo_first', TODO, TODO),  # the tiny door (3:02 hole?), Clark squeezing through
  ('and run until', 's1_first_b', TODO, TODO),            # Clark running
  ('back in your store', 's1_first_b', TODO, TODO),       # Clark back in the store gripping a stool
  ('a camera in there', 's1_joblo_first', TODO, TODO),    # a security camera on a Backrooms wall
  ('on a tape dated', 's1_joblo_first', TODO, TODO),      # the tape of Clark's entry (camera POV) or the slit
  ('one trip through that wall', 's1_a24_clip', TODO, TODO),  # the slit glowing
  ('gives you a ninety', 's1_first_b', TODO, TODO),       # Clark staring at the wall, breathing (the 90% lands)
  ('the best it will ever be', 's1_joblo_first', TODO, TODO),  # wide empty yellow room
  ('rule one', 's1_joblo_first', TODO, TODO),             # the wrong copy of his chair again
  ('leave', 's1_first_b', TODO, TODO),                    # Clark backing away from the wall
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do')],
  extra=[('date', ['JUNE 29, 1990'], 'dated june twenty-ninth', 'one trip through that wall')]))
# ---------------------------------------------------------------- s03 THE MAP (39.6 s) ------------------------------------------
X.append(sec('s03', [
  (0, 's1_a24_clip', TODO, TODO),              # Clark at the glowing wall again
  ('you go back every night', 's1_first_b', TODO, TODO),  # Clark stepping in again (flashlight, notebook)
  ('and you start drawing a map', 's2_tells_mary', TODO, TODO),  # Clark's maze map / drawing
  ('you ask your therapist mary', 's2_tells_mary', TODO, TODO),  # the therapy room, Mary listening
  ("if she's ever had someone committed", 's2_tells_mary', TODO, TODO),  # Clark asking ("ever 5150 someone")
  ('then tell her the store', 's2_tells_mary', TODO, TODO),   # Clark explaining
  ('close but wrong', 's2_tells_mary', TODO, TODO),           # Mary's face
  ('like a dog drawn by someone', 's2_tells_mary', TODO, TODO),  # the dog drawing
  ('and your map is a maze', 's2_tells_mary', TODO, TODO),    # the maze map
  ('that goes on and on', 's2_tells_mary', TODO, TODO),       # Clark, quiet
  ("she doesn't believe you", 's2_tells_mary', TODO, TODO),   # Mary unconvinced
  ('so you swear', 's2_tells_mary', TODO, TODO),              # Clark determined
  ('that drops you to seventy', 's1_joblo_first', TODO, TODO),  # Clark alone in the yellow rooms (the 70% lands)
  ('because a trained scientist', 'op_joblo_1990', TODO, TODO, T4),  # Naren on the 1990 tape with his radio
  ('and you keep going in alone', 's1_joblo_first', TODO, TODO),  # Clark deeper, alone
  ('rule two', 's1_first_b', TODO, TODO),                     # the slit / Clark stepping through
  ('because this place only has to win once', 's1_joblo_first', TODO, TODO),  # endless hall, slow push
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('and on and on', 2.8, 'film', shots=[(0, 's2_tells_mary', TODO, 1.0, 'lufs=-17')], sub="Sometimes I'm scared I'll get lost.")]))
# ---------------------------------------------------------------- s04 THE LAUNDRY ROOM (47.0 s) ---------------------------------
X.append(sec('s04', [
  (0, 's3_kids_enter', TODO, TODO),            # Clark with the camera, Kat and Bobby at the store
  ('your assistant manager kat', 's3_kids_enter', TODO, TODO),  # Kat
  ('and her boyfriend bobby', 's3_kids_enter', TODO, TODO),     # Bobby
  ('and you lead them', 's3_kids_enter', TODO, TODO),     # the three stepping through the wall
  ('a steep ramp down', 's3_joblo_pullup', TODO, TODO),   # the ramp to the lower level
  ('bobby volunteers', 's3_joblo_pullup', TODO, TODO),    # Bobby ready to go down
  ('you tie a rope', 's3_joblo_pullup', TODO, TODO),      # the rope tied to the bed
  ('and he jokes', 's3_bobby', TODO, TODO),               # Bobby joking ("tell my mom I love her")
  ('down there is a basement', 's3_laundry', TODO, TODO),  # the laundry basement
  ('with a t-shirt bobby', 's3_laundry', TODO, TODO),     # the T-shirt he wore earlier
  ('a room turned on its side', 's3_joblo_pullup', TODO, TODO),  # the tilted room (1:39)
  ('a cardboard caveman torn in half', 's3_laundry', TODO, TODO),  # the torn caveman
  ('and when a light flickers', 's3_laundry', TODO, TODO),  # flicker
  ('bobby sees something', 's3_laundry', TODO, TODO),     # Bobby staring into the dark
  ('you pull', 's3_joblo_pullup', TODO, TODO),            # Clark and Kat hauling the rope
  ('but something pulls harder', 's3_joblo_pullup', TODO, TODO),  # the rope snaps taut, yanked
  ('dragging the bed', 's3_joblo_pullup', TODO, TODO),    # the bed sliding toward the ramp
  ('just in time to see bobby', 's3_joblo_pullup', TODO, TODO),  # Bobby gone through a door (~1:42)
  ('leaving a long trail of blood', 's3_joblo_pullup', TODO, TODO),  # the blood trail only, never the body
  ("you're down to forty", 's3_joblo_pullup', TODO, TODO),  # Kat and Clark in shock (the 40% lands)
  ('rule three', 's3_joblo_pullup', TODO, TODO),          # the ramp, looking down
  ('and if your clothes got there', 's3_laundry', TODO, TODO),  # the T-shirt again
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('standing in the dark', 2.2, 'film', shots=[(0, 's3_laundry', TODO, 1.0, 'lufs=-17')], sub="There's someone down there!")]))
# ---------------------------------------------------------------- s05 THE STILL LIFES (44.1 s) ----------------------------------
X.append(sec('s05', [
  (0, 's4_chase', TODO, TODO),                 # Clark and Kat running after Bobby
  ('and lose each other', 's4_chase', TODO, TODO),        # Clark alone, calling out
  ('while something heavy thuds', 's4_tree_a', TODO, TODO),  # dark levels, Clark hiding
  ('room after room', 's4_tree_a', TODO, TODO),           # running through dark rooms
  ('until you stumble into a dark room', 's4_tree_b', TODO, TODO),  # the dark room
  ('lit only by a glowing christmas tree', 's4_tree_b', TODO, TODO),  # the Christmas tree (s4_tree_b ~30-52 s, s3_joblo_pullup ~237 s)
  ('with people fused into the floor', 's4_tree_b', TODO, TODO),  # people fused into the floor
  ('a half-man in a wheelchair', 's4_tree_b', TODO, TODO),  # the half man switching on the lamp
  ('and a red-haired woman', 's4_tree_b', TODO, TODO),    # the red-haired still life stepping out
  ('because the backrooms copies people too', 's4_tree_b', TODO, TODO),  # her blank, misshapen face
  ('and fans call these copies', 's4_tree_a', TODO, TODO),  # still lifes standing in the dark
  ('two of them chase you', 's4_chase', TODO, TODO),      # the chase into a dead end
  ('and then you hear knocking', 's3_joblo_pullup', TODO, TODO),  # Clark at the wall, listening (the pool room)
  ("it's kat", 's3_joblo_pullup', TODO, TODO),            # Kat behind the glass (5:15-6:20)
  ('and from her side', 's3_joblo_pullup', TODO, TODO),   # through the window: Clark across the pool room
  ('but from yours', 's3_joblo_pullup', TODO, TODO),      # Clark facing a plain wall
  ('you set the camera down', 's3_joblo_pullup', TODO, TODO),  # the camera set down
  ('and something much taller', 's3_joblo_pullup', TODO, TODO),  # a tall figure behind Clark picks up the camera (Kat's view)
  ("you're down to fifteen", 's3_joblo_pullup', TODO, TODO),  # Kat screaming at the glass (the 15% lands)
  ('rule four', 's4_tree_a', TODO, TODO),                 # an empty dark level
  ('and nothing in here that looks', 's4_tree_b', TODO, TODO),  # a still life's face, close
  ], inserts=[ins('picks it up', 2.2, 'film', shots=[(0, 's3_joblo_pullup', TODO, 1.0, 'lufs=-17')], sub='Clark, behind you!')]))
# ---------------------------------------------------------------- s06 AFTER HIM (62.4 s) ----------------------------------------
X.append(sec('s06', [
  (0, 's3_joblo_pullup', TODO, TODO),          # the dropped camera / Clark's last shot as himself
  ("so from here on you're mary", 's5_mary_enters', TODO, TODO),  # Mary, close
  ('the house you grew up in', 's6_home', TODO, TODO),    # her childhood home (real or remembered)
  ('your mother ended up', 's6_home', TODO, TODO),        # her mother (flashback)
  ('and you still keep the chunk', 's5_mary_enters', TODO, TODO),  # the concrete with two handprints
  ('then clark leaves a message', 's5_mary_b', TODO, TODO),  # the phone / answering machine
  ('you go after him', 's5_mary_enters', TODO, TODO),     # Mary arrives at the store
  ('with no rope', 's5_mary_enters', TODO, TODO),         # Mary alone, nothing with her
  ('his store is unlocked', 's5_mary_enters', TODO, TODO),  # the unlocked door
  ('days of mail', 's5_mary_enters', TODO, TODO),         # mail covering the floor
  ('and his map is on a whiteboard', 's5_mary_enters', TODO, TODO),  # the whiteboard map in the basement
  ('and when a fly buzzes', 's5_mary_enters', TODO, TODO),  # the fly vanishing into the wall
  ('you follow it', 's5_mary_enters', TODO, TODO),        # Mary pushing through the wall
  ('inside a camera has been torn', 's5_mary_enters', TODO, TODO),  # the camera ripped off the wall
  ('chairs are piled', 's5_mary_enters', TODO, TODO),     # the barricade of chairs
  ('and someone has drawn a giant pirate', 's5_mary_enters', TODO, TODO),  # the mural: giant pirate lifting a tiny yellow figure
  ('clark steps out of hiding', 's5_mary_enters', TODO, TODO),  # Clark appears
  ("says you're too loud", 's5_mary_enters', TODO, TODO),  # Clark, hushed
  ('and tells you this is every place', 's5_mary_enters', TODO, TODO),  # Clark talking, eyes wide
  ('then something growls', 's5_mary_enters', TODO, TODO),  # Mary freezing, listening
  ('the lights flicker', 's5_mary_enters', TODO, TODO),   # flicker
  ('the lights go out', 's5_mary_enters', TODO, TODO),    # dark
  ('and clark chokes you', 's5_mary_enters', TODO, TODO),  # the choke, kept short
  ("telling you it's for your own good", 's5_mary_enters', TODO, TODO),  # fading, near-black
  ("you're down to ten", 's7_joblo_reveal', TODO, TODO),  # Mary unconscious / waking (the 10% lands)
  ('rule five', 's7_joblo_reveal', TODO, TODO),           # Clark's face
  ('might be the most dangerous', 's7_joblo_reveal', TODO, TODO),  # Clark looming
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do')]))
# ---------------------------------------------------------------- s07 YOUR OLD HOME (26.8 s) ------------------------------------
X.append(sec('s07', [
  (0, 's7_joblo_reveal', TODO, TODO),          # Mary out cold
  ('you dream of your mother', 's6_home', TODO, TODO),   # her mother wheeled away
  ('and of the house', 's6_home', TODO, TODO),           # the house
  ('and the backrooms builds it', 's6_home', TODO, TODO),  # the copied home inside the Backrooms
  ('then another below it', 's6_home', TODO, TODO),      # another level of the house
  ('each one more wrong', 's6_home', TODO, TODO),        # wrong details
  ('until the bottom one', 's6_home', TODO, TODO),       # the blank, barely-a-room copy
  ('because as clark puts it', 's7_joblo_reveal', TODO, TODO),  # Clark
  ('the more times this place', 's6_home', TODO, TODO),  # copies of copies
  ("you're down to seven", 's6_home', TODO, TODO),       # Mary in the copied home (the 7% lands)
  ('and rule six', 's6_home', TODO, TODO),               # the copied home
  ("you're already too deep", 's6_home', TODO, TODO),    # the deepest copy
  ]))
# ---------------------------------------------------------------- s08 THE DINING ROOM (61.4 s) ----------------------------------
X.append(sec('s08', [
  (0, 's7_joblo_reveal', TODO, TODO),          # Mary tied to a chair at the dinner table
  ('where the guests are still lifes', 's7_eat_them', TODO, TODO),  # the still-life guests around the table
  ('and clark loves them', 's7_eat_them', TODO, TODO),   # Clark smiling at them
  ("because they can't feel anything", 's7_eat_them', TODO, TODO),  # a blank still-life face
  ('he pushes a knife', 's7_eat_them', TODO, TODO),      # the knife going in - only the blank face, no wound close-up
  ("and it doesn't even blink", 's7_eat_them', TODO, TODO),  # the blank face
  ('they simply exist', 's7_joblo_reveal', TODO, TODO),  # Clark ("they simply exist")
  ('like furniture', 's7_eat_them', TODO, TODO),         # the table, wide
  ('and the best part', 's7_eat_them', TODO, TODO),      # Clark
  ('so he scoops out white stuffing', 's7_eat_them', TODO, TODO),  # the white stuffing served
  ("kat's head is in his fridge", 's7_eat_them', TODO, TODO),  # Mary's reaction or the CLOSED fridge - never the head
  ('and all he says', 's7_joblo_reveal', TODO, TODO),    # Clark, calm
  ('then he makes you play his wife', 's7_stay_char', TODO, TODO),  # the red wig, the role-play
  ('to relive the night', 's7_stay_char', TODO, TODO),   # Clark directing her
  ("and when you say you're not", 's7_stay_char', TODO, TODO),  # Mary
  ('so you tell him the truth', 's7_joblo_reveal', TODO, TODO),  # Mary's speech (0:48-1:53)
  ('that it was never the drinking', 's7_joblo_reveal', TODO, TODO),  # Mary
  ('and nothing is ever his fault', 's7_joblo_reveal', TODO, TODO),  # Clark taking it
  ("he says he doesn't want", 's7_joblo_reveal', TODO, TODO),  # Clark ("I like it in here" 2:21)
  ("right where he's supposed to be", 's7_joblo_reveal', TODO, TODO),  # Clark
  ('so you tell him to stay', 's7_joblo_reveal', TODO, TODO),  # Mary
  ('and he starts to untie you', 's7_joblo_reveal', TODO, TODO),  # the ropes
  ("you're down to five", 's7_joblo_reveal', TODO, TODO),  # Mary (the 5% lands)
  ('at a dinner party', 's7_eat_them', TODO, TODO),      # the table with the guests
  ('rule seven', 's7_joblo_reveal', TODO, TODO),         # Clark content at the table
  ("you're never leaving", 's7_joblo_reveal', TODO, TODO),  # Mary
  ('and then the red-haired woman', 's7_joblo_reveal', 204.0, -2.6),  # the red-wig still life in the corner by the cabinet (3:24-3:26.5)
  ('panics and runs', 's7_joblo_reveal', 206.4, -1.4),   # it turns and runs off (~3:27)
  ], inserts=[ins('he snaps', 1.9, 'film', shots=[(0, 's7_stay_char', TODO, 1.0, 'lufs=-17')], sub='Stay in character!'),
              ins('END', 0.85, 'hum', shots=[(0, 's7_joblo_reveal', 219.5, 1.0, 'a=-24')])]))   # the empty dark arch (3:39-3:49), room tone
# ---------------------------------------------------------------- s09 CAPTAIN CLARK (66.0 s) ------------------------------------
X.append(sec('s09', [
  (0, 's7_joblo_reveal', 230.4, -5.4),         # Captain Clark walks through the arch into the room (3:50-3:56)
  ('a copy of clark', 's7_joblo_reveal', TODO, TODO),   # Captain Clark full figure (4:07)
  ('towering and stretched', 's8_pack_a', TODO, TODO),  # its height, low angle
  ('dressed as the pirate', 's8_pack_a', TODO, TODO),   # the pirate hat and coat
  ('from his own tv commercial', 's1_commercial', TODO, TODO),  # the in-film commercial: Cap'n Clark at the helm
  ('peg leg and all', 's8_pack_b', TODO, TODO),         # the peg leg
  ('this is captain clark', 's8_pack_b', TODO, TODO),   # Captain Clark's face/hat, clearest shot
  ('and clark tries to calm it', 's7_joblo_reveal', TODO, TODO),  # Clark with hands up
  ('introducing you like a dinner guest', 's7_joblo_reveal', TODO, TODO),  # Clark gesturing at Mary
  ('he tells it', 's7_joblo_reveal', TODO, TODO),       # Clark talking up at it
  ('and that you said', 's7_joblo_reveal', TODO, TODO),  # Mary frozen
  ("because it's just the way", 's7_joblo_reveal', TODO, TODO),  # Captain Clark looming
  ("and that's when captain clark", 's7_joblo_reveal', TODO, TODO),  # it lifts Clark - cut before the bite
  ('and bites into him', 's7_joblo_reveal', TODO, TODO),  # Mary's scream (4:47), not the bite
  ('you tear free and run', 's8_joblo_fight', TODO, TODO),  # Mary breaking free, running
  ('and it hobbles after you', 's8_chase_b', TODO, TODO),  # Captain Clark hobbling after her
  ('through a street of fake apartments', 's8_chase_a', TODO, TODO),  # the fake apartment street
  ('a room full of couches', 's8_chase_c', TODO, TODO),  # the couch room
  ('and a hall with a locked door', 's8_chase_d', TODO, TODO),  # a locked door, Mary pulling at it
  ('so you crawl through a doggy door', 's8_chase_e', TODO, TODO),  # the doggy door
  ('into the biggest space', 's8_joblo_fight', TODO, TODO),  # the Escher space
  ('endless floors around a giant drop', 's8_joblo_fight', TODO, TODO),  # wide, the drop
  ('with a staircase floating', 's8_joblo_fight', TODO, TODO),  # the floating staircase
  ('another door brings you up', 's8_joblo_fight', TODO, TODO),  # the door in the floor
  ("of clark's store", 's8_joblo_fight', TODO, TODO),    # the copied store
  ("except it's the copy", 's8_joblo_fight', TODO, TODO),  # wrong details in the store
  ('ringed with gas canisters', 's8_joblo_fight', TODO, TODO),  # the gas canisters
  ('and its door opens onto a wall', 's8_joblo_fight', TODO, TODO),  # the door opening onto a wall
  ('with nowhere left to run', 's8_joblo_fight', TODO, TODO),  # Mary cornered
  ('you snap its peg leg', 's8_joblo_fight', TODO, TODO),  # the hat rack swing
  ('knock over a cutout', 's8_joblo_fight', TODO, TODO),  # the cutout falls, gas hissing
  ("and when it's right on top of you", 's8_joblo_fight', TODO, TODO),  # Captain Clark over her
  ('you smash its face', 's8_joblo_fight', TODO, TODO),  # the concrete swing - cut on the hit
  ('until the concrete breaks', 's8_joblo_fight', TODO, TODO),  # the concrete breaking
  ("you're down to two", 's8_joblo_fight', TODO, TODO),  # Mary, spent (the 2% lands)
  ('and rule eight is the simplest', 's8_joblo_fight', TODO, TODO),  # Mary in the gas
  ("when you can't run", 's8_joblo_fight', TODO, TODO),  # Mary's face (4:08 smoky store)
  ], inserts=[ins(0, 0.4, 'thud', shots=[(0, 's7_joblo_reveal', 229.9, 1.0, 'a=-16')]),   # the first heavy step at the arch
              ins('dinner guest', 2.4, 'film', shots=[(0, 's7_joblo_reveal', 244.6, 1.0, 'lufs=-17')], sub="This is Mary. She's our therapist.")]))  # ~4:05, verify words and times
# ---------------------------------------------------------------- s10 ASYNC (58.0 s) --------------------------------------------
X.append(sec('s10', [
  (0, 's8_joblo_fight', TODO, TODO),           # hazmat men walking out of the gas (7:04)
  ('and more gas knocks you out', 'end_extract', TODO, TODO),  # Mary collapsing in the gas
  ('you wake up at async', 'end_extract', TODO, TODO),   # the Async facility (blue light)
  ('where they scan your body', 'end_b', TODO, TODO),    # the scan
  ('and down the hall captain clark', 'end_b', TODO, TODO),  # Captain Clark on a table
  ('his pirate hat part of his own body', 'end_b', TODO, TODO),  # the hat close
  ('and behind another door', 'end_b', TODO, TODO),      # a door opening
  ('is a room full of cardboard cavemen', 'end_b', TODO, TODO),  # the cavemen room
  ('so that hello and welcome', 'end_b', TODO, TODO),    # a caveman cutout close
  ('came from async all along', 'end_b', TODO, TODO),    # Async corridor
  ('phil the man who watched', 'end_joblo_phil', TODO, TODO),  # Phil (3:08)
  ('tells you his company', 'end_joblo_phil', TODO, TODO),  # Phil talking
  ('until it found this place', 'end_joblo_phil', TODO, TODO),  # Mary listening
  ('that he goes in every day', 'end_joblo_phil', TODO, TODO),  # Phil
  ('and that doors are opening everywhere', 'end_joblo_phil', TODO, TODO),  # Phil (4:23)
  ("so you ask if they'll let you go", 'end_joblo_phil', TODO, TODO),  # Mary asking
  ('and inside the backrooms', 'end_joblo_phil', TODO, TODO),  # ending montage (4:44-6:00)
  ('your house', 'end_mary_still', TODO, TODO),          # copy of Mary's house
  ('a bookstore with your book', 'end_mary_still', TODO, TODO),  # the bookstore
  ('missing posters for kat', 'end_joblo_phil', TODO, TODO),  # the MISSING poster (4:41)
  ('the strip mall', 'end_mary_still', TODO, TODO),      # the strip mall with Clark's store
  ('and finally a copy of the room', 'end_mary_still', TODO, TODO),  # the copied interrogation room
  ('with a copy of you', 'end_mary_still', TODO, TODO),  # Mary's still life sitting perfectly still
  ('five people walked in', 's1_joblo_first', TODO, TODO),  # empty yellow hall
  ('one walked out', 'end_joblo_phil', TODO, TODO),      # Mary
  ('and even she never got', 'end_joblo_phil', TODO, TODO),  # Mary in the room
  ('one out of five', 's1_joblo_first', TODO, TODO),     # a wide empty yellow room under the 1 OF 5 card
  ], inserts=[ins("let you go", 2.0, 'film', shots=[(0, 'end_joblo_phil', 241.0, 1.0, 'lufs=-17')], sub="That decision's not up to me.")],  # ~4:01, verify
  pad=0.9))
# ---------------------------------------------------------------- s11 outro (35.5 s) --------------------------------------------
X.append(sec('s11', [
  (0, 'op_joblo_1990', TODO, TODO, T4),        # the 1990 tape again
  ('naren died on june', 'op_joblo_1990', TODO, TODO, T4),  # Naren
  ('and clark found the door', 's1_a24_clip', TODO, TODO),  # Clark at the slit
  ('ten days later', 's1_joblo_first', TODO, TODO),      # Clark entering
  ('the movie never says it', 'op_joblo_1990', TODO, TODO, T4),  # the black silhouette in the doorway (5:12.2-5:12.7), slowed
  ('but the only giant', 'op_joblo_1990', TODO, TODO, T4),  # the doorway, the figure's legs
  ('is captain clark', 's7_joblo_reveal', TODO, TODO),   # Captain Clark in the arch (3:51-3:56)
  ('so the backrooms had already made', 's8_pack_a', TODO, TODO),  # Captain Clark looming
  ('before he ever walked in', 's1_joblo_first', TODO, TODO),  # Clark walking in for the first time
  ("it doesn't wait for you", 's1_a24_clip', TODO, TODO),  # the slit glowing
  ("because it's already started on you", 's1_joblo_first', TODO, TODO),  # empty yellow hall, slow push
  ('so how long would you have lasted', 's1_joblo_first', TODO, TODO),  # yellow rooms
  ('and which stage', 's8_chase_a', TODO, TODO),         # Mary running
  ('tell me in the comments', 's1_joblo_first', TODO, TODO),  # calm wide yellow room
  ('subscribe so you', 's1_joblo_first', TODO, TODO),    # calm yellow room (subscribe button on screen)
  ('and if you ever see a line of light', 's1_a24_clip', TODO, TODO),  # the store at night, the glowing slit
  ('leave it alone', 's1_a24_clip', TODO, TODO),         # the slit, hold to the end
  ], extra=[('date', ['JUNE 19, 1990'], 'june nineteenth', 'and clark found'),
            ('date', ['JUNE 29, 1990'], 'june twenty-ninth', 'ten days later'),
            ('date', ['JUNE 29, 1990', '!10 DAYS LATER'], 'ten days later', 'the movie never says'),
            ('png', 'tiles/subscribe.png', 'subscribe so you', 'and if you ever')],
  pad=2.0))
