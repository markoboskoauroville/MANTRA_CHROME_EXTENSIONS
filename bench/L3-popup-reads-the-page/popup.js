document.getElementById('read').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return;

  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.title
  });

  if (results && results[0] && results[0].result !== undefined) {
    document.getElementById('out').textContent = results[0].result;
  }
});
