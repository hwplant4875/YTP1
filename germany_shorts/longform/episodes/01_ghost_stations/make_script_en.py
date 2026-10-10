"""English beat script for 'Berlin's ghost stations' (FP channel, long-form #1). Writes script_en.json next to this file.

Narration: ElevenLabs eleven_v4, Mattes. The German PA announcement is the original announce_pa.wav, placed right
after the first line as the hook.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CR = {m["n"]: m["attribution"].replace("CC-BY-SA 3.0", "CC BY-SA 3.0").replace(", via Wikimedia Commons", "")
      for m in json.load(open(os.path.join(HERE, "assets/commons.json")))}
CR[19] = "Map: Ericmetro / CC0"


def g3(shot, scene="ghost_station", t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def gi(shot, t0=0):
    return {"type": "3d", "scene": "intro", "shot": shot, "t0": t0}


def img(n, frm=(1.05, 0.5, 0.5), to=(1.18, 0.5, 0.5), ext="jpg"):
    return {"type": "image", "file": f"assets/c{n:02d}.{ext}", "from": list(frm), "to": list(to), "credit": CR[n]}


def news(file, start, credit):
    return {"type": "video", "file": f"assets/{file}.mp4", "start": start, "credit": credit}


N61, N62 = "1961-08-31_Berlin", "1962-08-16_The_Wall"
C61, C62 = "Universal Newsreel, 31 Aug 1961 (public domain)", "Universal Newsreel, 16 Aug 1962 (public domain)"

# reusable sound cues (ElevenLabs sound generation, cached by prompt)
WHOOSH = {"prompt": "fast cinematic whoosh transition", "len": 1.2, "vol": 0.5, "at": -0.15}
HIT = {"prompt": "deep cinematic sub boom hit with short metallic tail", "len": 2.5, "vol": 0.55}
FLASH = {"prompt": "camera flash pop with soft whoosh", "len": 1, "vol": 0.4, "at": -0.1}
RISER = {"prompt": "dark cinematic riser building tension, rising pitch, ends abruptly", "len": 4, "vol": 0.4}
TRAIN = {"prompt": "subway train running through a tunnel, rhythmic wheels on rail joints, inside the driver cab", "len": 22, "vol": 0.16}
TICK = {"prompt": "old projector film flicker and click", "len": 2, "vol": 0.3}
TYPE = {"prompt": "single old typewriter keystrokes and carriage bell, short", "len": 2, "vol": 0.3}
CROWD = {"prompt": "crowd murmur in an echoing train station hall, 1960s", "len": 10, "vol": 0.18}

B = []
def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# ---------------------------------------------------------------- cold open
AMB = [{"prompt": "empty underground subway station ambience, faint electrical hum, distant water drips, low air rumble", "len": 22, "vol": 0.22, "at": 0},
       {"prompt": "old light bulbs clicking and buzzing on one by one, electrical relay clicks, echo", "len": 6, "vol": 0.35, "at": 0.4}]
B.append({"visual": gi("lightsup", 0), "hold": 1.3, "id": "intro",
          "sfx": [{"prompt": "deep low cinematic drone swelling slowly from silence", "len": 6, "vol": 0.35, "at": 0}] + AMB})
say("For twenty-eight years, no train ever stopped at this station.", sub="For 28 years, no train *ever stopped* at this station")
# the hook: the real-sounding West Berlin PA, then silence and a hit
B.append({"visual": gi("cab", 0), "hold": 4.0, "trans": "dip",
          "text": {"kind": "quote", "content": "„Voltastraße. Letzter Bahnhof in Berlin-West.“\\N{\\fs40}Voltastraße. Last station in West Berlin.", "pos": [0.5, 0.8]},
          "sfx": [{"file": "announce_pa.wav", "vol": 1.0, "duck": False, "at": 0.25},
                  {"prompt": "PA speaker feedback chime, old station loudspeaker ding dong", "len": 1.5, "vol": 0.3, "at": -0.2},
                  TRAIN]})
say("And yet... there was always someone standing on the platform.", img(3, (1.25, 0.42, 0.45), (1.42, 0.38, 0.42)), trans="flash",
    sub="And yet, there was *always someone* on the platform",
    sfx=[FLASH, {"prompt": "low ominous cinematic hit, deep sub boom", "len": 2, "vol": 0.5, "at": 0.2}])
say("Watching.", gi("guard", 0), hold=1.0,
    sfx={"prompt": "single bare light bulb flickering on with electric buzz and click", "len": 2.5, "vol": 0.45, "at": 0.1})
B.append({"visual": "same", "hold": 0.6, "sfx": {"prompt": "dark cinematic boom hit with metallic tail", "len": 3, "vol": 0.6}})
say("West Berlin. 1975.", gi("cab", 6), trans="flash", text={"kind": "label", "content": "WEST BERLIN · 1975", "pos": [0.5, 0.12]},
    sfx=[WHOOSH, TRAIN])
say("You're riding the U8, heading north.")
say("You've just passed the last station in the West. The train slips back into the dark.",
    sub="The *last station* in the West. The train slips back into the dark")
say("Then, it starts to slow down.", sfx={"prompt": "old subway train brakes squealing, slowing down in a tunnel", "len": 3, "vol": 0.4})
say("Lights. A platform.")
say("Old posters on the walls. Benches. Signs. Nobody waiting.")
say("No... not nobody.", gi("guardclose", 0), trans="dip", sub="No. *Not nobody*",
    sfx={"prompt": "low ominous cinematic hit, deep sub boom", "len": 2, "vol": 0.55})
say("A soldier with a rifle turns his head, and looks straight at you.", sub="A soldier with a rifle turns, and looks *straight at you*")
say("The train doesn't stop.", gi("passby", 1.5), sub="The train *doesn't stop*",
    sfx={"prompt": "subway train passing by fast at close range, whoosh and rumble, doppler", "len": 5, "vol": 0.45})
say("It rolls on, and the platform disappears behind you.", gi("leave", 0), hold=1.0)
say("This is Rosenthaler Platz.", img(2, (1.06, 0.5, 0.55), (1.2, 0.45, 0.6)), trans="flash",
    text={"kind": "label", "content": "U-Bahnhof Rosenthaler Platz", "pos": [0.5, 0.12]}, sfx=FLASH)
say("For twenty-eight years, not a single passenger got on or off here.", img(3, (1.12, 0.5, 0.45), (1.3, 0.45, 0.42)),
    sub="For 28 years, *not a single passenger* got off here")
say("And beneath Berlin, there were sixteen stations just like it.", g3("reveal", "cross_section"), trans="dip",
    sub="And beneath Berlin, there were *sixteen* of them", sfx=RISER)
say("Berliners had a name for them.")
B.append({"visual": gi("drift", 0), "hold": 4.2, "text": {"kind": "flicker", "content": "GHOST STATIONS", "pos": [0.5, 0.45]},
          "sfx": [{"prompt": "fluorescent tube flickering on, electric buzz and pings", "len": 3, "vol": 0.5},
                  {"prompt": "deep cinematic impact boom with long dark reverb tail", "len": 4, "vol": 0.6, "at": 0.5}]})
B.append({"visual": "same", "hold": 0.1, "text": {"kind": "label", "content": "GEISTERBAHNHÖFE", "pos": [0.5, 0.58], "delay": -3.0, "span": 0}})
say("Why did they exist?", news(N61, 63, C61), trans="flash", sfx={"prompt": "short whoosh", "len": 0.8, "vol": 0.4, "at": -0.1})
say("What were those guards really guarding?", gi("guardclose", 3.5))
say("And how did one man use these tunnels to escape?", g3("border", t0=2))
say("This is the story of the stations that vanished from the map, and the city that paid for its own trains to pass through them.",
    gi("drift", 4), hold=0.8, sub="The stations that *vanished* from the map")

# ---------------------------------------------------------------- act 1: the city splits
say("Before the Wall, Berlin was a strange city.", news(N62, 9, C62), id="act1", trans="dip")
say("After the war, the victors carved Germany's capital into four sectors.")
say("The Soviets took the east. The Americans, British and French took the west.")
say("But underground, none of that mattered. One subway ride, and you were on the other side.")
say("Tens of thousands of people lived in the East and commuted to jobs in the West.")
say("The problem was, many of them never came back.")
say("By the summer of 1961, thousands of East Germans were leaving every single day.", sub="By summer 1961, *thousands* were leaving every day")
say("Then, in the early hours of Sunday, August 13th, 1961...", news(N61, 57.5, C61), text={"kind": "year", "content": "1961"}, sfx=HIT)
say("East Germany cut Berlin in two. Overnight.", sub="East Germany cut Berlin in two. *Overnight*")
say("Barbed wire went down. Then bricks went up.", news(N61, 63, C61))
say("Buildings on the border had their windows bricked shut.", news(N62, 36, C62))
say("A street you could walk across yesterday was now an international border.", news(N61, 87, C61))
say("Families could only wave to each other across the wire.", news(N61, 98, C61), hold=1.5)
say("But East Germany still had a problem.", g3("pass", "cross_section"), sfx=RISER)
say("You can wall off a street. Walling off what's underneath it is much harder.",
    sub="You can wall off a street. *What's underneath* is harder")
say("Berlin's subway had been built decades before the city was divided.")
say("So a few lines started in West Berlin, ran under East Berlin, and came back up in the West.",
    img(19, (1.0, 0.55, 0.5), (1.25, 0.62, 0.55), "png"))
say("Two U-Bahn lines, the U6 and the U8, plus the north-south S-Bahn tunnel.")
say("For West Berliners, they were the fastest way from the north of the city to the south.")
say("Here's what that looked like.", g3("reveal", "cross_section", t0=0))
say("Up top: the Wall, the watchtowers, and the death strip.", sub="Up top: the Wall, the watchtowers, and the *death strip*")
say("A few meters below...")
say("West Berlin's trains, still running right underneath it all.", hold=0.8)
say("So instead of cutting the lines, East Germany chose something far stranger.", g3("cab", t0=10))
say("Western trains could pass through. But they could never stop.", sub="Western trains could pass. But they could *never stop*")
say("And the strangest part of this story? West Berlin was paying East Germany for the privilege.",
    sub="West Berlin was *paying* East Germany for it")
say("We'll get to the money. First, let's step inside a ghost station.")

# ---------------------------------------------------------------- act 2: anatomy of a ghost station
say("On August 13th, 1961, the stations died overnight.", news(N62, 18, C62), id="act2",
    text={"kind": "label", "content": "Bernauer Straße", "pos": [0.5, 0.86]})
say("On the U8: Bernauer Straße, Rosenthaler Platz, Weinmeisterstraße, Alexanderplatz, Jannowitzbrücke, Heinrich-Heine-Straße.",
    img(19, (1.25, 0.72, 0.5), (1.4, 0.72, 0.62), "png"), sub="U8: six stations, *all closed*")
say("On the U6: Schwartzkopffstraße, Nordbahnhof, Oranienburger Tor, Französische Straße, and Stadtmitte.",
    img(19, (1.3, 0.35, 0.45), (1.45, 0.4, 0.6), "png"), sub="U6: five more")
say("And on the S-Bahn: Nordbahnhof, Oranienburger Straße, Unter den Linden, and Potsdamer Platz.",
    img(19, (1.3, 0.5, 0.5), (1.4, 0.45, 0.8), "png"), sub="S-Bahn: four more")
say("Add Bornholmer Straße above ground, and you get sixteen.", sub="Plus Bornholmer Straße: *sixteen*")
say("Street entrances were walled up. The subway signs came down.", img(2, (1.08, 0.5, 0.42), (1.2, 0.55, 0.45)))
say("Some entrances were simply buried, until they vanished from the street entirely.")
say("On East Berlin's maps, the stations, and even the lines, were erased.", news(N62, 30, C62),
    text={"kind": "label", "content": "Potsdamer Platz", "pos": [0.5, 0.86]})
say("Most East Berliners probably forgot that Western trains were rumbling beneath their feet.")
say("At Nordbahnhof, the border guards built six separate walls to seal off the station.")
say("And then added wire fencing on top.")
say("On West Berlin's subway maps, meanwhile, there was a quiet little note.", {"type": "black"})
B.append({"visual": "same", "hold": 3.4, "sfx": TYPE,
          "text": {"kind": "quote", "content": "„Bahnhöfe, auf denen die Züge nicht halten“\\N\\N{\\fs44}Stations where trains do not stop", "pos": [0.5, 0.5]}})
say("So what was it like down on the platform?", g3("platform", t0=0), sfx=AMB[0])
say("The lights were dimmed to almost nothing.")
say("Time stood still in 1961.")
say("The adverts and signs on the walls didn't change for twenty-eight years.", sub="The adverts didn't change for *28 years*")
say("And in that darkness stood the border guards.", g3("guard", t0=4))
say("They worked in pairs, watching the platform through narrow slits in locked guard rooms.")
say("Their shifts were rotated at random. There were surprise inspections.")
say("Even the people watching were being watched.", sub="Even the watchers were *being watched*",
    sfx={"prompt": "single heavy metal door closing with echo in an empty concrete hall", "len": 2.5, "vol": 0.45})
say("Put yourself in their boots for a second.", g3("thumb", t0=0))
say("You stand in a platform that never sees daylight, and every few minutes, a Western train rolls past.",
    sfx={"prompt": "subway train passing slowly through an empty station, echo, rumble", "len": 6, "vol": 0.3, "at": 0.8})
say("Through the windows, you see West Berliners.")
say("Someone reading a newspaper. Someone asleep. Someone staring right back at you.")
say("They're close enough to touch. But the moment you step onto that train, you're a deserter.",
    sub="Close enough to touch. Step on, and you're a *deserter*")
say("That's exactly why East Germany made the guards watch each other.")
say("Barbed wire was laid along the edge of the platforms.", g3("platform", t0=12))
say("Emergency exits were welded shut.")
say("Shutters came down over the tracks, and in the eighties, light barriers were installed to detect anyone on foot.")
say("And on the tunnel wall, someone painted a single white line.", g3("border", t0=0),
    sfx={"prompt": "eerie low drone swell, tension", "len": 4, "vol": 0.35})
say("The border. From here on, you were in East Germany.", hold=1.2, sub="The border. From here on: *East Germany*")
say("Western trains had to crawl through at fifteen kilometers an hour.", g3("cab", t0=22), sub="Trains crawled through at *15 km/h*")
say("Until one day, an East German policeman tried to jump onto a passing train.")
say("After that, the speed went up, to twenty-five.", sub="After that: *25 km/h*")
say("Slow trains were too easy to catch.")

# ---------------------------------------------------------------- act 3: the escape
say("So did anyone actually escape through the ghost tunnels?", g3("border", t0=4), id="act3", sfx=RISER)
say("A few did. You can count them on your fingers.")
say("The boldest was Dieter Wendt, in 1980.", {"type": "black"}, text={"kind": "label", "content": "DIETER WENDT · 1980", "pos": [0.5, 0.5]},
    sfx=TYPE)
say("He was twenty-eight, and he worked as a signal technician on the East Berlin subway.")
say("He knew the signals in those tunnels better than almost anyone.", g3("cab", t0=0))
say("Because he worked down there every day.")
say("So he made a plan.")
say("He would fake a signal fault.")
say("When a signal breaks, a technician is allowed into the tunnel to fix it.")
say("The spot: a tunnel near Jannowitzbrücke station.", text={"kind": "label", "content": "Jannowitzbrücke", "pos": [0.5, 0.86]})
say("As a West Berlin train approached, he stood by the tracks and flagged it down.", sfx=RISER)
B.append({"visual": "same", "hold": 0.6, "sfx": {"prompt": "subway train emergency braking, loud metal screech in a tunnel", "len": 3, "vol": 0.55}})
say("The stunned driver opened the door and shouted:")
B.append({"visual": {"type": "black"}, "hold": 2.8, "sfx": [HIT, {"file": "driver_shout.wav", "vol": 1.0, "duck": False, "at": 0.15}],
          "text": {"kind": "quote", "content": "„Rein und hinlegen!“\\N\\N{\\fs44}Get in and lie down!", "pos": [0.5, 0.5]}})
say("Minutes later, the train pulled into West Berlin.", g3("platform", t0=4),
    sfx={"prompt": "subway train accelerating away, doors closing beep", "len": 4, "vol": 0.4})
say("He'd ridden straight through the border, inside a ghost tunnel.", hold=1.2, sub="Straight through the border, *inside a ghost tunnel*")
say("But luck like that was rare. Most attempts ended long before anyone reached the line.")
say("For twenty-eight years, the ghost stations let almost no one through.")
say("If you're enjoying this story, subscribing helps more than you think. There's a lot more hidden under Berlin.",
    g3("cab", t0=40), sub="Subscribe: there's a lot more *hidden under Berlin*")

# ---------------------------------------------------------------- act 4: Friedrichstrasse and the money
say("Now, of all the stations under East Berlin, trains stopped at exactly one.", img(13, (1.05, 0.5, 0.5), (1.2, 0.55, 0.5)), id="act4",
    sub="Trains stopped at *exactly one*")
say("Friedrichstraße.", text={"kind": "label", "content": "Bahnhof Friedrichstraße", "pos": [0.5, 0.86]}, sfx=CROWD)
say("For West Berliners, it was a place to change trains without any checks.", img(11, (1.08, 0.5, 0.44), (1.2, 0.45, 0.42)))
say("And at the same time, it was a border crossing into East Germany.", img(7, (1.05, 0.5, 0.5), (1.18, 0.5, 0.55)))
say("Two countries inside one station, separated by a wall.", sub="Two countries in *one station*")
say("Families visiting relatives in the East were searched and questioned here.", img(9, (1.1, 0.5, 0.42), (1.22, 0.5, 0.4)))
say("And the departure hall, where so many goodbyes were said, got a nickname.", img(17, (1.0, 0.5, 0.5), (1.12, 0.52, 0.48)))
say("The Palace of Tears.", text={"kind": "title", "content": "Tränenpalast", "pos": [0.5, 0.47]}, sfx=HIT,
    sub="*The Palace of Tears*")
say("The station also had a very strange shop.", img(8, (1.08, 0.5, 0.4), (1.2, 0.46, 0.38)))
say("The Intershop, which only took Western money.")
say("West Berliners rode the subway into East German territory just to buy cheap cigarettes and alcohol, then rode straight back.",
    sub="They rode into the East for *cheap cigarettes and booze*")
say("The last train after one in the morning, full of tipsy shoppers, had its own nickname.")
say("The rag collector.", text={"kind": "quote", "content": "„Lumpensammler“", "pos": [0.5, 0.8]}, sub="*The rag collector*")
say("But Friedrichstraße wasn't always harmless.", img(6, (1.1, 0.5, 0.42), (1.22, 0.5, 0.4)), sfx=RISER)
say("In March 1974, a Polish man threatened the embassy with a fake bomb, demanding to be let out to the West.")
say("East Germany pretended to agree.")
say("Moments after he passed through the checkpoint here, a hidden Stasi officer shot him.", sub="A hidden *Stasi* officer shot him",
    sfx={"prompt": "single distant gunshot echoing in a concrete hall", "len": 2, "vol": 0.4, "at": 1.6})
say("West Berlin was only a few steps away.", hold=1.5)
say("Now, about that money.", g3("pass", "cross_section"), sfx={"prompt": "old cash register ding and coins", "len": 1.5, "vol": 0.3})
say("In return for running its trains under East Berlin,")
say("from 1963, West Berlin paid East Germany a fee. Every single month.", text={"kind": "year", "content": "1963"},
    sub="West Berlin paid East Germany. *Every month*")
say("At first, around a hundred and eighty thousand marks a month.")
say("By 1989, it was almost half a million.", text={"kind": "label", "content": "181,132 DM  {\\fnPretendard Black}→{\\fnYouTube Sans}  495,756 DM / month", "pos": [0.5, 0.86]},
    sub="By 1989: almost *half a million*")
say("That's close to six million marks a year.")
say("To run its own subway, the city was paying the country that built the Wall around it.",
    sub="Paying the country that *built the Wall* around it")
say("And the S-Bahn was even more absurd.", img(18, (1.05, 0.5, 0.5), (1.18, 0.6, 0.5)))
say("Even inside West Berlin, the S-Bahn was run by East Germany's state railway.")
say("West Berliners were furious, and they boycotted it.")
say("The slogan: every S-Bahn ticket pays for the barbed wire.",
    text={"kind": "quote", "content": "„Der S-Bahn-Fahrer zahlt den Stacheldraht“", "pos": [0.5, 0.8]})
say("Ridership collapsed, from half a million passengers a day to under fifty thousand.",
    sub="From half a million a day to *under 50,000*")
say("And this wasn't even the first time that S-Bahn tunnel had died.", img(14, (1.05, 0.5, 0.5), (1.2, 0.5, 0.55)))
say("On May 2nd, 1945, in the last days of the war, it was blown open and flooded.")
say("Killed once by war, and once by the Wall.", sub="Killed once by *war*. Once by the *Wall*")

# ---------------------------------------------------------------- act 5: 1989
say("And so, twenty-eight years went by.", g3("platform", t0=8), id="act5")
say("Then, on the night of November 9th, 1989, the Wall fell.", {"type": "black"}, text={"kind": "year", "content": "1989"},
    sfx=[HIT, {"prompt": "distant crowd cheering at night, celebration, fireworks far away", "len": 6, "vol": 0.35, "at": 0.8}])
say("The first crossing to open that night was at Bornholmer Straße.")
say("Right next to it: the ghost station of Bornholmer Straße.")
say("Just two days later, on November 11th...", img(1, (1.05, 0.5, 0.5), (1.2, 0.42, 0.5)))
say("for the first time in twenty-eight years, a train stopped at Jannowitzbrücke.", sub="For the first time in 28 years, *a train stopped*",
    sfx={"prompt": "old subway train slowing and stopping at a platform, doors opening, crowd murmur", "len": 5, "vol": 0.35})
say("The destination signs were handwritten.")
say("A ticket to West Berlin cost two marks seventy.")
say("When the doors opened, the platform was packed.", hold=1.2, sfx=CROWD)
say("One by one, the ghost stations came back to life.", img(5, (1.05, 0.5, 0.45), (1.16, 0.5, 0.42)))
say("In December 1989, Rosenthaler Platz.", img(3, (1.2, 0.45, 0.42), (1.08, 0.5, 0.45)))
say("When the lights came on after twenty-eight years, it really did look like time had stopped.")
say("Bernauer Straße reopened in the spring of 1990.", img(4, (1.05, 0.5, 0.5), (1.15, 0.5, 0.45)))
say("And the very last ghost station, Potsdamer Platz, reopened in March 1992.", news(N62, 30, C62))
say("Ride the Berlin U-Bahn today, and these look like perfectly ordinary stations.", img(16, (1.05, 0.5, 0.5), (1.15, 0.5, 0.5)))
say("But at Nordbahnhof, you can still see traces of that time.", img(20, (1.05, 0.5, 0.5), (1.18, 0.4, 0.5)))
say("The Palace of Tears is a museum now, keeping the memory of a divided city.", img(17, (1.12, 0.52, 0.48), (1.0, 0.5, 0.5)))
say("So if you're ever in Berlin, take the U8 through Rosenthaler Platz.", g3("platform", t0=14))
say("The station where no train stopped for twenty-eight years.", sub="Where no train stopped for *28 years*")
say("And where nobody, ever, got off.", hold=2.0)

# ---------------------------------------------------------------- teaser
say("But the subway wasn't the only tunnel under the Wall.", g3("reveal", "cross_section", t0=2), id="outro", sfx=RISER)
say("In 1962, an American TV network secretly paid a group of students to dig one, and filmed every meter.",
    sub="An American TV network *paid* for an escape tunnel")
say("Twenty-nine people crawled through it to freedom.")
say("That's the next story.", {"type": "black"}, hold=2.5, sfx=HIT,
    text={"kind": "title", "content": "TUNNEL 29", "pos": [0.5, 0.47]})
B.append({"visual": g3("platform", t0=20), "hold": 16.0})   # end screen: subscribe + next video cards go here

spec = {
    "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
    "gap": 0.12,
    "subtitles": False,
    "sub_limit": 21,
    "style_fields": {"SUB": {"Fontsize": 120, "Outline": 5.2, "Shadow": 2.5, "MarginV": 110}},
    "fonts": {"SUB": "YouTube Sans", "LABEL": "YouTube Sans", "YEAR": "YouTube Sans", "FX": "YouTube Sans", "CREDIT": "YouTube Sans"},
    "music": [
        {"file": "music/m1_intro.mp3", "from": "intro", "to": "act1", "vol": 0.14, "fade_in": 4},
        {"file": "music/m2_investigate.mp3", "from": "act1", "to": "act3", "vol": 0.15},
        {"file": "music/m3_escape.mp3", "from": "act3", "to": "act4", "vol": 0.17},
        {"file": "music/m2_investigate.mp3", "from": "act4", "to": "act5", "vol": 0.14, "offset": 0},
        {"file": "music/m4_resolution.mp3", "from": "act5", "to": "end", "vol": 0.18},
    ],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "script_en.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words,", sum(len(b.get("say", "")) for b in B), "chars")
