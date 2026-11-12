(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function randomDelay(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
  }

  async function waitForElement(selector, maxAttempts = 3) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const el = document.querySelector(selector);
      if (el) return el;
      if (attempt < maxAttempts) {
        await sleep(attempt * 500);
      }
    }
    return null;
  }

  function setNativeValue(el, value) {
    if (el instanceof HTMLTextAreaElement) {
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      setter.call(el, value);
    } else if (el instanceof HTMLInputElement) {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(el, value);
    } else {
      el.value = value;
    }
  }

  function keyMeta(ch) {
    const upper = ch.toUpperCase();
    return {
      key: ch,
      code: upper === ' ' ? 'Space' : `Key${upper}`,
      bubbles: true,
      cancelable: true,
      composed: true
    };
  }

  async function typeHuman(selector, text) {
    const el = await waitForElement(selector);
    if (!el) throw new Error('typeHuman: selector not found after 3 attempts: ' + selector);

    el.focus();
    el.dispatchEvent(new FocusEvent('focus', { bubbles: true }));

    for (const ch of text) {
      await sleep(randomDelay(45, 150));

      el.dispatchEvent(new KeyboardEvent('keydown', keyMeta(ch)));
      el.dispatchEvent(new KeyboardEvent('keypress', keyMeta(ch)));

      const next = el.value !== undefined ? el.value + ch : el.textContent + ch;
      setNativeValue(el, next);

      el.dispatchEvent(new InputEvent('input', {
        data: ch,
        inputType: 'insertText',
        bubbles: true,
        cancelable: false,
        composed: true
      }));

      el.dispatchEvent(new KeyboardEvent('keyup', keyMeta(ch)));
    }

    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  async function clickHuman(selector) {
    const el = await waitForElement(selector);
    if (!el) throw new Error('clickHuman: selector not found after 3 attempts: ' + selector);

    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    await sleep(randomDelay(120, 400));

    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  }

  window.typeHuman = typeHuman;
  window.clickHuman = clickHuman;
})();
