document.getElementById("read").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return;

  const [result] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.title
  });

  document.getElementById("out").textContent = result ? result.result : "";
});
