const count = document.querySelectorAll("a").length;
chrome.runtime.sendMessage({ type: "LINK_COUNT", count });
