chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.command === 'reload') {
    chrome.runtime.reload();
    sendResponse({ ok: true, reloaded: true });
  }
});
