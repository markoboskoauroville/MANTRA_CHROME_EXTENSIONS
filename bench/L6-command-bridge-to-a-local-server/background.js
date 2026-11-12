const POLL_URL = "http://127.0.0.1:8765/api/ext/poll";
const RESULT_URL = "http://127.0.0.1:8765/api/ext/result";
const POLL_INTERVAL_MS = 2000;

async function executeAndReport(command) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return;

  let result;
  try {
    result = await chrome.tabs.sendMessage(tab.id, {
      id: command.id,
      action: command.action,
      selector: command.selector,
      text: command.text
    });
  } catch (err) {
    result = { id: command.id, ok: false, error: String(err) };
  }

  const payload = result || { id: command.id, ok: false, error: "no response from content script" };
  try {
    await fetch(RESULT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.warn("[Mantra Bridge] result POST failed:", err);
  }
}

async function poll() {
  try {
    const res = await fetch(POLL_URL, { method: "GET" });
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.action) {
      await executeAndReport(data);
    }
  } catch (err) {
    console.warn("[Mantra Bridge] poll error (worker stays alive):", err);
  }
}

function scheduleNext() {
  setTimeout(poll, POLL_INTERVAL_MS);
}

poll();
scheduleNext();
