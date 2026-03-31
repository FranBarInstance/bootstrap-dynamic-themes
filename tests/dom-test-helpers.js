const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class FakeClassList {
  constructor(element) {
    this.element = element;
    this._set = new Set();
  }

  add(...names) {
    names.forEach((name) => this._set.add(name));
  }

  remove(...names) {
    names.forEach((name) => this._set.delete(name));
  }

  contains(name) {
    return this._set.has(name);
  }

  toggle(name, force) {
    if (force === true) {
      this._set.add(name);
      return true;
    }

    if (force === false) {
      this._set.delete(name);
      return false;
    }

    if (this._set.has(name)) {
      this._set.delete(name);
      return false;
    }

    this._set.add(name);
    return true;
  }

  toString() {
    return Array.from(this._set).join(' ');
  }
}

class FakeElement {
  constructor(tagName, ownerDocument) {
    this.tagName = String(tagName || '').toUpperCase();
    this.ownerDocument = ownerDocument;
    this.children = [];
    this.parentNode = null;
    this.attributes = new Map();
    this.classList = new FakeClassList(this);
    this.listeners = new Map();
    this.rel = '';
    this.disabled = false;
    this.media = '';
    this._id = '';
    this._href = '';
  }

  set id(value) {
    this._id = value;
    this.setAttribute('id', value);
  }

  get id() {
    return this._id;
  }

  set href(value) {
    this._href = new URL(value, this.ownerDocument.baseURI).href;
  }

  get href() {
    return this._href;
  }

  appendChild(child) {
    if (child.parentNode) {
      child.parentNode.removeChild(child);
    }
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  removeChild(child) {
    const index = this.children.indexOf(child);
    if (index >= 0) {
      this.children.splice(index, 1);
      child.parentNode = null;
    }
    return child;
  }

  remove() {
    if (this.parentNode) {
      this.parentNode.removeChild(this);
    }
  }

  setAttribute(name, value) {
    const normalized = String(name);
    const stringValue = String(value);
    this.attributes.set(normalized, stringValue);
    if (normalized === 'id') {
      this._id = stringValue;
    }
    if (normalized === 'class') {
      this.classList = new FakeClassList(this);
      stringValue.split(/\s+/).filter(Boolean).forEach((cls) => this.classList.add(cls));
    }
  }

  getAttribute(name) {
    return this.attributes.has(name) ? this.attributes.get(name) : null;
  }

  removeAttribute(name) {
    this.attributes.delete(name);
    if (name === 'id') this._id = '';
  }

  addEventListener(type, listener) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type).push(listener);
  }

  dispatchEvent(event) {
    event.target = event.target || this;
    const listeners = this.listeners.get(event.type) || [];
    listeners.forEach((listener) => listener.call(this, event));
    return true;
  }

  closest(selector) {
    if (!selector.startsWith('.')) return null;
    const className = selector.slice(1);
    return this.classList.contains(className) ? this : null;
  }

  querySelectorAll(selector) {
    const results = [];
    const visit = (node) => {
      node.children.forEach((child) => {
        if (matchesSelector(child, selector)) {
          results.push(child);
        }
        visit(child);
      });
    };
    visit(this);
    return results;
  }
}

class FakeDocument {
  constructor(baseURI = 'https://example.test/app/') {
    this.baseURI = baseURI;
    this.listeners = new Map();
    this.cookieValue = '';
    this.documentElement = new FakeElement('html', this);
    this.head = new FakeElement('head', this);
    this.body = new FakeElement('body', this);
    this.documentElement.appendChild(this.head);
    this.documentElement.appendChild(this.body);
    this.currentScript = null;
  }

  createElement(tagName) {
    return new FakeElement(tagName, this);
  }

  getElementById(id) {
    return this._allElements().find((element) => element.id === id) || null;
  }

  querySelectorAll(selector) {
    return this.documentElement.querySelectorAll(selector);
  }

  addEventListener(type, listener) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type).push(listener);
  }

  dispatchEvent(event) {
    event.target = event.target || this;
    const listeners = this.listeners.get(event.type) || [];
    listeners.forEach((listener) => listener.call(this, event));
    return true;
  }

  _allElements() {
    const elements = [];
    const visit = (node) => {
      elements.push(node);
      node.children.forEach(visit);
    };
    visit(this.documentElement);
    return elements;
  }

  get cookie() {
    return this.cookieValue;
  }

  set cookie(value) {
    this.cookieValue = value;
  }
}

class FakeStorage {
  constructor() {
    this.map = new Map();
  }

  getItem(key) {
    return this.map.has(key) ? this.map.get(key) : null;
  }

  setItem(key, value) {
    this.map.set(key, String(value));
  }

  removeItem(key) {
    this.map.delete(key);
  }
}

class FakeCustomEvent {
  constructor(type, init = {}) {
    this.type = type;
    this.detail = init.detail;
    this.bubbles = Boolean(init.bubbles);
    this.defaultPrevented = false;
    this.target = null;
  }
}

function matchesSelector(element, selector) {
  if (selector === '.dark-mode-enabled') {
    return element.classList.contains('dark-mode-enabled');
  }

  if (selector === '.dark-mode-disabled') {
    return element.classList.contains('dark-mode-disabled');
  }

  if (selector === 'link[rel="stylesheet"]') {
    return element.tagName === 'LINK' && element.rel === 'stylesheet';
  }

  return false;
}

function createWindow(document, options = {}) {
  const listeners = new Map();
  const matchMediaState = {
    matches: Boolean(options.prefersDark),
    listeners: [],
  };

  return {
    document,
    location: { href: document.baseURI },
    BTDT_COLORS: options.colors,
    BTDT_FONTS: options.fonts,
    BTDT_UI: options.ui,
    BTDT_PRESETS: options.presets,
    CustomEvent: FakeCustomEvent,
    addEventListener(type, listener) {
      if (!listeners.has(type)) {
        listeners.set(type, []);
      }
      listeners.get(type).push(listener);
    },
    dispatchEvent(event) {
      const callbacks = listeners.get(event.type) || [];
      callbacks.forEach((listener) => listener.call(this, event));
      return true;
    },
    matchMedia() {
      return {
        matches: matchMediaState.matches,
        addEventListener(type, listener) {
          if (type === 'change') {
            matchMediaState.listeners.push(listener);
          }
        },
      };
    },
    __setSystemDark(matches) {
      matchMediaState.matches = matches;
      matchMediaState.listeners.forEach((listener) => listener({ matches }));
    },
  };
}

function createTestEnv(options = {}) {
  const document = new FakeDocument(options.baseURI);
  const window = createWindow(document, options);
  const localStorage = new FakeStorage();
  const computedStyleValues = { ...(options.computedStyleValues || {}) };

  return {
    window,
    document,
    localStorage,
    computedStyleValues,
    CustomEvent: FakeCustomEvent,
    getComputedStyle() {
      return {
        getPropertyValue(name) {
          return computedStyleValues[name] || '';
        },
      };
    },
  };
}

function runBtdtLoader(env, scriptAttributes = {}) {
  const scriptPath = path.join(process.cwd(), 'btdt/js/btdt.js');
  const code = fs.readFileSync(scriptPath, 'utf8');
  const script = env.document.createElement('script');
  script.src = scriptAttributes.src || 'https://example.test/btdt/js/btdt.js';

  Object.entries(scriptAttributes).forEach(([name, value]) => {
    if (name !== 'src') {
      script.setAttribute(name, value);
    }
  });

  env.document.currentScript = script;

  const sandbox = {
    window: env.window,
    document: env.document,
    localStorage: env.localStorage,
    CustomEvent: env.CustomEvent,
    URL,
    console,
    setTimeout(fn) {
      fn();
      return 1;
    },
    clearTimeout() {},
  };

  env.window.window = env.window;
  env.window.document = env.document;
  env.window.localStorage = env.localStorage;
  env.window.CustomEvent = env.CustomEvent;
  env.window.console = console;
  env.window.setTimeout = sandbox.setTimeout;
  env.window.clearTimeout = sandbox.clearTimeout;
  env.window.URL = URL;

  vm.runInNewContext(code, sandbox, { filename: scriptPath });
  return env.window.btdt;
}

module.exports = {
  createTestEnv,
  runBtdtLoader,
  FakeCustomEvent,
};
