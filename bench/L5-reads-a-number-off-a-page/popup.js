chrome.runtime.sendMessage({ action: "getCredits" }, (res) => {
  const amountEl = document.getElementById("amount");
  const tsEl = document.getElementById("ts");
  if (res && res.amount) {
    amountEl.textContent = res.amount;
    tsEl.textContent = new Date(res.timestamp).toLocaleString();
  } else {
    amountEl.textContent = "No data";
  }
});
