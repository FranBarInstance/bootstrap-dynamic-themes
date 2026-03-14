# Skill: Create Color Theme

This skill allows the AI to design and implement new color palettes for the Bootstrap Dynamic Themes (BTDT) system.

## Project Context
The application is a dynamic theme engine for Bootstrap 5. Themes are injected at runtime. Color themes must define core Bootstrap variables and handle component-specific overrides to ensure a premium look.

## Directory Structure
Color themes are stored in: `btdt/themes/colors/[theme-name].css`

## Implementation Guidelines

### 0. Research & Reference (MANDATORY)
Before starting, you MUST read at least two existing color themes to understand the current structure and how variables are mapped.
- Recommended: `btdt/themes/colors/ocean.css` and `btdt/themes/colors/corporate.css`.
- Notice how text contrast is handled and how specific Bootstrap components are overridden.

### 1. Root Variables
Every theme must define the following variables in a `:root` block:
- `--bs-body-bg`: Main background color. **Default to `#ffffff` (white) unless the user explicitly requests a Dark theme**.
- `--bs-body-color`: Main text color. Ensure a minimum contrast ratio of 4.5:1.
- `--bs-primary`, `--bs-primary-rgb`: The main accent color.
- `--bs-secondary`, `--bs-secondary-rgb`: The secondary accent color.
- `--bs-link-color`, `--bs-link-hover-color`: High visibility link colors.

### 1.1 Contrast Awareness (CRITICAL)
If the `--bs-primary` or `--bs-secondary` color is light (e.g., pastels, lime, yellow):
- Elements like `.bg-primary`, `.bg-secondary`, and `.btn-primary` MUST use a dark text color (e.g., `#1a1a1a`) instead of white to ensure legibility.
- Conversely, for dark primary colors, always use white text.

### 2. Button Overrides
Customize `.btn-primary` and `.btn-secondary` to match the palette. Ensure text remains legible on the button background.

### 3. Utility Classes
Define `.bg-primary`, `.bg-secondary`, `.text-primary`, and `.text-secondary`.

### 4. Metadata Update (CRITICAL)
After creating the CSS file, you MUST add the new theme metadata to `btdt/js/config-colors.js`.
- Add a new entry with the theme ID and its primary, secondary, and accent colors (hex values).
- This ensures the editor can display the color swatch in the new custom select dropdown.

### 5. Accessibility & Legibility (Crucial)
To ensure links remain visible in different backgrounds, always include this block at the end of the file:

```css
/* Ensure link legibility in background containers (excluding navbar) */
[class*="bg-"]:not(.navbar) a:not(.btn):not(.nav-link),
[class*="text-bg-"]:not(.navbar) a:not(.btn):not(.nav-link) {
  color: inherit !important;
  text-decoration: underline;
}
```

## Aesthetic Standards
- Avoid generic colors. Use harmonious, curated palettes (e.g., Pastel, Midnight, Earth tones).
- For "Dark" themes, ensure subtle contrast rather than pure black (#000). Use deep grays or navy.
- For "Light" themes, ensure the primary color isn't too bright to wash out text.

## Example Reference
See `btdt/themes/colors/ocean.css` or `btdt/themes/colors/white.css` for structural examples.
