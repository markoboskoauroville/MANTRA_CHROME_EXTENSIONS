const POLL_URL = 'http://127.0.0.1:8765/api/ext/poll';
const RESULT_URL = 'http://127.0.0.1:8765/api/ext/result';
const POLL_INTERVAL = 2000;

let polling = false;

async function poll() {
  if (polling) return;
  polling = true;
  
  try {
    const res = await fetch(POLL_URL, { method: 'GET' });
    if (!res.ok) return;
    
    const action = await res.json();
    
    if (action && action.id && action.action) {
      // Get the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        try {
          // Inject content script if not already present (optional, assuming persistent content script or re-injection)
          // For robustness, we ensure the script is there. Since we defined content_scripts in manifest, it's already there on load.
          // But if the page reloaded after extension install, it's there.
          
          const results = await chrome.tabs.sendMessage(tab.id, {
            type: 'EXECUTE',
            command: action
          });
          
          // Send result back to local server
          await fetch(RESULT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id: action.id,
              result: results
            })
          });
        } catch (err) {
          // Error communicating with content script
          await fetch(RESULT_URL, {
            message: 'FAILED_TO_EXECUTE',
            error: err.message,
            id: action.id
          });
        }
      }
    }
  } catch (e) {
    // Network error or fetch failed, ignore to prevent crash
    console.error('Poll error:', e);
  } finally {
    polling = false;
  }
}

// Start polling loop
setInterval(poll, POLL_INTERVAL);
// Initial poll
poll();
