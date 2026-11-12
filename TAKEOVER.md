# TAKEOVER: MANTRA_CHROME_EXTENSIONS (12.11.2026)

Public, unpromoted: no README and no description by rule (MANTRA_MANIFEST modules/repo-privacy.md). This file says what it is.

## What it is
The Chrome extensions Queen (Groq AI Studio) writes and Macro Recorder loads, plus the two tools that keep them honest.
Marko, 12.11.2026: "Groq AI Studio needs to have skills in how to build, update, and debug Chrome extensions to do the
work ... make a repository of mantra_chrome_extensions, and intelligently use them, loading them and unloading them to
do the work inside the web browser."

Extensions are the FAST path for acting inside a page. When a site detects or blocks them, the fallback is the real
keyboard and mouse in human-like patterns (skill `chrome-debug-control`, block `human-input` in MACRO_SKILLS).

| Path | What |
|---|---|
| `tools/extcheck.py` | the MV3 consistency linter: every file the manifest names exists, every file written is reachable, every `chrome.*` API is declared, every fetch host permitted, every `.js` parses. Prints the exact fix. |
| `tools/queen_bench.py` | the capability benchmark: seven extensions trivial to complex, graded mechanically. Produces `bench/results.json`. |
| `bench/L1..L7` | what Queen built on 12.11.2026, kept as evidence |
| `extensions/` | the real extensions (empty on 12.11.2026) |

## State on 12.11.2026
Benchmark run and reproduced: 4 of 7 clean, 3 broken, every failure the same defect (manifest and files disagree),
3 out of 3 on a repeat. Full write-up: `groq_ai_studio/PROFILE.md`. `extcheck.py` catches all three in under a second.

## Continue here
1. `extctl.py` is NOT written yet: load unpacked / reload / unload an extension per profile through Macro Recorder.
   Developer mode is per profile; remote debugging is one switch for the whole browser.
2. The first real extension: read the credit balance off the Claude Console page and report it to Queen
   (Anthropic exposes no balance to a normal API key, so the page is the only source).
3. Teach Queen `extcheck` and the two-strikes rule: fail the same check twice, escalate to Claude, write the skill.
4. Chrome's HTTP DevTools endpoints 404 even with remote debugging on (the UI toggle restricts them), and a direct
   WebSocket to the browser target timed out. There is no CDP channel today: extensions or real input.

No build step: Python and plain extension files. One branch, main.
