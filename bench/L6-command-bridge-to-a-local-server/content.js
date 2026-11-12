chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'EXECUTE') {
    const { action, selector, text } = message.command;
    
    try {
      let result = 'SUCCESS';
      
      if (!selector) {
        throw new Error('No selector provided');
      }
      
      const el = document.querySelector(selector);
      
      if (action === 'click') {
        if (el) {
          el.click();
        } else {
          throw new Error('Element not found for click');
        }
      } else if (action === 'type') {
        if (el) {
          // Set value directly for input/textarea, or dispatch events for contentEditable
          if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          } else {
            el.textContent = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
          }
        } else {
          throw new Error('Element not found for type');
        }
      } else if (action === 'read') {
        if (el) {
          // Return visible text or value
          result = el.innerText || el.value || el.textContent;
        } else {
          result = '';
        }
      } else {
        throw new Error(`Unknown action: ${action}`);
      }
      
      sendResponse({ success: true, data: result });
      
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
    
    return true; // Keep message channel open for async response if needed, though sendResponse is sync here mostly
  }
});
