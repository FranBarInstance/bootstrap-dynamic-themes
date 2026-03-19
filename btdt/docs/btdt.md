# btdt-loader.js

Production loader for BTDT. Handles color mode (light/dark) detection and application, loads the active preset's stylesheet, synchronizes UI elements based on the active mode, persists the mode preference to a cookie, and automatically binds toggle button listeners.

**CSP compliant** — no inline styles, no `eval`, no nonce required.

---

## Installation

Include the script in the `<head>` of your HTML, before any preset stylesheets:

```html
<script src="path/to/btdt/js/btdt-loader.js"
        data-preset="theme-name"
        data-dark-cookie="dark_mode"
        data-cookie-expire="30"
        data-dark-system="true">
</script>
```

The script auto-detects its own base path from the `src` URL, so no additional configuration is needed in most setups.

---

## Attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `data-base-path` | string | auto | Base path for assets. Detected automatically from the script URL. |
| `data-preset` | string | — | CSS preset to load. Short name (e.g. `"theme-name"`) or a full path/URL ending in `.css`. |
| `data-minified` | boolean | `false` | If `"true"`, loads `.min.css` files. |
| `data-auto-init` | boolean | `true` | If `"false"`, disables automatic initialization. |
| `data-dark-value` | string | — | Literal value indicating the initial dark mode state. Takes priority over all other sources. |
| `data-dark-cookie` | string | — | Name of the cookie that stores the mode preference. If not set, no cookie is read or written at any point. |
| `data-cookie-expire` | number | `0` | Cookie expiry in days (e.g. `"30"` = 30 days). `"0"` creates a session cookie that expires when the browser is closed. Ignored if `data-dark-cookie` is not set. |
| `data-dark-system` | boolean | `false` | If `"true"`, uses the OS `prefers-color-scheme` as the mode preference. |

### Recognized values for `data-dark-value` and `data-dark-cookie`

Values are case-insensitive.

| Mode | Accepted values |
|---|---|
| Dark | `"1"` `"true"` `"yes"` `"dark"` `"on"` |
| Light | `"0"` `"false"` `"no"` `"light"` `"off"` |

---

## Mode resolution priority

When the script initializes, the active color mode is resolved in this order. The first source that returns a recognized value wins:

1. `data-dark-value` — literal attribute value
2. `data-dark-cookie` — browser cookie
3. `data-dark-system` — OS `prefers-color-scheme`
4. `"light"` — built-in default

---

## JavaScript API

The script exposes a global `window.btdt` object. All methods are chainable.

### `btdt.load(name, options)`

Loads a CSS preset stylesheet. Updates the `<link id="theme-preset">` element in place, or creates one if it does not exist.

| Parameter | Type | Description |
|---|---|---|
| `name` | string | Preset name (e.g. `"corporate"`) or a full path/URL ending in `.css`. |
| `options.minified` | boolean | Load the `.min.css` variant. Defaults to `data-minified`. |

```js
btdt.load('corporate');
btdt.load('corporate', { minified: true });
btdt.load('/assets/themes/custom.css');
```

### `btdt.setMode(mode)`

Sets the active color mode. Updates the DOM, writes the cookie (if configured), and fires the `btdt:modechange` event.

```js
btdt.setMode('dark');
btdt.setMode('light');
```

### `btdt.toggleMode()`

Toggles between `"dark"` and `"light"` mode.

```js
btdt.toggleMode();
```

### `btdt.getMode()`

Returns the currently active color mode.

```js
const mode = btdt.getMode(); // "dark" | "light"
```

---

## Events

### `btdt:modechange`

Fired on `<html>` whenever the color mode changes. Bubbles.

```js
document.documentElement.addEventListener('btdt:modechange', (e) => {
    console.log(e.detail.mode); // "dark" | "light"
});
```

---

## DOM conventions

The script automatically manages the following CSS classes and elements — no extra JavaScript required.

### Toggle buttons — `.theme-light-dark-toggle`

Any element with this class triggers a mode toggle on click. Listeners are registered via event delegation on `DOMContentLoaded`, so dynamically inserted elements are also supported.

```html
<button class="theme-light-dark-toggle">Toggle dark mode</button>
<a href="#" class="theme-light-dark-toggle">Switch theme</a>
```

### Mode-specific visibility — `.dark-mode-enabled` / `.dark-mode-disabled`

Elements with `.dark-mode-enabled` are shown only in dark mode. Elements with `.dark-mode-disabled` are shown only in light mode. The script toggles the `display-none` class automatically on every mode change, including on initial load.

```html
<!-- Visible only in dark mode -->
<img class="dark-mode-enabled" src="logo-dark.svg" alt="Logo">

<!-- Visible only in light mode -->
<img class="dark-mode-disabled" src="logo-light.svg" alt="Logo">
```

> Your stylesheet must define `.display-none { display: none !important; }`.

---

## HTML attributes set on `<html>`

The script writes the following attributes on the `<html>` element to allow CSS targeting:

| Attribute | Dark mode | Light mode |
|---|---|---|
| `data-bs-theme` | `"dark"` | `"light"` |
| `data-mode` | `"dark"` | _(removed)_ |

```css
/* Target dark mode in CSS */
[data-bs-theme="dark"] .my-element { color: white; }
[data-mode="dark"] .my-element { color: white; }
```

---

## Usage examples

### Minimal — light mode only, no cookie

```html
<script src="btdt/js/btdt-loader.js"
        data-preset="theme-name">
</script>
```

### Follow the OS preference

```html
<script src="btdt/js/btdt-loader.js"
        data-preset="theme-name"
        data-dark-system="true">
</script>
```

### Persist preference in a session cookie

The cookie expires when the browser is closed. The OS preference is used as fallback if no cookie exists yet.

```html
<script src="btdt/js/btdt-loader.js"
        data-preset="theme-name"
        data-dark-cookie="dark_mode"
        data-dark-system="true">
</script>
```

### Persist preference in a 30-day cookie

```html
<script src="btdt/js/btdt-loader.js"
        data-preset="theme-name"
        data-dark-cookie="dark_mode"
        data-cookie-expire="30"
        data-dark-system="true">
</script>
```

### Server-side preference injected at render time

The server writes the user's stored preference directly into the attribute. `data-dark-value` takes priority over the cookie and the OS, so the rendered value always wins on first load.

```html
<script src="btdt/js/btdt-loader.js"
        data-preset="theme-name"
        data-dark-value="<?= $user->darkMode ? 'dark' : 'light' ?>"
        data-dark-cookie="dark_mode"
        data-cookie-expire="365">
</script>
```

### Load a custom preset via JavaScript

```js
btdt.load('corporate');
```

### Load a preset from an arbitrary URL

```js
btdt.load('/assets/themes/my-theme.css');
```

### Switch mode programmatically and react to the change

```js
btdt.setMode('dark');

document.documentElement.addEventListener('btdt:modechange', (e) => {
    console.log('Mode changed to:', e.detail.mode);
});
```

### Manual init — disable auto-init and control everything yourself

```html
<script src="btdt/js/btdt-loader.js"
        data-auto-init="false">
</script>
<script>
    btdt.load('theme-name');
    btdt.setMode('dark');
</script>
```

### Toggle button with mode-specific icons

```html
<button class="theme-light-dark-toggle" aria-label="Toggle dark mode">
    <svg class="dark-mode-disabled" ...><!-- sun icon --></svg>
    <svg class="dark-mode-enabled"  ...><!-- moon icon --></svg>
</button>
```

---

## Notes

- The script applies the resolved mode to `<html>` **immediately on parse**, before the DOM is ready, to avoid a flash of unstyled content (FOUC).
- If a `<link rel="stylesheet">` matching the preset path convention already exists in the markup, the script adopts it in place instead of creating a new one.
- The dark-mode overlay stylesheet (`themes/modes/dark.min.css`) is always injected but toggled via the `media` attribute (`"all"` / `"not all"`), so the browser downloads it once and applies it without layout shift.
- When `data-dark-value` is present, no cookie is written on toggle, since `data-dark-value` would override it on the next page load anyway.
- The OS `prefers-color-scheme` listener is only registered when `data-dark-system="true"` is set and no higher-priority source (`data-dark-value`, `data-dark-cookie`) is configured.
