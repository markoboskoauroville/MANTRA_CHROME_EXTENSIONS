chrome.runtime.onMessage.addListener(function (msg, _sender, sendResponse) {
  if (msg && msg.type === "getCredits") {
    chrome.storage.local.get("credits", function (result) {
      sendResponse(result.credits || null);
    });
    return true;
  }
});
