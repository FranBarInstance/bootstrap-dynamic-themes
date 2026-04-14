# Skill: Create Font Module

## When to use this skill
Use this skill when the user asks to:
- "add a new font", "create a font module", "add typography option"
- "I want the theme to use [Font Name]", when that font has no module yet
- Add a Google Font to the system for use in presets

This skill allows the AI to add new typography options to the BTDT ecosystem using Google Fonts.

## Project Context
The system uses modular CSS files to load fonts dynamically. Fonts are hosted locally in `btdt/fonts/` and imported via CSS in `btdt/themes/fonts/`.

## Available Utilities

The project provides three scripts for font management:

1. **`download_google_fonts.py`** - Downloads individual fonts from Google Fonts
2. **`sync-fonts.py`** - Synchronizes all fonts defined in themes (bulk operation)
3. **`add-fonts.py`** - One-step font addition (download + create theme CSS)

## Directory Structure
- `btdt/fonts/[font-slug]/` - Downloaded font files (WOFF2/TTF) and CSS
  - `[font-slug].css` - @font-face rules with local file references
  - `LICENSE.txt` - OFL license from Google Fonts
  - Font files (e.g., `inter-400-normal.woff2`, `inter-700-normal.ttf`)
- `btdt/themes/fonts/[font-slug].css` - Theme typography rules that import local font

## Implementation Steps

### Step 1: Add the Font

Use `add-fonts.py` to download the font and create theme CSS:

```bash
python3 btdt/scripts/add-fonts.py "Font Name"
```

Example:

```bash
python3 btdt/scripts/add-fonts.py "Inter"
python3 btdt/scripts/add-fonts.py "Playfair Display"
python3 btdt/scripts/add-fonts.py "JetBrains Mono"
```

**What it does:**
1. Checks if font files exist in `btdt/fonts/[slug]/`
2. If missing, downloads from Google Fonts (all weights, WOFF2/TrueType)
3. Downloads OFL license from Google Fonts GitHub repository
4. Checks if theme CSS exists in `btdt/themes/fonts/[slug].css`
5. If missing, creates theme CSS with proper Bootstrap variable mappings

### Step 2: Update Catalog

After adding the font, regenerate the catalog:

```bash
python3 btdt/scripts/sync-configs.py
python3 btdt/scripts/minify-all.py
```

## Catalog Sync (CRITICAL)

After creating or removing a font module, do NOT edit `btdt/js/config-fonts.js` manually.

Instead, run:

```bash
python3 btdt/scripts/sync-configs.py
```

This regenerates `btdt/js/config-fonts.js` from the filesystem.

If minified assets need updating, run after that:

```bash
python3 btdt/scripts/minify-all.py
```

`btdt/scripts/minify-all.py` relies on the shared `btdt/scripts/.venv`
environment and the dependencies listed in `btdt/scripts/requirements.txt`.

**Order matters:**
1. `python3 btdt/scripts/sync-configs.py`
2. `python3 btdt/scripts/minify-all.py`

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

- Font name is case-sensitive (use exact name from https://fonts.google.com/)
- Both WOFF2 and TrueType formats are supported (detected automatically)
- Licenses are downloaded automatically from the official Google Fonts GitHub repository
- If a font doesn't support variable weights (100..900), the script automatically falls back to specific weights (400;700) or the default set
