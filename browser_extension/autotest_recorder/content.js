(() => {
  const AUTOTEST_FLAG = '__autotest_recorder_installed__';
  if (window[AUTOTEST_FLAG]) return;
  window[AUTOTEST_FLAG] = true;

  let config = { enabled: false, caseId: '', apiBase: 'http://127.0.0.1:8000', captureScroll: false, showBadge: true };
  let lastInputTimer = null;
  let lastScrollTimer = null;
  let lastUrl = location.href;

  chrome.storage.local.get(config, (stored) => {
    config = { ...config, ...stored };
    updateBadge();
    if (config.enabled && config.caseId) {
      sendEvent('navigation', document.documentElement, { action_type: 'open', url: location.href, title: document.title });
    }
  });

  chrome.storage.onChanged.addListener((changes) => {
    Object.keys(changes).forEach((key) => { config[key] = changes[key].newValue; });
    updateBadge();
  });

  function isEnabled() {
    return config.enabled && config.caseId && config.apiBase;
  }

  function cleanText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim().slice(0, 200);
  }

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function getSelector(element) {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) return { selector_type: 'css', selector_value: null, alternative_selector: null };
    const el = element;
    const id = el.getAttribute('id');
    if (id) return { selector_type: 'css', selector_value: `#${cssEscape(id)}`, alternative_selector: buildCssPath(el) };
    const testId = el.getAttribute('data-testid') || el.getAttribute('data-test') || el.getAttribute('data-qa');
    if (testId) return { selector_type: 'css', selector_value: `[data-testid="${testId}"]`, alternative_selector: buildCssPath(el) };
    const name = el.getAttribute('name');
    if (name) return { selector_type: 'css', selector_value: `[name="${name}"]`, alternative_selector: buildCssPath(el) };
    const aria = el.getAttribute('aria-label');
    if (aria) return { selector_type: 'css', selector_value: `[aria-label="${aria}"]`, alternative_selector: buildCssPath(el) };
    return { selector_type: 'css', selector_value: buildCssPath(el), alternative_selector: buildXPath(el) };
  }

  function buildCssPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE && node !== document.body && parts.length < 6) {
      let part = node.tagName.toLowerCase();
      const classes = Array.from(node.classList || []).filter(Boolean).slice(0, 2);
      if (classes.length) part += '.' + classes.map(cssEscape).join('.');
      const parent = node.parentElement;
      if (parent) {
        const sameTag = Array.from(parent.children).filter(child => child.tagName === node.tagName);
        if (sameTag.length > 1) part += `:nth-of-type(${sameTag.indexOf(node) + 1})`;
      }
      parts.unshift(part);
      node = node.parentElement;
    }
    return parts.length ? parts.join(' > ') : null;
  }

  function buildXPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
      let index = 1;
      let sibling = node.previousElementSibling;
      while (sibling) {
        if (sibling.tagName === node.tagName) index += 1;
        sibling = sibling.previousElementSibling;
      }
      parts.unshift(`${node.tagName.toLowerCase()}[${index}]`);
      node = node.parentElement;
    }
    return '/' + parts.join('/');
  }

  function elementValue(element) {
    if (!element) return null;
    const tag = element.tagName ? element.tagName.toLowerCase() : '';
    const type = (element.getAttribute('type') || '').toLowerCase();
    if (type === 'password') return '__AUTOTEST_MASKED_PASSWORD__';
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return element.value || '';
    return cleanText(element.innerText || element.textContent || element.value || '');
  }


  function updateBadge() {
    const existing = document.getElementById('autotest-recorder-badge');
    if (!isEnabled() || !config.showBadge) {
      if (existing) existing.remove();
      return;
    }
    let badge = existing;
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'autotest-recorder-badge';
      badge.style.cssText = 'position:fixed;right:14px;bottom:14px;z-index:2147483647;background:#2463eb;color:#fff;font:600 12px Arial;padding:9px 12px;border-radius:999px;box-shadow:0 8px 28px rgba(0,0,0,.25);pointer-events:none;';
      document.documentElement.appendChild(badge);
    }
    badge.textContent = `AutoTest grabando #${config.caseId}`;
  }

  function sendEvent(eventType, element, extra = {}) {
    if (!isEnabled()) return;
    const selector = getSelector(element);
    const payload = {
      event_type: eventType,
      selector_type: selector.selector_type,
      selector_value: selector.selector_value,
      alternative_selector: selector.alternative_selector,
      input_value: extra.input_value ?? elementValue(element),
      url: extra.url || location.href,
      title: extra.title || document.title,
      tag: element && element.tagName ? element.tagName.toLowerCase() : null,
      text: element ? cleanText(element.innerText || element.textContent || '') : null,
      timestamp: new Date().toISOString(),
      ...extra
    };

    fetch(`${config.apiBase.replace(/\/$/, '')}/api/recorder/public/cases/${config.caseId}/browser-events`, {
      method: 'POST',
      mode: 'cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
  }

  document.addEventListener('click', (event) => {
    if (!isEnabled()) return;
    sendEvent('click', event.target, { action_type: 'click' });
  }, true);

  document.addEventListener('dblclick', (event) => {
    if (!isEnabled()) return;
    sendEvent('dblclick', event.target, { action_type: 'double_click' });
  }, true);

  document.addEventListener('contextmenu', (event) => {
    if (!isEnabled()) return;
    sendEvent('contextmenu', event.target, { action_type: 'right_click' });
  }, true);

  document.addEventListener('input', (event) => {
    if (!isEnabled()) return;
    clearTimeout(lastInputTimer);
    const target = event.target;
    lastInputTimer = setTimeout(() => {
      sendEvent('input', target, { action_type: 'type', input_value: elementValue(target) });
    }, 450);
  }, true);

  document.addEventListener('change', (event) => {
    if (!isEnabled()) return;
    sendEvent('change', event.target, { action_type: 'type', input_value: elementValue(event.target) });
  }, true);

  window.addEventListener('scroll', () => {
    if (!isEnabled() || !config.captureScroll) return;
    clearTimeout(lastScrollTimer);
    lastScrollTimer = setTimeout(() => {
      sendEvent('scroll', document.documentElement, { action_type: 'scroll', input_value: String(window.scrollY) });
    }, 800);
  }, true);

  setInterval(() => {
    if (!isEnabled()) return;
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      sendEvent('url_change', document.documentElement, { action_type: 'open', url: location.href, title: document.title });
    }
  }, 700);
})();
