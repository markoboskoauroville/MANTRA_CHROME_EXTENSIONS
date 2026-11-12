(function () {
  "use strict";
  var text = document.body ? document.body.innerText : "";
  var match = text.match(/\$[\d,]+(?:\.\d{1,2})?/);
  if (match) {
    chrome.storage.local.set({
      credits: {
        amount: match[0],
        timestamp: new Date().toISOString()
      }
    });
  }
})();
