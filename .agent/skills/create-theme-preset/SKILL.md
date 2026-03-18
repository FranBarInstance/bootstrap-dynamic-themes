# Skill: Create Theme Preset

This skill allows the AI to combine color, font, and style modules into a "Production Preset" that is self-descriptive and compatible with the BTDT engine.

## Project Context
A preset is a single CSS file that imports other modules. It also includes "Invisible Metadata" so the Editor can recognize and sync the configuration even when running locally via `file://`.

## Directory Structure
Presets are stored in: `btdt/themes/preset/[preset-name].css`

## Implementation Guidelines

### 1. Modular Imports
Include `@import` statements in this exact order:
- `colors`
- `fonts`
- `background`
- `borders`
- `rounding`
- `shadows`
- `spacing`
- `gradients`
- `accent`
- `accentSize`
- `accentColor`

Use exactly one module from each category. Presets in this project are now considered complete only when all 11 categories are explicit.

### 2. Zero-CORS Metadata Block
Append a `:root` block at the end of the file containing `--preset-[category]` variables for all 11 categories. These values MUST match the imported modules exactly.

### 3. Metadata Update (CRITICAL)
After creating the CSS file, you MUST add the new preset metadata to `btdt/js/config-presets.js`.
- Add a new entry with the preset ID, a human-readable title, and the ID of the primary color palette it use (for the visual swatch in the dropdown).
- This ensures the preset appears in the editor's custom select dropdown.

## Example Reference
```css
/* btdt/themes/preset/studio.css */
@import "../colors/corporate.css";
@import "../fonts/ubuntu.css";
@import "../styles/background-none.css";
@import "../styles/borders-normal.css";
@import "../styles/rounding-normal.css";
@import "../styles/shadows-normal.css";
@import "../styles/spacing-normal.css";
@import "../styles/gradients-off.css";
@import "../styles/accent-bottom.css";
@import "../styles/accent-1.css";
@import "../styles/accent-primary.css";

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
}
```

## Aesthetic Standards
- **Cohesion**: Ensure the chosen segments complement each other (e.g., don't pair a 'Wild' neon palette with a 'Classical' Serif font unless specifically looking for a 'Retro-Futurism' vibe).
- **Curation**: Give the preset a meaningful name that describes the "Mood" (e.g., *Zen*, *Electric*, *Minimalist*, *Corporate*).
- **Restraint**: Presets should feel elegant. Avoid stacking too many loud effects at once.
- **Backgrounds**: Default to `background-none.css` unless a subtle tinted background genuinely improves the preset.
- **Identity**: If updating an existing preset, preserve its core palette and overall personality. Refine it; do not reinvent it.
