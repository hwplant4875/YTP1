"""STRATA France Short #5: 'The 3,000 teachers'. Writes short5.json.
Facts: research.md 5.2 via lines.py: 8 Oct, Education Minister Édouard Geffray on TF1: 3,024 supply teachers, already
on the payroll but not assigned to classes; 'Les Lycéens' called it a first concrete announcement; a 17-year-old in
Nantes to France 24: 'We don't want words. We want action.'; Lecornu promised decisions and budget changes by the end
of October. (Replaces the suggested 'what happens next' angle: on 13 Oct its first date is already today.)"""
from common import Short, P, ph, v2, news, cc, d3, MUSIC, HIT

s = Short(5, "FRANCE · LYCÉE PROTESTS")
s.line("France promised its protesting pupils three thousand teachers, within hours.", [
    P(ph(14), cap="*3,000*\nTEACHERS,\nWITHIN HOURS", col="green", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5]),
    P(ph(490), at="three thousand", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(110, [
    P(ph(353), cap="THEN CAME\nTHE *OFFER*", col="green", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(news("franceinfo_geffray"), at="Education Minister", cap="8 OCT\n*PRIME-TIME TV*", col="green")])
s.lf(112, [
    P(d3("staffroom", "tags_fall"), cap="*3,024*\nSUPPLY\nTEACHERS", col="green"),
    P(d3("timetable", "lost_lessons"), at="already on the payroll", cap="ALREADY *PAID*,\nNOT ASSIGNED", col="green"),
    P(v2("moliere_classroom"), at="not assigned", kb=[1.04, 0.5, 0.6, 1.14, 0.5, 0.5])])
s.lf(114, [
    P(ph(46), cap="\"A FIRST\n*CONCRETE*\nANNOUNCEMENT\"", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(10), at="concrete", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(115, [
    P(ph(410), cap="OTHERS\nWEREN'T\n*CONVINCED*", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(cc("Lycée_Louis-le-Grand_in_Paris_82"), at="A seventeen", start=2.0),
    P(ph(404), at="We don't want", cap="\"WE DON'T WANT\nWORDS. WE WANT\n*ACTION*.\"", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(116, [
    P(v2("dorian_classroom"), cap="WHY NOT IN\nCLASSROOMS\n*ALREADY*?", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(6), at="If three", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(v2("lucie_aubrac_corridor"), at="why weren't", kb=[1.03, 0.5, 0.5, 1.16, 0.5, 0.5])])
s.lf(117, [
    P(ph(453), cap="MINISTER:\nTHEY WEREN'T\n*ASSIGNED*", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(137, [
    P(d3("calendar", "oct23_27"), cap="END OF OCT:\n*DECISIONS*\nPROMISED", col="blue"),
    P(ph(492), at="and changes", cap="AND *BUDGET*\nCHANGES", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.end(sfx=HIT)
s.write(MUSIC["interloper"], "France Found 3,000 Teachers Overnight. The Catch? #shorts",
        "On 8 October, France's education minister promised 3,000 teachers for protesting lycées within hours: 3,024 "
        "supply teachers who were already on the payroll but not assigned to any classes.")
