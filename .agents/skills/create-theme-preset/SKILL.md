# Skill: Create Theme Preset

This skill allows the AI to combine color, font, and style modules into a "Production Preset" that is self-descriptive and compatible with the BTDT engine.

## When to use this skill
Use this skill when the user asks to:
- "create a preset", "create a theme", "make a preset", "combine styles into a preset"
- "fix a missing preset", "a preset is not working / doesn't exist"
- "create a theme called…" when the intent is to assemble existing modules (not design new colors)

## Available Modules
Before choosing modules, inspect what already exists:
- **Colors**: `btdt/themes/colors/` — all `.css` files except `_template_.css` and `*.min.css`
- **Fonts**: `btdt/themes/fonts/` — all `.css` files except `*.min.css`
- **Styles**: `btdt/themes/styles/` — grouped by prefix:
  - `background-*`, `borders-*`, `rounding-*`, `shadows-*`, `spacing-*`
  - `gradients-*`, `accent-*` (position), `accent-[1-5].css` (size), `accent-primary/secondary/gray.css` (color)
  - `personality-*` (optional final finish layer)

## Project Context
A preset is a single CSS file that imports other modules. It also includes "Invisible Metadata" so the Editor can recognize and sync the configuration even when running locally via `file://`.

## Directory Structure
Presets are stored in: `btdt/themes/preset/[preset-name].css`

## Implementation Guidelines

### 1. Modular Imports
Include `@import` statements in this exact order:
- `fonts`
- `colors`
- `background`
- `borders`
- `rounding`
- `shadows`
- `spacing`
- `gradients`
- `accent`
- `accentSize`
- `accentColor`
- `personality` (optional, only when the preset intentionally includes a personality layer)

All `@import` rules MUST stay together at the top of the stylesheet, before any non-`@import` CSS rules such as `:root` metadata blocks.
Leading license/header comments are acceptable and already used in the project.

Use exactly one module from each base category.
For current BTDT presets, the standard complete base set is:
- `fonts`
- `colors`
- `background`
- `borders`
- `rounding`
- `shadows`
- `spacing`
- `gradients`
- `accent`
- `accentSize`
- `accentColor`

`personality` is an optional twelfth layer. Include it only when the preset is meant to carry a personality finish.

### 2. Zero-CORS Metadata Block
Append a `:root` block at the end of the file containing `--preset-[category]` variables matching the imported modules.

Required metadata keys for the current base preset standard:
- `--preset-colors`
- `--preset-fonts`
- `--preset-background`
- `--preset-borders`
- `--preset-rounding`
- `--preset-shadows`
- `--preset-spacing`
- `--preset-gradients`
- `--preset-accent`
- `--preset-accentSize`
- `--preset-accentColor`

Optional metadata key:
- `--preset-personality`

If the preset imports `personality-*`, add `--preset-personality` as well so the file remains fully self-descriptive.

### 3. Catalog Sync (CRITICAL)
After creating or removing a preset CSS file, do NOT edit `btdt/js/config-presets.js` manually.

Instead, run:
- `btdt/scripts/sync-configs.py`

This regenerates `btdt/js/config-presets.js` from the preset files present on disk.

If the task also requires minified assets to be updated, run after that:
- `btdt/scripts/minify-all.py`

`btdt/scripts/minify-all.py` uses the shared `btdt/scripts/.venv`
environment and the dependencies declared in
`btdt/scripts/requirements.txt`.

Order matters:
1. `btdt/scripts/sync-configs.py`
2. `btdt/scripts/minify-all.py`

## Example Reference
```css
/* btdt/themes/preset/studio.css */
@import "../fonts/ubuntu.css";
@import "../colors/corporate.css";
@import "../styles/background-none.css";
@import "../styles/borders-normal.css";
@import "../styles/rounding-normal.css";
@import "../styles/shadows-normal.css";
@import "../styles/spacing-normal.css";
@import "../styles/gradients-off.css";
@import "../styles/accent-bottom.css";
@import "../styles/accent-1.css";
@import "../styles/accent-primary.css";
@import "../styles/personality-material.css";

/* Metadata for the editor */
:root {
  --preset-colors: "corporate";
  --preset-fonts: "ubuntu";
  --preset-background: "none";
  --preset-borders: "normal";
  --preset-rounding: "normal";
  --preset-shadows: "normal";
  --preset-spacing: "normal";
  --preset-gradients: "off";
  --preset-accent: "bottom";
  --preset-accentSize: "1";
  --preset-accentColor: "primary";
  --preset-personality: "material";
}
```

## Aesthetic Standards
- **Cohesion**: Ensure the chosen segments complement each other (e.g., don't pair a 'Wild' neon palette with a 'Classical' Serif font unless specifically looking for a 'Retro-Futurism' vibe).
- **Curation**: Give the preset a meaningful name that describes the "Mood" (e.g., *Zen*, *Electric*, *Minimalist*, *Corporate*).
- **Restraint**: Presets should feel elegant. Avoid stacking too many loud effects at once.
- **Backgrounds**: Default to `background-none.css` unless a subtle tinted background genuinely improves the preset.
- **Identity**: If updating an existing preset, preserve its core palette and overall personality. Refine it; do not reinvent it.
