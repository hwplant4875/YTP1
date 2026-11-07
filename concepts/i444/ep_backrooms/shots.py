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
  (0, 'film', 3141.65, -8.00, 'z=1.333'),  # FRAME 0: Kat and Bobby big and bright in the yellow room, rope on Bobby's belt
  ('went into', 'film', 2780.30, -1.00, 'z=1.333,a=-18'),  # Clark leans into the taped store wall and sinks into it (eerie swoosh)
  ('the backrooms', 'film', 1749.30, -3.40),  # bright empty HD yellow room, fluorescent ceiling, nobody in it
  ('in this movie', 'film', 5396.60, -2.80),  # the Escher drop: endless floors of shelving around the pit
  ('and they got', 'film', 2970.45, -1.90, 'z=1.333'),  # Kat and Clark together with the rope in the yellow room
  ('chased', 'film', 5566.15, -2.70, 'a=-18'),  # Captain Clark right behind Mary through the store furniture
  ('dragged', 'film', 3150.90, -2.30, 'z=1.333'),  # Bobby yanked toward the hole on the rope, Kat grabbing him (no body)
  ('lost', 'film', 1687.00, -6.50),  # Clark tiny and alone among the pillars of the endless rooms
  ('eaten', 'film', 5261.80, -0.85, 'a=-20'),  # v3 QA: Captain Clark's mouth at Clark's neck, Clark screaming, lit (no wound, before the lift)
  ('only one of them', 'film', 5309.15, -2.10),  # Mary alone in front of a white door, bright
  ('made it back out', 'film', 5713.30, -2.60, 'a=-18'),  # Mary bursts out of the wall through the hazmat spray and hits the floor
  ("now it's your turn", 'film', 2791.70, -2.20, 'z=1.333'),  # first-person: a hand reaches out and presses the wall where Clark vanished
  ('and how long', 'film', 2843.00, -6.50, 'z=1.333'),  # VHS POV pushing through the furniture-filled yellow rooms
  ('would you survive', 'film', 5655.50, -0.75, 'a=-18'),  # Captain Clark's face close and bright under the hat, growling
  ('in the backrooms', 'film', 1744.75, -3.85),  # empty HD yellow room, dark doorway with in-world stop sign, hold
  ], extra=[('cap', w, a, b) for w, a, b in [
    ('Five people', 0, 'went into'), ('Went into', 'went into', 'the backrooms'), ('The Backrooms', 'the backrooms', 'in this movie'),
    ('In this movie', 'in this movie', 'and they got'), ('And they got', 'and they got', 'chased'), ('Chased', 'chased', 'dragged'),
    ('Dragged', 'dragged', 'lost'), ('Lost', 'lost', 'eaten'), ('Eaten', 'eaten', 'only one of them'), ('Only one of them', 'only one of them', 'made it back out'),
    ('Made it back out', 'made it back out', "now it's your turn"), ("Now it's your turn", "now it's your turn", 'and how long'),
    ('And how long', 'and how long', 'would you survive'), ('Would you survive', 'would you survive', 'in the backrooms'),
    ('In the Backrooms?', 'in the backrooms', 999)]], clip_db=-22))
for ov in X[-1]['overlays']:   # QA fix: snap each caption to the cut's frame (it lagged one frame at 7 cuts)
    if ov[0] == 'cap':
        ov[2] = max(0.0, round(ov[2] * 30) / 30 - 0.005) if ov[2] > 0 else 0.0
        if ov[3] < 900: ov[3] = round(ov[3] * 30) / 30 - 0.005
# ---------------------------------------------------------------- s01 the 1990 tape (35.4 s) ------------------------------------
X.append(sec('s01', [
  (0, 'film', 73.50, -6.00, 'z=1.333'),  # tape POV: wall on the left, empty yellow rooms beyond
  ('naren a researcher', 'film', 89.60, -3.50, 'z=1.333'),  # Naren's black bag, then his yellow hazmat glove
  ('has lost his team', 'film', 95.00, -5.00, 'z=1.333'),  # camera turning through empty rooms, alone
  ("and he's on the radio", 'film', 178.30, -5.00, 'z=1.333'),  # the radio set, ball mic, amber dial
  ('nobody answers', 'film', 193.00, -3.00, 'z=1.333'),  # radio and floppy disks on the desk, nothing happening
  ('down the hall a door', 'film', 349.60, -2.60, 'z=1.333,a=-18'),  # long yellow corridor, dark doorway at the end; the film's door creak at 351.0
  ('something huge steps out', 'film', 356.30, -1.90, 'z=1.333,a=-18'),  # same corridor, the dark doorway, distant rasping breath at 356.7
  ('steps out', 'film', 357.65, -0.85, 'z=4,dx=30,dy=-115,a=-18'),  # NEW CUT  zoom: the dark figure standing in the lit doorway at the end of the hall
  ('and naren runs', 'film', 361.00, -3.40, 'z=1.333'),  # camera running down the yellow corridor
  ('a room covered in', 'film', 375.10, -2.45, 'z=1.333'),  # the dead end: beach/sky photo-mural room, yellow door
  ('and the moment he runs back', 'film', 381.95, -1.95, 'z=1.333'),  # hand on the locked door's handle, whip back to the mural doorway
  ('he runs straight into it', 'film', 383.90, -1.75, 'z=1.333,a=-18'),  # rushing the doorway, the giant's black legs fill it at 385.2, camera drops
  ('he had training', 'film', 387.40, -5.00, 'z=1.333,a=-20'),  # the dropped camera lying still, mural ceiling, distorted screams
  ("and he still didn't", 'film', 396.60, -2.30, 'g=1.25'),  # NEW CUT: CRT in the dark showing blue, then static (16:9, no z)
  ('and you have none of that', 'film', 1498.80, -1.60, 'g=1.3'),  # Clark close, alone in his dark store
  ('the number in the corner', 'film', 1557.40, -6.39),  # Clark on all fours in the empty yellow room, furniture behind (later in the same take, after s02's 1555.80-1557.25)
  ('and in here', 'film', 1574.60, -6.40),  # Clark from behind walking into the endless yellow room
  ], inserts=[ins('come and get him', 1.41, 'film', shots=[(0, 'film', 202.99, 1.0, 'z=1.333,lufs=-17')], sub="There's something else in here.")],
  extra=[('date', ['JUNE 19, 1990'], 'dated june nineteenth', 'naren a researcher')]))
# ---------------------------------------------------------------- s02 THE SLIT (74.2 s) -----------------------------------------
X.append(sec('s02', [
  ('that shouldn\'t exist', 'film', 1040.48, -1.85),  # NEW CUT  a finger points at the breakers that shouldn't be there
  ('that shouldn\'t exist', 'film', 1040.48, -1.85),  # NEW CUT  a finger points at the breakers that shouldn't be there
  (0, 'film', 839.30, -1.50, 'z=1.333'),  # the store commercial: Cap'n Clark at the ship's wheel (4:3 tape)
  ('a failed architect', 'film', 1441.30, -3.90),  # Clark close, tired, store lamps behind
  ('who sleeps in the back', 'film', 1236.00, -5.00, 'g=1.25'),  # wide: Clark in a display bed on the dark store floor
  ('the lights flicker', 'film', 1211.55, -1.80, 'a=-18'),  # Clark in the dim store, the fluorescents stutter on above him at 1211.97-1212.7
  ('there are two breakers', 'film', 1033.45, -2.45),  # close: the breaker box with the odd extra breakers
  ('that shouldn\'t exist', 'film', 1040.48, -1.85),  # NEW CUT  a finger points at the breakers that shouldn't be there
  ('and one night the tv', 'film', 1410.60, -2.90, 'g=1.25'),  # the store TV in the dark: ad -> static -> yellow security feed
  ('with a figure standing', 'film', 1419.05, -1.50, 'g=1.25'),  # the TV close: yellow feed, small figure in the doorway
  ('in a doorway', 'film', 1413.55, -1.20, 'g=1.25'),  # NEW CUT  wider: the TV holding on the feed with the figure
  ('you flip the strange breakers', 'film', 1456.00, -5.90),  # close: his hands flipping the strange breakers
  ('the store goes dark', 'film', 1478.00, -3.00, 'g=1.5'),  # the whole store black, Clark a small silhouette
  ('and there it is', 'film', 1490.40, -4.20, 'g=1.4'),  # Clark in the dark turning toward the glow
  ('a thin line of light', 'film', 1514.20, -5.20, 'g=1.75'),  # the slit: thin vertical line of light glowing in the bare wall
  ('you lean on it', 'film', 1543.20, -2.40, 'g=1.5,a=-18'),  # Clark's silhouette, hands flat on the wall (swoosh + gasp)
  ('fall straight through', 'film', 1545.80, -3.00, 'a=-18'),  # Clark tumbles onto the yellow carpet
  ('into an empty yellow room', 'film', 1555.80, -2.50),  # Clark on all fours in the huge empty yellow room
  ('of melted furniture', 'film', 1646.00, -3.00),  # the fused heap of furniture, Clark small beside it
  ('and since you can step', 'film', 1606.90, -2.40, 'g=1.4'),  # Clark back out in the dark store, at the wall
  ('you explore', 'film', 1573.50, -1.50),  # Clark gets up and walks off into the yellow room
  ("there's a backwards stop sign", 'film', 1745.95, -6.72),  # the mirrored STOP sign in the dark doorway (same pan, after s00's 1744.75-1745.80, before s00's 1749.30)
  ('a dead bird', 'film', 2096.10, -2.20),  # the green parrot dead on the carpet, Clark's legs, throne behind
  ('and a voice saying hello', 'film', 1787.00, -2.60),  # Clark stops and listens as the greetings start
  ('in dozens of languages', 'film', 1823.00, -2.00),  # Clark close, turning to follow the voices
  ('coming from a cardboard caveman', 'film', 1868.90, -3.20),  # the cardboard caveman, tape recorder on its chest
  ('behind a fake tile', 'film', 1981.00, -1.60, 'g=1.25'),  # the panel open in the dark wall, Naren's bag in the light behind
  ("naren's bag full of tapes", 'film', 2001.05, -2.20),  # top-down: Clark opens Naren's duffel full of tapes and disks
  ('and further in', 'film', 2044.00, -1.50),  # down the tunnel into the next room: shoes on the floor, chair far off
  ('the chair from your own', 'film', 2099.60, -2.50),  # Clark walks up to the purple throne
  ('slightly wrong', 'film', 2104.20, -1.40),  # the throne close, Clark's hand on it
  ('with shoes sticking out', 'film', 2082.50, -2.20),  # the shoes sticking up out of the carpet, chair behind
  ('then the thuds start', 'film', 2135.00, -2.00, 'a=-16'),  # wide: Clark tiny in the room, the rhythmic thudding begins
  ('the caveman flies', 'film', 2189.30, -1.40, 'z=3.5,dy=-40,a=-14'),  # zoom down the tunnel: crash 2189.8, the cardboard caveman flies across the opening 2190.2-2190.6
  ('and smashes to pieces', 'film', 2190.80, -2.20, 'z=1.4,a=-14'),  # NEW CUT  Clark in the room, turning toward the crash (clatter 2191.0)
  ('and you squeeze through', 'film', 2216.00, -2.30),  # Clark on hands and knees forcing into the tiny door
  ('and run until', 'film', 2244.30, -1.50),  # Clark running at camera
  ('back in your store', 'film', 2295.60, -3.20, 'g=1.4'),  # dark store, Clark holding the stool up like a weapon
  ('a camera in there', 'film', 2377.60, -2.10),  # the monitor playing the Backrooms security camera feed
  ('on a tape dated', 'film', 2385.00, -2.50),  # same monitor: in-world overlay 06/29/1990, Clark walking in the feed
  ('one trip through that wall', 'film', 1495.50, -2.20, 'g=1.75'),  # the slit glowing in the dark wall (second shot)
  ('gives you a ninety', 'film', 2318.00, -2.60, 'g=1.4'),  # Clark close in the dark store after he gets back
  ('the best it will ever be', 'film', 1750.05, -2.62),  # bright empty yellow rooms (end of the same pan, after s00's 1749.30-1749.86)
  ('rule one', 'film', 2109.45, -2.45),  # wide: Clark beside the wrong copy of his chair
  ('if you see a copy', 'film', 2105.80, -2.50),  # NEW CUT  low close: Clark's hands on the copy of his commercial throne
  ('leave', 'film', 2204.30, -2.40),  # Clark running away down the slanted room toward the tiny door
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do')],
  extra=[('date', ['JUNE 29, 1990'], 'dated june twenty-ninth', 'one trip through that wall')]))
# ---------------------------------------------------------------- s03 THE MAP (39.6 s) ------------------------------------------
X.append(sec('s03', [
  (0, 'film', 1621.30, -3.20, 'g=1.4'),  # Clark at the dark store wall, his hand rising toward it
  ('so what do you do', 'film', 1528.30, -1.80, 'g=1.4'),  # Clark's silhouette facing the wall
  ('you go back every night', 'film', 1810.00, -3.60),  # Clark walking alone into the endless yellow rooms
  ('and you start drawing a map', 'film', 2579.25, -2.10),  # Clark unfolds his hand-drawn maze map on the table
  ('you ask your therapist mary', 'film', 2420.60, -2.80),  # Mary in her armchair, the therapy room
  ("if she's ever had someone committed", 'film', 2442.75, -2.55),  # Clark asking "You ever 5150'd someone?"
  ('then tell her the store', 'film', 2496.10, -5.60),  # Clark explaining with his hands ("the store just keeps going")
  ('close but wrong', 'film', 2501.95, -4.10),  # Mary's face, not following
  ('like a dog drawn by someone', 'film', 2521.90, -5.40),  # Clark gesturing through the dog analogy (no dog drawing exists)
  ('and your map is a maze', 'film', 2584.30, -2.60),  # the maze map on the table, Clark slides it to Mary
  ('that goes on and on', 'film', 2591.20, -4.10),  # Mary holding the maze map open on her lap
  ("she doesn't believe you", 'film', 2606.00, -3.60),  # Mary with the map, unconvinced
  ('so you swear', 'film', 2616.50, -2.40),  # Clark in the chair cutting her off, then jumping to his feet
  ('that drops you to seventy', 'film', 1720.00, -2.20),  # Clark small and alone walking through the rooms
  ('because a trained scientist', 'film', 208.00, -3.60, 'z=1.333'),  # Naren's radio, amber VU dials (1990 tape)
  ('and you keep going in alone', 'film', 1840.00, -2.30),  # Clark walking alone down a long corridor
  ('rule two', 'film', 1502.20, -2.60, 'g=1.75'),  # the slit glowing in the dark wall
  ('because this place only has to win once', 'film', 1695.00, -3.00, 'g=1.25'),  # slow drift into dimmer empty rooms
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('and on and on', 2.12, 'film', shots=[(0, 'film', 2586.99, 1.0, 'lufs=-17')], sub="Sometimes I'm scared I'll get lost.")]))
# ---------------------------------------------------------------- s04 THE LAUNDRY ROOM (47.0 s) ---------------------------------
X.append(sec('s04', [
  (0, 'film', 2708.00, -3.30),  # Clark at the shop door facing Kat and Bobby, the two he brings
  ('your assistant manager kat', 'film', 2769.40, -1.70, 'z=1.333'),  # Kat close in the store, wide-eyed
  ('and her boyfriend bobby', 'film', 2716.80, -1.60, 'z=1.333'),  # Bobby filming himself in the store mirror, white T-shirt
  ('and you lead them', 'film', 2837.00, -1.20, 'z=1.333'),  # Clark walking ahead into the yellow rooms, Bobby filming him
  ('a steep ramp down', 'film', 2930.30, -3.30, 'z=1.333'),  # the long steep ramp, looking straight down it
  ('bobby volunteers', 'film', 3143.00, -7.04, 'z=1.333'),  # Bobby with the rope tied at his waist, Kat holding him (after the INS line and s00's 3141.65-3142.22)
  ('you tie a rope', 'film', 2921.00, -2.30, 'z=1.333'),  # hands knotting the rope at the bed
  ('and he jokes', 'film', 2718.40, -1.92, 'z=1.333'),  # Bobby in his white T filming himself in the store mirror, clowning
  ("you'll tell his mom", 'film', 2720.35, -1.70, 'z=1.333'),  # NEW CUT  Bobby in the mirror waving at the camera, "hi mom"
  ('down there is a basement', 'film', 3017.00, -3.10, 'z=1.333,g=1.25'),  # the basement: piles of laundry under small lit windows
  ('with a t-shirt bobby', 'film', 3057.40, -2.95, 'z=1.333,g=1.25'),  # his T-shirt surfacing in the pile
  ('a room turned on its side', 'film', 3074.00, -2.10, 'z=1.333'),  # the tilted room rolling: floor as a wall, windows sideways
  ('a cardboard caveman torn in half', 'film', 3087.00, -2.55, 'z=1.7,dx=90,dy=-160,g=1.25'),  # the torn cardboard caveman lying on the laundry pile
  ('and when a light flickers', 'film', 3130.40, -1.60, 'z=1.333,g=1.25'),  # the light flashing on and off in the black ramp
  ('bobby sees something', 'film', 3113.20, -2.25, 'z=1.6,dx=-90,dy=-40,g=1.3,a=-18'),  # zoom on the black doorway: a figure shows in it 3114.5-3115.2 (creak, gasp)
  ('you pull', 'film', 3154.90, -1.10, 'z=1.333'),  # Clark and Kat bracing at the hole, hauling on the rope
  ('but something pulls harder', 'film', 3152.15, -1.64, 'z=1.333'),  # the rope drags Bobby back toward the hole, Kat clinging to him (right after s00's "Dragged" 3150.90-3152.01)
  ('dragging the bed', 'film', 3175.10, -2.60, 'z=1.333'),  # Kat and Clark at the hole, then the bed-mounted camera lurches toward it
  ('just in time to see bobby', 'film', 3186.50, -3.10, 'z=1.333'),  # from the floor: Bobby's legs dragged out through the far door (no body)
  ('leaving a long trail of blood', 'film', 3192.20, -2.30, 'z=1.333'),  # the red smear across the laundry-room floor (no body)
  ("you're down to forty", 'film', 3168.60, -1.90, 'z=1.333'),  # Kat and Clark on their knees at the hole, Bobby gone
  ('rule three', 'film', 2974.00, -2.80, 'z=1.333'),  # POV going down the steep ramp into the dark
  ('and if your clothes got there', 'film', 3060.40, -2.20, 'z=1.333,g=1.25'),  # the T-shirt held up, close
  ("you're already too late", 'film', 3194.60, -1.80, 'z=1.333'),  # NEW CUT  the blood trail across the floor
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('standing in the dark', 1.65, 'film', shots=[(0, 'film', 3139.10, 1.0, 'z=1.333,lufs=-21')], sub="There's someone down there.")]))
# ---------------------------------------------------------------- s05 THE STILL LIFES (44.1 s) ----------------------------------
X.append(sec('s05', [
  (0, 'film', 3231.50, -1.80, 'z=1.333'),  # POV running through the white rooms past the toppled rack
  ('and lose each other', 'film', 3242.20, -1.40, 'z=1.333,g=1.25'),  # dim cluttered level, nobody there
  ('while something heavy thuds', 'film', 3256.50, -2.55, 'z=1.333,g=1.25,a=-18'),  # POV swings to a dark doorway as the heavy thud lands
  ('room after room', 'film', 3285.80, -2.00, 'z=1.333'),  # running through empty yellow room after room
  ('until you stumble into a dark room', 'film', 3293.60, -2.20, 'z=1.333'),  # a hand pushes the white door open into blackness
  ('lit only by a glowing christmas tree', 'film', 3302.00, -2.70, 'z=1.333'),  # the lone lit Christmas tree in the dark room, slow approach
  ('with people fused into the floor', 'film', 3317.10, -2.50, 'z=1.333,g=1.4'),  # a person sunk into the carpet, head and arms out
  ('a half-man in a wheelchair', 'film', 3346.00, -2.80, 'z=1.333,g=1.25'),  # the lamp clicks on beside the half-man in the wheelchair
  ('and a red-haired woman', 'film', 3348.80, -2.60, 'z=1.333'),  # the red-haired still life comes into the lamplight
  ('steps out of the dark', 'film', 3351.40, -1.40, 'z=1.333'),  # NEW CUT  she steps forward and lunges at the camera
  ('because the backrooms copies people too', 'film', 3338.00, -2.60, 'z=1.333,g=1.4'),  # still-life silhouettes standing beside the tree
  ('and fans call these copies', 'film', 4558.30, -1.90),  # a still life's misshapen face, clear: the bearded guest
  ('still lifes', 'film', 4560.45, -2.30),  # NEW CUT  the red-haired woman's twisted, stitched face, clear
  ('two of them chase you', 'film', 3362.50, -2.20, 'z=1.333'),  # fleeing down dim halls into the green-lit corridor
  ('and then you hear knocking', 'film', 3408.60, -2.00, 'z=1.333,g=1.25,a=-18'),  # the pool annex, camera swings round at the knock on the wall
  ("it's kat", 'film', 2860.00, -1.00, 'z=1.333'),  # Kat's frightened face looking up (yellow rooms)
  ('and from her side', 'film', 3433.00, -2.60, 'z=1.333'),  # across the pool room: Clark small at the far wall
  ('but from yours', 'film', 3452.00, -2.40, 'z=1.333'),  # Clark at the plain wall, palm on it
  ('you set the camera down', 'film', 3421.85, -1.95, 'z=1.333'),  # the camera settles on the floor facing the empty pool room
  ('and something much taller', 'film', 3461.60, -2.60, 'z=1.333,g=1.5'),  # Clark small at the far wall, a huge dark leg sweeps past the lens, the camera is lifted and tilts
  ("you're down to fifteen", 'film', 2943.20, -2.10, 'z=1.333'),  # Kat terrified, close
  ('rule four', 'film', 3437.50, -2.50, 'z=1.333'),  # Clark alone, tiny, at the far wall of the pool room
  ('and nothing in here that looks', 'film', 4501.70, -2.51),  # the bearded still life sitting at the set table like a man, Clark bringing plates behind
  ('is one', 'film', 4593.25, -2.08),  # NEW CUT  the half-man in the wheelchair with his lamp, clear (later in s08's take, after 4592.20-4593.11)
  ], inserts=[ins('picks it up', 1.55, 'film', shots=[(0, 'film', 3472.88, 1.0, 'z=1.333,lufs=-17')], sub='Clark, behind you!')]))
# ---------------------------------------------------------------- s06 AFTER HIM (62.4 s) ----------------------------------------
X.append(sec('s06', [
  (0, 'film', 3424.40, -2.95, 'z=1.333'),  # from the set-down camera: Clark walks away across the pool room, his last shot as himself
  ("so from here on you're mary", 'film', 3820.00, -3.30),  # Mary close at the store window
  ('the house you grew up in', 'film', 3504.50, -2.40),  # Mary's childhood home, the cluttered living room
  ('your mother ended up', 'film', 4374.00, -2.40),  # her mother in the hospital ward with the nurse
  ('and you still keep the chunk', 'film', 3625.00, -4.40),  # hands turning the concrete chunk with the two handprints
  ('then clark leaves a message', 'film', 3668.20, -4.50),  # the answering machine on the desk, his message playing
  ('you go after him', 'film', 3704.00, -3.20),  # Mary driving out alone
  ('with no rope', 'film', 3851.60, -3.10),  # Mary walking alone through the empty store, nothing in her hands
  ('his store is unlocked', 'film', 3799.00, -1.70),  # Mary at the shop's glass door, pulling it open
  ('days of mail', 'film', 3796.20, -1.90),  # the pile of mail on the floor at her feet
  ('and his map is on a whiteboard', 'film', 3923.95, -1.80),  # the whiteboard map, close
  ('in the basement', 'film', 3904.00, -1.30),  # NEW CUT  Mary standing in the dark shop basement
  ('and when a fly buzzes', 'film', 3963.70, -2.90, 'a=-18'),  # the wall with the tape outline, the fly on it; the buzzing stops
  ('you follow it', 'film', 3976.70, -1.00),  # Mary's hand reaching into the wall
  ('inside a camera has been torn', 'film', 4110.90, -2.64, 'z=3.5,dx=690,dy=-125'),  # zoom: the security camera torn off, hanging by its wire on the wall
  ('chairs are piled', 'film', 4113.60, -2.30, 'z=1.3,dx=250,dy=100'),  # chairs, desks and cabinets piled into a barricade
  ('and someone has drawn a giant pirate', 'film', 4174.00, -2.50),  # the giant pirate mural filling the far wall
  ('lifting a tiny yellow figure', 'film', 4204.40, -2.10),  # the pirate close, lifting the tiny yellow figure
  ('clark steps out of hiding', 'film', 4254.00, -1.60),  # Clark steps out at the end of the yellow hall
  ("says you're too loud", 'film', 4260.00, -1.45),  # Mary at the mural, staring at him
  ('and tells you this is every place', 'film', 4264.40, -3.35),  # Clark standing in the hall, talking to her
  ('then something growls', 'film', 4286.10, -1.72),  # Mary gasps at the growl
  ('the lights flicker', 'film', 4315.00, -1.20, 'z=3.2,dy=-30,a=-18'),  # zoom on the far lit corridor, its light flickering (thuds peak)
  ('the sound stops', 'film', 4316.55, -1.20, 'z=2.6,dy=-30,a=-18'),  # the hall: the flicker and the thudding stop dead at 4317.0
  ('the lights go out', 'film', 4321.80, -1.10, 'z=3.2,dy=-30,a=-18'),  # zoom on the far corridor: its light clicks off at 4322.1
  ('and clark chokes you', 'film', 4327.20, -0.70),  # wide, Clark grabs Mary from behind (short)
  ('chokes you', 'film', 4329.00, -2.55),  # close, the choke, her face (kept short)
  ("telling you it's for your own good", 'film', 4340.00, -2.15),  # her view of the ceiling light as she goes under
  ("you're down to ten", 's7_joblo_reveal', 109.50, -2.00),  # Mary close, worn out (unchanged)
  ('rule five', 's7_joblo_reveal', 123.00, -2.60),  # Clark's face, close (unchanged)
  ('might be the most dangerous', 's7_joblo_reveal', 192.00, -3.00),  # Clark with the knife, standing over Mary tied to her chair (unchanged)
  ], inserts=[ins('in there for good', 2.38, 'film', shots=[(0, 'film', 3675.29, 1.0, 'lufs=-17')], sub="I won't be coming back."),
              ins('so what do you do', 0.9, 'choice', q='so what do you do')]))
# ---------------------------------------------------------------- s07 YOUR OLD HOME (26.8 s) ------------------------------------
X.append(sec('s07', [
  (0, 'film', 4474.00, -1.20),  # Mary out cold, head lolling, eyes shut
  ('you dream of your mother', 'film', 4384.00, -2.55),  # the nurse wheeling her mother away down the hospital ward
  ('and of the house', 'film', 4395.40, -1.90),  # young Mary sitting in the cluttered house she grew up in
  ('and the backrooms builds it', 'film', 4400.40, -3.35),  # the copied home, top level, cluttered, sun through the window
  ('then another below it', 'film', 4413.50, -1.75),  # copy 2: same room, sparser
  ('each one more wrong', 'film', 4427.80, -2.55),  # copy 3: things askew, scraps on the floor
  ('until the bottom one', 'film', 4440.80, -2.80),  # blank box, one ceiling light
  ('because as clark puts it', 'film', 4568.40, -2.10),  # Clark at the table explaining with his hands
  ('the more times this place', 'film', 4435.00, -4.00),  # a copy of a copy: bare walls, scraps on the floor
  ("you're down to seven", 'film', 4446.00, -2.05),  # a copy with only tape outlines left on the floor
  ('and rule six', 'film', 4416.00, -3.40),  # the copied home with the sun through the window
  ("you're already too deep", 'film', 4459.60, -1.95),  # the deepest copy: bare room, one dark arched doorway
  ]))
# ---------------------------------------------------------------- s08 THE DINING ROOM (61.4 s) ----------------------------------
X.append(sec('s08', [
  (0, 'film', 4477.50, -3.00),  # Mary comes to, head lolling, at the dinner table
  ('where the guests are still lifes', 'film', 4499.50, -2.30),  # bearded still life sits blank at the set table, Clark coming with plates
  ('and clark loves them', 'film', 4688.00, -1.60),  # Clark cheek to cheek with the still life, laughing
  ("because they can't feel anything", 'film', 4588.90, -2.10),  # the bearded still life's blank face, close
  ('he pushes a knife', 'film', 4634.00, -1.50),  # close: Clark's knife at the bearded still life's neck
  ("one guest's neck", 'film', 4638.50, -1.10),  # NEW CUT  wide: Clark pushes the knife into its neck, it sits unmoved
  ("and it doesn't even blink", 'film', 4639.70, -1.60, 'z=2.2,dx=-625,dy=10'),  # zoom: its blank face, knife in the neck (blank face only)
  ('they simply exist', 'film', 4658.60, -2.40),  # Clark close: "They simply... exist"
  ('like furniture', 'film', 4592.20, -1.10),  # the wheelchair still life under its lamp
  ('and the best part', 'film', 4671.10, -2.50),  # Clark's grin: "You can eat them!"
  ('so he scoops out white stuffing', 'film', 4679.30, -2.00),  # white stuffing pulled out over the plate
  ('and serves it', 'film', 4694.50, -1.80),  # Clark's arm drops stuffing on Mary's plate
  ("kat's head is in his fridge", 'film', 4704.20, -2.00),  # Clark walks to the CLOSED white fridge (head never shown)
  ('and all he says', 'film', 4727.10, -3.00),  # Mary's shaken face after "I tried to help her"
  ('then he makes you play his wife', 'film', 4946.60, -2.80),  # Mary in the red wig, close
  ('to relive the night', 'film', 4936.00, -2.00),  # Clark at the head of the table telling the night
  ("and when you say you're not", 'film', 4981.00, -3.00, 'z=1.4,dy=-80,g=1.2'),  # Mary in the red wig, close, talking back
  ('so you tell him the truth', 'film', 5019.50, -1.40),  # Mary, wig off: "You wanna know the real reason"
  ('that it was never the drinking', 'film', 5027.10, -2.80),  # Mary wide at the table, mid-speech
  ('and nothing is ever his fault', 'film', 5031.00, -2.10),  # Clark taking it
  ("he says he doesn't want", 'film', 5097.00, -3.40),  # Clark close: "I don't think I want to change"
  ("right where he's supposed to be", 'film', 5124.50, -1.70),  # Clark close: "right where I'm supposed to be"
  ('so you tell him to stay', 'film', 5130.40, -2.80),  # Mary: "Then stay."
  ('and he starts to untie you', 'film', 5170.60, -1.80),  # Clark bent at her strapped wrist, freeing it
  ("you're down to five", 'film', 5159.50, -1.90),  # Mary close, low angle
  ('at a dinner party', 'film', 5183.00, -1.90, 'g=1.25'),  # the dinner party through the arch: Clark, Mary, the still lifes
  ('who keeps a head', 'film', 4839.80, -2.10),  # Clark beside the closed fridge
  ('rule seven', 'film', 4910.00, -3.60),  # Clark sits at the head of his table, plate of stuffing, at home
  ("you're never leaving", 'film', 4919.20, -1.40),  # Mary in the wig at the table, wide
  ('and then the red-haired woman', 'film', 5174.30, -3.00, 'g=1.25'),  # the red-haired still life by the window
  ('panics and runs', 'film', 5177.35, -1.53, 'g=1.25'),  # she bolts out of frame
  ], inserts=[ins('he snaps', 3.40, 'film', shots=[(0, 'film', 5010.03, 1.0, 'lufs=-17')], sub="Stay in character! I've never even met her! STAY IN CHARACTER!"),
              ins('END', 0.85, 'hum', shots=[(0, 'film', 5190.50, 1.0, 'a=-24')])]))   # the empty dark arch (3:39-3:49), room tone
# ---------------------------------------------------------------- s09 CAPTAIN CLARK (66.0 s) ------------------------------------
X.append(sec('s09', [
  (0, 'film', 5201.40, -5.40, 'g=1.25,a=-18'),  # Captain Clark's silhouette comes through the arch, thudding steps
  ('a copy of clark', 'film', 5217.50, -1.50, 'g=1.25'),  # its tall silhouette in the arch over Clark
  ('towering and stretched', 'film', 5235.80, -1.90, 'g=1.25'),  # low angle: the towering hat silhouette over Clark
  ('dressed as the pirate', 'film', 5574.50, -1.15),  # Captain Clark in full costume, bright, in the store
  ('from his own tv commercial', 'film', 847.90, -1.70, 'z=1.333'),  # the film's own commercial: Cap'n Clark in his showroom
  ('peg leg and all', 'film', 856.80, -2.93, 'z=1.333'),  # the film's own commercial: Cap'n Clark hobbling across the showroom on crutch and peg leg
  ('this is captain clark', 'film', 5258.60, -0.80),  # his face under the tricorn, close
  ('captain clark', 'film', 5638.00, -1.10),  # NEW CUT  face and hat close, bright
  ('and clark tries to calm it', 'film', 5226.50, -2.00),  # Clark talking up at it
  ('introducing you like a dinner guest', 'film', 5212.50, -1.95),  # Clark turns from it toward Mary
  ('he tells it', 'film', 5230.60, -1.80),  # Clark, still talking up at it
  ('and that you said', 'film', 5221.30, -1.90),  # Mary frozen, close
  ("because it's just the way", 'film', 5247.60, -2.10),  # Clark, its head at his shoulder: "It's just the way we're wired"
  ("and that's when captain clark", 'film', 5250.55, -1.25),  # it seizes him, face at his neck
  ('picks him up', 'film', 5254.00, -1.50),  # NEW CUT  it holds him from behind, eyes over his shoulder
  ('and bites into him', 'film', 5256.56, -0.65, 'a=-20'),  # Clark screaming in its jaws (tail of the take, after s00's "Eaten" 5255.75-5256.51; no wound)
  ('into him', 'film', 5255.60, -0.95, 'a=-20'),  # NEW CUT  Captain Clark's mouth at Clark's neck, Clark screaming (no wound; ends 5262.57, before the bloody lift at 5264)
  ('you tear free and run', 'film', 5274.60, -1.70),  # Mary breaks up and away from the table
  ('and it hobbles after you', 'film', 5307.00, -1.30),  # Captain Clark coming down the middle of the fake street
  ('through a street of fake apartments', 'film', 5288.00, -2.20),  # Mary running between the fake houses
  ('a room full of couches', 'film', 5346.00, -1.30),  # Mary climbing over the piled striped couches
  ('and a hall with a locked door', 'film', 5374.45, -1.90),  # Mary shoving the locked door in the narrow hall
  ('so you crawl through a doggy door', 'film', 5385.10, -1.60),  # Mary crawling out through the doggy door
  ('into the biggest space', 'film', 5394.00, -2.00),  # walls of shelving, Mary's hand on the ledge
  ('endless floors around a giant drop', 'film', 5411.60, -2.40),  # wide: floors of shelving around the drop
  ('with a staircase floating', 'film', 5419.90, -3.20),  # Mary tiny on the floating stairs over the drop
  ('another door brings you up', 'film', 5456.50, -1.70),  # Mary climbs up out of the hatch in the floor
  ("of clark's store", 'film', 5485.10, -1.30),  # the copied store, wide
  ("except it's the copy", 'film', 5494.80, -1.60),  # Mary, the blank white cutout beside her
  ('ringed with gas canisters', 'film', 5520.40, -1.80),  # the store wide, blue canisters at the pillars
  ('and its door opens onto a wall', 'film', 5511.00, -2.40),  # Mary pushing the glass door, wall behind the glass
  ('with nowhere left to run', 'film', 5529.00, -1.40),  # Mary at the glass, frightened
  ('you snap its peg leg', 'film', 5570.00, -0.65),  # Mary swings the hat rack
  ('its peg leg with', 'film', 5572.38, -0.67),  # NEW CUT  the swing at camera
  ('a hat rack', 'film', 5573.66, -0.77, 'a=-18'),  # NEW CUT  the peg leg snaps (cut on the hit)
  ('knock over a cutout', 'film', 5576.88, -0.64),  # the caveman cutout tips over
  ('cutout that sets', 'film', 5578.80, -0.90),  # NEW CUT  the igniter under the fallen board sparks
  ('the gas hissing', 'film', 5612.80, -1.20, 'a=-18'),  # NEW CUT  a blue canister hissing gas
  ("and when it's right on top of you", 'film', 5630.25, -0.95),  # Captain Clark crawls over Mary through the gas
  ('on top of you', 'film', 5633.90, -1.00),  # NEW CUT  its face and hat looming over her
  ('you smash its face', 'film', 5653.60, -0.95),  # Mary raising the concrete
  ('face with your', 'film', 5639.35, -3.90),  # NEW CUT  its face under her hand (start of the take s10 uses at 5640.60; after s09's 5638.00 take)
  ('concrete handprint', 'film', 5646.60, -0.52),  # NEW CUT  the concrete handprint in her hand
  ('handprint until', 'film', 5662.42, -0.43),  # NEW CUT  the swing
  ('until the concrete breaks', 'film', 5663.10, -0.37, 'a=-18'),  # the hit, its head snaps (cut on the hit)
  ('concrete breaks', 'film', 5663.50, -0.60),  # NEW CUT  concrete fragments falling to the floor
  ('breaks', 'film', 5665.00, -1.00),  # NEW CUT  Mary on the floor, gasping
  ("you're down to two", 'film', 5668.15, -1.55),  # Mary scrambles away
  ('and rule eight is the simplest', 'film', 5604.80, -2.20),  # Mary crawling in the gas fog
  ("when you can't run", 'film', 5597.50, -2.35),  # Mary, gas spraying behind her
  ], inserts=[ins(0, 0.4, 'thud', shots=[(0, 'film', 5200.90, 1.0, 'a=-16')]),   # the first heavy step at the arch
              ins('dinner guest', 2.56, 'film', shots=[(0, 'film', 5214.53, 1.0, 'lufs=-17')], sub='This is Mary.')]))  # ~4:05, verify words and times
# ---------------------------------------------------------------- s10 ASYNC (58.0 s) --------------------------------------------
X.append(sec('s10', [
  (0, 'film', 5715.70, -2.70),  # hazmat men (yellow, green) walking at camera, mural behind
  ('and more gas knocks you out', 'film', 5710.05, -1.03, 'g=1.25,a=-18'),  # the hazmat man in the lit doorway, gas blasts into the dark room
  ('knocks you out', 'film', 5620.35, -2.03),  # NEW CUT  Mary lying knocked out on the store carpet, eyes shut
  ('you wake up at async', 'film', 5748.00, -1.70),  # Mary on all fours in the blue Async bay, hazmat men behind
  ('where they scan your body', 'film', 5785.00, -1.30),  # the body x-ray
  ('and your brain', 'film', 5796.50, -1.20),  # NEW CUT  the MRI brain scan
  ('and down the hall captain clark', 'film', 5818.20, -2.30),  # Mary led down the white Async hall by staff
  ('a table', 'film', 5821.95, -0.70),  # NEW CUT  the lab through the doorway: the body on the table, scans on the monitor
  ('his pirate hat part of his own body', 'film', 5822.75, -1.90, 'z=1.6,dx=-292,dy=43'),  # pushing into the lab: Captain Clark on the table, the tricorn on the table in front
  ('and from behind another door', 'film', 5831.75, -1.55, 'a=-4'),  # v3b: the closed Async doors, the child greeting 'Hello from the children of Planet Earth' (5832.4) heard under the voice
  ('comes that same tape of greetings', 'film', 5833.30, -2.55, 'a=-4'),  # v3b: the doors, camera pushing in, greetings playing behind (clean to 5835.85)
  ('so the hello and welcome', 'film', 1858.40, -3.20, 'g=1.25'),  # first trip: Clark walks to the lit doorway where the caveman stands
  ('may have come from async all along', 'film', 5809.00, -2.20),  # Async staff leading Mary down the white corridor
  ('phil the man who watched', 'film', 5875.00, -2.40),  # Phil comes in through the door
  ('tells you his company', 'film', 5990.80, -2.50),  # Phil: "Our company, we make..."
  ('until it found this place', 'film', 6005.00, -2.00),  # Phil: "before we found--"
  ('that he goes in every day', 'film', 6026.10, -2.30),  # Phil: "Every day, I go in there"
  ('and that doors are opening everywhere', 'film', 6040.00, -4.10),  # Phil talking at the table, wide
  ("so you ask if they'll let you go", 'film', 6080.30, -2.00),  # Mary: "You'll let me go?"
  ('and inside the backrooms', 'film', 6158.80, -4.00),  # her house's rubble in a yellow Backrooms room, street lamp (edl in 6158.63 after the insert pull-back; cut at 6158.50)
  ('your house', 'film', 6169.00, -1.20, 'g=1.25'),  # the copied living room
  ('a bookstore with your book', 'film', 6183.70, -2.30),  # the bookstore, her book's display
  ('missing posters for kat', 'film', 6188.00, -2.30),  # MISSING: Kathrine Taylor, Robert Franklin
  ('the strip mall', 'film', 6205.80, -1.90, 'g=1.25'),  # the strip mall at night, Clark's store sign
  ('and finally a copy of the room', 'film', 6211.20, -2.90, 'g=1.25'),  # the copied room, a figure by the windows
  ('with a copy of you', 'film', 6216.10, -2.90, 'g=1.25'),  # Mary's still life, hands in her lap
  ('five people walked in', 's1_joblo_first', 328.70, -1.90),  # (kept) empty yellow room, curved wall
  ('one walked out', 'film', 5891.20, -1.30),  # Mary alone at the table, wide
  ('and even she never got', 'film', 6125.00, -2.60),  # Mary close
  ('one out of five', 's1_joblo_first', 164.00, -2.00),  # (kept) wide empty yellow room, a hole in the floor
  ], inserts=[ins('let you go', 2.57, 'film', shots=[(0, 'film', 6099.53, 1.0, 'lufs=-17')], sub="That decision's not up to me.")],  # ~4:01, verify
  pad=0.9))
# ---------------------------------------------------------------- s11 outro (35.5 s) --------------------------------------------
X.append(sec('s11', [
  (0, 'film', 80.00, -4.00, 'z=1.333'),  # the tape again: wall + empty yellow rooms
  ('naren died on june', 'film', 142.40, -2.60, 'z=1.333'),  # Naren's yellow glove over the bench
  ('and clark found the door', 'film', 1531.00, -14.71, 'g=1.4'),  # Clark's silhouette at the store wall, light on it, night (same take, between s03 1528.30-1530.03 and s02 1543.20)
  ('ten days later', 'film', 1548.00, -7.67),  # Clark lying on the yellow carpet just after falling in (later in the take, after s02's 1545.80-1547.11)
  ('the movie never says it', 'film', 296.00, -3.00, 'z=1.333,g=1.25'),  # dark tape corridor, lit doorway far down
  ('but the only giant', 'film', 309.00, -1.50, 'z=1.333'),  # bright tape corridor, door at its far end
  ('giant', 'film', 5203.70, -3.92, 'g=1.25'),  # NEW CUT: Captain Clark's huge silhouette steps through the arch (moved 0.10 s: old 5203.60 overlapped s09's 5201.40-5203.64 by 0.04 s)
  ('it ever shows you', 'film', 5219.10, -2.07, 'g=1.15'),  # NEW CUT: Captain Clark stands in the arch over the tiny dining room (after s09's 5217.50-5218.86)
  ('is captain clark', 'film', 5237.70, -1.63, 'g=1.25'),  # low angle: Captain Clark's tricorn silhouette towering over Clark at the table (after s09's 5235.80-5237.56)
  ('so the backrooms had already made', 'film', 5242.00, -8.00),  # Clark's face beside Captain Clark's face: the original and the copy
  ('before he ever walked in', 'film', 1616.20, -11.68, 'g=1.4'),  # Clark standing close at the dark store wall, before he goes through (second trip, before s03's 1621.30)
  ("it doesn't wait for you", 'film', 1624.20, -3.68, 'g=1.4'),  # Clark at the dark wall, hands up, reaching into it (after s03's 1621.30-1624.08)
  ("because it's already started on you", 'film', 1730.30, -8.50, 'g=1.25'),  # dim room, lit opening, in-world stop sign
  ('so how long would you have lasted', 'film', 1722.20, -7.51),  # Clark walks toward the bright opening (after s03's 1720.00-1721.84)
  ('and which stage', 'film', 5301.80, -2.60),  # Mary running far down the fake street toward the door at its end (cut at 5301.71)
  ('tell me in the comments', 'film', 1652.20, -6.00),  # calm huge yellow room, Clark small by the furniture pile
  ('subscribe so you', 'film', 1698.00, -5.83, 'g=1.25'),  # calm empty yellow rooms, nobody in them (after s03's 1695.00-1697.56)
  ('and if you ever see a line of light', 'film', 2330.00, -8.00, 'g=1.5'),  # the glow on Clark's dark store wall (his later night, 2329.38 take; glow fades ~2338)
  ('leave it alone', 'film', 1496.70, -1.76, 'g=1.5'),  # the glow on the wall again (tail of the 1495.29 take, after s02's 1495.50-1496.58)
  ], extra=[('date', ['JUNE 19, 1990'], 'june nineteenth', 'and clark found'),
            ('date', ['JUNE 29, 1990'], 'june twenty-ninth', 'ten days later'),
            ('date', ['JUNE 29, 1990', '!10 DAYS LATER'], 'ten days later', 'the movie never says'),
            ('png', '../ep04/tiles/subscribe.png', 'subscribe so you', 'and if you ever')],
  pad=2.0))
