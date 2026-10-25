# API credit tools ($100/month Console credits)

Heavy reading jobs run on the Console API (workspace key `TIMELAPSE_API_KEY`) so the
claude.ai weekly usage is spared. Plan: https://claude.ai/artifact/Ab43zsusnB1HVhR13jZmfg

## Cloud threads: `ytapi.py`

Needs `pip install anthropic` and the env secret `TIMELAPSE_API_KEY` (only sessions started
after the secret was added can see it). Never put the key in files, memory or commits.

| Command | Model (default) | Typical cost |
|---|---|---|
| `python tools/api/ytapi.py digest comments.json transcript.txt --goal "..."` | Haiku 5.5 | < $0.01 per video |
| `python tools/api/ytapi.py qa final.mp4 --srt final.srt` | Sonnet 5.5 | ~ $0.2 per video (60 frames) |
| `python tools/api/ytapi.py kit script.md --channel "PEEK."` | Sonnet 5.5 | ~ $0.02 per video |

`--model haiku|sonnet|opus` overrides. Each run prints tokens and cost to stderr.
QA silence detection (> 1.5 s) runs locally with ffmpeg and costs nothing.

## Laptop: 3D timelapse Claude Code on credits

Only Claude Code running ON the laptop can bill the API. A cloud thread that controls the
laptop still uses the subscription.

One time (cmd): make a second key in the same Console workspace named `laptop-timelapse`, then

    setx YTP_TIMELAPSE_KEY "paste-the-key-here"

Each 3D timelapse session (new cmd window):

    cd /d "E:\YTP2\3D Timelapse"
    set ANTHROPIC_API_KEY=%YTP_TIMELAPSE_KEY%
    claude --model sonnet

Approve "use this API key" when asked; `/status` shows API billing. Switch to `/model opus`
only when stuck. Normal sessions (no `set` line) keep using the subscription.
