# EP04 Freddy v3 shot plan (11/7 KST, for the approved script_v3.md and the v3 voice)

Each line is one hard cut: `anchor phrase | clip candidates (first = preferred) | what must be on screen from the first frame`.

- The anchor is the exact script phrase where the cut lands (build_edl_v3.py finds it in voice/words.json, LEAD 0.08 s).
- The laptop picks the verified in-point and the clean span (no title card, no logo, no cut inside the span) and writes them into
  shots_v3.py in the EP07 format: (anchor, clip, in_s, -clean_s[, opts]).
- More cuts are welcome where a shot would run past about 3 s. Keep a fresh shot every 2 to 3 s and anchor each extra cut to a real script phrase.
- A candidate is a guess from the YouTube title. If none holds the moment, search the other clips of the same film first.
  Then use the closest real moment and note it in beats_v3.md. Never show a different film's Freddy than the one being talked about.
- **L** = the stat card is up, so keep the subject left or centre (EP07 opts 'z=1.35,dx=249').
- Never show the same moment twice. A later section may use the same scene, but a different moment of it.
- Gore is OK, but never the most extreme frame (cut on the hit or the reaction). No nudity.

## s00 cold open (14.8 s)

- Frame 0 = a big, bright, clear Freddy with the caption "HE WILL" already on screen.
- Every spoken word is captioned in 1 to 4 word chunks (list below). Each chunk gets its own hard cut showing that exact meaning.
- Victims get hurt from the second shot on.
- "We're ranking" shows the poster wall of the 9 films, which stays to the end. The last captions run in its centre band.

```
0 | n4_junkyard, n3_heres, n4_soulfood | FREDDY close-up, iconic face and hat, bright (frame 0)
drag you across | n1_tina_kill | Tina dragged up the bedroom wall by the invisible force
the ceiling | n1_tina_kill | Tina on the ceiling
turn you into | n3_marionette, n3_marionette_uk | Freddy slices Phillip's arms, the veins come out
a puppet | n3_marionette, n3_marionette_uk | Phillip walking like a puppet on his vein strings
smash your head | n3_primetime, n3_primetime_wb | the TV Freddy grabs Jennifer's head
through a tv | n3_primetime, n3_primetime_wb | her head goes into the TV (cut on the impact)
crush you | n4_roach | Freddy's hand closes the roach motel
like a bug | n4_roach | Debbie as a cockroach / the crush
or pull you down | n1_glen_bed, n1_glen | Glen pulled down into his bed
into your own bed | n1_glen, n1_glen_bed | the bed swallows him (cut before the worst of the geyser)
and all he needs | n1_wall, n1_boiler, n1_preview4k | Freddy watching, grinning, glove up
is for you | n1_bathroom | Nancy in the bath, eyes closing
to fall asleep | n1_bathroom | the glove rises out of the water between her knees
we're ranking | still_posterwall | the 9 posters pop in (release order) and hold to the end
```

Captions (the `extra` word list):

| Caption | From | To |
|---|---|---|
| He will | 0 | drag you across |
| Drag you across | drag you across | the ceiling |
| The ceiling | the ceiling | turn you into |
| Turn you into | turn you into | a puppet |
| A puppet | a puppet | smash your head |
| Smash your head | smash your head | through a tv |
| Through a TV | through a tv | crush you |
| Crush you | crush you | like a bug |
| Like a bug | like a bug | or pull you down |
| Or pull you down | or pull you down | into your own bed |
| Into your own bed | into your own bed | and all he needs |
| And all he needs | and all he needs | is for you |
| Is for you | is for you | to fall asleep |
| To fall asleep | to fall asleep | we're ranking |
| We're ranking | we're ranking | every freddy |
| Every Freddy | every freddy | by your chance |
| By your chance | by your chance | of surviving |
| Of surviving him | of surviving | 999 |

## s01 rules (26.5 s)

The stat card shows from frame 0: tile mystery.png, name FREDDY, STRENGTH 6, INTELLIGENCE 7, KILL COUNT 5, DREAM POWER 8, "??%".
- Bars fill on "strength", "intelligence", "kill count" and "dream power".
- The % lands on "survival rate".
- All shots are L.

```
0 | n1_screw_sleep, n1_plan | Nancy fighting sleep (coffee, eyes heavy)
you fall asleep | n3_kristen, n3_bed, r10_m1 | a teenager falls asleep in bed
and that movie's freddy | n1_boiler, n1_opening | the 1984 Freddy in the boiler room
is waiting for you | n1_opening, n1_boiler | Freddy steps out of the shadows / glove on the pipes
and every freddy is different | r10_unavoidable, r10_creepiest | the 2010 Freddy's face
one is so weak | fj_notstrong | the weak Freddy vs. Jason Freddy
he needs jason | fj_crash, fj_rave | Jason with the machete
one needs a teenager's body | n2_brain, n2_emerge | Freddy's claws/face coming out of Jesse
and one is strong enough | n4_soulfood, n4_alice | the Dream Master Freddy
to wipe out kids | n4_karate, n4_hell | Freddy beating a Dream Warrior (Rick or Kristen)
so we score | n1_opening | the glove being forged
intelligence | n3_heres | Freddy's trick ("Here's Freddy")
kill count | n5_forcefed4k, n4_kiss | a Freddy kill
and dream power | n3_worm | Freddy turns into the worm
once your eyes close | n1_bathroom, r10_bath_uk | eyes closing (another moment than the open)
put it all together | n6_forever | Freddy close-up
your survival rate | n7_coming | the New Nightmare Freddy close-up
```

## s02 #9 Freddy vs. Jason 95% (36.6 s, card from "if you've never heard")

```
0 | fj_world, fj_notstrong | the Freddy vs. Jason Freddy (rank card over it)
this freddy is the weakest | fj_notstrong | Freddy weak, powerless in his dream world
because his town forgot | fj_intro, fj_cornfield | Springwood, a quiet street / houses
the adults erased | fj_intro, fj_back | the adults covering it up (cops, parents, files)
every trace of him | fj_intro | Freddy's past, newspaper clippings or the empty Elm Street house
and anyone who still dreams | fj_intro, fj_back | the Westin Hills patients (Will, Mark)
gets locked away | fj_back, fj_influence | Westin Hills hospital
and kept on a drug | fj_influence, fj_intro | Hypnocil pills or the injection
he's so weak | fj_notstrong | Freddy (frustrated, can't kill)
bring jason back | fj_mom | Freddy disguised as Jason's mother, talking to Jason
to scare people | fj_mommy, fj_dreaming | Jason rising / walking into Springwood
in a movie with his own name | fj_kicks, fj_world | Freddy
jason does nearly all | fj_rave, fj_crash | Jason slaughtering the rave
and freddy kills exactly | fj_back | Freddy goes after Mark
one person himself | fj_back | Mark's death ("Freddy's back" on his back)
in the end lori | fj_hell, fj_construction | Lori with Jason's machete
cuts his head off | fj_hell | the swing / Freddy's head (cut on the hit)
with jason's machete | fj_hell | Jason holding Freddy's head, the wink
if you've never heard | fj_notstrong | Freddy fading (L)
he can't even find | fj_world | Freddy (L)
survival rate | fj_kicks | Freddy close-up (L)
```

## s03 #8 Freddy's Revenge 65% (42.9 s, card from "stay far away")

```
0 | n2_brain | the Freddy's Revenge Freddy (rank card)
this freddy is far more | n2_pool, n2_party | Freddy menacing at the party
because he doesn't need | n2_emerge | Freddy close-up
he takes over a teenager | n2_kill4k, n2_brain | Jesse possessed, sweating
named jesse | n2_kill4k | Jesse
climbs right out | n2_brain, n2_emerge | Freddy bursting out of Jesse's body
and kills more people | n2_pool | panic at the pool party
than any other freddy | n2_party | Freddy at the party
he kills jesse's gym teacher | n2_creepiest | Coach Schneider in the showers
in the showers | n2_creepiest | the shower attack
then his friend grady | n2_kill4k, n2_grady_fan | Grady attacked in his bedroom
then a whole group | n2_pool | kids attacked at the pool party
and in the very last scene | n2_creepiest, n2_kerry_fan | the final bus scene
his claws burst out | n2_creepiest, n2_kerry_fan | the claws burst out of Kerry
on the school bus | n2_bus, n2_schoolbus | the bus speeding off
but he's also the dumbest | n2_party | Freddy (clumsy, showy)
he barely uses | n2_pool | Freddy in the real world at the pool
and he can be beaten | n2_creepiest, n2_kiss_fan | Lisa confronting Freddy
lisa tells jesse | n2_creepiest, n2_kiss_fan | Lisa
kisses freddy | n2_creepiest, n2_kiss_fan | the kiss
and he burns to ash | n2_creepiest, n2_kiss_fan | Freddy burns away
stay far away | n2_kill4k | Jesse (L)
and you'll probably be fine | n2_creepiest | Lisa and Jesse (L)
survival rate | n2_brain | Freddy (L)
```

## s04 #7 The Dream Child 55% (39.9 s, card from "he only gets three")

```
0 | n5_tricks, n5_son4k | the Dream Child Freddy (rank card)
this freddy kills fewer | n5_hell4k | Freddy
but he's far smarter | n5_superfreddy | Freddy smirking
and much stronger | n5_pool | Freddy's dream power
he finds a sneaky | n5_son4k, n5_itsaboy | pregnant Alice / the unborn baby
through the dreams | n5_son4k | Jacob, the child
so he can come | n5_drunk, n5_motorcycle | Freddy coming for her friends
even while she's wide | n5_tricks | Alice awake and scared
he turns dan | n5_motorcycle, n5_drunk | Dan on the motorcycle
into part of his own | n5_motorcycle | Dan fused with the bike
force-feeds greta | n5_forcefed4k, n5_force_feed | Greta force-fed by Freddy
until she chokes | n5_force_feed, n5_forcefed4k | Greta choking
and turns mark | n5_superfreddy | Mark pulled into the comic book
into a paper drawing | n5_superfreddy | Mark as paper
before slicing him | n5_superfreddy | Super Freddy slices him
but alice has beaten | n5_tricks | Alice
and in the end | n5_hell4k, n5_back_to_hell | Amanda Krueger, Freddy's mother
jacob uses the power | n5_back_to_hell, n5_hell4k | Jacob using his power
to destroy him | n5_back_to_hell | Freddy pulled apart
he only gets three | n5_baby4k, n5_baby | Freddy (L)
so if he comes | n5_tricks | Freddy (L)
survival rate | n5_son4k | Freddy (L)
```

## s05 #6 Freddy's Dead 45% (45.3 s, card from "he's deadly but")

```
0 | n6_forever | the Freddy's Dead Freddy (rank card)
unlike the last one | n6_father | Freddy
has the biggest body count | n6_town | empty Springwood
before the movie even starts | n6_town | the empty town, the carnival, the strange adults
almost every child | n6_town | missing children posters / empty school
but he's also the silliest | n6_oz | Freddy on the broomstick
and he plays with his victims | n6_playground, n6_game | Freddy playing with a victim
he turns up carlos's | n6_ear, n6_earcheck | Carlos's hearing aid
until one scratch | n6_chalk, n6_nice | Freddy's claws on the chalkboard
kills him | n6_nice | Carlos's reaction (no explosion frame)
traps spencer inside | n6_game, n6_drug | Spencer pulled into the video game
a video game | n6_game | Freddy with the Power Glove
and drops john doe | n6_doom | John Doe falling
the last teenager | n6_busrt, n6_doom | John Doe
onto a bed of spikes | n6_doom | the spikes (cut before the impact)
all those jokes | n6_forever | Freddy laughing
tracy gets woken | n6_father | Tracy attacked in the dream, then wakes
before he can finish | n6_father | Tracy fights him off
in the end his own daughter | n6_daughter, n6_blood | Maggie
drags him into the real | n6_maggie | Maggie pulls him out
and shoves a pipe bomb | n6_maggie | the pipe bomb in his chest
he's deadly but | n6_brain | Freddy (L)
and that time is | n6_maggie | Freddy blown up / gone (L)
survival rate | n6_forever | Freddy (L)
```

## s06 #5 the 2010 remake 38% (39.3 s, card from "staying awake won't")

```
0 | r10_creepiest, r10_unavoidable | the 2010 Freddy (rank card)
this freddy is the opposite | r10_unavoidable | the dark 2010 Freddy
he's dark mean | r10_boyfriend | Freddy close-up
and serious | r10_dreaming | Freddy
and he has a trick | r10_m3 | Quentin in the store
that makes staying awake | r10_m1, r10_m2 | Nancy fighting sleep
go too long without | r10_m3 | tired eyes, pills
and your brain drops | r10_m3 | the micro-nap flicker
for a few seconds | r10_m3 | Freddy appears in the store
without you even noticing | r10_m3 | snapping back awake
by the time nancy figures | r10_m4 | Nancy
every other kid | r10_creepiest, r10_m4 | the preschool photo
except her and quentin | r10_m4 | Nancy and Quentin
he gets dean | r10_preview, r10_dean_fan | Dean in the diner
kris in her bedroom | r10_creepiest, r10_kris_fan | Kris thrown around her bedroom
and jesse in a jail cell | r10_creepiest | Jesse in the cell
and even after nancy drags | r10_creepiest | Nancy pulls Freddy out
and cuts his throat | r10_creepiest | the throat cut (cut on the move)
he comes back through | r10_creepiest | the mirror attack on Nancy's mother
staying awake won't | r10_boyfriend | Freddy (L)
survival rate | r10_dreaming | Freddy (L)
```

## s07 #4 New Nightmare 30% (38.9 s, card from "he only gets four")

```
0 | n7_coming | the New Nightmare Freddy (rank card)
this freddy is stronger | n7_missme | Freddy
and he doesn't just hunt | n7_stalks | Freddy
he hunts a whole family | n7_dylan | Heather, Dylan and Chase at home
he goes after heather | n7_stalks | Heather scared
the actress who played | n7_funeral, n7_dylan | Heather
and picks off the people | n7_funeral | the funeral
he kills two special | n7_hand, n7_handbed, n7_bloodiest | the new glove attacks the effects men on set
working on a new | n7_hand, n7_bloodiest | the film set
then her husband | n7_bloodiest, n7_chase_fan | Chase driving at night, nodding off
while he's driving | n7_bloodiest, n7_chase_fan | the claws, the crash
then her son's babysitter | n7_julie | Julie in the hospital
dragging her up the wall | n7_julie | Julie dragged up the wall
then he takes her little | n7_traffic, n7_dylan | Dylan
right into his world | n7_end | Freddy's lair
it takes heather and dylan | n7_end | Heather and Dylan together
to push him into | n7_end | the furnace
he only gets four | n7_surgery | Freddy (L)
but if he picks | n7_son | Freddy (L)
survival rate | n7_coming_uk | Freddy (L)
```

## s08 #3 the 1984 original 22% (42.2 s, card from "unless you're as")

```
0 | n1_preview4k, n1_wall | the 1984 Freddy (rank card)
from nineteen eighty-four | n1_opening, n1_preview4k | the 1984 glove / Freddy in the boiler room
this freddy isn't as strong | n1_tina_chase | Freddy in the alley
but he's the scariest | n1_boiler | Freddy in the shadows
he barely talks | n1_opening | silent Freddy
he stays in the shadows | n1_tina_chase | Freddy half hidden in the dark
and nobody believes you | n1_plan, n1_screw_sleep | Nancy with her mother or the police
until it's too late | n1_dark_story | Nancy alone
he drags tina | n1_tina_kill | Tina dragged (another moment than the open)
across the ceiling | n1_tina_kill | Tina on the ceiling (another moment than the open)
strangles rod | n1_rod | the bedsheet around Rod's neck
in a jail cell | n1_rod | the cell
and pulls glen down | n1_glen | Glen in bed (another moment than the open)
nancy only survives | n1_plan | Nancy
to learn his rules | n1_plan | Nancy planning
she sets traps | n1_traps | the traps
drags him into the real | n1_fight | Nancy pulls Freddy out
and finally turns her back | n1_no_fear | Nancy turns her back
taking away the fear | n1_no_fear | Freddy vanishes
and even then | n1_ending | Marge
he still takes her mother | n1_ending | Marge pulled through the window
unless you're as | n1_plan | Nancy (L)
he gets you | n1_god | Freddy (L)
survival rate | n1_wall | Freddy (L)
```

## s09 #2 Dream Warriors 12% (40.3 s, card from "you don't have")

```
0 | n3_heres | the Dream Warriors Freddy (rank card)
this freddy is deadlier | n3_real | Freddy
because kids who learn | n3_best4k | the Dream Warriors in the dream
still can't stop | n3_souls | Freddy
he hunts the last children | n3_best4k | the group at Westin Hills
in a mental hospital | n3_wizard, n3_best4k | the hospital corridor
he turns phillip | n3_marionette_uk | Phillip (another moment than the open)
using his own veins | n3_marionette_uk | Freddy working the vein strings
smashes jennifer's head | n3_primetime_wb | Jennifer and the TV (another moment than the open)
and kills taryn | n3_taryn | Taryn, syringe fingers
and will | n3_wizard_rt | Will in his wheelchair
even after they find | n3_wizard | Will's wizard magic
then his skeleton kills | n3_skeleton | the skeleton attacks Donald
in the real world | n3_skeleton | the junkyard
and freddy kills nancy | n3_nancy | Freddy stabs Nancy
while pretending to be | n3_nancy | Freddy disguised as her father
so even the girl | n3_nancy | Nancy dying
the kids who survived | n3_best4k | Kristen, Kincaid and Joey
and it still took | n3_skeleton | Neil with the holy water
on his bones | n3_skeleton | the bones burning
you don't have | n3_heres | Freddy (L)
survival rate | n3_real | Freddy (L)
```

## s10 #1 The Dream Master 5% (38.1 s, card from "if the kids")

```
0 | n4_junkyard, n4_reborn | the Dream Master Freddy reborn (rank card)
this freddy is the strongest | n4_reborn | Freddy
the one who wiped out | n4_soulfood | Freddy
kincaid | n4_junkyard | Kincaid in the junkyard
joey | n4_waterbed, n4_nurse | Joey and the waterbed
and kristen | n4_beach | Kristen on the beach
the kids who survived | n4_hell | Kristen thrown into the furnace
are all dead early | n4_hell | Freddy
then he goes through alice's | n4_alice | Alice and her friends
sheila | n4_kiss | Sheila's kiss of death
rick | n4_karate | Rick's karate fight
and debbie | n4_roach | Debbie (another moment than the open)
who he turns into | n4_roach | the roach transformation
and every soul he takes | n4_soulpizza, n4_soulfood | the souls in his chest
alice only wins | n4_alice | Alice
and showing freddy | n4_death, n4_torn | the mirror, his reflection
so the souls inside | n4_torn | the souls breaking out
and tear him apart | n4_torn | Freddy torn apart
if the kids | n4_doctor | Freddy (L)
you won't either | n4_alice | Freddy (L)
survival rate | n4_soulfood | Freddy (L)
```

## s11 outro (24.2 s)

```
0 | still_posterwall | callback to the cold open: the poster wall
from the one who needed | fj_collide | Freddy and Jason
to the one who wiped | n4_alice | the Dream Master Freddy
which freddy would | n7_coming_uk | Freddy
tell me in the comments | n6_forever | Freddy
along with the killer | n3_heres | Freddy
and honestly | n1_god | Freddy
every death in all | n4_kiss, n5_forcefed4k | a quick kill
to get this ranking | n7_missme | Freddy
we're a small channel | n2_party | Freddy
thanks for watching | n1_ending | the girls skipping rope
don't fall asleep | n1_bathroom | the glove in the bath, hold to the end (pad 2.0 s)
```

Overlays like the EP07 outro:
- a two-line title on "which freddy would" until "tell me in the comments", e.g. "WHICH FREDDY / !WOULD YOU LEAST WANT TO MEET?" (shrink to fit);
- tiles/subscribe.png (copy from ../ep07_pinhead/tiles) on "every subscribe" until "thanks for watching";
- the title "DON'T FALL / !ASLEEP" on "don't fall asleep" to the end.
