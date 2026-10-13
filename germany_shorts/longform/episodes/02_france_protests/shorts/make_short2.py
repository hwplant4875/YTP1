"""STRATA France Short #2: '250,000 in the streets'. Writes short2.json (see common.py for the render command).
Facts: research.md 1.2 (6 Oct 'Acte 3': ~250,000 police count / 450,000 organisers; Paris 56,000 / 100,000;
Louis-le-Grand and Henri-IV walk out; >=488 arrests, 43 officers wounded) and the Justice Ministry toll to 8 Oct
(6,877 in custody, 86% minors)."""
from common import Short, P, ph, v2, news, cc, d3, MUSIC, CROWD, TICK, HIT

s = Short(2, "FRANCE · 6 OCTOBER")
s.line("A quarter of a million people marched for France's schools on October sixth, police say.", [
    P(news("ap_cortege"), cap="*{n}*\nMARCHED", count=[0, 250000, 2.2], col="blue"),
    P(ph(418), at="France's schools", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.45]),
    P(ph(435), at="October sixth", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])], sfx=TICK)
s.lf(4, [
    P(ph(76), cap="ORGANISERS:\n*450,000*", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.45]),
    P(ph(436), at="four hundred", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])])
s.lf(67, [
    P(cc("Lycée_Louis-le-Grand_in_Paris_75"), start=20.0, cap="PARIS\nPOLICE COUNT:\n*56,000*", col="blue"),
    P(ph(423), at="fifty-six", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5]),
    P(ph(425), at="Organisers", cap="PARIS\nORGANISERS:\n*100,000*", col="red", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5]),
    P(ph(424), at="hundred thousand", kb=[1.04, 0.5, 0.5, 1.12, 0.5, 0.45])])
s.lf(70, [
    P(cc("Lycée_Louis-le-Grand_in_Paris_78"), start=0.5, cap="ELITE SCHOOLS\n*WALKED OUT*", col="blue"),
    P(ph(168), at="two of the most", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(189), at="walked out", cap="IN\n*SOLIDARITY*", col="blue", kb=[1.04, 0.5, 0.45, 1.14, 0.5, 0.45])])
s.lf(72, [
    P(ph(355), cap="\"TOO YOUNG\nTO BE *HEARD*...\"", col="red", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5]),
    P(ph(466), at="but not", cap="\"...BUT NOT TOO\nYOUNG TO BE\n*CLUBBED*\"", col="red", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5])])
s.lf(73, [
    P(ph(339), cap="*PERPIGNAN*", col="blue", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(313), at="one banner", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5]),
    P(ph(310), at="We just want", cap="\"WE JUST\nWANT A\n*FUTURE*\"", col="blue", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])])
s.lf(75, [
    P(news("reuters_teargas"), cap="BY EVENING:\n*TEAR GAS*", col="red"),
    P(ph(415), at="four hundred", cap="*488+*\nARRESTS", col="red", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5]),
    P(ph(510), at="forty-three", cap="*43* OFFICERS\nWOUNDED", col="blue", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.45])])
s.lf(5, [
    P(ph(519), cap="*{n}*\nIN CUSTODY", count=[0, 6877, 1.8], col="blue", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.45]),
    P(cc("Lycée_Louis-le-Grand_in_Paris_80"), at="eight hundred", start=1.0),
    P(ph(307), at="Eighty-six", cap="*86%*\nARE MINORS", col="red", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5])], sfx=TICK)
s.end(sfx=HIT)
s.write(MUSIC["tide"], "250,000 Marched for France's Schools #shorts",
        "On 6 October, police counted about 250,000 marchers across France (organisers: 450,000), as elite Paris lycées "
        "walked out in solidarity. Since mid-September 6,877 people have been taken into custody, 86% of them minors.",
        sfx_first=CROWD)
