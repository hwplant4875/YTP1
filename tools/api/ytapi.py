"""YTP1 helper that runs heavy reading jobs on the Console API credits instead of
the claude.ai subscription. The thread runs this and reads only the short result.

Key: env TIMELAPSE_API_KEY (or ANTHROPIC_API_KEY). Never pass the key on the command line.

  python tools/api/ytapi.py digest comments.json transcript.txt --goal "what viewers want"
  python tools/api/ytapi.py qa video.mp4 [--srt subs.srt] [--every 2] [--max 60]
  python tools/api/ytapi.py kit script.md --channel "PEEK." [--rules rules.md]

Every run prints its token use and cost at the end (stderr).
"""
import argparse, base64, glob, os, re, subprocess, sys, tempfile

import anthropic

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
# $ per 1M tokens: input, output
PRICE = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0)}

QA_RULES = """Check this finished video for delivery problems. Rules of this project:
- No covered or overlapping text, text inside the safe area (clear of the right-side buttons and bottom title on shorts).
- No visual artifacts, glitches, stretched or cut-off images, awkward pop-ins.
- Frame 0 must be a full opening image usable as a cover.
- Subtitles big and readable, no typos.
- Drawn front-facing faces have two eyes.
Report ONLY real problems as lines "MM:SS - problem - fix". If nothing is wrong, say "OK"."""


def client():
    key = os.environ.get("TIMELAPSE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("No API key: set TIMELAPSE_API_KEY")
    return anthropic.Anthropic(api_key=key)


def ask(model, content, effort, max_tokens=16000):
    msg = client().messages.create(
        model=model, max_tokens=max_tokens,
        output_config={"effort": effort},
        messages=[{"role": "user", "content": content}],
    )
    if msg.stop_reason == "refusal":
        sys.exit("Model refused this request")
    u = msg.usage
    pin, pout = PRICE[model]
    cost = (u.input_tokens * pin + u.output_tokens * pout) / 1e6
    print(f"[{model}] in {u.input_tokens} out {u.output_tokens} tokens, ${cost:.4f}", file=sys.stderr)
    return "".join(b.text for b in msg.content if b.type == "text")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def cmd_digest(a):
    docs = "\n\n".join(f"<file name='{os.path.basename(p)}'>\n{read(p)}\n</file>" for p in a.files)
    prompt = (f"{docs}\n\nThese are YouTube comments and/or transcripts. Goal: {a.goal}\n"
              "Give a compact digest (max 25 lines): repeated viewer phrases (quoted), questions, "
              "complaints, what they want next, and hook/title ideas that come straight from their words. "
              f"Answer in {a.lang}.")
    print(ask(MODELS[a.model], prompt, "low"))


def cmd_qa(a):
    tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-vf",
                    f"fps=1/{a.every},scale=640:-2", "-frames:v", str(a.max), f"{tmp}/f%03d.jpg"], check=True)
    # Silences are found locally for free; the model only judges the frames.
    sil = subprocess.run(["ffmpeg", "-i", a.video, "-af", "silencedetect=n=-45dB:d=1.5", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    silences = re.findall(r"silence_start: ([\d.]+)", sil)
    content = []
    for i, p in enumerate(sorted(glob.glob(f"{tmp}/f*.jpg"))):
        t = i * a.every
        content.append({"type": "text", "text": f"{t // 60:02d}:{t % 60:02d}"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                     "data": base64.standard_b64encode(open(p, "rb").read()).decode()}})
    text = QA_RULES
    if a.srt:
        text += f"\n\nSubtitles (check typos and timing):\n{read(a.srt)}"
    content.append({"type": "text", "text": text})
    print(ask(MODELS[a.model], content, "medium"))
    print("Silences over 1.5 s at (s): " + (", ".join(silences) if silences else "none"))


def cmd_kit(a):
    rules = read(a.rules) if a.rules else ""
    prompt = (f"<script>\n{read(a.script)}\n</script>\n{rules}\n\nChannel: {a.channel}. Make the YouTube upload kit:\n"
              "1. Three title options (simple English, no ':' or '-', e.g. 'The Entire History of X in N Minutes').\n"
              "2. Description (hook line, 2 short paragraphs).\n"
              "3. Chapters: few, big sections, with timestamps if the script has them.\n"
              "4. Tags: 8-12 simple popular ones only, comma separated.\n"
              "5. One short IG/TikTok caption with 3-5 hashtags.")
    print(ask(MODELS[a.model], prompt, "medium"))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("digest"); d.add_argument("files", nargs="+"); d.add_argument("--goal", default="audience research")
    d.add_argument("--lang", default="Korean"); d.add_argument("--model", default="haiku", choices=MODELS)
    q = sub.add_parser("qa"); q.add_argument("video"); q.add_argument("--srt"); q.add_argument("--every", type=int, default=2)
    q.add_argument("--max", type=int, default=60); q.add_argument("--model", default="sonnet", choices=MODELS)
    k = sub.add_parser("kit"); k.add_argument("script"); k.add_argument("--channel", required=True); k.add_argument("--rules")
    k.add_argument("--model", default="sonnet", choices=MODELS)
    a = p.parse_args()
    {"digest": cmd_digest, "qa": cmd_qa, "kit": cmd_kit}[a.cmd](a)


if __name__ == "__main__":
    main()
