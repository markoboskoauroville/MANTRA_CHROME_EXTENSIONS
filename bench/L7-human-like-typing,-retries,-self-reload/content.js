const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomBetween = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function waitForElement(selector, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const el = document.querySelector(selector);
    if (el) return el;
    // Growing delay: 500ms, 1000ms, 1500ms
    await wait(500 * (i + 1));
  }
  // Final check before throwing
  const el = document.querySelector(selector);
  if (el) return el;
  throw new Error(`Element with selector "${selector}" not found after ${maxRetries} retries`);
}

async function typeCharacter(el, char) {
  const delay = randomBetween(45, 150);
  await wait(delay);

  el.dispatchEvent(new KeyboardEvent('keydown', { key: char, bubbles: true }));
  el.value += char;
  el.dispatchEvent(new InputEvent('input', { data: char, bubbles: true }));
  el.dispatchEvent(new KeyboardEvent('keyup', { key: char, bubbles: true }));
}

async function typeHuman(selector, text) {
  const el = await waitForElement(selector);
  el.focus();
  
  for (const char of text) {
    await typeCharacter(el, char);
  }
}

async function clickHuman(selector) {
  const el = await waitForElement(selector);
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  
  const waitTime = randomBetween(120, 400);
  await wait(waitTime);
  
  el.click();
}

// Expose to window for potential direct use or debugging, though messaging is primary
window.mantraHands = { typeHuman, clickHuman };

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'MANTRA_HANDS') {
    const { action, selector, text } = message;
    
    if (action === 'type') {
      typeHuman(selector, text).then(() => {
        sendResponse({ success: true });
      }).catch(err => {
        sendResponse({ success: false, error: err.message });
      });
      return true; // Async response
    } else if (action === 'click') {
      clickHuman(selector).then(() => {
        sendResponse({ success: true });
      }).catch(err => {
        sendResponse({ success: false, error: err.message });
      });
      return true; // Async response
    }
  }
});
