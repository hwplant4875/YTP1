# STRATA #02 France lycée protests — shot list (v2)

Narration estimate 12.8 min at 150 wpm. 3D: 66 shots over 88 beats ≈ 7.7 min (60%). 3D + 2D graphics ≈ 88% of runtime; news clips ≈ 5%; the rest CC photos.
**No 3D shot is used twice.** The map scene appears in 14 different shots, each with different content (different camera, data and highlight). Highlights are amber (#FFB25C); people are faceless mannequins; no red arrows or circles (the only red is the official "red lycée" category in `france_map red_orange`).
Render: `node render.mjs scenes/<scene>.js OUT --shot <shot>[:seconds]`. Every shot stretches with `name:seconds`. Machine-readable list: `shots3d.json`.

Status: **NEW** = built in this pass, **FIXED** = existing shot reworked, **existing** = unchanged.

| # | Narration (start) | Visual | Status |
|---|---|---|---|
| 1 | In France right now, teenagers are blockading their own schools. | NEWS CLIP ≤5s (AP, pupils dragging bins), as script |  |
| 2 | With bins. With barriers. With human chains. | **3D** `france_lycee outside_blockade` — gate barricade of wheelie bins + barriers, faceless pupils with readable placards, amber glow on the chained gate | FIXED |
| 3 | On October sixth, police counted about a quarter of a million people i… | 2D: dot crowd + counter 250,000 POLICE |  |
| 4 | Organisers say it was four hundred and fifty thousand. | 2D: dot field grows, 450,000 ORGANISERS |  |
| 5 | More than six thousand eight hundred people have been taken into polic… | 2D: 6,877 icons, 86% amber |  |
| 6 | One fifteen-year-old lost his hand. | 2D: black 0.8 s, then CC photo (blurred march) |  |
| 7 | And it all started with a few empty classrooms, in one school outside … | **3D** `france_map spark` — drop from high to one amber point at Créteil | existing |
| 8 | What are these teenagers so angry about? | CC photo: Paris placards 6 Oct (FreCha) |  |
| 9 | Why are so many of them ending up hurt, or in custody? | **3D** `france_police standoff` — behind pupils toward a shield line in amber haze (replaces the red-tinted 2D silhouette) | NEW |
| 10 | And can the government calm it down, before the next wave? | **3D** `france_calendar teaser` — calendar rail, 13/17/23/27 Oct and 5 Nov flick past | NEW |
| 11 | *(title card, no VO)* | 2D: title card |  |
| 12 | This is what's happening in France's high schools, as of today. | **3D** `france_map creteil_hold` — held framing on the Créteil dot | existing |
| 13 | Créteil [kray-TAY]. A suburb just southeast of Paris. | **3D** `france_map creteil_hold` — held framing on the Créteil dot | existing |
| 14 | Lycée Saint-Exupéry [LEE-say san-teg-zoo-pay-REE]. About fifteen hundr… | **3D** `france_lycee exterior` — night, street level, slow push on the intact façade; LYCÉE lettering warms to amber | NEW |
| 15 | A lycée is a French high school, for fifteen- to eighteen-year-olds. | 2D: age bar 15→18, LYCÉE = HIGH SCHOOL |  |
| 16 | At the start of this school year, several teaching posts there were si… | **3D** `france_lycee three_empty` — dollhouse cutaway, three teacher desks in three rooms light amber one by one | NEW |
| 17 | So in mid-September, the teachers went on strike. | **3D** `france_calendar sept17` — calendar tile 17 SEPT teachers strike | NEW |
| 18 | The next day, the pupils joined in, their own way. They blocked the ga… | **3D** `france_lycee bins_slide` — dawn, bins slide in from the street one after another and build the barricade, amber on the chain | NEW |
| 19 | A few days later, two MPs from the radical-left party La France Insoum… | **3D** `france_phone posts` — two phones with generic post layouts dated 21 SEPT, amber underline | NEW |
| 20 | Remember that visit. The government will. | **3D** `france_phone posts` — two phones with generic post layouts dated 21 SEPT, amber underline | NEW |
| 21 | Then, on September twenty-fourth, a rap-news outlet called Booska-P [B… | **3D** `france_phone viral` — blurred faceless vertical video, caption, counter to 1.5M | NEW |
| 22 | They talked about feeling abandoned, as kids from the banlieue [bahn-L… | **3D** `france_phone viral` — blurred faceless vertical video, caption, counter to 1.5M | NEW |
| 23 | On TikTok, the clip was watched around one and a half million times. | **3D** `france_phone viral` — blurred faceless vertical video, caption, counter to 1.5M | NEW |
| 24 | And the idea spread with it. If your school is falling apart... block … | **3D** `france_map spread` — Créteil → suburbs → cities → 1 Oct flood (labels no longer overlap) | FIXED |
| 25 | By September twenty-fifth, around sixty schools in the Paris region we… | **3D** `france_map spread` — Créteil → suburbs → cities → 1 Oct flood (labels no longer overlap) | FIXED |
| 26 | Three days later, the Interior Ministry counted one hundred and eighty… | **3D** `france_map spread` — Créteil → suburbs → cities → 1 Oct flood (labels no longer overlap) | FIXED |
| 27 | And on October first... one thousand and twenty-seven. | **3D** `france_map spread` — Créteil → suburbs → cities → 1 Oct flood (labels no longer overlap) | FIXED |
| 28 | That's more than a quarter of all the lycées in France. | 2D: 3,700-school grid, 1,027 amber |  |
| 29 | Teenagers don't shut down a thousand schools over one viral video. | **3D** `france_lycee cut` — amber slice line opens the façade into the cutaway | existing |
| 30 | So what's actually going on inside these buildings? | **3D** `france_lycee cut` — amber slice line opens the façade into the cutaway | existing |
| 31 | Let's walk inside a typical French lycée. | **3D** `france_lycee hall` — glide through the glass entrance doors into the hall, amber light lands on the stairs | NEW |
| 32 | First, the building. On average, it's sixty-five years old. | **3D** `france_lycee facade_age` — rust streaks and cracks creep over the concrete, one long crack glows amber | NEW |
| 33 | More than half of France's lycées were built before 1970. | **3D** `france_lycee toilets` — broken toilet block, taped HORS SERVICE stall picked out in amber | existing |
| 34 | Pupils describe rats, cockroaches, and ceilings that have come down. | **3D** `france_lycee leak` — stained ceiling, missing tile, drips, rat | existing |
| 35 | In summer, teachers report classrooms at thirty-five to forty degrees.… | **3D** `france_lycee heat` — thermometer climbs to 38 °C in low amber sun | existing |
| 36 | A Senate report says fixing them would take about one and a half billi… | **3D** `france_money repair_need` — coin stacks 2026→2050, "€1.5 BN needed every year" | NEW |
| 37 | But for most pupils, the building isn't the biggest problem. It's who'… | **3D** `france_lycee empty_desk` — amber pool on an empty teacher desk | existing |
| 38 | This September, France's biggest secondary teachers' union surveyed ov… | 2D: 1,033 school icons, SNES-FSU source line |  |
| 39 | Fifty-three percent were missing at least one teacher. | **3D** `france_staffroom staffroom` — empty staff room, blank name tags glow amber | NEW |
| 40 | The ministry disputes that. It says more than ninety-six percent of se… | 2D: split screen UNION 53% vs MINISTRY 96.1% |  |
| 41 | But by the ministry's own count, in 2024 to 2025, ten percent of lycée… | **3D** `france_timetable lost_lessons` — timetable, 1 in 10 slots flip to amber gaps | NEW |
| 42 | One pupil told Euronews they'd gone six months without a teacher, in a… | CC photo: Paris placards, Ken Burns + quote card |  |
| 43 | And when teachers are there, classrooms are packed. A teacher in Marse… | **3D** `france_lycee crowded` — 37 desks light up one by one, the 37th pupil squeezed in by the board flares last | FIXED |
| 44 | French lycée students also spend around twelve hundred hours a year in… | **3D** `france_timetable hours` — slab stacks 60 vs 48 (×20 h), "+240 h" | NEW |
| 45 | And at the end of all that, there's Parcoursup [par-koor-SOOP], the na… | **3D** `france_parcoursup dashboard` — generic admissions dashboard, amber cursor | NEW |
| 46 | This summer, eighteen percent of applicants got no offer at all in the… | **3D** `france_parcoursup cascade` — 100 application cards flip, 18 "NO OFFER" | NEW |
| 47 | Then, on October first, the government published its budget for 2027. | **3D** `france_state assemblee` — Assemblée portico at night, budget beat | NEW |
| 48 | Education spending goes up, by about one point two billion euros. | 2D: bar +€1.2bn |  |
| 49 | But the same budget cuts one thousand five hundred and eighty-eight te… | **3D** `france_staffroom tags_fall` — teacher name tags drop out leaving amber gaps | NEW |
| 50 | The government points to about a hundred and eighty thousand fewer pup… | 2D: caption −180,000 pupils expected |  |
| 51 | The budget landed on the very day the protests hit their most violent … | **3D** `france_calendar oct1` — calendar 1 OCT tile | NEW |
| 52 | And that day, the map of France caught fire. | **3D** `france_map ignite` — low oblique over France, 180 → 1,027 lycées ignite in a rush | NEW |
| 53 | Here's how fast it moved. | **3D** `france_map tour` — day-by-day flight, named cities light (Saint-Denis … Strasbourg) | NEW |
| 54 | First, the suburbs north and east of Paris. Saint-Denis. Sarcelles. La… | **3D** `france_map tour` — day-by-day flight, named cities light (Saint-Denis … Strasbourg) | NEW |
| 55 | Then Marseille. Lille. Lyon [lee-OHN]. | **3D** `france_map tour` — day-by-day flight, named cities light (Saint-Denis … Strasbourg) | NEW |
| 56 | Then Nantes. Rennes. Bordeaux. Toulouse. Strasbourg. | **3D** `france_map tour` — day-by-day flight, named cities light (Saint-Denis … Strasbourg) | NEW |
| 57 | On October first, the Interior Ministry counted one thousand nine hund… | 2D: arrest counter 1,949 |  |
| 58 | Two hundred and twenty-two lycées were fully blockaded. | **3D** `france_map blockaded` — 1,027 dim, 222 turn solid amber | NEW |
| 59 | In Nantes, a fire destroyed a lycée's entrance hall. | **3D** `france_aftermath nantes` — burned entrance hall, soot, tape, embers (generic, no real school) | NEW |
| 60 | In Marseille, a firefighters' truck was torched, and the city shut dow… | **3D** `france_aftermath marseille` — burned generic fire truck, bus shelter "NETWORK SUSPENDED" | NEW |
| 61 | The movement even crossed the border, into schools in Belgium, and the… | **3D** `france_map border` — amber arcs Lille → Charleroi, Liège (Belgium) and Lyon → Italy | NEW |
| 62 | On October second, prefects closed around four hundred lycées, and ban… | **3D** `france_map padlocks` — ~400 amber padlocks pop over lit lycées | NEW |
| 63 | The message from the state was clear. Stay home. | **3D** `france_map padlocks` — ~400 amber padlocks pop over lit lycées | NEW |
| 64 | The pupils answered with a date. Tuesday, October sixth. | **3D** `france_calendar oct6` — 6 Oct police counts as glowing columns | NEW |
| 65 | In Paris, the march left Place de la République [ray-poob-LEEK] at two… | CC photo: République monument + 2D route line |  |
| 66 | About two thousand police and gendarmes were deployed, with motorbike … | CC photo: CRS on boulevard Voltaire |  |
| 67 | Police counted fifty-six thousand people in Paris. Organisers said a h… | 2D: bars 56,000 vs 100,000 |  |
| 68 | In Lyon, twenty thousand, by police count. In Toulouse, thirteen and a… | **3D** `france_map oct6` — 6 Oct police counts as glowing columns | existing |
| 69 | And this time, it wasn't just the suburbs. | NEWS CLIP ≤5s: AP Paris cortège |  |
| 70 | Pupils from Louis-le-Grand and Henri-IV, two of the most elite schools… | CC photo: Louis-le-Grand blockade |  |
| 71 | The placards said a lot. | CC photo set: Paris placards, slow pan |  |
| 72 | "Too young to be listened to, but not too young to be clubbed." | 2D: quote card |  |
| 73 | And in Perpignan [pair-pee-NYAHN], one banner read: "Sorry for the tro… | CC photo: Perpignan banner |  |
| 74 | Across France: about a quarter of a million marchers, police say. Four… | 2D: bars 250,000 vs 450,000 |  |
| 75 | By evening, there was tear gas, at least four hundred and eighty-eight… | NEWS CLIP ≤5s: Reuters tear gas + counter |  |
| 76 | Outside parliament, Prime Minister Sébastien Lecornu [say-bas-TYAN luh… | NEWS CLIP ≤5s: Lecornu outside the Assemblée |  |
| 77 | Headteachers' unions called it "a complete cacophony". | 2D: quote card |  |
| 78 | Because by then, one question was dominating the news. | 2D: fade to black |  |
| 79 | Why were teenagers getting hurt? | 2D: black + amber line |  |
| 80 | First, the tools. | **3D** `france_weapons lineup` — three stylised intermediate weapons on plinths | NEW |
| 81 | French police use what they call "intermediate weapons". | **3D** `france_weapons lineup` — three stylised intermediate weapons on plinths | NEW |
| 82 | The LBD, a launcher that fires rubber projectiles. | **3D** `france_weapons lbd` — LBD with dotted projectile path | NEW |
| 83 | Launchers that fire tear-gas grenades. | **3D** `france_weapons gas` — tear-gas launcher, canister arc | NEW |
| 84 | And dispersal and stun grenades, which explode, some scattering rubber… | **3D** `france_weapons grenade` — grenade, abstract radial pellet burst | NEW |
| 85 | On October second, Interior Minister Laurent Nuñez [loh-RAHN noon-YEZ]… | NEWS CLIP ≤5s: Nuñez interview |  |
| 86 | Then came three cases that changed the conversation. | **3D** `france_map cases` — three amber pins drop: Saint-Ouen-l'Aumône 28 SEPT, Tours 30 SEPT, Lens 5 OCT | NEW |
| 87 | September twenty-eighth. Saint-Ouen-l'Aumône [san-TWAN loh-MOHN], nort… | **3D** `france_weapons close_range` — launcher with amber CLOSE RANGE bracket | NEW |
| 88 | Prosecutors say he had struck a policewoman first. On October sixth, t… | 2D: two-line text card |  |
| 89 | September thirtieth. Tours [TOOR]. A sixteen-year-old loses the use of… | **3D** `france_map cases_fly` — low flight Tours pin → Lens pin | NEW |
| 90 | October fifth. Lens [LAHNSS], in the far north. A fifteen-year-old los… | **3D** `france_map cases_fly` — low flight Tours pin → Lens pin | NEW |
| 91 | A police source says he had picked it up to throw it back. The prosecu… | 2D: three-line attributed text card |  |
| 92 | Two days later, Nuñez suspended stun grenades at lycée protests, "unti… | **3D** `france_weapons suspended` — grenade under a glass case, SUSPENDED · 7 Oct | NEW |
| 93 | The police watchdog, the IGPN [I-G-P-N], now has twenty-four investiga… | 2D: 24 case folders |  |
| 94 | Amnesty International, UNICEF France and the UN human rights office ha… | 2D: three text tags |  |
| 95 | But the violence hasn't gone one way. | **3D** `france_police behind_line` — behind police helmets toward pupils with placards | NEW |
| 96 | By the interior minister's count on October seventh, seven hundred and… | 2D: 761 officer icons |  |
| 97 | Along with two hundred and fifteen pupils, and eighty-nine school staff. | 2D: +215 pupils, +89 staff |  |
| 98 | In Belfort [bel-FOR], a plain-clothes police officer was beaten uncons… | CC photo: Belfort 6 Oct |  |
| 99 | Headteachers have been hit by fireworks. | **3D** `france_lycee firework` — night, from the yard: a firework streak arcs over the barricade and bursts in sparks | NEW |
| 100 | No one has died. | 2D: black, silence |  |
| 101 | So far, two thousand three hundred and seventy-six people have been pr… | 2D: 6,877 → 2,376 |  |
| 102 | So who does the government blame? And what is it actually offering? | **3D** `france_state matignon` — Matignon façade, one office window goes amber | NEW |
| 103 | Its first answer was political. | **3D** `france_state matignon` — Matignon façade, one office window goes amber | NEW |
| 104 | The prime minister's office called the movement an operation organised… | 2D: quote card (Matignon, 1 Oct) |  |
| 105 | Remember those two MPs in Créteil? | 2D: callback card "21 SEPT · two MPs visit" (no 3D re-use) |  |
| 106 | But the newspaper Le Monde [luh MOHND] read the intelligence note behi… | **3D** `france_state dossier` — redacted note, "outsiders" ×6 vs "LFI" ×1 highlighted (ILLUSTRATION tag) | NEW |
| 107 | It covered one area, and a few days. It mentioned outsiders six times.… | **3D** `france_state dossier` — redacted note, "outsiders" ×6 vs "LFI" ×1 highlighted (ILLUSTRATION tag) | NEW |
| 108 | The party denies organising anything, and accuses the government of co… | 2D: text card, LFI response |  |
| 109 | Lecornu has also said the voice of high-school students is precious, a… | 2D: quote card (Lecornu, on X) |  |
| 110 | Then came the offer. On October eighth, Education Minister Édouard Gef… | NEWS CLIP ≤5s: Geffray on TV |  |
| 111 | Three thousand teachers, he said, would arrive within hours. | **3D** `france_teachers standby` — rows of teachers on standby, amber lamps, front rows step forward | NEW |
| 112 | Three thousand and twenty-four supply teachers, already on the payroll… | **3D** `france_teachers standby` — rows of teachers on standby, amber lamps, front rows step forward | NEW |
| 113 | They're going to the schools hit hardest: a hundred and fourteen "red"… | **3D** `france_map red_orange` — 114 red + ~400 orange lycées (official categories) | existing |
| 114 | One pupil association called it a first concrete announcement. | 2D: text tag "Les Lycéens" |  |
| 115 | Others weren't convinced. A seventeen-year-old in Nantes told France 2… | 2D: quote card |  |
| 116 | And critics asked the obvious question. If three thousand teachers wer… | **3D** `france_teachers drop` — teachers descend on amber threads onto red/orange school blocks | NEW |
| 117 | Geffray admitted they hadn't been assigned. | 2D: text card |  |
| 118 | Then there's the damage. Twenty-four lycées have been burned or ransac… | **3D** `france_aftermath ransacked` — ransacked classroom, overturned desks, fire light | NEW |
| 119 | About thirty thousand pupils have no classes in person. | **3D** `france_teachers empty_field` — field of empty desks, one amber hero desk | NEW |
| 120 | Local officials say many of the fires were set by masked outsiders, no… | CC photo: pupils at a bin fire |  |
| 121 | The government's estimate of the bill: at least thirty million euros. | **3D** `france_money damage_bill` — note-brick pile, "≥ €30 MILLION" | NEW |
| 122 | So it's pushing a law nicknamed "casseurs-payeurs" [kah-SUR pay-YUR]. … | 2D: title "CASSEURS-PAYEURS / RIOTERS PAY" |  |
| 123 | Anyone in a group that causes damage could be made to pay up to ten th… | **3D** `france_money fine` — ten faceless pupils, €10,000 tags drop | NEW |
| 124 | And the public? In a poll for Le Figaro, sixty-two percent said the mo… | 2D: 62% donut |  |
| 125 | But seventy-eight percent also said La France Insoumise was exploiting… | 2D: 78% donut |  |
| 126 | So where does it go from here? | 2D: calendar strip slides in |  |
| 127 | Right now, the blockades are shrinking. | **3D** `france_map dimming` — 1,027 lit lycées go dark until 141 remain | NEW |
| 128 | On October first, more than a thousand lycées were affected. On Octobe… | **3D** `france_map dimming` — 1,027 lit lycées go dark until 141 remain | NEW |
| 129 | A government source calls it a clear slowdown. Pupil unions say it's n… | 2D: split text GOVERNMENT / PUPILS |  |
| 130 | Here's the calendar. | **3D** `france_calendar wall` — calendar full wall, NOW line at 11 Oct | NEW |
| 131 | Tuesday, October thirteenth. A national strike and day of action, call… | **3D** `france_calendar oct13` — 13 OCT lights amber | NEW |
| 132 | Saturday the seventeenth. A separate call that's been spreading on Tik… | **3D** `france_phone anon` — phone, anonymous call "SATURDAY 17 OCTOBER" | NEW |
| 133 | It's not an official union date. But some lycée protesters have said t… | **3D** `france_calendar oct17` — 17 OCT dashed outline + autumn holiday band unrolling | NEW |
| 134 | That same weekend, the autumn school holidays begin. Unions worry two … | **3D** `france_calendar oct17` — 17 OCT dashed outline + autumn holiday band unrolling | NEW |
| 135 | October twenty-third. The government's online consultation for pupils … | **3D** `france_calendar oct23_27` — 23 + 27 OCT | NEW |
| 136 | October twenty-seventh. The rioters-pay bill goes to the Senate. | **3D** `france_calendar oct23_27` — 23 + 27 OCT | NEW |
| 137 | By the end of October, Lecornu has promised decisions, and changes to … | **3D** `france_calendar nov5` — END OCT bracket, 5 NOV | NEW |
| 138 | And on November fifth, France's five biggest union confederations stri… | **3D** `france_calendar nov5` — END OCT bracket, 5 NOV | NEW |
| 139 | And behind all of it, a presidential election in April 2027. | **3D** `france_calendar apr2027` — rail extends to APR 2027 | NEW |
| 140 | In mid-September, this was about a few empty posts, at one school in C… | **3D** `france_map ripple` — holds on the Créteil dot, then an amber wave runs over the whole country | NEW |
| 141 | Now, it's a question for the whole country. | **3D** `france_map ripple` — holds on the Créteil dot, then an amber wave runs over the whole country | NEW |
| 142 | What does France owe the teenagers sitting in its classrooms? | CC photo: human chain at Nation, slow push |  |
| 143 | We'll keep following this story on the thirteenth, and after. If you'd… | 2D: end card |  |

## 3D shots in order

| Beats | Scene | Shot | Base s | Hint s |
|---|---|---|---|---|
| 2 | france_lycee | outside_blockade | 7 | 3.2 |
| 7 | france_map | spark | 8 | 6.0 |
| 9 | france_police | standoff | 7 | 5.1 |
| 10 | france_calendar | teaser | 6 | 4.8 |
| 12,13 | france_map | creteil_hold | 8 | 8.3 |
| 14 | france_lycee | exterior | 8 | 3.2 |
| 16 | france_lycee | three_empty | 7 | 6.0 |
| 17 | france_calendar | sept17 | 5 | 3.6 |
| 18 | france_lycee | bins_slide | 7 | 6.0 |
| 19,20 | france_phone | posts | 7 | 10.3 |
| 21,22,23 | france_phone | viral | 9 | 17.9 |
| 24,25,26,27 | france_map | spread | 6 | 20.2 |
| 29,30 | france_lycee | cut | 8 | 8.3 |
| 31 | france_lycee | hall | 8 | 3.2 |
| 32 | france_lycee | facade_age | 7 | 3.9 |
| 33 | france_lycee | toilets | 6 | 4.3 |
| 34 | france_lycee | leak | 7 | 4.3 |
| 35 | france_lycee | heat | 6 | 8.0 |
| 36 | france_money | repair_need | 8 | 7.1 |
| 37 | france_lycee | empty_desk | 6 | 6.3 |
| 39 | france_staffroom | staffroom | 8 | 3.6 |
| 41 | france_timetable | lost_lessons | 7 | 8.0 |
| 43 | france_lycee | crowded | 6 | 8.3 |
| 44 | france_timetable | hours | 8 | 9.5 |
| 45 | france_parcoursup | dashboard | 7 | 8.0 |
| 46 | france_parcoursup | cascade | 8 | 8.8 |
| 47 | france_state | assemblee | 7 | 4.8 |
| 49 | france_staffroom | tags_fall | 7 | 5.5 |
| 51 | france_calendar | oct1 | 5 | 6.0 |
| 52 | france_map | ignite | 6 | 3.9 |
| 53,54,55,56 | france_map | tour | 12 | 12.6 |
| 58 | france_map | blockaded | 6 | 3.6 |
| 59 | france_aftermath | nantes | 8 | 3.9 |
| 60 | france_aftermath | marseille | 8 | 7.5 |
| 61 | france_map | border | 7 | 5.5 |
| 62,63 | france_map | padlocks | 7 | 9.9 |
| 64 | france_calendar | oct6 | 4 | 3.9 |
| 68 | france_map | oct6 | 6 | 6.0 |
| 80,81 | france_weapons | lineup | 8 | 5.1 |
| 82 | france_weapons | lbd | 6 | 3.6 |
| 83 | france_weapons | gas | 6 | 2.4 |
| 84 | france_weapons | grenade | 6 | 4.8 |
| 86 | france_map | cases | 7 | 3.6 |
| 87 | france_weapons | close_range | 6 | 8.3 |
| 89,90 | france_map | cases_fly | 9 | 15.9 |
| 92 | france_weapons | suspended | 6 | 6.3 |
| 95 | france_police | behind_line | 7 | 3.2 |
| 99 | france_lycee | firework | 6 | 2.8 |
| 102,103 | france_state | matignon | 7 | 7.5 |
| 106,107 | france_state | dossier | 8 | 11.9 |
| 111,112 | france_teachers | standby | 8 | 10.7 |
| 113 | france_map | red_orange | 6 | 8.0 |
| 116 | france_teachers | drop | 8 | 7.5 |
| 118 | france_aftermath | ransacked | 7 | 4.8 |
| 119 | france_teachers | empty_field | 7 | 3.9 |
| 121 | france_money | damage_bill | 7 | 4.8 |
| 123 | france_money | fine | 7 | 9.9 |
| 127,128 | france_map | dimming | 7 | 11.1 |
| 130 | france_calendar | wall | 5 | 1.5 |
| 131 | france_calendar | oct13 | 5 | 6.8 |
| 132 | france_phone | anon | 6 | 8.8 |
| 133,134 | france_calendar | oct17 | 6 | 13.5 |
| 135,136 | france_calendar | oct23_27 | 6 | 7.9 |
| 137,138 | france_calendar | nov5 | 6 | 12.7 |
| 139 | france_calendar | apr2027 | 7 | 4.8 |
| 140,141 | france_map | ripple | 7 | 9.5 |

Every built 3D shot is placed exactly once. Beat 105 (callback to the phone posts) is a 2D card on purpose, so the phone shot is not reused.
