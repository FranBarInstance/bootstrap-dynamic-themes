/**
 * BTDT production loader — CSP compliant.
 * No inline styles, no eval, no nonce required.
 *
 * @file        btdt-loader.js
 * @description Production loader for BTDT. Handles color mode (light/dark) detection and application,
 *              and loads the active preset's stylesheet. Content Security Policy (CSP) compliant:
 *              no inline styles, eval, or nonce required.
 *
 * @usage
 *   <script src="path/to/btdt-loader.js"
 *           data-preset="default"
 *           data-mode="dark"
 *           data-minified="true"
 *           data-auto-init="true"
 *           data-dark-var="MY_DARK_VAR"
 *           data-dark-cookie="dark_mode"
 *           data-dark-system="true">
 *   </script>
 *
 * @attributes
 *   data-base-path    {string}   Base path for assets. Automatically detected from the script URL by default.
 *   data-preset       {string}   Name of the CSS preset to load (e.g. "default", "corporate").
 *                                Can be a short name or a complete path/URL to a .css file.
 *   data-mode         {string}   Initial color mode: "light" | "dark".
 *                                Takes priority over all other sources.
 *   data-minified     {boolean}  If "true", loads .min.css files. Default: false.
 *   data-auto-init    {boolean}  If "false", disables automatic initialization. Default: true.
 *   data-dark-var     {string}   Name of a window global variable whose value indicates if dark mode is active.
 *                                Recognized values: "1","true","yes","dark","on" for dark;
 *                                "0","false","no","light","off" for light.
 *   data-dark-cookie  {string}   Name of the cookie that stores dark mode preference.
 *                                Same recognized values as data-dark-var.
 *   data-dark-system  {boolean}  If "true", uses the operating system's prefers-color-scheme as mode preference.
 *
 * @priority    Color mode source resolution order:
 *              1. data-mode (explicit attribute)
 *              2. data-dark-var (window global variable)
 *              3. data-dark-cookie (browser cookie)
 *              4. data-dark-system (operating system preference)
 *              5. "light" (default value)
 *
 * @api         Exposes window.btdt with the following methods:
 *   btdt.load(name, options)  Loads a CSS preset by name or options.
 *   btdt.setMode(mode)        Sets the color mode ("light" | "dark").
 *   btdt.toggleMode()         Toggles between light and dark mode.
 *   btdt.getMode()            Returns the active color mode.
 *
 * @events
 *   btdt:modechange  Fired on <html> when color mode changes.
 *                    detail: { mode: "light" | "dark" }
 */
(function() {
    if (window.btdt && window.btdt._initialized) return;

    const VERSION = '1.0.0';

    const script = document.currentScript;
    if (!script) return;

    const detectedBase    = script.src.split('/').slice(0, -2).join('/') + '/';
    const basePath        = (script.getAttribute('data-base-path') || detectedBase).replace(/\/?$/, '/');
    const autoInit        = script.getAttribute('data-auto-init') !== 'false';
    const initialPreset   = script.getAttribute('data-preset') || null;
    const initialMode     = script.getAttribute('data-mode') || null;
    const defaultMinified = script.getAttribute('data-minified') === 'true';
    const darkVarName     = script.getAttribute('data-dark-var') || null;
    const darkCookieName  = script.getAttribute('data-dark-cookie') || null;
    const useSystemDark   = script.getAttribute('data-dark-system') === 'true';

    const DARK_VALUES  = new Set(['1', 'true', 'yes', 'dark', 'on']);
    const LIGHT_VALUES = new Set(['0', 'false', 'no', 'light', 'off']);

    function classifyValue(value) {
        if (value == null) return null;
        const n = String(value).trim().toLowerCase();
        if (DARK_VALUES.has(n))  return 'dark';
        if (LIGHT_VALUES.has(n)) return 'light';
        return null;
    }

    function getCookie(name) {
        const match = document.cookie.match(
            new RegExp('(?:^|; )' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)')
        );
        return match ? decodeURIComponent(match[1]) : null;
    }

    function resolveTargetMode() {
        if (initialMode === 'dark' || initialMode === 'light') return initialMode;
        if (darkVarName)    { const r = classifyValue(window[darkVarName]);       if (r) return r; }
        if (darkCookieName) { const r = classifyValue(getCookie(darkCookieName)); if (r) return r; }
        if (useSystemDark && window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return 'light';
    }

    const targetMode = resolveTargetMode();
    const html       = document.documentElement;

    html.setAttribute('data-bs-theme', targetMode);
    if (targetMode === 'dark') {
        html.setAttribute('data-mode', 'dark');
    } else {
        html.removeAttribute('data-mode');
    }

    function findLinkByFilename(filename) {
        const links = document.head.querySelectorAll('link[rel="stylesheet"]');
        for (let i = 0; i < links.length; i++) {
            const url = new URL(links[i].href);
            if (url.pathname.includes(filename)) return links[i];
        }
        return null;
    }

    function findPresetLink() {
        return document.getElementById('theme-preset') ||
               findLinkByFilename('themes/preset/') ||
               null;
    }

    function resolvePresetHref(name, options) {
        if (!name) return null;
        if (name.endsWith('.css') || name.includes('/')) return name;
        const min = (options && options.minified != null) ? options.minified : defaultMinified;
        return `${basePath}themes/preset/${name}${min ? '.min' : ''}.css`;
    }

    function ensurePresetLink() {
        const existing = findPresetLink();
        if (existing) { existing.id = 'theme-preset'; return existing; }
        const link = document.createElement('link');
        link.id  = 'theme-preset';
        link.rel = 'stylesheet';
        document.head.appendChild(link);
        return link;
    }

    function ensureModeLink() {
        let link = document.getElementById('theme-preset-dark');
        if (!link) {
            link = document.createElement('link');
            link.id   = 'theme-preset-dark';
            link.rel  = 'stylesheet';
            link.href = `${basePath}themes/modes/dark.min.css?v=${VERSION}`;
            document.head.appendChild(link);
        }

        link.media = targetMode === 'dark' ? 'all' : 'not all';
        return link;
    }

    function applyMode(mode) {
        const normalized = mode === 'dark' ? 'dark' : 'light';
        const modeLink   = ensureModeLink();

        html.setAttribute('data-bs-theme', normalized);
        if (normalized === 'dark') {
            html.setAttribute('data-mode', 'dark');
            modeLink.media = 'all';
        } else {
            html.removeAttribute('data-mode');
            modeLink.media = 'not all';
        }

        html.dispatchEvent(new CustomEvent('btdt:modechange', {
            bubbles: true,
            detail: { mode: normalized }
        }));

        return normalized;
    }

    window.btdt = {
        _initialized: true,
        _mode: targetMode,

        load: function(name, options) {
            const href = resolvePresetHref(name, options);
            if (!href) return this;
            const link = ensurePresetLink();
            if (link.href !== href) link.href = href;
            return this;
        },

        setMode: function(mode) {
            this._mode = applyMode(mode);
            return this;
        },

        toggleMode: function() {
            return this.setMode(this._mode === 'dark' ? 'light' : 'dark');
        },

        getMode: function() {
            return this._mode;
        }
    };

    if (autoInit) {
        const existingPreset = findPresetLink();

        if (existingPreset) {
            existingPreset.id = 'theme-preset';
        } else if (initialPreset) {
            window.btdt.load(initialPreset);
        }

        ensureModeLink();

        if (useSystemDark && !initialMode && !darkVarName && !darkCookieName && window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', function(e) {
                    window.btdt.setMode(e.matches ? 'dark' : 'light');
                });
        }
    }
})();
