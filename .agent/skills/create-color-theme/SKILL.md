# Skill: Create Color Theme

This skill allows the AI to design and implement new color palettes for the Bootstrap Dynamic Themes (BTDT) system.

## Project Context
The application is a dynamic theme engine for Bootstrap 5. Themes are injected at runtime. Color themes must define core Bootstrap variables and handle component-specific overrides to ensure a premium look.

## Directory Structure
Color themes are stored in: `btdt/themes/colors/[theme-name].css`

## Implementation Guidelines

### 1. Root Variables
Every theme must define the following variables in a `:root` block:
- `--bs-body-bg`: Main background color.
- `--bs-body-color`: Main text color (ensure high contrast with background).
- `--bs-primary`, `--bs-primary-rgb`: The main accent color.
- `--bs-secondary`, `--bs-secondary-rgb`: The secondary accent color.
- `--bs-link-color`, `--bs-link-hover-color`: High visibility link colors.

### 2. Button Overrides
Customize `.btn-primary` and `.btn-secondary` to match the palette. Ensure text remains legible on the button background.

### 3. Utility Classes
Define `.bg-primary`, `.bg-secondary`, `.text-primary`, and `.text-secondary`.

### 4. Accessibility & Legibility (Crucial)
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
