chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== "LINK_COUNT") return;
  const n = msg.count;
  chrome.storage.local.set({ linkCount: n });
  chrome.action.setBadgeText({ text: String(n) });
});
