(() => {
  'use strict';

  (function () {
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach((form) => {
      form.addEventListener('submit', (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  })();

  window.themeManager = new ThemeManager({ basePath: '../' });
  let bundledMinifiedCSS = '';

  const colorSwatches = window.BTDT_COLORS;
  const labels = {
    fonts: window.BTDT_FONTS,
    ...window.BTDT_UI
  };
  const presetMeta = window.BTDT_PRESETS;

  function buildPanel() {
    const presetsHtml = themeManager.getPresets()
      .filter(name => name !== 'default')
      .map(name => {
        const meta = presetMeta[name] || { title: name, color: null };
        const swatch = colorSwatches[meta.color] || {
          primary: '#ced4da', secondary: '#e9ecef', accent: '#adb5bd'
        };
        return `
          <div class="custom-option" data-value="${name}" onclick="applyPreset('${name}', event); closeAllCustomDropdowns();">
            <div class="mini-swatch">
              <div style="background:${swatch.primary}"></div>
              <div style="background:${swatch.secondary}"></div>
              <div style="background:${swatch.accent}"></div>
            </div>
            <span class="option-label">${meta.title}</span>
          </div>
        `;
      }).join('');
    document.getElementById('presetDropdown').innerHTML = presetsHtml;

    const colorsHtml = Object.entries(colorSwatches)
      .map(([name, colors]) => `
        <div class="custom-option" data-value="${name}" onclick="setTheme('colors','${name}', event); closeAllCustomDropdowns();">
          <div class="mini-swatch">
            <div style="background:${colors.primary}"></div>
            <div style="background:${colors.secondary}"></div>
            <div style="background:${colors.accent}"></div>
          </div>
          <span class="option-label text-capitalize">${name}</span>
        </div>
      `).join('');
    document.getElementById('colorsDropdown').innerHTML = colorsHtml;

    const fontsHtml = Object.entries(labels.fonts)
      .map(([value, label]) => `
        <div class="custom-option" data-value="${value}" onclick="setTheme('fonts','${value}', event); closeAllCustomDropdowns();">
          <span class="option-label" style="font-family: '${label}', sans-serif;">${label}</span>
        </div>
      `).join('');
    document.getElementById('fontsDropdown').innerHTML = fontsHtml;

    ['background', 'borders', 'rounding', 'shadows', 'spacing', 'gradients', 'accent', 'accentSize', 'accentColor', 'personality']
      .forEach(cat => {
        const dropdown = document.getElementById(`${cat}Dropdown`);
        if (!dropdown) return;
        const opts = Object.entries(labels[cat])
          .map(([value, label]) => `
            <div class="custom-option" data-value="${value}" onclick="setTheme('${cat}','${value}', event); closeAllCustomDropdowns();">
              <span class="option-label">${label}</span>
            </div>
          `).join('');
        dropdown.innerHTML = opts;
      });
  }

  function toggleDarkMode(isDark) {
    themeManager.setMode(isDark ? 'dark' : 'light');
    updatePanelState();
  }

  function setTheme(category, value, e) {
    if (e && typeof e.stopPropagation === 'function') e.stopPropagation();
    themeManager.set(category, value);
    updatePanelState();
  }

  async function applyPreset(name, e) {
    if (e && typeof e.stopPropagation === 'function') e.stopPropagation();
    await themeManager.applyPreset(name);
    updatePanelState();
  }

  function toggleCustomDropdown(type) {
    const container = document.getElementById(`${type}SelectContainer`);
    const dropdown = document.getElementById(`${type}Dropdown`);
    const isOpen = dropdown.classList.contains('show');

    closeAllCustomDropdowns();

    if (!isOpen) {
      container.classList.add('open');
      dropdown.classList.add('show');
    }
  }

  function closeAllCustomDropdowns() {
    document.querySelectorAll('.custom-select-container').forEach(el => el.classList.remove('open'));
    document.querySelectorAll('.custom-select-dropdown').forEach(el => el.classList.remove('show'));
  }

  function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie
      .split(';')
      .map((item) => item.trim())
      .find((item) => item.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : '';
  }

  function setCookie(name, value, days = 30) {
    const expires = new Date(Date.now() + (days * 24 * 60 * 60 * 1000)).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
  }

  function syncNavbarHeight() {
    const navbar = document.getElementById('main-navbar');
    document.documentElement.style.setProperty('--theme-navbar-h', `${navbar?.offsetHeight || 56}px`);
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllCustomDropdowns();
      closePanel();
    }
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.custom-select-container')) {
      closeAllCustomDropdowns();
    }
  });

  function togglePanel() {
    const toggle = document.getElementById('theme-drawer-toggle');
    if (toggle) toggle.click();
  }

  function closePanel() {
    const overlay = document.getElementById('theme-drawer-overlay');
    if (overlay && overlay.classList.contains('show')) {
      overlay.click();
    }
  }

  function copyConfig() {
    const css = themeManager.generatePresetCSS();
    navigator.clipboard.writeText(css);
    alert('CSS Preset copied to clipboard!');
  }

  async function generateBundledConfig() {
    const pre = document.getElementById('bundledMinifiedConfig');
    const copyBtn = document.getElementById('copyBundledBtn');

    if (!window.BTDTMinifier || !window.BTDTMinifier.isAvailable()) {
      bundledMinifiedCSS = '';
      if (pre) pre.textContent = 'Bundled export is not available when the editor is opened via file://. Serve the project over HTTP to enable it.';
      if (copyBtn) copyBtn.disabled = true;
      return;
    }

    if (pre) pre.textContent = 'Generating bundled CSS...';
    if (copyBtn) copyBtn.disabled = true;

    try {
      bundledMinifiedCSS = await window.BTDTMinifier.bundleAndMinifyPresetCSS(
        themeManager.generatePresetCSS()
      );
      if (pre) pre.textContent = bundledMinifiedCSS;
      if (copyBtn) copyBtn.disabled = false;
    } catch (error) {
      bundledMinifiedCSS = '';
      if (pre) pre.textContent = `Could not generate bundled CSS: ${error.message}`;
      if (copyBtn) copyBtn.disabled = true;
    }
  }

  function copyBundledConfig() {
    if (!bundledMinifiedCSS) return;
    navigator.clipboard.writeText(bundledMinifiedCSS);
    alert('Bundled minified CSS copied to clipboard!');
  }

  function updatePanelState() {
    const config = themeManager.getConfig();
    const isDark = themeManager.getMode() === 'dark';

    const navIcon = document.getElementById('navbarModeIcon');
    const navText = document.getElementById('navbarModeText');
    if (navIcon) navIcon.className = `mdi ${isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'}`;
    if (navText) navText.textContent = isDark ? 'Dark mode' : 'Light mode';

    ['preset', 'colors', 'fonts', 'background', 'borders', 'rounding', 'shadows', 'spacing', 'gradients', 'accent', 'accentSize', 'accentColor', 'personality']
      .forEach(type => {
        const dropdown = document.getElementById(`${type}Dropdown`);
        const triggerContent = document.getElementById(`${type}SelectContent`);
        if (!dropdown || !triggerContent) return;

        const value = type === 'preset' ? config._preset : config[type];

        dropdown.querySelectorAll('.custom-option').forEach(el => {
          el.classList.toggle('active', el.dataset.value === value);
        });

        if (value && value !== 'default') {
          if (type === 'preset') {
            const meta = presetMeta[value] || { title: value, color: null };
            const swatch = colorSwatches[meta.color] || { primary: '#ced4da', secondary: '#e9ecef', accent: '#adb5bd' };
            triggerContent.innerHTML = `
              <div class="mini-swatch">
                <div style="background:${swatch.primary}"></div>
                <div style="background:${swatch.secondary}"></div>
                <div style="background:${swatch.accent}"></div>
              </div>
              <span class="option-label">${meta.title}</span>
            `;
          } else if (type === 'colors') {
            const colors = colorSwatches[value] || { primary: '#ced4da', secondary: '#e9ecef', accent: '#adb5bd' };
            triggerContent.innerHTML = `
              <div class="mini-swatch">
                <div style="background:${colors.primary}"></div>
                <div style="background:${colors.secondary}"></div>
                <div style="background:${colors.accent}"></div>
              </div>
              <span class="option-label text-capitalize">${value}</span>
            `;
          } else if (type === 'fonts') {
            const label = labels.fonts[value] || value;
            triggerContent.innerHTML = `<span class="option-label" style="font-family: '${label}', sans-serif;">${label}</span>`;
          } else {
            const label = labels[type][value] || value;
            triggerContent.innerHTML = `<span class="option-label">${label}</span>`;
          }
        } else {
          const defaultLabels = {
            preset: 'Select a theme...',
            colors: 'Select colors...',
            fonts: 'Select fonts...',
            background: 'Select background...',
            borders: 'Select border...',
            rounding: 'Select rounding...',
            shadows: 'Select shadows...',
            spacing: 'Select spacing...',
            gradients: 'Gradients?',
            accent: 'Select accent...',
            accentSize: 'Select accent size...',
            accentColor: 'Select accent color...',
            personality: 'Select personality...'
          };
          triggerContent.innerHTML = `<span>${defaultLabels[type]}</span>`;
        }
      });

    const pre = document.getElementById('currentConfig');
    if (pre) pre.textContent = themeManager.generatePresetCSS();

    const bundledPre = document.getElementById('bundledMinifiedConfig');
    const generateBtn = document.getElementById('generateBundledBtn');
    const copyBtn = document.getElementById('copyBundledBtn');

    bundledMinifiedCSS = '';
    if (copyBtn) copyBtn.disabled = true;

    if (window.BTDTMinifier && !window.BTDTMinifier.isAvailable()) {
      if (bundledPre) bundledPre.textContent = 'Bundled export is not available when the editor is opened via file://. Serve the project over HTTP to enable it.';
      if (generateBtn) generateBtn.disabled = true;
    } else {
      if (bundledPre) bundledPre.textContent = 'Click "Generate bundled CSS" to build a single minified stylesheet.';
      if (generateBtn) generateBtn.disabled = false;
    }
  }

  function showToast(id) {
    const el = document.getElementById(id);
    if (el) new bootstrap.Toast(el, { delay: 3000 }).show();
  }

  function initThemeDrawer() {
    const STORAGE_KEY = 'theme-drawer-state';
    const PIN_KEY = 'theme-drawer-pin-full';
    const drawer = document.getElementById('theme-drawer');
    const toggle = document.getElementById('theme-drawer-toggle');
    const tabsToggle = document.getElementById('theme-drawer-tabs-toggle-btn');
    const pinToggle = document.getElementById('theme-drawer-pin');
    const overlay = document.getElementById('theme-drawer-overlay');
    const navbar = document.getElementById('main-navbar');
    const tabButtons = drawer ? drawer.querySelectorAll('#theme-drawer-tabs [data-bs-toggle="pill"]') : [];
    const states = ['theme-drawer-state-full', 'theme-drawer-state-icons', 'theme-drawer-state-hidden'];
    let refreshToken = 0;
    let hasHydrated = false;

    if (!drawer || !toggle || !tabsToggle || !overlay || !navbar) {
      return;
    }

    document.body.classList.add('theme-drawer-preload');
    overlay.classList.add('theme-drawer-preload');

    const isMobile = () => window.innerWidth < 768;

    function enableLayoutTransitions() {
      document.body.classList.remove('theme-drawer-preload');
    }

    function isPinned() {
      return !isMobile() && getCookie(PIN_KEY) === '1';
    }

    function syncPinToggle() {
      if (!pinToggle) return;
      pinToggle.checked = isPinned();
      pinToggle.disabled = isMobile();
    }

    function normalizeState(state) {
      if (isPinned()) return 'theme-drawer-state-full';
      if (isMobile()) return state === 'theme-drawer-state-full' ? state : 'theme-drawer-state-hidden';
      return states.includes(state) ? state : 'theme-drawer-state-hidden';
    }

    function recoverState(state) {
      if (isMobile()) return 'theme-drawer-state-hidden';
      const normalized = normalizeState(state);
      if (!isMobile() && normalized === 'theme-drawer-state-full') return 'theme-drawer-state-icons';
      return normalized;
    }

    function ensureActiveTab() {
      const activeButton = drawer.querySelector('#theme-drawer-tabs .active');
      const activePane = drawer.querySelector('#theme-drawer-tabs-content .tab-pane.active');
      if (activeButton && activePane) return;
      const firstButton = tabButtons[0];
      const firstPaneSelector = firstButton ? firstButton.getAttribute('data-bs-target') : '';
      const firstPane = firstPaneSelector ? drawer.querySelector(firstPaneSelector) : null;
      if (!firstButton) return;
      firstButton.classList.add('active');
      firstButton.setAttribute('aria-selected', 'true');
      if (firstPane) firstPane.classList.add('active', 'show');
    }

    function applyState(rawState) {
      const state = normalizeState(rawState);
      states.forEach((item) => drawer.classList.remove(item));
      drawer.classList.add(state);

      document.body.classList.remove('theme-drawer-layout-full', 'theme-drawer-layout-icons', 'theme-drawer-layout-hidden');
      if (state === 'theme-drawer-state-full') {
        document.body.classList.add('theme-drawer-layout-full');
      } else if (state === 'theme-drawer-state-icons') {
        document.body.classList.add('theme-drawer-layout-icons');
      } else {
        document.body.classList.add('theme-drawer-layout-hidden');
      }

      const expanded = state !== 'theme-drawer-state-hidden';
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      tabsToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      overlay.classList.toggle('show', isMobile() && expanded);
      setCookie(STORAGE_KEY, isMobile() ? 'theme-drawer-state-hidden' : state);

      if (!hasHydrated) {
        hasHydrated = true;
        requestAnimationFrame(() => {
          drawer.classList.remove('theme-drawer-preload');
          overlay.classList.remove('theme-drawer-preload');
        });
      }
    }

    function nextState() {
      if (isMobile()) {
        return drawer.classList.contains('theme-drawer-state-full') ? 'theme-drawer-state-hidden' : 'theme-drawer-state-full';
      }
      if (drawer.classList.contains('theme-drawer-state-full')) return 'theme-drawer-state-icons';
      if (drawer.classList.contains('theme-drawer-state-icons')) return 'theme-drawer-state-hidden';
      return 'theme-drawer-state-full';
    }

    function getCurrentState() {
      return states.find((state) => drawer.classList.contains(state)) || 'theme-drawer-state-hidden';
    }

    function refreshLayout(useStoredState = false) {
      syncNavbarHeight();
      syncPinToggle();
      ensureActiveTab();
      const state = useStoredState
        ? recoverState(getCookie(STORAGE_KEY) || 'theme-drawer-state-hidden')
        : getCurrentState();
      applyState(state);
    }

    function scheduleRefresh(useStoredState = false) {
      refreshToken += 1;
      const currentToken = refreshToken;
      refreshLayout(useStoredState);
      requestAnimationFrame(() => {
        if (currentToken !== refreshToken) return;
        refreshLayout(useStoredState);
        requestAnimationFrame(() => {
          if (currentToken !== refreshToken) return;
          refreshLayout(useStoredState);
        });
      });
    }

    toggle.addEventListener('click', () => {
      enableLayoutTransitions();
      ensureActiveTab();
      applyState(nextState());
    });

    tabsToggle.addEventListener('click', () => {
      enableLayoutTransitions();
      ensureActiveTab();
      applyState(nextState());
    });

    if (pinToggle) {
      pinToggle.addEventListener('change', () => {
        enableLayoutTransitions();
        setCookie(PIN_KEY, pinToggle.checked ? '1' : '0');
        syncPinToggle();
        applyState(pinToggle.checked ? 'theme-drawer-state-full' : 'theme-drawer-state-icons');
      });
    }

    overlay.addEventListener('click', () => {
      enableLayoutTransitions();
      applyState('theme-drawer-state-hidden');
    });

    tabButtons.forEach((button) => {
      button.addEventListener('click', () => {
        enableLayoutTransitions();
        if (!isMobile() && drawer.classList.contains('theme-drawer-state-icons')) {
          applyState('theme-drawer-state-full');
        }
      });
    });

    window.addEventListener('resize', () => {
      scheduleRefresh(false);
    });

    window.addEventListener('load', () => scheduleRefresh(true));
    window.addEventListener('pageshow', () => scheduleRefresh(true));
    window.addEventListener('pagehide', () => {
      if (isMobile()) setCookie(STORAGE_KEY, 'theme-drawer-state-hidden');
    });

    if (typeof ResizeObserver !== 'undefined') {
      const navbarObserver = new ResizeObserver(() => {
        scheduleRefresh(false);
      });
      navbarObserver.observe(navbar);
    }

    scheduleRefresh(true);
  }

  document.addEventListener('DOMContentLoaded', () => {
    syncNavbarHeight();

    document.querySelectorAll('[data-bs-toggle="tooltip"]')
      .forEach(el => new bootstrap.Tooltip(el));
    document.querySelectorAll('[data-bs-toggle="popover"]')
      .forEach(el => new bootstrap.Popover(el));

    window.addEventListener('themechange', () => {
      updatePanelState();
    });

    if (typeof themeManager !== 'undefined') {
      buildPanel();
      updatePanelState();
    }

    initThemeDrawer();
  });

  window.toggleDarkMode = toggleDarkMode;
  window.setTheme = setTheme;
  window.applyPreset = applyPreset;
  window.toggleCustomDropdown = toggleCustomDropdown;
  window.closeAllCustomDropdowns = closeAllCustomDropdowns;
  window.togglePanel = togglePanel;
  window.closePanel = closePanel;
  window.copyConfig = copyConfig;
  window.generateBundledConfig = generateBundledConfig;
  window.copyBundledConfig = copyBundledConfig;
  window.showToast = showToast;
})();
