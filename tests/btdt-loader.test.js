const test = require('node:test');
const assert = require('node:assert/strict');

const { createTestEnv, runBtdtLoader, FakeCustomEvent } = require('./dom-test-helpers');

test('btdt loader loads the minified preset by default and creates the dark mode link', () => {
  const env = createTestEnv();
  const btdt = runBtdtLoader(env, {
    'data-preset': 'studio',
  });

  const presetLink = env.document.getElementById('theme-preset');
  const darkLink = env.document.getElementById('theme-preset-dark');

  assert.equal(btdt.getMode(), 'light');
  assert.equal(presetLink.href, 'https://example.test/btdt/themes/preset/studio.min.css');
  assert.equal(darkLink.href, 'https://example.test/btdt/themes/modes/dark.min.css?v=2.0.6');
  assert.equal(darkLink.media, 'not all');
});

test('btdt loader respects data-dark-value priority and updates DOM on mode changes', () => {
  const env = createTestEnv();
  const enabled = env.document.createElement('div');
  enabled.classList.add('dark-mode-enabled');
  const disabled = env.document.createElement('div');
  disabled.classList.add('dark-mode-disabled');
  env.document.body.appendChild(enabled);
  env.document.body.appendChild(disabled);

  const btdt = runBtdtLoader(env, {
    'data-dark-value': 'dark',
    'data-dark-cookie': 'dark_mode',
  });

  env.document.dispatchEvent(new FakeCustomEvent('DOMContentLoaded'));

  assert.equal(btdt.getMode(), 'dark');
  assert.equal(env.document.documentElement.getAttribute('data-bs-theme'), 'dark');
  assert.equal(env.document.documentElement.getAttribute('data-mode'), 'dark');
  assert.equal(enabled.classList.contains('display-none'), false);
  assert.equal(disabled.classList.contains('display-none'), true);
  assert.equal(env.document.cookie, '');

  btdt.setMode('light');

  assert.equal(env.document.documentElement.getAttribute('data-bs-theme'), 'light');
  assert.equal(env.document.documentElement.getAttribute('data-mode'), null);
  assert.equal(env.document.getElementById('theme-preset-dark').media, 'not all');
  assert.equal(enabled.classList.contains('display-none'), true);
  assert.equal(disabled.classList.contains('display-none'), false);
});

test('btdt loader listens to delegated toggles and uses system dark mode when enabled', () => {
  const env = createTestEnv({ prefersDark: true });
  const toggle = env.document.createElement('button');
  toggle.classList.add('theme-light-dark-toggle');
  env.document.body.appendChild(toggle);

  const modeEvents = [];
  env.document.documentElement.addEventListener('btdt:modechange', (event) => {
    modeEvents.push(event.detail.mode);
  });

  const btdt = runBtdtLoader(env, {
    'data-dark-system': 'true',
  });

  env.document.dispatchEvent(new FakeCustomEvent('DOMContentLoaded'));
  env.document.dispatchEvent({
    type: 'click',
    target: toggle,
    preventDefault() {
      this.defaultPrevented = true;
    },
  });

  assert.equal(btdt.getMode(), 'light');
  assert.deepEqual(modeEvents, ['light']);

  env.window.__setSystemDark(true);
  assert.equal(btdt.getMode(), 'dark');
});
