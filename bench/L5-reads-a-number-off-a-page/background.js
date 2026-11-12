chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_CREDITS") {
    chrome.storage.local.get(["credits", "timestamp"]).then((data) => {
      sendResponse({ credits: data.credits || null, timestamp: data.timestamp || null });
    });
    return true;
  }
});
