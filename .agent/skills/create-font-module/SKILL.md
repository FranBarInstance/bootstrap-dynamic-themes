# Skill: Create Font Module

## When to use this skill
Use this skill when the user asks to:
- "add a new font", "create a font module", "add typography option"
- "I want the theme to use [Font Name]", when that font has no module yet
- Add a Google Font to the system for use in presets

This skill allows the AI to add new typography options to the BTDT ecosystem using Google Fonts.

## Project Context
The system uses modular CSS files to load fonts dynamically. Fonts are hosted locally in `btdt/fonts/` and imported via CSS in `btdt/themes/fonts/`.

## Directory Structure
- `btdt/fonts/[font-slug]/` - Downloaded font files (WOFF2/TTF) and CSS
  - `[font-slug].css` - @font-face rules
  - `LICENSE.txt` - OFL license
  - Font files (e.g., `inter-400-normal.woff2`)
- `btdt/themes/fonts/[font-slug].css` - Theme typography rules that import local font

## Implementation Steps

### 1. Download Font Files
Use the provided script to download the font from Google Fonts:

```bash
python3 btdt/scripts/download-google-fonts.py "Font Name"
```

This downloads:
- All font variants (supports variable ranges like 100..900)
- Original OFL license from Google Fonts GitHub
- Generates local CSS with @font-face rules

### 2. Create Theme CSS (if not exists)
If `btdt/themes/fonts/[slug].css` doesn't exist, create it:

```css
/* btdt/themes/fonts/inter.css */
@import url('../../fonts/inter/inter.css');

:root {
  --bs-body-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --bs-body-font-weight: 400;
  --bs-body-line-height: 1.6;
}

h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6 {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
}

.display-1, .display-2, .display-3,
.display-4, .display-5, .display-6 {
  font-weight: 300;
}

.btn {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
}
```

### 3. Alternative: Use add-fonts.py
For a one-step process, use:

```bash
python3 btdt/scripts/add-fonts.py "Font Name"
```

This downloads the font AND creates the theme CSS if missing.

### 4. Catalog Sync (CRITICAL)
After creating or removing a font module, do NOT edit `btdt/js/config-fonts.js` manually.

Instead, run:
- `btdt/scripts/sync-configs.py`

This regenerates `btdt/js/config-fonts.js` from the filesystem.

If minified assets need updating, run after that:
- `btdt/scripts/minify-all.py`

Order matters:
1. `btdt/scripts/sync-configs.py`
2. `btdt/scripts/minify-all.py`

## Example Reference

```css
/* btdt/themes/fonts/inter.css */
@import url('../../fonts/inter/inter.css');

:root {
  --bs-body-font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --bs-body-font-weight: 400;
  --bs-body-line-height: 1.6;
}

h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6 {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
}
```

## Selection Criteria
- **Professionalism**: Pick fonts that look premium and are highly legible.
- **Variety**: Offer a mix of High-quality Sans-serifs (Modern), Serifs (Classic), and Mono fonts (Technical).
- **Performance**: Variable fonts with range (100..900) provide flexibility with fewer files.

## Notes
- Font name is case-sensitive (use exact name from Google Fonts)
- Both WOFF2 and TrueType formats are supported
- Licenses are downloaded automatically from the official Google Fonts GitHub repository
