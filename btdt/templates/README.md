# BTDT Templates

Ready-to-use HTML website templates powered by BTDT. Each template lives in
its own folder (`btdt/templates/<name>/index.html`) and is meant to be copied
into your own project.

> **Status: experimental.** This directory is currently a single proof of
> concept to validate the approach. More templates will be added in the future.

## Current templates

| Folder | Description |
|---|---|
| `dashboard` | App shell with a fixed side menu (offcanvas on mobile), a transparent navbar, stat cards, buttons, table and activity panels. |

## How a template works

Templates follow the BTDT philosophy: **no design CSS**. All colors, borders
and states come from the theme — each page includes a single theme preset
link, and switching themes changes the whole look:

```html
<link rel="stylesheet" id="theme-preset" href="../../themes/preset/studio-asymmetric.min.css">
```

Change the `href` to any preset in `btdt/themes/preset/` and everything adapts.
The BTDT loader (`btdt.min.js`) adopts that link, resolves light/dark mode and
binds the `.theme-light-dark-toggle` button.

The only CSS a template may add is **functional** (layout that the theme cannot
provide, such as the side menu's sticky behavior or small-screen fixes).

## Adding a new template

1. Create a folder: `btdt/templates/<name>/index.html`.
2. Reference BTDT assets with relative paths:
   - `../../css/bootstrap.min.css`
   - `../../themes/preset/<preset>.min.css` (as `#theme-preset`)
   - `../../js/btdt.min.js`
3. Use theme classes (`bg-*`, `nav-pills`, `btn-*`, `card`, …) for all design.
4. Only add functional CSS (layout), never visual styling.
5. Keep all comments and content in English.
