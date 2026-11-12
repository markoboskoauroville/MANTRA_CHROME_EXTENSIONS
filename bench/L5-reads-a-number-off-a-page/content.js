(() => {
  const text = document.body.innerText;
  const match = text.match(/\$[\d,]+(\.\d+)?/);
  if (match) {
    chrome.storage.local.set({
      credits: match[0],
      timestamp: Date.now()
    });
  }
})();
