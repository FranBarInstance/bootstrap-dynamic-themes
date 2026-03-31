const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const { createTestEnv } = require('./dom-test-helpers');

const themeManagerPath = path.join(process.cwd(), 'btdt/js/theme-manager.js');

function loadThemeManager(env) {
  delete require.cache[themeManagerPath];

  global.window = env.window;
  global.document = env.document;
  global.localStorage = env.localStorage;
  global.CustomEvent = env.CustomEvent;
  global.getComputedStyle = env.getComputedStyle;

  const ThemeManager = require(themeManagerPath);
  return ThemeManager;
}

function cleanupGlobals() {
  delete global.window;
  delete global.document;
  delete global.localStorage;
  delete global.CustomEvent;
  delete global.getComputedStyle;
}

test('ThemeManager loads category links and preserves cascade order', () => {
  const env = createTestEnv({
    colors: { ocean: {} },
    fonts: { inter: {} },
    ui: {
      background: { none: {} },
      borders: { default: {} },
      rounding: { default: {} },
      shadows: { default: {} },
      spacing: { default: {} },
      gradients: { default: {} },
      accent: { left: {} },
      accentSize: { 3: {} },
      accentColor: { secondary: {} },
      personality: { sketch: {} },
    },
  });

  const ThemeManager = loadThemeManager(env);
  const manager = new ThemeManager({ basePath: 'btdt' });

  manager.set('accentColor', 'secondary');
  manager.set('fonts', 'inter');
  manager.set('colors', 'ocean');

  const styleLinks = env.document.head.children
    .filter((element) => element.tagName === 'LINK' && element.id.startsWith('theme-'))
    .map((element) => element.id);

  assert.deepEqual(styleLinks, ['theme-colors', 'theme-fonts', 'theme-accentColor', 'theme-mode']);
  assert.equal(env.document.getElementById('theme-colors').href, 'https://example.test/app/btdt/themes/colors/ocean.css?v=' + manager._cacheBust);
  assert.equal(env.document.getElementById('theme-fonts').href, 'https://example.test/app/btdt/themes/fonts/inter.css?v=' + manager._cacheBust);

  cleanupGlobals();
});

test('ThemeManager setMode syncs attributes, mode link, and localStorage', () => {
  const env = createTestEnv();
  const ThemeManager = loadThemeManager(env);
  const manager = new ThemeManager();

  let eventDetail = null;
  env.window.addEventListener('themechange', (event) => {
    eventDetail = event.detail;
  });

  manager.setMode('dark');

  assert.equal(manager.getMode(), 'dark');
  assert.equal(env.document.documentElement.getAttribute('data-mode'), 'dark');
  assert.equal(env.document.documentElement.getAttribute('data-bs-theme'), 'dark');
  assert.equal(env.document.getElementById('theme-mode').disabled, false);
  assert.equal(env.localStorage.getItem('bs-theme-mode'), 'dark');
  assert.equal(eventDetail.category, 'mode');
  assert.equal(eventDetail.value, 'dark');

  manager.setMode('light');

  assert.equal(env.document.documentElement.getAttribute('data-mode'), null);
  assert.equal(env.document.documentElement.getAttribute('data-bs-theme'), 'light');
  assert.equal(env.document.getElementById('theme-mode').disabled, true);

  cleanupGlobals();
});

test('ThemeManager generatePresetCSS exports imports in order and keeps metadata', () => {
  const env = createTestEnv();
  const ThemeManager = loadThemeManager(env);
  const manager = new ThemeManager();

  manager.activeTheme = {
    colors: 'ocean',
    fonts: 'inter',
    background: 'primary-medium',
    borders: null,
    rounding: 'extra',
    shadows: null,
    spacing: 'large',
    gradients: 'off',
    accent: 'left',
    accentSize: '3',
    accentColor: 'secondary',
    personality: 'sketch',
    _preset: null,
  };

  const css = manager.generatePresetCSS();

  assert.ok(css.indexOf('@import "../fonts/inter.css";') < css.indexOf('@import "../colors/ocean.css";'));
  assert.ok(css.includes('@import "../styles/accent-secondary.css";'));
  assert.ok(css.includes('--preset-personality: "sketch";'));
  assert.ok(!css.includes('--preset-_preset'));

  cleanupGlobals();
});
