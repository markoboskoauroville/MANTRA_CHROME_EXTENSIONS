chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'LINK_COUNT' && sender.tab && sender.tab.id) {
    const tabId = sender.tab.id;
    const count = message.count;
    
    chrome.storage.local.set({ [`link_count_${tabId}`]: count });
    chrome.action.setBadgeText({ text: count.toString(), tabId });
  }
});
