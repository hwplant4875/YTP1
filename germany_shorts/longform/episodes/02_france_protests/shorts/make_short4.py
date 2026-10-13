"""STRATA France Short #4: 'Teens hurt by police weapons' (factual; no injury imagery). Writes short4.json.
Facts: research.md 1.2/3.x via lines.py: Saint-Ouen-l'Aumône 28 Sept (14, jaw broken by a tear-gas round at close
range; prosecutor says he struck a policewoman first; officer charged 6 Oct), Tours 30 Sept (16, lost the use of an eye,
consistent with an LBD round per the prosecutor), Lens 5 Oct (15, lost his hand to a police grenade), stun grenades
suspended at lycée protests on 7 Oct. Visuals: maps, weapon objects (3D, no people), real police/protest photos, signs."""
from common import Short, P, ph, v2, news, cc, d3, MUSIC, HIT

s = Short(4, "FRANCE · LYCÉE PROTESTS")
s.line("At France's school protests, police weapons have left teenagers badly hurt.", [
    P(news("ap_police_line"), cap="TEENS *HURT*\nBY POLICE\nWEAPONS", col="red"),
    P(d3("weapons", "lineup"), at="police weapons", start=1.5),
    P(ph(456), at="teenagers", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(87, [
    P(d3("map", "cases"), start=0.4, cap="28 SEPT\n*SAINT-OUEN-\nL'AUMÔNE*", col="red"),
    P(ph(511), at="northwest", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(d3("weapons", "gas"), at="A fourteen", cap="*AGE 14*\nJAW BROKEN", col="red"),
    P(d3("weapons", "close_range"), at="tear-gas round", start=2.0, cap="TEAR-GAS ROUND\nAT *CLOSE*\n*RANGE*", col="red")])
s.lf(88, [
    P(ph(522), cap="PROSECUTOR:\nHE HIT AN\nOFFICER *FIRST*", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(301), at="On October sixth", cap="6 OCT:\nOFFICER\n*CHARGED*", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(516), at="who fired", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])])
s.lf(89, [
    P(d3("map", "cases_fly"), start=0.5, cap="30 SEPT\n*TOURS*", col="red"),
    P(ph(461), at="A sixteen", cap="*AGE 16*\nLOST THE USE\nOF AN EYE", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(d3("weapons", "lbd"), at="The prosecutor", cap="PROSECUTOR:\nAN *LBD* ROUND", col="red"),
    P(ph(514), at="LBD round", kb=[1.04, 0.5, 0.5, 1.12, 0.5, 0.5])])
s.lf(90, [
    P(ph(463), cap="5 OCT\n*LENS*", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(d3("weapons", "grenade"), at="A fifteen", cap="*AGE 15*\nLOST HIS HAND", col="red"),
    P(ph(520), at="police grenade", kb=[1.04, 0.5, 0.45, 1.12, 0.5, 0.4])])
s.lf(92, [
    P(d3("weapons", "suspended"), cap="7 OCT\nSTUN GRENADES\n*SUSPENDED*", col="blue"),
    P(ph(518), at="at lycée protests", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])])
s.end(sfx=HIT)
s.write(MUSIC["lightless"], "Teenagers Hurt at France's School Protests #shorts",
        "Three cases changed the debate: a 14-year-old's jaw broken by a tear-gas round, a 16-year-old who lost the use "
        "of an eye, a 15-year-old who lost his hand to a police grenade. On 7 October France suspended stun grenades at "
        "lycée protests.")
