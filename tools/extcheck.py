#!/usr/bin/env python3
"""extcheck: does this Manifest V3 extension hang together? The linter for Queen's blind spot.

Chrome loads an extension whose manifest and files disagree and then fails SILENTLY at runtime:
a content script nobody declares never runs; chrome.action without "action" in the manifest throws;
a file the manifest names and nobody wrote stops the whole extension loading.

    extcheck <dir> [--json]      check one unpacked extension
    extcheck <dir> --fix-report  also print the exact manifest lines that would fix it

Exit 0 clean, 1 problems found. Written 12.11.2026.
"""
import json, re, subprocess, sys
from pathlib import Path

# chrome.<api> -> what the manifest must contain for it to work
API_NEEDS = {
    "action": ("action key", lambda m: "action" in m),
    "storage": ("permission storage", lambda m: "storage" in (m.get("permissions") or [])),
    "scripting": ("permission scripting", lambda m: "scripting" in (m.get("permissions") or [])),
    "alarms": ("permission alarms", lambda m: "alarms" in (m.get("permissions") or [])),
    "cookies": ("permission cookies", lambda m: "cookies" in (m.get("permissions") or [])),
    "notifications": ("permission notifications", lambda m: "notifications" in (m.get("permissions") or [])),
    "contextMenus": ("permission contextMenus", lambda m: "contextMenus" in (m.get("permissions") or [])),
    "webRequest": ("permission webRequest", lambda m: "webRequest" in (m.get("permissions") or [])),
    "downloads": ("permission downloads", lambda m: "downloads" in (m.get("permissions") or [])),
}


def check(d):
    d = Path(d)
    problems, notes = [], []
    mfp = d / "manifest.json"
    if not mfp.exists():
        return [{"level": "error", "what": "no manifest.json"}], []
    try:
        m = json.loads(mfp.read_text())
    except Exception as e:
        return [{"level": "error", "what": f"manifest.json does not parse: {e}"}], []

    blob = json.dumps(m)
    on_disk = {p.name for p in d.iterdir() if p.is_file()}
    written_code = {f for f in on_disk if f.endswith((".js", ".html", ".css"))}

    if m.get("manifest_version") != 3:
        problems.append({"level": "error", "what": f'manifest_version is {m.get("manifest_version")}, must be 3'})
    for k in ("name", "version"):
        if not m.get(k):
            problems.append({"level": "error", "what": f'manifest has no "{k}"'})
    if "scripts" in (m.get("background") or {}):
        problems.append({"level": "error", "what": 'MV2 leftover: background.scripts (MV3 uses background.service_worker)'})
    if "browser_action" in m:
        problems.append({"level": "error", "what": 'MV2 leftover: browser_action (MV3 uses action)'})

    # 1. every file the manifest names must exist
    named = set(re.findall(r'"([A-Za-z0-9_\-./]+\.(?:js|html|css|json|png|svg))"', blob))
    for n in sorted(named):
        if n.lstrip("./") not in on_disk:
            problems.append({"level": "error", "what": f'manifest names "{n}" but that file was not written',
                             "fix": f"write {n}, or remove it from the manifest"})

    # 2. every code file written must be reachable
    reachable = set()
    for n in named:
        reachable.add(n.lstrip("./"))
    for h in [f for f in on_disk if f.endswith(".html")]:
        body = (d / h).read_text(errors="ignore")
        for ref in re.findall(r'(?:src|href)="([^"]+)"', body):
            reachable.add(ref.lstrip("./"))
    for j in [f for f in on_disk if f.endswith(".js")]:
        body = (d / j).read_text(errors="ignore")
        for ref in re.findall(r'files\s*:\s*\[([^\]]*)\]', body):      # scripting.executeScript({files:[...]})
            for q in re.findall(r'["\']([^"\']+)["\']', ref):
                reachable.add(q.lstrip("./"))
        for ref in re.findall(r'importScripts\(([^)]*)\)', body):
            for q in re.findall(r'["\']([^"\']+)["\']', ref):
                reachable.add(q.lstrip("./"))
        for ref in re.findall(r'getURL\(\s*["\']([^"\']+)["\']', body):
            reachable.add(ref.lstrip("./"))
    for f in sorted(written_code - reachable):
        problems.append({"level": "error", "what": f'"{f}" was written but nothing loads it: it will never run',
                         "fix": f'declare {f} in content_scripts/action/background, inject it with '
                                f'chrome.scripting.executeScript({{files:["{f}"]}}), or delete it'})

    # 3. every chrome API used must be declared
    used = {}
    for j in [f for f in on_disk if f.endswith((".js", ".html"))]:
        for api in re.findall(r'chrome\.([A-Za-z]+)\s*\.', (d / j).read_text(errors="ignore")):
            used.setdefault(api, set()).add(j)
    for api, where in sorted(used.items()):
        if api in API_NEEDS:
            label, ok = API_NEEDS[api]
            if not ok(m):
                problems.append({"level": "error",
                                 "what": f'chrome.{api} is used in {", ".join(sorted(where))} but the manifest has no {label}',
                                 "fix": (f'add "action": {{}} to the manifest' if api == "action"
                                         else f'add "{api}" to "permissions"')})

    # 3b. chrome.tabs: tab.id is fine under activeTab; tab.url / tab.title are not
    if "tabs" in used and "tabs" not in (m.get("permissions") or []):
        reads_detail = False
        for j in used["tabs"]:
            body = (d / j).read_text(errors="ignore")
            if re.search(r"\btab\w*\.(url|title)\b", body) or re.search(r"tabs\[\d+\]\.(url|title)", body):
                reads_detail = True
        if reads_detail and not (m.get("host_permissions") or []):
            problems.append({"level": "error",
                             "what": f'chrome.tabs reads .url/.title in {", ".join(sorted(used["tabs"]))} but the '
                                     f'manifest has no "tabs" permission and no host_permissions (they come back undefined)',
                             "fix": 'add "tabs" to "permissions", or a host_permissions entry'})
        elif "activeTab" not in (m.get("permissions") or []):
            notes.append('chrome.tabs is used with neither "tabs" nor "activeTab": most calls will be refused')

    # 4. fetch to a host that is not permitted
    hosts = set(m.get("host_permissions") or [])
    for j in [f for f in on_disk if f.endswith(".js")]:
        for url in re.findall(r'fetch\(\s*["\'`](https?://[^"\'`/]+)', (d / j).read_text(errors="ignore")):
            host = url.split("//")[1]
            if not any(host in h or h.replace("*", "") in url for h in hosts):
                problems.append({"level": "error",
                                 "what": f'{j} fetches {url} but no host_permissions entry covers it',
                                 "fix": f'add "{url}/*" to "host_permissions"'})

    # 5. javascript must parse
    for j in sorted(f for f in on_disk if f.endswith(".js")):
        r = subprocess.run(["node", "--check", str(d / j)], capture_output=True, text=True)
        if r.returncode:
            problems.append({"level": "error", "what": f"{j} is not valid JavaScript",
                             "fix": (r.stderr or "").strip().splitlines()[-1][:120]})

    if not m.get("description"):
        notes.append("no description (Chrome shows an empty card)")
    if not any(k.startswith("icon") for k in m):
        notes.append("no icons declared")
    return problems, notes


def main(argv):
    if not argv:
        print(__doc__); return 2
    d = argv[0]
    problems, notes = check(d)
    if "--json" in argv:
        print(json.dumps({"dir": d, "ok": not problems, "problems": problems, "notes": notes}, indent=2))
        return 1 if problems else 0
    print(f"extcheck {d}")
    for p in problems:
        print(f'  ERROR  {p["what"]}')
        if p.get("fix") and "--fix-report" in argv:
            print(f'         fix: {p["fix"]}')
    for n in notes:
        print(f'  note   {n}')
    print("  clean" if not problems else f'  {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
