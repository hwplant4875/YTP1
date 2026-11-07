"""Build the YouTube .srt and the chapter list from js/words.js.

usage: python3 tools/make_srt.py <out.srt> [chapters.txt]
Numbers are written as numerals ($2.8 trillion, 4.4%) so the captions read fast.
"""
import json, re, sys

MAXL = 42          # characters per line
MAXC = 2 * MAXL    # characters per cue
MAXD = 6.0         # seconds per cue

PHRASES = [  # spoken tokens (lowercase, no punctuation) -> caption text
    ("two point eight trillion dollars", "$2.8 trillion"),
    ("hundred-dollar bills", "$100 bills"),
    ("three thousand kilometers", "3,000 kilometers"),
    ("november fifth", "November 5th"),
    ("s and p five hundred", "S&P 500"),
    ("five hundred of", "500 of"),
    ("four point four percent", "4.4%"),
    ("five and a half percent", "5.5%"),
    ("two hundred dollars", "$200"),
    ("a hundred and eighty-two", "$182"),
    ("nine percent", "9%"),
    ("four hundred and fifty billion dollars", "$450 billion"),
    ("five hundred kilometers", "500 kilometers"),
    ("twenty-four billion", "24 billion"),
    ("eighteen and a half dollars", "$18.50"),
    ("three hundred million", "300 million"),
    ("one share in every eighty", "1 share in every 80"),
    ("seventy-nine", "79"),
    ("three percent", "3%"),
]
CHAPTERS = [("b01", "$2.8 trillion in $100 bills"),
            ("b03", "What happened on November 5th"),
            ("b04", "Inside Nvidia"),
            ("b05", "How a company's value works"),
            ("b07", "Where the money really went"),
            ("b09", "What it means for your savings")]


def load(path):
    s = open(path).read()
    off = json.loads(re.search(r'export const OFF = (\{.*?\});', s).group(1))
    words = json.loads(re.search(r'export const WORDS = (\{.*\});', s, re.S).group(1))
    toks = []
    for b in sorted(words):
        toks += [[w, a, z] for w, a, z in words[b]]
    return off, toks


def key(w):
    return re.sub(r"[^\w'\-]", "", w.lower())


def merge(toks):
    out, i = [], 0
    while i < len(toks):
        for spoken, text in PHRASES:
            p = spoken.split()
            seg = toks[i:i + len(p)]
            if len(seg) == len(p) and [key(t[0]) for t in seg] == p:
                tail = re.search(r"[^\w%$]*$", seg[-1][0]).group(0)
                out.append([text.replace(' ', '\u00a0') + tail, seg[0][1], seg[-1][2]])
                i += len(p)
                break
        else:
            out.append(toks[i])
            i += 1
    return out


WEAK = {'a', 'an', 'the', 'and', 'of', 'to', 'that', 'by', 'for', 'with',
        'its', 'their', 'your', 'our'}
BEFORE = {'becomes', 'but', 'so', 'because', 'which', 'that', 'when', 'until', 'yet', 'from',
          'before', 'times', 'only', 'the', 'a', 'it', 'is'}


def fits(seg):
    return len(' '.join(x[0] for x in seg)) <= MAXC and seg[-1][2] - seg[0][1] <= MAXD


def split(seg):
    """split one sentence into cues: whole if it fits, else at the best break, recursively"""
    if fits(seg) or len(seg) < 4:
        return [seg]
    best = None
    for k in range(2, len(seg) - 1):
        a, b = seg[:k], seg[k:]
        la, lb = len(' '.join(x[0] for x in a)), len(' '.join(x[0] for x in b))
        cost = abs(la - lb) / 10.0
        if a[-1][0][-1] in ',:;':
            cost -= 6
        elif b[0][0].lower() in BEFORE:
            cost -= 2
        else:
            cost += 4
        if len(b) < 3 or len(a) < 3:
            cost += 8
        if key(a[-1][0]) in WEAK:
            cost += 6
        if best is None or cost < best[0]:
            best = (cost, k)
    k = best[1]
    return split(seg[:k]) + split(seg[k:])


def cues(toks):
    res, cur = [], []
    for t in toks:
        cur.append(t)
        if t[0][-1] in '.?!':
            res += split(cur)
            cur = []
    if cur:
        res += split(cur)
    return res


def lines(text):
    if len(text) <= MAXL:
        return text
    ws, best = text.split(' '), None
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
        if len(a) <= MAXL and len(b) <= MAXL:
            score = abs(len(a) - len(b)) - (12 if a[-1] in ',:;' else 0) \
                + (10 if key(a.split()[-1]) in WEAK else 0)
            if best is None or score < best[0]:
                best = (score, a + '\n' + b)
    return best[1] if best else text


def ts(x):
    ms = int(round(x * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def main():
    off, toks = load('js/words.js')
    cs = cues(merge(toks))
    out = []
    for i, c in enumerate(cs):
        a = c[0][1]
        nxt = cs[i + 1][0][1] if i + 1 < len(cs) else off['end']
        z = min(max(c[-1][2] + 0.35, a + 1.0), nxt - 0.04)
        out.append('%d\n%s --> %s\n%s\n' % (i + 1, ts(a), ts(z), lines(' '.join(x[0] for x in c)).replace('\u00a0', ' ')))
    open(sys.argv[1], 'w').write('\n'.join(out))
    print(len(cs), 'cues ->', sys.argv[1])
    if len(sys.argv) > 2:
        ch = ['%d:%02d %s' % (int(off[b]) // 60 if b != 'b01' else 0,
                              int(off[b]) % 60 if b != 'b01' else 0, name) for b, name in CHAPTERS]
        open(sys.argv[2], 'w').write('\n'.join(ch) + '\n')
        print('\n'.join(ch))


if __name__ == '__main__':
    main()
