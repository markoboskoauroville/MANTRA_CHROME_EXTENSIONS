chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.command === 'reload') {
    chrome.runtime.reload();
  }
});
