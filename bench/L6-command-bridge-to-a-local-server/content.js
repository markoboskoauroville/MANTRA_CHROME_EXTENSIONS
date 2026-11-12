chrome.runtime.onMessage.addListener((msg) => {
  return new Promise((resolve) => {
    try {
      if (!msg || !msg.action || !msg.selector) {
        resolve({ id: msg && msg.id, ok: false, error: "missing action or selector" });
        return;
      }

      const el = document.querySelector(msg.selector);
      if (!el) {
        resolve({ id: msg.id, ok: false, error: "element not found", selector: msg.selector });
        return;
      }

      let result;
      switch (msg.action) {
        case "click":
          el.click();
          result = { id: msg.id, ok: true, action: "click", selector: msg.selector, detail: "clicked" };
          break;

        case "type":
          el.focus();
          if (el.isContentEditable) {
            el.textContent = msg.text || "";
          } else {
            el.value = msg.text || "";
          }
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
          result = { id: msg.id, ok: true, action: "type", selector: msg.selector, detail: msg.text || "" };
          break;

        case "read": {
          const value = (el.value !== undefined && el.value !== null)
            ? el.value
            : el.textContent;
          result = { id: msg.id, ok: true, action: "read", selector: msg.selector, detail: value };
          break;
        }

        default:
          result = { id: msg.id, ok: false, error: "unknown action: " + msg.action };
      }

      resolve(result);
    } catch (err) {
      resolve({ id: msg && msg.id, ok: false, error: String(err) });
    }
  });
});
