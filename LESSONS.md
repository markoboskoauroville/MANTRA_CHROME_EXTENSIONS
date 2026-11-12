# LESSONS: MANTRA_CHROME_EXTENSIONS

- **12.11.2026, Queen's one defect.** Every failing extension failed the same way: the manifest and the files disagree.
  `chrome.action` used with no `"action"` key; `popup.html` named and never written; `content.js` written, never
  declared, never injected. The JavaScript was always valid and always did the task. Check declarations, not logic.
- **12.11.2026, a benchmark needs its own audit.** My first grader passed L7, which had written a content script the
  manifest never loads. The grader only checked what each level's spec listed. A generic rule - every written file must
  be reachable, every API used must be declared - found it. Grade with general rules, not a per-case list.
- **12.11.2026, avoid false positives.** The first version flagged `chrome.tabs` without the `"tabs"` permission, but
  `tab.id` works under `activeTab`; only `.url` and `.title` need more. A linter that cries wolf gets ignored.
- **12.11.2026, no CDP.** Remote debugging on, Chrome listening on 9222, and `/json`, `/json/list`, `/json/version` all
  404; a direct WebSocket to the browser target timed out. Switching it on through the page does not open the HTTP
  discovery endpoints the way the command-line flag does. Do not plan on CDP.
- **12.11.2026, the Claude Usage Tracker is not the answer for credits.** It is GPL-3 (so copying it into a public repo
  makes that repo GPL-3) and it tracks claude.ai chat quota, not platform.claude.com API credits. Write our own.
