"""STRATA France Short #3: 'Schools falling apart'. Writes short3.json (see common.py for the render command).
Facts: research.md 4.x via lines.py (average lycée ~65 years old, 56% built before 1970 - franceinfo 5 Oct; rats,
cockroaches, fallen ceilings; 35-40°C in summer, no heating in winter; Senate report ~€1.5 bn a year; 37 pupils in a
Marseille class - teacher Diane Di Sciullo, 8 Oct)."""
from common import Short, P, ph, v2, news, cc, d3, MUSIC, BINS, HIT

s = Short(3, "FRANCE · LYCÉE PROTESTS")
s.line("In France, teenagers are blockading schools they say are falling apart.", [
    P(ph(413), cap="SCHOOLS\n*FALLING APART*", col="cyan", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5]),
    P(ph(157), at="blockading", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(440), at="falling apart", kb=[1.04, 0.5, 0.45, 1.14, 0.5, 0.4])])
s.line("The average French lycée is sixty-five years old.", [
    P(v2("paul_eluard"), cap="AVERAGE AGE:\n*65 YEARS*", col="cyan", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(v2("montreuil_jaures"), at="sixty-five", kb=[1.12, 0.5, 0.4, 1.24, 0.5, 0.35])])
s.lf(33, [
    P(ph(102), cap="*56%*\nBUILT BEFORE\n1970", col="cyan", kb=[1.04, 0.5, 0.45, 1.14, 0.5, 0.4]),
    P(ph(150), at="built before", kb=[1.04, 0.5, 0.4, 1.14, 0.5, 0.35])])
s.lf(34, [
    P(news("f24_ceiling"), cap="RATS, ROACHES,\n*FALLEN CEILINGS*", col="cyan")])
s.lf(35, [
    P(ph(52), cap="*35-40°C*\nIN SUMMER", col="red", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5]),
    P(ph(50), at="thirty-five", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(news("f24_radiator"), at="In winter", cap="*NO HEATING*\nIN WINTER", col="cyan")])
s.lf(36, [
    P(d3("money", "repair_need"), start=4.2, cap="*€1.5 BN*\nA YEAR\nTO FIX THEM", col="green"),
    P(ph(369), at="would take", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.lf(43, [
    P(v2("salle57_pupils"), cap="CLASSES\n*PACKED*", col="cyan", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(497), at="A teacher", cap="*37 PUPILS*\nIN ONE CLASS", col="cyan", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.45]),
    P(ph(359), at="she has", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])])
s.line("That's why so many pupils have been blocking their own schools.", [
    P(cc("Lycée_Colbert_in_Paris_36"), start=0.5, cap="SO THEY\n*BLOCKED THEM*", col="cyan"),
    P(ph(225), at="blocking", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])])
s.end(sfx=HIT)
s.write(MUSIC["hiding"], "French Pupils Say Their Schools Are Falling Apart #shorts",
        "The average French lycée is 65 years old. Pupils describe rats, fallen ceilings, 35-40°C classrooms in summer "
        "and no heating in winter. A Senate report says repairs need about €1.5 billion a year.",
        sfx_first=BINS)
