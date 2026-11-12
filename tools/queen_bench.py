#!/usr/bin/env python3
"""queen_bench: how far up the Chrome-extension ladder can Queen (Groq AI Studio) be trusted alone?

Marko, 12.11.2026: "Do the comprehensive test using Groq Studio by starting to build the most basic Chrome extensions
until the most complex one, and please assess its intelligence until which level we can leave him unsupervised, and from
which level we need to supervise him."

Each level is a spec. Queen writes the files. We grade MECHANICALLY (no opinion):
  manifest parses · required MV3 fields · every declared file exists · every .js parses (node --check)
  · the behaviour markers the level requires are present · no forbidden MV2 leftovers.
A level PASSES only if every check passes.

    queen_bench.py run [--levels 1,2,3] [--model M]     build and grade
    queen_bench.py report                                read the last results
"""
import json, re, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "bench"
QUEEN = "http://127.0.0.1:8765"
TOKEN = (Path.home() / ".groq" / "api_token").read_text().strip() if (Path.home() / ".groq" / "api_token").exists() else ""

FORMAT = """Output ONLY files, nothing else, each in this exact shape and no markdown fences:

=== FILE: manifest.json ===
<the whole file>
=== FILE: content.js ===
<the whole file>

Rules: Chrome Manifest V3 only. No background "scripts" array, no "browser_action", no remote code.
Every file you name in the manifest must be written out. No commentary before or after the files."""

LEVELS = [
    dict(n=1, name="valid manifest",
         spec='A Manifest V3 Chrome extension called "Mantra Hello", version 1.0.0, description "Says hello." '
              'Only manifest.json is needed. No scripts.',
         need_files=["manifest.json"], markers=[], mf=dict()),
    dict(n=2, name="content script",
         spec='A Manifest V3 extension "Mantra Mark" that runs a content script on https://example.com/* which '
              'sets document.title to "MANTRA". Files: manifest.json, content.js.',
         need_files=["manifest.json", "content.js"], markers=[("content.js", r"document\.title")],
         mf=dict(content_scripts=True)),
    dict(n=3, name="popup reads the page",
         spec='A Manifest V3 extension "Mantra Peek" with a popup (popup.html + popup.js). The popup has a button '
              '#read; pressing it uses chrome.scripting.executeScript on the active tab to get document.title and '
              'shows it in #out. Needs permissions "activeTab" and "scripting". Files: manifest.json, popup.html, popup.js.',
         need_files=["manifest.json", "popup.html", "popup.js"],
         markers=[("popup.js", r"chrome\.scripting\.executeScript"), ("popup.html", r'id=["\']read')],
         mf=dict(action=True, perms=["scripting"])),
    dict(n=4, name="service worker + storage + badge",
         spec='A Manifest V3 extension "Mantra Count" whose content script counts the <a> links on every page and '
              'sends the number to a background service worker, which saves it with chrome.storage.local and shows it '
              'with chrome.action.setBadgeText. Files: manifest.json, content.js, background.js.',
         need_files=["manifest.json", "content.js", "background.js"],
         markers=[("background.js", r"chrome\.storage\.local"), ("background.js", r"setBadgeText"),
                  ("content.js", r"querySelectorAll"), ("background.js", r"onMessage")],
         mf=dict(sw=True, action=True)),
    dict(n=5, name="reads a number off a page",
         spec='A Manifest V3 extension "Mantra Credits" with a content script on https://platform.claude.com/* that '
              'finds the first dollar amount on the page (a string like $12.34 or $1,234.56), and stores it with '
              'chrome.storage.local under the key "credits" together with a timestamp. A service worker re-reads it '
              'when the popup asks. Files: manifest.json, content.js, background.js.',
         need_files=["manifest.json", "content.js", "background.js"],
         markers=[("content.js", r"\\\$|\$"), ("content.js", r"chrome\.storage\.local|chrome\.runtime\.sendMessage"),
                  ("manifest.json", r"platform\.claude\.com")],
         mf=dict(content_scripts=True)),
    dict(n=6, name="command bridge to a local server",
         spec='A Manifest V3 extension "Mantra Bridge". Its service worker polls http://127.0.0.1:8765/api/ext/poll '
              'every 2 seconds with fetch. Each reply may contain {"id":..., "action":"click"|"type"|"read", '
              '"selector":"...", "text":"..."}. The worker forwards the command to the active tab content script, '
              'which performs it on the DOM and returns a result; the worker POSTs the result back to '
              'http://127.0.0.1:8765/api/ext/result. Handle fetch errors without crashing the worker. '
              'Files: manifest.json, background.js, content.js.',
         need_files=["manifest.json", "background.js", "content.js"],
         markers=[("background.js", r"127\.0\.0\.1:8765"), ("background.js", r"catch"),
                  ("content.js", r"querySelector"), ("background.js", r"tabs\.sendMessage|scripting")],
         mf=dict(sw=True, hosts=["127.0.0.1"])),
    dict(n=7, name="human-like typing, retries, self-reload",
         spec='A Manifest V3 extension "Mantra Hands". Content script exposes typeHuman(selector, text) which types '
              'character by character with a random delay of 45-150 ms, dispatching real input and keydown events so '
              'frameworks notice, and clickHuman(selector) which scrolls the element into view, waits 120-400 ms, then '
              'clicks. Both retry up to 3 times with a growing delay if the selector is not found yet. The service '
              'worker exposes a "reload" command that calls chrome.runtime.reload(). '
              'Files: manifest.json, background.js, content.js.',
         need_files=["manifest.json", "background.js", "content.js"],
         markers=[("content.js", r"typeHuman"), ("content.js", r"clickHuman"),
                  ("content.js", r"Math\.random"), ("content.js", r"dispatchEvent"),
                  ("background.js", r"chrome\.runtime\.reload")],
         mf=dict(sw=True)),
]


def ask(prompt, model=None):
    # fresh: each level is independent (12.11.2026 - see queen_stress.py)
    body = {"prompt": prompt, "mode": "code", "fresh": True}
    if model:
        body["model"] = model
    req = urllib.request.Request(f"{QUEEN}/api/remote/send", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "X-Queen-Token": TOKEN})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return d.get("reply", ""), d.get("telemetry", {}), round(time.time() - t0, 1)


def split_files(text):
    # The qwen models think out loud in <think>...</think>, and that reasoning QUOTES the "=== FILE: x ===" format
    # from the instructions. Reading it as output made Queen look like she wrote a broken content.js when she had
    # actually reasoned "only manifest.json is needed" (12.11.2026). Strip the thinking first, and when a filename
    # appears twice keep the LAST block - the real answer comes after the reasoning.
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<think>.*", "", text, flags=re.S | re.I)      # an unclosed think block eats the rest
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^\s*===\s*FILE:\s*(.+?)\s*===\s*$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
            continue
        if cur is not None:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    # strip stray markdown fences the model may still add
    for k, v in out.items():
        v = re.sub(r"^```[a-zA-Z]*\n", "", v)
        v = re.sub(r"\n```$", "", v)
        out[k] = v.strip()
    return out


def grade(lv, files, d):
    checks = []

    def add(ok, label, detail=""):
        checks.append({"ok": bool(ok), "check": label, "detail": detail})

    for f in lv["need_files"]:
        add(f in files and files[f].strip(), f"file {f} written")

    mf = None
    if "manifest.json" in files:
        try:
            mf = json.loads(files["manifest.json"])
            add(True, "manifest.json parses")
        except Exception as e:
            add(False, "manifest.json parses", str(e)[:90])
    else:
        add(False, "manifest.json parses", "missing")

    if mf:
        add(mf.get("manifest_version") == 3, "manifest_version is 3", str(mf.get("manifest_version")))
        add(bool(mf.get("name")) and bool(mf.get("version")), "has name and version")
        add("background" not in mf or "scripts" not in (mf.get("background") or {}),
            "no MV2 background.scripts")
        add("browser_action" not in mf, "no MV2 browser_action")
        want = lv["mf"]
        if want.get("sw"):
            add(bool((mf.get("background") or {}).get("service_worker")), "declares a service worker")
        if want.get("content_scripts"):
            add(bool(mf.get("content_scripts")), "declares content_scripts")
        if want.get("action"):
            # "action": {} is correct and complete; bool({}) is False, so test for the KEY (12.11.2026)
            add("action" in mf, "declares action (popup)")
        for p in want.get("perms", []):
            add(p in (mf.get("permissions") or []), f"permission {p}")
        for h in want.get("hosts", []):
            blob = json.dumps(mf)
            add(h in blob, f"host {h} declared")
        # every file the manifest names must exist
        named = set(re.findall(r'"([A-Za-z0-9_\-/]+\.(?:js|html|css|json|png))"', json.dumps(mf)))
        missing = [n for n in named if n not in files and not n.endswith(".png")]
        add(not missing, "every file the manifest names was written", ",".join(missing))

    for fn, content in files.items():
        if fn.endswith(".js"):
            p = d / fn
            r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
            add(r.returncode == 0, f"{fn} parses as JavaScript", (r.stderr or "").strip().splitlines()[-1][:90] if r.returncode else "")

    for fn, pat in lv["markers"]:
        body = files.get(fn, "")
        add(re.search(pat, body) is not None, f"{fn} contains {pat}")

    passed = all(c["ok"] for c in checks)
    return passed, checks


def run(levels, model=None):
    OUT.mkdir(exist_ok=True)
    results, spent = [], 0.0
    for lv in LEVELS:
        if levels and lv["n"] not in levels:
            continue
        d = OUT / f'L{lv["n"]}-{lv["name"].replace(" ", "-")}'
        d.mkdir(parents=True, exist_ok=True)
        print(f'\n=== L{lv["n"]}  {lv["name"]} ===')
        reply, tel, secs = ask(lv["spec"] + "\n\n" + FORMAT, model)
        cost = float(tel.get("cost", 0) or 0)
        spent += cost
        files = split_files(reply)
        if not files:
            files = {"RAW.txt": reply}
        for fn, body in files.items():
            (d / fn).parent.mkdir(parents=True, exist_ok=True)
            (d / fn).write_text(body + "\n")
        ok, checks = grade(lv, files, d)
        bad = [c for c in checks if not c["ok"]]
        print(f'  {"PASS" if ok else "FAIL"}  {len(checks)-len(bad)}/{len(checks)} checks · {secs}s · ${cost:.4f} · files: {", ".join(files)}')
        for c in bad:
            print(f'     x {c["check"]}' + (f'  ({c["detail"]})' if c["detail"] else ""))
        results.append({"level": lv["n"], "name": lv["name"], "pass": ok,
                        "checks_total": len(checks), "checks_failed": len(bad),
                        "failed": [c["check"] for c in bad], "secs": secs, "cost_usd": cost,
                        "model": tel.get("model", ""), "files": list(files)})
    (OUT / "results.json").write_text(json.dumps({"when": time.strftime("%Y-%m-%d %H:%M"),
                                                  "total_cost_usd": round(spent, 5),
                                                  "results": results}, indent=2))
    print(f'\ntotal spent: ${spent:.4f}   results: {OUT / "results.json"}')
    return results


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "report":
        print((OUT / "results.json").read_text()); sys.exit(0)
    lv = []
    if "--levels" in a:
        lv = [int(x) for x in a[a.index("--levels") + 1].split(",")]
    model = a[a.index("--model") + 1] if "--model" in a else None
    run(lv, model)
