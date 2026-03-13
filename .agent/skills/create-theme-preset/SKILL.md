# Skill: Create Theme Preset

This skill allows the AI to combine color, font, and style modules into a "Production Preset" that is self-descriptive and compatible with the BTDT engine.

## Project Context
A preset is a single CSS file that imports other modules. It also includes "Invisible Metadata" so the Editor can recognize and sync the configuration even when running locally via `file://`.

## Directory Structure
Presets are stored in: `btdt/themes/preset/[preset-name].css`

## Implementation Guidelines

### 1. Modular Imports
Include `@import` statements for exactly one module from each relevant category (Color, Font, Styles).

### 2. Zero-CORS Metadata Block
Append a `:root` block at the end of the file containing `--preset-[category]` variables. These MUST match the values in the `ThemeManager.js`.

## Example Reference
```css
/* btdt/themes/preset/studio.css */
@import "../colors/corporate.css";
@import "../fonts/inter.css";
@import "../styles/borders-normal.css";
@import "../styles/rounding-normal.css";

/* Metadata for the Editor (MUST BE PRESENT) */
:root {
  --preset-colors: "corporate";
  --preset-fonts: "inter";
  --preset-borders: "normal";
  --preset-rounding: "normal";
}
```

## Aesthetic Standards
- **Cohesion**: Ensure the chosen segments complement each other (e.g., don't pair a 'Wild' neon palette with a 'Classical' Serif font unless specifically looking for a 'Retro-Futurism' vibe).
- **Curation**: Give the preset a meaningful name that describes the "Mood" (e.g., *Zen*, *Electric*, *Minimalist*, *Corporate*).
