"""Run a headless Claude agent on the timelapse repo via the Claude Agent SDK, billed to the org's API key
(promotional credits apply to "Agent SDK / API", not to the Claude Code CLI).

    python tools/sdk_agent.py "task text"            (or: --file task.md)  [--model opus|sonnet] [--resume SESSION_ID]

The key is read from the user env var YTP_TIMELAPSE_KEY and passed only to this process (never printed).
Log: tools/sdk_logs/<timestamp>.log (assistant text, tool calls, result, cost).  The session id is printed so a
follow-up can --resume the same conversation.
"""
import argparse, asyncio, datetime, os, sys, winreg

REPO = r"E:\YTP2\3D Timelapse\repo\timelapse3d"
LOGD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdk_logs")

def user_env(name):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]

ap = argparse.ArgumentParser()
ap.add_argument("task", nargs="?", default="")
ap.add_argument("--file")
ap.add_argument("--model", default="opus")
ap.add_argument("--resume")
ap.add_argument("--max-turns", type=int, default=400)
ap.add_argument("--budget", type=float, default=20.0, help="stop the run when total_cost_usd passes this (USD)")
a = ap.parse_args()
task = open(a.file, encoding="utf-8").read() if a.file else a.task
if not task:
    sys.exit("no task")
os.environ["ANTHROPIC_API_KEY"] = user_env("YTP_TIMELAPSE_KEY")

from claude_agent_sdk import query, ClaudeAgentOptions

RULES = ("Binding: work only inside E:\\YTP2; never delete existing files outside your own outputs; no uploads; no final/"
         "hi-res render; previews 480p 15 fps + one contact sheet per segment. "
         "You work on the AoT 3D sky-view timelapse repo (cwd). Stay inside E:\\YTP2. Read HANDOFF.md 'RESUME 10/27' "
         "first. Lean rules: no subagents, small targeted edits, one 480p 15 fps preview + contact sheet per segment, "
         "use the GPU lock, push every render version-labelled to renders/laptop/ with git (branch "
         "claude/project-thread-4b2beh; pull --rebase --autostash before push). Never print secrets. "
         "CHECKPOINT rule: after each finished segment/sub-task, git commit + push and append a 2-line progress note to "
         "HANDOFF.md, so a budget stop loses at most one step. Start long Blender renders as DETACHED processes "
         "(e.g. PowerShell Start-Process / nohup) writing to a log, so they survive this agent exiting.")

async def main():
    os.makedirs(LOGD, exist_ok=True)
    log = open(os.path.join(LOGD, datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"), "w", encoding="utf-8")
    opts = ClaudeAgentOptions(model=a.model, cwd=REPO, max_turns=a.max_turns, resume=a.resume,
                              system_prompt={"type": "preset", "preset": "claude_code", "append": RULES},
                              permission_mode="acceptEdits", max_budget_usd=a.budget, max_buffer_size=50 * 1024 * 1024,
                              allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"], setting_sources=["project"])
    async for m in query(prompt=task, options=opts):
        n = type(m).__name__
        if n == "SystemMessage" and getattr(m, "subtype", "") == "init":
            sid = (getattr(m, "data", {}) or {}).get("session_id")
            line = f"[start] session={sid}"
            print(line, flush=True); log.write(line + "\n")
        if n == "AssistantMessage":
            for b in m.content:
                bn = type(b).__name__
                line = (b.text if bn == "TextBlock" else f"[tool] {getattr(b, 'name', '')} {str(getattr(b, 'input', ''))[:300]}"
                        if bn == "ToolUseBlock" else "")
                if line:
                    print(line, flush=True); log.write(line + "\n"); log.flush()
        elif n == "ResultMessage":
            line = (f"[result] session={m.session_id} turns={m.num_turns} cost=${(m.total_cost_usd or 0):.2f} "
                    f"error={m.is_error}\n{m.result or ''}")
            print(line, flush=True); log.write(line + "\n")
            if "budget" in str(getattr(m, "subtype", "")).lower() or (m.total_cost_usd or 0) >= a.budget:
                line = f"BUDGET REACHED: rerun with --resume {m.session_id} --budget N to continue"
                print(line, flush=True); log.write(line + "\n")
    log.close()

sys.unraisablehook = lambda *_: None      # Windows proactor pipes print "I/O operation on closed pipe" at GC; harmless
asyncio.run(main())
sys.stdout.flush(); os._exit(0)
