"""English beat script for 'Tunnel 29' (long-form #2). Writes script_en.json next to this file.
Facts and sources: research_tunnel29.md. Single-source details are framed as participants' accounts.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CR = {m["n"]: m["attribution"].replace("CC-BY-SA 3.0", "CC BY-SA 3.0").replace(", via Wikimedia Commons", "")
      for m in json.load(open(os.path.join(HERE, "assets/commons.json")))}


def t3(shot, t0=0):
    return {"type": "3d", "scene": "tunnel29", "shot": shot, "t0": t0}


def xs(shot, t0=0):
    return {"type": "3d", "scene": "cross_section", "shot": shot, "t0": t0}


def img(n, frm=(1.05, 0.5, 0.5), to=(1.18, 0.5, 0.5)):
    return {"type": "image", "file": f"assets/t{n:02d}.jpg", "from": list(frm), "to": list(to), "credit": CR[n]}


def film(file, start, credit, **kw):
    return {"type": "video", "file": f"assets/{file}.mp4", "start": start, "credit": credit, **kw}


USAF = "1961_USAF_Berlin_Documentary_342-USAF-31891A"
CUSAF = "U.S. Air Force film, 1961 (public domain), National Archives"
N61, N62 = "1961-08-31_Berlin", "1962-08-16_The_Wall"
C61, C62 = "Universal Newsreel, 31 Aug 1961 (public domain)", "Universal Newsreel, 16 Aug 1962 (public domain)"

WHOOSH = {"prompt": "fast cinematic whoosh transition", "len": 1.2, "vol": 0.5, "at": -0.15}
HIT = {"prompt": "deep cinematic sub boom hit with short metallic tail", "len": 2.5, "vol": 0.55}
FLASH = {"prompt": "camera flash pop with soft whoosh", "len": 1, "vol": 0.4, "at": -0.1}
RISER = {"prompt": "dark cinematic riser building tension, rising pitch, ends abruptly", "len": 4, "vol": 0.4}
TYPE = {"prompt": "single old typewriter keystrokes and carriage bell, short", "len": 2, "vol": 0.3}
DIG = {"prompt": "spade scraping and chopping into wet clay in a cramped tunnel, close, muffled, rhythmic", "len": 12, "vol": 0.3}
DRIP = {"prompt": "water dripping in a narrow underground tunnel, echo, quiet", "len": 15, "vol": 0.22}
REEL = {"prompt": "1960s 16mm film camera running, mechanical whirr and clatter", "len": 6, "vol": 0.3}
NIGHT = {"prompt": "quiet city street at night 1960s, distant dog barking, wind, faint electric hum of floodlights", "len": 20, "vol": 0.22}
CART = {"prompt": "small cart rolling on narrow rails in a tunnel, pulled by a rope winch", "len": 6, "vol": 0.3}
WATER = {"prompt": "pipe bursting underground, water gushing and splashing into a tunnel", "len": 5, "vol": 0.45}
PUB = {"prompt": "small 1960s pub interior, quiet murmur, glasses clinking, clock ticking", "len": 12, "vol": 0.2}

B = []
def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# ---------------------------------------------------------------- cold open
B.append({"visual": t3("street", 0), "hold": 1.2, "id": "intro",
          "sfx": [{"prompt": "deep low cinematic drone swelling slowly from silence", "len": 6, "vol": 0.35}, NIGHT]})
say("Berlin. Bernauer Straße. Summer, 1962.", text={"kind": "label", "content": "BERNAUER STRASSE · 1962", "pos": [0.5, 0.12]})
say("On one side of the street: the West.")
say("On the other: East Germany. Its windows bricked shut.", film(USAF, 1160, CUSAF), trans="flash", sfx=FLASH,
    sub="On the other: East Germany. Windows *bricked shut*")
say("But five meters under the pavement...", t3("reveal", 0), trans="dip", sfx=RISER)
say("a group of students is lying on their backs in the dark, digging.", sub="students lie on their backs in the dark, *digging*", sfx=DIG)
say("They're digging toward the East.", t3("crawl", 2), sfx=[DRIP, DIG])
say("Toward a cellar, more than a hundred meters away, on the other side of the Wall.", sub="Toward a cellar *on the other side* of the Wall")
say("And right behind them...", t3("camera", 0), trans="dip", sfx={"prompt": "low ominous cinematic hit, deep sub boom", "len": 2, "vol": 0.5})
say("there's an American television camera.", sub="there's an *American television camera*", sfx=REEL, hold=0.6)
B.append({"visual": "same", "hold": 0.4, "sfx": HIT})
say("NBC paid for this tunnel.", {"type": "black"}, sub="NBC *paid* for this tunnel", text={"kind": "label", "content": "NBC · 1962", "pos": [0.5, 0.5]})
say("The tunnel would flood. A rival tunnel would be betrayed to the Stasi. And Washington would try to stop the film.",
    t3("water", 2), sub="It would flood. A rival tunnel would be *betrayed*. Washington would try to *stop the film*",
    sfx={"prompt": "water trickling and rising in a narrow tunnel, echo", "len": 8, "vol": 0.3})
say("But on one night in September, twenty-nine people crawled through it, to freedom.", t3("cellar", 0),
    sub="But one night in September, *29 people* crawled through it", sfx=RISER)
B.append({"visual": t3("section", 3), "hold": 4.2, "text": {"kind": "flicker", "content": "TUNNEL 29", "pos": [0.5, 0.45]},
          "sfx": [{"prompt": "old bare light bulbs buzzing on one by one in a tunnel, electric hum", "len": 3, "vol": 0.5},
                  {"prompt": "deep cinematic impact boom with long dark reverb tail", "len": 4, "vol": 0.6, "at": 0.5}]})
say("This is how they did it.", hold=0.6)

# ---------------------------------------------------------------- act 1: Bernauer Strasse and the people
say("To understand Tunnel 29, you need to understand this street.", img(1, (1.05, 0.5, 0.5), (1.18, 0.4, 0.55)), id="act1", trans="dip",
    text={"kind": "label", "content": "Bernauer Straße · 1955", "pos": [0.5, 0.86]})
say("Before 1961, Bernauer Straße was just a street. The sign on it said: you are entering the French sector.")
say("The pavement was West Berlin. The houses along it were East Berlin.", img(10, (1.05, 0.5, 0.5), (1.15, 0.45, 0.5)))
say("So when the Wall went up in August 1961, people simply jumped. Out of their windows, into the West.", img(9, (1.05, 0.5, 0.5), (1.18, 0.55, 0.5)),
    sub="People *jumped* out of their windows, into the West")
say("Within weeks, the doors were nailed shut. Then the windows were bricked up.", film(N62, 36, C62))
say("Whole buildings were emptied.", img(12, (1.05, 0.5, 0.5), (1.18, 0.5, 0.45)))
say("And the street became a border.", img(15, (1.08, 0.5, 0.4), (1.2, 0.5, 0.35)), hold=0.8)
say("Now, meet the diggers.", {"type": "black"}, sfx=TYPE)
say("Two Italian students in West Berlin, Luigi Spina and Domenico Sesta.", text={"kind": "label", "content": "LUIGI SPINA · DOMENICO SESTA", "pos": [0.5, 0.5]})
say("Their friend Peter Schmidt was stuck in the East, with his wife and a newborn baby.",
    sub="Their friend was stuck in the East, with his wife and a *newborn baby*")
say("In early 1962, he asked them for help. They thought about a helicopter. Then they settled on a tunnel.",
    sub="They thought about a *helicopter*. Then: a *tunnel*")
say("Then there was Hasso Herschel.", text={"kind": "label", "content": "HASSO HERSCHEL", "pos": [0.5, 0.5]}, sfx=TYPE)
say("He'd spent years in an East German prison, and had only just escaped on a borrowed Swiss passport.")
say("His sister Anita was still in the East, with her husband and their little girl.")
say("And Joachim Rudolph, a twenty-three-year-old who had fled himself only months earlier, wading across a river.",
    text={"kind": "label", "content": "JOACHIM RUDOLPH", "pos": [0.5, 0.5]}, sfx=TYPE,
    sub="Joachim Rudolph, 23. He'd fled across a river *months earlier*")
say("He studied engineering. Now he was going back. Underground.", sub="Now he was going back. *Underground*", hold=0.8)

# ---------------------------------------------------------------- act 2: the dig
say("The entrance was a small, war-damaged factory, right on Bernauer Straße.", t3("street", 4), id="act2", trans="dip",
    text={"kind": "label", "content": "Bernauer Straße 78", "pos": [0.5, 0.86]}, sfx=NIGHT)
say("Its owner let them use the cellar for free.")
say("They dug a shaft straight down, about five meters.", t3("reveal", 0), sfx=DIG)
say("Then they turned east, and started digging under the street, under the death strip, and under the Wall.",
    sub="Then east: under the street, the death strip, and *the Wall*")
say("The tunnel was barely wider than a man's shoulders.", t3("dig", 0), sfx=[DIG, DRIP])
say("They lay on their backs and hacked at the clay in front of them, by the light of a single bulb.",
    sub="They lay on their backs and hacked at the clay *by the light of a single bulb*")
say("The earth went back in a cart on rails, pulled by an electric winch.", t3("crawl", 6), sfx=CART)
say("Some two hundred and fifty tonnes of it. Seven cellar rooms filled to the ceiling.", sub="Some *250 tonnes* of earth")
say("Twenty tonnes of timber held the roof up. A field telephone connected them to the surface.",
    sfx={"prompt": "old field telephone crank ring, muffled underground", "len": 2, "vol": 0.35})
say("And then, they ran out of money.", {"type": "black"}, sfx=HIT, hold=0.6)
say("That's when the Americans came in.", t3("camera", 3), sfx=REEL)
say("NBC's Berlin correspondent, Piers Anderton, had been looking for exactly this story.")
say("The deal: seven and a half thousand dollars for exclusive rights to film. Five thousand more if the escape worked.",
    text={"kind": "label", "content": "$7,500  +  $5,000", "pos": [0.5, 0.86]},
    sub="$7,500 to film. *$5,000 more* if it worked")
say("In return, NBC's cameramen would crawl into the tunnel and film it, from the inside.", sub="NBC would film it *from the inside*")
say("The producer back in New York? He never saw the tunnel. Not once.")
say("By early June, they were under the border line.", t3("section", 2), trans="dip")
say("According to one of the diggers, they even hung a sign at that spot: 'You are leaving the American sector'.",
    text={"kind": "quote", "content": "„YOU ARE LEAVING THE AMERICAN SECTOR“", "pos": [0.5, 0.8]},
    sub="They hung a sign: *'You are leaving the American sector'*")
say("Then, in early summer, the water came.", t3("water", 0), sfx=WATER, id="flood")
say("A water main had burst somewhere above them. The tunnel began to flood.", sub="A water main had burst. The tunnel *began to flood*")
say("They pumped day and night. It wasn't enough.", sfx={"prompt": "hand water pump squeaking and splashing in a tunnel, repetitive", "len": 6, "vol": 0.3})
say("So they did something remarkable: they persuaded West Berlin officials to ask East Berlin to shut off its own water main,",
    sub="They got *East Berlin* to shut off its own water main")
say("disguised as a routine repair.", hold=0.6)
say("It worked. But the tunnel took weeks to dry out.")
say("And while they waited, something went very wrong in another tunnel.", xs("pass"), trans="dip", sfx=RISER)
say("Across the city, another group was digging, at Kiefholzstraße.",
    text={"kind": "label", "content": "Kiefholzstraße · 1962", "pos": [0.5, 0.86]})
say("They had a TV deal too. With CBS.", sub="They had a TV deal too. With *CBS*")
say("Herschel, Rudolph and their friend Uli Pfeifer went to help.")
say("But the group had been infiltrated by a Stasi informer.", {"type": "black"}, sub="But the group had a *Stasi informer*", sfx=HIT)
say("That summer, as refugees gathered at the eastern end, East German forces sprang the trap.",
    film(N61, 87, C61), sub="East German forces *sprang the trap*")
say("Dozens of people waiting in the East were arrested.")
say("The three diggers escaped only by crawling back through the tunnel.", t3("crawl", 12), sub="The diggers escaped by *crawling back*",
    sfx={"prompt": "frantic crawling and breathing in a narrow tunnel, close, dirt falling", "len": 5, "vol": 0.35})
say("Then, on August 17th, an eighteen-year-old named Peter Fechter was shot at the Wall.",
    {"type": "black"}, text={"kind": "label", "content": "PETER FECHTER · 1944–1962", "pos": [0.5, 0.5]}, sub="August 17th: Peter Fechter, 18, was shot at the Wall")
say("He bled to death at the foot of the Wall, in full view of the West, while nobody helped him.", sub="He bled to death *in full view of the West*")
say("The diggers pinned his photo inside their tunnel. And kept digging.", t3("crawl", 18), sub="They pinned his photo in the tunnel. *And kept digging*", hold=1.0)

# ---------------------------------------------------------------- act 3: escape day
say("By September, the water was back.", t3("water", 4), id="act3", sfx=DRIP)
say("They couldn't reach their original target, so they aimed for a closer building instead.")
say("Schönholzer Straße, number seven.", img(17, (1.05, 0.5, 0.5), (1.15, 0.5, 0.6)),
    text={"kind": "label", "content": "Schönholzer Straße 7", "pos": [0.5, 0.86]})
say("On the morning of September 14th, Hasso Herschel dug upward, and broke through the floor of the cellar.", t3("cellar", 0),
    sub="September 14th: they broke through the *cellar floor*",
    sfx={"prompt": "pickaxe breaking through a brick floor from below, rubble falling, air rushing", "len": 4, "vol": 0.45})
say("He waited at the bottom of the cellar stairs. With a loaded pistol.", sub="He waited at the stairs. *With a loaded pistol*", sfx=HIT)
say("Now someone had to tell the families. Without anyone noticing.", {"type": "black"})
say("That job went to Ellen, the group's courier. It was her twenty-second birthday.",
    text={"kind": "label", "content": "THE COURIER", "pos": [0.5, 0.5]})
say("She crossed into East Berlin, and walked to a playground near a church.", img(14, (1.05, 0.5, 0.5), (1.18, 0.45, 0.5)))
say("From there, she watched one window. A white sheet meant the tunnel was open. A red one meant run.",
    sub="A *white* sheet: open. A *red* one: run")
say("The sheet was white.", t3("street", 8), sfx={"prompt": "cloth flapping in the wind, single", "len": 2, "vol": 0.35}, hold=0.6)
say("According to the participants, she then went from pub to pub, where the families were waiting.", {"type": "black"}, sfx=PUB)
say("The signals were tiny. Buying a box of matches. Carrying a certain newspaper.",
    sub="The signals: a box of *matches*. A certain *newspaper*")
say("At the last pub, the code was to order a coffee. They didn't have coffee. So she ordered a cognac.",
    sub="The code was to order *coffee*. They had none. *She ordered cognac*")
say("And every five minutes, another small group walked to Schönholzer Straße seven.", img(17, (1.15, 0.5, 0.6), (1.05, 0.5, 0.5)))
say("Into the cellar. Down the ladder. Into the dark.", t3("cellar", 4),
    sfx={"prompt": "footsteps on old wooden cellar stairs, then climbing down a wooden ladder", "len": 4, "vol": 0.35})
say("A hundred and thirty-five meters of mud, on hands and knees.", t3("crawl", 0), sfx=[DRIP, {"prompt": "people crawling through mud and shallow water in a tunnel, splashing, breathing", "len": 8, "vol": 0.35}],
    sub="*135 meters* of mud, on hands and knees")
say("Parents. A grandmother. Children. Babies, passed from arm to arm.", sub="Parents. Children. *Babies, passed from arm to arm*")
say("And the water was rising again.", t3("water", 3), sub="And the water was *rising again*")
say("At the other end, the NBC cameras were rolling.", t3("camera", 6), sfx=REEL)
say("They filmed a young mother climbing the ladder with her baby, her clothes soaked with mud.",
    sub="A young mother climbing the ladder *with her baby*")
say("And they filmed one of the diggers, holding his son for the very first time.", sub="A digger, holding his son *for the first time*", hold=1.4)
say("By the end, twenty-nine people had made it through.", t3("section", 8), trans="dip", text={"kind": "year", "content": "29"},
    sfx=HIT)
say("No one was caught. No one was hurt.")
say("The next day, the water won, and the tunnel flooded for good.", t3("water", 6))
say("Eleven days later, the ground above it sank, and the Stasi finally found it.", sub="*11 days later*, the Stasi finally found it", hold=0.8)

# ---------------------------------------------------------------- act 4: the film nobody wanted aired
say("NBC had the story of the decade.", {"type": "black"}, id="act4", sfx=REEL)
say("The broadcast was set for October 31st, 1962.")
say("But word got out that NBC had paid for an escape. Time magazine called it chicanery. The State Department was furious.",
    sub="Critics called it *chicanery*. The State Department was *furious*")
say("Then, on October 22nd, President Kennedy went on television to announce the Cuban Missile Crisis.",
    film(N61, 63, C61), text={"kind": "label", "content": "22 OCTOBER 1962", "pos": [0.5, 0.86]},
    sub="October 22nd: the *Cuban Missile Crisis*")
say("With the world on the edge of nuclear war, Washington leaned hard on NBC to hold the film.")
say("The next day, NBC pulled it.", sub="The next day, NBC *pulled it*", sfx=HIT)
say("It finally aired on December 10th, 1962.", t3("camera", 9), text={"kind": "label", "content": "10 DECEMBER 1962", "pos": [0.5, 0.86]})
say("Ninety minutes. No interviews. Just the tunnel.")
say("It won three Emmys, including Program of the Year.", sub="Three Emmys. Including *Program of the Year*")
say("It's still the only documentary ever to win it.")
say("And the U.S. government, the same one that had tried to stop it? Its own information agency reportedly bought a hundred copies, to show around the world.",
    sub="Then a U.S. agency *bought 100 copies*")
say("Not everyone was celebrating.", img(11, (1.05, 0.5, 0.5), (1.15, 0.5, 0.45)))
say("Seventeen of the helpers publicly distanced themselves from the deal. Escape, they said, should never be a business.",
    sub="*17 helpers* said escape should never be a business")
say("Hasso Herschel didn't stop. Over the next decade, he helped around a thousand more people escape.",
    sub="Herschel went on to help *around a thousand* more people escape")
say("Some hidden in secret compartments of cars. One of them, a converted Cadillac.", hold=0.6)

# ---------------------------------------------------------------- act 5: today
say("Today, Bernauer Straße is a memorial.", img(20, (1.0, 0.5, 0.5), (1.12, 0.6, 0.5)), id="act5", trans="dip")
say("Lines of metal plates in the grass trace where escape tunnels once ran.", img(19, (1.05, 0.5, 0.5), (1.18, 0.5, 0.6)))
say("And on the wall of Schönholzer Straße seven, there's a small plaque.", img(16, (1.05, 0.5, 0.4), (1.25, 0.5, 0.45)))
say("It says: one hundred and thirty-five meters. Twenty-nine people. Dug by brave men,",
    sub="135 meters. 29 people. *Dug by brave men*")
say("so they could hold their wives, children, relatives and friends in their arms again.",
    sub="so they could hold their families *in their arms again*", hold=1.0)
say("A TV network bought a tunnel under the Iron Curtain.", t3("thumb", 0), trans="dip")
say("But what came out the other end wasn't a story. It was twenty-nine people.", sub="What came out the other end was *29 people*", hold=1.5)
say("If you want more stories from under Europe's surface, subscribe. There are plenty more.", t3("crawl", 22),
    sub="More stories from *under Europe's surface*: subscribe")
B.append({"visual": t3("section", 14), "hold": 16.0})   # end screen

spec = {
    "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
    "gap": 0.12,
    "sub_limit": 44,
    "music": [
        {"file": "music/t1_intro.mp3", "from": "intro", "to": "act1", "vol": 0.15, "fade_in": 3},
        {"file": "music/t2_dig.mp3", "from": "act1", "to": "flood", "vol": 0.14},
        {"file": "music/t3_tension.mp3", "from": "flood", "to": "act3", "vol": 0.15},
        {"file": "music/t4_escape.mp3", "from": "act3", "to": "act4", "vol": 0.16},
        {"file": "music/t2_dig.mp3", "from": "act4", "to": "act5", "vol": 0.13},
        {"file": "music/t5_resolution.mp3", "from": "act5", "to": "end", "vol": 0.18},
    ],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "script_en.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words,", sum(len(b.get("say", "")) for b in B), "chars")
