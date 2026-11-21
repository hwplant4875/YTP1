# EP04 Freddy Krueger, story fact check of script_v3.md and stats.json (2026-11-21)

Scope: every factual claim in s00 to s11 of `script_v3.md` and every KILL COUNT and survival % in `stats.json`. Neither file was edited. I did not trust the script's own notes or any "verified" label.

Verdict key: RIGHT, WRONG, MISLEADING, UNCONFIRMED. For death lists, "2 src" means two separate sources agree, "1 src" means one source, UNCONFIRMED means no source I could reach states it.

---

## 1. Sources, and what was blocked

| # | Source | How fetched | Used for | Status |
|---|---|---|---|---|
| W | English Wikipedia, `/wiki/<title>` HTML, Plot section, all 9 films | curl, browser UA | Main plot spine for all 9 | OK |
| E | Elm Street fandom wiki, "List of deaths in the A Nightmare on Elm Street films" plus character pages (Marcus Yeon, Julie, Spencer Lewis, Mark Davis), reboot-murders page | fandom `api.php action=parse prop=wikitext` | Per-film death tables | OK. The page itself is tagged `{{Unreferenced}}` |
| H | Horror fandom wiki (horror.fandom.com), film pages for all 9 with "List of Deaths" tables | fandom api.php | Second death table for each film | OK. Its plot text partly copies Wikipedia and its tables look partly copied from E, so H and E are **not fully independent**. Where only E and H agree I still write "2 src", but treat that as weaker than W plus one fandom wiki |
| V | Villains fandom wiki, "Freddy Krueger (A Nightmare on Elm Street)/Synopsis", which covers every film including the 2010 Freddy and the New Nightmare entity | fandom api.php | Film-by-film description of kills, written separately from W | OK |
| F | Friday the 13th fandom wiki, "Freddy vs. Jason" page with a timestamped deaths list | fandom api.php | FvJ deaths, who killed whom | OK |
| P | Plugged In, 2010 remake review, "Violent Content" | curl | 2010 deaths, content flags | OK |
| P2 | Plugged In, Freddy vs. Jason review | curl | General only | The page loads, but its Violent Content section is empty in the HTML. Not useful |
| X1 | themoviespoiler.com | curl search | none | Their search returns no page for any Elm Street film. No such pages exist, so nothing was used |
| X2 | IMDb plot synopsis pages, all 9 | curl | none | **Blocked**: HTTP 202 with an empty body (bot challenge) |
| X3 | Dead Meat Kill Count totals | WebSearch | none | Only episode listings came back, with no totals. **Not confirmed**. I use no Dead Meat number anywhere |
| X4 | Plugged In reviews of the other 7 films | WebSearch | none | Not found |

---

## 2. Per-film death and attack lists (in film order)

Counting rule for "Freddy's own kills": a death counts if Freddy causes it directly. That covers his glove or powers in a dream, his body in the real world, his possessed host (Jesse in 1985) and his possessed bones (Dream Warriors). Kills by Jason, by other people and by accidents do not count, and neither do kills Freddy only sets up. Each count is split into **on-screen in the present**, **shown in a flashback** and **implied off-screen**.

### 2.1 A Nightmare on Elm Street (1984)
1. Tina Gray. Slashed, dragged up the wall and across the ceiling, dropped. Freddy, in a dream, on screen. 2 src (W, E, H)
2. Rod Lane. Strangled and hanged with his own bedsheet in a jail cell, staged to look like suicide. Freddy, in a dream, on screen. 2 src (W "staging it as a suicide", E, H)
3. Glen Lantz. Pulled into his bed, blood geyser. Freddy, in a dream, on screen. 2 src (W, E, H)
4. Marge Thompson. Smothered by a burning Freddy and sinks into the bed, before Nancy turns her back on him. In the final twist scene she is alive again and is grabbed through the door window. Freddy, on screen. 2 src (W, E, H). Counted once.
- Backstory: Freddy killed 20 children before he died (Marge's line). Implied, before the film. 1 src (W)
- **Attacked and survived**: Nancy many times. She is nearly drowned in the bathtub, burns her arm on a pipe to wake up in class, pulls his hat out of a dream at the sleep clinic, and in the end traps him and turns her back on him. Don Thompson is also present at the end. 2 src (W, V)
- Freddy's own kills: on-screen **4**. Flashback 0. Implied 20 before the film.

### 2.2 Freddy's Revenge (1985)
1. Coach Schneider. Tied up and slashed in the showers. Freddy through Jesse's body, real world, on screen. 2 src (W, E, H)
2. Ron Grady. Slashed or impaled through his bedroom door. Freddy emerging from Jesse, real world, on screen. 2 src (W, E, V)
3. Pool party guests. W says only "slaughters several partygoers". E and H each list 6 kills by Freddy (slashed, two in the boiling pool, one into the fire, one gutted, one through the grill) plus 1 guest trampled by the crowd, which is an accident. E notes that the gutted guest might have survived. Real world, on screen. The number of party deaths is **1 src (E and H as one source), and the exact number is UNCONFIRMED**.
4. Kerry. His claws burst out of her chest on the school bus in the last scene, and it is unclear whether this is a dream. Freddy, on screen. 2 src (W, E, V)
- Fate of Jesse and Lisa after the bus scene: ambiguous. Not a death.
- **Attacked and survived**: Lisa. Freddy attacks her at her house but cannot harm her because of Jesse's influence, and later she beats him with love at the factory. 2 src (W, V). Jesse is possessed and freed, 2 src. Most party guests survive, 1 src (H says most guests ran for the fence). Lisa stops her father from shooting Freddy, 1 src (H).
- Freddy's own kills: on-screen **about 9** (Schneider, Grady, about 6 party guests, Kerry). The party number is not confirmed. Without the party it is 3.

### 2.3 Dream Warriors (1987)
1. Phillip. Veins pulled out and worked like puppet strings, then he walks off a high ledge or window, which looks like suicide. Freddy, dream and real world, on screen. 2 src (W, E, H, V)
2. Jennifer. Head smashed into a TV. Freddy, dream, on screen. 2 src
3. Taryn. Needle claws inject her with heroin. Freddy, dream, on screen. 2 src (W, E, H, V)
4. Will. Stabbed with the glove. Freddy, dream, on screen. 2 src
5. Don Thompson. Freddy's possessed skeleton throws him onto a car's tail fin. Real world, on screen. 2 src (W "Freddy kills Don", H "takes possession of his bones", V)
6. Nancy Thompson. Stabbed by Freddy disguised as her father. Dream, on screen. 2 src
- Opening scene: Freddy cuts Kristen's wrist so that it looks like a suicide attempt, and she survives. 2 src (W, E)
- **Attacked and survived**: Kristen, who escapes the opening attack and is saved at the end when Nancy stabs Freddy with his own glove. Joey, who is captured and left in a coma, then rescued. Kincaid, who is overpowered and saved when the bones are disturbed. Neil, who is knocked out by the skeleton. All 2 src (W, H, V)
- Freddy's own kills: on-screen **6**.

### 2.4 The Dream Master (1988)
1. Kincaid. Stabbed in the junkyard. Freddy, dream, on screen. 2 src
2. Joey. Pulled into his waterbed, where the woman is a nude model who turns into Freddy, and drowned. Freddy, dream, on screen. 2 src (W, E, V)
3. Kristen. Thrown into the boiler. Freddy, dream, on screen. 2 src
4. Sheila. Life sucked out by a kiss, looks like an asthma attack. Freddy, dream, on screen. 2 src
5. Rick. Killed by an invisible Freddy in a dojo. Freddy, dream, on screen. 2 src
6. Debbie. Turned into a cockroach and crushed in a roach motel. Freddy, dream, on screen. 2 src
- **Attacked and survived**: Alice, who defeats him. Dan, who is badly hurt in a real car crash, then hurt again in the dream and woken by his surgeons. 2 src (W, V)
- Freddy's own kills: on-screen **6**.

### 2.5 The Dream Child (1989)
1. Dan Jordan. Fused with a motorcycle and sent into oncoming traffic. Freddy, dream, death in the real world, on screen. 2 src (W, E, V). What vehicle Dan was really driving is UNCONFIRMED: V says "crashes his truck", W does not say.
2. Greta. Force-fed until she chokes. Freddy, dream, on screen. 2 src
3. Mark Gray. Turned into a paper cutout and slashed to pieces. Freddy, dream, on screen. 2 src
- H also lists "Mr Gibson" as killed by Freddy. No other source has this, so UNCONFIRMED and ignored.
- **Attacked and survived**: Mark, nearly killed the first time and saved by Alice. Yvonne, lured into danger in a Jacuzzi and rescued by Alice. Alice and Jacob. 2 src (W, V)
- Freddy's own kills: on-screen **3**.

### 2.6 Freddy's Dead (1991)
- Before the film: Freddy has killed "nearly every child and teenager in Springwood". Implied, uncountable. 2 src (W, H, V)
1. Carlos. His hearing aid is turned up and a chalkboard scratch makes his head explode. Freddy, dream, on screen. 2 src (E, H, V)
2. Spencer. Trapped in a video game, then knocked into a pit or killed with the Power Glove. He dies. Freddy, dream, on screen. 2 src (W, E, V)
3. John Doe. Dropped onto a bed of spikes. Freddy, dream, on screen. 2 src
- Flashbacks inside Maggie's journey into his mind: his wife Loretta is strangled, on screen in the flashback, 2 src (W "murdered his wife", H, V). His foster father Underwood is killed with a razor, 1 src (V; H says not on screen).
- **Attacked and survived**: John at the start, whom Freddy deliberately throws out of town to use him (2 src). Tracy, almost killed and woken by Maggie (2 src, W, H). Later Tracy wakes herself by pressing her wrists onto a hot stove (1 src, V). Doc tears his sweater and wakes up (1 src, V). Maggie kills him.
- Freddy's own kills: on-screen in the present **3**. Flashback 1 to 2. Implied: almost every child in Springwood.

### 2.7 Wes Craven's New Nightmare (1994)
1. Chuck (Charles Wilson), special effects technician. Killed by the claw in Heather's opening nightmare, and the death turns out to be real. The entity as Freddy, on screen. 2 src (E, V). W only mentions the claw attack, not the deaths.
2. Terry (Terrance Feinstein), special effects technician. Same scene. 2 src (E, V)
3. Chase Porter, Heather's husband. Slashed at the wheel while driving. On screen. 2 src (W, E, V)
4. Julie, the babysitter. Stabbed, dragged up the wall and across the ceiling like Tina, in the hospital. On screen. 2 src (W, E)
- **Attacked and survived**: Heather, many times. Dylan, who is abducted and rescued, and who pushes Freddy into the furnace together with Heather. Chase survives a first cut in Heather's dream. 2 src (W)
- Freddy's own kills: on-screen **4**.

### 2.8 Freddy vs. Jason (2003)
Jason kills, all real world (2 src, W, E, F). Trey. Blake's father. Blake. Gibb, whom Freddy was attacking in her dream. A raver at the field. A man whose head is twisted. Shack. About 6 more ravers. A security guard. Deputy Stubbs. Bill Freeburg, while Freddy is possessing him. Linderman. Kia. That is about 18 to 20, depending on whether the dream-opening "Heather" (F, H) is counted.
1. Mark Davis. Burned, with "Freddy's Back" seared into his back. **Freddy**, dream, on screen. 2 src (W, E, F)
2. Lori's mother. Stabbed by Freddy. This is revealed and shown in a flashback in the dream near the end. 2 src (W "learns that he murdered her mother", F "Lori's Mom stabbed to death by Freddy", H "Flashback")
- Possible extra: the opening montage shows Freddy with a little girl (H, 1 src). Bobby Davis's death may be Freddy's or a suicide (H, 1 src). Both UNCONFIRMED.
- **Attacked and survived**: Lori, attacked in dreams several times. She wakes up and pulls a piece of him out, later pulls all of him into the real world, and beheads him. Will. Jason, whom Freddy tortures in a dream. Freeburg survives Freddy's possession but is killed by Jason. Gibb is attacked by Freddy in her dream but is killed by Jason. 2 src (W, F)
- Freddy's own kills: on-screen in the present **1** (Mark). Flashback **1** (Lori's mother). Total 2.

### 2.9 A Nightmare on Elm Street (2010)
- Before the film: all the other children from the preschool class are dead, "most of them in their sleep". 2 src (W, H). H names 7 of them, 1 src.
1. Dean Russell. In the diner, in his dream Freddy turns Dean's knife on him, and in reality Dean is seen cutting his own throat. Freddy, on screen. 2 src (W, P, V)
2. Kris Fowles. Thrown around the room and slashed while Jesse is with her at her house, on her bed. Freddy, dream, on screen. 2 src (W, P "on her bed", H "her house")
3. Jesse Braun. Impaled in a jail cell. Freddy, dream, on screen. 2 src (W, P, V)
4. Marcus Yeon. Falls asleep on his webcam blog and his head is smashed into the computer, seen as a video Nancy watches. Freddy, on screen. 2 src (E, H, V; W does not mention him)
5. Gwen Holbrook, Nancy's mother. Blades through her head from behind, pulled through the mirror. Freddy, on screen. 2 src (W, P, E)
- **Attacked and survived**: Kris, attacked in class but wakes up (1 src, V). Nancy, attacked in a microsleep, cut on the arm, and pulls a piece of his sweater out (2 src, W, V). Quentin, attacked at the end (2 src). Nancy and Quentin together use adrenaline, pull him out and cut his throat.
- Freddy's own kills: on-screen **5**. Implied: all other preschool kids, about 7 by name (1 src).

---

## 3. Line-by-line table

Proposed fixes are written as spoken lines, with no colons and no dashes.

### s00 cold open
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| drag you across the ceiling | RIGHT | Tina 1984, and Julie in New Nightmare | |
| turn you into a puppet | RIGHT | Phillip, Dream Warriors | |
| smash your head through a TV | RIGHT | Jennifer, Dream Warriors. Her head goes into the screen | |
| crush you like a bug | RIGHT | Debbie, Dream Master | |
| pull you down into your own bed | RIGHT | Glen 1984 | |
| all he needs is for you to fall asleep | RIGHT as a hook | It does not hold for 1985, where Freddy acts through an awake Jesse, or for the real-world climaxes. This is acceptable for a cold open | |

### s01 rules
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| One is so weak he needs Jason to kill for him | RIGHT | FvJ (W) | |
| one needs a teenager's body | RIGHT | 1985, Jesse | |
| one is strong enough to wipe out kids with superpowers | RIGHT | Dream Master kills Kincaid, Joey and Kristen | |

### s02 #9 Freddy vs. Jason, 95%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| weakest of them all, because his town forgot him | RIGHT | W | |
| The adults erased every trace of him | RIGHT | W | |
| dreamers are locked in a hospital and kept on a drug that stops dreaming | RIGHT | Westin Hills and Hypnocil (W, F) | |
| he has to bring Jason back from Hell to scare people for him | RIGHT | W, "using the last of his power, he resurrects Jason" | |
| Jason does nearly all the killing | RIGHT | About 18 to 20 Jason kills against 1 or 2 by Freddy (E, F) | |
| Freddy kills exactly one person himself, Mark | **MISLEADING** | True for on-screen kills in the present. But the film reveals and shows in a flashback that Freddy murdered Lori's mother (W, F, H). Strict fans will raise this | "and in the present day, Freddy kills exactly one person himself, Mark, though we find out he also murdered Lori's mother years before" |
| Lori cuts his head off with Jason's machete | RIGHT | W, F. Note that his head still winks in the final shot | |
| If you've never heard his name, he can't even find you | **Reason rule broken**, see section 5 | | see section 5 |

### s03 #8 Freddy's Revenge, 65%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| far more dangerous than the last one, because he doesn't need Jason | RIGHT, and it matches the stats | KC 8 against 1 and STR 7 against 5 | |
| takes over Jesse, climbs right out of his body | RIGHT | W | |
| kills more people on screen than any other Freddy | RIGHT, with a caveat | About 9 against 6 for Dream Warriors and Dream Master. It depends on the party deaths, whose exact number is only 1 src (E/H). Without the party he has only 3 | Keep it, but make sure the visuals show party victims dying |
| kills Jesse's gym teacher in the showers | RIGHT | Coach Schneider (W, E, H) | |
| then his friend Grady | RIGHT | W | |
| then a whole group of kids at a pool party | MISLEADING, minor | W says "several partygoers", and H says most guests ran for the fence. "A whole group" can sound like everyone there | "then several kids at a pool party" |
| claws burst out of Lisa's friend Kerry on the school bus, in the very last scene | RIGHT | W, E, V | |
| he's also the dumbest Freddy | Opinion, UNCONFIRMED as fact | Matches INTELLIGENCE 3, the lowest card. It is not a film fact, so keep it framed as the channel's view | |
| he barely uses his dream powers | RIGHT, interpretive | Most of his kills are in the real world through Jesse's body (E, H) | |
| beaten by love, Lisa says she loves him, kisses Freddy, he burns to ash | RIGHT | W. Jesse then climbs out of the ashes | |
| Stay far away from Jesse, and you'll probably be fine | **Reason rule broken**, see section 5 | | |

### s04 #7 The Dream Child, 55%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| kills fewer people than the last one, far smarter, much stronger in dreams | RIGHT, matches the stats | KC 3 against 8, INT 7 against 3, DP 8 against 4 | |
| comes in through the dreams of Alice's unborn son, Jacob, so he can reach her friends while she's awake | RIGHT | W | |
| He turns Dan into part of his own motorcycle | **MISLEADING** | With "He" as the subject, "his own" reads as Freddy's motorcycle. Dan is fused with a motorcycle in his dream and sent into traffic (W, E). Whether it was Dan's real vehicle is UNCONFIRMED, since V says he was driving a truck | "He fuses Dan to a motorcycle in his dream and sends him into oncoming traffic" |
| force-feeds Greta until she chokes | RIGHT | W, E | |
| turns Mark into a paper drawing before slicing him to pieces | RIGHT | W, E ("paper cutout") | |
| Alice has beaten him once already | RIGHT | Dream Master | |
| with help from Freddy's own mother, Jacob uses the power Freddy gave him to destroy him | RIGHT | W, V. Amanda then seals him away | |
| He only gets three kills | RIGHT | Dan, Greta, Mark | |
| so if he comes for you, it's close to a coin flip | Acceptable, see section 5 for a better grounded version | | |

### s05 #6 Freddy's Dead, 45%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| this Freddy has the biggest body count of them all | MISLEADING as worded | Right only if you count the implied massacre before the film (W, H, V). On screen in the present he kills just 3, which ties Dream Child for the fewest after FvJ. It also sits awkwardly next to s03's on-screen superlative | "this Freddy has the biggest body count of them all, even if almost all of it happens before the movie starts" |
| before the movie he has killed almost every child and teenager in his town | RIGHT | W, H, V | |
| silliest Freddy, plays with victims like toys | Opinion, fair | V | |
| turns up Carlos's hearing until one chalkboard scratch kills him | RIGHT | E, H, V (hearing aid) | |
| traps Spencer inside a video game | **MISLEADING, it implies fewer deaths** | Spencer dies (W, E, V). As written, a viewer could think he was only trapped | "traps Spencer inside a video game and kills him there" |
| drops John Doe, the last teenager from Springwood, onto a bed of spikes | RIGHT | W ("only surviving teenager"), E | |
| order Carlos, Spencer, John | RIGHT | E, H | |
| Tracy gets woken up before he can finish her | RIGHT | W, "Tracy is almost killed but is awakened by Maggie" | |
| "All those jokes take time, and in that time" as the cause of Tracy's escape | UNCONFIRMED as cause | No source links her escape to his joking. It is a fair reading of his style but should be framed as the channel's take. Acceptable as narration | |
| Maggie, his daughter, drags him into the real world and shoves a pipe bomb into his chest | RIGHT | W | |

### s06 #5 2010 remake, 38%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| opposite of the last one, dark and serious | Opinion, fair | | |
| staying awake makes your brain drop into his world for seconds without noticing | RIGHT | Microsleeps (W, H) | |
| By the time Nancy figures out who he is, every other kid from their old preschool is dead except her and Quentin | RIGHT, with a small caveat | W, H. Strictly, Nancy learns who he is from Gwen first and then finds out the others are dead. The sentence still holds because they are already dead by then. Optional tighter version on the right | "By the time Nancy tracks down her old preschool class, every other kid from it is dead except her and Quentin" |
| Dean in a diner | RIGHT | W, P, V | |
| Kris in her bedroom | RIGHT | P "on her bed", H "her house", W "accompanied by Jesse" | |
| Jesse in a jail cell | RIGHT | W, P, V | |
| list leaves out Marcus Yeon | Not wrong | The line before covers all the kids as dead, so it does not imply fewer deaths. Marcus is the fourth on-screen death (E, H, V) | |
| Nancy drags him into the real world and cuts his throat | RIGHT | W, V (with Quentin's adrenaline, paper-cutter blade) | |
| comes back through a mirror for her mother | RIGHT | W, P | |
| Staying awake won't save you from this one | Fine, but see section 5 on tone | | |

### s07 #4 New Nightmare, 30%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| stronger and smarter than the last one | RIGHT, matches the stats | STR 8 against 6, INT 8 against 7 | |
| goes after Heather, the actress who played Nancy | RIGHT | W | |
| kills two special effects men working on a new Freddy movie | RIGHT | Chuck and Terry (E, V) | |
| then her husband while he's driving | RIGHT | W | |
| then her son's babysitter in a hospital, dragged up the wall just like Tina | RIGHT | W, E | |
| takes Dylan into his world | RIGHT | W | |
| Heather and Dylan together push him into a furnace | RIGHT | W | |
| only gets four kills | RIGHT | 4 | |
| if he picks you, the people you love go first | **Reason rule problem**, see section 5 | | |

### s08 #3 A Nightmare on Elm Street 1984, 22%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| isn't as strong as the last one | RIGHT, matches the stats | STR 7 against 8 | |
| scariest Freddy of them all, barely talks, stays in the shadows | Opinion, fair | | |
| drags Tina across the ceiling | RIGHT | | |
| strangles Rod with his own bedsheet in a jail cell | RIGHT | W, E | |
| pulls Glen down into his bed | RIGHT | | |
| Nancy sets traps, drags him into the real world, turns her back on him | RIGHT | W | |
| "and even then, he still takes her mother" | MISLEADING, order | Freddy kills Marge **before** Nancy turns her back (W). In the final twist scene Marge is alive and is grabbed through the door window. As written, it sounds like a single death that comes after the back-turn | "and even after that, in the very last scene, he grabs her mother and pulls her through the door window" |
| Unless you're as brave and as smart as Nancy, he gets you | OK, grounded in the film | | |

### s09 #2 Dream Warriors, 12%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| deadlier than the last one | RIGHT, matches the stats | KC 6 against 4 | |
| hunts the last children of Elm Street in a mental hospital | RIGHT | W | |
| Phillip as a puppet with his own veins | RIGHT | W, H, V | |
| smashes Jennifer's head into a TV | RIGHT | | |
| kills Taryn and Will after they find their dream powers | RIGHT | W, V | |
| his skeleton kills Nancy's father in the real world | RIGHT | H, V (possessed bones), W | |
| kills Nancy while pretending to be her dad | RIGHT | W | |
| even the girl who beat the last Freddy | RIGHT | "Last" in playback order is s08, the 1984 Freddy, whom Nancy beat | |
| it still took holy water on his bones to stop him | RIGHT, incomplete | Neil uses holy water **and** a crucifix on the bones, and Nancy also stabs Freddy with his own glove at the same moment (W, H) | Optional: "it still took holy water and a cross on his bones to stop him" |
| kids who survived had superpowers | RIGHT | Kristen, Kincaid, Joey | |

### s10 #1 The Dream Master, 5%
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| strongest of them all, wiped out the Dream Warriors | RIGHT, matches the stats | STR 9, the highest | |
| Kincaid, Joey and Kristen, survivors of the last Freddy, all dead early | RIGHT | W | |
| Sheila, Rick, then Debbie as a crushed cockroach | RIGHT, order RIGHT | W, E | |
| every soul he takes stays trapped inside him | RIGHT | W, V | |
| Alice wins with her dead friends' powers and his reflection, and the souls tear him apart | RIGHT | W | |
| If the kids with superpowers couldn't survive this one, you won't either | MISLEADING, minor | Alice had superpowers and survived, and Dan survived too (W) | see section 5 |

### s11 outro
| Claim | Verdict | Evidence | Fix |
|---|---|---|---|
| from the one who needed Jason, to the one who wiped out the Dream Warriors | RIGHT | | |
| I went through every death in all nine movies | UNCONFIRMED, risky | The cards do not apply one counting rule (see section 4), so this boast invites "you missed X" comments. Keep it only after the cards are fixed | |

---

## 4. KILL COUNT check (stats.json)

Rule: deaths Freddy causes directly, as set out in section 2. The card numbers follow a literal count for 7 films but not for Freddy's Dead (10) or 2010 (6), so **the cards mix two counting systems**.

| Film | Card KC | On-screen present | Flashback shown | Implied before or off screen | Verdict |
|---|---|---|---|---|---|
| Freddy vs. Jason | 1 | 1 (Mark) | 1 (Lori's mother) | possibly the little girl in the prologue, UNCONFIRMED | OK for on-screen present. Total shown is 2 |
| Freddy's Revenge | 8 | about 9 (Schneider, Grady, about 6 party, Kerry). Party number 1 src | 0 | | Close. 9 if you follow E/H. Not provably wrong, since the party count is not confirmed |
| Dream Child | 3 | 3 | 0 | | RIGHT |
| Freddy's Dead | 10 | 3 | 1 to 2 (Loretta, and Underwood 1 src) | nearly every child in Springwood | Card is a "scale" number, not a count. Literal on-screen is 3. If the scale is kept, s05's superlative needs the "before the movie" wording |
| 2010 | 6 | 5 (Dean, Kris, Jesse, Marcus, Gwen) | 0 | all other preschool kids, about 7 named (1 src) | **Matches no rule**. Literal is 5. If implied kills count, it should be higher than 6 |
| New Nightmare | 4 | 4 | 0 | | RIGHT |
| 1984 | 4 | 4 | 0 | 20 children before his death | RIGHT on-screen |
| Dream Warriors | 6 | 6 | 0 | | RIGHT |
| Dream Master | 6 | 6 | 0 | | RIGHT |

Recommendation: either make every card the on-screen count (FvJ 1, FR 9, DC 3, FD 3, 2010 5, NN 4, 1984 4, DW 6, DM 6) and treat Freddy's Dead's massacre as narration only, or keep a 1 to 10 danger scale and label it that way on the card. The ranking does not depend on the card values. Note that s04 "kills fewer than the last one" and s09 "deadlier than the last one" still hold under the on-screen rule.

---

## 5. Survival reason lines: problems and replacements

Owner rule: he is in my room, next to me, coming for me. Odds must come from how dangerous, cruel and strong he is, and from what the film shows of victims who got away.

| Entry | Current line | Problem | Replacement (grounded) |
|---|---|---|---|
| s02, 95% | "If you've never heard his name, he can't even find you." | **Breaks the rule.** This is the banned "he can't find you" type of reason | "And even when he does come for you, he's so weak that Lori keeps waking up from him, pulls him into the real world, and ends up holding his head. Survival rate, ninety-five percent." (Lori survives repeated dream attacks and pulls part of him, then all of him, into reality, W, F) |
| s03, 65% | "Stay far away from Jesse, and you'll probably be fine." | **Breaks the rule** (the banned "stay away from Jesse" reason). The tone also clashes with the line saying he kills the most on screen | "But when he came face to face with Lisa, he couldn't even hurt her, and she walked into his factory alone and beat him, so keep your head and you've got a real shot. Survival rate, sixty-five percent." (W, V) |
| s04, 55% | "He only gets three kills, so if he comes for you, it's close to a coin flip." | Allowed, but rests only on the kill count | "Mark and Yvonne both got pulled out of his dreams alive, but Mark didn't get lucky twice, so if he comes for you, it's close to a coin flip. Survival rate, fifty-five percent." (W, V) |
| s05, 45% | "He's deadly, but he wastes time, and that time is your way out." | OK. It is grounded in Tracy's escape and matches the number | Keep |
| s06, 38% | "Staying awake won't save you from this one." | Not a rule break, but it reads as near-certain death and gives no reason why 38% of people would get out | "Staying awake won't save you from this one, and the only two who made it out had to pump themselves full of adrenaline and fight him together. Survival rate, thirty-eight percent." (W) |
| s07, 30% | "He only gets four kills, but if he picks you, the people you love go first." | **Conditional on being picked**, while the premise is that he is already coming for you. It is also about the people around you, not your own odds | "He only gets four kills, but he tears through everyone around Heather, and even she only gets out by following him into his world and fighting him with her son. Survival rate, thirty percent." (W) |
| s08, 22% | "Unless you're as brave and as smart as Nancy, he gets you." | OK, grounded, and the tone fits | Keep |
| s09, 12% | "You don't have superpowers." | OK | Keep |
| s10, 5% | "If the kids with superpowers couldn't survive this one, you won't either." | Factually loose, because Alice had powers and survived | "Even the kids with superpowers didn't survive this one, and the only one who did had to soak up all her dead friends' powers first. Survival rate, five percent." (W) |

---

## 6. Content limits for the visuals (no suicide acts shown, no nudity, no sexualized minors)

| Script line | Risk in the matching scene | Advice |
|---|---|---|
| s06 "He gets Dean in a diner" | The death shot shows Dean cutting his own throat in reality, which reads as a suicide act (W, P) | Use Freddy in the diner and the dream shots only. No real-world cut |
| s08 "strangles Rod with his own bedsheet" | The death is staged as a suicide hanging (W) | Use the sheet moving by itself, never the hanging body |
| s09 "turns Phillip into a puppet" | It ends with Phillip falling from a ledge, which looks like suicide (V) | Use the vein-strings walk only, not the fall |
| s10 "Kincaid, Joey and Kristen ... are all dead" | Joey's death begins with a nude woman in the waterbed, and Joey is a teen | Do not use Joey's death footage |
| s03 "gym teacher in the showers" | The coach is stripped in the shower scene. This is from memory, not from a fetched source, so it is UNCONFIRMED. Also the gay-bar scene and Jesse walking around naked | Check the clip frames. Use the ropes and the gym equipment shots |
| s06 "their old preschool" | The flashbacks show child abuse, including scenes from Krueger's room | No preschool flashback footage of the children with Krueger |
| not in script | Kristen's wrist cut (DW opening), Tracy burning her wrists on the stove (FD), Bobby's wrists (FvJ flashback), Nancy's bath scenes (1984 and 2010), Gibb's shower (FvJ), and the 2010 dream where Nancy is dressed as a little girl and Freddy talks to her sexually (P) | Keep all of these out of B-roll |

---

## 7. Open doubts

1. The exact number of party deaths in Freddy's Revenge. W only says "several", and E and H (which may be copies of each other) say 6 by Freddy plus 1 trampled. This decides whether the card should say 8 or 9, and the s03 superlative depends on it.
2. Whether Kerry's death on the bus is real or a dream. The film leaves it ambiguous.
3. Gwen's death in 2010 is marked "debatable" by E and H. W and P both say he kills her.
4. In 1984 Marge has two death scenes, one before the back-turn and the twist at the end. I count her as one kill.
5. For FvJ, the possible prologue kill of a little girl and the cause of Bobby Davis's death rest on 1 src each.
6. Underwood's death in the Freddy's Dead flashback is 1 src (V).
7. Dan's real vehicle in Dream Child (truck or motorcycle) is UNCONFIRMED.
8. Not reached: Dead Meat totals, IMDb (blocked), themoviespoiler (no pages), and Plugged In for 7 of the films. None of their numbers are used here.
9. Fan wikis E and H are tagged unreferenced and partly copy each other. Most items rest on W plus V or F, which do not depend on each other.

---

## 8. Review of script_v4_draft.md

Checked against the death and attack lists in section 2 and against the header stats in the new playback order: FvJ, then Revenge, Dream Child, 1984, Dream Warriors, New Nightmare, Freddy's Dead, 2010 and Dream Master. The file was not edited.

Mechanical check: the voiced text in s00 to s11 has no colons and no dashes. The only hyphens are inside words (eighty-four, force-feeds, ninety-five, thirty-five, twenty-five), which is fine. Every banned scene listed in the header has other usable footage for its line. The one leftover risk is the s03 shower, where the coach is stripped (from my memory, UNCONFIRMED), so use the ropes and gym-equipment shots.

### 8.1 Header and KILL COUNT score map
| Film | On-screen kills (section 4) | Score by the header map | Card | Verdict |
|---|---|---|---|---|
| FvJ | 1, plus 1 in a flashback | 1 | 1 | OK |
| Revenge | about 9 (party number 1 src) | 6 | 6 | OK |
| Dream Child | 3 | 3 | 3 | OK |
| 1984 | 4 | 4 | 4 | OK, but see note |
| Dream Warriors | 6 | 5 | 5 | OK |
| New Nightmare | 4 | 4 | 4 | OK |
| Freddy's Dead | 3 on screen, plus a whole town implied | 10 | 10 | OK under the "whole town" rule |
| 2010 | 5 on screen, plus the other preschool kids implied | 5 on screen, 8 only if implied kills count | 8 | **Inconsistent**. 10 or more needs the implied preschool kills, and that number (about 7 named) comes only from the horror fandom wiki. W just says "all of them". And if implied kills count for 2010, the 1984 card should also count the 20 children Marge describes, which would make it 8, not 4. Either set 2010 to 5 (on screen only, with Freddy's Dead as the one stated "whole town" exception), or explain the rule |
| Dream Master | 6 | 5 | 5 | OK |

"Strongest of them all" (s10): Dream Master STR is 8, and so is New Nightmare's. It is a tie, so the superlative does not match the card. **Fix**: make Dream Master STR 9, or change the line to "This Freddy is the most powerful of them all", which DREAM 10 (the only 10) supports.

### 8.2 Line by line (only lines with problems; everything else is RIGHT)

**s00, s01**: no problems.

**s02 FvJ 95%**: no problems. The flashback caveat is now correct (Lori's mother, W, F). The closing "you'll almost certainly wake up" follows the rule and fits 95%, and Lori waking up again and again is in the film.

**s03 Revenge 60%**
1. "and most of the kids at that party got away" is UNCONFIRMED. No source says most guests survived. W only says he "slaughters several partygoers before escaping", and H says the guests were cornered against the fence. **Fix**: "and at that party, he only got a handful of kids before he ran off."
2. "Everyone he caught alone died" is **WRONG**. Freddy came at Lisa alone at her house and could not hurt her (W, V), and Lisa survives. Kerry was not alone, since Jesse and Lisa were on the bus. **Fix**: "Coach Schneider and Grady were trapped alone with him and died, but this is a Freddy you can run from."
3. "beat him with a kiss" is RIGHT in short form. W says she confesses her love and kisses Freddy, Jesse fights back, and Freddy burns.
4. Comparison "far more dangerous than the last one": OK (STR 7 against 5, KILL 6 against 1).

**s04 Dream Child 50%**
1. "Half the people he went after lived and half died" is **MISLEADING**. He went after Dan, Greta, Mark, Yvonne and Alice. Three died (Dan, Greta, Mark) and two lived (Yvonne, Alice). Mark's first escape does not make him a survivor. It is only half and half if you count Jacob, and Freddy uses Jacob rather than hunting him. **Fix**: "Three of the people he went after died, but Alice and Yvonne both got out alive, so this one is close to a coin flip."
2. Comparisons: "kills fewer" (3 against 6), "far smarter" (7 against 3) and "back inside your dreams" (DREAM 7 against 3) are all OK.
3. Yvonne's rescue and Mark being saved once are RIGHT (W).

**s05 1984 35%**
1. "Of the four teenagers he went after, three died" is RIGHT (Tina, Rod and Glen died, Nancy lived). But the number does not match the card. One in four is 25%, yet the card says 35%. And in s06, Dream Warriors says six of ten died, so four in ten lived (40%), yet its card says 25%. The fractions run backwards against the ranking, and a careful viewer will notice. **Fix** (closing line): "So there is a way to beat this one with no powers at all, and that's more than you can say for most of the Freddys still to come." Keep "three died" if you want it, but drop "only one kid in four".
2. "takes Nancy's mother right in front of her" is RIGHT (W, Marge smothered in the bed while Nancy and Don watch).
3. "scarier than the last one": no stat card measures scary. The stats do show 1984 above Dream Child on STR, KILL and DREAM. This is acceptable as opinion. If you want it tied to the cards: "This Freddy is stronger and scarier than the last one, because..."

**s06 Dream Warriors 25%**
1. "Six of the ten people he went after died" is RIGHT only if Neil counts as someone he went after. The skeleton knocks Neil out (W "incapacitates Neil"). The 6 dead are Phillip, Jennifer, Taryn, Will, Don and Nancy. The 4 who lived are Kristen, Joey, Kincaid and Neil. See the fraction clash in s05.
2. "the ones who lived had dream powers and a friend pouring holy water on his bones": Neil lived without powers, and he is the one pouring the water. This is acceptable as written.
3. "You don't have superpowers." followed by the survival line is a **choppy short pair**. **Fix**: "Six of the ten people he went after died, and the four who lived had dream powers or a friend pouring holy water on his bones, and you've got neither."
4. "even the girl who beat the last Freddy": RIGHT. The previous entry is 1984, and Nancy beat him.

**s07 New Nightmare 20%**
1. "Nobody he went for got away from him until Heather followed him into his world" is **WRONG**. Heather got away from him again and again before the climax, and Chase survived a first attack in her opening dream (W). **Fix**: "Four people around Heather died, and the only two who lived, Heather and Dylan, had to face him in his own world and push him into a furnace together."
2. "stronger and scarier than the last one": STR 8 against 6 is OK. Dropping "smarter" was correct, since INT is 7 against 8.
3. "There are no powers and no holy water this time": RIGHT. It refers back to the previous entry, Dream Warriors, which is now the right one.

**s08 Freddy's Dead 15%**
1. "Then he plays with the few who are left like toys" is MISLEADING. Carlos and Spencer are runaways from a shelter outside Springwood (W), not the few kids left in town. **Fix**: "Then he plays with the kids who wander back into town like toys."
2. "Tracy only lives because Maggie wakes her up in time" is MISLEADING, minor. She also survives a later attack by waking herself (V, 1 src, a stove burn on her wrists, which must not be shown) and survives the final fight. **Fix**: "Tracy lives because Maggie wakes her up in time."
3. The body count line, the town line, the Carlos, Spencer and John line, and the pipe bomb are all RIGHT. Spencer's death is now stated.
4. Closing line: it follows the rule. "you won't either" is strong for 15%, but acceptable in this Slaughtered tier.

**s09 2010 10%**
1. Facts are all RIGHT, and so is "the opposite of the last one" (Freddy's Dead is silly, 2010 is serious). "only two kids lived" is RIGHT (W). Marcus is not named, but "every other kid ... is dead" covers him, so nothing implies fewer deaths.
2. "they had to pump themselves full of adrenaline": Quentin stole the adrenaline and injected Nancy with it (W, H). This is close enough. A stricter version would be "and they needed stolen adrenaline and each other to fight him".
3. KILL 8: see 8.1.

**s10 Dream Master 5%**
1. "strongest of them all": see 8.1 (STR tie with New Nightmare).
2. "You don't stand a chance." followed by the survival line is a **choppy short pair**. "Don't stand a chance" is also absolute for 5%. **Fix**: "Even the kids with superpowers died, and the only one who beat him had to take all of their powers first, so you've barely got a chance."
3. Everything else is RIGHT, including that Kincaid, Joey and Kristen beat him in Dream Warriors.

**s11**: the facts are right. As before, "I went through every death in all nine movies" is only safe once the 2010 and 1984 card rule is settled.
